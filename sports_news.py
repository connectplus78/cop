from datetime import datetime
import json
import feedparser
import requests

RSS_URLS = {
    "Anasayfa": "https://www.ntvspor.net/rss",
    "Futbol": "https://www.ntvspor.net/futbol/rss",
    "Dünyadan Futbol": "https://www.ntvspor.net/dunyadan-futbol/rss",
    "Voleybol": "https://www.ntvspor.net/voleybol/rss",
    "Tenis": "https://www.ntvspor.net/tenis/rss",
    "Basketbol": "https://www.ntvspor.net/basketbol/rss",
}


def fetch_news():
  categories_data = {}

  for cat_name, url in RSS_URLS.items():
    print(f"İşleniyor: {cat_name}")
    feed = feedparser.parse(url)
    items = []

    for entry in feed.entries[:15]:
      link = entry.link
      image_url = None

      try:
        res = requests.get(
            link,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=8,
        )
        if res.status_code == 200:
          from bs4 import BeautifulSoup

          soup = BeautifulSoup(res.content, "html.parser")
          og = soup.find("meta", property="og:image")
          if og and og.get("content"):
            image_url = og["content"]
      except:
        pass

      if not image_url and "summary" in entry:
        from bs4 import BeautifulSoup

        s = BeautifulSoup(entry.summary, "html.parser")
        img = s.find("img")
        if img and img.get("src"):
          image_url = img["src"]

      items.append({
          "title": entry.title,
          "link": link,
          "description": entry.get("summary", ""),
          "image": image_url,
          "pub_date": entry.get("published", datetime.now().isoformat()),
      })

    categories_data[cat_name] = items

  final_output = {
      "updated_at": datetime.now().isoformat(),
      "categories": categories_data,
  }

  with open("spor_haberleri.json", "w", encoding="utf-8") as f:
    json.dump(final_output, f, ensure_ascii=False, indent=4)

  print("Dosya başarıyla güncellendi.")


if __name__ == "__main__":
  fetch_news()
