# Reliability Bugs 1, 2, 3 — Blueprint
**Date:** 2026-04-24 | **Agent:** Bellows Systems Analyst | **Plan:** executable-bellows-reliability-bugs-1-2-3-2026-04-24

---

## Section 1 — Bug 1: `_consume_verdicts` unconditional `shutil.move` to `processed-*`

### Current Code (bellows.py L597-710)

The outer loop at L605 iterates verdict files in `resolved/`. The inner loops at L645-701 search for a matching `verdict-pending-*` plan. The `break` at L701 exits only the innermost `for pname` loop — it does NOT break the `for decisions_path` loop (latent issue: if slugs ever collide across projects, both get processed).

At L708-710:
```python
# Move the verdict file out of resolved to prevent re-processing
processed_path = resolved_dir / f"processed-{fname}"
shutil.move(str(resolved_dir / fname), str(processed_path))
```

This fires **unconditionally** — regardless of whether the inner loop found a match. When no `verdict-pending-*` plan exists (e.g., plan stuck at `in-progress-*` from Bug 2, or plan already in `Done/`), the verdict is consumed without dispatching anything, and future verdict writes for the same step are silently moved to `processed-*` too.

### Confirmed Fix Shape

Add a `plan_matched = False` flag before the inner loop. Set `True` inside the inner loop on successful dispatch (before the `break` at L701). Gate the L708-710 `shutil.move` AND the L703-706 pending-file cleanup on `if plan_matched:`.

Additionally, fix the latent directory-loop break: add `if plan_matched: break` after the `for pname` loop (inside `for decisions_path`) to prevent double-processing across projects.

**Pseudocode:**
```python
plan_matched = False
for decisions_path in search_dirs:                          # L645
    if not os.path.isdir(decisions_path):
        continue
    for pname in os.listdir(decisions_path):                # L648
        if pname.startswith("verdict-pending-") and plan_slug in pname:
            plan_matched = True
            # ... existing processing at L650-700 (unchanged) ...
            break                                            # L701
    if plan_matched:
        break  # NEW: also break directory loop

if plan_matched:
    # Existing L703-710 code — only fires on successful match
    pending_file = BELLOWS_ROOT / "verdicts" / "pending" / f"verdict-request-{plan_slug}-step-{step_number}.md"
    if pending_file.exists():
        pending_file.unlink()
    processed_path = resolved_dir / f"processed-{fname}"
    shutil.move(str(resolved_dir / fname), str(processed_path))
else:
    # No match — check if plan is already in Done/ (stale verdict)
    stale = False
    for decisions_path in search_dirs:
        done_dir = os.path.join(decisions_path, "Done")
        if os.path.isdir(done_dir):
            for dname in os.listdir(done_dir):
                if plan_slug in dname:
                    stale = True
                    break
        if stale:
            break
    if stale:
        processed_path = resolved_dir / f"processed-{fname}"
        shutil.move(str(resolved_dir / fname), str(processed_path))
        print(f"Bellows: ⚠️  stale verdict for {plan_slug} step {step_number} — plan already in Done/, moving to processed")
    else:
        print(f"Bellows: ⚠️  no verdict-pending plan found for {plan_slug} step {step_number} — leaving in resolved/ for retry")
```

### Edge Cases Resolved

**(i) Stale verdicts (plan already in Done/).** When the plan slug matches a file in any `Done/` directory, the verdict is a stale artifact from a completed plan. The fix moves it to `processed-*` with a warning log, preventing infinite retry loops. This handles the scenario where auto-close (or a Planner-owned Done/ move) completed the plan before the verdict was consumed.

**(ii) `resolved/` dir empty or missing.** Current code at L600-601 is already defensive: `if not resolved_dir.is_dir(): return`. No change needed.

**(iii) Inner loop raises exception.** If the inner loop raises before setting `plan_matched = True`, the flag remains False and the verdict stays in `resolved/` — correct behavior, since partial processing should retry.

**(iv) Latent directory-loop break.** The current `break` at L701 only exits the `for pname` loop. Without the directory-loop break, a second matching plan in a different watched project could also get processed. The added `if plan_matched: break` after the `for pname` loop prevents this.

---

## Section 2 — Bug 2: Pause-time rename wrong-path when plan enters at `in-progress-*`

### Current Code (bellows.py L200-202)

```python
plan_dir = str(pathlib.Path(plan_path).parent)          # L200
plan_filename = os.path.basename(plan_path)              # L201
inprogress_path = os.path.join(plan_dir, f"in-progress-{plan_filename}")  # L202
```

When `plan_filename` is `in-progress-executable-foo.md` (resume dispatch via `_consume_verdicts` at L687-690), `inprogress_path` becomes `decisions/in-progress-in-progress-executable-foo.md` — does not exist on disk.

### Bug Impact — 5 Affected Sites

All sites in `run_plan()` that construct filesystem paths from `plan_filename` without prefix-stripping are affected when the plan enters with a lifecycle prefix:

| Line | Code | Result with `in-progress-` prefix |
|------|------|-----------------------------------|
| L202 | `f"in-progress-{plan_filename}"` | `in-progress-in-progress-foo.md` (double prefix) |
| L233 | `os.path.join(plan_dir, "Done", plan_filename)` | `Done/in-progress-foo.md` (wrong name in Done/) |
| L294 | `f"verdict-pending-{plan_filename}"` | `verdict-pending-in-progress-foo.md` (embedded prefix) |
| L352 | `f"verdict-pending-{plan_filename}"` | `verdict-pending-in-progress-foo.md` (embedded prefix) |
| L372 | `os.path.join(done_dir, plan_filename)` | `Done/in-progress-foo.md` (wrong name in Done/) |

Sites that pass `plan_filename` to shadow helpers (L205, L225, L234, L240, L377) are NOT affected — `_shadow_path()` at L90-98 already strips lifecycle prefixes internally.

### Fix Variant Choice: (a) Canonicalize `plan_filename`

**Variant (a)** — introduce `base_filename` with prefix-stripping, matching the existing pattern in `_shadow_path()` at L93-97. This is a **3-line insertion** after L201 that fixes all 5 affected sites.

**Rejected variant (b)** — use `plan_path` directly. While `plan_path` is updated at L223 after the claim, it is NOT the right source for constructing `verdict_pending_path` (which needs the base name with a `verdict-pending-` prefix prepended). Using `plan_path` would require additional manipulation to strip its `in-progress-` prefix before prepending `verdict-pending-`. Variant (a) is cleaner: canonicalize once, use everywhere.

### Confirmed Fix Shape

Insert after L201:
```python
plan_filename = os.path.basename(plan_path)              # L201 (existing)
# Canonicalize: strip lifecycle prefix for path construction
base_filename = plan_filename
for prefix in ("in-progress-", "verdict-pending-", "halted-"):
    if base_filename.startswith(prefix):
        base_filename = base_filename[len(prefix):]
        break
```

Then replace `plan_filename` with `base_filename` at these 5 sites:
- L202: `inprogress_path = os.path.join(plan_dir, f"in-progress-{base_filename}")`
- L233: `shutil.move(plan_path, os.path.join(plan_dir, "Done", base_filename))`
- L294: `verdict_pending_path = os.path.join(plan_dir, f"verdict-pending-{base_filename}")`
- L352: `verdict_pending_path = os.path.join(plan_dir, f"verdict-pending-{base_filename}")`
- L372: `done_path = os.path.join(done_dir, base_filename)`

**No change needed** at:
- L221: `if not plan_filename.startswith("in-progress-"):` — this guard checks the ORIGINAL filename to decide whether to claim; must keep using `plan_filename`
- L205, L225, L234, L240, L377: shadow helpers already handle prefixes via `_shadow_path()`

### Other Call Sites

No other files construct `in-progress-{plan_filename}` or `verdict-pending-{plan_filename}`. The `_consume_verdicts` function at L685-687 constructs `inprogress_name = f"in-progress-{original_name}"` where `original_name` is derived by stripping `verdict-pending-` from `pname` — this is already correct because it starts from a known-prefix file and strips before rebuilding.

---

## Section 3 — Bug 3: `extract_total_steps()` case-sensitive regex

### Current Code (bellows.py L86-87)

```python
def extract_total_steps(plan_text: str) -> int:
    return len(re.findall(r"^## STEP", plan_text, re.MULTILINE))
```

`re.MULTILINE` enables `^` to match at line boundaries but the regex requires uppercase `STEP`. A plan with `## Step 1 — X` yields 0, triggering the skip branch at L230-235 which moves the plan to `Done/` without dispatching.

### Callers (3 total)

| Line | Context | Depends on case-sensitivity? |
|------|---------|------------------------------|
| L212 | `run_plan()` — determines step count for dispatch | No |
| L662 | `_consume_verdicts()` — determines total steps for continue-to-done check | No |
| L668 | `_consume_verdicts()` — same, fallback path | No |

None of these callers depend on the current case-sensitive behavior. All expect a correct count of step headers.

### False-positive risk assessment

The regex `^## STEP` with `re.IGNORECASE` would match `## step`, `## Step`, `## STEP`, etc. at start of line. Potential false positives:
- `## Step-by-step approach` — this would match `## Step` but NOT be followed by a digit. However, `extract_total_steps` counts ANY `## STEP` prefix, not `## STEP \d+`. A section titled `## Step-by-step` would be counted as a step. **Recommendation:** tighten the regex to `r"^## STEP\s+\d+"` with `re.IGNORECASE` to require a step number, eliminating false positives from prose H2 headers.

### Confirmed Fix Shape

```python
def extract_total_steps(plan_text: str) -> int:
    case_insensitive_count = len(re.findall(r"^## STEP\s+\d+", plan_text, re.MULTILINE | re.IGNORECASE))
    case_sensitive_count = len(re.findall(r"^## STEP\s+\d+", plan_text, re.MULTILINE))
    if case_insensitive_count > 0 and case_sensitive_count == 0:
        print(f"Bellows: ⚠️  WARNING: plan has step headers but case does not match expected '## STEP N' — count={case_insensitive_count} matched case-insensitively")
    return case_insensitive_count
```

This provides:
1. Correct counting of mixed-case plans (`re.IGNORECASE`)
2. Tightened regex requiring a step number (`\s+\d+`) to avoid false positives from prose headers
3. Warning when exact case doesn't match — loud-fail visibility for authoring errors

### Skip-branch impact

The skip branch at L230-235 fires when `total_steps == 0`. After the fix, a plan with `## Step 1 — X` would correctly yield `total_steps = 1` (with a warning), and the skip branch would NOT fire. This is the intended behavior.

---

## Section 4 — Unit Test Enumeration

### Bug 1 Tests

| # | Test Name | What It Verifies | Expected Result |
|---|-----------|------------------|-----------------|
| 1 | `test_consume_verdicts_no_match_leaves_in_resolved` | Verdict whose slug matches no `verdict-pending-*` plan stays in `resolved/`, NOT moved to `processed-*` | Verdict file remains in `resolved/` |
| 2 | `test_consume_verdicts_stale_verdict_plan_in_done_moves_to_processed` | Verdict whose slug matches a plan in `Done/` is moved to `processed-*` with stale-verdict handling | Verdict file moved to `processed-*` |
| 3 | `test_consume_verdicts_match_still_moves_to_processed` | Existing behavior preserved: verdict with matching `verdict-pending-*` plan is processed normally | Verdict file moved to `processed-*` (regression guard) |

### Bug 2 Tests

| # | Test Name | What It Verifies | Expected Result |
|---|-----------|------------------|-----------------|
| 4 | `test_run_plan_inprogress_entry_renames_to_verdict_pending` | Plan entering `run_plan()` with `in-progress-` prefix correctly renames to `verdict-pending-{base_name}` on pause | File renamed to `verdict-pending-executable-foo.md`, NOT `verdict-pending-in-progress-executable-foo.md` |
| 5 | `test_run_plan_inprogress_entry_no_double_prefix` | Confirm `inprogress_path` does NOT have double `in-progress-in-progress-` prefix | `inprogress_path` equals `decisions/in-progress-executable-foo.md` |

### Bug 3 Tests

| # | Test Name | What It Verifies | Expected Result |
|---|-----------|------------------|-----------------|
| 6 | `test_extract_total_steps_mixed_case` | `## Step 1 — X` counted correctly | Returns 1 |
| 7 | `test_extract_total_steps_lowercase` | `## step 1 — X` counted correctly | Returns 1 |
| 8 | `test_extract_total_steps_uppercase_unchanged` | `## STEP 1 — X` still works (regression guard) | Returns 1 |
| 9 | `test_extract_total_steps_requires_number` | `## Step-by-step approach` does NOT count as a step | Returns 0 |
| 10 | `test_extract_total_steps_case_mismatch_warning` | Warning fires when exact case doesn't match (capsys capture) | Warning printed to stdout |

**Net test delta:** +10 new tests, 0 existing tests changed.

---

## Section 5 — Interaction Matrix

| Fix | Bug 1 alone | Bug 2 alone | Bug 1 + 2 combined |
|-----|-------------|-------------|---------------------|
| **Bug 1** (plan_matched gate) | Verdicts without matching `verdict-pending-*` stay in `resolved/` for retry. Plan stuck at `in-progress-*` retries until manually unstuck or Bug 2 is also fixed. **Improvement over status quo** (verdict no longer consumed on mismatch). | N/A | Verdicts retry until Bug 2 fix allows the `in-progress-*` → `verdict-pending-*` rename to succeed; then match is found and verdict processes normally. **Full resolution.** |
| **Bug 2** (canonical filename) | N/A | Rename from `in-progress-*` to `verdict-pending-*` succeeds, so `_consume_verdicts` finds the match. Bug 1 unconditional move is not triggered because match succeeds. **Full resolution for the common case**, but a race condition or edge case that still prevents matching would silently consume the verdict. | Defense-in-depth: Bug 2 prevents the mismatch; Bug 1 catches any remaining edge cases. **Most robust.** |
| **Bug 3** (case-insensitive) | Independent — affects plan parsing, not pause/verdict lifecycle | Independent | Independent |

**Recommendation:** Ship all three in one commit. Bugs 1 and 2 are tightly coupled (Bug 2 is the most common trigger for Bug 1's failure mode). Bug 3 is independent but trivial to include. No regression risk from shipping together — each fix targets a distinct code path.

---

## Section 6 — Restart Requirement

All three fixes modify `bellows.py`. The running Bellows daemon holds pre-fix code in memory. **A Bellows daemon restart is required after commit to load the fixes.** This is the standard Bellows deployment model — Python import semantics mean the running process uses the module state from startup.

---

## Layer Impact

| Finding | Layer 1 (Bellows) | Layer 2 (Agents) | Layer 3 (Planner) |
|---------|-------------------|-------------------|--------------------|
| Bug 1: unconditional processed-move | **Root cause** — `_consume_verdicts` moves verdict before confirming dispatch | Not affected | Affected — produces silent verdict consumption requiring manual recovery |
| Bug 2: double-prefix rename | **Root cause** — `plan_filename` not canonicalized before path construction | Not affected | Affected — plan orphans at `in-progress-*` blocking verdict cycle |
| Bug 3: case-sensitive regex | **Root cause** — `extract_total_steps` uses case-sensitive `^## STEP` | Not affected (agents receive bootstrap prompt regardless) | Affected — mixed-case plans silently move to Done/ without execution |

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Traced all three reliability bugs against live code in `bellows.py`, confirmed each CEO-specified fix shape, identified 5 affected path-construction sites for Bug 2 (not just the 2 pause branches), tightened Bug 3's regex to require a step number (prevents false positives from prose H2 headers), resolved Bug 1's stale-verdict edge case with a Done/ directory check, and enumerated 10 unit tests for DEV to implement.

### Files Deposited
- `knowledge/architecture/reliability-bugs-1-2-3-blueprint-2026-04-24.md` — this blueprint

### Files Created or Modified (Code)
- None (blueprint only)

### Decisions Made
- Bug 2 fix variant: chose (a) canonicalize `plan_filename` via `base_filename` over (b) use `plan_path` directly. Reason: `plan_path` is the wrong source for constructing `verdict_pending_path` (would need additional prefix manipulation); `base_filename` follows the existing pattern in `_shadow_path()` and fixes all 5 affected sites with one canonical variable.
- Bug 1 stale-verdict handling: chose Done/ directory check over `orphaned/` subdirectory. Reason: stale verdicts are a known state (plan completed via another path), not an error state. Moving to `processed-*` with a warning log is consistent with the existing processed-verdict convention. An `orphaned/` directory would create a new lifecycle state with no consumer.
- Bug 3 regex tightening: added `\s+\d+` to require a step number after `## STEP`. Without this, a prose H2 like `## Step-by-step approach` would be falsely counted as a step header.

### Flags for CEO
- None

### Flags for Next Step
- DEV should implement all three fixes in a single commit per Section 5's recommendation
- Bug 2 has 5 affected sites (Section 2 table), not just the 2 pause branches — DEV must update all 5
- All 10 tests enumerated in Section 4 should be implemented; the capsys warning test (#10) requires `capsys` or stdout capture
- Restart Bellows daemon after commit — mandatory per Section 6
