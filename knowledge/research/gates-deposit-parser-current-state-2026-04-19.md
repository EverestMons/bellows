# Gates / Verdict Current State for Rule 26 Parser Work

**Date:** 2026-04-19 | **Source diagnostic:** `in-progress-diagnostic-gates-deposit-parser-current-state-2026-04-19.md`

---

## Question 1 — `_gate_deposit_exists` current shape

### (a) Function signature

```python
def _gate_deposit_exists(parsed, failures, project_path, plan_text=None, step_number=None):
```

- `parsed`: dict — the runner output parsed by `parser.parse()` (contains `result_text`, etc.)
- `failures`: list — mutable list; gate appends failure dicts to it
- `project_path`: str — absolute path to the project root
- `plan_text`: str or None — full plan file content (keyword-only by convention)
- `step_number`: int or None — current step number

### (b) Return shape

None (mutates `failures` list in-place).

### (c) Full body verbatim

```python
def _gate_deposit_exists(parsed, failures, project_path, plan_text=None, step_number=None):
    result_text = parsed.get("result_text", "")
    match = re.search(r"### Files Deposited\s*\n(.*?)(?:\n###|\Z)", result_text, re.DOTALL)

    # Collect agent-declared paths and check they exist on disk
    agent_declared = set()
    if match:
        section = match.group(1)
        for line in section.splitlines():
            line = line.strip()
            if not line or not line.startswith("- "):
                continue
            path = line[2:].strip().strip("`")
            if path:
                agent_declared.add(path)
                if not _resolve_deposit_path(path, project_path):
                    failures.append({"gate": "deposit_exists", "evidence": f"missing: {path}"})

    # Plan-aware: detect deposits the plan requires but the agent didn't declare
    if plan_text and step_number is not None:
        step_pattern = rf"## STEP {step_number}\b.*?(?=\n## STEP |\Z)"
        step_match = re.search(step_pattern, plan_text, re.DOTALL)
        if step_match:
            step_text = step_match.group(0)
            for path in _extract_plan_required_deposits(step_text):
                if path not in agent_declared and not _resolve_deposit_path(path, project_path):
                    failures.append({"gate": "deposit_exists", "evidence": f"plan-required deposit missing (not declared by agent): {path}"})
```

### (d) Call sites

**File: `gates.py`, line 58** (only caller):

```python
    # Gate 5: deposit exists
    _gate_deposit_exists(parsed, failures, project_path, plan_text=plan_text, step_number=step_number)
```

Context (lines 56-60):
```python
    # Gate 4: no permission denials
    _gate_no_permission_denials(parsed, failures)
    # Gate 5: deposit exists
    _gate_deposit_exists(parsed, failures, project_path, plan_text=plan_text, step_number=step_number)
    # Gate 6: QA step detection (informational)
```

Called from `check()` at `gates.py:58`. No direct calls from `bellows.py`.

**File: `bellows.py`** — `_gate_deposit_exists` is NOT called directly from `bellows.py`. It is invoked indirectly via `gates.check()` at two locations:

- `bellows.py:253`: `gate_result = gates.check(parsed, plan_text, current_step, project_path, files_changed=files_changed)`
- `bellows.py:311`: `gate_result = gates.check(parsed, plan_text, current_step, project_path, files_changed=files_changed)`

### (e) What inputs the callers pass

`gates.check()` passes:
- `parsed` — the full parsed runner output dict
- `failures` — an internally-created empty list
- `project_path` — the project_path string from its own parameter
- `plan_text=plan_text` — the **full plan file text** (not scoped to a step)
- `step_number=step_number` — the current step integer

The step-scoping happens **inside** `_gate_deposit_exists` itself (lines 148-154) via regex extraction.

---

## Question 2 — `_extract_plan_required_deposits` current shape

### (a) Function signature

```python
def _extract_plan_required_deposits(step_text):
```

- `step_text`: str — text of a single plan step (already scoped by caller)

### (b) Return shape

Returns `set[str]` — a set of file path strings.

### (c) Full body verbatim

```python
def _extract_plan_required_deposits(step_text):
    """Extract file paths explicitly required by deposit instructions in the plan step text.

    Only matches explicit 'Deposit X to path' instructions and canonical Python
    file writes. Does not match vague references without a concrete path.
    """
    paths = set()
    # Pattern 1: Deposit ... to `path` (backtick-quoted — most explicit form)
    for m in re.finditer(r'Deposit[^\n`]*?to\s+`([^`]+)`', step_text, re.IGNORECASE):
        candidate = m.group(1).strip()
        if candidate:
            paths.add(candidate)
    # Pattern 2: Deposit ... to path.md (unquoted, must contain a directory separator)
    for m in re.finditer(r'Deposit[^\n]*?to\s+(\S+\.md)', step_text, re.IGNORECASE):
        candidate = m.group(1).strip().rstrip('.,;)').strip('`')
        if '/' in candidate:
            paths.add(candidate)
    # Pattern 3: with open("path.md", "w") canonical Python write
    for m in re.finditer(r'with open\(["\']([^"\']+\.md)["\'],\s*["\']w["\']', step_text):
        paths.add(m.group(1).strip())
    return paths
```

### (d) Exact regex patterns

1. **Pattern 1** — `r'Deposit[^\n`]*?to\s+`([^`]+)`'` (case-insensitive)
   - Matches "Deposit ... to \`path\`" — backtick-quoted deposit target, most explicit form.

2. **Pattern 2** — `r'Deposit[^\n]*?to\s+(\S+\.md)'` (case-insensitive)
   - Matches "Deposit ... to path.md" — unquoted, but requires a `/` in the candidate to filter noise.

3. **Pattern 3** — `r'with open\(["\']([^"\']+\.md)["\'],\s*["\']w["\']'` (case-sensitive)
   - Matches `with open("path.md", "w")` — canonical Python file write pattern.

### (e) Plan boundary scoping

`_extract_plan_required_deposits` does NOT perform its own scoping — it receives `step_text` already scoped by its caller. The caller (`_gate_deposit_exists`, line 148-151) extracts the step text using:

```python
step_pattern = rf"## STEP {step_number}\b.*?(?=\n## STEP |\Z)"
step_match = re.search(step_pattern, plan_text, re.DOTALL)
```

This scopes from `## STEP N` to the next `## STEP` header or end-of-file.

### (f) Callers

**Only caller:** `gates.py`, line 152, inside `_gate_deposit_exists`:

```python
            for path in _extract_plan_required_deposits(step_text):
```

No other callers in gates.py, bellows.py, parser.py, or verdict.py.

---

## Question 3 — `post_verdict_request` current shape in `verdict.py`

### (a) Function signature

```python
def post_verdict_request(plan_path, project_path, step_number, log_path, gate_result, pause_reason="auto_close_disabled", planner_py_decision=None, total_steps=None, step_text=""):
```

- `plan_path`: str — path to the plan file
- `project_path`: str — path to the project root
- `step_number`: int — current step
- `log_path`: str — path to log directory
- `gate_result`: dict — gate check result dict
- `pause_reason`: str — reason code for pause (default "auto_close_disabled")
- `planner_py_decision`: dict or None — legacy planner decision
- `total_steps`: int or None — total steps in plan (raises ValueError if None)
- `step_text`: str — plan text (note: callers pass the FULL plan text, not step-scoped text)

### (b) Full body verbatim

```python
def post_verdict_request(plan_path, project_path, step_number, log_path, gate_result, pause_reason="auto_close_disabled", planner_py_decision=None, total_steps=None, step_text=""):
    """Create a verdict request file in verdicts/pending/."""
    pending_dir = VERDICTS_DIR / "pending"
    pending_dir.mkdir(parents=True, exist_ok=True)

    slug = _slug_from_path(plan_path)
    filename = f"verdict-request-{slug}-step-{step_number}.md"
    filepath = pending_dir / filename

    _pause_reason_labels = {
        "gate_failure": "Gate failure",
        "qa_checkpoint": "QA checkpoint",
        "agent_verdict_request": "Agent verdict request",
        "header_pause": "Header pause (pause_for_verdict)",
        "auto_close_disabled": "Auto-close disabled",
    }
    pause_reason_label = _pause_reason_labels.get(pause_reason, pause_reason)

    if total_steps is None:
        raise ValueError("total_steps must be an integer, got None")

    if pause_reason == "gate_failure" and gate_result.get("failures"):
        failures_text = ""
        for f in gate_result["failures"]:
            failures_text += f"- **{f['gate']}**: {f['evidence']}\n"
        pause_section = f"## Gate Failures\n\n{failures_text}"
    else:
        _pause_descriptions = {
            "qa_checkpoint": "This step is a QA checkpoint. All gates passed — CEO review requested before proceeding.",
            "agent_verdict_request": "The agent deposited a verdict-request file during execution and is requesting\nCEO guidance before proceeding to the next step.",
            "header_pause": "The plan header specifies `pause_for_verdict`. This step is complete;\nCEO review is required before the next step begins.",
            "auto_close_disabled": "Plan completed. Auto-close is disabled for this plan (diagnostic default or\n`auto_close: false` in header). CEO review required before closing.",
        }
        desc = _pause_descriptions.get(pause_reason, f"Pause reason: {pause_reason}")
        pause_section = f"## Pause Reason\n\n{desc}"

    content = (
        f"# Verdict Request\n\n"
        f"**Plan:** {plan_path}\n"
        f"**Project:** {project_path}\n"
        f"**Step:** {step_number}\n"
        f"**Log:** {log_path}\n"
        f"**Timestamp:** {datetime.now().isoformat()}\n"
        f"**Pause Reason:** {pause_reason_label}\n"
        f"**Pause Reason Code:** {pause_reason}\n"
        f"**Deposit:** {extract_primary_deposit(step_text) or 'none'}\n"
        f"**Gate Result Passed:** {gate_result.get('passed', False)}\n"
        f"**Total Steps:** {total_steps}\n\n"
        f"{pause_section}\n\n"
        f"## Files Changed\n\n"
    )
    for fc in gate_result.get("files_changed", []):
        content += f"- {fc}\n"

    if planner_py_decision:
        content += f"\n## Planner.py Decision (legacy)\n\n{json.dumps(planner_py_decision)}\n"

    filepath.write_text(content)
    return str(filepath)
```

### (c) Template string (verbatim)

```python
    content = (
        f"# Verdict Request\n\n"
        f"**Plan:** {plan_path}\n"
        f"**Project:** {project_path}\n"
        f"**Step:** {step_number}\n"
        f"**Log:** {log_path}\n"
        f"**Timestamp:** {datetime.now().isoformat()}\n"
        f"**Pause Reason:** {pause_reason_label}\n"
        f"**Pause Reason Code:** {pause_reason}\n"
        f"**Deposit:** {extract_primary_deposit(step_text) or 'none'}\n"
        f"**Gate Result Passed:** {gate_result.get('passed', False)}\n"
        f"**Total Steps:** {total_steps}\n\n"
        f"{pause_section}\n\n"
        f"## Files Changed\n\n"
    )
```

### (d) Callers in `bellows.py`

**Call site 1 — `bellows.py:274`** (inside the while-loop, mid-plan pause):

```python
                verdict.post_verdict_request(plan_path, project_path, current_step, log_path, gate_result, pause_reason=_pause_reason, total_steps=total_steps, step_text=plan_text)
```

Context (lines 272-276):
```python
                else:
                    _pause_reason = "header_pause"
                verdict.post_verdict_request(plan_path, project_path, current_step, log_path, gate_result, pause_reason=_pause_reason, total_steps=total_steps, step_text=plan_text)
                notifier.notify_verdict_request(
                    app_key, user_key, plan_name, current_step, gate_result["failures"]
```

**Call site 2 — `bellows.py:333`** (final-step pause):

```python
            verdict.post_verdict_request(plan_path, project_path, current_step, log_path, gate_result, pause_reason=_pause_reason, total_steps=total_steps, step_text=plan_text)
```

Context (lines 331-335):
```python
            else:
                _pause_reason = "auto_close_disabled"
            verdict.post_verdict_request(plan_path, project_path, current_step, log_path, gate_result, pause_reason=_pause_reason, total_steps=total_steps, step_text=plan_text)
            notifier.notify_verdict_request(
                app_key, user_key, plan_name, current_step, gate_result["failures"]
```

**Critical observation:** Both call sites pass `step_text=plan_text` — the **full plan file content**, not the current step's text. The parameter is named `step_text` in the function signature, but receives the entire plan. `extract_primary_deposit(step_text)` in verdict.py:94 therefore scans the **entire plan**, not just the current step. This means it will return the first deposit match from any step, not necessarily the current step's deposit.

---

## Question 4 — Step-text extraction in the codebase

**No standalone step-text extraction function found in gates.py, bellows.py, parser.py, or verdict.py.**

However, the same inline regex pattern exists in **two places** within `gates.py`:

1. **`_gate_deposit_exists`** at line 148:
   ```python
   step_pattern = rf"## STEP {step_number}\b.*?(?=\n## STEP |\Z)"
   step_match = re.search(step_pattern, plan_text, re.DOTALL)
   ```

2. **`_gate_scope_check`** at line 199:
   ```python
   pattern = rf"## STEP {step_number}\b.*?(?=\n## STEP |\Z)"
   match = re.search(pattern, plan_text, re.DOTALL)
   ```

Both use identical regex logic. Neither is factored out into a reusable function.

`verdict.py`'s `extract_primary_deposit(step_text)` **expects** step-scoped text as input but does not extract it — it relies on the caller to provide scoped text. As noted in Question 3, the current callers in `bellows.py` pass the full plan text instead.

---

## Question 5 — Test layout for gates and verdict

### (a) Line counts and test function counts

| File | Lines | `def test_` count |
|---|---|---|
| `tests/test_gates.py` | 189 | 22 |
| `tests/test_verdict.py` | 184 | 11 |

### (b) Test framework

Both files use **pytest** (bare `assert` statements, no `unittest.TestCase` subclassing). `unittest.mock.patch` is imported for mocking.

### (c) Fixture plan files

No `.md` fixture files found in `tests/`. No `tests/fixtures/` subdirectory exists. Plan text fixtures are defined inline as Python strings (e.g., `PLAN_TEXT` constant in `test_gates.py`).

### (d) Existing tests for deposit-detection functions

- `test_gates.py` has **`test_deposit_path_missing`** (line 82) — tests `_gate_deposit_exists` indirectly via `gates.check()` with a mocked `os.path.isfile`.
- `test_gates.py` has **`test_no_deposit_section_passes`** (line 120) — tests that no deposit failure fires when result_text has no `### Files Deposited` section.

**No existing tests directly test `_extract_plan_required_deposits`.** No tests exercise the plan-aware deposit detection (patterns 1-3) or the step-text scoping logic within `_gate_deposit_exists`.

No existing tests in `test_verdict.py` test `extract_primary_deposit`.

---

## Output Receipt

- **Status:** Complete
- **Deposit:** `bellows/knowledge/research/gates-deposit-parser-current-state-2026-04-19.md`
- **Key findings for follow-up work:**
  1. `post_verdict_request` receives `step_text=plan_text` (full plan) at both call sites — `extract_primary_deposit` scans the entire plan, not the current step. This is a scoping bug.
  2. Step-text extraction is duplicated inline in two gates (`_gate_deposit_exists`, `_gate_scope_check`) — candidate for factoring into a shared helper.
  3. `_extract_plan_required_deposits` has no direct test coverage.
  4. `extract_primary_deposit` has no direct test coverage.
  5. No fixture `.md` files exist in the test tree — all plan text is inline strings.
