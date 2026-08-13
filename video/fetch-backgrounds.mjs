// Downloads freely-licensed background photos from Wikimedia Commons (no API key needed)
// into video/public/bg/, plus a credits file listing each image's licence and author.
//
// Usage: node fetch-backgrounds.mjs
//
// Wikimedia images are mostly CC BY / CC BY-SA, which require attribution. The credit
// line is rendered small at the bottom of the video by the Background component.
// If you later want attribution-free footage, sign up for a free Pexels API key and
// swap the SOURCES block - the rest of the pipeline stays the same.

import { mkdirSync, writeFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';

const OUT = 'public/bg';
const UA = 'LeavingAmerica-video/1.0 (https://leavingamerica.co; contact@leavingamerica.co)';

// one search term per background slot, keyed by the name the composition asks for
const SOURCES = {
  'cairo': 'Cairo skyline Nile',
  'egypt-market': 'Khan el-Khalili bazaar Cairo',
  'passport': 'passport stamp immigration',
  'world-map': 'world map political',
  'cafe-laptop': 'laptop cafe working',
  'danang': 'Da Nang Vietnam beach city',
  'hanoi': 'Hanoi street old quarter',
  'batumi': 'Batumi Georgia seaside',
  'bangkok': 'Bangkok skyline',
  'lisbon': 'Lisbon tram street',
  'hospital': 'modern hospital corridor',
  'money': 'banknotes cash close up',
};

const api = async (search) => {
  const url = 'https://commons.wikimedia.org/w/api.php?' + new URLSearchParams({
    action: 'query',
    generator: 'search',
    gsrsearch: search,
    gsrlimit: '6',
    gsrnamespace: '6',
    prop: 'imageinfo',
    iiprop: 'url|extmetadata|size',
    iiurlwidth: '1600',
    format: 'json',
  });
  const r = await fetch(url, { headers: { 'User-Agent': UA } });
  const j = await r.json();
  return Object.values(j?.query?.pages ?? {});
};

const meta = (p, key) => p.imageinfo?.[0]?.extmetadata?.[key]?.value?.replace(/<[^>]+>/g, '').trim();

mkdirSync(OUT, { recursive: true });
const credits = [];

for (const [slot, term] of Object.entries(SOURCES)) {
  const file = join(OUT, `${slot}.jpg`);
  if (existsSync(file)) {
    console.log(`${slot}: already downloaded`);
    continue;
  }

  const pages = await api(term);
  // prefer landscape, reasonably large, jpg
  const pick = pages
    .filter(p => p.imageinfo?.[0])
    .filter(p => /\.jpe?g$/i.test(p.title))
    .filter(p => (p.imageinfo[0].width ?? 0) >= 1200)
    .sort((a, b) => (b.imageinfo[0].width ?? 0) - (a.imageinfo[0].width ?? 0))[0];

  if (!pick) { console.log(`${slot}: NOTHING FOUND for "${term}"`); continue; }

  const ii = pick.imageinfo[0];
  const src = ii.thumburl ?? ii.url;
  const buf = Buffer.from(await (await fetch(src, { headers: { 'User-Agent': UA } })).arrayBuffer());
  writeFileSync(file, buf);

  const licence = meta(pick, 'LicenseShortName') ?? 'see Commons';
  const author = meta(pick, 'Artist') ?? 'unknown';
  credits.push({ slot, title: pick.title, author, licence });
  console.log(`${slot}: ${Math.round(buf.length / 1024)} KB  [${licence}]`);
}

writeFileSync(
  join(OUT, 'credits.json'),
  JSON.stringify(credits, null, 2),
  'utf8'
);
console.log(`\ndone -> ${OUT}/  (${credits.length} new)`);
