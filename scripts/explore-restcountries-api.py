import json
import os

def load_api_key():
    env_path = os.path.join(
        os.path.dirname(__file__), '..', '.env'
    )
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('RESTCOUNTRIES_API_KEY='):
                return line.split('=', 1)[1].strip()
    raise ValueError("API key not found")

import requests

API_KEY = load_api_key()

response = requests.get(
    "https://api.restcountries.com/countries/v5",
    params={"codes.alpha_2": "PT"},
    headers={"Authorization": f"Bearer {API_KEY}"},
    timeout=15
)
response.raise_for_status()
data = response.json()

print(json.dumps(data, indent=2)[:3000])
