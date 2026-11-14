"""
V2/sources/drivers/html_card_driver.py
--------------------------------------
底层驱动 2：规整图文卡片 & Next.js `__NEXT_DATA__` 抽取器 (补丁 2 & 3)。
特性：
1. 支持 `search_spec.endpoint_template` + `keywords` 参数化遍历请求（消除“在搜索框输入”伪指令）；
2. 优先提取 Next.js `<script id="__NEXT_DATA__">` 预渲染 JSON 职位/文章数组；
3. 自动剥离 nav/header/footer/aside 导航菜单并过滤停用词，提取语义卡片、日期与 PDF 附件链接。
"""

import json
import re
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus

try:
    from bs4 import BeautifulSoup  # type: ignore
except ImportError:  # pragma: no cover
    BeautifulSoup = None

from sources.interfaces.contracts import NetworkConfig, ParsedSourceCard
from sources.drivers.base import (
    BaseProtocolDriver,
    DriverRecord,
    HttpFetcher,
    SimpleLinkParser,
    absolutize_url,
    clean_text,
    extract_date_from_text,
    is_noise_nav_text,
    strip_html_tags,
)


def _walk_json_for_items(node: Any, depth: int = 0) -> List[Dict[str, Any]]:
    """Recursively find lists of dicts that look like job/article objects inside __NEXT_DATA__."""
    if depth > 8:
        return []
    found: List[Dict[str, Any]] = []
    if isinstance(node, list):
        if node and all(isinstance(x, dict) for x in node):
            sample = node[0]
            title_keys = {"jobTitle", "title", "name", "headline", "post_title"}
            url_keys = {"jobUrl", "url", "slug", "link", "href", "alias"}
            if any(k in sample for k in title_keys) and any(k in sample for k in url_keys):
                return node
        for item in node:
            found.extend(_walk_json_for_items(item, depth + 1))
    elif isinstance(node, dict):
        # Fast-path common Next.js paths
        for priority_key in ("jobs", "articles", "posts", "items", "data", "results"):
            if priority_key in node:
                res = _walk_json_for_items(node[priority_key], depth + 1)
                if res:
                    return res
        for val in node.values():
            res = _walk_json_for_items(val, depth + 1)
            if res:
                return res
    return found


def _extract_from_next_data(json_text: str, base_url: str, max_items: int) -> List[DriverRecord]:
    try:
        payload = json.loads(json_text)
    except json.JSONDecodeError:
        return []

    raw_items = _walk_json_for_items(payload)
    records: List[DriverRecord] = []
    for obj in raw_items[:max_items]:
        title = clean_text(
            str(
                obj.get("jobTitle")
                or obj.get("title")
                or obj.get("headline")
                or obj.get("name")
                or ""
            )
        )
        raw_url = str(
            obj.get("jobUrl")
            or obj.get("url")
            or obj.get("link")
            or obj.get("href")
            or obj.get("slug")
            or ""
        ).strip()
        if raw_url and not raw_url.startswith(("http://", "https://", "/")):
            raw_url = f"/{raw_url}"
        direct_url = absolutize_url(base_url, raw_url)
        if not title or not direct_url:
            continue

        pub_date = clean_text(
            str(
                obj.get("publishedOn")
                or obj.get("publishedAt")
                or obj.get("createdAt")
                or obj.get("date")
                or ""
            )
        )
        company = clean_text(str(obj.get("companyName") or obj.get("company") or ""))
        location = clean_text(str(obj.get("workLocation") or obj.get("location") or ""))
        if not location and isinstance(obj.get("workingLocations"), list):
            loc_parts = []
            for wl in obj["workingLocations"]:
                if isinstance(wl, dict):
                    part = wl.get("cityNameVI") or wl.get("cityName") or wl.get("address") or ""
                    if part and str(part) not in loc_parts:
                        loc_parts.append(str(part))
            location = clean_text(", ".join(loc_parts))
        desc = strip_html_tags(str(obj.get("summary") or obj.get("description") or obj.get("jobDescription") or ""))
        if not desc:
            parts = [p for p in (company, location) if p]
            desc = " | ".join(parts)

        records.append(
            DriverRecord(
                title=title,
                direct_url=direct_url,
                pub_date_raw=extract_date_from_text(pub_date) or pub_date,
                summary=desc[:350],
                extra={
                    "company": company,
                    "location": location,
                    "from_next_data": True,
                },
            )
        )
    return records


_HIGH_VALUE_DATE_PROBE_RE = re.compile(
    r"(?:\bfdi\b|\bkcn\b|\bkhu công nghiệp\b|\bkhu kinh tế\b|\bcụm công nghiệp\b|"
    r"\bnhà máy\b|\bđầu tư\b|\btriệu usd\b|\btỷ usd\b|\bkhởi công\b|\bđộng thổ\b|"
    r"\bvận hành\b|\bthuê đất\b|\bgiao đất\b|\bgiải phóng mặt bằng\b|\bbot\b|"
    r"\bnhiệt điện\b|\bbán dẫn\b|\bsemiconductor\b|\bfactory\b|\bplant\b|"
    r"\bindustrial park\b|\bcấp phép\b|\bchủ trương đầu tư\b|\bmở rộng\b|\btăng vốn\b)",
    re.IGNORECASE,
)


def _find_card_headline_and_href(card: Any, base_url: str) -> tuple[str, str]:
    """Extract substantive headline text and URL from a card container, skipping empty thumbnail links."""
    h_tag = card.find(["h1", "h2", "h3", "h4", "h5", "h6"])
    title_a = h_tag.find("a", href=True) if h_tag else None
    if not title_a:
        for a in card.find_all("a", href=True):
            t = clean_text(a.get_text(" ", strip=True))
            if len(t) >= 12 and not is_noise_nav_text(t):
                title_a = a
                break
    if not title_a:
        for a in card.find_all("a", href=True):
            t = clean_text(a.get_text(" ", strip=True))
            if t and not is_noise_nav_text(t):
                title_a = a
                break
    if not title_a:
        return "", ""
    h_text = clean_text(h_tag.get_text(" ", strip=True)) if h_tag else ""
    a_text = clean_text(title_a.get_text(" ", strip=True))
    title = h_text if len(h_text) >= 12 else (a_text or h_text)
    href = absolutize_url(base_url, title_a["href"])
    return title, href


def _extract_ancestor_date(tag: Any) -> tuple[str, str]:
    """Walk up to 3 enclosing blocks (bounded size/link count) to capture sibling date tags."""
    cur = tag.parent
    best_text = ""
    for _ in range(3):
        if not cur or getattr(cur, "name", "") in ("body", "html", "main"):
            break
        txt = clean_text(cur.get_text(" ", strip=True))
        if len(txt) > 900:
            break
        link_cnt = sum(
            1 for x in cur.find_all("a", href=True) if len(clean_text(x.get_text(" ", strip=True))) >= 15
        )
        if link_cnt > 4:
            break
        if not best_text:
            best_text = txt
        d = extract_date_from_text(txt)
        if d:
            return d, txt
        cur = cur.parent
    return "", best_text


def _probe_detail_date(url: str, base_cfg: NetworkConfig, http: HttpFetcher) -> str:
    """Lightweight detail-page date sniffer for undated P0/P1 industrial cards."""
    try:
        probe_cfg = NetworkConfig(
            verify_ssl=base_cfg.verify_ssl,
            timeout=min(base_cfg.timeout, 6),
            headers=base_cfg.headers,
            use_curl=base_cfg.use_curl,
        )
        resp = http.request("GET", url, probe_cfg)
        html = resp.text or ""
        if BeautifulSoup is not None:
            soup = BeautifulSoup(html, "html.parser")
            for meta in soup.find_all("meta"):
                key = str(meta.get("property") or meta.get("name") or "").lower()
                if any(k in key for k in ("published_time", "pubdate", "publishdate", "date")):
                    d = extract_date_from_text(str(meta.get("content") or ""))
                    if d:
                        return d
            for t in soup.find_all("time"):
                d = extract_date_from_text(str(t.get("datetime") or "") or t.get_text(" ", strip=True))
                if d:
                    return d
        m = re.search(r"\b\d{1,2}/\d{1,2}/202[56]\b", html)
        if m:
            d = extract_date_from_text(m.group(0))
            if d:
                return d
        m_iso = re.search(r"\b202[56]-\d{2}-\d{2}\b", html[:25000])
        if m_iso:
            return m_iso.group(0)
    except Exception:
        return ""
    return ""


def _extract_cards_html(html_text: str, base_url: str, max_items: int) -> List[DriverRecord]:
    # 1. Check __NEXT_DATA__ first
    m_next = re.search(
        r'<script[^>]*id=["\']__NEXT_DATA__["\'][^>]*>(.*?)</script>',
        html_text,
        re.IGNORECASE | re.DOTALL,
    )
    if m_next:
        next_records = _extract_from_next_data(m_next.group(1), base_url, max_items)
        if next_records:
            return next_records

    records: List[DriverRecord] = []
    seen_urls = set()

    if BeautifulSoup is not None:
        soup = BeautifulSoup(html_text, "html.parser")
        for tag in soup.find_all(["nav", "header", "footer", "aside", "script", "style"]):
            tag.decompose()

        # Look for semantic card containers first
        card_nodes = soup.select(
            "article, .news-item, .post-item, .card, .item-news, .list-item, "
            ".article-news, .article-item, .story, .news_focus, .list_news_home, .box-news-item"
        )
        if card_nodes:
            for card in card_nodes:
                title, href = _find_card_headline_and_href(card, base_url)
                if not title or not href or href in seen_urls or is_noise_nav_text(title):
                    continue
                seen_urls.add(href)

                card_text = clean_text(card.get_text(" ", strip=True))
                date_str = extract_date_from_text(card_text)
                if not date_str:
                    time_tag = card.find("time")
                    if time_tag and time_tag.get("datetime"):
                        date_str = extract_date_from_text(str(time_tag.get("datetime")))
                if not date_str:
                    date_str, _ = _extract_ancestor_date(card)

                p_tag = card.find("p")
                summary = clean_text(p_tag.get_text(" ", strip=True)) if p_tag else card_text[:280]
                pdfs = [
                    absolutize_url(base_url, a["href"])
                    for a in card.find_all("a", href=True)
                    if ".pdf" in a["href"].lower()
                ]
                records.append(
                    DriverRecord(
                        title=title,
                        direct_url=href,
                        pub_date_raw=date_str,
                        summary=summary[:350],
                        attachment_urls=pdfs,
                    )
                )
                if len(records) >= max_items:
                    return records

        # Fallback: substantive <a> links outside nav
        for a_tag in soup.find_all("a", href=True):
            title = clean_text(a_tag.get_text(" ", strip=True))
            href = absolutize_url(base_url, a_tag["href"])
            if not href or href in seen_urls or is_noise_nav_text(title) or len(title) < 18:
                continue
            seen_urls.add(href)
            date_str, parent_text = _extract_ancestor_date(a_tag)
            records.append(
                DriverRecord(
                    title=title,
                    direct_url=href,
                    pub_date_raw=date_str or extract_date_from_text(href),
                    summary=parent_text[:300],
                )
            )
            if len(records) >= max_items:
                break
        return records

    # Stdlib fallback when BeautifulSoup is unavailable
    parser = SimpleLinkParser()
    parser.feed(html_text)
    if parser.next_data_json:
        next_records = _extract_from_next_data(parser.next_data_json, base_url, max_items)
        if next_records:
            return next_records

    for title, raw_href in parser.links:
        href = absolutize_url(base_url, raw_href)
        if not href or href in seen_urls or is_noise_nav_text(title) or len(title) < 18:
            continue
        seen_urls.add(href)
        records.append(
            DriverRecord(
                title=title,
                direct_url=href,
                pub_date_raw=extract_date_from_text(href),
                summary="",
            )
        )
        if len(records) >= max_items:
            break
    return records


class HtmlCardDriver(BaseProtocolDriver):
    driver_name = "html_card_driver"

    def fetch(
        self,
        card: ParsedSourceCard,
        fetcher: Optional[HttpFetcher] = None,
        max_items: int = 25,
    ) -> List[DriverRecord]:
        http = fetcher or HttpFetcher()
        urls_to_fetch: List[str] = []

        if card.search_spec and card.search_spec.endpoint_template and card.search_spec.keywords:
            for kw in card.search_spec.keywords:
                encoded = quote_plus(kw)
                urls_to_fetch.append(card.search_spec.endpoint_template.format(keyword=encoded))
        else:
            urls_to_fetch.append(card.meta["target_url"])

        all_records: List[DriverRecord] = []
        seen_urls = set()

        for url in urls_to_fetch:
            resp = http.request("GET", url, card.network_config)
            batch = _extract_cards_html(resp.text, resp.url or url, max_items=max_items)
            for rec in batch:
                if rec.direct_url not in seen_urls:
                    seen_urls.add(rec.direct_url)
                    all_records.append(rec)
            if len(all_records) >= max_items:
                break

        # Targeted detail-page date sniffer for high-priority / heavy-asset cards
        prio = str(card.meta.get("priority", "P2")).upper()
        cluster = str(card.meta.get("cluster", ""))
        is_heavy_asset = prio in ("P0", "P1") or cluster in (
            "industrial_park", "job_radar", "corporate_disclosure", "legal_approval"
        )
        if is_heavy_asset:
            probed_count = 0
            for rec in all_records:
                if not rec.pub_date_raw or rec.pub_date_raw == "date_unverified":
                    combined = f"{rec.title} {rec.summary}".lower()
                    if _HIGH_VALUE_DATE_PROBE_RE.search(combined):
                        sniffed = _probe_detail_date(rec.direct_url, card.network_config, http)
                        if sniffed:
                            rec.pub_date_raw = sniffed
                        probed_count += 1
                        if probed_count >= 8:
                            break

        return all_records[:max_items]
