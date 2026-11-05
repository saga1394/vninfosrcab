# -*- coding: utf-8 -*-
"""
Add D5 Strategic Signals to projects.db
"""

import os
import sys
import sqlite3

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from scripts.stage2.save_signals import save_signals

RAW_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "daily", "collector.db"))

D5_CONFIG = [
    {
        "fp_prefix": "dbde805d",
        "dimension_code": "D5",
        "entity_name": "胜科工业 (Sembcorp) / 越苏石油 (PTSC)",
        "province": "巴地头顿省 / 离岸海域 (越新跨境走廊)",
        "severity_level": "HIGH",
        "summary_insight": "【东盟跨国能源大通道战略突破】新加坡能源局有条件批准胜科从越南进口 1.3 GW 海上绿电。标志着越南首次从国内能源消纳迈向‘东盟电网互联（ASEAN Power Grid）’出口国，将拉动巴地头顿与南部近海百亿美元级海上风电、换流站及海底高压海缆产业大投资。"
    },
    {
        "fp_prefix": "36f1dad3",
        "dimension_code": "D5",
        "entity_name": "春善集团 (Xuân Thiện Group)",
        "province": "南定省 / 宁平省 (北部沿海重工带)",
        "severity_level": "HIGH",
        "summary_insight": "【北越 174 亿美元超级绿色能源工业带】越南本土大型综合财团春善集团规划总投资 174 亿美元，在南定和宁平沿海打造绿色工业与 LNG 清洁能源复合基地，构建涵盖绿氢、高精钢材制造及大型深水码头的北部民营重工业空间增长极。"
    },
    {
        "fp_prefix": "b26c2fe9",
        "dimension_code": "D5",
        "entity_name": "VSIP (新加坡胜科与平阳 Becamex 合资)",
        "province": "全国 20 大工业走廊 (南北联动)",
        "severity_level": "MEDIUM",
        "summary_insight": "【跨国工业园区全国网络空间布局】新加坡胜科与 Becamex 签署深化合作协议，统筹推进全越 20 个新一代绿色智能 VSIP 工业园区开发，覆盖平阳、北宁、海防、义安、广义等地，为未来十年跨国先进制造业转移构筑标准化空间底盘。"
    }
]

def main():
    conn_raw = sqlite3.connect(RAW_DB_PATH)
    cur_raw = conn_raw.cursor()

    signals_to_commit = []
    for item in D5_CONFIG:
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
    conn_raw.close()

    inserted = save_signals(signals_to_commit)
    print(f"Committed {inserted} D5 signals.")

if __name__ == "__main__":
    main()
