import httpx
from bs4 import BeautifulSoup

r = httpx.get('http://www.vietnamtextile.org.vn/', verify=False, timeout=10)
soup = BeautifulSoup(r.text, 'html.parser')
links = soup.find_all('a', href=True)
vitas_articles = []
for a in links:
    h = a['href']
    t = a.get_text(strip=True)
    if '_p1_' in h and len(t) > 15 and not any(t == item['title'] for item in vitas_articles):
        full_url = "http://www.vietnamtextile.org.vn/" + h.lstrip('/')
        vitas_articles.append({"title": t, "url": full_url})

print("VITAS articles found:", len(vitas_articles))
for item in vitas_articles[:5]:
    print(f" - {item['title'][:60]} | {item['url']}")
