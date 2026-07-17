# Schema Guide

> Educational static analysis only. This tool uses local synthetic or user-supplied inputs, does not fetch live data, does not connect to brokers, does not place orders, and does not provide tax, legal, investment, buy, sell, or hold advice.

Version: `0.10.1`

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

### portfolio.csv

CSV asset rows accepted by csv-import and input-lint.

Required fields: `name`, `value`, `liquidity_tier`, `annual_yield_rate`, `annual_fee_rate`

| Path | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | `string` | true | Asset display name. |
| `value` | `number` | true | Gross asset value. |
| `liquidity_tier` | `enum` | true | Liquidity bucket copied into portfolio.assets[].liquidity_tier. Allowed values: `same_day`, `one_week`, `one_month`, `locked`. |
| `annual_yield_rate` | `number` | true | Annual yield assumption as a decimal. |
| `annual_fee_rate` | `number` | true | Annual fee assumption as a decimal. |

### ledger.csv

CSV settings and scheduled event rows accepted by csv-import and input-lint.

Required fields: `record_type`, `monthly_income`, `monthly_expenses`, `month`, `type`, `label`, `amount`

| Path | Type | Required | Description |
| --- | --- | --- | --- |
| `record_type` | `enum` | true | settings row supplies recurring values; event rows supply scheduled events. Allowed values: `settings`, `event`. |
| `monthly_income` | `number` | settings | Monthly income for the single settings row. |
| `monthly_expenses` | `number` | settings | Monthly expenses for the single settings row. |
| `month` | `integer` | event | Scheduled event month. |
| `type` | `enum` | event | Scheduled event direction. Allowed values: `inflow`, `outflow`. |
| `label` | `string` | false | Scheduled event label. |
| `amount` | `number` | event | Scheduled event amount. |

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
| `import_report.json` | `csv-import` | `boundary`, `status`, `inputs`, `outputs`, `row_counts`, `schema_refs`, `findings` |
| `export_manifest.json` | `csv-export` | `boundary`, `status`, `packet`, `portfolio_name`, `scenario`, `files` |
| `input-lint stdout JSON` | `input-lint` | `boundary`, `status`, `results`, `finding_counts` |
| `SHA256SUMS.txt` | `bundle-checksums` | `sha256 path lines` |
| `bundle_manifest.json` | `bundle-checksums` | `boundary`, `version`, `root`, `file_count`, `files` |
| `evidence-bundle/index.html` | `evidence-bundle` | `no JavaScript static evidence index` |
| `evidence_manifest.json` | `evidence-bundle` | `boundary`, `version`, `root`, `artifact_count`, `artifacts` |
| `template_manifest.json` | `template-pack` | `boundary`, `version`, `file_count`, `files` |

## Command Matrix

| Command | Inputs | Outputs | Static no-JS HTML |
| --- | --- | --- | --- |
| `build-packet` | portfolio.json, ledger.json, assumptions.json | liquidity_packet.json, liquidity_packet.md, liquidity_packet.html | true |
| `compare-history` | history.json | stdout JSON, optional JSON file | false |
| `review-ledger` | ledger.json | stdout JSON, optional JSON file | false |
| `static-dashboard` | portfolio.json, ledger.json, assumptions.json | liquidity_packet.json, liquidity_packet.md, liquidity_packet.html | true |
| `scenario-gallery` | portfolio.json, ledger.json, assumptions.json | scenario_gallery.json, scenario_gallery.md, scenario_gallery.html | true |
| `assumption-audit` | portfolio.json, ledger.json, assumptions.json | assumption_audit.json, assumption_audit.md | false |
| `batch-compare` | portfolio directory, ledger.json, assumptions.json | batch_compare.json, batch_compare.md, batch_compare.html | true |
| `casebook` | portfolio.json, portfolio directory, ledger.json, assumptions.json | casebook.json, casebook.md, casebook.html | true |
| `artifact-catalog` | repo or output root | artifact_catalog.json, artifact_catalog.md | false |
| `release-check` | repo root | release_check.json, release_check.md | false |
| `visual-receipt` | portfolio.json, ledger.json, assumptions.json | visual_receipt.md | false |
| `schema-export` | built-in schema metadata | schema_guide.json, schema_guide.md | false |
| `csv-import` | portfolio.csv, ledger.csv | portfolio.json, ledger.json, import_report.json, import_report.md | false |
| `csv-export` | liquidity_packet.json | assets.csv, runway.csv, warnings.csv, bucket_summaries.csv, export_manifest.json, export_manifest.md | false |
| `input-lint` | portfolio/ledger/assumptions JSON, portfolio/ledger CSV | stdout JSON, optional JSON file | false |
| `bundle-checksums` | repo root, docs, demos, optional dist wheel/sdist | SHA256SUMS.txt, bundle_manifest.json, bundle_manifest.md | false |
| `evidence-bundle` | repo docs and demo evidence | index.md, index.html, SHA256SUMS.txt, evidence_manifest.json, boundary_risks.md, command_replay.md | true |
| `template-pack` | built-in starter templates | README.md, template_manifest.json, portfolio.csv, ledger.csv, portfolio.json, ledger.json, assumptions.json | false |
| `fixture-doctor` | bundled or supplied examples | fixture_doctor.json, fixture_doctor.md | true |
| `docs-export` | README and generated release evidence | static-docs/index.html, static-docs/index.md, static-docs/*.md | true |
| `command-matrix` | built-in command metadata | command_matrix.json, command_matrix.md, command_matrix.html | true |
| `golden-replay` | repo root, committed demo artifacts | golden_replay.json, golden_replay.md | false |
| `release-deck` | repo docs and demo evidence | release_deck.md, release_deck.html | true |
| `quickstart-check` | bundled examples | copied examples, packet artifacts | true |
| `selfcheck` | bundled examples | stdout JSON | true |
| `public-scan` | repo root | stdout JSON, optional JSON file | false |
| `release-manifest` | repo root | stdout JSON, optional JSON file | false |
| `maturity-report` | repo root | stdout JSON, optional JSON file | false |
