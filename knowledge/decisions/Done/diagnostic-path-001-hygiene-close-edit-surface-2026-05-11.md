**project:** bellows | **type:** diagnostic | **steps:** 1 | **pause_for_verdict:** always | **auto_close:** false

# Diagnostic — PATH-001 hygiene-close edit surface audit

## Why this exists

The 2026-05-11 staleness audit (`Done/diagnostic-path-001-rule-20-staleness-audit-2026-05-11.md`) classified BACKLOG entry `2026-04-19: PATH-001 recurrence in Rule 20 self-check` as STALE. The hygiene-close executable will touch two files: `bellows/knowledge/BACKLOG.md` and `bellows/knowledge/research/agent-prompt-feedback.md`.

The first file is well-characterized — the Planner has read it directly and knows exactly which bullet to remove and where to insert the closure entry. The second file is not. The staleness audit reported only that the PATH-001 section exists at "lines 399–412" and is "marked OPEN" — it did not capture the exact byte-level structure (section header format, status line format, whether `**Status:** OPEN` is a literal substring or some other format, what surrounds the section, what comes immediately before and after lines 399–412). The Planner is forbidden from reading `agent-prompt-feedback.md` directly under the standing "no source code, no config" constraint extended by precedent to specialist feedback files.

Without that byte-level structure, the executable would have to instruct the DEV to "read the file first and match whatever format you find," which is the same "figure it out at execution time" anti-pattern the diagnostic-before-executable rule exists to prevent. This diagnostic captures the exact edit surface so the executable can specify deterministic anchor strings.

## Step 1 — Documentation Analyst: capture the PATH-001 edit surface

You are the Bellows Documentation Analyst. Read `bellows/agents/BELLOWS_DOCUMENTATION_ANALYST.md` before starting; if the exact filename differs, use the closest match in `bellows/agents/`.

### Context

Two follow-up edits will be authored against `bellows/knowledge/research/agent-prompt-feedback.md`:
1. The PATH-001 section's status marker will be changed from its current OPEN state to a CLOSED state with date.
2. A new line will be appended immediately under the status marker referencing the 2026-05-10 migration commits.

This diagnostic captures the byte-level structure of the existing section so the next executable can specify exact `old_string` / `new_string` anchors for surgical `Desktop Commander:edit_block` calls. No edits are made in this step — read-only audit.

### Task

Answer the following questions about `bellows/knowledge/research/agent-prompt-feedback.md`. Cite exact line numbers and quote verbatim.

1. **Section header.** Read lines 395–415. Quote the exact PATH-001 section header verbatim (the heading line that starts the section — e.g., `## PATH-001: ...`). Report its exact line number. Report the line immediately above it (the preceding line, whatever it is) — quote verbatim with line number.

2. **Status marker format.** Inside the PATH-001 section, locate the line that indicates the OPEN status. Quote it verbatim with its exact line number. Report whether the marker is on its own line, embedded mid-sentence, formatted as a bold field (`**Status:** OPEN`), formatted as a different field name (e.g., `**State:**`, `**Open:**`), or some other format. Report what character immediately precedes and follows it (so the executable can build an unambiguous anchor).

3. **Line immediately after the status marker.** Quote verbatim the line that immediately follows the status marker line (line N+1). This is where the new closure line will be inserted. Report its exact line number.

4. **Other status-like markers in the file.** Run `grep -n -i "status" bellows/knowledge/research/agent-prompt-feedback.md` and `grep -n "OPEN" bellows/knowledge/research/agent-prompt-feedback.md`. Report every match. For each match, report whether it is the PATH-001 status line or some other line. This tells the executable whether `**Status:** OPEN` (or whatever the exact format is) appears multiple times in the file and therefore needs additional context for unambiguous matching.

5. **End of the PATH-001 section.** Identify the line that ends the PATH-001 section (the last line before the next section header or end-of-file). Quote it verbatim with its line number. This tells the executable how much of the section must be preserved.

6. **File total line count.** Report the total line count of `bellows/knowledge/research/agent-prompt-feedback.md`.

7. **Recommended anchor strings.** Based on questions 1–6, propose two exact `old_string` anchors for `Desktop Commander:edit_block` calls:
   - **Anchor A — Status change.** The exact multi-line string that uniquely identifies the status marker line plus enough surrounding context (typically 1 line above, 1 line below) to be unambiguous. Include the proposed `new_string` that changes only the status indicator.
   - **Anchor B — Closure line insertion.** The exact multi-line string that uniquely identifies the insertion point (the status line + the line immediately after it). Include the proposed `new_string` that inserts the new closure line between them.

   Specify both anchors as ready-to-use block edits. The executable will paste these verbatim.

### Out of scope

- Do NOT modify any file. Read-only audit.
- Do NOT propose changes to `bellows/knowledge/BACKLOG.md`. That file's edit surface is already known.
- Do NOT modify `RULE_20_SELF_CHECK_BLOCK.md`, `PLANNER_TEMPLATE.md`, or any plan file.

### Deliverables

A findings file at `bellows/knowledge/research/path-001-hygiene-close-edit-surface-2026-05-11.md` containing:
- One section per question (1–7) with the question restated, evidence quoted verbatim, and line numbers cited.
- A final "Anchor strings" section with the two ready-to-use `old_string` / `new_string` pairs from question 7.
- An Output Receipt at the bottom.

**Deposits:**
- `bellows/knowledge/research/path-001-hygiene-close-edit-surface-2026-05-11.md`
