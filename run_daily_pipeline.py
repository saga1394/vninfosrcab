# -*- coding: utf-8 -*-
"""
Master Autonomous Daily Pipeline for Vietnam Industrial & Investment Intelligence.
Full End-to-End Orchestrator:
1. Stage 1 Collection (38 verified core sources);
2. Stage 2 Entity Alignment & Timeline Assembly (projects.db);
3. Automated Curation & Milestone Progression (anti-duplication & 5 orthogonal categories);
4. Multi-Channel Asset Assembly (HTML Dashboard, Vector PDF, Executive Markdown, RSS);
5. Pre-Flight Quality Gate (Zero-tolerance automated QA check on URLs, titles, freshness, size);
6. Safe Delivery (3-person matrix SMTP dispatch & state ledger recording).

Usage:
    python run_daily_pipeline.py --dry-run           # Full run with Quality Gate, skips email sending
    python run_daily_pipeline.py --skip-collect       # Fast run using local DB, runs QA and delivery
    python run_daily_pipeline.py --send-email         # Full production run with automatic email delivery
"""

import os
import sys
import argparse
import time
import json
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))


def main():
    parser = argparse.ArgumentParser(description="Vietnam Investment Intelligence Master Autonomous Pipeline")
    parser.add_argument("--skip-collect", action="store_true", help="Skip web scraping, process existing collector.db")
    parser.add_argument("--dry-run", action="store_true", help="Run full pipeline and Quality Gate, but skip email dispatch")
    parser.add_argument("--send-email", action="store_true", help="Automatically send email to the 3-member team if QA passes")
    args = parser.parse_args()

    t_start = time.time()
    today_str = datetime.now().strftime("%Y-%m-%d")

    print("\n" + "=" * 75)
    print(f"  VIETNAM INDUSTRIAL INTELLIGENCE PIPELINE - DAILY AUTONOMOUS RUN ({today_str})")
    print("=" * 75)

    # 0. Initialize State Ledger
    from scripts.pipeline.state_ledger import init_ledger, record_reported_items
    init_ledger()

    # 1. Stage 1: Collection Engine (38 core sources)
    if not args.skip_collect:
        print("\n>>> [STEP 1/5] Executing Stage 1 Routine Collection (38 Core Sources)...")
        from scripts.collector.collector_engine import run_collector
        config_path = os.path.join("config", "sources_core_39.json")
        collector_report = run_collector(config_path, workers=6)
        print(f"    Stage 1 finished: {collector_report['successful_sources']}/{collector_report['total_sources_configured']} sources succeeded in {collector_report['total_elapsed_seconds']}s.")
        print(f"    Total items extracted: {collector_report['total_extracted_records']}, New inserted: {collector_report['total_new_records_inserted']}.")
    else:
        print("\n>>> [STEP 1/5] Skipped Stage 1 Collection (--skip-collect). Using local data/daily/collector.db.")

    # 2. Stage 2: Entity & Timeline Pipeline
    print("\n>>> [STEP 2/5] Executing Stage 2 Entity Extraction & Timeline Assembly...")
    from scripts.stage2.entity_pipeline import run_pipeline as run_stage2_pipeline
    run_stage2_pipeline()

    # 3. Automated Curation & Milestone Progression Engine
    print("\n>>> [STEP 3/5] Executing Automated Cognitive Curation & Milestone Progression...")
    from scripts.pipeline.curation_engine import curate_daily_intelligence
    curated_items = curate_daily_intelligence(max_items=20)
    print(f"    Curated: {len(curated_items)} high-value intelligence items across 5 orthogonal categories.")

    # 4. Multi-Channel Asset Assembly (HTML Dashboard, Vector PDF, Dossier Portfolio, Markdown Brief)
    print("\n>>> [STEP 4/5] Compiling Multi-Channel Deliverable Assets...")
    from scripts.stage2.generate_dossier_portfolio import build_portfolio
    build_portfolio()

    from scripts.stage2.generate_dimensional_report import generate_report as generate_dim_report
    generate_dim_report()

    from scripts.stage2.generate_html_report import build_dashboard_html
    html_path, artifact_path = build_dashboard_html(curated_items)

    from scripts.stage2.generate_rss_feed import generate_rss
    generate_rss()

    # 5. Pre-Flight Quality Gate (Zero-Tolerance Automated Audit)
    print("\n>>> [STEP 5/5] Executing Pre-Flight Quality Gate Audit...")
    from scripts.pipeline.preflight_gate import run_preflight_gate
    passed, audit_report = run_preflight_gate(curated_items, today_str)

    # 6. Delivery Decision & Circuit Breaker
    print("\n" + "=" * 75)
    if not passed:
        print("  🚨 [PIPELINE BLOCKED BY QUALITY GATE]")
        print("  The generated briefing failed one or more critical quality requirements.")
        print("  Email dispatch and publishing have been safely aborted.")
        for err in audit_report.get("errors", []):
            print(f"  - {err}")
        print("=" * 75)
        sys.exit(1)

    print("  ✅ [QUALITY GATE PASSED] All 5 Quality Gates 100% Cleared.")

    if args.dry_run:
        print("  [DRY RUN] Simulation complete. Quality Gate verified. Email dispatch skipped.")
    elif args.send_email:
        print("  [DISPATCH] Quality Gate verified. Triggering automated delivery to 3-person matrix...")
        from scripts.delivery.send_report_email import send_report_email
        delivery_ok = send_report_email(send_to_all=True)
        if delivery_ok:
            # Commit items into state ledger
            recorded = record_reported_items(curated_items, today_str)
            print(f"  [STATE LEDGER] Successfully locked {recorded} items into reported_briefing_items ledger.")
    else:
        print("  [NOTICE] Pipeline passed. Use --send-email to trigger SMTP dispatch, or --dry-run for audit.")

    total_duration = round(time.time() - t_start, 2)
    print("=" * 75)
    print(f"  DAILY PIPELINE EXECUTION FINISHED SUCCESSFULLY IN {total_duration}s")
    print("=" * 75)
    print("  Published Deliverables:")
    print("  - Live Online Dashboard:  docs/index.html (GitHub Pages)")
    print("  - Vector PDF Report:      docs/stage2/FULL-DIMENSIONAL-INTELLIGENCE-REPORT.pdf")
    print("  - Executive Briefing:     docs/stage2/FULL-DIMENSIONAL-INTELLIGENCE-BRIEF.md")
    print("  - Project Portfolio:      docs/stage2/PROJECT-DOSSIER-PORTFOLIO.md")
    print("  - Public RSS Stream:      docs/stage2/feed.xml")
    print("  - Daily Curated Dataset:  data/daily/curated_today.json")
    print("=" * 75 + "\n")


if __name__ == "__main__":
    main()
