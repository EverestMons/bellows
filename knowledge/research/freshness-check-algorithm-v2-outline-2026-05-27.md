# Freshness-Check Algorithm V2 — Blueprint Outline

**Date:** 2026-05-27
**Plan:** executable-freshness-check-algorithm-v2-blueprint-2026-05-27
**Step:** 1 (SA)
**V1 Script:** `scripts/check_backlog_freshness.py` (239 LOC)
**V1 Dev Log:** `knowledge/development/leftover-after-ship-tooling-implementation-2026-05-26.md`

---

## 1. High-Distinctiveness Term Extraction

This section will specify the replacement for v1's `extract_fingerprint()` function, which currently emits all title words and backticked identifiers without filtering for distinctiveness. The v2 extractor will retain only terms that are structurally distinctive — backtick-delimited identifiers, hyphenated compounds above a length floor, underscore-bearing identifiers, and executable slugs cited in the entry text — and will drop title-word matching entirely. The section will state each extraction rule as a literal regex with minimum-length thresholds, producing a compact fingerprint that excludes the generic shared-vocabulary terms (`project`, `status`, `diagnostic`, `deposits`, `output`, `match`, etc.) that drove v1's 6/6 false-positive rate.

## 2. Per-Source Matching Rules

This section will redefine the matching threshold for each of the three evidence sources (git log, PROJECT_STATUS Completed, BACKLOG Closed) using only the high-distinctiveness terms from Section 1. Each source's matching rule will specify the minimum overlap count, minimum term-length constraints, and any source-specific qualifications (e.g., slug-token length floor for PROJECT_STATUS, backticked-identifier equality for BACKLOG Closed). The goal is to tighten matching so that only entries with structurally distinctive term overlap — not generic vocabulary coincidence — produce candidates.

## 3. FP Validation Against 6 Currently-Open Entries

This section will take the 6 Open entries from the v1 live run (all of which were flagged as `investigate-as-shipped`) and re-evaluate each one under v2 rules. For every v1-flagged candidate, the section will list the candidate, apply v2's high-distinctiveness extraction and per-source matching rules, and state whether the candidate survives or is filtered out. The target is zero false positives — no Open entry should surface a candidate unless the candidate genuinely addresses that entry's topic.

## 4. Ground-Truth Re-Validation Against 4 Recurrences

This section will re-trace the 4 confirmed recurrence cases (set→list, precondition-failure-field, Phase 3b read-side, mcp\_\_vexp\_\_) through v2's extraction and matching rules. For each case, the section will identify which terms qualify as high-distinctiveness under Section 1's criteria and which evidence sources still trigger under Section 2's thresholds. The purpose is to confirm that v2's tighter filtering preserves all 4 true-positive catches — no regression from v1.

## 5. Implementation-Edit Guidance

This section will specify the targeted code changes needed in `scripts/check_backlog_freshness.py` to implement v2. It will identify which functions to modify (primarily `extract_fingerprint()` and the per-source matching blocks), which constants change, what stays identical (parsing, output format, CLI, `CLOSURE_SIGNAL_RE`, entry regex patterns), and any new constants or helpers required. The guidance will be precise enough for a DEV agent to apply as a scoped edit rather than a full rewrite.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Produced a 5-section thin outline for the v2 blueprint addendum. Each section contains an H2 heading and a 2-3 sentence intent paragraph describing what the full blueprint (Step 2) will contain. No algorithm design, regex shapes, threshold numbers, or traces are included — this is the scaffold only.

### Files Deposited
- `knowledge/research/freshness-check-algorithm-v2-outline-2026-05-27.md` — this outline

### Files Created or Modified (Code)
- None

### Decisions Made
- Claim-move skipped: plan file is in `.bellows-cache/`, not `knowledge/decisions/` (same pattern as 3 prior plans in this session)
- No domain glossary exists; specialist file provides sufficient context (same as prior feedback)

### Flags for CEO
- None

### Flags for Next Step
- Step 2 should read this outline and fill each section sequentially per the plan's detailed spec
- The 6 currently-Open entries referenced in Section 3 are from the v1 live output at `knowledge/research/backlog-freshness-check-2026-05-26.md`
