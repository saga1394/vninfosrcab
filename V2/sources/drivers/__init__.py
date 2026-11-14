"""V2 Layer 1: Stateless Protocol Drivers Registry."""

from typing import Dict
from .base import (
    BaseProtocolDriver,
    DriverRecord,
    HostThrottle,
    HttpFetcher,
    HttpResponseData,
)
from .rss_driver import RssDriver
from .html_card_driver import HtmlCardDriver
from .html_table_driver import HtmlTableDriver
from .rest_api_driver import RestApiDriver
from .sitemap_driver import SitemapDriver
from .pdf_probe import probe_pdf_attachments, extract_pdf_first_page_text

DRIVER_REGISTRY: Dict[str, BaseProtocolDriver] = {
    "rss_driver": RssDriver(),
    "html_card_driver": HtmlCardDriver(),
    "html_table_driver": HtmlTableDriver(),
    "rest_api_driver": RestApiDriver(),
    "sitemap_driver": SitemapDriver(),
}


def get_protocol_driver(driver_name: str) -> BaseProtocolDriver:
    if driver_name not in DRIVER_REGISTRY:
        raise KeyError(f"未注册的底层协议驱动: {driver_name}")
    return DRIVER_REGISTRY[driver_name]


__all__ = [
    "BaseProtocolDriver",
    "DriverRecord",
    "HostThrottle",
    "HttpFetcher",
    "HttpResponseData",
    "RssDriver",
    "HtmlCardDriver",
    "HtmlTableDriver",
    "RestApiDriver",
    "SitemapDriver",
    "DRIVER_REGISTRY",
    "get_protocol_driver",
    "probe_pdf_attachments",
    "extract_pdf_first_page_text",
]
