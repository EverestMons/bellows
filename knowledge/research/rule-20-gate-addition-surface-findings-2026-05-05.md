# Rule 20 Gate Addition Surface — Investigation Findings

**Date:** 2026-05-05
**Agent:** Bellows Developer
**Plan Reference:** `knowledge/decisions/in-progress-diagnostic-rule-20-gate-addition-surface-2026-05-05.md`

---

## Investigation Section 1 — Gate Function Pattern

Each gate follows a private `_gate_*` function pattern. All blocking gates receive a `failures` list and append a dict on failure.

| Gate # | Function Name | Parameters | Blocking? | Failure Shape |
|--------|--------------|------------|-----------|---------------|
| 1 | `_gate_receipt_status` | `(parsed, failures)` | Yes | `{"gate": "receipt_status", "evidence": status}` |
| 2 | `_gate_ceo_flags` | `(parsed, failures)` | Yes | `{"gate": "ceo_flags", "evidence": "; ".join(flags)}` |
| 3 | `_gate_no_errors` | `(parsed, failures)` | Yes | `{"gate": "no_errors", "evidence": parsed.get("error", "unknown error")}` |
| 4 | `_gate_no_permission_denials` | `(parsed, failures)` | Yes | `{"gate": "no_permission_denials", "evidence": f"{len(blocking)} blocking denial(s): {first}"}` |
| 5 | `_gate_deposit_exists` | `(parsed, failures, project_path, plan_text=None, step_number=None)` | Yes | `{"gate": "deposit_exists", "evidence": f"missing: {path}"}` or `{"gate": "deposit_exists", "evidence": f"plan-required deposit missing (not declared by agent): {path}"}` |
| 6 | `_gate_is_qa_step` | `(plan_text, step_number)` | No (informational) | Returns `bool`, no failures append |
| 7 | `_gate_file_change_audit` | `(files_changed)` | No (informational) | Returns `files_changed`, no failures append |
| 8 | `_gate_scope_check` | `(plan_text, step_number, files_changed, failures)` | Yes | `{"gate": "scope_check", "evidence": f"out-of-scope files: {', '.join(out_of_scope)} \| plan step context: {context}"}` |

### Verbatim Gate Function Signatures

```python
def _gate_receipt_status(parsed, failures):
    status = parsed.get("receipt_status", "Unknown")
    if status != "Complete":
        failures.append({"gate": "receipt_status", "evidence": status})

def _gate_ceo_flags(parsed, failures):
    flags = parsed.get("ceo_flags", [])
    if flags:
        failures.append({"gate": "ceo_flags", "evidence": "; ".join(flags)})

def _gate_no_errors(parsed, failures):
    if parsed.get("is_error", False):
        failures.append({"gate": "no_errors", "evidence": parsed.get("error", "unknown error")})

def _gate_no_permission_denials(parsed, failures):
    # Filters READ_CLASS_TOOLS, appends on blocking denials
    ...

def _gate_deposit_exists(parsed, failures, project_path, plan_text=None, step_number=None):
    # Checks agent-declared deposits and plan-required deposits
    ...

def _gate_is_qa_step(plan_text, step_number):
    # Returns bool — informational only
    ...

def _gate_file_change_audit(files_changed):
    # Returns files_changed — informational only
    ...

def _gate_scope_check(plan_text, step_number, files_changed, failures):
    # Checks files_changed against step text mentions
    ...
```

---

## Investigation Section 2 — Gate Dispatcher

The dispatcher is the `check()` function at `gates.py:36–83`.

### Function Signature

```python
def check(parsed, plan_text, step_number, project_path, files_changed=None):
```

### Gate Call Order (verbatim from `check()`)

```python
    # Gate 1: receipt status
    _gate_receipt_status(parsed, failures)
    # Gate 2: CEO flags
    _gate_ceo_flags(parsed, failures)
    # Gate 3: no errors
    _gate_no_errors(parsed, failures)
    # Gate 4: no permission denials
    _gate_no_permission_denials(parsed, failures)
    # Gate 5: deposit exists
    _gate_deposit_exists(parsed, failures, project_path, plan_text=plan_text, step_number=step_number)
    # Gate 6: QA step detection (informational)
    is_qa_step = _gate_is_qa_step(plan_text, step_number)
    # Gate 7: file change audit (informational)
    _gate_file_change_audit(files_changed)
    # Gate 8: scope check
    _gate_scope_check(plan_text, step_number, files_changed, failures)
```

### Inputs Available to a New Gate

The dispatcher receives all of: `parsed` (parsed JSON output from agent), `plan_text` (full plan markdown), `step_number` (int), `project_path` (str), `files_changed` (list of str). Additionally, `is_qa_step` is computed by gate 6 and stored as a local variable — available to any code after gate 6 in `check()`.

### Where to Register a New Gate

A new Rule 20 gate would logically be placed **after gate 6** (since it depends on `is_qa_step` being True) and **after gate 5** (since it needs the deposit file to exist). The natural insertion point is between gate 6 and gate 7 (current line 67), or after gate 8 at the end. Since it is a blocking gate that conditionally fires on QA steps, placing it after gate 6 (which computes `is_qa_step`) is the cleanest position.

---

## Investigation Section 3 — Deposit Path Resolution (Gate 5)

Gate 5 (`_gate_deposit_exists`) resolves deposit paths via the helper `_resolve_deposit_path` at `gates.py:126–142`.

### Resolution Strategy

```python
def _resolve_deposit_path(path, project_path):
    """Check if a deposit path exists, trying multiple path resolution strategies.

    Returns True if the path exists (as a file or directory) at any of:
      1. path as-is (absolute or CWD-relative)
      2. os.path.join(project_path, path) — relative to project root
      3. os.path.join(os.path.dirname(project_path), path) — path includes project dir name
    """
```

Three-tier fallback: absolute → project-relative → parent-relative. Checks both `os.path.isfile()` and `os.path.isdir()`.

### How Gate 5 Finds the Deposit Path

Gate 5 does NOT return a resolved path — it only returns True/False for existence. The actual path comes from two sources:

1. **Agent-declared paths:** Extracted from `parsed["result_text"]` via regex on `### Files Deposited` section. Each `- path` or `- \`path\`` line yields a path.
2. **Plan-required paths:** Extracted from step text via `_extract_plan_required_deposits(step_text)`, which parses the `**Deposits:**` block (Rule 26) or falls back to legacy prose regexes.

### For the New Gate

The new gate needs to **read** the deposit file, not just check existence. It must:
1. Get the deposit path — reuse `_extract_plan_required_deposits()` or parse the `**Deposits:**` block directly (same approach gate 5 uses via `_extract_step_text` + `_extract_plan_required_deposits`).
2. Resolve it to an absolute path — reuse `_resolve_deposit_path()` BUT note this returns bool, not the resolved path. The new gate will need a variant that returns the resolved path string, or it can try each resolution strategy inline (path as-is, project-relative, parent-relative) and open the first one that exists.

**Key function:** `_resolve_deposit_path(path, project_path)` at `gates.py:126–142` — returns bool only. A new `_resolve_deposit_path_to_abs()` helper (or modification to return the path) would be needed.

---

## Investigation Section 4 — `is_qa_step` Computation (Gate 6)

### Location

`_gate_is_qa_step` at `gates.py:220–225`.

### Exact Heuristic

```python
def _gate_is_qa_step(plan_text, step_number):
    pattern = rf"## STEP {step_number}\b[^\n]*"
    match = re.search(pattern, plan_text)
    if match:
        return "qa" in match.group(0).lower()
    return False
```

It checks only the **step header line** (e.g., `## STEP 2 — QA (QA Engineer)`) for the substring `"qa"` (case-insensitive). It does NOT examine the step body.

### How `is_qa_step` Is Consumed

In `check()`, gate 6 returns a bool stored as `is_qa_step` local variable (line 65). This is then passed through in the return dict as `result["is_qa_step"]`. It is NOT passed to any subsequent gate — gates 7 and 8 do not receive it. The new gate would consume it directly from the local variable in `check()`, the same way the return dict does.

---

## Investigation Section 5 — Test Pattern

### Test File Structure

`tests/test_gates.py` — 351 lines, 30 test functions.

### Test Setup Pattern

A helper `_clean_parsed()` returns a baseline parsed dict with all gates passing:

```python
def _clean_parsed():
    return {
        "receipt_status": "Complete",
        "ceo_flags": [],
        "is_error": False,
        "permission_denials": [],
        "result_text": "All done.",
        "cost_usd": 0.05,
        "verdict_requested": {"requested": False, "reason": None},
    }
```

A module-level `PLAN_TEXT` constant provides a minimal two-step plan with DEV and QA steps.

### How Tests Work

- Most tests call `gates.check(parsed, PLAN_TEXT, step_number, project_path)` with a modified `_clean_parsed()`.
- Assertions check `result["passed"]`, `result["failures"]`, and `result["is_qa_step"]`.
- File-system tests use `tmp_path` (pytest fixture) to create real files/dirs.
- Mock-based tests use `@patch("os.path.isfile", return_value=False)` for missing-file scenarios.

### Existing Test Functions by Gate

| Gate | Test Function | Scenario |
|------|--------------|----------|
| All | `test_all_gates_pass_on_clean_parsed` | Baseline — all gates pass |
| 1 (receipt) | `test_receipt_status_blocked` | Status "Blocked" → fail |
| 1 (receipt) | `test_receipt_status_partial` | Status "Partial" → fail |
| 2 (CEO) | `test_ceo_flags_nonempty` | Non-empty CEO flags → fail |
| 3 (errors) | `test_is_error_true` | is_error=True → fail |
| 4 (perms) | `test_permission_denials_nonempty` | String denial → fail |
| 4 (perms) | `test_permission_denials_read_class_only_passes` | Grep/Glob/Read → pass |
| 4 (perms) | `test_permission_denials_write_class_fails` | Edit → fail |
| 4 (perms) | `test_permission_denials_mixed_read_write_fails` | Mixed → fail |
| 4 (perms) | `test_permission_denials_missing_tool_name_fails` | Missing key → fail |
| 4 (perms) | `test_permission_denials_none_tool_name_fails` | None value → fail |
| 4 (perms) | `test_permission_denials_unknown_tool_fails` | Unknown tool → fail |
| 4 (perms) | `test_permission_denials_string_form_fails` | String form → fail |
| 5 (deposit) | `test_deposit_path_missing` | Path doesn't exist → fail |
| 5 (deposit) | `test_no_deposit_section_passes` | No section → pass |
| 5 (deposit) | `test_resolve_deposit_path_directory_as_is` | Dir exists as-is → True |
| 5 (deposit) | `test_resolve_deposit_path_directory_project_relative` | Dir project-relative → True |
| 5 (deposit) | `test_resolve_deposit_path_directory_parent_relative` | Dir parent-relative → True |
| 5 (deposit) | `test_resolve_deposit_path_nonexistent` | Nothing exists → False |
| 5 (deposit) | `test_gate_deposit_exists_directory_in_deposits_block` | Dir in Deposits: block → pass |
| 5 (deposit) | `test_deposit_exists_extracts_path_from_backtick_with_description` | Backtick+desc format |
| 5 (deposit) | `test_deposit_exists_extracts_path_from_backtick_only` | Backtick-only format |
| 5 (deposit) | `test_deposit_exists_extracts_path_from_bare_path_without_backticks` | Bare path format |
| 5 (deposit) | `test_deposit_exists_still_fails_on_genuinely_missing_path_with_new_format` | Missing with new format |
| 6 (QA) | `test_qa_step_detection` | Step 2 with "QA" header → True |
| 7 (audit) | `test_file_change_audit_populates` | Files passed through |
| 8 (scope) | `test_scope_check_passes_when_files_in_plan` | In-plan files → pass |
| 8 (scope) | `test_scope_check_fails_when_file_not_in_plan` | Out-of-plan → fail |
| 8 (scope) | `test_scope_check_allowlist` | Allowlisted names → pass |
| 8 (scope) | `test_scope_check_prefix_allowlist_in_progress` | in-progress- prefix → pass |
| 8 (scope) | `test_scope_check_prefix_allowlist_verdict_pending` | verdict-pending- prefix → pass |
| 8 (scope) | `test_scope_check_prefix_allowlist_halted` | halted- prefix → pass |
| 8 (scope) | `test_scope_check_prefix_allowlist_does_not_suppress_real_violations` | Non-prefixed → fail |
| Misc | `test_verdict_requested_from_parsed_dict` | Verdict requested → True |
| Misc | `test_verdict_requested_defaults_when_key_missing` | Missing key → defaults |
| Header | `test_parse_plan_header_empty` | No frontmatter → {} |
| Header | `test_parse_plan_header_basic` | Frontmatter parsed |
| Header | `test_parse_plan_header_malformed` | Malformed → {} |

---

## Investigation Section 6 — Verdict Request Emission for Gate Failures

### Location

`verdict.py:78–139`, function `post_verdict_request`.

### Gate Failure Section Construction

```python
    if pause_reason == "gate_failure" and gate_result.get("failures"):
        failures_text = ""
        for f in gate_result["failures"]:
            failures_text += f"- **{f['gate']}**: {f['evidence']}\n"
        pause_section = f"## Gate Failures\n\n{failures_text}"
```

### Format

Each failure dict is rendered as `- **{gate}**: {evidence}`. The only keys accessed are `gate` and `evidence` — no other fields are expected.

### Implication for New Gate

The new gate's failure dict only needs `{"gate": "rule_20_self_check", "evidence": "..."}` — the standard two-key shape. No additional fields are required by the verdict emission logic.

---

## Investigation Section 7 — File-Read Helpers

### In `gates.py`

There are **no file-read helpers** in `gates.py`. Gate 5 only checks existence via `os.path.isfile()` / `os.path.isdir()` — it never reads file contents.

### In Other Bellows Modules

- `verdict.py` uses `filepath.read_text()` (pathlib) for reading verdict files.
- `bellows.py` uses standard `open()` / `Path.read_text()` for plan files.
- No shared safe-read utility with encoding error handling exists.

### Implication

The new gate will need to read the QA report file. It should use a simple `open(path, "r", encoding="utf-8")` with a try/except for `FileNotFoundError` and `UnicodeDecodeError`. If the file cannot be read, the gate should fail with evidence indicating the read failure. No existing helper to reuse — but the pattern is straightforward and a dedicated helper is not warranted for a single call site.

---

## Findings — Six Answered Questions

### Question A: Canonical Gate Function Signature, Return Contract, and Failure-Dict Shape

**Signature:** `def _gate_<name>(parsed, failures, ...)` — blocking gates receive at minimum `parsed` (dict) and `failures` (list). Additional parameters (e.g., `project_path`, `plan_text`, `step_number`) are added as needed. Informational gates (6, 7) do not receive `failures`.

**Return contract:** Blocking gates return `None`; they signal failure by appending to the `failures` list. Informational gates return a value (bool for gate 6, list for gate 7).

**Failure dict shape:** `{"gate": "<gate_name>", "evidence": "<human-readable string>"}` — exactly two keys. This is the only shape the verdict emission logic accesses.

### Question B: Where Is a New Gate Registered, and What Inputs Does It Have Access To?

A new gate is registered by adding a call in the `check()` function (gates.py:36–83). The new gate has access to: `parsed`, `plan_text`, `step_number`, `project_path`, `files_changed`, and the `is_qa_step` local variable (computed by gate 6 at line 65). The natural insertion point is **after gate 6** (line 65) — the new gate depends on `is_qa_step` being computed first.

### Question C: How Does the New Gate Access the Deposited QA Report File Path?

The new gate should reuse `_extract_step_text(plan_text, step_number)` to get the step text, then `_extract_plan_required_deposits(step_text)` to get the set of deposit paths. It then needs to resolve to an absolute path using the three-tier strategy from `_resolve_deposit_path`. However, `_resolve_deposit_path` returns bool, not the resolved path. Two options:
1. **Preferred:** Refactor `_resolve_deposit_path` to return the resolved path (or None), and update gate 5 to check `is not None` instead of `is True`. Single change, no logic duplication.
2. **Alternative:** Create `_resolve_deposit_path_abs(path, project_path)` that returns the resolved absolute path or None. Gate 5 continues using the bool version.

The new gate should NOT duplicate path-finding logic — it must call one of these helpers.

### Question D: How Does the New Gate Consume the Existing `is_qa` Boolean?

`is_qa_step` is computed at line 65 of `check()` as a local variable. The new gate should receive it as a parameter: `_gate_rule_20_self_check(is_qa_step, ..., failures)`. If `is_qa_step` is False, the gate returns immediately (no-op). This avoids recomputing the QA heuristic.

### Question E: Test Pattern and Estimated Test Cases

Tests follow the pattern: modify `_clean_parsed()`, call `gates.check()`, assert on `result["passed"]` and `result["failures"]`. File content tests use `tmp_path` to create real files.

**Estimated test cases for the new gate (minimum 5):**
1. **Positive case:** QA step with report containing both banner and PASSED line → gate passes
2. **Banner missing:** QA step with report that has no `Rule 20 — QA Self-Check Results` banner → gate fails
3. **Banner without PASSED:** QA step with banner present but no `PASSED — SELF-CHECK PASSED` line after it → gate fails
4. **Deposit file missing:** QA step where the deposit file path doesn't exist → gate fails
5. **Non-QA step skip:** Non-QA step → gate is a no-op, passes regardless of file content

Optional additional cases: empty file, file with encoding errors, banner at end of file with no content after it.

### Question F: Architectural Constraints and Risks

1. **Gate ordering dependency:** The new gate MUST run after gate 6 (needs `is_qa_step`) and after gate 5 (deposit should exist). If gate 5 already failed because the deposit is missing, the new gate will also fail on file-read — this is acceptable (both failures are reported), but the new gate should handle `FileNotFoundError` gracefully rather than crashing.

2. **No circular imports:** The new gate lives entirely in `gates.py` and uses only stdlib (`os`, `re`, `open`). No risk of circular imports.

3. **`_resolve_deposit_path` returns bool, not path:** This is the main friction point. The new gate needs the actual file path to read it. Refactoring the helper is the cleanest approach.

4. **Multiple deposits:** `_extract_plan_required_deposits` returns a set of paths. QA steps typically have one primary deposit (the QA report). The new gate should check all `.md` deposit paths (or the primary one identified by `extract_primary_deposit` from `verdict.py`). Using `verdict.py`'s `extract_primary_deposit` would introduce a cross-module dependency — acceptable since verdict.py already has this function, but an alternative is to check all deposits for the Rule 20 banner.

5. **No cache invalidation concern:** Gates run once per step execution in a single pass. No state is cached between gate runs within a single `check()` call.

6. **Keep-in-sync comment:** `_extract_step_text` is duplicated in `verdict.py`. Any changes to it must be mirrored. The new gate uses the `gates.py` copy, so no sync issue for the new gate itself.

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Read-only investigation of the gate system in `gates.py`, the test suite in `tests/test_gates.py`, and the verdict emission logic in `verdict.py`. Mapped the complete implementation surface for adding a Rule 20 self-check verification gate: function signatures, dispatcher flow, deposit path resolution, `is_qa_step` computation, test patterns, and verdict emission format. Answered six synthesis questions covering the canonical patterns, registration point, path access, QA boolean consumption, test scope, and architectural risks.

### Files Deposited
- `bellows/knowledge/research/rule-20-gate-addition-surface-findings-2026-05-05.md` — investigation findings with gate pattern table, dispatcher mapping, deposit resolution trace, test inventory, and six synthesis questions answered

### Files Created or Modified (Code)
- None (read-only investigation)

### Decisions Made
- Identified refactoring `_resolve_deposit_path` to return the resolved path (or None) as the preferred approach over creating a parallel helper

### Flags for CEO
- None

### Flags for Next Step
- The `_resolve_deposit_path` bool-vs-path return type is the main implementation friction point — the executable plan should address this explicitly
