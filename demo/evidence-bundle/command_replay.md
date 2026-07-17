# Command Replay Notes

Run from the repository root to refresh the review evidence:

```bash
python -m portfolio_liquidity_runway_lab selfcheck
python -m portfolio_liquidity_runway_lab scenario-gallery --out demo/scenario-gallery
python -m portfolio_liquidity_runway_lab assumption-audit --portfolio portfolio_liquidity_runway_lab/examples/portfolio_concentrated.json --out demo/assumption-audit
python -m portfolio_liquidity_runway_lab batch-compare --portfolios-dir demo/batch-inputs --scenarios base,stress --out demo/batch-compare
python -m portfolio_liquidity_runway_lab casebook --portfolios-dir demo/batch-inputs --scenario stress --scenarios base,stress,income_shock --out demo/casebook
python -m portfolio_liquidity_runway_lab schema-export --out docs
python -m portfolio_liquidity_runway_lab command-matrix --out docs/command-matrix
python -m portfolio_liquidity_runway_lab golden-replay --root . --out docs/golden-replay
python -m portfolio_liquidity_runway_lab release-deck --root . --out docs/release-deck
python -m portfolio_liquidity_runway_lab artifact-catalog --out docs
python -m portfolio_liquidity_runway_lab bundle-checksums --root . --out docs/bundle-checksums
python -m portfolio_liquidity_runway_lab evidence-bundle --root . --out docs/evidence-bundle
python -m portfolio_liquidity_runway_lab template-pack --out docs/template-pack
python -m portfolio_liquidity_runway_lab release-check --out docs
```
