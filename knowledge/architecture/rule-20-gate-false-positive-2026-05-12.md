# SA Findings — `_gate_rule_20_self_check` False Positive (2026-05-12)

**Date:** 2026-05-12
**Scope:** Diagnostic — investigation only, no code or governance changes
**Trigger:** Gate produced false positive on Step 2 (QA) of `executable-bellows-self-exposure-wontfix-close-2026-05-12`; Planner override via Rule 22 posted

---

## Q1 — Trace of `_gate_rule_20_self_check` Against 2026-05-12 Inputs

**Inputs:** plan file = `Done/executable-bellows-self-exposure-wontfix-close-2026-05-12.md`, QA report = `knowledge/qa/bellows-self-exposure-wontfix-close-qa-2026-05-12.md`, `project_path` = `wt_path` = `/Users/marklehn/Desktop/GitHub/bellows` (bellows-self, no worktree).

### Step-by-step trace through `gates.py`

1. **Line 303 — `is_qa_step` guard.** `_gate_is_qa_step` (line 351-357) strips fenced code blocks from plan text, finds `## STEP 2 — QA` (plan file line 32), confirms `"qa"` is in the lowercased header. Returns `True`. Gate proceeds.

2. **Line 306 — `_extract_step_text(plan_text, 2)`.** Calls `_extract_step_text` (lines 253-262). Line 259 applies `strip_fenced_code_blocks()` to the full plan text — the plan has no top-level fenced code blocks, so the text is unchanged. Line 260-261 regex `^## STEP 2\b.*?(?=^## STEP |\Z)` matches from plan line 32 (`## STEP 2 — QA`) through end of file (line 40). Returns the full Step 2 text (lines 32-40).

3. **Line 310 — `_extract_plan_required_deposits(step_text)`.** Calls `_extract_plan_required_deposits` (lines 265-298).

   - **Line 274 — Block regex:** `r'[> ]*\*\*Deposits:\*\*\s*\n(?:[> ]*\n)*((?:[> ]*-\s+.*\n?)+)'`. The step text contains `**Deposits:**` on plan line 38, but the deposit bullets are on the **same line** as the `**Deposits:**` marker (inline comma-separated format: `` **Deposits:** `- /path/a`, `- /path/b`. ``). The regex requires `\s*\n` (a newline) immediately after `**Deposits:**` before looking for bullet lines. **No match.** `block_match` is `None`.

   - **Lines 283-298 — Legacy fallback patterns:**
     - Pattern 1 (line 286): `Deposit[^\n`]*?to\s+\`([^\`]+)\`` — looks for `Deposit...to \`path\`` prose. The inline format uses `**Deposits:** \`- /path\`` which does not contain the word `to` between `Deposit` and the backticked path. **No match.**
     - Pattern 2 (line 290): `Deposit[^\n]*?to\s+(\S+\.md)` — same reason. **No match.**
     - Pattern 3 (line 296): `with open(...)` — not present. **No match.**

   - **Returns empty set `{}`.**

4. **Line 311 — `md_paths` filter.** `[p for p in {} if p.endswith(".md")]` → empty list `[]`.

5. **Line 312-313 — Empty `md_paths` branch.** `if not md_paths:` is `True`. Appends failure: `{"gate": "rule_20_self_check", "evidence": "no QA deposit contains Rule 20 self-check banner"}`. **Returns immediately.**

**The gate never reaches the file-reading logic (lines 319-348).** It fails at line 313 because `_extract_plan_required_deposits` returned an empty set. The QA report file — which exists, contains the correct banner at line 26, and has `PASSED — SELF-CHECK PASSED` at line 28 — was never opened or searched.

---

## Q2 — Proximate Cause Classification

**Root cause: (a) Deposit enumeration parser issue.**

The `_extract_plan_required_deposits` function's block regex at **line 274** of `gates.py` requires a newline (`\s*\n`) after the `**Deposits:**` marker before scanning for bullet lines. The 2026-05-12 wontfix-close plan uses an **inline format** where the deposit bullets appear on the **same line** as `**Deposits:**`, comma-separated and individually backtick-wrapped (`` **Deposits:** `- /path/a`, `- /path/b`. ``). The regex does not match this format. The three legacy fallback patterns (lines 286, 290, 296) also do not match because they look for `Deposit...to` prose or `with open(...)` Python patterns, neither of which appears in the inline format.

The failing logic is concentrated at line 274. The inline format bypasses both the block parser and all legacy fallback patterns, yielding an empty deposit set. The `_gate_rule_20_self_check` function then concludes — correctly given its empty input — that no QA deposit was declared, and reports failure.

Causes (b), (c), and (d) are ruled out:
- **(b) Fence-strip false negative:** `_gate_rule_20_self_check` does **not** apply `strip_fenced_code_blocks()` before banner search (line 332 searches raw file `content`). Although the banner IS inside a fenced block in the QA report (lines 24-31), the gate would have found it via substring match — if it had ever read the file. It never did.
- **(c) Path resolution drift:** `_resolve_deposit_path` was never called because the deposit set was empty. The worktree-aware path resolution (line 205, `wt_path != project_path` guard) is a no-op here because `wt_path == project_path` for bellows-self plans.
- **(d) Other:** Not applicable.

---

## Q3 — Population Check

### Bellows QA Reports (10 most recent by mtime)

| # | QA Report | Banner in Fence? | Corresponding Plan Step 2 Deposits Format |
|---|---|---|---|
| 1 | bellows-self-exposure-wontfix-close-qa-2026-05-12 | Yes (lines 24-31) | **Inline** (same line as `**Deposits:**`) |
| 2 | backlog-2026-04-19-plan-fixing-bug-x-hygiene-close-qa-2026-05-12 | Yes | Multi-line |
| 3 | terminal-notification-backlog-close-qa-2026-05-12 | Yes | Multi-line |
| 4 | notification-coalescing-qa-2026-05-12 | Yes | Multi-line |
| 5 | terminal-capture-qa-2026-05-12 | Yes | Multi-line |
| 6 | path-001-hygiene-close-qa-2026-05-11 | Yes | Multi-line |
| 7 | daemon-version-observability-qa-2026-05-11 | Yes | Multi-line |
| 8 | planner-template-parser-self-trip-and-session-wrap-qa-2026-05-11 | Yes | Multi-line |
| 9 | plan-handler-seen-slug-refactor-qa-2026-05-11 | Yes | Multi-line |
| 10 | backlog-append-fix-plan-trips-own-bug-qa-2026-05-11 | Yes | Multi-line |

**Bellows summary:** 10/10 banners inside fenced code blocks. 9/10 plans use multi-line Deposits format; 1/10 (the 2026-05-12 wontfix-close) uses inline format. Full grep of all plans in `decisions/Done/` confirms: **every** historical bellows plan uses multi-line Deposits format. The inline format is unique to this plan.

### Invoice-Pulse QA Reports (10 most recent by mtime)

| # | QA Report | Banner in Fence? | Plan Deposits Format |
|---|---|---|---|
| 1 | qa-action-queue-limit-and-contract-name-deliverable-verification-2026-05-08 | No banner | N/A (deliverable verification, not QA) |
| 2 | qa-action-queue-limit-and-contract-name-2026-05-08 | Yes (inside fence) | Legacy prose (no `**Deposits:**` block) |
| 3 | qa-aggregated-queue-customer-display-2026-05-07 | Outside fence | Legacy prose |
| 4–6 | (duplicates of 1–3, `.md 2` copies) | Same as originals | Same |
| 7 | qa-rule-20-banner-fix-verification-2026-05-07 | Outside fence | Legacy prose |
| 8 | qa-action-queue-aggregation-2026-05-07 | Outside fence | Legacy prose |
| 9 | qa-action-queue-aggregation-deliverable-verification-2026-05-07 | No banner | N/A |
| 10 | billto-type-field-mapping-fix-qa-2026-05-07 | No banner | N/A |

**Invoice-pulse summary:** Mixed banner placement (some inside fences, some outside, some absent). Plans use legacy prose deposit format — no `**Deposits:**` blocks. Not directly relevant to this gate trip (different project, different parser path).

### Population Conclusion

The failure shape is **specific to this plan.** The inline Deposits format that triggered the false positive appears in exactly 1 of 30+ bellows plans. No historical bellows plan would have tripped this gate because they all use multi-line format. The inline format is a one-off Planner output variation.

**Latent risk noted:** All 10 bellows QA reports place the Rule 20 banner inside a fenced code block. The gate currently does NOT fence-strip before banner search (line 332), so this works — `banner in content` matches the raw text inside the fences. However, if `strip_fenced_code_blocks()` were ever added to the banner search path (as it was to four other parsers in the 2026-05-11 fence-strip close, commit `4d57fd3`), ALL historical QA reports would produce false negatives. This is candidate cause (b) from the CEO Context — not the proximate cause today, but a latent fragility worth noting.

---

## Q4 — Recommendation

**Primary: (ii) Code fix in `_extract_plan_required_deposits`.**

Modify the block regex at line 274 of `gates.py` to also handle the inline format. Fix shape: add a second branch that matches when `**Deposits:**` is followed by backtick-wrapped paths on the same line (no newline). The branch should extract paths using the existing backtick-extraction regex (`r'-\s+\`([^\`]+)\```, line 278). Estimated change: ~5-8 lines in `_extract_plan_required_deposits`, one new test case in `test_gates.py`.

Rationale: The parser should handle both formats because the Planner is a generative system that may produce either format. Relying solely on a governance constraint (multi-line only) is fragile — the Planner has already deviated once, and the parser is the mechanical check. The code fix makes the gate robust to format variation without imposing a new template constraint.

**Secondary: (i) Governance note (informational, not blocking).** The Planner should prefer multi-line Deposits format for consistency, but this is a soft preference, not a hard constraint worth documenting in PLANNER_TEMPLATE. The code fix eliminates the need for a governance rule.

**Not recommended: (iii) Accept as Rule 22 override class.** While the Rule 22 override worked correctly this time, the override required manual CEO verification and Planner intervention. The underlying parser gap is small and fixable — paying the override cost on every inline-format plan is not worthwhile.

### Layer Impact

| Layer | Impact |
|---|---|
| Layer 1 (Bellows) | Code fix in `_extract_plan_required_deposits` — parser enhancement, no behavioral change for correctly-formatted plans |
| Layer 2 (Agents) | None — agents are downstream of the gate, not upstream |
| Layer 3 (Planner) | Reduced Rule 22 override friction — the Planner no longer needs to override this gate when it emits inline Deposits format |

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Traced `_gate_rule_20_self_check` step-by-step against the 2026-05-12 inputs, identifying the proximate cause as (a) deposit enumeration parser issue: the block regex at `gates.py:274` requires a newline after `**Deposits:**` but the plan uses inline format. Performed population check across 10 bellows and 10 invoice-pulse QA reports confirming the failure is specific to this plan. Recommended a code fix in `_extract_plan_required_deposits` to handle both inline and multi-line formats.

### Files Deposited
- `/Users/marklehn/Desktop/GitHub/bellows/knowledge/architecture/rule-20-gate-false-positive-2026-05-12.md` — SA findings on rule_20_self_check gate false positive

### Files Created or Modified (Code)
- None (investigation only)

### Decisions Made
- Classified proximate cause as (a) deposit enumeration parser issue, ruling out (b) fence-strip, (c) path resolution, and (d) other
- Recommended code fix over governance fix or Rule 22 override acceptance

### Flags for CEO
- None

### Flags for Next Step
- None
