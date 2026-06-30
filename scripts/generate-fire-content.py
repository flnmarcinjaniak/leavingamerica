"""
Generate "Retiring in [Country]" articles for /fire/[slug] pages via Claude API.

Usage:
  python scripts/generate-fire-content.py           # skip already generated
  python scripts/generate-fire-content.py --force   # regenerate all
  python scripts/generate-fire-content.py portugal  # one country
"""
import json, os, sys, time, requests

DATA_PATH = "src/data/quality-scores.json"

def load_api_key():
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    if not os.path.exists(env_path):
        raise FileNotFoundError(".env not found.")
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

SE_ASIA = {
    'thailand','vietnam','cambodia','indonesia','philippines',
    'malaysia','sri-lanka','india','nepal','singapore'
}
LATAM = {
    'mexico','colombia','peru','ecuador','argentina','chile',
    'brazil','bolivia','uruguay','paraguay','costa-rica','panama',
    'belize','jamaica','dominican-republic','el-salvador',
    'honduras','nicaragua'
}
AFRICA = {'kenya','ghana','rwanda','south-africa','egypt','morocco'}
RETIREMENT_HAVENS = {'costa-rica','panama','portugal','mexico'}

def affiliate_hint(slug, healthcare):
    if slug in SE_ASIA or (slug in AFRICA and healthcare <= 6):
        return 'Airalo (for the first days) and SafetyWing (for ongoing health coverage at around $45/month while you sort out local insurance options)'
    if slug in LATAM and healthcare <= 7:
        return 'SafetyWing — US health insurance is void here, and SafetyWing gives you solid nomad coverage for around $45/month'
    return 'Wise — set it up before you leave, it works at ATMs and handles currency conversion without the fees your US bank charges'

SYSTEM_PROMPT = """You are a personal finance and expat journalist writing for Americans \
who are seriously researching early retirement abroad. You write like a knowledgeable \
friend who has lived in these places and knows the real numbers — specific, honest, \
practical. Think: Mr. Money Mustache meets a long-form travel essay.

AUDIENCE: Americans aged 30-55 who know what FIRE is, have done basic research, \
and want to know what their FIRE number actually buys them in this country.

STRUCTURE: Exactly 5 paragraphs separated by blank lines. No headers. No bullet lists.

P1 — WHAT YOUR FIRE NUMBER BUYS: Translate the monthly budget into real daily life. \
What does $X/month look like in practice? What can you afford that you couldn't in the US? \
Be specific — mention a neighborhood, a meal, a weekly rhythm. Reference the actual FIRE \
number and monthly budget from the data.

P2 — THE COST BREAKDOWN: Where does the money actually go. Housing range, \
food costs, healthcare access costs, transport. Use the city data provided. \
One concrete US comparison to make the scale click.

P3 — HEALTHCARE AND PRACTICAL FRICTION: What Americans need to know about \
healthcare access, language barrier, banking setup, bureaucracy for residency. \
Honest about what's easy and what takes patience. Use the healthcare score if it \
is notably high or low.

P4 — WHO MAKES THIS WORK (AND WHO DOESN'T): What kind of American actually \
thrives here in early retirement. What lifestyle assumptions hold up and which ones \
don't. What makes people stay long-term. What makes them leave.

P5 — FIRST STEPS: Practical things to do before and immediately after arriving. \
Include ONE natural mention of the recommended product (provided in input) — \
write it as advice from a friend, not an advertisement. Also mention the visa \
situation briefly (visa_days / nomad visa).

LENGTH: 550-700 words total.

SEO PHRASES (include naturally, do not force):
"retire in [country]", "early retirement [country]", \
"Americans retiring in [country]", "FIRE number [country]", \
"how much to retire in [country]"

STRICTLY FORBIDDEN: "rich history", "vibrant culture", "nestled", "boasts", \
"tapestry", "seamlessly", "embark", "delve", "in conclusion", "it's worth noting", \
"overall", "ultimately", "don't miss", "hidden gem". No em dashes. \
Never start a sentence with "This".

DATA RULE: Use the provided data for all numbers. Do not invent cost figures.

OUTPUT: 5 paragraphs separated by blank lines. No preamble, no title, \
no markdown, no quotation marks."""


def fire_number(monthly):
    return round(monthly * 12 / 0.04 / 1000) * 1000


def build_prompt(country_name, slug, data):
    monthly = data['budget_single']
    fire = fire_number(monthly)
    us_fire = 1_050_000
    savings = us_fire - fire
    aff = affiliate_hint(slug, data.get('healthcare', 7))

    lines = [
        f"COUNTRY: {country_name}",
        f"FIRE Number (4% rule): ${fire:,}",
        f"Monthly budget (single person): ~${monthly:,}/month",
        f"US baseline for comparison: ${us_fire:,} (~$3,500/month median US city)",
    ]
    if savings > 0:
        lines.append(f"Savings vs US baseline: ${savings:,} less capital needed")
    if data.get('us_comparison'):
        lines.append(f"Cost comparison: {data['us_comparison']}")
    if data.get('affordable_cities'):
        cities = ', '.join(
            f"{c['name']} (~${c['monthly_usd']:,}/mo)"
            for c in data['affordable_cities'][:3]
        )
        lines.append(f"Affordable cities: {cities}")

    for field, label in [
        ('healthcare','Healthcare quality'),
        ('safety','Safety'),
        ('happiness','Happiness / wellbeing'),
        ('hdi','Human Development'),
        ('internet','Internet'),
    ]:
        if data.get(field):
            lines.append(f"{label}: {data[field]}/10")

    if data.get('english'):
        lines.append(f"English proficiency: EF EPI {int(data['english'])}")
    if data.get('visa_days'):
        lines.append(f"US passport visa-free: {data['visa_days']} days")
    if data.get('nomad_visa'):
        lines.append("Digital Nomad Visa: Available")
    if data.get('tax_system'):
        lines.append(f"Tax system: {data['tax_system']}")
    if data.get('grade_label'):
        lines.append(f"QoL rating: {data['grade_label']}")

    memberships = data.get('memberships', {})
    active = [k.upper() for k, v in memberships.items() if v]
    if active:
        lines.append(f"Memberships: {', '.join(active)}")

    lines.append(f"\nRECOMMENDED AFFILIATE: {aff}")
    lines.append(
        f"\nWrite the 5-paragraph article for /fire/{slug} about retiring in "
        f"{country_name}. Follow the system prompt exactly. "
        f"Output only the paragraphs, separated by blank lines."
    )
    return '\n'.join(lines)


def generate(country_name, slug, data):
    r = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-sonnet-4-6",
            "max_tokens": 1100,
            "system": SYSTEM_PROMPT,
            "messages": [{"role":"user","content": build_prompt(country_name, slug, data)}]
        },
        timeout=60
    )
    r.raise_for_status()
    return r.json()['content'][0]['text'].strip()


def main():
    args = sys.argv[1:]
    force = "--force" in args
    target = next((a for a in args if a != "--force"), None)

    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        full = json.load(f)
    countries = full['countries']

    slugs = [target] if target else list(countries.keys())
    if target and target not in countries:
        print(f"ERROR: '{target}' not found"); sys.exit(1)

    generated = skipped = 0
    failed = []

    print("--- Generating FIRE articles via Claude API ---")
    print(f"Mode: {'force' if force else 'skip existing'}\n")

    for slug in slugs:
        data = countries[slug]
        name = NAMES.get(slug, slug)

        if not data.get('budget_single'):
            print(f"  SKIP {name} (no budget_single data)")
            skipped += 1
            continue

        existing = data.get('fire_article', '')
        if not force and existing and '\n\n' in existing:
            print(f"  SKIP {name} (already generated)")
            skipped += 1
            continue

        print(f"  Generating: {name}...")
        try:
            text = generate(name, slug, data)
            paras = [p.strip() for p in text.split('\n\n') if p.strip()]
            countries[slug]['fire_article'] = '\n\n'.join(paras)
            generated += 1
            print(f"    OK ({len(paras)} paragraphs, {len(text.split())} words)")
            time.sleep(0.8)
        except Exception as e:
            print(f"    FAILED: {e}")
            failed.append(name)

    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(full, f, indent=2, ensure_ascii=False)

    print(f"\nDone: {generated} generated, {skipped} skipped, {len(failed)} failed")
    if failed:
        print(f"Failed: {', '.join(failed)}")

if __name__ == "__main__":
    main()
