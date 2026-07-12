# Data Pipeline Scripts

This folder contains all scripts that fetch, compute, or enrich data in
`src/data/quality-scores.json`. Read this before running anything, especially
after a long break — it's easy to forget the order and the gotchas.

## ⚠️ Critical rule: never lose enrichment data

`fetch-quality-scores.py` MERGES with the existing JSON instead of overwriting
it (fixed June 2026 after a real incident where an update silently wiped out
`quick_facts_paragraph`, budget data, and all REST Countries geographic fields
for all 55 countries). If you ever rewrite this script from scratch, preserve
that merge behavior — read the existing file first, merge new computed fields
into each country object, never replace the whole object.

## Scripts, in the order they should be run

### 1. `fetch-quality-scores.py` — the core script
Fetches and computes the 8 weighted quality metrics for all 55 countries:
Safety (Global Peace Index via Wikipedia, World Bank homicide rate as fallback),
Healthcare (UHC Service Coverage Index, World Bank), Happiness (World Happiness
Report via Our World in Data), Human Development (HDI via Our World in Data),
Pollution/Traffic (Numbeo), Unemployment/GDP data (World Bank), Internet speed
(Wikipedia), English proficiency (EF EPI via Wikipedia), visa requirements
(Passport Index GitHub), digital nomad visa list.

**Run this first**, before any other script, whenever you need to refresh core
metrics. Takes a few minutes. Safe to re-run — it merges, not overwrites.

**Known fragility:** uses Numbeo (4 scrapes) and Wikipedia (3 scrapes: GPI,
Internet Speeds, EF EPI). Numbeo aggressively rate-limits by IP — if you get
blocked, restart your router/modem for a fresh IP before retrying. Wikipedia
403s were fixed by using an honest, policy-compliant User-Agent
(`LeavingAmericaBot/1.0 (https://leavingamerica.co; contact@leavingamerica.co)`)
instead of impersonating a browser — do not revert this to a fake Chrome
User-Agent, it will start triggering 403s again.

### 2. `recompute-grades.py` — run after #1
Recalculates `grade_percent` and `grade_label` for all 55 countries using the
absolute weighted formula (not percentile ranking — we deliberately moved away
from percentile ranking because it gave countries like Kenya an "F" grade
despite having decent healthcare/GDP growth, just because they ranked low
relative to our curated 55-country list).

**Always run this after #1**, since the underlying metric scores may have changed.

Current weights: Safety 25%, Healthcare 20%, Happiness 15%, HDI 15%,
Pollution 8%, Unemployment 7%, Internet 5%, Traffic 5%.

Current 8 label tiers: Outstanding (90+) / Excellent (80+) / Very good (70+) /
Good (60+) / Moderate (50+) / Mixed (40+) / Limited (30+) / Challenging
(below 30) — all suffixed "destination".

### 3. `fetch-monthly-budget.py` — run occasionally, NOT every time
Fetches `budget_single`, `budget_couple`, `cost_index`, `us_comparison`, and
`affordable_cities` from the WhereNext open data API (getwherenext.com). No
auth needed, no rate limit hit so far.

**Run this only when you want fresh cost-of-living data** — not part of the
regular refresh cycle, since this data doesn't change often.

**Known issue:** the `affordable_cities` field from WhereNext has been found
unreliable for some countries (e.g. Poland showed Gdansk as more expensive than
Warsaw, contradicting real cost-of-living data; Singapore's "affordable" cities
were priced ABOVE the national average). We stopped displaying this field on
country pages and replaced it with a "Getting Around" section using REST
Countries data instead. The field is still fetched/stored but not shown — if
you want to re-enable it, verify the data manually first.

### 4. `fetch-country-facts.py` — run rarely, data barely changes
Fetches `area_km2`, `population`, `capital`, `languages`, `currencies`,
`demonym`, `driving_side`, `borders`, `timezones`, `landlocked`, `gini`,
`memberships`, `government_type`, and `continents` from the REST Countries v5
API.

**Requires an API key** — stored in `.env` as `RESTCOUNTRIES_API_KEY` (free
tier, 500 requests/month, sign up at restcountries.com/sign-up). This data
essentially never changes (population/borders/languages are stable), so there's
no need to re-run this often — once every few months is plenty.

**Important:** uses `codes.alpha_2` as a direct query parameter (e.g.
`?codes.alpha_2=PT`), NOT a `filter=` parameter — the filter syntax doesn't
work on this API despite some documentation suggesting otherwise.

**Rate limit note:** Free tier is 500 requests/month. Fetching all 82
countries uses most of this allowance in one run. If you need to add more
countries before your monthly limit resets, check your usage at
restcountries.com first.

### 5. `generate-quick-facts.py` — run rarely, costs API credits
Generates the editorial "WHAT [COUNTRY] IS ACTUALLY LIKE" paragraph for each
country by calling the Claude API, using only the real facts already in the JSON
(population, capital, languages, memberships, etc — never inventing anything).
Costs a small amount of Anthropic API credit (roughly $0.50–1.50 for all 55
countries with Sonnet).

**Requires `ANTHROPIC_API_KEY` in `.env`.** Run this AFTER #4 (country-facts),
since it depends on having fresh geographic data to build paragraphs from. Only
re-run if you want to regenerate the editorial copy — it's not part of the
regular metrics refresh.

### 6. `fetch-english-proficiency-only.py` — standalone Wikipedia fallback
Fetches only the EF English Proficiency Index from Wikipedia and merges it into
the existing JSON without touching any other fields. Use this if step #1 failed
or was skipped due to a Wikipedia 403 on the English proficiency page.

**Best run after restarting the modem** (fresh IP), since Wikipedia 403s on
EF EPI typically happen when the same IP has already hit 2+ Wikipedia pages
in the same session (GPI + Internet Speeds in step #1).

### 7. `generate-compare-content.py` — run quarterly or on tax change, costs API credits
Generates 450-550 word comparative editorial prose for each of the 55 /compare/ pairs
by calling the Claude API. Stores results in `quality-scores.json` under the top-level
`compare_pairs` object (keyed by canonical pair slug, e.g. `"portugal-vs-spain"`).

**Requires `ANTHROPIC_API_KEY` in `.env`.** Run only when underlying cost, safety,
or tax data has actually changed since the last run — not blindly every quarter.
Estimated API cost: ~$1-2 for all 55 pairs with Sonnet.

**Tax exception:** if `tax_system` changes for any country (new legislation), run
this immediately outside the normal quarterly cycle — stale tax information in
comparison text is more misleading than a cost figure that's $50 off.

Usage:
```
py scripts/generate-compare-content.py                    # skip already generated
py scripts/generate-compare-content.py --force            # regenerate all 55
py scripts/generate-compare-content.py portugal-vs-spain  # one pair only
```

---

## Refresh schedule

### Monthly
```
py scripts/fetch-quality-scores.py
py scripts/recompute-grades.py
```
Refreshes: safety, healthcare, happiness, HDI, pollution, unemployment, internet,
traffic for all 82 countries. Sources: Numbeo, World Bank, Wikipedia, Our World
in Data. No request limits to worry about. Safe to run any time.

### Quarterly (once every 3 months)
```
py scripts/fetch-monthly-budget.py
py scripts/fetch-country-facts.py        # CHECK RATE LIMIT FIRST (see note below)
py scripts/generate-compare-content.py  # ONLY if base data actually changed
```

**fetch-country-facts.py rate limit:** REST Countries free tier = 500 requests/month,
resets on the 20th of each month. Fetching all 82 countries uses ~82 requests. Check
your usage at restcountries.com before running.

**generate-compare-content.py:** run only when `budget_single`, `safety`, or
`tax_system` values have actually changed since the last run. If the quarterly
fetch-monthly-budget and fetch-quality-scores runs produced no meaningful changes,
skip this script and save the API credits.

### Rarely — only when adding new countries or conscious style decision
```
py scripts/generate-quick-facts.py   # only for slugs missing quick_facts_paragraph
```

### Exception: immediate run outside normal schedule
If `tax_system` changes for any country (new legislation, country changes to
territorial/worldwide/zero), run `generate-compare-content.py` immediately for
all pairs containing that country. Use the `portugal-vs-spain`-style argument
to target only affected pairs. Stale tax info in compare text is more misleading
than a stale cost figure.

### After every fetch — always, regardless of what you ran
```
git add .
git commit -m "Data refresh: describe what was updated"
git push origin main
npm run build
py scripts/ping-indexnow.py
```

---

## Typical refresh workflow

**Quick metrics refresh (monthly-ish):**
```
python scripts/fetch-quality-scores.py
python scripts/recompute-grades.py
```
If step 1 fails on English Proficiency (403):
```
# restart modem, then:
python scripts/fetch-english-proficiency-only.py
python scripts/recompute-grades.py
```

**Full refresh after adding new countries:**
```
python scripts/fetch-quality-scores.py
python scripts/recompute-grades.py
python scripts/fetch-monthly-budget.py
python scripts/fetch-country-facts.py
python scripts/generate-quick-facts.py   # only for countries missing quick_facts_paragraph
```

**After changing grade weights or tier labels only** (no data change needed):
```
python scripts/recompute-grades.py
```

**Quarterly PPP refresh** (purchasing power values embedded in the calculator):
```
python scripts/fetch-ppp-embed.py
```
This updates the `STATIC_PPP` object in `src/pages/index.astro` directly. PPP values change slowly (World Bank updates annually), so quarterly is more than enough. Exchange rates are always live — only PPP needs this script.

---

## Fields written by each script

| Field | Written by |
|---|---|
| `safety`, `healthcare`, `happiness`, `hdi`, `pollution`, `traffic`, `unemployment`, `internet` | #1 fetch-quality-scores.py |
| `english`, `visa_days`, `visa_info`, `tax_system`, `nomad_visa` | #1 fetch-quality-scores.py |
| `raw` (nested object with source values) | #1 fetch-quality-scores.py |
| `grade_percent`, `grade_label` | #2 recompute-grades.py |
| `budget_single`, `budget_couple`, `cost_index`, `us_comparison`, `affordable_cities` | #3 fetch-monthly-budget.py |
| `area_km2`, `population`, `capital`, `languages`, `currencies`, `demonym` | #4 fetch-country-facts.py |
| `driving_side`, `borders`, `timezones`, `landlocked`, `gini`, `memberships`, `government_type`, `continents` | #4 fetch-country-facts.py |
| `quick_facts_paragraph` | #5 generate-quick-facts.py |
| `compare_pairs` (top-level object, keyed by pair slug) | #7 generate-compare-content.py |

Fields not in this table (e.g. `grade` from old A/B/C system) are legacy and
can be ignored — they may exist in the JSON from older runs but are not read
by any page template.
