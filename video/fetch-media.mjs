// Downloads vertical stock VIDEO (and photos as fallback) from Pexels into video/public/bg/.
//
// Setup once:  get a free key at https://www.pexels.com/api/  then either
//   set PEXELS_API_KEY in your shell, or drop it into video/.env as PEXELS_API_KEY=xxx
//
// Usage:  node fetch-media.mjs            (only missing slots)
//         node fetch-media.mjs --force    (re-download everything)
//
// Pexels licence allows commercial use with no per-clip attribution; their API terms
// ask for a visible "Pexels" credit, which Background.tsx renders as one small line.

import { mkdirSync, writeFileSync, existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const OUT = 'public/bg';
const FORCE = process.argv.includes('--force');

/* ── key ── */
let KEY = process.env.PEXELS_API_KEY;
if (!KEY && existsSync('.env')) {
  const m = readFileSync('.env', 'utf8').match(/PEXELS_API_KEY\s*=\s*(.+)/);
  if (m) KEY = m[1].trim();
}
if (!KEY) {
  console.error(`
No Pexels API key found.

  1. Sign up (free, instant): https://www.pexels.com/api/
  2. Copy the key
  3. Create video/.env with:   PEXELS_API_KEY=your_key_here

Then run this again.`);
  process.exit(1);
}

/* ── what each beat needs. Order matters: first term that returns a good clip wins. ── */
const SLOTS = {
  'cairo':        ['cairo egypt city', 'egypt pyramids', 'middle east city aerial'],
  'egypt-street': ['egypt market street', 'arabic market bazaar', 'old town street walking'],
  'passport':     ['american passport united states', 'us passport travel', 'passport stamp customs'],
  'airport':      ['airport terminal departure', 'airport departure board', 'plane taking off'],
  'cafe-laptop':  ['working laptop cafe', 'remote work laptop', 'digital nomad working'],
  'danang':       ['vietnam beach city aerial', 'da nang vietnam', 'vietnam coastline drone'],
  'hanoi':        ['hanoi street scooters', 'vietnam street food', 'asia street market night'],
  'batumi':       ['georgia batumi sea', 'black sea promenade', 'seaside city europe'],
  'bangkok':      ['bangkok city aerial', 'thailand city night', 'asia skyline drone'],
  'lisbon':       ['lisbon portugal tram', 'portugal old town', 'europe old street'],
  'hospital':     ['modern hospital corridor', 'doctor hospital clean', 'medical clinic modern'],
  'money':        ['counting money cash', 'savings coins', 'financial planning desk'],
  'malaysia':     ['Kuala Lumpur Malaysia city', 'Malaysia skyline petronas', 'Malaysia city aerial'],
  'spain':        ['Madrid Spain city street', 'Barcelona Spain city', 'Spain old town plaza'],
  'india':        ['India street market delhi', 'Mumbai India city', 'India city street traffic'],
  'map':          ['world map globe', 'globe spinning earth', 'map planning travel'],
};

const api = async (path, params) => {
  const url = `https://api.pexels.com/${path}?` + new URLSearchParams(params);
  const r = await fetch(url, { headers: { Authorization: KEY } });
  if (!r.ok) throw new Error(`Pexels ${r.status}: ${await r.text()}`);
  return r.json();
};

/** pick the best vertical file at or above 1080 wide, smallest that still qualifies */
const pickFile = (files) => {
  const vertical = files
    .filter(f => f.width && f.height && f.height > f.width)
    .filter(f => f.width >= 1000)
    .sort((a, b) => a.width - b.width);
  if (vertical.length) return vertical[0];
  // fall back to the largest landscape and let object-fit crop it
  return files.filter(f => f.width >= 1600).sort((a, b) => a.width - b.width)[0] ?? files[0];
};

mkdirSync(OUT, { recursive: true });
const credits = [];

for (const [slot, terms] of Object.entries(SLOTS)) {
  const mp4 = join(OUT, `${slot}.mp4`);
  if (!FORCE && existsSync(mp4)) { console.log(`${slot}: already have it`); continue; }

  let got = false;
  for (const term of terms) {
    const res = await api('videos/search', {
      query: term,
      orientation: 'portrait',
      size: 'medium',
      per_page: '10',
    });
    // prefer 6-25s clips: long enough to cover a beat, small enough to download fast
    const vid = (res.videos ?? [])
      .filter(v => v.duration >= 5 && v.duration <= 30)
      .sort((a, b) => b.width * b.height - a.width * a.height)[0];
    if (!vid) continue;

    const file = pickFile(vid.video_files);
    if (!file) continue;

    const buf = Buffer.from(await (await fetch(file.link)).arrayBuffer());
    writeFileSync(mp4, buf);
    credits.push({
      slot, type: 'video', term,
      author: vid.user?.name ?? 'Pexels', url: vid.url,
      size: `${file.width}x${file.height}`, duration: vid.duration,
    });
    console.log(`${slot}: ${Math.round(buf.length / 1024 / 1024 * 10) / 10} MB  ${file.width}x${file.height}  ${vid.duration}s  ("${term}")`);
    got = true;
    break;
  }

  if (!got) console.log(`${slot}: NO VIDEO FOUND, tried ${terms.length} terms`);
}

writeFileSync(join(OUT, 'credits.json'), JSON.stringify(credits, null, 2), 'utf8');
console.log(`\ndone -> ${OUT}/  (${credits.length} clips)`);
