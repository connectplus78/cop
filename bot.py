import json
from datetime import datetime
import feedparser

# Kullanılacak RSS Linkleri
RSS_URLS = {
    "anasayfa": "https://www.ntvspor.net/rss/anasayfa",
    "futbol": "https://www.ntvspor.net/rss/kategori/futbol",
    "dunyadan_futbol": "https://www.ntvspor.net/rss/kategori/dunyadan-futbol",
    "basketbol": "https://www.ntvspor.net/rss/kategori/basketbol",
    "voleybol": "https://www.ntvspor.net/rss/kategori/voleybol",
    "tenis": "https://www.ntvspor.net/rss/kategori/tenis"
}

def extract_image(entry):
    """RSS girdisinden farklı yöntemlerle görsel URL'si bulmaya çalışır."""
    # 1. 'media_content' kontrolü
    if 'media_content' in entry and entry.media_content:
        for media in entry.media_content:
            if 'url' in media:
                return media['url']
                
    # 2. 'enclosures' kontrolü
    if 'enclosures' in entry and entry.enclosures:
        for enc in entry.enclosures:
            if 'href' in enc:
                return enc['href']
                
    # 3. 'summary' veya 'description' içindeki HTML tag'lerini kontrol et (Gelişmiş alternatif eklenebilir)
    return ""

def fetch_rss(url):
    try:
        d = feedparser.parse(url, agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        items = []
        for entry in d.entries:
            title = entry.get('title', '')
            link = entry.get('link', '')
            description = entry.get('description', '')
            pub_date = entry.get('published', entry.get('updated', ''))
            image_url = extract_image(entry)
            
            items.append({
                "title": title.strip(),
                "link": link.strip(),
                "description": description.strip(),
                "image": image_url.strip(),
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
    
    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)
        
    print("Haberler başarıyla 'news.json' dosyasına kaydedildi.")

if __name__ == "__main__":
    main()
