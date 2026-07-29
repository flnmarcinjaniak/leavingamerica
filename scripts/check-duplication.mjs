// Detects word-for-word phrase duplication across country prose fields.
// Usage: node scripts/check-duplication.mjs [--min 4] [--ngram 6] [--slug portugal]
import { readFileSync } from 'node:fs';

const args = process.argv.slice(2);
const getArg = (name, def) => {
  const i = args.indexOf(`--${name}`);
  return i !== -1 ? args[i + 1] : def;
};
const MIN_SHARED = parseInt(getArg('min', '4'), 10);
const NGRAM = parseInt(getArg('ngram', '6'), 10);
const FOCUS_SLUG = getArg('slug', null);

const data = JSON.parse(readFileSync(new URL('../src/data/quality-scores.json', import.meta.url), 'utf8'));
const goalArticles = JSON.parse(readFileSync(new URL('../src/data/goal-articles.json', import.meta.url), 'utf8'));

function ngrams(text, n) {
  const words = text.replace(/[^a-zA-Z0-9' ]/g, ' ').split(/\s+/).filter(Boolean);
  const out = [];
  for (let i = 0; i <= words.length - n; i++) out.push(words.slice(i, i + n).join(' ').toLowerCase());
  return out;
}

const freq = new Map();
const sources = [];
for (const [slug, d] of Object.entries(data.countries)) {
  for (const field of ['quick_facts_paragraph', 'fire_article']) {
    if (d[field]) sources.push({ id: `${slug}:${field}`, slug, text: d[field] });
  }
}
for (const [key, text] of Object.entries(goalArticles)) {
  sources.push({ id: `goal:${key}`, slug: `goal:${key}`, text });
}

for (const src of sources) {
  for (const g of new Set(ngrams(src.text, NGRAM))) {
    if (!freq.has(g)) freq.set(g, new Set());
    freq.get(g).add(src.slug);
  }
}

const repeated = [...freq.entries()]
  .filter(([, set]) => set.size >= MIN_SHARED)
  .sort((a, b) => b[1].size - a[1].size);

const affected = new Set(repeated.flatMap(([, set]) => [...set]));

console.log(`${NGRAM}-word phrases shared by ${MIN_SHARED}+ pages: ${repeated.length}`);
console.log(`pages affected: ${affected.size} of ${sources.length} prose sources (${Object.keys(data.countries).length} countries + ${Object.keys(goalArticles).length} goal articles)`);

if (FOCUS_SLUG) {
  console.log(`\nPhrases in "${FOCUS_SLUG}" shared with other pages:`);
  const hits = repeated.filter(([, set]) => set.has(FOCUS_SLUG));
  if (hits.length === 0) console.log('  (none — clean)');
  hits.forEach(([g, set]) => console.log(`  ${set.size}x "${g}"`));
} else {
  console.log('\nTop 20 worst offenders:');
  repeated.slice(0, 20).forEach(([g, set]) =>
    console.log(`  ${set.size}x "${g}" -> ${[...set].slice(0, 5).join(', ')}${set.size > 5 ? '…' : ''}`));
}
