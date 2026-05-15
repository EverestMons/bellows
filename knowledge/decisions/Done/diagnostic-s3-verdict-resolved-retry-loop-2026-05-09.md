# Diagnostic — S3 Verdict-Resolved Retry Loop

**Created:** 2026-05-09
**Author:** Planner
**Project:** bellows
**Type:** diagnostic
**auto_close:** false
**Total Steps:** 1

---

## Context

Bellows's `_consume_verdicts()` runs every ~30 seconds and is supposed to: read each non-`processed-` file in `bellows/verdicts/resolved/`, parse the verdict, dispatch the next step (or move the plan to `Done/` / `halted-`), clean up the corresponding `verdict-request-*` file in `pending/`, and rename the resolved verdict file to `processed-*` so it does not re-fire.

**Observed symptom (S3):** The 30-second rescan repeatedly logs that it cannot find the corresponding `verdict-pending-*` plan in `knowledge/decisions/` and never escalates the resolved file out of `resolved/`. Confirmed twice on 2026-05-08 in a single session and called out as a known reliability issue ("S3 — Verdict-resolved retry loop"). The CEO's only known mitigation is manual `mv` of the offending files into `pending/archived/`.

**Current evidence on disk** (snapshot from `bellows/verdicts/resolved/`):

- 17 stranded `verdict-{slug}-step-{N}.md` files (no `processed-` prefix), all dated 2026-04-30 or 2026-05-01.
- 2 misplaced `verdict-request-{slug}-step-{N}.md` files (request-shaped, not response-shaped) — `billto-extraction-architecture-2026-05-07-step-1` and `pipe-header-parser-and-comprehensive-qa-2026-05-08-step-2`.
- 1 manually-recovered `_PLANNER_RECALLED_*` file (out of scope — manual artifact).
- 168 correctly-processed `processed-verdict-*` files (the happy path works most of the time).

The 17 stranded files all date from a single 2-day window 8-9 days ago. Since then several Bellows changes shipped: worktree implementation (2026-05-03), monorepo scope fix (2026-05-04), type-contract fix in `verdict.py` (2026-05-04/05), Rule 25 verdict format fix (2026-05-01), BACKLOG #1 closure (2026-05-05). The bug may already be partially or wholly fixed in current code; that is one of the questions this diagnostic must answer.

## Goal

Produce findings sufficient for the Planner to either (a) write a fix executable, (b) close S3 as already-fixed and queue cleanup, or (c) split S3 into multiple distinct bugs. Specifically answer:

1. **Live reproduction.** Does the S3 retry loop still reproduce on current `main` HEAD? Construct a minimal test scenario and observe what `_consume_verdicts()` does when a resolved verdict file matches no `verdict-pending-*` plan in any watched project's `knowledge/decisions/` (the plan is already in `Done/`).
2. **Root cause.** Trace the exact code path in `_consume_verdicts()` (and any helpers it calls) that decides whether to rename a resolved file to `processed-*`. Identify every condition that blocks the rename. Cite file:line for each branch.
3. **Stranded-file pattern.** Examine the 17 stranded `verdict-{slug}-step-{N}.md` files for a common cause. Group by slug, project, step number, and presence/absence of a corresponding `verdict-pending-*` plan in any watched location (`knowledge/decisions/`, `Done/`, `halted-`). Determine whether all 17 share the same failure mode or whether multiple distinct causes are present.
4. **Anomaly: request-shaped files in `resolved/`.** The two `verdict-request-{slug}-step-{N}.md` files in `resolved/` are not response files — they have the `verdict-request-` prefix, which is the schema for files in `pending/`. Determine whether (a) Bellows misfiled them, (b) the Planner deposited them with the wrong filename, or (c) some other explanation. Cite evidence.

## Step 1 — Bellows Systems Analyst investigation

You are the Bellows Systems Analyst. Investigate the S3 verdict-resolved retry loop and deposit findings. Do NOT modify any production file under `bellows/` or any watched project. This is investigation only.

**Read first (required):**

- `bellows/agents/BELLOWS_SYSTEMS_ANALYST.md` — your role
- `bellows/PROJECT_BRIEF.md` — project orientation
- `bellows/knowledge/research/agent-prompt-feedback.md` — recent prompt feedback (last ~30 entries)
- `bellows/knowledge/BACKLOG.md` — find existing BACKLOG entries that mention S3 or verdict-resolved retry; note their entry numbers and current status

**Scope of code reading:** `bellows/bellows.py` (especially `_consume_verdicts` and any helpers it calls), `bellows/verdict.py`, `bellows/gates.py` only as needed to understand verdict file shape. You may read `bellows/knowledge/research/verdict-file-schema-2026-04-18.md` and `bellows/verdicts/README.md` for the file-format contract.

**Scope of filesystem reading:** `bellows/verdicts/resolved/`, `bellows/verdicts/pending/`, `bellows/verdicts/pending/archived/` if it exists. For checking whether a corresponding plan file exists, you may `ls` (or equivalent Glob) inside any watched project's `knowledge/decisions/` and `knowledge/decisions/Done/` — but DO NOT read plan file contents; you only need filename existence.

**Investigation tasks:**

**Task A — Live reproduction.**
Construct a controlled reproduction in a scratch directory under `/tmp/` (NOT inside `bellows/verdicts/`). Create a fake `resolved/verdict-fake-plan-step-1.md` file with valid `verdict: continue` content, ensure no `verdict-pending-fake-plan-*.md` exists in any watched `knowledge/decisions/`, then either (1) read the relevant code carefully enough to predict what `_consume_verdicts()` would do on the next scan, or (2) write a minimal Python harness that imports and calls `_consume_verdicts()` against the scratch directory (preferred if feasible without side effects). Report whether the resolved file gets renamed to `processed-`, gets archived elsewhere, or is left in place. If left in place, quote the exact log line(s) Bellows would emit on each scan iteration.

**Task B — Code path trace.**
In `bellows.py`, locate `_consume_verdicts()` and produce a control-flow trace covering: (1) the file-listing step that selects which files in `resolved/` are candidates for processing (including any prefix filtering), (2) the lookup step that finds the corresponding `verdict-pending-*` plan, (3) the rename-to-`processed-` step, (4) every `continue`/`return`/early-exit that can skip the rename. For each branch that skips the rename, quote the exact line and explain the condition. Report file:line for each citation.

**Task C — Stranded-file census.**
List all files in `bellows/verdicts/resolved/` whose name matches `verdict-{slug}-step-{N}.md` (i.e., NOT `processed-` prefixed). For each, parse the slug and step number from the filename and:
- Search every watched project's `knowledge/decisions/` AND `knowledge/decisions/Done/` AND any `halted-*` files for a plan filename matching the slug.
- Record: slug, step, file mtime, plan location (`Done/`, `decisions/`, `halted-`, or "not found"), and whether a corresponding `verdict-request-{slug}-step-{N}.md` still exists in `bellows/verdicts/pending/`.
- Group results by failure pattern (e.g., "plan in Done/, request still in pending/" vs. "plan not found anywhere" vs. other).

Produce a Markdown table in the findings with one row per stranded file. Do NOT exceed 50 rows; if fewer than 50 stranded files exist, table all of them.

**Task D — Request-shaped file anomaly.**
For the two files matching `verdict-request-{slug}-step-{N}.md` shape currently in `bellows/verdicts/resolved/`:
- Read each file's first 30 lines.
- Determine whether the content is request-shaped (contains `**Plan:**`, `**Step:**`, `**Pause Reason Code:**` fields) or response-shaped (starts with `verdict: continue` or `verdict: stop`).
- Check whether a corresponding `verdict-{slug}-step-{N}.md` (response-shaped) also exists in `resolved/` for the same slug+step.
- Hypothesize how the file got there: Bellows misfiled it, Planner deposited with wrong filename, or other.

**Task E — Synthesis.**
Combining Tasks A–D, answer:
1. Does the bug reproduce on current `main`? (yes/no/partial — explain)
2. What is the single-sentence root cause, OR if multiple distinct bugs are conflated under "S3", enumerate each.
3. For the 17 stranded files, are they recoverable via verdict deposit + Bellows scan, or do they require physical CEO `rm`?
4. Recommended fix shape (one paragraph). Constraints: stay within Bellows's mechanical-only Layer 1 invariant; do not propose anything that requires Layer 3 judgment to be encoded in Bellows.

**Deposit findings to:** `bellows/knowledge/research/s3-verdict-resolved-retry-loop-findings-2026-05-09.md`

Required structure:
- `## Summary` — 3–5 sentence high-level answer to the four Goal questions
- `## Task A — Live Reproduction` — what you tried, what happened, log lines if any
- `## Task B — Code Path Trace` — control-flow walkthrough with file:line citations
- `## Task C — Stranded-File Census` — Markdown table + grouping
- `## Task D — Request-Shaped File Anomaly` — per-file analysis
- `## Task E — Synthesis` — the four numbered questions answered explicitly
- `## Recommended Next Action` — fix-executable / close-as-fixed / split-into-multiple-bugs, with rationale

**Output Receipt requirements:**
- Status: Complete / Partial / Blocked
- Deposit path verified to exist via `os.path.isfile()`
- CEO Flags: list any surprises, scope changes, or ambiguities the CEO should review before authorizing a fix plan
- Files modified: only the deposit file. Any other modification triggers scope_check failure.

**After depositing findings, append a feedback entry** to `bellows/knowledge/research/agent-prompt-feedback.md` covering: clarity of investigation tasks, whether any task was unsolvable as written, whether scope was right-sized.

**Deposits:**
- `bellows/knowledge/research/s3-verdict-resolved-retry-loop-findings-2026-05-09.md`
- `bellows/knowledge/research/agent-prompt-feedback.md`

---

## Bootstrap prompt for CEO

```
RUN DIAG bellows
```
