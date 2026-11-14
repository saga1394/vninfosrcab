"""
V2/sources/skills/park_news_inspector.py
----------------------------------------
上层技能 2：park-news-inspector（工业园区现场动态技能）。
识别供地签约、开工奠基、厂房交付动向，屏蔽党建/工会/慈善花絮。
"""

from typing import List
from sources.drivers import DriverRecord
from sources.interfaces.contracts import ParsedSourceCard, RawExtractedItem, SignalType
from sources.skills.base_skill import BaseArchetypeSkill


class ParkNewsInspectorSkill(BaseArchetypeSkill):
    skill_name = "park-news-inspector"
    default_signal_type = "land_grant"
    noise_keywords = (
        "hội thao",
        "văn nghệ",
        "đảng bộ",
        "công đoàn",
        "từ thiện",
        "học bổng",
        "tổng kết năm",
        "hiến máu",
    )

    def classify_signal(self, rec: DriverRecord) -> SignalType:
        blob = f"{rec.title} {rec.summary}".lower()
        if any(k in blob for k in ("khởi công", "động thổ", "groundbreaking", "ground breaking")):
            return "ground_breaking"
        if any(k in blob for k in ("mou", "biên bản ghi nhớ", "thỏa thuận hợp tác")):
            return "investment_mou"
        if any(k in blob for k in ("mở rộng", "giai đoạn 2", "phase 2", "expansion")):
            return "capital_increase"
        return "land_grant"

    def interpret(self, card: ParsedSourceCard, records: List[DriverRecord]) -> List[RawExtractedItem]:
        items: List[RawExtractedItem] = []
        for rec in records:
            if self.should_discard(card, rec):
                continue
            items.append(self._build_raw_item(card, rec))
        return items
