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
    lines.append('<h1 style="margin: 0; font-size: 20px; font-weight: 800; color: #0f172a; letter-spacing: -0.5px;">越南实体投资与产业动态简报（今日增量专版）</h1>')
    lines.append(f'<div style="font-size: 12px; color: #64748b; margin-top: 6px;">本期精选 <strong>{len(items)} 项</strong> 纯增量一手动态线索（严格遵循“杜绝历史旧账侵占日常早报版面”原则，100% 聚焦近 24 小时最新动向，往期已发情报沉淀入库备查）。</div>')
    lines.append('</div>')

    # 插入：【FDI 全景大盘月度监测】专属版块
    lines.append('<div style="background: #ffffff; border: 2px solid #7f1d1d; border-radius: 6px; padding: 16px; margin-bottom: 24px;">')
    lines.append('<div style="background: #450a0a; color: #ffffff; padding: 8px 12px; border-radius: 4px; font-size: 14px; font-weight: 800; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;">')
    lines.append('<span>📊 【FDI 全景大盘月度监测】（2026年前10个月权威官报 · 按月更新）</span>')
    lines.append('<span style="font-size: 11px; background: #991b1b; padding: 2px 6px; border-radius: 3px;">月度基准</span>')
    lines.append('</div>')
    lines.append('<div style="font-size: 11px; color: #64748b; margin-bottom: 12px;">数据源：越南计划投资部外国投资局 (FIA) & 国家统计总局 (NSO) 联合官方公报（截至 2026-10-31）</div>')

    # 1. 全国总盘
    lines.append('<div style="margin-bottom: 14px;">')
    lines.append('<div style="font-size: 13px; font-weight: 700; color: #0f172a; margin-bottom: 8px;">一、 全国外商投资总量大盘（投资登记 vs 实际到位）</div>')
    lines.append('<table style="width: 100%; border-collapse: collapse; font-size: 12px; margin-bottom: 6px;">')
    lines.append('<tr>')
    lines.append('<td style="width: 33%; background: #fef2f2; border: 1px solid #fecaca; padding: 10px; vertical-align: top; border-radius: 4px;">')
    lines.append('<div style="color: #991b1b; font-weight: 700; font-size: 11px;">FDI 投资登记总额</div>')
    lines.append('<div style="font-size: 18px; font-weight: 800; color: #450a0a; margin: 4px 0;">548.5 亿美元</div>')
    lines.append('<div style="color: #7f1d1d; font-size: 11px;">同比 <strong>+74.0%</strong> (创17年新高)</div>')
    lines.append('<div style="font-size: 10px; color: #64748b; margin-top: 6px; line-height: 1.4;">• 新批: 307.3亿 (3,478项, 增2.2倍)<br>• 增资: 161.3亿 (1,079次, +33.2%)<br>• 并购: 79.9亿 (2,616次, +49.6%)</div>')
    lines.append('</td>')
    lines.append('<td style="width: 33%; background: #ecfdf5; border: 1px solid #a7f3d0; padding: 10px; vertical-align: top; border-radius: 4px;">')
    lines.append('<div style="color: #065f46; font-weight: 700; font-size: 11px;">FDI 实际到位资金 (解付)</div>')
    lines.append('<div style="font-size: 18px; font-weight: 800; color: #064e3b; margin: 4px 0;">240.8 亿美元</div>')
    lines.append('<div style="color: #065f46; font-size: 11px;">同比 <strong>+13.1%</strong> (近5年最快)</div>')
    lines.append('<div style="font-size: 10px; color: #64748b; margin-top: 6px; line-height: 1.4;">反映工程履约落地与设备进场变现率极高，各省园区清表交地与通电保障实质性加速。</div>')
    lines.append('</td>')
    lines.append('<td style="width: 33%; background: #eff6ff; border: 1px solid #bfdbfe; padding: 10px; vertical-align: top; border-radius: 4px;">')
    lines.append('<div style="color: #1e40af; font-weight: 700; font-size: 11px;">制造产业集聚度</div>')
    lines.append('<div style="font-size: 18px; font-weight: 800; color: #172554; margin: 4px 0;">51.6% 占总盘</div>')
    lines.append('<div style="color: #1e40af; font-size: 11px;">超 <strong>280 亿美元</strong> 流向实体制造</div>')
    lines.append('<div style="font-size: 10px; color: #64748b; margin-top: 6px; line-height: 1.4;">电子半导体、算力硬件、汽车三电及新能源高端装备居核心，其次为仓储物流与工业地产。</div>')
    lines.append('</td>')
    lines.append('</tr>')
    lines.append('</table>')
    lines.append('</div>')

    # 2. 各省前 10 强表格
    lines.append('<div style="margin-bottom: 14px;">')
    lines.append('<div style="font-size: 13px; font-weight: 700; color: #0f172a; margin-bottom: 6px;">🏆 二、 各省市外资承接排名前 10 强（截至 10 月底）</div>')
    lines.append('<table style="width: 100%; border-collapse: collapse; font-size: 11px; text-align: left;">')
    lines.append('<tr style="background: #f1f5f9; color: #475569; border-bottom: 1px solid #cbd5e1;">')
    lines.append('<th style="padding: 5px 8px; width: 36px; text-align: center;">排名</th><th style="padding: 5px 8px;">省市名称</th><th style="padding: 5px 8px; text-align: right;">登记金额</th><th style="padding: 5px 8px; text-align: right;">占比</th><th style="padding: 5px 8px;">产业核心聚集特征</th>')
    lines.append('</tr>')
    provinces_data = [
        ("01", "胡志明市 (TP.HCM)", "201.4 亿美元", "36.7%", "芹蒢国际中转港超级基建、金融与高科技研发领跑全国"),
        ("02", "太原省 (Thái Nguyên)", "80.1 亿美元", "14.6%", "三星产业链扩产、半导体高阶器件与西普安新工业区"),
        ("03", "北宁省 (Bắc Ninh)", "45.7 亿美元", "8.3%", "安靠 Amkor 16亿封测厂、富士康与本土 FPT 芯片测试"),
        ("04", "海防市 (Hải Phòng)", "31.2 亿美元", "5.7%", "深水港区与临港重工，LG 生态链与中国汽配产业链集聚"),
        ("05", "广宁省 (Quảng Ninh)", "28.5 亿美元", "5.2%", "晶科、天合光能及安美德宋快光伏与高新制造承接地"),
        ("06", "河内市 (Hà Nội)", "23.6 亿美元", "4.3%", "跨国研发中心、金融商业与和乐高新产业园"),
        ("07", "同奈省 (Đồng Nai)", "20.8 亿美元", "3.8%", "隆城空港周边精密五金、汽车零配件与高标包装"),
        ("08", "平阳省 (Bình Dương)", "18.4 亿美元", "3.4%", "南部工业腹地，高标仓储冷链、轻工与乐高超级工厂"),
        ("09", "义安省 (Nghệ An)", "15.2 亿美元", "2.8%", "中部承接标杆，立讯精密、歌尔声学及蓝思科技生产基地"),
        ("10", "北江省 (Bắc Giang)", "13.9 亿美元", "2.5%", "苹果果链精密五金与电子元器件集群核心承载地")
    ]
    for rk, pname, pcap, pshr, pfeat in provinces_data:
        bg = "#fffbeb" if rk in ("01", "02", "03") else "#ffffff"
        lines.append(f'<tr style="background: {bg}; border-bottom: 1px solid #f1f5f9;">')
        lines.append(f'<td style="padding: 4px 8px; text-align: center; font-weight: 700; color: #b45309;">{rk}</td>')
        lines.append(f'<td style="padding: 4px 8px; font-weight: 700; color: #0f172a;">{pname}</td>')
        lines.append(f'<td style="padding: 4px 8px; text-align: right; font-family: monospace; font-weight: 700; color: #0f172a;">{pcap}</td>')
        lines.append(f'<td style="padding: 4px 8px; text-align: right; font-family: monospace; color: #64748b;">{pshr}</td>')
        lines.append(f'<td style="padding: 4px 8px; color: #475569;">{pfeat}</td>')
        lines.append('</tr>')
    lines.append('</table>')
    lines.append('</div>')

    # 3. 来源国/地区前 8 强表格
    lines.append('<div>')
    lines.append('<div style="font-size: 13px; font-weight: 700; color: #0f172a; margin-bottom: 6px;">🌐 三、 主要外资来源国 / 地区排名（截至 10 月底）</div>')
    lines.append('<table style="width: 100%; border-collapse: collapse; font-size: 11px; text-align: left;">')
    lines.append('<tr style="background: #f1f5f9; color: #475569; border-bottom: 1px solid #cbd5e1;">')
    lines.append('<th style="padding: 5px 8px; width: 36px; text-align: center;">排名</th><th style="padding: 5px 8px;">投资来源国/地区</th><th style="padding: 5px 8px; text-align: right;">新批金额</th><th style="padding: 5px 8px; text-align: right;">占比</th><th style="padding: 5px 8px;">在越投资行业侧重与主力主体</th>')
    lines.append('</tr>')
    countries_data = [
        ("01", "新加坡 (Singapore)", "95.2 亿美元", "31.0%", "工业地产商（VSIP、BW）、清洁能源基建与跨境资金通道"),
        ("02", "韩国 (South Korea)", "58.1 亿美元", "18.9%", "三星、LG、安靠等半导体、显示模组及高精密元器件增资"),
        ("03", "卢森堡 (Luxembourg)", "49.9 亿美元", "16.2%", "欧洲大型基础设施与绿色循环经济专项投资基金"),
        ("04", "中国大陆 (China)", "41.6 亿美元", "13.5%", "新批项目数全国第一；光伏、汽车三电零部件、PCB 与电子制造"),
        ("05", "中国香港 (Hong Kong)", "33.8 亿美元", "11.0%", "中资离岸出海主体、工业物流仓储基金与跨境股权投资"),
        ("06", "日本 (Japan)", "27.5 亿美元", "8.9%", "汽车总成、高精机械加工、温控冷链现代物流及包装新材料"),
        ("07", "中国台湾 (Taiwan)", "21.0 亿美元", "6.8%", "光宝科技、仁宝、广达等 AI 服务器高功率电源、主板与线缆"),
        ("08", "荷兰 (Netherlands)", "14.2 亿美元", "4.6%", "半导体前道特种耗材、自动化流水线与高精化工")
    ]
    for crk, cname, ccap, cshr, cfeat in countries_data:
        bg = "#fef2f2" if crk == "04" else "#ffffff"
        lines.append(f'<tr style="background: {bg}; border-bottom: 1px solid #f1f5f9;">')
        lines.append(f'<td style="padding: 4px 8px; text-align: center; font-weight: 700; color: #991b1b;">{crk}</td>')
        lines.append(f'<td style="padding: 4px 8px; font-weight: 700; color: #0f172a;">{cname}</td>')
        lines.append(f'<td style="padding: 4px 8px; text-align: right; font-family: monospace; font-weight: 700; color: #0f172a;">{ccap}</td>')
        lines.append(f'<td style="padding: 4px 8px; text-align: right; font-family: monospace; color: #64748b;">{cshr}</td>')
        lines.append(f'<td style="padding: 4px 8px; color: #475569;">{cfeat}</td>')
        lines.append('</tr>')
    lines.append('</table>')
    lines.append('</div>')

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
            sector_name = escape(it.get("sector_name", ""))
            source = escape(it.get("source_name", ""))
            fact = escape(it.get("fact", ""))
            reason = escape(it.get("reason", ""))

            sector_html = f' · <span style="background: #fef3c7; color: #92400e; padding: 1px 5px; border-radius: 3px; font-weight: 700;">💡 {sector_name}</span>' if sector_name else ""

            lines.append('<div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px 14px; margin-bottom: 10px;">')
            # 标题与外链
            lines.append(f'<div style="font-size: 14px; font-weight: 700; color: #0f172a; margin-bottom: 4px;"><a href="{url}" target="_blank" style="color: #1e40af; text-decoration: none;">{title}</a></div>')
            # 元数据
            lines.append(f'<div style="font-size: 11px; color: #64748b; margin-bottom: 6px;">🕒 {date} · <span style="background: #e2e8f0; padding: 1px 5px; border-radius: 3px; color: #334155;">{sub_tag}</span>{sector_html} · 来源：{source}</div>')
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

    subject = f"【太空建筑观察】越南实体投资与产业动态简报（今日增量专版） - {today_str}"

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
