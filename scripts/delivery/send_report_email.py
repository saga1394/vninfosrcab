#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
邮件推送模块：自动将生成的全中文 HTML 投资情报简报发送至指定邮箱。
支持内嵌 HTML 正文预览与 HTML 完整文件附件双重保障。
"""

import os
import sys
import json
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from pathlib import Path

# 确保 UTF-8 输出
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = BASE_DIR / "config" / "email_config.json"
DEFAULT_REPORT_PATH = BASE_DIR / "docs" / "stage2" / "FULL-DIMENSIONAL-INTELLIGENCE-REPORT.html"
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


def send_report_email(report_path=None, recipient=None):
    """发送 HTML 简报邮件"""
    config = load_email_config()
    
    target_recipient = recipient or config.get("recipient_email", DEFAULT_RECIPIENT)
    sender = config.get("sender_email")
    auth_code = config.get("sender_auth_code")
    smtp_host = config.get("smtp_host", "smtp.qq.com")
    smtp_port = config.get("smtp_port", 465)
    use_ssl = config.get("use_ssl", True)

    actual_report_path = Path(report_path) if report_path else DEFAULT_REPORT_PATH

    if not actual_report_path.exists():
        print(f"[错误] 简报文件不存在: {actual_report_path}")
        return False

    # 检查发件人凭据是否配置
    if not sender or not auth_code:
        print("\n" + "=" * 60)
        print("【邮件发送前置提示】尚未配置发件邮箱与授权码：")
        print(f"目标接收人: {target_recipient}")
        print(f"请在配置文件 {CONFIG_PATH} 中填入您的发信邮箱账号与授权码。")
        print("如果是 QQ 邮箱发给自己：")
        print("  1. 登录 mail.qq.com -> 设置 -> 账户 -> 开启 'POP3/IMAP/SMTP服务'")
        print("  2. 生成 16 位'授权码'（客户端密码）")
        print("  3. 填入 config/email_config.json 即可实现每日自动发送。")
        print("=" * 60 + "\n")
        return False

    # 读取 HTML 简报内容
    with open(actual_report_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    today_str = datetime.now().strftime("%Y-%m-%d")
    subject = f"【越南投资与产业内参】每日简报（全中文审校版）- {today_str}"

    # 构建 MIME 消息
    msg = MIMEMultipart("mixed")
    msg["From"] = f"越南投资情报雷达 <{sender}>"
    msg["To"] = target_recipient
    msg["Subject"] = subject

    # 1. 邮件正文（HTML 富文本渲染）
    part_html = MIMEText(html_content, "html", "utf-8")
    msg.attach(part_html)

    # 2. 邮件附件（保全原始 HTML 离线查看）
    attachment_name = f"越南实体投资情报简报_{today_str}.html"
    part_attach = MIMEApplication(html_content.encode("utf-8"), Name=attachment_name)
    part_attach["Content-Disposition"] = f'attachment; filename="{attachment_name}"'
    msg.attach(part_attach)

    # 建立 SMTP 连接并发送
    try:
        print(f"[正在连接] SMTP 服务器 {smtp_host}:{smtp_port} (SSL: {use_ssl})...")
        if use_ssl:
            server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=15)
        else:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=15)
            server.starttls()

        server.login(sender, auth_code)
        server.sendmail(sender, [target_recipient], msg.as_string())
        server.quit()

        print(f" [成功] 简报已成功投递至: {target_recipient}")
        return True
    except Exception as e:
        print(f"❌ [发送失败] 邮件投递遇到错误: {e}")
        return False


if __name__ == "__main__":
    report_file = sys.argv[1] if len(sys.argv) > 1 else None
    to_addr = sys.argv[2] if len(sys.argv) > 2 else None
    success = send_report_email(report_file, to_addr)
    sys.exit(0 if success else 1)
