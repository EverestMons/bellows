# bellows — T6 READS EVERY SCOPE THAT EVALUATES AN ANNOTATION: its helper descends into the blocks of module- and class-level compound statements — `if`, `for`, `while`, `with`, `try`, `match` — and into a class defined inside a function, reading each block by field name so no node type newer than Python 3.9 is named, and still passes over a function body's own annotations (thread 314)

**Date:** 2026-09-15 | **Project:** bellows | **Tier:** Small (one test helper's walk; two parametrized test items, eighteen cases; one mutation manifest; one dev-log) | **Dispatch Mode:** bellows | **Test Scope:** full-suite (the commit chain's gate; `pytest tests/ -q`) | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** after_qa_step | **known_failures:** 0 | **Discharges:** thread 314 | **cycle_tier:** T1

**auto_close:** false

**Post-close:** no daemon restart owed — only a test file and its records change. One bound follow-up, T-3's check — the CEO's act on the Air, where the Planner only reads: after the Air pulls, `cd ~/Developer/GitHub/bellows && .venv/bin/python -m pytest tests/test_tools_safe_to_invoke.py -q` under its 3.9.6 venv — `23 passed, 1 skipped`, the `match` case skipped below 3.10 — the Planner pasting the result into `tuyere.threads done 314 --commit bellows:<the DEV's first commit>`. The mini's `/usr/bin/python3` (3.9.6) has no pytest (P3), so the Air's run is the only run of this file under 3.9.

**Depends on:** thread 314 (filed 2026-09-12 19:56, found at #100095's (b) read, session d04ebd33); t6 and its helper as #100095 built them (`knowledge/decisions/Done/executable-100095.md`, thread 305, `d9bf917`) — `_def_time_unions`, its future-import check, `_has_union`, the function-annotation walk, and `_check_stmts`, which reads a module's top-level statements and recurses into class bodies alone (P1); #100095's spec for t6, its *What this changes* 2: report a union in an annotation evaluated at definition time — a function's argument or return, or a module- or class-level `AnnAssign` — pass over a function body's local `AnnAssign`, and be Python 3.9 code itself, because the Air runs the file under 3.9.6 (P2). The order: the reliability stretch; this plan writes `tests/test_tools_safe_to_invoke.py` and its own manifest, run file and dev-log, which no plan held or drafting writes — thread 329's held fix reads the test file (P5) — so it runs in any order beside them, held for the CEO's release as every bellows plan is. Clone origin by kind: #100095 — the helper's own plan and its spec; the plan's shape — DEV → QA, the commit chain, the mutation run, the Rule 20 block — from #100101 (Done 2026-09-14), the newest completed bellows plan.

**Tier computed (§1):** **T1** — T-3 fires: the helper and its tests run under the Air's venv 3.9.6 and the mini's 3.12.14, whose `ast` modules differ — `ast.Match` and `ast.TryStar` exist on 3.12.14 and not on 3.9.6 (P3) — so a helper that named either would error the whole file on the Air, and a `match` fixture parses on 3.10 and later only. T-1 does not (one test file); T-2, T-4, T-5, T-6 and T-7 do not (a test helper changes; nothing is written, deleted or governed); T-8 does not (a structure clone of #100095's t6 and its helper).

## CEO Context

One of the suite's safety tests, t6, checks that no module uses the `X | Y` type syntax where Python 3.9 — the Air's version — would evaluate it and fail at import; two census tools broke that way on the Air (thread 305). t6 finds such annotations on functions and at the top level of modules and classes, but it does not look inside an `if`, `for`, `with` or `try` block at the top of a module, or inside a class defined in a function — places Python evaluates the annotation too. Nothing in the repo does that today, so t6 is green and this is a gap, not a live failure. This plan makes t6's helper look in those places as well, while still ignoring annotations inside function bodies, which Python never evaluates. Only a test file changes; nothing needs a restart. The class is shop-infra, so it holds for your release.

## What this changes

1. **`tests/test_tools_safe_to_invoke.py`** (P1):
   - `_check_stmts(stmts)` (:298–303) becomes `_check_stmts(stmts, evaluated)`, `evaluated` true at module and class scope and false in a function body: an `AnnAssign` is reported only when `evaluated`; a `ClassDef`'s body is read as evaluated; a `FunctionDef`'s or `AsyncFunctionDef`'s body is read as not evaluated, so a class defined inside it is still found; every other statement's blocks — `body`, `orelse`, `finalbody`, each handler's `body`, each match case's `body` — are read with the enclosing scope, by field name through `getattr`, so no node type newer than 3.9's `ast` is named (P3); the call `_check_stmts(tree.body)` (:305) becomes `_check_stmts(tree.body, True)`; a comment says why. The future-import check (:269–273), `_has_union` (:275–279) and the function-annotation walk (:281–296) are unchanged.
   - After t6, the file's last line (:323), a helper `_module(tmp_path, source)` that writes a module under `tmp_path`, and two items:
   - (t7) `test_t6_reads_every_evaluated_scope`, parametrized — fourteen cases, each a module holding one `x: int | None = None` that the helper must report at its line: `if`, `elif`, `else`, `for`, `for-else`, `while`, `with`, `try`, `except`, `try-else`, `finally`, `class-in-function`, `class-in-if`, and `match`, skipped below 3.10, where `match` does not parse;
   - (t8) `test_t6_passes_over_unevaluated_scopes`, parametrized — four cases the helper must not report: `function-local`, `block-in-function`, `function-in-if`, and `future-import`.
   - Red on the base: t7's fourteen; t8's four green by design, since the base helper reports nothing inside a function or a block.
2. **`knowledge/mutants/def-time-union-nested.json`** — `{"target": "tests/test_tools_safe_to_invoke.py", "mutants": [ … ]}`, each mutant's keys `name`, `why`, `anchor`, `replacement` and `expect_fail`; eight, each `expect_fail` a node id: (m1) the compound blocks dropped → t7; (m2) `orelse` dropped → t7; (m3) `finalbody` dropped → t7; (m4) the handlers dropped → t7; (m5) the match cases dropped → t7, killed on the mini's 3.12; (m6) the class inside a function dropped → t7; (m7) a function body read as evaluated → t8; (m8) a block inside a function read as evaluated → t8. An anchor that matches its target other than once is the run's `ERROR` (`tools/mutation_check.py:266–270`).
3. **The dev-log** `knowledge/development/dev-log-def-time-union-nested-2026-09-15.md`.
4. **Not changed:** the test functions t1–t6, unedited; the rest of `_def_time_unions`; every other file.

## Why this exists

#100095's t6 reads an `AnnAssign` only through `_check_stmts(tree.body)`, which visits a module's top-level statements and recurses into class bodies alone (P1). An annotated assignment nested in a module-level `if`, `for`, `while`, `with` or `try` block — or in the body of a class defined inside a function — is evaluated when that code runs, so a PEP 604 union there fails under Python 3.9 exactly as the two census tools did, and t6 does not read it. None exists today: the prototype's helper, reading every such block, finds nothing in the repo (t6 green over the real tree, P4). Thread 314, found at #100095's (b) read, marks it low priority because t6 still guards the pattern that failed; this plan closes the gap while t6's spec is fresh.

## What this does NOT do

- It does not change what t6 scans (t5's files and the test files) or its future-import rule.
- It does not tell a block that never runs from one that does: a union under `if TYPE_CHECKING:` or `if False:` at a module's top level is reported, though Python never evaluates it there, and the future import — the remedy t6's failure names — clears it; neither construct is in the repo today (`git grep -F TYPE_CHECKING -- '*.py'` over bellows: no file; no module-level `if False:`).
- It does not report a function body's own annotated assignment, in any block of it — never evaluated, as #100095's spec states.
- It does not name `ast.Match` or `ast.TryStar`: the `match` arm is read through the generic `cases` field, and a `try … except*` block through `handlers`, so the helper runs unchanged on 3.9.6.
- It does not change any tool or module outside the test file.

## MUST-PRESERVE

- ⛔ **The test functions t1–t6 pass unedited;** the edits are `_check_stmts` and its call, and the items after the file's last line.
- ⛔ **The helper and its tests stay Python 3.9 code:** no node type newer than 3.9's `ast` named, a tuple in `isinstance`, never `A | B` in an annotation — the Air runs the file under 3.9.6.
- ⛔ **A function body's own annotated assignment is never reported** (t8).
- ⛔ **t6 over the repo stays green:** no module today holds a nested union (P4).
- ⛔ **Every `expect_fail` is a node id,** and the mutation run is redirected into its deposit, never piped.
- ⛔ **Test code runs under pytest inside `tests/` or not at all** (bellows `CLAUDE.md`, *Test code*; thread 313).
- ⛔ **The thread-262 stop:** a QA step that must change production code STOPS and requests a verdict.

## Numbers discipline — measured 2026-09-15 by the Planner (bellows main `3753152`; `tests/test_tools_safe_to_invoke.py` blob `b978d4a1`, as at `65f713c`)

| # | pin | value | how to re-derive |
|---|---|---|---|
| P1 | ⛔ the helper | `tests/test_tools_safe_to_invoke.py`, 323 lines, 6 test functions: t5 `test_every_module_parses_under_python39` :219, its `OLD = "/usr/bin/python3"` :220; `_def_time_unions` :262 — the future-import check :269–273 (`__future__` :270), `_has_union` :275–279, the function-annotation walk :281–296, `_check_stmts` :298–303, its call `_check_stmts(tree.body)` :305, `return hits` :307; t6 :310–323, the file's last line :323 | `sed -n '262,323p' tests/test_tools_safe_to_invoke.py`; `wc -l` |
| P2 | the prior writers and #100095's record | `:262–307`, all 46 lines #100095's `d9bf917`; the file's newest writers `d9bf917` (2026-09-12), `440bdbd` (census-tool-parses-under-39) and #100088's `222252b` (2026-09-11); counts: `def _check_stmts(stmts):` 1, `_check_stmts(tree.body)` 1, test functions 6, `ast.Match` 0; #100095's *What this changes* 2 (its :20) — the t6 spec; its manifest `knowledge/mutants/def-time-union.json`, one mutant (the future import removed from `tools/fold_signal_census.py`) → t6, `MUTATION: 1 killed, 0 survived, 0 error`; its Post-close, the file's six passed on the Air | `git blame -L 262,307 tests/test_tools_safe_to_invoke.py`; the plan and the manifest |
| P3 | the interpreters' `ast` | 3.9.6 (`/usr/bin/python3`, and the Air's venv): `ast.AsyncWith` and `ast.AsyncFor`, no `ast.Match`, no `ast.TryStar`; 3.12.14 (the bellows venv): all four; `/usr/bin/python3` has no pytest (`ModuleNotFoundError: No module named 'pytest'`) | `python -c "import ast; print(hasattr(ast, 'Match'))"` under each |
| P4 | the prototype | a scratch clone of bellows at `65f713c` (`scratchpad/r314`, branch `r314`): `0b486d13` the tests, `3e0df794` the helper, `1c416d90` the manifest, `2b94ff76` its run; the file over the base helper `14 failed, 10 passed` — t7's fourteen — and over the change `24 passed`, t6 over the real tree among them; t7 and t8 verbose, `18 passed`; `MUTATION: 8 killed, 0 survived, 0 error`; `py_compile` rc 0 under 3.9.6; the file's diff, four hunks — three inside the base's `_check_stmts` and its call (:298–305), one addition after :323; the full suite behind the fence, the base `65f713c` `53 failed, 2323 passed, 3 skipped` and the prototype `53 failed, 2341 passed, 3 skipped` — the eighteen cases green, and the 53 failures the same node ids on both, none in `tests/test_tools_safe_to_invoke.py`: the scratch environment's, none the change's | the register's walk 0 |
| P5 | class; in flight; the suite | the writes → **shop-infra** (bellows, the project floor), HOLDS at admission for the CEO's release; in flight at drafting: nothing running (`status.py`: IN-FLIGHT none, AWAITING VERDICT none); held for release — threads 341's, 329's fix, 324's, 333's, 317's, 315's and 307's plans; drafting — threads 322's and 321's; none writes `tests/test_tools_safe_to_invoke.py`, and thread 329's held fix reads it; the bellows venv 3.12.14, `/usr/bin/python3` 3.9.6, the Air's venv 3.9.6; the full suite at `65f713c`, derived and not run in a canonical-shaped tree: 2377 passed, 2 skipped (thread 329's fix plan, its P5) | `status.py`; `python -V`; the suite |

DEV re-derives P1 and P3 in Item 1 and HALTs on a mechanism mismatch; P2, P4 and P5 are the drafting record.

## Drafting Cycle

**Tier:** **T1** — T-3 fires. **Walk register:** /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-def-time-union-nested-2026-09-15.md
**Walks:** walk 0 pinned (P1–P5 measured on bellows `3753152`, the file's blob as at `65f713c`; the change prototyped in a scratch clone at `65f713c`; clone-diff against `Done/executable-100095.md`: FACTS, ARTEFACTS, STRUCTURE; no walk-0 scout — T1, the Planner's call); `fold_check --save-baseline` ARMED on v0 before any fold, re-saved after every intended edit; every lens commit through `/Users/marklehn/Developer/bellows/scripts/lens_commit.py`, invoked directly with its output whole — no filter between it and the screen — its exit read; no lens or walk number in any `--desc`, and no plain commit subject carrying a walk and a lens number; `lens_order_check` after every lens commit.

- Weak spots:          w1 dry
- Destruction:         w1 1 folded — instruction 0 / record 1
- Vulnerabilities:     w1 dry
- Integration-record:  w1 dry
- ACID:                w1 dry
**Closing:** WARM close after walk 1 — BAR MET (T1), thread 314's plan. One walk, one finding, record-class — the widened walk reads a block that never runs (`if TYPE_CHECKING:`, `if False:`) as one that does, stated with the future import as its remedy and the measurement that the repo holds neither — and dry on the other four lenses; 0 of 1 fold-introduced. T1, no panel. Every lens commit through `lens_commit.py`, its output whole and its exit read, the first walk's table header committed with v0 (thread 312); the close through `close_cycle.py`. Deposit via `ready-`; HOLDS on class shop-infra, the CEO releases (`clear_plan --release-class-hold`). Close acts: no restart — only a test file changes; Post-close's check on the Air after it pulls, the file's `23 passed, 1 skipped`, the CEO's act, whose result the Planner pastes into `threads done 314`; no open fork.

## Cycle Manifest
tier: T1
target: tests/test_tools_safe_to_invoke.py
class: shop-infra
reads: tests/test_tools_safe_to_invoke.py, knowledge/decisions/Done/executable-100095.md, knowledge/mutants/def-time-union.json
writes: tests/test_tools_safe_to_invoke.py, knowledge/mutants/def-time-union-nested.json, knowledge/mutants/def-time-union-nested.run.txt, knowledge/development/dev-log-def-time-union-nested-2026-09-15.md, knowledge/qa/evidence/def-time-union-nested-qa-receipt-2026-09-15.md, knowledge/qa/evidence/def-time-union-nested-suite-2026-09-15.txt
mutants: knowledge/mutants/def-time-union-nested.json
open_forks: none — a test helper's reach widened to the scopes #100095's spec already names
walks: 1
yields: 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=VACUOUS, propagation_check=DIVERGENT:57
coherence: 1/1 body walks named in the register (1 register rows; walk-token match, NOT row coverage)
fold_baseline: governance/knowledge/decisions/drafts/.executable-bellows-def-time-union-nested.md.foldcheck.json

---

## STEP 1 — DEV (one helper's walk; two test items, eighteen cases; the mutation run; two commits)

> ⛔ **Every item starts by re-establishing the root** — `cd "$(git rev-parse --show-toplevel)" && test -f tests/test_tools_safe_to_invoke.py && echo TREE_OK` — HALT unless TREE_OK. ⛔ **The interpreter is `/Users/marklehn/Developer/bellows/.venv/bin/python`, ABSOLUTE.** ⛔ A commit's message goes to `git commit -F -` on stdin — a quoted heredoc ending the commit's own command: `<<'MSG'`, the message on the lines after it, `MSG` alone on the last — so no file is written for it (a Write-tool call inside `.git/` is refused as "a sensitive file", a permission denial Gate 4 halts the step on: thread 333's scoped re-run, R-1). ⛔ The helper and the new items are Python 3.9 code: no node type newer than 3.9's `ast`, a tuple in `isinstance`, never `A | B` in an annotation. ⛔ Test code runs under pytest inside `tests/` or not at all (bellows `CLAUDE.md`, *Test code*): no helper is called from `python -c`.
>
> **Scope:**
> - `tests/test_tools_safe_to_invoke.py`
> - `knowledge/mutants/def-time-union-nested.json`
> - `knowledge/mutants/def-time-union-nested.run.txt`
> - `knowledge/development/dev-log-def-time-union-nested-2026-09-15.md`
>
> **Item 1 — re-derive P1 and P3 and HALT on a mechanism mismatch** (a line-number drift is not one, and a count that moved is a record — paste it; a `_check_stmts` that already reads compound blocks or function bodies, a helper that names `ast.Match` or `ast.TryStar`, or 3.12's `ast` without either IS one). Paste each pin's re-derived line beside it.
> **Item 2 — the failing tests FIRST:** `_module`, t7 and t8 as *What this changes* 1, after t6; run the file on the unedited helper — `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest -q tests/test_tools_safe_to_invoke.py` — and paste the summary line: `14 failed, 10 passed`, t7's fourteen failing and t8's four with t1–t6 passing.
> **Item 3 — the edit** as *What this changes* 1 and 2, each manifest anchor matching the file once; the file green — predicted `24 passed`, t6 over the real tree among them — then `/usr/bin/python3 -m py_compile tests/test_tools_safe_to_invoke.py`, exit 0 (the Air's interpreter, 3.9.6: T-3) — then the FULL suite green: predicted `2395 passed, 2 skipped` on `65f713c` — P5's derived base and the eighteen cases — plus the tests of the plans merged before this one (the run supersedes the prediction; HALT only on a non-zero failure count). An existing test failing here is a HALT, never an edit.
> **Item 4 — first commit**, gated on the FULL suite AND the pre-check with the stage flag, path-scoped, run as ONE command — the verdict read checks each commit's place in the step's transcript: `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ -q && /Users/marklehn/Developer/bellows/.venv/bin/python tools/check_deposit.py /Users/marklehn/Developer/bellows/knowledge/decisions/in-progress-executable-<id>.md 1 --wt "$(git rev-parse --show-toplevel)" --expect-missing knowledge/development/dev-log-def-time-union-nested-2026-09-15.md knowledge/mutants/def-time-union-nested.run.txt && git add tests/test_tools_safe_to_invoke.py knowledge/mutants/def-time-union-nested.json && git commit -F - -- tests/test_tools_safe_to_invoke.py knowledge/mutants/def-time-union-nested.json <<'MSG'`, the message on the lines after it and `MSG` closing it — two files (the manifest rides this commit so the mutation run's `HEAD:` archive contains it); the message tagged with the plan id and `thread 314`.
> **Item 5 — the mutation run, REDIRECTED into `knowledge/mutants/def-time-union-nested.run.txt` (a Deposit):** `/Users/marklehn/Developer/bellows/.venv/bin/python tools/mutation_check.py knowledge/mutants/def-time-union-nested.json > knowledge/mutants/def-time-union-nested.run.txt 2>&1`; the last line must read `MUTATION: 8 killed, 0 survived, 0 error` — a survivor is a test to write, not a mutant to delete: the case, in t7 or t8, and the manifest when that mutant's `expect_fail` must name a new node — `tools/mutation_check.py` runs each mutant's `expect_fail` node alone, against the `HEAD:` archive, so a test the manifest does not name or the commit does not hold kills nothing — in ONE further commit, run as one command: `rm knowledge/mutants/def-time-union-nested.run.txt` first (a run file recording a survivor fails the pre-check's `mutation_result` gate, and a present path cannot be named), then the FULL suite AND the pre-check with `--expect-missing knowledge/development/dev-log-def-time-union-nested-2026-09-15.md knowledge/mutants/def-time-union-nested.run.txt`, then `git add` and `git commit`, path-scoped to the test file and the manifest — then the run again, which writes the run file anew, its `HEAD:` naming that commit.
> **Item 6 — the dev-log** `knowledge/development/dev-log-def-time-union-nested-2026-09-15.md` under the four headings declared below; `## Pins re-derived (P1)` opens with P1's value cell pasted verbatim, whole, to its last character — ⛔ the cell ends with the words `the file's last line` and its number, `:323`; paste through it, then stop. Under `## Failing-first (red, then green)` the red line and the three green lines (the file, the compile, the full suite); under `## The scopes observed (t7, t8)` the eighteen PASSED lines of a `-v` run over t7 and t8 — each case asserts one scope the helper reads or passes over, and nothing in this step prints them otherwise; under `## Mutation run` the run file's last line. **The last commit** (the second, or the third after a survivor fix), gated on the FULL suite and the pre-check bare (`… tools/check_deposit.py … 1 --wt "$(git rev-parse --show-toplevel)"`, no stage flag — the run file and the dev-log now exist), run as one command, path-scoped to the run file and the dev-log.
> **Headings:** `## Pins re-derived (P1)`; `## Failing-first (red, then green)`; `## The scopes observed (t7, t8)`; `## Mutation run`
> **Verbatim:** `## Pins re-derived (P1)` ← P1
>
> **Deposits:**
> - `knowledge/mutants/def-time-union-nested.json`
> - `knowledge/mutants/def-time-union-nested.run.txt`
> - `knowledge/development/dev-log-def-time-union-nested-2026-09-15.md`
>
> **Post-conditions:** the eighteen new cases green with t1–t6; the file compiling under `/usr/bin/python3` (3.9.6); the FULL suite green with no `failed`; the mutation run's last line as Item 5 states it; two DEV commits, or three after a survivor fix — the first carrying the test file and the manifest, the last the run file and the dev-log; the dev-log's four headings present as full lines with P1's cell whole; `git status --porcelain` empty after the last commit.

## STEP 2 — QA (full suite; the helper read through its tests; the receipt)

> ⛔ **Every item starts by re-establishing the root** — `cd "$(git rev-parse --show-toplevel)" && test -f tests/test_tools_safe_to_invoke.py && echo TREE_OK` — HALT unless TREE_OK. Interpreter ABSOLUTE; read-only beyond the two evidence files; the commit's message goes on stdin, as STEP 1's header states.
>
> **Item 1 — the full suite REDIRECTED not piped:** `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ --tb=short -q > knowledge/qa/evidence/def-time-union-nested-suite-2026-09-15.txt 2>&1`; the summary line quoted in the receipt as `N passed` with the skips named as `two skips (test_gate_watcher live-DB; test_fallback_live_wal_window version gate)` — never the word the Rule 20 block scans for.
> **Item 2 — the helper, read through its tests:** `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest -v tests/test_tools_safe_to_invoke.py::test_no_def_time_union_without_future_import tests/test_tools_safe_to_invoke.py::test_t6_reads_every_evaluated_scope tests/test_tools_safe_to_invoke.py::test_t6_passes_over_unevaluated_scopes`, and paste the nineteen PASSED lines — t6 over the real tree, t7's fourteen and t8's four. No call into the helper outside pytest.
> **Item 3 — production writes, stated exactly:** none outside the two evidence files; no lane file, no live lifecycle row, no daemon act.
> **Item 4 — receipt** `knowledge/qa/evidence/def-time-union-nested-qa-receipt-2026-09-15.md`: `numstat` over the DEV commits (`<base>..<dev>`, four files); the unchanged tests, checked — `git diff -U0 <base>..<dev> -- tests/test_tools_safe_to_invoke.py | grep -F '@@'` pasted, every hunk's base range inside `_check_stmts` and its call (:298–305) or an addition after the file's last line (:323) — a hunk elsewhere is an edit to a test MUST-PRESERVE freezes, and the step STOPS; a `## Verification` table with one row per Item 1–3, each quoting the line it rests on — ⛔ the status cell holds exactly one token (`✅`) and no positive row's text carries a hedging keyword; then RUN the canonical Rule 20 block (`/Users/marklehn/Developer/eluvian-governance/RULE_20_SELF_CHECK_BLOCK.md`) with `plan_slug: def-time-union-nested-2026-09-15`, `qa_report_path` and `evidence_dir` absolute under `$(git rev-parse --show-toplevel)/knowledge/qa/evidence/`, `required_evidence_files: ["def-time-union-nested-suite-2026-09-15.txt"]`, and APPEND its stdout — the banner `Rule 20 — QA Self-Check Results` and the `PASSED — SELF-CHECK PASSED` line are the block's output, never hand-authored; a `FAILED` stdout goes into the receipt and the step STOPS (thread 262).
> **Item 5 — commit**, path-scoped and gated, run as one command: `grep -Eq '^[0-9]+ passed' knowledge/qa/evidence/def-time-union-nested-suite-2026-09-15.txt && ! grep -Eq '[0-9]+ (failed|error)' knowledge/qa/evidence/def-time-union-nested-suite-2026-09-15.txt && /Users/marklehn/Developer/bellows/.venv/bin/python tools/check_deposit.py /Users/marklehn/Developer/bellows/knowledge/decisions/in-progress-executable-<id>.md 2 --wt "$(git rev-parse --show-toplevel)" && git add knowledge/qa/evidence/def-time-union-nested-qa-receipt-2026-09-15.md knowledge/qa/evidence/def-time-union-nested-suite-2026-09-15.txt && git commit -F - -- knowledge/qa/evidence/def-time-union-nested-qa-receipt-2026-09-15.md knowledge/qa/evidence/def-time-union-nested-suite-2026-09-15.txt <<'MSG'`, the message on the lines after it and `MSG` closing it. ⛔ A QA step that must change production code STOPS and requests a verdict (thread 262).
>
> **Deposits:**
> - `knowledge/qa/evidence/def-time-union-nested-qa-receipt-2026-09-15.md`
> - `knowledge/qa/evidence/def-time-union-nested-suite-2026-09-15.txt`
>
> **Scope:**
> - `knowledge/qa/evidence/def-time-union-nested-qa-receipt-2026-09-15.md`
> - `knowledge/qa/evidence/def-time-union-nested-suite-2026-09-15.txt`
>
> **Post-conditions:** the suite file's summary line is `N passed, 2 skipped` with N at least the DEV's count and no `failed`; Item 2's nineteen PASSED lines pasted; the receipt's `## Verification` table has three rows, and the receipt carries the block's stdout, its `PASSED — SELF-CHECK PASSED` line among it; one QA commit carrying the two evidence files.
