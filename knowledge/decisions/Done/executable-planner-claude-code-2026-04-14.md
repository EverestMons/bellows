# Bellows — Planner via Claude Code
**Date:** 2026-04-14 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA)
**Priority:** 1

## How to Run This Plan

```
Read the plan at bellows/knowledge/decisions/executable-planner-claude-code-2026-04-14.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation before proceeding to Step 2.
```

---
---

## STEP 1 — DEV

---

> **FIRST — claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-planner-claude-code-2026-04-14.md", "bellows/knowledge/decisions/in-progress-executable-planner-claude-code-2026-04-14.md")`. Skip specialist file and glossary reads — pure implementation task. Working directory is `/Users/marklehn/Desktop/GitHub/bellows/`. **Rewrite `planner.py`** — replace the Anthropic SDK approach with a `claude -p` subprocess approach. Remove the `anthropic` import entirely. Keep `build_system_prompt()` and `build_context_envelope()` exactly as they are — they are correct and reusable. **Add `build_consult_file(parsed, plan_text, step_number, project_brief, project_status) -> str`:** writes a self-contained consultation document to a temp file at `/tmp/bellows-consult-{uuid}.md` where uuid comes from `import uuid; str(uuid.uuid4())`. The file content is: `# Bellows — Planner Consultation\n\nYou are the Eluvian Project Planner. Read the context below and return a JSON decision.\n\n` followed by `build_system_prompt()` output, then `\n\n---\n\n`, then `build_context_envelope(...)` output. Returns the temp file path. **Rewrite `consult(parsed, plan_text, step_number, model, project_brief="", project_status="") -> dict`:** (1) calls `build_consult_file(...)` to write the temp file; (2) builds prompt string: `f"Read {consult_path} carefully. You are the Eluvian Project Planner. Return ONLY a JSON object — no prose, no markdown fences. Schema: {{\"decision\": \"continue\" | \"rewrite\" | \"escalate\", \"reason\": \"one sentence\", \"next_step_prompt\": \"full revised prompt string or null\"}}"` ; (3) runs `subprocess.run(["claude", "-p", prompt, "--output-format", "json", "--model", model, "--allowedTools", "Read"], cwd="/tmp", capture_output=True, text=True, timeout=120)`; (4) on `subprocess.TimeoutExpired` returns escalate dict with reason "Planner consultation timed out"; (5) on success: parses `result.stdout` as JSON via `json.loads`, extracts `raw["result"]`, strips markdown fences, parses as JSON decision dict, returns it; (6) on any parse failure returns `{"decision": "escalate", "reason": "Planner response was not valid JSON", "next_step_prompt": None}`; (7) in a `finally` block: deletes the temp file via `os.unlink(consult_path)` if it exists. **Update `tests/test_planner.py`** — replace the two existing tests with: (1) `test_build_consult_file` — calls `build_consult_file` with a minimal parsed fixture, asserts the returned path exists on disk, reads it and asserts it contains "Eluvian Project Planner" and "continue", deletes it; (2) `test_consult_bad_json` — mocks `subprocess.run` to return a mock with `stdout='{"type":"result","subtype":"success","is_error":false,"result":"not json","stop_reason":"end_turn","session_id":"x","total_cost_usd":0.0,"permission_denials":[]}'`, calls `consult(parsed_fixture, "plan text", 1, "claude-sonnet-4-6")`, asserts `decision == "escalate"` and `"not valid JSON"` in reason. (3) `test_consult_timeout` — mocks `subprocess.run` to raise `subprocess.TimeoutExpired("claude", 120)`, calls consult, asserts `decision == "escalate"` and `"timed out"` in reason. **Run tests:** `python -m pytest tests/test_planner.py -v` — all must pass. Commit: `feat: rewrite planner.py to use claude -p subprocess instead of SDK`. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — QA

---

> Before starting, verify Step 1 committed via `git --no-pager log --oneline -3`. Skip specialist file and glossary reads — mechanical verification only. **Deliverable verification:** confirm `planner.py` exists, grep it for `subprocess`, `build_consult_file`, `consult`, `os.unlink` — all must be present. Confirm `import anthropic` does NOT appear in `planner.py`. **Re-run tests** fresh: `python -m pytest tests/test_planner.py -v` — write raw output to `bellows/knowledge/qa/evidence/planner-claude-code/pytest_targeted.txt` via Python file I/O. **Smoke test — consult file build:** `python3 -c "import planner; path = planner.build_consult_file({'receipt_status':'Complete','escalate':False,'ceo_flags':[],'result_text':'done','cost_usd':0.1,'permission_denials':[]}, 'plan text', 1); content = open(path).read(); print(len(content), 'chars,', 'Planner' in content); import os; os.unlink(path)"` from `bellows/` — assert prints char count above 1000 and True. Write to `bellows/knowledge/qa/evidence/planner-claude-code/smoke_consult_file.txt`. **Smoke test — no anthropic import:** `python3 -c "import planner; print('anthropic' not in dir(planner))"` — assert prints True. Write to `bellows/knowledge/qa/evidence/planner-claude-code/smoke_no_sdk.txt`. Produce verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |`. Deposit QA report to `bellows/knowledge/qa/planner-claude-code-qa-2026-04-14.md`. **Run Rule 20 self-check:**
> ```python
> import os, sys
> qa_report_path = "bellows/knowledge/qa/planner-claude-code-qa-2026-04-14.md"
> evidence_dir = "bellows/knowledge/qa/evidence/planner-claude-code/"
> required_evidence_files = ["pytest_targeted.txt", "smoke_consult_file.txt", "smoke_no_sdk.txt"]
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
> If self-check fails, stop and report to CEO. If passes: update `bellows/PROJECT_STATUS.md` — add entry: "2026-04-14: planner.py rewritten to use claude -p subprocess — no API key required." Move plan to Done: `import shutil; shutil.move("bellows/knowledge/decisions/in-progress-executable-planner-claude-code-2026-04-14.md", "bellows/knowledge/decisions/Done/executable-planner-claude-code-2026-04-14.md")`. Commit: `chore: QA report — planner claude-p rewrite`. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
