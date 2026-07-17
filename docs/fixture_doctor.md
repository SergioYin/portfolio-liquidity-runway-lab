# Fixture Doctor

> Educational static analysis only. This tool uses local synthetic or user-supplied inputs, does not fetch live data, does not connect to brokers, does not place orders, and does not provide tax, legal, investment, buy, sell, or hold advice.

Status: `pass`
Work dir: `docs/work`

## Copied Examples

- `assumptions.json` -> `docs/work/examples/assumptions.json`
- `history.json` -> `docs/work/examples/history.json`
- `ledger.csv` -> `docs/work/examples/ledger.csv`
- `ledger.json` -> `docs/work/examples/ledger.json`
- `portfolio.csv` -> `docs/work/examples/portfolio.csv`
- `portfolio.json` -> `docs/work/examples/portfolio.json`
- `portfolio_concentrated.json` -> `docs/work/examples/portfolio_concentrated.json`

## Command Plan

| Command | Args |
| --- | --- |
| `build-packet` | `build-packet --portfolio docs/work/examples/portfolio.json --ledger docs/work/examples/ledger.json --assumptions docs/work/examples/assumptions.json --scenario stress --out docs/work/packet` |
| `static-dashboard` | `static-dashboard --portfolio docs/work/examples/portfolio.json --ledger docs/work/examples/ledger.json --assumptions docs/work/examples/assumptions.json --out docs/work/dashboard` |
| `scenario-gallery` | `scenario-gallery --portfolio docs/work/examples/portfolio.json --ledger docs/work/examples/ledger.json --assumptions docs/work/examples/assumptions.json --out docs/work/scenario-gallery` |
| `assumption-audit` | `assumption-audit --portfolio docs/work/examples/portfolio_concentrated.json --ledger docs/work/examples/ledger.json --assumptions docs/work/examples/assumptions.json --out docs/work/assumption-audit` |
| `batch-compare` | `batch-compare --portfolios-dir docs/work/portfolios --ledger docs/work/examples/ledger.json --assumptions docs/work/examples/assumptions.json --scenarios base,stress --out docs/work/batch-compare` |
| `casebook` | `casebook --portfolio docs/work/examples/portfolio.json --ledger docs/work/examples/ledger.json --assumptions docs/work/examples/assumptions.json --portfolios-dir docs/work/portfolios --scenario stress --scenarios base,stress,income_shock --out docs/work/casebook` |
| `visual-receipt` | `visual-receipt --portfolio docs/work/examples/portfolio.json --ledger docs/work/examples/ledger.json --assumptions docs/work/examples/assumptions.json --scenario stress --out docs/work/visual_receipt.md` |
| `compare-history` | `compare-history --history docs/work/examples/history.json --out docs/work/history_compare.json` |
| `review-ledger` | `review-ledger --ledger docs/work/examples/ledger.json --out docs/work/ledger_review.json` |
| `schema-export` | `schema-export --out docs/work/schema-export` |
| `csv-import` | `csv-import --portfolio-csv docs/work/examples/portfolio.csv --ledger-csv docs/work/examples/ledger.csv --out docs/work/csv-import` |
| `csv-export` | `csv-export --packet docs/work/packet/liquidity_packet.json --out docs/work/csv-export` |
| `input-lint` | `input-lint --portfolio docs/work/examples/portfolio.json --ledger docs/work/examples/ledger.json --assumptions docs/work/examples/assumptions.json --portfolio-csv docs/work/examples/portfolio.csv --ledger-csv docs/work/examples/ledger.csv` |
| `docs-export` | `docs-export --root docs/work --out docs/work/static-docs` |
| `command-matrix` | `command-matrix --out docs/work/command-matrix` |
| `release-deck` | `release-deck --root docs/work --out docs/work/release-deck` |
| `artifact-catalog` | `artifact-catalog --root docs/work --paths packet,dashboard,scenario-gallery,assumption-audit,batch-compare,casebook,schema-export,csv-import,csv-export,static-docs --out docs/work/catalog` |
| `release-check` | `release-check --root docs/work --out docs/work/release-check` |
| `public-scan` | `public-scan --root docs/work --out docs/work/public_scan.json` |
| `release-manifest` | `release-manifest --root docs/work --out docs/work/release_manifest.json` |
| `maturity-report` | `maturity-report --root docs/work --out docs/work/maturity_report.json` |

## Results

| Command | Status | Outputs | Message |
| --- | --- | --- | --- |
| `build-packet` | `pass` | `docs/work/packet/liquidity_packet.json`, `docs/work/packet/liquidity_packet.md`, `docs/work/packet/liquidity_packet.html` |  |
| `static-dashboard` | `pass` | `docs/work/dashboard/liquidity_packet.json`, `docs/work/dashboard/liquidity_packet.md`, `docs/work/dashboard/liquidity_packet.html` |  |
| `scenario-gallery` | `pass` | `docs/work/scenario-gallery/scenario_gallery.json`, `docs/work/scenario-gallery/scenario_gallery.md`, `docs/work/scenario-gallery/scenario_gallery.html` |  |
| `assumption-audit` | `pass` | `docs/work/assumption-audit/assumption_audit.json`, `docs/work/assumption-audit/assumption_audit.md` |  |
| `batch-compare` | `pass` | `docs/work/batch-compare/batch_compare.json`, `docs/work/batch-compare/batch_compare.md`, `docs/work/batch-compare/batch_compare.html` |  |
| `casebook` | `pass` | `docs/work/casebook/casebook.json`, `docs/work/casebook/casebook.md`, `docs/work/casebook/casebook.html` |  |
| `visual-receipt` | `pass` | `docs/work/visual_receipt.md` |  |
| `compare-history` | `pass` | `docs/work/history_compare.json` |  |
| `review-ledger` | `pass` | `docs/work/ledger_review.json` |  |
| `schema-export` | `pass` | `docs/work/schema-export/schema_guide.json`, `docs/work/schema-export/schema_guide.md` |  |
| `csv-import` | `pass` | `docs/work/csv-import/portfolio.json`, `docs/work/csv-import/ledger.json`, `docs/work/csv-import/import_report.json`, `docs/work/csv-import/import_report.md` |  |
| `csv-export` | `pass` | `docs/work/csv-export/assets.csv`, `docs/work/csv-export/runway.csv`, `docs/work/csv-export/warnings.csv`, `docs/work/csv-export/bucket_summaries.csv`, `docs/work/csv-export/export_manifest.json`, `docs/work/csv-export/export_manifest.md` |  |
| `input-lint` | `pass` | `stdout JSON` |  |
| `docs-export` | `pass` | `docs/work/static-docs/index.html`, `docs/work/static-docs/index.md` |  |
| `command-matrix` | `pass` | `docs/work/command-matrix/command_matrix.json`, `docs/work/command-matrix/command_matrix.md`, `docs/work/command-matrix/command_matrix.html` |  |
| `release-deck` | `pass` | `docs/work/release-deck/release_deck.md`, `docs/work/release-deck/release_deck.html` |  |
| `artifact-catalog` | `pass` | `docs/work/catalog/artifact_catalog.json`, `docs/work/catalog/artifact_catalog.md` |  |
| `release-check` | `pass` | `docs/work/release-check/release_check.json`, `docs/work/release-check/release_check.md` |  |
| `public-scan` | `pass` | `docs/work/public_scan.json` |  |
| `release-manifest` | `pass` | `docs/work/release_manifest.json` |  |
| `maturity-report` | `pass` | `docs/work/maturity_report.json` |  |
