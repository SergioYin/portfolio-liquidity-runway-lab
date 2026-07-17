# Cold Start User Audit: v0.8.0

Audit date: 2026-07-18
Repository: `portfolio-liquidity-runway-lab`
Version audited: `0.8.0`
Audit stance: first-time user starting from the README, then verifying CLI behavior, core implementation, tests, docs, demos, and generated evidence.

Boundary observed throughout: educational static analysis only; local synthetic or user-supplied files; no live data, broker connection, order placement, or tax, legal, investment, buy, sell, or hold advice.

## Sources Reviewed

- `README.md`: primary entry point, quickstart, command list, input shape, boundaries.
- `pyproject.toml`: package metadata, version, console script, runtime dependencies.
- `portfolio_liquidity_runway_lab/cli.py`: argparse surface and command stdout behavior.
- `portfolio_liquidity_runway_lab/core.py`: packet generation, validation, release checks, evidence builders, boundary text.
- `portfolio_liquidity_runway_lab/examples/*`: bundled JSON and CSV starter inputs.
- `tests/test_cli.py`: command-level smoke, determinism, no-script, lint, public-scan coverage.
- `tests/test_core.py`: core analysis, builder determinism, release manifest, maturity coverage.
- `docs/cold_start_walkthrough.md`: documented empty-directory walkthrough.
- `docs/release_readiness_review.md`: release-owner command plan and maturity rubric.
- `docs/command-matrix/command_matrix.md`: complete command catalog.
- `docs/evidence-bundle/boundary_risks.md`: residual risk notes.
- `docs/golden-replay/golden_replay.md`: committed-vs-regenerated evidence comparison.
- `docs/release_check.md`: generated release check summary.
- `demo/visual_receipt.md`, `demo/casebook/casebook.md`, `demo/csv-import/import_report.md`: representative committed user-facing artifacts.

## First 10 Minute Walkthrough

### Minute 0-1: Identify What This Is

The README opens clearly: `README.md` describes a deterministic local liquidity runway packet builder from JSON portfolio, ledger, and assumptions inputs. It immediately names the target users and states the boundary before the quickstart. That is strong for a finance-adjacent tool.

Friction: the first command block is long. A first-time analyst who wants "show me the packet" sees more than twenty commands before seeing a minimal path. The README does not visually separate "first useful packet" from "full release evidence pack."

### Minute 1-2: Check Installation Shape

`pyproject.toml` confirms:

- Package name: `portfolio-liquidity-runway-lab`
- Version: `0.8.0`
- Console script: `portfolio-liquidity-runway-lab = "portfolio_liquidity_runway_lab.cli:main"`
- Runtime dependencies: none
- Python requirement: `>=3.9`

This is favorable for cold start because the tool should run in a plain Python environment without dependency resolution surprises.

### Minute 2-4: Run Discovery Commands

Command tried:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m portfolio_liquidity_runway_lab --version
```

Observed output:

```text
portfolio-liquidity-runway-lab 0.8.0
```

Command tried:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m portfolio_liquidity_runway_lab --help
```

Observed output shape: argparse help lists all 28 commands, including `build-packet`, `quickstart-check`, `input-lint`, `template-pack`, `casebook`, `golden-replay`, `release-check`, and `maturity-report`.

Friction: the help output is complete but dense. It has no "start here" grouping, so cold users must infer that `quickstart-check`, `build-packet`, `input-lint`, and `template-pack` are the onboarding commands, while `release-deck`, `bundle-checksums`, and `golden-replay` are release-owner commands.

### Minute 4-6: Empty Directory Quickstart

Command tried from `<tmp-workdir>`:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=<repo> \
  python -m portfolio_liquidity_runway_lab quickstart-check --out liquidity-demo
```

Observed output:

```json
{
  "boundary": "Educational static analysis only. This tool uses local synthetic or user-supplied inputs, does not fetch live data, does not connect to brokers, does not place orders, and does not provide tax, legal, investment, buy, sell, or hold advice.",
  "examples": "liquidity-demo",
  "packet": "liquidity-demo/packet",
  "status": "ok"
}
```

Expected artifacts were created:

- `liquidity-demo/portfolio.json`
- `liquidity-demo/portfolio_concentrated.json`
- `liquidity-demo/ledger.json`
- `liquidity-demo/assumptions.json`
- `liquidity-demo/history.json`
- `liquidity-demo/portfolio.csv`
- `liquidity-demo/ledger.csv`
- `liquidity-demo/packet/liquidity_packet.json`
- `liquidity-demo/packet/liquidity_packet.md`
- `liquidity-demo/packet/liquidity_packet.html`

Assessment: this is the strongest cold-start command. It proves packaged examples work and gives a packet immediately.

### Minute 6-7: Build The Stress Packet

Command tried:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=<repo> \
  python -m portfolio_liquidity_runway_lab build-packet --out liquidity-demo/packet --scenario stress
```

Observed output:

```json
{
  "boundary": "Educational static analysis only. This tool uses local synthetic or user-supplied inputs, does not fetch live data, does not connect to brokers, does not place orders, and does not provide tax, legal, investment, buy, sell, or hold advice.",
  "html": "liquidity-demo/packet/liquidity_packet.html",
  "json": "liquidity-demo/packet/liquidity_packet.json",
  "markdown": "liquidity-demo/packet/liquidity_packet.md",
  "status": "ok"
}
```

The committed visual receipt at `demo/visual_receipt.md` shows what a user should expect from the packet: gross assets, stress haircut assets, effective monthly burn, reserve months, liquidity bucket bars, and forced-sale review signals.

### Minute 7-8: Validate Inputs

Command tried:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=<repo> \
  python -m portfolio_liquidity_runway_lab input-lint \
  --portfolio liquidity-demo/portfolio.json \
  --ledger liquidity-demo/ledger.json \
  --assumptions liquidity-demo/assumptions.json \
  --portfolio-csv liquidity-demo/portfolio.csv \
  --ledger-csv liquidity-demo/ledger.csv
```

Observed output summary:

```json
{
  "finding_counts": {
    "error": 0,
    "warning": 0
  },
  "status": "pass"
}
```

The detailed results covered `portfolio_json`, `ledger_json`, `assumptions_json`, `portfolio_csv`, and `ledger_csv`; all passed. This command is important enough to be in the first-run path, but the README currently places it after many artifact-generation commands.

### Minute 8-9: Exercise CSV Workflow

Command tried:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=<repo> \
  python -m portfolio_liquidity_runway_lab csv-import \
  --portfolio-csv liquidity-demo/portfolio.csv \
  --ledger-csv liquidity-demo/ledger.csv \
  --out liquidity-demo/csv-import
```

Observed output:

```json
{
  "ledger_json": "liquidity-demo/csv-import/ledger.json",
  "portfolio_json": "liquidity-demo/csv-import/portfolio.json",
  "report_json": "liquidity-demo/csv-import/import_report.json",
  "report_markdown": "liquidity-demo/csv-import/import_report.md",
  "status": "ok"
}
```

`demo/csv-import/import_report.md` confirms row counts and validation findings:

- Portfolio rows: `4`
- Ledger events: `3`
- Validation: no findings

Command tried:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=<repo> \
  python -m portfolio_liquidity_runway_lab csv-export \
  --packet liquidity-demo/packet/liquidity_packet.json \
  --out liquidity-demo/csv-export
```

Observed output names these expected files:

- `liquidity-demo/csv-export/assets.csv`
- `liquidity-demo/csv-export/runway.csv`
- `liquidity-demo/csv-export/warnings.csv`
- `liquidity-demo/csv-export/bucket_summaries.csv`
- `liquidity-demo/csv-export/export_manifest.json`
- `liquidity-demo/csv-export/export_manifest.md`

### Minute 9-10: Verify Release Evidence Claims

Commands tried from repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m portfolio_liquidity_runway_lab release-check --root .
PYTHONDONTWRITEBYTECODE=1 python -m portfolio_liquidity_runway_lab public-scan --root .
PYTHONDONTWRITEBYTECODE=1 python -m portfolio_liquidity_runway_lab maturity-report --root .
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests
```

Observed outputs:

- `release-check`: `status: "pass"`, `expected_files: true`, `html_no_script_tags: true`, `public_scan: true`, no missing files, no script tag findings.
- `public-scan`: `status: "pass"`, no findings.
- `maturity-report`: score `38`, all checks true.
- Unit tests: `Ran 43 tests in 2.278s`, `OK`.

`docs/golden-replay/golden_replay.md` reports `Status: pass`, `Compared artifacts: 17`, `Passed: 17`, `Failed: 0`.

## Friction Log

| Severity | Area | Path | Finding | User Impact |
| --- | --- | --- | --- | --- |
| High | README onboarding | `README.md` | Quickstart is a full evidence-production script, not a minimal first packet path. | New users may abandon before finding the core value. |
| High | Command prioritization | `README.md`, `docs/command-matrix/command_matrix.md` | 28 commands are presented flat. | Users cannot quickly distinguish analyst workflow, CSV workflow, and release-owner workflow. |
| Medium | First packet review | `README.md`, `docs/cold_start_walkthrough.md` | Docs list output files but do not say which artifact to open first or what "good" looks like. | Users get artifacts but may not know how to evaluate them. |
| Medium | Input authoring | `docs/template-pack/README.md`, `docs/schema_guide.md` | Template pack exists, but README does not put it in a tight "use your own data" path. | Users may edit packaged JSON directly without using lintable starters. |
| Medium | CLI help | `portfolio_liquidity_runway_lab/cli.py` | Argparse help is comprehensive but ungrouped. | The command list reads like an API catalog, not a task guide. |
| Medium | Error expectations | `README.md`, `docs/cold_start_walkthrough.md` | Happy path is well documented; intentional bad-input examples are not prominent. | Users may not trust remediation behavior until they hit an error. |
| Medium | Release artifacts in quickstart | `README.md` | `release-deck`, `bundle-checksums`, `evidence-bundle`, `artifact-catalog`, `golden-replay`, and `release-check` appear in the same first block as packet commands. | Analyst users are exposed to maintainer workflows too early. |
| Low | Naming | `quickstart-check`, `fixture-doctor`, `visual-receipt` | Names are useful after learning the project, but not self-evident to finance users. | Some commands require reading descriptions before usage is clear. |
| Low | HTML review | `README.md` | README says to open several HTML files, but does not explain that no server is needed. | Nontechnical users may wonder whether to run a web server. |
| Low | Boundary repetition | Many generated artifacts | Boundary text is consistently present. | Good for safety, but it consumes visual space in stdout and docs; keep it, but compensate with clearer section hierarchy. |

## Exact Commands Tried

Discovery:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m portfolio_liquidity_runway_lab --version
PYTHONDONTWRITEBYTECODE=1 python -m portfolio_liquidity_runway_lab --help
```

Cold-start path:

```bash
TMPDIR="<tmp-workdir>"
cd "$TMPDIR"
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=<repo> python -m portfolio_liquidity_runway_lab quickstart-check --out liquidity-demo
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=<repo> python -m portfolio_liquidity_runway_lab build-packet --out liquidity-demo/packet --scenario stress
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=<repo> python -m portfolio_liquidity_runway_lab input-lint --portfolio liquidity-demo/portfolio.json --ledger liquidity-demo/ledger.json --assumptions liquidity-demo/assumptions.json --portfolio-csv liquidity-demo/portfolio.csv --ledger-csv liquidity-demo/ledger.csv
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=<repo> python -m portfolio_liquidity_runway_lab assumption-audit --portfolio liquidity-demo/portfolio_concentrated.json --out liquidity-demo/assumption-audit
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=<repo> python -m portfolio_liquidity_runway_lab csv-import --portfolio-csv liquidity-demo/portfolio.csv --ledger-csv liquidity-demo/ledger.csv --out liquidity-demo/csv-import
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=<repo> python -m portfolio_liquidity_runway_lab csv-export --packet liquidity-demo/packet/liquidity_packet.json --out liquidity-demo/csv-export
find liquidity-demo -maxdepth 2 -type f | sort
```

Repository verification:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m portfolio_liquidity_runway_lab release-check --root .
PYTHONDONTWRITEBYTECODE=1 python -m portfolio_liquidity_runway_lab public-scan --root .
PYTHONDONTWRITEBYTECODE=1 python -m portfolio_liquidity_runway_lab maturity-report --root .
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests
```

## Expected Outputs

Minimal first-run expected stdout:

```json
{
  "status": "ok",
  "examples": "liquidity-demo",
  "packet": "liquidity-demo/packet"
}
```

Minimal first-run expected files:

```text
liquidity-demo/portfolio.json
liquidity-demo/portfolio_concentrated.json
liquidity-demo/ledger.json
liquidity-demo/assumptions.json
liquidity-demo/history.json
liquidity-demo/portfolio.csv
liquidity-demo/ledger.csv
liquidity-demo/packet/liquidity_packet.json
liquidity-demo/packet/liquidity_packet.md
liquidity-demo/packet/liquidity_packet.html
```

Core packet expected content, based on `demo/visual_receipt.md`:

- Scenario: `stress`
- Gross assets: `$165,000.00`
- Stress haircut assets: `$133,460.00`
- Effective monthly burn: `$7,282.83`
- Same-day reserve months: `4.51`
- Thirty-day runway months: `12.97`
- Review signals include negative liquid balance in month 10, same-day reserve below threshold, and locked/gated assets above 35 percent of gross assets.

Input lint expected status for packaged examples:

```json
{
  "finding_counts": {
    "error": 0,
    "warning": 0
  },
  "status": "pass"
}
```

Release check expected status:

```json
{
  "checks": {
    "expected_files": true,
    "html_no_script_tags": true,
    "public_scan": true
  },
  "status": "pass"
}
```

Test expected output:

```text
Ran 43 tests in 2.278s
OK
```

## Scoring Rubric

| Area | Score | Rationale |
| --- | ---: | --- |
| Install/package clarity | 8/10 | `pyproject.toml` is clean, no runtime deps, version and console script are correct. README could add an explicit install command for package users. |
| First useful output | 8/10 | `quickstart-check` creates examples and a packet in one command. README obscures this by continuing into the full release workflow. |
| CLI discoverability | 7/10 | Help text is complete and command descriptions are concise. Missing task grouping and "common first commands." |
| Input validation | 9/10 | `input-lint` covers JSON and CSV with remediation and schema refs; tests cover failure behavior. |
| Artifact usefulness | 8/10 | Packet, visual receipt, casebook, CSV exports, and static HTML are useful. Users need clearer artifact triage. |
| Determinism/reproducibility | 9/10 | Tests, `golden-replay`, checksums, and release check support deterministic claims. |
| Safety boundaries | 9/10 | Boundary text is present in README, CLI stdout, packets, docs, and evidence. Residual risks are documented. |
| Test coverage | 8/10 | 43 tests cover core and CLI behavior broadly. More tests could cover grouped onboarding docs or command failure ergonomics. |
| Release evidence | 9/10 | `release-check`, `public-scan`, `maturity-report`, evidence bundle, and golden replay are all present and passing. |
| Cold-start user fit | 7/10 | The software works well; the onboarding information architecture is the main weakness. |

Overall cold-start score: 82/100.

Interpretation: v0.8.0 is technically ready for alpha promotion to users comfortable with CLIs and local files. It is not yet polished enough for a broad nontechnical finance audience without a shorter first-run guide.

## Top 10 Fixes

1. Split `README.md` Quickstart into "First packet in 2 commands" and "Full evidence/release workflow." Put only `quickstart-check`, `build-packet`, and "open `liquidity-demo/packet/liquidity_packet.html`" in the first block.
2. Add a "Which artifact should I open?" table to `README.md` and `docs/cold_start_walkthrough.md`: packet HTML for review, packet JSON for automation, visual receipt for summary, template pack for own data, casebook for release owners.
3. Add a "Use your own data" path near the top of `README.md`: `template-pack`, edit CSV/JSON, `input-lint`, `build-packet`.
4. Group CLI commands in docs and help-adjacent docs as: analyst workflow, CSV workflow, evidence/release workflow, diagnostics. `docs/command-matrix/command_matrix.md` already has the metadata needed.
5. Add one intentional bad-input walkthrough to `docs/cold_start_walkthrough.md` showing nonzero `input-lint` output and remediation fields.
6. Add a brief "no server required" note wherever HTML artifacts are introduced; the generated files are static no-JavaScript files.
7. Rename or alias cold-start commands for clarity in a future minor release: consider `quickstart` as an alias for `quickstart-check`, while keeping the existing command for compatibility.
8. Add expected packet snapshot values to `README.md`, borrowing the concise numbers already in `demo/visual_receipt.md`.
9. Add install examples to `README.md`: source checkout with `python -m ...`, installed package with console script, and optional isolated virtualenv.
10. Add a release-owner note that `release-deck`, `bundle-checksums`, `evidence-bundle`, `artifact-catalog`, `golden-replay`, and `release-check` are not required for ordinary analyst usage.

## Release And Promotion Implications

Promote as: alpha public utility for CLI-comfortable analysts, operators, founders, and finance teams who can work with local JSON/CSV files.

Do not promote as: automated portfolio advice, broker-connected financial tooling, real-time liquidity monitoring, compliance software, tax planning, investment optimization, or production treasury automation.

Positive release signals:

- `pyproject.toml` reports no runtime dependencies and Python `>=3.9`.
- `portfolio_liquidity_runway_lab/core.py` centralizes `BOUNDARY_TEXT`, `PROJECT_VERSION = "0.8.0"`, expected release files, and deterministic artifact builders.
- `tests/test_cli.py` includes an empty-directory `quickstart-check` test and public scan test.
- `tests/test_core.py` validates deterministic builders, release manifest content, README expectations, and maturity checks.
- `docs/release_check.md` reports pass for expected files, no-script HTML, and public scan.
- `docs/golden-replay/golden_replay.md` reports 17/17 committed demo artifacts match regenerated artifacts.
- `docs/evidence-bundle/boundary_risks.md` names stale input, static scenario, and incomplete security/compliance audit risks.

Promotion constraints:

- Keep the "Alpha" classifier in `pyproject.toml` unless onboarding and user-data workflow are simplified.
- Do not market the release around predictive accuracy. Market it around deterministic local review packets and assumption transparency.
- Avoid screenshots or copy that imply transaction recommendations. The strongest artifacts are review prompts, runway rows, warnings, and offline evidence bundles.
- Before broader promotion, fix README command prioritization so non-maintainers are not asked to run release evidence commands in the first experience.

## Boundary And Risk Notes

Confirmed safety boundaries:

- `README.md` states the tool does not fetch live data, connect to brokers, place orders, or provide tax, legal, investment, buy, sell, or hold advice.
- `portfolio_liquidity_runway_lab/core.py` uses the same `BOUNDARY_TEXT` across generated outputs.
- CLI stdout includes the boundary for packet, audit, CSV, evidence, and release commands.
- `docs/evidence-bundle/boundary_risks.md` states outputs are deterministic review artifacts, not instructions to transact.
- Generated HTML checked by `release-check` contains no script tags.

Residual risks:

- Stale local inputs can create misleading packets even when validation passes.
- Liquidity tiers and haircut assumptions are user/model inputs, not externally verified market data.
- Static scenarios do not model taxes, legal restrictions, custody lockups, redemption gates, settlement failures, changing rates, or stress-market execution.
- `public-scan` and `release-check` are useful release aids, not a complete security, privacy, compliance, or financial-model audit.
- The package includes many release-owner artifacts; if users treat those as required for normal analysis, onboarding feels heavier than the core product actually is.

## Audit Conclusion

v0.8.0 is functionally solid for a cold-start alpha: the empty-directory quickstart works, packaged examples lint cleanly, core packet outputs are deterministic, CSV workflows are usable, tests pass, and generated release evidence is coherent. The main release blocker is not code correctness; it is onboarding information architecture. The project should promote the two-command packet path first, then progressively disclose CSV authoring, scenario review, and release-owner evidence commands.
