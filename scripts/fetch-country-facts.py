import json
import os
import time
import requests

DATA_PATH = "src/data/quality-scores.json"


def load_api_key():
    """Read RESTCOUNTRIES_API_KEY from .env
    without adding a new dependency like
    python-dotenv"""
    env_path = os.path.join(
        os.path.dirname(__file__), '..', '.env'
    )
    if not os.path.exists(env_path):
        raise FileNotFoundError(
            ".env file not found at project root"
        )
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('RESTCOUNTRIES_API_KEY='):
                return line.split('=', 1)[1].strip()
    raise ValueError(
        "RESTCOUNTRIES_API_KEY not found in .env"
    )


API_KEY = load_api_key()

HEADERS = {
    "Authorization": f"Bearer {API_KEY}"
}

COUNTRY_ISO2 = {
    "PT": "portugal", "ES": "spain", "MX": "mexico",
    "DE": "germany", "IT": "italy", "GR": "greece",
    "CR": "costa-rica", "PA": "panama",
    "TH": "thailand", "MY": "malaysia",
    "ID": "indonesia", "CO": "colombia",
    "HR": "croatia", "CZ": "czech-republic",
    "PL": "poland", "HU": "hungary",
    "RO": "romania", "BG": "bulgaria",
    "VN": "vietnam", "JP": "japan",
    "KR": "south-korea", "AU": "australia",
    "NZ": "new-zealand", "CA": "canada",
    "IE": "ireland", "NL": "netherlands",
    "FR": "france", "AR": "argentina",
    "EC": "ecuador", "MA": "morocco",
    "CH": "switzerland", "NO": "norway",
    "DK": "denmark", "SE": "sweden",
    "BE": "belgium", "AT": "austria",
    "FI": "finland", "GB": "united-kingdom",
    "SG": "singapore", "AE": "united-arab-emirates",
    "QA": "qatar", "SA": "saudi-arabia",
    "IS": "iceland", "IN": "india",
    "PH": "philippines", "CN": "china",
    "GE": "georgia", "RS": "serbia",
    "KE": "kenya", "PE": "peru",
    "BR": "brazil", "CL": "chile",
    "AL": "albania", "LK": "sri-lanka",
    "EG": "egypt",
    "BS": "bahamas", "BZ": "belize", "BO": "bolivia",
    "KH": "cambodia", "CY": "cyprus", "DO": "dominican-republic",
    "SV": "el-salvador", "EE": "estonia", "GH": "ghana",
    "HN": "honduras", "JM": "jamaica", "KZ": "kazakhstan",
    "LV": "latvia", "LT": "lithuania", "MT": "malta",
    "ME": "montenegro", "NP": "nepal", "NI": "nicaragua",
    "MK": "north-macedonia", "PY": "paraguay", "RW": "rwanda",
    "SK": "slovakia", "SI": "slovenia", "ZA": "south-africa",
    "TW": "taiwan", "TR": "turkey", "UY": "uruguay",
}


def fetch_country_facts(iso2_code):
    """Fetch area, population, and
    contextual facts for one country from
    REST Countries v5 using its ISO 3166-1
    alpha-2 code"""
    response = requests.get(
        "https://api.restcountries.com/countries/v5",
        params={
            "codes.alpha_2": iso2_code,
            "limit": 1
        },
        headers=HEADERS,
        timeout=15
    )
    response.raise_for_status()
    data = response.json()

    objects = data.get('data', {}).get('objects', [])
    if not objects:
        return None

    country = objects[0]
    area = country.get('area', {})
    returned_name = country.get(
        'names', {}
    ).get('common', '')

    capitals = country.get('capitals', [])
    capital_name = (
        capitals[0].get('name')
        if capitals else None
    )

    currencies = country.get('currencies', [])
    currency_names = [
        c.get('name') for c in currencies
        if c.get('name')
    ]

    languages = country.get('languages', [])
    language_names = [
        l.get('name') for l in languages
        if l.get('name')
    ]

    memberships = country.get('memberships', {})

    demonyms = country.get('demonyms', {})
    demonym_eng = (
        demonyms.get('eng', {}).get('m')
        if demonyms.get('eng') else None
    )

    cars = country.get('cars', {})
    driving_side = cars.get('driving_side')

    borders = country.get('borders', [])

    timezones = country.get('timezones', [])

    landlocked = country.get('landlocked')

    gini = country.get('economy', {}).get(
        'gini_coefficient', {}
    )
    gini_latest = None
    if gini:
        latest_year = max(gini.keys())
        gini_latest = {
            'year': latest_year,
            'value': gini[latest_year]
        }

    continents = country.get('continents', [])

    return {
        'returned_name': returned_name,
        'area_km2': area.get('kilometers'),
        'population': country.get('population'),
        'government_type': country.get(
            'government_type'
        ),
        'capital': capital_name,
        'currencies': currency_names,
        'languages': language_names,
        'demonym': demonym_eng,
        'driving_side': driving_side,
        'borders': borders,
        'timezones': timezones,
        'landlocked': landlocked,
        'gini': gini_latest,
        'continents': continents,
        'memberships': {
            'nato': memberships.get('nato'),
            'eu': memberships.get('eu'),
            'eurozone': memberships.get(
                'eurozone'
            ),
            'schengen': memberships.get(
                'schengen'
            ),
            'oecd': memberships.get('oecd'),
            'g7': memberships.get('g7'),
            'g20': memberships.get('g20'),
            'commonwealth': memberships.get(
                'commonwealth'
            ),
        },
    }


def fetch_all_facts():
    print("--- Country Facts "
          "(REST Countries v5) ---\n")
    results = {}
    failed = []

    for iso2, slug in COUNTRY_ISO2.items():
        try:
            facts = fetch_country_facts(iso2)
            if facts:
                results[slug] = facts
                pop = facts['population']
                pop_str = (
                    f"{pop:,}" if pop else "N/A"
                )
                eu = (
                    "EU" if facts['memberships'].get(
                        'eu'
                    ) else ""
                )
                nato = (
                    "NATO" if facts['memberships'].get(
                        'nato'
                    ) else ""
                )
                tags = ' '.join(
                    filter(None, [eu, nato])
                )
                print(
                    f"  {iso2} -> "
                    f"{facts['returned_name']}: "
                    f"pop={pop_str}, "
                    f"capital={facts['capital']}, "
                    f"lang={facts['languages']}, "
                    f"{tags}"
                )
            else:
                print(f"  {iso2}: no data found")
                failed.append(iso2)
            time.sleep(0.3)
        except Exception as e:
            print(f"  WARNING: {iso2} failed: {e}")
            failed.append(iso2)
            continue

    print(f"\nFetched {len(results)}/"
          f"{len(COUNTRY_ISO2)} countries")
    if failed:
        print(f"Failed: {', '.join(failed)}")

    return results


def merge_into_json(facts_data):
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    countries_data = data.get('countries', {})
    updated_count = 0

    fields_to_copy = [
        'area_km2', 'population',
        'government_type', 'capital',
        'currencies', 'languages', 'demonym',
        'driving_side', 'borders', 'timezones',
        'landlocked', 'gini', 'memberships',
        'continents'
    ]

    for slug, facts in facts_data.items():
        if slug not in countries_data:
            continue
        for field in fields_to_copy:
            countries_data[slug][field] = (
                facts.get(field)
            )
        updated_count += 1

    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nMerged country facts into "
          f"{updated_count}/{len(COUNTRY_ISO2)} "
          f"countries in {DATA_PATH}")


if __name__ == "__main__":
    facts_data = fetch_all_facts()
    if facts_data:
        merge_into_json(facts_data)
    else:
        print("\nNo data fetched — "
              "nothing to merge.")
