# Bellows — isinstance(f, dict) Asymmetry Diagnostic Findings
**Date:** 2026-05-21 | **Author:** Bellows Systems Analyst | **Scope:** bellows.py read-only investigation

---

## 1. Block Identification

### Block 1 — bellows.py:505 (in-loop pause-reason)

**Function:** `run_plan()`
**Variable checked:** `f` (each element of `gate_result["failures"]`)
**Loop context:** `all(... for f in gate_result["failures"])` generator inside the `while not is_final_step(current_step, total_steps)` loop
**Next operation dependent on dict-ness:** `f.get("gate")` (safe dict accessor)

```python
# bellows.py:497-514
        while not is_final_step(current_step, total_steps):
            # Check gates: if failed, QA step, verdict-request file, or header says pause
            if (not gate_result["passed"]
                    or gate_result["is_qa_step"]
                    or gate_result.get("verdict_requested", {}).get("requested", False)
                    or header_says_pause(header, current_step, total_steps, gate_result["is_qa_step"])):
                log_path = str(BELLOWS_ROOT / "logs")
                if not gate_result["passed"]:
                    if all(isinstance(f, dict) and f.get("gate") == "rule_22_verification" for f in gate_result["failures"]):
                        _pause_reason = "rule_22_check_failed"
                    else:
                        _pause_reason = "gate_failure"
                elif gate_result["is_qa_step"]:
                    _pause_reason = "qa_checkpoint"
                elif gate_result.get("verdict_requested", {}).get("requested", False):
                    _pause_reason = "agent_verdict_request"
                else:
                    _pause_reason = "header_pause"
```

### Block 2 — bellows.py:594 (post-loop / final-step pause-reason)

**Function:** `run_plan()`
**Variable checked:** `f` (each element of `gate_result["failures"]`)
**Loop context:** `all(... for f in gate_result["failures"])` generator after the while loop exits (final step completed)
**Next operation dependent on dict-ness:** `f["gate"]` (subscript access — will raise `TypeError` on string, `KeyError` on dict-without-key)

```python
# bellows.py:584-605
        # Final step completed — check gates one last time.
        if (not gate_result["passed"]
                or gate_result["is_qa_step"]
                or gate_result.get("verdict_requested", {}).get("requested", False)
                or header_says_pause(header, current_step, total_steps, gate_result["is_qa_step"])
                or not effective_auto_close):
            log_path = str(BELLOWS_ROOT / "logs")
            if not gate_result["passed"]:
                if all(f["gate"] == "rule_22_verification" for f in gate_result["failures"]):
                    _pause_reason = "rule_22_check_failed"
                else:
                    _pause_reason = "gate_failure"
            elif gate_result["is_qa_step"]:
                _pause_reason = "qa_checkpoint"
            elif gate_result.get("verdict_requested", {}).get("requested", False):
                _pause_reason = "agent_verdict_request"
            elif header_says_pause(header, current_step, total_steps, gate_result["is_qa_step"]):
                _pause_reason = "header_pause"
            else:
                _pause_reason = "auto_close_disabled"
```

### Asymmetry summary

| Aspect | Block 1 (line 505) | Block 2 (line 594) |
|---|---|---|
| `isinstance(f, dict)` guard | Yes | **No** |
| Dict access method | `.get("gate")` (safe) | `["gate"]` (subscript, raises on non-dict) |
| Failure mode on non-dict `f` | Silent fallback to `gate_failure` | `TypeError: string indices must be integers` crash |

---

## 2. Upstream Data Flow

### Source A: `gates.check()` return value

Both blocks receive `gate_result` from `gates.check()` (gates.py:148-198). The function initializes `failures = []` at line 164 and passes this list to gate functions. Every gate function appends dict literals with `gate` and `evidence` keys:

| Gate function | Line(s) | Entry format |
|---|---|---|
| `_gate_receipt_status` | gates.py:204 | `{"gate": "receipt_status", "evidence": status}` |
| `_gate_ceo_flags` | gates.py:210 | `{"gate": "ceo_flags", "evidence": "; ".join(flags)}` |
| `_gate_no_errors` | gates.py:215-218 | `{"gate": "no_errors", "evidence": ...}` |
| `_gate_no_permission_denials` | gates.py:241-243 | `{"gate": "no_permission_denials", "evidence": ...}` |
| `_gate_deposit_exists` | gates.py:328, 335, 342 | `{"gate": "deposit_exists", "evidence": ...}` |
| `_gate_rule_20_self_check` | gates.py:426, 435, 442, 461, 465 | `{"gate": "rule_20_self_check", "evidence": ...}` |
| `_gate_rule_22_verification` | gates.py:480-483, 520-528, 536-539 | `{"gate": "rule_22_verification", "evidence": ...}` |
| `_gate_scope_check` | gates.py:580-583 | `{"gate": "scope_check", "evidence": ...}` |

**Count:** 16 distinct append sites in gates.py. All produce dict literals.

### Source B: bellows.py post-gates appends

After `gates.check()` returns, `bellows.py` appends additional failure entries at 5 sites:

| Site | Line | Entry format | Reaches Block 1? | Reaches Block 2? |
|---|---|---|---|---|
| Mode A (pre-loop) | bellows.py:487-490 | `{"gate": "unauthorized_done_move", "evidence": ...}` | Yes (1st iter) | Yes (single-step) |
| Worktree teardown (in-loop) | bellows.py:520 | `{"gate": "worktree_teardown", "evidence": str(e)}` | No (appended after Block 1 checks) | No |
| Mode A (in-loop) | bellows.py:577-580 | `{"gate": "unauthorized_done_move", "evidence": ...}` | Yes (subsequent iters) | Yes (final iter) |
| Worktree teardown (post-loop) | bellows.py:611 | `{"gate": "worktree_teardown", "evidence": str(e)}` | No | No (appended after Block 2 checks) |
| Worktree teardown (auto-close) | bellows.py:639 | `{"gate": "worktree_teardown", "evidence": str(e)}` | No | No (different code path) |

**Count:** 5 append sites in bellows.py. All produce dict literals.

### Source C: Worktree creation failure (early return)

bellows.py:438 constructs `gate_result` directly:
```python
gate_result = {"failures": [{"gate": "worktree_creation", "evidence": str(e)}], ...}
```
This path returns before either block is reached. Not relevant.

### Summary

**Total contributing sites:** 21 (16 in gates.py + 5 in bellows.py). All produce dict entries.

---

## 3. Format Invariants

**Is there ANY upstream site that can produce a non-dict entry reaching Block 1 or Block 2?**

**No.** Every upstream site appends a dict literal with `gate` and `evidence` string keys.

**What enforces the dict invariant?**

**Implicit convention only.** There is:
- No type annotation on the `failures` list (no `list[dict[str, str]]`)
- No assertion or runtime check at the `gates.check()` return site
- No schema validator on `gate_result`
- No TypedDict, dataclass, or namedtuple for failure entries

The invariant is maintained entirely by convention: every contributor appends a `{"gate": ..., "evidence": ...}` literal.

**Historical precedent for breakage:** The BACKLOG closed entry dated 2026-05-03 documents that **plain strings were previously used** as failure entries:
> "Type-mismatch fix at commit `272fbe4` changed `gate_result["failures"]` entries from plain strings to dicts matching `verdict.py::post_verdict_request` contract."

The research file at `knowledge/research/fix-plan-worktree-teardown-type-mismatch-2026-05-03.md` confirms 4 sites in bellows.py originally appended plain strings like `f"worktree_teardown_failed: {e}"`. The convention-only enforcement means this class of bug has already occurred once and could recur.

---

## 4. Defensive-Guard Cost

### Exact diff to symmetrize

```python
# bellows.py:594 — change:
                if all(f["gate"] == "rule_22_verification" for f in gate_result["failures"]):
# to:
                if all(isinstance(f, dict) and f.get("gate") == "rule_22_verification" for f in gate_result["failures"]):
```

**Cost:** 1 line changed. Zero new lines. The change adds `isinstance(f, dict) and ` prefix and changes `f["gate"]` to `f.get("gate")` — identical to Block 1's pattern.

**Anchor line for edit_block:** bellows.py:594, unique string: `if all(f["gate"] == "rule_22_verification" for f in gate_result["failures"]):`

### Would this change observed behavior today?

**No.** All entries reaching Block 2 are dicts today. The guard would only change behavior if a non-dict entry were introduced upstream. In that scenario:
- **Without guard (current):** `TypeError` crash in `run_plan()`, plan left in `in-progress-*` state, no verdict request posted, daemon continues but plan is stranded.
- **With guard (proposed):** Silent fallback to `_pause_reason = "gate_failure"`, verdict request posted normally, plan pauses for CEO review. This is the correct degradation behavior.

### Bug-masking risk assessment

**None.** The guard does not mask bugs — it produces the safer fallback (`gate_failure` pause instead of crash). A non-dict entry reaching this code path would be a contract violation that should be fixed upstream, but the crash vs. graceful-pause distinction matters operationally: a crash strands the plan with no CEO visibility, while a `gate_failure` pause produces a verdict request with full context.

---

## 5. Future-Refactor Risk

### Realistic scenarios that could introduce non-dict entries

1. **New gate function in gates.py appending a string or tuple.** The 16 existing sites establish a strong convention, but a new contributor or a hasty fix could break it. There is no enforcement mechanism.

2. **External data injected into failures.** If a future feature parses failure data from an external source (e.g., CI output, webhook payload) and appends raw entries without normalization, non-dict entries could appear.

3. **Regression during refactoring.** The 2026-05-03 incident demonstrates this exact scenario: a refactoring pass changed failure entry format at some sites but not all.

### In-flight or planned work touching failure entry shape

**BACKLOG open items (2026-05-21):** None of the 5 open items directly modify the `gate_result["failures"]` format. The closest interaction is:
- `pause_for_verdict` unvalidated enum — affects `_pause_reason` assignment downstream of both blocks but does not modify failure entries.
- Deposits parser parenthetical qualifier — affects `_gate_deposit_exists` failure message strings but not entry format.

**Recent commits to bellows.py (since 2026-05-01):**
- `4bd1c84` (2026-05-21): verdict-request enrichment — **this commit introduced both Block 1 and Block 2** in the same change. The asymmetry is an oversight within a single commit, not a deliberate design difference.
- Other recent commits (`2f47b64`, `3671965`, `73b27bd`, `37edd40`, `9e79e4d`) do not modify the failure entry format.

### Risk classification

The risk is **low probability, high impact**: breakage requires a specific type of upstream change (non-dict append), but when it occurs the impact is a `TypeError` crash that strands the plan. The 2026-05-03 precedent demonstrates this failure class is historically real.

---

## 6. Gap Assessment

| Gap | Current State | Proposed State | Change Required | Recommended | Rationale |
|---|---|---|---|---|---|
| (a) Block 2 defensive guard | `f["gate"]` — subscript access, no isinstance check; crashes on non-dict | `isinstance(f, dict) and f.get("gate")` — mirrors Block 1 pattern | 1-line edit at bellows.py:594 | **Yes** | Zero-cost defensive fix; eliminates crash-vs-graceful-pause asymmetry; same commit introduced both blocks so the asymmetry is clearly an oversight |
| (b) Non-dict-producing upstream site | None identified — all 21 sites produce dicts | No change needed | None | **No** | Convention holds today; the isinstance guard is the defense against future breakage, not a response to current breakage |
| (c) Missing type enforcement on failures list | Implicit convention only — no annotation, assertion, or validator | (Optional) Add type annotation `failures: list[dict[str, str]]` at gates.py:164 | 1-line annotation | **Defer** | Low ROI; the isinstance guard at consumption sites is more operationally valuable than a type hint at the production site since Python type hints are not enforced at runtime |
