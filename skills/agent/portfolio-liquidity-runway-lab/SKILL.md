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
11. Convert local CSV rows into JSON schemas when source data arrives as spreadsheets:
   `portfolio-liquidity-runway-lab csv-import --portfolio-csv portfolio.csv --ledger-csv ledger.csv --out dist/csv-import`
12. Export packet review tables to deterministic CSV:
   `portfolio-liquidity-runway-lab csv-export --packet dist/packet/liquidity_packet.json --out dist/csv-export`
13. Lint JSON and CSV inputs before generating packets:
   `portfolio-liquidity-runway-lab input-lint --portfolio portfolio.json --ledger ledger.json --assumptions assumptions.json --portfolio-csv portfolio.csv --ledger-csv ledger.csv`
14. Write reproducible release checksums:
   `portfolio-liquidity-runway-lab bundle-checksums --root . --out docs/bundle-checksums`
15. Copy review evidence into an offline bundle:
   `portfolio-liquidity-runway-lab evidence-bundle --root . --out docs/evidence-bundle`
16. Export starter templates for a new offline user:
   `portfolio-liquidity-runway-lab template-pack --out docs/template-pack`
17. Run fixture diagnostics against bundled examples:
   `portfolio-liquidity-runway-lab fixture-doctor --out docs`
18. Export static no-JavaScript documentation:
   `portfolio-liquidity-runway-lab docs-export --out docs/static-docs`
19. Export the full command catalog:
   `portfolio-liquidity-runway-lab command-matrix --out docs/command-matrix`
20. Build the one-page release deck:
   `portfolio-liquidity-runway-lab release-deck --root . --out docs/release-deck`
21. Replay committed demos before release:
   `portfolio-liquidity-runway-lab golden-replay --root . --out docs/golden-replay`
22. Run the release validator before packaging:
   `portfolio-liquidity-runway-lab release-check --out docs`
23. Run `public-scan` before publishing generated docs or demos; it checks local path leakage, provider-token patterns, secret-like environment labels, and unsafe generated HTML.
24. For stress review, pass `--scenario stress` or another scenario defined in the assumptions JSON. For gallery, batch, and casebook review, pass `--scenarios base,stress,income_shock` or rely on bundled defaults.
25. Use `review-ledger`, `compare-history`, `static-dashboard`, `maturity-report`, and `release-manifest` for supporting checks.

## Output Expectations

Artifacts are deterministic JSON, spreadsheet-hardened CSV, Markdown, no-JavaScript HTML, scenario galleries, assumption audits, CSV import reports, CSV export manifests, input lint findings, checksum manifests, evidence bundles, template packs, batch comparisons, release-owner casebooks, schema guides, fixture diagnostics, static documentation bundles, command catalogs, golden replay summaries, release decks, artifact catalogs, release checks, and optional visual receipt Markdown. Review warnings are prompts to inspect assumptions, liquidity tiers, scheduled events, fees, yields, and forced-sale risks; they are not transaction instructions. Do not publish user-generated packets or evidence bundles unless personal balances, income, expenses, event labels, assumptions, and local paths have been reviewed and intentionally sanitized.
