# bellows — THE CENSUS TOOL PARSES UNDER PYTHON 3.9 AGAIN: the nested f-string at `tools/cycle_log_projection_census.py:192` becomes three plain lines (its dead `if False` branch dropped, its printed line unchanged), and a test parses every tool, script, daemon module and hook with the oldest interpreter the shop runs — `/usr/bin/python3`, 3.9.6 on both machines — so a construct only 3.12 accepts fails the suite on the mini before it reaches the Air (thread 304)

**Date:** 2026-09-11 | **Project:** bellows | **Tier:** Small (one expression in one tool, one test, one mutation manifest, one dev-log) | **Dispatch Mode:** bellows | **Test Scope:** full-suite (Rule 21 — `pytest tests/ -q`) | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** after_qa_step | **known_failures:** 0 | **Discharges:** thread 304 | **cycle_tier:** T0 (no trigger); integration-vs-record pass: no precedent conflict — thread 276 (2026-09-11, #100072's AST pass) first recorded this file's 3.9 parse failure; #100088 (merged tonight, thread 302) added tests that parse every tool, which on the Air's 3.9.6 venv now fail on this one file; MACHINE_SETUP §2's bootstrap uses `python3.12` where present and `python3` otherwise, so the machines do not share an interpreter; the fix changes one expression's syntax and not its value, and the new test names the interpreter it uses.

**auto_close:** false

**Post-close:** no restart (a command-line tool and a test; no daemon-loaded module changes). One Planner act after the merge, over the tailnet: pull on the Air and run `tests/test_tools_safe_to_invoke.py` under its 3.9.6 venv, the summary line pasted into `tuyere.threads done 304 --commit bellows:<the DEV commit that touched the tool>`. One CEO question carried, for MACHINE_SETUP §2: one interpreter on every machine (Python 3.12 installed on the Air) or a rule that bellows code targets 3.9 — the new test enforces the second until the first is ruled.

**Depends on:** thread 304 (the successor of 276, filed 2026-09-11 21:00) and bellows #100088 (Done 2026-09-11, thread 302). Clone origin: `Done/executable-100077.md` (a T0 from this morning: one small change, the test first, the two-commit DEV with the manifest riding the first commit, the mutation run, the full-suite QA) and `Done/executable-100088.md` (the test file this plan extends).

**Tier computed (§1):** **T0** — no trigger fires: a trivial localized change to one expression in one command-line tool, plus one test; no gate, no doctrine, no data.

## CEO Context

Tonight's tools plan added tests that parse every bellows tool with the suite's interpreter. On the mini that is Python 3.12, and every file parses. On the Air the bellows venv is Python 3.9.6, and one file does not: `tools/cycle_log_projection_census.py` has a nested f-string at line 192 that reuses quotes inside its expression, which only 3.12's parser accepts. So the Air's suite now fails four tests on one line of an old census instrument. Nothing breaks today — the Air runs no bellows lane until stage 3 — but the Air's daemon also runs under that 3.9.6 venv, so the same kind of construct in a daemon module would stop the Air's daemon outright, and nothing on the mini would notice. The fix rewrites the one expression so 3.9 parses it, with the same output, and adds a test that parses every tool, script, daemon module and hook with the machine's `/usr/bin/python3` (3.9.6 on both machines), so the next such construct fails on the mini first.

## What this changes

1. **`tools/cycle_log_projection_census.py`** — the one statement at :192 becomes three, with names that shadow no local of the enclosing function: the `missing` list read from `exp` into its own variable; the expected text computed as `'AGREEING'` when `exp['agree']` is true and otherwise as an f-string `"DIVERGING, missing {<that variable>}"` in double quotes; then `a(f"      expected       : {<the expected text>}")`. The fragment `exp[chr(34)+chr(34)] if False else` is dead — its condition is the constant `False` — and goes. The printed line is byte-identical for both values of `exp['agree']`; no other line of the file moves.
2. **`tests/test_tools_safe_to_invoke.py`** — (t5) `test_every_module_parses_under_python39`: `OLD = "/usr/bin/python3"`; the test skips, printing why, unless `OLD` exists and reports a version below (3, 12) (one subprocess, `-c "import sys; print(sys.version_info[:2])"`); then ONE subprocess of `OLD` runs a short `-c` script over every path of `_py_files()` plus `ROOT/*.py` and `ROOT/hooks/eluvian/*.py`, printing `<relative path>:<line>:<message>` for each `SyntaxError` that `ast.parse` raises and nothing else; the test asserts the output is empty, with the output as the failure message. Red before the fix: exactly one line, naming `tools/cycle_log_projection_census.py:192`. t1–t4 and `_py_files()` unchanged.
3. **`knowledge/mutants/census-tool-parses-under-39.json`** — `target` `tools/cycle_log_projection_census.py`, one mutant: (m1) the three lines restored to the original nested f-string → `tests/test_tools_safe_to_invoke.py::test_every_module_parses_under_python39`.
4. **Not changed:** the census logic; t1–t4; `_py_files()`; every other tool, script, module and hook.

## MUST-PRESERVE

- ⛔ **The printed line is unchanged.** The DEV evaluates the original expression and the new three lines on the two literal inputs `{'agree': True, 'missing': []}` and `{'agree': False, 'missing': [4, 6]}` under the venv, where both parse, and pastes the four strings: pairwise equal.
- ⛔ **t5 names its interpreter and never passes vacuously** — with no interpreter below 3.12 it skips with its reason, and on both shop machines it runs.
- ⛔ **Every `expect_fail` is a node id**, and the mutation run is redirected into its deposit, never piped.
- ⛔ **The thread-262 stop:** a QA step that must change production code STOPS and requests a verdict rather than committing.

## Numbers discipline — measured 2026-09-11 by the Planner (bellows `87f9a32`, governance `dc39c8bb`)

| # | pin | value | how to re-derive |
|---|---|---|---|
| P1 | ⛔ the line and its parse | `tools/cycle_log_projection_census.py:192` reads `a(f"      expected       : {'AGREEING' if exp['agree'] else f'DIVERGING, missing {exp[chr(34)+chr(34)] if False else exp['missing']}'}")`; under `/usr/bin/python3` (3.9.6) `ast.parse` of the file raises `SyntaxError: f-string: f-string: unmatched '['` at :192, and it is the only file among `tools/`, `scripts/` and the root modules that fails there (measured with `ast` alone at 20:55); the venv's 3.12.14 parses it (PEP 701) | `sed -n 192p tools/cycle_log_projection_census.py`; `/usr/bin/python3 -c "import ast; ast.parse(open('tools/cycle_log_projection_census.py').read())"` |
| P2 | ⛔ the Air | `~/Developer/GitHub/bellows/.venv/bin/python -V` → `Python 3.9.6` (the venv's `python` a symlink to `python3`); the same `ast.parse` raises there (measured over the tailnet at 20:59); the Air's daemon runs under that venv (pid 98765, HEAD `9e6ef650`); MACHINE_SETUP §2: `scripts/bootstrap.sh` creates `.venv` with `python3.12` where present, else `python3` | `ssh` to the Air: the same two commands under its venv |
| P3 | ⛔ the tests | `tests/test_tools_safe_to_invoke.py` (212 lines, bellows #100088): `_py_files()` :31–32 (`tools/*.py` then `scripts/*.py`); t1 `test_no_absolute_home_paths` :120 and t2 `test_no_import_time_writes` :129 call `ast.parse` under the suite's interpreter, and t3 :138 and t4 :177 reach it through `_static_ok` — so on a 3.9.6 venv all four fail on this one file | `grep -nE '^def ' tests/test_tools_safe_to_invoke.py` |
| P4 | ⛔ the mutation tool and the manifest form | `tools/mutation_check.py <manifest> [--repo-root] [--keep-sandbox] [--python] [--timeout]`; the manifest form `{"target", "mutants": [{"name", "why", "anchor", "replacement", "expect_fail"}]}` (`knowledge/mutants/debt-hook-unverified-header.json`, #100077); a clean run's last line `MUTATION: <n> killed, 0 survived, 0 error` | the file; `--help` |
| P5 | in-flight; class; interpreter | the plan for thread 299 holding for the CEO's release at drafting; the plans for thread 298 and thread 296 queued; this plan deposits after them; writes: the tool, the test file, the manifest, the run file, the dev-log, two QA evidence files → **shop-infra** (`_assign_class`) — HOLDS at admission, the CEO releases; the bellows venv, Python 3.12.14, and `/usr/bin/python3`, 3.9.6, for t5 | `.venv/bin/python status.py`; `_assign_class` |

## Drafting Cycle

**Tier:** T0 (no trigger) — the integration-vs-record pass only, per §1; no walk register.

**Integration-vs-record pass:** no precedent conflict — thread 276 recorded the parse failure on 2026-09-11 from #100072's AST pass; #100088's tests (thread 302) turned it into four failures on the Air's 3.9.6 venv, measured over the tailnet (P2); the change is one expression's syntax with its value proven unchanged, and the new test parses with a named interpreter instead of assuming one.

**Closing:** T0 floor — deposited after the pass; class shop-infra holds, the CEO releases.

## Cycle Manifest
tier: T0
target: tools/cycle_log_projection_census.py
class: shop-infra
reads: tools/cycle_log_projection_census.py, tests/test_tools_safe_to_invoke.py, tools/mutation_check.py, tools/check_deposit.py, knowledge/decisions/Done/executable-100077.md, knowledge/decisions/Done/executable-100088.md
writes: tools/cycle_log_projection_census.py, tests/test_tools_safe_to_invoke.py, knowledge/mutants/census-tool-parses-under-39.json, knowledge/mutants/census-tool-parses-under-39.run.txt, knowledge/development/dev-log-census-tool-parses-under-39-2026-09-11.md, knowledge/qa/evidence/census-tool-parses-under-39-qa-receipt-2026-09-11.md, knowledge/qa/evidence/census-tool-parses-under-39-suite-2026-09-11.txt
mutants: knowledge/mutants/census-tool-parses-under-39.json
open_forks: 1. one interpreter on every machine — Python 3.12 on the Air, a CEO act for MACHINE_SETUP §2 — or a rule that bellows code targets 3.9; 2. the hooks' interpreter named in MACHINE_SETUP (the harness runs them under the system `python3`)
walks: 0
yields: none
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=VACUOUS, propagation_check=DIVERGENT:31
coherence: T0 — the integration-vs-record pass recorded in the Drafting Cycle block; no register
fold_baseline: governance/knowledge/decisions/drafts/.executable-bellows-census-tool-parses-under-39.md.foldcheck.json

---

## STEP 1 — DEV (one expression, one test; the mutation run; two commits)

> ⛔ **Every item starts by re-establishing the root** — `cd "$(git rev-parse --show-toplevel)" && test -f gates.py && echo TREE_OK` — HALT unless TREE_OK. ⛔ **The interpreter is `/Users/marklehn/Developer/bellows/.venv/bin/python`, ABSOLUTE;** `/usr/bin/python3` is used only inside t5 and for Item 1's parse check. ⛔ Never run the daemon, `run_plan`, a claim, or the census tool itself; `T=$(mktemp -d /tmp/parse39.XXXXXX)` for scratch, removed at the end.
>
> **Scope:**
> - `tools/cycle_log_projection_census.py`
> - `tests/test_tools_safe_to_invoke.py`
> - `knowledge/mutants/census-tool-parses-under-39.json`
> - `knowledge/mutants/census-tool-parses-under-39.run.txt`
> - `knowledge/development/dev-log-census-tool-parses-under-39-2026-09-11.md`
>
> **Item 1 — re-derive P1 and P3 and HALT on a mechanism mismatch** (the file already parsing under `/usr/bin/python3`, or t1–t4 absent, IS one). Paste each pin's re-derived line beside it.
> **Item 2 — write the failing test FIRST:** t5 as *What this changes* 2. Run it; paste the red line and its one reported path.
> **Item 3 — the edit** as *What this changes* 1; then the MUST-PRESERVE equivalence check (the four strings, pasted); then t1–t5 green, then the FULL suite green (`N passed, 2 skipped` — `test_gate_watcher`'s live-DB skip and `test_fallback_live_wal_window`'s version gate).
> **Item 4 — first commit**, gated on the FULL suite AND the pre-check with the stage flag (#100067), path-scoped: `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ -q && /Users/marklehn/Developer/bellows/.venv/bin/python tools/check_deposit.py /Users/marklehn/Developer/bellows/knowledge/decisions/in-progress-executable-<id>.md 1 --wt "$(git rev-parse --show-toplevel)" --expect-missing knowledge/development/dev-log-census-tool-parses-under-39-2026-09-11.md knowledge/mutants/census-tool-parses-under-39.run.txt && git add tools/cycle_log_projection_census.py tests/test_tools_safe_to_invoke.py knowledge/mutants/census-tool-parses-under-39.json && git commit -F <msg-file> -- tools/cycle_log_projection_census.py tests/test_tools_safe_to_invoke.py knowledge/mutants/census-tool-parses-under-39.json` — three files; the message tagged with the plan id and `thread 304`.
> **Item 5 — the mutation run, REDIRECTED into `knowledge/mutants/census-tool-parses-under-39.run.txt` (a Deposit):** `/Users/marklehn/Developer/bellows/.venv/bin/python tools/mutation_check.py knowledge/mutants/census-tool-parses-under-39.json > knowledge/mutants/census-tool-parses-under-39.run.txt 2>&1`; the last line must read `MUTATION: 1 killed, 0 survived, 0 error`.
> **Item 6 — the dev-log** `knowledge/development/dev-log-census-tool-parses-under-39-2026-09-11.md` under the four headings declared below; `## Pins re-derived (P1, P3)` opens with P1's value cell pasted verbatim, whole, to its last character — ⛔ the cell ends with the words `parses it (PEP 701)`; paste through those words, then stop. Under `## Failing-first (red, then green)` the red line and the green line; under `## The line unchanged (both branches)` the four strings; under `## Mutation run` the run file's last line. **Second commit**, gated on the FULL suite and the pre-check bare, path-scoped to the run file and the dev-log. Last act: `[ -n "$T" ] && [ -d "$T" ] && rm -rf "$T"`.
> **Headings:** `## Pins re-derived (P1, P3)`; `## Failing-first (red, then green)`; `## The line unchanged (both branches)`; `## Mutation run`
> **Verbatim:** `## Pins re-derived (P1, P3)` ← P1
>
> **Deposits:**
> - `knowledge/mutants/census-tool-parses-under-39.json`
> - `knowledge/mutants/census-tool-parses-under-39.run.txt`
> - `knowledge/development/dev-log-census-tool-parses-under-39-2026-09-11.md`
>
> **Post-conditions:** t1–t5 green; the full suite `N passed, 2 skipped` with no `failed`; the mutation run's last line `MUTATION: 1 killed, 0 survived, 0 error`; two DEV commits; the dev-log's four headings present as full lines with P1's cell whole; `git status --porcelain` empty after the second commit.

## STEP 2 — QA (full suite; the thread's own check; the receipt)

> ⛔ **Every item starts by re-establishing the root** — `cd "$(git rev-parse --show-toplevel)" && test -f gates.py && echo TREE_OK` — HALT unless TREE_OK. Interpreter ABSOLUTE; read-only beyond the two evidence files; `T=$(mktemp -d /tmp/parse39-qa.XXXXXX)`.
>
> **Item 1 — the full suite REDIRECTED not piped:** `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ --tb=short -q > knowledge/qa/evidence/census-tool-parses-under-39-suite-2026-09-11.txt 2>&1`; the summary line quoted in the receipt as `N passed` with the skips named as `two skips (test_gate_watcher live-DB; test_fallback_live_wal_window version gate)` — never the word the Rule 20 block scans for.
> **Item 2 — the thread's own check:** `/usr/bin/python3 -c "import ast; ast.parse(open('tools/cycle_log_projection_census.py').read()); print('parses under', __import__('sys').version.split()[0])"` from this worktree's root — paste its one line.
> **Item 3 — production writes, stated exactly:** none outside the two evidence files; `$T` removed; no lane file, no lifecycle row, no daemon act.
> **Item 4 — receipt** `knowledge/qa/evidence/census-tool-parses-under-39-qa-receipt-2026-09-11.md`: `numstat` over the DEV commits (`<base>..<dev>`, five files); a `## Verification` table with one row per Item 1–3, each quoting the line it rests on — ⛔ the status cell holds exactly one token (`✅`) and no positive row's text carries a hedging keyword; then RUN the canonical Rule 20 block (`$ELUVIAN_WRAP_ROOT/RULE_20_SELF_CHECK_BLOCK.md`) with `plan_slug: census-tool-parses-under-39-2026-09-11`, `qa_report_path` and `evidence_dir` absolute under `$(git rev-parse --show-toplevel)/knowledge/qa/evidence/`, `required_evidence_files: ["census-tool-parses-under-39-suite-2026-09-11.txt"]`, and APPEND its stdout — the banner `Rule 20 — QA Self-Check Results` and the closing `PASSED — SELF-CHECK PASSED` line are the block's output, never hand-authored; a `FAILED` stdout goes into the receipt and the step STOPS (thread 262).
> **Item 5 — commit**, path-scoped and gated: `grep -Eq '^[0-9]+ passed' knowledge/qa/evidence/census-tool-parses-under-39-suite-2026-09-11.txt && ! grep -Eq '[0-9]+ (failed|error)' knowledge/qa/evidence/census-tool-parses-under-39-suite-2026-09-11.txt && /Users/marklehn/Developer/bellows/.venv/bin/python tools/check_deposit.py /Users/marklehn/Developer/bellows/knowledge/decisions/in-progress-executable-<id>.md 2 --wt "$(git rev-parse --show-toplevel)" && git add knowledge/qa/evidence/census-tool-parses-under-39-qa-receipt-2026-09-11.md knowledge/qa/evidence/census-tool-parses-under-39-suite-2026-09-11.txt && git commit -F <msg-file> -- knowledge/qa/evidence/census-tool-parses-under-39-qa-receipt-2026-09-11.md knowledge/qa/evidence/census-tool-parses-under-39-suite-2026-09-11.txt`. ⛔ A QA step that must change production code STOPS and requests a verdict (thread 262).
>
> **Deposits:**
> - `knowledge/qa/evidence/census-tool-parses-under-39-qa-receipt-2026-09-11.md`
> - `knowledge/qa/evidence/census-tool-parses-under-39-suite-2026-09-11.txt`
>
> **Scope:**
> - `knowledge/qa/evidence/census-tool-parses-under-39-qa-receipt-2026-09-11.md`
> - `knowledge/qa/evidence/census-tool-parses-under-39-suite-2026-09-11.txt`
>
> **Post-conditions:** the suite file's summary line is `N passed, 2 skipped` with N ≥ the DEV's count and no `failed`; Item 2's line reads `parses under 3.9.6`; the receipt's `## Verification` table has three rows and closes with the block's own PASSED line; one QA commit carrying the two evidence files.
