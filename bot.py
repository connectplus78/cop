import json
import re
import time
import urllib.request
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup


def temiz_metin(html_metin):
  if not html_metin:
    return ""
  temiz = re.sub(r"<[^<]+?>", "", html_metin)
  return temiz.replace("&nbsp;", " ").strip()


def haber_detayini_cek(url):
  try:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
            " like Gecko) Chrome/121.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        ),
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as response:
      html = response.read().decode("utf-8", errors="ignore")

    soup = BeautifulSoup(html, "html.parser")

    # 1. BAŞLIK ÇEKME
    sayfa_basligi = None
    meta_title = soup.find("meta", property="og:title")
    if meta_title and meta_title.get("content"):
      sayfa_basligi = meta_title.get("content").strip()

    # 2. RESİM ÇEKME
    detay_resim = None
    meta_image = soup.find("meta", property="og:image")
    if meta_image and meta_image.get("content"):
      detay_resim = meta_image.get("content")

    # 3. VİDEO VE MEDYA
    videolar_html = ""
    eklenen_videolar = set()
    for iframe in soup.find_all("iframe"):
      src = iframe.get("src", "")
      if src and not any(
          x in src
          for x in [
              "doubleclick",
              "google",
              "adsystem",
              "facebook",
              "twitter",
          ]
      ):
        if src.startswith("//"):
          src = "https:" + src
        elif src.startswith("/"):
          src = "https://www.ntvspor.net" + src
        if src not in eklenen_videolar:
          videolar_html += (
              '<div class="relative w-full overflow-hidden rounded-2xl mb-8'
              ' shadow-lg border border-gray-100" style="padding-top: 56.25%;"><iframe'
              ' class="absolute top-0 left-0 w-full h-full" src="'
              + src
              + '" frameborder="0" allowfullscreen></iframe></div>'
          )
          eklenen_videolar.add(src)

    # 4. TEMİZ METİN (NTV Spor içerik yapısına göre güncellendi)
    metin_html = ""
    # NTV Spor haber detay gövdesi genellikle article veya belirli class'lar içerisindedir
    icerik_alani = soup.find("div", class_=lambda x: x and any(c in x for c in ["news-content", "content-detail", "detail-body", "article-content"])) or soup
    
    for p in icerik_alani.find_all("p"):
      metin = p.get_text(strip=True)
      if len(metin) > 20 and not any(
          x in metin for x in ["NTV Spor", "Abone Ol", "İlgili Haber", "KAYNAK"]
      ):
        metin_html += f"<p class='mb-4'>{metin}</p>"

    tam_icerik = videolar_html + metin_html
    return sayfa_basligi, tam_icerik, detay_resim
  except Exception as e:
    return None, "", None


def ntvspor_haber_cek():
  # NTV Spor Kategori RSS URL'leri
  kategoriler = {
      "Anasayfa": "https://www.ntvspor.net/rss/anasayfa",
      "Futbol": "https://www.ntvspor.net/rss/kategori/futbol",
      "Dünyadan Futbol": "https://www.ntvspor.net/rss/kategori/dunyadan-futbol",
      "Voleybol": "https://www.ntvspor.net/rss/kategori/voleybol",
      "Tenis": "https://www.ntvspor.net/rss/kategori/tenis",
      "Basketbol": "https://www.ntvspor.net/rss/kategori/basketbol"
  }

  tum_haberler = []

  for kategori_adi, url in kategoriler.items():
    print(f"Kategori işleniyor: {kategori_adi}...")
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
        },
    )

    try:
      with urllib.request.urlopen(req, timeout=15) as response:
        xml_data = response.read()
      root = ET.fromstring(xml_data)
    except Exception:
      print(f"{kategori_adi} kategorisine bağlanılamadı, atlanıyor.")
      continue

    items = root.findall(".//item")[:12]

    for item in items:
      try:
        rss_baslik = item.find("title")
        link = item.find("link")
        aciklama = item.find("description")
        pubDate = item.find("pubDate")

        haber_linki = link.text if link is not None and link.text else "#"
        nihai_baslik = (
            rss_baslik.text
            if rss_baslik is not None and rss_baslik.text
            else "Başlıksız"
        )
        uzun_metin = ""
        resim_url = (
            "https://via.placeholder.com/400x220/1a1a2e/6c5ce7?text=Görsel+Yok"
        )

        if haber_linki != "#":
          sayfa_basligi, tam_icerik, detay_resim = haber_detayini_cek(
              haber_linki
          )

          if sayfa_basligi and len(sayfa_basligi) > 5:
            nihai_baslik = sayfa_basligi
          if tam_icerik:
            uzun_metin = tam_icerik
          if detay_resim:
            resim_url = detay_resim

          time.sleep(0.3)

        temiz_ozet = temiz_metin(
            aciklama.text if aciklama is not None and aciklama.text else ""
        )
        if not uzun_metin:
          uzun_metin = f"<p>{temiz_ozet}</p>"

        tum_haberler.append({
            "kategori": kategori_adi,
            "baslik": nihai_baslik,
            "link": haber_linki,
            "aciklama": temiz_ozet,
            "tam_metin": uzun_metin,
            "resim": resim_url,
            "tarih": (
                pubDate.text if pubDate is not None and pubDate.text else ""
            ),
        })
      except Exception:
        continue

  with open("ntvspor_haberler.json", "w", encoding="utf-8") as f:
    json.dump(tum_haberler, f, ensure_ascii=False, indent=4)

  print(f"Toplam {len(tum_haberler)} adet NTV Spor haberi başarıyla çekildi.")


if __name__ == "__main__":
  ntvspor_haber_cek()
