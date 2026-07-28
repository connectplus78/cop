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


def haber_gorselini_bul(haber_url):
  try:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
            " like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }
    response = requests.get(haber_url, headers=headers, timeout=10)
    if response.status_code == 200:
      soup = BeautifulSoup(response.content, "html.parser")
      og_image = soup.find("meta", property="og:image")
      if og_image and og_image.get("content"):
        return og_image["content"]
  except Exception as e:
    print(f"Görsel alınamadı ({haber_url}): {e}")
  return None


def rss_verilerini_guncelle():
  tum_kategoriler = {}

  for kategori, url in RSS_URLS.items():
    print(f"{kategori} kategorisi işleniyor...")
    feed = feedparser.parse(url)
    kategori_haberleri = []

    for entry in feed.entries[:15]:
      haber_url = entry.link
      gorsel = haber_gorselini_bul(haber_url)

      if not gorsel and "summary" in entry:
        soup_desc = BeautifulSoup(entry.summary, "html.parser")
        img_tag = soup_desc.find("img")
        if img_tag and img_tag.get("src"):
          gorsel = img_tag["src"]

      pub_date = entry.get("published", datetime.now().isoformat())

      haber_objesi = {
          "title": entry.title,
          "link": haber_url,
          "description": entry.get("summary", ""),
          "image": gorsel,
          "pub_date": pub_date,
      }
      kategori_haberleri.append(haber_objesi)

    tum_kategoriler[kategori] = kategori_haberleri

  # SÖZLÜK YAPISI KESİNLİKLE İNGİLİZCE OLARAK TANIMLANDI
  veri = {"updated_at": datetime.now().isoformat(), "categories": tum_kategoriler}

  dosya_adi = "spor_haberleri.json"
  with open(dosya_adi, "w", encoding="utf-8") as f:
    json.dump(veri, f, ensure_ascii=False, indent=4)

  print(f"{dosya_adi} başarıyla İngilizce anahtarlarla güncellendi!")


if __name__ == "__main__":
  rss_verilerini_guncelle()
