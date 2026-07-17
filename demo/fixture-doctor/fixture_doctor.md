# Fixture Doctor

> Educational static analysis only. This tool uses local synthetic or user-supplied inputs, does not fetch live data, does not connect to brokers, does not place orders, and does not provide tax, legal, investment, buy, sell, or hold advice.

Status: `pass`
Work dir: `demo/fixture-doctor/work`

## Copied Examples

- `assumptions.json` -> `demo/fixture-doctor/work/examples/assumptions.json`
- `history.json` -> `demo/fixture-doctor/work/examples/history.json`
- `ledger.csv` -> `demo/fixture-doctor/work/examples/ledger.csv`
- `ledger.json` -> `demo/fixture-doctor/work/examples/ledger.json`
- `portfolio.csv` -> `demo/fixture-doctor/work/examples/portfolio.csv`
- `portfolio.json` -> `demo/fixture-doctor/work/examples/portfolio.json`
- `portfolio_concentrated.json` -> `demo/fixture-doctor/work/examples/portfolio_concentrated.json`

## Command Plan

| Command | Args |
| --- | --- |
| `build-packet` | `build-packet --portfolio demo/fixture-doctor/work/examples/portfolio.json --ledger demo/fixture-doctor/work/examples/ledger.json --assumptions demo/fixture-doctor/work/examples/assumptions.json --scenario stress --out demo/fixture-doctor/work/packet` |
| `static-dashboard` | `static-dashboard --portfolio demo/fixture-doctor/work/examples/portfolio.json --ledger demo/fixture-doctor/work/examples/ledger.json --assumptions demo/fixture-doctor/work/examples/assumptions.json --out demo/fixture-doctor/work/dashboard` |
| `scenario-gallery` | `scenario-gallery --portfolio demo/fixture-doctor/work/examples/portfolio.json --ledger demo/fixture-doctor/work/examples/ledger.json --assumptions demo/fixture-doctor/work/examples/assumptions.json --out demo/fixture-doctor/work/scenario-gallery` |
| `assumption-audit` | `assumption-audit --portfolio demo/fixture-doctor/work/examples/portfolio_concentrated.json --ledger demo/fixture-doctor/work/examples/ledger.json --assumptions demo/fixture-doctor/work/examples/assumptions.json --out demo/fixture-doctor/work/assumption-audit` |
| `batch-compare` | `batch-compare --portfolios-dir demo/fixture-doctor/work/portfolios --ledger demo/fixture-doctor/work/examples/ledger.json --assumptions demo/fixture-doctor/work/examples/assumptions.json --scenarios base,stress --out demo/fixture-doctor/work/batch-compare` |
| `casebook` | `casebook --portfolio demo/fixture-doctor/work/examples/portfolio.json --ledger demo/fixture-doctor/work/examples/ledger.json --assumptions demo/fixture-doctor/work/examples/assumptions.json --portfolios-dir demo/fixture-doctor/work/portfolios --scenario stress --scenarios base,stress,income_shock --out demo/fixture-doctor/work/casebook` |
| `visual-receipt` | `visual-receipt --portfolio demo/fixture-doctor/work/examples/portfolio.json --ledger demo/fixture-doctor/work/examples/ledger.json --assumptions demo/fixture-doctor/work/examples/assumptions.json --scenario stress --out demo/fixture-doctor/work/visual_receipt.md` |
| `compare-history` | `compare-history --history demo/fixture-doctor/work/examples/history.json --out demo/fixture-doctor/work/history_compare.json` |
| `review-ledger` | `review-ledger --ledger demo/fixture-doctor/work/examples/ledger.json --out demo/fixture-doctor/work/ledger_review.json` |
| `schema-export` | `schema-export --out demo/fixture-doctor/work/schema-export` |
| `csv-import` | `csv-import --portfolio-csv demo/fixture-doctor/work/examples/portfolio.csv --ledger-csv demo/fixture-doctor/work/examples/ledger.csv --out demo/fixture-doctor/work/csv-import` |
| `csv-export` | `csv-export --packet demo/fixture-doctor/work/packet/liquidity_packet.json --out demo/fixture-doctor/work/csv-export` |
| `input-lint` | `input-lint --portfolio demo/fixture-doctor/work/examples/portfolio.json --ledger demo/fixture-doctor/work/examples/ledger.json --assumptions demo/fixture-doctor/work/examples/assumptions.json --portfolio-csv demo/fixture-doctor/work/examples/portfolio.csv --ledger-csv demo/fixture-doctor/work/examples/ledger.csv` |
| `bundle-checksums` | `bundle-checksums --root . --out demo/fixture-doctor/work/bundle-checksums` |
| `evidence-bundle` | `evidence-bundle --root . --out demo/fixture-doctor/work/evidence-bundle` |
| `template-pack` | `template-pack --out demo/fixture-doctor/work/template-pack` |
| `docs-export` | `docs-export --root . --out demo/fixture-doctor/work/static-docs` |
| `command-matrix` | `command-matrix --out demo/fixture-doctor/work/command-matrix` |
| `release-deck` | `release-deck --root . --out demo/fixture-doctor/work/release-deck` |
| `artifact-catalog` | `artifact-catalog --root . --paths packet,dashboard,scenario-gallery,assumption-audit,batch-compare,casebook,schema-export,csv-import,csv-export,static-docs --out demo/fixture-doctor/work/catalog` |
| `release-check` | `release-check --root . --out demo/fixture-doctor/work/release-check` |
| `public-scan` | `public-scan --root . --out demo/fixture-doctor/work/public_scan.json` |
| `release-manifest` | `release-manifest --root . --out demo/fixture-doctor/work/release_manifest.json` |
| `maturity-report` | `maturity-report --root . --out demo/fixture-doctor/work/maturity_report.json` |

## Results

| Command | Status | Outputs | Message |
| --- | --- | --- | --- |
| `build-packet` | `pass` | `demo/fixture-doctor/work/packet/liquidity_packet.json`, `demo/fixture-doctor/work/packet/liquidity_packet.md`, `demo/fixture-doctor/work/packet/liquidity_packet.html` |  |
| `static-dashboard` | `pass` | `demo/fixture-doctor/work/dashboard/liquidity_packet.json`, `demo/fixture-doctor/work/dashboard/liquidity_packet.md`, `demo/fixture-doctor/work/dashboard/liquidity_packet.html` |  |
| `scenario-gallery` | `pass` | `demo/fixture-doctor/work/scenario-gallery/scenario_gallery.json`, `demo/fixture-doctor/work/scenario-gallery/scenario_gallery.md`, `demo/fixture-doctor/work/scenario-gallery/scenario_gallery.html` |  |
| `assumption-audit` | `pass` | `demo/fixture-doctor/work/assumption-audit/assumption_audit.json`, `demo/fixture-doctor/work/assumption-audit/assumption_audit.md` |  |
| `batch-compare` | `pass` | `demo/fixture-doctor/work/batch-compare/batch_compare.json`, `demo/fixture-doctor/work/batch-compare/batch_compare.md`, `demo/fixture-doctor/work/batch-compare/batch_compare.html` |  |
| `casebook` | `pass` | `demo/fixture-doctor/work/casebook/casebook.json`, `demo/fixture-doctor/work/casebook/casebook.md`, `demo/fixture-doctor/work/casebook/casebook.html` |  |
| `visual-receipt` | `pass` | `demo/fixture-doctor/work/visual_receipt.md` |  |
| `compare-history` | `pass` | `demo/fixture-doctor/work/history_compare.json` |  |
| `review-ledger` | `pass` | `demo/fixture-doctor/work/ledger_review.json` |  |
| `schema-export` | `pass` | `demo/fixture-doctor/work/schema-export/schema_guide.json`, `demo/fixture-doctor/work/schema-export/schema_guide.md` |  |
| `csv-import` | `pass` | `demo/fixture-doctor/work/csv-import/portfolio.json`, `demo/fixture-doctor/work/csv-import/ledger.json`, `demo/fixture-doctor/work/csv-import/import_report.json`, `demo/fixture-doctor/work/csv-import/import_report.md` |  |
| `csv-export` | `pass` | `demo/fixture-doctor/work/csv-export/assets.csv`, `demo/fixture-doctor/work/csv-export/runway.csv`, `demo/fixture-doctor/work/csv-export/warnings.csv`, `demo/fixture-doctor/work/csv-export/bucket_summaries.csv`, `demo/fixture-doctor/work/csv-export/export_manifest.json`, `demo/fixture-doctor/work/csv-export/export_manifest.md` |  |
| `input-lint` | `pass` | `stdout JSON` |  |
| `bundle-checksums` | `pass` | `demo/fixture-doctor/work/bundle-checksums/SHA256SUMS.txt`, `demo/fixture-doctor/work/bundle-checksums/bundle_manifest.json`, `demo/fixture-doctor/work/bundle-checksums/bundle_manifest.md` |  |
| `evidence-bundle` | `pass` | `demo/fixture-doctor/work/evidence-bundle/index.md`, `demo/fixture-doctor/work/evidence-bundle/index.html`, `demo/fixture-doctor/work/evidence-bundle/SHA256SUMS.txt`, `demo/fixture-doctor/work/evidence-bundle/evidence_manifest.json` |  |
| `template-pack` | `pass` | `demo/fixture-doctor/work/template-pack/README.md`, `demo/fixture-doctor/work/template-pack/template_manifest.json` |  |
| `docs-export` | `pass` | `demo/fixture-doctor/work/static-docs/index.html`, `demo/fixture-doctor/work/static-docs/index.md` |  |
| `command-matrix` | `pass` | `demo/fixture-doctor/work/command-matrix/command_matrix.json`, `demo/fixture-doctor/work/command-matrix/command_matrix.md`, `demo/fixture-doctor/work/command-matrix/command_matrix.html` |  |
| `release-deck` | `pass` | `demo/fixture-doctor/work/release-deck/release_deck.md`, `demo/fixture-doctor/work/release-deck/release_deck.html` |  |
| `artifact-catalog` | `pass` | `demo/fixture-doctor/work/catalog/artifact_catalog.json`, `demo/fixture-doctor/work/catalog/artifact_catalog.md` |  |
| `release-check` | `pass` | `demo/fixture-doctor/work/release-check/release_check.json`, `demo/fixture-doctor/work/release-check/release_check.md` |  |
| `public-scan` | `pass` | `demo/fixture-doctor/work/public_scan.json` |  |
| `release-manifest` | `pass` | `demo/fixture-doctor/work/release_manifest.json` |  |
| `maturity-report` | `pass` | `demo/fixture-doctor/work/maturity_report.json` |  |
