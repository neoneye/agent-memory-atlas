---
title: Memory System Map
eyebrow: Prototype
description: Every report placed by the memory mechanisms it shares with the others, with a ranking of the systems built least like their neighbours.
root: ..
page_kind: methodology
layout: wide
---

A draft view of the corpus, published for feedback. Each report is described by its design choices: how it stores, searches, writes, corrects, forgets and scopes memory, and which of the atlas's seven marks it carries. Reports that share choices sit close together. The map is a way to find neighbours and outliers, not a ranking of quality.

<div class="mm-card" id="map-card" data-memory-map data-map="../assets/memory-map/memory-map.json" data-readings="../assets/memory-map/readings.json">
<link rel="stylesheet" href="../assets/memory-map/map.css">
<p class="mm-figures"><b data-fill="reports">—</b> reports placed by <b data-fill="features">—</b> features. <b data-fill="rare-many">—</b> are rare in that space and carry at least <b data-fill="sound">—</b> marks; <b data-fill="rare-few">—</b> are rare with fewer.</p>
<div class="mm-bar">
<label for="mm-color">Color by
<select id="mm-color" class="mm-color">
<option value="quadrant">Rarity and marks</option>
<option value="family">Family</option>
<option value="marks">Number of marks</option>
<option value="det">Model decision points</option>
<option value="deploy">Deployment</option>
</select>
</label>
</div>
<p class="mm-note">Nearby points share mechanisms; the axes have no units. Hollow points are thin profiles with fewer than <span data-fill="thin">—</span> features, placed but left out of the ranking. Click a point to pin it; the address then names that system, so the link can be shared.</p>
<p class="mm-note mm-loading">Loading the map…</p>
<p class="mm-note mm-failed" hidden>The map data did not load. The files are in assets/memory-map/ in the repository.</p>
<div class="mm-legend"></div>
<div class="mm-plot"></div>
<div class="mm-detail"></div>
</div>

## Most isolated systems

Systems built unlike their neighbours. These are the ones whose mix of choices looks least like any other report's. *What sets it apart* names up to three choices that at most a quarter of reports share, with how many others make each, then anything the system leaves out that most others have. Unusual does not mean good; the marks show how much of a design is actually built and tested.

<div class="mm-card" id="ranking-card">
<div class="mm-filters">
<label for="mm-deploy">Runs
<select id="mm-deploy" class="mm-filter" data-param="deploy">
<option value="">Anywhere</option>
<option value="local store">Locally</option>
<option value="local, local model possible">Locally, with a local model</option>
<option value="cloud store">With a cloud store</option>
</select>
</label>
<label for="mm-lang">Language
<select id="mm-lang" class="mm-filter" data-param="lang">
<option value="">Any</option>
<option value="multilingual">Multilingual signs</option>
<option value="english">English-only signs</option>
<option value="mixed">Mixed signs</option>
<option value="not_recorded">Not recorded</option>
</select>
</label>
<label for="mm-integ">Reached through
<select id="mm-integ" class="mm-filter" data-param="integ">
<option value="">Anything</option>
<option value="mcp">MCP server</option>
<option value="skill">Skill</option>
<option value="hooks">Hooks or plugin</option>
<option value="library">Library or SDK</option>
<option value="cli">Command line</option>
<option value="http">HTTP API</option>
<option value="harness">Agent harness or runtime</option>
<option value="app">App or UI</option>
</select>
</label>
<button type="button" class="mm-reset">Clear filters</button>
</div>
<p class="mm-note"><b data-fill="match">—</b> ranked systems match; the <span data-fill="top">—</span> highest-ranked are listed. # is the rank by isolation, the average distance to the five most similar reports, from 0 (same choices) to 1 (nothing shared). Sort by #, Kind or Marks with the column headings, and click a row to find it on the map.</p>
<p class="mm-note mm-empty" hidden>No ranked system matches these filters.</p>
<div class="mm-tablebox">
<table class="mm-table">
<thead>
<tr>
<th class="num" aria-sort="ascending"><button type="button" class="mm-sort" data-key="rank">#</button></th>
<th>Report</th>
<th aria-sort="none"><button type="button" class="mm-sort" data-key="kind">Kind</button></th>
<th>Family</th>
<th class="num" aria-sort="none"><button type="button" class="mm-sort" data-key="n_marks">Marks</button></th>
<th>What sets it apart</th>
<th>Reading</th>
</tr>
</thead>
<tbody></tbody>
</table>
</div>
<p class="mm-note">Kind and Reading are an editorial interpretation for the <span data-fill="readings">—</span> highest-ranked systems, written from each report's description and its feature profile; systems further down have neither yet.</p>
<ul class="mm-kinds">
<li><b>Unusual design</b>: a mechanism few others have, such as human approval, rejected-value blocks or deliberate forgetting.</li>
<li><b>Uncommon mix of common parts</b>: ordinary ideas in a combination few others use.</li>
<li><b>Memory inside something else</b>: a robot, a router, a simulator or a trading system that keeps memory.</li>
<li><b>Older or research original</b>: earlier designs from before the conventions newer systems share.</li>
<li><b>Missing the usual parts</b>: unusual mostly for what it lacks, such as search or a working store.</li>
</ul>
</div>

## How the map is made

Every feature comes from a report's frontmatter at the atlas commit the data file was built from, <a class="mm-commit" href="https://github.com/neoneye/agent-memory-atlas"><code data-fill="commit">—</code></a>. Reports added after that commit appear once the file is rebuilt with `scripts/memory_map/run.sh`. Some features are exact; others are read off each report's one-line matrix summaries by keyword rules, which miss and misread phrasing.

- **Exact:** the seven capability marks, the kinds of store in `stack_storage` (grouped by kind, so a choice of vendor is not a design choice), the retrieval arms in `stack_retrieval`, and the family from the hand-kept lists on the [families page](../families/). Reports missing from those lists show as Unassigned.
- **Keyword-derived, unverified:** who writes (an extractor model, a hook, an agent tool, a person, an indexer), background writes, how a correction lands (overwrite, supersede, append-only, soft or hard delete, tombstone), forgetting (expiry, decay, none), background passes, trust (none, score, status, provenance), scope (none, partition, key, model-chosen), and whether a model sits in the read path. In *What sets it apart* these carry an asterisk.
- **Layout:** UMAP over each report's feature set under Jaccard distance, with a fixed seed, so the same reports always land in the same places.
- **Rare** means isolation at or above percentile <span data-fill="pctl">—</span> of reports with full profiles, an isolation of <span data-fill="cut">—</span>. At least <span data-fill="sound">—</span> marks is the line for the second axis.
- **Model decision points** count a model in the write path, in a background pass and in the read path, from the same keyword rules, 0 to 3.
- **Runs** reads hosted databases and services, and local models such as Ollama or llama.cpp, from the storage and integration summaries. **Reached through** reads the integration summary; a system can match several.
- **Language** searches each report's full text for signs of handling other languages (CJK search, segmenters, multilingual embedders, cross-lingual recall) or of English-only paths (the porter stemmer, English stopwords, an English-only step). Most reports say nothing either way, and those show as not recorded, not as English-only.
- The mechanism features do not predict a report's family: the families describe what kind of product a system is, and the map describes how its memory works.

<script src="https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js"></script>
<script src="../assets/memory-map/map.js"></script>
