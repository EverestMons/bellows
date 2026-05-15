# Bellows — Fix: Source SHA Visibility at Startup (Bug C)
**Date:** 2026-04-14 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA)
**Priority:** 1

## How to Run This Plan

This plan is picked up and executed by Bellows automatically.

## Context

Bug C — Bellows has no hot-reload. Python loads `bellows.py` at module import time when the process starts. Code changes on disk do not take effect until the process is killed and restarted. This was observed today: the `is_runnable_plan` parallel-prefix fix shipped cleanly (commit, tests, QA), but the running Bellows process kept using the old function until manual restart. Every Bellows bug fix has this property.

This plan does not "fix" Bug C — Python import semantics are not a Bellows issue. Instead, this plan makes the staleness **visible**: at startup, Bellows prints the git SHA of the `bellows.py` file it loaded from. The CEO can compare against `git log -1 bellows.py` on disk to know immediately whether a restart is needed. Cheap, obvious, no runtime overhead, no hot-reload magic.

Single fix in `bellows/bellows.py`:
1. Add `_source_sha()` helper function that returns the short git SHA of `bellows.py`
2. Print the SHA in the startup banner block inside `Bellows.start()`

---
---

## STEP 1 — DEV

---

> **FIRST — claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-source-sha-startup-2026-04-14.md", "bellows/knowledge/decisions/in-progress-executable-source-sha-startup-2026-04-14.md")`. Skip specialist file and glossary reads — small additive change. Working directory is `/Users/marklehn/Desktop/GitHub/bellows/`. Two edits to `bellows.py`, then one test.
>
> **Edit 1 — Add `_source_sha()` helper.** Locate `bellows.py`. Find the top-level function definitions (functions that are NOT inside a class — e.g. `load_config`, `migrate_db`, `load_file`, `extract_step_number`, etc.). Add `import subprocess` to the imports at the top of the file if not already present. Then add this new helper function near the other top-level helpers (good location: immediately after `load_file` or near `is_runnable_plan`, wherever reads cleanly — DEV chooses placement):
>
> ```python
> def _source_sha() -> str:
>     """Return the short git SHA for bellows.py, or 'unknown' on any failure."""
>     try:
>         result = subprocess.run(
>             ["git", "log", "-1", "--format=%h", "--", "bellows.py"],
>             cwd=str(BELLOWS_ROOT),
>             capture_output=True,
>             text=True,
>             timeout=5,
>         )
>         sha = result.stdout.strip()
>         return sha if sha else "unknown"
>     except Exception:
>         return "unknown"
> ```
>
> The helper must use `BELLOWS_ROOT` (already defined as a module-level constant at the top of `bellows.py`) as the `cwd` for the git call. Do NOT use `os.path.dirname(__file__)` or `os.getcwd()` — those can point to the wrong place depending on how Bellows is invoked. `BELLOWS_ROOT` is the canonical reference.
>
> **Edit 2 — Print the SHA in the startup banner.** Locate `Bellows.start()` method. Find the banner block that currently looks like:
>
> ```python
>         print("=" * 50)
>         print("  🔥 Bellows is running")
>         print(f"  Watching {len(self.config.get('watched_projects', []))} projects")
>         print(f"  Rescan interval: 30s")
>         print(f"  Callback: http://{self.config.get('tailscale_ip','localhost')}:{self.config.get('callback_port',5000)}/respond")
>         print("=" * 50)
> ```
>
> Replace with a version that adds a new line showing the source SHA:
>
> ```python
>         print("=" * 50)
>         print("  🔥 Bellows is running")
>         print(f"  Source: bellows.py @ {_source_sha()}")
>         print(f"  Watching {len(self.config.get('watched_projects', []))} projects")
>         print(f"  Rescan interval: 30s")
>         print(f"  Callback: http://{self.config.get('tailscale_ip','localhost')}:{self.config.get('callback_port',5000)}/respond")
>         print("=" * 50)
> ```
>
> The SHA line goes between "Bellows is running" and "Watching N projects". This placement groups identity info (what's running) above operational info (what it's watching).
>
> **Test updates in `tests/test_bellows.py`.** Add one new test — `test_source_sha_returns_string`. Keep it simple: call `bellows._source_sha()`, assert the return value is a non-empty string, assert the return value is either a valid short SHA (regex match `^[0-9a-f]{7,12}$`) OR the literal string `"unknown"`. Do NOT hardcode a specific SHA value — that would break on every commit. The test verifies the function contract, not a specific git state. Example:
>
> ```python
> def test_source_sha_returns_string():
>     import re
>     sha = bellows._source_sha()
>     assert isinstance(sha, str)
>     assert len(sha) > 0
>     assert sha == "unknown" or re.match(r"^[0-9a-f]{7,12}$", sha), f"unexpected SHA format: {sha!r}"
> ```
>
> Fit this into the existing test file style — same import pattern, same indentation, same place where other function-level tests live (alongside `test_extract_parallel_group_match`, `test_is_runnable_plan_diagnostic`, etc.). **Run targeted tests:** `python3 -m pytest tests/test_bellows.py -v` from `/Users/marklehn/Desktop/GitHub/bellows/`. All tests from Plan 1 must still pass (11 total) plus the 1 new test = 12 total. Commit: `feat: Bellows startup prints source SHA for staleness visibility`. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — QA

---

> Before starting, verify Step 1 committed via `git --no-pager log --oneline -3` from `/Users/marklehn/Desktop/GitHub/bellows/`. Skip specialist file and glossary reads — mechanical verification only. **Deliverable verification:** grep `bellows.py` for `_source_sha` — must appear at least 3 times (definition + 2 uses: import context, startup banner print). Grep for `import subprocess` — must be present in imports (may have been there already, that's fine). Grep for `"Source: bellows.py @"` — must appear in `Bellows.start()` banner. Grep `tests/test_bellows.py` for `test_source_sha_returns_string` — must be present. **Re-run targeted tests:** `python3 -m pytest tests/test_bellows.py -v` from `/Users/marklehn/Desktop/GitHub/bellows/` — write raw output to `bellows/knowledge/qa/evidence/source-sha-startup/pytest_targeted.txt` via Python file I/O. All 12 tests must pass. **Smoke test module import:** `python3 -c "import bellows; print('ok')"` from `/Users/marklehn/Desktop/GitHub/bellows/`. Write to `bellows/knowledge/qa/evidence/source-sha-startup/smoke_import.txt`. **Smoke test `_source_sha()` directly:** `python3 -c "import bellows; sha = bellows._source_sha(); print(f'sha={sha!r}'); assert isinstance(sha, str) and len(sha) > 0, 'SHA returned empty'; import re; assert sha == 'unknown' or re.match(r'^[0-9a-f]{7,12}$', sha), f'unexpected SHA format: {sha!r}'; print('sha contract OK')"` from `/Users/marklehn/Desktop/GitHub/bellows/`. Write to `bellows/knowledge/qa/evidence/source-sha-startup/smoke_sha.txt`. Produce verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |` covering: `_source_sha` function defined, startup banner prints Source line, subprocess imported, new test present and passing, all 12 tests pass, module imports clean, live smoke returns valid SHA or "unknown". Deposit QA report to `bellows/knowledge/qa/source-sha-startup-qa-2026-04-14.md`. **Run Rule 20 self-check:**
> ```python
> import os, sys
> qa_report_path = "knowledge/qa/source-sha-startup-qa-2026-04-14.md"
> evidence_dir = "knowledge/qa/evidence/source-sha-startup/"
> required_evidence_files = ["pytest_targeted.txt", "smoke_import.txt", "smoke_sha.txt"]
> hedging_keywords = ["pending","inferred","extrapolated","estimated","approximate","skipped","assumed","close enough","should pass","would pass","not run"]
> POSITIVE_STATUS_TOKENS = ["✅","OK","PASS","[x]","done","complete","verified"]
> def is_positive_row(line):
>     if "|" not in line: return False
>     cells = [c.strip() for c in line.split("|")]
>     for cell in cells:
>         for token in POSITIVE_STATUS_TOKENS:
>             if token == "✅":
>                 if "✅" in cell: return True
>             elif cell.lower() == token.lower(): return True
>     return False
> failures = []
> if not os.path.isdir(evidence_dir): failures.append(f"CRITICAL: evidence folder missing: {evidence_dir}")
> else:
>     for fname in required_evidence_files:
>         fpath = os.path.join(evidence_dir, fname)
>         if not os.path.isfile(fpath): failures.append(f"CRITICAL: evidence file missing: {fpath}")
>         elif os.path.getsize(fpath) == 0: failures.append(f"CRITICAL: evidence file empty: {fpath}")
> if os.path.isfile(qa_report_path):
>     with open(qa_report_path) as f: report = f.read()
>     for line in report.splitlines():
>         if is_positive_row(line):
>             lower = line.lower()
>             for kw in hedging_keywords:
>                 if kw in lower: failures.append(f"CRITICAL: hedging keyword '{kw}' in positive-status row: {line.strip()[:120]}"); break
> else: failures.append(f"CRITICAL: QA report not found at {qa_report_path}")
> print("="*60)
> print("Rule 20 — QA Self-Check Results")
> print("="*60)
> if failures:
>     print(f"FAILED — {len(failures)} issue(s):")
>     for f in failures: print(f"  - {f}")
>     sys.exit(1)
> else:
>     print("PASSED — all evidence files present, no hedging keywords.")
> ```
> Run from `/Users/marklehn/Desktop/GitHub/bellows/`. If self-check fails, stop and report to CEO. If passes: update `bellows/PROJECT_STATUS.md` — add entry: "2026-04-14: Source SHA visibility at startup shipped (Bug C mitigation). _source_sha() helper added; startup banner now prints `Source: bellows.py @ <sha>`. Does not fix Python import semantics — still requires manual restart — but makes staleness immediately visible on boot. REMINDER: restart Bellows manually to see the new banner." Move plan to Done: `import shutil; shutil.move("knowledge/decisions/in-progress-executable-source-sha-startup-2026-04-14.md", "knowledge/decisions/Done/executable-source-sha-startup-2026-04-14.md")`. Commit: `chore: QA report — Bellows source SHA startup`. Standard prompt feedback protocol → `knowledge/research/agent-prompt-feedback.md`.
