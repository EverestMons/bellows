# Verdict Schema Refresh — Diagnostic Findings

**Date:** 2026-04-19 | **Plan:** diagnostic-verdict-schema-refresh-2026-04-19
**Purpose:** Refresh 2026-04-18 verdict schema findings after Rule 26 parser work shipped.

---

## Q1 — Callers of `post_verdict_request()`

There are exactly **2 call sites**, both in `bellows.py` function `run_plan()`.

### Call Site 1 — bellows.py:274 (while-loop mid-plan pause)

```python
# bellows.py lines 265-278
265:                log_path = str(BELLOWS_ROOT / "logs")
266:                if not gate_result["passed"]:
267:                    _pause_reason = "gate_failure"
268:                elif gate_result["is_qa_step"]:
269:                    _pause_reason = "qa_checkpoint"
270:                elif gate_result.get("verdict_requested", {}).get("requested", False):
271:                    _pause_reason = "agent_verdict_request"
272:                else:
273:                    _pause_reason = "header_pause"
274:                verdict.post_verdict_request(plan_path, project_path, current_step, log_path, gate_result, pause_reason=_pause_reason, total_steps=total_steps, step_text=plan_text)
275:                notifier.notify_verdict_request(
276:                    app_key, user_key, plan_name, current_step, gate_result["failures"]
277:                )
278:                # Rename plan to verdict-pending
```

**(a)** File: `bellows.py`, line 274. **(b)** Function: `run_plan()`. **(c)** `total_steps` computed at line 199 via `extract_total_steps(metadata_text)` (where `metadata_text` is the shadow copy or original plan text); forced to 1 for diagnostics at line 200-201. Always an integer at this call site. **(d)** `project_path` in scope (line 185); `plan_text` in scope (line 181); `current_step` in scope (line 241 or incremented in the loop).

### Call Site 2 — bellows.py:333 (final-step pause)

```python
# bellows.py lines 322-337
322:            log_path = str(BELLOWS_ROOT / "logs")
323:            if not gate_result["passed"]:
324:                _pause_reason = "gate_failure"
325:            elif gate_result["is_qa_step"]:
326:                _pause_reason = "qa_checkpoint"
327:            elif gate_result.get("verdict_requested", {}).get("requested", False):
328:                _pause_reason = "agent_verdict_request"
329:            elif header_says_pause(header, current_step, total_steps, gate_result["is_qa_step"]):
330:                _pause_reason = "header_pause"
331:            else:
332:                _pause_reason = "auto_close_disabled"
333:            verdict.post_verdict_request(plan_path, project_path, current_step, log_path, gate_result, pause_reason=_pause_reason, total_steps=total_steps, step_text=plan_text)
334:            notifier.notify_verdict_request(
335:                app_key, user_key, plan_name, current_step, gate_result["failures"]
336:            )
337:            verdict_pending_path = os.path.join(plan_dir, f"verdict-pending-{plan_filename}")
```

**(a)** File: `bellows.py`, line 333. **(b)** Function: `run_plan()`. **(c)** `total_steps` — same computation as Call Site 1, same variable, always integer. **(d)** Same scope: `project_path`, `plan_text`, `current_step` all available. This block adds `"auto_close_disabled"` as a possible pause reason (line 332) — the only call site that can produce it.

### No other callers

Grep confirms no other module calls `post_verdict_request`. Test files call it directly for testing but those are not production call sites.

---

## Q2 — `extract_primary_deposit()` signature

### Definition — verdict.py:34-62

```python
# verdict.py lines 34-62
34: def extract_primary_deposit(step_text: str) -> Optional[str]:
35:     """Extract the primary deposit path from a plan step's text."""
36:     # Rule 26: prefer declared **Deposits:** block when present — block is authoritative,
37:     # legacy regexes not applied as fallback.
38:     block_match = DEPOSITS_BLOCK_RE.search(step_text)
39:     if block_match:
40:         for m in BLOCK_BULLET_RE.finditer(block_match.group(1)):
41:             path = m.group(1)
42:             if path.endswith('.md'):
43:                 if '/Desktop/GitHub/' in path:
44:                     parts = path.split('/Desktop/GitHub/')
45:                     if len(parts) == 2:
46:                         path = parts[1]
47:                 return path
48:         return None
49:
50:     for line in step_text.splitlines():
51:         if FEEDBACK_EXCLUSION_RE.search(line):
52:             continue
53:         for pattern in (STRICT_DEPOSIT_RE, BOLD_NOUN_DEPOSIT_RE, INLINE_DEPOSIT_RE):
54:             match = pattern.search(line)
55:             if match:
56:                 path = match.group(1)
57:                 if '/Desktop/GitHub/' in path:
58:                     parts = path.split('/Desktop/GitHub/')
59:                     if len(parts) == 2:
60:                         path = parts[1]
61:                 return path
62:     return None
```

**Signature:** `extract_primary_deposit(step_text: str) -> Optional[str]`

**Parameters:** Single parameter `step_text` (str) — the text of a single plan step, NOT the full plan.

**Return:** `Optional[str]` — the first `.md` deposit path found, or `None`.

**Helper functions called:** Uses module-level compiled regexes `DEPOSITS_BLOCK_RE`, `BLOCK_BULLET_RE`, `FEEDBACK_EXCLUSION_RE`, `STRICT_DEPOSIT_RE`, `BOLD_NOUN_DEPOSIT_RE`, `INLINE_DEPOSIT_RE` (all defined at verdict.py lines 14-20). Does NOT call `_extract_step_text_from_plan()` — that function is called by `post_verdict_request()` at line 115 to isolate the step text before passing it to `extract_primary_deposit()`.

**Circular import question:** `post_verdict_request()` already calls `extract_primary_deposit()` at line 126. Both functions are in the same file (`verdict.py`), so this is an intra-module call — **no circular import risk whatsoever**. The call chain is:

```python
# verdict.py line 115
115:    current_step_text = _extract_step_text_from_plan(step_text, step_number) or step_text
# verdict.py line 126
126:    f"**Deposit:** {extract_primary_deposit(current_step_text) or 'none'}\n"
```

---

## Q3 — `_pause_reason_labels` current state

### Current dict — verdict.py:87-93

```python
# verdict.py lines 87-94
87:     _pause_reason_labels = {
88:         "gate_failure": "Gate failure",
89:         "qa_checkpoint": "QA checkpoint",
90:         "agent_verdict_request": "Agent verdict request",
91:         "header_pause": "Header pause (pause_for_verdict)",
92:         "auto_close_disabled": "Auto-close disabled",
93:     }
94:     pause_reason_label = _pause_reason_labels.get(pause_reason, pause_reason)
```

Note: this dict is a **local variable** inside `post_verdict_request()`, not a module-level constant.

### Cross-reference: all unique `pause_reason` values passed by callers

| Caller Location | Value | In Dict? |
|---|---|---|
| bellows.py:267 | `"gate_failure"` | Yes |
| bellows.py:269 | `"qa_checkpoint"` | Yes |
| bellows.py:271 | `"agent_verdict_request"` | Yes |
| bellows.py:273 | `"header_pause"` | Yes |
| bellows.py:324 | `"gate_failure"` | Yes |
| bellows.py:326 | `"qa_checkpoint"` | Yes |
| bellows.py:328 | `"agent_verdict_request"` | Yes |
| bellows.py:330 | `"header_pause"` | Yes |
| bellows.py:332 | `"auto_close_disabled"` | Yes |
| default param (verdict.py:78) | `"auto_close_disabled"` | Yes |

**All 5 unique values match dict keys. No caller passes an unlisted key.**

**Enum status:** Pause reasons are bare string literals — no `Enum` or constants defined anywhere in the codebase. The dict keys in `_pause_reason_labels` serve as the de facto taxonomy. The `_pause_descriptions` dict (verdict.py:105-110) uses the same 4 keys (excluding `gate_failure` which gets its own branch at line 99).

---

## Q4 — Test coverage for `verdict.py`

### Test files in `bellows/tests/`

11 files total:
- `test_bellows.py`
- `test_extract_primary_deposit_blocks.py`
- `test_gates.py`
- `test_notifier_server.py`
- `test_phase4_parser.py`
- `test_phase4_planner_retry.py`
- `test_planner.py`
- `test_rule_26_deposit_parser.py`
- `test_runner.py`
- `test_runner_parser.py`
- `test_verdict.py`

### Files that directly test verdict.py functions

**1. `test_verdict.py`** — 12 tests targeting verdict.py functions

- Imports: `import verdict`
- Functions tested: `post_verdict_request` (10 tests), `check_verdict` (3 tests), `log_to_ledger` (1 test)
- Assertion style: Per-field string assertions on file content (`assert "receipt_status" in content`)
- Fixtures: `_make_gate_result()` helper (line 67) builds gate result dicts; no shared pytest fixture that posts a verdict request

Representative test:

```python
# test_verdict.py lines 13-30
def test_post_verdict_request_creates_file():
    with tempfile.TemporaryDirectory() as tmp:
        with patch.object(verdict, "VERDICTS_DIR", Path(tmp) / "verdicts"):
            gate_result = {
                "passed": False,
                "failures": [{"gate": "receipt_status", "evidence": "Blocked"}],
                "is_qa_step": False,
                "files_changed": ["gates.py"],
            }
            path = verdict.post_verdict_request(
                "/tmp/plans/in-progress-executable-test-2026-04-16.md",
                "/tmp/project", 1, "/tmp/logs", gate_result, pause_reason="gate_failure", total_steps=2
            )
            assert os.path.isfile(path)
            content = open(path).read()
            assert "receipt_status" in content
            assert "Blocked" in content
            assert "gates.py" in content
```

**2. `test_extract_primary_deposit_blocks.py`** — 6 tests targeting `extract_primary_deposit`

- Imports: `from verdict import extract_primary_deposit`
- Functions tested: `extract_primary_deposit` only
- Assertion style: Exact return-value assertions (`assert result == "project/knowledge/development/my-feature-2026-04-19.md"`)
- Covers: block single path, block multiple (first returned), none bullet, directory-only, legacy fallback, blockquote prefix

**3. `test_rule_26_deposit_parser.py`** — 6 tests targeting both `gates._extract_plan_required_deposits` and `verdict.extract_primary_deposit`

- Imports: `import gates`, `import verdict`
- Verdict-specific tests: 1 test (`test_extract_primary_deposit_scoping_in_post_verdict_request`) — verifies the scoping fix where `post_verdict_request` extracts deposit from the correct step
- Assertion style: Per-field regex match on verdict file content (`re.search(r'\*\*Deposit:\*\*\s+(.*)', content)`)

**4. `test_bellows.py`, `test_gates.py`, `test_runner_parser.py`** — reference verdict indirectly via mock patching or imports but do not directly test verdict.py functions

### Coverage summary

| verdict.py Function | Test Count | Coverage Quality |
|---|---|---|
| `post_verdict_request` | 11 (10 in test_verdict + 1 in test_rule_26) | Good — all 5 pause reasons tested, gate failure section vs prose section tested, scoping tested |
| `extract_primary_deposit` | 12 (6 in test_blocks + 6 in test_rule_26) | Good — block/legacy/none/prefix/scoping all covered |
| `check_verdict` | 3 (test_verdict) | Adequate — not_found, continue, stop |
| `log_to_ledger` | 1 (test_verdict) | Minimal — tests append-two-entries, no edge cases |
| `_extract_step_text_from_plan` | 0 direct, tested indirectly via `extract_primary_deposit` scoping test | Gap — no dedicated unit test |
| `_slug_from_path` | 0 | Gap — no dedicated unit test (exercised indirectly by `post_verdict_request` tests) |

---

## Q5 — Circular import risk

### verdict.py imports — lines 1-8

```python
# verdict.py lines 1-8
1: """Verdict queue for async Planner review. Posts requests, checks resolved verdicts, logs to ledger."""
2:
3: import json
4: import os
5: import re
6: from datetime import datetime
7: from pathlib import Path
8: from typing import Optional
```

**verdict.py imports ZERO modules from the bellows codebase.** Only stdlib imports.

### bellows.py imports — lines 1-28

```python
# bellows.py lines 1-28
1: """Entry point. Initializes watcher and starts the orchestration loop."""
2:
3: import json
4: import os
5: import pathlib
6: import re
7: import shutil
8: import sqlite3
9: import subprocess
10: import threading
11: import time
12: from datetime import datetime
13: from pathlib import Path
14: from typing import Optional
15:
16: BELLOWS_ROOT = Path(__file__).parent.resolve()
17: DB_PATH = str(BELLOWS_ROOT / "bellows.db")
18: SHADOW_CACHE_DIR = BELLOWS_ROOT / ".bellows-cache"
19:
20: from watchdog.observers import Observer
21: from watchdog.events import FileSystemEventHandler
22:
23: import runner
24: import parser
25: import gates
26: import verdict
27: import notifier
28: import server
```

**bellows.py imports verdict at line 26.** The dependency is one-directional: `bellows → verdict`. There is no reverse dependency (`verdict → bellows`).

### Circular import assessment

**No circular import risk exists or would be created by the proposed schema executable.**

`post_verdict_request()` already calls `extract_primary_deposit()` at verdict.py:126 — both functions live in `verdict.py`. The step-text extraction helper `_extract_step_text_from_plan()` is also in `verdict.py` (line 23). The entire deposit extraction pipeline runs within `verdict.py` without touching any other bellows module.

If the executable needs to add fields (Project, Gate Result Passed, Pause Reason Code), all the data is already passed as parameters to `post_verdict_request()`:
- `project_path` — already a parameter (verdict.py:78)
- `gate_result['passed']` — already passed via `gate_result` parameter
- `pause_reason` — already a parameter

**No new imports, no new dependencies, no resolution needed.** This was confirmed by the 2026-04-18 diagnostic but is now doubly confirmed: the Rule 26 changes added `_extract_step_text_from_plan` and `extract_primary_deposit` to `verdict.py` (not to a shared module), keeping the dependency graph unchanged.

---

## Delta from 2026-04-18 Diagnostic

| Item | 2026-04-18 State | 2026-04-19 State (current) | Change |
|---|---|---|---|
| `post_verdict_request` signature | `(plan_path, step_number, log_path, gate_result, pause_reason, planner_py_decision, total_steps)` | `(plan_path, project_path, step_number, log_path, gate_result, pause_reason, planner_py_decision, total_steps, step_text)` | **`project_path` and `step_text` added** |
| `**Project:**` field | Missing — proposed as new | **Already present** (verdict.py:120) | Shipped in Plan A |
| `**Pause Reason Code:**` field | Missing — proposed as new | **Already present** (verdict.py:125) | Shipped in Plan A |
| `**Gate Result Passed:**` field | Missing — proposed as new | **Already present** (verdict.py:127) | Shipped in Plan A |
| `**Total Steps:**` None guard | `total_steps` defaulted to `None` | `raise ValueError` if None (verdict.py:96-97) | Shipped in Plan A |
| `**Deposit:**` field | Missing — proposed as new | **Already present** (verdict.py:126) via `extract_primary_deposit()` | Shipped in Plan B |
| `extract_primary_deposit` | Not in verdict.py | verdict.py:34-62, block-aware Rule 26 extraction | Shipped in Plan B + Rule 26 scope fix |
| `_extract_step_text_from_plan` | Not in verdict.py | verdict.py:23-31, scopes deposit extraction to current step | Shipped with Plan B |
| Call site line numbers | ~lines 274 and 333 (approximate) | Lines 274 and 333 (confirmed exact) | Minor drift from intermediate commits |
| Test count for verdict.py | Not measured | 12 in test_verdict + 12 in deposit tests = 24 total | Good coverage |

**Key finding: All 5 schema additions proposed by the 2026-04-18 diagnostic have already been implemented.** The verdict request file now contains: Plan, Project, Step, Log, Timestamp, Pause Reason (label), Pause Reason Code (raw enum), Deposit (extracted path), Gate Result Passed (boolean), Total Steps (integer, never None), pause section, files changed section.

The proposed executable (A–E changes) has **already shipped** across Plan A (`executable-bellows-verdict-schema-plan-a-2026-04-18`) and Plan B (`executable-bellows-verdict-schema-plan-b-2026-04-18`). No further schema changes are needed.

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Read verdict.py and bellows.py end-to-end. Answered all 5 diagnostic questions with verbatim line-numbered code snippets. Discovered that all 5 schema additions proposed by the 2026-04-18 diagnostic have already been implemented — the executable this diagnostic was supposed to unblock is unnecessary.

### Files Deposited
- `bellows/knowledge/research/verdict-schema-refresh-2026-04-19.md` — this findings file

### Files Created or Modified (Code)
- None (read-only investigation)

### Decisions Made
- None (diagnostic only)

### Flags for CEO
- The proposed verdict schema executable (A–E changes) is redundant — all changes already shipped via Plan A and Plan B. The Planner should close or cancel the planned executable rather than writing it.

### Flags for Next Step
- None — this diagnostic does not have a Step 2
