# Disable Auto-Close Blueprint
**Date:** 2026-04-24 | **Agent:** Bellows Systems Analyst | **Plan:** executable-disable-auto-close-2026-04-24

---

## Section 1 — Bellows Code Change

### Current Behavior (bellows.py L272, commit 5eea941)

```python
effective_auto_close = header.get("auto_close", "true" if not is_diagnostic else "false").lower() == "true"
```

The default is bifurcated: executables default to `auto_close=True`, diagnostics default to `auto_close=False`. When `effective_auto_close` is True and all terminal-step gates pass, Bellows executes the auto-close branch (L363-381): log to ledger, move plan to `Done/`, delete shadow, notify via Pushover.

When `effective_auto_close` is False and gates pass at the terminal step, Bellows takes the pause branch (L332-358): post verdict request with `pause_reason="auto_close_disabled"`, rename plan to `verdict-pending-*`, notify, return.

### Proposed Change: Plan-Header Default Inversion

**Type:** Plan-header default change (not config inversion, not code removal).

**Justification:** A config knob (`auto_close_default: false` in config.json) adds indirection without value — the CEO's architectural decision is clear and permanent: Bellows should not decide that a plan succeeded. A code-removal approach would eliminate the auto-close branch entirely, but the branch remains useful for future opt-in cases (e.g., trivial housekeeping plans the CEO pre-approves). The plan-header default change is the minimal intervention: one line of code, preserving the opt-in escape hatch.

### Before (L272)

```python
effective_auto_close = header.get("auto_close", "true" if not is_diagnostic else "false").lower() == "true"
```

### After (L272)

```python
effective_auto_close = header.get("auto_close", "false").lower() == "true"
```

### Pseudocode — Before vs. After

**Before (executable plan, no header override, terminal step, gates pass):**
```
1. gates pass
2. effective_auto_close = True  (executable default)
3. → auto-close branch fires
4. → plan moves to Done/
5. → shadow deleted
6. → Pushover: "Plan Complete, Auto-closed"
```

**After (same scenario):**
```
1. gates pass
2. effective_auto_close = False  (new default)
3. → pause branch fires (L332-358)
4. → verdict request posted with pause_reason="auto_close_disabled"
5. → plan renamed to verdict-pending-*
6. → Pushover: verdict request notification
7. → Planner reads verdict, applies Rule 22, performs Done/ move
```

**After (explicit `auto_close: true` in plan header):**
```
1. gates pass
2. effective_auto_close = True  (explicit header override)
3. → auto-close branch fires (L363-381 unchanged)
4. → plan moves to Done/
```

### Files Modified

| File | Line(s) | Change |
|---|---|---|
| `bellows.py` | 272 | Default value: `"true" if not is_diagnostic else "false"` → `"false"` |

### What Does NOT Change

- The auto-close branch (L363-381) stays intact — it fires when `auto_close: true` is explicitly set in a plan header.
- The pause branch (L332-358) is unchanged — it already handles the `auto_close_disabled` pause reason correctly.
- The `_consume_verdicts` method is unchanged — it already handles `continue-to-done` for terminal-step verdicts.
- The mid-loop pause conditions (L274-300) are unchanged — mid-plan steps are unaffected by auto-close (auto-close only applies to terminal steps).

---

## Section 2 — Governance Edits (PLANNER_TEMPLATE.md)

### Edit 2.1 — Rule 8, Final-Step Ordering (L447)

**Old text:**
```
The last step in every executable plan (always the QA step) must do four things in order: (1) **deliverable verification** (Rule 17), (2) deposit the QA report, (3) update `PROJECT_STATUS.md` with a summary of all changes made across the plan, (4) move the plan file to Done. The QA agent has the full picture of what was implemented — it is the right agent to write the status update. The ordering within the final step's prompt must be: **deliverable verification → QA deposit → PROJECT_STATUS.md update → feedback append → final commit → move plan to Done.** If any deliverable verification item is ❌ MISSING, the plan does NOT move to Done — the agent attempts to fix the missing items or flags as blocked.
```

**New text:**
```
The last step in every executable plan (always the QA step) must do three things in order: (1) **deliverable verification** (Rule 17), (2) deposit the QA report, (3) update `PROJECT_STATUS.md` with a summary of all changes made across the plan. The QA agent has the full picture of what was implemented — it is the right agent to write the status update. The ordering within the final step's prompt must be: **deliverable verification → QA deposit → PROJECT_STATUS.md update → feedback append → final commit.** The agent does NOT move the plan to Done — the Planner performs that move after Rule 22 verification passes. If any deliverable verification item is ❌ MISSING, the plan does NOT close — the agent attempts to fix the missing items or flags as blocked.
```

### Edit 2.2 — Rule 8, PROJECT_STATUS.md Update Instruction (L451)

**Old text:**
```
**PROJECT_STATUS.md update instruction (include in final QA step):** `**Final:** Update PROJECT_STATUS.md — add a completed milestone entry summarizing all changes from this plan (features added, files changed, tests added). Then move this plan to Done: mv [project]/knowledge/decisions/executable-[name].md [project]/knowledge/decisions/Done/. Commit: "chore: status update + move [name] plan to Done".`
```

**New text:**
```
**PROJECT_STATUS.md update instruction (include in final QA step):** `**Final:** Update PROJECT_STATUS.md — add a completed milestone entry summarizing all changes from this plan (features added, files changed, tests added). Commit with descriptive message. **STOP.** Do NOT move this plan to Done/. Per the disable-auto-close model, the Planner performs the terminal move after Rule 22 verification passes.`
```

### Edit 2.3 — Rule 8, Housekeeping Ordering Paragraph (L453)

**Old text:**
```
**Per Rule 23 (housekeeping discipline), the order is feedback append → final commit → move-to-Done — move-to-Done is always the absolute last operation.** The move-to-Done is the structural completion gate Bellows uses to mark the plan complete. If feedback append fails, the plan correctly strands BEFORE the move and the failure is visible. If commit fails, same thing. Putting move-to-Done last preserves both Bellows' strand-detection guarantee AND the recoverability of upstream failures. (Note: the previous version of Rule 8 specified the opposite ordering on the assumption that agent context exhaustion was the primary risk; Phase 4 of the Bellows reliability fixes (parser stop_reason inference + planner consultation logging) made agent termination visible, shifting the primary risk to operation failures during housekeeping — which Rule 23's ordering handles correctly.)
```

**New text:**
```
**Per Rule 23 (housekeeping discipline), the order is feedback append → final commit.** The final commit is the absolute last agent operation. The Planner performs the move-to-Done after Rule 22 verification passes — this is a Planner responsibility, not an agent responsibility. If feedback append fails, the plan correctly strands and the failure is visible. If commit fails, same thing. Separating the agent's final commit from the Planner's move-to-Done eliminates the Failure 3 ordering issue where agents moved plans to Done/ before Bellows evaluated gates, producing stranded verdict requests for already-shipped work.
```

### Edit 2.4 — Rule 8, Diagnostic Plans Paragraph, Final Sentence (L455)

**Old text:**
```
Rule 8 (this rule) continues to govern executable plans only: the final QA step in every executable does deliverable verification → QA deposit → PROJECT_STATUS.md update → feedback append → final commit → move plan to Done, in that order (per Rule 23), with the Planner verification gate from Rule 22 applied via the Planner reading the QA report after Step 2 completes.
```

**New text:**
```
Rule 8 (this rule) continues to govern executable plans only: the final QA step in every executable does deliverable verification → QA deposit → PROJECT_STATUS.md update → feedback append → final commit, in that order (per Rule 23). The agent does NOT move the plan to Done. The Planner performs the terminal move after Rule 22 verification passes — the same pattern diagnostic plans already follow.
```

### Edit 2.5 — Rule 23, Title (L647)

**Old text:**
```
### 23. End-of-plan housekeeping must use anchored edits, enumerated sub-steps, and the order: feedback → commit → move-to-Done
```

**New text:**
```
### 23. End-of-plan housekeeping must use anchored edits, enumerated sub-steps, and the order: feedback → commit
```

### Edit 2.6 — Rule 23, Paragraph (c) (L655)

**Old text:**
```
**(c) Ordering: feedback → commit → move-to-Done.** The move-to-Done is always the absolute last operation. It is the structural completion gate Bellows uses to mark the plan complete. If feedback append fails, the plan correctly strands BEFORE the move and the failure is visible. If commit fails, same thing. Any other ordering creates a window where Bellows marks the plan complete but housekeeping is incomplete.
```

**New text:**
```
**(c) Ordering: feedback → commit.** The final commit is the absolute last agent operation. The Planner performs the move-to-Done after Rule 22 verification passes — this is a Planner responsibility, not an agent responsibility. If feedback append fails, the plan correctly strands and the failure is visible. If commit fails, same thing. The agent never moves the plan to Done; the Planner does, via `Filesystem:move_file`, after verifying the deposited files pass Rule 22's (a)–(e) checks.
```

### Edit 2.7 — Rule 25, New Paragraph After L703 (Terminal-Step Resolution)

**Insert after** the paragraph ending "...this resolution path falls away." (L703), **before** the "Gate-failure guard" paragraph (L705):

**New text to insert:**
```

**Terminal-step resolution and Planner-owned Done/ move:** When a verdict request has `auto_close_disabled` as its Pause Reason Code AND the step is the terminal step (step number equals total steps as declared in the verdict request's `**Total Steps:**` field), a clean Rule 22 pass authorizes the Planner to perform the terminal move. The resolution sequence is:

1. Perform Rule 22 (a)–(e) verification on all deposits declared in the plan's `**Deposits:**` block for that step.
2. If Rule 22 passes: move the plan file from `[project]/knowledge/decisions/verdict-pending-[slug].md` (or `in-progress-[slug].md`) to `[project]/knowledge/decisions/Done/[slug].md` via `Filesystem:move_file`, stripping the lifecycle prefix (`in-progress-`, `verdict-pending-`). Tool call pattern: `Filesystem:move_file(source: "[project]/knowledge/decisions/verdict-pending-executable-[name].md", destination: "[project]/knowledge/decisions/Done/executable-[name].md")`.
3. Resolve the Bellows verdict by depositing a verdict file to `bellows/verdicts/resolved/verdict-[slug]-step-[N].md` with content `continue\nRule 22 passed — Planner-authorized terminal close.`
4. Report the resolution to the CEO.

This stays within the Planner's declared filesystem access scope: file renames within `[project]/knowledge/decisions/` are explicitly allowed (see "What the Planner CAN write" — "File renames within `[project]/knowledge/decisions/`"). The `Done/` subdirectory is inside `knowledge/decisions/`.

**Non-terminal steps with `auto_close_disabled`:** For mid-plan steps (step < total steps), the existing Rule 25 routing applies unchanged: auto-proceed to Rule 22 verification, report result to CEO, CEO resolves the verdict. The Planner does NOT perform a Done/ move for non-terminal steps.

```

### Filesystem Access Scope Confirmation

The Planner's "What the Planner CAN write" section (PLANNER_TEMPLATE.md L112-116) explicitly lists:
- `[project]/knowledge/decisions/` — depositing plans
- File renames within `[project]/knowledge/decisions/` (e.g., stripping `in-progress-` prefix)

Moving a file from `knowledge/decisions/verdict-pending-[slug].md` to `knowledge/decisions/Done/[slug].md` is a file rename within `knowledge/decisions/`. This is within declared scope. No access expansion required.

---

## Section 3 — Verdict-Log Schema

**File:** `bellows/knowledge/verdict-log.md`

**Purpose:** Planner appends to this log on every verdict resolution — observation surface for future auto-approval patterns. Phase 2 work (auto-approval logic) will analyze this log to identify which pause-reason/gate combinations are safe to auto-approve. This file is the data collection layer; no automation reads it yet.

**Schema:**

```markdown
# Verdict Resolution Log

Planner appends to this log on every verdict resolution — observation surface for future auto-approval patterns.

| Plan Slug | Step | Pause Reason | Gates Passed | Gates Failed | Rule 22 Result | Planner Decision | Timestamp |
|---|---|---|---|---|---|---|---|
```

**Field definitions:**

| Field | Type | Description |
|---|---|---|
| Plan Slug | string | Plan slug without lifecycle prefix (e.g., `executable-disable-auto-close-2026-04-24`) |
| Step | string | `N/M` format (e.g., `3/4` = step 3 of 4) |
| Pause Reason | enum | One of: `auto_close_disabled`, `qa_checkpoint`, `gate_failure`, `scope_violation`, `agent_verdict_request`, `header_pause` |
| Gates Passed | string | Comma-separated list of gates that passed, or `all` |
| Gates Failed | string | Comma-separated list of gates that failed, or `none` |
| Rule 22 Result | string | `pass`, `fail:(a)`, `fail:(b)`, etc., or `skipped` (for gate_failure/scope_violation routes) |
| Planner Decision | string | `clean close`, `escalated to CEO`, `reverted`, or free-text |
| Timestamp | ISO 8601 | When the Planner resolved the verdict |

**Append convention:** The Planner adds one row per verdict resolution. Rows are append-only; no editing or deletion. The file is not machine-parsed by Bellows — it is a Planner-side observation log read by the Planner (and CEO) during future Phase 2 analysis.

---

## Section 4 — Test Impact Enumeration

### Existing Tests — Impact Assessment

| Test | Current Behavior | After Change | Action |
|---|---|---|---|
| `test_diagnostic_auto_close_moves_to_done` (L113) | Uses explicit `plan_header: {"auto_close": "true"}` → auto-closes | Header explicitly sets `auto_close: "true"` → default not consulted → still auto-closes | **No change needed** |
| `test_clean_diagnostic_no_header_posts_verdict` (L166) | Empty header → diagnostic default `"false"` → pauses | Empty header → new universal default `"false"` → pauses | **No change needed** |
| `test_clean_diagnostic_auto_close_true_moves_to_done` (L234) | Explicit `auto_close: "true"` → auto-closes | Same | **No change needed** |
| `test_verdict_continue_at_final_step_moves_to_done` (L303) | Tests `_consume_verdicts` continue path → Done | Unchanged | **No change needed** |
| `test_run_plan_claims_file_before_runner_runs` (L988) | Uses `_clean_gates(auto_close="true")` → auto-closes | Explicit header → auto-closes | **No change needed** |
| `test_run_plan_continuation_prompt_uses_shadow_path` (L1101) | Uses `_clean_gates()` → auto-close="true" explicit → auto-closes | Same | **No change needed** |
| All other tests using `_clean_gates()` | Explicit `auto_close: "true"` in gate result → default not consulted | Same | **No change needed** |

### New Tests Required

| # | Test Name | What It Verifies |
|---|---|---|
| 1 | `test_executable_no_header_defaults_to_verdict` | Executable plan with empty `plan_header: {}` (no `auto_close` key) should pause for verdict at terminal step, NOT auto-close to Done. This is the key behavioral change — validates the default inversion. |
| 2 | `test_executable_explicit_auto_close_true_still_closes` | Executable plan with explicit `plan_header: {"auto_close": "true"}` should still auto-close to Done. Regression guard for the opt-in escape hatch. |

### Net Test Delta

- **+2 new tests**
- **0 existing tests modified**
- **0 existing tests removed**

---

## Section 5 — Rollback Plan

If the disable-auto-close model produces unacceptable Planner friction (too many verdict requests requiring manual resolution), the reversal is a single commit touching three files:

1. **`bellows.py` L272:** Revert default from `"false"` back to `"true" if not is_diagnostic else "false"`. One-line change.
2. **`PLANNER_TEMPLATE.md`:** Revert Rules 8, 23, and 25 to their pre-edit text (edits 2.1–2.7 in Section 2 above). The Rule 25 terminal-step-resolution paragraph is removed; the routing table reverts to its current form.
3. **`tests/test_bellows.py`:** Remove the two new tests (`test_executable_no_header_defaults_to_verdict`, `test_executable_explicit_auto_close_true_still_closes`).

**Data preservation:** `bellows/knowledge/verdict-log.md` entries accumulated during the auto-close-disabled window are historical records with no coupling to the auto-close default. They can be preserved for future Phase 2 analysis regardless of whether the default is reverted. The file itself can remain in place (harmless) or be archived.

---

## Layer Impact

| Change | Layer 1 (Bellows) | Layer 2 (Agents) | Layer 3 (Planner) |
|---|---|---|---|
| Default inversion (bellows.py L272) | **Modified** — all plans without explicit header now pause at terminal step | Not affected — agents don't read the auto-close flag | **Affected** — receives more verdict requests; must perform Done/ move on clean pass |
| Rule 8 edit (remove move-to-Done from agent ordering) | Not affected | **Modified** — agents no longer perform move-to-Done as housekeeping | Not affected (Planner already does this for diagnostics) |
| Rule 23 edit (ordering drops move-to-Done) | Not affected | **Modified** — agent's last operation is now final commit, not move-to-Done | Not affected |
| Rule 25 extension (terminal-step resolution) | Not affected | Not affected | **Modified** — Planner gains explicit terminal-step Done/ move responsibility |
| verdict-log.md | Not affected | Not affected | **Modified** — Planner appends to log on every verdict resolution |

**Net layer-responsibility shift:** Move-to-Done for executable plans shifts from Layer 2 (agent housekeeping) to Layer 3 (Planner post-verification). This aligns executables with the pattern diagnostics already follow (Planner performs Done/ move after Rule 22 pass). Layer 1 (Bellows) gains no new responsibilities — it continues to dispatch and gate. The shift eliminates the Failure 3 structural gap where agents moved plans to Done/ before Bellows evaluated gates.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Produced a four-part blueprint for disabling auto-close: (1) Bellows code change — single-line default inversion at L272 from bifurcated executable/diagnostic defaults to universal `"false"`, preserving opt-in via explicit header; (2) governance edits — 7 anchored edits to PLANNER_TEMPLATE.md Rules 8, 23, and 25 removing agent-owned move-to-Done and adding Planner-owned terminal-step resolution; (3) verdict-log.md schema for pause-telemetry observation surface; (4) test impact — 0 existing tests affected, +2 new tests for default inversion and opt-in regression guard.

### Files Deposited
- `knowledge/architecture/disable-auto-close-blueprint-2026-04-24.md` — full blueprint for disable-auto-close implementation

### Files Created or Modified (Code)
- None (blueprint only)

### Decisions Made
- **Plan-header default change** over config inversion or code removal — minimal intervention, preserves opt-in escape hatch, no config.json coupling
- **No new pause_reason code** — the existing `auto_close_disabled` code already covers the terminal-step pause case; adding a new code (e.g., `terminal_step_pause`) would require taxonomy changes with no behavioral benefit since Rule 25 already routes `auto_close_disabled` to auto-proceed
- **verdict-log.md as Planner-side append-only log** rather than a Bellows-side structured file — keeps observation data in the Planner's domain (Layer 3) where the analysis will happen

### Flags for CEO
- None

### Flags for Next Step
- The Developer (Step 2) should verify that L272 is still the correct line number before editing — the one-line change is simple but line numbers may have shifted if any concurrent work landed between blueprint and implementation
- The `_clean_gates()` test helper defaults to `auto_close="true"` — existing tests that use this helper are testing explicit-header behavior and will not be affected by the default change, but the Developer should confirm this by tracing through the test setup
- The Documentation Analyst (Step 3) should use the exact old-text blocks from Section 2 as `old_string` anchors for `edit_block` — these were extracted verbatim from the current PLANNER_TEMPLATE.md (v4.26, last updated 2026-04-20)
