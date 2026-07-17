# Promotion Audit v0.8.0

Audit date: 2026-07-18
Product: `portfolio-liquidity-runway-lab`
Version audited: `0.8.0`
Audit stance: product, market, and promotion readiness for a finance-adjacent offline CLI utility.

Boundary to preserve in every promotion surface: educational static analysis only; local synthetic or user-supplied inputs; no live data, broker connection, order placement, or tax, legal, investment, buy, sell, or hold advice.

## Sources And Commands Reviewed

Paths reviewed:

- `README.md`
- `docs/release-deck/release_deck.md`
- `docs/command-matrix/command_matrix.md`
- `demo/visual_receipt.md`
- `docs/evidence-bundle/index.md`
- `docs/evidence-bundle/command_replay.md`
- `docs/evidence-bundle/boundary_risks.md`
- `docs/template-pack/README.md`
- `docs/cold_start_walkthrough.md`
- `docs/release_readiness_review.md`
- `docs/release_check.md`
- `docs/maturity_report.json`
- `docs/artifact_catalog.md`
- `docs/golden-replay/golden_replay.md`
- `demo/scenario-gallery/scenario_gallery.md`
- `demo/assumption-audit/assumption_audit.md`
- `demo/casebook/casebook.md`
- `tests/test_cli.py`
- `tests/test_core.py`

Commands used for this audit:

```bash
pwd && rg --files
git status --short
sed -n '1,240p' README.md
sed -n '1,260p' docs/release-deck/release_deck.md
sed -n '1,260p' docs/command-matrix/command_matrix.md
sed -n '1,240p' demo/visual_receipt.md
sed -n '1,260p' docs/evidence-bundle/index.md
sed -n '1,240p' docs/evidence-bundle/command_replay.md
sed -n '1,240p' docs/evidence-bundle/boundary_risks.md
sed -n '1,260p' docs/template-pack/README.md
sed -n '1,260p' docs/release_readiness_review.md
sed -n '1,220p' docs/release_check.md
sed -n '1,260p' docs/cold_start_walkthrough.md
sed -n '1,260p' docs/artifact_catalog.md
sed -n '1,260p' docs/golden-replay/golden_replay.md
sed -n '1,240p' docs/maturity_report.json
sed -n '1,620p' tests/test_cli.py
sed -n '1,680p' tests/test_core.py
find docs/release-audits -maxdepth 1 -type f -print -exec sed -n '1,220p' {} \;
sed -n '1,260p' demo/scenario-gallery/scenario_gallery.md
sed -n '1,220p' demo/assumption-audit/assumption_audit.md
sed -n '1,220p' demo/casebook/casebook.md
```

## Target User Definition

Primary user: a financially literate operator, founder, analyst, family-office staffer, or fractional finance lead who already maintains offline records and needs a repeatable packet for liquidity, reserve, runway, and assumption review. This user is comfortable with CSV/JSON or can work from spreadsheet exports, but does not want a broker-connected tool or live financial data dependency.

Best-fit buyer/user situations:

- A founder or operator preparing a board, lender, advisor, or household liquidity discussion from local records.
- An analyst comparing portfolio liquidity under base, stress, income-shock, and reserve-rebuild scenarios.
- A release owner or internal tool maintainer who needs deterministic evidence, checksums, no-JavaScript HTML, and replayable demo artifacts.
- A consultant who wants a transparent offline template pack that can be handed to clients without creating an account or connecting accounts.

Poor-fit users:

- Consumers expecting portfolio optimization, allocation advice, investment recommendations, tax planning, brokerage sync, account aggregation, market data, or automated orders.
- Teams that need continuously refreshed balances or institution-grade compliance workflows.
- Users unwilling to inspect and maintain their own input records.

## Jobs To Be Done

Functional jobs:

- When I have local portfolio, ledger, and assumptions files, I want a deterministic packet so I can review liquidity tiers, burn, reserves, runway, and warnings without live integrations.
- When I am not sure whether my inputs are usable, I want lint and assumption-audit outputs so I can find missing tiers, suspicious rates, invalid events, and schema issues before using the packet.
- When I need to compare assumptions, I want scenario gallery and batch compare artifacts so I can discuss how runway changes across stress cases and portfolio variants.
- When I need a portable review bundle, I want static Markdown/HTML/CSV/JSON outputs, checksums, and command replay notes so another reviewer can inspect the same evidence offline.
- When I am starting from a spreadsheet, I want CSV import/export and a template pack so I can move between spreadsheet workflows and the JSON packet model.

Emotional jobs:

- Reduce anxiety around "what exactly are we reviewing?" by turning scattered local records into named, reproducible artifacts.
- Build confidence that the packet can be regenerated and audited because the tool has no runtime dependencies, no JavaScript in generated HTML, and committed replay evidence.
- Keep finance-adjacent boundaries explicit so the tool feels like a review aid, not a hidden recommendation engine.

Social jobs:

- Give operators and analysts a shareable packet that looks controlled enough for an advisor, board member, or reviewer.
- Let maintainers promote the release with evidence instead of vague claims: `docs/golden-replay/golden_replay.md` reports 17 compared artifacts passing, `docs/release_check.md` reports pass, and `docs/maturity_report.json` reports all maturity checks true with score `38`.

## Demo Quality

Demo quality is strong for a technical, evidence-led launch. `README.md` gives a complete quickstart, `docs/cold_start_walkthrough.md` documents an empty-directory path, and `tests/test_cli.py` verifies `quickstart-check` creates example inputs plus `liquidity_packet.html` from an empty current working directory. The demo corpus covers packet generation, visual receipt, scenario gallery, assumption audit, batch compare, casebook, CSV import/export, static docs, command matrix, release deck, bundle checksums, evidence bundle, template pack, fixture doctor, artifact catalog, golden replay, and release check.

The best demo entry point is not the whole README command block. It is this shorter story:

```bash
portfolio-liquidity-runway-lab quickstart-check --out liquidity-demo
portfolio-liquidity-runway-lab build-packet --out liquidity-demo/packet --scenario stress
portfolio-liquidity-runway-lab visual-receipt --out liquidity-demo/visual_receipt.md --scenario stress
portfolio-liquidity-runway-lab scenario-gallery --out liquidity-demo/scenario-gallery
portfolio-liquidity-runway-lab input-lint --portfolio liquidity-demo/portfolio.json --ledger liquidity-demo/ledger.json --assumptions liquidity-demo/assumptions.json --portfolio-csv liquidity-demo/portfolio.csv --ledger-csv liquidity-demo/ledger.csv
```

Demo artifacts are concrete. `demo/visual_receipt.md` shows gross assets of `$165,000.00`, stress haircut assets of `$133,460.00`, effective monthly burn of `$7,282.83`, same-day reserve months of `4.51`, thirty-day runway months of `12.97`, tier bars, and three review signals. `demo/scenario-gallery/scenario_gallery.md` compares `base`, `stress`, `income_shock`, and `reserve_rebuild`. `demo/assumption-audit/assumption_audit.md` demonstrates review findings for missing liquidity tiers and suspicious fee/yield rates. `demo/casebook/casebook.md` is the strongest full-review artifact because it combines packet summary, cash buckets, warnings, scenario summary, audit summary, and batch compare summary.

Main demo friction: the public README is complete but too broad for first contact. It lists a release-owner evidence factory before the user has seen the smallest useful packet. Promotion should lead with the packet, visual receipt, template pack, and scenario gallery; then introduce evidence bundle and release checks as trust infrastructure.

## Artifact Differentiation

The release is differentiated less by financial modeling complexity and more by offline reproducibility, reviewability, and artifact discipline.

Clear differentiators:

- Offline-first: `README.md`, `docs/evidence-bundle/boundary_risks.md`, and generated artifacts repeatedly state no live data, broker connections, orders, or advice.
- Deterministic multi-format outputs: packet, scenario gallery, batch compare, casebook, command matrix, release deck, static docs, and evidence bundle produce JSON/Markdown and often no-JavaScript HTML.
- Spreadsheet bridge: `csv-import`, `csv-export`, `input-lint`, and `docs/template-pack/README.md` make the tool usable for spreadsheet-based operators without abandoning deterministic JSON.
- Review evidence: `docs/evidence-bundle/index.md` lists 26 copied artifacts; `docs/artifact_catalog.md` catalogs 149 artifacts with SHA256 and regeneration commands; `docs/golden-replay/golden_replay.md` reports 17/17 replay comparisons passing.
- Release-owner tooling: `fixture-doctor`, `release-check`, `public-scan`, `maturity-report`, `bundle-checksums`, `release-manifest`, and `artifact-catalog` give maintainers an unusually explicit audit surface for a small CLI.
- No runtime dependencies: `docs/release_readiness_review.md` calls this ready, and tests assert release-manifest runtime dependencies are empty in `tests/test_core.py`.

What is not differentiated:

- It is not a live personal finance app.
- It is not a tax, legal, accounting, trading, or optimization engine.
- It is not a full compliance system; `docs/evidence-bundle/boundary_risks.md` correctly states public scan and release check are release aids, not complete security or compliance audits.

## User-Facing Copy Examples

Existing copy that should be reused or lightly adapted:

- "Build deterministic local liquidity runway packets from JSON portfolio, ledger, and assumption inputs." Source: `README.md`.
- "For analysts, founders, operators, and finance teams who need static review packets for liquidity assumptions and runway discussions." Source: `README.md`.
- "Use these files as clean local starters. Replace every value with your own offline records before review." Source: `docs/template-pack/README.md`.
- "Outputs are deterministic review artifacts, not instructions to transact." Source: `docs/evidence-bundle/boundary_risks.md`.
- "HTML artifacts are static and contain no JavaScript." Source: `docs/cold_start_walkthrough.md`.

Recommended homepage/README lead copy:

```text
Portfolio Liquidity Runway Lab turns local portfolio, ledger, and assumption files into deterministic liquidity review packets: reserve months, runway rows, scenario comparisons, assumption warnings, CSV exports, and offline evidence bundles. It does not fetch live data, connect to brokers, place orders, or provide investment, tax, or legal advice.
```

Recommended CTA copy:

```text
Start with synthetic examples:
portfolio-liquidity-runway-lab quickstart-check --out liquidity-demo
```

Recommended audience copy:

```text
Built for operators, founders, analysts, and finance teams who need a repeatable offline packet before a liquidity, runway, advisor, or board review.
```

Recommended artifact copy:

```text
Every packet is local and reviewable: JSON for automation, Markdown for notes, static no-JavaScript HTML for inspection, and CSV for spreadsheet workflows.
```

## Promotion Risks

1. Release evidence inconsistency: `docs/release-deck/release_deck.md` says `Release check: fail`, while `docs/release_check.md` says `Status: pass`. Promotion should not cite the release deck status until the deck is regenerated or the discrepancy is explained.
2. README overload: `README.md` promotes more than twenty commands in the first quickstart block. This demonstrates maturity but can obscure the first useful user path.
3. Finance-adjacent wording: terms such as "forced-sale warnings" in `demo/visual_receipt.md` and `demo/casebook/casebook.md` are useful but can sound action-oriented. Promotion should consistently say "review signals" or "review prompts" around these outputs.
4. Static input risk: `docs/evidence-bundle/boundary_risks.md` states stale user inputs can make a packet misleading even when checks pass. Launch copy must repeat that users must verify inputs against source records.
5. Public-scan scope risk: release checks pass, but the existing security audit in `docs/release-audits/security_public_audit_v080.md` identifies public-scan limitations and stale/path leakage concerns. Do not oversell `public-scan` as a security audit.
6. Market category ambiguity: the product could be mistaken for a personal finance app, investment analysis tool, or cash management product. Position it as an offline review packet generator.
7. Artifact sprawl: 149 cataloged artifacts in `docs/artifact_catalog.md` is impressive for auditability but too much for launch readers. Promotion needs a curated artifact map: Packet, Visual Receipt, Scenario Gallery, Template Pack, Evidence Bundle.
8. Installation proof gap in reviewed docs: tests cover module execution and console-script assumptions are documented, but this audit did not run a wheel-install smoke. `docs/release_readiness_review.md` includes wheel smoke documentation as a checklist item.

## Launch Snippets

1. Short launch post:

```text
Released portfolio-liquidity-runway-lab v0.8.0: an offline CLI that turns local portfolio, ledger, and assumptions files into deterministic liquidity runway packets, scenario comparisons, CSV exports, and static review artifacts. No live data, no broker connection, no orders, no advice.
```

2. Technical audience:

```text
v0.8.0 is built around reproducibility: JSON/Markdown/static HTML packets, CSV import/export, scenario galleries, assumption audits, batch compares, casebooks, SHA256 manifests, evidence bundles, and golden replay checks. Start with: portfolio-liquidity-runway-lab quickstart-check --out liquidity-demo
```

3. Operator/founder audience:

```text
Before a runway or liquidity discussion, generate a local review packet from your own offline records: reserve months, burn, scenario stress, liquidity tiers, and review prompts. The tool is deliberately static and does not connect to accounts or recommend transactions.
```

4. Template-pack angle:

```text
Start from clean CSV/JSON templates, lint the inputs, build a stress packet, and export the results back to spreadsheet-friendly CSV. The template pack is designed for offline records, not account aggregation.
```

5. Evidence-led launch:

```text
The v0.8.0 release includes an offline evidence bundle, command matrix, artifact catalog, release check, maturity report, and golden replay summary, so reviewers can inspect what shipped and how to regenerate it.
```

## Weighted Promotion Gate Rubric

Promotion gate score: `82/100`.

Gate recommendation: pass for a targeted technical/finance-operations launch; hold back from broad consumer-finance promotion until release-deck inconsistency, README onboarding focus, and finance wording are tightened.

| Category | Weight | Score | Weighted | Rationale |
| --- | ---: | ---: | ---: | --- |
| Target clarity | 15 | 13 | 13.0 | README names analysts, founders, operators, and finance teams; poor-fit users need sharper exclusion in promotion. |
| JTBD strength | 15 | 14 | 14.0 | Strong fit for offline packet generation, scenario comparison, input linting, and evidence review. |
| Demo quality | 15 | 12 | 12.0 | Demos are concrete and tested, but README's first path is overloaded. |
| Artifact differentiation | 15 | 14 | 14.0 | Offline deterministic multi-format artifacts, checksums, evidence bundles, and no-JS HTML are meaningful differentiators. |
| Trust and proof | 15 | 12 | 12.0 | Tests, release check, maturity report, artifact catalog, and golden replay are strong; release deck status inconsistency weakens trust. |
| Boundary and compliance hygiene | 10 | 8 | 8.0 | Boundary is repeated everywhere, but promotion must avoid action-oriented financial phrasing and overselling scans. |
| Copy readiness | 10 | 7 | 7.0 | Good raw copy exists; launch copy needs hierarchy and a shorter first-run CTA. |
| Market reach | 5 | 2 | 2.0 | Strong niche utility, but limited appeal outside CLI-comfortable users and offline-review workflows. |

Minimum launch conditions:

- Do not publish copy that says or implies recommendations, optimization, trading, live balances, or professional advice.
- Lead with `quickstart-check`, `build-packet`, `visual-receipt`, `scenario-gallery`, and `template-pack`; keep release-owner commands as proof points.
- Cite `docs/release_check.md`, `docs/golden-replay/golden_replay.md`, and `docs/maturity_report.json` only if regenerated status remains consistent.
- Keep "local records must be verified" near every launch artifact example.
- Avoid using `docs/release-deck/release_deck.md` as-is while it reports `Release check: fail`.
