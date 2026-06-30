# NOTE: Run this ONLY after the site is live at https://leavingamerica.co
# Pinging IndexNow before the site is live will waste the key verification
# and may cause errors. Run manually after each deploy where content changes
# significantly.
#
# Usage: python scripts/ping-indexnow.py

import json
import urllib.request
import xml.etree.ElementTree as ET

KEY  = "mdUr9u7l1tM3xpvY0qFGaebAcDn8ByIP"
HOST = "leavingamerica.co"
SITEMAP_PATH = "dist/sitemap-0.xml"
INDEXNOW_ENDPOINT = "https://api.indexnow.org/indexnow"

def read_urls_from_sitemap(path):
    tree = ET.parse(path)
    root = tree.getroot()
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [loc.text.strip() for loc in root.findall(".//sm:loc", ns) if loc.text]
    return urls

def ping_indexnow(urls):
    payload = json.dumps({
        "host": HOST,
        "key": KEY,
        "keyLocation": f"https://{HOST}/{KEY}.txt",
        "urlList": urls,
    }).encode("utf-8")

    req = urllib.request.Request(
        INDEXNOW_ENDPOINT,
        data=payload,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "leavingamerica-indexnow/1.0",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as response:
            status = response.status
            body = response.read().decode("utf-8", errors="replace")
            return status, body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return e.code, body

def main():
    print(f"Reading sitemap: {SITEMAP_PATH}")
    try:
        urls = read_urls_from_sitemap(SITEMAP_PATH)
    except FileNotFoundError:
        print(f"ERROR: {SITEMAP_PATH} not found. Run 'npm run build' first.")
        return

    print(f"Found {len(urls)} URLs in sitemap.")
    print(f"Pinging IndexNow ({INDEXNOW_ENDPOINT})...")

    status, body = ping_indexnow(urls)

    if status == 200:
        print(f"SUCCESS ({status}): All {len(urls)} URLs submitted.")
    elif status == 202:
        print(f"ACCEPTED ({status}): URLs queued for processing.")
    elif status == 400:
        print(f"ERROR ({status}): Bad request — check payload format.")
    elif status == 403:
        print(f"ERROR ({status}): Key not found at https://{HOST}/{KEY}.txt — is the site live?")
    elif status == 422:
        print(f"ERROR ({status}): URLs don't match host '{HOST}' or key is invalid.")
    elif status == 429:
        print(f"ERROR ({status}): Too many requests — wait before retrying.")
    else:
        print(f"UNEXPECTED STATUS ({status}): {body}")

if __name__ == "__main__":
    main()
