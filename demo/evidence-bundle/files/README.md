# portfolio-liquidity-runway-lab

Build deterministic local liquidity runway packets from JSON portfolio, ledger, and assumption inputs.

For analysts, founders, operators, and finance teams who need static review packets for liquidity assumptions and runway discussions.

Boundary: educational static analysis only. The tool uses local synthetic or user-supplied inputs, does not fetch live data, does not connect to brokers, does not place orders, and does not provide tax, legal, investment, buy, sell, or hold advice.

## Quickstart

From an empty working directory after installation:

```bash
portfolio-liquidity-runway-lab quickstart-check --out liquidity-demo
portfolio-liquidity-runway-lab build-packet --out liquidity-demo/packet --scenario stress
portfolio-liquidity-runway-lab scenario-gallery --out liquidity-demo/scenario-gallery
portfolio-liquidity-runway-lab assumption-audit --portfolio liquidity-demo/portfolio_concentrated.json --out liquidity-demo/assumption-audit
mkdir -p liquidity-demo/portfolios
cp liquidity-demo/portfolio.json liquidity-demo/portfolios/portfolio.json
cp liquidity-demo/portfolio_concentrated.json liquidity-demo/portfolios/portfolio_concentrated.json
portfolio-liquidity-runway-lab batch-compare --portfolios-dir liquidity-demo/portfolios --scenarios base,stress --out liquidity-demo/batch-compare
portfolio-liquidity-runway-lab casebook --portfolios-dir liquidity-demo/portfolios --scenario stress --scenarios base,stress,income_shock --out liquidity-demo/casebook
portfolio-liquidity-runway-lab visual-receipt --out liquidity-demo/visual_receipt.md --scenario stress
portfolio-liquidity-runway-lab schema-export --out liquidity-demo/schema-export
portfolio-liquidity-runway-lab csv-import --portfolio-csv liquidity-demo/portfolio.csv --ledger-csv liquidity-demo/ledger.csv --out liquidity-demo/csv-import
portfolio-liquidity-runway-lab build-packet --portfolio liquidity-demo/csv-import/portfolio.json --ledger liquidity-demo/csv-import/ledger.json --out liquidity-demo/csv-packet
portfolio-liquidity-runway-lab csv-export --packet liquidity-demo/csv-packet/liquidity_packet.json --out liquidity-demo/csv-export
portfolio-liquidity-runway-lab input-lint --portfolio liquidity-demo/portfolio.json --ledger liquidity-demo/ledger.json --assumptions liquidity-demo/assumptions.json --portfolio-csv liquidity-demo/portfolio.csv --ledger-csv liquidity-demo/ledger.csv
portfolio-liquidity-runway-lab fixture-doctor --out liquidity-demo/fixture-doctor
portfolio-liquidity-runway-lab docs-export --root . --out liquidity-demo/static-docs
portfolio-liquidity-runway-lab command-matrix --out liquidity-demo/command-matrix
portfolio-liquidity-runway-lab release-deck --root . --out liquidity-demo/release-deck
portfolio-liquidity-runway-lab bundle-checksums --root . --out liquidity-demo/bundle-checksums
portfolio-liquidity-runway-lab evidence-bundle --root . --out liquidity-demo/evidence-bundle
portfolio-liquidity-runway-lab template-pack --out liquidity-demo/template-pack
portfolio-liquidity-runway-lab artifact-catalog --root liquidity-demo
portfolio-liquidity-runway-lab golden-replay --root . --out liquidity-demo/golden-replay
portfolio-liquidity-runway-lab release-check --root .
```

Example outputs:

- `liquidity-demo/portfolio.json`, `portfolio_concentrated.json`, `ledger.json`, `assumptions.json`, `history.json`, `portfolio.csv`, and `ledger.csv`
- `liquidity-demo/packet/liquidity_packet.json`
- `liquidity-demo/packet/liquidity_packet.md`
- `liquidity-demo/packet/liquidity_packet.html`
- `liquidity-demo/scenario-gallery/scenario_gallery.json`
- `liquidity-demo/scenario-gallery/scenario_gallery.md`
- `liquidity-demo/scenario-gallery/scenario_gallery.html`
- `liquidity-demo/assumption-audit/assumption_audit.json`
- `liquidity-demo/assumption-audit/assumption_audit.md`
- `liquidity-demo/batch-compare/batch_compare.json`
- `liquidity-demo/batch-compare/batch_compare.md`
- `liquidity-demo/batch-compare/batch_compare.html`
- `liquidity-demo/casebook/casebook.json`
- `liquidity-demo/casebook/casebook.md`
- `liquidity-demo/casebook/casebook.html`
- `liquidity-demo/visual_receipt.md`
- `liquidity-demo/schema-export/schema_guide.json`
- `liquidity-demo/schema-export/schema_guide.md`
- `liquidity-demo/csv-import/portfolio.json`
- `liquidity-demo/csv-import/ledger.json`
- `liquidity-demo/csv-import/import_report.json`
- `liquidity-demo/csv-import/import_report.md`
- `liquidity-demo/csv-export/assets.csv`
- `liquidity-demo/csv-export/runway.csv`
- `liquidity-demo/csv-export/warnings.csv`
- `liquidity-demo/csv-export/bucket_summaries.csv`
- `liquidity-demo/csv-export/export_manifest.json`
- `liquidity-demo/csv-export/export_manifest.md`
- `liquidity-demo/fixture-doctor/fixture_doctor.json`
- `liquidity-demo/fixture-doctor/fixture_doctor.md`
- `liquidity-demo/static-docs/index.html`
- `liquidity-demo/static-docs/index.md`
- `liquidity-demo/command-matrix/command_matrix.json`
- `liquidity-demo/command-matrix/command_matrix.md`
- `liquidity-demo/command-matrix/command_matrix.html`
- `liquidity-demo/release-deck/release_deck.md`
- `liquidity-demo/release-deck/release_deck.html`
- `liquidity-demo/bundle-checksums/SHA256SUMS.txt`
- `liquidity-demo/bundle-checksums/bundle_manifest.json`
- `liquidity-demo/bundle-checksums/bundle_manifest.md`
- `liquidity-demo/evidence-bundle/index.md`
- `liquidity-demo/evidence-bundle/index.html`
- `liquidity-demo/evidence-bundle/SHA256SUMS.txt`
- `liquidity-demo/evidence-bundle/evidence_manifest.json`
- `liquidity-demo/template-pack/README.md`
- `liquidity-demo/template-pack/template_manifest.json`
- `liquidity-demo/template-pack/portfolio.csv`, `ledger.csv`, `portfolio.json`, `ledger.json`, and `assumptions.json`
- `liquidity-demo/golden-replay/golden_replay.json`
- `liquidity-demo/golden-replay/golden_replay.md`

The packet contains liquidity buckets, stress-haircut values, monthly runway rows, forced-sale warnings, and review prompts. The scenario gallery compares bundled `base`, `stress`, `income_shock`, and `reserve_rebuild` scenarios across deterministic JSON, Markdown, and no-JavaScript HTML artifacts. `assumption-audit` validates portfolio, ledger, and assumptions JSON for liquidity tier completeness, nonnumeric values, suspicious yields or fees, missing scenarios, reserve thresholds, and scheduled event issues. `csv-import` converts local portfolio and ledger CSV rows into the existing JSON schemas with a deterministic import report. `csv-export` writes packet assets, runway rows, warnings, and bucket summaries as deterministic CSV with a manifest. `input-lint` strictly validates JSON and CSV inputs with remediation messages, schema references, and nonzero failure exits. `batch-compare` compares runway, reserves, and warnings across a directory of portfolio JSON files that share one ledger and assumptions file. `casebook` combines packet, scenario gallery, assumption audit, and batch compare summaries into deterministic JSON, Markdown, and no-JavaScript HTML release-owner artifacts. `schema-export` writes deterministic JSON and Markdown guides for every supported input file and output artifact. `fixture-doctor` copies examples into an isolated work directory, runs the command plan, and writes pass/fail diagnosis artifacts. `docs-export` creates a compact no-JavaScript documentation bundle linking README summary, command matrix, boundaries, demos, and release evidence. `command-matrix` writes the full deterministic JSON, Markdown, and no-JavaScript HTML command catalog with purpose, inputs, outputs, demo command, and risk boundary for every CLI command. `release-deck` builds a deterministic Markdown and no-JavaScript HTML one-page promotion/release deck covering product value, commands, evidence, risks, and roadmap. `bundle-checksums` writes deterministic `SHA256SUMS.txt` plus JSON and Markdown manifests for release files, docs, demos, and wheel/sdist files when present. `evidence-bundle` copies selected review artifacts into a deterministic offline bundle with index pages, checksums, command replay notes, and boundary/risk notes. `template-pack` exports clean CSV and JSON starter templates with a README for creating an offline portfolio, ledger, and assumptions set. `golden-replay` regenerates key demo artifacts into a replay directory and compares committed demo hashes/content with JSON and Markdown pass/fail summaries. `artifact-catalog` walks demo/docs outputs and records file sizes, SHA256 hashes, and regeneration commands. `release-check` validates expected package/docs/demo files, public scan results, and generated HTML script tags. The visual receipt is a compact Markdown showcase that links the packet artifacts, boundary text, liquidity bucket bars, and regeneration commands. Open `liquidity-demo/packet/liquidity_packet.html`, inspect `liquidity-demo/scenario-gallery/scenario_gallery.html`, inspect `liquidity-demo/batch-compare/batch_compare.html`, inspect `liquidity-demo/casebook/casebook.html`, inspect `liquidity-demo/static-docs/index.html`, inspect `liquidity-demo/command-matrix/command_matrix.html`, inspect `liquidity-demo/release-deck/release_deck.html`, inspect `liquidity-demo/evidence-bundle/index.html`, inspect `demo/visual_receipt.md`, or run supporting checks:

```bash
portfolio-liquidity-runway-lab compare-history
portfolio-liquidity-runway-lab review-ledger
portfolio-liquidity-runway-lab scenario-gallery
portfolio-liquidity-runway-lab assumption-audit
portfolio-liquidity-runway-lab batch-compare --portfolios-dir liquidity-demo/portfolios
portfolio-liquidity-runway-lab casebook --portfolios-dir liquidity-demo/portfolios
portfolio-liquidity-runway-lab schema-export --out docs
portfolio-liquidity-runway-lab csv-import --out demo/csv-import
portfolio-liquidity-runway-lab build-packet --out demo/csv-export-packet --scenario stress
portfolio-liquidity-runway-lab csv-export --packet demo/csv-export-packet/liquidity_packet.json --out demo/csv-export
portfolio-liquidity-runway-lab input-lint
portfolio-liquidity-runway-lab fixture-doctor --out docs
portfolio-liquidity-runway-lab docs-export --out docs/static-docs
portfolio-liquidity-runway-lab command-matrix --out docs/command-matrix
portfolio-liquidity-runway-lab release-deck --root . --out docs/release-deck
portfolio-liquidity-runway-lab bundle-checksums --root . --out docs/bundle-checksums
portfolio-liquidity-runway-lab evidence-bundle --root . --out docs/evidence-bundle
portfolio-liquidity-runway-lab template-pack --out docs/template-pack
portfolio-liquidity-runway-lab artifact-catalog --out docs
portfolio-liquidity-runway-lab golden-replay --root . --out docs/golden-replay
portfolio-liquidity-runway-lab release-check --out docs
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
- `scenario-gallery`: build deterministic JSON, Markdown, and no-JavaScript HTML gallery artifacts for at least three named scenarios.
- `assumption-audit`: validate portfolio, ledger, and assumptions JSON and emit deterministic JSON and Markdown findings.
- `batch-compare`: run selected scenarios across a directory of portfolio JSON files and emit deterministic JSON, Markdown, and no-JavaScript HTML.
- `casebook`: combine packet, scenario gallery, assumption audit, and batch compare summaries into deterministic release-owner JSON, Markdown, and no-JavaScript HTML.
- `artifact-catalog`: walk demo/docs outputs and emit deterministic JSON and Markdown with file sizes, SHA256 hashes, and regeneration commands.
- `release-check`: validate expected package/docs/demo files, public scan status, and generated HTML no-script requirements.
- `visual-receipt`: write a compact deterministic Markdown receipt for packet review.
- `schema-export`: export deterministic JSON and Markdown schema guides for supported inputs and artifacts.
- `csv-import`: convert local portfolio and ledger CSV rows into validated JSON schemas plus an import report.
- `csv-export`: export packet assets, runway rows, warnings, and bucket summaries into deterministic CSV plus a manifest.
- `input-lint`: strictly validate JSON and CSV inputs with remediation messages and schema references.
- `bundle-checksums`: write deterministic `SHA256SUMS.txt` plus JSON and Markdown manifests for release files and built distributions when present.
- `evidence-bundle`: copy selected docs and demo evidence into a deterministic offline review bundle with indexes, checksums, replay notes, and boundary/risk notes.
- `template-pack`: export clean CSV and JSON starter templates for a new user to create their own offline portfolio, ledger, and assumptions.
- `fixture-doctor`: copy examples to a work directory, run the command plan, and write pass/fail JSON and Markdown diagnosis.
- `docs-export`: export a compact static no-JavaScript documentation bundle.
- `command-matrix`: export deterministic JSON, Markdown, and no-JavaScript HTML command catalog with purpose, inputs, outputs, demo command, and risk boundary for every CLI command.
- `golden-replay`: regenerate key demo artifacts and compare SHA256/content against committed demos with JSON and Markdown pass/fail summaries.
- `release-deck`: build a one-page deterministic Markdown and no-JavaScript HTML promotion/release deck.
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

Ledger inputs include monthly income, monthly expenses, and scheduled inflow or outflow events by month. Assumptions include reserve thresholds, scenario expense and income multipliers, and liquidity haircuts. CSV imports use `portfolio.csv` columns `name,value,liquidity_tier,annual_yield_rate,annual_fee_rate` and `ledger.csv` columns `record_type,monthly_income,monthly_expenses,month,type,label,amount`.

## Boundaries

This project deliberately does not:

- fetch market prices, account balances, rates, or other live data
- connect to brokerage, banking, custodian, or order systems
- recommend asset purchases, sales, holds, allocations, optimizations, or predictions
- provide tax, legal, accounting, or investment advice

Use the outputs as review packets for local records and professional discussion, not as instructions to transact.
