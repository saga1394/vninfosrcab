"""
V2/sources/drivers/sitemap_driver.py
------------------------------------
底层驱动 5：XML Sitemap 增量流解析器 (补丁 2)。
覆盖 VBPL（国家法律法规库 sitemap/1.xml）、The Investor（sitemap.xml）、Enterprise Singapore 等边缘源。
支持标准 `<urlset>` 与 `<sitemapindex>` 索引递归，按 `<lastmod>` 倒序筛选近 72h 增量。
"""

from datetime import datetime, timedelta, timezone
import re
from typing import List, Optional, Tuple
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

from sources.interfaces.contracts import ParsedSourceCard
from sources.drivers.base import (
    BaseProtocolDriver,
    DriverRecord,
    HttpFetcher,
    clean_text,
)


def _local_tag(tag: str) -> str:
    return tag.split("}", 1)[-1].lower() if "}" in tag else tag.lower()


def _parse_iso_dt(raw: str) -> Optional[datetime]:
    if not raw:
        return None
    s = raw.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        m = re.match(r"^(\d{4}-\d{2}-\d{2})", s)
        if m:
            try:
                return datetime.strptime(m.group(1), "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except ValueError:
                return None
    return None


def _slug_to_title(url: str) -> str:
    path = urlparse(url).path.rstrip("/")
    if not path:
        return url
    seg = path.rsplit("/", 1)[-1]
    seg = re.sub(r"\.(html?|aspx|php)$", "", seg, flags=re.IGNORECASE)
    seg = re.sub(r"--[0-9a-f-]{8,}$", "", seg, flags=re.IGNORECASE)
    seg = seg.replace("-", " ").replace("_", " ").strip()
    return clean_text(seg).title() if seg else url


def _extract_urlset_entries(xml_text: str) -> Tuple[List[str], List[Tuple[str, str, str]]]:
    """Returns (child_sitemaps, [(loc, lastmod, news_title)])."""
    root = ET.fromstring(xml_text)
    root_name = _local_tag(root.tag)
    child_sitemaps: List[str] = []
    url_rows: List[Tuple[str, str, str]] = []

    if root_name == "sitemapindex":
        for elem in root:
            if _local_tag(elem.tag) == "sitemap":
                loc = ""
                for child in elem:
                    if _local_tag(child.tag) == "loc":
                        loc = (child.text or "").strip()
                if loc:
                    child_sitemaps.append(loc)
        return child_sitemaps, url_rows

    for elem in root:
        if _local_tag(elem.tag) != "url":
            continue
        loc = ""
        lastmod = ""
        news_title = ""
        for child in elem:
            ctag = _local_tag(child.tag)
            if ctag == "loc":
                loc = (child.text or "").strip()
            elif ctag == "lastmod":
                lastmod = (child.text or "").strip()
            elif ctag == "news":
                for sub in child.iter():
                    if _local_tag(sub.tag) == "title" and sub.text:
                        news_title = clean_text(sub.text)
                        break
        if loc:
            url_rows.append((loc, lastmod, news_title))
    return child_sitemaps, url_rows


class SitemapDriver(BaseProtocolDriver):
    driver_name = "sitemap_driver"

    def fetch(
        self,
        card: ParsedSourceCard,
        fetcher: Optional[HttpFetcher] = None,
        max_items: int = 30,
        fresh_hours: Optional[int] = 72,
        reference_now: Optional[datetime] = None,
    ) -> List[DriverRecord]:
        http = fetcher or HttpFetcher()
        target_url = card.meta["target_url"]
        resp = http.request("GET", target_url, card.network_config)

        child_sitemaps, url_rows = _extract_urlset_entries(resp.text)
        if not url_rows and child_sitemaps:
            # Fetch up to first 2 child sitemaps
            for child_url in child_sitemaps[:2]:
                child_resp = http.request("GET", child_url, card.network_config)
                _, sub_rows = _extract_urlset_entries(child_resp.text)
                url_rows.extend(sub_rows)

        # Sort descending by lastmod when present
        def _sort_key(row: Tuple[str, str, str]):
            dt = _parse_iso_dt(row[1])
            return dt.timestamp() if dt else 0.0

        url_rows.sort(key=_sort_key, reverse=True)

        now_utc = reference_now or datetime.now(timezone.utc)
        cutoff = now_utc - timedelta(hours=fresh_hours) if fresh_hours is not None else None

        filtered_rows = url_rows
        if cutoff is not None:
            fresh_only = []
            for loc, lastmod, news_title in url_rows:
                dt = _parse_iso_dt(lastmod)
                if dt is None or dt >= cutoff:
                    fresh_only.append((loc, lastmod, news_title))
            if fresh_only:
                filtered_rows = fresh_only

        records: List[DriverRecord] = []
        for loc, lastmod, news_title in filtered_rows[:max_items]:
            title = news_title or _slug_to_title(loc)
            records.append(
                DriverRecord(
                    title=title,
                    direct_url=loc,
                    pub_date_raw=lastmod,
                    summary=f"Sitemap incremental entry ({lastmod or 'date_unverified'}): {title}",
                )
            )
        return records
