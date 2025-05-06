import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

# URL de la page à scraper
url = "https://nicotinepolicy.net/"
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

# Sélection de tous les articles
articles = soup.select('section.container.shadow-5.border.border-1')

# Création du flux RSS
fg = FeedGenerator()
fg.title("Nicotine Science and Policy")
fg.link(href="https://nicotinepolicy.net/", rel="alternate")
fg.description("Daily digest of views, debates and discussions on nicotine science, policy, regulation and advocacy.")

# Boucle sur chaque article
for section in articles:
    date_tag = section.select_one("p.text-black-50")
    if not date_tag:
        continue
    date_text = date_tag.get_text(strip=True).split(" by ")[0]

    link_tag = section.select_one("h2 a")
    if not link_tag:
        continue
    article_url = link_tag.get("href")
    article_title = link_tag.get_text(strip=True)

    content_tag = section.select_one("div.bodyArticle p")
    summary = content_tag.get_text(strip=True) if content_tag else ""

    entry = fg.add_entry()
    entry.title(article_title)
    entry.link(href=article_url)
    entry.description(f"{summary} (Published on {date_text})")

# Enregistre le fichier RSS
fg.rss_file("docs/nicotinepolicy.xml")
print("✅ Flux RSS généré : nicotinepolicy.xml")
