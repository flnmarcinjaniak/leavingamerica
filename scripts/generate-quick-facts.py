import json
import os
import time
import requests

DATA_PATH = "src/data/quality-scores.json"


def load_api_key():
    """Read ANTHROPIC_API_KEY from .env"""
    env_path = os.path.join(
        os.path.dirname(__file__), '..', '.env'
    )
    if not os.path.exists(env_path):
        raise FileNotFoundError(
            ".env file not found. Add "
            "ANTHROPIC_API_KEY=sk-ant-... to it."
        )
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('ANTHROPIC_API_KEY='):
                return line.split('=', 1)[1].strip()
    raise ValueError(
        "ANTHROPIC_API_KEY not found in .env"
    )


API_KEY = load_api_key()

NAMES = {
    'portugal':'Portugal','spain':'Spain','poland':'Poland',
    'mexico':'Mexico','thailand':'Thailand','germany':'Germany',
    'japan':'Japan','croatia':'Croatia',
    'czech-republic':'Czech Republic','hungary':'Hungary',
    'romania':'Romania','bulgaria':'Bulgaria','vietnam':'Vietnam',
    'south-korea':'South Korea','australia':'Australia',
    'new-zealand':'New Zealand','canada':'Canada','ireland':'Ireland',
    'netherlands':'Netherlands','france':'France',
    'argentina':'Argentina','ecuador':'Ecuador','morocco':'Morocco',
    'switzerland':'Switzerland','norway':'Norway','denmark':'Denmark',
    'sweden':'Sweden','belgium':'Belgium','austria':'Austria',
    'finland':'Finland','united-kingdom':'United Kingdom',
    'singapore':'Singapore','united-arab-emirates':'UAE',
    'qatar':'Qatar','saudi-arabia':'Saudi Arabia','iceland':'Iceland',
    'india':'India','philippines':'Philippines','china':'China',
    'georgia':'Georgia','serbia':'Serbia','kenya':'Kenya',
    'peru':'Peru','brazil':'Brazil','chile':'Chile',
    'albania':'Albania','sri-lanka':'Sri Lanka','egypt':'Egypt',
    'indonesia':'Indonesia','colombia':'Colombia',
    'costa-rica':'Costa Rica','panama':'Panama',
    'malaysia':'Malaysia','italy':'Italy','greece':'Greece'
}

SYSTEM_PROMPT = """You are an experienced
travel and relocation writer for a website
helping Americans considering a move abroad.
You write the way a human editor at a
publication like Conde Nast Traveler or
Bloomberg would — varied sentence structure,
genuine voice, never templated.

CRITICAL RULES:
1. Use ONLY the facts provided. Never invent
   additional facts, statistics, or claims
   not present in the input data.
2. NEVER use an em dash (—), and never use
   a hyphen or double hyphen as a sentence
   pause either (for example: "Portugal,
   despite its size -- has..." or "Portugal -
   despite its size - has..."). If you need
   a pause or aside, restructure the sentence
   or use a comma, a period, or the word "and"
   or "but" instead.
3. NEVER use these AI-cliche phrases or
   anything similar in spirit: "we believe",
   "unlock", "journey", "navigate",
   "seamlessly", "in today's world",
   "when it comes to", "boasts", "nestled",
   "rich history", "vibrant culture",
   "tapestry", "embark", "delve", "dive into",
   "in conclusion", "it's worth noting",
   "ultimately".
4. Vary your opening across different
   countries. Don't always start with
   population or always start the same way.
   Sometimes open with a contrast, sometimes
   with the capital, sometimes with a
   membership fact, sometimes with size.
5. Write 2-3 sentences, 50-80 words total.
   Conversational but informative tone, like
   a knowledgeable friend explaining what a
   country is actually like, not a brochure.
6. Do not address the reader directly with
   "you" more than once if at all. Write more
   like third-person reporting.
7. Only mention EU/NATO/Schengen/OECD/G7/G20
   membership if it's actually true for this
   country and relevant to context (e.g. ease
   of travel, institutional stability). Don't
   force it in if it doesn't fit naturally.
8. If the country is landlocked, or has many
   land borders, or drives on the left, you
   may mention it only if it adds genuine
   interest, not as a checklist.
"""


def build_user_prompt(country_name, data):
    facts = []
    if data.get('population'):
        facts.append(
            f"Population: {data['population']:,}"
        )
    if data.get('area_km2'):
        facts.append(
            f"Area: {data['area_km2']:,} km2"
        )
    if data.get('capital'):
        facts.append(f"Capital: {data['capital']}")
    if data.get('languages'):
        facts.append(
            f"Official/recognized languages: "
            f"{', '.join(data['languages'])}"
        )
    if data.get('currencies'):
        facts.append(
            f"Currency: {', '.join(data['currencies'])}"
        )
    if data.get('demonym'):
        facts.append(
            f"What residents are called: "
            f"{data['demonym']}"
        )
    if data.get('driving_side'):
        facts.append(
            f"Driving side: {data['driving_side']}"
        )
    if data.get('landlocked') is not None:
        facts.append(
            f"Landlocked: {data['landlocked']}"
        )
    if data.get('borders'):
        facts.append(
            f"Number of land borders: "
            f"{len(data['borders'])}"
        )

    memberships = data.get('memberships', {})
    active_memberships = [
        k.upper() for k, v in memberships.items()
        if v
    ]
    if active_memberships:
        facts.append(
            f"International memberships: "
            f"{', '.join(active_memberships)}"
        )

    if data.get('gini'):
        facts.append(
            f"Income inequality (Gini "
            f"coefficient, {data['gini']['year']}): "
            f"{data['gini']['value']}"
        )

    facts_text = '\n'.join(f"- {f}" for f in facts)

    return (
        f"Write a short editorial paragraph "
        f"about {country_name} for Americans "
        f"considering moving there. Use only "
        f"these facts:\n\n{facts_text}\n\n"
        f"Write only the paragraph, no preamble, "
        f"no title, no quotation marks around it."
    )


def generate_paragraph(country_name, data):
    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-sonnet-4-6",
            "max_tokens": 300,
            "system": SYSTEM_PROMPT,
            "messages": [
                {
                    "role": "user",
                    "content": build_user_prompt(
                        country_name, data
                    )
                }
            ]
        },
        timeout=30
    )
    response.raise_for_status()
    result = response.json()
    return result['content'][0]['text'].strip()


def main():
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        full_data = json.load(f)

    countries = full_data.get('countries', {})
    generated_count = 0
    failed = []

    print("--- Generating Quick Facts "
          "paragraphs via Claude API ---\n")

    for slug, data in countries.items():
        country_name = NAMES.get(slug, slug)
        try:
            paragraph = generate_paragraph(
                country_name, data
            )
            countries[slug][
                'quick_facts_paragraph'
            ] = paragraph
            generated_count += 1
            print(f"  {country_name}:")
            print(f"    {paragraph}\n")
            time.sleep(0.5)
        except Exception as e:
            print(f"  FAILED {country_name}: {e}")
            failed.append(country_name)
            continue

    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(
            full_data, f, indent=2,
            ensure_ascii=False
        )

    print(f"\nGenerated {generated_count}/"
          f"{len(countries)} paragraphs")
    if failed:
        print(f"Failed: {', '.join(failed)}")
    print(f"Saved to {DATA_PATH}")


if __name__ == "__main__":
    main()
