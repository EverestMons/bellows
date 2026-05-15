# no_permission_denials Gate Taxonomy — Diagnostic Findings

**Date:** 2026-04-28
**Agent:** Bellows Systems Analyst
**Plan:** diagnostic-no-permission-denials-taxonomy-2026-04-28
**Step:** 1

---

## 1. Executive Summary

The Planner's Option (b) hypothesis is **confirmed by the evidence**. Every observed `no_permission_denials` gate failure in production was caused by a read-class tool (Grep or Glob) hitting cross-project paths — zero write-class denials have been observed. The gate at `gates.py:101-108` makes no distinction between tool types; any non-empty `permission_denials` list trips it. The proposed `READ_CLASS_TOOLS` set is `{Grep, Glob, Read}` — these three tools have bash equivalents that agents routinely use as fallbacks, so their denials do not block execution. Write-class tools (`Edit, Write, Bash, NotebookEdit`) have no equivalent fallback and their denials represent genuine execution blockers. Test coverage is minimal (one test, string-form only) and will need 6-8 new cases if Option (b) ships.

---

## 2. Q1 — Gate Implementation

### Quoted function (`gates.py:101-108`)

```python
def _gate_no_permission_denials(parsed, failures):
    denials = parsed.get("permission_denials", [])
    if denials:
        first = denials[0] if isinstance(denials[0], str) else str(denials[0])
        failures.append({
            "gate": "no_permission_denials",
            "evidence": f"{len(denials)} denial(s): {first}",
        })
```

### Analysis

**(a) Shape of `parsed["permission_denials"]`:** The code handles **both** list-of-strings and list-of-dicts. Line 104's `isinstance(denials[0], str)` branch handles the string case; the `else str(denials[0])` branch stringifies dicts. In production, Claude Code emits **dicts** (see Q3 samples). The test suite uses **strings** (see Q5). Both shapes are tolerated but only one is tested.

**(b) Fields reliably present on each denial dict:** From observed production denials, each dict contains:
- `tool_name` (str) — always present in observed samples (e.g., `'Grep'`, `'Glob'`)
- `tool_use_id` (str) — always present (e.g., `'toolu_01T2AqANiyKMBVa48WtEDNQ3'`)
- `tool_input` (dict) — always present, contains the tool's parameter dict

**No observed case has a denial dict missing `tool_name`.** However, Claude Code's schema is not formally documented, so the field cannot be guaranteed.

**(c) Blocking vs. non-blocking distinction:** **None.** The gate treats any non-empty list as a failure — line 103's `if denials:` is the only check. No tool-name filtering, no severity classification, no correlation with deposit existence or receipt status.

---

## 3. Q2 — Denial Source

### Where `permission_denials` is populated

**`parser.py:12`:**
```python
permission_denials = raw.get("permission_denials", [])
```

**`parser.py:52`:**
```python
"permission_denials": permission_denials,
```

**(a) Stream:** Bellows reads `permission_denials` from Claude Code's JSON result output. The `raw` dict is the parsed `result` event from `claude -p`'s NDJSON stream (confirmed by `knowledge/research/stream-json-feasibility-2026-04-23.md:80` — "`permission_denials` — same key"). Bellows does **not** construct denial entries itself; it passes through whatever Claude Code reports.

**(b) What triggers a denial entry:** Claude Code adds a denial entry when the **user's permission settings** deny a tool call. This happens when an agent invokes a tool (e.g., `Grep`) against a path outside the project's allowed scope. The denial is a Claude Code platform-level event, not a Bellows event.

**(c) Whether `tool_name` is always populated:** In all observed production denials, `tool_name` is present. However:
- The gate code never inspects `tool_name` — it only checks list non-emptiness
- The `isinstance(denials[0], str)` branch suggests Bellows anticipated a legacy string-form (e.g., `"Write denied for /etc/passwd"` as used in the test fixture)
- If Claude Code ever changes its denial format, `tool_name` could be absent or renamed

**Conclusion:** `tool_name` is reliably present in current Claude Code output but not formally guaranteed. Any taxonomy fix should handle the missing-`tool_name` case defensively.

---

## 4. Q3 — Observed Denials Sample

### Raw evidence from verdict files

| Source File | Tool | Count | Target Path |
|---|---|---|---|
| `verdict-request-verdict-only-resume-docs-2026-04-28-step-1.md:16` | Grep | 3 | `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` |
| `verdict-request-planner-template-lessons-step-numbering-2026-04-23-step-1.md:16` | Grep | 3 | `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` |
| `processed-verdict-disable-auto-close-2026-04-24-step-1.md:2` | Grep | (unspecified) | cross-project PLANNER_TEMPLATE.md |
| `processed-verdict-disable-auto-close-2026-04-24-step-3.md:2` | Grep | (unspecified) | cross-project PLANNER_TEMPLATE.md |
| `processed-verdict-lessons-forge-phase1-schema-ingest-2026-04-23-step-1.md:5` | Glob | 1 | `/Users/marklehn/Desktop/GitHub` (cross-project root) |
| `processed-verdict-scope-check-monorepo-fix-2026-04-28-step-2.md:5` | Grep | (unspecified) | `/Users/marklehn/Desktop/GitHub` for pattern `rule.?20\|self.check` |
| BACKLOG #2 (2026-04-23 initial report) | Grep | 4 | `/Users/marklehn/Desktop/GitHub/anvil` |
| BACKLOG #2 (2026-04-23 additional reproduction) | Grep | 5 | `/Users/marklehn/Desktop/GitHub/governance/adr/ADR-002*.md` |
| BACKLOG #2 (2026-04-23 additional reproduction) | Glob | 1 | `/Users/marklehn/Desktop/GitHub` |
| verdict-log.md lines 7, 9 | Grep | (unspecified) | cross-project (logged as gate failure) |

### Frequency table

| tool_name | Observed Instances | Notes |
|---|---|---|
| **Grep** | 8+ distinct incidents | Dominant. All against cross-project paths. |
| **Glob** | 2 distinct incidents | Cross-project root path. |
| **Read** | 0 | Not observed in any denial record. |
| **Edit** | 0 | Not observed. |
| **Write** | 0 | Not observed. |
| **Bash** | 0 | Not observed. |
| **NotebookEdit** | 0 | Not observed. |
| **WebFetch** | 0 | Not observed. |
| **WebSearch** | 0 | Not observed. |
| MCP tools | 0 | Not observed. |

**100% of observed denials are on Grep or Glob.** Zero write-class tool denials have been recorded. This strongly confirms the Planner's hypothesis that the noise is concentrated in read-class tools.

---

## 5. Q4 — Read-vs-Write Taxonomy

### Classification criterion

A tool is **read-class** if its denial does NOT prevent the agent from completing the task — the agent can route around it via bash or alternate tools. A tool is **write-class** if its denial blocks the actual deliverable work and has no equivalent fallback.

### Proposed `READ_CLASS_TOOLS` set

```python
READ_CLASS_TOOLS = {"Grep", "Glob", "Read"}
```

### Per-tool classification

| Tool | Class | Reasoning | Confidence |
|---|---|---|---|
| **Grep** | READ | Agent fallback: `bash grep/rg`. Confirmed by 8+ production incidents where agents completed work despite Grep denials. | **High** — empirically validated |
| **Glob** | READ | Agent fallback: `bash find/ls`. Confirmed by 2 production incidents. | **High** — empirically validated |
| **Read** | READ | Agent fallback: `bash cat/head/tail`. Same class as Grep/Glob — information retrieval only. Not yet observed in denials but the routing-around pattern applies identically. | **High** — by analogy to observed Grep/Glob pattern |
| **Edit** | WRITE | No equivalent fallback. Agents cannot modify files without Edit, Write, or Bash. Denial blocks deliverables. | **High** |
| **Write** | WRITE | Same as Edit — file creation is blocked. | **High** |
| **Bash** | WRITE | Critical: Bash is both the fallback FOR read-class denials and a write-class tool in its own right. A Bash denial has no workaround — the agent is fully blocked. | **High** |
| **NotebookEdit** | WRITE | Notebook modification has no fallback. | **High** |
| **WebFetch** | **AMBIGUOUS** | Read-only, but may be the only path to a specific URL. If the agent needs to fetch a URL and WebFetch is denied, there may be no alternative (Bash `curl` would also need permission). However, WebFetch has never been observed in a denial. | **Medium** — classify as write-class for safety (default-deny) |
| **WebSearch** | **AMBIGUOUS** | Same reasoning as WebFetch. Read-only but potentially irreplaceable for the specific task. Never observed in a denial. | **Medium** — classify as write-class for safety |

### Recommendation

The `READ_CLASS_TOOLS = {"Grep", "Glob", "Read"}` set is safe and covers all observed false-positive denials. The ambiguous tools (WebFetch, WebSearch) should default to write-class (i.e., NOT in the exempt set) until empirical evidence shows they produce false positives. This is conservative — it may allow some future noise from WebFetch/WebSearch denials, but those tools have never triggered a denial in production and the noise risk is near-zero.

---

## 6. Q5 — Test Coverage and Edge Cases

### Current tests for `_gate_no_permission_denials`

**`tests/test_gates.py:73-78`** — single test:
```python
def test_permission_denials_nonempty():
    parsed = _clean_parsed()
    parsed["permission_denials"] = ["Write denied for /etc/passwd"]
    result = gates.check(parsed, PLAN_TEXT, 1, "/tmp")
    assert result["passed"] is False
    assert any(f["gate"] == "no_permission_denials" and "1 denial" in f["evidence"] for f in result["failures"])
```

**Scenarios tested:**
- String-form denial list (1 element) trips gate — **tested**
- Empty denial list passes — **implicitly tested** (via `test_all_gates_pass_on_clean_parsed` at line 32)

**Scenarios NOT tested:**
- Dict-form denial (the format actually emitted by Claude Code in production)
- Multiple denials (count display)
- Mixed string and dict denials

### Edge cases needed if Option (b) ships

| # | Case | Expected Behavior | Why |
|---|---|---|---|
| 1 | Empty `permission_denials` list | Gate passes | Baseline — already implicitly covered |
| 2 | All read-class denials (e.g., `[{"tool_name": "Grep", ...}]`) | Gate passes (new behavior) | Core Option (b) test |
| 3 | All write-class denials (e.g., `[{"tool_name": "Edit", ...}]`) | Gate fails | Verify write-class still blocked |
| 4 | Mixed read+write denials | Gate fails | One write-class denial is sufficient |
| 5 | Denial dict missing `tool_name` key | Gate fails (default to write-class) | Defensive — unknown denial should block |
| 6 | Denial dict with `tool_name: None` | Gate fails | Same defensive logic |
| 7 | String-form denial (legacy, no `tool_name`) | Gate fails | Legacy strings have no tool info — cannot classify, so default to blocking |
| 8 | Unknown tool name (e.g., `"SomeNewTool"`) | Gate fails | Allowlist, not denylist — only explicitly read-class tools are exempt |

### Malformed `permission_denials` handling today

- **Missing field:** `parsed.get("permission_denials", [])` defaults to `[]` — **handled gracefully**
- **Empty list:** `if denials:` is falsy — **handled gracefully**
- **String instead of list:** `if denials:` would be truthy for non-empty string, `denials[0]` would return the first character, and the evidence would be `"1 denial(s): W"` (for `"Write denied..."`) — **NOT handled gracefully** (silent corruption, not a crash)
- **None:** `if denials:` is falsy for None — **handled gracefully** (but silently — a `None` value might indicate a bug upstream)
- **List containing None:** `denials[0]` is `None`, `isinstance(None, str)` is False, `str(None)` is `"None"` — **handled** (evidence would be `"1 denial(s): None"`)

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Investigated the `_gate_no_permission_denials` gate implementation, traced the denial data source, sampled all observed denials from verdict files and BACKLOG, proposed a read-vs-write tool taxonomy, and audited test coverage and edge cases. The Planner's Option (b) hypothesis (scope gate to write-class tools) is confirmed by empirical evidence.

### Files Deposited
- `bellows/knowledge/research/no-permission-denials-taxonomy-2026-04-28.md` — diagnostic findings with gate analysis, denial frequency table, proposed taxonomy, and test coverage audit

### Files Created or Modified (Code)
- None (investigation only)

### Decisions Made
- Proposed `READ_CLASS_TOOLS = {"Grep", "Glob", "Read"}` based on observed denial patterns and confirmed bash-fallback routing
- Classified WebFetch and WebSearch as ambiguous/write-class (conservative default)
- Identified 8 test cases needed for Option (b) implementation

### Flags for CEO
- None

### Flags for Next Step
- None (single-step diagnostic, terminal step)
