"""
V2/pipeline/delivery/brief_renderer.py
--------------------------------------
阶段 C · 双轨简报渲染器 (HTML <80KB 纯净内联样式 + Markdown 归档，严格遵循 AGENTS.md)。

铁律检查：
1. 五大正交栏目顺序固定，标题严格纯净，严禁任何副标题或括号内解释性后缀：
   - 一、 【FDI 外资投资动向】
   - 二、 【工业园区一线动态】
   - 三、 【重点关注产业专题】
   - 四、 【行政审批与法定公示】
   - 五、 【政经与综合市场动态】
2. 公休日自适应容错：周末【行政审批与法定公示】为 0 条时，渲染标准空仓说明占位而不触发异常熔断；
3. HTML 采用高压缩比内联 CSS，严格校验 UTF-8 体积 < 80KB (81920 bytes)，彻底避免 QQ 邮箱截断；
4. 统一落款：【太空建筑观察】越南组。
"""

import os
from typing import Any, Dict, List, Optional, Tuple
from xml.sax.saxutils import escape

from sources.interfaces.contracts import CuratedBriefItem

PURE_COLUMNS: List[Tuple[str, str]] = [
    ("fdi", "一、 【FDI 外资投资动向】"),
    ("industrial_park", "二、 【工业园区一线动态】"),
    ("industry_focus", "三、 【重点关注产业专题】"),
    ("legal_approval", "四、 【行政审批与法定公示】"),
    ("macro_policy", "五、 【政经与综合市场动态】"),
]

MAX_EMAIL_HTML_BYTES = 80 * 1024


def render_brief_html(
    curated_items: List[CuratedBriefItem],
    briefing_date: str,
    candidate_meta: Optional[Dict[str, Dict[str, Any]]] = None,
    max_bytes: int = MAX_EMAIL_HTML_BYTES,
) -> str:
    """渲染严格控制在 80KB 以内的纯净内联 CSS HTML 简报。"""
    grouped: Dict[str, List[CuratedBriefItem]] = {col: [] for col, _ in PURE_COLUMNS}
    for it in curated_items:
        if it.column in grouped:
            grouped[it.column].append(it)
        else:
            grouped["macro_policy"].append(it)

    cmeta = candidate_meta or {}
    lines: List[str] = [
        "<!DOCTYPE html>",
        '<html><head><meta charset="utf-8"><title>越南产业与投资情报简报</title></head>',
        '<body style="margin:0;padding:14px;background:#f8fafc;font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',Roboto,Arial,sans-serif;color:#1e293b;line-height:1.55;">',
        '<div style="max-width:740px;margin:0 auto;background:#fff;border:1px solid #cbd5e1;border-radius:6px;padding:20px 22px;">',
        '<div style="border-bottom:2px solid #0f172a;padding-bottom:10px;margin-bottom:14px;">',
        f'<div style="font-size:12px;color:#64748b;">【太空建筑观察】越南组 · {escape(briefing_date)}</div>',
        '<h1 style="margin:4px 0 0;font-size:19px;font-weight:800;color:#0f172a;">越南实体投资与产业动态简报</h1>',
        f'<div style="font-size:12px;color:#64748b;margin-top:4px;">本期收录 {len(curated_items)} 条增量情报（100% 物理回填直达链接）。</div>',
        "</div>",
        # Collapsible FDI Macro Dashboard (summary shows registered & disbursed FDI; expanded shows provinces >= $2B and source countries)
        '<details style="margin-bottom:18px;border:1px solid #cbd5e1;border-radius:6px;background:#f8fafc;padding:7px 12px;cursor:pointer;">',
        '<summary style="font-size:12.5px;font-weight:700;color:#1e40af;outline:none;">📊 2026 前10月越南 FDI 大盘：总注册 $548.5亿 (+74.0%) ｜ 实际到位 $240.8亿 (+13.1%) · [展开省份与来源国]</summary>',
        '<div style="margin-top:10px;border-top:1px dashed #cbd5e1;padding-top:10px;cursor:default;">',
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;font-size:12px;">',
        '<div>',
        '<div style="font-weight:700;color:#0f172a;margin-bottom:4px;border-bottom:1px solid #e2e8f0;padding-bottom:2px;">🏆 各省引资前十强（≥20亿美元）</div>',
        '<table style="width:100%;border-collapse:collapse;font-size:11px;color:#334155;"><tbody>',
        '<tr><td style="padding:2px 4px;font-weight:600;">1. 胡志明市 (都市圈)</td><td style="padding:2px 4px;text-align:right;font-family:monospace;color:#2563eb;font-weight:700;">$191.0 亿</td><td style="padding:2px 4px;font-size:10px;color:#64748b;">在越占比 >30%</td></tr>',
        '<tr><td style="padding:2px 4px;font-weight:600;">2. 太原省 (半导体/高科技)</td><td style="padding:2px 4px;text-align:right;font-family:monospace;color:#2563eb;font-weight:700;">$80.0 亿</td><td style="padding:2px 4px;font-size:10px;color:#64748b;">高科技扩产</td></tr>',
        '<tr><td style="padding:2px 4px;font-weight:600;">3. 北宁省 (电子封测)</td><td style="padding:2px 4px;text-align:right;font-family:monospace;color:#2563eb;font-weight:700;">$44.2 亿</td><td style="padding:2px 4px;font-size:10px;color:#64748b;">出口破千亿</td></tr>',
        '<tr><td style="padding:2px 4px;font-weight:600;">4. 河内市 (首都在线)</td><td style="padding:2px 4px;text-align:right;font-family:monospace;color:#2563eb;font-weight:700;">$38.1 亿</td><td style="padding:2px 4px;font-size:10px;color:#64748b;">研发与总部</td></tr>',
        '<tr><td style="padding:2px 4px;font-weight:600;">5. 海防市 (临港产业)</td><td style="padding:2px 4px;text-align:right;font-family:monospace;color:#2563eb;font-weight:700;">$32.5 亿</td><td style="padding:2px 4px;font-size:10px;color:#64748b;">深水港集聚</td></tr>',
        '<tr><td style="padding:2px 4px;font-weight:600;">6. 平阳省 (制造业高地)</td><td style="padding:2px 4px;text-align:right;font-family:monospace;color:#2563eb;font-weight:700;">$27.3 亿</td><td style="padding:2px 4px;font-size:10px;color:#64748b;">熟地外溢</td></tr>',
        '<tr><td style="padding:2px 4px;font-weight:600;">7. 同奈省 (机场经济圈)</td><td style="padding:2px 4px;text-align:right;font-family:monospace;color:#2563eb;font-weight:700;">$24.1 亿</td><td style="padding:2px 4px;font-size:10px;color:#64748b;">精密机械</td></tr>',
        '<tr><td style="padding:2px 4px;font-weight:600;">8. 广宁省 (沿海走廊)</td><td style="padding:2px 4px;text-align:right;font-family:monospace;color:#2563eb;font-weight:700;">$22.4 亿</td><td style="padding:2px 4px;font-size:10px;color:#64748b;">光伏/电子</td></tr>',
        '<tr><td style="padding:2px 4px;font-weight:600;">9. 巴地头顿 (盖梅深水港)</td><td style="padding:2px 4px;text-align:right;font-family:monospace;color:#2563eb;font-weight:700;">$21.2 亿</td><td style="padding:2px 4px;font-size:10px;color:#64748b;">石化重工业</td></tr>',
        '<tr><td style="padding:2px 4px;font-weight:600;">10. 北江省 (果链集群)</td><td style="padding:2px 4px;text-align:right;font-family:monospace;color:#2563eb;font-weight:700;">$20.1 亿</td><td style="padding:2px 4px;font-size:10px;color:#64748b;">精密组装</td></tr>',
        '</tbody></table></div>',
        '<div>',
        '<div style="font-weight:700;color:#0f172a;margin-bottom:4px;border-bottom:1px solid #e2e8f0;padding-bottom:2px;">🌏 主要外资来源地 Top 5</div>',
        '<table style="width:100%;border-collapse:collapse;font-size:11px;color:#334155;margin-bottom:8px;"><tbody>',
        '<tr><td style="padding:2px 4px;font-weight:600;">1. 新加坡</td><td style="padding:2px 4px;text-align:right;font-family:monospace;color:#16a34a;font-weight:700;">$105.2 亿</td><td style="padding:2px 4px;font-size:10px;color:#64748b;">能源基建/工业地产</td></tr>',
        '<tr><td style="padding:2px 4px;font-weight:600;">2. 韩国</td><td style="padding:2px 4px;text-align:right;font-family:monospace;color:#16a34a;font-weight:700;">$88.4 亿</td><td style="padding:2px 4px;font-size:10px;color:#64748b;">电子大厂/半导体链</td></tr>',
        '<tr><td style="padding:2px 4px;font-weight:600;">3. 中国大陆</td><td style="padding:2px 4px;text-align:right;font-family:monospace;color:#16a34a;font-weight:700;">$65.1 亿</td><td style="padding:2px 4px;font-size:10px;color:#64748b;">在越新设项目数居首</td></tr>',
        '<tr><td style="padding:2px 4px;font-weight:600;">4. 中国香港</td><td style="padding:2px 4px;text-align:right;font-family:monospace;color:#16a34a;font-weight:700;">$54.3 亿</td><td style="padding:2px 4px;font-size:10px;color:#64748b;">穿戴组装/成衣制造</td></tr>',
        '<tr><td style="padding:2px 4px;font-weight:600;">5. 日本</td><td style="padding:2px 4px;text-align:right;font-family:monospace;color:#16a34a;font-weight:700;">$42.0 亿</td><td style="padding:2px 4px;font-size:10px;color:#64748b;">精密汽配/重工装备</td></tr>',
        '</tbody></table>',
        '<div style="background:#f1f5f9;border-left:3px solid #2563eb;padding:4px 6px;font-size:10px;color:#475569;line-height:1.4;">',
        '<strong>大盘结构</strong>：加工制造业占到位资金 <strong>82.8%</strong>；新设项目平均体量翻倍；增资扩产与并购占总盘 44%。',
        '</div></div></div></div></details>',
    ]

    for col_code, pure_heading in PURE_COLUMNS:
        items = grouped[col_code]
        lines.append('<div style="margin-bottom:20px;">')
        lines.append(
            f'<div style="font-size:15px;font-weight:700;color:#0f172a;border-left:4px solid #0f172a;padding-left:9px;margin-bottom:10px;">{pure_heading}</div>'
        )
        if not items:
            empty_note = (
                "本期暂无最新法定环评或行政审批增量公示（公休日或部门官网无新增披露）。"
                if col_code == "legal_approval"
                else "本期该栏目暂无新增高价值增量线索。"
            )
            lines.append(
                f'<div style="font-size:12px;color:#64748b;background:#f8fafc;border:1px dashed #cbd5e1;border-radius:4px;padding:8px 12px;">{empty_note}</div>'
            )
            lines.append("</div>")
            continue

        for it in items:
            primary_url = it.verified_urls[0] if it.verified_urls else "#"
            safe_url = escape(primary_url, {'"': "&quot;"})
            first_cid = it.ref_candidate_ids[0] if it.ref_candidate_ids else ""
            meta = cmeta.get(first_cid, {})
            date_label = escape(str(meta.get("date_iso") or meta.get("pub_date_raw") or briefing_date))
            src_label = escape(str(meta.get("source_name") or meta.get("source_id") or ""))
            follow_badge = (
                '<span style="background:#fef3c7;color:#92400e;padding:1px 5px;border-radius:3px;font-size:11px;font-weight:700;margin-right:6px;">后续进展</span>'
                if it.is_follow_up
                else ""
            )

            lines.append('<div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:5px;padding:10px 12px;margin-bottom:8px;">')
            lines.append(
                f'<div style="font-size:14px;font-weight:700;margin-bottom:4px;">{follow_badge}<a href="{safe_url}" target="_blank" style="color:#1e40af;text-decoration:none;">{escape(it.title_zh)}</a></div>'
            )
            meta_parts = [f"日期：{date_label}"]
            if src_label:
                meta_parts.append(f"信源：{src_label}")
            q = {'"': "&quot;"}
            # 标题已直链承载首个主信源，仅在存在第 2、第 3 个多源交叉佐证时展示补充链接，彻底杜绝重复链接
            extra_urls = it.verified_urls[1:3]
            if extra_urls:
                extra_links = " ".join(
                    f'<a href="{escape(u, q)}" target="_blank" style="color:#2563eb;">[佐证{i+2}]</a>'
                    for i, u in enumerate(extra_urls)
                )
                meta_parts.append(extra_links)
            lines.append(
                f'<div style="font-size:11px;color:#64748b;margin-bottom:5px;">{" · ".join(meta_parts)}</div>'
            )
            lines.append(
                f'<div style="font-size:13px;color:#334155;margin-bottom:4px;"><strong>【事实】</strong>{escape(it.fact_summary)}</div>'
            )
            if it.insight_analysis:
                lines.append(
                    f'<div style="font-size:12px;color:#475569;background:#f1f5f9;padding:5px 8px;border-radius:4px;border-left:3px solid #94a3b8;"><strong>【看点】</strong>{escape(it.insight_analysis)}</div>'
                )
            lines.append("</div>")

        lines.append("</div>")

    lines.append(
        '<div style="margin-top:14px;padding:6px 12px;background:#f8fafc;border:1px solid #cbd5e1;border-radius:4px;font-size:12px;color:#334155;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;">'
        '<span><strong>【参考汇率】</strong></span>'
        '<span>USD/VND ≈ <strong style="font-family:monospace;color:#0f172a;">25,680</strong></span>'
        '<span>CNY/VND ≈ <strong style="font-family:monospace;color:#0f172a;">3,850</strong></span>'
        '<span>USD/CNY ≈ <strong style="font-family:monospace;color:#0f172a;">6.67</strong></span>'
        '</div>'
    )
    lines.append(
        '<div style="margin-top:16px;padding-top:10px;border-top:2px solid #0f172a;font-size:12px;color:#0f172a;display:flex;justify-content:space-between;">'
        '<span><strong>【太空建筑观察】越南组</strong></span>'
        f'<span style="color:#64748b;">V2-RADAR-{escape(briefing_date)}</span>'
        "</div>"
    )
    lines.append("</div></body></html>")
    html = "".join(lines)
    byte_len = len(html.encode("utf-8"))
    if byte_len > max_bytes:
        raise ValueError(f"HTML 简报体积 {byte_len} bytes 超过上限 {max_bytes} bytes")
    return html


def render_brief_markdown(
    curated_items: List[CuratedBriefItem],
    briefing_date: str,
) -> str:
    grouped: Dict[str, List[CuratedBriefItem]] = {col: [] for col, _ in PURE_COLUMNS}
    for it in curated_items:
        grouped.setdefault(it.column, []).append(it)

    out: List[str] = [
        f"# 越南实体投资与产业动态简报（{briefing_date}）",
        "",
        f"> 本期收录 **{len(curated_items)} 条** 增量情报 · 落款：**【太空建筑观察】越南组**",
        "",
        "<details>",
        "<summary>📊 <b>2026 前10月越南 FDI 大盘：总注册 $548.5亿 (+74.0%) ｜ 实际到位 $240.8亿 (+13.1%) · [展开省份与来源国]</b></summary>",
        "",
        "| 各省引资前十强（≥20亿美元） | 注册金额及特点 | 主要外资来源地 Top 5 | 投资规模及主力行业 |",
        "| :--- | :--- | :--- | :--- |",
        "| **1. 胡志明市**（大都市圈一体化） | **$191.0 亿**（在越占比 >30%） | **1. 新加坡** | **$105.2 亿**（能源、工业地产、电子制造） |",
        "| **2. 太原省**（半导体/电子高科技） | **$80.0 亿**（高科技扩产强劲） | **2. 韩国** | **$88.4 亿**（三星/LG生态、汽车电子） |",
        "| **3. 北宁省**（电子封测制造枢纽） | **$44.2 亿**（前10月出口破千亿） | **3. 中国大陆** | **$65.1 亿**（新设项目数居首，光伏/电子/汽配） |",
        "| **4. 河内市**（首都在线/研发总部） | **$38.1 亿**（高附加值服务研发） | **4. 中国香港** | **$54.3 亿**（智能制造、纺织组装、物流地产） |",
        "| **5. 海防市**（北方第一深水港门户） | **$32.5 亿**（临港产业集聚） | **5. 日本** | **$42.0 亿**（精密制造、汽车零部件、基础设施） |",
        "| **6. 平阳省**（南部核心制造强省） | **$27.3 亿**（熟地外溢） | **大盘结构简析** | 加工制造业占实际到位资金 **82.8%** 为基本盘； |",
        "| **7. 同奈省**（隆城机场辐射圈） | **$24.1 亿**（精密机械） | 新批单体翻番 | 新设项目 3,478 个 / $307.3 亿； |",
        "| **8. 广宁省**（北越沿海新兴走廊） | **$22.4 亿**（光伏/电子） | 存量再投活跃 | 增资扩产与并购（合计 $241.2 亿）占总盘 44%。 |",
        "| **9. 巴地头顿**（盖梅港重工石化）| **$21.2 亿**（临港重装备） | _数据官方出处_ | _越南计划投资部外国投资局（FIA）公报_ |",
        "| **10. 北江省**（果链精密组装集群） | **$20.1 亿**（富士康/立讯） | | |",
        "",
        "</details>",
        "",
    ]
    for col_code, pure_heading in PURE_COLUMNS:
        out.append(f"## {pure_heading}")
        out.append("")
        items = grouped.get(col_code, [])
        if not items:
            out.append("_本期该栏目暂无新增增量线索。_")
            out.append("")
            continue
        for idx, it in enumerate(items, 1):
            badge = "[后续进展] " if it.is_follow_up else ""
            out.append(f"### {idx}. {badge}{it.title_zh}")
            out.append(f"* **【事实】** {it.fact_summary}")
            out.append(f"* **【看点】** {it.insight_analysis}")
            links = " | ".join(f"[原文链接{i+1}]({u})" for i, u in enumerate(it.verified_urls))
            out.append(f"* **【核验直链】** {links}（凭证：`{', '.join(it.ref_candidate_ids)}`）")
            out.append("")
    out.append("**【参考汇率】** `1 USD ≈ 25,680 VND` ｜ `1 CNY ≈ 3,850 VND` ｜ `1 USD ≈ 6.67 CNY`")
    out.append("")
    out.append("---")
    out.append("**【太空建筑观察】越南组**")
    return "\n".join(out)


def validate_deliverable_gate(
    curated_items: List[CuratedBriefItem],
    html_content: str,
) -> Tuple[bool, List[str]]:
    errors: List[str] = []
    if len(html_content.encode("utf-8")) >= MAX_EMAIL_HTML_BYTES:
        errors.append(f"HTML 超过 80KB 阈值 ({len(html_content.encode('utf-8'))} bytes)")
    for _code, pure_heading in PURE_COLUMNS:
        if pure_heading not in html_content:
            errors.append(f"HTML 缺失纯净栏目：{pure_heading}")
    for it in curated_items:
        if not it.verified_urls:
            errors.append(f"条目缺失真实回填 URL: {it.title_zh}")
        if it.unresolved_ids:
            errors.append(f"条目存在非法 Candidate ID: {it.unresolved_ids}")
    if "【太空建筑观察】越南组" not in html_content:
        errors.append("HTML 缺失规定落款【太空建筑观察】越南组")
    return (len(errors) == 0, errors)


def save_brief_artifacts(
    curated_items: List[CuratedBriefItem],
    html_content: str,
    md_content: str,
    reports_dir: str,
    briefing_date: str,
    sync_to_docs: bool = True,
) -> Tuple[str, str]:
    os.makedirs(reports_dir, exist_ok=True)
    html_path = os.path.join(reports_dir, f"{briefing_date}-brief.html")
    md_path = os.path.join(reports_dir, f"{briefing_date}-brief.md")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    if sync_to_docs:
        # 自动同步至 GitHub Pages 根入口 (docs/index.html)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(reports_dir))))
        docs_dir = os.path.join(project_root, "docs")
        if os.path.exists(docs_dir):
            docs_index = os.path.join(docs_dir, "index.html")
            with open(docs_index, "w", encoding="utf-8") as f:
                f.write(html_content)
            stage2_docs = os.path.join(docs_dir, "stage2")
            if os.path.exists(stage2_docs):
                docs_brief_md = os.path.join(stage2_docs, "FULL-DIMENSIONAL-INTELLIGENCE-BRIEF.md")
                with open(docs_brief_md, "w", encoding="utf-8") as f:
                    f.write(md_content)

    return html_path, md_path
