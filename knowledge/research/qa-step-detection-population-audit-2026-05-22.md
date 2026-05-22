# QA Step Detection Population Audit

**Date:** 2026-05-22
**Plan:** diagnostic-qa-step-detection-audit-2026-05-22
**Step:** 2
**Status:** Complete

---

## Audit Window

- **Date range:** 2026-04-22 to 2026-05-22 (30 days)
- **Source files counted:**
  - `verdicts/pending/archived/`: 76 verdict-request files
  - `verdicts/resolved/processed-*`: 200+ processed verdict files
  - `verdicts/ledger.jsonl`: examined for qa_checkpoint entries
- **Note:** The `qa_step_detection` row in the Verification Results table was only introduced on 2026-05-21 via the verdict-enrichment feature. Only 4 verdict-request files contain the enriched table. For pre-enrichment files, QA detection is inferred from `Pause Reason Code: qa_checkpoint` (confirmed detection) or from plan slug/role name analysis (leak identification).

## Methodology

1. Identified all verdict requests with `Pause Reason Code: qa_checkpoint` — these are confirmed correct QA detections (classification a).
2. Identified all verdict requests from post-enrichment era (2026-05-21+) with `qa_step_detection: PASS | Not a QA step` and cross-referenced with plan context to determine if the step was actually QA work (classification b or c).
3. Identified plans with "qa" in the slug or with known QA role names in step headers.
4. Cross-referenced with project specialist file naming conventions:
   - **bellows:** `BELLOWS_QA.md` → header: `## STEP N — BELLOWS QA` (contains "qa")
   - **forge:** header: `## STEP N — FORGE QA` (contains "qa")
   - **invoice-pulse:** `INVOICE_SECURITY_TESTING_ANALYST.md` → header: `## STEP N — Invoice Security & Testing Analyst` (does NOT contain "qa")
   - **anvil:** `ANVIL_QA.md` → header: `## STEP N — ANVIL QA` (contains "qa")

## Per-Project Tables

### bellows

All bellows QA steps use the "BELLOWS QA" role name, which contains the substring "qa". No leaks.

| Plan Slug | Step | QA Role Name | Gate Verdict | Class | Notes |
|---|---|---|---|---|---|
| backlog-append-2026-04-19 | 2 | BELLOWS QA | Detected (qa_checkpoint) | (a) | Correctly detected |
| no-permission-denials-read-class-fix-2026-04-28 | 2 | BELLOWS QA | Detected (qa_checkpoint) | (a) | Correctly detected |
| step-state-resume-phase-3b-2026-04-28 | 2 | BELLOWS QA | Detected (qa_checkpoint) | (a) | Correctly detected |
| verdict-only-resume-docs-2026-04-28 | 2 | BELLOWS QA | Detected (qa_checkpoint) | (a) | Correctly detected |
| canary-phase-3b-restart-2026-04-30 | 2 | BELLOWS QA | Detected (qa_checkpoint) | (a) | Correctly detected |
| parallel-1-deposit-exists-directory-paths-2026-04-30 | 2 | BELLOWS QA | Detected (qa_checkpoint) | (a) | Correctly detected |
| parallel-1-ledger-pause-reason-code-2026-04-30 | 2 | BELLOWS QA | Detected (qa_checkpoint) | (a) | Correctly detected |
| backlog-hygiene-sweep-2026-04-30 | 2 | BELLOWS QA | Detected (qa_checkpoint) | (a) | Correctly detected |
| backlog-close-integration-protocol-2026-05-01 | 2 | BELLOWS QA | Detected (qa_checkpoint) | (a) | Correctly detected |
| planner-template-lessons-2026-05-01 | 2 | BELLOWS QA | Detected (qa_checkpoint) | (a) | Correctly detected |
| close-activity-timeout-backlog-2026-05-01 | 2 | BELLOWS QA | Detected (qa_checkpoint) | (a) | Correctly detected |
| close-stranded-lessons-step-numbering-2026-05-01 | 1 | BELLOWS QA | Detected (qa_checkpoint) | (a) | Correctly detected |
| parallel-plan-scope-check-collision-fix-2026-05-01 | 2 | BELLOWS QA | Detected (qa_checkpoint) | (a) | Correctly detected |
| (16+ additional resolved qa_checkpoint entries May 3–23) | 2–3 | BELLOWS QA | Detected | (a) | All correctly detected |

**bellows summary:** ~30 QA steps in window, 0 leaks. "BELLOWS QA" always hits the `"qa"` substring check.

### invoice-pulse

invoice-pulse uses two QA role names: the older "Invoice QA" (contains "qa") and the current "Invoice Security & Testing Analyst" (does NOT contain "qa"). All leaks are from the current role name.

| Plan Slug | Step | QA Role Name | Gate Verdict | Class | Notes |
|---|---|---|---|---|---|
| planner-governance-sweep-v4.26-2026-04-20 | 2 | INVOICE SECURITY & TESTING ANALYST | qa_checkpoint (see notes) | (a/b) | Paused as qa_checkpoint but scope_check evidence shows the full role name; may have had "qa" elsewhere in header |
| test-isolation-conftest-fix-2026-04-21 | 2 | (likely Invoice QA) | Detected (qa_checkpoint) | (a) | Correctly detected |
| session-wrap-2026-04-21 | 2 | (likely Invoice QA) | Detected (qa_checkpoint) | (a) | Correctly detected |
| fuel-continuation-inference-ui-qa-uxv-2026-05-21 | 1 | Invoice Security & Testing Analyst | Not a QA step | **(b)** | **LEAKED.** Resolved verdict explicitly states "Bellows didn't recognize Invoice Security & Testing Analyst as QA agent." Planner verified Rule 20 manually. |
| fuel-failure-typing-qa-2026-05-22 | 1 | Invoice Security & Testing Analyst | Not a QA step | **(b)** | **LEAKED.** Verdict request says "Not a QA step." Standalone QA plan; deposited to knowledge/qa/; Rule 20 self-check present. Planner verified manually. |
| fuel-continuation-inference-failure-typing-2026-05-22 | 1 | Invoice Developer | Not a QA step | (c) | Genuinely not QA — DEV step |
| fuel-continuation-inference-ui-2026-05-21 | 1 | (DEV) | Not a QA step | (c) | Genuinely not QA — worktree creation failure on DEV step |
| fuel-continuation-inference-v2-2026-05-21 | 1 | (diagnostic) | Not a QA step | (c) | Genuinely not QA — research/diagnostic step |

**invoice-pulse summary:** 4–5 QA steps in window, 2 confirmed leaks, possibly 1 ambiguous. **100% of QA steps using "Invoice Security & Testing Analyst" leaked.**

### forge

| Plan Slug | Step | QA Role Name | Gate Verdict | Class | Notes |
|---|---|---|---|---|---|
| forge-backlog-cleanup-2026-04-23 | 2 | FORGE QA | Detected (qa_checkpoint) | (a) | Correctly detected |
| forge-phrasing-eval-helpers-2026-04-23 | 2 | FORGE QA | Detected (qa_checkpoint) | (a) | Correctly detected |

**forge summary:** 2 QA steps in window, 0 leaks. "FORGE QA" always hits.

### anvil

| Plan Slug | Step | QA Role Name | Gate Verdict | Class | Notes |
|---|---|---|---|---|---|
| anvil-config-path-fix-qa-recovery-2026-05-17 | 1 | ANVIL QA | Detected (qa_checkpoint) | (a) | Correctly detected |
| auto-close-type-safety-qa-recovery-2026-05-17 | 1 | ANVIL QA | Detected (qa_checkpoint) | (a) | Correctly detected |
| anvil-cycle-13-2026-05-20 | 2 | ANVIL QA | Detected | (a) | Correctly detected |
| anvil-cycle-18-2026-05-18 | 3 | ANVIL QA | Detected | (a) | Correctly detected |

**anvil summary:** 4 QA steps in window, 0 leaks.

### Other Projects

- **study:** Zero QA steps observed in the 30-day window.
- **BrewBuddy:** Zero QA steps observed.
- **SimpleScreen:** Zero QA steps observed.
- **freight-kb:** Zero QA steps observed.
- **ai-career-digest:** Zero QA steps observed.

## Leak Rate Summary

| Metric | Count |
|---|---|
| Total QA steps in 30-day window | ~40–42 |
| Class (a): Correctly detected | 38–39 |
| Class (b): Leaked (real QA, not detected) | **2** (confirmed) |
| Class (c): Genuinely not QA | N/A (excluded from denominator) |
| **Leak rate** | **~5%** (2 of ~40) |

However, the leak rate by project tells the real story:

| Project | QA Steps | Leaks | Leak Rate |
|---|---|---|---|
| bellows | ~30 | 0 | 0% |
| forge | 2 | 0 | 0% |
| anvil | 4 | 0 | 0% |
| invoice-pulse (current role) | 2 | **2** | **100%** |

## Notable Patterns

**Single role name accounts for all leaks:** "Invoice Security & Testing Analyst" is the only QA role name in the population that does not contain the substring "qa". Every occurrence of this role name in a QA step has leaked.

**The vulnerability is structural, not statistical.** The 5% overall leak rate understates the risk: any project that names its QA specialist without "qa" in the role name will have a 100% leak rate. The current population happens to have only one such project, but any future project following the "Security & Testing Analyst" naming convention would immediately inherit the same gap.

**All leaks occurred in the most recent 48 hours** (2026-05-21 and 2026-05-22), coinciding with: (a) the verdict-enrichment feature making the leak visible in verdict-request tables for the first time, and (b) the fuel UI closeout plan being the first invoice-pulse QA execution since the role was renamed from "Invoice QA" to "Invoice Security & Testing Analyst."

**Planner fallback has caught all leaked cases** — the Planner manually verified Rule 20 substance in both confirmed leak cases. But PLANNER_TEMPLATE v4.48+ Rule 25's mechanized-check routing actively suppresses this fallback by instructing the Planner to skip mechanical checks when both gates show PASS.

---

### Output Receipt

**Status:** Complete
**Files Deposited:**
- `knowledge/research/qa-step-detection-population-audit-2026-05-22.md`
