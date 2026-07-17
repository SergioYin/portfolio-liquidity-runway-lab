# Offline Starter Template Pack

> Educational static analysis only. This tool uses local synthetic or user-supplied inputs, does not fetch live data, does not connect to brokers, does not place orders, and does not provide tax, legal, investment, buy, sell, or hold advice.

Use these files as clean local starters. Replace every value with your own offline records before review.

## Files

- `portfolio.csv` and `ledger.csv`: spreadsheet-friendly starters for `csv-import`.
- `portfolio.json`, `ledger.json`, and `assumptions.json`: direct JSON starters for packet commands.
- `template_manifest.json`: deterministic file inventory and hashes.

## Replay

```bash
portfolio-liquidity-runway-lab input-lint --portfolio portfolio.json --ledger ledger.json --assumptions assumptions.json --portfolio-csv portfolio.csv --ledger-csv ledger.csv
portfolio-liquidity-runway-lab build-packet --portfolio portfolio.json --ledger ledger.json --assumptions assumptions.json --scenario stress --out packet
portfolio-liquidity-runway-lab csv-import --portfolio-csv portfolio.csv --ledger-csv ledger.csv --out csv-import
```
