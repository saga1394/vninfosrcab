# -*- coding: utf-8 -*-
"""
Production Routine Collector Framework & Engine (Reference Code: 8253)
Automated Inspection Engine for Vietnam Intelligence Gathering

Features:
- Config-driven (loads JSON configuration, e.g. config/sources_core_39.json)
- Multi-protocol adapter matrix: RSS/Atom, REST API, HTML Table, HTML Card/Semantic List, Chrome CDP
- Multi-threaded worker pool with thread-safe SQLite & JSONL dual-track persistence
- High-precision DOM cleaning (stripping header/nav/footer/sidebars, suppressing static menus)
- Intelligent Multi-format Date Parsing (Vietnamese textual dates, standard DD/MM/YYYY, ISO dates)
- Source-specific news subpath routing and regex heuristics
- SHA-256 fingerprint incremental idempotency
- Comprehensive telemetry, metrics reporting, and run logging
- Strict Zero-Token compliance
"""

import os
import sys
import json
import time
import re
import hashlib
import threading
import argparse
import subprocess
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin

# Force UTF-8 stdout on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CURL_BIN = "curl.exe" if sys.platform == "win32" else "curl"

import httpx
from bs4 import BeautifulSoup
import feedparser
import sqlite3

DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,application/json,*/*;q=0.8',
    'Accept-Language': 'vi,en-US;q=0.9,en;q=0.8,zh-CN;q=0.7',
}

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "daily"))
os.makedirs(DATA_DIR, exist_ok=True)

db_lock = threading.Lock()

NAV_STOPWORDS = [
    'chức năng', 'nhiệm vụ', 'giới thiệu', 'sơ đồ tổ chức', 'liên hệ', 'bản đồ',
    'quy chế', 'lịch công tác', 'contact us', 'privacy policy', 'tiềm năng phát triển',
    'các đơn vị hành chính', 'tổng quan', 'làng nghề', 'chuyển đổi số', 'dịch vụ công',
    'điều lệ', 'điều khoản', 'hướng dẫn', 'thủ tục', 'văn phòng hiệp hội', 'thông tin hội viên',
    'banking & finance', 'vietnamese edition', 'industrial real estate', 'tất cả bài viết',
    'chính sách', 'lịch sử phát triển', 'địa chỉ trụ sở', 'văn bản tiện ích', 'danh mục thông tin'
]

def compute_fingerprint(source_id: str, url: str, title: str) -> str:
    raw = f"{source_id}:{url.strip() or title.strip()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

def init_db(db_path: str):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS raw_materials (
        fingerprint TEXT PRIMARY KEY,
        source_id TEXT NOT NULL,
        source_name TEXT NOT NULL,
        category TEXT NOT NULL,
        tier TEXT NOT NULL,
        fetch_channel TEXT NOT NULL,
        province TEXT,
        dimension_hints TEXT,
        title TEXT NOT NULL,
        pub_date TEXT,
        snippet TEXT,
        url TEXT NOT NULL,
        fetched_at TEXT NOT NULL
    );
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_source ON raw_materials(source_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_pub_date ON raw_materials(pub_date);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_province ON raw_materials(province);")
    conn.commit()
    conn.close()

def save_record(db_path: str, jsonl_path: str, record: dict) -> bool:
    with db_lock:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("""
        INSERT OR IGNORE INTO raw_materials 
        (fingerprint, source_id, source_name, category, tier, fetch_channel, province, dimension_hints, title, pub_date, snippet, url, fetched_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record["fingerprint"],
            record["source_id"],
            record["source_name"],
            record["category"],
            record["tier"],
            record["fetch_channel"],
            record.get("province", ""),
            json.dumps(record.get("dimension_hints", []), ensure_ascii=False),
            record["title"],
            record["pub_date"],
            record["snippet"],
            record["url"],
            record["fetched_at"]
        ))
        is_new = cur.rowcount > 0
        conn.commit()
        conn.close()

        if is_new:
            with open(jsonl_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        return is_new

def clean_database_noise(db_path: str):
    """Purge historical noisy menu items and invalid titles from the SQLite database."""
    with db_lock:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        # Delete entries matching stop words or too short
        conditions = " OR ".join([f"title LIKE '%{sw}%'" for sw in NAV_STOPWORDS[:15]])
        query = f"DELETE FROM raw_materials WHERE length(title) < 20 OR ({conditions});"
        cur.execute(query)
        deleted = cur.rowcount
        conn.commit()
        conn.close()
        if deleted > 0:
            print(f"[*] Cleaned {deleted} noisy/navigation records from SQLite database.")

def parse_date_heuristic(el, text_blob: str, href: str) -> str:
    # 1. Class or tag with date/time
    d_tag = el.find(['time', 'span', 'p'], class_=lambda c: c and any(k in str(c).lower() for k in ['date', 'time', 'ngay', 'published']))
    if d_tag and d_tag.get_text(strip=True):
        raw = d_tag.get_text(strip=True)
        m = re.search(r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{4})\b', raw)
        if m:
            return m.group(1)
        m2 = re.search(r'\b(\d{4}-\d{2}-\d{2})\b', raw)
        if m2:
            return m2.group(1)
            
    # 2. Vietnamese textual date: "31 Tháng 7 2026" or "Tháng 8 2026"
    m_vn = re.search(r'(\d{1,2})\s+Tháng\s+(\d{1,2})\s+(\d{4})', text_blob, re.I)
    if m_vn:
        d, mo, y = m_vn.groups()
        return f"{y}-{int(mo):02d}-{int(d):02d}"
        
    # 3. Standard date regex in text
    m = re.search(r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{4})\b', text_blob)
    if m:
        return m.group(1)
    m2 = re.search(r'\b(\d{4}-\d{2}-\d{2})\b', text_blob)
    if m2:
        return m2.group(1)
        
    # 4. Look inside URL path (e.g. 2026/10/28 or 2026-10-28)
    m_url = re.search(r'/(202[4-6])[/-](\d{1,2})[/-](\d{1,2})', href)
    if m_url:
        y, mo, d = m_url.groups()
        return f"{y}-{int(mo):02d}-{int(d):02d}"
        
    # 5. Fallback to today
    return datetime.now().strftime("%Y-%m-%d")

# ----------------- Adapters Matrix -----------------

class AdapterMatrix:
    def __init__(self, client: httpx.Client):
        self.client = client

    def fetch_rss(self, src: dict) -> list:
        url = src.get("endpoint") or src.get("target_url")
        resp = self.client.get(url, timeout=15)
        feed = feedparser.parse(resp.content)
        records = []
        for entry in feed.entries[:5]:
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()
            if not title or not link:
                continue
            pub_date = entry.get("published", "") or entry.get("updated", "") or datetime.now().strftime("%Y-%m-%d")
            summary = entry.get("summary", "") or entry.get("description", "")
            snippet = BeautifulSoup(summary, "html.parser").get_text(strip=True)[:250]
            records.append({
                "fingerprint": compute_fingerprint(src["source_id"], link, title),
                "source_id": src["source_id"],
                "source_name": src["name"],
                "category": src["category"],
                "tier": src["tier"],
                "fetch_channel": "rss",
                "province": src.get("province", "National"),
                "dimension_hints": src.get("dimension_hints", []),
                "title": title,
                "pub_date": pub_date,
                "snippet": snippet or title,
                "url": link,
                "fetched_at": datetime.now(timezone.utc).isoformat()
            })
        return records

    def fetch_api(self, src: dict) -> list:
        api_type = src.get("api_type", "")
        records = []

        if api_type == "cninfo":
            # 巨潮资讯网
            today_fmt = datetime.now().strftime("%Y-%m-%d")
            payload = {
                "pageNum": 1, "pageSize": 5, "column": "szse", "tabName": "fulltext",
                "plateau": "", "stock": "", "searchkey": "越南", "secid": "",
                "category": "", "trade": "", "seDate": f"2024-01-01~{today_fmt}"
            }
            resp = self.client.post(src["endpoint"], data=payload, timeout=15)
            data = resp.json()
            for item in data.get("announcements", [])[:5]:
                title = f"[{item.get('secCode')}] {item.get('secName')}: {item.get('announcementTitle')}"
                ts = item.get("announcementTime")
                pub_date = datetime.fromtimestamp(ts/1000).strftime('%Y-%m-%d') if ts else datetime.now().strftime("%Y-%m-%d")
                link = f"http://static.cninfo.com.cn/{item.get('adjunctUrl', '')}"
                snippet = f"证券代码: {item.get('secCode')}, 公司名称: {item.get('secName')}, 公告文件大小: {item.get('adjunctSize')}KB"
                records.append({
                    "fingerprint": compute_fingerprint(src["source_id"], link, title),
                    "source_id": src["source_id"],
                    "source_name": src["name"],
                    "category": src["category"],
                    "tier": src["tier"],
                    "fetch_channel": "api",
                    "province": src.get("province", "National"),
                    "dimension_hints": src.get("dimension_hints", []),
                    "title": title,
                    "pub_date": pub_date,
                    "snippet": snippet,
                    "url": link,
                    "fetched_at": datetime.now(timezone.utc).isoformat()
                })

        elif api_type == "szse":
            # 深圳证券交易所 (通过 curl 解决 Windows TLS 连接重置问题)
            body = json.dumps({
                "seDate": ["", ""], "searchKey": ["越南"], "channelCode": ["listedNotice_disc"],
                "pageSize": 5, "pageNum": 1
            })
            cmd = [
                CURL_BIN, "-s", "-k", "-X", "POST", src["endpoint"],
                "-H", "Content-Type: application/json",
                "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "-H", "Referer: https://www.szse.cn/",
                "-d", body
            ]
            res = subprocess.run(cmd, capture_output=True, timeout=15)
            data = json.loads(res.stdout.decode("utf-8", errors="ignore"))
            for item in data.get("data", [])[:5]:
                title = item.get("title", "").strip()
                code = item.get("secCode", [""])[0] if item.get("secCode") else ""
                pub_date = str(item.get("publishTime", ""))[:10] or datetime.now().strftime("%Y-%m-%d")
                doc_id = item.get("id", "")
                link = f"https://www.szse.cn/disclosure/listed/bulletin/detail/index.html?{doc_id}"
                snippet = f"证券代码: {code}, 标题: {title}"
                records.append({
                    "fingerprint": compute_fingerprint(src["source_id"], link, title),
                    "source_id": src["source_id"],
                    "source_name": src["name"],
                    "category": src["category"],
                    "tier": src["tier"],
                    "fetch_channel": "api",
                    "province": src.get("province", "National"),
                    "dimension_hints": src.get("dimension_hints", []),
                    "title": title,
                    "pub_date": pub_date,
                    "snippet": snippet,
                    "url": link,
                    "fetched_at": datetime.now(timezone.utc).isoformat()
                })

        elif api_type == "hkex":
            # 港交所披露易
            cmd = [
                CURL_BIN, "-s", "-k",
                "https://www1.hkexnews.hk/search/titleSearchServlet.do?sortDir=0&sortByOptions=DateTime&category=0&market=SEHK&documentType=-1&t1code=-2&t2Gcode=-2&t2code=-2&title=%E8%B6%8A%E5%8D%97&lang=zh",
                "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "-H", "Referer: https://www1.hkexnews.hk/search/titlesearch.xhtml?lang=zh"
            ]
            res = subprocess.run(cmd, capture_output=True, timeout=15)
            d = json.loads(res.stdout.decode("utf-8", errors="ignore"))
            items = json.loads(d.get("result", "[]"))
            for item in items[:5]:
                code = item.get("STOCK_CODE", "")
                sname = item.get("STOCK_NAME", "")
                title = f"[{code}] {sname}: {item.get('TITLE', '')}"
                pub_date = item.get("DATE_TIME", "") or datetime.now().strftime("%Y-%m-%d")
                file_link = f"https://www1.hkexnews.hk{item.get('FILE_LINK', '')}"
                snippet = f"股份代号: {code}, 上市公司: {sname}, 公告大小: {item.get('FILE_INFO', '')}"
                records.append({
                    "fingerprint": compute_fingerprint(src["source_id"], file_link, title),
                    "source_id": src["source_id"],
                    "source_name": src["name"],
                    "category": src["category"],
                    "tier": src["tier"],
                    "fetch_channel": "api",
                    "province": src.get("province", "National"),
                    "dimension_hints": src.get("dimension_hints", []),
                    "title": title,
                    "pub_date": pub_date,
                    "snippet": snippet,
                    "url": file_link,
                    "fetched_at": datetime.now(timezone.utc).isoformat()
                })

        elif api_type == "edgar":
            # 美国 SEC EDGAR EFTS
            sec_headers = {
                'User-Agent': 'VnInvestmentResearch AdminContact@vnresearch.org',
                'Accept': 'application/json'
            }
            resp = self.client.get(src["endpoint"], headers=sec_headers, timeout=15)
            data = resp.json()
            hits = data.get("hits", {}).get("hits", [])
            for h in hits[:5]:
                source_doc = h.get("_source", {})
                names = source_doc.get("display_names", [""])[0] if source_doc.get("display_names") else "SEC Registrant"
                form = source_doc.get("form", "Filing")
                period = source_doc.get("file_date", "") or source_doc.get("period_ending", "") or datetime.now().strftime("%Y-%m-%d")
                file_num = source_doc.get("file_num", [""])[0] if source_doc.get("file_num") else ""
                title = f"[{form}] {names} (Filed: {period})"
                doc_id = h.get("_id", "")
                link = f"https://www.sec.gov/edgar/browse/?CIK={source_doc.get('ciks', [''])[0]}" if source_doc.get('ciks') else f"https://www.sec.gov/edgar/search/#/q=Vietnam"
                snippet = f"SEC Form {form}, File No: {file_num}, CIK: {source_doc.get('ciks', [''])[0]}"
                records.append({
                    "fingerprint": compute_fingerprint(src["source_id"], link, title),
                    "source_id": src["source_id"],
                    "source_name": src["name"],
                    "category": src["category"],
                    "tier": src["tier"],
                    "fetch_channel": "api",
                    "province": src.get("province", "National"),
                    "dimension_hints": src.get("dimension_hints", []),
                    "title": title,
                    "pub_date": period,
                    "snippet": snippet,
                    "url": link,
                    "fetched_at": datetime.now(timezone.utc).isoformat()
                })

        elif api_type == "danang_dseza":
            # 岘港高新区管委会 REST API
            resp = self.client.get(src["endpoint"], timeout=15)
            data = resp.json()
            items = data if isinstance(data, list) else data.get("data", []) or data.get("items", []) or []
            for item in items[:5]:
                title = item.get("title", "") or item.get("name", "")
                if not title:
                    continue
                code = item.get("id", "") or item.get("slug", "")
                link = f"https://dseza.danang.gov.vn/tin-tuc/{code}"
                pub_date = str(item.get("created_at", ""))[:10] or str(item.get("published_at", ""))[:10] or datetime.now().strftime("%Y-%m-%d")
                snippet = item.get("summary", "") or item.get("description", "") or title
                records.append({
                    "fingerprint": compute_fingerprint(src["source_id"], link, title),
                    "source_id": src["source_id"],
                    "source_name": src["name"],
                    "category": src["category"],
                    "tier": src["tier"],
                    "fetch_channel": "api",
                    "province": src.get("province", "Đà Nẵng"),
                    "dimension_hints": src.get("dimension_hints", []),
                    "title": title,
                    "pub_date": pub_date,
                    "snippet": snippet[:250],
                    "url": link,
                    "fetched_at": datetime.now(timezone.utc).isoformat()
                })

        return records

    def fetch_table(self, src: dict) -> list:
        table_type = src.get("table_type", "")
        records = []

        if table_type in ["mae_eia", "mae_permit"]:
            # 环评公示 / 排污许可 (使用 native curl 并绑定健康节点 103.9.85.148，避开故障节点 103.9.85.134 导致的 TLS Reset)
            cmd = [CURL_BIN, "-k", "-s", "--resolve", "thamvan.mae.gov.vn:443:103.9.85.148", src["endpoint"]]
            res = subprocess.run(cmd, capture_output=True, timeout=20)
            soup = BeautifulSoup(res.stdout.decode("utf-8", errors="ignore"), "html.parser")
            table = soup.find("table")
            if table:
                rows = table.find_all("tr")[1:6]
                for r in rows:
                    cols = [td.get_text(strip=True) for td in r.find_all("td")]
                    if len(cols) >= 3:
                        title_a = r.find("a")
                        title = title_a.get_text(strip=True) if title_a else (cols[1] if len(cols) > 1 else cols[0])
                        link = urljoin("https://thamvan.mae.gov.vn", title_a["href"]) if title_a and title_a.get("href") else src["endpoint"]
                        location = cols[2] if len(cols) > 2 else ""
                        investor = cols[3] if len(cols) > 3 else ""
                        pub_date = cols[4] if len(cols) > 4 and cols[4] else datetime.now().strftime("%Y-%m-%d")
                        snippet = f"Địa điểm: {location}. Chủ dự án: {investor}"
                        records.append({
                            "fingerprint": compute_fingerprint(src["source_id"], link, title),
                            "source_id": src["source_id"],
                            "source_name": src["name"],
                            "category": src["category"],
                            "tier": src["tier"],
                            "fetch_channel": "table",
                            "province": src.get("province", "National"),
                            "dimension_hints": src.get("dimension_hints", []),
                            "title": title,
                            "pub_date": pub_date,
                            "snippet": snippet[:250],
                            "url": link,
                            "fetched_at": datetime.now(timezone.utc).isoformat()
                        })

        return records

    def fetch_card(self, src: dict) -> list:
        url = src.get("endpoint") or src.get("target_url")
        html_text = ""
        try:
            resp = self.client.get(url, timeout=15)
            html_text = resp.text
        except Exception:
            # Native curl fallback
            cmd = [CURL_BIN, "-k", "-s", url]
            res = subprocess.run(cmd, capture_output=True, timeout=20)
            html_text = res.stdout.decode("utf-8", errors="ignore")

        soup = BeautifulSoup(html_text, "html.parser")
        
        # 1. Structural DOM Pre-cleaning (strip navigation tags and menus)
        for tag in soup(['nav', 'header', 'footer', 'aside', 'script', 'style', 'noscript']):
            tag.decompose()
        for el in soup.find_all(['ul', 'ol', 'div', 'section'], class_=re.compile(r'^(menu|main-nav|navbar|site-header|site-footer|breadcrumb|top-nav|navigation)$', re.I)):
            el.decompose()

        records = []
        seen_titles = set()
        sid = src["source_id"]

        # Strategy A: Candidate container extraction
        cards = soup.find_all(["div", "article", "li"], class_=lambda c: c and any(k in str(c).lower() for k in ["news", "item", "post", "article", "tin", "entry", "box"]))
        for c in cards:
            a = c.find("a", href=True)
            if not a:
                continue
            t = a.get_text(' ', strip=True)
            if len(t) < 20 or t.count(' ') < 2:
                continue
            if any(sw in t.lower() for sw in NAV_STOPWORDS):
                continue
            if t in seen_titles:
                continue
                
            href = a["href"]
            # Domain-specific filtering
            if sid == "src-A07" and ("/detail" not in href.lower() or "newsid" not in href.lower()):
                continue
            if sid == "src-B04" and ("/vi/blog/" not in href or "/category/" in href):
                continue
            if sid == "VN-LOC-03-BN-A" and ("/news/-/details/" not in href and "/vanban/" not in href):
                continue
            if sid == "src-ASSOC-01" and "danhba" in href.lower():
                continue

            seen_titles.add(t)
            link = urljoin(url, href)
            date_str = parse_date_heuristic(c, c.get_text(' ', strip=True), href)
            desc = c.find(class_=lambda cls: cls and any(k in str(cls).lower() for k in ["desc", "summary", "lead", "brief", "content"]))
            snippet = desc.get_text(strip=True) if desc else t

            records.append({
                "fingerprint": compute_fingerprint(src["source_id"], link, t),
                "source_id": src["source_id"],
                "source_name": src["name"],
                "category": src["category"],
                "tier": src["tier"],
                "fetch_channel": "card",
                "province": src.get("province", "National"),
                "dimension_hints": src.get("dimension_hints", []),
                "title": t,
                "pub_date": date_str,
                "snippet": snippet[:250],
                "url": link,
                "fetched_at": datetime.now(timezone.utc).isoformat()
            })
            if len(records) >= 5:
                break

        # Strategy B: Fallback scan across all clean anchor tags
        if len(records) < 3:
            for a in soup.find_all("a", href=True):
                t = a.get_text(' ', strip=True)
                if len(t) < 22 or t.count(' ') < 2:
                    continue
                if any(sw in t.lower() for sw in NAV_STOPWORDS):
                    continue
                if t in seen_titles:
                    continue

                href = a["href"]
                # Domain-specific filtering in fallback
                if sid == "src-A07" and ("/detail" not in href.lower() or "newsid" not in href.lower()):
                    continue
                if sid == "src-B04" and ("/vi/blog/" not in href or "/category/" in href):
                    continue
                if sid == "VN-LOC-03-BN-A" and ("/news/-/details/" not in href and "/vanban/" not in href):
                    continue
                if sid == "src-ASSOC-01" and ("danhba" in href.lower() or not ('_p1_1-' in href or '.html' in href)):
                    continue

                seen_titles.add(t)
                link = urljoin(url, href)
                parent_context = a.parent.get_text(' ', strip=True) if a.parent else t
                date_str = parse_date_heuristic(a.parent if a.parent else a, parent_context, href)

                records.append({
                    "fingerprint": compute_fingerprint(src["source_id"], link, t),
                    "source_id": src["source_id"],
                    "source_name": src["name"],
                    "category": src["category"],
                    "tier": src["tier"],
                    "fetch_channel": "card",
                    "province": src.get("province", "National"),
                    "dimension_hints": src.get("dimension_hints", []),
                    "title": t,
                    "pub_date": date_str,
                    "snippet": t,
                    "url": link,
                    "fetched_at": datetime.now(timezone.utc).isoformat()
                })
                if len(records) >= 5:
                    break

        return records

    def fetch_cdp(self, src: dict) -> list:
        url = src.get("endpoint") or src.get("target_url")
        cmd = [
            CHROME_PATH,
            "--headless=new",
            "--disable-gpu",
            "--virtual-time-budget=5000",
            "--dump-dom",
            url
        ]
        res = subprocess.run(cmd, capture_output=True, timeout=25)
        soup = BeautifulSoup(res.stdout.decode("utf-8", errors="ignore"), "html.parser")
        records = []
        seen_titles = set()
        for a in soup.find_all("a", href=True):
            t = a.get_text(' ', strip=True)
            if len(t) > 22 and t.count(' ') >= 2 and not any(sw in t.lower() for sw in NAV_STOPWORDS) and t not in seen_titles:
                seen_titles.add(t)
                link = urljoin(url, a["href"])
                records.append({
                    "fingerprint": compute_fingerprint(src["source_id"], link, t),
                    "source_id": src["source_id"],
                    "source_name": src["name"],
                    "category": src["category"],
                    "tier": src["tier"],
                    "fetch_channel": "cdp",
                    "province": src.get("province", "National"),
                    "dimension_hints": src.get("dimension_hints", []),
                    "title": t,
                    "pub_date": datetime.now().strftime("%Y-%m-%d"),
                    "snippet": t,
                    "url": link,
                    "fetched_at": datetime.now(timezone.utc).isoformat()
                })
                if len(records) >= 5:
                    break
        return records

# ----------------- Worker & Runner -----------------

def inspect_single_source(src: dict, matrix: AdapterMatrix, db_path: str, jsonl_path: str) -> dict:
    source_id = src["source_id"]
    source_name = src["name"]
    channel = src.get("channel", "card")
    t0 = time.time()
    extracted = []
    error_msg = ""
    status = "SUCCESS"

    try:
        if channel == "rss":
            extracted = matrix.fetch_rss(src)
        elif channel == "api":
            extracted = matrix.fetch_api(src)
        elif channel == "table":
            extracted = matrix.fetch_table(src)
        elif channel == "card":
            extracted = matrix.fetch_card(src)
        elif channel == "cdp":
            extracted = matrix.fetch_cdp(src)
        else:
            status = "UNKNOWN_CHANNEL"
            error_msg = f"Unsupported channel: {channel}"
    except Exception as e:
        status = "ERROR"
        error_msg = str(e)

    elapsed_s = round(time.time() - t0, 2)
    new_count = 0
    if extracted:
        for r in extracted:
            if save_record(db_path, jsonl_path, r):
                new_count += 1

    return {
        "source_id": source_id,
        "name": source_name,
        "cluster": src.get("cluster", "General"),
        "channel": channel,
        "province": src.get("province", "National"),
        "status": status,
        "elapsed_s": elapsed_s,
        "extracted_count": len(extracted),
        "new_count": new_count,
        "error_msg": error_msg,
        "sample_titles": [r["title"] for r in extracted[:2]]
    }

def run_collector(config_path: str, workers: int = 6, clean_first: bool = False):
    start_time = datetime.now()
    today_str = start_time.strftime("%Y-%m-%d")
    jsonl_path = os.path.join(DATA_DIR, f"{today_str}.jsonl")
    db_path = os.path.join(DATA_DIR, "collector.db")
    init_db(db_path)

    if clean_first:
        clean_database_noise(db_path)

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    sources = [s for s in config.get("sources", []) if s.get("enabled", True)]
    print(f"\n================================================================================")
    print(f"🚀 [Routine Collector Engine] Starting inspection across {len(sources)} sources")
    print(f"   Date: {today_str} | Concurrency Workers: {workers}")
    print(f"   Storage: {jsonl_path}")
    print(f"   Database: {db_path}")
    print(f"================================================================================\n")

    client = httpx.Client(verify=False, follow_redirects=True, timeout=18.0, headers=DEFAULT_HEADERS)
    matrix = AdapterMatrix(client)

    telemetry = []
    t_start = time.time()

    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_map = {
            executor.submit(inspect_single_source, src, matrix, db_path, jsonl_path): src
            for src in sources
        }
        for future in as_completed(future_map):
            src_def = future_map[future]
            try:
                res = future.result()
                telemetry.append(res)
                icon = "✅" if res["status"] == "SUCCESS" and res["extracted_count"] > 0 else ("⚠️" if res["extracted_count"] == 0 else "❌")
                print(f" {icon} [{res['source_id']:<15}] [{res['channel']:<5}] {res['name'][:28]:<28} | {res['extracted_count']:>2} ext | +{res['new_count']:>2} new | {res['elapsed_s']:>4.1f}s")
                if res["error_msg"]:
                    print(f"    └─ Error: {res['error_msg']}")
            except Exception as exc:
                print(f" ❌ [{src_def['source_id']}] Unhandled future exception: {exc}")
                telemetry.append({
                    "source_id": src_def["source_id"], "name": src_def["name"],
                    "cluster": src_def.get("cluster", ""), "channel": src_def.get("channel", ""),
                    "status": "CRITICAL_FAIL", "elapsed_s": 0.0, "extracted_count": 0,
                    "new_count": 0, "error_msg": str(exc), "sample_titles": []
                })

    client.close()
    total_elapsed = round(time.time() - t_start, 2)

    # Aggregated stats
    total_sources = len(telemetry)
    success_sources = sum(1 for t in telemetry if t["status"] == "SUCCESS" and t["extracted_count"] > 0)
    zero_extracted_sources = sum(1 for t in telemetry if t["extracted_count"] == 0 and t["status"] == "SUCCESS")
    error_sources = sum(1 for t in telemetry if t["status"] in ["ERROR", "CRITICAL_FAIL"])
    total_extracted = sum(t["extracted_count"] for t in telemetry)
    total_new = sum(t["new_count"] for t in telemetry)

    # SQLite DB total state
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT count(*), count(DISTINCT source_id), count(DISTINCT province) FROM raw_materials;")
    db_total, db_sources, db_provinces = cur.fetchone()
    conn.close()

    run_report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "today": today_str,
        "config_used": config_path,
        "workers": workers,
        "total_elapsed_seconds": total_elapsed,
        "total_sources_configured": total_sources,
        "successful_sources": success_sources,
        "zero_extracted_sources": zero_extracted_sources,
        "error_sources": error_sources,
        "total_extracted_records": total_extracted,
        "total_new_records_inserted": total_new,
        "sqlite_total_rows": db_total,
        "sqlite_distinct_sources": db_sources,
        "sqlite_distinct_provinces": db_provinces,
        "detailed_telemetry": telemetry
    }

    report_path = os.path.join(DATA_DIR, f"{today_str}_run_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(run_report, f, ensure_ascii=False, indent=2)

    print(f"\n================================================================================")
    print(f"📊 [Routine Inspection Complete Summary]")
    print(f"   Execution Time: {total_elapsed}s | Total Configured: {total_sources}")
    print(f"   Success Rate: {success_sources}/{total_sources} ({success_sources/total_sources*100:.1f}%)")
    print(f"   Records Extracted: {total_extracted} | New Records Inserted: {total_new}")
    print(f"   Zero Extracted: {zero_extracted_sources} | Failed/Errors: {error_sources}")
    print(f"   SQLite Cumulative Rows: {db_total} (across {db_sources} sources, {db_provinces} provinces)")
    print(f"   Report Saved: {report_path}")
    print(f"================================================================================\n")
    return run_report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Routine Collector Framework Engine")
    parser.add_argument("--config", default=os.path.join(os.path.dirname(__file__), "..", "..", "config", "sources_core_39.json"))
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--clean", action="store_true", help="Clean historical noisy records from DB")
    args = parser.parse_args()

    run_collector(args.config, args.workers, clean_first=args.clean)
