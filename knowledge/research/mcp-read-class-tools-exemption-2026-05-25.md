# MCP READ_CLASS_TOOLS Exemption — Diagnostic Findings

**Date:** 2026-05-25 | **Agent:** Bellows Systems Analyst | **Diagnostic:** mcp-read-class-tools-exemption-2026-05-25 | **Step:** 1

---

## 1. Current State

### Q1 — READ_CLASS_TOOLS literal value

`gates.py` line 35:

```python
READ_CLASS_TOOLS = {"Grep", "Glob", "Read", "mcp__vexp__run_pipeline"}
```

`mcp__vexp__run_pipeline` **is present** — validating the 2026-05-12 close claim (`executable-intermediate-decision-detector-2026-05-12.md` Step 2 shipped this addition). The 2026-05-12 dev log confirms: "Extended `READ_CLASS_TOOLS` from `{"Grep", "Glob", "Read"}` to `{"Grep", "Glob", "Read", "mcp__vexp__run_pipeline"}`" (`knowledge/development/intermediate-decision-detector-dev-log-2026-05-12.md` line 85).

`mcp__vexp__get_context_capsule` is **absent** — this is the active gap producing the post-2026-05-12 gate failures.

### Q2 — Filter mechanism in `_gate_no_permission_denials`

`gates.py` lines 221-244:

```python
def _gate_no_permission_denials(parsed, failures):
    denials = parsed.get("permission_denials", [])
    blocking = []
    for d in denials:
        if isinstance(d, dict):
            tool_name = d.get("tool_name")
            if tool_name in READ_CLASS_TOOLS:
                continue
            # Exempt Bash denials matching the GUARDRAILS-prescribed git lock cleanup.
            # Command text is in tool_input.command per Claude Code's denial payload schema.
            if tool_name == "Bash":
                cmd = d.get("tool_input", {}).get("command", "") if isinstance(d.get("tool_input"), dict) else ""
                if GUARDRAILS_BASH_EXEMPTION_PATTERN.search(cmd):
                    continue
            blocking.append(d)
        else:
            # String-form denial (legacy) has no tool_name — default to blocking
            blocking.append(d)
    if blocking:
        first = blocking[0] if isinstance(blocking[0], str) else str(blocking[0])
        failures.append({
            "gate": "no_permission_denials",
            "evidence": f"{len(blocking)} blocking denial(s): {first}",
        })
```

**Matching mechanism:** `tool_name in READ_CLASS_TOOLS` — **exact string equality** via Python set membership. No prefix matching, no pattern matching. A tool name must appear as a literal member of the set to be exempted.

---

## 2. MCP Tool Corpus — Q3 Enumeration

Source: `knowledge/research/permission-denial-history-audit-2026-05-22.md` (authoritative 30-day audit, 2026-04-23 to 2026-05-22), cross-referenced with verdict files in `verdicts/resolved/` and `verdicts/pending/archived/`.

| # | Tool Name | Denial Count (log-level) | Gate Failures | Dates of Occurrence |
|---|---|---|---|---|
| 1 | `mcp__vexp__run_pipeline` | 1 | 1 | 2026-05-12 |
| 2 | `mcp__vexp__get_context_capsule` | 2 | 2 | 2026-05-20, 2026-05-21 |

**Total MCP tool denial events:** 3 (log-level), 3 (gate-level).

**Evidence for event #1:** Gate inventory event #8 in the audit; verdict at `verdicts/resolved/processed-verdict-intermediate-decision-detection-design-2026-05-12-step-1.md`. This denial occurred **before** the 2026-05-12 fix shipped `mcp__vexp__run_pipeline` into READ_CLASS_TOOLS. Post-fix, any subsequent `run_pipeline` denials would be filtered.

**Evidence for event #2a (2026-05-20):** Gate inventory event #9 in the audit; verdict at `verdicts/resolved/processed-verdict-defer-validation-bulk-ingest-2026-05-20-step-1.md`.

**Evidence for event #2b (2026-05-21):** Noted as "additional" in the audit (line 51); verdict at `verdicts/pending/archived/verdict-request-fuel-continuation-inference-v2-2026-05-21-step-1.md` and `verdicts/resolved/_PLANNER_RECALLED_processed-verdict-fuel-continuation-inference-v2-2026-05-21-step-1.md`.

**No other `mcp__*` tool names appear in the 30-day denial corpus.** The audit scanned 613 step log files and 15 verdict files mentioning `no_permission_denials`. WebSearch and WebFetch denials also appeared (2 events on 2026-05-22) but these are not MCP tools — they are native Claude Code tools denied because they were not in the `--allowedTools` list (separate BACKLOG entry).

---

## 3. Classification — Q4

All 7 `mcp__vexp__*` tools are enumerated below. Classifications are based on tool schema descriptions fetched via ToolSearch (authoritative — actual MCP tool definitions from the running vexp server).

| Tool Name | Classification | Basis |
|---|---|---|
| `mcp__vexp__run_pipeline` | **Read-class** | Runs code analysis pipeline (context search + impact analysis + memory recall). Returns information only. Description: "PRIMARY TOOL... runs a full analysis pipeline server-side and returns a single compressed result." No state modification. |
| `mcp__vexp__get_context_capsule` | **Read-class** | Lightweight context search via semantic + graph search. Description: "finds relevant code via semantic + graph search." Returns information only. No state modification. |
| `mcp__vexp__get_session_context` | **Read-class** | Retrieves observations from current/previous sessions. Description: "Get observations from the current and optionally previous sessions." Read-only memory recall. |
| `mcp__vexp__get_skeleton` | **Read-class** | Returns token-efficient file skeletons. Description: "Get a token-efficient skeleton of one or more files." Read-only. |
| `mcp__vexp__index_status` | **Read-class** | Returns index status, node/edge counts, daemon uptime. Description: "Get the current status of the vexp index." Read-only. |
| `mcp__vexp__search_memory` | **Read-class** | Searches session memories by keywords and semantic similarity. Description: "Search across all session memories." Read-only. |
| `mcp__vexp__save_observation` | **Write-class** | Saves an observation to session memory. Description: "Manually save an insight, decision, or important observation to session memory." **Modifies state** — writes to the vexp session store. Denials of this tool carry real signal (an agent attempting to persist state it shouldn't). |

**Summary:** 6 of 7 vexp tools are read-class. 1 (`save_observation`) is write-class. The write-class tool is identifiable by its `save_` prefix and its schema description ("Manually save...").

---

## 4. Resolution Shapes — Q5

### Shape A — Literal Set Extension

Extend READ_CLASS_TOOLS with each read-class MCP tool enumerated by exact name:

```python
READ_CLASS_TOOLS = {
    "Grep", "Glob", "Read",
    "mcp__vexp__run_pipeline",
    "mcp__vexp__get_context_capsule",
    "mcp__vexp__get_session_context",
    "mcp__vexp__get_skeleton",
    "mcp__vexp__index_status",
    "mcp__vexp__search_memory",
}
```

| Criterion | Assessment |
|---|---|
| **LOC (production)** | 1 — extend the set literal with 5 new entries (1 already present) |
| **LOC (test)** | ~5 — one regression test per newly-added tool name (pattern: existing `test_permission_denials_vexp_run_pipeline_exempt` at `tests/test_gates.py:874`) |
| **Risk of over-exemption** | **Zero** — each tool is individually vetted against its schema. `save_observation` is explicitly excluded. |
| **Risk of under-exemption** | **Moderate** — if a new `mcp__vexp__*` read-class tool is added in the future, it must be manually added to READ_CLASS_TOOLS. Failure to do so produces a gate failure (detectable, not silent). |
| **Maintenance cost** | Low — vexp tool set is small and stable. New tools require a 1-line addition + 1 test. The existing `test_permission_denials_vexp_run_pipeline_exempt` pattern is already established. |

### Shape B — Pattern-Match Generalization

Replace exact set membership with pattern-based matching (e.g., prefix `mcp__vexp__get_*`, `mcp__vexp__search_*`, `mcp__vexp__index_*`, `mcp__vexp__run_pipeline`).

| Criterion | Assessment |
|---|---|
| **LOC (production)** | ~5-10 — modify `_gate_no_permission_denials` to add regex/prefix matching alongside set membership |
| **LOC (test)** | ~10-15 — tests for each pattern, plus negative tests for `save_observation` |
| **Risk of over-exemption** | **HIGH** — the critical risk. A naive `mcp__vexp__*` prefix pattern would match `mcp__vexp__save_observation`, which is write-class. More refined patterns like `mcp__vexp__get_*` still risk matching future write-class tools with `get_`-prefixed names (e.g., a hypothetical `get_and_clear_cache`). The naming convention is **not a reliable proxy for read/write classification** — `run_pipeline` is read-class despite the `run_` prefix, which in other contexts implies mutation. |
| **Risk of under-exemption** | **Low** — broad patterns cover most cases automatically |
| **Maintenance cost** | Near-zero for new tools, but pattern review required when tool naming conventions evolve |

### Shape C (Emergent) — Config-Driven Allowlist

A third shape observed in the codebase: read the exemption list from a governance-root config file (paralleling `INTERMEDIATE_DECISION_PHRASES.md` for phrase detection). Would separate exemption data from code.

**Assessment:** Over-engineered for the current corpus size (7 tools, 6 read-class). Adds indirection without meaningful benefit. The governance-root file pattern makes sense for the 33-phrase intermediate-decision list, but not for a 6-entry static set that changes rarely. Dismissed.

### Recommendation

**Shape A (literal set extension).** Reasoning:

1. **Safety.** The write-class tool (`save_observation`) is excluded with certainty. Pattern matching introduces over-exemption risk that cannot be fully eliminated without a tool-schema introspection mechanism that doesn't exist in the filter path.
2. **Precedent.** The existing READ_CLASS_TOOLS architecture uses a literal set. Shape A is a 1-LOC extension of the existing pattern, not a mechanism change. The 2026-04-28 fix and 2026-05-12 extension both used literal additions.
3. **Corpus size.** 7 total vexp tools is small enough that enumeration is trivially maintainable. Pattern matching is justified when the corpus is large or frequently changing — neither is true here.
4. **Under-exemption is detectable.** If a new read-class MCP tool appears and isn't on the list, the gate fires, producing a verdict request. This is the same detection mechanism that surfaced the current gap. The maintenance cost is one line of code when it happens.

---

## 5. Population Sanity Check — Q6

**BACKLOG hypothesis:** "5 log-level denial events and 2 gate-level failures over 30 days."

**Actual counts from audit scan:**

| Metric | BACKLOG Claim | Audit Finding | Match? |
|---|---|---|---|
| MCP tool log-level denial events | 5 | 3 enumerated (1 `run_pipeline` + 2 `get_context_capsule`) | Partial — see below |
| MCP tool gate-level failures | 2 | 3 (events #8, #9 in gate inventory + fuel-continuation-inference-v2 additional) | Close but not exact |

**Discrepancy analysis:**

*Log-level (5 claimed vs. 3 enumerated):* The audit's bucket (d) enumerates 3 MCP events explicitly. The BACKLOG entry's count of 5 likely includes repeated denial attempts within a single step execution (e.g., the agent tried `mcp__vexp__get_context_capsule` multiple times in one step before falling back). The audit counted unique incidents per step log file, not individual denial entries within a step's `permission_denials` array. The 2026-05-21 verdict file (`verdict-request-fuel-continuation-inference-v2-2026-05-21-step-1.md`) shows the denial payload with a specific `tool_use_id`, consistent with a single attempt — but the same step may have contained additional attempts not surfaced in the verdict.

*Gate-level (2 claimed vs. 3 observed):* The audit explicitly counts events #8 (`run_pipeline`, 2026-05-12) and #9 (`get_context_capsule`, 2026-05-20) in its 10-event gate inventory. The `fuel-continuation-inference-v2-2026-05-21` event is noted as "additional" (line 51 of the audit), outside the 10-count, because the auditor treated it as a duplicate of event #9's pattern. If counted independently, the true MCP gate-failure count is 3.

**Hypothesis on partial filter effectiveness:** The discrepancy does NOT indicate partial filter effectiveness. The filter works as designed — it is exact string equality on READ_CLASS_TOOLS. `mcp__vexp__run_pipeline` is in the set (added 2026-05-12) and would be filtered for any post-fix denial. `mcp__vexp__get_context_capsule` is NOT in the set and correctly fires the gate every time. The "partial" appearance in the BACKLOG is because one tool was fixed (run_pipeline) while the other was not (get_context_capsule).

---

## 6. Recommendation

**Shape A — literal set extension.** Add the 5 remaining read-class `mcp__vexp__*` tools to READ_CLASS_TOOLS as exact-name literals, keeping `mcp__vexp__save_observation` excluded (write-class). Estimated effort: ~1 LOC production change + ~5 LOC tests (one regression test per new tool, following the pattern at `tests/test_gates.py:874`). Also add one negative test confirming `mcp__vexp__save_observation` IS NOT exempted. Total LOC: ~8 production+test. Risk profile: zero over-exemption risk, low maintenance cost, detectable under-exemption. This follows the established architectural precedent of the 2026-04-28 and 2026-05-12 READ_CLASS_TOOLS additions.

---

## Output Receipt

**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Characterized the current state of MCP tool exemption in `gates.py`, enumerated all `mcp__*` denials in the 30-day corpus, classified all 7 vexp tools as read-class or write-class using authoritative MCP tool schemas, compared two resolution shapes (literal-list vs. pattern-match) plus one emergent shape (config-driven), and validated the BACKLOG population hypothesis against audit data.

### Files Deposited
- `knowledge/research/mcp-read-class-tools-exemption-2026-05-25.md` — diagnostic findings (this file)

### Files Created or Modified (Code)
- None — read-only investigation

### Decisions Made
- Classified 6/7 vexp tools as read-class, 1/7 as write-class, based on MCP tool schema descriptions (not naming convention inference)
- Recommended Shape A (literal set extension) over Shape B (pattern match) due to zero over-exemption risk and small corpus size
- Dismissed Shape C (config-driven allowlist) as over-engineered for 6-entry static set

### Flags for CEO
- None

### Flags for Next Step
- `mcp__vexp__save_observation` is the only write-class vexp tool. The executable MUST include a negative test asserting it IS NOT exempted.
- The existing `test_permission_denials_vexp_run_pipeline_exempt` test at `tests/test_gates.py:874` is the pattern template for the new tests.
- Post-ship: daemon restart required for the new exemptions to take effect.
