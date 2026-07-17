# Command Matrix

| Command | Inputs | Outputs | Static no-JS HTML |
| --- | --- | --- | --- |
| `build-packet` | portfolio.json, ledger.json, assumptions.json | liquidity_packet.json, liquidity_packet.md, liquidity_packet.html | true |
| `compare-history` | history.json | stdout JSON, optional JSON file | false |
| `review-ledger` | ledger.json | stdout JSON, optional JSON file | false |
| `static-dashboard` | portfolio.json, ledger.json, assumptions.json | liquidity_packet.html | true |
| `scenario-gallery` | portfolio.json, ledger.json, assumptions.json | scenario_gallery.json, scenario_gallery.md, scenario_gallery.html | true |
| `assumption-audit` | portfolio.json, ledger.json, assumptions.json | assumption_audit.json, assumption_audit.md | false |
| `batch-compare` | portfolio directory, ledger.json, assumptions.json | batch_compare.json, batch_compare.md, batch_compare.html | true |
| `casebook` | portfolio.json, portfolio directory, ledger.json, assumptions.json | casebook.json, casebook.md, casebook.html | true |
| `artifact-catalog` | repo or output root | artifact_catalog.json, artifact_catalog.md | false |
| `release-check` | repo root | release_check.json, release_check.md | false |
| `visual-receipt` | portfolio.json, ledger.json, assumptions.json | visual_receipt.md | false |
| `quickstart-check` | bundled examples | copied examples, packet artifacts | true |
| `selfcheck` | bundled examples | stdout JSON | true |
| `public-scan` | repo root | stdout JSON, optional JSON file | false |
| `release-manifest` | repo root | stdout JSON, optional JSON file | false |
| `maturity-report` | repo root | stdout JSON, optional JSON file | false |
| `schema-export` | built-in schema metadata | schema_guide.json, schema_guide.md | false |
| `fixture-doctor` | bundled or supplied examples | fixture_doctor.json, fixture_doctor.md | true |
| `docs-export` | README and generated release evidence | static-docs/index.html, static-docs/index.md, static-docs/*.md | true |
