# Bellows — Phase 2A: Threading, Diagnostic Fix, Rescan, Terminal Output
**Date:** 2026-04-14 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA)
**Priority:** 1

## How to Run This Plan

This plan is picked up and executed by Bellows automatically.

---
---

## STEP 1 — DEV

---

> **FIRST — claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-phase2a-2026-04-14.md", "bellows/knowledge/decisions/in-progress-executable-phase2a-2026-04-14.md")`. Skip specialist file and glossary reads — pure implementation task. Working directory is `/Users/marklehn/Desktop/GitHub/bellows/`. Four changes to `bellows.py`: **Change 1 — Threading.** Add `import threading` to imports. In the `Bellows` class, replace `handle_new_plan` with: `def handle_new_plan(self, path: str): t = threading.Thread(target=run_plan, args=(path, self.config, self.response_server), daemon=True); t.start(); print(f"Bellows: ▶ started {os.path.basename(path)}")`. Also add a `self._active_plans: set = set()` to `Bellows.__init__`. In `run_plan`, at the very start of the `try` block add `print(f"Bellows: ⏳ RUNNING — {plan_name}")` and just before `notifier.notify_complete` add `print(f"Bellows: ✅ DONE — {plan_name} (${total_cost:.4f})")`. In the `except` block add `print(f"Bellows: ❌ FAILED — {plan_name}: {e}")`. **Change 2 — Diagnostic prompt fix.** In `run_plan`, after the `extract_total_steps` call add: `is_diagnostic = os.path.basename(plan_path).startswith("diagnostic-")` and `if is_diagnostic: total_steps = 1`. Replace the `bootstrap_prompt` assignment with: `if is_diagnostic: bootstrap_prompt = f"Read the diagnostic at {plan_path}. Execute it fully — this is a single-step investigation. Deposit your findings and report Complete when done." else: bootstrap_prompt = f"Read the plan at {plan_path}. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation before proceeding to Step 2."`. **Change 3 — Periodic rescan.** In `Bellows.start()`, replace the `while True: time.sleep(1)` loop with: `rescan_interval = 30; last_rescan = time.time()` then `while True: time.sleep(1); if time.time() - last_rescan >= rescan_interval: self._rescan(handler); last_rescan = time.time()`. Add a new method to `Bellows`: `def _rescan(self, handler): for decisions_path in self.config.get("watched_projects", []): if os.path.isdir(decisions_path): for fname in os.listdir(decisions_path): if is_runnable_plan(fname): full_path = os.path.join(decisions_path, fname); handler._handle(full_path)`. **Change 4 — Startup banner.** In `Bellows.start()`, replace `print(f"Bellows watching {len(...)} projects")` with a multi-line banner: `print("=" * 50); print("  🔥 Bellows is running"); print(f"  Watching {len(self.config.get('watched_projects', []))} projects"); print(f"  Rescan interval: 30s"); print(f"  Callback: http://{self.config.get('tailscale_ip','localhost')}:{self.config.get('callback_port',5000)}/respond"); print("=" * 50)`. **Update `tests/test_bellows.py`** — add one new test: `test_is_runnable_plan_diagnostic` — asserts `is_runnable_plan("diagnostic-foo-2026-04-14.md")` is True and `is_runnable_plan("in-progress-diagnostic-foo.md")` is False. **Run tests:** `python -m pytest tests/test_bellows.py -v` — all must pass. Commit: `feat: Phase 2A — threading, diagnostic fix, periodic rescan, terminal output`. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — QA

---

> Before starting, verify Step 1 committed via `git --no-pager log --oneline -3`. Skip specialist file and glossary reads — mechanical verification only. **Deliverable verification:** grep `bellows.py` for `threading.Thread`, `is_diagnostic`, `single-step investigation`, `_rescan`, `🔥 Bellows is running`, `⏳ RUNNING`, `✅ DONE`, `❌ FAILED` — all must be present. **Re-run tests** fresh: `python -m pytest tests/test_bellows.py -v` — write raw output to `bellows/knowledge/qa/evidence/phase2a/pytest_targeted.txt` via Python file I/O. **Smoke test imports:** `python3 -c "import bellows; print('ok')"` from `bellows/` — assert prints ok. Write to `bellows/knowledge/qa/evidence/phase2a/smoke_import.txt`. Produce verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |`. Deposit QA report to `bellows/knowledge/qa/phase2a-qa-2026-04-14.md`. **Run Rule 20 self-check:**
> ```python
> import os, sys
> qa_report_path = "bellows/knowledge/qa/phase2a-qa-2026-04-14.md"
> evidence_dir = "bellows/knowledge/qa/evidence/phase2a/"
> required_evidence_files = ["pytest_targeted.txt", "smoke_import.txt"]
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
> If self-check fails, stop and report to CEO. If passes: update `bellows/PROJECT_STATUS.md` — add entry: "2026-04-14: Phase 2A complete — threading, diagnostic fix, periodic rescan, terminal output." Move plan to Done: `import shutil; shutil.move("bellows/knowledge/decisions/in-progress-executable-phase2a-2026-04-14.md", "bellows/knowledge/decisions/Done/executable-phase2a-2026-04-14.md")`. Commit: `chore: QA report — phase2a`. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
