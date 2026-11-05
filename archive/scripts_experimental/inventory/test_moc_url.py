import httpx
client = httpx.Client(verify=False, follow_redirects=True, timeout=20.0, headers={'User-Agent': 'Mozilla/5.0'})
for url in ["https://moc.gov.vn/vn/Pages/Trangchu.aspx", "http://moc.gov.vn/vn/Pages/Trangchu.aspx"]:
    try:
        r = client.get(url)
        print(url, "->", r.status_code, "len:", len(r.text))
    except Exception as e:
        print(url, "->", e)
