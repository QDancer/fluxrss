import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

URL = "https://www.reuters.com/business/healthcare-pharmaceuticals/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/90.0.4430.93 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.reuters.com/",
}

try:
    resp = requests.get(URL, headers=headers, timeout=15)
    resp.raise_for_status()
except requests.exceptions.RequestException as e:
    print(f"⚠️ Impossible de récupérer la page Reuters: {e}")
    # On sort sans planter le workflow
    exit(0)

soup = BeautifulSoup(resp.content, "html.parser")

resp.raise_for_status()
soup = BeautifulSoup(resp.content, "html.parser")

fg = FeedGenerator()
fg.title("Reuters – Healthcare & Pharmaceuticals")
fg.link(href=URL, rel="alternate")
fg.description("Breaking news on healthcare & pharma from Reuters")

cards = soup.select("ul.static-media-maximizer__cards__1Z1KE li")
for li in cards:
    a = li.select_one("a[data-testid='Title']")
    if not a:
        continue
    href = a["href"]
    if href.startswith("/"):
        href = "https://www.reuters.com" + href
    title = a.get_text(strip=True)

    time_tag = li.select_one("time[datetime]")
    pub_date = None
    if time_tag and time_tag.has_attr("datetime"):
        dt = time_tag["datetime"]
        pub_date = datetime.fromisoformat(dt.replace("Z", "+00:00"))

    entry = fg.add_entry()
    entry.title(title)
    entry.link(href=href)
    entry.description("")      # pas de résumé disponible ici
    if pub_date:
        entry.pubDate(pub_date)

fg.rss_file("docs/reuters_healthcare_pharma.xml")
print("✅ Flux généré : docs/reuters_healthcare_pharma.xml")
