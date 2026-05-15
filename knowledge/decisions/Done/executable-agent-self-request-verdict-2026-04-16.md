# Bellows — Agent Self-Request Verdict via Text Marker
**Date:** 2026-04-16 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA)

## How to Run This Plan

**Bootstrap:**
```
Read the plan at bellows/knowledge/decisions/executable-agent-self-request-verdict-2026-04-16.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for CEO confirmation before proceeding.
```

---
---

## STEP 1 — DEV

---

> **FIRST — claim this plan:** `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/executable-agent-self-request-verdict-2026-04-16.md", "/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/in-progress-executable-agent-self-request-verdict-2026-04-16.md")`. Skip specialist file and glossary reads. **Read first:** diagnostic findings at `bellows/knowledge/research/agent-self-request-verdict-diagnostic-2026-04-16.md` (Q1–Q5). Three files change: `parser.py`, `gates.py`, and tests. `bellows.py` and `verdict.py` are NOT modified — the gate_result dict shape is unchanged so the existing pause logic in `run_plan` works without changes. **Change 1 — `parser.py`: extract VERDICT_REQUESTED marker.** After the `ceo_flags` extraction block (the regex that scans for `### Flags for CEO`) and before the `escalate` assignment, add: `verdict_requested = {"requested": False, "reason": None}` then `vr_match = re.search(r"^VERDICT_REQUESTED:\s*(.+)$", result_text, re.MULTILINE)` then `if vr_match: verdict_requested = {"requested": True, "reason": vr_match.group(1).strip()}`. Add `"verdict_requested": verdict_requested` to the returned dict. Also add `"verdict_requested": {"requested": False, "reason": None}` to every error-path return dict in `runner.py` (the hardcoded dicts returned on timeout, exception, JSON decode failure) so the key is always present. **Change 2 — `gates.py`: replace filesystem scan with parsed dict lookup.** (a) Remove the `VERDICT_REQUEST_DIR` constant (line 14). (b) Remove the entire `_verdict_requested()` function (lines 30–48). (c) In `check()`, replace the line that calls `_verdict_requested(plan_path, step_number)` (line 87) with: `vr = parsed.get("verdict_requested", {})` then `requested = vr.get("requested", False)` then `request_body = vr.get("reason")`. The rest of the function that builds `"verdict_requested": {"requested": requested, "body": request_body}` in the gate_result dict stays unchanged. (d) If `plan_path` is no longer used by any gate after removing `_verdict_requested`, remove it from `check()`'s signature and update the two call sites in `bellows.py` to stop passing it. Check first — if another gate uses `plan_path`, leave it. **Tests:** (1) In `tests/test_bellows.py` or a new `tests/test_parser.py`: test that `parse()` given a `result_text` containing `VERDICT_REQUESTED: agent found inconsistency` returns `{"requested": True, "reason": "agent found inconsistency"}` in the `verdict_requested` field. (2) Test that `parse()` given a `result_text` WITHOUT the marker returns `{"requested": False, "reason": None}`. (3) Test that the marker works when it appears mid-text (not first line, not last line). (4) In `tests/test_gates.py`: test that `check()` with `parsed["verdict_requested"]["requested"] = True` sets `gate_result["verdict_requested"]["requested"] = True` without any filesystem operations. (5) Test that `check()` with `parsed` missing the `verdict_requested` key defaults to `requested = False`. **Commit:** `cd /Users/marklehn/Desktop/GitHub/bellows && git add -A && git commit -m "feat: agent self-request verdict via VERDICT_REQUESTED text marker"`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — QA

---

> Before starting, verify Step 1 committed by running `git --no-pager log --oneline -1`. If commit message doesn't match, stop and report. **Deliverable Verification:** (a) Parser extracts marker: `grep -n "VERDICT_REQUESTED" /Users/marklehn/Desktop/GitHub/bellows/parser.py` — expect 2+ matches (regex + dict assignment). (b) Dead code removed from gates: `grep -n "_verdict_requested\|VERDICT_REQUEST_DIR" /Users/marklehn/Desktop/GitHub/bellows/gates.py` — expect 0 matches. (c) gates.py uses parsed dict: `grep -n "verdict_requested" /Users/marklehn/Desktop/GitHub/bellows/gates.py` — expect 2+ matches (dict lookup + gate_result assignment). (d) Error paths in runner.py include the key: `grep -n "verdict_requested" /Users/marklehn/Desktop/GitHub/bellows/runner.py` — expect 1+ matches. (e) Tests exist: `grep -rn "VERDICT_REQUESTED\|verdict_requested" /Users/marklehn/Desktop/GitHub/bellows/tests/` — expect 5+ matches. Produce verification table. **Run targeted tests:** `cd /Users/marklehn/Desktop/GitHub/bellows && python -m pytest tests/ -k "verdict" -v 2>&1 | tee /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/agent-self-request-verdict/pytest_targeted.txt`. Then full suite: `python -m pytest tests/ -v 2>&1 | tee /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/agent-self-request-verdict/pytest_full.txt`. **Deposit:** write QA report to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/agent-self-request-verdict-qa-2026-04-16.md`. Create evidence directory first: `mkdir -p /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/agent-self-request-verdict/`. **Rule 20 self-check:**
>
> ```python
> import os, sys
> plan_slug = "executable-agent-self-request-verdict-2026-04-16"
> qa_report_path = "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/agent-self-request-verdict-qa-2026-04-16.md"
> evidence_dir = "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/agent-self-request-verdict/"
> required_evidence_files = ["pytest_targeted.txt", "pytest_full.txt"]
> hedging_keywords = ["pending", "inferred", "extrapolated", "estimated", "approximate", "skipped", "assumed", "close enough", "should pass", "would pass", "not run"]
> POSITIVE_STATUS_TOKENS = ["✅", "OK", "PASS", "[x]", "done", "complete", "verified"]
> def is_positive_row(line):
>     if "|" not in line: return False
>     cells = [c.strip() for c in line.split("|")]
>     for cell in cells:
>         for token in POSITIVE_STATUS_TOKENS:
>             if token == "✅":
>                 if "✅" in cell: return True
>             else:
>                 if cell.lower() == token.lower(): return True
>     return False
> failures = []
> if not os.path.isdir(evidence_dir):
>     failures.append(f"CRITICAL: evidence folder missing: {evidence_dir}")
> else:
>     for fname in required_evidence_files:
>         fpath = os.path.join(evidence_dir, fname)
>         if not os.path.isfile(fpath): failures.append(f"CRITICAL: evidence file missing: {fpath}")
>         elif os.path.getsize(fpath) == 0: failures.append(f"CRITICAL: evidence file empty: {fpath}")
> if os.path.isfile(qa_report_path):
>     with open(qa_report_path, "r") as f: report = f.read()
>     for line in report.splitlines():
>         if is_positive_row(line):
>             lower = line.lower()
>             for kw in hedging_keywords:
>                 if kw in lower: failures.append(f"CRITICAL: hedging keyword '{kw}' in positive-status row: {line.strip()[:120]}"); break
> else:
>     failures.append(f"CRITICAL: QA report not found at {qa_report_path}")
> print("=" * 60)
> print("Rule 20 — QA Self-Check Results")
> print("=" * 60)
> if failures:
>     print(f"FAILED — {len(failures)} issue(s):")
>     for f in failures: print(f"  - {f}")
>     print("\nPlan CANNOT close. Fix issues and re-run QA.")
>     sys.exit(1)
> else:
>     print("PASSED — all evidence files present, no hedging keywords found.")
>     print(f"Evidence folder: {evidence_dir}")
>     print(f"Files verified: {len(required_evidence_files)}")
> ```
>
> **Final:** Update PROJECT_STATUS.md — add completed milestone: "Agent self-request verdict mechanism: agents can output `VERDICT_REQUESTED: <reason>` to trigger a pause. Dead filesystem-scanning code in gates.py removed. Parser extracts the signal from result_text." Then move this plan to Done: `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/in-progress-executable-agent-self-request-verdict-2026-04-16.md", "/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/Done/executable-agent-self-request-verdict-2026-04-16.md")`. Commit: `"chore: QA + status update for agent self-request verdict"`. Standard prompt feedback protocol → `/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed further. Plan complete after this step.**
