import json
from datetime import datetime
import feedparser
import requests
from bs4 import BeautifulSoup

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
    if 'enclosures' in entry and entry.enclosures:
        for enc in entry.enclosures:
            if 'href' in enc: return enc['href']
            elif 'url' in enc: return enc['url']
    if 'media_content' in entry and entry.media_content:
        for media in entry.media_content:
            if 'url' in media: return media['url']
    if 'media_thumbnail' in entry and entry.media_thumbnail:
        for thumb in entry.media_thumbnail:
            if 'url' in thumb: return thumb['url']
    return ""

def fetch_rss(url):
    try:
        d = feedparser.parse(url, agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        items = []
        for entry in d.entries:
            title = entry.get('title', '')
            link = entry.get('link', '')
            pub_date = entry.get('published', entry.get('updated', ''))
            image_url = extract_image(entry)
            
            # Doğrudan RSS description'ı alıyoruz
            desc = entry.get('description', '')
            
            # "Devamı için" veya "tıklayınız" ifadelerini ve sonrasını metinden tamamen siliyoruz
            if "Devamı için" in desc:
                desc = desc.split("Devamı için")[0]
            if "tıklayınız" in desc.lower():
                # Tıklayınız kelimesinin geçtiği cümleyi temizle
                parts = desc.split('.')
                clean_parts = [p for p in parts if "tıklayınız" not in p.lower()]
                desc = ".".join(clean_parts) + ("." if clean_parts else "")

            items.append({
                "title": title.strip(),
                "link": link.strip(),
                "description": desc.strip(),
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
        all_news[category] = fetch_rss(url)
        
    output_data = {
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "categories": all_news
    }
    
    with open("news.json", "w", encoding="text/html" if False else "utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)
        
    print("Haberler güncellendi.")

if __name__ == "__main__":
    main()
