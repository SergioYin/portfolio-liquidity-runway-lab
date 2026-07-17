import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class CliTests(unittest.TestCase):
    def run_cli(self, *args, cwd=None):
        repo_root = Path(__file__).resolve().parents[1]
        env = dict(os.environ)
        env["PYTHONPATH"] = str(repo_root) + os.pathsep + env.get("PYTHONPATH", "")
        return subprocess.run(
            [sys.executable, "-m", "portfolio_liquidity_runway_lab", *args],
            cwd=cwd,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_selfcheck(self):
        result = self.run_cli("selfcheck")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "ok")
        self.assertTrue(payload["checks"]["html_artifact"])

    def test_quickstart_from_empty_cwd(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_cli("quickstart-check", "--out", "demo", cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "ok")
            self.assertTrue((Path(tmp) / "demo" / "portfolio.json").exists())
            self.assertTrue((Path(tmp) / "demo" / "portfolio_concentrated.json").exists())
            self.assertTrue((Path(tmp) / "demo" / "packet" / "liquidity_packet.html").exists())

    def test_compare_history_uses_bundled_example(self):
        result = self.run_cli("compare-history")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(len(payload["comparisons"]), 2)

    def test_visual_receipt_writes_compact_deterministic_markdown(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "receipt.md"
            result = self.run_cli("visual-receipt", "--out", str(out), "--scenario", "stress")
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "ok")
            receipt = out.read_text(encoding="utf-8")
            self.assertIn("# Visual Receipt:", receipt)
            self.assertIn("portfolio-liquidity-runway-lab build-packet", receipt)
            self.assertIn("does not fetch live data", receipt)
            self.assertIn("`########################`", receipt)
            second = self.run_cli("visual-receipt", "--out", str(out), "--scenario", "stress")
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(receipt, out.read_text(encoding="utf-8"))

    def test_scenario_gallery_command_writes_static_deterministic_gallery(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "gallery"
            result = self.run_cli("scenario-gallery", "--out", str(out))
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "ok")
            gallery_json = out / "scenario_gallery.json"
            gallery_md = out / "scenario_gallery.md"
            gallery_html = out / "scenario_gallery.html"
            self.assertTrue(gallery_json.exists())
            self.assertTrue(gallery_md.exists())
            self.assertTrue(gallery_html.exists())
            first = {
                "json": gallery_json.read_text(encoding="utf-8"),
                "markdown": gallery_md.read_text(encoding="utf-8"),
                "html": gallery_html.read_text(encoding="utf-8"),
            }
            data = json.loads(first["json"])
            self.assertEqual(data["scenario_names"], ["base", "stress", "income_shock", "reserve_rebuild"])
            self.assertIn("reserve_rebuild", first["markdown"])
            self.assertNotIn("<script", first["html"].lower())

            second = self.run_cli("scenario-gallery", "--out", str(out))
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(first["json"], gallery_json.read_text(encoding="utf-8"))
            self.assertEqual(first["markdown"], gallery_md.read_text(encoding="utf-8"))
            self.assertEqual(first["html"], gallery_html.read_text(encoding="utf-8"))

    def test_assumption_audit_command_writes_expected_deterministic_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "audit"
            result = self.run_cli(
                "assumption-audit",
                "--portfolio",
                str(Path(__file__).resolve().parents[1] / "portfolio_liquidity_runway_lab" / "examples" / "portfolio_concentrated.json"),
                "--out",
                str(out),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "ok")
            audit_json = out / "assumption_audit.json"
            audit_md = out / "assumption_audit.md"
            first_json = audit_json.read_text(encoding="utf-8")
            first_md = audit_md.read_text(encoding="utf-8")
            data = json.loads(first_json)
            codes = {finding["code"] for finding in data["findings"]}
            self.assertIn("suspicious_yield", codes)
            self.assertIn("missing_liquidity_tier", codes)
            self.assertIn("# Assumption Audit:", first_md)

            second = self.run_cli(
                "assumption-audit",
                "--portfolio",
                str(Path(__file__).resolve().parents[1] / "portfolio_liquidity_runway_lab" / "examples" / "portfolio_concentrated.json"),
                "--out",
                str(out),
            )
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(first_json, audit_json.read_text(encoding="utf-8"))
            self.assertEqual(first_md, audit_md.read_text(encoding="utf-8"))

    def test_batch_compare_command_writes_no_script_deterministic_html(self):
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            portfolio_dir = Path(tmp) / "portfolios"
            portfolio_dir.mkdir()
            for name in ("portfolio.json", "portfolio_concentrated.json"):
                (portfolio_dir / name).write_text(
                    (repo_root / "portfolio_liquidity_runway_lab" / "examples" / name).read_text(encoding="utf-8"),
                    encoding="utf-8",
                )
            out = Path(tmp) / "batch"
            result = self.run_cli("batch-compare", "--portfolios-dir", str(portfolio_dir), "--scenarios", "base,stress", "--out", str(out))
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "ok")
            batch_json = out / "batch_compare.json"
            batch_md = out / "batch_compare.md"
            batch_html = out / "batch_compare.html"
            first = {
                "json": batch_json.read_text(encoding="utf-8"),
                "markdown": batch_md.read_text(encoding="utf-8"),
                "html": batch_html.read_text(encoding="utf-8"),
            }
            data = json.loads(first["json"])
            self.assertEqual(data["scenario_names"], ["base", "stress"])
            self.assertEqual(len(data["summary"]), 4)
            self.assertNotIn("<script", first["html"].lower())
            self.assertIn("Batch Portfolio Compare", first["markdown"])

            second = self.run_cli("batch-compare", "--portfolios-dir", str(portfolio_dir), "--scenarios", "base,stress", "--out", str(out))
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(first["json"], batch_json.read_text(encoding="utf-8"))
            self.assertEqual(first["markdown"], batch_md.read_text(encoding="utf-8"))
            self.assertEqual(first["html"], batch_html.read_text(encoding="utf-8"))

    def test_casebook_command_writes_deterministic_no_script_artifacts(self):
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            portfolio_dir = Path(tmp) / "portfolios"
            portfolio_dir.mkdir()
            for name in ("portfolio.json", "portfolio_concentrated.json"):
                (portfolio_dir / name).write_text(
                    (repo_root / "portfolio_liquidity_runway_lab" / "examples" / name).read_text(encoding="utf-8"),
                    encoding="utf-8",
                )
            out = Path(tmp) / "casebook"
            result = self.run_cli(
                "casebook",
                "--portfolios-dir",
                str(portfolio_dir),
                "--scenario",
                "stress",
                "--scenarios",
                "base,stress,income_shock",
                "--out",
                str(out),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "ok")
            casebook_json = out / "casebook.json"
            casebook_md = out / "casebook.md"
            casebook_html = out / "casebook.html"
            first = {
                "json": casebook_json.read_text(encoding="utf-8"),
                "markdown": casebook_md.read_text(encoding="utf-8"),
                "html": casebook_html.read_text(encoding="utf-8"),
            }
            data = json.loads(first["json"])
            self.assertEqual(data["packet_summary"]["scenario"], "stress")
            self.assertIn("Assumption Audit Summary", first["markdown"])
            self.assertNotIn("<script", first["html"].lower())

            second = self.run_cli(
                "casebook",
                "--portfolios-dir",
                str(portfolio_dir),
                "--scenario",
                "stress",
                "--scenarios",
                "base,stress,income_shock",
                "--out",
                str(out),
            )
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(first["json"], casebook_json.read_text(encoding="utf-8"))
            self.assertEqual(first["markdown"], casebook_md.read_text(encoding="utf-8"))
            self.assertEqual(first["html"], casebook_html.read_text(encoding="utf-8"))

    def test_artifact_catalog_command_writes_hash_catalog(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "demo").mkdir()
            (root / "docs").mkdir()
            (root / "demo" / "alpha.md").write_text("alpha\n", encoding="utf-8")
            out = root / "docs"
            result = self.run_cli("artifact-catalog", "--root", str(root), "--out", str(out))
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "ok")
            catalog = json.loads((out / "artifact_catalog.json").read_text(encoding="utf-8"))
            self.assertTrue(any(item["path"] == "demo/alpha.md" for item in catalog["artifacts"]))
            self.assertIn("b6a98d9ce9a2d9149288fa3df42d377c3e42737afdcdaf714e33c0a100b51060", (out / "artifact_catalog.md").read_text(encoding="utf-8"))

    def test_schema_export_command_writes_deterministic_schema_guide(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "schema"
            result = self.run_cli("schema-export", "--out", str(out))
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "ok")
            schema_json = out / "schema_guide.json"
            schema_md = out / "schema_guide.md"
            first_json = schema_json.read_text(encoding="utf-8")
            first_md = schema_md.read_text(encoding="utf-8")
            data = json.loads(first_json)
            self.assertIn("portfolio.json", {item["file"] for item in data["input_files"]})
            self.assertIn("schema_guide.json", {item["artifact"] for item in data["output_artifacts"]})
            self.assertIn("assets[].liquidity_tier", first_md)
            second = self.run_cli("schema-export", "--out", str(out))
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(first_json, schema_json.read_text(encoding="utf-8"))
            self.assertEqual(first_md, schema_md.read_text(encoding="utf-8"))

    def test_fixture_doctor_command_reports_success_and_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "doctor"
            result = self.run_cli("fixture-doctor", "--out", str(out))
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "pass")
            self.assertTrue((out / "fixture_doctor.json").exists())
            self.assertTrue(any(item["command"] == "docs-export" for item in payload["results"]))

        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            examples = Path(tmp) / "examples"
            examples.mkdir()
            for name in ("portfolio.json", "portfolio_concentrated.json", "ledger.json", "assumptions.json", "history.json"):
                (examples / name).write_text(
                    (repo_root / "portfolio_liquidity_runway_lab" / "examples" / name).read_text(encoding="utf-8"),
                    encoding="utf-8",
                )
            (examples / "assumptions.json").write_text('{"months": 0, "scenarios": {}}\n', encoding="utf-8")
            result = self.run_cli("fixture-doctor", "--out", str(Path(tmp) / "doctor"), "--examples-dir", str(examples))
            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "fail")
            self.assertTrue(any(item["status"] == "fail" for item in payload["results"]))

    def test_docs_export_command_writes_no_script_static_bundle(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# Local Docs\n\nQuickstart.\n", encoding="utf-8")
            (root / "demo").mkdir()
            (root / "demo" / "sample.md").write_text("sample\n", encoding="utf-8")
            out = root / "static-docs"
            result = self.run_cli("docs-export", "--root", str(root), "--out", str(out))
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "ok")
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertIn("<!doctype html>", html)
            self.assertNotIn("<script", html.lower())
            self.assertIn("command_matrix.md", (out / "index.md").read_text(encoding="utf-8"))

    def test_command_matrix_command_writes_catalog_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "matrix"
            result = self.run_cli("command-matrix", "--out", str(out))
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "ok")
            data = json.loads((out / "command_matrix.json").read_text(encoding="utf-8"))
            commands = {item["command"] for item in data["commands"]}
            self.assertIn("golden-replay", commands)
            self.assertIn("release-deck", commands)
            html = (out / "command_matrix.html").read_text(encoding="utf-8")
            self.assertNotIn("<script", html.lower())

            second = self.run_cli("command-matrix", "--out", str(out))
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(data, json.loads((out / "command_matrix.json").read_text(encoding="utf-8")))

    def test_release_deck_command_writes_no_script_static_deck(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            (root / "README.md").write_text("# Demo\n\nQuickstart. Does not fetch live data.\n", encoding="utf-8")
            (root / "demo").mkdir()
            (root / "docs").mkdir()
            out = Path(tmp) / "deck"
            result = self.run_cli("release-deck", "--root", str(root), "--out", str(out))
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "ok")
            markdown = (out / "release_deck.md").read_text(encoding="utf-8")
            html = (out / "release_deck.html").read_text(encoding="utf-8")
            self.assertIn("Product Value", markdown)
            self.assertIn("Next Roadmap", markdown)
            self.assertNotIn("<script", html.lower())

    def test_golden_replay_command_reports_failure_for_changed_demo(self):
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            (root / "demo").mkdir(parents=True)
            seed = Path(tmp) / "seed"
            seed_result = self.run_cli("golden-replay", "--root", str(root), "--out", str(Path(tmp) / "seed-out"), "--replay-dir", str(seed))
            self.assertEqual(seed_result.returncode, 1)
            for path in (seed / "demo").rglob("*"):
                if path.is_file():
                    target = root / "demo" / path.relative_to(seed / "demo")
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
            (root / "demo" / "visual_receipt.md").write_text("changed\n", encoding="utf-8")
            result = self.run_cli("golden-replay", "--root", str(root), "--out", str(Path(tmp) / "golden"))
            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "fail")
            report = json.loads((Path(tmp) / "golden" / "golden_replay.json").read_text(encoding="utf-8"))
            self.assertTrue(any(item["path"] == "demo/visual_receipt.md" and item["status"] == "fail" for item in report["comparisons"]))

    def test_release_check_command_reports_no_script_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("readme\n", encoding="utf-8")
            (root / "demo").mkdir()
            (root / "demo" / "bad.html").write_text("<script>alert(1)</script>\n", encoding="utf-8")
            result = self.run_cli("release-check", "--root", str(root))
            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "fail")
            self.assertIn("demo/bad.html", payload["html_with_script_tags"])

    def test_public_scan_passes_repo_without_ai_metadata(self):
        repo_root = Path(__file__).resolve().parents[1]
        result = self.run_cli("public-scan", "--root", str(repo_root))
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["findings"], [])
        self.assertIn(
            "Portfolio Liquidity Runway Lab contributors",
            (repo_root / "pyproject.toml").read_text(encoding="utf-8"),
        )
        self.assertIn(
            "Portfolio Liquidity Runway Lab contributors",
            (repo_root / "LICENSE").read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
