# Bellows — `file_change_audit` False-Negative Diagnostic

**Date:** 2026-05-25 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** none | **Execution:** Step 1 (SA) | **pause_for_verdict:** after_step_1

## Context

The `file_change_audit` gate (`gates.py:594` — `_gate_file_change_audit`) has been reporting `0 files modified` on real code-edit steps. Documented in BACKLOG `bellows/knowledge/BACKLOG.md` line 35 (added 2026-05-21). Reproduced 6+ times since: 2026-05-21 isinstance-asymmetry, 2026-05-22 multiple, 2026-05-24 multiple, and most recently 2x today during `executable-extract-plan-required-deposits-set-to-list-2026-05-25` (both Step 1 DEV and Step 2 QA verdict requests showed `file_change_audit | PASS | 0 files modified` despite the commits touching 3 files / 136 insertions and 4+ files respectively).

The BACKLOG entry framed this as "informational gate produces misleading signal." Closer inspection of `bellows.py` reveals `files_changed` is consumed by `_gate_scope_check` at `gates.py:600` — and `_gate_scope_check` short-circuits when `files_changed` is empty (line 601). That makes the false-negative a **silent failure of a blocking gate**, not just noisy display. `_gate_scope_check` is the gate that would catch an agent editing files outside plan scope; if it never runs on real code changes, scope-violation detection is effectively disabled.

The BACKLOG hypothesized two root causes: (1) timing race (post-teardown audit captures clean state), (2) wrong scope. Today's code read suggests a third candidate: **commits hide diff.** `_capture_git_diff` uses `git --no-pager diff --stat --relative -- .` (bellows.py:687-690), which by default shows ONLY uncommitted changes. Agents committing during a step (the standard pattern) leave a clean working tree at post-step capture time. Pre and post both empty → `_parse_diff_stat` returns `[]` → `files_changed` empty → scope_check no-ops → audit prints "0 files modified."

This diagnostic verifies which (if any) of the candidate root causes is correct. It does NOT propose a fix.

**Sources:**
- BACKLOG entry: `bellows/knowledge/BACKLOG.md` line 35 (2026-05-21 addition)
- Caller sites: `bellows/bellows.py:451, 486, 542, 577` (pre/post diff capture per step)
- Diff capture: `bellows/bellows.py:678-694` (`_capture_git_diff`)
- Diff parse: `bellows/bellows.py:697-731` (`_parse_diff_stat`)
- Consumer gate (informational): `bellows/gates.py:594-597` (`_gate_file_change_audit`)
- Consumer gate (blocking): `bellows/gates.py:600-624` (`_gate_scope_check`)
- Today's reproductions: `bellows/verdicts/resolved/processed-verdict-extract-plan-required-deposits-set-to-list-2026-05-25-step-1.md` and `-step-2.md`

**Worktree-prefix note for the agent:** plan references use `bellows/` prefix for Planner readability. Inside the worktree, files are at the worktree root (strip the `bellows/` prefix when reading or editing).

## How to Run This Plan

Bellows dispatches this plan automatically when deposited; no manual bootstrap required.

---
---

## STEP 1 — Bellows Systems Analyst

---

> You are the Bellows Systems Analyst. Skip specialist file and glossary reads — this is a code-tracing investigation, not a domain task. **Task:** characterize the root cause of the `file_change_audit` false-negative. Three candidate hypotheses to test, in priority order: H1 — commits hide diff (`git diff --stat` shows only uncommitted changes; agents commit during step, leaving working tree clean at post-step capture); H2 — timing race vs teardown (audit runs AFTER teardown moved commits out of the worktree); H3 — wrong scope (`cwd` or pathspec mismatch causes `git diff` to look at the wrong directory). Do NOT propose or implement any fix. Findings only.
>
> **Investigation procedure:**
>
> **(1) Read the diff capture and gate flow:** read `bellows.py:430-490` (the run_plan first-step diff capture + gates.check call), `bellows.py:540-580` (the loop-step diff capture), `bellows.py:678-694` (`_capture_git_diff`), `bellows.py:697-731` (`_parse_diff_stat`), `gates.py:594-624` (`_gate_file_change_audit` and `_gate_scope_check`). Map the lifecycle: when is pre_diff captured, when does the agent run, when does the agent commit, when is post_diff captured, when is teardown called. Produce a sequence diagram or numbered timeline of these operations relative to the worktree's git state.
>
> **(2) Test H1 directly in an isolated worktree.** Create a scratch worktree: `git worktree add /tmp/bellows-h1-test HEAD --detach` from inside `bellows/` directory. Inside `/tmp/bellows-h1-test`: (a) run `git --no-pager diff --stat --relative -- .` (capture as `pre_clean.txt`); (b) make a real edit — `echo "# H1 test marker" >> README.md`; (c) run the same `git diff` command (capture as `post_dirty.txt`); (d) `git add README.md && git commit -m "h1 test"`; (e) run the same `git diff` command again (capture as `post_committed.txt`); (f) compare all three. The hypothesis predicts: pre_clean.txt is empty, post_dirty.txt shows README.md change, post_committed.txt is empty. Clean up the test worktree with `git worktree remove /tmp/bellows-h1-test --force`.
>
> **(3) Test H2 by inspecting a real recent run.** Look at today's `executable-extract-plan-required-deposits-set-to-list-2026-05-25` step 1 — examine the runner logs at `bellows/logs/` (find the step JSON or terminal log corresponding to step 1). Identify whether the agent's commit happened BEFORE post_diff was captured. If yes, H1 is supported (commits run during the agent's step, not after). If the timeline shows the agent did NOT commit during the step but the gate still reported 0 files, H1 is partially refuted and H2/H3 deserve more weight.
>
> **(4) Test H3 by examining the cwd.** Confirm that `_capture_git_diff` receives `wt_path` (not `project_path`) at the call sites. The function parameter is named `project_path` (bellows.py:678) but the callers (bellows.py:451, 486, 542, 577) pass `wt_path`. Document this naming discrepancy. Determine whether the `cwd=project_path` argument inside the function (line 688, which is actually receiving `wt_path`) is correct — i.e., is the diff being captured against the worktree's git state, not the main project state. Use `git rev-parse --show-toplevel` from inside a recent worktree (if one still exists at `.bellows-worktrees/`) to confirm the worktree's own git root.
>
> **(5) Run a controlled reproduction.** Inside a scratch worktree, simulate the full sequence: capture pre_diff (empty expected), make an edit, commit, capture post_diff. Pass both diffs to `_parse_diff_stat(post_diff, pre_diff, project_path)` (you can import this from bellows.py inside a python3 -c session). Confirm the function returns `[]` even though a file was clearly changed and committed. This is the smoking-gun reproduction if H1 is correct.
>
> **(6) Verdict per hypothesis.** Rate each of H1/H2/H3 as: CONFIRMED (direct evidence in this investigation), HIGH (strong indirect evidence), MEDIUM (plausible, needs more data), LOW (refuted by this investigation), N/A. State the confidence level with one-sentence rationale per hypothesis.
>
> **(7) Verification blocks per Rule 39.** For each hypothesis-supporting claim that a future fix plan would build on, produce a `(claim, query, expected_output)` verification block. The acting agent of any downstream fix plan will re-run these queries before editing.
>
> **(8) Surface secondary findings.** If the investigation reveals related issues — e.g., `_parse_diff_stat`'s `..` path filtering being a separate confound, or `cwd` mismatch in `_capture_git_diff` — note them in a "Related observations" section. Do NOT propose fixes for them.
>
> **Deposit findings** at `bellows/knowledge/research/file-change-audit-false-negative-2026-05-25.md` with sections: (a) sequence-diagram/timeline of pre_diff→agent_run→commit→post_diff→teardown, (b) H1 test results (3 git diff captures + analysis), (c) H2 examination of today's run logs, (d) H3 cwd/path scope analysis, (e) controlled reproduction outcome, (f) verdict per hypothesis with confidence levels, (g) verification blocks per Rule 39 for any HIGH/CONFIRMED claims, (h) related observations, (i) Output Receipt with Status: Complete.
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/research/file-change-audit-false-negative-2026-05-25.md`
