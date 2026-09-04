#!/usr/bin/env python3
"""Count what each reviewed system stores memory in, and which retrieval arms it runs.

The atlas can already say which systems carry a tombstone, because every report
declares its capability flags in frontmatter. It could not say what any of them
stores memory in — that lived in a free-text `matrix.storage` line meant for a
human reading one report, and the first version of this script mined it with
substring rules.

That was wrong in three ways at once and the fixes are recorded in the self-test:
`graph` unanchored matched LangGraph, arms read from the storage line counted
`pgvector` as a vector arm, and clause negation was invisible so "no lexical
arm" counted as a lexical arm. Those bugs are the argument for this file's
current shape: **the read path is frontmatter, not prose.**

Each report declares two flat keys in the same quoted-comma shape the
`capabilities:` flag already uses:

    stack_storage: "sqlite, files"
    stack_retrieval: "lexical, vector"
    stack_source: "seeded"

`stack_source` separates a value a reviewer confirmed against the tree
(`reviewed`) from one derived from that report's own prose by `--seed`
(`seeded`). Both render identically in a table, and only one is evidence, which
is the same reason `check_claim_counts.py` exists. The seeded count can only
fall: `--check` fails if it rises.

Inference survives in exactly one place — `--seed`, which proposes values for a
report that has none. It is never consulted at read time, so a report missing
the keys is an error rather than a silent guess.

What this deliberately does not do: rank engines, call a shape typical, or let a
count stand as an argument about a mechanism. The project has a standing rule
against adoption-as-evidence, and a distribution is the most inviting possible
way to break it.

Usage:
    extract_stack.py [root] [--list] [--json] [--seed] [--write] [--render]
                            [--check] [--self-test]

    --list     one row per report: name, source, storage, retrieval
    --json     the distribution, for anything that wants to render it
    --seed     print the keys each undeclared report would gain, for review
    --write    write those keys into reports that lack them (seeded)
    --render   regenerate the section in content/capabilities.md
    --check    fail if a report lacks the keys, if the seeded count rose, or if
               the rendered section is out of date
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

BEGIN = "<!-- BEGIN GENERATED STACK -->"
END = "<!-- END GENERATED STACK -->"

#: Controlled vocabulary. A value outside these lists is an error, because the
#: point of the field is that two reports naming the same engine spell it the
#: same way.
STORAGE_VOCAB = [
    "sqlite", "postgres", "files", "graph", "chroma", "qdrant", "lancedb",
    "milvus", "weaviate", "pinecone", "faiss", "elastic", "redis", "mongo",
    "duckdb", "kv", "memory", "delegated", "tepindb",
]
ARM_VOCAB = ["lexical", "vector", "graph"]

STORAGE_LABELS = {
    "sqlite": "SQLite", "postgres": "Postgres", "files": "Files on disk",
    "graph": "Graph database", "chroma": "Chroma", "qdrant": "Qdrant",
    "lancedb": "LanceDB", "milvus": "Milvus", "weaviate": "Weaviate",
    "pinecone": "Pinecone", "faiss": "FAISS", "elastic": "Elasticsearch",
    "redis": "Redis", "mongo": "MongoDB", "duckdb": "DuckDB",
    "kv": "Embedded key-value", "memory": "In-process only",
    "tepindb": "TepinDB",
    "delegated": "Delegated to the adopter",
}
ARM_LABELS = {"lexical": "Lexical", "vector": "Vector", "graph": "Graph"}

#: Seeding rules only. Ordered, first match wins nothing — every match counts,
#: because a report may legitimately name two stores.
STORAGE_RULES: list[tuple[str, str]] = [
    ("sqlite", r"sqlite|libsql|better-sqlite|node:sqlite|turso"),
    ("postgres", r"postgres|pgvector|supabase|pglite|\bneon\b|timescale"),
    ("graph", r"neo4j|falkordb|falkor|kuzu|neptune|memgraph|graph database|"
              r"graph provider|graph service|\bcypher\b"),
    ("chroma", r"chroma"),
    ("qdrant", r"qdrant"),
    ("lancedb", r"lance"),
    ("milvus", r"milvus|zilliz"),
    ("weaviate", r"weaviate"),
    ("pinecone", r"pinecone"),
    ("faiss", r"faiss"),
    ("elastic", r"elasticsearch|opensearch"),
    ("redis", r"redis|valkey"),
    ("mongo", r"mongo"),
    ("duckdb", r"duckdb"),
    ("tepindb", r"tepindb|tepin"),
    ("kv", r"badger|pebble|rocksdb|leveldb|lmdb|key-value"),
    ("files", r"\bjson\b|jsonl|markdown|flat file|plain file|yaml file|"
              r"filesystem|file-backed|file backend|\bvault\b|git repositor|"
              r"directory tree|\bfiles in\b|on disk"),
    ("memory", r"in-memory|in memory|in-process|process memory"),
    ("delegated", r"application-chosen|adapters?\b|basestore|orm database|"
                  r"through the framework|abstractions|pluggable|configurable"),
]
ARM_RULES: list[tuple[str, str]] = [
    ("lexical", r"bm25|fts5|\bfts\b|full[- ]text|tsvector|trigram|keyword|"
                r"lexical|inverted index|ripgrep|\bgrep\b|like query|substring|"
                r"exact match|exact-match|tag match|glob"),
    ("vector", r"vector|embedding|cosine|semantic|\bknn\b|k-nn|\bann\b|hnsw|"
               r"\bdense\b|similarity"),
    # \bgraph\b, not `graph` — "LangGraph" is a framework name, not an arm.
    ("graph", r"\bgraph\b|traversal|spreading activation|pagerank|\bbfs\b|"
              r"\bcypher\b|\bedges?\b"),
]
HYBRID_RULE = r"hybrid"

#: Clause openers that mean the arm named next is *absent*. Without this,
#: "no lexical arm" seeds a lexical arm.
NEGATOR = re.compile(r"^\s*(?:no|without|neither|nor|nothing)\b", re.I)
CLAUSE_SPLIT = re.compile(r"[;,.]|—|\s-\s")

#: Reports whose stack was seeded from prose rather than confirmed against the
#: tree. Lower it as reports are reviewed; --check fails if it rises.
#:
#: **Tighten this whenever the live count falls below it.** It sat at 238 while
#: the live count was 217, so twenty-one rows could silently revert to `seeded`
#: without failing anything — a ratchet with slack in it is a ratchet for the
#: twenty-one it does not cover. Set on 2026-08-30 to the live count.
SEEDED_CEILING = 217


def affirmative(text: str) -> str:
    """Drop clauses that deny the thing they name."""
    return " ".join(c for c in CLAUSE_SPLIT.split(text) if not NEGATOR.match(c))


def front_of(text: str) -> str:
    if not text.startswith("---\n"):
        return ""
    end = text.find("\n---\n", 3)
    return text[4:end] if end != -1 else ""


def flat_list(front: str, key: str) -> list[str] | None:
    """Read `key: "a, b"`. None means the key is absent, which is not empty."""
    match = re.search(rf'^{key}: "(.*)"$', front, re.M)
    if not match:
        return None
    return [v.strip() for v in match.group(1).split(",") if v.strip()]


def scalar(front: str, key: str) -> str | None:
    match = re.search(rf'^{key}: "(.*)"$', front, re.M)
    return match.group(1).strip() if match else None


def matrix_field(front: str, field: str) -> str:
    match = re.search(rf'^  {field}: "(.*)"$', front, re.M)
    return match.group(1) if match else ""


def seed(storage_text: str, retrieval_text: str) -> tuple[list[str], list[str]]:
    """Propose values from a report's own prose. Never used at read time."""
    storage = [n for n, pat in STORAGE_RULES if re.search(pat, storage_text.lower())]
    haystack = affirmative(retrieval_text.lower())
    arms = [n for n, pat in ARM_RULES if re.search(pat, haystack)]
    if re.search(HYBRID_RULE, haystack):
        for required in ("lexical", "vector"):
            if required not in arms:
                arms.append(required)
    return storage, sorted(arms, key=ARM_VOCAB.index)


def read_reports(root: Path) -> tuple[list[dict], list[str]]:
    rows, problems = [], []
    for path in sorted((root / "content" / "systems").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        front = front_of(text)
        storage = flat_list(front, "stack_storage")
        arms = flat_list(front, "stack_retrieval")
        source = scalar(front, "stack_source")
        if storage is None or arms is None:
            problems.append(f"{path.stem}: no stack_storage/stack_retrieval in frontmatter")
            continue
        if source not in ("seeded", "reviewed"):
            problems.append(f"{path.stem}: stack_source is {source!r}, expected seeded or reviewed")
        for value in storage:
            if value not in STORAGE_VOCAB:
                problems.append(f"{path.stem}: unknown storage value {value!r}")
        for value in arms:
            if value not in ARM_VOCAB:
                problems.append(f"{path.stem}: unknown retrieval value {value!r}")
        rows.append({
            "name": path.stem, "path": path, "source": source,
            "storage": storage, "retrieval": arms,
            "storage_text": matrix_field(front, "storage"),
            "retrieval_text": matrix_field(front, "retrieval"),
        })
    return rows, problems


def distribution(rows: list[dict]) -> dict:
    storage, arms, combos = Counter(), Counter(), Counter()
    # The same counts over reviewed rows only. A total that mixes 57 readings
    # with 233 inferences into one number reads as a census of 290, and the
    # aggregate was the one place the `stack_source` distinction disappeared —
    # it was on every row in the frontmatter and on none of them in the table.
    storage_reviewed, arms_reviewed = Counter(), Counter()
    for row in rows:
        is_reviewed = row["source"] == "reviewed"
        for value in row["storage"]:
            storage[value] += 1
            if is_reviewed:
                storage_reviewed[value] += 1
        for value in row["retrieval"]:
            arms[value] += 1
            if is_reviewed:
                arms_reviewed[value] += 1
        combos[" + ".join(row["retrieval"]) or "none named"] += 1
    return {
        "total": len(rows),
        "reviewed": sum(1 for r in rows if r["source"] == "reviewed"),
        "seeded": sum(1 for r in rows if r["source"] == "seeded"),
        "no_storage": sum(1 for r in rows if not r["storage"]),
        "no_arm": sum(1 for r in rows if not r["retrieval"]),
        "no_arm_reviewed": sum(
            1 for r in rows if not r["retrieval"] and r["source"] == "reviewed"
        ),
        "storage": dict(storage.most_common()),
        "arms": dict(arms.most_common()),
        "storage_reviewed": dict(storage_reviewed),
        "arms_reviewed": dict(arms_reviewed),
        "arm_combinations": dict(combos.most_common()),
    }


def write_seeds(root: Path) -> int:
    """Add seeded keys to reports that have none. Existing values are never touched."""
    written = 0
    for path in sorted((root / "content" / "systems").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        front = front_of(text)
        if not front or flat_list(front, "stack_storage") is not None:
            continue
        storage, arms = seed(matrix_field(front, "storage"),
                             matrix_field(front, "retrieval"))
        block = (f'stack_storage: "{", ".join(storage)}"\n'
                 f'stack_retrieval: "{", ".join(arms)}"\n'
                 f'stack_source: "seeded"\n')
        anchor = re.search(r"^capabilities: \".*\"\n", front + "\n", re.M)
        if anchor:
            new_front = front.replace(anchor.group(0), anchor.group(0) + block, 1)
        else:  # no capability line: sit above the matrix block instead
            new_front = re.sub(r"^matrix:\n", block + "matrix:\n", front, count=1, flags=re.M)
        path.write_text(text.replace(front, new_front, 1), encoding="utf-8")
        written += 1
    return written


def render_section(dist: dict) -> str:
    lines = [
        BEGIN,
        "",
        "| Stored in | Systems | Read off code | | Retrieval arm | Systems | Read off code |",
        "| --- | ---: | ---: | --- | --- | ---: | ---: |",
    ]
    # .get, not [] — an out-of-vocabulary value is reported by --check as a
    # problem, and rendering it as its raw key beats crashing the build before
    # the problem list is printed.
    storage_rows = [
        (STORAGE_LABELS.get(k, k), v, dist["storage_reviewed"].get(k, 0))
        for k, v in dist["storage"].items()
    ]
    arm_rows = [
        (ARM_LABELS.get(k, k), v, dist["arms_reviewed"].get(k, 0))
        for k, v in dist["arms"].items()
    ]
    arm_rows.append(
        ("No arm named in the review", dist["no_arm"], dist["no_arm_reviewed"])
    )
    for index in range(max(len(storage_rows), len(arm_rows))):
        left = storage_rows[index] if index < len(storage_rows) else ("", "", "")
        right = arm_rows[index] if index < len(arm_rows) else ("", "", "")
        lines.append(
            f"| {left[0]} | {left[1]} | {left[2]} | | {right[0]} | {right[1]} | {right[2]} |"
        )
    lines += [
        "",
        f"Counted across {dist['total']} reports, each of which may name more "
        f"than one store. The **Read off code** column is the part of each row "
        f"confirmed against the tree at the pinned commit: "
        f"{dist['reviewed']} of {dist['total']} reports have been read that way, "
        f"and the other {dist['seeded']} were derived from the review's own "
        "summary lines and are labelled `seeded` rather than `reviewed`. Read "
        "the first number as what the corpus says about itself and the second as "
        "what has been checked.",
        "",
        END,
    ]
    return "\n".join(lines)


def write_render(root: Path, section: str) -> bool:
    page = root / "content" / "capabilities.md"
    text = page.read_text(encoding="utf-8")
    if BEGIN in text and END in text:
        new = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END), section, text, flags=re.S)
    else:
        new = text.rstrip("\n") + "\n\n" + section + "\n"
    if new == text:
        return False
    page.write_text(new, encoding="utf-8")
    return True


def self_test() -> int:
    cases = [
        ("One local SQLite file via `node:sqlite`", "BM25 fused with MiniLM cosine by RRF",
         ["sqlite"], ["lexical", "vector"], "sqlite plus both arms"),
        ("A single Postgres table on Supabase with pgvector HNSW", "Three lanes fused by RRF",
         ["postgres"], [], "pgvector in a storage line is not a retrieval arm"),
        ("Plain markdown in `brain/`", "ripgrep over the tree",
         ["files"], ["lexical"], "files plus lexical only"),
        ("LangGraph `BaseStore`", "framework default",
         ["delegated"], [], "LangGraph is a name, not a graph arm"),
        ("SQLite with FTS5", "hybrid search",
         ["sqlite"], ["lexical", "vector"], "hybrid implies both arms"),
        ("Neo4j, FalkorDB, Kuzu", "BFS across edges",
         ["graph"], ["graph"], "graph store and graph traversal"),
        ("A vault", "Vector search with a scoped predicate; no lexical arm",
         ["files"], ["vector"], "a denied arm is not an arm"),
        ("A vault", "Section extraction by marker; no embeddings, no search engine",
         ["files"], [], "several denials in a row"),
        ("SQLite", "BM25 over FTS5 — no embeddings anywhere",
         ["sqlite"], ["lexical"], "denial after an em dash scopes to its clause"),
    ]
    failures = []
    for storage_text, retrieval_text, want_storage, want_arms, label in cases:
        got_storage, got_arms = seed(storage_text, retrieval_text)
        if got_storage != want_storage:
            failures.append(f"{label}: storage {got_storage} != {want_storage}")
        if got_arms != want_arms:
            failures.append(f"{label}: arms {got_arms} != {want_arms}")

    front = 'title: "x"\nstack_storage: "sqlite, files"\nstack_retrieval: "lexical"\n'
    if flat_list(front, "stack_storage") != ["sqlite", "files"]:
        failures.append("declared storage list misparsed")
    if flat_list(front, "stack_retrieval") != ["lexical"]:
        failures.append("declared arm list misparsed")
    if flat_list(front, "stack_source") is not None:
        failures.append("absent key must read as None, not empty")
    if flat_list('stack_storage: ""\n', "stack_storage") != []:
        failures.append('empty declared list must read as [], not None')

    for failure in failures:
        print(failure, file=sys.stderr)
    if failures:
        return 1
    print(f"self-test: {len(cases) + 4} controls passed")
    return 0


def main() -> int:
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    if "--self-test" in flags:
        return self_test()
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    root = Path(args[0]) if args else ROOT

    if "--seed" in flags or "--write" in flags:
        if "--write" in flags:
            print(f"seeded {write_seeds(root)} reports")
            return 0
        for path in sorted((root / "content" / "systems").glob("*.md")):
            front = front_of(path.read_text(encoding="utf-8"))
            if flat_list(front, "stack_storage") is not None:
                continue
            storage, arms = seed(matrix_field(front, "storage"),
                                 matrix_field(front, "retrieval"))
            print(f'# {path.stem}\n#   {matrix_field(front, "storage")[:100]}')
            print(f'stack_storage: "{", ".join(storage)}"')
            print(f'stack_retrieval: "{", ".join(arms)}"')
            print('stack_source: "seeded"\n')
        return 0

    rows, problems = read_reports(root)
    if problems and "--check" not in flags:
        for problem in problems[:10]:
            print(problem, file=sys.stderr)
        print(f"({len(problems)} problems; run --write to seed)", file=sys.stderr)
    if not rows:
        return 1
    dist = distribution(rows)

    if "--json" in flags:
        print(json.dumps(dist, indent=2))
        return 0
    if "--list" in flags:
        for row in rows:
            print(f"{row['name']:<32} {row['source']:<9} "
                  f"{','.join(row['storage']) or '-':<28} "
                  f"{','.join(row['retrieval']) or '-'}")
        return 0
    if "--render" in flags:
        changed = write_render(root, render_section(dist))
        print("stack section regenerated." if changed
              else "stack section already up to date.")
        return 0

    if "--check" in flags:
        failures = list(problems)
        if dist["seeded"] > SEEDED_CEILING:
            failures.append(f"seeded rows rose to {dist['seeded']} > {SEEDED_CEILING}")
        # Only compare the rendered section once the frontmatter is known good.
        # A malformed value would otherwise be reported as a stale table.
        if not failures:
            page = (root / "content" / "capabilities.md").read_text(encoding="utf-8")
            if render_section(dist) not in page:
                failures.append("capabilities.md stack section is out of date; run --render")
        for failure in failures:
            print(failure, file=sys.stderr)
        if failures:
            return 1
        print(f"{dist['total']} stack rows checked "
              f"({dist['reviewed']} reviewed, {dist['seeded']} seeded).")
        return 0

    print(f"{dist['total']} reports — {dist['reviewed']} reviewed, {dist['seeded']} seeded")
    print("\nstored in (a report may name more than one)")
    for name, count in dist["storage"].items():
        print(f"  {STORAGE_LABELS[name]:<26} {count:>4}")
    print(f"  {'(none named)':<26} {dist['no_storage']:>4}")
    print("\nretrieval arms")
    for name, count in dist["arms"].items():
        print(f"  {ARM_LABELS[name]:<26} {count:>4}")
    print(f"  {'(none named)':<26} {dist['no_arm']:>4}")
    print("\narm combinations")
    for name, count in dist["arm_combinations"].items():
        print(f"  {name:<26} {count:>4}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
