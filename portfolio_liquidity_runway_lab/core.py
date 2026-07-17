from __future__ import annotations

import csv
import html
import json
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


IGNORED_RELEASE_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
}


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
        if _is_ignored_release_path(path):
            continue
        if path.is_dir():
            continue
        rel = path.relative_to(root).as_posix()
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
        if path.is_file() and not _is_ignored_release_path(path):
            files.append(path.relative_to(root).as_posix())
    return {
        "name": "portfolio-liquidity-runway-lab",
        "version": "0.2.0",
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
        "demo_scenario_gallery": (root / "demo/scenario-gallery/scenario_gallery.md").exists(),
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
