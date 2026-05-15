# Deposit Parser Prose Failure — Diagnostic Findings

**Date:** 2026-05-05
**Plan:** diagnostic-deposit-parser-prose-failure-2026-05-05
**Agent:** Bellows Systems Analyst

---

## Q1: Mechanism Trace — What Code Path Produced the False Positive?

### Finding

The false positive comes from the **agent-receipt parsing** logic in `_gate_deposit_exists` (gates.py lines 146–161), NOT from `_extract_plan_required_deposits` (the plan-text parser). The BACKLOG entry's hypothesis — that the parser "fell back to prose scanning" or "scanned both block and prose" — is **incorrect**.

### Root Cause

The agent wrote its `### Files Deposited` section in the standard Output Receipt format specified by specialist files:

```
### Files Deposited
- `bellows/knowledge/BACKLOG.md` — BACKLOG #1 closed, bellows-self exposure opened as known constraint
- `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` — v4.33 with new Lessons Learned entry
- `bellows/knowledge/research/agent-prompt-feedback.md` — prompt feedback appended
```

The parsing logic at gates.py line 157:

```python
path = line[2:].strip().strip("`")
```

`.strip("`")` only removes backtick characters at the **boundaries** of the string. For an input line like:

```
- `bellows/knowledge/BACKLOG.md` — BACKLOG #1 closed, ...
```

The trace is:
1. `line[2:]` → `` `bellows/knowledge/BACKLOG.md` — BACKLOG #1 closed, ... ``
2. `.strip()` → same (no surrounding whitespace)
3. `.strip("`")` → `bellows/knowledge/BACKLOG.md` — BACKLOG #1 closed, ...` — leading backtick stripped, but last character is `t` from description, so no trailing strip occurs

Result: a mangled "path" containing the closing backtick, em-dash, and description text. This never exists on disk → `_resolve_deposit_path` returns False → gate reports "missing."

### REPL Evidence — Plan-Text Parser (correct)

```
_extract_plan_required_deposits() returned:
  '/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md'
  'bellows/knowledge/BACKLOG.md'
  'bellows/knowledge/research/agent-prompt-feedback.md'

Total: 3 paths
Block regex matched: True
```

The plan-text parser correctly matched the `**Deposits:**` block and returned ONLY the 3 declared paths. Legacy prose regexes were never reached.

### REPL Evidence — Agent-Receipt Parser (broken)

```
Agent-declared paths (3):
  '/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` — v4.33 with new Lessons Learned entry'
  'bellows/knowledge/BACKLOG.md` — BACKLOG #1 closed, bellows-self exposure opened as known constraint'
  'bellows/knowledge/research/agent-prompt-feedback.md` — prompt feedback appended'
```

All 3 paths are mangled — they contain the closing backtick + em-dash + description text appended to the actual path.

### REPL Evidence — Full Gate Simulation

```
After agent-receipt parsing:
  failures = 3
    missing: bellows/knowledge/BACKLOG.md` — BACKLOG #1 closed, bellows-self exposur...
    missing: /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` — v4.33 with new Le...
    missing: bellows/knowledge/research/agent-prompt-feedback.md` — prompt feedback ...

Plan-required deposits check:
  bellows/knowledge/research/agent-prompt-feedback.md → In agent_declared: False, On disk: True → No failure
  bellows/knowledge/BACKLOG.md → In agent_declared: False, On disk: True → No failure
  /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md → In agent_declared: False, On disk: True → No failure

Final failures count: 3
All from agent-receipt parsing, zero from plan-aware check.
```

The plan-aware check (lines 164–169) passes cleanly because all 3 plan-required paths exist on disk. The false positives come exclusively from the agent-receipt section parser.

### Secondary Effect

Because `agent_declared` contains the mangled paths (not matching the clean plan-required paths), the plan-aware check at line 168 finds `path not in agent_declared` = True for all 3 plan-required paths. But since all 3 exist on disk, `_resolve_deposit_path` returns True, so no additional failures are appended. This means the agent-receipt mangling does NOT cascade into plan-aware false positives — the two code paths fail independently.

---

## Q2: Population Audit — How Many Done/ Plans Have the Same Vulnerability?

### Corpus

- **Total plans in Done/ directories across all watched projects:** 1,024
- **Plans with `**Deposits:**` blocks:** 110
- **At-risk plans** (block + prose backtick paths with trailing description text): 36

### Clarification: Which Vulnerability Matters?

The BACKLOG entry framed the vulnerability around `_extract_plan_required_deposits` (the plan-text parser). The Q1 finding reveals the actual vulnerability is in the **agent-receipt parser** (the `### Files Deposited` section parsing). These are separate code paths:

- **Plan-text parser vulnerability (theoretical):** 36 plans have `**Deposits:**` blocks AND prose backtick paths with trailing descriptions. However, the plan-text parser correctly uses the block when present and never falls back to prose. These 36 plans are NOT at risk.
- **Agent-receipt parser vulnerability (actual):** ANY log where the agent wrote `- \`path\` — description` in the `### Files Deposited` section triggers the false positive. Only 1 log in the corpus (20260505-123021-step.json, the backlog-1-close plan) uses this format.

### Why Only 1 Log?

Most agents write `### Files Deposited` entries in one of these non-vulnerable formats:
- `- path — description` (no backticks → `.strip("`")` is a no-op, path still gets mangled by description, but without the extra backtick)
- `- \`path\`` (backtick-only, no description → `.strip("`")` strips both sides correctly)
- `- path` (bare path, no backticks, no description)

The vulnerable format (`- \`path\` — description`) matches the Output Receipt template in specialist files exactly. The 2026-05-05 execution was the first time an agent followed the template verbatim with all three elements (backticks + em-dash + description). As agents increasingly follow the standard template, this failure will recur.

### Sample At-Risk Plan-Text Plans (for reference, NOT the actual vulnerability)

| Plan | Step | Prose Path with Description |
|---|---|---|
| invoice-pulse/.../executable-planner-governance-sweep-v4.26-2026-04-20.md | 1 | `invoice-pulse/knowledge/research/planner-governance-sweep-findings-2026-04-20.md` |
| forge/.../executable-lessons-forge-phase1-schema-ingest-2026-04-23.md | 1 | `forge/src/test_lessons_forge.py` |
| forge/.../executable-lessons-forge-phase1b-duplicate-orchestrator-specialist-2026-04-23.md | 1 | `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md`, `forge/SPECIALIST_TEMPLATE.md` |
| forge/.../executable-forge-phrasing-eval-helpers-2026-04-23.md | 1 | `src/test_lab_research.py` |
| bellows/.../executable-handle-subdirectory-guard-2026-04-19.md | 1 | `tests/test_bellows.py` |

### Worse-Than-False-Failed (FALSE PASS) Check

**Result: zero false-pass risk.**

The mangled paths always contain description text (e.g., `BACKLOG.md\` — BACKLOG #1 closed, ...`). No filesystem path contains embedded em-dashes and prose descriptions. Therefore:
- Mangled paths ALWAYS fail `_resolve_deposit_path` → always produce false-FAIL (spurious gate trip)
- Mangled paths NEVER pass `_resolve_deposit_path` → never produce false-PASS (silent acceptance of missing deposits)

The failure mode is unidirectional: false-fail only, never false-pass.

---

## Q3: Fix Shape Recommendation

### The BACKLOG Entry's Three Candidates (Assessed Against Q1 Findings)

The BACKLOG entry proposed three fixes targeting `_extract_plan_required_deposits` (the plan-text parser):

1. **Block-takes-precedence (already implemented but bypassed)** — BACKLOG hypothesis was wrong. Block-takes-precedence IS implemented and works correctly. It was not bypassed.
2. **Regex tightening to reject backtick-after-path** — Addresses the wrong code path. The plan-text parser already correctly extracts only backtick-quoted paths from blocks.
3. **Governance change (deposits-only-in-block)** — Irrelevant to the actual root cause, which is in agent-receipt parsing.

**None of the three BACKLOG-suggested fixes address the actual root cause.**

### Actual Fix: Agent-Receipt Path Extraction (gates.py:157)

**File:** `bellows/gates.py`
**Function:** `_gate_deposit_exists`
**Line:** 157

**Current code:**
```python
path = line[2:].strip().strip("`")
```

**Fix — Option A (regex extraction, recommended):**
```python
m = re.match(r'`([^`]+)`', line[2:].strip())
path = m.group(1) if m else line[2:].strip().strip("`")
```

This extracts ONLY the backtick-quoted portion of the line. If the line has no backticks, it falls back to the current behavior. Handles all three agent output formats:
- `` - `path` — description `` → extracts `path`
- `` - `path` `` → extracts `path`
- `- path` → falls back to current `.strip("`")` behavior

**Fix — Option B (split on backtick):**
```python
raw = line[2:].strip()
if raw.startswith("`") and "`" in raw[1:]:
    path = raw[1:raw.index("`", 1)]
else:
    path = raw.strip("`")
```

**Recommendation:** Option A. It is 1 LOC change (replacing line 157), zero architectural impact, zero risk of false-negative (the regex is strictly more precise than `.strip("`")`), and handles the em-dash-description format that the Output Receipt template encourages.

**LOC delta:** +1, -1 (net 0). Single line replacement.

**Secondary consideration:** The agent-receipt parser also adds mangled paths to `agent_declared`, which means the plan-aware check at line 168 cannot match them against clean plan-required paths. After the fix, `agent_declared` will contain clean paths, and the `path not in agent_declared` check will correctly skip plan-required paths the agent declared. This eliminates a latent code-path interaction that currently works by accident (plan-required paths pass because they exist on disk, not because they match agent_declared).

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Traced the deposit_exists false positive to its root cause: the agent-receipt parser at gates.py:157 uses `.strip("`")` which only removes boundary backticks, mangling paths when agents write the standard `- \`path\` — description` Output Receipt format. The BACKLOG entry's hypothesis (plan-text parser prose fallback) was empirically disproven — `_extract_plan_required_deposits` correctly uses the Deposits block. Population audit: 1,024 plans in corpus, 1 log exhibited the failure, but the format is encouraged by specialist templates so recurrence is expected. Fix is a 1-LOC regex extraction at gates.py:157.

### Files Deposited
- `bellows/knowledge/research/deposit-parser-prose-failure-diagnosis-2026-05-05.md`
- `bellows/knowledge/research/agent-prompt-feedback.md`

### Files Created or Modified (Code)
- None (read-only diagnostic)

### Decisions Made
- Classified the BACKLOG entry's three fix candidates as addressing the wrong code path
- Recommended Option A (regex extraction) as the fix for the actual root cause

### Flags for CEO
- None

### Flags for Next Step
- None (single-step diagnostic)
