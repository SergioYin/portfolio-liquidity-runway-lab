# Boundary And Risks

Educational static analysis only. This tool uses local synthetic or user-supplied inputs, does not fetch live data, does not connect to brokers, does not place orders, and does not provide tax, legal, investment, buy, sell, or hold advice.

## Review Boundary

- Inputs are local synthetic or user-supplied files.
- Outputs are deterministic review artifacts, not instructions to transact.
- Reviewers must verify liquidity tiers, scheduled events, fees, yields, and scenario assumptions against source records.

## Residual Risks

- Stale user inputs can make a packet misleading even when all checks pass.
- Static scenarios do not model every market, tax, legal, custody, or operational constraint.
- Public scan and release check are release aids, not complete security or compliance audits.
