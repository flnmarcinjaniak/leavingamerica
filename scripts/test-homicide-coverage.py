import requests

test_countries = {
    "PT": "Portugal",
    "TH": "Thailand",
    "NZ": "New Zealand",
    "GB": "United Kingdom",
    "KE": "Kenya",
}

for iso2, name in test_countries.items():
    url = (f"https://api.worldbank.org/v2/country/{iso2}"
           f"/indicator/VC.IHR.PSRC.P5"
           f"?format=json&mrv=15&per_page=20")
    print(f"\n{'='*50}")
    print(f"Testing {name} ({iso2}) with mrv=15")
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        if len(data) < 2 or not data[1]:
            print(f"  NO DATA AT ALL (even with mrv=15)")
            print(f"  Raw response: {data}")
        else:
            print(f"  Found {len(data[1])} data points:")
            for item in data[1]:
                print(f"    year={item['date']}, "
                      f"value={item['value']}")
    except Exception as e:
        print(f"  ERROR: {e}")

print(f"\n{'='*50}")
print("DIAGNOSIS COMPLETE - no changes made to "
      "the main pipeline")
