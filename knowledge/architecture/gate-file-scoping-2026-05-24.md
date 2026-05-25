# Gate File-Scoping: Shared Root Cause Analysis for BACKLOG Items #6 and #7

**Date:** 2026-05-25 | **Type:** Diagnostic findings | **Plan:** diagnostic-gate-file-scoping-2026-05-24 | **Step:** 1

---

## Section A — Joint File Resolution (Q1)

### A1. `_gate_rule_22_verification` file resolution

**Function signature:** `gates.py:468`
```python
def _gate_rule_22_verification(is_qa_step, plan_text, step_number, project_path, parsed, failures, wt_path=None):
```

**File-resolution mechanism** — three-stage pipeline, all inside the gate:

1. **Step text extraction** at `gates.py:470`:
   ```python
   step_text = _extract_step_text(plan_text, step_number)
   ```

2. **Deposit enumeration** at `gates.py:474`:
   ```python
   deposit_paths = _extract_plan_required_deposits(step_text)
   ```

3. **Path resolution** at `gates.py:478` (for (a) check) and `gates.py:494` (for (c)/(d) checks):
   ```python
   resolved = _resolve_deposit_path(dep_path, project_path, wt_path=wt_path)
   ```

**QA report selection** at `gates.py:493`:
```python
qa_report_path = md_paths[0]
```
The gate selects the FIRST `.md` deposit path as "the QA report." No other selection logic exists.

### A2. `_gate_rule_20_self_check` file resolution

**Function signature:** `gates.py:414`
```python
def _gate_rule_20_self_check(is_qa_step, plan_text, step_number, project_path, parsed, failures, wt_path=None):
```

**File-resolution mechanism** — identical three-stage pipeline:

1. **Step text extraction** at `gates.py:419`:
   ```python
   step_text = _extract_step_text(plan_text, step_number)
   ```

2. **Deposit enumeration** at `gates.py:423`:
   ```python
   deposit_paths = _extract_plan_required_deposits(step_text)
   ```

3. **Path resolution** at `gates.py:433` (inside iteration loop):
   ```python
   resolved = _resolve_deposit_path(dep_path, project_path, wt_path=wt_path)
   ```

**QA report selection:** NONE. The gate iterates ALL `.md` deposit paths looking for the Rule 20 banner (`gates.py:432`):
```python
for dep_path in md_paths:
```
No single-file selection. All `.md` deposits are scanned.

### A3. Shared vs independent code paths

Both gates use the **exact same** file-resolution helpers:
- `_extract_step_text` at `gates.py:345-354` (shared)
- `_extract_plan_required_deposits` at `gates.py:364-411` (shared)
- `_resolve_deposit_path` at `gates.py:270-308` (shared)

The difference is in how each gate CONSUMES the deposit list:
- Rule 22: picks `md_paths[0]` (first `.md` deposit) as the QA report
- Rule 20: iterates ALL `md_paths` looking for the banner

### A4. Call sites in `bellows.py`

Both gates are invoked indirectly via `gates.check()`. Two call sites:

**`bellows.py:488`** (first-step path):
```python
gate_result = gates.check(parsed, plan_text, current_step, project_path, files_changed=files_changed, wt_path=wt_path)
```

**`bellows.py:579`** (while-loop path):
```python
gate_result = gates.check(parsed, plan_text, current_step, project_path, files_changed=files_changed, wt_path=wt_path)
```

File resolution is done entirely inside `gates.py`. `bellows.py` passes `wt_path` to `check()`, which threads it to both gates:

**`gates.py:180`:**
```python
_gate_rule_20_self_check(is_qa_step, plan_text, step_number, project_path, parsed, failures, wt_path=wt_path)
```

**`gates.py:182`:**
```python
_gate_rule_22_verification(is_qa_step, plan_text, step_number, project_path, parsed, failures, wt_path=wt_path)
```

### A5. Prior fix status

**2026-05-06 worktree-aware fix:** Applied to `_gate_deposit_exists` and `_resolve_deposit_path`. Strategy 0 (worktree-first) added at `gates.py:280-298`.

**2026-05-10 missed-gate fix:** Applied to `_gate_rule_20_self_check`. The `wt_path=None` parameter is present in the signature at `gates.py:414`, and `wt_path=wt_path` is passed to `_resolve_deposit_path` at `gates.py:433`.

**`_gate_rule_22_verification`:** Also has `wt_path=None` in its signature (`gates.py:468`) and passes it correctly at `gates.py:478` and `gates.py:494`. This gate was added after the worktree-aware fixes and was written with `wt_path` from the start.

**2026-05-11 step-text-extraction anchor fix:** Applied. `_extract_step_text` at `gates.py:352` now uses `^` anchor with `re.MULTILINE`:
```python
pattern = rf"^## STEP {step_number}\b.*?(?=^## STEP |\Z)"
match = re.search(pattern, plan_text, re.DOTALL | re.MULTILINE)
```

`_gate_is_qa_step` at `gates.py:545` also anchored:
```python
pattern = rf"^## STEP {step_number}\b[^\n]*"
match = re.search(pattern, plan_text, re.MULTILINE)
```

**Conclusion for A5:** All prior path-resolution and step-text-extraction fixes have been applied. Today's items #6 and #7 are NOT recurrences of the path-resolution gap or the step-text-extraction gap. They are a different class of bug: **content-scoping** (which file/table to inspect), not **path-resolution** (how to find the file on disk).

---

## Section B — Item #6 Mechanism (Q2)

### B6. Table-discovery mechanism in the (c) check

The (c) check at `gates.py:507-528` uses a line-by-line state machine:

```python
in_data = False
for i, line in enumerate(lines, 1):
    stripped = line.strip()
    if "|" not in stripped:
        in_data = False
        continue
    if _TABLE_SEPARATOR_RE.match(stripped):
        in_data = True
        continue
    if not in_data:
        continue  # Header row
    # Data row — check status
```

**Table-type classification: NONE.** The state machine treats EVERY markdown table in the QA report identically. There is no filter for:
- Table section header (e.g., "## Deliverable Verification")
- Column headers (e.g., a "Status" column)
- Table position in the document
- Any other signal that distinguishes verification tables from non-verification tables

Every data row in every table must contain ✅ or ❌, regardless of the table's purpose.

### B7. Row-status check predicate

**`gates.py:519-528`:**
```python
if "\u274c" in stripped:                          # ❌ present → flag as failed row
    failures.append(...)
elif "\u2705" not in stripped:                     # ✅ absent → flag as missing status
    failures.append(...)
```

The (c) check accepts ONLY two status indicators:
- `✅` (U+2705, green check mark) — positive status
- `❌` (U+274C, cross mark) — negative status

It does NOT accept text-based status tokens: "PASS", "OK", "done", "complete", "verified", "N/A". These tokens ARE defined in `POSITIVE_STATUS_TOKENS` at `gates.py:58` and used by `_is_positive_status_row()` at `gates.py:63-76`, but only for the (d) hedging check — NOT for the (c) status check.

### B8. Evidence truncation vs detection truncation

**Evidence output** at `gates.py:522` and `gates.py:527` uses `stripped[:120]`:
```python
"evidence": f"(c) QA verification table row {i} missing status: {stripped[:120]}. See {qa_report_path} line {i}.",
```

The 120-character truncation applies ONLY to the evidence string shown in the verdict request. The **detection logic** at `gates.py:524` uses `stripped` (the full line, no truncation):
```python
elif "\u2705" not in stripped:
```

**The BACKLOG's "truncation before reaching the status column" hypothesis is incorrect as a detection-side explanation.** The gate reads the full row but doesn't recognize "PASS" text as a valid status token. The evidence output's 120-char cap makes the quoted row APPEAR truncated before the status column, which is misleading but not causal.

### B9. 2026-05-22 reproduction: 47 rows flagged

From the processed verdict at `verdicts/resolved/processed-verdict-invoice-pulse-specialist-file-drift-refresh-2026-05-22-step-2.md`:

> "rule_22_verification flagged 47 QA-report-table rows as 'missing status' — every flagged row has `| PASS |` as the final column (visible in the verdict request's own quoted text of each row)."

**Classification:** These 47 rows are in a verification-style table but use text "PASS" instead of ✅ emoji. The gate's (c) check only recognizes ✅ → false positive on all 47 rows. This is a **status-token limitation** issue.

### B9b. 2026-05-24 reproduction context

The diagnostic references a 2026-05-24 case on the pre-scan removal QA that flagged a "failure-classification table (a 3-column table with Test name | Classification | Notes, no status column by design)." The verdict request at `verdicts/pending/archived/verdict-request-remove-pre-scan-processed-rename-v2-2026-05-24-step-2.md` shows `rule_22_verification | PASS`, indicating this specific verdict request passed. The 2026-05-24 occurrence likely manifested on an earlier halted run (the plan had 3 halted predecessor plans per the BACKLOG Closed entry). This is consistent with a **table-type confusion** issue — the QA report for one of the halted predecessors would have had a failure-classification table (not a verification table) that was incorrectly inspected.

### B10. Fix shape for Item #6

The gate has TWO contributing defects:

**(i) Table-type confusion** — the gate inspects ALL tables regardless of purpose. Fix requires scoping to verification-section tables.

**(ii) Status-token limitation** — the (c) check only recognizes ✅/❌ emojis. Text tokens like "PASS" are ignored even though `_is_positive_status_row()` already supports them.

Both defects contribute to false positives. The structural fix must address both. See Section E for concrete fix shapes.

---

## Section C — Item #7 Mechanism (Q3)

### C11. `_gate_rule_20_self_check` file-resolution end-to-end

The gate's file-resolution is correct at the PATH level (worktree-aware since 2026-05-10). The issue is at the CONTENT level — which files the gate chooses to scan.

The gate at `gates.py:414-465`:

1. **QA guard** (`gates.py:416`): `if not is_qa_step: return` — only runs on QA steps.
2. **Step text** (`gates.py:419`): `step_text = _extract_step_text(plan_text, step_number)` — correctly anchored.
3. **Deposit paths** (`gates.py:423`): `deposit_paths = _extract_plan_required_deposits(step_text)` — returns ALL deposits from the step.
4. **Filter to `.md`** (`gates.py:424`): `md_paths = [p for p in deposit_paths if p.endswith(".md")]`.
5. **Iterate ALL `.md` deposits** (`gates.py:432-458`):
   ```python
   for dep_path in md_paths:
       resolved = _resolve_deposit_path(dep_path, project_path, wt_path=wt_path)
       # ... read file, check for banner ...
       if banner not in content:
           continue
       # Banner found — check for PASSED line
       if re.search(PASSED_PATTERN, remaining, re.MULTILINE):
           return  # Gate passes
       banner_found_path = dep_path
   ```

The gate reads EVERY `.md` deposit file. If it finds the banner string `"Rule 20 — QA Self-Check Results"` in ANY file:
- If PASSED line follows → return (gate passes)
- If no PASSED line → set `banner_found_path`, continue to next file

After all files checked, if `banner_found_path` is set → fail with "banner present but PASSED line missing."

### C12. 2026-05-22 reproduction: gate scanned wrong file

From the processed verdict:

> "rule_20_self_check flagged 'banner present but PASSED line missing in invoice-pulse/knowledge/research/agent-prompt-feedback.md'"

**What happened:**

1. The gate's `_extract_plan_required_deposits` returned deposit paths from the step text. The set included `agent-prompt-feedback.md` (at path `invoice-pulse/knowledge/research/agent-prompt-feedback.md`). This file was either explicitly listed in the plan's `**Deposits:**` block or captured by the legacy prose fallback.

2. The gate iterated all `.md` deposit paths. It read `agent-prompt-feedback.md` and found the exact string `"Rule 20 — QA Self-Check Results"` in a feedback entry (likely a feedback entry DESCRIBING prior Rule 20 work, containing the banner text as prose).

3. The gate then searched for the PASSED pattern after the banner. The feedback entry contained the banner text in a descriptive context without a following PASSED line → `banner_found_path` set to the feedback file.

4. The gate then either (a) checked the QA report but didn't find the banner (format mismatch — the CEO notes the QA report uses `RULE 20 SELF-CHECK: PASSED` which does NOT contain the exact string `"Rule 20 — QA Self-Check Results"`), OR (b) the QA report path wasn't in the deposit list, OR (c) the QA report was checked and had banner + PASSED but was checked before the feedback file (this would have caused the gate to PASS — contradicts the failure).

5. Gate concluded with `banner_found_path` set → failure fired.

The original (non-processed) verdict request for the 2026-05-22 case is no longer available in `verdicts/pending/archived/` — only the processed verdict in `verdicts/resolved/` survives. The exact plan text and deposit list cannot be verified from surviving artifacts. However, the mechanism is unambiguous from the code: the gate iterates ALL `.md` deposit paths, and `agent-prompt-feedback.md` was in that set.

### C13. Does the gate parse the `**Deposits:**` block vs heuristic?

The gate uses `_extract_plan_required_deposits(step_text)` at `gates.py:423`, which:

1. **First:** Looks for a `**Deposits:**` block (`gates.py:376`). If found, extracts ONLY backtick-quoted paths from its bullet list.
2. **If no block:** Falls back to legacy prose regexes (`gates.py:396-410`) — "Deposit to `path`", "Deposit to path.md", "with open('path.md', 'w')".

The gate does NOT:
- Parse the verdict request's singular `Deposit:` field
- Iterate files-modified-this-step (`files_changed`)
- Scan any directory for files

The BACKLOG hypothesis "(a) gate iterates all files-modified-this-step looking for Rule 20 banners" is **incorrect**. The gate uses `_extract_plan_required_deposits` against the plan step text, not `files_changed`.

The BACKLOG hypothesis "(b) gate scans for any text matching the Rule 20 banner regex anywhere in any deposit" is **partially correct** — the gate does scan all deposit `.md` files for the banner, but the deposit list comes from the plan step text, not from "any deposit."

### C14. Root cause mechanism for Item #7

The root cause is: **the gate iterates ALL `.md` deposit paths looking for the Rule 20 banner, without scoping to "the QA report" specifically.** When a non-QA file (e.g., `agent-prompt-feedback.md`) is listed as a deposit and happens to contain the exact banner text as incidental prose, the gate matches on it.

Contributing factor: The gate's banner-matching is a literal substring check (`banner not in content` at `gates.py:445`). It cannot distinguish structural banner headers from incidental mentions in prose.

This is a DIFFERENT mechanism from the 2026-05-10 "missed `wt_path` threading" bug. That was about path resolution (the gate couldn't find the file on disk). This is about content scoping (the gate reads the wrong file's content).

---

## Section D — Joint Root Cause Analysis (Q4)

### D15. Are items #6 and #7 surface manifestations of one underlying issue?

**Independent bugs with shared design ancestry.**

Both gates lack a robust concept of "the QA report" as a specific, identified file. But the specific failure mechanisms are distinct:

| Dimension | Item #6 (rule_22 (c)) | Item #7 (rule_20) |
|---|---|---|
| **Bug location** | `gates.py:507-528` (c) check loop | `gates.py:432-458` banner scan loop |
| **Which file?** | Correct file selected (`md_paths[0]`) | Wrong file scanned (iterates ALL `.md` deposits) |
| **What fails?** | Within-file: all tables inspected; ✅-only status check | Cross-file: banner matched in non-QA file |
| **Root cause class** | Content-parsing: no table-type filter + status-token limitation | Content-scoping: no QA-report-specific file selection |

**They do NOT share a common helper, predicate, or design assumption that could be fixed once.** The shared pipeline (`_extract_step_text` → `_extract_plan_required_deposits` → `_resolve_deposit_path`) works correctly for both gates. The bugs are in how each gate CONSUMES the resolved content:
- Rule 22 correctly selects the QA report but incorrectly parses its tables
- Rule 20 incorrectly selects which files to scan but correctly parses banner content

### D16. Cross-reference with 2026-05-10 closed entry

The 2026-05-10 entry identified "`_gate_rule_20_self_check` was missed by the 2026-05-06 worktree-aware fix." That was a **path-resolution gap** (Class 1: missing `wt_path` parameter). It was fixed surgically by threading `wt_path` through the gate.

Today's items are a **different design flaw class** — content-scoping, not path-resolution:
- Item #6 is about WHICH TABLES within a file to inspect (content parsing)
- Item #7 is about WHICH FILES to scan for the banner (content scoping)

The surgical patch pattern from 2026-05-06/2026-05-10 does not apply here. Those patches fixed "gate can't find the file on disk." Today's bugs are "gate finds the file but reads the wrong content within it" (#6) or "gate reads the wrong file entirely" (#7).

### D17. Structural fix vs surgical patches

**For Item #6:** The structural fix requires the (c) check to distinguish verification tables from other table types. This means either scoping to a known section header or checking column headers for a status column. Without this, every new table type added to QA reports will produce false positives.

**For Item #7:** The structural fix requires the Rule 20 gate to scope its banner scan to the QA report specifically, not iterate all deposits. The simplest form: use `md_paths[0]` (like Rule 22 does) instead of iterating all. A more robust form: identify the QA report by naming pattern or by being the first `.md` deposit.

**These are two separate code changes in two separate code regions.** No unified "one fix closes both" design exists, because the bugs operate at different levels (within-file parsing vs cross-file scanning).

---

## Section E — Fix Shapes (Q5)

### E18. Item #6 fix shapes

**Shape 6A: Table-section scoping (structural)**

Scope the (c) check to tables that appear under a verification-section header. Only inspect tables that follow a line matching a verification-section pattern (e.g., `## Deliverable Verification`, `## Verification`, or any `##` header containing "Verification").

- **LOC estimate:** ~15 production + ~20 test
- **Structural vs surgical:** Structural — eliminates false positives from ALL non-verification tables (failure-classification, test result, structural compliance, commit stat, etc.)
- **Interaction with 2026-05-06/2026-05-10 fixes:** None — different code region (content parsing vs path resolution)
- **Regression tests needed:**
  - QA report with verification table (all ✅) + failure-classification table (no status column) → only verification table inspected, gate passes
  - QA report with verification table (has ❌) + other tables → gate correctly flags verification-table failure
  - QA report with no verification section header → fallback behavior (inspect all tables, or skip)

**Shape 6B: Broaden status-token acceptance (surgical)**

Replace the ✅-only check at `gates.py:524` with a call to `_is_positive_status_row()` (already defined at `gates.py:63-76`), which accepts "PASS", "OK", "done", "complete", "verified", and ✅.

- **LOC estimate:** ~5 production + ~10 test
- **Structural vs surgical:** Surgical — handles "PASS" text tokens but doesn't fix table-type confusion. Non-verification tables with no status tokens would still be flagged.
- **Interaction with 2026-05-06/2026-05-10 fixes:** None
- **Regression tests needed:**
  - QA report with "| PASS |" text status (no ✅) → gate passes
  - QA report with "| N/A |" text → behavior decision needed (N/A not currently in `POSITIVE_STATUS_TOKENS`)
  - QA report with empty status cell → gate correctly flags

**Shape 6C: Combined 6A + 6B (structural)**

Apply both table-section scoping AND broadened status-token acceptance.

- **LOC estimate:** ~20 production + ~25 test
- **Structural vs surgical:** Structural — addresses both contributing mechanisms
- **Recommended** — closes the boundary permanently for both table-type confusion and status-token limitation

### E19. Item #7 fix shapes

**Shape 7A: Scope to first `.md` deposit (surgical)**

Change the banner scan loop at `gates.py:432` from iterating all `md_paths` to checking only `md_paths[0]` (the first `.md` deposit, same as Rule 22 uses).

```python
# Current: for dep_path in md_paths:
# Proposed: scan only first .md deposit (the QA report)
qa_report_path = md_paths[0]
```

- **LOC estimate:** ~10 production (refactor loop to single-file check) + ~10 test
- **Structural vs surgical:** Surgical but effective — the first `.md` deposit is the QA report in all observed plan templates. Incidental banner matches in other files are eliminated.
- **Interaction with 2026-05-06/2026-05-10 fixes:** None
- **Regression tests needed:**
  - Plan with QA report (has banner+PASSED) and second `.md` deposit (has banner text without PASSED) → gate passes (reads only QA report)
  - Plan with QA report (has banner+PASSED) only → gate passes (same as today)

**Shape 7B: Scope to first `.md` deposit + banner context check (structural)**

Same as 7A, plus add a structural-context check: the banner must appear at the start of a line or after a header marker (e.g., `^=+\n.*Rule 20` or `^#+.*Rule 20`), not embedded in prose text.

- **LOC estimate:** ~15 production + ~15 test
- **Structural vs surgical:** Structural — eliminates incidental matches even if the QA report itself contains Rule 20 references in prose sections
- **Regression tests needed:**
  - QA report with banner in a `===` block → gate passes
  - QA report with banner mentioned in prose (not as a structural header) → gate correctly ignores the prose mention

### E19b. Unified fix consideration

Both gates would benefit from a shared helper that identifies "the primary QA report deposit" from the deposit list. However, since both gates already select the QA report (Rule 22 at `gates.py:493`, Rule 20 would do so with Shape 7A), factoring a shared helper is optional and can be deferred to a future cleanup pass without blocking either fix.

### E20. Test coverage gaps

**Item #6 — existing test gaps:**

| Gap | Missing test scenario |
|---|---|
| Multi-table QA report | No test uses a QA report with both verification and non-verification tables |
| Text status tokens | No test uses "PASS", "OK", or other text status tokens instead of ✅ |
| Table-type classification | No test verifies that non-verification tables are excluded |

Existing tests that would catch regression: `test_rule_22_qa_all_pass`, `test_rule_22_qa_fail_row`, `test_rule_22_qa_missing_status` — but all use single-table reports with ✅/❌ only.

**Item #7 — existing test gaps:**

| Gap | Missing test scenario |
|---|---|
| Multi-deposit plan | No test uses a plan with multiple `.md` deposits where a non-QA file contains the banner text |
| Incidental banner match | No test verifies that a file containing the banner text in prose (not as a structural header) doesn't trip the gate |

Existing tests that would catch regression: `test_rule_20_self_check_passes_with_valid_banner_and_passed_line`, `test_rule_20_self_check_resolves_via_worktree_path` — but all use single-deposit plans.

---

## Summary Table

| Question | Answer |
|---|---|
| Q1: Shared file resolution? | Yes — both gates use `_extract_step_text` → `_extract_plan_required_deposits` → `_resolve_deposit_path`. Path resolution is correct. Divergence is in content consumption. |
| Q2: Item #6 mechanism? | Two contributing defects: (i) no table-type classification — ALL tables inspected; (ii) ✅-only status check — "PASS" text not recognized. Evidence truncation at 120 chars is cosmetic, not causal. |
| Q3: Item #7 mechanism? | Gate iterates ALL `.md` deposit paths for banner. Non-QA file (`agent-prompt-feedback.md`) contained incidental banner text and was matched. Gate does NOT iterate `files_changed` — uses `_extract_plan_required_deposits` against plan step text. |
| Q4: Shared root cause? | **Independent.** #6 = within-file content-parsing bug (table-type + status-token). #7 = cross-file content-scoping bug (iterates all deposits). Different code regions (`gates.py:507-528` vs `gates.py:432-458`). NOT a recurrence of the 2026-05-10 path-resolution gap. |
| Q5: Fix sequencing? | Independent — can be fixed in either order. Shape 6C (combined table-scoping + status-token broadening) for #6; Shape 7A (scope to first `.md` deposit) for #7. No interaction with worktree-aware fixes. |

---

## Output Receipt

**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Joint characterization of BACKLOG items #6 (`rule_22_verification` (c) false-positive on tables) and #7 (`rule_20_self_check` fires on wrong file). Traced both gates' file-resolution pipelines through `gates.py`, confirming they share the same three-stage path-resolution mechanism (step text → deposit enumeration → path resolution) which works correctly. Identified the bugs as content-level issues, not path-level: Item #6 has no table-type classification and ✅-only status acceptance; Item #7 iterates all `.md` deposit files rather than scoping to the QA report. Confirmed independence (different code regions, different failure mechanisms). Proposed fix shapes with LOC estimates and test coverage gap analysis.

### Files Deposited
- `knowledge/architecture/gate-file-scoping-2026-05-24.md` — full diagnostic findings (Sections A-E) with code citations

### Files Created or Modified (Code)
- None (diagnostic only — no source code changes per plan constraints)

### Decisions Made
- Classified items #6 and #7 as **independent bugs** with shared design ancestry but distinct root causes and distinct code regions
- Determined that neither item is a recurrence of the 2026-05-10 path-resolution gap — both are content-scoping issues, a different class
- Overturned the BACKLOG's "truncation before reaching the status column" hypothesis for Item #6 — the detection logic uses full rows; truncation is in evidence output only
- Overturned the BACKLOG's "iterates all files-modified-this-step" hypothesis for Item #7 — the gate uses `_extract_plan_required_deposits` from plan text, not `files_changed`

### Flags for CEO
- None

### Flags for Next Step
- Fix shapes are independent — can be planned as separate executables or batched
- Shape 6C (table-section scoping + status-token broadening) recommended over 6A or 6B alone
- Shape 7A (scope to first `.md` deposit) is sufficient; 7B (structural-context banner check) is optional hardening
- No existing tests cover multi-table or multi-deposit scenarios — new tests are mandatory for either fix
