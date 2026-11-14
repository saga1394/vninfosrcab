"""
V2/pipeline/delivery/email_sender.py
------------------------------------
阶段 C · 安全邮件投递器（零附件内联 <80KB、单人安全锁定）。
只读复用根目录 `config/email_config.json` 与环境变量凭证，严禁更改根目录任何配置。
未经显式传入收件人或全员参数前，默认锁死仅投递至单人测试地址 `18677106863@qq.com`。
"""

from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
import json
import os
import smtplib
from typing import Any, Dict, List, Optional

V2_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECT_ROOT = os.path.dirname(V2_ROOT)
DEFAULT_V1_EMAIL_CONFIG = os.path.join(PROJECT_ROOT, "config", "email_config.json")
SAFE_DEFAULT_RECIPIENT = ["18677106863@qq.com"]


def load_email_config(config_path: str = DEFAULT_V1_EMAIL_CONFIG) -> Dict[str, Any]:
    cfg: Dict[str, Any] = {
        "smtp_host": os.environ.get("SMTP_HOST", "smtp.qq.com"),
        "smtp_port": int(os.environ.get("SMTP_PORT", 465)),
        "use_ssl": os.environ.get("SMTP_USE_SSL", "true").lower() in ("true", "1", "yes"),
        "sender_email": os.environ.get("SMTP_USER", ""),
        "sender_auth_code": os.environ.get("SMTP_PASSWORD", ""),
        "recipient_emails": list(SAFE_DEFAULT_RECIPIENT),
    }
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            file_cfg = json.load(f)
        for k, v in file_cfg.items():
            if v and not cfg.get(k):
                cfg[k] = v
    return cfg


def dispatch_brief_email(
    html_content: str,
    briefing_date: str,
    recipients: Optional[List[str]] = None,
    dry_run: bool = True,
    config_path: str = DEFAULT_V1_EMAIL_CONFIG,
) -> Dict[str, Any]:
    cfg = load_email_config(config_path=config_path)
    targets = recipients if recipients else SAFE_DEFAULT_RECIPIENT
    byte_size = len(html_content.encode("utf-8"))
    if byte_size >= 80 * 1024:
        raise ValueError(f"邮件正文体积 {byte_size} bytes 超出 80KB 安全线，中止投递。")

    result: Dict[str, Any] = {
        "dry_run": dry_run,
        "recipients": targets,
        "html_bytes": byte_size,
        "has_credentials": bool(cfg.get("sender_email") and cfg.get("sender_auth_code")),
        "sent": False,
    }
    if dry_run:
        return result

    sender = cfg.get("sender_email")
    auth_code = cfg.get("sender_auth_code")
    if not sender or not auth_code:
        raise RuntimeError("缺失 SMTP 发件账号或授权码，无法真实发信。")

    subject = f"【太空建筑观察·越南组】越南实体投资与产业动态简报 ({briefing_date})"
    msg = MIMEMultipart("alternative")
    msg["From"] = formataddr((str(Header("太空建筑观察 · 越南组", "utf-8")), sender))
    msg["To"] = ", ".join(targets)
    msg["Subject"] = str(Header(subject, "utf-8"))
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    host = cfg.get("smtp_host", "smtp.qq.com")
    port = int(cfg.get("smtp_port", 465))
    if cfg.get("use_ssl", True):
        with smtplib.SMTP_SSL(host, port, timeout=20) as srv:
            srv.login(sender, auth_code)
            srv.sendmail(sender, targets, msg.as_string())
    else:
        with smtplib.SMTP(host, port, timeout=20) as srv:
            srv.starttls()
            srv.login(sender, auth_code)
            srv.sendmail(sender, targets, msg.as_string())

    result["sent"] = True
    return result
