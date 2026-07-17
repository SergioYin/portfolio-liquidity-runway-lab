from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

from . import __version__
from .core import (
    BOUNDARY_TEXT,
    artifact_catalog,
    build_assumption_audit,
    build_artifact_catalog,
    build_batch_compare,
    build_casebook,
    build_packet,
    build_release_check,
    build_scenario_gallery,
    build_visual_receipt,
    bundled_example_path,
    compare_history,
    dump_json,
    load_json,
    maturity_report,
    public_scan,
    release_check,
    release_manifest,
    review_ledger,
)


def _example_or_path(path: Optional[str], example_name: str) -> Path:
    return Path(path) if path else bundled_example_path(example_name)


def _print_json(data: Dict[str, Any]) -> None:
    json.dump(data, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


def cmd_build_packet(args: argparse.Namespace) -> int:
    paths = build_packet(
        _example_or_path(args.portfolio, "portfolio"),
        _example_or_path(args.ledger, "ledger"),
        _example_or_path(args.assumptions, "assumptions"),
        Path(args.out),
        args.scenario,
    )
    _print_json(
        {
            "status": "ok",
            "boundary": BOUNDARY_TEXT,
            "json": str(paths.json_path),
            "markdown": str(paths.markdown_path),
            "html": str(paths.html_path),
        }
    )
    return 0


def cmd_compare_history(args: argparse.Namespace) -> int:
    result = compare_history(load_json(_example_or_path(args.history, "history")))
    if args.out:
        dump_json(result, Path(args.out))
    _print_json(result)
    return 0


def cmd_review_ledger(args: argparse.Namespace) -> int:
    result = review_ledger(load_json(_example_or_path(args.ledger, "ledger")))
    if args.out:
        dump_json(result, Path(args.out))
    _print_json(result)
    return 0


def cmd_static_dashboard(args: argparse.Namespace) -> int:
    paths = build_packet(
        _example_or_path(args.portfolio, "portfolio"),
        _example_or_path(args.ledger, "ledger"),
        _example_or_path(args.assumptions, "assumptions"),
        Path(args.out),
        args.scenario,
    )
    _print_json({"status": "ok", "html": str(paths.html_path), "boundary": BOUNDARY_TEXT})
    return 0


def _split_scenarios(value: Optional[str]) -> Optional[list[str]]:
    if not value:
        return None
    scenarios = [item.strip() for item in value.split(",") if item.strip()]
    if len(scenarios) < 3:
        raise ValueError("--scenarios must name at least three scenarios")
    return scenarios


def _split_optional_scenarios(value: Optional[str]) -> Optional[list[str]]:
    if not value:
        return None
    scenarios = [item.strip() for item in value.split(",") if item.strip()]
    if not scenarios:
        raise ValueError("--scenarios must name at least one scenario")
    return scenarios


def cmd_scenario_gallery(args: argparse.Namespace) -> int:
    paths = build_scenario_gallery(
        _example_or_path(args.portfolio, "portfolio"),
        _example_or_path(args.ledger, "ledger"),
        _example_or_path(args.assumptions, "assumptions"),
        Path(args.out),
        _split_scenarios(args.scenarios),
    )
    _print_json(
        {
            "status": "ok",
            "boundary": BOUNDARY_TEXT,
            "json": str(paths.json_path),
            "markdown": str(paths.markdown_path),
            "html": str(paths.html_path),
        }
    )
    return 0


def cmd_assumption_audit(args: argparse.Namespace) -> int:
    paths = build_assumption_audit(
        _example_or_path(args.portfolio, "portfolio"),
        _example_or_path(args.ledger, "ledger"),
        _example_or_path(args.assumptions, "assumptions"),
        Path(args.out),
    )
    _print_json({"status": "ok", "boundary": BOUNDARY_TEXT, "json": str(paths.json_path), "markdown": str(paths.markdown_path)})
    return 0


def cmd_batch_compare(args: argparse.Namespace) -> int:
    paths = build_batch_compare(
        Path(args.portfolios_dir),
        _example_or_path(args.ledger, "ledger"),
        _example_or_path(args.assumptions, "assumptions"),
        Path(args.out),
        _split_optional_scenarios(args.scenarios),
    )
    _print_json(
        {
            "status": "ok",
            "boundary": BOUNDARY_TEXT,
            "json": str(paths.json_path),
            "markdown": str(paths.markdown_path),
            "html": str(paths.html_path),
        }
    )
    return 0


def _default_portfolios_dir() -> tempfile.TemporaryDirectory[str]:
    tmp = tempfile.TemporaryDirectory(prefix="plrl-portfolios-")
    tmp_path = Path(tmp.name)
    shutil.copyfile(bundled_example_path("portfolio"), tmp_path / "portfolio.json")
    shutil.copyfile(bundled_example_path("portfolio_concentrated"), tmp_path / "portfolio_concentrated.json")
    return tmp


def cmd_casebook(args: argparse.Namespace) -> int:
    temp_dir: Optional[tempfile.TemporaryDirectory[str]] = None
    try:
        portfolios_dir = Path(args.portfolios_dir) if args.portfolios_dir else None
        if portfolios_dir is None:
            temp_dir = _default_portfolios_dir()
            portfolios_dir = Path(temp_dir.name)
        paths = build_casebook(
            _example_or_path(args.portfolio, "portfolio"),
            _example_or_path(args.ledger, "ledger"),
            _example_or_path(args.assumptions, "assumptions"),
            portfolios_dir,
            Path(args.out),
            args.scenario,
            _split_scenarios(args.scenarios) if args.scenarios else None,
        )
    finally:
        if temp_dir is not None:
            temp_dir.cleanup()
    _print_json(
        {
            "status": "ok",
            "boundary": BOUNDARY_TEXT,
            "json": str(paths.json_path),
            "markdown": str(paths.markdown_path),
            "html": str(paths.html_path),
        }
    )
    return 0


def cmd_artifact_catalog(args: argparse.Namespace) -> int:
    selected = [item.strip() for item in args.paths.split(",") if item.strip()] if args.paths else ["demo", "docs"]
    if args.out:
        paths = build_artifact_catalog(Path(args.root), Path(args.out), selected)
        _print_json({"status": "ok", "boundary": BOUNDARY_TEXT, "json": str(paths.json_path), "markdown": str(paths.markdown_path)})
    else:
        _print_json(artifact_catalog(Path(args.root), selected))
    return 0


def cmd_release_check(args: argparse.Namespace) -> int:
    if args.out:
        paths = build_release_check(Path(args.root), Path(args.out))
        result = load_json(paths.json_path)
        _print_json(
            {
                "status": result["status"],
                "boundary": BOUNDARY_TEXT,
                "json": str(paths.json_path),
                "markdown": str(paths.markdown_path),
                "checks": result["checks"],
            }
        )
    else:
        result = release_check(Path(args.root))
        _print_json(result)
    return 0 if result["status"] == "pass" else 1


def cmd_visual_receipt(args: argparse.Namespace) -> int:
    path = build_visual_receipt(
        _example_or_path(args.portfolio, "portfolio"),
        _example_or_path(args.ledger, "ledger"),
        _example_or_path(args.assumptions, "assumptions"),
        Path(args.out),
        args.scenario,
        args.packet_out,
    )
    _print_json({"status": "ok", "receipt": str(path), "boundary": BOUNDARY_TEXT})
    return 0


def cmd_quickstart_check(args: argparse.Namespace) -> int:
    out = Path(args.out)
    if out.exists() and not out.is_dir():
        raise ValueError("--out must be a directory")
    out.mkdir(parents=True, exist_ok=True)
    for name in ("portfolio.json", "portfolio_concentrated.json", "ledger.json", "assumptions.json", "history.json"):
        shutil.copyfile(bundled_example_path(name), out / name)
    paths = build_packet(out / "portfolio.json", out / "ledger.json", out / "assumptions.json", out / "packet")
    _print_json({"status": "ok", "examples": str(out), "packet": str(paths.out_dir), "boundary": BOUNDARY_TEXT})
    return 0


def cmd_selfcheck(args: argparse.Namespace) -> int:
    with tempfile.TemporaryDirectory(prefix="plrl-selfcheck-") as tmp:
        tmp_path = Path(tmp)
        paths = build_packet(
            bundled_example_path("portfolio"),
            bundled_example_path("ledger"),
            bundled_example_path("assumptions"),
            tmp_path / "packet",
            "stress",
        )
        gallery_paths = build_scenario_gallery(
            bundled_example_path("portfolio"),
            bundled_example_path("ledger"),
            bundled_example_path("assumptions"),
            tmp_path / "scenario-gallery",
        )
        gallery = load_json(gallery_paths.json_path)
        packet = load_json(paths.json_path)
        audit_paths = build_assumption_audit(
            bundled_example_path("portfolio_concentrated"),
            bundled_example_path("ledger"),
            bundled_example_path("assumptions"),
            tmp_path / "assumption-audit",
        )
        batch_dir = tmp_path / "batch-inputs"
        batch_dir.mkdir()
        shutil.copyfile(bundled_example_path("portfolio"), batch_dir / "portfolio.json")
        shutil.copyfile(bundled_example_path("portfolio_concentrated"), batch_dir / "portfolio_concentrated.json")
        batch_paths = build_batch_compare(
            batch_dir,
            bundled_example_path("ledger"),
            bundled_example_path("assumptions"),
            tmp_path / "batch-compare",
            ["base", "stress"],
        )
        audit = load_json(audit_paths.json_path)
        batch = load_json(batch_paths.json_path)
        checks = {
            "json_artifact": paths.json_path.exists(),
            "markdown_artifact": paths.markdown_path.exists(),
            "html_artifact": paths.html_path.exists() and "<script" not in paths.html_path.read_text(encoding="utf-8").lower(),
            "scenario_gallery": (
                gallery_paths.json_path.exists()
                and gallery_paths.markdown_path.exists()
                and gallery_paths.html_path.exists()
                and "<script" not in gallery_paths.html_path.read_text(encoding="utf-8").lower()
                and gallery.get("scenario_names") == ["base", "stress", "income_shock", "reserve_rebuild"]
            ),
            "assumption_audit": (
                audit_paths.json_path.exists()
                and audit_paths.markdown_path.exists()
                and audit.get("status") == "review"
                and any(item.get("code") == "suspicious_yield" for item in audit.get("findings", []))
            ),
            "batch_compare": (
                batch_paths.json_path.exists()
                and batch_paths.markdown_path.exists()
                and batch_paths.html_path.exists()
                and "<script" not in batch_paths.html_path.read_text(encoding="utf-8").lower()
                and batch.get("scenario_names") == ["base", "stress"]
                and len(batch.get("summary", [])) == 4
            ),
            "casebook": (
                build_casebook(
                    bundled_example_path("portfolio"),
                    bundled_example_path("ledger"),
                    bundled_example_path("assumptions"),
                    batch_dir,
                    tmp_path / "casebook",
                    "stress",
                    ["base", "stress", "income_shock"],
                ).html_path.read_text(encoding="utf-8").lower().find("<script")
                == -1
            ),
            "artifact_catalog": artifact_catalog(tmp_path, ["packet", "scenario-gallery", "assumption-audit", "batch-compare"])["artifact_count"] >= 8,
            "release_check_failure_mode": release_check(tmp_path, ["missing.md"])["status"] == "fail",
            "visual_receipt": (
                build_visual_receipt(
                    bundled_example_path("portfolio"),
                    bundled_example_path("ledger"),
                    bundled_example_path("assumptions"),
                    tmp_path / "visual_receipt.md",
                    "stress",
                ).read_text(encoding="utf-8").count(BOUNDARY_TEXT)
                == 1
            ),
            "forced_sale_warnings": bool(packet.get("forced_sale_warnings")),
            "cash_buckets": set(packet.get("cash_buckets", {})) == {"same_day", "one_week", "one_month", "locked"},
        }
    status = "ok" if all(checks.values()) else "fail"
    _print_json({"status": status, "version": __version__, "checks": checks, "boundary": BOUNDARY_TEXT})
    return 0 if status == "ok" else 1


def cmd_public_scan(args: argparse.Namespace) -> int:
    result = public_scan(Path(args.root))
    if args.out:
        dump_json(result, Path(args.out))
    _print_json(result)
    return 0 if result["status"] == "pass" else 1


def cmd_release_manifest(args: argparse.Namespace) -> int:
    result = release_manifest(Path(args.root))
    if args.out:
        dump_json(result, Path(args.out))
    _print_json(result)
    return 0


def cmd_maturity_report(args: argparse.Namespace) -> int:
    result = maturity_report(Path(args.root))
    if args.out:
        dump_json(result, Path(args.out))
    _print_json(result)
    return 0 if all(result["checks"].values()) else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="portfolio-liquidity-runway-lab",
        description="Build static local liquidity runway packets from local JSON inputs.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_common_inputs(p: argparse.ArgumentParser) -> None:
        p.add_argument("--portfolio", help="Portfolio JSON path. Defaults to bundled synthetic example.")
        p.add_argument("--ledger", help="Ledger JSON path. Defaults to bundled synthetic example.")
        p.add_argument("--assumptions", help="Assumptions JSON path. Defaults to bundled synthetic example.")
        p.add_argument("--scenario", help="Scenario name from assumptions JSON.")

    p = sub.add_parser("build-packet", help="Build JSON, Markdown, and no-JavaScript HTML packet artifacts.")
    add_common_inputs(p)
    p.add_argument("--out", default="dist/packet", help="Output directory.")
    p.set_defaults(func=cmd_build_packet)

    p = sub.add_parser("compare-history", help="Compare historical reserve and burn snapshots.")
    p.add_argument("--history", help="History JSON path. Defaults to bundled synthetic example.")
    p.add_argument("--out", help="Optional JSON output path.")
    p.set_defaults(func=cmd_compare_history)

    p = sub.add_parser("review-ledger", help="Review ledger assumptions and prompts.")
    p.add_argument("--ledger", help="Ledger JSON path. Defaults to bundled synthetic example.")
    p.add_argument("--out", help="Optional JSON output path.")
    p.set_defaults(func=cmd_review_ledger)

    p = sub.add_parser("static-dashboard", help="Build the static no-JavaScript HTML dashboard.")
    add_common_inputs(p)
    p.add_argument("--out", default="dist/dashboard", help="Output directory.")
    p.set_defaults(func=cmd_static_dashboard)

    p = sub.add_parser("scenario-gallery", help="Build JSON, Markdown, and no-JavaScript HTML scenario gallery artifacts.")
    p.add_argument("--portfolio", help="Portfolio JSON path. Defaults to bundled synthetic example.")
    p.add_argument("--ledger", help="Ledger JSON path. Defaults to bundled synthetic example.")
    p.add_argument("--assumptions", help="Assumptions JSON path. Defaults to bundled synthetic example.")
    p.add_argument("--scenarios", help="Comma-separated scenario names. Defaults to base, stress, income_shock, reserve_rebuild when present.")
    p.add_argument("--out", default="dist/scenario-gallery", help="Output directory.")
    p.set_defaults(func=cmd_scenario_gallery)

    p = sub.add_parser("assumption-audit", help="Audit portfolio, ledger, and assumption JSON for completeness and suspicious assumptions.")
    p.add_argument("--portfolio", help="Portfolio JSON path. Defaults to bundled synthetic example.")
    p.add_argument("--ledger", help="Ledger JSON path. Defaults to bundled synthetic example.")
    p.add_argument("--assumptions", help="Assumptions JSON path. Defaults to bundled synthetic example.")
    p.add_argument("--out", default="dist/assumption-audit", help="Output directory.")
    p.set_defaults(func=cmd_assumption_audit)

    p = sub.add_parser("batch-compare", help="Compare selected scenarios across a directory of portfolio JSON files.")
    p.add_argument("--portfolios-dir", required=True, help="Directory containing portfolio JSON files.")
    p.add_argument("--ledger", help="Ledger JSON path. Defaults to bundled synthetic example.")
    p.add_argument("--assumptions", help="Assumptions JSON path. Defaults to bundled synthetic example.")
    p.add_argument("--scenarios", help="Comma-separated scenario names. Defaults to bundled scenario order when present.")
    p.add_argument("--out", default="dist/batch-compare", help="Output directory.")
    p.set_defaults(func=cmd_batch_compare)

    p = sub.add_parser("casebook", help="Build deterministic Markdown, JSON, and no-JavaScript HTML release-owner casebook artifacts.")
    add_common_inputs(p)
    p.add_argument("--portfolios-dir", help="Directory containing portfolio JSON files for the batch summary. Defaults to bundled synthetic examples.")
    p.add_argument("--scenarios", help="Comma-separated scenario names for gallery and batch summaries. Defaults to bundled gallery scenarios.")
    p.add_argument("--out", default="dist/casebook", help="Output directory.")
    p.set_defaults(func=cmd_casebook)

    p = sub.add_parser("artifact-catalog", help="Catalog demo/docs artifacts with sizes, sha256 hashes, and regeneration commands.")
    p.add_argument("--root", default=".", help="Repository root.")
    p.add_argument("--paths", default="demo,docs", help="Comma-separated root-relative paths to catalog.")
    p.add_argument("--out", help="Optional output directory for artifact_catalog.json and artifact_catalog.md.")
    p.set_defaults(func=cmd_artifact_catalog)

    p = sub.add_parser("release-check", help="Validate expected files, public scan, and no-script generated HTML.")
    p.add_argument("--root", default=".", help="Repository root.")
    p.add_argument("--out", help="Optional output directory for release_check.json and release_check.md.")
    p.set_defaults(func=cmd_release_check)

    p = sub.add_parser("visual-receipt", help="Write a compact deterministic Markdown receipt for packet review.")
    add_common_inputs(p)
    p.add_argument("--out", default="demo/visual_receipt.md", help="Receipt Markdown output path.")
    p.add_argument("--packet-out", default="dist/packet", help="Packet output path to show in regeneration commands.")
    p.set_defaults(func=cmd_visual_receipt)

    p = sub.add_parser("quickstart-check", help="Copy bundled examples and build a packet from an empty directory.")
    p.add_argument("--out", default="quickstart-output", help="Output directory for example files and packet.")
    p.set_defaults(func=cmd_quickstart_check)

    p = sub.add_parser("selfcheck", help="Run deterministic smoke checks against bundled examples.")
    p.set_defaults(func=cmd_selfcheck)

    p = sub.add_parser("public-scan", help="Scan repo for public-release concerns.")
    p.add_argument("--root", default=".", help="Repository root.")
    p.add_argument("--out", help="Optional JSON output path.")
    p.set_defaults(func=cmd_public_scan)

    p = sub.add_parser("release-manifest", help="Emit a deterministic manifest for release review.")
    p.add_argument("--root", default=".", help="Repository root.")
    p.add_argument("--out", help="Optional JSON output path.")
    p.set_defaults(func=cmd_release_manifest)

    p = sub.add_parser("maturity-report", help="Report basic repo maturity checks.")
    p.add_argument("--root", default=".", help="Repository root.")
    p.add_argument("--out", help="Optional JSON output path.")
    p.set_defaults(func=cmd_maturity_report)
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
