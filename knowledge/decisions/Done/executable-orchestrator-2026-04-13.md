# Bellows — Main Orchestrator
**Date:** 2026-04-13 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA)
**Priority:** 1

## How to Run This Plan

```
Read the plan at bellows/knowledge/decisions/executable-orchestrator-2026-04-13.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation before proceeding to Step 2.
```

---
---

## STEP 1 — DEV

---

> **FIRST — claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-orchestrator-2026-04-13.md", "bellows/knowledge/decisions/in-progress-executable-orchestrator-2026-04-13.md")`. Skip specialist file and glossary reads — pure implementation task. Working directory is `/Users/marklehn/Desktop/GitHub/bellows/`. **Implement `bellows.py`** as the main orchestration entry point. **Imports:** `json`, `os`, `pathlib`, `re`, `shutil`, `sqlite3`, `time`, `datetime` from `datetime`, `watchdog.observers.Observer`, `watchdog.events.FileSystemEventHandler`, and local modules `runner`, `parser`, `planner`, `notifier`, `server`. **`load_config(path: str = "config.json") -> dict`:** reads and returns parsed JSON from config file. **`load_file(path: str) -> str`:** reads file at path, returns text, returns empty string if file missing. **`extract_step_number(plan_text: str, result_text: str) -> int`:** scans result_text for `**Step:** N` pattern via regex, returns int N, returns 1 if not found. **`extract_total_steps(plan_text: str) -> int`:** counts `## STEP` headers in plan_text via regex, returns count. **`record_run(db_path: str, plan_path: str, project: str, session_id: str, step: int, status: str, cost: float)`:** inserts a row into `bellows.db` runs table. Opens connection, executes INSERT, commits, closes. **`is_final_step(step: int, total_steps: int) -> bool`:** returns `step >= total_steps`. **`run_plan(plan_path: str, config: dict, response_server: server.ResponseServer)`:** the core execution loop for a single plan. Steps: (1) read plan file text; (2) extract project path from plan_path (parent of `knowledge/decisions/`); (3) load `PROJECT_BRIEF.md` and `PROJECT_STATUS.md` from project root via `load_file`; (4) extract total steps; (5) build bootstrap prompt: `f"Read the plan at {plan_path}. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation before proceeding to Step 2."`; (6) call `runner.run_step(prompt, project_path, config["default_model"])` — no session_id on first step; (7) record run to db; (8) enter step loop: while not final step — call `planner.consult(parsed, plan_text, current_step, config["planner_model"], project_brief, project_status)` to get decision; if decision is `"escalate"` or `parsed["escalate"]` is True: call `notifier.notify_escalation(...)` with callback URL `f"http://localhost:{config['callback_port']}/respond"`, call `response_server.wait_for_response(timeout=3600)`, if response is None or response["decision"] == "stop": log and return; if response["decision"] == "continue": proceed with original next step prompt; if response has non-empty "instruction": use instruction as next step prompt; if decision is `"rewrite"` and `next_step_prompt` is not None: use `next_step_prompt` as prompt for next step; if decision is `"continue"`: build next step prompt as `f"Read the plan at {plan_path}. Execute Step {current_step + 1}."` ; (9) call `runner.run_step(next_prompt, project_path, config["default_model"], session_id=parsed["session_id"])`; (10) update parsed, increment step, record to db; (11) on loop exit (final step complete): call `notifier.notify_complete(...)` with total cost summed across all steps. On any unhandled exception: call `notifier.notify_failure(...)`. **`class PlanHandler(FileSystemEventHandler)`:** `on_created(self, event)` — if not `event.is_directory` and filename starts with `executable-` or `diagnostic-` and does not start with `in-progress-` and ends with `.md`: call `self.orchestrator.handle_new_plan(event.src_path)`. **`class Bellows`:** `__init__(self, config)` sets config, creates `ResponseServer(config["callback_port"])`, creates sqlite3 connection check. **`handle_new_plan(self, path: str)`:** calls `run_plan(path, self.config, self.response_server)`. **`start(self)`:** starts `self.response_server`, creates `Observer`, attaches `PlanHandler` to each path in `config["watched_projects"]`, starts observer, logs "Bellows watching N projects", loops `time.sleep(1)` until KeyboardInterrupt, stops observer. **`if __name__ == "__main__"`:** loads config, creates `Bellows(config)`, calls `start()`. **Implement `tests/test_bellows.py`** with two tests: (1) `test_load_config` — writes a temp config.json to a tmp dir, calls `load_config` with that path, asserts `default_model == "claude-sonnet-4-6"`; (2) `test_is_final_step` — asserts `is_final_step(2, 2)` is True, `is_final_step(1, 2)` is False. **Run tests:** `python -m pytest tests/test_bellows.py -v` — all must pass. Commit: `feat: implement bellows.py orchestrator with tests`. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — QA

---

> Before starting, verify Step 1 committed via `git --no-pager log --oneline -3`. Skip specialist file and glossary reads — mechanical verification only. **Deliverable verification:** confirm `bellows.py` and `tests/test_bellows.py` exist. Grep `bellows.py` for `run_plan`, `PlanHandler`, `Bellows`, `handle_new_plan`, `planner.consult`, `notifier.notify_escalation`, `notifier.notify_complete`, `response_server.wait_for_response`. **Re-run tests** fresh: `python -m pytest tests/test_bellows.py -v` — write raw output to `bellows/knowledge/qa/evidence/orchestrator/pytest_targeted.txt` via Python file I/O. **Run full test suite:** `python -m pytest tests/ -v` — write raw output to `bellows/knowledge/qa/evidence/orchestrator/pytest_full.txt` via Python file I/O. **Smoke test imports:** `python3 -c "import bellows; print('ok')"` from `bellows/` — assert prints `ok`. Write to `bellows/knowledge/qa/evidence/orchestrator/smoke_import.txt`. Produce verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |`. Deposit QA report to `bellows/knowledge/qa/orchestrator-qa-2026-04-13.md`.

> **Run Rule 20 self-check:**
> ```python
> import os, sys
> qa_report_path = "bellows/knowledge/qa/orchestrator-qa-2026-04-13.md"
> evidence_dir = "bellows/knowledge/qa/evidence/orchestrator/"
> required_evidence_files = ["pytest_targeted.txt", "pytest_full.txt", "smoke_import.txt"]
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
> If self-check fails, stop and report to CEO. If passes: update `bellows/PROJECT_STATUS.md` — add entry: "2026-04-13: bellows.py orchestrator implemented and tested. Phase 1 build complete." Move plan to Done: `import shutil; shutil.move("bellows/knowledge/decisions/in-progress-executable-orchestrator-2026-04-13.md", "bellows/knowledge/decisions/Done/executable-orchestrator-2026-04-13.md")`. Commit: `chore: QA report — orchestrator`. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
