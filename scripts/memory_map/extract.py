"""Feature vectors for every atlas report, from frontmatter only, for the memory map page (content/map.md).

Run through scripts/memory_map/run.sh, which passes the result to layout.js.

Exact features: the seven marks, stack_storage, stack_retrieval, family.
Keyword features: rules over the matrix sentences (write, update_delete,
background, trust, scoping, retrieval, storage, integration). These are rough
and unverified; the page says so.
"""
import json
import math
import re
import subprocess
import sys
from pathlib import Path

ATLAS = Path(sys.argv[1])
OUT = Path(sys.argv[2])
MARKS = ["tombstone", "trust_state", "bitemporal", "scope_enforced", "audit_log", "human_review", "negative_eval"]
# A vendor is not a design choice: stores are grouped by kind before they become features.
STORE_KIND = {
    "chroma": "vector_db", "qdrant": "vector_db", "milvus": "vector_db", "pinecone": "vector_db", "weaviate": "vector_db",
    "faiss": "vector_db", "lancedb": "vector_db",
    "sqlite": "database", "postgres": "database", "duckdb": "database", "dolt": "database", "mongo": "database",
    "elastic": "database", "tepindb": "database",
    "redis": "kv", "kv": "kv",
}
FAMILIES = ["Embeddable memory libraries", "Hosted and service memory", "Agent-runtime memory",
            "Host runtimes with pluggable memory", "Local coding-agent memory",
            "Graph, temporal, and symbolic memory", "Verification and trust-first memory", "Research lineage"]


def frontmatter(text):
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    top, matrix, block = {}, {}, None
    if not m:
        return top, matrix
    for line in m.group(1).split("\n"):
        km = re.match(r"^([a-z_]+):\s*(.*)$", line)
        if km:
            block = km.group(1)
            top[block] = unquote(km.group(2))
            continue
        sm = re.match(r"^  ([a-z_]+):\s*(.*)$", line)
        if sm and block == "matrix":
            matrix[sm.group(1)] = unquote(sm.group(2))
    return top, matrix


def unquote(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == '"' and v[-1] == '"':
        v = v[1:-1].replace('\\"', '"')
    return v


def families(atlas):
    text = (atlas / "content" / "families.md").read_text()
    out = {}
    for fam in FAMILIES:
        m = re.search(r"^## " + re.escape(fam) + r"\n\n(.*?)\n\n", text, re.S | re.M)
        if not m:
            continue
        for slug in re.findall(r"\.\./systems/([a-z0-9-]+)/", m.group(1)):
            out.setdefault(slug, fam)
    return out


NEG = re.compile(r"\b(no|not|nothing|never|none|without|withheld|off|neither|nor|lacks?|absent|unwired|declared)\b", re.I)


def clauses(text):
    return [c for c in re.split(r"[;.]\s+|\s+—\s+|, but ", text) if c.strip()]


def has(text, pat):
    """True when some clause matches pat and carries no negation."""
    return any(re.search(pat, c, re.I) and not NEG.search(c) for c in clauses(text))


def has_raw(text, pat):
    return re.search(pat, text, re.I) is not None


def keyword_features(mx):
    f = set()
    w, ud, bg = mx.get("write", ""), mx.get("update_delete", ""), mx.get("background", "")
    tr, sc, rt = mx.get("trust", ""), mx.get("scoping", ""), mx.get("retrieval", "")
    integ, st = mx.get("integration", ""), mx.get("storage", "")

    # who writes
    llm_write = has(w, r"\bLLM\b|\bmodel\b.{0,40}(extract|writ|decid|distil|summar|classif)|extract(ion|or|s)?\b|distil")
    if llm_write: f.add("writer:llm_extract")
    if has(w, r"\bhooks?\b|lifecycle|on (session|turn|stop)|after (every|each) turn"): f.add("writer:hook")
    if has(w, r"\btools?\b|\bMCP\b|agent-driven|agent calls|the agent writes"): f.add("writer:agent_tool")
    if has(w, r"\b(person|operator|user)\b.{0,30}(writ|edit|add|approv)|manual|hand-edit|by hand"): f.add("writer:human")
    if has(w, r"index(er|es|ing)\b|watch(es|er)|ingest(s|ion)? (of )?(files|documents|repos)"): f.add("writer:indexer")
    if has(w, r"\basync|background|detached|queue|later"): f.add("write:async")

    # correction
    if has(ud, r"tombstone"): f.add("correct:tombstone")
    if has(ud, r"supersed|valid_to|invalidat|new version|versions?\b|revision"): f.add("correct:supersede")
    if has(ud, r"overwrit|in place|replac|upsert|rewrit"): f.add("correct:overwrite")
    if has_raw(ud, r"append-only|nothing (is )?(edited|deleted|removed)|never (deleted|removed|updated|edited)|no (update|edit|delete)"): f.add("correct:append_only")
    if has(ud, r"soft[- ]delet|archiv|trash|retir|inactive|deleted_at|forgotten flag"): f.add("correct:soft_delete")
    if has(ud, r"hard delete|\bDELETE\b|delete[sd]? (by id|the row|a row|rows|records|memor)|removes? (the|a) (row|record|memory|file|note)"): f.add("correct:hard_delete")

    # forgetting
    if has(ud + " " + bg, r"\bTTL\b|expir|\bretention\b"): f.add("forget:ttl")
    if has(ud + " " + bg, r"decay|half-life|forgetting curve"): f.add("forget:decay")
    if has_raw(ud + " " + bg, r"never forgets|nothing (is )?(ever )?(deleted|removed|forgotten)|no (delete|forget|deletion)"): f.add("forget:none")

    # background
    if not bg or has_raw(bg, r"^none\b|^no background|^nothing"):
        f.add("bg:none")
    else:
        if has(bg, r"consolidat|merg|dedup"): f.add("bg:consolidate")
        if has(bg, r"summar|compact|reflect|digest"): f.add("bg:summarize")
        if has(bg, r"re-?index|re-?embed|embed(s|ding)? in the background|extract"): f.add("bg:reprocess")
        if has(bg, r"prun|garbage|evict|clean"): f.add("bg:prune")
    bg_llm = has(bg, r"\bLLM\b|\bmodel\b") and not has(bg, r"^none")

    # trust
    if not tr or has_raw(tr, r"^none\b|^no (source|trust|status|epistemic)"):
        f.add("trust:none")
    else:
        if has(tr, r"confidence|score|weight|float"): f.add("trust:score")
        if has(tr, r"status|state|candidate|verified|pending|quarantin|withheld|rejected|superseded"): f.add("trust:state")
        if has(tr, r"provenance|evidence|source|cite|citation|quote"): f.add("trust:provenance")

    # scope
    if not sc or has_raw(sc, r"^none|^no scop|single[- ]user|global\b"): f.add("scope:none")
    if has(sc, r"physical|one [a-z.]+ per|per[- ](project|agent|user|session) (file|database|directory|folder)"): f.add("scope:partition")
    if has(sc, r"user_id|tenant|namespace|agent_id|workspace|project_id|scope (key|column)|filter|predicate|keyed"): f.add("scope:key")
    if has_raw(sc, r"model[- ](supplied|chosen|named)|any (bank|scope|namespace) the model|caller[- ]chosen|argument"): f.add("scope:model_chosen")

    # retrieval beyond the arms
    rerank = has(rt, r"rerank|re-rank|LLM|model (selects|chooses|ranks|picks)|agentic")
    if rerank: f.add("read:model_in_loop")
    if has(rt, r"by id|addressed|no search|whole|in full|entire|all of it|loaded into"): f.add("read:addressed_or_whole")

    # deployment
    cloud = has(st + " " + integ, r"hosted|cloud|SaaS|managed service|vendor|Supabase|Pinecone|Firestore|DynamoDB|S3\b")
    local_model = has(st + " " + integ + " " + w, r"ollama|local model|llama\.cpp|on-device|offline|no model|without a model|lm studio")

    det = int(llm_write) + int(bg_llm) + int(rerank)
    return f, det, cloud, local_model


LANG_MULTI = re.compile(r"multilingual|multi-lingual|cross-lingual|\bCJK\b|non-English|language detection|jieba|(?<!porter )unicode61|trigram tokeni|word segmentation|segmenter|tokeni[sz]er[^.]{0,60}(Chinese|Japanese|Korean)|(Chinese|Japanese|Korean)[^.]{0,60}(tokeni|segment|search|embedding|query)", re.I)
LANG_EN = re.compile(r"English[- ]only|porter stemmer|\bporter\b|English stop ?words|only English", re.I)
INTEG = [
    ("mcp", r"\bMCP\b"), ("skill", r"\bskills?\b|SKILL\.md"), ("hooks", r"\bhooks?\b|plug-?in"),
    ("library", r"\blibrar(y|ies)\b|\bSDK\b|\bpackage\b|\bcrate\b"), ("cli", r"\bCLI\b|command[- ]line"),
    ("http", r"\bREST\b|\bHTTP\b|\bAPI\b|endpoint"), ("harness", r"harness|runtime|framework|agent OS|operating system"),
    ("app", r"desktop|web app|\bUI\b|dashboard|browser extension|\bpanel\b|front-end"),
]


def language(text):
    m, e = bool(LANG_MULTI.search(text)), bool(LANG_EN.search(text))
    return "mixed" if m and e else "multilingual" if m else "english" if e else "not_recorded"


def integration(mx):
    s = mx.get("integration", "")
    return " ".join(k for k, pat in INTEG if re.search(pat, s, re.I))


def main():
    fam = families(ATLAS)
    rows = []
    for p in sorted((ATLAS / "content" / "systems").glob("*.md")):
        text = p.read_text()
        top, mx = frontmatter(text)
        slug = p.stem
        marks = [m.strip() for m in top.get("capabilities", "").split(",") if m.strip()]
        feats = {f"mark:{m}" for m in marks}
        feats |= {f"store:{STORE_KIND.get(s.strip(), s.strip())}" for s in top.get("stack_storage", "").split(",") if s.strip()}
        arms = [a.strip() for a in top.get("stack_retrieval", "").split(",") if a.strip()]
        feats |= {f"arm:{a}" for a in arms} or {"arm:none"}
        kf, det, cloud, local_model = keyword_features(mx)
        feats |= kf
        rows.append({
            "slug": slug, "title": top.get("title", slug), "eyebrow": top.get("eyebrow", ""),
            "family": fam.get(slug, "Unassigned"), "marks": marks, "n_marks": len(marks),
            "features": sorted(feats), "det": det,
            "deploy": "cloud store" if cloud else ("local, local model possible" if local_model else "local store"),
            "lang": language(text), "integ": integration(mx),
            "licence": top.get("licence", ""), "source_url": top.get("source_url", ""),
            "stack_source": top.get("stack_source", ""),
        })
    # rarity: self-information of present features
    n = len(rows)
    count = {}
    for r in rows:
        for f in r["features"]:
            count[f] = count.get(f, 0) + 1
    for r in rows:
        r["rarity"] = round(sum(-math.log2(count[f] / n) for f in r["features"]), 3)
    # isolation: mean Jaccard distance to the 5 nearest neighbours
    sets = [set(r["features"]) for r in rows]
    for i, r in enumerate(rows):
        d = []
        for j, s in enumerate(sets):
            if i == j:
                continue
            u = len(sets[i] | s)
            d.append(1 - (len(sets[i] & s) / u if u else 1))
        d.sort()
        r["isolation"] = round(sum(d[:5]) / 5, 4)
    commit = subprocess.run(["git", "-C", str(ATLAS), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    OUT.write_text(json.dumps({"n": n, "commit": commit, "feature_counts": dict(sorted(count.items())), "rows": rows}, indent=1))
    print(n, "reports,", len(count), "features")


main()
