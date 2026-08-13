// Pulls straight from the live site dataset so videos can never drift from the site.
import qs from '../../src/data/quality-scores.json';

type Raw = {
  budget_single?: number;
  budget_couple?: number;
  visa_days?: number;
  nomad_visa?: unknown;
  healthcare?: number;
  safety?: number;
  affordable_cities?: { name: string; monthly_usd?: number }[];
};

const title = (s: string) => s.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase());

export const rows = Object.entries(qs.countries as Record<string, Raw>)
  .filter(([, d]) => d.budget_single && d.budget_couple)
  .map(([slug, d]) => ({
    slug,
    name: title(slug),
    cost: d.budget_single as number,
    visa: typeof d.visa_days === 'number' ? d.visa_days : null,
    nomad: Boolean(d.nomad_visa),
    health: d.healthcare as number,
    safety: d.safety as number,
    cities: d.affordable_cities ?? [],
    y100: +(100000 / (d.budget_single as number) / 12).toFixed(1),
  }));

export const get = (slug: string) => {
  const r = rows.find(x => x.slug === slug);
  if (!r) throw new Error(`unknown country: ${slug}`);
  return r;
};

export const total = rows.length;
export const under = (t: number) => rows.filter(r => r.cost <= t).length;
export const thirtyDay = rows.filter(r => r.visa === 30).length;
export const nomadCount = rows.filter(r => r.nomad).length;

export const quality = rows
  .filter(r => r.y100 >= 5 && r.health >= 7 && r.safety >= 7)
  .sort((a, b) => b.y100 - a.y100);

export const cities = rows
  .flatMap(r => r.cities.map(c => ({ ...c, country: r.name })))
  .filter((c): c is { name: string; monthly_usd: number; country: string } =>
    typeof c.monthly_usd === 'number')
  .sort((a, b) => a.monthly_usd - b.monthly_usd);
