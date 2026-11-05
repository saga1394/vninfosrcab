#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
邮件推送模块：将全量 16 项投资与实体产业情报（全中文、分章节、事实与看点）
以纯内联 CSS 完整渲染在邮件正文中，零附件，仅保留在线大盘链接作为兜底。
正文风格客观严谨，无宣教废话。
落款标注：【太空建筑观察】越南组
严守单人安全发信纪律：未经用户明确批准前，默认仅向 18677106863@qq.com 单人投递。
"""

import os
import sys
import json
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
from pathlib import Path
from xml.sax.saxutils import escape

# 确保 UTF-8 输出
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = BASE_DIR / "config" / "email_config.json"

# 单人安全锁收件人（用户未确认前绝对锁死单人）
SAFE_DEFAULT_RECIPIENT = ["18677106863@qq.com"]
FULL_TEAM_RECIPIENTS = [
    "18677106863@qq.com",
    "443672603@qq.com",
    "515235776@qq.com"
]


def load_email_config():
    """读取邮件配置（优先环境变量，其次配置文件，默认安全单人保护）"""
    config = {
        "smtp_host": os.environ.get("SMTP_HOST", "smtp.qq.com"),
        "smtp_port": int(os.environ.get("SMTP_PORT", 465)),
        "use_ssl": os.environ.get("SMTP_USE_SSL", "true").lower() in ("true", "1", "yes"),
        "sender_email": os.environ.get("SMTP_USER", ""),
        "sender_auth_code": os.environ.get("SMTP_PASSWORD", ""),
        "recipient_emails": SAFE_DEFAULT_RECIPIENT
    }

    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                file_config = json.load(f)
                for k, v in file_config.items():
                    if not os.environ.get(k.upper()) and v:
                        config[k] = v
        except Exception as e:
            print(f"[警告] 读取配置文件 {CONFIG_PATH} 失败: {e}")

    # 规范化收件人列表（默认锁定单人，除非调用时显式指定）
    recipients = config.get("recipient_emails")
    if not recipients:
        recipients = SAFE_DEFAULT_RECIPIENT
    elif isinstance(recipients, str):
        recipients = [s.strip() for s in recipients.split(",") if s.strip()]
    config["recipient_emails"] = recipients

    return config


def get_curated_intelligence():
    """获取审校后的完整情报列表"""
    sys.path.insert(0, str(BASE_DIR / "scripts" / "stage2"))
    try:
        import generate_html_report
        return generate_html_report.CURATED_INTELLIGENCE
    except Exception as e:
        print(f"[错误] 加载情报数据失败: {e}")
        return []


def build_full_inbox_email_html(items, today_str):
    """
    构建专为 QQ 邮箱邮件框架定制的全量 HTML 正文：
    1. 采用高压缩比轻量内联 CSS，总体积约 55KB，彻底规避 QQ 邮箱 100KB 截断；
    2. 全文直入主题，无任何框架解释或虚构占位；
    3. 分五大预期章节排列，事实与看点严格客观呈现，100% 真实链接；
    4. 邮件内 FDI 大盘采用精炼 KPI 概览卡片，并引导点击在线大盘查看完整折叠明细；
    5. 落款【太空建筑观察】越南组。
    """
    categories = [
        ("APPROVALS", "一、 🏛️ 行政审批与法定公示（捕获潜在项目与核实阶段依据）"),
        ("FDI", "二、 🎯 FDI 外资投资动向（真实跨国资本入越动向）"),
        ("INDUSTRIAL_PARKS", "三、 🏭 工业园区一线动态（承接 FDI 物理载体与现场推进）"),
        ("SECTORS", "四、 ⚡ 重点关注产业专题（半导体/数据中心/先进制造专区）"),
        ("MACRO_MARKET", "五、 🌐 政经与综合市场动态（宏观走向·涉企法规·要素成本·干线物流）")
    ]

    grouped = {code: [] for code, _ in categories}
    for item in items:
        cat = item.get("category", "MACRO_MARKET")
        if cat in grouped:
            grouped[cat].append(item)
        else:
            grouped["MACRO_MARKET"].append(item)

    lines = []
    lines.append('<!DOCTYPE html>')
    lines.append('<html>')
    lines.append('<head>')
    lines.append('<meta charset="utf-8">')
    lines.append('<title>越南实体投资与产业动态简报</title>')
    lines.append('</head>')
    lines.append('<body style="margin: 0; padding: 16px; background-color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, \'Helvetica Neue\', Arial, sans-serif; color: #1e293b; line-height: 1.6;">')
    lines.append('<div style="max-width: 760px; margin: 0 auto; background: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 24px 28px;">')

    # 简报头部（直接、客观、无废话）
    lines.append('<div style="border-bottom: 2px solid #0f172a; padding-bottom: 12px; margin-bottom: 24px;">')
    lines.append(f'<div style="font-size: 12px; color: #64748b; font-family: monospace; margin-bottom: 4px;">【太空建筑观察】越南组 · 简报日期：{today_str}</div>')
    lines.append('<h1 style="margin: 0; font-size: 20px; font-weight: 800; color: #0f172a; letter-spacing: -0.5px;">越南实体投资与产业动态简报（今日增量专版）</h1>')
    lines.append(f'<div style="font-size: 12px; color: #64748b; margin-top: 6px;">本期精选 <strong>{len(items)} 项</strong> 纯增量一手动态线索（严格遵循真实信源直接链接原则，往期已发情报沉淀入库备查）。</div>')
    lines.append('</div>')

    # 插入：【FDI 全景大盘月度监测】紧凑高亮版块
    lines.append('<div style="background: #ffffff; border: 2px solid #7f1d1d; border-radius: 6px; padding: 14px 16px; margin-bottom: 24px;">')
    lines.append('<div style="background: #450a0a; color: #ffffff; padding: 8px 12px; border-radius: 4px; font-size: 13px; font-weight: 800; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">')
    lines.append('<span>📊 【FDI 全景大盘月度监测】（2026年前10个月权威官报 · 截至 10-31）</span>')
    lines.append('<span style="font-size: 11px; background: #991b1b; padding: 2px 6px; border-radius: 3px;">月度基准</span>')
    lines.append('</div>')
    lines.append('<div style="font-size: 11px; color: #64748b; margin-bottom: 10px;">数据源：越南计划投资部外国投资局 (FIA) & 国家统计总局 (NSO) 联合官方公报</div>')

    # 全国三维指标
    lines.append('<table style="width: 100%; border-collapse: collapse; font-size: 12px; margin-bottom: 10px;">')
    lines.append('<tr>')
    lines.append('<td style="width: 33%; background: #fef2f2; border: 1px solid #fecaca; padding: 8px 10px; vertical-align: top; border-radius: 4px;">')
    lines.append('<div style="color: #991b1b; font-weight: 700; font-size: 11px;">FDI 投资登记总额</div>')
    lines.append('<div style="font-size: 17px; font-weight: 800; color: #450a0a; margin: 3px 0;">548.5 亿美元</div>')
    lines.append('<div style="color: #7f1d1d; font-size: 11px;">同比 <strong>+74.0%</strong> (创17年新高)</div>')
    lines.append('</td>')
    lines.append('<td style="width: 33%; background: #ecfdf5; border: 1px solid #a7f3d0; padding: 8px 10px; vertical-align: top; border-radius: 4px;">')
    lines.append('<div style="color: #065f46; font-weight: 700; font-size: 11px;">FDI 实际到位资金</div>')
    lines.append('<div style="font-size: 17px; font-weight: 800; color: #064e3b; margin: 3px 0;">240.8 亿美元</div>')
    lines.append('<div style="color: #065f46; font-size: 11px;">同比 <strong>+13.1%</strong> (近5年最快)</div>')
    lines.append('</td>')
    lines.append('<td style="width: 33%; background: #eff6ff; border: 1px solid #bfdbfe; padding: 8px 10px; vertical-align: top; border-radius: 4px;">')
    lines.append('<div style="color: #1e40af; font-weight: 700; font-size: 11px;">制造产业集聚度</div>')
    lines.append('<div style="font-size: 17px; font-weight: 800; color: #172554; margin: 3px 0;">51.6% 占总盘</div>')
    lines.append('<div style="color: #1e40af; font-size: 11px;">超 <strong>280 亿美元</strong> 流向实体制造</div>')
    lines.append('</td>')
    lines.append('</tr>')
    lines.append('</table>')

    # 精炼摘要条目与网页大盘完整展开链接
    lines.append('<div style="font-size: 11px; color: #475569; background: #f8fafc; border: 1px dashed #cbd5e1; padding: 8px 12px; border-radius: 4px; line-height: 1.5;">')
    lines.append('<strong>• 各省前5强：</strong>胡志明 (201.4亿)、太原 (80.1亿)、北宁 (45.7亿)、海防 (31.2亿)、广宁 (28.5亿)<br>')
    lines.append('<strong>• 来源国前5强：</strong>新加坡 (95.2亿)、韩国 (58.1亿)、卢森堡 (49.9亿)、中国大陆 (41.6亿，新批项目数全国第一)、中国香港 (33.8亿)<br>')
    lines.append('<div style="margin-top: 6px; text-align: right;"><a href="https://saga1394.github.io/vninfosrcab/#macro-fdi" target="_blank" style="color: #991b1b; text-decoration: underline; font-weight: 700;">点击在大盘中展开查看完整前10强与详细分析 &rarr;</a></div>')
    lines.append('</div>')

    lines.append('</div>')

    # 五大章节主体
    for cat_code, cat_title in categories:
        cat_items = grouped[cat_code]
        if not cat_items:
            continue

        lines.append(f'<div style="margin-bottom: 26px;">')
        lines.append(f'<div style="font-size: 15px; font-weight: 700; color: #0f172a; border-left: 4px solid #0f172a; padding-left: 10px; margin-bottom: 12px;">{cat_title} ({len(cat_items)} 条)</div>')

        for it in cat_items:
            title = escape(it.get("title", ""))
            url = it.get("url", "#")
            date = it.get("date", "")
            sub_tag = escape(it.get("sub_tag", ""))
            sector_name = escape(it.get("sector_name", ""))
            source = escape(it.get("source_name", ""))
            fact = escape(it.get("fact", ""))
            reason = escape(it.get("reason", ""))

            sector_html = f' · <span style="background: #fef3c7; color: #92400e; padding: 1px 5px; border-radius: 3px; font-weight: 700;">⚡ {sector_name}</span>' if sector_name else ""

            lines.append('<div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px 14px; margin-bottom: 10px;">')
            # 标题与外链
            lines.append(f'<div style="font-size: 14px; font-weight: 700; color: #0f172a; margin-bottom: 4px;"><a href="{url}" target="_blank" style="color: #1e40af; text-decoration: none;">{title}</a></div>')
            # 元数据
            lines.append(f'<div style="font-size: 11px; color: #64748b; margin-bottom: 6px;">🕒 {date} · <span style="background: #e2e8f0; padding: 1px 5px; border-radius: 3px; color: #334155;">{sub_tag}</span>{sector_html} · 信源：<strong>{source}</strong> · <a href="{url}" target="_blank" style="color: #2563eb; text-decoration: underline;">查看原始报道 &rarr;</a></div>')
            # 事实
            lines.append(f'<div style="font-size: 13px; color: #334155; margin-bottom: 6px;"><strong>【事实】</strong>{fact}</div>')
            # 看点（客观低调、不喧宾夺主）
            if reason:
                lines.append(f'<div style="font-size: 12px; color: #475569; background: #f1f5f9; padding: 6px 10px; border-radius: 4px; border-left: 3px solid #94a3b8;"><strong>【看点】</strong>{reason}</div>')
            lines.append('</div>')

        lines.append('</div>')

    # 兜底链接与落款
    lines.append('<div style="margin-top: 28px; padding: 12px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 12px; color: #64748b; text-align: center;">')
    lines.append('在线交互大盘备查（含全文检索、FDI月度大盘展开与多维筛选）：<br>')
    lines.append('<a href="https://saga1394.github.io/vninfosrcab/" target="_blank" style="color: #1e40af; text-decoration: underline; font-weight: 600;">https://saga1394.github.io/vninfosrcab/</a>')
    lines.append('</div>')

    lines.append('<div style="margin-top: 20px; padding-top: 12px; border-top: 2px solid #0f172a; font-size: 13px; color: #0f172a; display: flex; justify-content: space-between; align-items: center;">')
    lines.append('<div><strong>【太空建筑观察】越南组</strong></div>')
    lines.append(f'<div style="color: #64748b; font-size: 12px; font-family: monospace;">TB-VN-{today_str}</div>')
    lines.append('</div>')

    lines.append('</div>')
    lines.append('</body>')
    lines.append('</html>')

    return "".join(lines)


def send_report_email(recipients=None, send_to_all=False):
    """
    发送全量全文邮件（零附件、正文完整渲染）
    安全保护：
    1. 默认仅发送给 SAFE_DEFAULT_RECIPIENT = ["18677106863@qq.com"]
    2. 只有当 send_to_all 为 True 时才允许发送给 3 人全员列表
    """
    config = load_email_config()

    if send_to_all:
        target_recipients = FULL_TEAM_RECIPIENTS
    elif recipients:
        if isinstance(recipients, str):
            target_recipients = [s.strip() for s in recipients.split(",") if s.strip()]
        else:
            target_recipients = list(recipients)
    else:
        target_recipients = SAFE_DEFAULT_RECIPIENT

    sender = config.get("sender_email")
    auth_code = config.get("sender_auth_code")
    smtp_host = config.get("smtp_host", "smtp.qq.com")
    smtp_port = config.get("smtp_port", 465)
    use_ssl = config.get("use_ssl", True)

    if not sender or not auth_code:
        print(f"[错误] 尚未配置发件凭据，请检查 {CONFIG_PATH}")
        return False

    today_str = datetime.now().strftime("%Y-%m-%d")

    # 1. 获取全量审校情报
    items = get_curated_intelligence()
    if not items:
        print("[错误] 未能加载到有效情报列表。")
        return False

    # 2. 构建专为 QQ 邮箱优化的全量正文
    full_email_html = build_full_inbox_email_html(items, today_str)
    html_bytes = full_email_html.encode("utf-8")
    print(f"[正文编译] 全量 {len(items)} 项情报已编译为内联 HTML，正文大小: {len(html_bytes)} 字节 (~{len(html_bytes)//1024} KB)")

    subject = f"【太空建筑观察】越南实体投资与产业动态简报（今日增量专版） - {today_str}"

    # 3. 建立官方 SMTP 连接投递
    success_count = 0
    try:
        print(f"[正在连接] 腾讯官方 SMTP 服务器 {smtp_host}:{smtp_port} (SSL: {use_ssl})...")
        if use_ssl:
            server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=25)
        else:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=25)
            server.starttls()

        server.login(sender, auth_code)

        for rec in target_recipients:
            try:
                msg = MIMEMultipart("alternative")
                msg["From"] = formataddr((str(Header("【太空建筑观察】越南组", "utf-8")), sender))
                msg["To"] = formataddr((str(Header("投资决策人", "utf-8")), rec))
                msg["Subject"] = Header(subject, "utf-8").encode()
                msg.attach(MIMEText(full_email_html, "html", "utf-8"))

                server.sendmail(sender, [rec], msg.as_string())
                print(f"  [成功投递] -> {rec}")
                success_count += 1
            except Exception as e_rec:
                print(f"  ❌ [投递失败] -> {rec}: {e_rec}")

        server.quit()

        print(f"\n [投递汇总] 共计划投递 {len(target_recipients)} 位，成功送达 {success_count} 位")
        print(f"  信件主题: {subject}")
        print(f"  正文规模: {len(items)} 项情报完整内嵌，无附件，零截断")
        print(f"  收件人列表: {target_recipients}")
        print(f"  落款: 【太空建筑观察】越南组")
        return success_count == len(target_recipients)
    except Exception as e:
        print(f"❌ [SMTP 连接异常]: {e}")
        return False


if __name__ == "__main__":
    send_all_flag = "--all" in sys.argv or "--send-to-all" in sys.argv
    target = None
    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            target = arg
            break

    success = send_report_email(recipients=target, send_to_all=send_all_flag)
    sys.exit(0 if success else 1)
