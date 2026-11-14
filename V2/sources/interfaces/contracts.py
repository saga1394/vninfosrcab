"""
V2/sources/interfaces/contracts.py
------------------------------------
V2 强类型契约中心（依据 8492 QA 审计报告全量 5 大补丁构建，与 V1 彻底隔离）：
- 补丁 1：RegistryEntry 对齐 priority / expected_column / protocol_driver，大小写与中文周期容错，
         RawExtractedItem 与 ExtractedCandidate 两级解耦，稳健 YAML 卡片解析器（保留 URL # 锚点）。
- 补丁 2：业务原型技能（5 Archetypes）与底层协议驱动（5 Protocol Drivers）双层解耦契约。
- 补丁 3：NetworkConfig / SearchSpec / ApiSpec / attachment_probe 机读参数化结构。
- 补丁 5：CandidateVault 统一防冲突赋码 + 脱敏 Payload + CuratedBriefItem + backfill_candidate_urls 防幻觉回填闭环。
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Literal, Tuple
import json
import logging
import re

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover - stdlib fallback when PyYAML is absent
    yaml = None

logger = logging.getLogger(__name__)

# 1. 核心枚举定义
ClusterType = Literal[
    "job_radar",              # 招聘前瞻雷达
    "industrial_park",        # 工业园区一线
    "legal_approval",         # 法定公文审批
    "corporate_disclosure",   # 境外母公司信披
    "media_fdi",              # 主流财经专版
]

ArchetypeSkillType = Literal[
    "job-radar-scanner",
    "park-news-inspector",
    "gazette-table-parser",
    "disclosure-sniffer",
    "media-stream-curator",
]

ProtocolDriverType = Literal[
    "rss_driver",             # 原生 RSS / Atom
    "html_card_driver",       # 规整图文卡片容器 / __NEXT_DATA__
    "html_table_driver",      # 规整 HTML / ASP.NET 数据表格
    "rest_api_driver",        # JSON REST API / SPA 接口 / 静态 JS 数组
    "sitemap_driver",         # XML Sitemap 增量流
]

SourceStatus = Literal[
    "active",                 # 正常活跃，纳入轮巡
    "degraded",               # 故障待修复（连续失败触发）
    "low_freq",               # 低频源（降级为每周轮巡）
    "retired",                # 退役归档
]

PriorityType = Literal["P0", "P1", "P2"]

ColumnType = Literal[
    "fdi",                    # 一、【FDI 外资投资动向】
    "industrial_park",        # 二、【工业园区一线动态】
    "industry_focus",         # 三、【重点关注产业专题】
    "legal_approval",         # 四、【行政审批与法定公示】
    "macro_policy",           # 五、【政经与综合市场动态】
]

SignalType = Literal[
    "factory_setup",          # 筹建团队/选址招聘
    "land_grant",             # 园区供地/签约/租地
    "ground_breaking",        # 现场奠基/开工
    "eia_approval",           # 环评审批公示
    "investment_mou",         # 投资意向备忘录
    "capital_increase",       # 增资扩产
    "policy_regulation",      # 税制电价法令调整
]

VALID_CLUSTERS = {"job_radar", "industrial_park", "legal_approval", "corporate_disclosure", "media_fdi"}
VALID_ARCHETYPES = {
    "job-radar-scanner",
    "park-news-inspector",
    "gazette-table-parser",
    "disclosure-sniffer",
    "media-stream-curator",
}
VALID_DRIVERS = {"rss_driver", "html_card_driver", "html_table_driver", "rest_api_driver", "sitemap_driver"}
VALID_STATUSES = {"active", "degraded", "low_freq", "retired"}
VALID_PRIORITIES = {"P0", "P1", "P2"}
VALID_COLUMNS = {"fdi", "industrial_park", "industry_focus", "legal_approval", "macro_policy"}
VALID_SIGNALS = {
    "factory_setup",
    "land_grant",
    "ground_breaking",
    "eia_approval",
    "investment_mou",
    "capital_increase",
    "policy_regulation",
}
FREQ_MAP = {"每日": "daily", "每周": "weekly", "每月": "monthly"}


def normalize_status(raw: str) -> str:
    cleaned = str(raw).strip().strip("`\"'").lower()
    if cleaned not in VALID_STATUSES:
        raise ValueError(f"非法状态枚举值: {raw}")
    return cleaned


def normalize_frequency(raw: str) -> str:
    cleaned = str(raw).strip().strip("`\"'").lower()
    return FREQ_MAP.get(cleaned, cleaned)


def _strip_inline_yaml_comment(value: str) -> str:
    """Strip `# comment` only outside quotes and when `#` is preceded by whitespace (preserving URL #fragments)."""
    in_single = False
    in_double = False
    for idx, ch in enumerate(value):
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == "#" and not in_single and not in_double:
            if idx == 0 or value[idx - 1].isspace():
                return value[:idx].rstrip()
    return value.strip()


def _parse_yaml_scalar(raw: str) -> Any:
    val = _strip_inline_yaml_comment(raw.strip())
    if not val:
        return ""
    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
        return val[1:-1]
    low = val.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    if low in ("null", "~"):
        return None
    if re.fullmatch(r"-?\d+", val):
        return int(val)
    if re.fullmatch(r"-?\d+\.\d+", val):
        return float(val)
    return val


def _fallback_safe_load_yaml(yaml_text: str) -> Dict[str, Any]:
    """Minimal safe YAML subset parser for Frontmatter when PyYAML is not installed."""
    root: Dict[str, Any] = {}
    stack: List[Tuple[int, Any, Optional[str]]] = [(-1, root, None)]

    lines = yaml_text.splitlines()
    for line in lines:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()

        while len(stack) > 1 and indent <= stack[-1][0]:
            stack.pop()

        parent_indent, parent_obj, parent_key = stack[-1]

        if stripped.startswith("- "):
            item_val = _parse_yaml_scalar(stripped[2:])
            if isinstance(parent_obj, list):
                parent_obj.append(item_val)
            elif isinstance(parent_obj, dict) and parent_key is not None:
                if not isinstance(parent_obj.get(parent_key), list):
                    parent_obj[parent_key] = []
                parent_obj[parent_key].append(item_val)
                stack.append((indent - 1, parent_obj[parent_key], None))
            continue

        if ":" in stripped:
            key, rest = stripped.split(":", 1)
            key = key.strip().strip("\"'")
            rest_clean = _strip_inline_yaml_comment(rest.strip())

            target_dict = parent_obj
            if isinstance(parent_obj, dict) and parent_key is not None and parent_obj.get(parent_key) is None:
                parent_obj[parent_key] = {}
                target_dict = parent_obj[parent_key]
                stack.append((indent - 1, target_dict, None))

            if rest_clean == "":
                target_dict[key] = None
                stack.append((indent, target_dict, key))
            else:
                target_dict[key] = _parse_yaml_scalar(rest)

    # Convert leftover None containers created by empty keys into empty dicts
    def _clean_nones(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {k: ({} if v is None and k in ("network_config", "search_spec", "api_spec", "headers", "payload_template") else _clean_nones(v)) for k, v in obj.items()}
        return obj

    return _clean_nones(root)


def load_yaml_frontmatter(yaml_block: str) -> Dict[str, Any]:
    if yaml is not None:
        parsed = yaml.safe_load(yaml_block)
    else:
        parsed = _fallback_safe_load_yaml(yaml_block)
    if not isinstance(parsed, dict):
        raise ValueError("YAML Frontmatter 解析结果不是有效字典。")
    return parsed


# 2. 网络与参数化抓取配置结构 (补丁 3)
@dataclass
class NetworkConfig:
    verify_ssl: bool = True
    timeout: int = 15
    resolve_ip: Optional[str] = None
    use_curl: bool = False
    headers: Dict[str, str] = field(
        default_factory=lambda: {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }
    )


@dataclass
class SearchSpec:
    endpoint_template: str = ""
    keywords: List[str] = field(default_factory=list)


@dataclass
class ApiSpec:
    method: str = "GET"
    content_type: str = "json"          # json | form
    headers: Dict[str, str] = field(default_factory=dict)
    payload_template: Optional[Dict[str, Any]] = None
    json_path: str = ""
    nested_json_field: str = ""         # e.g. HKEX where result is a JSON-encoded string
    detail_url_template: str = ""
    title_template: str = ""
    date_field: str = ""
    filter_field: str = ""
    filter_contains: str = ""


# 3. 信源总册行条目契约 (补丁 1 & 2 强对齐)
@dataclass
class RegistryEntry:
    source_id: str                      # 唯一编号，如 SRC-JOB-001
    name: str                           # 机构/源名称
    cluster: ClusterType                # 归属集群大类
    target_url: str                     # 监控靶点 URL
    archetype_skill: ArchetypeSkillType # 上层业务认知技能
    protocol_driver: ProtocolDriverType # 底层网络协议驱动
    check_frequency: str                # daily | weekly | monthly
    priority: PriorityType              # P0 | P1 | P2
    expected_column: ColumnType         # 预期归仓栏目
    status: SourceStatus                # active | degraded | low_freq | retired
    card_path: str                      # 专属作业卡相对路径
    last_audit_date: str                # YYYY-MM-DD

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RegistryEntry":
        """容错反序列化适配器，清理反引号、别名差异与大小写/中文频次。"""
        clean = {k: (v.strip("` ") if isinstance(v, str) else v) for k, v in data.items()}
        if "freq" in clean and "check_frequency" not in clean:
            clean["check_frequency"] = clean.pop("freq")
        if "last_audit" in clean and "last_audit_date" not in clean:
            clean["last_audit_date"] = clean.pop("last_audit")

        cluster = clean["cluster"]
        if cluster not in VALID_CLUSTERS:
            raise ValueError(f"非法 cluster 枚举值: {cluster}")

        archetype = clean["archetype_skill"]
        if archetype not in VALID_ARCHETYPES:
            raise ValueError(f"非法 archetype_skill 枚举值: {archetype}")

        driver = clean["protocol_driver"]
        if driver not in VALID_DRIVERS:
            raise ValueError(f"非法 protocol_driver 枚举值: {driver}")

        priority = str(clean.get("priority", "P1")).strip("` ").upper()
        if priority not in VALID_PRIORITIES:
            raise ValueError(f"非法 priority 枚举值: {priority}")

        expected_col = str(clean.get("expected_column", "fdi")).strip("` ")
        if expected_col not in VALID_COLUMNS:
            raise ValueError(f"非法 expected_column 枚举值: {expected_col}")

        return cls(
            source_id=clean["source_id"],
            name=clean["name"],
            cluster=cluster,
            target_url=clean["target_url"],
            archetype_skill=archetype,
            protocol_driver=driver,
            check_frequency=normalize_frequency(clean["check_frequency"]),
            priority=priority,  # type: ignore[arg-type]
            expected_column=expected_col,  # type: ignore[arg-type]
            status=normalize_status(clean["status"]),  # type: ignore[arg-type]
            card_path=clean["card_path"],
            last_audit_date=str(clean["last_audit_date"]),
        )


# 4. 抽取物料与候选实体两级解耦 (补丁 1 & 5)
@dataclass
class RawExtractedItem:
    """
    底层驱动与业务技能抽取的原始物料（不含运行时 candidate_id 与 extracted_at，完全对齐卡片第 4 节 JSON 契约）。
    """
    source_id: str
    title: str
    pub_date_raw: str
    subject_entity: str
    geo_location: str
    signal_type: SignalType
    project_scale: Optional[str]
    evidence_snippet: str
    direct_url: str
    attachment_urls: List[str] = field(default_factory=list)

    def to_candidate(self, seq: int) -> "ExtractedCandidate":
        """由框架调度器统一包裹并分配防冲突的不可变 Candidate ID。"""
        cid = f"C-{self.source_id}-{seq:04d}"
        now_iso = datetime.now(timezone.utc).isoformat()
        return ExtractedCandidate(
            candidate_id=cid,
            extracted_at=now_iso,
            **asdict(self),
        )


@dataclass
class ExtractedCandidate:
    """
    经框架统一赋码（Candidate ID）并登记时间后的完整候选实体。
    """
    candidate_id: str
    source_id: str
    title: str
    pub_date_raw: str
    subject_entity: str
    geo_location: str
    signal_type: SignalType
    project_scale: Optional[str]
    evidence_snippet: str
    direct_url: str
    extracted_at: str
    attachment_urls: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_llm_payload(self) -> Dict[str, Any]:
        """
        生成给大模型做对账研判的脱敏字典。
        核心安全策略：剥夺大模型接触 URL 的权力，仅保留 candidate_id。
        """
        d = asdict(self)
        d.pop("direct_url", None)
        d.pop("attachment_urls", None)
        return d


class CandidateVault:
    """
    框架级 Candidate 唯一赋码器与不可变 URL 映射底账 (补丁 5)。
    保证多源并发时 candidate_id 绝对不冲突，并安全隔离大模型可见 Payload 与物理直达 URL。
    """

    def __init__(self) -> None:
        self._seq_by_source: Dict[str, int] = {}
        self._vault: Dict[str, ExtractedCandidate] = {}

    def register(self, raw_item: RawExtractedItem) -> ExtractedCandidate:
        next_seq = self._seq_by_source.get(raw_item.source_id, 0) + 1
        self._seq_by_source[raw_item.source_id] = next_seq
        candidate = raw_item.to_candidate(next_seq)
        self._vault[candidate.candidate_id] = candidate
        return candidate

    def register_many(self, raw_items: List[RawExtractedItem]) -> List[ExtractedCandidate]:
        return [self.register(item) for item in raw_items]

    def to_llm_payloads(self) -> List[Dict[str, Any]]:
        return [cand.to_llm_payload() for cand in self._vault.values()]

    def as_dict(self) -> Dict[str, ExtractedCandidate]:
        return dict(self._vault)

    def __len__(self) -> int:
        return len(self._vault)


# 5. 大模型输出 Schema 与防幻觉 URL 回填闭环 (补丁 5)
@dataclass
class CuratedBriefItem:
    """
    大模型对账与研判完成后的结构化输出契约。
    大模型只输出 ref_candidate_ids，绝不允许输出任何 URL。
    """
    column: ColumnType
    title_zh: str
    fact_summary: str
    insight_analysis: str
    ref_candidate_ids: List[str]
    is_follow_up: bool = False
    verified_urls: List[str] = field(default_factory=list)
    unresolved_ids: List[str] = field(default_factory=list)


def backfill_candidate_urls(
    curated_items: List[CuratedBriefItem],
    candidate_vault: Dict[str, ExtractedCandidate],
) -> List[CuratedBriefItem]:
    """
    防幻觉终极屏障：将大模型研判输出的 ref_candidate_ids
    精确映射回底层抓取记录中的真实 direct_url。
    支持多源合流（一条简报关联多个 Candidate ID）自动去重并保留全部真实佐证链接。
    """
    for item in curated_items:
        urls: List[str] = []
        unresolved: List[str] = []
        seen_urls = set()

        for cid in item.ref_candidate_ids:
            if cid in candidate_vault:
                real_url = candidate_vault[cid].direct_url
                if real_url and real_url not in seen_urls:
                    urls.append(real_url)
                    seen_urls.add(real_url)
            else:
                logger.warning("检测到非法 Candidate ID 幻觉引用: %s", cid)
                unresolved.append(cid)

        item.verified_urls = urls
        item.unresolved_ids = unresolved

    return curated_items


# 6. 强健的 YAML 卡片解析器 (补丁 1 & 3)
@dataclass
class ParsedSourceCard:
    meta: Dict[str, Any]
    network_config: NetworkConfig
    search_spec: Optional[SearchSpec]
    api_spec: Optional[ApiSpec]
    attachment_probe: bool
    instructions: str

    def to_registry_entry(self, card_path: str) -> RegistryEntry:
        """将卡片元数据无损转换为 RegistryEntry，彻底消除字段遗漏导致的 TypeError。"""
        data = dict(self.meta)
        data["card_path"] = card_path
        return RegistryEntry.from_dict(data)


class SourceCardParser:
    """
    基于 PyYAML（及内置安全兜底解析器）的信源作业卡解析器，
    完好保留 URL 中的 # 锚点、带引号字符串与嵌套配置块，并强制校验必填键。
    """
    REQUIRED_META_KEYS = {
        "source_id",
        "name",
        "cluster",
        "target_url",
        "archetype_skill",
        "protocol_driver",
        "check_frequency",
        "priority",
        "expected_column",
        "status",
        "last_audit_date",
    }

    @classmethod
    def parse_card_markdown(cls, md_content: str) -> ParsedSourceCard:
        match = re.match(r"^---\s*\r?\n(.*?)\r?\n---\s*\r?\n(.*)$", md_content, re.DOTALL)
        if not match:
            raise ValueError("卡片格式不符合规范：缺少有效的 YAML Frontmatter 头部。")

        yaml_block = match.group(1)
        body_markdown = match.group(2).strip()

        raw_meta = load_yaml_frontmatter(yaml_block)
        missing = cls.REQUIRED_META_KEYS - set(raw_meta.keys())
        if missing:
            raise ValueError(f"卡片 Frontmatter 缺失必填键: {sorted(missing)}")

        net_raw = raw_meta.get("network_config") or {}
        if not isinstance(net_raw, dict):
            raise ValueError("network_config 必须为字典结构。")
        default_headers = NetworkConfig().headers
        net_headers = dict(net_raw.get("headers") or default_headers)
        net_cfg = NetworkConfig(
            verify_ssl=bool(net_raw.get("verify_ssl", True)),
            timeout=int(net_raw.get("timeout", 15)),
            resolve_ip=str(net_raw["resolve_ip"]).strip() if net_raw.get("resolve_ip") else None,
            use_curl=bool(net_raw.get("use_curl", False)),
            headers=net_headers,
        )

        search_raw = raw_meta.get("search_spec")
        search_spec = None
        if isinstance(search_raw, dict):
            search_spec = SearchSpec(
                endpoint_template=str(search_raw.get("endpoint_template", "")),
                keywords=[str(k) for k in (search_raw.get("keywords") or [])],
            )

        api_raw = raw_meta.get("api_spec")
        api_spec = None
        if isinstance(api_raw, dict):
            payload = api_raw.get("payload_template")
            if isinstance(payload, str):
                try:
                    payload = json.loads(payload)
                except json.JSONDecodeError:
                    payload = None
            api_spec = ApiSpec(
                method=str(api_raw.get("method", "GET")).upper(),
                content_type=str(api_raw.get("content_type", "json")).lower(),
                headers=dict(api_raw.get("headers") or {}),
                payload_template=payload if isinstance(payload, dict) else None,
                json_path=str(api_raw.get("json_path", "")),
                nested_json_field=str(api_raw.get("nested_json_field", "")),
                detail_url_template=str(api_raw.get("detail_url_template", "")),
                title_template=str(api_raw.get("title_template", "")),
                date_field=str(api_raw.get("date_field", "")),
                filter_field=str(api_raw.get("filter_field", "")),
                filter_contains=str(api_raw.get("filter_contains", "")),
            )

        attachment_probe = bool(raw_meta.get("attachment_probe", False))

        raw_meta["status"] = normalize_status(raw_meta["status"])
        raw_meta["check_frequency"] = normalize_frequency(raw_meta["check_frequency"])
        raw_meta["last_audit_date"] = str(raw_meta["last_audit_date"])

        # Eagerly validate RegistryEntry fields so invalid enums fail fast on card parse
        RegistryEntry.from_dict({**raw_meta, "card_path": "validation-placeholder.md"})

        return ParsedSourceCard(
            meta=raw_meta,
            network_config=net_cfg,
            search_spec=search_spec,
            api_spec=api_spec,
            attachment_probe=attachment_probe,
            instructions=body_markdown,
        )
