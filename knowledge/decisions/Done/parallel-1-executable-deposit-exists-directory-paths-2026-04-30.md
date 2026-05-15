# Bellows — deposit_exists Gate Accepts Directory Paths
**Date:** 2026-04-30 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (Bellows Developer) → Step 2 (Bellows QA)
**Priority:** 3

## Context

BACKLOG #11 (2026-04-30): the `deposit_exists` gate rejects directory paths declared in Rule 26 `**Deposits:**` blocks. Surfaced today on `executable-planner-template-bellows-execution-model-section-2026-04-30` Step 2 — plan declared `bellows/knowledge/qa/evidence/<plan-slug>/` (a directory) per Rule 26's documented convention ("list the evidence directory as a single bullet"); `_resolve_deposit_path` in `bellows/gates.py` uses `os.path.isfile()` only, returning False for directories. Result: spurious gate_failure verdict on every Rule 26 plan that lists an evidence directory. Rule 26's Migration scope paragraph anticipated this.

Test Scope: targeted — single-function change in gates.py with matching test additions in test_gates.py. No cross-bucket regression risk.

Parallel-1 with `parallel-1-executable-ledger-pause-reason-code-2026-04-30.md` — disjoint files (gates.py vs verdict.py, test_gates.py vs test_verdict.py), safe to dispatch simultaneously.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation ("ok") before proceeding to Step 2.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/parallel-1-executable-deposit-exists-directory-paths-2026-04-30.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — Bellows Developer

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/parallel-1-executable-deposit-exists-directory-paths-2026-04-30.md", "bellows/knowledge/decisions/in-progress-parallel-1-executable-deposit-exists-directory-paths-2026-04-30.md")`. Read your specialist file at `bellows/agents/BELLOWS_DEVELOPER.md` first. **Skip glossary read — this is a code-tracing + one-line fix task, no domain interpretation needed.** All commands run from `/Users/marklehn/Desktop/GitHub/`. **The fix:** change `_resolve_deposit_path` in `bellows/gates.py` so that a path resolves successfully if it exists as either a file OR a directory. The current function calls `os.path.isfile(path)` at three resolution strategies (path as-is, project-relative, parent-relative); each call must become `(os.path.isfile(p) or os.path.isdir(p))` for the corresponding path `p`. The function's contract becomes "exists at one of the candidate paths as either a file or a directory" — directory paths declared in Rule 26 `**Deposits:**` blocks (e.g., evidence directories) now resolve correctly. **Add tests** to `bellows/tests/test_gates.py` covering: (a) a `_resolve_deposit_path` call where the path exists only as a directory at the as-is location (returns True); (b) a call where the path exists only as a directory at the project-relative location (returns True); (c) a call where the path exists only as a directory at the parent-relative location (returns True); (d) a call where the path does not exist at any location (returns False, regression guard); (e) one end-to-end test of `_gate_deposit_exists` with a Rule 26 `**Deposits:**` block that declares a directory path which exists on disk — assert the gate produces zero failures. Five new tests total. **Do not** change the function signature, the resolution-strategy ordering, or the existing file-resolution behavior — purely additive: directories now resolve where they didn't before. **Run tests:** `cd /Users/marklehn/Desktop/GitHub/bellows && python3 -m pytest tests/test_gates.py --tb=short`. Report the count (expect existing tests + 5 new tests pass; the pre-existing `test_run_step_timeout` failure in `tests/test_runner_parser.py` does not run under this targeted scope and is unrelated). **Deposit dev log** at `bellows/knowledge/development/deposit-exists-directory-paths-dev-log-2026-04-30.md` with: (1) verbatim before/after of the `_resolve_deposit_path` function, (2) verbatim test additions, (3) test run output (count, pass/fail), (4) any deviations from the plan. **Commit:** `cd /Users/marklehn/Desktop/GitHub/bellows && git add gates.py tests/test_gates.py knowledge/development/deposit-exists-directory-paths-dev-log-2026-04-30.md && git --no-pager commit -m "fix(gates): _resolve_deposit_path accepts directory paths (BACKLOG #11)"`. **Standard prompt feedback protocol** → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/development/deposit-exists-directory-paths-dev-log-2026-04-30.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — Bellows QA

---

> **Before starting, read `bellows/knowledge/development/deposit-exists-directory-paths-dev-log-2026-04-30.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding.** Read your specialist file at `bellows/agents/BELLOWS_QA.md` first. **Skip glossary read — this is mechanical QA for a one-function code change.** All commands run from `/Users/marklehn/Desktop/GitHub/bellows/`.
>
> **FIRST — Deliverable Verification.** Read the Step 1 dev log "Files Created or Modified (Code)" list. For every listed file, verify the change exists on disk via grep. Produce a verification table: | Deliverable | Expected | Status (✅/❌) | Evidence |. If ANY item is ❌, attempt to fix; if unfixable, stop and report.
>
> **Verification checks (each deposits literal output to `bellows/knowledge/qa/evidence/parallel-1-executable-deposit-exists-directory-paths-2026-04-30/`):**
>
> (1) Grep for `os.path.isdir` in gates.py — expect at least 3 matches (one per resolution strategy in `_resolve_deposit_path`): `grep -n "os.path.isdir" gates.py > knowledge/qa/evidence/parallel-1-executable-deposit-exists-directory-paths-2026-04-30/grep_isdir_gates.txt 2>&1`.
>
> (2) Grep for the function definition to confirm it still exists: `grep -n "def _resolve_deposit_path" gates.py > knowledge/qa/evidence/parallel-1-executable-deposit-exists-directory-paths-2026-04-30/grep_function_def.txt 2>&1`. Expect exactly 1 match.
>
> (3) Run targeted test suite: `python3 -m pytest tests/test_gates.py --tb=short > knowledge/qa/evidence/parallel-1-executable-deposit-exists-directory-paths-2026-04-30/pytest_targeted.txt 2>&1`. Expect all tests pass — the prior baseline was 29 tests passing per the 2026-04-28 BACKLOG #2 close; this plan adds 5 new tests, so expect ≥34 passing.
>
> (4) Behavioral smoke — call `_resolve_deposit_path` directly with a directory path that exists. Write the script to `knowledge/qa/evidence/parallel-1-executable-deposit-exists-directory-paths-2026-04-30/smoke.py` with content that imports gates, calls `gates._resolve_deposit_path("knowledge/qa/evidence/", "/Users/marklehn/Desktop/GitHub/bellows")`, and prints the result. Run it: `python3 knowledge/qa/evidence/parallel-1-executable-deposit-exists-directory-paths-2026-04-30/smoke.py > knowledge/qa/evidence/parallel-1-executable-deposit-exists-directory-paths-2026-04-30/smoke_output.txt 2>&1`. Expect output `True`.
>
> (5) Git log — last commit on gates.py: `cd /Users/marklehn/Desktop/GitHub/bellows && git --no-pager log -1 --name-only -- gates.py > knowledge/qa/evidence/parallel-1-executable-deposit-exists-directory-paths-2026-04-30/git_commit.txt 2>&1`. Expect commit message references BACKLOG #11.
>
> **Deposit QA report** to `bellows/knowledge/qa/deposit-exists-directory-paths-qa-2026-04-30.md` with the verification table citing each evidence file path in the Evidence column. Include the literal stdout of the Rule 20 self-check block in the QA report body. Mark any check that cannot be completed as ❌ with a reason; do NOT mark ✅ with hedging language.
>
> **Mandatory Rule 20 self-check block (execute verbatim, include literal stdout in QA report):**
>
> ```python
> import os, sys
> plan_slug = "parallel-1-executable-deposit-exists-directory-paths-2026-04-30"
> qa_report_path = "knowledge/qa/deposit-exists-directory-paths-qa-2026-04-30.md"
> evidence_dir = f"knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = [
>     "grep_isdir_gates.txt",
>     "grep_function_def.txt",
>     "pytest_targeted.txt",
>     "smoke.py",
>     "smoke_output.txt",
>     "git_commit.txt",
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
>         elif os.path.getsize(fpath) == 0:
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
>     print(f"FAILED — SELF-CHECK FAILED — {len(failures)} issue(s):")
>     for f in failures:
>         print(f"  - {f}")
>     print("\nPlan CANNOT close. Fix issues and re-run QA.")
>     sys.exit(1)
> else:
>     print("PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.")
>     print(f"Evidence folder: {evidence_dir}")
>     print(f"Files verified: {len(required_evidence_files)}")
> ```
>
> If the self-check prints `FAILED`, STOP — do not update PROJECT_STATUS, do not move plan to Done, report to CEO. If `PASSED`, proceed with closeout in this exact order per Rule 23.
>
> **Final — PROJECT_STATUS update.** Use `Filesystem:edit_file` to add a completed milestone entry under PROJECT_STATUS.md's `## Completed` section. Anchor: insert the new entry as the FIRST bullet under the `## Completed` header (immediately after the header line). New entry verbatim: `- 2026-04-30: BACKLOG #11 closed — deposit_exists gate accepts directory paths. Fix: _resolve_deposit_path in gates.py now accepts paths that exist as either files or directories. Closes the false-positive gate_failure on every Rule 26 plan that declares an evidence directory in its **Deposits:** block. +5 unit tests in test_gates.py. Reference: parallel-1-executable-deposit-exists-directory-paths-2026-04-30. REMINDER: restart Bellows daemon to load fix.`
>
> **Final — BACKLOG move-to-Closed.** Use `Filesystem:edit_file` on `bellows/knowledge/BACKLOG.md` to mark BACKLOG #11 as closed. Find the verbatim line beginning `- 2026-04-30: deposit_exists gate rejects directory paths` and replace its leading `- ` with `- ~~` and append `~~ **[CLOSED 2026-04-30 — see Closed section below]**` immediately before the entry's terminating period. Then append a new Closed entry to the `## Closed` section verbatim: `- **Closed 2026-04-30:** BACKLOG #11 (deposit_exists gate rejects directory paths in Rule 26 **Deposits:** blocks). Fix: _resolve_deposit_path in gates.py extended to accept paths that exist as either files (os.path.isfile) or directories (os.path.isdir) at any of three resolution strategies. +5 unit tests. Closes the false-positive gate_failure observed on executable-planner-template-bellows-execution-model-section-2026-04-30 Step 2. Reference: parallel-1-executable-deposit-exists-directory-paths-2026-04-30. REMINDER: restart Bellows daemon to load.`
>
> **Step A — Feedback append.** Standard prompt feedback protocol → append entry to `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Step B — Final commit.** `cd /Users/marklehn/Desktop/GitHub/bellows && git add knowledge/qa/ knowledge/research/agent-prompt-feedback.md PROJECT_STATUS.md knowledge/BACKLOG.md && git --no-pager commit -m "chore: QA + status + BACKLOG close for deposit_exists directory paths (BACKLOG #11)"`.
>
> **STOP. Plan complete after this step. Do NOT move plan to Done — Planner performs Done/ move after Rule 22 verification per Rule 25 terminal-step resolution.**
>
> **Deposits:**
> - `bellows/knowledge/qa/deposit-exists-directory-paths-qa-2026-04-30.md`
> - `bellows/knowledge/qa/evidence/parallel-1-executable-deposit-exists-directory-paths-2026-04-30/grep_isdir_gates.txt`
> - `bellows/knowledge/qa/evidence/parallel-1-executable-deposit-exists-directory-paths-2026-04-30/grep_function_def.txt`
> - `bellows/knowledge/qa/evidence/parallel-1-executable-deposit-exists-directory-paths-2026-04-30/pytest_targeted.txt`
> - `bellows/knowledge/qa/evidence/parallel-1-executable-deposit-exists-directory-paths-2026-04-30/smoke.py`
> - `bellows/knowledge/qa/evidence/parallel-1-executable-deposit-exists-directory-paths-2026-04-30/smoke_output.txt`
> - `bellows/knowledge/qa/evidence/parallel-1-executable-deposit-exists-directory-paths-2026-04-30/git_commit.txt`
