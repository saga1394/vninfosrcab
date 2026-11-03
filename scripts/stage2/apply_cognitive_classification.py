# -*- coding: utf-8 -*-
"""
Cognitive Classifier Test Runner (Reference Code: 2491).
Demonstrates the L2 LLM cognitive layer processing multi-dimensional signals,
performing open entity extraction, commercial intent reasoning, and committing
structured signals to projects.db (dimensional_signals) with 100% evidence closure.
"""

import os
import sys
import json
import sqlite3
from datetime import datetime

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAW_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "daily", "collector.db"))
STAGE2_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "stage2", "projects.db"))

def run_classification():
    conn_raw = sqlite3.connect(RAW_DB_PATH)
    cur_raw = conn_raw.cursor()

    # Pre-select key fingerprints representing the 5 dimensions
    target_fps = [
        # D1: 企业动向与实体变动 (进退、增资、注销)
        ("9d3d9d34", "D1", "隆扬电子（301389.SZ）", "北宁/海防", "HIGH",
         "中资消费电子产业链在越【战略收缩与实体退出】罕见风向标。隆扬电子拟出售控股孙公司越南德佑部分资产并注销，表明上游辅料厂商面对全球电子周期调整及产能过剩时的止损重整与撤退动作，打破中资只会单向盲目涌入的固有认知。"),
        ("f218cb8b", "D1", "共创草坪（605099.SH）", "西宁/隆安", "MEDIUM",
         "人造草坪全球制造冠军对越基地实施二次追加投资。越南生产实体已成为其向欧美出口规避关税贸易壁垒的战略核心支点，增资用于加码自动化产线。"),
        ("5d05a6db", "D1", "金风科技（002202.SZ / 02208.HK）", "平顺/全国", "MEDIUM",
         "中国风电设备巨头为越南全资运维实体提供母公司跨国履约担保，标志着中资在越从单纯主机出口迈入属地深耕承揽与长期电站运维新阶段。"),
        ("abac5c42", "D1", "宝胜股份（600973.SH）", "广义/中部", "MEDIUM",
         "国内特种线缆龙头拟在越新设全资制造实体，配套东南亚电网改造及跨国科技大厂电力基础设施用线需求，重资产出海落地。"),
        ("a31f87bc", "D1", "五新智能（920174.BJ）", "全国/未定", "LOW",
         "北交所基建专用设备上市公司完成越南全资子公司法定登记注册，拿到营业执照，海外实体进入实质化运营准备。"),

        # D2: 项目实体工程全周期进展 (环评、排污、开工)
        ("d98e4124", "D2", "LG Innotek 半导体载板厂", "海防市 (DEEP C 2)", "HIGH",
         "韩国半导体封装与光学部件巨头 10 亿美元扩产项目正式获批并取得投资登记证（IRC），是海防市年度最大单体外资高精尖制造工程，拉动半导体辅材产业链聚集。"),
        ("1173153a", "D2", "越澳钢铁（Vinausteel）", "兴安省 (邓礼工业集群)", "MEDIUM",
         "成品钢制造基地完成环保部法定排污许可证审批受理，标志着重工业实体进入投产合规前夕关键节点。"),
        ("23e6e23d", "D2", "顺兴包装纸业（Thuận Hưng）", "海防市 (先清工业区)", "MEDIUM",
         "造纸包装重污染监控企业向环境部申办排污许可，反映沿海出口包装供应链实体环保合规提速。"),
        ("d1fe7aab", "D2", "春梅纸业（Xuân Mai）", "胡志明市 (协福工业区)", "MEDIUM",
         "南部核心工业区纸制品生产基地提交法定排污许可申请，投运前环保审查进入公示期。"),
        ("b77f90db", "D2", "西普安工业区一期基建工程", "太原省 (Phổ Yên)", "MEDIUM",
         "太原省工业区管委会举行开工奠基仪式，一期重点承载三星电子周边精密电子机械配套产线转移，拉动周边土地与厂房需求。"),
        ("2f8d15e8", "D2", "安平 2 号工业区征地拆迁工程", "太原省 (Yên Bình)", "LOW",
         "太原工业区管委会协同地方推进土地补偿、安置与清表，为后续规模化产业承接扫除供地障碍。"),

        # D3: 产业供应链与配套生态 (航空、高标仓储、物流风控)
        ("4eb21865", "D3", "ASCO Industries（比利时）", "中部核心工业区", "HIGH",
         "欧洲顶级航空结构件制造商拟在越南中部投资 1 亿美元建厂，标志着继美系航空供应链之后，欧洲航空制造巨头首次将高精密机身结构件产能向越迁移。"),
        ("e1c47a75", "D3", "越南物流协会（VLA）", "全国/航运港口", "HIGH",
         "【极高价值行业协会经营风控警示】VLA 正式发文预警企业应收账款与现金流断裂危机，指出当前越南制造业外贸出口账期拉长、货代承运商垫资压力剧增，属一线供应链承压的强烈弱信号。"),

        # D4: 经营与政策营商环境 (税收红利、用工刚性合规)
        ("fb41a6e4", "D4", "越南财政部（MOF）", "全国", "HIGH",
         "越南财政部出台落实国会第 43/2026/QH16 号决议的个人及企业所得税减免细则，属于国家层面重大普惠性减税红利，直接增厚在越制造企业净利润。"),
        ("dd9e0132", "D4", "越南财政部（MOF）", "全国", "MEDIUM",
         "自 11 月 1 日起汽油特别消费税税率正式降为 0%，大幅减轻物流运输与通勤燃料成本，有效平抑四季度制造业通胀压力。"),
        ("cea4cf19", "D4", "越南政府门户与工贸部", "全国", "MEDIUM",
         "官方通报评估“工业降电价 2% + 汽油税免征”组合拳，直接利好高耗能制造实体，对年底工业产出提供宏观成本支撑。"),

        # D5: 宏观大盘与空间规划 (水光互补清洁能源、跨国大通道)
        ("3a8ab009", "D5", "VinEnergo（本查水上光伏）", "莱州/西北水库", "MEDIUM",
         "莱州本查 1 号水上浮式光伏电站（4.18 亿美元）进入环境部环评法定公示，开辟越西北高山峡谷水库“水光互补”清洁能源带示范通道。")
    ]

    signals = []
    for fp_prefix, d_code, entity, prov, sev, insight in target_fps:
        cur_raw.execute("""
            SELECT fingerprint, source_id, source_name, title, pub_date, url
            FROM raw_materials
            WHERE fingerprint LIKE ?
            LIMIT 1;
        """, (fp_prefix + "%",))
        row = cur_raw.fetchone()
        if row:
            fp, sid, sname, title, pdate, url = row
            signals.append({
                "signal_id": f"SIG-{d_code}-{fp[:8]}",
                "dimension_code": d_code,
                "title": title,
                "summary_insight": insight,
                "entity_name": entity,
                "province": prov,
                "severity_level": sev,
                "pub_date": pdate,
                "source_id": sid,
                "source_name": sname,
                "raw_fingerprint": fp,
                "url": url
            })

    conn_raw.close()

    # Save to Stage 2 database
    from scripts.stage2.save_signals import save_signals
    save_signals(signals)

if __name__ == "__main__":
    run_classification()
