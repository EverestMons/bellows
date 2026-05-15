**Project:** bellows | **Type:** executable | **Steps:** 2 | **pause_for_verdict:** after_step_1 | **auto_close:** false

# Hygiene Close — 2026-04-19 BACKLOG Entry: "Plan Fixing Bug X Tripped Bug X During Its Own Close"

## Context

The Bellows BACKLOG has one Open entry dated 2026-04-19 documenting the pattern that any Bellows-side fix-plan targeting a close-path bug will trip the bug during its own close (because the running daemon executes pre-fix code through the fix-plan's lifecycle). The entry itself flagged "May warrant promotion to a PLANNER_TEMPLATE Lessons Learned entry at next governance pass."

PLANNER_TEMPLATE v4.38 (shipped 2026-05-11, governance-root commit `4e54c02`) added a paragraph to the Restart Discipline subsection (line 882) and a Lessons Learned row (line 1227) that document this pattern — but the v4.38 coverage is **narrower** than the BACKLOG entry's general scope. v4.38 specifically covers fix-plans modifying the 5 named plan-text parsers (`_extract_step_text`, `_gate_is_qa_step`, `extract_total_steps`, `_extract_step_text_from_plan`, `strip_fenced_code_blocks`). The BACKLOG entry's original 2026-04-19 example (`executable-verdict-lifecycle-coupling-2026-04-19`) was a verdict-lifecycle fix — not a plan-text parser fix — so it falls in the general class the v4.38 paragraph doesn't explicitly name.

Closure framing (CEO decision: Option B, 2026-05-12): partial supersession. The parser-fix subset is now structurally documented in PLANNER_TEMPLATE v4.38; the general close-path pattern remains procedurally documented in the BACKLOG entry's own mitigation text (procedural mitigations a/b/c). Move the entry to Closed with a hygiene note that records both the v4.38 coverage and the explicit scope-narrowing.

No code changes. No daemon restart required.

## Execution Map

`Step 1 (DOC) → Step 2 (QA)`

---

## STEP 1 — Documentation Analyst: BACKLOG hygiene edit + dev log + commit

You are the Documentation Analyst for this plan. Your job is to move the 2026-04-19 Open BACKLOG entry to the Closed section with a hygiene-close note, write a brief dev log entry, and commit both changes.

**Read first (in this order):**
1. `bellows/agents/BELLOWS_DOCUMENTATION_ANALYST.md` — your role.
2. `bellows/knowledge/BACKLOG.md` — the file you will edit. Note the exact text of the 2026-04-19 Open entry (it is the second Open bullet, starts with `- 2026-04-19: plan fixing bug X tripped bug X during its own close`). Note also the structure and style of recent Closed entries (the 2026-05-11 hygiene closes are the nearest precedents).
3. `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` lines 876–882 (Restart Discipline subsection) and line 1227 (Lessons Learned row from 2026-05-11). These are the v4.38 references your hygiene-close note will cite.

**Do NOT read** `bellows.py`, `gates.py`, `verdict.py`, or any source code. This is a markdown-only hygiene close.

### Phase 1 — Remove the entry from Open

In `bellows/knowledge/BACKLOG.md`, locate the bullet that begins:

`- 2026-04-19: plan fixing bug X tripped bug X during its own close — documented pattern, not a discrete item to fix.`

This is the entire second bullet in the `## Open` section. Delete it (the entire bullet, from the leading `- ` through the final period of "next governance pass."). The blank line that separated it from the preceding entry should also be removed so the Open section remains cleanly formatted with one entry remaining.

After this edit, the `## Open` section should contain exactly one bullet (the 2026-05-05 bellows-self parallel/concurrent activity exposure entry).

### Phase 2 — Add the hygiene close to Closed

At the top of the `## Closed` section (immediately after the section header and its blank line, before the existing `**Closed 2026-05-12:**` Terminal output redesign entry), insert a new bullet using the format below. Keep the bullet on a single logical line (one bullet, prose that wraps naturally — no internal line breaks).

```
- **Closed 2026-05-12 (hygiene):** Plan-fixing-bug-X tripped bug X during own close (originally 2026-04-19). Partial supersession by PLANNER_TEMPLATE v4.38 (governance-root commit `4e54c02`, shipped 2026-05-11). The Restart Discipline subsection (line 882) and Lessons Learned row at line 1227 document the structural inevitability of QA-step gate trips on Bellows-side fix-plans that modify plan-text parsers — naming the 5 affected parsers (`_extract_step_text`, `_gate_is_qa_step`, `extract_total_steps`, `_extract_step_text_from_plan`, `strip_fenced_code_blocks`) and the correct CEO override pattern. **Scope note:** v4.38's structural documentation covers the parser-fix subset of the pattern, not the full general class. The original 2026-04-19 example (`executable-verdict-lifecycle-coupling-2026-04-19`) was a verdict-lifecycle fix, not a parser fix — that general class (any Bellows-side code change targeting a close-path bug) remains procedurally documented in the original BACKLOG entry's own mitigation text (code-level-only QA, accept manual cleanup as one-time cost, post-fix validation via separate dependent plan after restart). The original entry's "May warrant promotion to a PLANNER_TEMPLATE Lessons Learned entry at next governance pass" disposition is satisfied for the parser-fix subset; the general pattern continues to be procedurally documented in this BACKLOG's Closed section as historical reference. No code change. Reference: PLANNER_TEMPLATE.md v4.38 Restart Discipline subsection (line 882), Lessons Learned row 2026-05-11 (line 1227), governance-root commit `4e54c02`.
```

### Phase 3 — Dev log

Create the file `bellows/knowledge/development/backlog-2026-04-19-plan-fixing-bug-x-hygiene-close-2026-05-12.md` with the following content (replace `<commit-sha>` with the actual short SHA after Phase 4's commit lands; you'll update it as the final dev-log edit before committing):

```
# Dev Log — Hygiene Close of 2026-04-19 BACKLOG Entry: Plan Fixing Bug X Tripped Bug X

**Date:** 2026-05-12
**Plan:** executable-backlog-2026-04-19-plan-fixing-bug-x-hygiene-close-2026-05-12
**Commit:** <commit-sha>

## What changed

`bellows/knowledge/BACKLOG.md`:
- Removed the 2026-04-19 entry "plan fixing bug X tripped bug X during its own close" from the `## Open` section.
- Added a hygiene-close bullet at the top of the `## Closed` section recording the partial supersession by PLANNER_TEMPLATE v4.38 and the explicit scope-narrowing.

## Why

The 2026-04-19 entry's own text flagged "May warrant promotion to a PLANNER_TEMPLATE Lessons Learned entry at next governance pass." PLANNER_TEMPLATE v4.38 (2026-05-11, governance-root commit `4e54c02`) shipped a Restart Discipline paragraph and a Lessons row that document the parser-fix subset of this pattern. The general close-path pattern (broader than the parser subset) remains procedurally documented in the original entry's own mitigation text, so moving the entry to Closed with a scope-narrowing note preserves the historical reference while clearing the Open list.

## Scope

- No code changes.
- No tests added or modified.
- No daemon restart required.
- BACKLOG `## Open` count: 2 → 1.

## References

- PLANNER_TEMPLATE.md v4.38 Restart Discipline subsection, line 882
- PLANNER_TEMPLATE.md v4.38 Lessons Learned row, line 1227 (2026-05-11)
- Governance-root commit `4e54c02`
```

### Phase 4 — Commit

After both Phase 1+2 edits to `BACKLOG.md` and the Phase 3 dev log file are written:

1. From `/Users/marklehn/Desktop/GitHub/bellows/`, run:
   - `git add knowledge/BACKLOG.md knowledge/development/backlog-2026-04-19-plan-fixing-bug-x-hygiene-close-2026-05-12.md`
   - `git status` (verify only the two files are staged)
   - `git commit -m "chore(backlog): hygiene-close 2026-04-19 plan-fixing-bug-X entry (partial supersession by v4.38)"`
2. Capture the short SHA from the commit output.
3. Open the dev-log file and replace `<commit-sha>` with the captured short SHA.
4. Amend the commit: `git commit --amend --no-edit -a` (this folds the SHA fill-in into the same commit so the dev log accurately self-references).
5. Capture the new short SHA from the amend output.

### Output Receipt

In your final message for this step, report:
- Confirmation that the 2026-04-19 bullet is no longer present in `## Open` (Phase 1 verification: report the current count of Open bullets — should be 1).
- Confirmation that the new hygiene-close bullet is present at the top of `## Closed` (Phase 2 verification: paste the first 200 characters of the new bullet).
- The dev-log file path and final commit SHA.
- The exact phrase: `Step 1 complete — ready for QA verification.`

**Deposits:**
- `bellows/knowledge/BACKLOG.md`
- `bellows/knowledge/development/backlog-2026-04-19-plan-fixing-bug-x-hygiene-close-2026-05-12.md`

---

## STEP 2 — QA Analyst: verify edits + Rule 20 self-check

You are the QA Analyst for this plan. Your job is to verify the Step 1 DEV's BACKLOG hygiene close landed correctly, run the Rule 20 self-check, deposit the QA report, update PROJECT_STATUS.md, and append agent feedback.

**Read first (in this order):**
1. `bellows/agents/BELLOWS_QA.md` — your role.
2. `bellows/knowledge/BACKLOG.md` — the edited file.
3. The Step 1 DEV's output receipt (in conversation history).

### Phase 1 — Verify Step 1 deliverables (grep + git log)

Run the following verifications and capture stdout into evidence files:

1. **BACKLOG Open count = 1.**
   - Command: `awk '/^## Open$/,/^## Closed$/' bellows/knowledge/BACKLOG.md | grep -c '^- '`
   - Expected: `1`
   - Capture into: `bellows/knowledge/qa/evidence/backlog-2026-04-19-plan-fixing-bug-x-hygiene-close-2026-05-12/open-count.txt`

2. **2026-04-19 plan-fixing-bug-X bullet is GONE from `## Open`.**
   - Command: `awk '/^## Open$/,/^## Closed$/' bellows/knowledge/BACKLOG.md | grep -c 'plan fixing bug X tripped bug X'`
   - Expected: `0`
   - Capture into: `bellows/knowledge/qa/evidence/backlog-2026-04-19-plan-fixing-bug-x-hygiene-close-2026-05-12/open-no-match.txt`

3. **Hygiene-close bullet is PRESENT in `## Closed`.**
   - Command: `grep -c "Closed 2026-05-12 (hygiene):\*\* Plan-fixing-bug-X" bellows/knowledge/BACKLOG.md`
   - Expected: `1`
   - Capture into: `bellows/knowledge/qa/evidence/backlog-2026-04-19-plan-fixing-bug-x-hygiene-close-2026-05-12/closed-match.txt`

4. **Hygiene-close bullet cites v4.38 references.**
   - Command: `grep "Plan-fixing-bug-X" bellows/knowledge/BACKLOG.md | grep -c "v4.38"`
   - Expected: `1`
   - Capture into: `bellows/knowledge/qa/evidence/backlog-2026-04-19-plan-fixing-bug-x-hygiene-close-2026-05-12/v438-citation.txt`

5. **Commit landed in bellows.**
   - Command: `cd /Users/marklehn/Desktop/GitHub/bellows && git log -1 --oneline --grep="hygiene-close 2026-04-19"`
   - Expected: one line matching the commit message from Step 1 Phase 4.
   - Capture into: `bellows/knowledge/qa/evidence/backlog-2026-04-19-plan-fixing-bug-x-hygiene-close-2026-05-12/git-log.txt`

6. **Dev log file exists and references the same commit SHA the git log shows.**
   - Command: `cat bellows/knowledge/development/backlog-2026-04-19-plan-fixing-bug-x-hygiene-close-2026-05-12.md`
   - Capture stdout into: `bellows/knowledge/qa/evidence/backlog-2026-04-19-plan-fixing-bug-x-hygiene-close-2026-05-12/dev-log-content.txt`
   - Verify visually: the `<commit-sha>` placeholder was replaced with a real short SHA matching the SHA from check 5.

If ANY of these checks fails, halt and report. Do NOT proceed to deliverable verification or Rule 20 self-check.

### Phase 2 — Deliverable verification (Rule 17)

In the QA report, include a deliverable verification table with one row per declared deliverable from Step 1:

| Deliverable | Status |
|---|---|
| BACKLOG.md: 2026-04-19 bullet removed from Open | ✅ / ❌ |
| BACKLOG.md: hygiene-close bullet added to Closed | ✅ / ❌ |
| BACKLOG.md: hygiene-close cites v4.38 + commit `4e54c02` | ✅ / ❌ |
| Dev log file created with final commit SHA | ✅ / ❌ |
| Commit landed in bellows with expected message | ✅ / ❌ |

If any row is ❌ MISSING, halt and report. Do not deposit a passing QA report.

### Phase 3 — Rule 20 self-check

Run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at the governance root. Use these values when filling in the template:

- `plan_slug`: `executable-backlog-2026-04-19-plan-fixing-bug-x-hygiene-close-2026-05-12`
- `qa_report_path`: `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/backlog-2026-04-19-plan-fixing-bug-x-hygiene-close-qa-2026-05-12.md`
- `evidence_dir`: `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/backlog-2026-04-19-plan-fixing-bug-x-hygiene-close-2026-05-12/`
- `required_evidence_files`: `["open-count.txt", "open-no-match.txt", "closed-match.txt", "v438-citation.txt", "git-log.txt", "dev-log-content.txt"]`

Include the literal stdout output of the block in the QA report. If the block prints `FAILED`, do not proceed with closure — halt and report.

### Phase 4 — Deposit QA report

Write the QA report to: `bellows/knowledge/qa/backlog-2026-04-19-plan-fixing-bug-x-hygiene-close-qa-2026-05-12.md`

Required sections:
- **Plan slug** (top line)
- **Deliverable Verification** (table from Phase 2)
- **Phase 1 Evidence Summary** (one paragraph per check, citing the evidence file)
- **Rule 20 — QA Self-Check Results** (literal stdout from Phase 3)
- **Final Verdict** (PASS or FAIL)

### Phase 5 — Update PROJECT_STATUS.md

Append a new bullet at the top of the `## Completed` section in `bellows/PROJECT_STATUS.md` summarizing this plan. Format:

```
- 2026-05-12: **BACKLOG hygiene close — 2026-04-19 plan-fixing-bug-X entry moved to Closed (partial supersession by v4.38).** Hygiene-only close per CEO Option B 2026-05-12: PLANNER_TEMPLATE v4.38 (governance-root commit `4e54c02`, 2026-05-11) covers the parser-fix subset of the pattern via the Restart Discipline paragraph (line 882) and Lessons row (line 1227); the general close-path pattern remains procedurally documented in the original BACKLOG entry's mitigation text. No code changes. No daemon restart required. Open BACKLOG count: 2 → 1. **Commit:** `<commit-sha>` (BACKLOG + dev log together). Reference: `Done/executable-backlog-2026-04-19-plan-fixing-bug-x-hygiene-close-2026-05-12.md`, QA at `knowledge/qa/backlog-2026-04-19-plan-fixing-bug-x-hygiene-close-qa-2026-05-12.md`.
```

Also bump the file header `**Last Updated:** YYYY-MM-DD (...)` line to today's date and update the summary tally.

### Phase 6 — Feedback append + final commit

1. Append to `bellows/agent-prompt-feedback.md` a one-paragraph note on how this plan was to execute (any ambiguity in the BACKLOG anchor text, any friction with the dev-log self-reference loop, etc.). If you have no feedback, write a one-line "no friction observed" note rather than skipping the append.

2. Final commit (single commit, all QA artifacts together):
   - `cd /Users/marklehn/Desktop/GitHub/bellows`
   - `git add knowledge/qa/backlog-2026-04-19-plan-fixing-bug-x-hygiene-close-qa-2026-05-12.md knowledge/qa/evidence/backlog-2026-04-19-plan-fixing-bug-x-hygiene-close-2026-05-12/ PROJECT_STATUS.md agent-prompt-feedback.md`
   - `git status` (verify only QA artifacts + PROJECT_STATUS + feedback are staged)
   - `git commit -m "docs(qa): backlog 2026-04-19 plan-fixing-bug-X hygiene close QA + status update"`

3. **STOP.** Do NOT move this plan to Done/. Per the disable-auto-close model, the Planner performs the terminal move after Rule 22 verification passes.

### Output Receipt

In your final message for this step, report:
- The QA report path.
- The final verdict (PASS or FAIL).
- The Rule 20 self-check stdout line (the `Rule 20 — QA Self-Check Results` banner and the PASSED/FAILED line).
- The final commit SHA.
- The exact phrase: `Step 2 complete — ready for Planner Rule 22 verification.`

**Deposits:**
- `bellows/knowledge/qa/backlog-2026-04-19-plan-fixing-bug-x-hygiene-close-qa-2026-05-12.md`
- `bellows/knowledge/qa/evidence/backlog-2026-04-19-plan-fixing-bug-x-hygiene-close-2026-05-12/`
- `bellows/PROJECT_STATUS.md`
- `bellows/knowledge/research/agent-prompt-feedback.md`
