"""
V2/sources/drivers/base.py
--------------------------
底层协议驱动层公共基础设施 (补丁 2 & 3)：
- HostThrottle：域名级并发节流阀（同 Host 最大并发 <= 2），防止多厅局集中并发触发 429 封锁；
- HttpFetcher：透传卡片 NetworkConfig（verify_ssl / timeout / headers），并支持单测注入 Mock；
- DriverRecord & BaseProtocolDriver：所有协议驱动统一输出标准原始记录，零 LLM Token 消耗。
"""

from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass, field
from html.parser import HTMLParser
import logging
import re
import subprocess
import sys
import threading
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse
import urllib.request
import ssl

try:
    import httpx
except ImportError:  # pragma: no cover
    httpx = None

from sources.interfaces.contracts import NetworkConfig, ParsedSourceCard

logger = logging.getLogger(__name__)

NAV_STOPWORDS = (
    "chức năng", "nhiệm vụ", "giới thiệu", "sơ đồ tổ chức", "liên hệ",
    "quy chế", "lịch công tác", "contact us", "privacy policy", "tất cả bài viết",
    "chuyển đổi số", "dịch vụ công", "điều lệ", "điều khoản", "hướng dẫn",
    "địa chỉ trụ sở", "danh mục thông tin", "login", "sign in", "register",
)


@dataclass
class DriverRecord:
    """底层协议驱动统一产出的结构化原始记录（尚未做业务认知加工）。"""
    title: str
    direct_url: str
    pub_date_raw: str = ""
    summary: str = ""
    attachment_urls: List[str] = field(default_factory=list)
    extra: Dict[str, Any] = field(default_factory=dict)


class HostThrottle:
    """域名级并发信号量控制器（同 Host 默认并发 <= 2）。"""

    def __init__(self, max_per_host: int = 2) -> None:
        self.max_per_host = max(1, max_per_host)
        self._lock = threading.Lock()
        self._semaphores: Dict[str, threading.Semaphore] = {}

    def _get_semaphore(self, host: str) -> threading.Semaphore:
        with self._lock:
            if host not in self._semaphores:
                self._semaphores[host] = threading.Semaphore(self.max_per_host)
            return self._semaphores[host]

    @contextmanager
    def acquire(self, url: str):
        host = urlparse(url).netloc.lower() or "default"
        sem = self._get_semaphore(host)
        sem.acquire()
        try:
            yield host
        finally:
            sem.release()


DEFAULT_HOST_THROTTLE = HostThrottle(max_per_host=2)


@dataclass
class HttpResponseData:
    status_code: int
    text: str
    content: bytes
    url: str
    headers: Dict[str, str] = field(default_factory=dict)


def _safe_decode_bytes(raw: bytes, hinted_encoding: Optional[str] = None) -> str:
    if not raw:
        return ""
    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        return raw.decode("utf-16", errors="replace")
    if len(raw) >= 4 and raw[:4] in (b"<\x00?\x00", b"\x00<\x00?") or (raw[1:2] == b"\x00" and raw[3:4] == b"\x00"):
        return raw.decode("utf-16-le", errors="replace").lstrip("\ufeff")
    if len(raw) >= 4 and raw[0:1] == b"\x00" and raw[2:3] == b"\x00":
        return raw.decode("utf-16-be", errors="replace").lstrip("\ufeff")
    enc = (hinted_encoding or "utf-8").strip().lower()
    if enc in ("utf-16", "utf16"):
        try:
            return raw.decode("utf-16").lstrip("\ufeff")
        except UnicodeError:
            return raw.decode("utf-16-le", errors="replace").lstrip("\ufeff")
    try:
        return raw.decode(enc, errors="replace")
    except (LookupError, UnicodeError):
        return raw.decode("utf-8", errors="replace")


class HttpFetcher:
    """
    统一 HTTP 请求执行器，严格透传卡片 NetworkConfig 与 HostThrottle。
    支持传入 transport_fn 用于离线测试注入，零外部网络依赖。
    """

    def __init__(
        self,
        throttle: Optional[HostThrottle] = None,
        transport_fn: Optional[Callable[..., HttpResponseData]] = None,
    ) -> None:
        self.throttle = throttle or DEFAULT_HOST_THROTTLE
        self.transport_fn = transport_fn

    def request(
        self,
        method: str,
        url: str,
        network_config: NetworkConfig,
        headers: Optional[Dict[str, str]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        form_body: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> HttpResponseData:
        merged_headers = dict(network_config.headers)
        if headers:
            merged_headers.update(headers)

        with self.throttle.acquire(url):
            if self.transport_fn is not None:
                return self.transport_fn(
                    method=method.upper(),
                    url=url,
                    verify_ssl=network_config.verify_ssl,
                    timeout=network_config.timeout,
                    headers=merged_headers,
                    json_body=json_body,
                    form_body=form_body,
                    params=params,
                )

            if network_config.resolve_ip or network_config.use_curl:
                import json as _json
                from urllib.parse import urlencode as _urlencode
                parsed_u = urlparse(url)
                host = parsed_u.hostname or ""
                port = parsed_u.port or (443 if parsed_u.scheme == "https" else 80)
                curl_bin = "curl.exe" if sys.platform == "win32" else "curl"
                final_url = url
                if params:
                    sep = "&" if "?" in final_url else "?"
                    final_url = f"{final_url}{sep}{_urlencode(params)}"
                cmd = [
                    curl_bin,
                    "-sS",
                    "-L",
                    "-X",
                    method.upper(),
                    "--max-time",
                    str(network_config.timeout),
                ]
                if network_config.resolve_ip:
                    cmd.extend(["--resolve", f"{host}:{port}:{network_config.resolve_ip}"])
                if not network_config.verify_ssl:
                    cmd.append("-k")
                for hk, hv in merged_headers.items():
                    cmd.extend(["-H", f"{hk}: {hv}"])
                if json_body is not None:
                    cmd.extend(["-H", "Content-Type: application/json", "-d", _json.dumps(json_body)])
                elif form_body is not None:
                    cmd.extend(["-d", _urlencode(form_body)])
                cmd.append(final_url)
                proc = subprocess.run(cmd, capture_output=True, check=True)
                raw_bytes = proc.stdout
                return HttpResponseData(
                    status_code=200,
                    text=_safe_decode_bytes(raw_bytes),
                    content=raw_bytes,
                    url=final_url,
                )

            if httpx is not None:
                last_exc: Optional[Exception] = None
                for attempt in range(2):
                    try:
                        with httpx.Client(
                            verify=network_config.verify_ssl,
                            timeout=network_config.timeout,
                            headers=merged_headers,
                            follow_redirects=True,
                        ) as client:
                            resp = client.request(
                                method=method.upper(),
                                url=url,
                                json=json_body,
                                data=form_body,
                                params=params,
                            )
                            resp.raise_for_status()
                            return HttpResponseData(
                                status_code=resp.status_code,
                                text=_safe_decode_bytes(resp.content, resp.encoding),
                                content=resp.content,
                                url=str(resp.url),
                                headers=dict(resp.headers),
                            )
                    except (httpx.RemoteProtocolError, httpx.ReadTimeout, httpx.ConnectError) as exc:
                        last_exc = exc
                        if attempt == 0:
                            continue
                        raise
                if last_exc is not None:  # pragma: no cover
                    raise last_exc

            # Stdlib urllib fallback
            ctx = ssl.create_default_context()
            if not network_config.verify_ssl:
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
            data_bytes = None
            if json_body is not None:
                import json
                data_bytes = json.dumps(json_body).encode("utf-8")
                merged_headers.setdefault("Content-Type", "application/json")
            req = urllib.request.Request(url, data=data_bytes, headers=merged_headers, method=method.upper())
            with urllib.request.urlopen(req, timeout=network_config.timeout, context=ctx) as r:
                raw = r.read()
                charset = r.headers.get_content_charset() or "utf-8"
                return HttpResponseData(
                    status_code=r.status,
                    text=raw.decode(charset, errors="replace"),
                    content=raw,
                    url=r.geturl(),
                    headers=dict(r.headers),
                )

    def probe_live(self, url: str, network_config: Optional[NetworkConfig] = None) -> Tuple[bool, int]:
        """Lazy Probe 物理探活校验：返回 (is_ok, status_code)。"""
        cfg = network_config or NetworkConfig(timeout=10)
        try:
            resp = self.request("GET", url, cfg)
            return (200 <= resp.status_code < 400, resp.status_code)
        except Exception as exc:
            logger.debug("Lazy probe failed for %s: %s", url, exc)
            return (False, 0)


class BaseProtocolDriver(ABC):
    driver_name: str = ""

    @abstractmethod
    def fetch(self, card: ParsedSourceCard, fetcher: Optional[HttpFetcher] = None) -> List[DriverRecord]:
        """执行纯协议级拉取并返回 DriverRecord 列表。"""


def clean_text(raw: str) -> str:
    return re.sub(r"\s+", " ", (raw or "")).strip()


def strip_html_tags(raw_html: str) -> str:
    if not raw_html:
        return ""
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", raw_html, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    return clean_text(text)


def is_noise_nav_text(text: str) -> bool:
    low = clean_text(text).lower()
    if len(low) < 10:
        return True
    return any(sw in low for sw in NAV_STOPWORDS)


def extract_date_from_text(text: str) -> str:
    if not text:
        return ""
    # YYYY-MM-DD
    m_iso = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", text)
    if m_iso:
        return m_iso.group(1)
    # Vietnamese: "31 Tháng 7 2026"
    m_vn = re.search(r"\b(\d{1,2})\s+Tháng\s+(\d{1,2})\s+(20\d{2})\b", text, re.IGNORECASE)
    if m_vn:
        d, mo, y = m_vn.groups()
        return f"{y}-{int(mo):02d}-{int(d):02d}"
    # DD/MM/YYYY or DD-MM-YYYY
    m_dmy = re.search(r"\b(\d{1,2})[/-](\d{1,2})[/-](20\d{2})\b", text)
    if m_dmy:
        d, mo, y = m_dmy.groups()
        return f"{y}-{int(mo):02d}-{int(d):02d}"
    return ""


def absolutize_url(base_url: str, href: str) -> str:
    if not href:
        return ""
    href = href.strip()
    if href.startswith(("javascript:", "mailto:", "#")):
        return ""
    return urljoin(base_url, href)


class SimpleTableParser(HTMLParser):
    """Stdlib HTML table fallback parser when BeautifulSoup is unavailable."""

    def __init__(self) -> None:
        super().__init__()
        self.tables: List[List[List[Dict[str, Any]]]] = []
        self._in_table = False
        self._in_row = False
        self._in_cell = False
        self._curr_table: List[List[Dict[str, Any]]] = []
        self._curr_row: List[Dict[str, Any]] = []
        self._curr_text: List[str] = []
        self._curr_links: List[str] = []
        self._curr_is_header = False

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        t = tag.lower()
        attr_map = dict(attrs)
        if t == "table":
            self._in_table = True
            self._curr_table = []
        elif t == "tr" and self._in_table:
            self._in_row = True
            self._curr_row = []
        elif t in ("td", "th") and self._in_row:
            self._in_cell = True
            self._curr_text = []
            self._curr_links = []
            self._curr_is_header = t == "th"
        elif t == "a" and self._in_cell and attr_map.get("href"):
            self._curr_links.append(attr_map["href"] or "")

    def handle_data(self, data: str) -> None:
        if self._in_cell:
            self._curr_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        t = tag.lower()
        if t in ("td", "th") and self._in_cell:
            self._in_cell = False
            self._curr_row.append({
                "text": clean_text("".join(self._curr_text)),
                "links": list(self._curr_links),
                "is_header": self._curr_is_header,
            })
        elif t == "tr" and self._in_row:
            self._in_row = False
            if self._curr_row:
                self._curr_table.append(self._curr_row)
        elif t == "table" and self._in_table:
            self._in_table = False
            if self._curr_table:
                self.tables.append(self._curr_table)


class SimpleLinkParser(HTMLParser):
    """Stdlib anchor & script fallback parser when BeautifulSoup is unavailable."""

    def __init__(self) -> None:
        super().__init__()
        self._skip_depth = 0
        self._in_a = False
        self._curr_href = ""
        self._curr_a_text: List[str] = []
        self.links: List[Tuple[str, str]] = []
        self._in_next_data = False
        self._next_data_chunks: List[str] = []
        self.next_data_json: str = ""

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        t = tag.lower()
        attr_map = dict(attrs)
        if t == "script" and attr_map.get("id") == "__NEXT_DATA__":
            self._in_next_data = True
            self._next_data_chunks = []
            return
        if t in ("nav", "header", "footer", "aside", "script", "style"):
            self._skip_depth += 1
            return
        if self._skip_depth == 0 and t == "a" and attr_map.get("href"):
            self._in_a = True
            self._curr_href = attr_map["href"] or ""
            self._curr_a_text = []

    def handle_data(self, data: str) -> None:
        if self._in_next_data:
            self._next_data_chunks.append(data)
        elif self._in_a and self._skip_depth == 0:
            self._curr_a_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        t = tag.lower()
        if t == "script" and self._in_next_data:
            self._in_next_data = False
            self.next_data_json = "".join(self._next_data_chunks)
            return
        if t in ("nav", "header", "footer", "aside", "script", "style") and self._skip_depth > 0:
            self._skip_depth -= 1
            return
        if t == "a" and self._in_a:
            self._in_a = False
            txt = clean_text("".join(self._curr_a_text))
            if txt and self._curr_href:
                self.links.append((txt, self._curr_href))
