# Bellows — Verdict Lifecycle Coupling (BACKLOG #9)
**Date:** 2026-04-19 | **Tier:** Medium | **Test Scope:** full-suite | **Execution:** Step 1 (DEV) → Step 2 (QA)

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation ("ok") before proceeding to Step 2. The agent must never skip steps, auto-chain to the next step, or move the plan to Done without completing all steps including QA.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/executable-verdict-lifecycle-coupling-2026-04-19.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — BELLOWS DEVELOPER

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-verdict-lifecycle-coupling-2026-04-19.md", "bellows/knowledge/decisions/in-progress-executable-verdict-lifecycle-coupling-2026-04-19.md")`.
>
> You are the Bellows Developer. Read your specialist file at `bellows/agents/BELLOWS_DEVELOPER.md`. Skip glossary read — Bellows has no domain glossary and this is a mechanical implementation task.
>
> **Context:** BACKLOG #9 — verdict lifecycle coupling. The `verdicts/pending/` directory accumulates `verdict-request-*.md` files that strand when plans reach terminal state (Done or halted) without the specific step's verdict being consumed. Current per-step cleanup in `_consume_verdicts` only removes the single step file matching the consumed verdict; any other step requests for the same slug strand. Full diagnostic + design spec at `bellows/knowledge/research/verdict-lifecycle-coupling-2026-04-19.md`. Cite it for every design question.
>
> **Implementation — four deliverables, one commit per deliverable:**
>
> **Deliverable 1 — new helper `_cleanup_verdicts_for_slug(slug: str) -> int`** in `bellows.py`. Insert immediately after the `_delete_shadow()` function (find via `grep -n "def _delete_shadow" bellows/bellows.py`). Function body: glob `BELLOWS_ROOT / "verdicts" / "pending"` for files matching `f"verdict-request-{slug}-step-*.md"`, unlink each match, print `Bellows: cleaned {count} pending verdict(s) for {slug}` when count > 0 (silent when count == 0), return count. Use `pathlib.Path.glob()` since `pathlib` is already imported at the top of the module. Commit: `"feat(bellows): add _cleanup_verdicts_for_slug helper"`.
>
> **Deliverable 2 — three terminal-state call sites.** All three sites are BEFORE the `shutil.move` that performs the terminal transition. Use the exact code anchors below, not line numbers (line numbers drift).
>
> Site A (auto-close in `run_plan`): locate the block starting `done_dir = os.path.join(plan_dir, "Done")` inside `run_plan` (the one followed two lines later by `source = inprogress_path if os.path.exists(inprogress_path) else plan_path`). Insert `_cleanup_verdicts_for_slug(verdict._slug_from_path(plan_path))` immediately before the `if os.path.exists(source):` guard.
>
> Site B (continue-to-done in `_consume_verdicts`): locate the block starting `done_dir = os.path.join(decisions_path, "Done")` inside the `if step_number >= total_steps_c:` branch. Insert `_cleanup_verdicts_for_slug(plan_slug)` immediately before the `shutil.move(full_plan_path, done_path)` line. `plan_slug` is already in scope from the enclosing loop.
>
> Site C (halt in `_consume_verdicts`): locate `halted_name = f"halted-{original_name}"` in the `else:` branch of the continue check. Insert `_cleanup_verdicts_for_slug(plan_slug)` immediately before the `shutil.move(full_plan_path, halted_path)` line.
>
> Commit: `"feat(bellows): sweep stranded verdict requests on terminal-state transitions"`.
>
> **Deliverable 3 — one-time startup sweep in `Bellows.start()`.** Locate the startup plan-scan loop (look for `print(f"Bellows: startup scan found {fname}")` — the loop iterating `self.config.get("watched_projects", [])` is immediately above it). Insert a new block BEFORE this loop that:
> 1. Collects the set of "active" plan slugs — iterate every watched_projects directory, collect slugs from all filenames in the directory root. For each filename: if it starts with `in-progress-` or `verdict-pending-`, strip that prefix and use `verdict._slug_from_path()` on the result. Otherwise check if `is_runnable_plan(fname)` returns True, and if so use `verdict._slug_from_path(fname)`. ALSO include plans in the `Done/` subdirectory — if `os.path.isdir(os.path.join(decisions_path, "Done"))`, iterate that directory and collect slugs from files ending in `.md` via `verdict._slug_from_path()`.
> 2. Iterate `BELLOWS_ROOT / "verdicts" / "pending"`, match every filename against regex `r"^verdict-request-(.+)-step-\d+\.md$"`, extract the slug (capture group 1), and delete any file whose extracted slug is NOT in the active set. Track deleted filenames in a list.
> 3. Print `Bellows: startup cleanup — {count} orphaned verdict requests removed` when count > 0, followed by one line per removed filename (indented with `  - `). Silent when count == 0.
>
> This is option (b) from the design review: sweep any request with no matching plan in any state (decisions root + Done). Per diagnostic section 5, this is safe — terminal-state plans cannot spawn new verdict requests.
>
> Commit: `"feat(bellows): one-time startup sweep for orphaned verdict requests"`.
>
> **Deliverable 4 — unit tests** in NEW file `bellows/tests/test_cleanup_verdicts.py`. Four tests. To keep the helper testable, refactor it to accept an optional `verdicts_root` parameter defaulting to `BELLOWS_ROOT / "verdicts" / "pending"` — this keeps the production call sites unchanged while allowing tests to pass a `tempfile.TemporaryDirectory` path. Tests:
>
> - `test_cleanup_removes_all_step_files_for_slug` — create `verdict-request-foo-2026-04-19-step-1.md`, `-step-2.md`, `-step-3.md`; call sweep with slug `foo-2026-04-19`; assert return value == 3 and all three files are gone.
> - `test_cleanup_noop_when_no_matches` — empty pending dir; call sweep with any slug; assert return value == 0, no errors.
> - `test_cleanup_respects_slug_boundary` — create `verdict-request-foo-2026-04-19-step-1.md` AND `verdict-request-foo-bar-2026-04-19-step-1.md`; call sweep with slug `foo-2026-04-19`; assert the `foo-bar-*` file is untouched and return value == 1. This is the prefix-collision test from diagnostic section 8(d).
> - `test_cleanup_ignores_resolved_directory` — create a sibling `resolved/` dir with `verdict-request-foo-2026-04-19-step-1.md` in it (the sweep should only touch `pending/`); call sweep pointed at `pending/`; assert the resolved file is untouched.
>
> Commit: `"test(bellows): unit tests for _cleanup_verdicts_for_slug"`.
>
> **Verification before reporting Complete:** Run `python3 -m pytest bellows/tests/test_cleanup_verdicts.py -v` — all 4 tests must pass. Run `python3 -c "import bellows; import bellows.bellows"` to verify the module still imports cleanly. Confirm `git --no-pager log --oneline -5` shows all four commits in order.
>
> **Deposit dev log at** `bellows/knowledge/development/verdict-lifecycle-coupling-2026-04-19.md` — include the four commit SHAs, the full test output, and the four deliverable files with line ranges of changes. Use the canonical Python file-write pattern: `with open("bellows/knowledge/development/verdict-lifecycle-coupling-2026-04-19.md", "w") as f: f.write(content)`. Append the Output Receipt per the template. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/development/verdict-lifecycle-coupling-2026-04-19.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — BELLOWS QA

---

> Before starting, read `bellows/knowledge/development/verdict-lifecycle-coupling-2026-04-19.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding.
>
> You are the Bellows QA Analyst. Read your specialist file at `bellows/agents/BELLOWS_QA.md`. Skip glossary read — mechanical verification work.
>
> **FIRST — Deliverable Verification (Rule 17).** Read the Step 1 dev log's "Files Created or Modified (Code)" list. For every listed file and change, verify it exists on disk and contains the described content. Produce a verification table: `| Deliverable | Expected | Status | Evidence |`. Mandatory verifications (pipe raw command output to evidence files per Rule 18 — use `python3 -c "import subprocess; r = subprocess.run([...], capture_output=True, text=True); open('path', 'w').write(r.stdout + r.stderr)"` or equivalent):
>
> - Helper function exists — `grep -n "def _cleanup_verdicts_for_slug" bellows/bellows.py` → `bellows/knowledge/qa/evidence/executable-verdict-lifecycle-coupling-2026-04-19/grep_helper.txt` (expect exactly 1 hit)
> - Call sites exist — `grep -n "_cleanup_verdicts_for_slug(" bellows/bellows.py` → `bellows/knowledge/qa/evidence/executable-verdict-lifecycle-coupling-2026-04-19/grep_call_sites.txt` (expect 4-5 hits: 1 def + 3 terminal sites, optionally +1 if startup sweep calls it by slug)
> - Startup sweep block exists — `grep -n "startup cleanup" bellows/bellows.py` → `bellows/knowledge/qa/evidence/executable-verdict-lifecycle-coupling-2026-04-19/grep_startup_sweep.txt` (expect 1 hit)
> - Test file collects 4 tests — `python3 -m pytest bellows/tests/test_cleanup_verdicts.py --collect-only -q` → `bellows/knowledge/qa/evidence/executable-verdict-lifecycle-coupling-2026-04-19/pytest_collect.txt`
> - Four commits — `git --no-pager log --oneline -5` → `bellows/knowledge/qa/evidence/executable-verdict-lifecycle-coupling-2026-04-19/git_log.txt`
>
> If ANY item is ❌, attempt to fix before proceeding. If unfixable, stop and report to CEO — do NOT move plan to Done.
>
> **Targeted test run:** `python3 -m pytest bellows/tests/test_cleanup_verdicts.py -v` → `bellows/knowledge/qa/evidence/executable-verdict-lifecycle-coupling-2026-04-19/pytest_targeted.txt`. All 4 tests must pass.
>
> **Full suite run (Rule 21 full-suite scope):** `python3 -m pytest bellows/tests/ -v` → `bellows/knowledge/qa/evidence/executable-verdict-lifecycle-coupling-2026-04-19/pytest_full.txt`. Record pass/fail/error counts in the QA report. The baseline from the 2026-04-19 `_handle` subdirectory guard work was 42/42 passing. Expected new total: 46/46 (42 pre-existing + 4 new). If any pre-existing tests fail, run `git --no-pager stash && python3 -m pytest bellows/tests/ -v` against main to determine if pre-existing or introduced.
>
> **Stranded-file baseline check:** Count files in `verdicts/pending/` before any test activity and record → `bellows/knowledge/qa/evidence/executable-verdict-lifecycle-coupling-2026-04-19/pending_counts.txt`. Format: `before_count = N\ncurrent filenames:\n<list>`. Note: the startup sweep only runs at Bellows daemon restart; this QA step does NOT restart Bellows, so the count will not decrease during this plan. The evidence is informational — plan verification does not depend on immediate pending/ reduction.
>
> **Deposit QA report at** `bellows/knowledge/qa/verdict-lifecycle-coupling-2026-04-19.md` using canonical Python file-write pattern. Include: deliverable verification table, targeted + full test run summaries, stranded-file baseline, Rule 20 self-check stdout.
>
> **Rule 20 — Mandatory QA Self-Check** — run this Python block at the end of the QA step and include the literal stdout in the QA report. If it prints FAILED, STOP — do not update PROJECT_STATUS, do not move plan to Done:
>
> ```python
> # Rule 20 — Mandatory QA Self-Check
> import os, sys
> plan_slug = "executable-verdict-lifecycle-coupling-2026-04-19"
> qa_report_path = "bellows/knowledge/qa/verdict-lifecycle-coupling-2026-04-19.md"
> evidence_dir = f"bellows/knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = [
>     "grep_helper.txt",
>     "grep_call_sites.txt",
>     "grep_startup_sweep.txt",
>     "pytest_collect.txt",
>     "git_log.txt",
>     "pytest_targeted.txt",
>     "pytest_full.txt",
>     "pending_counts.txt",
> ]
> hedging_keywords = ["pending", "inferred", "extrapolated", "estimated", "approximate", "skipped", "assumed", "close enough", "should pass", "would pass", "not run"]
> POSITIVE_STATUS_TOKENS = ["✅", "OK", "PASS", "[x]", "done", "complete", "verified"]
>
> def is_positive_row(line):
>     if "|" not in line:
>         return False
>     cells = [c.strip() for c in line.split("|")]
>     for cell in cells:
>         for token in POSITIVE_STATUS_TOKENS:
>             if token == "✅":
>                 if "✅" in cell:
>                     return True
>             else:
>                 if cell.lower() == token.lower():
>                     return True
>     return False
>
> failures = []
> if not os.path.isdir(evidence_dir):
>     failures.append(f"CRITICAL: evidence folder missing: {evidence_dir}")
> else:
>     for fname in required_evidence_files:
>         fpath = os.path.join(evidence_dir, fname)
>         if not os.path.isfile(fpath):
>             failures.append(f"CRITICAL: evidence file missing: {fpath}")
>         elif os.path.getsize(fpath) == 0:
>             failures.append(f"CRITICAL: evidence file empty: {fpath}")
> if os.path.isfile(qa_report_path):
>     with open(qa_report_path, "r") as f:
>         report = f.read()
>     for line in report.splitlines():
>         if is_positive_row(line):
>             lower = line.lower()
>             for kw in hedging_keywords:
>                 if kw in lower:
>                     failures.append(f"CRITICAL: hedging keyword '{kw}' in positive-status row: {line.strip()[:120]}")
>                     break
> else:
>     failures.append(f"CRITICAL: QA report not found at {qa_report_path}")
> print("=" * 60)
> print("Rule 20 — QA Self-Check Results")
> print("=" * 60)
> if failures:
>     print(f"FAILED — SELF-CHECK FAILED — {len(failures)} issue(s):")
>     for f in failures:
>         print(f"  - {f}")
>     print("\nPlan CANNOT close. Fix issues and re-run QA.")
>     sys.exit(1)
> else:
>     print("PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.")
>     print(f"Evidence folder: {evidence_dir}")
>     print(f"Files verified: {len(required_evidence_files)}")
> ```
>
> **If self-check PASSES, final housekeeping in order (Rule 23: feedback → commit → move-to-Done).** Do these as discrete operations (Rule 23(b)):
>
> **Step A — feedback append.** Append dated entry to `bellows/knowledge/research/agent-prompt-feedback.md` per standard protocol.
>
> **Step B — PROJECT_STATUS update.** Read `bellows/PROJECT_STATUS.md` first. Use `Desktop Commander:edit_block` to insert a new completed-milestone entry. Anchor: the exact line of the most recent `- 2026-04-19` entry under `## Completed`. Replace that line with itself followed by `\n- 2026-04-19 — Verdict lifecycle coupling shipped (BACKLOG #9 closed). New \`_cleanup_verdicts_for_slug\` helper sweeps stranded verdict-request files on three terminal-state transitions (auto-close, continue-to-done, halt) and on Bellows startup. Four call sites + 4 unit tests. REMINDER: restart Bellows to load startup sweep.`
>
> **Step C — BACKLOG.md update.** Read `bellows/knowledge/BACKLOG.md` first. Move the `2026-04-19: verdict lifecycle coupling` entry from `## Open` to `## Closed` via two discrete `Desktop Commander:edit_block` calls (one removes from Open, one adds to Closed with closure note prepended). Closure note: `**Closed 2026-04-19:** Shipped via executable-verdict-lifecycle-coupling-2026-04-19. _cleanup_verdicts_for_slug helper + 4 terminal-state call sites + one-time startup sweep + 4 unit tests. Commit range: <first SHA>..<last SHA>. REMINDER: restart Bellows to load startup sweep.`. Also close BACKLOG #1 (scope_check gate race condition, 2026-04-18 entry) — move to `## Closed` with note: `**Closed 2026-04-19:** Resolved as side-effect of verdict lifecycle coupling. The startup sweep cleans the stranded files #1 produces; option 3 of the originally-proposed fix candidates (clean stale verdict request on rename failure) is structurally equivalent to this plan's per-transition sweep.`
>
> **Step D — final commit.** Shell: `git add bellows/PROJECT_STATUS.md bellows/knowledge/BACKLOG.md bellows/knowledge/qa/verdict-lifecycle-coupling-2026-04-19.md bellows/knowledge/qa/evidence/executable-verdict-lifecycle-coupling-2026-04-19/ bellows/knowledge/research/agent-prompt-feedback.md && git commit -m "chore: QA close + status update for verdict lifecycle coupling"`.
>
> **Step E — move-to-Done.** Python: `import shutil; shutil.move("bellows/knowledge/decisions/in-progress-executable-verdict-lifecycle-coupling-2026-04-19.md", "bellows/knowledge/decisions/Done/executable-verdict-lifecycle-coupling-2026-04-19.md")`. Then shell: `git add bellows/knowledge/decisions/ && git commit -m "chore: move verdict-lifecycle-coupling plan to Done"`.
>
> **Deposits:**
> - `bellows/knowledge/qa/verdict-lifecycle-coupling-2026-04-19.md`
