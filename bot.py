import json
from datetime import datetime
import feedparser

# Güncellenmiş Fotomaç RSS Linkleri
RSS_URLS = {
    "anasayfa": "https://www.fotomac.com.tr/rss/anasayfa.xml",
    "basketbol": "https://www.fotomac.com.tr/rss/basketbol.xml",
    "son24saat": "https://www.fotomac.com.tr/rss/son24saat.xml",
    "superlig": "https://www.fotomac.com.tr/rss/superlig.xml",
    "galatasaray": "https://www.fotomac.com.tr/rss/galatasaray.xml",
    "fenerbahce": "https://www.fotomac.com.tr/rss/fenerbahce.xml",
    "besiktas": "https://www.fotomac.com.tr/rss/besiktas.xml"
}

def extract_image(entry):
    """RSS girdisinden (Fotomaç formatına uygun şekilde) görsel URL'sini yakalar."""
    
    # 1. 'enclosure' etiketini kontrol et
    if 'enclosures' in entry and entry.enclosures:
        for enc in entry.enclosures:
            if 'href' in enc:
                return enc['href']
            elif 'url' in enc:
                return enc['url']
                
    # 2. 'media_content' etiketini kontrol et
    if 'media_content' in entry and entry.media_content:
        for media in entry.media_content:
            if 'url' in media:
                return media['url']
                
    # 3. 'media_thumbnail' etiketini kontrol et
    if 'media_thumbnail' in entry and entry.media_thumbnail:
        for thumb in entry.media_thumbnail:
            if 'url' in thumb:
                return thumb['url']
                
    return ""

def fetch_rss(url):
    try:
        # Bot engellerini aşmak için User-Agent ekliyoruz
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
    
    # Verileri dosyaya kaydet
    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)
        
    print("Haberler başarıyla 'news.json' dosyasına kaydedildi.")

if __name__ == "__main__":
    main()
