# Bellows Teardown — Dirty-Main Root-Cause Diagnostic
**Date:** 2026-06-05 | **Tier:** Diagnostic | **Dispatch Mode:** manual_bootstrap | **Test Scope:** none | **Execution:** Step 1 (SA) | **Priority:** 1

**auto_close:** false
**pause_for_verdict:** after_step_1

## Execution Map
Step 1 (SA) — single investigative step. Read-only on source + sandboxed reproduction in /tmp. No Bellows source change.

## Context

The lessons-forge baton nominated "Gap 3 dirty-tree auto-stash" as the next
reliability cut. Auto-stash automates cleanup of a dirty main at teardown — it
treats "main is dirty" as permanent and mops up. This diagnostic rejects that
frame until the prior question is answered: **a worktree run should leave main's
working tree clean by construction; a dirty main is an anomaly with a cause.**

Teardown is already heavily patched. The research/dev corpus includes
`worktree-teardown-dirty-tree-precheck-surface-2026-05-27.md`,
`dirty-tree-precheck-false-trip-filter-2026-05-28.md`,
`worktree-precheck-hardening-2026-05-29.md`,
`reattempt-teardown-on-continue-resume-2026-06-04.md`,
`teardown-b-raise-on-log-failure-2026-06-05.md`,
`teardown-git-operations-mapping-2026-05-21.md`,
`worktree-teardown-resume-regression-2026-05-31.md`. Repeated patching of one
function across a month is itself the signal: cause has not been cut, symptoms
have been caught. The goal here is the cut, not a new catch.

This is NOT a redo of the 05-28 filter-surface work (which made the
`_is_lifecycle_artifact` filter more complete). It asks the orthogonal,
upstream question and treats auto-stash as a last-resort backstop only.

## How to Run This Plan

Manual bootstrap — run the Step 1 SA prompt directly via Claude Code against the
bellows repo. Do NOT deposit as a `bellows`-mode plan in a watched directory: the
daemon must not dispatch a worktree run that studies its own teardown. SA works
in-place, read-only on source; any reproduction is confined to a /tmp throwaway repo.

---
---

## STEP 1 — BELLOWS SYSTEMS ANALYST

---

> **Identity:** You are the Bellows Systems Analyst. Begin your reply with the single line `SA claim: teardown dirty-main root-cause diagnostic` BEFORE any reads (liveness anchor). **Reads (in order):** `agents/BELLOWS_SYSTEMS_ANALYST.md`; `bellows.py` lines 38-60, 881-1055, 1056-1090; then the teardown corpus listed in the plan Context (at minimum the 05-21 git-operations mapping, the 05-27/05-28/05-29 dirty-tree/filter docs, the 05-31 resume-regression, and the 06-04/06-05 dev docs). Emit a 1-line acknowledgment after each read.
>
> **Frame:** A worktree run should leave main's working tree clean by construction. Find every reason it doesn't, decide which are eliminable at the source, and only then judge whether any residual justifies a backstop. **Do NOT modify Bellows source. Reproduction only in a /tmp throwaway git repo.** Prefix each section below with a 1-line marker.
>
> **(R0) Patch-accretion audit.** From the corpus, build a table of every teardown fix shipped to date: date, what it changed, which failure it targeted, and whether that failure recurred afterward. Conclusion line: are these independent bugs or repeated catches of one uncut cause?
>
> **(R1) Dirty-main source inventory — ROOT.** Enumerate every distinct path by which main's working tree becomes dirty during a worktree run, grounded in real porcelain lines from logs/evidence (not hypotheses). For each source record: (i) example path(s); (ii) tracked vs untracked; (iii) the writer — agent-in-worktree, a tool with a hardcoded canonical path (e.g. anvil `run_cycle` joining `ANVIL_ROOT`, which writes the cycle report into MAIN not the worktree), the daemon's own bookkeeping, or the Planner editing mid-flight; (iv) whether the content is also landed via cherry-pick or is a pure side-write that the worktree commits never contain.
>
> **(R2) Per-source eliminability.** For each R1 source, state the root-cause fix that makes main never dirty for that source, and its blast radius:
> - lifecycle/daemon artifacts that still trip → filter completeness (where, exactly).
> - misdirected canonical writes (tool writes to main from inside a worktree) → the fix must thread worktree isolation against the reason the canonical path exists. Note specifically: F8 hardcoded `ANVIL_ROOT` so `cycle_reports.report_path` records a path that survives teardown; naively "write to the worktree" reintroduces the dead-path bug F8 fixed. Options to weigh: write-in-worktree + record-canonical; teardown adopts/commits the declared side-artifact; or a declared-artifact contract the daemon owns. Pick one and justify.
> - legitimate concurrent edits (e.g. `PROJECT_STATUS.md` touched mid-flight) → process rule vs daemon ownership of the file; is this ever truly unavoidable?
> Classify each source as ELIMINABLE (and how) or IRREDUCIBLE (why).
>
> **(R3) Teardown model — the structural lever.** Using the 05-21 git-operations mapping, characterize the current model: cherry-pick worktree commits onto the live main working tree, which is what makes working-tree dirtiness able to block landing at all. Evaluate the alternative of landing at the ref level (e.g. fetch/merge or fast-forward the worktree branch into main without checking out onto a dirty tree), under which a dirty working tree is largely irrelevant to whether commits land. State what breaks, migration cost, and whether this dissolves the dirty-tree failure class outright rather than per-source. Give a keep-current vs redesign recommendation with reasoning.
>
> **(R4) Residual + backstop judgment.** After R2 eliminations and the R3 recommendation, list the dirty-main cases that genuinely survive. ONLY for that residual, evaluate auto-stash as a backstop, carrying the full safety contract: (a) stash flag fit (`-u` for untracked; never `-a`); (b) overlap/pop-conflict risk — can a cherry-picked worktree commit touch the same path as a stashed main file (reproduce the worst case in /tmp: stash -u → cherry-pick same path → pop; record clean-pop vs conflict vs retained-stash); (c) atomicity — on pop conflict, the land-or-raise contract that avoids orphaned stashes / conflict markers under a passed=True line. **If the residual is empty, say so and recommend auto-stash be dropped entirely as dead complexity.**
>
> **Verdict.** Produce: (1) a ranked root-cause elimination plan — which sources to cut, in what order, each as its own follow-up plan stub; (2) keep-vs-redesign call on the teardown model; (3) auto-stash disposition — backstop-for-named-residual, or cut. No fix is authored here. Mark any claim you can't settle from code + logs + sandbox as OPEN.
>
> Standard prompt-feedback protocol — append issues to `knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `knowledge/research/teardown-dirty-main-rootcause-2026-06-05.md`
