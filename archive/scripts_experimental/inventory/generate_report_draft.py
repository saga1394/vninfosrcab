import json
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('data/inventory/batch_2_raw_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

meta = data['meta']
sources = data['sources']

print(f"Loaded {len(sources)} sources.")

# Group sources
categories = {
    "Vietnam National General": ("一、 越南全国综合媒体 (12 项)", []),
    "Vietnam Finance & Industry": ("二、 越南财经与工业专业媒体 (10 项)", []),
    "Vietnam Local Media": ("三、 越南地方省市报媒 (8 项)", []),
    "International Wire": ("四、 国际主流通讯社 (3 项)", []),
    "Singapore Media": ("五、 新加坡媒体 (3 项)", []),
    "Japan Media": ("六、 日本媒体 (1 项)", []),
    "Korea Media": ("七、 韩国媒体 (8 项)", []),
    "Taiwan Media": ("八、 台湾媒体 (2 项)", []),
    "India Media": ("九、 印度媒体 (2 项)", []),
    "Industry Specialized": ("十、 行业专业与垂直媒体 (3 项)", []),
    "Other & Chinese Original": ("十一、 其他地区与中文原创 (3 项)", []),
}

for s in sources:
    cat = s["category"]
    if cat in categories:
        categories[cat][1].append(s)
    else:
        print("Unknown category:", cat)

for cat_k, (cat_title, cat_sources) in categories.items():
    print(f"{cat_title}: {len(cat_sources)} sources")
