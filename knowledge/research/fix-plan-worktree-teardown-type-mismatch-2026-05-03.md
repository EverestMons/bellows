# Bellows — Worktree Teardown Type-Mismatch Fix
**Date:** 2026-05-03 | **Tier:** Small | **Test Scope:** targeted | **Run mode:** Manual bootstrap (Bellows must NOT dispatch this plan) | **Execution:** Step 1 (BELLOWS DEVELOPER) → Step 2 (BELLOWS QA)

## Status: SHIPPED 2026-05-03

Both steps complete and Rule 22 verified by Planner. Fix landed at commit `272fbe4`. QA report at `knowledge/qa/worktree-teardown-type-mismatch-fix-qa-report-2026-05-03.md` (commit `0f2059f`). Bellows daemon must be restarted for the new code to take effect on future dispatches. See BACKLOG.md for downstream items: monorepo-worktree-at-governance-root structural fix (deferred), `origin/HEAD` setup for 3 projects (one-line CEO action), and post-fix canary diagnostic (recommended next session).

## Plan Origin and Run Constraint

This plan fixes the type-contract violation between `bellows.py` and `verdict.py` identified by `bellows/knowledge/research/worktree-teardown-bug-diagnosis-2026-05-03.md`. Four sites in `bellows.py` append plain strings to `gate_result["failures"]`; `verdict.py`'s `post_verdict_request` then iterates that list expecting dicts and crashes with `string indices must be integers`. The fix is mechanical — change the four call sites to append dicts instead.

**This plan must NOT be dispatched by Bellows.** Reason: dispatching it would create a worktree of the bellows project, and bellows has no own `.git` (the monorepo trap from Q2 of the diagnosis). The dispatch would land in the same crash-on-teardown state that yesterday's plan did. Run mode is therefore manual bootstrap in Claude Code. The plan file lives in `bellows/knowledge/research/` — an unwatched directory — so Bellows cannot auto-claim it. The `fix-plan-` filename prefix also doesn't match Bellows's runnable-plan regex (`executable-` / `diagnostic-` / `parallel-N-`).

**Bootstrap (paste into Claude Code from any cwd):**
```
Read the plan at /Users/marklehn/Desktop/GitHub/bellows/knowledge/research/fix-plan-worktree-teardown-type-mismatch-2026-05-03.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2.
```

After Step 1 completes and CEO confirms, paste:
```
Continue with Step 2 of the same plan.
```

After Step 2 completes, the Planner reads the QA report directly per Rule 22, then performs housekeeping manually (move plan to a permanent home, update PROJECT_STATUS).

---
---

## STEP 1 — BELLOWS DEVELOPER

---

> You are the Bellows Developer. Read your specialist file at `/Users/marklehn/Desktop/GitHub/bellows/agents/BELLOWS_DEVELOPER.md` first. Skip glossary read — this is a mechanical type-format fix.
>
> **Context.** The diagnosis at `/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/worktree-teardown-bug-diagnosis-2026-05-03.md` identified a type-contract violation: `bellows.py` appends plain strings (e.g., `f"worktree_teardown_failed: {e}"`) to `gate_result["failures"]`, but `verdict.py`'s `post_verdict_request` iterates failures as dicts (`f['gate']`, `f['evidence']`). Diagnosis enumerated three sites; Planner verification surfaced a fourth. All four sites must be fixed.
>
> **The four sites in `/Users/marklehn/Desktop/GitHub/bellows/bellows.py`:** Use `grep -n 'worktree_teardown_failed\|worktree_creation_failed' /Users/marklehn/Desktop/GitHub/bellows/bellows.py` to locate them. Expected matches (line numbers approximate, may have drifted): one `worktree_creation_failed` site in the `_create_worktree` failure exception handler (~line 318), and three `worktree_teardown_failed` sites in (a) the mid-step pause path (~line 340), (b) the final-step pause path (~line 405), and (c) the auto-close path (~line 433). Confirm count = 4 before editing. If grep shows fewer or more matches, STOP and report the discrepancy — do not guess.
>
> **The fix.** At each of the four sites, replace the string append with a dict append matching the `verdict.py` contract:
>
> Replace:
> ```python
> gate_result["failures"].append(f"worktree_teardown_failed: {e}")
> ```
> With:
> ```python
> gate_result["failures"].append({"gate": "worktree_teardown", "evidence": str(e)})
> ```
>
> And replace:
> ```python
> "failures": [f"worktree_creation_failed: {e}"]
> ```
> With:
> ```python
> "failures": [{"gate": "worktree_creation", "evidence": str(e)}]
> ```
>
> The `gate` value is `worktree_teardown` for the three teardown sites and `worktree_creation` for the creation site — distinct names because they represent different gate concepts even though the format is shared. The `evidence` value is `str(e)` to match `post_verdict_request`'s expectation that evidence is a string.
>
> **Verify the contract on the consumer side.** Before editing, read `/Users/marklehn/Desktop/GitHub/bellows/verdict.py` and locate `post_verdict_request`. Find the loop that iterates `gate_result["failures"]` (the failing line is something like `failures_text += f"- **{f['gate']}**: {f['evidence']}\n"`). Confirm the dict shape `{"gate": ..., "evidence": ...}` is what the consumer expects. If the consumer expects different keys, STOP and report — the diagnosis cited `f['gate']` and `f['evidence']`, but consumer code may have evolved.
>
> **Add a regression test.** In the test file that covers `verdict.py` (locate via `grep -rn 'post_verdict_request' /Users/marklehn/Desktop/GitHub/bellows/tests/` — likely `tests/test_verdict.py` or similar), add ONE new test that:
>
> 1. Constructs a `gate_result` dict matching what `bellows.py` produces when teardown fails, using the dict-format failure entry: `{"failures": [{"gate": "worktree_teardown", "evidence": "simulated teardown error"}], "files_changed": [], "passed": False, "is_qa_step": False}`.
> 2. Calls `post_verdict_request` with `pause_reason="gate_failure"` and the gate_result above (along with whatever other args are required — refer to existing tests for the call signature).
> 3. Asserts `post_verdict_request` does NOT raise `TypeError` (the symptom of the original bug).
> 4. Reads the verdict-request file the call deposits and asserts the `## Gate Failures` section contains a line matching `worktree_teardown` and `simulated teardown error` (substring match — proves the consumer parsed the dict correctly).
> 5. Cleans up the deposited verdict-request file at end of test (use a tmp_path fixture if pytest, or a teardown that deletes the file).
>
> Test name: `test_post_verdict_request_handles_worktree_teardown_failure_dict_format`. Place it adjacent to existing `post_verdict_request` tests. Use existing fixtures and helpers — do not invent new infrastructure.
>
> **Run targeted tests.** After editing, run `cd /Users/marklehn/Desktop/GitHub/bellows && python3 -m pytest tests/test_verdict.py tests/test_bellows.py -v 2>&1 | tee /tmp/pytest-targeted-fix.txt`. Confirm the new test passes AND no existing tests in those files regressed. If anything fails, do NOT proceed to commit — report the failure and stop.
>
> **Commit.** When tests pass, commit:
> - `bellows.py` — the four-site fix
> - the test file — the new regression test
>
> Commit message: `fix(bellows): use dict format for worktree failure entries (4 sites)\n\nbellows.py appended plain strings to gate_result['failures'], but verdict.py's post_verdict_request iterates failures expecting dict format ({gate, evidence}). Mismatch crashed teardown with 'string indices must be integers' on 2026-05-03 close of executable-close-2026-05-03-step-count-regression-2026-05-03 (BACKLOG entry). Fixed all 4 sites: 3 worktree_teardown_failed (lines ~340, ~405, ~433) and 1 worktree_creation_failed (line ~318). Added regression test covering the contract.\n\nDiagnosis: knowledge/research/worktree-teardown-bug-diagnosis-2026-05-03.md`
>
> Commit from `/Users/marklehn/Desktop/GitHub/bellows/` (bellows repo, NOT governance-root — this fix is bellows-local code).
>
> **Deposit a dev log** at `/Users/marklehn/Desktop/GitHub/bellows/knowledge/development/worktree-teardown-type-mismatch-fix-dev-log-2026-05-03.md` with: which 4 sites were edited (with final line numbers), the consumer contract verification, the new test description, the commit SHA, and a standard Output Receipt.
>
> **Standard prompt feedback protocol** → `/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/agent-prompt-feedback.md`. Commit feedback log update separately with message `docs: prompt feedback — bellows developer worktree teardown type fix`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move this plan anywhere. Wait for CEO confirmation before continuing.**
>
> **Deposits:**
> - `/Users/marklehn/Desktop/GitHub/bellows/knowledge/development/worktree-teardown-type-mismatch-fix-dev-log-2026-05-03.md`

---
---

## STEP 2 — BELLOWS QA

---

> You are the Bellows QA. Read your specialist file at `/Users/marklehn/Desktop/GitHub/bellows/agents/BELLOWS_QA.md` first. Skip glossary read — this is a deliverable verification + targeted regression check.
>
> **Before starting, read `/Users/marklehn/Desktop/GitHub/bellows/knowledge/development/worktree-teardown-type-mismatch-fix-dev-log-2026-05-03.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding.**
>
> **FIRST — Deliverable Verification (Rule 17).** Read the dev log's "Files Created or Modified (Code)" list. For every listed change, verify on disk:
>
> 1. **Site 1 — `_create_worktree` failure handler.** `grep -n 'worktree_creation' /Users/marklehn/Desktop/GitHub/bellows/bellows.py`. Expected: a line containing `{"gate": "worktree_creation", "evidence": str(e)}`. Pipe output to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/worktree-teardown-type-mismatch-fix-2026-05-03/grep_creation_site.txt`.
> 2. **Sites 2-4 — three `worktree_teardown` sites.** `grep -n 'worktree_teardown' /Users/marklehn/Desktop/GitHub/bellows/bellows.py`. Expected: three lines containing `{"gate": "worktree_teardown", "evidence": str(e)}`. Pipe output to `evidence/worktree-teardown-type-mismatch-fix-2026-05-03/grep_teardown_sites.txt`.
> 3. **No remaining string-format sites.** `grep -n 'worktree_teardown_failed\|worktree_creation_failed' /Users/marklehn/Desktop/GitHub/bellows/bellows.py`. Expected: zero matches (the old string format is fully replaced). Pipe to `evidence/worktree-teardown-type-mismatch-fix-2026-05-03/grep_old_format.txt`. Empty file = pass.
> 4. **New test exists.** `grep -n 'test_post_verdict_request_handles_worktree_teardown_failure_dict_format' /Users/marklehn/Desktop/GitHub/bellows/tests/`. Expected: one match in test_verdict.py or wherever Step 1 placed it. Pipe to `evidence/worktree-teardown-type-mismatch-fix-2026-05-03/grep_new_test.txt`.
> 5. **Commit landed.** `git -C /Users/marklehn/Desktop/GitHub/bellows --no-pager log -1 --format='%H %s'`. Expected: HEAD commit message starts with `fix(bellows): use dict format for worktree failure entries`. Pipe to `evidence/worktree-teardown-type-mismatch-fix-2026-05-03/git_log_head.txt`.
>
> Produce a verification table: `| # | Deliverable | Expected | Status (✅/❌) | Evidence |`. Cite evidence files by path in the Evidence column. If ANY item is ❌, attempt to fix (re-commit, re-grep) before proceeding. If unfixable, stop and report — do NOT proceed to test regression.
>
> **THEN — Targeted Regression (Rule 21).** Run `cd /Users/marklehn/Desktop/GitHub/bellows && python3 -m pytest tests/test_verdict.py tests/test_bellows.py -v 2>&1 | tee /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/worktree-teardown-type-mismatch-fix-2026-05-03/pytest_targeted.txt`. Confirm: (a) the new test `test_post_verdict_request_handles_worktree_teardown_failure_dict_format` PASSES, (b) no other test in those files regressed (compare pass/fail counts to expected baseline of all-passing).
>
> Add a row to the verification table: `| 6 | Targeted test regression | All tests in test_verdict.py and test_bellows.py pass, including new regression test | ✅/❌ | evidence/.../pytest_targeted.txt |`. **Do NOT mark ✅ if any test failed. Do NOT mark ✅ with any of these hedging keywords in evidence: pending, inferred, extrapolated, estimated, approximate, skipped, assumed, close enough, should pass, would pass, not run.** Per Rule 19, hedging keywords on a positive-status row auto-fail the self-check.
>
> **Deposit QA report.** Write to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/worktree-teardown-type-mismatch-fix-qa-report-2026-05-03.md`. Include: a one-paragraph summary, the verification table, and the literal stdout of the Rule 20 self-check below.
>
> **Run the Rule 20 self-check.** Execute the Python block below VERBATIM (do not modify it). Include its literal stdout in the QA report. If it prints `❌ SELF-CHECK FAILED`, STOP — do not update PROJECT_STATUS, do not commit anything else, report the failure to the CEO.
>
> ```python
> # Rule 20 — Mandatory QA Self-Check
> import os, sys
> plan_slug = "worktree-teardown-type-mismatch-fix-2026-05-03"
> qa_report_path = "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/worktree-teardown-type-mismatch-fix-qa-report-2026-05-03.md"
> evidence_dir = f"/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = [
>     "grep_creation_site.txt",
>     "grep_teardown_sites.txt",
>     "grep_old_format.txt",
>     "grep_new_test.txt",
>     "git_log_head.txt",
>     "pytest_targeted.txt",
> ]
> hedging_keywords = ["pending", "inferred", "extrapolated", "estimated", "approximate", "skipped", "assumed", "close enough", "should pass", "would pass", "not run"]
> POSITIVE_STATUS_TOKENS = ["✅", "OK", "PASS", "done", "complete", "verified"]
>
> def is_positive_row(line):
>     if "|" not in line:
>         return False
>     cells = [c.strip() for c in line.split("|")]
>     for cell in cells:
>         for token in POSITIVE_STATUS_TOKENS:
>             if token == "✅":
>                 if "✅" in cell:
>                     return True
>             else:
>                 if cell.lower() == token.lower():
>                     return True
>     return False
>
> failures = []
> if not os.path.isdir(evidence_dir):
>     failures.append(f"CRITICAL: evidence folder missing: {evidence_dir}")
> else:
>     for fname in required_evidence_files:
>         fpath = os.path.join(evidence_dir, fname)
>         if not os.path.isfile(fpath):
>             failures.append(f"CRITICAL: evidence file missing: {fpath}")
>         elif fname != "grep_old_format.txt" and os.path.getsize(fpath) == 0:
>             # grep_old_format.txt is expected to be empty (proves no remaining string-format sites)
>             failures.append(f"CRITICAL: evidence file empty: {fpath}")
> if os.path.isfile(qa_report_path):
>     with open(qa_report_path, "r") as f:
>         report = f.read()
>     for line in report.splitlines():
>         if is_positive_row(line):
>             lower = line.lower()
>             for kw in hedging_keywords:
>                 if kw in lower:
>                     failures.append(f"CRITICAL: hedging keyword '{kw}' in positive-status row: {line.strip()[:120]}")
>                     break
> else:
>     failures.append(f"CRITICAL: QA report not found at {qa_report_path}")
> print("=" * 60)
> print("Rule 20 — QA Self-Check Results")
> print("=" * 60)
> if failures:
>     print(f"❌ SELF-CHECK FAILED — {len(failures)} issue(s):")
>     for f in failures:
>         print(f"  - {f}")
>     print("\nPlan CANNOT close. Fix issues and re-run QA.")
>     sys.exit(1)
> else:
>     print("✅ SELF-CHECK PASSED — all evidence files present, no hedging keywords found.")
>     print(f"Evidence folder: {evidence_dir}")
>     print(f"Files verified: {len(required_evidence_files)}")
> ```
>
> **Final — feedback then commit.** Append a feedback entry to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/agent-prompt-feedback.md` per the standard protocol. Then commit ONLY the QA report and evidence files (do NOT commit any plan moves — the Planner handles plan placement after Rule 22 verification). Commit message: `qa: worktree teardown type-mismatch fix verification (passed)` if self-check passed, or `qa: worktree teardown type-mismatch fix verification (FAILED)` if it didn't.
>
> **STOP.** Do NOT move this plan anywhere. Per the disable-auto-close model and Rule 8, the Planner performs the terminal placement (this plan lives in `bellows/knowledge/research/fix-prompts/`, NOT a watched decisions directory, so there is no Done/ move — the Planner appends a status note to the plan file or moves it to an archived location after Rule 22 verification passes).
>
> **Deposits:**
> - `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/worktree-teardown-type-mismatch-fix-qa-report-2026-05-03.md`
> - `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/worktree-teardown-type-mismatch-fix-2026-05-03/` (six files per Rule 20 self-check)
