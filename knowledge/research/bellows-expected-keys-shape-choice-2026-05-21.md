# SA Findings — bellows expected-keys fix-shape choice

**Date:** 2026-05-21
**Diagnostic:** `diagnostic-bellows-expected-keys-shape-choice-2026-05-21`
**Prior findings (established, not re-derived):** `bellows-expected-keys-warning-2026-05-21.md` Sections 1, 2, 6
**Scope:** read-only investigation of `bellows.py` lines 317-420 + 495-515 + 586-606; grep for `_apply_defensive_header_defaults` across all modules; 10 recent Done plans sampled

---

## 1. `_apply_defensive_header_defaults` — function and call sites

### Function definition (bellows.py:317-326)

```python
# bellows.py:315-326
    return False


def _apply_defensive_header_defaults(header: dict, total_steps: int) -> dict:
    """Apply defensive defaults for sparse multi-step plan headers.

    If header parse returned < 3 keys for a multi-step plan and pause_for_verdict
    is missing, default to after_step_1 (safe-pause). Returns the mutated header.
    """
    if total_steps > 1 and len(header) < 3:
        if not header.get("pause_for_verdict", "").strip():
            header["pause_for_verdict"] = "after_step_1"
    return header
```

**Return contract:** Returns the mutated dict. The function mutates `header` in place AND returns it. The return value is ignored at the only runtime call site (line 381).

### Call site in run_plan (bellows.py:379-383)

```python
# bellows.py:377-384
        # Defensive default (Shape g, BACKLOG 2026-05-10 closure): if header
        # parse looks sparse for a multi-step plan, default to safe-pause
        # rather than auto-advance. Catches future parser-miss classes.
        prev_len = len(header)
        _apply_defensive_header_defaults(header, total_steps)
        if "pause_for_verdict" in header and len(header) > prev_len:
            _log("WARN", f"⚠️ sparse header ({prev_len} keys) for {total_steps}-step plan — defaulting pause_for_verdict to after_step_1 (safe-pause)", slug=slug_for(plan_name))
        model = header.get("Model", header.get("model", config["default_model"]))
```

Return value is discarded — the function's effect is entirely through in-place mutation of the `header` dict.

### Sparse-header warning (bellows.py:382-383)

```python
        if "pause_for_verdict" in header and len(header) > prev_len:
            _log("WARN", f"⚠️ sparse header ({prev_len} keys) for {total_steps}-step plan — defaulting pause_for_verdict to after_step_1 (safe-pause)", slug=slug_for(plan_name))
```

Fires when the defensive default actually inserted the key (dict grew). This is the Case 3 reporter.

### All call sites across the codebase

| File | Line | Context |
|------|------|---------|
| `bellows.py` | 317 | Function definition |
| `bellows.py` | 381 | Single runtime call site in `run_plan()` — return value ignored |
| `tests/test_bellows.py` | 2903 | Test: `result = bellows._apply_defensive_header_defaults(sparse_header, total_steps=2)` — uses return value |
| `tests/test_bellows.py` | 2910 | Test: `result = bellows._apply_defensive_header_defaults(sparse_header, total_steps=3)` — uses return value |

**No calls in:** `gates.py`, `verdict.py`, `parser.py`, `validators.py`, `runner.py`. Confirmed by exhaustive grep of `_apply_defensive_header_defaults` across the entire working tree. Matches outside the above 4 sites are documentation/knowledge files only.

**Shape A impact:** Changing the return type from `dict` to `tuple[dict, bool]` would require updates at 3 sites: bellows.py:381 (destructure), tests/test_bellows.py:2903 (destructure), tests/test_bellows.py:2910 (destructure). The runtime call site at 381 currently ignores the return, so the destructure change is additive.

---

## 2. Four-case dispatch trace

### Critical finding: header reassignment at bellows.py:494

The `header` dict mutated by `_apply_defensive_header_defaults` at line 381 is **not the same header** used for runtime pause decisions. At bellows.py:494:

```python
# bellows.py:494
        header = gate_result.get("plan_header", {})
```

This reassigns `header` to a freshly parsed dict from `gates.check()` (gates.py:165: `header = _parse_plan_header(plan_text)`). The fresh parse does NOT apply `_apply_defensive_header_defaults`. Therefore:

- The header used for `header_says_pause()` at lines 502 and 590 does NOT include the defensive default's `pause_for_verdict = "after_step_1"`.
- The defensive default at line 381 is effective only for: (a) the sparse-header warning at 382-383, (b) the expected-keys warning at 416-419, (c) model extraction at 384.
- **The defensive default is NOT effective for actual pause behavior.** This is a pre-existing issue, out of scope for the warning fix, but relevant to how we evaluate the shapes.

### Downstream pause logic

**While-loop (intermediate steps) — bellows.py:497-502:**
```python
        while not is_final_step(current_step, total_steps):
            if (not gate_result["passed"]
                    or gate_result["is_qa_step"]
                    or gate_result.get("verdict_requested", {}).get("requested", False)
                    or header_says_pause(header, current_step, total_steps, gate_result["is_qa_step"])):
```

Uses `header` from line 494 (re-parsed, no defensive default).

**Final step — bellows.py:587-591:**
```python
        if (not gate_result["passed"]
                or gate_result["is_qa_step"]
                or gate_result.get("verdict_requested", {}).get("requested", False)
                or header_says_pause(header, current_step, total_steps, gate_result["is_qa_step"])
                or not effective_auto_close):
```

Includes `or not effective_auto_close` — since `auto_close` defaults to `"false"`, final step always pauses when `auto_close` is absent.

### Four-case table

| Case | PV present originally? | Header key count | Defensive default fires? | Runtime behavior | Warning emitted today | Desired warning behavior (post-fix) |
|------|----------------------|------------------|------------------------|-----------------|----------------------|-------------------------------------|
| 1 | Yes | ≥ 3 | No (condition not met) | Pauses per PV directive (correct) | May fire for cosmetic missing keys (`author`, `total_steps`, etc.) — noise | No warning needed |
| 2 | Yes | < 3 | No (PV already present) | Pauses per PV directive (correct) | Fires for cosmetic missing keys — noise | No warning needed |
| 3 | No | < 3 | Yes — inserts `after_step_1` | **Intermediate steps auto-advance** (defensive default NOT effective at runtime — see §2 header reassignment). Final step pauses via `not effective_auto_close`. | Sparse-header warning at 382-383 says "safe-pause" (misleading). Expected-keys warning at 416-419 does NOT mention PV (defensive default added it to dict). | Sparse-header warning at 382-383 is sufficient Case 3 reporter. The line-416 warning should not fire (defensive default added PV to the dict used for this check). **Separate fix needed for the runtime ineffectiveness.** |
| 4 | No | ≥ 3 | No (header ≥ 3 keys) | **All intermediate steps auto-advance.** Final step pauses via `not effective_auto_close`. | Fires, mentions PV among cosmetic keys — signal buried in noise | **Must fire.** This is the only case where a targeted PV warning is needed. |

**Key observation for shape choice:** After `_apply_defensive_header_defaults` at line 381, `"pause_for_verdict" not in header` is True if and only if Case 4 applies. In Case 3, the defensive default inserts PV into the dict, so the key IS present. This means a simple `"pause_for_verdict" not in header` check after the defensive default is sufficient to distinguish Case 4 from all other cases — no flag, no snapshot needed.

---

## 3. Shape evaluation

### Shape A — Return flag from `_apply_defensive_header_defaults`

```python
# Modified function
def _apply_defensive_header_defaults(header: dict, total_steps: int) -> tuple:
    fired = False
    if total_steps > 1 and len(header) < 3:
        if not header.get("pause_for_verdict", "").strip():
            header["pause_for_verdict"] = "after_step_1"
            fired = True
    return header, fired

# Modified call site (bellows.py:380-383)
prev_len = len(header)
_, defensive_fired = _apply_defensive_header_defaults(header, total_steps)
if defensive_fired:
    _log("WARN", f"⚠️ sparse header ({prev_len} keys) for {total_steps}-step plan — defaulting pause_for_verdict to after_step_1 (safe-pause)", slug=slug_for(plan_name))

# Modified warning (bellows.py:416-419)
if total_steps > 1 and "pause_for_verdict" not in header and not defensive_fired:
    _log("WARN", f"⚠️ {total_steps}-step plan missing pause_for_verdict — plan will auto-advance without pausing", slug=slug_for(plan_name))
```

**The flag is provably redundant.** After the defensive default fires, `header["pause_for_verdict"]` exists, so `"pause_for_verdict" not in header` is False. The `and not defensive_fired` clause can never be reached when `"pause_for_verdict" not in header` is True — because the only way the flag is True is if PV was inserted into the dict. The conjunct `"pause_for_verdict" not in header AND defensive_fired` is a logical impossibility. The flag adds no distinguishing power.

**Emits warning for Case 4 and only Case 4?** Yes (by tautology — the flag check is unreachable, so the condition reduces to `total_steps > 1 and "pause_for_verdict" not in header`).

**Preserves line 382-383 warning?** Yes — restructures it to use the flag instead of `len(header) > prev_len`, but same behavior.

**LOC delta:** +5 (function signature change, fired variable, tuple return, call site destructure, flag in warning condition).

**Hidden side effects:** Return type changes from `dict` to `tuple`. Tests at test_bellows.py:2903 and 2910 use the return value and would break without destructuring updates.

### Shape B — Capture original_header_keys snapshot

```python
# Call site (bellows.py:379-383)
original_header_keys = set(header.keys())
prev_len = len(header)
_apply_defensive_header_defaults(header, total_steps)
if "pause_for_verdict" in header and len(header) > prev_len:
    _log("WARN", f"⚠️ sparse header ({prev_len} keys) for {total_steps}-step plan — defaulting pause_for_verdict to after_step_1 (safe-pause)", slug=slug_for(plan_name))

# Warning (bellows.py:416-419)
if total_steps > 1 and "pause_for_verdict" not in original_header_keys and "pause_for_verdict" not in header:
    _log("WARN", f"⚠️ {total_steps}-step plan missing pause_for_verdict — plan will auto-advance without pausing", slug=slug_for(plan_name))
```

**The snapshot is also redundant.** `"pause_for_verdict" not in original_header_keys and "pause_for_verdict" not in header` simplifies to `"pause_for_verdict" not in header` — because if PV was absent from the original keys AND the defensive default fired, PV is now IN `header`. The only way PV is absent from BOTH the snapshot and the current dict is if the defensive default didn't fire (Case 4). But `"pause_for_verdict" not in header` alone already captures exactly that case.

**Emits warning for Case 4 and only Case 4?** Yes (snapshot check adds no information).

**Preserves line 382-383 warning?** Yes — unchanged.

**LOC delta:** +2 (snapshot variable, dual-check in warning condition).

**Hidden side effects:** Introduces `original_header_keys` variable that must stay in sync with the header dict. If future code inserts keys between the snapshot and the defensive default call, the snapshot becomes stale. Low risk but non-zero maintenance cost.

### Shape C — Two warnings, consolidated (narrow expected_keys to PV only)

```python
# Warning replacement (bellows.py:416-419)
if total_steps > 1 and "pause_for_verdict" not in header:
    _log("WARN", f"⚠️ {total_steps}-step plan missing pause_for_verdict — plan will auto-advance without pausing at intermediate steps", slug=slug_for(plan_name))
```

Replaces the 4-line expected_keys block (lines 416-419) with a 2-line targeted check. The existing sparse-header warning at 382-383 remains unchanged and covers Case 3 reporting.

**Emits warning for Case 4 and only Case 4?** Yes. After the defensive default at line 381:
- Cases 1, 2: PV in header (original) → condition False → no warning ✓
- Case 3: PV in header (defensive default added it) → condition False → no warning ✓ (sparse-header warning at 382-383 covers)
- Case 4: PV NOT in header → condition True → warning fires ✓

**Preserves line 382-383 warning?** Yes — no changes.

**LOC delta:** -2 net (remove 4 lines: `expected_keys`, `missing_keys`, `if total_steps > 1 and missing_keys:`, long log string; add 2 lines: `if` + log string).

**Hidden side effects:** None. No changes to `_apply_defensive_header_defaults`, no changes to its return type, no new variables, no test breakage. The 2 tests at test_bellows.py:2903 and 2910 call `_apply_defensive_header_defaults` directly and are unaffected.

---

## 4. `_apply_defensive_header_defaults` callers audit

Exhaustive grep across the working tree:

| Module | Occurrences | Notes |
|--------|-------------|-------|
| `bellows.py` | 2 (line 317 def, line 381 call) | Single runtime call site; return ignored |
| `gates.py` | 0 | No reference |
| `verdict.py` | 0 | No reference |
| `parser.py` | File does not exist in this repo | N/A |
| `validators.py` | 0 | No reference |
| `runner.py` | 0 | No reference |
| `tests/test_bellows.py` | 2 (lines 2903, 2910) | Direct calls; use return value |

**Shape A impact assessment:** Changing the return type would require updates at exactly 3 sites: bellows.py:381, test_bellows.py:2903, test_bellows.py:2910. No other module calls the function.

---

## 5. Recent-plan reality check

10 most recently added Done plans (by git commit date, descending):

| # | Plan | Format | Steps | PV present? | Header keys (parsed) | Case |
|---|------|--------|-------|-------------|---------------------|------|
| 1 | executable-priority-3-audit-closeout-2026-05-21 | D (pipe) | 2 | Yes (`after_qa_step`) | ≥ 3 (`date`, `tier`, `dispatch_mode`, `test_scope`, `execution`, `pause_for_verdict`, `priority`, `depends_on`) | **Case 1** |
| 2 | diagnostic-priority-3-carryover-audit-v2-2026-05-21 | D (pipe) | 1 | Yes (`after_step_1`) | ≥ 3 | N/A (single step) |
| 3 | executable-bellows-verdict-enrichment-2026-05-21 | D (pipe) | 2 | Yes (`always`) | ≥ 3 (`date`, `tier`, `dispatch_mode`, `test_scope`, `execution`, `pause_for_verdict`, `auto_close`) | **Case 1** |
| 4 | diagnostic-teardown-git-operations-mapping-2026-05-21 | D (pipe) | 1 | Yes (`always`) | ≥ 3 | N/A (single step) |
| 5 | diagnostic-verdict-enrichment-surface-2026-05-27 | E (bold) | 1 | No | 5 (`project`, `dispatch_mode`, `plan_type`, `date`, `source_roadmap`) | N/A (single step) |
| 6 | diagnostic-deposit-exists-path-form-normalization-2026-05-27 | E (bold) | 1 | No | 4 (`project`, `dispatch_mode`, `plan_type`, `date`) | N/A (single step) |
| 7 | executable-deposit-exists-path-form-normalization-2026-05-27 | E (bold) | 2 | No | ≥ 3 (`project`, `dispatch_mode`, `plan_type`, `date`, `source_diagnostic`, `closes...`, `execution_map`) | **Case 4** |
| 8 | executable-disable-autoupdater-2026-05-27 | E (bold) | 2 | No | ≥ 3 (`project`, `dispatch_mode`, `plan_type`, `date`, `closes_backlog_entry`, `execution_map`) | **Case 4** |
| 9 | diagnostic-planner-authored-contract-validation-2026-05-20 | D (pipe) | 1 | Yes (`after_step_1`) | ≥ 3 | N/A (single step) |
| 10 | executable-planner-contract-validators-three-validator-drop-2026-05-20 | D (pipe) | 2 | Yes (`after_each_step`) | ≥ 3 | **Case 1** |

**Distribution:**
- **Case 1 (safe):** 3 plans (#1, #3, #10) — all Format D (pipe), all have explicit `pause_for_verdict`
- **Case 2 (safe):** 0 plans
- **Case 3 (defensive default fires):** 0 plans
- **Case 4 (dangerous — PV missing, default skipped):** 2 plans (#7, #8) — both Format E (multi-line bold) executables that use `**Execution Map:**` but omit `**pause_for_verdict:**`
- **N/A (single step):** 5 plans — warning doesn't fire regardless

**Pattern:** Format D (pipe) plans consistently include `pause_for_verdict`. Format E (multi-line bold) executables do NOT — they use `**Execution Map:**` and `**Plan Type:**` but omit the PV field. This is a template-version gap: Format E was introduced for the 2026-05-27 batch of plans, and its template didn't include `pause_for_verdict`.

**Case 3 non-occurrence:** Zero plans in the sample have header < 3 keys. All plans have ≥ 4 parsed keys. The defensive default's `len(header) < 3` threshold has never been reached in recent plans. This further confirms that Case 4 (not Case 3) is the real-world dangerous case.

---

## 6. Recommendation — Gap Assessment

| Shape | LOC delta | Reads cleanly? | Hidden side effects? | Covers all 4 cases correctly? | Recommendation |
|-------|-----------|----------------|---------------------|-------------------------------|----------------|
| **A** | +5 | No — the returned flag is provably redundant (see §3); reader must reason about why a flag exists when `"pause_for_verdict" not in header` already captures the same information | Yes — return type change breaks 2 test call sites (test_bellows.py:2903, 2910) | Yes | **Reject** |
| **B** | +2 | No — `original_header_keys` snapshot is redundant for the same reason as Shape A; introduces parallel state that must stay in sync | No (no API changes) but introduces a maintenance-fragile variable | Yes | **Reject** |
| **C** | -2 | Yes — `if total_steps > 1 and "pause_for_verdict" not in header:` is a direct expression of the intent ("warn when PV is missing after defensive defaults have had their chance to inject it") | None — no changes to `_apply_defensive_header_defaults`, no new variables, no test breakage | Yes | **Accept** |

### Recommended Shape: **C**

Shape C is the correct implementation for two reasons grounded in the code trace:

1. **The defensive default's in-place mutation is the discriminator.** After `_apply_defensive_header_defaults` at line 381, PV's presence or absence in `header` already encodes the full Case 3/4 distinction. In Case 3 (sparse header), the default inserts PV → `"pause_for_verdict" in header` is True → warning doesn't fire. In Case 4 (non-sparse header, PV missing), the default doesn't fire → `"pause_for_verdict" not in header` is True → warning fires. Neither a return flag (Shape A) nor a key snapshot (Shape B) adds information that the dict doesn't already contain. Both are provably redundant.

2. **Zero test or API breakage.** Shape C touches only lines 416-419 of `bellows.py` — the warning itself. It does not modify `_apply_defensive_header_defaults`, its return type, or its call convention. The 2 unit tests that call the function directly (test_bellows.py:2903, 2910) are unaffected. Shape A would break both tests; Shape B would not break tests but adds a fragile parallel variable.

### Side-finding (out of scope, flagged for Planner)

The defensive default at bellows.py:381 is **ineffective for actual runtime pause behavior**. At bellows.py:494, `header` is reassigned from `gates.check()` (gates.py:165), which re-parses the plan header WITHOUT applying `_apply_defensive_header_defaults`. The header used by `header_says_pause()` at lines 502 and 590 therefore does NOT contain the defensive default's `pause_for_verdict = "after_step_1"`. In Case 3, intermediate steps auto-advance despite the sparse-header warning claiming "safe-pause." This is a pre-existing issue, separate from the warning-narrowing fix, and should be tracked as a BACKLOG item.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1 (standalone diagnostic)
**Status:** Complete

### What Was Done
Resolved the implementation shape choice for narrowing the expected-keys warning at bellows.py:416-419 to `pause_for_verdict` only. Traced four logical cases through the dispatch path (lines 317-420 + 495-515 + 586-606), evaluated Shapes A/B/C with code sketches and correctness proofs, audited all `_apply_defensive_header_defaults` callers, and grounded the choice in a 10-plan reality check.

### Files Deposited
- `knowledge/research/bellows-expected-keys-shape-choice-2026-05-21.md` — shape choice findings with code-evidence rationale

### Files Created or Modified (Code)
- None (read-only investigation)

### Decisions Made
- Recommended Shape C (two warnings, consolidated) as the implementation shape
- Identified Shapes A and B as provably redundant — the defensive default's in-place dict mutation already encodes the Case 3/4 distinction

### Flags for CEO
- **Side-finding:** Defensive default at bellows.py:381 is ineffective for runtime pause behavior due to header reassignment at line 494. Case 3 plans auto-advance at intermediate steps despite the "safe-pause" warning. Recommend BACKLOG entry.

### Flags for Next Step
- Shape C implementation: replace bellows.py:416-419 (4 lines) with targeted PV check (2 lines). Exact boolean expression: `if total_steps > 1 and "pause_for_verdict" not in header:`
- The existing sparse-header warning at 382-383 covers Case 3 reporting and must be preserved unchanged.
- Existing test `test_warning_multi_step_plan_without_pause_for_verdict` (test_bellows.py) may need assertion update to match the new warning text.
