# Bellows — Planner API Client
**Date:** 2026-04-13 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA)
**Priority:** 1

## How to Run This Plan

```
Read the plan at bellows/knowledge/decisions/executable-planner-2026-04-13.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation before proceeding to Step 2.
```

---
---

## STEP 1 — DEV

---

> **FIRST — claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-planner-2026-04-13.md", "bellows/knowledge/decisions/in-progress-executable-planner-2026-04-13.md")`. Skip specialist file and glossary reads — pure implementation task. Working directory is `/Users/marklehn/Desktop/GitHub/bellows/`. **Implement `planner.py`** with the following: **Imports:** `anthropic`, `json`, `os`, `pathlib`. **Constants:** `GOVERNANCE_ROOT = "/Users/marklehn/Desktop/GitHub"`, `PLANNER_TEMPLATE_PATH = f"{GOVERNANCE_ROOT}/PLANNER_TEMPLATE.md"`, `COMPANY_MD_PATH = f"{GOVERNANCE_ROOT}/COMPANY.md"`. **`build_system_prompt() -> str`:** reads PLANNER_TEMPLATE.md and COMPANY.md via Python file I/O, concatenates with a separator `\n\n---\n\n`, returns the combined string. Raises `FileNotFoundError` with a clear message if either file is missing. **`build_context_envelope(parsed: dict, plan_text: str, step_number: int, project_brief: str = "", project_status: str = "") -> str`:** assembles the user message that gets sent to the Planner API. Returns a structured string with clearly labelled sections: `## Plan (current step: {step_number})\n{plan_text}\n\n## Step Output\n{parsed["result_text"]}\n\n## Output Receipt Summary\n- Status: {parsed["receipt_status"]}\n- Escalate: {parsed["escalate"]}\n- CEO Flags: {parsed["ceo_flags"]}\n- Cost: ${parsed["cost_usd"]:.4f}\n- Permission Denials: {len(parsed["permission_denials"])}` — append `\n\n## Project Brief\n{project_brief}` if project_brief non-empty, append `\n\n## Project Status\n{project_status}` if project_status non-empty. End with: `\n\n## Your Task\nBased on the step output and Output Receipt above, decide the next action. Respond with a JSON object only — no prose, no markdown fences. Schema: {{"decision": "continue" | "rewrite" | "escalate", "reason": "one sentence", "next_step_prompt": "full revised prompt string or null if continue or escalate"}}`. **`consult(parsed: dict, plan_text: str, step_number: int, model: str, project_brief: str = "", project_status: str = "") -> dict`:** creates `anthropic.Anthropic()` client (reads `ANTHROPIC_API_KEY` from environment), calls `client.messages.create` with `model=model`, `max_tokens=1024`, `system=build_system_prompt()`, `messages=[{"role": "user", "content": build_context_envelope(...)}]`. Parses response: `text = response.content[0].text.strip()` — strips any accidental markdown fences (lines starting with ` ``` `) before parsing as JSON. Returns parsed JSON dict. On JSON parse failure returns `{"decision": "escalate", "reason": "Planner response was not valid JSON", "next_step_prompt": None}`. On `anthropic.APIError` returns `{"decision": "escalate", "reason": f"Planner API error: {str(e)}", "next_step_prompt": None}`. **Implement `tests/test_planner.py`** with two tests using `pytest` and `unittest.mock.patch`: (1) `test_consult_continue` — mocks `anthropic.Anthropic` client, sets `mock_client.messages.create.return_value.content[0].text = '{"decision": "continue", "reason": "clean step", "next_step_prompt": null}'`, calls `planner.consult(parsed_fixture, "plan text", 1, "claude-haiku-4-5-20251001")` where `parsed_fixture` is a clean dict with `receipt_status="Complete"`, `escalate=False`, `ceo_flags=[]`, `result_text="done"`, `cost_usd=0.1`, `permission_denials=[]` — asserts returned dict has `decision == "continue"`; (2) `test_consult_bad_json` — mocks client to return `"not json"` as text, calls consult, asserts `decision == "escalate"` and `"not valid JSON"` in reason. **Run tests:** `python -m pytest tests/test_planner.py -v` — all must pass. Commit: `feat: implement planner.py with tests`. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — QA

---

> Before starting, verify Step 1 committed via `git --no-pager log --oneline -3`. Skip specialist file and glossary reads — mechanical verification only. **Deliverable verification:** confirm `planner.py` and `tests/test_planner.py` exist. Grep `planner.py` for `build_system_prompt`, `build_context_envelope`, `consult`, `ANTHROPIC_API_KEY`. **Re-run tests** fresh: `python -m pytest tests/test_planner.py -v` — write raw output to `bellows/knowledge/qa/evidence/planner/pytest_targeted.txt` via Python file I/O. **Smoke test system prompt build:** `python3 -c "import planner; s = planner.build_system_prompt(); print(len(s), 'chars')"` from `bellows/` — assert it prints a char count above 1000 (confirms both files loaded). Write output to `bellows/knowledge/qa/evidence/planner/smoke_system_prompt.txt`. **Smoke test envelope:** `python3 -c "import planner; e = planner.build_context_envelope({'receipt_status':'Complete','escalate':False,'ceo_flags':[],'result_text':'done','cost_usd':0.1,'permission_denials':[]}, 'plan text', 1); print('continue' in e or 'decision' in e)"` — assert prints `True`. Write output to `bellows/knowledge/qa/evidence/planner/smoke_envelope.txt`. Produce verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |`. Deposit QA report to `bellows/knowledge/qa/planner-qa-2026-04-13.md`. **Run Rule 20 self-check:**
> ```python
> import os, sys
> plan_slug = "executable-planner-2026-04-13"
> qa_report_path = "bellows/knowledge/qa/planner-qa-2026-04-13.md"
> evidence_dir = "bellows/knowledge/qa/evidence/planner/"
> required_evidence_files = ["pytest_targeted.txt", "smoke_system_prompt.txt", "smoke_envelope.txt"]
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
> If self-check fails, stop and report to CEO. If passes: update `bellows/PROJECT_STATUS.md` — add entry: "2026-04-13: planner.py implemented and tested." Move plan to Done: `import shutil; shutil.move("bellows/knowledge/decisions/in-progress-executable-planner-2026-04-13.md", "bellows/knowledge/decisions/Done/executable-planner-2026-04-13.md")`. Commit: `chore: QA report — planner`. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
