from datetime import datetime
import json
import urllib.request
import xml.etree.ElementTree as ET

# NTV Spor RSS adresleri
RSS_URLS = {
    "Anasayfa": "https://www.ntvspor.net/rss/anasayfa",
    "Futbol": "https://www.ntvspor.net/rss/kategori/futbol",
    "Dünyadan Futbol": "https://www.ntvspor.net/rss/kategori/dunyadan-futbol",
    "Voleybol": "https://www.ntvspor.net/rss/kategori/voleybol",
    "Tenis": "https://www.ntvspor.net/rss/kategori/tenis",
    "Basketbol": "https://www.ntvspor.net/rss/kategori/basketbol",
}


def fetch_rss(url):
  try:
    # Gerçek bir tarayıcı gibi görünmek için detaylı header ekledik
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "application/rss+xml, application/xml, text/xml;q=0.9",
        },
    )

    with urllib.request.urlopen(req, timeout=15) as response:
      xml_data = response.read()
      root = ET.fromstring(xml_data)

      items = []
      # RSS yapısındaki channel altındaki item'ları bulur
      for item in root.findall(".//item"):
        title_elem = item.find("title")
        link_elem = item.find("link")
        pub_date_elem = item.find("pubDate")
        desc_elem = item.find("description")

        title = title_elem.text if title_elem is not None and title_elem.text else ""
        link = link_elem.text if link_elem is not None and link_elem.text else ""
        pub_date = (
            pub_date_elem.text
            if pub_date_elem is not None and pub_date_elem.text
            else ""
        )
        description = (
            desc_elem.text if desc_elem is not None and desc_elem.text else ""
        )

        items.append({
            "title": title.strip(),
            "link": link.strip(),
            "pub_date": pub_date.strip(),
            "description": description.strip(),
        })
      return items
  except Exception as e:
    print(f"Hata oluştu ({url}): {e}")
    return []


def main():
  all_data = {}
  for category, url in RSS_URLS.items():
    print(f"Çekiliyor: {category}")
    all_data[category] = fetch_rss(url)

  output = {
      "updated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
      "categories": all_data,
  }

  with open("sports_news.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=4)

  print("Veriler başarıyla sports_news.json dosyasına kaydedildi.")


if __name__ == "__main__":
  main()
