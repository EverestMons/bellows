# Rule 20 Block Sourcing — Migration Surface Findings

**Diagnostic:** diagnostic-rule-20-block-sourcing-2026-05-10
**Agent:** Bellows Systems Analyst
**Date:** 2026-05-10

---

## Q1. PLANNER_TEMPLATE Rule 20 canonical block — verbatim

The Rule 20 section spans **lines 506–598** of `PLANNER_TEMPLATE.md` (v4.35).

**Section header (line 506):**
```
### 20. Mandatory QA self-check Python block
```

**Prose preamble (lines 507–510):**
> Every QA step in every executable plan MUST end with a mandatory Python self-check block that runs AFTER the QA report is written but BEFORE the plan can close. The self-check is mechanical — it does not depend on the agent's judgment, and the agent cannot fake its output because the Python output is deterministic. The agent must execute the block, include its literal output in the QA report, and halt the plan if any check fails. The self-check is glyph-agnostic — it detects positive-status rows by matching any of {✅, OK, PASS, [x], done, complete, verified} as a standalone cell value, preventing bypass via alternate status indicators.

**Template block introduction (line 510):**
> **Self-check block template** (include verbatim at the end of every QA step prompt):

**Full Python block (lines 512–576):**
```python
# Rule 20 — Mandatory QA Self-Check
import os, sys
plan_slug = "<plan-filename-without-md>"  # e.g., "executable-base-rates-section-type-2026-04-08"
qa_report_path = f"<project>/knowledge/qa/<qa-report-filename>.md"
evidence_dir = f"<project>/knowledge/qa/evidence/{plan_slug}/"
required_evidence_files = [
    # List every filename this plan's QA step is required to deposit
]
hedging_keywords = ["pending", "inferred", "extrapolated", "estimated", "approximate", "skipped", "assumed", "close enough", "should pass", "would pass", "not run"]
# Glyph-agnostic positive-status detection. Any of these tokens, when appearing
# as a standalone cell value in a markdown table row, marks that row as a
# positive status row subject to the hedging scan. Bounded matching (cell
# equality, not substring) prevents false positives on words like "completed"
# or "passing". Closes the v4.19 bypass where QA could use "OK" instead of
# "✅" to evade the scan.
POSITIVE_STATUS_TOKENS = ["✅", "OK", "PASS", "done", "complete", "verified"]

def is_positive_row(line):
    """True if the line is a markdown table row marked with a positive status token."""
    if "|" not in line:
        return False
    cells = [c.strip() for c in line.split("|")]
    for cell in cells:
        for token in POSITIVE_STATUS_TOKENS:
            if token == "✅":
                if "✅" in cell:
                    return True
            else:
                if cell.lower() == token.lower():
                    return True
    return False

failures = []
if not os.path.isdir(evidence_dir):
    failures.append(f"CRITICAL: evidence folder missing: {evidence_dir}")
else:
    for fname in required_evidence_files:
        fpath = os.path.join(evidence_dir, fname)
        if not os.path.isfile(fpath):
            failures.append(f"CRITICAL: evidence file missing: {fpath}")
        elif os.path.getsize(fpath) == 0:
            failures.append(f"CRITICAL: evidence file empty: {fpath}")
if os.path.isfile(qa_report_path):
    with open(qa_report_path, "r") as f:
        report = f.read()
    for line in report.splitlines():
        if is_positive_row(line):
            lower = line.lower()
            for kw in hedging_keywords:
                if kw in lower:
                    failures.append(f"CRITICAL: hedging keyword '{kw}' in positive-status row: {line.strip()[:120]}")
                    break
else:
    failures.append(f"CRITICAL: QA report not found at {qa_report_path}")
print("=" * 60)
print("Rule 20 — QA Self-Check Results")
print("=" * 60)
if failures:
    print(f"FAILED — SELF-CHECK FAILED — {len(failures)} issue(s):")
    for f in failures:
        print(f"  - {f}")
    print("\nPlan CANNOT close. Fix issues and re-run QA.")
    sys.exit(1)
else:
    print("PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.")
    print(f"Evidence folder: {evidence_dir}")
    print(f"Files verified: {len(required_evidence_files)}")
```

**Prose postamble — "The Planner's job when writing a QA step" (lines 578–583):**
1. Enumerate every non-trivial check in the QA step
2. Assign each check a short evidence filename
3. Populate `required_evidence_files` with those filenames
4. Write the QA prompt so each check deposits output to evidence files

**Prose postamble — "The QA agent's job" (lines 585–593):**
1. Execute every check, depositing output to evidence files
2. Fill in verification table citing evidence file paths
3. Run the mandatory self-check Python block at the end
4. Include literal stdout in the QA report
5. If FAILED, STOP — report to CEO
6. If PASSED, proceed with closure

**Prose postamble — "When a self-check fails" (lines 595–596):** CEO review protocol (re-run / escalate / override).

**Final prose (lines 597–598):**
> **This rule is the enforcement teeth for Rules 17, 18, and 19.** Rule 17 says verify deliverables. Rule 18 says deposit evidence files. Rule 19 says hedging language is invalid. Rule 20 is the Python block that mechanically checks whether all three rules were actually followed. An agent can lie in its prose, but it can't lie about what `os.path.isfile()` returns.

**Cross-references from other rules:**

- **Rule 22(e) (line 646):** `For QA reports specifically: the literal Rule 20 banner string "Rule 20 — QA Self-Check Results" MUST be present, immediately followed (within the same code block or section) by a line beginning with "PASSED — SELF-CHECK PASSED". Section header without banner = fabrication; banner without PASSED line = self-check ran but failed. Both halt the plan.`
- **Rule 26 / Deposits (line 747):** Evidence files do NOT need individual deposit bullets — list the evidence directory as a single bullet, `because the Rule 20 self-check already enumerates the individual evidence filenames`.
- **Rule 26 / Deposits (line 757):** Rule 20 mechanically verifies evidence files exist; Rule 26 declares the deposits shape. The three rules (18, 20, 26) compose.
- **Lessons entry (line 1271):** 2026-05-05 Rule 20 self-check fabrication lesson — documents the two-part fix (Bellows-side gate + Rule 22(e) tightening).

---

## Q2. `bellows/agents/BELLOWS_QA.md` — current structure

**File:** `/Users/marklehn/Desktop/GitHub/bellows/agents/BELLOWS_QA.md`
**Total lines:** 180 (≈6 KB)

**Top-level section headers (## lines), in order:**

| Line | Header |
|------|--------|
| 14 | `## Role Summary` |
| 20 | `## Project Context` |
| 44 | `## Core Responsibilities` |
| 55 | `## Operating Procedure` |
| 66 | `## Output Format` |
| 75 | `### Output Receipt` |
| 81 | `## Output Receipt` |
| 107 | `## Decision Authority` |
| 122 | `## Peer Consultation` |
| 136 | `## Quality Standards` |
| 145 | `## Guardrails` |
| 154 | `## Project Knowledge Base Index` |
| 164 | `## Completeness Checklist` |

**Existing references to "Rule 20" or "self-check":**

- **Line 16 (Role Summary):** `"The QA specialist enforces Rule 17 deliverable verification, Rule 20 self-check blocks, and Rule 21 test scope declarations across all Bellows plan executions..."`
- **Line 48 (Core Responsibilities):** `"Execute Rule 20 self-check blocks: run the Python verification script embedded in QA steps and include literal stdout in QA reports"`
- **Line 62 (Project-Specific Procedure):** `"When running Rule 20 self-check scripts, execute them exactly as written (do not modify the script) and include the full stdout output in the QA report. If the self-check prints FAILED, do not proceed with plan closure — report the failure and wait for CEO direction."`
- **Line 141 (Project-Specific Quality Notes):** `"Every QA report must include the literal stdout of any Rule 20 self-check script, not a summary or paraphrase."`

**Assessment:** The agent file references Rule 20 in four places — all describing the agent's obligation to _execute_ and _report_ the block. None of these locations contain the canonical Python block itself. The agent file currently assumes the block is embedded in the plan prompt (per PLANNER_TEMPLATE Rule 20's "include verbatim at the end of every QA step prompt" instruction).

**Recommended insertion point:** After line 151 (end of `### Project-Specific Guardrails` section content), before line 154 (`## Project Knowledge Base Index`). Rationale: the block is a project-specific operational artifact — it fits between the guardrails section and the index. Alternatively, a dedicated new `## Rule 20 Self-Check (Canonical Block)` section could be inserted between `## Guardrails` (line 145) and `## Project Knowledge Base Index` (line 154), at approximately line 152. This keeps the block near the quality/guardrails sections where it is conceptually referenced.

---

## Q3. Invoice-pulse QA agent file — current structure

**File:** `/Users/marklehn/Desktop/GitHub/invoice-pulse/agents/INVOICE_SECURITY_TESTING_ANALYST.md`
**Total lines:** 213 (≈7 KB)

**Top-level section headers (## lines), in order:**

| Line | Header |
|------|--------|
| 13 | `## Role Summary` |
| 19 | `## Project Context` |
| 48 | `## Core Responsibilities` |
| 59 | `## Operating Procedure` |
| 77 | `## Output Format` |
| 94 | `### Output Receipt` |
| 100 | `## Output Receipt` |
| 126 | `## Decision Authority` |
| 141 | `## Peer Consultation` |
| 153 | `## Quality Standards` |
| 162 | `## Guardrails` |
| 176 | `## Project Knowledge Base Index` |

**Existing references to "Rule 20" or "self-check":** **None.** A grep for `Rule 20`, `self-check`, and `SELF-CHECK` returned zero matches. The invoice-pulse QA agent file does not mention Rule 20 at all.

**Assessment:** The invoice-pulse QA agent file does NOT publish the canonical Rule 20 block locally. Migration is **net-new authoring** for invoice-pulse, not consolidation. The block would need to be authored into this file from scratch (with invoice-pulse–specific path conventions for `qa_report_path`, `evidence_dir`, etc.).

Note: invoice-pulse has no agent file named `qa.md` — the QA role is served by `INVOICE_SECURITY_TESTING_ANALYST.md`. The original BACKLOG entry's reference to `bellows/agents/qa.md` would need to map to `BELLOWS_QA.md` for bellows and `INVOICE_SECURITY_TESTING_ANALYST.md` for invoice-pulse.

---

## Q4. PLANNER_TEMPLATE Rule 20 prose that mandates the block

Two locations mandate the block's inclusion:

### 4a. Rule 20 itself (line 506–510)

The section header and preamble:

> `### 20. Mandatory QA self-check Python block`
> `Every QA step in every executable plan MUST end with a mandatory Python self-check block that runs AFTER the QA report is written but BEFORE the plan can close.`

The template introduction (line 510):
> `**Self-check block template** (include verbatim at the end of every QA step prompt):`

This is the primary mandate. It tells the **Planner** to include the block verbatim in every QA step prompt. The migration would rewrite this from "include this Python block verbatim" to something like "instruct the QA agent to run the canonical Rule 20 self-check from their agent file."

### 4b. Rule 22(e) (line 646)

> `(e) For QA reports specifically: the literal Rule 20 banner string "Rule 20 — QA Self-Check Results" MUST be present, immediately followed (within the same code block or section) by a line beginning with "PASSED — SELF-CHECK PASSED".`

This is the **verification** mandate — it tells the Planner what to check in deposited QA reports. It does not directly mandate where the block appears in the plan; it mandates what must appear in the **output**. This section would likely remain unchanged by the migration (it checks output, not source).

### 4c. Positional guidance

Rule 20 says the block must appear "at the end of every QA step prompt" (line 510). It does NOT specify where in the QA _report_ the output must appear — only that the "literal stdout" must be "included in the QA report" (line 591).

Rule 22(e) enforces banner presence in the deposited QA report file but does not specify position within that file — only presence + adjacency of PASSED line.

The Bellows gate (`_gate_rule_20_self_check` in `gates.py`) reads the entire deposited QA report and matches the banner string anywhere in the file. It is position-agnostic.

**Summary for migration:** The positional instruction "at the end of every QA step prompt" is an instruction to the **Planner** about where to place the block in the authored plan. If the block moves to the agent file, this instruction would change to something like "instruct the QA agent to run the self-check per their agent file." The output-side checks (Rule 22(e) and Bellows gate) are already position-agnostic and would not need changes.

---

## Q5. Recent Planner-authored plans containing a Rule 20 block

**Search scope:** All `*.md` files in `*/knowledge/decisions/` and `*/knowledge/decisions/Done/` modified in the last 7 days (since 2026-05-03).

### Bellows project (13 plans)

| # | File | State | Banner variant |
|---|------|-------|----------------|
| 1 | `in-progress-diagnostic-rule-20-block-sourcing-2026-05-10.md` | in-progress | Reference only (this plan) |
| 2 | `Done/diagnostic-inactivity-timeout-investigation-2026-05-10.md` | Done | Canonical: `Rule 20 — QA Self-Check Results` |
| 3 | `Done/executable-rule-20-self-check-wt-path-2026-05-10.md` | Done | Non-canonical: `RULE 20 SELF-CHECK PASSED` |
| 4 | `Done/executable-s3-verdict-resolved-retry-loop-fix-2026-05-09.md` | Done | Non-canonical: `Rule 20 Self-Check` (heading) |
| 5 | `Done/executable-startup-sweep-extract-2026-05-10.md` | Done | Non-canonical: `RULE 20 SELF-CHECK` |
| 6 | `Done/executable-session-wrap-s3-2026-05-09.md` | Done | Canonical: `Rule 20 — QA Self-Check Results` |
| 7 | `Done/executable-phase-1-5-lessons-source-d-2026-05-10.md` | Done | Canonical: `Rule 20 — QA Self-Check Results` |
| 8 | `Done/executable-s3-bug-c-halted-stale-check-2026-05-10.md` | Done | Canonical: `Rule 20 — QA Self-Check Results` |
| 9 | `Done/executable-teardown-worktree-lock-cleanup-2026-05-10.md` | Done | Non-canonical: `RULE 20 SELF-CHECK` |
| 10 | `Done/executable-s3-fix-qa-rule-20-banner-redeposit-2026-05-09.md` | Done | Canonical: `Rule 20 — QA Self-Check Results` (redeposit fix plan) |
| 11 | `Done/executable-session-wrap-evening-2026-05-10.md` | Done | Non-canonical: `Rule 20 Self-Check` |
| 12 | `in-progress-executable-session-wrap-2026-05-08.md` | in-progress | Has Rule 20 reference |

### Invoice-pulse project (11 plans)

| # | File | State | Banner variant |
|---|------|-------|----------------|
| 1 | `Done/executable-backlog-hygiene-edits-2026-05-06.md` | Done | Canonical: `Rule 20 — QA Self-Check Results` |
| 2 | `Done/executable-session-wrap-action-queue-aggregation-2026-05-07.md` | Done | Canonical: `Rule 20 — QA Self-Check Results` |
| 3 | `Done/executable-aggregated-queue-customer-display-2026-05-07.md` | Done | Canonical: `Rule 20 — QA Self-Check Results` |
| 4 | `Done/executable-half-up-currency-rounding-2026-05-06.md` | Done | Canonical: `Rule 20 — QA Self-Check Results` |
| 5 | `Done/executable-backlog-hygiene-edits-2026-05-06c.md` | Done | Canonical: `Rule 20 — QA Self-Check Results` |
| 6 | `Done/executable-backlog-hygiene-lanes-csrf-close-2026-05-06.md` | Done | Non-canonical: `Rule 20 Self-Check` |
| 7 | `Done/executable-backlog-hygiene-edits-2026-05-06b.md` | Done | Canonical: `Rule 20 — QA Self-Check Results` |
| 8 | `Done/executable-qa-report-rule-20-banner-fix-2026-05-07.md` | Done | Canonical: `Rule 20 — QA Self-Check Results` (banner fix plan) |
| 9 | `Done/executable-session-wrap-2026-05-06.md` | Done | Canonical: `Rule 20 — QA Self-Check Results` |
| 10 | `Done/executable-session-wrap-half-up-rounding-2026-05-06.md` | Done | Non-canonical: `Rule 20 Self-Check` |
| 11 | `verdict-pending-executable-action-queue-aggregation-2026-05-07.md` | verdict-pending | Has Rule 20 reference (in-flight) |

### Summary statistics

- **Total plans with Rule 20 references (last 7 days):** 24 across 2 projects
- **Bellows:** 12 plans (1 in-progress, 11 Done)
- **Invoice-pulse:** 11 plans (1 verdict-pending, 10 Done)
- **Other projects (forge, anvil, etc.):** 0 matches
- **Canonical banner** (`Rule 20 — QA Self-Check Results`): ~14 plans
- **Non-canonical variants** (`Rule 20 Self-Check`, `RULE 20 SELF-CHECK`, `RULE 20 SELF-CHECK PASSED`): ~7 plans
- **In-flight plans that would need updating if migration ships:** 3 (bellows in-progress-diagnostic-rule-20-block-sourcing-2026-05-10, bellows in-progress-executable-session-wrap-2026-05-08, invoice-pulse verdict-pending-executable-action-queue-aggregation-2026-05-07)

The non-canonical variant frequency (~30%) confirms the BACKLOG entry's observation that plans re-author the block rather than copying it verbatim, leading to banner string drift that trips the Bellows gate.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Investigated five questions about the Rule 20 self-check block migration surface: (1) quoted the full canonical block from PLANNER_TEMPLATE.md with line numbers, (2) mapped bellows QA agent file structure and existing Rule 20 references with recommended insertion point, (3) identified invoice-pulse's QA agent file (`INVOICE_SECURITY_TESTING_ANALYST.md`) which has zero Rule 20 references (net-new authoring needed), (4) documented the mandate prose and positional guidance (output-side checks are position-agnostic), (5) catalogued 24 recent plans across 2 projects with ~30% non-canonical banner variant rate.

### Files Deposited
- `bellows/knowledge/research/rule-20-block-sourcing-migration-surface-2026-05-10.md` — migration surface findings for all five diagnostic questions

### Files Created or Modified (Code)
- None (read-only investigation)

### Decisions Made
- Identified `INVOICE_SECURITY_TESTING_ANALYST.md` as the invoice-pulse QA agent file (no `qa.md` exists; BACKLOG entry's reference needs remapping)
- Recommended insertion point for bellows: new section between `## Guardrails` (line 145) and `## Project Knowledge Base Index` (line 154)

### Flags for CEO
- None

### Flags for Next Step
- The migration is cross-project (bellows + invoice-pulse), not bellows-only — invoice-pulse requires net-new block authoring
- 3 in-flight plans would need updating if migration ships before they close
- ~30% of recent plans use non-canonical banner variants, confirming the re-authoring drift problem
