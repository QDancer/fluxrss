import requests
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

# 1) URL de l'API interne Reuters pour la section Healthcare & Pharmaceuticals
API = (
    "https://www.reuters.com/pf/api/v3/content/fetch/articles-by-section?"
    "section=business-healthcare-pharmaceuticals&limit=20"
)

# 2) Récupère le JSON
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/90.0.4430.93 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.reuters.com/business/healthcare-pharmaceuticals/"
}

try:
    resp = requests.get(API, headers=headers, timeout=15)
    resp.raise_for_status()
    data = resp.json()
except requests.exceptions.RequestException as e:
    print(f"⚠️ Impossible d’appeler l’API Reuters: {e}")
    data = {"result": []}


# 3) Prépare le flux
fg = FeedGenerator()
fg.title("Reuters – Healthcare & Pharmaceuticals")
fg.link(href=API, rel="alternate")
fg.description("Breaking news on healthcare & pharma from Reuters")
fg.lastBuildDate(datetime.now(timezone.utc))

# 4) Parcourt les articles JSON
for art in data.get("result", []):
    # chaque item a "url", "title", "published_time"
    url = art.get("url")
    if url and url.startswith("/"):
        url = "https://www.reuters.com" + url
    title = art.get("title")
    dt = art.get("published_time")  # ex. "2025-05-06T10:08:10Z"

    entry = fg.add_entry()
    entry.title(title or "No title")
    entry.link(href=url or API)
    entry.description(art.get("summary") or "")
    if dt:
        # parse l’ISO +Z
        entry.pubDate(datetime.fromisoformat(dt.replace("Z", "+00:00")))

# 5) Écrit toujours dans /docs
out = "docs/reuters_healthcare_pharma.xml"
fg.rss_file(out)
print(f"✅ Flux généré : {out}")
