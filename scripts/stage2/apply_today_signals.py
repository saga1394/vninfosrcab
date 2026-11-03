# -*- coding: utf-8 -*-
"""
Daily Intelligence Signal Processor for 2026-11-03 Inspection.
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
    # 1. Lite-On $320M injection into Vietnam subsidiaries
    {
        "fp_prefix": "9c3b93b8",
        "dimension_code": "D1",
        "entity_name": "光宝科技 (Lite-On Technology / 2301.TW)",
        "province": "海阳省 / 广宁省 (北越电子产业走廊)",
        "severity_level": "HIGH",
        "summary_insight": "【台资龙头重大资本加码】台湾知名电源与光电半导体巨头光宝科技向越南两家全资子公司注资 3.2 亿美元。该笔巨额重资产投资重点用于扩建 AI 服务器高功率电源、云端运算装备及智能汽车电子产能，显示在欧美科技客户供应链安全驱动下，台资核心算力硬件产业链向北越聚集的确定性进一步增强。"
    },
    # 2. Vietnam Paper Industry Strategy to 2045 (Decision 2082/QĐ-TTg)
    {
        "fp_prefix": "233b86d8",
        "dimension_code": "D4",
        "entity_name": "越南政府总理府 / 工贸部",
        "province": "全国",
        "severity_level": "HIGH",
        "summary_insight": "【国家级顶层产业战略重磅出台】越南政府常务副总理范嘉宿正式签署第 2082/QĐ-TTg 号决定，批准《至2045年造纸工业发展战略》。战略明确要求淘汰落后高污染产能，集约化布局现代绿色包装纸基地。这一政策顶层定调直接解释了近期顺兴、春梅、同进、灵江等一批大型纸业项目集中向环境部申办排污许可的深层法规动因。"
    },
    # 3. Law Amending Investment Law: Cutting 62 Conditional Sectors
    {
        "fp_prefix": "3e11565a",
        "dimension_code": "D4",
        "entity_name": "越南国会 / 计划投资部 / 同奈省管委会",
        "province": "全国 / 同奈省",
        "severity_level": "HIGH",
        "summary_insight": "【全国性外资营商准入历史性突破】同奈省工业区管委会通报《2026年投资法若干条款修改补充法》最新细则：越南正式大幅削减 62 个有条件投资经营行业门槛（自2027年3月1日全面施行）。此举将大幅压缩中外资企业落地审批周期，打破诸多行业行政壁垒，显著提升在越建厂投资便利度。"
    },
    # 4. BW Industrial $120M JV for High-Quality For-Rent Industrial Portfolio
    {
        "fp_prefix": "6740658f",
        "dimension_code": "D3",
        "entity_name": "BW Industrial Development (华平投资与Becamex合资)",
        "province": "越南核心经济区 (河内/海防/平阳/同奈)",
        "severity_level": "HIGH",
        "summary_insight": "【工业地产与供应链承载力升级】越南领先的高标工业地产平台 BW Industrial 与全球主权机构达成 1.2 亿美元战略合资，在越南主要经济带开发高标租赁厂房与现代物流枢纽。这为出海中资及跨国高端制造提供了‘即租即投产’的高抗风险物理载体，降低初始固定资产沉没成本。"
    },
    # 5. Oji Liquid Pak $110M Plant in Amata City Long Thanh
    {
        "fp_prefix": "d06f8fc3",
        "dimension_code": "D2",
        "entity_name": "日本王子控股 (Oji Liquid Pak / Oji Holdings)",
        "province": "同奈省 (Amata City Long Thành)",
        "severity_level": "HIGH",
        "summary_insight": "【外资高端消费供应链实体落地】日本百年纸业巨头王子控股斥资 1.1 亿美元在同奈省安美德隆城工业区建设无菌液体包装盒生产基地。该项目直接配套越南本土乳业（如 Vinamilk）、快消饮品龙头及出口东南亚的食品供应链，成为南部高端工业园区关键外资引资标杆。"
    },
    # 6. Cà Ná LNG Thermal Power Plant Feasibility Study
    {
        "fp_prefix": "1abdb20e",
        "dimension_code": "D2",
        "entity_name": "卡拿 LNG 液化天然气热电厂 (Cà Ná LNG)",
        "province": "庆和省 / 宁顺省 (中南部枢纽)",
        "severity_level": "MEDIUM",
        "summary_insight": "【南部电网压舱石工程关键进展】庆和省工贸厅完成卡拿 LNG 热电厂可行性研究报告（BCNCKT）初审。该项目作为国家第八版电力规划（PDP8）核心骨干电厂，建成后将向南部工业制造腹地（胡志明、平阳、同奈）提供高稳定性调峰基荷电力，有效防范枯水期极端缺电风险。"
    },
    # 7. Nhựa Tiền Phong (NTP) Repurposing Education Land into Housing
    {
        "fp_prefix": "7335cb32",
        "dimension_code": "D1",
        "entity_name": "先锋塑料 (CTCP Nhựa Thiếu niên Tiền Phong / HNX: NTP)",
        "province": "海防市 (02 An Đà, Ngô Quyền)",
        "severity_level": "MEDIUM",
        "summary_insight": "【建材实体资本运作与资产盘活】海防塑料管材龙头先锋塑料拟对其动工 18 个月的 3.74 公顷先锋教育综合体进行规划用途变更，转为商业住宅项目开发。此举反映制造业实体在主营平稳期盘活核心城市优质存量土地资产、寻求资产重估与现金流回补的资本运作诉求。"
    },
    # 8. Fountain Set (福田实业) 81% Acquisition of Vietnam Company
    {
        "fp_prefix": "ef30d06e",
        "dimension_code": "D1",
        "entity_name": "福田实业 (00420.HK)",
        "province": "南部核心产业带",
        "severity_level": "MEDIUM",
        "summary_insight": "【纺织供应链跨国控股并购】港股针织布制造龙头福田实业发布股东通告，建议收购一家越南制造企业 81% 控股权并签署金融服务协议。中资纺织巨头通过收购成熟属地实体快速扩充原产地产能，规避贸易关税审查，强化东盟垂直供应链壁垒。"
    },
    # 9. Gia Binh 2 International Airport Urban Area EIA
    {
        "fp_prefix": "f4bada2c",
        "dimension_code": "D2",
        "entity_name": "嘉平 2 号国际航空临空新城",
        "province": "北宁省 (Gia Bình)",
        "severity_level": "MEDIUM",
        "summary_insight": "【临空枢纽基建法定环评公示】北宁嘉平 2 号国际机场临空新城项目正式在自然资源与环境部启动环境影响评价（ĐTM）公众咨询。该项目紧密配套北宁规划的现代化航空枢纽与冷链保税区，将带动北宁南部周边工业物流地块价值跃升。"
    },
    # 10. Vietnam Factories Ramping up Robot Acquisition
    {
        "fp_prefix": "1f9894e0",
        "dimension_code": "D3",
        "entity_name": "越南制造业各工业区制造企业",
        "province": "全国",
        "severity_level": "MEDIUM",
        "summary_insight": "【制造业自动化替代浪潮提速】越媒商业调查显示，面对近年劳工最低薪酬上涨、熟练技工争夺加剧与出口质检高标准，越南电子、机械制造企业采购工业机器人与自动化工作站意愿激增。专家提醒中小企业需做好自动化改造投资回报测算与技术人员储备。"
    },
    # 11. Global Shipping Lines Expanding to Rail Logistics
    {
        "fp_prefix": "7f64c5f4",
        "dimension_code": "D3",
        "entity_name": "MSC / CMA CGM / 越南铁路与多式联运网络",
        "province": "全国 / 海防港-内陆干线",
        "severity_level": "MEDIUM",
        "summary_insight": "【海铁多式联运生态竞争】全球航运巨头 MSC 与达飞轮船加速从传统港口海运向内陆铁路货运延伸投资，打通‘海防港-北宁/太原工业区’内陆集装箱班列直达走廊，有助于降低工业区企业端到端综合货运周转成本与公路拥堵风险。"
    },
    # 12. SK Hynix PCB Material Shortage
    {
        "fp_prefix": "8c6c0bd9",
        "dimension_code": "D3",
        "entity_name": "SK Hynix (SK海力士) / 电子时报",
        "province": "亚太 / 越北半导体配套走廊",
        "severity_level": "MEDIUM",
        "summary_insight": "【半导体高阶材料供求传导】SK海力士因生产放量加大 SOCAMM2 压缩附加内存模块 PCB 订单，上游基板原材料短缺推升价格。这进一步提升了以 LG Innotek 海防载板新厂为代表的先进封装基板产能的市场稀缺性与战略议价权。"
    },
    # 13. SMC Steel Trading Return to Profit
    {
        "fp_prefix": "76146805",
        "dimension_code": "D1",
        "entity_name": "SMC 商业投资股份公司 (HOSE: SMC)",
        "province": "胡志明市 / 南部大宗建材流通",
        "severity_level": "LOW",
        "summary_insight": "【大宗建材供应链出清与修复】历经一年多严峻的债务重组与坏账处置，越南老牌钢铁流通巨头 SMC 成功实现三季度扭亏为盈。这表明越南工程机械与工业建材流通链条的现金流压力正逐步筑底，供应链最危险的坏账传染期基本过去。"
    },
    # 14. Geleximco & Thai Binh University Partnership
    {
        "fp_prefix": "cf75d334",
        "dimension_code": "D3",
        "entity_name": "Geleximco 集团 / 太平大学",
        "province": "兴安省 / 太平省",
        "severity_level": "LOW",
        "summary_insight": "【重工企业产教融合用工储备】越南综合工业龙头 Geleximco 与太平大学签署 2026-2030 战略合作，重点围绕工业区装备制造、智能电气与汽车零部件产业定向培养高技能专业技术工人，为未来 5 年工业产能扩张储备属地劳工技能底盘。"
    }
]

def main():
    conn_raw = sqlite3.connect(RAW_DB_PATH)
    cur_raw = conn_raw.cursor()

    signals_to_commit = []
    for item in NEW_SIGNALS_CONFIG:
        fp_prefix = item["fp_prefix"]
        cur_raw.execute("""
            SELECT fingerprint, source_id, source_name, title, pub_date, url
            FROM raw_materials
            WHERE fingerprint LIKE ?
            LIMIT 1;
        """, (fp_prefix + "%",))
        row = cur_raw.fetchone()
        if row:
            fp, sid, sname, title, pdate, url = row
            d_code = item["dimension_code"]
            signals_to_commit.append({
                "signal_id": f"SIG-{d_code}-{fp[:8]}",
                "dimension_code": d_code,
                "title": title,
                "summary_insight": item["summary_insight"],
                "entity_name": item["entity_name"],
                "province": item["province"],
                "severity_level": item["severity_level"],
                "pub_date": pdate,
                "source_id": sid,
                "source_name": sname,
                "raw_fingerprint": fp,
                "url": url
            })
        else:
            print(f"⚠️ Fingerprint prefix {fp_prefix} not found in {RAW_DB_PATH}")

    conn_raw.close()

    print(f"Parsed {len(signals_to_commit)} valid signals from collector.db.")
    inserted = save_signals(signals_to_commit)
    print(f"Committed {inserted} fresh dimensional signals to projects.db.")

if __name__ == "__main__":
    main()
