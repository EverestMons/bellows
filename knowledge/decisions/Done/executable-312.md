# Executable: gate→verdict transaction-mechanization test — pin the decided_by prose gap

**Type:** Executable
**Project:** bellows
**Depends on:** none (additive test-only; no production code changes)
**Created:** 2026-08-07
**Author:** Planner
**dispatch_mode:** bellows
**pause_for_verdict:** always
**Priority:** 5
**cycle_tier:** T0
**qa_steps:** [2]

⚠️ **ID NOTE — the deposit filename is decided AT DEPOSIT.** Bellows mints the id from `id_sequence` at claim (`lifecycle.py:199`) and does not parse the filename. This plan uses the slug+date name form to avoid claiming a number blind.

---

## Why this exists

The CEO asked whether the Bellows lifecycle's node-to-node transitions are decided **mechanically** (from records) or by **prose an agent interprets**. A read of the transaction seam established:

- **`gates.check` is a pure, deterministic function** — `passed == (len(failures) == 0)` (`gates.py:230`). No LLM, no interpretation.
- **`lifecycle.record_gate_events` is a faithful mechanical mirror** of `gate_result["failures"]` (`lifecycle.py:419-444`) — one `fail` row per declared failure, one `pass` row per other standard gate; no prose path can create a row.
- **The verdict-outcome record is prose-blind.** The one and only `record_verdict_outcome` call site (`bellows.py:2118`) fires only inside `consume_verdicts`, after an **agent-written** `verdict-…-step-N.md` file is regex-parsed (`bellows.py:2095`), and it hardcodes **`decided_by="ceo"`**. A mechanical auto-continue and a prose-interpreted continue are therefore **indistinguishable in the record** — the `verdicts.decided_by` column, schema'd to answer "which transitions leaned on prose?", carries no such signal today.

This plan ships a test that **asserts the transaction is decided by records, reading only the mechanical `gate_result` and `lifecycle.db` rows** — never narrative output. Invariants 1–2 pin the mechanical guarantees; invariant 3 is a **characterization test that pins the `decided_by` gap** and will fail the day real mechanical-vs-prose discrimination is wired, forcing the record to catch up.

**Scope boundary:** test-only. No change to `bellows.py`, `gates.py`, or `lifecycle.py`. The `decided_by` fix (if the CEO wants it) is a separate executable.

---

## How to Run This Plan

**Bootstrap prompt:**
```
Read the plan at knowledge/decisions/in-progress-executable-<id>.md (the daemon renames the deposited placeholder on claim). Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation.
```

---
---

## STEP 1 — DEV

> **FIRST — post a short visible chat message (1–2 sentences) confirming you are starting this plan and your immediate next action.** Do NOT rename this plan file. Read your Bellows Developer specialist file, then `lifecycle.py` (the record functions `mint_and_claim`, `record_step_start`, `record_gate_events`, `record_verdict_request`, `record_verdict_outcome`), `gates.py` (`check`), and `tests/conftest.py` (the autouse `isolate_lifecycle_db` fixture — the isolated DB is already inited per-test). **All commands run from `/Users/marklehn/Developer/GitHub/bellows`.**
>
> **Task A0 — pre-edit cleanliness.** `git -C /Users/marklehn/Developer/GitHub/bellows status --porcelain -- tests/test_gate_transaction_mechanization.py` must be empty (the file is new). If a stale copy exists, enumerate its hunks, attribute each to this plan, and only then `git restore`; any unattributable hunk → HALT.
>
> **Task B — write `tests/test_gate_transaction_mechanization.py`** with exactly the three invariants below. Every assertion reads the mechanical `gate_result` or a `lifecycle.db` row; NO test inspects narrative agent output. Bind to the real signatures: `mint_and_claim(plan_type, target_project, title, dispatch_mode, tier, total_steps, deposit_placeholder_name, db_path=...)`, `record_step_start(plan_id, step_number, db_path=...) -> step_id`, `record_gate_events(step_id, gate_result, db_path=...)`, `record_verdict_request(plan_id, step_number, db_path=...)`, `record_verdict_outcome(plan_id, step_number, outcome, decided_by=..., db_path=...)`. Use a per-test DB via `lifecycle.init_lifecycle_db(str(tmp_path / "lifecycle.db"))` (the conftest fixture also isolates the module-level path). Standard gate name set to assert against: `receipt_status, no_errors, no_permission_denials, deposit_exists, scope_check, rule_20_self_check, rule_22_verification` (7 total — mirror `lifecycle.py:433-437`).
>
> **Invariant 1 — `gate_events` is an exact mechanical image of `gate_result`:** given a `gate_result` with one failure (`scope_check`), assert the DB has exactly one `fail` row (`scope_check`), a `pass` row for each of the other six standard gates, and exactly 7 rows total — nothing conjured. A second test: an all-failures `gate_result` yields zero `pass` rows.
>
> **Invariant 2 — `gates.check` is deterministic and arithmetic over failures:** call `gates.check(parsed, plan_text, 1, str(tmp_path))` twice with an identical `parsed` receipt and assert `failures` and `passed` are identical across calls; assert `passed is (len(failures) == 0)`; with a failing receipt (`receipt_status="Incomplete"`) assert `passed is False` and `receipt_status` is among the failures.
>
> **Invariant 3 — characterization test pinning the `decided_by` gap:** record two verdict outcomes (steps 1 and 2) via `record_verdict_outcome(..., decided_by="ceo")`, then query `verdicts.decided_by` and assert both are `"ceo"`. The test's docstring MUST state: this pins that `bellows.py:2118` hardcodes `decided_by="ceo"`, so a mechanical auto-continue and a prose-parsed continue are indistinguishable in the record, and this test is EXPECTED to fail the day real discrimination is wired — that failure is the signal to update it.
>
> **Task C — run targeted tests ONLY** (never the full suite in DEV): `python3 -m pytest tests/test_gate_transaction_mechanization.py -v 2>&1 | cat`. Paste the RAW output UNTRUNCATED; all tests must pass and `echo $?` = 0.
>
> **Scope:**
> - `tests/test_gate_transaction_mechanization.py`
> - `knowledge/development/gate-transaction-mechanization-dev-log-2026-08-07.md`
>
> **Deposit the dev log** with the final test source, the RAW targeted-test output, and the invariant-3 gap note. Canonical Python/MCP file-write — NO heredoc. Commit all (NO push). `#### Prompt Feedback` in `### Ledger Updates`.
>
> **STOP. Do NOT proceed to Step 2. Wait for CEO verdict.**

**Deposits:**
- `bellows/tests/test_gate_transaction_mechanization.py`
- `bellows/knowledge/development/gate-transaction-mechanization-dev-log-2026-08-07.md`

---
---

## STEP 2 — QA

> **Task Q0 — re-pin state.** `git -C /Users/marklehn/Developer/GitHub/bellows log -1 --oneline -- tests/test_gate_transaction_mechanization.py` — the most recent commit touching it must be Step 1's. A foreign commit → HALT and report.
>
> 1. **Run the full `bellows` test suite** → `full-suite.txt`: `python3 -m pytest tests/ --tb=short -q 2>&1 | cat`. Record the raw summary line verbatim.
> 2. **Re-run the targeted subset** → `targeted-tests.txt`: `python3 -m pytest tests/test_gate_transaction_mechanization.py -v 2>&1 | cat`. Record raw output (≥ last 200 lines including the pytest summary line) — never a summary of it.
> 3. Confirm all three invariants pass and that invariant 3 asserts `decided_by == "ceo"` for both rows (the pinned gap).
> 4. **Emit the QA Receipt with the canonical Rule 20 self-check block**, a verification row per numbered item above with its raw evidence.
>    - `required_evidence_files`: `[full-suite.txt, targeted-tests.txt]`
>    - Deposit both evidence files BEFORE running the block — it `sys.exit(1)`s if any is missing or empty.
>    - Include the block's literal stdout. The banner `Rule 20 — QA Self-Check Results` and the `PASSED — SELF-CHECK PASSED` line must appear BYTE-EXACT (em-dash U+2014). If it prints FAILED, HALT.
>    - **Evidence rule:** deposit RAW command output (≥ last 200 lines including the pytest summary line), never a summary.
>
> **Scope:**
> - `knowledge/qa/gate-transaction-mechanization-qa-report-2026-08-07.md`
> - `knowledge/qa/full-suite.txt`
> - `knowledge/qa/targeted-tests.txt`
>
> **STOP. Wait for CEO verdict.**

**Deposits:**
- `bellows/knowledge/qa/gate-transaction-mechanization-qa-report-2026-08-07.md`
- `bellows/knowledge/qa/full-suite.txt`
- `bellows/knowledge/qa/targeted-tests.txt`

---

## Method + boundaries

- **Scope is a new test file only.** No production code (`bellows.py`/`gates.py`/`lifecycle.py`) is edited. Invariant 3 is a characterization test, not a fix.
- ⚠️ **HALT ROUTING:** if `lifecycle.py`, `gates.py`, `tests/conftest.py`, the Bellows Developer specialist file, or `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` (Step 2 item 4's block source) is unreadable, HALT the step that needs it and name it in the dev/QA log.
- ⚠️ **`grep -F` mandatory for literals** (ugrep shim; a non-`-F` pattern can exit 1 silently on a present line).
- ⚠️ Every `**Deposits:**` filename is the DECLARED deposit, matched by basename. Do NOT re-date any at run time — keep the authored date.
