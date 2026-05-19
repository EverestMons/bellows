# Dispatch Mode Validator — Design Note

**Date:** 2026-05-19
**Plan:** `executable-bellows-dispatch-mode-validator-2026-05-19`
**Step:** 1 (SA)

---

## 1. Module Placement

**Decision: New `validators.py` module.**

Justification: `gates.py` runs *after* each step completes (post-execution gates). The dispatch mode validator runs at *claim time* — before the plan is claimed and before the first step is dispatched. These are distinct lifecycle moments:

- **Claim time** (`bellows.py:run_plan()`, lines 351–367): header is parsed, plan is moved to `in-progress-`. The validator fires here.
- **Step gate time** (`gates.check()`, called at `bellows.py:448`): step output is inspected for receipt status, CEO flags, deposit existence, scope check, etc.

Placing claim-time validation in `gates.py` would conflate these two lifecycle moments. A new `validators.py` keeps the separation clean and mirrors the existing module factoring pattern (`gates.py` = post-step, `validators.py` = pre-claim).

**Insertion point for new code:** New file `bellows/validators.py`. No line insertion into an existing module for the validator logic itself — only the call site in `bellows.py` (see Section 7).

---

## 2. Header Field Parser

The validator reads `dispatch_mode` from the dict returned by `gates._parse_plan_header()` (`gates.py:37–103`).

**Bold-Markdown plans:** The existing parser normalizes keys to lowercase with underscores. `**Dispatch Mode:** bellows` becomes key `dispatch_mode` with value `"bellows"`. This is the expected plan format for Bellows-dispatched plans.

**YAML frontmatter plans:** The key in the dict is whatever the YAML author writes. If `dispatch_mode: bellows` is in the frontmatter, it parses directly. If `Dispatch Mode: bellows` is used, the key would be `"Dispatch Mode"` (YAML preserves case and spaces).

**Validator approach:** Look up `header.get("dispatch_mode")` first (covers bold-Markdown and well-formatted YAML). If absent, fall back to `header.get("Dispatch Mode")` (covers YAML with space-separated keys). The validator normalizes the retrieved value to lowercase and strips whitespace before comparison.

```python
def _get_dispatch_mode(header: dict) -> str | None:
    """Extract dispatch_mode from parsed plan header, normalizing key variants."""
    raw = header.get("dispatch_mode") or header.get("Dispatch Mode")
    if raw is None:
        return None
    return str(raw).strip().lower()
```

---

## 3. Check (a) — Mismatch Detection

**Condition:** `dispatch_mode == "manual_bootstrap"` AND plan deposit path is within a Bellows-watched directory.

**Pseudocode:**

```python
def check_dispatch_mismatch(header: dict, plan_path: str, config: dict) -> dict | None:
    """Check (a): manual_bootstrap plan in a Bellows-watched directory."""
    mode = _get_dispatch_mode(header)
    if mode != "manual_bootstrap":
        return None  # Not a mismatch — either bellows mode or missing (handled by check_c)

    plan_dir = str(Path(plan_path).parent)
    watched = config.get("watched_projects", [])
    # Normalize paths for comparison
    plan_dir_resolved = str(Path(plan_dir).resolve())
    for wp in watched:
        wp_resolved = str(Path(wp).resolve())
        if plan_dir_resolved == wp_resolved:
            return {
                "check": "dispatch_mismatch",
                "severity": "warn",
                "message": f"Plan declares dispatch_mode=manual_bootstrap but is deposited in Bellows-watched directory {wp}"
            }
    return None  # Not in a watched directory — no mismatch
```

**Config access:** Reads `config["watched_projects"]` — the same list used by `Bellows.__init__()` and `PlanHandler._handle()`. The config dict is already available in `run_plan()` as the `config` parameter.

**Path matching:** Compares the resolved absolute path of the plan's parent directory against each resolved watched-project path. Uses `Path.resolve()` to handle symlinks and relative components.

---

## 4. Check (b) — STOP-Prose Detection

**Condition:** `dispatch_mode == "bellows"` AND step bodies contain any of the three STOP-prose patterns.

**Regexes (case-insensitive):**
1. `STOP\.`
2. `wait for confirmation`
3. `do not proceed`

**Scope boundaries:**

- **Step bodies only:** Text between `## STEP N` headers. Everything before the first `## STEP` header is excluded (plan header, CEO Context, Execution Map, etc.). The final step body extends from its `## STEP N` header to end-of-file.
- **Excluded inline contexts within step bodies:**
  - Fenced code blocks (`` ``` ... ``` ``)
  - Backtick-wrapped inline code (`` `...` ``)
  - `**Deposits:**` blocks (from `**Deposits:**` marker through its bullet list)

**Parse approach — line-based scan with state tracking:**

```python
STOP_PROSE_PATTERNS = [
    re.compile(r"STOP\.", re.IGNORECASE),
    re.compile(r"wait for confirmation", re.IGNORECASE),
    re.compile(r"do not proceed", re.IGNORECASE),
]

def check_stop_prose(header: dict, plan_text: str) -> list[dict]:
    """Check (b): STOP-prose patterns in step bodies under bellows dispatch mode."""
    mode = _get_dispatch_mode(header)
    if mode != "bellows":
        return []  # Only check bellows-mode plans

    warnings = []
    in_step_body = False
    in_fenced_block = False
    in_deposits_block = False

    for line in plan_text.splitlines():
        # Detect step header boundaries
        if re.match(r"^## STEP \d+", line, re.IGNORECASE):
            in_step_body = True
            in_fenced_block = False
            in_deposits_block = False
            continue

        if not in_step_body:
            continue

        # Track fenced code blocks
        if line.strip().startswith("```"):
            in_fenced_block = not in_fenced_block
            continue
        if in_fenced_block:
            continue

        # Track **Deposits:** blocks — from marker through consecutive bullet lines
        if re.match(r'\s*\*\*Deposits:\*\*', line):
            in_deposits_block = True
            continue
        if in_deposits_block:
            stripped = line.strip()
            if stripped.startswith("- ") or stripped == "":
                continue  # Still in deposits block
            else:
                in_deposits_block = False
                # Fall through to scan this line

        # Strip inline backtick content before scanning
        scan_line = re.sub(r'`[^`]*`', '', line)

        for pattern in STOP_PROSE_PATTERNS:
            if pattern.search(scan_line):
                warnings.append({
                    "check": "stop_prose",
                    "severity": "warn",
                    "message": f"STOP-prose detected in step body: '{pattern.pattern}' matched in line: {line.strip()[:80]}"
                })
                break  # One warning per line is sufficient

    return warnings
```

**Rationale for exclusions:** A plan that ships the validator necessarily references the regex patterns by name (in CEO Context, in code blocks, in deposits blocks). The scope must distinguish *naming a pattern* ("`STOP\.` is one of the three regexes") from *using the pattern as instruction* ("the agent should STOP. and wait for confirmation"). The header/preamble exclusion catches the former by position; the inline-code and fenced-block exclusions catch it by formatting convention.

---

## 5. Check (c) — Missing Field Detection

**Condition:** `dispatch_mode` key is not present in the parsed header at all.

**Pseudocode:**

```python
def check_missing_dispatch_mode(header: dict) -> dict | None:
    """Check (c): dispatch_mode field entirely absent from plan header."""
    mode = _get_dispatch_mode(header)
    if mode is None:
        return {
            "check": "missing_dispatch_mode",
            "severity": "reject",
            "message": "Plan header missing **Dispatch Mode:** field. Per Rule 35, this field is required. Plan will not be claimed."
        }
    # Also reject if value is present but not in the valid set
    if mode not in ("bellows", "manual_bootstrap"):
        return {
            "check": "missing_dispatch_mode",
            "severity": "reject",
            "message": f"Plan header has invalid dispatch_mode='{mode}'. Must be 'bellows' or 'manual_bootstrap'. Plan will not be claimed."
        }
    return None
```

**Absence conditions:**
- Key not present in header dict at all (`_get_dispatch_mode()` returns `None`) → **reject**
- Key present with empty string value (after strip, effectively absent) → **reject** (caught by `_get_dispatch_mode` returning empty string, which is not in the valid set)
- Key present with value not in `["bellows", "manual_bootstrap"]` → **reject** (invalid value is treated the same as missing — it's an authoring error)

---

## 6. Warn vs. Reject Mechanics

### Warn cases (a, b)

**Log format:**

```
HH:MM:SS [WARN] [slug] dispatch-validator: <check_name> — <message>
```

Example:
```
14:32:07 [WARN] [dispatch-mode-val] dispatch-validator: dispatch_mismatch — Plan declares dispatch_mode=manual_bootstrap but is deposited in Bellows-watched directory /Users/.../knowledge/decisions
```

**Pushover notification:** No. Warn-level validator findings are logged only. Rationale: these warns surface information for the CEO at verdict-review time via the log trail. Pushing a Pushover notification for every warn would be noisy — the plan still proceeds, and the verdict-request notification (when the step completes) already triggers CEO attention. If warn-level push is desired later, it can be added without structural change.

**Dedup:** Not needed at the validator level. The validator runs once per plan at claim time (not on every poll cycle). The claim-time code path in `run_plan()` executes exactly once per plan invocation — the plan is moved to `in-progress-` immediately after validation, so subsequent poll cycles skip it via `is_runnable_plan()` returning False for `in-progress-` prefixed files.

**Non-blocking:** Warn checks return their findings but do NOT prevent claim. The plan proceeds normally. Warnings are informational annotations in the log.

### Reject case (c)

**Mechanism:** The validator returns a reject result. The caller in `bellows.py:run_plan()` moves the plan to `halted-` prefix (consistent with existing halt patterns at `bellows.py:1190`) and logs the rejection.

**Existing halt pattern reference:** `bellows.py:1190–1197` — when a verdict returns `stop`, the plan is moved to `halted-{original_name}`. The reject case follows this same pattern but triggers earlier (at claim time, before any step runs).

**Implementation in `bellows.py`:**

```python
# After header parse, before claim
validation_result = validators.validate_at_claim(header, plan_path, config, metadata_text)
if validation_result["rejected"]:
    # Move to halted-
    halted_path = os.path.join(plan_dir, f"halted-{base_filename}")
    shutil.move(plan_path, halted_path)
    _log("ERROR", f"plan rejected by dispatch-mode validator: {validation_result['reject_reason']}", slug=slug_for(plan_name))
    notifier.push(app_key, user_key, "Bellows — Plan Rejected", f"Plan: {plan_name}\nReason: {validation_result['reject_reason']}")
    return
for w in validation_result["warnings"]:
    _log("WARN", f"dispatch-validator: {w['check']} — {w['message']}", slug=slug_for(plan_name))
```

**Pushover on reject:** Yes. A rejected plan requires CEO attention (the author must fix the plan header and re-deposit). This is an urgent event analogous to `notify_failure`.

---

## 7. Integration Point

**Location:** `bellows.py:run_plan()`, between the header parse + defensive defaults block and the claim (move-to-in-progress) block.

**Exact insertion point:** After line 358 (the defensive header defaults warning log) and before line 363 (the `if not plan_filename.startswith("in-progress-"):` claim block).

**Current code at insertion site (`bellows.py:351–367`):**

```python
        header = gates._parse_plan_header(metadata_text)          # line 351
        # Defensive default ...                                    # lines 352-358
        prev_len = len(header)
        _apply_defensive_header_defaults(header, total_steps)
        if "pause_for_verdict" in header and len(header) > prev_len:
            _log("WARN", ...)
        model = header.get("Model", ...)                          # line 359

        # >>> VALIDATOR INSERTION POINT <<<                        # after line 359

        # Claim the plan atomically before calling the runner.     # line 362
        if not plan_filename.startswith("in-progress-"):           # line 363
            shutil.move(plan_path, inprogress_path)                # line 364
```

**Call ordering:** The validator runs:
1. **After** `_parse_plan_header()` — needs the parsed header dict
2. **After** `_apply_defensive_header_defaults()` — needs finalized header
3. **After** model extraction (line 359) — no dependency, just sequencing
4. **Before** the claim move (line 363) — a rejected plan must NOT be claimed

**Import:** Add `import validators` to the import block at `bellows.py:114–119`.

---

## 8. Test Specification

Test file: `tests/test_validators.py`

All tests import `validators` and use helper fixtures for plan text construction.

### Test 1: `test_clean_plan_all_checks_pass`
- **Setup:** Plan text with `**Dispatch Mode:** bellows`, step bodies containing no STOP-prose, plan path inside a watched directory from config.
- **Function under test:** `validators.validate_at_claim(header, plan_path, config, plan_text)`
- **Assertion:** `result["rejected"]` is `False`, `result["warnings"]` is empty list.

### Test 2: `test_reject_missing_dispatch_mode`
- **Setup:** Plan text with no `**Dispatch Mode:**` field in header.
- **Function under test:** `validators.validate_at_claim(header, plan_path, config, plan_text)`
- **Assertion:** `result["rejected"]` is `True`, `result["reject_reason"]` contains "missing".

### Test 3: `test_reject_invalid_dispatch_mode_value`
- **Setup:** Plan text with `**Dispatch Mode:** unknown_value`.
- **Function under test:** `validators.validate_at_claim(header, plan_path, config, plan_text)`
- **Assertion:** `result["rejected"]` is `True`, `result["reject_reason"]` contains "invalid".

### Test 4: `test_warn_mismatch_manual_bootstrap_in_watched_dir`
- **Setup:** Plan text with `**Dispatch Mode:** manual_bootstrap`, plan path inside a watched directory.
- **Function under test:** `validators.validate_at_claim(header, plan_path, config, plan_text)`
- **Assertion:** `result["rejected"]` is `False`, `result["warnings"]` has one entry with `check == "dispatch_mismatch"`.

### Test 5: `test_no_warn_manual_bootstrap_not_in_watched_dir`
- **Setup:** Plan text with `**Dispatch Mode:** manual_bootstrap`, plan path NOT in any watched directory.
- **Function under test:** `validators.validate_at_claim(header, plan_path, config, plan_text)`
- **Assertion:** `result["rejected"]` is `False`, `result["warnings"]` is empty list.

### Test 6: `test_warn_stop_prose_in_bellows_mode`
- **Setup:** Plan text with `**Dispatch Mode:** bellows`, step body containing `do not proceed` as prose text.
- **Function under test:** `validators.validate_at_claim(header, plan_path, config, plan_text)`
- **Assertion:** `result["rejected"]` is `False`, `result["warnings"]` has at least one entry with `check == "stop_prose"`.

### Test 7: `test_no_warn_stop_prose_in_manual_bootstrap_mode`
- **Setup:** Plan text with `**Dispatch Mode:** manual_bootstrap`, step body containing `do not proceed`.
- **Function under test:** `validators.validate_at_claim(header, plan_path, config, plan_text)`
- **Assertion:** `result["warnings"]` has no entries with `check == "stop_prose"` (STOP-prose check only applies to bellows mode).

### Test 8: `test_stop_prose_in_fenced_code_block_excluded`
- **Setup:** Plan text with `**Dispatch Mode:** bellows`, step body containing `do not proceed` inside a fenced code block.
- **Function under test:** `validators.validate_at_claim(header, plan_path, config, plan_text)`
- **Assertion:** `result["warnings"]` is empty (fenced code block content excluded from scan).

### Test 9: `test_stop_prose_in_inline_code_excluded`
- **Setup:** Plan text with `**Dispatch Mode:** bellows`, step body containing `` `do not proceed` `` as inline code.
- **Function under test:** `validators.validate_at_claim(header, plan_path, config, plan_text)`
- **Assertion:** `result["warnings"]` is empty (inline code content excluded from scan).

### Test 10: `test_stop_prose_in_header_excluded`
- **Setup:** Plan text with `**Dispatch Mode:** bellows`, STOP-prose text appearing in the CEO Context section (before first `## STEP`), clean step bodies.
- **Function under test:** `validators.validate_at_claim(header, plan_path, config, plan_text)`
- **Assertion:** `result["warnings"]` is empty (header/preamble excluded from scan).

### Test 11: `test_stop_prose_in_deposits_block_excluded`
- **Setup:** Plan text with `**Dispatch Mode:** bellows`, step body with STOP-prose text inside a `**Deposits:**` bullet list.
- **Function under test:** `validators.validate_at_claim(header, plan_path, config, plan_text)`
- **Assertion:** `result["warnings"]` is empty (deposits block excluded from scan).

### Test 12: `test_multiple_stop_prose_patterns_detected`
- **Setup:** Plan text with `**Dispatch Mode:** bellows`, step body containing both `STOP.` and `wait for confirmation` on separate lines.
- **Function under test:** `validators.validate_at_claim(header, plan_path, config, plan_text)`
- **Assertion:** `result["warnings"]` has at least 2 entries with `check == "stop_prose"`.

### Test 13: `test_reject_empty_dispatch_mode_value`
- **Setup:** Plan text with `**Dispatch Mode:**` followed by no value (empty string).
- **Function under test:** `validators.validate_at_claim(header, plan_path, config, plan_text)`
- **Assertion:** `result["rejected"]` is `True` (empty value treated as absent/invalid).

---

## Public API Summary

`validators.py` exposes one top-level function:

```python
def validate_at_claim(header: dict, plan_path: str, config: dict, plan_text: str) -> dict:
    """Run all claim-time validators on a plan.

    Args:
        header: Parsed plan header dict (from gates._parse_plan_header())
        plan_path: Absolute path to the plan file
        config: Bellows config dict (with watched_projects list)
        plan_text: Full plan text (for STOP-prose body scan)

    Returns:
        {
            "rejected": bool,         # True if any check returned reject
            "reject_reason": str,     # Human-readable reason (empty if not rejected)
            "warnings": [             # List of warn-level findings
                {"check": str, "severity": "warn", "message": str},
                ...
            ]
        }
    """
```

Internal functions: `_get_dispatch_mode()`, `check_missing_dispatch_mode()`, `check_dispatch_mismatch()`, `check_stop_prose()`. Each returns its finding or None/empty list.
