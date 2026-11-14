"""
V2/sources/interfaces/test_contracts.py
-----------------------------------------
V2 强类型契约与总册编译回归测试（验证 8492 QA 报告补丁 1~5）。
"""

import glob
import json
import os
import re
import sys
import tempfile

V2_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if V2_ROOT not in sys.path:
    sys.path.insert(0, V2_ROOT)

from sources.interfaces.compile_registry_md import compile_registry
from sources.interfaces.contracts import (
    CandidateVault,
    CuratedBriefItem,
    RawExtractedItem,
    RegistryEntry,
    SourceCardParser,
    backfill_candidate_urls,
)
from sources.interfaces.health_ledger import SourceHealthLedger


def test_cards_and_contracts():
    cards_dir = os.path.join(V2_ROOT, "sources", "cards")
    card_files = sorted(glob.glob(os.path.join(cards_dir, "*.md")))
    assert len(card_files) >= 6, f"期望至少 6 张覆盖全驱动的 V2 卡片，实际仅发现 {len(card_files)}"

    vault = CandidateVault()

    for fpath in card_files:
        fname = os.path.basename(fpath)
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()

        parsed = SourceCardParser.parse_card_markdown(content)
        rel_path = os.path.relpath(fpath, V2_ROOT).replace("\\", "/")

        entry = parsed.to_registry_entry(rel_path)
        assert isinstance(entry, RegistryEntry)
        assert entry.status in ("active", "degraded", "low_freq", "retired")

        # 容错适配器测试：反引号、大写 Status、中文周期、别名字段
        dirty_dict = entry.to_dict()
        dirty_dict["status"] = "`Active`"
        dirty_dict["freq"] = "每日"
        dirty_dict["last_audit"] = dirty_dict.pop("last_audit_date")
        del dirty_dict["check_frequency"]
        clean_entry = RegistryEntry.from_dict(dirty_dict)
        assert clean_entry.status == "active"
        assert clean_entry.check_frequency == "daily"

        # 校验第 4 节 JSON 示例与 RawExtractedItem 强对齐
        m = re.search(r"## 4\. 抽取字段契约.*?```json\s*\n(.*?)\n```", content, re.DOTALL)
        assert m, f"{fname} 未找到第 4 节 JSON 契约示例"
        sample_json = json.loads(m.group(1))
        raw_item = RawExtractedItem(**sample_json)
        assert raw_item.source_id == entry.source_id

        cand = vault.register(raw_item)
        llm_payload = cand.to_llm_payload()
        assert "direct_url" not in llm_payload, "URL 泄漏给大模型 Payload!"
        assert "attachment_urls" not in llm_payload
        assert llm_payload["candidate_id"] == cand.candidate_id
        print(f"  [PASS] V2 卡片契约校验: {fname} ({entry.protocol_driver}, verify_ssl={parsed.network_config.verify_ssl})")

    real_cids = list(vault.as_dict().keys())
    simulated_llm_output = [
        CuratedBriefItem(
            column="fdi",
            title_zh="安靠科技环评公示与立讯精密筹建招聘多源印证",
            fact_summary="多源印证北宁省半导体与精密制造新增产能落地推进。",
            insight_analysis="北宁工业区产业链集群继续扩容。",
            ref_candidate_ids=[real_cids[0], real_cids[1], "C-HALLUCINATED-999"],
        )
    ]

    backfilled = backfill_candidate_urls(simulated_llm_output, vault.as_dict())
    item0 = backfilled[0]
    assert len(item0.verified_urls) == 2
    assert item0.unresolved_ids == ["C-HALLUCINATED-999"]
    print(f"  [PASS] V2 防幻觉回填验证成功: 回填 {len(item0.verified_urls)} 条真链接，拦截 {item0.unresolved_ids}")


def test_health_ledger_and_compiler():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_db = os.path.join(tmpdir, "v2_test_state.db")
        ledger = SourceHealthLedger(tmp_db)

        ledger.ensure_source("SRC-APP-001", "active")
        assert ledger.get_health("SRC-APP-001")["current_status"] == "active"
        assert ledger.record_failure("SRC-APP-001", "Timeout", degrade_threshold=2) == "active"
        assert ledger.record_failure("SRC-APP-001", "HTTP 500", degrade_threshold=2) == "degraded"
        assert ledger.get_health("SRC-APP-001")["consecutive_failures"] == 2
        assert ledger.record_success("SRC-APP-001") == "active"
        assert ledger.get_health("SRC-APP-001")["consecutive_failures"] == 0
        print("  [PASS] V2 健康账本状态机流转验证通过 (active -> degraded -> active)")

    compiled = compile_registry()
    assert len(compiled) >= 6
    print(f"  [PASS] V2 只读总册编译器测试通过，成功编译 V2/sources/MASTER-SOURCE-REGISTRY.md ({len(compiled)} 项)")


if __name__ == "__main__":
    print("=== 运行 V2 (8492) 契约与编译器全量测试 ===")
    test_cards_and_contracts()
    test_health_ledger_and_compiler()
    print("=== V2 契约测试 100% 通过！ ===")
