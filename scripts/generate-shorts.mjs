// Generates ready-to-assemble vertical video frames (1080x1920) + narration scripts
// for TikTok / YouTube Shorts / Instagram Reels, straight from the site dataset.
//
// Usage:  node scripts/generate-shorts.mjs
// Output: shorts-output/<NN-slug>/  (PNG frames + script.txt)
//
// Frames are drawn as SVG and rasterised with sharp (ships with Astro, no extra install).
// Fonts are Windows system fonts so the output matches what you see locally.

import sharp from 'sharp';
import { mkdirSync, writeFileSync, rmSync } from 'node:fs';
import { join } from 'node:path';
import qs from '../src/data/quality-scores.json' with { type: 'json' };

const W = 1080, H = 1920;

/* ── brand ── */
const C = {
  bg1: '#0B1220', bg2: '#12243F',
  white: '#FFFFFF', cyan: '#22D3EE', red: '#EF4444',
  green: '#34D399', gray: '#94A3B8', dim: '#64748B',
};
const FONT_BLACK = 'Arial Black, Arial, sans-serif';
const FONT = 'Arial, sans-serif';

/* ── data ── */
const rows = Object.entries(qs.countries)
  .filter(([, d]) => d.budget_single && d.budget_couple)
  .map(([slug, d]) => ({
    slug,
    name: slug.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
    cost: d.budget_single,
    visa: typeof d.visa_days === 'number' ? d.visa_days : null,
    nomad: !!d.nomad_visa,
    health: d.healthcare,
    safety: d.safety,
    cities: d.affordable_cities || [],
    y100: +(100000 / d.budget_single / 12).toFixed(1),
  }));

const byName = n => rows.find(r => r.slug === n);
const total = rows.length;
const under = t => rows.filter(r => r.cost <= t).length;
const thirtyDay = rows.filter(r => r.visa === 30).length;
const nomadCount = rows.filter(r => r.nomad).length;
const quality = rows.filter(r => r.y100 >= 5 && r.health >= 7 && r.safety >= 7)
  .sort((a, b) => b.y100 - a.y100);
const allCities = rows.flatMap(r => r.cities.map(c => ({ ...c, country: r.name })))
  .filter(c => typeof c.monthly_usd === 'number')
  .sort((a, b) => a.monthly_usd - b.monthly_usd);

/* ── svg helpers ── */
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

const txt = (y, s, { size = 72, color = C.white, weight = 400, font = FONT, x = W / 2 } = {}) =>
  `<text x="${x}" y="${y}" font-family="${font}" font-size="${size}" font-weight="${weight}" fill="${color}" text-anchor="middle">${esc(s)}</text>`;

// Arial Black runs ~0.66em per char; shrink until the line fits inside the safe width.
const fitSize = (s, ideal, maxW = 940, ratio = 0.66) =>
  Math.min(ideal, Math.floor(maxW / (Math.max(String(s).length, 1) * ratio)));

const big = (y, s, o = {}) =>
  txt(y, s, { size: fitSize(s, o.size ?? 210), weight: 900, font: FONT_BLACK, ...o, ...{ size: fitSize(s, o.size ?? 210) } });
const head = (y, s, o = {}) =>
  txt(y, s, { size: fitSize(s, o.size ?? 118), weight: 900, font: FONT_BLACK, ...o, ...{ size: fitSize(s, o.size ?? 118) } });
const label = (y, s, o = {}) =>
  txt(y, s, { size: fitSize(s, o.size ?? 60, 940, 0.55), color: C.gray, ...o, ...{ size: fitSize(s, o.size ?? 60, 940, 0.55) } });

const wrap = (y, s, { size = 88, color = C.white, weight = 900, lh = 1.18, max = 18 } = {}) => {
  const words = String(s).split(' ');
  const lines = [];
  let cur = '';
  for (const w of words) {
    if ((cur + ' ' + w).trim().length > max) { lines.push(cur.trim()); cur = w; }
    else cur += ' ' + w;
  }
  if (cur.trim()) lines.push(cur.trim());
  const step = size * lh;
  const start = y - ((lines.length - 1) * step) / 2;
  return lines.map((l, i) =>
    txt(start + i * step, l, { size, color, weight, font: FONT_BLACK })).join('\n');
};

const badge = () =>
  `<rect x="330" y="1735" width="420" height="76" rx="38" fill="rgba(255,255,255,0.08)" stroke="rgba(255,255,255,0.18)" stroke-width="2"/>` +
  txt(1787, 'leavingamerica.co', { size: 40, color: C.gray });

// OVERLAY mode drops the background so frames can sit on top of stock footage in CapCut.
// A soft top/bottom scrim keeps text readable over busy video.
const OVERLAY = process.argv.includes('--overlay');
const OUT = OVERLAY ? 'shorts-output-overlay' : 'shorts-output';

const frame = body => OVERLAY
  ? `<svg width="${W}" height="${H}" xmlns="http://www.w3.org/2000/svg">
<defs><linearGradient id="scrim" x1="0" y1="0" x2="0" y2="1">
<stop offset="0%" stop-color="#000" stop-opacity="0.72"/>
<stop offset="45%" stop-color="#000" stop-opacity="0.42"/>
<stop offset="100%" stop-color="#000" stop-opacity="0.78"/></linearGradient></defs>
<rect width="${W}" height="${H}" fill="url(#scrim)"/>
${body}
${badge()}
</svg>`
  : `<svg width="${W}" height="${H}" xmlns="http://www.w3.org/2000/svg">
<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
<stop offset="0%" stop-color="${C.bg1}"/><stop offset="100%" stop-color="${C.bg2}"/></linearGradient></defs>
<rect width="${W}" height="${H}" fill="url(#bg)"/>
${body}
${badge()}
</svg>`;

/* ── frame layouts ── */
const L = {
  hook: (line, sub) => frame(wrap(820, line, { size: 104 }) + (sub ? label(1180, sub) : '')),

  bigNumber: (top, value, bottom, color = C.cyan) => frame(
    head(700, top) + big(1000, value, { color }) + label(1120, bottom)
  ),

  contrast: (title, aVal, aLab, bVal, bLab) => frame(
    head(620, title) +
    big(900, aVal, { color: C.cyan, size: 190 }) + label(1000, aLab) +
    txt(1140, 'BUT', { size: 64, color: C.dim, weight: 900, font: FONT_BLACK }) +
    big(1350, bVal, { color: C.red, size: 190 }) + label(1450, bLab)
  ),

  list: (title, items, color = C.cyan) => frame(
    head(480, title) +
    items.map((it, i) =>
      txt(700 + i * 132, it.left, { size: 62, color: C.white, weight: 900, font: FONT_BLACK, x: 130 })
        .replace('text-anchor="middle"', 'text-anchor="start"') +
      txt(700 + i * 132, it.right, { size: 62, color, weight: 900, font: FONT_BLACK, x: W - 130 })
        .replace('text-anchor="middle"', 'text-anchor="end"')
    ).join('\n')
  ),

  cta: line => frame(
    wrap(880, line, { size: 92, color: C.white }) +
    txt(1240, 'Full data, free', { size: 56, color: C.cyan })
  ),
};

/* ── count-up animation: renders a number ticking from 0 to its value ──
   Import the resulting PNG sequence into CapCut at ~25fps for real motion. */
const COUNT_FRAMES = 25;
const countUp = (top, target, bottom, color = C.cyan) => {
  const num = parseFloat(String(target).replace(/[^0-9.]/g, ''));
  const decimals = String(target).includes('.') ? 1 : 0;
  const prefix = String(target).startsWith('$') ? '$' : '';
  const out = [];
  for (let i = 1; i <= COUNT_FRAMES; i++) {
    // ease-out so it decelerates into the final value
    const t = 1 - Math.pow(1 - i / COUNT_FRAMES, 3);
    const val = prefix + (num * t).toFixed(decimals);
    out.push(frame(head(700, top) + big(1000, val, { color }) + label(1120, bottom)));
  }
  return out;
};

/* ── video definitions ── */
const eg = byName('egypt'), ind = byName('india'), tur = byName('turkey'),
      vnm = byName('vietnam'), col = byName('colombia');
const cheapest = allCities[0];

const VIDEOS = [
  {
    slug: 'egypt-visa-trap',
    footage: [
      'Cairo street aerial / Egypt pyramids drone',
      'Egyptian market Khan el Khalili walking',
      'passport stamp close up / airport immigration desk',
      'world map spinning / airport departure board',
      'laptop on cafe table abroad',
    ],
    caption: `You can afford 12 years in Egypt. Your visa lasts 30 days. #movingabroad #expat #digitalnomad #fire`,
    frames: [
      ['hook', L.hook('Your money lasts 12 years here.', 'Your visa lasts 30 days.')],
      ['reveal', countUp('EGYPT', eg.y100, `YEARS ON $100,000`)],
      ['twist', L.contrast('THE CATCH', `${eg.y100}`, 'YEARS YOU CAN AFFORD', `${eg.visa}`, 'DAYS YOU CAN STAY')],
      ['context', L.bigNumber('AND IT IS NOT ALONE', `${thirtyDay}`, `OF ${total} COUNTRIES GIVE 30 DAYS`, C.red)],
      ['cta', L.cta('I tracked all 74. Link in bio.')],
    ],
    script: [
      ['0-2s', 'Your money lasts twelve years in Egypt. Your visa lasts thirty days.'],
      ['2-5s', 'A hundred thousand dollars covers 11.9 years of living costs there.'],
      ['5-9s', 'But the tourist visa runs out after 30 days. Affordability and legal access are two completely different maps.'],
      ['9-12s', `And Egypt is not alone. ${thirtyDay} of 74 countries give Americans just 30 days.`],
      ['12-15s', 'I tracked all of them. Link in bio.'],
    ],
  },
  {
    slug: 'income-threshold',
    footage: [
      'person working laptop beach cafe',
      'money counting close up / bank notes',
      'city skyline timelapse cheap asia',
      'sunset relaxing hammock tropical',
      'laptop on cafe table abroad',
    ],
    caption: `You don't need a million saved. You need $2,000 a month. #fire #geoarbitrage #remotework #expat`,
    frames: [
      ['hook', L.hook('Stop asking how much you need saved.')],
      ['reveal', countUp('$2,000 / MONTH', `${under(2000)}`, `OF ${total} COUNTRIES COVERED`)],
      ['scale', L.list('WHAT INCOME UNLOCKS', [
        { left: '$1,000/mo', right: `${under(1000)} countries` },
        { left: '$1,500/mo', right: `${under(1500)} countries` },
        { left: '$2,000/mo', right: `${under(2000)} countries` },
        { left: '$3,000/mo', right: `${under(3000)} countries` },
      ])],
      ['point', L.hook('At that point your savings stop shrinking.')],
      ['cta', L.cta('74 countries, real numbers. Link in bio.')],
    ],
    script: [
      ['0-3s', 'Everyone asks how much you need saved to move abroad. Wrong question.'],
      ['3-6s', `Ask how little you need to earn. Two thousand a month covers full living costs in ${under(2000)} of 74 countries.`],
      ['6-10s', `A thousand a month covers ${under(1000)}. Three thousand covers ${under(3000)}.`],
      ['10-13s', 'At that point your savings stop shrinking. The runway becomes infinite.'],
      ['13-15s', 'Link in bio.'],
    ],
  },
  {
    slug: 'cheap-not-livable',
    footage: [
      'busy chaotic street traffic asia',
      'modern hospital corridor clean',
      'Vietnam Da Nang beach drone / Malaysia Kuala Lumpur skyline',
      'crowded street night market busy',
      'laptop on cafe table abroad',
    ],
    caption: `Only 13 of 74 cheap countries pass a healthcare and safety check. #expat #retireabroad #movingabroad`,
    frames: [
      ['hook', L.hook('Cheap countries are easy to find. Cheap AND safe is not.')],
      ['reveal', countUp('PASS THE FILTER', `${quality.length}`, `OF ${total} COUNTRIES`, C.green)],
      ['winners', L.list('CHEAP AND LIVABLE', quality.slice(0, 5).map(r => ({
        left: r.name, right: `${r.y100} yrs`,
      })), C.green)],
      ['losers', L.list('WHAT LISTS PUT FIRST', [
        { left: ind.name, right: `safety ${ind.safety}/10` },
        { left: tur.name, right: `safety ${tur.safety}/10` },
        { left: col.name, right: `safety ${col.safety}/10` },
      ], C.red)],
      ['cta', L.cta('Cheap and livable overlap less than you think.')],
    ],
    script: [
      ['0-3s', 'Finding a cheap country is easy. Finding one that is cheap and actually livable is not.'],
      ['3-6s', `Of 74 countries, only ${quality.length} combine five plus years of runway with healthcare and safety scores of seven or better.`],
      ['6-10s', `${quality[0].name} leads at ${quality[0].y100} years, then ${quality[1].name} and ${quality[2].name}.`],
      ['10-13s', `Meanwhile India offers 11 years of runway at a safety score of ${ind.safety} out of 10. Turkey scores ${tur.safety}.`],
      ['13-15s', 'Full breakdown in bio.'],
    ],
  },
  {
    slug: 'cheapest-city',
    footage: [
      'world map close up / globe spinning',
      'Batumi Georgia seaside drone / Black Sea promenade',
      'small european old town street walking',
      'coins stacking / savings jar',
      'laptop on cafe table abroad',
    ],
    caption: `The cheapest city I tracked costs $350 a month. #costofliving #digitalnomad #expat #budgettravel`,
    frames: [
      ['hook', L.hook('Country averages lie. Look at cities.')],
      ['reveal', countUp(cheapest.name.toUpperCase(), `$${cheapest.monthly_usd}`, 'PER MONTH')],
      ['list', L.list('CHEAPEST TRACKED CITIES', allCities.slice(0, 5).map(c => ({
        left: c.name, right: `$${c.monthly_usd}/mo`,
      })))],
      ['math', L.bigNumber('$100,000 THERE LASTS', `${(100000 / cheapest.monthly_usd / 12).toFixed(1)}`, 'YEARS')],
      ['cta', L.cta('222 cities tracked. Link in bio.')],
    ],
    script: [
      ['0-3s', 'National averages hide the real numbers. You do not live in a country, you live in a city.'],
      ['3-6s', `${cheapest.name} in ${cheapest.country} costs ${cheapest.monthly_usd} dollars a month.`],
      ['6-10s', 'That is not a hostel budget. That is rent, food, transport, a normal life.'],
      ['10-13s', `A hundred thousand dollars lasts ${(100000 / cheapest.monthly_usd / 12).toFixed(1)} years there.`],
      ['13-15s', 'I tracked 222 cities. Link in bio.'],
    ],
  },
  {
    slug: 'nomad-visa-gap',
    footage: [
      'digital nomad working laptop poolside',
      'passport visa pages flipping',
      'airport queue immigration line',
      'stressed person paperwork desk',
      'laptop on cafe table abroad',
    ],
    caption: `Only 35 of 74 countries have a digital nomad visa. #digitalnomad #remotework #visa #expat`,
    frames: [
      ['hook', L.hook('Everyone talks about nomad visas. Most countries do not have one.')],
      ['reveal', countUp('HAVE A NOMAD VISA', `${nomadCount}`, `OF ${total} COUNTRIES`)],
      ['gap', L.bigNumber('DO NOT', `${total - nomadCount}`, 'NO FORMAL REMOTE ROUTE', C.red)],
      ['point', L.hook('For those, staying means work, investment, ancestry or border runs.')],
      ['cta', L.cta('Check yours before you book. Link in bio.')],
    ],
    script: [
      ['0-3s', 'Everyone talks about digital nomad visas like they are everywhere. They are not.'],
      ['3-6s', `Of the 74 countries I track, only ${nomadCount} have one.`],
      ['6-10s', `That leaves ${total - nomadCount} with no formal route for remote workers at all.`],
      ['10-13s', 'For those, staying long term means employment, investment, ancestry, or repeated border runs.'],
      ['13-15s', 'Check yours before you book a flight. Link in bio.'],
    ],
  },
  {
    slug: 'vietnam-winner',
    footage: [
      'Vietnam Hanoi street food scooters',
      'Da Nang beach aerial drone Vietnam',
      'Vietnamese hospital or pharmacy modern',
      'India crowded street contrast',
      'laptop on cafe table abroad',
    ],
    caption: `The best value country I found is not the cheapest. #expat #retireabroad #vietnam #fire`,
    frames: [
      ['hook', L.hook('The best value country is not the cheapest one.')],
      ['reveal', countUp(vnm.name.toUpperCase(), `${vnm.y100}`, 'YEARS ON $100,000', C.green)],
      ['scores', L.list('WHY IT WINS', [
        { left: 'Runway', right: `${vnm.y100} yrs` },
        { left: 'Healthcare', right: `${vnm.health}/10` },
        { left: 'Safety', right: `${vnm.safety}/10` },
        { left: 'Monthly cost', right: `$${vnm.cost}` },
      ], C.green)],
      ['contrast', L.contrast('COMPARE', `${ind.y100}`, `${ind.name.toUpperCase()} RUNWAY`, `${ind.safety}/10`, 'ITS SAFETY SCORE')],
      ['cta', L.cta('Longest runway is not the same as best.')],
    ],
    script: [
      ['0-3s', 'The country with the longest runway is not the one you want. The best value is somewhere else.'],
      ['3-7s', `${vnm.name} gives ${vnm.y100} years on a hundred thousand, at ${vnm.cost} dollars a month.`],
      ['7-10s', `Healthcare ${vnm.health} out of 10. Safety ${vnm.safety} out of 10. Both above average.`],
      ['10-13s', `India gives you ${ind.y100} years but scores ${ind.safety} on safety. That is the trade nobody mentions.`],
      ['13-15s', 'Full comparison in bio.'],
    ],
  },
];

/* ── render ── */
rmSync(OUT, { recursive: true, force: true });
mkdirSync(OUT, { recursive: true });

let count = 0;
for (const [i, v] of VIDEOS.entries()) {
  const dir = join(OUT, `${String(i + 1).padStart(2, '0')}-${v.slug}`);
  mkdirSync(dir, { recursive: true });

  for (const [n, [name, svg]] of v.frames.entries()) {
    if (Array.isArray(svg)) {
      // count-up sequence -> its own subfolder, import into CapCut as an image sequence
      const seq = join(dir, `${n + 1}-${name}-seq`);
      mkdirSync(seq, { recursive: true });
      for (const [k, s] of svg.entries()) {
        await sharp(Buffer.from(s)).png()
          .toFile(join(seq, `${String(k + 1).padStart(3, '0')}.png`));
        count++;
      }
    } else {
      await sharp(Buffer.from(svg)).png().toFile(join(dir, `${n + 1}-${name}.png`));
      count++;
    }
  }

  if (v.footage) {
    writeFileSync(join(dir, 'footage.txt'), [
      'FREE STOCK FOOTAGE TO LAYER UNDER THESE FRAMES',
      'Sources: pexels.com/videos · pixabay.com/videos · coverr.co  (all free, no attribution)',
      'Download vertical or crop to 9:16. Put video on the bottom layer, PNG frames on top.',
      '', ...v.footage.map((f, i) => `frame ${i + 1}:  ${f}`),
    ].join('\n'), 'utf8');
  }

  const lines = [
    `VIDEO ${i + 1}: ${v.slug}`,
    '='.repeat(60), '',
    'POST CAPTION:', v.caption, '',
    'NARRATION / ON-SCREEN TEXT (frame per beat):', '',
    ...v.script.map(([t, s], n) => `[${t}]  frame ${n + 1}\n   ${s}\n`),
    '', 'ASSEMBLY NOTES:',
    '- Import frames in order into CapCut, ~3s each.',
    '- Add a trending sound at low volume, or TTS voiceover from the lines above.',
    '- Burn captions: CapCut auto-captions, then fix numbers by hand.',
    '- First 2 seconds decide everything. Do not add an intro.',
  ];
  writeFileSync(join(dir, 'script.txt'), lines.join('\n'), 'utf8');
}

console.log(`${VIDEOS.length} videos, ${count} frames -> ${OUT}/`);
console.log('Frames are 1080x1920 PNG, ready for CapCut.');
