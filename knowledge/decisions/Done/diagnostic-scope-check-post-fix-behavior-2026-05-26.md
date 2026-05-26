# Diagnostic — Post-Fix Scope_Check Behavior Characterization (2026-05-26)
**Project:** bellows
**Date:** 2026-05-26
**Author:** Planner
**Dispatch Mode:** bellows
**Total Steps:** 1
**pause_for_verdict:** after_step_1
**auto_close:** false
**qa_steps:** none

---

## CEO Context

On 2026-05-25 the `executable-file-change-audit-fix` plan (DEV commit `950436c`) rewrote `_capture_git_diff` to use HEAD SHA + commit-range diff. The prior implementation used `git diff --stat` (working-tree-vs-index), blind to committed changes. The LESSONS entry captured the cascading effect: `_gate_scope_check` short-circuits when `files_changed` is empty (`if not files_changed: return`), so the broken capture meant scope_check was **silently bypassed on every Bellows-dispatched code-edit step** over the entire bug window. The fix landed; the daemon was restarted; today is the first post-restart session with material plans dispatched through it.

This afternoon's `executable-planner-template-rule-21-contract-change-2026-05-26` plan tripped `scope_check` at Step 1 (DOC) with the gate flagging `...-template-rule-21-contract-change-2026-05-26.md` (the plan file's own claim rename) as out-of-scope. Files Changed list: the plan file rename + `agent-prompt-feedback.md` append. The PLANNER_TEMPLATE.md edit itself (in the governance root, outside the worktree) did not appear in the audit — it was committed via the Rule 8 split-commit pattern to a different repo.

**The framing question is not "did the fix regress scope_check" — scope_check has effectively been off for weeks; today is the first time it actually ran against a real plan.** The framing question is: what does scope_check now flag, and is its current scope-definition logic the right one given the fix.

**Hypothesis under test:** the plan-file rename (`shutil.move` from `executable-*` to `in-progress-*`) is a routine lifecycle operation that should NOT be flagged as a scope violation. But the post-fix `_gate_scope_check` is now seeing it because it sees committed worktree-state changes for the first time. The diagnostic should determine: (a) how often this triggers, (b) what scope_check considers in-scope under its current code, (c) whether the plan-file rename has a clean structural exemption path, and (d) whether other lifecycle artifacts (verdict response files, processed-verdict renames) would also trip if they happened during a step.

This is a diagnostic, not a fix. No source code changes; characterization only.

---

## STEP 1 (SA) — Scope_Check Post-Fix Behavior Audit

Read your specialist file at `agents/BELLOWS_SYSTEMS_ANALYST.md` first. Skip glossary read — this is a gate-behavior characterization task with no domain terminology surface. Note: worktree root IS the bellows project root — strip the `bellows/` prefix from any path references in this prompt.

### Investigation questions

**Q1 — `_gate_scope_check` current code shape.** Read `gates.py` and produce the function's current code in the findings file (paste verbatim, with line numbers). Specifically capture: (a) how it determines what's in-scope, (b) what data it consumes (plan_text, files_changed, anything else), (c) what exemptions exist (if any). Reference the 2026-05-25 file-change-audit-fix change for context — quote the relevant lines of `_capture_git_diff` and `_parse_diff_stat` post-fix to establish what `files_changed` now contains.

**Q2 — Post-restart dispatch population.** Enumerate every plan dispatched since the daemon restart this morning (2026-05-26). Three are now closed in `Done/` or `Done/halted-*/`:

- `diagnostic-parallel-sha-population-audit-2026-05-26.md`
- `executable-planner-template-rule-21-contract-change-2026-05-26.md` (halted at Step 1 scope_check)

For each plan, capture from the corresponding `processed-verdict-*` files in `verdicts/resolved/`:
- The `scope_check` row from the Verification Results table
- The Files Changed list
- The Gate Failures section (if any)

If only 1 plan tripped scope_check (the Rule 21 plan), the audit window is too narrow to characterize population behavior — note this and recommend a future-rerun trigger. If multiple plans tripped, enumerate the trip patterns.

**Q3 — What does scope_check consider in-scope?** Trace the code path: `gate_result["failures"]` populates with a scope_check failure when files_changed contains a path that fails the in-scope predicate. What IS the predicate? Specifically:

- Does scope_check read the plan's `**Deposits:**` block to determine in-scope paths?
- Does it use the plan's `## STEP N` prose to extract path references?
- Does it have a hardcoded list of always-exempt patterns (knowledge/, verdicts/, etc.)?
- Does it cross-reference against `Files Created or Modified` in agent output receipts?

Cite the specific code lines that define "in-scope" and quote them in the findings.

**Q4 — Plan-file rename: structurally exempt or not?** The agent's first action on claim is `shutil.move(executable-X.md, in-progress-X.md)`. This is a Bellows protocol-mandated operation, listed verbatim in PLANNER_TEMPLATE Rule 6 plan structure boilerplate. Is the plan-file path supposed to be in scope_check's exemption list? Search `gates.py` for any logic that recognizes `in-progress-`, `verdict-pending-`, or `executable-` prefixes as lifecycle paths. If no such exemption exists, that's a structural gap: every Bellows-dispatched plan executes a rename that scope_check now catches.

**Q5 — Other lifecycle artifacts at risk.** Besides plan-file renames, what other Bellows lifecycle operations could trigger committed changes during a step? Enumerate:

- Verdict response files (Planner-owned, post-step, shouldn't appear during agent dispatch)
- Processed-verdict renames (Bellows-owned, post-consumption, shouldn't appear during agent dispatch)
- Shadow cache writes (Bellows-owned, post-claim, in `.bellows-cache/`)
- Worktree-internal artifacts (the agent's commits in the worktree branch)

For each, declare whether it could appear in `files_changed` during a step. The goal: enumerate the complete population of lifecycle artifacts that the post-fix scope_check might flag, so any fix can address all of them rather than just the plan-file rename.

**Q6 — Fix-shape options.** Based on Q1–Q5, propose 2–4 candidate fix shapes for the plan-file rename specifically. Examples (not prescriptive — the SA should propose what fits the actual code):

- (a) Add `in-progress-*`, `verdict-pending-*`, `executable-*`, `diagnostic-*`, `halted-*` filename prefix patterns to a scope_check exemption set (similar to `READ_CLASS_TOOLS` exemption for permission gates)
- (b) Exempt the entire `knowledge/decisions/` directory from scope_check (lifecycle directory; agent work happens elsewhere)
- (c) Read the plan-file's slug at claim time and exempt that filename specifically
- (d) Require plans to declare their own filename in `**Deposits:**` (governance change, not code change — but Rule 26 explicitly says don't list plan file as a deposit, so this would conflict)

For each candidate, provide a code-sketch (5–15 lines), a LOC estimate, a blast-radius assessment (other gates affected? other tests affected?), and a one-sentence trade-off summary.

**Q7 — Disposition recommendation.** Pick one of three:
- **STRUCTURAL-FIX-NEEDED:** the plan-file rename is genuinely supposed to be exempt; recommend a specific fix shape from Q6 with rationale. Specify the executable plan shape (SA-derived or DEV-direct? scope tier?).
- **DESIGN-INTENT-AUDIT-NEEDED:** unclear whether the plan-file rename should be exempt or whether the rename should not be committed at all; recommend a follow-up SA diagnostic to characterize the design intent before authoring a fix.
- **NO-FIX-NEEDED:** the trip is structurally correct (e.g., plans really should declare lifecycle ops, or some other framing makes it intended behavior); recommend a governance edit to document the override workflow as the standard recovery path.

### Verification Blocks (Rule 39)

Capture verification blocks for the load-bearing claims:

- **Block 1:** The post-fix `_capture_git_diff` return shape. Command: `grep -A 15 "def _capture_git_diff" gates.py`. Expected: function returns HEAD SHA + commit-range diff output. Actual: paste full function body. Materiality: the entire diagnostic rests on understanding what `files_changed` now contains.

- **Block 2:** `_gate_scope_check` in-scope predicate. Command: `grep -B 2 -A 30 "def _gate_scope_check" gates.py`. Expected: function with in-scope predicate. Actual: paste full function body, identify the predicate line(s). Materiality: Q3's answer depends on this.

- **Block 3:** Post-restart scope_check trip count. Command: list every `processed-verdict-*-2026-05-26-step-*.md` file in `verdicts/resolved/` AND any `halted-*-2026-05-26-*.md` files in `knowledge/decisions/Done/`, grep each for `scope_check`. Expected: trip count = N (where N is whatever the audit finds). Actual: report N with per-plan breakdown.

### Deposits

- `knowledge/research/scope-check-post-fix-behavior-2026-05-26.md` — findings file with the seven question answers, code citations, fix-shape proposals, and three verification blocks

### Output Receipt Format

End the deposit with the standard Output Receipt. Status: Complete. Files Deposited: the single findings file. Flags for CEO: the disposition recommendation (STRUCTURAL-FIX-NEEDED / DESIGN-INTENT-AUDIT-NEEDED / NO-FIX-NEEDED) with one-line reasoning. Flag any side-findings — e.g., if Q3 reveals that scope_check's in-scope predicate has other surprising behavior beyond the plan-file rename, that's worth surfacing as a separate observation.

### Boundary constraints

- **Do NOT modify any source code.** This is a characterization audit; fix authoring is a separate plan.
- **Do NOT run `git push`** during the audit.
- **Do NOT attempt to reproduce the trip by dispatching a test plan.** If a test plan is needed to characterize behavior, recommend it as a follow-up in Q7 rather than authoring it inline.
- **Source reads ARE in scope here.** This is an SA diagnostic — the agent is permitted to read `gates.py`, `bellows.py`, and other Bellows source to answer the questions. Rule 27 prohibits Planner source reads, not agent source reads during a diagnostic.

