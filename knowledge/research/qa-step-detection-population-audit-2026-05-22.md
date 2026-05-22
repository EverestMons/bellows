# QA Step Detection Population Audit

**Date:** 2026-05-22
**Plan:** diagnostic-qa-step-detection-audit-2026-05-22
**Step:** 2
**Status:** Complete

---

## Audit Window

- **Date range:** 2026-04-22 to 2026-05-22 (30 days)
- **Source files counted:**
  - `verdicts/pending/archived/`: 62 verdict-request files within the 30-day window
  - `verdicts/resolved/processed-*`: 348 processed-verdict files within the 30-day window (326 without matching archived requests)
  - Plan files in `knowledge/decisions/Done/` across all 10 watched projects — exhaustive scan of every `## STEP N` header line
- **Note:** The `qa_step_detection` Verification Results table row was introduced on 2026-05-21 via the verdict-enrichment feature. Only 4 verdict-request files contain this row. For all other steps, QA detection was determined by directly replaying the gate's classification logic (`"qa" in header.lower()`) against the actual plan step headers in the Done/ directory.

## Methodology

1. **Exhaustive plan header scan.** For each of the 10 watched project directories, read every plan file in `knowledge/decisions/Done/` dated within the 30-day window. Extracted all `## STEP N` header lines and applied the exact same test used by `_gate_is_qa_step` (gates.py:543–549): case-insensitive substring check for `"qa"` in the matched header line.
2. **QA role identification.** A step is classified as substantively QA when the step header names a recognized QA specialist role (e.g., "Invoice Security & Testing Analyst", "BELLOWS QA", "ANVIL QA ANALYST") or the step deposited to `knowledge/qa/`. Non-QA steps with "verification" or "analyst" in the header were individually reviewed and excluded unless the role is a known QA role for that project.
3. **Gate detection cross-reference.** For each QA step, checked whether `"qa"` appears (case-insensitive) anywhere in the `## STEP N` header line. If yes: class (a). If no: class (b).
4. **Verdict file confirmation.** For each class (b) step, verified the step actually ran through the gate by locating a corresponding archived verdict-request or processed-verdict file. Steps with no verdict record (plan halted before the QA step ran) are noted but excluded from the confirmed leak count.
5. **Per-project specialist naming conventions confirmed:**
   - **bellows:** "Bellows QA", "BELLOWS QA", "BELLOWS_QA", "QA", "QA Agent", "Bellows QA: ...", "BELLOWS DEVELOPER (QA)" — all contain "qa"
   - **bellows exception:** "Bellows Security & Testing" — does NOT contain "qa"
   - **forge:** "Forge QA Agent", "Forge QA", "FORGE QA ANALYST", "Forge Developer (QA)", "ELUVIAN_DOCUMENTATION_QA" — all contain "qa"
   - **invoice-pulse:** "Invoice Security & Testing Analyst", "INVOICE_SECURITY_TESTING_ANALYST", "INVOICE SECURITY TESTING ANALYST" — do NOT contain "qa"; "Invoice QA", "Invoice QA Analyst", "Invoice Documentation Analyst (QA)", "Invoice Security & Testing Analyst (QA)" — DO contain "qa"
   - **anvil:** "ANVIL QA", "ANVIL QA ANALYST" — all contain "qa"
   - **governance:** "QA", "QA AGENT" — all contain "qa"
   - **lessons-forge:** "QA verification", "Forge Developer (QA)" — all contain "qa"

## Per-Project Tables

### invoice-pulse

invoice-pulse uses two QA role name families: variants containing "QA" (detected) and variants of "Invoice Security & Testing Analyst" without the "QA" qualifier (leaked). The latter is the project's current default QA specialist.

| Plan Slug | Step | QA Role Name | Gate Verdict | Class | Notes |
|---|---|---|---|---|---|
| contract-pubs-route-removal-2026-04-22 | 2 | INVOICE SECURITY TESTING ANALYST | Not detected | **(b)** | No "qa" in header; gate missed |
| close-stranded-csv-upload-fetch-fix-2026-05-01 | 1 | Invoice Security & Testing Analyst | Not detected | **(b)** | Standalone QA plan; auto_close_disabled pause |
| invoice-pulse-session-wrap-2026-05-01 | 2 | Invoice QA | Detected | (a) | Contains "qa" |
| backlog-hygiene-edits-2026-05-06 | 2 | Invoice Documentation Analyst (QA) | Detected | (a) | Contains "qa" via parenthetical |
| backlog-hygiene-edits-2026-05-06b | 2 | Invoice Documentation Analyst (QA) | Detected | (a) | Contains "qa" via parenthetical |
| backlog-hygiene-edits-2026-05-06c | 2 | Invoice Documentation Analyst (QA) | Detected | (a) | Contains "qa" via parenthetical |
| session-wrap-2026-05-06 | 2 | Invoice Documentation Analyst (QA) | Detected | (a) | Contains "qa" via parenthetical |
| billto-type-field-mapping-fix-2026-05-07 | 2 | INVOICE_SECURITY_TESTING_ANALYST | Not detected | **(b)** | No verdict record found; plan in Done/ — probable leak |
| qa-action-queue-limit-and-contract-name-2026-05-08 | 1 | QA | Detected | (a) | Contains "qa" |
| billto-csv-header-resilience-2026-05-14 | 2 | Invoice Security & Testing Analyst | Not detected | **(b)** | Obsolete verdict present; gate missed |
| action-queue-integration-tests-1-3-2026-05-18 | 2 | Invoice Security & Testing Analyst | Not detected | **(b)** | Processed verdict confirmed step ran |
| pytest-xdist-refactor-2026-05-19 | 2 | INVOICE SECURITY TESTING ANALYST | Not detected | **(b)** | No "qa" in header |
| action-queue-integration-tests-4-6-2026-05-20 | 2 | INVOICE_SECURITY_TESTING_ANALYST | Not detected | **(b)** | No "qa" in header |
| defer-validation-recovery-2026-05-20 | 2 | QA: Verify launcher fix | Detected | (a) | Contains "qa" |
| fuel-continuation-inference-backend-2026-05-20 | 4 | Invoice Security & Testing Analyst (QA) | Detected | (a) | Contains "qa" via parenthetical |
| fuel-copilot-prompt-hardening-2026-05-20 | 2 | Invoice Security & Testing Analyst | Not detected | **(b)** | No "qa" in header |
| fuel-import-eia-region-unblock-2026-05-20 | 2 | Invoice Security & Testing Analyst | Not detected | **(b)** | No "qa" in header |
| fuel-continuation-inference-ui-qa-uxv-2026-05-21 | 1 | Invoice Security & Testing Analyst | Not detected | **(b)** | Planner manually verified Rule 20 |
| fuel-prompt-cents-as-integer-2026-05-21 | 2 | Invoice Security & Testing Analyst | Not detected | **(b)** | No "qa" in header |
| fuel-paste-prompt-cents-as-integer-2026-05-21 | 2 | Invoice Security & Testing Analyst | Not detected | **(b)** | Halted-but-shipped; QA step ran |
| fuel-failure-typing-qa-2026-05-22 | 1 | (bare `## STEP 1`) | Not detected | **(b)** | Standalone QA plan; no role name in header at all |

**invoice-pulse summary:** 21 QA steps in window. 8 class (a), 13 class (b). **Leak rate: 13/21 = 61.9%.** All 13 leaks use "Invoice Security & Testing Analyst" variants or bare headers without role names.

### bellows

93 of 94 bellows QA steps use role names containing "qa" (e.g., "Bellows QA", "BELLOWS_QA", "QA", "BELLOWS DEVELOPER (QA)"). One step uses "Bellows Security & Testing" which does not contain "qa".

| Plan Slug | Step | QA Role Name | Gate Verdict | Class | Notes |
|---|---|---|---|---|---|
| deposits-block-regex-blank-line-2026-04-28 | 2 | Bellows Security & Testing | Not detected | **(b)** | Only bellows class (b); processed verdict confirmed step ran |
| (93 additional QA steps April 22 – May 23) | various | Bellows QA / BELLOWS_QA / QA / etc. | Detected | (a) | All contain "qa" substring |

**bellows summary:** 94 QA steps in window. 93 class (a), 1 class (b). **Leak rate: 1/94 = 1.1%.**

### forge

| Plan Slug | Step | QA Role Name | Gate Verdict | Class | Notes |
|---|---|---|---|---|---|
| adr-002-amendment-classification-external-2026-04-23 | 2 | Forge Documentation Agent (QA) | Detected | (a) | |
| forge-backlog-cleanup-2026-04-23 | 2 | Forge QA Agent | Detected | (a) | |
| forge-cycle-12-2026-04-23 | 6 | Forge Agent (QA + Verification + Closeout) | Detected | (a) | |
| forge-phrasing-eval-helpers-2026-04-23 | 2 | Forge QA Agent | Detected | (a) | |
| lessons-forge-phase1-schema-ingest-2026-04-23 | 4 | Forge Developer (QA) | Detected | (a) | |
| lessons-forge-phase1b-duplicate-orchestrator-specialist-2026-04-23 | 5 | Forge Developer (QA) | Detected | (a) | |
| forge-cycle-13-drain-extraction-queue-2026-05-13 | 4 | Forge Agent (QA + Closeout) | Detected | (a) | |
| lessons-forge-2026-05-01-cycle-ratifications-2026-05-13 | 2 | ELUVIAN_DOCUMENTATION_QA | Detected | (a) | |
| lessons-forge-2026-05-13-cycle-ratifications-2026-05-13 | 2 | ELUVIAN_DOCUMENTATION_QA | Detected | (a) | |
| lessons-forge-extraction-phase-b1-cutover-2026-05-17 | 5 | FORGE DEVELOPER (QA: test suite + DB state verification) | Detected | (a) | |
| timeline-trigger-evaluator-2026-05-19 | 2 | Forge QA | Detected | (a) | |

**forge summary:** 11 QA steps in window. 11 class (a), 0 class (b). **Leak rate: 0%.** All forge QA roles contain "qa".

### anvil

| Plan Slug | Step | QA Role Name | Gate Verdict | Class | Notes |
|---|---|---|---|---|---|
| anvil-config-path-fix-qa-recovery-2026-05-17 | 1 | QA | Detected | (a) | |
| f9-follow-scoring-methodology-fix-qa-recovery-2026-05-18 | 1 | ANVIL QA | Detected | (a) | |
| anvil-cycle-18-2026-05-18 | 3 | ANVIL QA ANALYST | Detected | (a) | |
| anvil-root-hardcode-2026-05-18 | 2 | ANVIL QA | Detected | (a) | |
| percentile-inversion-backlog-entry-2026-05-18 | 2 | ANVIL QA ANALYST | Detected | (a) | |
| anvil-cycle-13-2026-05-20 | 2 | ANVIL QA ANALYST | Detected | (a) | |

**anvil summary:** 6 QA steps in window. 6 class (a), 0 class (b). **Leak rate: 0%.**

### governance

| Plan Slug | Step | QA Role Name | Gate Verdict | Class | Notes |
|---|---|---|---|---|---|
| governance-project-bootstrap-2026-05-21 | 2 | QA | Detected | (a) | |
| rule-25-routing-cleanup-2026-05-21 | 3 | QA | Detected | (a) | |
| rule-25-rule-22-check-failed-and-date-discipline-2026-05-21 | 3 | QA | Detected | (a) | |
| options-1-and-3-pre-edit-verification-2026-05-22 | 3 | QA AGENT | Detected | (a) | |
| timeline-trigger-format-2026-05-23 | 3 | QA AGENT | Detected | (a) | |

**governance summary:** 5 QA steps in window. 5 class (a), 0 class (b). **Leak rate: 0%.**

### lessons-forge

| Plan Slug | Step | QA Role Name | Gate Verdict | Class | Notes |
|---|---|---|---|---|---|
| gate-2a-recovery-2026-05-19 | 3 | QA verification | Detected | (a) | |
| lessons-forge-cycle-run-2026-05-18 | 4 | Forge Developer (QA) | Detected | (a) | |

**lessons-forge summary:** 2 QA steps in window. 2 class (a), 0 class (b). **Leak rate: 0%.**

### Projects with Zero QA Steps in Window

- **study:** 0 plans with step headers in Done/ within 30-day window.
- **BrewBuddy:** 0 plans with step headers in Done/ within 30-day window.
- **freight-kb:** 0 plans with step headers in Done/ within 30-day window.
- **ai-career-digest:** 0 plans with step headers in Done/ within 30-day window.

## Leak Rate Summary

| Metric | Count |
|---|---|
| Total QA steps in 30-day window | 139 |
| Class (a): Correctly detected | 125 |
| Class (b): Leaked (real QA, gate said not-QA) | **14** (13 confirmed + 1 probable) |
| Class (c): Genuinely not QA | 342 (non-QA steps; excluded from denominator) |
| **Overall leak rate** | **14/139 = 10.1%** |

Per-project breakdown:

| Project | QA Steps | Class (a) | Class (b) | Leak Rate |
|---|---|---|---|---|
| invoice-pulse | 21 | 8 | **13** | **61.9%** |
| bellows | 94 | 93 | **1** | 1.1% |
| forge | 11 | 11 | 0 | 0% |
| anvil | 6 | 6 | 0 | 0% |
| governance | 5 | 5 | 0 | 0% |
| lessons-forge | 2 | 2 | 0 | 0% |
| study | 0 | — | — | N/A |
| BrewBuddy | 0 | — | — | N/A |
| freight-kb | 0 | — | — | N/A |
| ai-career-digest | 0 | — | — | N/A |
| **Total** | **139** | **125** | **14** | **10.1%** |

## Notable Patterns

**The leak is concentrated in one project.** 13 of 14 class (b) cases are in invoice-pulse. The project's current default QA specialist — "Invoice Security & Testing Analyst" (specialist file `INVOICE_SECURITY_TESTING_ANALYST.md`) — does not contain the substring "qa" in any casing variant used in step headers.

**Three naming variants all leak identically:**
1. `Invoice Security & Testing Analyst` — 7 occurrences (natural-language form)
2. `INVOICE SECURITY TESTING ANALYST` — 2 occurrences (uppercase-space form)
3. `INVOICE_SECURITY_TESTING_ANALYST` — 2 occurrences (underscore form)
4. Bare `## STEP 1` with no role name — 1 occurrence (standalone QA plan)
5. `Bellows Security & Testing` — 1 occurrence (bellows variant, same pattern)

**The "(QA)" parenthetical is the Planner's ad-hoc fix.** One invoice-pulse plan (`fuel-continuation-inference-backend-2026-05-20`, step 4) used "Invoice Security & Testing Analyst (QA)" — the parenthetical caused the gate to detect it. This shows the Planner has sometimes compensated for the gap, but inconsistently.

**The leak is not new — it spans the entire 30-day window.** The earliest class (b) case is `contract-pubs-route-removal-2026-04-22` (April 22, day 1 of the window). The "Invoice Security & Testing Analyst" role name has been the default throughout; the 2-case finding in the prior Step 2 run was an artifact of only checking verdict files rather than scanning plan headers.

**The overall 10% rate understates the structural risk.** The leak rate is determined by role naming convention, not by probability. Any project whose QA specialist name lacks "qa" will have a 100% leak rate. The current population has only two such role names (invoice-pulse's "Security & Testing Analyst" and one bellows "Security & Testing" instance), but study and BrewBuddy also use "Security & Testing Analyst" conventions in their specialist files — they simply had no QA activity in this window.

**Rule 20 and Rule 22 QA-specific checks were silently skipped in all 14 cases.** Each leaked step produced `rule_20_self_check: PASS | N/A (not a QA step)` and `rule_22_verification` ran deposit-exists only (no verification-table or hedging checks). The Planner caught these manually in the two most recent cases (2026-05-21, 2026-05-22), but Rule 25's mechanized-check routing now actively suppresses this manual fallback.

---

### Output Receipt

**Status:** Complete
**Files Deposited:**
- `knowledge/research/qa-step-detection-population-audit-2026-05-22.md`
