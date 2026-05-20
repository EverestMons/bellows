# bellows — Planner Contract Validators: Three-Validator Drop
**Date:** 2026-05-20 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** targeted | **Execution:** Step 1 (Bellows Developer) → Step 2 (Bellows QA) | **pause_for_verdict:** after_each_step

## How to Run This Plan

Bellows dispatches this plan automatically when deposited; no manual bootstrap required. DEV (Step 1) implements three new validators; QA (Step 2) verifies deliverables and runs targeted tests. The Planner performs the terminal Done/ move after Rule 22 verification on Step 2's QA report.

## CEO Context

Derived from `bellows/knowledge/research/planner-authored-contract-validation-2026-05-20.md` Q6 (Gap Assessment table). Three validators ship together: (V1) verdict filename format check, (V2) `pause_for_verdict` enum value validation, (V3) header field type contract enforcement. All three address silent-failure modes in Planner-authored artifacts, totaling approximately 125 LOC across `bellows/bellows.py` (V1) and `bellows/validators.py` (V2 + V3). Test scope is `targeted` — changes are scoped to validator + verdict-consumption code paths with dedicated test files (`tests/test_validators.py`, `tests/test_bellows.py`), and the diagnostic explicitly identified all three as small/parallelizable with no cross-file dependencies (Q4).

## Pre-Edit Verification (Rule 39)

Before performing any edits in Step 1, re-run each query below. If the output differs materially from the recorded output, STOP — do not proceed with edits. Instead, deposit a verification-mismatch report to `bellows/knowledge/flags/verification-mismatch-planner-contract-validators-three-validator-drop-step-1.md` documenting the claim, expected output, actual output, and timestamp. The Planner will triage the mismatch.

1. **Claim:** `_consume_verdicts()` in `bellows.py` silently continues when a file starts with `verdict-` but does NOT match the slug-step regex, with no log emitted (per diagnostic Q1 #2 and Q2 #2).
 **Query:** `grep -n "continue" bellows/bellows.py | head -40 && echo "---" && grep -n "_consume_verdicts" bellows/bellows.py`
 **Expected:** A `continue` statement near line 1123-1125 inside `_consume_verdicts()` (function definition near line 1083 or earlier per the SA's enclosing-scope reference) that follows a regex non-match without a preceding WARN log.

2. **Claim:** `header_says_pause()` in `bellows.py` returns `False` for any `pause_for_verdict` value not in `{"always", "after_step_1", "after_qa_step"}` (per diagnostic Q1 #4 and Gap 4b).
 **Query:** `grep -n "header_says_pause\|after_step_1\|after_qa_step\|always" bellows/bellows.py | head -30`
 **Expected:** Function definition near line 301-310 containing enumerated value checks against the three recognized strings, with no fall-through validation.

3. **Claim:** `_parse_plan_header()` in `gates.py` can return non-string values for header fields when YAML frontmatter is used (per diagnostic Q1 #4 and Gap 4a, observed 2026-05-17 `auto_close: false` Python bool crash).
 **Query:** `grep -n "_parse_plan_header\|str(.*auto_close\|\.lower()" bellows/bellows.py bellows/gates.py | head -30`
 **Expected:** `_parse_plan_header()` defined in `gates.py:50-116`. Point-fix `str()` wrap around line 491 in `bellows.py` for `auto_close`. No systematic type coercion at parse time.

4. **Claim:** `validators.py` exposes a `validate_at_claim()` orchestrator function that calls individual `check_*` functions and returns reject/warn results (per diagnostic Q3 Artifact 4 and shipped 2026-05-19 dispatch-mode validator pattern).
 **Query:** `grep -n "def check_\|def validate_at_claim\|_get_dispatch_mode" bellows/validators.py`
 **Expected:** Functions including `check_missing_dispatch_mode`, `check_stop_prose`, `validate_at_claim` (orchestrator), and `_get_dispatch_mode` helper near line 19-24.

---

## STEP 1 — Bellows Developer

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-planner-contract-validators-three-validator-drop-2026-05-20.md", "bellows/knowledge/decisions/in-progress-executable-planner-contract-validators-three-validator-drop-2026-05-20.md")`.
>
> You are the Bellows Developer. Read your specialist file at `bellows/agents/BELLOWS_DEVELOPER.md` first. **Pre-edit verification — run the four queries in the Pre-Edit Verification section at the top of this plan file BEFORE any edits.** If any query's actual output differs materially from the expected output, STOP and deposit a verification-mismatch report per the instructions in that section. Read the diagnostic findings at `bellows/knowledge/research/planner-authored-contract-validation-2026-05-20.md` — it is the canonical reference for every change in this plan. Skip the domain glossary read — this is validator implementation work with no domain interpretation. Implement three validators per the diagnostic's Q6 Gap Assessment, then commit.
>
> **V1 — Verdict filename format validator.** Edit `bellows/bellows.py` `_consume_verdicts()` function. Per the diagnostic Q1 Artifact 2 and Q3 Artifact 2 recommendation: after the existing `fname.startswith("verdict-request-")` exclusion AND the existing filename match against `^verdict-(.+)-step-(\d+)\.md$`, add a NEW check: if a file's name starts with `verdict-`, ends with `.md`, is NOT a `processed-*` file, is NOT a `verdict-request-*` file, AND does NOT match the slug-step regex — emit a WARN log naming the actual filename and the expected pattern, plus call the existing `_notify_malformed_verdict()` helper (or equivalent Pushover notification function — confirm the helper name from the 2026-05-12 verdict content validator implementation at `verdict.py:172-185`) to alert the CEO. Reuse the notification helper from the 2026-05-12 fix rather than creating a parallel one. The file is still skipped (`continue`) as before — only the silent-skip is transformed into loud failure. Add the new check immediately before the existing silent `continue` so the regex non-match path now logs before skipping.
>
> **V2 — `pause_for_verdict` enum validator.** Edit `bellows/validators.py`. Per diagnostic Gap 4b: add a new `check_pause_for_verdict_value(header: dict) -> ValidationResult` function (or whatever the existing return type is — confirm by reading `validators.py:check_missing_dispatch_mode` signature and matching the pattern exactly). The check reads the parsed `pause_for_verdict` header field; if present AND its value (after string coercion) is not in the set `{"always", "after_step_1", "after_qa_step", ""}` (empty string allowed because absent field defaults to empty), emit a WARN-level result naming the invalid value and the expected enum values. Do NOT reject — the defensive default already prevents the worst outcome (unintended auto-advance per diagnostic Q2 #4). Register the new check inside `validate_at_claim()` alongside the existing checks.
>
> **V3 — Header field type contract.** Edit `bellows/validators.py`. Per diagnostic Gap 4a: add a new `check_header_field_types(header: dict) -> ValidationResult` function. The check enumerates the known string-typed header fields (`auto_close`, `pause_for_verdict`, `dispatch_mode`) and verifies each (when present) is a string after `_parse_plan_header()` returns. For each field that exists but is not a string, emit a WARN naming the field, the actual type, and the actual value. This is WARN-level not reject because the point-fix `str()` wrap at `bellows.py:~491` already prevents the immediate crash class — V3 adds detectability so future occurrences are surfaced before they hit downstream code paths. Register inside `validate_at_claim()`.
>
> **Test additions for all three.** Edit `bellows/tests/test_validators.py` for V2 + V3, `bellows/tests/test_bellows.py` for V1 (or wherever `_consume_verdicts` tests live — confirm by reading the test file structure). Each validator gets at least three tests: positive case (valid input passes silently), negative case (invalid input produces the expected WARN/notification), and boundary case (empty/missing field handled gracefully). For V1 specifically, the test must use a temp directory containing a malformed-named verdict file and assert (a) the file is still skipped, (b) the notification helper is called with the expected filename, (c) a WARN is logged. For V2, parametrize against the set `{"true", "yes", "after_qa", "qa_checkpoint", "1"}` — plausible YAML-think values that all should WARN. For V3, parametrize against bool/int/None values for each enumerated field.
>
> **Run targeted tests.** `cd bellows && python -m pytest tests/test_validators.py tests/test_bellows.py -v` (or the equivalent — adjust pattern per project conventions). Deposit raw output to `bellows/knowledge/qa/evidence/executable-planner-contract-validators-three-validator-drop-2026-05-20/pytest_targeted.txt` (the QA agent will re-run; DEV runs to confirm no regressions before commit). All tests must pass. If any fail, fix before committing.
>
> **Restart-discipline reminder.** Per PLANNER_TEMPLATE Restart Discipline subsection: this plan modifies `validators.py` (consumed at plan claim time) and `bellows.py` (consumed by the running event loop). The Bellows daemon does NOT hot-reload Python modules. The QA step will exercise the changed code paths via unit tests in a fresh process, but the running daemon will continue to execute the pre-fix code until CEO restarts Bellows post-merge. Note this in the dev log so the CEO knows a restart is required for the validators to take effect on live plan dispatch.
>
> **Commit** with message `feat: three Planner contract validators (V1 verdict filename, V2 pause_for_verdict enum, V3 header field types)`.
>
> **Deposit a development log** at `bellows/knowledge/development/planner-contract-validators-three-validator-drop-2026-05-20.md` with: files modified (with line ranges), each of the 3 validators summarized in one paragraph each, test counts (before / after / new), test results, deviations from this plan (if any), restart-required note for CEO.
>
> **Then** append a standard prompt-feedback entry to `bellows/knowledge/research/agent-prompt-feedback.md` per the protocol at the top of that file.
>
> **Deposits:**
> - `bellows/bellows.py` (modified — V1)
> - `bellows/validators.py` (modified — V2 + V3)
> - `bellows/tests/test_bellows.py` (modified — V1 tests)
> - `bellows/tests/test_validators.py` (modified — V2 + V3 tests)
> - `bellows/knowledge/development/planner-contract-validators-three-validator-drop-2026-05-20.md` (new dev log)
> - `bellows/knowledge/research/agent-prompt-feedback.md` (appended)
> - `bellows/knowledge/qa/evidence/executable-planner-contract-validators-three-validator-drop-2026-05-20/` (evidence directory; pytest output deposited)

---

## STEP 2 — Bellows QA

---

> **Before starting, read `bellows/knowledge/development/planner-contract-validators-three-validator-drop-2026-05-20.md` and check the Output Receipt status field.** If status is not Complete, stop and report the issue to the CEO before proceeding.
>
> You are the Bellows QA agent. Read your specialist file at `bellows/agents/BELLOWS_QA.md` and the dev log from Step 1. Skip the domain glossary read — this is verification work scoped to specific files. Verify all 3 validators per Rule 17, run targeted tests per Rule 21, and produce a QA report.
>
> **FIRST — Deliverable Verification (Rule 17).** Read the DEV Output Receipt's "Files Created or Modified (Code)" list. For each listed file: verify it exists on disk and contains the described change. Produce a verification table:
>
> | Deliverable | Expected | Status (✅/❌) | Evidence |
> |---|---|---|---|
> | V1 production code | `_consume_verdicts()` in `bellows.py` emits WARN + notification on malformed verdict filename (file starts with `verdict-` but doesn't match slug-step regex and isn't `processed-*` or `verdict-request-*`) | | grep_v1_prod.txt |
> | V1 tests | `tests/test_bellows.py` contains ≥3 tests covering positive/negative/boundary cases for malformed verdict filename | | grep_v1_test.txt |
> | V2 production code | `validators.py` contains `check_pause_for_verdict_value` function with enum check against `{"always", "after_step_1", "after_qa_step", ""}` | | grep_v2_prod.txt |
> | V2 registration | `check_pause_for_verdict_value` is called inside `validate_at_claim` | | grep_v2_reg.txt |
> | V2 tests | `tests/test_validators.py` contains ≥3 tests covering positive/negative/boundary cases for pause_for_verdict enum | | grep_v2_test.txt |
> | V3 production code | `validators.py` contains `check_header_field_types` function enumerating `auto_close`, `pause_for_verdict`, `dispatch_mode` for string-type check | | grep_v3_prod.txt |
> | V3 registration | `check_header_field_types` is called inside `validate_at_claim` | | grep_v3_reg.txt |
> | V3 tests | `tests/test_validators.py` contains ≥3 tests covering positive/negative/boundary cases for header field types | | grep_v3_test.txt |
>
> Each evidence file is the raw `grep -n` output deposited at `bellows/knowledge/qa/evidence/executable-planner-contract-validators-three-validator-drop-2026-05-20/<filename>.txt`. Any ❌ → attempt fix or flag as blocked.
>
> **Run targeted tests (Rule 21 scope: targeted).** Execute `cd bellows && python -m pytest tests/test_validators.py tests/test_bellows.py -v`. Deposit raw output to `bellows/knowledge/qa/evidence/executable-planner-contract-validators-three-validator-drop-2026-05-20/pytest_targeted.txt`. All tests must pass.
>
> **Update PROJECT_STATUS.md** at `bellows/PROJECT_STATUS.md` — add a milestone entry: `2026-05-20: Planner Contract Validators V1+V2+V3. Three new validators (verdict filename format, pause_for_verdict enum, header field types) shipped per diagnostic-planner-authored-contract-validation-2026-05-20. Completes 5/8 → 8/8 of the Planner-authored contract surface identified in the 2026-05-12 architectural audit. ~125 LOC. CEO restart of Bellows daemon required for live effect.` Commit the PROJECT_STATUS update with descriptive message.
>
> **Deposit QA report** at `bellows/knowledge/qa/planner-contract-validators-three-validator-drop-qa-2026-05-20.md` with: deliverable verification table (Rule 17), targeted test results (Rule 21 with `pytest_targeted.txt` cited in evidence column), CEO restart-required note, and the Rule 20 self-check.
>
> **Rule 20 self-check.** Run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at the governance root. Use these values when filling in the template:
> - `plan_slug`: `executable-planner-contract-validators-three-validator-drop-2026-05-20`
> - `qa_report_path`: `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/planner-contract-validators-three-validator-drop-qa-2026-05-20.md`
> - `evidence_dir`: `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/executable-planner-contract-validators-three-validator-drop-2026-05-20/`
> - `required_evidence_files`: `["grep_v1_prod.txt", "grep_v1_test.txt", "grep_v2_prod.txt", "grep_v2_reg.txt", "grep_v2_test.txt", "grep_v3_prod.txt", "grep_v3_reg.txt", "grep_v3_test.txt", "pytest_targeted.txt"]`
>
> Include the literal stdout output of the block in the QA report. If the block prints `FAILED`, do not proceed with closure — halt and report to CEO.
>
> **Then** append a standard prompt-feedback entry to `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Final commit** with message `qa: planner contract validators (V1+V2+V3) verified`.
>
> **Deposits:**
> - `bellows/knowledge/qa/planner-contract-validators-three-validator-drop-qa-2026-05-20.md`
> - `bellows/knowledge/qa/evidence/executable-planner-contract-validators-three-validator-drop-2026-05-20/`
> - `bellows/PROJECT_STATUS.md` (modified)
> - `bellows/knowledge/research/agent-prompt-feedback.md` (appended)
