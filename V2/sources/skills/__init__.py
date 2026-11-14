"""V2 Layer 2: Archetype Cognitive Skills Registry."""

from typing import Dict
from .base_skill import BaseArchetypeSkill
from .job_radar_scanner import JobRadarScannerSkill
from .park_news_inspector import ParkNewsInspectorSkill
from .gazette_table_parser import GazetteTableParserSkill
from .disclosure_sniffer import DisclosureSnifferSkill
from .media_stream_curator import MediaStreamCuratorSkill

SKILL_REGISTRY: Dict[str, BaseArchetypeSkill] = {
    "job-radar-scanner": JobRadarScannerSkill(),
    "park-news-inspector": ParkNewsInspectorSkill(),
    "gazette-table-parser": GazetteTableParserSkill(),
    "disclosure-sniffer": DisclosureSnifferSkill(),
    "media-stream-curator": MediaStreamCuratorSkill(),
}


def get_archetype_skill(skill_name: str) -> BaseArchetypeSkill:
    if skill_name not in SKILL_REGISTRY:
        raise KeyError(f"未注册的业务原型技能: {skill_name}")
    return SKILL_REGISTRY[skill_name]


__all__ = [
    "BaseArchetypeSkill",
    "JobRadarScannerSkill",
    "ParkNewsInspectorSkill",
    "GazetteTableParserSkill",
    "DisclosureSnifferSkill",
    "MediaStreamCuratorSkill",
    "SKILL_REGISTRY",
    "get_archetype_skill",
]
