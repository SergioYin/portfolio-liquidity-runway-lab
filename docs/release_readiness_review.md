# Release Readiness Review

Boundary: educational static analysis only. The project does not fetch live data, connect to brokers, place orders, or provide tax, legal, investment, buy, sell, or hold advice.

## Release Candidate Commands

Run from the repository root:

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
python -m portfolio_liquidity_runway_lab release-manifest --out docs/release_manifest.json
python -m portfolio_liquidity_runway_lab maturity-report --out docs/maturity_report.json
python -m portfolio_liquidity_runway_lab artifact-catalog --out docs
python -m portfolio_liquidity_runway_lab release-check --out docs
```

Optional manual demo:

```bash
tmpdir="$(mktemp -d)"
cd "$tmpdir"
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
```

## Maturity Rubric

Current maturity: alpha public utility.

| Area | Status | Notes |
| --- | --- | --- |
| Scope boundary | Ready | README, CLI outputs, generated packets, and docs state no live data, broker actions, orders, or advice. |
| Runtime dependency risk | Ready | Package has no runtime dependencies and uses the Python standard library. |
| Determinism | Ready | Packets and release manifest are deterministic for the same file tree and inputs. |
| Scenario gallery | Ready | `scenario-gallery` writes deterministic JSON, Markdown, and no-JavaScript HTML for bundled `base`, `stress`, `income_shock`, and `reserve_rebuild` scenarios. |
| Assumption audit | Ready | `assumption-audit` writes deterministic JSON and Markdown findings for liquidity tier completeness, nonnumeric values, suspicious yields or fees, missing scenarios, reserve thresholds, and scheduled event issues. |
| Batch compare | Ready | `batch-compare` writes deterministic JSON, Markdown, and no-JavaScript HTML comparing runway, reserves, and warnings across portfolio JSON files. |
| Casebook | Ready | `casebook` writes deterministic JSON, Markdown, and no-JavaScript HTML release-owner artifacts combining packet, scenario gallery, assumption audit, and batch compare summaries. |
| Artifact catalog | Ready | `artifact-catalog` records demo/docs file sizes, SHA256 hashes, and regeneration commands in deterministic JSON and Markdown. |
| Release check | Ready | `release-check` validates expected docs/demo/package files, public scan status, and generated HTML no-script requirements. |
| Visual receipt | Ready | `visual-receipt` writes compact deterministic Markdown linking packet artifacts, boundary text, bucket bars, and regeneration commands. |
| Cold start | Ready | `quickstart-check` copies packaged examples and builds a packet from an empty directory. |
| Test coverage | Basic | Unit tests cover analysis, static artifacts, CLI smoke paths, public metadata, README expectations, and manifest expectations. |
| Public scan | Basic | Scanner checks workflow files, binary-like artifacts, and common credential marker strings. It is a release aid, not a complete security audit. |
| Financial data safety | Ready | Inputs are local JSON only; packaged examples are synthetic. |
| Advice boundary | Ready | Outputs contain review prompts and warnings, not transaction instructions. |
| Packaging | Basic | `pyproject.toml`, package data, `MANIFEST.in`, and console script are present. |

## Release Notes Checklist

- Confirm `LICENSE` and `pyproject.toml` use neutral contributor metadata.
- Confirm `README.md` starts with purpose, target user, quickstart, example outputs, and boundaries.
- Regenerate `demo/visual_receipt.md` when changing bundled examples or receipt formatting.
- Regenerate `demo/scenario-gallery/` when changing bundled scenarios or gallery formatting.
- Regenerate `demo/assumption-audit/` when changing audit rules or bundled concentrated fixtures.
- Regenerate `demo/batch-compare/` when changing batch compare rendering or summary fields.
- Regenerate `demo/casebook/` when changing casebook summaries, bundled examples, or release-owner review fields.
- Regenerate `docs/artifact_catalog.*` after changing demo or docs artifacts.
- Regenerate `docs/release_check.*` after changing release expectations or generated HTML artifacts.
- Regenerate `docs/release_manifest.json` after adding or removing release files.
- Do not add `.github/workflows` for this release.
- Do not include large generated demo output directories in a source distribution.
