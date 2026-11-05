import httpx
import socket

# Test thamvan.mae.gov.vn
url = "https://thamvan.mae.gov.vn/Home/DSDTM"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'vi,en-US;q=0.9,en;q=0.8',
    'Connection': 'close',
}

try:
    with httpx.Client(verify=False, http2=False, timeout=15.0, headers=headers) as client:
        r = client.get(url)
        print("thamvan DSDTM response:", r.status_code, len(r.text))
except Exception as e:
    print("thamvan DSDTM failed:", type(e), e)

# Test amata domains
domains = [
    "amatavietnam.com",
    "amata.com",
    "amatavn.com",
    "www.amata.com",
    "amata.vn"
]

for d in domains:
    try:
        ip = socket.gethostbyname(d)
        print(f"Domain {d} -> {ip}")
    except Exception as e:
        print(f"Domain {d} -> DNS error: {e}")
