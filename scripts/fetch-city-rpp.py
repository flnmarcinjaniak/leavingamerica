import requests
import json
from datetime import date

API_KEY = "CDA89224-A3F1-4B4A-AD54-05250B523636"

# STEP 1 - Fetch all MSA RPP data
params = {
    "UserID": API_KEY,
    "method": "GetData",
    "datasetname": "Regional",
    "TableName": "MARPP",
    "LineCode": "1",
    "GeoFips": "MSA",
    "Year": "2024",
    "ResultFormat": "json"
}

response = requests.get("https://apps.bea.gov/api/data", params=params, timeout=30)
data = response.json()
print("API Response keys:", data["BEAAPI"]["Results"].keys())
print("Full response:", json.dumps(data["BEAAPI"]["Results"], indent=2)[:500])
try:
    all_msas = data["BEAAPI"]["Results"]["Data"]
except KeyError as e:
    print(f"KeyError: {e}")
    print("Full Results:", json.dumps(data["BEAAPI"]["Results"], indent=2))
    exit(1)
year_used = all_msas[0]["TimePeriod"] if all_msas else "unknown"
print(f"Fetched {len(all_msas)} MSAs for year {year_used}")

# STEP 2 - Define 50 cities with search strings
cities = [
    {"id": "new-york",        "search": "New York-Newark"},
    {"id": "los-angeles",     "search": "Los Angeles-Long Beach-Anaheim"},
    {"id": "chicago",         "search": "Chicago-Naperville"},
    {"id": "houston",         "search": "Houston-Pasadena"},
    {"id": "phoenix",         "search": "Phoenix-Mesa"},
    {"id": "philadelphia",    "search": "Philadelphia-Camden"},
    {"id": "san-antonio",     "search": "San Antonio-New Braunfels"},
    {"id": "san-diego",       "search": "San Diego-Chula Vista"},
    {"id": "dallas",          "search": "Dallas-Fort Worth"},
    {"id": "san-jose",        "search": "San Jose-Sunnyvale"},
    {"id": "austin",          "search": "Austin-Round Rock"},
    {"id": "jacksonville",    "search": "Jacksonville, FL"},
    {"id": "fort-worth",      "search": "Dallas-Fort Worth"},
    {"id": "columbus",        "search": "Columbus, OH"},
    {"id": "charlotte",       "search": "Charlotte-Concord"},
    {"id": "indianapolis",    "search": "Indianapolis-Carmel"},
    {"id": "san-francisco",   "search": "San Francisco-Oakland"},
    {"id": "seattle",         "search": "Seattle-Tacoma"},
    {"id": "denver",          "search": "Denver-Aurora"},
    {"id": "nashville",       "search": "Nashville-Davidson"},
    {"id": "oklahoma-city",   "search": "Oklahoma City, OK"},
    {"id": "el-paso",         "search": "El Paso, TX"},
    {"id": "washington-dc",   "search": "Washington-Arlington"},
    {"id": "boston",          "search": "Boston-Cambridge"},
    {"id": "las-vegas",       "search": "Las Vegas-Henderson"},
    {"id": "memphis",         "search": "Memphis, TN"},
    {"id": "louisville",      "search": "Louisville/Jefferson"},
    {"id": "portland",        "search": "Portland-Vancouver"},
    {"id": "baltimore",       "search": "Baltimore-Columbia"},
    {"id": "milwaukee",       "search": "Milwaukee-Waukesha"},
    {"id": "albuquerque",     "search": "Albuquerque, NM"},
    {"id": "tucson",          "search": "Tucson, AZ"},
    {"id": "fresno",          "search": "Fresno, CA"},
    {"id": "mesa",            "search": "Phoenix-Mesa"},
    {"id": "sacramento",      "search": "Sacramento-Roseville"},
    {"id": "atlanta",         "search": "Atlanta-Sandy Springs"},
    {"id": "kansas-city",     "search": "Kansas City, MO"},
    {"id": "omaha",           "search": "Omaha, NE-IA"},
    {"id": "colorado-springs","search": "Colorado Springs, CO"},
    {"id": "raleigh",         "search": "Raleigh-Cary"},
    {"id": "long-beach",      "search": "Los Angeles-Long Beach-Anaheim"},
    {"id": "virginia-beach",  "search": "Virginia Beach-Chesapeake"},
    {"id": "miami",           "search": "Miami-Fort Lauderdale"},
    {"id": "oakland",         "search": "San Francisco-Oakland"},
    {"id": "minneapolis",     "search": "Minneapolis-St. Paul"},
    {"id": "tampa",           "search": "Tampa-St. Petersburg"},
    {"id": "tulsa",           "search": "Tulsa, OK"},
    {"id": "arlington",       "search": "Dallas-Fort Worth"},
    {"id": "new-orleans",     "search": "New Orleans-Metairie"},
    {"id": "wichita",         "search": "Wichita, KS"},
]

# STEP 3 - Match each city to BEA MSA data
results = {}
not_found = []

for city in cities:
    matched = None
    for msa in all_msas:
        if city["search"] in msa["GeoName"]:
            matched = msa
            break

    if matched:
        rpp = float(matched["DataValue"])
        multiplier = round(rpp / 100, 4)
        results[city["id"]] = multiplier
        print(f"OK  {city['id']}: {matched['GeoName']} -> RPP {rpp} -> {multiplier}")
    else:
        not_found.append(city["id"])
        print(f"NOT FOUND: {city['id']} (searched: {city['search']})")

# STEP 4 - Save to src/data/city-rpp.json
output = {
    "lastUpdated": str(date.today()),
    "dataYear": year_used,
    "source": "U.S. Bureau of Economic Analysis, Regional Price Parities by MSA (MARPP table)",
    "sourceUrl": "https://www.bea.gov/data/prices-inflation/regional-price-parities-state-and-metro-area",
    "note": "RPP index where 100 = US national average. Values above 1.0 mean more expensive than average.",
    "cities": results,
}

with open("src/data/city-rpp.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)

print(f"\nSaved {len(results)} cities to src/data/city-rpp.json")
print(f"Data year: {year_used}")
if not_found:
    print(f"Not found ({len(not_found)}): {', '.join(not_found)}")
