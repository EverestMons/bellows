# Bellows — Next Session Baton

**Last session:** 2026-05-26
**Last session focus:** Bellows hardening — parallel-SHA audit closeout + Rule 21 governance edit (halted on scope_check) + scope_check post-fix behavior diagnostic

---

## Session summary

Three plans dispatched. Two closed cleanly to `Done/`; one halted at Step 1 scope_check but its substantive Edit A/B/C all landed at the governance root, so the governance change shipped despite the halt.

| # | Plan | Outcome |
|---|---|---|
| 1 | `diagnostic-parallel-sha-population-audit-2026-05-26` | Population audit n=34 plans post-v4.47, **0 parallel-SHA reproductions**. Disposition: CLOSE-SUPERSEDED. v4.47 closed the root cause. No follow-up needed. |
| 2 | `executable-planner-template-rule-21-contract-change-2026-05-26` | **HALTED at Step 1 scope_check.** Edits all landed: PLANNER_TEMPLATE v4.50 → v4.51 with Rule 21 contract-change carve-out (function appears in >1 test file → MUST be `full-suite`). Step 2 QA never ran. Plan sits in `decisions/` as `halted-*`. |
| 3 | `diagnostic-scope-check-post-fix-behavior-2026-05-26` | Reframed CEO context. Plan-file rename does NOT trip scope_check (architecturally impossible). The Rule 21 trip was the **dev log deposit** failing the text-mention predicate. Disposition: DESIGN-INTENT-AUDIT-NEEDED. |

**Daemon restart this session at session start (CEO confirmed).** All three plans ran against the post-fix `_capture_git_diff` + `_parse_diff_stat` code. The Rule 21 halt was the first time scope_check actually evaluated against a real plan post-fix — scope_check had been silently bypassed for weeks pre-fix because `files_changed` was always empty.

---

## In-flight threads (carry forward)

### 1. Rule 21 plan post-halt cleanup (PRIORITY)

The Rule 21 governance edits shipped to PLANNER_TEMPLATE v4.51 (commit `bc0f51e` at governance root) but the plan halted at Step 1 before Step 2 QA ran. No structural QA verification exists for the edits. Options:

- (a) Author a thin executable-rule-21-qa-cleanup plan that runs only Step 2 verification against the now-committed edits.
- (b) Manually verify the edits via direct file reads (low overhead, no plan needed).
- (c) Leave it — the governance edits are content-verifiable in the file itself, and the plan can be archived as `halted-*` indefinitely.

Recommend (b) at start of next session: read PLANNER_TEMPLATE.md sections around Rule 21, the Lessons row table, and the version line; confirm the three edits landed correctly. Move the halted plan to `Done/halted-*-2026-05-26.md` once verified.

### 2. Pristine-plan-text follow-up diagnostic (the scope_check design-intent audit)

The scope_check diagnostic ended with DESIGN-INTENT-AUDIT-NEEDED. To resolve, a follow-up SA diagnostic should:
- Read the pristine Rule 21 plan step text from the main repo's `.bellows-cache/` (the worktree didn't have access)
- Determine whether the dev log path was mentioned in the step text in a form the text-mention predicate didn't match (path-form gap) or whether the predicate has a structural failure mode
- Then select one of Fix Shape B (parse `**Deposits:**` block structurally) or Fix Shape D (governance rule requiring deposit paths be mentioned in step prose)

This diagnostic is scoped — single SA step, no DEV/QA chain. Can be the first plan of next session if Rule 21 cleanup goes the (b) route.

### 3. `knowledge/development/` deposits = systemic scope_check risk (side-finding from diagnostic 3)

The SA's side-finding 3: every Rule 8 split-commit DOC step creates a `knowledge/development/*.md` deposit. If the Planner doesn't mention the deposit path in step text, scope_check trips. The Rule 21 plan tripped this on its first run. Without a structural fix, every DOC step from now on will trip scope_check unless the Planner is meticulous about including the dev log path in step prose. Fix Shape B (parse Deposits block structurally) would close this systemically; Fix Shape D (governance rule) closes it via discipline. Decision waits on the in-flight thread 2 diagnostic.

---

## Open BACKLOG items at session end

No new BACKLOG additions this session. Two existing Open entries remain relevant:

1. **Teardown push silent failure (2026-05-24).** Push observability gap; unrelated to today's work but surfaced as adjacent during the parallel-SHA audit. Not in today's hardening scope.
2. **Cherry-pick conflicts on shared bookkeeping files (2026-05-22).** BACKLOG defers this until second occurrence demonstrates LESSONS-based discipline alone is insufficient. Not triggered today.

---

## On the horizon (next session)

In priority order:

1. **Rule 21 plan cleanup** — option (b) recommended; ~5 minutes
2. **Pristine-plan-text scope_check diagnostic** — single SA step; gets us to a fix decision on the `knowledge/development/` systemic risk
3. **Whichever fix shape is chosen** — small DEV plan if Fix Shape B, governance edit if Fix Shape D

---

## LESSONS entries from this session

One entry: 2026-05-26 — scope_check trip identified the WRONG file in CEO context (pattern-recognition + planner-discipline tag). Filename-slug-overloading made the Files Changed message ambiguous; I picked the most operationally salient interpretation without reading the literal Files Changed list. Mitigation: read literal entries before authoring follow-up plans on gate failures.

---

## CEO actions before next session

- **Restart daemon** if any further code lands in the bellows worktree between sessions. The current daemon has all post-fix code loaded.
- **Session-wrap git commits** for the bellows-side lifecycle artifacts (this commit) and the governance-root LESSONS entry (next commit). Both happen at session-wrap below.
