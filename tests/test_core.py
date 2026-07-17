import json
import tempfile
import unittest
from pathlib import Path

from portfolio_liquidity_runway_lab.core import (
    analyze,
    artifact_catalog,
    assumption_audit,
    build_artifact_catalog,
    build_assumption_audit,
    build_batch_compare,
    build_casebook,
    build_docs_export,
    build_fixture_doctor,
    build_packet,
    build_release_check,
    build_scenario_gallery,
    build_schema_export,
    bundled_example_path,
    load_json,
    maturity_report,
    release_manifest,
    release_check,
    schema_guide,
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

    def test_casebook_writes_deterministic_no_script_release_owner_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            portfolio_dir = Path(tmp) / "portfolios"
            portfolio_dir.mkdir()
            (portfolio_dir / "portfolio.json").write_text(bundled_example_path("portfolio").read_text(encoding="utf-8"), encoding="utf-8")
            (portfolio_dir / "portfolio_concentrated.json").write_text(
                bundled_example_path("portfolio_concentrated").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            out = Path(tmp) / "casebook"
            paths = build_casebook(
                bundled_example_path("portfolio"),
                bundled_example_path("ledger"),
                bundled_example_path("assumptions"),
                portfolio_dir,
                out,
                "stress",
                ["base", "stress", "income_shock"],
            )
            first_json = paths.json_path.read_text(encoding="utf-8")
            first_markdown = paths.markdown_path.read_text(encoding="utf-8")
            first_html = paths.html_path.read_text(encoding="utf-8")
            payload = json.loads(first_json)
            self.assertEqual(payload["packet_summary"]["scenario"], "stress")
            self.assertEqual(payload["scenario_names"], ["base", "stress", "income_shock"])
            self.assertEqual(len(payload["batch_compare_summary"]), 6)
            self.assertIn("# Release Owner Casebook:", first_markdown)
            self.assertIn("<!doctype html>", first_html)
            self.assertNotIn("<script", first_html.lower())

            build_casebook(
                bundled_example_path("portfolio"),
                bundled_example_path("ledger"),
                bundled_example_path("assumptions"),
                portfolio_dir,
                out,
                "stress",
                ["base", "stress", "income_shock"],
            )
            self.assertEqual(first_json, paths.json_path.read_text(encoding="utf-8"))
            self.assertEqual(first_markdown, paths.markdown_path.read_text(encoding="utf-8"))
            self.assertEqual(first_html, paths.html_path.read_text(encoding="utf-8"))

    def test_artifact_catalog_records_deterministic_sizes_hashes_and_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            demo = root / "demo"
            docs = root / "docs"
            demo.mkdir()
            docs.mkdir()
            (demo / "alpha.md").write_text("alpha\n", encoding="utf-8")
            (docs / "beta.html").write_text("<!doctype html>\n<p>beta</p>\n", encoding="utf-8")
            first = artifact_catalog(root)
            second = artifact_catalog(root)
            self.assertEqual(first, second)
            self.assertEqual(first["artifact_count"], 2)
            alpha = next(item for item in first["artifacts"] if item["path"] == "demo/alpha.md")
            self.assertEqual(alpha["size_bytes"], 6)
            self.assertEqual(alpha["sha256"], "b6a98d9ce9a2d9149288fa3df42d377c3e42737afdcdaf714e33c0a100b51060")
            self.assertEqual(alpha["regeneration_command"], "manual edit")

            paths = build_artifact_catalog(root, docs)
            markdown = paths.markdown_path.read_text(encoding="utf-8")
            self.assertIn("Artifact Catalog", markdown)
            self.assertIn(alpha["sha256"], markdown)

    def test_schema_export_covers_inputs_outputs_and_is_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "schema"
            paths = build_schema_export(out)
            first_json = paths.json_path.read_text(encoding="utf-8")
            first_markdown = paths.markdown_path.read_text(encoding="utf-8")
            payload = json.loads(first_json)
            input_files = {item["file"] for item in payload["input_files"]}
            output_artifacts = {item["artifact"] for item in payload["output_artifacts"]}
            portfolio_fields = {
                field["path"]
                for item in payload["input_files"]
                if item["file"] == "portfolio.json"
                for field in item["fields"]
            }
            self.assertIn("portfolio.json", input_files)
            self.assertIn("assumptions.json", input_files)
            self.assertIn("assets[].liquidity_tier", portfolio_fields)
            self.assertIn("fixture_doctor.json", output_artifacts)
            self.assertIn("static-docs/index.html", output_artifacts)
            self.assertIn("schema-export", first_markdown)
            build_schema_export(out)
            self.assertEqual(first_json, paths.json_path.read_text(encoding="utf-8"))
            self.assertEqual(first_markdown, paths.markdown_path.read_text(encoding="utf-8"))
            self.assertEqual(schema_guide(), json.loads(paths.json_path.read_text(encoding="utf-8")))

    def test_fixture_doctor_reports_success_and_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "doctor"
            paths = build_fixture_doctor(out)
            report = json.loads(paths.json_path.read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "pass")
            commands = {item["command"] for item in report["results"]}
            self.assertIn("build-packet", commands)
            self.assertIn("docs-export", commands)
            self.assertIn("# Fixture Doctor", paths.markdown_path.read_text(encoding="utf-8"))

        with tempfile.TemporaryDirectory() as tmp:
            examples = Path(tmp) / "bad-examples"
            examples.mkdir()
            for name in ("portfolio.json", "portfolio_concentrated.json", "ledger.json", "assumptions.json", "history.json"):
                (examples / name).write_text(bundled_example_path(name).read_text(encoding="utf-8"), encoding="utf-8")
            (examples / "assumptions.json").write_text('{"months": 0, "scenarios": {}}\n', encoding="utf-8")
            paths = build_fixture_doctor(Path(tmp) / "doctor", examples_dir=examples)
            report = json.loads(paths.json_path.read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "fail")
            self.assertTrue(any(item["status"] == "fail" for item in report["results"]))

    def test_docs_export_writes_no_script_static_bundle(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# Demo README\n\nQuickstart text.\n", encoding="utf-8")
            (root / "demo").mkdir()
            (root / "demo" / "sample.md").write_text("sample\n", encoding="utf-8")
            out = root / "docs-bundle"
            paths = build_docs_export(root, out)
            first_html = paths.index_html_path.read_text(encoding="utf-8")
            first_markdown = paths.index_markdown_path.read_text(encoding="utf-8")
            self.assertIn("<!doctype html>", first_html)
            self.assertNotIn("<script", first_html.lower())
            self.assertIn("[Command matrix](command_matrix.md)", first_markdown)
            self.assertTrue((out / "boundaries.md").exists())
            self.assertTrue((out / "demos.md").exists())
            build_docs_export(root, out)
            self.assertEqual(first_html, paths.index_html_path.read_text(encoding="utf-8"))
            self.assertEqual(first_markdown, paths.index_markdown_path.read_text(encoding="utf-8"))

    def test_release_check_passes_and_reports_failure_modes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in ("README.md", "demo/ok.html"):
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("plain\n", encoding="utf-8")
            passing = release_check(root, ["README.md", "demo/ok.html"])
            self.assertEqual(passing["status"], "pass")
            self.assertTrue(passing["checks"]["html_no_script_tags"])

            bad_html = root / "demo" / "bad.html"
            bad_html.write_text("<script>alert(1)</script>\n", encoding="utf-8")
            failing = release_check(root, ["README.md", "missing.md"])
            self.assertEqual(failing["status"], "fail")
            self.assertIn("missing.md", failing["missing_files"])
            self.assertIn("demo/bad.html", failing["html_with_script_tags"])

            paths = build_release_check(root, root / "docs", ["README.md", "missing.md"])
            payload = json.loads(paths.json_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "fail")
            self.assertIn("Release Check", paths.markdown_path.read_text(encoding="utf-8"))

    def test_readme_and_maturity_report_cover_public_release_expectations(self):
        repo_root = Path(__file__).resolve().parents[1]
        readme = (repo_root / "README.md").read_text(encoding="utf-8").lower()
        self.assertLess(readme.index("quickstart"), readme.index("## commands"))
        self.assertIn("example outputs", readme)
        self.assertIn("visual-receipt", readme)
        self.assertIn("casebook", readme)
        self.assertIn("artifact-catalog", readme)
        self.assertIn("release-check", readme)
        self.assertIn("schema-export", readme)
        self.assertIn("fixture-doctor", readme)
        self.assertIn("docs-export", readme)
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
        self.assertIn("docs/artifact_catalog.json", manifest["files"])
        self.assertIn("docs/schema_guide.json", manifest["files"])
        self.assertIn("docs/fixture_doctor.json", manifest["files"])
        self.assertIn("docs/static-docs/index.html", manifest["files"])
        self.assertIn("demo/casebook/casebook.md", manifest["files"])
        self.assertIn("demo/scenario-gallery/scenario_gallery.md", manifest["files"])
        self.assertIn("demo/assumption-audit/assumption_audit.md", manifest["files"])
        self.assertIn("demo/batch-compare/batch_compare.html", manifest["files"])
        self.assertIn("README.md", manifest["files"])
        self.assertEqual(manifest["version"], "0.5.0")


if __name__ == "__main__":
    unittest.main()
