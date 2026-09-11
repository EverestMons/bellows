## Pins re-derived (P2, P3, P4)

P2 value cell (verbatim, to last character):

`tools/check_deposit.py` (206 lines, sha `ad6e7ed9972a`, last writer `b501482` #100060): `GATES` `:19–25` (five gate functions, a documentation tuple); `_make_parsed(deposits)` `:28–31` synthesises the receipt's `### Files Deposited` list; `main()` `:147–202`: argparse `plan_path`, `step`, `--wt`, `--base`, `--dependents` `:148–155`; `step_text = gates._extract_step_text` `:172`; `deposits = gates._extract_plan_required_deposits(step_text)` `:173`; the five gate calls `:180–190` each taking `plan_text`; `FAIL <gate>: <evidence>` lines `:197–198`; `PRECHECK: {n} failure(s) — {plan} step {s}` `:200`; `return 1 if failures else 0` `:202`

Mechanism verification — no mismatch detected:

P3 re-derived (gate functions, re-confirmed against the current file):
- `_gate_rule_22_verification` at `gates.py:801`: `:807` reads `_extract_plan_required_deposits(step_text)` from the **plan text** (not the receipt); `:809–815` (a) appends `Plan-declared deposit missing: <path>` per absent path, then returns.
- `_gate_mutation_result` at `gates.py:1284`: `:1297–1311` a manifest `.json` declared in Scope or Deposits without a `.run.txt` Deposit in the same step → FAIL *mutant manifest … declared without a .run.txt Deposit in this step* and return.
- `_gate_dev_log_declared_text` at `gates.py:1437`: reads the step's declared dev-log `.md` files for the declared headings and verbatim cells; FAIL rows at `:1480/1495/1505/1531`.
- The other two gates (`:1237` quoted nodes, `:1352` nodes-match-suite) do not read deposits that a first commit lacks.
- No gate signature change. No rule-22 (a) reading the receipt. Mutation gate manifest-without-run rule intact. No mechanism mismatch.

P4 re-derived (helpers and test count):
- `_make_plan(step_body, step)` `:23`, `_write_plan(tmp_path, step_body, step)` `:32`, `_run(plan_path, step, wt, capsys, extra=())` `:38`, `_git_init` `:44`, `_git_commit` `:53` — all signatures match P4.
- Count: 10 tests (t1–t10) before this plan's edit; P4 stated 11 (one class with two). The discrepancy is a count error in P4's record, not a mechanism mismatch — no helper signature changed, no gate logic changed, and the `_run` helper still calls `check_deposit.main(argv)` with `--wt`.

## Failing-first (three red, one pinned, then green)

Before the edit — t11, t12, t14 red (argparse rejects the unknown flag — `SystemExit: 2`, reported as FAILED); t13 GREEN (it pins today's reading — no `--expect-missing` flag, so argparse accepts the invocation):

```
FAILED tests/test_check_deposit.py::TestT11ExpectMissingFirstCommit::test_t11
FAILED tests/test_check_deposit.py::TestT12ExpectMissingGuard::test_t12
FAILED tests/test_check_deposit.py::TestT14ExpectMissingUndeclared::test_t14
3 failed, 11 passed in 2.03s
```

After the edit — 15 tests green (t1–t14 + t13 which was already green), 1 skipped (`test_gate_watcher`):

```
2212 passed, 1 skipped in 92.77s
```

## The tool's own first use (Item 4)

Subshell output from the first commit (shipped tool, before the flag was built — seven failures on the in-progress plan's step 1):

```
FAIL rule_22_verification: (a) Plan-declared deposit missing: knowledge/mutants/check-deposit-expect-missing.run.txt
FAIL rule_22_verification: (a) Plan-declared deposit missing: knowledge/development/dev-log-check-deposit-expect-missing-2026-09-10.md
FAIL dev_log_declared_text: declared heading not found in any deposit: ## Pins re-derived (P2, P3, P4)
FAIL dev_log_declared_text: declared heading not found in any deposit: ## Failing-first (three red, one pinned, then green)
FAIL dev_log_declared_text: declared heading not found in any deposit: ## The tool's own first use (Item 4)
FAIL dev_log_declared_text: declared heading not found in any deposit: ## Mutation run
FAIL dev_log_declared_text: heading missing: ## Pins re-derived (P2, P3, P4)
PRECHECK: 7 failure(s) — in-progress-executable-100067.md step 1
```

The just-built tool's own first use — flag passing the same commit the shipped tool could not:

```
PRECHECK: mutation_result N/A — run file expected missing (knowledge/mutants/check-deposit-expect-missing.run.txt)
PRECHECK: dev_log_declared_text N/A — dev-log expected missing (knowledge/development/dev-log-check-deposit-expect-missing-2026-09-10.md)
PRECHECK: 0 failure(s) — in-progress-executable-100067.md step 1 (expecting 2 missing)
rc=0
```

## Mutation run

```
LIVE-TREE UNCHANGED: tools/check_deposit.py sha256=a63be12182f8

MUTATION: 4 killed, 0 survived, 0 error
```

All four mutants killed: `skip-bullet-removal` (t11), `drop-mutation-gate-skip` (t11), `drop-present-path-guard` (t12), `drop-undeclared-path-guard` (t14).
