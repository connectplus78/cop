from datetime import datetime
import json
import xml.etree.ElementTree as ET
import urllib.request

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
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as response:
      xml_data = response.read()
      root = ET.fromstring(xml_data)

      items = []
      for item in root.findall(".//item"):
        title = item.find("title").text if item.find("title") is not None else ""
        link = item.find("link").text if item.find("link") is not None else ""
        pub_date = (
            item.find("pubDate").text if item.find("pubDate") is not None else ""
        )
        description = (
            item.find("description").text
            if item.find("description") is not None
            else ""
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
