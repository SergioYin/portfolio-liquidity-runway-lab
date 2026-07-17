# Portfolio Liquidity Runway Lab v0.7.0 Release Deck

> Educational static analysis only. This tool uses local synthetic or user-supplied inputs, does not fetch live data, does not connect to brokers, does not place orders, and does not provide tax, legal, investment, buy, sell, or hold advice.

## Product Value

- Builds deterministic local liquidity runway packets from JSON and CSV inputs.
- Imports portfolio and ledger CSV rows into validated JSON schemas, then exports packet analysis back to reviewable CSV.
- Packages scenario, audit, batch comparison, casebook, schema, command, and replay evidence.
- Keeps outputs static and reviewable with no runtime dependencies and no JavaScript in generated HTML demos.

## Commands

| Command | Purpose |
| --- | --- |
| `build-packet` | Build the core liquidity runway packet. |
| `compare-history` | Compare reserve and burn snapshots over time. |
| `review-ledger` | Flag ledger review prompts and unusual scheduled events. |
| `static-dashboard` | Build the packet HTML dashboard without JavaScript. |
| `scenario-gallery` | Compare named scenarios side by side. |
| `assumption-audit` | Audit portfolio, ledger, and assumptions for review issues. |
| `batch-compare` | Compare multiple portfolio JSON files under shared scenarios. |
| `casebook` | Assemble packet, scenario, audit, and batch evidence for release owners. |
| `artifact-catalog` | Inventory demo and doc artifacts with SHA256 hashes. |
| `release-check` | Validate expected files, public scan, and no-script HTML. |
| `visual-receipt` | Write a compact Markdown review receipt. |
| `schema-export` | Export input and artifact schema documentation. |
| `csv-import` | Convert local portfolio and ledger CSV rows into validated JSON schemas. |
| `csv-export` | Export packet assets, runway rows, warnings, and bucket summaries as deterministic CSV. |
| `input-lint` | Strict lint for JSON and CSV inputs with remediation and schema references. |
| `fixture-doctor` | Run all workflows against isolated copied fixtures. |
| `docs-export` | Export compact static documentation bundle. |
| `command-matrix` | Export the full deterministic command catalog. |
| `golden-replay` | Regenerate committed demos into a temp directory and compare hashes/content. |
| `release-deck` | Build a one-page promotion and release evidence deck. |
| `quickstart-check` | Copy packaged examples and build a packet from an empty directory. |
| `selfcheck` | Run deterministic smoke checks against bundled examples. |
| `public-scan` | Scan repo tree for public-release concerns. |
| `release-manifest` | Emit deterministic release file inventory. |
| `maturity-report` | Report basic repo maturity checks. |

## Evidence

- Release check: `fail`
- Maturity score: `32/32`
- Cataloged artifacts: `187`
- No-script HTML files: `26`

## Risks

- Outputs depend on supplied local JSON quality and should be reviewed against source records.
- Static scenarios are assumptions, not predictions or transaction instructions.
- No live integrations means users must update inputs manually before each review.

## Next Roadmap

- Expand fixture doctor coverage for malformed batch directories and scenario edge cases.
- Add signed release bundle checksums for downstream archival workflows.
- Broaden CSV templates for multi-currency review workflows without adding live integrations.
