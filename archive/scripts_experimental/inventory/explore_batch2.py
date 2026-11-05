"""
Exploratory probe for Batch 2: 55 media sources
Tests connectivity, searches for RSS links, checks sitemaps and headers.
"""

import sys
import time
import json
import re
import httpx
from bs4 import BeautifulSoup
import feedparser

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,application/json,*/*;q=0.8',
    'Accept-Language': 'vi,en-US;q=0.9,en;q=0.8',
}

SOURCES = [
    # 1. 越南全国综合 (12)
    {"id": "src-VN-GEN-01", "name": "VietnamPlus", "url": "https://www.vietnamplus.vn", "rss_candidates": ["https://www.vietnamplus.vn/rss/home.rss", "https://www.vietnamplus.vn/rss/kinhte.rss"]},
    {"id": "src-VN-GEN-02", "name": "Nhân Dân (人民报)", "url": "https://nhandan.vn", "rss_candidates": ["https://nhandan.vn/rss/kinhte-1188.rss", "https://nhandan.vn/rss/home.rss", "https://nhandan.vn/rss"]},
    {"id": "src-VN-GEN-03", "name": "VTV", "url": "https://vtv.vn", "rss_candidates": ["https://vtv.vn/kinh-te.rss", "https://vtv.vn/dong-dong-su-kien.rss", "https://vtv.vn/rss"]},
    {"id": "src-VN-GEN-04", "name": "VOV", "url": "https://vov.vn", "rss_candidates": ["https://vov.vn/rss/kinh-te.rss", "https://vov.vn/rss.vov"]},
    {"id": "src-VN-GEN-05", "name": "SGGP", "url": "https://www.sggp.org.vn", "rss_candidates": ["https://www.sggp.org.vn/rss/kinhte.rss", "https://www.sggp.org.vn/rss/home.rss", "https://www.sggp.org.vn/rss"]},
    {"id": "src-VN-GEN-06", "name": "Vietnam News", "url": "https://vietnamnews.vn", "rss_candidates": ["https://vietnamnews.vn/rss/economy.rss", "https://vietnamnews.vn/rss/business.rss", "https://vietnamnews.vn/rss"]},
    {"id": "src-VN-GEN-07", "name": "VnExpress", "url": "https://vnexpress.net", "rss_candidates": ["https://vnexpress.net/rss/kinh-doanh.rss", "https://vnexpress.net/rss/tin-moi-nhat.rss"]},
    {"id": "src-VN-GEN-08", "name": "Tuổi Trẻ", "url": "https://tuoitre.vn", "rss_candidates": ["https://tuoitre.vn/rss/kinh-doanh.rss", "https://tuoitre.vn/rss/home.rss"]},
    {"id": "src-VN-GEN-09", "name": "Thanh Niên", "url": "https://thanhnien.vn", "rss_candidates": ["https://thanhnien.vn/rss/kinh-te.rss", "https://thanhnien.vn/rss/home.rss"]},
    {"id": "src-VN-GEN-10", "name": "VietnamNet", "url": "https://vietnamnet.vn", "rss_candidates": ["https://vietnamnet.vn/rss/kinh-doanh.rss", "https://vietnamnet.vn/rss/home.rss"]},
    {"id": "src-VN-GEN-11", "name": "Dân Trí", "url": "https://dantri.com.vn", "rss_candidates": ["https://dantri.com.vn/rss/kinh-doanh.rss", "https://dantri.com.vn/rss/home.rss"]},
    {"id": "src-VN-GEN-12", "name": "Znews", "url": "https://znews.vn", "rss_candidates": ["https://znews.vn/rss/kinh-doanh-tai-chinh.rss", "https://znews.vn/rss"]},

    # 2. 越南财经工业 (10)
    {"id": "src-VN-FIN-01", "name": "Báo Đầu tư (投资报)", "url": "https://baodautu.vn", "rss_candidates": ["https://baodautu.vn/rss/dau-tu.rss", "https://baodautu.vn/rss/thoi-su.rss", "https://baodautu.vn/rss"]},
    {"id": "src-VN-FIN-02", "name": "VnEconomy", "url": "https://vneconomy.vn", "rss_candidates": ["https://vneconomy.vn/kinh-te-so.rss", "https://vneconomy.vn/rss.htm", "https://vneconomy.vn/rss"]},
    {"id": "src-VN-FIN-03", "name": "CafeF", "url": "https://cafef.vn", "rss_candidates": ["https://cafef.vn/home.rss", "https://cafef.vn/thi-truong-chung-khoan.rss"]},
    {"id": "src-VN-FIN-04", "name": "Vietstock", "url": "https://vietstock.vn", "rss_candidates": ["https://vietstock.vn/737/doanh-nghiep/hoat-dong-kinh-doanh.rss", "https://vietstock.vn/kinh-te.rss"]},
    {"id": "src-VN-FIN-05", "name": "Công Thương (工贸报)", "url": "https://congthuong.vn", "rss_candidates": ["https://congthuong.vn/rss/cong-nghiep.rss", "https://congthuong.vn/rss/home.rss"]},
    {"id": "src-VN-FIN-06", "name": "The Investor", "url": "https://theinvestor.vn", "rss_candidates": ["https://theinvestor.vn/rss", "https://theinvestor.vn/sitemap.xml"]},
    {"id": "src-VN-FIN-07", "name": "BizHub", "url": "https://bizhub.vietnamnews.vn", "rss_candidates": ["https://bizhub.vietnamnews.vn/rss/corporate.rss", "https://bizhub.vietnamnews.vn/rss"]},
    {"id": "src-VN-FIN-08", "name": "Thời báo Tài chính VN", "url": "https://thoibaotaichinhvietnam.vn", "rss_candidates": ["https://thoibaotaichinhvietnam.vn/rss", "https://thoibaotaichinhvietnam.vn/rss/tai-chinh.rss"]},
    {"id": "src-VN-FIN-09", "name": "CafeLand", "url": "https://cafeland.vn", "rss_candidates": ["https://cafeland.vn/rss/du-an.rss", "https://cafeland.vn/rss", "https://cafeland.vn/rss/thi-truong.rss"]},
    {"id": "src-VN-FIN-10", "name": "Diễn đàn Doanh nghiệp", "url": "https://diendandoanhnghiep.vn", "rss_candidates": ["https://diendandoanhnghiep.vn/rss.html", "https://diendandoanhnghiep.vn/rss/doanh-nghiep-rss.html", "https://diendandoanhnghiep.vn/rss"]},

    # 3. 越南地方报媒 (8)
    {"id": "src-VN-LOC-01", "name": "Báo Hải Phòng", "url": "https://baohaiphong.vn", "rss_candidates": ["https://baohaiphong.vn/rss", "https://baohaiphong.com.vn/rss", "https://baohaiphong.vn/kinh-te/"]},
    {"id": "src-VN-LOC-02", "name": "Báo Bắc Ninh", "url": "https://baobacninh.vn", "rss_candidates": ["https://baobacninh.vn/rss", "https://baobacninh.com.vn/rss", "https://baobacninh.vn/kinh-te/"]},
    {"id": "src-VN-LOC-03", "name": "Báo Hưng Yên", "url": "https://baohungyen.vn", "rss_candidates": ["https://baohungyen.vn/rss", "https://baohungyen.vn/kinh-te/"]},
    {"id": "src-VN-LOC-04", "name": "Báo Thái Nguyên", "url": "https://baothainguyen.vn", "rss_candidates": ["https://baothainguyen.vn/rss", "https://baothainguyen.vn/kinh-te/"]},
    {"id": "src-VN-LOC-05", "name": "Báo Đà Nẵng", "url": "https://baodanang.vn", "rss_candidates": ["https://baodanang.vn/rss", "https://baodanang.vn/channel/5404/"]},
    {"id": "src-VN-LOC-06", "name": "Báo Tây Ninh", "url": "https://baotayninh.vn", "rss_candidates": ["https://baotayninh.vn/rss", "https://baotayninh.vn/kinh-te/"]},
    {"id": "src-VN-LOC-07", "name": "Báo Đồng Nai", "url": "https://baodongnai.com.vn", "rss_candidates": ["https://baodongnai.com.vn/rss", "https://baodongnai.com.vn/kinh-te/"]},
    {"id": "src-VN-LOC-08", "name": "Báo Quảng Ninh", "url": "https://baoquangninh.vn", "rss_candidates": ["https://baoquangninh.vn/rss", "https://baoquangninh.vn/kinh-te/"]},

    # 4. 国际通讯社 (3)
    {"id": "src-INT-WIRE-01", "name": "Reuters", "url": "https://www.reuters.com", "rss_candidates": ["https://www.reutersagency.com/feed/?taxonomy=markets&post_type=reuters_event", "https://www.reuters.com/arc/outboundfeeds/rss/?outputType=xml"]},
    {"id": "src-INT-WIRE-02", "name": "Bloomberg", "url": "https://www.bloomberg.com", "rss_candidates": ["https://www.bloomberg.com/feed/bview.xml", "https://feeds.bloomberg.com/markets/news.rss"]},
    {"id": "src-INT-WIRE-03", "name": "South China Morning Post (SCMP)", "url": "https://www.scmp.com", "rss_candidates": ["https://www.scmp.com/rss/91/feed", "https://www.scmp.com/rss/2/feed", "https://www.scmp.com/rss/4/feed"]},

    # 5. 新加坡媒体 (3)
    {"id": "src-SG-MED-01", "name": "DealStreetAsia", "url": "https://www.dealstreetasia.com", "rss_candidates": ["https://www.dealstreetasia.com/feed/", "https://www.dealstreetasia.com/section/indochina/feed/"]},
    {"id": "src-SG-MED-02", "name": "The Business Times", "url": "https://www.businesstimes.com.sg/international/asean", "rss_candidates": ["https://www.businesstimes.com.sg/rss/international/asean.xml", "https://www.businesstimes.com.sg/rss/top-stories.xml", "https://www.businesstimes.com.sg/rss"]},
    {"id": "src-SG-MED-03", "name": "CNA (亚洲栏目)", "url": "https://www.channelnewsasia.com/asia", "rss_candidates": ["https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=6511", "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml"]},

    # 6. 日本媒体 (1)
    {"id": "src-JP-MED-01", "name": "Nikkei Asia", "url": "https://asia.nikkei.com", "rss_candidates": ["https://asia.nikkei.com/rss/feed/nar", "https://asia.nikkei.com/rss/feed/nar_business"]},

    # 7. 韩国媒体 (8)
    {"id": "src-KR-MED-01", "name": "BusinessKorea", "url": "https://www.businesskorea.co.kr", "rss_candidates": ["https://www.businesskorea.co.kr/rss/allArticle.xml", "https://www.businesskorea.co.kr/rss/S1N1.xml"]},
    {"id": "src-KR-MED-02", "name": "Korea Herald", "url": "https://www.koreaherald.com", "rss_candidates": ["https://www.koreaherald.com/common/rss_xml.php?ct=102", "https://www.koreaherald.com/rss/allArticle.xml"]},
    {"id": "src-KR-MED-03", "name": "Yonhap", "url": "https://en.yna.co.kr", "rss_candidates": ["https://en.yna.co.kr/RSS/economy.xml", "https://en.yna.co.kr/RSS/news.xml"]},
    {"id": "src-KR-MED-04", "name": "THE ELEC", "url": "https://thelec.net", "rss_candidates": ["https://thelec.net/feed/", "https://thelec.net/rss", "https://www.thelec.kr/rss/allArticle.xml"]},
    {"id": "src-KR-MED-05", "name": "Korea Times", "url": "https://www.koreatimes.co.kr", "rss_candidates": ["https://www.koreatimes.co.kr/www/rss/rss.xml", "https://www.koreatimes.co.kr/www/rss/biz.xml"]},
    {"id": "src-KR-MED-06", "name": "Financial News", "url": "https://www.fnnews.com", "rss_candidates": ["https://www.fnnews.com/rss/fn_realnews_all.xml", "https://www.fnnews.com/rss/new/fn_realnews_stock.xml"]},
    {"id": "src-KR-MED-07", "name": "Chosun", "url": "https://biz.chosun.com", "rss_candidates": ["https://biz.chosun.com/rss/index.xml", "https://www.chosun.com/arc/outboundfeeds/rss/?outputType=xml"]},
    {"id": "src-KR-MED-08", "name": "Seoul Economic Daily", "url": "https://www.sedaily.com", "rss_candidates": ["https://www.sedaily.com/RSS/Economy", "https://www.sedaily.com/RSS/Industry"]},

    # 8. 台湾媒体 (2)
    {"id": "src-TW-MED-01", "name": "DigiTimes", "url": "https://www.digitimes.com", "rss_candidates": ["https://www.digitimes.com/rss/daily.xml", "https://www.digitimes.com.tw/rss/news_xml.asp"]},
    {"id": "src-TW-MED-02", "name": "TechNews (科技新报)", "url": "https://technews.tw", "rss_candidates": ["https://technews.tw/feed/", "https://technews.tw/category/component/feed/"]},

    # 9. 印度媒体 (2)
    {"id": "src-IN-MED-01", "name": "The Economic Times", "url": "https://economictimes.indiatimes.com", "rss_candidates": ["https://economictimes.indiatimes.com/news/economy/rssfeeds/1373380680.cms", "https://economictimes.indiatimes.com/rssfeeds/2143429.cms"]},
    {"id": "src-IN-MED-02", "name": "Business Standard", "url": "https://www.business-standard.com", "rss_candidates": ["https://www.business-standard.com/rss/economy-policy-102.rss", "https://www.business-standard.com/rss/companies-101.rss", "https://www.business-standard.com/rss/home_page_top_stories.rss"]},

    # 10. 行业专业媒体 (3)
    {"id": "src-IND-PROP-01", "name": "Mingtiandi (工业地产)", "url": "https://www.mingtiandi.com", "rss_candidates": ["https://www.mingtiandi.com/feed/", "https://www.mingtiandi.com/tag/vietnam/feed/"]},
    {"id": "src-IND-PROP-02", "name": "TechNode Global", "url": "https://technode.global", "rss_candidates": ["https://technode.global/feed/"]},
    {"id": "src-IND-PROP-03", "name": "DatacenterDynamics", "url": "https://www.datacenterdynamics.com", "rss_candidates": ["https://www.datacenterdynamics.com/en/rss/"]},

    # 11. 其他与中文原创 (3)
    {"id": "src-OTH-MED-01", "name": "Manila Bulletin", "url": "https://mb.com.ph", "rss_candidates": ["https://mb.com.ph/rss/business", "https://mb.com.ph/feed/"]},
    {"id": "src-OTH-MED-02", "name": "The Star", "url": "https://www.thestar.com.my", "rss_candidates": ["https://www.thestar.com.my/rss/business/business-news", "https://www.thestar.com.my/rss/editors-choice"]},
    {"id": "src-CN-ORIG-01", "name": "界面新闻 (出海专栏)", "url": "https://www.jiemian.com", "rss_candidates": ["https://a.jiemian.com/index.php?m=article&a=rss", "https://www.jiemian.com/rss/index.xml"]}
]

def probe_one(client, item):
    sid = item["id"]
    name = item["name"]
    url = item["url"]
    print(f"\n--- Probing [{sid}] {name} ({url}) ---")
    
    # 1. Try home page
    home_res = None
    try:
        t0 = time.time()
        r = client.get(url, timeout=12.0)
        dur = round((time.time() - t0) * 1000, 1)
        print(f"  Home: HTTP {r.status_code} in {dur}ms, len={len(r.content)}, server={r.headers.get('server')}")
        home_res = r
    except Exception as e:
        print(f"  Home FAILED: {type(e).__name__}: {e}")

    # Check for RSS in homepage html
    discovered_rss = []
    if home_res and home_res.status_code == 200:
        soup = BeautifulSoup(home_res.text[:100000], "html.parser")
        for link in soup.find_all("link", rel=lambda x: x and ("alternate" in x.lower() or "rss" in x.lower())):
            href = link.get("href", "")
            t = link.get("type", "")
            if "rss" in t or "xml" in t or "feed" in href or "rss" in href:
                full_href = href if href.startswith("http") else url.rstrip("/") + "/" + href.lstrip("/")
                discovered_rss.append(full_href)
        if discovered_rss:
            print(f"  Discovered RSS in HTML: {discovered_rss[:3]}")

    # 2. Test candidate RSS
    all_candidates = list(dict.fromkeys(item.get("rss_candidates", []) + discovered_rss))
    rss_found = None
    for cand in all_candidates:
        try:
            t0 = time.time()
            cr = client.get(cand, timeout=10.0)
            if cr.status_code == 200:
                # Test feedparser
                fp = feedparser.parse(cr.content)
                if fp.entries and len(fp.entries) > 0:
                    print(f"  SUCCESS RSS: {cand} ({len(fp.entries)} entries)")
                    rss_found = {
                        "endpoint": cand,
                        "count": len(fp.entries),
                        "sample_title": fp.entries[0].get("title", ""),
                        "sample_date": fp.entries[0].get("published", "") or fp.entries[0].get("updated", ""),
                        "sample_link": fp.entries[0].get("link", ""),
                    }
                    print(f"    Sample: {rss_found['sample_title']} | {rss_found['sample_date']}")
                    break
                else:
                    # Maybe XML sitemap?
                    if "<urlset" in cr.text or "<sitemapindex" in cr.text:
                        print(f"  SUCCESS XML Sitemap: {cand}")
                        rss_found = {"endpoint": cand, "type": "sitemap", "xml": True}
                        break
                    else:
                        print(f"  Candidate 200 but 0 entries: {cand}")
            else:
                print(f"  Candidate HTTP {cr.status_code}: {cand}")
        except Exception as e:
            print(f"  Candidate error {cand}: {type(e).__name__}")

    return {
        "id": sid,
        "name": name,
        "url": url,
        "home_status": home_res.status_code if home_res else None,
        "server": home_res.headers.get("server") if home_res else None,
        "rss_found": rss_found
    }

def main():
    client = httpx.Client(verify=False, follow_redirects=True, headers=DEFAULT_HEADERS)
    results = []
    
    # Run all 55 sources
    for item in SOURCES:
        res = probe_one(client, item)
        results.append(res)
        time.sleep(0.1)
        
    print(f"\nFinished probing {len(results)} sources.")
    rss_count = sum(1 for r in results if r["rss_found"])
    print(f"RSS/Sitemap found: {rss_count}/{len(results)}")

if __name__ == "__main__":
    main()
