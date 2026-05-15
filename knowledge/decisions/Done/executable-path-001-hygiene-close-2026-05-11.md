**project:** bellows | **type:** executable | **steps:** 2 | **pause_for_verdict:** after_step_1 | **auto_close:** false

# Executable — Hygiene close: PATH-001 Rule 20 self-check

## Why this exists

The 2026-05-11 staleness audit (`Done/diagnostic-path-001-rule-20-staleness-audit-2026-05-11.md`) classified BACKLOG entry `2026-04-19: PATH-001 recurrence in Rule 20 self-check` as STALE. The 2026-05-10 single-source migration (governance commit `a109e47`, bellows commit `b05dc42`) structurally eliminated the failure mode by moving the canonical Rule 20 block to `/Users/marklehn/Desktop/GitHub/RULE_20_SELF_CHECK_BLOCK.md` with placeholder-enforced absolute paths and removing Planner-side block authoring. Population audit confirmed 17/17 post-migration QA reports show Rule 20 self-check PASSED with zero PATH-001 recurrences.

The 2026-05-11 edit-surface audit (`Done/diagnostic-path-001-hygiene-close-edit-surface-2026-05-11.md`) captured the exact byte-level structure of the `agent-prompt-feedback.md` PATH-001 section: header at line 399, status line at line 401 (`**Status:** OPEN. First identified pre-2026-05-04. Reinforced 4 times in 2026-05-04 session feedback (Backlog Capture DEV, Backlog Capture QA, Monorepo Fix QA, Canary DEV).`), blank line at 402, `**Pattern:**` line at 403. Six other `**Status:** OPEN` lines exist in the file, so anchors must include the section header for uniqueness.

This plan closes the BACKLOG entry as hygiene and updates the `agent-prompt-feedback.md` PATH-001 pattern entry from OPEN to CLOSED with cross-reference to the migration.

## Execution Map

Step 1 (Documentation Analyst) → Step 2 (Bellows QA)

## Step 1 — Documentation Analyst: BACKLOG close + pattern entry update

You are the Bellows Documentation Analyst. Read `bellows/agents/BELLOWS_DOCUMENTATION_ANALYST.md` before starting; if the exact filename differs, use the closest match in `bellows/agents/`.

### Context

Two files are edited in this step, then committed together. Both edits are specified as exact `Desktop Commander:edit_block` operations — do NOT freelance, do NOT modify the anchor strings, do NOT add additional changes outside these anchors.

### Edit 1 — Close the BACKLOG entry in `bellows/knowledge/BACKLOG.md`

**Edit 1a — Remove the open entry.** Use `Desktop Commander:edit_block` with:

`old_string`:
```

- 2026-04-19: PATH-001 recurrence in Rule 20 self-check — the CWD-relative path issue first documented in agent-prompt-feedback.md Patterns (PATH-001) has now recurred in executable-verdict-lifecycle-coupling-2026-04-19 QA. The self-check script prefixes paths with `bellows/` assuming execution from the parent directory, but agents often execute from inside the project directory. Pattern was identified but the PLANNER_TEMPLATE Rule 20 template was not updated to fix it. Candidate fix: change the Rule 20 block template to use either `os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))` as the first line (if the block is known to be run from an evidence-file path) or explicit absolute paths. Deferred to next governance pass.

---
```

`new_string`:
```

---
```

This removes the entire bullet (with its leading blank line) and leaves only the `---` separator that terminates the Open section.

**Edit 1b — Insert closure entry at top of Closed section.** Use `Desktop Commander:edit_block` with:

`old_string`:
```
## Closed

- **Closed 2026-05-11 (hygiene):** Bellows-side parser fix-plans trip own bug
```

`new_string`:
```
## Closed

- **Closed 2026-05-11 (hygiene):** PATH-001 recurrence in Rule 20 self-check (originally 2026-04-19). Stale entry — structurally fixed by the 2026-05-10 Rule 20 single-source migration (governance commit `a109e47`, bellows commit `b05dc42`). Diagnostic at `bellows/knowledge/research/path-001-rule-20-staleness-audit-2026-05-11.md` confirmed: (a) the current canonical block at `/Users/marklehn/Desktop/GitHub/RULE_20_SELF_CHECK_BLOCK.md` uses placeholder-enforced absolute paths (`<absolute-path-to-qa-report.md>`, `<absolute-path-to-evidence-dir>/`) with no `bellows/` prefix anywhere; (b) the Planner no longer authors the Rule 20 block in plans, eliminating the original failure surface; (c) population audit of 17 post-migration QA reports (2026-05-10 and 2026-05-11) showed Rule 20 self-check PASSED in 17/17 with zero path-resolution failures. The companion pattern entry in `agent-prompt-feedback.md` (PATH-001 at line ~399) was updated to CLOSED in the same plan. Reference: `Done/diagnostic-path-001-rule-20-staleness-audit-2026-05-11.md`, `Done/diagnostic-path-001-hygiene-close-edit-surface-2026-05-11.md`, `Done/executable-rule-20-single-source-2026-05-10.md`.

- **Closed 2026-05-11 (hygiene):** Bellows-side parser fix-plans trip own bug
```

Note the trailing line includes the start of the next existing entry — this guarantees the new entry inserts above it.

### Edit 2 — Update PATH-001 status in `bellows/knowledge/research/agent-prompt-feedback.md`

Apply these two `Desktop Commander:edit_block` operations in sequence.

**Edit 2a — Status change (OPEN → CLOSED 2026-05-11).** Use `Desktop Commander:edit_block` with:

`old_string`:
```
## PATH-001: Plan paths must use cwd-consistent prefix (or absolute paths)

**Status:** OPEN. First identified pre-2026-05-04. Reinforced 4 times in 2026-05-04 session feedback (Backlog Capture DEV, Backlog Capture QA, Monorepo Fix QA, Canary DEV).
```

`new_string`:
```
## PATH-001: Plan paths must use cwd-consistent prefix (or absolute paths)

**Status:** CLOSED 2026-05-11. First identified pre-2026-05-04. Reinforced 4 times in 2026-05-04 session feedback (Backlog Capture DEV, Backlog Capture QA, Monorepo Fix QA, Canary DEV).
```

**Edit 2b — Insert closure line.** Use `Desktop Commander:edit_block` with:

`old_string`:
```
**Status:** CLOSED 2026-05-11. First identified pre-2026-05-04. Reinforced 4 times in 2026-05-04 session feedback (Backlog Capture DEV, Backlog Capture QA, Monorepo Fix QA, Canary DEV).

**Pattern:** Plans use `bellows/knowledge/...` paths in agent instructions,
```

`new_string`:
```
**Status:** CLOSED 2026-05-11. First identified pre-2026-05-04. Reinforced 4 times in 2026-05-04 session feedback (Backlog Capture DEV, Backlog Capture QA, Monorepo Fix QA, Canary DEV).
**Closure:** Structurally fixed by the 2026-05-10 Rule 20 single-source migration (governance commit `a109e47`, bellows commit `b05dc42`). The canonical block at `/Users/marklehn/Desktop/GitHub/RULE_20_SELF_CHECK_BLOCK.md` uses placeholder-enforced absolute paths; Planner no longer authors the block inline. 17/17 post-migration QA reports passed Rule 20 self-check with zero path-resolution failures. Reference: `bellows/knowledge/research/path-001-rule-20-staleness-audit-2026-05-11.md`, BACKLOG.md 2026-05-11 closure.

**Pattern:** Plans use `bellows/knowledge/...` paths in agent instructions,
```

Apply Edit 2a first, then Edit 2b. Edit 2b depends on 2a's output (it anchors on `CLOSED 2026-05-11`).

### Commit

After all four edits land, stage and commit both files together. Use `Desktop Commander:start_process` with `timeout_ms: 5000`:

```
git add bellows/knowledge/BACKLOG.md bellows/knowledge/research/agent-prompt-feedback.md && git commit -m "docs(backlog): close PATH-001 as hygiene — structurally fixed by 2026-05-10 Rule 20 single-source migration"
```

Capture the commit SHA for the dev log.

### Out of scope

- Do NOT modify any other BACKLOG entries.
- Do NOT modify any other section of `agent-prompt-feedback.md`. Only the four anchor-based edits above.
- Do NOT modify `RULE_20_SELF_CHECK_BLOCK.md`, `PLANNER_TEMPLATE.md`, or any plan file.
- Do NOT push to remote. Local commit only.

### Deliverables

- `bellows/knowledge/BACKLOG.md` updated (open entry removed, closure entry added)
- `bellows/knowledge/research/agent-prompt-feedback.md` updated (PATH-001 status changed to CLOSED 2026-05-11, closure line inserted)
- Dev log at `bellows/knowledge/development/path-001-hygiene-close-dev-log-2026-05-11.md` capturing: files changed (with line ranges of edits), confirmation that all four `edit_block` operations succeeded on first try (no anchor-match failures), commit SHA, and an Output Receipt.

**Deposits:**
- `bellows/knowledge/development/path-001-hygiene-close-dev-log-2026-05-11.md`

## Step 2 — Bellows QA: Verify hygiene close

You are the Bellows QA specialist. Read `bellows/agents/BELLOWS_QA.md` before starting.

### Context

Step 1 closed BACKLOG entry `2026-04-19: PATH-001 recurrence in Rule 20 self-check` as hygiene and updated the corresponding pattern entry in `agent-prompt-feedback.md` from OPEN to CLOSED. Read the dev log at `bellows/knowledge/development/path-001-hygiene-close-dev-log-2026-05-11.md` to confirm what was done and capture the commit SHA.

### Task

Verify the hygiene close landed correctly. Markdown-only QA — no test suite, no PRAGMA.

1. **BACKLOG.md verification.**
   - 1a. Run `grep -n "2026-04-19: PATH-001" bellows/knowledge/BACKLOG.md`. Expect zero matches.
   - 1b. Run `grep -n "Closed 2026-05-11 (hygiene): PATH-001" bellows/knowledge/BACKLOG.md`. Expect exactly one match in the `## Closed` section.
   - 1c. Confirm the new closure entry references all three: `Done/diagnostic-path-001-rule-20-staleness-audit-2026-05-11.md`, `Done/diagnostic-path-001-hygiene-close-edit-surface-2026-05-11.md`, and `Done/executable-rule-20-single-source-2026-05-10.md`.
   - 1d. Run `git diff HEAD~1 -- bellows/knowledge/BACKLOG.md | head -100` and confirm the diff shows only: (a) removal of the original PATH-001 open bullet, (b) insertion of the new closure entry at the top of Closed. No other changes.

2. **agent-prompt-feedback.md verification.**
   - 2a. Run `grep -n "## PATH-001:" bellows/knowledge/research/agent-prompt-feedback.md`. Confirm exactly one match around line 399.
   - 2b. Run `grep -n "Status:.. CLOSED 2026-05-11" bellows/knowledge/research/agent-prompt-feedback.md` (using `..` to match the bold markdown around `Status:`). Confirm exactly one match.
   - 2c. Run `grep -n "Closure:.. Structurally fixed" bellows/knowledge/research/agent-prompt-feedback.md`. Confirm exactly one match immediately after the status line.
   - 2d. Confirm the original `**Pattern:**` paragraph and all following lines through line 411 (the `**Reference:**` line) are PRESERVED. Run `git diff HEAD~1 -- bellows/knowledge/research/agent-prompt-feedback.md` and confirm the diff shows only: (a) one-word change OPEN → CLOSED 2026-05-11 on the status line, (b) one new `**Closure:**` line inserted. No other changes.
   - 2e. Confirm the other 5 `**Status:** OPEN` lines elsewhere in the file (at lines 417, 433, 449, 465, 482 per the edit-surface audit) are UNCHANGED. Run `grep -n "Status:.. OPEN" bellows/knowledge/research/agent-prompt-feedback.md` and confirm exactly 5 matches (down from 6 before this plan).

3. **Commit verification.**
   - 3a. Run `git log -1 --stat` and confirm exactly two files changed: `bellows/knowledge/BACKLOG.md` and `bellows/knowledge/research/agent-prompt-feedback.md`.
   - 3b. Confirm the commit message starts with `docs(backlog): close PATH-001 as hygiene`.

4. **Rule 20 self-check.** Run the canonical Rule 20 self-check from `/Users/marklehn/Desktop/GitHub/RULE_20_SELF_CHECK_BLOCK.md`. Use these values:
   - `plan_slug`: `executable-path-001-hygiene-close-2026-05-11`
   - `qa_report_path`: `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/path-001-hygiene-close-qa-2026-05-11.md`
   - `evidence_dir`: `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-path-001-hygiene-close-2026-05-11/`
   - `required_evidence_files`:
     - `backlog_open_no_path_001.txt` — captured grep output from 1a (zero matches expected)
     - `backlog_closed_has_entry.txt` — captured grep output from 1b (one match expected)
     - `feedback_status_closed.txt` — captured grep output from 2b (one match expected)
     - `feedback_open_count.txt` — captured grep output from 2e (five matches expected)
     - `commit_log.txt` — captured `git log -1 --stat` output from 3a

Include the literal stdout of the self-check in the QA report. If it prints FAILED, halt and report.

### Deliverables

- QA report at `bellows/knowledge/qa/path-001-hygiene-close-qa-2026-05-11.md` containing:
  - Verification table with columns: `| File | Section # | Section Name | Present | Content Filled | Evidence |`
  - One row per verification subtask (1a–1d, 2a–2e, 3a–3b, 4)
  - Literal stdout of the Rule 20 self-check
  - Output Receipt
- Evidence directory at `bellows/knowledge/qa/evidence/executable-path-001-hygiene-close-2026-05-11/` containing the five files listed above.

**Deposits:**
- `bellows/knowledge/qa/path-001-hygiene-close-qa-2026-05-11.md`
- `bellows/knowledge/qa/evidence/executable-path-001-hygiene-close-2026-05-11/`
