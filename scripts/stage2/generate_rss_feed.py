#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成标准 RSS 2.0 Feed (docs/stage2/feed.xml)，支持通过 Blogtrottr / Follow 等免费 RSS 转邮件服务
每日定时免密将最新全中文投资情报推送到指定邮箱。
"""

import os
import sys
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

# 确保 UTF-8 输出
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "data" / "stage2" / "projects.db"
OUTPUT_RSS = BASE_DIR / "docs" / "stage2" / "feed.xml"


def format_rfc822_date(date_str):
    """转换 YYYY-MM-DD 为 RFC-822 标准 RSS 日期格式"""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d").replace(hour=9, minute=0, second=0, tzinfo=timezone.utc)
        return dt.strftime("%a, %d %b %Y %H:%M:%S GMT")
    except Exception:
        return datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")


def generate_rss():
    if not DB_PATH.exists():
        print(f"[错误] 数据库不存在: {DB_PATH}")
        return False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 提取按预期分类的所有有效情报
    query = """
    SELECT expectation_category, title, summary_insight, entity_name, province, pub_date, url, strategic_sub_tag
    FROM dimensional_signals
    WHERE pub_date >= '2026-11-01'
    ORDER BY 
        CASE expectation_category
            WHEN '客户动向' THEN 1
            WHEN '审批公示' THEN 2
            WHEN '重点赛道' THEN 3
            WHEN '整体市场' THEN 4
            WHEN '各省园区' THEN 5
            ELSE 6
        END,
        pub_date DESC
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("[警告] 没有提取到有效情报记录。")
        return False

    today_str = datetime.now().strftime("%Y-%m-%d")
    pub_rfc822 = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

    # 分类归集
    categories = {
        "客户动向": {"badge": "🎯 P0 客户与潜在客户动向", "items": []},
        "审批公示": {"badge": "🏛️ 各类审批与法定公示", "items": []},
        "重点赛道": {"badge": "⚡ 重点关注赛道与未来产业储备", "items": []},
        "整体市场": {"badge": "🌐 整体市场动向与政经大盘", "items": []},
        "各省园区": {"badge": "🏭 各省工业园区招商与产业综合", "items": []}
    }

    for row in rows:
        cat = row[0]
        if cat in categories:
            categories[cat]["items"].append(row)
        else:
            categories["整体市场"]["items"].append(row)

    # 组装 HTML 格式的每日整期内参正文（供 RSS 邮件客户端直接渲染）
    content_html = [f"<div style='font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif; max-width: 800px; margin: 0 auto; color: #1e293b; line-height: 1.6;'>"]
    content_html.append(f"<div style='background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #ffffff; padding: 24px; border-radius: 12px; margin-bottom: 24px;'>")
    content_html.append(f"<h1 style='margin: 0 0 8px 0; font-size: 22px; font-weight: 700;'>今日越南实体与投资情报内参（全中文审校版）</h1>")
    content_html.append(f"<p style='margin: 0; font-size: 13px; color: #94a3b8;'>报告日期：{today_str} | 已审校高价值情报：{len(rows)} 条 | 纯中文提炼</p>")
    content_html.append("</div>")

    for cat_name, cat_data in categories.items():
        items = cat_data["items"]
        if not items:
            continue
        content_html.append(f"<div style='margin-bottom: 24px;'>")
        content_html.append(f"<h2 style='font-size: 16px; font-weight: 700; color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 6px; margin-bottom: 12px;'>{cat_data['badge']} ({len(items)} 条)</h2>")
        
        for item in items:
            title = item[1]
            summary = item[2]
            entity = item[3] or "实体未标明"
            prov = item[4] or "越南全境"
            pdate = item[5]
            url = item[6] or "#"
            sub_tag = f" · {item[7]}" if item[7] else ""

            # 解析 [客观事实] 与 [决策价值]
            fact_text = summary
            val_text = ""
            if "[决策价值]" in summary:
                parts = summary.split("[决策价值]")
                fact_text = parts[0].replace("[客观事实]", "").strip()
                val_text = parts[1].strip()

            content_html.append(f"<div style='background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px; margin-bottom: 10px;'>")
            content_html.append(f"<div style='font-size: 15px; font-weight: 600; color: #0f172a; margin-bottom: 6px;'><a href='{url}' target='_blank' style='color: #1e40af; text-decoration: none;'>{escape(title)}</a></div>")
            content_html.append(f"<div style='font-size: 12px; color: #64748b; margin-bottom: 8px;'><span style='background: #e2e8f0; padding: 2px 6px; border-radius: 4px;'>{escape(entity)}</span> · <span>📍 {escape(prov)}</span> · <span>🕒 {escape(pdate)}</span><span style='color: #0284c7; font-weight: 500;'>{escape(sub_tag)}</span></div>")
            content_html.append(f"<div style='font-size: 13px; color: #334155; margin-bottom: 4px;'><strong>【客观事实】</strong>{escape(fact_text)}</div>")
            if val_text:
                content_html.append(f"<div style='font-size: 13px; color: #b45309; background: #fef3c7; padding: 6px 10px; border-radius: 4px; border-left: 3px solid #f59e0b;'><strong>【决策价值】</strong>{escape(val_text)}</div>")
            content_html.append("</div>")

        content_html.append("</div>")

    content_html.append("<div style='text-align: center; font-size: 12px; color: #94a3b8; padding: 20px 0;'>本内参由越南实体与投资情报每日巡检系统自动生成与审校</div>")
    content_html.append("</div>")

    full_html = "".join(content_html)

    # 组装标准 RSS 2.0 XML
    xml = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
        '  <channel>',
        '    <title>越南实体投资与产业决策内参</title>',
        '    <link>https://github.com/saga1394/vninfosrcab</link>',
        '    <description>每日越南投资与实体产业情报全中文审校版（按预期分类、100%专业翻译、客观事实与决策价值）</description>',
        '    <language>zh-cn</language>',
        f'    <lastBuildDate>{pub_rfc822}</lastBuildDate>',
        f'    <atom:link href="https://raw.githubusercontent.com/saga1394/vninfosrcab/main/docs/stage2/feed.xml" rel="self" type="application/rss+xml" />',
        '    <item>',
        f'      <title>【每日内参】越南实体与投资情报每日简报（全中文审校版）- {today_str}</title>',
        f'      <link>https://raw.githubusercontent.com/saga1394/vninfosrcab/main/docs/stage2/feed.xml#{today_str}</link>',
        f'      <guid isPermaLink="false">vietnam-intel-{today_str}</guid>',
        f'      <pubDate>{pub_rfc822}</pubDate>',
        '      <description><![CDATA[',
        full_html,
        '      ]]></description>',
        '    </item>',
        '  </channel>',
        '</rss>'
    ]

    OUTPUT_RSS.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_RSS, "w", encoding="utf-8") as f:
        f.write("\n".join(xml))

    print(f" [成功] RSS Feed 生成完毕: {OUTPUT_RSS} (共 {len(rows)} 条情报)")
    return True


if __name__ == "__main__":
    generate_rss()
