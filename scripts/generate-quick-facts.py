"""
Generate multi-paragraph "What [Country] is actually like" sections
for all 82 country pages via Claude API.

Usage:
  python scripts/generate-quick-facts.py           # skip countries already extended
  python scripts/generate-quick-facts.py --force   # regenerate all
  python scripts/generate-quick-facts.py portugal  # regenerate one country by slug
"""
import json
import os
import sys
import time
import requests

DATA_PATH = "src/data/quality-scores.json"


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


API_KEY = load_api_key()

NAMES = {
    'portugal':'Portugal','spain':'Spain','poland':'Poland',
    'mexico':'Mexico','thailand':'Thailand','germany':'Germany',
    'japan':'Japan','croatia':'Croatia','czech-republic':'Czech Republic',
    'hungary':'Hungary','romania':'Romania','bulgaria':'Bulgaria',
    'vietnam':'Vietnam','south-korea':'South Korea','australia':'Australia',
    'new-zealand':'New Zealand','canada':'Canada','ireland':'Ireland',
    'netherlands':'Netherlands','france':'France','argentina':'Argentina',
    'ecuador':'Ecuador','morocco':'Morocco','switzerland':'Switzerland',
    'norway':'Norway','denmark':'Denmark','sweden':'Sweden',
    'belgium':'Belgium','austria':'Austria','finland':'Finland',
    'united-kingdom':'United Kingdom','singapore':'Singapore',
    'united-arab-emirates':'UAE','qatar':'Qatar',
    'saudi-arabia':'Saudi Arabia','iceland':'Iceland','india':'India',
    'philippines':'Philippines','china':'China','georgia':'Georgia',
    'serbia':'Serbia','kenya':'Kenya','peru':'Peru','brazil':'Brazil',
    'chile':'Chile','albania':'Albania','sri-lanka':'Sri Lanka',
    'egypt':'Egypt','indonesia':'Indonesia','colombia':'Colombia',
    'costa-rica':'Costa Rica','panama':'Panama','malaysia':'Malaysia',
    'italy':'Italy','greece':'Greece','bahamas':'Bahamas','belize':'Belize',
    'bolivia':'Bolivia','cambodia':'Cambodia','cyprus':'Cyprus',
    'dominican-republic':'Dominican Republic','el-salvador':'El Salvador',
    'estonia':'Estonia','ghana':'Ghana','honduras':'Honduras',
    'jamaica':'Jamaica','kazakhstan':'Kazakhstan','latvia':'Latvia',
    'lithuania':'Lithuania','malta':'Malta','montenegro':'Montenegro',
    'nepal':'Nepal','nicaragua':'Nicaragua',
    'north-macedonia':'North Macedonia','paraguay':'Paraguay',
    'rwanda':'Rwanda','slovakia':'Slovakia','slovenia':'Slovenia',
    'south-africa':'South Africa','taiwan':'Taiwan','turkey':'Turkey',
    'uruguay':'Uruguay',
}

SYSTEM_PROMPT = """You are a veteran expat journalist who has lived in 30+ countries \
and writes an insider column for Americans who are seriously evaluating relocation \
abroad. Your job is to write the "What [Country] is actually like" section \
for a country profile page.

AUDIENCE: Americans who have done their research, seen the data, and want to know \
what daily life actually feels like — not a tourism pitch, not Wikipedia.

VOICE: Write like a trusted friend who spent 6 months there and knows the real deal. \
Specific. Occasionally opinionated. Honest about trade-offs. Never enthusiastic for \
its own sake. The tone sits between a good long-form travel essay and practical \
relocation advice.

STRUCTURE: Write exactly 4 paragraphs separated by a blank line. No headers. \
No bullet points. No numbered lists. Prose only.

Paragraph 1 - HOOK: Open with something specific, counterintuitive, or surprising \
about this country that most Americans don't know. Not a brochure opener. \
Not a geography fact unless it's genuinely the most interesting thing. \
Make the reader feel they just learned something real.

Paragraph 2 - PRACTICAL REALITY: What costs actually look like (use the budget data \
provided), how healthcare access works in practice, what bureaucracy is like for \
foreign residents. This is the paragraph people bookmark. Include concrete numbers.

Paragraph 3 - THE AMERICAN PERSPECTIVE: What Americans particularly notice when \
they move here. What surprises them (good and bad). What takes adjustment. \
Language realities. Cultural friction points. What makes them stay.

Paragraph 4 - FIRST STEPS: Practical things to do in the first weeks. One and only \
one natural mention of a product or service that solves a real problem Americans \
face here. Choose the single most relevant option:
  - "Wise" if the biggest friction is moving money, paying bills, or the local \
    banking setup is slow or complex for foreigners. Mention naturally, like a \
    recommendation from a friend: "Most Americans open a Wise account before \
    they leave - it works at local ATMs while you wait for a bank account."
  - "NordVPN" if streaming access loss or US banking app geo-blocking is the \
    most common practical complaint. Mention as a tool people quietly rely on.
  - "SafetyWing" if healthcare quality is 7 or below, or the country is in \
    SE Asia, Africa, or Latin America where US health insurance typically does \
    not apply. Position as the standard starter option: "SafetyWing is what most \
    American nomads use here for the first year - around $45/month while you \
    sort out local options."
  - "Airalo" if SIM card access is the most immediate friction point on arrival \
    (especially SE Asia, countries with complicated prepaid SIM rules). \
    Position as the solution for the first days: "Pick up an Airalo eSIM \
    before boarding - it activates on the plane and skips the airport SIM hunt."
Do NOT mention more than one product. Do NOT use promotional language. \
Write the mention the way you would text it to a friend.

LENGTH: 500-700 words total across the 4 paragraphs.

SEO - naturally include (do not force): "Americans moving to [Country]", \
"living in [Country]", "[Country] expat", and at least one practical \
number (rent estimate, meal cost, budget figure).

STRICTLY FORBIDDEN - these phrases trigger rejection:
"rich history", "vibrant culture", "nestled", "boasts", "tapestry", \
"seamlessly", "embark", "delve", "dive into", "it's worth noting", \
"in conclusion", "ultimately", "overall", "additionally", \
"when it comes to", "unlock", "journey", "navigate", "don't miss", \
"hidden gem". Never use em dashes. Never start a sentence with "This".

DATA RULE: You may use your general knowledge for cultural context and \
qualitative descriptions. For any numerical claims (costs, scores, rankings, \
percentages), use only the data provided in the input - never invent statistics.

OUTPUT FORMAT: Output only the 4 paragraphs of prose. No preamble. No title. \
No quotation marks. No markdown. Paragraphs separated by a single blank line."""


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


def build_user_prompt(country_name, slug, data):
    lines = [f"COUNTRY: {country_name}\n"]

    geo = []
    if data.get('capital'):
        geo.append(f"Capital: {data['capital']}")
    if data.get('population'):
        geo.append(f"Population: {data['population']:,}")
    if data.get('area_km2'):
        geo.append(f"Area: {data['area_km2']:,} km2")
    if data.get('languages'):
        geo.append(f"Language(s): {', '.join(data['languages'])}")
    if data.get('currencies'):
        geo.append(f"Currency: {', '.join(data['currencies'])}")
    if data.get('landlocked') is not None:
        geo.append(f"Landlocked: {'Yes' if data['landlocked'] else 'No'}")
    if data.get('borders'):
        geo.append(f"Land borders: {len(data['borders'])}")
    if data.get('driving_side'):
        geo.append(f"Driving: {data['driving_side']} side of road")

    memberships = data.get('memberships', {})
    active = [k.upper() for k, v in memberships.items() if v]
    if active:
        geo.append(f"International memberships: {', '.join(active)}")

    if data.get('gini'):
        g = data['gini']
        inequality = (
            'low' if g['value'] < 32
            else 'moderate' if g['value'] < 40
            else 'high'
        )
        geo.append(
            f"Income inequality (Gini {g['year']}): {g['value']} ({inequality} inequality)"
        )
    lines.append("GEOGRAPHY & BASICS:\n" + "\n".join(f"  {g}" for g in geo))

    scores = []
    score_fields = [
        ('safety',       'Safety / crime rate'),
        ('healthcare',   'Healthcare quality'),
        ('happiness',    'Happiness / wellbeing'),
        ('hdi',          'Human Development Index'),
        ('pollution',    'Air & environmental quality'),
        ('unemployment', 'Employment stability'),
        ('internet',     'Internet speed & coverage'),
        ('traffic',      'Traffic safety'),
    ]
    for field, label in score_fields:
        if data.get(field) is not None:
            scores.append(f"{label}: {score_label(data[field])}")

    if data.get('english'):
        proficiency = (
            "Very High" if data['english'] > 600
            else "High" if data['english'] > 500
            else "Moderate" if data['english'] > 400
            else "Low"
        )
        scores.append(
            f"English proficiency: {proficiency} (EF EPI score {int(data['english'])})"
        )
    if scores:
        lines.append("\nQUALITY SCORES:\n" + "\n".join(f"  {s}" for s in scores))

    practical = []
    if data.get('budget_single'):
        practical.append(
            f"Estimated monthly budget (single person): ~${data['budget_single']:,}/month"
        )
    if data.get('budget_couple'):
        practical.append(
            f"Estimated monthly budget (couple): ~${data['budget_couple']:,}/month"
        )
    if data.get('us_comparison'):
        practical.append(f"Cost vs the US: {data['us_comparison']}")
    if data.get('affordable_cities'):
        cities = ", ".join(
            f"{c['name']} (~${c['monthly_usd']:,}/mo)"
            for c in data['affordable_cities'][:3]
        )
        practical.append(f"Most affordable cities: {cities}")
    if data.get('visa_days'):
        practical.append(f"US passport visa-free entry: {data['visa_days']} days")
    if data.get('nomad_visa'):
        practical.append("Digital Nomad Visa: Available")
    if data.get('tax_system'):
        practical.append(f"Tax system for residents: {data['tax_system']}")
    if practical:
        lines.append("\nPRACTICAL & COST DATA:\n" + "\n".join(f"  {p}" for p in practical))

    lines.append(
        f"\nWrite the 4-paragraph section for {country_name}. "
        f"Follow the system prompt exactly. "
        f"Output only the 4 paragraphs, separated by blank lines."
    )

    return "\n".join(lines)


def is_extended(text):
    return bool(text and "\n\n" in text.strip())


def generate_section(country_name, slug, data):
    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-sonnet-4-6",
            "max_tokens": 1200,
            "system": SYSTEM_PROMPT,
            "messages": [
                {
                    "role": "user",
                    "content": build_user_prompt(country_name, slug, data)
                }
            ]
        },
        timeout=60
    )
    response.raise_for_status()
    result = response.json()
    return result['content'][0]['text'].strip()


def main():
    args = sys.argv[1:]
    force = "--force" in args
    target_slug = next((a for a in args if a != "--force"), None)

    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        full_data = json.load(f)

    countries = full_data.get('countries', {})

    if target_slug:
        if target_slug not in countries:
            print(f"ERROR: slug '{target_slug}' not found in data.")
            sys.exit(1)
        slugs_to_process = [target_slug]
    else:
        slugs_to_process = list(countries.keys())

    generated = 0
    skipped = 0
    failed = []

    print("--- Generating extended Quick Facts sections via Claude API ---")
    print(f"Mode: {'force regenerate all' if force else 'skip already extended'}")
    print(f"Countries to check: {len(slugs_to_process)}\n")

    for slug in slugs_to_process:
        data = countries[slug]
        country_name = NAMES.get(slug, slug)
        existing = data.get('quick_facts_paragraph', '')

        if not force and is_extended(existing):
            print(f"  SKIP {country_name} (already extended)")
            skipped += 1
            continue

        print(f"  Generating: {country_name}...")
        try:
            text = generate_section(country_name, slug, data)
            paras = [p.strip() for p in text.split('\n\n') if p.strip()]
            if len(paras) < 2:
                print(
                    f"    WARNING: only {len(paras)} paragraph(s) returned "
                    f"- regenerate with --force if needed"
                )
            countries[slug]['quick_facts_paragraph'] = "\n\n".join(paras)
            generated += 1
            word_count = len(text.split())
            print(f"    OK ({len(paras)} paragraphs, {word_count} words)")
            time.sleep(0.8)
        except Exception as e:
            print(f"    FAILED: {e}")
            failed.append(country_name)
            continue

    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(full_data, f, indent=2, ensure_ascii=False)

    print(f"\nDone: {generated} generated, {skipped} skipped, {len(failed)} failed")
    if failed:
        print(f"Failed: {', '.join(failed)}")
    print(f"Saved to {DATA_PATH}")


if __name__ == "__main__":
    main()
