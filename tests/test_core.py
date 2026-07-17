import json
import tempfile
import unittest
from pathlib import Path

from portfolio_liquidity_runway_lab.core import (
    analyze,
    assumption_audit,
    build_assumption_audit,
    build_batch_compare,
    build_packet,
    build_scenario_gallery,
    bundled_example_path,
    load_json,
    maturity_report,
    release_manifest,
)


class CoreTests(unittest.TestCase):
    def test_analyze_bundled_stress_has_expected_sections(self):
        packet = analyze(
            load_json(bundled_example_path("portfolio")),
            load_json(bundled_example_path("ledger")),
            load_json(bundled_example_path("assumptions")),
            "stress",
        )
        self.assertEqual(packet["scenario"], "stress")
        self.assertEqual(set(packet["cash_buckets"]), {"same_day", "one_week", "one_month", "locked"})
        self.assertGreater(packet["totals"]["effective_monthly_burn"], 0)
        self.assertTrue(packet["forced_sale_warnings"])
        self.assertIn("does not fetch live data", packet["boundary"])

    def test_build_packet_writes_deterministic_static_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "packet"
            paths = build_packet(
                bundled_example_path("portfolio"),
                bundled_example_path("ledger"),
                bundled_example_path("assumptions"),
                out,
                "base",
            )
            self.assertTrue(paths.json_path.exists())
            self.assertTrue(paths.markdown_path.exists())
            html = paths.html_path.read_text(encoding="utf-8")
            self.assertIn("<!doctype html>", html)
            self.assertNotIn("<script", html.lower())

    def test_scenario_gallery_writes_static_deterministic_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "gallery"
            paths = build_scenario_gallery(
                bundled_example_path("portfolio"),
                bundled_example_path("ledger"),
                bundled_example_path("assumptions"),
                out,
            )
            first_json = paths.json_path.read_text(encoding="utf-8")
            first_markdown = paths.markdown_path.read_text(encoding="utf-8")
            first_html = paths.html_path.read_text(encoding="utf-8")
            payload = json.loads(first_json)
            self.assertEqual(payload["scenario_names"], ["base", "stress", "income_shock", "reserve_rebuild"])
            self.assertEqual([row["scenario"] for row in payload["summary"]], payload["scenario_names"])
            self.assertIn("# Scenario Gallery:", first_markdown)
            self.assertIn("income_shock", first_markdown)
            self.assertIn("<!doctype html>", first_html)
            self.assertNotIn("<script", first_html.lower())

            build_scenario_gallery(
                bundled_example_path("portfolio"),
                bundled_example_path("ledger"),
                bundled_example_path("assumptions"),
                out,
            )
            self.assertEqual(first_json, paths.json_path.read_text(encoding="utf-8"))
            self.assertEqual(first_markdown, paths.markdown_path.read_text(encoding="utf-8"))
            self.assertEqual(first_html, paths.html_path.read_text(encoding="utf-8"))

    def test_assumption_audit_reports_expected_findings_and_is_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "audit"
            paths = build_assumption_audit(
                bundled_example_path("portfolio_concentrated"),
                bundled_example_path("ledger"),
                bundled_example_path("assumptions"),
                out,
            )
            first_json = paths.json_path.read_text(encoding="utf-8")
            first_markdown = paths.markdown_path.read_text(encoding="utf-8")
            payload = json.loads(first_json)
            codes = {finding["code"] for finding in payload["findings"]}
            self.assertEqual(payload["status"], "review")
            self.assertIn("suspicious_yield", codes)
            self.assertIn("suspicious_fee", codes)
            self.assertIn("missing_liquidity_tier", codes)
            self.assertIn("# Assumption Audit:", first_markdown)

            build_assumption_audit(
                bundled_example_path("portfolio_concentrated"),
                bundled_example_path("ledger"),
                bundled_example_path("assumptions"),
                out,
            )
            self.assertEqual(first_json, paths.json_path.read_text(encoding="utf-8"))
            self.assertEqual(first_markdown, paths.markdown_path.read_text(encoding="utf-8"))

    def test_assumption_audit_catches_nonnumeric_and_scheduled_event_issues(self):
        portfolio = {
            "name": "Bad inputs",
            "assets": [
                {"name": "Cash", "liquidity_tier": "same_day", "value": "n/a", "annual_yield_rate": 0.5, "annual_fee_rate": "fee"}
            ],
        }
        ledger = {
            "monthly_income": "income",
            "monthly_expenses": 1000,
            "scheduled_events": [
                {"month": 99, "type": "maybe", "label": "", "amount": "large"},
                {"month": 1, "type": "outflow", "label": "Large", "amount": 4000},
            ],
        }
        assumptions = {
            "months": 2,
            "target_reserve_months": 30,
            "default_scenario": "base",
            "scenarios": {"base": {"expense_multiplier": "x", "income_multiplier": 1, "liquidity_haircuts": {"same_day": 0}}},
        }
        audit = assumption_audit(portfolio, ledger, assumptions)
        codes = {finding["code"] for finding in audit["findings"]}
        self.assertIn("nonnumeric_value", codes)
        self.assertIn("event_outside_window", codes)
        self.assertIn("invalid_event_type", codes)
        self.assertIn("large_scheduled_outflow", codes)
        self.assertIn("missing_haircut", codes)
        self.assertIn("reserve_threshold_issue", codes)

    def test_batch_compare_writes_static_deterministic_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            portfolio_dir = Path(tmp) / "portfolios"
            portfolio_dir.mkdir()
            (portfolio_dir / "portfolio.json").write_text(bundled_example_path("portfolio").read_text(encoding="utf-8"), encoding="utf-8")
            (portfolio_dir / "portfolio_concentrated.json").write_text(
                bundled_example_path("portfolio_concentrated").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            out = Path(tmp) / "batch"
            paths = build_batch_compare(
                portfolio_dir,
                bundled_example_path("ledger"),
                bundled_example_path("assumptions"),
                out,
                ["base", "stress"],
            )
            first_json = paths.json_path.read_text(encoding="utf-8")
            first_markdown = paths.markdown_path.read_text(encoding="utf-8")
            first_html = paths.html_path.read_text(encoding="utf-8")
            payload = json.loads(first_json)
            self.assertEqual(payload["portfolio_files"], ["portfolio.json", "portfolio_concentrated.json"])
            self.assertEqual(payload["scenario_names"], ["base", "stress"])
            self.assertEqual(len(payload["summary"]), 4)
            self.assertIn("# Batch Portfolio Compare", first_markdown)
            self.assertIn("<!doctype html>", first_html)
            self.assertNotIn("<script", first_html.lower())

            build_batch_compare(
                portfolio_dir,
                bundled_example_path("ledger"),
                bundled_example_path("assumptions"),
                out,
                ["base", "stress"],
            )
            self.assertEqual(first_json, paths.json_path.read_text(encoding="utf-8"))
            self.assertEqual(first_markdown, paths.markdown_path.read_text(encoding="utf-8"))
            self.assertEqual(first_html, paths.html_path.read_text(encoding="utf-8"))

    def test_readme_and_maturity_report_cover_public_release_expectations(self):
        repo_root = Path(__file__).resolve().parents[1]
        readme = (repo_root / "README.md").read_text(encoding="utf-8").lower()
        self.assertLess(readme.index("quickstart"), readme.index("## commands"))
        self.assertIn("example outputs", readme)
        self.assertIn("visual-receipt", readme)
        self.assertIn("scenario-gallery", readme)
        self.assertIn("assumption-audit", readme)
        self.assertIn("batch-compare", readme)
        self.assertIn("does not fetch live data", readme)
        self.assertIn("does not provide tax, legal, investment, buy, sell, or hold advice", readme)

        report = maturity_report(repo_root)
        self.assertTrue(all(report["checks"].values()), json.dumps(report, indent=2, sort_keys=True))

    def test_release_manifest_includes_public_docs_and_runtime_boundary(self):
        repo_root = Path(__file__).resolve().parents[1]
        manifest = release_manifest(repo_root)
        self.assertEqual(manifest["runtime_dependencies"], [])
        self.assertIn("does not fetch live data", manifest["boundary"])
        self.assertIn("docs/cold_start_walkthrough.md", manifest["files"])
        self.assertIn("docs/release_readiness_review.md", manifest["files"])
        self.assertIn("demo/visual_receipt.md", manifest["files"])
        self.assertIn("demo/scenario-gallery/scenario_gallery.md", manifest["files"])
        self.assertIn("demo/assumption-audit/assumption_audit.md", manifest["files"])
        self.assertIn("demo/batch-compare/batch_compare.html", manifest["files"])
        self.assertIn("README.md", manifest["files"])
        self.assertEqual(manifest["version"], "0.3.0")


if __name__ == "__main__":
    unittest.main()
