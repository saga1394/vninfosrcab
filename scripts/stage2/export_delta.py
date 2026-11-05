# -*- coding: utf-8 -*-
"""
Forwarder for Delta Candidate Extraction.
Delegates directly to scripts/pipeline/extract_delta.py.
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.pipeline.extract_delta import extract_delta_candidates

if __name__ == "__main__":
    extract_delta_candidates()
