"""
V2/sources/skills/media_stream_curator.py
-----------------------------------------
上层技能 5：media-stream-curator（主流财经专版与部委政经流技能）。
坚持高召回“宽进”原则，仅剔除明显社会刑事/娱乐花边/彩票体育杂讯。
"""

from typing import List
from sources.drivers import DriverRecord
from sources.interfaces.contracts import ParsedSourceCard, RawExtractedItem, SignalType
from sources.skills.base_skill import BaseArchetypeSkill


class MediaStreamCuratorSkill(BaseArchetypeSkill):
    skill_name = "media-stream-curator"
    default_signal_type = "policy_regulation"
    noise_keywords = (
        "xổ số",
        "bóng đá",
        "hoa hậu",
        "ca sĩ",
        "showbiz",
        "tai nạn giao thông",
        "trúng thưởng",
    )

    def classify_signal(self, rec: DriverRecord) -> SignalType:
        blob = f"{rec.title} {rec.summary}".lower()
        if any(k in blob for k in ("thuế", "giá điện", "nghị định", "nghị quyết", "thông tư", "luật")):
            return "policy_regulation"
        if any(k in blob for k in ("khởi công", "động thổ", "groundbreaking")):
            return "ground_breaking"
        if any(k in blob for k in ("tăng vốn", "mở rộng", "capital increase", "expansion")):
            return "capital_increase"
        if any(k in blob for k in ("fdi", "đầu tư nước ngoài", "nhà máy mới", "new plant")):
            return "factory_setup"
        return "policy_regulation"

    def interpret(self, card: ParsedSourceCard, records: List[DriverRecord]) -> List[RawExtractedItem]:
        items: List[RawExtractedItem] = []
        for rec in records:
            if self.should_discard(card, rec):
                continue
            items.append(self._build_raw_item(card, rec))
        return items
