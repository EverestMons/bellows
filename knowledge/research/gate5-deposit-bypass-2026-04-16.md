# Gate 5 Deposit Bypass — Investigation Findings
**Date:** 2026-04-16 | **Type:** Research | **Source:** diagnostic-bellows-gate5-deposit-bypass-2026-04-16.md

---

## Summary Table

| Question | Finding | Root Cause Implication |
|----------|---------|------------------------|
| Q1 — Gate 5 trigger condition | If `### Files Deposited` is absent, Gate 5 returns immediately with no failure recorded | Gate 5 cannot detect deposits the plan requires but the agent silently omits |
| Q2 — What is `result_text`? | `raw.get("result", "")` from `claude -p` JSON — the agent's final response text | Empty or structurally wrong responses bypass the regex entirely |
| Q3 — Path resolution | `os.path.isfile(path)` runs in Bellows' CWD, not `project_path`; `project_path` is not forwarded to `_gate_deposit_exists` | Cross-project paths like `invoice-pulse/knowledge/...` would fail even if agent listed them correctly |
| Q4 — Reproduce with today's data | All three plans: no `### Files Deposited` section in result_text → Gate 5 silently passed; billto-config timed out, Gate 1 failed | Primary bypass is the missing section, not path resolution |
| Q5 — Agent output inspection | Agents used informal narrative format ("Step 1 complete. Here's what was changed:…") with no Output Receipt, no `### Files Deposited` heading | Gate 5 is rendered inert when agents don't use the canonical Output Receipt format |

---

## Q1 — Gate 5 Trigger Condition

**File:** `gates.py:110-122` (`_gate_deposit_exists`)

Gate 5 reads `parsed["result_text"]` and applies:

```python
match = re.search(r"### Files Deposited\s*\n(.*?)(?:\n###|\Z)", result_text, re.DOTALL)
if not match:
    return  # No Files Deposited section — pass
```

**Exact early-return logic (gates.py:113-114):**
```python
if not match:
    return  # No Files Deposited section — pass
```

If the agent's output does not contain a `### Files Deposited` section, the gate returns with zero failures — a silent pass. The gate only checks paths that the agent explicitly declares; it has no knowledge of what the plan *required* to be deposited.

When a `### Files Deposited` section IS present, Gate 5 parses each `- path` bullet, strips backtick quoting, and calls `os.path.isfile(path)` on each. Any missing file appends a failure.

---

## Q2 — What is `parsed["result_text"]`?

**File:** `parser.py:10`

```python
result_text = raw.get("result", "")
```

`result_text` is the `"result"` field from the `claude -p` JSON output — the agent's final response text. It is:
- The full text the agent produced (Bellows does not truncate it)
- Populated only when `claude -p` exits normally with a JSON payload
- **Empty (`""`)** in three failure cases: timeout (`runner.py:59`), generic exception (`runner.py:88`), and JSON decode error (`runner.py:117`)

For the three plans investigated, the two executable plans produced non-empty `result_text` containing narrative step summaries but no `### Files Deposited` heading. The billto-config plan timed out, so `result_text = ""` from the pre-built timeout return.

---

## Q3 — Path Resolution

**File:** `gates.py:121`, `bellows.py:200/257`, `runner.py:13`

`_gate_deposit_exists` calls `os.path.isfile(path)` with the path exactly as listed in the agent's output (e.g. `invoice-pulse/knowledge/development/file-first-accessorials-fak-2026-04-16.md`).

`gates.check()` receives `project_path` as its fourth argument (`bellows.py:200`):
```python
gate_result = gates.check(parsed, plan_text, current_step, project_path, files_changed=files_changed)
```

But `_gate_deposit_exists` is called as:
```python
_gate_deposit_exists(parsed, failures)
```

`project_path` is **not forwarded** to `_gate_deposit_exists`. `os.path.isfile()` therefore runs relative to Bellows' own CWD (the directory from which `python bellows.py` was launched, typically `/Users/marklehn/Desktop/GitHub/bellows/`).

For a path like `invoice-pulse/knowledge/development/file-first-accessorials-fak-2026-04-16.md`:
- **Checked:** `/Users/marklehn/Desktop/GitHub/bellows/invoice-pulse/knowledge/development/...`
- **Actual location:** `/Users/marklehn/Desktop/GitHub/invoice-pulse/knowledge/development/...`

These are different paths. This is a **secondary bug**: even if agents used the canonical `### Files Deposited` format with project-relative paths, Gate 5's `os.path.isfile()` would always return `False` for cross-project deposits (producing false positives), or would need agents to write absolute paths to work correctly.

---

## Q4 — Reproduce with Today's Data

### Log-to-Plan Mapping

| Log file | Plan | DB run ID | DB status |
|----------|------|-----------|-----------|
| `20260416-161548-step.json` | `executable-file-first-accessorials-fak` | 175 (Complete) + 176 (VerdictPending) | Complete |
| `20260416-161704-step.json` | `executable-file-first-fuel-brackets` | 179 (Complete) + 180 (VerdictPending) | Complete |
| `20260416-161751-step.json` | `diagnostic-billto-config-extraction` | 181 (Blocked) + 182 (VerdictPending) | **Blocked (timeout)** |

### file-first-accessorials-fak (run 175)

- **receipt_status:** `Complete` (stop_reason = `end_turn`)
- **`### Files Deposited` found:** No
- **Gate 5 paths checked:** None (early return)
- **Gate 5 failures:** None (silent pass)
- **result_text contains:** Narrative — "Step 1 complete. Here's what was changed: **Templates** — added file-upload card…"
- **DB status:** Complete → VerdictPending

### file-first-fuel-brackets (run 179)

- **receipt_status:** `Complete` (stop_reason = `end_turn`)
- **`### Files Deposited` found:** No
- **Gate 5 paths checked:** None (early return)
- **Gate 5 failures:** None (silent pass)
- **result_text contains:** Narrative — "Step 1 complete. Here's what was done: **Template change (`contract_fuel.html`):**…"
- **DB status:** Complete → VerdictPending

### diagnostic-billto-config-extraction (run 181)

- **receipt_status:** `Blocked` (timeout — elapsed exactly 600s, matching default `timeout=600` in `runner.py:31`)
- **log file keys:** `['success', 'error', 'elapsed_seconds', 'stderr_partial']` — matches the `TimeoutExpired` branch in `runner.py:54-73`
- **result_text:** `""` (pre-built timeout return, `runner.py:70`)
- **Gate 1 failure:** `receipt_status != Complete` → `passed = False`
- **Gate 5:** Early return (empty string → no `### Files Deposited`) — moot because Gate 1 already failed
- **DB status:** Blocked → VerdictPending
- **Note:** The diagnostic states all three completed with `passed=True`. This is **incorrect for billto-config** — it was blocked by timeout, Gate 1 fired.

---

## Q5 — Agent Output Inspection

### file-first-accessorials-fak (run 175) — full result_text

```
Step 1 complete. Here's what was changed:

**Templates** — added file-upload card (primary path) + "Or paste here" divider above the
existing `copilot_inline.html` include (now the paste fallback):
- `web/templates/contract_accessorials.html` — `section_type=accessorials`
- `web/templates/contract_fak.html` — `section_type=fak`

**Prompts** (`copilot_prompts.py`) — replaced `OUTPUT FORMAT: CSV (comma-separated)...` with
the hybrid block (downloadable file preferred, inline paste fallback) for:
- `"accessorials"` key → filename `accessorials_{carrier_code}_{YYYY-MM-DD}.csv`
- `"fak"` key → filename `fak_{carrier_code}_{YYYY-MM-DD}.csv`

No backend changes. Templates only + string constants, so no tests to run per CLAUDE.md rules.

Ready for your "ok" to proceed to Step 2 (QA).
```

**Output Receipt present:** No
**`### Files Deposited` section:** Absent
**Format:** Informal markdown narrative. No structured Output Receipt.

### file-first-fuel-brackets (run 179) — full result_text

```
Step 1 complete. Here's what was done:

**Template change (`contract_fuel.html`):** Inside the collapsed "Bracket-Only Import"
`<details>` section, replaced the paste-only `copilot_inline.html` with the file-first
pattern...

All targeted tests pass. Ready for your confirmation to proceed to Step 2 (QA).
```

**Output Receipt present:** No
**`### Files Deposited` section:** Absent
**Format:** Informal markdown narrative. No structured Output Receipt.

### diagnostic-billto-config-extraction (run 181)

- Result_text: `""` — process timed out before producing output

---

## Root Cause Analysis

### Primary Root Cause: Gate 5 is opt-in, not opt-out

Gate 5 only validates deposits that the agent *explicitly declares* in a `### Files Deposited` section. If the agent omits this section entirely — whether by using an informal narrative format or by not writing an Output Receipt at all — Gate 5 returns with zero failures. There is no mechanism for Gate 5 to compare the plan's required deposits against what was actually produced.

The gate design assumes agents will always include a `### Files Deposited` section when deposits are required. Both executable plans used informal narrative summaries with no Output Receipt structure, so the gate was entirely bypassed.

### Secondary Root Cause: Path resolution is wrong for cross-project deposits

`_gate_deposit_exists` does not receive `project_path`. `os.path.isfile()` resolves relative to Bellows CWD, not the watched project directory. A path like `invoice-pulse/knowledge/development/...` would never resolve correctly from the Bellows root. This bug is masked by the primary issue (no `### Files Deposited` section at all) but would surface as false positives if the primary issue were fixed.

### Billto-config: Different failure mode

Billto-config did not have a Gate 5 bypass — it timed out at 600s and was correctly flagged Blocked by Gate 1. The diagnostic's claim that all three plans had `passed=True` is incorrect for this plan.
