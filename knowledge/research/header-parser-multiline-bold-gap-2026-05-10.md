# Findings — Multi-Line Bold Header Parser Gap

**Date:** 2026-05-10 | **Author:** Bellows SA | **Diagnostic:** diagnostic-header-parser-multiline-bold-2026-05-10

---

## Q1. Empirical verification of the parser gap

### Parser function body (`gates.py` lines 22–71)

```python
def _parse_plan_header(plan_text):
    """Extract plan header fields. Tries YAML frontmatter first, then pipe-separated format.

    Supported formats:
    1. YAML frontmatter: file starts with ``---\\n...\\n---\\n``
    2. Pipe-separated bold-Markdown: ``**Key:** value | **Key:** value`` on the
       first non-empty line after a ``# Title`` line.
    Returns {} if neither format is found.
    """
    # Strategy 1: YAML frontmatter
    match = re.search(r"\A---\n(.*?)\n---\n", plan_text, re.DOTALL)
    if match:
        result = {}
        for line in match.group(1).splitlines():
            if ":" in line:
                key, _, value = line.partition(":")
                key = key.strip().strip("*")
                result[key] = value.strip().strip("*").strip()
        if result:
            return result

    # Strategy 2: Pipe-separated bold-Markdown header
    # Expects: line 1 = "# Title", line 2 = "**Key:** value | **Key:** value | ..."
    lines = plan_text.split("\n")
    header_line = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("# "):
            # Found the title line — look for the next non-empty line
            for j in range(i + 1, len(lines)):
                candidate = lines[j].strip()
                if candidate:
                    header_line = candidate
                    break
            break
        else:
            # File doesn't start with # — no pipe-format header
            break

    if not header_line or "**" not in header_line:
        return {}

    result = {}
    for m in re.finditer(r'\*\*([^:*]+):\*\*\s*([^|]*?)(?:\s*\||$)', header_line):
        key = m.group(1).strip().lower().replace(" ", "_")
        value = m.group(2).strip()
        result[key] = value
    return result
```

**Root cause confirmed:** Lines 53–56 — the inner `for j in range(...)` loop finds the first non-empty line after `# Title`, assigns it to `header_line`, then `break`s. Only that single line is parsed by the regex at line 67. All subsequent bold-Markdown lines are invisible.

### REPL output

**Multi-line bold fixture** (mirrors `executable-startup-sweep-extract-2026-05-10.md`):

```python
fixture = """# Executable — Extract _perform_startup_sweep from Bellows.start()

**Project:** bellows
**Date:** 2026-05-10
**Author:** Planner
**Tier:** Small
**Total Steps:** 2

**pause_for_verdict:** after_step_1

---

## Context
..."""

>>> gates._parse_plan_header(fixture)
{'project': 'bellows'}
```

**Single-line pipe fixture** (mirrors `executable-rule-20-single-source-2026-05-10.md`):

```python
fixture_pipe = """# Executable — Rule 20 Self-Check Block Single-Source File

**Project:** bellows | **Date:** 2026-05-10 | **Author:** Planner | **Tier:** Small-to-Medium | **Total Steps:** 2 | **pause_for_verdict:** after_step_1

---

## Context
..."""

>>> gates._parse_plan_header(fixture_pipe)
{'project': 'bellows', 'date': '2026-05-10', 'author': 'Planner', 'tier': 'Small-to-Medium', 'total_steps': '2', 'pause_for_verdict': 'after_step_1'}
```

### Verdict

**Hypothesis CONFIRMED.** Multi-line bold returns `{'project': 'bellows'}` (single key). Pipe format returns all 6 fields including `pause_for_verdict`. The parser gap is real.

---

## Q2. Auto-advance mechanism trace

### Call chain

1. **`bellows.py:247`** — `header = gates._parse_plan_header(metadata_text)` — initial parse in `run_plan()`.
2. **`bellows.py:248`** — `model = header.get("Model", header.get("model", config["default_model"]))` — uses parsed header for model selection.
3. **`bellows.py:268`** — `if total_steps > 1 and not header.get("pause_for_verdict", "").strip():` — emits the warning log `"has N steps but no pause_for_verdict header"`. This is the diagnostic message observed in the incident.
4. **`gates.py:111`** (inside `gates.check()`) — `header = _parse_plan_header(plan_text)` — re-parsed and returned in `gate_result["plan_header"]`.
5. **`bellows.py:342`** — `header = gate_result.get("plan_header", {})` — this is the header dict used for all pause decisions.
6. **`bellows.py:350`** — `header_says_pause(header, current_step, total_steps, gate_result["is_qa_step"])` — inside the while-loop guard. If this returns `False`, auto-advance proceeds.
7. **`bellows.py:433`** — same `header_says_pause()` call at the final-step check.

### `header_says_pause()` function (`bellows.py` lines 188–197)

```python
def header_says_pause(header: dict, current_step: int, total_steps: int, is_qa_step: bool) -> bool:
    """Return True if plan header's pause_for_verdict field matches current step."""
    pv = header.get("pause_for_verdict", "")
    if pv == "always":
        return True
    if pv == "after_step_1":
        return current_step == 1
    if pv == "after_qa_step":
        return is_qa_step
    return False
```

### Auto-advance vector confirmed

When `_parse_plan_header` returns `{'project': 'bellows'}` (multi-line bold case):
- `header.get("pause_for_verdict", "")` → `""` (empty string)
- `header_says_pause()` → `False` (none of the `if` branches match)
- The while-loop guard at line 345–350 does not pause
- Bellows auto-advances to Step 2 without waiting for verdict

**No fallback logic exists.** There is no secondary path that reads `pause_for_verdict` from the raw plan text. The parsed header dict is the sole source of truth.

**Additional miss:** `total_steps` is also invisible in the multi-line bold case. At `bellows.py:237`, `extract_total_steps()` counts `## STEP N` section headers (not the `**Total Steps:**` header field), so `total_steps` is correct regardless of the header parser. But `model` override (line 248), `tier`, `date`, and `author` metadata are all lost.

---

## Q3. Live plan population audit

### Count table (last 30 days, all watched projects)

| Header format | Count | Plans with `pause_for_verdict` declared | Plans where parser would miss `pause_for_verdict` |
|---|---|---|---|
| single-line pipe | ~710 | ~10 | 0 |
| multi-line bold | ~57 | 3 | 3 |
| other/none | ~46 | 0 | 0 |
| **Total** | **~813** | **~13** | **3** |

### Affected files (all in Done/ — already executed)

1. `bellows/knowledge/decisions/Done/diagnostic-rule-20-block-sourcing-2026-05-10.md` — `pause_for_verdict: always` on line 9 (missed)
2. `bellows/knowledge/decisions/Done/diagnostic-teardown-cherry-pick-audit-2026-05-10.md` — `pause_for_verdict: true` on line 6 (missed)
3. `bellows/knowledge/decisions/Done/executable-startup-sweep-extract-2026-05-10.md` — `pause_for_verdict: after_step_1` on line 9 (missed; this is the incident trigger)

### In-flight plans at risk

**None.** All currently in-flight plans (in `decisions/` — not Done/) use single-line pipe format. No current plan is at risk of silent auto-advance from this bug.

The vulnerability is latent: it will activate the next time the Planner emits a multi-line bold header with `pause_for_verdict` on a non-first line.

---

## Q4. Fix shape cost evaluation

### Comparison table

| Aspect | Shape (a): Extend Strategy 2 multi-line | Shape (b): New Strategy 3 | Shape (c): Governance-only mandate |
|---|---|---|---|
| Code LOC delta in `gates.py` | +8–12 lines (modify inner loop) | +15–20 lines (new block after Strategy 2) | 0 |
| Regression test count | 3–4 (multi-line, pipe, mixed, edge) | 4–5 (same + Strategy 3 isolation) | 0 code tests; 1 governance doc update |
| Risk to existing single-line pipe plans | None — pipe `\|` separator still parsed on single line | None — Strategy 2 runs first | None |
| Risk to existing YAML plans | None — Strategy 1 runs first | None — Strategy 1 runs first | None |
| Cost to migrate in-flight multi-line bold plans | 0 (parser now handles them) | 0 (parser now handles them) | Must rewrite all future plans; existing Done/ plans unchanged |
| Cross-cutting changes | None | None | PLANNER_TEMPLATE update, agent files update, Planner prompt update |
| Hidden-substitution failure risk | Low — single parser path | Medium — two bolt-on strategies could diverge | Low as governance, but fragile if Planner ignores constraint |

### Shape (a) feasibility sketch

Current Strategy 2 inner loop (`gates.py` lines 52–57):

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

Proposed edit — collect ALL consecutive bold-Markdown lines instead of just the first:

```python
if stripped.startswith("# "):
    # Collect all consecutive bold-Markdown header lines after title
    header_lines = []
    for j in range(i + 1, len(lines)):
        candidate = lines[j].strip()
        if not candidate:
            if header_lines:
                continue  # skip blank lines between header fields
            continue  # skip blank lines before first header field
        if candidate.startswith("**") or candidate.startswith("---"):
            if candidate.startswith("---"):
                break  # hit the horizontal rule — stop
            header_lines.append(candidate)
        else:
            break  # non-bold, non-blank line — stop
    header_line = " | ".join(header_lines)
    break
```

This joins multi-line bold fields into a synthetic pipe-separated line, so the existing regex at line 67 parses them unchanged. **~10 LOC delta — confirms the BACKLOG estimate.**

The regex `r'\*\*([^:*]+):\*\*\s*([^|]*?)(?:\s*\||$)'` already handles `|` as a delimiter, so the join-with-pipe approach requires zero regex changes.

### Risk assessment for Shape (a)

- **Correctness:** Handles multi-line bold, single-line pipe, and mixed formats uniformly.
- **Regression surface:** The only behavioral change is that Strategy 2 now reads multiple lines. Existing single-line pipe plans produce a single-element `header_lines` list, which joins to the same string — behavior unchanged.
- **Edge case:** A plan with `**bold text**` in the Context section won't be reached because the `---` horizontal rule terminates collection.

---

## Q5. Hidden alternatives

### (d) Single-source canonical plan-header template

A `PLAN_HEADER_TEMPLATE.md` file at the governance root that the Planner imports. Plans reference it; the Planner cannot author non-conforming headers by construction.

- **Cost:** Medium — requires Planner template changes, governance doc, and enforcement mechanism.
- **Risk:** Low code risk, but adds a dependency on the Planner's template rendering path.
- **Effectiveness:** High for prevention, but does not fix the parser — a manually-authored multi-line bold plan would still fail silently.
- **Verdict:** Complementary to (a) or (b), not a standalone fix.

### (e) Bellows-side validation warning for missing expected keys

Emit a warning when `_parse_plan_header` returns a dict missing expected keys (e.g., `total_steps > 1` and no `pause_for_verdict`).

- **Cost:** Low — 3–5 LOC in `bellows.py` around line 268 (the existing warning is already there, line 268–269).
- **Risk:** None — warning-only, does not change execution behavior.
- **Effectiveness:** Defensive layer — catches parser misses at runtime. Already partially implemented at line 268 (`"has N steps but no pause_for_verdict header"` warning). Could be promoted to a gate failure instead of a warning.
- **Verdict:** Strong complement to any code fix. **Recommend promoting the line 268 warning to a blocking gate or at minimum extending it to also warn when `total_steps`, `date`, `author` are missing from a multi-step plan.**

### (f) Parsed-header summary at dispatch time

Emit a one-line summary showing all parsed header fields so the CEO can spot a parser miss immediately.

- **Cost:** Low — 1–2 LOC, `print(f"Bellows: parsed header: {header}")`.
- **Risk:** None — informational only.
- **Effectiveness:** Moderate — helps manual detection but does not prevent auto-advance.
- **Verdict:** Low-cost observability improvement. Useful regardless of which fix shape is chosen.

### (g) Identified additional alternative: Defensive default for `pause_for_verdict`

If `_parse_plan_header` returns a dict with fewer than N expected keys for a multi-step plan, default `pause_for_verdict` to `"after_step_1"` rather than empty string. This is a safety net — if the parser misses fields, Bellows defaults to pausing rather than auto-advancing.

- **Cost:** Low — 3–4 LOC in `run_plan()` after header parse.
- **Risk:** Low — only fires when parser output is suspiciously sparse.
- **Effectiveness:** High as a safety net — converts a silent failure into a safe pause.
- **Verdict:** Strong defensive alternative. Could be implemented alongside Shape (a) as a belt-and-suspenders measure. Example:

```python
if total_steps > 1 and len(header) < 3:
    header.setdefault("pause_for_verdict", "after_step_1")
    print(f"Bellows: ⚠️  sparse header ({len(header)} keys) for multi-step plan — defaulting pause_for_verdict to after_step_1")
```

---

## Recommendation Summary

| Fix shape | Standalone viable? | Recommended? |
|---|---|---|
| **(a)** Extend Strategy 2 | Yes | **Yes — primary fix** |
| **(b)** New Strategy 3 | Yes | No — unnecessary complexity over (a) |
| **(c)** Governance mandate | Partially | As complement only |
| **(d)** Template single-source | Partially | As complement only |
| **(e)** Missing-key validation | No | **Yes — complement to (a)** |
| **(f)** Dispatch-time summary | No | Yes — low-cost observability |
| **(g)** Defensive default | Partially | **Yes — strong safety net complement to (a)** |

**Recommended combination:** Shape (a) + (e) + (g). Fix the parser, warn on sparse headers, and default to safe-pause when the parser output looks incomplete. Total LOC: ~20 in `gates.py` + ~5 in `bellows.py`.
