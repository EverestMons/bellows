# Worktree Teardown Bug Diagnosis — 2026-05-03

## Q1 — Literal Python Error

### Root Cause

The error `string indices must be integers` is raised at **`verdict.py:102`**, NOT inside `_teardown_worktree` itself:

```python
# verdict.py lines 99-102
if pause_reason == "gate_failure" and gate_result.get("failures"):
    failures_text = ""
    for f in gate_result["failures"]:
        failures_text += f"- **{f['gate']}**: {f['evidence']}\n"  # <-- CRASH HERE
```

The function `post_verdict_request` assumes every element in `gate_result["failures"]` is a **dict** with keys `'gate'` and `'evidence'`. But `bellows.py` appends **plain strings** when `WorktreeTeardownError` is caught:

```python
# bellows.py line 405 (final-step pause path)
except WorktreeTeardownError as e:
    _pause_reason = "gate_failure"
    gate_result["failures"].append(f"worktree_teardown_failed: {e}")  # STRING, not dict
```

When `f` is the string `"worktree_teardown_failed: cherry-pick conflict on..."`, the expression `f['gate']` attempts string indexing with a string key, raising `TypeError: string indices must be integers`.

### All affected locations in bellows.py

| Line | Context | Appends string? |
|------|---------|-----------------|
| 340 | Mid-step pause: `except WorktreeTeardownError` | YES — `f"worktree_teardown_failed: {e}"` |
| 405 | Final-step pause: `except WorktreeTeardownError` | YES — `f"worktree_teardown_failed: {e}"` |
| 433 | Auto-close: `except WorktreeTeardownError` | YES — `f"worktree_teardown_failed: {e}"` |

All three paths call `verdict.post_verdict_request` afterward with `pause_reason="gate_failure"`, triggering the crash at `verdict.py:102`.

### Comparison with gates.py (correct format)

Every failure appended by `gates.py` is a dict:
```python
# gates.py — ALL failures use this format
failures.append({"gate": "receipt_status", "evidence": status})
failures.append({"gate": "ceo_flags", "evidence": "; ".join(flags)})
failures.append({"gate": "scope_check", "evidence": ...})
failures.append({"gate": "deposit_exists", "evidence": f"missing: {path}"})
```

### Reproduction transcript

```python
>>> gate_result = {"passed": True, "is_qa_step": False, "failures": [], "files_changed": []}
>>> gate_result["failures"].append("worktree_teardown_failed: cherry-pick conflict on 44ab370...")
>>> pause_reason = "gate_failure"
>>> # verdict.py line 99 condition:
>>> pause_reason == "gate_failure" and gate_result.get("failures")
['worktree_teardown_failed: cherry-pick conflict on 44ab370...']  # truthy
>>> # verdict.py line 101-102:
>>> for f in gate_result["failures"]:
...     f"- **{f['gate']}**: {f['evidence']}\n"
TypeError: string indices must be integers
```

### Crash sequence (exact order matching observed console output)

1. `bellows.py:428` → `_teardown_worktree(project_path, wt_path, plan_slug)` called
2. `bellows.py:565` → section (a) prints: `⚠ could not detect main branch for close-2026-05-03-step-count-regression-2026-05-03, falling back to 'main'`
3. `bellows.py:583-594` → section (c) cherry-pick fails → `WorktreeTeardownError` raised
4. `bellows.py:403-405` → caught; string appended to failures; `_pause_reason = "gate_failure"`
5. `bellows.py:406` → `verdict.post_verdict_request(..., pause_reason="gate_failure", ...)`
6. `verdict.py:102` → `f['gate']` on string → `TypeError: string indices must be integers`
7. TypeError propagates (not caught as `WorktreeTeardownError`)
8. `bellows.py:458-459` → `except Exception as e:` catches it → prints `❌ FAILED — ...string indices must be integers`

### Why the stranded worktree and stuck plan state

The TypeError at step 6 bypasses ALL cleanup:
- No `verdict_pending_path` rename (plan stays `in-progress-`)
- No `git worktree remove` (worktree stranded on disk)
- No verdict request posted
- No ledger entry written

---

## Q2 — Monorepo Worktree at Governance-Root

### Hypothesis: Confirmed

`bellows/` has **no `.git`** (neither directory nor file). Git commands from `cwd=bellows/` walk up to `/Users/marklehn/Desktop/GitHub/.git` (governance-root). Consequently:

```python
# _create_worktree (bellows.py:529)
cmd = ["git", "--no-pager", "worktree", "add", wt_path, "HEAD", "--detach"]
result = subprocess.run(cmd, cwd=project_path, ...)  # project_path = bellows/
```

Creates a worktree of the **entire governance-root repo**, not just bellows/.

### Evidence from reproduction

```
$ git -C /Users/marklehn/Desktop/GitHub/bellows worktree add /tmp/bellows-teardown-test HEAD --detach
Preparing worktree (detached HEAD b1b4790)

$ cat /tmp/bellows-teardown-test/.git
gitdir: /Users/marklehn/Desktop/GitHub/.git/worktrees/bellows-teardown-test

$ ls /tmp/bellows-teardown-test/
anvil  ARCHITECTURE.md  bellows  COMPANY.md  governance  knowledge  LESSONS.md  PLANNER_TEMPLATE.md  SPECIALIST_TEMPLATE.md
```

The worktree contains ALL governance-root content (anvil, bellows, forge, etc.), not just bellows/.

### Consequences

1. **`origin/HEAD` not set for governance-root** → section (a) detection fails → fallback to `'main'`
2. **Cherry-pick targets governance-root's main branch** — any dirty state in the governance-root working tree (119 files observed today) can conflict with the agent's commit
3. **Scope mismatch**: agent works in `wt_path/bellows/...` but the worktree root is governance-root level. `_capture_git_diff(wt_path)` captures ALL governance-root changes, not just bellows/
4. **Worktree metadata stored at governance-root level**: `/Users/marklehn/Desktop/GitHub/.git/worktrees/<slug>/` — not bellows-local

### Analogous to BACKLOG #4

BACKLOG #4 fixed `_capture_git_diff` by adding `--relative -- .` to scope git output to the project subtree. The fix pattern was: detect that `project_path` is a subdirectory of the actual repo root and scope operations accordingly. `_create_worktree` and `_teardown_worktree` need the same treatment.

### Fix-shape options for the monorepo trap

| Option | Description | Tradeoffs |
|--------|-------------|-----------|
| (a) Detect governance-root and refuse | If `rev-parse --show-toplevel` != project_path, skip worktree creation | Simple but means bellows-self plans never get isolation |
| (b) Create worktree at discovered repo root, scope agent cwd to subdir | `wt_path = <repo_root>/.bellows-worktrees/<slug>/`, agent cwd = `wt_path/bellows/` | Preserves isolation; agent sees correct relative paths; more complex path logic |
| (c) Give bellows its own .git (standalone repo) | One-time restructure: `git init` in bellows/, push to own remote | Cleanest long-term; requires migration |
| (d) Create worktree then `git sparse-checkout` to bellows/ subdir only | Reduces scope of worktree content | Complex; sparse-checkout has edge cases |

---

## Q3 — Other-Project Teardown Audit

| project | has own .git? | origin/HEAD set? | default branch (per HEAD) | worktree creation likely succeeds? | teardown likely succeeds for read-only plan? | teardown likely succeeds for committing plan? | notes |
|---|---|---|---|---|---|---|---|
| invoice-pulse | yes (dir) | yes (origin/main) | main | yes | yes | yes | — |
| BrewBuddy | yes (dir) | yes (origin/main) | main | yes | yes | yes | — |
| study | yes (dir) | yes (origin/main) | main | yes | yes | yes | — |
| ai-career-digest | yes (dir) | no | main | yes | yes | likely yes (main exists) | should set origin/HEAD |
| freight-kb | yes (dir) | no | main | yes | yes | likely yes (main exists) | should set origin/HEAD |
| forge | yes (dir) | yes (origin/main) | main | yes | yes | yes | — |
| anvil | yes (dir) | no | main | yes | yes | likely yes (main exists) | should set origin/HEAD |
| bellows | **no** | no | main (governance-root) | **NO — monorepo trap** | yes (no commits → no cherry-pick) | **NO — crash on cherry-pick failure** | git resolves to governance-root |

### Key findings

1. **Bellows is the ONLY project without its own `.git`** — all other projects have standalone repos
2. **Three projects (ai-career-digest, freight-kb, anvil)** lack `origin/HEAD` but have a `main` branch — the fallback to `'main'` is correct for them. They produce the warning message but function correctly
3. **No other project inherits the monorepo trap** — the type mismatch bug (Q1) can still trigger for any project if cherry-pick fails (e.g., dirty working tree), but the monorepo trap makes failures far more likely for bellows specifically
4. **The Q1 type mismatch bug is universal** — it affects ALL projects, not just bellows. If any cherry-pick fails for any reason (network timeout, dirty state, conflict), the error handling crashes

---

## Q4 — Fix-Shape Recommendation

### Fix (a): Literal Python error — type mismatch in failure format

**What:** Change bellows.py lines 340, 405, 433 to append dicts instead of strings:
```python
# Before (crashes verdict.py):
gate_result["failures"].append(f"worktree_teardown_failed: {e}")

# After (matches gates.py format):
gate_result["failures"].append({"gate": "worktree_teardown", "evidence": str(e)})
```

**LOC:** ~3 lines changed (one per site)
**Independent?** YES — can ship without (b) or (c). Fixes the crash for ALL projects.
**Risk:** Zero — purely aligning format with the existing contract in verdict.py.

### Fix (b): Monorepo worktree-at-governance-root

**What:** In `_create_worktree`, detect when `project_path` is a subdirectory of the actual git repo (via `rev-parse --show-toplevel`). When detected:
- Create the worktree at repo-root level (e.g., `<repo_root>/.bellows-worktrees/<slug>/`)
- Return the SUBDIR path as the effective working directory for the agent: `<worktree>/<relative_project_path>/`
- Update `_teardown_worktree` to resolve cherry-pick and porcelain operations from the correct root

**LOC:** ~20-30 lines (detection logic + path remapping in both create and teardown)
**Independent?** Mostly independent of (a), but (a) should ship FIRST to prevent crashes during development/testing of (b).
**Alternative:** Give bellows its own `.git` (option (c) in Q2 table). This is structurally cleaner but requires a one-time repo reorganization beyond the scope of a code fix.

### Fix (c): `origin/HEAD` warnings for ai-career-digest, freight-kb, anvil

**What:** Run `git remote set-head origin --auto` in each project to set `origin/HEAD` correctly. This eliminates the noisy fallback warning.

**LOC:** 0 code changes — just 3 one-time git commands.
**Independent?** YES — purely environmental.

### Sequencing recommendation

1. **Ship (a) first** — 3-line fix, eliminates the crash for all projects immediately. Can be a standalone plan.
2. **Ship (c) concurrently** — no code change, just env setup. Can happen in the same plan or ad-hoc.
3. **Ship (b) after** — larger change requiring the monorepo detection + path logic. Should include a test case that creates a worktree from a subdirectory of a multi-project repo. Can be a separate plan.

All three fixes are independent — no sequencing dependency. But (a) is the highest priority because it makes the error handling non-crashy even if (b) isn't yet shipped. With (a) alone, a bellows-self plan that hits a cherry-pick conflict would correctly pause for verdict instead of crashing.

### Unanticipated finding (flag for CEO)

The **cherry-pick failure trigger** is not solely a monorepo issue. The governance-root working tree had **119 dirty files** at time of diagnosis. If any of those dirty files overlap with a worktree commit's changed files, `git cherry-pick` refuses to proceed. This means:
- Even after fix (b) lands, cherry-pick can still fail if the real working tree has uncommitted changes to the same files
- Fix (a) (the type mismatch fix) is the real safety net — it ensures failures are HANDLED, not that they don't OCCUR
- A more robust approach for section (c) of `_teardown_worktree` could stash uncommitted changes before cherry-pick and pop them after, but this adds complexity and risk. The simpler path is: let cherry-pick fail, handle it correctly via (a), and surface it as a verdict request for CEO resolution.

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1 (diagnostic, single-step)
**Status:** Complete

### What Was Done
Diagnosed the worktree teardown crash reported in BACKLOG 2026-05-03. Identified the literal Python error (type mismatch: string indexed as dict in verdict.py, triggered by bellows.py appending wrong format to failures list), confirmed the monorepo worktree-at-governance-root hypothesis, audited all 8 watched projects, and produced fix-shape recommendations.

### Files Deposited
- `bellows/knowledge/research/worktree-teardown-bug-diagnosis-2026-05-03.md` — full Q1-Q4 findings

### Files Created or Modified (Code)
- None (investigation only)

### Decisions Made
- Used /tmp/ reproduction (stranded worktree was already cleaned up during manual recovery)
- Classified the bug as a type-contract violation between bellows.py and verdict.py (not a subprocess handling bug as initially hypothesized in BACKLOG)

### Flags for CEO
- **The type mismatch bug affects ALL projects**, not just bellows — any cherry-pick failure on any project would crash the same way. Fix (a) should ship before Bellows restarts.
- **Cherry-pick reliability depends on clean working tree state** — the governance-root had 119 dirty files. Consider whether Bellows should stash before cherry-pick or accept failure-and-verdict as the path.
