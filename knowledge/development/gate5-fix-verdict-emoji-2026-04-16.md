# Gate 5 Fix + Verdict Emoji — Development Log
**Date:** 2026-04-16 | **Plan:** executable-gate5-fix-verdict-emoji-2026-04-16 | **Step:** 1

---

## Commits

| SHA | Message |
|-----|---------|
| `ad344e0` | fix: gate 5 deposit path resolution — use project_path for relative paths |
| `9c30950` | feat: gate 5 plan-aware deposit requirement — detect missing deposits even when agent omits Output Receipt |
| `90bc475` | feat: ⏸️ emoji for verdict-paused state — distinguish from running/complete |

---

## Files Modified

- `gates.py` — Gate 5 path resolution + plan-aware deposit detection
- `bellows.py` — verdict-paused emoji in print statements + `_check_queue_drain` scan

---

## Gate 5 Function Signature — Before/After

**Before (Commit 1 baseline):**
```python
def _gate_deposit_exists(parsed, failures):
    ...
    if path and not os.path.isfile(path):
        failures.append(...)
```

**After Commit 1 (`ad344e0`):**
```python
def _gate_deposit_exists(parsed, failures, project_path):
    ...
    if path and not os.path.isfile(path) and not os.path.isfile(os.path.join(project_path, path)):
        failures.append(...)
```

**After Commit 2 (`9c30950`) — final signature:**
```python
def _gate_deposit_exists(parsed, failures, project_path, plan_text=None, step_number=None):
```

Call site in `check()`:
```python
# Before:
_gate_deposit_exists(parsed, failures)

# After:
_gate_deposit_exists(parsed, failures, project_path, plan_text=plan_text, step_number=step_number)
```

---

## Deposit-Detection Regex Patterns

Three patterns in `_extract_plan_required_deposits(step_text)`:

**Pattern 1 — Backtick-quoted path:**
```python
r'Deposit[^\n`]*?to\s+`([^`]+)`'
```
Matches: `Deposit findings to \`project/knowledge/research/foo.md\``
Captures: `project/knowledge/research/foo.md`

**Pattern 2 — Unquoted path with directory separator:**
```python
r'Deposit[^\n]*?to\s+(\S+\.md)'
# + guard: if '/' in candidate
```
Matches: `Deposit development log to bellows/knowledge/development/bar.md`
Requires `/` in path to avoid matching bare filenames.

**Pattern 3 — Canonical Python file write:**
```python
r'with open\(["\']([^"\']+\.md)["\'],\s*["\']w["\']'
```
Matches: `with open("bellows/knowledge/development/bar.md", "w") as f:`

---

## Emoji Output Format

**Verdict-paused (two locations in `run_plan`):**
```
Bellows: ⏸️  PAUSED — {plan_name} step {current_step} — waiting for CEO verdict
```

**`_check_queue_drain` when verdict-pending plans exist:**
```
Bellows: ⏸️  {count} plan(s) awaiting verdict
Bellows: 🏁 Queue empty — all plans complete
```

---

## Test Results

```
104 passed, 1 warning in 0.75s
```
All existing tests pass.

---

## Output Receipt

**Status:** Complete
**Step:** 1
**Commits:** 3
**Tests:** 104 passed, 0 failed

### Files Deposited
- `bellows/knowledge/development/gate5-fix-verdict-emoji-2026-04-16.md`
