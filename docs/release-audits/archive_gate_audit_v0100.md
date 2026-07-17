# Archive Gate Audit v0.10.0

Scope: focused final archive promotion audit for current `portfolio-liquidity-runway-lab` v0.10.0 artifacts and current repo state only. This audit specifically rechecked the v0.9.0 blockers recorded in `docs/release-audits/archive_gate_audit_v090.md`.

Decision: **REVIEW**

The v0.10.0 wheel and sdist are published on GitHub as non-draft, non-prerelease assets; the wheel installs and imports cleanly; release-check, public-scan, and golden replay pass; the sdist no longer contains `docs/release-audits`; and extracted sdist release evidence no longer contains stale `0.8.0` or `0.9.0` strings. However, the current bundle checksum manifests record v0.10.0 archive filenames with stale hashes and an old sdist size that do not match the current local or downloaded GitHub release assets. That checksum provenance mismatch blocks a clean final archive promotion.

## Commands Run

```bash
pwd && rg --files
sed -n '1,240p' docs/release-audits/archive_gate_audit_v090.md
git status --short
ls -la dist docs docs/release-audits
find dist -maxdepth 1 -type f -printf '%f %s bytes\n' | sort
rg -n '0\.8\.0|0\.9\.0|0\.10\.0|version' docs/bundle-checksums demo/bundle-checksums docs/golden-replay demo/golden-replay docs/release_check.* docs/release_manifest.json pyproject.toml portfolio_liquidity_runway_lab
python -m portfolio_liquidity_runway_lab --version || true
git rev-parse --short HEAD
git log -1 --pretty='%h %ci %s'
rm -rf <tmp>/plrl-archive-audit-v0100 && mkdir -p <tmp>/plrl-archive-audit-v0100/wheel <tmp>/plrl-archive-audit-v0100/sdist
python -m zipfile -e dist/portfolio_liquidity_runway_lab-0.10.0-py3-none-any.whl <tmp>/plrl-archive-audit-v0100/wheel
tar -xzf dist/portfolio_liquidity_runway_lab-0.10.0.tar.gz -C <tmp>/plrl-archive-audit-v0100/sdist
find <tmp>/plrl-archive-audit-v0100/sdist -maxdepth 4 -type f | sort | sed 's#<tmp>/plrl-archive-audit-v0100/sdist/portfolio_liquidity_runway_lab-0.10.0/##' | head -240
python - <<'PY'
from pathlib import Path
import hashlib
for archive in ['dist/portfolio_liquidity_runway_lab-0.10.0-py3-none-any.whl','dist/portfolio_liquidity_runway_lab-0.10.0.tar.gz']:
    p=Path(archive)
    print(archive, p.stat().st_size, hashlib.sha256(p.read_bytes()).hexdigest())
PY
python -m portfolio_liquidity_runway_lab golden-replay --root . --out <tmp>/plrl-archive-audit-v0100/golden-replay
python -m portfolio_liquidity_runway_lab release-check --out <tmp>/plrl-archive-audit-v0100/release-check
python -m portfolio_liquidity_runway_lab public-scan --root .
rg -n --hidden --no-ignore '0\.8\.0|0\.9\.0|v0\.8\.0|v0\.9\.0' <tmp>/plrl-archive-audit-v0100/sdist/portfolio_liquidity_runway_lab-0.10.0/docs <tmp>/plrl-archive-audit-v0100/sdist/portfolio_liquidity_runway_lab-0.10.0/demo || true
python -m venv <tmp>/plrl-archive-audit-v0100/venv
<tmp>/plrl-archive-audit-v0100/venv/bin/python -m pip install --no-index --find-links dist portfolio-liquidity-runway-lab==0.10.0
<tmp>/plrl-archive-audit-v0100/venv/bin/python -c 'import portfolio_liquidity_runway_lab as p; print(p.__version__)'
<tmp>/plrl-archive-audit-v0100/venv/bin/portfolio-liquidity-runway-lab selfcheck
find <tmp>/plrl-archive-audit-v0100/sdist/portfolio_liquidity_runway_lab-0.10.0 -path '*/release-audits*' -print
python - <<'PY'
from pathlib import Path
from portfolio_liquidity_runway_lab.core import public_scan, release_check
root=Path('<tmp>/plrl-archive-audit-v0100/sdist/portfolio_liquidity_runway_lab-0.10.0')
print('public_scan', public_scan(root))
print('release_check', release_check(root))
PY
python - <<'PY'
from pathlib import Path
import json
root=Path('<tmp>/plrl-archive-audit-v0100/sdist/portfolio_liquidity_runway_lab-0.10.0')
for rel in ['docs/bundle-checksums/bundle_manifest.json','demo/bundle-checksums/bundle_manifest.json','docs/golden-replay/golden_replay.json','demo/golden-replay/golden_replay.json']:
    data=json.loads((root/rel).read_text())
    print(rel, 'version=', data.get('version'), 'status=', data.get('status'), 'file_count=', data.get('file_count'), 'pass_count=', data.get('pass_count'), 'fail_count=', data.get('fail_count'))
    if 'bundle_manifest' in rel:
        for f in data.get('files', []):
            if f.get('path','').startswith('dist/'):
                print(' ', f.get('path'), f.get('size_bytes'), f.get('sha256'))
PY
gh release view v0.10.0 --json tagName,name,isDraft,isPrerelease,publishedAt,url,assets --jq '{tagName,name,isDraft,isPrerelease,publishedAt,url,assets: [.assets[] | {name,size,downloadUrl}]}'
python - <<'PY'
from pathlib import Path
import json
for rel in ['docs/bundle-checksums/bundle_manifest.json','demo/bundle-checksums/bundle_manifest.json']:
    data=json.loads(Path(rel).read_text())
    print(rel)
    for f in data['files']:
        if f['path'].startswith('dist/'):
            print(f)
PY
rm -rf <tmp>/plrl-archive-audit-v0100/gh-assets && mkdir -p <tmp>/plrl-archive-audit-v0100/gh-assets
gh release download v0.10.0 --dir <tmp>/plrl-archive-audit-v0100/gh-assets --pattern 'portfolio_liquidity_runway_lab-0.10.0*'
python - <<'PY'
from pathlib import Path
import hashlib
for p in sorted(Path('<tmp>/plrl-archive-audit-v0100/gh-assets').iterdir()):
    print(p.name, p.stat().st_size, hashlib.sha256(p.read_bytes()).hexdigest())
PY
wc -l <tmp>/plrl-archive-audit-v0100/wheel/portfolio_liquidity_runway_lab-0.10.0.dist-info/RECORD <tmp>/plrl-archive-audit-v0100/sdist/portfolio_liquidity_runway_lab-0.10.0/portfolio_liquidity_runway_lab.egg-info/SOURCES.txt
sed -n '1,120p' <tmp>/plrl-archive-audit-v0100/wheel/portfolio_liquidity_runway_lab-0.10.0.dist-info/METADATA
sed -n '1,80p' <tmp>/plrl-archive-audit-v0100/sdist/portfolio_liquidity_runway_lab-0.10.0/PKG-INFO
git status --short
```

## Evidence

| Gate | Evidence | Result |
| --- | --- | --- |
| Current version metadata | `pyproject.toml` has `version = "0.10.0"`; `portfolio_liquidity_runway_lab/__init__.py` has `__version__ = "0.10.0"`; `core.py` has `PROJECT_VERSION = "0.10.0"`; CLI `--version` printed `portfolio-liquidity-runway-lab 0.10.0`; wheel `METADATA` and sdist `PKG-INFO` report `Version: 0.10.0`. | Pass |
| Current artifacts present | `dist/portfolio_liquidity_runway_lab-0.10.0-py3-none-any.whl` and `dist/portfolio_liquidity_runway_lab-0.10.0.tar.gz` are the only listed v0.10.0 dist files. Local sizes: wheel `50285`, sdist `220920`. | Pass |
| Git state at audit start | `git status --short` was clean before writing this audit file. HEAD was `585d6f1`, `2026-07-18 03:28:58 +0800 Regenerate clean release evidence v0.10.0`. | Pass |
| No release-audits directory in sdist | `find <tmp>/plrl-archive-audit-v0100/sdist/portfolio_liquidity_runway_lab-0.10.0 -path '*/release-audits*' -print` returned no output. Extracted sdist file list includes generated docs/demos but no `docs/release-audits`. | Pass |
| No stale v0.8.0/v0.9.0 strings in sdist release evidence | `rg -n --hidden --no-ignore '0\.8\.0|0\.9\.0|v0\.8\.0|v0\.9\.0'` over extracted sdist `docs/` and `demo/` returned no output. | Pass |
| Golden replay | `python -m portfolio_liquidity_runway_lab golden-replay --root . --out <tmp>/plrl-archive-audit-v0100/golden-replay` returned `status: pass`, `pass_count: 17`, `fail_count: 0`. Extracted sdist `docs/golden-replay/golden_replay.json` and `demo/golden-replay/golden_replay.json` both report `version=0.10.0`, `status=pass`, `pass_count=17`, `fail_count=0`. | Pass |
| Bundle manifests version | Extracted sdist `docs/bundle-checksums/bundle_manifest.json` and `demo/bundle-checksums/bundle_manifest.json` both report `version=0.10.0` and list `dist/portfolio_liquidity_runway_lab-0.10.0-py3-none-any.whl` plus `dist/portfolio_liquidity_runway_lab-0.10.0.tar.gz`. | Pass for version/name gate |
| Bundle checksum accuracy | Current local and downloaded GitHub assets hash to wheel `93cd5cf482bde76f8fabbc24540af1488fdd8eb821d7bc5b3624dc5a83405b21`, sdist `697c420db4d1c1c3df8f63f72801d4fdfa900dd1f6a48175db77d9022e806325`. Both repo and extracted sdist bundle manifests instead record wheel `7baee8c84e4d6ee6c1a77db17bf1a76876ee776b85a62d483a6c64d04aaf1bca` and sdist `862919579195cc88537841bad16cca7d4169590e9c95ae0a3c2b0b366538c537`; manifest sdist size is `223948`, current/GitHub sdist size is `220920`. | Review blocker |
| Release-check | Repo CLI release-check returned `status: pass` with `expected_files`, `html_no_script_tags`, `html_static_safe`, and `public_scan` all true. Extracted sdist `release_check(root)` also returned `status: pass`, no missing files, no HTML script tags, no HTML safety findings, no public scan findings. | Pass |
| Public-scan | Repo `public-scan --root .` returned `status: pass`, `findings: []`. Extracted sdist `public_scan(root)` returned `status: pass`, `findings: []`. | Pass |
| Wheel install/import/selfcheck | Fresh venv install from local `dist` with `--no-index --find-links dist portfolio-liquidity-runway-lab==0.10.0` succeeded. Import printed `0.10.0`. Console `selfcheck` returned `status: ok`, `version: 0.10.0`, and all listed checks true. | Pass |
| GitHub release metadata | `gh release view v0.10.0` returned `isDraft: false`, `isPrerelease: false`, published `2026-07-17T19:29:05Z`, URL `https://github.com/SergioYin/portfolio-liquidity-runway-lab/releases/tag/v0.10.0`, with both assets: wheel `50285`, sdist `220920`. `gh release download v0.10.0` downloaded both assets and their hashes matched local current `dist`. | Pass |
| Archive contents size | Extracted wheel `RECORD` has `17` lines. Extracted sdist `SOURCES.txt` has `173` lines. | Informational |

## v0.9.0 Blocker Resolution

| v0.9.0 blocker | v0.10.0 status |
| --- | --- |
| Sdist included `docs/release-audits/*` historical audits. | Resolved. Current extracted sdist has no `release-audits` path. |
| Sdist release evidence contained stale `0.8.0` and `0.9.0` strings. | Resolved for extracted sdist `docs/` and `demo/`; targeted stale-version scan returned no matches. |
| Golden replay failed for v0.9.0. | Resolved. Current golden replay passes with `17` passes and `0` failures; committed docs/demo replay evidence also reports pass for v0.10.0. |
| Bundle manifests reported stale v0.8.0 version/archive names. | Partially resolved. Manifests now report `version: "0.10.0"` and v0.10.0 archive paths, but their recorded wheel/sdist hashes and sdist size do not match the current local or GitHub release assets. |
| Release-check and public-scan were insufficient alone. | Current release-check and public-scan pass in repo and extracted sdist, but checksum mismatch remains outside those gates. |
| Wheel install/import/selfcheck needed to pass. | Resolved. Fresh wheel install, import, and selfcheck all pass for v0.10.0. |
| GitHub release needed to be non-draft/non-prerelease with both assets. | Resolved. v0.10.0 release is published, non-draft, non-prerelease, and has both expected assets. |

## Findings

### A1. Bundle checksum manifests do not match the promoted v0.10.0 archives

Severity: High

Evidence:

- Current local wheel: `50285` bytes, SHA256 `93cd5cf482bde76f8fabbc24540af1488fdd8eb821d7bc5b3624dc5a83405b21`.
- Current local sdist: `220920` bytes, SHA256 `697c420db4d1c1c3df8f63f72801d4fdfa900dd1f6a48175db77d9022e806325`.
- Downloaded GitHub release assets match those same current sizes and hashes.
- `docs/bundle-checksums/bundle_manifest.json` and `demo/bundle-checksums/bundle_manifest.json`, both in repo and extracted sdist, record wheel SHA256 `7baee8c84e4d6ee6c1a77db17bf1a76876ee776b85a62d483a6c64d04aaf1bca`.
- The same manifests record sdist size `223948` and SHA256 `862919579195cc88537841bad16cca7d4169590e9c95ae0a3c2b0b366538c537`, while the current/GitHub sdist is `220920` bytes and SHA256 `697c420db4d1c1c3df8f63f72801d4fdfa900dd1f6a48175db77d9022e806325`.

Impact:

The stale v0.8.0/v0.9.0 evidence blocker is resolved, but the current checksum evidence still does not authenticate the archives actually present in `dist` or published on GitHub. This is an archive promotion blocker because consumers using the shipped manifests cannot verify the promoted release assets from the bundled evidence.

## Non-Findings

- No `docs/release-audits` directory or files are included in the extracted v0.10.0 sdist.
- No stale `0.8.0`, `0.9.0`, `v0.8.0`, or `v0.9.0` strings were found in extracted sdist `docs/` or `demo/` release evidence.
- No public-scan findings were reported for repo root or extracted sdist.
- No generated HTML safety findings were reported by release-check.
- The GitHub release assets are coherent with the current local `dist` files by size and SHA256.
- The wheel installs, imports, and passes selfcheck in a fresh virtual environment.

## Remaining Cautions

- `release-check` and `public-scan` pass despite the checksum manifest/archive mismatch. Promotion should not rely on those gates alone for archive provenance.
- Bundle checksum evidence likely needs to be regenerated after the final wheel/sdist build, then the sdist rebuilt so the included manifests describe the exact final archives.
- After regenerating checksum evidence and rebuilding archives, re-run this focused audit against the newly built local archives and downloaded GitHub release assets.

