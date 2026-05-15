# Output Receipt Capture Completeness Audit — Findings

**Date:** 2026-05-12
**Window:** 2026-04-28 → 2026-05-12 (14 days)
**Populations:** Bellows `knowledge/decisions/Done/`, Invoice-pulse `knowledge/decisions/Done/`
**Plan count:** 142 Done plans total (118 bellows, 24 invoice-pulse)
**DEV plans (target population):** 82 (68 bellows, 14 invoice-pulse)
**Sample partition:** Stratified: 5 oldest + 20 random (seed 42) + 5 newest = 30 of 82 DEV plans. Part 3 grep totals reported across full 82-plan population; Parts 4–7 on the 30-plan sample.
**Disposition:** Observation-only. No recommendations.

---

## Final Extended Grep List

Starting list (20 phrases) plus 15 phrases discovered through pattern analysis of the 5 highest-content assistant text files:

| # | Phrase (case-insensitive) | Source |
|---|---|---|
| 1 | `had to` | Starting |
| 2 | `decided to` | Starting |
| 3 | `on initiative` | Starting |
| 4 | `noticed that` | Starting |
| 5 | `chose to` | Starting |
| 6 | `I'll update` | Starting |
| 7 | `I need to update` | Starting |
| 8 | `I'll modify` | Starting |
| 9 | `not in the plan` | Starting |
| 10 | `not mentioned` | Starting |
| 11 | `unclear from the plan` | Starting |
| 12 | `assumed` | Starting |
| 13 | `defaulted to` | Starting |
| 14 | `since the plan` | Starting |
| 15 | `the plan doesn't specify` | Starting |
| 16 | `went with` | Starting |
| 17 | `opted for` | Starting |
| 18 | `corrected the` | Starting |
| 19 | `I'll go with` | Starting |
| 20 | `let me adjust` | Starting |
| 21 | `let me fix` / `need to fix` | Extended — 19 hits across high-content files |
| 22 | `re-run` / `rerun` | Extended — 26 hits |
| 23 | `let me also` | Extended — 21 hits |
| 24 | `found the issue` / `found that` | Extended — 9 hits |
| 25 | `returned 0` / `no matches` / `0 matches` | Extended — 9 hits |
| 26 | `actually` (followed by comma or space) | Extended — 7 hits |
| 27 | `instead of` / `instead,` | Extended — 5 hits |
| 28 | `Wait,` | Extended — corrective-realization pattern |
| 29 | `seems empty` / `seems wrong` | Extended — 3 hits |
| 30 | `doesn't exist` / `does not exist` | Extended — 12 hits (merged with "missing") |
| 31 | `didn't work` / `doesn't work` | Extended — observation-driven course correction |
| 32 | `I'll skip` / `skipping` | Extended — scope-boundary decision |
| 33 | `need to adjust` | Extended — 3 hits |

---

## Artifact Paths Confirmed (Part 1)

**Artifact location:** All per-step artifacts live in `bellows/logs/` as flat files.

**(a) Output Receipt** — the structured receipt is the `parsed.result_text` field inside each `YYYYMMDD-HHMMSS-step.json` file. This is extracted from the terminal `result` NDJSON event's `result` field. It contains the agent's final summary message for the step.

**(b) Raw `claude -p` stdout** — the full NDJSON stream is stored as the `raw_output` field inside the same `YYYYMMDD-HHMMSS-step.json` file. Claude CLI is invoked with `--output-format stream-json --verbose`. The NDJSON stream contains events of types: `system`, `user`, `assistant`, `result`, `rate_limit_event`. Intermediate agent narration (where decisions are surfaced) lives in `assistant` events, in content items of type `text`.

**(c) Other artifacts:** `parsed` field in step.json contains extracted metadata (session_id, cost_usd, receipt_status, ceo_flags, permission_denials). The `stderr` field captures stderr output. No separate "decisions" or "events" file exists.

**Critical structural observation:** Both populations (raw stdout and Output Receipt) live inside the same JSON file. There is no separate raw stdout text file. The raw stdout is the NDJSON stream (not human-readable text), requiring JSON parsing to extract the intermediate assistant narration. The step.json files are flat (not organized by plan slug) and must be mapped to plans via session_id cross-referenced against `bellows.db`.

---

## Part 3+4+5 — Per-Plan Results (30-plan sample)

### Full Population (82 DEV plans) — Part 3 Totals Only

| Metric | Count |
|---|---|
| Stdout-detected decision instances | 89 |
| Output Receipt decision instances | 8 |

### Sample Plan Table

| # | Slug | Project | Steps | Stdout instances | OR instances | α (captured) | β (leaked) | Capture rate |
|---|---|---|---|---|---|---|---|---|
| 1 | deposit-exists-prose-canary-2026-04-28 | bellows | 19 | 5 | 0 | 0 | 5 | 0.0% |
| 2 | bellows-worktree-impl-2026-05-03 | bellows | 4 | 4 | 0 | 0 | 4 | 0.0% |
| 3 | terminal-capture-2026-05-12 | bellows | 4 | 4 | 0 | 0 | 4 | 0.0% |
| 4 | phase-3c-plan-hash-drift-warning-2026-04-30 | bellows | 3 | 3 | 0 | 0 | 3 | 0.0% |
| 5 | cleanup-slug-normalization-2026-05-01 | bellows | 4 | 3 | 0 | 0 | 3 | 0.0% |
| 6 | remove-phase-3b-3c-2026-05-01 | bellows | 2 | 2 | 0 | 0 | 2 | 0.0% |
| 7 | bellows-session-wrap-final-2026-05-01 | bellows | 2 | 2 | 0 | 0 | 2 | 0.0% |
| 8 | bellows-session-wrap-2026-05-03 | bellows | 2 | 2 | 0 | 0 | 2 | 0.0% |
| 9 | failure-3-mode-a-closure-2026-05-06 | bellows | 3 | 2 | 0 | 0 | 2 | 0.0% |
| 10 | canary-phase-3b-restart-2026-04-30 | bellows | 2 | 1 | 0 | 0 | 1 | 0.0% |
| 11 | session-wrap-2026-05-05 | invoice-pulse | 1 | 1 | 0 | 0 | 1 | 0.0% |
| 12 | session-wrap-action-queue-aggregation-2026-05-07 | invoice-pulse | 1 | 1 | 0 | 0 | 1 | 0.0% |
| 13 | half-up-currency-rounding-2026-05-06 | invoice-pulse | 3 | 1 | 0 | 0 | 1 | 0.0% |
| 14 | bellows-self-exposure-wontfix-close-2026-05-12 | bellows | 2 | 1 | 0 | 0 | 1 | 0.0% |
| 15 | terminal-notification-backlog-close-2026-05-12 | bellows | 2 | 1 | 1 | 1 | 0 | 100.0% |
| 16 | backlog-hygiene-sweep-2026-04-30 | bellows | 2 | 1 | 0 | 0 | 1 | 0.0% |
| 17 | planner-template-bellows-execution-model-section-2026-04-30 | bellows | 2 | 1 | 0 | 0 | 1 | 0.0% |
| 18 | close-stranded-csv-upload-fetch-fix-2026-05-01 | invoice-pulse | 1 | 1 | 0 | 0 | 1 | 0.0% |
| 19 | deposit-exists-worktree-aware-2026-05-06 | bellows | 2 | 1 | 0 | 0 | 1 | 0.0% |
| 20–30 | (remaining 11 plans) | mixed | — | 0 | 0 | 0 | 0 | 100.0% (trivially — no instances) |

Plans 20–30 had zero decision-phrase instances in both stdout and OR. These are plans where the intermediate assistant narration contained only procedural task-execution text ("Let me read the plan", "Now commit") without any of the 33 grep patterns.

---

## Part 6 — Capture-Completeness Summary

| Metric | Value |
|---|---|
| Total stdout-detected instances (sample) | 37 |
| Total α (captured in OR) | 1 |
| Total β (leaked — in stdout only) | 36 |
| **Capture rate** | **2.7%** |

### Per-Project Capture Rates

| Project | Stdout instances | α | Capture rate |
|---|---|---|---|
| Bellows | 31 | 1 | 3.2% |
| Invoice-pulse | 6 | 0 | 0.0% |

### Assessment

**The mechanism is structurally lossy (<80%).** The capture rate of 2.7% indicates that the Output Receipt systematically omits intermediate decisions narrated during `claude -p` execution.

**Root cause (structural, not discipline):** Bellows invokes `claude -p --output-format stream-json`. The NDJSON stream captures ALL intermediate assistant text (decisions narrated between tool calls). However, the Output Receipt is solely the agent's final `result` text — a structured summary of outcomes. The agent's intermediate narration (course corrections, retries, problem diagnoses, scope decisions) exists in the NDJSON stream's `assistant` events but is not echoed into the final result text. The `runner.py` `_write_log()` function saves the full `raw_output` to the step.json file, so the data IS preserved on disk — but it is not part of the "Output Receipt" that the Planner inspects via `parsed.result_text`.

### Worst Three Plans by β Count

| Rank | Slug | β count | Stdout instances | Capture rate |
|---|---|---|---|---|
| 1 | deposit-exists-prose-canary-2026-04-28 | 5 | 5 | 0.0% |
| 2 | bellows-worktree-impl-2026-05-03 | 4 | 4 | 0.0% |
| 3 | terminal-capture-2026-05-12 | 4 | 4 | 0.0% |

### Best Three Plans by Capture Rate (with hits)

| Rank | Slug | α | Stdout instances | Capture rate |
|---|---|---|---|---|
| 1 | terminal-notification-backlog-close-2026-05-12 | 1 | 1 | 100.0% |

Only 1 plan in the sample had any α instances. The sole captured instance was a phrase that happened to appear in both the intermediate narration and the final result text. All other plans with decision-phrase hits had 0% capture rate.

---

## Part 7 — Representative β Instances

### β-A: Substantive — corrective action on evidence file (deposit-exists-prose-canary-2026-04-28, step 2)

**Stdout context (verbatim):**
> Both deposits verified — findings file exists with correct content (read above), dev log exists with Status: Complete. Now let me generate the evidence files.
> Let me verify the evidence files were created correctly.
> The grep evidence file seems empty. Let me fix that — the working directory might be wrong.
> Found the issue — the phrase uses capital letters. Let me write the evidence file properly.
> Good — evidence files are both populated. Now let me write the QA report.

**Corresponding Output Receipt section (verbatim):**
> **Step 2 complete.** Commit `326dca6`.
>
> Summary of what was done:
> - Verified Step 1's Output Receipt status = Complete
> - Confirmed both Step 1 deposits exist with correct content
> - Generated evidence files [...]

**Assessment:** The agent discovered an empty evidence file, diagnosed the root cause (case-sensitive grep pattern), and regenerated it. This three-step corrective sequence (detect → diagnose → fix) is absent from the Output Receipt. The receipt says "Generated evidence files" — implying a clean generation, not the fix-and-retry that actually occurred. **This is a substantive leak**: the Planner cannot see that the agent encountered and self-corrected an issue during execution.

### β-B: Substantive — architectural fix with course correction (bellows-worktree-impl-2026-05-03, step 2)

**Stdout context (verbatim):**
> Wait, I need to fix the project path derivation in the prune hook. The watched_projects entries are `knowledge/decisions/` paths — need to go up 2 levels to get the project root.

**Corresponding Output Receipt section:**
The result text for this step summarizes delivered code changes and test results. No mention of the project-path derivation fix or the `Wait,` correction moment.

**Assessment:** The agent caught a logical error in path derivation during implementation and corrected it. The Output Receipt reports the final correct state without noting the mid-course correction. **Substantive leak**: the decision to change path derivation logic is invisible to the Planner.

### β-C: Borderline — scope expansion for test research (phase-3c-plan-hash-drift-warning-2026-04-30, step 2)

**Stdout context (verbatim):**
> Let me also look at one of the existing run_plan tests to see the full pattern for mocking and setup, particularly `test_run_plan_resume_prompt_uses_shadow_path` since it involves resume and shadow.
> Let me also check for `_shadow_path` and `_create_test_db` helper, and look at the `import sqlite3` in tests.
> Now I have everything I need. Let me also check the end of the test file to see where to add the new test.

**Corresponding Output Receipt section:**
> Step 1 complete. Summary:
> - **`bellows.py`**: Added `import hashlib` [...] and a 5-line plan-hash drift warning block [...]
> - **`tests/test_bellows.py`**: Added `test_plan_hash_drift_warning` [...]

**Assessment:** Three "let me also" instances represent the agent's self-directed research scope — choosing which existing tests to study and where to insert the new test. The Output Receipt reports the outcome (test added) without the research decisions. **Borderline**: these are reasonable implementation choices that don't change the deliverable, but they reveal how the agent decided on the test structure.

### β-D: Trivial — procedural retry (remove-phase-3b-3c-2026-05-01, step 2)

**Stdout context (verbatim):**
> Check 7 exit code 1 is expected (known `test_run_step_timeout` failure). Let me verify the evidence files and re-run Check 8.

**Corresponding Output Receipt section:**
> **Step 2 complete.** Summary:
> - **8/8 verification checks passed** [...]
> - **Rule 20 self-check: PASSED** [...]

**Assessment:** The "re-run Check 8" is a procedural retry during QA verification — the agent needed another pass to complete verification. The Output Receipt correctly summarizes the final QA state. **Trivial leak**: the retry doesn't affect the outcome and the receipt correctly omits it.

### β-E: Trivial — procedural intent narration (canary-phase-3b-restart-2026-04-30, step 2)

**Stdout context (verbatim):**
> Self-check PASSED. Now I'll update PROJECT_STATUS.md and append feedback.
> Now I need to find the insertion point and also verify the Step 1 deliverables exist on disk. Let me do all remaining tasks.

**Corresponding Output Receipt section:**
> Step 2 complete. Committed as `a405ba2`.
> **Summary of QA results:** [table of assertions with ✅ results]

**Assessment:** "Now I'll update" is intent narration — the agent stating what it will do next. The Output Receipt covers what was done, not what was planned. **Trivial leak**: the receipt correctly summarizes the outcome, and the procedural intent statement adds no decision information.

---

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/output-receipt-capture-audit-2026-05-12/
Files verified: 3
```

---

## Output Receipt

**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Empirical audit of Output Receipt capture completeness across 82 DEV plans (30-plan stratified sample) from the 2026-04-28 → 2026-05-12 window. Extended the starting 20-phrase grep list to 33 phrases based on pattern analysis. Found a 2.7% capture rate — the mechanism is structurally lossy because the Output Receipt contains only the agent's final summary, not the intermediate decision narration preserved in the NDJSON stream.

### Files Deposited
- `bellows/knowledge/research/output-receipt-capture-audit-2026-05-12.md` — full audit findings with per-plan tables and representative β instances
- `bellows/knowledge/qa/evidence/output-receipt-capture-audit-2026-05-12/worst-plan-stdout-vs-or.md` — full grep transcript for worst-leak plan
- `bellows/knowledge/qa/evidence/output-receipt-capture-audit-2026-05-12/beta-instance-stdout-context.txt` — raw stdout context for β-A
- `bellows/knowledge/qa/evidence/output-receipt-capture-audit-2026-05-12/beta-instance-or-section.txt` — Output Receipt section for β-A

### Decisions Made
- Extended grep list from 20 to 33 phrases based on empirical pattern analysis (specialist authority: investigation methodology)
- Separated intermediate assistant text from the final result text by excluding the last assistant message that duplicates the result event (specialist authority: measurement methodology)

### Flags for CEO
- None

### Flags for Next Step
- None
