"""
Fetches fresh PPP values from World Bank and updates STATIC_PPP in src/pages/index.astro.
Run quarterly alongside fetch-quality-scores.py.

Usage:
    python scripts/fetch-ppp-embed.py
"""

import urllib.request
import json
import re
import sys
from datetime import date

ASTRO_FILE = "src/pages/index.astro"

# All 82 country ISO2 codes (must match COUNTRY_CURRENCIES in index.astro)
CODES = [
    "PT","ES","PL","MX","TH","DE","JP","HR","CZ","HU","RO","BG","VN","KR",
    "AU","NZ","CA","IE","NL","FR","AR","EC","MA","CH","NO","DK","SE","BE",
    "AT","FI","GB","SG","AE","QA","SA","IS","IN","PH","CN","GE","RS","KE",
    "PE","BR","CL","AL","LK","EG","ID","CO","CR","PA","MY","IT","GR",
    "BS","BZ","BO","KH","CY","DO","SV","EE","GH","HN","JM","KZ","LV","LT",
    "MT","ME","NP","NI","MK","PY","RW","SK","SI","ZA","TW","TR","UY",
]

# Countries excluded from World Bank (geopolitical) — use hardcoded values
MANUAL_PPP = {
    "TW": 15.0,  # Taiwan: ~15 TWD/intl$ (IMF/OECD estimate)
}


def fetch_ppp(codes):
    batch = ";".join(c for c in codes if c not in MANUAL_PPP)
    url = (
        f"https://api.worldbank.org/v2/country/{batch}"
        f"/indicator/PA.NUS.PRVT.PP?format=json&mrv=5&per_page=500"
    )
    req = urllib.request.Request(
        url, headers={"User-Agent": "LeavingAmericaBot/1.0 (https://leavingamerica.co)"}
    )
    with urllib.request.urlopen(req, timeout=40) as r:
        data = json.loads(r.read())

    results = {}
    best_years = {}
    for item in data[1]:
        if item["value"] is not None:
            iso2 = item["country"]["id"]
            year = int(item["date"])
            if iso2 not in best_years or year > best_years[iso2]:
                results[iso2] = item["value"]
                best_years[iso2] = year

    return results, best_years


def build_js_object(ppp_values, best_years, all_codes):
    today = date.today().isoformat()
    lines = [
        f"    // Static PPP values (World Bank PA.NUS.PRVT.PP, fetched {today})",
        "    // Eliminates runtime WB API calls — update quarterly by running scripts/fetch-ppp-embed.py",
        "    const STATIC_PPP: Record<string, number> = {",
    ]

    # Build in sorted order, 5 per line
    entries = {}
    for code in all_codes:
        if code in ppp_values:
            entries[code] = round(ppp_values[code], 4)
        elif code in MANUAL_PPP:
            entries[code] = MANUAL_PPP[code]

    items = list(entries.items())
    for i in range(0, len(items), 5):
        chunk = items[i : i + 5]
        line = ",".join(f'"{k}":{v}' for k, v in chunk)
        lines.append(f"      {line},")

    lines.append("    };")
    return "\n".join(lines)


def update_astro_file(new_block):
    with open(ASTRO_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(
        r"    // Static PPP values.*?    \};",
        re.DOTALL,
    )
    if not pattern.search(content):
        print("ERROR: Could not find STATIC_PPP block in index.astro.")
        print("Expected a block starting with '// Static PPP values'.")
        sys.exit(1)

    updated = pattern.sub(new_block, content)

    with open(ASTRO_FILE, "w", encoding="utf-8") as f:
        f.write(updated)


def main():
    print("Fetching PPP values from World Bank (mrv=5)...")
    try:
        ppp_values, best_years = fetch_ppp(CODES)
    except Exception as e:
        print(f"ERROR fetching from World Bank: {e}")
        sys.exit(1)

    fetched = len(ppp_values)
    manual = len(MANUAL_PPP)
    total = len(CODES)
    missing = [c for c in CODES if c not in ppp_values and c not in MANUAL_PPP]

    print(f"Fetched: {fetched} from WB, {manual} manual override, total {fetched + manual}/{total}")
    if missing:
        print(f"WARNING — missing PPP for: {missing}")
        print("  These countries will not work in the calculator until added manually.")

    print("\nValues by country:")
    for code in sorted(CODES):
        if code in ppp_values:
            print(f"  {code}: {round(ppp_values[code], 4)} ({best_years[code]})")
        elif code in MANUAL_PPP:
            print(f"  {code}: {MANUAL_PPP[code]} (manual override)")
        else:
            print(f"  {code}: MISSING")

    new_block = build_js_object(ppp_values, best_years, CODES)
    update_astro_file(new_block)
    print(f"\nUpdated STATIC_PPP in {ASTRO_FILE}")
    print("Run 'npm run build' or restart dev server to apply.")


if __name__ == "__main__":
    main()
