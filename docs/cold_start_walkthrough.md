# Cold Start Walkthrough

This walkthrough starts from an empty working directory and uses only packaged synthetic examples.

Boundary: educational static analysis only. The tool uses local synthetic or user-supplied inputs, does not fetch live data, does not connect to brokers, does not place orders, and does not provide tax, legal, investment, buy, sell, or hold advice.

## Install Or Run Locally

From a source checkout:

```bash
python -m unittest discover -s tests
python -m portfolio_liquidity_runway_lab selfcheck
```

If installed as a package, use the console script:

```bash
portfolio-liquidity-runway-lab --version
```

## Build The Demo Packet

Run the quickstart from an empty directory:

```bash
mkdir -p /tmp/plrl-demo
cd /tmp/plrl-demo
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
portfolio-liquidity-runway-lab fixture-doctor --out liquidity-demo/fixture-doctor
portfolio-liquidity-runway-lab docs-export --root . --out liquidity-demo/static-docs
```

Expected files:

```text
liquidity-demo/portfolio.json
liquidity-demo/portfolio_concentrated.json
liquidity-demo/ledger.json
liquidity-demo/assumptions.json
liquidity-demo/history.json
liquidity-demo/packet/liquidity_packet.json
liquidity-demo/packet/liquidity_packet.md
liquidity-demo/packet/liquidity_packet.html
liquidity-demo/scenario-gallery/scenario_gallery.json
liquidity-demo/scenario-gallery/scenario_gallery.md
liquidity-demo/scenario-gallery/scenario_gallery.html
liquidity-demo/assumption-audit/assumption_audit.json
liquidity-demo/assumption-audit/assumption_audit.md
liquidity-demo/batch-compare/batch_compare.json
liquidity-demo/batch-compare/batch_compare.md
liquidity-demo/batch-compare/batch_compare.html
liquidity-demo/casebook/casebook.json
liquidity-demo/casebook/casebook.md
liquidity-demo/casebook/casebook.html
liquidity-demo/visual_receipt.md
liquidity-demo/schema-export/schema_guide.json
liquidity-demo/schema-export/schema_guide.md
liquidity-demo/fixture-doctor/fixture_doctor.json
liquidity-demo/fixture-doctor/fixture_doctor.md
liquidity-demo/static-docs/index.html
liquidity-demo/static-docs/index.md
```

## Review Supporting Outputs

```bash
portfolio-liquidity-runway-lab compare-history --history liquidity-demo/history.json
portfolio-liquidity-runway-lab review-ledger --ledger liquidity-demo/ledger.json
portfolio-liquidity-runway-lab static-dashboard --out liquidity-demo/dashboard --scenario stress
portfolio-liquidity-runway-lab scenario-gallery --out liquidity-demo/scenario-gallery
portfolio-liquidity-runway-lab assumption-audit --portfolio liquidity-demo/portfolio_concentrated.json --out liquidity-demo/assumption-audit
portfolio-liquidity-runway-lab batch-compare --portfolios-dir liquidity-demo/portfolios --scenarios base,stress --out liquidity-demo/batch-compare
portfolio-liquidity-runway-lab casebook --portfolios-dir liquidity-demo/portfolios --scenario stress --scenarios base,stress,income_shock --out liquidity-demo/casebook
portfolio-liquidity-runway-lab visual-receipt --out liquidity-demo/visual_receipt.md --scenario stress
portfolio-liquidity-runway-lab schema-export --out liquidity-demo/schema-export
portfolio-liquidity-runway-lab fixture-doctor --out liquidity-demo/fixture-doctor
portfolio-liquidity-runway-lab docs-export --root . --out liquidity-demo/static-docs
portfolio-liquidity-runway-lab artifact-catalog --root liquidity-demo
```

The packet, gallery, audit, batch compare, casebook, schema guide, fixture diagnosis, static docs, catalog, and visual receipt artifacts should be deterministic for the same inputs. HTML artifacts are static and contain no JavaScript.

## Public Readiness Checks

From the repository root:

```bash
python -m unittest discover -s tests
python -m portfolio_liquidity_runway_lab selfcheck
python -m portfolio_liquidity_runway_lab public-scan
python -m portfolio_liquidity_runway_lab maturity-report
python -m portfolio_liquidity_runway_lab scenario-gallery --out demo/scenario-gallery
python -m portfolio_liquidity_runway_lab assumption-audit --portfolio portfolio_liquidity_runway_lab/examples/portfolio_concentrated.json --out demo/assumption-audit
tmpdir="$(mktemp -d)"
cp portfolio_liquidity_runway_lab/examples/portfolio.json "$tmpdir/portfolio.json"
cp portfolio_liquidity_runway_lab/examples/portfolio_concentrated.json "$tmpdir/portfolio_concentrated.json"
python -m portfolio_liquidity_runway_lab batch-compare --portfolios-dir "$tmpdir" --scenarios base,stress --out demo/batch-compare
python -m portfolio_liquidity_runway_lab casebook --portfolios-dir "$tmpdir" --scenario stress --scenarios base,stress,income_shock --out demo/casebook
python -m portfolio_liquidity_runway_lab visual-receipt --out demo/visual_receipt.md --scenario stress
python -m portfolio_liquidity_runway_lab schema-export --out demo/schema-export
python -m portfolio_liquidity_runway_lab fixture-doctor --out demo/fixture-doctor --work-dir dist/fixture-doctor-work
python -m portfolio_liquidity_runway_lab docs-export --root . --out demo/static-docs
python -m portfolio_liquidity_runway_lab schema-export --out docs
python -m portfolio_liquidity_runway_lab fixture-doctor --out docs --work-dir dist/fixture-doctor-work
python -m portfolio_liquidity_runway_lab docs-export --root . --out docs/static-docs
python -m portfolio_liquidity_runway_lab release-manifest --out docs/release_manifest.json
python -m portfolio_liquidity_runway_lab maturity-report --out docs/maturity_report.json
python -m portfolio_liquidity_runway_lab artifact-catalog --out docs
python -m portfolio_liquidity_runway_lab release-check --out docs
```

All commands should exit with status 0 before a public release candidate is tagged.
