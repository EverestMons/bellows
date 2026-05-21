# deposit_exists Path-Form Normalization — Diagnostic Findings

**Date:** 2026-05-27 | **Type:** Diagnostic findings | **Plan:** diagnostic-deposit-exists-path-form-normalization-2026-05-27

---

## Prior Work (cited per Rule 27)

- **gate-path-resolution-post-teardown-2026-05-10.md (RC1):** Confirmed gates.check() runs BEFORE _teardown_worktree. Root Cause 1 was missing `wt_path` threading in `_gate_rule_20_self_check` (fixed). Root Cause 2 was legacy prose regex capturing unresolvable short paths (governance fix). Established the ordering: gates at bellows.py:333, teardown at bellows.py:362 (line numbers since shifted).
- **deposit-exists-false-positive-audit-2026-05-11.md (Cause 5):** Identified plan-agent evidence path convention mismatch as a distinct failure class (18 failure lines). Recommended Planner-side fix (full project-relative paths in Deposits blocks). Confirmed Cause 4 (normalization/case) ruled out for that population.

The 2026-05-23 reproductions are **mechanistically distinct** from both prior root causes. Even when `_resolve_deposit_path` is passed `wt_path` and the worktree is alive, the gate fails because: (a) the `agent_declared` membership check uses raw string comparison on paths of different forms (absolute vs relative), and (b) `_resolve_deposit_path` cannot remap absolute paths to the worktree because `os.path.join(wt_path, absolute_path)` returns `absolute_path` unchanged when the second argument starts with `/`.

---

## Q1 — `_gate_deposit_exists` Path Comparison Mechanism

### `agent_declared` construction (gates.py:250–265)

Parses the `### Files Deposited` section from `parsed["result_text"]`:

```python
agent_declared = set()
if match:
    section = match.group(1)
    for line in section.splitlines():
        line = line.strip()
        if not line or not line.startswith("- "):
            continue
        m = re.match(r'`([^`]+)`', line[2:].strip())
        path = m.group(1) if m else line[2:].strip().strip("`")
        if path:
            agent_declared.add(path)         # ← raw string, no normalization
```

Paths are added as raw strings extracted from backtick-quoted bullets. No `os.path.normpath`, `os.path.abspath`, or any other form normalization. The set contains whatever the agent wrote in its Output Receipt.

### Plan-required path extraction (gates.py:267–279)

Two sources, tried in order:

1. **Frontmatter deposits** (line 268–272): `plan_header.get("deposits")` — used when plan has YAML frontmatter with a `deposits` list. The config-split plan uses bold-Markdown header, not YAML, so this path is not taken.

2. **Prose fallback** (lines 273–279): `_extract_plan_required_deposits(step_text)` — extracts backtick-quoted paths from the `**Deposits:**` block (lines 311–320):

```python
block_match = re.search(r'[> ]*\*\*Deposits:\*\*\s*\n(?:[> ]*\n)*((?:[> ]*-\s+.*\n?)+)', step_text)
if block_match:
    block_text = block_match.group(1)
    paths = set()
    for m in re.finditer(r'-\s+`([^`]+)`', block_text):
        paths.add(m.group(1))    # ← raw string, no normalization
    return _filter_transient_paths(paths)
```

Again, raw literal strings. Whatever is between backticks in the plan is returned verbatim.

### The comparison (gates.py:278)

```python
for path in _extract_plan_required_deposits(step_text):
    if path not in agent_declared and _resolve_deposit_path(path, project_path, wt_path=wt_path) is None:
        failures.append({"gate": "deposit_exists", "evidence": f"plan-required deposit missing (not declared by agent): {path}"})
```

**This is a plain Python `set` membership check** (`path not in agent_declared`) — hash-based string equality. No `os.path.samefile`, no `pathlib.Path.resolve()` equality, no `os.path.realpath`, no `os.path.normpath`. Two strings representing the same filesystem path in different forms will not match.

The same pattern applies at line 271 for frontmatter deposits.

### `_resolve_deposit_path` behavior with absolute paths (gates.py:216–245)

When the plan-required path is absolute and the `agent_declared` check fails (string mismatch), the gate falls through to `_resolve_deposit_path`. For an absolute path like `/Users/marklehn/Developer/GitHub/bellows/knowledge/architecture/config-split-design-2026-05-23.md`:

| Strategy | Code | Result |
|----------|------|--------|
| 0 (worktree-first) | `os.path.join(wt_path, path)` | Returns `path` unchanged — `os.path.join` returns the second arg when it's absolute. Checks main-repo path, not worktree. **File not there.** |
| 1 (as-is) | `os.path.isfile(path)` | Checks main-repo absolute path. New file only in worktree. **Not found.** |
| 2 (project-relative) | `os.path.join(project_path, path)` | Returns `path` (absolute second arg). Same as Strategy 1. **Not found.** |
| 3 (parent-relative) | `os.path.join(dirname(project_path), path)` | Returns `path` (absolute second arg). Same as Strategy 1. **Not found.** |

**All four strategies collapse to the same check** when the input path is absolute. Strategy 0's worktree remapping only works for relative paths (specifically those starting with `project_basename + os.sep`). Absolute paths completely bypass worktree-first resolution.

---

## Q2 — Empirical Audit of 2026-05-23 Reproductions

### Source data

- Plan: `knowledge/decisions/Done/executable-bellows-config-split-2026-05-23.md`
- Verdicts: `verdicts/resolved/processed-verdict-bellows-config-split-2026-05-23-step-{1,2,3}.md`

### Plan `**Deposits:**` block paths (verbatim from plan)

**Step 1 (SA):**
- `` `/Users/marklehn/Developer/GitHub/bellows/knowledge/architecture/config-split-design-2026-05-23.md` ``

**Step 2 (DEV):**
- `` `/Users/marklehn/Developer/GitHub/bellows/knowledge/dev-logs/config-split-dev-2026-05-23.md` ``
- `` `/Users/marklehn/Developer/GitHub/bellows/bellows.py` `` (modified)
- `` `/Users/marklehn/Developer/GitHub/bellows/scripts/migrate_config.py` `` (new)
- `` `/Users/marklehn/Developer/GitHub/bellows/tests/test_bellows.py` `` (modified)
- `` `/Users/marklehn/Developer/GitHub/bellows/.gitignore` `` (modified)
- `` `/Users/marklehn/Developer/GitHub/.gitignore` `` (modified)

**Step 3 (QA):**
- `` `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/config-split-qa-2026-05-23.md` ``
- `` `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/config-split-2026-05-23/` `` (directory)

### Agent-declared paths (extracted from verdict narratives)

**Step 1:** Relative form in receipt (verdict: "the agent declared the same file as a relative path in its receipt").

**Step 2:** `bellows/knowledge/dev-logs/config-split-dev-2026-05-23.md` and `bellows/scripts/migrate_config.py` (verdict: "DEV declared ... as relative paths in Files Deposited").

**Step 3:** Relative forms (verdict: "same path-form mismatch ... as Steps 1 and 2").

### Comparison table

| Step | Plan-declared path | Agent-declared path (inferred) | Gate-reported missing path | Form mismatch type |
|------|-------------------|-------------------------------|--------------------------|-------------------|
| 1 | `/Users/.../bellows/knowledge/architecture/config-split-design-2026-05-23.md` | `bellows/knowledge/architecture/config-split-design-2026-05-23.md` | `plan-required deposit missing (not declared by agent): /Users/.../bellows/knowledge/architecture/config-split-design-2026-05-23.md` | **abs-vs-rel** |
| 2 | `/Users/.../bellows/knowledge/dev-logs/config-split-dev-2026-05-23.md` | `bellows/knowledge/dev-logs/config-split-dev-2026-05-23.md` | `plan-required deposit missing (not declared by agent): /Users/.../bellows/knowledge/dev-logs/config-split-dev-2026-05-23.md` | **abs-vs-rel** |
| 2 | `/Users/.../bellows/scripts/migrate_config.py` | `bellows/scripts/migrate_config.py` | `plan-required deposit missing (not declared by agent): /Users/.../bellows/scripts/migrate_config.py` | **abs-vs-rel** |
| 3 | `/Users/.../bellows/knowledge/qa/config-split-qa-2026-05-23.md` | `bellows/knowledge/qa/config-split-qa-2026-05-23.md` | `plan-required deposit missing (not declared by agent): /Users/.../bellows/knowledge/qa/config-split-qa-2026-05-23.md` | **abs-vs-rel** |
| 3 | (same path as above) | (same) | `rule_20_self_check: deposit file unreadable: ... (file not found)` | **abs-vs-rel** (downstream symptom) |

**Notes on Step 2 modified-file deposits:** Plan-declared deposits for `bellows.py`, `test_bellows.py`, `.gitignore`, and parent `.gitignore` are existing files. Even in absolute form, `_resolve_deposit_path` Strategy 1 finds them at the main-repo path (the pre-edit version exists). These did NOT fail the gate. Only new files (dev-log, migrate_config.py) failed.

### Form mismatch type

All 2026-05-23 reproductions are a single type: **abs-vs-rel**. The plan's `**Deposits:**` block uses absolute paths (starting with `/Users/marklehn/Developer/GitHub/`). Agents declare project-prefixed relative paths (starting with `bellows/`). The raw string comparison fails. The `_resolve_deposit_path` fallback also fails because absolute paths bypass worktree-first resolution (Strategy 0's `os.path.join` returns the absolute second argument unchanged).

No instances of: project-prefix-included-vs-stripped, trailing-slash, symlink-vs-target, case sensitivity, or OS-path-separator mismatches.

---

## Q3 — Order of Operations Confirmation

The 2026-05-10 finding still holds. Current line numbers:

| Order | Operation | Line(s) | Code |
|-------|-----------|---------|------|
| 1 | Pre-step diff capture | 448 | `pre_diff = _capture_git_diff(wt_path)` |
| 2 | Agent process runs and exits | 450 | `parsed = runner.run_step(...)` |
| 3 | Record run | 459 | `record_run(...)` |
| 4 | Mode A detection check | 465–480 | `if not os.path.exists(inprogress_path): ...` |
| 5 | Post-step diff capture | 483 | `post_diff = _capture_git_diff(wt_path)` |
| 6 | File change parsing | 484 | `files_changed = _parse_diff_stat(...)` |
| 7 | **gates.check()** | **485** | `gate_result = gates.check(parsed, plan_text, current_step, project_path, files_changed=files_changed, wt_path=wt_path)` |
| 8 | Pause condition evaluation | 497–502 | `if (not gate_result["passed"] or ...)` |
| 9 | **_teardown_worktree** | **514** | `_teardown_worktree(project_path, wt_path, plan_slug)` |

The same ordering applies for the multi-step loop (gates at line 572, teardown at line 602) and the final-step path (teardown at line 602 or 628).

**Confirmed:** `gates.check()` runs BEFORE `_teardown_worktree` in all code paths. Line numbers shifted +~150 lines since the 2026-05-10 diagnostic due to intervening code additions, but the structural ordering is unchanged.

---

## Q4 — Gate-vs-Teardown Race Investigation

### Call chain between agent completion and gate evaluation

Between `runner.run_step()` returning (line 450) and `gates.check()` (line 485):

1. **`record_run()`** (line 459) — writes to `bellows.db` via sqlite3. No worktree I/O.
2. **Mode A detection** (lines 465–480) — checks whether the plan file was moved to Done/. Reads/moves files in `knowledge/decisions/`, never touches deposit files in the worktree.
3. **`_capture_git_diff(wt_path)`** (line 483) — runs `git --no-pager diff --stat --relative -- .` with `cwd=project_path`. This is read-only: `git diff --stat` reports changes without modifying the index or working tree. No file mutations.
4. **`_parse_diff_stat()`** (line 484) — pure string parsing of the diff output. No I/O.

**No code path between agent completion and `_gate_deposit_exists` mutates the worktree.** No subprocess refreshes the git index in a destructive way. No sweep touches deposit files. No rename, removal, or modification of deposits occurs.

### Conclusion

**(a) No race exists.** The path-form mismatch alone explains all 3 reproductions. The worktree is intact and unmutated when gates.check() runs. Strategy 0 in `_resolve_deposit_path` WOULD find the files — if it could remap absolute paths to the worktree. The gap is that Strategy 0's `os.path.join(wt_path, absolute_path)` returns `absolute_path` unchanged when the second argument is absolute, so it checks the main-repo path instead of the worktree path.

The Planner's verdict narrative for Step 2 ("Worktree was torn down by gate-check time") is incorrect. This is the same timing misconception the 2026-05-10 diagnostic corrected. The worktree is alive at gate time; the issue is that absolute paths defeat Strategy 0's join-based remapping.

---

## Q5 — Fix-Shape Recommendation

### Recommended: (a) Pure normalization

The bug has two components, both addressable by normalization without any order-of-operations change:

**Component 1 — `agent_declared` membership check (primary).** The `path not in agent_declared` check at lines 271 and 278 is raw string comparison. When the plan uses absolute paths and the agent uses project-prefixed relative paths, the strings never match.

**Component 2 — `_resolve_deposit_path` absolute-path blindness (secondary).** When the membership check fails, the fallback `_resolve_deposit_path` also fails because `os.path.join(wt_path, absolute_path)` returns `absolute_path` unchanged, bypassing Strategy 0's worktree remapping.

### Normalization function

Add a `_normalize_deposit_path(path, project_path)` helper that reduces any path form to a canonical project-relative form:

```python
def _normalize_deposit_path(path, project_path):
    """Normalize deposit path to project-relative form for comparison.

    Handles three input forms:
      - Absolute:           /Users/.../bellows/knowledge/foo.md  → knowledge/foo.md
      - Project-prefixed:   bellows/knowledge/foo.md             → knowledge/foo.md
      - Project-relative:   knowledge/foo.md                     → knowledge/foo.md (unchanged)
    """
    abs_project = os.path.abspath(project_path)
    if os.path.isabs(path):
        prefix = abs_project + os.sep
        if path.startswith(prefix):
            return path[len(prefix):]
        parent_prefix = os.path.dirname(abs_project) + os.sep
        if path.startswith(parent_prefix):
            return path[len(parent_prefix):]
    project_basename = os.path.basename(abs_project)
    if path.startswith(project_basename + os.sep):
        return path[len(project_basename) + 1:]
    return path
```

### Call sites to change

| # | Location | Change |
|---|----------|--------|
| 1 | `_normalize_deposit_path` | New function (~15 LOC) |
| 2 | `_gate_deposit_exists` line 263 | Normalize when adding to `agent_declared`: `agent_declared.add(_normalize_deposit_path(path, project_path))` |
| 3 | `_gate_deposit_exists` line 271 | Normalize frontmatter path before membership check |
| 4 | `_gate_deposit_exists` line 278 | Normalize plan-required path before membership check |
| 5 | `_resolve_deposit_path` Strategy 0 | Add absolute-path-to-worktree remapping: if `os.path.isabs(path)` and path starts with `project_path`, strip prefix and resolve against `wt_path` |

### Tests to add

| Test | Type | Description |
|------|------|-------------|
| `test_normalize_deposit_path_abs_to_rel` | Positive | Absolute path → project-relative |
| `test_normalize_deposit_path_prefixed_to_rel` | Positive | Project-prefixed relative → project-relative |
| `test_normalize_deposit_path_already_rel` | Positive | Already project-relative → unchanged |
| `test_gate_deposit_exists_cross_form_abs_vs_rel` | Positive | Plan declares absolute, agent declares relative — gate passes |
| `test_gate_deposit_exists_actually_missing` | Negative | File genuinely missing — gate still fails |
| `test_resolve_deposit_path_absolute_worktree_remap` | Positive | Absolute path remapped to worktree finds file |

### LOC estimate

| Category | LOC |
|----------|-----|
| `_normalize_deposit_path` function | ~15 |
| `_gate_deposit_exists` modifications | ~5 |
| `_resolve_deposit_path` Strategy 0 addition | ~5 |
| **Production total** | **~25** |
| Unit tests | ~50 |
| **Overall total** | **~75** |

### Why not (b) or (c)

**(b) normalization + order-of-operations change:** The order of operations is already correct (gates before teardown). No change needed. The 2026-05-10 diagnostic confirmed this, and Q3 above re-confirms with current line numbers.

**(c) broader restructure:** Not needed. The bug is localized to two specific gaps: a missing normalization step in the membership check, and a missing absolute-path handler in Strategy 0. Both are additive changes with no structural implications.

---

## Q6 — Authoring Guidance for the Fix Plan

### What form does `_extract_plan_required_deposits` return?

It returns the **literal string** between backticks in the `**Deposits:**` block. No normalization is applied. The form is entirely determined by how the Planner writes the block.

### What form do agents typically declare in their Output Receipts?

Agents declare **project-prefixed relative paths** (e.g., `bellows/knowledge/research/file.md`). This is the convention established by the specialist template's `### Files Deposited` section — agents write paths relative to their working context, which in a worktree is project-relative with the project name prefix.

### Canonical form for the fix plan's `**Deposits:**` block

The fix plan **MUST use project-prefixed relative paths** in its `**Deposits:**` block — the same form agents declare in their receipts. Example:

```markdown
**Deposits:**
- `bellows/gates.py` (modified)
- `bellows/tests/test_gates.py` (modified)
```

**NOT** absolute paths like:
```markdown
**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/gates.py`
```

### Rationale

The fix plan executes on the CURRENT (pre-fix) code. The current `_gate_deposit_exists` performs raw string comparison between plan-declared paths and agent-declared paths. If the plan uses absolute paths and the agent declares relative paths, the fix plan trips the very bug it's fixing (the recursion-risk constraint from LESSONS 2026-05-19).

By using project-prefixed relative paths (`bellows/...`), the plan's declared paths match the form agents use in their Output Receipts. The raw string comparison succeeds, and the gate passes.

### Additional guidance

- The fix plan MUST NOT use bare project-relative paths without the project prefix (e.g., `knowledge/research/...`) — agents include the `bellows/` prefix, so omitting it creates a different form mismatch.
- For modified existing files that are listed in `**Deposits:**` (e.g., `bellows/gates.py`), the gate's `_resolve_deposit_path` will find them even if the membership check fails (the file exists at the main-repo path). The recursion risk applies only to **new files** that don't yet exist in the main repo.

---

## Root Cause Summary

**Single root cause with two components:**

### Component A — Missing normalization in `agent_declared` membership check (gates.py:271, 278)

The `path not in agent_declared` check compares raw strings from two independent sources that use different path conventions:
- Plan `**Deposits:**` block: may use absolute paths (`/Users/.../bellows/...`)
- Agent `### Files Deposited`: uses project-prefixed relative paths (`bellows/...`)

These strings represent the same file but are never equal under raw comparison. No normalization is applied at any point in the comparison chain.

### Component B — `_resolve_deposit_path` cannot remap absolute paths to worktree (gates.py:228–235)

When the membership check fails (Component A), the fallback `_resolve_deposit_path` also fails for new files because:
- Strategy 0 uses `os.path.join(wt_path, path)`, which returns `path` unchanged when `path` is absolute
- Strategies 1–3 all collapse to `os.path.isfile(path)` for absolute paths, checking the main-repo location where new files don't exist yet (they're only in the worktree)

### Distinction from prior root causes

| Root cause | First identified | Mechanism | Status |
|-----------|-----------------|-----------|--------|
| RC1: missing `wt_path` in `_gate_rule_20_self_check` | 2026-05-10 | Gate function lacked worktree parameter | Fixed (gates.py:151, 351) |
| RC2: legacy prose regex captures unresolvable short paths | 2026-05-11 | `evidence/foo.txt` extracted from prose, no such path on disk | Governance fix (Rule 26 adoption) |
| **RC3: abs-vs-rel form mismatch in `agent_declared` check** | **2026-05-27 (this diagnostic)** | Plan uses absolute paths, agent uses relative; raw string comparison fails; `_resolve_deposit_path` can't bridge absolute paths to worktree | **Open — fix recommended** |

---

## Confidence

**HIGH.** The mechanism is fully traceable in source code:
1. The plan file contains absolute paths in `**Deposits:**` blocks — verified verbatim in `executable-bellows-config-split-2026-05-23.md`.
2. The verdict narratives explicitly identify the agent-relative vs plan-absolute mismatch for all 3 steps.
3. The `_gate_deposit_exists` comparison is raw string membership (`path not in agent_declared`) — no normalization at lines 271 or 278.
4. `_resolve_deposit_path` Strategy 0's `os.path.join(wt_path, abs_path)` returns `abs_path` unchanged — Python `os.path.join` semantics are deterministic.
5. Order of operations confirmed: gates run pre-teardown (line 485 before line 514), so the worktree is alive. The failure is not timing — it's form normalization.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1 (diagnostic, single-step)
**Status:** Complete

### What Was Done
Investigated the path-form normalization gap in `_gate_deposit_exists` that produced three Planner overrides on the 2026-05-23 config-split plan. Identified the root cause as a missing normalization step in the `agent_declared` membership check combined with `_resolve_deposit_path`'s inability to remap absolute paths to the worktree. Produced a fix-shape recommendation (pure normalization, ~25 LOC production + ~50 LOC test) and authoring guidance for the fix plan.

### Files Deposited
- `bellows/knowledge/research/deposit-exists-path-form-normalization-2026-05-27.md` — this diagnostic findings file
- `bellows/knowledge/research/agent-prompt-feedback.md` — appended dated entry per standard protocol

### Files Created or Modified (Code)
- None (read-only diagnostic)

### Decisions Made
- Fix shape is (a) pure normalization — no order-of-operations change needed
- Canonical path form for fix plan authoring is project-prefixed relative (`bellows/...`)

### Flags for CEO
- None

### Flags for Next Step
- The fix plan must use project-prefixed relative paths in its `**Deposits:**` block (see Q6)
- The normalization function must handle three forms: absolute, project-prefixed relative, and bare project-relative
- Test coverage must include both positive (cross-form equivalence) and negative (actually-missing file still fails)
