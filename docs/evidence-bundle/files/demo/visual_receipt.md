# Visual Receipt: Synthetic household reserve portfolio

Scenario: `stress`

Boundary: Educational static analysis only. This tool uses local synthetic or user-supplied inputs, does not fetch live data, does not connect to brokers, does not place orders, and does not provide tax, legal, investment, buy, sell, or hold advice.

## Packet Linkage

- Packet JSON: `liquidity_packet.json`
- Packet Markdown: `liquidity_packet.md`
- Packet HTML: `liquidity_packet.html`

## Regeneration

```bash
portfolio-liquidity-runway-lab build-packet --out dist/packet --scenario stress
portfolio-liquidity-runway-lab visual-receipt --out demo/visual_receipt.md --scenario stress
```

## Snapshot

- Gross assets: $165,000.00
- Stress haircut assets: $133,460.00
- Effective monthly burn: $7,282.83
- Same-day reserve months: 4.51
- Same-day + one-week runway months: 10.4
- Thirty-day runway months: 12.97

## Liquidity View

| Tier | Stress value | Visual |
| --- | ---: | --- |
| Same day | $50,000.00 | `########################` |
| One week | $25,760.00 | `############............` |
| One month | $18,700.00 | `#########...............` |
| Locked or gated | $39,000.00 | `###################.....` |

## Review Signals

- Liquid balance turns negative in month 10; review whether one_month or locked holdings would be needed.
- Same-day reserve is 4.5 months, below the 6.0 month review threshold.
- Locked or gated assets exceed 35% of gross assets while burn is positive.
