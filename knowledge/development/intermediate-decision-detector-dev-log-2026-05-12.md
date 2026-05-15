# Dev Log — Intermediate Decision Detector (Step 1)

**Date:** 2026-05-12
**Plan:** executable-intermediate-decision-detector-2026-05-12

---

## Files Created

| File | Description |
|---|---|
| `/Users/marklehn/Desktop/GitHub/INTERMEDIATE_DECISION_PHRASES.md` | Governance-root phrase list — 33 entries (some with `/`-separated alternatives), matching the 2026-05-12 audit's final extended grep list |
| `bellows/decisions.py` | Detector module — `load_phrases()` reads + caches phrase file, `extract_decision_blocks()` scans NDJSON for assistant text matches |
| `bellows/tests/test_decisions.py` | Unit tests — 16 tests covering load, S-class ground truth, edge cases, multiple content items |

## Files Modified

| File | Description |
|---|---|
| `bellows/verdict.py` | Added `intermediate_decisions` parameter to `post_verdict_request()`, renders `## Intermediate Decisions Detected` section when blocks present |
| `bellows/runner.py` | Added `import decisions`, calls `extract_decision_blocks()` after NDJSON parse, adds `intermediate_decisions` key to returned dict |
| `bellows/bellows.py` | Passes `intermediate_decisions=parsed.get("intermediate_decisions", [])` at 3 verdict-request call sites (mid-plan pause, final-step pause, auto-close teardown failure) |
| `bellows/tests/test_verdict.py` | Added 3 integration tests for the new section rendering (populated, empty, None) |

## Test Results

- **Total:** 292 (291 passed, 1 failed)
- **Pre-existing failure:** `test_run_step_timeout` (mocks `subprocess.run` but `runner.py` uses `subprocess.Popen`)
- **New tests added:** 19 (16 in `test_decisions.py` + 3 in `test_verdict.py`)
- **Test count delta:** +19

## Deviations from Plan

- **Phrase file format for "actually":** The audit entry `actually (followed by comma or space)` is represented as two bullet alternatives `actually, / actually` in the phrase file, with `load_phrases()` splitting on ` / `. The parenthetical qualifier is handled via the two variants rather than special-case regex.
- **Text truncation:** Plan specified 500 chars, implemented as specified.
- **No changes to `bellows.py` module fingerprint list:** `decisions.py` is a new module but was not added to `_module_fingerprints()` since the plan did not specify this and the function currently tracks only the 5 original modules.

## Decisions Made on Initiative

- **`load_phrases()` caching:** Used a module-level `_cached_phrases` variable with explicit `None` sentinel for cache invalidation in tests via `decisions._cached_phrases = None`. This avoids re-reading the file on every step execution.
- **Slash-alternative splitting:** `load_phrases()` splits on ` / ` (space-slash-space) to convert multi-phrase audit entries into individual searchable phrases. This produces ~45 individual phrases from 33 bullet lines.
- **Worktree creation failure path (line 398):** Did NOT add `intermediate_decisions` parameter — this call site has no `parsed` result (worktree failed before runner invocation).

---

## Output Receipt

**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Implemented phrase-based intermediate-decision detection for Bellows. Created governance-root phrase file with 33 entries from the 2026-05-12 audit. Built `decisions.py` detector module with `load_phrases()` and `extract_decision_blocks()`. Integrated into `verdict.py` (new optional section), `runner.py` (extraction after NDJSON parse), and `bellows.py` (pass-through at 3 verdict call sites). Added 19 tests covering ground truth, edge cases, and verdict rendering.

### Files Deposited
- Listed above in Files Created/Modified tables

### Decisions Made
- Listed above in Decisions Made on Initiative

### Flags for CEO
- None

### Flags for Next Step
- None

---

## Step 2 — Vexp Exemption

**Date:** 2026-05-12

### Tools Added

| Tool | Justification |
|---|---|
| `mcp__vexp__run_pipeline` | Read-class code-exploration tool. Triggered `no_permission_denials` gate failure on the 2026-05-12 design diagnostic (confirmed in verdict `processed-verdict-intermediate-decision-detection-design-2026-05-12-step-1.md`). Agent fell back to direct file reads, so the denial was a false positive. |

No other Vexp tools were added. Scanned all log files (`logs/2026*-step.json`) for parsed `permission_denials` entries containing Vexp tool names — none found. Per plan guidance: "If only `run_pipeline` is observed today, add only that one — do not speculatively add tools that aren't confirmed Vexp read-class."

### Files Modified

| File | Description |
|---|---|
| `bellows/gates.py` | Extended `READ_CLASS_TOOLS` from `{"Grep", "Glob", "Read"}` to `{"Grep", "Glob", "Read", "mcp__vexp__run_pipeline"}` |
| `bellows/tests/test_gates.py` | Added 1 regression test: `test_permission_denials_vexp_run_pipeline_exempt` — asserts that a `mcp__vexp__run_pipeline` denial does NOT trip the gate |

### Test Results

- **Total:** 293 (292 passed, 1 failed)
- **Pre-existing failure:** `test_run_step_timeout` (unchanged)
- **New tests added:** 1 (`test_permission_denials_vexp_run_pipeline_exempt` in `test_gates.py`)
- **Test count delta:** +1

### Deviations from Plan

- None.

---

## Output Receipt

**Agent:** Bellows Developer
**Step:** 2
**Status:** Complete

### What Was Done
Extended `READ_CLASS_TOOLS` in `gates.py` to include `mcp__vexp__run_pipeline`, closing the gate-exemption gap that caused a false-positive `no_permission_denials` gate failure on the 2026-05-12 design diagnostic. Added 1 regression test.

### Files Deposited
- `bellows/gates.py`
- `bellows/tests/test_gates.py`
- `bellows/knowledge/development/intermediate-decision-detector-dev-log-2026-05-12.md`

### Decisions Made
- Added only `mcp__vexp__run_pipeline` — no other Vexp tools confirmed in parsed denial logs.

### Flags for CEO
- None

### Flags for Next Step
- None
