"""
V2/sources/interfaces/compile_registry_md.py
--------------------------------------------
V2 只读总册编译器 (补丁 1 & 4)。
自动扫描 V2/sources/cards/*.md，结合 V2/data/state_ledger.db 状态机实时数据，
确定性地编译生成人类可读的 V2/sources/MASTER-SOURCE-REGISTRY.md 与机器配置 V2/config/master_sources_registry.json。
"""

import glob
import json
import os
import sys
from datetime import datetime
from typing import List, Optional

V2_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if V2_ROOT not in sys.path:
    sys.path.insert(0, V2_ROOT)

from sources.interfaces.contracts import SourceCardParser, RegistryEntry
from sources.interfaces.health_ledger import SourceHealthLedger, DEFAULT_LEDGER_DB

CARDS_DIR = os.path.join(V2_ROOT, "sources", "cards")
OUT_REGISTRY_MD = os.path.join(V2_ROOT, "sources", "MASTER-SOURCE-REGISTRY.md")
OUT_REGISTRY_JSON = os.path.join(V2_ROOT, "config", "master_sources_registry.json")


def compile_registry(
    cards_dir: str = CARDS_DIR,
    out_md: str = OUT_REGISTRY_MD,
    out_json: str = OUT_REGISTRY_JSON,
    db_path: Optional[str] = None,
    root_dir: Optional[str] = None,
) -> List[RegistryEntry]:
    ledger = SourceHealthLedger(db_path or DEFAULT_LEDGER_DB)
    health_map = ledger.get_all_health()
    base_root = root_dir or (
        V2_ROOT
        if os.path.abspath(cards_dir) == os.path.abspath(CARDS_DIR)
        else os.path.dirname(os.path.dirname(os.path.abspath(cards_dir)))
    )

    card_files = sorted(glob.glob(os.path.join(cards_dir, "*.md")))
    entries: List[RegistryEntry] = []

    for fpath in card_files:
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        parsed = SourceCardParser.parse_card_markdown(content)
        rel_path = os.path.relpath(fpath, base_root).replace("\\", "/")
        entry = parsed.to_registry_entry(rel_path)

        if entry.source_id in health_map:
            entry.status = health_map[entry.source_id]["current_status"]  # type: ignore[assignment]
        else:
            ledger.ensure_source(entry.source_id, entry.status)

        entries.append(entry)

    os.makedirs(os.path.dirname(out_json), exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as jf:
        json.dump([e.to_dict() for e in entries], jf, ensure_ascii=False, indent=2)

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    active_cnt = sum(1 for e in entries if e.status == "active")
    degraded_cnt = sum(1 for e in entries if e.status == "degraded")

    lines = [
        "# 越南产业与 FDI 全景信源总册 V2 (Master Source Registry)\n\n",
        f"> **自动编译时间戳**：{now_str}  \n",
        "> **重要警告**：本文件由 `V2/sources/interfaces/compile_registry_md.py` 依据各卡片 YAML 与健康账本自动生成，**严禁手工直接修改本表格**！\n\n",
        f"- **总纳管信源数**：`{len(entries)}` 项（活跃 `active`: **{active_cnt}** | 降级 `degraded`: **{degraded_cnt}**）\n\n",
        "| `source_id` | `name` | `cluster` | `target_url` | `archetype_skill` | `protocol_driver` | `priority` | `expected_column` | `check_frequency` | `status` | `card_path` | `last_audit_date` |\n",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :---: | :--- | :---: | :---: | :--- | :---: |\n",
    ]

    for e in entries:
        card_link = e.card_path[len("sources/"):] if e.card_path.startswith("sources/") else e.card_path
        lines.append(
            f"| `{e.source_id}` | {e.name} | `{e.cluster}` | {e.target_url} | `{e.archetype_skill}` | "
            f"`{e.protocol_driver}` | **{e.priority}** | `{e.expected_column}` | `{e.check_frequency}` | "
            f"**{e.status}** | [{os.path.basename(e.card_path)}]({card_link}) | {e.last_audit_date} |\n"
        )

    os.makedirs(os.path.dirname(out_md), exist_ok=True)
    with open(out_md, "w", encoding="utf-8") as mf:
        mf.writelines(lines)

    return entries


if __name__ == "__main__":
    compiled = compile_registry()
    print(f"[V2] 成功编译总册，共纳入 {len(compiled)} 个信源。")
