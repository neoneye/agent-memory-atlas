"""Defects found in the first live batch, 11 September 2026, each pinned by a test.

Every case here was observed on a real repository in that batch, and the fixture
reproduces the shape of the file that exposed it.
"""

from __future__ import annotations

import unittest
import uuid
from pathlib import Path

import assess as assess_module
import atlas
import ingest as ingest_module
from db import transaction
from evidence import Blob, Inspection, choose_blobs, classify_scope
from policy import Policy, mechanism_terms
from tests.support import FakeClient, Harness, repo_routes
from util import civil_day, dumps, iso, utc_now

# The shape of Free_agent_memory_system's src/memory_system/core/persistence.rs:
# a Rust store that writes with std::fs, which the first rules could not see.
RUST_PERSISTENCE = '''
use std::fs::{self, File};
use std::io::Write;

pub struct MemoryPersistence { root: std::path::PathBuf }

impl MemoryPersistence {
    pub fn save(&self, memory: &Memory) -> std::io::Result<()> {
        let mut file = File::create(self.root.join(&memory.id))?;
        file.write_all(&memory.encode())
    }
}
'''

# The shape of ContextMeld's src-tauri/src/memories.rs: soft deletion, a scope
# column and a version — correction vocabulary the first rules did not know.
CORRECTABLE_ROWS = '''
conn.execute("CREATE TABLE memories (id TEXT PRIMARY KEY, scope TEXT NOT NULL,
              content TEXT, version INTEGER, deleted_at TEXT)", [])?;
conn.execute("SELECT * FROM memories WHERE scope = ?1 AND deleted_at IS NULL", [scope])?;
'''

PLAIN_CODE = "def handler(request):\n    return {'ok': True}\n"


def inspection(files: dict[str, str], listed: list[str] | None = None) -> Inspection:
    found = Inspection(commit="a" * 40)
    found.coverage["tree"] = "complete"
    found.tree_paths = list(files) + list(listed or [])
    found.blobs = [Blob(path=p, sha=None, size=len(t), text=t, excerpt=t[:100])
                   for p, t in files.items()]
    return found


class PersistenceVocabularyTests(unittest.TestCase):
    def test_a_rust_store_written_with_std_fs_is_seen(self):
        scope = classify_scope(inspection({"src/memory_system/core/persistence.rs": RUST_PERSISTENCE}))
        self.assertIs(scope.in_scope, True, scope.reasons)

    def test_go_and_sqlx_stores_are_seen(self):
        for text in ('os.WriteFile(path, data, 0o600)\n// memory',
                     'sqlx::query("INSERT INTO memory VALUES ($1)")'):
            scope = classify_scope(inspection({"src/memory.rs": text}))
            self.assertIs(scope.in_scope, True, text)


class SampledAbsenceTests(unittest.TestCase):
    def test_no_store_in_a_sample_is_unknown_not_out_of_scope(self):
        unread = [f"src/module{i}.py" for i in range(30)]
        scope = classify_scope(inspection({"src/memory/api.py": PLAIN_CODE}, listed=unread))
        self.assertIsNone(scope.in_scope)
        self.assertIn("of", " ".join(scope.reasons))

    def test_no_store_when_every_implementation_file_was_read_is_out_of_scope(self):
        scope = classify_scope(inspection({"app.py": PLAIN_CODE, "README.md": "an agent"}))
        self.assertIs(scope.in_scope, False)


class BlobChoiceTests(unittest.TestCase):
    def test_issue_templates_configs_and_translations_do_not_take_implementation_slots(self):
        listed = [
            "README.md", "README.zh-CN.md", "package.json", ".prettierrc.json",
            "docker-compose.yml", ".github/ISSUE_TEMPLATE/bug_report.yml",
            ".github/ISSUE_TEMPLATE/config.yml", "License/Third_Party_Notice.md",
            "docs/memories.md", "tests/memory.test.ts",
            "src/memory/store.ts", "src/memory/recall.ts", "src/server.ts", "src/routes.ts",
        ]
        found = Inspection(commit="a" * 40, tree_paths=listed)
        chosen = choose_blobs(found, 12)
        for junk in ("README.zh-CN.md", ".prettierrc.json", "docker-compose.yml",
                     ".github/ISSUE_TEMPLATE/bug_report.yml", ".github/ISSUE_TEMPLATE/config.yml",
                     "License/Third_Party_Notice.md", "docs/memories.md"):
            self.assertNotIn(junk, chosen)
        for source in ("src/memory/store.ts", "src/memory/recall.ts", "src/server.ts"):
            self.assertIn(source, chosen)


class AtlasValueVocabularyTests(unittest.TestCase):
    def test_soft_deletion_scope_and_versioning_are_leads(self):
        rare, common = mechanism_terms({"src-tauri/src/memories.rs": CORRECTABLE_ROWS})
        self.assertIn("scope_enforced", common)
        self.assertIn("correction", rare + common)

    def test_readme_vocabulary_still_does_not_count(self):
        rare, common = mechanism_terms({"README.md": "tombstone deleted_at scope audit log"})
        self.assertEqual((rare, common), ([], []))


class EmptyRepositoryAndBackoffTests(unittest.TestCase):
    def setUp(self):
        self.h = Harness()
        self.addCleanup(self.h.close)
        self.policy = Policy.load(self.h.config.policy_file)
        self.day = civil_day(utc_now(), self.h.config.timezone)
        atlas.sync(self.h.connection, self.h.atlas_repo,
                   Path(self.h.config.policy_file).parent / "exclusions.txt")
        self.client = FakeClient(self.h.config, self.h.connection, self.day)

    def test_an_empty_repository_says_so_and_backs_off(self):
        from fetching import FetchError, api_url
        self.h.feed([{"kind": "repo", "repo": "empty/repo"}])
        ingest_module.run(self.h.config, self.h.connection, None)
        repo_routes(self.client, "empty/repo", commit="e" * 40, files={}, repo_id=9)
        self.client.route(api_url("repos", "empty", "repo", "commits", sha="main", per_page=100),
                          FetchError("unavailable", "HTTP 409 (empty repository)", status=409))
        run = assess_module.AssessRun()
        assess_module.collect_metadata(self.h.config, self.h.connection, self.client, self.day, run)
        assess_module.run_stage_c(self.h.config, self.h.connection, self.client, self.policy,
                                  self.day, run, {})
        row = self.h.connection.execute(
            "SELECT triage_status, triage_reason FROM candidate").fetchone()
        self.assertEqual(row["triage_status"], "deferred")
        self.assertIn("empty repository", row["triage_reason"])
        self.assertNotIn("could not be listed", row["triage_reason"])

    def test_repeated_deferrals_back_off_to_the_configured_maximum(self):
        days = [assess_module.backoff_days(self.policy, n) for n in range(1, 8)]
        self.assertEqual(days[0], self.policy.reassessment_days["incomplete_evidence"])
        self.assertEqual(days, sorted(days))
        self.assertEqual(days[-1], self.policy.reassessment_days["incomplete_evidence_max"])


class PolicyVersionTests(unittest.TestCase):
    """A rejection is a statement under one policy. A new policy reopens it."""

    def setUp(self):
        self.h = Harness()
        self.addCleanup(self.h.close)
        self.policy = Policy.load(self.h.config.policy_file)

    def _rejected_under(self, version: str) -> None:
        now = iso(utc_now())
        far = iso(utc_now().replace(year=utc_now().year + 1))
        with transaction(self.h.connection):
            cursor = self.h.connection.execute(
                "INSERT INTO candidate(canonical_name, display_name, first_seen_at, last_seen_at, "
                "triage_status, next_assessment_at) VALUES ('a/b', 'a/b', ?, ?, 'rejected', ?)",
                (now, now, far))
            assessment = self.h.connection.execute(
                "INSERT INTO assessment(uuid, candidate_id, assessed_at, policy_version, outcome) "
                "VALUES (?, ?, ?, ?, 'rejected')", (str(uuid.uuid4()), cursor.lastrowid, now, version))
            self.h.connection.execute("UPDATE candidate SET latest_assessment = ?",
                                      (assessment.lastrowid,))

    def test_a_rejection_under_an_older_policy_is_due_again(self):
        self._rejected_under("2000-01-01.0")
        due = assess_module.assessable(self.h.connection, self.policy.version)
        self.assertEqual([row["canonical_name"] for row in due], ["a/b"])

    def test_a_rejection_under_the_current_policy_waits_its_turn(self):
        self._rejected_under(self.policy.version)
        self.assertEqual(assess_module.assessable(self.h.connection, self.policy.version), [])


if __name__ == "__main__":
    unittest.main()
