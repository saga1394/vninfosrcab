"""
V2/sources/drivers/pdf_probe.py
-------------------------------
公共增强器：公报 PDF 附件首页摘要探针 (补丁 2)。
针对外资局 FIA、统计总局 NSO、环评 DSDTM 等将核心数值封装于内嵌 PDF 附件的信源：
自动抓取 PDF 并抽取第一页摘要文本，注入 DriverRecord.summary / evidence_snippet。
兼容 pypdf / pymupdf (fitz) / pdfplumber。
"""

import io
import logging
import re
from typing import List, Optional

from sources.interfaces.contracts import NetworkConfig
from sources.drivers.base import DriverRecord, HttpFetcher, absolutize_url, clean_text

logger = logging.getLogger(__name__)


def extract_pdf_first_page_text(pdf_bytes: bytes, max_chars: int = 500) -> str:
    """尝试多种 PDF 解析器抽取首页文本，零异常降级。"""
    if not pdf_bytes:
        return ""

    # 1. pypdf
    try:
        import pypdf  # type: ignore
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        if reader.pages:
            txt = clean_text(reader.pages[0].extract_text() or "")
            if txt:
                return txt[:max_chars]
    except Exception:
        pass

    # 2. PyMuPDF (pymupdf / fitz)
    try:
        import pymupdf  # type: ignore
        doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
        if len(doc) > 0:
            txt = clean_text(doc[0].get_text() or "")
            if txt:
                return txt[:max_chars]
    except Exception:
        pass

    # 3. pdfplumber
    try:
        import pdfplumber  # type: ignore
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            if pdf.pages:
                txt = clean_text(pdf.pages[0].extract_text() or "")
                if txt:
                    return txt[:max_chars]
    except Exception:
        pass

    return ""


def _discover_pdf_in_detail_html(html_text: str, base_url: str) -> List[str]:
    matches = re.findall(r'href=["\']([^"\']+\.pdf(?:\?[^"\']*)?)["\']', html_text, re.IGNORECASE)
    urls = []
    for m in matches:
        abs_u = absolutize_url(base_url, m)
        if abs_u and abs_u not in urls:
            urls.append(abs_u)
    return urls


def probe_pdf_attachments(
    records: List[DriverRecord],
    network_config: NetworkConfig,
    fetcher: Optional[HttpFetcher] = None,
    max_pdfs: int = 5,
) -> List[DriverRecord]:
    """
    若记录已有 `.pdf` 附件链接或详情页内嵌 `.pdf` 链接，抽取首页核心摘要补充到 summary。
    """
    http = fetcher or HttpFetcher()
    probed = 0

    for rec in records:
        if probed >= max_pdfs:
            break

        if not rec.attachment_urls and rec.direct_url and not rec.direct_url.lower().endswith(".pdf"):
            try:
                detail_resp = http.request("GET", rec.direct_url, network_config)
                found_pdfs = _discover_pdf_in_detail_html(detail_resp.text, detail_resp.url or rec.direct_url)
                if found_pdfs:
                    rec.attachment_urls.extend(found_pdfs)
            except Exception as exc:
                logger.debug("Detail PDF discovery skipped for %s: %s", rec.direct_url, exc)

        pdf_targets = [u for u in rec.attachment_urls if ".pdf" in u.lower()]
        if not pdf_targets:
            continue

        try:
            pdf_resp = http.request("GET", pdf_targets[0], network_config)
            excerpt = extract_pdf_first_page_text(pdf_resp.content)
            if excerpt:
                prefix = f"{rec.summary} | " if rec.summary else ""
                rec.summary = f"{prefix}[PDF首页摘要] {excerpt}"[:500]
                rec.extra["pdf_probed"] = True
            probed += 1
        except Exception as exc:
            logger.debug("PDF probe failed for %s: %s", pdf_targets[0], exc)

    return records
