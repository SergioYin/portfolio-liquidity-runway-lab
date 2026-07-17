# Release Readiness Review

Boundary: educational static analysis only. The project does not fetch live data, connect to brokers, place orders, or provide tax, legal, investment, buy, sell, or hold advice.

## Release Candidate Commands

Run from the repository root:

```bash
python -m unittest discover -s tests
python -m portfolio_liquidity_runway_lab selfcheck
python -m portfolio_liquidity_runway_lab public-scan
python -m portfolio_liquidity_runway_lab maturity-report
python -m portfolio_liquidity_runway_lab visual-receipt --out demo/visual_receipt.md --scenario stress
python -m portfolio_liquidity_runway_lab release-manifest --out docs/release_manifest.json
```

Optional manual demo:

```bash
tmpdir="$(mktemp -d)"
cd "$tmpdir"
portfolio-liquidity-runway-lab quickstart-check --out liquidity-demo
portfolio-liquidity-runway-lab build-packet --out liquidity-demo/packet --scenario stress
portfolio-liquidity-runway-lab visual-receipt --out liquidity-demo/visual_receipt.md --scenario stress
```

## Maturity Rubric

Current maturity: alpha public utility.

| Area | Status | Notes |
| --- | --- | --- |
| Scope boundary | Ready | README, CLI outputs, generated packets, and docs state no live data, broker actions, orders, or advice. |
| Runtime dependency risk | Ready | Package has no runtime dependencies and uses the Python standard library. |
| Determinism | Ready | Packets and release manifest are deterministic for the same file tree and inputs. |
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
- Regenerate `docs/release_manifest.json` after adding or removing release files.
- Do not add `.github/workflows` for this release.
- Do not include large generated demo output directories in a source distribution.
