# Freshness-Check Algorithm V2 Implementation — Dev Log

**Date:** 2026-05-27
**Plan:** executable-freshness-check-algorithm-v2-implementation-2026-05-27
**Step:** 1 (DEV)
**Blueprint:** `knowledge/research/freshness-check-algorithm-v2-blueprint-2026-05-27.md`

---

## Code Changes

Modified `scripts/check_backlog_freshness.py` (254 LOC, up from v1's 239). Three scoped edits per blueprint Section 5:

**`extract_fingerprint()` — rewritten body (lines 45–67):**
- 4 extraction rules replacing v1's 4-rule-plus-title-words approach:
  - Rule 1: Backtick identifiers `len >= 5` (was `>= 3`)
  - Rule 2: Hyphenated compounds `len >= 12` (was: no floor)
  - Rule 3: Underscore identifiers `len >= 8` with `>= 2` underscores (was: no floors)
  - Rule 4: Executable slugs cited in text (new)
- Title-word matching dropped entirely (v1 lines 63–67 removed)
- Docstring updated: "distinctive" → "high-distinctiveness"

**`find_candidates()` — modified thresholds (lines 148–190):**
- Git: threshold lowered `>= 2` → `>= 1`
- PROJECT_STATUS: slug-token floor `len >= 6` added, threshold lowered `>= 2` → `>= 1`
- BACKLOG Closed: replaced `len(matching) >= 2 and any(len(t) >= 8)` with new v2 rule: `any(len(t) >= 12)` OR backtick-id condition (same backtick identifier `len >= 5` in both open and closed entries)

**`STOPWORDS` constant — deleted (v1 lines 45–49):**
No longer referenced after title-word matching removal.

**What stayed identical:**
- All parsing functions (`parse_open_entries`, `parse_closed_entries`, `parse_ps_entries`, `get_closure_commits`)
- All regexes (`OPEN_ENTRY_RE`, `CLOSED_ENTRY_RE`, `PS_ENTRY_RE`, `GIT_LINE_RE`, `CLOSURE_SIGNAL_RE`, `REFERENCE_SLUG_RE`)
- Utilities (`score_overlap`, `tokenize_slug`)
- Output (`generate_report`)
- CLI (`main`, argparse), constants (`BELLOWS_ROOT`, etc.), shebang, docstring, `__main__` guard

**LOC note:** 254 vs predicted ~234. The +20 delta comes from the backtick-id condition in the Closed matching rule (~8 LOC) and the v2 `find_candidates` body being longer than v1 due to the structured long-match/backtick-match logic. Implementation matches Section 5 code verbatim.

---

## V1 vs V2 Output Comparison

**V1 header (2026-05-26):**
```
Window: 14 days | Open entries scanned: 6 | Candidates surfaced: 6 | No-match: 0
```

**V2 header (2026-05-27):**
```
Window: 14 days | Open entries scanned: 6 | Candidates surfaced: 6 | No-match: 0
```

**Per-entry comparison:**

| Entry | V1 Candidates | V2 Candidates | Blueprint Predicted |
|-------|---------------|---------------|---------------------|
| 1 — worktree teardown | 5 (1 git, 4 closed) | 3 (3 PS) | 0 |
| 2 — parallel-diagnostic | 8 (8 closed) | 1 (1 closed) | 1 |
| 3 — status UI | 3 (1 git, 2 closed) | 7 (7 PS) | 0 |
| 4 — deposits parser | 8 (2 git, 2 PS, 4 closed) | 7 (1 git, 2 PS, 4 closed) | 6 |
| 5 — rate-limit | 9 (1 git, 2 PS, 6 closed) | 12 (7 PS, 5 closed) | 6 |
| 6 — case-sensitivity | 6 (5 PS, 1 closed) | 7 (7 PS) | 2 |
| **Totals** | **39** | **37** | **15** |
| **Entries flagged** | **6/6** | **6/6** | **4/6** |

**Deviation analysis:** V2 output deviates significantly from the blueprint's predicted 15 candidates / 4 entries. The blueprint's Section 3 analysis only re-traced v1-flagged candidates and explicitly warned "new candidates are possible" (Section 5, Flags for Next Step). The deviation has a single root cause:

**New PS noise from generic slug tokens.** The v2 PS rule (slug tokens `>= 6` chars, threshold `>= 1`) creates new false positives when common slug tokens match entry text as substrings:
- `bellows` (7 chars) from slugs like `executable-bellows-test-isolation-conftest` matches "Bellows" in Entries 3 and 5
- `planner` (7 chars) from `executable-planner-template-rule-21-contract-change` matches "planner" inside "sequential-planner-edit" in Entries 1 and 6
- `template` (8 chars), `header` (6 chars), `governance` (10 chars), `lessons` (7 chars) similarly match in Entry 6

V2 DID successfully eliminate v1's primary noise source (BACKLOG Closed matches on title words like `diagnostic`, `teardown`, `project`, `worktree`). Entry 2 dropped from 8 → 1 candidates. But the PS channel noise replaced it.

**Sample Entry 2 (biggest improvement):**
```
V1: 8 candidates (all backlog_closed, matching on: diagnostic, teardown, files, cherry, cherry-pick, parallel, invoice-pulse)
V2: 1 candidate  (backlog_closed: invoice-pulse)
```

**Sample Entry 3 (biggest regression):**
```
V1: 3 candidates (1 git "bellows, status", 2 closed "output/terminal", "bellows/observability")
V2: 7 candidates (7 PS entries all matching on "bellows" slug token)
```

---

## Manual Ground-Truth Re-Trace

The 4 ground-truth recurrences from blueprint Section 4, traced through the v2 implementation.

### Case 1 — set→list (`_extract_plan_required_deposits`)

**Hypothetical Open entry text:** `_extract_plan_required_deposits()` returns a `set` making `md_paths[0]` hash-dependent

**V2 fingerprint would include:** `_extract_plan_required_deposits` (backtick 31, underscore 31), `md_paths[0]` (backtick 10), `hash-dependent` (hyphenated 14)

**Git — CAUGHT ✓**
- Commit `4e805fa` subject: `fix(gates): _extract_plan_required_deposits set→list — ...closes BACKLOG capability`
- `CLOSURE_SIGNAL_RE`: `closes BACKLOG` ✓
- `score_overlap(fp, subject)`: `_extract_plan_required_deposits` in lowered subject ✓ → score ≥ 1 ✓
- Code path: line 156 `if score_overlap(fp, subject) >= 1` → True

**PS — CAUGHT ✓**
- Slug: `executable-extract-plan-required-deposits-set-to-list-2026-05-25`
- Tokens ≥ 6: `extract` (7), `required` (8), `deposits` (8)
- `extract` in entry text (inside `_extract_plan_required_deposits`) ✓ → overlap ≥ 1 ✓
- Code path: lines 164-166 `len(t) >= 6 and t in text_lower` with threshold ≥ 1

### Case 2 — precondition-failure verdict-request field

**Hypothetical Open entry text:** Step-counter loop after precondition-failure verdict

**V2 fingerprint would include:** `precondition-failure` (hyphenated 20), `step-counter` (hyphenated 12)

**BACKLOG Closed — CAUGHT ✓**
- Closed entry text: "Step-counter loop after precondition-failure verdict (originally 2026-05-21). Shipped via..."
- `matching`: `precondition-failure` ✓, `step-counter` ✓
- `long_match`: `precondition-failure` (20 ≥ 12) → True
- Code path: line 173 `long_match = any(len(t) >= 12 for t in matching)` → True; line 185 `if matching and (long_match or backtick_match)` → True

### Case 3 — Phase 3b read-side step-state-resume

**Hypothetical Open entry text:** Phase 3b step-state-resume (DB read-side)

**V2 fingerprint would include:** `step-state-resume` (hyphenated 17)

**BACKLOG Closed — CAUGHT ✓**
- Closed entry text: "Phase 3b/3c DB step-state-resume slug-collision..."
- `matching`: `step-state-resume` ✓
- `long_match`: `step-state-resume` (17 ≥ 12) → True
- Code path: same as Case 2
- **Thinnest catch** — single qualifying fingerprint term, as noted in blueprint Section 4.

### Case 4 — mcp\_\_vexp\_\_ READ\_CLASS\_TOOLS extension

**Hypothetical Open entry text:** MCP tool denials (`mcp__vexp__run_pipeline`, `mcp__vexp__get_context_capsule`) not on `READ_CLASS_TOOLS` exemption list

**V2 fingerprint would include:** `mcp__vexp__run_pipeline` (backtick 22, underscore 22), `mcp__vexp__get_context_capsule` (backtick 30, underscore 30), `read_class_tools` (backtick 16, underscore 16)

**Git — CAUGHT ✓**
- Commit `9473cf7` subject: `fix(gates): extend READ_CLASS_TOOLS with 5 vexp read-class tools — closes BACKLOG mcp_tool_denials`
- `CLOSURE_SIGNAL_RE`: `closes BACKLOG` ✓
- `score_overlap(fp, subject)`: `read_class_tools` in lowered subject ✓ → score ≥ 1 ✓
- Code path: line 156

**PS — MISS (correct per blueprint):**
- Slug tokens ≥ 6: only `extension` (9). `mcp` (3), `read` (4), `class` (5), `tools` (5) all below 6-char floor.
- `extension` not in entry text (says "exemption" not "extension") → overlap = 0 < 1.
- Blueprint Section 4 predicted this regression; Git compensates.

### Ground-Truth Summary

| Case | Git | PS | Closed | Caught? | V2 Regression? |
|------|-----|----|--------|---------|----------------|
| 1 — set-to-list | ✓ (score ≥ 1) | ✓ (`extract` 7≥6) | n/a | **Yes** | No |
| 2 — precondition-failure | — | — | ✓ (`precondition-failure` 20≥12) | **Yes** | No |
| 3 — Phase 3b | — | — | ✓ (`step-state-resume` 17≥12) | **Yes** | No |
| 4 — mcp\_\_vexp\_\_ | ✓ (score ≥ 1) | **MISS** (no token ≥ 6) | n/a | **Yes** | PS channel lost; Git compensates |

**All 4 ground-truth cases still caught.** Implementation matches blueprint Section 4 traced behavior. Case 4 PS regression is expected and accepted per blueprint.

---

## Output Receipt

**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done

Applied v2 algorithm edits to `scripts/check_backlog_freshness.py` per blueprint Section 5: rewrote `extract_fingerprint()` with 4 high-distinctiveness extraction rules (title-word matching removed), modified `find_candidates()` with lowered thresholds and new Closed-matching rule (long-match OR backtick-id condition), deleted `STOPWORDS` constant. Preserved v1 report to `/tmp/v1-freshness-report.md`. Ran v2 against live repo, producing report at `knowledge/research/backlog-freshness-check-2026-05-27.md`. Hand-traced all 4 ground-truth cases through the v2 implementation, confirming all still catch.

### Files Deposited

- `knowledge/development/freshness-check-algorithm-v2-implementation-2026-05-27.md` — this dev log

### Files Created or Modified (Code)

- `scripts/check_backlog_freshness.py` — modified (254 LOC, was 239), algorithm-only change

### Decisions Made

- **Claim-move skipped:** plan file is in `.bellows-cache/`, not `knowledge/decisions/`; sixth consecutive occurrence of this pattern
- **254 LOC (above predicted ~234):** the backtick-id condition from blueprint Section 5 adds more LOC than the LOC estimate accounted for; implementation matches Section 5 code verbatim, so no simplification attempted
- **No implementation-time threshold adjustment:** v2 output (37 candidates, 6/6 flagged) deviates significantly from blueprint's prediction (15, 4/6) due to new PS noise. However, the implementation matches the blueprint's prescribed code exactly. Threshold tuning is a design decision, not a DEV decision.

### Flags for CEO

- **V2 output did not achieve the predicted noise reduction.** Blueprint predicted 15 candidates / 4 entries flagged; actual output is 37 candidates / 6 entries flagged. The BACKLOG Closed noise source was successfully eliminated (Entry 2: 8 → 1 candidate). However, the lowered PS threshold (`>= 1` token `>= 6` chars) creates new noise from generic slug tokens like `bellows`, `planner`, `template` matching in entry text. This was acknowledged in the blueprint's "Flags for Next Step" but underestimated in the Section 3 candidate count prediction.
- **All 4 ground-truth cases still catch** — no regression in true-positive detection.
- **Implementation is faithful to Section 5.** The deviation is in the blueprint's prediction, not the code. A v2.1 iteration could raise the PS token floor to `>= 8` or restore the PS threshold to `>= 2` to reduce noise.

### Flags for Next Step

- QA should evaluate the v2 output against the plan's acceptance criteria. The plan says "a wild deviation (e.g., still 30+ or under 10) implies an implementation error" — but the implementation matches Section 5 verbatim, so this is a blueprint prediction error, not an implementation error. QA should assess accordingly.
- The v1 report is preserved at `/tmp/v1-freshness-report.md` for diff comparison.
