---
type: executable
project: bellows
created: 2026-05-12
auto_close: false
pause_for_verdict: after_step_1
---

# Executable — Append Verdict-Format Failure Lessons Row to PLANNER_TEMPLATE.md

**Execution Map:** Step 1 (DOCUMENTATION_ANALYST) → Step 2 (DOCUMENTATION_ANALYST)

**Context:** The 2026-05-12 verdict-format silent-skip failure (Planner authored four continue-verdict files in a self-invented format that Bellows could not parse; Bellows silently skipped them; two plans stuck for ~2 hours) needs a Lessons entry at the governance root. The entry captures both the specific failure and the recurrence pattern (second contract-mismatch case in twelve days, after 2026-05-11 stale Rule 26 lesson edit). A companion architecture diagnostic shipping the same day at `bellows/knowledge/decisions/diagnostic-planner-authored-contract-validation-2026-05-12.md` enumerates and evaluates the broader design space. This plan lives in Bellows's watched directory but edits the governance-root `PLANNER_TEMPLATE.md` — split-commit pattern per v4.38.

---

## STEP 1 — DOCUMENTATION_ANALYST

Read your specialist file and the PLANNER_TEMPLATE.md Lessons Learned table format first (look at the last 3-5 rows in `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` under `## Lessons Learned` for current shape and length conventions). Append one new row at the END of the table (after the most recent dated entry — verify by reading the tail of the file). Use `Filesystem:edit_file` with an anchored edit that anchors on the last existing row's closing `|` plus newline, and inserts the new row immediately after. The new row content is the verdict-format Lessons entry drafted at `/Users/marklehn/Desktop/GitHub/_draft_verdict-format-lessons-and-architecture-2026-05-12.md`. Read that draft file to get the exact text — the row is in the "Lessons Entry" section as a single markdown table row beginning with `| 2026-05-12 |`. Copy the entire row verbatim including the leading and trailing `|`. Do NOT modify the entry text. Do NOT touch any other content in PLANNER_TEMPLATE.md. Do NOT bump the version number — this is a Lessons addition, not a rule change. After the edit, verify with `grep -c "^| 2026-05-12 | Verdict file format silent-skip" /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` — the count should be exactly 1. If grep returns 0 or 2+, stop and report. Commit at the governance root with message `docs(governance): Lessons entry for 2026-05-12 verdict-format silent-skip failure`. The working directory for the commit is `/Users/marklehn/Desktop/GitHub/`. Deposit a dev log at `bellows/knowledge/development/governance-lessons-2026-05-12-dev-log.md` covering: edit anchor used, grep-count verification result, commit hash, any deviations.

**Deposits:**
- `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md`
- `bellows/knowledge/development/governance-lessons-2026-05-12-dev-log.md`

---

## STEP 2 — DOCUMENTATION_ANALYST

Read your specialist file and the Rule 20 self-check canonical block at `/Users/marklehn/Desktop/GitHub/RULE_20_SELF_CHECK_BLOCK.md` first. **FIRST — Deliverable Verification.** Read Step 1's Output Receipt "Files Created or Modified" list. Verify: (1) `PLANNER_TEMPLATE.md` modified — run `git --no-pager log -1 --stat /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` and confirm the most recent commit touches the file with a small additive diff (one row added, no other changes), (2) the new row is present — `grep -c "^| 2026-05-12 | Verdict file format silent-skip" /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` returns 1, (3) the row content matches the draft — read both `/Users/marklehn/Desktop/GitHub/_draft_verdict-format-lessons-and-architecture-2026-05-12.md` and the new line in PLANNER_TEMPLATE.md and compare verbatim (no character drift), (4) the dev log exists at the expected path. Produce a verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |`. If any item is ❌, attempt to fix; if unfixable, stop and report. **Verbatim-content check.** This is the load-bearing verification — Lessons entry content must match the reviewed draft exactly. Compare character-for-character. Quote any divergence. **Rule 20 self-check** per the canonical block. Evidence files at `bellows/knowledge/qa/evidence/governance-lessons-2026-05-12-qa/`: deliverable-verification output, verbatim-content comparison output. **No PROJECT_STATUS update needed** — this is a governance-root edit, not a Bellows project change. Append to `bellows/feedback.log`: `2026-05-12 — governance Lessons entry for verdict-format silent-skip — appended to PLANNER_TEMPLATE.md`. Final commit message: `docs(bellows): QA + feedback for governance Lessons entry 2026-05-12`. This is a Bellows-repo commit (QA report + evidence + feedback log all under `bellows/`). **STOP.** Do NOT move this plan to Done/.

**Deposits:**
- `bellows/knowledge/qa/governance-lessons-2026-05-12-qa.md`
- `bellows/knowledge/qa/evidence/governance-lessons-2026-05-12-qa/`
- `bellows/feedback.log`
