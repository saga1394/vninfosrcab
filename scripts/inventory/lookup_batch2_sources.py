import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('2026-11-01-PROJECT-RESULTS.md', 'r', encoding='utf-8') as f:
    text1 = f.read()
with open('2026-11-01-ADJUSTED-SOURCES.md', 'r', encoding='utf-8') as f:
    text2 = f.read()

combined = text1 + '\n' + text2

keywords = [
    ('VietnamPlus', ['vietnamplus']),
    ('Nhân Dân', ['nhandan']),
    ('VTV', ['vtv.vn']),
    ('VOV', ['vov.vn']),
    ('SGGP', ['sggp.org.vn']),
    ('Vietnam News', ['vietnamnews.vn']),
    ('VnExpress', ['vnexpress.net']),
    ('Tuổi Trẻ', ['tuoitre.vn']),
    ('Thanh Niên', ['thanhnien.vn']),
    ('VietnamNet', ['vietnamnet.vn']),
    ('Dân Trí', ['dantri.com.vn']),
    ('Znews', ['znews.vn', 'zingnews.vn']),
    ('Báo Đầu tư', ['baodautu.vn']),
    ('VnEconomy', ['vneconomy.vn']),
    ('CafeF', ['cafef.vn']),
    ('Vietstock', ['vietstock.vn']),
    ('Công Thương', ['congthuong.vn']),
    ('The Investor', ['theinvestor.vn']),
    ('BizHub', ['bizhub.vietnamnews.vn', 'bizhub']),
    ('Thời báo Tài chính VN', ['thoibaotaichinhvietnam.vn']),
    ('CafeLand', ['cafeland.vn']),
    ('Diễn đàn Doanh nghiệp', ['diendandoanhnghiep.vn', 'dddn.com.vn']),
    ('Báo Hải Phòng', ['baohaiphong.com.vn', 'baohaiphong.vn']),
    ('Báo Bắc Ninh', ['baobacninh.com.vn']),
    ('Báo Hưng Yên', ['baohungyen.vn']),
    ('Báo Thái Nguyên', ['baothainguyen.vn']),
    ('Báo Đà Nẵng', ['baodanang.vn']),
    ('Báo Tây Ninh', ['baotayninh.vn']),
    ('Báo Đồng Nai', ['baodongnai.com.vn']),
    ('Báo Quảng Ninh', ['baoquangninh.vn', 'baoquangninh.com.vn']),
    ('Reuters', ['reuters.com']),
    ('Bloomberg', ['bloomberg.com']),
    ('South China Morning Post', ['scmp.com']),
    ('DealStreetAsia', ['dealstreetasia.com']),
    ('The Business Times', ['businesstimes.com.sg']),
    ('CNA', ['channelnewsasia.com']),
    ('Nikkei Asia', ['asia.nikkei.com']),
    ('BusinessKorea', ['businesskorea.co.kr']),
    ('Korea Herald', ['koreaherald.com']),
    ('Yonhap', ['yna.co.kr', 'en.yna.co.kr']),
    ('THE ELEC', ['thelec.net', 'thelec.kr']),
    ('Korea Times', ['koreatimes.co.kr']),
    ('Financial News', ['fnnews.com']),
    ('Chosun', ['chosun.com']),
    ('Seoul Economic Daily', ['sedaily.com']),
    ('DigiTimes', ['digitimes.com']),
    ('TechNews', ['technews.tw']),
    ('The Economic Times', ['economictimes.indiatimes.com']),
    ('Business Standard', ['business-standard.com']),
    ('Mingtiandi', ['mingtiandi.com']),
    ('TechNode Global', ['technode.global']),
    ('DatacenterDynamics', ['datacenterdynamics.com']),
    ('Manila Bulletin', ['mb.com.ph']),
    ('The Star', ['thestar.com.my']),
    ('界面新闻', ['jiemian.com'])
]

print(f"Total targets: {len(keywords)}")
for name, patterns in keywords:
    found_urls = set()
    for p in patterns:
        matches = re.findall(rf'https?://[^\s\)\"\'\<\>]*{p}[^\s\)\"\'\<\>]*', combined, re.IGNORECASE)
        for m in matches:
            found_urls.add(m)
    print(f"[{name}]: {list(found_urls)[:3] if found_urls else 'NOT FOUND IN TEXT'}")
