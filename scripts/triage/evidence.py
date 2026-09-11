"""Bounded evidence: one tree listing, a few text blobs, and what they support.

Nothing is cloned, extracted or executed. The tree is one API call at a pinned
commit; the blobs are read from raw.githubusercontent.com at that same commit,
counted against the per-repository ceilings, assessed, and dropped. What survives
into the database is paths, blob hashes, and short excerpts.

The classification that matters is test evidence, and its six values exist so
that *not knowing* is sayable. A truncated tree, an unfamiliar layout, a failed
request or an exhausted budget all produce `unknown`, which defers. Only an
adequately covered tree with nothing in it produces `absent`, which rejects.
The difference between those two is the difference between a finding and a gap,
and collapsing them is how a project gets rejected for the reviewer's timeout.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from fetching import BUDGET, Client, FetchError, RepoBudget, api_url, raw_url
from util import sha256_hex, truncate

UNKNOWN, ABSENT, MENTION_ONLY, FILES_ONLY, SUBSTANTIVE, MEMORY_SPECIFIC = (
    "unknown", "absent", "mention_only", "files_only", "substantive", "memory_specific"
)
PASSING = {SUBSTANTIVE, MEMORY_SPECIFIC}

# Paths whose contents are somebody else's code. A vendored dependency's test
# suite is evidence about that dependency, not about this project.
VENDORED = re.compile(
    r"(^|/)(node_modules|vendor|third_party|thirdparty|site-packages|\.venv|venv|dist|build|"
    r"target/(debug|release)|\.git|Pods|Godeps|bower_components|__pycache__|\.next|\.nuxt)(/|$)"
)

TEST_PATH = re.compile(
    r"(^|/)(tests?|spec|specs|__tests__|testing|e2e|it)(/|$)"
    r"|(^|/)test_[^/]+\.py$|[^/]+_test\.py$|[^/]+_test\.go$|[^/]+_test\.rb$"
    r"|[^/]+\.test\.(ts|tsx|js|jsx|mjs)$|[^/]+\.spec\.(ts|tsx|js|jsx|mjs)$"
    r"|[^/]+Test\.java$|[^/]+Tests\.cs$|[^/]+Spec\.scala$|[^/]+_spec\.rb$"
    r"|(^|/)tests\.rs$|(^|/)test\.exs$|[^/]+_test\.exs$|[^/]+Test\.php$",
    re.IGNORECASE,
)

# Languages that put tests inside the implementation file. Absence of a `tests/`
# directory in a Rust or Go project says nothing until these have been looked for.
INLINE_TEST = re.compile(
    r"#\[test\]|#\[cfg\(test\)\]|#\[tokio::test\]"           # Rust
    r"|func Test[A-Z]\w*\(t \*testing\.T\)"                  # Go
    r"|@Test\b|\[Fact\]|\[Theory\]|\[TestMethod\]"           # Java / .NET
    r"|def test_\w+|class Test\w+\("                          # Python
    r"|describe\([\"'`]|it\([\"'`]|test\([\"'`]"              # JS/TS
    r"|XCTAssert|func test[A-Z]\w*\(\)"                       # Swift
)

ASSERTION = re.compile(
    r"(?m:^\s*assert\b\s+\S)|\bassert\w*\s*[\(\!]|assertEquals?|assertTrue|assertRaises|assertIn"
    r"|expect\s*\(|\.should\b|\.to\.(equal|be|deep)|require\.(NoError|Equal|True)"
    r"|t\.(Errorf?|Fatalf?)\(|XCTAssert\w*|assert_eq!|assert!|assert_ne!"
    r"|\bShould\w*\(|Assert\.\w+"
)

# A placeholder that ships with a project template. Present in enough new repos
# that counting it as evidence would admit a steady stream of empty scaffolds.
TEMPLATE_TEST = re.compile(
    r"(?m:^\s*assert\s+True\s*$)|assert\s+1\s*==\s*1|expect\(true\)\.toBe\(true\)"
    r"|it\(['\"]works['\"]|fn it_works\(\)|assert_eq!\(2 \+ 2, 4\)"
    r"|def test_example|Learn more about testing|add your tests here"
    r"|TODO:? *write tests|placeholder test",
    re.IGNORECASE,
)

MEMORY_TERMS = re.compile(
    r"\bmemor(y|ies)\b|\brecall\b|\bremember\b|\bforget(ting)?\b|\bretriev\w+|\bpersist\w+"
    r"|\bsession[_ ]?(id|state|memory)\b|\bepisodic\b|\bsemantic memory\b|\bconsolidat\w+"
    r"|\bembedding\b|\bvector (store|search|db)\b|\btombstone\b|\bsupersed\w+|\bprovenance\b"
    r"|\bcontradict\w+|\bknowledge[ _]?(graph|base)\b|\bcontext[ _]?(store|window|memory)\b"
    r"|\bscope[d]?[ _]?(memory|key|filter)\b|\bforget|\bdecay\b|\brecency\b",
    re.IGNORECASE,
)

# Structural signals that something is stored and read back later. Deliberately
# separate from the memory vocabulary above: a project can use every memory word
# in its README and write nothing down.
PERSISTENCE = re.compile(
    r"sqlite3?|CREATE TABLE|psycopg|asyncpg|SQLAlchemy|prisma|mongo|redis|duckdb|lmdb|leveldb"
    r"|chromadb|qdrant|weaviate|pinecone|milvus|lancedb|faiss|pgvector|neo4j|surrealdb"
    r"|\.jsonl?['\"]|open\([^)]*['\"][wa]|writeFile|fs\.write|json\.dump|pickle\.dump"
    r"|\bDB_PATH\b|\bstorage\b|\bstore\.(save|put|write|upsert)"
    # Rust. The first live batch rejected a crate whose store lives in a file
    # called `core/persistence.rs` because none of the above is Rust.
    r"|std::fs\b|\bfs::write|File::create|OpenOptions|rusqlite|\bsqlx\b|\bdiesel\b|\bsled\b"
    r"|\bredb\b|bincode::|serde_json::to_(writer|vec|string_pretty)"
    # Go, JVM, .NET, browser
    r"|os\.(WriteFile|Create|OpenFile)|ioutil\.WriteFile|\bbbolt\b|\bbadger\b|\bgorm\b"
    r"|Files\.write|FileWriter|\bjdbc\b|File\.WriteAll|localStorage\.setItem|indexedDB",
    re.IGNORECASE,
)

MANIFESTS = (
    "package.json", "pyproject.toml", "setup.py", "setup.cfg", "requirements.txt",
    "Cargo.toml", "go.mod", "pom.xml", "build.gradle", "build.gradle.kts", "Gemfile",
    "composer.json", "pubspec.yaml", "mix.exs", "Package.swift", "deno.json",
)
TEST_CONFIG = (
    "pytest.ini", "tox.ini", "jest.config.js", "jest.config.ts", "vitest.config.ts",
    "vitest.config.js", "karma.conf.js", "phpunit.xml", "conftest.py", "noxfile.py",
)
DOC_FILES = ("README.md", "README.rst", "README.txt", "readme.md", "Readme.md", "README")


@dataclass
class Blob:
    path: str
    sha: str | None
    size: int | None
    text: str | None = None
    excerpt: str | None = None


@dataclass
class Inspection:
    commit: str | None = None
    tree_paths: list[str] = field(default_factory=list)
    truncated: bool = False
    coverage: dict[str, str] = field(default_factory=dict)
    blobs: list[Blob] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def by_path(self, path: str) -> Blob | None:
        for blob in self.blobs:
            if blob.path == path:
                return blob
        return None


def _coverage_for(error: FetchError) -> str:
    return "budget_exceeded" if error.category == BUDGET else "unavailable"


def read_tree(client: Client, owner: str, name: str, commit: str,
              budget: RepoBudget) -> Inspection:
    """One recursive tree listing at the pinned commit.

    GitHub truncates large trees. A truncated tree is recorded as truncated and
    nothing is concluded from what is missing from it — the specification's rule,
    and the only safe reading of a list that the server chose to cut.
    """
    inspection = Inspection(commit=commit)
    try:
        response = client.get(
            api_url("repos", owner, name, "git", "trees", commit, recursive="1"),
            max_bytes=client.limits.tree_bytes, repo_budget=budget, cache=True,
        )
        payload = response.json()
    except FetchError as error:
        inspection.coverage["tree"] = _coverage_for(error)
        inspection.notes.append(f"tree unavailable: {error}")
        return inspection

    entries = payload.get("tree") or []
    inspection.truncated = bool(payload.get("truncated"))
    inspection.tree_paths = [
        entry["path"] for entry in entries
        if entry.get("type") == "blob" and not VENDORED.search(entry["path"])
    ]
    inspection.coverage["tree"] = "sampled" if inspection.truncated else "complete"
    if inspection.truncated:
        inspection.notes.append(
            "GitHub truncated the tree listing; absence of any path below is not evidence"
        )
    return inspection


def choose_blobs(inspection: Inspection, limit: int) -> list[str]:
    """Pick what to read, in the order that answers the gates soonest.

    README first because it is what a promotional repository has instead of an
    implementation; then the manifest and CI, which say what the project claims
    to run; then test files, which is the gate; then the largest implementation
    files, which is where the memory is if there is one.
    """
    paths = inspection.tree_paths
    if not paths:
        return []
    chosen: list[str] = []

    def take(candidates: list[str], count: int) -> None:
        for path in candidates:
            if len(chosen) >= limit:
                return
            if path not in chosen:
                chosen.append(path)
                count -= 1
                if count <= 0:
                    return

    # The top-level README only. A translation is the same promise in another
    # language, and xiaoO's twelve reads included one.
    take([p for p in paths if p in DOC_FILES or p.lower() == "readme.md"], 1)
    take([p for p in paths if p.split("/")[-1] in MANIFESTS and "/" not in p], 2)
    take([p for p in paths if p.startswith(".github/workflows/") and p.endswith((".yml", ".yaml"))], 1)
    take([p for p in paths if p.split("/")[-1] in TEST_CONFIG], 1)

    tests = sorted(
        (p for p in paths if TEST_PATH.search(p) and p.endswith(_CODE_SUFFIXES)),
        key=lambda p: (p.count("/"), len(p)),
    )
    take(tests, 4)

    source = [p for p in paths if _implementation(p)]
    memory_named = [p for p in source if MEMORY_TERMS.search(p)]
    take(sorted(memory_named, key=lambda p: (p.count("/"), len(p))), 3)
    take(sorted(source, key=lambda p: (p.count("/"), len(p))), limit)
    return chosen[:limit]


_SOURCE_SUFFIXES = (
    ".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".go", ".rs", ".java", ".kt", ".rb",
    ".cs", ".php", ".swift", ".scala", ".ex", ".exs", ".c", ".cc", ".cpp", ".h", ".hpp",
    ".sql",
)
# Everything a test file or a manifest can be. Wider than source on purpose; it is
# never used to pick implementation files, which is the mistake it used to make.
_CODE_SUFFIXES = _SOURCE_SUFFIXES + (".yml", ".yaml", ".toml", ".json", ".md")

# Paths that are never the implementation, whatever their suffix. The first live
# batch spent three of ContextMeld's twelve reads on issue templates.
NOT_IMPLEMENTATION = re.compile(
    r"(^|/)\.github/|(^|/)(docs?|examples?|samples?|scripts|benchmarks?|migrations)/"
    r"|(^|/)(LICEN[CS]E|NOTICE|CHANGELOG|CONTRIBUTING)|\.config\.(js|ts|mjs|cjs)$"
    r"|(^|/)\.[^/]+rc(\.json|\.js)?$|\.d\.ts$|(^|/)setup\.(py|ts|js)$",
    re.IGNORECASE,
)


def _implementation(path: str) -> bool:
    return (
        path.endswith(_SOURCE_SUFFIXES)
        and not TEST_PATH.search(path)
        and not NOT_IMPLEMENTATION.search(path)
    )


def read_blobs(client: Client, owner: str, name: str, commit: str, paths: list[str],
               budget: RepoBudget) -> tuple[list[Blob], dict[str, str]]:
    """Read the chosen paths at the pinned commit, under the per-repository caps."""
    limits = client.limits
    blobs: list[Blob] = []
    coverage = "complete"
    for path in paths:
        if budget.blobs >= limits.blobs_per_repo:
            coverage = "sampled"
            break
        if budget.source_bytes >= limits.source_text_bytes_per_repo:
            coverage = "sampled"
            break
        try:
            response = client.get(
                raw_url(f"{owner}/{name}", commit, path), accept="text/plain",
                max_bytes=limits.blob_bytes, reject_binary=True, repo_budget=budget,
            )
        except FetchError as error:
            if error.category in ("too_large", "malformed"):
                blobs.append(Blob(path=path, sha=None, size=None, text=None,
                                  excerpt=f"[not read: {error.category}]"))
                continue
            if error.category == BUDGET:
                coverage = "budget_exceeded"
                break
            coverage = "sampled"
            continue
        budget.blobs += 1
        budget.source_bytes += len(response.body)
        text = response.text()
        blobs.append(Blob(path=path, sha=None, size=len(response.body), text=text,
                          excerpt=text[:400]))
    return blobs, {"blobs": coverage}


# --- classification --------------------------------------------------------

@dataclass
class TestEvidence:
    level: str = UNKNOWN
    reason: str = ""
    files: list[dict[str, Any]] = field(default_factory=list)
    assertion_files: int = 0
    memory_test_files: int = 0
    template_only: bool = False
    ci_configured: bool = False
    ci_workflow: str | None = None
    ci_run_observed: bool = False


def classify_tests(inspection: Inspection, excerpt_chars: int) -> TestEvidence:
    """Six levels, decided from paths plus the contents actually read."""
    evidence = TestEvidence()

    if inspection.coverage.get("tree") in (None, "unavailable", "budget_exceeded"):
        evidence.level = UNKNOWN
        evidence.reason = "the repository tree could not be listed"
        return evidence

    workflow = next(
        (blob for blob in inspection.blobs
         if blob.path.startswith(".github/workflows/") and blob.text),
        None,
    )
    if workflow is not None:
        evidence.ci_workflow = workflow.path
        # A workflow says tests are *configured* to run. Whether a run passed is
        # a claim about a run, and this program has not looked at one.
        evidence.ci_configured = bool(
            re.search(r"\b(pytest|npm (run )?test|yarn test|go test|cargo test|mvn test|"
                      r"gradle test|dotnet test|rspec|vitest|jest|tox|nox)\b",
                      workflow.text, re.IGNORECASE)
        )

    test_paths = [
        path for path in inspection.tree_paths
        if TEST_PATH.search(path) and path.endswith(_CODE_SUFFIXES)
    ]
    read_tests = [
        blob for blob in inspection.blobs
        if blob.text and (TEST_PATH.search(blob.path) or INLINE_TEST.search(blob.text))
    ]

    for blob in read_tests:
        text = blob.text or ""
        has_assertions = bool(ASSERTION.search(text))
        template = bool(TEMPLATE_TEST.search(text)) and len(text) < 4000
        memory_related = bool(MEMORY_TERMS.search(text))
        if has_assertions and not template:
            evidence.assertion_files += 1
            if memory_related:
                evidence.memory_test_files += 1
        evidence.files.append(
            {
                "path": blob.path,
                "bytes": blob.size,
                "content_sha256": sha256_hex(text.encode("utf-8")),
                "assertions": has_assertions,
                "template_shaped": template,
                "memory_related": memory_related,
                "excerpt": truncate(_first_assertion(text) or text[:200], excerpt_chars),
            }
        )

    if evidence.assertion_files:
        evidence.level = MEMORY_SPECIFIC if evidence.memory_test_files else SUBSTANTIVE
        evidence.reason = (
            f"{evidence.assertion_files} inspected test file(s) carry assertions"
            + (f", {evidence.memory_test_files} of them about memory behaviour"
               if evidence.memory_test_files else "")
        )
        return evidence

    if read_tests and all(item["template_shaped"] or not item["assertions"]
                          for item in evidence.files):
        evidence.template_only = True
        if inspection.truncated:
            evidence.level = UNKNOWN
            evidence.reason = (
                "the tests read look like template stubs, but the tree was truncated "
                "so the rest of the suite was not listed"
            )
            return evidence
        evidence.level = FILES_ONLY
        evidence.reason = "test files exist but the ones read assert nothing beyond a template stub"
        return evidence

    if test_paths and not read_tests:
        evidence.level = UNKNOWN
        evidence.reason = (
            f"{len(test_paths)} test-shaped path(s) listed but none were read within budget"
        )
        return evidence

    if inspection.truncated:
        evidence.level = UNKNOWN
        evidence.reason = "no tests in a truncated tree listing, which is not an absence"
        return evidence

    if not inspection.blobs:
        evidence.level = UNKNOWN
        evidence.reason = "no file contents were read"
        return evidence

    mentions = any(
        blob.text and re.search(r"\b(test|tests|testing|coverage)\b", blob.text, re.IGNORECASE)
        for blob in inspection.blobs
        if blob.path.lower().startswith("readme")
    )
    known_layout = any(
        path.endswith((".py", ".ts", ".js", ".go", ".rs", ".java", ".rb", ".cs"))
        for path in inspection.tree_paths
    )
    if not known_layout:
        evidence.level = UNKNOWN
        evidence.reason = "no files in a language whose test layout this program recognises"
        return evidence
    evidence.level = MENTION_ONLY if mentions else ABSENT
    evidence.reason = (
        "the README mentions testing and the tree carries no test file"
        if mentions else
        "no test file in a complete tree listing of a recognised layout"
    )
    return evidence


def _first_assertion(text: str) -> str | None:
    for line in text.splitlines():
        if ASSERTION.search(line):
            return line.strip()[:300]
    return None


@dataclass
class ScopeEvidence:
    in_scope: bool | None = None
    basis: str = "heuristic"
    persistence_paths: list[str] = field(default_factory=list)
    memory_paths: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)


def classify_scope(inspection: Inspection) -> ScopeEvidence:
    """A structural reading, labelled as one.

    This is keyword and structure matching. It is *not* an answer to the atlas's
    actual question — does this persist agent-relevant claims across sessions,
    under an identity that could later be corrected — and it does not claim to
    be. `basis` stays `heuristic` unless a classifier or a human assessment
    replaces it, and every report that carries a heuristic basis says so.
    """
    scope = ScopeEvidence()
    if not inspection.tree_paths:
        scope.reasons.append("no tree listing; scope not assessed")
        return scope

    scope.memory_paths = [p for p in inspection.tree_paths if MEMORY_TERMS.search(p)][:10]
    for blob in inspection.blobs:
        if blob.text and PERSISTENCE.search(blob.text) and not blob.path.lower().startswith("readme"):
            scope.persistence_paths.append(blob.path)
    scope.persistence_paths = scope.persistence_paths[:10]

    code_vocabulary = any(
        blob.text and MEMORY_TERMS.search(blob.text)
        for blob in inspection.blobs
        if not blob.path.lower().startswith("readme") and blob.path.endswith(_CODE_SUFFIXES)
    )

    if scope.persistence_paths and (scope.memory_paths or code_vocabulary):
        scope.in_scope = True
        scope.reasons.append(
            "a store is written to in inspected implementation code, and the memory vocabulary "
            "appears in code rather than only in the README"
        )
    elif not scope.persistence_paths:
        # An absence is only a finding when the whole implementation was read.
        # Eight files of forty-five with no store write in them says nothing
        # about the other thirty-seven, and the first live batch rejected a
        # memory crate on exactly that reading.
        listed = [p for p in inspection.tree_paths if _implementation(p)]
        read = [b.path for b in inspection.blobs if b.text and _implementation(b.path)]
        if listed and len(read) < len(listed):
            scope.in_scope = None
            scope.reasons.append(
                f"no store write in the {len(read)} of {len(listed)} implementation files read; "
                f"the rest were not read, so this is not an absence"
            )
        else:
            scope.in_scope = False
            scope.reasons.append(
                "nothing in the implementation writes to a store, and every implementation "
                "file listed was read"
            )
    else:
        scope.in_scope = None
        scope.reasons.append(
            "a store is written to, but the memory vocabulary appears only outside the code read"
        )
    return scope


@dataclass
class SubstanceEvidence:
    readable: bool | None = None
    code_files: int = 0
    code_bytes: int = 0
    readme_bytes: int = 0
    reasons: list[str] = field(default_factory=list)


def classify_substance(inspection: Inspection) -> SubstanceEvidence:
    """Is there an implementation, or is there a README and a template?"""
    substance = SubstanceEvidence()
    if not inspection.tree_paths:
        substance.reasons.append("no tree listing")
        return substance

    code = [path for path in inspection.tree_paths if _implementation(path)]
    substance.code_files = len(code)
    read_code = [
        blob for blob in inspection.blobs
        if blob.text and blob.path in code
    ]
    substance.code_bytes = sum(blob.size or 0 for blob in read_code)
    readme = next((blob for blob in inspection.blobs
                   if blob.path.lower().startswith("readme") and blob.text), None)
    substance.readme_bytes = readme.size or 0 if readme else 0

    if substance.code_files == 0:
        substance.readable = False
        substance.reasons.append("no implementation file outside tests in the listed tree")
        return substance
    if read_code and substance.code_bytes < 500 and substance.readme_bytes > 4000:
        substance.readable = False
        substance.reasons.append(
            f"{substance.code_bytes} bytes of implementation read against a "
            f"{substance.readme_bytes}-byte README"
        )
        return substance
    if not read_code:
        substance.readable = None
        substance.reasons.append("implementation files listed but none read within budget")
        return substance
    substance.readable = True
    substance.reasons.append(
        f"{substance.code_files} implementation file(s) listed, {len(read_code)} read"
    )
    return substance
