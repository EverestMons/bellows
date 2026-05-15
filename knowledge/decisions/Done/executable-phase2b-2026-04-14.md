# Bellows — Phase 2B: Parallel Groups + Queue Drain Notification
**Date:** 2026-04-14 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA)
**Priority:** 1

## How to Run This Plan

This plan is picked up and executed by Bellows automatically.

---
---

## STEP 1 — DEV

---

> **FIRST — claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-phase2b-2026-04-14.md", "bellows/knowledge/decisions/in-progress-executable-phase2b-2026-04-14.md")`. Skip specialist file and glossary reads — pure implementation task. Working directory is `/Users/marklehn/Desktop/GitHub/bellows/`. Three changes to `bellows.py`: **Change 1 — Parallel group detection.** Add a module-level function `extract_parallel_group(filename: str) -> Optional[str]` — imports `Optional` from `typing` if not present. Uses `re.match(r"^(parallel-\d+)-", filename)` and returns the group prefix (e.g. `"parallel-1"`) if matched, else `None`. Add a method to `PlanHandler`: `def collect_group(self, decisions_path: str, group: str) -> list[str]` — lists all files in `decisions_path`, filters for files starting with `group + "-"` that `is_runnable_plan()` returns True for and are not in `self._seen`, returns their full paths. **Change 2 — Group-aware handle_new_plan.** Replace `PlanHandler._handle` with: `def _handle(self, path: str): filename = os.path.basename(path); if not is_runnable_plan(filename) or path in self._seen: return; group = extract_parallel_group(filename); if group: decisions_path = str(pathlib.Path(path).parent); siblings = self.collect_group(decisions_path, group); all_paths = [p for p in siblings if p not in self._seen]; [self._seen.add(p) for p in all_paths]; print(f"Bellows: parallel group {group} — {len(all_paths)} plans"); self.orchestrator.handle_parallel_group(all_paths); else: self._seen.add(path); print(f"Bellows: detected plan {filename}"); self.orchestrator.handle_new_plan(path)`. Add `handle_parallel_group` to `Bellows` class: `def handle_parallel_group(self, paths: list): threads = [threading.Thread(target=self._run_tracked, args=(p,), daemon=True) for p in paths]; [t.start() for t in threads]; print(f"Bellows: ▶ started {len(threads)} parallel threads")`. **Change 3 — Active plan tracking + queue drain notification.** Replace `_active_plans: set` with `_active_lock = threading.Lock()` and `_active_count = 0` in `Bellows.__init__`. Add `_run_tracked` method to `Bellows`: `def _run_tracked(self, path: str): with self._active_lock: self._active_count += 1; try: run_plan(path, self.config, self.response_server); finally: with self._active_lock: self._active_count -= 1; self._check_queue_drain()`. Add `_check_queue_drain` method: `def _check_queue_drain(self): with self._active_lock: if self._active_count > 0: return; pending = []; [pending.extend([f for f in os.listdir(d) if is_runnable_plan(f)]) for d in self.config.get("watched_projects", []) if os.path.isdir(d)]; if not pending: app_key = self.config.get("pushover",{}).get("app_key",""); user_key = self.config.get("pushover",{}).get("user_key",""); print("Bellows: 🏁 Queue empty — all plans complete"); notifier.push(app_key, user_key, "Bellows — Queue Empty", "All plans complete. Ready for Forge cycle.")`. Update `handle_new_plan` to use `_run_tracked`: `def handle_new_plan(self, path: str): t = threading.Thread(target=self._run_tracked, args=(path,), daemon=True); t.start(); print(f"Bellows: ▶ started {os.path.basename(path)}")`. **Update `tests/test_bellows.py`** — add two tests: (1) `test_extract_parallel_group_match` — asserts `extract_parallel_group("parallel-1-executable-foo-2026-04-14.md") == "parallel-1"` and `extract_parallel_group("parallel-2-diagnostic-bar.md") == "parallel-2"`; (2) `test_extract_parallel_group_no_match` — asserts `extract_parallel_group("executable-foo.md") is None` and `extract_parallel_group("diagnostic-bar.md") is None`. **Run tests:** `python -m pytest tests/test_bellows.py -v` — all must pass. Commit: `feat: Phase 2B — parallel groups, queue drain notification`. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — QA

---

> Before starting, verify Step 1 committed via `git --no-pager log --oneline -3`. Skip specialist file and glossary reads — mechanical verification only. **Deliverable verification:** grep `bellows.py` for `extract_parallel_group`, `collect_group`, `handle_parallel_group`, `_run_tracked`, `_check_queue_drain`, `_active_count`, `_active_lock`, `Queue Empty` — all must be present. **Re-run tests** fresh: `python -m pytest tests/test_bellows.py -v` — write raw output to `bellows/knowledge/qa/evidence/phase2b/pytest_targeted.txt` via Python file I/O. **Smoke test parallel group extraction:** `python3 -c "from bellows import extract_parallel_group; print(extract_parallel_group('parallel-1-executable-foo.md'), extract_parallel_group('executable-foo.md'))"` — assert prints `parallel-1 None`. Write to `bellows/knowledge/qa/evidence/phase2b/smoke_parallel.txt`. **Smoke test imports:** `python3 -c "import bellows; print('ok')"` — assert prints ok. Write to `bellows/knowledge/qa/evidence/phase2b/smoke_import.txt`. Produce verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |`. Deposit QA report to `bellows/knowledge/qa/phase2b-qa-2026-04-14.md`. **Run Rule 20 self-check:**
> ```python
> import os, sys
> qa_report_path = "bellows/knowledge/qa/phase2b-qa-2026-04-14.md"
> evidence_dir = "bellows/knowledge/qa/evidence/phase2b/"
> required_evidence_files = ["pytest_targeted.txt", "smoke_parallel.txt", "smoke_import.txt"]
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
> If self-check fails, stop and report to CEO. If passes: update `bellows/PROJECT_STATUS.md` — add entry: "2026-04-14: Phase 2B complete — parallel groups, queue drain notification." Move plan to Done: `import shutil; shutil.move("bellows/knowledge/decisions/in-progress-executable-phase2b-2026-04-14.md", "bellows/knowledge/decisions/Done/executable-phase2b-2026-04-14.md")`. Commit: `chore: QA report — phase2b`. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
