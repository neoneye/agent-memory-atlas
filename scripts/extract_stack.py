#!/usr/bin/env python3
"""Extract the storage engine and retrieval arms each report describes.

The atlas can already answer "which systems have a tombstone" from declared
frontmatter flags. It cannot answer "what do these systems store their memory
in", which is the question most people arrive with and the one the build page
deliberately refuses to answer for them. This script counts it.

Two sources, kept apart on purpose:

* **Declared.** A report may carry a `stack:` block in its frontmatter with
  `storage:` and `retrieval:` lists drawn from the vocabularies below. That is a
  reviewer's judgement at a pinned commit, the same standing as a capability
  flag.
* **Inferred.** Where the block is absent, the engine and arms are guessed by
  substring rules over the free-text `matrix.storage` and `matrix.retrieval`
  lines. This is a *summary of a summary* and it is wrong in both directions: a
  report saying "application-chosen" may ship SQLite in its default path, and a
  storage line that mentions a vector store in passing is counted as one.

The split is printed on every run rather than folded together, because a
declared count and an inferred count look identical in a chart and only one of
them is evidence. `--check` fails when the inferred share rises above a recorded
floor, so back-filling can only move in one direction.

What this deliberately does not do: rank engines, call a shape typical, or let a
count stand as an argument about a mechanism. The project has a standing rule
against adoption-as-evidence and a distribution is the most inviting possible
way to break it.

Usage:
    extract_stack.py [root] [--list] [--proposal] [--json] [--check] [--self-test]

    --list      one row per report: name, source, storage, retrieval
    --proposal  emit the `stack:` block each undeclared report would get, for
                review before pasting — never written automatically
    --json      the distribution as JSON, for a generator to render
    --check     fail if inferred coverage worsens against INFERRED_CEILING
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: Ordered because the first match wins for the primary label, and because a
#: report naming both SQLite and Chroma is a SQLite system with a vector
#: sidecar far more often than the reverse. Every value here is a *substring
#: rule over prose*, not a schema.
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
    ("kv", r"badger|pebble|rocksdb|leveldb|lmdb|key-value"),
    ("files", r"\bjson\b|jsonl|markdown|flat file|plain file|yaml file|"
              r"filesystem|file-backed|file backend|\bvault\b|git repositor|"
              r"directory tree|\bfiles in\b|on disk"),
    ("memory", r"in-memory|in memory|in-process|process memory"),
    ("delegated", r"application-chosen|adapters?\b|basestore|orm database|"
                  r"through the framework|abstractions|pluggable|configurable"),
]

#: Retrieval arms. "hybrid" implies both without naming either, which is why it
#: is a rule of its own rather than a synonym in each list.
ARM_RULES: list[tuple[str, str]] = [
    ("lexical", r"bm25|fts5|\bfts\b|full[- ]text|tsvector|trigram|keyword|"
                r"lexical|inverted index|ripgrep|\bgrep\b|like query|substring|"
                r"exact match|exact-match|tag match|glob"),
    ("vector", r"vector|embedding|cosine|semantic|\bknn\b|k-nn|\bann\b|hnsw|"
               r"\bdense\b|similarity"),
    # \bgraph\b, not `graph` — "LangGraph" is a framework name, not an arm, and
    # the unanchored rule counted it as graph retrieval.
    ("graph", r"\bgraph\b|traversal|spreading activation|pagerank|\bbfs\b|"
              r"\bcypher\b|\bedges?\b"),
]
HYBRID_RULE = r"hybrid"

#: Clause openers that mean the arm named next is *absent*. Without this,
#: "no lexical arm" counts as a lexical arm and "no embeddings, no search
#: engine" counts as a vector one — three reports in the corpus said exactly
#: that. Negation is scoped to the clause, so a later clause still counts.
NEGATOR = re.compile(r"^\s*(?:no|without|neither|nor|nothing)\b", re.I)
CLAUSE_SPLIT = re.compile(r"[;,.]|—|\s-\s")


def affirmative(text: str) -> str:
    """Drop clauses that deny the thing they name."""
    return " ".join(c for c in CLAUSE_SPLIT.split(text) if not NEGATOR.match(c))

STORAGE_VOCAB = [name for name, _ in STORAGE_RULES]
ARM_VOCAB = [name for name, _ in ARM_RULES]

#: Reports whose stack is inferred rather than declared, as of the last time
#: this floor was moved. --check fails if the number rises. It starts at the
#: whole corpus because nothing is declared yet; lowering it is the point.
INFERRED_CEILING = 238


def parse_frontmatter(text: str) -> str:
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    return match.group(1) if match else ""


def matrix_field(front: str, field: str) -> str:
    match = re.search(rf'^  {field}: "(.*)"$', front, re.M)
    return match.group(1) if match else ""


def declared_stack(front: str) -> dict[str, list[str]] | None:
    """Read an explicit `stack:` block. Absent is the normal case for now."""
    block = re.search(r"^stack:\n((?:  \w+: \[.*\]\n)+)", front, re.M)
    if not block:
        return None
    out: dict[str, list[str]] = {}
    for key, raw in re.findall(r"^  (\w+): \[(.*)\]$", block.group(1), re.M):
        values = [v.strip().strip('"\'') for v in raw.split(",") if v.strip()]
        out[key] = values
    return out


def infer(storage_text: str, retrieval_text: str) -> dict[str, list[str]]:
    """Arms come from the retrieval line only.

    Reading arms out of the combined text counted `pgvector` in a storage line
    as a vector arm, which inflates exactly the number a reader would quote.
    An engine that implies an arm still has to say so where retrieval is
    described.
    """
    storage = [n for n, pat in STORAGE_RULES if re.search(pat, storage_text.lower())]
    haystack = affirmative(retrieval_text.lower())
    arms = [n for n, pat in ARM_RULES if re.search(pat, haystack)]
    if re.search(HYBRID_RULE, haystack):
        for required in ("lexical", "vector"):
            if required not in arms:
                arms.append(required)
    return {"storage": storage, "retrieval": sorted(arms, key=ARM_VOCAB.index)}


def read_reports(root: Path) -> list[dict]:
    rows = []
    for path in sorted((root / "content" / "systems").glob("*.md")):
        front = parse_frontmatter(path.read_text(encoding="utf-8"))
        storage_text = matrix_field(front, "storage")
        retrieval_text = matrix_field(front, "retrieval")
        declared = declared_stack(front)
        stack = declared or infer(storage_text, retrieval_text)
        rows.append({
            "name": path.stem,
            "source": "declared" if declared else "inferred",
            "storage": stack.get("storage", []),
            "retrieval": stack.get("retrieval", []),
            "storage_text": storage_text,
            "retrieval_text": retrieval_text,
        })
    return rows


def distribution(rows: list[dict]) -> dict:
    storage = Counter()
    storage_declared = Counter()
    arms = Counter()
    combos = Counter()
    for row in rows:
        for value in row["storage"]:
            storage[value] += 1
            if row["source"] == "declared":
                storage_declared[value] += 1
        for value in row["retrieval"]:
            arms[value] += 1
        combos[" + ".join(row["retrieval"]) or "(none named)"] += 1
    return {
        "total": len(rows),
        "declared": sum(1 for r in rows if r["source"] == "declared"),
        "inferred": sum(1 for r in rows if r["source"] == "inferred"),
        "no_storage_matched": sum(1 for r in rows if not r["storage"]),
        "no_arm_matched": sum(1 for r in rows if not r["retrieval"]),
        "storage": dict(storage.most_common()),
        "storage_declared": dict(storage_declared),
        "arms": dict(arms.most_common()),
        "arm_combinations": dict(combos.most_common()),
    }


def cooccurrence(rows: list[dict], engine: str, arm: str) -> tuple[int, int]:
    """How many reports pair an engine with an arm, and how many name that arm alone."""
    both = [r for r in rows if engine in r["storage"] and arm in r["retrieval"]]
    solo = [r for r in both if r["retrieval"] == [arm]]
    return len(both), len(solo)


def render(rows: list[dict], dist: dict) -> None:
    print(f"{dist['total']} reports — {dist['declared']} declared, "
          f"{dist['inferred']} inferred from prose")
    print()
    print("storage engine named (a report may name more than one)")
    for name, count in dist["storage"].items():
        declared = dist["storage_declared"].get(name, 0)
        suffix = f"  ({declared} declared)" if declared else ""
        print(f"  {name:<11} {count:>4}{suffix}")
    print(f"  {'(unmatched)':<11} {dist['no_storage_matched']:>4}")
    print()
    print("retrieval arms named")
    for name, count in dist["arms"].items():
        print(f"  {name:<11} {count:>4}")
    print(f"  {'(unmatched)':<11} {dist['no_arm_matched']:>4}")
    print()
    print("arm combinations")
    for name, count in dist["arm_combinations"].items():
        print(f"  {name:<24} {count:>4}")
    print()
    both, solo = cooccurrence(rows, "sqlite", "lexical")
    print(f"sqlite with a lexical arm: {both}, of which lexical-only: {solo}")
    both, solo = cooccurrence(rows, "postgres", "vector")
    print(f"postgres with a vector arm: {both}, of which vector-only: {solo}")


def render_list(rows: list[dict]) -> None:
    for row in rows:
        print(f"{row['name']:<32} {row['source']:<9} "
              f"{','.join(row['storage']) or '-':<28} "
              f"{','.join(row['retrieval']) or '-'}")


def render_proposal(rows: list[dict]) -> None:
    """Emit what each undeclared report would gain. Never written for you."""
    for row in rows:
        if row["source"] == "declared":
            continue
        print(f"# {row['name']}")
        print(f"#   storage:   {row['storage_text']}")
        print(f"#   retrieval: {row['retrieval_text']}")
        print("stack:")
        print(f"  storage: [{', '.join(row['storage'])}]")
        print(f"  retrieval: [{', '.join(row['retrieval'])}]")
        print()


def self_test() -> int:
    cases = [
        ("One local SQLite file via `node:sqlite`", "BM25 fused with MiniLM cosine by RRF",
         ["sqlite"], ["lexical", "vector"], "sqlite plus both arms"),
        ("A single Postgres table on Supabase with pgvector HNSW", "Three lanes fused by RRF",
         ["postgres"], [], "postgres recognised, arms unnamed in this line"),
        ("Plain markdown in `brain/`", "ripgrep over the tree",
         ["files"], ["lexical"], "files plus lexical only"),
        ("LangGraph `BaseStore`", "framework default",
         ["delegated"], [], "framework abstraction is its own category"),
        ("SQLite with FTS5", "hybrid search",
         ["sqlite"], ["lexical", "vector"], "hybrid implies both arms"),
        ("Neo4j, FalkorDB, Kuzu", "BFS across edges",
         ["graph"], ["graph"], "graph store and graph traversal"),
        ("A vault", "Vector search with mandatory agent-scoped predicate; no lexical arm",
         ["files"], ["vector"], "a denied arm is not an arm"),
        ("A vault", "Section extraction by marker; no embeddings, no search engine",
         ["files"], [], "several denials in a row"),
        ("SQLite", "BM25 over FTS5 — no embeddings anywhere",
         ["sqlite"], ["lexical"], "denial after an em dash still scopes to its clause"),
    ]
    failures = []
    for storage_text, retrieval_text, want_storage, want_arms, label in cases:
        got = infer(storage_text, retrieval_text)
        if got["storage"] != want_storage:
            failures.append(f"{label}: storage {got['storage']} != {want_storage}")
        if got["retrieval"] != want_arms:
            failures.append(f"{label}: arms {got['retrieval']} != {want_arms}")

    declared = declared_stack("stack:\n  storage: [sqlite]\n  retrieval: [lexical, vector]\n")
    if declared != {"storage": ["sqlite"], "retrieval": ["lexical", "vector"]}:
        failures.append(f"declared block parsed as {declared}")
    if declared_stack("title: x\n") is not None:
        failures.append("absent stack block should read as None")

    for failure in failures:
        print(failure, file=sys.stderr)
    if failures:
        return 1
    print(f"self-test: {len(cases) + 2} controls passed")
    return 0


def main() -> int:
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    if "--self-test" in flags:
        return self_test()
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    root = Path(args[0]) if args else ROOT
    rows = read_reports(root)
    if not rows:
        print(f"no reports found under {root}/content/systems", file=sys.stderr)
        return 1
    dist = distribution(rows)

    if "--json" in flags:
        print(json.dumps(dist, indent=2))
        return 0
    if "--list" in flags:
        render_list(rows)
        return 0
    if "--proposal" in flags:
        render_proposal(rows)
        return 0

    render(rows, dist)
    if "--check" in flags and dist["inferred"] > INFERRED_CEILING:
        print(f"\ninferred coverage worsened: {dist['inferred']} > "
              f"{INFERRED_CEILING}; declare the stack or move the floor",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
