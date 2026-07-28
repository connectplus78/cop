import json
import xml.etree.ElementTree as ET
import urllib.request
from datetime import datetime

# Kullanılacak RSS Linkleri
RSS_URLS = {
    "anasayfa": "https://www.ntvspor.net/rss/anasayfa",
    "futbol": "https://www.ntvspor.net/rss/kategori/futbol",
    "dunyadan_futbol": "https://www.ntvspor.net/rss/kategori/dunyadan-futbol",
    "basketbol": "https://www.ntvspor.net/rss/kategori/basketbol",
    "voleybol": "https://www.ntvspor.net/rss/kategori/voleybol",
    "tenis": "https://www.ntvspor.net/rss/kategori/tenis"
}

def fetch_rss(url):
    try:
        # Gerçek bir tarayıcı gibi görünmek için detaylı header bilgileri ekliyoruz
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/rss+xml, application/xml, text/xml, */*',
            'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7'
        }
        
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            
            items = []
            channel = root.find('channel')
            if channel is not None:
                for item in channel.findall('item'):
                    title = item.find('title').text if item.find('title') is not None else ""
                    link = item.find('link').text if item.find('link') is not None else ""
                    description = item.find('description').text if item.find('description') is not None else ""
                    pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ""
                    
                    items.append({
                        "title": title.strip(),
                        "link": link.strip(),
                        "description": description.strip(),
                        "pubDate": pub_date.strip()
                    })
            return items
    except Exception as e:
        print(f"Hata oluştu ({url}): {e}")
        return []

def main():
    all_news = {}
    
    for category, url in RSS_URLS.items():
        print(f"Çekiliyor: {category}...")
        all_news[category] = fetch_rss(url)
        
    output_data = {
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "categories": all_news
    }
    
    # Verileri dosyaya kaydet
    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)
        
    print("Haberler başarıyla 'news.json' dosyasına kaydedildi.")

if __name__ == "__main__":
    main()
