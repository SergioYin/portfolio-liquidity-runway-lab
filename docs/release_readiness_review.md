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
python -m portfolio_liquidity_runway_lab schema-export --out demo/schema-export
python -m portfolio_liquidity_runway_lab fixture-doctor --out demo/fixture-doctor --work-dir dist/fixture-doctor-work
python -m portfolio_liquidity_runway_lab docs-export --root . --out demo/static-docs
python -m portfolio_liquidity_runway_lab bundle-checksums --root . --out demo/bundle-checksums
python -m portfolio_liquidity_runway_lab evidence-bundle --root . --out demo/evidence-bundle
python -m portfolio_liquidity_runway_lab template-pack --out demo/template-pack
python -m portfolio_liquidity_runway_lab schema-export --out docs
python -m portfolio_liquidity_runway_lab fixture-doctor --out docs --work-dir dist/fixture-doctor-work
python -m portfolio_liquidity_runway_lab docs-export --root . --out docs/static-docs
python -m portfolio_liquidity_runway_lab bundle-checksums --root . --out docs/bundle-checksums
python -m portfolio_liquidity_runway_lab evidence-bundle --root . --out docs/evidence-bundle
python -m portfolio_liquidity_runway_lab template-pack --out docs/template-pack
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
portfolio-liquidity-runway-lab schema-export --out liquidity-demo/schema-export
portfolio-liquidity-runway-lab bundle-checksums --root . --out liquidity-demo/bundle-checksums
portfolio-liquidity-runway-lab evidence-bundle --root . --out liquidity-demo/evidence-bundle
portfolio-liquidity-runway-lab template-pack --out liquidity-demo/template-pack
portfolio-liquidity-runway-lab fixture-doctor --out liquidity-demo/fixture-doctor
portfolio-liquidity-runway-lab docs-export --root . --out liquidity-demo/static-docs
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
| Schema guide | Ready | `schema-export` writes deterministic JSON and Markdown guides for every supported input file and output artifact family. |
| Fixture diagnosis | Ready | `fixture-doctor` copies examples to a work directory, validates the command plan, and writes pass/fail JSON and Markdown diagnosis. |
| Static docs | Ready | `docs-export` writes compact no-JavaScript HTML and Markdown docs linking README summary, command matrix, boundaries, demos, and release evidence. |
| Artifact catalog | Ready | `artifact-catalog` records demo/docs file sizes, SHA256 hashes, and regeneration commands in deterministic JSON and Markdown. |
| Bundle checksums | Ready | `bundle-checksums` writes deterministic SHA256SUMS plus JSON and Markdown manifests for source files, docs, demos, and built distributions when present. |
| Evidence bundle | Ready | `evidence-bundle` copies selected review docs and demo artifacts into an offline bundle with index pages, checksums, command replay notes, and boundary/risk notes. |
| Template pack | Ready | `template-pack` writes lintable CSV and JSON starters plus a README and manifest for offline user setup. |
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
- Regenerate `demo/schema-export/` and `docs/schema_guide.*` when changing schemas, command metadata, or artifact fields.
- Regenerate `demo/fixture-doctor/` and `docs/fixture_doctor.*` when changing command behavior or bundled examples.
- Regenerate `demo/static-docs/` and `docs/static-docs/` when changing README, command matrix, boundary text, demos, or release evidence.
- Regenerate `docs/artifact_catalog.*` after changing demo or docs artifacts.
- Regenerate `demo/bundle-checksums/` and `docs/bundle-checksums/` after changing release files or built distributions.
- Regenerate `demo/evidence-bundle/` and `docs/evidence-bundle/` after changing review docs, demo evidence, replay notes, or boundary text.
- Regenerate `demo/template-pack/` and `docs/template-pack/` after changing starter input schemas or CSV expectations.
- Regenerate `docs/release_check.*` after changing release expectations or generated HTML artifacts.
- Regenerate `docs/release-deck/` and `demo/release-deck/` after `release-check` so the deck reports the current release-check status.
- Regenerate `docs/release_manifest.json` after adding or removing release files.
- Run `public-scan --root .` before publishing and resolve local path leakage, provider-token patterns, secret-like environment labels, and unsafe generated HTML findings.
- Do not add `.github/workflows` for this release.
- Do not include large generated demo output directories in a source distribution.
- Wheel-install smoke documentation: build with `python -m build`, create a clean virtual environment, install the generated wheel with `python -m pip install dist/portfolio_liquidity_runway_lab-0.10.0-py3-none-any.whl`, then run `portfolio-liquidity-runway-lab selfcheck`, `portfolio-liquidity-runway-lab template-pack --out release-smoke/templates`, and `portfolio-liquidity-runway-lab quickstart-check --out release-smoke/quickstart`.
