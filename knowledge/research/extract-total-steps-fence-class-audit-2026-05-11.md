# extract_total_steps Fenced-Code Class Audit — Findings

**Date:** 2026-05-11 | **Plan:** diagnostic-extract-total-steps-fence-class-audit-2026-05-11 | **Step:** 1

---

## Q0 — Has Any Fix Shipped Since 2026-05-10?

**No fix has shipped.** Five commits exist since 2026-05-09:

| SHA | Summary | Touches affected parsers? |
|---|---|---|
| 1c6c5b2 | fix(parser): multi-line bold header support | No |
| dc1acd4 | refactor: extract _perform_startup_sweep | No |
| db78919 | fix(verdicts): stale-verdict check for halted plans | No |
| 8eac4c3 | fix(teardown): stale index.lock + orphan worktree cleanup | No |
| be8cba4 | fix(gates): thread wt_path into _gate_rule_20_self_check | No |

None touch `extract_total_steps`, `_gate_is_qa_step`, `_extract_step_text`, or add any code-fence stripping logic. Proceeding.

---

## Q1 — Confirm Current Behavior of `extract_total_steps()`

**Source:** `bellows.py:98-103`

```python
def extract_total_steps(plan_text: str) -> int:
    case_insensitive_count = len(re.findall(r"^## STEP\s+\d+", plan_text, re.MULTILINE | re.IGNORECASE))
    case_sensitive_count = len(re.findall(r"^## STEP\s+\d+", plan_text, re.MULTILINE))
    if case_insensitive_count > 0 and case_sensitive_count == 0:
        print(f"Bellows: ⚠️  WARNING: plan has step headers but case does not match expected '## STEP N' — count={case_insensitive_count} matched case-insensitively")
    return case_insensitive_count
```

**REPL Fixture:**

```python
fence = chr(96)*3
fixture = f"""---
name: test-plan
---

## STEP 1 — Real Step One

Do something real. Here is a test fixture:

{fence}python
FIXTURE = \"\"\"
## STEP 1 — Example Fixture Step
Do example stuff.

## STEP 2 — Example Fixture Step
More example.
\"\"\"
{fence}

## STEP 2 — Real Step Two

Do something else.
"""
extract_total_steps(fixture)  # Returns: 4
```

**Result:** Returns **4** instead of 2. **BUG-CONFIRMED.** The `^` anchor with `re.MULTILINE` matches any line-start, including lines inside fenced code blocks. When `## STEP N` patterns appear at the start of a line within a fenced block (as happens in heredoc test fixtures embedded in plans), they are counted as real steps.

**Note:** If the in-fence patterns are NOT at line-start (e.g., `plan = "## STEP 1 — example"` on one line), the `^` anchor correctly excludes them. The bug only triggers when the pattern begins at column 0 inside the fence — which is exactly the case with embedded multi-line test fixtures or markdown examples.

---

## Q2 — Survey of `STEP N` Regex Use

| File | Line | Function | Regex Pattern | Purpose | Strips fences? | Classification |
|---|---|---|---|---|---|---|
| bellows.py | 99 | `extract_total_steps` | `r"^## STEP\s+\d+"` (MULTILINE\|IGNORECASE) | Count total plan steps | No | IN-SCOPE |
| bellows.py | 100 | `extract_total_steps` | `r"^## STEP\s+\d+"` (MULTILINE) | Case-sensitive sanity check | No | IN-SCOPE (same fn) |
| bellows.py | 251 | `run_plan` (comment) | N/A | Inline comment referencing the pattern | N/A | OUT-OF-SCOPE (comment) |
| bellows.py | 281 | `run_plan` (log) | N/A | Log/print string referencing the pattern | N/A | OUT-OF-SCOPE (display) |
| gates.py | 244 | `_extract_step_text` (docstring) | N/A | Docstring describing behavior | N/A | OUT-OF-SCOPE (docs) |
| gates.py | 249 | `_extract_step_text` | `rf"## STEP {step_number}\b.*?(?=\n## STEP \|\Z)"` (DOTALL) | Extract text of one step | No | IN-SCOPE |
| gates.py | 341 | `_gate_is_qa_step` | `rf"## STEP {step_number}\b[^\n]*"` | Detect if step is a QA step | No | IN-SCOPE |

Additionally, `verdict.py:29` contains a duplicate of `_extract_step_text`:

| File | Line | Function | Regex Pattern | Purpose | Strips fences? | Classification |
|---|---|---|---|---|---|---|
| verdict.py | 29 | `_extract_step_text_from_plan` | `rf"## STEP {step_number}\b.*?(?=\n## STEP \|\Z)"` (DOTALL) | Extract step text (dup of gates.py) | No | IN-SCOPE |

---

## Q3 — Probe Each IN-SCOPE Parser

### Parser 1: `extract_total_steps` (bellows.py:98-103)

See Q1 above. **BUG-CONFIRMED** — returns 4 instead of 2 when 2 real headers + 2 in-fence headers at line-start exist.

### Parser 2: `_extract_step_text` (gates.py:243-251)

```python
fence = chr(96)*3
fixture = f"""## STEP 1 — Real Step One

Some prose.

{fence}markdown
## STEP 2 — Bellows QA
Example.
{fence}

## STEP 2 — Developer

Real step 2.
"""
_extract_step_text(fixture, 2)
# Returns: '## STEP 2 — Bellows QA\nExample.\n```\n'
```

**BUG-CONFIRMED.** `re.search` (no `^` anchor) finds the FIRST `## STEP 2` occurrence, which is inside the fenced code block. The extracted "step text" contains fenced example content instead of the real Step 2 body. Downstream consumers (`_gate_scope_check`, `_gate_deposit_exists`, `_extract_plan_required_deposits`) all inherit this corruption.

### Parser 3: `_gate_is_qa_step` (gates.py:340-345)

```python
fence = chr(96)*3
fixture = f"""## STEP 1 — Real Step One

Some prose.

{fence}markdown
## STEP 2 — Bellows QA
Example.
{fence}

## STEP 2 — Developer

Real step 2.
"""
_gate_is_qa_step(fixture, 2)
# Returns: True  (should be False — real Step 2 is "Developer", not "QA")
```

**BUG-CONFIRMED.** `re.search` finds the in-fence `## STEP 2 — Bellows QA` first, causing the function to incorrectly classify a non-QA step as QA. This would cause Bellows to apply QA gates (Rule 20 self-check) to a non-QA step, or conversely skip QA gates on a real QA step if the fenced example showed a non-QA header.

### Parser 4: `_extract_step_text_from_plan` (verdict.py:23-31)

```python
fence = chr(96)*3
fixture = f"""## STEP 1 — Real

{fence}markdown
## STEP 2 — Bellows QA
Example.
{fence}

## STEP 2 — Developer

Real step 2.
"""
_extract_step_text_from_plan(fixture, 2)
# Returns: '## STEP 2 — Bellows QA\nExample.\n```\n'
```

**BUG-CONFIRMED.** Identical behavior to gates.py `_extract_step_text` (same regex, duplicated per the in-code comment). Affects verdict request deposit path extraction.

---

## Q4 — Audit for the Broader Pattern

### Regex calls across all four files

| File | Line | Function | Pattern target | Operates on | Classification |
|---|---|---|---|---|---|
| bellows.py:92 | `extract_step_number` | `\*\*Step:\*\*\s*(\d+)` | result_text | IRRELEVANT |
| bellows.py:99-100 | `extract_total_steps` | `^## STEP\s+\d+` | plan_text | Already in Q2 |
| bellows.py:759 | `_is_runnable_plan` | `^(parallel-\d+-)?(executable\|...)` | filename | IRRELEVANT |
| bellows.py:763 | `_extract_parallel_group` | `^(parallel-\d+)-` | filename | IRRELEVANT |
| bellows.py:934 | `_consume_verdicts` | `^verdict-(.+)-step-(\d+)` | filename | IRRELEVANT |
| bellows.py:1109 | `_consume_verdicts` | `^verdict-request-(.+)-step-\d+` | filename | IRRELEVANT |
| gates.py:34 | `_parse_plan_header` | `\A---\n(.*?)\n---\n` | plan_text | IRRELEVANT (`\A` anchored to string start) |
| gates.py:84 | `_parse_plan_header` | `\*\*([^:*]+):\*\*...` | single header_line | IRRELEVANT (single line) |
| gates.py:217 | `_extract_agent_declared_deposits` | `### Files Deposited\s*\n...` | result_text | IRRELEVANT |
| gates.py:250 | `_extract_step_text` | `## STEP {N}...` | plan_text | Already in Q2 |
| gates.py:263-285 | `_extract_plan_required_deposits` | various deposit patterns | step_text (downstream) | IRRELEVANT (operates on already-extracted step) |
| gates.py:342 | `_gate_is_qa_step` | `## STEP {N}...` | plan_text | Already in Q2 |
| parser.py:29 | `extract_ceo_flags` | `### Flags for CEO\s*\n...` | result_text | IRRELEVANT |
| parser.py:40 | `extract_verdict_request` | `^VERDICT_REQUESTED:...` | result_text | IRRELEVANT |
| verdict.py:30 | `_extract_step_text_from_plan` | `## STEP {N}...` | plan_text | Already in Q2 |
| verdict.py:157 | `parse_verdict` | `^(continue\|stop)$` | verdict content | IRRELEVANT |

**No additional RELEVANT parsers found** beyond those already covered in Q2/Q3. All other regex calls either operate on result_text (agent output), filenames, single lines, or verdict file content — none parse multi-line plan text for structural headers.

---

## Q5 — Population Scan of Recent Plans

**Script used:**

```python
import re
from pathlib import Path

fence_marker = chr(96) * 3
step_pattern = re.compile(r"^## STEP\s+\d+", re.MULTILINE | re.IGNORECASE)

total_with_fences = 0
total_with_infence_steps = 0
affected_plans = []

for done_dir in [
    Path("knowledge/decisions/Done"),
    Path("../invoice-pulse/knowledge/decisions/Done"),
]:
    if not done_dir.exists():
        continue
    for f in done_dir.iterdir():
        if not (f.is_file() and f.suffix == ".md"):
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        if fence_marker not in text:
            continue
        total_with_fences += 1
        lines = text.split('\n')
        in_fence = False
        in_fence_lines = []
        for line in lines:
            if line.strip().startswith(fence_marker):
                in_fence = not in_fence
                continue
            if in_fence:
                in_fence_lines.append(line)
        in_text = '\n'.join(in_fence_lines)
        in_fence_count = len(step_pattern.findall(in_text))
        if in_fence_count > 0:
            total_with_infence_steps += 1
            affected_plans.append((str(f), in_fence_count))
```

**Results:**

| Metric | Count |
|---|---|
| Total plans with fenced code blocks (both Done dirs) | 663 |
| Plans with in-fence `## STEP N` patterns | **2** |

**Affected plans:**

| Plan | In-fence STEP count |
|---|---|
| `knowledge/decisions/Done/executable-bellows-phase8-verdict-layer-redesign-2026-04-16.md` | 1 |
| `knowledge/decisions/Done/executable-header-parser-multiline-fix-2026-05-10.md` | 2 |

The second plan is the one that triggered the original observation (dispatched as 4 steps instead of 2). The first is an older plan that was not observed to fail at dispatch time — it has only 1 in-fence pattern, which may or may not have caused a miscount depending on whether it was an additional `## STEP N` not already present as a real header.

**Population-level risk:** Low frequency (2/663 = 0.3%), but the risk is structural — any plan that embeds example step headers in code fences (e.g., test fixtures, REPL demonstrations, documentation examples) will trigger the bug. The frequency will increase as plans increasingly contain inline code examples.

---

## Q6 — Recommended Fix Shape Per Affected Parser

### All 4 parsers: Shape (a) — Shared fence-stripping utility

**Recommendation:** Create a shared utility function `strip_fenced_code_blocks(text: str) -> str` and apply it to plan_text before passing to any structural parser.

**Concrete approach:** A regex-based strip is sufficient:

```python
def strip_fenced_code_blocks(text: str) -> str:
    """Remove fenced code blocks (``` ... ```) from text, preserving line structure."""
    return re.sub(r"^```[^\n]*\n.*?^```[^\n]*$", "", text, flags=re.MULTILINE | re.DOTALL)
```

This uses `^` anchoring with `re.MULTILINE` to match triple-backtick lines at line-start, which is the standard markdown convention. A character-by-character state machine would be more robust to edge cases (e.g., indented fences, tildes), but the regex approach handles all plans in the current population and is simpler.

**No existing fence-stripper exists in the codebase.** A `grep -i` for `fence|strip.*code|code.*block` across all `.py` files found no stripping utility. The only fence-aware code is in `test_rule_26_deposit_parser.py` (test-only, not a utility).

**Shared vs. per-parser:** Shared utility. Four parsers need the same treatment. Placing it in `bellows.py` (near `extract_total_steps`) or in a new `utils.py` keeps it DRY. The strip should be applied at the call site (before passing `plan_text` to the parser), not inside each parser, so that parsers remain pure text-matching functions.

**Note on the verdict.py duplicate:** `_extract_step_text_from_plan` in `verdict.py:23-31` is explicitly documented as a duplicate of `gates.py::_extract_step_text` ("keep in sync"). The fix must be applied to both. Consider whether this is an opportunity to deduplicate (shared import), but that is a scope expansion decision for the Planner.

**Cost estimate:**
- LOC: ~5 for the utility + 4 call-site changes (one per parser)
- Tests: 4 new regression tests (one per BUG-CONFIRMED parser) + 1 unit test for the strip utility
- Breaking changes: None. The strip only removes fenced blocks from the text passed to structural parsers; it does not modify the plan file or the text passed to agents.

---

## Q7 — Test Surface

### `extract_total_steps` (bellows.py:98-103)

| File | Function | Description |
|---|---|---|
| tests/test_bellows.py:1813 | `test_extract_total_steps_mixed_case` | Mixed-case `## Step N` headers counted |
| tests/test_bellows.py:1818 | `test_extract_total_steps_lowercase` | Lowercase `## step N` headers counted |
| tests/test_bellows.py:1823 | `test_extract_total_steps_uppercase_unchanged` | Standard uppercase headers counted |
| tests/test_bellows.py:1828 | `test_extract_total_steps_requires_number` | Rejects "## Step-by-step" (no digit) |
| tests/test_bellows.py:1833 | `test_extract_total_steps_case_mismatch_warning` | Warning printed on case mismatch |

**Gap:** No test exercises behavior with fenced code blocks containing `## STEP N`. Need a regression test with a fixture like Q1.

### `_extract_step_text` (gates.py:243-251)

| File | Function | Description |
|---|---|---|
| tests/test_rule_26_deposit_parser.py:156 | `test_extract_step_text_helper_gates_py` | Basic step extraction from multi-step plan |

**Gap:** No test with in-fence `## STEP N` patterns.

### `_gate_is_qa_step` (gates.py:340-345)

**No existing tests.** Zero coverage. Needs both baseline tests and fence-regression tests.

### `_extract_step_text_from_plan` (verdict.py:23-31)

**No existing tests.** Zero coverage (the gates.py duplicate has 1 test; this copy has none). Needs both baseline and fence-regression tests.

---

## Planner-Facing Summary

1. **No fix has shipped** (Q0) — all 5 commits since 2026-05-09 address unrelated issues.
2. **4 parsers BUG-CONFIRMED** (Q3): `extract_total_steps` (bellows.py:98), `_extract_step_text` (gates.py:249), `_gate_is_qa_step` (gates.py:341), `_extract_step_text_from_plan` (verdict.py:29).
3. **Recommended fix shape:** All 4 parsers want **shape (a)** — a shared `strip_fenced_code_blocks()` utility applied to `plan_text` before parsing. No parser warrants shape (b) or (c). Estimated cost: ~5 LOC utility + 4 call-site changes + 5 new tests.
4. **Population-level risk:** 2 out of 663 fenced-code-block plans (0.3%) contain in-fence `## STEP N` patterns that would trigger the bug today. Frequency is low but structural — any future plan embedding step-header examples in code fences will be affected.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Full population-level audit of the fenced-code-block blindness bug class across all structural parsers in bellows.py, gates.py, parser.py, and verdict.py. Confirmed 4 BUG-CONFIRMED parsers via REPL fixtures, scanned 663 plans for population-level risk, and produced fix-shape recommendations.

### Files Deposited
- `bellows/knowledge/research/extract-total-steps-fence-class-audit-2026-05-11.md` — diagnostic findings (Q0–Q7)

### Files Created or Modified (Code)
- None (diagnostic only)

### Decisions Made
- Classified all 4 affected parsers as shape (a) candidates (shared fence-stripping utility)
- Determined no existing fence-stripper exists in the codebase

### Flags for CEO
- None

### Flags for Next Step
- The verdict.py `_extract_step_text_from_plan` duplicate should be considered for deduplication during the fix, but that is a scope expansion decision
- `_gate_is_qa_step` has zero test coverage — the fix plan should include baseline tests, not just regression tests
