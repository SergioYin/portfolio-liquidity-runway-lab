from __future__ import annotations

import csv
import hashlib
import html
import json
import shutil
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
    "docs/cold_start_walkthrough.md",
    "docs/release_readiness_review.md",
    "docs/release_manifest.json",
    "docs/maturity_report.json",
    "docs/artifact_catalog.json",
    "docs/artifact_catalog.md",
    "docs/schema_guide.json",
    "docs/schema_guide.md",
    "docs/fixture_doctor.json",
    "docs/fixture_doctor.md",
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
    receipt_command = f"portfolio-liquidity-runway-lab visual-receipt --out {out_path.as_posix()}{scenario_part}"
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


def _contains_script_tag(path: Path) -> bool:
    try:
        return "<script" in path.read_text(encoding="utf-8").lower()
    except UnicodeDecodeError:
        return False


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
            "portfolio": portfolio_path.as_posix(),
            "ledger": ledger_path.as_posix(),
            "assumptions": assumptions_path.as_posix(),
            "portfolios_dir": portfolios_dir.as_posix(),
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
    ]
    command_matrix = command_matrix_data()
    return {
        "boundary": BOUNDARY_TEXT,
        "version": "0.5.0",
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
    return [
        {"command": "build-packet", "inputs": ["portfolio.json", "ledger.json", "assumptions.json"], "outputs": ["liquidity_packet.json", "liquidity_packet.md", "liquidity_packet.html"], "no_script_html": True},
        {"command": "compare-history", "inputs": ["history.json"], "outputs": ["stdout JSON", "optional JSON file"], "no_script_html": False},
        {"command": "review-ledger", "inputs": ["ledger.json"], "outputs": ["stdout JSON", "optional JSON file"], "no_script_html": False},
        {"command": "static-dashboard", "inputs": ["portfolio.json", "ledger.json", "assumptions.json"], "outputs": ["liquidity_packet.html"], "no_script_html": True},
        {"command": "scenario-gallery", "inputs": ["portfolio.json", "ledger.json", "assumptions.json"], "outputs": ["scenario_gallery.json", "scenario_gallery.md", "scenario_gallery.html"], "no_script_html": True},
        {"command": "assumption-audit", "inputs": ["portfolio.json", "ledger.json", "assumptions.json"], "outputs": ["assumption_audit.json", "assumption_audit.md"], "no_script_html": False},
        {"command": "batch-compare", "inputs": ["portfolio directory", "ledger.json", "assumptions.json"], "outputs": ["batch_compare.json", "batch_compare.md", "batch_compare.html"], "no_script_html": True},
        {"command": "casebook", "inputs": ["portfolio.json", "portfolio directory", "ledger.json", "assumptions.json"], "outputs": ["casebook.json", "casebook.md", "casebook.html"], "no_script_html": True},
        {"command": "artifact-catalog", "inputs": ["repo or output root"], "outputs": ["artifact_catalog.json", "artifact_catalog.md"], "no_script_html": False},
        {"command": "release-check", "inputs": ["repo root"], "outputs": ["release_check.json", "release_check.md"], "no_script_html": False},
        {"command": "visual-receipt", "inputs": ["portfolio.json", "ledger.json", "assumptions.json"], "outputs": ["visual_receipt.md"], "no_script_html": False},
        {"command": "quickstart-check", "inputs": ["bundled examples"], "outputs": ["copied examples", "packet artifacts"], "no_script_html": True},
        {"command": "selfcheck", "inputs": ["bundled examples"], "outputs": ["stdout JSON"], "no_script_html": True},
        {"command": "public-scan", "inputs": ["repo root"], "outputs": ["stdout JSON", "optional JSON file"], "no_script_html": False},
        {"command": "release-manifest", "inputs": ["repo root"], "outputs": ["stdout JSON", "optional JSON file"], "no_script_html": False},
        {"command": "maturity-report", "inputs": ["repo root"], "outputs": ["stdout JSON", "optional JSON file"], "no_script_html": False},
        {"command": "schema-export", "inputs": ["built-in schema metadata"], "outputs": ["schema_guide.json", "schema_guide.md"], "no_script_html": False},
        {"command": "fixture-doctor", "inputs": ["bundled or supplied examples"], "outputs": ["fixture_doctor.json", "fixture_doctor.md"], "no_script_html": True},
        {"command": "docs-export", "inputs": ["README and generated release evidence"], "outputs": ["static-docs/index.html", "static-docs/index.md", "static-docs/*.md"], "no_script_html": True},
    ]


def _copy_example_set(target: Path, source: Optional[Path] = None) -> Dict[str, str]:
    target.mkdir(parents=True, exist_ok=True)
    copied = {}
    for name in ("portfolio.json", "portfolio_concentrated.json", "ledger.json", "assumptions.json", "history.json"):
        src = source / name if source else bundled_example_path(name)
        dst = target / name
        shutil.copyfile(src, dst)
        copied[name] = dst.as_posix()
    return copied


def fixture_doctor(work_dir: Path, examples_dir: Optional[Path] = None) -> Dict[str, Any]:
    examples = work_dir / "examples"
    copied = _copy_example_set(examples, examples_dir)
    portfolios_dir = work_dir / "portfolios"
    portfolios_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(examples / "portfolio.json", portfolios_dir / "portfolio.json")
    shutil.copyfile(examples / "portfolio_concentrated.json", portfolios_dir / "portfolio_concentrated.json")

    plan = [
        {"command": "build-packet", "argv": ["build-packet", "--portfolio", copied["portfolio.json"], "--ledger", copied["ledger.json"], "--assumptions", copied["assumptions.json"], "--scenario", "stress", "--out", (work_dir / "packet").as_posix()]},
        {"command": "static-dashboard", "argv": ["static-dashboard", "--portfolio", copied["portfolio.json"], "--ledger", copied["ledger.json"], "--assumptions", copied["assumptions.json"], "--out", (work_dir / "dashboard").as_posix()]},
        {"command": "scenario-gallery", "argv": ["scenario-gallery", "--portfolio", copied["portfolio.json"], "--ledger", copied["ledger.json"], "--assumptions", copied["assumptions.json"], "--out", (work_dir / "scenario-gallery").as_posix()]},
        {"command": "assumption-audit", "argv": ["assumption-audit", "--portfolio", copied["portfolio_concentrated.json"], "--ledger", copied["ledger.json"], "--assumptions", copied["assumptions.json"], "--out", (work_dir / "assumption-audit").as_posix()]},
        {"command": "batch-compare", "argv": ["batch-compare", "--portfolios-dir", portfolios_dir.as_posix(), "--ledger", copied["ledger.json"], "--assumptions", copied["assumptions.json"], "--scenarios", "base,stress", "--out", (work_dir / "batch-compare").as_posix()]},
        {"command": "casebook", "argv": ["casebook", "--portfolio", copied["portfolio.json"], "--ledger", copied["ledger.json"], "--assumptions", copied["assumptions.json"], "--portfolios-dir", portfolios_dir.as_posix(), "--scenario", "stress", "--scenarios", "base,stress,income_shock", "--out", (work_dir / "casebook").as_posix()]},
        {"command": "visual-receipt", "argv": ["visual-receipt", "--portfolio", copied["portfolio.json"], "--ledger", copied["ledger.json"], "--assumptions", copied["assumptions.json"], "--scenario", "stress", "--out", (work_dir / "visual_receipt.md").as_posix()]},
        {"command": "compare-history", "argv": ["compare-history", "--history", copied["history.json"], "--out", (work_dir / "history_compare.json").as_posix()]},
        {"command": "review-ledger", "argv": ["review-ledger", "--ledger", copied["ledger.json"], "--out", (work_dir / "ledger_review.json").as_posix()]},
        {"command": "schema-export", "argv": ["schema-export", "--out", (work_dir / "schema-export").as_posix()]},
        {"command": "docs-export", "argv": ["docs-export", "--root", work_dir.as_posix(), "--out", (work_dir / "static-docs").as_posix()]},
        {"command": "artifact-catalog", "argv": ["artifact-catalog", "--root", work_dir.as_posix(), "--paths", "packet,dashboard,scenario-gallery,assumption-audit,batch-compare,casebook,schema-export,static-docs", "--out", (work_dir / "catalog").as_posix()]},
        {"command": "release-check", "argv": ["release-check", "--root", work_dir.as_posix(), "--out", (work_dir / "release-check").as_posix()]},
        {"command": "public-scan", "argv": ["public-scan", "--root", work_dir.as_posix(), "--out", (work_dir / "public_scan.json").as_posix()]},
        {"command": "release-manifest", "argv": ["release-manifest", "--root", work_dir.as_posix(), "--out", (work_dir / "release_manifest.json").as_posix()]},
        {"command": "maturity-report", "argv": ["maturity-report", "--root", work_dir.as_posix(), "--out", (work_dir / "maturity_report.json").as_posix()]},
    ]

    results = []
    for item in plan:
        command = item["command"]
        try:
            if command in {"build-packet", "static-dashboard"}:
                paths = build_packet(examples / "portfolio.json", examples / "ledger.json", examples / "assumptions.json", Path(item["argv"][-1]), "stress" if command == "build-packet" else None)
                output_paths = [paths.json_path.as_posix(), paths.markdown_path.as_posix(), paths.html_path.as_posix()]
                passed = paths.html_path.exists() and not _contains_script_tag(paths.html_path)
            elif command == "scenario-gallery":
                paths = build_scenario_gallery(examples / "portfolio.json", examples / "ledger.json", examples / "assumptions.json", Path(item["argv"][-1]))
                output_paths = [paths.json_path.as_posix(), paths.markdown_path.as_posix(), paths.html_path.as_posix()]
                passed = not _contains_script_tag(paths.html_path)
            elif command == "assumption-audit":
                paths = build_assumption_audit(examples / "portfolio_concentrated.json", examples / "ledger.json", examples / "assumptions.json", Path(item["argv"][-1]))
                output_paths = [paths.json_path.as_posix(), paths.markdown_path.as_posix()]
                passed = paths.json_path.exists() and paths.markdown_path.exists()
            elif command == "batch-compare":
                paths = build_batch_compare(portfolios_dir, examples / "ledger.json", examples / "assumptions.json", Path(item["argv"][-1]), ["base", "stress"])
                output_paths = [paths.json_path.as_posix(), paths.markdown_path.as_posix(), paths.html_path.as_posix()]
                passed = not _contains_script_tag(paths.html_path)
            elif command == "casebook":
                paths = build_casebook(examples / "portfolio.json", examples / "ledger.json", examples / "assumptions.json", portfolios_dir, Path(item["argv"][-1]), "stress", ["base", "stress", "income_shock"])
                output_paths = [paths.json_path.as_posix(), paths.markdown_path.as_posix(), paths.html_path.as_posix()]
                passed = not _contains_script_tag(paths.html_path)
            elif command == "visual-receipt":
                path = build_visual_receipt(examples / "portfolio.json", examples / "ledger.json", examples / "assumptions.json", work_dir / "visual_receipt.md", "stress")
                output_paths = [path.as_posix()]
                passed = path.exists()
            elif command == "compare-history":
                out = work_dir / "history_compare.json"
                dump_json(compare_history(load_json(examples / "history.json")), out)
                output_paths = [out.as_posix()]
                passed = out.exists()
            elif command == "review-ledger":
                out = work_dir / "ledger_review.json"
                dump_json(review_ledger(load_json(examples / "ledger.json")), out)
                output_paths = [out.as_posix()]
                passed = out.exists()
            elif command == "schema-export":
                paths = build_schema_export(work_dir / "schema-export")
                output_paths = [paths.json_path.as_posix(), paths.markdown_path.as_posix()]
                passed = paths.json_path.exists() and paths.markdown_path.exists()
            elif command == "docs-export":
                paths = build_docs_export(work_dir, work_dir / "static-docs")
                output_paths = [paths.index_html_path.as_posix(), paths.index_markdown_path.as_posix()]
                passed = paths.index_html_path.exists() and not _contains_script_tag(paths.index_html_path)
            elif command == "artifact-catalog":
                paths = build_artifact_catalog(work_dir, work_dir / "catalog", ["packet", "dashboard", "scenario-gallery", "assumption-audit", "batch-compare", "casebook", "schema-export", "static-docs"])
                output_paths = [paths.json_path.as_posix(), paths.markdown_path.as_posix()]
                passed = load_json(paths.json_path)["artifact_count"] > 0
            elif command == "release-check":
                paths = build_release_check(work_dir, work_dir / "release-check", ["examples/portfolio.json", "examples/ledger.json", "packet/liquidity_packet.html"])
                output_paths = [paths.json_path.as_posix(), paths.markdown_path.as_posix()]
                passed = load_json(paths.json_path)["checks"]["html_no_script_tags"]
            elif command == "public-scan":
                out = work_dir / "public_scan.json"
                result = public_scan(work_dir)
                dump_json(result, out)
                output_paths = [out.as_posix()]
                passed = result["status"] == "pass"
            elif command == "release-manifest":
                out = work_dir / "release_manifest.json"
                dump_json(release_manifest(work_dir), out)
                output_paths = [out.as_posix()]
                passed = out.exists()
            elif command == "maturity-report":
                out = work_dir / "maturity_report.json"
                dump_json(maturity_report(work_dir), out)
                output_paths = [out.as_posix()]
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
        "work_dir": work_dir.as_posix(),
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
    actual_work = work_dir or (out_dir / "work")
    actual_work.mkdir(parents=True, exist_ok=True)
    report = fixture_doctor(actual_work, examples_dir)
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
    lines = ["# Command Matrix", "", "| Command | Inputs | Outputs | Static no-JS HTML |", "| --- | --- | --- | --- |"]
    for item in command_matrix_data():
        lines.append(f"| `{item['command']}` | {', '.join(item['inputs']) or 'none'} | {', '.join(item['outputs']) or 'stdout'} | {str(item['no_script_html']).lower()} |")
    lines.append("")
    return "\n".join(lines)


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
    return {"boundary": BOUNDARY_TEXT, "root": root.as_posix(), "artifact_count": len(entries), "artifacts": entries}


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
    if rel.startswith("demo/fixture-doctor/") or rel.startswith("docs/fixture_doctor."):
        return "portfolio-liquidity-runway-lab fixture-doctor --out demo/fixture-doctor"
    if rel.startswith("demo/static-docs/") or rel.startswith("docs/static-docs/"):
        return "portfolio-liquidity-runway-lab docs-export --out demo/static-docs"
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
    html_with_script = [rel for rel in html_files if _contains_script_tag(root / rel)]
    scan = public_scan(root)
    checks = {
        "expected_files": not missing,
        "public_scan": scan["status"] == "pass",
        "html_no_script_tags": not html_with_script,
    }
    status = "pass" if all(checks.values()) else "fail"
    return {
        "boundary": BOUNDARY_TEXT,
        "status": status,
        "checks": checks,
        "missing_files": missing,
        "html_files": html_files,
        "html_with_script_tags": html_with_script,
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
            if term in lowered:
                findings.append(f"Potential secret marker {term!r} in {rel}")
    return {"boundary": BOUNDARY_TEXT, "status": "pass" if not findings else "review", "findings": findings}


def release_manifest(root: Path) -> Dict[str, Any]:
    files = []
    for path in sorted(root.rglob("*")):
        rel_path = path.relative_to(root)
        if path.is_file() and not _is_ignored_release_path(rel_path):
            files.append(path.relative_to(root).as_posix())
    return {
        "name": "portfolio-liquidity-runway-lab",
        "version": "0.5.0",
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
        "demo_fixture_doctor": (root / "demo/fixture-doctor/fixture_doctor.md").exists(),
        "demo_static_docs": (root / "demo/static-docs/index.html").exists(),
        "demo_visual_receipt": (root / "demo/visual_receipt.md").exists(),
        "tests": (root / "tests").exists(),
        "agent_skill": (root / "skills/agent/portfolio-liquidity-runway-lab/SKILL.md").exists(),
        "no_github_workflows": not (root / ".github/workflows").exists(),
    }
    return {"boundary": BOUNDARY_TEXT, "score": sum(1 for value in checks.values() if value), "checks": checks}


def write_csv(rows: List[Mapping[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
