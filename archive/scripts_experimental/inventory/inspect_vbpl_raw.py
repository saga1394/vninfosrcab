import httpx

client = httpx.Client(verify=False, follow_redirects=True, timeout=20.0, headers={'User-Agent': 'Mozilla/5.0'})
r_vbpl = client.get("https://vbpl.vn/")
print("=== VBPL RAW HTML (First 1000 chars) ===")
print(r_vbpl.text[:1000])

r_vbpl_moj = client.get("https://vbpl.moj.gov.vn/")
print("\n=== VBPL MOJ RAW HTML (First 1000 chars) ===")
print(r_vbpl_moj.text[:1000])
