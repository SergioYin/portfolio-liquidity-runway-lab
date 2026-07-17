# Security And Public Release Audit v0.8.0

Audit date: 2026-07-18

Scope: `portfolio-liquidity-runway-lab` v0.8.0 source tree, public-scan implementation, generated docs/demos, packaging metadata, manifest policy, tests, and local release metadata. This audit did not modify code or generated artifacts.

## Commands Run

```bash
pwd && rg --files
rg -n "public|scan|secret|token|key|password|credential|path|home|/home|C:\\\\|disclaimer|financial|investment|advice|release|version|github|gh |MANIFEST|package|include|exclude" .
sed -n '1,240p' pyproject.toml
sed -n '1,220p' MANIFEST.in
git status --short && git tag --list && find . -maxdepth 3 \( -name '.github' -o -name 'release*' -o -name '*release*' \) -print
rg -n "def public_scan|def release_check|def build_release_check|def build_.*html|html|script|csv|manifest|checksum|BOUNDARY_TEXT|def release_manifest|def build_csv|escape|html.escape|Path\(" portfolio_liquidity_runway_lab/core.py portfolio_liquidity_runway_lab/cli.py tests README.md docs/release-audits/cold_start_audit_v080.md
PYTHONDONTWRITEBYTECODE=1 python -m portfolio_liquidity_runway_lab public-scan --root .
PYTHONDONTWRITEBYTECODE=1 python -m portfolio_liquidity_runway_lab release-check --root .
rg -n --hidden -g '!dist/**' -g '!build/**' -g '!.git/**' -F "<linux-home>/" .
rg -n --hidden -g '!dist/**' -g '!build/**' -g '!.git/**' "(AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9_]{20,}|github_pat_|sk-[A-Za-z0-9_-]{20,}|xox[baprs]-|-----BEGIN|password\s*[:=]|api[_-]?key\s*[:=]|secret\s*[:=]|access[_-]?token\s*[:=]|refresh[_-]?token\s*[:=])" .
rg -n --hidden -g '!dist/**' -g '!build/**' -g '!.git/**' "<script|onerror=|onload=|javascript:|data:text/html" docs demo portfolio_liquidity_runway_lab tests README.md
git show --stat --oneline --decorate --no-renames v0.8.0 --
git ls-files | sort
git ls-files dist build .github docs/release-audits || true
git check-ignore -v dist/fixture-doctor-work/release_manifest.json build 2>/dev/null || true
```

## Executive Result

Release status: review before wider public release.

The built-in public release checks pass: `public-scan --root .` returns `status: "pass"` with no findings, and `release-check --root .` returns `status: "pass"` with `expected_files`, `public_scan`, and `html_no_script_tags` all true. `docs/release_check.json` and `docs/release_check.md` also report pass.

Residual public-release risk remains because the shipped scan is intentionally narrow. It does not catch absolute local paths, token-shaped values without exact marker names, CSV formula injection, stale generated release evidence, or broad packaging of duplicated generated docs/demos. A targeted scan found committed absolute workspace paths in `demo/casebook/casebook.json` and pre-existing local audit command lines in `docs/release-audits/cold_start_audit_v080.md`.

## Threat Model

Primary assets:

- User-supplied portfolio, ledger, assumptions, and history values in JSON/CSV.
- Generated public artifacts under `demo/` and `docs/`.
- Source distribution contents controlled by `MANIFEST.in`.
- Public trust boundary around finance-adjacent output and release evidence.

Likely attackers and failure modes:

- A malicious input author injects HTML, Markdown table delimiters, or spreadsheet formulas into asset names, event labels, portfolio names, scenario names, or CSV values.
- A maintainer accidentally commits local paths, private working directory names, generated fixture work output, or personal review notes.
- A release operator publishes an sdist with too much generated evidence or stale artifacts that contradict current checks.
- A downstream user treats the deterministic liquidity packet as financial advice because the package is classified for financial/insurance audiences.

Out of scope based on implementation:

- Broker/bank/API compromise. The code has no runtime dependencies and no live integrations in `pyproject.toml`.
- Server-side web exploitation. Generated HTML is static local output and no web server is shipped.

## Public-Scan Implementation

The scan lives in `portfolio_liquidity_runway_lab/core.py`.

- `FORBIDDEN_PUBLIC_TERMS` only includes underscore terms: `api_key`, `secret_key`, `private_key`, `password`, `broker_token`, `access_token`, and `refresh_token` (`core.py` near the top of the file).
- `IGNORED_RELEASE_PARTS` excludes `.git`, caches, `.venv`, `__pycache__`, `build`, and `dist` (`core.py:183`).
- `public_scan(root)` walks all non-ignored files, flags `.github/workflows/`, binary-like suffixes, non-UTF-8 files, and files containing exact forbidden terms (`core.py:3529`).
- `release_check(root)` wraps missing expected files, public-scan status, and generated HTML `<script` checks (`core.py:3418`).

False positive handling is coarse but predictable. The scanner does not support allowlists, line-level suppressions, severities, or finding codes. Any exact forbidden term anywhere causes `status: "review"`. Tests assert the current repository passes with no findings in `tests/test_cli.py:467`, and release-check failure behavior is covered in `tests/test_core.py:454` and `tests/test_cli.py:455`.

False negative risk is higher than false positive risk:

- It misses dashed, camelCase, spaced, and environment-style secret labels such as `API_KEY=`, `api-key`, `accessToken`, `Authorization: Bearer`, and provider-specific token prefixes.
- It misses absolute paths. The targeted command `rg -F "<linux-home>/" .` found local paths even though `public-scan` passed.
- It misses CSV formula injection and spreadsheet external links.
- It only checks HTML for the literal substring `<script`, not event handlers, `javascript:` URLs, meta refreshes, remote assets, forms, or inline CSS data exfiltration.

## Leakage Findings

No provider-token-shaped strings were found by the targeted credential regex command. No committed `.github` workflow surface exists, and local tags include `v0.8.0`.

Findings requiring review:

1. Absolute workspace paths are committed in `demo/casebook/casebook.json:115`, `demo/casebook/casebook.json:116`, and `demo/casebook/casebook.json:117`. Root cause: `build_casebook_data` serializes `portfolio_path.as_posix()`, `ledger_path.as_posix()`, and `assumptions_path.as_posix()` directly (`core.py:1813`). If generated from an absolute path, the public demo leaks local workspace layout.
2. `docs/release-audits/cold_start_audit_v080.md` contains absolute `PYTHONPATH=<repo>` command lines. This is a prior audit artifact, not code behavior, but it expands the public path leakage surface if `docs/release-audits/` is tracked or included later.
3. Generated release decks are stale/inconsistent: `docs/release-deck/release_deck.md:48` and `demo/release-deck/release_deck.md:48` say `Release check: fail`, while current `release-check --root .` and `docs/release_check.md:5` say pass. This is not a secret leak, but it is a public trust issue for release evidence.

## Packaging Risk

`pyproject.toml` is minimal and favorable for security: v0.8.0, Python >=3.9, MIT license, console script, and `dependencies = []` (`pyproject.toml:5` through `pyproject.toml:26`). Package data includes only packaged examples (`pyproject.toml:31`).

`MANIFEST.in` is broad (`MANIFEST.in:4` and `MANIFEST.in:5`): it recursively includes `docs` and `demo` Markdown, JSON, HTML, CSV, and text files, plus `skills` Markdown. This means stale release evidence, generated demo JSON, duplicated evidence bundles, and absolute path leaks in generated artifacts can be shipped in the source distribution even when the wheel package data is cleaner.

The local ignored `dist/fixture-doctor-work/...` output is covered by `.gitignore` for `dist/`, and `public_scan` ignores `dist`. That is acceptable for local workspace scanning, but it means pre-publish sdist/tarball review must inspect the built archive explicitly rather than relying only on repo-tree `public-scan`.

## Generated HTML Risk

Positive controls:

- Current `release-check --root .` reports all 12 generated HTML files have no `<script` tags.
- HTML renderers consistently use `html.escape` for Markdown-derived content in representative renderers such as `render_casebook_html` (`core.py:1930`) and `render_release_deck_html` (`core.py:3271`).
- `_html_shell` escapes the document title (`core.py:1774`).

Residual risks:

- `_contains_script_tag` only searches for `<script` (`core.py:1767`). It does not detect `onerror=`, `onload=`, `javascript:`, `<iframe>`, `<object>`, `<embed>`, `<meta http-equiv>`, forms, external links, or remote images.
- Markdown table rendering is custom and simple. It escapes cell text but splits on pipes, so malicious user text containing `|` can distort tables even if it does not execute.
- Stale generated HTML can contradict current release status because generation and release-check are separate steps.

## CSV Risk

CSV import/export is deterministic and uses Python's `csv.DictWriter` (`core.py:3618`), which is good for escaping commas and quotes.

Residual risk is spreadsheet formula injection. Values beginning with `=`, `+`, `-`, or `@` can execute or create external references when opened in spreadsheet software. The current scanner and tests do not flag this class. This matters because `csv-export` writes asset names and warning text derived from user-controlled or fixture-controlled content into `demo/csv-export/*.csv` and user-selected export directories.

## Local Path, Token, And Privacy Risks

Token risk is currently low based on targeted regex scanning and absence of runtime integrations. Privacy risk is medium because generated artifacts can preserve source paths and financial-looking values.

Path handling risks:

- `casebook` records input paths as supplied (`core.py:1813`). Absolute paths become public JSON fields.
- `artifact_catalog`, `bundle_checksums`, and `evidence_bundle` store `root.as_posix()` (`core.py:3341`, `core.py:2697`, `core.py:2920`). With `--root .` this is stable; with an absolute `--root`, generated public artifacts can leak the local filesystem path.
- CLI outputs return output paths to stdout. That is acceptable for local operation, but generated docs should avoid persisting absolute paths unless explicitly requested.

Privacy content risks:

- Example data appears synthetic and no real identities were found.
- Finance-adjacent values in demos are realistic enough that users may copy the format for personal data. Public docs should keep telling users not to commit their own generated packets.

## Finance Disclaimer Risk

The boundary text is strong and reused widely: it says the tool is educational static analysis, uses local synthetic or user-supplied inputs, does not fetch live data, does not connect to brokers, does not place orders, and does not provide tax, legal, investment, buy, sell, or hold advice.

Risk remains because `pyproject.toml` declares `Intended Audience :: Financial and Insurance Industry` and `Topic :: Office/Business :: Financial`, and README/demo outputs contain concrete reserve months, runway months, forced-sale warnings, yields, fees, and review prompts. The wording is generally careful, but "forced-sale warnings" can sound action-oriented. Generated artifacts should keep "review" and "consult qualified professional" phrasing prominent wherever warnings appear.

## Exact Remediation Backlog

1. Redact or relativize generated input paths in `build_casebook_data` (`portfolio_liquidity_runway_lab/core.py:1813`). Store repo-relative paths when under the root, otherwise store only basename plus a `source_kind` field. Regenerate `demo/casebook/casebook.json` and any evidence bundles that copied it.
2. Add path leakage checks to `public_scan`: flag `<linux-home>/`, `<mac-home>/`, `<windows-user>`, `<tmp>/`, and current working directory prefixes in tracked public artifacts. Include tests that fail on absolute paths in generated JSON/Markdown/HTML.
3. Expand secret detection beyond exact underscore terms. Add provider token regexes and label forms for `API_KEY=`, `api-key`, `accessToken`, `Authorization: Bearer`, `OPENAI_API_KEY`, `AWS_SECRET_ACCESS_KEY`, `GITHUB_TOKEN`, and private key blocks. Return structured findings with code, path, and severity.
4. Add public-scan allowlist support for documented false positives. Use explicit path-and-code allow entries, not global substring suppression.
5. Replace `_contains_script_tag` with an HTML safety check that also flags event-handler attributes, `javascript:` URLs, iframes, objects, embeds, forms, meta refresh, and external network URLs. Keep the current no-script check as a subset.
6. Add CSV formula hardening for `write_csv` or for export rows before writing. Prefix spreadsheet-dangerous strings beginning with `=`, `+`, `-`, `@`, tab, or carriage return, or document and test an explicit "raw CSV" policy.
7. Add targeted tests for malicious asset names and event labels containing HTML, Markdown pipes, and CSV formulas. Cover `build-packet`, `casebook`, `scenario-gallery`, `batch-compare`, and `csv-export`.
8. Regenerate `docs/release-deck/*` and `demo/release-deck/*` after `release-check` so the release deck does not say `Release check: fail` while `docs/release_check.md` says pass.
9. Narrow `MANIFEST.in` for public sdist if demos are not required at install time. Prefer including source, README, LICENSE, packaged examples, and a curated docs subset; exclude duplicated evidence bundles and release-audit scratch material unless intentionally published.
10. Add an archive-level release gate: build sdist/wheel, list archive contents, run public-scan against extracted sdist, and check for absolute paths and token regexes inside the archive.
11. Add a "do not commit user-generated packets" warning to README near CSV and packet commands. Mention that local output can contain personal balances, income, expenses, and scheduled events.
12. Strengthen finance boundary language near generated warnings: prefer "review prompt" over "forced-sale warning" in public-facing text where feasible, and keep the qualified professional escalation line in all generated packet surfaces.

## Release Decision

Do not block a small private or internal v0.8.0 release on credential leakage: no token-shaped secrets were found and current built-in checks pass. For a public package release, address at least backlog items 1, 2, 5, 6, 8, and 10 before publishing archives or attaching generated demos to a GitHub release.
