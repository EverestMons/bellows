# Bellows — Gate file-scoping fixes: Shape 6C (rule_22 table scoping + status tokens) + Shape 7A (rule_20 scope to first .md)
**Date:** 2026-05-24 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** full | **Execution:** Step 1 (DEV) → Step 2 (QA) | **pause_for_verdict:** after_step_1 | **auto_close:** false

## Context

Per the 2026-05-24 gate-file-scoping diagnostic at `bellows/knowledge/architecture/gate-file-scoping-2026-05-24.md`, BACKLOG items #6 and #7 are independent bugs (different code regions, different mechanisms) but both contribute to QA-step gate false-positives. This executable ships both fixes together because they're disjoint code changes in adjacent gate functions — Shape 6C in `_gate_rule_22_verification`, Shape 7A in `_gate_rule_20_self_check` — with no interaction risk.

**Item #6 (Shape 6C) — Combined table-section scoping + status-token broadening:**

Two contributing defects in `_gate_rule_22_verification`'s (c) check at `gates.py:507-528`:
1. **No table-type classification.** The line-by-line state machine inspects every markdown table in the QA report, including non-verification tables (failure-classification tables, test-result tables, structural-compliance tables) that have no status column by design.
2. **Status-token limitation.** The (c) check accepts only `\u2705` (✅) as positive status. Text tokens like "PASS" are ignored, despite `_is_positive_status_row()` at `gates.py:62-76` already supporting them with bounded cell-equality matching.

Shape 6C addresses both: (a) track current section via `## <header>` lines; only inspect tables inside sections whose header contains "verification" (case-insensitive); (b) replace the `\u2705` substring check with a call to `_is_positive_status_row()` which accepts `\u2705` plus `OK`, `PASS`, `done`, `complete`, `verified`.

**Item #7 (Shape 7A) — Scope rule_20 banner scan to first `.md` deposit:**

`_gate_rule_20_self_check` at `gates.py:432-458` iterates ALL `.md` deposit paths looking for the Rule 20 banner. When a non-QA file (e.g., `agent-prompt-feedback.md`) is listed as a deposit and contains the banner text as incidental prose, the gate matches on it and fails with "banner present but PASSED line missing." Shape 7A harmonizes with `_gate_rule_22_verification`'s pattern (which selects `md_paths[0]` as the QA report) by scoping the banner scan to only the first `.md` deposit.

**Why ship both together:** disjoint code regions (`gates.py:507-528` vs `gates.py:432-458`), similar test-fixture shape (multi-table and multi-deposit QA fixtures), no interaction risk per the diagnostic Section D15. Single DEV→QA pass instead of two.

**What gets changed (Planner-verified by reading the live file before authoring):**

| File | Site | Change |
|---|---|---|
| `gates.py:432-458` | `_gate_rule_20_self_check` banner loop | Replace `for dep_path in md_paths:` with single-file check on `md_paths[0]` |
| `gates.py:507-528` | `_gate_rule_22_verification` (c) check | Track section via `## <header>`; only inspect tables inside "verification" sections; replace `\u2705 not in stripped` with `_is_positive_status_row(line)` call |

**What stays unchanged:**

- `_extract_step_text`, `_extract_plan_required_deposits`, `_resolve_deposit_path` — path resolution pipeline works correctly per diagnostic Section A.
- `_is_positive_status_row` at `gates.py:62-76` — used as-is, no signature changes.
- `POSITIVE_STATUS_TOKENS` at `gates.py:57` — unchanged.
- The (a) "deposits exist" and (d) "no hedging in positive rows" checks within `_gate_rule_22_verification` — unchanged.
- Rule 20's "banner not found at all" failure path — preserved.
- Rule 20's PASSED-line regex check — unchanged.

**Backward compatibility:**

- Shape 6C with section scoping: a QA report with NO section header containing "verification" will skip the (c) check entirely (`in_verification_section` stays False throughout). This is a deliberate trade-off: if a future QA template uses a different section name, the gate fails open (no false positives) rather than fail closed. Test coverage verifies this fallback.
- Shape 6C with status tokens: the existing `\u2705` semantics are preserved — adding "PASS"/"OK"/etc. is purely additive. Rows that already passed with ✅ continue to pass.
- Shape 7A: scoping to `md_paths[0]` matches the pre-2026-05-10 historical behavior (before iteration was added). The "iterate all .md deposits" expansion has no documented prior plan or test that depends on it; it appears to have been written that way without specific reason.

**Acknowledged scope:**

- This executable does NOT address BACKLOG items #4, #8, #10, #11 (other hardening items). Those are independent issues in different code families.
- Shape 7B (structural-context banner check) from the diagnostic is NOT included — it's additional hardening but feature-shaped (adds a new check). Deferred per current hardening discipline.

**Daemon-restart note:** This fix touches `gates.py`, which Bellows does not hot-reload. The running daemon will continue executing pre-fix code through this plan's lifecycle. After plan close + daemon restart, the new gate behaviors become effective for all future QA steps.

## Execution Map

```
Step 1 (DEV) → Step 2 (QA)
```

Sequential. Step 1 changes `gates.py` (two disjoint functions), adds regression tests, commits everything as one atomic commit, deposits dev log. Step 2 verifies and runs full pytest.

---
---

## STEP 1 — Bellows Developer

---

> You are the Bellows Developer. Read your specialist file at `agents/BELLOWS_DEVELOPER.md` first. **Skip glossary read — this is a precise code-change task on two adjacent gate functions.** **Authority:** the 2026-05-24 gate-file-scoping diagnostic at `knowledge/architecture/gate-file-scoping-2026-05-24.md`. Read Section A (joint file resolution), Section B (item #6 mechanism), Section C (item #7 mechanism), Section E18 (Shape 6C), and Section E19 (Shape 7A) before editing. **PATH CONVENTION: bare paths in all commands. Your cwd is the bellows project root within your worktree. Do NOT prefix paths with `bellows/`. Do NOT `cd bellows`. Files are at `gates.py`, `tests/test_*.py`, `knowledge/...` — bare, relative to cwd.**
>
> **Pre-edit verification.** Confirm the expected starting state. Run each check and confirm the listed expected output. If any check fails, STOP — deposit a flag at `knowledge/flags/state-mismatch-gate-file-scoping-2026-05-24-step-1.md` documenting actual output, and halt.
> - Check (i): `grep -n 'def _gate_rule_20_self_check' gates.py` — expected: one match at ~line 414.
> - Check (ii): `grep -n 'def _gate_rule_22_verification' gates.py` — expected: one match at ~line 468.
> - Check (iii): `grep -n 'def _is_positive_status_row' gates.py` — expected: one match at ~line 62.
> - Check (iv): `grep -n 'for dep_path in md_paths' gates.py` — expected: one match in `_gate_rule_20_self_check` at ~line 432.
> - Check (v): `grep -c '"\\\\u2705" not in stripped' gates.py` — expected: exactly 1 (the (c) check predicate). Note: depending on grep escaping, this may also be verifiable as `grep -n 'u2705. not in stripped' gates.py` or by reading the function directly.
> - Check (vi): `python3 -c "import gates"` from cwd — expected: clean exit (urllib3 SSL warning is fine).
> - Check (vii): `python3 -m pytest tests/test_gates.py -q 2>&1 | tail -5` — expected: passes cleanly. Capture baseline.
>
> **Task A — Shape 7A: scope `_gate_rule_20_self_check` to first `.md` deposit.**
>
> Use `Desktop Commander:edit_block` with this anchor. Match exactly (preserve indentation):
>
> `old_string`:
> ```
>     banner = "Rule 20 — QA Self-Check Results"
>     banner_found_path = None
>
>     for dep_path in md_paths:
>         resolved = _resolve_deposit_path(dep_path, project_path, wt_path=wt_path)
>         if resolved is None:
>             failures.append({"gate": "rule_20_self_check", "evidence": f"deposit file unreadable: {dep_path} (file not found)"})
>             continue
>
>         try:
>             with open(resolved, "r", encoding="utf-8") as f:
>                 content = f.read()
>         except (FileNotFoundError, UnicodeDecodeError, OSError) as e:
>             failures.append({"gate": "rule_20_self_check", "evidence": f"deposit file unreadable: {dep_path} ({e})"})
>             continue
>
>         if banner not in content:
>             continue
>
>         # Banner found — scan ALL remaining content for the PASSED line, tolerating
>         # whitespace, decoration lines, and fenced-block indentation.
>         # Per LESSONS 2026-05-17 strike-3 and 2026-05-18 strike-5 entries.
>         banner_pos = content.index(banner)
>         remaining = content[banner_pos:]
>         # The PASSED line may be anywhere in the remaining content, optionally
>         # preceded by whitespace on its line. Use re.MULTILINE so ^ matches each
>         # line start, and \s* tolerates leading indentation/whitespace.
>         if re.search(r'^\s*\*{0,2}\s*PASSED\s+—\s+SELF-CHECK\s+PASSED', remaining, re.MULTILINE):
>             return  # Gate passes
>         banner_found_path = dep_path
>
>     if banner_found_path:
>         failures.append({"gate": "rule_20_self_check", "evidence": f"banner present but PASSED line missing in {banner_found_path}"})
>     else:
>         # Only reach here if no deposit had the banner (and no unreadable errors already appended)
>         if not any(f.get("gate") == "rule_20_self_check" for f in failures):
>             failures.append({"gate": "rule_20_self_check", "evidence": "no QA deposit contains Rule 20 self-check banner"})
> ```
>
> `new_string`:
> ```
>     banner = "Rule 20 — QA Self-Check Results"
>
>     # Item #7 fix (2026-05-24, Shape 7A): scope banner scan to the QA report (first .md deposit),
>     # matching the pattern used by _gate_rule_22_verification. Previously iterated ALL md_paths,
>     # which caused false-positives when a non-QA deposit (e.g., agent-prompt-feedback.md)
>     # contained the banner text as incidental prose.
>     qa_report_path = md_paths[0]
>     resolved = _resolve_deposit_path(qa_report_path, project_path, wt_path=wt_path)
>     if resolved is None:
>         failures.append({"gate": "rule_20_self_check", "evidence": f"deposit file unreadable: {qa_report_path} (file not found)"})
>         return
>
>     try:
>         with open(resolved, "r", encoding="utf-8") as f:
>             content = f.read()
>     except (FileNotFoundError, UnicodeDecodeError, OSError) as e:
>         failures.append({"gate": "rule_20_self_check", "evidence": f"deposit file unreadable: {qa_report_path} ({e})"})
>         return
>
>     if banner not in content:
>         failures.append({"gate": "rule_20_self_check", "evidence": "no QA deposit contains Rule 20 self-check banner"})
>         return
>
>     # Banner found — scan ALL remaining content for the PASSED line, tolerating
>     # whitespace, decoration lines, and fenced-block indentation.
>     # Per LESSONS 2026-05-17 strike-3 and 2026-05-18 strike-5 entries.
>     banner_pos = content.index(banner)
>     remaining = content[banner_pos:]
>     # The PASSED line may be anywhere in the remaining content, optionally
>     # preceded by whitespace on its line. Use re.MULTILINE so ^ matches each
>     # line start, and \s* tolerates leading indentation/whitespace.
>     if re.search(r'^\s*\*{0,2}\s*PASSED\s+—\s+SELF-CHECK\s+PASSED', remaining, re.MULTILINE):
>         return  # Gate passes
>     failures.append({"gate": "rule_20_self_check", "evidence": f"banner present but PASSED line missing in {qa_report_path}"})
> ```
>
> **Task B — Shape 6C: section scoping + broadened status tokens in `_gate_rule_22_verification` (c) check.**
>
> Use `Desktop Commander:edit_block` with this anchor. Match exactly:
>
> `old_string`:
> ```
>     lines = content.splitlines()
>
>     # (c) Verification table: no ❌ rows, no data rows missing ✅
>     in_data = False
>     for i, line in enumerate(lines, 1):
>         stripped = line.strip()
>         if "|" not in stripped:
>             in_data = False
>             continue
>         if _TABLE_SEPARATOR_RE.match(stripped):
>             in_data = True
>             continue
>         if not in_data:
>             continue  # Header row
>         # Data row
>         if "\u274c" in stripped:
>             failures.append({
>                 "gate": "rule_22_verification",
>                 "evidence": f"(c) QA verification table row {i}: {stripped[:120]}. See {qa_report_path} line {i}.",
>             })
>         elif "\u2705" not in stripped:
>             failures.append({
>                 "gate": "rule_22_verification",
>                 "evidence": f"(c) QA verification table row {i} missing status: {stripped[:120]}. See {qa_report_path} line {i}.",
>             })
> ```
>
> `new_string`:
> ```
>     lines = content.splitlines()
>
>     # (c) Verification table: no ❌ rows, no data rows missing a positive status.
>     # Item #6 fix (2026-05-24, Shape 6C):
>     #   (a) Section-scoped: only inspect tables inside sections whose ## header contains
>     #       "verification" (case-insensitive). QA reports contain non-verification tables
>     #       (failure classifications, commit stats) that should not be inspected.
>     #   (b) Status-token broadened: use _is_positive_status_row() which accepts ✅ AND
>     #       text tokens (PASS, OK, done, complete, verified) with bounded cell equality.
>     #       Previously accepted only ✅ as positive status, false-positiving on rows like
>     #       "| ... | PASS |".
>     in_data = False
>     in_verification_section = False
>     for i, line in enumerate(lines, 1):
>         stripped = line.strip()
>         # Track section transitions via ## headers.
>         if stripped.startswith("## "):
>             in_verification_section = "verification" in stripped.lower()
>             in_data = False
>             continue
>         if "|" not in stripped:
>             in_data = False
>             continue
>         if _TABLE_SEPARATOR_RE.match(stripped):
>             in_data = True
>             continue
>         if not in_data:
>             continue  # Header row
>         if not in_verification_section:
>             continue  # Skip tables outside verification sections
>         # Data row inside a verification-section table
>         if "\u274c" in stripped:
>             failures.append({
>                 "gate": "rule_22_verification",
>                 "evidence": f"(c) QA verification table row {i}: {stripped[:120]}. See {qa_report_path} line {i}.",
>             })
>         elif not _is_positive_status_row(line):
>             failures.append({
>                 "gate": "rule_22_verification",
>                 "evidence": f"(c) QA verification table row {i} missing status: {stripped[:120]}. See {qa_report_path} line {i}.",
>             })
> ```
>
> **Task C — post-edit verification.** Run each:
> - `python3 -c "import gates"` from cwd — expected: clean exit. If import fails, paste traceback into `knowledge/flags/import-failure-gate-file-scoping-2026-05-24-step-1.md` and halt.
> - `grep -c 'Item #7 fix (2026-05-24, Shape 7A)' gates.py` — expected: 1 match (the comment in `_gate_rule_20_self_check`).
> - `grep -c 'Item #6 fix (2026-05-24, Shape 6C)' gates.py` — expected: 1 match (the comment in `_gate_rule_22_verification`).
> - `grep -c 'for dep_path in md_paths' gates.py` — expected: 0 matches (the iteration was removed; rule_22 already used `md_paths[0]` not a loop).
> - `grep -c '_is_positive_status_row(line)' gates.py` — expected: at least 1 match in `_gate_rule_22_verification`. Note: `_is_positive_status_row` is also called in the (d) check, so this grep may return 2 matches.
> - `grep -c 'in_verification_section' gates.py` — expected: 3 matches (init, header-line tracking, predicate check).
>
> **Task D — add regression tests.** Add tests to `tests/test_gates.py`. The exact test names and minimum scenarios:
>
> **For Shape 7A (rule_20_self_check):**
> 1. `test_rule_20_self_check_scopes_to_first_md_deposit_ignoring_incidental_banner_in_other_deposits` — Plan with two `.md` deposits: a QA report (has valid banner + PASSED line) and a feedback file (contains the literal banner text in prose but no PASSED line). Gate should pass (only inspects the first deposit, which is the QA report). This is the direct item #7 regression.
> 2. `test_rule_20_self_check_fails_when_first_md_deposit_lacks_passed_line` — Plan with QA report deposit that has banner but no PASSED line. Gate should fail with "banner present but PASSED line missing" referencing the QA report path. This verifies the surviving failure mode.
>
> **For Shape 6C (rule_22_verification (c)):**
> 3. `test_rule_22_verification_c_skips_non_verification_section_tables` — QA report with: a verification section table (all rows have ✅), a "Test Failures" section table (3 columns: Name | Classification | Notes, no status column). Gate should pass (only inspects the verification table). This is the direct item #6 regression case from the 2026-05-24 reproduction.
> 4. `test_rule_22_verification_c_accepts_text_pass_status` — QA report with verification section containing a table where the final column has text "PASS" instead of ✅ in every row. Gate should pass (recognizes "PASS" via `_is_positive_status_row`). This is the direct item #6 regression case from the 2026-05-22 reproduction.
> 5. `test_rule_22_verification_c_flags_genuine_missing_status_in_verification_table` — QA report with verification section table where one row has neither ✅ nor a text positive status nor ❌. Gate should flag that specific row. This verifies the surviving failure mode is preserved.
>
> Use existing test fixtures and patterns in `tests/test_gates.py` as scaffolding — search for `def test_rule_22_` and `def test_rule_20_` for working patterns. Each test should be self-contained, creating its QA report content as a string and using `tmp_path` for file I/O. If you cannot reliably scaffold ANY test, STOP — deposit a flag at `knowledge/flags/test-fixture-blocking-gate-file-scoping-2026-05-24-step-1.md` and halt.
>
> **Task E — run full pytest to verify no regressions.** Run `python3 -m pytest 2>&1 | tee /tmp/pytest_gate_file_scoping.txt` and confirm: (a) all 5 new tests pass, (b) pre-existing carry-over failures stay carry-over (4 `test_decisions.py` worktree artifacts + 1 `test_run_step_timeout`), (c) no NEW failures appear elsewhere. **Particularly important:** verify that existing `test_rule_22_*` and `test_rule_20_*` tests still pass — these are the tests that confirm the existing behavior is preserved. If any existing test fails, STOP — paste pytest tail into a flag at `knowledge/flags/regression-gate-file-scoping-2026-05-24-step-1.md` and halt.
>
> **Task F — deposit dev log.** Write to `knowledge/development/gate-file-scoping-2026-05-24.md` documenting:
> - (a) Pre-edit verification stdout for all 7 checks
> - (b) Before/after snippets for both edit sites (Shape 7A and Shape 6C) with ~5 lines context each
> - (c) The 5 new test function names with one-line description each (2 for Shape 7A, 3 for Shape 6C)
> - (d) Task C post-edit verification stdout
> - (e) Task E pytest summary (test counts: passed, failed, skipped)
> - (f) One-paragraph summary citing the 2026-05-24 gate-file-scoping diagnostic as authority, identifying which BACKLOG items this closes (#6 and #7), and noting that Shape 7B (structural-context banner check) was deferred as feature-shaped hardening.
>
> **Task G — commit everything as ONE commit.** Stage `gates.py`, `tests/test_gates.py`, and the dev log. Verify with `git status --porcelain` that exactly these three paths are staged. Commit with message `fix(gates): section-scoped table inspection + status tokens + rule_20 first-deposit scoping (items #6, #7)`. **DO NOT push.**
>
> **Standard prompt feedback protocol** → append entry to `knowledge/research/agent-prompt-feedback.md`. Note any observations about: (1) test fixture patterns for multi-table or multi-deposit QA reports (these are new test shapes), (2) whether the section-tracking state machine integrated cleanly with the existing in_data/separator-line state, (3) whether `_is_positive_status_row()` substitution preserved all existing (c)-check test expectations. Second commit: `docs: prompt feedback — bellows DEV gate file scoping`. **DO NOT push.**
>
> **Deposits:**
> - `bellows/gates.py` (modified)
> - `bellows/tests/test_gates.py` (modified)
> - `bellows/knowledge/development/gate-file-scoping-2026-05-24.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md`

---
---

## STEP 2 — Bellows QA

---

> You are the Bellows QA Agent. Read your specialist file at `agents/BELLOWS_QA.md` first. **Skip glossary read — this is a gate-fix QA task.** **PATH CONVENTION: bare paths in all commands. Your cwd is the bellows project root within your worktree. Do NOT prefix paths with `bellows/`. Do NOT `cd bellows`. Files are at `gates.py`, `tests/test_*.py`, `knowledge/...` — bare, relative to cwd.**
>
> **Before starting, read `knowledge/development/gate-file-scoping-2026-05-24.md` (DEV Step 1 deposit) and check its Output Receipt status; if not Complete, stop and report the blocker.**
>
> **FIRST — Deliverable Verification (Rule 17).** Build a verification table inside a `## Deliverable Verification` section so the new section-scoped (c) check correctly inspects it on this QA step. Capture each grep to evidence under `knowledge/qa/evidence/executable-gate-file-scoping-2026-05-24/`. Verifications:
> 1. `grep -c 'Item #7 fix (2026-05-24, Shape 7A)' gates.py` returns 1 — evidence `shape_7a_comment.txt`
> 2. `grep -c 'Item #6 fix (2026-05-24, Shape 6C)' gates.py` returns 1 — evidence `shape_6c_comment.txt`
> 3. `grep -c 'for dep_path in md_paths' gates.py` returns 0 (rule_20 no longer iterates) — evidence `rule_20_iteration_removed.txt`
> 4. `grep -c 'in_verification_section' gates.py` returns 3 (init, header tracking, predicate check) — evidence `in_verification_section_present.txt`
> 5. `grep -c '_is_positive_status_row(line)' gates.py` returns at least 1 (now used by both (c) and (d) checks) — evidence `is_positive_status_row_used.txt`
> 6. `python3 -c "import gates"` exits cleanly — evidence `import_smoke.txt`
> 7. The 5 new test functions exist: `grep -n 'def test_rule_20_self_check_scopes_to_first_md_deposit_ignoring_incidental_banner_in_other_deposits\|def test_rule_20_self_check_fails_when_first_md_deposit_lacks_passed_line\|def test_rule_22_verification_c_skips_non_verification_section_tables\|def test_rule_22_verification_c_accepts_text_pass_status\|def test_rule_22_verification_c_flags_genuine_missing_status_in_verification_table' tests/test_gates.py` returns 5 matches — evidence `new_tests_present.txt`
> 8. Dev log exists at `knowledge/development/gate-file-scoping-2026-05-24.md` with all six documentation items (a-f) — evidence `dev_log_present.txt`
> 9. `agent-prompt-feedback.md` has a new 2026-05-24 entry from DEV — evidence `feedback_entry.txt`
>
> **Full pytest suite (Test Scope: full).** Run `python3 -m pytest 2>&1 | tee knowledge/qa/evidence/executable-gate-file-scoping-2026-05-24/pytest_full.txt`. Expected: all tests pass EXCEPT pre-existing carry-over failures (4 `test_decisions.py` + 1 `test_run_step_timeout`). The 5 new tests should pass. **Particularly important — verify existing tests are unchanged:** all `test_rule_22_*` and `test_rule_20_*` tests must pass. If any existing test fails, mark ❌ and halt — the section-scoping or status-token change has caused a regression. Capture pytest summary line to evidence file.
>
> **Structural compliance check.** Identify the DEV commit SHA (the code-change commit, NOT the prompt-feedback commit). Run `git --no-pager show --stat <DEV-commit-sha> 2>&1 | tee knowledge/qa/evidence/executable-gate-file-scoping-2026-05-24/dev_commit.txt` and confirm exactly three paths in the commit: `gates.py`, `tests/test_gates.py`, and `knowledge/development/gate-file-scoping-2026-05-24.md`. Run `git --no-pager show <DEV-commit-sha> -- gates.py 2>&1 | tee knowledge/qa/evidence/executable-gate-file-scoping-2026-05-24/diff_gates.txt`. The diff should show: (i) two regions modified — `_gate_rule_20_self_check` (around line 432) and `_gate_rule_22_verification` (around line 507); (ii) Shape 7A reduces lines (loop removed, replaced with single-file logic); (iii) Shape 6C adds lines (in_verification_section state, header-tracking branch, status-token call). The net change is a mix of additions and deletions. There should be NO modifications outside `_gate_rule_20_self_check` and `_gate_rule_22_verification`. If diff shows changes elsewhere in `gates.py`, mark ❌ and halt.
>
> **Rule 20 self-check** — run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at governance root. Use these values:
> - `plan_slug` = `executable-gate-file-scoping-2026-05-24`
> - `qa_report_path` = `knowledge/qa/executable-gate-file-scoping-2026-05-24.md`
> - `evidence_dir` = `knowledge/qa/evidence/executable-gate-file-scoping-2026-05-24/`
> - `required_evidence_files` = `["shape_7a_comment.txt", "shape_6c_comment.txt", "rule_20_iteration_removed.txt", "in_verification_section_present.txt", "is_positive_status_row_used.txt", "import_smoke.txt", "new_tests_present.txt", "dev_log_present.txt", "feedback_entry.txt", "pytest_full.txt", "dev_commit.txt", "diff_gates.txt"]`
>
> Include literal stdout in QA report. If FAILED, halt — report to CEO.
>
> **Final.** Update `PROJECT_STATUS.md` — prepend a 2026-05-24 entry under Completed for "Gate file-scoping fixes (Shape 6C + 7A) — closes BACKLOG items #6 (rule_22 table false-positive) and #7 (rule_20 wrong file)" with a one-paragraph summary citing the 2026-05-24 gate-file-scoping diagnostic as authority. Use `Desktop Commander:edit_block` with the existing topmost Completed entry as the anchor (insert immediately before it). **Commit:** stage QA report, evidence files, and `PROJECT_STATUS.md` update with message `qa(bellows): gate file-scoping fixes`. **DO NOT push.**
>
> **Standard prompt feedback protocol** → append entry to `knowledge/research/agent-prompt-feedback.md`. Second commit: `docs: prompt feedback — bellows QA gate file scoping`. **DO NOT push.**
>
> **Deposits:**
> - `bellows/knowledge/qa/executable-gate-file-scoping-2026-05-24.md`
> - `bellows/knowledge/qa/evidence/executable-gate-file-scoping-2026-05-24/` (12 evidence files per Rule 20 self-check list)
> - `bellows/PROJECT_STATUS.md` (modified)
> - `bellows/knowledge/research/agent-prompt-feedback.md`
