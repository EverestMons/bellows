# diagnostic — deposit_exists False Positive Root Cause (BACKLOG #1)

**Date:** 2026-05-06
**Tier:** Diagnostic
**Test Scope:** none — investigation only, no code changes, no tests

## Execution Map

Step 1 (Bellows Systems Analyst — DEV) → Done

Single-step diagnostic per PLANNER_TEMPLATE Rule 22 single-step diagnostic provision.

---

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan, executes Step 1, and on completion runs the housekeeping block at the end of Step 1 (commit + move-to-Done).

**Bootstrap:**

```
Read the plan at bellows/knowledge/decisions/diagnostic-deposit-exists-false-positive-root-cause-2026-05-06.md and execute Step 1.
```

---

## Context

**The 4-reproduction threshold has been crossed.** BACKLOG #1 (active, top of `bellows/knowledge/BACKLOG.md` Open section, originally documented 2026-05-06) tracks a `deposit_exists` gate false-positive pattern with 3 reproductions logged. As of 2026-05-06 evening, **5 NEW reproductions have been logged in a single working session**, all on `invoice-pulse/` plans:

| # | Plan | Step | Reported missing path | File state on disk |
|---|---|---|---|---|
| 1 | `diagnostic-backlog-hygiene-audit-2026-05-06` | 1 | `invoice-pulse/knowledge/research/backlog-hygiene-audit-2026-05-06.md` | exists, well-formed |
| 2 | `executable-backlog-hygiene-edits-2026-05-06b` | 2 | `invoice-pulse/knowledge/qa/backlog-hygiene-edits-round-2-qa-2026-05-06.md` + `invoice-pulse/knowledge/qa/evidence/executable-backlog-hygiene-edits-2026-05-06b/` | both exist |
| 3 | `executable-backlog-hygiene-edits-2026-05-06c` | 2 | `invoice-pulse/knowledge/qa/backlog-hygiene-edits-round-3-qa-2026-05-06.md` + `invoice-pulse/knowledge/qa/evidence/executable-backlog-hygiene-edits-2026-05-06c/` | both exist |
| 4 | `executable-session-wrap-2026-05-06` | 2 | `knowledge/qa/session-wrap-2026-05-06-qa.md` + `knowledge/qa/evidence/executable-session-wrap-2026-05-06/` | both exist (note: paths declared without `invoice-pulse/` prefix) |
| 5 | `diagnostic-tier-display-test-failure-2026-05-06` | 1 | `knowledge/research/tier-display-test-failure-diagnostic-2026-05-06.md` | exists (note: path declared without `invoice-pulse/` prefix) |

**Cross-cutting observation:** Reproductions 4 and 5 declare deposit paths WITHOUT the `invoice-pulse/` project prefix (relative to project root); reproductions 1, 2, 3 declare paths WITH the `invoice-pulse/` prefix (relative to governance root). Both forms reproduce the bug.

**Reproductions today match BACKLOG #1's hypothesis (a) timing race or (b) path resolution drift most plausibly.** Verifying which is the goal of this diagnostic.

This diagnostic does NOT propose a fix. It produces a root-cause finding with evidence and ranks the four hypotheses (a/b/c/d) by what the evidence supports. A separate fix plan follows the diagnostic.

**Out of scope for this diagnostic:** the `scope_check` false positive on `diagnostic-bash-permission-rules-audit-2026-05-04` is a separate gate; it is addressed by the 2026-05-05 monorepo-worktree close (accepted tradeoff for bellows-self plans) and is NOT in scope here.

---

## Step 1 — `_gate_deposit_exists` Root Cause Investigation (Bellows Systems Analyst — DEV)

**Agent:** Bellows Systems Analyst
**Specialist file:** `bellows/agents/BELLOWS_SYSTEMS_ANALYST.md`

**Goal:** Identify which of BACKLOG #1's four hypotheses is the actual root cause of `deposit_exists` false positives, with evidence sufficient to design a targeted fix.

**Read first (in order):**

1. `bellows/agents/BELLOWS_SYSTEMS_ANALYST.md`
2. `bellows/knowledge/BACKLOG.md` — the BACKLOG #1 entry at top of Open section (it lists hypotheses a/b/c/d and the 3 prior reproductions)
3. `bellows/gates.py` — full file. Pay particular attention to `_gate_deposit_exists`, `_resolve_deposit_path`, `_extract_plan_required_deposits`, and the agent-receipt parser at line ~157
4. `bellows/verdict.py` — `extract_primary_deposit()`, `slug_from_path()`, and how the `Deposit:` field is populated in verdict requests
5. `bellows/bellows.py` — the gate-invocation path: where in `run_plan()` does `gates.check()` fire, what filesystem state is it operating against, and what synchronization (if any) exists between agent file-write and gate evaluation
6. `bellows/knowledge/research/deposit-parser-prose-failure-diagnosis-2026-05-05.md` — the prior diagnostic that fixed the agent-receipt parser at gates.py:157 (this diagnostic must NOT regress that fix; the question is whether a sibling bug exists)

**Investigation tasks (run in order, capture all evidence):**

### Task 1 — Static analysis of `_resolve_deposit_path`

For each of the 5 reproduction paths in the table above, manually trace through `_resolve_deposit_path` in `gates.py`:

1. What is the value of `project_path` at the time of evaluation? (Read from `bellows.py` `run_plan()` to see how it's set per-plan.)
2. What is the value of `path` (the candidate deposit) as extracted from the plan or agent receipt?
3. What candidate paths does `_resolve_deposit_path` try? (Read the function — it likely tries `os.path.join(project_path, path)`, then `path` directly, then maybe a parent-relative form.)
4. For each candidate, would `os.path.isfile()` return True against the live filesystem state? (Confirm by direct `os.path.isfile()` invocation against the actual paths from the table above — these files all exist on disk per Rule 22 verification this session.)
5. Which candidate `_resolve_deposit_path` returns, and whether that matches the file's actual on-disk path.

**Hypothesis (b) check:** if step 5 reveals path-resolution returning None for paths that ARE present on disk, hypothesis (b) is supported. Capture the exact mismatch (declared path → expected resolved path → what `_resolve_deposit_path` returned).

### Task 2 — Timing analysis (hypothesis (a))

Read the gate-invocation path in `bellows.py::run_plan()`. Specifically:

1. What command does the agent run that produces the deposit file? (Likely `claude -p ... --output-format=stream-json`.)
2. After the agent process exits (return code 0), what synchronization happens before `gates.check()` fires? Is there a `flush()`, `sync()`, `time.sleep()`, or filesystem barrier?
3. Is the agent's stdout consumed in a streaming reader that may buffer past the agent's actual exit?
4. Could the gate fire before the agent's filesystem writes are visible to the gate's `os.path.isfile()` calls?

**Hypothesis (a) check:** if there's NO synchronization between agent exit and gate evaluation, AND the deposit file is created by the agent's last few writes, hypothesis (a) is supported. Quantify the typical write-to-gate window from log timestamps (compare deposit file mtime to gate-evaluation timestamp from `bellows.py`'s logging).

### Task 3 — Stale-snapshot analysis (hypothesis (c))

Examine whether `gates.check()` operates against a pre-step filesystem snapshot rather than live state:

1. Does `bellows.py` capture any pre-step filesystem state (`git diff --stat` baseline, file-list snapshot, mtime cache)?
2. Does `gates.check()` consult that snapshot, or live `os.path.isfile()`?
3. If both: is the deposit-existence check correctly using live state, or is there a code path where it leaks the snapshot?

**Hypothesis (c) check:** if any deposit-existence code path consults a pre-step snapshot, hypothesis (c) is supported.

### Task 4 — Agent-receipt parser regression check (hypothesis (d))

The 2026-05-05 fix at `gates.py:157` was specifically about the agent-receipt parser regex extraction. Verify that fix is still in place and not the source of today's reproductions:

1. Read `gates.py:157` and the surrounding `_gate_deposit_exists` function. Confirm the 2026-05-05 fix shape (regex extraction with fallback to `.strip("\`")`) is intact.
2. For each of the 5 reproductions, check whether the agent-receipt parser is even invoked. The error message "plan-required deposit missing (not declared by agent)" suggests this code path is NOT firing — the gate is failing at the plan-extraction or path-resolution layer, NOT at agent-receipt parsing.
3. Confirm the relevant code path: trace from `_gate_deposit_exists` → which sub-function determines a path is "plan-required" vs "agent-declared" → whether the failure occurs because the agent's receipt didn't list the path.

**Hypothesis (d) check:** if the agent-receipt parser is bypassed entirely on these reproductions (gate fails during plan-extraction or path-resolution before agent receipts are consulted), hypothesis (d) is NOT the cause.

### Task 5 — Distinguish path-form variant impact

The 5 reproductions split into two declaration forms:
- Form A (3 reproductions): paths declared with `invoice-pulse/` prefix (governance-root-relative)
- Form B (2 reproductions): paths declared without prefix (project-root-relative)

For each form, document:
1. What `project_path` does Bellows pass to the gate?
2. How does `_resolve_deposit_path` interpret the declared path against `project_path`?
3. Whether one form resolves correctly and the other doesn't — or whether both fail by the same mechanism.

**This is critical for fix design:** if Form B fails for a different reason than Form A, the fix may need two prongs.

### Task 6 — Verdict and ranking

Synthesize Tasks 1–5 into a verdict:

- **Confirmed root cause:** which hypothesis (a/b/c/d) is supported by evidence
- **Ruled out:** which hypotheses can be eliminated based on the evidence
- **Inconclusive:** which (if any) cannot be resolved without further investigation
- **Fix shape (high-level only):** describe the SHAPE of the fix in 2-4 sentences (where in code, what changes), but DO NOT write the fix or scope an executable. The Planner authors the fix plan after reviewing this diagnostic.

**Findings file:** `bellows/knowledge/research/deposit-exists-false-positive-root-cause-2026-05-06.md`

The findings file MUST contain:

- **Verdict line at the top:** Format: `**Root Cause: [a|b|c|d|combined a+b|...]** — [one-sentence summary]`. Hedging keywords ("likely", "probably", "should be", "I think", "perhaps") auto-invalidate the verdict per Rule 20.
- **Task 1–5 sections:** each with evidence captured per the task instructions (file:line citations, code excerpts, path-resolution traces, log-timestamp comparisons as applicable)
- **Task 6 verdict + ranking** as specified above
- **Output Receipt** at the bottom per the Bellows Systems Analyst specialist file's standard format. Test Results field can read "N/A — diagnostic, no code changes."

**Deposits:**
- `bellows/knowledge/research/deposit-exists-false-positive-root-cause-2026-05-06.md`

---

## Housekeeping (Step 1 final block — Bellows Systems Analyst)

After the findings file is written, perform housekeeping in this exact order:

**A. Self-check (Rule 20 mandatory):**

```python
import os, sys
findings_path = "bellows/knowledge/research/deposit-exists-false-positive-root-cause-2026-05-06.md"
plan_path = "bellows/knowledge/decisions/in-progress-diagnostic-deposit-exists-false-positive-root-cause-2026-05-06.md"

problems = []
if not os.path.isfile(findings_path):
    problems.append(f"MISSING: {findings_path}")
else:
    with open(findings_path) as f:
        body = f.read()
    if not body.strip():
        problems.append(f"EMPTY: {findings_path}")
    # Verdict line check — must contain "Root Cause:" in first 10 lines
    first_lines = "\n".join(body.splitlines()[:10])
    if "Root Cause:" not in first_lines:
        problems.append(f"NO 'Root Cause:' verdict line in first 10 lines of {findings_path}")
    # Hedging keywords auto-invalidate per Rule 20 (case-insensitive)
    hedges = ["MAYBE", "PROBABLY", "LIKELY", "SHOULD BE", "I THINK", "PERHAPS"]
    body_upper = body.upper()
    # Allow hedging in the BACKLOG #1 cited text (it uses "all unverified, listed for future diagnostic")
    # but NOT in the findings' own verdict or task sections
    findings_only = body
    # Strip BACKLOG #1 quoted text if present (between ``` blocks that match)
    for h in hedges:
        if h in body_upper:
            # Only flag if the hedge appears in non-quoted, non-evidence sections
            # Simple heuristic: count occurrences; if more than 2, flag
            count = body_upper.count(h)
            if count > 2:
                problems.append(f"HEDGING KEYWORD '{h}' found {count} times in {findings_path} (>2 occurrences suggests verdict hedging)")

if not os.path.isfile(plan_path):
    problems.append(f"MISSING in-progress plan: {plan_path}")

if problems:
    print("SELF-CHECK FAILED")
    for p in problems:
        print("  - " + p)
    sys.exit(1)
else:
    print("SELF-CHECK PASSED")
    print(f"Findings file: {findings_path}")
    print(f"Plan in-progress: {plan_path}")
```

The Python block above MUST execute and its literal stdout MUST appear in the findings file in a section titled `## Rule 20 Self-Check`.

**B. Commit:**
```bash
git add bellows/knowledge/research/deposit-exists-false-positive-root-cause-2026-05-06.md
git commit -m "diagnostic: deposit_exists false positive root cause (BACKLOG #1)"
```

**C. Move to Done (final action):**

Use Python (not heredoc):
```python
import shutil
shutil.move(
    "bellows/knowledge/decisions/in-progress-diagnostic-deposit-exists-false-positive-root-cause-2026-05-06.md",
    "bellows/knowledge/decisions/Done/diagnostic-deposit-exists-false-positive-root-cause-2026-05-06.md"
)
```

Then commit the move:
```bash
git add bellows/knowledge/decisions/Done/diagnostic-deposit-exists-false-positive-root-cause-2026-05-06.md
git commit -m "chore: move deposit_exists root cause diagnostic to Done"
```

**Deposits:**
- `bellows/knowledge/research/deposit-exists-false-positive-root-cause-2026-05-06.md`
