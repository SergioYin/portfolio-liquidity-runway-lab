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
