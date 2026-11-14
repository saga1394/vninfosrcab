"""
V2/sources/skills/job_radar_scanner.py
--------------------------------------
上层技能 1：job-radar-scanner（招聘前瞻雷达技能）。
识别新厂筹建、选址团队、厂长/EHS总监等早期投资微信号，剔除普工/外包/零售噪音。
"""

from typing import List
from sources.drivers import DriverRecord
from sources.interfaces.contracts import ParsedSourceCard, RawExtractedItem, SignalType
from sources.skills.base_skill import BaseArchetypeSkill


class JobRadarScannerSkill(BaseArchetypeSkill):
    skill_name = "job-radar-scanner"
    default_signal_type = "factory_setup"
    noise_keywords = (
        "công nhân sản xuất",
        "tạp vụ",
        "bảo vệ",
        "lễ tân",
        "nhân viên bán hàng",
        "retail sales",
        "telesales",
        "intern ",
    )

    def classify_signal(self, rec: DriverRecord) -> SignalType:
        blob = f"{rec.title} {rec.summary}".lower()
        if any(k in blob for k in ("expansion", "mở rộng", "phase 2", "giai đoạn 2")):
            return "capital_increase"
        return "factory_setup"

    def interpret(self, card: ParsedSourceCard, records: List[DriverRecord]) -> List[RawExtractedItem]:
        items: List[RawExtractedItem] = []
        for rec in records:
            if self.should_discard(card, rec):
                continue
            items.append(self._build_raw_item(card, rec))
        return items
