# bellows — THE DASHBOARD'S RELEASE KEY IS TESTED ON ITS POSITIVE PATH: `y` or `Y` in `confirm_release` runs the release once, on the plan the confirm named, and the footer names the file before the release runs — two test items beside #100093's cancel test, no code changed (thread 307)

**Date:** 2026-09-15 | **Project:** bellows | **Tier:** Small (two test items in one file, three cases; one mutation manifest; one dev-log) | **Dispatch Mode:** bellows | **Test Scope:** full-suite (the commit chain's gate; `pytest tests/ -q`) | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** after_qa_step | **known_failures:** 0 | **Discharges:** thread 307 | **cycle_tier:** T1

**auto_close:** false

**Post-close:** no daemon restart owed — only a test file and its records change, and no module the daemon or the dashboard loads changes. One bound follow-up, T-3's check — the CEO's act on the Air, where the Planner only reads: after the Air pulls, `cd ~/Developer/GitHub/bellows && .venv/bin/python -m pytest tests/test_dashboard.py::TestHandleKey -q` under its 3.9.6 venv — `4 passed`, the three new cases and t7 under the Air's interpreter (the file's PTY smoke test launches the dashboard, and the mini's whole-file count does not predict the Air's) — the Planner pasting the result into `tuyere.threads done 307 --commit bellows:<the DEV's first commit>`.

**Depends on:** thread 307 (filed 2026-09-12 09:55, found at #100093's verdict read, session d04ebd33); the release key as #100093 built it (`knowledge/decisions/Done/executable-100093.md`, thread 291, `9fca55c`) — `_handle_key`'s `confirm_release` branch, `_do_release` and `class_hold_rows` (P1) — and its seven tests, t7 among them, `TestHandleKey::test_confirm_cancels_and_l_needs_a_class_hold`, which presses `n` and `l` and never `y` (P2); #100093's manifest `knowledge/mutants/dashboard-release-key.json`, four mutants, its `confirm-release-y-check-removed` killed by t7 because a release on any key breaks the cancel (P3). The order: the reliability stretch; this plan writes `tests/test_dashboard.py` and its own manifest, run file and dev-log, which no plan held or drafting writes — thread 324's held plan reads `dashboard.py` (P5) — so it runs in any order beside them, held for the CEO's release as every bellows plan is; thread 292's hub, which the thread offered to fold this into, is not drafted, so this runs alone. Clone origin by kind: #100093 — the file's test shape (`CursesShell(bellows_root=tmp_path)` over a `config.json` of `{}`, `_make_state`, `patch.object` on the shell's `_do_release`); the plan's shape — DEV → QA, the commit chain, the mutation run, the Rule 20 block — from #100101 (Done 2026-09-14), the newest completed bellows plan.

**Tier computed (§1):** **T1** — T-3 fires: the test runs in the suite on both machines, the Air's venv 3.9.6 beside the mini's 3.12.14 (P5), where a construct newer than 3.9 would first fail. T-1 does not (one test file; the dashboard's code is unchanged); T-2 does not (every item patches `_do_release`, and no release runs); T-5 and T-6 do not (a test added and nothing deleted; no doctrine, gate or contract text changes); T-4 and T-7 do not; T-8 does not (a structure clone of #100093's t7, in its own class). #100093 was T1 on T-1, the write-bearing path it added; this plan adds that path's test.

## CEO Context

The dashboard's `l` key offers to release a class hold and `y` confirms it — the one key on the dashboard that changes anything. #100093's tests cover the cancel (`n` releases nothing) and the release command itself, but no test presses `y` and checks that the release runs, or that it runs on the plan the confirm named; a change that broke it — `y` doing nothing, or releasing a different hold — would pass the whole suite. This plan adds that test: `y` and `Y` each run the release once, on the named plan even when another hold is listed first, and the footer names the file before the release starts, since the release can take up to two minutes. Only a test file changes; nothing needs a restart. The class is shop-infra, so it holds for your release.

## What this changes

1. **`tests/test_dashboard.py`** (P2) — two items appended to `TestHandleKey`, after the file's last line (:863), in t7's shape:
   - (d1) `test_y_in_confirm_release_releases_the_target`, parametrized over `ord("y")` and `ord("Y")` with ids `y` and `Y`: the shell in `confirm_release` with `release_target` the row `hold-b.md`, and the state's deposit rows `[hold-a.md, hold-b.md]` — so the first class hold, `class_hold_rows` sorting by file (P1), is another row; `_do_release` patched: called once, with the target, and `_handle_key` returning `None`;
   - (d2) `test_release_draws_its_line_before_it_runs`: a `MagicMock` screen at 50 × 120 whose `addstr` and `refresh`, and the patched `_do_release`, each record one event — the events in the order `addstr`, `refresh`, `release`; the line at row 49, column 0, holding `Releasing hold-a.md`; the release on `hold-a.md`.
   - Green on the unedited code, by design: the code is right and the gap is its test. The mutation run (2) is what shows each item bites.
2. **`knowledge/mutants/dashboard-release-positive.json`** — `{"target": "dashboard.py", "mutants": [ … ]}`, each mutant's keys `name`, `why`, `anchor`, `replacement` and `expect_fail`; five, each `expect_fail` a class-qualified node id: (m1) the release call dropped → d1; (m2) the release of the first class hold the state lists, not the target → d1; (m3) `Y` ignored → d1; (m4) the release run before its line → d2; (m5) the screen guard dropped, so a key pressed without a screen draws on `None` → d1. None repeats #100093's four (P3). An anchor that matches its target other than once is the run's `ERROR` (`tools/mutation_check.py:266–270`).
3. **The dev-log** `knowledge/development/dev-log-dashboard-release-positive-2026-09-15.md`.
4. **Not changed:** `dashboard.py` and every other module; t1–t7, unedited — the two items sit after t7's last line.

## Why this exists

#100093's plan specified t7 as the cancel alone — `n` in `confirm_release` returns to `normal` and releases nothing, and `l` needs a class hold (its *What this changes* 2) — and its manifest's `confirm-release-y-check-removed` is killed by t7 only because a release on every key breaks the cancel. Nothing pins the confirm itself: a change that made `y` do nothing, release another row, or release before the footer names the file passes the suite. Thread 307, found at #100093's verdict read, names this the Planner's gap, not the DEV's. A break is fail-safe — nothing is released without `y` — but the release is the dashboard's one write-bearing act.

## What this does NOT do

- It does not change `dashboard.py` or any other module.
- It does not run a real release: every item patches `_do_release`, and the QA never presses the key on a live dashboard.
- It does not test `_do_release` itself, which t5 and t6 do, or the `l` branch, which t7 does.

## MUST-PRESERVE

- ⛔ **Every existing test passes unedited** — t1–t7 among them; the two items are appended after the file's last line.
- ⛔ **No item runs a release:** `_do_release` is patched in each, and no test or QA step runs `tools/clear_plan.py`.
- ⛔ **Every `expect_fail` is a class-qualified node id,** and the mutation run is redirected into its deposit, never piped.
- ⛔ **Test code runs under pytest inside `tests/` or not at all** (bellows `CLAUDE.md`, *Test code*; thread 313).
- ⛔ **The thread-262 stop:** a QA step that must change production code STOPS and requests a verdict.

## Numbers discipline — measured 2026-09-15 by the Planner (bellows main `3753152`; `dashboard.py` blob `5f9fdbee` and `tests/test_dashboard.py` blob `19a1da9e`, both as at `65f713c`)

| # | pin | value | how to re-derive |
|---|---|---|---|
| P1 | ⛔ the key | `dashboard.py`: `class_hold_rows` :108–113, sorted by `r["file"]` (:112); the shell's `mode` :417 and `release_target` :418; `_do_release` :526–555, which resets `release_target` and `mode` (:554–555); `_handle_key` :557; the `l` branch :564–568; the `confirm_release` branch :580–590 — `if key in (ord("y"), ord("Y")):` :581, `if stdscr is not None:` :582, the footer row :584, the `Releasing` line :585, `addstr` :586, `refresh` :587, `self._do_release(self.release_target)` :588; `return None` :591 | `sed -n '108,113p;526,591p' dashboard.py` |
| P2 | ⛔ the tests | `tests/test_dashboard.py`: 863 lines, 44 test functions; `_make_state` :27; `TestDoRelease` :803 — t5 :804, t6 :821; `TestHandleKey` :840, t7 :841–863, the file's last line :863 | `grep -n -E '^(class\|    def test_)' tests/test_dashboard.py`; `wc -l tests/test_dashboard.py` |
| P3 | the prior writers | `dashboard.py:557–591`, all 35 lines #100093's `9fca55c`; `tests/test_dashboard.py:836–863`, all 28 the same; #100093's manifest `knowledge/mutants/dashboard-release-key.json`: `class-hold-filter-dropped` → t1, `release-class-hold-arg-dropped` → t5, `nonzero-reported-as-success` → t6, `confirm-release-y-check-removed` → t7; its run `MUTATION: 4 killed, 0 survived, 0 error` | `git blame -L 557,591 dashboard.py`; the manifest |
| P4 | the prototype | a scratch clone of bellows at `65f713c` (`scratchpad/r307`, branch `r307`): `e3c849b2` the tests, `540d1d5f` the manifest, `7619b1ae` its run, `d033c640` the readable ids, `1c74f2b7` the run over them; `TestHandleKey` verbose — t7, d1`[y]`, d1`[Y]`, d2 — `4 passed`; the file `47 passed`; `MUTATION: 5 killed, 0 survived, 0 error`, `LIVE-TREE UNCHANGED`; `py_compile` rc 0 under 3.9.6; the full suite behind the fence, the base `65f713c` `53 failed, 2323 passed, 3 skipped` and the prototype `53 failed, 2326 passed, 3 skipped` — the three cases green, and the 53 failures the same node ids on both, none in `tests/test_dashboard.py`: the scratch environment's, none the change's | the register's walk 0 |
| P5 | class; in flight; interpreters; the suite | the writes → **shop-infra** (bellows, the project floor), HOLDS at admission for the CEO's release; in flight at drafting: nothing running (`status.py`: IN-FLIGHT none, AWAITING VERDICT none); held for release — threads 341's, 329's fix, 324's, 333's, 317's and 315's plans; drafting — threads 322's and 321's; none writes `dashboard.py` or `tests/test_dashboard.py`, and thread 324's held plan reads `dashboard.py`; the bellows venv 3.12.14, `/usr/bin/python3` 3.9.6, the Air's venv 3.9.6; the full suite at `65f713c`, derived and not run in a canonical-shaped tree: 2377 passed, 2 skipped (thread 329's fix plan, its P5) | `status.py`; `python -V`; the suite |

DEV re-derives P1 and P2 in Item 1 and HALTs on a mechanism mismatch; P3–P5 are the drafting record.

## Drafting Cycle

**Tier:** **T1** — T-3 fires. **Walk register:** /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-dashboard-release-positive-2026-09-15.md
**Walks:** walk 0 pinned (P1–P5 measured on bellows `3753152`, both files' blobs as at `65f713c`; the tests and the manifest prototyped in a scratch clone at `65f713c`; clone-diff against `Done/executable-100093.md`: FACTS, ARTEFACTS, STRUCTURE; no walk-0 scout — T1, the Planner's call); `fold_check --save-baseline` ARMED on v0 before any fold, re-saved after every intended edit; every lens commit through `/Users/marklehn/Developer/bellows/scripts/lens_commit.py`, invoked directly with its output whole — no filter between it and the screen — its exit read; no lens or walk number in any `--desc`, and no plain commit subject carrying a walk and a lens number; `lens_order_check` after every lens commit.

- Weak spots:          w1 dry
- Destruction:         w1 dry
- Vulnerabilities:     w1 dry
- Integration-record:  w1 dry
- ACID:                w1 dry
**Closing:** WARM close after walk 1 — BAR MET (T1), thread 307's plan. One walk, dry on all five lenses; no finding. Before the baseline, in v0: the fixture's target renamed `hold-b.md`, so a release of the first class hold cannot pass (the first name would have let m2 survive), the parametrize ids made readable, and the Air's check narrowed to `TestHandleKey` (the file's PTY smoke test launches the dashboard). T1, no panel. Every lens commit through `lens_commit.py`, its output whole and its exit read, the first walk's table header committed with v0 (thread 312); the close through `close_cycle.py`. Deposit via `ready-`; HOLDS on class shop-infra, the CEO releases (`clear_plan --release-class-hold`). Close acts: no restart — only a test file changes; Post-close's check on the Air after it pulls, `TestHandleKey`'s `4 passed`, the CEO's act, whose result the Planner pastes into `threads done 307`; no open fork.

## Cycle Manifest
tier: T1
target: tests/test_dashboard.py
class: shop-infra
reads: dashboard.py, tests/test_dashboard.py, knowledge/decisions/Done/executable-100093.md, knowledge/mutants/dashboard-release-key.json
writes: tests/test_dashboard.py, knowledge/mutants/dashboard-release-positive.json, knowledge/mutants/dashboard-release-positive.run.txt, knowledge/development/dev-log-dashboard-release-positive-2026-09-15.md, knowledge/qa/evidence/dashboard-release-positive-qa-receipt-2026-09-15.md, knowledge/qa/evidence/dashboard-release-positive-suite-2026-09-15.txt
mutants: knowledge/mutants/dashboard-release-positive.json
open_forks: none — a coverage plan: the code is unchanged, and the test pins what #100093 built
walks: 1
yields: 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=VACUOUS, propagation_check=DIVERGENT:22
coherence: 1/1 body walks named in the register (0 register rows; walk-token match, NOT row coverage)
fold_baseline: governance/knowledge/decisions/drafts/.executable-bellows-dashboard-release-positive.md.foldcheck.json

---

## STEP 1 — DEV (two test items, three cases; the mutation run; two commits)

> ⛔ **Every item starts by re-establishing the root** — `cd "$(git rev-parse --show-toplevel)" && test -f dashboard.py && echo TREE_OK` — HALT unless TREE_OK. ⛔ **The interpreter is `/Users/marklehn/Developer/bellows/.venv/bin/python`, ABSOLUTE.** ⛔ A commit's message goes to `git commit -F -` on stdin — a quoted heredoc ending the commit's own command: `<<'MSG'`, the message on the lines after it, `MSG` alone on the last — so no file is written for it (a Write-tool call inside `.git/` is refused as "a sensitive file", a permission denial Gate 4 halts the step on: thread 333's scoped re-run, R-1). ⛔ No item and no command in this step runs a release: `_do_release` is patched in each item, and `tools/clear_plan.py` is never run. ⛔ Test code runs under pytest inside `tests/` or not at all (bellows `CLAUDE.md`, *Test code*): no helper is called from `python -c`.
>
> **Scope:**
> - `tests/test_dashboard.py`
> - `knowledge/mutants/dashboard-release-positive.json`
> - `knowledge/mutants/dashboard-release-positive.run.txt`
> - `knowledge/development/dev-log-dashboard-release-positive-2026-09-15.md`
>
> **Item 1 — re-derive P1 and P2 and HALT on a mechanism mismatch** (a line-number drift is not one, and a count that moved is a record — paste it; a `confirm_release` branch that no longer calls `_do_release` with `self.release_target`, a `class_hold_rows` no longer sorted by file, or a test already pressing `y` in `confirm_release` IS one). Paste each pin's re-derived line beside it.
> **Item 2 — the items, on the unedited code:** d1 and d2 as *What this changes* 1, appended to `TestHandleKey` after the file's last line; run `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest -v tests/test_dashboard.py::TestHandleKey` and paste its four PASSED lines — t7, d1`[y]`, d1`[Y]`, d2 — and its summary, `4 passed`: green by design, the code being right and its test the gap; Item 5's mutation run is what shows each item bites.
> **Item 3 — the manifest and the checks:** the manifest as *What this changes* 2, each anchor matching `dashboard.py` once; the file green — `tests/test_dashboard.py`, predicted `47 passed` — then `/usr/bin/python3 -m py_compile tests/test_dashboard.py`, exit 0 (the Air's interpreter, 3.9.6: T-3) — then the FULL suite green: predicted `2380 passed, 2 skipped` on `65f713c` — P5's derived base and the three cases — plus the tests of the plans merged before this one (the run supersedes the prediction; HALT only on a non-zero failure count). An existing test failing here is a HALT, never an edit.
> **Item 4 — first commit**, gated on the FULL suite AND the pre-check with the stage flag, path-scoped, run as ONE command — the verdict read checks each commit's place in the step's transcript: `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ -q && /Users/marklehn/Developer/bellows/.venv/bin/python tools/check_deposit.py /Users/marklehn/Developer/bellows/knowledge/decisions/in-progress-executable-<id>.md 1 --wt "$(git rev-parse --show-toplevel)" --expect-missing knowledge/development/dev-log-dashboard-release-positive-2026-09-15.md knowledge/mutants/dashboard-release-positive.run.txt && git add tests/test_dashboard.py knowledge/mutants/dashboard-release-positive.json && git commit -F - -- tests/test_dashboard.py knowledge/mutants/dashboard-release-positive.json <<'MSG'`, the message on the lines after it and `MSG` closing it — two files (the manifest rides this commit so the mutation run's `HEAD:` archive contains it); the message tagged with the plan id and `thread 307`.
> **Item 5 — the mutation run, REDIRECTED into `knowledge/mutants/dashboard-release-positive.run.txt` (a Deposit):** `/Users/marklehn/Developer/bellows/.venv/bin/python tools/mutation_check.py knowledge/mutants/dashboard-release-positive.json > knowledge/mutants/dashboard-release-positive.run.txt 2>&1`; the last line must read `MUTATION: 5 killed, 0 survived, 0 error` — a survivor is a test to write, not a mutant to delete: the test, in `TestHandleKey` after the file's last line, and the manifest when that mutant's `expect_fail` must name a new node — `tools/mutation_check.py` runs each mutant's `expect_fail` node alone, against the `HEAD:` archive, so a test the manifest does not name or the commit does not hold kills nothing — in ONE further commit, run as one command: `rm knowledge/mutants/dashboard-release-positive.run.txt` first (a run file recording a survivor fails the pre-check's `mutation_result` gate, and a present path cannot be named), then the FULL suite AND the pre-check with `--expect-missing knowledge/development/dev-log-dashboard-release-positive-2026-09-15.md knowledge/mutants/dashboard-release-positive.run.txt`, then `git add` and `git commit`, path-scoped to the test file and the manifest — then the run again, which writes the run file anew, its `HEAD:` naming that commit.
> **Item 6 — the dev-log** `knowledge/development/dev-log-dashboard-release-positive-2026-09-15.md` under the four headings declared below; `## Pins re-derived (P1, P2)` opens with P1's value cell pasted verbatim, whole, to its last character — ⛔ the cell ends with `return None` and its line, `:591`; paste through it, then stop. Under `## Green on the unedited code` Item 2's four PASSED lines and its summary, then the three check lines (the file, the compile, the full suite); under `## The confirm observed (d1, d2)` the three PASSED lines of a `-v` run over d1 and d2 — each asserts a release that runs, on the named plan, after its line, and nothing in this step prints them otherwise; under `## Mutation run` the run file's last line. **The last commit** (the second, or the third after a survivor fix), gated on the FULL suite and the pre-check bare (`… tools/check_deposit.py … 1 --wt "$(git rev-parse --show-toplevel)"`, no stage flag — the run file and the dev-log now exist), run as one command, path-scoped to the run file and the dev-log.
> **Headings:** `## Pins re-derived (P1, P2)`; `## Green on the unedited code`; `## The confirm observed (d1, d2)`; `## Mutation run`
> **Verbatim:** `## Pins re-derived (P1, P2)` ← P1
>
> **Deposits:**
> - `knowledge/mutants/dashboard-release-positive.json`
> - `knowledge/mutants/dashboard-release-positive.run.txt`
> - `knowledge/development/dev-log-dashboard-release-positive-2026-09-15.md`
>
> **Post-conditions:** the three new cases green with the file's existing tests; the file compiling under `/usr/bin/python3` (3.9.6); the FULL suite green with no `failed`; the mutation run's last line as Item 5 states it; two DEV commits, or three after a survivor fix — the first carrying the test file and the manifest, the last the run file and the dev-log; the dev-log's four headings present as full lines with P1's cell whole; `git status --porcelain` empty after the last commit.

## STEP 2 — QA (full suite; the key read through its tests; the receipt)

> ⛔ **Every item starts by re-establishing the root** — `cd "$(git rev-parse --show-toplevel)" && test -f dashboard.py && echo TREE_OK` — HALT unless TREE_OK. Interpreter ABSOLUTE; read-only beyond the two evidence files; no release is run and the dashboard is not launched; the commit's message goes on stdin, as STEP 1's header states.
>
> **Item 1 — the full suite REDIRECTED not piped:** `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ --tb=short -q > knowledge/qa/evidence/dashboard-release-positive-suite-2026-09-15.txt 2>&1`; the summary line quoted in the receipt as `N passed` with the skips named as `two skips (test_gate_watcher live-DB; test_fallback_live_wal_window version gate)` — never the word the Rule 20 block scans for.
> **Item 2 — the key, read through its tests:** `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest -v tests/test_dashboard.py::TestHandleKey tests/test_dashboard.py::TestDoRelease`, and paste the six PASSED lines — t7, d1`[y]`, d1`[Y]`, d2, t5 and t6. No call into the dashboard outside pytest.
> **Item 3 — production writes, stated exactly:** none outside the two evidence files; no release, no lane file, no daemon act.
> **Item 4 — receipt** `knowledge/qa/evidence/dashboard-release-positive-qa-receipt-2026-09-15.md`: `numstat` over the DEV commits (`<base>..<dev>`, four files); the unchanged tests, checked — `git diff -U0 <base>..<dev> -- tests/test_dashboard.py | grep -F '@@'` pasted, every hunk adding lines and removing none (the two items after the file's last line) — a hunk that removes a line is an edit to a test MUST-PRESERVE freezes, and the step STOPS; a `## Verification` table with one row per Item 1–3, each quoting the line it rests on — ⛔ the status cell holds exactly one token (`✅`) and no positive row's text carries a hedging keyword; then RUN the canonical Rule 20 block (`/Users/marklehn/Developer/eluvian-governance/RULE_20_SELF_CHECK_BLOCK.md`) with `plan_slug: dashboard-release-positive-2026-09-15`, `qa_report_path` and `evidence_dir` absolute under `$(git rev-parse --show-toplevel)/knowledge/qa/evidence/`, `required_evidence_files: ["dashboard-release-positive-suite-2026-09-15.txt"]`, and APPEND its stdout — the banner `Rule 20 — QA Self-Check Results` and the `PASSED — SELF-CHECK PASSED` line are the block's output, never hand-authored; a `FAILED` stdout goes into the receipt and the step STOPS (thread 262).
> **Item 5 — commit**, path-scoped and gated, run as one command: `grep -Eq '^[0-9]+ passed' knowledge/qa/evidence/dashboard-release-positive-suite-2026-09-15.txt && ! grep -Eq '[0-9]+ (failed|error)' knowledge/qa/evidence/dashboard-release-positive-suite-2026-09-15.txt && /Users/marklehn/Developer/bellows/.venv/bin/python tools/check_deposit.py /Users/marklehn/Developer/bellows/knowledge/decisions/in-progress-executable-<id>.md 2 --wt "$(git rev-parse --show-toplevel)" && git add knowledge/qa/evidence/dashboard-release-positive-qa-receipt-2026-09-15.md knowledge/qa/evidence/dashboard-release-positive-suite-2026-09-15.txt && git commit -F - -- knowledge/qa/evidence/dashboard-release-positive-qa-receipt-2026-09-15.md knowledge/qa/evidence/dashboard-release-positive-suite-2026-09-15.txt <<'MSG'`, the message on the lines after it and `MSG` closing it. ⛔ A QA step that must change production code STOPS and requests a verdict (thread 262).
>
> **Deposits:**
> - `knowledge/qa/evidence/dashboard-release-positive-qa-receipt-2026-09-15.md`
> - `knowledge/qa/evidence/dashboard-release-positive-suite-2026-09-15.txt`
>
> **Scope:**
> - `knowledge/qa/evidence/dashboard-release-positive-qa-receipt-2026-09-15.md`
> - `knowledge/qa/evidence/dashboard-release-positive-suite-2026-09-15.txt`
>
> **Post-conditions:** the suite file's summary line is `N passed, 2 skipped` with N at least the DEV's count and no `failed`; Item 2's six PASSED lines pasted; the receipt's `## Verification` table has three rows, and the receipt carries the block's stdout, its `PASSED — SELF-CHECK PASSED` line among it; one QA commit carrying the two evidence files.
