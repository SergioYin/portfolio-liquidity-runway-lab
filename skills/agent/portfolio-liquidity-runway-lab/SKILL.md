# portfolio-liquidity-runway-lab

Use this skill when a user needs static local portfolio liquidity runway artifacts from JSON inputs without live data, broker connections, orders, or advice.

## Workflow

1. Keep the boundary explicit: educational static analysis only, no live data, no broker actions, no buy/sell/hold recommendations, and no tax/legal/investment advice.
2. Prefer packaged examples when the user wants a demo or is in an empty working directory:
   `portfolio-liquidity-runway-lab quickstart-check --out liquidity-demo`
3. Build packet artifacts with:
   `portfolio-liquidity-runway-lab build-packet --portfolio portfolio.json --ledger ledger.json --assumptions assumptions.json --out dist/packet`
4. Build a scenario gallery when the user needs side-by-side assumption review:
   `portfolio-liquidity-runway-lab scenario-gallery --portfolio portfolio.json --ledger ledger.json --assumptions assumptions.json --out dist/scenario-gallery`
5. Build a compact receipt/showcase when the user needs a review handoff:
   `portfolio-liquidity-runway-lab visual-receipt --portfolio portfolio.json --ledger ledger.json --assumptions assumptions.json --out demo/visual_receipt.md`
6. For stress review, pass `--scenario stress` or another scenario defined in the assumptions JSON. For gallery review, pass `--scenarios base,stress,income_shock` or rely on bundled defaults.
7. Use `review-ledger`, `compare-history`, `static-dashboard`, `maturity-report`, `release-manifest`, and `public-scan` for supporting checks.

## Output Expectations

Artifacts are deterministic JSON, Markdown, no-JavaScript HTML, scenario galleries, and optional visual receipt Markdown. Review warnings are prompts to inspect assumptions, liquidity tiers, scheduled events, fees, yields, and forced-sale risks; they are not transaction instructions.
