# Findings — Teardown Push Silent-Failure Disposition

**Diagnostic:** diagnostic-teardown-push-silent-failure-2026-05-26
**Date:** 2026-05-26
**Agent:** Bellows Systems Analyst
**Step:** 1
**Scope:** Ship-or-retire disposition for BACKLOG entry "Teardown push silently fails on long-running plans without surface signal" (2026-05-24).

---

## Item 1 — Fresh Grep: Zero Push Calls Confirmed

**Command:** `grep` for `git push`, `git_push`, `.push(` across all `*.py` in the bellows source tree.

**Result:** Zero `git push` calls. All `.push(` matches are `notifier.push()` — Pushover notification calls, not git operations:

| File:Line | Match | Classification |
|-----------|-------|----------------|
| `verdict.py:271` | `notifier.push(` | Pushover notification |
| `bellows.py:394` | `notifier.push(` | Pushover notification |
| `bellows.py:1146` | `notifier.push(` | Pushover notification |
| `tests/test_notifier_server.py:16,25,33,49` | `notifier.push(` | Test for Pushover |

**Disposition:** The 2026-05-21 finding (CVB-1: "Bellows codebase contains zero `git push` calls") is **CONFIRMED FRESH** as of 2026-05-26. No push call has been added since the original diagnostic.

### Verification Block 1
- **Claim:** Bellows source tree contains zero `git push` subprocess calls.
- **Command:** `grep` for `git push|git_push|\.push(` across `*.py` (excluding tests/worktrees).
- **Expected:** Zero git-push matches (per 2026-05-21 CVB-1).
- **Actual:** Zero git-push matches. All `.push(` hits are `notifier.push()`.
- **Materiality:** The entire disposition pivots on this. Confirmed: teardown cannot possibly be pushing.

---

## Item 2 — `_teardown_worktree` Step-by-Step Behavior

Source: `bellows.py:798-912`.

### Function signature
```python
def _teardown_worktree(project_path: str, wt_path: str, slug: str) -> None:
```

### Step-by-step enumeration

| Step | Lines | Operation | Git Subcommand | Direction |
|------|-------|-----------|----------------|-----------|
| (a) | 808-822 | Detect main branch name | `git symbolic-ref --short refs/remotes/origin/HEAD` | **read-only** (reads local remote-tracking ref) |
| (b) | 825-832 | Collect worktree commits | `git log --format=%H HEAD --not <main>` (cwd=wt_path) | **read-only** |
| lock | 834-852 | Detect/remove stale `.git/index.lock` | (filesystem only) | **local cleanup** |
| (c) | 855-869 | Cherry-pick each commit onto main | `git cherry-pick <sha>` (cwd=project_path) | **local write** |
| (c-err) | 863-868 | Abort on conflict | `git cherry-pick --abort` (cwd=project_path) | **local write** |
| (d) | 872-894 | Copy uncommitted dirty files back | `git status --porcelain` + `shutil.copy2` | **read-only + local file copy** |
| (e) | 897-912 | Remove worktree | `git worktree remove <wt_path> --force` + fallback `shutil.rmtree` | **local cleanup** |

### Specific answers

- **Does it push?** NO. Zero push calls anywhere in the function. Cross-confirmed by Item 1 grep.
- **Does it cherry-pick?** YES. Onto the local main checkout (`cwd=project_path`) at step (c).
- **Does it interact with origin?** NO. Step (a) reads `refs/remotes/origin/HEAD` — this is a local ref, not a network call. No `git fetch`, no `git push`, no network interaction of any kind.
- **Does it produce signal on push success/failure?** N/A — there is no push to succeed or fail. The function produces signal only on cherry-pick conflict (`WorktreeTeardownError` raised at line 867-868) and worktree removal failure (WARN log at lines 903, 905).

### Verification Block 2
- **Claim:** `_teardown_worktree` contains zero origin interactions.
- **Source:** Direct read of `bellows.py:798-912`.
- **Expected:** Enumeration of subprocess calls with no push/fetch/pull.
- **Actual:** 5 git subprocess calls (symbolic-ref, log, cherry-pick, cherry-pick --abort, worktree remove) — all local. Zero network operations.
- **Materiality:** Independently confirms teardown does not push, regardless of grep results.

---

## Item 3 — Reconciliation with 2026-05-24 Observation

The BACKLOG entry cites 50 commits accumulating on local main beyond origin/main during the `executable-remove-pre-scan-processed-rename-v2-2026-05-24` P0 loop.

**Given Item 2's finding (teardown does NOT push):**

The 50-commit local-only accumulation is fully explained by:
1. **Teardown cherry-picks commits onto local main** — this is its designed behavior (step (c) above).
2. **No mechanism pushes those cherry-picked commits to origin** — also by design. Bellows contains zero push calls.
3. **The P0 loop iterated ~25 times** — each iteration produced agent commits that teardown cherry-picked onto local main, accumulating ~50 commits (25 iterations × ~2 commits each).
4. **Pre-v4.47, agents pushed directly to origin** from plan prose instructions. Post-v4.47, agents are prohibited from pushing. Neither path involves Bellows-the-daemon pushing.

The BACKLOG entry's framing — "teardown push silently fails" — is **wrong**. There was no silent failure because there was no push. The entry's "documented design" ("worktree teardown pushes agent commits direct to origin") was the Planner's mental model at the time of authoring, not the actual code. The actual design has always been: teardown cherry-picks onto local main; something else pushes to origin.

---

## Item 4 — Current Operational Reality

Post-v4.47, with agents prohibited from pushing:

**How commits reach origin today:**
- **Planner-side session-wrap push.** The Planner runs `git push origin main` at session-wrap. This is documented in PLANNER_TEMPLATE Rule 23 housekeeping. Evidence: the 2026-05-21 teardown-git-operations timeline shows CEO manual push at session-wrap (00:53:27, commit `aa3fc6f`).

**Scenarios where session-wrap push doesn't happen:**
- **Long session without checkpoints:** commits accumulate on local main until session-wrap. This is the normal case and is not a gap — commits are safe on local, and the push happens at session end.
- **Daemon crash mid-plan:** cherry-picked commits survive on local main (they're git commits). Next session-wrap push delivers them.
- **Machine failure:** local commits could be lost if not yet pushed. This is a standard git risk, not a teardown-specific gap.

**Is there an operational gap?** No. The session-wrap push is the documented and functioning path. The 2026-05-24 50-commit accumulation was caused by the P0 loop (already Closed in BACKLOG), not by push absence. The Planner's operational mitigation (`git log --oneline origin/main..HEAD | wc -l` at session checkpoints) detects drift, but the drift itself is expected behavior — commits accumulate locally between session-wrap pushes.

### Verification Block 3
- **Claim:** Session-wrap push is the operational path for commits reaching origin.
- **Source:** 2026-05-21 teardown-git-operations timeline (CEO push at 00:53:27); v4.47 agent push prohibition (commit `7641ac9`, 2026-05-21); 34-plan post-v4.47 audit showing zero parallel-SHA reproductions.
- **Expected:** Single documented push path (Planner/CEO session-wrap).
- **Actual:** Confirmed. No other push mechanism exists in Bellows. Agents prohibited from pushing post-v4.47.
- **Materiality:** Confirms absence of teardown push creates no operational gap.

---

## Item 5 — Disposition Recommendation

### **RETIRE**

Teardown is NOT supposed to push. The evidence is unambiguous:

1. **Item 1:** Fresh grep confirms zero `git push` calls across all bellows Python modules — unchanged since the 2026-05-21 diagnostic.
2. **Item 2:** `_teardown_worktree` performs exactly 5 git subprocess operations, all local (symbolic-ref, log, cherry-pick, cherry-pick --abort, worktree remove). Zero network interactions. Zero origin interactions beyond reading a local remote-tracking ref.
3. **Item 3:** The 2026-05-24 50-commit accumulation is fully explained by teardown cherry-picking onto local main (correct behavior) during 25 P0 loop iterations (the loop is the cause, already Closed). No push failure is needed to explain the observation.
4. **Item 4:** Session-wrap push is the documented and functioning path for commits reaching origin. No operational gap exists.

The BACKLOG entry's premise — "teardown should be pushing commits to origin" — was the Planner's mental model at the time of authoring, not the actual code. The "documented design" the entry cites was never implemented in Bellows. The actual architecture:

- **Pre-v4.47:** Agents pushed from plan prose instructions (the mechanism identified by the 2026-05-21 teardown-git-operations diagnostic). Bellows teardown cherry-picked the same commits onto local main as a parallel path.
- **Post-v4.47:** Agents are prohibited from pushing. Bellows teardown cherry-picks onto local main. Planner/CEO session-wrap pushes to origin.

No concrete failure mode exists to close. "Teardown push silently fails" is not a failure mode — there is no push to fail. Cannot name a specific line of code, return value, or error path where a push is attempted and fails. The diagnostic's discipline note applies: the BACKLOG entry was authored from the 2026-05-24 P0 loop observation (50-commit local accumulation) without scanning the v4.47 architectural shift (agent push prohibition shipped 2026-05-21) or the 2026-05-21 teardown-git-operations diagnostic (which established the zero-push-calls claim). The entry's framing reflects a mental model that never matched the code.

### Recommended action
Close the BACKLOG entry "Teardown push silently fails on long-running plans without surface signal" (2026-05-24) as **RETIRE — premise wrong**. Retirement reasoning: Bellows contains zero push calls; `_teardown_worktree` has zero origin interactions; the "silent failure" was absence of a feature that was never implemented and is not needed (session-wrap push covers the operational need). The 50-commit accumulation was caused by the P0 loop, not push absence.

### Revisit trigger
If a future design decision introduces a push call into `_teardown_worktree` (e.g., to reduce commit delivery latency between session-wraps), that implementation should include error capture, logging, and notification — but this is a feature-design concern, not a bug-fix concern. File as a new BACKLOG entry at that time with the appropriate "capability addition" framing.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Executed the ship-or-retire disposition for the BACKLOG entry "Teardown push silently fails on long-running plans without surface signal" (2026-05-24). Confirmed the 2026-05-21 zero-push-calls finding with a fresh grep, characterized `_teardown_worktree`'s complete behavior (5 local-only git operations, zero origin interactions), reconciled the 2026-05-24 50-commit observation with the absence of push (explained by P0 loop + cherry-pick accumulation), and confirmed session-wrap push as the operational path with no gap.

### Files Deposited
- `knowledge/research/teardown-push-silent-failure-disposition-2026-05-26.md` — disposition findings (RETIRE)

### Files Created or Modified (Code)
- None (read-only diagnostic)

### Decisions Made
- Classified the BACKLOG entry's premise as wrong: teardown was never designed to push, the "documented design" was the Planner's mental model, not actual code
- Recommended RETIRE disposition with explicit revisit trigger

### Flags for CEO
- **Disposition: RETIRE.** The BACKLOG entry "Teardown push silently fails on long-running plans without surface signal" (2026-05-24) should be closed as premise-wrong. Bellows contains zero `git push` calls; `_teardown_worktree` has zero origin interactions; the 50-commit local accumulation was caused by the P0 loop (already Closed), not by push absence. No concrete failure mode exists — there is no push to fail silently. Session-wrap push is the documented and functioning path for commits reaching origin post-v4.47. The entry was authored from observation of the P0 loop's effects without scanning the v4.47 agent-push prohibition or the 2026-05-21 teardown diagnostic that established the zero-push-calls claim.

### Flags for Next Step
- None — terminal diagnostic.
