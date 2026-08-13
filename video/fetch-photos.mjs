// Downloads ONE photo per country, searched by that country's own cities.
//
// Why per-country and not per-region: region pooling put a Croatian castle (with a
// Croatian flag) on the Albania and Bulgaria pins. A wrong-country landmark is worse
// than no landmark - it destroys the credibility the data earns.
//
// Strategy per country, in order:
//   1. "<its own biggest tracked city> <country>"   e.g. "Tirana Albania"
//   2. "<country> city"
//   3. "<country> landscape"
//   4. NEUTRAL fallback (abstract/travel imagery) - never another country's photo
//
// Usage:  node fetch-photos.mjs            only missing
//         node fetch-photos.mjs --force    redownload all
//         node fetch-photos.mjs --sheet    also build a contact sheet for review

import { mkdirSync, writeFileSync, existsSync, readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import sharp from 'sharp';
import qs from '../src/data/quality-scores.json' with { type: 'json' };

const OUT = 'public/bg';
const FORCE = process.argv.includes('--force');
const SHEET = process.argv.includes('--sheet');

let KEY = process.env.PEXELS_API_KEY;
if (!KEY && existsSync('.env')) {
  const m = readFileSync('.env', 'utf8').match(/PEXELS_API_KEY\s*=\s*(.+)/);
  if (m) KEY = m[1].trim();
}
if (!KEY) { console.error('PEXELS_API_KEY missing in video/.env'); process.exit(1); }

const title = s => s.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase());

/* Countries whose Pexels results are unreliable under the plain name, plus the
   landmark that actually returns that country. Verified by eye, not guessed. */
const OVERRIDE = {
  lithuania: 'Vilnius Lithuania old town',      // otherwise: Kaliningrad, which is Russia
  germany: 'Berlin Germany Brandenburg Gate',
  thailand: 'Bangkok Thailand temple wat',
  hungary: 'Budapest Hungary parliament Danube',
  norway: 'Norway fjord village',
  china: 'Shanghai China skyline Pudong',
  jamaica: 'Jamaica beach palm resort',
  slovenia: 'Ljubljana Slovenia bridge castle',
  taiwan: 'Taipei Taiwan 101 tower',
  latvia: 'Riga Latvia old town',
  estonia: 'Tallinn Estonia old town',
  serbia: 'Belgrade Serbia fortress',
  albania: 'Tirana Albania city',
  bulgaria: 'Sofia Bulgaria cathedral',
  montenegro: 'Kotor Montenegro bay',
  panama: 'Panama City Panama skyline',        // otherwise: Cartagena, which is Colombia

  georgia: 'Tbilisi Georgia Caucasus',      // otherwise: US state of Georgia
  turkey: 'Istanbul Turkey mosque',          // otherwise: the bird
  jordan: 'Petra Jordan',
  chile: 'Santiago Chile Andes',
  'north-macedonia': 'Skopje Macedonia',
  'dominican-republic': 'Santo Domingo Dominican Republic',
  'el-salvador': 'El Salvador beach volcano',
  'costa-rica': 'Costa Rica rainforest beach',
  'south-africa': 'Cape Town South Africa',
  'south-korea': 'Seoul South Korea',
  'united-arab-emirates': 'Dubai United Arab Emirates',
  'united-kingdom': 'London United Kingdom',
  'czech-republic': 'Prague Czech Republic',
  'new-zealand': 'New Zealand mountains lake',
  'sri-lanka': 'Sri Lanka temple beach',
};

/* Neutral, place-free imagery. Used ONLY when a country cannot be found -
   an honest generic beats a false landmark. */
const NEUTRAL = {
  'neutral-map': 'world map travel planning flatlay',
  'neutral-money': 'savings money jar coins',
  'neutral-laptop': 'working laptop cafe window',
  'neutral-passport': 'passport travel documents flatlay',
  'neutral-suitcase': 'packed suitcase travel',
};

const api = async (params) => {
  const r = await fetch('https://api.pexels.com/v1/search?' + new URLSearchParams(params),
    { headers: { Authorization: KEY } });
  if (!r.ok) throw new Error(`Pexels ${r.status}`);
  return r.json();
};

const grab = async (term) => {
  const res = await api({ query: term, orientation: 'portrait', size: 'large', per_page: '5' });
  const p = (res.photos ?? [])[0];
  if (!p) return null;
  const src = p.src.portrait ?? p.src.large2x ?? p.src.large;
  return { buf: Buffer.from(await (await fetch(src)).arrayBuffer()), alt: p.alt ?? '', term };
};

mkdirSync(OUT, { recursive: true });

/* ── country photos ── */
const countries = Object.entries(qs.countries)
  .filter(([, d]) => d.budget_single)
  .map(([slug, d]) => ({
    slug,
    name: title(slug),
    city: (d.affordable_cities ?? []).slice(-1)[0]?.name ?? null, // biggest = last in list
  }));

const log = [];
let found = 0, fell = 0;

for (const c of countries) {
  const file = join(OUT, `c-${c.slug}.jpg`);
  if (!FORCE && existsSync(file)) { console.log(`${c.slug}: have it`); continue; }

  const terms = OVERRIDE[c.slug]
    ? [OVERRIDE[c.slug], `${c.name} city`, `${c.name} landscape`]
    : [
        c.city ? `${c.city} ${c.name}` : null,
        `${c.name} city skyline`,
        `${c.name} landscape travel`,
      ].filter(Boolean);

  let got = null;
  for (const t of terms) {
    got = await grab(t);
    if (got) break;
  }

  if (got) {
    writeFileSync(file, got.buf);
    log.push({ slug: c.slug, term: got.term, alt: got.alt, ok: true });
    console.log(`${c.slug}: ${Math.round(got.buf.length / 1024)} KB  ("${got.term}")`);
    found++;
  } else {
    log.push({ slug: c.slug, term: null, alt: null, ok: false });
    console.log(`${c.slug}: NOT FOUND -> will use neutral background`);
    fell++;
  }
}

/* ── neutral fallbacks + concept backgrounds for list/contrast pins ── */
for (const [slot, term] of Object.entries(NEUTRAL)) {
  const file = join(OUT, `${slot}.jpg`);
  if (!FORCE && existsSync(file)) continue;
  const got = await grab(term);
  if (got) { writeFileSync(file, got.buf); console.log(`${slot}: ok`); }
}

writeFileSync(join(OUT, 'photo-log.json'), JSON.stringify(log, null, 2));
console.log(`\ncountries with own photo: ${found} | falling back to neutral: ${fell}`);

/* ── contact sheet: 74 thumbnails in one image, so quality can actually be checked ── */
if (SHEET) {
  const files = readdirSync(OUT).filter(f => f.startsWith('c-') && f.endsWith('.jpg')).sort();
  const cols = 10, tw = 200, th = 300, pad = 4;
  const rows = Math.ceil(files.length / cols);
  const tiles = await Promise.all(files.map(async (f, i) => ({
    input: await sharp(join(OUT, f)).resize(tw - pad * 2, th - pad * 2, { fit: 'cover' }).toBuffer(),
    left: (i % cols) * tw + pad,
    top: Math.floor(i / cols) * th + pad,
  })));
  await sharp({
    create: { width: cols * tw, height: rows * th, channels: 3, background: '#0B1220' },
  }).composite(tiles).jpeg({ quality: 82 }).toFile('../shots/contact-sheet.jpg');
  console.log(`contact sheet -> shots/contact-sheet.jpg  (${files.length} countries, order: ${files.map(f=>f.slice(2,-4)).slice(0,3).join(', ')}…)`);
}
