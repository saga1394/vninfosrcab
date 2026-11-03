import sys
import httpx
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = httpx.Client(verify=False, follow_redirects=True, timeout=10.0, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'vi,en-US;q=0.9,en;q=0.8',
})

def extract_samples_from_html(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    samples = []
    seen_urls = set()

    # Strategy 1: Check RSS links first
    rss_link = soup.find('link', type=lambda t: t and ('rss' in t.lower() or 'xml' in t.lower()))
    
    # Strategy 2: Look for article / item containers
    # Common classes in VN government portals:
    # .item, .news-item, .article, .list-news, .post, .tin-tuc, .media
    # Or table rows
    candidates = soup.find_all(['div', 'li', 'article', 'tr'], class_=lambda c: c and any(k in str(c).lower() for k in [
        'item', 'news', 'article', 'post', 'tin-tuc', 'media', 'view-content', 'entry', 'row-fluid'
    ]))
    
    for cand in candidates:
        a_tag = cand.find('a', href=True)
        if not a_tag:
            continue
        title = a_tag.get_text(strip=True)
        if not title or len(title) < 18 or len(title) > 300:
            # Check if there is an h2/h3/h4 with text
            h = cand.find(['h2', 'h3', 'h4', 'h5'])
            if h and len(h.get_text(strip=True)) >= 18:
                title = h.get_text(strip=True)
            else:
                continue
        
        href = a_tag['href']
        if href.startswith('#') or href.startswith('javascript:'):
            continue
        full_url = urljoin(base_url, href)
        if full_url in seen_urls:
            continue
            
        # Try to find date
        date_str = ""
        # Look for time tag or elements with date class
        time_tag = cand.find(['time', 'span', 'small', 'p', 'div'], class_=lambda c: c and any(k in str(c).lower() for k in ['date', 'time', 'ngay', 'created']))
        if time_tag:
            m = re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', time_tag.get_text())
            if m:
                date_str = m.group(0)
        if not date_str:
            m = re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{4}', cand.get_text())
            if m:
                date_str = m.group(0)
                
        # Try to find snippet
        snippet = ""
        desc = cand.find(['p', 'div', 'span'], class_=lambda c: c and any(k in str(c).lower() for k in ['summary', 'desc', 'lead', 'sapo', 'tom-tat', 'intro']))
        if desc:
            snippet = desc.get_text(strip=True)
        if not snippet:
            # use cand text minus title and date
            cand_text = cand.get_text(" ", strip=True)
            if title in cand_text:
                cand_text = cand_text.replace(title, "").strip()
            if date_str in cand_text:
                cand_text = cand_text.replace(date_str, "").strip()
            if len(cand_text) > 20:
                snippet = cand_text[:200]
                
        seen_urls.add(full_url)
        samples.append({
            "title": title,
            "pub_date": date_str,
            "snippet": snippet[:250],
            "url": full_url
        })
        if len(samples) >= 5:
            break
            
    # Fallback: if candidates didn't yield >= 3 samples, look for any substantial <a> tags
    if len(samples) < 3:
        for a in soup.find_all('a', href=True):
            t = a.get_text(strip=True)
            if len(t) > 25 and not any(k in t.lower() for k in ['bản quyền', 'điều khoản', 'liên hệ', 'sơ đồ']):
                href = a['href']
                if href.startswith('#') or href.startswith('javascript:'):
                    continue
                full_url = urljoin(base_url, href)
                if full_url in seen_urls:
                    continue
                seen_urls.add(full_url)
                samples.append({
                    "title": t,
                    "pub_date": "",
                    "snippet": "",
                    "url": full_url
                })
                if len(samples) >= 5:
                    break

    return samples

# Test on 8 diverse sites
test_urls = [
    ("Hà Nội Portal", "https://hanoi.gov.vn"),
    ("Hà Nội KCN", "https://hhtip.hanoi.gov.vn"),
    ("Hải Phòng HEZA", "https://heza.gov.vn"),
    ("Hải Phòng XD", "https://soxd.haiphong.gov.vn"),
    ("Thái Nguyên Portal", "https://thainguyen.gov.vn"),
    ("Quảng Ninh QEZA", "https://www.qeza.gov.vn"),
    ("Đà Nẵng DSEZA", "https://dseza.danang.gov.vn"),
    ("Thanh Hóa Nghi Sơn", "https://nghison.thanhhoa.gov.vn/vi/portal/pages/default.aspx"),
    ("Invest in Thanh Hóa", "https://investinthanhhoa.gov.vn/vi/"),
]

for name, u in test_urls:
    try:
        r = client.get(u)
        samples = extract_samples_from_html(r.text, str(r.url))
        print(f"\n=== {name} ({u}) -> Status: {r.status_code} | Samples extracted: {len(samples)} ===")
        for i, s in enumerate(samples[:3], 1):
            print(f"  [{i}] {s['title'][:60]} | Date: {s['pub_date']} | URL: {s['url']}")
    except Exception as e:
        print(f"\n=== {name} ERR: {e} ===")
