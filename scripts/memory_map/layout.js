// UMAP over binary feature vectors with a Jaccard distance and a seeded RNG, so the layout is the same on every run.
// Writes the memory map page's data file (assets/memory-map/memory-map.json); run through run.sh.
const fs = require("fs");
const { UMAP } = require("umap-js");

const [, , inFile, outFile] = process.argv;
const data = JSON.parse(fs.readFileSync(inFile, "utf8"));
const names = Object.keys(data.feature_counts);
const index = new Map(names.map((n, i) => [n, i]));
const X = data.rows.map((r) => {
  const v = new Array(names.length).fill(0);
  for (const f of r.features) v[index.get(f)] = 1;
  return v;
});

function jaccard(a, b) {
  let inter = 0, union = 0;
  for (let i = 0; i < a.length; i++) {
    if (a[i] || b[i]) union++;
    if (a[i] && b[i]) inter++;
  }
  return union ? 1 - inter / union : 0;
}

function mulberry32(seed) {
  return function () {
    seed |= 0; seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const umap = new UMAP({ nComponents: 2, nNeighbors: 15, minDist: 0.15, distanceFn: jaccard, random: mulberry32(20261101) });
const Y = umap.fit(X);
const rows = data.rows.map((r, i) => ({
  slug: r.slug, title: r.title, eyebrow: r.eyebrow, family: r.family, n_marks: r.n_marks,
  marks: r.marks.join(" "), det: r.det, deploy: r.deploy, lang: r.lang, integ: r.integ, rarity: r.rarity, isolation: r.isolation,
  features: r.features.join(" "), x: +Y[i][0].toFixed(4), y: +Y[i][1].toFixed(4),
}));
fs.writeFileSync(outFile, JSON.stringify({ meta: { commit: data.commit, reports: rows.length, features: names.length }, rows }));
console.log(rows.length, "points");
