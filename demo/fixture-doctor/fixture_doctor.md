# Fixture Doctor

> Educational static analysis only. This tool uses local synthetic or user-supplied inputs, does not fetch live data, does not connect to brokers, does not place orders, and does not provide tax, legal, investment, buy, sell, or hold advice.

Status: `pass`
Work dir: `dist/fixture-doctor-work`

## Copied Examples

- `assumptions.json` -> `dist/fixture-doctor-work/examples/assumptions.json`
- `history.json` -> `dist/fixture-doctor-work/examples/history.json`
- `ledger.json` -> `dist/fixture-doctor-work/examples/ledger.json`
- `portfolio.json` -> `dist/fixture-doctor-work/examples/portfolio.json`
- `portfolio_concentrated.json` -> `dist/fixture-doctor-work/examples/portfolio_concentrated.json`

## Command Plan

| Command | Args |
| --- | --- |
| `build-packet` | `build-packet --portfolio dist/fixture-doctor-work/examples/portfolio.json --ledger dist/fixture-doctor-work/examples/ledger.json --assumptions dist/fixture-doctor-work/examples/assumptions.json --scenario stress --out dist/fixture-doctor-work/packet` |
| `static-dashboard` | `static-dashboard --portfolio dist/fixture-doctor-work/examples/portfolio.json --ledger dist/fixture-doctor-work/examples/ledger.json --assumptions dist/fixture-doctor-work/examples/assumptions.json --out dist/fixture-doctor-work/dashboard` |
| `scenario-gallery` | `scenario-gallery --portfolio dist/fixture-doctor-work/examples/portfolio.json --ledger dist/fixture-doctor-work/examples/ledger.json --assumptions dist/fixture-doctor-work/examples/assumptions.json --out dist/fixture-doctor-work/scenario-gallery` |
| `assumption-audit` | `assumption-audit --portfolio dist/fixture-doctor-work/examples/portfolio_concentrated.json --ledger dist/fixture-doctor-work/examples/ledger.json --assumptions dist/fixture-doctor-work/examples/assumptions.json --out dist/fixture-doctor-work/assumption-audit` |
| `batch-compare` | `batch-compare --portfolios-dir dist/fixture-doctor-work/portfolios --ledger dist/fixture-doctor-work/examples/ledger.json --assumptions dist/fixture-doctor-work/examples/assumptions.json --scenarios base,stress --out dist/fixture-doctor-work/batch-compare` |
| `casebook` | `casebook --portfolio dist/fixture-doctor-work/examples/portfolio.json --ledger dist/fixture-doctor-work/examples/ledger.json --assumptions dist/fixture-doctor-work/examples/assumptions.json --portfolios-dir dist/fixture-doctor-work/portfolios --scenario stress --scenarios base,stress,income_shock --out dist/fixture-doctor-work/casebook` |
| `visual-receipt` | `visual-receipt --portfolio dist/fixture-doctor-work/examples/portfolio.json --ledger dist/fixture-doctor-work/examples/ledger.json --assumptions dist/fixture-doctor-work/examples/assumptions.json --scenario stress --out dist/fixture-doctor-work/visual_receipt.md` |
| `compare-history` | `compare-history --history dist/fixture-doctor-work/examples/history.json --out dist/fixture-doctor-work/history_compare.json` |
| `review-ledger` | `review-ledger --ledger dist/fixture-doctor-work/examples/ledger.json --out dist/fixture-doctor-work/ledger_review.json` |
| `schema-export` | `schema-export --out dist/fixture-doctor-work/schema-export` |
| `docs-export` | `docs-export --root dist/fixture-doctor-work --out dist/fixture-doctor-work/static-docs` |
| `artifact-catalog` | `artifact-catalog --root dist/fixture-doctor-work --paths packet,dashboard,scenario-gallery,assumption-audit,batch-compare,casebook,schema-export,static-docs --out dist/fixture-doctor-work/catalog` |
| `release-check` | `release-check --root dist/fixture-doctor-work --out dist/fixture-doctor-work/release-check` |
| `public-scan` | `public-scan --root dist/fixture-doctor-work --out dist/fixture-doctor-work/public_scan.json` |
| `release-manifest` | `release-manifest --root dist/fixture-doctor-work --out dist/fixture-doctor-work/release_manifest.json` |
| `maturity-report` | `maturity-report --root dist/fixture-doctor-work --out dist/fixture-doctor-work/maturity_report.json` |

## Results

| Command | Status | Outputs | Message |
| --- | --- | --- | --- |
| `build-packet` | `pass` | `dist/fixture-doctor-work/packet/liquidity_packet.json`, `dist/fixture-doctor-work/packet/liquidity_packet.md`, `dist/fixture-doctor-work/packet/liquidity_packet.html` |  |
| `static-dashboard` | `pass` | `dist/fixture-doctor-work/dashboard/liquidity_packet.json`, `dist/fixture-doctor-work/dashboard/liquidity_packet.md`, `dist/fixture-doctor-work/dashboard/liquidity_packet.html` |  |
| `scenario-gallery` | `pass` | `dist/fixture-doctor-work/scenario-gallery/scenario_gallery.json`, `dist/fixture-doctor-work/scenario-gallery/scenario_gallery.md`, `dist/fixture-doctor-work/scenario-gallery/scenario_gallery.html` |  |
| `assumption-audit` | `pass` | `dist/fixture-doctor-work/assumption-audit/assumption_audit.json`, `dist/fixture-doctor-work/assumption-audit/assumption_audit.md` |  |
| `batch-compare` | `pass` | `dist/fixture-doctor-work/batch-compare/batch_compare.json`, `dist/fixture-doctor-work/batch-compare/batch_compare.md`, `dist/fixture-doctor-work/batch-compare/batch_compare.html` |  |
| `casebook` | `pass` | `dist/fixture-doctor-work/casebook/casebook.json`, `dist/fixture-doctor-work/casebook/casebook.md`, `dist/fixture-doctor-work/casebook/casebook.html` |  |
| `visual-receipt` | `pass` | `dist/fixture-doctor-work/visual_receipt.md` |  |
| `compare-history` | `pass` | `dist/fixture-doctor-work/history_compare.json` |  |
| `review-ledger` | `pass` | `dist/fixture-doctor-work/ledger_review.json` |  |
| `schema-export` | `pass` | `dist/fixture-doctor-work/schema-export/schema_guide.json`, `dist/fixture-doctor-work/schema-export/schema_guide.md` |  |
| `docs-export` | `pass` | `dist/fixture-doctor-work/static-docs/index.html`, `dist/fixture-doctor-work/static-docs/index.md` |  |
| `artifact-catalog` | `pass` | `dist/fixture-doctor-work/catalog/artifact_catalog.json`, `dist/fixture-doctor-work/catalog/artifact_catalog.md` |  |
| `release-check` | `pass` | `dist/fixture-doctor-work/release-check/release_check.json`, `dist/fixture-doctor-work/release-check/release_check.md` |  |
| `public-scan` | `pass` | `dist/fixture-doctor-work/public_scan.json` |  |
| `release-manifest` | `pass` | `dist/fixture-doctor-work/release_manifest.json` |  |
| `maturity-report` | `pass` | `dist/fixture-doctor-work/maturity_report.json` |  |
