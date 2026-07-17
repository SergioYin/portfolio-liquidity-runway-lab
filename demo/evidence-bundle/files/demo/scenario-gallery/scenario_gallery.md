# Scenario Gallery: Synthetic household reserve portfolio

> Educational static analysis only. This tool uses local synthetic or user-supplied inputs, does not fetch live data, does not connect to brokers, does not place orders, and does not provide tax, legal, investment, buy, sell, or hold advice.

## Scenario Summary

| Scenario | Haircut assets | Effective monthly burn | Same-day reserve months | 30-day runway months | Warnings | First negative month |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| base | $147,090.00 | $4,030.83 | 5.32 | 24.4 | 2 |  |
| stress | $133,460.00 | $7,282.83 | 4.51 | 12.97 | 3 | 10 |
| income_shock | $138,210.00 | $7,360.83 | 5.07 | 13.04 | 3 | 10 |
| reserve_rebuild | $149,260.00 | $2,862.83 | 5.78 | 34.43 | 2 |  |

## base

- Gross assets: $165,000.00
- Stress haircut assets: $147,090.00
- Effective monthly burn: $4,030.83
- Same-day reserve months: 5.32
- Same-day + one-week runway months: 19.21
- Thirty-day runway months: 24.4

Warnings:
- Same-day reserve is 5.3 months, below the 6.0 month review threshold.
- Locked or gated assets exceed 35% of gross assets while burn is positive.

## stress

- Gross assets: $165,000.00
- Stress haircut assets: $133,460.00
- Effective monthly burn: $7,282.83
- Same-day reserve months: 4.51
- Same-day + one-week runway months: 10.4
- Thirty-day runway months: 12.97

Warnings:
- Liquid balance turns negative in month 10; review whether one_month or locked holdings would be needed.
- Same-day reserve is 4.5 months, below the 6.0 month review threshold.
- Locked or gated assets exceed 35% of gross assets while burn is positive.

## income_shock

- Gross assets: $165,000.00
- Stress haircut assets: $138,210.00
- Effective monthly burn: $7,360.83
- Same-day reserve months: 5.07
- Same-day + one-week runway months: 10.41
- Thirty-day runway months: 13.04

Warnings:
- Liquid balance turns negative in month 10; review whether one_month or locked holdings would be needed.
- Same-day reserve is 5.1 months, below the 6.0 month review threshold.
- Locked or gated assets exceed 35% of gross assets while burn is positive.

## reserve_rebuild

- Gross assets: $165,000.00
- Stress haircut assets: $149,260.00
- Effective monthly burn: $2,862.83
- Same-day reserve months: 5.78
- Same-day + one-week runway months: 27.05
- Thirty-day runway months: 34.43

Warnings:
- Same-day reserve is 5.8 months, below the 6.0 month review threshold.
- Locked or gated assets exceed 35% of gross assets while burn is positive.
