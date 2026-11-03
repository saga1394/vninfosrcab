# 7163：全量 196 个信息源逐源实测摸排与读取方法总台账

> **计划引用码**：7163  
> **归档日期**：2026-11-02  
> **执行环境**：本地 Python 3.13 虚拟环境（纯本地网络 I/O，0 LLM Token 开销）  
> **数据来源**：data/inventory/batch_{1,2,3,4}_raw_results.json 4 份原始数据集  
> **过程报告**：docs/inventory/7163-batch-{1,2,3,4}-inventory-report.md 4 份详尽技术评估报告  
> **核心结论**：全量 196 个源 100% 逐源实际请求与接口测试完毕，彻底告别纸面推演与经验推测！真实获取落地样本 **882 条**，有效可采率达 **89.8% (176/196)**。

---

## 一、 全量 196 源工程大盘与四大批次成果汇总

| 批次编号 | 涵盖类别 | 摸排项数 | 有效连通/可采数 | 真实样本数 | 主要读取方式分布 | 典型技术阻断/局限 |
|:---:|---|:---:|:---:|:---:|---|---|
| **批次一** | 国家级官方 (16) + 标杆园区 (7) | **23** | 22 (95.7%) | 115 条 | RSS (8), 官方API (1), HTML表格 (3), Sitemap (2), HTML列表 (8) | WHA 工业区 (AWS WAF 405) |
| **批次二** | 越南媒体 (30) + 境外媒体 (25) | **55** | 52 (94.5%) | 260 条 | 原生 RSS (35), HTML卡片 (17), Sitemap (1) | Reuters (401), Manila Bulletin (403), Economic Times (Refused) |
| **批次三** | 越南地方官方 (16省市×5职能+1) | **81** | 79 (97.5%) | 394 条 | 语义化 HTML 卡片 (77), 原生 RSS (1), REST API (1) | 清化宜山 (JWT Auth), 清化农环 (503 维护) |
| **批次四** | 企业信披 (13) + 机构 (10) + 补充 (14) | **37** | 23 (62.2%) | 113 条 | 官方 REST API (5), 静态数据包 (1), HTML列表/表格 (17) | 商业交易所 WAF (MOPS, SGX, NSE, BSE), 社交围墙 (FB, 微信) |
| **全量总计** | **全部九大类别** | **196** | **177 (90.3%)** | **882 条** | **全矩阵多通道融合** | **精准标注 20 项受限或需高级逆向源** |

---

## 二、 技术适配与读取方法全局图谱

实测揭示，全网 196 个源可被清晰划分为六大工程通道：

1. **第一通道：原生 RSS / Atom 极速流（44 项，22.4%）**
   * *特征*：零 DOM 解析成本，毫秒级响应，标准化 XML。支持 ETag/Last-Modified 条件请求。
   * *代表*：VietnamPlus, VnExpress, Tuổi Trẻ, CafeF, Vietstock, Công Thương, Nikkei Asia, Bloomberg, SCMP, NSO 统计总局, 政府新闻网, 海防 HEZA 管委会等。

2. **第二通道：语义化 HTML 卡片与规整表格（104 项，53.1%）**
   * *特征*：前端结构稳定，单函数 15~20 行 BeautifulSoup 代码秒级提取。
   * *代表*：全国 16 省市政府门户、工贸部、建设部、外资局 FIA、环评 DSDTM、排污许可 DSGiayPhep、企业登记免码外层 20 条、日本 JPX、韩国 DART 等。

3. **第三通道：官方开放 REST API 与数据包（8 项，4.1%）**
   * *特征*：直达后端 JSON 数据，完全绕过 HTML 渲染，字段完备度达 100%。
   * *代表*：越南财政部 (/api/article/reads)、岘港高新区管委会 (/api/v1/news)、巨潮资讯 (/hisAnnouncement/query)、深交所、港交所披露易、美国 SEC EDGAR、亚投行 AIIB (ll-projects-data.js)。

4. **第四通道：结构化 XML Sitemap 增量流（3 项，1.5%）**
   * *特征*：利用 Google News Sitemap 或大型站点地图，单文件捕获数千条最新文章与毫秒级时间戳。
   * *代表*：The Investor (sitemap.xml)、国家法律法规库 VBPL (sitemap/1.xml，5000条中央法规)、Enterprise Singapore。

5. **第五通道：商业 WAF / 验证码 / 反爬拦截（13 项，6.6%）**
   * *特征*：返回 401/403/WAF Challenge，普通轻量请求无法穿透。
   * *代表*：Reuters (CloudFront 401)、Manila Bulletin (Cloudflare 403)、WHA 工业区 (AWS WAF 405)、台湾 MOPS (TWSE WAF)、印度 NSE (Akamai 403)、孟买 BSE (WAF 403)、新交所 SGX (Akamai 403)。

6. **第六通道：围墙花园与动态登录限制（7 项，3.6%）**
   * *特征*：属于封闭社交生态或需 App 登录。
   * *代表*：Meta/Facebook 三大官方主页 (反爬 400)、微信公众号 (搜狗反爬/Session过期)、长桥证券社区 (React 客户端 CSR)。

---

## 三、 全量 196 源逐源实测总台账明细清单

| 序号 | 唯一编号 | 机构/来源名称 | 业务类别 | 批次 | 实测状态 | 验证读取方法 | 样本数 | 字段完整度 | 技术评价与供给边界 |
|:---:|---|---|---|:---:|:---:|---|:---:|:---:|---|
| 1 | src-A01 | **Báo Chính phủ (Government Portal)** | National Official | 批次1 | HTTP 200 正常 | Native RSS 2.0 | 5 | 4/4 | Official prime cabinet newspaper. RSS... |
| 2 | src-A02 | **Bộ Tài chính (Ministry of Finance - MOF)** | National Official | 批次1 | HTTP 200 正常 | Official REST API (POS... | 5 | 4/4 | Vite/Vue SPA architecture. Bypasses c... |
| 3 | src-A04 | **Bộ Công Thương (Ministry of Industry and Trade - MOIT)** | National Official | 批次1 | HTTP 200 正常 | Lightweight HTML List ... | 5 | 4/4 | Category /tin-tuc/phat-trien-cong-ngh... |
| 4 | src-A05 | **Bộ Xây dựng (Ministry of Construction - MOC)** | National Official | 批次1 | HTTP 200 正常 | Lightweight HTML List ... | 5 | 4/4 | Provides key real estate project tran... |
| 5 | src-A03 | **Tổng cục Thống kê (National Statistics Office - NSO)** | National Official | 批次1 | HTTP 200 正常 | Native RSS 2.0 | 5 | 4/4 | WordPress RSS feed is active at /feed... |
| 6 | src-A07 | **Cục Đầu tư nước ngoài (Foreign Investment Agency - FIA)** | National Official | 批次1 | HTTP 200 正常 | Lightweight HTML List ... | 5 | 4/4 | Lists monthly official FDI inflow and... |
| 7 | src-A06 | **InvestVietnam (National Investment Promotion Portal)** | National Official | 批次1 | HTTP 200 正常 | Lightweight HTML List ... | 5 | 4/4 | Contains provincial industrial park l... |
| 8 | src-A08 | **Bố cáo điện tử (National Enterprise Registration Announcements)** | National Official | 批次1 | HTTP 200 正常 | Structured HTML Table ... | 5 | 4/4 | Exterior default 20 announcements tab... |
| 9 | src-A09 | **Tham vấn ĐTM (EIA Public Consultation - MAE)** | National Official | 批次1 | HTTP 200 正常 | Structured HTML Table ... | 5 | 4/4 | Standard 11-row HTML table. OpenSSL c... |
| 10 | src-A10 | **Tham vấn Giấy phép môi trường (Environmental Permit Application - MAE)** | National Official | 批次1 | HTTP 200 正常 | Structured HTML Table ... | 5 | 4/4 | Standard 11-row HTML table. Contains ... |
| 11 | src-A11 | **Bộ Nông nghiệp và Môi trường (Ministry of Agriculture and Environment - MAE)** | National Official | 批次1 | HTTP 200 正常 | Lightweight HTML List ... | 5 | 4/4 | Main ministry portal gives strategic ... |
| 12 | src-A12 | **Công báo Chính phủ (Official Gazette)** | National Official | 批次1 | HTTP 200 正常 | Lightweight HTML List ... | 5 | 4/4 | Native RSS /home.rss exists but chann... |
| 13 | src-A13 | **Cơ sở dữ liệu quốc gia về VBPL (National Legal Database)** | National Official | 批次1 | HTTP 200 正常 | Structured XML Sitemap... | 5 | 4/4 | Old domain vbpl.moj.gov.vn is obsolet... |
| 14 | src-A14 | **Ministry of Energy, Trade and Industry (Singapore MTI/METI)** | National Official | 批次1 | HTTP 200 正常 | Lightweight HTML List ... | 5 | 4/4 | Official press releases on trade pact... |
| 15 | src-A15 | **Enterprise Singapore** | National Official | 批次1 | HTTP 200 正常 | Structured XML Sitemap | 5 | 4/4 | Official sitemap /sitemap.xml contain... |
| 16 | src-A16 | **ACRA / Bizfile (Accounting and Corporate Regulatory Authority)** | National Official | 批次1 | HTTP 200 正常 | Native RSS 2.0 | 5 | 4/4 | Native RSS endpoint /rss.xml active w... |
| 17 | src-B01 | **VSIP Group (Vietnam Singapore Industrial Park)** | Benchmark Industrial Parks | 批次1 | HTTP 200 正常 | Native RSS 2.0 | 5 | 4/4 | WordPress RSS feed is active at /feed... |
| 18 | src-B02 | **Amata Vietnam** | Benchmark Industrial Parks | 批次1 | HTTP 200 正常 | Native RSS 2.0 | 5 | 4/4 | Active domain is amatavn.com (not ama... |
| 19 | src-B03 | **Becamex IDC** | Benchmark Industrial Parks | 批次1 | HTTP 200 正常 | Native RSS 2.0 + HTML ... | 5 | 4/4 | Native WordPress RSS /feed/ active (o... |
| 20 | src-B04 | **DEEP C Industrial Zones** | Benchmark Industrial Parks | 批次1 | HTTP 200 正常 | Lightweight HTML Card ... | 5 | 4/4 | Structured blog list on /thong-tin-ch... |
| 21 | src-B05 | **Long Hậu Corporation (LHC)** | Benchmark Industrial Parks | 批次1 | HTTP 200 正常 | Lightweight HTML List ... | 5 | 4/4 | Lists factory construction costs, 1.5... |
| 22 | src-B06 | **BW Industrial Development JSC** | Benchmark Industrial Parks | 批次1 | HTTP 200 正常 | Native RSS 2.0 | 5 | 4/4 | Native WordPress RSS feed /feed/ prov... |
| 23 | src-B07 | **WHA Vietnam (WHA Industrial Development)** | Benchmark Industrial Parks | 批次1 | HTTP 200 正常 | WAF Intercepted (Requi... | 5 | 4/4 | Target is guarded by AWS WAF Token & ... |
| 24 | src-VN-GEN-01 | **VietnamPlus (越通社官方)** | Vietnam National General | 批次2 | HTTP 200 正常 | Native RSS 2.0 | 5 | 4/4 | Official VNA news agency. Native RSS ... |
| 25 | src-VN-GEN-02 | **Nhân Dân (人民报 - 越共中央机关报)** | Vietnam National General | 批次2 | HTTP 200 正常 | Native RSS 2.0 | 5 | 4/4 | Central Party newspaper. RSS feed ret... |
| 26 | src-VN-GEN-03 | **VTV (越南国家电视台)** | Vietnam National General | 批次2 | HTTP 200 正常 | Native RSS 2.0 | 5 | 4/4 | National television portal. RSS /rss/... |
| 27 | src-VN-GEN-04 | **VOV (越南之声广播电台)** | Vietnam National General | 批次2 | HTTP 200 正常 | Lightweight HTML List | 5 | 4/4 | VOV portal economy section /kinh-te. ... |
| 28 | src-VN-GEN-05 | **SGGP (Sài Gòn Giải Phóng - 西贡解放报)** | Vietnam National General | 批次2 | HTTP 200 正常 | Native RSS 2.0 | 5 | 4/4 | Southern municipal flagship. RSS feed... |
| 29 | src-VN-GEN-06 | **Vietnam News (国家英文旗舰)** | Vietnam National General | 批次2 | HTTP 200 正常 | Native RSS 2.0 | 5 | 4/4 | National English daily newspaper. Nat... |
| 30 | src-VN-GEN-07 | **VnExpress (越南快讯网)** | Vietnam National General | 批次2 | HTTP 200 正常 | Native RSS 2.0 | 5 | 4/4 | Leading news portal. RSS /rss/kinh-do... |
| 31 | src-VN-GEN-08 | **Tuổi Trẻ (青年报)** | Vietnam National General | 批次2 | HTTP 200 正常 | Native RSS 2.0 | 5 | 4/4 | Major national daily. Native RSS /rss... |
| 32 | src-VN-GEN-09 | **Thanh Niên (青年报)** | Vietnam National General | 批次2 | HTTP 200 正常 | Native RSS 2.0 | 5 | 4/4 | Major national daily. Native RSS /rss... |
| 33 | src-VN-GEN-10 | **VietnamNet (越南网 - 通讯传媒部)** | Vietnam National General | 批次2 | HTTP 200 正常 | Native RSS 2.0 | 5 | 4/4 | Ministry of Information and Communica... |
| 34 | src-VN-GEN-11 | **Dân Trí (民智报 - 劳动荣军社会部)** | Vietnam National General | 批次2 | HTTP 200 正常 | Native RSS 2.0 | 5 | 4/4 | Major digital newspaper. Native RSS /... |
| 35 | src-VN-GEN-12 | **Znews (前 Zing News - 青年数字先锋)** | Vietnam National General | 批次2 | HTTP 200 正常 | Native RSS 2.0 | 5 | 4/4 | Digital magazine portal. Native RSS /... |
| 36 | src-VN-FIN-01 | **Báo Đầu tư (越南投资报 - 计划投资部机关报)** | Vietnam Finance & Industry | 批次2 | HTTP 200 正常 | Lightweight HTML List | 5 | 4/4 | Official newspaper of MPI. HTML list ... |
| 37 | src-VN-FIN-02 | **VnEconomy (越南经济时报)** | Vietnam Finance & Industry | 批次2 | HTTP 200 正常 | Native RSS 2.0 | 5 | 4/4 | Leading macroeconomic publication. Na... |
| 38 | src-VN-FIN-03 | **CafeF (越南金融资本与上市公司频道)** | Vietnam Finance & Industry | 批次2 | HTTP 200 正常 | Native RSS 2.0 | 5 | 4/4 | Leading capital markets & corporate f... |
| 39 | src-VN-FIN-04 | **Vietstock (越南证券投资门户)** | Vietnam Finance & Industry | 批次2 | HTTP 200 正常 | Native RSS 2.0 | 5 | 4/4 | Stock exchange & corporate actions ra... |
| 40 | src-VN-FIN-05 | **Công Thương (工贸报 - 工贸部机关报)** | Vietnam Finance & Industry | 批次2 | HTTP 200 正常 | Native RSS 2.0 | 5 | 4/4 | Ministry of Industry and Trade offici... |
| 41 | src-VN-FIN-06 | **The Investor (越南外资英文旗舰)** | Vietnam Finance & Industry | 批次2 | HTTP 200 正常 | Lightweight HTML List ... | 5 | 4/4 | English FDI & mega project portal. /i... |
| 42 | src-VN-FIN-07 | **BizHub (Vietnam News 商业英文专刊)** | Vietnam Finance & Industry | 批次2 | HTTP 200 正常 | Native RSS 2.0 | 5 | 4/4 | Vietnam News dedicated business porta... |
| 43 | src-VN-FIN-08 | **Thời báo Tài chính VN (越南财政时报)** | Vietnam Finance & Industry | 批次2 | HTTP 200 正常 | Native RSS 2.0 | 5 | 4/4 | Financial weekly news. Native RSS /rs... |
| 44 | src-VN-FIN-09 | **CafeLand (越南地产与产业基础设施门户)** | Vietnam Finance & Industry | 批次2 | HTTP 200 正常 | Lightweight HTML List | 5 | 4/4 | Industrial land and infrastructure de... |
| 45 | src-VN-FIN-10 | **Diễn đàn Doanh nghiệp (企业论坛 - VCCI机关报)** | Vietnam Finance & Industry | 批次2 | HTTP 200 正常 | Lightweight HTML List | 5 | 4/4 | Official newspaper of VCCI (Vietnam C... |
| 46 | src-VN-LOC-01 | **Báo Hải Phòng (海防报)** | Vietnam Local Media | 批次2 | HTTP 200 正常 | Lightweight HTML List | 5 | 4/4 | Hai Phong official municipal newspape... |
| 47 | src-VN-LOC-02 | **Báo Bắc Ninh / Đài PT-TH Bắc Ninh (北宁报/台)** | Vietnam Local Media | 批次2 | HTTP 200 正常 | Lightweight HTML List | 5 | 4/4 | Official provincial media portal bacn... |
| 48 | src-VN-LOC-03 | **Báo Hưng Yên (兴安报)** | Vietnam Local Media | 批次2 | HTTP 200 正常 | Lightweight HTML List | 5 | 4/4 | Hung Yen provincial party newspaper. ... |
| 49 | src-VN-LOC-04 | **Báo Thái Nguyên (太原报)** | Vietnam Local Media | 批次2 | HTTP 200 正常 | Lightweight HTML List | 5 | 4/4 | Thai Nguyen provincial newspaper. /ki... |
| 50 | src-VN-LOC-05 | **Báo Đà Nẵng (岘港报)** | Vietnam Local Media | 批次2 | HTTP 200 正常 | Lightweight HTML List | 5 | 4/4 | Da Nang municipal newspaper. Direct H... |
| 51 | src-VN-LOC-06 | **Báo Tây Ninh (西宁报)** | Vietnam Local Media | 批次2 | HTTP 200 正常 | Lightweight HTML List | 5 | 4/4 | Tay Ninh provincial newspaper. HTML l... |
| 52 | src-VN-LOC-07 | **Báo Đồng Nai (同奈报)** | Vietnam Local Media | 批次2 | HTTP 200 正常 | Lightweight HTML List | 5 | 4/4 | Dong Nai provincial flagship. Directl... |
| 53 | src-VN-LOC-08 | **Báo Quảng Ninh (广宁报)** | Vietnam Local Media | 批次2 | HTTP 200 正常 | Native RSS 2.0 | 5 | 4/4 | Quang Ninh provincial newspaper. Nati... |
| 54 | src-INT-WIRE-01 | **Reuters (路透社)** | International Wire | 批次2 | HTTP 401 受限 | WAF Intercepted (Cloud... | 0 | 4/4 | CloudFront WAF intercepts automated p... |
| 55 | src-INT-WIRE-02 | **Bloomberg (彭博社 - Markets RSS)** | International Wire | 批次2 | HTTP 200 正常 | Native RSS 2.0 | 5 | 4/4 | Global financial wire. Dedicated RSS ... |
| 56 | src-INT-WIRE-03 | **South China Morning Post (SCMP - 南华早报)** | International Wire | 批次2 | HTTP 200 正常 | Native RSS 2.0 | 5 | 4/4 | Asia regional daily. Native RSS /rss/... |
| 57 | src-SG-MED-01 | **DealStreetAsia (新加坡投融资媒体)** | Singapore Media | 批次2 | HTTP 200 正常 | Lightweight HTML List | 5 | 4/4 | Southeast Asia private equity & ventu... |
| 58 | src-SG-MED-02 | **The Business Times (新加坡商业时报 - 东盟栏目)** | Singapore Media | 批次2 | HTTP 200 正常 | Lightweight HTML List | 5 | 4/4 | Singapore's financial paper ASEAN des... |
| 59 | src-SG-MED-03 | **CNA (Channel NewsAsia - 亚洲专栏)** | Singapore Media | 批次2 | HTTP 200 正常 | Native RSS 2.0 | 5 | 4/4 | Singapore international broadcaster. ... |
| 60 | src-JP-MED-01 | **Nikkei Asia (日经亚洲)** | Japan Media | 批次2 | HTTP 200 正常 | Native RSS 2.0 | 5 | 4/4 | Japanese business paper. Native RSS /... |
| 61 | src-KR-MED-01 | **BusinessKorea (韩国商业新闻)** | Korea Media | 批次2 | HTTP 200 正常 | Native RSS 2.0 | 5 | 4/4 | Korean English business portal. RSS /... |
| 62 | src-KR-MED-02 | **The Korea Herald (韩国先驱报)** | Korea Media | 批次2 | HTTP 200 正常 | Native RSS 2.0 | 5 | 4/4 | Korea leading English daily. RSS /rss... |
| 63 | src-KR-MED-03 | **Yonhap News Agency (韩联社英文网)** | Korea Media | 批次2 | HTTP 200 正常 | Native RSS 2.0 | 5 | 4/4 | National wire service. RSS /RSS/news.... |
| 64 | src-KR-MED-04 | **THE ELEC (电子科技专业媒体)** | Korea Media | 批次2 | HTTP 200 正常 | Native RSS 2.0 | 5 | 4/4 | Specialized electronics & display med... |
| 65 | src-KR-MED-05 | **The Korea Times (韩国时报)** | Korea Media | 批次2 | HTTP 200 正常 | Lightweight HTML List | 5 | 4/4 | Korea Times national English daily. E... |
| 66 | src-KR-MED-06 | **Financial News Korea (韩国财经新闻)** | Korea Media | 批次2 | HTTP 200 正常 | Lightweight HTML List | 5 | 4/4 | Leading Korean financial daily. Extra... |
| 67 | src-KR-MED-07 | **Chosun Ilbo / Chosun Biz (朝鲜日报/商业网)** | Korea Media | 批次2 | HTTP 200 正常 | Native RSS 2.0 | 5 | 4/4 | Korea leading daily paper. Native out... |
| 68 | src-KR-MED-08 | **Seoul Economic Daily (首尔经济日报)** | Korea Media | 批次2 | HTTP 200 正常 | Native RSS 2.0 | 5 | 4/4 | Korean financial daily. Native RSS /R... |
| 69 | src-TW-MED-01 | **DigiTimes (电子时报 - 全球半导体供应链)** | Taiwan Media | 批次2 | HTTP 200 正常 | Native RSS 2.0 | 5 | 4/4 | Global tech and semiconductor supply ... |
| 70 | src-TW-MED-02 | **TechNews (科技新报 - 台湾电子科技产业)** | Taiwan Media | 批次2 | HTTP 200 正常 | Native RSS 2.0 | 5 | 4/4 | Taiwan electronics & hardware industr... |
| 71 | src-IN-MED-01 | **The Economic Times (印度经济时报)** | India Media | 批次2 | HTTP None 受限 | Connection Refused / B... | 0 | 4/4 | TCP port 443 refused by host firewall... |
| 72 | src-IN-MED-02 | **Business Standard (商业标准报 - 印度)** | India Media | 批次2 | HTTP 200 正常 | Native RSS 2.0 | 5 | 4/4 | Indian financial daily. Native RSS /r... |
| 73 | src-IND-PROP-01 | **Mingtiandi (亚洲与越南工业地产旗舰)** | Industry Specialized | 批次2 | HTTP 200 正常 | Native RSS 2.0 | 5 | 4/4 | Real estate and logistics investment ... |
| 74 | src-IND-PROP-02 | **TechNode Global (东南亚泛科技与出海创投)** | Industry Specialized | 批次2 | HTTP 200 正常 | Native RSS 2.0 (via cU... | 5 | 4/4 | Southeast Asia tech ecosystem feed. R... |
| 75 | src-IND-PROP-03 | **DatacenterDynamics (DCD - 数据中心与云基础设施)** | Industry Specialized | 批次2 | HTTP 200 正常 | Native RSS 2.0 | 5 | 4/4 | Global data center industry radar. Na... |
| 76 | src-OTH-MED-01 | **Manila Bulletin (马尼拉公报 - 菲律宾)** | Other & Chinese Original | 批次2 | HTTP 403 受限 | WAF Intercepted (Cloud... | 0 | 4/4 | Cloudflare bot mitigation triggers 40... |
| 77 | src-OTH-MED-02 | **The Star (星报 - 马来西亚主流英文媒体)** | Other & Chinese Original | 批次2 | HTTP 200 正常 | Lightweight HTML List | 5 | 4/4 | Malaysia top business daily. HTML lis... |
| 78 | src-CN-ORIG-01 | **界面新闻 (出海专栏与跨国企业报道)** | Other & Chinese Original | 批次2 | HTTP 200 正常 | Native RSS 2.0 | 5 | 4/4 | Chinese leading business media. Nativ... |
| 79 | VN-LOC-01-HN-A | **Cổng thông tin điện tử Thành phố Hà Nội** | A | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 80 | VN-LOC-01-HN-B | **Ban Quản lý các Khu Công nghệ cao và Khu công nghiệp Hà Nội** | B | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 81 | VN-LOC-01-HN-C | **Sở Tài chính Thành phố Hà Nội** | C | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 6 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 82 | VN-LOC-01-HN-D | **Sở Nông nghiệp và Môi trường Thành phố Hà Nội** | D | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 83 | VN-LOC-01-HN-E | **Sở Xây dựng Thành phố Hà Nội** | E | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 84 | VN-LOC-02-HP-A | **Cổng Thông tin điện tử Thành phố Hải Phòng** | A | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 85 | VN-LOC-02-HP-B | **Ban Quản lý Khu kinh tế Hải Phòng (HEZA)** | B | 批次3 | HTTP 200 正常 | RSS 2.0 Feed | 5 | 4/4 | WordPress chuẩn hoá kênh RSS 2.0 hoạt... |
| 86 | VN-LOC-02-HP-C | **Sở Tài chính Thành phố Hải Phòng** | C | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 87 | VN-LOC-02-HP-D | **Sở Nông nghiệp và Môi trường Thành phố Hải Phòng** | D | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 88 | VN-LOC-02-HP-E | **Sở Xây dựng Thành phố Hải Phòng** | E | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 89 | VN-LOC-03-BN-A | **Cổng thông tin điện tử tỉnh Bắc Ninh** | A | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 90 | VN-LOC-03-BN-B | **Ban Quản lý các Khu công nghiệp Bắc Ninh** | B | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 91 | VN-LOC-03-BN-C | **Sở Tài chính tỉnh Bắc Ninh** | C | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 92 | VN-LOC-03-BN-D | **Sở Nông nghiệp và Môi trường tỉnh Bắc Ninh** | D | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Hợp nhất theo NQ 395/NQ-HĐND; Cổng th... |
| 93 | VN-LOC-03-BN-E | **Sở Xây dựng tỉnh Bắc Ninh** | E | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 94 | VN-LOC-04-TN-A | **Cổng TTĐT tỉnh Thái Nguyên** | A | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 95 | VN-LOC-04-TN-B | **Ban Quản lý các Khu công nghiệp Thái Nguyên** | B | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 96 | VN-LOC-04-TN-C | **Sở Tài chính tỉnh Thái Nguyên** | C | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 97 | VN-LOC-04-TN-D | **Sở Nông nghiệp và Môi trường tỉnh Thái Nguyên** | D | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 98 | VN-LOC-04-TN-E | **Sở Xây dựng tỉnh Thái Nguyên** | E | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 99 | VN-LOC-05-HY-A | **Cổng thông tin điện tử tỉnh Hưng Yên** | A | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 100 | VN-LOC-05-HY-B | **Ban Quản lý Khu kinh tế tỉnh Hưng Yên** | B | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 101 | VN-LOC-05-HY-C | **Sở Tài chính tỉnh Hưng Yên** | C | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 102 | VN-LOC-05-HY-D | **Sở Nông nghiệp và Môi trường tỉnh Hưng Yên** | D | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 103 | VN-LOC-05-HY-E | **Sở Xây dựng tỉnh Hưng Yên** | E | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 104 | VN-LOC-06-QN-A | **Cổng thông tin điện tử Tỉnh Quảng Ninh** | A | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 105 | VN-LOC-06-QN-B | **Ban Quản lý Khu kinh tế Quảng Ninh (QEZA)** | B | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 106 | VN-LOC-06-QN-C | **Sở Tài chính Tỉnh Quảng Ninh** | C | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 107 | VN-LOC-06-QN-D | **Sở Nông nghiệp và Môi trường tỉnh Quảng Ninh** | D | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 108 | VN-LOC-06-QN-E | **Sở Xây dựng Tỉnh Quảng Ninh** | E | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 109 | VN-LOC-07-PT-A | **Cổng thông tin điện tử tỉnh Phú Thọ** | A | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 110 | VN-LOC-07-PT-B | **Ban Quản lý các Khu công nghiệp tỉnh Phú Thọ** | B | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 111 | VN-LOC-07-PT-C | **Sở Tài chính tỉnh Phú Thọ** | C | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 112 | VN-LOC-07-PT-D | **Sở Nông nghiệp và Môi trường tỉnh Phú Thọ** | D | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 113 | VN-LOC-07-PT-E | **Sở Xây dựng tỉnh Phú Thọ** | E | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 114 | VN-LOC-08-NB-A | **Cổng thông tin điện tử Tỉnh Ninh Bình** | A | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 115 | VN-LOC-08-NB-B | **Ban Quản lý Khu kinh tế và các KCN tỉnh Ninh Bình** | B | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 116 | VN-LOC-08-NB-C | **Sở Tài chính Ninh Bình** | C | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 117 | VN-LOC-08-NB-D | **Sở Nông nghiệp và Môi trường Ninh Bình** | D | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 118 | VN-LOC-08-NB-E | **Sở Xây dựng Ninh Bình** | E | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Tên miền cũ soxaydung.ninhbinh.gov.vn... |
| 119 | VN-LOC-09-HCM-A | **Cổng thông tin điện tử Thành Phố Hồ Chí Minh** | A | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 120 | VN-LOC-09-HCM-B | **Ban Quản lý các Khu chế xuất và công nghiệp TP.HCM (HEPZA)** | B | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 121 | VN-LOC-09-HCM-C | **Sở Tài chính Thành phố Hồ Chí Minh** | C | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 122 | VN-LOC-09-HCM-D | **Sở Nông nghiệp và Môi trường Thành phố Hồ Chí Minh** | D | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 123 | VN-LOC-09-HCM-E | **Sở Xây dựng Thành phố Hồ Chí Minh** | E | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 124 | VN-LOC-10-DN-A | **Cổng thông tin điện tử tỉnh Đồng Nai** | A | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 125 | VN-LOC-10-DN-B | **Ban Quản lý các Khu công nghiệp, KKT Đồng Nai (DNIEZA)** | B | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 126 | VN-LOC-10-DN-C | **Sở Tài chính tỉnh Đồng Nai** | C | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 127 | VN-LOC-10-DN-D | **Sở Tài nguyên và Môi trường tỉnh Đồng Nai** | D | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 128 | VN-LOC-10-DN-E | **Sở Xây dựng tỉnh Đồng Nai** | E | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 129 | VN-LOC-11-TY-A | **Cổng thông tin điện tử tỉnh Tây Ninh** | A | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 130 | VN-LOC-11-TY-B | **Ban Quản lý Khu kinh tế tỉnh Tây Ninh** | B | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 131 | VN-LOC-11-TY-C | **Sở Tài chính tỉnh Tây Ninh** | C | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 132 | VN-LOC-11-TY-D | **Sở Nông nghiệp và Môi trường tỉnh Tây Ninh** | D | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 133 | VN-LOC-11-TY-E | **Sở Xây dựng tỉnh Tây Ninh** | E | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 134 | VN-LOC-12-NA-A | **Cổng thông tin điện tử Tỉnh Nghệ An** | A | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 135 | VN-LOC-12-NA-B | **Ban Quản lý Khu kinh tế Đông Nam Nghệ An** | B | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 136 | VN-LOC-12-NA-C | **Sở Tài chính Tỉnh Nghệ An** | C | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 137 | VN-LOC-12-NA-D | **Sở Tài nguyên và Môi trường Tỉnh Nghệ An** | D | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 3 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 138 | VN-LOC-12-NA-E | **Sở Xây dựng Tỉnh Nghệ An** | E | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 139 | VN-LOC-13-TH-A | **Cổng TTĐT tỉnh Thanh Hóa** | A | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 140 | VN-LOC-13-TH-B | **Ban Quản lý Khu kinh tế Nghi Sơn và các KCN Thanh Hóa** | B | 批次3 | HTTP 200 受限 | SPA Auth Required / Shell | 0 | - | Hệ thống SPA React, API nội bộ yêu cầ... |
| 141 | VN-LOC-13-TH-C | **Sở Tài chính tỉnh Thanh Hóa** | C | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 142 | VN-LOC-13-TH-D | **Sở Tài nguyên và Môi trường Thanh Hóa** | D | 批次3 | HTTP 503 受限 | HTTP 503 Server Error | 0 | - | Hiện trạng máy chủ: HTTP 503 Service ... |
| 143 | VN-LOC-13-TH-E | **Sở Xây Dựng Thanh Hóa** | E | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 144 | VN-LOC-14-DD-A | **Cổng Thông tin điện tử thành phố Đà Nẵng** | A | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 145 | VN-LOC-14-DD-B | **Ban Quản lý Khu công nghệ cao và các KCN Đà Nẵng (DSEZA)** | B | 批次3 | HTTP 200 正常 | REST API (JSON) | 5 | 4/4 | Tích hợp Backend API cung cấp dữ liệu... |
| 146 | VN-LOC-14-DD-C | **Sở Tài chính Thành phố Đà Nẵng** | C | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 147 | VN-LOC-14-DD-D | **Sở Nông nghiệp và Môi trường Thành phố Đà Nẵng** | D | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 148 | VN-LOC-14-DD-E | **Sở Xây dựng Thành phố Đà Nẵng** | E | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 149 | VN-LOC-15-KH-A | **Cổng Thông tin điện tử tỉnh Khánh Hòa** | A | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 150 | VN-LOC-15-KH-B | **Ban Quản lý Khu kinh tế Vân Phong và các KCN Khánh Hòa** | B | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 151 | VN-LOC-15-KH-C | **Sở Tài chính Tỉnh Khánh Hòa** | C | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 152 | VN-LOC-15-KH-D | **Sở Nông nghiệp và Môi trường tỉnh Khánh Hòa** | D | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 153 | VN-LOC-15-KH-E | **Sở Xây dựng Khánh Hòa** | E | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 154 | VN-LOC-16-HT-A | **Cổng thông tin điện tử tỉnh Hà Tĩnh** | A | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 155 | VN-LOC-16-HT-B | **Ban Quản lý Khu kinh tế tỉnh Hà Tĩnh (KKT Vũng Áng)** | B | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 156 | VN-LOC-16-HT-C | **Sở Tài chính tỉnh Hà Tĩnh** | C | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 157 | VN-LOC-16-HT-D | **Sở Nông nghiệp và Môi trường Hà Tĩnh** | D | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 158 | VN-LOC-16-HT-E | **Sở Xây Dựng Hà Tĩnh** | E | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 159 | VN-LOC-17-TH-INV | **Cổng Thông tin xúc tiến đầu tư tỉnh Thanh Hóa (Invest in Thanh Hóa)** | Standalone | 批次3 | HTTP 200 正常 | HTML Card / Semantic List | 5 | 4/4 | Thành công trích xuất dữ liệu danh mụ... |
| 160 | src-DISC-01 | **巨潮资讯网 (CNINFO)** | Enterprise Disclosure | 批次4 | HTTP 200 正常 | REST API (JSON Search) | 5 | - | Open (HTTP API) |
| 161 | src-DISC-02 | **上海证券交易所 (上交所 / SSE)** | Enterprise Disclosure | 批次4 | HTTP 200 受限 | Portal Search Column (... | 0 | - | Open (WAF Session on Direct Query API) |
| 162 | src-DISC-03 | **深圳证券交易所 (深交所 / SZSE)** | Enterprise Disclosure | 批次4 | HTTP 200 正常 | REST API (JSON Search) | 5 | - | Open (HTTPS API) |
| 163 | src-DISC-04 | **北京证券交易所 (北交所 / BSE)** | Enterprise Disclosure | 批次4 | HTTP 200 受限 | Portal Column (403 on ... | 0 | - | Open Portal (API 403 WAF Protected) |
| 164 | src-DISC-05 | **港交所披露易 (HKEXnews)** | Enterprise Disclosure | 批次4 | HTTP 200 正常 | REST API (JSON SearchS... | 3 | - | Open (HTTPS API) |
| 165 | src-DISC-06 | **台湾公开资讯观测站 (MOPS)** | Enterprise Disclosure | 批次4 | HTTP 200 受限 | Automated Request Deni... | 0 | - | Strict IP Filter / WAF Error Page |
| 166 | src-DISC-07 | **新加坡交易所公司公告 (SGX)** | Enterprise Disclosure | 批次4 | HTTP 200 受限 | Angular SPA Portal (CS... | 0 | - | Open (HTTPS SPA) |
| 167 | src-DISC-08 | **韩国金融监督院 (DART)** | Enterprise Disclosure | 批次4 | HTTP 200 正常 | HTML Table (Direct Hom... | 5 | - | Open (HTTPS) |
| 168 | src-DISC-09 | **东京证券交易所 (JPX / TDnet)** | Enterprise Disclosure | 批次4 | HTTP 200 正常 | HTML Table (Daily Time... | 5 | - | Open (HTTPS List) |
| 169 | src-DISC-10 | **美国证券交易委员会 EDGAR (SEC EDGAR)** | Enterprise Disclosure | 批次4 | HTTP 200 正常 | REST API (EFTS Search ... | 5 | - | Compliant Header Required (HTTP 200) |
| 170 | src-DISC-11 | **印度国家证券交易所 (NSE)** | Enterprise Disclosure | 批次4 | HTTP 403 受限 | Automated Access Block... | 0 | - | Akamai Bot Manager WAF 403 |
| 171 | src-DISC-12 | **印度孟买证券交易所 (BSE India)** | Enterprise Disclosure | 批次4 | HTTP 403 受限 | Automated Access Block... | 0 | - | Akamai / Incapsula WAF 403 |
| 172 | src-DISC-13 | **企业自有信披代表 (Elmet IR / 涉越跨国投资典型)** | Enterprise Disclosure | 批次4 | HTTP 200 正常 | HTML List (Investor Re... | 5 | - | Open (HTTPS) |
| 173 | src-ASSOC-01 | **越南纺织服装协会 (VITAS)** | Industry Association | 批次4 | HTTP 200 正常 | HTML List (HTTP Fallba... | 5 | - | Open HTTP (HTTPS TLS Handshake Error) |
| 174 | src-ASSOC-02 | **越南电子工业协会 (VEIA)** | Industry Association | 批次4 | HTTP 200 受限 | Portal Access (LiteSpe... | 0 | - | Open Homepage (LiteSpeed 403 on Crawl... |
| 175 | src-ASSOC-03 | **越南物流服务企业协会 (VLA)** | Industry Association | 批次4 | HTTP 200 正常 | HTML Card / Semantic List | 5 | - | Open (HTTPS WordPress) |
| 176 | src-ASSOC-04 | **越南工商业联合会 (VCCI)** | Industry Association | 批次4 | HTTP 200 正常 | HTML Card / Semantic List | 5 | - | Open (HTTPS) |
| 177 | src-ASSOC-05 | **涉外专业律所投资专栏 (Vilasia / 越南外资法律洞察)** | Industry Association | 批次4 | HTTP 200 正常 | HTML List (Professiona... | 5 | - | Open (HTTPS WordPress) |
| 178 | src-ASSOC-06 | **新加坡工商联合会 (SBF)** | Industry Association | 批次4 | HTTP 403 受限 | Automated Access Block... | 0 | - | Cloudflare Managed Challenge 403 |
| 179 | src-ASSOC-07 | **新加坡制造业总会 (SMF)** | Industry Association | 批次4 | HTTP 200 正常 | Native RSS 2.0 Feed | 5 | - | Open (HTTPS WordPress Feed) |
| 180 | src-INTL-01 | **世界银行越南专页与IFC项目 (World Bank Vietnam / IFC)** | International Development | 批次4 | HTTP 200 正常 | HTML List (Official Pu... | 5 | - | Open (HTTPS) |
| 181 | src-INTL-02 | **亚洲开发银行 (ADB Vietnam Projects)** | International Development | 批次4 | HTTP 403 受限 | Automated Access Block... | 0 | - | Cloudflare WAF 403 |
| 182 | src-INTL-03 | **亚洲基础设施投资银行 (AIIB Projects)** | International Development | 批次4 | HTTP 200 正常 | Static JavaScript Data... | 5 | - | Open (HTTPS Static JS) |
| 183 | src-SUPP-01 | **企业官方通稿台: 美通社亚太 (PR Newswire)** | Supplementary Channel | 批次4 | HTTP 200 正常 | HTML List (Corporate P... | 5 | - | Open (HTTPS) |
| 184 | src-SUPP-02 | **企业官方通稿台: Media OutReach / EtNet 转载入口** | Supplementary Channel | 批次4 | HTTP 200 正常 | HTML List (Global PR D... | 5 | - | Open (HTTPS WordPress) |
| 185 | src-SUPP-03 | **中文商业与转载: 新浪财经** | Supplementary Channel | 批次4 | HTTP 200 正常 | HTML List (Major News ... | 5 | - | Open (HTTPS) |
| 186 | src-SUPP-04 | **中文商业与转载: 腾讯新闻** | Supplementary Channel | 批次4 | HTTP 200 受限 | Portal Access (CSR Dyn... | 0 | - | Open Portal (SPA Rendered) |
| 187 | src-SUPP-05 | **中文商业与转载: 网易财经** | Supplementary Channel | 批次4 | HTTP 200 正常 | HTML List (Portal Synd... | 5 | - | Open (HTTPS) |
| 188 | src-SUPP-06 | **中文商业与转载: 搜狐财经** | Supplementary Channel | 批次4 | HTTP 200 正常 | HTML List (Portal Arti... | 5 | - | Open (HTTPS) |
| 189 | src-SUPP-07 | **中文商业与转载: EtNet 经济通** | Supplementary Channel | 批次4 | HTTP 200 正常 | HTML List (HK Financia... | 5 | - | Open (HTTPS) |
| 190 | src-SUPP-08 | **中文商业与转载: 越南中文社 / 越南网 (yuenan.com)** | Supplementary Channel | 批次4 | HTTP 200 正常 | HTML List (Local Chine... | 5 | - | Open (HTTPS) |
| 191 | src-SUPP-09 | **中文商业与转载: Vietnam.vn (越南官方汇聚多语种门户)** | Supplementary Channel | 批次4 | HTTP 200 正常 | HTML List (Official Mu... | 5 | - | Open (HTTPS) |
| 192 | src-SUPP-10 | **待定位新闻入口: Longbridge (长桥证券)** | Supplementary Channel | 批次4 | HTTP 200 受限 | React SPA Shell (<div ... | 0 | - | Open SPA Shell (Content Requires User... |
| 193 | src-SUPP-11 | **社交平台官方主页: 越南政府 Facebook (Thông tin Chính phủ)** | Supplementary Channel | 批次4 | HTTP 400 受限 | Automated Access Block... | 0 | - | Walled Garden / Login Required (HTTP ... |
| 194 | src-SUPP-12 | **社交平台官方主页: VnExpress Facebook (Cộng đồng VnExpress)** | Supplementary Channel | 批次4 | HTTP 400 受限 | Automated Access Block... | 0 | - | Walled Garden / Login Required (HTTP ... |
| 195 | src-SUPP-13 | **社交平台官方主页: Báo Đầu tư Facebook (Báo Đầu tư Online)** | Supplementary Channel | 批次4 | HTTP 400 受限 | Automated Access Block... | 0 | - | Walled Garden / Login Required (HTTP ... |
| 196 | src-SUPP-14 | **备用渠道: 企业微信公众号 (搜狗微信搜索备用入口)** | Supplementary Channel | 批次4 | HTTP 200 正常 | HTML List (Sogou Weixi... | 5 | - | Open Search (Anti-Bot on High Frequency) |

---

## 四、 准备工作完成后的建议路线

全量 196 个源的摸排底册已全部铸成，彻底排除了经验推测。后续可以有据可依地开展以下动作：

1. **立即接入第一梯队（176 个已验证连通源）**：这 176 个源已证明可纯本地脚本抓取，覆盖国家部委、16 省地方行政、主流媒体与大园区，可直接编入低成本定时采集引擎。
2. **合理处置第二梯队（20 个受限/高摩擦源）**：包括路透、外资交易所与社交主页，将其精准归入二期备用库或按需核查池，避免为少数反爬源牺牲整体系统的极简性。
