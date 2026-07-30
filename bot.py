import json
from datetime import datetime
import feedparser
import requests
from bs4 import BeautifulSoup

# Fotomaç RSS Linkleri
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
    """RSS girdisinden görsel URL'sini yakalar."""
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

def fetch_full_content(link):
    """Haberin detay sayfasına giderek içeriğin tamamını (tüm paragrafları) çeker."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(link, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Fotomaç içerik alanı
            content_div = soup.find('div', class_='news-content') or soup.find('div', class_='article-body') or soup.find('div', class_='text')
            
            if content_div:
                for unwanted in content_div.find_all(['script', 'style', 'iframe', 'ins']):
                    unwanted.decompose()
                return str(content_div)
            else:
                paragraphs = soup.find_all('p')
                full_text = "".join([str(p) for p in paragraphs if len(p.text.strip()) > 20])
                if full_text:
                    return full_text
        return ""
    except Exception as e:
        print(f"İçerik çekilemedi ({link}): {e}")
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
            
            print(f"Detaylar çekiliyor: {title[:30]}...")
            full_description = fetch_full_content(link)
            
            if not full_description:
                full_description = entry.get('description', '')

            items.append({
                "title": title.strip(),
                "link": link.strip(),
                "description": full_description.strip(),
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
        print(f"Kategori işleniyor: {category}...")
        all_news[category] = fetch_rss(url)
        
    output_data = {
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "categories": all_news
    }
    
    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)
        
    print("Haberler başarıyla 'news.json' dosyasına kaydedildi ve tamamı eklendi.")

if __name__ == "__main__":
    main()
