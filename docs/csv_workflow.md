# CSV Workflow

> Educational static analysis only. This tool uses local synthetic or user-supplied inputs, does not fetch live data, does not connect to brokers, does not place orders, and does not provide tax, legal, investment, buy, sell, or hold advice.

## Import

`csv-import` converts local `portfolio.csv` and `ledger.csv` rows into the existing `portfolio.json` and `ledger.json` schemas. It also writes `import_report.json` and `import_report.md` with row counts, schema references, and validation findings.

```bash
portfolio-liquidity-runway-lab csv-import --out demo/csv-import
```

## Export

`csv-export` reads an existing `liquidity_packet.json` and writes deterministic CSV files for packet assets, monthly runway rows, forced-sale warnings, and liquidity bucket summaries. String cells beginning with spreadsheet formula prefixes are written with a leading apostrophe for safer spreadsheet opening. It also writes `export_manifest.json` and `export_manifest.md` with row counts and SHA256 hashes.

```bash
portfolio-liquidity-runway-lab build-packet --out demo/csv-export-packet --scenario stress
portfolio-liquidity-runway-lab csv-export --packet demo/csv-export-packet/liquidity_packet.json --out demo/csv-export
```

## Lint

`input-lint` validates JSON and CSV inputs before packet generation. Errors include a schema reference and a remediation message, and the command exits nonzero when any error is present.

```bash
portfolio-liquidity-runway-lab input-lint --portfolio portfolio.json --ledger ledger.json --assumptions assumptions.json --portfolio-csv portfolio.csv --ledger-csv ledger.csv
```
