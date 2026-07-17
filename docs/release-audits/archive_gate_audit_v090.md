# Archive Gate Audit v0.9.0

Scope: archive-level release gate audit for `portfolio-liquidity-runway-lab` v0.9.0. This audit inspected `pyproject.toml`, `MANIFEST.in`, built `dist` artifacts, release checks, public-scan implementation, prior release audits, docs, demos, tests, extracted wheel and sdist contents, package importability, and GitHub release metadata via `gh`.

Decision: **REVIEW**

The v0.9.0 wheel is importable, installable, compact, and aligned with package metadata. The source distribution is not promotion-clean: it ships stale generated release evidence from v0.8.0, a failing v0.9.0 golden replay report, and prior v0.8.0 audit materials that still describe unresolved public-release risks. These are public trust and release-coherence blockers for archive promotion even though credential/path/HTML safety scans did not find active leaks in the extracted archives.

## Commands Run

```bash
pwd
rg --files -g 'pyproject.toml' -g 'MANIFEST.in' -g 'dist/**' -g 'docs/**' -g 'demos/**' -g 'tests/**' -g '.github/**' -g 'release*' -g '*release*' -g '*audit*' -g '*check*'
git status --short
ls -la dist docs docs/release-audits
sed -n '1,240p' pyproject.toml
sed -n '1,220p' MANIFEST.in
sed -n '1,220p' docs/release_check.md
sed -n '1,260p' docs/release_readiness_review.md
find . -maxdepth 3 -type f \( -iname '*scan*' -o -iname '*public*' -o -iname '*security*' -o -iname '*release*check*' \) | sort
rm -rf <tmp>/plrl-archive-audit-v090 && mkdir -p <tmp>/plrl-archive-audit-v090/wheel <tmp>/plrl-archive-audit-v090/sdist
python -m zipfile -e dist/portfolio_liquidity_runway_lab-0.9.0-py3-none-any.whl <tmp>/plrl-archive-audit-v090/wheel
tar -xzf dist/portfolio_liquidity_runway_lab-0.9.0.tar.gz -C <tmp>/plrl-archive-audit-v090/sdist
find <tmp>/plrl-archive-audit-v090/wheel -type f | sort
find <tmp>/plrl-archive-audit-v090/sdist -type f | sort
sed -n '1,180p' <tmp>/plrl-archive-audit-v090/wheel/portfolio_liquidity_runway_lab-0.9.0.dist-info/METADATA
sed -n '1,120p' <tmp>/plrl-archive-audit-v090/sdist/portfolio_liquidity_runway_lab-0.9.0/PKG-INFO
wc -l <tmp>/plrl-archive-audit-v090/wheel/portfolio_liquidity_runway_lab-0.9.0.dist-info/RECORD
wc -l <tmp>/plrl-archive-audit-v090/sdist/portfolio_liquidity_runway_lab-0.9.0/portfolio_liquidity_runway_lab.egg-info/SOURCES.txt
rg -n --hidden --no-ignore -i '(/home/|/Users/|C:\\|xjyin|workspace|tmp/plrl|token-lab|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9_]{20,}|github_pat_|sk-[A-Za-z0-9]{20,}|xox[baprs]-|BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY|password\s*[:=]|secret\s*[:=]|api[_-]?key\s*[:=]|token\s*[:=])' <tmp>/plrl-archive-audit-v090/wheel <tmp>/plrl-archive-audit-v090/sdist
python -m unittest discover -s tests
python -m portfolio_liquidity_runway_lab release-check --out <tmp>/plrl-archive-audit-v090/release-check
python -m portfolio_liquidity_runway_lab public-scan --root .
python -m portfolio_liquidity_runway_lab golden-replay --root . --out <tmp>/plrl-archive-audit-v090/golden-replay
python -m portfolio_liquidity_runway_lab maturity-report --out <tmp>/plrl-archive-audit-v090/maturity-report.json
python -m portfolio_liquidity_runway_lab release-manifest --out <tmp>/plrl-archive-audit-v090/release_manifest.json
python -m portfolio_liquidity_runway_lab bundle-checksums --root . --out <tmp>/plrl-archive-audit-v090/bundle-checksums
python -m venv <tmp>/plrl-archive-audit-v090/venv
<tmp>/plrl-archive-audit-v090/venv/bin/python -m pip install --no-index --find-links dist portfolio-liquidity-runway-lab==0.9.0
<tmp>/plrl-archive-audit-v090/venv/bin/python -c 'import portfolio_liquidity_runway_lab as p; print(p.__version__)'
<tmp>/plrl-archive-audit-v090/venv/bin/portfolio-liquidity-runway-lab selfcheck
python - <<'PY'
from pathlib import Path
from portfolio_liquidity_runway_lab.core import public_scan, release_check
root=Path('<tmp>/plrl-archive-audit-v090/sdist/portfolio_liquidity_runway_lab-0.9.0')
print(public_scan(root))
print(release_check(root))
PY
python - <<'PY'
from pathlib import Path
import hashlib
for archive in ['dist/portfolio_liquidity_runway_lab-0.9.0-py3-none-any.whl','dist/portfolio_liquidity_runway_lab-0.9.0.tar.gz']:
    p=Path(archive)
    print(archive, p.stat().st_size, hashlib.sha256(p.read_bytes()).hexdigest())
PY
gh release view v0.9.0 --json tagName,name,isDraft,isPrerelease,publishedAt,url,body
gh release view v0.9.0 --json tagName,name,isDraft,isPrerelease,publishedAt,url,assets --jq '{tagName,name,isDraft,isPrerelease,publishedAt,url,assets: [.assets[] | {name,size,downloadUrl}]}'
git tag --list 'v0.*' --sort=version:refname
git rev-parse --short HEAD
git log -1 --pretty='%h %ci %s'
```

## Evidence Table

| Area | Evidence | Gate Impact |
| --- | --- | --- |
| Version metadata | `pyproject.toml`, wheel `METADATA`, and sdist `PKG-INFO` all report `Version: 0.9.0`; `PROJECT_VERSION = "0.9.0"` in `core.py`. | Pass |
| License and README | `README.md` and `LICENSE` exist in repo and sdist; wheel includes `portfolio_liquidity_runway_lab-0.9.0.dist-info/licenses/LICENSE`. | Pass |
| Runtime dependencies | `dependencies = []`; wheel install used `--no-index --find-links dist` successfully. | Pass |
| Archive sizes and hashes | Wheel: `50267` bytes, SHA256 `032dfdb1b17b825c6b81d70dbb643619d4b85838fcef8a7d05fa4c9d53ffa2b8`. Sdist: `248809` bytes, SHA256 `fe8c1e0688815f3c466a5cf7492ee8c0272cd59584ef5ebb2df7704357c12e87`. | Pass |
| GitHub release metadata | `gh release view v0.9.0` reports non-draft, non-prerelease, published `2026-07-17T19:20:10Z`, URL `https://github.com/SergioYin/portfolio-liquidity-runway-lab/releases/tag/v0.9.0`. Assets match local sizes: wheel `50267`, sdist `248809`. | Pass, confirms published impact |
| Wheel contents | Extracted wheel has 17 files: package code, examples, dist-info metadata, entry point, and license. No docs/demo/test sprawl. | Pass |
| Sdist contents | Extracted sdist has 179 files and `SOURCES.txt` has 176 entries, including docs, demos, tests, skills, evidence bundles, and v0.8.0 release audits. | Review |
| Importability | Fresh venv install from wheel succeeded; `import portfolio_liquidity_runway_lab` printed `0.9.0`; console `selfcheck` returned `status: ok`, `version: 0.9.0`. | Pass |
| Unit tests | `python -m unittest discover -s tests` ran 47 tests and passed. | Pass |
| Release check | Repo release check and extracted-sdist `release_check` both returned `status: pass`; expected files, public scan, no-script HTML, and expanded HTML static safety all true. | Pass with caveat |
| Public scan | Repo `public-scan --root .` returned `status: pass`; extracted sdist `public_scan(root)` returned `status: pass` with zero findings. | Pass with caveat |
| HTML safety | Extracted sdist has 12 `.html` files and wheel has 0; expanded pattern scan found 0 unsafe HTML matches. | Pass |
| Local path and token patterns | Targeted archive scan found no active absolute local path leaks or provider-token-shaped secrets in product artifacts. Matches were limited to scanner regex source/tests and prior v0.8.0 audit text discussing old findings. | Pass with caveat |
| Golden replay | Current command returned `status: fail`, `pass_count: 16`, `fail_count: 1`; committed `demo/casebook/casebook.json` hash differs from regenerated hash. `docs/golden-replay/golden_replay.md` in the sdist also says `Status: fail`. | Review blocker |
| Bundle checksum evidence | `docs/bundle-checksums/bundle_manifest.json` and `demo/bundle-checksums/bundle_manifest.json` in the sdist report `version: "0.8.0"` and enumerate `dist/portfolio_liquidity_runway_lab-0.8.0-*`, not the v0.9.0 archives. | Review blocker |
| Demo golden replay evidence | `demo/golden-replay/golden_replay.json` reports `version: "0.7.0"` with `status: pass`, while docs golden replay reports v0.9.0 fail. | Review blocker |
| Prior audits in sdist | Sdist includes `docs/release-audits/*_v080.md`; these still state v0.8.0 scope and earlier public-release risks. Historical docs are not secrets, but they are shipped as live release evidence. | Review |
| Maturity report | `maturity-report` returned score `38` with all named checks true, including `golden_replay`; this conflicts with the actual `golden-replay` command failure. | Review |
| Git state | `git status --short` was clean before report generation; current HEAD `2ba68c5`, log `2026-07-18 03:20:03 +0800 Harden public release checks v0.9.0`; tag list includes `v0.9.0`. | Informational |

## Findings

### A1. Published sdist ships stale v0.8.0 checksum manifests

Severity: High

Evidence:

- `<tmp>/plrl-archive-audit-v090/sdist/portfolio_liquidity_runway_lab-0.9.0/docs/bundle-checksums/bundle_manifest.json` contains `"version": "0.8.0"`.
- `<tmp>/plrl-archive-audit-v090/sdist/portfolio_liquidity_runway_lab-0.9.0/demo/bundle-checksums/bundle_manifest.json` contains `"version": "0.8.0"`.
- Both manifests list `dist/portfolio_liquidity_runway_lab-0.8.0-py3-none-any.whl` and `dist/portfolio_liquidity_runway_lab-0.8.0.tar.gz`.
- GitHub release assets for v0.9.0 match the local v0.9.0 archive sizes, so this stale evidence is part of the published sdist.

Impact:

The sdist tells consumers and reviewers that checksum evidence belongs to v0.8.0, not v0.9.0. This breaks archive-level provenance and makes the published source artifact unsuitable for promotion without regeneration or replacement.

### A2. Golden replay evidence fails for v0.9.0

Severity: High

Evidence:

- `python -m portfolio_liquidity_runway_lab golden-replay --root . --out <tmp>/plrl-archive-audit-v090/golden-replay` exited nonzero and returned `status: fail`, `pass_count: 16`, `fail_count: 1`.
- `docs/golden-replay/golden_replay.json` reports `version: "0.9.0"`, `status: "fail"`.
- Failed artifact: `demo/casebook/casebook.json`; committed SHA256 `f80ca2c5bf9c9707702edd9be3839ab740846723fc3dcde6f5e8ad09f153a550`, generated SHA256 `50ed6d9bc8597d65752072af623755452773ed0479104da7a53f78c1920ff783`.
- The same failing docs golden replay report is included in the extracted sdist.

Impact:

The archive includes release evidence proving one committed demo artifact does not reproduce. This directly undermines deterministic-release claims and blocks promotion until the demo artifact and replay evidence agree.

### A3. Demo golden replay evidence is from v0.7.0

Severity: Medium

Evidence:

- `demo/golden-replay/golden_replay.json` reports `version: "0.7.0"` and `status: "pass"`.
- `docs/golden-replay/golden_replay.json` reports `version: "0.9.0"` and `status: "fail"`.
- Both demo and docs golden replay evidence are included by the sdist manifest policy.

Impact:

The source archive presents contradictory replay status across demo and docs evidence. Even if the product code is functional, the public evidence package is stale and internally inconsistent.

### A4. Sdist includes broad generated docs/demos and historical v0.8.0 release audits

Severity: Medium

Evidence:

- `MANIFEST.in` recursively includes `docs` and `demo` Markdown, JSON, HTML, CSV, and text files, plus `skills` Markdown.
- Extracted sdist has 179 files and includes `docs/release-audits/cold_start_audit_v080.md`, `promotion_audit_v080.md`, and `security_public_audit_v080.md`.
- Prior v0.8.0 audit text still says "Release status: review before wider public release" and discusses earlier stale/path leakage risks.

Impact:

Historical audits are not inherently unsafe, but including them in a release archive makes them part of the public evidence surface. For promotion, the sdist should either exclude historical gate docs or clearly separate them from current release evidence.

### A5. Built-in release gates pass while missing stale-evidence failures

Severity: Medium

Evidence:

- `release-check` returned `status: pass` for repo and extracted sdist.
- `public-scan` returned `status: pass` for repo and extracted sdist.
- `maturity-report` returned score `38` with `golden_replay: true`.
- The independent golden replay command fails, and bundle checksum manifests remain v0.8.0.

Impact:

The current automated gates are useful for file presence, public scans, and HTML safety, but they do not enforce that generated release evidence matches the current project version or that golden replay actually passes. Promotion should not rely on `release-check` alone.

## Non-Findings

- No active credential-shaped values were found in the extracted product artifacts. Regex hits were scanner implementation patterns, tests that deliberately construct fake tokens, or historical audit text describing old scans.
- No active absolute local workspace path leaks were found in extracted product/demo artifacts under the targeted scan.
- No unsafe HTML was found in extracted archive HTML files under checks for script tags, event handlers, `javascript:` URLs, iframe/object/embed/form tags, meta refresh, or external network URLs.
- Package metadata includes README, MIT license, Python `>=3.9`, console entry point, and no runtime dependencies.
- The v0.9.0 wheel installs and imports cleanly in a fresh venv.

## Decision

**REVIEW**

The archive is not ready for promotion as a clean v0.9.0 public release artifact set. Runtime package quality is acceptable, but release-evidence integrity is not. The published sdist contains stale v0.8.0 checksum manifests, contradictory golden replay status, and a failing v0.9.0 replay artifact.

## Promotion Implications

- Do not promote v0.9.0 archives as fully release-gated or reproducible.
- If v0.9.0 remains published, release notes should avoid claiming clean deterministic replay or current checksum evidence for the sdist.
- Before promoting or cutting a replacement release, regenerate `demo/bundle-checksums`, `docs/bundle-checksums`, `demo/golden-replay`, `docs/golden-replay`, evidence bundles, release manifest, release deck, artifact catalog, and release check from the same final tree.
- Rebuild wheel and sdist after regeneration, then re-run archive extraction, targeted leak scan, HTML safety scan, fresh wheel install/import smoke, `public-scan`, `release-check`, and `golden-replay`.
- Consider narrowing `MANIFEST.in` or clearly separating historical audits from current release evidence so stale audit docs cannot be mistaken for v0.9.0 gate output.
