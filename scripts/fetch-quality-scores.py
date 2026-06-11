import requests
from bs4 import BeautifulSoup
import json
import time
import csv
import io
from datetime import date
import sys
sys.stdout.reconfigure(encoding='utf-8')

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

COUNTRIES = {
    "Portugal": "portugal",
    "Spain": "spain",
    "Mexico": "mexico",
    "Germany": "germany",
    "Italy": "italy",
    "Greece": "greece",
    "Costa Rica": "costa-rica",
    "Panama": "panama",
    "Thailand": "thailand",
    "Malaysia": "malaysia",
    "Indonesia": "indonesia",
    "Colombia": "colombia",
    "Croatia": "croatia",
    "Czech Republic": "czech-republic",
    "Poland": "poland",
    "Hungary": "hungary",
    "Romania": "romania",
    "Bulgaria": "bulgaria",
    "Vietnam": "vietnam",
    "Japan": "japan",
    "South Korea": "south-korea",
    "Australia": "australia",
    "New Zealand": "new-zealand",
    "Canada": "canada",
    "Ireland": "ireland",
    "Netherlands": "netherlands",
    "France": "france",
    "Argentina": "argentina",
    "Ecuador": "ecuador",
    "Morocco": "morocco"
}

# ISO3 codes for OWID happiness CSV
OWID_CODES = {
    "portugal": "PRT", "spain": "ESP", "mexico": "MEX",
    "germany": "DEU", "italy": "ITA", "greece": "GRC",
    "costa-rica": "CRI", "panama": "PAN", "thailand": "THA",
    "malaysia": "MYS", "indonesia": "IDN", "colombia": "COL",
    "croatia": "HRV", "czech-republic": "CZE", "poland": "POL",
    "hungary": "HUN", "romania": "ROU", "bulgaria": "BGR",
    "vietnam": "VNM", "japan": "JPN", "south-korea": "KOR",
    "australia": "AUS", "new-zealand": "NZL", "canada": "CAN",
    "ireland": "IRL", "netherlands": "NLD", "france": "FRA",
    "argentina": "ARG", "ecuador": "ECU", "morocco": "MAR"
}

# ISO2 codes for World Bank API
WORLD_BANK_CODES = {
    "portugal": "PT", "spain": "ES", "mexico": "MX",
    "germany": "DE", "italy": "IT", "greece": "GR",
    "costa-rica": "CR", "panama": "PA", "thailand": "TH",
    "malaysia": "MY", "indonesia": "ID", "colombia": "CO",
    "croatia": "HR", "czech-republic": "CZ", "poland": "PL",
    "hungary": "HU", "romania": "RO", "bulgaria": "BG",
    "vietnam": "VN", "japan": "JP", "south-korea": "KR",
    "australia": "AU", "new-zealand": "NZ", "canada": "CA",
    "ireland": "IE", "netherlands": "NL", "france": "FR",
    "argentina": "AR", "ecuador": "EC", "morocco": "MA"
}

# Wikipedia country name variations to match our slugs
WIKIPEDIA_NAMES = {
    "Portugal": "portugal",
    "Spain": "spain",
    "Mexico": "mexico",
    "Germany": "germany",
    "Italy": "italy",
    "Greece": "greece",
    "Costa Rica": "costa-rica",
    "Panama": "panama",
    "Thailand": "thailand",
    "Malaysia": "malaysia",
    "Indonesia": "indonesia",
    "Colombia": "colombia",
    "Croatia": "croatia",
    "Czech Republic": "czech-republic",
    "Czechia": "czech-republic",
    "Poland": "poland",
    "Hungary": "hungary",
    "Romania": "romania",
    "Bulgaria": "bulgaria",
    "Vietnam": "vietnam",
    "Japan": "japan",
    "South Korea": "south-korea",
    "Australia": "australia",
    "New Zealand": "new-zealand",
    "Canada": "canada",
    "Ireland": "ireland",
    "Netherlands": "netherlands",
    "France": "france",
    "Argentina": "argentina",
    "Ecuador": "ecuador",
    "Morocco": "morocco"
}

def safety_to_score(value):
    if value is None:
        return None
    score = round(float(value) / 10)
    return max(1, min(10, score))

def healthcare_to_score(value):
    if value is None:
        return None
    score = round(float(value) / 15)
    return max(1, min(10, score))

def pollution_to_score(value):
    if value is None:
        return None
    v = float(value)
    if v < 30: return 10
    elif v < 45: return 9
    elif v < 60: return 8
    elif v < 75: return 7
    elif v < 90: return 6
    elif v < 110: return 5
    elif v < 135: return 4
    else: return 3

def traffic_to_score(value):
    if value is None:
        return None
    v = float(value)
    if v < 2000: return 10
    elif v < 3000: return 9
    elif v < 4000: return 8
    elif v < 5000: return 7
    elif v < 6000: return 6
    elif v < 7000: return 5
    elif v < 8000: return 4
    else: return 3

def unemployment_to_score(value):
    if value is None:
        return None
    v = float(value)
    if v < 3: return 10
    elif v < 5: return 9
    elif v < 7: return 8
    elif v < 9: return 7
    elif v < 12: return 6
    elif v < 15: return 5
    elif v < 20: return 4
    else: return 3

def gdp_growth_to_score(value):
    if value is None:
        return None
    v = float(value)
    if v > 5: return 10
    elif v > 4: return 9
    elif v > 3: return 8
    elif v > 2: return 7
    elif v > 1: return 6
    elif v > 0: return 5
    elif v > -1: return 4
    else: return 3

def happiness_to_score(value):
    if value is None:
        return None
    # WHR scale 0-10, convert to 1-10
    score = round(float(value))
    return max(1, min(10, score))

def internet_to_score(value):
    if value is None:
        return None
    v = float(value)
    if v < 60: return 5
    elif v < 90: return 6
    elif v < 130: return 7
    elif v < 180: return 8
    elif v < 250: return 9
    else: return 10

def parse_numbeo_rankings(url):
    print(f"Fetching: {url}")
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'id': 't2'})
    if not table:
        print("WARNING: table#t2 not found")
        return {}
    results = {}
    for row in table.find_all('tr'):
        cols = row.find_all('td')
        if len(cols) < 3:
            continue
        country_name = cols[1].get_text(strip=True)
        for col in reversed(cols):
            text = col.get_text(strip=True)
            try:
                value = float(text)
                results[country_name] = value
                break
            except ValueError:
                continue
    return results

def fetch_world_bank_indicator(indicator_code):
    iso_codes = ";".join(WORLD_BANK_CODES.values())
    url = (f"https://api.worldbank.org/v2/country/{iso_codes}"
           f"/indicator/{indicator_code}"
           f"?format=json&mrv=1&per_page=35")
    print(f"Fetching World Bank: {indicator_code}")
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    data = response.json()
    if not data[1]:
        print(f"WARNING: No data for {indicator_code}")
        return {}
    results = {}
    for item in data[1]:
        if item["value"] is not None:
            iso2 = item["country"]["id"]
            for slug, code in WORLD_BANK_CODES.items():
                if code == iso2:
                    results[slug] = item["value"]
                    break
    return results

def fetch_happiness_owid():
    url = ("https://ourworldindata.org/grapher/"
           "happiness-cantril-ladder.csv?v=1&csvType=full")
    print(f"Fetching: {url}")
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    results = {}
    # Find latest score for each country
    latest = {}
    reader = csv.DictReader(io.StringIO(response.text))
    for row in reader:
        code = row.get("Code", "")
        year = row.get("Year", "")
        value_key = [k for k in row.keys()
                     if "satisfaction" in k.lower() or
                     "cantril" in k.lower() or
                     "happiness" in k.lower()]
        if not value_key:
            continue
        value = row.get(value_key[0], "")
        if not value or not code or not year:
            continue
        try:
            v = float(value)
            y = int(year)
            if code not in latest or y > latest[code][0]:
                latest[code] = (y, v)
        except (ValueError, TypeError):
            continue
    # Map ISO3 codes to our slugs
    for slug, iso3 in OWID_CODES.items():
        if iso3 in latest:
            year, value = latest[iso3]
            results[slug] = value
            print(f"  {slug}: {value:.3f} (year {year})")
        else:
            print(f"  NOT FOUND: {slug} ({iso3})")
    return results

def fetch_internet_wikipedia():
    url = ("https://en.wikipedia.org/wiki/"
           "List_of_countries_by_Internet_connection_speeds")
    print(f"Fetching: {url}")
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    results = {}
    tables = soup.find_all('table', {'class': 'wikitable'})
    # Use only the first table (fixed broadband)
    # The page has two tables: fixed broadband and mobile
    # We want fixed broadband as it's more representative
    if tables:
        tables = [tables[0]]
    for table in tables:
        for row in table.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) < 2:
                continue
            # Get all text from first column including links
            country_cell = cols[0]
            # Find anchor tag with country name
            link = country_cell.find('a')
            if link:
                country_name = link.get_text(strip=True)
            else:
                country_name = country_cell.get_text(strip=True)
            # Clean up country name
            country_name = country_name.strip()
            # Find first numeric value in row
            speed_val = None
            for col in cols[1:]:
                text = col.get_text(strip=True).replace(',', '').replace('\xa0', '')
                try:
                    speed_val = float(text)
                    if speed_val > 0:
                        break
                except ValueError:
                    continue
            if speed_val and country_name in WIKIPEDIA_NAMES:
                slug = WIKIPEDIA_NAMES[country_name]
                results[slug] = speed_val
                print(f"  {slug}: {speed_val} Mbps ({country_name})")
            elif speed_val and country_name:
                # Debug: show unmatched countries
                pass
    return results

# STEP 1 - Numbeo Safety
print("\n--- Step 1: Safety Index (Numbeo) ---")
safety_data = parse_numbeo_rankings(
    "https://www.numbeo.com/crime/rankings_by_country.jsp"
    "?displayColumn=1"
)
print(f"Found {len(safety_data)} countries")
time.sleep(3)

# STEP 2 - Numbeo Healthcare
print("\n--- Step 2: Healthcare Index (Numbeo) ---")
health_data = parse_numbeo_rankings(
    "https://www.numbeo.com/health-care/rankings_by_country.jsp"
)
print(f"Found {len(health_data)} countries")
time.sleep(3)

# STEP 3 - Numbeo Pollution
print("\n--- Step 3: Pollution Index (Numbeo) ---")
pollution_data = parse_numbeo_rankings(
    "https://www.numbeo.com/pollution/rankings_by_country.jsp"
)
print(f"Found {len(pollution_data)} countries")
time.sleep(3)

# STEP 4 - Numbeo Traffic
print("\n--- Step 4: Traffic Index (Numbeo) ---")
traffic_data = parse_numbeo_rankings(
    "https://www.numbeo.com/traffic/rankings_by_country.jsp"
)
print(f"Found {len(traffic_data)} countries")
time.sleep(3)

# STEP 5 - World Bank Unemployment
print("\n--- Step 5: Unemployment (World Bank) ---")
unemployment_data = fetch_world_bank_indicator("SL.UEM.TOTL.ZS")
print(f"Found {len(unemployment_data)} countries")
time.sleep(2)

# STEP 6 - World Bank GDP Growth
print("\n--- Step 6: GDP Growth (World Bank) ---")
gdp_data = fetch_world_bank_indicator("NY.GDP.MKTP.KD.ZG")
print(f"Found {len(gdp_data)} countries")
time.sleep(2)

# STEP 7 - OWID Happiness
print("\n--- Step 7: Happiness (Our World in Data / WHR) ---")
happiness_data = fetch_happiness_owid()
print(f"Found {len(happiness_data)} countries")
time.sleep(2)

# STEP 8 - Wikipedia Internet Speeds
print("\n--- Step 8: Internet Speeds (Wikipedia/Speedtest) ---")
internet_data = fetch_internet_wikipedia()
print(f"Found {len(internet_data)} countries")

# BUILD RESULTS
print("\n--- Building results ---")
results = {}

for numbeo_name, slug in COUNTRIES.items():
    safety_val = safety_data.get(numbeo_name)
    health_val = health_data.get(numbeo_name)
    pollution_val = pollution_data.get(numbeo_name)
    traffic_val = traffic_data.get(numbeo_name)
    unemp_val = unemployment_data.get(slug)
    gdp_val = gdp_data.get(slug)
    happiness_val = happiness_data.get(slug)
    internet_val = internet_data.get(slug)

    results[slug] = {
        "safety": safety_to_score(safety_val),
        "healthcare": healthcare_to_score(health_val),
        "pollution": pollution_to_score(pollution_val),
        "traffic": traffic_to_score(traffic_val),
        "unemployment": unemployment_to_score(unemp_val),
        "gdpGrowth": gdp_growth_to_score(gdp_val),
        "happiness": happiness_to_score(happiness_val),
        "internet": internet_to_score(internet_val),
        "raw": {
            "safety": round(safety_val, 1) if safety_val else None,
            "healthcare": round(health_val, 1) if health_val else None,
            "pollution": round(pollution_val, 1) if pollution_val else None,
            "traffic": round(traffic_val, 1) if traffic_val else None,
            "unemployment": round(unemp_val, 2) if unemp_val else None,
            "gdpGrowth": round(gdp_val, 2) if gdp_val else None,
            "happiness": round(happiness_val, 3) if happiness_val else None,
            "internet": round(internet_val, 2) if internet_val else None
        }
    }

    print(f"[OK] {numbeo_name}: "
          f"safety={results[slug]['safety']}, "
          f"health={results[slug]['healthcare']}, "
          f"pollution={results[slug]['pollution']}, "
          f"traffic={results[slug]['traffic']}, "
          f"unemp={results[slug]['unemployment']}, "
          f"gdp={results[slug]['gdpGrowth']}, "
          f"happy={results[slug]['happiness']}, "
          f"net={results[slug]['internet']}")

# SAVE
output = {
    "lastUpdated": str(date.today()),
    "source": {
        "safety": "Numbeo Safety Index (latest available) - numbeo.com",
        "healthcare": "Numbeo Health Care Index (latest available) - numbeo.com",
        "pollution": "Numbeo Pollution Index (latest available) - numbeo.com",
        "traffic": "Numbeo Traffic Index (latest available) - numbeo.com",
        "unemployment": "World Bank ILO Unemployment (latest available) - data.worldbank.org",
        "gdpGrowth": "World Bank GDP Growth (latest available) - data.worldbank.org",
        "happiness": "World Happiness Report via Our World in Data (latest available) - ourworldindata.org",
        "internet": "Speedtest Global Index via Wikipedia (latest available) - en.wikipedia.org/wiki/List_of_countries_by_Internet_connection_speeds"
    },
    "countries": results
}

with open("src/data/quality-scores.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

complete = sum(1 for v in results.values()
               if all(v.get(k) for k in
               ["safety", "healthcare", "pollution", "traffic",
                "unemployment", "gdpGrowth", "happiness", "internet"]))
print(f"\nDone. {complete}/30 countries fully complete.")
print(f"Saved to src/data/quality-scores.json")
print(f"Date: {str(date.today())}")
