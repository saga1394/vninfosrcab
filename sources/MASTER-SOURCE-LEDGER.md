# 全网全量 196 个信息源全局动态管理总台账 (Ref: 4729)

> **项目执行代号**：4729  
> **资产性质**：越南产业情报监测系统底层信源核心资产库（永久存续、全量覆盖、动态维护）  
> **管理原则**：彻底抛弃“二八定律收窄”与“机械爬虫抓取”思维；196 个源全量同等对待、无抽查、无死角；逐源建立独立活体档案卡（位于 `sources/dossiers/`）；全面推行“人类分析师模拟浏览与供给画像”；优先锁定细分 RSS 频道与权威直达入口。

---

## 一、 全局信源大盘与工程通道统计

| 统计维度 | 数量 / 占比 | 说明 |
|---|:---:|---|
| **信源总盘子** | **196 个** | 涵盖国家部委、标杆园区、国内外主流与专业媒体、16大工业省市、资本市场信披与行业协会 |
| **原生 RSS / Atom 通道** | **44 个 (22.4%)** | 毫秒级极速响应，零 DOM 破损风险，精准锁定产业/经济二级 RSS 频道 |
| **规整 HTML 表格/列表** | **112 个 (57.1%)** | 地方门户、部委通知、环评/排污法定公示、轻量语义化提取 |
| **官方 REST API 通道** | **8 个 (4.1%)** | 财政部、证券交易所、国际金融组织直达 JSON 接口 |
| **XML Sitemap / 索引** | **5 个 (2.6%)** | 法律数据库、新加坡政务网增量流 |
| **受限/需会话穿透通道** | **27 个 (13.8%)** | 商业交易所 WAF (MOPS/SGX/NSE)、外媒 Cloudflare 拦截、社交围墙 (需专项配置) |

---

## 二、 全量 196 源明细清单与档案卡索引

| 序号 | 唯一代码 | 机构 / 信源全称 | 所属类别 | 首选通道 / 交互方式 | 目标正交栏目 | 档案卡直达链接 | 状态与可信度 |
|:---:|---|---|---|---|---|:---:|:---:|
| 1 | `SRC-A01` | **Báo Chính phủ (Government Portal)** | National Official | Native RSS 2.0 | 行政审批 / 政经宏观 | [SRC-A01 档案卡](dossiers/SRC-A01-baochinhphu.md) | HTTP 200 正常 |
| 2 | `SRC-A02` | **Bộ Tài chính (Ministry of Finance - MOF)** | National Official | Official REST API (POST JSON) | 行政审批 / 政经宏观 | [SRC-A02 档案卡](dossiers/SRC-A02-mof.md) | HTTP 200 正常 |
| 3 | `SRC-A04` | **Bộ Công Thương (Ministry of Industry and Trade - MOIT)** | National Official | Lightweight HTML List Scraping | 行政审批 / 政经宏观 | [SRC-A04 档案卡](dossiers/SRC-A04-moit.md) | HTTP 200 正常 |
| 4 | `SRC-A05` | **Bộ Xây dựng (Ministry of Construction - MOC)** | National Official | Lightweight HTML List Scraping | 行政审批 / 政经宏观 | [SRC-A05 档案卡](dossiers/SRC-A05-moc.md) | HTTP 200 正常 |
| 5 | `SRC-A03` | **Tổng cục Thống kê (National Statistics Office - NSO)** | National Official | Native RSS 2.0 | 行政审批 / 政经宏观 | [SRC-A03 档案卡](dossiers/SRC-A03-nso.md) | HTTP 200 正常 |
| 6 | `SRC-A07` | **Cục Đầu tư nước ngoài (Foreign Investment Agency - FIA)** | National Official | Lightweight HTML List Scraping | 行政审批 / 政经宏观 | [SRC-A07 档案卡](dossiers/SRC-A07-fia.md) | HTTP 200 正常 |
| 7 | `SRC-A06` | **InvestVietnam (National Investment Promotion Portal)** | National Official | Lightweight HTML List Scraping | 行政审批 / 政经宏观 | [SRC-A06 档案卡](dossiers/SRC-A06-investvietnam.md) | HTTP 200 正常 |
| 8 | `SRC-A08` | **Bố cáo điện tử (National Enterprise Registration Announcements)** | National Official | Structured HTML Table (No Captcha) | 行政审批 / 政经宏观 | [SRC-A08 档案卡](dossiers/SRC-A08-bocaodientu.md) | HTTP 200 正常 |
| 9 | `SRC-A09` | **Tham vấn ĐTM (EIA Public Consultation - MAE)** | National Official | Structured HTML Table (SChannel fallback) | 行政审批 / 政经宏观 | [SRC-A09 档案卡](dossiers/SRC-A09-dsdtm.md) | HTTP 200 正常 |
| 10 | `SRC-A10` | **Tham vấn Giấy phép môi trường (Environmental Permit Application - MAE)** | National Official | Structured HTML Table (SChannel fallback) | 行政审批 / 政经宏观 | [SRC-A10 档案卡](dossiers/SRC-A10-dsgiayphep.md) | HTTP 200 正常 |
| 11 | `SRC-A11` | **Bộ Nông nghiệp và Môi trường (Ministry of Agriculture and Environment - MAE)** | National Official | Lightweight HTML List Scraping | 行政审批 / 政经宏观 | [SRC-A11 档案卡](dossiers/SRC-A11-mae.md) | HTTP 200 正常 |
| 12 | `SRC-A12` | **Công báo Chính phủ (Official Gazette)** | National Official | Lightweight HTML List Scraping (RSS empty placeholder) | 行政审批 / 政经宏观 | [SRC-A12 档案卡](dossiers/SRC-A12-congbao.md) | HTTP 200 正常 |
| 13 | `SRC-A13` | **Cơ sở dữ liệu quốc gia về VBPL (National Legal Database)** | National Official | Structured XML Sitemap Index | 行政审批 / 政经宏观 | [SRC-A13 档案卡](dossiers/SRC-A13-vbpl.md) | HTTP 200 正常 |
| 14 | `SRC-A14` | **Ministry of Energy, Trade and Industry (Singapore MTI/METI)** | National Official | Lightweight HTML List Scraping | 行政审批 / 政经宏观 | [SRC-A14 档案卡](dossiers/SRC-A14-mti_sg.md) | HTTP 200 正常 |
| 15 | `SRC-A15` | **Enterprise Singapore** | National Official | Structured XML Sitemap | 行政审批 / 政经宏观 | [SRC-A15 档案卡](dossiers/SRC-A15-enterprisesg.md) | HTTP 200 正常 |
| 16 | `SRC-A16` | **ACRA / Bizfile (Accounting and Corporate Regulatory Authority)** | National Official | Native RSS 2.0 | 行政审批 / 政经宏观 | [SRC-A16 档案卡](dossiers/SRC-A16-acra_bizfile.md) | HTTP 200 正常 |
| 17 | `SRC-B01` | **VSIP Group (Vietnam Singapore Industrial Park)** | Benchmark Industrial Parks | Native RSS 2.0 | 工业园区一线动态 | [SRC-B01 档案卡](dossiers/SRC-B01-vsip.md) | HTTP 200 正常 |
| 18 | `SRC-B02` | **Amata Vietnam** | Benchmark Industrial Parks | Native RSS 2.0 | 工业园区一线动态 | [SRC-B02 档案卡](dossiers/SRC-B02-amata.md) | HTTP 200 正常 |
| 19 | `SRC-B03` | **Becamex IDC** | Benchmark Industrial Parks | Native RSS 2.0 + HTML News Supplement | 工业园区一线动态 | [SRC-B03 档案卡](dossiers/SRC-B03-becamex.md) | HTTP 200 正常 |
| 20 | `SRC-B04` | **DEEP C Industrial Zones** | Benchmark Industrial Parks | Lightweight HTML Card Scraping | 工业园区一线动态 | [SRC-B04 档案卡](dossiers/SRC-B04-deepc.md) | HTTP 200 正常 |
| 21 | `SRC-B05` | **Long Hậu Corporation (LHC)** | Benchmark Industrial Parks | Lightweight HTML List Scraping | 工业园区一线动态 | [SRC-B05 档案卡](dossiers/SRC-B05-longhau.md) | HTTP 200 正常 |
| 22 | `SRC-B06` | **BW Industrial Development JSC** | Benchmark Industrial Parks | Native RSS 2.0 | 工业园区一线动态 | [SRC-B06 档案卡](dossiers/SRC-B06-bwindustrial.md) | HTTP 200 正常 |
| 23 | `SRC-B07` | **WHA Vietnam (WHA Industrial Development)** | Benchmark Industrial Parks | WAF Intercepted (Requires Headless/Session Token) | 工业园区一线动态 | [SRC-B07 档案卡](dossiers/SRC-B07-wha.md) | HTTP 200 正常 |
| 24 | `SRC-VN-GEN-01` | **VietnamPlus (越通社官方)** | Vietnam National General | Native RSS 2.0 | 五大栏目全面供给 | [SRC-VN-GEN-01 档案卡](dossiers/SRC-VN-GEN-01-vietnamplus.md) | HTTP 200 正常 |
| 25 | `SRC-VN-GEN-02` | **Nhân Dân (人民报 - 越共中央机关报)** | Vietnam National General | Native RSS 2.0 | 五大栏目全面供给 | [SRC-VN-GEN-02 档案卡](dossiers/SRC-VN-GEN-02-nhandan.md) | HTTP 200 正常 |
| 26 | `SRC-VN-GEN-03` | **VTV (越南国家电视台)** | Vietnam National General | Native RSS 2.0 | 五大栏目全面供给 | [SRC-VN-GEN-03 档案卡](dossiers/SRC-VN-GEN-03-vtv.md) | HTTP 200 正常 |
| 27 | `SRC-VN-GEN-04` | **VOV (越南之声广播电台)** | Vietnam National General | Lightweight HTML List | 五大栏目全面供给 | [SRC-VN-GEN-04 档案卡](dossiers/SRC-VN-GEN-04-vov.md) | HTTP 200 正常 |
| 28 | `SRC-VN-GEN-05` | **SGGP (Sài Gòn Giải Phóng - 西贡解放报)** | Vietnam National General | Native RSS 2.0 | 五大栏目全面供给 | [SRC-VN-GEN-05 档案卡](dossiers/SRC-VN-GEN-05-sggp.md) | HTTP 200 正常 |
| 29 | `SRC-VN-GEN-06` | **Vietnam News (国家英文旗舰)** | Vietnam National General | Native RSS 2.0 | 五大栏目全面供给 | [SRC-VN-GEN-06 档案卡](dossiers/SRC-VN-GEN-06-vietnamnews.md) | HTTP 200 正常 |
| 30 | `SRC-VN-GEN-07` | **VnExpress (越南快讯网)** | Vietnam National General | Native RSS 2.0 | 五大栏目全面供给 | [SRC-VN-GEN-07 档案卡](dossiers/SRC-VN-GEN-07-vnexpress.md) | HTTP 200 正常 |
| 31 | `SRC-VN-GEN-08` | **Tuổi Trẻ (青年报)** | Vietnam National General | Native RSS 2.0 | 五大栏目全面供给 | [SRC-VN-GEN-08 档案卡](dossiers/SRC-VN-GEN-08-tuoitre.md) | HTTP 200 正常 |
| 32 | `SRC-VN-GEN-09` | **Thanh Niên (青年报)** | Vietnam National General | Native RSS 2.0 | 五大栏目全面供给 | [SRC-VN-GEN-09 档案卡](dossiers/SRC-VN-GEN-09-thanhnien.md) | HTTP 200 正常 |
| 33 | `SRC-VN-GEN-10` | **VietnamNet (越南网 - 通讯传媒部)** | Vietnam National General | Native RSS 2.0 | 五大栏目全面供给 | [SRC-VN-GEN-10 档案卡](dossiers/SRC-VN-GEN-10-vietnamnet.md) | HTTP 200 正常 |
| 34 | `SRC-VN-GEN-11` | **Dân Trí (民智报 - 劳动荣军社会部)** | Vietnam National General | Native RSS 2.0 | 五大栏目全面供给 | [SRC-VN-GEN-11 档案卡](dossiers/SRC-VN-GEN-11-dantri.md) | HTTP 200 正常 |
| 35 | `SRC-VN-GEN-12` | **Znews (前 Zing News - 青年数字先锋)** | Vietnam National General | Native RSS 2.0 | 五大栏目全面供给 | [SRC-VN-GEN-12 档案卡](dossiers/SRC-VN-GEN-12-znews.md) | HTTP 200 正常 |
| 36 | `SRC-VN-FIN-01` | **Báo Đầu tư (越南投资报 - 计划投资部机关报)** | Vietnam Finance & Industry | Lightweight HTML List | 五大栏目全面供给 | [SRC-VN-FIN-01 档案卡](dossiers/SRC-VN-FIN-01-baodautu.md) | HTTP 200 正常 |
| 37 | `SRC-VN-FIN-02` | **VnEconomy (越南经济时报)** | Vietnam Finance & Industry | Native RSS 2.0 | 五大栏目全面供给 | [SRC-VN-FIN-02 档案卡](dossiers/SRC-VN-FIN-02-vneconomy.md) | HTTP 200 正常 |
| 38 | `SRC-VN-FIN-03` | **CafeF (越南金融资本与上市公司频道)** | Vietnam Finance & Industry | Native RSS 2.0 | 五大栏目全面供给 | [SRC-VN-FIN-03 档案卡](dossiers/SRC-VN-FIN-03-cafef.md) | HTTP 200 正常 |
| 39 | `SRC-VN-FIN-04` | **Vietstock (越南证券投资门户)** | Vietnam Finance & Industry | Native RSS 2.0 | 五大栏目全面供给 | [SRC-VN-FIN-04 档案卡](dossiers/SRC-VN-FIN-04-vietstock.md) | HTTP 200 正常 |
| 40 | `SRC-VN-FIN-05` | **Công Thương (工贸报 - 工贸部机关报)** | Vietnam Finance & Industry | Native RSS 2.0 | 五大栏目全面供给 | [SRC-VN-FIN-05 档案卡](dossiers/SRC-VN-FIN-05-congthuong.md) | HTTP 200 正常 |
| 41 | `SRC-VN-FIN-06` | **The Investor (越南外资英文旗舰)** | Vietnam Finance & Industry | Lightweight HTML List + XML Sitemap | FDI 外资投资动向 | [SRC-VN-FIN-06 档案卡](dossiers/SRC-VN-FIN-06-theinvestor.md) | HTTP 200 正常 |
| 42 | `SRC-VN-FIN-07` | **BizHub (Vietnam News 商业英文专刊)** | Vietnam Finance & Industry | Native RSS 2.0 | 五大栏目全面供给 | [SRC-VN-FIN-07 档案卡](dossiers/SRC-VN-FIN-07-bizhub.md) | HTTP 200 正常 |
| 43 | `SRC-VN-FIN-08` | **Thời báo Tài chính VN (越南财政时报)** | Vietnam Finance & Industry | Native RSS 2.0 | 五大栏目全面供给 | [SRC-VN-FIN-08 档案卡](dossiers/SRC-VN-FIN-08-thoibaotaichinh.md) | HTTP 200 正常 |
| 44 | `SRC-VN-FIN-09` | **CafeLand (越南地产与产业基础设施门户)** | Vietnam Finance & Industry | Lightweight HTML List | 五大栏目全面供给 | [SRC-VN-FIN-09 档案卡](dossiers/SRC-VN-FIN-09-cafeland.md) | HTTP 200 正常 |
| 45 | `SRC-VN-FIN-10` | **Diễn đàn Doanh nghiệp (企业论坛 - VCCI机关报)** | Vietnam Finance & Industry | Lightweight HTML List | 五大栏目全面供给 | [SRC-VN-FIN-10 档案卡](dossiers/SRC-VN-FIN-10-dddn.md) | HTTP 200 正常 |
| 46 | `SRC-VN-LOC-01` | **Báo Hải Phòng (海防报)** | Vietnam Local Media | Lightweight HTML List | 五大栏目全面供给 | [SRC-VN-LOC-01 档案卡](dossiers/SRC-VN-LOC-01-baohaiphong.md) | HTTP 200 正常 |
| 47 | `SRC-VN-LOC-02` | **Báo Bắc Ninh / Đài PT-TH Bắc Ninh (北宁报/台)** | Vietnam Local Media | Lightweight HTML List | 五大栏目全面供给 | [SRC-VN-LOC-02 档案卡](dossiers/SRC-VN-LOC-02-baobacninh.md) | HTTP 200 正常 |
| 48 | `SRC-VN-LOC-03` | **Báo Hưng Yên (兴安报)** | Vietnam Local Media | Lightweight HTML List | 五大栏目全面供给 | [SRC-VN-LOC-03 档案卡](dossiers/SRC-VN-LOC-03-baohungyen.md) | HTTP 200 正常 |
| 49 | `SRC-VN-LOC-04` | **Báo Thái Nguyên (太原报)** | Vietnam Local Media | Lightweight HTML List | 五大栏目全面供给 | [SRC-VN-LOC-04 档案卡](dossiers/SRC-VN-LOC-04-baothainguyen.md) | HTTP 200 正常 |
| 50 | `SRC-VN-LOC-05` | **Báo Đà Nẵng (岘港报)** | Vietnam Local Media | Lightweight HTML List | 五大栏目全面供给 | [SRC-VN-LOC-05 档案卡](dossiers/SRC-VN-LOC-05-baodanang.md) | HTTP 200 正常 |
| 51 | `SRC-VN-LOC-06` | **Báo Tây Ninh (西宁报)** | Vietnam Local Media | Lightweight HTML List | 五大栏目全面供给 | [SRC-VN-LOC-06 档案卡](dossiers/SRC-VN-LOC-06-baotayninh.md) | HTTP 200 正常 |
| 52 | `SRC-VN-LOC-07` | **Báo Đồng Nai (同奈报)** | Vietnam Local Media | Lightweight HTML List | 五大栏目全面供给 | [SRC-VN-LOC-07 档案卡](dossiers/SRC-VN-LOC-07-baodongnai.md) | HTTP 200 正常 |
| 53 | `SRC-VN-LOC-08` | **Báo Quảng Ninh (广宁报)** | Vietnam Local Media | Native RSS 2.0 | 五大栏目全面供给 | [SRC-VN-LOC-08 档案卡](dossiers/SRC-VN-LOC-08-baoquangninh.md) | HTTP 200 正常 |
| 54 | `SRC-INT-WIRE-01` | **Reuters (路透社)** | International Wire | WAF Intercepted (CloudFront 401) | FDI / 重点产业 (海外强传导) | [SRC-INT-WIRE-01 档案卡](dossiers/SRC-INT-WIRE-01-reuters.md) | HTTP 401 需穿透 |
| 55 | `SRC-INT-WIRE-02` | **Bloomberg (彭博社 - Markets RSS)** | International Wire | Native RSS 2.0 | FDI / 重点产业 (海外强传导) | [SRC-INT-WIRE-02 档案卡](dossiers/SRC-INT-WIRE-02-bloomberg.md) | HTTP 200 正常 |
| 56 | `SRC-INT-WIRE-03` | **South China Morning Post (SCMP - 南华早报)** | International Wire | Native RSS 2.0 | FDI / 重点产业 (海外强传导) | [SRC-INT-WIRE-03 档案卡](dossiers/SRC-INT-WIRE-03-scmp.md) | HTTP 200 正常 |
| 57 | `SRC-SG-MED-01` | **DealStreetAsia (新加坡投融资媒体)** | Singapore Media | Lightweight HTML List | 五大栏目全面供给 | [SRC-SG-MED-01 档案卡](dossiers/SRC-SG-MED-01-dealstreetasia.md) | HTTP 200 正常 |
| 58 | `SRC-SG-MED-02` | **The Business Times (新加坡商业时报 - 东盟栏目)** | Singapore Media | Lightweight HTML List | 五大栏目全面供给 | [SRC-SG-MED-02 档案卡](dossiers/SRC-SG-MED-02-businesstimes.md) | HTTP 200 正常 |
| 59 | `SRC-SG-MED-03` | **CNA (Channel NewsAsia - 亚洲专栏)** | Singapore Media | Native RSS 2.0 | 五大栏目全面供给 | [SRC-SG-MED-03 档案卡](dossiers/SRC-SG-MED-03-cna.md) | HTTP 200 正常 |
| 60 | `SRC-JP-MED-01` | **Nikkei Asia (日经亚洲)** | Japan Media | Native RSS 2.0 | 五大栏目全面供给 | [SRC-JP-MED-01 档案卡](dossiers/SRC-JP-MED-01-nikkei.md) | HTTP 200 正常 |
| 61 | `SRC-KR-MED-01` | **BusinessKorea (韩国商业新闻)** | Korea Media | Native RSS 2.0 | 五大栏目全面供给 | [SRC-KR-MED-01 档案卡](dossiers/SRC-KR-MED-01-businesskorea.md) | HTTP 200 正常 |
| 62 | `SRC-KR-MED-02` | **The Korea Herald (韩国先驱报)** | Korea Media | Native RSS 2.0 | 五大栏目全面供给 | [SRC-KR-MED-02 档案卡](dossiers/SRC-KR-MED-02-koreaherald.md) | HTTP 200 正常 |
| 63 | `SRC-KR-MED-03` | **Yonhap News Agency (韩联社英文网)** | Korea Media | Native RSS 2.0 | 五大栏目全面供给 | [SRC-KR-MED-03 档案卡](dossiers/SRC-KR-MED-03-yonhap.md) | HTTP 200 正常 |
| 64 | `SRC-KR-MED-04` | **THE ELEC (电子科技专业媒体)** | Korea Media | Native RSS 2.0 | 五大栏目全面供给 | [SRC-KR-MED-04 档案卡](dossiers/SRC-KR-MED-04-theelec.md) | HTTP 200 正常 |
| 65 | `SRC-KR-MED-05` | **The Korea Times (韩国时报)** | Korea Media | Lightweight HTML List | 五大栏目全面供给 | [SRC-KR-MED-05 档案卡](dossiers/SRC-KR-MED-05-koreatimes.md) | HTTP 200 正常 |
| 66 | `SRC-KR-MED-06` | **Financial News Korea (韩国财经新闻)** | Korea Media | Lightweight HTML List | 五大栏目全面供给 | [SRC-KR-MED-06 档案卡](dossiers/SRC-KR-MED-06-fnnews.md) | HTTP 200 正常 |
| 67 | `SRC-KR-MED-07` | **Chosun Ilbo / Chosun Biz (朝鲜日报/商业网)** | Korea Media | Native RSS 2.0 | 五大栏目全面供给 | [SRC-KR-MED-07 档案卡](dossiers/SRC-KR-MED-07-chosun.md) | HTTP 200 正常 |
| 68 | `SRC-KR-MED-08` | **Seoul Economic Daily (首尔经济日报)** | Korea Media | Native RSS 2.0 | 五大栏目全面供给 | [SRC-KR-MED-08 档案卡](dossiers/SRC-KR-MED-08-sedaily.md) | HTTP 200 正常 |
| 69 | `SRC-TW-MED-01` | **DigiTimes (电子时报 - 全球半导体供应链)** | Taiwan Media | Native RSS 2.0 | 五大栏目全面供给 | [SRC-TW-MED-01 档案卡](dossiers/SRC-TW-MED-01-digitimes.md) | HTTP 200 正常 |
| 70 | `SRC-TW-MED-02` | **TechNews (科技新报 - 台湾电子科技产业)** | Taiwan Media | Native RSS 2.0 | 五大栏目全面供给 | [SRC-TW-MED-02 档案卡](dossiers/SRC-TW-MED-02-technews.md) | HTTP 200 正常 |
| 71 | `SRC-IN-MED-01` | **The Economic Times (印度经济时报)** | India Media | Connection Refused / Blocked | 五大栏目全面供给 | [SRC-IN-MED-01 档案卡](dossiers/SRC-IN-MED-01-economictimes.md) | HTTP None 需穿透 |
| 72 | `SRC-IN-MED-02` | **Business Standard (商业标准报 - 印度)** | India Media | Native RSS 2.0 | 五大栏目全面供给 | [SRC-IN-MED-02 档案卡](dossiers/SRC-IN-MED-02-businessstandard.md) | HTTP 200 正常 |
| 73 | `SRC-IND-PROP-01` | **Mingtiandi (亚洲与越南工业地产旗舰)** | Industry Specialized | Native RSS 2.0 | 综合市场动态 | [SRC-IND-PROP-01 档案卡](dossiers/SRC-IND-PROP-01-mingtiandi.md) | HTTP 200 正常 |
| 74 | `SRC-IND-PROP-02` | **TechNode Global (东南亚泛科技与出海创投)** | Industry Specialized | Native RSS 2.0 (via cURL engine) | 综合市场动态 | [SRC-IND-PROP-02 档案卡](dossiers/SRC-IND-PROP-02-technode.md) | HTTP 200 正常 |
| 75 | `SRC-IND-PROP-03` | **DatacenterDynamics (DCD - 数据中心与云基础设施)** | Industry Specialized | Native RSS 2.0 | 综合市场动态 | [SRC-IND-PROP-03 档案卡](dossiers/SRC-IND-PROP-03-datacenterdynamics.md) | HTTP 200 正常 |
| 76 | `SRC-OTH-MED-01` | **Manila Bulletin (马尼拉公报 - 菲律宾)** | Other & Chinese Original | WAF Intercepted (Cloudflare 403) | 综合市场动态 | [SRC-OTH-MED-01 档案卡](dossiers/SRC-OTH-MED-01-manilabulletin.md) | HTTP 403 需穿透 |
| 77 | `SRC-OTH-MED-02` | **The Star (星报 - 马来西亚主流英文媒体)** | Other & Chinese Original | Lightweight HTML List | 综合市场动态 | [SRC-OTH-MED-02 档案卡](dossiers/SRC-OTH-MED-02-thestar.md) | HTTP 200 正常 |
| 78 | `SRC-CN-ORIG-01` | **界面新闻 (出海专栏与跨国企业报道)** | Other & Chinese Original | Native RSS 2.0 | 综合市场动态 | [SRC-CN-ORIG-01 档案卡](dossiers/SRC-CN-ORIG-01-jiemian.md) | HTTP 200 正常 |
| 79 | `VN-LOC-01-HN-A` | **Cổng thông tin điện tử Thành phố Hà Nội** | A | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-01-HN-A 档案卡](dossiers/VN-LOC-01-HN-A-VN_HN_PORTAL.md) | HTTP 200 正常 |
| 80 | `VN-LOC-01-HN-B` | **Ban Quản lý các Khu Công nghệ cao và Khu công nghiệp Hà Nội** | B | HTML Card / Semantic List | 工业园区一线动态 | [VN-LOC-01-HN-B 档案卡](dossiers/VN-LOC-01-HN-B-VN_HN_KCN.md) | HTTP 200 正常 |
| 81 | `VN-LOC-01-HN-C` | **Sở Tài chính Thành phố Hà Nội** | C | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-01-HN-C 档案卡](dossiers/VN-LOC-01-HN-C-VN_HN_SOTC.md) | HTTP 200 正常 |
| 82 | `VN-LOC-01-HN-D` | **Sở Nông nghiệp và Môi trường Thành phố Hà Nội** | D | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-01-HN-D 档案卡](dossiers/VN-LOC-01-HN-D-VN_HN_SONNMT.md) | HTTP 200 正常 |
| 83 | `VN-LOC-01-HN-E` | **Sở Xây dựng Thành phố Hà Nội** | E | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-01-HN-E 档案卡](dossiers/VN-LOC-01-HN-E-VN_HN_SOXD.md) | HTTP 200 正常 |
| 84 | `VN-LOC-02-HP-A` | **Cổng Thông tin điện tử Thành phố Hải Phòng** | A | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-02-HP-A 档案卡](dossiers/VN-LOC-02-HP-A-VN_HP_PORTAL.md) | HTTP 200 正常 |
| 85 | `VN-LOC-02-HP-B` | **Ban Quản lý Khu kinh tế Hải Phòng (HEZA)** | B | RSS 2.0 Feed | 综合市场动态 | [VN-LOC-02-HP-B 档案卡](dossiers/VN-LOC-02-HP-B-VN_HP_HEZA.md) | HTTP 200 正常 |
| 86 | `VN-LOC-02-HP-C` | **Sở Tài chính Thành phố Hải Phòng** | C | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-02-HP-C 档案卡](dossiers/VN-LOC-02-HP-C-VN_HP_SOTC.md) | HTTP 200 正常 |
| 87 | `VN-LOC-02-HP-D` | **Sở Nông nghiệp và Môi trường Thành phố Hải Phòng** | D | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-02-HP-D 档案卡](dossiers/VN-LOC-02-HP-D-VN_HP_SONNMT.md) | HTTP 200 正常 |
| 88 | `VN-LOC-02-HP-E` | **Sở Xây dựng Thành phố Hải Phòng** | E | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-02-HP-E 档案卡](dossiers/VN-LOC-02-HP-E-VN_HP_SOXD.md) | HTTP 200 正常 |
| 89 | `VN-LOC-03-BN-A` | **Cổng thông tin điện tử tỉnh Bắc Ninh** | A | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-03-BN-A 档案卡](dossiers/VN-LOC-03-BN-A-VN_BN_PORTAL.md) | HTTP 200 正常 |
| 90 | `VN-LOC-03-BN-B` | **Ban Quản lý các Khu công nghiệp Bắc Ninh** | B | HTML Card / Semantic List | 工业园区一线动态 | [VN-LOC-03-BN-B 档案卡](dossiers/VN-LOC-03-BN-B-VN_BN_KCN.md) | HTTP 200 正常 |
| 91 | `VN-LOC-03-BN-C` | **Sở Tài chính tỉnh Bắc Ninh** | C | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-03-BN-C 档案卡](dossiers/VN-LOC-03-BN-C-VN_BN_STC.md) | HTTP 200 正常 |
| 92 | `VN-LOC-03-BN-D` | **Sở Nông nghiệp và Môi trường tỉnh Bắc Ninh** | D | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-03-BN-D 档案卡](dossiers/VN-LOC-03-BN-D-VN_BN_SONNMT.md) | HTTP 200 正常 |
| 93 | `VN-LOC-03-BN-E` | **Sở Xây dựng tỉnh Bắc Ninh** | E | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-03-BN-E 档案卡](dossiers/VN-LOC-03-BN-E-VN_BN_SXD.md) | HTTP 200 正常 |
| 94 | `VN-LOC-04-TN-A` | **Cổng TTĐT tỉnh Thái Nguyên** | A | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-04-TN-A 档案卡](dossiers/VN-LOC-04-TN-A-VN_TN_PORTAL.md) | HTTP 200 正常 |
| 95 | `VN-LOC-04-TN-B` | **Ban Quản lý các Khu công nghiệp Thái Nguyên** | B | HTML Card / Semantic List | 工业园区一线动态 | [VN-LOC-04-TN-B 档案卡](dossiers/VN-LOC-04-TN-B-VN_TN_KCN.md) | HTTP 200 正常 |
| 96 | `VN-LOC-04-TN-C` | **Sở Tài chính tỉnh Thái Nguyên** | C | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-04-TN-C 档案卡](dossiers/VN-LOC-04-TN-C-VN_TN_SOTC.md) | HTTP 200 正常 |
| 97 | `VN-LOC-04-TN-D` | **Sở Nông nghiệp và Môi trường tỉnh Thái Nguyên** | D | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-04-TN-D 档案卡](dossiers/VN-LOC-04-TN-D-VN_TN_SONNMT.md) | HTTP 200 正常 |
| 98 | `VN-LOC-04-TN-E` | **Sở Xây dựng tỉnh Thái Nguyên** | E | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-04-TN-E 档案卡](dossiers/VN-LOC-04-TN-E-VN_TN_SOXD.md) | HTTP 200 正常 |
| 99 | `VN-LOC-05-HY-A` | **Cổng thông tin điện tử tỉnh Hưng Yên** | A | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-05-HY-A 档案卡](dossiers/VN-LOC-05-HY-A-VN_HY_PORTAL.md) | HTTP 200 正常 |
| 100 | `VN-LOC-05-HY-B` | **Ban Quản lý Khu kinh tế tỉnh Hưng Yên** | B | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-05-HY-B 档案卡](dossiers/VN-LOC-05-HY-B-VN_HY_KKT.md) | HTTP 200 正常 |
| 101 | `VN-LOC-05-HY-C` | **Sở Tài chính tỉnh Hưng Yên** | C | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-05-HY-C 档案卡](dossiers/VN-LOC-05-HY-C-VN_HY_SOTC.md) | HTTP 200 正常 |
| 102 | `VN-LOC-05-HY-D` | **Sở Nông nghiệp và Môi trường tỉnh Hưng Yên** | D | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-05-HY-D 档案卡](dossiers/VN-LOC-05-HY-D-VN_HY_SONNMT.md) | HTTP 200 正常 |
| 103 | `VN-LOC-05-HY-E` | **Sở Xây dựng tỉnh Hưng Yên** | E | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-05-HY-E 档案卡](dossiers/VN-LOC-05-HY-E-VN_HY_SOXD.md) | HTTP 200 正常 |
| 104 | `VN-LOC-06-QN-A` | **Cổng thông tin điện tử Tỉnh Quảng Ninh** | A | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-06-QN-A 档案卡](dossiers/VN-LOC-06-QN-A-VN_QN_PORTAL.md) | HTTP 200 正常 |
| 105 | `VN-LOC-06-QN-B` | **Ban Quản lý Khu kinh tế Quảng Ninh (QEZA)** | B | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-06-QN-B 档案卡](dossiers/VN-LOC-06-QN-B-VN_QN_QEZA.md) | HTTP 200 正常 |
| 106 | `VN-LOC-06-QN-C` | **Sở Tài chính Tỉnh Quảng Ninh** | C | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-06-QN-C 档案卡](dossiers/VN-LOC-06-QN-C-VN_QN_SOTC.md) | HTTP 200 正常 |
| 107 | `VN-LOC-06-QN-D` | **Sở Nông nghiệp và Môi trường tỉnh Quảng Ninh** | D | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-06-QN-D 档案卡](dossiers/VN-LOC-06-QN-D-VN_QN_SONNMT.md) | HTTP 200 正常 |
| 108 | `VN-LOC-06-QN-E` | **Sở Xây dựng Tỉnh Quảng Ninh** | E | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-06-QN-E 档案卡](dossiers/VN-LOC-06-QN-E-VN_QN_SOXD.md) | HTTP 200 正常 |
| 109 | `VN-LOC-07-PT-A` | **Cổng thông tin điện tử tỉnh Phú Thọ** | A | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-07-PT-A 档案卡](dossiers/VN-LOC-07-PT-A-VN_PT_PORTAL.md) | HTTP 200 正常 |
| 110 | `VN-LOC-07-PT-B` | **Ban Quản lý các Khu công nghiệp tỉnh Phú Thọ** | B | HTML Card / Semantic List | 工业园区一线动态 | [VN-LOC-07-PT-B 档案卡](dossiers/VN-LOC-07-PT-B-VN_PT_KCN.md) | HTTP 200 正常 |
| 111 | `VN-LOC-07-PT-C` | **Sở Tài chính tỉnh Phú Thọ** | C | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-07-PT-C 档案卡](dossiers/VN-LOC-07-PT-C-VN_PT_SOTC.md) | HTTP 200 正常 |
| 112 | `VN-LOC-07-PT-D` | **Sở Nông nghiệp và Môi trường tỉnh Phú Thọ** | D | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-07-PT-D 档案卡](dossiers/VN-LOC-07-PT-D-VN_PT_SONNMT.md) | HTTP 200 正常 |
| 113 | `VN-LOC-07-PT-E` | **Sở Xây dựng tỉnh Phú Thọ** | E | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-07-PT-E 档案卡](dossiers/VN-LOC-07-PT-E-VN_PT_SOXD.md) | HTTP 200 正常 |
| 114 | `VN-LOC-08-NB-A` | **Cổng thông tin điện tử Tỉnh Ninh Bình** | A | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-08-NB-A 档案卡](dossiers/VN-LOC-08-NB-A-VN_NB_PORTAL.md) | HTTP 200 正常 |
| 115 | `VN-LOC-08-NB-B` | **Ban Quản lý Khu kinh tế và các KCN tỉnh Ninh Bình** | B | HTML Card / Semantic List | 工业园区一线动态 | [VN-LOC-08-NB-B 档案卡](dossiers/VN-LOC-08-NB-B-VN_NB_IZA.md) | HTTP 200 正常 |
| 116 | `VN-LOC-08-NB-C` | **Sở Tài chính Ninh Bình** | C | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-08-NB-C 档案卡](dossiers/VN-LOC-08-NB-C-VN_NB_STC.md) | HTTP 200 正常 |
| 117 | `VN-LOC-08-NB-D` | **Sở Nông nghiệp và Môi trường Ninh Bình** | D | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-08-NB-D 档案卡](dossiers/VN-LOC-08-NB-D-VN_NB_SONNMT.md) | HTTP 200 正常 |
| 118 | `VN-LOC-08-NB-E` | **Sở Xây dựng Ninh Bình** | E | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-08-NB-E 档案卡](dossiers/VN-LOC-08-NB-E-VN_NB_SXD.md) | HTTP 200 正常 |
| 119 | `VN-LOC-09-HCM-A` | **Cổng thông tin điện tử Thành Phố Hồ Chí Minh** | A | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-09-HCM-A 档案卡](dossiers/VN-LOC-09-HCM-A-VN_HCM_PORTAL.md) | HTTP 200 正常 |
| 120 | `VN-LOC-09-HCM-B` | **Ban Quản lý các Khu chế xuất và công nghiệp TP.HCM (HEPZA)** | B | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-09-HCM-B 档案卡](dossiers/VN-LOC-09-HCM-B-VN_HCM_HEPZA.md) | HTTP 200 正常 |
| 121 | `VN-LOC-09-HCM-C` | **Sở Tài chính Thành phố Hồ Chí Minh** | C | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-09-HCM-C 档案卡](dossiers/VN-LOC-09-HCM-C-VN_HCM_SOTC.md) | HTTP 200 正常 |
| 122 | `VN-LOC-09-HCM-D` | **Sở Nông nghiệp và Môi trường Thành phố Hồ Chí Minh** | D | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-09-HCM-D 档案卡](dossiers/VN-LOC-09-HCM-D-VN_HCM_SONNMT.md) | HTTP 200 正常 |
| 123 | `VN-LOC-09-HCM-E` | **Sở Xây dựng Thành phố Hồ Chí Minh** | E | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-09-HCM-E 档案卡](dossiers/VN-LOC-09-HCM-E-VN_HCM_SOXD.md) | HTTP 200 正常 |
| 124 | `VN-LOC-10-DN-A` | **Cổng thông tin điện tử tỉnh Đồng Nai** | A | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-10-DN-A 档案卡](dossiers/VN-LOC-10-DN-A-VN_DN_PORTAL.md) | HTTP 200 正常 |
| 125 | `VN-LOC-10-DN-B` | **Ban Quản lý các Khu công nghiệp, KKT Đồng Nai (DNIEZA)** | B | HTML Card / Semantic List | 工业园区一线动态 | [VN-LOC-10-DN-B 档案卡](dossiers/VN-LOC-10-DN-B-VN_DN_DNIEZA.md) | HTTP 200 正常 |
| 126 | `VN-LOC-10-DN-C` | **Sở Tài chính tỉnh Đồng Nai** | C | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-10-DN-C 档案卡](dossiers/VN-LOC-10-DN-C-VN_DN_STC.md) | HTTP 200 正常 |
| 127 | `VN-LOC-10-DN-D` | **Sở Tài nguyên và Môi trường tỉnh Đồng Nai** | D | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-10-DN-D 档案卡](dossiers/VN-LOC-10-DN-D-VN_DN_STNMT.md) | HTTP 200 正常 |
| 128 | `VN-LOC-10-DN-E` | **Sở Xây dựng tỉnh Đồng Nai** | E | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-10-DN-E 档案卡](dossiers/VN-LOC-10-DN-E-VN_DN_SXD.md) | HTTP 200 正常 |
| 129 | `VN-LOC-11-TY-A` | **Cổng thông tin điện tử tỉnh Tây Ninh** | A | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-11-TY-A 档案卡](dossiers/VN-LOC-11-TY-A-VN_TY_PORTAL.md) | HTTP 200 正常 |
| 130 | `VN-LOC-11-TY-B` | **Ban Quản lý Khu kinh tế tỉnh Tây Ninh** | B | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-11-TY-B 档案卡](dossiers/VN-LOC-11-TY-B-VN_TY_KKT.md) | HTTP 200 正常 |
| 131 | `VN-LOC-11-TY-C` | **Sở Tài chính tỉnh Tây Ninh** | C | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-11-TY-C 档案卡](dossiers/VN-LOC-11-TY-C-VN_TY_STC.md) | HTTP 200 正常 |
| 132 | `VN-LOC-11-TY-D` | **Sở Nông nghiệp và Môi trường tỉnh Tây Ninh** | D | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-11-TY-D 档案卡](dossiers/VN-LOC-11-TY-D-VN_TY_SNNMT.md) | HTTP 200 正常 |
| 133 | `VN-LOC-11-TY-E` | **Sở Xây dựng tỉnh Tây Ninh** | E | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-11-TY-E 档案卡](dossiers/VN-LOC-11-TY-E-VN_TY_SXD.md) | HTTP 200 正常 |
| 134 | `VN-LOC-12-NA-A` | **Cổng thông tin điện tử Tỉnh Nghệ An** | A | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-12-NA-A 档案卡](dossiers/VN-LOC-12-NA-A-VN_NA_PORTAL.md) | HTTP 200 正常 |
| 135 | `VN-LOC-12-NA-B` | **Ban Quản lý Khu kinh tế Đông Nam Nghệ An** | B | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-12-NA-B 档案卡](dossiers/VN-LOC-12-NA-B-VN_NA_DONGNAM.md) | HTTP 200 正常 |
| 136 | `VN-LOC-12-NA-C` | **Sở Tài chính Tỉnh Nghệ An** | C | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-12-NA-C 档案卡](dossiers/VN-LOC-12-NA-C-VN_NA_SOTC.md) | HTTP 200 正常 |
| 137 | `VN-LOC-12-NA-D` | **Sở Tài nguyên và Môi trường Tỉnh Nghệ An** | D | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-12-NA-D 档案卡](dossiers/VN-LOC-12-NA-D-VN_NA_SOTNMT.md) | HTTP 200 正常 |
| 138 | `VN-LOC-12-NA-E` | **Sở Xây dựng Tỉnh Nghệ An** | E | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-12-NA-E 档案卡](dossiers/VN-LOC-12-NA-E-VN_NA_SOXD.md) | HTTP 200 正常 |
| 139 | `VN-LOC-13-TH-A` | **Cổng TTĐT tỉnh Thanh Hóa** | A | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-13-TH-A 档案卡](dossiers/VN-LOC-13-TH-A-VN_TH_PORTAL.md) | HTTP 200 正常 |
| 140 | `VN-LOC-13-TH-B` | **Ban Quản lý Khu kinh tế Nghi Sơn và các KCN Thanh Hóa** | B | SPA Auth Required / Shell | 工业园区一线动态 | [VN-LOC-13-TH-B 档案卡](dossiers/VN-LOC-13-TH-B-VN_TH_NGHISON.md) | HTTP 200 正常 |
| 141 | `VN-LOC-13-TH-C` | **Sở Tài chính tỉnh Thanh Hóa** | C | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-13-TH-C 档案卡](dossiers/VN-LOC-13-TH-C-VN_TH_STC.md) | HTTP 200 正常 |
| 142 | `VN-LOC-13-TH-D` | **Sở Tài nguyên và Môi trường Thanh Hóa** | D | HTTP 503 Server Error | 综合市场动态 | [VN-LOC-13-TH-D 档案卡](dossiers/VN-LOC-13-TH-D-VN_TH_STNMT.md) | HTTP 503 需穿透 |
| 143 | `VN-LOC-13-TH-E` | **Sở Xây Dựng Thanh Hóa** | E | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-13-TH-E 档案卡](dossiers/VN-LOC-13-TH-E-VN_TH_SXD.md) | HTTP 200 正常 |
| 144 | `VN-LOC-14-DD-A` | **Cổng Thông tin điện tử thành phố Đà Nẵng** | A | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-14-DD-A 档案卡](dossiers/VN-LOC-14-DD-A-VN_DD_PORTAL.md) | HTTP 200 正常 |
| 145 | `VN-LOC-14-DD-B` | **Ban Quản lý Khu công nghệ cao và các KCN Đà Nẵng (DSEZA)** | B | REST API (JSON) | 工业园区一线动态 | [VN-LOC-14-DD-B 档案卡](dossiers/VN-LOC-14-DD-B-VN_DD_DSEZA.md) | HTTP 200 正常 |
| 146 | `VN-LOC-14-DD-C` | **Sở Tài chính Thành phố Đà Nẵng** | C | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-14-DD-C 档案卡](dossiers/VN-LOC-14-DD-C-VN_DD_STC.md) | HTTP 200 正常 |
| 147 | `VN-LOC-14-DD-D` | **Sở Nông nghiệp và Môi trường Thành phố Đà Nẵng** | D | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-14-DD-D 档案卡](dossiers/VN-LOC-14-DD-D-VN_DD_SNNMT.md) | HTTP 200 正常 |
| 148 | `VN-LOC-14-DD-E` | **Sở Xây dựng Thành phố Đà Nẵng** | E | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-14-DD-E 档案卡](dossiers/VN-LOC-14-DD-E-VN_DD_SXD.md) | HTTP 200 正常 |
| 149 | `VN-LOC-15-KH-A` | **Cổng Thông tin điện tử tỉnh Khánh Hòa** | A | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-15-KH-A 档案卡](dossiers/VN-LOC-15-KH-A-VN_KH_PORTAL.md) | HTTP 200 正常 |
| 150 | `VN-LOC-15-KH-B` | **Ban Quản lý Khu kinh tế Vân Phong và các KCN Khánh Hòa** | B | HTML Card / Semantic List | 工业园区一线动态 | [VN-LOC-15-KH-B 档案卡](dossiers/VN-LOC-15-KH-B-VN_KH_VANPHONG.md) | HTTP 200 正常 |
| 151 | `VN-LOC-15-KH-C` | **Sở Tài chính Tỉnh Khánh Hòa** | C | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-15-KH-C 档案卡](dossiers/VN-LOC-15-KH-C-VN_KH_STC.md) | HTTP 200 正常 |
| 152 | `VN-LOC-15-KH-D` | **Sở Nông nghiệp và Môi trường tỉnh Khánh Hòa** | D | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-15-KH-D 档案卡](dossiers/VN-LOC-15-KH-D-VN_KH_SNNMT.md) | HTTP 200 正常 |
| 153 | `VN-LOC-15-KH-E` | **Sở Xây dựng Khánh Hòa** | E | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-15-KH-E 档案卡](dossiers/VN-LOC-15-KH-E-VN_KH_SXD.md) | HTTP 200 正常 |
| 154 | `VN-LOC-16-HT-A` | **Cổng thông tin điện tử tỉnh Hà Tĩnh** | A | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-16-HT-A 档案卡](dossiers/VN-LOC-16-HT-A-VN_HT_PORTAL.md) | HTTP 200 正常 |
| 155 | `VN-LOC-16-HT-B` | **Ban Quản lý Khu kinh tế tỉnh Hà Tĩnh (KKT Vũng Áng)** | B | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-16-HT-B 档案卡](dossiers/VN-LOC-16-HT-B-VN_HT_KKT.md) | HTTP 200 正常 |
| 156 | `VN-LOC-16-HT-C` | **Sở Tài chính tỉnh Hà Tĩnh** | C | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-16-HT-C 档案卡](dossiers/VN-LOC-16-HT-C-VN_HT_SOTC.md) | HTTP 200 正常 |
| 157 | `VN-LOC-16-HT-D` | **Sở Nông nghiệp và Môi trường Hà Tĩnh** | D | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-16-HT-D 档案卡](dossiers/VN-LOC-16-HT-D-VN_HT_SONNMT.md) | HTTP 200 正常 |
| 158 | `VN-LOC-16-HT-E` | **Sở Xây Dựng Hà Tĩnh** | E | HTML Card / Semantic List | 综合市场动态 | [VN-LOC-16-HT-E 档案卡](dossiers/VN-LOC-16-HT-E-VN_HT_SOXD.md) | HTTP 200 正常 |
| 159 | `VN-LOC-17-TH-INV` | **Cổng Thông tin xúc tiến đầu tư tỉnh Thanh Hóa (Invest in Thanh Hóa)** | Standalone | HTML Card / Semantic List | FDI 外资投资动向 | [VN-LOC-17-TH-INV 档案卡](dossiers/VN-LOC-17-TH-INV-VN_TH_INVEST.md) | HTTP 200 正常 |
| 160 | `SRC-DISC-01` | **巨潮资讯网 (CNINFO)** | Enterprise Disclosure | REST API (JSON Search) | FDI (母公司重大决议) | [SRC-DISC-01 档案卡](dossiers/SRC-DISC-01-cninfo.md) | HTTP 200 正常 |
| 161 | `SRC-DISC-02` | **上海证券交易所 (上交所 / SSE)** | Enterprise Disclosure | Portal Search Column (Mirror on CNINFO) | FDI (母公司重大决议) | [SRC-DISC-02 档案卡](dossiers/SRC-DISC-02-sse.md) | HTTP 200 正常 |
| 162 | `SRC-DISC-03` | **深圳证券交易所 (深交所 / SZSE)** | Enterprise Disclosure | REST API (JSON Search) | FDI (母公司重大决议) | [SRC-DISC-03 档案卡](dossiers/SRC-DISC-03-szse.md) | HTTP 200 正常 |
| 163 | `SRC-DISC-04` | **北京证券交易所 (北交所 / BSE)** | Enterprise Disclosure | Portal Column (403 on infoResult.do / Mirror on CNINFO) | FDI (母公司重大决议) | [SRC-DISC-04 档案卡](dossiers/SRC-DISC-04-bse.md) | HTTP 200 正常 |
| 164 | `SRC-DISC-05` | **港交所披露易 (HKEXnews)** | Enterprise Disclosure | REST API (JSON SearchServlet) | FDI (母公司重大决议) | [SRC-DISC-05 档案卡](dossiers/SRC-DISC-05-hkexnews.md) | HTTP 200 正常 |
| 165 | `SRC-DISC-06` | **台湾公开资讯观测站 (MOPS)** | Enterprise Disclosure | Automated Request Denied (TWSE Firewall) | FDI (母公司重大决议) | [SRC-DISC-06 档案卡](dossiers/SRC-DISC-06-mops.md) | HTTP 200 正常 |
| 166 | `SRC-DISC-07` | **新加坡交易所公司公告 (SGX)** | Enterprise Disclosure | Angular SPA Portal (CSR Dynamic Loading) | FDI (母公司重大决议) | [SRC-DISC-07 档案卡](dossiers/SRC-DISC-07-sgx.md) | HTTP 200 正常 |
| 167 | `SRC-DISC-08` | **韩国金融监督院 (DART)** | Enterprise Disclosure | HTML Table (Direct Homepage Disclosures) | FDI (母公司重大决议) | [SRC-DISC-08 档案卡](dossiers/SRC-DISC-08-dart.md) | HTTP 200 正常 |
| 168 | `SRC-DISC-09` | **东京证券交易所 (JPX / TDnet)** | Enterprise Disclosure | HTML Table (Daily Timely Disclosure List) | FDI (母公司重大决议) | [SRC-DISC-09 档案卡](dossiers/SRC-DISC-09-jpx_tdnet.md) | HTTP 200 正常 |
| 169 | `SRC-DISC-10` | **美国证券交易委员会 EDGAR (SEC EDGAR)** | Enterprise Disclosure | REST API (EFTS Search Index) | FDI (母公司重大决议) | [SRC-DISC-10 档案卡](dossiers/SRC-DISC-10-sec_edgar.md) | HTTP 200 正常 |
| 170 | `SRC-DISC-11` | **印度国家证券交易所 (NSE)** | Enterprise Disclosure | Automated Access Blocked (Akamai WAF 403) | FDI (母公司重大决议) | [SRC-DISC-11 档案卡](dossiers/SRC-DISC-11-nse_india.md) | HTTP 403 需穿透 |
| 171 | `SRC-DISC-12` | **印度孟买证券交易所 (BSE India)** | Enterprise Disclosure | Automated Access Blocked (WAF 403) | FDI (母公司重大决议) | [SRC-DISC-12 档案卡](dossiers/SRC-DISC-12-bse_india.md) | HTTP 403 需穿透 |
| 172 | `SRC-DISC-13` | **企业自有信披代表 (Elmet IR / 涉越跨国投资典型)** | Enterprise Disclosure | HTML List (Investor Relations Releases) | FDI (母公司重大决议) | [SRC-DISC-13 档案卡](dossiers/SRC-DISC-13-elmet_ir.md) | HTTP 200 正常 |
| 173 | `SRC-ASSOC-01` | **越南纺织服装协会 (VITAS)** | Industry Association | HTML List (HTTP Fallback / Legacy TLS) | 重点关注产业专题 | [SRC-ASSOC-01 档案卡](dossiers/SRC-ASSOC-01-vitas.md) | HTTP 200 正常 |
| 174 | `SRC-ASSOC-02` | **越南电子工业协会 (VEIA)** | Industry Association | Portal Access (LiteSpeed Anti-Bot on Subpages) | 重点关注产业专题 | [SRC-ASSOC-02 档案卡](dossiers/SRC-ASSOC-02-veia.md) | HTTP 200 正常 |
| 175 | `SRC-ASSOC-03` | **越南物流服务企业协会 (VLA)** | Industry Association | HTML Card / Semantic List | 重点关注产业专题 | [SRC-ASSOC-03 档案卡](dossiers/SRC-ASSOC-03-vla.md) | HTTP 200 正常 |
| 176 | `SRC-ASSOC-04` | **越南工商业联合会 (VCCI)** | Industry Association | HTML Card / Semantic List | 重点关注产业专题 | [SRC-ASSOC-04 档案卡](dossiers/SRC-ASSOC-04-vcci.md) | HTTP 200 正常 |
| 177 | `SRC-ASSOC-05` | **涉外专业律所投资专栏 (Vilasia / 越南外资法律洞察)** | Industry Association | HTML List (Professional Legal Insights) | 重点关注产业专题 | [SRC-ASSOC-05 档案卡](dossiers/SRC-ASSOC-05-vilasia.md) | HTTP 200 正常 |
| 178 | `SRC-ASSOC-06` | **新加坡工商联合会 (SBF)** | Industry Association | Automated Access Blocked (Cloudflare WAF 403) | 重点关注产业专题 | [SRC-ASSOC-06 档案卡](dossiers/SRC-ASSOC-06-sbf.md) | HTTP 403 需穿透 |
| 179 | `SRC-ASSOC-07` | **新加坡制造业总会 (SMF)** | Industry Association | Native RSS 2.0 Feed | 重点关注产业专题 | [SRC-ASSOC-07 档案卡](dossiers/SRC-ASSOC-07-smf.md) | HTTP 200 正常 |
| 180 | `SRC-INTL-01` | **世界银行越南专页与IFC项目 (World Bank Vietnam / IFC)** | International Development | HTML List (Official Publications & Project Briefs) | 综合市场动态 | [SRC-INTL-01 档案卡](dossiers/SRC-INTL-01-worldbank_vn.md) | HTTP 200 正常 |
| 181 | `SRC-INTL-02` | **亚洲开发银行 (ADB Vietnam Projects)** | International Development | Automated Access Blocked (Cloudflare WAF 403) | 综合市场动态 | [SRC-INTL-02 档案卡](dossiers/SRC-INTL-02-adb_vn.md) | HTTP 403 需穿透 |
| 182 | `SRC-INTL-03` | **亚洲基础设施投资银行 (AIIB Projects)** | International Development | Static JavaScript Dataset (JSON Evaluation) | 综合市场动态 | [SRC-INTL-03 档案卡](dossiers/SRC-INTL-03-aiib_projects.md) | HTTP 200 正常 |
| 183 | `SRC-SUPP-01` | **企业官方通稿台: 美通社亚太 (PR Newswire)** | Supplementary Channel | HTML List (Corporate Press Release Feed) | 综合市场动态 | [SRC-SUPP-01 档案卡](dossiers/SRC-SUPP-01-pr_newswire.md) | HTTP 200 正常 |
| 184 | `SRC-SUPP-02` | **企业官方通稿台: Media OutReach / EtNet 转载入口** | Supplementary Channel | HTML List (Global PR Distribution) | 综合市场动态 | [SRC-SUPP-02 档案卡](dossiers/SRC-SUPP-02-media_outreach.md) | HTTP 200 正常 |
| 185 | `SRC-SUPP-03` | **中文商业与转载: 新浪财经** | Supplementary Channel | HTML List (Major News Portal Syndication) | 综合市场动态 | [SRC-SUPP-03 档案卡](dossiers/SRC-SUPP-03-sina_finance.md) | HTTP 200 正常 |
| 186 | `SRC-SUPP-04` | **中文商业与转载: 腾讯新闻** | Supplementary Channel | Portal Access (CSR Dynamic Content) | 综合市场动态 | [SRC-SUPP-04 档案卡](dossiers/SRC-SUPP-04-tencent_news.md) | HTTP 200 正常 |
| 187 | `SRC-SUPP-05` | **中文商业与转载: 网易财经** | Supplementary Channel | HTML List (Portal Syndication) | 综合市场动态 | [SRC-SUPP-05 档案卡](dossiers/SRC-SUPP-05-netease_finance.md) | HTTP 200 正常 |
| 188 | `SRC-SUPP-06` | **中文商业与转载: 搜狐财经** | Supplementary Channel | HTML List (Portal Articles) | 综合市场动态 | [SRC-SUPP-06 档案卡](dossiers/SRC-SUPP-06-sohu_finance.md) | HTTP 200 正常 |
| 189 | `SRC-SUPP-07` | **中文商业与转载: EtNet 经济通** | Supplementary Channel | HTML List (HK Financial Portal) | 综合市场动态 | [SRC-SUPP-07 档案卡](dossiers/SRC-SUPP-07-etnet.md) | HTTP 200 正常 |
| 190 | `SRC-SUPP-08` | **中文商业与转载: 越南中文社 / 越南网 (yuenan.com)** | Supplementary Channel | HTML List (Local Chinese Community News) | 综合市场动态 | [SRC-SUPP-08 档案卡](dossiers/SRC-SUPP-08-yuenan_zhongwen.md) | HTTP 200 正常 |
| 191 | `SRC-SUPP-09` | **中文商业与转载: Vietnam.vn (越南官方汇聚多语种门户)** | Supplementary Channel | HTML List (Official Multi-Language Aggregation Portal) | 综合市场动态 | [SRC-SUPP-09 档案卡](dossiers/SRC-SUPP-09-vietnam_vn.md) | HTTP 200 正常 |
| 192 | `SRC-SUPP-10` | **待定位新闻入口: Longbridge (长桥证券)** | Supplementary Channel | React SPA Shell (<div id='root'></div> / In-App API Required) | 综合市场动态 | [SRC-SUPP-10 档案卡](dossiers/SRC-SUPP-10-longbridge.md) | HTTP 200 正常 |
| 193 | `SRC-SUPP-11` | **社交平台官方主页: 越南政府 Facebook (Thông tin Chính phủ)** | Supplementary Channel | Automated Access Blocked (Meta Anti-Crawler 400 Bad Request) | 综合市场动态 | [SRC-SUPP-11 档案卡](dossiers/SRC-SUPP-11-fb_chinhphu.md) | HTTP 400 需穿透 |
| 194 | `SRC-SUPP-12` | **社交平台官方主页: VnExpress Facebook (Cộng đồng VnExpress)** | Supplementary Channel | Automated Access Blocked (Meta Anti-Crawler 400 Bad Request) | 综合市场动态 | [SRC-SUPP-12 档案卡](dossiers/SRC-SUPP-12-fb_vnexpress.md) | HTTP 400 需穿透 |
| 195 | `SRC-SUPP-13` | **社交平台官方主页: Báo Đầu tư Facebook (Báo Đầu tư Online)** | Supplementary Channel | Automated Access Blocked (Meta Anti-Crawler 400 Bad Request) | 综合市场动态 | [SRC-SUPP-13 档案卡](dossiers/SRC-SUPP-13-fb_baodautu.md) | HTTP 400 需穿透 |
| 196 | `SRC-SUPP-14` | **备用渠道: 企业微信公众号 (搜狗微信搜索备用入口)** | Supplementary Channel | HTML List (Sogou Weixin Search Aggregator) | 综合市场动态 | [SRC-SUPP-14 档案卡](dossiers/SRC-SUPP-14-wechat_mp.md) | HTTP 200 正常 |
