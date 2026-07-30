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

def fetch_full_content(link):
    """Haberin detay sayfasına giderek tüm paragraf metinlerini eksiksiz çeker."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(link, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Fotomaç haber detay metninin bulunduğu ana alanlar
            content_div = soup.find('div', class_='news-detail-content') or soup.find('div', class_='news-content') or soup.find('article')
            
            if content_div:
                # Reklamları ve gereksiz etiketleri temizle
                for unwanted in content_div.find_all(['script', 'style', 'iframe', 'ins', 'div'], class_=['social-share', 'related-news', 'ad-container']):
                    unwanted.decompose()
                return str(content_div)
            else:
                # Bulamazsa sayfadaki tüm anlamlı paragrafları topla
                paragraphs = soup.find_all('p')
                full_html = ""
                for p in paragraphs:
                    text = p.get_text().strip()
                    if len(text) > 20 and "devamı için" not in text.lower() and "tıklayınız" not in text.lower():
                        full_html += str(p)
                if full_html:
                    return full_html
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
            
            print(f"Tam metin çekiliyor: {title[:30]}...")
            full_desc = fetch_full_content(link)
            
            # Eğer detay sayfası çekilemezse yedek olarak RSS özetini al ama "Devamı için" kısmını temizle
            if not full_desc:
                full_desc = entry.get('description', '')
                if "Devamı için" in full_desc:
                    full_desc = full_desc.split("Devamı için")[0]

            items.append({
                "title": title.strip(),
                "link": link.strip(),
                "description": full_desc.strip(),
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
        
    print("Haberler tam metin olarak başarıyla 'news.json' dosyasına kaydedildi.")

if __name__ == "__main__":
    main()
