# -*- coding: utf-8 -*-
"""
Daily Intelligence Signal Processor for 2026-11-04 Inspection.
Parses, reasons, and commits fresh multi-dimensional signals into projects.db.
"""

import os
import sys
import json
import sqlite3

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from scripts.stage2.save_signals import save_signals

RAW_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "daily", "collector.db"))

NEW_SIGNALS_CONFIG = [
    # 1. BCG Energy cutting stake in Cu Chi Waste-to-Power Plant
    {
        "fp_prefix": "be9e5114",
        "dimension_code": "D1",
        "entity_name": "BCG Energy (Bamboo Capital 旗下清洁能源旗舰) / Tâm Sinh Nghĩa",
        "province": "胡志明市 (TP.HCM / Củ Chi)",
        "severity_level": "HIGH",
        "summary_insight": "【垃圾发电核心赛道资本大幅撤退】越南清洁能源龙头 BCG Energy 拟对胡志明市古芝县 Tâm Sinh Nghĩa 垃圾焚烧发电厂（项目总投资 6.4 万亿越盾，折合约 2.6 亿美元）实施大幅减持，持股比例从 25% 削减至 5%，几近清仓退出。作为胡志明市规模最大的垃圾焚烧能源化特许经营标杆工程之一，核心出资方的急剧退场暴露出垃圾发电与环保特许经营项目在垃圾计量分类、上网电价结算（FiT）以及政企审批协同上面临的现实挑战，对计划在越投资环保基建、垃圾发电的企业构成极高警示。"
    },
    # 2. Coteccons acquires 64% controlling stake in AnPR
    {
        "fp_prefix": "78e16ca0",
        "dimension_code": "D1",
        "entity_name": "Coteccons (CTCP Xây dựng Coteccons / HOSE: CTD)",
        "province": "胡志明市 / 全国",
        "severity_level": "MEDIUM",
        "summary_insight": "【本土建筑承包龙头多元化资本运作】越南头部总包建筑巨头 Coteccons 将其在公关传播机构 AnPR 的持股比例提升至 64% 实现绝对控股。面对工业建筑及高端地产周期波动，本土总包龙头通过整合品牌传播、咨询及对外关系生态，旨在强化其在大客户全生命周期服务及工业园区代建招商中的综合话语权。"
    },
    # 3. PNJ shifts creditor structure with 700B VND loan from Chairman family
    {
        "fp_prefix": "ea82143d",
        "dimension_code": "D1",
        "entity_name": "PNJ (CTCP Vàng bạc Đá quý Phú Nhuận / HOSE: PNJ)",
        "province": "胡志明市 / 全国",
        "severity_level": "MEDIUM",
        "summary_insight": "【消费零售龙头资金链结构性调整】越南大型消费连锁龙头 PNJ 披露其获董事长家族提供 7000 亿越盾年利率 10% 的无抵押贷款，用于置换银行到期信贷额度。此举反映出四季度越南本土商业银行信贷额度偏紧、优质企业依托大股东借款进行流动性兜底的阶段性特征。"
    },
    # 4. Quang Trach Power Center 4,500 MW key energy complex
    {
        "fp_prefix": "c50566d8",
        "dimension_code": "D2",
        "entity_name": "EVN (越南电力集团) / 广泽电力中心 (Quảng Trạch I & II, LNG)",
        "province": "广平省 (Quảng Bình)",
        "severity_level": "HIGH",
        "summary_insight": "【国家骨干综合能源基地战略推进】越南政府网重磅通报中部广泽电力中心推进成果。该项目规划总装机容量达 4500 MW（包含超超临界燃煤、LNG 发电及配套清洁电站），未来规划扩展至 6000 MW。该综合能源枢纽作为国家电力规划第八版（PDP8）关键支撑点，承担向中部各大沿海经济区及 500kV 输电三回线输送高可靠基荷电力的关键任务，将从根本上缓解中部沿海制造基地的电力紧张预期。"
    },
    # 5. Ca Mau clears 72 pending projects, revokes 4
    {
        "fp_prefix": "1d2a111d",
        "dimension_code": "D2",
        "entity_name": "金瓯省委与人委会 / 招商引资项目实体",
        "province": "金瓯省 (Cà Mau)",
        "severity_level": "MEDIUM",
        "summary_insight": "【地方倒逼拖延项目出清与供地合规整肃】金瓯省针对辖区内 72 个进展迟缓的投资项目展开“零容忍”专项清理，已收回注销 4 个囤地及无法履约项目的投资主张，并对 33 个阻滞项目倒排工期。这一信号反映出越南地方政府对招商引资“占地不建、虚报投资”的清理风暴正在升级，督促出海实体拿地后必须严格把控土地出让合同约定的动工与竣工时间节点，防范被依法无偿收回土地权属。"
    },
    # 6. Thai Nguyen Industrial Zones digital twin bidding
    {
        "fp_prefix": "6ecd526d",
        "dimension_code": "D2",
        "entity_name": "太原省工业区管委会 (BQL các KCN Thái Nguyên)",
        "province": "太原省 (Thái Nguyên)",
        "severity_level": "MEDIUM",
        "summary_insight": "【北越核心电子集群智慧园区升级】太原省工业区管委会启动工业区数字化转型与数字孪生底座标段招标。太原省作为三星、富士康、领益智造等跨国电子产业链核心聚集地，正通过数字孪生技术全面整合工业区能耗监测、排污在线监管与厂房资产管理，推动传统园区向高精度数字园区演进。"
    },
    # 7. Hai Phong Vice Chairman visits industrial park enterprises
    {
        "fp_prefix": "436905c3",
        "dimension_code": "D2",
        "entity_name": "海防市人委会 (UBND TP Hải Phòng) / 各工业园区",
        "province": "海防市 (Hải Phòng)",
        "severity_level": "MEDIUM",
        "summary_insight": "【北越沿海制造枢纽现场纾困保交付】海防市主管工业与投资的市领导率发改、工贸与经济区管委会深入一线，重点协调年内投产项目的供电、物流通关与劳务招工诉求，保障外资工业项目四季度产能满负荷释放。"
    },
    # 8. Tesla and Samsung protest US tariff hike on Vietnam
    {
        "fp_prefix": "940aaf35",
        "dimension_code": "D3",
        "entity_name": "特斯拉 (Tesla) / 三星电子 (Samsung) / 美国商务部",
        "province": "全国 / 北宁 / 太原 / 胡志明",
        "severity_level": "HIGH",
        "summary_insight": "【海外强传导核心标杆：跨国巨头联手抗击关税壁垒】全球电动汽车龙头特斯拉与消费电子龙头三星正式向美方提出申诉，坚决反对对产自越南的相关工业品加征新关税。三星在越投资超 228 亿美元且占其全球手机产量近半，特斯拉在越采购大量电子元器件与车载线束。两大龙头的联合抗议直接印证了在越制造基地在全球供应链中的不可替代性，同时也预警了美国在“原产地穿透与洗产地监管”上的加码风险，对出海中资供应链企业的原产地增值率（Local Value Content）提出了更苛刻的合规考验。"
    },
    # 9. PC brands shifting production back to China from Southeast Asia
    {
        "fp_prefix": "77ee5d1c",
        "dimension_code": "D3",
        "entity_name": "越南工商联 (VCCI) / 全球主要 PC 代工厂商",
        "province": "越南电子走廊 vs 中国产业带",
        "severity_level": "HIGH",
        "summary_insight": "【供应链配套深水区理性反思】越南工商会转引国际产业供应链重磅报告，披露部分外迁至越南及东南亚的 PC 品牌因精密结构件、高阶模具、高频连接器本地缺乏二级配套，导致跨境料件周转成本高企、良品率爬坡过慢，部分低利润机型出现回流中国组装或暂缓追加产线。这清晰表明单纯“组装产能出海”红利正在递减，唯有自带成熟模具、注塑及精密五金配套的“抱团式出海”方能构建稳固壁垒。"
    },
    # 10. Samsung Electro-Mechanics LTA tops 5T KRW
    {
        "fp_prefix": "337406ca",
        "dimension_code": "D3",
        "entity_name": "三星电机 (Samsung Electro-Mechanics / SEMCO)",
        "province": "太原省 (Thái Nguyên - Yên Bình)",
        "severity_level": "MEDIUM",
        "summary_insight": "【AI 服务器算力硬件景气度向在越产线传导】韩国三星电机（SEMCO）披露其今年签署的高端 MLCC 与 AI 服务器电容长期供货协议（LTA）突破 5 万亿韩元。三星电机在越南太原安平工业区的载板及元器件基地系其全球高阶产能核心支柱，此举直接巩固了太原省在全球 AI 高性能服务器供应链中的底层供应地位。"
    },
    # 11. Airbus forecasts 1,000 aircraft needed in Vietnam over next 20 years
    {
        "fp_prefix": "a3e646b9",
        "dimension_code": "D3",
        "entity_name": "空中客车 (Airbus) / 越南民航局",
        "province": "全国",
        "severity_level": "MEDIUM",
        "summary_insight": "【中长期航空交通与临空物流爆发预期】空客发布 2026 最新民航展望，预计越南航空客运增速高居全球前列，机队规模需在现有基础上扩容 1000 架客机。该中长期规划直接为龙城国际机场（Long Thành）、嘉平机场（Gia Bình）等临空经济区及现代航空货运物流港提供了巨大的市场运力承载预期。"
    },
    # 12. Decision 3151/QD-BTC: Tax Reform Action Plan 2026-2030
    {
        "fp_prefix": "0cc958ac",
        "dimension_code": "D4",
        "entity_name": "越南财政部 (Bộ Tài chính)",
        "province": "全国",
        "severity_level": "HIGH",
        "summary_insight": "【2026-2030 国家税制改革顶层路线图发布】越南财政部签发第 3151/QĐ-BTC 号决定，对未来 5 年税收体系重构作出刚性部署。核心看点包括：全面贯彻 OECD 全球最低税 15% 顶层规则并建立非税财务激励基金（对冲税收优惠失效）、深化电子发票与跨境电商增值税穿透征管、严格规制跨国关联方交易转让定价（TP）。出海企业须根据该计划重新测算未来五年的税负模型，健全合规抵扣凭据链。"
    },
    # 13. Electricity Law Amendment: breaking planning and DPPA bottlenecks
    {
        "fp_prefix": "e2e98f1a",
        "dimension_code": "D4",
        "entity_name": "越南国会 / 工贸部 (Bộ Công Thương)",
        "province": "全国",
        "severity_level": "HIGH",
        "summary_insight": "【电力能源法典重大修法突破】越南国会重点审议《电力法修改法草案》。此次修改直击痛点：放开可再生能源（海上风电、光伏）与独立电厂在电网建设和售电环节的民营/外资准入，明确双边绿电直接购售电协议（DPPA）结算细则，理顺储能与调峰电价机制。若法案如期通过，将从法律层面彻底解决外资高科技大厂对 100% 绿色电力认证（RE100）与用电稳定性的刚性关切。"
    },
    # 14. Hai Phong Administrative Reform Index 2026
    {
        "fp_prefix": "119bf1cf",
        "dimension_code": "D4",
        "entity_name": "海防市人委会 (UBND TP Hải Phòng)",
        "province": "海防市",
        "severity_level": "MEDIUM",
        "summary_insight": "【地方营商环境指标化倒逼】海防市作为北越吸引 FDI 领头羊，率先推出包含多项新增指标的 2026 行政改革考评体系，重点针对规划许可、施工报建、环评审批设立限时办结与超时问责机制，持续保持其在省级竞争力指数（PCI）中的第一梯队优势。"
    },
    # 15. Fuel price cut on Nov 3
    {
        "fp_prefix": "e63362dd",
        "dimension_code": "D4",
        "entity_name": "工贸部 / 财政部",
        "province": "全国",
        "severity_level": "LOW",
        "summary_insight": "【运营物流成本短期松动】成品油迎近年最大降幅，结合 11 月 1 日起汽油特别消费税降至 0% 的新政，直接降低内陆集卡干线与干散货疏港物流运输成本。"
    },
    # 16. First 'Make in Vietnam' Security Chip Unveiled
    {
        "fp_prefix": "b0c772c7",
        "dimension_code": "D5",
        "entity_name": "越南本土半导体研发机构 (Viettel / FPT Semiconductor)",
        "province": "全国 / 河内 (Khu CNC Hòa Lạc)",
        "severity_level": "HIGH",
        "summary_insight": "【国家半导体战略硬科技自主化里程碑】2026 年 11 月 3 日，越南正式发布首款完全由本土工程师团队自主架构设计的专用安全芯片。实测显示其高速加密算法处理效率较通用芯片提升 10 倍，主要供给国内电力自动化终端、工业物联网边缘节点及移动通信基站。这标志着越南在承接外资封测（如安靠 Amkor、英特尔 Intel）之余，其本土半导体“芯片设计（Fabless）”种子生态迈出关键一步。"
    },
    # 17. Public Investment Disbursement reaches 76.6% in 10 Months
    {
        "fp_prefix": "ed79c9bf",
        "dimension_code": "D5",
        "entity_name": "越南财政部 (Bộ Tài chính)",
        "province": "全国",
        "severity_level": "MEDIUM",
        "summary_insight": "【宏观基建落地进度超预期】截至 2026 年 10 月 31 日，越南全国公共投资解付率已达总理下达计划的 76.6%，创近五年同期新高。南北高速公路、胡志明三环线、海防跨海大桥等一批重点交通骨干工程加速变现为实物物流能力，有力对冲外需波动，改善制造业内陆集疏运效率。"
    },
    # 18. Hai Phong Master Marine Economy Plan to 2045
    {
        "fp_prefix": "33fb0e3e",
        "dimension_code": "D5",
        "entity_name": "海防市人委会 (UBND TP Hải Phòng)",
        "province": "海防市",
        "severity_level": "MEDIUM",
        "summary_insight": "【北越核心出海口空间格局定型】海防市出台海洋强市长远纲要，将重点依托莱县（Lạch Huyện）深水港区与南庭武（Nam Đình Vũ）免税保税区，建设绿色深水集装箱港口群与国家级海洋工程装备制造基地，确立北越国际航运枢纽地位。"
    }
]

def apply_signals():
    conn_raw = sqlite3.connect(RAW_DB_PATH)
    cur_raw = conn_raw.cursor()

    signals_to_commit = []
    for conf in NEW_SIGNALS_CONFIG:
        fp_prefix = conf["fp_prefix"]
        cur_raw.execute("""
            SELECT fingerprint, source_id, source_name, title, pub_date, url
            FROM raw_materials
            WHERE fingerprint LIKE ?
            LIMIT 1
        """, (f"{fp_prefix}%",))
        row = cur_raw.fetchone()
        if not row:
            print(f"⚠️ Warning: Could not find raw record for prefix {fp_prefix}")
            continue

        sig_data = {
            "signal_id": f"SIG-{conf['dimension_code']}-{row[0][:8]}",
            "dimension_code": conf["dimension_code"],
            "title": row[3],
            "summary_insight": conf["summary_insight"],
            "entity_name": conf.get("entity_name"),
            "province": conf.get("province"),
            "severity_level": conf.get("severity_level", "MEDIUM"),
            "pub_date": row[4],
            "source_id": row[1],
            "source_name": row[2],
            "raw_fingerprint": row[0],
            "url": row[5]
        }
        signals_to_commit.append(sig_data)

    conn_raw.close()

    print(f"Prepared {len(signals_to_commit)} signals for persistence.")
    inserted = save_signals(signals_to_commit)
    print(f"✅ Successfully persisted {inserted} fresh signals into projects.db.")

if __name__ == "__main__":
    apply_signals()
