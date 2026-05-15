# Deposit-Exists Prose-Path Canary — QA Report
**Date:** 2026-04-28 | **Agent:** Bellows QA | **Plan:** executable-deposit-exists-prose-canary-2026-04-28

---

## 1. Rule 17 Deliverable Verification

| Deliverable | Expected | Status | Evidence |
|---|---|---|---|
| `bellows/knowledge/research/deposit-exists-prose-canary-findings-2026-04-28.md` | Findings file describing canary test, prose-distractor pattern, expected gate behavior | PASS | `knowledge/qa/evidence/executable-deposit-exists-prose-canary-2026-04-28/grep_findings_file.txt` — grep confirms signature phrase present |
| `bellows/knowledge/development/deposit-exists-prose-canary-dev-log-2026-04-28.md` | Dev log with verbatim findings content, post-write verification, anomalies, Output Receipt | PASS | File exists, Output Receipt status = Complete, 2 deposits listed |
| Step 1 commit | `test: deposit-exists prose-path canary — findings + dev log` | PASS | `knowledge/qa/evidence/executable-deposit-exists-prose-canary-2026-04-28/git_log.txt` — commit `2ac772d` confirmed |

---

## 2. Deposit-Exists Gate Evaluation — Canary Result

The Step 1 resolved verdict (`verdicts/resolved/processed-verdict-deposit-exists-prose-canary-2026-04-28-step-1.md`) states:

> verdict: continue
>
> Rule 22 verification passed for canary's actual deliverable (deposit_exists gate did NOT trip on prose paths — structural fix confirmed live, BACKLOG #1 closeable).

**Finding:** The `deposit_exists` gate did NOT flag the prose-embedded directory references (`bellows/knowledge/decisions/` and `bellows/knowledge/decisions/Done/`) that produced the original 2026-04-23 false positive. The `_extract_plan_required_deposits()` function correctly scoped extraction to the declared `**Deposits:**` block and ignored prose distractors.

**Conclusion:** The structural fix shipped 2026-04-19 holds under the same prose-distractor density that caused the original failure. BACKLOG item "deposit_exists false positive on prose-embedded directory paths" is closeable.

---

## 3. Rule 20 Self-Check Output

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
plan_slug: executable-deposit-exists-prose-canary-2026-04-28
qa_report_path: bellows/knowledge/qa/deposit-exists-prose-canary-qa-2026-04-28.md
evidence_dir: bellows/knowledge/qa/evidence/executable-deposit-exists-prose-canary-2026-04-28/

Checking required evidence files:
  [OK] grep_findings_file.txt — exists, non-empty (2 lines)
  [OK] git_log.txt — exists, non-empty (1 lines)

Evidence files verified: 2/2
Hedging keywords scan: NONE FOUND
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: bellows/knowledge/qa/evidence/executable-deposit-exists-prose-canary-2026-04-28/
Files verified: 2
============================================================
```

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Executed Rule 17 deliverable verification for Step 1's two deposits + commit. Confirmed `deposit_exists` gate did not trip on prose-embedded directory paths during Step 1 dispatch (via resolved verdict). Ran Rule 20 self-check — PASSED.

### Files Deposited
- `bellows/knowledge/qa/deposit-exists-prose-canary-qa-2026-04-28.md` — this QA report
- `bellows/knowledge/qa/evidence/executable-deposit-exists-prose-canary-2026-04-28/grep_findings_file.txt` — grep evidence
- `bellows/knowledge/qa/evidence/executable-deposit-exists-prose-canary-2026-04-28/git_log.txt` — git log evidence

### Files Created or Modified (Code)
- None (QA verification only)

### Decisions Made
- BACKLOG item "deposit_exists false positive on prose-embedded directory paths" confirmed closeable — structural fix holds under canary conditions

### Flags for CEO
- None

### Flags for Next Step
- None (final step)
