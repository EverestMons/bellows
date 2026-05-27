# Leftover-After-Ship Tooling Implementation — Dev Log

**Date:** 2026-05-26
**Plan:** executable-leftover-after-ship-tooling-implementation-2026-05-26
**Step:** 1 (DEV)
**Blueprint:** `knowledge/research/leftover-after-ship-tooling-blueprint-2026-05-26.md`

---

## Implementation Notes

Implemented `scripts/check_backlog_freshness.py` (239 LOC) literally per the SA blueprint. Style matches `scripts/migrate_config.py`: shebang, module docstring, module-level constants, single `main()` entry, `__main__` guard.

**Four sources implemented:**
1. **BACKLOG Open** — parsed via `OPEN_ENTRY_RE`, fingerprints extracted per blueprint `extract_fingerprint()`
2. **BACKLOG Closed** — parsed via `CLOSED_ENTRY_RE`, used for duplicate-after-ship detection
3. **PROJECT_STATUS Completed** — parsed via `PS_ENTRY_RE`, date-windowed, slug tokenized
4. **Git log** — closure-signal commits filtered via `CLOSURE_SIGNAL_RE`

**Thresholds (Section 7 final):**
- Git: `score_overlap(fingerprint, subject) >= 2`
- PROJECT_STATUS: `>= 2` slug tokens as substrings in entry text[:300]
- BACKLOG Closed: `score_overlap >= 2` AND at least one matching term `len >= 8`

**Dependencies:** Python stdlib only (`pathlib`, `re`, `subprocess`, `argparse`, `datetime`).

---

## Script Output (Live Run)

**Header summary:**

```
Window: 14 days | Open entries scanned: 6 | Candidates surfaced: 6 | No-match: 0
```

**Sample Entry (no-match would show if present):**

```markdown
## Entry 4: Deposits parser does not strip parenthetical qualifiers (Priority 3 audit). `_ex...

**Filed:** 2026-05-21 | **Action:** investigate-as-shipped

### Candidates

- **[git]** `4e805fa` — `fix(gates): _extract_plan_required_deposits set→list — ...closes BACKLOG capability`
  Match terms: _extract_plan_required_deposits, deposits
- **[project_status]** 2026-05-25 — `executable-extract-plan-required-deposits-set-to-list-2026-05-25`
  Match terms: deposits, extract, plan, required
- **[backlog_closed]** 2026-05-26 — `_extract_plan_required_deposits()` returns a `set`...
  Match terms: _extract_plan_required_deposits, deposits
```

**Sample Entry 1 (worktree teardown cherry-pick):**

```markdown
## Entry 1: Worktree teardown cherry-pick conflict on dirty `PROJECT_STATUS.md`...

**Filed:** 2026-05-22 | **Action:** investigate-as-shipped

### Candidates

- **[git]** `d2e07a9` — `research(bellows): BACKLOG freshness-check script blueprint...`
  Match terms: project, project_status, status
- **[backlog_closed]** 2026-05-10 — `_teardown_worktree` cherry-pick fragility...
  Match terms: cherry, cherry-pick, teardown, worktree
```

**Observation:** All 6 current Open entries surfaced candidates. The blueprint's false-positive analysis (Section 6) claimed zero false positives, but several matches are topic-adjacent rather than exact-topic (e.g., generic terms like `diagnostic`, `project`, `status` matching across unrelated Closed entries). This is expected behavior from substring matching with shared vocabulary — QA Step 2 will evaluate false-positive rate.

---

## Manual Ground-Truth Trace

The 4 ground-truth recurrences are already Closed in the current BACKLOG. Below traces each case through the implemented algorithm to confirm the implementation matches the blueprint Section 6 behavior.

### Case 1 — set-to-list (`_extract_plan_required_deposits`)

**Open entry (hypothetical, now Closed):** `_extract_plan_required_deposits()` returns a `set` making `md_paths[0]` hash-dependent

**Fingerprint includes:** `_extract_plan_required_deposits`, `set`, `md_paths[0]`, `hash-dependent`, `returns`, `making`, `deposits`

**Git match — CAUGHT:**
- Commit `4e805fa`: subject contains `_extract_plan_required_deposits` and `set` → `closes BACKLOG` passes `CLOSURE_SIGNAL_RE`
- `score_overlap(fp, subject)`: `_extract_plan_required_deposits` ✓, `set` ✓ → score = 2 ≥ 2 ✓
- Implementation: `score_overlap()` at line 75 iterates fingerprint terms, checks `term in text_lower` — both terms are substrings of the lowercased subject ✓

**PS match — CAUGHT:**
- Slug: `executable-extract-plan-required-deposits-set-to-list-2026-05-25`
- `tokenize_slug()` → `{extract, plan, required, deposits, set, list}`
- Checked as substrings in entry text[:300]: `extract` ✓, `plan` ✓, `required` ✓, `deposits` ✓, `set` ✓ → overlap = 5 ≥ 2 ✓
- Implementation: lines 147-150 iterate slug tokens, check `t in text_lower` ✓

### Case 2 — precondition-failure verdict-request field

**Open entry (hypothetical, now Closed):** Step-counter loop after precondition-failure verdict

**Fingerprint includes:** `step-counter`, `precondition-failure`, `verdict`, `counter`

**Git — NOT CAUGHT (correct per blueprint):**
- Ship commit `0a90e26` subject lacks closure-signal phrase (`closes BACKLOG` / `backlog hygiene`)
- `CLOSURE_SIGNAL_RE.search()` returns None → commit excluded from candidates ✓

**BACKLOG Closed match — CAUGHT:**
- Closed entry (line 56): "Step-counter loop after precondition-failure verdict (originally 2026-05-21). Shipped via..."
- `score_overlap(fp, closed_text[:300])`: `step-counter` ✓ (12 chars), `precondition-failure` ✓ (20 chars), `verdict` ✓ → score = 3 ≥ 2 ✓
- Length guard: `step-counter` (12) ≥ 8 ✓, `precondition-failure` (20) ≥ 8 ✓
- Implementation: lines 152-155 check `len(matching) >= 2 and any(len(t) >= 8 for t in matching)` ✓

### Case 3 — Phase 3b read-side step-state-resume

**Open entry (hypothetical, now Closed):** Phase 3b step-state-resume (DB read-side)

**Fingerprint includes:** `step-state-resume`, `read-side`, `phase`

**Git — NOT CAUGHT (correct per blueprint):** Ship event was 2026-05-01, outside 14-day window.

**PS — NOT CAUGHT (correct per blueprint):** No PS entry within window references Phase 3b.

**BACKLOG Closed match — CAUGHT:**
- Closed entry (line 147): "Phase 3b/3c DB step-state-resume slug-collision..."
- `score_overlap(fp, closed_text[:300])`: `step-state-resume` ✓ (17 chars), `phase` ✓ → score = 2 ≥ 2 ✓
- Length guard: `step-state-resume` (17) ≥ 8 ✓
- Implementation: same path as Case 2 ✓
- **This is the case that motivated the revised threshold** (≥ 2 with length guard instead of ≥ 3)

### Case 4 — mcp\_\_vexp\_\_ READ\_CLASS\_TOOLS extension

**Open entry (hypothetical, now Closed):** MCP tool denials (`mcp__vexp__run_pipeline`, `mcp__vexp__get_context_capsule`) not on `READ_CLASS_TOOLS` exemption list

**Fingerprint includes:** `mcp__vexp__run_pipeline`, `mcp__vexp__get_context_capsule`, `read_class_tools`, `denials`, `exemption`

**Git match — CAUGHT:**
- Commit `9473cf7`: `fix(gates): extend READ_CLASS_TOOLS with 5 vexp read-class tools — closes BACKLOG mcp_tool_denials`
- `CLOSURE_SIGNAL_RE`: `closes BACKLOG` ✓
- `score_overlap(fp, subject)`: `read_class_tools` ✓ (subject contains `READ_CLASS_TOOLS` lowercased), `denials` ✓ (in `mcp_tool_denials`) → score = 2 ≥ 2 ✓

**PS match — CAUGHT:**
- Slug: `executable-mcp-read-class-tools-extension-2026-05-25`
- `tokenize_slug()` → `{mcp, read, class, tools, extension}`
- Checked as substrings in entry text[:300]: `mcp` ✓, `read` ✓, `class` ✓, `tools` ✓ → overlap = 4 ≥ 2 ✓

### Ground-Truth Summary

| Case | Git | PS | Closed | Caught? | Implementation Match |
|------|-----|----|--------|---------|---------------------|
| 1 — set-to-list | ✓ (score 2) | ✓ (score 5) | n/a | Yes | ✓ |
| 2 — precondition-failure | — | — | ✓ (score 3, len ≥ 8) | Yes | ✓ |
| 3 — Phase 3b | — | — | ✓ (score 2, len ≥ 8) | Yes | ✓ |
| 4 — mcp\_\_vexp\_\_ | ✓ (score 2) | ✓ (score 4) | n/a | Yes | ✓ |

All 4 ground-truth cases confirmed caught by the implemented algorithm. Implementation matches blueprint Section 6 traced behavior for every case.

---

## Output Receipt

**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done

Implemented `scripts/check_backlog_freshness.py` (239 LOC) per the SA blueprint, covering all 4 matching sources (BACKLOG Open fingerprinting, BACKLOG Closed duplicate detection, PROJECT_STATUS Completed slug matching, git log closure-signal matching) with the final thresholds from blueprint Section 7. Ran the script against the live repo, producing a report at `knowledge/research/backlog-freshness-check-2026-05-26.md`. Hand-traced all 4 ground-truth cases through the implementation, confirming each would be caught with the traced match path and scores matching the blueprint.

### Files Deposited

- `knowledge/development/leftover-after-ship-tooling-implementation-2026-05-26.md` — this dev log

### Files Created or Modified (Code)

- `scripts/check_backlog_freshness.py` — new script (239 LOC), Python stdlib only

### Decisions Made

- **239 LOC (within 150-250 range):** chose to keep sorted match-term output for readability; slightly above midpoint but well within bounds
- **Claim-move skipped:** plan file is in `.bellows-cache/`, not `knowledge/decisions/`; same pattern as prior plans in this session

### Flags for CEO

- **All 6 Open entries surfaced candidates:** the blueprint's false-positive analysis claimed zero false positives, but the live run shows topic-adjacent matches from shared vocabulary (e.g., `diagnostic`, `project`, `teardown` match across unrelated Closed entries). The algorithm is implemented correctly per blueprint; the false-positive rate is a threshold-tuning question for future iterations.

### Flags for Next Step

- QA should evaluate the false-positive rate in the live report — all 6 Open entries flagged as `investigate-as-shipped` when the blueprint predicted 0 false positives
- The git commit `d2e07a9` (this plan's own blueprint research commit) triggers matches via generic terms (`project`, `status`, `bellows`) — this is a systemic pattern with research commits that mention multiple BACKLOG/PROJECT_STATUS keywords
