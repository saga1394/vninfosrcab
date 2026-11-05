import sys
import httpx
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = httpx.Client(verify=False, follow_redirects=True, timeout=8.0, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
})

def probe(url):
    try:
        r = client.get(url)
        title = ""
        try:
            soup = BeautifulSoup(r.text[:50000], 'html.parser')
            if soup.title and soup.title.string:
                title = soup.title.string.strip()
        except:
            pass
        return r.status_code, str(r.url), title[:70], len(r.content), None
    except Exception as e:
        return 0, url, "", 0, str(e)[:50]

targets = {
    "Bac Ninh - D (TNMT)": [
        "https://sotnmt.bacninh.gov.vn",
        "https://sonnmt.bacninh.gov.vn",
        "https://tnmt.bacninh.gov.vn",
        "http://sotnmt.bacninh.gov.vn",
        "https://bacninh.gov.vn/so-tai-nguyen-va-moi-truong",
        "https://bacninh.gov.vn/vi/web/so-tai-nguyen-va-moi-truong"
    ],
    "Quang Ninh - D (TNMT)": [
        "https://www.quangninh.gov.vn/So/sotainguyenmoitruong/Trang/default.aspx",
        "https://www.quangninh.gov.vn/So/sotnmt/Trang/default.aspx",
        "https://sotnmt.quangninh.gov.vn",
        "https://sonnmt.quangninh.gov.vn"
    ],
    "Tay Ninh - D (TNMT)": [
        "https://sotnmt.tayninh.gov.vn",
        "https://sonnmt.tayninh.gov.vn",
        "http://sotnmt.tayninh.gov.vn",
        "https://stnmt.tayninh.gov.vn"
    ],
    "Nghe An - C (Tai Chinh)": [
        "https://sotaichinh.nghean.gov.vn",
        "http://sotaichinh.nghean.gov.vn",
        "https://nghean.gov.vn/so-tai-chinh",
        "https://nghean.gov.vn/portal/folder/sotaichinh"
    ],
    "Nghe An - D (TNMT)": [
        "https://sotnmt.nghean.gov.vn",
        "http://sotnmt.nghean.gov.vn",
        "https://sonnmt.nghean.gov.vn",
        "https://nghean.gov.vn/so-tai-nguyen-va-moi-truong"
    ],
    "Nghe An - E (Xay Dung)": [
        "https://soxaydung.nghean.gov.vn",
        "http://soxaydung.nghean.gov.vn",
        "https://nghean.gov.vn/so-xay-dung"
    ],
    "Thanh Hoa - B (KCN/KKT)": [
        "https://bqlkktnghison.thanhhoa.gov.vn",
        "http://bqlkktnghison.thanhhoa.gov.vn",
        "https://kktnghison.thanhhoa.gov.vn",
        "https://bqlkcn.thanhhoa.gov.vn",
        "https://bqlkkt.thanhhoa.gov.vn"
    ],
    "Thanh Hoa - D (TNMT)": [
        "https://stnmt.thanhhoa.gov.vn",
        "http://stnmt.thanhhoa.gov.vn",
        "https://sotnmt.thanhhoa.gov.vn",
        "https://sonnmt.thanhhoa.gov.vn"
    ],
    "Da Nang - C (Tai Chinh)": [
        "https://sotaichinh.danang.gov.vn",
        "http://sotaichinh.danang.gov.vn",
        "https://danang.gov.vn/chinh-quyen/chi-tiet?id=38&_details_WAR_danangportlet_INSTANCE_Xwz2x9p8E8vY_viewMode=view"
    ],
    "Da Nang - D (TNMT)": [
        "https://sotnmt.danang.gov.vn",
        "http://sotnmt.danang.gov.vn",
        "https://sonnmt.danang.gov.vn"
    ],
    "Khanh Hoa - D (TNMT)": [
        "https://sotnmt.khanhhoa.gov.vn",
        "http://sotnmt.khanhhoa.gov.vn",
        "https://sonnmt.khanhhoa.gov.vn",
        "https://stnmt.khanhhoa.gov.vn"
    ],
    "Ha Tinh - B (KCN/KKT)": [
        "https://bqlkkt.hatinh.gov.vn",
        "http://bqlkkt.hatinh.gov.vn",
        "https://kkt.hatinh.gov.vn",
        "https://kktvungang.hatinh.gov.vn",
        "https://hatinh.gov.vn/ban-quan-ly-khu-kinh-te"
    ]
}

print("Probing unresolved candidates...")
for name, urls in targets.items():
    print(f"\n--- {name} ---")
    found = False
    for u in urls:
        code, final_url, title, length, err = probe(u)
        print(f"  [{code}] {u} -> Length: {length} | Title: {title} | Err: {err}")
        if code == 200 and length > 500:
            found = True
            print(f"  ===> MATCH: {final_url} ({title})")
            break
