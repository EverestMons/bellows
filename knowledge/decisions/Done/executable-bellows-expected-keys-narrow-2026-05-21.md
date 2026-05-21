# Bellows — expected-keys warning narrow to pause_for_verdict only (bellows.py:416-419)
**Date:** 2026-05-21 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA) | **pause_for_verdict:** after_step_1 | **auto_close:** false

## Context

Per the 2026-05-21 expected-keys-warning diagnostic (`bellows/knowledge/decisions/Done/diagnostic-bellows-expected-keys-warning-2026-05-21.md`, findings at `bellows/knowledge/research/bellows-expected-keys-warning-2026-05-21.md`) and the 2026-05-21 expected-keys-shape-choice diagnostic (`bellows/knowledge/decisions/Done/diagnostic-bellows-expected-keys-shape-choice-2026-05-21.md`, findings at `bellows/knowledge/research/bellows-expected-keys-shape-choice-2026-05-21.md`), the expected-keys warning at bellows.py:416-419 is replaced with a targeted check for `pause_for_verdict` only. Shape C from the shape-choice diagnostic is the recommended implementation.

**Diagnostic-1 finding (lifted verbatim from Gap Assessment row (e)):**

| Gap | Current State | Proposed State | Change Required | Recommended | Rationale |
|-----|--------------|----------------|-----------------|-------------|-----------|
| (e) `pause_for_verdict` key | In `expected_keys` — warning fires when absent. **Consumed at runtime** by `header_says_pause()` for pause routing. Defensive default covers sparse headers. | **Keep in `expected_keys`** (as sole remaining member) OR use targeted warning. | Bellows code change (refine warning) | **Yes — keep, but refine** | Only safety-critical key in the set. Warning should fire for this key specifically, not bundled with cosmetic keys. |

**Diagnostic-2 finding (lifted verbatim from Recommended Shape):**

Shape C is the correct implementation for two reasons grounded in the code trace:

1. The defensive default's in-place mutation is the discriminator. After `_apply_defensive_header_defaults` at line 381, PV's presence or absence in `header` already encodes the full Case 3/4 distinction. In Case 3 (sparse header), the default inserts PV → `"pause_for_verdict" in header` is True → warning doesn't fire. In Case 4 (non-sparse header, PV missing), the default doesn't fire → `"pause_for_verdict" not in header` is True → warning fires. Neither a return flag (Shape A) nor a key snapshot (Shape B) adds information that the dict doesn't already contain. Both are provably redundant.

2. Zero test or API breakage. Shape C touches only lines 416-419 of `bellows.py` — the warning itself. It does not modify `_apply_defensive_header_defaults`, its return type, or its call convention. The 2 unit tests that call the function directly (test_bellows.py:2903, 2910) are unaffected.

**Exact anchor (from diagnostic-2 §3 Shape C, verbatim):**

Anchor (4 lines, bellows.py:416-419):
```
        expected_keys = {"project", "date", "author", "total_steps", "pause_for_verdict"}
        missing_keys = expected_keys - set(header.keys())
        if total_steps > 1 and missing_keys:
            _log("WARN", f"⚠️ {total_steps} steps but parsed header is missing: {sorted(missing_keys)}. Parsed keys: {sorted(header.keys())}. If pause_for_verdict was missing, the defensive default has set it to after_step_1.", slug=slug_for(plan_name))
```

Replacement (2 lines):
```
        if total_steps > 1 and "pause_for_verdict" not in header:
            _log("WARN", f"⚠️ {total_steps}-step plan missing pause_for_verdict — plan will auto-advance without pausing at intermediate steps", slug=slug_for(plan_name))
```

The existing sparse-header warning at bellows.py:382-383 covers Case 3 reporting and MUST be preserved unchanged.

**Side-finding NOT addressed by this plan:** Diagnostic-2 §2 surfaced that the defensive default at bellows.py:381 is ineffective for runtime pause behavior because `header` is reassigned at bellows.py:494 from `gates.check()` which re-parses without applying the defensive default. This is out of scope for the warning-narrowing fix and is tracked as a separate BACKLOG item dated 2026-05-21.

---
---

## STEP 1 — Bellows Developer

---

> You are the Bellows Developer. Read your specialist file at `bellows/agents/BELLOWS_DEVELOPER.md` first. **Skip glossary read.** **Pre-edit verification:** Before performing the edit, run `grep -n 'expected_keys = {' bellows.py` and confirm exactly ONE match at line 416 with content `        expected_keys = {"project", "date", "author", "total_steps", "pause_for_verdict"}`. Then run `grep -n 'sparse header' bellows.py` and confirm exactly ONE match (the line-382-383 sparse-header warning) — this must remain UNCHANGED after the edit. If either count differs from expected, STOP — deposit a verification-mismatch report at `bellows/knowledge/flags/verification-mismatch-bellows-expected-keys-narrow-2026-05-21-step-1.md` documenting actual line numbers and counts, and halt. **Task:** Apply ONE edit to `bellows/bellows.py` using the Edit tool. Replace the exact 4-line block:<br><br>```<br>        expected_keys = {"project", "date", "author", "total_steps", "pause_for_verdict"}<br>        missing_keys = expected_keys - set(header.keys())<br>        if total_steps > 1 and missing_keys:<br>            _log("WARN", f"⚠️ {total_steps} steps but parsed header is missing: {sorted(missing_keys)}. Parsed keys: {sorted(header.keys())}. If pause_for_verdict was missing, the defensive default has set it to after_step_1.", slug=slug_for(plan_name))<br>```<br><br>with the 2-line block:<br><br>```<br>        if total_steps > 1 and "pause_for_verdict" not in header:<br>            _log("WARN", f"⚠️ {total_steps}-step plan missing pause_for_verdict — plan will auto-advance without pausing at intermediate steps", slug=slug_for(plan_name))<br>```<br><br>Preserve indentation exactly (8 spaces of leading whitespace on each line). **Verification after edit:** read bellows.py lines 380-420 (covering both the sparse-header warning at 382-383 and the new narrowed warning) and confirm: (a) the new 2-line warning is present at approximately line 416-417, (b) the existing sparse-header warning at 382-383 is UNCHANGED, (c) the old 4-line `expected_keys`/`missing_keys` block is GONE. Re-run `grep -n 'expected_keys = {' bellows.py` and confirm 0 matches. Re-run `grep -n 'sparse header' bellows.py` and confirm exactly 1 match (the preserved line-382-383 warning). **Deposit a dev log:** write to `bellows/knowledge/development/bellows-expected-keys-narrow-2026-05-21.md` documenting: the anchor block (4 lines), the replacement block (2 lines), before/after snippets with 3 lines of surrounding context (lines 413-422 approximately), grep verification counts before/after, and a paragraph citing both 2026-05-21 expected-keys diagnostics as authority. **Test impact note:** Diagnostic-2 §6 flagged that the existing test `test_warning_multi_step_plan_without_pause_for_verdict` (if present in test_bellows.py) may need an assertion update to match the new warning text — check whether this test exists by running `grep -n 'pause_for_verdict' tests/test_bellows.py | grep -i warn` and report results in the dev log. Do NOT modify the test file in this step; report findings for the QA agent to handle. **Commit:** stage `bellows.py` and the dev log; commit message `fix(bellows): narrow expected-keys warning to pause_for_verdict only (bellows.py:416-419)`. **DO NOT push.** **Standard prompt feedback protocol** → append entry to `bellows/knowledge/research/agent-prompt-feedback.md`. Second commit: `docs: prompt feedback — bellows DEV expected-keys narrow`. **DO NOT push.**
>
> **Deposits:**
> - `bellows/bellows.py` (modified)
> - `bellows/knowledge/development/bellows-expected-keys-narrow-2026-05-21.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md`

---
---

## STEP 2 — Bellows QA

---

> You are the Bellows QA Agent. Read your specialist file at `bellows/agents/BELLOWS_QA.md` first. **Skip glossary read.** **Before starting, read `bellows/knowledge/development/bellows-expected-keys-narrow-2026-05-21.md` (DEV Step 1 deposit) and check its Output Receipt status; if not Complete, stop and report the blocker.** **FIRST — Deliverable Verification (Rule 17).** Verification table: | Deliverable | Expected | Status (✅/❌) | Evidence |. Specifically: (1) `bellows.py` no longer contains `expected_keys = {` anywhere — `grep -n 'expected_keys = {' bellows.py` returns 0 matches; (2) `bellows.py` contains the new narrowed warning — `grep -n '"pause_for_verdict" not in header' bellows.py` returns exactly 1 match; (3) the new warning message text is present — `grep -n 'will auto-advance without pausing at intermediate steps' bellows.py` returns exactly 1 match; (4) the existing sparse-header warning at bellows.py:382-383 is unchanged — `grep -n 'sparse header' bellows.py` returns exactly 1 match (the same line as before the edit); (5) dev log exists at `bellows/knowledge/development/bellows-expected-keys-narrow-2026-05-21.md` with anchor/replacement blocks, before/after snippets, grep verifications, and citation of both 2026-05-21 expected-keys diagnostics; (6) `agent-prompt-feedback.md` has a new 2026-05-21 entry from this plan. Capture each grep to evidence files in `bellows/knowledge/qa/evidence/executable-bellows-expected-keys-narrow-2026-05-21/`: `no_expected_keys.txt`, `new_predicate.txt`, `new_warning_text.txt`, `sparse_header_preserved.txt`, `dev_log_present.txt`, `feedback_entry.txt`. **Targeted test run.** Run `python3 -m pytest tests/test_bellows.py -v 2>&1 | tee bellows/knowledge/qa/evidence/executable-bellows-expected-keys-narrow-2026-05-21/pytest_targeted.txt`. The change replaces a warning's text and trigger condition. Existing tests for the warning may need assertion updates — see DEV's "Test impact note" in the dev log. If `test_warning_multi_step_plan_without_pause_for_verdict` (or any similarly-named test) fails because its expected-text assertion no longer matches the new warning, that's an expected failure for this fix: update the test assertion to match the new warning text (`"will auto-advance without pausing at intermediate steps"` instead of `"steps but parsed header is missing"`), commit the test update separately with message `test(bellows): update assertion for narrowed expected-keys warning`, then re-run pytest. Any OTHER test failures are unexpected and block the plan close — report to CEO. Capture the final passing pytest output to `pytest_targeted.txt`. **Structural compliance check.** Run `git diff HEAD~1 -- bellows.py 2>&1 | tee bellows/knowledge/qa/evidence/executable-bellows-expected-keys-narrow-2026-05-21/diff.txt` and verify the diff shows exactly the 4-line removal + 2-line addition at lines 416-419, with no other modifications to bellows.py. The diff must show -4/+2 line count for the bellows.py change. **Rule 20 self-check** — run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at governance root. Use these values: `plan_slug` = `executable-bellows-expected-keys-narrow-2026-05-21`; `qa_report_path` = `bellows/knowledge/qa/executable-bellows-expected-keys-narrow-2026-05-21.md`; `evidence_dir` = `bellows/knowledge/qa/evidence/executable-bellows-expected-keys-narrow-2026-05-21/`; `required_evidence_files` = `["no_expected_keys.txt", "new_predicate.txt", "new_warning_text.txt", "sparse_header_preserved.txt", "dev_log_present.txt", "feedback_entry.txt", "pytest_targeted.txt", "diff.txt"]`. Include literal stdout in QA report. If FAILED, halt — report to CEO. **Final:** Update `bellows/PROJECT_STATUS.md` — prepend a 2026-05-21 entry under Completed for "Bellows expected-keys warning narrowed to pause_for_verdict only (bellows.py:416-419)" with a one-paragraph summary citing the two 2026-05-21 expected-keys diagnostics. Use `Desktop Commander:edit_block` with the existing topmost Completed entry as the anchor (insert immediately before it). **Commit:** stage QA report, evidence files, and PROJECT_STATUS update with message `qa(bellows): expected-keys warning narrow`. **DO NOT push.** **Standard prompt feedback protocol** → append entry to `bellows/knowledge/research/agent-prompt-feedback.md`. Second commit: `docs: prompt feedback — bellows QA expected-keys narrow`. **DO NOT push.**
>
> **Deposits:**
> - `bellows/knowledge/qa/executable-bellows-expected-keys-narrow-2026-05-21.md`
> - `bellows/knowledge/qa/evidence/executable-bellows-expected-keys-narrow-2026-05-21/` (8 evidence files per Rule 20 self-check list)
> - `bellows/PROJECT_STATUS.md` (modified)
> - `bellows/knowledge/research/agent-prompt-feedback.md`
> - optional: `tests/test_bellows.py` (modified IFF the test assertion update is needed)

---

## Daemon-restart note

This fix touches `bellows.py`, which Bellows does not hot-reload (Rule 35 / Restart Discipline). The running daemon continues executing pre-fix code through this plan's lifecycle. The warning narrowing affects log output only — no behavior change for plan dispatch, gates, or verdict logic. After plan close + daemon restart, the new narrowed warning becomes effective for all future plan dispatches.
