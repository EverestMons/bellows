
> **FIRST — claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-plan-truncation-fix-2026-04-17.md", "bellows/knowledge/decisions/in-progress-executable-plan-truncation-fix-2026-04-17.md")`. Read `bellows/bellows.py` and `bellows/verdict.py` in full. Read the diagnostic at `bellows/knowledge/research/plan-file-truncation-2026-04-17.md`. **This plan has 2 commits.**
>
> **Commit 1 — Store total_steps in verdict-request metadata.** **(1a) `verdict.py` — `post_verdict_request`.** Add a `total_steps` parameter to the function signature (default `None`). In the content string that gets written to the verdict-request file, add a metadata line: `**Total Steps:** {total_steps}` right after the existing `**Pause Reason:**` line. **(1b) `bellows.py` — pass total_steps to verdict requests.** There are two call sites for `verdict.post_verdict_request` in `run_plan`: the while-loop pause (~line 222) and the final-step pause (~line 279). Both already have `total_steps` in scope (computed at ~line 162). Pass it as `total_steps=total_steps` to both calls. **(1c) `bellows.py` — `_consume_verdicts` reads total_steps from verdict-request instead of re-parsing plan.** In `_consume_verdicts`, find the block where it handles `v == "continue"` (~line 553-570). Currently it does: `plan_text_c = load_file(full_plan_path)` then `total_steps_c = 1 if is_diag else extract_total_steps(plan_text_c)`. Replace this with: read `total_steps` from the pending verdict-request file. The pending request file is already being read earlier in the method (at ~line 534, `pending_req_file` is opened to extract `plan_path_from_request`). Add parsing for the `**Total Steps:**` line from the same file: `for req_line in pending_req_file_text.splitlines(): if req_line.startswith("**Total Steps:**"): total_steps_c = int(req_line.split(":**", 1)[1].strip())`. If the line isn't found (backward compat with old verdict-request files that predate this change), fall back to the existing `load_file` + `extract_total_steps` behavior. Keep `is_diag` override: `if is_diag: total_steps_c = 1`. The key change: `load_file(full_plan_path)` is no longer the primary source for step count — the verdict-request metadata is. The plan file on disk may be truncated but the verdict-request file is never touched by the agent. Commit: `fix: store total_steps in verdict metadata — prevents agent-truncated plan files from causing QA skip`.
>
> **Commit 2 — Defensive: cache plan_text at dispatch time.** As belt-and-suspenders for any other code path that might re-read the plan file: in `run_plan`, right after `plan_text = load_file(plan_path)` (~line 160), also store `original_plan_text = plan_text`. Then at the second `verdict.post_verdict_request` call site (final-step pause, ~line 279), pass the original plan text as a new optional parameter `plan_text=original_plan_text` so the verdict system has the full content if it ever needs it. This does NOT change the primary fix (Commit 1 already solved the step-count problem) — it's insurance for future code paths. Do NOT change the `_consume_verdicts` read path — Commit 1's metadata approach is the fix. This commit is additive only. Commit: `refactor: cache original plan text at dispatch time (defensive)`.
>
> **After both commits**, verify: (a) `grep -n "total_steps" bellows/verdict.py` — should show the new parameter and metadata line, (b) `grep -n "Total Steps" bellows/bellows.py` — should show the parsing in `_consume_verdicts`, (c) run any existing tests in `bellows/tests/` if they exist. **Deposit development log** to `bellows/knowledge/development/plan-truncation-fix-2026-04-17.md` using canonical Python file write. Include commit SHAs, files modified, before/after of the `_consume_verdicts` step-count logic, before/after of `post_verdict_request` signature. End with Output Receipt. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — QA

---

> Before starting, read `bellows/knowledge/development/plan-truncation-fix-2026-04-17.md` and check Output Receipt status. If not Complete, stop and report. **Deliverable Verification (Rule 17).** **(a)** `verdict.py` — grep for `total_steps` in `post_verdict_request` function signature. Grep for `Total Steps` in the content string. **(b)** `bellows.py` — grep for `total_steps=total_steps` at both `post_verdict_request` call sites. Grep for `Total Steps` parsing in `_consume_verdicts`. Confirm the old `load_file(full_plan_path)` + `extract_total_steps` is still present as fallback (backward compat). **(c)** Verify no regressions: `python3 -c "import bellows, verdict, runner, gates; print('PASS — all modules import')"`. **(d)** If `bellows/tests/` exists, run `pytest bellows/tests/ -v --tb=short`. Pipe all evidence to `bellows/knowledge/qa/evidence/executable-plan-truncation-fix-2026-04-17/grep_deliverables.txt`. **Deposit QA report** to `bellows/knowledge/qa/plan-truncation-fix-qa-2026-04-17.md`.
>
> **Rule 20 Self-Check:**
> ```python
> import os, sys
> plan_slug = "executable-plan-truncation-fix-2026-04-17"
> qa_report_path = "bellows/knowledge/qa/plan-truncation-fix-qa-2026-04-17.md"
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
> If self-check FAILS, STOP. If PASSES: move plan to Done: `import shutil; shutil.move("bellows/knowledge/decisions/in-progress-executable-plan-truncation-fix-2026-04-17.md", "bellows/knowledge/decisions/Done/executable-plan-truncation-fix-2026-04-17.md")`. Commit: `chore: move plan-truncation-fix to Done`. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed further. Wait for CEO confirmation.**
