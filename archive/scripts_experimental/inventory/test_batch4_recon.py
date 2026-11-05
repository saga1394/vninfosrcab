import sys
import httpx
from bs4 import BeautifulSoup
import feedparser

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

TEST_TARGETS = [
    # 1. Enterprise Disclosure (13)
    {"id": "DISC-01", "name": "巨潮资讯网 (CNINFO)", "url": "http://www.cninfo.com.cn/new/index"},
    {"id": "DISC-02", "name": "上海证券交易所 (SSE)", "url": "https://www.sse.com.cn/disclosure/listedinfo/announcement/"},
    {"id": "DISC-03", "name": "深圳证券交易所 (SZSE)", "url": "https://www.szse.cn/disclosure/listed/notice/index.html"},
    {"id": "DISC-04", "name": "北京证券交易所 (BSE)", "url": "https://www.bse.cn/disclosure/announcement.html"},
    {"id": "DISC-05", "name": "港交所披露易 (HKEXnews)", "url": "https://www.hkexnews.hk/index_c.htm"},
    {"id": "DISC-06", "name": "台湾公开资讯观测站 (MOPS)", "url": "https://mops.twse.com.tw/mops/web/t05st01"},
    {"id": "DISC-07", "name": "新加坡交易所公告 (SGX)", "url": "https://www.sgx.com/securities/company-announcements"},
    {"id": "DISC-08", "name": "韩国金融监督院 (DART)", "url": "https://dart.fss.or.kr/"},
    {"id": "DISC-09", "name": "东京证券交易所 (JPX/TDnet)", "url": "https://www.release.tdnet.info/inbs/I_main_00.html"},
    {"id": "DISC-10", "name": "美国SEC EDGAR检索", "url": "https://www.sec.gov/edgar/searchedgar/companysearch"},
    {"id": "DISC-11", "name": "印度国家证券交易所 (NSE)", "url": "https://www.nseindia.com/companies-listing/corporate-filings-announcements"},
    {"id": "DISC-12", "name": "印度孟买证券交易所 (BSE)", "url": "https://www.bseindia.com/corporates/ann.html"},
    {"id": "DISC-13", "name": "企业自有信披代表 (Elmet IR)", "url": "https://investors.theelmetgroup.com/"},

    # 2. Industry Associations (7)
    {"id": "ASSOC-01", "name": "越南纺织服装协会 (VITAS)", "url": "https://vietnamtextile.org.vn"},
    {"id": "ASSOC-02", "name": "越南电子工业协会 (VEIA)", "url": "https://veia.org.vn"},
    {"id": "ASSOC-03", "name": "越南物流服务企业协会 (VLA)", "url": "https://vla.com.vn"},
    {"id": "ASSOC-04", "name": "越南工商业联合会 (VCCI)", "url": "https://vcci.com.vn/news"},
    {"id": "ASSOC-05", "name": "涉外专业律所 (Vilasia)", "url": "https://vilasia.com"},
    {"id": "ASSOC-06", "name": "新加坡工商联合会 (SBF)", "url": "https://www.sbf.org.sg"},
    {"id": "ASSOC-07", "name": "新加坡制造业总会 (SMF)", "url": "https://www.smfederation.org.sg"},

    # 3. International Development (3)
    {"id": "INTL-01", "name": "世界银行越南专页 (World Bank Vietnam / IFC)", "url": "https://www.worldbank.org/en/country/vietnam"},
    {"id": "INTL-02", "name": "亚洲开发银行 (ADB Vietnam Projects)", "url": "https://www.adb.org/where-we-work/viet-nam/projects-results"},
    {"id": "INTL-03", "name": "亚洲基础设施投资银行 (AIIB Projects)", "url": "https://www.aiib.org/en/projects/list/index.html"},

    # 4. Supplementary Channels (14)
    {"id": "SUPP-01", "name": "美通社亚太 (PR Newswire)", "url": "https://www.prnasia.com/"},
    {"id": "SUPP-02", "name": "Media OutReach / EtNet", "url": "https://www.media-outreach.com/"},
    {"id": "SUPP-03", "name": "新浪财经", "url": "https://finance.sina.com.cn"},
    {"id": "SUPP-04", "name": "腾讯新闻", "url": "https://news.qq.com"},
    {"id": "SUPP-05", "name": "网易财经", "url": "https://money.163.com"},
    {"id": "SUPP-06", "name": "搜狐财经", "url": "https://business.sohu.com"},
    {"id": "SUPP-07", "name": "EtNet 经济通", "url": "https://www.etnet.com.hk"},
    {"id": "SUPP-08", "name": "越南中文社", "url": "https://www.yuenanzhongwen.com"},
    {"id": "SUPP-09", "name": "Vietnam.vn (官方汇聚)", "url": "https://www.vietnam.vn"},
    {"id": "SUPP-10", "name": "Longbridge (长桥)", "url": "https://longbridge.hk"},
    {"id": "SUPP-11", "name": "越南政府 Facebook", "url": "https://www.facebook.com/thongtinchinhphu"},
    {"id": "SUPP-12", "name": "VnExpress Facebook", "url": "https://www.facebook.com/CongdongVnexpress"},
    {"id": "SUPP-13", "name": "Báo Đầu tư Facebook", "url": "https://www.facebook.com/Baodautuonline"},
    {"id": "SUPP-14", "name": "企业微信公众号 (搜狗微信)", "url": "https://weixin.sogou.com/"},
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
}

client = httpx.Client(verify=False, follow_redirects=True, timeout=12.0, headers=headers)

for item in TEST_TARGETS:
    try:
        r = client.get(item['url'])
        print(f"[{item['id']}] {item['name']}: {r.status_code} len={len(r.content)} url={r.url}")
    except Exception as e:
        print(f"[{item['id']}] {item['name']}: ERROR {type(e).__name__} - {str(e)[:100]}")
