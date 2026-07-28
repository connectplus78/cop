from datetime import datetime
import json
import os
from bs4 import BeautifulSoup
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

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
}


def rss_verilerini_guncelle():
  kategoriler_data = {}

  for kategori, url in RSS_URLS.items():
    print(f"{kategori} kategorisi işleniyor...")
    try:
      # RSS verisini özel başlıklarla çekiyoruz
      response = requests.get(url, headers=HEADERS, timeout=15)
      feed = feedparser.parse(response.content)
      kategori_haberleri = []

      for entry in feed.entries[:15]:
        haber_url = entry.link
        gorsel = None

        # Haber detayından görsel bulma
        try:
          detay_res = requests.get(haber_url, headers=HEADERS, timeout=10)
          if detay_res.status_code == 200:
            soup = BeautifulSoup(detay_res.content, "html.parser")
            og_image = soup.find("meta", property="og:image")
            if og_image and og_image.get("content"):
              gorsel = og_image["content"]
        except:
          pass

        # Alternatif olarak özetten görsel bulma
        if not gorsel and "summary" in entry:
          soup_desc = BeautifulSoup(entry.summary, "html.parser")
          img_tag = soup_desc.find("img")
          if img_tag and img_tag.get("src"):
            gorsel = img_tag["src"]

        haber_objesi = {
            "title": entry.title,
            "link": haber_url,
            "description": entry.get("summary", ""),
            "image": gorsel,
            "pub_date": entry.get("published", datetime.now().isoformat()),
        }
        kategori_haberleri.append(haber_objesi)

      kategoriler_data[kategori] = kategori_haberleri
    except Exception as e:
      print(f"{kategori} çekilirken hata oluştu: {e}")
      kategoriler_data[kategori] = []

  veri = {
      "güncellendi": datetime.now().isoformat(),
      "kategoriler": kategoriler_data,
  }

  with open("spor_haberleri.json", "w", encoding="utf-8") as f:
    json.dump(veri, f, ensure_ascii=False, indent=4)

  print("spor_haberleri.json başarıyla dolduruldu ve güncellendi!")


if __name__ == "__main__":
  rss_verilerini_guncelle()
