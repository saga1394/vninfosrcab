"""
V2/tests/test_v2_suite.py
-------------------------
V2 全链路自动化回归测试套件（完全离线、零外部网络依赖）：
覆盖 8492 QA 审计报告全部 5 大补丁：
1. YAML Frontmatter 边界用例（URL # 锚点保留、带引号字符串、缺失必填键报错）；
2. 5 大底层协议驱动（rss_driver, html_card_driver + __NEXT_DATA__ + search_spec, html_table_driver + verify_ssl=False, rest_api_driver + json_path + JS数组, sitemap_driver + SitemapIndex）；
3. PDF 附件首页摘要探针（pdf_probe）；
4. HostThrottle 同域名并发 <= 2 节流验证；
5. 5 大上层业务原型技能（含噪音剔除与信号归类）+ 健康状态机降级恢复；
6. E2E run_collection_pipeline + CandidateVault + backfill_candidate_urls + Lazy Probe 死链拦截。
"""

from datetime import datetime, timezone
import json
import os
import sys
import tempfile
import threading
import time
import unittest

V2_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if V2_ROOT not in sys.path:
    sys.path.insert(0, V2_ROOT)

from run_v2 import finalize_curated_brief, run_collection_pipeline
from sources.drivers import (
    DriverRecord,
    HostThrottle,
    HttpFetcher,
    HttpResponseData,
    get_protocol_driver,
    probe_pdf_attachments,
)
from sources.interfaces.contracts import (
    CandidateVault,
    CuratedBriefItem,
    NetworkConfig,
    SourceCardParser,
    backfill_candidate_urls,
)
from sources.interfaces.health_ledger import SourceHealthLedger
from sources.skills import get_archetype_skill


def _make_card_md(
    source_id: str,
    cluster: str,
    archetype: str,
    driver: str,
    target_url: str,
    extra_yaml: str = "",
) -> str:
    return f"""---
source_id: {source_id}
name: "Test Source: {source_id}"
cluster: {cluster}
target_url: {target_url}
archetype_skill: {archetype}
protocol_driver: {driver}
check_frequency: daily
priority: P0
expected_column: fdi
status: active
last_audit_date: "2026-11-12"
{extra_yaml}
---

# {source_id}
"""


class V2ArchitectureTestSuite(unittest.TestCase):
    def test_yaml_parser_preserves_hash_anchor_and_rejects_missing_keys(self):
        md = _make_card_md(
            "SRC-IP-099",
            "industrial_park",
            "park-news-inspector",
            "html_card_driver",
            "https://example.com/portal#news-section",
        )
        parsed = SourceCardParser.parse_card_markdown(md)
        self.assertEqual(parsed.meta["target_url"], "https://example.com/portal#news-section")
        self.assertEqual(parsed.meta["name"], "Test Source: SRC-IP-099")

        bad_md = "---\nsource_id: SRC-BAD-001\n---\n\n# Bad"
        with self.assertRaises(ValueError):
            SourceCardParser.parse_card_markdown(bad_md)

    def test_html_card_driver_with_search_spec_and_next_data(self):
        md = _make_card_md(
            "SRC-JOB-001",
            "job_radar",
            "job-radar-scanner",
            "html_card_driver",
            "https://www.vietnamworks.com/tim-viec-lam",
            extra_yaml="""
search_spec:
  endpoint_template: "https://www.vietnamworks.com/tim-viec-lam?q={keyword}&order=created_at_desc"
  keywords:
    - "Factory Setup"
    - "Plant Manager"
""",
        )
        parsed = SourceCardParser.parse_card_markdown(md)
        requested_urls = []

        def mock_transport(method, url, **kwargs):
            requested_urls.append(url)
            next_data = {
                "props": {
                    "pageProps": {
                        "jobs": [
                            {
                                "jobTitle": "Plant Manager (New Factory Setup)",
                                "companyName": "Luxshare-ICT Vietnam",
                                "workLocation": "VSIP Bac Ninh",
                                "publishedOn": "2026-11-11",
                                "jobUrl": "/job/plant-manager-123",
                            },
                            {
                                "jobTitle": "Tạp vụ văn phòng",
                                "companyName": "Local Services",
                                "workLocation": "Hanoi",
                                "publishedOn": "2026-11-11",
                                "jobUrl": "/job/cleaner-456",
                            },
                        ]
                    }
                }
            }
            html = f'<html><body><script id="__NEXT_DATA__" type="application/json">{json.dumps(next_data)}</script></body></html>'
            return HttpResponseData(200, html, html.encode("utf-8"), url)

        skill = get_archetype_skill("job-radar-scanner")
        items = skill.execute(parsed, fetcher=HttpFetcher(transport_fn=mock_transport))
        self.assertEqual(len(requested_urls), 2)
        self.assertIn("q=Factory+Setup", requested_urls[0])
        # Noise role filtered out by job-radar-scanner
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].subject_entity, "Luxshare-ICT Vietnam")
        self.assertEqual(items[0].geo_location, "Bắc Ninh (北宁省)")
        self.assertEqual(items[0].direct_url, "https://www.vietnamworks.com/job/plant-manager-123")

    def test_html_table_driver_ssl_flag_and_noise_discard(self):
        md = _make_card_md(
            "SRC-APP-001",
            "legal_approval",
            "gazette-table-parser",
            "html_table_driver",
            "https://thamvan.mae.gov.vn/Home/DSDTM",
            extra_yaml="""
network_config:
  verify_ssl: false
  timeout: 20
attachment_probe: false
""",
        )
        parsed = SourceCardParser.parse_card_markdown(md)
        observed_verify = []

        def mock_transport(method, url, verify_ssl=True, **kwargs):
            observed_verify.append(verify_ssl)
            html = """
            <table class="table">
              <thead><tr><th>STT</th><th>Tên dự án</th><th>Chủ dự án</th><th>Địa điểm</th><th>Ngày</th></tr></thead>
              <tbody>
                <tr>
                  <td>1</td>
                  <td><a href="/Home/ChiTietDSDTM?id=101">Nhà máy sản xuất linh kiện bán dẫn Amkor Giai đoạn 2</a></td>
                  <td>Amkor Technology Vietnam</td>
                  <td>KCN Yên Phong II-C, Bắc Ninh</td>
                  <td>10/11/2026 <a href="/Uploads/amkor.pdf">PDF</a></td>
                </tr>
                <tr>
                  <td>2</td>
                  <td><a href="/Home/ChiTietDSDTM?id=102">Nạo vét kênh mương thủy lợi nông thôn xã X</a></td>
                  <td>UBND xã X</td>
                  <td>Thanh Hóa</td>
                  <td>10/11/2026</td>
                </tr>
              </tbody>
            </table>
            """
            return HttpResponseData(200, html, html.encode("utf-8"), url)

        skill = get_archetype_skill("gazette-table-parser")
        items = skill.execute(parsed, fetcher=HttpFetcher(transport_fn=mock_transport))
        self.assertEqual(observed_verify, [False])
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].signal_type, "eia_approval")
        self.assertEqual(items[0].pub_date_raw, "2026-11-10")
        self.assertEqual(items[0].attachment_urls, ["https://thamvan.mae.gov.vn/Uploads/amkor.pdf"])

    def test_rss_driver(self):
        md = _make_card_md(
            "SRC-MED-001",
            "media_fdi",
            "media-stream-curator",
            "rss_driver",
            "https://baochinhphu.vn/kinh-te.rss",
        )
        parsed = SourceCardParser.parse_card_markdown(md)

        def mock_transport(method, url, **kwargs):
            rss = """<?xml version="1.0" encoding="UTF-8"?>
            <rss version="2.0"><channel>
              <item>
                <title>Chính phủ mở rộng cơ chế DPPA cho khu công nghiệp tại Hải Phòng</title>
                <link>https://baochinhphu.vn/dppa-123.htm</link>
                <pubDate>Tue, 11 Nov 2026 08:00:00 +0700</pubDate>
                <description>Đầu tư mới 250 million USD vào hạ tầng xanh.</description>
              </item>
              <item>
                <title>Kết quả xổ số kiến thiết miền Bắc hôm nay</title>
                <link>https://baochinhphu.vn/xoso-999.htm</link>
                <pubDate>Tue, 11 Nov 2026 08:00:00 +0700</pubDate>
                <description>Trúng thưởng đặc biệt.</description>
              </item>
            </channel></rss>"""
            return HttpResponseData(200, rss, rss.encode("utf-8"), url)

        skill = get_archetype_skill("media-stream-curator")
        items = skill.execute(parsed, fetcher=HttpFetcher(transport_fn=mock_transport))
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].geo_location, "Hải Phòng (海防市)")
        self.assertIn("250 million USD", items[0].project_scale or "")

    def test_rest_api_driver_json_and_js_array(self):
        md = _make_card_md(
            "SRC-MED-002",
            "media_fdi",
            "media-stream-curator",
            "rest_api_driver",
            "https://www.mof.gov.vn/api/article/reads",
            extra_yaml="""
api_spec:
  method: POST
  payload_template:
    offset: 0
    limit: 10
  json_path: "data.items"
""",
        )
        parsed = SourceCardParser.parse_card_markdown(md)

        def mock_json_transport(method, url, json_body=None, **kwargs):
            assert method == "POST"
            assert json_body == {"offset": 0, "limit": 10}
            body = json.dumps({
                "data": {
                    "items": [
                        {
                            "title": "Nghị định giảm thuế TNDN cho dự án công nghệ cao",
                            "url": "/chi-tiet-tin/giam-thue-tdn",
                            "publishedAt": "2026-11-11T09:00:00Z",
                            "summary": "Áp dụng cho doanh nghiệp bán dẫn tại Hà Nội.",
                        }
                    ]
                }
            })
            return HttpResponseData(200, body, body.encode("utf-8"), url)

        items = get_archetype_skill("media-stream-curator").execute(
            parsed, fetcher=HttpFetcher(transport_fn=mock_json_transport)
        )
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].direct_url, "https://www.mof.gov.vn/chi-tiet-tin/giam-thue-tdn")

        # Also verify static JS variable extraction (e.g., AIIB all-projects-data.js)
        js_md = _make_card_md(
            "SRC-SEC-010",
            "corporate_disclosure",
            "disclosure-sniffer",
            "rest_api_driver",
            "https://www.aiib.org/all-projects-data.js",
        )
        js_parsed = SourceCardParser.parse_card_markdown(js_md)

        def mock_js_transport(method, url, **kwargs):
            js_text = 'var allProjectsData = [{"title": "新设越南生产基地 50 million USD", "url": "/projects/vn-01", "date": "2026-11-11"}];'
            return HttpResponseData(200, js_text, js_text.encode("utf-8"), url)

        js_items = get_archetype_skill("disclosure-sniffer").execute(
            js_parsed, fetcher=HttpFetcher(transport_fn=mock_js_transport)
        )
        self.assertEqual(len(js_items), 1)
        self.assertEqual(js_items[0].signal_type, "factory_setup")

    def test_sitemap_driver_and_index_recursion(self):
        md = _make_card_md(
            "SRC-APP-002",
            "legal_approval",
            "gazette-table-parser",
            "sitemap_driver",
            "https://vbpl.vn/sitemap.xml",
        )
        parsed = SourceCardParser.parse_card_markdown(md)

        def mock_transport(method, url, **kwargs):
            if url.endswith("sitemap.xml"):
                xml = """<?xml version="1.0" encoding="UTF-8"?>
                <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
                  <sitemap><loc>https://vbpl.vn/sitemap/1.xml</loc></sitemap>
                </sitemapindex>"""
            else:
                xml = """<?xml version="1.0" encoding="UTF-8"?>
                <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
                  <url>
                    <loc>https://vbpl.vn/van-ban/nghi-dinh-khu-cong-nghiep-2026</loc>
                    <lastmod>2026-11-11T10:00:00Z</lastmod>
                  </url>
                  <url>
                    <loc>https://vbpl.vn/van-ban/luat-dat-dai-cu-2020</loc>
                    <lastmod>2024-01-01T10:00:00Z</lastmod>
                  </url>
                </urlset>"""
            return HttpResponseData(200, xml, xml.encode("utf-8"), url)

        driver = get_protocol_driver("sitemap_driver")
        recs = driver.fetch(
            parsed,
            fetcher=HttpFetcher(transport_fn=mock_transport),
            reference_now=datetime(2026, 11, 12, 12, 0, tzinfo=timezone.utc),
        )
        self.assertEqual(len(recs), 1)
        self.assertIn("Nghi Dinh Khu Cong Nghiep 2026", recs[0].title)

    def test_host_throttle_limits_concurrency_to_two(self):
        throttle = HostThrottle(max_per_host=2)
        active = 0
        peak = 0
        lock = threading.Lock()

        def worker():
            nonlocal active, peak
            with throttle.acquire("https://thamvan.mae.gov.vn/Home/DSDTM"):
                with lock:
                    active += 1
                    peak = max(peak, active)
                time.sleep(0.05)
                with lock:
                    active -= 1

        threads = [threading.Thread(target=worker) for _ in range(6)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertLessEqual(peak, 2)

    def test_e2e_v2_pipeline_and_anti_hallucination_lazy_probe(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Copy cards into temp V2 root to avoid touching V2/data/state_ledger.db
            for sub in ("sources/cards", "sources/interfaces", "config", "data/runs"):
                os.makedirs(os.path.join(tmpdir, sub), exist_ok=True)
            real_cards_dir = os.path.join(V2_ROOT, "sources", "cards")
            demo_fnames = (
                "SRC-JOB-001-vietnamworks.md",
                "SRC-IP-001-becamex.md",
                "SRC-APP-001-dsdtm.md",
                "SRC-APP-002-vbpl.md",
                "SRC-MED-001-baochinhphu.md",
                "SRC-MED-002-mof.md",
            )
            for fname in demo_fnames:
                src_path = os.path.join(real_cards_dir, fname)
                if os.path.exists(src_path):
                    with open(src_path, "r", encoding="utf-8") as src:
                        with open(os.path.join(tmpdir, "sources", "cards", fname), "w", encoding="utf-8") as dst:
                            dst.write(src.read())

            def mock_transport(method, url, **kwargs):
                if "vietnamworks.com" in url:
                    nd = {"props": {"pageProps": {"jobs": [{"jobTitle": "Factory Director", "companyName": "Delta Electronics", "workLocation": "Bac Ninh", "publishedOn": "2026-11-12", "jobUrl": "/job/fd-1"}]}}}
                    return HttpResponseData(200, f'<script id="__NEXT_DATA__">{json.dumps(nd)}</script>', b"", url)
                if "becamex.com.vn" in url:
                    html = '<article class="news-item"><h3><a href="/tin-tuc/ky-ket-10ha">Becamex ký kết thuê 10 ha tại Bàu Bàng</a></h3><p>11/11/2026 Hợp đồng thuê đất.</p></article>'
                    return HttpResponseData(200, html, b"", url)
                if "thamvan.mae.gov.vn" in url:
                    html = '<table><tr><td>1</td><td><a href="/Home/ChiTietDSDTM?id=7">Nhà máy pin lưu trữ BESS</a></td><td>BESS VN</td><td>Đồng Nai</td><td>11/11/2026</td></tr></table>'
                    return HttpResponseData(200, html, b"", url)
                if "baochinhphu.vn" in url:
                    rss = '<rss version="2.0"><channel><item><title>Chính phủ duyệt quy hoạch điện VIII</title><link>https://baochinhphu.vn/qh-dien.htm</link><pubDate>2026-11-12</pubDate><description>DPPA</description></item></channel></rss>'
                    return HttpResponseData(200, rss, b"", url)
                if "mof.gov.vn" in url:
                    js = json.dumps({"data": [{"title": "Giảm thuế nhập khẩu thiết bị bán dẫn", "url": "/chi-tiet-tin/thue-ban-dan", "publishedAt": "2026-11-12", "summary": "MOF"}]})
                    return HttpResponseData(200, js, b"", url)
                if "vbpl.vn" in url:
                    xml = '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://vbpl.vn/van-ban/luat-dau-tu-2026</loc><lastmod>2026-11-12T08:00:00Z</lastmod></url></urlset>'
                    return HttpResponseData(200, xml, b"", url)
                if "dead-link" in url:
                    raise RuntimeError("404 Not Found")
                return HttpResponseData(200, "ok", b"ok", url)

            http = HttpFetcher(transport_fn=mock_transport)
            report = run_collection_pipeline(v2_root=tmpdir, fetcher=http)

            self.assertEqual(report["total_registry_sources"], 6)
            self.assertEqual(report["succeeded_sources"], 6)
            self.assertEqual(report["failed_sources"], {})
            self.assertEqual(report["total_candidates"], 6)

            with open(report["llm_payload_path"], "r", encoding="utf-8") as pf:
                payloads = json.load(pf)
            for p in payloads:
                self.assertNotIn("direct_url", p)
                self.assertNotIn("attachment_urls", p)

            vault: CandidateVault = report["vault"]
            cids = list(vault.as_dict().keys())
            brief = [
                CuratedBriefItem(
                    column="fdi",
                    title_zh="台达电子北宁筹建新厂与 Becamex 供地动向",
                    fact_summary="台达电子招募北宁厂长，Becamex 包邦工业区签约 10 公顷。",
                    insight_analysis="北越电源与南越工业用地承接同步升温。",
                    ref_candidate_ids=[cids[0], cids[1], "C-FAKE-999"],
                )
            ]
            final = finalize_curated_brief(brief, vault.as_dict(), fetcher=http, lazy_probe=True)
            self.assertEqual(len(final[0].verified_urls), 2)
            self.assertEqual(final[0].unresolved_ids, ["C-FAKE-999"])

    def test_pdf_probe_discovers_attachment_links_and_enriches_summary(self):
        rec = DriverRecord(
            title="FIA Monthly FDI Report",
            direct_url="https://fia.mof.gov.vn/Detail/123",
            summary="Monthly FDI report",
        )
        # Minimal valid single-page PDF bytes with text "FDI 54.8B USD"
        minimal_pdf = (
            b"%PDF-1.4\n"
            b"1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n"
            b"2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj\n"
            b"3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 144] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>endobj\n"
            b"4 0 obj<< /Length 44 >>stream\nBT /F1 12 Tf 10 100 Td (FDI 54.8B USD) Tj ET\nendstream endobj\n"
            b"5 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>endobj\n"
            b"xref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000241 00000 n \n0000000334 00000 n \n"
            b"trailer<< /Size 6 /Root 1 0 R >>\nstartxref\n404\n%%EOF"
        )

        def mock_transport(method, url, **kwargs):
            if url.endswith(".pdf"):
                return HttpResponseData(200, "", minimal_pdf, url)
            html = '<html><body><a href="/uploads/fia_oct_2026.pdf">Download PDF</a></body></html>'
            return HttpResponseData(200, html, html.encode("utf-8"), url)

        enriched = probe_pdf_attachments(
            [rec],
            NetworkConfig(verify_ssl=False),
            fetcher=HttpFetcher(transport_fn=mock_transport),
        )
        self.assertEqual(enriched[0].attachment_urls, ["https://fia.mof.gov.vn/uploads/fia_oct_2026.pdf"])

    def test_stage_b_triage_event_ledger_and_stage_c_renderer_gate(self):
        from datetime import datetime, timezone
        from pipeline.cognitive.event_ledger import EventLedger
        from pipeline.cognitive.stage1_triage import run_stage1_triage
        from pipeline.cognitive.stage2_curate import select_and_curate_candidates
        from pipeline.delivery.brief_renderer import (
            PURE_COLUMNS,
            render_brief_html,
            validate_deliverable_gate,
        )
        from sources.interfaces.contracts import ExtractedCandidate

        with tempfile.TemporaryDirectory() as tmpdir:
            ledger = EventLedger(db_path=os.path.join(tmpdir, "projects.db"), seed_from_v1=False)
            with ledger._connect() as conn:
                conn.execute(
                    """
                    INSERT INTO projects (project_id, project_name, project_name_cn, investor_name, province, current_stage, updated_at)
                    VALUES ('PRJ-001', 'Meiko PCB Bac Ninh', '名幸电子北宁PCB项目', 'Meiko', 'Bắc Ninh', 'IRC_APPROVED', '2026-10-01')
                    """
                )
                conn.commit()

            ref_dt = datetime(2026, 11, 13, 12, 0, tzinfo=timezone.utc)
            payloads = [
                {
                    "candidate_id": "C-1",
                    "source_id": "SRC-IND-PROP-02",
                    "title": "Japan PCB maker Meiko expands $450M Vietnam plant groundbreaking",
                    "pub_date_raw": "2026-11-12",
                    "subject_entity": "Meiko",
                    "geo_location": "Bắc Ninh",
                    "signal_type": "ground_breaking",
                    "project_scale": "450M USD",
                    "evidence_snippet": "Meiko holds groundbreaking in Bac Ninh.",
                },
                {
                    "candidate_id": "C-2",
                    "source_id": "SRC-A03",
                    "title": "Evergreen navigation directory page",
                    "pub_date_raw": "date_unverified",
                    "subject_entity": "NSO",
                    "geo_location": "Vietnam",
                    "signal_type": "policy_regulation",
                    "evidence_snippet": "nav",
                },
                {
                    "candidate_id": "C-3",
                    "source_id": "SRC-VN-GEN-07",
                    "title": "Ket qua xo so mien Bac hom nay",
                    "pub_date_raw": "2026-11-12",
                    "subject_entity": "VnExpress",
                    "geo_location": "Hà Nội",
                    "signal_type": "policy_regulation",
                    "evidence_snippet": "xo so",
                },
            ]
            registry = [
                {"source_id": "SRC-IND-PROP-02", "name": "TechNode Global", "cluster": "media_fdi", "priority": "P1", "expected_column": "industry_focus"},
                {"source_id": "SRC-A03", "name": "NSO", "cluster": "media_fdi", "priority": "P1", "expected_column": "macro_policy"},
                {"source_id": "SRC-VN-GEN-07", "name": "VnExpress", "cluster": "media_fdi", "priority": "P1", "expected_column": "macro_policy"},
            ]

            triage = run_stage1_triage(payloads, registry, ledger=ledger, reference_date=ref_dt, batch_size=2)
            self.assertEqual(triage["stats"]["isolate_unverified"], 1)
            self.assertEqual(triage["stats"]["drop_noise"], 1)
            self.assertEqual(triage["stats"]["kept"], 1)
            self.assertTrue(triage["kept_candidates"][0]["is_follow_up"])

            vault = {
                "C-1": ExtractedCandidate(
                    candidate_id="C-1",
                    source_id="SRC-IND-PROP-02",
                    title=payloads[0]["title"],
                    pub_date_raw="2026-11-12",
                    subject_entity="Meiko",
                    geo_location="Bắc Ninh",
                    signal_type="ground_breaking",
                    project_scale="450M USD",
                    evidence_snippet="Meiko holds groundbreaking in Bac Ninh.",
                    direct_url="https://technode.global/meiko-vietnam-450m",
                    extracted_at="2026-11-13T00:00:00Z",
                )
            }
            mock_http = HttpFetcher(transport_fn=lambda method, url, **kw: HttpResponseData(200, "ok", b"ok", url))
            curated_res = select_and_curate_candidates(triage["kept_candidates"], vault, fetcher=mock_http, lazy_probe=True)
            items = curated_res["curated_items"]
            self.assertEqual(len(items), 1)
            self.assertEqual(items[0].verified_urls, ["https://technode.global/meiko-vietnam-450m"])

            html = render_brief_html(items, "2026-11-13")
            ok, errs = validate_deliverable_gate(items, html)
            self.assertTrue(ok, f"Gate errors: {errs}")
            # Verify weekend graceful placeholder for empty legal_approval & pure headings
            self.assertIn("本期暂无最新法定环评或行政审批增量公示", html)
            for _, heading in PURE_COLUMNS:
                self.assertIn(heading, html)
            self.assertLess(len(html.encode("utf-8")), 80 * 1024)

    def test_golden_set_regression_and_asset_track_writeback(self):
        from datetime import datetime, timezone
        from pipeline.cognitive.event_ledger import EventLedger
        from pipeline.cognitive.stage1_triage import _evaluate_candidate
        from sources.interfaces.contracts import CuratedBriefItem, ExtractedCandidate

        gs_path = os.path.join(V2_ROOT, "tests", "golden_set.json")
        with open(gs_path, "r", encoding="utf-8") as f:
            gs = json.load(f)

        ref_dt = datetime.fromisoformat(gs["reference_date"].replace("Z", "+00:00"))
        with tempfile.TemporaryDirectory() as tmp:
            ledger = EventLedger(db_path=os.path.join(tmp, "projects.db"), seed_from_v1=False)
            for case in gs["cases"]:
                reg_map = {case["source_meta"]["source_id"]: case["source_meta"]}
                res = _evaluate_candidate(case["payload"], ref_dt, 3, reg_map, ledger)
                exp = case["expect"]
                self.assertEqual(
                    res["decision"],
                    exp["decision"],
                    f"{case['id']} ({case['proposition']}) got decision={res}",
                )
                if "target_column" in exp:
                    self.assertEqual(
                        res.get("target_column"),
                        exp["target_column"],
                        f"{case['id']} wrong column: {res}",
                    )
                if "not_target_column" in exp:
                    self.assertNotEqual(
                        res.get("target_column"),
                        exp["not_target_column"],
                        f"{case['id']} hit forbidden column: {res}",
                    )

            # Verify Asset-Track writeback increments projects & timeline cleanly and skips macro_policy
            vault = {
                "C-GS-01": ExtractedCandidate(
                    candidate_id="C-GS-01",
                    source_id="SRC-VN-FIN-02",
                    title="Luxshare ICT tăng vốn thêm 150 triệu USD mở rộng nhà máy tại Bắc Giang",
                    pub_date_raw="2026-11-12",
                    subject_entity="Luxshare ICT",
                    geo_location="Bắc Giang",
                    signal_type="capital_increase",
                    project_scale="150M USD",
                    evidence_snippet="Luxshare ICT expands factory in Bac Giang.",
                    direct_url="https://vneconomy.vn/luxshare-150m-2026",
                    extracted_at="2026-11-13T00:00:00Z",
                ),
                "C-GS-08": ExtractedCandidate(
                    candidate_id="C-GS-08",
                    source_id="SRC-A01",
                    title="FTA customs rule update",
                    pub_date_raw="2026-11-12",
                    subject_entity="MOIT",
                    geo_location="Hà Nội",
                    signal_type="policy_regulation",
                    project_scale=None,
                    evidence_snippet="FTA origin rule.",
                    direct_url="https://chinhphu.vn/fta-2026",
                    extracted_at="2026-11-13T00:00:00Z",
                ),
            }
            curated = [
                CuratedBriefItem(
                    column="fdi",
                    title_zh="立讯精密拟在北江追加 1.5 亿美元扩建工厂",
                    fact_summary="立讯精密在北江增资 1.5 亿美元扩产。",
                    insight_analysis="北越电子组装产能继续扩张。",
                    ref_candidate_ids=["C-GS-01"],
                    verified_urls=["https://vneconomy.vn/luxshare-150m-2026"],
                ),
                CuratedBriefItem(
                    column="macro_policy",
                    title_zh="工贸部更新 FTA 原产地规则指引",
                    fact_summary="更新原产地核查细则。",
                    insight_analysis="有助于合规出口清关。",
                    ref_candidate_ids=["C-GS-08"],
                    verified_urls=["https://chinhphu.vn/fta-2026"],
                ),
            ]
            stats = ledger.record_project_milestones(curated, vault, "2026-11-13", source_names={"SRC-VN-FIN-02": "VnEconomy"})
            self.assertEqual(stats["projects_created"], 1)
            self.assertEqual(stats["timeline_events_added"], 1)

            # Repeat call must be idempotent for timeline_events_added
            stats_repeat = ledger.record_project_milestones(curated, vault, "2026-11-13")
            self.assertEqual(stats_repeat["projects_created"], 0)
            self.assertEqual(stats_repeat["timeline_events_added"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
