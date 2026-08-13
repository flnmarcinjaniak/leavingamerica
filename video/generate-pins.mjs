// Renders the full Pinterest pin library (1000x1500) plus the SEO metadata that
// actually decides whether a pin is found: title, keyword-rich description, link.
//
// Usage:  node generate-pins.mjs           everything
//         node generate-pins.mjs --limit 8 quick test batch
//
// Output: pins-output/*.png  +  pins-output/pins.csv  (title, description, link, board)
//
// Pinterest is a SEARCH engine. The image wins the click, the description wins the
// impression. Both are generated here so they can never drift apart.

import { bundle } from '@remotion/bundler';
import { renderStill, selectComposition } from '@remotion/renderer';
import { mkdirSync, writeFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import qs from '../src/data/quality-scores.json' with { type: 'json' };

const OUT = 'pins-output';
const LIMIT = process.argv.includes('--limit')
  ? Number(process.argv[process.argv.indexOf('--limit') + 1])
  : Infinity;

/* ── data ── */
const title = s => s.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase());

const rows = Object.entries(qs.countries)
  .filter(([, d]) => d.budget_single && d.budget_couple)
  .map(([slug, d]) => ({
    slug,
    name: title(slug),
    monthly: d.budget_single,
    years: +(100000 / d.budget_single / 12).toFixed(1),
    health: d.healthcare,
    safety: d.safety,
    visa: typeof d.visa_days === 'number' ? d.visa_days : null,
    nomad: Boolean(d.nomad_visa),
    cities: d.affordable_cities ?? [],
  }));

const total = rows.length;
const under = t => rows.filter(r => r.monthly <= t).length;
const quality = rows
  .filter(r => r.years >= 5 && r.health >= 7 && r.safety >= 7)
  .sort((a, b) => b.years - a.years);
const cities = rows
  .flatMap(r => r.cities.map(c => ({ ...c, country: r.name, slug: r.slug })))
  .filter(c => typeof c.monthly_usd === 'number')
  .sort((a, b) => a.monthly_usd - b.monthly_usd);

/* ── backgrounds ──
   Every country has its OWN photo (c-<slug>.jpg), fetched by its own landmark.
   Region pooling is gone: it put a Croatian castle and flag on both the Albania
   and Bulgaria pins, which is worse than having no photo at all. */
const bgFor = (slug) => `c-${slug}`;

/* ── the pin library ── */
const pins = [];

// 1. one per country: the long tail that Pinterest search feeds on
rows.forEach((r, i) => {
  pins.push({
    id: `country-${r.slug}`,
    comp: 'pin-country',
    props: {
      name: r.name, bg: bgFor(r.slug), monthly: r.monthly, years: r.years,
      health: r.health, safety: r.safety, visa: r.visa, nomad: r.nomad,
    },
    seo: {
      title: `Cost of Living in ${r.name} 2026: $${r.monthly.toLocaleString()}/Month`,
      description: `How much does it cost to live in ${r.name}? A single person needs about $${r.monthly.toLocaleString()} per month. $100,000 in savings lasts ${r.years} years there. Healthcare scores ${r.health}/10, safety ${r.safety}/10${r.visa ? `, and Americans get ${r.visa} days visa-free` : ''}. Free calculator and full data for ${total} countries. #movingabroad #expat #costofliving #retireabroad`,
      link: `https://leavingamerica.co/countries/${r.slug}/`,
      board: 'Cost of Living Abroad',
    },
  });
});

// 2. cheapest cities: the numbers nobody else publishes
cities.slice(0, 45).forEach((c, i) => {
  pins.push({
    id: `city-${c.slug}-${c.name.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`,
    comp: 'pin-city',
    props: {
      city: c.name, country: c.country, bg: bgFor(c.slug),
      monthly: c.monthly_usd, years: +(100000 / c.monthly_usd / 12).toFixed(1),
    },
    seo: {
      title: `${c.name}, ${c.country}: Live on $${c.monthly_usd.toLocaleString()}/Month`,
      description: `${c.name} in ${c.country} costs around $${c.monthly_usd.toLocaleString()} a month for one person, including rent, food and transport. That means $100,000 in savings lasts ${(100000 / c.monthly_usd / 12).toFixed(1)} years. City-level costs for 222 cities, free to check. #digitalnomad #costofliving #expatlife #budgettravel`,
      link: `https://leavingamerica.co/countries/${c.slug}/`,
      board: 'Cheapest Cities to Live',
    },
  });
});

// 3. rankings: the saveable reference format Pinterest rewards hardest
const listPins = [
  {
    id: 'list-quality',
    eyebrow: 'ranking', accent: '#34D399', bg: 'c-vietnam',
    title: 'Cheap countries that are actually safe',
    metric: 'how long $100,000 lasts',
    rows: quality.slice(0, 10).map(r => ({ left: r.name, right: `${r.years} yrs` })),
    // Title must match what the image shows - a reader who counts must not find a gap.
    seoTitle: 'The 10 Best Cheap Countries With Good Healthcare and Safety (2026)',
    seoDesc: `Only ${quality.length} of ${total} countries combine 5+ years of savings runway with healthcare and safety scores of 7/10 or better. ${quality[0].name} leads at ${quality[0].years} years on $100,000. Cheap and livable overlap far less than cost tables suggest. #retireabroad #expat #movingabroad`,
    link: 'https://leavingamerica.co/statistics/2026-runway-report/',
    board: 'Best Countries to Move To',
  },
  {
    id: 'list-cheapest',
    eyebrow: 'cheapest', accent: '#22D3EE', bg: 'c-georgia',
    title: 'Cheapest cities for Americans in 2026',
    metric: 'cost per month, one person',
    rows: cities.slice(0, 10).map(c => ({ left: c.name, right: `$${c.monthly_usd}` })),
    seoTitle: 'The 10 Cheapest Cities to Live Abroad in 2026 (Real Monthly Costs)',
    seoDesc: `${cities[0].name} in ${cities[0].country} costs $${cities[0].monthly_usd} a month, all in. These are real city-level costs for 222 cities, not national averages. Rent, food and transport included. #costofliving #digitalnomad #budgettravel #expatlife`,
    link: 'https://leavingamerica.co/statistics/2026-runway-report/',
    board: 'Cheapest Cities to Live',
  },
  {
    id: 'list-longest-runway',
    eyebrow: 'savings runway', accent: '#22D3EE', bg: 'neutral-map',
    title: 'Where $100,000 lasts longest',
    metric: 'years your savings last',
    rows: [...rows].sort((a, b) => b.years - a.years).slice(0, 10)
      .map(r => ({ left: r.name, right: `${r.years} yrs` })),
    seoTitle: 'Where $100,000 in Savings Lasts Longest: Top 10 Countries (2026)',
    seoDesc: `In a typical US city $100,000 covers about 2.4 years. Abroad it stretches to more than a decade in several countries. Full ranking of ${total} countries with monthly costs, visa rules and quality-of-life scores. #fire #geoarbitrage #retireabroad #movingabroad`,
    link: 'https://leavingamerica.co/runway/',
    board: 'FIRE and Early Retirement Abroad',
  },
  {
    id: 'list-nomad-visa',
    eyebrow: 'visas', accent: '#34D399', bg: 'neutral-laptop',
    title: 'Countries with a digital nomad visa',
    metric: 'cost per month, one person',
    rows: rows.filter(r => r.nomad).sort((a, b) => a.monthly - b.monthly).slice(0, 10)
      .map(r => ({ left: r.name, right: `$${r.monthly}` })),
    seoTitle: 'The 10 Cheapest Countries With a Digital Nomad Visa (2026)',
    seoDesc: `Only ${rows.filter(r => r.nomad).length} of ${total} tracked countries offer a formal digital nomad visa. These are the cheapest of them, with real monthly costs for one person. Check visa length and income requirements before you book. #digitalnomad #remotework #nomadvisa #expat`,
    link: 'https://leavingamerica.co/countries/',
    board: 'Digital Nomad Visas',
  },
];

listPins.forEach(p => {
  pins.push({
    id: p.id, comp: 'pin-list',
    props: { eyebrow: p.eyebrow, title: p.title, bg: p.bg, rows: p.rows, accent: p.accent, metric: p.metric },
    seo: { title: p.seoTitle, description: p.seoDesc, link: p.link, board: p.board },
  });
});

// 4. contrast pins: the counterintuitive hooks that earn saves
const eg = rows.find(r => r.slug === 'egypt');
const contrastPins = [
  {
    id: 'contrast-visa-trap', bg: 'c-egypt',
    eyebrow: 'the visa trap', title: 'You can afford it. You cannot stay.',
    a: { label: 'What $100,000 buys', value: `${eg.years} years` },
    b: { label: 'What the visa allows', value: `${eg.visa} days` },
    note: `${rows.filter(r => r.visa === 30).length} of ${total} countries do exactly this`,
    seoTitle: 'The Visa Trap: Where Your Money Outlasts Your Welcome',
    seoDesc: `In Egypt $100,000 covers ${eg.years} years of living costs, but the tourist visa runs out after ${eg.visa} days. Affordability and legal access are two different maps, and almost nobody publishes them side by side. Visa lengths and costs for ${total} countries. #movingabroad #expat #visa #digitalnomad`,
    link: 'https://leavingamerica.co/statistics/2026-runway-report/',
    board: 'Moving Abroad Tips',
  },
  {
    id: 'contrast-us-vs-abroad', bg: 'neutral-money',
    eyebrow: 'reality check', title: 'Same savings. Very different life.',
    a: { label: 'Abroad, cheapest', value: `${Math.max(...rows.map(r => r.years))} years` },
    b: { label: 'Typical US city', value: '2.4 years' },
    note: `${under(2000)} of ${total} countries cost under $2,000 a month`,
    seoTitle: 'How Long $100,000 Lasts: Abroad vs a Typical US City',
    seoDesc: `A $3,500/month US city burns through $100,000 in about 2.4 years. Abroad the same money can last more than a decade. ${under(2000)} of ${total} countries cost under $2,000 a month for one person. Free runway calculator. #fire #geoarbitrage #costofliving #retireearly`,
    link: 'https://leavingamerica.co/runway/',
    board: 'FIRE and Early Retirement Abroad',
  },
  {
    id: 'contrast-income', bg: 'neutral-laptop',
    eyebrow: 'remote income', title: 'You need less income than you think.',
    a: { label: '$2,000 a month covers', value: `${under(2000)} countries` },
    b: { label: '$1,000 a month covers', value: `${under(1000)} countries` },
    note: 'at that point your savings stop shrinking',
    seoTitle: `$2,000 a Month Covers Full Living Costs in ${under(2000)} of ${total} Countries`,
    seoDesc: `Stop asking how much you need saved and ask how little you need to earn. $2,000 a month covers full local costs in ${under(2000)} of ${total} countries, $1,000 covers ${under(1000)}. Once income beats local cost, savings never shrink. #remotework #geoarbitrage #digitalnomad #fire`,
    link: 'https://leavingamerica.co/runway/',
    board: 'Remote Work and Income Abroad',
  },
];

contrastPins.forEach(p => {
  pins.push({
    id: p.id, comp: 'pin-contrast',
    props: { eyebrow: p.eyebrow, title: p.title, bg: p.bg, a: p.a, b: p.b, note: p.note },
    seo: { title: p.seoTitle, description: p.seoDesc, link: p.link, board: p.board },
  });
});

/* ── render ── */
const queue = pins.slice(0, LIMIT);
mkdirSync(OUT, { recursive: true });

console.log(`bundling…`);
const serveUrl = await bundle({ entryPoint: 'src/pins/index.ts' });
console.log(`rendering ${queue.length} pins\n`);

let done = 0;
for (const pin of queue) {
  const file = join(OUT, `${pin.id}.png`);
  const composition = await selectComposition({
    serveUrl, id: pin.comp, inputProps: pin.props,
  });
  await renderStill({
    composition, serveUrl, output: file, inputProps: pin.props, overwrite: true,
  });
  done++;
  if (done % 10 === 0 || done === queue.length) console.log(`  ${done}/${queue.length}`);
}

/* ── metadata: this is what makes the pins findable ── */
const esc = s => `"${String(s).replace(/"/g, '""')}"`;
const csv = [
  ['file', 'title', 'description', 'link', 'board'].join(','),
  ...queue.map(p => [
    `${p.id}.png`, p.seo.title, p.seo.description, p.seo.link, p.seo.board,
  ].map(esc).join(',')),
].join('\n');

writeFileSync(join(OUT, 'pins.csv'), '﻿' + csv, 'utf8');
writeFileSync(join(OUT, 'pins.json'), JSON.stringify(queue.map(p => ({ file: `${p.id}.png`, ...p.seo })), null, 2));

const boards = [...new Set(queue.map(p => p.seo.board))];
console.log(`\ndone -> ${OUT}/`);
console.log(`${queue.length} pins, ${boards.length} boards:`);
boards.forEach(b => console.log(`  · ${b} (${queue.filter(p => p.seo.board === b).length})`));
console.log(`\npins.csv holds titles, descriptions and links for scheduling.`);
