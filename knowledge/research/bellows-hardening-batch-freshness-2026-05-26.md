# Bellows Hardening Batch — Freshness & Disposition Audit
**Date:** 2026-05-26 | **Agent:** Bellows Systems Analyst | **Step:** 1 (SA) | **Plan:** diagnostic-bellows-hardening-batch-freshness-2026-05-26

---

## Gap Assessment Table

| Item | BACKLOG Claim | Current State (verbatim line + quote) | Status | Recommended Disposition |
|------|--------------|---------------------------------------|--------|------------------------|
| **1** — `_gate_rule_20_self_check` ambiguous evidence string | BACKLOG claims `gates.py:441` (`if not md_paths`) and `gates.py:464` (`if banner not in content`) both emit the same evidence string `"no QA deposit contains Rule 20 self-check banner"`. | **gates.py:441:** `failures.append({"gate": "rule_20_self_check", "evidence": "no QA deposit contains Rule 20 self-check banner"})` (branch: no `.md` paths in deposits). **gates.py:464:** `failures.append({"gate": "rule_20_self_check", "evidence": "no QA deposit contains Rule 20 self-check banner"})` (branch: banner not found in QA report content). Both evidence strings are **byte-identical**. Line numbers match BACKLOG exactly. | **Open-confirmed** | Include in executable batch as 1-line evidence string change at `gates.py:441` — disambiguate the no-md-paths branch to e.g. `"deposits block declares no .md paths (check **Deposits:** block format)"`. Leave `gates.py:464` as-is. Trivial: 1 string edit + 1 regression test. |
| **2** — `_extract_plan_required_deposits` set-vs-list | BACKLOG claims function returns a `set`, making `md_paths[0]` hash-dependent. | **gates.py:391:** `paths = []` (list initializer in block form). **gates.py:402:** `paths = []` (inline form). **gates.py:409:** `paths = []` (legacy fallback). **gates.py:425:** `paths = list(dict.fromkeys(paths))` (dedup preserving insertion order). All three code paths return `_filter_transient_paths(paths)` where `paths` is a **list**. Function docstring at line 373: "Returns a list preserving insertion order". | **Closed-shipped** | Retire from BACKLOG with reference to 2026-05-25 QA report at `knowledge/qa/executable-extract-plan-required-deposits-set-to-list-2026-05-25.md`. The function now returns an ordered list with `dict.fromkeys` dedup. BACKLOG hygiene closure only — no code change needed. |
| **3** — Path-keyed rejection cache for `dispatch_mode_validator` | BACKLOG claims that when `dispatch_mode_validator` rejects a plan, a corrected re-deposit at the same filename is silently skipped on subsequent scans. Claims cache is keyed by filename/path and not invalidated on `on_modified`. | The "rejection cache" is the **`self._seen`** set at **bellows.py:1047** (`self._seen = set()`), keyed by **slug** via `verdict.slug_from_path()`. Flow: (1) `on_created`/`on_modified` → `_handle()` → `_seen.add(slug)` at line 1024 before `handle_new_plan()` is called; (2) `run_plan()` → `validators.validate_at_claim()` rejects at line 390 → file moved to `halted-*` at line 391; (3) corrected re-deposit at same filename → `on_created` fires → slug already in `_seen` → returns at line 1004. **`on_modified` handler** at **bellows.py:1032-1034** calls `self._handle(event.src_path)` which checks `_seen` at line 1004 — **no invalidation logic**. The `_rescan` method at line 1105 also checks `_seen` at line 1116 with no invalidation. BACKLOG's claim is **confirmed**: cache keyed by slug (path-derived identifier), not content hash, not invalidated on file modification. | **Open-confirmed** | Include in executable batch. Fix shape: invalidate `_seen` entry on `on_modified` when the modified file is a runnable plan whose slug is in `_seen` AND the file is not currently `in-progress-*` or `verdict-pending-*`. Small: ~5 LOC in `_handle` method + 1 regression test. |
| **4** — `_apply_defensive_header_defaults` ineffective at runtime | BACKLOG claims function at `bellows.py:381` mutates header, but `header` is reassigned at `bellows.py:494` from `gate_result.get("plan_header", {})` dropping the defensive default. Claims `header_says_pause()` consumers at `bellows.py:502` and `bellows.py:590` use the re-parsed header without the default. | **(a)** Function definition at **bellows.py:318-327**: `def _apply_defensive_header_defaults(header: dict, total_steps: int) -> dict:` — mutates header in place, sets `header["pause_for_verdict"] = "after_step_1"` when `total_steps > 1 and len(header) < 3` and PV is missing/empty. **(b)** Call site at **bellows.py:382**: `_apply_defensive_header_defaults(header, total_steps)` — applies the default to the pre-gate `header`. **(c)** Reassignment at **bellows.py:498**: `header = gate_result.get("plan_header", {})` — fresh dict from `gates.check()` re-parse, does NOT call `_apply_defensive_header_defaults`. **(d)** First consumer at **bellows.py:506**: `header_says_pause(header, current_step, total_steps, gate_result["is_qa_step"])` (intermediate-step while loop). Second consumer at **bellows.py:596**: `header_says_pause(header, current_step, total_steps, gate_result["is_qa_step"])` (final-step check). Both use the reassigned header from line 498 without the defensive default. BACKLOG claim is **confirmed**. Line numbers have shifted: BACKLOG cited 381/494/502/590; actual current lines are 382/498/506/596 (shifted +1 to +6 from intervening commits). | **Open-shifted** | Re-scope line numbers: call site is `bellows.py:382`, reassignment is `bellows.py:498`, consumers at `bellows.py:506` and `bellows.py:596`. Same fix shape applies: add `_apply_defensive_header_defaults(header, total_steps)` after line 498. Small: 1 LOC insertion + 1 regression test. |

---

## Q5 — Verification Block (Rule 39)

Exact line numbers found in current files for each quoted evidence line:

| Item | BACKLOG Line Ref | Verified Current Line | Delta | File |
|------|------------------|-----------------------|-------|------|
| 1 | `gates.py:441` (no-md_paths branch) | **gates.py:441** | 0 | `gates.py` |
| 1 | `gates.py:464` (banner-not-in-content branch) | **gates.py:464** | 0 | `gates.py` |
| 2 | `gates.py:373` (function def) | **gates.py:372** | -1 | `gates.py` |
| 2 | `gates.py:380` (paths initializer) | **gates.py:391** (block form) | +11 | `gates.py` |
| 2 | `gates.py:397` (dedup) | **gates.py:425** | +28 | `gates.py` |
| 3 | `_seen` set (no BACKLOG line ref) | **bellows.py:1047** | N/A | `bellows.py` |
| 3 | `on_modified` handler | **bellows.py:1032-1034** | N/A | `bellows.py` |
| 4 | `bellows.py:381` (call site) | **bellows.py:382** | +1 | `bellows.py` |
| 4 | `bellows.py:494` (reassignment) | **bellows.py:498** | +4 | `bellows.py` |
| 4 | `bellows.py:502` (while-loop consumer) | **bellows.py:506** | +4 | `bellows.py` |
| 4 | `bellows.py:590` (final-step consumer) | **bellows.py:596** | +6 | `bellows.py` |

**Notes:**
- Item 1 line numbers are exact matches — no drift.
- Item 2 line numbers drifted significantly because the function was rewritten (set → list conversion, block/inline/legacy code paths restructured) as part of the already-shipped fix.
- Item 3 had no specific line references in the BACKLOG entry; the cache mechanism is now precisely located.
- Item 4 line numbers shifted +1 to +6, consistent with code additions from intervening 2026-05-24 through 2026-05-26 commits (rename-first ordering, precondition-failure field, Fix F guard removal, deposit-exists normalization). The structural claim is fully intact; only line numbers need updating in the executable batch.

---

## Q6 — Cross-Item Dependency Check

Items 1, 3, and 4 are fully independent and have no ordering constraints. Item 1 touches a single evidence string in `_gate_rule_20_self_check` at `gates.py:441` — entirely within `gates.py`. Item 3 touches the `_seen` set and `_handle` method in the `PlanHandler` class at `bellows.py:991-1034` — watchdog event handling, disjoint from plan execution. Item 4 touches the `header` reassignment at `bellows.py:498` in `run_plan()` — plan execution path, but a different region from Item 3's watchdog handler and a different file from Item 1's gates.py change. No merge churn risk from shipping in any order or together. The three items can be authored as independent steps within a single executable batch or as three separate plans without conflict.

---

## Flags for CEO

**Recommendation: (a) executable batch covering confirmed-Open subset, with Item 2 closed via BACKLOG hygiene edit.**

- **Items 1, 3, 4** are all confirmed as live, fixable issues. Item 1 is Open-confirmed (exact line match), Item 3 is Open-confirmed (mechanism now precisely located), Item 4 is Open-shifted (same fix, updated line numbers). All three are small-effort (1-5 LOC each + regression tests). They are independent and can ship in a single batch.
- **Item 2** is Closed-shipped. The BACKLOG entry should be retired with a reference to the 2026-05-25 QA report. This is the BACKLOG hygiene closure the Planner identified as needed.
- **No further investigation required** — all four items are now grounded in verified code state with exact line numbers for the executable batch.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1 (SA diagnostic)
**Status:** Complete

### What Was Done
Audited four BACKLOG items against current code state to produce a Gap Assessment table with verified line numbers, cross-item dependency analysis, and CEO disposition recommendation. Three items confirmed as live (1 exact match, 1 confirmed with new mechanism details, 1 confirmed with shifted line numbers); one item confirmed as already shipped.

### Files Deposited
- `bellows/knowledge/research/bellows-hardening-batch-freshness-2026-05-26.md` — Gap Assessment table (Items 1-4), Q5 verification block, Q6 ordering analysis, Flags for CEO

### Files Created or Modified (Code)
- None (read-only investigation)

### Decisions Made
- Classified Item 3's "rejection cache" as the `_seen` set mechanism (keyed by slug, not path or content hash) — this is a more precise characterization than the BACKLOG entry's framing
- Confirmed Item 4's line number shifts are consistent with intervening commits, not a structural change to the bug

### Flags for CEO
- Recommend executable batch for Items 1, 3, 4 with BACKLOG hygiene closure for Item 2
- Item 4 line numbers in the executable batch must use the verified current values (382/498/506/596), not the BACKLOG's stale references (381/494/502/590)

### Flags for Next Step
- None — this is the terminal step of a single-step diagnostic
