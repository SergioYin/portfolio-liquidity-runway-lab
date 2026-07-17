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
5. Audit input quality before relying on packet outputs:
   `portfolio-liquidity-runway-lab assumption-audit --portfolio portfolio.json --ledger ledger.json --assumptions assumptions.json --out dist/assumption-audit`
6. Compare multiple portfolios against the same ledger and assumptions:
   `portfolio-liquidity-runway-lab batch-compare --portfolios-dir portfolios --ledger ledger.json --assumptions assumptions.json --scenarios base,stress --out dist/batch-compare`
7. Build a compact receipt/showcase when the user needs a review handoff:
   `portfolio-liquidity-runway-lab visual-receipt --portfolio portfolio.json --ledger ledger.json --assumptions assumptions.json --out demo/visual_receipt.md`
8. Build a release-owner casebook when the user needs one handoff artifact family:
   `portfolio-liquidity-runway-lab casebook --portfolio portfolio.json --ledger ledger.json --assumptions assumptions.json --portfolios-dir portfolios --scenario stress --scenarios base,stress,income_shock --out dist/casebook`
9. Catalog generated docs and demo files before release:
   `portfolio-liquidity-runway-lab artifact-catalog --out docs`
10. Export schema guides for handoff and integration review:
   `portfolio-liquidity-runway-lab schema-export --out docs`
11. Run fixture diagnostics against bundled examples:
   `portfolio-liquidity-runway-lab fixture-doctor --out docs`
12. Export static no-JavaScript documentation:
   `portfolio-liquidity-runway-lab docs-export --out docs/static-docs`
13. Run the release validator before packaging:
   `portfolio-liquidity-runway-lab release-check --out docs`
14. For stress review, pass `--scenario stress` or another scenario defined in the assumptions JSON. For gallery, batch, and casebook review, pass `--scenarios base,stress,income_shock` or rely on bundled defaults.
15. Use `review-ledger`, `compare-history`, `static-dashboard`, `maturity-report`, `release-manifest`, and `public-scan` for supporting checks.

## Output Expectations

Artifacts are deterministic JSON, Markdown, no-JavaScript HTML, scenario galleries, assumption audits, batch comparisons, release-owner casebooks, schema guides, fixture diagnostics, static documentation bundles, artifact catalogs, release checks, and optional visual receipt Markdown. Review warnings are prompts to inspect assumptions, liquidity tiers, scheduled events, fees, yields, and forced-sale risks; they are not transaction instructions.
