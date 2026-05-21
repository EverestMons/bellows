# Bellows — isinstance Asymmetry Fix at bellows.py:594
**Date:** 2026-05-21 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA) | **pause_for_verdict:** after_step_1 | **auto_close:** false

## Context

Per the 2026-05-21 isinstance-asymmetry diagnostic findings at `bellows/knowledge/research/bellows-isinstance-asymmetry-2026-05-21.md` (now in `Done/`), Block 2 at bellows.py:594 lacks the defensive `isinstance(f, dict)` guard that Block 1 at bellows.py:505 has. Both blocks were introduced in the same commit `4bd1c84` (2026-05-21 verdict-enrichment), making the asymmetry an authorial oversight rather than deliberate design.

**Diagnostic Gap Assessment row (a) — lifted verbatim:**

| Gap | Current State | Proposed State | Change Required | Recommended | Rationale |
|---|---|---|---|---|---|
| (a) Block 2 defensive guard | `f["gate"]` — subscript access, no isinstance check; crashes on non-dict | `isinstance(f, dict) and f.get("gate")` — mirrors Block 1 pattern | 1-line edit at bellows.py:594 | **Yes** | Zero-cost defensive fix; eliminates crash-vs-graceful-pause asymmetry; same commit introduced both blocks so the asymmetry is clearly an oversight |

**Why ship it:**

The diagnostic's Section 4 establishes (1) no behavioral change today (all entries are dicts), (2) no bug-masking risk (the guard produces graceful `gate_failure` pause instead of `TypeError` crash on hypothetical non-dict entry), (3) historical precedent for breakage (2026-05-03 commit `272fbe4` documents string-to-dict refactor in this exact code area).

Items (b) and (c) from the Gap Assessment are out of scope for this executable: (b) no current upstream non-dict producer exists (verified clean by the 21-site enumeration); (c) optional type annotation is deferred (low ROI per the diagnostic).

**Exact anchor (from diagnostic Section 4, verbatim):**

Anchor: `if all(f["gate"] == "rule_22_verification" for f in gate_result["failures"]):`

Replacement: `if all(isinstance(f, dict) and f.get("gate") == "rule_22_verification" for f in gate_result["failures"]):`

Location: bellows.py:594 (single occurrence — Block 1 at line 505 already uses `isinstance(f, dict) and f.get("gate") == ...` pattern).

---
---

## STEP 1 — Bellows Developer

---

> You are the Bellows Developer. Read your specialist file at `bellows/agents/BELLOWS_DEVELOPER.md` first. **Skip glossary read — this is a single-line code-tracing fix task.** **Pre-edit verification:** Before performing the edit, run `grep -n 'f\["gate"\] == "rule_22_verification"' bellows.py` and confirm exactly ONE match at line 594. Then run `grep -n 'isinstance(f, dict) and f.get("gate") == "rule_22_verification"' bellows.py` and confirm exactly ONE match at line 505. If either count differs from expected, STOP — deposit a verification-mismatch report at `bellows/knowledge/flags/verification-mismatch-bellows-isinstance-asymmetry-fix-2026-05-21-step-1.md` documenting the actual line numbers and counts, and halt. The Planner triages. **Task:** Apply ONE edit to `bellows/bellows.py` using the Edit tool. Replace the exact line `                if all(f["gate"] == "rule_22_verification" for f in gate_result["failures"]):` with `                if all(isinstance(f, dict) and f.get("gate") == "rule_22_verification" for f in gate_result["failures"]):`. Preserve indentation exactly (16 spaces of leading whitespace). The replacement adds `isinstance(f, dict) and ` after `all(` and changes `f["gate"]` to `f.get("gate")` — mirroring Block 1's pattern at line 505 verbatim. **Verification after edit:** read bellows.py lines 590-600 and confirm the change landed cleanly. Re-run `grep -n 'isinstance(f, dict) and f.get("gate") == "rule_22_verification"' bellows.py` and confirm the count is now exactly TWO (lines 505 and 594). **Deposit a dev log:** write to `bellows/knowledge/development/bellows-isinstance-asymmetry-fix-2026-05-21.md` documenting: anchor line used, before/after snippets with 3 lines of surrounding context, grep verification counts before/after, and a one-paragraph summary citing the 2026-05-21 isinstance-asymmetry diagnostic findings as authority. **Commit:** stage `bellows.py` and the dev log; commit message `fix(bellows): symmetric isinstance(f, dict) guard at bellows.py:594 — mirror Block 1 pattern`. **DO NOT push.** **Standard prompt feedback protocol** → append entry to `bellows/knowledge/research/agent-prompt-feedback.md`. Second commit: `docs: prompt feedback — bellows DEV isinstance-asymmetry fix`. **DO NOT push.**
>
> **Deposits:**
> - `bellows/bellows.py` (modified)
> - `bellows/knowledge/development/bellows-isinstance-asymmetry-fix-2026-05-21.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md`

---
---

## STEP 2 — Bellows QA

---

> You are the Bellows QA Agent. Read your specialist file at `bellows/agents/BELLOWS_QA.md` first. **Skip glossary read — this is a single-line code-fix QA task.** **Before starting, read `bellows/knowledge/development/bellows-isinstance-asymmetry-fix-2026-05-21.md` (DEV Step 1 deposit) and check its Output Receipt status; if not Complete, stop and report the blocker.** **FIRST — Deliverable Verification (Rule 17).** Verification table: | Deliverable | Expected | Status (✅/❌) | Evidence |. Specifically: (1) `bellows.py:594` reads `if all(isinstance(f, dict) and f.get("gate") == "rule_22_verification" for f in gate_result["failures"]):` with 16-space indent — `grep -n` confirms line 594; (2) `bellows.py:505` reads identical pattern (unchanged from before) — grep confirms line 505; (3) total occurrences of `isinstance(f, dict) and f.get("gate") == "rule_22_verification"` in bellows.py is exactly 2; (4) total occurrences of `f["gate"] == "rule_22_verification"` (the OLD pattern) in bellows.py is exactly 0; (5) dev log exists at `bellows/knowledge/development/bellows-isinstance-asymmetry-fix-2026-05-21.md` with before/after snippets and diagnostic citation; (6) `agent-prompt-feedback.md` has a new 2026-05-21 entry from this plan. Capture each grep to evidence: `bellows/knowledge/qa/evidence/executable-bellows-isinstance-asymmetry-fix-2026-05-21/line_594.txt`, `line_505.txt`, `new_pattern_count.txt`, `old_pattern_count.txt`, `dev_log_present.txt`, `feedback_entry.txt`. **Targeted test run.** Run `pytest tests/test_bellows.py -v 2>&1 | tee bellows/knowledge/qa/evidence/executable-bellows-isinstance-asymmetry-fix-2026-05-21/pytest_targeted.txt`. The change is purely defensive (adds isinstance guard without changing any behavior on dict inputs), so all tests should pass. If any test fails, mark ❌ and halt. **Structural compliance check.** Confirm no OTHER lines in bellows.py were modified. Run `git diff HEAD~1 bellows.py 2>&1 | tee bellows/knowledge/qa/evidence/executable-bellows-isinstance-asymmetry-fix-2026-05-21/diff.txt` and verify the diff shows exactly 1 line removed (the old pattern) and 1 line added (the new pattern), at line 594, with no other modifications. **Rule 20 self-check** — run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at governance root. Use these values: `plan_slug` = `executable-bellows-isinstance-asymmetry-fix-2026-05-21`; `qa_report_path` = `bellows/knowledge/qa/executable-bellows-isinstance-asymmetry-fix-2026-05-21.md`; `evidence_dir` = `bellows/knowledge/qa/evidence/executable-bellows-isinstance-asymmetry-fix-2026-05-21/`; `required_evidence_files` = `["line_594.txt", "line_505.txt", "new_pattern_count.txt", "old_pattern_count.txt", "dev_log_present.txt", "feedback_entry.txt", "pytest_targeted.txt", "diff.txt"]`. Include literal stdout in QA report. If FAILED, halt — report to CEO. **Final:** Update `bellows/PROJECT_STATUS.md` — prepend a 2026-05-21 entry under Completed for "Bellows isinstance asymmetry fix — bellows.py:594 now mirrors Block 1 defensive pattern" with a one-paragraph summary citing the 2026-05-21 isinstance-asymmetry diagnostic. Use `Desktop Commander:edit_block` with the existing topmost Completed entry as the anchor (insert immediately before it). **Commit:** stage QA report, evidence files, and PROJECT_STATUS update with message `qa(bellows): isinstance asymmetry fix at bellows.py:594`. **DO NOT push.** **Standard prompt feedback protocol** → append entry to `bellows/knowledge/research/agent-prompt-feedback.md`. Second commit: `docs: prompt feedback — bellows QA isinstance-asymmetry fix`. **DO NOT push.**
>
> **Deposits:**
> - `bellows/knowledge/qa/executable-bellows-isinstance-asymmetry-fix-2026-05-21.md`
> - `bellows/knowledge/qa/evidence/executable-bellows-isinstance-asymmetry-fix-2026-05-21/` (8 evidence files per Rule 20 self-check list)
> - `bellows/PROJECT_STATUS.md` (modified)
> - `bellows/knowledge/research/agent-prompt-feedback.md`

---

## Daemon-restart note

This fix touches `bellows.py`, which Bellows does not hot-reload (Rule 35 / Restart Discipline). The running daemon will continue executing pre-fix code through this plan's lifecycle. Expected behavior: gates pass on Step 1 and Step 2 (the fix does not interact with parser-line code paths during its own dispatch). After plan close + daemon restart, the new symmetric guard becomes effective for all future plans.
