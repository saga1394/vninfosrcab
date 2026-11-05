import httpx

client = httpx.Client(verify=False, follow_redirects=True, timeout=20.0)
r1 = client.get("https://moc.gov.vn/vn/Pages/Trangchu.aspx")
print("First call:", r1.status_code)
# Repeat with the same client (reusing cookies)
r2 = client.get("https://moc.gov.vn/vn/Pages/Trangchu.aspx")
print("Second call with same client cookies:", r2.status_code)
print("Client cookies:", dict(client.cookies))
