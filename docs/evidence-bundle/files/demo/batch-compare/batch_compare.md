# Batch Portfolio Compare

> Educational static analysis only. This tool uses local synthetic or user-supplied inputs, does not fetch live data, does not connect to brokers, does not place orders, and does not provide tax, legal, investment, buy, sell, or hold advice.

## Summary

| Portfolio | Scenario | Same-day reserve months | Same-day + one-week runway | 30-day runway | Effective monthly burn | Warnings | First negative month |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| portfolio.json | base | 5.32 | 19.21 | 24.4 | $4,030.83 | 2 |  |
| portfolio.json | stress | 4.51 | 10.4 | 12.97 | $7,282.83 | 3 | 10 |
| portfolio_concentrated.json | base | 1.01 | 3.83 | 3.83 | $2,478.38 | 3 | 7 |
| portfolio_concentrated.json | stress | 0.86 | 1.66 | 1.66 | $5,730.38 | 3 | 2 |

## Warnings

### portfolio:base
- Same-day reserve is 5.3 months, below the 6.0 month review threshold.
- Locked or gated assets exceed 35% of gross assets while burn is positive.

### portfolio:stress
- Liquid balance turns negative in month 10; review whether one_month or locked holdings would be needed.
- Same-day reserve is 4.5 months, below the 6.0 month review threshold.
- Locked or gated assets exceed 35% of gross assets while burn is positive.

### portfolio_concentrated:base
- Liquid balance turns negative in month 7; review whether one_month or locked holdings would be needed.
- Same-day reserve is 1.0 months, below the 6.0 month review threshold.
- Locked or gated assets exceed 35% of gross assets while burn is positive.

### portfolio_concentrated:stress
- Liquid balance turns negative in month 2; review whether one_month or locked holdings would be needed.
- Same-day reserve is 0.9 months, below the 6.0 month review threshold.
- Locked or gated assets exceed 35% of gross assets while burn is positive.
