# Bellows — Runner and Parser
**Date:** 2026-04-13 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA)
**Priority:** 1

## How to Run This Plan

```
Read the plan at bellows/knowledge/decisions/executable-runner-parser-2026-04-13.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation before proceeding to Step 2.
```

---
---

## STEP 1 — DEV

---

> **FIRST — claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-runner-parser-2026-04-13.md", "bellows/knowledge/decisions/in-progress-executable-runner-parser-2026-04-13.md")`. Skip specialist file and glossary reads — this is a pure implementation task. Working directory is `/Users/marklehn/Desktop/GitHub/bellows/`. **Implement `parser.py`** — this module receives the raw JSON dict from a `claude -p --output-format json` call and extracts everything Bellows needs to make decisions. Implement the following: `parse(raw: dict) -> dict` that extracts and returns: `session_id` (str), `is_error` (bool), `stop_reason` (str), `result_text` (str — the full `result` field), `cost_usd` (float — `total_cost_usd`), `permission_denials` (list — empty list if absent), `receipt_status` (str — one of "Complete", "Partial", "Blocked", "Unknown" — extracted by scanning `result_text` for the pattern `**Status:** Complete`, `**Status:** Partial`, `**Status:** Blocked`; returns "Unknown" if none match), `ceo_flags` (list[str] — extracted by finding the `### Flags for CEO` section in `result_text` and collecting non-"None" bullet lines; empty list if section absent or only contains "None"), `escalate` (bool — True if `receipt_status` is "Blocked" or `ceo_flags` is non-empty or `is_error` is True). Also implement `is_clean(parsed: dict) -> bool` that returns True if `escalate` is False and `stop_reason` == "end_turn" and `receipt_status` in ("Complete", "Partial"). **Implement `runner.py`** — this module executes a single plan step via `claude -p` and returns the parsed result. Implement: `run_step(prompt: str, project_path: str, model: str, session_id: str | None = None, allowed_tools: str = "Read,Edit,Write,Bash") -> dict` that: (1) builds the `claude -p` command as a list for `subprocess.run` — args: `["claude", "-p", prompt, "--output-format", "json", "--model", model, "--allowedTools", allowed_tools]`, appending `["--resume", session_id]` if session_id is not None; (2) runs subprocess with `cwd=project_path`, `capture_output=True`, `text=True`, `timeout=300`; (3) on `subprocess.TimeoutExpired` returns `{"is_error": True, "error": "timeout", "session_id": None, "escalate": True, "receipt_status": "Blocked", "ceo_flags": ["Step timed out after 300s"], "cost_usd": 0.0, "stop_reason": "timeout", "result_text": "", "permission_denials": []}`; (4) on any other exception returns same shape with `"error": str(e)`; (5) on success: parses stdout as JSON via `json.loads`, calls `parser.parse()` on the result, logs raw stdout to `bellows/logs/{timestamp}-step.json` via Python file I/O where timestamp is `datetime.now().strftime("%Y%m%d-%H%M%S")`, returns parsed dict. Import `parser` directly (`from parser import parse`). **Implement `tests/test_runner_parser.py`** — create `tests/` directory if absent. Write three tests using `pytest` and `unittest.mock`: (1) `test_parse_clean_output` — calls `parser.parse()` with a dict matching the confirmed JSON structure from the characterization test (use the step1-output.json fields as the fixture — `type: result`, `subtype: success`, `is_error: False`, `result: "Step 1 complete.\n\n---\n## Output Receipt\n**Agent:** Test\n**Step:** 1\n**Status:** Complete\n\n### Flags for CEO\n- None"`, `stop_reason: end_turn`, `session_id: "abc123"`, `total_cost_usd: 0.14`, `permission_denials: []`) — asserts `receipt_status == "Complete"`, `ceo_flags == []`, `escalate == False`, `is_clean(result) == True`; (2) `test_parse_blocked_output` — same fixture but `result` contains `**Status:** Blocked` and `### Flags for CEO\n- Schema drift detected` — asserts `receipt_status == "Blocked"`, `ceo_flags == ["Schema drift detected"]`, `escalate == True`; (3) `test_run_step_timeout` — mocks `subprocess.run` to raise `subprocess.TimeoutExpired("claude", 300)`, calls `runner.run_step("test prompt", "/tmp", "claude-sonnet-4-6")`, asserts returned dict has `is_error == True`, `escalate == True`, `stop_reason == "timeout"`. **Run tests:** `python -m pytest tests/test_runner_parser.py -v`. All three must pass before committing. Commit: `feat: implement runner.py and parser.py with tests`. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — QA

---

> Before starting, verify Step 1 committed via `git --no-pager log --oneline -3`. Skip specialist file and glossary reads — mechanical verification only. **Deliverable verification:** read the Step 1 Output Receipt and verify every listed file exists: `runner.py`, `parser.py`, `tests/test_runner_parser.py`. Grep `runner.py` for `subprocess.run` and `TimeoutExpired`. Grep `parser.py` for `receipt_status` and `ceo_flags` and `escalate`. **Re-run tests** fresh: `python -m pytest tests/test_runner_parser.py -v` — write raw output to `bellows/knowledge/qa/evidence/runner-parser/pytest_targeted.txt` via Python file I/O. **Smoke test** — run `python3 -c "from parser import parse; r = parse({'type':'result','subtype':'success','is_error':False,'result':'done\n**Status:** Complete\n### Flags for CEO\n- None','stop_reason':'end_turn','session_id':'x','total_cost_usd':0.1,'permission_denials':[]}); print(r['receipt_status'], r['escalate'])"` from `bellows/` — assert output is `Complete False`. Write output to `bellows/knowledge/qa/evidence/runner-parser/smoke_test.txt`. Produce verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |`. Deposit QA report to `bellows/knowledge/qa/runner-parser-qa-2026-04-13.md`. **Run Rule 20 self-check:**
> ```python
> import os, sys
> plan_slug = "executable-runner-parser-2026-04-13"
> qa_report_path = "bellows/knowledge/qa/runner-parser-qa-2026-04-13.md"
> evidence_dir = "bellows/knowledge/qa/evidence/runner-parser/"
> required_evidence_files = ["pytest_targeted.txt", "smoke_test.txt"]
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
>     print("\nPlan CANNOT close.")
>     sys.exit(1)
> else:
>     print("PASSED — all evidence files present, no hedging keywords.")
> ```
> If self-check fails, stop and report to CEO. If self-check passes: update `bellows/PROJECT_STATUS.md` — add entry: "2026-04-13: runner.py and parser.py implemented and tested." Move plan to Done: `import shutil; shutil.move("bellows/knowledge/decisions/in-progress-executable-runner-parser-2026-04-13.md", "bellows/knowledge/decisions/Done/executable-runner-parser-2026-04-13.md")`. Commit: `chore: QA report — runner and parser`. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
