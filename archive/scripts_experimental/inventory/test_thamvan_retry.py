import httpx
import time

for i in range(3):
    try:
        t0 = time.time()
        print(f"Attempt {i+1} connecting to thamvan.mae.gov.vn...")
        with httpx.Client(verify=False, timeout=25.0) as client:
            r = client.get("https://thamvan.mae.gov.vn/Home/DSDTM")
            print(f"Success! Status: {r.status_code}, time: {round(time.time()-t0, 2)}s, bytes: {len(r.content)}")
            break
    except Exception as e:
        print(f"Attempt {i+1} failed ({round(time.time()-t0, 2)}s): {type(e)} {e}")
        time.sleep(2)
