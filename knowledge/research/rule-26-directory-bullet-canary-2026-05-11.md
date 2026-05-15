# Rule 26 Directory-Bullet Acceptance Canary — Findings

**Date:** 2026-05-11
**Diagnostic:** diagnostic-rule-26-directory-bullet-canary-2026-05-11
**Author:** Systems Analyst

---

## 1. Verdict

**YES** — the current gate-5 implementation fully accepts a directory-only `**Deposits:**` bullet. A `**Deposits:**` block containing only a directory path resolves successfully and does not trigger a Gate 5 failure, provided the directory exists on disk.

---

## 2. Code Evidence

### `_resolve_deposit_path()` — `gates.py:183-212`

All four resolution strategies use `os.path.isfile() or os.path.isdir()`:

```python
# Strategy 0 — worktree-first (line 201)
if os.path.isfile(wt_candidate) or os.path.isdir(wt_candidate):
    return wt_candidate

# Strategy 1 — as-is (line 204)
if os.path.isfile(path) or os.path.isdir(path):
    return os.path.abspath(path)

# Strategy 2 — relative to project root (line 207)
if os.path.isfile(p2) or os.path.isdir(p2):
    return os.path.abspath(p2)

# Strategy 3 — path includes project dir name (line 210)
if os.path.isfile(p3) or os.path.isdir(p3):
    return os.path.abspath(p3)
```

Directories resolve at every strategy. No `isfile()`-only fallback exists anywhere in the resolution chain.

### `_extract_plan_required_deposits()` — `gates.py:254-270`

The Rule 26 block parser extracts backtick-quoted paths via regex `-\s+\x60([^\x60]+)\x60` and adds them to a `set()` unconditionally. **No filtering by extension or path type.** Directory paths (with or without trailing `/`) are extracted and returned identically to file paths.

### `_gate_deposit_exists()` — `gates.py:215-240`

Calls `_resolve_deposit_path()` for each plan-required path. No separate `isfile()`-only check is applied before or after resolution. If `_resolve_deposit_path()` returns non-None, the deposit is considered present. A directory that resolves does not generate a failure entry.

### `extract_primary_deposit()` — `verdict.py:34-48`

This function filters for `.md`-only paths (line 42: `if path.endswith('.md')`). A directory bullet does NOT become the primary deposit for the verdict request `Deposit:` header. However, this is independent of gate evaluation — `_gate_deposit_exists()` uses `_extract_plan_required_deposits()` from `gates.py`, not `extract_primary_deposit()` from `verdict.py`. The two paths are decoupled.

---

## 3. Historical Evidence

### Post-fix plan with directory bullet

**Plan:** `executable-deposit-exists-worktree-aware-2026-05-06.md` (Step 2)
**Deposits block (line 397-399):**
```
**Deposits:**
- `bellows/knowledge/qa/deposit-exists-worktree-aware-qa-2026-05-06.md`
- `bellows/knowledge/qa/evidence/executable-deposit-exists-worktree-aware-2026-05-06/`
```

The directory `knowledge/qa/evidence/executable-deposit-exists-worktree-aware-2026-05-06/` exists on disk (verified). The run completed with status `Complete` → `VerdictPending` (bellows.db run IDs 688+, session `ce7ff89d`). No gate-5 failure is recorded in the DB. The plan reached Done/ successfully, confirming the directory bullet did not block gate passage.

Additional historical example: `executable-close-2026-05-03-step-count-regression-2026-05-03.md` (Step 2, line 174) also declared a directory bullet `bellows/knowledge/qa/evidence/close-step-count-regression-2026-05-03/` and completed successfully.

The step-level JSON logs (`logs/`) do not record per-deposit gate outcomes (only `parsed` fields for session/cost/receipt), so gate-5 pass/fail per individual deposit cannot be extracted from log files. However, the run completing without `gate_failure` status confirms the directory bullet did not trip gate 5.

---

## 4. Simulation

Manual simulation against `_resolve_deposit_path()` with three real directory paths on disk:

| Input path | Strategy matched | Resolved to | Accepted? |
|---|---|---|---|
| `knowledge/qa/evidence/` | Strategy 2 (project-relative) | `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence` | YES |
| `bellows/knowledge/qa/evidence/` | Strategy 3 (includes project dir) | `/Users/marklehn/Desktop/GitHub/bellows/bellows/knowledge/qa/evidence` | YES |
| `knowledge/qa/evidence` (no trailing `/`) | Strategy 2 (project-relative) | `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence` | YES |

Full gate-5 simulation with a `**Deposits:**` block containing only a directory bullet: `_gate_deposit_exists()` returned zero failures. Gate 5 PASSED.

---

## 5. Stale-Knowledge Confirmation

The 2026-04-19 Lessons entry stating "deposit_exists gate uses os.path.isfile() which returns False for directory paths" **is stale**.

**What made it stale:** Commit `e609ad3` ("fix(gates): _resolve_deposit_path accepts directory paths (BACKLOG #11)"), authored 2026-04-30. This commit changed all resolution strategies in `_resolve_deposit_path()` from `os.path.isfile()` to `os.path.isfile() or os.path.isdir()`. The corresponding BACKLOG #11 was closed 2026-04-30 (see `knowledge/BACKLOG.md` line 70).

The Lessons entry predates this fix by 11 days and reflects the code state as of 2026-04-19, when `isfile()` was indeed the only check. The fix landed as part of `parallel-1-executable-deposit-exists-directory-paths-2026-04-30` with +5 unit tests covering directory acceptance.

**Implication for Rule 26 contradiction:** The current Rule 26 line 738 guidance ("list the evidence directory as a single bullet") is correct and safe — the gate accepts it. The 2026-04-19 Lesson prohibition ("Do NOT list a directory path in the block") is stale and should be updated or removed when the Planner authors the governance edit.
