# Diagnostic — Multi-Line Bold Header Parser Gap

**Project:** bellows | **Date:** 2026-05-10 | **Author:** Planner | **Tier:** Small | **Total Steps:** 1 | **pause_for_verdict:** always

---

## Context

BACKLOG `2026-05-10: Multi-line bold plan headers bypass _parse_plan_header Strategy 2` documents a hypothesized parser gap. The hypothesis: when a plan uses multi-line bold-Markdown headers (each field on its own line, no pipe separators), `gates.py::_parse_plan_header` Strategy 2 reads only the first non-empty line after `# Title` and the regex captures a single `{project: "..."}` dict, missing all subsequent header fields including `pause_for_verdict`.

The BACKLOG entry was authored by the Planner from symptom observation, not from code-traced verification. Today's `executable-startup-sweep-extract-2026-05-10` triggered the symptom (Bellows logged `"has 2 steps but no pause_for_verdict header"` and auto-advanced through Step 1), but the root cause has not been independently verified by an agent who has read the code and tested fixtures.

Before authoring a fix executable, the Planner needs the SA to:
1. Empirically verify the parser behavior with fixtures mirroring real plan header structures.
2. Confirm the parse-strategy mechanism is the actual auto-advance vector (vs. some other code path).
3. Survey the live plan population (last 30 days) to size the impact.
4. Cost-evaluate the three proposed fix shapes (a/b/c) with concrete LOC and risk estimates.

This diagnostic surfaces those facts so the Planner can scope a sized executable with verified fix-shape choice.

---

## STEP 1 — Systems Analyst: verify header parser gap and size the fix

**Agent:** Bellows Systems Analyst (`bellows/agents/BELLOWS_SA.md`)
**Working directory:** `/Users/marklehn/Desktop/GitHub/`

**Deposits:**
- `bellows/knowledge/research/header-parser-multiline-bold-gap-2026-05-10.md`

### Prompt

You are the Bellows Systems Analyst. Read your agent file at `bellows/agents/BELLOWS_SA.md` before starting. Today's investigation is parser-mechanics-scoped — your job is to verify and characterize, not to design a fix. The Planner makes the fix-shape decision after reading your findings.

This is a single-step investigation. Read-only on production code. You may create temporary fixture files in `/tmp/` or use Python REPL for empirical testing — but do NOT modify `gates.py`, `bellows.py`, or any test file in the bellows repo.

Answer the following five questions and write a single findings file at `bellows/knowledge/research/header-parser-multiline-bold-gap-2026-05-10.md`. Use the questions as section headers. Quote evidence verbatim (code snippets with line numbers, REPL output, file paths).

### Q1. Empirical verification of the parser gap

The Planner's hypothesis: `_parse_plan_header()` in `bellows/gates.py` (≈ lines 22–73 per recent diagnostics) reads only the first non-empty line after `# Title` and runs the pipe-format regex on it. When that line is a single bold-Markdown field with no pipe separators (e.g., `**Project:** bellows`), only `{project: "bellows"}` is captured and all subsequent header fields are invisible.

To verify empirically:

1. Read `gates.py::_parse_plan_header` in full. Quote the function body with line numbers in your findings.
2. Open a Python REPL in `/Users/marklehn/Desktop/GitHub/bellows/`. Construct a fixture string that exactly mirrors today's `executable-startup-sweep-extract-2026-05-10.md` header (multi-line bold form):

```python
fixture = """# Executable — Extract `_perform_startup_sweep` from `Bellows.start()`

**Project:** bellows
**Date:** 2026-05-10
**Author:** Planner
**Tier:** Small
**Total Steps:** 2

**pause_for_verdict:** after_step_1

---

## Context
..."""
```

3. Import `gates` and call `gates._parse_plan_header(fixture)`. Quote the literal returned dict in your findings.
4. Repeat with a single-line pipe-format header (mirrors today's `executable-rule-20-single-source-2026-05-10.md`):

```python
fixture_pipe = """# Executable — Rule 20 Self-Check Block Single-Source File

**Project:** bellows | **Date:** 2026-05-10 | **Author:** Planner | **Tier:** Small-to-Medium | **Total Steps:** 2 | **pause_for_verdict:** after_step_1

---

## Context
..."""
```

5. Compare the two returned dicts. Confirm or refute: the multi-line form returns only `{project: ...}` (or similar single-key dict), while the pipe-format returns all six fields including `pause_for_verdict`.

If the hypothesis is **refuted** (multi-line form actually returns all fields), STOP — the BACKLOG entry needs rewriting and the rest of the diagnostic is moot. Document the unexpected behavior and propose a follow-up investigation.

If the hypothesis is **confirmed**, proceed to Q2.

### Q2. Auto-advance mechanism trace

Trace the code path that consumes `pause_for_verdict` and triggers (or fails to trigger) the auto-advance. Specifically:

1. Read `bellows.py` and locate every place `pause_for_verdict` is read from a parsed header dict. Quote each location with line numbers and surrounding context (5 lines each).
2. Read `gates.py::header_says_pause` (or equivalent function). Quote it in full.
3. Identify the call chain: which function reads the plan header → passes the dict where → which function checks `pause_for_verdict` → which function decides whether to dispatch the next step.
4. Confirm that if `_parse_plan_header` returns a dict missing `pause_for_verdict`, the downstream check sees empty/falsy and auto-advances. (If there is fallback logic that reads the header by a different path, document it.)

### Q3. Live plan population audit

Enumerate plans in the last 30 days (since 2026-04-10) across all watched projects and classify each plan's header format. Sources:

- `bellows/knowledge/decisions/` and `bellows/knowledge/decisions/Done/`
- `invoice-pulse/knowledge/decisions/` and `invoice-pulse/knowledge/decisions/Done/`

For each `.md` file with a creation/modification date in that 30-day window:

1. Read the first ~15 lines.
2. Classify the header format as one of: **single-line pipe** (one line of bold-Markdown with pipe separators after the `# Title`), **multi-line bold** (multiple lines of bold-Markdown, no pipe separators after the `# Title`), **YAML frontmatter** (file starts with `---\n` block), or **other/none** (no recognizable header).
3. For each plan that includes `pause_for_verdict` anywhere in its header lines (any form), note whether the parser would have correctly captured it. (For multi-line bold headers with `pause_for_verdict` on a non-first line, the parser misses it.)

Deposit a count table:

| Header format | Count (last 30 days) | Plans with `pause_for_verdict` declared | Plans where parser would miss `pause_for_verdict` |
|---|---|---|---|

Also identify any in-flight plans (in `decisions/` not `decisions/Done/`) whose header format would cause silent auto-advance. List them by full path.

### Q4. Fix shape cost evaluation

The BACKLOG entry proposes three fix shapes:
- **(a)** Extend `_parse_plan_header` Strategy 2 to read multiple consecutive bold-Markdown lines until a non-bold line, parsing each independently.
- **(b)** Add a new Strategy 3 specifically for multi-line bold blocks.
- **(c)** Governance-only — mandate single-line pipe-format headers in PLANNER_TEMPLATE.

For each fix shape, evaluate:

| Aspect | Shape (a) | Shape (b) | Shape (c) |
|---|---|---|---|
| Code LOC delta in `gates.py` | | | |
| Regression test count | | | |
| Risk to existing single-line pipe-format plans | | | |
| Risk to existing YAML-frontmatter plans (if any in Q3 audit) | | | |
| Cost to migrate existing in-flight multi-line bold plans | | | |
| Cross-cutting changes (docs, agent files, etc.) | | | |
| Hidden-substitution failure-mode risk (does this lock in a single format the way Rule 20 single-source did)? | | | |

For shape (a) specifically, sketch the actual regex or parser logic you would write. Cite the existing Strategy 2 code (line numbers in `gates.py`) you would modify, and propose the surgical edit. This is not the executable — it's a feasibility sketch to confirm the BACKLOG entry's "~10–15 LOC" estimate.

### Q5. Hidden alternatives

The BACKLOG entry lists three fix shapes the Planner thought of. Are there others worth surfacing? Examples to consider:

- **(d)** Single-source the canonical plan-header format in a `PLAN_HEADER_TEMPLATE.md` file at governance root (analogous to today's Rule 20 single-source migration). Plans reference it; the Planner cannot author a non-conforming header by construction.
- **(e)** Add a Bellows-side validation check that warns when `_parse_plan_header` returns a dict missing expected keys (e.g., warn-and-proceed when total_steps > 1 and no `pause_for_verdict`).
- **(f)** Bellows-side governance: emit a one-line summary at plan-dispatch time showing all parsed header fields, so the CEO can spot a parser miss immediately rather than 5 minutes later when the auto-advance happens.

For each alternative, briefly evaluate cost/risk/effectiveness. If you identify a fix shape not on the BACKLOG entry's list AND not in (d)/(e)/(f), document it.

### Output

Deposit findings at `bellows/knowledge/research/header-parser-multiline-bold-gap-2026-05-10.md`. Sections in order matching Q1–Q5.

### Output Receipt

When complete:

```
**Step:** 1
**Status:** Complete
**Deposits:**
- bellows/knowledge/research/header-parser-multiline-bold-gap-2026-05-10.md (created)
```

STOP after Step 1. This is a single-step diagnostic. The Planner reviews the findings directly per Rule 22 before authoring any fix executable.

---

## Deliverables Summary

| Step | Agent | Deliverable | Location |
|------|-------|-------------|----------|
| 1 | SA | findings file (created) | `bellows/knowledge/research/header-parser-multiline-bold-gap-2026-05-10.md` |
