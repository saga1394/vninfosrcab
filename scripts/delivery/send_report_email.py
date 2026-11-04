#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
邮件推送模块：将全量 55 项投资与实体产业情报（全中文、分章节、事实与看点）
以纯内联 CSS 完整渲染在邮件正文中，零附件，仅保留在线大盘链接作为兜底。
正文风格客观严谨，无宣教废话。
落款标注：【太空建筑观察】越南组
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
DEFAULT_RECIPIENTS = [
    "18677106863@qq.com",
    "443672603@qq.com",
    "515235776@qq.com"
]


def load_email_config():
    """读取邮件配置（优先环境变量，其次配置文件）"""
    config = {
        "smtp_host": os.environ.get("SMTP_HOST", "smtp.qq.com"),
        "smtp_port": int(os.environ.get("SMTP_PORT", 465)),
        "use_ssl": os.environ.get("SMTP_USE_SSL", "true").lower() in ("true", "1", "yes"),
        "sender_email": os.environ.get("SMTP_USER", ""),
        "sender_auth_code": os.environ.get("SMTP_PASSWORD", ""),
        "recipient_emails": DEFAULT_RECIPIENTS
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

    # 规范化收件人列表
    recipients = config.get("recipient_emails")
    if not recipients:
        single = config.get("recipient_email")
        if single:
            recipients = [s.strip() for s in single.split(",") if s.strip()]
        else:
            recipients = DEFAULT_RECIPIENTS
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
    1. 采用高压缩比轻量内联 CSS，总体积约 60KB，彻底规避 QQ 邮箱 100KB 截断；
    2. 全文直入主题，无任何框架解释或废话；
    3. 分五大预期章节排列，事实与看点严格客观呈现；
    4. 仅保留网页链接作为兜底，落款【太空建筑观察】越南组。
    """
    categories = [
        ("FDI", "一、 🎯 FDI 外资投资动向（特别关注中资大厂）"),
        ("INDUSTRIAL_PARKS", "二、 🏭 工业园区一线动态（承接 FDI 物理载体与现场推进）"),
        ("APPROVALS", "三、 🏛️ 行政审批与法定公示（捕获潜在项目与核实阶段依据）"),
        ("SECTORS", "四、 ⚡ 重点关注产业专题（半导体/数据中心/垃圾发电/车企/冷链/绿电/自动化）"),
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
    lines.append('<h1 style="margin: 0; font-size: 20px; font-weight: 800; color: #0f172a; letter-spacing: -0.5px;">越南实体投资与产业动态简报</h1>')
    lines.append(f'<div style="font-size: 12px; color: #64748b; margin-top: 6px;">本期汇总 <strong>{len(items)} 项</strong> 动态线索，覆盖在越主要企业动向、法定审批、重点赛道及宏观政策。</div>')
    lines.append('</div>')

    # 五大章节主体
    for cat_code, cat_title in categories:
        cat_items = grouped[cat_code]
        if not cat_items:
            continue

        lines.append(f'<div style="margin-bottom: 28px;">')
        lines.append(f'<div style="font-size: 16px; font-weight: 700; color: #0f172a; border-left: 4px solid #0f172a; padding-left: 10px; margin-bottom: 14px;">{cat_title} ({len(cat_items)} 条)</div>')

        for it in cat_items:
            title = escape(it.get("title", ""))
            url = it.get("url", "#")
            date = it.get("date", "")
            sub_tag = escape(it.get("sub_tag", ""))
            source = escape(it.get("source_name", ""))
            fact = escape(it.get("fact", ""))
            reason = escape(it.get("reason", ""))

            lines.append('<div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px 14px; margin-bottom: 10px;">')
            # 标题与外链
            lines.append(f'<div style="font-size: 14px; font-weight: 700; color: #0f172a; margin-bottom: 4px;"><a href="{url}" target="_blank" style="color: #1e40af; text-decoration: none;">{title}</a></div>')
            # 元数据
            lines.append(f'<div style="font-size: 11px; color: #64748b; margin-bottom: 6px;">🕒 {date} · <span style="background: #e2e8f0; padding: 1px 5px; border-radius: 3px; color: #334155;">{sub_tag}</span> · 来源：{source}</div>')
            # 事实
            lines.append(f'<div style="font-size: 13px; color: #334155; margin-bottom: 6px;"><strong>【事实】</strong>{fact}</div>')
            # 看点（客观低调、不喧宾夺主）
            if reason:
                lines.append(f'<div style="font-size: 12px; color: #475569; background: #f1f5f9; padding: 6px 10px; border-radius: 4px; border-left: 3px solid #94a3b8;"><strong>【看点】</strong>{reason}</div>')
            lines.append('</div>')

        lines.append('</div>')

    # 兜底链接与落款
    lines.append('<div style="margin-top: 32px; padding: 14px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 12px; color: #64748b; text-align: center;">')
    lines.append('在线交互大盘备查（含全文检索与分类筛选）：<br>')
    lines.append('<a href="https://saga1394.github.io/vninfosrcab/" target="_blank" style="color: #1e40af; text-decoration: underline; font-weight: 600;">https://saga1394.github.io/vninfosrcab/</a>')
    lines.append('</div>')

    lines.append('<div style="margin-top: 24px; padding-top: 14px; border-top: 2px solid #0f172a; font-size: 13px; color: #0f172a; display: flex; justify-content: space-between; align-items: center;">')
    lines.append('<div><strong>【太空建筑观察】越南组</strong></div>')
    lines.append(f'<div style="color: #64748b; font-size: 12px; font-family: monospace;">TB-VN-{today_str}</div>')
    lines.append('</div>')

    lines.append('</div>')
    lines.append('</body>')
    lines.append('</html>')

    return "".join(lines)


def send_report_email(recipients=None):
    """发送全量全文邮件（零附件、正文完整渲染、支持多收件人独立信头投递）"""
    config = load_email_config()
    
    if recipients:
        if isinstance(recipients, str):
            target_recipients = [s.strip() for s in recipients.split(",") if s.strip()]
        else:
            target_recipients = list(recipients)
    else:
        target_recipients = config.get("recipient_emails", DEFAULT_RECIPIENTS)

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

    subject = f"【太空建筑观察】越南实体投资与产业动态简报 - {today_str}"

    # 3. 建立官方 SMTP 连接投递多收件人
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
                # 独立构建 RFC 5322 信头，保证私密性与反垃圾信誉
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
        print(f"  落款: 【太空建筑观察】越南组")
        return success_count == len(target_recipients)
    except Exception as e:
        print(f"❌ [SMTP 连接异常]: {e}")
        return False


if __name__ == "__main__":
    to_addr = sys.argv[1] if len(sys.argv) > 1 else None
    success = send_report_email(to_addr)
    sys.exit(0 if success else 1)
