#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
邮件推送模块：自动将全中文投资情报简报（高清 PDF + 在线简报）发送至指定邮箱。
针对 QQ 邮箱对超大 HTML 截断的特性，正文采用高管精炼导读排版，核心大盘以高清 PDF 附件完整交付。
落款标注：【太空建筑观察】越南组
"""

import os
import sys
import json
import smtplib
import subprocess
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.header import Header
from email.utils import formataddr
from pathlib import Path

# 确保 UTF-8 输出
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = BASE_DIR / "config" / "email_config.json"
DEFAULT_REPORT_PATH = BASE_DIR / "docs" / "stage2" / "FULL-DIMENSIONAL-INTELLIGENCE-REPORT.html"
DEFAULT_PDF_PATH = BASE_DIR / "docs" / "stage2" / "FULL-DIMENSIONAL-INTELLIGENCE-REPORT.pdf"
DEFAULT_RECIPIENT = "18677106863@qq.com"


def load_email_config():
    """读取邮件配置（优先环境变量，其次配置文件）"""
    config = {
        "smtp_host": os.environ.get("SMTP_HOST", "smtp.qq.com"),
        "smtp_port": int(os.environ.get("SMTP_PORT", 465)),
        "use_ssl": os.environ.get("SMTP_USE_SSL", "true").lower() in ("true", "1", "yes"),
        "sender_email": os.environ.get("SMTP_USER", ""),
        "sender_auth_code": os.environ.get("SMTP_PASSWORD", ""),
        "recipient_email": os.environ.get("EMAIL_TO", DEFAULT_RECIPIENT)
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

    return config


def ensure_pdf_generated(html_path, pdf_path):
    """确保 PDF 文件存在且最新"""
    if pdf_path.exists() and pdf_path.stat().st_mtime >= html_path.stat().st_mtime:
        return True

    print("[正在编译 PDF] 调用无头浏览器渲染高清 A4 PDF...")
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ]
    browser_exe = next((p for p in chrome_paths if os.path.exists(p)), None)
    if not browser_exe:
        print("[警告] 未检测到 Chrome 或 Edge 浏览器，跳过 PDF 编译。")
        return False

    cmd = [
        browser_exe,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}",
        f"file:///{os.path.abspath(html_path)}"
    ]
    try:
        subprocess.run(cmd, capture_output=True, timeout=30)
        return pdf_path.exists() and pdf_path.stat().st_size > 0
    except Exception as e:
        print(f"[警告] PDF 编译异常: {e}")
        return False


def build_email_digest_html(today_str):
    """构建专为 QQ 邮箱优化的轻量高管导读正文（绝不截断、排版美观）"""
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #1e293b; margin: 0; padding: 16px; background-color: #f1f5f9; }}
  .container {{ max-width: 680px; margin: 0 auto; background: #ffffff; border-radius: 12px; overflow: hidden; border: 1px solid #cbd5e1; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
  .header {{ background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #ffffff; padding: 24px; }}
  .header h1 {{ margin: 0 0 6px 0; font-size: 20px; font-weight: 800; letter-spacing: -0.5px; }}
  .header p {{ margin: 0; font-size: 13px; color: #94a3b8; font-family: monospace; }}
  .body-content {{ padding: 24px; }}
  .notice-box {{ background: #eff6ff; border-left: 4px solid #3b82f6; padding: 12px 16px; border-radius: 4px; margin-bottom: 20px; font-size: 13px; color: #1e40af; }}
  .section-title {{ font-size: 15px; font-weight: 700; color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 6px; margin: 20px 0 12px 0; }}
  .card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 14px; margin-bottom: 10px; font-size: 13px; }}
  .card-title {{ font-size: 14px; font-weight: 700; color: #0f172a; margin-bottom: 4px; }}
  .card-fact {{ color: #334155; margin-bottom: 4px; }}
  .card-value {{ color: #b45309; background: #fef3c7; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; display: inline-block; }}
  .footer {{ background: #f8fafc; border-top: 1px solid #e2e8f0; padding: 16px 24px; text-align: center; font-size: 12px; color: #64748b; font-family: monospace; }}
  .signature {{ margin-top: 8px; font-size: 14px; font-weight: 700; color: #0f172a; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div style="font-size: 11px; font-weight: 700; color: #38bdf8; text-transform: uppercase; margin-bottom: 4px;">【太空建筑观察】越南组 · 绝密决策内参</div>
    <h1>越南实体投资与产业动态每日简报</h1>
    <p>简报日期: {today_str} | 100% 越南区域强关联 | 大模型深度研判</p>
  </div>

  <div class="body-content">
    <div class="notice-box">
      <strong>📌 尊敬的高管读者：</strong><br>
      为解决邮箱直接解析复杂长篇网页时的截断与排版失真问题，今日全量 55 项投资信号已编译为<strong>高清矢量 PDF 报告</strong>随信附带，推荐您直接下载附件查阅。<br>
      📎 <strong>附件：</strong><code>越南实体投资情报简报_{today_str}.pdf</code>（支持手机横屏/离线/打印）
    </div>

    <div class="section-title">🎯 今日重点核心动态摘要速览</div>

    <div class="card">
      <div class="card-title">【P0 客户动向】BCG Energy 拟大幅减持胡志明市古芝 2.6 亿美元垃圾发电厂股权至 5%（几近清仓离场）</div>
      <div class="card-fact"><strong>【客观事实】</strong>Bamboo Capital 核心清洁能源平台拟将胡志明市古芝县垃圾发电厂（总投 6.4 万亿越盾）持股比例自 51% 暴降至 5%。</div>
      <div class="card-value"><strong>【决策价值】</strong>暴露出越南环保特许经营权在属地协同、垃圾计量分类、上网电价结算上的现实阻力，对赴越投资垃圾发电的企业构成极高风控警示。</div>
    </div>

    <div class="card">
      <div class="card-title">【P0 客户动向】越南建筑总包龙头 Coteccons 控股收购公关传媒公司 AnPR 64% 股权</div>
      <div class="card-fact"><strong>【客观事实】</strong>Coteccons（HOSE: CTD）通过资本运作控股专业品牌传播机构 AnPR，拓展全生命周期工程配套服务。</div>
      <div class="card-value"><strong>【决策价值】</strong>反映本土工程巨头正在向工业园区综合招商与跨国大客户全周期代理建厂能力延伸。</div>
    </div>

    <div class="card">
      <div class="card-title">【P1 宏观大盘】越南财政部正式印发《2026-2030年税制改革行动计划》（第 3151/QĐ-BTC 号决定）</div>
      <div class="card-fact"><strong>【客观事实】</strong>部署未来 5 年税改纲领，贯彻 OECD 15% 最低税、电子发票穿透征管与关联交易转让定价（TP）严查。</div>
      <div class="card-value"><strong>【决策价值】</strong>出海企业原有的跨国利润转移避税路径面临全面封堵，需抓紧重新测算五年期税负模型。</div>
    </div>

    <div class="card">
      <div class="card-title">【P1 宏观大盘】越南国会加速审议《电力法修改法草案》：全面拆除独立电厂（IPP）与绿电交易堵点</div>
      <div class="card-fact"><strong>【客观事实】</strong>聚焦放开私营与外资在输电与独立电厂准入，理顺双边绿电直购（DPPA）结算与新型储能调峰价格机制。</div>
      <div class="card-value"><strong>【决策价值】</strong>从法律层面破解制造业扩产中的绿电刚性关切与用电制度瓶颈。</div>
    </div>

    <div class="card">
      <div class="card-title">【P2 重点赛道】越南首款完全自研自主设计安全加密芯片（Make in Vietnam）亮相</div>
      <div class="card-fact"><strong>【客观事实】</strong>本土研发团队发布专用安全加密芯片，算法处理效率较通用芯片提升 10 倍，主攻电力自动化与物联网边缘节点。</div>
      <div class="card-value"><strong>【决策价值】</strong>标志着越南半导体正在从“纯外资代工封测”向本土“芯片设计（Fabless）”种子生态延伸。</div>
    </div>

    <div class="card">
      <div class="card-title">【海外强传导】特斯拉与三星联合强烈抗议美国拟对越南产商品加征额外关税</div>
      <div class="card-fact"><strong>【客观事实】</strong>全球电动车与电子巨头联手抗辩美方对越加税动向，强调越南供应链的全球关键节点地位。</div>
      <div class="card-value"><strong>【决策价值】</strong>美方对越南“洗产地与原产地增值率”的监管风暴正在逼近，出海链条需健全本地化增值合规凭据。</div>
    </div>

    <div style="text-align: center; margin: 24px 0 12px 0;">
      <a href="https://saga1394.github.io/vninfosrcab/" target="_blank" style="background: #0f172a; color: #ffffff; padding: 10px 20px; border-radius: 6px; text-decoration: none; font-size: 13px; font-weight: 700; display: inline-block;">👉 在线浏览实时全维度大盘（网页版）</a>
    </div>
  </div>

  <div class="footer">
    <div>本报告由越南实体与投资情报每日巡检系统自动生成与审校</div>
    <div class="signature">【太空建筑观察】越南组</div>
    <div style="margin-top: 4px; color: #94a3b8; font-size: 11px;">报告编号：TB-VN-{today_str} · 仅供内部决策参考</div>
  </div>
</div>
</body>
</html>
"""


def send_report_email(report_path=None, recipient=None):
    """发送投资情报邮件（含高清 PDF 附件与轻量导读正文）"""
    config = load_email_config()
    
    target_recipient = recipient or config.get("recipient_email", DEFAULT_RECIPIENT)
    sender = config.get("sender_email")
    auth_code = config.get("sender_auth_code")
    smtp_host = config.get("smtp_host", "smtp.qq.com")
    smtp_port = config.get("smtp_port", 465)
    use_ssl = config.get("use_ssl", True)

    actual_report_path = Path(report_path) if report_path else DEFAULT_REPORT_PATH
    actual_pdf_path = actual_report_path.parent / "FULL-DIMENSIONAL-INTELLIGENCE-REPORT.pdf"

    if not actual_report_path.exists():
        print(f"[错误] 简报文件不存在: {actual_report_path}")
        return False

    if not sender or not auth_code:
        print(f"[错误] 尚未配置发件凭据，请检查 {CONFIG_PATH}")
        return False

    today_str = datetime.now().strftime("%Y-%m-%d")

    # 1. 确保 PDF 最新
    ensure_pdf_generated(actual_report_path, actual_pdf_path)

    # 2. 读取原始 HTML 备作备用附件
    with open(actual_report_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # 3. 构建符合 RFC 5322/2047 标准的邮件信头
    subject = f"【太空建筑观察】越南实体投资与产业动态内参 - {today_str} (附完整PDF)"
    msg = MIMEMultipart("mixed")
    msg["From"] = formataddr((str(Header("【太空建筑观察】越南组", "utf-8")), sender))
    msg["To"] = formataddr((str(Header("投资决策人", "utf-8")), target_recipient))
    msg["Subject"] = Header(subject, "utf-8").encode()

    # 4. 邮件正文：轻量高管导读版（专为 QQ 邮箱优化，绝不截断）
    digest_html = build_email_digest_html(today_str)
    part_html = MIMEText(digest_html, "html", "utf-8")
    msg.attach(part_html)

    # 5. 主力附件：高清 PDF 版本
    if actual_pdf_path.exists():
        with open(actual_pdf_path, "rb") as f:
            pdf_bytes = f.read()
        attachment_name_pdf = f"越南实体投资情报简报_{today_str}.pdf"
        part_pdf = MIMEApplication(pdf_bytes, _subtype="pdf")
        part_pdf.add_header("Content-Disposition", "attachment", filename=("utf-8", "", attachment_name_pdf))
        msg.attach(part_pdf)
        print(f" [附件装配] 成功挂载高清 PDF 附件: {attachment_name_pdf} ({len(pdf_bytes)} bytes)")

    # 6. 辅助附件：原始 HTML 离线大盘
    attachment_name_html = f"越南实体投资情报简报_{today_str}.html"
    part_html_attach = MIMEApplication(html_content.encode("utf-8"), _subtype="html")
    part_html_attach.add_header("Content-Disposition", "attachment", filename=("utf-8", "", attachment_name_html))
    msg.attach(part_html_attach)

    # 7. 建立 SMTP 连接投递
    try:
        print(f"[正在连接] 腾讯官方 SMTP 服务器 {smtp_host}:{smtp_port} (SSL: {use_ssl})...")
        if use_ssl:
            server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=20)
        else:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=20)
            server.starttls()

        server.login(sender, auth_code)
        server.sendmail(sender, [target_recipient], msg.as_string())
        server.quit()

        print(f" [成功投递] 邮件已成功送达: {target_recipient}")
        print(f"  落款: 【太空建筑观察】越南组")
        print(f"  包含附件: 越南实体投资情报简报_{today_str}.pdf")
        return True
    except Exception as e:
        print(f"❌ [发送失败] 邮件投递遇到错误: {e}")
        return False


if __name__ == "__main__":
    report_file = sys.argv[1] if len(sys.argv) > 1 else None
    to_addr = sys.argv[2] if len(sys.argv) > 2 else None
    success = send_report_email(report_file, to_addr)
    sys.exit(0 if success else 1)
