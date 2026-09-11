"""Section 11: what counts as test evidence, and what uncertainty looks like."""

from __future__ import annotations

import unittest

from evidence import (
    ABSENT, FILES_ONLY, MEMORY_SPECIFIC, MENTION_ONLY, SUBSTANTIVE, UNKNOWN,
    Blob, Inspection, classify_scope, classify_substance, classify_tests,
)

REAL_TEST = '''
import pytest
from mem.store import MemoryStore

def test_recall_excludes_superseded_entries(tmp_path):
    store = MemoryStore(tmp_path / "m.sqlite3")
    store.write("user likes tea", key="drink")
    store.write("user likes coffee", key="drink")
    results = store.recall("drink")
    assert "user likes coffee" in [r.text for r in results]
    assert "user likes tea" not in [r.text for r in results]
'''

PLAIN_TEST = '''
def test_adds():
    assert add(2, 2) == 4

def test_subtracts():
    assert subtract(4, 2) == 2
'''

TEMPLATE_TEST = '''
def test_example():
    # TODO: write tests
    assert True
'''

IMPLEMENTATION = '''
import sqlite3

class MemoryStore:
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.execute("CREATE TABLE IF NOT EXISTS memory (key TEXT, text TEXT, session_id TEXT)")

    def write(self, text, key, session_id):
        self.db.execute("INSERT INTO memory VALUES (?, ?, ?)", (key, text, session_id))
'''


def inspection(files: dict[str, str], *, truncated: bool = False,
               extra_paths: list[str] | None = None) -> Inspection:
    found = Inspection(commit="a" * 40, truncated=truncated)
    found.coverage["tree"] = "sampled" if truncated else "complete"
    found.tree_paths = list(files) + list(extra_paths or [])
    found.blobs = [
        Blob(path=path, sha=None, size=len(text), text=text, excerpt=text[:200])
        for path, text in files.items()
    ]
    return found


class TestEvidenceTests(unittest.TestCase):
    def test_memory_tests_with_assertions_are_memory_specific(self):
        found = classify_tests(inspection({"tests/test_recall.py": REAL_TEST}), 400)
        self.assertEqual(found.level, MEMORY_SPECIFIC)
        self.assertEqual(found.memory_test_files, 1)
        self.assertTrue(found.files[0]["assertions"])

    def test_ordinary_tests_with_assertions_are_substantive(self):
        found = classify_tests(inspection({"tests/test_math.py": PLAIN_TEST}), 400)
        self.assertEqual(found.level, SUBSTANTIVE)

    def test_a_template_stub_does_not_pass(self):
        found = classify_tests(inspection({"tests/test_example.py": TEMPLATE_TEST}), 400)
        self.assertEqual(found.level, FILES_ONLY)
        self.assertTrue(found.template_only)

    def test_a_readme_promise_is_only_a_mention(self):
        found = classify_tests(
            inspection({"README.md": "Fully tested! [![tests](badge.svg)](ci)",
                        "app.py": IMPLEMENTATION}),
            400,
        )
        self.assertEqual(found.level, MENTION_ONLY)

    def test_a_complete_tree_with_no_tests_is_absent(self):
        found = classify_tests(inspection({"README.md": "A memory.", "app.py": IMPLEMENTATION}), 400)
        self.assertEqual(found.level, ABSENT)

    def test_a_truncated_tree_is_never_an_absence(self):
        found = classify_tests(
            inspection({"README.md": "A memory.", "app.py": IMPLEMENTATION}, truncated=True), 400)
        self.assertEqual(found.level, UNKNOWN)
        self.assertIn("truncated", found.reason)

    def test_inline_rust_tests_are_recognised(self):
        rust = (
            "pub fn recall(k: &str) -> Option<String> { None }\n\n"
            "#[cfg(test)]\nmod tests {\n    use super::*;\n"
            "    #[test]\n    fn recall_returns_the_stored_memory() {\n"
            "        assert_eq!(recall(\"a\"), Some(\"b\".to_string()));\n    }\n}\n"
        )
        found = classify_tests(inspection({"src/lib.rs": rust}), 400)
        self.assertEqual(found.level, MEMORY_SPECIFIC)

    def test_an_unfamiliar_layout_is_unknown_not_absent(self):
        found = classify_tests(inspection({"README.md": "hi", "main.zig": "pub fn main() {}"}), 400)
        self.assertEqual(found.level, UNKNOWN)

    def test_listed_but_unread_tests_are_unknown(self):
        found = classify_tests(
            inspection({"README.md": "hi", "app.py": IMPLEMENTATION},
                       extra_paths=["tests/test_a.py", "tests/test_b.py"]),
            400,
        )
        self.assertEqual(found.level, UNKNOWN)
        self.assertIn("none were read", found.reason)

    def test_vendored_tests_do_not_count(self):
        from evidence import read_tree  # noqa: F401  (import kept for symmetry)
        found = inspection({"README.md": "hi"})
        found.tree_paths = ["README.md", "node_modules/lib/tests/test_lib.js"]
        # read_tree filters vendored paths at the source; assert the filter's regex
        from evidence import VENDORED
        self.assertTrue(VENDORED.search("node_modules/lib/tests/test_lib.js"))
        self.assertFalse(VENDORED.search("src/tests/test_lib.js"))

    def test_ci_configuration_is_not_a_test_run(self):
        workflow = "jobs:\n  test:\n    steps:\n      - run: pytest -q\n"
        found = classify_tests(
            inspection({".github/workflows/ci.yml": workflow, "tests/test_a.py": PLAIN_TEST}), 400)
        self.assertTrue(found.ci_configured)
        self.assertFalse(found.ci_run_observed)


class ScopeAndSubstanceTests(unittest.TestCase):
    def test_a_store_plus_memory_vocabulary_in_code_is_in_scope(self):
        scope = classify_scope(inspection({"mem/store.py": IMPLEMENTATION}))
        self.assertIs(scope.in_scope, True)
        self.assertEqual(scope.basis, "heuristic")

    def test_a_readme_full_of_memory_words_with_no_store_is_out_of_scope(self):
        scope = classify_scope(inspection({
            "README.md": "Episodic memory, semantic recall, long-term remembering!",
            "cli.py": "import click\n\n@click.command()\ndef main():\n    print('hi')\n",
        }))
        self.assertIs(scope.in_scope, False)

    def test_a_readme_only_repository_has_no_substance(self):
        found = inspection({"README.md": "x" * 6000, "app.py": "x = 1\n"})
        substance = classify_substance(found)
        self.assertIs(substance.readable, False)

    def test_a_real_implementation_is_readable(self):
        found = inspection({f"pkg/mod{index}.py": IMPLEMENTATION for index in range(6)})
        self.assertIs(classify_substance(found).readable, True)


if __name__ == "__main__":
    unittest.main()
