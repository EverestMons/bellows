# `extract_primary_deposit` — Current Shape

**Date:** 2026-04-19 | **Source:** `bellows/verdict.py` | **Diagnostic:** read-only code trace

---

## Question 1 — `extract_primary_deposit` Verbatim

### (a) Exact function signature

```python
def extract_primary_deposit(step_text: str) -> Optional[str]:
```

Location: `verdict.py` line 19. Single parameter `step_text` (str), no defaults. Returns `Optional[str]`.

### (b) Full function body

```python
def extract_primary_deposit(step_text: str) -> Optional[str]:
    """Extract the primary deposit path from a plan step's text."""
    for line in step_text.splitlines():
        if FEEDBACK_EXCLUSION_RE.search(line):
            continue
        for pattern in (STRICT_DEPOSIT_RE, BOLD_NOUN_DEPOSIT_RE, INLINE_DEPOSIT_RE):
            match = pattern.search(line)
            if match:
                path = match.group(1)
                if '/Desktop/GitHub/' in path:
                    parts = path.split('/Desktop/GitHub/')
                    if len(parts) == 2:
                        path = parts[1]
                return path
    return None
```

Lines 19–33 of `verdict.py`.

### (c) Module-level constants referenced by the body

**Line 13 — `STRICT_DEPOSIT_RE`:**
```python
STRICT_DEPOSIT_RE = re.compile(r'\*\*Deposits?:\*\*\s+(?:.*?\s+)?`([^`]+\.md)`')
```

**Line 14 — `BOLD_NOUN_DEPOSIT_RE`:**
```python
BOLD_NOUN_DEPOSIT_RE = re.compile(r'\*\*(?:Deposit|Write)[^*]+\*\*\s+(?:to|at)\s+`([^`]+\.md)`', re.IGNORECASE)
```

**Line 15 — `INLINE_DEPOSIT_RE`:**
```python
INLINE_DEPOSIT_RE = re.compile(r'[Dd]eposit(?:ing)?\s+(?:[\w]+\s+)*(?:to:?|at|as)\s+`([^`]+\.md)`')
```

**Line 16 — `FEEDBACK_EXCLUSION_RE`:**
```python
FEEDBACK_EXCLUSION_RE = re.compile(r'[Ss]tandard prompt feedback protocol')
```

No helper functions are called — the function uses only the four compiled regexes above plus `str.splitlines()` and `str.split()`.

---

## Question 2 — All Callers of `extract_primary_deposit`

### Call site 1: `verdict.py` line 94 (internal, within `post_verdict_request`)

```python
# verdict.py lines 92-96
        f"**Pause Reason:** {pause_reason_label}\n"
        f"**Pause Reason Code:** {pause_reason}\n"
        f"**Deposit:** {extract_primary_deposit(step_text) or 'none'}\n"
        f"**Gate Result Passed:** {gate_result.get('passed', False)}\n"
        f"**Total Steps:** {total_steps}\n\n"
```

**Argument passed:** `step_text` — the `step_text` parameter of `post_verdict_request()`.

### Call site 2: `bellows.py` line 274 (mid-plan pause)

```python
# bellows.py lines 272-276
                else:
                    _pause_reason = "header_pause"
                verdict.post_verdict_request(plan_path, project_path, current_step, log_path, gate_result, pause_reason=_pause_reason, total_steps=total_steps, step_text=plan_text)
                notifier.notify_verdict_request(
                    app_key, user_key, plan_name, current_step, gate_result["failures"]
```

**Argument passed:** `step_text=plan_text` — **the full plan file content**, not the current step's text.

### Call site 3: `bellows.py` line 333 (final-step / plan-complete pause)

```python
# bellows.py lines 331-335
            else:
                _pause_reason = "auto_close_disabled"
            verdict.post_verdict_request(plan_path, project_path, current_step, log_path, gate_result, pause_reason=_pause_reason, total_steps=total_steps, step_text=plan_text)
            notifier.notify_verdict_request(
                app_key, user_key, plan_name, current_step, gate_result["failures"]
```

**Argument passed:** `step_text=plan_text` — again **the full plan file content**.

### Files with zero call sites

| File | Result |
|------|--------|
| `bellows/gates.py` | No calls to `extract_primary_deposit` |
| `bellows/parser.py` | No calls to `extract_primary_deposit` |
| `bellows/runner.py` | No calls to `extract_primary_deposit` |
| `bellows/planner.py` | No calls to `extract_primary_deposit` |

**Scoping bug confirmed:** Both `bellows.py` call sites pass `plan_text` (the entire plan file) as `step_text`. The function scans line-by-line and returns the first match from *any* step — not necessarily the current step's deposit.

---

## Question 3 — Surrounding `verdict.py` Context

### (a) Imports (lines 1–8)

```python
"""Verdict queue for async Planner review. Posts requests, checks resolved verdicts, logs to ledger."""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional
```

### (b) Module-level constants relevant to deposit extraction (lines 10–16)

```python
BELLOWS_ROOT = Path(__file__).parent.resolve()          # line 10
VERDICTS_DIR = BELLOWS_ROOT / "verdicts"                 # line 11

STRICT_DEPOSIT_RE = re.compile(r'\*\*Deposits?:\*\*\s+(?:.*?\s+)?`([^`]+\.md)`')                                     # line 13
BOLD_NOUN_DEPOSIT_RE = re.compile(r'\*\*(?:Deposit|Write)[^*]+\*\*\s+(?:to|at)\s+`([^`]+\.md)`', re.IGNORECASE)      # line 14
INLINE_DEPOSIT_RE = re.compile(r'[Dd]eposit(?:ing)?\s+(?:[\w]+\s+)*(?:to:?|at|as)\s+`([^`]+\.md)`')                  # line 15
FEEDBACK_EXCLUSION_RE = re.compile(r'[Ss]tandard prompt feedback protocol')                                            # line 16
```

### (c) Plural `Deposits` function

**No plural deposits function exists in verdict.py.** The only deposit-related function is the singular `extract_primary_deposit`. The `STRICT_DEPOSIT_RE` regex does match both `**Deposit:**` and `**Deposits:**` via `Deposits?`, but there is no `extract_deposits` (plural) function that returns a list of all deposits.

---

## Output Receipt

- **Deposit:** `bellows/knowledge/research/extract-primary-deposit-shape-2026-04-19.md`
- **Method:** Read-only code trace of `verdict.py` (lines 1–151), grep across `bellows.py`, `gates.py`, `parser.py`, `runner.py`, `planner.py`
- **Key findings:**
  1. Function signature: `extract_primary_deposit(step_text: str) -> Optional[str]` — single param, returns first match or None
  2. Three-regex priority cascade: STRICT -> BOLD_NOUN -> INLINE, with feedback-line exclusion
  3. Absolute-path normalization via `/Desktop/GitHub/` split
  4. Only caller is `post_verdict_request()` at line 94; both external call sites in `bellows.py` (lines 274, 333) pass `plan_text` (full plan) as `step_text` — **scoping bug**: function scans entire plan, returns first deposit from any step
  5. No plural `extract_deposits` function exists
  6. No callers in gates.py, parser.py, runner.py, or planner.py
