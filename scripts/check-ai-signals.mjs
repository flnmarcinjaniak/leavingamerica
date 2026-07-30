// Scans site source prose for AI-writing signals (em-dashes, cliché vocabulary).
// Usage: node scripts/check-ai-signals.mjs [--file src/pages/about.astro]
import { readdirSync, statSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const only = process.argv.includes('--file')
  ? process.argv[process.argv.indexOf('--file') + 1]
  : null;

function walk(dir, acc = []) {
  for (const f of readdirSync(dir)) {
    const p = join(dir, f);
    if (statSync(p).isDirectory()) walk(p, acc);
    else if (/\.(astro|md|mdx)$/.test(f)) acc.push(p);
  }
  return acc;
}

const SIGNALS = [
  [/\u2014/g, 'em-dash'],
  [/ -- /g, 'double-hyphen'],
  [/\bdelve/gi, 'delve'],
  [/\bunlock\w*/gi, 'unlock'],
  [/tapestry/gi, 'tapestry'],
  [/\bnavigat\w*/gi, 'navigate'],
  [/\bboasts\b/gi, 'boasts'],
  [/underscores\b/gi, 'underscores'],
  [/testament to/gi, 'testament to'],
  [/game.?chang\w*/gi, 'game-changer'],
  [/in today'?s/gi, "in today's"],
  [/it'?s (important|worth) (to note|noting)/gi, 'worth noting'],
  [/\bin conclusion\b/gi, 'in conclusion'],
  [/\bmoreover\b/gi, 'moreover'],
  [/\bfurthermore\b/gi, 'furthermore'],
  [/\bseamless\w*/gi, 'seamless'],
  [/\bvibrant\b/gi, 'vibrant'],
  [/\bleverage\b/gi, 'leverage'],
  [/\bcrucial\b/gi, 'crucial'],
  [/\bmyriad\b/gi, 'myriad'],
  [/\bplethora\b/gi, 'plethora'],
];

const files = only ? [only] : walk('src');
const hits = {};

for (const f of files) {
  const raw = readFileSync(f, 'utf8');
  // Strip style/script blocks so CSS and JS identifiers don't trigger false positives.
  const prose = raw
    .replace(/<style[\s\S]*?<\/style>/g, '')
    .replace(/<script[\s\S]*?<\/script>/g, '');
  for (const [re, name] of SIGNALS) {
    const m = prose.match(re);
    if (m) (hits[f] ||= []).push(`${name} x${m.length}`);
  }
}

const keys = Object.keys(hits).sort();
console.log(`scanned ${files.length} files`);
if (!keys.length) {
  console.log('clean: no AI-writing signals found');
} else {
  console.log(`signals found in ${keys.length} file(s):\n`);
  for (const k of keys) console.log(`${k.split('\\').join('/')}\n   ${hits[k].join(', ')}`);
}
