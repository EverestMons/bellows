
> **FIRST — claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-gate5-fix-verdict-emoji-2026-04-16.md", "bellows/knowledge/decisions/in-progress-executable-gate5-fix-verdict-emoji-2026-04-16.md")`. Read `bellows/gates.py`, `bellows/bellows.py`, and `bellows/parser.py` in full. Read the diagnostic findings at `bellows/knowledge/research/gate5-deposit-bypass-2026-04-16.md`. **This plan has 3 commits.**
>
> **Commit 1 — Fix Gate 5 path resolution.** In `gates.py`, modify `_gate_deposit_exists` to accept `project_path` as a parameter. When `os.path.isfile(path)` is called, try the path as-is first (handles absolute paths), then try `os.path.join(project_path, path)` (handles project-relative paths like `invoice-pulse/knowledge/...`). Update the call site in `check()` to pass `project_path` to `_gate_deposit_exists`. The function signature changes from `_gate_deposit_exists(parsed, failures)` to `_gate_deposit_exists(parsed, failures, project_path)`. Commit: `fix: gate 5 deposit path resolution — use project_path for relative paths`.
>
> **Commit 2 — Add plan-aware deposit requirement to Gate 5.** This is the primary fix. Gate 5 currently only checks paths the agent declares in `### Files Deposited`. If the agent omits the section entirely, Gate 5 silently passes. The fix: Gate 5 also extracts expected deposit paths from the plan text itself. Scan the plan step's prompt text (the `## STEP N` section) for deposit instructions by matching patterns like `Deposit findings to`, `Deposit development log to`, `Deposit.*to.*knowledge/`, or paths matching `knowledge/(research|development|qa|architecture)/.*\.md`. Collect these as "plan-required deposits." After checking the agent-declared deposits, also check each plan-required deposit path via `os.path.isfile()` (using the same project_path resolution from Commit 1). If a plan-required deposit is missing AND the agent did not declare it in `### Files Deposited`, append a failure: `{"gate": "deposit_exists", "evidence": f"plan-required deposit missing (not declared by agent): {path}"}`. This way Gate 5 catches both scenarios: (a) agent declares a deposit but doesn't write it (existing behavior), (b) plan requires a deposit but agent doesn't even mention it (new behavior). **Important edge case:** the regex should extract the path from instructions like `Deposit findings to \`invoice-pulse/knowledge/research/foo.md\`` — strip backtick quoting and capture the path. Also handle the canonical Python file write pattern: `with open("path/to/file.md", "w")` — extract the path from the open() call. **Do NOT make this gate overly aggressive.** Only match explicit deposit instructions with concrete file paths. Do not match vague references to "deposit your work" without a path. False positives (gate failing on plans that don't require deposits) are worse than false negatives here. Commit: `feat: gate 5 plan-aware deposit requirement — detect missing deposits even when agent omits Output Receipt`.
>
> **Commit 3 — Add verdict-paused emoji.** In `bellows.py`, find the two locations where verdict-pending state is reached (the while-loop pause at ~line 222 and the final-step pause at ~line 279). Both currently print `Bellows: verdict requested for {plan_name} step {current_step} — pausing plan`. Change these to print `Bellows: ⏸️  PAUSED — {plan_name} step {current_step} — waiting for CEO verdict`. This makes it visually distinct from `⏳ RUNNING` (processing) and `🏁 Queue empty` (done). Also update the `_check_queue_drain` method: before printing `🏁 Queue empty`, scan all watched project directories for `verdict-pending-` prefixed files. If any exist, print `Bellows: ⏸️  {count} plan(s) awaiting verdict` instead of (or in addition to) `🏁 Queue empty`. This way the CEO always knows if plans are paused even after the queue drains. Commit: `feat: ⏸️ emoji for verdict-paused state — distinguish from running/complete`.
>
> **After all 3 commits**, run any existing tests: check if `bellows/tests/` exists and run `pytest` if it does. If no test directory exists, manually verify Gate 5 by running a quick Python check: `python3 -c "import gates; print(gates._gate_deposit_exists.__code__.co_varnames[:3])"` to confirm the new `project_path` parameter is present. **Deposit development log** to `bellows/knowledge/development/gate5-fix-verdict-emoji-2026-04-16.md` using canonical Python file write. Include commit SHAs, files modified, before/after of the Gate 5 function signature, the deposit-detection regex patterns used, and the emoji output format. End with Output Receipt. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — QA

---

> Before starting, read `bellows/knowledge/development/gate5-fix-verdict-emoji-2026-04-16.md` and check Output Receipt status. If not Complete, stop and report. **Deliverable Verification (Rule 17).** **(a)** `gates.py` — grep for `project_path` in `_gate_deposit_exists` function signature. Grep for `os.path.join(project_path` to confirm path resolution. Grep for `plan-required deposit missing` to confirm plan-aware detection. Grep for the deposit-detection regex patterns. **(b)** `bellows.py` — grep for `⏸️` emoji to confirm it appears in verdict-paused print statements. Grep for `verdict-pending-` in `_check_queue_drain` to confirm it scans for paused plans. **(c)** Verify Gate 5 function signature: `python3 -c "import gates; import inspect; sig = inspect.signature(gates._gate_deposit_exists); print(list(sig.parameters.keys()))"` — should include `project_path`. **(d)** Simulate the bypass scenario: `python3 -c "import gates; failures = []; gates._gate_deposit_exists({'result_text': 'Step complete. No output receipt.'}, failures, '/tmp'); print(f'Failures: {len(failures)}')"` — with no `### Files Deposited` section AND no plan text, this should still return 0 failures (no false positives on plans without deposit instructions). Pipe all evidence to `bellows/knowledge/qa/evidence/executable-gate5-fix-verdict-emoji-2026-04-16/grep_deliverables.txt`. **Deposit QA report** to `bellows/knowledge/qa/gate5-fix-verdict-emoji-qa-2026-04-16.md`.
>
> **Rule 20 Self-Check:**
> ```python
> import os, sys
> plan_slug = "executable-gate5-fix-verdict-emoji-2026-04-16"
> qa_report_path = "bellows/knowledge/qa/gate5-fix-verdict-emoji-qa-2026-04-16.md"
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
> print("Rule 20 — QA Self-Check Results")
> print("=" * 60)
> if failures:
>     print(f"FAILED — {len(failures)} issue(s):")
>     for f in failures: print(f"  - {f}")
>     sys.exit(1)
> else:
>     print("PASSED — all evidence files present, no hedging keywords found.")
>     print(f"Evidence folder: {evidence_dir}")
>     print(f"Files verified: {len(required_evidence_files)}")
> ```
>
> If self-check FAILS, STOP. If PASSES: move plan to Done: `import shutil; shutil.move("bellows/knowledge/decisions/in-progress-executable-gate5-fix-verdict-emoji-2026-04-16.md", "bellows/knowledge/decisions/Done/executable-gate5-fix-verdict-emoji-2026-04-16.md")`. Commit: `chore: move gate5-fix plan to Done`. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed further. Wait for CEO confirmation.**
