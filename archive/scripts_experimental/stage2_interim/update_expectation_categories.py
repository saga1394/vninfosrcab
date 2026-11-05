# -*- coding: utf-8 -*-
import sqlite3

conn = sqlite3.connect('data/stage2/projects.db')
c = conn.cursor()

# Update 18 fresh signals for 2026-11-04
updates = [
    ('SIG-D1-be9e5114', 'CLIENTS', '垃圾发电与资本运作'),
    ('SIG-D1-78e16ca0', 'CLIENTS', '总包建筑与多元控股'),
    ('SIG-D1-ea82143d', 'CLIENTS', '消费零售与大股东借款'),
    ('SIG-D2-c50566d8', 'STRATEGIC', '综合骨干能源基建'),
    ('SIG-D2-1d2a111d', 'GENERAL', '积压土地项目清理'),
    ('SIG-D2-6ecd526d', 'APPROVALS', '智慧园区数字化招标'),
    ('SIG-D2-436905c3', 'GENERAL', '园区一线调研纾困'),
    ('SIG-D3-940aaf35', 'STRATEGIC', '海外强传导·关税壁垒'),
    ('SIG-D3-77ee5d1c', 'STRATEGIC', '海外强传导·供应链回流'),
    ('SIG-D3-337406ca', 'STRATEGIC', '半导体与AI算力长单'),
    ('SIG-D3-a3e646b9', 'STRATEGIC', '航空物流机队规划'),
    ('SIG-D4-0cc958ac', 'MACRO', '税制改革顶层行动计划'),
    ('SIG-D4-e2e98f1a', 'MACRO', '电力法修法与绿电直购'),
    ('SIG-D4-119bf1cf', 'APPROVALS', '涉企行政审批数字化改革'),
    ('SIG-D4-e63362dd', 'MACRO', '成品油降价与要素成本'),
    ('SIG-D5-b0c772c7', 'STRATEGIC', '半导体自主化首颗安全芯片'),
    ('SIG-D5-ed79c9bf', 'MACRO', '公共投资解付与基建加速'),
    ('SIG-D5-33fb0e3e', 'GENERAL', '海洋经济与临港产业走廊')
]

for sid, cat, sub in updates:
    c.execute("UPDATE dimensional_signals SET expectation_category = ?, strategic_sub_tag = ? WHERE signal_id = ?", (cat, sub, sid))

# Fill default for any other NULL expectation_category
c.execute("""
UPDATE dimensional_signals 
SET expectation_category = CASE dimension_code
    WHEN 'D1' THEN 'CLIENTS'
    WHEN 'D2' THEN 'APPROVALS'
    WHEN 'D3' THEN 'STRATEGIC'
    WHEN 'D4' THEN 'MACRO'
    WHEN 'D5' THEN 'GENERAL'
    ELSE 'MACRO'
END
WHERE expectation_category IS NULL
""")

conn.commit()

c.execute("SELECT expectation_category, COUNT(*) FROM dimensional_signals GROUP BY expectation_category")
print("Updated Expectation Categories:", c.fetchall())

conn.close()
