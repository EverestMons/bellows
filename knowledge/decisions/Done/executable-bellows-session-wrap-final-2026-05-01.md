# bellows — Session Wrap Final 2026-05-01
**Date:** 2026-05-01 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (Documentation) → Step 2 (QA)

## CEO Context

**Test Scope: targeted** — no test execution. The session-end full suite per Rule 21 was already run at 22:36:09 by the F3 removal plan's Step 2 (last plan to touch test files). That output (`bellows/knowledge/qa/evidence/executable-remove-phase-3b-3c-2026-05-01/pytest_full.txt`) IS the session-end ledger entry; this wrap references it rather than re-running.

**Why this exists.** The session-wrap-v2 plan (closed 21:00:something) covered three plans: cleanup-slug-normalization, inactivity-timeout-bump, and the original session-wrap halt. Since then, two MORE plans have shipped:
- `diagnostic-phase-3b-mechanism-and-cost-benefit-2026-05-01` (closed 21:55-ish)
- `executable-remove-phase-3b-3c-2026-05-01` (closed 22:38-ish)

This wrap captures those in PROJECT_STATUS so the project record is complete.

**No PLANNER_TEMPLATE edits.** The Phase 3b investigation reinforced existing lessons (snapshot-fix evidence-driven recommendation, Rule 13 anchoring) — they were applied correctly, which is the goal. No new lessons emerged.

**No new BACKLOG entries.** The "Phase 3b/3c slug-collision" entry added by session-wrap-v2 was closed in the F3 plan's Step 2. The "inline-replicated startup-sweep test indirection" entry remains open as a low-priority test-quality refactor. Nothing to add.

**Slug discipline.** Using `-final-` in the slug to avoid any collision with the still-orphan `bellows-session-wrap-2026-05-01` DB rows. With Phase 3b/3c removed those rows are inert, but a unique slug is cheap insurance until the orphan rows are manually deleted.

## How to Run This Plan

Paste the bootstrap into Claude Code. After Step 1 reports Complete, CEO confirms ("ok") to advance to Step 2.

**Bootstrap:**
```
Read the plan at bellows/knowledge/decisions/executable-bellows-session-wrap-final-2026-05-01.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — BELLOWS DOCUMENTATION ANALYST

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-bellows-session-wrap-final-2026-05-01.md", "bellows/knowledge/decisions/in-progress-executable-bellows-session-wrap-final-2026-05-01.md")`.
>
> You are the Bellows Documentation Analyst. Skip specialist file and glossary reads — this is one anchored markdown edit.
>
> **Edit — PROJECT_STATUS.md.** Read `bellows/PROJECT_STATUS.md` first. The session-wrap-v2 plan added an entry earlier today: "2026-05-01 (session): Closed BACKLOG #3 ..." — find the verbatim text of that entry as the anchor. Use the `Edit` tool to insert a new entry IMMEDIATELY AFTER the v2 entry. The new entry text:
>
> "2026-05-01 (later session): Two additional plans shipped after the session-wrap-v2 close. (1) `diagnostic-phase-3b-mechanism-and-cost-benefit-2026-05-01` — investigated the phantom-resume bug observed during the original session-wrap dispatch. SA characterized DB state with literal SQL evidence (rows 554-556 from prior session triggered phantom resume of fresh wrap deposit). Q6 cost-benefit recommended F3 (remove Phase 3b/3c) over patch (F1) and simplify (F2) — Phase 3b/3c guarded the manual-rename resume path that's unsupported per Rule 25, while the supported verdict-resume path passes resume_step explicitly without consulting the DB. (2) `executable-remove-phase-3b-3c-2026-05-01` — implemented F3: removed `_get_last_completed_step` (L175-188), DB-resume guard (L243-247), Phase 3c hash-drift block (L249-254), `import hashlib`. Deleted 5 Phase 3b/3c canary tests; added regression test `test_dispatch_starts_fresh_when_db_has_orphan_slug_rows` exercising production `run_plan` directly. Net ~30 LOC removed from bellows.py. Eliminates phantom-resume bug class structurally. plan_slug column preserved for analytics. Test count: 180→176 passing (5 deleted + 1 added) + 1 known pre-existing failure. CEO restart required to load."
>
> Use the `Edit` tool with the v2 entry's verbatim text as `old_str` and append the new entry text below it as `new_str`.
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Commit:** `cd /Users/marklehn/Desktop/GitHub && git add bellows/PROJECT_STATUS.md bellows/knowledge/research/agent-prompt-feedback.md && git commit -m "docs: session wrap final 2026-05-01 — Phase 3b/3c diag + F3 removal entries"`.
>
> **Deposits:**
> - `bellows/PROJECT_STATUS.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — BELLOWS QA

---

> Before starting, read `bellows/PROJECT_STATUS.md` to verify Step 1 edit landed. If the new entry isn't there, stop and report.
>
> You are the Bellows QA Agent. Skip specialist file and glossary reads — this is verification of one markdown edit.
>
> **FIRST — Deliverable Verification (Rule 17).** Read Step 1's commit log. Verify PROJECT_STATUS.md contains the new entry. Produce a verification table.
>
> **Run four verification checks** with output to evidence files. Create the directory: `mkdir -p bellows/knowledge/qa/evidence/executable-bellows-session-wrap-final-2026-05-01`.
>
> Check 1 — PROJECT_STATUS contains the new entry: `grep -n "2026-05-01 (later session)" bellows/PROJECT_STATUS.md > bellows/knowledge/qa/evidence/executable-bellows-session-wrap-final-2026-05-01/grep_new_entry.txt` — expect at least one match.
>
> Check 2 — New entry mentions both plans: `grep -E "diagnostic-phase-3b-mechanism|executable-remove-phase-3b-3c" bellows/PROJECT_STATUS.md > bellows/knowledge/qa/evidence/executable-bellows-session-wrap-final-2026-05-01/grep_plan_refs.txt` — expect both plan filenames present.
>
> Check 3 — Session-end ledger reference (the F3 plan's pytest_full.txt) is present and shows expected count: `tail -3 bellows/knowledge/qa/evidence/executable-remove-phase-3b-3c-2026-05-01/pytest_full.txt > bellows/knowledge/qa/evidence/executable-bellows-session-wrap-final-2026-05-01/session_end_ledger.txt` — expect "176 passed" and "1 failed" in the tail.
>
> Check 4 — Commit landed: `git --no-pager log -1 --name-only -- bellows/PROJECT_STATUS.md > bellows/knowledge/qa/evidence/executable-bellows-session-wrap-final-2026-05-01/git_log_commit.txt` — expect commit message includes "session wrap final" and file list shows `bellows/PROJECT_STATUS.md`.
>
> Deposit the QA report at `bellows/knowledge/qa/session-wrap-final-qa-2026-05-01.md` with verification table citing each evidence file path.
>
> **Then run the mandatory Rule 20 self-check Python block:**
>
> ```python
> # Rule 20 — Mandatory QA Self-Check
> import os, sys
> plan_slug = "executable-bellows-session-wrap-final-2026-05-01"
> qa_report_path = "bellows/knowledge/qa/session-wrap-final-qa-2026-05-01.md"
> evidence_dir = f"bellows/knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = [
>     "grep_new_entry.txt",
>     "grep_plan_refs.txt",
>     "session_end_ledger.txt",
>     "git_log_commit.txt",
> ]
> hedging_keywords = ["pending", "inferred", "extrapolated", "estimated", "approximate", "skipped", "assumed", "close enough", "should pass", "would pass", "not run"]
> POSITIVE_STATUS_TOKENS = ["✅", "OK", "PASS", "done", "complete", "verified"]
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
> Include the literal stdout in the QA report. Standard prompt feedback protocol.
>
> **Final commit:** `cd /Users/marklehn/Desktop/GitHub && git add bellows/knowledge/qa/session-wrap-final-qa-2026-05-01.md bellows/knowledge/qa/evidence/executable-bellows-session-wrap-final-2026-05-01/ bellows/knowledge/research/agent-prompt-feedback.md && git commit -m "qa: session wrap final verified — 6 plans this session, 4 closed cleanly"`. **STOP.** Do NOT move this plan to Done/. Per the disable-auto-close model, the Planner performs the terminal move after Rule 22 verification passes.
>
> **Deposits:**
> - `bellows/knowledge/qa/session-wrap-final-qa-2026-05-01.md`
> - `bellows/knowledge/qa/evidence/executable-bellows-session-wrap-final-2026-05-01/`
> - `bellows/knowledge/research/agent-prompt-feedback.md`
