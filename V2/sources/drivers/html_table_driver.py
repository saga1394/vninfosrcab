"""
V2/sources/drivers/html_table_driver.py
---------------------------------------
底层驱动 3：规整 HTML / ASP.NET 数据表格解析器 (补丁 2 & 3)。
透传 network_config.verify_ssl=false，稳定解析 DSDTM/DSGiayPhep 等政务表格 `<tr>` 行与附件链接。
"""

from typing import Dict, List, Optional

try:
    from bs4 import BeautifulSoup  # type: ignore
except ImportError:  # pragma: no cover
    BeautifulSoup = None

from sources.interfaces.contracts import ParsedSourceCard
from sources.drivers.base import (
    BaseProtocolDriver,
    DriverRecord,
    HttpFetcher,
    SimpleTableParser,
    absolutize_url,
    clean_text,
    extract_date_from_text,
)


def _rows_to_records(rows: List[List[Dict[str, object]]], base_url: str, max_items: int) -> List[DriverRecord]:
    records: List[DriverRecord] = []
    seen_urls = set()

    for row in rows:
        if not row or all(cell.get("is_header") for cell in row):
            continue
        texts = [str(cell.get("text", "")).strip() for cell in row if str(cell.get("text", "")).strip()]
        if not texts:
            continue

        all_links: List[str] = []
        for cell in row:
            for href in cell.get("links", []):  # type: ignore[union-attr]
                abs_u = absolutize_url(base_url, str(href))
                if abs_u:
                    all_links.append(abs_u)

        attachments = [u for u in all_links if any(ext in u.lower() for ext in (".pdf", ".doc", ".docx"))]
        detail_links = [u for u in all_links if u not in attachments]
        direct_url = detail_links[0] if detail_links else (attachments[0] if attachments else "")
        if not direct_url or direct_url in seen_urls:
            continue
        seen_urls.add(direct_url)

        # Pick longest non-numeric column text as project/notice title
        candidate_titles = [t for t in texts if not t.isdigit() and len(t) >= 8]
        title = max(candidate_titles, key=len) if candidate_titles else " | ".join(texts[:2])
        joined_row = " | ".join(texts)
        pub_date = extract_date_from_text(joined_row)

        records.append(
            DriverRecord(
                title=clean_text(title),
                direct_url=direct_url,
                pub_date_raw=pub_date,
                summary=clean_text(joined_row)[:350],
                attachment_urls=attachments,
                extra={"columns": texts},
            )
        )
        if len(records) >= max_items:
            break
    return records


class HtmlTableDriver(BaseProtocolDriver):
    driver_name = "html_table_driver"

    def fetch(
        self,
        card: ParsedSourceCard,
        fetcher: Optional[HttpFetcher] = None,
        max_items: int = 25,
    ) -> List[DriverRecord]:
        http = fetcher or HttpFetcher()
        target_url = card.meta["target_url"]
        resp = http.request("GET", target_url, card.network_config)
        base_url = resp.url or target_url

        if BeautifulSoup is not None:
            soup = BeautifulSoup(resp.text, "html.parser")
            best_records: List[DriverRecord] = []
            for table in soup.find_all("table"):
                parsed_rows: List[List[Dict[str, object]]] = []
                for tr in table.find_all("tr"):
                    cells = tr.find_all(["td", "th"])
                    if not cells:
                        continue
                    row_data: List[Dict[str, object]] = []
                    for c in cells:
                        row_data.append({
                            "text": clean_text(c.get_text(" ", strip=True)),
                            "links": [a["href"] for a in c.find_all("a", href=True)],
                            "is_header": c.name == "th",
                        })
                    parsed_rows.append(row_data)
                recs = _rows_to_records(parsed_rows, base_url, max_items)
                if len(recs) > len(best_records):
                    best_records = recs
            return best_records

        parser = SimpleTableParser()
        parser.feed(resp.text)
        best_records = []
        for table_rows in parser.tables:
            recs = _rows_to_records(table_rows, base_url, max_items)
            if len(recs) > len(best_records):
                best_records = recs
        return best_records
