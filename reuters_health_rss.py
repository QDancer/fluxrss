import requests
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

# 1) URL de l'API interne Reuters pour la section Healthcare & Pharmaceuticals
API = (
    "https://www.reuters.com/pf/api/v3/content/fetch/articles-by-section?"
    "section=business-healthcare-pharmaceuticals&limit=20"
)

# 2) Récupère le JSON
resp = requests.get(API, headers={
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
})
resp.raise_for_status()
data = resp.json()

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
