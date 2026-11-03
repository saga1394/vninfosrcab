import httpx
import json

targets = [
    # National Official (16)
    {"id": "baochinhphu", "name": "Báo Chính phủ", "url": "https://baochinhphu.vn/"},
    {"id": "mof", "name": "Bộ Tài chính (MOF)", "url": "https://www.mof.gov.vn/"},
    {"id": "moit", "name": "Bộ Công Thương (MOIT)", "url": "https://moit.gov.vn/"},
    {"id": "moc", "name": "Bộ Xây dựng (MOC)", "url": "https://moc.gov.vn/"},
    {"id": "nso", "name": "Tổng cục Thống kê (NSO)", "url": "https://www.nso.gov.vn/"},
    {"id": "fia", "name": "Cục Đầu tư nước ngoài (FIA)", "url": "https://fia.mof.gov.vn/"},
    {"id": "investvietnam", "name": "InvestVietnam", "url": "https://investvietnam.gov.vn/"},
    {"id": "bocaodientu", "name": "Bố cáo điện tử (DKKD)", "url": "https://bocaodientu.dkkd.gov.vn/egazette/Forms/Egazette/DefaultAnnouncements.aspx"},
    {"id": "dsdtm", "name": "Tham vấn ĐTM (MAE)", "url": "https://thamvan.mae.gov.vn/Home/DSDTM"},
    {"id": "dsgiayphep", "name": "Tham vấn Giấy phép môi trường (MAE)", "url": "https://thamvan.mae.gov.vn/Home/DSGiayPhep"},
    {"id": "mae", "name": "Bộ Nông nghiệp và Môi trường (MAE)", "url": "https://mae.gov.vn/"},
    {"id": "congbao", "name": "Công báo Chính phủ", "url": "https://congbao.chinhphu.vn/"},
    {"id": "vbpl", "name": "Cơ sở dữ liệu quốc gia về VBPL", "url": "https://vbpl.vn/"},
    {"id": "mti_sg", "name": "Singapore MTI/METI", "url": "https://www.mti.gov.sg/"},
    {"id": "enterprisesg", "name": "Enterprise Singapore", "url": "https://www.enterprisesg.gov.sg/"},
    {"id": "acra_bizfile", "name": "Singapore ACRA / Bizfile", "url": "https://www.acra.gov.sg/"},
    
    # Benchmark Parks (7)
    {"id": "vsip", "name": "VSIP Group", "url": "https://www.vsip.com.vn/"},
    {"id": "amata", "name": "Amata Vietnam", "url": "https://amatavietnam.com/"},
    {"id": "becamex", "name": "Becamex IDC", "url": "https://becamex.com.vn/"},
    {"id": "deepc", "name": "DEEP C Industrial Zones", "url": "https://deepc.vn/"},
    {"id": "longhau", "name": "Long Hậu (LHC)", "url": "https://longhau.com.vn/"},
    {"id": "bwindustrial", "name": "BW Industrial Development", "url": "https://bwindustrial.com/"},
    {"id": "wha", "name": "WHA Vietnam", "url": "https://www.whavietnam.com/"},
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'vi,en-US;q=0.9,en;q=0.8',
}

client = httpx.Client(verify=False, follow_redirects=True, timeout=15.0, headers=headers)

results = []
for t in targets:
    try:
        resp = client.get(t["url"])
        print(f"[{t['id']}] {resp.status_code} | URL: {resp.url} | len: {len(resp.content)} | server: {resp.headers.get('server')}")
        results.append({
            "id": t["id"],
            "name": t["name"],
            "target_url": t["url"],
            "final_url": str(resp.url),
            "status": resp.status_code,
            "content_type": resp.headers.get("content-type"),
            "server": resp.headers.get("server"),
            "content_length": len(resp.content),
            "title_sample": ""
        })
    except Exception as e:
        print(f"[{t['id']}] ERROR: {e}")
        results.append({
            "id": t["id"],
            "name": t["name"],
            "target_url": t["url"],
            "final_url": None,
            "status": None,
            "error": str(e)
        })

print(f"\nDone probing {len(targets)} targets.")
