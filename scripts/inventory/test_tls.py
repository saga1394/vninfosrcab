import ssl
import httpx

# Create custom SSL context with TLS 1.2
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
ctx.set_ciphers('DEFAULT@SECLEVEL=1')

for tls_ver in [ssl.TLSVersion.TLSv1_2, ssl.TLSVersion.TLSv1_3]:
    ctx.maximum_version = tls_ver
    ctx.minimum_version = tls_ver
    try:
        with httpx.Client(verify=ctx, timeout=15.0) as client:
            r = client.get("https://thamvan.mae.gov.vn/Home/DSDTM")
            print(f"TLS ver {tls_ver.name}: Success! {r.status_code}, len={len(r.text)}")
    except Exception as e:
        print(f"TLS ver {tls_ver.name}: Failed: {type(e)} {e}")
