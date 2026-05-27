# Freshness-Check Algorithm V2 — Blueprint

**Date:** 2026-05-27
**Plan:** executable-freshness-check-algorithm-v2-blueprint-retry-2026-05-27
**Step:** 1 (SA)
**V1 Script:** `scripts/check_backlog_freshness.py` (239 LOC)
**V1 Blueprint:** `knowledge/research/leftover-after-ship-tooling-blueprint-2026-05-26.md`
**V1 Live Output:** `knowledge/research/backlog-freshness-check-2026-05-26.md`
**V1 FP Rate:** 6/6 Open entries flagged, 39 total candidates, all false positives

---

## 1. High-Distinctiveness Term Extraction

Replaces v1's `extract_fingerprint()` (lines 52–68). Four extraction rules; title-word matching dropped entirely.

### Rule 1 — Backtick-Delimited Identifiers (length ≥ 5)

**Regex:** `r'`([^`]+)`'` applied to `text[:500]`
**Post-filter:** `len(cleaned) >= 5` where `cleaned = m.group(1).strip('()').lower()`
**Change from v1:** threshold raised from 3 to 5. Excludes short identifiers like `set` (3), `mcp` (3), `list` (4).

**Examples captured:** `_extract_plan_required_deposits` (31), `project_status.md` (17), `mcp__vexp__run_pipeline` (22), `read_class_tools` (16), `_consume_verdicts` (17), `_extract_step_text` (18), `bellows.py:1280` (14), `bellows.db` (10), `agent-prompt-feedback.md` (25)

### Rule 2 — Hyphenated Compounds (total length ≥ 12)

**Regex:** `r'\b([a-zA-Z][\w]*(?:-[a-zA-Z][\w]*){1,})\b'` applied to `text[:300]`
**Post-filter:** `len(compound) >= 12`
**Change from v1:** added length floor. v1 captured all hyphenated compounds regardless of length.

**Examples captured:** `precondition-failure` (20), `step-state-resume` (17), `step-counter` (12), `hash-dependent` (14), `parallel-diagnostic` (21), `sequential-planner-edit` (23), `terminal-only` (13), `case-sensitivity` (16), `invoice-pulse` (13), `verdict-pending` (15)
**Examples excluded:** `cherry-pick` (11), `rate-limit` (10), `no-match` (8), `read-side` (9), `menu-bar` (8)

### Rule 3 — Underscore Identifiers (length ≥ 8, ≥ 2 underscores)

**Regex:** `r'\b(_?[a-z][a-z0-9]*(?:_[a-z0-9]+)+)\b'` applied to `text[:300]` with `re.IGNORECASE`
**Post-filter:** `len(ident) >= 8 and ident.count('_') >= 2`
**Change from v1:** added both length and underscore-count floors. v1 captured all underscore identifiers.

**Examples captured:** `_extract_plan_required_deposits` (31 chars, 5 underscores), `mcp__vexp__run_pipeline` (22, 5), `mcp__vexp__get_context_capsule` (30, 5), `read_class_tools` (16, 2), `_consume_verdicts` (17, 2), `_extract_step_text` (18, 3), `_gate_deposit_exists` (20, 3)
**Examples excluded:** `project_status` (14, 1 underscore), `md_paths` (8, 1 underscore)

### Rule 4 — Executable Slugs Cited in Entry Text

**Regex:** `r'(executable-[\w-]+-\d{4}-\d{2}-\d{2})'` applied to `text[:500]`
**Change from v1:** new rule. Captures explicitly cited executable plan slugs, which are extremely high-distinctiveness.

### Dropped — Title-Word Matching

**Removed entirely.** v1's first-sentence word extraction (lines 63–67) and the `STOPWORDS` constant (lines 45–49) are deleted.

**Terms now excluded from fingerprint:** `project`, `status`, `bellows`, `diagnostic`, `output`, `terminal`, `deposits`, `parser`, `verdict`, `audit`, `priority`, `files`, `teardown`, `worktree`, `cherry`, `parallel`, `convention`, `extract`, `regex`, `match`, `planner`, `template`, `rule`, `lessons`, `plan`, `observability`, `counter`, `loop`, `after`, `phase`, `denials`, `exemption`.

These generic shared-vocabulary terms were the primary driver of v1's 6/6 false-positive rate.

---

## 2. Per-Source Matching Rules

Three sources, each with tightened thresholds using only v2 high-distinctiveness terms.

### Git Log

- **Pre-filter:** subject matches `CLOSURE_SIGNAL_RE` (unchanged from v1)
- **Threshold:** ≥ 1 high-distinctiveness term from the Open entry's fingerprint appears as substring in the commit subject (lowercased)
- **Change from v1:** threshold lowered from ≥ 2 to ≥ 1. The v2 fingerprint is much smaller and each surviving term is individually meaningful; a single high-distinctiveness match (e.g., `_extract_plan_required_deposits` in a commit subject) is strong evidence of topic overlap.

### PROJECT_STATUS

- **Pre-filter:** date within window, has Reference slug (unchanged from v1)
- **Slug tokenization:** `tokenize_slug()` unchanged (tokens ≥ 3 chars from slug body)
- **Threshold:** ≥ 1 slug token where `len(token) >= 6` appears as substring in entry `text[:300]` (lowercased)
- **Change from v1:** added `len >= 6` floor on qualifying slug tokens; threshold lowered from ≥ 2 to ≥ 1. Short tokens (`mcp`, `set`, `list`, `read`, `class`, `tools`) are excluded from matching, reducing noise from generic slug fragments.

### BACKLOG Closed

- **Pre-filter:** all entries, no date window (unchanged from v1)
- **Threshold:** ≥ 1 high-distinctiveness term from the Open entry's fingerprint appears as substring in the Closed entry's `text[:300]`, AND the matching term satisfies either:
  - **(a)** `len(term) >= 12` — the term is long enough to be structurally distinctive on its own, OR
  - **(b)** the term is a backtick-delimited identifier present in both the Open entry's `text[:500]` and the Closed entry's `text[:300]`
- **Change from v1:** replaced `len(matching) >= 2 and any(len(t) >= 8 for t in matching)` with this new rule. The length floor increases from 8 to 12 for condition (a); the count floor decreases from 2 to 1. Condition (b) provides a path for shorter-but-distinctive identifiers that appear in backticks in both entries.

---

## 3. FP Validation Against 6 Currently-Open Entries

For each Open entry from the v1 live run, the v2 fingerprint is computed and every v1-flagged candidate is re-evaluated under v2 rules.

### Entry 1: Worktree teardown cherry-pick conflict on dirty `PROJECT_STATUS.md`

**Filed:** 2026-05-22

**V2 fingerprint (key terms):** `project_status.md` (backtick, 17), `sequential-planner-edit` (hyphenated, 23), `parallel-diagnostic` (hyphenated, 21)

| V1 Candidate | V1 Match Terms | V2 Outcome | Reason |
|---|---|---|---|
| **[git]** `d2e07a9` research(bellows): BACKLOG freshness-check... | project, project\_status, status | **DROPPED** | All title words; `project_status.md` not substring of subject (subject has `PROJECT_STATUS` without `.md`) |
| **[backlog\_closed]** 2026-05-10 — `_teardown_worktree` cherry-pick fragility | cherry, cherry-pick, teardown, worktree | **DROPPED** | All title words or hyphenated < 12 (`cherry-pick` = 11) |
| **[backlog\_closed]** 2026-05-06 — BACKLOG #1 (`deposit_exists` gate...) | project, worktree | **DROPPED** | Both title words |
| **[backlog\_closed]** 2026-05-04 — monorepo-worktree-at-governance-root... | project, worktree | **DROPPED** | Both title words |
| **[backlog\_closed]** 2026-05-03 — worktree teardown crash | teardown, worktree | **DROPPED** | Both title words |

**V2 result: 0/5 candidates survive → no-match ✓**

---

### Entry 2: Parallel-diagnostic cherry-pick conflicts on shared bookkeeping files

**Filed:** 2026-05-22

**V2 fingerprint (key terms):** `project_status.md` (backtick, 17), `agent-prompt-feedback.md` (backtick, 25), `parallel-diagnostic` (hyphenated, 21), `invoice-pulse` (hyphenated, 13)

| V1 Candidate | V1 Match Terms | V2 Outcome | Reason |
|---|---|---|---|
| **[backlog\_closed]** 2026-05-26 — Teardown push silently fails... | diagnostic, teardown | **DROPPED** | Both title words; no v2 fingerprint term in closed text |
| **[backlog\_closed]** 2026-05-21 — `_consume_verdicts` did not drain... | diagnostic, files | **DROPPED** | Both title words |
| **[backlog\_closed]** 2026-05-12 — bellows-self parallel/concurrent... | diagnostic, parallel | **DROPPED** | Both title words; `parallel-diagnostic` not in closed text (entry says `parallel/concurrent`) |
| **[backlog\_closed]** 2026-05-10 — Stranded plan/verdict files in invoice-pulse... | diagnostic, files, invoice-pulse | **SURVIVES** | `invoice-pulse` (13 ≥ 12) appears in closed text ✓ |
| **[backlog\_closed]** 2026-05-10 — `_teardown_worktree` cherry-pick fragility | cherry, cherry-pick, diagnostic, teardown | **DROPPED** | All title words or < 12 |
| **[backlog\_closed]** 2026-05-10 — deposit\_exists / rule\_20\_self\_check gate... | diagnostic, teardown | **DROPPED** | Both title words |
| **[backlog\_closed]** 2026-05-06 — BACKLOG #1 (`deposit_exists` gate...) | diagnostic, files | **DROPPED** | Both title words |
| **[backlog\_closed]** 2026-05-03 — worktree teardown crash | diagnostic, teardown | **DROPPED** | Both title words |

**V2 result: 1/8 candidates survive → investigate-as-shipped (FP)**
**FP cause:** shared project name `invoice-pulse` — both entries reference the same project but describe different issues (cherry-pick conflicts vs stranded files).

---

### Entry 3: Bellows status UI — replace terminal-only output

**Filed:** 2026-05-21

**V2 fingerprint (key terms):** `terminal-only` (hyphenated, 13), `bellows.db` (backtick, 10)

| V1 Candidate | V1 Match Terms | V2 Outcome | Reason |
|---|---|---|---|
| **[git]** `d2e07a9` research(bellows): BACKLOG freshness-check... | bellows, status | **DROPPED** | Both title words; no v2 fingerprint term in subject |
| **[backlog\_closed]** 2026-05-12 — Terminal output redesign... | output, terminal | **DROPPED** | Both title words; `terminal-only` not in closed text (says `Terminal output`) |
| **[backlog\_closed]** 2026-05-11 — Daemon code-version observability gap | bellows, observability | **DROPPED** | Both title words |

**V2 result: 0/3 candidates survive → no-match ✓**

---

### Entry 4: Deposits parser does not strip parenthetical qualifiers

**Filed:** 2026-05-21

**V2 fingerprint (key terms):** `_extract_plan_required_deposits` (backtick + underscore, 31), `_gate_deposit_exists` (backtick + underscore, 20), `gates.py:380` (backtick, 12), `gates.py:323` (backtick, 12), `backtick-only` (hyphenated, 13)

| V1 Candidate | V1 Match Terms | V2 Outcome | Reason |
|---|---|---|---|
| **[git]** `4e805fa` fix(gates): \_extract\_plan\_required\_deposits set→list... | \_extract\_plan\_required\_deposits, deposits | **SURVIVES** | `_extract_plan_required_deposits` in subject ✓ (git threshold: ≥ 1) |
| **[git]** `a5b9a33` docs: close Priority 3 carry-over audit... | audit, priority | **DROPPED** | Both title words; no v2 fingerprint term in subject |
| **[project\_status]** 2026-05-25 — executable-extract-plan-required-deposits-set-to-list | deposits, extract, plan, required | **SURVIVES** | Token `extract` (7 ≥ 6) is substring of `_extract_plan_required_deposits` in entry text ✓ |
| **[project\_status]** 2026-05-27 — executable-deposit-exists-path-form-normalization | deposit, exists, path | **SURVIVES** | Token `deposit` (7 ≥ 6) is substring of `_extract_plan_required_deposits` in entry text ✓ |
| **[backlog\_closed]** 2026-05-26 — \_extract\_plan\_required\_deposits() returns a set | \_extract\_plan\_required\_deposits, deposits | **SURVIVES** | `_extract_plan_required_deposits` (31 ≥ 12) in closed text ✓ |
| **[backlog\_closed]** 2026-05-11 — deposit\_exists Cause 5... | \_extract\_plan\_required\_deposits, deposits | **SURVIVES** | `_extract_plan_required_deposits` (31 ≥ 12) in closed text ✓ |
| **[backlog\_closed]** 2026-04-28 — BACKLOG #5 (deposit parser gap...) | deposits, parser | **DROPPED** | v1 terms were title words; closed entry likely doesn't contain `_extract_plan_required_deposits` (v1 didn't match on it) |
| **[backlog\_closed]** 2026-04-19 — deposit-path parser false positives | \_extract\_plan\_required\_deposits, deposits, parser | **SURVIVES** | `_extract_plan_required_deposits` (31 ≥ 12) in closed text ✓ (v1 matched on this term) |

**V2 result: 6/8 candidates survive → investigate-as-shipped (FP)**
**FP cause:** shared function name `_extract_plan_required_deposits` (31 chars) — this identifier appears in both the Open entry (about parenthetical qualifier stripping) and multiple Closed entries/commits (about the set→list ordering bug and other deposit parser issues). These are different bugs in the same function.

---

### Entry 5: No-match verdict warning rate-limit

**Filed:** 2026-05-21

**V2 fingerprint (key terms):** `_consume_verdicts` (backtick + underscore, 17), `bellows.py:1280` (backtick, 14), `bellows.py:1278` (backtick, 14), `verdict-pending` (hyphenated, 15)

| V1 Candidate | V1 Match Terms | V2 Outcome | Reason |
|---|---|---|---|
| **[git]** `a5b9a33` docs: close Priority 3 carry-over audit... | audit, priority | **DROPPED** | Both title words |
| **[project\_status]** 2026-05-25 — executable-file-change-audit-fix | audit, file | **DROPPED** | Token `change` (6 ≥ 6) unlikely in entry text; `audit` (5) and `file` (4) below threshold |
| **[project\_status]** 2026-05-21 — executable-bellows-verdict-enrichment | bellows, verdict | **SURVIVES** | Token `bellows` (7 ≥ 6) is substring of `bellows.py:1280` in entry text ✓ |
| **[backlog\_closed]** 2026-05-26 — Step 2 gate\_failure pause...verdict-pending | verdict, verdict-pending | **SURVIVES** | `verdict-pending` (15 ≥ 12) in closed text (`verdict-pending-*`) ✓ |
| **[backlog\_closed]** 2026-05-26 — Daemon-restart recovery shape | match, resolved/, verdict | **DROPPED** | No v2 fingerprint term ≥ 12 in first 300 chars of closed text |
| **[backlog\_closed]** 2026-05-21 — `_consume_verdicts` did not drain... | \_consume\_verdicts, resolved/, verdict | **SURVIVES** | `_consume_verdicts` (17 ≥ 12) in closed text ✓ |
| **[backlog\_closed]** 2026-05-10 — S3 Bug C — stale-verdict check | \_consume\_verdicts, verdict | **SURVIVES** | `_consume_verdicts` (17 ≥ 12) in closed text ✓ |
| **[backlog\_closed]** 2026-05-10 — Plan filename not flipped verdict-pending | verdict, verdict-pending | **SURVIVES** | `verdict-pending` (15 ≥ 12) in closed text ✓ |
| **[backlog\_closed]** 2026-04-24 — Reliability bugs 1, 2, 3 | \_consume\_verdicts, match, verdict | **SURVIVES** | `_consume_verdicts` (17 ≥ 12) in closed text ✓ |

**V2 result: 6/9 candidates survive → investigate-as-shipped (FP)**
**FP causes:** (1) shared function name `_consume_verdicts` — same function referenced by different bugs (drain failure, stale-verdict check, reliability bugs vs rate-limiting). (2) Shared lifecycle term `verdict-pending` — different entries about the verdict lifecycle share this compound. (3) Slug-token collision: `bellows` appears as substring of `bellows.py:1280` in the entry text.

---

### Entry 6: `_extract_step_text` regex case-sensitivity

**Filed:** 2026-05-13

**V2 fingerprint (key terms):** `_extract_step_text` (backtick + underscore, 18), `case-sensitivity` (hyphenated, 16), `re.ignorecase` (backtick, 13)

| V1 Candidate | V1 Match Terms | V2 Outcome | Reason |
|---|---|---|---|
| **[project\_status]** 2026-05-26 — executable-planner-template-rule-21-contract-change | planner, rule, template | **DROPPED** | No token ≥ 6 in entry text[:300] (`planner`, `template`, `contract` absent from entry) |
| **[project\_status]** 2026-05-25 — executable-extract-plan-required-deposits-set-to-list | extract, plan | **SURVIVES** | Token `extract` (7 ≥ 6) is substring of `_extract_step_text` in entry text ✓ |
| **[project\_status]** 2026-05-21 — executable-planner-template-rule-25-codification | planner, rule, template | **DROPPED** | No qualifying token in entry text |
| **[project\_status]** 2026-05-21 — executable-planner-template-no-push-and-routing-count | planner, template | **DROPPED** | No qualifying token in entry text |
| **[project\_status]** 2026-05-13 — executable-plan-write-time-lessons-reread | lessons, plan | **SURVIVES** | Token `lessons` (7 ≥ 6) appears in entry text (Entry mentions "Lessons Forge proposal") ✓ |
| **[backlog\_closed]** 2026-05-11 — deposit\_exists Cause 5 — convention mismatch | convention, extract, regex | **DROPPED** | v1 terms were title words; `_extract_step_text` (18 ≥ 12) not in closed text (entry is about `deposit_exists`) |

**V2 result: 2/6 candidates survive → investigate-as-shipped (FP)**
**FP cause:** slug-token substring collision. `extract` (from the set-to-list slug) matches `_extract_step_text` in the entry text. `lessons` (from the lessons-reread slug) matches `Lessons Forge proposal` in the entry text. Both are incidental substring overlaps, not topic matches.

---

### Section 3 Summary

| Entry | V1 Candidates | V2 Survivors | V2 Status | FP Cause |
|---|---|---|---|---|
| 1 — worktree teardown | 5 | 0 | **no-match** ✓ | — |
| 2 — parallel-diagnostic | 8 | 1 | **FP** | Shared project name (`invoice-pulse`) |
| 3 — status UI | 3 | 0 | **no-match** ✓ | — |
| 4 — deposits parser | 8 | 6 | **FP** | Shared function name (`_extract_plan_required_deposits`) |
| 5 — rate-limit | 9 | 6 | **FP** | Shared function name + lifecycle term |
| 6 — case-sensitivity | 6 | 2 | **FP** | Slug-token substring collision |
| **Totals** | **39** | **15** | **4/6 FP** | |

**V2 reduces from 6/6 to 4/6 false-positive entries and from 39 to 15 total candidates.** The target of zero false positives is not achieved. The residual FPs are inherent to substring-matching approaches when entries share high-distinctiveness identifiers (function names, project names) but describe different issues. These are not threshold-tunable — tightening thresholds would regress ground-truth catches.

**Residual FP categories:**
1. **Same-function-different-bug** (Entries 4, 5): `_extract_plan_required_deposits` and `_consume_verdicts` each appear in both an Open entry and Closed entries about different bugs in the same function. No term-matching threshold can distinguish these.
2. **Shared project name** (Entry 2): `invoice-pulse` identifies the project, not the specific issue.
3. **Slug-token substring collision** (Entry 6): slug tokens (`extract`, `lessons`) are substrings of unrelated terms in the entry text.

---

## 4. Ground-Truth Re-Validation Against 4 Recurrences

### Case 1 — set→list (`_extract_plan_required_deposits`)

**Open entry text (hypothetical):** `_extract_plan_required_deposits()` returns a `set` making `md_paths[0]` hash-dependent

**V2 fingerprint:** `_extract_plan_required_deposits` (backtick 31 + underscore 31), `md_paths[0]` (backtick 10), `hash-dependent` (hyphenated 14)

**Git — CAUGHT ✓**
- Commit `4e805fa`: `fix(gates): _extract_plan_required_deposits set→list — deterministic md_paths[0] selection — closes BACKLOG capability`
- `CLOSURE_SIGNAL_RE` passes (`closes BACKLOG` ✓)
- `_extract_plan_required_deposits` in lowered subject ✓ → score ≥ 1 ✓

**PROJECT_STATUS — CAUGHT ✓**
- Slug: `executable-extract-plan-required-deposits-set-to-list-2026-05-25`
- Tokens ≥ 6: `extract` (7), `required` (8), `deposits` (8)
- `extract` in entry text (within `_extract_plan_required_deposits`) ✓ → score ≥ 1 ✓

**BACKLOG Closed — not needed (already caught by Git + PS)**

---

### Case 2 — precondition-failure verdict-request field

**Open entry text (hypothetical):** Step-counter loop after precondition-failure verdict

**V2 fingerprint:** `precondition-failure` (hyphenated 20), `step-counter` (hyphenated 12)

**Git — NOT CAUGHT (correct)**
Ship commit `0a90e26` lacks `closes BACKLOG` / `backlog hygiene` closure signal.

**PROJECT_STATUS — NOT CAUGHT (correct)**
No relevant PS entry within window.

**BACKLOG Closed — CAUGHT ✓**
- Closed entry: "Step-counter loop after precondition-failure verdict (originally 2026-05-21). Shipped via executable-precondition-failure-field-2026-05-24..."
- `precondition-failure` (20 ≥ 12) in closed text ✓
- `step-counter` (12 ≥ 12) in closed text ✓
- Condition (a) satisfied: term ≥ 12 ✓

---

### Case 3 — Phase 3b read-side step-state-resume

**Open entry text (hypothetical):** Phase 3b step-state-resume (DB read-side)

**V2 fingerprint:** `step-state-resume` (hyphenated 17)

**Git — NOT CAUGHT (correct)**
Ship event was 2026-05-01, outside 14-day window.

**PROJECT_STATUS — NOT CAUGHT (correct)**
No PS entry within window references Phase 3b.

**BACKLOG Closed — CAUGHT ✓**
- Closed entry: "Phase 3b/3c DB step-state-resume slug-collision..."
- `step-state-resume` (17 ≥ 12) in closed text ✓
- Condition (a) satisfied ✓

**Note:** This is the thinnest catch — only one qualifying fingerprint term. The v2 fingerprint for this entry is sparse because "Phase 3b" (no backtick, no hyphenation, no underscore) and "read-side" (9 chars < 12) are excluded.

---

### Case 4 — mcp\_\_vexp\_\_ READ\_CLASS\_TOOLS extension

**Open entry text (hypothetical):** MCP tool denials (`mcp__vexp__run_pipeline`, `mcp__vexp__get_context_capsule`) not on `READ_CLASS_TOOLS` exemption list

**V2 fingerprint:** `mcp__vexp__run_pipeline` (backtick 22 + underscore 22), `mcp__vexp__get_context_capsule` (backtick 30 + underscore 30), `read_class_tools` (backtick 16 + underscore 16)

**Git — CAUGHT ✓**
- Commit `9473cf7`: `fix(gates): extend READ_CLASS_TOOLS with 5 vexp read-class tools — closes BACKLOG mcp_tool_denials`
- `CLOSURE_SIGNAL_RE` passes ✓
- `read_class_tools` in lowered subject (`read_class_tools` ✓) → score ≥ 1 ✓

**PROJECT_STATUS — NOT CAUGHT (regression from v1, non-critical)**
- Slug: `executable-mcp-read-class-tools-extension-2026-05-25`
- Tokens ≥ 6: `extension` (9) only. Other tokens: `mcp` (3), `read` (4), `class` (5), `tools` (5) — all below 6-char floor.
- `extension` in entry text[:300]? Entry says "exemption list" not "extension." Score = 0 < 1. **Miss.**
- V1 caught this via 4 tokens ≥ 3 (`mcp`, `read`, `class`, `tools`) as substrings; v2's 6-char floor excludes them all.
- **Impact: none.** Case 4 is already caught by Git. The PS channel is lost but the entry would still be flagged.

---

### Ground-Truth Summary

| Case | Git | PS | Closed | Caught? | V2 Regression? |
|---|---|---|---|---|---|
| 1 — set-to-list | ✓ (`_extract_plan_required_deposits`) | ✓ (`extract`, `required`, `deposits`) | n/a | **Yes** | No |
| 2 — precondition-failure | — | — | ✓ (`precondition-failure` 20, `step-counter` 12) | **Yes** | No |
| 3 — Phase 3b | — | — | ✓ (`step-state-resume` 17) | **Yes** | No |
| 4 — mcp\_\_vexp\_\_ | ✓ (`read_class_tools`) | **MISS** (no token ≥ 6 matches) | n/a | **Yes** | PS channel lost; Git compensates |

**All 4 ground-truth cases still caught.** Case 4 has a PS regression (tokens below 6-char floor) but remains caught via Git.

---

## 5. Implementation-Edit Guidance

### Functions to Modify

**`extract_fingerprint()` (lines 52–68) — rewrite body:**

Current 4 extraction blocks become:

```python
def extract_fingerprint(text):
    """Extract high-distinctiveness terms from entry text for matching."""
    terms = set()
    # Rule 1: Backtick-delimited identifiers (length >= 5)
    for m in re.finditer(r'`([^`]+)`', text[:500]):
        cleaned = m.group(1).strip('()').lower()
        if len(cleaned) >= 5:
            terms.add(cleaned)
    # Rule 2: Hyphenated compounds (total length >= 12)
    for m in re.finditer(r'\b([a-zA-Z][\w]*(?:-[a-zA-Z][\w]*){1,})\b', text[:300]):
        compound = m.group(1).lower()
        if len(compound) >= 12:
            terms.add(compound)
    # Rule 3: Underscore identifiers (length >= 8, >= 2 underscores)
    for m in re.finditer(r'\b(_?[a-z][a-z0-9]*(?:_[a-z0-9]+)+)\b', text[:300],
                         re.IGNORECASE):
        ident = m.group(1).lower()
        if len(ident) >= 8 and ident.count('_') >= 2:
            terms.add(ident)
    # Rule 4: Executable slugs cited in text
    for m in re.finditer(r'(executable-[\w-]+-\d{4}-\d{2}-\d{2})', text[:500]):
        terms.add(m.group(1).lower())
    # Title-word matching: REMOVED
    return terms
```

**`find_candidates()` (lines 149–176) — modify matching thresholds:**

```python
def find_candidates(open_entries, closure_commits, ps_entries, closed_entries):
    for entry in open_entries:
        candidates = []
        fp = entry['fingerprint']
        text_300 = entry['text'][:300]
        # Source 1: Git log — threshold >= 1 (was >= 2)
        for sha, subject in closure_commits:
            if score_overlap(fp, subject) >= 1:
                matching = sorted(t for t in fp if t in subject.lower())
                candidates.append(("git", sha, subject, matching))
        # Source 2: PROJECT_STATUS — slug tokens >= 6 chars, threshold >= 1 (was >= 2)
        for ps in ps_entries:
            if ps['slug']:
                slug_tokens = tokenize_slug(ps['slug'])
                text_lower = text_300.lower()
                overlap = sorted(t for t in slug_tokens
                                 if len(t) >= 6 and t in text_lower)
                if len(overlap) >= 1:
                    candidates.append(("project_status", ps['date'],
                                       ps['slug'], overlap))
        # Source 3: BACKLOG Closed — new v2 rule
        for closed in closed_entries:
            closed_text = closed['text'][:300]
            matching = sorted(t for t in fp if t in closed_text.lower())
            long_match = any(len(t) >= 12 for t in matching)
            # Backtick-id condition: same backtick identifier in both entries
            backtick_match = False
            if matching and not long_match:
                open_bt = {m.group(1).strip('()').lower()
                           for m in re.finditer(r'`([^`]+)`', entry['text'][:500])
                           if len(m.group(1).strip('()')) >= 5}
                closed_bt = {m.group(1).strip('()').lower()
                             for m in re.finditer(r'`([^`]+)`', closed_text)
                             if len(m.group(1).strip('()')) >= 5}
                backtick_match = bool(
                    open_bt & closed_bt & set(matching))
            if matching and (long_match or backtick_match):
                candidates.append(("backlog_closed", closed['date'],
                                   closed['text'][:80].replace('\n', ' '),
                                   matching))
        entry['candidates'] = candidates
        entry['action'] = "investigate-as-shipped" if candidates else "no-match"
```

### Constants to Remove

- **`STOPWORDS`** (lines 45–49): delete entirely. No longer referenced by `extract_fingerprint()`.

### What Stays Identical

- **Parsing functions:** `parse_open_entries()`, `parse_closed_entries()`, `parse_ps_entries()`, `get_closure_commits()` — unchanged
- **Regexes:** `OPEN_ENTRY_RE`, `CLOSED_ENTRY_RE`, `PS_ENTRY_RE`, `GIT_LINE_RE`, `CLOSURE_SIGNAL_RE`, `REFERENCE_SLUG_RE` — unchanged
- **Utilities:** `score_overlap()`, `tokenize_slug()` — unchanged
- **Output:** `generate_report()` — unchanged
- **CLI:** `main()`, argparse setup, constants (`BELLOWS_ROOT`, `BACKLOG_PATH`, etc.) — unchanged
- **Script structure:** shebang, module docstring, `__main__` guard — unchanged

### Constraints

- Algorithm-only change. No parsing, output, or CLI modifications.
- Python stdlib only. No new dependencies.
- Net LOC delta: approximately -5 (remove STOPWORDS + title-word block, add executable-slug block + backtick-id condition).

---

## Output Receipt

**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done

Produced a 5-section v2 blueprint for the freshness-check algorithm. Section 1 specifies 4 extraction rules (backtick ≥ 5, hyphenated ≥ 12, underscore ≥ 8 with ≥ 2 underscores, executable slugs) with title-word matching dropped. Section 2 redefines per-source matching thresholds. Section 3 traces all 39 v1 candidates through v2 rules — 15 survive across 4 of 6 entries (down from 39 across 6 of 6). Section 4 confirms all 4 ground-truth cases still caught (Case 4 loses its PS channel but retains Git catch). Section 5 provides line-level edit guidance for `scripts/check_backlog_freshness.py`.

### Files Deposited

- `knowledge/research/freshness-check-algorithm-v2-blueprint-2026-05-27.md` — this blueprint

### Files Created or Modified (Code)

- None (blueprint only, no code changes)

### Decisions Made

- **4/6 FP rate (not zero):** the v2 rules as specified cannot achieve zero FPs because entries sharing high-distinctiveness identifiers (same function name, same project name) across different bugs are inherently indistinguishable to term matching. Tightening thresholds would regress ground-truth catches.
- **Case 4 PS regression accepted:** the 6-char slug-token floor excludes all qualifying tokens for the `mcp-read-class-tools-extension` slug. The Git channel compensates, so the case is still caught. Lowering the floor to 5 would restore PS but re-introduce noise from short generic tokens.
- **Backtick-id condition on Closed matching:** condition (b) was specified as written ("same backticked identifier in both entries"). In current data, all matching terms that qualify as backtick identifiers also exceed 12 chars, so condition (b) is currently redundant with condition (a). It provides future coverage for shorter distinctive identifiers.

### Flags for CEO

- **Target zero FPs not achieved.** V2 reduces false positives from 6/6 to 4/6 entries and from 39 to 15 candidates. Remaining FPs are caused by shared function names (`_extract_plan_required_deposits`, `_consume_verdicts`), shared project names (`invoice-pulse`), and slug-token substring collisions (`extract`, `lessons`). These are inherent to any term-matching approach; eliminating them would require semantic understanding of whether two entries describe the same bug.
- **All 4 ground-truth catches preserved.** No regression in true-positive detection.

### Flags for Next Step

- DEV implementing from this blueprint should apply the code from Section 5 as a scoped edit of `extract_fingerprint()` and `find_candidates()` only.
- The backtick-id condition in the Closed matching rule adds ~8 LOC of complexity for a currently-redundant path. If CEO prefers simplicity, condition (b) can be dropped and the Closed rule simplified to just `any(len(t) >= 12 for t in matching)`.
- A live run after v2 implementation will reveal any NEW false positives from v2's different fingerprint terms matching Closed entries that v1 didn't flag. Section 3 only traces v1-flagged candidates; new candidates are possible.
