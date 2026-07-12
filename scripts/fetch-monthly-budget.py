import json
import time
import requests

DATA_PATH = "src/data/quality-scores.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; "
    "LeavingAmericaBot/1.0; "
    "+https://leavingamerica.co)"
}

# Same slug -> ISO2 mapping used in
# fetch-quality-scores.py (WORLD_BANK_CODES)
COUNTRY_CODES = {
    "portugal": "PT", "spain": "ES",
    "mexico": "MX", "germany": "DE",
    "italy": "IT", "greece": "GR",
    "costa-rica": "CR", "panama": "PA",
    "thailand": "TH", "malaysia": "MY",
    "indonesia": "ID", "colombia": "CO",
    "croatia": "HR", "czech-republic": "CZ",
    "poland": "PL", "hungary": "HU",
    "romania": "RO", "bulgaria": "BG",
    "vietnam": "VN", "japan": "JP",
    "south-korea": "KR", "australia": "AU",
    "new-zealand": "NZ", "canada": "CA",
    "ireland": "IE", "netherlands": "NL",
    "france": "FR", "argentina": "AR",
    "ecuador": "EC", "morocco": "MA",
    "switzerland": "CH", "norway": "NO",
    "denmark": "DK", "sweden": "SE",
    "belgium": "BE", "austria": "AT",
    "finland": "FI", "united-kingdom": "GB",
    "singapore": "SG",
    "united-arab-emirates": "AE",
    "qatar": "QA", "saudi-arabia": "SA",
    "iceland": "IS", "india": "IN",
    "philippines": "PH", "china": "CN",
    "georgia": "GE", "serbia": "RS",
    "kenya": "KE", "peru": "PE",
    "brazil": "BR", "chile": "CL",
    "albania": "AL", "sri-lanka": "LK",
    "egypt": "EG",
    "turkey": "TR", "kazakhstan": "KZ",
    "lithuania": "LT", "latvia": "LV",
    "estonia": "EE", "south-africa": "ZA",
    "cambodia": "KH", "uruguay": "UY",
    "paraguay": "PY", "bolivia": "BO",
    "ghana": "GH", "rwanda": "RW",
    "nepal": "NP", "taiwan": "TW",
    "slovenia": "SI", "slovakia": "SK",
    "malta": "MT", "cyprus": "CY",
    "montenegro": "ME", "north-macedonia": "MK",
    "dominican-republic": "DO", "belize": "BZ",
    "el-salvador": "SV", "honduras": "HN",
    "jamaica": "JM", "nicaragua": "NI",
    "bahamas": "BS",
}


def fetch_country_budget(slug, iso2):
    """Fetch cost of living data for one
    country from WhereNext API"""
    url = (
        f"https://getwherenext.com/api/data/"
        f"ai-cost-of-living/{iso2.lower()}"
    )
    response = requests.get(
        url, headers=HEADERS, timeout=15
    )
    response.raise_for_status()
    payload = response.json()

    data = payload.get('data', {})
    monthly = data.get('monthlyEstimate', {})
    cities = data.get('mostAffordableCities', [])

    single = monthly.get('singlePerson')
    couple = monthly.get('couple')
    cost_index = data.get('costIndex')
    us_comparison = data.get('usComparison')

    affordable_cities = []
    for city in cities[:3]:
        affordable_cities.append({
            'name': city.get('name'),
            'monthly_usd': city.get(
                'estimatedMonthlyCostUsd'
            ),
        })

    return {
        'budget_single': single,
        'budget_couple': couple,
        'cost_index': cost_index,
        'us_comparison': us_comparison,
        'affordable_cities': affordable_cities,
    }


def fetch_all_budgets():
    """Fetch budget data for all 82 countries.
    WhereNext has no documented rate limit,
    but we add a small courtesy delay between
    requests anyway."""
    print("--- Monthly Budget "
          "(WhereNext Open Data API) ---")
    print("Source: getwherenext.com — "
          "CC BY 4.0, World Bank ICP / "
          "Eurostat institutional data\n")

    results = {}
    failed = []

    for slug, iso2 in COUNTRY_CODES.items():
        try:
            result = fetch_country_budget(
                slug, iso2
            )
            results[slug] = result
            print(
                f"  {slug} ({iso2}): "
                f"single=${result['budget_single']}, "
                f"couple=${result['budget_couple']}, "
                f"index={result['cost_index']}"
            )
            time.sleep(0.5)
        except Exception as e:
            print(f"  WARNING: {slug} ({iso2}) "
                  f"failed: {e}")
            failed.append(slug)
            continue

    print(f"\nFetched {len(results)}/"
          f"{len(COUNTRY_CODES)} countries")
    if failed:
        print(f"Failed: {', '.join(failed)}")

    return results


def merge_into_json(budget_data):
    """Merge WhereNext budget data into
    existing quality-scores.json without
    touching any other fields"""
    with open(DATA_PATH, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)

    countries_data = data.get('countries', {})
    updated_count = 0

    for slug, vals in budget_data.items():
        if slug not in countries_data:
            print(f"  SKIP: {slug} not found "
                  f"in quality-scores.json")
            continue
        countries_data[slug]['budget_single'] = (
            vals.get('budget_single')
        )
        countries_data[slug]['budget_couple'] = (
            vals.get('budget_couple')
        )
        countries_data[slug]['cost_index'] = (
            vals.get('cost_index')
        )
        countries_data[slug]['us_comparison'] = (
            vals.get('us_comparison')
        )
        countries_data[slug]['affordable_cities'] = (
            vals.get('affordable_cities')
        )
        updated_count += 1

    data['budget_data_source'] = (
        'WhereNext (getwherenext.com), '
        'CC BY 4.0, World Bank ICP + Eurostat'
    )

    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nMerged budget data into "
          f"{updated_count}/{len(COUNTRY_CODES)} "
          f"countries in {DATA_PATH}")


if __name__ == "__main__":
    budget_data = fetch_all_budgets()
    if budget_data:
        merge_into_json(budget_data)
    else:
        print("\nNo data fetched — "
              "nothing to merge.")
