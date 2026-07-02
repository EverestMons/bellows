# Plan-Lint Feasibility Audit — Checklist Item Classification

**Date:** 2026-07-01
**Scope:** PLANNER_TEMPLATE.md `## Plan Authoring Checklist` items 1–22
**Purpose:** Classify each item as (A) LINTABLE, (B) LINTABLE-WITH-CONTEXT, or (C) JUDGMENT to determine how much plan-authoring discipline can be offloaded from the Planner to a mechanical pre-deposit lint script.
**HARD CONSTRAINT applied:** Bucket (B) counts only read-only-or-trivial-edit checks. If a (B) check requires deciding whether content is ADEQUATE, CORRECT, or WELL-FORMED-IN-MEANING rather than merely PRESENT, it is reclassified to (C).

---

## Summary Table

| # | Description | Bucket | Concrete Check / Reason It Resists | Existing Code Overlap |
|---|---|---|---|---|
| 1 | Deposits blocks use canonical multi-line bullet form | **A** | Grep for `**Deposits:**`; verify each match is followed by `- ` bullet lines with single backtick-quoted paths; reject inline comma-separated form. PASS = every Deposits block is multi-line bullets. FAIL = any inline form detected. | `_extract_plan_required_deposits` (gates.py:437) already distinguishes block (line 453) vs inline (line 464) deposit formats — partial overlap. Currently ACCEPTS both; lint would REJECT inline. |
| 2 | Agent deposits use Rule 26 Deposits block format | **A** | Extract all backtick-quoted paths from step prose (outside `**Deposits:**` blocks) matching `*.md` or containing `/`; cross-reference against declared Deposits block entries. PASS = every prose-embedded path also appears in a Deposits block. FAIL = orphan prose deposit path found. | `_extract_plan_required_deposits` (gates.py:474–491) has legacy prose-matching fallback regexes — partial overlap. Those patterns are what the lint would flag as violations. |
| 3 | No STOP-prose in Bellows-dispatched plans | **A** | Parse header for `dispatch_mode`; if `bellows`, grep plan text for prohibited strings: `**STOP.**`, `do not proceed`, `halt and report`, `wait for CEO confirmation`, `wait for my confirmation`. PASS = zero matches. FAIL = any match found. | `_parse_plan_header` (gates.py:117) parses dispatch_mode — header parsing reusable. No existing STOP-prose check. |
| 4 | QA step includes exact canonical Rule 20 self-check reference | **B** | Read `RULE_20_SELF_CHECK_BLOCK.md` at governance root. For each QA step (identified via `qa_steps` header field), verify the step text contains the canonical template paragraph. Also verify four placeholder values (`plan_slug`, `qa_report_path`, `evidence_dir`, `required_evidence_files`) are filled (not placeholder text). PASS = exact template match with filled placeholders. FAIL = missing, paraphrased, or unfilled placeholders. **Dependency:** `RULE_20_SELF_CHECK_BLOCK.md` — reliably available at deposit time (static governance file). **HARD CONSTRAINT test:** read-only string comparison — stays B, pipeline-eligible. | `_gate_rule_20_self_check` (gates.py:494) checks QA REPORT for banner post-execution — shift-left: catching plan-side omission prevents wasted QA cycle. |
| 5 | Frontend-to-backend DEV steps specify exact field names | **C** | Trigger condition requires understanding whether a DEV step "connects a frontend component to a backend handler" — this is intent interpretation, not structural parsing. Keyword detection (e.g., "form", "handler", "endpoint") would produce unacceptable false-positive rates across project domains. Whether field names are "exact enough" is judgment about specification adequacy. | None. |
| 6 | QA-step Deposits blocks declare only the QA report | **A** | Identify QA steps via `qa_steps` header field. Parse each QA step's `**Deposits:**` block. Count `.md` entries. PASS = exactly one `.md` file declared. FAIL = zero or more than one `.md` entries. Evidence directories are excluded from the count per existing convention. | `_gate_is_qa_step` (gates.py:666) identifies QA steps — reusable. `_gate_deposit_exists` (gates.py:371) checks deposits post-execution — shift-left prevents false gate failures from over-declared deposits. |
| 7 | Follow-up plans from gate failures match files against full paths | **C** | Trigger condition requires knowing the plan's origin context (is it a follow-up from a gate failure?). This information is not encoded in the plan file itself — it exists in the Planner's session context and the verdict request that prompted the follow-up. Even if detectable via prose keywords, the full-path matching check requires the original verdict request's Files Changed list as comparison context, which is not reliably addressable by filename from the plan file. | None. |
| 8 | Filename-pattern fixes enumerate all lifecycle stages | **C** | Trigger condition requires understanding whether the plan's fix operates on files by filename pattern (intent interpretation). Whether "all lifecycle stages" are properly enumerated requires knowledge of Bellows lifecycle stages AND judgment about enumeration completeness relative to the specific pattern. The lifecycle stages are knowable, but the trigger is not. | None. |
| 9 | Multi-step diagnostics use pause_for_verdict: always | **A** | Parse header for plan type (from filename pattern or title: `diagnostic-*`). Count `## STEP` headers. If type is diagnostic AND step count > 1, verify `pause_for_verdict` header field == `always`. PASS = field present with value `always`. FAIL = field absent, or value is `after_step_1` or other non-`always` value. | `_parse_plan_header` (gates.py:117) parses `pause_for_verdict` — reusable. |
| 10 | Data-source mechanization plans include governance edit | **C** | Trigger condition requires understanding whether the plan "mechanizes a new authoritative data source" — this is a semantic judgment about the plan's architectural impact. Keyword detection for "data source", "authoritative", or "mechanize" would false-positive on plans that merely reference existing data sources. Whether a governance edit step is adequate for the specific data source requires domain judgment. | None. |
| 11 | Contract-changing plans grep test files before declaring targeted scope | **C** | Trigger condition requires understanding whether the plan changes a function's contract (return type, parameter types, or semantic contract). "Semantic contract" explicitly resists mechanization — it requires understanding what a function promises, not just what it returns. Even for return-type changes, detecting them requires parsing plan prose for intent ("change the return type of X") which is natural-language interpretation, not structural parsing. | None. |
| 12 | Schema migration plans include init_db and PRAGMA verification | **C** | Trigger condition ("does the plan ship a schema migration?") requires understanding plan intent. Keyword detection for migration-related terms (ALTER TABLE, CREATE TABLE, .db) would false-positive on plans that discuss database concepts without shipping migrations, and false-negative on plans that describe migrations in non-standard terminology. The downstream checks (init_db, PRAGMA presence) are mechanical, but the unreliable trigger makes end-to-end enforcement non-deterministic. | None. |
| 13 | Verify plan header against current parser before deposit | **B** | Run `gates._parse_plan_header()` against the composed plan file. PASS = parser returns a non-empty dict with expected fields. FAIL = parser returns `{}` or raises an exception. **Dependency:** `gates.py` — reliably available at deposit time (same codebase). **HARD CONSTRAINT test:** read-only cross-reference (run parser, check output shape) — stays B, pipeline-eligible. | `_parse_plan_header` (gates.py:117) IS the parser — the check literally invokes this function. |
| 14 | Name all target file paths literally in step bodies | **A** | For each step: extract paths from the step's `**Deposits:**` block; verify each path also appears as a literal string in the step's body text (outside the Deposits block). PASS = every deposit path found in step body. FAIL = deposit path only in Deposits block, not in body. Note: part (b) of the rule (all DEV edit targets inlined, not just deposits) requires understanding which paths are "edit targets" — that aspect is judgment (C). The primary check (deposit paths in body text) is mechanical. | `_gate_scope_check` (gates.py:695) reads step body for file authorization — shift-left: catching missing paths pre-deposit prevents scope_check gate failures post-execution. |
| 15 | No specific values from session memory in plan assertions | **C** | A lint cannot determine where a value came from (tool call vs session memory recall). The rule prohibits a PROCESS (authoring from memory), not a STRUCTURE (specific string patterns). The result of memory-based authoring (a wrong value) is indistinguishable from a correctly-recalled value until runtime verification fails. No structural signal in the plan file distinguishes recalled vs. tool-read values. | None. |
| 16 | Copy strict convention strings from known-good artifacts | **A** | Validate known header field values against hardcoded enum sets: `dispatch_mode` ∈ {`bellows`, `manual_bootstrap`}; `pause_for_verdict` ∈ {`always`, `after_step_1`}; `test_scope` ∈ {`targeted`, `full-suite`, `both`}; lifecycle directory names match `knowledge/decisions/`, `knowledge/research/`, etc. PASS = all convention strings match valid values. FAIL = any unrecognized value. Note: like Item 15, this catches the RESULT (invalid string) not the PROCESS (recall vs copy), but the result check is sufficient to prevent the failure mode (typos/invalid tokens that Bellows silently mishandles). | `_parse_plan_header` (gates.py:117) parses these fields — reusable. No existing value validation. |
| 17 | Mechanize dispatch-mode validation | **A** | Parse header for `dispatch_mode` field; verify value ∈ {`bellows`, `manual_bootstrap`}. PASS = valid value. FAIL = missing field or unrecognized value. This is a subset of Item 16 — if Item 16 is implemented, this check is subsumed. | `_parse_plan_header` (gates.py:117) parses the field but does not validate its value — the lint adds validation. |
| 18 | Strictly monotonic integer STEP header labels | **A** | Regex-match all `## STEP` headers in the plan file. Extract the label portion. Verify labels form a strictly monotonic integer sequence: 1, 2, 3, .... PASS = consecutive integers starting at 1. FAIL = non-integer label (e.g., "2A"), gap in sequence, or non-monotonic order. | `_extract_step_text` (gates.py:418) uses `## STEP {step_number}` pattern — reusable regex. Step numbering assumed but not validated. |
| 19 | Deposited filename is the draft placeholder | **A** | Match the destination filename against `^(parallel-\d+-)?(executable|diagnostic|qa)-draft-\d{6}\.md$`. PASS = filename matches pattern. FAIL = descriptive slug, date, or non-standard prefix in filename. The lint receives the destination filename as an input argument (the path the Planner is about to `move_file` to). | None — filename validation is not in gates.py. |
| 20 | Derivations citation present and integer | **A** | Grep the plan text for `implements diagnostic`. If found, extract the token after `diagnostic` and verify it is a bare integer (regex: `\d+`). PASS = integer id or no citation present. FAIL = citation present but id is a legacy slug (non-integer). Note: the check cannot determine whether a citation SHOULD be present when absent — that requires knowing the plan's provenance (whether it derives from a prior diagnostic). The absence case is outside lint scope. | None — derivations are not checked in existing gates. |
| 21 | Scope enumerations include implied test-infrastructure files | **C** | Trigger condition requires understanding whether the plan "introduces a new module-level path or state constant" — this is semantic analysis of the plan's code-change impact, not structural parsing. Even if detectable via keywords, determining which test-infrastructure files are "implied" requires understanding the project's test isolation patterns, which varies by project. | None. |
| 22 | Never re-enumerate artifact-authoritative specifics inline | **C** | Requires understanding whether a step "designates a design artifact as authoritative" and whether it "restates those specifics" — both are content-meaning assessments. A structural check might detect co-occurrence of artifact references and DDL/schema keywords in the same step, but whether the keywords constitute "re-enumeration" vs. legitimate instructional context is judgment. The rule's own distinction ("file PATHS must be inlined; technical SPECS must not") requires interpreting what constitutes a "spec" vs a "path." | None. |

---

## Bottom-Line Feasibility Count

| Bucket | Count | Items | Pipeline-Eligible? |
|---|---|---|---|
| **A — LINTABLE** (plan file alone) | **11** | 1, 2, 3, 6, 9, 14, 16, 17, 18, 19, 20 | Yes — all deterministic |
| **B — LINTABLE-WITH-CONTEXT** (reliable external dependency) | **2** | 4, 13 | Yes — both are read-only cross-references with reliably available dependencies |
| **C — JUDGMENT** (requires model interpretation) | **9** | 5, 7, 8, 10, 11, 12, 15, 21, 22 | No — trigger conditions or adequacy assessments require intent interpretation |

**13 of 22 checklist items are mechanically enforceable** (11 A + 2 B with reliable dependencies). These can be offloaded from the Planner to a coded pre-deposit lint script that exits non-zero on violation.

**9 of 22 items remain model judgment**, predominantly because their trigger conditions require understanding plan intent (items 5, 7, 8, 10, 11, 12, 21) or distinguishing a process from its result (item 15), or interpreting content meaning (item 22). These cannot be reduced to deterministic checks regardless of implementation sophistication.

### Shift-Left Assessment

Several A-bucket items overlap with existing post-execution gates in `gates.py`. Pre-deposit enforcement would shift these checks LEFT in the pipeline — catching plan-authoring errors before Bellows dispatches the plan, rather than after the agent has spent an execution cycle:

| Checklist Item | Existing Gate | Shift-Left Value |
|---|---|---|
| 1 (deposit block format) | `_extract_plan_required_deposits` accepts both forms | Prevents parser ambiguity at extraction time |
| 2 (Rule 26 format) | Legacy prose fallback in `_extract_plan_required_deposits` | Prevents deposit_exists false negatives from unregistered prose paths |
| 6 (QA deposits = 1 .md) | `_gate_deposit_exists` checks declared deposits | Prevents deposit_exists false positives from over-declared QA deposits |
| 14 (paths in step bodies) | `_gate_scope_check` reads step body for authorization | Prevents scope_check gate failures — high value (saves full re-deposit cycle) |
| B-4 (Rule 20 reference) | `_gate_rule_20_self_check` checks QA report | Prevents wasted QA execution cycle when self-check instruction is missing |

Items 3, 9, 16, 17, 18, 19, 20 have NO existing gate coverage — these are purely NEW enforcement that currently relies entirely on the Planner's memory and discipline. These represent the highest marginal value for a pre-deposit lint.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1 (SA — diagnostic investigation)
**Status:** Complete

### What Was Done
Classified all 22 Plan Authoring Checklist items from PLANNER_TEMPLATE.md into lintability buckets (A/B/C). Produced a summary table with concrete checks, judgment-resistance reasons, and existing-code overlap citations. Determined that 13 of 22 items (59%) are mechanically enforceable via a pre-deposit lint script, while 9 items (41%) require model judgment and must remain Planner-side discipline.

### Files Deposited
- `knowledge/research/plan-lint-feasibility-2026-07-01.md` — feasibility classification of all 22 checklist items with concrete checks, existing-code overlap, and bottom-line count

### Files Created or Modified (Code)
- None (read-only investigation)

### Decisions Made
- Classified B-items strictly per HARD CONSTRAINT: only read-only cross-references counted as B; any check requiring content-adequacy judgment reclassified to C
- Items 16 and 17 classified as A (not B) because convention-string validation can use hardcoded enum sets within the lint itself, making the canonical source an implementation detail rather than a runtime dependency
- Item 14 classified as A for the primary check (deposit paths in body text) with a note that the broader check (all edit targets inlined) has a judgment component

### Flags for CEO
- Items 16 and 17 are substantially overlapping (17 is a subset of 16 for dispatch_mode specifically). A lint implementation should consolidate them into a single convention-string validator.
- 7 of the 11 A-items (items 3, 9, 16, 17, 18, 19, 20) have zero existing gate coverage — these are the highest-value targets for a lint because they currently rely entirely on Planner memory.

### Flags for Next Step
- None (single-step diagnostic)

### Ledger Updates

#### Prompt Feedback
- Prompt was well-scoped: the HARD CONSTRAINT on bucket (B) prevented false inflation of the mechanizable count by catching checks that look mechanical but require judgment beneath the surface.
- The specific instruction to check for existing-code overlap was valuable — it revealed the shift-left dimension (pre-deposit vs post-execution enforcement) that pure classification would have missed.
- The 22-item scope was correctly bounded. PLANNER_TEMPLATE.md also contains 46 "Orchestration Plan Rules" (a separate section) that are conceptual rules, not deposit-time checks. The diagnostic correctly scoped to the checklist section.
