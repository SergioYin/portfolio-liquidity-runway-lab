# Schema Guide

> Educational static analysis only. This tool uses local synthetic or user-supplied inputs, does not fetch live data, does not connect to brokers, does not place orders, and does not provide tax, legal, investment, buy, sell, or hold advice.

Version: `0.5.0`

## Input Files

### portfolio.json

Portfolio asset inventory used by packet, gallery, audit, batch, casebook, and receipt commands.

Required fields: `name`, `currency`, `assets`

| Path | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | `string` | false | Human-readable portfolio name. |
| `currency` | `string` | false | Display currency label; calculations treat values as already normalized. |
| `assets` | `array<object>` | true | Asset rows used for liquidity buckets and yield or fee assumptions. |
| `assets[].name` | `string` | false | Asset display name. |
| `assets[].value` | `number` | true | Gross asset value. |
| `assets[].liquidity_tier` | `enum` | true | Liquidity bucket for stress haircut and runway grouping. Allowed values: `same_day`, `one_week`, `one_month`, `locked`. |
| `assets[].annual_yield_rate` | `number` | true | Annual yield assumption as a decimal, for example 0.04. |
| `assets[].annual_fee_rate` | `number` | true | Annual fee assumption as a decimal, for example 0.01. |

### ledger.json

Recurring income, recurring expenses, and scheduled cash events.

Required fields: `monthly_income`, `monthly_expenses`, `scheduled_events`

| Path | Type | Required | Description |
| --- | --- | --- | --- |
| `monthly_income` | `number` | true | Expected monthly income before scenario multiplier. |
| `monthly_expenses` | `number` | true | Expected monthly expenses before scenario multiplier. |
| `scheduled_events` | `array<object>` | false | One-time inflow or outflow events by month. |
| `scheduled_events[].month` | `integer` | true | 1-based month in the runway window. |
| `scheduled_events[].type` | `enum` | true | Cash event direction. Allowed values: `inflow`, `outflow`. |
| `scheduled_events[].label` | `string` | false | Event label for review. |
| `scheduled_events[].amount` | `number` | true | Positive event amount. |

### assumptions.json

Runway window, reserve threshold, default scenario, and named scenario stress assumptions.

Required fields: `months`, `target_reserve_months`, `default_scenario`, `scenarios`

| Path | Type | Required | Description |
| --- | --- | --- | --- |
| `months` | `integer` | true | Number of monthly runway rows to produce. |
| `target_reserve_months` | `number` | true | Same-day reserve threshold used for warnings. |
| `default_scenario` | `string` | false | Scenario used when no scenario argument is supplied. |
| `scenarios` | `object` | true | Named scenario map. |
| `scenarios.<name>.expense_multiplier` | `number` | true | Multiplier applied to monthly expenses. |
| `scenarios.<name>.income_multiplier` | `number` | true | Multiplier applied to monthly income. |
| `scenarios.<name>.liquidity_haircuts` | `object` | true | Haircut map keyed by liquidity tier. |
| `scenarios.<name>.liquidity_haircuts.same_day` | `number` | true | Haircut from 0 to 1. |
| `scenarios.<name>.liquidity_haircuts.one_week` | `number` | true | Haircut from 0 to 1. |
| `scenarios.<name>.liquidity_haircuts.one_month` | `number` | true | Haircut from 0 to 1. |
| `scenarios.<name>.liquidity_haircuts.locked` | `number` | true | Haircut from 0 to 1. |

### history.json

Historical reserve and burn snapshots for compare-history.

Required fields: `snapshots`

| Path | Type | Required | Description |
| --- | --- | --- | --- |
| `snapshots` | `array<object>` | true | At least two snapshots. |
| `snapshots[].label` | `string` | true | Snapshot label. |
| `snapshots[].same_day_reserve_months` | `number` | true | Reserve-month value for delta comparison. |
| `snapshots[].effective_monthly_burn` | `number` | true | Monthly burn value for delta comparison. |

## Output Artifacts

| Artifact | Command | Top-level fields |
| --- | --- | --- |
| `liquidity_packet.json` | `build-packet` | `boundary`, `scenario`, `portfolio_name`, `currency`, `totals`, `cash_buckets`, `assets`, `scheduled_events`, `monthly_runway`, `forced_sale_warnings`, `review_prompts` |
| `liquidity_packet.md` | `build-packet` | `summary`, `cash buckets`, `scheduled events`, `monthly runway`, `warnings`, `review prompts` |
| `liquidity_packet.html` | `build-packet/static-dashboard` | `no JavaScript static HTML rendering of packet Markdown` |
| `scenario_gallery.json` | `scenario-gallery` | `boundary`, `portfolio_name`, `currency`, `scenario_names`, `summary`, `scenarios` |
| `assumption_audit.json` | `assumption-audit` | `boundary`, `status`, `finding_counts`, `portfolio_name`, `findings` |
| `batch_compare.json` | `batch-compare` | `boundary`, `portfolio_files`, `scenario_names`, `summary`, `warnings` |
| `casebook.json` | `casebook` | `boundary`, `title`, `inputs`, `regeneration_commands`, `packet_summary`, `scenario_gallery_summary`, `assumption_audit_summary`, `batch_compare_summary` |
| `visual_receipt.md` | `visual-receipt` | `packet linkage`, `regeneration`, `snapshot`, `liquidity view`, `review signals` |
| `artifact_catalog.json` | `artifact-catalog` | `boundary`, `root`, `artifact_count`, `artifacts` |
| `release_check.json` | `release-check` | `boundary`, `status`, `checks`, `missing_files`, `html_files`, `html_with_script_tags`, `public_scan_findings` |
| `schema_guide.json` | `schema-export` | `boundary`, `version`, `input_files`, `output_artifacts` |
| `fixture_doctor.json` | `fixture-doctor` | `boundary`, `status`, `work_dir`, `examples`, `command_plan`, `results` |
| `static-docs/index.html` | `docs-export` | `no JavaScript static documentation index` |

## Command Matrix

| Command | Inputs | Outputs | Static no-JS HTML |
| --- | --- | --- | --- |
| `build-packet` | portfolio.json, ledger.json, assumptions.json | liquidity_packet.json, liquidity_packet.md, liquidity_packet.html | true |
| `compare-history` | history.json | stdout JSON, optional JSON file | false |
| `review-ledger` | ledger.json | stdout JSON, optional JSON file | false |
| `static-dashboard` | portfolio.json, ledger.json, assumptions.json | liquidity_packet.html | true |
| `scenario-gallery` | portfolio.json, ledger.json, assumptions.json | scenario_gallery.json, scenario_gallery.md, scenario_gallery.html | true |
| `assumption-audit` | portfolio.json, ledger.json, assumptions.json | assumption_audit.json, assumption_audit.md | false |
| `batch-compare` | portfolio directory, ledger.json, assumptions.json | batch_compare.json, batch_compare.md, batch_compare.html | true |
| `casebook` | portfolio.json, portfolio directory, ledger.json, assumptions.json | casebook.json, casebook.md, casebook.html | true |
| `artifact-catalog` | repo or output root | artifact_catalog.json, artifact_catalog.md | false |
| `release-check` | repo root | release_check.json, release_check.md | false |
| `visual-receipt` | portfolio.json, ledger.json, assumptions.json | visual_receipt.md | false |
| `quickstart-check` | bundled examples | copied examples, packet artifacts | true |
| `selfcheck` | bundled examples | stdout JSON | true |
| `public-scan` | repo root | stdout JSON, optional JSON file | false |
| `release-manifest` | repo root | stdout JSON, optional JSON file | false |
| `maturity-report` | repo root | stdout JSON, optional JSON file | false |
| `schema-export` | built-in schema metadata | schema_guide.json, schema_guide.md | false |
| `fixture-doctor` | bundled or supplied examples | fixture_doctor.json, fixture_doctor.md | true |
| `docs-export` | README and generated release evidence | static-docs/index.html, static-docs/index.md, static-docs/*.md | true |
