# portfolio-liquidity-runway-lab

Build deterministic local liquidity runway packets from JSON portfolio, ledger, and assumption inputs.

For analysts, founders, operators, and finance teams who need static review packets for liquidity assumptions and runway discussions.

Boundary: educational static analysis only. The tool uses local synthetic or user-supplied inputs, does not fetch live data, does not connect to brokers, does not place orders, and does not provide tax, legal, investment, buy, sell, or hold advice.

## Quickstart

From an empty working directory after installation:

```bash
portfolio-liquidity-runway-lab quickstart-check --out liquidity-demo
portfolio-liquidity-runway-lab build-packet --out liquidity-demo/packet --scenario stress
portfolio-liquidity-runway-lab visual-receipt --out liquidity-demo/visual_receipt.md --scenario stress
```

Example outputs:

- `liquidity-demo/portfolio.json`, `ledger.json`, `assumptions.json`, and `history.json`
- `liquidity-demo/packet/liquidity_packet.json`
- `liquidity-demo/packet/liquidity_packet.md`
- `liquidity-demo/packet/liquidity_packet.html`
- `liquidity-demo/visual_receipt.md`

The packet contains liquidity buckets, stress-haircut values, monthly runway rows, forced-sale warnings, and review prompts. The visual receipt is a compact Markdown showcase that links the packet artifacts, boundary text, liquidity bucket bars, and regeneration commands. Open `liquidity-demo/packet/liquidity_packet.html`, inspect `demo/visual_receipt.md`, or run supporting checks:

```bash
portfolio-liquidity-runway-lab compare-history
portfolio-liquidity-runway-lab review-ledger
portfolio-liquidity-runway-lab selfcheck
portfolio-liquidity-runway-lab public-scan
portfolio-liquidity-runway-lab maturity-report
```

For local development from the repo:

```bash
python -m unittest discover -s tests
python -m portfolio_liquidity_runway_lab selfcheck
```

## Commands

- `build-packet`: build JSON, Markdown, and no-JavaScript HTML packet artifacts.
- `compare-history`: compare reserve-month and burn snapshots.
- `review-ledger`: produce ledger flags and review prompts.
- `static-dashboard`: build the static HTML dashboard artifact.
- `visual-receipt`: write a compact deterministic Markdown receipt for packet review.
- `quickstart-check`: copy packaged synthetic examples and build a packet.
- `selfcheck`: run a smoke test against packaged examples.
- `public-scan`: scan a repo tree for public-release concerns.
- `release-manifest`: emit deterministic release file inventory.
- `maturity-report`: check basic repo readiness items.

## Input Shape

The CLI accepts local JSON files for portfolio assets, ledger assumptions, and scenarios. If paths are omitted, packaged synthetic examples are used.

Portfolio assets include:

- `name`
- `value`
- `liquidity_tier`: `same_day`, `one_week`, `one_month`, or `locked`
- `annual_yield_rate`
- `annual_fee_rate`

Ledger inputs include monthly income, monthly expenses, and scheduled inflow or outflow events by month. Assumptions include reserve thresholds, scenario expense and income multipliers, and liquidity haircuts.

## Boundaries

This project deliberately does not:

- fetch market prices, account balances, rates, or other live data
- connect to brokerage, banking, custodian, or order systems
- recommend asset purchases, sales, holds, allocations, optimizations, or predictions
- provide tax, legal, accounting, or investment advice

Use the outputs as review packets for local records and professional discussion, not as instructions to transact.
