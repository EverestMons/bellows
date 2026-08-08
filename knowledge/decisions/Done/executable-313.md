# Executable: record decided_by transition provenance — gate_auto vs verdict_file

**Type:** Executable
**Project:** bellows
**Depends on:** executable-312 (Done — shipped the characterization test that pins this gap; invariant 3 flips here)
**Created:** 2026-08-07
**Author:** Planner
**dispatch_mode:** bellows
**pause_for_verdict:** always
**Priority:** 5
**cycle_tier:** T1
**qa_steps:** [2]

⚠️ **ID NOTE — the deposit filename is decided AT DEPOSIT.** Bellows mints the id from `id_sequence` at claim (`lifecycle.py:199`); it does not parse the filename. Slug+date name form used to avoid claiming a number blind.

---

## Why this exists

Plan 312's invariant 3 pinned a real gap: `verdicts.decided_by` cannot distinguish a **mechanical** transition from a **prose** one. Two facts established by direct read:

1. **`bellows.py:2118`** is the only `record_verdict_outcome` call. It fires inside `consume_verdicts` after an agent-written verdict file is regex-parsed, and hardcodes `decided_by="ceo"` — inaccurate, since under delegated verdict authority the file is often a Planner self-issue, not a live CEO.
2. **The auto-close branch** (`bellows.py:904-934`) advances a plan on clean gates + `auto_close` with NO `verdicts` row at all — a mechanical continue is invisible in the table.

This plan makes `decided_by` mechanically meaningful with two literal values a log reader can query:
- **`gate_auto`** — the daemon auto-continued/closed on clean gates, no verdict file involved.
- **`verdict_file`** — a verdict file was consumed (CEO or Planner self-issue; the daemon cannot distinguish these, so the label claims only what is mechanically true: a file decided it).

**Blast radius (verified):** no `reporting.py`/`status.py`/`dashboard.py` reads `decided_by`; the only `"ceo"` assertions are `test_lifecycle.py:512` (a storage round-trip writing its own value — unaffected) and `test_gate_transaction_mechanization.py` invariant 3 (updated here by design). Historical rows (incl. plan 312's two `"ceo"` rows) are left as-is; the change is forward-looking.

---

## How to Run This Plan

**Bootstrap prompt:**
```
Read the plan at knowledge/decisions/in-progress-executable-<id>.md (the daemon renames the deposited placeholder on claim). Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation.
```

---
---

## STEP 1 — DEV

> **FIRST — post a short visible chat message (1–2 sentences) confirming you are starting this plan and your immediate next action.** Do NOT rename this plan file. Read your Bellows Developer specialist file, then `bellows.py` around the `consume_verdicts` outcome write (`:2118`) and the auto-close branch (`:904`-`:934`), `lifecycle.py` (`record_verdict_request`, `record_verdict_outcome`), and `tests/test_bellows.py::test_diagnostic_auto_close_moves_to_done` (the auto-close test template). **All commands run from `/Users/marklehn/Developer/GitHub/bellows`.**
>
> **Task A0 — pre-edit cleanliness.** `git -C /Users/marklehn/Developer/GitHub/bellows status --porcelain -- bellows.py tests/test_gate_transaction_mechanization.py` must be empty. If DIRTY, enumerate the hunks, attribute each to this plan; any unattributable hunk → HALT, do not restore.
>
> **Task B — edit `bellows.py`, two sites, quoted anchors (read and locate the exact lines before editing):**
> - **Site 1 (prose path):** the single line `lifecycle.record_verdict_outcome(_lc_plan_id, step_number, v, decided_by="ceo", disposition_summary=reason)` — change `decided_by="ceo"` to `decided_by="verdict_file"`. Change ONLY the literal; leave every other argument identical.
> - **Site 2 (auto-close path):** immediately AFTER the `verdict.log_to_ledger(..., "auto-close", ...)` call in the auto-close branch and BEFORE the plan is moved to `Done/`, add two calls:
>   `lifecycle.record_verdict_request(plan_id, current_step, pause_reason_code="auto_close")`
>   `lifecycle.record_verdict_outcome(plan_id, current_step, "continue", decided_by="gate_auto")`
>   Use the `plan_id` and `current_step` already in scope in `run_plan`. Add a one-line comment stating these record the mechanical auto-continue so the transition is auditable (the 312 gap).
>
> **Task C — update `tests/test_gate_transaction_mechanization.py` invariant 3 (`TestDecidedByGap`).** The characterization test that asserted both rows are `"ceo"` is now stale by design. Replace it with a discrimination test: record one outcome with `decided_by="gate_auto"` and one with `decided_by="verdict_file"`, then assert the two are DISTINCT and each equals its expected literal — i.e. a log reader can mechanically tell a mechanical transition from a prose one. Update the docstring to state the gap is now CLOSED and reference this plan. Rename the class/method if the old name (`...record_ceo`) no longer fits.
>
> **Task D — add an auto-close provenance test** to `tests/test_gate_transaction_mechanization.py` (or extend the pattern of `test_diagnostic_auto_close_moves_to_done` if driving `run_plan` is needed): assert that when the auto-close branch runs, a `verdicts` row is written with `decided_by="gate_auto"` and `outcome="continue"`. If a full `run_plan` drive is impractical in a unit test, assert at minimum, at the lifecycle layer, that `record_verdict_request`+`record_verdict_outcome(decided_by="gate_auto")` produces a queryable row — and state explicitly in a comment why the run_plan-level assertion was or was not included (do not silently omit it).
>
> **Task E — run targeted tests ONLY** (never the full suite in DEV): `python3 -m pytest tests/test_gate_transaction_mechanization.py tests/test_bellows.py -k "verdict or decided or auto_close or transaction" --tb=short -q 2>&1 | cat`. Paste RAW output UNTRUNCATED; all selected tests pass and `echo $?` = 0.
>
> **Scope:**
> - `bellows.py`
> - `tests/test_gate_transaction_mechanization.py`
> - `knowledge/development/decided-by-provenance-dev-log-2026-08-07.md`
>
> **Deposit the dev log** with the exact before/after lines for both `bellows.py` sites, the invariant-3 flip, the Task D decision (included or why deferred), and the RAW targeted-test output. Canonical Python/MCP file-write — NO heredoc. Commit all (NO push). `#### Prompt Feedback` in `### Ledger Updates`.
>
> **STOP. Do NOT proceed to Step 2. Wait for CEO verdict.**

**Deposits:**
- `bellows/bellows.py`
- `bellows/tests/test_gate_transaction_mechanization.py`
- `bellows/knowledge/development/decided-by-provenance-dev-log-2026-08-07.md`

---
---

## STEP 2 — QA

> **Task Q0 — re-pin state.** `git -C /Users/marklehn/Developer/GitHub/bellows log -1 --oneline -- bellows.py tests/test_gate_transaction_mechanization.py` — the most recent commit touching either must be Step 1's. A foreign commit → HALT and report.
>
> 1. **Run the full `bellows` test suite** → `full-suite.txt`: `python3 -m pytest tests/ --tb=short -q 2>&1 | cat`. Record the raw summary line verbatim. ⚠️ The suite baseline before this plan was 873 passed (312's QA); this plan changes test COUNT (invariant 3 flipped, Task D may add one) — report the fresh number, do not reconcile to 873.
> 2. **Re-run the targeted subset** → `targeted-tests.txt`: the Step 1 Task E command. Record raw output (≥ last 200 lines incl. the pytest summary line) — never a summary of it.
> 3. Confirm both `bellows.py` sites changed (`grep -F 'decided_by="gate_auto"' bellows.py` and `grep -F 'decided_by="verdict_file"' bellows.py` each print a line and exit 0; confirm `grep -F 'decided_by="ceo"' bellows.py` prints nothing / exits 1 — bare grep, no pipe). State what each prints on success and failure.
> 4. **Emit the QA Receipt with the canonical Rule 20 self-check block**, a verification row per numbered item with its raw evidence.
>    - `required_evidence_files`: `[full-suite.txt, targeted-tests.txt]`
>    - Deposit both evidence files BEFORE running the block — it `sys.exit(1)`s if any is missing or empty.
>    - Include the block's literal stdout. The banner `Rule 20 — QA Self-Check Results` and the `PASSED — SELF-CHECK PASSED` line must appear BYTE-EXACT (em-dash U+2014). If it prints FAILED, HALT.
>    - **Evidence rule:** deposit RAW command output (≥ last 200 lines incl. the pytest summary line), never a summary.
>
> **Scope:**
> - `knowledge/qa/decided-by-provenance-qa-report-2026-08-07.md`
> - `knowledge/qa/full-suite.txt`
> - `knowledge/qa/targeted-tests.txt`
>
> **STOP. Wait for CEO verdict.**

**Deposits:**
- `bellows/knowledge/qa/decided-by-provenance-qa-report-2026-08-07.md`
- `bellows/knowledge/qa/full-suite.txt`
- `bellows/knowledge/qa/targeted-tests.txt`

---

## Method + boundaries

- **Scope:** two literal/call edits in `bellows.py` + test updates. No schema change (`verdicts.decided_by` already exists). No historical-row migration.
- ⚠️ **HALT ROUTING:** if `bellows.py`, `lifecycle.py`, `tests/test_gate_transaction_mechanization.py`, `tests/test_bellows.py`, the Bellows Developer specialist file, or `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` (Step 2 item 4's block source) is unreadable, HALT the step that needs it and name it.
- ⚠️ **`grep -F` mandatory for literals** (ugrep shim; a non-`-F` pattern can exit 1 silently on a present line); run the grep BARE, never through a pipe (`$?` after a pipe reports the last command's exit).
- ⚠️ Every `**Deposits:**` filename is the DECLARED deposit, matched by basename. Do NOT re-date any at run time.

---

## Drafting Cycle

**Tier:** T1 — trigger fired: T-6 (touches daemon verdict-recording, gate-adjacent machinery). Not T2: additive-plus-one-literal, no gate LOGIC changed, no clone, blast radius verified nil (no production consumer of `decided_by`).

- **Lens 1 (weak spots):** the auto-close path has no pending `verdicts` row, so `record_verdict_outcome` alone (which updates WHERE outcome IS NULL) would no-op — Task B Site 2 pairs it with `record_verdict_request` first. Verified against `record_verdict_outcome` (`lifecycle.py:515-518`).
- **Lens 2 (destruction):** no guard relaxed; both edits are additive/relabel. The relabel is safe — no code branches on `decided_by`'s value (grep-verified), only stores it.
- **Lens 3 (vulnerabilities):** the `WorktreeTeardownError` sub-branch of auto-close converts to a `gate_failure` pause and `return`s BEFORE reaching Site 2 — so the `gate_auto` rows are only written on genuine successful auto-close, never on the teardown-failure fork. Site 2 must sit after `log_to_ledger("auto-close")`, which is only reached past that `return`.
- **Lens 4 (integration-vs-record):** invariant 3's characterization test (312) becomes false when the gap closes — that flip is the intended signal and is executed in Task C; the record (dev log) states the closure. `test_lifecycle.py:512` writes its own `"ceo"` value and is unaffected.
- **Lens 5 (ACID):** a halt after Step 1 leaves `bellows.py` changed with the invariant-3 test flipped — a consistent state (production + test move together in one step). No partial-schema risk (no schema change). Step 2 measures the fresh suite count rather than asserting the stale 873.

**Closing:** small, well-scoped production change with verified nil blast radius; one drafting pass, no fork requiring CEO decision beyond deposit approval.
