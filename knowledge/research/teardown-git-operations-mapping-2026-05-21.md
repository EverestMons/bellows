# Findings — Teardown Git Operations Mapping & Parallel-SHA Divergence

**Diagnostic:** diagnostic-teardown-git-operations-mapping-2026-05-21
**Date:** 2026-05-21
**Agent:** Bellows Systems Analyst
**Scope:** Map actual git operation timeline from agent dispatch through teardown through next-session-start; explain parallel-SHA local-vs-origin divergence pattern observed in the 2026-05-21 session (mis-dated 2026-05-27 in earlier artifacts).

---

## Q1 Answer — Does the dispatched agent execute `git push`?

**YES.** The agent pushes to origin. Three independent evidence streams confirm this:

### Evidence A — Plan step prose contains explicit push instructions

Grep of `knowledge/decisions/` (Done/ and halted/) for `git push` and `push to origin`:

| File | Line | Instruction |
|------|------|-------------|
| `halted-executable-auto-close-type-safety-2026-05-17.md` | 51 | "Commit with message ... and push to origin/main." |
| `executable-lessons-forge-extraction-phase-b2-governance-wiring-2026-05-18.md` | 386 | `git push origin main` |
| `executable-lessons-forge-extraction-phase-b2-governance-wiring-2026-05-18.md` | 413 | `git push origin main` |
| `halted-executable-bellows-dispatch-mode-validator-2026-05-19.md` | 98 | "Push to origin/main." |
| `halted-executable-rule-20-bold-tolerance-2026-05-17.md` | 61 | "push to origin/main." |

The Planner authors plan step prose that explicitly instructs agents to run `git push origin main` as part of their housekeeping after committing.

### Evidence B — `Bash(git:*)` auto-approves all git commands

`.claude/settings.local.json:4`:
```json
"Bash(git:*)"
```

This permission rule auto-approves ALL git commands (including `git push`, `git push --force`, `git reset --hard`) without interactive prompt. The agent running via `claude -p` with `--allowedTools "Read,Edit,Write,Bash"` can execute any git command without operator confirmation. This was flagged in the 2026-05-04 bash-permission-rules-audit as a critical gap (zero deny rules for destructive commands).

### Evidence C — Reflog timestamps confirm agent-side pushes

```
80ca915 refs/remotes/origin/main@{2026-05-20 23:33:52 -0500}: update by push
```

The commit `80ca915` was authored at committer-date `1779338028` (2026-05-20 23:33:48) and pushed to origin 4 seconds later at 23:33:52. This timing is consistent with an agent executing `git commit` followed immediately by `git push` — not with a human session-wrap push.

### Evidence D — Agent specialist files do NOT prescribe push

BELLOWS_QA.md, BELLOWS_DEVELOPER.md, BELLOWS_SYSTEMS_ANALYST.md, and BELLOWS_DOCUMENTATION_ANALYST.md contain zero references to `git push`. The push originates solely from Planner-authored plan step prose.

### Evidence E — BELLOWS_AGENT_SYSTEM_PROMPT says "commit" not "push"

`runner.py:23`:
```python
BELLOWS_AGENT_SYSTEM_PROMPT = """...Your final operation is ALWAYS the commit..."""
```

The system prompt says "commit" as the final operation. The agent pushes because plan step prose overrides this with an explicit `git push` instruction, and Claude Code's own system prompt says "DO NOT push to the remote repository unless the user explicitly asks you to do so" — but the plan prompt IS the "user" from Claude Code's perspective, and when the plan says "push to origin/main," the agent complies.

### Claim Verification Block — Q1

**Claim:** "Agent specialist files contain no git push instructions."
**Query:** `grep -r "git push" agents/BELLOWS_*.md`
**Result:** Zero matches. Verified 2026-05-21.

**Claim:** "Bash(git:*) auto-approves all git commands."
**Query:** `cat .claude/settings.local.json | grep "git:"`
**Result:** `"Bash(git:*)"` at line 4. No deny rules exist for git push or git push --force.

---

## Q2 Answer — Git subprocess calls in the Bellows codebase

### Enumerated call sites

| # | File:Line | Git Subcommand | Trigger | Direction |
|---|-----------|---------------|---------|-----------|
| 1 | `bellows.py:674` | `git diff --stat --relative -- .` | Pre/post step file-change tracking | read-only |
| 2 | `bellows.py:739` | `git worktree add <wt_path> HEAD --detach` | Plan claim → worktree creation | local write |
| 3 | `bellows.py:769` | `git symbolic-ref --short refs/remotes/origin/HEAD` | Teardown → detect main branch | read-only |
| 4 | `bellows.py:786` | `git log --format=%H HEAD --not <main>` | Teardown → collect worktree commits | read-only |
| 5 | `bellows.py:817` | `git cherry-pick <sha>` | Teardown → integrate agent commits | local write |
| 6 | `bellows.py:822` | `git cherry-pick --abort` | Teardown → conflict cleanup | local write |
| 7 | `bellows.py:833` | `git status --porcelain` | Teardown → dirty file detection | read-only |
| 8 | `bellows.py:857` | `git worktree remove <wt_path> --force` | Teardown → worktree cleanup | local write |
| 9 | `bellows.py:877` | `git log -1 --format=%h -- bellows.py` | Source SHA display | read-only |
| 10 | `bellows.py:903` | `git log -1 --format=%h -- <module>` | Module fingerprint heartbeat | read-only |
| 11 | `bellows.py:1013` | `git worktree prune` | Startup → stale worktree cleanup | local write |

**Total: 11 call sites, 0 push operations.** Pre-diagnostic claim VERIFIED: Bellows contains zero `git push` subprocess calls anywhere in the codebase.

### Claim Verification Block — Q2

**Claim:** "Bellows codebase contains zero git push calls."
**Query:** `grep -rn "subprocess.*push\|git.*push" bellows/*.py` (also `grep -rn "push" *.py | grep -i git`)
**Result:** Zero matches in `bellows.py`, `runner.py`, `gates.py`, `verdict.py`, `parser.py`, `planner.py`, `server.py`, `notifier.py`, `decisions.py`, `validators.py`.

---

## Q3 Answer — End-to-end trace: `eeaedcb` (local) ≡ `4294706` (origin)

### Raw commit data

**4294706 (on origin — agent's original commit):**
```
commit 4294706327e4b2da68d4f921563c3fc132d25731
tree 59df0694553167a4248e47e3c00964da601fd3da
parent 80ca91559e11aa3c2b652a63c1d6a5045475064f
author Mark Lehn <marklehn@icloud.com> 1779339036 -0500
committer Mark Lehn <marklehn@icloud.com> 1779341423 -0500
    fix(gates): normalize path forms in _gate_deposit_exists abs-vs-rel comparison
```

**eeaedcb (on local main — cherry-pick copy):**
```
commit eeaedcba65585e451c0c1f7786f8b3e94b76a4da
tree 59df0694553167a4248e47e3c00964da601fd3da
parent 307576474a6143eaa2990497621683d7bc6d0ab0
author Mark Lehn <marklehn@icloud.com> 1779339036 -0500
committer Mark Lehn <marklehn@icloud.com> 1779339466 -0500
    fix(gates): normalize path forms in _gate_deposit_exists abs-vs-rel comparison
```

### Field comparison

| Field | 4294706 (origin) | eeaedcb (local) | Same? |
|-------|------------------|-----------------|-------|
| tree | `59df069...` | `59df069...` | **YES** — content-identical |
| parent | `80ca915...` | `3075764...` | **NO** — different parent chains |
| author | `marklehn 1779339036` | `marklehn 1779339036` | **YES** — preserved by cherry-pick |
| committer | `marklehn 1779341423` | `marklehn 1779339466` | **NO** — cherry-pick uses new timestamp |
| message | `fix(gates): normalize...` | `fix(gates): normalize...` | YES |

**`git diff 4294706 eeaedcb` returns empty** — content-identical confirmed.

### (a) What produced `4294706` on origin?

**Agent-side push.** The commit was authored at 23:50:36 (AuthorDate 1779339036) in a Bellows-created worktree. The agent then pushed to origin. The reflog shows `refs/remotes/origin/main` updated to `7f0c6f2` at `2026-05-21 00:30:28` — this push included `4294706`, `8469c44`, and `7f0c6f2` as a single fast-forward push from `80ca915`.

### (b) What produced `eeaedcb` on local?

**Bellows cherry-pick during teardown.** Reflog:
```
eeaedcb refs/heads/main@{2026-05-20 23:57:46}: cherry-pick: fix(gates): normalize path forms...
```

`_teardown_worktree` (bellows.py:757) collected the commit via `git log --format=%H HEAD --not main` (line 786, cwd=wt_path) and cherry-picked it onto the local main checkout (line 817, cwd=project_path).

### (c) Why different SHAs despite identical content?

Two factors:
1. **Different parent SHA:** `4294706` has parent `80ca915` (the agent's diagnostic commit on origin). `eeaedcb` has parent `3075764` (the cherry-picked copy of that same diagnostic commit on local). Since the first commit in the chain already diverged (due to committer-date difference), all subsequent commits have different parents.
2. **Different committer date:** Cherry-pick preserves AuthorDate but sets CommitDate to the current time. `4294706` has CommitDate `1779341423` (00:30:23); `eeaedcb` has CommitDate `1779339466` (23:57:46).

Either difference alone would produce a different SHA. Together they guarantee it.

### (d) After teardown, what does Bellows do with local main?

**Nothing.** No push, no fetch, no reset, no pull. `_teardown_worktree` exits after worktree removal (line 864). Control returns to `run_plan`, which posts a verdict request, renames to `verdict-pending-`, and returns. Local main retains the cherry-picked commits; origin/main retains the agent's original commits. The divergence persists until manual reconciliation.

### (e) Divergence state at session end

At session end (before reconciliation):
- **Local main** at `9acd499`: `d1b60c1` → `2f47b64` → `2bfc8aa` → `3075764` → `eeaedcb` → `289df0c` → `9acd499`
- **Origin/main** at `7f0c6f2`: `d1b60c1` → `2f47b64` → `2bfc8aa` → `80ca915` → `4294706` → `8469c44` → `7f0c6f2`

Local was 4 commits ahead of origin (the cherry-pick copies `3075764`, `eeaedcb`, `289df0c` + manual recovery `9acd499`).
Origin was 4 commits ahead of local (the agent originals `80ca915`, `4294706`, `8469c44`, `7f0c6f2`).

**Reconciled** at `2026-05-21 00:37:20` via `git reset --hard origin/main`, moving local to `7f0c6f2`.

### Timeline

| Time | Actor | Operation | SHA | On |
|------|-------|-----------|-----|-----|
| 23:16:59 | Bellows teardown | cherry-pick ×2 (disable-autoupdater) | `2f47b64`, `2bfc8aa` | local main |
| ~23:33 | Agent (worktree) | commit (diagnostic) | `80ca915` | worktree HEAD |
| 23:33:52 | Agent (worktree) | `git push origin main` | `80ca915` | origin/main |
| 23:34:22 | Bellows teardown | cherry-pick (diagnostic) | `3075764` | local main |
| ~23:50 | Agent (worktree) | commit (fix) | — (becomes `4294706` on push) | worktree HEAD |
| ~23:57 | Agent (worktree) | commit (QA) | — (becomes `8469c44` on push) | worktree HEAD |
| 23:57:46 | Bellows teardown | cherry-pick ×2 (fix + QA) | `eeaedcb`, `289df0c` | local main |
| ~00:30 | Agent (worktree) | commit (verdict-enrichment diag) | `7f0c6f2` | worktree HEAD |
| 00:30:28 | Agent (worktree) | `git push origin main` | up to `7f0c6f2` | origin/main |
| 00:34:19 | CEO (manual) | commit (recovered from uncommitted worktree) | `9acd499` | local main |
| 00:37:20 | CEO (manual) | `git reset --hard origin/main` | → `7f0c6f2` | local main |
| 00:53:26 | CEO (manual) | commit (session wrap) | `aa3fc6f` | local main |
| 00:53:27 | CEO (manual) | `git push` | `aa3fc6f` | origin/main |

---

## Q4 Answer — Mechanism producing the divergence

The parallel-SHA divergence is caused by a dual-path commit delivery architecture that was not designed to exist. **Path A (agent push):** The dispatched agent, running via `claude -p` in a Bellows-created worktree (bellows.py:739, `git worktree add ... --detach`), executes `git push origin main` as instructed by Planner-authored plan step prose. The `Bash(git:*)` permission in `.claude/settings.local.json` auto-approves this push. This updates `origin/main` with the agent's commit (original SHA, original parent chain, original committer date). **Path B (Bellows cherry-pick):** After the `claude -p` subprocess exits, `_teardown_worktree` (bellows.py:757) collects the same commit via `git log --format=%H HEAD --not main` (line 786, cwd=wt_path) and cherry-picks it onto the local main checkout (line 817, cwd=project_path). Cherry-pick produces a new commit with the same tree and author date but a new committer timestamp and (for all commits after the first in a chain) a new parent SHA, yielding a content-identical commit with a different SHA. Bellows performs no post-teardown push or fetch (confirmed: zero push calls in Q2), so the divergence persists until manual reconciliation. **This is not a Bellows bug — Bellows's teardown is functioning exactly as designed.** The bug is architectural: teardown was designed for a world where the agent does NOT push to origin. The introduction of `git push` instructions in Planner-authored plans created a second delivery path for the same commits, producing the parallel-SHA divergence.

---

## Q5 Answer — Recovery surface

### (a) Is `git reset --hard origin/main` safe in all cases?

**NO — it is safe ONLY when all unique local commits are already on origin** (possibly under different SHAs due to the parallel-SHA pattern). If local main has commits that were NEVER pushed to origin — e.g., manual CEO commits made between teardowns, or Bellows lifecycle artifacts committed by session-wrap but not yet pushed — those commits would be irrecoverably lost.

In the observed 2026-05-21 session, the local-only commit `9acd499` ("recovered from uncommitted worktree") was content-identical to `7f0c6f2` on origin. The reset was safe in this specific case. But the safety depends on the operator's knowledge of what's on local vs. origin.

A safer reconciliation sequence would be:
```
git fetch origin
git log HEAD --not origin/main --oneline  # verify nothing unique is local-only
git reset --hard origin/main
```

### (b) Should Bellows auto-reconcile post-teardown?

**NO.** An automatic `git reset --hard origin/main` after teardown would:
- Overwrite any CEO or Planner work-in-progress on local main
- Discard cherry-picked commits from other plans that haven't yet been pushed
- Create a footgun when Bellows is running concurrent plans (Plan A teardown resets local, discarding Plan B's cherry-picked commits)

A `git push origin main` after teardown would be safer but introduces push contention with the agent's concurrent push and could fail if origin has advanced beyond what local knows about.

### (c) Observability recommendations

1. **Startup-sweep divergence check:** At Bellows startup (in `_perform_startup_sweep` or `start`), run:
   ```
   git rev-list --count HEAD --not origin/main
   git rev-list --count origin/main --not HEAD
   ```
   If either count > 0, log a warning: `⚠ local/origin divergence: local +{N} / origin +{M}`.

2. **Post-teardown divergence check:** After `_teardown_worktree` completes (all three call sites), run `git fetch origin` and check divergence. Log a warning if detected. Do NOT auto-reconcile.

3. **Reflog-based push detection:** After teardown, check if `refs/remotes/origin/main` advanced during the agent's execution window. If it did, log: `⚠ agent pushed to origin during execution — local/origin divergence expected`.

---

## Q6 Answer — Implications for Priority 1

### Does the divergence compound?

**YES — the divergence compounds per-agent-push, which is per-plan-dispatch.** Each plan dispatch produces:
1. One or more agent commits in the worktree
2. One agent push to origin (including all commits since worktree creation)
3. One Bellows teardown cherry-picking the same commits onto local main

For the Priority 1 verdict-enrichment executable with 5 deposits (each producing an agent commit + teardown), each dispatch would produce one parallel-SHA pair per commit. At session end, local would be ahead by N cherry-picks and origin ahead by N agent pushes (where N is the total number of agent commits across all dispatches).

### Is it effectively rate-limited?

No. The 2026-05-21 session demonstrated 4 parallel-SHA pairs from 3 plan dispatches in a single evening. The Priority 1 plan with 5 deposits would produce at least 5 pairs (likely more, since QA steps and feedback commits add additional commits per dispatch). The divergence grows linearly with dispatch count.

### Recommendation for Priority 1

**Priority 1 can proceed without code changes to Bellows**, subject to ONE of:

1. **Preferred — Remove `git push` from Priority 1 plan step instructions.** Replace "Commit with message X and push to origin/main" with "Commit with message X. Do NOT push — the Planner will handle session-wrap commits." This eliminates Path A entirely, leaving only Path B (Bellows cherry-pick → local main). The CEO/session-wrap pushes to origin at session end.

2. **Acceptable — Accept the divergence operationally.** Dispatch Priority 1 as-is. At session end, run `git fetch origin && git log HEAD --not origin/main --oneline` to verify no unique local commits, then `git reset --hard origin/main` to reconcile. This is the same procedure used successfully on 2026-05-21.

Option 1 is preferred because it eliminates the divergence at the source rather than requiring post-hoc reconciliation. It also aligns the agent's behavior with the BELLOWS_AGENT_SYSTEM_PROMPT ("Your final operation is ALWAYS the commit") and Claude Code's default instruction ("DO NOT push to the remote repository unless the user explicitly asks").

### Longer-term fix

The root cause is that the Planner's plan template includes `git push` in the housekeeping section. The PLANNER_TEMPLATE.md (not accessible from this worktree — located outside the bellows repo) should be updated to remove `git push` from the standard housekeeping order. Plans should instruct agents to commit only; Bellows teardown integrates the commit onto local main; the CEO/session-wrap pushes.

---

## Claim Verification Blocks

### CVB-1: "Bellows codebase contains zero git push calls"
**Query:** `grep -rn "subprocess.*push\|git.*push" *.py`
**Result:** Zero matches across all 10 Python modules.
**Confidence:** HIGH — exhaustive search, unambiguous.

### CVB-2: "Agent pushes to origin from worktree"
**Query:** `git reflog --date=iso refs/remotes/origin/main | head -15`
**Result:** `80ca915 refs/remotes/origin/main@{2026-05-20 23:33:52}: update by push` — 4 seconds after commit at 23:33:48. Agent-side timing confirmed.
**Confidence:** HIGH — reflog is authoritative for push events.

### CVB-3: "Bash(git:*) auto-approves all git commands"
**Query:** `cat .claude/settings.local.json`
**Result:** `"Bash(git:*)"` at line 4, inside `permissions.allow` array. No deny rules exist.
**Confidence:** HIGH — settings file is unambiguous.

### CVB-4: "Cherry-pick produces different SHA due to committer-date and parent differences"
**Query:** `git show --pretty=raw 4294706` and `git show --pretty=raw eeaedcb`
**Result:** Same tree `59df069...`, same author date `1779339036`, different parent (`80ca915` vs `3075764`), different committer date (`1779341423` vs `1779339466`).
**Confidence:** HIGH — raw commit data is authoritative.

### CVB-5: "Plan step prose includes git push instructions"
**Query:** `grep -r "git push\|push to origin" knowledge/decisions/`
**Result:** 7 matches across 5 plan files (Done/ and halted/), all instructing agents to push after committing.
**Confidence:** HIGH — direct grep evidence.

### CVB-6: "No push in agent specialist files"
**Query:** `grep -r "git push" agents/BELLOWS_*.md`
**Result:** Zero matches across all 4 specialist files (QA, Developer, SA, Documentation Analyst).
**Confidence:** HIGH — exhaustive search.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Mapped the complete git operation timeline from agent dispatch through teardown through session-end reconciliation. Identified the dual-path commit delivery mechanism (agent push + Bellows cherry-pick) that produces the parallel-SHA divergence. Verified all six investigation questions with reflog forensics, raw commit data, subprocess call enumeration, and grep evidence across plan files and settings.

### Files Deposited
- `knowledge/research/teardown-git-operations-mapping-2026-05-21.md` — this diagnostic findings file

### Files Created or Modified (Code)
- None (read-only diagnostic)

### Decisions Made
- Classified the divergence as an architectural mismatch (agent push + Bellows cherry-pick dual-path), not a Bellows code bug
- Recommended removing `git push` from Planner-authored plan step instructions as the preferred fix
- Assessed Priority 1 as safe to proceed with operational adjustment (either remove push from plan steps or accept divergence and reconcile at session end)

### Flags for CEO
- **PLANNER_TEMPLATE.md not accessible from worktree** — Rule 23 housekeeping order could not be directly verified. Evidence from plan files confirms agents are instructed to push, but the template itself was not read.
- **`Bash(git:*)` permission is overly broad** — auto-approves `git push --force`, `git reset --hard`, and all destructive git commands. Flagged in 2026-05-04 bash-permission audit but not yet addressed.

### Flags for Next Step
- None — terminal diagnostic. The recommended operational change (remove `git push` from plan step prose) is a Planner-side edit, not a Bellows code change.
