"""
V2/sources/drivers/rss_driver.py
--------------------------------
底层驱动 1：原生 RSS / Atom 极速流解析器 (零 Token 消耗)。
优先使用 feedparser，无第三方库时自动降级至 stdlib xml.etree.ElementTree。
"""

from typing import List, Optional
import xml.etree.ElementTree as ET

try:
    import feedparser  # type: ignore
except ImportError:  # pragma: no cover
    feedparser = None

from sources.interfaces.contracts import ParsedSourceCard
from sources.drivers.base import (
    BaseProtocolDriver,
    DriverRecord,
    HttpFetcher,
    absolutize_url,
    clean_text,
    strip_html_tags,
)


def _local_tag(tag: str) -> str:
    return tag.split("}", 1)[-1].lower() if "}" in tag else tag.lower()


def _parse_rss_stdlib(xml_text: str, base_url: str, max_items: int) -> List[DriverRecord]:
    root = ET.fromstring(xml_text)
    records: List[DriverRecord] = []

    for elem in root.iter():
        tag = _local_tag(elem.tag)
        if tag not in ("item", "entry"):
            continue
        title = ""
        link = ""
        pub_date = ""
        summary = ""
        attachments: List[str] = []

        for child in elem:
            ctag = _local_tag(child.tag)
            ctext = (child.text or "").strip()
            if ctag == "title" and not title:
                title = clean_text(ctext)
            elif ctag == "link":
                href = child.attrib.get("href", "").strip()
                candidate_url = href or ctext
                if candidate_url and not link:
                    link = absolutize_url(base_url, candidate_url)
            elif ctag in ("pubdate", "published", "updated", "date") and not pub_date:
                pub_date = clean_text(ctext)
            elif ctag in ("description", "summary", "content") and not summary:
                summary = strip_html_tags(ctext)[:350]
            elif ctag == "enclosure":
                enc_url = child.attrib.get("url", "").strip()
                if enc_url.lower().endswith(".pdf"):
                    attachments.append(absolutize_url(base_url, enc_url))

        if title and link:
            records.append(
                DriverRecord(
                    title=title,
                    direct_url=link,
                    pub_date_raw=pub_date,
                    summary=summary,
                    attachment_urls=attachments,
                )
            )
            if len(records) >= max_items:
                break
    return records


class RssDriver(BaseProtocolDriver):
    driver_name = "rss_driver"

    def fetch(
        self,
        card: ParsedSourceCard,
        fetcher: Optional[HttpFetcher] = None,
        max_items: int = 30,
    ) -> List[DriverRecord]:
        http = fetcher or HttpFetcher()
        target_url = card.meta["target_url"]
        resp = http.request("GET", target_url, card.network_config)

        if feedparser is not None:
            feed = feedparser.parse(resp.text)
            if getattr(feed, "entries", None):
                records: List[DriverRecord] = []
                for entry in feed.entries[:max_items]:
                    title = clean_text(entry.get("title", ""))
                    link = absolutize_url(target_url, entry.get("link", ""))
                    if not title or not link:
                        continue
                    pub_date = clean_text(
                        entry.get("published", "") or entry.get("updated", "")
                    )
                    summary_raw = entry.get("summary", "") or entry.get("description", "")
                    summary = strip_html_tags(summary_raw)[:350]
                    attachments: List[str] = []
                    for enc in entry.get("enclosures", []) or []:
                        enc_url = enc.get("href") or enc.get("url") or ""
                        if enc_url.lower().endswith(".pdf"):
                            attachments.append(absolutize_url(target_url, enc_url))
                    records.append(
                        DriverRecord(
                            title=title,
                            direct_url=link,
                            pub_date_raw=pub_date,
                            summary=summary,
                            attachment_urls=attachments,
                        )
                    )
                if records:
                    return records

        return _parse_rss_stdlib(resp.text, target_url, max_items=max_items)
