# Release Owner Casebook: Synthetic household reserve portfolio

> Educational static analysis only. This tool uses local synthetic or user-supplied inputs, does not fetch live data, does not connect to brokers, does not place orders, and does not provide tax, legal, investment, buy, sell, or hold advice.

## Regeneration

```bash
portfolio-liquidity-runway-lab casebook --out demo/casebook
portfolio-liquidity-runway-lab build-packet --out demo/casebook/packet
portfolio-liquidity-runway-lab scenario-gallery --out demo/casebook/scenario-gallery
portfolio-liquidity-runway-lab assumption-audit --out demo/casebook/assumption-audit
portfolio-liquidity-runway-lab batch-compare --portfolios-dir portfolio_liquidity_runway_lab/examples --out demo/casebook/batch-compare
```

## Packet Summary

- Scenario: `stress`
- Gross assets: $165,000.00
- Stress haircut assets: $133,460.00
- Effective monthly burn: $7,282.83
- Same-day reserve months: 4.51

### Cash Buckets

| Tier | Count | Gross | Stress value |
| --- | ---: | ---: | ---: |
| Same day | 2 | $50,000.00 | $50,000.00 |
| One week | 1 | $28,000.00 | $25,760.00 |
| One month | 1 | $22,000.00 | $18,700.00 |
| Locked or gated | 1 | $65,000.00 | $39,000.00 |

### Forced-Sale Warnings

- Liquid balance turns negative in month 10; review whether one_month or locked holdings would be needed.
- Same-day reserve is 4.5 months, below the 6.0 month review threshold.
- Locked or gated assets exceed 35% of gross assets while burn is positive.

## Scenario Gallery Summary

| Scenario | Haircut assets | Effective monthly burn | 30-day runway | Warnings |
| --- | ---: | ---: | ---: | ---: |
| base | $147,090.00 | $4,030.83 | 24.4 | 2 |
| stress | $133,460.00 | $7,282.83 | 12.97 | 3 |
| income_shock | $138,210.00 | $7,360.83 | 13.04 | 3 |

## Assumption Audit Summary

- Status: `pass`
- Errors: 0
- Warnings: 0

| Severity | Code | Location | Message |
| --- | --- | --- | --- |
| pass | none |  | No audit findings were triggered. |

## Batch Compare Summary

| Portfolio | Scenario | Same-day reserve months | 30-day runway | Effective monthly burn | Warnings |
| --- | --- | ---: | ---: | ---: | ---: |
| portfolio.json | base | 5.32 | 24.4 | $4,030.83 | 2 |
| portfolio.json | stress | 4.51 | 12.97 | $7,282.83 | 3 |
| portfolio.json | income_shock | 5.07 | 13.04 | $7,360.83 | 3 |
| portfolio_concentrated.json | base | 1.01 | 3.83 | $2,478.38 | 3 |
| portfolio_concentrated.json | stress | 0.86 | 1.66 | $5,730.38 | 3 |
| portfolio_concentrated.json | income_shock | 0.96 | 1.64 | $5,808.38 | 3 |
