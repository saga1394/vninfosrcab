# -*- coding: utf-8 -*-
"""
Workflow Runner Test Script
Demonstrating end-to-end:
1. Fast scripts (RSS, REST API, HTML Table, HTML Card)
2. Built-in Chrome Headless / CDP fallback (SPA & dynamic rendering)
3. Normalized 4-element record extraction + Fingerprint deduplication
4. Daily JSONL + SQLite persistence
"""

import os
import sys
import json
import time
import hashlib
import subprocess
from datetime import datetime, timezone
import httpx
import feedparser
from bs4 import BeautifulSoup
import sqlite3

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "daily"))
os.makedirs(DATA_DIR, exist_ok=True)

TODAY_STR = datetime.now().strftime("%Y-%m-%d")
JSONL_PATH = os.path.join(DATA_DIR, f"{TODAY_STR}.jsonl")
DB_PATH = os.path.join(DATA_DIR, "collector.db")

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

def save_record(record: dict) -> bool:
    # 1. Insert into SQLite (ignore duplicates)
    conn = sqlite3.connect(DB_PATH)
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

    # 2. Append to JSONL only if new (or log)
    if is_new:
        with open(JSONL_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return is_new

# ----------------- Adapters -----------------

def fetch_rss_source(source_id: str, source_name: str, url: str, category: str, province: str, dims: list):
    print(f"[*] [RSS] Fetching {source_name} ({url})...")
    t0 = time.time()
    resp = httpx.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"}, follow_redirects=True)
    feed = feedparser.parse(resp.content)
    elapsed = time.time() - t0
    records = []
    for entry in feed.entries[:3]:
        title = entry.get("title", "").strip()
        link = entry.get("link", "").strip()
        pub_date = entry.get("published", "") or entry.get("updated", "")
        snippet = BeautifulSoup(entry.get("summary", "") or entry.get("description", ""), "html.parser").get_text(strip=True)[:250]
        rec = {
            "fingerprint": compute_fingerprint(source_id, link, title),
            "source_id": source_id,
            "source_name": source_name,
            "category": category,
            "tier": "L1",
            "fetch_channel": "rss",
            "province": province,
            "dimension_hints": dims,
            "title": title,
            "pub_date": pub_date,
            "snippet": snippet,
            "url": link,
            "fetched_at": datetime.now(timezone.utc).isoformat()
        }
        records.append(rec)
    print(f"    -> Extracted {len(records)} records in {elapsed:.2f}s")
    return records

def fetch_api_source(source_id: str, source_name: str, url: str, category: str, province: str, dims: list):
    print(f"[*] [API] Fetching {source_name} ({url})...")
    t0 = time.time()
    headers = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}
    payload = {"channelId": "4", "pageIndex": 1, "pageSize": 3}
    resp = httpx.post(url, json=payload, headers=headers, timeout=15, verify=False)
    data = resp.json()
    elapsed = time.time() - t0
    records = []
    items = data.get("data", []) or data.get("items", []) or []
    for it in items[:3]:
        title = it.get("title", "").strip()
        code = it.get("articleId", "") or it.get("id", "")
        link = f"https://mof.gov.vn/webcenter/portal/btcvn/pages_r/l/tin-bo-tai-chinh?dDocName={code}"
        pub_date = it.get("publishedDate", "") or it.get("createdDate", "")
        snippet = it.get("summary", "") or it.get("shortContent", "") or ""
        rec = {
            "fingerprint": compute_fingerprint(source_id, link, title),
            "source_id": source_id,
            "source_name": source_name,
            "category": category,
            "tier": "L1",
            "fetch_channel": "api",
            "province": province,
            "dimension_hints": dims,
            "title": title,
            "pub_date": str(pub_date)[:10],
            "snippet": snippet[:250],
            "url": link,
            "fetched_at": datetime.now(timezone.utc).isoformat()
        }
        records.append(rec)
    print(f"    -> Extracted {len(records)} records in {elapsed:.2f}s")
    return records

def fetch_table_source(source_id: str, source_name: str, url: str, category: str, province: str, dims: list):
    print(f"[*] [Table] Fetching {source_name} ({url})...")
    t0 = time.time()
    html_text = ""
    try:
        resp = httpx.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"}, verify=False)
        html_text = resp.text
    except Exception as e:
        print(f"    [!] httpx error ({e}), falling back to native curl.exe...")
        res = subprocess.run(["curl.exe", "-k", "-s", url], capture_output=True, encoding="utf-8", errors="ignore", timeout=20)
        html_text = res.stdout
        
    soup = BeautifulSoup(html_text, "html.parser")
    elapsed = time.time() - t0
    table = soup.find("table")
    records = []
    if table:
        rows = table.find_all("tr")[1:4] # top 3
        for r in rows:
            cols = [td.get_text(strip=True) for td in r.find_all("td")]
            if len(cols) >= 3:
                title_a = r.find("a")
                title = title_a.get_text(strip=True) if title_a else (cols[1] if len(cols) > 1 else cols[0])
                link = ("https://thamvan.mae.gov.vn" + title_a["href"]) if title_a and title_a.get("href") else url
                location = cols[2] if len(cols) > 2 else ""
                investor = cols[3] if len(cols) > 3 else ""
                snippet = f"Địa điểm: {location}. Chủ dự án: {investor}"
                rec = {
                    "fingerprint": compute_fingerprint(source_id, link, title),
                    "source_id": source_id,
                    "source_name": source_name,
                    "category": category,
                    "tier": "L1",
                    "fetch_channel": "html_table",
                    "province": province,
                    "dimension_hints": dims,
                    "title": title,
                    "pub_date": cols[4] if len(cols) > 4 else TODAY_STR,
                    "snippet": snippet[:250],
                    "url": link,
                    "fetched_at": datetime.now(timezone.utc).isoformat()
                }
                records.append(rec)
    print(f"    -> Extracted {len(records)} records in {elapsed:.2f}s")
    return records

def fetch_card_source(source_id: str, source_name: str, url: str, category: str, province: str, dims: list):
    print(f"[*] [Card] Fetching {source_name} ({url})...")
    t0 = time.time()
    resp = httpx.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"}, verify=False)
    soup = BeautifulSoup(resp.text, "html.parser")
    elapsed = time.time() - t0
    records = []
    cards = soup.find_all(["div", "article", "li"], class_=lambda c: c and any(k in str(c).lower() for k in ["news", "item", "post", "article", "tin"]))
    found = 0
    for card in cards:
        a = card.find("a", href=True)
        t = a.get_text(strip=True) if a else ""
        if len(t) > 15:
            link = a["href"]
            if not link.startswith("http"):
                link = "https://bacninh.gov.vn" + ("/" + link.lstrip("/"))
            date_tag = card.find(class_=lambda c: c and any(k in str(c).lower() for k in ["date", "time"]))
            date_str = date_tag.get_text(strip=True) if date_tag else ""
            desc = card.find(class_=lambda c: c and any(k in str(c).lower() for k in ["desc", "summary", "lead", "brief"]))
            snippet = desc.get_text(strip=True) if desc else t
            rec = {
                "fingerprint": compute_fingerprint(source_id, link, t),
                "source_id": source_id,
                "source_name": source_name,
                "category": category,
                "tier": "L1",
                "fetch_channel": "html_card",
                "province": province,
                "dimension_hints": dims,
                "title": t,
                "pub_date": date_str,
                "snippet": snippet[:250],
                "url": link,
                "fetched_at": datetime.now(timezone.utc).isoformat()
            }
            records.append(rec)
            found += 1
            if found >= 3:
                break
    print(f"    -> Extracted {len(records)} records in {elapsed:.2f}s")
    return records

def fetch_cdp_source(source_id: str, source_name: str, url: str, category: str, province: str, dims: list):
    print(f"[*] [Chrome CDP / Headless] Fetching dynamic SPA: {source_name} ({url})...")
    t0 = time.time()
    cmd = [
        CHROME_PATH,
        "--headless=new",
        "--disable-gpu",
        "--virtual-time-budget=5000",
        "--dump-dom",
        url
    ]
    res = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="ignore", timeout=25)
    soup = BeautifulSoup(res.stdout, "html.parser")
    elapsed = time.time() - t0
    records = []
    links = soup.find_all("a", href=True)
    seen_titles = set()
    for a in links:
        t = a.get_text(strip=True)
        if len(t) > 20 and t not in seen_titles:
            seen_titles.add(t)
            link = a["href"]
            if not link.startswith("http"):
                link = "https://nghison.thanhhoa.gov.vn" + ("/" + link.lstrip("/"))
            rec = {
                "fingerprint": compute_fingerprint(source_id, link, t),
                "source_id": source_id,
                "source_name": source_name,
                "category": category,
                "tier": "L1",
                "fetch_channel": "chrome_cdp",
                "province": province,
                "dimension_hints": dims,
                "title": t,
                "pub_date": TODAY_STR,
                "snippet": t,
                "url": link,
                "fetched_at": datetime.now(timezone.utc).isoformat()
            }
            records.append(rec)
            if len(records) >= 3:
                break
    print(f"    -> Extracted {len(records)} records in {elapsed:.2f}s")
    return records

def run_test_workflow():
    init_db(DB_PATH)
    all_records = []
    
    # 1. RSS: Báo Chính phủ
    try:
        recs = fetch_rss_source(
            source_id="src-A01",
            source_name="Báo Chính phủ (Government Portal)",
            url="https://baochinhphu.vn/kinh-te.rss",
            category="National Official",
            province="National",
            dims=["D01", "D07", "D11"]
        )
        all_records.extend(recs)
    except Exception as e:
        print(f"[!] RSS error: {e}")
        
    # 2. REST API: Bộ Tài chính
    try:
        recs = fetch_api_source(
            source_id="src-A02",
            source_name="Bộ Tài chính (Ministry of Finance)",
            url="https://mof.gov.vn/api/article/reads",
            category="National Official",
            province="National",
            dims=["D07", "D11"]
        )
        all_records.extend(recs)
    except Exception as e:
        print(f"[!] API error: {e}")
        
    # 3. HTML Table: Tham vấn ĐTM (EIA)
    try:
        recs = fetch_table_source(
            source_id="src-A09",
            source_name="Tham vấn ĐTM (EIA Public Consultation)",
            url="https://thamvan.mae.gov.vn/Home/DSDTM",
            category="National Official",
            province="National",
            dims=["D02"]
        )
        all_records.extend(recs)
    except Exception as e:
        print(f"[!] Table error: {e}")
        
    # 4. HTML Card: Cổng TTĐT tỉnh Bắc Ninh
    try:
        recs = fetch_card_source(
            source_id="VN-LOC-03-BN-A",
            source_name="Cổng TTĐT tỉnh Bắc Ninh",
            url="https://bacninh.gov.vn/tin-tuc-su-kien",
            category="Provincial Portal",
            province="Bac Ninh",
            dims=["D01", "D02", "D05"]
        )
        all_records.extend(recs)
    except Exception as e:
        print(f"[!] Card error: {e}")
        
    # 5. Chrome CDP / Headless for SPA: BQL KKT Nghi Sơn
    try:
        recs = fetch_cdp_source(
            source_id="VN-LOC-13-TH-B",
            source_name="BQL Khu kinh tế Nghi Sơn (Thanh Hóa)",
            url="https://nghison.thanhhoa.gov.vn",
            category="Provincial Zone Management",
            province="Thanh Hoa",
            dims=["D01", "D02"]
        )
        all_records.extend(recs)
    except Exception as e:
        print(f"[!] CDP error: {e}")

    # Persistence & deduplication
    print(f"\n[*] Total extracted candidate records: {len(all_records)}")
    new_count = 0
    for r in all_records:
        if save_record(r):
            new_count += 1
            
    print(f"[*] New records inserted (deduplicated): {new_count}")
        
    # Verify DB content
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT count(*), count(DISTINCT source_id), count(DISTINCT province), count(DISTINCT fetch_channel) FROM raw_materials;")
    row = cur.fetchone()
    print(f"[*] SQLite Database State: {row[0]} total rows, {row[1]} sources, {row[2]} provinces, {row[3]} channels.")
    
    # Query sample by channel
    cur.execute("SELECT fetch_channel, source_name, title, pub_date FROM raw_materials GROUP BY fetch_channel;")
    sample_rows = cur.fetchall()
    print("\n[*] Sample across 5 distinct channels in DB:")
    for sr in sample_rows:
        print(f"    - [{sr[0]}] {sr[1]} | {sr[3]} | {sr[2][:45]}...")
    conn.close()
    
    print(f"\n[*] JSON Lines path: {JSONL_PATH}")
    print(f"[*] SQLite DB path: {DB_PATH}")

if __name__ == "__main__":
    run_test_workflow()
