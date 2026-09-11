# bellows — NO TEST SPAWNS A REAL GATE WATCHER: an autouse fixture in `tests/conftest.py` stubs `deposit_receipt._spawn_watcher` for every test, `test_16` passes `spawn_watcher=False` explicitly, and one test proves the default path reaches the stub — the detached `gate_watcher.py diagnostic-holdfix.md` that every full-suite run left alive for two hours (thread 274)

**Date:** 2026-09-10 | **Project:** bellows | **Tier:** Small (one conftest fixture, one test edited and one added, one mutation manifest, one dev-log) | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** full-suite (Rule 21 — a conftest autouse fixture touches every test; `pytest tests/ -q`) | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** after_qa_step | **known_failures:** 0 | **Discharges:** thread 274

**auto_close:** false

**Post-close:** no restart (test files and a conftest; nothing daemon-loaded moves). No doctrine: bellows `CLAUDE.md`'s pytest-only rule already forbids test-shaped probes outside pytest — this plan makes pytest itself leave no process behind.

**Depends on:** thread 274 (2026-09-10, superseding 273 — the producer measured by reading the suite: `test_16_hold_prefix_receipt_satisfies_check`, not `test_11`); bellows #100060/#100062/#100063's QA and panel runs, which each left a live watcher (P1). Clone origin by kind: `Done/executable-100062.md` (the hook-family plan whose tests isolate the harness through by-path loading and fixtures — the isolation discipline); by layout: the closed 271 draft. In flight at drafting: #100068 (`scripts/lens_commit.py`, `tests/test_lens_commit.py`) and #100069 (`scripts/close_cycle.py`, `tests/test_close_cycle.py`) — no W-W with `tests/conftest.py` or `tests/test_depositor_receipts.py`.

**Tier computed (§1):** **T1** — T-1 fires (two test-side files); T-6 does NOT fire — no tool, gate or doctrine changes: `tools/deposit_receipt.py` is READ, not edited; T-2 does not.

## CEO Context

Every full run of the bellows suite on 2026-09-10 left a real process behind: `tools/gate_watcher.py diagnostic-holdfix.md`, detached (`start_new_session=True`), sleeping fifteen seconds at a time for its 120-minute default timeout, logging under whatever tree it was spawned from — four were alive at once during the 270 cycle's panel, each from a scratch archive's pytest run, and the cold seats counted them (D8, C11). The seats attributed the spawn to `test_11_gate_watcher` by its name; reading the suite says otherwise: that test loads the watcher module by path and patches a pager. The producer is `tests/test_depositor_receipts.py::TestHoldSlugFix::test_16_hold_prefix_receipt_satisfies_check` (`:627`), which calls `tools.deposit_receipt.write_receipt(hold_path, "test-session-16")` — and `write_receipt`'s `spawn_watcher` parameter defaults to `True` (P2), so the real `_spawn_watcher` runs `subprocess.Popen` on the real `gate_watcher.py`. A reporter, never a writer, and it exits on its own — but a suite that leaves a live process is not isolated, the CLI already has the seam (`--no-spawn`), and the class is one default away from recurring in any future test that writes a receipt. This plan closes it at the suite's root: an autouse fixture stubs the spawn for every test, the one test that reaches it today opts out explicitly as well, and a new test proves that the DEFAULT path lands on the stub under pytest.

## What this changes

1. **`tests/conftest.py`** — one autouse fixture beside the four that exist (`isolate_verdicts_dir` `:17`, `isolate_runner_logs_dir` `:24`, `isolate_lifecycle_db` `:30`, `_clear_notifier_dedupe` `:39`, P3), in their shape: `@pytest.fixture(autouse=True) def isolate_watcher_spawn(monkeypatch)` — imports `tools.deposit_receipt as _dr` and sets `_dr._SPAWN_CALLS = []` on the tool module (`monkeypatch.setattr(_dr, "_SPAWN_CALLS", [], raising=False)` — the list lives on the module the test reads, so a test never imports `conftest` by name and never REQUESTS the fixture) and monkeypatches `_dr._spawn_watcher` to a recording stub named `_stub_spawn_watcher` that appends its `claimable_name` argument to that list and returns `-1` (a pid-shaped sentinel no live process carries); yields nothing. Every test that reaches `write_receipt`'s default now records a call and spawns nothing.
2. **`tests/test_depositor_receipts.py`** — (a) `test_16` (`:627–668`) passes `spawn_watcher=False` to `write_receipt` (the CLI's `--no-spawn` value, P2) — explicit at the one site that reaches the default today, so the test reads correctly on its own; (b) a new test **t24** `test_24_default_spawn_reaches_the_stub`: calls `dr.write_receipt(<a staged hold- path>, "test-session-24")` with NO `spawn_watcher` argument (the default), in this ORDER: first `assert dr._spawn_watcher.__name__ == "_stub_spawn_watcher"` (the guard that the fixture is in force — it runs BEFORE any call that could spawn, so the `autouse` mutant fails here and spawns nothing), then the `write_receipt` call with the default, then `assert dr._SPAWN_CALLS == ["<the staged plan's claimable name>"]` (one recorded name, the plan's). Measured through the stub, never through `ps`. The 23 existing tests stay green (t16 with its explicit `False`; the others never call `write_receipt`).
3. **`knowledge/mutants/no-test-spawns-a-watcher.json`** — at least two mutants (`target: tests/conftest.py` for the first, `tests/test_depositor_receipts.py` for the second; every `expect_fail` a class-qualified node id where the test is a method — t16 and t24 sit on `TestHoldSlugFix` and a new `TestNoSpawn` class, P3): the fixture's `autouse=True` removed (t24 — the default then reaches the real `_spawn_watcher`, `SPAWN_CALLS` stays empty and the `__name__` assert fails; the mutant is killed WITHOUT spawning a real watcher only if t24's first assertion runs before any real spawn could matter — so t24 asserts `__name__` FIRST, then calls `write_receipt`); t16's `spawn_watcher=False` reverted to the default (t16's last assertion, added by this plan: `assert dr._SPAWN_CALLS == []` — the reverted default records one call and fails).
4. **Not changed:** `tools/deposit_receipt.py` (its default stays `True` — the CLI and the Planner's real deposits keep spawning the watcher they rely on), `tools/gate_watcher.py`, every other test. The diff touches two files plus the manifest, the run file and the dev-log.

## Why this exists

A test that leaves a process alive is measured only by whoever counts processes afterwards; three cold seats did, and the count grew by one per suite run. The seam exists in the tool (`spawn_watcher=False`, `--no-spawn`); the suite's root is where the default is made safe for every test at once, and the explicit `False` at the one live site keeps that test honest when read alone.

## What this does NOT do

- Does not change the tool's default or the real deposit path — a Planner's `deposit_receipt.py` still arms a watcher.
- Does not kill the watchers alive today (they exit on their timeout; none writes).
- Does not touch `gate_watcher.py`'s own exit rules (a watcher whose plan name never appears could exit earlier — thread 274's last sentence, its own plan if ever measured as a cost).

## MUST-PRESERVE

- ⛔ **The stub is autouse and reached by the default.** t24 proves the path; the `__name__` assertion runs before the call.
- ⛔ **The tool is read, not edited.** `deposit_receipt.py` and `gate_watcher.py` stay byte-identical (`git diff --stat` names neither).
- ⛔ **Suite green at both commits;** nothing outside the two files moves.

## Numbers discipline — measured 2026-09-10 by the Planner (bellows `ba74706`, governance `88f42fa6`)

| # | pin | value | how to re-derive |
|---|---|---|---|
| P1 | ⛔ the measured producer | `tests/test_depositor_receipts.py:627` `test_16_hold_prefix_receipt_satisfies_check` (class `TestHoldSlugFix`, `:626`): stages `diagnostic-holdfix`, evaluates it to a hold, then `result = dr.write_receipt(hold_path, "test-session-16")` (`:653`-ish, inside a `try` that swaps `dr._RECEIPTS_DIR`) — no `spawn_watcher` argument; `test_11_gate_watcher` (`tests/test_notifier_coverage.py:632`) loads `gate_watcher.py` by path and patches `notifier.notify_verdict_request` — it spawns nothing (the seats' attribution corrected by thread 274); the live processes on 2026-09-10: `gate_watcher.py diagnostic-holdfix.md` ×3 across the day (pids 37972, 69036, 75677), each from a scratch archive's suite run, 120-minute timeout | `grep -n 'write_receipt(' tests/*.py`; `ps -eo pid,etime,command \| grep -F gate_watcher` after a suite run |
| P2 | ⛔ the tool's seam | `tools/deposit_receipt.py:55–66` `_spawn_watcher(claimable_name)` → `subprocess.Popen([sys.executable, watcher, claimable_name], stdout=DEVNULL, stderr=DEVNULL, start_new_session=True)`, returns the pid or `None`; `:69` `def write_receipt(plan_path, session_id, spawn_watcher=True)`; `:118–119` `if spawn_watcher: pid = _spawn_watcher(slug + ".md")`; the CLI `:148–152` `--no-spawn` → `spawn_watcher=not args.no_spawn`; `tools/gate_watcher.py:153–154` `--timeout-min` default 120, `--interval-sec` 15 | `sed -n '55,69p;118,119p;148,152p' tools/deposit_receipt.py` |
| P3 | ⛔ the tests as they stand | `tests/conftest.py` (sha `6e7a5f1c08f3`): four autouse fixtures — `isolate_verdicts_dir` `:17`, `isolate_runner_logs_dir` `:24`, `isolate_lifecycle_db` `:30`, `_clear_notifier_dedupe` `:39` — each a `monkeypatch.setattr` on a module constant; `tests/test_depositor_receipts.py` (sha `8601a54bc640`, last writer `6f9faea` #100037): 23 tests on classes, helpers `_write_receipt` `:107` (writes the JSON itself — no spawn), `_write_receipt_for_plan` `:121`, `_stage_plan`, `_make_depositor`; `tests/test_depositor.py`'s `_write_receipt_for_plan` `:34` likewise writes JSON directly | `grep -n 'autouse\|^def ' tests/conftest.py`; `grep -n 'def test_\|def _\|^class' tests/test_depositor_receipts.py` |
| P4 | the mutation contract; class; in-flight | `tools/mutation_check.py`: manifest-driven, KILLED = exit 1 only, sandbox = `git archive HEAD`, per-mutant `target`; run file `knowledge/mutants/<slug>.run.txt` ending `MUTATION: N killed, 0 survived, 0 error`; this plan writes `tests/` only → **shop-infra** (bellows is an infra project: the class assigner's floor names the project, not the path — HOLDS, the CEO releases); in flight: #100068, #100069 on `scripts/` and their own test files | `python3 status.py` |

## Drafting Cycle

**Tier:** **T1** — T-1 fires. **Walk register:** /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-no-test-spawns-a-watcher-2026-09-10.md
**Walks:** walk 0 pinned (P1–P4 measured on bellows `ba74706`; clone-diff against `Done/executable-100062.md` (kind) and the closed 271 draft (layout) run: FACTS, ARTEFACTS, STRUCTURE); `fold_check --save-baseline` ARMED on v0 before any fold; re-saved after every intended edit; every lens commit through `scripts/lens_commit.py`; the tool run bare, its exit read; no lens or walk number in any `--desc`.

- Weak spots:          w1 4 folded — instruction 3 / record 1 (the call list on the tool module, not conftest; t24's assertion order; QA Item 2 rewritten as a pid census; the red reasons); w2 dry

- Destruction:         w1 dry — recorded: no test calls `_spawn_watcher` directly or asserts a real spawn (P3: only t16 reaches it, through the default); the tool's default and the real deposit path are untouched; w2 dry

- Vulnerabilities:       w1 dry; w2 dry

- Integration-record:    w1 dry; w2 dry

- ACID:                  w1 dry; w2 dry

**Closing:** WARM close after walk 2 — BAR MET (T1), thread 274's plan (superseding 273). Two walks: 4 → 0. Every lens commit through `lens_commit.py`, the tool run bare, its exit read; `walks:` by hand for the last time before #100069 ships. Deposit via `ready-`; HOLDS on class shop-infra, released on the CEO's behalf under the 2026-09-10 delegation.

## Cycle Manifest
tier: T1
target: tests/conftest.py
class: shop-infra
reads: tests/conftest.py, tests/test_depositor_receipts.py, tests/test_notifier_coverage.py, tools/deposit_receipt.py, tools/gate_watcher.py, tools/mutation_check.py, knowledge/decisions/Done/executable-100062.md
writes: tests/conftest.py, tests/test_depositor_receipts.py, knowledge/mutants/no-test-spawns-a-watcher.json, knowledge/mutants/no-test-spawns-a-watcher.run.txt, knowledge/development/dev-log-no-test-spawns-a-watcher-2026-09-10.md, knowledge/qa/evidence/no-test-spawns-a-watcher-qa-receipt-2026-09-10.md, knowledge/qa/evidence/no-test-spawns-a-watcher-suite-2026-09-10.txt
mutants: knowledge/mutants/no-test-spawns-a-watcher.json
open_forks: 1. `gate_watcher.py` exiting early when its plan name never appears within N ticks (thread 274's last sentence) — after one measured cost; 2. a suite-level guard that fails the run when a child process outlives pytest (a `ps` census in a session-scoped fixture) — after a second producer is measured
walks: 2
yields: 3, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=VACUOUS, propagation_check=DIVERGENT:5
coherence: 2/2 body walks named in the register (5 register rows; walk-token match, NOT row coverage)
fold_baseline: governance/knowledge/decisions/drafts/.executable-bellows-no-test-spawns-a-watcher.md.foldcheck.json

---

## STEP 1 — DEV (one fixture, one test edited, one added; the mutation run; two commits)

> ⛔ **Every item starts by re-establishing the root** — `cd "$(git rev-parse --show-toplevel)" && test -f gates.py && echo TREE_OK` — HALT unless TREE_OK. ⛔ **The interpreter is `/Users/marklehn/Developer/bellows/.venv/bin/python`, ABSOLUTE.** ⛔ Never run the daemon, `run_plan`, a claim; never import `lifecycle` outside pytest. ⛔ Every deposit is written in THIS worktree (`"$(git rev-parse --show-toplevel)"`), never in the canonical checkout; the plan's own lane file lives in the canonical checkout at `/Users/marklehn/Developer/bellows/knowledge/decisions/in-progress-executable-<id>.md` (`<id>` from the prompt). ⛔ Before this plan's tests are written, ONE suite run spawns a watcher (P1) — record its pid from `ps` after Item 1's run and say so; do not kill it (it exits on its timeout).
>
> **Scope:**
> - `tests/conftest.py`
> - `tests/test_depositor_receipts.py`
> - `knowledge/mutants/no-test-spawns-a-watcher.json`
> - `knowledge/mutants/no-test-spawns-a-watcher.run.txt`
> - `knowledge/development/dev-log-no-test-spawns-a-watcher-2026-09-10.md`
>
> **Item 1 — re-derive P1, P2 and P3 and HALT on a mechanism mismatch** (P4 is a record; a line-number drift is not a mismatch, a `spawn_watcher` default other than `True`, a test other than t16 calling `write_receipt` with the default, or a conftest without the four fixtures is). Paste `write_receipt`'s signature, `_spawn_watcher`, t16's call line, and the fixture names under the first declared heading. Then measure P1 live: `ps -eo pid,etime,command | grep -F gate_watcher | grep -v grep` before and after `pytest tests/test_depositor_receipts.py -q -k test_16` — one new `gate_watcher.py diagnostic-holdfix.md` line after; paste both listings.
> **Item 2 — write the failing tests FIRST:** *What this changes* 2 — t24 and t16's last assertion. Run the file: t24 red at its first assertion (the real function's `__name__` is `_spawn_watcher`), t16 red on its new assertion (`AttributeError`: the module has no `_SPAWN_CALLS`); t1–t23 otherwise green. Paste under the second declared heading.
> **Item 3 — the edits** as *What this changes* 1–2; then the file green (24 tests), then the FULL suite green (`N passed, 1 skipped` — `test_gate_watcher` skips in a worktree; a skip is not a failure) — and `ps` after that full run shows NO new `gate_watcher.py` process (paste the listing: the pre-existing ones from Item 1 and this session's real deposits only).
> **Item 4 — first commit**, gated on the FULL suite AND the pre-check with the stage flag (#100067), path-scoped: `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ -q && /Users/marklehn/Developer/bellows/.venv/bin/python tools/check_deposit.py /Users/marklehn/Developer/bellows/knowledge/decisions/in-progress-executable-<id>.md 1 --wt "$(git rev-parse --show-toplevel)" --expect-missing knowledge/development/dev-log-no-test-spawns-a-watcher-2026-09-10.md knowledge/mutants/no-test-spawns-a-watcher.run.txt && git add tests/conftest.py tests/test_depositor_receipts.py knowledge/mutants/no-test-spawns-a-watcher.json && git commit -F <msg-file> -- tests/conftest.py tests/test_depositor_receipts.py knowledge/mutants/no-test-spawns-a-watcher.json` — three files (the manifest rides this commit so the mutation run's `HEAD:` archive contains it); the message tagged with the plan id and `thread 274`; the paste MUST contain `PRECHECK: 0 failure(s) — … (expecting 2 missing)`.
> **Item 5 — the mutation run, REDIRECTED into `knowledge/mutants/no-test-spawns-a-watcher.run.txt` (a Deposit):** `/Users/marklehn/Developer/bellows/.venv/bin/python tools/mutation_check.py knowledge/mutants/no-test-spawns-a-watcher.json > knowledge/mutants/no-test-spawns-a-watcher.run.txt 2>&1`; the last line must read `MUTATION: <n> killed, 0 survived, 0 error` with n ≥ 2 — a survivor is a test to write, not a mutant to delete. ⛔ The `autouse` mutant runs t24 with the real spawn reachable: t24's `__name__` assertion fires FIRST and fails before `write_receipt` is called, so the mutant spawns nothing — confirm with `ps` after the run and paste it.
> **Item 6 — the dev-log** `knowledge/development/dev-log-no-test-spawns-a-watcher-2026-09-10.md` under the four headings declared below; `## Pins re-derived (P1, P2, P3)` opens with P2's value cell pasted verbatim, whole, to its last character — ⛔ the VALUE cell (third column) ends with the words `` `--interval-sec` 15 ``; paste through those words, then stop. **Second commit**, gated on the FULL suite AND the run file AND the pre-check run BARE, path-scoped: `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ -q && grep -Eq 'MUTATION: ([2-9]|[1-9][0-9]+) killed, 0 survived, 0 error' knowledge/mutants/no-test-spawns-a-watcher.run.txt && /Users/marklehn/Developer/bellows/.venv/bin/python tools/check_deposit.py /Users/marklehn/Developer/bellows/knowledge/decisions/in-progress-executable-<id>.md 1 --wt "$(git rev-parse --show-toplevel)" && git add knowledge/mutants/no-test-spawns-a-watcher.run.txt knowledge/development/dev-log-no-test-spawns-a-watcher-2026-09-10.md && git commit -F <msg-file> -- knowledge/mutants/no-test-spawns-a-watcher.run.txt knowledge/development/dev-log-no-test-spawns-a-watcher-2026-09-10.md` — two files.
> **Headings:** `## Pins re-derived (P1, P2, P3)`; `## Failing-first (two red, then green)`; `## The watcher census (Items 1, 3, 5)`; `## Mutation run`
> **Verbatim:** `## Pins re-derived (P1, P2, P3)` ← P2
>
> **Deposits:**
> - `tests/conftest.py`
> - `tests/test_depositor_receipts.py`
> - `knowledge/mutants/no-test-spawns-a-watcher.json`
> - `knowledge/mutants/no-test-spawns-a-watcher.run.txt`
> - `knowledge/development/dev-log-no-test-spawns-a-watcher-2026-09-10.md`
>
> **Post-conditions:** t24 green, t16 green with its added assertion, the other 22 green; the full suite spawns no watcher (Item 3's `ps` listing); the mutation run's last line `n ≥ 2 killed, 0 survived, 0 error`; `git diff --stat main...HEAD` (three-dot) names exactly the five Scope files; the four declared headings present with P2's cell whole; `tools/deposit_receipt.py` and `tools/gate_watcher.py` unchanged.

## STEP 2 — QA (full suite with a process census before and after)

> ⛔ **Every item starts by re-establishing the root** — `cd "$(git rev-parse --show-toplevel)" && test -f gates.py && echo TREE_OK` — HALT unless TREE_OK. Interpreter ABSOLUTE; read-only beyond the two evidence files.
>
> **Item 1 — the census, then the full suite REDIRECTED not piped, then the census:** `ps -eo pid,etime,command | grep -F gate_watcher.py | grep -v grep > $T/before.txt`; `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ --tb=short -q > knowledge/qa/evidence/no-test-spawns-a-watcher-suite-2026-09-10.txt 2>&1`; `ps … > $T/after.txt`; `diff $T/before.txt $T/after.txt` → empty (no line added) — paste the diff's emptiness and both counts; the summary line quoted in the receipt as `N passed` with the skip named as `one skip (test_gate_watcher, live-DB)` — never the word the Rule 20 block scans for.
> **Item 2 — the fix proven from outside pytest:** the pid census around the ONE test that used to spawn: `ps -eo pid,command | grep -F gate_watcher.py | grep -v grep | awk '{print $1}' | sort > $T/p0`; `pytest tests/test_depositor_receipts.py -q -p no:cacheprovider -k 'test_16 or test_24'`; the same census to `$T/p1`; `comm -13 $T/p0 $T/p1` → empty (no new pid). The control is READ, not run — a run would spawn the very process the plan retires: quote the DEV's dev-log heading `## The watcher census (Items 1, 3, 5)`, where Item 1's pre-fix run added one `gate_watcher.py diagnostic-holdfix.md` pid, beside this item's empty `comm` output.
> **Item 3 — production writes, stated exactly:** none outside the two evidence files; `$T` removed; no lane file, no lifecycle row, no lifecycle import outside pytest.
> **Item 4 — receipt** `knowledge/qa/evidence/no-test-spawns-a-watcher-qa-receipt-2026-09-10.md`: `numstat` over the DEV commits (`<base>..<dev>`, five files); a `## Verification` table with one row per Item 1–3, each quoting the line it rests on — ⛔ the status cell holds exactly one token (`✅`) and no positive row's text carries a hedging keyword; then RUN the canonical Rule 20 block (`$ELUVIAN_WRAP_ROOT/RULE_20_SELF_CHECK_BLOCK.md`) with `plan_slug: no-test-spawns-a-watcher-2026-09-10`, `qa_report_path` and `evidence_dir` absolute under `$(git rev-parse --show-toplevel)/knowledge/qa/evidence/`, `required_evidence_files: ["no-test-spawns-a-watcher-suite-2026-09-10.txt"]`, and APPEND its stdout — the banner `Rule 20 — QA Self-Check Results` and the closing `PASSED — SELF-CHECK PASSED` line are the block's output, never hand-authored; a `FAILED` stdout goes into the receipt and the step STOPS (thread 262).
> **Item 5 — commit**, path-scoped and gated: `grep -Eq '^[0-9]+ passed' knowledge/qa/evidence/no-test-spawns-a-watcher-suite-2026-09-10.txt && ! grep -Eq '[0-9]+ (failed|error)' knowledge/qa/evidence/no-test-spawns-a-watcher-suite-2026-09-10.txt && /Users/marklehn/Developer/bellows/.venv/bin/python tools/check_deposit.py /Users/marklehn/Developer/bellows/knowledge/decisions/in-progress-executable-<id>.md 2 --wt "$(git rev-parse --show-toplevel)" && git add knowledge/qa/evidence/no-test-spawns-a-watcher-qa-receipt-2026-09-10.md knowledge/qa/evidence/no-test-spawns-a-watcher-suite-2026-09-10.txt && git commit -F <msg-file> -- knowledge/qa/evidence/no-test-spawns-a-watcher-qa-receipt-2026-09-10.md knowledge/qa/evidence/no-test-spawns-a-watcher-suite-2026-09-10.txt`. ⛔ A QA step that finds it must change production code STOPS and requests a verdict (thread 262) rather than committing the change.
>
> **Deposits:**
> - `knowledge/qa/evidence/no-test-spawns-a-watcher-qa-receipt-2026-09-10.md`
> - `knowledge/qa/evidence/no-test-spawns-a-watcher-suite-2026-09-10.txt`
>
> **Scope:**
> - `knowledge/qa/evidence/no-test-spawns-a-watcher-qa-receipt-2026-09-10.md`
> - `knowledge/qa/evidence/no-test-spawns-a-watcher-suite-2026-09-10.txt`
>
> **Post-conditions:** the suite file's summary line is `N passed, 1 skipped` with N ≥ the DEV's count and no `failed`; Item 1's before/after census diff is empty; Item 2's empty `comm` output pasted beside the DEV's pre-fix census; the receipt's `## Verification` table has three rows and closes with the block's own PASSED line; one QA commit carrying the two evidence files.
