"""
V2/sources/skills/disclosure_sniffer.py
---------------------------------------
上层技能 4：disclosure-sniffer（境外上市公司母公司信披技能）。
识别对越投资、设立在越子公司/孙公司、增资扩产与资产出售退出决议。
"""

from typing import List
from sources.drivers import DriverRecord
from sources.interfaces.contracts import ParsedSourceCard, RawExtractedItem, SignalType
from sources.skills.base_skill import BaseArchetypeSkill


class DisclosureSnifferSkill(BaseArchetypeSkill):
    skill_name = "disclosure-sniffer"
    default_signal_type = "capital_increase"
    noise_keywords = (
        "理财产品",
        "闲置募集资金",
        "独立董事述职",
        "监事会决议",
        "证券事务代表",
        "dividend distribution",
    )

    def classify_signal(self, rec: DriverRecord) -> SignalType:
        blob = f"{rec.title} {rec.summary}".lower()
        if any(k in blob for k in ("设立", "新设", "vietnam subsidiary", "greenfield", "新建")):
            return "factory_setup"
        if any(k in blob for k in ("mou", "意向", "框架协议")):
            return "investment_mou"
        return "capital_increase"

    def interpret(self, card: ParsedSourceCard, records: List[DriverRecord]) -> List[RawExtractedItem]:
        items: List[RawExtractedItem] = []
        for rec in records:
            if self.should_discard(card, rec):
                continue
            items.append(self._build_raw_item(card, rec))
        return items
