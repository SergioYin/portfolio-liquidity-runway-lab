from __future__ import annotations

import csv
import hashlib
import html
import json
import re
import shutil
import tempfile
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Tuple

LIQUIDITY_ORDER = ("same_day", "one_week", "one_month", "locked")
LIQUIDITY_LABELS = {
    "same_day": "Same day",
    "one_week": "One week",
    "one_month": "One month",
    "locked": "Locked or gated",
}
BOUNDARY_TEXT = (
    "Educational static analysis only. This tool uses local synthetic or user-supplied inputs, "
    "does not fetch live data, does not connect to brokers, does not place orders, and does not "
    "provide tax, legal, investment, buy, sell, or hold advice."
)
FORBIDDEN_PUBLIC_TERMS = tuple(
    "_".join(parts)
    for parts in (
        ("api", "key"),
        ("secret", "key"),
        ("private", "key"),
        ("pass", "word"),
        ("broker", "token"),
        ("access", "token"),
        ("refresh", "token"),
    )
)
PUBLIC_PATH_LEAK_PATTERNS = (
    ("linux_home_path", re.compile(r"(?<![\w.-])/" + r"home/[A-Za-z0-9._/-]+")),
    ("mac_home_path", re.compile(r"(?<![\w.-])/" + r"Users/[A-Za-z0-9._/-]+")),
    ("windows_user_path", re.compile(r"(?i)\b[A-Z]:\\" + r"Users\\[A-Za-z0-9._ -]+(?:\\[^\s\"'`<>|]+)*")),
    ("tmp_path", re.compile(r"(?<![\w.-])/" + r"tmp/[A-Za-z0-9._/-]+")),
)
PROVIDER_TOKEN_PATTERNS = (
    ("aws_access_key_id", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("github_classic_token", re.compile(r"\bghp_[A-Za-z0-9_]{20,}\b")),
    ("github_fine_grained_token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    ("openai_token", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("private_key_block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
)
ENV_SECRET_LABEL_PATTERN = re.compile(
    r"(?im)^\s*(?:export\s+)?(?:"
    r"OPENAI_API_KEY|AWS_SECRET_ACCESS_KEY|GITHUB_TOKEN|"
    r"API[_-]?KEY|SECRET[_-]?KEY|PRIVATE[_-]?KEY|PASSWORD|"
    r"BROKER[_-]?TOKEN|ACCESS[_-]?TOKEN|REFRESH[_-]?TOKEN|accessToken"
    r")\s*[:=]\s*[^\s#<>{}\[\]\"']{8,}"
)
AUTH_HEADER_PATTERN = re.compile(r"(?im)^\s*Authorization\s*:\s*Bearer\s+[A-Za-z0-9._~+/=-]{10,}")
HTML_SAFETY_PATTERNS = (
    ("script_tag", re.compile(r"<\s*script\b", re.IGNORECASE)),
    ("event_handler", re.compile(r"\son[a-z]+\s*=", re.IGNORECASE)),
    ("javascript_url", re.compile(r"javascript\s*:", re.IGNORECASE)),
    ("iframe_tag", re.compile(r"<\s*iframe\b", re.IGNORECASE)),
    ("object_tag", re.compile(r"<\s*object\b", re.IGNORECASE)),
    ("embed_tag", re.compile(r"<\s*embed\b", re.IGNORECASE)),
    ("form_tag", re.compile(r"<\s*form\b", re.IGNORECASE)),
    ("meta_refresh", re.compile(r"<\s*meta\b[^>]*http-equiv\s*=\s*['\"]?\s*refresh", re.IGNORECASE)),
    ("external_network_url", re.compile(r"\b(?:href|src|action)\s*=\s*['\"]\s*https?://", re.IGNORECASE)),
)
CSV_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


@dataclass(frozen=True)
class PacketPaths:
    out_dir: Path
    json_path: Path
    markdown_path: Path
    html_path: Path


@dataclass(frozen=True)
class ScenarioGalleryPaths:
    out_dir: Path
    json_path: Path
    markdown_path: Path
    html_path: Path


@dataclass(frozen=True)
class AuditPaths:
    out_dir: Path
    json_path: Path
    markdown_path: Path


@dataclass(frozen=True)
class BatchComparePaths:
    out_dir: Path
    json_path: Path
    markdown_path: Path
    html_path: Path


@dataclass(frozen=True)
class CasebookPaths:
    out_dir: Path
    json_path: Path
    markdown_path: Path
    html_path: Path


@dataclass(frozen=True)
class CatalogPaths:
    out_dir: Path
    json_path: Path
    markdown_path: Path


@dataclass(frozen=True)
class ReleaseCheckPaths:
    out_dir: Path
    json_path: Path
    markdown_path: Path


@dataclass(frozen=True)
class SchemaExportPaths:
    out_dir: Path
    json_path: Path
    markdown_path: Path


@dataclass(frozen=True)
class FixtureDoctorPaths:
    out_dir: Path
    json_path: Path
    markdown_path: Path
    work_dir: Path


@dataclass(frozen=True)
class DocsExportPaths:
    out_dir: Path
    index_html_path: Path
    index_markdown_path: Path


@dataclass(frozen=True)
class CommandMatrixPaths:
    out_dir: Path
    json_path: Path
    markdown_path: Path
    html_path: Path


@dataclass(frozen=True)
class GoldenReplayPaths:
    out_dir: Path
    json_path: Path
    markdown_path: Path


@dataclass(frozen=True)
class ReleaseDeckPaths:
    out_dir: Path
    markdown_path: Path
    html_path: Path


@dataclass(frozen=True)
class CsvImportPaths:
    out_dir: Path
    portfolio_json_path: Path
    ledger_json_path: Path
    report_json_path: Path
    report_markdown_path: Path


@dataclass(frozen=True)
class CsvExportPaths:
    out_dir: Path
    assets_csv_path: Path
    runway_csv_path: Path
    warnings_csv_path: Path
    bucket_summaries_csv_path: Path
    manifest_json_path: Path
    manifest_markdown_path: Path


@dataclass(frozen=True)
class BundleChecksumPaths:
    out_dir: Path
    sums_path: Path
    manifest_json_path: Path
    manifest_markdown_path: Path


@dataclass(frozen=True)
class EvidenceBundlePaths:
    out_dir: Path
    index_markdown_path: Path
    index_html_path: Path
    checksums_path: Path
    manifest_json_path: Path


@dataclass(frozen=True)
class TemplatePackPaths:
    out_dir: Path
    readme_path: Path
    manifest_json_path: Path


PROJECT_VERSION = "0.9.0"

IGNORED_RELEASE_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
}

EXPECTED_RELEASE_FILES = (
    "README.md",
    "LICENSE",
    "MANIFEST.in",
    "pyproject.toml",
    "portfolio_liquidity_runway_lab/__init__.py",
    "portfolio_liquidity_runway_lab/__main__.py",
    "portfolio_liquidity_runway_lab/cli.py",
    "portfolio_liquidity_runway_lab/core.py",
    "portfolio_liquidity_runway_lab/examples/portfolio.json",
    "portfolio_liquidity_runway_lab/examples/portfolio_concentrated.json",
    "portfolio_liquidity_runway_lab/examples/ledger.json",
    "portfolio_liquidity_runway_lab/examples/assumptions.json",
    "portfolio_liquidity_runway_lab/examples/history.json",
    "portfolio_liquidity_runway_lab/examples/portfolio.csv",
    "portfolio_liquidity_runway_lab/examples/ledger.csv",
    "docs/cold_start_walkthrough.md",
    "docs/csv_workflow.md",
    "docs/release_readiness_review.md",
    "docs/release_manifest.json",
    "docs/maturity_report.json",
    "docs/artifact_catalog.json",
    "docs/artifact_catalog.md",
    "docs/bundle-checksums/SHA256SUMS.txt",
    "docs/bundle-checksums/bundle_manifest.json",
    "docs/bundle-checksums/bundle_manifest.md",
    "docs/evidence-bundle/index.md",
    "docs/evidence-bundle/index.html",
    "docs/evidence-bundle/SHA256SUMS.txt",
    "docs/evidence-bundle/evidence_manifest.json",
    "docs/evidence-bundle/boundary_risks.md",
    "docs/evidence-bundle/command_replay.md",
    "docs/template-pack/README.md",
    "docs/template-pack/template_manifest.json",
    "docs/template-pack/portfolio.csv",
    "docs/template-pack/ledger.csv",
    "docs/template-pack/portfolio.json",
    "docs/template-pack/ledger.json",
    "docs/template-pack/assumptions.json",
    "docs/schema_guide.json",
    "docs/schema_guide.md",
    "docs/fixture_doctor.json",
    "docs/fixture_doctor.md",
    "docs/command-matrix/command_matrix.json",
    "docs/command-matrix/command_matrix.md",
    "docs/command-matrix/command_matrix.html",
    "docs/golden-replay/golden_replay.json",
    "docs/golden-replay/golden_replay.md",
    "docs/release-deck/release_deck.md",
    "docs/release-deck/release_deck.html",
    "docs/static-docs/index.html",
    "docs/static-docs/index.md",
    "docs/static-docs/command_matrix.md",
    "docs/static-docs/boundaries.md",
    "docs/static-docs/demos.md",
    "docs/static-docs/release_evidence.md",
    "demo/visual_receipt.md",
    "demo/casebook/casebook.json",
    "demo/casebook/casebook.md",
    "demo/casebook/casebook.html",
    "demo/scenario-gallery/scenario_gallery.json",
    "demo/scenario-gallery/scenario_gallery.md",
    "demo/scenario-gallery/scenario_gallery.html",
    "demo/assumption-audit/assumption_audit.json",
    "demo/assumption-audit/assumption_audit.md",
    "demo/batch-compare/batch_compare.json",
    "demo/batch-compare/batch_compare.md",
    "demo/batch-compare/batch_compare.html",
    "demo/schema-export/schema_guide.json",
    "demo/schema-export/schema_guide.md",
    "demo/fixture-doctor/fixture_doctor.json",
    "demo/fixture-doctor/fixture_doctor.md",
    "demo/command-matrix/command_matrix.json",
    "demo/command-matrix/command_matrix.md",
    "demo/command-matrix/command_matrix.html",
    "demo/golden-replay/golden_replay.json",
    "demo/golden-replay/golden_replay.md",
    "demo/release-deck/release_deck.md",
    "demo/release-deck/release_deck.html",
    "demo/csv-import/portfolio.json",
    "demo/csv-import/ledger.json",
    "demo/csv-import/import_report.json",
    "demo/csv-import/import_report.md",
    "demo/csv-export-packet/liquidity_packet.json",
    "demo/csv-export-packet/liquidity_packet.md",
    "demo/csv-export-packet/liquidity_packet.html",
    "demo/csv-export/assets.csv",
    "demo/csv-export/runway.csv",
    "demo/csv-export/warnings.csv",
    "demo/csv-export/bucket_summaries.csv",
    "demo/csv-export/export_manifest.json",
    "demo/csv-export/export_manifest.md",
    "demo/bundle-checksums/SHA256SUMS.txt",
    "demo/bundle-checksums/bundle_manifest.json",
    "demo/bundle-checksums/bundle_manifest.md",
    "demo/evidence-bundle/index.md",
    "demo/evidence-bundle/index.html",
    "demo/evidence-bundle/SHA256SUMS.txt",
    "demo/evidence-bundle/evidence_manifest.json",
    "demo/evidence-bundle/boundary_risks.md",
    "demo/evidence-bundle/command_replay.md",
    "demo/template-pack/README.md",
    "demo/template-pack/template_manifest.json",
    "demo/template-pack/portfolio.csv",
    "demo/template-pack/ledger.csv",
    "demo/template-pack/portfolio.json",
    "demo/template-pack/ledger.json",
    "demo/template-pack/assumptions.json",
    "demo/static-docs/index.html",
    "demo/static-docs/index.md",
    "demo/static-docs/command_matrix.md",
    "demo/static-docs/boundaries.md",
    "demo/static-docs/demos.md",
    "demo/static-docs/release_evidence.md",
    "skills/agent/portfolio-liquidity-runway-lab/SKILL.md",
    "tests/test_cli.py",
    "tests/test_core.py",
)


def _is_ignored_release_path(path: Path) -> bool:
    return any(part in IGNORED_RELEASE_PARTS or part.endswith(".egg-info") for part in path.parts)


def bundled_example_path(name: str) -> Path:
    if not name.endswith(".json"):
        name = f"{name}.json"
    return Path(str(resources.files(__package__).joinpath("examples", name)))


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def dump_json(data: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")


def bundled_csv_example_path(name: str) -> Path:
    if not name.endswith(".csv"):
        name = f"{name}.csv"
    return Path(str(resources.files(__package__).joinpath("examples", name)))


def _read_csv_dicts(path: Path) -> Tuple[List[Dict[str, str]], List[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        rows = [{key: (value or "").strip() for key, value in row.items() if key is not None} for row in reader]
    return rows, fieldnames


def _lint_error(code: str, location: str, message: str, remediation: str, schema_ref: str) -> Dict[str, str]:
    return {
        "severity": "error",
        "code": code,
        "location": location,
        "message": message,
        "remediation": remediation,
        "schema_ref": schema_ref,
    }


def _lint_warning(code: str, location: str, message: str, remediation: str, schema_ref: str) -> Dict[str, str]:
    return {
        "severity": "warning",
        "code": code,
        "location": location,
        "message": message,
        "remediation": remediation,
        "schema_ref": schema_ref,
    }


def _parse_required_number(value: str, location: str, findings: List[Dict[str, str]], schema_ref: str) -> float:
    if value == "":
        findings.append(
            _lint_error("missing_number", location, "Required numeric value is blank.", "Provide a decimal number.", schema_ref)
        )
        return 0.0
    try:
        return float(value)
    except ValueError:
        findings.append(
            _lint_error("invalid_number", location, f"Value {value!r} is not numeric.", "Use a plain decimal number without currency symbols.", schema_ref)
        )
        return 0.0


def _parse_required_int(value: str, location: str, findings: List[Dict[str, str]], schema_ref: str) -> int:
    number = _parse_required_number(value, location, findings, schema_ref)
    if int(number) != number:
        findings.append(_lint_error("invalid_integer", location, "Value must be an integer.", "Use a whole-number month.", schema_ref))
    return int(number)


def validate_portfolio_csv(path: Path) -> Dict[str, Any]:
    required = ["name", "value", "liquidity_tier", "annual_yield_rate", "annual_fee_rate"]
    rows, fieldnames = _read_csv_dicts(path)
    findings: List[Dict[str, str]] = []
    for field in required:
        if field not in fieldnames:
            findings.append(
                _lint_error(
                    "missing_column",
                    f"{path.name}:{field}",
                    f"Portfolio CSV is missing column {field!r}.",
                    f"Add a {field} column.",
                    f"csv.portfolio.{field}",
                )
            )
    for row_index, row in enumerate(rows, start=2):
        tier = row.get("liquidity_tier", "")
        if tier not in LIQUIDITY_ORDER:
            findings.append(
                _lint_error(
                    "invalid_liquidity_tier",
                    f"{path.name}:row {row_index}:liquidity_tier",
                    f"Unknown liquidity tier {tier!r}.",
                    "Use one of: " + ", ".join(LIQUIDITY_ORDER) + ".",
                    "portfolio.assets[].liquidity_tier",
                )
            )
        for field in ("value", "annual_yield_rate", "annual_fee_rate"):
            _parse_required_number(row.get(field, ""), f"{path.name}:row {row_index}:{field}", findings, f"portfolio.assets[].{field}")
    if not rows:
        findings.append(
            _lint_error("empty_csv", path.name, "Portfolio CSV has no asset rows.", "Add at least one asset row.", "portfolio.assets")
        )
    return {"path": path.as_posix(), "kind": "portfolio_csv", "status": "pass" if not findings else "fail", "row_count": len(rows), "findings": findings}


def validate_ledger_csv(path: Path) -> Dict[str, Any]:
    required = ["record_type", "monthly_income", "monthly_expenses", "month", "type", "label", "amount"]
    rows, fieldnames = _read_csv_dicts(path)
    findings: List[Dict[str, str]] = []
    for field in required:
        if field not in fieldnames:
            findings.append(
                _lint_error("missing_column", f"{path.name}:{field}", f"Ledger CSV is missing column {field!r}.", f"Add a {field} column.", f"csv.ledger.{field}")
            )
    settings_rows = [row for row in rows if row.get("record_type", "").lower() == "settings"]
    if len(settings_rows) != 1:
        findings.append(
            _lint_error(
                "invalid_settings_count",
                f"{path.name}:record_type",
                "Ledger CSV must contain exactly one settings row.",
                "Add one row with record_type=settings and monthly income/expenses.",
                "ledger.monthly_income",
            )
        )
    for row_index, row in enumerate(rows, start=2):
        record_type = row.get("record_type", "").lower()
        if record_type not in {"settings", "event"}:
            findings.append(
                _lint_error("invalid_record_type", f"{path.name}:row {row_index}:record_type", f"Unknown record type {record_type!r}.", "Use settings or event.", "csv.ledger.record_type")
            )
        if record_type == "settings":
            _parse_required_number(row.get("monthly_income", ""), f"{path.name}:row {row_index}:monthly_income", findings, "ledger.monthly_income")
            _parse_required_number(row.get("monthly_expenses", ""), f"{path.name}:row {row_index}:monthly_expenses", findings, "ledger.monthly_expenses")
        if record_type == "event":
            _parse_required_int(row.get("month", ""), f"{path.name}:row {row_index}:month", findings, "ledger.scheduled_events[].month")
            kind = row.get("type", "").lower()
            if kind not in {"inflow", "outflow"}:
                findings.append(
                    _lint_error("invalid_event_type", f"{path.name}:row {row_index}:type", f"Unknown event type {kind!r}.", "Use inflow or outflow.", "ledger.scheduled_events[].type")
                )
            _parse_required_number(row.get("amount", ""), f"{path.name}:row {row_index}:amount", findings, "ledger.scheduled_events[].amount")
    return {"path": path.as_posix(), "kind": "ledger_csv", "status": "pass" if not findings else "fail", "row_count": len(rows), "findings": findings}


def portfolio_from_csv(path: Path, portfolio_name: str = "Imported CSV portfolio", currency: str = "USD") -> Tuple[Dict[str, Any], Dict[str, Any]]:
    validation = validate_portfolio_csv(path)
    if validation["status"] != "pass":
        raise ValueError(f"portfolio CSV failed validation with {len(validation['findings'])} error(s)")
    rows, _fieldnames = _read_csv_dicts(path)
    assets = []
    for row in rows:
        assets.append(
            {
                "annual_fee_rate": round(float(row["annual_fee_rate"]), 8),
                "annual_yield_rate": round(float(row["annual_yield_rate"]), 8),
                "liquidity_tier": row["liquidity_tier"],
                "name": row.get("name", "") or "Imported asset",
                "value": round(float(row["value"]), 2),
            }
        )
    assets.sort(key=lambda item: (LIQUIDITY_ORDER.index(item["liquidity_tier"]), item["name"]))
    return {"assets": assets, "currency": currency, "name": portfolio_name}, validation


def ledger_from_csv(path: Path) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    validation = validate_ledger_csv(path)
    if validation["status"] != "pass":
        raise ValueError(f"ledger CSV failed validation with {len(validation['findings'])} error(s)")
    rows, _fieldnames = _read_csv_dicts(path)
    settings = next(row for row in rows if row.get("record_type", "").lower() == "settings")
    events = []
    for row in rows:
        if row.get("record_type", "").lower() != "event":
            continue
        events.append(
            {
                "amount": round(float(row["amount"]), 2),
                "label": row.get("label", "") or "Imported event",
                "month": int(float(row["month"])),
                "type": row["type"].lower(),
            }
        )
    events.sort(key=lambda item: (item["month"], item["type"], item["label"]))
    return {
        "monthly_expenses": round(float(settings["monthly_expenses"]), 2),
        "monthly_income": round(float(settings["monthly_income"]), 2),
        "scheduled_events": events,
    }, validation


def render_csv_import_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# CSV Import Report",
        "",
        f"> {report['boundary']}",
        "",
        f"Status: `{report['status']}`",
        "",
        "## Outputs",
        "",
        f"- Portfolio JSON: `{report['outputs']['portfolio_json']}`",
        f"- Ledger JSON: `{report['outputs']['ledger_json']}`",
        "",
        "## Row Counts",
        "",
        f"- Portfolio rows: `{report['row_counts']['portfolio_assets']}`",
        f"- Ledger events: `{report['row_counts']['ledger_events']}`",
        "",
        "## Validation",
        "",
    ]
    findings = report["findings"]
    if findings:
        for finding in findings:
            lines.append(f"- `{finding['severity']}` `{finding['schema_ref']}` {finding['location']}: {finding['message']} Remediation: {finding['remediation']}")
    else:
        lines.append("- No validation findings.")
    lines.append("")
    return "\n".join(lines)


def build_csv_import(portfolio_csv: Path, ledger_csv: Path, out_dir: Path, portfolio_name: str = "Imported CSV portfolio", currency: str = "USD") -> CsvImportPaths:
    portfolio, portfolio_validation = portfolio_from_csv(portfolio_csv, portfolio_name, currency)
    ledger, ledger_validation = ledger_from_csv(ledger_csv)
    out_dir.mkdir(parents=True, exist_ok=True)
    portfolio_json_path = out_dir / "portfolio.json"
    ledger_json_path = out_dir / "ledger.json"
    report_json_path = out_dir / "import_report.json"
    report_markdown_path = out_dir / "import_report.md"
    dump_json(portfolio, portfolio_json_path)
    dump_json(ledger, ledger_json_path)
    report = {
        "boundary": BOUNDARY_TEXT,
        "status": "pass",
        "inputs": {"portfolio_csv": portfolio_csv.name, "ledger_csv": ledger_csv.name},
        "outputs": {"portfolio_json": portfolio_json_path.name, "ledger_json": ledger_json_path.name},
        "row_counts": {"portfolio_assets": len(portfolio["assets"]), "ledger_events": len(ledger["scheduled_events"])},
        "schema_refs": ["portfolio.assets[]", "ledger.monthly_income", "ledger.monthly_expenses", "ledger.scheduled_events[]"],
        "findings": portfolio_validation["findings"] + ledger_validation["findings"],
    }
    dump_json(report, report_json_path)
    report_markdown_path.write_text(render_csv_import_markdown(report), encoding="utf-8")
    return CsvImportPaths(out_dir, portfolio_json_path, ledger_json_path, report_json_path, report_markdown_path)


def _csv_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def _write_ordered_csv(rows: List[Mapping[str, Any]], path: Path, fields: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: _csv_text(row.get(field, "")) for field in fields})


def render_csv_export_manifest_markdown(manifest: Mapping[str, Any]) -> str:
    lines = [
        "# CSV Export Manifest",
        "",
        f"> {manifest['boundary']}",
        "",
        f"Status: `{manifest['status']}`",
        f"Scenario: `{manifest['scenario']}`",
        f"Portfolio: `{manifest['portfolio_name']}`",
        "",
        "## Files",
        "",
        "| File | Rows | SHA256 |",
        "| --- | ---: | --- |",
    ]
    for item in manifest["files"]:
        lines.append(f"| `{item['path']}` | {item['rows']} | `{item['sha256']}` |")
    lines.append("")
    return "\n".join(lines)


def build_csv_export(packet_json: Path, out_dir: Path) -> CsvExportPaths:
    packet = load_json(packet_json)
    out_dir.mkdir(parents=True, exist_ok=True)
    assets_path = out_dir / "assets.csv"
    runway_path = out_dir / "runway.csv"
    warnings_path = out_dir / "warnings.csv"
    bucket_path = out_dir / "bucket_summaries.csv"
    manifest_json_path = out_dir / "export_manifest.json"
    manifest_markdown_path = out_dir / "export_manifest.md"
    _write_ordered_csv(
        list(packet.get("assets", [])),
        assets_path,
        ["name", "tier", "gross", "haircut_value", "annual_yield", "annual_fee"],
    )
    _write_ordered_csv(
        list(packet.get("monthly_runway", [])),
        runway_path,
        ["month", "scheduled_inflows", "scheduled_outflows", "net_burn", "liquid_balance_after"],
    )
    warnings = [{"index": index + 1, "warning": warning} for index, warning in enumerate(packet.get("forced_sale_warnings", []))]
    _write_ordered_csv(warnings, warnings_path, ["index", "warning"])
    buckets = []
    for tier in LIQUIDITY_ORDER:
        bucket = packet.get("cash_buckets", {}).get(tier, {})
        buckets.append(
            {
                "tier": tier,
                "label": bucket.get("label", LIQUIDITY_LABELS[tier]),
                "count": bucket.get("count", 0),
                "gross": bucket.get("gross", 0),
                "stress_haircut_value": bucket.get("stress_haircut_value", 0),
            }
        )
    _write_ordered_csv(buckets, bucket_path, ["tier", "label", "count", "gross", "stress_haircut_value"])
    file_rows = [
        (assets_path, len(packet.get("assets", []))),
        (runway_path, len(packet.get("monthly_runway", []))),
        (warnings_path, len(warnings)),
        (bucket_path, len(buckets)),
    ]
    manifest = {
        "boundary": BOUNDARY_TEXT,
        "status": "pass",
        "packet": packet_json.name,
        "portfolio_name": packet.get("portfolio_name", ""),
        "scenario": packet.get("scenario", ""),
        "files": [{"path": path.name, "rows": rows, "sha256": _sha256_file(path)} for path, rows in file_rows],
    }
    dump_json(manifest, manifest_json_path)
    manifest_markdown_path.write_text(render_csv_export_manifest_markdown(manifest), encoding="utf-8")
    return CsvExportPaths(out_dir, assets_path, runway_path, warnings_path, bucket_path, manifest_json_path, manifest_markdown_path)


def validate_portfolio_json(path: Path) -> Dict[str, Any]:
    findings: List[Dict[str, str]] = []
    try:
        data = load_json(path)
    except Exception as exc:
        return {
            "path": path.as_posix(),
            "kind": "portfolio_json",
            "status": "fail",
            "findings": [_lint_error("invalid_json", path.name, str(exc), "Write a valid JSON object.", "portfolio.json")],
        }
    assets = data.get("assets")
    if not isinstance(assets, list) or not assets:
        findings.append(_lint_error("invalid_assets", "portfolio.assets", "assets must be a non-empty list.", "Add asset objects under assets.", "portfolio.assets"))
        assets = []
    for index, asset in enumerate(assets):
        location = f"portfolio.assets[{index}]"
        if not isinstance(asset, dict):
            findings.append(_lint_error("invalid_asset", location, "Asset row must be an object.", "Replace the row with an object.", "portfolio.assets[]"))
            continue
        tier = asset.get("liquidity_tier")
        if tier not in LIQUIDITY_ORDER:
            findings.append(_lint_error("invalid_liquidity_tier", f"{location}.liquidity_tier", f"Unknown liquidity tier {tier!r}.", "Use one of: " + ", ".join(LIQUIDITY_ORDER) + ".", "portfolio.assets[].liquidity_tier"))
        for field in ("value", "annual_yield_rate", "annual_fee_rate"):
            try:
                _as_number(asset.get(field), f"{location}.{field}")
            except ValueError as exc:
                findings.append(_lint_error("invalid_number", f"{location}.{field}", str(exc), "Use a JSON number.", f"portfolio.assets[].{field}"))
    return {"path": path.as_posix(), "kind": "portfolio_json", "status": "pass" if not findings else "fail", "findings": findings}


def validate_ledger_json(path: Path) -> Dict[str, Any]:
    findings: List[Dict[str, str]] = []
    try:
        data = load_json(path)
    except Exception as exc:
        return {
            "path": path.as_posix(),
            "kind": "ledger_json",
            "status": "fail",
            "findings": [_lint_error("invalid_json", path.name, str(exc), "Write a valid JSON object.", "ledger.json")],
        }
    for field in ("monthly_income", "monthly_expenses"):
        try:
            _as_number(data.get(field), f"ledger.{field}")
        except ValueError as exc:
            findings.append(_lint_error("invalid_number", f"ledger.{field}", str(exc), "Use a JSON number.", f"ledger.{field}"))
    events = data.get("scheduled_events", [])
    if not isinstance(events, list):
        findings.append(_lint_error("invalid_events", "ledger.scheduled_events", "scheduled_events must be a list.", "Use an array of event objects.", "ledger.scheduled_events"))
        events = []
    for index, event in enumerate(events):
        location = f"ledger.scheduled_events[{index}]"
        if not isinstance(event, dict):
            findings.append(_lint_error("invalid_event", location, "Event must be an object.", "Replace the row with an object.", "ledger.scheduled_events[]"))
            continue
        try:
            month = _as_number(event.get("month"), f"{location}.month")
            if int(month) != month:
                findings.append(_lint_error("invalid_integer", f"{location}.month", "month must be an integer.", "Use a whole-number month.", "ledger.scheduled_events[].month"))
        except ValueError as exc:
            findings.append(_lint_error("invalid_number", f"{location}.month", str(exc), "Use a JSON number.", "ledger.scheduled_events[].month"))
        if event.get("type") not in {"inflow", "outflow"}:
            findings.append(_lint_error("invalid_event_type", f"{location}.type", f"Unknown event type {event.get('type')!r}.", "Use inflow or outflow.", "ledger.scheduled_events[].type"))
        try:
            _as_number(event.get("amount"), f"{location}.amount")
        except ValueError as exc:
            findings.append(_lint_error("invalid_number", f"{location}.amount", str(exc), "Use a JSON number.", "ledger.scheduled_events[].amount"))
    return {"path": path.as_posix(), "kind": "ledger_json", "status": "pass" if not findings else "fail", "findings": findings}


def validate_assumptions_json(path: Path) -> Dict[str, Any]:
    findings: List[Dict[str, str]] = []
    try:
        data = load_json(path)
    except Exception as exc:
        return {
            "path": path.as_posix(),
            "kind": "assumptions_json",
            "status": "fail",
            "findings": [_lint_error("invalid_json", path.name, str(exc), "Write a valid JSON object.", "assumptions.json")],
        }
    for field in ("months", "target_reserve_months"):
        try:
            _as_number(data.get(field), f"assumptions.{field}")
        except ValueError as exc:
            findings.append(_lint_error("invalid_number", f"assumptions.{field}", str(exc), "Use a JSON number.", f"assumptions.{field}"))
    scenarios = data.get("scenarios")
    if not isinstance(scenarios, dict) or not scenarios:
        findings.append(_lint_error("invalid_scenarios", "assumptions.scenarios", "scenarios must be a non-empty object.", "Add named scenario objects.", "assumptions.scenarios"))
        scenarios = {}
    for name, scenario in scenarios.items():
        location = f"assumptions.scenarios.{name}"
        if not isinstance(scenario, dict):
            findings.append(_lint_error("invalid_scenario", location, "Scenario must be an object.", "Replace with a scenario object.", "assumptions.scenarios.<name>"))
            continue
        for field in ("expense_multiplier", "income_multiplier"):
            try:
                _as_number(scenario.get(field), f"{location}.{field}")
            except ValueError as exc:
                findings.append(_lint_error("invalid_number", f"{location}.{field}", str(exc), "Use a JSON number.", f"assumptions.scenarios.<name>.{field}"))
        haircuts = scenario.get("liquidity_haircuts")
        if not isinstance(haircuts, dict):
            findings.append(_lint_error("invalid_haircuts", f"{location}.liquidity_haircuts", "liquidity_haircuts must be an object.", "Add haircut values for every liquidity tier.", "assumptions.scenarios.<name>.liquidity_haircuts"))
            haircuts = {}
        for tier in LIQUIDITY_ORDER:
            try:
                _as_number(haircuts.get(tier), f"{location}.liquidity_haircuts.{tier}")
            except ValueError as exc:
                findings.append(_lint_error("invalid_number", f"{location}.liquidity_haircuts.{tier}", str(exc), "Use a JSON number from 0 to 1.", f"assumptions.scenarios.<name>.liquidity_haircuts.{tier}"))
    return {"path": path.as_posix(), "kind": "assumptions_json", "status": "pass" if not findings else "fail", "findings": findings}


def input_lint(paths: Iterable[Tuple[Path, str]]) -> Dict[str, Any]:
    results = []
    for path, kind in paths:
        if kind == "portfolio_json":
            results.append(validate_portfolio_json(path))
        elif kind == "ledger_json":
            results.append(validate_ledger_json(path))
        elif kind == "assumptions_json":
            results.append(validate_assumptions_json(path))
        elif kind == "portfolio_csv":
            results.append(validate_portfolio_csv(path))
        elif kind == "ledger_csv":
            results.append(validate_ledger_csv(path))
        else:
            results.append(
                {
                    "path": path.as_posix(),
                    "kind": kind,
                    "status": "fail",
                    "findings": [_lint_error("unknown_kind", path.name, f"Unknown lint kind {kind!r}.", "Use a supported input kind.", "input-lint.kind")],
                }
            )
    findings = [finding for result in results for finding in result["findings"]]
    return {
        "boundary": BOUNDARY_TEXT,
        "status": "pass" if not any(finding["severity"] == "error" for finding in findings) else "fail",
        "results": results,
        "finding_counts": {
            "error": sum(1 for finding in findings if finding["severity"] == "error"),
            "warning": sum(1 for finding in findings if finding["severity"] == "warning"),
        },
    }


def money(value: float) -> str:
    return f"${value:,.2f}"


def months(value: float) -> str:
    if value == float("inf"):
        return "infinite"
    return f"{value:.1f}"


def _as_number(value: Any, field: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be numeric") from exc


def _maybe_number(value: Any) -> Optional[float]:
    if isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _iter_items(portfolio: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
    items = portfolio.get("assets", [])
    if not isinstance(items, list):
        raise ValueError("portfolio.assets must be a list")
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"portfolio.assets[{index}] must be an object")
        yield item


def _schedule_totals(ledger: Mapping[str, Any], months_count: int) -> Tuple[List[Dict[str, Any]], List[float], List[float]]:
    events = ledger.get("scheduled_events", [])
    if not isinstance(events, list):
        raise ValueError("ledger.scheduled_events must be a list")
    normalized: List[Dict[str, Any]] = []
    inflows = [0.0 for _ in range(months_count)]
    outflows = [0.0 for _ in range(months_count)]
    for index, event in enumerate(events):
        if not isinstance(event, dict):
            raise ValueError(f"scheduled_events[{index}] must be an object")
        month = int(_as_number(event.get("month", 0), f"scheduled_events[{index}].month"))
        amount = _as_number(event.get("amount", 0), f"scheduled_events[{index}].amount")
        kind = str(event.get("type", "")).strip().lower()
        label = str(event.get("label", f"event {index + 1}"))
        if month < 1 or month > months_count:
            continue
        if kind == "inflow":
            inflows[month - 1] += amount
        elif kind == "outflow":
            outflows[month - 1] += amount
        else:
            raise ValueError(f"scheduled_events[{index}].type must be inflow or outflow")
        normalized.append({"month": month, "type": kind, "label": label, "amount": round(amount, 2)})
    normalized.sort(key=lambda item: (item["month"], item["type"], item["label"]))
    return normalized, inflows, outflows


def analyze(
    portfolio: Mapping[str, Any],
    ledger: Mapping[str, Any],
    assumptions: Mapping[str, Any],
    scenario_name: Optional[str] = None,
) -> Dict[str, Any]:
    monthly_expenses = _as_number(ledger.get("monthly_expenses", 0), "ledger.monthly_expenses")
    monthly_income = _as_number(ledger.get("monthly_income", 0), "ledger.monthly_income")
    months_count = int(_as_number(assumptions.get("months", 12), "assumptions.months"))
    if months_count < 1:
        raise ValueError("assumptions.months must be at least 1")

    scenarios = assumptions.get("scenarios", {})
    if scenarios is None:
        scenarios = {}
    if not isinstance(scenarios, dict):
        raise ValueError("assumptions.scenarios must be an object")
    scenario = scenarios.get(scenario_name or assumptions.get("default_scenario", "base"), {})
    if not isinstance(scenario, dict):
        raise ValueError("selected scenario must be an object")

    expense_multiplier = _as_number(scenario.get("expense_multiplier", 1), "scenario.expense_multiplier")
    income_multiplier = _as_number(scenario.get("income_multiplier", 1), "scenario.income_multiplier")
    liquidity_haircuts = scenario.get("liquidity_haircuts", {})
    if not isinstance(liquidity_haircuts, dict):
        raise ValueError("scenario.liquidity_haircuts must be an object")

    buckets = {tier: {"count": 0, "gross": 0.0, "haircut_value": 0.0} for tier in LIQUIDITY_ORDER}
    assets: List[Dict[str, Any]] = []
    total_gross = 0.0
    total_haircut = 0.0
    annual_yield = 0.0
    annual_fees = 0.0
    for index, item in enumerate(_iter_items(portfolio)):
        tier = str(item.get("liquidity_tier", "locked"))
        if tier not in buckets:
            raise ValueError(f"asset {index + 1} has unknown liquidity_tier {tier!r}")
        value = _as_number(item.get("value", 0), f"asset {index + 1}.value")
        yield_rate = _as_number(item.get("annual_yield_rate", 0), f"asset {index + 1}.annual_yield_rate")
        fee_rate = _as_number(item.get("annual_fee_rate", 0), f"asset {index + 1}.annual_fee_rate")
        haircut = _as_number(liquidity_haircuts.get(tier, 0), f"haircut {tier}")
        haircut_value = value * max(0.0, 1.0 - haircut)
        total_gross += value
        total_haircut += haircut_value
        annual_yield += value * yield_rate
        annual_fees += value * fee_rate
        buckets[tier]["count"] += 1
        buckets[tier]["gross"] += value
        buckets[tier]["haircut_value"] += haircut_value
        assets.append(
            {
                "name": str(item.get("name", f"Asset {index + 1}")),
                "tier": tier,
                "gross": round(value, 2),
                "haircut_value": round(haircut_value, 2),
                "annual_yield": round(value * yield_rate, 2),
                "annual_fee": round(value * fee_rate, 2),
            }
        )

    events, inflows, outflows = _schedule_totals(ledger, months_count)
    base_income = monthly_income * income_multiplier
    base_expenses = monthly_expenses * expense_multiplier
    net_base_burn = base_expenses - base_income
    monthly_yield = annual_yield / 12.0
    monthly_fees = annual_fees / 12.0
    effective_monthly_burn = net_base_burn - monthly_yield + monthly_fees

    monthly_rows: List[Dict[str, Any]] = []
    balance = buckets["same_day"]["haircut_value"] + buckets["one_week"]["haircut_value"]
    forced_sale_warnings: List[str] = []
    first_negative_month: Optional[int] = None
    for month_index in range(months_count):
        inflow = inflows[month_index]
        outflow = outflows[month_index]
        net_burn = effective_monthly_burn + outflow - inflow
        balance -= net_burn
        row = {
            "month": month_index + 1,
            "scheduled_inflows": round(inflow, 2),
            "scheduled_outflows": round(outflow, 2),
            "net_burn": round(net_burn, 2),
            "liquid_balance_after": round(balance, 2),
        }
        monthly_rows.append(row)
        if balance < 0 and first_negative_month is None:
            first_negative_month = month_index + 1
            forced_sale_warnings.append(
                f"Liquid balance turns negative in month {first_negative_month}; review whether one_month or locked holdings would be needed."
            )

    same_day = buckets["same_day"]["haircut_value"]
    liquid_30 = same_day + buckets["one_week"]["haircut_value"] + buckets["one_month"]["haircut_value"]
    reserve_months = 0.0 if base_expenses <= 0 else same_day / base_expenses
    liquid_runway = float("inf") if effective_monthly_burn <= 0 else (
        buckets["same_day"]["haircut_value"] + buckets["one_week"]["haircut_value"]
    ) / effective_monthly_burn
    thirty_day_runway = float("inf") if effective_monthly_burn <= 0 else liquid_30 / effective_monthly_burn

    target_reserve = _as_number(assumptions.get("target_reserve_months", 6), "assumptions.target_reserve_months")
    if reserve_months < target_reserve:
        forced_sale_warnings.append(
            f"Same-day reserve is {reserve_months:.1f} months, below the {target_reserve:.1f} month review threshold."
        )
    if buckets["locked"]["gross"] > total_gross * 0.35 and effective_monthly_burn > 0:
        forced_sale_warnings.append("Locked or gated assets exceed 35% of gross assets while burn is positive.")

    prompts = [
        "Confirm each liquidity tier against account restrictions and settlement timing.",
        "Check that scheduled inflows and outflows are documented and still expected.",
        "Review whether fees, yields, and stress haircuts are assumptions rather than live quotes.",
        "Escalate to a qualified professional for tax, legal, investment, or brokerage decisions.",
    ]

    scenario_label = scenario_name or str(assumptions.get("default_scenario", "base"))
    return {
        "boundary": BOUNDARY_TEXT,
        "scenario": scenario_label,
        "portfolio_name": str(portfolio.get("name", "Synthetic portfolio")),
        "currency": str(portfolio.get("currency", "USD")),
        "totals": {
            "gross_assets": round(total_gross, 2),
            "stress_haircut_assets": round(total_haircut, 2),
            "annual_yield_assumption": round(annual_yield, 2),
            "annual_fee_assumption": round(annual_fees, 2),
            "monthly_net_burn_before_yield_fee": round(net_base_burn, 2),
            "monthly_yield_assumption": round(monthly_yield, 2),
            "monthly_fee_assumption": round(monthly_fees, 2),
            "effective_monthly_burn": round(effective_monthly_burn, 2),
            "same_day_reserve_months": round(reserve_months, 2),
            "same_day_one_week_runway_months": None if liquid_runway == float("inf") else round(liquid_runway, 2),
            "thirty_day_runway_months": None if thirty_day_runway == float("inf") else round(thirty_day_runway, 2),
        },
        "cash_buckets": {
            tier: {
                "label": LIQUIDITY_LABELS[tier],
                "count": buckets[tier]["count"],
                "gross": round(buckets[tier]["gross"], 2),
                "stress_haircut_value": round(buckets[tier]["haircut_value"], 2),
            }
            for tier in LIQUIDITY_ORDER
        },
        "assets": sorted(assets, key=lambda item: (LIQUIDITY_ORDER.index(item["tier"]), item["name"])),
        "scheduled_events": events,
        "monthly_runway": monthly_rows,
        "forced_sale_warnings": forced_sale_warnings,
        "review_prompts": prompts,
    }


def render_markdown(packet: Mapping[str, Any]) -> str:
    totals = packet["totals"]
    lines = [
        f"# Portfolio Liquidity Runway Packet: {packet['portfolio_name']}",
        "",
        f"Scenario: `{packet['scenario']}`",
        "",
        f"> {packet['boundary']}",
        "",
        "## Summary",
        "",
        f"- Gross assets: {money(totals['gross_assets'])}",
        f"- Stress haircut assets: {money(totals['stress_haircut_assets'])}",
        f"- Effective monthly burn: {money(totals['effective_monthly_burn'])}",
        f"- Same-day reserve months: {totals['same_day_reserve_months']:.2f}",
        f"- Same-day + one-week runway months: {totals['same_day_one_week_runway_months']}",
        f"- Thirty-day runway months: {totals['thirty_day_runway_months']}",
        "",
        "## Cash Buckets",
        "",
        "| Tier | Count | Gross | Stress value |",
        "| --- | ---: | ---: | ---: |",
    ]
    for tier in LIQUIDITY_ORDER:
        bucket = packet["cash_buckets"][tier]
        lines.append(f"| {bucket['label']} | {bucket['count']} | {money(bucket['gross'])} | {money(bucket['stress_haircut_value'])} |")
    lines.extend(["", "## Scheduled Events", "", "| Month | Type | Label | Amount |", "| ---: | --- | --- | ---: |"])
    for event in packet["scheduled_events"]:
        lines.append(f"| {event['month']} | {event['type']} | {event['label']} | {money(event['amount'])} |")
    lines.extend(["", "## Monthly Runway", "", "| Month | Inflows | Outflows | Net burn | Liquid balance after |", "| ---: | ---: | ---: | ---: | ---: |"])
    for row in packet["monthly_runway"]:
        lines.append(
            f"| {row['month']} | {money(row['scheduled_inflows'])} | {money(row['scheduled_outflows'])} | "
            f"{money(row['net_burn'])} | {money(row['liquid_balance_after'])} |"
        )
    lines.extend(["", "## Forced-Sale Warnings"])
    warnings = packet["forced_sale_warnings"]
    if warnings:
        lines.extend(f"- {warning}" for warning in warnings)
    else:
        lines.append("- No forced-sale warnings were triggered by these assumptions.")
    lines.extend(["", "## Review Prompts"])
    lines.extend(f"- {prompt}" for prompt in packet["review_prompts"])
    lines.append("")
    return "\n".join(lines)


def render_html(packet: Mapping[str, Any]) -> str:
    md = render_markdown(packet)
    body_lines = []
    in_list = False
    in_table = False
    for line in md.splitlines():
        if line.startswith("# "):
            if in_list:
                body_lines.append("</ul>")
                in_list = False
            if in_table:
                body_lines.append("</table>")
                in_table = False
            body_lines.append(f"<h1>{html.escape(line[2:])}</h1>")
        elif line.startswith("## "):
            if in_list:
                body_lines.append("</ul>")
                in_list = False
            if in_table:
                body_lines.append("</table>")
                in_table = False
            body_lines.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("- "):
            if not in_list:
                body_lines.append("<ul>")
                in_list = True
            body_lines.append(f"<li>{html.escape(line[2:])}</li>")
        elif line.startswith("| ") and not line.startswith("| ---"):
            if not in_table:
                body_lines.append("<table>")
                in_table = True
            cells = [html.escape(cell.strip()) for cell in line.strip("|").split("|")]
            tag = "th" if all(not any(ch.isdigit() for ch in cell) for cell in cells) else "td"
            body_lines.append("<tr>" + "".join(f"<{tag}>{cell}</{tag}>" for cell in cells) + "</tr>")
        elif line.startswith("| ---"):
            continue
        elif line.startswith("> "):
            body_lines.append(f"<blockquote>{html.escape(line[2:])}</blockquote>")
        elif line.strip():
            body_lines.append(f"<p>{html.escape(line)}</p>")
    if in_list:
        body_lines.append("</ul>")
    if in_table:
        body_lines.append("</table>")
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Portfolio Liquidity Runway Packet</title>
<style>
body { font-family: Arial, sans-serif; margin: 2rem; color: #1d2329; background: #fbfbf8; }
main { max-width: 980px; margin: 0 auto; }
table { border-collapse: collapse; width: 100%; margin: 1rem 0; }
th, td { border: 1px solid #c7cbd1; padding: 0.45rem; text-align: left; }
th { background: #e8ecef; }
blockquote { border-left: 4px solid #6b7280; margin-left: 0; padding-left: 1rem; color: #3f4650; }
</style>
</head>
<body><main>
""" + "\n".join(body_lines) + "\n</main></body>\n</html>\n"


def _default_gallery_scenarios(assumptions: Mapping[str, Any]) -> List[str]:
    scenarios = assumptions.get("scenarios", {})
    if not isinstance(scenarios, dict):
        raise ValueError("assumptions.scenarios must be an object")
    preferred = ["base", "stress", "income_shock", "reserve_rebuild"]
    selected = [name for name in preferred if name in scenarios]
    if len(selected) < 3:
        for name in sorted(str(key) for key in scenarios):
            if name not in selected:
                selected.append(name)
            if len(selected) >= 3:
                break
    if len(selected) < 3:
        raise ValueError("scenario gallery requires at least three scenarios in assumptions.scenarios")
    return selected


def build_scenario_gallery_data(
    portfolio: Mapping[str, Any],
    ledger: Mapping[str, Any],
    assumptions: Mapping[str, Any],
    scenario_names: Optional[Iterable[str]] = None,
) -> Dict[str, Any]:
    scenario_list = list(scenario_names) if scenario_names else _default_gallery_scenarios(assumptions)
    if len(scenario_list) < 3:
        raise ValueError("scenario gallery requires at least three scenario names")
    packets = [analyze(portfolio, ledger, assumptions, name) for name in scenario_list]
    rows = []
    for packet in packets:
        totals = packet["totals"]
        rows.append(
            {
                "scenario": packet["scenario"],
                "gross_assets": totals["gross_assets"],
                "stress_haircut_assets": totals["stress_haircut_assets"],
                "effective_monthly_burn": totals["effective_monthly_burn"],
                "same_day_reserve_months": totals["same_day_reserve_months"],
                "same_day_one_week_runway_months": totals["same_day_one_week_runway_months"],
                "thirty_day_runway_months": totals["thirty_day_runway_months"],
                "warning_count": len(packet["forced_sale_warnings"]),
                "first_negative_month": next(
                    (row["month"] for row in packet["monthly_runway"] if row["liquid_balance_after"] < 0),
                    None,
                ),
            }
        )
    return {
        "boundary": BOUNDARY_TEXT,
        "portfolio_name": str(portfolio.get("name", "Synthetic portfolio")),
        "currency": str(portfolio.get("currency", "USD")),
        "scenario_names": scenario_list,
        "summary": rows,
        "scenarios": packets,
    }


def render_scenario_gallery_markdown(gallery: Mapping[str, Any]) -> str:
    lines = [
        f"# Scenario Gallery: {gallery['portfolio_name']}",
        "",
        f"> {gallery['boundary']}",
        "",
        "## Scenario Summary",
        "",
        "| Scenario | Haircut assets | Effective monthly burn | Same-day reserve months | 30-day runway months | Warnings | First negative month |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in gallery["summary"]:
        first_negative = "" if row["first_negative_month"] is None else str(row["first_negative_month"])
        lines.append(
            f"| {row['scenario']} | {money(row['stress_haircut_assets'])} | {money(row['effective_monthly_burn'])} | "
            f"{row['same_day_reserve_months']:.2f} | {row['thirty_day_runway_months']} | {row['warning_count']} | {first_negative} |"
        )
    for packet in gallery["scenarios"]:
        totals = packet["totals"]
        lines.extend(
            [
                "",
                f"## {packet['scenario']}",
                "",
                f"- Gross assets: {money(totals['gross_assets'])}",
                f"- Stress haircut assets: {money(totals['stress_haircut_assets'])}",
                f"- Effective monthly burn: {money(totals['effective_monthly_burn'])}",
                f"- Same-day reserve months: {totals['same_day_reserve_months']:.2f}",
                f"- Same-day + one-week runway months: {totals['same_day_one_week_runway_months']}",
                f"- Thirty-day runway months: {totals['thirty_day_runway_months']}",
                "",
                "Warnings:",
            ]
        )
        warnings = packet["forced_sale_warnings"]
        if warnings:
            lines.extend(f"- {warning}" for warning in warnings)
        else:
            lines.append("- No forced-sale warnings were triggered by these assumptions.")
    lines.append("")
    return "\n".join(lines)


def render_scenario_gallery_html(gallery: Mapping[str, Any]) -> str:
    summary_rows = []
    for row in gallery["summary"]:
        first_negative = "" if row["first_negative_month"] is None else str(row["first_negative_month"])
        summary_rows.append(
            "<tr>"
            f"<td>{html.escape(str(row['scenario']))}</td>"
            f"<td>{html.escape(money(row['stress_haircut_assets']))}</td>"
            f"<td>{html.escape(money(row['effective_monthly_burn']))}</td>"
            f"<td>{row['same_day_reserve_months']:.2f}</td>"
            f"<td>{html.escape(str(row['thirty_day_runway_months']))}</td>"
            f"<td>{row['warning_count']}</td>"
            f"<td>{html.escape(first_negative)}</td>"
            "</tr>"
        )
    scenario_sections = []
    for packet in gallery["scenarios"]:
        totals = packet["totals"]
        warnings = packet["forced_sale_warnings"] or ["No forced-sale warnings were triggered by these assumptions."]
        scenario_sections.append(
            f"<section><h2>{html.escape(str(packet['scenario']))}</h2>"
            "<dl>"
            f"<dt>Gross assets</dt><dd>{html.escape(money(totals['gross_assets']))}</dd>"
            f"<dt>Stress haircut assets</dt><dd>{html.escape(money(totals['stress_haircut_assets']))}</dd>"
            f"<dt>Effective monthly burn</dt><dd>{html.escape(money(totals['effective_monthly_burn']))}</dd>"
            f"<dt>Same-day reserve months</dt><dd>{totals['same_day_reserve_months']:.2f}</dd>"
            f"<dt>Thirty-day runway months</dt><dd>{html.escape(str(totals['thirty_day_runway_months']))}</dd>"
            "</dl>"
            "<h3>Warnings</h3><ul>"
            + "".join(f"<li>{html.escape(warning)}</li>" for warning in warnings)
            + "</ul></section>"
        )
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Portfolio Liquidity Scenario Gallery</title>
<style>
body { font-family: Arial, sans-serif; margin: 2rem; color: #1d2329; background: #fbfbf8; }
main { max-width: 1080px; margin: 0 auto; }
table { border-collapse: collapse; width: 100%; margin: 1rem 0 2rem; }
th, td { border: 1px solid #c7cbd1; padding: 0.45rem; text-align: left; }
th { background: #e8ecef; }
blockquote { border-left: 4px solid #6b7280; margin-left: 0; padding-left: 1rem; color: #3f4650; }
section { border-top: 1px solid #c7cbd1; padding-top: 1rem; margin-top: 1rem; }
dt { font-weight: 700; }
dd { margin: 0 0 0.5rem 0; }
</style>
</head>
<body><main>
""" + f"<h1>Scenario Gallery: {html.escape(str(gallery['portfolio_name']))}</h1>\n" + f"<blockquote>{html.escape(str(gallery['boundary']))}</blockquote>\n" + """<table>
<tr><th>Scenario</th><th>Haircut assets</th><th>Effective monthly burn</th><th>Same-day reserve months</th><th>30-day runway months</th><th>Warnings</th><th>First negative month</th></tr>
""" + "\n".join(summary_rows) + "\n</table>\n" + "\n".join(scenario_sections) + "\n</main></body>\n</html>\n"


def _bar(value: float, maximum: float, width: int = 24) -> str:
    filled = 0 if maximum <= 0 else int(round((value / maximum) * width))
    filled = max(0, min(width, filled))
    return "#" * filled + "." * (width - filled)


def render_visual_receipt(
    packet: Mapping[str, Any],
    packet_command: str = "portfolio-liquidity-runway-lab build-packet --out dist/packet",
    receipt_command: str = "portfolio-liquidity-runway-lab visual-receipt --out demo/visual_receipt.md",
) -> str:
    totals = packet["totals"]
    buckets = packet["cash_buckets"]
    max_bucket = max((bucket["stress_haircut_value"] for bucket in buckets.values()), default=0)
    lines = [
        f"# Visual Receipt: {packet['portfolio_name']}",
        "",
        f"Scenario: `{packet['scenario']}`",
        "",
        f"Boundary: {packet['boundary']}",
        "",
        "## Packet Linkage",
        "",
        "- Packet JSON: `liquidity_packet.json`",
        "- Packet Markdown: `liquidity_packet.md`",
        "- Packet HTML: `liquidity_packet.html`",
        "",
        "## Regeneration",
        "",
        "```bash",
        packet_command,
        receipt_command,
        "```",
        "",
        "## Snapshot",
        "",
        f"- Gross assets: {money(totals['gross_assets'])}",
        f"- Stress haircut assets: {money(totals['stress_haircut_assets'])}",
        f"- Effective monthly burn: {money(totals['effective_monthly_burn'])}",
        f"- Same-day reserve months: {totals['same_day_reserve_months']:.2f}",
        f"- Same-day + one-week runway months: {totals['same_day_one_week_runway_months']}",
        f"- Thirty-day runway months: {totals['thirty_day_runway_months']}",
        "",
        "## Liquidity View",
        "",
        "| Tier | Stress value | Visual |",
        "| --- | ---: | --- |",
    ]
    for tier in LIQUIDITY_ORDER:
        bucket = buckets[tier]
        lines.append(
            f"| {bucket['label']} | {money(bucket['stress_haircut_value'])} | `{_bar(bucket['stress_haircut_value'], max_bucket)}` |"
        )
    lines.extend(["", "## Review Signals", ""])
    warnings = packet["forced_sale_warnings"]
    if warnings:
        lines.extend(f"- {warning}" for warning in warnings)
    else:
        lines.append("- No forced-sale warnings were triggered by these assumptions.")
    lines.append("")
    return "\n".join(lines)


def build_packet(
    portfolio_path: Path,
    ledger_path: Path,
    assumptions_path: Path,
    out_dir: Path,
    scenario: Optional[str] = None,
) -> PacketPaths:
    packet = analyze(load_json(portfolio_path), load_json(ledger_path), load_json(assumptions_path), scenario)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "liquidity_packet.json"
    markdown_path = out_dir / "liquidity_packet.md"
    html_path = out_dir / "liquidity_packet.html"
    dump_json(packet, json_path)
    markdown_path.write_text(render_markdown(packet), encoding="utf-8")
    html_path.write_text(render_html(packet), encoding="utf-8")
    return PacketPaths(out_dir, json_path, markdown_path, html_path)


def build_scenario_gallery(
    portfolio_path: Path,
    ledger_path: Path,
    assumptions_path: Path,
    out_dir: Path,
    scenario_names: Optional[Iterable[str]] = None,
) -> ScenarioGalleryPaths:
    gallery = build_scenario_gallery_data(
        load_json(portfolio_path),
        load_json(ledger_path),
        load_json(assumptions_path),
        scenario_names,
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "scenario_gallery.json"
    markdown_path = out_dir / "scenario_gallery.md"
    html_path = out_dir / "scenario_gallery.html"
    dump_json(gallery, json_path)
    markdown_path.write_text(render_scenario_gallery_markdown(gallery), encoding="utf-8")
    html_path.write_text(render_scenario_gallery_html(gallery), encoding="utf-8")
    return ScenarioGalleryPaths(out_dir, json_path, markdown_path, html_path)


def build_visual_receipt(
    portfolio_path: Path,
    ledger_path: Path,
    assumptions_path: Path,
    out_path: Path,
    scenario: Optional[str] = None,
    packet_out: str = "dist/packet",
) -> Path:
    packet = analyze(load_json(portfolio_path), load_json(ledger_path), load_json(assumptions_path), scenario)
    scenario_part = f" --scenario {packet['scenario']}" if packet.get("scenario") else ""
    packet_command = f"portfolio-liquidity-runway-lab build-packet --out {packet_out}{scenario_part}"
    receipt_command = f"portfolio-liquidity-runway-lab visual-receipt --out {_public_path(out_path, out_path.parent)}{scenario_part}"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render_visual_receipt(packet, packet_command, receipt_command), encoding="utf-8")
    return out_path


def _finding(severity: str, code: str, location: str, message: str) -> Dict[str, str]:
    return {"severity": severity, "code": code, "location": location, "message": message}


def assumption_audit(
    portfolio: Mapping[str, Any],
    ledger: Mapping[str, Any],
    assumptions: Mapping[str, Any],
) -> Dict[str, Any]:
    findings: List[Dict[str, str]] = []

    assets = portfolio.get("assets", [])
    seen_tiers = set()
    if not isinstance(assets, list):
        findings.append(_finding("error", "portfolio_assets_not_list", "portfolio.assets", "portfolio.assets must be a list."))
        assets = []
    for index, asset in enumerate(assets):
        location = f"portfolio.assets[{index}]"
        if not isinstance(asset, dict):
            findings.append(_finding("error", "asset_not_object", location, "Asset entry must be an object."))
            continue
        tier = asset.get("liquidity_tier")
        if tier not in LIQUIDITY_ORDER:
            findings.append(
                _finding("error", "invalid_liquidity_tier", f"{location}.liquidity_tier", "Liquidity tier must be one of same_day, one_week, one_month, locked.")
            )
        else:
            seen_tiers.add(str(tier))
        for field in ("value", "annual_yield_rate", "annual_fee_rate"):
            number = _maybe_number(asset.get(field))
            if number is None:
                findings.append(_finding("error", "nonnumeric_value", f"{location}.{field}", f"{field} must be numeric."))
                continue
            if field == "value" and number < 0:
                findings.append(_finding("warning", "negative_asset_value", f"{location}.{field}", "Asset value is negative."))
            if field == "annual_yield_rate" and (number < -0.01 or number > 0.20):
                findings.append(_finding("warning", "suspicious_yield", f"{location}.{field}", "Annual yield rate is outside the -1% to 20% audit band."))
            if field == "annual_fee_rate" and (number < 0 or number > 0.05):
                findings.append(_finding("warning", "suspicious_fee", f"{location}.{field}", "Annual fee rate is outside the 0% to 5% audit band."))
    for tier in LIQUIDITY_ORDER:
        if tier not in seen_tiers:
            findings.append(_finding("warning", "missing_liquidity_tier", f"portfolio.assets.{tier}", f"No asset uses liquidity tier {tier}."))

    monthly_expenses = _maybe_number(ledger.get("monthly_expenses"))
    monthly_income = _maybe_number(ledger.get("monthly_income"))
    if monthly_expenses is None:
        findings.append(_finding("error", "nonnumeric_value", "ledger.monthly_expenses", "monthly_expenses must be numeric."))
    elif monthly_expenses <= 0:
        findings.append(_finding("warning", "reserve_threshold_issue", "ledger.monthly_expenses", "Monthly expenses should be positive for reserve checks."))
    if monthly_income is None:
        findings.append(_finding("error", "nonnumeric_value", "ledger.monthly_income", "monthly_income must be numeric."))

    months_count = _maybe_number(assumptions.get("months"))
    if months_count is None:
        findings.append(_finding("error", "nonnumeric_value", "assumptions.months", "months must be numeric."))
        normalized_months = 0
    else:
        normalized_months = int(months_count)
        if normalized_months < 1:
            findings.append(_finding("error", "invalid_months", "assumptions.months", "months must be at least 1."))
        if months_count != normalized_months:
            findings.append(_finding("warning", "noninteger_months", "assumptions.months", "months should be an integer."))

    target_reserve = _maybe_number(assumptions.get("target_reserve_months"))
    if target_reserve is None:
        findings.append(_finding("error", "nonnumeric_value", "assumptions.target_reserve_months", "target_reserve_months must be numeric."))
    else:
        if target_reserve <= 0:
            findings.append(_finding("warning", "reserve_threshold_issue", "assumptions.target_reserve_months", "Reserve threshold should be positive."))
        if target_reserve < 3 or target_reserve > 24:
            findings.append(_finding("warning", "reserve_threshold_issue", "assumptions.target_reserve_months", "Reserve threshold is outside the 3 to 24 month audit band."))

    scenarios = assumptions.get("scenarios", {})
    if not isinstance(scenarios, dict) or not scenarios:
        findings.append(_finding("error", "missing_scenarios", "assumptions.scenarios", "assumptions.scenarios must contain named scenarios."))
        scenarios = {}
    default_scenario = str(assumptions.get("default_scenario", "base"))
    if default_scenario not in scenarios:
        findings.append(_finding("error", "missing_default_scenario", "assumptions.default_scenario", "default_scenario is not present in assumptions.scenarios."))
    for scenario_name in ("base", "stress", "income_shock"):
        if scenario_name not in scenarios:
            findings.append(_finding("warning", "missing_scenario", f"assumptions.scenarios.{scenario_name}", f"Scenario {scenario_name} is missing."))
    for scenario_name in sorted(str(name) for name in scenarios):
        scenario = scenarios.get(scenario_name)
        location = f"assumptions.scenarios.{scenario_name}"
        if not isinstance(scenario, dict):
            findings.append(_finding("error", "scenario_not_object", location, "Scenario must be an object."))
            continue
        for field in ("expense_multiplier", "income_multiplier"):
            number = _maybe_number(scenario.get(field))
            if number is None:
                findings.append(_finding("error", "nonnumeric_value", f"{location}.{field}", f"{field} must be numeric."))
            elif number <= 0 or number > 3:
                findings.append(_finding("warning", "suspicious_multiplier", f"{location}.{field}", "Scenario multiplier is outside the 0 to 3 audit band."))
        haircuts = scenario.get("liquidity_haircuts", {})
        if not isinstance(haircuts, dict):
            findings.append(_finding("error", "haircuts_not_object", f"{location}.liquidity_haircuts", "liquidity_haircuts must be an object."))
            continue
        for tier in LIQUIDITY_ORDER:
            if tier not in haircuts:
                findings.append(_finding("error", "missing_haircut", f"{location}.liquidity_haircuts.{tier}", f"Missing haircut for {tier}."))
                continue
            haircut = _maybe_number(haircuts.get(tier))
            if haircut is None:
                findings.append(_finding("error", "nonnumeric_value", f"{location}.liquidity_haircuts.{tier}", "Haircut must be numeric."))
            elif haircut < 0 or haircut > 1:
                findings.append(_finding("warning", "suspicious_haircut", f"{location}.liquidity_haircuts.{tier}", "Haircut is outside the 0 to 1 audit band."))

    events = ledger.get("scheduled_events", [])
    if not isinstance(events, list):
        findings.append(_finding("error", "scheduled_events_not_list", "ledger.scheduled_events", "scheduled_events must be a list."))
        events = []
    event_keys = set()
    for index, event in enumerate(events):
        location = f"ledger.scheduled_events[{index}]"
        if not isinstance(event, dict):
            findings.append(_finding("error", "scheduled_event_not_object", location, "Scheduled event must be an object."))
            continue
        month = _maybe_number(event.get("month"))
        amount = _maybe_number(event.get("amount"))
        kind = str(event.get("type", "")).strip().lower()
        label = str(event.get("label", "")).strip()
        if month is None:
            findings.append(_finding("error", "nonnumeric_value", f"{location}.month", "Scheduled event month must be numeric."))
        else:
            month_int = int(month)
            if month != month_int:
                findings.append(_finding("warning", "noninteger_event_month", f"{location}.month", "Scheduled event month should be an integer."))
            if normalized_months > 0 and (month_int < 1 or month_int > normalized_months):
                findings.append(_finding("warning", "event_outside_window", f"{location}.month", "Scheduled event falls outside the assumptions.months window."))
        if amount is None:
            findings.append(_finding("error", "nonnumeric_value", f"{location}.amount", "Scheduled event amount must be numeric."))
        else:
            if amount <= 0:
                findings.append(_finding("warning", "nonpositive_event_amount", f"{location}.amount", "Scheduled event amount should be positive."))
            if monthly_expenses and monthly_expenses > 0 and kind == "outflow" and amount > monthly_expenses * 3:
                findings.append(_finding("warning", "large_scheduled_outflow", f"{location}.amount", "Scheduled outflow exceeds three months of expenses."))
        if kind not in {"inflow", "outflow"}:
            findings.append(_finding("error", "invalid_event_type", f"{location}.type", "Scheduled event type must be inflow or outflow."))
        if not label:
            findings.append(_finding("warning", "missing_event_label", f"{location}.label", "Scheduled event label is missing."))
        key = (month, kind, label)
        if key in event_keys:
            findings.append(_finding("warning", "duplicate_scheduled_event", location, "Scheduled event duplicates an earlier month/type/label combination."))
        event_keys.add(key)

    findings.sort(key=lambda item: (item["severity"], item["code"], item["location"], item["message"]))
    counts = {severity: sum(1 for item in findings if item["severity"] == severity) for severity in ("error", "warning")}
    return {
        "boundary": BOUNDARY_TEXT,
        "status": "pass" if not findings else "review",
        "finding_counts": counts,
        "portfolio_name": str(portfolio.get("name", "Synthetic portfolio")),
        "findings": findings,
    }


def render_assumption_audit_markdown(audit: Mapping[str, Any]) -> str:
    lines = [
        f"# Assumption Audit: {audit['portfolio_name']}",
        "",
        f"> {audit['boundary']}",
        "",
        f"Status: `{audit['status']}`",
        "",
        "## Finding Counts",
        "",
        f"- Errors: {audit['finding_counts']['error']}",
        f"- Warnings: {audit['finding_counts']['warning']}",
        "",
        "## Findings",
        "",
    ]
    if audit["findings"]:
        lines.extend(["| Severity | Code | Location | Message |", "| --- | --- | --- | --- |"])
        for finding in audit["findings"]:
            lines.append(
                f"| {finding['severity']} | {finding['code']} | `{finding['location']}` | {finding['message']} |"
            )
    else:
        lines.append("- No audit findings were triggered.")
    lines.append("")
    return "\n".join(lines)


def build_assumption_audit(portfolio_path: Path, ledger_path: Path, assumptions_path: Path, out_dir: Path) -> AuditPaths:
    audit = assumption_audit(load_json(portfolio_path), load_json(ledger_path), load_json(assumptions_path))
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "assumption_audit.json"
    markdown_path = out_dir / "assumption_audit.md"
    dump_json(audit, json_path)
    markdown_path.write_text(render_assumption_audit_markdown(audit), encoding="utf-8")
    return AuditPaths(out_dir, json_path, markdown_path)


def _default_batch_scenarios(assumptions: Mapping[str, Any], scenario_names: Optional[Iterable[str]]) -> List[str]:
    if scenario_names:
        selected = [str(name) for name in scenario_names]
        if not selected:
            raise ValueError("batch compare requires at least one scenario")
        return selected
    scenarios = assumptions.get("scenarios", {})
    if not isinstance(scenarios, dict) or not scenarios:
        raise ValueError("assumptions.scenarios must contain at least one scenario")
    preferred = ["base", "stress", "income_shock", "reserve_rebuild"]
    selected = [name for name in preferred if name in scenarios]
    return selected or sorted(str(name) for name in scenarios)


def build_batch_compare_data(
    portfolios_dir: Path,
    ledger: Mapping[str, Any],
    assumptions: Mapping[str, Any],
    scenario_names: Optional[Iterable[str]] = None,
) -> Dict[str, Any]:
    files = sorted(path for path in portfolios_dir.glob("*.json") if path.is_file())
    if not files:
        raise ValueError("portfolio directory must contain at least one .json file")
    scenarios = _default_batch_scenarios(assumptions, scenario_names)
    rows = []
    warnings: Dict[str, List[str]] = {}
    for path in files:
        portfolio = load_json(path)
        portfolio_key = path.stem
        for scenario in scenarios:
            packet = analyze(portfolio, ledger, assumptions, scenario)
            totals = packet["totals"]
            row = {
                "portfolio_file": path.name,
                "portfolio_name": packet["portfolio_name"],
                "scenario": scenario,
                "same_day_reserve_months": totals["same_day_reserve_months"],
                "same_day_one_week_runway_months": totals["same_day_one_week_runway_months"],
                "thirty_day_runway_months": totals["thirty_day_runway_months"],
                "effective_monthly_burn": totals["effective_monthly_burn"],
                "warning_count": len(packet["forced_sale_warnings"]),
                "first_negative_month": next(
                    (item["month"] for item in packet["monthly_runway"] if item["liquid_balance_after"] < 0),
                    None,
                ),
            }
            rows.append(row)
            warnings[f"{portfolio_key}:{scenario}"] = list(packet["forced_sale_warnings"])
    return {
        "boundary": BOUNDARY_TEXT,
        "portfolio_files": [path.name for path in files],
        "scenario_names": scenarios,
        "summary": rows,
        "warnings": warnings,
    }


def render_batch_compare_markdown(compare: Mapping[str, Any]) -> str:
    lines = [
        "# Batch Portfolio Compare",
        "",
        f"> {compare['boundary']}",
        "",
        "## Summary",
        "",
        "| Portfolio | Scenario | Same-day reserve months | Same-day + one-week runway | 30-day runway | Effective monthly burn | Warnings | First negative month |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in compare["summary"]:
        first_negative = "" if row["first_negative_month"] is None else str(row["first_negative_month"])
        lines.append(
            f"| {row['portfolio_file']} | {row['scenario']} | {row['same_day_reserve_months']:.2f} | "
            f"{row['same_day_one_week_runway_months']} | {row['thirty_day_runway_months']} | "
            f"{money(row['effective_monthly_burn'])} | {row['warning_count']} | {first_negative} |"
        )
    lines.extend(["", "## Warnings", ""])
    for key in sorted(compare["warnings"]):
        lines.append(f"### {key}")
        warnings = compare["warnings"][key]
        if warnings:
            lines.extend(f"- {warning}" for warning in warnings)
        else:
            lines.append("- No forced-sale warnings were triggered by these assumptions.")
        lines.append("")
    return "\n".join(lines)


def render_batch_compare_html(compare: Mapping[str, Any]) -> str:
    rows = []
    for row in compare["summary"]:
        first_negative = "" if row["first_negative_month"] is None else str(row["first_negative_month"])
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(row['portfolio_file']))}</td>"
            f"<td>{html.escape(str(row['scenario']))}</td>"
            f"<td>{row['same_day_reserve_months']:.2f}</td>"
            f"<td>{html.escape(str(row['same_day_one_week_runway_months']))}</td>"
            f"<td>{html.escape(str(row['thirty_day_runway_months']))}</td>"
            f"<td>{html.escape(money(row['effective_monthly_burn']))}</td>"
            f"<td>{row['warning_count']}</td>"
            f"<td>{html.escape(first_negative)}</td>"
            "</tr>"
        )
    warning_sections = []
    for key in sorted(compare["warnings"]):
        warnings = compare["warnings"][key] or ["No forced-sale warnings were triggered by these assumptions."]
        warning_sections.append(
            f"<section><h2>{html.escape(key)}</h2><ul>"
            + "".join(f"<li>{html.escape(warning)}</li>" for warning in warnings)
            + "</ul></section>"
        )
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Batch Portfolio Compare</title>
<style>
body { font-family: Arial, sans-serif; margin: 2rem; color: #1d2329; background: #fbfbf8; }
main { max-width: 1120px; margin: 0 auto; }
table { border-collapse: collapse; width: 100%; margin: 1rem 0 2rem; }
th, td { border: 1px solid #c7cbd1; padding: 0.45rem; text-align: left; }
th { background: #e8ecef; }
blockquote { border-left: 4px solid #6b7280; margin-left: 0; padding-left: 1rem; color: #3f4650; }
section { border-top: 1px solid #c7cbd1; padding-top: 1rem; margin-top: 1rem; }
</style>
</head>
<body><main>
<h1>Batch Portfolio Compare</h1>
""" + f"<blockquote>{html.escape(str(compare['boundary']))}</blockquote>\n" + """<table>
<tr><th>Portfolio</th><th>Scenario</th><th>Same-day reserve months</th><th>Same-day + one-week runway</th><th>30-day runway</th><th>Effective monthly burn</th><th>Warnings</th><th>First negative month</th></tr>
""" + "\n".join(rows) + "\n</table>\n" + "\n".join(warning_sections) + "\n</main></body>\n</html>\n"


def build_batch_compare(
    portfolios_dir: Path,
    ledger_path: Path,
    assumptions_path: Path,
    out_dir: Path,
    scenario_names: Optional[Iterable[str]] = None,
) -> BatchComparePaths:
    compare = build_batch_compare_data(portfolios_dir, load_json(ledger_path), load_json(assumptions_path), scenario_names)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "batch_compare.json"
    markdown_path = out_dir / "batch_compare.md"
    html_path = out_dir / "batch_compare.html"
    dump_json(compare, json_path)
    markdown_path.write_text(render_batch_compare_markdown(compare), encoding="utf-8")
    html_path.write_text(render_batch_compare_html(compare), encoding="utf-8")
    return BatchComparePaths(out_dir, json_path, markdown_path, html_path)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _deterministic_text_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _contains_script_tag(path: Path) -> bool:
    try:
        return "<script" in path.read_text(encoding="utf-8").lower()
    except UnicodeDecodeError:
        return False


def _html_safety_findings(path: Path) -> List[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [f"html_non_utf8: {path.as_posix()}"]
    return [code for code, pattern in HTML_SAFETY_PATTERNS if pattern.search(text)]


def _html_has_unsafe_content(path: Path) -> bool:
    return bool(_html_safety_findings(path))


def _public_path(path: Path, root: Optional[Path] = None) -> str:
    candidate = Path(path)
    if not candidate.is_absolute():
        return candidate.as_posix()
    bases = [root, Path.cwd()]
    for base in bases:
        if base is None:
            continue
        try:
            return candidate.resolve().relative_to(base.resolve()).as_posix()
        except ValueError:
            continue
    return candidate.name


def _html_shell(title: str, body: str) -> str:
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>""" + html.escape(title) + """</title>
<style>
body { font-family: Arial, sans-serif; margin: 2rem; color: #1d2329; background: #fbfbf8; }
main { max-width: 1120px; margin: 0 auto; }
table { border-collapse: collapse; width: 100%; margin: 1rem 0 2rem; }
th, td { border: 1px solid #c7cbd1; padding: 0.45rem; text-align: left; vertical-align: top; }
th { background: #e8ecef; }
blockquote { border-left: 4px solid #6b7280; margin-left: 0; padding-left: 1rem; color: #3f4650; }
section { border-top: 1px solid #c7cbd1; padding-top: 1rem; margin-top: 1rem; }
code { background: #eef0f2; padding: 0.1rem 0.25rem; }
</style>
</head>
<body><main>
""" + body + "\n</main></body>\n</html>\n"


def build_casebook_data(
    portfolio_path: Path,
    ledger_path: Path,
    assumptions_path: Path,
    portfolios_dir: Path,
    scenario: Optional[str] = None,
    scenario_names: Optional[Iterable[str]] = None,
) -> Dict[str, Any]:
    portfolio = load_json(portfolio_path)
    ledger = load_json(ledger_path)
    assumptions = load_json(assumptions_path)
    packet = analyze(portfolio, ledger, assumptions, scenario)
    gallery = build_scenario_gallery_data(portfolio, ledger, assumptions, scenario_names)
    audit = assumption_audit(portfolio, ledger, assumptions)
    batch = build_batch_compare_data(portfolios_dir, ledger, assumptions, scenario_names)
    return {
        "boundary": BOUNDARY_TEXT,
        "title": f"Release Owner Casebook: {packet['portfolio_name']}",
        "inputs": {
            "portfolio": _public_path(portfolio_path),
            "ledger": _public_path(ledger_path),
            "assumptions": _public_path(assumptions_path),
            "portfolios_dir": _public_path(portfolios_dir),
        },
        "regeneration_commands": [
            "portfolio-liquidity-runway-lab casebook --out demo/casebook",
            "portfolio-liquidity-runway-lab build-packet --out demo/casebook/packet",
            "portfolio-liquidity-runway-lab scenario-gallery --out demo/casebook/scenario-gallery",
            "portfolio-liquidity-runway-lab assumption-audit --out demo/casebook/assumption-audit",
            "portfolio-liquidity-runway-lab batch-compare --portfolios-dir portfolio_liquidity_runway_lab/examples --out demo/casebook/batch-compare",
        ],
        "packet_summary": {
            "scenario": packet["scenario"],
            "portfolio_name": packet["portfolio_name"],
            "totals": packet["totals"],
            "cash_buckets": packet["cash_buckets"],
            "forced_sale_warnings": packet["forced_sale_warnings"],
            "review_prompts": packet["review_prompts"],
        },
        "scenario_gallery_summary": gallery["summary"],
        "scenario_names": gallery["scenario_names"],
        "assumption_audit_summary": {
            "status": audit["status"],
            "finding_counts": audit["finding_counts"],
            "findings": audit["findings"],
        },
        "batch_compare_summary": batch["summary"],
        "batch_portfolio_files": batch["portfolio_files"],
        "batch_warnings": batch["warnings"],
    }


def render_casebook_markdown(casebook: Mapping[str, Any]) -> str:
    totals = casebook["packet_summary"]["totals"]
    lines = [
        f"# {casebook['title']}",
        "",
        f"> {casebook['boundary']}",
        "",
        "## Regeneration",
        "",
        "```bash",
        *casebook["regeneration_commands"],
        "```",
        "",
        "## Packet Summary",
        "",
        f"- Scenario: `{casebook['packet_summary']['scenario']}`",
        f"- Gross assets: {money(totals['gross_assets'])}",
        f"- Stress haircut assets: {money(totals['stress_haircut_assets'])}",
        f"- Effective monthly burn: {money(totals['effective_monthly_burn'])}",
        f"- Same-day reserve months: {totals['same_day_reserve_months']:.2f}",
        "",
        "### Cash Buckets",
        "",
        "| Tier | Count | Gross | Stress value |",
        "| --- | ---: | ---: | ---: |",
    ]
    for tier in LIQUIDITY_ORDER:
        bucket = casebook["packet_summary"]["cash_buckets"][tier]
        lines.append(f"| {bucket['label']} | {bucket['count']} | {money(bucket['gross'])} | {money(bucket['stress_haircut_value'])} |")
    lines.extend(["", "### Forced-Sale Warnings", ""])
    warnings = casebook["packet_summary"]["forced_sale_warnings"]
    lines.extend(f"- {warning}" for warning in warnings) if warnings else lines.append("- No forced-sale warnings were triggered by these assumptions.")
    lines.extend(
        [
            "",
            "## Scenario Gallery Summary",
            "",
            "| Scenario | Haircut assets | Effective monthly burn | 30-day runway | Warnings |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in casebook["scenario_gallery_summary"]:
        lines.append(
            f"| {row['scenario']} | {money(row['stress_haircut_assets'])} | {money(row['effective_monthly_burn'])} | "
            f"{row['thirty_day_runway_months']} | {row['warning_count']} |"
        )
    audit = casebook["assumption_audit_summary"]
    lines.extend(
        [
            "",
            "## Assumption Audit Summary",
            "",
            f"- Status: `{audit['status']}`",
            f"- Errors: {audit['finding_counts']['error']}",
            f"- Warnings: {audit['finding_counts']['warning']}",
            "",
            "| Severity | Code | Location | Message |",
            "| --- | --- | --- | --- |",
        ]
    )
    if audit["findings"]:
        for finding in audit["findings"]:
            lines.append(f"| {finding['severity']} | {finding['code']} | `{finding['location']}` | {finding['message']} |")
    else:
        lines.append("| pass | none |  | No audit findings were triggered. |")
    lines.extend(
        [
            "",
            "## Batch Compare Summary",
            "",
            "| Portfolio | Scenario | Same-day reserve months | 30-day runway | Effective monthly burn | Warnings |",
            "| --- | --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in casebook["batch_compare_summary"]:
        lines.append(
            f"| {row['portfolio_file']} | {row['scenario']} | {row['same_day_reserve_months']:.2f} | "
            f"{row['thirty_day_runway_months']} | {money(row['effective_monthly_burn'])} | {row['warning_count']} |"
        )
    lines.append("")
    return "\n".join(lines)


def render_casebook_html(casebook: Mapping[str, Any]) -> str:
    md = render_casebook_markdown(casebook)
    body = []
    in_table = False
    in_list = False
    in_code = False
    for line in md.splitlines():
        if line == "```bash":
            body.append("<pre><code>")
            in_code = True
            continue
        if line == "```" and in_code:
            body.append("</code></pre>")
            in_code = False
            continue
        if in_code:
            body.append(html.escape(line))
            continue
        if line.startswith("# "):
            if in_table:
                body.append("</table>")
                in_table = False
            if in_list:
                body.append("</ul>")
                in_list = False
            body.append(f"<h1>{html.escape(line[2:])}</h1>")
        elif line.startswith("## "):
            if in_table:
                body.append("</table>")
                in_table = False
            if in_list:
                body.append("</ul>")
                in_list = False
            body.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("### "):
            if in_table:
                body.append("</table>")
                in_table = False
            if in_list:
                body.append("</ul>")
                in_list = False
            body.append(f"<h3>{html.escape(line[4:])}</h3>")
        elif line.startswith("> "):
            body.append(f"<blockquote>{html.escape(line[2:])}</blockquote>")
        elif line.startswith("- "):
            if not in_list:
                body.append("<ul>")
                in_list = True
            body.append(f"<li>{html.escape(line[2:])}</li>")
        elif line.startswith("| ") and not line.startswith("| ---"):
            if not in_table:
                body.append("<table>")
                in_table = True
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            tag = "th" if all(not any(ch.isdigit() for ch in cell) for cell in cells) else "td"
            body.append("<tr>" + "".join(f"<{tag}>{html.escape(cell)}</{tag}>" for cell in cells) + "</tr>")
        elif line.startswith("| ---"):
            continue
        elif line.strip():
            body.append(f"<p>{html.escape(line)}</p>")
    if in_table:
        body.append("</table>")
    if in_list:
        body.append("</ul>")
    return _html_shell(str(casebook["title"]), "\n".join(body))


def build_casebook(
    portfolio_path: Path,
    ledger_path: Path,
    assumptions_path: Path,
    portfolios_dir: Path,
    out_dir: Path,
    scenario: Optional[str] = None,
    scenario_names: Optional[Iterable[str]] = None,
) -> CasebookPaths:
    casebook = build_casebook_data(portfolio_path, ledger_path, assumptions_path, portfolios_dir, scenario, scenario_names)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "casebook.json"
    markdown_path = out_dir / "casebook.md"
    html_path = out_dir / "casebook.html"
    dump_json(casebook, json_path)
    markdown_path.write_text(render_casebook_markdown(casebook), encoding="utf-8")
    html_path.write_text(render_casebook_html(casebook), encoding="utf-8")
    return CasebookPaths(out_dir, json_path, markdown_path, html_path)


def schema_guide() -> Dict[str, Any]:
    input_files = [
        {
            "file": "portfolio.json",
            "description": "Portfolio asset inventory used by packet, gallery, audit, batch, casebook, and receipt commands.",
            "required_fields": ["name", "currency", "assets"],
            "fields": [
                {"path": "name", "type": "string", "required": False, "description": "Human-readable portfolio name."},
                {"path": "currency", "type": "string", "required": False, "description": "Display currency label; calculations treat values as already normalized."},
                {"path": "assets", "type": "array<object>", "required": True, "description": "Asset rows used for liquidity buckets and yield or fee assumptions."},
                {"path": "assets[].name", "type": "string", "required": False, "description": "Asset display name."},
                {"path": "assets[].value", "type": "number", "required": True, "description": "Gross asset value."},
                {"path": "assets[].liquidity_tier", "type": "enum", "required": True, "allowed_values": list(LIQUIDITY_ORDER), "description": "Liquidity bucket for stress haircut and runway grouping."},
                {"path": "assets[].annual_yield_rate", "type": "number", "required": True, "description": "Annual yield assumption as a decimal, for example 0.04."},
                {"path": "assets[].annual_fee_rate", "type": "number", "required": True, "description": "Annual fee assumption as a decimal, for example 0.01."},
            ],
        },
        {
            "file": "ledger.json",
            "description": "Recurring income, recurring expenses, and scheduled cash events.",
            "required_fields": ["monthly_income", "monthly_expenses", "scheduled_events"],
            "fields": [
                {"path": "monthly_income", "type": "number", "required": True, "description": "Expected monthly income before scenario multiplier."},
                {"path": "monthly_expenses", "type": "number", "required": True, "description": "Expected monthly expenses before scenario multiplier."},
                {"path": "scheduled_events", "type": "array<object>", "required": False, "description": "One-time inflow or outflow events by month."},
                {"path": "scheduled_events[].month", "type": "integer", "required": True, "description": "1-based month in the runway window."},
                {"path": "scheduled_events[].type", "type": "enum", "required": True, "allowed_values": ["inflow", "outflow"], "description": "Cash event direction."},
                {"path": "scheduled_events[].label", "type": "string", "required": False, "description": "Event label for review."},
                {"path": "scheduled_events[].amount", "type": "number", "required": True, "description": "Positive event amount."},
            ],
        },
        {
            "file": "assumptions.json",
            "description": "Runway window, reserve threshold, default scenario, and named scenario stress assumptions.",
            "required_fields": ["months", "target_reserve_months", "default_scenario", "scenarios"],
            "fields": [
                {"path": "months", "type": "integer", "required": True, "description": "Number of monthly runway rows to produce."},
                {"path": "target_reserve_months", "type": "number", "required": True, "description": "Same-day reserve threshold used for warnings."},
                {"path": "default_scenario", "type": "string", "required": False, "description": "Scenario used when no scenario argument is supplied."},
                {"path": "scenarios", "type": "object", "required": True, "description": "Named scenario map."},
                {"path": "scenarios.<name>.expense_multiplier", "type": "number", "required": True, "description": "Multiplier applied to monthly expenses."},
                {"path": "scenarios.<name>.income_multiplier", "type": "number", "required": True, "description": "Multiplier applied to monthly income."},
                {"path": "scenarios.<name>.liquidity_haircuts", "type": "object", "required": True, "description": "Haircut map keyed by liquidity tier."},
                {"path": "scenarios.<name>.liquidity_haircuts.same_day", "type": "number", "required": True, "description": "Haircut from 0 to 1."},
                {"path": "scenarios.<name>.liquidity_haircuts.one_week", "type": "number", "required": True, "description": "Haircut from 0 to 1."},
                {"path": "scenarios.<name>.liquidity_haircuts.one_month", "type": "number", "required": True, "description": "Haircut from 0 to 1."},
                {"path": "scenarios.<name>.liquidity_haircuts.locked", "type": "number", "required": True, "description": "Haircut from 0 to 1."},
            ],
        },
        {
            "file": "history.json",
            "description": "Historical reserve and burn snapshots for compare-history.",
            "required_fields": ["snapshots"],
            "fields": [
                {"path": "snapshots", "type": "array<object>", "required": True, "description": "At least two snapshots."},
                {"path": "snapshots[].label", "type": "string", "required": True, "description": "Snapshot label."},
                {"path": "snapshots[].same_day_reserve_months", "type": "number", "required": True, "description": "Reserve-month value for delta comparison."},
                {"path": "snapshots[].effective_monthly_burn", "type": "number", "required": True, "description": "Monthly burn value for delta comparison."},
            ],
        },
        {
            "file": "portfolio.csv",
            "description": "CSV asset rows accepted by csv-import and input-lint.",
            "required_fields": ["name", "value", "liquidity_tier", "annual_yield_rate", "annual_fee_rate"],
            "fields": [
                {"path": "name", "type": "string", "required": True, "description": "Asset display name."},
                {"path": "value", "type": "number", "required": True, "description": "Gross asset value."},
                {"path": "liquidity_tier", "type": "enum", "required": True, "allowed_values": list(LIQUIDITY_ORDER), "description": "Liquidity bucket copied into portfolio.assets[].liquidity_tier."},
                {"path": "annual_yield_rate", "type": "number", "required": True, "description": "Annual yield assumption as a decimal."},
                {"path": "annual_fee_rate", "type": "number", "required": True, "description": "Annual fee assumption as a decimal."},
            ],
        },
        {
            "file": "ledger.csv",
            "description": "CSV settings and scheduled event rows accepted by csv-import and input-lint.",
            "required_fields": ["record_type", "monthly_income", "monthly_expenses", "month", "type", "label", "amount"],
            "fields": [
                {"path": "record_type", "type": "enum", "required": True, "allowed_values": ["settings", "event"], "description": "settings row supplies recurring values; event rows supply scheduled events."},
                {"path": "monthly_income", "type": "number", "required": "settings", "description": "Monthly income for the single settings row."},
                {"path": "monthly_expenses", "type": "number", "required": "settings", "description": "Monthly expenses for the single settings row."},
                {"path": "month", "type": "integer", "required": "event", "description": "Scheduled event month."},
                {"path": "type", "type": "enum", "required": "event", "allowed_values": ["inflow", "outflow"], "description": "Scheduled event direction."},
                {"path": "label", "type": "string", "required": False, "description": "Scheduled event label."},
                {"path": "amount", "type": "number", "required": "event", "description": "Scheduled event amount."},
            ],
        },
    ]
    output_artifacts = [
        {"artifact": "liquidity_packet.json", "command": "build-packet", "top_level_fields": ["boundary", "scenario", "portfolio_name", "currency", "totals", "cash_buckets", "assets", "scheduled_events", "monthly_runway", "forced_sale_warnings", "review_prompts"]},
        {"artifact": "liquidity_packet.md", "command": "build-packet", "top_level_fields": ["summary", "cash buckets", "scheduled events", "monthly runway", "warnings", "review prompts"]},
        {"artifact": "liquidity_packet.html", "command": "build-packet/static-dashboard", "top_level_fields": ["no JavaScript static HTML rendering of packet Markdown"]},
        {"artifact": "scenario_gallery.json", "command": "scenario-gallery", "top_level_fields": ["boundary", "portfolio_name", "currency", "scenario_names", "summary", "scenarios"]},
        {"artifact": "assumption_audit.json", "command": "assumption-audit", "top_level_fields": ["boundary", "status", "finding_counts", "portfolio_name", "findings"]},
        {"artifact": "batch_compare.json", "command": "batch-compare", "top_level_fields": ["boundary", "portfolio_files", "scenario_names", "summary", "warnings"]},
        {"artifact": "casebook.json", "command": "casebook", "top_level_fields": ["boundary", "title", "inputs", "regeneration_commands", "packet_summary", "scenario_gallery_summary", "assumption_audit_summary", "batch_compare_summary"]},
        {"artifact": "visual_receipt.md", "command": "visual-receipt", "top_level_fields": ["packet linkage", "regeneration", "snapshot", "liquidity view", "review signals"]},
        {"artifact": "artifact_catalog.json", "command": "artifact-catalog", "top_level_fields": ["boundary", "root", "artifact_count", "artifacts"]},
        {"artifact": "release_check.json", "command": "release-check", "top_level_fields": ["boundary", "status", "checks", "missing_files", "html_files", "html_with_script_tags", "public_scan_findings"]},
        {"artifact": "schema_guide.json", "command": "schema-export", "top_level_fields": ["boundary", "version", "input_files", "output_artifacts"]},
        {"artifact": "fixture_doctor.json", "command": "fixture-doctor", "top_level_fields": ["boundary", "status", "work_dir", "examples", "command_plan", "results"]},
        {"artifact": "static-docs/index.html", "command": "docs-export", "top_level_fields": ["no JavaScript static documentation index"]},
        {"artifact": "import_report.json", "command": "csv-import", "top_level_fields": ["boundary", "status", "inputs", "outputs", "row_counts", "schema_refs", "findings"]},
        {"artifact": "export_manifest.json", "command": "csv-export", "top_level_fields": ["boundary", "status", "packet", "portfolio_name", "scenario", "files"]},
        {"artifact": "input-lint stdout JSON", "command": "input-lint", "top_level_fields": ["boundary", "status", "results", "finding_counts"]},
        {"artifact": "SHA256SUMS.txt", "command": "bundle-checksums", "top_level_fields": ["sha256 path lines"]},
        {"artifact": "bundle_manifest.json", "command": "bundle-checksums", "top_level_fields": ["boundary", "version", "root", "file_count", "files"]},
        {"artifact": "evidence-bundle/index.html", "command": "evidence-bundle", "top_level_fields": ["no JavaScript static evidence index"]},
        {"artifact": "evidence_manifest.json", "command": "evidence-bundle", "top_level_fields": ["boundary", "version", "root", "artifact_count", "artifacts"]},
        {"artifact": "template_manifest.json", "command": "template-pack", "top_level_fields": ["boundary", "version", "file_count", "files"]},
    ]
    command_matrix = command_matrix_data()
    return {
        "boundary": BOUNDARY_TEXT,
        "version": PROJECT_VERSION,
        "input_files": input_files,
        "output_artifacts": output_artifacts,
        "command_matrix": command_matrix,
    }


def render_schema_guide_markdown(guide: Mapping[str, Any]) -> str:
    lines = [
        "# Schema Guide",
        "",
        f"> {guide['boundary']}",
        "",
        f"Version: `{guide['version']}`",
        "",
        "## Input Files",
        "",
    ]
    for file_spec in guide["input_files"]:
        lines.extend(
            [
                f"### {file_spec['file']}",
                "",
                file_spec["description"],
                "",
                "Required fields: " + ", ".join(f"`{field}`" for field in file_spec["required_fields"]),
                "",
                "| Path | Type | Required | Description |",
                "| --- | --- | --- | --- |",
            ]
        )
        for field in file_spec["fields"]:
            allowed = ""
            if "allowed_values" in field:
                allowed = " Allowed values: " + ", ".join(f"`{value}`" for value in field["allowed_values"]) + "."
            lines.append(f"| `{field['path']}` | `{field['type']}` | {str(field['required']).lower()} | {field['description']}{allowed} |")
        lines.append("")
    lines.extend(["## Output Artifacts", "", "| Artifact | Command | Top-level fields |", "| --- | --- | --- |"])
    for artifact in guide["output_artifacts"]:
        fields = ", ".join(f"`{field}`" for field in artifact["top_level_fields"])
        lines.append(f"| `{artifact['artifact']}` | `{artifact['command']}` | {fields} |")
    lines.extend(["", "## Command Matrix", "", "| Command | Inputs | Outputs | Static no-JS HTML |", "| --- | --- | --- | --- |"])
    for command in guide["command_matrix"]:
        lines.append(
            f"| `{command['command']}` | {', '.join(command['inputs']) or 'none'} | "
            f"{', '.join(command['outputs']) or 'stdout'} | {str(command['no_script_html']).lower()} |"
        )
    lines.append("")
    return "\n".join(lines)


def build_schema_export(out_dir: Path) -> SchemaExportPaths:
    guide = schema_guide()
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "schema_guide.json"
    markdown_path = out_dir / "schema_guide.md"
    dump_json(guide, json_path)
    markdown_path.write_text(render_schema_guide_markdown(guide), encoding="utf-8")
    return SchemaExportPaths(out_dir, json_path, markdown_path)


def command_matrix_data() -> List[Dict[str, Any]]:
    boundary = "Local deterministic analysis; no live data, broker connection, order placement, or advice."
    rows = [
        ("build-packet", "Build the core liquidity runway packet.", ["portfolio.json", "ledger.json", "assumptions.json"], ["liquidity_packet.json", "liquidity_packet.md", "liquidity_packet.html"], "portfolio-liquidity-runway-lab build-packet --scenario stress --out dist/packet", True),
        ("compare-history", "Compare reserve and burn snapshots over time.", ["history.json"], ["stdout JSON", "optional JSON file"], "portfolio-liquidity-runway-lab compare-history --out dist/history_compare.json", False),
        ("review-ledger", "Flag ledger review prompts and unusual scheduled events.", ["ledger.json"], ["stdout JSON", "optional JSON file"], "portfolio-liquidity-runway-lab review-ledger --out dist/ledger_review.json", False),
        ("static-dashboard", "Build the packet HTML dashboard without JavaScript.", ["portfolio.json", "ledger.json", "assumptions.json"], ["liquidity_packet.json", "liquidity_packet.md", "liquidity_packet.html"], "portfolio-liquidity-runway-lab static-dashboard --scenario stress --out dist/dashboard", True),
        ("scenario-gallery", "Compare named scenarios side by side.", ["portfolio.json", "ledger.json", "assumptions.json"], ["scenario_gallery.json", "scenario_gallery.md", "scenario_gallery.html"], "portfolio-liquidity-runway-lab scenario-gallery --out dist/scenario-gallery", True),
        ("assumption-audit", "Audit portfolio, ledger, and assumptions for review issues.", ["portfolio.json", "ledger.json", "assumptions.json"], ["assumption_audit.json", "assumption_audit.md"], "portfolio-liquidity-runway-lab assumption-audit --portfolio portfolio_liquidity_runway_lab/examples/portfolio_concentrated.json --out dist/assumption-audit", False),
        ("batch-compare", "Compare multiple portfolio JSON files under shared scenarios.", ["portfolio directory", "ledger.json", "assumptions.json"], ["batch_compare.json", "batch_compare.md", "batch_compare.html"], "portfolio-liquidity-runway-lab batch-compare --portfolios-dir portfolios --scenarios base,stress --out dist/batch-compare", True),
        ("casebook", "Assemble packet, scenario, audit, and batch evidence for release owners.", ["portfolio.json", "portfolio directory", "ledger.json", "assumptions.json"], ["casebook.json", "casebook.md", "casebook.html"], "portfolio-liquidity-runway-lab casebook --scenario stress --scenarios base,stress,income_shock --out dist/casebook", True),
        ("artifact-catalog", "Inventory demo and doc artifacts with SHA256 hashes.", ["repo or output root"], ["artifact_catalog.json", "artifact_catalog.md"], "portfolio-liquidity-runway-lab artifact-catalog --out docs", False),
        ("release-check", "Validate expected files, public scan, and no-script HTML.", ["repo root"], ["release_check.json", "release_check.md"], "portfolio-liquidity-runway-lab release-check --out docs", False),
        ("visual-receipt", "Write a compact Markdown review receipt.", ["portfolio.json", "ledger.json", "assumptions.json"], ["visual_receipt.md"], "portfolio-liquidity-runway-lab visual-receipt --scenario stress --out demo/visual_receipt.md", False),
        ("schema-export", "Export input and artifact schema documentation.", ["built-in schema metadata"], ["schema_guide.json", "schema_guide.md"], "portfolio-liquidity-runway-lab schema-export --out docs", False),
        ("csv-import", "Convert local portfolio and ledger CSV rows into validated JSON schemas.", ["portfolio.csv", "ledger.csv"], ["portfolio.json", "ledger.json", "import_report.json", "import_report.md"], "portfolio-liquidity-runway-lab csv-import --out dist/csv-import", False),
        ("csv-export", "Export packet assets, runway rows, warnings, and bucket summaries as deterministic CSV.", ["liquidity_packet.json"], ["assets.csv", "runway.csv", "warnings.csv", "bucket_summaries.csv", "export_manifest.json", "export_manifest.md"], "portfolio-liquidity-runway-lab csv-export --packet dist/packet/liquidity_packet.json --out dist/csv-export", False),
        ("input-lint", "Strict lint for JSON and CSV inputs with remediation and schema references.", ["portfolio/ledger/assumptions JSON", "portfolio/ledger CSV"], ["stdout JSON", "optional JSON file"], "portfolio-liquidity-runway-lab input-lint --portfolio portfolio.json --ledger ledger.json --assumptions assumptions.json", False),
        ("bundle-checksums", "Write deterministic SHA256SUMS and JSON/Markdown manifests for release files.", ["repo root", "docs", "demos", "optional dist wheel/sdist"], ["SHA256SUMS.txt", "bundle_manifest.json", "bundle_manifest.md"], "portfolio-liquidity-runway-lab bundle-checksums --root . --out docs/bundle-checksums", False),
        ("evidence-bundle", "Copy selected review evidence into a deterministic offline bundle.", ["repo docs and demo evidence"], ["index.md", "index.html", "SHA256SUMS.txt", "evidence_manifest.json", "boundary_risks.md", "command_replay.md"], "portfolio-liquidity-runway-lab evidence-bundle --root . --out docs/evidence-bundle", True),
        ("template-pack", "Export clean CSV and JSON starter templates for offline user portfolios.", ["built-in starter templates"], ["README.md", "template_manifest.json", "portfolio.csv", "ledger.csv", "portfolio.json", "ledger.json", "assumptions.json"], "portfolio-liquidity-runway-lab template-pack --out docs/template-pack", False),
        ("fixture-doctor", "Run all workflows against isolated copied fixtures.", ["bundled or supplied examples"], ["fixture_doctor.json", "fixture_doctor.md"], "portfolio-liquidity-runway-lab fixture-doctor --out docs", True),
        ("docs-export", "Export compact static documentation bundle.", ["README and generated release evidence"], ["static-docs/index.html", "static-docs/index.md", "static-docs/*.md"], "portfolio-liquidity-runway-lab docs-export --out docs/static-docs", True),
        ("command-matrix", "Export the full deterministic command catalog.", ["built-in command metadata"], ["command_matrix.json", "command_matrix.md", "command_matrix.html"], "portfolio-liquidity-runway-lab command-matrix --out docs/command-matrix", True),
        ("golden-replay", "Regenerate committed demos into a temp directory and compare hashes/content.", ["repo root", "committed demo artifacts"], ["golden_replay.json", "golden_replay.md"], "portfolio-liquidity-runway-lab golden-replay --root . --out docs/golden-replay", False),
        ("release-deck", "Build a one-page promotion and release evidence deck.", ["repo docs and demo evidence"], ["release_deck.md", "release_deck.html"], "portfolio-liquidity-runway-lab release-deck --root . --out docs/release-deck", True),
        ("quickstart-check", "Copy packaged examples and build a packet from an empty directory.", ["bundled examples"], ["copied examples", "packet artifacts"], "portfolio-liquidity-runway-lab quickstart-check --out liquidity-demo", True),
        ("selfcheck", "Run deterministic smoke checks against bundled examples.", ["bundled examples"], ["stdout JSON"], "portfolio-liquidity-runway-lab selfcheck", True),
        ("public-scan", "Scan repo tree for public-release concerns.", ["repo root"], ["stdout JSON", "optional JSON file"], "portfolio-liquidity-runway-lab public-scan --root .", False),
        ("release-manifest", "Emit deterministic release file inventory.", ["repo root"], ["stdout JSON", "optional JSON file"], "portfolio-liquidity-runway-lab release-manifest --out docs/release_manifest.json", False),
        ("maturity-report", "Report basic repo maturity checks.", ["repo root"], ["stdout JSON", "optional JSON file"], "portfolio-liquidity-runway-lab maturity-report --out docs/maturity_report.json", False),
    ]
    return [
        {
            "command": command,
            "purpose": purpose,
            "inputs": inputs,
            "outputs": outputs,
            "demo_command": demo_command,
            "risk_boundary": boundary,
            "no_script_html": no_script_html,
        }
        for command, purpose, inputs, outputs, demo_command, no_script_html in rows
    ]


def _copy_example_set(target: Path, source: Optional[Path] = None) -> Dict[str, str]:
    target.mkdir(parents=True, exist_ok=True)
    copied = {}
    for name in ("portfolio.json", "portfolio_concentrated.json", "ledger.json", "assumptions.json", "history.json"):
        src = source / name if source else bundled_example_path(name)
        dst = target / name
        shutil.copyfile(src, dst)
        copied[name] = _public_path(dst, target.parent)
    for name in ("portfolio.csv", "ledger.csv"):
        src = source / name if source and (source / name).exists() else bundled_csv_example_path(name)
        dst = target / name
        shutil.copyfile(src, dst)
        copied[name] = _public_path(dst, target.parent)
    return copied


def fixture_doctor(work_dir: Path, examples_dir: Optional[Path] = None) -> Dict[str, Any]:
    examples = work_dir / "examples"
    copied = _copy_example_set(examples, examples_dir)
    portfolios_dir = work_dir / "portfolios"
    portfolios_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(examples / "portfolio.json", portfolios_dir / "portfolio.json")
    shutil.copyfile(examples / "portfolio_concentrated.json", portfolios_dir / "portfolio_concentrated.json")

    plan = [
        {"command": "build-packet", "argv": ["build-packet", "--portfolio", copied["portfolio.json"], "--ledger", copied["ledger.json"], "--assumptions", copied["assumptions.json"], "--scenario", "stress", "--out", _public_path(work_dir / "packet", work_dir)]},
        {"command": "static-dashboard", "argv": ["static-dashboard", "--portfolio", copied["portfolio.json"], "--ledger", copied["ledger.json"], "--assumptions", copied["assumptions.json"], "--out", _public_path(work_dir / "dashboard", work_dir)]},
        {"command": "scenario-gallery", "argv": ["scenario-gallery", "--portfolio", copied["portfolio.json"], "--ledger", copied["ledger.json"], "--assumptions", copied["assumptions.json"], "--out", _public_path(work_dir / "scenario-gallery", work_dir)]},
        {"command": "assumption-audit", "argv": ["assumption-audit", "--portfolio", copied["portfolio_concentrated.json"], "--ledger", copied["ledger.json"], "--assumptions", copied["assumptions.json"], "--out", _public_path(work_dir / "assumption-audit", work_dir)]},
        {"command": "batch-compare", "argv": ["batch-compare", "--portfolios-dir", _public_path(portfolios_dir, work_dir), "--ledger", copied["ledger.json"], "--assumptions", copied["assumptions.json"], "--scenarios", "base,stress", "--out", _public_path(work_dir / "batch-compare", work_dir)]},
        {"command": "casebook", "argv": ["casebook", "--portfolio", copied["portfolio.json"], "--ledger", copied["ledger.json"], "--assumptions", copied["assumptions.json"], "--portfolios-dir", _public_path(portfolios_dir, work_dir), "--scenario", "stress", "--scenarios", "base,stress,income_shock", "--out", _public_path(work_dir / "casebook", work_dir)]},
        {"command": "visual-receipt", "argv": ["visual-receipt", "--portfolio", copied["portfolio.json"], "--ledger", copied["ledger.json"], "--assumptions", copied["assumptions.json"], "--scenario", "stress", "--out", _public_path(work_dir / "visual_receipt.md", work_dir)]},
        {"command": "compare-history", "argv": ["compare-history", "--history", copied["history.json"], "--out", _public_path(work_dir / "history_compare.json", work_dir)]},
        {"command": "review-ledger", "argv": ["review-ledger", "--ledger", copied["ledger.json"], "--out", _public_path(work_dir / "ledger_review.json", work_dir)]},
        {"command": "schema-export", "argv": ["schema-export", "--out", _public_path(work_dir / "schema-export", work_dir)]},
        {"command": "csv-import", "argv": ["csv-import", "--portfolio-csv", copied["portfolio.csv"], "--ledger-csv", copied["ledger.csv"], "--out", _public_path(work_dir / "csv-import", work_dir)]},
        {"command": "csv-export", "argv": ["csv-export", "--packet", _public_path(work_dir / "packet" / "liquidity_packet.json", work_dir), "--out", _public_path(work_dir / "csv-export", work_dir)]},
        {"command": "input-lint", "argv": ["input-lint", "--portfolio", copied["portfolio.json"], "--ledger", copied["ledger.json"], "--assumptions", copied["assumptions.json"], "--portfolio-csv", copied["portfolio.csv"], "--ledger-csv", copied["ledger.csv"]]},
        {"command": "bundle-checksums", "argv": ["bundle-checksums", "--root", ".", "--out", _public_path(work_dir / "bundle-checksums", work_dir)]},
        {"command": "evidence-bundle", "argv": ["evidence-bundle", "--root", ".", "--out", _public_path(work_dir / "evidence-bundle", work_dir)]},
        {"command": "template-pack", "argv": ["template-pack", "--out", _public_path(work_dir / "template-pack", work_dir)]},
        {"command": "docs-export", "argv": ["docs-export", "--root", ".", "--out", _public_path(work_dir / "static-docs", work_dir)]},
        {"command": "command-matrix", "argv": ["command-matrix", "--out", _public_path(work_dir / "command-matrix", work_dir)]},
        {"command": "release-deck", "argv": ["release-deck", "--root", ".", "--out", _public_path(work_dir / "release-deck", work_dir)]},
        {"command": "artifact-catalog", "argv": ["artifact-catalog", "--root", ".", "--paths", "packet,dashboard,scenario-gallery,assumption-audit,batch-compare,casebook,schema-export,csv-import,csv-export,static-docs", "--out", _public_path(work_dir / "catalog", work_dir)]},
        {"command": "release-check", "argv": ["release-check", "--root", ".", "--out", _public_path(work_dir / "release-check", work_dir)]},
        {"command": "public-scan", "argv": ["public-scan", "--root", ".", "--out", _public_path(work_dir / "public_scan.json", work_dir)]},
        {"command": "release-manifest", "argv": ["release-manifest", "--root", ".", "--out", _public_path(work_dir / "release_manifest.json", work_dir)]},
        {"command": "maturity-report", "argv": ["maturity-report", "--root", ".", "--out", _public_path(work_dir / "maturity_report.json", work_dir)]},
    ]

    results = []
    for item in plan:
        command = item["command"]
        try:
            if command in {"build-packet", "static-dashboard"}:
                paths = build_packet(examples / "portfolio.json", examples / "ledger.json", examples / "assumptions.json", work_dir / ("packet" if command == "build-packet" else "dashboard"), "stress" if command == "build-packet" else None)
                output_paths = [_public_path(paths.json_path, work_dir), _public_path(paths.markdown_path, work_dir), _public_path(paths.html_path, work_dir)]
                passed = paths.html_path.exists() and not _html_has_unsafe_content(paths.html_path)
            elif command == "scenario-gallery":
                paths = build_scenario_gallery(examples / "portfolio.json", examples / "ledger.json", examples / "assumptions.json", work_dir / "scenario-gallery")
                output_paths = [_public_path(paths.json_path, work_dir), _public_path(paths.markdown_path, work_dir), _public_path(paths.html_path, work_dir)]
                passed = not _html_has_unsafe_content(paths.html_path)
            elif command == "assumption-audit":
                paths = build_assumption_audit(examples / "portfolio_concentrated.json", examples / "ledger.json", examples / "assumptions.json", work_dir / "assumption-audit")
                output_paths = [_public_path(paths.json_path, work_dir), _public_path(paths.markdown_path, work_dir)]
                passed = paths.json_path.exists() and paths.markdown_path.exists()
            elif command == "batch-compare":
                paths = build_batch_compare(portfolios_dir, examples / "ledger.json", examples / "assumptions.json", work_dir / "batch-compare", ["base", "stress"])
                output_paths = [_public_path(paths.json_path, work_dir), _public_path(paths.markdown_path, work_dir), _public_path(paths.html_path, work_dir)]
                passed = not _html_has_unsafe_content(paths.html_path)
            elif command == "casebook":
                paths = build_casebook(examples / "portfolio.json", examples / "ledger.json", examples / "assumptions.json", portfolios_dir, work_dir / "casebook", "stress", ["base", "stress", "income_shock"])
                output_paths = [_public_path(paths.json_path, work_dir), _public_path(paths.markdown_path, work_dir), _public_path(paths.html_path, work_dir)]
                passed = not _html_has_unsafe_content(paths.html_path)
            elif command == "visual-receipt":
                path = build_visual_receipt(examples / "portfolio.json", examples / "ledger.json", examples / "assumptions.json", work_dir / "visual_receipt.md", "stress")
                output_paths = [_public_path(path, work_dir)]
                passed = path.exists()
            elif command == "compare-history":
                out = work_dir / "history_compare.json"
                dump_json(compare_history(load_json(examples / "history.json")), out)
                output_paths = [_public_path(out, work_dir)]
                passed = out.exists()
            elif command == "review-ledger":
                out = work_dir / "ledger_review.json"
                dump_json(review_ledger(load_json(examples / "ledger.json")), out)
                output_paths = [_public_path(out, work_dir)]
                passed = out.exists()
            elif command == "schema-export":
                paths = build_schema_export(work_dir / "schema-export")
                output_paths = [_public_path(paths.json_path, work_dir), _public_path(paths.markdown_path, work_dir)]
                passed = paths.json_path.exists() and paths.markdown_path.exists()
            elif command == "csv-import":
                paths = build_csv_import(examples / "portfolio.csv", examples / "ledger.csv", work_dir / "csv-import")
                output_paths = [
                    _public_path(paths.portfolio_json_path, work_dir),
                    _public_path(paths.ledger_json_path, work_dir),
                    _public_path(paths.report_json_path, work_dir),
                    _public_path(paths.report_markdown_path, work_dir),
                ]
                passed = load_json(paths.report_json_path)["status"] == "pass"
            elif command == "csv-export":
                paths = build_csv_export(work_dir / "packet" / "liquidity_packet.json", work_dir / "csv-export")
                output_paths = [
                    _public_path(paths.assets_csv_path, work_dir),
                    _public_path(paths.runway_csv_path, work_dir),
                    _public_path(paths.warnings_csv_path, work_dir),
                    _public_path(paths.bucket_summaries_csv_path, work_dir),
                    _public_path(paths.manifest_json_path, work_dir),
                    _public_path(paths.manifest_markdown_path, work_dir),
                ]
                passed = load_json(paths.manifest_json_path)["status"] == "pass"
            elif command == "input-lint":
                result = input_lint(
                    [
                        (examples / "portfolio.json", "portfolio_json"),
                        (examples / "ledger.json", "ledger_json"),
                        (examples / "assumptions.json", "assumptions_json"),
                        (examples / "portfolio.csv", "portfolio_csv"),
                        (examples / "ledger.csv", "ledger_csv"),
                    ]
                )
                output_paths = ["stdout JSON"]
                passed = result["status"] == "pass"
            elif command == "bundle-checksums":
                paths = build_bundle_checksums(work_dir, work_dir / "bundle-checksums", ["examples", "packet", "scenario-gallery", "assumption-audit", "batch-compare", "casebook", "schema-export", "csv-import", "csv-export"])
                output_paths = [_public_path(paths.sums_path, work_dir), _public_path(paths.manifest_json_path, work_dir), _public_path(paths.manifest_markdown_path, work_dir)]
                passed = paths.sums_path.exists() and load_json(paths.manifest_json_path)["file_count"] > 0
            elif command == "evidence-bundle":
                paths = build_evidence_bundle(work_dir, work_dir / "evidence-bundle")
                output_paths = [_public_path(paths.index_markdown_path, work_dir), _public_path(paths.index_html_path, work_dir), _public_path(paths.checksums_path, work_dir), _public_path(paths.manifest_json_path, work_dir)]
                passed = paths.index_html_path.exists() and not _html_has_unsafe_content(paths.index_html_path)
            elif command == "template-pack":
                paths = build_template_pack(work_dir / "template-pack")
                output_paths = [_public_path(paths.readme_path, work_dir), _public_path(paths.manifest_json_path, work_dir)]
                passed = (work_dir / "template-pack" / "portfolio.csv").exists() and load_json(paths.manifest_json_path)["file_count"] >= 6
            elif command == "docs-export":
                paths = build_docs_export(work_dir, work_dir / "static-docs")
                output_paths = [_public_path(paths.index_html_path, work_dir), _public_path(paths.index_markdown_path, work_dir)]
                passed = paths.index_html_path.exists() and not _html_has_unsafe_content(paths.index_html_path)
            elif command == "command-matrix":
                paths = build_command_matrix(work_dir / "command-matrix")
                output_paths = [_public_path(paths.json_path, work_dir), _public_path(paths.markdown_path, work_dir), _public_path(paths.html_path, work_dir)]
                passed = paths.html_path.exists() and not _html_has_unsafe_content(paths.html_path)
            elif command == "release-deck":
                paths = build_release_deck(work_dir, work_dir / "release-deck")
                output_paths = [_public_path(paths.markdown_path, work_dir), _public_path(paths.html_path, work_dir)]
                passed = paths.html_path.exists() and not _html_has_unsafe_content(paths.html_path)
            elif command == "artifact-catalog":
                paths = build_artifact_catalog(work_dir, work_dir / "catalog", ["packet", "dashboard", "scenario-gallery", "assumption-audit", "batch-compare", "casebook", "schema-export", "csv-import", "csv-export", "static-docs"])
                output_paths = [_public_path(paths.json_path, work_dir), _public_path(paths.markdown_path, work_dir)]
                passed = load_json(paths.json_path)["artifact_count"] > 0
            elif command == "release-check":
                paths = build_release_check(work_dir, work_dir / "release-check", ["examples/portfolio.json", "examples/ledger.json", "packet/liquidity_packet.html"])
                output_paths = [_public_path(paths.json_path, work_dir), _public_path(paths.markdown_path, work_dir)]
                passed = load_json(paths.json_path)["checks"]["html_no_script_tags"]
            elif command == "public-scan":
                out = work_dir / "public_scan.json"
                result = public_scan(work_dir)
                dump_json(result, out)
                output_paths = [_public_path(out, work_dir)]
                passed = result["status"] == "pass"
            elif command == "release-manifest":
                out = work_dir / "release_manifest.json"
                dump_json(release_manifest(work_dir), out)
                output_paths = [_public_path(out, work_dir)]
                passed = out.exists()
            elif command == "maturity-report":
                out = work_dir / "maturity_report.json"
                dump_json(maturity_report(work_dir), out)
                output_paths = [_public_path(out, work_dir)]
                passed = out.exists()
            else:
                output_paths = []
                passed = False
            results.append({"command": command, "status": "pass" if passed else "fail", "argv": item["argv"], "outputs": output_paths, "message": ""})
        except Exception as exc:
            results.append({"command": command, "status": "fail", "argv": item["argv"], "outputs": [], "message": str(exc)})
    status = "pass" if all(result["status"] == "pass" for result in results) else "fail"
    return {
        "boundary": BOUNDARY_TEXT,
        "status": status,
        "work_dir": _public_path(work_dir),
        "examples": copied,
        "command_plan": plan,
        "results": results,
    }


def render_fixture_doctor_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# Fixture Doctor",
        "",
        f"> {report['boundary']}",
        "",
        f"Status: `{report['status']}`",
        f"Work dir: `{report['work_dir']}`",
        "",
        "## Copied Examples",
        "",
    ]
    for name in sorted(report["examples"]):
        lines.append(f"- `{name}` -> `{report['examples'][name]}`")
    lines.extend(["", "## Command Plan", "", "| Command | Args |", "| --- | --- |"])
    for item in report["command_plan"]:
        lines.append(f"| `{item['command']}` | `{' '.join(item['argv'])}` |")
    lines.extend(["", "## Results", "", "| Command | Status | Outputs | Message |", "| --- | --- | --- | --- |"])
    for result in report["results"]:
        outputs = ", ".join(f"`{path}`" for path in result["outputs"]) or ""
        lines.append(f"| `{result['command']}` | `{result['status']}` | {outputs} | {result['message']} |")
    lines.append("")
    return "\n".join(lines)


def build_fixture_doctor(out_dir: Path, work_dir: Optional[Path] = None, examples_dir: Optional[Path] = None) -> FixtureDoctorPaths:
    out_dir.mkdir(parents=True, exist_ok=True)
    temp_work: Optional[tempfile.TemporaryDirectory[str]] = None
    if work_dir is None:
        temp_work = tempfile.TemporaryDirectory(prefix="plrl-fixture-doctor-")
        actual_work = Path(temp_work.name)
    else:
        actual_work = work_dir
        actual_work.mkdir(parents=True, exist_ok=True)
    try:
        report = fixture_doctor(actual_work, examples_dir)
        if temp_work is not None:
            report["work_dir"] = "temporary"
    finally:
        if temp_work is not None:
            temp_work.cleanup()
    json_path = out_dir / "fixture_doctor.json"
    markdown_path = out_dir / "fixture_doctor.md"
    dump_json(report, json_path)
    markdown_path.write_text(render_fixture_doctor_markdown(report), encoding="utf-8")
    return FixtureDoctorPaths(out_dir, json_path, markdown_path, actual_work)


def _read_summary(path: Path, fallback: str) -> str:
    if not path.exists():
        return fallback
    text = path.read_text(encoding="utf-8")
    lines = []
    for line in text.splitlines():
        if line.startswith("# ") or line.startswith("## "):
            lines.append(line)
        elif line.strip() and len(lines) < 8:
            lines.append(line)
        if len(lines) >= 12:
            break
    return "\n".join(lines) if lines else fallback


def render_docs_index_markdown(root: Path) -> str:
    lines = [
        "# Static Documentation Bundle",
        "",
        f"> {BOUNDARY_TEXT}",
        "",
        "## README Summary",
        "",
        _read_summary(root / "README.md", "README.md was not present in this export root."),
        "",
        "## Links",
        "",
        "- [Command matrix](command_matrix.md)",
        "- [Boundaries](boundaries.md)",
        "- [Demos](demos.md)",
        "- [Release evidence](release_evidence.md)",
        "",
    ]
    return "\n".join(lines)


def render_command_matrix_markdown() -> str:
    lines = [
        "# Command Matrix",
        "",
        f"> {BOUNDARY_TEXT}",
        "",
        f"Version: `{PROJECT_VERSION}`",
        "",
        "| Command | Purpose | Inputs | Outputs | Demo command | Risk boundary | Static no-JS HTML |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in command_matrix_data():
        lines.append(
            f"| `{item['command']}` | {item['purpose']} | {', '.join(item['inputs']) or 'none'} | "
            f"{', '.join(item['outputs']) or 'stdout'} | `{item['demo_command']}` | {item['risk_boundary']} | "
            f"{str(item['no_script_html']).lower()} |"
        )
    lines.append("")
    return "\n".join(lines)


def command_matrix() -> Dict[str, Any]:
    return {"boundary": BOUNDARY_TEXT, "version": PROJECT_VERSION, "commands": command_matrix_data()}


def render_command_matrix_html(catalog: Mapping[str, Any]) -> str:
    rows = []
    for item in catalog["commands"]:
        rows.append(
            "<tr>"
            f"<td><code>{html.escape(item['command'])}</code></td>"
            f"<td>{html.escape(item['purpose'])}</td>"
            f"<td>{html.escape(', '.join(item['inputs']) or 'none')}</td>"
            f"<td>{html.escape(', '.join(item['outputs']) or 'stdout')}</td>"
            f"<td><code>{html.escape(item['demo_command'])}</code></td>"
            f"<td>{html.escape(item['risk_boundary'])}</td>"
            f"<td>{html.escape(str(item['no_script_html']).lower())}</td>"
            "</tr>"
        )
    body = (
        "<h1>Command Matrix</h1>\n"
        f"<blockquote>{html.escape(str(catalog['boundary']))}</blockquote>\n"
        f"<p>Version: <code>{html.escape(str(catalog['version']))}</code></p>\n"
        "<table><tr><th>Command</th><th>Purpose</th><th>Inputs</th><th>Outputs</th>"
        "<th>Demo command</th><th>Risk boundary</th><th>Static no-JS HTML</th></tr>\n"
        + "\n".join(rows)
        + "\n</table>"
    )
    return _html_shell("Command Matrix", body)


def build_command_matrix(out_dir: Path) -> CommandMatrixPaths:
    catalog = command_matrix()
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "command_matrix.json"
    markdown_path = out_dir / "command_matrix.md"
    html_path = out_dir / "command_matrix.html"
    dump_json(catalog, json_path)
    markdown_path.write_text(render_command_matrix_markdown(), encoding="utf-8")
    html_path.write_text(render_command_matrix_html(catalog), encoding="utf-8")
    return CommandMatrixPaths(out_dir, json_path, markdown_path, html_path)


def render_boundaries_markdown() -> str:
    return "\n".join(
        [
            "# Boundaries",
            "",
            BOUNDARY_TEXT,
            "",
            "- No live market, account, broker, or banking data is fetched.",
            "- No orders, allocations, optimizations, buy/sell/hold recommendations, or predictions are produced.",
            "- Outputs are deterministic local review artifacts for records and professional discussion.",
            "",
        ]
    )


def render_demos_markdown(root: Path) -> str:
    demo_paths = []
    demo_root = root / "demo"
    if demo_root.exists():
        demo_paths = sorted(path.relative_to(root).as_posix() for path in demo_root.rglob("*") if path.is_file())
    lines = ["# Demos", "", "| Artifact |", "| --- |"]
    if demo_paths:
        lines.extend(f"| `{path}` |" for path in demo_paths)
    else:
        lines.append("| No demo directory was present in this export root. |")
    lines.append("")
    return "\n".join(lines)


def render_release_evidence_markdown(root: Path) -> str:
    evidence = [
        "docs/release_manifest.json",
        "docs/maturity_report.json",
        "docs/release_check.json",
        "docs/artifact_catalog.json",
        "docs/schema_guide.json",
        "docs/fixture_doctor.json",
        "docs/bundle-checksums/bundle_manifest.json",
        "docs/evidence-bundle/evidence_manifest.json",
        "docs/template-pack/template_manifest.json",
    ]
    lines = ["# Release Evidence", "", "| Artifact | Present |", "| --- | --- |"]
    for rel in evidence:
        lines.append(f"| `{rel}` | {str((root / rel).exists()).lower()} |")
    lines.append("")
    return "\n".join(lines)


def render_docs_index_html(index_markdown: str) -> str:
    body = [
        "<h1>Static Documentation Bundle</h1>",
        f"<blockquote>{html.escape(BOUNDARY_TEXT)}</blockquote>",
        "<h2>README Summary</h2>",
    ]
    in_list = False
    for line in index_markdown.splitlines():
        if line.startswith("# ") or line.startswith("## ") or line.startswith("> "):
            continue
        if line.startswith("- ["):
            if not in_list:
                body.append("<ul>")
                in_list = True
            label = line.split("[", 1)[1].split("]", 1)[0]
            href = line.split("(", 1)[1].split(")", 1)[0]
            body.append(f'<li><a href="{html.escape(href)}">{html.escape(label)}</a></li>')
        elif line.strip():
            if in_list:
                body.append("</ul>")
                in_list = False
            body.append(f"<p>{html.escape(line)}</p>")
    if in_list:
        body.append("</ul>")
    return _html_shell("Static Documentation Bundle", "\n".join(body))


def build_docs_export(root: Path, out_dir: Path) -> DocsExportPaths:
    out_dir.mkdir(parents=True, exist_ok=True)
    index_md = render_docs_index_markdown(root)
    files = {
        "index.md": index_md,
        "command_matrix.md": render_command_matrix_markdown(),
        "boundaries.md": render_boundaries_markdown(),
        "demos.md": render_demos_markdown(root),
        "release_evidence.md": render_release_evidence_markdown(root),
    }
    for name, text in files.items():
        (out_dir / name).write_text(text, encoding="utf-8")
    index_html_path = out_dir / "index.html"
    index_html_path.write_text(render_docs_index_html(index_md), encoding="utf-8")
    return DocsExportPaths(out_dir, index_html_path, out_dir / "index.md")


def _release_candidate_files(root: Path, include_paths: Iterable[str], exclude_dir: Optional[Path] = None) -> List[Path]:
    files: List[Path] = []
    exclude_resolved = exclude_dir.resolve() if exclude_dir else None
    seen = set()
    for part in include_paths:
        base = root / part
        if not base.exists():
            continue
        candidates = [base] if base.is_file() else sorted(base.rglob("*"))
        for path in candidates:
            if not path.is_file():
                continue
            if exclude_resolved and exclude_resolved in path.resolve().parents:
                continue
            rel_path = path.relative_to(root)
            if _is_ignored_release_path(rel_path):
                continue
            rel = rel_path.as_posix()
            if rel in seen:
                continue
            seen.add(rel)
            files.append(path)
    for dist_path in sorted((root / "dist").glob("*")) if (root / "dist").exists() else []:
        if dist_path.is_file() and (dist_path.suffix in {".whl", ".gz", ".zip"} or ".tar." in dist_path.name):
            rel = dist_path.relative_to(root).as_posix()
            if rel not in seen:
                seen.add(rel)
                files.append(dist_path)
    return sorted(files, key=lambda item: item.relative_to(root).as_posix())


def bundle_checksums(root: Path, include_paths: Iterable[str], exclude_dir: Optional[Path] = None) -> Dict[str, Any]:
    files = _release_candidate_files(root, include_paths, exclude_dir)
    entries = [
        {
            "path": path.relative_to(root).as_posix(),
            "size_bytes": path.stat().st_size,
            "sha256": _sha256_file(path),
        }
        for path in files
    ]
    return {
        "boundary": BOUNDARY_TEXT,
        "version": PROJECT_VERSION,
        "root": _public_path(root, root),
        "file_count": len(entries),
        "files": entries,
    }


def render_sha256sums(manifest: Mapping[str, Any]) -> str:
    return "".join(f"{item['sha256']}  {item['path']}\n" for item in manifest["files"])


def render_bundle_manifest_markdown(manifest: Mapping[str, Any]) -> str:
    lines = [
        "# Bundle Checksums",
        "",
        f"> {manifest['boundary']}",
        "",
        f"Version: `{manifest['version']}`",
        f"File count: {manifest['file_count']}",
        "",
        "| Path | Size bytes | SHA256 |",
        "| --- | ---: | --- |",
    ]
    for item in manifest["files"]:
        lines.append(f"| `{item['path']}` | {item['size_bytes']} | `{item['sha256']}` |")
    lines.append("")
    return "\n".join(lines)


def build_bundle_checksums(root: Path, out_dir: Path, include_paths: Iterable[str] = ("README.md", "LICENSE", "MANIFEST.in", "pyproject.toml", "portfolio_liquidity_runway_lab", "docs", "demo", "skills", "tests")) -> BundleChecksumPaths:
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = bundle_checksums(root, include_paths, out_dir)
    sums_path = out_dir / "SHA256SUMS.txt"
    json_path = out_dir / "bundle_manifest.json"
    markdown_path = out_dir / "bundle_manifest.md"
    _deterministic_text_file(sums_path, render_sha256sums(manifest))
    dump_json(manifest, json_path)
    _deterministic_text_file(markdown_path, render_bundle_manifest_markdown(manifest))
    return BundleChecksumPaths(out_dir, sums_path, json_path, markdown_path)


EVIDENCE_SOURCE_FILES = (
    "README.md",
    "docs/cold_start_walkthrough.md",
    "docs/release_readiness_review.md",
    "docs/release_manifest.json",
    "docs/maturity_report.json",
    "docs/release_check.json",
    "docs/release_check.md",
    "docs/artifact_catalog.json",
    "docs/artifact_catalog.md",
    "docs/schema_guide.md",
    "docs/command-matrix/command_matrix.md",
    "docs/golden-replay/golden_replay.md",
    "docs/release-deck/release_deck.md",
    "demo/visual_receipt.md",
    "demo/casebook/casebook.md",
    "demo/scenario-gallery/scenario_gallery.md",
    "demo/assumption-audit/assumption_audit.md",
    "demo/batch-compare/batch_compare.md",
    "demo/csv-import/import_report.md",
    "demo/csv-export/export_manifest.md",
    "demo/static-docs/index.md",
    "demo/command-matrix/command_matrix.md",
    "demo/golden-replay/golden_replay.md",
    "demo/release-deck/release_deck.md",
)


def _evidence_boundary_page() -> str:
    return "\n".join(
        [
            "# Boundary And Risks",
            "",
            BOUNDARY_TEXT,
            "",
            "## Review Boundary",
            "",
            "- Inputs are local synthetic or user-supplied files.",
            "- Outputs are deterministic review artifacts, not instructions to transact.",
            "- Reviewers must verify liquidity tiers, scheduled events, fees, yields, and scenario assumptions against source records.",
            "",
            "## Residual Risks",
            "",
            "- Stale user inputs can make a packet misleading even when all checks pass.",
            "- Static scenarios do not model every market, tax, legal, custody, or operational constraint.",
            "- Public scan and release check are release aids, not complete security or compliance audits.",
            "",
        ]
    )


def _evidence_replay_notes() -> str:
    lines = [
        "# Command Replay Notes",
        "",
        "Run from the repository root to refresh the review evidence:",
        "",
        "```bash",
        "python -m portfolio_liquidity_runway_lab selfcheck",
        "python -m portfolio_liquidity_runway_lab scenario-gallery --out demo/scenario-gallery",
        "python -m portfolio_liquidity_runway_lab assumption-audit --portfolio portfolio_liquidity_runway_lab/examples/portfolio_concentrated.json --out demo/assumption-audit",
        "python -m portfolio_liquidity_runway_lab batch-compare --portfolios-dir demo/batch-inputs --scenarios base,stress --out demo/batch-compare",
        "python -m portfolio_liquidity_runway_lab casebook --portfolios-dir demo/batch-inputs --scenario stress --scenarios base,stress,income_shock --out demo/casebook",
        "python -m portfolio_liquidity_runway_lab schema-export --out docs",
        "python -m portfolio_liquidity_runway_lab command-matrix --out docs/command-matrix",
        "python -m portfolio_liquidity_runway_lab golden-replay --root . --out docs/golden-replay",
        "python -m portfolio_liquidity_runway_lab release-deck --root . --out docs/release-deck",
        "python -m portfolio_liquidity_runway_lab artifact-catalog --out docs",
        "python -m portfolio_liquidity_runway_lab bundle-checksums --root . --out docs/bundle-checksums",
        "python -m portfolio_liquidity_runway_lab evidence-bundle --root . --out docs/evidence-bundle",
        "python -m portfolio_liquidity_runway_lab template-pack --out docs/template-pack",
        "python -m portfolio_liquidity_runway_lab release-check --out docs",
        "```",
        "",
    ]
    return "\n".join(lines)


def render_evidence_index_markdown(manifest: Mapping[str, Any]) -> str:
    lines = [
        "# Evidence Bundle",
        "",
        f"> {manifest['boundary']}",
        "",
        f"Version: `{manifest['version']}`",
        f"Copied artifacts: {manifest['artifact_count']}",
        "",
        "## Bundle Files",
        "",
        "- `index.md`",
        "- `index.html`",
        "- `SHA256SUMS.txt`",
        "- `evidence_manifest.json`",
        "- `boundary_risks.md`",
        "- `command_replay.md`",
        "",
        "## Copied Evidence",
        "",
        "| Source | Bundle path | SHA256 |",
        "| --- | --- | --- |",
    ]
    for item in manifest["artifacts"]:
        lines.append(f"| `{item['source_path']}` | `{item['bundle_path']}` | `{item['sha256']}` |")
    lines.append("")
    return "\n".join(lines)


def render_evidence_index_html(index_markdown: str) -> str:
    body = []
    in_table = False
    in_list = False
    for line in index_markdown.splitlines():
        if line.startswith("# "):
            body.append(f"<h1>{html.escape(line[2:])}</h1>")
        elif line.startswith("## "):
            if in_table:
                body.append("</table>")
                in_table = False
            if in_list:
                body.append("</ul>")
                in_list = False
            body.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("> "):
            body.append(f"<blockquote>{html.escape(line[2:])}</blockquote>")
        elif line.startswith("- "):
            if not in_list:
                body.append("<ul>")
                in_list = True
            body.append(f"<li>{html.escape(line[2:])}</li>")
        elif line.startswith("| ") and not line.startswith("| ---"):
            if not in_table:
                body.append("<table>")
                in_table = True
            cells = [cell.strip().strip("`") for cell in line.strip("|").split("|")]
            tag = "th" if cells and cells[0] == "Source" else "td"
            body.append("<tr>" + "".join(f"<{tag}>{html.escape(cell)}</{tag}>" for cell in cells) + f"</tr>")
        elif line.startswith("| ---"):
            continue
        elif line.strip():
            body.append(f"<p>{html.escape(line)}</p>")
    if in_table:
        body.append("</table>")
    if in_list:
        body.append("</ul>")
    return _html_shell("Evidence Bundle", "\n".join(body))


def build_evidence_bundle(root: Path, out_dir: Path, source_files: Iterable[str] = EVIDENCE_SOURCE_FILES) -> EvidenceBundlePaths:
    out_dir.mkdir(parents=True, exist_ok=True)
    artifacts = []
    for rel in source_files:
        source = root / rel
        if not source.is_file():
            continue
        bundle_path = Path("files") / rel
        destination = out_dir / bundle_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        artifacts.append(
            {
                "source_path": rel,
                "bundle_path": bundle_path.as_posix(),
                "size_bytes": destination.stat().st_size,
                "sha256": _sha256_file(destination),
            }
        )
    artifacts.sort(key=lambda item: item["source_path"])
    boundary_path = out_dir / "boundary_risks.md"
    replay_path = out_dir / "command_replay.md"
    _deterministic_text_file(boundary_path, _evidence_boundary_page())
    _deterministic_text_file(replay_path, _evidence_replay_notes())
    for path in (boundary_path, replay_path):
        artifacts.append(
            {
                "source_path": "generated",
                "bundle_path": path.relative_to(out_dir).as_posix(),
                "size_bytes": path.stat().st_size,
                "sha256": _sha256_file(path),
            }
        )
    artifacts.sort(key=lambda item: item["bundle_path"])
    manifest = {
        "boundary": BOUNDARY_TEXT,
        "version": PROJECT_VERSION,
        "root": _public_path(root, root),
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
    }
    index_md = render_evidence_index_markdown(manifest)
    index_md_path = out_dir / "index.md"
    index_html_path = out_dir / "index.html"
    checksums_path = out_dir / "SHA256SUMS.txt"
    manifest_json_path = out_dir / "evidence_manifest.json"
    _deterministic_text_file(index_md_path, index_md)
    _deterministic_text_file(index_html_path, render_evidence_index_html(index_md))
    _deterministic_text_file(checksums_path, "".join(f"{item['sha256']}  {item['bundle_path']}\n" for item in artifacts))
    dump_json(manifest, manifest_json_path)
    return EvidenceBundlePaths(out_dir, index_md_path, index_html_path, checksums_path, manifest_json_path)


def _template_portfolio() -> Dict[str, Any]:
    return {
        "name": "Offline starter portfolio",
        "currency": "USD",
        "assets": [
            {"name": "Operating cash", "value": 25000.0, "liquidity_tier": "same_day", "annual_yield_rate": 0.01, "annual_fee_rate": 0.0},
            {"name": "Short settlement fund", "value": 15000.0, "liquidity_tier": "one_week", "annual_yield_rate": 0.025, "annual_fee_rate": 0.001},
            {"name": "Term reserve", "value": 20000.0, "liquidity_tier": "one_month", "annual_yield_rate": 0.035, "annual_fee_rate": 0.002},
            {"name": "Restricted holding", "value": 10000.0, "liquidity_tier": "locked", "annual_yield_rate": 0.0, "annual_fee_rate": 0.0},
        ],
    }


def _template_ledger() -> Dict[str, Any]:
    return {
        "monthly_income": 8000.0,
        "monthly_expenses": 9500.0,
        "scheduled_events": [
            {"month": 3, "type": "outflow", "label": "Quarterly tax estimate", "amount": 6000.0},
            {"month": 6, "type": "inflow", "label": "Expected receivable", "amount": 5000.0},
        ],
    }


def _template_assumptions() -> Dict[str, Any]:
    return {
        "months": 12,
        "target_reserve_months": 6,
        "default_scenario": "base",
        "scenarios": {
            "base": {
                "expense_multiplier": 1.0,
                "income_multiplier": 1.0,
                "liquidity_haircuts": {"same_day": 0.0, "one_week": 0.02, "one_month": 0.05, "locked": 0.25},
            },
            "stress": {
                "expense_multiplier": 1.15,
                "income_multiplier": 0.75,
                "liquidity_haircuts": {"same_day": 0.0, "one_week": 0.05, "one_month": 0.12, "locked": 0.45},
            },
            "income_shock": {
                "expense_multiplier": 1.0,
                "income_multiplier": 0.25,
                "liquidity_haircuts": {"same_day": 0.0, "one_week": 0.03, "one_month": 0.08, "locked": 0.35},
            },
        },
    }


def _write_template_csvs(out_dir: Path) -> None:
    portfolio_rows = [
        {"name": item["name"], "value": item["value"], "liquidity_tier": item["liquidity_tier"], "annual_yield_rate": item["annual_yield_rate"], "annual_fee_rate": item["annual_fee_rate"]}
        for item in _template_portfolio()["assets"]
    ]
    ledger = _template_ledger()
    ledger_rows = [
        {"record_type": "settings", "monthly_income": ledger["monthly_income"], "monthly_expenses": ledger["monthly_expenses"], "month": "", "type": "", "label": "", "amount": ""}
    ]
    for event in ledger["scheduled_events"]:
        ledger_rows.append(
            {
                "record_type": "event",
                "monthly_income": "",
                "monthly_expenses": "",
                "month": event["month"],
                "type": event["type"],
                "label": event["label"],
                "amount": event["amount"],
            }
        )
    write_csv(portfolio_rows, out_dir / "portfolio.csv")
    write_csv(ledger_rows, out_dir / "ledger.csv")


def render_template_readme(manifest: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# Offline Starter Template Pack",
            "",
            f"> {manifest['boundary']}",
            "",
            "Use these files as clean local starters. Replace every value with your own offline records before review.",
            "",
            "## Files",
            "",
            "- `portfolio.csv` and `ledger.csv`: spreadsheet-friendly starters for `csv-import`.",
            "- `portfolio.json`, `ledger.json`, and `assumptions.json`: direct JSON starters for packet commands.",
            "- `template_manifest.json`: deterministic file inventory and hashes.",
            "",
            "## Replay",
            "",
            "```bash",
            "portfolio-liquidity-runway-lab input-lint --portfolio portfolio.json --ledger ledger.json --assumptions assumptions.json --portfolio-csv portfolio.csv --ledger-csv ledger.csv",
            "portfolio-liquidity-runway-lab build-packet --portfolio portfolio.json --ledger ledger.json --assumptions assumptions.json --scenario stress --out packet",
            "portfolio-liquidity-runway-lab csv-import --portfolio-csv portfolio.csv --ledger-csv ledger.csv --out csv-import",
            "```",
            "",
        ]
    )


def build_template_pack(out_dir: Path) -> TemplatePackPaths:
    out_dir.mkdir(parents=True, exist_ok=True)
    dump_json(_template_portfolio(), out_dir / "portfolio.json")
    dump_json(_template_ledger(), out_dir / "ledger.json")
    dump_json(_template_assumptions(), out_dir / "assumptions.json")
    _write_template_csvs(out_dir)
    files = []
    for path in sorted(out_dir.glob("*")):
        if path.is_file() and path.name not in {"README.md", "template_manifest.json"}:
            files.append({"path": path.name, "size_bytes": path.stat().st_size, "sha256": _sha256_file(path)})
    manifest = {"boundary": BOUNDARY_TEXT, "version": PROJECT_VERSION, "file_count": len(files), "files": files}
    readme_path = out_dir / "README.md"
    manifest_path = out_dir / "template_manifest.json"
    _deterministic_text_file(readme_path, render_template_readme(manifest))
    files.append({"path": "README.md", "size_bytes": readme_path.stat().st_size, "sha256": _sha256_file(readme_path)})
    files.sort(key=lambda item: item["path"])
    manifest = {"boundary": BOUNDARY_TEXT, "version": PROJECT_VERSION, "file_count": len(files), "files": files}
    dump_json(manifest, manifest_path)
    return TemplatePackPaths(out_dir, readme_path, manifest_path)


def _prepare_demo_portfolios(root: Path, target: Path) -> Path:
    target.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(bundled_example_path("portfolio"), target / "portfolio.json")
    shutil.copyfile(bundled_example_path("portfolio_concentrated"), target / "portfolio_concentrated.json")
    return target


def _generate_replay_artifacts(root: Path, generated_demo: Path) -> List[str]:
    generated_demo.mkdir(parents=True, exist_ok=True)
    portfolios = _prepare_demo_portfolios(root, generated_demo / "batch-inputs")
    build_scenario_gallery(bundled_example_path("portfolio"), bundled_example_path("ledger"), bundled_example_path("assumptions"), generated_demo / "scenario-gallery")
    build_assumption_audit(bundled_example_path("portfolio_concentrated"), bundled_example_path("ledger"), bundled_example_path("assumptions"), generated_demo / "assumption-audit")
    build_batch_compare(portfolios, bundled_example_path("ledger"), bundled_example_path("assumptions"), generated_demo / "batch-compare", ["base", "stress"])
    build_casebook(
        bundled_example_path("portfolio"),
        bundled_example_path("ledger"),
        bundled_example_path("assumptions"),
        portfolios,
        generated_demo / "casebook",
        "stress",
        ["base", "stress", "income_shock"],
    )
    build_schema_export(generated_demo / "schema-export")
    build_visual_receipt(bundled_example_path("portfolio"), bundled_example_path("ledger"), bundled_example_path("assumptions"), generated_demo / "visual_receipt.md", "stress")
    build_command_matrix(generated_demo / "command-matrix")
    replay_prefix = generated_demo.as_posix()
    for path in generated_demo.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".json", ".md", ".html"}:
            text = path.read_text(encoding="utf-8")
            path.write_text(text.replace(replay_prefix, "demo").replace('"portfolios_dir": "batch-inputs"', '"portfolios_dir": "demo/batch-inputs"'), encoding="utf-8")
    return [
        "scenario-gallery/scenario_gallery.json",
        "scenario-gallery/scenario_gallery.md",
        "scenario-gallery/scenario_gallery.html",
        "assumption-audit/assumption_audit.json",
        "assumption-audit/assumption_audit.md",
        "batch-compare/batch_compare.json",
        "batch-compare/batch_compare.md",
        "batch-compare/batch_compare.html",
        "casebook/casebook.json",
        "casebook/casebook.md",
        "casebook/casebook.html",
        "schema-export/schema_guide.json",
        "schema-export/schema_guide.md",
        "visual_receipt.md",
        "command-matrix/command_matrix.json",
        "command-matrix/command_matrix.md",
        "command-matrix/command_matrix.html",
    ]


def golden_replay(root: Path, replay_dir: Path) -> Dict[str, Any]:
    generated_demo = replay_dir / "demo"
    expected = _generate_replay_artifacts(root, generated_demo)
    comparisons = []
    for rel in expected:
        committed = root / "demo" / rel
        generated = generated_demo / rel
        committed_exists = committed.exists()
        generated_exists = generated.exists()
        committed_sha = _sha256_file(committed) if committed_exists else None
        generated_sha = _sha256_file(generated) if generated_exists else None
        content_match = committed_exists and generated_exists and committed.read_bytes() == generated.read_bytes()
        comparisons.append(
            {
                "path": f"demo/{rel}",
                "generated_path": (Path("replay") / "demo" / rel).as_posix(),
                "status": "pass" if content_match else "fail",
                "committed_exists": committed_exists,
                "generated_exists": generated_exists,
                "committed_sha256": committed_sha,
                "generated_sha256": generated_sha,
                "size_bytes_committed": committed.stat().st_size if committed_exists else None,
                "size_bytes_generated": generated.stat().st_size if generated_exists else None,
            }
        )
    status = "pass" if all(item["status"] == "pass" for item in comparisons) else "fail"
    return {
        "boundary": BOUNDARY_TEXT,
        "version": PROJECT_VERSION,
        "status": status,
        "root": _public_path(root, root),
        "replay_dir": _public_path(replay_dir, root),
        "artifact_count": len(comparisons),
        "pass_count": sum(1 for item in comparisons if item["status"] == "pass"),
        "fail_count": sum(1 for item in comparisons if item["status"] == "fail"),
        "comparisons": comparisons,
    }


def render_golden_replay_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# Golden Replay",
        "",
        f"> {report['boundary']}",
        "",
        f"Version: `{report['version']}`",
        f"Status: `{report['status']}`",
        f"Compared artifacts: {report['artifact_count']}",
        f"Passed: {report['pass_count']}",
        f"Failed: {report['fail_count']}",
        "",
        "| Artifact | Status | Committed SHA256 | Generated SHA256 | Committed bytes | Generated bytes |",
        "| --- | --- | --- | --- | ---: | ---: |",
    ]
    for item in report["comparisons"]:
        lines.append(
            f"| `{item['path']}` | `{item['status']}` | `{item['committed_sha256'] or ''}` | "
            f"`{item['generated_sha256'] or ''}` | {item['size_bytes_committed'] or ''} | {item['size_bytes_generated'] or ''} |"
        )
    lines.append("")
    return "\n".join(lines)


def build_golden_replay(root: Path, out_dir: Path, replay_dir: Optional[Path] = None) -> GoldenReplayPaths:
    out_dir.mkdir(parents=True, exist_ok=True)
    temp_replay: Optional[tempfile.TemporaryDirectory[str]] = None
    if replay_dir is None:
        temp_replay = tempfile.TemporaryDirectory(prefix="plrl-golden-replay-")
        actual_replay = Path(temp_replay.name)
    else:
        actual_replay = replay_dir
        if actual_replay.exists():
            shutil.rmtree(actual_replay)
        actual_replay.mkdir(parents=True, exist_ok=True)
    try:
        report = golden_replay(root, actual_replay)
        if temp_replay is not None:
            report["replay_dir"] = "temporary"
    finally:
        if temp_replay is not None:
            temp_replay.cleanup()
    json_path = out_dir / "golden_replay.json"
    markdown_path = out_dir / "golden_replay.md"
    dump_json(report, json_path)
    markdown_path.write_text(render_golden_replay_markdown(report), encoding="utf-8")
    return GoldenReplayPaths(out_dir, json_path, markdown_path)


def release_deck(root: Path) -> Dict[str, Any]:
    matrix = command_matrix_data()
    release = release_check(root)
    maturity = maturity_report(root)
    catalog = artifact_catalog(root, ["demo", "docs"])
    return {
        "boundary": BOUNDARY_TEXT,
        "version": PROJECT_VERSION,
        "title": f"Portfolio Liquidity Runway Lab v{PROJECT_VERSION} Release Deck",
        "product_value": [
            "Builds deterministic local liquidity runway packets from JSON and CSV inputs.",
            "Imports portfolio and ledger CSV rows into validated JSON schemas, then exports packet analysis back to reviewable CSV.",
            "Packages scenario, audit, batch comparison, casebook, schema, command, and replay evidence.",
            "Adds deterministic checksums, offline evidence bundles, and starter template packs for reproducible review.",
            "Keeps outputs static and reviewable with no runtime dependencies and no JavaScript in generated HTML demos.",
        ],
        "commands": [{"command": item["command"], "purpose": item["purpose"]} for item in matrix],
        "evidence": {
            "release_check_status": release["status"],
            "maturity_score": maturity["score"],
            "maturity_total": len(maturity["checks"]),
            "artifact_count": catalog["artifact_count"],
            "html_files": release["html_files"],
        },
        "risks": [
            "Outputs depend on supplied local JSON quality and should be reviewed against source records.",
            "Static scenarios are assumptions, not predictions or transaction instructions.",
            "No live integrations means users must update inputs manually before each review.",
        ],
        "next_roadmap": [
            "Expand fixture doctor coverage for malformed archive bundles and scenario edge cases.",
            "Add optional detached signature support for checksum manifests.",
            "Broaden CSV templates for multi-currency review workflows without adding live integrations.",
        ],
    }


def render_release_deck_markdown(deck: Mapping[str, Any]) -> str:
    lines = [
        f"# {deck['title']}",
        "",
        f"> {deck['boundary']}",
        "",
        "## Product Value",
        "",
    ]
    lines.extend(f"- {item}" for item in deck["product_value"])
    lines.extend(["", "## Commands", "", "| Command | Purpose |", "| --- | --- |"])
    for item in deck["commands"]:
        lines.append(f"| `{item['command']}` | {item['purpose']} |")
    lines.extend(
        [
            "",
            "## Evidence",
            "",
            f"- Release check: `{deck['evidence']['release_check_status']}`",
            f"- Maturity score: `{deck['evidence']['maturity_score']}/{deck['evidence']['maturity_total']}`",
            f"- Cataloged artifacts: `{deck['evidence']['artifact_count']}`",
            f"- No-script HTML files: `{len(deck['evidence']['html_files'])}`",
            "",
            "## Risks",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in deck["risks"])
    lines.extend(["", "## Next Roadmap", ""])
    lines.extend(f"- {item}" for item in deck["next_roadmap"])
    lines.append("")
    return "\n".join(lines)


def render_release_deck_html(deck: Mapping[str, Any]) -> str:
    md = render_release_deck_markdown(deck)
    body = []
    in_list = False
    in_table = False
    for line in md.splitlines():
        if line.startswith("# "):
            body.append(f"<h1>{html.escape(line[2:])}</h1>")
        elif line.startswith("## "):
            if in_list:
                body.append("</ul>")
                in_list = False
            if in_table:
                body.append("</table>")
                in_table = False
            body.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("> "):
            body.append(f"<blockquote>{html.escape(line[2:])}</blockquote>")
        elif line.startswith("- "):
            if not in_list:
                body.append("<ul>")
                in_list = True
            body.append(f"<li>{html.escape(line[2:])}</li>")
        elif line.startswith("| `"):
            if not in_table:
                body.append("<table>")
                in_table = True
            cells = [cell.strip().strip("`") for cell in line.strip("|").split("|")]
            body.append("<tr>" + "".join(f"<td>{html.escape(cell)}</td>" for cell in cells) + "</tr>")
        elif line.startswith("| ---"):
            continue
        elif line.strip():
            body.append(f"<p>{html.escape(line)}</p>")
    if in_list:
        body.append("</ul>")
    if in_table:
        body.append("</table>")
    return _html_shell(str(deck["title"]), "\n".join(body))


def build_release_deck(root: Path, out_dir: Path) -> ReleaseDeckPaths:
    deck = release_deck(root)
    out_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = out_dir / "release_deck.md"
    html_path = out_dir / "release_deck.html"
    markdown_path.write_text(render_release_deck_markdown(deck), encoding="utf-8")
    html_path.write_text(render_release_deck_html(deck), encoding="utf-8")
    return ReleaseDeckPaths(out_dir, markdown_path, html_path)


def artifact_catalog(root: Path, paths: Iterable[str] = ("demo", "docs")) -> Dict[str, Any]:
    entries = []
    for part in paths:
        base = root / part
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            rel_path = path.relative_to(root)
            if path.is_file() and not _is_ignored_release_path(rel_path):
                rel = rel_path.as_posix()
                if rel in {"docs/artifact_catalog.json", "docs/artifact_catalog.md"}:
                    continue
                entries.append(
                    {
                        "path": rel,
                        "size_bytes": path.stat().st_size,
                        "sha256": _sha256_file(path),
                        "regeneration_command": _regeneration_command_for(rel),
                    }
                )
    return {"boundary": BOUNDARY_TEXT, "root": _public_path(root, root), "artifact_count": len(entries), "artifacts": entries}


def _regeneration_command_for(rel: str) -> str:
    if rel.startswith("demo/casebook/"):
        return "portfolio-liquidity-runway-lab casebook --out demo/casebook"
    if rel.startswith("demo/scenario-gallery/"):
        return "portfolio-liquidity-runway-lab scenario-gallery --out demo/scenario-gallery"
    if rel.startswith("demo/assumption-audit/"):
        return (
            "portfolio-liquidity-runway-lab assumption-audit "
            "--portfolio portfolio_liquidity_runway_lab/examples/portfolio_concentrated.json --out demo/assumption-audit"
        )
    if rel.startswith("demo/batch-compare/"):
        return "portfolio-liquidity-runway-lab batch-compare --portfolios-dir demo/batch-inputs --scenarios base,stress --out demo/batch-compare"
    if rel.startswith("demo/schema-export/") or rel.startswith("docs/schema_guide."):
        return "portfolio-liquidity-runway-lab schema-export --out demo/schema-export"
    if rel.startswith("demo/csv-import/"):
        return "portfolio-liquidity-runway-lab csv-import --out demo/csv-import"
    if rel.startswith("demo/csv-export/"):
        return "portfolio-liquidity-runway-lab csv-export --packet demo/csv-export-packet/liquidity_packet.json --out demo/csv-export"
    if rel.startswith("demo/bundle-checksums/") or rel.startswith("docs/bundle-checksums/"):
        return "portfolio-liquidity-runway-lab bundle-checksums --root . --out docs/bundle-checksums"
    if rel.startswith("demo/evidence-bundle/") or rel.startswith("docs/evidence-bundle/"):
        return "portfolio-liquidity-runway-lab evidence-bundle --root . --out docs/evidence-bundle"
    if rel.startswith("demo/template-pack/") or rel.startswith("docs/template-pack/"):
        return "portfolio-liquidity-runway-lab template-pack --out docs/template-pack"
    if rel.startswith("demo/fixture-doctor/") or rel.startswith("docs/fixture_doctor."):
        return "portfolio-liquidity-runway-lab fixture-doctor --out demo/fixture-doctor"
    if rel.startswith("demo/static-docs/") or rel.startswith("docs/static-docs/"):
        return "portfolio-liquidity-runway-lab docs-export --out demo/static-docs"
    if rel.startswith("demo/command-matrix/") or rel.startswith("docs/command-matrix/"):
        return "portfolio-liquidity-runway-lab command-matrix --out demo/command-matrix"
    if rel.startswith("demo/golden-replay/") or rel.startswith("docs/golden-replay/"):
        return "portfolio-liquidity-runway-lab golden-replay --out demo/golden-replay"
    if rel.startswith("demo/release-deck/") or rel.startswith("docs/release-deck/"):
        return "portfolio-liquidity-runway-lab release-deck --out demo/release-deck"
    if rel == "demo/visual_receipt.md":
        return "portfolio-liquidity-runway-lab visual-receipt --out demo/visual_receipt.md --scenario stress"
    if rel == "docs/release_manifest.json":
        return "portfolio-liquidity-runway-lab release-manifest --out docs/release_manifest.json"
    if rel == "docs/maturity_report.json":
        return "portfolio-liquidity-runway-lab maturity-report --out docs/maturity_report.json"
    if rel.startswith("docs/release_check."):
        return "portfolio-liquidity-runway-lab release-check --out docs"
    if rel.startswith("docs/artifact_catalog."):
        return "portfolio-liquidity-runway-lab artifact-catalog --out docs"
    return "manual edit"


def render_artifact_catalog_markdown(catalog: Mapping[str, Any]) -> str:
    lines = [
        "# Artifact Catalog",
        "",
        f"> {catalog['boundary']}",
        "",
        f"Artifact count: {catalog['artifact_count']}",
        "",
        "| Path | Size bytes | SHA256 | Regeneration command |",
        "| --- | ---: | --- | --- |",
    ]
    for item in catalog["artifacts"]:
        lines.append(f"| `{item['path']}` | {item['size_bytes']} | `{item['sha256']}` | `{item['regeneration_command']}` |")
    lines.append("")
    return "\n".join(lines)


def build_artifact_catalog(root: Path, out_dir: Path, paths: Iterable[str] = ("demo", "docs")) -> CatalogPaths:
    catalog = artifact_catalog(root, paths)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "artifact_catalog.json"
    markdown_path = out_dir / "artifact_catalog.md"
    dump_json(catalog, json_path)
    markdown_path.write_text(render_artifact_catalog_markdown(catalog), encoding="utf-8")
    return CatalogPaths(out_dir, json_path, markdown_path)


def release_check(root: Path, expected_files: Iterable[str] = EXPECTED_RELEASE_FILES) -> Dict[str, Any]:
    missing = [rel for rel in expected_files if not (root / rel).is_file()]
    html_files = sorted(
        path.relative_to(root).as_posix()
        for base in (root / "demo", root / "docs")
        if base.exists()
        for path in base.rglob("*.html")
        if path.is_file()
    )
    html_safety_findings = []
    for rel in html_files:
        for code in _html_safety_findings(root / rel):
            html_safety_findings.append({"path": rel, "code": code})
    html_with_script = [item["path"] for item in html_safety_findings if item["code"] == "script_tag"]
    scan = public_scan(root)
    checks = {
        "expected_files": not missing,
        "public_scan": scan["status"] == "pass",
        "html_no_script_tags": not html_with_script,
        "html_static_safe": not html_safety_findings,
    }
    status = "pass" if all(checks.values()) else "fail"
    return {
        "boundary": BOUNDARY_TEXT,
        "status": status,
        "checks": checks,
        "missing_files": missing,
        "html_files": html_files,
        "html_with_script_tags": html_with_script,
        "html_safety_findings": html_safety_findings,
        "public_scan_findings": scan["findings"],
    }


def render_release_check_markdown(result: Mapping[str, Any]) -> str:
    lines = [
        "# Release Check",
        "",
        f"> {result['boundary']}",
        "",
        f"Status: `{result['status']}`",
        "",
        "## Checks",
        "",
        "| Check | Pass |",
        "| --- | --- |",
    ]
    for key in sorted(result["checks"]):
        lines.append(f"| {key} | {str(result['checks'][key]).lower()} |")
    lines.extend(["", "## Missing Files", ""])
    lines.extend(f"- `{rel}`" for rel in result["missing_files"]) if result["missing_files"] else lines.append("- None")
    lines.extend(["", "## HTML Safety Findings", ""])
    lines.extend(f"- `{item['path']}`: {item['code']}" for item in result.get("html_safety_findings", [])) if result.get("html_safety_findings") else lines.append("- None")
    lines.extend(["", "## HTML Script Tag Findings", ""])
    lines.extend(f"- `{rel}`" for rel in result["html_with_script_tags"]) if result["html_with_script_tags"] else lines.append("- None")
    lines.extend(["", "## Public Scan Findings", ""])
    lines.extend(f"- {finding}" for finding in result["public_scan_findings"]) if result["public_scan_findings"] else lines.append("- None")
    lines.append("")
    return "\n".join(lines)


def build_release_check(root: Path, out_dir: Path, expected_files: Iterable[str] = EXPECTED_RELEASE_FILES) -> ReleaseCheckPaths:
    result = release_check(root, expected_files)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "release_check.json"
    markdown_path = out_dir / "release_check.md"
    dump_json(result, json_path)
    markdown_path.write_text(render_release_check_markdown(result), encoding="utf-8")
    return ReleaseCheckPaths(out_dir, json_path, markdown_path)


def compare_history(history: Mapping[str, Any]) -> Dict[str, Any]:
    snapshots = history.get("snapshots", [])
    if not isinstance(snapshots, list) or len(snapshots) < 2:
        raise ValueError("history.snapshots must contain at least two snapshots")
    rows = []
    previous = None
    for snap in snapshots:
        if not isinstance(snap, dict):
            raise ValueError("each snapshot must be an object")
        current = {
            "label": str(snap.get("label", "")),
            "same_day_reserve_months": _as_number(snap.get("same_day_reserve_months", 0), "same_day_reserve_months"),
            "effective_monthly_burn": _as_number(snap.get("effective_monthly_burn", 0), "effective_monthly_burn"),
        }
        if previous:
            rows.append(
                {
                    "from": previous["label"],
                    "to": current["label"],
                    "reserve_month_delta": round(current["same_day_reserve_months"] - previous["same_day_reserve_months"], 2),
                    "monthly_burn_delta": round(current["effective_monthly_burn"] - previous["effective_monthly_burn"], 2),
                }
            )
        previous = current
    return {"boundary": BOUNDARY_TEXT, "comparisons": rows}


def review_ledger(ledger: Mapping[str, Any]) -> Dict[str, Any]:
    monthly_income = _as_number(ledger.get("monthly_income", 0), "monthly_income")
    monthly_expenses = _as_number(ledger.get("monthly_expenses", 0), "monthly_expenses")
    events = ledger.get("scheduled_events", [])
    prompts = [
        "Verify recurring income and expense values against local records.",
        "Confirm one-time events are still expected and not duplicated.",
        "Flag any missing insurance, tax, rent, debt, or subscription outflows.",
    ]
    flags = []
    if monthly_expenses <= 0:
        flags.append("Monthly expenses are zero or negative; review input completeness.")
    if monthly_income > monthly_expenses * 2 and monthly_expenses > 0:
        flags.append("Income is more than double expenses; verify whether gross and net values are mixed.")
    for event in events if isinstance(events, list) else []:
        amount = _as_number(event.get("amount", 0), "event.amount")
        if amount > monthly_expenses * 3 and monthly_expenses > 0:
            flags.append(f"Large scheduled {event.get('type', 'event')} in month {event.get('month')}: {event.get('label', 'unlabeled')}.")
    return {"boundary": BOUNDARY_TEXT, "ledger_flags": flags, "review_prompts": prompts}


def public_scan(root: Path) -> Dict[str, Any]:
    findings: List[str] = []
    root_prefix = root.resolve().as_posix()
    for path in sorted(root.rglob("*")):
        rel_path = path.relative_to(root)
        if _is_ignored_release_path(rel_path):
            continue
        if path.is_dir():
            continue
        rel = rel_path.as_posix()
        if rel.startswith(".github/workflows/"):
            findings.append(f"Forbidden workflow file: {rel}")
        if path.suffix.lower() in {".pyc", ".pyo", ".so", ".dll", ".dylib"}:
            findings.append(f"Generated or binary-like artifact: {rel}")
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            findings.append(f"Non-text file should be reviewed before public release: {rel}")
            continue
        lowered = text.lower()
        for term in FORBIDDEN_PUBLIC_TERMS:
            if re.search(rf"(?im)^\s*{re.escape(term)}\s*[:=]\s*\S{{8,}}", lowered):
                findings.append(f"Potential secret marker {term!r} in {rel}")
        for code, pattern in PUBLIC_PATH_LEAK_PATTERNS:
            if pattern.search(text):
                findings.append(f"Potential path leakage [{code}] in {rel}")
        if root_prefix != "/" and root_prefix in text:
            findings.append(f"Potential path leakage [scan_root_path] in {rel}")
        for code, pattern in PROVIDER_TOKEN_PATTERNS:
            if pattern.search(text):
                findings.append(f"Potential provider token [{code}] in {rel}")
        if ENV_SECRET_LABEL_PATTERN.search(text):
            findings.append(f"Potential environment secret assignment in {rel}")
        if AUTH_HEADER_PATTERN.search(text):
            findings.append(f"Potential bearer authorization header in {rel}")
        if path.suffix.lower() in {".html", ".htm"}:
            for code in _html_safety_findings(path):
                findings.append(f"Unsafe HTML [{code}] in {rel}")
    return {"boundary": BOUNDARY_TEXT, "status": "pass" if not findings else "review", "findings": findings}


def release_manifest(root: Path) -> Dict[str, Any]:
    files = []
    for path in sorted(root.rglob("*")):
        rel_path = path.relative_to(root)
        if path.is_file() and not _is_ignored_release_path(rel_path):
            files.append(path.relative_to(root).as_posix())
    return {
        "name": "portfolio-liquidity-runway-lab",
        "version": PROJECT_VERSION,
        "boundary": BOUNDARY_TEXT,
        "files": files,
        "console_script": "portfolio-liquidity-runway-lab",
        "runtime_dependencies": [],
    }


def maturity_report(root: Path) -> Dict[str, Any]:
    checks = {
        "readme": (root / "README.md").exists(),
        "readme_quickstart": "quickstart" in (root / "README.md").read_text(encoding="utf-8").lower()
        if (root / "README.md").exists()
        else False,
        "readme_boundary": "does not fetch live data" in (root / "README.md").read_text(encoding="utf-8").lower()
        if (root / "README.md").exists()
        else False,
        "license": (root / "LICENSE").exists(),
        "pyproject": (root / "pyproject.toml").exists(),
        "cold_start_walkthrough": (root / "docs/cold_start_walkthrough.md").exists(),
        "release_readiness_review": (root / "docs/release_readiness_review.md").exists(),
        "release_manifest": (root / "docs/release_manifest.json").exists(),
        "artifact_catalog": (root / "docs/artifact_catalog.json").exists() and (root / "docs/artifact_catalog.md").exists(),
        "release_check": (root / "docs/release_check.json").exists() and (root / "docs/release_check.md").exists(),
        "schema_guide": (root / "docs/schema_guide.json").exists() and (root / "docs/schema_guide.md").exists(),
        "fixture_doctor": (root / "docs/fixture_doctor.json").exists() and (root / "docs/fixture_doctor.md").exists(),
        "static_docs": (root / "docs/static-docs/index.html").exists() and (root / "docs/static-docs/index.md").exists(),
        "demo_casebook": (root / "demo/casebook/casebook.html").exists(),
        "demo_scenario_gallery": (root / "demo/scenario-gallery/scenario_gallery.md").exists(),
        "demo_assumption_audit": (root / "demo/assumption-audit/assumption_audit.md").exists(),
        "demo_batch_compare": (root / "demo/batch-compare/batch_compare.html").exists(),
        "demo_schema_export": (root / "demo/schema-export/schema_guide.md").exists(),
        "demo_csv_import": (root / "demo/csv-import/import_report.md").exists(),
        "demo_csv_export": (root / "demo/csv-export/export_manifest.md").exists(),
        "demo_bundle_checksums": (root / "demo/bundle-checksums/SHA256SUMS.txt").exists(),
        "demo_evidence_bundle": (root / "demo/evidence-bundle/index.html").exists(),
        "demo_template_pack": (root / "demo/template-pack/template_manifest.json").exists(),
        "demo_fixture_doctor": (root / "demo/fixture-doctor/fixture_doctor.md").exists(),
        "demo_static_docs": (root / "demo/static-docs/index.html").exists(),
        "demo_command_matrix": (root / "demo/command-matrix/command_matrix.html").exists(),
        "demo_golden_replay": (root / "demo/golden-replay/golden_replay.md").exists(),
        "demo_release_deck": (root / "demo/release-deck/release_deck.html").exists(),
        "command_matrix": (root / "docs/command-matrix/command_matrix.html").exists(),
        "golden_replay": (root / "docs/golden-replay/golden_replay.md").exists(),
        "release_deck": (root / "docs/release-deck/release_deck.html").exists(),
        "bundle_checksums": (root / "docs/bundle-checksums/SHA256SUMS.txt").exists() and (root / "docs/bundle-checksums/bundle_manifest.json").exists(),
        "evidence_bundle": (root / "docs/evidence-bundle/index.html").exists() and (root / "docs/evidence-bundle/SHA256SUMS.txt").exists(),
        "template_pack": (root / "docs/template-pack/README.md").exists() and (root / "docs/template-pack/template_manifest.json").exists(),
        "demo_visual_receipt": (root / "demo/visual_receipt.md").exists(),
        "tests": (root / "tests").exists(),
        "agent_skill": (root / "skills/agent/portfolio-liquidity-runway-lab/SKILL.md").exists(),
        "no_github_workflows": not (root / ".github/workflows").exists(),
    }
    return {"boundary": BOUNDARY_TEXT, "score": sum(1 for value in checks.values() if value), "checks": checks}


def harden_csv_cell(value: Any) -> Any:
    if isinstance(value, str) and value.startswith(CSV_FORMULA_PREFIXES):
        return "'" + value
    return value


def write_csv(rows: List[Mapping[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: harden_csv_cell(value) for key, value in row.items()})
