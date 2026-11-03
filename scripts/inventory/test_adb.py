import httpx
from bs4 import BeautifulSoup

client = httpx.Client(verify=False, follow_redirects=True, timeout=10)
for ua in [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Googlebot/2.1 (+http://www.google.com/bot.html)',
    'curl/8.4.0'
]:
    for u in [
        "https://www.adb.org/where-we-work/viet-nam/projects-results",
        "https://www.adb.org/countries/viet-nam/main",
        "https://www.adb.org/rss/news"
    ]:
        try:
            r = client.get(u, headers={'User-Agent': ua})
            print(f"ADB {u[:35]} with {ua[:15]}: {r.status_code} server={r.headers.get('Server')}")
            if r.status_code == 200:
                print(" -> Success!", len(r.content))
                break
        except Exception as e:
            print(f"ADB error: {e}")
