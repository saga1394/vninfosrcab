"""
V2/sources/skills/gazette_table_parser.py
-----------------------------------------
上层技能 3：gazette-table-parser（法定公文与审批公示技能）。
识别环评 ĐTM、排污许可、法规公报，剔除纯乡村农业水利、垃圾转运站与微型商贸登记流水。
"""

from typing import List
from sources.drivers import DriverRecord
from sources.interfaces.contracts import ParsedSourceCard, RawExtractedItem, SignalType
from sources.skills.base_skill import BaseArchetypeSkill


class GazetteTableParserSkill(BaseArchetypeSkill):
    skill_name = "gazette-table-parser"
    default_signal_type = "eia_approval"
    noise_keywords = (
        "thủy lợi nông thôn",
        "nạo vét kênh mương",
        "nghĩa trang",
        "trường mầm non",
        "trường tiểu học",
        "trạm trung chuyển rác sinh hoạt",
        "đường giao thông nông thôn",
        "bố cáo thành lập doanh nghiệp",
    )

    def classify_signal(self, rec: DriverRecord) -> SignalType:
        blob = f"{rec.title} {rec.summary}".lower()
        if any(k in blob for k in ("đtm", "dtm", "đánh giá tác động môi trường", "giấy phép môi trường")):
            return "eia_approval"
        if any(k in blob for k in ("luật", "nghị định", "thông tư", "quyết định", "vbpl")):
            return "policy_regulation"
        return "eia_approval"

    def interpret(self, card: ParsedSourceCard, records: List[DriverRecord]) -> List[RawExtractedItem]:
        items: List[RawExtractedItem] = []
        for rec in records:
            if self.should_discard(card, rec):
                continue
            items.append(self._build_raw_item(card, rec))
        return items
