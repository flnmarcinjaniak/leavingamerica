import requests
from bs4 import BeautifulSoup
import sys
sys.stdout.reconfigure(encoding='utf-8')

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

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

ALL_SLUGS = set(WIKIPEDIA_NAMES.values())

def fetch_internet_wikipedia():
    url = ("https://en.wikipedia.org/wiki/"
           "List_of_countries_by_Internet_connection_speeds")
    print(f"Fetching: {url}")
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    results = {}
    tables = soup.find_all('table', {'class': 'wikitable'})
    if tables:
        tables = [tables[0]]
    print(f"Found {len(tables)} wikitable(s) on page")
    for table in tables:
        for row in table.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) < 2:
                continue
            country_cell = cols[0]
            link = country_cell.find('a')
            if link:
                country_name = link.get_text(strip=True)
            else:
                country_name = country_cell.get_text(strip=True)
            country_name = country_name.strip()
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
                print(f"  FOUND  {slug}: {speed_val} Mbps ({country_name})")
            elif speed_val and country_name:
                pass
    return results

results = fetch_internet_wikipedia()

print(f"\n=== SUMMARY ===")
print(f"Found {len(results)}/30 countries\n")

print("--- FOUND ---")
for slug, speed in sorted(results.items()):
    print(f"  {slug}: {speed} Mbps")

print("\n--- NOT FOUND ---")
not_found = ALL_SLUGS - set(results.keys())
for slug in sorted(not_found):
    print(f"  {slug}")
