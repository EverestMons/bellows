# bellows — THE TWO CENSUS TOOLS IMPORT UNDER PYTHON 3.9 AGAIN: `from __future__ import annotations` in `tools/fold_signal_census.py` and `tools/gate_failopen_census.py`, and t6 fails any module that evaluates a PEP 604 union in an annotation at definition time without it (thread 305)

**Date:** 2026-09-12 | **Project:** bellows | **Tier:** Small (one import line in each of two tools, one test, one mutation manifest, one dev-log) | **Dispatch Mode:** bellows | **Test Scope:** full-suite (Rule 21 — `pytest tests/ -q`) | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** after_qa_step | **known_failures:** 0 | **Discharges:** thread 305 | **cycle_tier:** T1

**auto_close:** false

**Post-close:** no restart — two command-line tools and a test, and the daemon imports neither tool. One Planner act after the merge, over the tailnet: pull on the Air and run `tests/test_tools_safe_to_invoke.py` and the full suite under its 3.9.6 venv — the file reads six passed and the suite no failure — the summary lines pasted into `tuyere.threads done 305 --commit bellows:<the DEV commit that touched the tools>` (component `tools/`, which thread 308's refusal checks). The CEO's question for MACHINE_SETUP §2 stays carried: one interpreter on every machine, or 3.9 as the floor — t5 and t6 hold the floor until it is ruled.

**Depends on:** thread 305 (filed 2026-09-12 at #100092's verdict read: the Air's full suite read one failure, `test_help_does_no_work`, on these two tools) and bellows #100092 (thread 304, Done 2026-09-12: t5, the parse test this plan's t6 sits beside). Clone origin BY KIND: `Done/executable-100092.md` — the same test file, the same interpreter gap, the same two-commit DEV and full-suite QA.

**Tier computed (§1):** **T1** — T-3 fires (the fix is for an interpreter other than the one the suite runs here: the mini's venv is Python 3.12.14, where the defect cannot show, and the Air's venv is 3.9.6 — P2); T-8 fires in part (t6's detector is new logic, not a clone of t5's parse); T-1 does not (two one-line edits and one test); T-2, T-4, T-5 and T-6 do not.

## CEO Context

Two bellows tools crash when they load on Python 3.9, the Air's interpreter, so the Air's test suite has one failure. The fix is one line in each tool. The plan also adds a test that catches the same mistake in any bellows module on every machine, because the mini's own suite runs Python 3.12, where the mistake is invisible. The class is shop-infra, so it holds for your release.

## What this changes

1. **`tools/fold_signal_census.py` and `tools/gate_failopen_census.py`** each gain `from __future__ import annotations` as the first statement after the module docstring — the docstrings end at :41 and :20 (P1) — so their PEP 604 signature annotations (:145 and :510; :222) are no longer evaluated when the module loads. Nothing else in either file changes.
2. **`tests/test_tools_safe_to_invoke.py`** gains t6 `test_no_def_time_union_without_future_import` after t5, with a helper `_def_time_unions(path)`: over t5's files (`_py_files()`, the root `*.py`, `hooks/eluvian/*.py`) and the test files themselves (`tests/**/*.py` — the Air runs them under 3.9 too, so a union in a test's own signature would stop the whole file there), parse each module with the suite's own interpreter and report every `ast.BinOp` whose operator is `ast.BitOr` inside an annotation evaluated at definition time — a function's argument or return annotation, nested functions included, or a module- or class-level `AnnAssign` — in a module whose top level lacks `from __future__ import annotations`; the failure lists `file:line`. A function body's local `AnnAssign` is not evaluated and is not reported. No subprocess and no pytest skip: t6 runs the same on every machine. t6 and its helper are themselves Python 3.9 code — a tuple in `isinstance`, never `A | B`, and nothing newer than 3.9 — because the Air runs this file under 3.9.6 and nothing on the mini runs it there; the Post-close run on the Air is its check. A file that does not parse under the suite's interpreter is passed over, as `_abs_home_paths` and `_import_time_writes` already do — t5 and pytest's own collection report parse failures — so a deliberately unparseable fixture under `tests/` cannot error it; none exists today (P3).
3. **The mutation manifest `knowledge/mutants/def-time-union.json`** — `target` `tools/fold_signal_census.py`, one mutant: (m1) the future import removed → t6. t6's other branch, green on the fixed tree, is the suite itself.
4. **The dev-log** `knowledge/development/dev-log-def-time-union-2026-09-12.md`.

## Why this exists

#100092 (thread 304) made `tools/cycle_log_projection_census.py` parse under 3.9, and its post-close check on the Air found the next gap behind it: the Air's full suite read one failure, `test_help_does_no_work`, because `fold_signal_census.py` and `gate_failopen_census.py` annotate signatures with PEP 604 unions and Python 3.9 evaluates such annotations when a module loads (thread 305, with a one-line probe of the TypeError). t5 parses every module under 3.9, and these two pass it: a parse proves grammar, not import. The mini cannot see the defect at all — its suite runs 3.12 — so the fix needs a check that does not depend on the interpreter: t6 reads the annotations statically.

## What this does NOT do

- It does not change t1–t5 or any other test.
- It does not change either tool's behaviour — only when its annotations are evaluated.
- It does not check a runtime `isinstance` union — the walk-0 scan found none (P1) — or any other 3.10-only call, which no scan here looked for (the Air's full suite is the only check today), and it does not rule on one interpreter per machine (carried, MACHINE_SETUP §2).
- It does not restart anything.

## MUST-PRESERVE

- ⛔ **t1–t5 pass unchanged,** and the full suite stays green on the mini.
- ⛔ **Each tool's behaviour is unchanged** — `--help` prints the same usage line (P2), and the one import line is the only edit in each file.
- ⛔ **t6 runs on every machine** — no subprocess, no pytest skip, no dependence on `/usr/bin/python3`.
- ⛔ **The future import sits first after the docstring** — anywhere later is a SyntaxError.
- ⛔ **Every `expect_fail` is a test node id,** and the mutation run is redirected into its deposit, never piped.

## Numbers discipline — measured 2026-09-12 by the Planner (bellows `713b423`, governance `baaf1709`)

| # | pin | value | how to re-derive |
|---|---|---|---|
| P1 | ⛔ the lines | `tools/fold_signal_census.py` (858 lines, blob `df36d6b9`): the module docstring ends at :41, no `from __future__` import, a PEP 604 union in the return annotation of `extract_revision` at :145 (`Path` or `None`) and in the `max_pairs` parameter of `run_census` at :510 (`int` or `None`); `tools/gate_failopen_census.py` (309 lines, blob `ba27f0c3`): the docstring ends at :20, a union in the `module_filter` parameter of `run_census` at :222 (`str` or `None`); an AST scan of all 56 modules (the root, `tools/`, `scripts/`, `hooks/eluvian/`) finds definition-time unions without the future import in these two files only — `hooks/eluvian/wrap_check.py` carries five under the import — and no runtime isinstance union anywhere | `sed -n '41p;145p;510p' tools/fold_signal_census.py`; `sed -n '20p;222p' tools/gate_failopen_census.py`; the scan over `ast` |
| P2 | the proof on the target interpreter (Planner-measured over the tailnet and on the mini's `/usr/bin/python3`; the step does not re-derive the Air's half) | on the Air (bellows `0d0c1467`, venv Python 3.9.6): `tests/test_tools_safe_to_invoke.py` reads `1 failed, 4 passed`; a scratch archive with the future import inserted after each docstring reads `5 passed`, and both tools print their usage line; on the mini, the same fix in a scratch archive under `/usr/bin/python3` 3.9.6 prints `usage: fold_signal_census.py [-h] [--json] [--max-pairs MAX_PAIRS]` and `usage: gate_failopen_census.py [-h] [--verbose] [--module MODULE]` | the Air over ssh; `/usr/bin/python3 <tool> --help` in a scratch archive |
| P3 | ⛔ the test file and t6's prototype | `tests/test_tools_safe_to_invoke.py` (257 lines): `_py_files()` :33 (`tools/*.py` then `scripts/*.py`), t1 :122, t2 :131, t3 `test_help_does_no_work` :140, t4 :179, t5 `test_every_module_parses_under_python39` :219 (a subprocess under `/usr/bin/python3`, skipped when absent or 3.12 or later); a prototype of t6 appended in two scratch archives of `713b423` (walk 0, the lesson of 2026-09-10) — green on the fixed copy, red on the unfixed copy naming `tools/fold_signal_census.py:145`, `:510` and `tools/gate_failopen_census.py:222`; the whole suite under the change read `3 failed, 2311 passed, 2 skipped`, the three outside the change's files and each passing by node id in the canonical tree (`3 passed`), so the archive's location failed them, not the change — the prototype is evidence for this pin, never the DEV's source; the test files themselves (walk 1): all 102 — 101 `test_*.py` and one `conftest.py`, in `tests/` alone — parse under `/usr/bin/python3` 3.9.6, two carry the future import, and none has a definition-time union without it | the lines; the scratch runs |
| P4 | the mutation tool and the manifest form | `tools/mutation_check.py <manifest> [--repo-root] [--keep-sandbox] [--python] [--timeout]`; the form `{"target", "mutants": [{"name", "why", "anchor", "replacement", "expect_fail"}]}` (`knowledge/mutants/census-tool-parses-under-39.json`, #100092); a clean run's last line `MUTATION: <n> killed, 0 survived, 0 error` | the file; `--help` |
| P5 | class; in-flight; interpreter; suite | the writes → `_assign_class` → **shop-infra** (bellows) — HOLDS at admission, the CEO releases; in flight at drafting: tuyere #100094 (another repository); the bellows venv Python 3.12.14 and `/usr/bin/python3` 3.9.6; the full suite at `713b423`: `2313 passed, 2 skipped` (#100093's QA; `713b423` adds no test) | `status.py`; `_assign_class` |

DEV re-derives P1 and P3 in Item 1 — their lines and counts, and P1's scan over `ast` — and HALTs on a mechanism mismatch; P2, and P3's scratch runs and its parse under `/usr/bin/python3`, are the Planner's measurements, not re-derived by the step; P4 and P5 are the drafting record.

## Drafting Cycle

**Tier:** **T1** — T-3 fires; T-8 in part. **Walk register:** /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-def-time-union-2026-09-12.md
**Walks:** walk 0 pinned (P1–P5 measured on bellows `713b423`; clone-diff against `Done/executable-100092.md` run: FACTS, ARTEFACTS, STRUCTURE; the fix and t6 prototyped in scratch archives on the Air and the mini); `fold_check --save-baseline` ARMED on v0 before any fold; re-saved after every intended edit; every lens commit through `/Users/marklehn/Developer/bellows/scripts/lens_commit.py`; the tool run bare, its exit read; no lens or walk number in any `--desc`; `lens_order_check` after every lens commit, and before the receipt on a copy of the draft in a scratch project-shaped repository. Walk 1's table was opened by hand before its dry first lens, and the tool, reading that edit as the lens's record, wrote no dry line for it — entered late in a record commit (thread 312).

- Weak spots:          w1 dry; w2 dry; w3 3 folded — instruction 2 / record 1; w4 dry
- Destruction:          w1 dry; w2 dry; w3 dry; w4 dry
- Vulnerabilities:      w1 1 folded — instruction 1 / record 0; w2 1 folded — instruction 1 / record 0; w3 1 folded — instruction 1 / record 0; w4 dry
- Integration-record:   w1 dry; w2 dry; w3 1 folded — instruction 1 / record 0; w4 dry
- ACID:                 w1 dry; w2 dry; w3 dry; w4 dry
**Closing:** WARM close after walk 4 — BAR MET (T1), thread 305's plan. Four walks, findings by class — walk 1: 1 (instruction 1 / record 0), walk 2: 1 (instruction 1 / record 0), walk 3: 5 (instruction 4 / record 1), walk 4: 0; the manifest's `yields` counts the instruction class alone, 1, 1, 4, 0. Walk 1 widened t6 to the test files; walk 2 made t6 pass over a file that does not parse; walk 3 — its yield rising, continued under the CEO's under-seven-walks ruling after an execution pass rehearsed the DEV's whole path in a scratch repository (the stage-flag pre-check with 0 failures, the four-file commit, the mutation run at 1 killed, the bare pre-check with 0 failures, the two-file commit, an empty status) — named the counts Item 1 re-derives and the measurements it does not, stated the 3.10 scan's reach as measured (its one record-class finding), made t6's own code 3.9 code, and cut walk 2's one-off proof outside pytest, the tests-only rule now in the DEV preamble (the region trigger, t6 folded on three consecutive walks, answered by that cut); walk 4 dry across all five lenses. Dry pass: walk 4 meets §2's bar — instruction 0 / record 0. Origin (diagnostic): 2 of 7 fold-introduced. Walk 1's first dry line was entered late (thread 312).

## Cycle Manifest
tier: T1
target: tools/fold_signal_census.py
class: shop-infra
reads: tools/fold_signal_census.py, tools/gate_failopen_census.py, tests/test_tools_safe_to_invoke.py, tools/mutation_check.py, tools/check_deposit.py, knowledge/decisions/Done/executable-100092.md, knowledge/mutants/census-tool-parses-under-39.json
writes: tools/fold_signal_census.py, tools/gate_failopen_census.py, tests/test_tools_safe_to_invoke.py, knowledge/mutants/def-time-union.json, knowledge/mutants/def-time-union.run.txt, knowledge/development/dev-log-def-time-union-2026-09-12.md, knowledge/qa/evidence/def-time-union-qa-receipt-2026-09-12.md, knowledge/qa/evidence/def-time-union-suite-2026-09-12.txt
mutants: knowledge/mutants/def-time-union.json
open_forks: 1. one interpreter on every machine, or 3.9 as the floor (MACHINE_SETUP §2, the CEO's ruling); 2. a runtime check for other 3.10-only calls if the floor is kept — P1 scanned for runtime isinstance unions only (none); the Air's full suite is the only check today
walks: 4
yields: 1, 1, 4, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=VACUOUS, propagation_check=DIVERGENT:18
coherence: 4/4 body walks named in the register (7 register rows; walk-token match, NOT row coverage)
fold_baseline: governance/knowledge/decisions/drafts/.executable-bellows-def-time-union.md.foldcheck.json

---

## STEP 1 — DEV (two import lines, one test, the mutation run, two commits)

> ⛔ **Every item starts by re-establishing the root** — `cd "$(git rev-parse --show-toplevel)" && test -f gates.py && echo TREE_OK` — HALT unless TREE_OK. ⛔ **The interpreter is `/Users/marklehn/Developer/bellows/.venv/bin/python`, ABSOLUTE;** `/usr/bin/python3` is used only to run each tool's `--help`. ⛔ Never run the daemon, `run_plan`, a claim, or either tool's census — only `--help`, from `$T` with `HOME=$T`; `T=$(mktemp -d /tmp/def-time-union.XXXXXX)` for scratch, removed at the end. ⛔ Test code — t6 and its helper included — runs under pytest inside `tests/` or not at all (LESSONS 2026-09-09): no helper is called from `python -c`.
>
> **Scope:**
> - `tools/fold_signal_census.py`
> - `tools/gate_failopen_census.py`
> - `tests/test_tools_safe_to_invoke.py`
> - `knowledge/mutants/def-time-union.json`
> - `knowledge/mutants/def-time-union.run.txt`
> - `knowledge/development/dev-log-def-time-union-2026-09-12.md`
>
> **Item 1 — re-derive P1 and P3 and HALT on a mechanism mismatch** (a line-number drift is not one, and a line or file count that moved is a record — paste it; a future import already in either tool, a union gone from either signature, or t1–t5 absent IS one). Paste each pin's re-derived line beside it, then each tool's `--help` under `/usr/bin/python3`, from `$T` with `HOME=$T` — paste the last line of each (the TypeError).
> **Item 2 — write the failing test FIRST:** t6 as *What this changes* 2. Run the file; paste the red line and the three `file:line` entries it names.
> **Item 3 — the edits** as *What this changes* 1; then each tool's `--help` under `/usr/bin/python3` again (paste each usage line); the file green — an existing test failing here is a HALT, never an edit; then the FULL suite green — predicted 2313 + 1 = **2314 passed, 2 skipped** (the run supersedes the prediction; HALT only on a non-zero failure count).
> **Item 4 — first commit**, gated on the FULL suite AND the pre-check with the stage flag, path-scoped: `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ -q && /Users/marklehn/Developer/bellows/.venv/bin/python tools/check_deposit.py /Users/marklehn/Developer/bellows/knowledge/decisions/in-progress-executable-<id>.md 1 --wt "$(git rev-parse --show-toplevel)" --expect-missing knowledge/development/dev-log-def-time-union-2026-09-12.md knowledge/mutants/def-time-union.run.txt && git add tools/fold_signal_census.py tools/gate_failopen_census.py tests/test_tools_safe_to_invoke.py knowledge/mutants/def-time-union.json && git commit -F <msg-file> -- tools/fold_signal_census.py tools/gate_failopen_census.py tests/test_tools_safe_to_invoke.py knowledge/mutants/def-time-union.json` — four files (the manifest rides this commit so the mutation run's `HEAD:` archive contains it); the message tagged with the plan id and `thread 305`.
> **Item 5 — the mutation run, REDIRECTED into `knowledge/mutants/def-time-union.run.txt` (a Deposit):** `/Users/marklehn/Developer/bellows/.venv/bin/python tools/mutation_check.py knowledge/mutants/def-time-union.json > knowledge/mutants/def-time-union.run.txt 2>&1`; the last line must read `MUTATION: 1 killed, 0 survived, 0 error`.
> **Item 6 — the dev-log** `knowledge/development/dev-log-def-time-union-2026-09-12.md` under the four headings below; `## Pins re-derived (P1, P3)` opens with P1's value cell pasted verbatim, whole, to its last character — ⛔ the cell ends with the words `no runtime isinstance union anywhere`; paste through those words, then stop. Under `## Failing-first (red, then green)` the red line with its three entries and the green line; under `## Both tools under Python 3.9 (before and after)` the two TypeError lines and the two usage lines; under `## Mutation run` the run file's last line. **Second commit**, gated on the FULL suite and the pre-check bare (`… tools/check_deposit.py … 1 --wt "$(git rev-parse --show-toplevel)"`, no stage flag — the run file and the dev-log now exist), path-scoped to the run file and the dev-log. Last act: `[ -n "$T" ] && [ -d "$T" ] && rm -rf "$T"`.
> **Headings:** `## Pins re-derived (P1, P3)`; `## Failing-first (red, then green)`; `## Both tools under Python 3.9 (before and after)`; `## Mutation run`
> **Verbatim:** `## Pins re-derived (P1, P3)` ← P1
>
> **Deposits:**
> - `knowledge/mutants/def-time-union.json`
> - `knowledge/mutants/def-time-union.run.txt`
> - `knowledge/development/dev-log-def-time-union-2026-09-12.md`
>
> **Post-conditions:** t1–t6 green and the FULL suite green with no `failed`; the mutation run's last line as Item 5 states it; two DEV commits — the first carrying the four files, the second the run file and the dev-log; the dev-log's four headings present as full lines with P1's cell whole; `git status --porcelain` empty after the second commit.

## STEP 2 — QA (full suite; both tools under Python 3.9; the receipt)

> ⛔ **Every item starts by re-establishing the root** — `cd "$(git rev-parse --show-toplevel)" && test -f gates.py && echo TREE_OK` — HALT unless TREE_OK. Interpreter ABSOLUTE; read-only beyond the two evidence files; `T=$(mktemp -d /tmp/def-time-union-qa.XXXXXX)`.
>
> **Item 1 — the full suite REDIRECTED not piped:** `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ --tb=short -q > knowledge/qa/evidence/def-time-union-suite-2026-09-12.txt 2>&1`; the summary line quoted in the receipt as `N passed` with the skips named as `two skips (test_gate_watcher live-DB; test_fallback_live_wal_window version gate)` — never the word the Rule 20 block scans for.
> **Item 2 — the thread's own check:** each tool's `--help` under `/usr/bin/python3`, from `$T` with `HOME=$T` — paste the two usage lines; then t6 by node id under the venv — paste its PASSED line.
> **Item 3 — production writes, stated exactly:** none outside the two evidence files; `$T` removed; no lane file, no lifecycle row, no daemon act.
> **Item 4 — receipt** `knowledge/qa/evidence/def-time-union-qa-receipt-2026-09-12.md`: `numstat` over the DEV commits (`<base>..<dev>`, six files); a `## Verification` table with one row per Item 1–3, each quoting the line it rests on — ⛔ the status cell holds exactly one token (`✅`) and no positive row's text carries a hedging keyword; then RUN the canonical Rule 20 block (`/Users/marklehn/Developer/eluvian-governance/RULE_20_SELF_CHECK_BLOCK.md`) with `plan_slug: def-time-union-2026-09-12`, `qa_report_path` and `evidence_dir` absolute under `$(git rev-parse --show-toplevel)/knowledge/qa/evidence/`, `required_evidence_files: ["def-time-union-suite-2026-09-12.txt"]`, and APPEND its stdout — the banner `Rule 20 — QA Self-Check Results` and the closing `PASSED — SELF-CHECK PASSED` line are the block's output, never hand-authored; a `FAILED` stdout goes into the receipt and the step STOPS (thread 262).
> **Item 5 — commit**, path-scoped and gated: `grep -Eq '^[0-9]+ passed' knowledge/qa/evidence/def-time-union-suite-2026-09-12.txt && ! grep -Eq '[0-9]+ (failed|error)' knowledge/qa/evidence/def-time-union-suite-2026-09-12.txt && /Users/marklehn/Developer/bellows/.venv/bin/python tools/check_deposit.py /Users/marklehn/Developer/bellows/knowledge/decisions/in-progress-executable-<id>.md 2 --wt "$(git rev-parse --show-toplevel)" && git add knowledge/qa/evidence/def-time-union-qa-receipt-2026-09-12.md knowledge/qa/evidence/def-time-union-suite-2026-09-12.txt && git commit -F <msg-file> -- knowledge/qa/evidence/def-time-union-qa-receipt-2026-09-12.md knowledge/qa/evidence/def-time-union-suite-2026-09-12.txt`. ⛔ A QA step that must change production code STOPS and requests a verdict (thread 262).
>
> **Deposits:**
> - `knowledge/qa/evidence/def-time-union-qa-receipt-2026-09-12.md`
> - `knowledge/qa/evidence/def-time-union-suite-2026-09-12.txt`
>
> **Scope:**
> - `knowledge/qa/evidence/def-time-union-qa-receipt-2026-09-12.md`
> - `knowledge/qa/evidence/def-time-union-suite-2026-09-12.txt`
>
> **Post-conditions:** the suite file's summary line is `N passed, 2 skipped` with N at least the DEV's count and no `failed`; Item 2's two usage lines and t6's PASSED line pasted; the receipt's `## Verification` table has three rows and closes with the block's own PASSED line; one QA commit carrying the two evidence files.
