import json
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; "
    "LeavingAmericaBot/1.0; "
    "+https://leavingamerica.co)"
}

response = requests.get(
    "https://getwherenext.com/api/data/index",
    headers=HEADERS,
    timeout=15
)
response.raise_for_status()
data = response.json()

tiers = data.get('tiers', {})
for tier_name, tier_data in tiers.items():
    print(f"\n{'='*60}")
    print(f"TIER: {tier_name}")
    print(f"Description: {tier_data.get('description')}")
    print(f"Count: {tier_data.get('count')}")
    print('='*60)
    for ep in tier_data.get('endpoints', []):
        print(f"\n  PATH: {ep.get('path')}")
        print(f"  DESC: {ep.get('description')}")
        params = ep.get('parameters', [])
        if params:
            print(f"  PARAMS:")
            for p in params:
                print(f"    - {p.get('name')} "
                      f"({'required' if p.get('required') else 'optional'}): "
                      f"{p.get('description')}")
        print(f"  EXAMPLE: {ep.get('exampleUrl')}")

print(f"\n\nTotal endpoints across all tiers: "
      f"{sum(t.get('count', 0) for t in tiers.values())}")
