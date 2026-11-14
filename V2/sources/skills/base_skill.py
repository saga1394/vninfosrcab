"""
V2/sources/skills/base_skill.py
-------------------------------
V2 上层业务原型认知技能基类 (补丁 2 & 4)：
1. 通过 `get_protocol_driver(card.meta["protocol_driver"])` 委托底层驱动拉取原始记录；
2. 若 `card.attachment_probe` 为 True，自动执行 `probe_pdf_attachments` 抽取 PDF 首页摘要；
3. 调用子类 `interpret(card, records)` 完成业务语义判定、噪音剔除与 `RawExtractedItem` 构造；
4. 自动将运行健康结果回写至 `SourceHealthLedger` (SQLite)。
"""

from abc import ABC, abstractmethod
import logging
import re
from typing import List, Optional

from sources.drivers import (
    DriverRecord,
    HttpFetcher,
    get_protocol_driver,
    probe_pdf_attachments,
)
from sources.interfaces.contracts import ParsedSourceCard, RawExtractedItem, SignalType
from sources.interfaces.health_ledger import SourceHealthLedger

logger = logging.getLogger(__name__)

GEO_PATTERNS = [
    ("Bắc Ninh (北宁省)", ("bắc ninh", "bac ninh", "vsip bac ninh", "yên phong", "yen phong", "quế võ", "gia bình")),
    ("Hải Phòng (海防市)", ("hải phòng", "hai phong", "deep c", "đình vũ", "tràng duệ", "nam cầu kiền")),
    ("Bình Dương (平阳省)", ("bình dương", "binh duong", "becamex", "bàu bàng", "bau bang", "mỹ phước")),
    ("Đồng Nai (同奈省)", ("đồng nai", "dong nai", "long thành", "amata", "nhơn trạch", "biên hòa")),
    ("TP. Hồ Chí Minh (胡志明市)", ("hồ chí minh", "ho chi minh", "tp.hcm", "tphcm", "hiệp phước")),
    ("Hà Nội (河内市)", ("hà nội", "ha noi", "hanoi", "hòa lạc", "hoa lac")),
    ("Thái Nguyên (太原省)", ("thái nguyên", "thai nguyen", "yên bình", "sông công", "điềm thụy")),
    ("Quảng Ninh (广宁省)", ("quảng ninh", "quang ninh", "hạ long", "sông khoai", "đông mai")),
    ("Long An (隆安省)", ("long an", "long hậu", "đức hòa", "bến lức")),
    ("Hưng Yên (兴安省)", ("hưng yên", "hung yen", "thăng long ii")),
    ("Nghệ An (义安省)", ("nghệ an", "nghe an", "waha", "vsip nghe an", "hoàng mai")),
    ("Đà Nẵng (岘港市)", ("đà nẵng", "da nang", "hòa khánh", "liên chiểu")),
]


def detect_geo_location(text: str, default_geo: str = "Vietnam (全国/待定位)") -> str:
    low = (text or "").lower()
    for label, patterns in GEO_PATTERNS:
        if any(p in low for p in patterns):
            return label
    return default_geo


def detect_project_scale(text: str) -> Optional[str]:
    if not text:
        return None
    matches: List[str] = []
    # USD / triệu USD / tỷ USD
    m_usd = re.search(
        r"(\d+(?:[.,]\d+)?\s*(?:million|billion|triệu|tỷ|tỉ)?\s*(?:USD|usd|\$|亿美元|万美元))",
        text,
        re.IGNORECASE,
    )
    if m_usd:
        matches.append(m_usd.group(1).strip())
    # ha / m2 / sqm / MW / GW
    m_area = re.search(
        r"(\d+(?:[.,]\d+)?\s*(?:ha|hecta|hectares|m2|sqm|m²|MW|GW|公顷))",
        text,
        re.IGNORECASE,
    )
    if m_area:
        matches.append(m_area.group(1).strip())
    return ", ".join(matches) if matches else None


class BaseArchetypeSkill(ABC):
    skill_name: str = ""
    default_signal_type: SignalType = "policy_regulation"
    noise_keywords: tuple = ()

    def execute(
        self,
        card: ParsedSourceCard,
        fetcher: Optional[HttpFetcher] = None,
        ledger: Optional[SourceHealthLedger] = None,
        fail_on_empty: bool = False,
    ) -> List[RawExtractedItem]:
        source_id = card.meta["source_id"]
        driver_name = card.meta["protocol_driver"]
        driver = get_protocol_driver(driver_name)
        http = fetcher or HttpFetcher()

        try:
            records = driver.fetch(card, fetcher=http)
            if fail_on_empty and not records:
                raise RuntimeError(f"{driver_name} 返回空列表（疑似页面改版或风控拦截）")

            if card.attachment_probe and records:
                records = probe_pdf_attachments(records, card.network_config, fetcher=http)

            items = self.interpret(card, records)
            if ledger is not None:
                ledger.record_success(source_id)
            return items
        except Exception as exc:
            logger.warning("[%s] 信源 %s 执行异常: %s", self.skill_name, source_id, exc)
            if ledger is not None:
                ledger.record_failure(source_id, str(exc))
            raise

    def should_discard(self, card: ParsedSourceCard, rec: DriverRecord) -> bool:
        blob = f"{rec.title} {rec.summary}".lower()
        return any(kw in blob for kw in self.noise_keywords)

    def classify_signal(self, rec: DriverRecord) -> SignalType:
        return self.default_signal_type

    def extract_subject_entity(self, card: ParsedSourceCard, rec: DriverRecord) -> str:
        company = str(rec.extra.get("company") or "").strip()
        if company:
            return company
        cols = rec.extra.get("columns")
        if isinstance(cols, list) and len(cols) >= 3:
            # Many official gazette tables put entity in col 2 or 3
            for c in cols[1:3]:
                if len(str(c)) >= 4 and not re.match(r"^\d{1,2}/\d{1,2}/\d{4}$", str(c)):
                    return str(c)
        return card.meta["name"]

    @abstractmethod
    def interpret(self, card: ParsedSourceCard, records: List[DriverRecord]) -> List[RawExtractedItem]:
        """将底层 DriverRecord 转化为符合 RawExtractedItem 契约的候选物料。"""

    def _build_raw_item(self, card: ParsedSourceCard, rec: DriverRecord) -> RawExtractedItem:
        blob = f"{rec.title} {rec.summary} {rec.extra.get('location', '')}"
        return RawExtractedItem(
            source_id=card.meta["source_id"],
            title=rec.title,
            pub_date_raw=rec.pub_date_raw or "date_unverified",
            subject_entity=self.extract_subject_entity(card, rec),
            geo_location=detect_geo_location(blob),
            signal_type=self.classify_signal(rec),
            project_scale=detect_project_scale(blob),
            evidence_snippet=(rec.summary or rec.title)[:350],
            direct_url=rec.direct_url,
            attachment_urls=list(rec.attachment_urls),
        )
