import json
import tempfile
import unittest
from pathlib import Path

from portfolio_liquidity_runway_lab.core import analyze, build_packet, bundled_example_path, load_json, maturity_report, release_manifest


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

    def test_readme_and_maturity_report_cover_public_release_expectations(self):
        repo_root = Path(__file__).resolve().parents[1]
        readme = (repo_root / "README.md").read_text(encoding="utf-8").lower()
        self.assertLess(readme.index("quickstart"), readme.index("## commands"))
        self.assertIn("example outputs", readme)
        self.assertIn("visual-receipt", readme)
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
        self.assertIn("README.md", manifest["files"])


if __name__ == "__main__":
    unittest.main()
