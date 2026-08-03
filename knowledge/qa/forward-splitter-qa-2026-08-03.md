# Forward Splitter — QA Report (Plan 294)

**Date:** 2026-08-03
**Step:** 2 (QA)
**BELLOWS_TREE:** /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/294
**CODE_SHA:** `eefd2a96cafb2bf3399fcaf37d25166b35cff432`

---

## Deliverable Verification

| Deliverable | Expected | Status | Evidence |
|---|---|---|---|
| `bellows.py` | `BULLET_RE`, `sanitize_items`, updated `_append_forward_row` | ✅ | `grep -n 'BULLET_RE\|def sanitize_items' bellows.py` confirms both present; controls pass |
| `tests/test_bellows.py` | Docstring amendment + 5 new tests in `TestForwardMultiItemSplit` | ✅ | Diff shows only docstring change in `TestForwardSingleLineItem`; 5 tests found at lines 5039-5165 |
| `knowledge/development/forward-splitter-dev-2026-08-03.md` | Dev-log with Output Receipt marked Complete | ✅ | Read and confirmed |

---

## Verification Table

| # | Claim | Status | Evidence |
|---|---|---|---|
| 1 | Negative control — plan 62 narration guard survives | ✅ | `sanitize_items` on plan-62 fixture: 1 result `['CANARY item text here']`; "Now commit" absent; "All 5 checks" absent. RAW output in `controls.txt` |
| 2 | Positive control — six-bullet block yields SIX rows | ✅ | `sanitize_items` on 6-bullet input: 6 results, each carrying its own item. RAW output in `controls.txt` |
| 3 | Existing assertions intact — only docstring changed | ✅ | `diff` of `TestForwardSingleLineItem` pre/post shows only line 27 docstring change: `"Multi-line item_text → valid single-line 7-pipe row."` → `"Narration-guard negative control: unbulleted multi-line → single row, trailing prose excluded."`. Drift check `git log eefd2a9..HEAD -- bellows.py tests/test_bellows.py` is EMPTY |
| 4 | All five new tests exist and pass | ✅ | (1) `test_threshold_discriminator_one_bullet_one_unbulleted` — 1 bullet + 1 unbulleted → 1 row carrying unbulleted line, bullet absent; (2) `test_multi_bullet_positive` — 3 bullets → 3 rows, 7-pipe each; (3) `test_narration_with_bullets_negative_contiguous` — 2 bullets + prose → 2 rows, prose excluded; (4) `test_trailing_artifact_strip_multi_bullet` — 2 bullets with ` .` → artifact stripped; (5) `test_preamble_then_bullets` — heading + 2 bullets → only bullets become rows. 180 targeted pass |
| 5 | Single-item path byte-identical | ✅ | Extracted pre-change module (121048 bytes, exit=0); both old and new produce `\| 2 \| 2026-08-03 \| CANARY item text here \| deferred-work \| — \| open \|` — byte-identical |
| 5b | Trailing artifact strip survives on multi-bullet path | ✅ | `grep -nF 'endswith(" .")' bellows.py` → line 1454 inside the per-item loop; `test_trailing_artifact_strip_multi_bullet` uses a ≥2-bullet fixture and asserts ` .` absent from each row's item cell |
| 6 | Row numbering correct across N rows | ✅ | `test_multi_bullet_positive` uses `FORWARD_FIXTURE` with row 1 pre-existing; asserts 3 new rows each with 7-pipe structure. `_append_forward_row` increments `next_num` per item in the loop (line 1458) |
| 7 | Suite green | ✅ | Targeted: 180 passed (175 + 5 new). Full: 839 passed (834 baseline + 5 new). Zero regressions. RAW output in `pytest_targeted.txt` and `pytest_full.txt` |
| 8 | Scope — only expected files changed | ✅ | `git show --name-only eefd2a9`: `bellows.py`, `tests/test_bellows.py`, `knowledge/development/forward-splitter-dev-2026-08-03.md`. `git status --porcelain` is clean. Cross-repo check: `invoice-pulse`, `anvil`, `lessons-forge`, `governance` all show no `FORWARD.md` modifications |
| 9 | No register written by this plan | ✅ | Commit scope (row 8) contains no `FORWARD.md`. No register was touched |
| 9b | Daemon still runs old code premise | NOTE | `pgrep -f '[b]ellows\.py\|[d]ashboard\.py'` returned NO PROCESS. The daemon is not currently running. Commit time: `2026-08-03T07:33:24-05:00`. Since no daemon is running, the premise is vacuously satisfied — no process is executing either old or new code. The CEO's wrap-time restart will start the daemon with the new code directly |

---

## Rule 20 Self-Check

**Pin:** `RULE_20_SELF_CHECK_BLOCK.md` = `3accbce0c8d2b445` (measured). Authoring pin: `3accbce0c8d2b445`. **Match — no drift.**

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/294/knowledge/qa/evidence/forward-splitter-2026-08-03/
Files verified: 2
```

---

### Ledger Updates

#### Project Status

The Forward Register append is now bullet-aware: multi-item Receipt blocks emit one row per item, with plan 62's narration guard preserved as the fallback when fewer than 2 bullet lines match. NOT live until the daemon is restarted — the code is on main but the running daemon (when started) will pick up the new module at its next launch.

#### Forward Register

- The Forward Register append has a partial-write window: if the process dies after the file write and commit but before record_ledger_write, a redo re-appends and yields duplicate rows — 2N under the multi-item splitter, unchanged in class from the pre-existing single-row behaviour and not closed by it.

#### Prompt Feedback

The plan's verification structure was thorough and well-calibrated. The row 3 `sed` extraction with `$d` on both sides worked correctly even with the new class adjacent — the plan's specific warning about this being required proved accurate. The single-item byte-identity test (row 5) required loading the pre-change module via `importlib` with `PYTHONPATH` set, matching plan 286's countermeasure. The threshold discriminator (test 1 in task D) is the strongest guard — it is the only test that distinguishes `>=2` from `>=1`, and its absence would let a guard-inverting implementation pass the entire suite.

---

## Output Receipt

### Status

**Complete**

### Deposits

- `knowledge/qa/forward-splitter-qa-2026-08-03.md` — this QA report
- `knowledge/qa/evidence/forward-splitter-2026-08-03/pytest_targeted.txt` — targeted test output (180 passed)
- `knowledge/qa/evidence/forward-splitter-2026-08-03/controls.txt` — negative and positive control outputs
- `knowledge/qa/evidence/forward-splitter-2026-08-03/pytest_full.txt` — full suite output (839 passed)
