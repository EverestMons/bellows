# Bellows — Notifier and Callback Server
**Date:** 2026-04-13 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA)
**Priority:** 1

## How to Run This Plan

```
Read the plan at bellows/knowledge/decisions/executable-notifier-server-2026-04-13.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation before proceeding to Step 2.
```

---
---

## STEP 1 — DEV

---

> **FIRST — claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-notifier-server-2026-04-13.md", "bellows/knowledge/decisions/in-progress-executable-notifier-server-2026-04-13.md")`. Skip specialist file and glossary reads — pure implementation task. Working directory is `/Users/marklehn/Desktop/GitHub/bellows/`. **Split `notifier.py` into two files: `notifier.py` (Pushover push) and `server.py` (Flask callback).** **Implement `notifier.py`:** imports `requests`. **Constants:** `PUSHOVER_API_URL = "https://api.pushover.net/1/messages.json"`. **`push(app_key: str, user_key: str, title: str, message: str, url: str = "", url_title: str = "") -> bool`:** sends a POST to the Pushover API with fields `token=app_key`, `user=user_key`, `title=title`, `message=message`, and optionally `url` and `url_title` if non-empty. Returns True if response status code is 200, False otherwise. On any `requests.RequestException` logs the error to stderr and returns False. **`notify_escalation(app_key: str, user_key: str, plan_name: str, step: int, reason: str, callback_url: str) -> bool`:** calls `push()` with title `f"Bellows — Escalation"`, message `f"Plan: {plan_name}\nStep: {step}\nReason: {reason}"`, url=callback_url, url_title="Respond". **`notify_complete(app_key: str, user_key: str, plan_name: str, total_cost: float) -> bool`:** calls `push()` with title `"Bellows — Complete"`, message `f"Plan: {plan_name}\nTotal cost: ${total_cost:.4f}"`, no url. **`notify_failure(app_key: str, user_key: str, plan_name: str, step: int, error: str) -> bool`:** calls `push()` with title `"Bellows — Failed"`, message `f"Plan: {plan_name}\nStep: {step}\nError: {error}"`, no url. **Implement `server.py`:** imports `flask`, `threading`, `queue`, `json`. **`ResponseServer`** class: `__init__(self, port: int)` sets `self.port = port`, `self.app = Flask(__name__)`, `self._response_queue = queue.Queue()`, `self._thread = None`. Registers one route: `POST /respond` — reads JSON body with fields `decision` (str) and `instruction` (str, optional), puts `{"decision": data.get("decision", ""), "instruction": data.get("instruction", "")}` onto `self._response_queue`, returns `{"status": "ok"}` as JSON with 200. **`start(self)`:** starts Flask in a daemon thread via `threading.Thread(target=lambda: self.app.run(host="0.0.0.0", port=self.port, use_reloader=False), daemon=True)`, sets `self._thread`. **`wait_for_response(self, timeout: int = 3600) -> Optional[dict]`:** calls `self._response_queue.get(timeout=timeout)`, returns the dict. On `queue.Empty` returns None. **`stop(self)`:** no-op for now — daemon thread dies with the process. **Implement `tests/test_notifier_server.py`** with three tests: (1) `test_push_success` — mocks `requests.post` to return a mock with `status_code=200`, calls `notifier.push("app", "user", "title", "msg")`, asserts returns True; (2) `test_push_failure` — mocks `requests.post` to return `status_code=400`, asserts returns False; (3) `test_server_respond` — creates `ResponseServer(port=15432)`, calls `start()`, sends a POST to `http://localhost:15432/respond` with JSON `{"decision": "continue"}` via `requests.post`, calls `wait_for_response(timeout=3)`, asserts returned dict has `decision == "continue"`. **Run tests:** `python -m pytest tests/test_notifier_server.py -v` — all must pass. Commit: `feat: implement notifier.py and server.py with tests`. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — QA

---

> Before starting, verify Step 1 committed via `git --no-pager log --oneline -3`. Skip specialist file and glossary reads — mechanical verification only. **Deliverable verification:** confirm `notifier.py` and `server.py` and `tests/test_notifier_server.py` exist. Grep `notifier.py` for `push`, `notify_escalation`, `notify_complete`, `notify_failure`. Grep `server.py` for `ResponseServer`, `wait_for_response`, `/respond`. **Re-run tests** fresh: `python -m pytest tests/test_notifier_server.py -v` — write raw output to `bellows/knowledge/qa/evidence/notifier-server/pytest_targeted.txt` via Python file I/O. **Smoke test notifier shape:** `python3 -c "import notifier; print(callable(notifier.push), callable(notifier.notify_escalation), callable(notifier.notify_complete), callable(notifier.notify_failure))"` — assert prints `True True True True`. Write to `bellows/knowledge/qa/evidence/notifier-server/smoke_notifier.txt`. **Smoke test server shape:** `python3 -c "from server import ResponseServer; s = ResponseServer(15433); print(hasattr(s, 'start'), hasattr(s, 'wait_for_response'))"` — assert prints `True True`. Write to `bellows/knowledge/qa/evidence/notifier-server/smoke_server.txt`. Produce verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |`. Deposit QA report to `bellows/knowledge/qa/notifier-server-qa-2026-04-13.md`.

> **Run Rule 20 self-check:**
> ```python
> import os, sys
> plan_slug = "executable-notifier-server-2026-04-13"
> qa_report_path = "bellows/knowledge/qa/notifier-server-qa-2026-04-13.md"
> evidence_dir = "bellows/knowledge/qa/evidence/notifier-server/"
> required_evidence_files = ["pytest_targeted.txt", "smoke_notifier.txt", "smoke_server.txt"]
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
> If self-check fails, stop and report to CEO. If passes: update `bellows/PROJECT_STATUS.md` — add entry: "2026-04-13: notifier.py and server.py implemented and tested." Move plan to Done: `import shutil; shutil.move("bellows/knowledge/decisions/in-progress-executable-notifier-server-2026-04-13.md", "bellows/knowledge/decisions/Done/executable-notifier-server-2026-04-13.md")`. Commit: `chore: QA report — notifier and server`. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
