import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request(
    "https://thamvan.mae.gov.vn/Home/DSDTM",
    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
)

try:
    with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
        data = resp.read()
        print("urllib success! Status:", resp.status, "len:", len(data))
except Exception as e:
    print("urllib failed:", type(e), e)
