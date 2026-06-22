import requests
from bs4 import BeautifulSoup
import json
import time
import csv
import io
import re
from datetime import date
import sys
sys.stdout.reconfigure(encoding='utf-8')

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

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
    "South Korea": ["South Korea", "Korea, Republic of",
                    "Korea, Rep."],
    "Spain": ["Spain"],
    "Sri Lanka": ["Sri Lanka"],
    "Sweden": ["Sweden"],
    "Switzerland": ["Switzerland"],
    "Thailand": ["Thailand"],
    "United Arab Emirates": ["United Arab Emirates", "UAE"],
    "United Kingdom": ["United Kingdom", "UK"],
    "Vietnam": ["Vietnam", "Viet Nam"]
}

def match_country(country_name, source_name):
    """Check if source_name matches country_name or its aliases"""
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

TAX_SYSTEMS = {
    "Albania": "worldwide",
    "Argentina": "worldwide",
    "Australia": "worldwide",
    "Austria": "worldwide",
    "Belgium": "worldwide",
    "Brazil": "worldwide",
    "Bulgaria": "worldwide",
    "Chile": "worldwide",
    "Canada": "worldwide",
    "China": "worldwide",
    "Colombia": "worldwide",
    "Costa Rica": "territorial",
    "Croatia": "worldwide",
    "Czech Republic": "worldwide",
    "Denmark": "worldwide",
    "Ecuador": "worldwide",
    "Egypt": "worldwide",
    "Finland": "worldwide",
    "France": "worldwide",
    "Georgia": "territorial",
    "Germany": "worldwide",
    "Greece": "worldwide",
    "Hungary": "worldwide",
    "Iceland": "worldwide",
    "India": "worldwide",
    "Indonesia": "worldwide",
    "Ireland": "worldwide",
    "Italy": "worldwide",
    "Japan": "worldwide",
    "Kenya": "worldwide",
    "Malaysia": "territorial",
    "Mexico": "worldwide",
    "Morocco": "worldwide",
    "Netherlands": "worldwide",
    "New Zealand": "worldwide",
    "Norway": "worldwide",
    "Panama": "territorial",
    "Peru": "worldwide",
    "Philippines": "worldwide",
    "Poland": "worldwide",
    "Portugal": "worldwide",
    "Qatar": "zero",
    "Romania": "worldwide",
    "Saudi Arabia": "zero",
    "Serbia": "worldwide",
    "Singapore": "territorial",
    "South Korea": "worldwide",
    "Spain": "worldwide",
    "Sri Lanka": "worldwide",
    "Sweden": "worldwide",
    "Switzerland": "worldwide",
    "Thailand": "territorial",
    "United Arab Emirates": "zero",
    "United Kingdom": "worldwide",
    "Vietnam": "worldwide"
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
    "Morocco": "morocco",
    "Switzerland": "switzerland",
    "Norway": "norway",
    "Denmark": "denmark",
    "Sweden": "sweden",
    "Belgium": "belgium",
    "Austria": "austria",
    "Finland": "finland",
    "United Kingdom": "united-kingdom",
    "Singapore": "singapore",
    "United Arab Emirates": "united-arab-emirates",
    "Qatar": "qatar",
    "Saudi Arabia": "saudi-arabia",
    "Iceland": "iceland",
    "India": "india",
    "Philippines": "philippines",
    "China": "china",
    "Georgia": "georgia",
    "Serbia": "serbia",
    "Kenya": "kenya",
    "Peru": "peru",
    "Brazil": "brazil",
    "Chile": "chile",
    "Albania": "albania",
    "Sri Lanka": "sri-lanka",
    "Egypt": "egypt"
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
    "argentina": "ARG", "ecuador": "ECU", "morocco": "MAR",
    "switzerland": "CHE", "norway": "NOR", "denmark": "DNK",
    "sweden": "SWE", "belgium": "BEL", "austria": "AUT",
    "finland": "FIN", "united-kingdom": "GBR", "singapore": "SGP",
    "united-arab-emirates": "ARE", "qatar": "QAT", "saudi-arabia": "SAU",
    "iceland": "ISL", "india": "IND", "philippines": "PHL",
    "china": "CHN", "georgia": "GEO", "serbia": "SRB",
    "kenya": "KEN", "peru": "PER", "brazil": "BRA",
    "chile": "CHL", "albania": "ALB", "sri-lanka": "LKA",
    "egypt": "EGY"
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
    "argentina": "AR", "ecuador": "EC", "morocco": "MA",
    "switzerland": "CH", "norway": "NO", "denmark": "DK",
    "sweden": "SE", "belgium": "BE", "austria": "AT",
    "finland": "FI", "united-kingdom": "GB", "singapore": "SG",
    "united-arab-emirates": "AE", "qatar": "QA", "saudi-arabia": "SA",
    "iceland": "IS", "india": "IN", "philippines": "PH",
    "china": "CN", "georgia": "GE", "serbia": "RS",
    "kenya": "KE", "peru": "PE", "brazil": "BR",
    "chile": "CL", "albania": "AL", "sri-lanka": "LK",
    "egypt": "EG"
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
    "Morocco": "morocco",
    "Switzerland": "switzerland",
    "Norway": "norway",
    "Denmark": "denmark",
    "Sweden": "sweden",
    "Belgium": "belgium",
    "Austria": "austria",
    "Finland": "finland",
    "United Kingdom": "united-kingdom",
    "Singapore": "singapore",
    "United Arab Emirates": "united-arab-emirates",
    "Qatar": "qatar",
    "Saudi Arabia": "saudi-arabia",
    "Iceland": "iceland",
    "India": "india",
    "Philippines": "philippines",
    "China": "china",
    "Georgia": "georgia",
    "Serbia": "serbia",
    "Kenya": "kenya",
    "Peru": "peru",
    "Brazil": "brazil",
    "Chile": "chile",
    "Albania": "albania",
    "Sri Lanka": "sri-lanka",
    "Egypt": "egypt"
}

def safety_to_score(value):
    if value is None:
        return None
    score = round(float(value) / 10)
    return max(1, min(10, score))

def healthcare_to_score(value):
    if value is None:
        return None
    v = float(value)
    if v >= 130: return 10
    elif v >= 110: return 9
    elif v >= 90:  return 8
    elif v >= 75:  return 7
    elif v >= 60:  return 6
    elif v >= 45:  return 5
    elif v >= 35:  return 4
    elif v >= 25:  return 3
    elif v >= 15:  return 2
    else:          return 1

def gpi_to_score(gpi_score):
    """Convert Global Peace Index score (1.0-5.0 scale, lower = more
    peaceful) to 1-10 safety score. Calibrated against the real 2026 GPI
    distribution: Iceland 1.161 (most peaceful) to Russia 3.367 (least
    peaceful among ranked nations), with most countries clustering 1.4-2.8."""
    if gpi_score is None:
        return None
    v = float(gpi_score)
    if v <= 1.3:   return 10
    elif v <= 1.5: return 9
    elif v <= 1.7: return 8
    elif v <= 1.9: return 7
    elif v <= 2.1: return 6
    elif v <= 2.3: return 5
    elif v <= 2.5: return 4
    elif v <= 2.8: return 3
    elif v <= 3.1: return 2
    else:          return 1

def homicide_to_score(rate):
    """Convert intentional homicides per 100k to 1-10 safety score.
    Lower rate = safer. Calibrated against real global distribution:
    global median ~2.6, most developed nations <1.5,
    worst-case countries 20-76 (UNODC/World Bank data, 2025 snapshot)."""
    if rate is None:
        return None
    v = float(rate)
    if v < 1.0:   return 10
    elif v < 2.0:  return 9
    elif v < 3.5:  return 8
    elif v < 5.5:  return 7
    elif v < 8.0:  return 6
    elif v < 12.0: return 5
    elif v < 18.0: return 4
    elif v < 25.0: return 3
    elif v < 40.0: return 2
    else:          return 1

def uhc_to_score(index_value):
    """Convert WHO/World Bank UHC Service Coverage Index (0-100 scale)
    to 1-10 healthcare score. Simple linear conversion since the index
    is already a well-calibrated 0-100 composite."""
    if index_value is None:
        return None
    v = float(index_value)
    score = round(v / 10)
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
    # Split into two batches to avoid timeout with 55 countries
    all_codes = list(WORLD_BANK_CODES.values())
    mid = len(all_codes) // 2
    batch1 = ";".join(all_codes[:mid])
    batch2 = ";".join(all_codes[mid:])

    results = {}
    for iso_codes in [batch1, batch2]:
        url = (f"https://api.worldbank.org/v2/country/{iso_codes}"
               f"/indicator/{indicator_code}"
               f"?format=json&mrv=1&per_page=35")
        print(f"Fetching World Bank: {indicator_code} (batch)")
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        data = response.json()
        if not data[1]:
            continue
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
    response = requests.get(url, timeout=30, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/csv,application/csv,text/plain,*/*',
    })
    response.raise_for_status()
    if 'text/html' in response.headers.get('Content-Type', ''):
        raise ValueError('OWID returned HTML instead of CSV')
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
    import time
    time.sleep(2)
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })
    response = session.get(url, timeout=30)
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

def fetch_homicide_rate():
    """Fetch Intentional Homicides per 100k from World Bank —
    objective safety proxy, replacing subjective Numbeo Safety Index"""
    print("\n--- Step: Homicide Rate "
          "(World Bank VC.IHR.PSRC.P5 - objective safety) ---")
    results = fetch_world_bank_indicator("VC.IHR.PSRC.P5")
    print(f"Found {len(results)} countries")
    return results


def fetch_uhc_index():
    """Fetch UHC Service Coverage Index from World Bank —
    objective healthcare proxy, replacing subjective Numbeo Health Care Index"""
    print("\n--- Step: UHC Healthcare Index "
          "(World Bank SH.UHC.SRVS.CV.XD - objective healthcare) ---")
    results = fetch_world_bank_indicator("SH_UHC_SCI")
    print(f"Found {len(results)} countries")
    return results


def fetch_global_peace_index():
    """Fetch Global Peace Index scores from Wikipedia — composite
    safety/stability measure (conflict, terrorism, crime, political
    instability) covering 163 countries, replacing the homicide-rate-only
    approach which had gaps for 17 of our 55 countries."""
    print("\n--- Step: Global Peace Index (Wikipedia) ---")
    time.sleep(2)
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; '
        'Win64; x64) AppleWebKit/537.36 (KHTML, '
        'like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,'
        'application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    })
    url = "https://en.wikipedia.org/wiki/Global_Peace_Index"
    response = session.get(url, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    results = {}
    tables = soup.find_all('table', class_='wikitable')
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 3:
                continue
            try:
                # Table format: Rank | Country | Score | Change
                # Country cell may contain flag icon + name
                country_cell = cells[1]
                score_cell = cells[2]
                country = country_cell.get_text(strip=True)
                score_text = score_cell.get_text(strip=True)
                score = float(score_text)
                if 0.5 <= score <= 5.0:
                    country = re.sub(r'\[.*?\]', '', country).strip()
                    results[country] = score
            except (ValueError, IndexError):
                continue

    print(f"  Found {len(results)} countries")
    return results


def fetch_english_proficiency():
    """Fetch EF English Proficiency Index from Wikipedia"""
    print("\n--- Step 9: English Proficiency (EF EPI / Wikipedia) ---")
    url = "https://en.wikipedia.org/wiki/EF_English_Proficiency_Index"
    response = requests.get(url, timeout=30, headers=HEADERS)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    results = {}
    tables = soup.find_all('table', class_='wikitable')
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) < 3:
                continue
            try:
                # Try each cell as potential score (200-700 range)
                country = None
                score = None
                for i, cell in enumerate(cells):
                    text = cell.get_text(strip=True)
                    try:
                        val = float(text.replace(',', '.'))
                        if 200 <= val <= 700:
                            score = val
                            # Country is likely the previous cell
                            if i > 0:
                                country = cells[i-1].get_text(
                                    strip=True
                                )
                            break
                    except ValueError:
                        continue
                if country and score:
                    # Clean country name
                    country = re.sub(r'\[.*?\]', '', country).strip()
                    if 2 < len(country) < 50:
                        results[country] = score
            except Exception:
                continue

    print(f"  Found {len(results)} countries")
    return results


def fetch_visa_requirements():
    """Fetch US passport visa requirements from Passport Index CSV"""
    print("\n--- Step 10: Visa Requirements (Passport Index / GitHub) ---")
    url = ("https://raw.githubusercontent.com/"
           "ilyankou/passport-index-dataset/master/"
           "passport-index-tidy.csv")
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    content = response.text
    reader = csv.DictReader(io.StringIO(content))

    # Debug: show actual column names
    fieldnames = reader.fieldnames
    print(f"  CSV columns: {fieldnames}")

    results = {}
    # Handle both capitalized and lowercase column names
    passport_col = None
    dest_col = None
    req_col = None

    if fieldnames:
        for col in fieldnames:
            col_lower = col.lower().strip()
            if 'passport' in col_lower:
                passport_col = col
            elif 'destination' in col_lower or 'dest' in col_lower:
                dest_col = col
            elif 'requirement' in col_lower or 'req' in col_lower:
                req_col = col

    if not all([passport_col, dest_col, req_col]):
        print(f"  WARNING: Could not find required columns. "
              f"Found: {fieldnames}")
        return results

    # Debug: show first 5 passport values
    reader2 = csv.DictReader(io.StringIO(content))
    sample = []
    for i, row in enumerate(reader2):
        if i < 5:
            sample.append(row.get(passport_col, ''))
    print(f"  Sample passport values: {sample}")

    # Re-read with correct column names
    reader = csv.DictReader(io.StringIO(content))
    for row in reader:
        passport = row.get(passport_col, '').strip().upper()
        if passport in ['US', 'UNITED STATES',
                        'United States', 'USA']:
            destination = row.get(dest_col, '').strip()
            requirement = row.get(req_col, '').strip()
            if destination:
                results[destination] = requirement

    print(f"  Found {len(results)} destinations for US passport")
    return results


def fetch_nomad_visas():
    """Fetch digital nomad visa availability from Citizen Remote"""
    print("\n--- Step 11: Digital Nomad Visas (Citizen Remote) ---")
    url = ("https://citizenremote.com/blog/"
           "digital-nomad-visa-countries/")
    response = requests.get(url, timeout=30, headers=HEADERS)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    nomad_countries = set()

    # Known countries with digital nomad visas
    # as fallback if scraping fails
    known_nomad_countries = {
        "Albania", "Brazil", "Chile", "Colombia",
        "Costa Rica", "Croatia", "Czech Republic",
        "Ecuador", "Georgia", "Germany", "Greece",
        "Hungary", "Iceland", "Indonesia", "Italy",
        "Japan", "Malaysia", "Mexico", "Netherlands",
        "Norway", "Panama", "Peru", "Philippines",
        "Portugal", "Romania", "Saudi Arabia",
        "Serbia", "Singapore", "South Korea", "Spain",
        "Sri Lanka", "Thailand", "United Arab Emirates",
        "United Kingdom", "Vietnam"
    }

    # Try to scrape headings
    headings = soup.find_all(['h2', 'h3'])
    found_via_scraping = False

    for heading in headings:
        text = heading.get_text(strip=True)
        # Remove footnotes and clean
        text = re.sub(r'\[.*?\]', '', text).strip()

        # Skip navigation/section headings
        skip_words = [
            'intro', 'what is', 'why', 'how to',
            'requirement', 'tax', 'europe', 'asia',
            'america', 'africa', 'caribbean',
            'digital nomad visa', 'conclusion', 'faq',
            'table of contents', 'overview', 'guide'
        ]
        if any(skip in text.lower() for skip in skip_words):
            continue

        if 2 < len(text) < 60:
            nomad_countries.add(text)
            found_via_scraping = True

    if not found_via_scraping or len(nomad_countries) < 10:
        print("  WARNING: Scraping returned few results, "
              "using known list as fallback")
        nomad_countries = known_nomad_countries

    print(f"  Found {len(nomad_countries)} countries "
          f"with nomad visas")
    return nomad_countries


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

# STEP 6b - World Bank Homicide Rate (objective safety proxy)
homicide_data = fetch_homicide_rate()
time.sleep(2)

# STEP 6c - World Bank UHC Index (objective healthcare proxy)
uhc_data = fetch_uhc_index()
time.sleep(2)

# STEP 6d - Global Peace Index (primary safety source, Wikipedia)
gpi_data = fetch_global_peace_index()
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

english_data = fetch_english_proficiency()
visa_data = fetch_visa_requirements()
nomad_data = fetch_nomad_visas()

# BUILD RESULTS
print("\n--- Building results ---")
results = {}

for numbeo_name, slug in COUNTRIES.items():
    country_name = numbeo_name

    homicide_rate = homicide_data.get(slug)
    uhc_val = uhc_data.get(slug)

    # GPI requires fuzzy name matching like english_data/visa_data
    gpi_score = None
    for source_country, score in gpi_data.items():
        if match_country(country_name, source_country):
            gpi_score = score
            break

    # Keep old Numbeo values as secondary reference
    safety_val_numbeo_legacy = safety_data.get(numbeo_name)
    health_val_numbeo_legacy = health_data.get(numbeo_name)
    pollution_val = pollution_data.get(numbeo_name)
    traffic_val = traffic_data.get(numbeo_name)
    unemp_val = unemployment_data.get(slug)
    gdp_val = gdp_data.get(slug)
    happiness_val = happiness_data.get(slug)
    internet_val = internet_data.get(slug)

    # English proficiency
    english_score = None
    english_raw = None
    for source_country, en_score in english_data.items():
        if match_country(country_name, source_country):
            english_score = round(en_score, 1)
            english_raw = round(en_score, 1)
            print(f"  {country_name}: english={english_score}")
            break

    NATIVE_ENGLISH = {
        'Australia', 'New Zealand', 'Canada',
        'Ireland', 'Singapore', 'United Kingdom',
        'United States'
    }
    if country_name in NATIVE_ENGLISH:
        english_score = 999
        english_raw = 999

    ENGLISH_OVERRIDES = {
        'Iceland': 630.0,
    }
    if english_score is None and country_name in ENGLISH_OVERRIDES:
        english_score = ENGLISH_OVERRIDES[country_name]
        english_raw = ENGLISH_OVERRIDES[country_name]

    # Visa requirements
    visa_info = None
    visa_days = None
    for dest_country, requirement in visa_data.items():
        if match_country(country_name, dest_country):
            visa_info = requirement
            # Extract days using regex
            m = re.search(r'(\d+)', requirement)
            if m:
                visa_days = int(m.group(1))
            elif any(x in requirement.lower() for x in [
                'visa free', 'visa-free', 'freedom of movement'
            ]):
                visa_days = 180
            elif any(x in requirement.lower() for x in [
                'visa on arrival', 'on arrival'
            ]):
                visa_days = 30
            elif requirement.lower() in ['eta', 'evisa',
                                          'e-visa', 'electronic']:
                visa_days = 90
            elif requirement.lower() == 'visa required':
                visa_days = 0
            break

    VISA_OVERRIDES = {
        "Romania": 90,
    }
    if visa_days is not None and country_name in VISA_OVERRIDES:
        visa_days = VISA_OVERRIDES[country_name]
        visa_info = str(VISA_OVERRIDES[country_name])

    # Tax system from static dictionary
    tax_system = TAX_SYSTEMS.get(country_name)

    # Digital nomad visa
    has_nomad_visa = False
    for nomad_country in nomad_data:
        if match_country(country_name, nomad_country):
            has_nomad_visa = True
            break

    results[slug] = {
        "safety": gpi_to_score(gpi_score) if gpi_score is not None else homicide_to_score(homicide_rate),
        "healthcare": uhc_to_score(uhc_val),
        "pollution": pollution_to_score(pollution_val),
        "traffic": traffic_to_score(traffic_val),
        "unemployment": unemployment_to_score(unemp_val),
        "gdpGrowth": gdp_growth_to_score(gdp_val),
        "happiness": happiness_to_score(happiness_val),
        "internet": internet_to_score(internet_val),
        "english": english_score,
        "visa_days": visa_days,
        "visa_info": visa_info,
        "tax_system": tax_system,
        "nomad_visa": has_nomad_visa,
        "raw": {
            "safety": round(gpi_score, 3) if gpi_score is not None else (round(homicide_rate, 2) if homicide_rate is not None else None),
            "safety_source": "gpi" if gpi_score is not None else ("homicide_rate" if homicide_rate is not None else None),
            "healthcare": round(uhc_val, 1) if uhc_val is not None else None,
            "safety_homicide_legacy": round(homicide_rate, 2) if homicide_rate is not None else None,
            "safety_numbeo_legacy": round(safety_val_numbeo_legacy, 1) if safety_val_numbeo_legacy is not None else None,
            "healthcare_numbeo_legacy": round(health_val_numbeo_legacy, 1) if health_val_numbeo_legacy is not None else None,
            "pollution": round(pollution_val, 1) if pollution_val is not None else None,
            "traffic": round(traffic_val, 1) if traffic_val is not None else None,
            "unemployment": round(unemp_val, 2) if unemp_val is not None else None,
            "gdpGrowth": round(gdp_val, 2) if gdp_val is not None else None,
            "happiness": round(happiness_val, 3) if happiness_val is not None else None,
            "internet": round(internet_val, 2) if internet_val is not None else None,
            "english": english_raw,
            "visa_days": visa_days,
        }
    }

    print(f"[OK] {country_name}: "
          f"safety={results[slug]['safety']} "
          f"(gpi={gpi_score}, "
          f"homicide={homicide_rate}, "
          f"numbeo_legacy={safety_val_numbeo_legacy}), "
          f"health={results[slug]['healthcare']} "
          f"(uhc={uhc_val}, "
          f"numbeo_legacy={health_val_numbeo_legacy}), "
          f"english={results[slug]['english']}, "
          f"visa={results[slug]['visa_days']}, "
          f"tax={results[slug]['tax_system']}, "
          f"nomad={results[slug]['nomad_visa']}")

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
print(f"\nDone. {complete}/{len(results)} countries fully complete.")
print(f"Saved to src/data/quality-scores.json")
print(f"Date: {str(date.today())}")
