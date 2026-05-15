# Diagnostic — Failure 3 Mode A Possible Reproduction (2026-05-05) Investigation

**Project:** bellows
**Plan Type:** Diagnostic
**Date:** 2026-05-06
**Total Steps:** 1

---

## Context

A possible Failure 3 Mode A reproduction was observed during the 2026-05-05 session that closed Mode A. The diagnostic plan `diagnostic-failure-3-mode-b-static-analysis-2026-05-05.md` was found in `bellows/knowledge/decisions/Done/` with a clean filename (no `verdict-pending-` prefix) at the time the Planner went to perform the Rule 25 terminal-step move — yet the verdict request was still in `bellows/verdicts/pending/` and no auto-close path was applicable (diagnostic plans default to NOT auto-close per the deposited findings).

This is a single-occurrence anomaly. The 2026-05-05 BACKLOG entry identified three candidate explanations and an investigation path. This diagnostic executes that path while artifacts are still fresh (~24 hours since the event).

### Three candidate explanations

- **(a)** Agent performed the Done/ move itself — Rule 8/23 violation, fresh Mode A reproduction
- **(b)** Bellows ran the verdict consumer twice and processed an unsignaled earlier verdict
- **(c)** Planner missed a verdict it had deposited earlier in the session

### Why now

Today is 2026-05-06; artifacts (logs, DB rows, git history) are still fresh. Waiting for a second reproduction means losing this evidence. A second reproduction without this baseline would be harder to root-cause, not easier.

### Scope boundary

This is a **read-only diagnostic**. No code changes. No plan edits. No verdict deposits. The output is a single findings file with a verdict on which candidate explanation (if any) the evidence supports.

---

## Step 1 — SA: Three-Source Evidence Audit and Verdict

**Agent:** Bellows Systems Analyst

**Deposits:**
- `bellows/knowledge/research/failure-3-mode-a-occurrence-investigation-2026-05-06.md`

### Read first

- `bellows/agents/BELLOWS_SYSTEMS_ANALYST.md` — your specialist file
- `bellows/PROJECT_STATUS.md` 2026-05-05 entries — context on what shipped that session

### Target plan and artifacts

The plan under investigation:

- **Plan filename (final state):** `diagnostic-failure-3-mode-b-static-analysis-2026-05-05.md`
- **Plan slug (Bellows-derived):** `failure-3-mode-b-static-analysis-2026-05-05`
- **Final location:** `bellows/knowledge/decisions/Done/diagnostic-failure-3-mode-b-static-analysis-2026-05-05.md`
- **Findings file produced:** `bellows/knowledge/research/failure-3-mode-b-static-analysis-findings-2026-05-05.md`

### Investigation protocol

Execute the three sub-investigations below in order. Each produces a verdict signal (HIT / MISS / INCONCLUSIVE) for one of the three candidate explanations. Record raw evidence (commit SHAs, timestamps, query results) in the findings file — do not paraphrase.

#### Sub-investigation 1: Git log evidence (tests candidate (a))

Question: Did the agent move the plan to Done/, or did the Planner?

Run from `/Users/marklehn/Desktop/GitHub/bellows/`:

```bash
git --no-pager log --all --follow --pretty=format:"%H %an %ai %s" -- 'knowledge/decisions/Done/diagnostic-failure-3-mode-b-static-analysis-2026-05-05.md'
```

Also run:

```bash
git --no-pager log --all --pretty=format:"%H %an %ai %s" --diff-filter=A -- 'knowledge/decisions/Done/diagnostic-failure-3-mode-b-static-analysis-2026-05-05.md'
git --no-pager log --all --pretty=format:"%H %an %ai %s" --diff-filter=R -- 'knowledge/decisions/Done/diagnostic-failure-3-mode-b-static-analysis-2026-05-05.md'
```

For each commit returned: capture the SHA, author, timestamp, commit message, and the file's path in that commit (was it added directly to Done/ or moved from elsewhere?). Use `git show --stat <SHA>` to see file path changes.

Verdict criteria:
- **HIT for (a)** if the move-to-Done commit author matches the bellows worktree pattern (typically a "Bellows agent" or generic agent commit signature based on the `claude -p` subprocess), AND the move happened before any verdict was deposited
- **MISS for (a)** if the move-to-Done commit was a Planner-direct edit (CEO author, manual commit message)
- **INCONCLUSIVE for (a)** if no git history exists for the file in Done/ (e.g., it was moved via filesystem operation without git commit)

#### Sub-investigation 2: Bellows DB ledger evidence (tests candidate (b))

Question: Did Bellows process a verdict for this plan more than once?

Query `bellows.db` from `/Users/marklehn/Desktop/GitHub/bellows/`:

```bash
sqlite3 bellows.db "SELECT id, plan_filename, plan_slug, step_number, status, started_at, finished_at FROM runs WHERE plan_slug LIKE '%failure-3-mode-b%' OR plan_filename LIKE '%failure-3-mode-b%' ORDER BY id;"
```

Also check schema first to confirm column names:

```bash
sqlite3 bellows.db ".schema runs"
```

For each row: capture id, plan_filename, plan_slug, step_number, status, timestamps. Note any rows with status indicating completion (likely `complete`, `done`, or similar — confirm from schema).

Verdict criteria:
- **HIT for (b)** if the runs table shows two or more rows for this plan_slug with completion-state status (excluding rows that are clearly different steps of the same dispatch — i.e., look for duplicate step_number entries)
- **MISS for (b)** if there is exactly one completion-state row, OR rows show a normal single-dispatch lifecycle
- **INCONCLUSIVE for (b)** if `bellows.db` has been rotated/wiped or rows are missing

Also grep the daemon log for verdict consumer activity on this slug:

```bash
grep -h "failure-3-mode-b" logs/*.log 2>/dev/null | head -50
grep -h "_consume_verdicts" logs/*.log 2>/dev/null | grep -i "failure-3-mode-b" | head -20
```

If multiple `_consume_verdicts` matches for this slug appear at different timestamps, that strengthens HIT for (b).

#### Sub-investigation 3: Verdict file evidence (tests candidate (c))

Question: Was there a verdict deposit earlier in the session that the Planner did not recall?

List all verdict files (current and archived) related to this slug:

```bash
find verdicts/ -type f \( -name '*failure-3-mode-b*' -o -name '*failure-3-mode-b-static-analysis*' \) 2>/dev/null | xargs -I{} ls -la {}
```

For each file found, capture: full path, mtime, size. Read the contents to determine verdict type and any timestamp markers inside the file.

Cross-reference timestamps:
- The plan landed in `Done/` at some point on 2026-05-05 — find that timestamp from sub-investigation 1's git log
- If a `processed-verdict-failure-3-mode-b-static-analysis-2026-05-05-step-*.md` file exists in `verdicts/resolved/` with mtime BEFORE the Done/ move time, that is evidence of an earlier verdict deposit

Verdict criteria:
- **HIT for (c)** if a processed/resolved verdict file exists with mtime before the Done/ move, AND the verdict file's content is a continue/stop verdict that would have triggered the Done/ transition
- **MISS for (c)** if no such verdict file exists, or the only verdict file has mtime AFTER the Done/ move (which would mean the Done/ move was not triggered by that verdict)
- **INCONCLUSIVE for (c)** if verdict files exist but timestamps are ambiguous or files are missing

### Output structure

Findings file at `bellows/knowledge/research/failure-3-mode-a-occurrence-investigation-2026-05-06.md` with these sections:

1. **Summary** — One paragraph stating the verdict (HIT for which candidate, or no clear hit)
2. **Sub-investigation 1: Git log** — Raw commit data, then verdict signal for (a)
3. **Sub-investigation 2: DB ledger** — Raw query results, then verdict signal for (b)
4. **Sub-investigation 3: Verdict files** — Raw file listing + content excerpts, then verdict signal for (c)
5. **Verdict** — One of:
   - **Confirmed (a) — agent moved plan to Done/** with citation to specific commit evidence
   - **Confirmed (b) — Bellows double-consumed a verdict** with citation to DB row or log evidence
   - **Confirmed (c) — earlier verdict deposit was missed by Planner** with citation to verdict file evidence
   - **Multiple HITs** — list each with evidence, propose which is most likely root cause
   - **No clear hit** — list which candidates are MISS vs INCONCLUSIVE, and what evidence (if any) would still need to be gathered
6. **Recommended next action** — Based on verdict:
   - If (a) confirmed → Failure 3 Mode A is not fully closed; recommend follow-up fix plan scope
   - If (b) confirmed → Bellows verdict consumer has a re-entrancy bug; recommend follow-up diagnostic on `_consume_verdicts`
   - If (c) confirmed → Planner-side discipline issue, not a Bellows bug; recommend BACKLOG closure with note
   - If no clear hit → BACKLOG entry stays open as tripwire; document specific evidence-gathering steps for next recurrence

### Constraints

- This is a read-only diagnostic. Do not modify any files outside the deposit path. Do not move plan files. Do not deposit verdicts.
- Do not infer or speculate beyond what the three artifact sources directly support. If evidence is missing, say INCONCLUSIVE — do not guess.
- Cite raw evidence (commit SHAs, query result rows, file paths with mtimes) inline in the findings file. The Planner needs to verify your claims via Rule 22 by reading the same artifacts.
- Single-step plan: complete all three sub-investigations and the verdict in this step. Do not pause for verdict mid-step.

### Rule 20 self-check

After writing the findings file, run this self-check Python block. The Planner relies on this to verify completion:

```python
import os

deposit_path = "/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/failure-3-mode-a-occurrence-investigation-2026-05-06.md"

print("=" * 60)
print("Rule 20 Self-Check")
print("=" * 60)

checks = []
checks.append(("Findings file exists", os.path.isfile(deposit_path)))

if os.path.isfile(deposit_path):
    with open(deposit_path) as f:
        content = f.read()
    checks.append(("Has Summary section", "## Summary" in content or "# Summary" in content))
    checks.append(("Has Sub-investigation 1", "Sub-investigation 1" in content))
    checks.append(("Has Sub-investigation 2", "Sub-investigation 2" in content))
    checks.append(("Has Sub-investigation 3", "Sub-investigation 3" in content))
    checks.append(("Has Verdict section", "## Verdict" in content or "# Verdict" in content))
    checks.append(("Has Recommended next action", "Recommended next action" in content or "## Next action" in content or "## Recommendation" in content))
    checks.append(("File is non-trivial (>2KB)", len(content) > 2000))

for label, result in checks:
    glyph = "✅" if result else "❌"
    print(f"{glyph} {label}")

all_pass = all(result for _, result in checks)
print()
print("SELF-CHECK PASSED" if all_pass else "SELF-CHECK FAILED")
```

### Output Receipt

End your response with the standard SA output receipt block (per `BELLOWS_SYSTEMS_ANALYST.md`). The "Status" should be `Complete`. The "Files Deposited" should list the findings file path. "Flags for CEO" should briefly state the verdict (HIT for which candidate, or no clear hit).

---

## Plan Lifecycle

This is a single-step diagnostic. Per Rule 22, after Step 1 completes:

1. The Planner reads the deposited findings file directly
2. The Planner verifies the verdict against cited evidence
3. The Planner authors a `verdict: continue` deposit (if findings are clean) or a follow-up diagnostic (if findings are inconclusive in a way that warrants more investigation)
4. The Planner moves this plan file to `Done/` per Rule 25 terminal-step resolution

No auto-close. No QA step (this is a diagnostic; the findings ARE the deliverable).
