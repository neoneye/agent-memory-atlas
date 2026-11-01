// The memory map page (content/map.md): a seeded UMAP layout of every report's feature set, a ranking of the most
// isolated systems with filters, and editorial readings for the top of that ranking. Data comes from
// memory-map.json (scripts/memory_map/run.sh) and readings.json beside this file; d3 v7 is loaded by the page.
(function () {
  const host = document.querySelector("[data-memory-map]");
  if (!host) return;
  const root = document.getElementById("article") || document.body;   // the map, the ranking and the notes are separate blocks of one page

  const THIN = 6;          // fewer features than this: a thin profile, placed but not ranked
  const RARE_PCTL = 0.75;  // isolation at or above this percentile of full profiles counts as rare
  const SOUND_MARKS = 3;   // marks that count as many
  const TOP = 25;          // rows listed in the ranking
  const KIND_ORDER = ["Unusual design", "Uncommon mix of common parts", "Memory inside something else",
    "Older or research original", "Missing the usual parts", ""];

  const css = getComputedStyle(document.documentElement);
  const token = (name) => css.getPropertyValue(name).trim();
  const C = [token("--sage-dark"), token("--amber"), token("--blue"), token("--rose"), token("--violet"),
    token("--cyan"), token("--sage"), token("--ink-soft")];
  const MUTED = token("--line-dark");

  const WORDS = {
    "mark:tombstone": "blocks a rejected fact from coming back", "mark:trust_state": "keeps unverified memories out of answers",
    "mark:bitemporal": "records when a fact was true, not only when it was saved", "mark:scope_enforced": "keeps each user or project apart when recalling",
    "mark:audit_log": "logs every change to memory", "mark:human_review": "lets a person approve memories", "mark:negative_eval": "tests that wrong material stays out",
    "arm:none": "no search: reads by name or loads everything", "arm:graph": "searches by following links between facts",
    "arm:vector": "searches by meaning", "arm:lexical": "searches by keywords",
    "store:files": "keeps memory in plain files", "store:memory": "keeps memory only while running", "store:delegated": "hands storage to another memory system",
    "store:graph": "keeps memory in a graph database", "store:kv": "keeps memory in a key-value store",
    "store:vector_db": "keeps memory in a vector database", "store:database": "keeps memory in a database",
    "writer:llm_extract": "an AI decides what to remember*", "writer:hook": "saves automatically at set moments*", "writer:agent_tool": "the agent saves on purpose*",
    "writer:human": "a person writes the memories*", "writer:indexer": "builds memory from files and documents*", "write:async": "saves in the background*",
    "correct:tombstone": "remembers which values were rejected*", "correct:supersede": "keeps old versions when a fact changes*", "correct:overwrite": "overwrites when a fact changes*",
    "correct:append_only": "never edits, only adds*", "correct:soft_delete": "deletes in a way that can be undone*", "correct:hard_delete": "deletes for good*",
    "forget:ttl": "forgets after a set time*", "forget:decay": "lets unused memories fade*", "forget:none": "never forgets*",
    "bg:none": "no background processing*", "bg:consolidate": "merges memories in the background*", "bg:summarize": "summarises in the background*",
    "bg:reprocess": "reprocesses stored data in the background*", "bg:prune": "prunes old data in the background*",
    "trust:none": "no notion of trust*", "trust:score": "gives each memory a confidence score*", "trust:state": "gives each memory a status*", "trust:provenance": "records where each memory came from*",
    "scope:none": "one shared memory for everyone*", "scope:partition": "a separate store per project or user*", "scope:key": "tags memories by user or project*",
    "scope:model_chosen": "the AI picks where memories go*", "read:model_in_loop": "an AI helps choose what to recall*", "read:addressed_or_whole": "reads by name or loads everything*",
  };

  const fmt3 = d3.format(".3f");
  const num = d3.format(",");
  const state = { color: "quadrant", deploy: "", lang: "", integ: "", sort: { key: "rank", dir: 1 }, pinned: null };
  let rows = [], bySlug = new Map(), ranked = [];

  const all = (sel) => root.querySelectorAll(sel);
  const fill = (name, text) => all(`[data-fill="${name}"]`).forEach((el) => { el.textContent = text; });

  function prepare(map, readings) {
    rows = map.rows;
    const fullIso = rows.filter((r) => r.features.split(" ").length >= THIN).map((r) => r.isolation).sort((a, b) => a - b);
    const cut = fullIso[Math.floor(RARE_PCTL * (fullIso.length - 1))];
    const count = new Map();
    for (const r of rows) for (const f of r.features.split(" ")) count.set(f, (count.get(f) || 0) + 1);
    const read = new Map(readings.map((x) => [x.slug, x]));
    for (const r of rows) {
      const fs = r.features.split(" ");
      r.thin = fs.length < THIN;
      const rare = !r.thin && r.isolation >= cut, many = r.n_marks >= SOUND_MARKS;
      r.quadrant = r.thin ? "Thin profile" : rare ? (many ? "Rare, many marks" : "Rare, few marks") : (many ? "Common, many marks" : "Common, few marks");
      const lacks = (f) => /:(none|memory)$/.test(f);   // an absence explains less than a choice, so it comes after the uncommon choices
      const byCount = (a, b) => count.get(a) - count.get(b);
      const uncommon = fs.filter((f) => !lacks(f) && count.get(f) <= rows.length / 4).sort(byCount);
      const picked = [...uncommon, ...fs.filter(lacks).sort(byCount)].slice(0, 3);
      r.apart = picked.length ? picked.map((f) => {
        const others = count.get(f) - 1, words = WORDS[f] || f;
        return `${words} (${others ? others + " other" + (others === 1 ? "" : "s") : "no other report"})`;
      }).join("; ") : "common choices in an unusual combination";
      r.why = read.get(r.slug)?.why || "";
      r.kind = read.get(r.slug)?.kind || "";
      bySlug.set(r.slug, r);
    }
    ranked = rows.filter((r) => !r.thin).sort((a, b) => b.isolation - a.isolation);
    ranked.forEach((r, i) => { r.rank = i + 1; });
    fill("reports", num(map.meta.reports));
    fill("features", num(map.meta.features));
    fill("commit", map.meta.commit.slice(0, 9));
    fill("rare-many", num(rows.filter((r) => r.quadrant === "Rare, many marks").length));
    fill("rare-few", num(rows.filter((r) => r.quadrant === "Rare, few marks").length));
    fill("sound", String(SOUND_MARKS));
    fill("thin", String(THIN));
    fill("pctl", String(Math.round(RARE_PCTL * 100)));
    fill("cut", fmt3(cut));
    fill("top", String(TOP));
    fill("readings", String(readings.length));
    all(".mm-commit").forEach((a) => { a.href = `https://github.com/neoneye/agent-memory-atlas/commit/${map.meta.commit}`; });
  }

  function palette() {
    return {
      quadrant: { domain: ["Rare, many marks", "Rare, few marks", "Common, many marks", "Common, few marks", "Thin profile"], range: [C[0], C[1], C[2], MUTED, MUTED] },
      family: { domain: ["Local coding-agent memory", "Agent-runtime memory", "Graph, temporal, and symbolic memory", "Host runtimes with pluggable memory", "Hosted and service memory", "Embeddable memory libraries", "Verification and trust-first memory", "Research lineage", "Unassigned"], range: [C[0], C[1], C[2], C[3], C[4], C[5], C[6], C[7], MUTED] },
      marks: { domain: ["0", "1", "2", "3", "4", "5", "6", "7"], range: [MUTED, C[2], C[2], C[0], C[0], C[1], C[1], C[1]] },
      det: { domain: ["0", "1", "2", "3"], range: [C[2], C[0], C[1], C[3]] },
      deploy: { domain: ["local store", "local, local model possible", "cloud store"], range: [C[2], C[0], C[1]] },
    };
  }
  const keyOf = (r) => ({ quadrant: r.quadrant, family: r.family, marks: String(r.n_marks), det: String(r.det), deploy: r.deploy })[state.color];
  const legendLabel = (k) => state.color === "det" ? `${k} model point${k === "1" ? "" : "s"}` : state.color === "marks" ? `${k} mark${k === "1" ? "" : "s"}` : k;

  function drawLegend() {
    all(".mm-legend").forEach((el) => {
      el.replaceChildren();
      const p = palette()[state.color];
      p.domain.forEach((k, i) => {
        const s = document.createElement("span"), dot = document.createElement("i");
        dot.style.background = p.range[i];
        s.append(dot, document.createTextNode(legendLabel(k)));
        el.append(s);
      });
    });
  }

  let plot = null;   // { place } from the last draw
  function drawPlot() {
    const el = root.querySelector(".mm-plot");
    if (!el) return;
    el.replaceChildren();
    const W = Math.max(280, el.clientWidth), H = Math.round(Math.min(Math.max(W * 0.66, 340), 680)), pad = 14;
    const p = palette()[state.color], color = d3.scaleOrdinal(p.domain, p.range);
    const x = d3.scaleLinear(d3.extent(rows, (d) => d.x), [pad, W - pad]);
    const y = d3.scaleLinear(d3.extent(rows, (d) => d.y), [H - pad, pad]);
    const svg = d3.select(el).append("svg").attr("width", "100%").attr("viewBox", `0 0 ${W} ${H}`)
      .attr("role", "img").attr("aria-label", "Scatter of atlas reports by similarity of their memory mechanisms");
    const back = (r) => r.thin || r.quadrant === "Common, few marks";
    const order = [...rows].sort((a, b) => back(b) - back(a));
    svg.append("g").selectAll("circle").data(order).join("circle")
      .attr("cx", (d) => x(d.x)).attr("cy", (d) => y(d.y)).attr("r", 4)
      .attr("fill", (d) => d.thin ? "none" : color(keyOf(d)))
      .attr("stroke", (d) => d.thin ? MUTED : token("--paper-light"))
      .attr("stroke-width", (d) => d.thin ? 1.2 : 0.6)
      .attr("fill-opacity", 0.88);
    const ring = svg.append("circle").attr("r", 8).attr("fill", "none").attr("stroke", token("--ink")).attr("stroke-width", 1.6).attr("visibility", "hidden");
    const hover = svg.append("circle").attr("r", 7).attr("fill", "none").attr("stroke", token("--ink-soft")).attr("stroke-width", 1).attr("visibility", "hidden");
    const delaunay = d3.Delaunay.from(rows, (d) => x(d.x), (d) => y(d.y));
    const tip = d3.select(el).append("div").attr("class", "mm-tip").style("visibility", "hidden");
    const place = () => {
      const t = state.pinned && bySlug.get(state.pinned);
      ring.attr("visibility", t ? "visible" : "hidden");
      if (t) ring.attr("cx", x(t.x)).attr("cy", y(t.y));
    };
    place();
    const nearest = (event) => {
      const [mx, my] = d3.pointer(event, svg.node());
      const scale = W / svg.node().getBoundingClientRect().width;
      const d = rows[delaunay.find(mx, my)];
      return Math.hypot(x(d.x) - mx, y(d.y) - my) < 18 * scale ? d : null;
    };
    svg.on("pointermove", (event) => {
      const d = nearest(event);
      if (!d) { tip.style("visibility", "hidden"); hover.attr("visibility", "hidden"); return; }
      hover.attr("visibility", "visible").attr("cx", x(d.x)).attr("cy", y(d.y));
      tip.selectAll("*").remove();
      tip.append("div").append("b").text(d.title);
      tip.append("div").attr("class", "k").text(d.eyebrow);
      tip.append("div").text(`${d.quadrant} · ${d.family}`);
      tip.append("div").text(`${d.n_marks} mark${d.n_marks === 1 ? "" : "s"} · isolation ${fmt3(d.isolation)}${d.rank ? " · rank " + d.rank : ""}`);
      const bw = el.clientWidth, sx = bw / W, px = x(d.x) * sx, py = y(d.y) * sx;
      tip.style("visibility", "visible");
      const tw = tip.node().offsetWidth, th = tip.node().offsetHeight;
      tip.style("left", `${Math.min(Math.max(4, px + 12), bw - tw - 4)}px`).style("top", `${py - th - 10 < 0 ? py + 12 : py - th - 10}px`);
    });
    svg.on("pointerleave", () => { tip.style("visibility", "hidden"); hover.attr("visibility", "hidden"); });
    svg.on("click", (event) => { const d = nearest(event); pin(d ? d.slug : null); });
    plot = { place };
  }

  function drawDetail() {
    all(".mm-detail").forEach((el) => {
      el.replaceChildren();
      const r = state.pinned && bySlug.get(state.pinned);
      if (!r) { el.textContent = "No system pinned. Click a point, or a row in the ranking."; return; }
      const a = document.createElement("a");
      a.href = `../systems/${r.slug}/`;
      a.textContent = r.title;
      const line = document.createElement("div");
      line.textContent = `${r.eyebrow} · ${r.quadrant} · ${r.n_marks} mark${r.n_marks === 1 ? "" : "s"}${r.marks ? " (" + r.marks.replaceAll("_", " ") + ")" : ""} · isolation ${fmt3(r.isolation)}`;
      const parts = [a, line];
      if (r.why) { const w = document.createElement("p"); w.className = "mm-why"; w.textContent = `${r.kind}. ${r.why}`; parts.push(w); }
      const feats = document.createElement("code");
      feats.textContent = r.features;
      const share = document.createElement("div");
      share.className = "mm-share";
      const url = document.createElement("input");
      url.type = "text"; url.readOnly = true; url.value = location.origin + location.pathname + "#" + r.slug;
      url.setAttribute("aria-label", "Link to this system on the map");
      url.addEventListener("focus", () => url.select());
      const copy = document.createElement("button");
      copy.type = "button"; copy.textContent = "Copy link";
      copy.addEventListener("click", () => {
        const done = () => { copy.textContent = "Copied"; setTimeout(() => { copy.textContent = "Copy link"; }, 1500); };
        const fallback = () => { url.focus(); url.select(); copy.textContent = "Press Ctrl+C or Cmd+C"; };
        try { navigator.clipboard.writeText(url.value).then(done, fallback); } catch { fallback(); }
      });
      share.append(url, copy);
      el.append(...parts, feats, share);
    });
  }

  function matching() {
    return ranked.filter((r) => (!state.deploy || r.deploy === state.deploy) && (!state.lang || r.lang === state.lang)
      && (!state.integ || r.integ.split(" ").includes(state.integ)));
  }

  function drawTable() {
    const m = matching();
    fill("match", num(m.length));
    all(".mm-empty").forEach((e) => { e.hidden = m.length > 0; });
    const { key, dir } = state.sort;
    const val = (r) => key === "kind" ? KIND_ORDER.indexOf(r.kind) : r[key];
    const shown = m.slice(0, TOP).sort((a, b) => (dir * (val(a) - val(b))) || (a.rank - b.rank));
    all(".mm-table tbody").forEach((tb) => {
      tb.replaceChildren();
      for (const r of shown) {
        const tr = document.createElement("tr");
        tr.dataset.key = r.slug;
        if (r.slug === state.pinned) tr.className = "is-pinned";
        const cells = [String(r.rank), r.title, r.kind, r.family, String(r.n_marks), r.apart, r.why];
        const cls = ["num", "", "kind", "", "num", "apart", "why"];
        cells.forEach((v, i) => { const td = document.createElement("td"); td.textContent = v; if (cls[i]) td.className = cls[i]; tr.append(td); });
        tb.append(tr);
      }
    });
    all(".mm-table th[aria-sort]").forEach((th) => {
      const own = th.querySelector(".mm-sort")?.dataset.key === key;
      th.setAttribute("aria-sort", own ? (dir === 1 ? "ascending" : "descending") : "none");
    });
  }

  function pin(slug, { scroll = false } = {}) {
    state.pinned = slug;
    history.replaceState(null, "", slug ? "#" + slug : location.pathname + location.search);
    if (plot) plot.place();
    drawDetail();
    drawTable();
    if (scroll) root.querySelector("#map-card")?.scrollIntoView({ block: "start" });
  }

  function wire() {
    all(".mm-color").forEach((s) => s.addEventListener("change", () => { state.color = s.value; drawLegend(); drawPlot(); }));
    all(".mm-filter").forEach((f) => f.addEventListener("change", () => { state[f.dataset.param] = f.value; drawTable(); }));
    all(".mm-reset").forEach((b) => b.addEventListener("click", () => {
      state.deploy = state.lang = state.integ = "";
      all(".mm-filter").forEach((f) => { f.value = ""; });
      drawTable();
    }));
    all(".mm-sort").forEach((b) => b.addEventListener("click", () => {
      const k = b.dataset.key, s = state.sort;
      state.sort = { key: k, dir: s.key === k ? -s.dir : (k === "n_marks" ? -1 : 1) };
      drawTable();
    }));
    all(".mm-table").forEach((t) => t.addEventListener("click", (event) => {
      const row = event.target.closest("tr[data-key]");
      if (row) pin(row.dataset.key, { scroll: true });
    }));
    window.addEventListener("hashchange", () => {
      const named = decodeURIComponent(location.hash.slice(1));
      if (bySlug.has(named) && named !== state.pinned) pin(named, { scroll: true });
    });
    let width = 0;
    new ResizeObserver(() => {
      const el = root.querySelector(".mm-plot");
      if (el && Math.abs(el.clientWidth - width) > 4) { width = el.clientWidth; drawPlot(); }
    }).observe(root.querySelector(".mm-plot"));
  }

  Promise.all([fetch(host.dataset.map).then((r) => r.json()), fetch(host.dataset.readings).then((r) => r.json())])
    .then(([map, readings]) => {
      prepare(map, readings);
      all(".mm-loading").forEach((e) => { e.hidden = true; });
      wire();
      drawLegend();
      drawPlot();
      drawTable();
      const named = decodeURIComponent(location.hash.slice(1));
      if (bySlug.has(named)) pin(named, { scroll: true }); else drawDetail();
    })
    .catch(() => {
      all(".mm-loading").forEach((e) => { e.hidden = true; });
      all(".mm-failed").forEach((e) => { e.hidden = false; });
    });
})();
