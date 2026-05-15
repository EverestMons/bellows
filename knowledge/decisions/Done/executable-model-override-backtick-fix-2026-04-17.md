# bellows — Per-Plan Model Override + Gate 5 Backtick Fix
**Date:** 2026-04-17 | **Type:** Executable | **Priority:** 1 | **Execution:** Step 1 (DEV) → Step 2 (QA)

## How to Run This Plan

**Bootstrap:** `Read the plan at bellows/knowledge/decisions/executable-model-override-backtick-fix-2026-04-17.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.`

## Context

Two small fixes. (1) Plans should be able to specify `**Model:** claude-sonnet-4-6` in the header to override the global `default_model` from config.json. This lets the Planner scope simple plans to Sonnet (cheaper) and complex plans to Opus. (2) Gate 5's plan-text regex extracts deposit paths with leading backticks that aren't stripped, causing `os.path.isfile` to always return False. Every deposit gate check this session was a false positive from this bug.

---
---

## STEP 1 — DEV

---

> **FIRST — claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-model-override-backtick-fix-2026-04-17.md", "bellows/knowledge/decisions/in-progress-executable-model-override-backtick-fix-2026-04-17.md")`. Read `bellows/bellows.py`, `bellows/runner.py`, and `bellows/gates.py`. **Two commits.**
>
> **Commit 1 — Per-plan model override.** (a) In `bellows.py`, `_parse_plan_header` already extracts YAML-like fields from plan headers. Verify it would capture a `**Model:**` line — note that plan headers use `**bold:**` markdown format, not YAML. The existing regex `if ":" in line: key, _, value = line.partition(":")` should work but may include `**` in the key. Add stripping of `**` and `*` from the key: `key = key.strip().strip("*")`. (b) After `header = gate_result.get("plan_header", {})` is available in `run_plan`, extract the model: `model = header.get("Model", header.get("model", config["default_model"]))`. But there's a problem — `header` isn't available until AFTER the first step runs (it comes from `gate_result`). The model needs to be known BEFORE the runner call. Fix: parse the header from `plan_text` at the TOP of `run_plan`, right after `total_steps = extract_total_steps(plan_text)`. Add: `header = _parse_plan_header(plan_text)` and `model = header.get("Model", header.get("model", config["default_model"]))`. Pass `model` to `runner.run_step` instead of `config["default_model"]`. (c) In `runner.py`, `run_step` currently receives the model as a parameter. Verify it passes it to the `claude -p` command. If it hardcodes the model anywhere, fix it to use the parameter. (d) Print the model being used: after the `plan has {total_steps} steps` line, add `if model != config["default_model"]: print(f"Bellows: using model override: {model}")`. Commit: `feat: per-plan model override via **Model:** header field`.
>
> **Commit 2 — Gate 5 backtick strip.** In `gates.py`, `_gate_deposit_exists`, find where paths are extracted from the agent's `### Files Deposited` section — the line `path = line[2:].strip().strip("`")` strips trailing backticks but not leading ones. Fix: `path = line[2:].strip().strip("\`")` should handle both, but verify — Python's `str.strip` removes characters from BOTH ends, so `strip("\`")` should work. Also find the plan-text regex extraction for plan-required deposits. The regex captures paths from patterns like `Deposit.*to.*\`path\`` — the backtick may be included in the capture group. Fix the regex to exclude backticks, or strip them after capture. Test by checking that `"\`invoice-pulse/knowledge/foo.md".strip("\`")` produces `"invoice-pulse/knowledge/foo.md"`. Commit: `fix: gate 5 — strip leading/trailing backticks from deposit paths`.
>
> **Deposit dev log** to `bellows/knowledge/development/model-override-backtick-fix-2026-04-17.md`. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — QA

---

> Before starting, read `bellows/knowledge/development/model-override-backtick-fix-2026-04-17.md` and check Output Receipt. If not Complete, stop. **Verification.** (a) `bellows.py` — grep for `Model` in the header parsing section. Grep for `model override` in the print statement. Confirm `model` is passed to `runner.run_step`. (b) `runner.py` — confirm the model parameter is used in the `claude -p` command, not a hardcoded value. (c) `gates.py` — grep for `strip` calls on deposit paths. Verify backtick stripping handles both leading and trailing. (d) Manual test: `python3 -c "path = '\`invoice-pulse/knowledge/foo.md'; print(path.strip('\`'))"` should output `invoice-pulse/knowledge/foo.md`. Pipe evidence to `bellows/knowledge/qa/evidence/executable-model-override-backtick-fix-2026-04-17/grep_deliverables.txt`. **Deposit QA report** to `bellows/knowledge/qa/model-override-backtick-fix-qa-2026-04-17.md`.
>
> **Rule 20 Self-Check:**
> ```python
> import os, sys
> plan_slug = "executable-model-override-backtick-fix-2026-04-17"
> qa_report_path = "bellows/knowledge/qa/model-override-backtick-fix-qa-2026-04-17.md"
> evidence_dir = f"bellows/knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = ["grep_deliverables.txt"]
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
> if failures:
>     print(f"FAILED — {len(failures)} issue(s):")
>     for f in failures: print(f"  - {f}")
>     sys.exit(1)
> else:
>     print("PASSED — all evidence present, no hedging.")
> ```
>
> If FAILS, STOP. If PASSES: move to Done. Commit: `chore: move model-override-backtick-fix to Done`. Standard prompt feedback protocol.
>
> **STOP. Do NOT proceed further. Wait for CEO confirmation.**
