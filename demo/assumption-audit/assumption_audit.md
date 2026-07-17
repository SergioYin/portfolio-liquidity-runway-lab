# Assumption Audit: Synthetic concentrated liquidity portfolio

> Educational static analysis only. This tool uses local synthetic or user-supplied inputs, does not fetch live data, does not connect to brokers, does not place orders, and does not provide tax, legal, investment, buy, sell, or hold advice.

Status: `review`

## Finding Counts

- Errors: 0
- Warnings: 4

## Findings

| Severity | Code | Location | Message |
| --- | --- | --- | --- |
| warning | missing_liquidity_tier | `portfolio.assets.one_month` | No asset uses liquidity tier one_month. |
| warning | missing_liquidity_tier | `portfolio.assets.one_week` | No asset uses liquidity tier one_week. |
| warning | suspicious_fee | `portfolio.assets[1].annual_fee_rate` | Annual fee rate is outside the 0% to 5% audit band. |
| warning | suspicious_yield | `portfolio.assets[1].annual_yield_rate` | Annual yield rate is outside the -1% to 20% audit band. |
