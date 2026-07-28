from datetime import datetime
import json
import os
from bs4 import BeautifulSoup
import requests

# Doğrudan NTV Spor kategorilerinin web sayfalarından veri çeken güvenli yapı
KATEGORILER = {
    "Anasayfa": "https://www.ntvspor.net",
    "Futbol": "https://www.ntvspor.net/futbol",
    "Dünyadan Futbol": "https://www.ntvspor.net/dunyadan-futbol",
    "Voleybol": "https://www.ntvspor.net/voleybol",
    "Tenis": "https://www.ntvspor.net/tenis",
    "Basketbol": "https://www.ntvspor.net/basketbol",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
}


def haberleri_cek():
  kategoriler_data = {}

  for kategori, url in KATEGORILER.items():
    print(f"{kategori} taranıyor...")
    kategori_haberleri = []
    try:
      response = requests.get(url, headers=HEADERS, timeout=15)
      if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")

        # Sitedeki haber kartlarını yakalama
        haber_kartlari = soup.find_all("a", href=True)
        islenen_linkler = set()

        for kart in haber_kartlari:
          href = kart["href"]
          # NTV Spor haber detay linklerini filtreleme
          if (
              any(
                  k in href
                  for k in [
                      "/futbol/",
                      "/basketbol/",
                      "/voleybol/",
                      "/tenis/",
                      "/dunyadan-futbol/",
                  ]
              )
              and len(href) > 25
          ):
            haber_url = (
                href
                if href.startswith("http")
                else f"https://www.ntvspor.net{href}"
            )

            if haber_url in islenen_linkler:
              continue
            islenen_linkler.add(haber_url)

            # Başlık bulma
            baslik_tag = kart.find(["h2", "h3", "h4", "span"])
            title = (
                baslik_tag.get_text(strip=True)
                if baslik_tag
                else kart.get_text(strip=True)
            )

            if not title or len(title) < 10:
              continue

            # Görsel bulma
            img_tag = kart.find("img")
            gorsel = None
            if img_tag:
              gorsel = img_tag.get("data-src") or img_tag.get("src")

            haber_objesi = {
                "title": title,
                "link": haber_url,
                "description": "",
                "image": gorsel,
                "pub_date": datetime.now().isoformat(),
            }
            kategori_haberleri.append(haber_objesi)

            if len(kategori_haberleri) >= 15:
              break

      kategoriler_data[kategori] = kategori_haberleri
    except Exception as e:
      print(f"{kategori} çekilirken hata: {e}")
      kategoriler_data[kategori] = []

  veri = {
      "güncellendi": datetime.now().isoformat(),
      "kategoriler": kategoriler_data,
  }

  with open("spor_haberleri.json", "w", encoding="utf-8") as f:
    json.dump(veri, f, ensure_ascii=False, indent=4)

  print("spor_haberleri.json başarıyla dolduruldu!")


if __name__ == "__main__":
  haberleri_cek()
