# Dev Log — Bash Gate GUARDRAILS Exemption

**Date:** 2026-05-20 | **Agent:** Bellows Developer | **Plan:** executable-bash-gate-guardrails-exemption-2026-05-20, Step 1

---

## Summary

Added a `GUARDRAILS_BASH_EXEMPTION_PATTERN` exemption to `_gate_no_permission_denials` in `gates.py` that filters Bash permission denials whose command text matches the GUARDRAILS-prescribed git index-lock cleanup pattern (`rm -f .git/index.lock ...`). This prevents bellows from converting these denials into `gate_failure`, eliminating the three documented false-positive fires (2026-04-17, 2026-05-06, 2026-05-21). The denial itself still originates from Claude Code's runtime — this change only stops bellows from treating it as blocking.

## Implementation Notes

### Denial payload field name

The Bash denial payload follows the standard Claude Code permission_denials schema:
```python
{"tool_name": "Bash", "tool_use_id": "toolu_*", "tool_input": {"command": "..."}}
```
The command text is at `d.get("tool_input", {}).get("command", "")`. Confirmed via existing test fixtures in `test_gates.py` (lines 84-86 show the same `tool_input` dict structure for other tools) and `parser.py:12` which passes `permission_denials` through from the raw Claude Code JSON output without transformation.

### Regex design

The pattern matches the canonical GUARDRAILS.md line 53 command shape:
- `rm -f .git/index.lock` (simplest form)
- Any combination of the three lock file glob patterns: `.git/index.lock`, `.git/"index "*.lock`, `.git/"index "[0-9]*`
- Optional `2>/dev/null` suffix
- Optional leading semicollon+whitespace (compound command prefix)
- Terminated by `;` or end-of-string

A helper string `_LOCK_GLOB` is used to avoid repeating the three-alternative group.

### Architectural precedent

Follows the same pattern as the existing `READ_CLASS_TOOLS` exemption (line 35): a module-level constant checked inside the `_gate_no_permission_denials` loop, with `continue` to skip non-blocking denials.

## Files Changed

### `gates.py`

**Lines 37-48 (new):** `GUARDRAILS_BASH_EXEMPTION_PATTERN` constant and `_LOCK_GLOB` helper.

Before:
```python
READ_CLASS_TOOLS = {"Grep", "Glob", "Read", "mcp__vexp__run_pipeline"}

def _parse_plan_header(plan_text):
```

After:
```python
READ_CLASS_TOOLS = {"Grep", "Glob", "Read", "mcp__vexp__run_pipeline"}

# Bash commands matching the GUARDRAILS-prescribed git index-lock cleanup are exempt
# from no_permission_denials blocking. The denial originates from Claude Code's runtime,
# not bellows — agents following governance/GUARDRAILS.md Development → Git Operations
# rule 1 should not be penalised. Closes shop_backlog: guardrails-vs-bash-gate-contradiction-git-locks.
_LOCK_GLOB = r'\.git/(?:index\.lock|"index "\*\.lock|"index "\[0-9\]\*)'
GUARDRAILS_BASH_EXEMPTION_PATTERN = re.compile(
    r'(?:^|;\s*)rm\s+-f\s+'
    + _LOCK_GLOB
    + r'(?:\s+' + _LOCK_GLOB + r')*'
    + r'(?:\s+2>/dev/null)?'
    + r'\s*(?:;|$)'
)

def _parse_plan_header(plan_text):
```

**Lines 198-203 (new):** Bash exemption filter inside `_gate_no_permission_denials`.

Before:
```python
            if tool_name in READ_CLASS_TOOLS:
                continue
            blocking.append(d)
```

After:
```python
            if tool_name in READ_CLASS_TOOLS:
                continue
            # Exempt Bash denials matching the GUARDRAILS-prescribed git lock cleanup.
            # Command text is in tool_input.command per Claude Code's denial payload schema.
            if tool_name == "Bash":
                cmd = d.get("tool_input", {}).get("command", "") if isinstance(d.get("tool_input"), dict) else ""
                if GUARDRAILS_BASH_EXEMPTION_PATTERN.search(cmd):
                    continue
            blocking.append(d)
```

### `tests/test_gates.py`

Two new tests added (lines 1146-1177):

1. `test_no_permission_denials_exempts_guardrails_lock_cleanup` — positive: Bash denial with the full canonical GUARDRAILS lock-cleanup command is filtered out, gate passes.
2. `test_no_permission_denials_still_blocks_other_bash_denials` — negative: Bash denial with `rm -rf /tmp/foo` still produces `gate_failure`.

## Test Count Delta

- Before: 91 tests
- After: 93 tests (+2)
- Regressions: 0

## Pytest Output

```
======================== 93 passed, 1 warning in 0.40s =========================
```

Full verbose output confirmed all 93 tests pass. The 1 warning is a pre-existing urllib3/LibreSSL compatibility warning unrelated to this change.

## Known Issues

None.

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Added GUARDRAILS_BASH_EXEMPTION_PATTERN exemption to `_gate_no_permission_denials` in `gates.py`, with two unit tests confirming correct positive and negative behavior. All 93 tests pass with zero regressions.

### Files Deposited
- `knowledge/development/bash-gate-guardrails-exemption-2026-05-20.md` — dev log with implementation summary, before/after snippets, field name discovery, and full pytest output

### Files Created or Modified (Code)
- `gates.py` — added `GUARDRAILS_BASH_EXEMPTION_PATTERN` constant (lines 37-48) and Bash exemption filter in `_gate_no_permission_denials` (lines 198-203)
- `tests/test_gates.py` — added `test_no_permission_denials_exempts_guardrails_lock_cleanup` and `test_no_permission_denials_still_blocks_other_bash_denials`

### Decisions Made
- Used `tool_input.command` as the field path for Bash denial command text, consistent with existing test fixtures and Claude Code's tool parameter schema
- Used `re.search` (not `re.fullmatch`) to handle compound commands where the lock cleanup is part of a larger command string

### Flags for CEO
- None

### Flags for Next Step
- The exemption regex matches the canonical GUARDRAILS.md line 53 pattern and its subsets. If GUARDRAILS.md ever changes the lock-cleanup command shape, the regex will need updating.
