"""
V2/sources/drivers/rest_api_driver.py
-------------------------------------
底层驱动 4：HTTP GET/POST REST API / SPA 后端接口 / 静态 JS 数据数组抽取器 (补丁 2 & 3)。
支持 JSON Body、Form-UrlEncoded Body、深层路径、JSON 字符串字段（如港交所 result）、
自定义标题/URL 模板（如 CNINFO/SZSE/MOF/DSEZA）及静态 JS 数组（如 AIIB）。
"""

from datetime import datetime, timedelta, timezone
import json
import re
from typing import Any, Dict, List, Optional

from sources.interfaces.contracts import ApiSpec, ParsedSourceCard
from sources.drivers.base import (
    BaseProtocolDriver,
    DriverRecord,
    HttpFetcher,
    absolutize_url,
    clean_text,
    extract_date_from_text,
    strip_html_tags,
)


class _SafeFormatDict(dict):
    def __missing__(self, key: str) -> str:
        return ""


def _resolve_json_path(data: Any, json_path: str) -> Any:
    if not json_path:
        return data
    curr = data
    for seg in json_path.split("."):
        if isinstance(curr, dict) and seg in curr:
            curr = curr[seg]
        elif isinstance(curr, list) and seg.isdigit():
            idx = int(seg)
            curr = curr[idx] if 0 <= idx < len(curr) else None
        else:
            return None
    return curr


def _extract_js_array(text: str) -> Optional[List[Dict[str, Any]]]:
    """Extract JSON array assigned to a JS variable, tolerating trailing commas."""
    m = re.search(r"(?:var|let|const)\s+[A-Za-z0-9_]+\s*=\s*(\[.*)", text, re.DOTALL)
    if not m:
        return None
    tail = m.group(1)
    ridx = tail.rfind("]")
    if ridx == -1:
        return None
    raw = re.sub(r",\s*(\]|\})", r"\1", tail[: ridx + 1])
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return [x for x in parsed if isinstance(x, dict)]
    except json.JSONDecodeError:
        return None
    return None


def _resolve_dynamic_tokens(payload: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if payload is None:
        return None
    now = datetime.now(timezone.utc)
    tokens = {
        "{today_yyyymmdd}": now.strftime("%Y%m%d"),
        "{ago_30d_yyyymmdd}": (now - timedelta(days=30)).strftime("%Y%m%d"),
        "{today_iso}": now.strftime("%Y-%m-%d"),
        "{ago_30d_iso}": (now - timedelta(days=30)).strftime("%Y-%m-%d"),
    }

    def _sub(val: Any) -> Any:
        if isinstance(val, str):
            out = val
            for k, v in tokens.items():
                out = out.replace(k, v)
            return out
        if isinstance(val, list):
            return [_sub(x) for x in val]
        if isinstance(val, dict):
            return {k: _sub(v) for k, v in val.items()}
        return val

    return _sub(payload)


def _coerce_items_list(payload: Any, json_path: str, nested_json_field: str = "") -> List[Dict[str, Any]]:
    target = _resolve_json_path(payload, json_path)
    if nested_json_field and isinstance(target, dict):
        sub_raw = target.get(nested_json_field)
        if isinstance(sub_raw, str):
            try:
                target = json.loads(sub_raw)
            except json.JSONDecodeError:
                target = None
        else:
            target = sub_raw
    elif isinstance(target, str):
        try:
            target = json.loads(target)
        except json.JSONDecodeError:
            target = None

    if isinstance(target, list):
        return [x for x in target if isinstance(x, dict)]
    if isinstance(target, dict):
        for key in ("items", "data", "results", "records", "list", "articles", "announcements", "hits"):
            sub = target.get(key)
            if isinstance(sub, list):
                return [x for x in sub if isinstance(x, dict)]
            if isinstance(sub, dict) and isinstance(sub.get("hits"), list):
                return [x for x in sub["hits"] if isinstance(x, dict)]
    return []


def _flatten_obj(obj: Dict[str, Any]) -> Dict[str, Any]:
    """Flatten common nested structures (like SEC EDGAR `_source`) for template formatting."""
    flat = dict(obj)
    src = obj.get("_source")
    if isinstance(src, dict):
        for k, v in src.items():
            if isinstance(v, list):
                flat[k] = str(v[0]) if v else ""
            else:
                flat[k] = v
    for k, v in list(flat.items()):
        if isinstance(v, list):
            flat[f"{k}_0"] = str(v[0]) if v else ""
    return flat


def _coerce_date(val: Any) -> str:
    if val is None or val == "":
        return ""
    if isinstance(val, (int, float)) and val > 10_000_000_000:
        return datetime.fromtimestamp(val / 1000.0, tz=timezone.utc).strftime("%Y-%m-%d")
    s = clean_text(str(val))
    return extract_date_from_text(s) or s


class RestApiDriver(BaseProtocolDriver):
    driver_name = "rest_api_driver"

    def fetch(
        self,
        card: ParsedSourceCard,
        fetcher: Optional[HttpFetcher] = None,
        max_items: int = 30,
    ) -> List[DriverRecord]:
        http = fetcher or HttpFetcher()
        target_url = card.meta["target_url"]
        spec = card.api_spec or ApiSpec()

        method = (spec.method or "GET").upper()
        resolved_payload = _resolve_dynamic_tokens(spec.payload_template)
        json_body = None
        form_body = None
        params = None
        if method in ("POST", "PUT", "PATCH"):
            if spec.content_type == "form":
                form_body = resolved_payload
            else:
                json_body = resolved_payload
        elif method == "GET" and resolved_payload:
            params = resolved_payload

        resp = http.request(
            method=method,
            url=target_url,
            network_config=card.network_config,
            headers=spec.headers,
            json_body=json_body,
            form_body=form_body,
            params=params,
        )

        items: List[Dict[str, Any]] = []
        try:
            parsed = json.loads(resp.text)
            items = _coerce_items_list(parsed, spec.json_path, spec.nested_json_field)
        except json.JSONDecodeError:
            js_arr = _extract_js_array(resp.text)
            if js_arr is not None:
                items = js_arr

        if spec.filter_field and spec.filter_contains:
            needle = spec.filter_contains.lower()
            items = [it for it in items if needle in str(it.get(spec.filter_field, "")).lower()]

        records: List[DriverRecord] = []
        for raw_obj in items[:max_items]:
            obj = _flatten_obj(raw_obj)
            if spec.title_template:
                title = clean_text(spec.title_template.format_map(_SafeFormatDict(obj)))
            else:
                title = clean_text(
                    str(
                        obj.get("title")
                        or obj.get("TITLE")
                        or obj.get("name")
                        or obj.get("headline")
                        or obj.get("projectName")
                        or obj.get("announcementTitle")
                        or ""
                    )
                )

            raw_url = ""
            if spec.detail_url_template:
                raw_url = spec.detail_url_template.format_map(_SafeFormatDict(obj)).strip()
            else:
                raw_url = str(
                    obj.get("url")
                    or obj.get("link")
                    or obj.get("detailUrl")
                    or obj.get("adjunctUrl")
                    or obj.get("FILE_LINK")
                    or obj.get("path")
                    or (f"/{obj['slug']}" if obj.get("slug") else "")
                ).strip()

            if raw_url and not raw_url.startswith(("http://", "https://", "/")):
                raw_url = f"/{raw_url}"
            direct_url = absolutize_url(target_url, raw_url)
            if not title or not direct_url:
                continue

            if spec.date_field and spec.date_field in obj:
                pub_date = _coerce_date(obj.get(spec.date_field))
            else:
                pub_date = _coerce_date(
                    obj.get("publicationTime")
                    or obj.get("publishedAt")
                    or obj.get("publishDate")
                    or obj.get("publishTime")
                    or obj.get("announcementTime")
                    or obj.get("DATE_TIME")
                    or obj.get("file_date")
                    or obj.get("createdAt")
                    or obj.get("created_at")
                    or obj.get("createTime")
                    or obj.get("date")
                    or ""
                )

            summary = strip_html_tags(
                str(
                    obj.get("summary")
                    or obj.get("description")
                    or obj.get("sapo")
                    or obj.get("abstract")
                    or obj.get("body")
                    or obj.get("secName")
                    or obj.get("STOCK_NAME")
                    or obj.get("display_names")
                    or ""
                )
            )[:350]
            if not pub_date and summary:
                pub_date = extract_date_from_text(summary) or ""

            attachments: List[str] = []
            att = obj.get("attachmentUrl") or obj.get("pdfUrl") or obj.get("adjunctUrl") or ""
            if isinstance(att, str) and att.strip().lower().endswith(".pdf"):
                attachments.append(absolutize_url(target_url, att.strip()))
            if direct_url.lower().endswith(".pdf") and direct_url not in attachments:
                attachments.append(direct_url)

            records.append(
                DriverRecord(
                    title=title,
                    direct_url=direct_url,
                    pub_date_raw=pub_date,
                    summary=summary,
                    attachment_urls=attachments,
                    extra={"raw_keys": list(obj.keys())[:10]},
                )
            )

        return records
