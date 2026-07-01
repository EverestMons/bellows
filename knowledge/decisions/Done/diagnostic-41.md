# Bellows — Worktree Teardown/Resume Friction Cluster Root Cause (FORWARD rows 4/5/12/13)
**Date:** 2026-06-13 | **Tier:** Medium | **Dispatch Mode:** bellows | **Execution:** Step 1 (SA) | **pause_for_verdict:** after_step_1

## Context (Rule 27)
Four open bellows FORWARD rows describe friction in the worktree teardown→resume git flow; they likely share the same merge-model and branch-tracking surface, so one root-cause diagnostic covers the cluster:
- **Row 4** (2026-05-22): teardown cherry-pick conflict when local `main` has uncommitted `PROJECT_STATUS.md` edits.
- **Row 5** (2026-05-22): parallel-diagnostic cherry-pick conflicts on shared append-only bookkeeping files at teardown.
- **Row 12** (2026-05-30): worktree re-creation on resume checks out `main` HEAD, not the step's branch — work from the prior step may not be the base.
- **Row 13** (2026-05-31): teardown→resume auto-resume-from-branch + auto-stash — deferred friction-reduction.
Anchors (re-verify by grep): `_create_worktree` (bellows.py:893), `_teardown_worktree` (bellows.py:1103); the cherry-pick/merge/branch logic lives inside or is called from teardown. Prior shipped work in this area (read for lineage, do not assume current): `executable-bellows-teardown-merge-model-2026-06-05`, `executable-reattempt-teardown-on-continue-resume-2026-06-04`, `executable-preserve-unlanded-commits-on-stranded-cleanup-2026-06-01`, `executable-worktree-precheck-hardening-2026-05-29`, `executable-worktree-teardown-dirty-tree-precheck-2026-05-27` (all in `knowledge/decisions/Done/`). Investigation ONLY — author no fix code; the fix executable(s) follow CEO review. Read/DB/git access read-only.

## How to Run
Bellows dispatches this plan automatically when deposited; no manual bootstrap required.

---
---

## STEP 1 — Bellows Systems Analyst

---

> **FIRST — before any reads or work: post a short visible chat message (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** Liveness anchor — do NOT rename the plan file (Bellows owns the claim). **AFTER posting:** read your specialist file `agents/BELLOWS_SYSTEMS_ANALYST.md` first, then the four rows' archive context (`knowledge/BACKLOG-ARCHIVE.md` entries dated 2026-05-22/30/31) and the prior-work plans named in Context. **Post a 1-line "Read X." after each file read and a 1-line "Drafting Section N." per section.** Ground every claim at file:line or a named log/git observation.
>
> **Section 1 — Teardown merge model anatomy.** Read `_teardown_worktree` (bellows.py:1103) in full and every helper it calls. Document at file:line: how worktree commits are landed onto the project's `main` (cherry-pick? merge? rebase? format-patch?), in what order, what the dirty-tree precheck does and when it runs, and the EXACT failure path when a cherry-pick conflicts. Identify which files are most conflict-prone and why (append-only bookkeeping like `PROJECT_STATUS.md`, `agent-prompt-feedback.md`, BACKLOG/FORWARD, lessons files).
>
> **Section 2 — Resume worktree re-creation anatomy.** Read `_create_worktree` (bellows.py:893) and the resume/step-dispatch path that calls it. Document at file:line: on a multi-step plan's resume (post-verdict), is the worktree created from `main` HEAD or from the branch/commit carrying the prior step's work? Trace where the prior step's commits live between steps and whether the resumed step's worktree has them as its base. This is the Row 12 question — answer it definitively with the code path.
>
> **Section 3 — Per-row root cause.** Root each of the four rows against Sections 1–2, CONFIRMED or with the precise mechanism + evidence pointer (file:line / archive log line): Row 4 (uncommitted main PROJECT_STATUS.md vs cherry-pick), Row 5 (parallel append-only conflicts), Row 12 (resume base branch), Row 13 (what auto-resume-from-branch + auto-stash would actually automate, and whether Row 12's fix subsumes it). Note any overlap/subsumption between rows (e.g., does fixing Row 12 dissolve Row 13? does an append-only-merge strategy fix both 4 and 5?).
>
> **Section 4 — Fix shapes.** Propose per problem (or per merged sub-cluster), comparing ≥2 options each, with blast radius at file:line and test strategy: (a) the cherry-pick-conflict class (rows 4+5) — e.g. merge-strategy `-X ours/theirs` for known append-only files, vs. rebase-onto, vs. precommit-stash of dirty main, vs. teaching teardown to union-merge append-only files; (b) resume base (row 12) — create the resumed worktree from the prior step's branch/commit rather than main HEAD; (c) row 13 friction-reduction — whether it survives as separate work after (a)/(b). Recommend one per problem and whether they ship as one executable or several.
>
> **Section 5 — Gap Assessment + `### Verification Blocks` (Rule 39).** Gap Assessment table `| Gap | Current State (file:line) | Proposed State | Change Required |`. Verification Blocks `(claim, query, expected_output)` for: the teardown merge mechanism, the resume-base finding (row 12), the conflict-prone-file identification, and any row subsumption. Close with **CEO decision forks** (each with a recommendation): fix-shape per sub-cluster; one executable vs several; whether Row 13 is closed-as-subsumed or kept open.
>
> **BEFORE FINISHING — explicitly `git add` your deposit file and `git commit` it.** Use `with open()` for the deposit; no heredocs. Standard prompt feedback → `knowledge/research/agent-prompt-feedback.md`. **Deposits:**
> - `bellows/knowledge/research/worktree-teardown-resume-cluster-2026-06-13.md`
