"""
Generate editorial articles for goal pages, countries hub, and country-match hub.

Usage:
  python scripts/generate-goal-content.py           # generate all missing
  python scripts/generate-goal-content.py --force   # regenerate all
  python scripts/generate-goal-content.py best-for-retirement   # one page

Outputs to src/data/goal-articles.json
Keys: best-for-retirement, remote-work-friendly, lowest-cost-of-living,
      safest-countries, english-friendly, countries-hub, country-match-hub
"""
import json, os, sys, requests

DATA_PATH     = "src/data/quality-scores.json"
ARTICLES_PATH = "src/data/goal-articles.json"

def load_api_key():
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('ANTHROPIC_API_KEY='):
                return line.split('=', 1)[1].strip()
    raise ValueError("ANTHROPIC_API_KEY not found in .env")

API_KEY = load_api_key()

NAMES = {
    'portugal':'Portugal','spain':'Spain','poland':'Poland','mexico':'Mexico',
    'thailand':'Thailand','germany':'Germany','japan':'Japan','croatia':'Croatia',
    'czech-republic':'Czech Republic','hungary':'Hungary','romania':'Romania',
    'bulgaria':'Bulgaria','vietnam':'Vietnam','south-korea':'South Korea',
    'australia':'Australia','new-zealand':'New Zealand','canada':'Canada',
    'ireland':'Ireland','netherlands':'Netherlands','france':'France',
    'argentina':'Argentina','ecuador':'Ecuador','morocco':'Morocco',
    'switzerland':'Switzerland','norway':'Norway','denmark':'Denmark',
    'sweden':'Sweden','belgium':'Belgium','austria':'Austria','finland':'Finland',
    'united-kingdom':'United Kingdom','singapore':'Singapore',
    'united-arab-emirates':'UAE','qatar':'Qatar','saudi-arabia':'Saudi Arabia',
    'iceland':'Iceland','india':'India','philippines':'Philippines','china':'China',
    'georgia':'Georgia','serbia':'Serbia','kenya':'Kenya','peru':'Peru',
    'brazil':'Brazil','chile':'Chile','albania':'Albania','sri-lanka':'Sri Lanka',
    'egypt':'Egypt','indonesia':'Indonesia','colombia':'Colombia',
    'costa-rica':'Costa Rica','panama':'Panama','malaysia':'Malaysia',
    'italy':'Italy','greece':'Greece','bahamas':'Bahamas','belize':'Belize',
    'bolivia':'Bolivia','cambodia':'Cambodia','cyprus':'Cyprus',
    'dominican-republic':'Dominican Republic','el-salvador':'El Salvador',
    'estonia':'Estonia','ghana':'Ghana','honduras':'Honduras','jamaica':'Jamaica',
    'kazakhstan':'Kazakhstan','latvia':'Latvia','lithuania':'Lithuania',
    'malta':'Malta','montenegro':'Montenegro','nepal':'Nepal',
    'nicaragua':'Nicaragua','north-macedonia':'North Macedonia','paraguay':'Paraguay',
    'rwanda':'Rwanda','slovakia':'Slovakia','slovenia':'Slovenia',
    'south-africa':'South Africa','taiwan':'Taiwan','turkey':'Turkey','uruguay':'Uruguay',
}

SYSTEM_PROMPT = """\
You are a personal finance and expat journalist writing for Americans who are seriously \
researching moving abroad. You write like a knowledgeable friend who has lived in \
multiple countries and knows the real trade-offs. Specific, honest, practical, direct. \
Think: a well-researched longform piece from someone who has actually done this.

AUDIENCE: Americans aged 30-55 who are past the daydreaming stage and want real \
comparisons backed by data.

STYLE RULES (non-negotiable):
- Write in plain, direct American English. Short sentences when they make a point better.
- Use specific country names, actual numbers, and real trade-offs. Never vague generalities.
- Vary sentence length and structure. Do not start consecutive sentences the same way.
- Do not start any sentence with "This".
- No em dashes anywhere. Use commas, periods, colons, or semicolons instead.
- No "Furthermore", "Moreover", "Additionally", "In conclusion", "To summarize".
- No "delve", "leverage", "crucial", "vital", "comprehensive", "robust", "seamless", \
"realm", "tapestry", "testament", "unlock", "foster", "holistic", "transformative", \
"empower", "synergy", "paramount", "nuanced", "navigate", "journey", "boasts", \
"vibrant", "nestled", "hidden gem", "don't miss".
- No "it is worth noting", "it is important to note", "needless to say".
- Do not use passive voice more than once per paragraph.
- Do not write like a listicle. Write paragraphs of connected thought.

SEO: Weave the target keyword phrase naturally into the first 100 words and once more \
in the final paragraph. Do not force it unnaturally.

OUTPUT FORMAT: Exactly 4 paragraphs separated by a blank line. No title, no headers, \
no bullet points, no preamble, no markdown. Just the 4 paragraphs.

LENGTH: 380-480 words total.
"""


def call_api(user_prompt):
    r = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-sonnet-4-6",
            "max_tokens": 900,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": user_prompt}],
        },
        timeout=60,
    )
    r.raise_for_status()
    return r.json()['content'][0]['text'].strip()


def fire_num(monthly):
    return round(monthly * 12 / 0.04 / 1000) * 1000


def top_countries(countries, score_fn, n=8, filter_fn=None):
    rows = []
    for slug, d in countries.items():
        if filter_fn and not filter_fn(d):
            continue
        score = score_fn(d)
        if score is None:
            continue
        rows.append((score, slug, d))
    rows.sort(key=lambda x: x[0], reverse=True)
    return [(slug, d) for _, slug, d in rows[:n]]


# ── Prompt builders ─────────────────────────────────────────────────

def prompt_retirement(countries):
    top = top_countries(
        countries,
        lambda d: (d.get('healthcare') or 0) * 0.4 + (d.get('safety') or 0) * 0.3 + (d.get('happiness') or 0) * 0.3,
        n=8,
    )
    lines = [
        "TARGET KEYWORD: best countries for Americans to retire abroad",
        "",
        "PAGE: /countries/goals/best-for-retirement",
        "RANKING METHOD: Healthcare (40%), Safety (30%), Happiness (30%)",
        "",
        "TOP 8 RANKED COUNTRIES:",
    ]
    for slug, d in top:
        budget = d.get('budget_single')
        fire = fire_num(budget) if budget else None
        lines.append(
            f"  {NAMES.get(slug, slug)}: healthcare {d.get('healthcare')}/10, "
            f"safety {d.get('safety')}/10, happiness {d.get('happiness')}/10"
            + (f", FIRE ~${fire:,}, ~${budget:,}/month" if fire else "")
        )
    lines += [
        "",
        "Write 4 editorial paragraphs for this page. Cover: what makes a country genuinely good "
        "for American retirement (not just cheap), the healthcare reality on the ground, trade-offs "
        "between Europe vs. Asia vs. Latin America options, and what actually drives long-term "
        "satisfaction for retired Americans. Reference specific top-ranked countries with their "
        "actual data. No affiliate mention needed.",
    ]
    return '\n'.join(lines)


def prompt_remote_work(countries):
    top = top_countries(
        countries,
        lambda d: d.get('internet') or 0,
        n=8,
        filter_fn=lambda d: d.get('nomad_visa') is True,
    )
    lines = [
        "TARGET KEYWORD: best countries for remote work for Americans",
        "",
        "PAGE: /countries/goals/remote-work-friendly",
        "RANKING METHOD: Internet speed (only countries with digital nomad visa)",
        "",
        "TOP 8 RANKED COUNTRIES (all have official digital nomad visas):",
    ]
    for slug, d in top:
        budget = d.get('budget_single')
        fire = fire_num(budget) if budget else None
        lines.append(
            f"  {NAMES.get(slug, slug)}: internet {d.get('internet')}/10, "
            f"nomad visa: yes, cost index {d.get('cost_index') or 'n/a'}"
            + (f", ~${budget:,}/month" if budget else "")
        )
    lines += [
        "",
        "Write 4 editorial paragraphs for this page. Cover: why a digital nomad visa matters "
        "practically (not just legally), internet reliability reality vs. speed test scores, "
        "the cost-vs-connectivity trade-off, and what separates countries that work well for "
        "American remote workers vs. those that just sound good on paper. Mention specific "
        "top-ranked countries with real numbers. The reader is deciding where to spend 1-2 years "
        "working remotely and wants honest trade-offs, not a list of pros.",
    ]
    return '\n'.join(lines)


def prompt_cost(countries):
    top = top_countries(
        countries,
        lambda d: -(d.get('cost_index') or 999),
        n=8,
        filter_fn=lambda d: d.get('cost_index') is not None,
    )
    lines = [
        "TARGET KEYWORD: cheapest countries for Americans to live abroad",
        "",
        "PAGE: /countries/goals/lowest-cost-of-living",
        "RANKING METHOD: Cost Index (lower = cheaper; US baseline = 82)",
        "",
        "TOP 8 CHEAPEST COUNTRIES:",
    ]
    for slug, d in top:
        budget = d.get('budget_single')
        fire = fire_num(budget) if budget else None
        lines.append(
            f"  {NAMES.get(slug, slug)}: cost index {d.get('cost_index')}"
            + (f", ~${budget:,}/month single person" if budget else "")
            + (f", FIRE ~${fire:,}" if fire else "")
        )
    lines += [
        "",
        "Write 4 editorial paragraphs for this page. Cover: what low cost actually means for "
        "American standard of living (some cheap countries are cheap because of trade-offs), "
        "the regional clusters and what they offer, why FIRE number matters more than raw "
        "cost index (monthly * 300), and what questions Americans should ask before picking "
        "a cheap country. Be honest about what you give up and what you gain. Reference "
        "specific countries with their actual numbers.",
    ]
    return '\n'.join(lines)


def prompt_safety(countries):
    top = top_countries(
        countries,
        lambda d: d.get('safety') or 0,
        n=8,
        filter_fn=lambda d: d.get('safety') is not None,
    )
    lines = [
        "TARGET KEYWORD: safest countries for Americans living abroad",
        "",
        "PAGE: /countries/goals/safest-countries",
        "RANKING METHOD: Numbeo Safety Index (10 = safest)",
        "",
        "TOP 8 SAFEST COUNTRIES:",
    ]
    for slug, d in top:
        budget = d.get('budget_single')
        lines.append(
            f"  {NAMES.get(slug, slug)}: safety {d.get('safety')}/10"
            + (f", ~${budget:,}/month" if budget else "")
            + (f", cost index {d['cost_index']}" if d.get('cost_index') else "")
        )
    lines += [
        "",
        "Write 4 editorial paragraphs for this page. Cover: what 'safe' actually means for "
        "American expats day-to-day (petty crime vs. violent crime, neighborhood variation, "
        "traffic vs. street crime), the correlation between safety scores and cost, whether "
        "the safest countries are also the most affordable, and what experienced expats "
        "actually pay attention to when evaluating safety. Be honest and specific. Reference "
        "top-ranked countries with their actual safety scores.",
    ]
    return '\n'.join(lines)


def prompt_english(countries):
    top = top_countries(
        countries,
        lambda d: d.get('english') or 0,
        n=8,
        filter_fn=lambda d: d.get('english') is not None and d.get('english') < 999,
    )
    # Add native English countries separately
    native = [slug for slug, d in countries.items() if d.get('english') == 999]
    lines = [
        "TARGET KEYWORD: English-speaking countries to move to from the US",
        "",
        "PAGE: /countries/goals/english-friendly",
        "RANKING METHOD: EF English Proficiency Index (higher = better English, max ~700; native speakers = 999)",
        "",
        "NATIVE ENGLISH COUNTRIES in dataset: " + ', '.join(NAMES.get(s, s) for s in native),
        "",
        "TOP 8 BY EF EPI (non-native, ranked by proficiency):",
    ]
    for slug, d in top:
        budget = d.get('budget_single')
        lines.append(
            f"  {NAMES.get(slug, slug)}: EF EPI {int(d.get('english'))}"
            + (f", ~${budget:,}/month" if budget else "")
        )
    lines += [
        "",
        "Write 4 editorial paragraphs for this page. Cover: why English proficiency varies so "
        "much from EF EPI score to real daily life (professional vs. street English, age gap, "
        "tourist areas vs. residential neighborhoods), the genuine advantages of English-friendly "
        "countries for American expats beyond communication, what native English countries offer "
        "vs. high-proficiency non-native ones (cost, lifestyle, FIRE number differences), and "
        "what Americans consistently get wrong about English abroad. Be specific and honest.",
    ]
    return '\n'.join(lines)


def prompt_countries_hub(countries):
    # Build a summary of key stats
    total = len(countries)
    cheapest = sorted(
        [(NAMES.get(s, s), d['cost_index']) for s, d in countries.items() if d.get('cost_index')],
        key=lambda x: x[1]
    )[:3]
    most_fire_friendly = sorted(
        [(NAMES.get(s, s), fire_num(d['budget_single'])) for s, d in countries.items() if d.get('budget_single')],
        key=lambda x: x[1]
    )[:3]
    lines = [
        "TARGET KEYWORD: countries for Americans moving abroad",
        "",
        "PAGE: /countries (main hub listing all 82 countries)",
        f"DATASET: {total} countries with economic, safety, healthcare, visa, and tax data",
        "",
        "SOME KEY DATA POINTS TO USE:",
        f"  3 cheapest by cost index: {', '.join(n + ' (' + str(ci) + ')' for n, ci in cheapest)}",
        f"  3 lowest FIRE numbers: {', '.join(n + ' (~$' + f'{f:,}' + ')' for n, f in most_fire_friendly)}",
        "  US cost index baseline: 82",
        "  US FIRE baseline (~$3,500/month): ~$1,050,000",
        "",
        "Write 4 editorial paragraphs introducing this comparison page. Cover: why Americans "
        "are increasingly comparing countries rather than just picking one by gut feeling, what "
        "data actually matters when comparing countries (and what doesn't), how cost index, "
        "FIRE number, healthcare score, and visa access work together as a picture, and what "
        "the data shows at a macro level (range of options, surprising conclusions). "
        "Use specific numbers from the dataset. Write for someone who just landed on this page "
        "and wants to understand how to use it, not a general expat pep talk.",
    ]
    return '\n'.join(lines)


def prompt_country_match_hub():
    lines = [
        "TARGET KEYWORD: which country should I move to from the US",
        "",
        "PAGE: /country-match (landing page for a 10-question quiz matching Americans to countries)",
        "QUIZ COVERS: finances (income/savings), lifestyle (climate, language, pace), "
        "priorities (healthcare, safety, English, nomad visa, cost), and timeline.",
        "",
        "Write 4 editorial paragraphs introducing this quiz page. Cover: why picking a country "
        "based on what sounds good is how most people get it wrong, what the quiz actually "
        "measures (not just 'do you like warm weather' but financial fit and practical friction), "
        "the trade-offs the quiz surfaces that people don't usually think about before moving, "
        "and what a good country match actually means for long-term satisfaction vs. a short "
        "vacation experience. Write for someone who is genuinely considering leaving and feels "
        "slightly overwhelmed by the options. Direct, useful, specific.",
    ]
    return '\n'.join(lines)


# ── Main ─────────────────────────────────────────────────────────────

TASKS = {
    'best-for-retirement':   prompt_retirement,
    'remote-work-friendly':  prompt_remote_work,
    'lowest-cost-of-living': prompt_cost,
    'safest-countries':      prompt_safety,
    'english-friendly':      prompt_english,
    'countries-hub':         prompt_countries_hub,
    'country-match-hub':     lambda _: prompt_country_match_hub(),
}


def main():
    args = sys.argv[1:]
    force  = "--force" in args
    target = next((a for a in args if a != "--force"), None)

    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    countries = data['countries']

    if os.path.exists(ARTICLES_PATH):
        with open(ARTICLES_PATH, 'r', encoding='utf-8') as f:
            articles = json.load(f)
    else:
        articles = {}

    keys = [target] if target else list(TASKS.keys())
    for key in keys:
        if key not in TASKS:
            print(f"ERROR: unknown key '{key}'"); sys.exit(1)

    generated = skipped = 0
    failed = []

    print("--- Generating goal/hub articles via Claude API ---\n")

    for key in keys:
        if not force and key in articles and len(articles[key]) > 200:
            print(f"  SKIP {key} (already generated)")
            skipped += 1
            continue

        print(f"  Generating: {key}...")
        try:
            prompt_fn = TASKS[key]
            user_prompt = prompt_fn(countries)
            text = call_api(user_prompt)
            paras = [p.strip() for p in text.split('\n\n') if p.strip()]
            articles[key] = '\n\n'.join(paras)

            with open(ARTICLES_PATH, 'w', encoding='utf-8') as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)

            print(f"    OK ({len(articles[key])} chars, {len(paras)} paragraphs)")
            generated += 1

        except Exception as e:
            print(f"    FAILED: {e}")
            failed.append(key)

    print(f"\nDone. Generated: {generated}, Skipped: {skipped}, Failed: {len(failed)}")
    if failed:
        print("Failed:", failed)


if __name__ == '__main__':
    main()
