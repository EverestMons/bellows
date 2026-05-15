# Governance — Lessons Learned: Bellows Step Parser Is 1-Indexed
**Date:** 2026-04-23 | **Tier:** Small | **Test Scope:** none | **Execution:** Step 1 (Documentation Agent) → Step 2 (QA Agent)
**Priority:** 2

## Context

A forge-cycle-12 plan authored earlier today used `## STEP 0 —` as its first step header (pre-scan sync preface) with subsequent steps numbered 1–5. Bellows dispatched the plan, its step parser counted headers positionally (1-indexed), and dispatched what it called "step 1" — which hit the author's STEP 1 (Ingest). Ingest's prior-step-verification instruction expected STEP 0's deposit, which had never been created because Bellows never ran it. The gate tripped on Step 1's downstream missing deposit; the root cause was in the header numbering. Recovery in progress via a separate renumber plan.

Per CEO decision: this gets codified as a Lessons Learned entry, not a new Rule. The invariant lives in how Bellows parses plans, not in a policy choice the Planner makes. A Lessons entry compounds via context-loading Phase 1.5 and Forge pattern synthesis without inflating the rules list with mechanical facts.

No version bump — Lessons additions don't force a version increment (standalone Lessons entries are appended without version changes; version bumps attach to Rule additions or rewrites).

Test Scope: none — single-file governance edit, no code, no tests.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation ("ok") before proceeding to Step 2.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/executable-planner-template-lessons-step-numbering-2026-04-23.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — Documentation Agent

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-planner-template-lessons-step-numbering-2026-04-23.md", "bellows/knowledge/decisions/in-progress-executable-planner-template-lessons-step-numbering-2026-04-23.md")`. **Skip specialist file and glossary reads — this is a mechanical governance edit.** All commands run from `/Users/marklehn/Desktop/GitHub/`. **Task:** Append a single Lessons Learned row to `PLANNER_TEMPLATE.md` at governance root. The anchor is the final existing Lessons row (the 2026-04-20 v4.26 governance sweep entry). Use `Desktop Commander:edit_block` to find the exact line `| 2026-04-20 | v4.26 governance sweep: six edits derived from a diagnostic pass over BACKLOG items deferred since v4.18 — (1) Rule 20 \`[x]\` dead code removal from POSITIVE_STATUS_TOKENS list; (2) Plan File Structure: commit-repo-location rule for governance-root edits; (3) Rule 14 state-transition enumeration extension; (4) Rule 13 fourth anchoring technique for UI placement; (5) Lessons entry codifying Position A (no markdown-only QA carve-out, immediately above); (6) this summary row. The sweep followed the v4.18 lesson: the focused diagnostic of PLANNER_TEMPLATE.md ran BEFORE the executable, producing a contradictions-and-duplications scan for each proposed change — no contradictions found, one partial overlap (Rule 13's existing UXD anchoring language) which the fourth-technique addition extends rather than duplicates. **Meta-lesson:** the Planner's scan-for-contradictions pass at plan-authoring time (formalized after the v4.18 Rule 22/Rule 8 contradiction) is doing its job — it let this sweep ship five rule changes in a single plan without the kind of downstream-contradiction failure that caused v4.18 to ship a conflict. The diagnostic-before-executable pattern for governance plans should now be considered standard, not optional. |` and replace with that line followed by `\n` followed by the new Lessons row. The new row verbatim (single table row, pipe-delimited):
>
> ```
> | 2026-04-23 | Bellows' step parser is positional and 1-indexed — every `## STEP N —` header in a plan becomes Bellows step 1, 2, 3, ... regardless of the value of N. A plan that opens with `## STEP 0 —` still has its first header counted as step 1 for Bellows' purposes. This surfaced during `forge-cycle-12-2026-04-23`: the plan used STEP 0 as a pre-scan sync preface and numbered the rest 1–5, but Bellows dispatched "step 1" which hit the author's STEP 1 (Ingest) — a step whose prior-step-verification instruction expected STEP 0's deposit, which had not been created because Bellows never ran it. The gate tripped on Step 1's downstream missing deposit; the root cause was in the header numbering. **Lesson:** plan step headers start at `## STEP 1 —`. The N in "STEP N" is a positional label that must match Bellows' step index, not a free-form convention. A "pre-flight" or "setup" step either gets numbered `STEP 1` like everything else or is done outside the plan (CEO-side shell command, git pull in the bootstrap, etc.). Using non-1-indexed headers produces silent off-by-one dispatch failures where the gate trips far from the actual authoring bug. |
> ```
>
> After the edit, verify by reading the tail of PLANNER_TEMPLATE.md (`Filesystem:read_text_file` with `tail: 5`) and confirm the new row is the final line in the Lessons Learned table. **Deposit dev log** at `bellows/knowledge/development/planner-template-lessons-step-numbering-dev-log-2026-04-23.md` with: (1) verbatim line of the anchor row found, (2) verbatim new row appended, (3) tail-read confirmation showing the new row is last, (4) any issues encountered. **Commit:** the edit is at governance-root — `cd /Users/marklehn/Desktop/GitHub && git add PLANNER_TEMPLATE.md bellows/knowledge/development/planner-template-lessons-step-numbering-dev-log-2026-04-23.md && git commit -m "docs(planner): lessons entry — Bellows step parser is 1-indexed"`. **Standard prompt feedback protocol** → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/development/planner-template-lessons-step-numbering-dev-log-2026-04-23.md`
> - `PLANNER_TEMPLATE.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — QA Agent

---

> **Before starting, read `bellows/knowledge/development/planner-template-lessons-step-numbering-dev-log-2026-04-23.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding.** **Skip specialist file and glossary reads — this is mechanical QA for a single-row governance edit.** All commands run from `/Users/marklehn/Desktop/GitHub/`.
>
> **FIRST — Deliverable Verification.** Read the Step 1 dev log "Files Created or Modified" list. Verify every listed deliverable exists with the described change. Produce a verification table: | Deliverable | Expected | Status (✅/❌) | Evidence |.
>
> **Verification checks (each deposits literal output to `bellows/knowledge/qa/evidence/executable-planner-template-lessons-step-numbering-2026-04-23/`):**
>
> (1) Grep for the new Lessons row anchor — the `2026-04-23` date and the distinctive phrase `Bellows' step parser is positional and 1-indexed`: `grep -n "Bellows' step parser is positional and 1-indexed" PLANNER_TEMPLATE.md > bellows/knowledge/qa/evidence/executable-planner-template-lessons-step-numbering-2026-04-23/grep_new_row.txt 2>&1`. Expect exactly 1 match.
>
> (2) Confirm the new row is the final line of the Lessons Learned table (no orphan rows after it): `tail -3 PLANNER_TEMPLATE.md > bellows/knowledge/qa/evidence/executable-planner-template-lessons-step-numbering-2026-04-23/tail_check.txt 2>&1`. Expect the tail to contain the new 2026-04-23 row followed by the `## Forge Observations` section header or similar — not another stray table row.
>
> (3) Confirm the v4.26 governance-sweep anchor row is still present (did not get overwritten): `grep -c "2026-04-20 | v4.26 governance sweep" PLANNER_TEMPLATE.md > bellows/knowledge/qa/evidence/executable-planner-template-lessons-step-numbering-2026-04-23/grep_anchor_preserved.txt 2>&1`. Expect count 1.
>
> (4) Confirm version header unchanged (still v4.26): `grep "^\*\*Version:\*\*" PLANNER_TEMPLATE.md > bellows/knowledge/qa/evidence/executable-planner-template-lessons-step-numbering-2026-04-23/grep_version.txt 2>&1`. Expect `**Version:** 4.26`.
>
> (5) Git log — last commit from governance-root repo: `cd /Users/marklehn/Desktop/GitHub && git --no-pager log -1 --name-only > bellows/knowledge/qa/evidence/executable-planner-template-lessons-step-numbering-2026-04-23/git_commit.txt 2>&1`. Expect commit includes `PLANNER_TEMPLATE.md` and the dev log.
>
> **Deposit QA report** to `bellows/knowledge/qa/planner-template-lessons-step-numbering-qa-2026-04-23.md` with the verification table citing each evidence file path in the Evidence column. **Include the literal stdout of the Rule 20 self-check block in the QA report body.**
>
> **Mandatory Rule 20 self-check block (execute verbatim, include literal stdout in QA report):**
>
> ```python
> import os, sys
> plan_slug = "executable-planner-template-lessons-step-numbering-2026-04-23"
> qa_report_path = "bellows/knowledge/qa/planner-template-lessons-step-numbering-qa-2026-04-23.md"
> evidence_dir = f"bellows/knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = [
>     "grep_new_row.txt",
>     "tail_check.txt",
>     "grep_anchor_preserved.txt",
>     "grep_version.txt",
>     "git_commit.txt",
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
> If the self-check prints `FAILED`, STOP — do not move plan to Done, report to CEO. If `PASSED`, proceed with closeout in this exact order per Rule 23.
>
> **Step A — Feedback append.** Standard prompt feedback protocol → append entry to `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Step B — Final commit.** `cd /Users/marklehn/Desktop/GitHub && git add bellows/knowledge/qa/ bellows/knowledge/research/agent-prompt-feedback.md && git commit -m "chore: QA + feedback for PLANNER_TEMPLATE lessons-step-numbering"`.
>
> **Step C — Move-to-Done (last).** `import shutil; shutil.move("bellows/knowledge/decisions/in-progress-executable-planner-template-lessons-step-numbering-2026-04-23.md", "bellows/knowledge/decisions/Done/executable-planner-template-lessons-step-numbering-2026-04-23.md")` then `cd /Users/marklehn/Desktop/GitHub && git add -A bellows/knowledge/decisions/ && git commit -m "chore: move PLANNER_TEMPLATE lessons-step-numbering plan to Done"`.
>
> **Deposits:**
> - `bellows/knowledge/qa/planner-template-lessons-step-numbering-qa-2026-04-23.md`
> - `bellows/knowledge/qa/evidence/executable-planner-template-lessons-step-numbering-2026-04-23/grep_new_row.txt`
> - `bellows/knowledge/qa/evidence/executable-planner-template-lessons-step-numbering-2026-04-23/tail_check.txt`
> - `bellows/knowledge/qa/evidence/executable-planner-template-lessons-step-numbering-2026-04-23/grep_anchor_preserved.txt`
> - `bellows/knowledge/qa/evidence/executable-planner-template-lessons-step-numbering-2026-04-23/grep_version.txt`
> - `bellows/knowledge/qa/evidence/executable-planner-template-lessons-step-numbering-2026-04-23/git_commit.txt`
>
> **STOP. Plan complete after this step.**
