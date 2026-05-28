# Gate FP Coordinated Shape — Joint Call-Site Characterization and Shared-Abstraction Evaluation

**Date:** 2026-05-27
**Diagnostic:** `diagnostic-gate-fp-coordinated-shape-2026-05-27`
**Agent:** Bellows Systems Analyst
**Step:** 1

---

## Section A — Q1: Three Call-Site Mechanism Characterizations

### A1. `ceo_flags` gate — `_gate_ceo_flags` + `parser.py` extraction

**Gate function:** `gates.py:215-218`

```python
def _gate_ceo_flags(parsed, failures):
    flags = parsed.get("ceo_flags", [])
    if flags:
        failures.append({"gate": "ceo_flags", "evidence": "; ".join(flags)})
```

**Extraction function:** `parser.py:28-36`

```python
ceo_flags = []
match = re.search(r"### Flags for CEO\s*\n(.*?)(?=\n##|\Z)", result_text, re.DOTALL)
if match:
    for line in match.group(1).splitlines():
        line = line.strip()
        if line.startswith("- "):
            txt = line[2:].strip()
            if txt and txt.lower() not in ("none", "n/a"):
                ceo_flags.append(txt)
```

**Parsing logic that produces the FP:** The parser extracts each bulleted line under `### Flags for CEO` in the agent's Output Receipt. It excludes exact-match `"none"` and `"n/a"` (case-insensitive) but does NOT handle null-declaration prose that starts with "None" followed by explanatory content. The gate at `gates.py:217` fires on any non-empty list (`if flags:`), treating every extracted flag entry as a genuine escalation signal.

**Structural shape:** Free-text field. The `### Flags for CEO` section is a subsection of the Output Receipt block. Each bulleted line becomes one entry in the `ceo_flags` list. The gate operates on the list as a whole (non-empty = fail).

**Triggering content:** From `processed-verdict-planner-template-bellows-operational-workarounds-2026-05-27-step-2.md`: the agent's Output Receipt `### Flags for CEO` field contained:
```
- None. All SA-cited anchor lines matched verbatim. No blueprint-vs-file mismatches. No prose adjustments needed.
```
The parser extracted `"None. All SA-cited anchor lines matched verbatim. No blueprint-vs-file mismatches. No prose adjustments needed."` — this does not match `"none"` exactly because of the trailing explanatory content. The gate received a 1-element list and fired.

**Key observation:** The FP has TWO potential fix sites: (1) the parser in `parser.py` (broader null-token matching at extraction time), or (2) the gate in `gates.py` (null-content classification at gate-check time). The BACKLOG entry's fix shapes target the gate side, which is architecturally correct — the parser is a thin extractor, and the gate is where semantic classification belongs.

### A2. `rule_22_verification` (c) sub-check — row-status / "missing status" branch

**Function:** `_gate_rule_22_verification` at `gates.py:480-556`

**Offending parsing logic:** `gates.py:527-556` — the (c) check iterates all lines of the QA report, tracking section headers (`## `) and table state (`in_data` / `_TABLE_SEPARATOR_RE`). Post-2026-05-24 fix (Shape 6C), it ONLY inspects tables inside `## ` sections whose header contains "verification" (case-insensitive, `gates.py:532-533`). For each data row in a verification-section table, it checks for `❌` or the absence of a positive-status token via `_is_positive_status_row(line)` (`gates.py:552`).

```python
in_data = False
in_verification_section = False
for i, line in enumerate(lines, 1):
    stripped = line.strip()
    if stripped.startswith("## "):
        in_verification_section = "verification" in stripped.lower()
        in_data = False
        continue
    ...
    if not in_verification_section:
        continue  # Skip tables outside verification sections
    # Data row inside a verification-section table
    if "\u274c" in stripped:
        failures.append(...)
    elif not _is_positive_status_row(line):
        failures.append(...)
```

**The FP mechanism (2026-05-27 enumerative tables):** The QA report at `lessons-forge/knowledge/qa/plan-authoring-checklist-qa-2026-05-27.md` uses `## Verification Checks` as its top-level heading (line 10: `## Verification Checks`). Because "verification" appears in this `## ` header, `in_verification_section` becomes `True` and remains `True` for ALL content under this heading — including non-verification tables nested as evidence within individual `### Check N` subsections. These enumerative tables (heading enumeration at lines 30-43, proposal-ID map at lines 50-64, rule-numbering at lines 74-78, archived-proposals, verbatim-match cross-reference) have structures like `| # | Line | Title |` with no status column. Every data row in these tables triggers `_is_positive_status_row(line) → False` → "missing status" failure.

**Structural shape:** Markdown table rows within a section-scoped region. The (c) check's section-scoping uses `## ` headers only — it does NOT distinguish `### ` sub-headers or distinguish between "this table is a verification-result table" and "this table is enumerative evidence within a verification section." The scoping granularity is too coarse: it scopes to `## Verification` but not to individual check-result tables vs. evidence tables within that section.

**Triggering content:** 31 false-positive failures across 5 enumerative tables, all under `## Verification Checks`. Example from the heading-enumeration table:
```
| 1 | 923 | Deposits blocks use canonical multi-line bullet form |
```
This row has no status cell — it's a content enumeration, not a verification result.

### A3. `rule_22_verification` (d) sub-check — hedging-detector branch

**Function:** `_gate_rule_22_verification` at `gates.py:558-568`

**Offending parsing logic:** `gates.py:558-568`

```python
# (d) No hedging keywords in positive-status rows
for i, line in enumerate(lines, 1):
    if _is_positive_status_row(line):
        lower = line.lower()
        for kw in HEDGING_KEYWORDS:
            if kw in lower:
                failures.append({
                    "gate": "rule_22_verification",
                    "evidence": f"(d) Hedging keyword '{kw}' in positive-status row: {line.strip()[:120]}...",
                })
                break
```

**Hedging vocabulary:** `gates.py:59-62`
```python
HEDGING_KEYWORDS = [
    "pending", "inferred", "extrapolated", "estimated", "approximate",
    "skipped", "assumed", "close enough", "should pass", "would pass", "not run",
]
```

**The FP mechanism:** The (d) check iterates ALL lines of the QA report (not scoped to any section), identifies positive-status rows via `_is_positive_status_row(line)`, and then substring-matches the ENTIRE row text (`line.lower()`) against each hedging keyword. It fires when a hedging keyword appears ANYWHERE in the row — including in the test-description cell, the evidence cell, or any cell that is NOT the status cell.

**Structural shape:** Vocabulary substring match against the entire markdown table row. No cell-level scoping. No section-level scoping (unlike the (c) check, the (d) check was NOT updated by the 2026-05-24 Shape 6C fix — it still iterates all lines globally).

**Triggering content:** From `verdict-request-deferred-validation-status-card-2026-05-22-step-4.md`, 5 hedging-keyword FPs all on the word `pending`:
1. Row 20: `| (c) | _run_pending flag lifecycle — try/finally | ...` — function name `_run_pending`
2. Row 21: `| (d) | POST /ingest/validation/run — 200 + correct JSON | ...` — JSON field reference `{"started":...`
3. Row 23: `| (d3) | GET /ingest/validation/status — JSON shape | ...` — JSON field `pending`
4. Row 28: `| (h) | State walkthrough — idle | ... pending=0, in_progress...` — state variable
5. Row 29: `| (h2) | State walkthrough — pending | ... pending=5...` — state name and variable

All 5 rows are positive-status verification rows (they contain `✅` or positive-status tokens). The word `pending` appears in test-description or evidence cells as a domain term (validation state machine states, function names, JSON fields), NOT as hedging language about the verification result.

**Key observation:** The (d) check has TWO independent scoping gaps: (1) no section-scoping (inspects all lines in the file, not just verification-section tables), and (2) no cell-scoping (substring matches the entire row, not just the status cell or its adjacent context).

---

## Section B — Q2: Abstraction Convergence Analysis

### Option A — Single helper (`_is_null_declaration(text) -> bool`)

**Structural support:** Partially. The CEO Flags FP (A1) is a null-declaration problem — the field contains "None. ..." which should be recognized as a no-flags-raised declaration. But the rule_22 (c) FP (A2) is NOT a null-declaration problem — the enumerative tables are real content, not null declarations. They simply aren't verification tables. The rule_22 (d) FP (A3) is also NOT a null-declaration problem — the rows are genuine positive-status verification rows containing domain terminology. A single `_is_null_declaration` predicate cannot meaningfully close (c) or (d).

**Verdict:** No — the three FP mechanisms are structurally distinct.

### Option B — Section-scoping primitive (`_iter_verification_rows()`)

**Structural support:** Partially. The (c) check already HAS section-scoping (Shape 6C from 2026-05-24) — the problem is that its scoping granularity is too coarse (scopes to `## Verification` headers but not to individual verification-result tables within that section). The (d) check currently has NO section-scoping at all — adding it would eliminate FPs where `pending` appears in non-verification tables (but the triggering artifact shows all 5 FP rows ARE inside verification tables). The CEO Flags field is not a table row — a section-scoping iterator is structurally irrelevant.

**Verdict:** Partially — could close (c) with refined scoping and partially help (d) if the FPs occurred in non-verification tables, but the actual (d) FPs occur in genuine verification rows. Does not help CEO Flags at all.

### Option C — Three independent predicates

**Structural support:** Yes. Each site's content shape is distinct:
- A1 (ceo_flags): free-text field, needs null-token classification
- A2 (rule_22 (c)): markdown tables within a section-scoped region, needs table-type classification (verification-result table vs. enumerative-evidence table)
- A3 (rule_22 (d)): entire row text, needs cell-level scoping of substring match

These are three different content shapes requiring three different scoping primitives.

### Option D — Mixed shape

**Structural support:** Yes. (c) and (d) share a common context — both operate on markdown table rows within `_gate_rule_22_verification`, both read from the same file, and both could benefit from a refined scoping mechanism that distinguishes "verification-result tables" from "evidence/content tables." CEO Flags is structurally independent (different gate, different content shape, different parsing pipeline).

**Concrete partition:** (c) row-status + (d) hedging share a refined section-scoping primitive within `_gate_rule_22_verification`; CEO Flags gets an independent null-token allowlist in the gate (or parser).

**Pick: Option D (mixed shape).**

**Justification:** The structural shapes from Section A make it clear: (c) and (d) are both downstream of the same `_gate_rule_22_verification` function, both read the same QA report content, and both suffer from scoping granularity gaps (though at different levels — section vs. cell). A shared refinement of the scoping model within that function would address both. CEO Flags is a completely different gate (`_gate_ceo_flags`), different input pipeline (`parser.py`), and different content shape (free text vs. table rows). Forcing CEO Flags into a shared abstraction with the rule_22 sub-checks would be architecturally incoherent.

---

## Section C — Q3: 2026-05-24 Helper Reusability

### 2026-05-24 helpers in current `gates.py`

**Helper 1:** `_is_positive_status_row(line)` at `gates.py:71-84`
- Signature: `_is_positive_status_row(line: str) -> bool`
- Current consumers: (c) check at `gates.py:552`, (d) check at `gates.py:560` (3 call sites per QA report grep showing 3 matches)

**Helper 2:** Section-scoping state machine (inline, not extracted as a helper)
- The 2026-05-24 fix added `in_verification_section` tracking at `gates.py:528,532-534,544` — this is inline state within the (c) check's `for` loop, NOT a reusable helper function.

### Reusability assessment per 2026-05-27 site

**A1 — CEO Flags (`_gate_ceo_flags`):**
- `_is_positive_status_row`: **(iii) Model-only.** The ceo_flags gate does not operate on table rows. The helper's signature (`line: str -> bool` where `line` is a markdown table row) is structurally irrelevant to a free-text field null-declaration check.
- Section-scoping state machine: **(iii) Model-only.** CEO Flags is not parsed from a sectioned document with markdown tables.

**A2 — Rule 22 (c) row-status:**
- `_is_positive_status_row`: **(i) Directly reusable — already consumed.** The (c) check at `gates.py:552` already calls `_is_positive_status_row(line)`. No change needed here.
- Section-scoping state machine: **(ii) Reusable with extension.** The current `## ` header scoping is already in place (`gates.py:532-533`). The problem is that it's too coarse — it needs refinement to distinguish verification-result tables from enumerative-evidence tables within a verification section. The extension shape would be: either (a) tighten the scoping to require a `### ` sub-header with specific patterns (but QA reports use `### Check N` as sub-headers, and the enumerative tables are WITHIN those checks), or (b) use table-header-column heuristics (presence of a "Status" or "Result" column in the header row), or (c) use the BACKLOG entry's option (b) status-cell heuristic (at least one row already contains a positive-status token → it's a verification table).

**A3 — Rule 22 (d) hedging-detector:**
- `_is_positive_status_row`: **(i) Directly reusable — already consumed.** The (d) check at `gates.py:560` already calls `_is_positive_status_row(line)` to identify which rows to inspect for hedging keywords. No change needed to this consumer call.
- Section-scoping state machine: **(ii) Reusable with extension.** The (d) check currently iterates ALL lines (`gates.py:559: for i, line in enumerate(lines, 1)`). If the (d) check were brought under the same section-scoping as the (c) check (only inspect rows in verification sections), it would eliminate FPs from non-verification-section tables. However, the triggering artifact shows the (d) FPs occur in genuine verification-table rows — section-scoping alone would NOT close this FP. The extension needed is cell-scoping: restrict the hedging keyword match to specific cells (e.g., the status cell or adjacent cells) rather than the entire row.

---

## Section D — Q4: Fix-Shape Interaction Matrix (3×3 Table)

### CEO Flags fix shapes (from BACKLOG)

| Option | CEO Flags | Rule 22 (c) | Rule 22 (d) |
|---|---|---|---|
| **(a) Null-token allowlist** | `_gate_ceo_flags` at `gates.py:215-218` OR `parser.py:35` — add prefix-match for `none`, `n/a`, `no flags`, `nothing`, `clean` etc. No new helper needed (inline predicate). | No effect — (c) FP is about table-type classification, not null tokens. | No effect — (d) FP is about domain-term substring matching, not null tokens. |
| **(b) Presence-of-issue heuristic** | `_gate_ceo_flags` at `gates.py:217` — replace `if flags:` with issue-shape token check. New helper: `_contains_issue_signal(text: str) -> bool`. | No effect. | No effect. |
| **(c) Require structured marker** | `parser.py:33` — change `if line.startswith("- "):` to require `"- "` bullet AND exclude prose-only (non-bullet) content. No new helper. | No effect. | No effect. |

### Rule 22 (c) row-status fix shapes (from BACKLOG)

| Option | CEO Flags | Rule 22 (c) | Rule 22 (d) |
|---|---|---|---|
| **(a) Section-scoping refinement** | No effect. | `_gate_rule_22_verification` (c) check at `gates.py:527-556` — refine `in_verification_section` tracking to distinguish verification-result tables from enumerative tables. Options: `### ` sub-header tracking, column-header heuristic, or dedicated verification-table-start marker. Extends existing section-scoping state machine. | **Partial** — if the (d) check is brought under the same section-scoping, it would skip non-verification-section tables. But the triggering (d) FPs are IN verification tables, so this alone doesn't close (d). |
| **(b) Status-cell heuristic** | No effect. | `_gate_rule_22_verification` (c) check at `gates.py:539-540` — after entering `in_data = True`, scan the first few data rows for positive-status tokens. If none found, treat as a non-verification table and skip. New helper: `_table_has_status_column(rows: list[str]) -> bool`. | **Partial** — same as (a): narrows which tables are inspected, but (d) FPs occur in tables that DO have status columns. |
| **(c) Opt-out marker** | No effect. | `_gate_rule_22_verification` (c) check — check for `<!-- enumerative-table -->` comment before table. No new helper, but requires governance edit to publish the convention. | No effect — (d) operates on individual rows, not table-level markers. |

### Rule 22 (d) hedging-detector fix shapes (from BACKLOG)

| Option | CEO Flags | Rule 22 (c) | Rule 22 (d) |
|---|---|---|---|
| **(a) Word-boundary + context match** | No effect. | No effect. | `_gate_rule_22_verification` (d) check at `gates.py:562-563` — replace `if kw in lower:` with word-boundary regex (`\bpending\b`) + context-anchoring (require adjacent hedging-context words like `pending verification`, `pending review`). Alternatively, require the hedging keyword to NOT be inside backticks, JSON, or function-name context. Edits the match predicate. New helper: `_is_hedging_context(line: str, keyword: str) -> bool`. |
| **(b) Per-project domain-term allowlist** | No effect. | No effect. | `gates.py` top-level or `config.json` — new config field mapping project → domain terms exempt from hedging check. `_gate_rule_22_verification` reads the allowlist and skips matching keywords. Schema change in `config.json`. Largest of the three options. |
| **(c) Cell-scope match** | No effect. | No effect. | `_gate_rule_22_verification` (d) check at `gates.py:561-563` — instead of `if kw in lower:` (whole row), split the row into cells, identify the status cell (or cells adjacent to the status token), and only match hedging keywords in those cells. New helper: `_hedging_in_status_cells(line: str, keyword: str) -> bool`. |

### Cross-site composition analysis

The matrix shows that **no single fix-shape option from any BACKLOG entry closes more than one FP pattern**. All CEO Flags options are independent of both Rule 22 sub-checks. All Rule 22 (c) options have at most "partial" interaction with (d). All Rule 22 (d) options are independent of both (c) and CEO Flags.

The cleanest cross-site composition is: CEO Flags option (a) (null-token allowlist) + Rule 22 (c) option (a) or (b) (section-scoping refinement or status-cell heuristic) + Rule 22 (d) option (c) (cell-scope match). This combination addresses each FP at the structurally correct level without forced abstraction sharing.

---

## Section E — Q5: Recommendation

### Recommendation: **5c — Mixed shape**

**Partition:** Rule 22 (c) and (d) share a coordinated fix within `_gate_rule_22_verification`; CEO Flags is independent.

#### Part 1: CEO Flags — independent fix

**Fix shape:** BACKLOG option (a) — null-token allowlist.

**Site:** Two candidate sites, choose one:
- **Preferred (gate-side):** `_gate_ceo_flags` at `gates.py:215-218`. Add a null-token prefix check before the `if flags:` gate fire. This keeps the parser thin and the semantic classification in the gate where it belongs.
- **Alternative (parser-side):** `parser.py:35`. Extend the existing `txt.lower() not in ("none", "n/a")` check to a prefix-match or token-match. This is simpler but mixes content classification into the extraction layer.

**Helper signature (if gate-side):** `_is_null_flag_declaration(flag_text: str) -> bool` — returns `True` if the text is a null-declaration (starts with null tokens like `none`, `n/a`, `no flags`, `nothing`, `clean`, case-insensitive, with or without trailing explanatory content).

**LOC estimate:** ~15 production + ~20 test. Confidence: high.

**Closest BACKLOG option:** Option (a) — null-token allowlist. No divergence.

#### Part 2: Rule 22 (c) + (d) — coordinated fix within `_gate_rule_22_verification`

**Fix shape for (c):** BACKLOG option (b) — status-cell heuristic. This is preferred over option (a) (section-scoping refinement) because:
- The current section-scoping already works at the `## ` header level. The FP occurs because enumerative tables are nested WITHIN `### Check N` subsections inside a `## Verification Checks` section. Refining the scoping to `### ` headers would require QA reports to use specific sub-header patterns for result tables vs. evidence tables — this is a governance-dependent convention that doesn't exist yet.
- The status-cell heuristic is content-intrinsic: a table is a verification-result table if and only if it contains rows with positive-status tokens. Enumerative tables (heading lists, proposal-ID maps, rule-numbering) never contain `✅`, `PASS`, `OK`, etc. This is a self-certifying property of the content.

**Implementation shape for (c):** After entering a table (when `_TABLE_SEPARATOR_RE` matches and `in_data` becomes `True`), track whether any row in the current table has matched `_is_positive_status_row()`. Defer "missing status" failures until the table ends. If no row in the table matched as a positive-status row, the entire table is treated as non-verification and all deferred failures are discarded.

**Fix shape for (d):** BACKLOG option (c) — cell-scope match. This is preferred over option (a) (word-boundary + context) because:
- Word-boundary matching (`\bpending\b`) would still fire on `pending=5` and `"pending": N` and state names like `pending` — these are all word-boundary-bounded uses of the domain term.
- Context-anchoring (`pending verification`, `pending review`) is fragile — it requires enumerating valid hedging contexts and will miss novel phrasings.
- Cell-scope matching is structurally precise: the hedging keyword should only trigger when it appears in or near the status cell (the cell that contains the positive-status token). Domain terms like `_run_pending`, `pending=5`, `"pending"` appear in description or evidence cells, not the status cell. This is the same bounded-cell-equality principle that `_is_positive_status_row()` already uses for status tokens.

**Helper signature for (d):** `_hedging_in_status_vicinity(line: str, keyword: str) -> bool` — splits the row into cells, identifies which cell(s) contain positive-status tokens, and checks for the hedging keyword only in those cells (and optionally adjacent cells). Returns `True` only if the hedging keyword appears in the status-bearing cell context, not in description/evidence cells.

**Section-scoping extension for (d):** As a secondary improvement, the (d) check's iteration should be brought under the same `in_verification_section` scoping that the (c) check uses. This is a one-line change (add `if not in_verification_section: continue` to the (d) loop) and closes the edge case where hedging keywords appear in non-verification-section tables. This does NOT close the triggering (d) FP (which occurs in verification-section tables) but prevents a future FP class.

**Coordination between (c) and (d):** The two fixes share the iteration context (same `lines`, same `_is_positive_status_row` helper, same section-scoping state). Shipping them together in one edit to `_gate_rule_22_verification` is natural — the function is ~90 lines and both sub-checks are adjacent. The (c) fix (status-cell heuristic for table classification) and the (d) fix (cell-scope match for hedging keywords) are structurally independent within the function but benefit from shared context: both use `_is_positive_status_row()` and both operate on the same parsed content.

**LOC estimate for (c) + (d) combined:** ~40-60 production + ~40-60 test. Confidence: medium (the cell-scope match for (d) requires careful cell-splitting logic and regression testing against existing hedging-detection test cases).

### Summary

| Entry | Fix | Helper | BACKLOG entries closed |
|---|---|---|---|
| CEO Flags | Option (a) null-token allowlist | `_is_null_flag_declaration(flag_text: str) -> bool` | 1 (ceo_flags FP) |
| Rule 22 (c) | Option (b) status-cell heuristic | Table-level verification-table classification (inline or extracted) | 1 (rule_22 (c) row-status FP) |
| Rule 22 (d) | Option (c) cell-scope match + section-scoping extension | `_hedging_in_status_vicinity(line: str, keyword: str) -> bool` | 1 (hedging-detector FP) |

**Total BACKLOG entries closed:** 3 of 3.

**Total LOC estimate:** ~55-75 production + ~60-80 test. Confidence: medium overall.

### Backward compatibility

- **CEO Flags:** The null-token allowlist makes the gate more permissive (fewer fires). No existing test or in-flight plan depends on the gate firing on null declarations. Backward compatible.
- **Rule 22 (c):** The status-cell heuristic makes the (c) check more permissive for tables that lack any positive-status rows. Existing tests that exercise the (c) check use tables WITH positive-status tokens — those continue to fire correctly. The 4 existing test fixtures updated by the 2026-05-24 ship (adding `## Deliverable Verification` headers) remain valid. Backward compatible.
- **Rule 22 (d):** Cell-scope matching makes the (d) check more precise (fewer fires on domain terms in non-status cells). The existing hedging-detection test cases use rows where the hedging keyword appears as the status itself (e.g., `| Check | pending |`) — these should still fire because the keyword IS in the status cell. Requires careful regression testing. Backward compatible with correct implementation.

### Daemon restart

**Required: yes.** All three fixes touch `gates.py` (and possibly `parser.py` for the CEO Flags alternative). Bellows does not hot-reload these modules. The running daemon will continue executing pre-fix code until restarted. Same pattern as the 2026-05-24 ship.

### Closest BACKLOG option per entry and divergences

- **CEO Flags:** Closest = option (a) null-token allowlist. No divergence — recommendation matches the BACKLOG entry's first-suggested option.
- **Rule 22 (c):** Closest = option (b) status-cell heuristic. The BACKLOG entry suggests option (a) section-scoping first ("analogous to the 2026-05-24 section-scoping fix"). This recommendation diverges: the 2026-05-24 section-scoping is already in place and is the CAUSE of the current FP (too-coarse `## ` header matching). Refining the scoping further (option (a)) would require governance-dependent sub-header conventions. The status-cell heuristic (option (b)) is content-intrinsic and self-certifying. Divergence is justified by the structural analysis in Section A2.
- **Rule 22 (d):** Closest = option (c) cell-scope match. The BACKLOG entry also suggests option (a) word-boundary + context as an alternative. This recommendation diverges from (a) because word-boundary matching doesn't close the FP (domain terms like `pending` ARE word-boundary-bounded). Cell-scope match is structurally precise. Divergence is justified by the structural analysis in Section A3.

### Flags for CEO

- **No entries closed fewer than 3.** The recommendation addresses all three BACKLOG entries.
- **One structural divergence from BACKLOG framing:** The BACKLOG entries suggest the three FPs share "the same root-cause shape: gate parses field content uniformly without scoping." The diagnostic confirms the root-cause SHAPE is similar (uniform parsing without context-appropriate scoping) but the root-cause MECHANISMS are distinct (null-declaration blindness vs. table-type blindness vs. cell-scope blindness). This means a single shared helper cannot close all three — the mixed shape (5c) is the correct abstraction. The BACKLOG's coordinated-fix hypothesis is partially validated: (c) and (d) DO coordinate naturally within `_gate_rule_22_verification`, but CEO Flags is structurally independent.
- **Rule 22 (c) option (a) "section-scoping" from BACKLOG is not the right fix shape.** The BACKLOG entry frames option (a) as "analogous to the 2026-05-24 section-scoping fix." In fact, the 2026-05-24 section-scoping IS already in place and is contributing to the FP by being too coarse. The fix is not MORE section-scoping; it's a different scoping primitive (table-type classification). This is not infeasibility — option (a) could work with a refined scoping model — but option (b) is structurally cleaner and doesn't require governance changes.

---

## Output Receipt

**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Joint call-site characterization of three 2026-05-27 gate false-positive BACKLOG entries. Traced each FP to its exact gate function, parsing logic, and structural content shape. Evaluated four abstraction-convergence options (single helper, section-scoping primitive, three independent, mixed). Assessed reusability of 2026-05-24 helpers. Built 3x3 fix-shape interaction matrix. Recommended 5c mixed shape: CEO Flags independent (null-token allowlist) + Rule 22 (c)/(d) coordinated (status-cell heuristic + cell-scope match).

### Files Deposited
- `bellows/knowledge/research/gate-fp-coordinated-shape-2026-05-27.md` — this diagnostic findings document

### Files Created or Modified (Code)
- None (read-only diagnostic)

### Decisions Made
- Option D (mixed shape) selected as abstraction convergence model — justified by structural divergence between CEO Flags (free-text field) and Rule 22 sub-checks (markdown table rows)
- Rule 22 (c) option (b) preferred over BACKLOG-suggested option (a) — justified by 2026-05-24 section-scoping already being in place and being too coarse
- Rule 22 (d) option (c) preferred over option (a) — justified by word-boundary matching not closing the FP

### Flags for CEO
- BACKLOG's coordinated-fix hypothesis partially validated: (c) and (d) coordinate naturally, but CEO Flags is structurally independent. Three BACKLOG entries still closeable but via mixed shape (5c), not single coordinated fix (5a).
- Rule 22 (c) BACKLOG option (a) "section-scoping" divergence flagged — existing section-scoping is too coarse, not absent. Fix is table-type classification, not more section-scoping.

### Flags for Next Step
- The CEO Flags fix has a parser-side alternative (`parser.py:35`) that may be simpler than the gate-side approach. The executable plan should evaluate both sites and choose.
- The Rule 22 (d) cell-scope match requires careful regression testing — existing hedging-detection tests may use row layouts where the keyword is in a non-status cell (which would change behavior). Enumerate existing test fixtures before implementing.
- Consider whether the (d) section-scoping extension (bringing the (d) loop under `in_verification_section`) should be shipped as part of this fix or deferred as incremental hardening.
