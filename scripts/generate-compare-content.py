"""
Generate 450-550 word comparative editorial content for all 55 compare pairs.

Usage:
  python scripts/generate-compare-content.py                      # skip already generated
  python scripts/generate-compare-content.py --force              # regenerate all
  python scripts/generate-compare-content.py portugal-vs-spain    # one pair
  python scripts/generate-compare-content.py portugal-vs-spain spain-vs-italy  # multiple
"""

import json
import os
import sys
import time
import requests

DATA_PATH = "src/data/quality-scores.json"

PAIRS = [
    'portugal-vs-spain', 'spain-vs-italy', 'portugal-vs-italy',
    'greece-vs-spain', 'greece-vs-portugal', 'malta-vs-cyprus',
    'croatia-vs-greece', 'croatia-vs-portugal',
    'mexico-vs-costa-rica', 'mexico-vs-panama', 'costa-rica-vs-panama',
    'mexico-vs-portugal', 'colombia-vs-mexico', 'ecuador-vs-colombia',
    'argentina-vs-chile', 'argentina-vs-uruguay', 'belize-vs-costa-rica',
    'nicaragua-vs-costa-rica', 'dominican-republic-vs-mexico',
    'thailand-vs-vietnam', 'thailand-vs-malaysia', 'vietnam-vs-philippines',
    'thailand-vs-philippines', 'malaysia-vs-indonesia', 'thailand-vs-portugal',
    'cambodia-vs-thailand', 'cambodia-vs-vietnam',
    'poland-vs-czech-republic', 'hungary-vs-poland', 'romania-vs-bulgaria',
    'czech-republic-vs-hungary', 'croatia-vs-slovenia', 'estonia-vs-lithuania',
    'latvia-vs-lithuania', 'albania-vs-montenegro', 'georgia-vs-turkey',
    'france-vs-spain', 'france-vs-italy', 'netherlands-vs-germany',
    'ireland-vs-united-kingdom', 'canada-vs-australia', 'australia-vs-new-zealand',
    'portugal-vs-costa-rica', 'spain-vs-mexico', 'panama-vs-portugal',
    'thailand-vs-mexico',
    'georgia-vs-portugal', 'taiwan-vs-south-korea', 'japan-vs-south-korea',
    'singapore-vs-malaysia', 'united-arab-emirates-vs-singapore',
    'south-africa-vs-portugal', 'morocco-vs-spain', 'kenya-vs-south-africa',
    'turkey-vs-greece',
]

NAMES = {
    'portugal': 'Portugal', 'spain': 'Spain', 'poland': 'Poland',
    'mexico': 'Mexico', 'thailand': 'Thailand', 'germany': 'Germany',
    'japan': 'Japan', 'croatia': 'Croatia', 'czech-republic': 'Czech Republic',
    'hungary': 'Hungary', 'romania': 'Romania', 'bulgaria': 'Bulgaria',
    'vietnam': 'Vietnam', 'south-korea': 'South Korea', 'australia': 'Australia',
    'new-zealand': 'New Zealand', 'canada': 'Canada', 'ireland': 'Ireland',
    'netherlands': 'Netherlands', 'france': 'France', 'argentina': 'Argentina',
    'ecuador': 'Ecuador', 'morocco': 'Morocco', 'switzerland': 'Switzerland',
    'norway': 'Norway', 'denmark': 'Denmark', 'sweden': 'Sweden',
    'belgium': 'Belgium', 'austria': 'Austria', 'finland': 'Finland',
    'united-kingdom': 'United Kingdom', 'singapore': 'Singapore',
    'united-arab-emirates': 'UAE', 'qatar': 'Qatar',
    'saudi-arabia': 'Saudi Arabia', 'iceland': 'Iceland', 'india': 'India',
    'philippines': 'Philippines', 'china': 'China', 'georgia': 'Georgia',
    'serbia': 'Serbia', 'kenya': 'Kenya', 'peru': 'Peru', 'brazil': 'Brazil',
    'chile': 'Chile', 'albania': 'Albania', 'sri-lanka': 'Sri Lanka',
    'egypt': 'Egypt', 'indonesia': 'Indonesia', 'colombia': 'Colombia',
    'costa-rica': 'Costa Rica', 'panama': 'Panama', 'malaysia': 'Malaysia',
    'italy': 'Italy', 'greece': 'Greece', 'bahamas': 'Bahamas',
    'belize': 'Belize', 'bolivia': 'Bolivia', 'cambodia': 'Cambodia',
    'cyprus': 'Cyprus', 'dominican-republic': 'Dominican Republic',
    'el-salvador': 'El Salvador', 'estonia': 'Estonia', 'ghana': 'Ghana',
    'honduras': 'Honduras', 'jamaica': 'Jamaica', 'kazakhstan': 'Kazakhstan',
    'latvia': 'Latvia', 'lithuania': 'Lithuania', 'malta': 'Malta',
    'montenegro': 'Montenegro', 'nepal': 'Nepal', 'nicaragua': 'Nicaragua',
    'north-macedonia': 'North Macedonia', 'paraguay': 'Paraguay',
    'rwanda': 'Rwanda', 'slovakia': 'Slovakia', 'slovenia': 'Slovenia',
    'south-africa': 'South Africa', 'taiwan': 'Taiwan', 'turkey': 'Turkey',
    'uruguay': 'Uruguay',
}

# Pre-assigned opening axes for all 55 pairs — rotated across 6 categories
# to prevent any single axis dominating more than ~20% of pieces.
# Axes: cost | safety | tax | visa_bureaucracy | lifestyle_pace | climate
OPENING_AXES = {
    'portugal-vs-spain':                  'tax',
    'spain-vs-italy':                     'lifestyle_pace',
    'portugal-vs-italy':                  'visa_bureaucracy',
    'greece-vs-spain':                    'cost',
    'greece-vs-portugal':                 'climate',
    'malta-vs-cyprus':                    'tax',
    'croatia-vs-greece':                  'cost',
    'croatia-vs-portugal':                'lifestyle_pace',
    'mexico-vs-costa-rica':               'safety',
    'mexico-vs-panama':                   'tax',
    'costa-rica-vs-panama':               'cost',
    'mexico-vs-portugal':                 'visa_bureaucracy',
    'colombia-vs-mexico':                 'safety',
    'ecuador-vs-colombia':                'cost',
    'argentina-vs-chile':                 'safety',
    'argentina-vs-uruguay':               'tax',
    'belize-vs-costa-rica':               'lifestyle_pace',
    'nicaragua-vs-costa-rica':            'cost',
    'dominican-republic-vs-mexico':       'visa_bureaucracy',
    'thailand-vs-vietnam':                'cost',
    'thailand-vs-malaysia':               'tax',
    'vietnam-vs-philippines':             'cost',
    'thailand-vs-philippines':            'safety',
    'malaysia-vs-indonesia':              'tax',
    'thailand-vs-portugal':               'climate',
    'cambodia-vs-thailand':               'safety',
    'cambodia-vs-vietnam':                'cost',
    'poland-vs-czech-republic':           'cost',
    'hungary-vs-poland':                  'tax',
    'romania-vs-bulgaria':                'cost',
    'czech-republic-vs-hungary':          'lifestyle_pace',
    'croatia-vs-slovenia':                'cost',
    'estonia-vs-lithuania':               'tax',
    'latvia-vs-lithuania':                'lifestyle_pace',
    'albania-vs-montenegro':              'cost',
    'georgia-vs-turkey':                  'safety',
    'france-vs-spain':                    'cost',
    'france-vs-italy':                    'visa_bureaucracy',
    'netherlands-vs-germany':             'lifestyle_pace',
    'ireland-vs-united-kingdom':          'tax',
    'canada-vs-australia':                'visa_bureaucracy',
    'australia-vs-new-zealand':           'cost',
    'portugal-vs-costa-rica':             'visa_bureaucracy',
    'spain-vs-mexico':                    'climate',
    'panama-vs-portugal':                 'tax',
    'thailand-vs-mexico':                 'climate',
    'georgia-vs-portugal':                'cost',
    'taiwan-vs-south-korea':              'lifestyle_pace',
    'japan-vs-south-korea':               'cost',
    'singapore-vs-malaysia':              'cost',
    'united-arab-emirates-vs-singapore':  'tax',
    'south-africa-vs-portugal':           'safety',
    'morocco-vs-spain':                   'cost',
    'kenya-vs-south-africa':              'safety',
    'turkey-vs-greece':                   'cost',
}

AXIS_INSTRUCTIONS = {
    'cost': (
        "Lead with the monthly budget gap between these two countries as the very "
        "first concrete fact. Name both budget figures in the opening paragraph. "
        "Explain immediately why that gap matters more or less than it looks on paper."
    ),
    'safety': (
        "Lead with the safety contrast. Be direct if one country scores significantly "
        "safer than the other. Use the provided safety scores. Explain what the gap "
        "means in practice for daily life, not just as an abstract number."
    ),
    'tax': (
        "Lead with how the local tax treatment differs between these two countries for "
        "a US expat (both still require US federal filing, but local obligations may "
        "differ: territorial vs worldwide vs zero). If both are worldwide, find the "
        "specific nuance within that similarity rather than pretending no contrast exists."
    ),
    'visa_bureaucracy': (
        "Lead with how getting legal residency in each country actually differs in "
        "practice: digital nomad visa availability, visa-free days, and what the "
        "bureaucratic path looks like in each. Make the comparison concrete."
    ),
    'lifestyle_pace': (
        "Lead with a concrete, data-grounded observation about how daily life rhythm "
        "or cultural fit differs between these two destinations, and which type of "
        "American tends to self-select into each."
    ),
    'climate': (
        "Lead with how the physical environment and climate differ between these two "
        "destinations, and what that means practically for someone choosing between "
        "them as a place to live full-time, not visit."
    ),
}

SYSTEM_PROMPT = """\
You are a data-driven relocation journalist writing head-to-head comparison pieces \
for Americans choosing between two specific destinations. Your job is to help a \
reader reach a decision, not to describe two places.

CRITICAL STRUCTURAL RULE:
Every paragraph must actively compare both countries against each other. \
Banned pattern: a paragraph describing Country A, followed by a separate paragraph \
describing Country B, with no sentence that references both. \
Required: every paragraph contains at least one explicit comparative construction \
("more than", "less than", "unlike [Country]", "where [A] does X, [B] does Y", \
"the real gap between them", "both share X but diverge on Y", "cheaper than", \
"safer than", "harder than"). \
If any sentence could appear unchanged in a single-country profile for either place, \
that sentence fails the rule and must be rewritten to force a comparison.

STRUCTURE — four paragraphs, no headers, prose only:

Paragraph 1 — SHARPEST CONTRAST: Open with the single most decisive point of \
difference between these two countries, using the axis specified in the input. \
Ground it in data immediately. Not a vague observation that could apply to \
many country pairs.

Paragraph 2 — COST AND PRACTICAL REALITY: Compare what daily life actually costs \
in each, using both budget figures. Compare healthcare in practice. State the dollar \
gap plainly. Be concrete about which is cheaper and by how much. If affordable cities \
data is available for both, name and compare specific cities.

Paragraph 3 — TAX, VISA, AND RESIDENCY: Compare local tax treatment for US expats, \
visa-free entry days, digital nomad visa availability, and what getting legal residency \
actually involves in each. If both countries are identical on an axis, say so honestly \
and find the genuine difference within the similarity. Do not manufacture a contrast \
that does not exist in the data.

Paragraph 4 — TWO READER PROFILES: End by explicitly naming two types of Americans, \
one who should choose each country, with reasons tied to the specific data. Not vague \
personality types. Specific profiles: budget level, tax situation, remote work status, \
risk tolerance, or priorities. End with a clear statement of who each country wins for. \
No hedged "both are great" finish.

VOICE: Direct, data-grounded comparative journalism. Write for someone who has \
already read both country profiles and is now choosing between them. Honest when \
one clearly outperforms the other on a metric. Not promotional for either.

LENGTH: 450-550 words total across the 4 paragraphs.

STRICTLY FORBIDDEN:
- Em dashes (—)
- "rich history", "vibrant culture", "vibrant", "nestled", "boasts", "tapestry", \
  "seamlessly", "embark", "delve", "dive into", "it's worth noting", "in conclusion", \
  "ultimately", "overall", "when it comes to", "unlock", "journey", "navigate", \
  "in today's world", "a world of", "a unique blend"
- Starting any sentence with "This"
- Addressing the reader as "you" more than twice across the entire piece
- Any sentence that could appear unchanged on a single-country profile page

DATA RULE: Use only numerical figures provided in the input for statistics, \
costs, scores, and rankings. Use general knowledge only for qualitative cultural \
context. Never invent or round a number to something not in the data.

OUTPUT: Four paragraphs separated by single blank lines. No title, no headers, \
no bullet points, no preamble, no quotation marks around the output.\
"""


def load_api_key():
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    if not os.path.exists(env_path):
        raise FileNotFoundError(".env not found. Add ANTHROPIC_API_KEY=sk-ant-... to it.")
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('ANTHROPIC_API_KEY='):
                return line.split('=', 1)[1].strip()
    raise ValueError("ANTHROPIC_API_KEY not found in .env")


def score_label(val):
    if val is None:
        return "N/A"
    if val >= 9:
        return f"{val}/10 (Excellent)"
    if val >= 7:
        return f"{val}/10 (Good)"
    if val >= 5:
        return f"{val}/10 (Moderate)"
    return f"{val}/10 (Below average)"


def build_country_block(name, data):
    lines = [f"{name.upper()}:"]
    if data.get('budget_single'):
        lines.append(f"  Monthly budget (single): ~${data['budget_single']:,}/month")
    if data.get('budget_couple'):
        lines.append(f"  Monthly budget (couple): ~${data['budget_couple']:,}/month")
    if data.get('us_comparison'):
        lines.append(f"  Cost vs US: {data['us_comparison']}")
    if data.get('cost_index'):
        lines.append(f"  Cost index (US=100): {data['cost_index']}")
    if data.get('safety') is not None:
        lines.append(f"  Safety: {score_label(data['safety'])}")
    if data.get('healthcare') is not None:
        lines.append(f"  Healthcare: {score_label(data['healthcare'])}")
    if data.get('internet') is not None:
        lines.append(f"  Internet: {score_label(data['internet'])}")
    if data.get('happiness') is not None:
        lines.append(f"  Happiness: {score_label(data['happiness'])}")
    if data.get('english'):
        if data['english'] >= 999:
            lines.append("  English: Native English country")
        else:
            lvl = ("Very High" if data['english'] > 600 else
                   "High" if data['english'] > 500 else
                   "Moderate" if data['english'] > 400 else "Low")
            lines.append(f"  English proficiency: {lvl} (EF EPI {int(data['english'])})")
    if data.get('grade_percent') is not None:
        lines.append(f"  Overall grade: {data['grade_percent']}/100 ({data.get('grade_label', '')})")
    if data.get('tax_system'):
        lines.append(f"  Tax system (local): {data['tax_system']}")
    lines.append(f"  Digital Nomad Visa: {'Yes' if data.get('nomad_visa') else 'No'}")
    if data.get('visa_days'):
        lines.append(f"  US passport visa-free: {data['visa_days']} days")
    if data.get('capital'):
        lines.append(f"  Capital: {data['capital']}")
    if data.get('languages'):
        lines.append(f"  Language(s): {', '.join(data['languages'])}")
    if data.get('affordable_cities'):
        cities = ", ".join(
            f"{c['name']} (~${c['monthly_usd']:,}/mo)"
            for c in data['affordable_cities'][:3]
        )
        lines.append(f"  Affordable cities: {cities}")
    return "\n".join(lines)


def build_user_prompt(pair, name_a, data_a, name_b, data_b):
    axis = OPENING_AXES.get(pair, 'cost')
    lines = [
        f"COMPARISON: {name_a} vs {name_b}",
        f"PAIR SLUG: {pair}",
        "",
        "OPENING AXIS INSTRUCTION:",
        AXIS_INSTRUCTIONS[axis],
        "",
        "COUNTRY DATA:",
        "",
        build_country_block(name_a, data_a),
        "",
        build_country_block(name_b, data_b),
        "",
        "KEY CONTRASTS (derive from data above):",
    ]

    if data_a.get('budget_single') and data_b.get('budget_single'):
        gap = abs(data_a['budget_single'] - data_b['budget_single'])
        cheaper = name_a if data_a['budget_single'] < data_b['budget_single'] else name_b
        lines.append(f"  Monthly budget gap: ${gap:,}/month ({cheaper} is cheaper)")

    if data_a.get('safety') is not None and data_b.get('safety') is not None:
        gap = abs(data_a['safety'] - data_b['safety'])
        if gap > 0:
            safer = name_a if data_a['safety'] > data_b['safety'] else name_b
            lines.append(f"  Safety gap: {gap}/10 points ({safer} scores higher)")

    tax_a = data_a.get('tax_system', 'unknown')
    tax_b = data_b.get('tax_system', 'unknown')
    if tax_a != tax_b:
        lines.append(f"  Tax systems differ: {name_a} is {tax_a}, {name_b} is {tax_b}")
    else:
        lines.append(f"  Tax systems identical: both {tax_a}")

    nv_a = data_a.get('nomad_visa')
    nv_b = data_b.get('nomad_visa')
    if nv_a != nv_b:
        has_it = name_a if nv_a else name_b
        lines.append(f"  Nomad visa asymmetry: only {has_it} offers one")
    else:
        lines.append(f"  Nomad visa: both {'offer' if nv_a else 'lack'} one")

    lines.append(
        f"\nWrite a 450-550 word comparative piece for {name_a} vs {name_b}. "
        "Follow the system prompt exactly. Four paragraphs, prose only, "
        "no title, no headers."
    )
    return "\n".join(lines)


def generate_comparison(api_key, pair, name_a, data_a, name_b, data_b):
    prompt = build_user_prompt(pair, name_a, data_a, name_b, data_b)
    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-sonnet-4-6",
            "max_tokens": 1200,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.json()['content'][0]['text'].strip()


def detect_opening_axis(text):
    first = text.split('\n\n')[0].lower()
    if any(w in first for w in ['safe', 'crime', 'security', 'risk', 'dangerous', 'peace']):
        return 'safety'
    if any(w in first for w in ['tax', 'territorial', 'worldwide', 'income tax', 'foreign income']):
        return 'tax'
    if any(w in first for w in ['visa', 'residency', 'bureaucra', 'permit', 'passport', 'nomad visa']):
        return 'visa_bureaucracy'
    if any(w in first for w in ['climate', 'weather', 'tropical', 'temperature', 'monsoon', 'season']):
        return 'climate'
    if any(w in first for w in ['pace', 'rhythm', 'culture', 'lifestyle', 'crowd', 'attitude', 'slower']):
        return 'lifestyle_pace'
    return 'cost'


def check_opening_repetition(recent_axes, new_axis):
    return len(recent_axes) >= 2 and all(a == new_axis for a in recent_axes[-2:])


def main():
    args = sys.argv[1:]
    force = "--force" in args
    targets = [a for a in args if a != "--force"]

    api_key = load_api_key()

    with open(DATA_PATH, 'r', encoding='utf-8-sig') as f:
        full_data = json.load(f)

    countries = full_data.get('countries', {})
    if 'compare_pairs' not in full_data:
        full_data['compare_pairs'] = {}
    compare_pairs = full_data['compare_pairs']

    if targets:
        for t in targets:
            if t not in PAIRS:
                print(f"ERROR: '{t}' is not in the canonical PAIRS list.")
                sys.exit(1)
        pairs_to_process = targets
    else:
        pairs_to_process = PAIRS

    generated = 0
    skipped = 0
    failed = []
    recent_axes = []

    print("--- Generating compare-pair editorial content via Claude API ---")
    print(f"Mode: {'force regenerate' if force else 'skip already generated'}")
    print(f"Pairs to check: {len(pairs_to_process)}\n")

    for pair in pairs_to_process:
        vi = pair.index('-vs-')
        slug_a, slug_b = pair[:vi], pair[vi + 4:]
        name_a = NAMES.get(slug_a, slug_a)
        name_b = NAMES.get(slug_b, slug_b)

        if slug_a not in countries or slug_b not in countries:
            print(f"  SKIP {pair} (slug not found in countries data)")
            skipped += 1
            continue

        existing = compare_pairs.get(pair, '')
        if not force and existing and '\n\n' in existing.strip():
            print(f"  SKIP {pair} (already generated)")
            skipped += 1
            continue

        print(f"  Generating: {name_a} vs {name_b}  [axis: {OPENING_AXES.get(pair, 'cost')}]")
        try:
            text = generate_comparison(
                api_key, pair,
                name_a, countries[slug_a],
                name_b, countries[slug_b],
            )
            paras = [p.strip() for p in text.split('\n\n') if p.strip()]
            if len(paras) < 3:
                print(f"    WARNING: only {len(paras)} paragraph(s) returned — check output")

            word_count = len(text.split())
            detected_axis = detect_opening_axis(text)
            suffix = ""
            if check_opening_repetition(recent_axes, detected_axis):
                suffix = f"  <-- WARNING: 3rd consecutive '{detected_axis}' opener"
            recent_axes.append(detected_axis)
            if len(recent_axes) > 10:
                recent_axes.pop(0)

            compare_pairs[pair] = "\n\n".join(paras)
            generated += 1
            print(f"    OK  {len(paras)} paragraphs, {word_count} words, detected axis: {detected_axis}{suffix}")
            time.sleep(0.8)

        except Exception as e:
            print(f"    FAILED: {e}")
            failed.append(pair)
            continue

    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(full_data, f, indent=2, ensure_ascii=False)

    print(f"\nDone: {generated} generated, {skipped} skipped, {len(failed)} failed")
    if failed:
        print(f"Failed: {', '.join(failed)}")
    print(f"Saved to {DATA_PATH}")


if __name__ == "__main__":
    main()
