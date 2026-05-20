# Diagnostic — Bash Gate vs GUARDRAILS.md `rm -f .git/index.lock` Contradiction

**Date:** 2026-05-20 | **Agent:** Bellows Systems Analyst | **Diagnostic:** bash-gate-vs-guardrails | **Step:** 1

---

## Executive Summary

The "Bash gate" that denies `.git/` writes does NOT exist in bellows source code. The denial originates from Claude Code's internal runtime permission system, surfaces to bellows via `permission_denials` in the stream-json result event, and is converted to a `gate_failure` by `gates.py::_gate_no_permission_denials`. Three historical fires of the GUARDRAILS-prescribed `rm -f .git/index.lock` pattern have been documented — all false positives. Neither `git gc --auto` nor `git update-index --refresh` can replace the guardrail's stale-lock recovery, making framing (b) non-viable. **Framing (a) is the recommended path**, implemented as an exemption in `gates.py::_gate_no_permission_denials` for Bash permission denials matching the lock-cleanup pattern.

---

## Q1. Bash Gate Location and Current Logic

### Search Results

Searched all `bellows/*.py` files (`bellows.py`, `runner.py`, `gates.py`, `parser.py`, `verdict.py`, `planner.py`, `notifier.py`, `server.py`, `validators.py`, `decisions.py`) for `.git/` denial logic. **No code in any bellows Python file denies Bash calls touching `.git/`.**

### Dispatch-Time Tool-Permission Scope

The dispatch-time tool permission is set at `runner.py:34`:

```python
allowed_tools: str = "Read,Edit,Write,Bash",
```

Passed to Claude Code at `runner.py:45`:

```python
"--allowedTools", allowed_tools,
```

This **permits** the Bash tool unconditionally. No filtering, no regex, no `.git/` exclusion.

### Where the Denial Actually Originates

The denial originates from **Claude Code's internal runtime permission system**, not bellows code. Per-project `settings.local.json` files contain `Bash(rm:*)` which should match the `rm -f .git/index.lock` pattern (confirmed by `knowledge/research/bash-permission-rules-audit-2026-05-04.md` — all 9 projects have `Bash(rm:*)` in their allow lists). Despite this broad allowlist, Claude Code's runtime still denies the GUARDRAILS-prescribed command — indicating a built-in safety layer within Claude Code that restricts certain `.git/` operations beyond the settings-based allowlist.

### How the Denial Surfaces to Bellows

1. Claude Code denies the Bash command at runtime, recording it in `permission_denials`
2. The denial is included in the stream-json `result` event
3. `parser.py:12` passes it through: `permission_denials = raw.get("permission_denials", [])`
4. `gates.py:177-194` (`_gate_no_permission_denials`) evaluates the denial

Relevant gate code (current, `gates.py:177-194`):

```python
def _gate_no_permission_denials(parsed, failures):
    denials = parsed.get("permission_denials", [])
    blocking = []
    for d in denials:
        if isinstance(d, dict):
            tool_name = d.get("tool_name")
            if tool_name in READ_CLASS_TOOLS:
                continue
            blocking.append(d)
        else:
            # String-form denial (legacy) has no tool_name — default to blocking
            blocking.append(d)
    if blocking:
        first = blocking[0] if isinstance(blocking[0], str) else str(blocking[0])
        failures.append({
            "gate": "no_permission_denials",
            "evidence": f"{len(blocking)} blocking denial(s): {first}",
        })
```

The gate filters read-class tools (`READ_CLASS_TOOLS = {"Grep", "Glob", "Read", "mcp__vexp__run_pipeline"}`) but has **no exemption for Bash commands matching the GUARDRAILS-prescribed lock-cleanup pattern**. Any Bash denial is treated as blocking.

### Key Finding

The diagnostic's premise that the `.git/` denial logic is "a dispatch-time tool-permission scope" in `bellows/*.py` is structurally incorrect — no such code exists in bellows. The denial mechanism is entirely within Claude Code's runtime. Bellows's role is limited to receiving and gating on the denial.

---

## Q2. Frequency of Historical Fires

### Documented Occurrences Against GUARDRAILS-Prescribed `rm -f .git/index.lock` Pattern

| # | Date | Project | Plan | Context | Outcome |
|---|------|---------|------|---------|---------|
| 1 | 2026-04-17 | BrewBuddy | diagnostic-flavornotes-subcategory-not-appearing-2026-04-17 | Compound command: `rm -f .git/index.lock 2>/dev/null; git add ...` | `no_permission_denials` gate failure. BrewBuddy settings may not have had `Bash(rm:*)` at that time. |
| 2 | 2026-05-06 | bellows (governance root) | executable-bellows-backlog-three-reliability-entries-2026-05-06 | Agent attempted `rm` to clear stale `.git/index.lock` at governance root | `no_permission_denials` gate failure. Override authorized. |
| 3 | 2026-05-21 | (Plan A.7) | executable-rule-25-routing-cleanup-2026-05-21, Step 3 | QA agent ran GUARDRAILS-prescribed lock cleanup after completing all substantive work | `no_permission_denials` gate failure. Override authorized. Captured as `shop_backlog.md` entry. |

**Total against GUARDRAILS-prescribed pattern: 3 occurrences.** All false positives — agents following their own guardrails.

### Documented Occurrences Against Other `.git/` Writes

| # | Date | Context | Legitimate Denial? |
|---|------|---------|-------------------|
| (none found) | — | — | — |

**Total against other `.git/` writes: 0 occurrences.** The gate has never fired against a genuinely dangerous `.git/` write.

### Observation

100% of documented `.git/` denial fires are false positives from agents following GUARDRAILS.md. Zero legitimate denials have been observed. The gate provides negative value on this pattern — it blocks correct behavior without catching any incorrect behavior.

---

## Q3. Framing (b) Recovery Viability

### GUARDRAILS.md Verbatim (Lines 49–58)

```markdown
### Git Operations (Mandatory)

Stale git lock files have caused repeated hangs and corrupted index state. All developers must follow these rules:

1. **Before any git command**, remove stale locks: `rm -f .git/index.lock .git/"index "*.lock .git/"index "[0-9]* 2>/dev/null`
2. **Never chain git commands** with `&&`. Run `git add`, `git commit`, `git push` as separate sequential operations. Verify each completes before starting the next.
3. **Always use** `GIT_TERMINAL_PROMPT=0` on `git push` to prevent credential prompt hangs.
4. **If a git command hangs** (>15 seconds): kill it, remove lock files, then retry. Never escalate to plumbing commands (`git write-tree`, `git update-ref`) as a workaround.
5. **Do NOT use `rm -rf`** on any directory — use the specific lock file removal pattern above.
```

### Recovery Scenario the Guardrail Addresses

The guardrail targets **orphaned `.git/index.lock` files left by killed git processes**. When a git process is killed mid-operation (e.g., by bellows's inactivity timeout, by the OS, or by manual intervention), it may leave `.git/index.lock` behind. No process holds the lock, but git refuses to proceed because the lock file exists. The only recovery is to delete the lock file.

This is documented as a real production failure mode: commit `8eac4c3` (2026-05-10) added lock detection to `bellows.py:789-807` specifically to handle this scenario before cherry-pick operations.

### Proposed Replacement 1: `git gc --auto`

- **What it does:** Cleans up loose objects, packs small packs into larger packs, prunes unreachable objects, repacks refs. Runs only if thresholds are exceeded (loose object count, pack count).
- **Does it remove `.git/index.lock`?** **No.** `git gc` does not interact with lock files. It operates on the object store (`.git/objects/`), pack files (`.git/objects/pack/`), and refs (`.git/refs/`, `.git/packed-refs`). The index lock mechanism is orthogonal.
- **Verdict:** Not a functional replacement.

### Proposed Replacement 2: `git update-index --refresh`

- **What it does:** Refreshes the cached stat information for files already tracked in the index. Used to update modification times after file system operations.
- **Does it remove `.git/index.lock`?** **No.** Worse: `git update-index --refresh` will **fail** if `.git/index.lock` exists, because it needs to acquire the index lock to update cached information. The command itself is a victim of the orphaned lock problem, not a solution to it.
- **Verdict:** Not only not a functional replacement — it would itself be blocked by the very condition it's proposed to replace.

### Framing (b) Assessment

**Non-viable.** Neither proposed replacement addresses the failure mode. The only programmatic way to recover from a truly orphaned `.git/index.lock` is to delete it. There is no git plumbing command that does this implicitly. The guardrail's `rm -f` approach is the correct recovery mechanism. Framing (b) would remove a functional recovery without providing an equivalent replacement.

---

## Q4. Framing (a) Gate-Tightening Conflict Surface

### Thread 3 Scope (from `shop_next_session.md`)

Thread 3 modifies `gates.py::_gate_deposit_exists` with ~10 LOC of path normalization (`os.path.realpath` or `os.path.relpath(path, project_path)`) before the `agent_declared` membership check, plus 1 unit test.

### Framing (a) Scope

The fix would modify `gates.py::_gate_no_permission_denials` to exempt Bash permission denials matching the GUARDRAILS-prescribed lock-cleanup pattern. Architecturally parallel to the existing `READ_CLASS_TOOLS` exemption.

### Conflict Analysis

| Dimension | Thread 3 | Framing (a) |
|-----------|----------|-------------|
| File | `gates.py` | `gates.py` |
| Function | `_gate_deposit_exists` (lines 229–261) | `_gate_no_permission_denials` (lines 177–194) |
| Shared logic | None | None |
| Shared data structures | None | None |
| Sequencing constraint | None | None |

**Same file, different functions, no shared logic.** Both changes are additive (adding exemption patterns to existing gates). No conflict surface. Either can ship first without affecting the other. No sequencing constraint.

---

## Gap Assessment

| Gap | Current State | Proposed State | Change Required |
|-----|--------------|----------------|-----------------|
| **Q1: Bash gate location** | No `.git/` denial logic in bellows code. Denial originates from Claude Code's runtime. Surfaces via `parser.py:12` → `gates.py:177` (`_gate_no_permission_denials`). Gate treats all non-read-class Bash denials as blocking. | Gate exempts Bash denials matching the GUARDRAILS-prescribed lock-cleanup pattern from blocking. | Add lock-cleanup pattern exemption to `_gate_no_permission_denials` in `gates.py` (~10 LOC). |
| **Q2: Historical fires** | 3 false-positive fires against GUARDRAILS `rm -f .git/index.lock` pattern (2026-04-17, 2026-05-06, 2026-05-21). 0 fires against other `.git/` writes. 100% false-positive rate on this pattern. | Gate exemption prevents these false positives from producing `gate_failure`. Legitimate `.git/` write denials (if any ever occur) still block. | Same code change as Q1. |
| **Q3: Framing (b) viability** | GUARDRAILS.md prescribes `rm -f .git/index.lock` to handle orphaned lock files from killed processes. | Considered replacing with `git gc --auto` or `git update-index --refresh`. | **No change — framing (b) non-viable.** Neither replacement handles orphaned lock files. `git update-index --refresh` itself fails on the orphaned lock. |
| **Q4: Thread 3 conflict** | Thread 3 modifies `_gate_deposit_exists` in `gates.py`. Framing (a) modifies `_gate_no_permission_denials` in `gates.py`. | Both changes ship. | **No conflict.** Different functions, no shared logic, no sequencing constraint. |

---

## Recommendation

**Framing (a)** — exempt the GUARDRAILS-prescribed lock-cleanup pattern from blocking in `_gate_no_permission_denials`.

**Justification:** Framing (b) is non-viable because neither `git gc --auto` nor `git update-index --refresh` can replace the guardrail's stale-lock recovery — `git update-index --refresh` is itself blocked by the orphaned lock. The guardrail is correct; the gate must accommodate it. The fix is architecturally parallel to the existing `READ_CLASS_TOOLS` exemption: a pattern-based carve-out for denials that are known to be non-harmful. Implementation is ~10 LOC in `gates.py::_gate_no_permission_denials` plus 1-2 unit tests. No conflict with Thread 3 (`_gate_deposit_exists` normalization).

**Implementation note:** Because the `.git/` denial originates from Claude Code's runtime (not bellows code), the fix cannot prevent the denial itself — it can only prevent bellows from converting the denial into a `gate_failure`. Agents will still see a denied tool call in their execution, but the denial will be treated as non-blocking by bellows's gate infrastructure. This matches the `READ_CLASS_TOOLS` precedent: agents see Grep/Glob denials but fall back to bash equivalents, and bellows does not treat these as failures.

---

## Output Receipt

**Agent:** Bellows Systems Analyst
**Step:** 1 (single-step diagnostic)
**Status:** Complete

### What Was Done
Investigated the contradiction between `governance/GUARDRAILS.md` Git Operations section and bellows's gate infrastructure. Searched all `bellows/*.py` files for `.git/` denial logic, audited historical gate fires, evaluated replacement recovery commands, and assessed conflict with in-flight Thread 3 work.

### Files Deposited
- `bellows/knowledge/research/bash-gate-vs-guardrails-diagnostic-2026-05-20.md` — diagnostic findings with Gap Assessment table and recommendation

### Files Created or Modified (Code)
- None — investigation only

### Decisions Made
- Determined that the `.git/` denial logic is NOT in bellows code — it originates from Claude Code's runtime permission system
- Classified framing (b) as non-viable based on functional analysis of proposed replacements
- Confirmed no conflict between framing (a) fix surface and Thread 3 fix surface
- Recommended framing (a) with `_gate_no_permission_denials` exemption pattern

### Flags for CEO
- None

### Flags for Next Step
- The fix plan should NOT exercise the gate change during its own execution (per LESSONS 2026-05-17 recursion-risk pattern). A subsequent canary plan should verify the exemption.
