import socket
import ssl
import httpx

# 1. Check DNS for thamvan.mae.gov.vn
try:
    ip = socket.gethostbyname("thamvan.mae.gov.vn")
    print("thamvan.mae.gov.vn IP:", ip)
except Exception as e:
    print("DNS error thamvan:", e)

# 2. Check HTTP vs HTTPS for thamvan
for scheme in ["http", "https"]:
    try:
        url = f"{scheme}://thamvan.mae.gov.vn/Home/DSDTM"
        with httpx.Client(verify=False, timeout=10.0) as client:
            r = client.get(url)
            print(f"{scheme} -> status {r.status_code}, len {len(r.text)}")
    except Exception as e:
        print(f"{scheme} -> error {type(e)}: {e}")

# 3. Check Amata domains
for dom in ["https://www.amata.com", "https://amatavn.com", "http://amatavn.com", "https://amata.vn"]:
    try:
        with httpx.Client(verify=False, timeout=10.0, follow_redirects=True) as client:
            r = client.get(dom)
            print(f"{dom} -> status {r.status_code}, url {r.url}, len {len(r.text)}")
    except Exception as e:
        print(f"{dom} -> error {type(e)}: {e}")
