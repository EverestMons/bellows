# Executable — Multi-Line Bold Header Parser Fix + Defensive Defaults

**Project:** bellows | **Date:** 2026-05-10 | **Author:** Planner | **Tier:** Small | **Total Steps:** 2 | **pause_for_verdict:** after_step_1

---

## Context

Closes BACKLOG `2026-05-10: Multi-line bold plan headers bypass _parse_plan_header Strategy 2`. Diagnostic at `bellows/knowledge/research/header-parser-multiline-bold-gap-2026-05-10.md` empirically confirmed the root cause via REPL fixtures, traced the call chain, audited the 30-day plan population (3 affected plans all in Done/, zero in-flight risk), wrote a concrete ~10 LOC edit for Shape (a), and surfaced Shape (g) as a defensive complement.

**CEO selected combination (a) + (e) + (g) per 2026-05-10 chat.** Implementation interpretation of (e): **extend the existing warning at `bellows.py:268`**, not promote it to a blocking gate. Rationale: (g) defensive default already catches the failure-mode (sparse header → safe-pause). Promoting the warning to a blocking gate would break legitimate plans that intentionally auto-advance without declaring `pause_for_verdict`. (e.2 observability-extension) is the safe interpretation; (e.1 blocking gate) would be over-engineering for a population of 3 historical plans.

**Three coordinated changes:**

1. **(a) Parser fix.** Extend `gates.py::_parse_plan_header` Strategy 2 to collect all consecutive bold-Markdown lines until a non-bold line or `---` rule, joining them with `|` so the existing regex parses them unchanged. ~10 LOC in `gates.py`.

2. **(g) Defensive default.** In `bellows.py::run_plan` after the header parse: if `total_steps > 1` and `len(header) < 3`, default `pause_for_verdict` to `"after_step_1"` and emit a warning. ~5 LOC in `bellows.py`.

3. **(e.2) Warning extension.** Extend the existing `bellows.py:268` warning to surface ALL missing expected keys for multi-step plans (not just `pause_for_verdict`), so the operator sees the parser state at dispatch. ~3 LOC modification at line 268.

**Total scope:** ~18 LOC across 2 files, 3 changes. Tests: ~5 new regression tests in `tests/test_gates.py` + ~2 in `tests/test_bellows.py`.

---

## Execution Map

Step 1 (DEV) → Step 2 (QA)

---

## STEP 1 — Developer: implement parser fix + defensive default + warning extension

**Agent:** Bellows Developer (`bellows/agents/BELLOWS_DEVELOPER.md`)
**Working directory:** `/Users/marklehn/Desktop/GitHub/bellows/`

**Deposits:**
- `bellows/gates.py` (modified — Strategy 2 multi-line extension)
- `bellows/bellows.py` (modified — defensive default + warning extension)
- `bellows/tests/test_gates.py` (modified — 5 new regression tests)
- `bellows/tests/test_bellows.py` (modified — 2 new regression tests)
- `bellows/knowledge/development/header-parser-multiline-fix-2026-05-10.md` (dev log)

### Prompt

You are the Bellows Developer. Read your agent file at `bellows/agents/BELLOWS_DEVELOPER.md` and the diagnostic findings at `bellows/knowledge/research/header-parser-multiline-bold-gap-2026-05-10.md` before making any edits. The diagnostic includes the exact ~10 LOC edit sketch for the parser fix in section Q4 — use that as your reference implementation.

This is a small, well-bounded fix with three coordinated changes. No test deletions, no scope creep.

### Edit 1 — `gates.py` Strategy 2 extension

Locate `_parse_plan_header` in `bellows/gates.py` (the diagnostic cited lines 22–71). Find the inner loop in Strategy 2 that currently reads only the first non-empty line after `# Title`:

```python
if stripped.startswith("# "):
    # Found the title line — look for the next non-empty line
    for j in range(i + 1, len(lines)):
        candidate = lines[j].strip()
        if candidate:
            header_line = candidate
            break
    break
```

Replace it with the diagnostic's proposed edit — collect all consecutive bold-Markdown lines:

```python
if stripped.startswith("# "):
    # Collect all consecutive bold-Markdown header lines after title.
    # Handles both single-line pipe-format (one line of **key:** val | **key:** val)
    # and multi-line bold (each **key:** val on its own line, separated by blanks).
    # The collected lines are joined with " | " so the existing pipe-separator
    # regex below parses them uniformly. Closes BACKLOG 2026-05-10
    # multi-line bold header parser gap.
    header_lines = []
    for j in range(i + 1, len(lines)):
        candidate = lines[j].strip()
        if not candidate:
            # Skip blank lines (both before first field and between fields)
            continue
        if candidate.startswith("---"):
            # Horizontal rule terminates the header block
            break
        if candidate.startswith("**"):
            header_lines.append(candidate)
        else:
            # Non-bold, non-blank line — header block is over
            break
    header_line = " | ".join(header_lines) if header_lines else None
    break
```

Update the function's docstring (lines 23–28) to reflect the multi-line support:

```python
    """Extract plan header fields. Tries YAML frontmatter first, then bold-Markdown format.

    Supported formats:
    1. YAML frontmatter: file starts with ``---\\n...\\n---\\n``
    2. Bold-Markdown header: ``**Key:** value | **Key:** value`` on a single line
       OR ``**Key:** value`` on each of multiple consecutive lines, after a
       ``# Title`` line. Blank lines between fields are tolerated; a ``---``
       horizontal rule or any non-bold non-blank line terminates the header block.
    Returns {} if neither format is found.
    """
```

### Edit 2 — `bellows.py` defensive default + warning extension

Locate the block in `run_plan()` around line 247–270 (per diagnostic). Find:

```python
        header = gates._parse_plan_header(metadata_text)
        model = header.get("Model", header.get("model", config["default_model"]))
```

After the model line, insert the defensive default (Shape g):

```python
        # Defensive default (Shape g, BACKLOG 2026-05-10 closure): if header
        # parse looks sparse for a multi-step plan, default to safe-pause
        # rather than auto-advance. Catches future parser-miss classes.
        if total_steps > 1 and len(header) < 3:
            if not header.get("pause_for_verdict", "").strip():
                header["pause_for_verdict"] = "after_step_1"
                print(f"Bellows: ⚠️  sparse header ({len(header)} keys) for {total_steps}-step plan — defaulting pause_for_verdict to after_step_1 (safe-pause)")
```

**Note:** The defensive default must run AFTER `total_steps` is computed. Per the diagnostic call chain (Q2), `extract_total_steps()` is called at `bellows.py:237` BEFORE `_parse_plan_header()` at line 247. Confirm the variable is in scope when you insert the block. If `total_steps` is not yet computed at this site, move the block to immediately after `total_steps = extract_total_steps(metadata_text)` AND `header = gates._parse_plan_header(metadata_text)` — whichever comes second. Read the surrounding code (~30 lines) before inserting to confirm scope.

Find the existing warning at line 268:

```python
        if total_steps > 1 and not header.get("pause_for_verdict", "").strip():
            print(f"Bellows: ⚠️  {plan_name} has {total_steps} steps but no pause_for_verdict header — Bellows will auto-advance. Add 'pause_for_verdict: after_step_1' to the plan header.")
```

Extend this warning (Shape e.2 — observability extension, NOT promotion to blocking gate). The defensive default above will have set `pause_for_verdict` if it was missing, so this exact warning may no longer fire in the sparse-header case. Instead, replace it with a richer observability message that fires when the header is sparse OR `pause_for_verdict` is missing:

```python
        expected_keys = {"project", "date", "author", "total_steps", "pause_for_verdict"}
        missing_keys = expected_keys - set(header.keys())
        if total_steps > 1 and missing_keys:
            print(f"Bellows: ⚠️  {plan_name} has {total_steps} steps but parsed header is missing: {sorted(missing_keys)}. Parsed keys: {sorted(header.keys())}. If pause_for_verdict was missing, the defensive default has set it to after_step_1.")
```

This preserves the operator-facing diagnostic signal even after the defensive default fills in `pause_for_verdict`.

### Edit 3 — `tests/test_gates.py` — 5 new regression tests

Add 5 tests to `bellows/tests/test_gates.py`. Place them at the end of the existing test functions for `_parse_plan_header` (use grep to find the section):

```python
def test_parse_plan_header_multi_line_bold_returns_all_fields():
    """Multi-line bold-Markdown headers (one **key:** val per line) parse all fields.
    Regression for BACKLOG 2026-05-10 multi-line bold parser gap."""
    text = """# Executable — Test

**Project:** bellows
**Date:** 2026-05-10
**Author:** Planner
**Tier:** Small
**Total Steps:** 2

**pause_for_verdict:** after_step_1

---

## Context
"""
    result = gates._parse_plan_header(text)
    assert result.get("project") == "bellows"
    assert result.get("date") == "2026-05-10"
    assert result.get("author") == "Planner"
    assert result.get("tier") == "Small"
    assert result.get("total_steps") == "2"
    assert result.get("pause_for_verdict") == "after_step_1"


def test_parse_plan_header_single_line_pipe_still_works():
    """Single-line pipe-format headers continue to parse correctly after multi-line extension."""
    text = """# Executable — Test

**Project:** bellows | **Date:** 2026-05-10 | **Author:** Planner | **Tier:** Small | **Total Steps:** 2 | **pause_for_verdict:** after_step_1

---

## Context
"""
    result = gates._parse_plan_header(text)
    assert result.get("project") == "bellows"
    assert result.get("pause_for_verdict") == "after_step_1"
    assert len(result) == 6


def test_parse_plan_header_multi_line_bold_with_blank_lines():
    """Blank lines between multi-line bold fields are tolerated."""
    text = """# Test

**Project:** bellows

**Date:** 2026-05-10


**pause_for_verdict:** always

---
"""
    result = gates._parse_plan_header(text)
    assert result.get("project") == "bellows"
    assert result.get("date") == "2026-05-10"
    assert result.get("pause_for_verdict") == "always"


def test_parse_plan_header_horizontal_rule_terminates_header_block():
    """A --- horizontal rule terminates the header block; bold lines after it are ignored."""
    text = """# Test

**Project:** bellows
**Date:** 2026-05-10

---

**This should NOT be parsed:** because it's after the rule
"""
    result = gates._parse_plan_header(text)
    assert result.get("project") == "bellows"
    assert result.get("date") == "2026-05-10"
    assert "this_should_not_be_parsed" not in result


def test_parse_plan_header_non_bold_line_terminates_header_block():
    """A non-bold, non-blank line terminates the header block."""
    text = """# Test

**Project:** bellows
**Date:** 2026-05-10
This is prose, not a header field.
**Not Parsed:** because prose ended the block

---
"""
    result = gates._parse_plan_header(text)
    assert result.get("project") == "bellows"
    assert result.get("date") == "2026-05-10"
    assert "not_parsed" not in result
```

### Edit 4 — `tests/test_bellows.py` — 2 new regression tests

Add 2 tests to `bellows/tests/test_bellows.py` for the defensive default (Shape g). Use grep to find the appropriate section (likely near tests for `run_plan` header handling).

```python
def test_defensive_default_sets_pause_for_verdict_when_header_sparse(tmp_path, monkeypatch):
    """Shape g safety net: when header parse returns < 3 keys for a multi-step plan,
    pause_for_verdict defaults to after_step_1 to prevent silent auto-advance.
    Regression for BACKLOG 2026-05-10."""
    # Construct a plan whose header would parse sparsely (deliberately malformed
    # or future parser-miss). Multi-step plan with ## STEP headers, but a header
    # the parser can't fully read.
    plan_content = """# Executable — Test

NOT A VALID HEADER LINE

## STEP 1 — first
do something

## STEP 2 — second
do another thing
"""
    # The actual assertion: after run_plan reads this, header.get("pause_for_verdict")
    # should return "after_step_1" due to the defensive default. Test by inspecting
    # the dispatch path or by mocking _parse_plan_header to return a sparse dict.
    import gates as g
    # Mock the parser to return a sparse dict simulating a future parser-miss
    sparse_header = {"project": "bellows"}
    # Inject defensive default behavior: simulate what bellows.py:run_plan does
    total_steps = 2
    if total_steps > 1 and len(sparse_header) < 3:
        if not sparse_header.get("pause_for_verdict", "").strip():
            sparse_header["pause_for_verdict"] = "after_step_1"
    assert sparse_header["pause_for_verdict"] == "after_step_1"


def test_defensive_default_does_not_override_explicit_pause_for_verdict(tmp_path, monkeypatch):
    """The defensive default must NOT override an explicit pause_for_verdict value."""
    sparse_header = {"project": "bellows", "pause_for_verdict": "always"}
    total_steps = 3
    if total_steps > 1 and len(sparse_header) < 3:
        if not sparse_header.get("pause_for_verdict", "").strip():
            sparse_header["pause_for_verdict"] = "after_step_1"
    assert sparse_header["pause_for_verdict"] == "always"
```

Note: the test pattern above is illustrative — the actual tests should exercise production code paths rather than re-implementing the logic. If the DEV finds that exercising `run_plan` directly is impractical due to side effects (subprocess calls, file moves), the alternative is to extract the defensive-default logic into a small helper function in `bellows.py` (e.g., `_apply_defensive_header_defaults(header, total_steps) -> dict`) and test that helper directly. **Use your judgment** — pick whichever approach gives high-fidelity coverage without test-side mocking gymnastics.

### Test discipline

Run the full bellows test suite (`pytest` from `/Users/marklehn/Desktop/GitHub/bellows/`) after the edits. Expected:

- Baseline: 246 passed, 1 pre-existing failure (`test_run_step_timeout`).
- After edits: ~253 passed (246 + 7 new), 1 pre-existing failure, 0 new failures.

If any pre-existing test fails that was passing before, stop and report — do NOT modify other tests.

### Dev log

Write a dev log at `bellows/knowledge/development/header-parser-multiline-fix-2026-05-10.md` covering:

1. The three concrete code edits (file, line range, summary).
2. The 7 new test functions added (names + what each verifies).
3. LOC delta per file, net total.
4. Test suite result: pass count delta, any unexpected behavior.
5. Behavioral spot-check: in a Python REPL, import gates, construct the multi-line bold fixture from the diagnostic's Q1, call `gates._parse_plan_header()`, and confirm all 6 fields are returned (vs. just `{'project': 'bellows'}` pre-fix).
6. Commit SHA.

### Output Receipt

```
**Step:** 1
**Status:** Complete
**Deposits:**
- bellows/gates.py (modified)
- bellows/bellows.py (modified)
- bellows/tests/test_gates.py (modified — 5 new tests)
- bellows/tests/test_bellows.py (modified — 2 new tests)
- bellows/knowledge/development/header-parser-multiline-fix-2026-05-10.md (created)
**Commit:** <short-sha>
**Test suite:** <passed_count> passed (delta: <delta>), 1 pre-existing failure, 0 new failures
```

STOP after Step 1.

---

## STEP 2 — QA: verify the fix

**Agent:** Bellows QA (`bellows/agents/BELLOWS_QA.md`)
**Working directory:** `/Users/marklehn/Desktop/GitHub/bellows/`

**Deposits:**
- `bellows/knowledge/qa/header-parser-multiline-fix-qa-2026-05-10.md` (QA report)
- `bellows/knowledge/qa/evidence/header-parser-multiline-fix-2026-05-10/` (evidence directory)
- `bellows/knowledge/qa/evidence/header-parser-multiline-fix-2026-05-10/repl-fixture-output.txt`
- `bellows/knowledge/qa/evidence/header-parser-multiline-fix-2026-05-10/test-suite-result.txt`
- `bellows/knowledge/qa/evidence/header-parser-multiline-fix-2026-05-10/code-grep-results.txt`

### Prompt

You are the Bellows QA agent. Read your agent file at `bellows/agents/BELLOWS_QA.md` and the dev log at `bellows/knowledge/development/header-parser-multiline-fix-2026-05-10.md` before starting.

### Verification matrix

| # | Property | How to check | Evidence file |
|---|----------|--------------|---------------|
| 1 | Parser fix: multi-line bold returns all fields | In Python REPL: `import gates; result = gates._parse_plan_header(fixture)` using the multi-line bold fixture from diagnostic Q1. Result must contain `project`, `date`, `author`, `tier`, `total_steps`, `pause_for_verdict`. | `repl-fixture-output.txt` |
| 2 | Parser fix: single-line pipe still works | Same REPL with the single-line pipe fixture. Must return 6 keys identical to pre-fix behavior. | `repl-fixture-output.txt` |
| 3 | Parser fix: blank lines between bold fields tolerated | Run `pytest tests/test_gates.py::test_parse_plan_header_multi_line_bold_with_blank_lines -v`. Must pass. | inline in report |
| 4 | Parser fix: `---` rule terminates header | Run `pytest tests/test_gates.py::test_parse_plan_header_horizontal_rule_terminates_header_block -v`. Must pass. | inline in report |
| 5 | Parser fix: non-bold line terminates header | Run `pytest tests/test_gates.py::test_parse_plan_header_non_bold_line_terminates_header_block -v`. Must pass. | inline in report |
| 6 | Defensive default fires on sparse multi-step header | Run `pytest tests/test_bellows.py::test_defensive_default_sets_pause_for_verdict_when_header_sparse -v`. Must pass. | inline in report |
| 7 | Defensive default does not override explicit value | Run `pytest tests/test_bellows.py::test_defensive_default_does_not_override_explicit_pause_for_verdict -v`. Must pass. | inline in report |
| 8 | Warning extension present in bellows.py | `grep -A 2 "parsed header is missing" /Users/marklehn/Desktop/GitHub/bellows/bellows.py` — must show the new richer warning message. | `code-grep-results.txt` |
| 9 | Defensive default present in bellows.py | `grep -A 3 "sparse header" /Users/marklehn/Desktop/GitHub/bellows/bellows.py` — must show the safe-pause default logic. | `code-grep-results.txt` |
| 10 | Strategy 2 extended in gates.py | `grep -A 5 "Collect all consecutive bold-Markdown" /Users/marklehn/Desktop/GitHub/bellows/gates.py` — must show the new collection loop. | `code-grep-results.txt` |
| 11 | Full test suite passes | `pytest` from bellows root. Must show ~253 passed (246 baseline + 7 new), 1 pre-existing failure, 0 new failures. | `test-suite-result.txt` |
| 12 | LOC delta matches estimate | Compute net LOC delta across `gates.py` + `bellows.py` + 2 test files. Expected ~18 LOC code + ~80 LOC tests = ~100 total. ±20 LOC tolerance. | inline in report |
| 13 | Behavioral end-to-end: parser correctly resolves the failure-case from earlier today | Read `bellows/knowledge/decisions/Done/executable-startup-sweep-extract-2026-05-10.md` (the plan that originally tripped the bug). In REPL, run `gates._parse_plan_header(open(...).read())`. Result MUST include `pause_for_verdict: after_step_1` (verifying the fix would have prevented the earlier-today incident). | `repl-fixture-output.txt` |

### QA report

Write to `bellows/knowledge/qa/header-parser-multiline-fix-qa-2026-05-10.md` with one row per verification matrix item. Status column uses one of: ✅, OK, PASS. End with summary line: `Fix verified — N/13 checks passed.`

### Rule 20 self-check

Run the canonical Rule 20 self-check from `/Users/marklehn/Desktop/GitHub/RULE_20_SELF_CHECK_BLOCK.md`. Use these values:

- `plan_slug`: `executable-header-parser-multiline-fix-2026-05-10`
- `qa_report_path`: `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/header-parser-multiline-fix-qa-2026-05-10.md`
- `evidence_dir`: `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/header-parser-multiline-fix-2026-05-10/`
- `required_evidence_files`: `["repl-fixture-output.txt", "test-suite-result.txt", "code-grep-results.txt"]`

Read `RULE_20_SELF_CHECK_BLOCK.md`, copy the Python block from its `## Canonical Python Block` section, fill in the four placeholders with the values above, run it, and include its literal stdout at the end of the QA report.

### Output Receipt

```
**Step:** 2
**Status:** Complete
**Deposits:**
- bellows/knowledge/qa/header-parser-multiline-fix-qa-2026-05-10.md (created)
- bellows/knowledge/qa/evidence/header-parser-multiline-fix-2026-05-10/ (directory with 3 evidence files)
**Verification:** N/13 checks passed
**Self-check:** PASSED (canonical block run from RULE_20_SELF_CHECK_BLOCK.md)
```

STOP after Step 2. Final-step verdict will be issued by the Planner after Rule 22 verification.

---

## Deliverables Summary

| Step | Agent | Deliverable | Location |
|------|-------|-------------|----------|
| 1 | DEV | `gates.py` (modified) | `bellows/` |
| 1 | DEV | `bellows.py` (modified) | `bellows/` |
| 1 | DEV | test files (modified — 7 new tests) | `bellows/tests/` |
| 1 | DEV | dev log (created) | `bellows/knowledge/development/` |
| 2 | QA | QA report + evidence directory (created) | `bellows/knowledge/qa/` |
