# bellows — executable: `tools/reconcile_plan.py` — the three-surface orphan recovery mechanized (and issue_verdict's dangling runbook pointer re-aimed)

**Date:** 2026-08-26 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** targeted (the new tests) + full suite at QA | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always

**auto_close:** false

**Depends on:** the CEO's batch-3 proceed; the reconciliation memory's verified three-surface contract (exec-454/458); the dangling pointer verified live (issue_verdict.py:91 names a CLAUDE.md runbook that does not exist — grep 0); the verdicts schema read live.

## Why this exists

Orphan recovery is a rare, high-stakes multi-surface act performed from a memory entry; each manual performance risks missing the ONE surface that drives AWAITING VERDICT. The tool performs all three in one transaction, refuses live workers, and the memory retires at close.

## What this plan does NOT do

- Never moves the plan FILE (a git act — the tool PRINTS the exact commands); never checkpoints/commits the DBs (the WAL law, in the docstring); never touches a plan whose state is in_progress without the explicit killed-verified flag.

## Numbers discipline

⚠️ **Measured 2026-08-26; re-measure pre-flight; mismatch → HALT; counts carry measure-record-supersede.**

| id | pin | value | anchor |
|---|---|---|---|
| C1 | tools/ | reconcile_plan.py ABSENT; run_check.py present (5 entries — record; supersede with derivation) | `tools/` (repo-relative — worktree law) |
| C2 | the pointer line | `"see the reconciliation runbook "` count-1 at issue_verdict.py (~L91) | `tools/issue_verdict.py` |
| C3 | schema | verdicts(outcome, decided_by, disposition_summary); plans(lifecycle_state, closed_at, plan_doc_ref); state vocab abandoned|closed|halted|in_progress | `lifecycle.db` read-only |

## STEP 1 — DEV (the tool + the pointer fix + tests)

> **Task A — worktree discipline.** `cd "$(git rev-parse --show-toplevel)" && test -d tools && echo TREE_OK` — HALT unless TREE_OK. Probes: (i) `test -f tools/reconcile_plan.py && echo 1 || echo 0`, (ii) `/usr/bin/grep -cF -- "reconcile_plan.py" tools/issue_verdict.py; true`. (0,0) → full run; (1,0) → resume at the pointer fix; (1,1) → Task D commit-check; (0,1) → HALT.
>
> **Task B — write `tools/reconcile_plan.py`** with EXACTLY this contract (author the code to it; keep it stdlib-only):
> - `usage: reconcile_plan.py <plan-id> {closed|halted|abandoned} --outcome {continue|stop} --summary "<text>" [--doc-ref <path>] [--killed-verified] [--db <path>]` (`--db` defaults to the repo-root lifecycle.db resolved relative to the tool's own location — worktree-safe).
> - FIRST prints the plan's current row, every NULL-outcome verdicts row, and any `verdicts/pending/verdict-request-<id>-step-*.md` files — the look-before-mutate law.
> - REFUSES (exit 3, nothing written) when `lifecycle_state == 'in_progress'` and `--killed-verified` is absent; the refusal text: a worker can survive ENOSPC and wedge (~70 min measured) — verify with `ps -o etime,%cpu -p <pid>`, kill it, then re-run with the flag.
> - ONE transaction: `UPDATE plans SET lifecycle_state=?, closed_at=<UTC now>, plan_doc_ref=COALESCE(?, plan_doc_ref) WHERE id=?` and `UPDATE verdicts SET outcome=?, decided_by='planner', disposition_summary=? WHERE plan_id=? AND outcome IS NULL` — the second UPDATE's rowcount is PRINTED (0 is legal and printed as such — the plan may never have paused).
> - Archives each pending `verdict-request-<id>-step-*.md` to `verdicts/archived/` (rename; report each).
> - ENDS by printing the remaining HUMAN acts verbatim: the git move of the plan file to `Done/` or the `halted-` name, and the commit — the tool never performs git acts.
> - Docstring carries the WAL law (writes are live-correct in the -wal; NEVER checkpoint or commit the DBs from a Planner session) and cites exec-454/458.
> Then the POINTER FIX: in `tools/issue_verdict.py`, replace the C2 anchor sentence fragment `see the reconciliation runbook ` + its continuation `"in CLAUDE.md for manual orphan-recovery."` (locate the full two-part string, count-1) so the message reads: `run tools/reconcile_plan.py <plan-id> ... (see its --help) for orphan-recovery.` Post-probes: `"reconcile_plan.py"` >= 1 in issue_verdict.py; `"in CLAUDE.md for manual orphan-recovery"` == 0; `"killed-verified"` >= 2 in the new tool; `"outcome IS NULL"` >= 1.
>
> **Task C — tests `tests/test_reconcile_plan.py`** (new): six tests over a tmp lifecycle.db built with the REAL schema subset (CREATE the plans + verdicts tables verbatim from C3) + a tmp verdicts/pending dir, invoking the tool via subprocess with `--db`: (1) full reconcile of a `halted` target: plans row updated, the NULL-outcome verdict gains outcome/decided_by/summary, the pending file lands in archived/, exit 0; (2) in_progress WITHOUT the flag → exit 3, DB byte-unchanged (compare full table dumps); (3) in_progress WITH `--killed-verified` → proceeds; (4) a plan with ZERO null-outcome verdicts → rowcount 0 printed, exit 0; (5) a TERMINAL-outcome verdict row is NEVER touched (its outcome/summary byte-identical after); (6) bad state vocab → exit 2 usage. Targeted run — 0 failed (record counts; supersede with derivation).
>
> **Task D — dev log + commit.** `knowledge/dev-logs/reconcile-plan-tool-dev-2026-08-26.md` (probe raws, targeted raw). Commit (WORKTREE toplevel): `cd "$(git rev-parse --show-toplevel)" && git add tools/reconcile_plan.py tools/issue_verdict.py tests/test_reconcile_plan.py knowledge/dev-logs/reconcile-plan-tool-dev-2026-08-26.md && git commit -m "[<id from your plan filename>] reconcile-plan-tool(reconcile-plan-tool-2026-08-26): three-surface orphan recovery mechanized; issue_verdict pointer re-aimed" -- tools/reconcile_plan.py tools/issue_verdict.py tests/test_reconcile_plan.py knowledge/dev-logs/reconcile-plan-tool-dev-2026-08-26.md && git rev-parse HEAD` — **CAPTURE_COMMIT**.
>
> **Deposits:**
> - `tools/reconcile_plan.py`
> - `tools/issue_verdict.py`
> - `tests/test_reconcile_plan.py`
> - `knowledge/dev-logs/reconcile-plan-tool-dev-2026-08-26.md`
>
> **Scope:**
> - `tools/reconcile_plan.py`
> - `tools/issue_verdict.py`
> - `tests/test_reconcile_plan.py`
> - `knowledge/dev-logs/reconcile-plan-tool-dev-2026-08-26.md`

## STEP 2 — QA (FULL suite + refusal proof)

> **Item 1 — full suite.** `cd "$(git rev-parse --show-toplevel)"`; `python3 -m pytest tests/ --tb=short -q 2>&1 | cat | tee knowledge/qa/evidence/reconcile-plan-tool-2026-08-26/pytest_full.txt` — 0 failed (record the count; derivation vs 1511 + 6).
> **Item 2 — behavior proof on a SCRATCH COPY (the live DB is NEVER an operand — the weakest-instrument law).** `cp` lifecycle.db to /private/tmp; run the COMMITTED tool against the copy targeting a closed plan → the printed look-before-mutate block matches a read-only query of the same copy; then flip one row to `in_progress` in the copy and re-run WITHOUT the flag → exit 3 with the refusal text and the copy's tables byte-unchanged (dump-compare). Paste all raw.
> **Item 3 — hygiene + receipt** `knowledge/qa/evidence/reconcile-plan-tool-2026-08-26/qa-receipt.md`: numstat 4 files; toplevel; reflog `-n 4` → 0 amends; per-item table, then the Rule 20 block INSIDE a "Verification"-headed section.
>
> ⚠️ **Gate note:** pytest summary named above — the gate parses; no benign override pre-declared.
>
> **Deposits:**
> - `knowledge/qa/evidence/reconcile-plan-tool-2026-08-26/pytest_full.txt`
> - `knowledge/qa/evidence/reconcile-plan-tool-2026-08-26/probes-raw.txt`
> - `knowledge/qa/evidence/reconcile-plan-tool-2026-08-26/qa-receipt.md`
>
> **Scope:**
> - `knowledge/qa/evidence/reconcile-plan-tool-2026-08-26/pytest_full.txt`
> - `knowledge/qa/evidence/reconcile-plan-tool-2026-08-26/probes-raw.txt`
> - `knowledge/qa/evidence/reconcile-plan-tool-2026-08-26/qa-receipt.md`

Rule 20 banner (byte-exact, inside the QA receipt's VERIFICATION section):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```

## Drafting Cycle

**Tier:** T1 — one tool with the memory's verified contract encoded, refusal-first; the live DB never an operand anywhere in the plan.

**Walk register:** `bellows/knowledge/research/walk-register-reconcile-plan-tool-2026-08-26.md`

**Walk 0 (context pin, measured):** the three surfaces + the AWAITING-VERDICT signal from the exec-454/458 measurements; the dangling pointer verified live; the alive-worker refusal; the WAL law; the schema read.

**Walks:**
- Weak spots:          w1 1 folded — Item 2 carried the author's own mid-sentence self-correction (the 545-F3 drafting-noise class, caught by this walk): de-garbled to the clean scratch-copy form with the byte-unchanged dump-compare.
- Destruction:         w1 dry — refusal-first (exit 3 writes nothing, test 2's dump-compare proves it); one transaction for the two UPDATEs; the pending-file archive is a rename, recoverable.
- Vulnerabilities:     w1 dry — the NULL-outcome predicate is the exact AWAITING-VERDICT signal (exec-454/458); terminal verdict rows untouchable by construction (test 5); the live DB appears in NO mutating operand anywhere in the plan.
- Integration-record:  w1 dry — the dangling pointer verified live before re-aiming; the memory retires at close (Planner-direct, class: stale — the same-plan discipline's sandbox split, stated).
- ACID:                w1 dry — counts clause-clothed; one pathspec-limited commit, 4 files.
- **Walk 1 total: one finding, folded.**
- Weak spots:          w2 dry — the cleaned Item 2 re-read; every probe earnable.
- Destruction:         w2 dry.
- Vulnerabilities:     w2 dry.
- Integration-record:  w2 dry.
- ACID:                w2 dry.
- **Walk 2 total: 0 findings — all five lenses dry.**

**Closing:** ✅ **BAR MET at walk 2 — dry confirming pass, all five lenses.** T1 two-walk form; no direction-class finding; close is MANUAL (CEO-lane verdicts).

**Fold-and-deposit exactly once.**

## Cycle Manifest
tier: T1
target: bellows/tools/reconcile_plan.py
class: shop-infra
reads: /Users/marklehn/Developer/GitHub/bellows/tools/issue_verdict.py, /Users/marklehn/Developer/GitHub/bellows/lifecycle.db
writes: tools/reconcile_plan.py, tools/issue_verdict.py, tests/test_reconcile_plan.py, knowledge/dev-logs/reconcile-plan-tool-dev-2026-08-26.md, knowledge/qa/evidence/reconcile-plan-tool-2026-08-26/pytest_full.txt, knowledge/qa/evidence/reconcile-plan-tool-2026-08-26/probes-raw.txt, knowledge/qa/evidence/reconcile-plan-tool-2026-08-26/qa-receipt.md
open_forks: batch-3 item 3 (the rename fix in _parse_diff_stat, SERIAL); the memory retirement at close (Planner-direct, class: stale); the 23-row triage at batch close
walks: 2
yields: 1, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=N/A
coherence: N/A
