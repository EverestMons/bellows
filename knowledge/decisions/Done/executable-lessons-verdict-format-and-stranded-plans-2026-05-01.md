# Governance — PLANNER_TEMPLATE Lessons Learned: Verdict Format, Verdict Semantics, Stranded Plans Audit
**Date:** 2026-05-01 | **Tier:** Small | **Test Scope:** targeted (markdown audit only, no test execution) | **Execution:** Step 1 (Bellows Documentation Analyst) → Step 2 (Bellows QA)
**Priority:** 1

## Context

Today's session surfaced three failure modes worth codifying as Lessons Learned rows in PLANNER_TEMPLATE.md:

1. **Verdict format mismatch** — Rule 25 documented `continue\n{reason}` but `bellows/verdicts/README.md` requires `verdict: continue\n{reason}`. The Planner stranded 13 verdict files before noticing. Root fix shipped via v4.30 plan (now in Done/). This Lessons row captures the meta-lesson: governance rules that interact with system components must match the system's actual requirements, not the Planner's mental model.
2. **Continue verdict semantics** — A continue verdict on a `verdict-pending-{slug}-step-N.md` advances to step N+1; it does NOT close the plan. Today's session triggered an accidental Step 2 dispatch on a 9-day-old stranded plan when the Planner deposited a continue verdict intending terminal-state cleanup but the plan had Step 2 unrun. Recovery required a stop verdict.
3. **Stranded plans audit** — Five plans from a 2-3 week window across 3 projects were stranded today (4 in invoice-pulse, 1 in bellows). Pattern suggests intermittent Bellows incidents and lifecycle ceremony loss, not per-plan governance violations. Systemic recovery via batched scan + per-plan triage is more efficient than catching them one at a time as they surface.

Version bump: 4.30 → 4.31. Three Lessons rows is a meaningful document change consistent with prior multi-row append precedents.

Test Scope: targeted — no production code, single governance-root file edit (PLANNER_TEMPLATE.md), mechanical verification via grep + git log. Per Position A, Step 2 is required even though work is markdown-only.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation before proceeding to Step 2.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/executable-lessons-verdict-format-and-stranded-plans-2026-05-01.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2.
```

---
---

## STEP 1 — Bellows Documentation Analyst

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-lessons-verdict-format-and-stranded-plans-2026-05-01.md", "bellows/knowledge/decisions/in-progress-executable-lessons-verdict-format-and-stranded-plans-2026-05-01.md")`. **Skip specialist file and glossary reads — this is a mechanical governance edit appending three Lessons Learned rows and bumping the version.** All commands run from `/Users/marklehn/Desktop/GitHub/`. **Use bash for all grep operations against PLANNER_TEMPLATE.md** — do NOT use the native Grep tool. **Task:** Apply three str_replace edits to PLANNER_TEMPLATE.md: (a) append three Lessons rows after the final existing row, (b) bump Version, (c) bump Last Updated. Use `Desktop Commander:edit_block` for each edit. **Edit 1 (append three Lessons rows):** find the exact line `| 2026-05-01 | Test names that imply a property must have assertions that verify that property. During the failed snapshot-fix close (see preceding entry), the DEV's test \`test_diff_immune_to_sibling_changes_in_unrelated_files\` had a name claiming sibling-immunity, but its assertions allowed sibling-modified files to appear in the diff — the test passed when \`plan_b_file.txt in diff_a\` was True. The mismatch was visible in the test's own commentary ("plan_b_file.txt DOES appear (it genuinely changed on disk) — but that's correct behavior for snapshot-based diff"). The Planner specified the test in the plan; the agent implemented it faithfully; QA passed it. The name-vs-assertion gap created false assurance. **Lesson:** when the Planner specifies a test in a plan, the assertion must encode the property the test name implies. If the property cannot be encoded as an assertion (because the implementation doesn't actually have the property), the test name is misleading and either the property or the name needs to change. A test named for immunity that passes when the property is violated is worse than no test — it provides false assurance and hides the bug from reviewers who skim test names rather than read assertions. |` and replace with that exact line followed by `\n` followed by these three new rows verbatim:
>
> ```
> | 2026-05-01 | Verdict format mismatch stranded 13 verdict files in a single session: PLANNER_TEMPLATE Rule 25's terminal-step resolution path documented the verdict file content as `continue\n{reason}`, but `bellows/verdicts/README.md` requires the literal `verdict:` prefix on line 1 (regex `^verdict:\s*(continue|stop)$`). Files lacking the prefix are silently rejected by Bellows's `_consume_verdicts()` — left in `resolved/` for retry, but retries never produce a different result without the prefix. The Planner deposited 13 malformed verdicts across multiple plan closeouts before noticing that resolved/ wasn't draining. Patching all 13 with a `verdict: ` prepend caused them to consume cleanly on the next scan. Root fix shipped via v4.30 governance plan (executable-rule-25-verdict-content-spec-fix-2026-05-01) which corrected three occurrences in PLANNER_TEMPLATE.md to match the README. **Meta-lesson:** when a Planner-side governance rule prescribes a behavior that interacts with a system component (parser, gate, watcher, daemon), the prescription must match the system's actual requirement, not the Planner's mental model. Discrepancies stay invisible until they fail at runtime, and they fail silently. Future rule-additions involving system interactions need a "does the README/source agree?" check at authoring time — read the README of the component the rule interacts with before specifying the rule's content. |
> | 2026-05-01 | Continue verdict semantics: a `verdict: continue` deposit on a `verdict-pending-{slug}-step-N.md` file advances the plan from step N to step N+1 — it does NOT close the plan. To close a non-terminal plan without running its remaining steps, deposit a `verdict: stop\n{reason}` (sends the plan to `halted-`) OR use the Planner-owned terminal-move pattern from Rule 25 (rename the plan file directly to `Done/` via `Filesystem:move_file`, then deposit a continue verdict for Bellows-side cleanup). Today's session triggered an accidental Step 2 dispatch on a 9-day-old stranded plan when the Planner deposited a continue verdict intending terminal-state cleanup but the plan had Step 2 unrun. Bellows correctly advanced to Step 2 (its declared semantics in the Plan Lifecycle State Machine), Step 2 ran and gate-failed on legitimate session-noise scope_check, recovery required a stop verdict. **Lesson:** "continue" means "advance"; "close" means either "terminal-step continue" (advances from step N to Done when N == total_steps) OR "stop" (halts at any step). The Planner conflated terminal-state Done/ move with a generic "approve-and-close" semantic that doesn't exist in Bellows. **Mechanical rule:** before depositing a continue verdict, check whether the plan's current step IS the terminal step (`Step:` field equals `Total Steps:` field in the verdict request). If yes, continue closes the plan. If no, continue advances to the next step. Treat them as different actions, not synonyms. |
> | 2026-05-01 | Stranded plans audit: five plans were silently stranded across 3 projects from a 2-3 week window before today's session caught them. Two plans from 2026-04-17 invoice-pulse (csv-upload-fetch-fix, gitattributes-crlf) both stranded mid-execution — work landed in production via commits, but plans never moved to `Done/`. One plan from 2026-04-23 bellows (planner-template-lessons-step-numbering) tripped a since-fixed permission gate (BACKLOG #2 closed 2026-04-28). Two diagnostic plans from 2026-04-20 and 2026-04-21 invoice-pulse (planner-governance-sweep, base-rates-method-not-allowed) completed cleanly but never received Rule 22 verification — their verdict requests had been sitting in `bellows/verdicts/pending/` for 10-11 days. Pattern suggests intermittent Bellows incidents (the April 17 cluster) and lifecycle ceremony loss (the April 20-23 cluster), not per-plan governance violations. The work in all five was real and verifiable; only the lifecycle ceremony was lost. Recovery cost ~5 minutes per plan via fresh QA executables OR direct `Filesystem:move_file` to Done/ when the original work was already verified. **Lesson:** when plans go silently stranded as a class (multiple plans from a single window), batch recovery is more efficient than per-plan triage. A "stranded plans audit" should be routine Planner discipline — periodically scan all watched projects for plan files with non-Done/non-halted prefixes older than ~30 days. Cheap audit script: `for proj in */; do find $proj/knowledge/decisions -maxdepth 1 -name "in-progress-*" -o -name "verdict-pending-*" | xargs -I{} stat -f "%m %N" {} | awk -v cutoff=$(date -v-30d +%s) '$1 < cutoff'; done`. Recovery options per stranded plan: (a) fresh QA executable if work needs re-verification, (b) direct Done/ move if work was already verified by the original QA, (c) stop verdict if work is being abandoned. Today's session caught 5; without the audit they would have continued accumulating indefinitely. |
> ```
>
> **Edit 2 (Version bump):** find the exact line `**Version:** 4.30` and replace with `**Version:** 4.31`. **Edit 3 (Last Updated bump):** find the exact line `**Last Updated:** 2026-05-01 (v4.30)` and replace with `**Last Updated:** 2026-05-01 (v4.31)`. After all three edits, verify by running `bash`: `tail -20 PLANNER_TEMPLATE.md > /tmp/verify.txt && grep -n "^**Version:** 4.31$" PLANNER_TEMPLATE.md >> /tmp/verify.txt && cat /tmp/verify.txt`. Expect three new Lessons rows visible at the tail and Version 4.31 match. **Deposit dev log** at `bellows/knowledge/development/lessons-verdict-format-and-stranded-plans-dev-log-2026-05-01.md` containing: (1) verbatim anchor for each of the 3 edits, (2) summary of the 3 new Lessons rows (one-line each), (3) verification grep output. **Commit:** governance root — `cd /Users/marklehn/Desktop/GitHub && git add PLANNER_TEMPLATE.md && git commit -m "docs(planner): v4.31 — Lessons rows for verdict format, verdict semantics, stranded plans audit"`. **Then dev log to bellows:** `cd /Users/marklehn/Desktop/GitHub/bellows && git add knowledge/development/lessons-verdict-format-and-stranded-plans-dev-log-2026-05-01.md && git commit -m "docs: dev log for PLANNER_TEMPLATE v4.31 Lessons additions"; cd /Users/marklehn/Desktop/GitHub`. Split-commit pattern per Plan File Structure rule. **Standard prompt feedback protocol** → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/development/lessons-verdict-format-and-stranded-plans-dev-log-2026-05-01.md`
> - `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — Bellows QA

---

> **Before starting, read `bellows/knowledge/development/lessons-verdict-format-and-stranded-plans-dev-log-2026-05-01.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding.** **Skip specialist file and glossary reads — this is mechanical QA for a Lessons table append.** All commands run from `/Users/marklehn/Desktop/GitHub/`. **Use bash for all grep operations against PLANNER_TEMPLATE.md** — do NOT use the native Grep tool.
>
> **FIRST — Deliverable Verification.** Read the Step 1 dev log "Files Created or Modified" list. Verify every listed deliverable exists with the described change.
>
> **Verification checks (each deposits literal output to `bellows/knowledge/qa/evidence/executable-lessons-verdict-format-and-stranded-plans-2026-05-01/`):**
>
> (1) **Verdict format Lessons row present** — `grep -n "Verdict format mismatch stranded 13 verdict files" PLANNER_TEMPLATE.md > bellows/knowledge/qa/evidence/executable-lessons-verdict-format-and-stranded-plans-2026-05-01/grep_row_1.txt 2>&1`. Expect exactly 1 match.
>
> (2) **Continue verdict semantics Lessons row present** — `grep -n "Continue verdict semantics: a \`verdict: continue\` deposit" PLANNER_TEMPLATE.md > bellows/knowledge/qa/evidence/executable-lessons-verdict-format-and-stranded-plans-2026-05-01/grep_row_2.txt 2>&1`. Expect exactly 1 match.
>
> (3) **Stranded plans audit Lessons row present** — `grep -n "Stranded plans audit: five plans were silently stranded" PLANNER_TEMPLATE.md > bellows/knowledge/qa/evidence/executable-lessons-verdict-format-and-stranded-plans-2026-05-01/grep_row_3.txt 2>&1`. Expect exactly 1 match.
>
> (4) **Anchor row preserved (test names property assertion row)** — `grep -c "Test names that imply a property must have assertions" PLANNER_TEMPLATE.md > bellows/knowledge/qa/evidence/executable-lessons-verdict-format-and-stranded-plans-2026-05-01/grep_anchor.txt 2>&1`. Expect count `1`.
>
> (5) **Version bumped to 4.31** — `grep -n "^\*\*Version:\*\* 4.31$" PLANNER_TEMPLATE.md > bellows/knowledge/qa/evidence/executable-lessons-verdict-format-and-stranded-plans-2026-05-01/grep_version.txt 2>&1`. Expect exactly 1 match.
>
> (6) **Adjacency check (3 new rows immediately after anchor)** — `awk -F: '{print $1}' bellows/knowledge/qa/evidence/executable-lessons-verdict-format-and-stranded-plans-2026-05-01/grep_anchor.txt > /tmp/anchor_count.txt; grep -n "Test names that imply a property" PLANNER_TEMPLATE.md | head -1 | awk -F: '{print $1}' > /tmp/anchor_line.txt; grep -n "Verdict format mismatch stranded" PLANNER_TEMPLATE.md | head -1 | awk -F: '{print $1}' > /tmp/row1_line.txt; echo "anchor_line: $(cat /tmp/anchor_line.txt) | row1_line: $(cat /tmp/row1_line.txt) | diff: $(($(cat /tmp/row1_line.txt) - $(cat /tmp/anchor_line.txt)))" > bellows/knowledge/qa/evidence/executable-lessons-verdict-format-and-stranded-plans-2026-05-01/adjacency_check.txt 2>&1`. Expect `diff: 1` (Row 1 immediately after the anchor).
>
> (7) **Governance-root commit landed** — `cd /Users/marklehn/Desktop/GitHub && git --no-pager log -1 --name-only -- PLANNER_TEMPLATE.md > bellows/knowledge/qa/evidence/executable-lessons-verdict-format-and-stranded-plans-2026-05-01/git_commit_governance.txt 2>&1; cd /Users/marklehn/Desktop/GitHub`. Expect commit message includes "v4.31" and the file list contains `PLANNER_TEMPLATE.md`.
>
> **Deposit QA report** to `bellows/knowledge/qa/lessons-verdict-format-and-stranded-plans-qa-2026-05-01.md` with the verification table citing each evidence file path in the Evidence column. **Include the literal stdout of the Rule 20 self-check block in the QA report body.**
>
> **Mandatory Rule 20 self-check block (execute verbatim from /Users/marklehn/Desktop/GitHub/, include literal stdout in QA report):**
>
> ```python
> import os, sys
> plan_slug = "executable-lessons-verdict-format-and-stranded-plans-2026-05-01"
> qa_report_path = "bellows/knowledge/qa/lessons-verdict-format-and-stranded-plans-qa-2026-05-01.md"
> evidence_dir = f"bellows/knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = [
>     "grep_row_1.txt",
>     "grep_row_2.txt",
>     "grep_row_3.txt",
>     "grep_anchor.txt",
>     "grep_version.txt",
>     "adjacency_check.txt",
>     "git_commit_governance.txt",
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
> If the self-check prints `FAILED`, STOP — do not proceed with closeout, report to CEO. If `PASSED`, proceed with closeout in this exact order per Rule 23: **Step A — Feedback append.** Standard prompt feedback protocol → append entry to `bellows/knowledge/research/agent-prompt-feedback.md`. **Step B — Final commit.** `cd /Users/marklehn/Desktop/GitHub/bellows && git add knowledge/qa/ knowledge/research/agent-prompt-feedback.md && git commit -m "qa: PLANNER_TEMPLATE v4.31 Lessons additions verified"; cd /Users/marklehn/Desktop/GitHub`. **STOP. Plan complete after this step. Do NOT move the plan to Done — the Planner performs the terminal move after Rule 22 verification per Rule 25.**
>
> **Deposits:**
> - `bellows/knowledge/qa/lessons-verdict-format-and-stranded-plans-qa-2026-05-01.md`
> - `bellows/knowledge/qa/evidence/executable-lessons-verdict-format-and-stranded-plans-2026-05-01/grep_row_1.txt`
> - `bellows/knowledge/qa/evidence/executable-lessons-verdict-format-and-stranded-plans-2026-05-01/grep_row_2.txt`
> - `bellows/knowledge/qa/evidence/executable-lessons-verdict-format-and-stranded-plans-2026-05-01/grep_row_3.txt`
> - `bellows/knowledge/qa/evidence/executable-lessons-verdict-format-and-stranded-plans-2026-05-01/grep_anchor.txt`
> - `bellows/knowledge/qa/evidence/executable-lessons-verdict-format-and-stranded-plans-2026-05-01/grep_version.txt`
> - `bellows/knowledge/qa/evidence/executable-lessons-verdict-format-and-stranded-plans-2026-05-01/adjacency_check.txt`
> - `bellows/knowledge/qa/evidence/executable-lessons-verdict-format-and-stranded-plans-2026-05-01/git_commit_governance.txt`
