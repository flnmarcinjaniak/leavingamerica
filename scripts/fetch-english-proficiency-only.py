import json
import requests
import time
import re
from bs4 import BeautifulSoup

DATA_PATH = "src/data/quality-scores.json"

HEADERS = {
    'User-Agent': 'LeavingAmericaBot/1.0 '
    '(https://leavingamerica.co; '
    'contact@leavingamerica.co) Python-requests',
    'Accept': 'text/html,application/xhtml+xml,'
    'application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip',
}

# Canonical name → slug (same as COUNTRIES in fetch-quality-scores.py)
COUNTRIES = {
    "Portugal": "portugal", "Spain": "spain", "Mexico": "mexico",
    "Germany": "germany", "Italy": "italy", "Greece": "greece",
    "Costa Rica": "costa-rica", "Panama": "panama", "Thailand": "thailand",
    "Malaysia": "malaysia", "Indonesia": "indonesia", "Colombia": "colombia",
    "Croatia": "croatia", "Czech Republic": "czech-republic", "Poland": "poland",
    "Hungary": "hungary", "Romania": "romania", "Bulgaria": "bulgaria",
    "Vietnam": "vietnam", "Japan": "japan", "South Korea": "south-korea",
    "Australia": "australia", "New Zealand": "new-zealand", "Canada": "canada",
    "Ireland": "ireland", "Netherlands": "netherlands", "France": "france",
    "Argentina": "argentina", "Ecuador": "ecuador", "Morocco": "morocco",
    "Switzerland": "switzerland", "Norway": "norway", "Denmark": "denmark",
    "Sweden": "sweden", "Belgium": "belgium", "Austria": "austria",
    "Finland": "finland", "United Kingdom": "united-kingdom",
    "Singapore": "singapore", "United Arab Emirates": "united-arab-emirates",
    "Qatar": "qatar", "Saudi Arabia": "saudi-arabia", "Iceland": "iceland",
    "India": "india", "Philippines": "philippines", "China": "china",
    "Georgia": "georgia", "Serbia": "serbia", "Kenya": "kenya",
    "Peru": "peru", "Brazil": "brazil", "Chile": "chile",
    "Albania": "albania", "Sri Lanka": "sri-lanka", "Egypt": "egypt",
    "Bahamas": "bahamas", "Belize": "belize", "Bolivia": "bolivia",
    "Cambodia": "cambodia", "Cyprus": "cyprus",
    "Dominican Republic": "dominican-republic",
    "El Salvador": "el-salvador", "Estonia": "estonia",
    "Ghana": "ghana", "Honduras": "honduras", "Jamaica": "jamaica",
    "Kazakhstan": "kazakhstan", "Latvia": "latvia",
    "Lithuania": "lithuania", "Malta": "malta",
    "Montenegro": "montenegro", "Nepal": "nepal",
    "Nicaragua": "nicaragua", "North Macedonia": "north-macedonia",
    "Paraguay": "paraguay", "Rwanda": "rwanda",
    "Slovakia": "slovakia", "Slovenia": "slovenia",
    "South Africa": "south-africa", "Taiwan": "taiwan",
    "Turkey": "turkey", "Uruguay": "uruguay",
}

# Same as COUNTRY_ALIASES in fetch-quality-scores.py
COUNTRY_ALIASES = {
    "Albania": ["Albania"],
    "Argentina": ["Argentina"],
    "Australia": ["Australia"],
    "Austria": ["Austria"],
    "Belgium": ["Belgium"],
    "Brazil": ["Brazil"],
    "Bulgaria": ["Bulgaria"],
    "Chile": ["Chile"],
    "China": ["China", "People's Republic of China"],
    "Colombia": ["Colombia"],
    "Costa Rica": ["Costa Rica"],
    "Croatia": ["Croatia"],
    "Czech Republic": ["Czech Republic", "Czechia"],
    "Denmark": ["Denmark"],
    "Ecuador": ["Ecuador"],
    "Egypt": ["Egypt", "Egypt, Arab Rep."],
    "Finland": ["Finland"],
    "France": ["France"],
    "Georgia": ["Georgia"],
    "Germany": ["Germany"],
    "Greece": ["Greece"],
    "Hungary": ["Hungary"],
    "Iceland": ["Iceland"],
    "India": ["India"],
    "Indonesia": ["Indonesia"],
    "Ireland": ["Ireland"],
    "Italy": ["Italy"],
    "Japan": ["Japan"],
    "Kenya": ["Kenya"],
    "Malaysia": ["Malaysia"],
    "Mexico": ["Mexico"],
    "Morocco": ["Morocco"],
    "Netherlands": ["Netherlands"],
    "New Zealand": ["New Zealand"],
    "Norway": ["Norway"],
    "Panama": ["Panama"],
    "Peru": ["Peru"],
    "Philippines": ["Philippines"],
    "Poland": ["Poland"],
    "Portugal": ["Portugal"],
    "Qatar": ["Qatar"],
    "Romania": ["Romania"],
    "Saudi Arabia": ["Saudi Arabia"],
    "Serbia": ["Serbia"],
    "Singapore": ["Singapore"],
    "South Korea": ["South Korea", "Korea, Republic of", "Korea, Rep."],
    "Spain": ["Spain"],
    "Sri Lanka": ["Sri Lanka"],
    "Sweden": ["Sweden"],
    "Switzerland": ["Switzerland"],
    "Thailand": ["Thailand"],
    "United Arab Emirates": ["United Arab Emirates", "UAE"],
    "United Kingdom": ["United Kingdom", "UK"],
    "Vietnam": ["Vietnam", "Viet Nam"],
    "Bahamas": ["Bahamas", "The Bahamas"],
    "Belize": ["Belize"],
    "Bolivia": ["Bolivia"],
    "Cambodia": ["Cambodia"],
    "Cyprus": ["Cyprus"],
    "Dominican Republic": ["Dominican Republic"],
    "El Salvador": ["El Salvador"],
    "Estonia": ["Estonia"],
    "Ghana": ["Ghana"],
    "Honduras": ["Honduras"],
    "Jamaica": ["Jamaica"],
    "Kazakhstan": ["Kazakhstan"],
    "Latvia": ["Latvia"],
    "Lithuania": ["Lithuania"],
    "Malta": ["Malta"],
    "Montenegro": ["Montenegro"],
    "Nepal": ["Nepal"],
    "Nicaragua": ["Nicaragua"],
    "North Macedonia": ["North Macedonia", "Macedonia"],
    "Paraguay": ["Paraguay"],
    "Rwanda": ["Rwanda"],
    "Slovakia": ["Slovakia"],
    "Slovenia": ["Slovenia"],
    "South Africa": ["South Africa"],
    "Taiwan": ["Taiwan"],
    "Turkey": ["Turkey", "Türkiye"],
    "Uruguay": ["Uruguay"],
}

# Countries where English is native — assigned sentinel score 999
NATIVE_ENGLISH = {
    'Australia', 'New Zealand', 'Canada',
    'Ireland', 'Singapore', 'United Kingdom',
    'United States', 'Jamaica', 'Bahamas',
}

# Manual overrides for countries not in the EF EPI table
ENGLISH_OVERRIDES = {
    'Iceland': 630.0,
}


def match_country(country_name, source_name):
    """Identical to match_country() in fetch-quality-scores.py"""
    aliases = COUNTRY_ALIASES.get(country_name, [country_name])
    source_lower = source_name.lower().strip()
    for alias in aliases:
        if alias.lower() == source_lower:
            return True
        if alias.lower() in source_lower:
            return True
        if source_lower in alias.lower():
            return True
    return False


def fetch_url_with_retry(url, max_retries=3, **kwargs):
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            last_error = e
            if (e.response is not None and
                    e.response.status_code == 403 and
                    attempt < max_retries):
                wait_time = 30 * attempt
                print(f"  Got 403, attempt {attempt}/{max_retries}. "
                      f"Waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            raise
    raise last_error


def fetch_english_proficiency():
    """Fetch EF English Proficiency Index from Wikipedia and return
    {slug: score} with NATIVE_ENGLISH and ENGLISH_OVERRIDES applied.

    Parsing logic is identical to fetch_english_proficiency() in
    fetch-quality-scores.py. Slug mapping and overrides (which live
    in the main loop there) are folded in here so merge_into_json()
    receives a slug-keyed dict it can apply directly."""
    url = "https://en.wikipedia.org/wiki/EF_English_Proficiency_Index"
    print(f"Fetching: {url}")
    response = fetch_url_with_retry(url, timeout=30, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')

    # --- Step 1: parse raw Wikipedia table → {wikipedia_name: ef_score} ---
    raw = {}
    tables = soup.find_all('table', class_='wikitable')
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) < 3:
                continue
            try:
                country = None
                score = None
                for i, cell in enumerate(cells):
                    text = cell.get_text(strip=True)
                    try:
                        val = float(text.replace(',', '.'))
                        if 200 <= val <= 700:
                            score = val
                            if i > 0:
                                country = cells[i - 1].get_text(strip=True)
                            break
                    except ValueError:
                        continue
                if country and score:
                    country = re.sub(r'\[.*?\]', '', country).strip()
                    if 2 < len(country) < 50:
                        raw[country] = score
            except Exception:
                continue

    print(f"  Parsed {len(raw)} countries from Wikipedia table")

    # --- Step 2: map to slugs via COUNTRIES + match_country ---
    results = {}
    for country_name, slug in COUNTRIES.items():
        # Native English — sentinel value
        if country_name in NATIVE_ENGLISH:
            results[slug] = 999
            print(f"  {country_name} ({slug}): native English → 999")
            continue

        matched_score = None
        for source_country, en_score in raw.items():
            if match_country(country_name, source_country):
                matched_score = round(en_score, 1)
                print(f"  {country_name} ({slug}): {matched_score}")
                break

        # Manual override when not found in table
        if matched_score is None and country_name in ENGLISH_OVERRIDES:
            matched_score = ENGLISH_OVERRIDES[country_name]
            print(f"  {country_name} ({slug}): override → {matched_score}")

        if matched_score is not None:
            results[slug] = matched_score
        else:
            print(f"  NOT FOUND: {country_name} ({slug})")

    return results


def merge_into_json(english_data):
    with open(DATA_PATH, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)
    countries_data = data.get('countries', {})
    updated = 0
    for slug, score in english_data.items():
        if slug in countries_data:
            countries_data[slug]['english'] = score
            if 'raw' in countries_data[slug]:
                countries_data[slug]['raw']['english'] = score
            updated += 1
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\nMerged English proficiency into {updated} countries in {DATA_PATH}")


if __name__ == "__main__":
    print("--- English Proficiency only "
          "(standalone, run after fresh IP) ---")
    results = fetch_english_proficiency()
    if results:
        merge_into_json(results)
    else:
        print("No data fetched.")
