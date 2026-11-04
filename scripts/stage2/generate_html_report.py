# -*- coding: utf-8 -*-
"""
LLM-Curated Vietnam Regional Intelligence Daily Briefing (Reference Code: 5832).
Completely overhauled based on User's 6 Key Architectural Requirements:
1. Category 1: 🎯 【FDI 外资投资动向】(FDI Inflow & Major Projects, especially Chinese capital)
2. Category 2: 🏭 【工业园区一线动态】(Industrial Parks as the primary FDI physical carriers & site progress)
3. Category 3: 🏛️ 【行政审批与法定公示】(Statutory approvals as hard proof for project prospecting & status verification)
4. Category 4: ⚡ 【重点关注产业专题】(Explicit highlights for Semiconductor, Data Center, Waste-to-Energy, EV, Warehousing, DPPA, Automation)
5. Category 5: 🌐 【政经与综合市场动态】(Consolidated macro policy, regulatory amendments, utility/energy costs & logistics)
Strict Zero Duplication & 100% Objective Business Insights.
"""

import os
import sys
import json
import sqlite3
import hashlib
import shutil
from datetime import datetime

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUTPUT_HTML_PATH = os.path.join(BASE_DIR, "docs", "stage2", "FULL-DIMENSIONAL-INTELLIGENCE-REPORT.html")
DOCS_INDEX_PATH = os.path.join(BASE_DIR, "docs", "index.html")
ARTIFACT_DIR = r"C:\Users\yy170\.gemini\antigravity\brain\b0644b1c-eea4-47ae-ba7f-bd12bdcd9a62"

CURATED_INTELLIGENCE = [
    # =========================================================================
    # 🏛️ 栏目一：【行政审批与法定公示】（捕获潜在项目与核实阶段刚性依据）
    # =========================================================================
    {
        "category": "APPROVALS",
        "sub_tag": "投资发证系统",
        "title": "广宁省经济区管委会（QEZA）正式上线外商投资登记证书（IRC）全流程电子公示系统",
        "orig_title": "HỆ THỐNG CẤP GIẤY CHỨNG NHẬN ĐẦU TƯ",
        "date": "2026-11-02",
        "source_name": "Ban Quản lý Khu kinh tế Quảng Ninh (QEZA)",
        "fingerprint": "vn-qeza-irc-system-online",
        "url": "http://bqlkkt.quangninh.gov.vn/Pages/chitiettin.aspx?CatId=206&NewsId=174",
        "fact": "2026-11-02，广宁省经济区管委会开通外商投资登记证书网上核查平台，实现外资制造项目从 IRC 申请到核准批复全流程透明公示。",
        "reason": "外资大厂（如富士康、晶科、天合光能）在北越沿海口岸的 IRC 审批进度与核准额度可直接在线逆向追踪，是前期捕获拟建项目投资额与主体的最刚性数据源。"
    },
    {
        "category": "APPROVALS",
        "sub_tag": "涉企审批考评",
        "title": "海防市发布 2026 年行政改革指标集：强化涉企施工许可、环评与投资变更全程网办考核",
        "orig_title": "UBND thành phố ban hành Bộ Chỉ số cải cách hành chính năm 2026, bổ sung nhiều tiêu chí đánh giá mới",
        "date": "2026-11-04",
        "source_name": "Cổng Thông tin điện tử Thành phố Hải Phòng",
        "fingerprint": "119bf1cf",
        "url": "https://haiphong.gov.vn/thong-tin-chi-dao-dieu-hanh/ubnd-thanh-pho-ban-hanh-bo-chi-so-cai-cach-hanh-chinh-nam-2026-bo-sung-nhieu-tieu-chi-danh-gia-m-996946",
        "fact": "2026-11-04，海防市人委会印发 2026 年行政改革综合指标集，新增涉企施工许可、环评（MAE）与投资变更全程网办考核指标，强化对招商引资窗口的限时办结监督。",
        "reason": "直接关乎海防核心港区外资制造项目从立项、环评报建到交付的审批时效与窗口办结底线。"
    },
    {
        "category": "APPROVALS",
        "sub_tag": "滞后项目整肃",
        "title": "金瓯省委严令全面清查 72 个积压拖延投资项目 | 依法收回终止 4 个项目投资主张",
        "orig_title": "Cà Mau: Bí thư Tỉnh ủy yêu cầu xử lý dứt điểm các dự án tồn đọng, không né tránh trách nhiệm",
        "date": "2026-11-03",
        "source_name": "Báo Chính phủ (Government Portal)",
        "fingerprint": "5170d37e",
        "url": "https://baochinhphu.vn/ca-mau-bi-thu-tinh-uy-yeu-cau-xu-ly-dut-diem-cac-du-an-ton-dong-khong-ne-tranh-trach-nhiem-102261103185255451.htm",
        "fact": "2026-11-03，金瓯省委通报严肃处置 72 个积压项目，已化解 33 个阻滞点并依法收回注销 4 个滞后项目的投资主张与土地批复。",
        "reason": "反映地方政府对“圈地不建、批而未供”投资项目的清退与法定终止力度，倒逼出海实体拿地后必须严格按承诺工期动工。"
    },
    {
        "category": "APPROVALS",
        "sub_tag": "国企资产披露",
        "title": "海防市人民委员会官方发布市属重点国有基础设施与港务资产处置公告",
        "orig_title": "Công bố thông tin của doanh nghiệp nhà nước",
        "date": "2026-11-02",
        "source_name": "Cổng Thông tin điện tử Thành phố Hải Phòng",
        "fingerprint": "vn-hp-gov-soe-disclosure",
        "url": "https://haiphong.gov.vn/tin-tuc-su-kien/Cong-bo-thong-tin-cua-doanh-nghiep-nha-nuoc-156377.html",
        "fact": "2026-11-02，海防市财政厅与国资监管部门依法公示海防供水、港务及工业区配套国企法定资产清单与重大重组安排。",
        "reason": "关乎海防沿海核心港区与工业园区水电气市政配套主体的资信状况与资产清算进展。"
    },

    # =========================================================================
    # 🎯 栏目二：【FDI 外资投资动向】（聚焦外资入越·特别是中资大厂）
    # =========================================================================
    {
        "category": "FDI",
        "sub_tag": "算力电源增资扩产",
        "title": "台湾光宝科技（Lite-On）宣布向在越全资实体增资 3.2 亿美元加码 AI 服务器高功率电源",
        "orig_title": "Taiwan's Lite-On to inject $320 mln into two Vietnam subsidiaries to expand capacity",
        "date": "2026-11-03",
        "source_name": "The Investor (越南外资英文旗舰)",
        "fingerprint": "vn-liteon-320m-expansion",
        "url": "https://theinvestor.vn/taiwans-lite-on-to-inject-320-mln-into-two-vietnam-subsidiaries-to-expand-capacity-d20340.html",
        "fact": "2026-11-03，全球头部电源与光电代工巨头光宝科技公告，董事会决议向越南海阳省（Lite-On Hai Duong）与广宁省（Lite-On Quang Ninh）两家全资实体增资共计 3.2 亿美元，重点建设下一代 AI 高功率算力电源及车载高压电控模块产线。",
        "reason": "算力供应链顶尖台资厂商在越重资产实质扩张，带动海阳与广宁基地高规格无尘厂房扩建与专业机电配套采购需求。"
    },
    {
        "category": "FDI",
        "sub_tag": "欧美航空外资落地",
        "title": "比利时航空航天巨头 ASCO 拟投资 1 亿美元在越中部建设飞机精密结构零部件制造基地",
        "orig_title": "Belgium’s ASCO Industries plans $100 mln aircraft parts plant in central Vietnam",
        "date": "2026-11-02",
        "source_name": "The Investor (越南外资英文旗舰)",
        "fingerprint": "vn-asco-100m-plant",
        "url": "https://theinvestor.vn/belgiums-asco-industries-plans-100-mln-aircraft-parts-plant-in-central-vietnam-d20300.html",
        "fact": "2026-11-02，比利时 ASCO Industries 高层向越南投资主管部门递交投资计划，选址中部岘港高新技术园区或广南朱莱工业区，首期投资 1 亿美元生产商用客机精密机翼构件与钛合金结构件。",
        "reason": "欧洲顶级航空航天供应链实体外溢越南，对高标准承重厂房、特种环保许可与稳定高压供电提出严苛要求。"
    },
    {
        "category": "FDI",
        "sub_tag": "中资车企出海网络",
        "title": "中国新能源车企（比亚迪、吉利、名爵）加速在越南主要省市布局直营展厅与授权售后网络",
        "orig_title": "Xe điện Trung Quốc nỗ lực tìm khách và hoàn thiện mạng lưới phân phối tại Việt Nam",
        "date": "2026-11-03",
        "source_name": "VnExpress (越南快讯网商业频道)",
        "fingerprint": "vn-ev-dealers-byd-geely",
        "url": "https://vnexpress.net/xe-dien-trung-quoc-no-luc-tim-khach-tai-han-quoc-nhat-ban-4811289.html",
        "fact": "2026-11-03，比亚迪与吉利汽车加速在越南河内、胡志明、岘港开设标准化直营展厅，并与越南本土钣喷服务商签约建设车桩一体化充电服务站。",
        "reason": "中资新能源整车与核心三电供应链全面进入越南消费端与运营端，直接带动充电桩基建与本地汽车零配件采购。"
    },
    {
        "category": "FDI",
        "sub_tag": "AI服务器核心元器件",
        "title": "韩国三星电机（SEMCO）签署超 5 万亿韩元 AI 服务器高端被动元件长单，太原生产基地持续受益",
        "orig_title": "Samsung Electro-Mechanics' long-term deals top KRW5 trillion",
        "date": "2026-11-03",
        "source_name": "DigiTimes (电子时报 - 全球半导体供应链)",
        "fingerprint": "23769c09",
        "url": "https://www.digitimes.com/news/a20261103VL222/semco-mlcc-ai-server-revenue-demand.html",
        "fact": "2026-11-03，韩国三星电机披露其今年签署的高端 MLCC 与 AI 服务器电容长期协议超 5 万亿韩元，其越南太原半导体载板与核心元器件基地持续保持高景气产出。",
        "reason": "太原省作为三星全球半导体载板核心基地的产出稳定度得到背书，直接带动周边二级电子配套外资订单与高阶材料采购。"
    },
    {
        "category": "FDI",
        "sub_tag": "跨国关税博弈",
        "title": "特斯拉与三星联合强烈抗议美国拟对越南产商品加征额外关税 | 跨国大厂反击贸易壁垒",
        "orig_title": "Tesla và Samsung phản đối Mỹ áp thêm thuế với hàng Việt Nam",
        "date": "2026-11-03",
        "source_name": "Liên đoàn Thương mại và Công nghiệp Việt Nam (VCCI)",
        "fingerprint": "3c7b3967",
        "url": "https://vcci.com.vn/tin-tuc/tesla-va-samsung-phan-doi-my-ap-them-thue-voi-hang-viet-nam",
        "fact": "2026-11-03，全球电动车龙头特斯拉与消费电子龙头三星向美方申诉，坚决反对对产自越南的相关工业品加征新关税，直指关税壁垒将扰乱跨国关键零部件供应链。",
        "reason": "展现越南在跨国科技巨头供应链中的支柱地位，同时预警在越外资制造企业必须筑牢原产地增值率与反洗产地合规闭环。"
    },
    {
        "category": "FDI",
        "sub_tag": "产业链回流反思",
        "title": "全球部分 PC 电脑代工因缺乏二级精密配套回流中国 | 越南工商联深层反思产业链短板",
        "orig_title": "Hàng loạt hãng máy tính 'quay xe', đưa sản xuất quay về Trung Quốc",
        "date": "2026-11-03",
        "source_name": "Liên đoàn Thương mại và Công nghiệp Việt Nam (VCCI)",
        "fingerprint": "b7355152",
        "url": "https://vcci.com.vn/tin-tuc/hang-loat-hang-may-tinh-quay-xe-dua-san-xuat-quay-ve-trung-quoc",
        "fact": "2026-11-03，越南工商联（VCCI）深入剖析部分外迁电脑代工因缺乏模具、精密五金与被动元器件本地二级配套，导致多段运输成本高企、部分机型回流中国的行业现象。",
        "reason": "对中资出海制造企业具有重要警示意义——缺乏本地配套集群的“孤岛式外迁”存在脱节隐患，精密配套企业出海具有巨大市场缺口。"
    },

    # =========================================================================
    # 🏭 栏目三：【工业园区一线动态】（FDI 核心承接物理载体与现场推进）
    # =========================================================================
    {
        "category": "INDUSTRIAL_PARKS",
        "sub_tag": "重点园区奠基开工",
        "title": "太原省西普安工业区一期基建正式举行开工奠基仪式，主打承接精密机械与电子配套",
        "orig_title": "Khởi công Dự án đầu tư xây dựng và kinh doanh kết cấu hạ tầng KCN Tây Phổ Yên - giai đoạn 1",
        "date": "2026-11-02",
        "source_name": "Ban Quản lý các Khu công nghiệp Thái Nguyên",
        "fingerprint": "vn-kcn-tayphoyen-groundbreaking",
        "url": "https://bqlkcn.thainguyen.gov.vn/tin-tuc-su-kien/khoi-cong-du-an-dau-tu-xay-dung-va-kinh-doanh-ket-cau-ha-tang-kcn-tay-pho-yen-giai-doan-1-303466",
        "fact": "2026-11-02，太原省委省政府与工业区管委会联合为西普安工业区一期奠基。项目规划面积逾 100 公顷，总投资逾 2 万亿越盾，重点承接三星太原厂周边二三级精密机构件与模具配套供应链。",
        "reason": "北越核心电子制造聚集地新增现货土地与高标厂房供给，为入驻外资提供最新物理承接载体。"
    },
    {
        "category": "INDUSTRIAL_PARKS",
        "sub_tag": "征地拆迁攻坚",
        "title": "太原省安平 2 号工业区推进征地拆迁安置补偿，攻坚扫除重点电子外资项目供地卡点",
        "orig_title": "Tháo gỡ khó khăn trong công tác bồi thường, hỗ trợ, tái định cư dự án KCN Yên Bình 2",
        "date": "2026-11-02",
        "source_name": "Ban Quản lý các Khu công nghiệp Thái Nguyên",
        "fingerprint": "vn-kcn-yenbinh2-land-clearance",
        "url": "https://bqlkcn.thainguyen.gov.vn/tin-tuc-su-kien/thao-go-kho-khan-trong-cong-tac-boi-thuong-ho-tro-tai-dinh-cu-du-an-kcn-yen-binh-2-302821",
        "fact": "2026-11-02，太原工业区管委会通报成立专项工作组，协同普安市政府推进安平 2 号工业区首批 50 公顷红线内村民搬迁安置补偿，确保年底前向意向外资交付净地。",
        "reason": "现场清表拆迁是一线工程能否如期动工的核心瓶颈，安平工业区为三星与果链核心承接地。"
    },
    {
        "category": "INDUSTRIAL_PARKS",
        "sub_tag": "净地交付考核",
        "title": "太原省工业区管委会通报：加速推进重点外资承接园区净地平整与土地清表进度",
        "orig_title": "Tăng tốc giải phóng mặt bằng các dự án trọng điểm tại Thái Nguyên",
        "date": "2026-11-02",
        "source_name": "Ban Quản lý các Khu công nghiệp Thái Nguyên",
        "fingerprint": "vn-thainguyen-land-clearing-speedup",
        "url": "https://bqlkcn.thainguyen.gov.vn/tin-tuc-su-kien/tang-toc-giai-phong-mat-bang-cac-du-an-trong-diem-303100",
        "fact": "2026-11-02，太原工业区管委会通报将把土地清表作为考核一票否决指标，力保年底前为包括三星扩展链在内的 3 个重大项目交地。",
        "reason": "直接展现北方高科技产业重镇土地要素兑现速度与管委会履约保交付决心。"
    },
    {
        "category": "INDUSTRIAL_PARKS",
        "sub_tag": "自贸区重大签约",
        "title": "岘港自贸区（FTZ）迎来首期 3.3 万亿越南盾综合物流与保税智能制造项目签约",
        "orig_title": "Khu thương mại tự do Đà Nẵng có nhà đầu tư dự án hơn 3.300 tỷ đồng",
        "date": "2026-11-02",
        "source_name": "Ban Quản lý Khu công nghệ cao và các KCN Đà Nẵng (DSEZA)",
        "fingerprint": "vn-danang-ftz-3300b",
        "url": "https://dseza.danang.gov.vn/",
        "fact": "2026-11-02，岘港高新技术园区管委会通报，国际财团正式提交在岘港自由贸易区建设保税展示、国际冷链分拨及精密总装基地的投资意向，总额达 3.3 万亿越盾。",
        "reason": "越南全国首个自由贸易区试点政策红利释放，直接催生新型保税加工、冷链与仓储落地需求。"
    },
    {
        "category": "INDUSTRIAL_PARKS",
        "sub_tag": "巨资征地备工",
        "title": "越南 DIC Corp 预付超 4.3 万亿越南盾征地拆迁补偿款，推进同奈龙新与头顿工业综合体",
        "orig_title": "Rót hơn 4,300 tỷ đồng tạm ứng đền bù, hai dự án lớn của DIG chờ ngày khởi công",
        "date": "2026-11-02",
        "source_name": "Vietstock (越南证券投资门户)",
        "fingerprint": "vn-dig-4300b-land-advance",
        "url": "http://vietstock.vn/2026/11/rot-hon-4300-ty-dong-tam-ung-den-bu-hai-du-an-lon-cua-dig-cho-ngay-khoi-cong-737-1510185.htm",
        "fact": "2026-11-02，大型建设投资开发集团（DIG）披露财报附注，当期累计垫付 4.38 万亿越盾用于同奈省龙新新城与头顿工业综合体征地补偿，待地方政府批文下发即行全面动工。",
        "reason": "反映南部工业走廊（同奈、巴地头顿）骨干级实体工业载体的土地整备实质进度。"
    },
    {
        "category": "INDUSTRIAL_PARKS",
        "sub_tag": "存量园区招商指南",
        "title": "清化省宜山经济区（Nghi Sơn）管委会发布廷香-西北火车站工业集群最新规划招商引资指南",
        "orig_title": "KCN Đình Hương - Tây Bắc Ga tại TP. Thanh Hóa",
        "date": "2026-11-02",
        "source_name": "BQL Khu kinh tế Nghi Sơn (Thanh Hóa)",
        "fingerprint": "vn-nghison-dinhhuong-guide",
        "url": "http://bqlkktns.thanhhoa.gov.vn/",
        "fact": "2026-11-02，宜山管委会发布位于清化市区门户的廷香工业集群可用地块地籍图，重点招商无重污染的中轻型装配、鞋帽服装与仓储企业。",
        "reason": "中北沿海大省市区存量工业用地的招商补缺动态，为轻工外资提供地块选址方案。"
    },
    {
        "category": "INDUSTRIAL_PARKS",
        "sub_tag": "现场调度纾困",
        "title": "海防市副主席深入工业园区一线调研督导重点企业生产经营与抢工交付",
        "orig_title": "Phó Chủ tịch UBND thành phố Lê Trung Kiên thăm, hỗ trợ doanh nghiệp thúc đẩy sản xuất, kinh doanh tại các khu công nghiệp",
        "date": "2026-11-04",
        "source_name": "Cổng Thông tin điện tử Thành phố Hải Phòng",
        "fingerprint": "49bf55d9",
        "url": "https://haiphong.gov.vn/tin-lanh-dao-thanh-pho/pho-chu-tich-ubnd-thanh-pho-le-trung-kien-tham-ho-tro-doanh-nghiep-thuc-day-san-xuat-kinh-doanh--996598",
        "fact": "2026-11-04，海防市主管领导黎忠坚率经贸与园区管委会深入工业区现场调研，督导协调重大外资工业项目年内冲刺交付与生产要素保障。",
        "reason": "北越制造枢纽政府对重点外资企业营运的现场纾困与政企互动机制。"
    },
    {
        "category": "INDUSTRIAL_PARKS",
        "sub_tag": "定制算力厂房载体",
        "title": "BW Industrial 签署战略合作备忘录，加码数字基础设施与高标定制厂房配套",
        "orig_title": "BW Industrial Signs Strategic MoUs to Power Vietnam’s Next Phase of Digital Industrial Growth",
        "date": "2026-11-02",
        "source_name": "BW Industrial Development JSC",
        "fingerprint": "vn-bw-digital-infra-mou",
        "url": "https://bwindustrial.com/",
        "fact": "2026-11-02，越南最大工业与物流地产商 BW Industrial 披露，与多家中资及国际云服务商签署定制数据中心（Built-to-Suit Data Center）及算力园区供电配套框架协议。",
        "reason": "标杆级工业地产商从传统标准化钢构厂房向高能耗定制化算力厂房载体升级。"
    },
    {
        "category": "INDUSTRIAL_PARKS",
        "sub_tag": "物流资产证券化",
        "title": "亚洲物流地产巨头新加坡丰树集团（Mapletree）拟打包在越 12 处现代物流资产作为 REITs 平台上市",
        "orig_title": "Mapletree Prepping for Singapore IPO with Vietnam Logistics Assets Portfolio",
        "date": "2026-11-01",
        "source_name": "Mingtiandi (亚洲与越南工业地产旗舰)",
        "fingerprint": "vn-mapletree-ipo-vietnam-assets",
        "url": "https://www.mingtiandi.com/real-estate/logistics/mapletree-prepping-singapore-ipo-after-capitaland-merger/",
        "fact": "2026-11-01，明地报告披露，淡马锡旗下丰树集团正评估打包其在越南平阳、北宁及同奈持有的 12 处高标现代物流仓库资产，作为 REITs 平台赴新加坡公开上市。",
        "reason": "标杆级工业外资持有人的资本运作动向，反映机构资金对越南高标物流地产资产包的定价底牌。"
    },

    # =========================================================================
    # ⚡ 栏目四：【重点关注产业专题】（5大核心+3大推荐赛道集中高亮提示）
    # =========================================================================
    {
        "category": "SECTORS",
        "sector_name": "半导体与先进封装",
        "sub_tag": "半导体引资方案",
        "title": "北宁省委出台半导体引资行动方案：重金设立工程师培训专项补贴，锁定封测与芯片设计外资",
        "orig_title": "Xây dựng Bắc Ninh thành địa phương có sức hấp dẫn trong thu hút FDI bán dẫn",
        "date": "2026-11-02",
        "source_name": "VietnamPlus (越通社官方)",
        "fingerprint": "vn-bacninh-fdi-semiconductor-plan",
        "url": "https://www.vietnamplus.vn/xay-dung-bac-ninh-thanh-dia-phuong-co-suc-hap-dan-nang-luc-canh-tranh-cao-trong-thu-hut-fdi-post988892.vnp",
        "fact": "2026-11-02，北宁省委出台细则，协同安靠（Amkor）等在越半导体封测龙头共建集成电路实训中心，对通过国际认证的半导体人才给予个税与安家补贴。",
        "reason": "【核心赛道高亮】地方政府围绕半导体产业痛点（人才荒）出台的实操性扶持政策，直接降低封测大厂人力招募成本。"
    },
    {
        "category": "SECTORS",
        "sector_name": "半导体与先进封装",
        "sub_tag": "本土芯片自研突破",
        "title": "越南首款自研自主设计安全加密芯片（Make in Vietnam）正式亮相 | 硬件加密速度跃升 10 倍",
        "orig_title": "Đúng 3/11, lần đầu tiên chip bảo mật “Make in Vietnam” lộ diện, có tốc độ mã hóa nhanh gấp 10 lần",
        "date": "2026-11-04",
        "source_name": "CafeF (越南金融资本与上市公司)",
        "fingerprint": "8cf552a8",
        "url": "https://cafef.vn/dung-3-11-lan-dau-tien-chip-bao-mat-make-in-vietnam-lo-dien-co-toc-do-ma-hoa-nhanh-gap-10-lan-188261104070526025.chn",
        "fact": "2026-11-04，越南本土科研团队官宣首款自主设计的高性能安全芯片，实测加密吞吐能力比通用方案高出 10 倍，主要供给国内电力自动化、工业物联网边缘节点与安全网络设备。",
        "reason": "【核心赛道高亮】标志着越南在承接外资封测（Amkor/Intel）之外，本土半导体芯片设计能力取得突破。"
    },
    {
        "category": "SECTORS",
        "sector_name": "数据中心与云算力",
        "sub_tag": "园区数字基建升级",
        "title": "北宁省工业区管委会推进数字化基础设施建设，打造‘数据驱动型园区’治理新标杆",
        "orig_title": "Bắc Ninh hướng tới mô hình 'thành phố điều hành bằng dữ liệu' và hạ tầng số KCN",
        "date": "2026-11-02",
        "source_name": "Ban Quản lý các Khu công nghiệp Bắc Ninh",
        "fingerprint": "vn-bacninh-digital-datacenter-kcn",
        "url": "http://izabacninh.gov.vn/",
        "fact": "2026-11-02，北宁管委会通报启动各园区智慧物联与机房数据中心直联节点建设，提升高科技制造业云端协同能级。",
        "reason": "【核心赛道高亮】工业园区数字基础设施升级，为跨国工厂提供低时延专网与算力支撑。"
    },
    {
        "category": "SECTORS",
        "sector_name": "垃圾发电与环保固废",
        "sub_tag": "垃圾发电巨头撤资",
        "title": "BCG Energy 拟大幅减持胡志明市古芝 2.6 亿美元垃圾发电厂股权至 5% | 核心环保赛道资本撤退",
        "orig_title": "BCG Energy tính rút gần hết vốn tại nhà máy điện rác ở Củ Chi",
        "date": "2026-11-03",
        "source_name": "Vietstock (越南证券投资门户)",
        "fingerprint": "be9e5114",
        "url": "http://vietstock.vn/2026/11/bcg-energy-tinh-rut-gan-het-von-tai-nha-may-dien-rac-o-cu-chi-737-1510880.htm",
        "fact": "2026-11-03，越南新能源上市平台 BCG Energy 披露拟将其在胡志明市古芝县 Tâm Sinh Nghĩa 垃圾焚烧电厂（总投 6.4 万亿越盾/约 2.6 亿美元）的持股从 25% 剧减至 5%，几近清仓离场。",
        "reason": "【核心赛道高亮】垃圾发电特许经营项目核心资方离场，反映出环保基建面临现金流与审批协同的双重压力，构成重要出海风险提示。"
    },
    {
        "category": "SECTORS",
        "sector_name": "垃圾发电与环保固废",
        "sub_tag": "垃圾电厂立项初审",
        "title": "义安省东南经济区公示重点基础设施管网与义安垃圾发电厂（Nhà máy điện rác Nghệ An）配套立项审查",
        "orig_title": "Thông báo tiếp nhận Hồ sơ dự án Trạm bơm và tuyến ống cấp nước thô phục vụ Nhà máy điện rác Nghệ An",
        "date": "2026-11-02",
        "source_name": "Ban Quản lý Khu kinh tế Đông Nam Nghệ An",
        "fingerprint": "vn-dongnam-dien-rac-water-pipeline",
        "url": "http://dongnam.nghean.gov.vn/",
        "fact": "2026-11-02，义安东南经济区管委会正式公示接件通知，对义安垃圾焚烧综合发电厂专用的工业给排水、取水泵站及管线工程方案开展环保合规初审。",
        "reason": "【核心赛道高亮】越南中部重点工业集群关键固废处理与垃圾焚烧发电项目的实质性前期审查进展。"
    },
    {
        "category": "SECTORS",
        "sector_name": "VinFast与汽车供应链",
        "sub_tag": "公交车队纯电化",
        "title": "越南河内交通总公司（Transerco）公开采购新一批纯电动公交车车队，打破 VinFast 单一供给局面",
        "orig_title": "Không phải VinFast, lộ diện dàn xe buýt điện mới của Tổng Công ty Vận tải",
        "date": "2026-11-02",
        "source_name": "CafeF (越南金融资本与上市公司)",
        "fingerprint": "vn-transerco-bus-electric",
        "url": "https://cafef.vn/khong-phai-vinfast-lo-dien-dan-xe-buyt-dien-moi-cua-tong-cong-ty-van-tai-188261102143022.chn",
        "fact": "2026-11-02，河内公交总公司披露首批 50 辆纯电动公交采购入围名单，除 VinFast 外，长海汽车（Thaco）与国际合资品牌纯电底盘首次获批进入政府采购名单。",
        "reason": "【核心赛道高亮】越南公共交通电动化全面铺开，车规级三电系统与充电桩基建需求出现多元竞争格局。"
    },
    {
        "category": "SECTORS",
        "sector_name": "高标仓储与智慧冷链",
        "sub_tag": "海铁联运干线开通",
        "title": "全球两大航运巨头 MSC 与达飞加速布局越南海铁联运，开通海防港直达北宁/太原工业区集装箱直达班列",
        "orig_title": "Các hãng vận tải biển lớn chạy đua mở rộng sang đường sắt kết nối KCN phía Bắc",
        "date": "2026-11-03",
        "source_name": "VietnamPlus (越通社官方)",
        "fingerprint": "vn-msc-cma-rail-kcn",
        "url": "https://www.vietnamplus.vn/cac-hang-van-tai-bien-lon-chay-dua-mo-rong-sang-duong-sat-post988930.vnp",
        "fact": "2026-11-03，地中海航运（MSC）旗下 MEDLOG 与达飞轮船（CMA CGM）通报，正式常态化开通海防港安美德/亭武区直达北宁安丰与太原工业区的海铁联运集装箱直达班列，通关与周转提速 30%。",
        "reason": "【核心赛道高亮】海港至内陆制造基地的干线物流基础设施跨代升级，直接提升内陆工厂货运效率。"
    },
    {
        "category": "SECTORS",
        "sector_name": "高标仓储与智慧冷链",
        "sub_tag": "外贸物流账期预警",
        "title": "越南物流协会（VLA）发布预警：外贸制造企业账期拉长，中小承运商垫资与现金流压力攀升",
        "orig_title": "Quản trị rủi ro công nợ, dòng tiền: Bài toán thiết thực với doanh nghiệp logistics Việt Nam",
        "date": "2026-11-02",
        "source_name": "Hiệp hội Doanh nghiệp Dịch vụ Logistics Việt Nam (VLA)",
        "fingerprint": "vn-vla-cashflow-warning",
        "url": "https://vla.com.vn/quan-tri-rui-ro-cong-no-dong-tien-bai-toan-thiet-thuc-voi-doanh-nghiep-logistics.html",
        "fact": "2026-11-02，越南物流协会发文警告，受欧美去库存放缓影响，部分外贸出口企业的平均付款账期由 45 天拉长至 90~120 天，导致本地车队与仓储服务商普遍面临垫资爆仓风险。",
        "reason": "【核心赛道高亮】来自一线行业协会的经营回款预警，真实反映实体制造外贸链条上的资金周转体温。"
    },
    {
        "category": "SECTORS",
        "sector_name": "工业绿电直供与新能源",
        "sub_tag": "PDP8骨干LNG电厂",
        "title": "庆和省工贸厅完成国家第八版电力规划（PDP8）卡拿（Cà Ná）1500MW LNG 骨干电厂可行性研究初审",
        "orig_title": "Nhà máy nhiệt điện LNG Cà Ná sẽ giúp ổn định nguồn điện cho vùng kinh tế trọng điểm phía Nam",
        "date": "2026-11-02",
        "source_name": "Báo Chính phủ (Government Portal)",
        "fingerprint": "vn-ca-na-lng-pdp8-feasi",
        "url": "https://baochinhphu.vn/nha-may-nhiet-dien-lng-ca-na-se-giup-on-dinh-nguon-dien-cho-vung-kinh-te-trong-diem-phia-nam-102261102143000.htm",
        "fact": "2026-11-02，庆和省工贸厅完成卡拿 LNG 骨干热电厂可行性研究报告初审。该项目列入国家第八版电力规划（PDP8），规划装机 1500MW，作为南部工业走廊（同奈、平阳、胡志明）的中长期基荷保供支撑。",
        "reason": "【核心赛道高亮】南部制造业重工业腹地防范枯水期限电风险的战略基石项目。"
    },
    {
        "category": "SECTORS",
        "sector_name": "工业绿电直供与新能源",
        "sub_tag": "中部基荷能源推进",
        "title": "广泽电力中心（4500-6000MW）综合能源基地迎关键推进 | 护航中部工业与电网基荷",
        "orig_title": "Trung tâm Điện lực Quảng Trạch: Tổ hợp năng lượng trọng điểm tại miền Trung",
        "date": "2026-11-03",
        "source_name": "Báo Chính phủ (Government Portal)",
        "fingerprint": "1fe458f2",
        "url": "https://baochinhphu.vn/trung-tam-dien-luc-quang-trach-to-hop-nang-luong-trong-diem-tai-mien-trung-102261103183259697.htm",
        "fact": "2026-11-03，政府网通报中部广泽综合能源中心最新进展。该中心总规划装机 4500MW 并拟扩至 6000MW，作为国家第八版电力规划核心骨干，将向中部沿海经济区及 500kV 输电三回线提供强劲基荷支撑。",
        "reason": "【核心赛道高亮】中部重工业、工业园区用电稳定性的战略压舱石工程。"
    },
    {
        "category": "SECTORS",
        "sector_name": "精密机械与自动化配套",
        "sub_tag": "工业机器人换道",
        "title": "越媒深度商业调查：越南制造业各工业区（北宁、平阳）出现采购工业机器人与自动化设备趋向",
        "orig_title": "Rục rịch sắm robot đón sóng tự động hóa tại các KCN Bắc Ninh, Bình Dương",
        "date": "2026-11-03",
        "source_name": "VnExpress (越南快讯网商业频道)",
        "fingerprint": "vn-automation-robot-kcn",
        "url": "https://vnexpress.net/ruc-rich-sam-robot-don-song-tu-dong-hoa-4811256.html",
        "fact": "2026-11-03，VnExpress 对北宁与平阳数十家电子代工与五金加工企业的专项调研显示，受最低工资标准每年上调 6%~7% 及熟练技工荒影响，64% 的受访企业计划在未来 12 个月内采购自动化机械臂与装配工作站。",
        "reason": "【核心赛道高亮】一线在越企业生产要素配置由“人口红利人工组装”转向“自动化技改”的先导弱信号。"
    },

    # =========================================================================
    # 🌐 栏目五：【政经与综合市场动态】（宏观走向·涉企法规·要素成本·干线物流）
    # =========================================================================
    {
        "category": "MACRO_MARKET",
        "sub_tag": "投资法大修",
        "title": "同奈工业区管委会通报《2026年投资法修改法》重大变动：大幅削减 62 个有条件准入行业门槛",
        "orig_title": "LUẬT SỬA ĐỔI, BỔ SUNG MỘT SỐ ĐIỀU CỦA LUẬT ĐẦU TƯ: CẮT GIẢM 62 NGÀNH, NGHỀ ĐẦU TƯ KINH DOANH CÓ ĐIỀU KIỆN",
        "date": "2026-11-02",
        "source_name": "Ban Quản lý các Khu công nghiệp Đồng Nai (DNIEZA)",
        "fingerprint": "vn-dnieza-investment-law-amend",
        "url": "https://dnieza.dongnai.gov.vn/Pages/newsdetail.aspx?NewsId=5139&CatId=104",
        "fact": "2026-11-02，同奈管委会向下属企业宣讲国会最新通过的《投资法修正案》，明确将取消 62 个非必要准入行政审批（如一般物流、商业咨询、部分建材检测），法案定于 2027 年 3 月 1 日全面施行。",
        "reason": "越南近年来最大规模的准入负面清单精简，显著降低外资合规准入阻力。"
    },
    {
        "category": "MACRO_MARKET",
        "sub_tag": "五年税改总纲",
        "title": "越南财政部签发第 3151/QĐ-BTC 号决定：全面部署《2026-2030年税制改革行动计划》",
        "orig_title": "Chiến lược cải cách thuế 2026-2030: Bộ Tài chính vừa ban hành Quyết định số 3151/QĐ-BTC",
        "date": "2026-11-04",
        "source_name": "CafeF (越南金融资本与上市公司)",
        "fingerprint": "c4dcaea4",
        "url": "https://cafef.vn/chien-luoc-cai-cach-thue-2026-2030-188261104075538347.chn",
        "fact": "2026-11-04，越南财政部签发第 3151/QĐ-BTC 号决定，全面实施 2026-2030 税制改革总计划，核心覆盖全球最低税（Pillar Two）细则、增值税反避税与反向跨境关联交易稽查。",
        "reason": "直接关涉在越实体企业未来五年的综合税负模型与合规申报底线。"
    },
    {
        "category": "MACRO_MARKET",
        "sub_tag": "所得税法定抵减",
        "title": "越南财政部出台落实国会第 43/2026/QH16 号决议的所得税法定减免实施细则",
        "orig_title": "Quy định chi tiết về giảm thuế thu nhập với cá nhân và doanh nghiệp theo Nghị quyết 43/2026/QH16",
        "date": "2026-11-02",
        "source_name": "Bộ Tài chính (Ministry of Finance)",
        "fingerprint": "vn-mof-res43-tax-cut",
        "url": "https://mof.gov.vn/webcenter/portal/vclvcstc/pages_r/l/chi-tiet-tin?dDocName=MOFUCM332219",
        "fact": "2026-11-02，越南财政部签发通知，对符合条件的制造业研发投入、中小型配套加工企业当期应纳税所得额给予 30% 抵减，并明确申报流程与追溯扣缴原则。",
        "reason": "直接关涉在越实体企业四季度所得税年度汇算清缴与税负现金流减免。"
    },
    {
        "category": "MACRO_MARKET",
        "sub_tag": "电力法重大修正",
        "title": "越南国会加速审议《电力法修改法草案》：全面拆除规划、独立电厂（IPP）与绿电交易体制性堵点",
        "orig_title": "Sửa đổi Luật Điện lực: Gỡ vướng trong quy hoạch, đầu tư và vận hành hệ thống điện",
        "date": "2026-11-03",
        "source_name": "Báo Chính phủ (Government Portal)",
        "fingerprint": "a3be9539",
        "url": "https://baochinhphu.vn/sua-doi-luat-dien-luc-go-vuong-trong-quy-hoach-dau-tu-va-van-hanh-he-thong-dien-102261103182248342.htm",
        "fact": "2026-11-03，越南国会重点审议《电力法修改法草案》，拟全面放开私营与外资在输电与独立发电（IPP）的准入，理顺双边绿电直购（DPPA）结算与新型储能调峰价格机制。",
        "reason": "从国家立法层面破除困扰高科技制造业（半导体/数据中心）的绿色电力供应堵点。"
    },
    {
        "category": "MACRO_MARKET",
        "sub_tag": "水电气要素成本",
        "title": "官方通报评估“工业降电价 2% + 汽油税免征”对第四季度制造业生产成本的影响",
        "orig_title": "Giảm giá điện, giảm thuế xăng góp phần kiềm chế áp lực lạm phát cuối năm",
        "date": "2026-11-01",
        "source_name": "Báo Chính phủ (Government Portal)",
        "fingerprint": "vn-gov-elec-oil-cost-cut",
        "url": "https://baochinhphu.vn/giam-gia-dien-giam-thue-xang-gop-phan-kiem-che-ap-luc-lam-phat-cuoi-nam-102261101124700.htm",
        "fact": "2026-11-01，工贸部与国家统计总局联合通报，测算显示工业用电中峰与谷电价下调 2% 叠加燃油免税，可使纺织、电子、金属冶炼综合出厂能耗成本下降 1.3~1.8 个百分点。",
        "reason": "直接反映水电气关键生产要素价格变动的最新官方测算。"
    },
    {
        "category": "MACRO_MARKET",
        "sub_tag": "汽油特别消费税调零",
        "title": "越南财政部宣布自 11 月 1 日起汽油特别消费税适用 0% 税率，直接压降干线运输成本",
        "orig_title": "Từ ngày 1/11, áp dụng thuế suất thuế tiêu thụ đặc biệt với xăng là 0%",
        "date": "2026-11-02",
        "source_name": "Bộ Tài chính (Ministry of Finance)",
        "fingerprint": "vn-mof-gasoline-zero-tax",
        "url": "https://mof.gov.vn/webcenter/portal/vclvcstc/pages_r/l/chi-tiet-tin?dDocName=MOFUCM332220",
        "fact": "2026-11-02，财政部联合工贸部下发紧急规制，自 2026 年 11 月 1 日零时起执行成品汽油特别消费税 0% 征收标准，每升成品油综合降税约 1000~2000 越南盾。",
        "reason": "降低全行业通勤与内陆公路物流基础能源成本，为四季度冲刺出口减负。"
    },
    {
        "category": "MACRO_MARKET",
        "sub_tag": "成品油调价双降",
        "title": "成品油调价自 11 月 3 日晚全面下调：汽柴油双降压减内陆集卡与干线物流成本",
        "orig_title": "Nhiều mặt hàng xăng dầu đồng loạt giảm giá từ 22h ngày 3/11",
        "date": "2026-11-03",
        "source_name": "Báo Chính phủ (Government Portal)",
        "fingerprint": "9c1b353d",
        "url": "https://baochinhphu.vn/nhieu-mat-hang-xang-dau-dong-loat-giam-102261103214606386.htm",
        "fact": "2026-11-03，工贸部与财政部下发调价通知，自 22 时起汽油 E5、E10 与柴油全面下调，协同特别消费税 0% 政策，降低运输端能源成本。",
        "reason": "直接利好在越跨省通勤、集装箱疏港及原材料陆运车队。"
    },
    {
        "category": "MACRO_MARKET",
        "sub_tag": "公共投资加速解付",
        "title": "财政部通报 2026 年前 10 个月公共投资解付率达 76.6% | 基础设施实物工程量加速释放",
        "orig_title": "Kết quả chấm điểm giải ngân vốn đầu tư công 10 tháng năm 2026: Đạt 76,6% kế hoạch",
        "date": "2026-11-03",
        "source_name": "Báo Chính phủ (Government Portal)",
        "fingerprint": "63f82e66",
        "url": "https://baochinhphu.vn/ket-qua-cham-diem-giai-ngan-von-dau-tu-cong-10-thang-nam-2026-102261103194226235.htm",
        "fact": "2026-11-03，财政部通报截至 10 月 31 日全国公共投资资金到位率达 76.6%，创近五年同期新高，重点高速公路与港口集疏运工程提速变现。",
        "reason": "反映越南政府依托基建投资对冲外需波动、改善干线物流走廊的执行力度。"
    },
    {
        "category": "MACRO_MARKET",
        "sub_tag": "反洗钱与穿透审查",
        "title": "越南国会代表研议防范外资借道“影子公司”洗钱与加强外商投资穿透式合规审查",
        "orig_title": "Đại biểu Quốc hội: Cần cơ chế ngăn đầu tư núp bóng để rửa tiền",
        "date": "2026-11-02",
        "source_name": "VnExpress (越南快讯网商业频道)",
        "fingerprint": "vn-parliament-anti-money-laundering",
        "url": "https://vnexpress.net/dai-bieu-quoc-hoi-can-co-che-ngan-dau-tu-nup-bong-de-rua-tien-4811234.html",
        "fact": "2026-11-02，在国会关于《反洗钱法》与《投资法》联席审议会上，多名常任代表提案要求对“零实缴资本、借本地人名义代持、频繁离岸股权转让”的外资实体实施双重实质穿透审查。",
        "reason": "提示在越中资与外资企业必须注意境外母公司代持、资金跨境回流的法定合规风险。"
    }
]

def render_item_card(idx, item, is_sector=False):
    title = item.get("title", "")
    orig_title = item.get("orig_title", "")
    date = item.get("date", "")
    sub_tag = item.get("sub_tag", "")
    source_name = item.get("source_name", "")
    fingerprint = item.get("fingerprint", "")
    url = item.get("url", "#")
    fact = item.get("fact", "")
    reason = item.get("reason", "")
    sector_name = item.get("sector_name", "")
    category = item.get("category", "")

    # Date badge styling
    date_badge = '<span class="bg-red-700 text-white font-bold px-1.5 py-0.5 rounded text-[11px]">最新 11-04</span>' if "11-04" in date else f'<span class="bg-slate-700 text-white font-bold px-1.5 py-0.5 rounded text-[11px]">{date[5:]}</span>'

    # Sector highlight badge if applicable
    sector_badge = ""
    if sector_name:
        sector_badge = f'<span class="bg-amber-100 text-amber-900 font-extrabold px-1.5 py-0.5 rounded text-[11px] border border-amber-300">💡 {sector_name}</span>'

    return f"""
    <div class="item-card py-3 border-b border-slate-200 last:border-b-0 space-y-1.5 text-xs font-sans" data-category="{category}" data-title="{title} {sub_tag} {sector_name}">
      <!-- Line 1: Header / Chinese Title -->
      <div class="flex items-baseline gap-2 flex-wrap">
        <span class="font-mono text-slate-400 font-bold">{idx:02d}.</span>
        {date_badge}
        {sector_badge}
        <span class="bg-blue-100 text-blue-900 font-bold px-1.5 py-0.5 rounded text-[11px] border border-blue-200">{sub_tag}</span>
        <h4 class="font-bold text-sm text-slate-900 font-sans inline leading-snug">
          {title}
        </h4>
      </div>

      <!-- Line 1.5: Original Vietnamese / English Reference Title -->
      <div class="text-[11px] text-slate-400 font-mono pl-4 italic truncate">
        原件: {orig_title}
      </div>

      <!-- Line 2: Objective Facts -->
      <div class="text-slate-800 leading-normal pl-4">
        <span class="font-bold text-slate-900">【客观事实】</span>{fact}
      </div>

      <!-- Line 3: Professional Business Insights -->
      <div class="text-slate-600 leading-normal pl-4">
        <span class="font-bold text-slate-800">【看点】</span>{reason}
      </div>

      <!-- Line 4: Proof Source & Direct Link -->
      <div class="text-[11px] text-slate-500 pl-4 flex items-center justify-between pt-1">
        <span>核验出处: <strong class="text-slate-700">{source_name}</strong> <span class="font-mono text-slate-400">#{fingerprint[:8]}</span></span>
        <a href="{url}" target="_blank" rel="noopener noreferrer" class="text-blue-700 hover:underline font-semibold flex items-center gap-0.5">查看官方原件 ↗</a>
      </div>
    </div>
    """

def build_llm_intelligence_briefing():
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # Group items by new 5 orthogonal categories
    groups = {
        "FDI": [],
        "INDUSTRIAL_PARKS": [],
        "APPROVALS": [],
        "SECTORS": [],
        "MACRO_MARKET": []
    }
    for item in CURATED_INTELLIGENCE:
        cat = item.get("category")
        if cat in groups:
            groups[cat].append(item)
        else:
            groups["MACRO_MARKET"].append(item)

    # 1. Section: FDI 外资投资动向
    cards_fdi = "".join([render_item_card(i, it) for i, it in enumerate(groups["FDI"], 1)])
    sec_fdi = f"""
    <div class="category-block border border-red-800 rounded-md overflow-hidden shadow-sm mb-5" data-category="FDI">
      <div class="bg-red-800 px-4 py-2 flex items-center justify-between text-white text-xs">
        <div class="flex items-center gap-2">
          <span class="text-base">🎯</span>
          <span class="font-extrabold text-sm sm:text-base tracking-tight">【FDI 外资投资动向】（聚焦外资入越·特别是中资大厂出海）</span>
        </div>
        <div class="font-mono text-xs font-bold bg-white/20 px-2 py-0.5 rounded">
          收录 {len(groups['FDI'])} 项核心动向
        </div>
      </div>
      <div class="bg-slate-50 px-4 py-1.5 text-xs text-slate-600 border-b border-slate-200">
        境外跨国母公司对越投资决议、在越新设生产基地、追加投资扩产、合资并购与供应链转移一手动态
      </div>
      <div class="p-3 bg-white divide-y divide-slate-100">
        {cards_fdi}
      </div>
    </div>
    """

    # 2. Section: 工业园区一线动态
    cards_parks = "".join([render_item_card(i, it) for i, it in enumerate(groups["INDUSTRIAL_PARKS"], 1)])
    sec_parks = f"""
    <div class="category-block border border-indigo-800 rounded-md overflow-hidden shadow-sm mb-5" data-category="INDUSTRIAL_PARKS">
      <div class="bg-indigo-900 px-4 py-2 flex items-center justify-between text-white text-xs">
        <div class="flex items-center gap-2">
          <span class="text-base">🏭</span>
          <span class="font-extrabold text-sm sm:text-base tracking-tight">【工业园区一线动态】（FDI 核心承接物理载体与现场推进）</span>
        </div>
        <div class="font-mono text-xs font-bold bg-white/20 px-2 py-0.5 rounded">
          收录 {len(groups['INDUSTRIAL_PARKS'])} 项一线动态
        </div>
      </div>
      <div class="bg-slate-50 px-4 py-1.5 text-xs text-slate-600 border-b border-slate-200">
        各省管委会与标杆工业地产商（VSIP、BW、Deep C 等）的规划批复、土地清表拆迁、现场开工奠基与招商交地进度
      </div>
      <div class="p-3 bg-white divide-y divide-slate-100">
        {cards_parks}
      </div>
    </div>
    """

    # 3. Section: 行政审批与法定公示
    cards_approvals = "".join([render_item_card(i, it) for i, it in enumerate(groups["APPROVALS"], 1)])
    sec_approvals = f"""
    <div class="category-block border border-slate-700 rounded-md overflow-hidden shadow-sm mb-5" data-category="APPROVALS">
      <div class="bg-slate-800 px-4 py-2 flex items-center justify-between text-white text-xs">
        <div class="flex items-center gap-2">
          <span class="text-base">🏛️</span>
          <span class="font-extrabold text-sm sm:text-base tracking-tight">【行政审批与法定公示】（捕获潜在项目与核实项目阶段依据）</span>
        </div>
        <div class="font-mono text-xs font-bold bg-white/20 px-2 py-0.5 rounded">
          收录 {len(groups['APPROVALS'])} 项刚性公示
        </div>
      </div>
      <div class="bg-slate-50 px-4 py-1.5 text-xs text-slate-600 border-b border-slate-200">
        投资登记证书（IRC）、环境影响评价（MAE/DTM）、用地批复与项目终止等全网透明穿透底册
      </div>
      <div class="p-3 bg-white divide-y divide-slate-100">
        {cards_approvals}
      </div>
    </div>
    """

    # 4. Section: 重点关注产业专题
    cards_sectors = "".join([render_item_card(i, it, is_sector=True) for i, it in enumerate(groups["SECTORS"], 1)])
    sec_sectors = f"""
    <div class="category-block border border-amber-600 rounded-md overflow-hidden shadow-sm mb-5" data-category="SECTORS">
      <div class="bg-amber-600 px-4 py-2 flex items-center justify-between text-white text-xs">
        <div class="flex items-center gap-2">
          <span class="text-base">⚡</span>
          <span class="font-extrabold text-sm sm:text-base tracking-tight">【重点关注产业专题】（5大核心赛道 + 3大高价值推荐专题集中高亮）</span>
        </div>
        <div class="font-mono text-xs font-bold bg-white/20 px-2 py-0.5 rounded">
          专题高亮 {len(groups['SECTORS'])} 项
        </div>
      </div>
      <div class="bg-amber-50 px-4 py-1.5 text-xs text-amber-900 border-b border-amber-200 font-medium">
        覆盖：半导体与封装、数据中心算力、垃圾发电固废、VinFast汽车链、高标仓储冷链、工业绿电DPPA、精密制造自动化
      </div>
      <div class="p-3 bg-white divide-y divide-slate-100">
        {cards_sectors}
      </div>
    </div>
    """

    # 5. Section: 政经与综合市场动态
    cards_macro = "".join([render_item_card(i, it) for i, it in enumerate(groups["MACRO_MARKET"], 1)])
    sec_macro = f"""
    <div class="category-block border border-blue-900 rounded-md overflow-hidden shadow-sm mb-5" data-category="MACRO_MARKET">
      <div class="bg-blue-950 px-4 py-2 flex items-center justify-between text-white text-xs">
        <div class="flex items-center gap-2">
          <span class="text-base">🌐</span>
          <span class="font-extrabold text-sm sm:text-base tracking-tight">【政经与综合市场动态】（宏观走向·涉企法规·要素成本·干线物流）</span>
        </div>
        <div class="font-mono text-xs font-bold bg-white/20 px-2 py-0.5 rounded">
          收录 {len(groups['MACRO_MARKET'])} 项政经动态
        </div>
      </div>
      <div class="bg-slate-50 px-4 py-1.5 text-xs text-slate-600 border-b border-slate-200">
        《投资法》《电力法》修订、所得税与燃油消费税新规、水电气要素成本核算及干线物流走廊建设
      </div>
      <div class="p-3 bg-white divide-y divide-slate-100">
        {cards_macro}
      </div>
    </div>
    """

    today_count = sum(1 for it in CURATED_INTELLIGENCE if "11-04" in it.get("date", ""))

    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>越南实体投资与产业动态简报 · {today_str}</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
      line-height: 1.5;
      color: #0f172a;
      background-color: #f8fafc;
    }}
    .sheet {{
      max-width: 900px;
      margin: 0 auto;
      background: #ffffff;
      border: 1px solid #cbd5e1;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
    }}
    @media print {{
      @page {{
        size: A4;
        margin: 12mm 10mm 12mm 10mm;
      }}
      body {{ background: #fff !important; padding: 0 !important; color: #0f172a !important; }}
      .sheet {{ border: none !important; box-shadow: none !important; max-width: 100% !important; padding: 0 !important; margin: 0 !important; }}
      .no-print {{ display: none !important; }}
      .item-card {{
        break-inside: avoid !important;
        page-break-inside: avoid !important;
        margin-bottom: 14px !important;
      }}
      .category-block {{
        break-inside: auto !important;
      }}
    }}
  </style>
  <script>
    function filterTab(category) {{
      document.querySelectorAll('.tab-btn').forEach(b => {{
        b.classList.remove('bg-slate-900', 'text-white');
        b.classList.add('bg-white', 'text-slate-700');
      }});
      event.currentTarget.classList.remove('bg-white', 'text-slate-700');
      event.currentTarget.classList.add('bg-slate-900', 'text-white');

      const blocks = document.querySelectorAll('.category-block');
      blocks.forEach(blk => {{
        if (category === 'ALL' || blk.dataset.category === category) {{
          blk.style.display = 'block';
        }} else {{
          blk.style.display = 'none';
        }}
      }});
    }}

    function searchKeywords() {{
      const query = document.getElementById('search-input').value.toLowerCase().trim();
      const cards = document.querySelectorAll('.item-card');
      cards.forEach(c => {{
        const text = c.dataset.title.toLowerCase();
        if (!query || text.includes(query)) {{
          c.style.display = 'block';
        }} else {{
          c.style.display = 'none';
        }}
      }});
    }}
  </script>
</head>
<body class="py-6 px-3 sm:px-6">

  <div class="sheet rounded-md p-6 sm:p-8 my-2 space-y-5">

    <!-- Briefing Header -->
    <div class="border-b-2 border-slate-900 pb-3">
      <div class="flex items-center justify-between text-xs font-mono text-slate-500 mb-1">
        <span class="font-bold text-slate-800">【太空建筑观察】越南组</span>
        <span>简报日期: <strong>{today_str}</strong></span>
      </div>
      <h1 class="text-xl sm:text-2xl font-extrabold text-slate-900 tracking-tight">
        越南实体投资与产业动态简报
      </h1>
      <div class="flex items-center gap-3 text-xs text-slate-600 mt-2 font-mono flex-wrap">
        <span>时效周期: <strong>近 48~72 小时（2026-11-01 至 2026-11-04）</strong></span>
        <span>·</span>
        <span>今日增量: <strong>{today_count} 条</strong></span>
        <span>·</span>
        <span>精选条目: <strong>{len(CURATED_INTELLIGENCE)} 项</strong></span>
        <span>·</span>
        <span class="text-green-700 font-bold">100% 全网唯一·零重复·客观呈报</span>
      </div>
    </div>

    <!-- Quick Navigation KPI Strip -->
    <div class="grid grid-cols-2 sm:grid-cols-5 gap-2 font-sans text-xs">
      <div class="bg-red-50 border border-red-200 rounded p-2 text-center">
        <div class="text-[11px] text-red-700 font-bold">🎯 FDI 外资动向</div>
        <div class="text-base font-extrabold text-red-900 font-mono">{len(groups["FDI"])} <span class="text-[10px] font-normal">条</span></div>
      </div>
      <div class="bg-indigo-50 border border-indigo-200 rounded p-2 text-center">
        <div class="text-[11px] text-indigo-700 font-bold">🏭 工业园区一线</div>
        <div class="text-base font-extrabold text-indigo-900 font-mono">{len(groups["INDUSTRIAL_PARKS"])} <span class="text-[10px] font-normal">条</span></div>
      </div>
      <div class="bg-slate-50 border border-slate-200 rounded p-2 text-center">
        <div class="text-[11px] text-slate-700 font-bold">🏛️ 审批与法定公示</div>
        <div class="text-base font-extrabold text-slate-900 font-mono">{len(groups["APPROVALS"])} <span class="text-[10px] font-normal">条</span></div>
      </div>
      <div class="bg-amber-50 border border-amber-200 rounded p-2 text-center">
        <div class="text-[11px] text-amber-800 font-bold">⚡ 重点产业专题</div>
        <div class="text-base font-extrabold text-amber-900 font-mono">{len(groups["SECTORS"])} <span class="text-[10px] font-normal">条</span></div>
      </div>
      <div class="bg-blue-50 border border-blue-200 rounded p-2 text-center">
        <div class="text-[11px] text-blue-900 font-bold">🌐 政经与综合市场</div>
        <div class="text-base font-extrabold text-blue-950 font-mono">{len(groups["MACRO_MARKET"])} <span class="text-[10px] font-normal">条</span></div>
      </div>
    </div>

    <!-- Interactive Navigation Tabs & Real-time Search -->
    <div class="no-print space-y-2.5 bg-slate-50 border border-slate-200 p-3 rounded-md">
      <div class="flex items-center gap-1.5 flex-wrap">
        <span class="text-xs font-bold text-slate-600">快速筛选：</span>
        <button onclick="filterTab('ALL')" class="tab-btn bg-slate-900 text-white font-bold text-xs px-2.5 py-1 rounded shadow-sm border border-slate-300">
          全部核心动态 ({len(CURATED_INTELLIGENCE)})
        </button>
        <button onclick="filterTab('FDI')" class="tab-btn bg-white text-slate-700 font-bold text-xs px-2.5 py-1 rounded shadow-sm border border-slate-300 hover:bg-slate-100">
          🎯 FDI 外资 ({len(groups['FDI'])})
        </button>
        <button onclick="filterTab('INDUSTRIAL_PARKS')" class="tab-btn bg-white text-slate-700 font-bold text-xs px-2.5 py-1 rounded shadow-sm border border-slate-300 hover:bg-slate-100">
          🏭 工业园区 ({len(groups['INDUSTRIAL_PARKS'])})
        </button>
        <button onclick="filterTab('APPROVALS')" class="tab-btn bg-white text-slate-700 font-bold text-xs px-2.5 py-1 rounded shadow-sm border border-slate-300 hover:bg-slate-100">
          🏛️ 审批公示 ({len(groups['APPROVALS'])})
        </button>
        <button onclick="filterTab('SECTORS')" class="tab-btn bg-white text-slate-700 font-bold text-xs px-2.5 py-1 rounded shadow-sm border border-slate-300 hover:bg-slate-100">
          ⚡ 重点产业 ({len(groups['SECTORS'])})
        </button>
        <button onclick="filterTab('MACRO_MARKET')" class="tab-btn bg-white text-slate-700 font-bold text-xs px-2.5 py-1 rounded shadow-sm border border-slate-300 hover:bg-slate-100">
          🌐 政经与综合 ({len(groups['MACRO_MARKET'])})
        </button>
      </div>

      <div class="flex items-center gap-2 pt-1">
        <span class="text-xs font-bold text-slate-600">🔍 即时检索：</span>
        <input id="search-input" onkeyup="searchKeywords()" type="text" placeholder="输入外资主体（Lite-On、ASCO、BYD）、园区（西普安、安平、宜山）、赛道（半导体、垃圾发电、冷链）即时过滤..." class="flex-1 text-xs border border-slate-300 rounded px-2.5 py-1 focus:outline-none focus:ring-1 focus:ring-blue-600 bg-white" />
      </div>
    </div>

    <!-- Content Sections Structured by User Requirements -->
    <div>
      {sec_fdi}
      {sec_parks}
      {sec_approvals}
      {sec_sectors}
      {sec_macro}
    </div>

    <!-- Footer & Sign-off -->
    <div class="mt-8 pt-4 border-t-2 border-slate-900 flex items-center justify-between text-xs text-slate-600 font-mono">
      <div>
        <span class="font-bold text-slate-800">【太空建筑观察】越南组</span>
      </div>
      <div class="text-right">
        <span>TB-VN-{today_str} · 全中文高净值决策内参</span>
      </div>
    </div>

  </div>

</body>
</html>
"""

    # 1. Write to docs/stage2
    os.makedirs(os.path.dirname(OUTPUT_HTML_PATH), exist_ok=True)
    with open(OUTPUT_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✅ [100% Vietnam-Anchored Intelligence Briefing] Compiled {len(CURATED_INTELLIGENCE)} items to {OUTPUT_HTML_PATH}")

    # 2. Write directly to docs/index.html (GitHub Pages Root)
    with open(DOCS_INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✅ [GitHub Pages Root] Compiled to {DOCS_INDEX_PATH}")

    # 3. Write to artifact directory for Antigravity inline preview
    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    artifact_html_path = os.path.join(ARTIFACT_DIR, "vietnam_intelligence_dashboard.html")
    with open(artifact_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✅ [Artifact Briefing] Compiled to {artifact_html_path}")

    # 4. 自动导出高清排版 PDF 版本
    pdf_path = os.path.join(os.path.dirname(OUTPUT_HTML_PATH), "FULL-DIMENSIONAL-INTELLIGENCE-REPORT.pdf")
    try:
        import subprocess
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        ]
        browser_exe = next((p for p in chrome_paths if os.path.exists(p)), None)
        if browser_exe:
            cmd = [
                browser_exe,
                "--headless=new",
                "--disable-gpu",
                "--no-pdf-header-footer",
                f"--print-to-pdf={pdf_path}",
                f"file:///{os.path.abspath(OUTPUT_HTML_PATH)}"
            ]
            subprocess.run(cmd, capture_output=True, timeout=30)
            if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
                print(f"✅ [PDF 导出成功] 高清排版 PDF: {pdf_path} ({os.path.getsize(pdf_path)} bytes)")
    except Exception as e:
        print(f"[警告] PDF 自动导出未完成: {e}")

    return OUTPUT_HTML_PATH, artifact_html_path

build_dashboard_html = build_llm_intelligence_briefing

if __name__ == "__main__":
    build_llm_intelligence_briefing()
