"""
Master Entry Point for Vietnam Industrial & Investment Intelligence Pipeline.
Executes Stage 1 (Collection) and Stage 2 (Entity Alignment & Dossier Portfolio).

Usage:
    python run_all.py                  # Full run: Stage 1 collect + Stage 2 process
    python run_all.py --skip-collect   # Fast run: Stage 2 process only (uses existing collector.db)
"""

import sys
import os
import argparse
import time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def main():
    parser = argparse.ArgumentParser(description="Vietnam Investment Intelligence Pipeline Master Runner")
    parser.add_argument("--skip-collect", action="store_true", help="Skip Stage 1 web collection, process existing DB only")
    args = parser.parse_args()

    t_start = time.time()
    print("=" * 70)
    print("  VIETNAM INDUSTRIAL INTELLIGENCE PIPELINE - MASTER RUNNER")
    print("=" * 70)

    # 1. Stage 1: Collection Engine
    if not args.skip_collect:
        print("\n>>> [STEP 1/3] Executing Stage 1 Routine Collection (39 Core Sources)...")
        from scripts.collector.collector_engine import run_collector
        config_path = os.path.join("config", "sources_core_39.json")
        collector_report = run_collector(config_path, workers=6)
        print(f"    Stage 1 finished: {collector_report['successful_sources']}/{collector_report['total_sources_configured']} sources succeeded in {collector_report['total_elapsed_seconds']}s.")
        print(f"    Total items extracted: {collector_report['total_extracted_records']}, New inserted: {collector_report['total_new_records_inserted']}.")
    else:
        print("\n>>> [STEP 1/3] Skipped Stage 1 Collection (--skip-collect). Using local data/daily/collector.db.")

    # 2. Stage 2: Entity Pipeline
    print("\n>>> [STEP 2/3] Executing Stage 2 Entity Extraction & Timeline Assembly...")
    from scripts.stage2.entity_pipeline import run_pipeline as run_stage2_pipeline
    run_stage2_pipeline()

    # 3. Stage 3: Portfolio Dossier & Dimensional Brief Generation
    print("\n>>> [STEP 3/3] Generating Markdown Dossier Portfolio & Full-Dimensional Brief...")
    from scripts.stage2.generate_dossier_portfolio import build_portfolio
    build_portfolio()

    from scripts.stage2.generate_dimensional_report import generate_report as generate_dim_report
    generate_dim_report()

    from scripts.stage2.generate_html_report import build_dashboard_html
    build_dashboard_html()

    total_duration = round(time.time() - t_start, 2)
    print("\n" + "=" * 70)
    print(f"  ALL PIPELINE STAGES COMPLETED SUCCESSFULLY IN {total_duration}s")
    print("=" * 70)
    print("  Artifacts Generated:")
    print("  - Raw Materials DB:        data/daily/collector.db")
    print("  - Daily Stream Log:        data/daily/YYYY-MM-DD.jsonl")
    print("  - Entity Database:         data/stage2/projects.db (405 projects, 968 events)")
    print("  - Historical Dossier:      data/stage2/historical_repository.json")
    print("  - Historical Knowledge:    docs/stage2/HISTORICAL-INTELLIGENCE-REPOSITORY.md")
    print("  - Project Portfolio:       docs/stage2/PROJECT-DOSSIER-PORTFOLIO.md")
    print("  - Markdown Brief:          docs/stage2/FULL-DIMENSIONAL-INTELLIGENCE-BRIEF.md")
    print("  - Interactive HTML Hub:    docs/stage2/FULL-DIMENSIONAL-INTELLIGENCE-REPORT.html")
    print("  - History Reverse-Lookup:  python scripts/stage2/query_history.py <query>")
    print("=" * 70)

if __name__ == "__main__":
    main()
