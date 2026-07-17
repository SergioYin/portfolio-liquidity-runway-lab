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
portfolio-liquidity-runway-lab visual-receipt --out liquidity-demo/visual_receipt.md --scenario stress
```

Expected files:

```text
liquidity-demo/portfolio.json
liquidity-demo/ledger.json
liquidity-demo/assumptions.json
liquidity-demo/history.json
liquidity-demo/packet/liquidity_packet.json
liquidity-demo/packet/liquidity_packet.md
liquidity-demo/packet/liquidity_packet.html
liquidity-demo/visual_receipt.md
```

## Review Supporting Outputs

```bash
portfolio-liquidity-runway-lab compare-history --history liquidity-demo/history.json
portfolio-liquidity-runway-lab review-ledger --ledger liquidity-demo/ledger.json
portfolio-liquidity-runway-lab static-dashboard --out liquidity-demo/dashboard --scenario stress
portfolio-liquidity-runway-lab visual-receipt --out liquidity-demo/visual_receipt.md --scenario stress
```

The JSON, Markdown, and visual receipt artifacts should be deterministic for the same inputs. The HTML artifact is static and contains no JavaScript.

## Public Readiness Checks

From the repository root:

```bash
python -m unittest discover -s tests
python -m portfolio_liquidity_runway_lab selfcheck
python -m portfolio_liquidity_runway_lab public-scan
python -m portfolio_liquidity_runway_lab maturity-report
python -m portfolio_liquidity_runway_lab release-manifest --out docs/release_manifest.json
```

All commands should exit with status 0 before a public release candidate is tagged.
