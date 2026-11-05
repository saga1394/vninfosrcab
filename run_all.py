# -*- coding: utf-8 -*-
"""
Master Entry Point for Vietnam Industrial & Investment Intelligence Pipeline.
Orchestrates Stage 1 (Collection), Stage 2 (Entity Alignment), Automated Curation,
Multi-Channel Publishing, Pre-Flight Quality Gate, and Safe Delivery.

Usage:
    python run_all.py                  # Full run: Collect + Process + QA Audit
    python run_all.py --skip-collect   # Fast run: Process existing DB + QA Audit
    python run_all.py --send-email     # Production run: Send email to team if QA passes
    python run_all.py --dry-run        # Audit mode: Full run with Quality Gate, skips email
"""

import sys
from run_daily_pipeline import main

if __name__ == "__main__":
    main()
