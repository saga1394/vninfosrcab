# -*- coding: utf-8 -*-
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from scripts.stage2.generate_html_report import CURATED_INTELLIGENCE

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

print(f"Total curated items: {len(CURATED_INTELLIGENCE)}")
vn_count = 0
non_vn_count = 0

for i, it in enumerate(CURATED_INTELLIGENCE):
    t = it['title']
    f = it['fact']
    sub = it.get('sub_tag', '')
    cat = it['category']
    
    # Check if purely foreign without Vietnam operation
    purely_foreign = False
    if any(non in t for non in ['日本爱信', '东京电子（TEL）', '美满电子（Marvell）', 'SK 海力士', '亚洲智能制造装备博览会（FIX 2026）', '中国新能源车企加速开拓东南亚与日韩']):
        if '越南' not in t and '在越' not in t and '越南' not in f and '在越' not in f:
            purely_foreign = True

    if purely_foreign:
        print(f"❌ [纯海外/需剥离] [{cat}] [{sub}] {t}")
        non_vn_count += 1
    else:
        print(f"✅ [越南境内/强关联] [{cat}] [{sub}] {t}")
        vn_count += 1

print(f"\nSummary: {vn_count} Vietnam-anchored, {non_vn_count} Purely Foreign.")
