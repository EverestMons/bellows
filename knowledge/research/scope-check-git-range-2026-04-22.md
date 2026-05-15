# scope_check Git-Range Mechanism — Diagnostic Findings
**Date:** 2026-04-22 | **Diagnostic:** diagnostic-scope-check-git-range-2026-04-22

---

## Mechanism Summary

`scope_check` does **not** use git directly. It receives a pre-computed `files_changed` list (produced by diffing two `git diff --stat` snapshots in `bellows.py`) and checks whether each changed file's path or basename appears as a substring in the plan step text. Files matching a static allowlist (basenames or prefixes) are exempted. There is no git range spec, no base/head SHA computation, and no claim-time metadata — the mechanism is a working-tree diff-of-diffs compared against plan text via substring search.

---

## Location

- **File:** `bellows/gates.py`
- **Function:** `_gate_scope_check`
- **Line range:** 216–241
- **Supporting constants:** `SCOPE_ALLOWLIST` (lines 8–12), `SCOPE_ALLOWLIST_PREFIXES` (line 15)

---

## Git Invocation

The gate itself issues **zero** git commands. The git invocation lives in `bellows.py`:

```python
# bellows.py:388-397
def _capture_git_diff(project_path: str) -> str:
    """Capture git diff --stat output for file change tracking."""
    try:
        result = subprocess.run(
            ["git", "--no-pager", "diff", "--stat"],
            cwd=project_path, capture_output=True, text=True, timeout=10,
        )
        return result.stdout
    except Exception:
        return ""
```

**Exact argv:** `["git", "--no-pager", "diff", "--stat"]`

This is a **working-tree vs index** diff — no commit range, no SHA arguments, no `--since`, no `HEAD~N..HEAD`. It captures all unstaged modifications in the repo at the moment it runs.

---

## Range Computation

There is no range computation in the traditional git-log sense. Instead, Bellows uses **diff-of-diffs** semantics:

1. **Pre-step snapshot:** `pre_diff = _capture_git_diff(project_path)` — captured immediately before `runner.run_step()` (bellows.py:250, 306)
2. **Post-step snapshot:** `post_diff = _capture_git_diff(project_path)` — captured immediately after `runner.run_step()` returns (bellows.py:266, 324)
3. **Delta extraction:** `_parse_diff_stat(post_diff, pre_diff)` (bellows.py:400-421):

```python
# bellows.py:400-421
def _parse_diff_stat(post_diff: str, pre_diff: str) -> list:
    def parse_stat_map(diff_text):
        result = {}
        for line in diff_text.strip().splitlines():
            line = line.strip()
            if "|" in line:
                filename, stat = line.split("|", 1)
                filename = filename.strip()
                if filename:
                    result[filename] = stat.strip()
        return result

    pre_map = parse_stat_map(pre_diff)
    post_map = parse_stat_map(post_diff)
    changed = [f for f, s in post_map.items() if pre_map.get(f) != s]
    return sorted(changed)
```

**Base ref:** the working-tree state at the moment `pre_diff` is captured (not a git ref — a diff-stat text snapshot).
**Head ref:** the working-tree state at the moment `post_diff` is captured.
**Delta:** files whose `--stat` line changed between pre and post. This filters out files that were already dirty before the step, but cannot distinguish agent writes from concurrent Bellows writes during the execution window.

---

## Plan-Owned Files Determination

The gate does **not** use a declared scope field, does not derive scope from agent commits, and does not use any plan metadata. It uses **plan step text substring matching**:

```python
# gates.py:216-241
def _gate_scope_check(plan_text, step_number, files_changed, failures):
    if not files_changed:
        return

    step_text = _extract_step_text(plan_text, step_number)
    if not step_text:
        return

    out_of_scope = []
    for fpath in files_changed:
        basename = os.path.basename(fpath)
        if basename in SCOPE_ALLOWLIST:
            continue
        if any(basename.startswith(p) for p in SCOPE_ALLOWLIST_PREFIXES):
            continue
        if fpath in step_text or basename in step_text:
            continue
        out_of_scope.append(fpath)

    if out_of_scope:
        context = step_text[:200]
        failures.append({
            "gate": "scope_check",
            "evidence": f"out-of-scope files: {', '.join(out_of_scope)} | plan step context: {context}",
        })
```

A file is considered **in-scope** if ANY of these hold:
1. Its basename is in `SCOPE_ALLOWLIST` (`agent-prompt-feedback.md`, `PROJECT_STATUS.md`, `.gitkeep`)
2. Its basename starts with a `SCOPE_ALLOWLIST_PREFIXES` entry (`in-progress-`, `verdict-pending-`, `halted-`)
3. Its full path appears as a substring in the extracted step text
4. Its basename appears as a substring in the extracted step text

Otherwise it is flagged as out-of-scope.

---

## Call Sites

Two call sites, both in `bellows.py:run_plan()`:

1. **First step** (bellows.py:268):
   ```python
   gate_result = gates.check(parsed, plan_text, current_step, project_path, files_changed=files_changed)
   ```

2. **Subsequent steps** in the while loop (bellows.py:326):
   ```python
   gate_result = gates.check(parsed, plan_text, current_step, project_path, files_changed=files_changed)
   ```

Arguments passed to `gates.check()`:
- `parsed`: the runner output dict (receipt status, cost, flags, etc.)
- `plan_text`: the full plan markdown read at plan-claim time
- `step_number`: current integer step
- `project_path`: the watched project directory (from config.json)
- `files_changed`: the diff-of-diffs result list

`gates.check()` calls `_gate_scope_check(plan_text, step_number, files_changed, failures)` at line 64.

---

## Claim-Time Metadata

**None persisted for scope_check purposes.** There is no claim-time SHA, no claim-time timestamp, no commit count, and no initial diff snapshot stored to disk. The only metadata stored at claim time is:
- The plan file rename (`shutil.move` to `in-progress-` prefix) — a filesystem operation, not scope metadata
- The shadow cache pristine copy (`_shadow_path()` → `.bellows-cache/*.pristine`) — stores the plan prompt text, not scope state

The `pre_diff` snapshot is held in a local variable for the duration of step execution, not persisted anywhere. If Bellows crashes between pre_diff capture and post_diff capture, the pre-step baseline is lost.

---

## Caching

**No caching of scope_check.** The gate is computed fresh on every invocation. Specifically:
- `_gate_scope_check` has no memoization, no disk cache, no in-memory state between calls
- `_capture_git_diff` always runs `git diff --stat` live — no cached output
- `_parse_diff_stat` is a pure function with no side effects or caching
- The `.bellows-cache/` directory stores shadow copies of plan prompts (`.pristine` files) for the bootstrap prompt mechanism — it has no relation to gate state

---

## Incident Validation

**LESSONS.md** — git repo root: `/Users/marklehn/Desktop/GitHub/`

| SHA | Date | Message |
|-----|------|---------|
| `e8867dd` | 2026-04-22 10:51:33 | docs: LESSONS — Rule 25 governance gap |
| `8d24336` | 2026-04-19 20:31:55 | chore: session wrap 2026-04-19 |
| `e43ab93` | 2026-04-15 15:22:14 | docs: LESSONS.md restructure |

**BACKLOG.md** — `bellows/knowledge/BACKLOG.md`:

| SHA | Date | Message |
|-----|------|---------|
| `4dd1490` | 2026-04-19 23:22:46 | chore: status + backlog + feedback for r3 shadow cache prompt |
| `e1b0e7c` | 2026-04-19 22:36:05 | docs: BACKLOG — 3 new items from plan-mutation-source diagnostic |
| `8d24336` | 2026-04-19 20:31:55 | chore: session wrap 2026-04-19 |

**Confirmation:** Both files were modified by commits made on 2026-04-19 in session-wrap and maintenance contexts (`8d24336`, `e1b0e7c`), not during the `plan-mutation-source-2026-04-19` diagnostic's execution. The `e1b0e7c` commit explicitly identifies itself as post-diagnostic backlog additions ("3 new items from plan-mutation-source diagnostic") — Planner housekeeping after the diagnostic completed, not agent activity during execution. The processed verdict (`processed-verdict-plan-mutation-source-2026-04-19-step-1.md`) confirms: "Gate failed on same scope_check false-positive pattern (LESSONS.md, BACKLOG.md from prior commits)."

The root cause: both files had unstaged working-tree modifications at the time `_capture_git_diff` ran, and their `--stat` lines changed between pre_diff and post_diff snapshots (likely from concurrent Bellows or session-level writes), causing `_parse_diff_stat` to include them in `files_changed`. Since neither file's path nor basename appears in the plan-mutation-source step text, `_gate_scope_check` correctly (per its logic) flagged them — but the flag was a false positive because the modifications were not caused by the executing agent.

---

## Open Questions

1. **Repo root vs project_path divergence:** The git repo root is `/Users/marklehn/Desktop/GitHub/` but `project_path` for bellows plans is `/Users/marklehn/Desktop/GitHub/bellows/`. `git diff --stat` with `cwd=bellows/` shows paths relative to bellows, but operates on the full repo. Files outside the bellows subdirectory (like `LESSONS.md` at repo root, or files in `anvil/`) could appear in the diff if they have unstaged changes, shown as `../LESSONS.md` in the stat output. This is a structural exposure — scope_check cannot distinguish "bellows-local" changes from repo-wide dirty state.

2. **Concurrent-write blindness:** The diff-of-diffs mechanism cannot attribute changes to the agent vs. Bellows itself (e.g., `ledger.jsonl` writes from `_rescan()` main thread, or plan file renames by the orchestration loop). This was documented in the prior diagnostic (`scope-check-infra-files-diagnostic-2026-04-16.md`) and partially mitigated by the prefix allowlist, but remains a design limitation.

3. **No staged-change awareness:** `git diff --stat` only sees unstaged changes. If an agent stages and commits files within a step, those files leave the working tree diff entirely. The diff-of-diffs would then show them as "removed from diff" (present in pre_diff, absent in post_diff), but `_parse_diff_stat` would NOT include them in `changed` because it only captures files present in `post_map` with a different stat line — not files that disappeared. Agent-committed files are invisible to scope_check.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1 (standalone diagnostic)
**Status:** Complete

### What Was Done
Mapped the complete scope_check mechanism: gate location, git invocation, range computation (diff-of-diffs, not git-range), plan-owned-files determination (substring match against step text + static allowlist), call sites, absence of claim-time metadata, absence of caching, and incident validation confirming the 2026-04-19 false positives were from out-of-plan working-tree changes.

### Files Deposited
- `bellows/knowledge/research/scope-check-git-range-2026-04-22.md` — full diagnostic findings

### Files Created or Modified (Code)
- None

### Decisions Made
- None (investigation only, no fixes proposed per diagnostic scope)

### Flags for CEO
- None

### Flags for Next Step
- None (single-step diagnostic)
