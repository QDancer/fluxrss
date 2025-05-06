import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

# 1. URL de la page d’archives voulue
ARCHIVE_URL = "https://www.medscape.com/index/list_13470_0"

# 2. Récupération et parsing
resp = requests.get(ARCHIVE_URL)
resp.raise_for_status()
soup = BeautifulSoup(resp.content, "html.parser")

# 3. Sélection des éléments <li> dans #archives
items = soup.select("#archives ul li")
print(f"DEBUG: {len(items)} items trouvés")  # doit être > 0

# 4. Configuration du flux RSS
fg = FeedGenerator()
fg.title("Medscape – Archives Health News")
fg.link(href=ARCHIVE_URL, rel="alternate")
fg.description("Flux personnalisé des archives Medscape Health News")

# 5. Boucle sur chaque item
for li in items:
    # a) Titre & lien
    a = li.select_one("a.title")
    if not a:
        continue
    title = a.get_text(strip=True)
    href  = a["href"]
    if href.startswith("//"):
        href = "https:" + href
    elif href.startswith("/"):
        href = "https://www.medscape.com" + href

    # b) Résumé
    teaser_tag = li.select_one("span.teaser")
    summary = teaser_tag.get_text(strip=True) if teaser_tag else ""

    # c) Source & date
    byline = li.select_one("div.byline")
    source = ""
    pub_date = None
    if byline:
        # ex. "Medscape Medical News, May 06, 2025"
        parts = [p.strip() for p in byline.get_text(" ", strip=True).split(",")]
        source = parts[0]  # "Medscape Medical News"
        if len(parts) >= 3:
            # reconstitue "May 06 2025"
            raw_date = f"{parts[1]} {parts[2]}"
            # parse en datetime aware UTC
            pub_date = datetime.strptime(raw_date, "%b %d %Y").replace(tzinfo=timezone.utc)

    # d) Création de l’entrée RSS
    entry = fg.add_entry()
    entry.title(title)
    entry.link(href=href)
    entry.description(f"{summary} (<em>{source}</em>, {raw_date if pub_date else ''})")
    if pub_date:
        entry.pubDate(pub_date)

# 6. Écriture du fichier RSS
output = "medscape_archives.xml"
fg.rss_file(output)
print(f"✅ Flux RSS généré : {output}")
