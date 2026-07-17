# Portfolio Liquidity Runway Packet: Synthetic household reserve portfolio

Scenario: `stress`

> Educational static analysis only. This tool uses local synthetic or user-supplied inputs, does not fetch live data, does not connect to brokers, does not place orders, and does not provide tax, legal, investment, buy, sell, or hold advice.

## Summary

- Gross assets: $165,000.00
- Stress haircut assets: $133,460.00
- Effective monthly burn: $7,282.83
- Same-day reserve months: 4.51
- Same-day + one-week runway months: 10.4
- Thirty-day runway months: 12.97

## Cash Buckets

| Tier | Count | Gross | Stress value |
| --- | ---: | ---: | ---: |
| Same day | 2 | $50,000.00 | $50,000.00 |
| One week | 1 | $28,000.00 | $25,760.00 |
| One month | 1 | $22,000.00 | $18,700.00 |
| Locked or gated | 1 | $65,000.00 | $39,000.00 |

## Scheduled Events

| Month | Type | Label | Amount |
| ---: | --- | --- | ---: |
| 2 | outflow | Insurance renewal | $1,800.00 |
| 4 | inflow | Contract receivable | $7,200.00 |
| 7 | outflow | Estimated tax placeholder | $5,500.00 |
| 10 | outflow | Home repair placeholder | $6,800.00 |

## Monthly Runway

| Month | Inflows | Outflows | Net burn | Liquid balance after |
| ---: | ---: | ---: | ---: | ---: |
| 1 | $0.00 | $0.00 | $7,282.83 | $68,477.17 |
| 2 | $0.00 | $1,800.00 | $9,082.83 | $59,394.33 |
| 3 | $0.00 | $0.00 | $7,282.83 | $52,111.50 |
| 4 | $7,200.00 | $0.00 | $82.83 | $52,028.67 |
| 5 | $0.00 | $0.00 | $7,282.83 | $44,745.83 |
| 6 | $0.00 | $0.00 | $7,282.83 | $37,463.00 |
| 7 | $0.00 | $5,500.00 | $12,782.83 | $24,680.17 |
| 8 | $0.00 | $0.00 | $7,282.83 | $17,397.33 |
| 9 | $0.00 | $0.00 | $7,282.83 | $10,114.50 |
| 10 | $0.00 | $6,800.00 | $14,082.83 | $-3,968.33 |
| 11 | $0.00 | $0.00 | $7,282.83 | $-11,251.17 |
| 12 | $0.00 | $0.00 | $7,282.83 | $-18,534.00 |

## Forced-Sale Warnings
- Liquid balance turns negative in month 10; review whether one_month or locked holdings would be needed.
- Same-day reserve is 4.5 months, below the 6.0 month review threshold.
- Locked or gated assets exceed 35% of gross assets while burn is positive.

## Review Prompts
- Confirm each liquidity tier against account restrictions and settlement timing.
- Check that scheduled inflows and outflows are documented and still expected.
- Review whether fees, yields, and stress haircuts are assumptions rather than live quotes.
- Escalate to a qualified professional for tax, legal, investment, or brokerage decisions.
