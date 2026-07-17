import csv
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
    build_command_matrix,
    build_csv_export,
    build_csv_import,
    build_docs_export,
    build_fixture_doctor,
    build_golden_replay,
    build_packet,
    build_release_deck,
    build_release_check,
    build_scenario_gallery,
    build_schema_export,
    bundled_example_path,
    load_json,
    input_lint,
    maturity_report,
    public_scan,
    release_manifest,
    release_check,
    schema_guide,
    write_csv,
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

    def test_csv_import_converts_valid_rows_deterministically_without_private_leakage(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "csv-import"
            paths = build_csv_import(
                Path(__file__).resolve().parents[1] / "portfolio_liquidity_runway_lab" / "examples" / "portfolio.csv",
                Path(__file__).resolve().parents[1] / "portfolio_liquidity_runway_lab" / "examples" / "ledger.csv",
                out,
                "CSV fixture",
                "USD",
            )
            first_report = paths.report_json_path.read_text(encoding="utf-8")
            portfolio = load_json(paths.portfolio_json_path)
            ledger = load_json(paths.ledger_json_path)
            self.assertEqual(portfolio["name"], "CSV fixture")
            self.assertEqual([asset["liquidity_tier"] for asset in portfolio["assets"]], ["same_day", "one_week", "one_month", "locked"])
            self.assertEqual(len(ledger["scheduled_events"]), 3)
            combined = first_report + paths.report_markdown_path.read_text(encoding="utf-8")
            self.assertNotIn("api" + "_" + "key", combined.lower())
            self.assertNotIn("private" + "_" + "key", combined.lower())

            build_csv_import(
                Path(__file__).resolve().parents[1] / "portfolio_liquidity_runway_lab" / "examples" / "portfolio.csv",
                Path(__file__).resolve().parents[1] / "portfolio_liquidity_runway_lab" / "examples" / "ledger.csv",
                out,
                "CSV fixture",
                "USD",
            )
            self.assertEqual(first_report, paths.report_json_path.read_text(encoding="utf-8"))

    def test_csv_export_writes_deterministic_packet_tables(self):
        with tempfile.TemporaryDirectory() as tmp:
            packet_paths = build_packet(
                bundled_example_path("portfolio"),
                bundled_example_path("ledger"),
                bundled_example_path("assumptions"),
                Path(tmp) / "packet",
                "stress",
            )
            paths = build_csv_export(packet_paths.json_path, Path(tmp) / "csv-export")
            first_manifest = paths.manifest_json_path.read_text(encoding="utf-8")
            self.assertIn("name,tier,gross,haircut_value,annual_yield,annual_fee", paths.assets_csv_path.read_text(encoding="utf-8").splitlines()[0])
            self.assertIn("month,scheduled_inflows,scheduled_outflows,net_burn,liquid_balance_after", paths.runway_csv_path.read_text(encoding="utf-8").splitlines()[0])
            manifest = load_json(paths.manifest_json_path)
            self.assertEqual([item["path"] for item in manifest["files"]], ["assets.csv", "runway.csv", "warnings.csv", "bucket_summaries.csv"])
            combined = first_manifest + paths.manifest_markdown_path.read_text(encoding="utf-8")
            self.assertNotIn("access" + "_" + "token", combined.lower())

            build_csv_export(packet_paths.json_path, Path(tmp) / "csv-export")
            self.assertEqual(first_manifest, paths.manifest_json_path.read_text(encoding="utf-8"))

    def test_input_lint_reports_csv_and_json_failures(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad_portfolio = Path(tmp) / "bad_portfolio.csv"
            bad_portfolio.write_text("name,value,liquidity_tier,annual_yield_rate,annual_fee_rate\nBad,not-money,overnight,0.01,0\n", encoding="utf-8")
            bad_ledger = Path(tmp) / "bad_ledger.json"
            bad_ledger.write_text('{"monthly_income":"x","monthly_expenses":1000,"scheduled_events":[{"month":1,"type":"maybe","amount":"large"}]}\n', encoding="utf-8")
            result = input_lint([(bad_portfolio, "portfolio_csv"), (bad_ledger, "ledger_json")])
            self.assertEqual(result["status"], "fail")
            self.assertGreaterEqual(result["finding_counts"]["error"], 3)
            findings = [finding for item in result["results"] for finding in item["findings"]]
            self.assertTrue(all("remediation" in finding and "schema_ref" in finding for finding in findings))

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

    def test_command_matrix_writes_deterministic_no_script_catalog(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "matrix"
            paths = build_command_matrix(out)
            first_json = paths.json_path.read_text(encoding="utf-8")
            first_markdown = paths.markdown_path.read_text(encoding="utf-8")
            first_html = paths.html_path.read_text(encoding="utf-8")
            payload = json.loads(first_json)
            commands = {item["command"]: item for item in payload["commands"]}
            self.assertIn("golden-replay", commands)
            self.assertIn("release-deck", commands)
            self.assertIn("risk_boundary", commands["command-matrix"])
            self.assertIn("demo_command", commands["command-matrix"])
            self.assertIn("Command Matrix", first_markdown)
            self.assertIn("<!doctype html>", first_html)
            self.assertNotIn("<script", first_html.lower())
            build_command_matrix(out)
            self.assertEqual(first_json, paths.json_path.read_text(encoding="utf-8"))
            self.assertEqual(first_markdown, paths.markdown_path.read_text(encoding="utf-8"))
            self.assertEqual(first_html, paths.html_path.read_text(encoding="utf-8"))

    def test_golden_replay_reports_pass_and_failure_modes(self):
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            (root / "demo").mkdir(parents=True)
            generated = root / "generated"
            # First create committed demo artifacts from the same builders.
            build_golden_replay(repo_root, root / "seed", generated)
            for path in (generated / "demo").rglob("*"):
                if path.is_file():
                    target = root / "demo" / path.relative_to(generated / "demo")
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(path.read_bytes())

            paths = build_golden_replay(root, root / "replay")
            first_json = paths.json_path.read_text(encoding="utf-8")
            report = json.loads(first_json)
            self.assertEqual(report["status"], "pass")
            self.assertGreater(report["pass_count"], 5)
            self.assertEqual(report["fail_count"], 0)

            (root / "demo" / "visual_receipt.md").write_text("changed\n", encoding="utf-8")
            failing_paths = build_golden_replay(root, root / "replay-fail")
            failing = json.loads(failing_paths.json_path.read_text(encoding="utf-8"))
            self.assertEqual(failing["status"], "fail")
            self.assertTrue(any(item["path"] == "demo/visual_receipt.md" and item["status"] == "fail" for item in failing["comparisons"]))

    def test_release_deck_writes_deterministic_no_script_one_pager(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# Demo\n\nQuickstart\n\nDoes not fetch live data.\n", encoding="utf-8")
            (root / "demo").mkdir()
            (root / "docs").mkdir()
            (root / "demo" / "sample.html").write_text("<!doctype html>\n<p>sample</p>\n", encoding="utf-8")
            out = root / "deck"
            paths = build_release_deck(root, out)
            first_md = paths.markdown_path.read_text(encoding="utf-8")
            first_html = paths.html_path.read_text(encoding="utf-8")
            self.assertIn("Product Value", first_md)
            self.assertIn("golden-replay", first_md)
            self.assertIn("v0.9.0 Release Deck", first_md)
            self.assertIn(f"Release check: `{release_check(root)['status']}`", first_md)
            self.assertIn("<!doctype html>", first_html)
            self.assertNotIn("<script", first_html.lower())
            build_release_deck(root, out)
            self.assertEqual(first_md, paths.markdown_path.read_text(encoding="utf-8"))
            self.assertEqual(first_html, paths.html_path.read_text(encoding="utf-8"))

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

    def test_release_check_flags_html_safety_beyond_script_tags(self):
        unsafe_cases = {
            "event.html": '<img src="x" onerror="alert(1)">',
            "javascript.html": '<a href="javascript:alert(1)">bad</a>',
            "iframe.html": "<iframe srcdoc='bad'></iframe>",
            "object.html": "<object data='bad'></object>",
            "embed.html": "<embed src='bad'>",
            "form.html": "<form action='/submit'></form>",
            "refresh.html": '<meta http-equiv="refresh" content="0;url=/next">',
            "external.html": '<img src="https://example.invalid/pixel.png">',
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("readme\n", encoding="utf-8")
            (root / "demo").mkdir()
            for name, body in unsafe_cases.items():
                (root / "demo" / name).write_text(f"<!doctype html>\n{body}\n", encoding="utf-8")
            result = release_check(root, ["README.md"])
            self.assertEqual(result["status"], "fail")
            codes = {item["code"] for item in result["html_safety_findings"]}
            self.assertTrue({"event_handler", "javascript_url", "iframe_tag", "object_tag", "embed_tag", "form_tag", "meta_refresh", "external_network_url"} <= codes)

    def test_public_scan_detects_path_leakage_tokens_env_labels_and_unsafe_html(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("readme\n", encoding="utf-8")
            leaked_path = "/" "ho" "me/release-owner/private/input.json"
            tmp_path = "/" "tm" "p/private/input.json"
            win_path = "C:" "\\Users\\release-owner\\private\\input.json"
            token = "sk-" + ("a" * 24)
            (root / "docs").mkdir()
            (root / "docs" / "leaks.md").write_text(
                "\n".join(
                    [
                        leaked_path,
                        tmp_path,
                        win_path,
                        "OPENAI_API_" "KEY=" + token,
                        "Authorization: Bearer " + ("b" * 16),
                    ]
                ),
                encoding="utf-8",
            )
            (root / "docs" / "unsafe.html").write_text('<!doctype html>\n<a href="javascript:alert(1)">bad</a>\n', encoding="utf-8")
            result = public_scan(root)
            self.assertEqual(result["status"], "review")
            findings = "\n".join(result["findings"])
            self.assertIn("linux_home_path", findings)
            self.assertIn("tmp_path", findings)
            self.assertIn("windows_user_path", findings)
            self.assertIn("openai_token", findings)
            self.assertIn("environment secret assignment", findings)
            self.assertIn("bearer authorization header", findings)
            self.assertIn("Unsafe HTML [javascript_url]", findings)

    def test_casebook_relativizes_or_redacts_input_paths(self):
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "casebook"
            paths = build_casebook(
                repo_root / "portfolio_liquidity_runway_lab" / "examples" / "portfolio.json",
                repo_root / "portfolio_liquidity_runway_lab" / "examples" / "ledger.json",
                repo_root / "portfolio_liquidity_runway_lab" / "examples" / "assumptions.json",
                repo_root / "demo" / "batch-inputs",
                out,
                "stress",
                ["base", "stress", "income_shock"],
            )
            data = json.loads(paths.json_path.read_text(encoding="utf-8"))
            self.assertEqual(data["inputs"]["portfolio"], "portfolio_liquidity_runway_lab/examples/portfolio.json")
            combined = json.dumps(data, sort_keys=True)
            self.assertNotIn("/" "ho" "me/", combined)
            self.assertNotIn("/" "tm" "p/", combined)

    def test_write_csv_hardens_formula_like_string_prefixes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "danger.csv"
            prefixes = ["=", "+", "-", "@", "\t", "\r"]
            write_csv([{"label": prefix + "formula", "amount": -12} for prefix in prefixes], path)
            with path.open("r", encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual([row["label"] for row in rows], ["'" + prefix + "formula" for prefix in prefixes])
            self.assertEqual({row["amount"] for row in rows}, {"-12"})

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
        self.assertIn("command-matrix", readme)
        self.assertIn("golden-replay", readme)
        self.assertIn("release-deck", readme)
        self.assertIn("bundle-checksums", readme)
        self.assertIn("evidence-bundle", readme)
        self.assertIn("template-pack", readme)
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
        self.assertIn("docs/command-matrix/command_matrix.json", manifest["files"])
        self.assertIn("docs/golden-replay/golden_replay.json", manifest["files"])
        self.assertIn("docs/release-deck/release_deck.html", manifest["files"])
        self.assertIn("docs/bundle-checksums/SHA256SUMS.txt", manifest["files"])
        self.assertIn("docs/evidence-bundle/index.html", manifest["files"])
        self.assertIn("docs/template-pack/template_manifest.json", manifest["files"])
        self.assertIn("demo/casebook/casebook.md", manifest["files"])
        self.assertIn("demo/scenario-gallery/scenario_gallery.md", manifest["files"])
        self.assertIn("demo/assumption-audit/assumption_audit.md", manifest["files"])
        self.assertIn("demo/batch-compare/batch_compare.html", manifest["files"])
        self.assertIn("README.md", manifest["files"])
        self.assertEqual(manifest["version"], "0.9.0")


if __name__ == "__main__":
    unittest.main()
