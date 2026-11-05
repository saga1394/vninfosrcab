import sys
import time
import httpx
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PROVINCES = [
    {"id_num": 1, "name_vi": "Hà Nội", "slug": "hanoi", "name_cn": "河内"},
    {"id_num": 2, "name_vi": "Hải Phòng", "slug": "haiphong", "name_cn": "海防"},
    {"id_num": 3, "name_vi": "Bắc Ninh", "slug": "bacninh", "name_cn": "北宁"},
    {"id_num": 4, "name_vi": "Thái Nguyên", "slug": "thainguyen", "name_cn": "太原"},
    {"id_num": 5, "name_vi": "Hưng Yên", "slug": "hungyen", "name_cn": "兴安"},
    {"id_num": 6, "name_vi": "Quảng Ninh", "slug": "quangninh", "name_cn": "广宁"},
    {"id_num": 7, "name_vi": "Phú Thọ", "slug": "phutho", "name_cn": "富寿"},
    {"id_num": 8, "name_vi": "Ninh Bình", "slug": "ninhbinh", "name_cn": "宁平"},
    {"id_num": 9, "name_vi": "TP. Hồ Chí Minh", "slug": "hochiminhcity", "alt_slugs": ["tphcm"], "name_cn": "胡志明市"},
    {"id_num": 10, "name_vi": "Đồng Nai", "slug": "dongnai", "name_cn": "同奈"},
    {"id_num": 11, "name_vi": "Tây Ninh", "slug": "tayninh", "name_cn": "西宁"},
    {"id_num": 12, "name_vi": "Nghệ An", "slug": "nghean", "name_cn": "义安"},
    {"id_num": 13, "name_vi": "Thanh Hóa", "slug": "thanhhoa", "name_cn": "清化"},
    {"id_num": 14, "name_vi": "Đà Nẵng", "slug": "danang", "name_cn": "岘港"},
    {"id_num": 15, "name_vi": "Khánh Hòa", "slug": "khanhhoa", "name_cn": "庆和"},
    {"id_num": 16, "name_vi": "Hà Tĩnh", "slug": "hatinh", "name_cn": "河静"},
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'vi,en-US;q=0.9,en;q=0.8',
}

client = httpx.Client(verify=False, follow_redirects=True, timeout=8.0, headers=HEADERS)

def test_url(url):
    try:
        r = client.get(url)
        # Parse title
        title = ""
        try:
            soup = BeautifulSoup(r.text[:50000], 'html.parser')
            if soup.title and soup.title.string:
                title = soup.title.string.strip()
        except:
            pass
        return {
            "url": str(r.url),
            "status": r.status_code,
            "title": title[:80],
            "bytes": len(r.content),
            "error": None
        }
    except Exception as e:
        err_msg = str(e)
        if "Name or service not known" in err_msg or "getaddrinfo failed" in err_msg or "ConnectError" in err_msg:
            err_type = "DNS/ConnectError"
        elif "Timeout" in err_msg or "timed out" in err_msg:
            err_type = "Timeout"
        elif "SSL" in err_msg or "certificate" in err_msg:
            err_type = "SSLError"
        else:
            err_type = err_msg[:50]
        return {
            "url": url,
            "status": 0,
            "title": "",
            "bytes": 0,
            "error": err_type
        }

def find_working(candidates):
    for u in candidates:
        res = test_url(u)
        if res["status"] in (200, 301, 302, 303, 307, 308) and res["bytes"] > 500:
            return res
        # try http if https failed with connect/ssl
        if u.startswith("https://") and res["status"] == 0 and res["error"] != "DNS/ConnectError":
            u_http = u.replace("https://", "http://")
            res_http = test_url(u_http)
            if res_http["status"] == 200 and res_http["bytes"] > 500:
                return res_http
    return res # return last failed

print("Starting Candidate Domain Discovery...")
for p in PROVINCES:
    slug = p["slug"]
    print(f"\n==================== [{p['id_num']}] {p['name_cn']} ({p['name_vi']}) ====================")
    
    # 1. Portal (A)
    portal_cands = [
        f"https://{slug}.gov.vn",
        f"http://{slug}.gov.vn",
        f"https://www.{slug}.gov.vn",
    ]
    res_a = find_working(portal_cands)
    print(f"  [A-Portal] -> Status: {res_a['status']} | URL: {res_a['url']} | Title: {res_a['title']} | Err: {res_a['error']}")
    
    # 2. Ban Quan ly KCN/KKT (B)
    b_cands = []
    if slug == "hanoi":
        b_cands = ["https://hhtip.hanoi.gov.vn", "https://bqlkcn.hanoi.gov.vn", "https://bqlkcxkcn.hanoi.gov.vn", "https://kcn.hanoi.gov.vn"]
    elif slug == "haiphong":
        b_cands = ["https://heza.gov.vn", "https://bqlkcn.haiphong.gov.vn"]
    elif slug == "bacninh":
        b_cands = ["https://bqlckcn.bacninh.gov.vn", "https://kcn.bacninh.gov.vn", "https://bqlkcn.bacninh.gov.vn"]
    elif slug == "quangninh":
        b_cands = ["https://www.qeza.gov.vn", "https://qeza.gov.vn", "https://bqlkkt.quangninh.gov.vn"]
    elif slug == "ninhbinh":
        b_cands = ["https://iza.ninhbinh.gov.vn", "https://bqlkcn.ninhbinh.gov.vn"]
    elif slug == "hochiminhcity":
        b_cands = ["https://hepza.hochiminhcity.gov.vn", "https://hepza.gov.vn"]
    elif slug == "dongnai":
        b_cands = ["https://dnieza.dongnai.gov.vn/Pages/home.aspx", "https://dnieza.dongnai.gov.vn", "https://diza.vn"]
    elif slug == "nghean":
        b_cands = ["https://dongnam.nghean.gov.vn", "https://bqlkkt.nghean.gov.vn"]
    elif slug == "thanhhoa":
        b_cands = ["https://bqlkktnghison.thanhhoa.gov.vn", "https://kktnghison.thanhhoa.gov.vn", "https://bqlkcn.thanhhoa.gov.vn"]
    elif slug == "danang":
        b_cands = ["https://dseza.danang.gov.vn", "https://bqlkcn.danang.gov.vn", "https://hi-techpark.danang.gov.vn"]
    elif slug == "khanhhoa":
        b_cands = ["https://vanphong.khanhhoa.gov.vn", "https://kktvanphong.khanhhoa.gov.vn", "https://bqlkkt.khanhhoa.gov.vn"]
    elif slug == "hatinh":
        b_cands = ["https://bqlkkt.hatinh.gov.vn", "https://kkt.hatinh.gov.vn", "https://bqlkcn.hatinh.gov.vn"]
    elif slug == "phutho":
        b_cands = ["https://bqlkcn.phutho.gov.vn", "https://kcn.phutho.gov.vn"]
    elif slug == "thainguyen":
        b_cands = ["https://bqlkcn.thainguyen.gov.vn", "https://kcn.thainguyen.gov.vn"]
    elif slug == "hungyen":
        b_cands = ["https://bqlkcn.hungyen.gov.vn", "https://kcn.hungyen.gov.vn"]
    elif slug == "tayninh":
        b_cands = ["https://bqlkkt.tayninh.gov.vn", "https://kkt.tayninh.gov.vn", "https://bqlkcn.tayninh.gov.vn"]
    
    # Generic fallbacks
    b_cands.extend([f"https://bqlkcn.{slug}.gov.vn", f"https://bqlkkt.{slug}.gov.vn", f"https://kcn.{slug}.gov.vn"])
    res_b = find_working(b_cands)
    print(f"  [B-KCN/KKT] -> Status: {res_b['status']} | URL: {res_b['url']} | Title: {res_b['title']} | Err: {res_b['error']}")

    # 3. So Tai chinh (C)
    c_cands = [
        f"https://sotc.{slug}.gov.vn",
        f"https://stc.{slug}.gov.vn",
        f"https://sotaichinh.{slug}.gov.vn",
        f"http://sotc.{slug}.gov.vn",
        f"http://stc.{slug}.gov.vn",
    ]
    if slug == "hochiminhcity":
        c_cands = ["https://sotaichinh.hochiminhcity.gov.vn", "https://stc.tphcm.gov.vn"] + c_cands
    res_c = find_working(c_cands)
    print(f"  [C-TaiChinh] -> Status: {res_c['status']} | URL: {res_c['url']} | Title: {res_c['title']} | Err: {res_c['error']}")

    # 4. So TNMT / NN&MT (D)
    d_cands = [
        f"https://sotnmt.{slug}.gov.vn",
        f"https://stnmt.{slug}.gov.vn",
        f"https://sonnmt.{slug}.gov.vn",
        f"https://snnptnt.{slug}.gov.vn",
        f"http://sotnmt.{slug}.gov.vn",
        f"http://stnmt.{slug}.gov.vn",
    ]
    if slug == "hochiminhcity":
        d_cands = ["https://donre.hochiminhcity.gov.vn", "https://sotnmt.tphcm.gov.vn"] + d_cands
    res_d = find_working(d_cands)
    print(f"  [D-TNMT/NNMT] -> Status: {res_d['status']} | URL: {res_d['url']} | Title: {res_d['title']} | Err: {res_d['error']}")

    # 5. So Xay dung (E)
    e_cands = [
        f"https://soxd.{slug}.gov.vn",
        f"https://sxd.{slug}.gov.vn",
        f"https://soxaydung.{slug}.gov.vn",
        f"http://soxd.{slug}.gov.vn",
        f"http://sxd.{slug}.gov.vn",
    ]
    if slug == "hochiminhcity":
        e_cands = ["https://soxaydung.hochiminhcity.gov.vn", "https://sxd.tphcm.gov.vn"] + e_cands
    res_e = find_working(e_cands)
    print(f"  [E-XayDung] -> Status: {res_e['status']} | URL: {res_e['url']} | Title: {res_e['title']} | Err: {res_e['error']}")

# Standalone: Invest in Thanh Hoa
print("\n==================== [Standalone] Thanh Hóa Investment Promotion Portal ====================")
res_th = find_working(["https://investinthanhhoa.gov.vn", "http://investinthanhhoa.gov.vn"])
print(f"  [Standalone-Invest] -> Status: {res_th['status']} | URL: {res_th['url']} | Title: {res_th['title']} | Err: {res_th['error']}")
