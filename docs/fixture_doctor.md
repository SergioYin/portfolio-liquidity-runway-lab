# Fixture Doctor

> Educational static analysis only. This tool uses local synthetic or user-supplied inputs, does not fetch live data, does not connect to brokers, does not place orders, and does not provide tax, legal, investment, buy, sell, or hold advice.

Status: `pass`
Work dir: `temporary`

## Copied Examples

- `assumptions.json` -> `examples/assumptions.json`
- `history.json` -> `examples/history.json`
- `ledger.csv` -> `examples/ledger.csv`
- `ledger.json` -> `examples/ledger.json`
- `portfolio.csv` -> `examples/portfolio.csv`
- `portfolio.json` -> `examples/portfolio.json`
- `portfolio_concentrated.json` -> `examples/portfolio_concentrated.json`

## Command Plan

| Command | Args |
| --- | --- |
| `build-packet` | `build-packet --portfolio examples/portfolio.json --ledger examples/ledger.json --assumptions examples/assumptions.json --scenario stress --out packet` |
| `static-dashboard` | `static-dashboard --portfolio examples/portfolio.json --ledger examples/ledger.json --assumptions examples/assumptions.json --out dashboard` |
| `scenario-gallery` | `scenario-gallery --portfolio examples/portfolio.json --ledger examples/ledger.json --assumptions examples/assumptions.json --out scenario-gallery` |
| `assumption-audit` | `assumption-audit --portfolio examples/portfolio_concentrated.json --ledger examples/ledger.json --assumptions examples/assumptions.json --out assumption-audit` |
| `batch-compare` | `batch-compare --portfolios-dir portfolios --ledger examples/ledger.json --assumptions examples/assumptions.json --scenarios base,stress --out batch-compare` |
| `casebook` | `casebook --portfolio examples/portfolio.json --ledger examples/ledger.json --assumptions examples/assumptions.json --portfolios-dir portfolios --scenario stress --scenarios base,stress,income_shock --out casebook` |
| `visual-receipt` | `visual-receipt --portfolio examples/portfolio.json --ledger examples/ledger.json --assumptions examples/assumptions.json --scenario stress --out visual_receipt.md` |
| `compare-history` | `compare-history --history examples/history.json --out history_compare.json` |
| `review-ledger` | `review-ledger --ledger examples/ledger.json --out ledger_review.json` |
| `schema-export` | `schema-export --out schema-export` |
| `csv-import` | `csv-import --portfolio-csv examples/portfolio.csv --ledger-csv examples/ledger.csv --out csv-import` |
| `csv-export` | `csv-export --packet packet/liquidity_packet.json --out csv-export` |
| `input-lint` | `input-lint --portfolio examples/portfolio.json --ledger examples/ledger.json --assumptions examples/assumptions.json --portfolio-csv examples/portfolio.csv --ledger-csv examples/ledger.csv` |
| `bundle-checksums` | `bundle-checksums --root . --out bundle-checksums` |
| `evidence-bundle` | `evidence-bundle --root . --out evidence-bundle` |
| `template-pack` | `template-pack --out template-pack` |
| `docs-export` | `docs-export --root . --out static-docs` |
| `command-matrix` | `command-matrix --out command-matrix` |
| `release-deck` | `release-deck --root . --out release-deck` |
| `artifact-catalog` | `artifact-catalog --root . --paths packet,dashboard,scenario-gallery,assumption-audit,batch-compare,casebook,schema-export,csv-import,csv-export,static-docs --out catalog` |
| `release-check` | `release-check --root . --out release-check` |
| `public-scan` | `public-scan --root . --out public_scan.json` |
| `release-manifest` | `release-manifest --root . --out release_manifest.json` |
| `maturity-report` | `maturity-report --root . --out maturity_report.json` |

## Results

| Command | Status | Outputs | Message |
| --- | --- | --- | --- |
| `build-packet` | `pass` | `packet/liquidity_packet.json`, `packet/liquidity_packet.md`, `packet/liquidity_packet.html` |  |
| `static-dashboard` | `pass` | `dashboard/liquidity_packet.json`, `dashboard/liquidity_packet.md`, `dashboard/liquidity_packet.html` |  |
| `scenario-gallery` | `pass` | `scenario-gallery/scenario_gallery.json`, `scenario-gallery/scenario_gallery.md`, `scenario-gallery/scenario_gallery.html` |  |
| `assumption-audit` | `pass` | `assumption-audit/assumption_audit.json`, `assumption-audit/assumption_audit.md` |  |
| `batch-compare` | `pass` | `batch-compare/batch_compare.json`, `batch-compare/batch_compare.md`, `batch-compare/batch_compare.html` |  |
| `casebook` | `pass` | `casebook/casebook.json`, `casebook/casebook.md`, `casebook/casebook.html` |  |
| `visual-receipt` | `pass` | `visual_receipt.md` |  |
| `compare-history` | `pass` | `history_compare.json` |  |
| `review-ledger` | `pass` | `ledger_review.json` |  |
| `schema-export` | `pass` | `schema-export/schema_guide.json`, `schema-export/schema_guide.md` |  |
| `csv-import` | `pass` | `csv-import/portfolio.json`, `csv-import/ledger.json`, `csv-import/import_report.json`, `csv-import/import_report.md` |  |
| `csv-export` | `pass` | `csv-export/assets.csv`, `csv-export/runway.csv`, `csv-export/warnings.csv`, `csv-export/bucket_summaries.csv`, `csv-export/export_manifest.json`, `csv-export/export_manifest.md` |  |
| `input-lint` | `pass` | `stdout JSON` |  |
| `bundle-checksums` | `pass` | `bundle-checksums/SHA256SUMS.txt`, `bundle-checksums/bundle_manifest.json`, `bundle-checksums/bundle_manifest.md` |  |
| `evidence-bundle` | `pass` | `evidence-bundle/index.md`, `evidence-bundle/index.html`, `evidence-bundle/SHA256SUMS.txt`, `evidence-bundle/evidence_manifest.json` |  |
| `template-pack` | `pass` | `template-pack/README.md`, `template-pack/template_manifest.json` |  |
| `docs-export` | `pass` | `static-docs/index.html`, `static-docs/index.md` |  |
| `command-matrix` | `pass` | `command-matrix/command_matrix.json`, `command-matrix/command_matrix.md`, `command-matrix/command_matrix.html` |  |
| `release-deck` | `pass` | `release-deck/release_deck.md`, `release-deck/release_deck.html` |  |
| `artifact-catalog` | `pass` | `catalog/artifact_catalog.json`, `catalog/artifact_catalog.md` |  |
| `release-check` | `pass` | `release-check/release_check.json`, `release-check/release_check.md` |  |
| `public-scan` | `pass` | `public_scan.json` |  |
| `release-manifest` | `pass` | `release_manifest.json` |  |
| `maturity-report` | `pass` | `maturity_report.json` |  |
