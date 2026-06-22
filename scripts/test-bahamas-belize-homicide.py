import requests

for iso2, name in [("BS", "Bahamas"), ("BZ", "Belize")]:
    url = (f"https://api.worldbank.org/v2/country/{iso2}"
           f"/indicator/VC.IHR.PSRC.P5"
           f"?format=json&mrv=10&per_page=20")
    print(f"\nTesting {name} ({iso2})")
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        if len(data) < 2 or not data[1]:
            print(f"  NO DATA in World Bank for {name}")
        else:
            for item in data[1]:
                print(f"    year={item['date']}, "
                      f"value={item['value']}")
    except Exception as e:
        print(f"  ERROR: {e}")
