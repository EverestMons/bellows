# Diagnostic — `_teardown_worktree` cherry-pick fragility audit

**Project:** bellows
**Specialist:** Bellows Systems Analyst
**auto_close:** false
**pause_for_verdict:** true
**Priority:** 1

## Purpose

Audit `_teardown_worktree`'s cherry-pick behavior to ground the fix design for BACKLOG `2026-05-07: _teardown_worktree cherry-pick fragility`. The BACKLOG entry hypothesizes the fix shape (cherry-pick `main..HEAD` range OR `git merge --ff-only`) but lacks ground truth on (a) which SHA the current code actually targets, (b) how often the disable-auto-close model produces ≥2 commits per worktree branch, and (c) how many recent plans silently stranded their non-cherry-picked commits. Failure 1 (stale `.git/index.lock`) is OUT OF SCOPE for this diagnostic — addressed separately.

## STEP 1 — `_teardown_worktree` audit + stranded-commit reproduction count

**Specialist:** Bellows Systems Analyst

**Deposits:**
- `bellows/knowledge/architecture/teardown-cherry-pick-audit-2026-05-10.md`

**Prompt:**

You are the Bellows Systems Analyst. Read your specialist file at `bellows/agents/BELLOWS_SYSTEMS_ANALYST.md` and follow its operating procedure.

This is a READ-ONLY investigation. Do NOT modify any code or commit anything. Produce a single findings file at `bellows/knowledge/architecture/teardown-cherry-pick-audit-2026-05-10.md` answering the questions below.

## Background

BACKLOG entry `2026-05-07: _teardown_worktree cherry-pick fragility` reports two failure modes from the same teardown event on `executable-billto-type-field-mapping-fix-2026-05-07`:
- **Failure 1 (out of scope here):** stale `.git/index.lock` caused 60s cherry-pick timeout
- **Failure 2 (in scope here):** the cherry-pick command was scoped to a single SHA (`2d39d0a6`), but the worktree branch had a chained second commit (`b618279e`) containing the QA report, evidence files, PROJECT_STATUS update, and agent-prompt-feedback append. The second commit was silently lost during teardown until manual recovery.

Under the disable-auto-close model (shipped 2026-04-24), agents commit DEV-step deliverables in one commit and QA-step deliverables in a second commit — multi-commit worktree branches are the norm, not the exception. The single-SHA cherry-pick pattern is structurally inadequate for that workflow.

## Questions

Answer each in the findings file. Cite specific file paths and line numbers from `bellows.py`. Quote relevant code snippets verbatim (≤15 lines per snippet).

### Q1. What does `_teardown_worktree` currently cherry-pick?

Read `bellows/bellows.py::_teardown_worktree`. Identify:

1. The exact argv passed to `git cherry-pick` (find the `subprocess` call; show the full command construction)
2. Which SHA is targeted — first commit on the worktree branch, last commit, HEAD, or something else? Show the code that computes the SHA.
3. Are there any pre-existing range-based or multi-SHA paths in the function (e.g., handling for the case where the branch has >1 commit)?

If the function does anything other than a single cherry-pick (e.g., conditional logic for commit counts), enumerate all branches.

### Q2. Commit-count distribution on recent worktree branches

The BACKLOG entry claims "the worktree's branch typically has 2+ commits at teardown" under disable-auto-close. Verify this empirically.

For invoice-pulse worktrees (the project with the highest plan throughput post-disable-auto-close):

1. Locate the worktree storage area for invoice-pulse. The standard git convention is `<project>/.git/worktrees/<branch-name>/`. List the directory and identify how many worktree branches exist.
2. For each plan dispatched 2026-04-24 (disable-auto-close ship date) through 2026-05-10 that used a worktree, count the number of commits on the worktree branch at teardown time. Use one of:
   - If worktree directories still exist and have HEAD/branch references: `git -C <invoice-pulse> log --oneline <branch-name>` for each
   - If worktrees were already cleaned up: `git -C <invoice-pulse> reflog --all | grep -i worktree` or check `git log --all --grep='cherry-pick'` for cherry-pick merge commits and trace back
   - Fallback: scan `bellows/knowledge/decisions/Done/` for plans dispatched in that window and check the invoice-pulse main-branch git log for the cherry-pick commits each one produced (commit count = number of cherry-picked SHAs per plan)
3. Produce a count distribution: how many plans had 1 commit, 2 commits, 3+ commits on their worktree branch at teardown?

If the data is sparse or the worktree branches are gone, state that explicitly and produce the best estimate possible from main-branch commit history (each plan typically leaves one or more cherry-picked commits with traceable patterns).

### Q3. Stranded-commit population audit

For invoice-pulse plans dispatched 2026-04-24 → 2026-05-10:

1. Enumerate every plan in `invoice-pulse/knowledge/decisions/Done/` dispatched in that window. Date is in the filename suffix (`-YYYY-MM-DD.md`).
2. For each plan, find the corresponding entry in `invoice-pulse/.git` history. Look for: (a) the commit(s) cherry-picked from the worktree (the agent's DEV commit), AND (b) whether the QA report / PROJECT_STATUS / agent-prompt-feedback updates landed on main.
3. Classify each plan as:
   - **(A) Single-commit plan** — only one commit on the worktree branch; cherry-pick was complete (this is fine)
   - **(B) Multi-commit plan, all commits cherry-picked** — somehow more than one commit landed on main (unlikely under single-SHA pattern, but check)
   - **(C) Multi-commit plan, only first/last commit cherry-picked** — the failure mode described in the BACKLOG entry. **This is the count we care about.**
   - **(D) Unknown / unable to determine** — worktree references gone, plan files reference no cherry-pick metadata

Report the count per class. The (C) count is the urgency signal for the fix.

### Q4. Fix-shape feasibility check

The BACKLOG entry proposes two fix candidates:

1. `git cherry-pick main..HEAD` from inside the worktree (range-pick)
2. `git merge --ff-only <wt-branch>` from main (fast-forward merge)

For each:

1. Does the current `_teardown_worktree` code structure accommodate the change with a minimal edit (1-line argv change)? If so, identify the exact line.
2. Are there any known edge cases that the SA flags as risks — e.g., what happens with (a) zero commits on the worktree branch (plan was a single-step diagnostic that did no commit work)? (b) cherry-pick conflicts mid-range? (c) main has diverged from the worktree's branch base since the worktree was created?
3. Which candidate does the SA recommend, and why? State the recommendation as either "(1) cherry-pick range" or "(2) ff-only merge" — do not propose hybrids unless one of the two is materially blocked.

### Q5. Layer impact

State the Layer Impact per your specialist output format:

- Which layers (1/2/3) are affected?
- Does the change shift any responsibility between layers? (Expected answer: no — this is purely Layer 1 mechanical fix. Confirm or contradict.)

## Output Receipt

Append the Output Receipt block from your specialist file. Status should be `Complete` if all 5 questions answered with evidence, `Partial` if Q2 or Q3 data is unavailable (explain why), `Blocked` only if you cannot read the source files.

After writing the findings file, STOP. Do not proceed to any other action. Wait for CEO verdict.

---

## Rule 20 Self-Check

```python
import os
files = [
    "bellows/knowledge/architecture/teardown-cherry-pick-audit-2026-05-10.md",
]
print("=" * 60)
print("Rule 20 Self-Check")
print("=" * 60)
all_present = True
for f in files:
    path = os.path.join("/Users/marklehn/Desktop/GitHub", f)
    exists = os.path.isfile(path)
    status = "✅" if exists else "❌"
    print(f"{status} {f}")
    if not exists:
        all_present = False
print("=" * 60)
print("SELF-CHECK PASSED" if all_present else "SELF-CHECK FAILED")
print("=" * 60)
```
