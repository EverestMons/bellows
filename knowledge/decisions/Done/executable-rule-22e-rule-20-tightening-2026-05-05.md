# Governance — Rule 22 (e) Tightening for Rule 20 Self-Check Verification (v4.34)
**Date:** 2026-05-05 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (Documentation Agent) → Step 2 (QA Agent)

**Test Scope justification:** targeted — markdown-only governance edit, no production code, no test suite to run, evidence captured via grep verification.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code, OR let Bellows pick it up. Bellows OP-001 is resolved (2026-05-05) and Bellows-self plans run in-place without worktree isolation. **Do NOT manually edit PLANNER_TEMPLATE.md while this plan is executing** — the plan modifies it, and concurrent edits will trip scope_check.

Per the governance-root commit-repo rule (Plan File Structure → Commit repo for governance-root edits): edits to `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` commit to the governance-root repo at `/Users/marklehn/Desktop/GitHub/`. The plan's housekeeping (move-to-Done, plan deposit) lives in the bellows repo since the plan file itself is in `bellows/knowledge/decisions/`. This is the split-commit pattern.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/executable-rule-22e-rule-20-tightening-2026-05-05.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — Bellows Documentation Analyst

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-rule-22e-rule-20-tightening-2026-05-05.md", "bellows/knowledge/decisions/in-progress-executable-rule-22e-rule-20-tightening-2026-05-05.md")`. **Skip glossary read — this is a governance markdown edit task.** Read your specialist file at `bellows/agents/BELLOWS_DOCUMENTATION_ANALYST.md` first. **Task:** make two edits to `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md`. **Edit 1 — Tighten Rule 22 (e) text.** Use the Filesystem:edit_file MCP tool (or Desktop Commander:edit_block) to replace the exact existing line `- **(e)** For QA reports specifically: does the Rule 20 self-check output show PASSED, and are all required evidence files actually present in the evidence directory?` with the new text `- **(e)** For QA reports specifically: the literal Rule 20 banner string \`Rule 20 — QA Self-Check Results\` MUST be present, immediately followed (within the same code block or section) by a line beginning with \`PASSED — SELF-CHECK PASSED\`. Section header without banner = fabrication; banner without PASSED line = self-check ran but failed. Both halt the plan. All required evidence files must also be present in the evidence directory.` This is an anchored edit per Rule 23(a) — the old_string must match the existing line verbatim including the leading `- **(e)**` prefix. Use only one edit_file call for this replacement. **Edit 2 — Update version metadata.** Replace the exact line `**Version:** 4.33` with `**Version:** 4.34`. Replace the exact line `**Last Updated:** 2026-05-05 (v4.33)` with `**Last Updated:** 2026-05-05 (v4.34)`. Two anchored edits, one for each line. **Edit 3 — Append Lessons row.** Append a new row to the Lessons Learned table at the bottom of PLANNER_TEMPLATE.md. The new row must appear AFTER the existing `2026-05-05` row (the NEXT_SESSION.md / population audit lesson) and BEFORE the closing `---` separator that follows the Lessons table. Use Filesystem:edit_file with the verbatim anchor `| 2026-05-05 | NEXT_SESSION.md framing` (the start of the most recent Lessons row) — find the END of that row (the closing `|` followed by newline) and insert the new row immediately after. The new row content (replace `<NEWROW>` with this single-line markdown table row): `| 2026-05-05 | Rule 20 self-check fabrication — agent wrote the section header without executing the Python block, then claimed "SELF-CHECK PASSED" verbally. Diagnostic of 10 invoice-pulse QA reports found 1 fabrication (banner present, Python block empty) + 4 omissions (no Rule 20 section at all) + 5 clean. Two failure modes, same root cause: no mechanical detection of missing or empty Rule 20 output in the deposited QA file. Two-part fix: **(1) Bellows-side gate** — new \`_gate_rule_20_self_check\` in \`gates.py\` runs only on QA steps, reads the deposited QA report, fails if banner missing or banner without PASSED line. Shipped 2026-05-05 with 8 new tests. **(2) Rule 22 (e) tightening (this entry)** — replaces the original loose phrasing ("does the self-check output show PASSED") with explicit banner-and-PASSED-line specificity. Both layers compose: Bellows mechanically blocks fabrication on QA-step pause; Rule 22 (e) is the Planner's belt-and-suspenders verification on Bellows-bypassed paths and pre-Bellows historical reports. **Meta-lesson:** governance enforcement at the rule layer must specify what the mechanical gate is checking for, not what it *should* be checking for. The original (e) text said "does the output show PASSED" which a fabricated report could trivially appear to satisfy on visual scan; the new text names the literal banner string the gate enforces, making the rule and the code agree at the byte level. Pattern: every Planner-side rule that pairs with a mechanical gate names the literal token, regex, or filename the gate matches. |`. **The exact insertion mechanic:** find the verbatim string `**Mechanical guidance:** before authoring a follow-up diagnostic for any BACKLOG item with multiple reproductions, run \`git --no-pager log --since=<earliest-reproduction-date> --oneline -- <suspected-file>\` and check whether any commit message matches the recommended fix shape from the BACKLOG entry. If yes, the next diagnostic should be a population audit, not a fresh design pass. |` (this is the END of the most recent existing Lessons row). Replace it with that exact string followed by `\n` followed by the new row content above. This anchored edit ensures the new row lands immediately after the existing 2026-05-05 entry. **Verify all three edits landed** by reading `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` lines around each anchor: line 4 (version), line 5 (last updated), the (e) bullet under Rule 22, and the new Lessons row at the bottom of the table. **Commit both repos per the split-commit pattern.** Run from the governance root: `cd /Users/marklehn/Desktop/GitHub && git --no-pager log -1 PLANNER_TEMPLATE.md && git add PLANNER_TEMPLATE.md && git commit -m "docs: PLANNER_TEMPLATE v4.34 — Rule 22 (e) tightening for Rule 20 banner verification"`. **Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.** **Then commit the bellows repo** for the plan housekeeping: `cd /Users/marklehn/Desktop/GitHub/bellows && git add knowledge/research/agent-prompt-feedback.md && git --no-pager log -1 && git commit -m "docs: prompt feedback — Bellows Documentation Analyst Rule 22e tightening"`. **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation.**
>
> **Deposits:**
> - `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md`

---
---

## STEP 2 — Bellows QA

---

> **FIRST — verify the plan is in-progress.** Verify the file exists at `bellows/knowledge/decisions/in-progress-executable-rule-22e-rule-20-tightening-2026-05-05.md`. **Before starting, verify Step 1 commits landed.** Run `cd /Users/marklehn/Desktop/GitHub && git --no-pager log -1 --pretty=format:"%H %s" -- PLANNER_TEMPLATE.md`. The most recent commit message must contain "v4.34" or "Rule 22 (e)". If not, stop and report to CEO. **Skip glossary read — QA verification of a markdown edit.** Read your specialist file at `bellows/agents/BELLOWS_QA.md` first. **Plan slug for evidence:** `executable-rule-22e-rule-20-tightening-2026-05-05`. **Evidence directory:** `bellows/knowledge/qa/evidence/executable-rule-22e-rule-20-tightening-2026-05-05/`. Create it: `import os; os.makedirs("bellows/knowledge/qa/evidence/executable-rule-22e-rule-20-tightening-2026-05-05", exist_ok=True)`. **FIRST — Deliverable Verification.** Three deliverables to verify. (1) Version bump: grep PLANNER_TEMPLATE.md for the version string. `grep -n "^\*\*Version:\*\* 4.34" /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md > bellows/knowledge/qa/evidence/executable-rule-22e-rule-20-tightening-2026-05-05/grep_version.txt 2>&1`. Result must be a single matching line. (2) Rule 22 (e) text: grep for the new banner-specific text. `grep -n "Rule 20 — QA Self-Check Results.*MUST be present" /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md > bellows/knowledge/qa/evidence/executable-rule-22e-rule-20-tightening-2026-05-05/grep_rule_22e.txt 2>&1`. Result must be a single matching line. Also verify the OLD text is gone: `grep -n "does the Rule 20 self-check output show PASSED, and are all required evidence files" /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md > bellows/knowledge/qa/evidence/executable-rule-22e-rule-20-tightening-2026-05-05/grep_old_text_absent.txt 2>&1`. Result must be empty (zero matches) — if the old text is still present, the edit failed and replaced nothing. (3) New Lessons row: grep for the unique new-row signature. `grep -n "Rule 20 self-check fabrication.*agent wrote the section header" /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md > bellows/knowledge/qa/evidence/executable-rule-22e-rule-20-tightening-2026-05-05/grep_lessons_row.txt 2>&1`. Result must be a single matching line. Build a verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |` with one row per deliverable, citing each evidence file by path. If ANY item is ❌, attempt to fix (re-run the failed edit). If unfixable, stop and report to CEO. **SECOND — Governance commit verification.** Confirm the v4.34 commit landed in the governance-root repo. `cd /Users/marklehn/Desktop/GitHub && git --no-pager log -1 --pretty=format:"%H %s%n%n%b" -- PLANNER_TEMPLATE.md > /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-rule-22e-rule-20-tightening-2026-05-05/git_log_governance.txt 2>&1`. Inspect the file: the commit subject must reference v4.34 or Rule 22 (e). Add a row to the verification table for the commit. **THIRD — Bellows commit verification.** Confirm the agent-prompt-feedback commit landed in the bellows repo. `cd /Users/marklehn/Desktop/GitHub/bellows && git --no-pager log -1 --pretty=format:"%H %s" -- knowledge/research/agent-prompt-feedback.md > knowledge/qa/evidence/executable-rule-22e-rule-20-tightening-2026-05-05/git_log_bellows.txt 2>&1`. The commit subject must reference prompt feedback. Add a row to the verification table. **FOURTH — No production code changes.** Targeted test scope justification claims this plan touches no production code. Confirm by checking the governance-root commit's file list. `cd /Users/marklehn/Desktop/GitHub && git --no-pager show --stat HEAD -- 'PLANNER_TEMPLATE.md' > bellows/knowledge/qa/evidence/executable-rule-22e-rule-20-tightening-2026-05-05/git_show_governance.txt 2>&1`. The file list must contain ONLY `PLANNER_TEMPLATE.md`. **FIFTH — Update PROJECT_STATUS.md.** Add a milestone entry to `bellows/PROJECT_STATUS.md`. Use Filesystem:edit_file with the verbatim anchor of the most recent existing milestone line in the Completed Milestones section. The new entry text: "2026-05-05 — PLANNER_TEMPLATE v4.34: Rule 22 (e) tightened to require literal Rule 20 banner string and PASSED line in QA reports. Pairs with Bellows-side `_gate_rule_20_self_check` (also shipped 2026-05-05) for two-layer detection of fabrication and omission." If the PROJECT_STATUS.md anchor is unclear, read the file first to identify the most recent milestone entry as your anchor — do NOT guess. **SIXTH — Deposit QA report to `bellows/knowledge/qa/rule-22e-rule-20-tightening-qa-report-2026-05-05.md`** using canonical Python file write pattern. The report structure: header, deliverable verification table, governance commit verification, bellows commit verification, no-production-code verification, Rule 20 self-check Python block (see below), Output Receipt. **SEVENTH — Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.** **EIGHTH — Final commit.** `cd /Users/marklehn/Desktop/GitHub/bellows && git add PROJECT_STATUS.md knowledge/qa/rule-22e-rule-20-tightening-qa-report-2026-05-05.md knowledge/qa/evidence/executable-rule-22e-rule-20-tightening-2026-05-05/ knowledge/research/agent-prompt-feedback.md && git --no-pager log -1 && git commit -m "qa: PLANNER_TEMPLATE v4.34 Rule 22 (e) tightening"`. **STOP.** Do NOT move this plan to Done/. Per the disable-auto-close model, the Planner performs the terminal move after Rule 22 verification passes.
>
> **Rule 20 — Mandatory QA Self-Check** (run AFTER all other steps, BEFORE the final commit):
>
> ```python
> # Rule 20 — Mandatory QA Self-Check
> import os, sys
> plan_slug = "executable-rule-22e-rule-20-tightening-2026-05-05"
> qa_report_path = f"bellows/knowledge/qa/rule-22e-rule-20-tightening-qa-report-2026-05-05.md"
> evidence_dir = f"bellows/knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = [
>     "grep_version.txt",
>     "grep_rule_22e.txt",
>     "grep_old_text_absent.txt",
>     "grep_lessons_row.txt",
>     "git_log_governance.txt",
>     "git_log_bellows.txt",
>     "git_show_governance.txt",
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
>         elif fname != "grep_old_text_absent.txt" and os.path.getsize(fpath) == 0:
>             # Note: grep_old_text_absent.txt is EXPECTED to be empty (proves old text is gone).
>             # All other evidence files must be non-empty.
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
> Execute the block, include its literal stdout in the QA report, and halt if it prints `FAILED`.
>
> **Deposits:**
> - `bellows/knowledge/qa/rule-22e-rule-20-tightening-qa-report-2026-05-05.md`
> - `bellows/PROJECT_STATUS.md`
> - `bellows/knowledge/qa/evidence/executable-rule-22e-rule-20-tightening-2026-05-05/grep_version.txt`
> - `bellows/knowledge/qa/evidence/executable-rule-22e-rule-20-tightening-2026-05-05/grep_rule_22e.txt`
> - `bellows/knowledge/qa/evidence/executable-rule-22e-rule-20-tightening-2026-05-05/grep_old_text_absent.txt`
> - `bellows/knowledge/qa/evidence/executable-rule-22e-rule-20-tightening-2026-05-05/grep_lessons_row.txt`
> - `bellows/knowledge/qa/evidence/executable-rule-22e-rule-20-tightening-2026-05-05/git_log_governance.txt`
> - `bellows/knowledge/qa/evidence/executable-rule-22e-rule-20-tightening-2026-05-05/git_log_bellows.txt`
> - `bellows/knowledge/qa/evidence/executable-rule-22e-rule-20-tightening-2026-05-05/git_show_governance.txt`
> - `bellows/knowledge/research/agent-prompt-feedback.md`
