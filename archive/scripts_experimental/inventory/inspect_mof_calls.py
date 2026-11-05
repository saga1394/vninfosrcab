import httpx
import re

client = httpx.Client(verify=False, follow_redirects=True, timeout=20.0, headers={'User-Agent': 'Mozilla/5.0'})
for chunk in ['assets/HomeDefaultViewVi-b_Iu7jgG.js', 'assets/ArticleDefaultView-CpEyiipU.js', 'assets/CategoryDefaultView-BFrlmGg5.js']:
    r = client.get(f"https://www.mof.gov.vn/{chunk}")
    # find api calls like .get("...") or .post("...")
    calls = re.findall(r'\.(?:get|post)\(["\']([^"\']+)["\']', r.text)
    print(f"Calls in {chunk}:", calls)
