import sys
import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import date

# Force UTF-8 output so arrow/checkmark chars print on Windows cp1250 terminals
sys.stdout.reconfigure(encoding="utf-8")

countries = [
    {"id": "portugal",       "numbeo": "Portugal"},
    {"id": "spain",          "numbeo": "Spain"},
    {"id": "mexico",         "numbeo": "Mexico"},
    {"id": "germany",        "numbeo": "Germany"},
    {"id": "italy",          "numbeo": "Italy"},
    {"id": "greece",         "numbeo": "Greece"},
    {"id": "costa-rica",     "numbeo": "Costa Rica"},
    {"id": "panama",         "numbeo": "Panama"},
    {"id": "thailand",       "numbeo": "Thailand"},
    {"id": "malaysia",       "numbeo": "Malaysia"},
    {"id": "indonesia",      "numbeo": "Indonesia"},
    {"id": "colombia",       "numbeo": "Colombia"},
    {"id": "croatia",        "numbeo": "Croatia"},
    {"id": "czech-republic", "numbeo": "Czech Republic"},
    {"id": "poland",         "numbeo": "Poland"},
    {"id": "hungary",        "numbeo": "Hungary"},
    {"id": "romania",        "numbeo": "Romania"},
    {"id": "bulgaria",       "numbeo": "Bulgaria"},
    {"id": "vietnam",        "numbeo": "Vietnam"},
    {"id": "japan",          "numbeo": "Japan"},
    {"id": "south-korea",    "numbeo": "South Korea"},
    {"id": "australia",      "numbeo": "Australia"},
    {"id": "new-zealand",    "numbeo": "New Zealand"},
    {"id": "canada",         "numbeo": "Canada"},
    {"id": "ireland",        "numbeo": "Ireland"},
    {"id": "netherlands",    "numbeo": "Netherlands"},
    {"id": "france",         "numbeo": "France"},
    {"id": "argentina",      "numbeo": "Argentina"},
    {"id": "ecuador",        "numbeo": "Ecuador"},
    {"id": "morocco",        "numbeo": "Morocco"},
]

# Speedtest Global Index 2025 — pre-verified scores (1-10)
internet_scores = {
    "portugal": 7, "spain": 8, "mexico": 5, "germany": 7,
    "italy": 6, "greece": 6, "costa-rica": 6, "panama": 5,
    "thailand": 7, "malaysia": 7, "indonesia": 5, "colombia": 6,
    "croatia": 7, "czech-republic": 8, "poland": 8, "hungary": 8,
    "romania": 9, "bulgaria": 8, "vietnam": 7, "japan": 9,
    "south-korea": 10, "australia": 7, "new-zealand": 7,
    "canada": 8, "ireland": 7, "netherlands": 9, "france": 8,
    "argentina": 6, "ecuador": 5, "morocco": 5,
}

# IQAir World Air Quality Report 2024 — PM2.5 converted to 1-10
air_scores = {
    "portugal": 8, "spain": 7, "mexico": 5, "germany": 7,
    "italy": 6, "greece": 7, "costa-rica": 9, "panama": 8,
    "thailand": 4, "malaysia": 5, "indonesia": 4, "colombia": 6,
    "croatia": 8, "czech-republic": 6, "poland": 5, "hungary": 6,
    "romania": 6, "bulgaria": 6, "vietnam": 4, "japan": 7,
    "south-korea": 5, "australia": 9, "new-zealand": 10,
    "canada": 9, "ireland": 9, "netherlands": 7, "france": 7,
    "argentina": 7, "ecuador": 8, "morocco": 6,
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

DELAY = 4  # seconds between requests — increased to avoid 429s


def extract_index(soup, label):
    """Find a labelled row in a Numbeo results table and return its numeric value."""
    for row in soup.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) >= 2 and label in cells[0].get_text():
            value_text = cells[1].get_text(strip=True)
            numeric = ""
            for ch in value_text:
                if ch.isdigit() or ch == ".":
                    numeric += ch
            if numeric:
                return float(numeric)
    return None


def to_score(value):
    """Convert a Numbeo 0-100 index to a 1-10 score."""
    if value is None:
        return None
    score = round(value / 10)
    return max(1, min(10, score))


def fetch_with_retry(url, retries=3, backoff=10):
    """GET with retry on 429 — waits backoff seconds before retrying."""
    for attempt in range(retries):
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 429:
            wait = backoff * (attempt + 1)
            print(f"  429 rate limit — waiting {wait}s before retry...")
            time.sleep(wait)
            continue
        response.raise_for_status()
        return response
    raise Exception(f"Failed after {retries} retries: {url}")


def fetch_safety(numbeo_name):
    url = (
        "https://www.numbeo.com/crime/country_result.jsp"
        f"?country={numbeo_name.replace(' ', '+')}"
    )
    response = fetch_with_retry(url)
    soup = BeautifulSoup(response.text, "html.parser")
    raw = extract_index(soup, "Safety Index:")
    return raw, to_score(raw)


def fetch_healthcare(numbeo_name):
    url = (
        "https://www.numbeo.com/health-care/country_result.jsp"
        f"?country={numbeo_name.replace(' ', '+')}"
    )
    response = fetch_with_retry(url)
    soup = BeautifulSoup(response.text, "html.parser")
    raw = extract_index(soup, "Health Care Index:")
    return raw, to_score(raw)


def main():
    results = {}
    success_count = 0

    for country in countries:
        cid = country["id"]
        name = country["numbeo"]
        print(f"\nFetching: {name}")

        # Safety
        try:
            raw_safety, safety_score = fetch_safety(name)
            if raw_safety is not None:
                print(f"  Safety Index {raw_safety:.1f} -> {safety_score}/10")
            else:
                print(f"  Safety Index: not found, defaulting to None")
        except Exception as e:
            print(f"  Safety fetch failed: {e}")
            raw_safety, safety_score = None, None

        time.sleep(DELAY)

        # Healthcare
        try:
            raw_health, health_score = fetch_healthcare(name)
            if raw_health is not None:
                print(f"  Healthcare Index {raw_health:.1f} -> {health_score}/10")
            else:
                print(f"  Healthcare Index: not found, defaulting to None")
        except Exception as e:
            print(f"  Healthcare fetch failed: {e}")
            raw_health, health_score = None, None

        time.sleep(DELAY)

        results[cid] = {
            "safety":     safety_score,
            "healthcare": health_score,
            "internet":   internet_scores[cid],
            "air":        air_scores[cid],
        }

        if safety_score is not None and health_score is not None:
            success_count += 1

    output = {
        "lastUpdated": str(date.today()),
        "source": {
            "safety":     "Numbeo Safety Index 2025",
            "healthcare": "Numbeo Health Care Index 2025",
            "internet":   "Speedtest Global Index 2025",
            "air":        "IQAir World Air Quality Report 2024",
        },
        "countries": results,
    }

    out_path = "src/data/quality-scores.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Saved quality scores for {len(results)} countries")
    print(f"     Last updated: {output['lastUpdated']}")
    print("     Source: Numbeo Safety + Healthcare, Speedtest, IQAir")


if __name__ == "__main__":
    main()
