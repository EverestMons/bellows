# Verdict-Request Enrichment Surface Mapping — Diagnostic Findings

**Date:** 2026-05-27 | **Type:** Diagnostic findings | **Plan:** diagnostic-verdict-enrichment-surface-2026-05-27

---

## Prior Work (cited per Rule 27)

- **Roadmap:** `/Users/marklehn/Developer/GitHub/roadmap-bellows-verdict-enrichment-2026-05-27.md` — design intent: re-surface all 8 gates in a unified Verification Results table, add `_gate_rule_22_verification`, add `rule_22_check_failed` Pause Reason Code, add Planner-Only Checks Remaining section. LOC estimate ~244 across one DEV + one QA step.
- **deposit-exists-path-form-normalization-2026-05-27.md:** Current `_gate_deposit_exists` and `_resolve_deposit_path` shape, `_normalize_deposit_path` helper (Component A fix now shipped). Confirms gates run pre-teardown (line 485 before line 514 in bellows.py). Confirms canonical path form for plan authoring is project-prefixed relative (`bellows/...`).

---

## Q1 — `post_verdict_request` Current Shape

### (a) Full function signature

```python
def post_verdict_request(
    plan_path,
    project_path,
    step_number,
    log_path,
    gate_result,
    pause_reason="auto_close_disabled",
    planner_py_decision=None,
    total_steps=None,
    step_text="",
    intermediate_decisions=None,
):
```
(verdict.py:95)

No type annotations on parameters. `total_steps=None` raises `ValueError` at runtime if not provided (line 114).

### (b) Data inputs

| Parameter | Source | Description |
|---|---|---|
| `plan_path` | `bellows.py` caller | Full filesystem path to the plan file |
| `project_path` | `bellows.py` caller | Project root directory (parent of `knowledge/decisions/`) |
| `step_number` | `bellows.py` caller | Current step integer |
| `log_path` | `bellows.py` caller | Path to logs directory (`str(BELLOWS_ROOT / "logs")`) |
| `gate_result` | `gates.check()` return value | Dict: `{"passed": bool, "failures": list, "is_qa_step": bool, "files_changed": list, "plan_header": dict, "verdict_requested": dict}` |
| `pause_reason` | Assigned in bellows.py pause-reason logic | String code from set: `{gate_failure, qa_checkpoint, agent_verdict_request, header_pause, auto_close_disabled}` |
| `planner_py_decision` | Legacy; always `None` at current call sites | JSON-serializable decision object |
| `total_steps` | `extract_total_steps(metadata_text)` in bellows.py | Integer count of `## STEP N` headers |
| `step_text` | `plan_text` variable in bellows.py | Full plan text (NOT just current step — step extraction happens inside the function at line 132) |
| `intermediate_decisions` | `parsed.get("intermediate_decisions", [])` | List of dicts from `decisions.extract_decision_blocks()`: `{"event_idx": int, "text": str, "matched_phrases": list[str]}` |

### (c) Markdown sections written, in order

| # | Section | Source data | Lines |
|---|---|---|---|
| 1 | `# Verdict Request` + metadata fields | `plan_path`, `project_path`, `step_number`, `log_path`, `datetime.now()`, `pause_reason` → label lookup, `pause_reason` code, `extract_primary_deposit(current_step_text)`, `gate_result["passed"]`, `total_steps` | 134–145 |
| 2a | `## Gate Failures` (when `pause_reason == "gate_failure"` AND `gate_result["failures"]`) | `gate_result["failures"]` — iterates `[{"gate": str, "evidence": str}]` | 116–120 |
| 2b | `## Pause Reason` (all other cases) | Static description from `_pause_descriptions` dict, keyed by `pause_reason` | 122–129 |
| 3 | `## Files Changed` | `gate_result["files_changed"]` — list of file paths | 147–150 |
| 4 | `## Intermediate Decisions Detected` (conditional: only when `intermediate_decisions` is truthy) | `intermediate_decisions` list of dicts | 152–157 |
| 5 | `## Planner.py Decision (legacy)` (conditional: only when `planner_py_decision` is truthy) | `planner_py_decision` JSON-serialized | 159–160 |

### (d) File path and naming

Written to: `verdicts/pending/verdict-request-{slug}-step-{step_number}.md` (lines 97–102)

Slug derived by `slug_from_path(plan_path)` which strips `in-progress-`, `verdict-pending-`, `executable-`, `diagnostic-` prefixes and `.md` extension (lines 82–92).

### (e) Helper functions called

| Helper | Line | Purpose |
|---|---|---|
| `slug_from_path(plan_path)` | 100 | Derive filename slug |
| `_extract_step_text_from_plan(step_text, step_number)` | 132 | Scope deposit extraction to current step |
| `extract_primary_deposit(current_step_text)` | 143 | Extract primary deposit path for metadata field |
| `datetime.now().isoformat()` | 140 | Timestamp |

---

## Q2 — `bellows.py` Call Sites for `post_verdict_request`

### Call site 1: Worktree creation failure (line 439–440)

**Trigger:** `WorktreeCreationError` caught at line 435, before any agent execution.

**Parameters passed:**
```python
verdict.post_verdict_request(
    plan_path, project_path, 1, log_path, gate_result,
    pause_reason="gate_failure", total_steps=total_steps, step_text=plan_text
)
```

**NOT passed:** `intermediate_decisions` (no `parsed` exists — agent never ran), `planner_py_decision`.

**Data in scope not passed:** `header`, `model`, `plan_slug`. No `parsed` dict exists at this point.

### Call site 2: Mid-plan pause (line 518)

**Trigger:** Inside the `while not is_final_step()` loop (line 497). Fires when any of: gate failure (line 499), QA checkpoint (line 500), agent verdict request (line 501), or header-says-pause (line 502).

**Parameters passed:**
```python
verdict.post_verdict_request(
    plan_path, project_path, current_step, log_path, gate_result,
    pause_reason=_pause_reason, total_steps=total_steps,
    step_text=plan_text,
    intermediate_decisions=parsed.get("intermediate_decisions", [])
)
```

**Pause reason assignment (lines 504–511):**
- `gate_failure` — gate_result not passed
- `qa_checkpoint` — is_qa_step
- `agent_verdict_request` — agent deposited a verdict-request file
- `header_pause` — plan header's `pause_for_verdict` matches current step

**Data in scope NOT passed:** full `parsed` dict (has `receipt_status`, `cost_usd`, `session_id`, `result_text`, `permission_denials`, `ceo_flags`, etc.), `header` dict, `model`, `wt_path`, `plan_slug`, `pre_diff`/`post_diff`, `files_changed` (though available inside `gate_result`).

### Call site 3: Final-step pause (line 606)

**Trigger:** After the while loop exits (final step completed), lines 584–588 check the same conditions as call site 2 plus `not effective_auto_close`.

**Parameters passed:** Same shape as call site 2.

**Pause reason assignment (lines 590–599):** Same as call site 2 plus `auto_close_disabled` as the final fallback.

### Call site 4: Worktree teardown failure during auto-close (lines 635–636)

**Trigger:** Auto-close path (line 621–625 conditions all met), but `_teardown_worktree` raises `WorktreeTeardownError` at line 629.

**Parameters passed:**
```python
verdict.post_verdict_request(
    plan_path, project_path, current_step, log_path, gate_result,
    pause_reason="gate_failure", total_steps=total_steps,
    step_text=plan_text,
    intermediate_decisions=parsed.get("intermediate_decisions", [])
)
```

### Key finding for the roadmap

**The full `gate_result` dict is already passed at all 4 call sites.** The proposed Verification Results table can be built entirely from `gate_result` without changing the `post_verdict_request` call signature. The `gate_result` contains `failures` (list of gate/evidence dicts), `is_qa_step`, `files_changed`, `plan_header`, and `verdict_requested`.

However, `gate_result` only contains **failure** information — it has no per-gate success data. This is the core finding for Q4.

---

## Q3 — "Intermediate Decisions Detected" Data Flow

### (a) Data shape at source

**Source function:** `decisions.py::extract_decision_blocks` (lines 53–116)

**Input:** `raw_output` (NDJSON string or pre-parsed list of event dicts), `phrases` (lowercased phrase list from `decisions.load_phrases()` which reads `INTERMEDIATE_DECISION_PHRASES.md`).

**Returns:** `list[dict]`, each dict:
```python
{
    "event_idx": int,          # index in the NDJSON event stream
    "text": str,               # assistant text block, truncated to 500 chars
    "matched_phrases": list[str]  # lowercased phrases that matched
}
```

### (b) Call chain from extraction to verdict-write

| Step | Module | Line | Operation |
|---|---|---|---|
| 1 | `runner.py` | 273 | `intermediate_decisions = decisions.extract_decision_blocks(raw_output, phrases)` |
| 2 | `runner.py` | 284 | `parsed["intermediate_decisions"] = intermediate_decisions` |
| 3 | `bellows.py` | 518, 606, 636 | `intermediate_decisions=parsed.get("intermediate_decisions", [])` passed to `post_verdict_request` |
| 4 | `verdict.py` | 152–157 | Rendered as `## Intermediate Decisions Detected` section |

Note: Call site 1 (worktree creation failure, line 439) does NOT pass `intermediate_decisions` because no `parsed` dict exists — the agent never ran.

### (c) Composability into Verification Results table row

**Yes, it composes cleanly.** The row needs:

| Check | Result | Detail |
|---|---|---|
| `intermediate_decisions` | PASS | `0 phrase-matched blocks` |
| `intermediate_decisions` | INFORMATIONAL | `3 phrase-matched blocks` |

The row status is determined by `len(intermediate_decisions)`:
- `0` → PASS (no decisions detected)
- `> 0` → INFORMATIONAL (count > 0 is not a gate failure, but the Planner sees it inline)

The existing detailed block listing (event index, text, matched phrases) can either:
1. Move to a detail column in the table (truncated)
2. Remain as a separate section below the table for cases where count > 0
3. Be linked in the detail column: "3 phrase-matched blocks — see details below"

**No data reshaping required.** The existing `list[dict]` structure maps directly to count (length) and detail (block text). The only question is presentation, which is a verdict-writer formatting choice.

---

## Q4 — Per-Gate Return Shape Audit

### Per-gate analysis

| # | Gate function | Signature | Failure shape | Success behavior |
|---|---|---|---|---|
| 1 | `_gate_receipt_status` (line 170) | `(parsed, failures)` | `{"gate": "receipt_status", "evidence": status}` | Silent — no append, no return |
| 2 | `_gate_ceo_flags` (line 176) | `(parsed, failures)` | `{"gate": "ceo_flags", "evidence": "; ".join(flags)}` | Silent |
| 3 | `_gate_no_errors` (line 182) | `(parsed, failures)` | `{"gate": "no_errors", "evidence": parsed.get("error", "unknown error")}` | Silent |
| 4 | `_gate_no_permission_denials` (line 190) | `(parsed, failures)` | `{"gate": "no_permission_denials", "evidence": f"{len(blocking)} blocking denial(s): {first}"}` | Silent |
| 5 | `_gate_deposit_exists` (line 280) | `(parsed, failures, project_path, plan_text=None, step_number=None, wt_path=None, plan_header=None)` | Multiple `{"gate": "deposit_exists", "evidence": ...}` variants (missing file, plan-required missing) | Silent |
| 6 | `_gate_is_qa_step` (line 437) | `(plan_text, step_number)` | N/A — informational, returns `bool` | Returns `True` if QA detected, `False` otherwise. Never touches `failures`. |
| 7 | `_gate_file_change_audit` (line 446) | `(files_changed)` | N/A — informational, returns `files_changed` passthrough | Returns the input list. Never touches `failures`. |
| 8 | `_gate_scope_check` (line 452) | `(plan_text, step_number, files_changed, failures)` | `{"gate": "scope_check", "evidence": f"out-of-scope files: ..."}` | Silent |
| 9 | `_gate_rule_20_self_check` (line 383) | `(is_qa_step, plan_text, step_number, project_path, parsed, failures, wt_path=None)` | Multiple `{"gate": "rule_20_self_check", "evidence": ...}` variants (banner missing, PASSED line missing, file unreadable) | Early return at line 426 — silent |

**Summary:** All 6 blocking gates (1–5, 8) and the conditional blocking gate (9) follow the **append-on-failure, silent-on-pass** pattern. The 2 informational gates (6, 7) return values but never append to failures.

### Approach recommendation: (ii) Post-hoc inference

Three approaches were considered:

**(i) Gate signature change** — each gate returns `(passed: bool, detail: str)` tuple.
- Pro: Semantically clean; gate owns its own PASS message.
- Con: Requires changing all 9 gate function signatures, the `check()` caller, and all test mocks. Largest refactor (~50+ LOC of signature changes).

**(ii) Post-hoc inference** — verdict-writer composes PASS messages from gate_result data.
- Pro: Zero change to gate functions. PASS messages are simple and static (e.g., `receipt_status` PASS → `"Status: Complete"`, `ceo_flags` PASS → `"No flags raised by agent"`). The verdict-writer already has access to `gate_result` which contains `files_changed`, `is_qa_step`, `plan_header`, etc. One ~30 LOC helper in verdict.py.
- Con: PASS detail strings are decoupled from gate logic. If a gate's semantics change, the PASS message must be updated separately.

**(iii) Registry pattern** — each gate has a `pass_message()` function alongside its check.
- Pro: Colocation of check logic and pass messaging.
- Con: Doubles the gate surface (~9 new functions), heavy for one-liner PASS messages.

**Recommended: (ii) Post-hoc inference.** Rationale:

1. PASS messages are one-liners that rarely change (the gates have been stable since initial implementation; only `deposit_exists` and `rule_20_self_check` have been modified, and their PASS semantics — "file exists" and "banner present + PASSED line present" — haven't changed).
2. The verdict-writer is the **only consumer** of PASS messages, so colocating the logic there is natural.
3. Zero gate refactoring means zero risk of breaking existing gate tests.
4. The verdict-writer already receives `gate_result` and `parsed`, giving it access to all data needed for PASS detail strings (e.g., `parsed.get("receipt_status")` for receipt_status PASS, `len(gate_result["files_changed"])` for file_change_audit detail).

### PASS detail strings (draft, for approach ii)

| Gate | PASS detail |
|---|---|
| `receipt_status` | `f"Status: {parsed.get('receipt_status', 'Complete')}"` |
| `ceo_flags` | `"No flags raised by agent"` |
| `errors` | `"No errors reported in step output"` |
| `permission_denials` | `"No blocking permission denials"` |
| `deposit_exists` | `"All agent-declared deposits present on disk"` |
| `qa_step_detection` | `f"QA step detected (step {step_number} of {total_steps})"` or `"Not a QA step"` |
| `file_change_audit` | `f"{len(files_changed)} files modified"` |
| `scope_check` | `"All changes within plan scope"` |
| `rule_20_self_check` | `"Banner byte-exact, PASSED line present"` (QA steps) or `"N/A (not a QA step)"` (non-QA) |

---

## Q5 — `_gate_rule_20_self_check` QA-Report Parse Reuse

### (a) QA report opening

The gate opens the QA report via this chain (gates.py:388–411):

1. **Path extraction:** `_extract_step_text(plan_text, step_number)` → `_extract_plan_required_deposits(step_text)` → `md_paths` (filtered to `.md` extensions) — lines 388–393
2. **Path resolution:** `_resolve_deposit_path(dep_path, project_path, wt_path=wt_path)` — line 402. Uses 4-strategy resolution (worktree-first, as-is, project-relative, parent-relative).
3. **File open:** `open(resolved, "r", encoding="utf-8")` — line 408
4. **Error handling:** Catches `FileNotFoundError`, `UnicodeDecodeError`, `OSError` (line 410). Each appends a failure: `{"gate": "rule_20_self_check", "evidence": f"deposit file unreadable: {dep_path} ({e})"}`.

### (b) Parse structure

**No structured parse.** The gate reads the full file as a single string (`content = f.read()`, line 409), then performs two checks:

1. Substring search: `if banner not in content:` where `banner = "Rule 20 — QA Self-Check Results"` — line 414
2. Regex search on content after the banner: `re.search(r'^\s*\*{0,2}\s*PASSED\s+—\s+SELF-CHECK\s+PASSED', remaining, re.MULTILINE)` — line 425

No line-by-line parse, no markdown table parse, no AST, no structured object produced or cached. The raw content string is used and discarded.

### (c) Evaluation order and shared-state feasibility

In `gates.check()` (line 119):
- Line 149: `is_qa_step = _gate_is_qa_step(plan_text, step_number)`
- Line 151: `_gate_rule_20_self_check(is_qa_step, ...)`
- (proposed) Line ~152: `_gate_rule_22_verification(is_qa_step, ...)`

The new gate could be added immediately after `_gate_rule_20_self_check`. However, **there is no shared-state mechanism between gates.** Each gate receives explicit parameters from `check()`. To share a cached parse:
- Add a `memo: dict` parameter to `check()` and thread it through both gates (~15 LOC of plumbing)
- `_gate_rule_20_self_check` stores `{dep_path: content}` in memo
- `_gate_rule_22_verification` reads from memo, falls back to independent open

### Recommendation: Independent open (simpler path)

**Independent open is recommended (~5 LOC extra in the new gate).**

| Approach | LOC | Benefit | Cost |
|---|---|---|---|
| Independent open | ~5 extra | Gates remain fully independent; no ordering dependency for correctness; no plumbing changes to `check()` or existing gates | One redundant file read (~100KB) |
| Shared cached parse | ~15 plumbing | Saves one file read | Introduces ordering dependency (rule_20 must run before rule_22); requires `memo` parameter threading through `check()` and both gates; breaks gate independence |

QA reports are small files (< 100KB typical). The redundant read adds < 1ms overhead. Gate independence is more valuable than micro-optimization.

---

## Q6 — Pause Reason Code Routing Surface

### (a) Full enum/string-set of Pause Reason Codes

Currently defined in `verdict.py::_pause_reason_labels` (lines 104–110):

| Code | Label | Used for |
|---|---|---|
| `gate_failure` | Gate failure | Any blocking gate fails |
| `qa_checkpoint` | QA checkpoint | QA step detected |
| `agent_verdict_request` | Agent verdict request | Agent deposited a verdict-request file |
| `header_pause` | Header pause (pause_for_verdict) | Plan header triggers pause |
| `auto_close_disabled` | Auto-close disabled | Final step, auto-close not enabled |

Additionally, `"auto_close"` appears at bellows.py:644 as a ledger-only code (not a pause reason — used when auto-close succeeds).

### (b) Assignment locations

**Mid-plan pause block** (bellows.py:504–511):
```python
if not gate_result["passed"]:
    _pause_reason = "gate_failure"
elif gate_result["is_qa_step"]:
    _pause_reason = "qa_checkpoint"
elif gate_result.get("verdict_requested", {}).get("requested", False):
    _pause_reason = "agent_verdict_request"
else:
    _pause_reason = "header_pause"
```

**Final-step pause block** (bellows.py:590–599):
```python
if not gate_result["passed"]:
    _pause_reason = "gate_failure"
elif gate_result["is_qa_step"]:
    _pause_reason = "qa_checkpoint"
elif gate_result.get("verdict_requested", {}).get("requested", False):
    _pause_reason = "agent_verdict_request"
elif header_says_pause(header, current_step, total_steps, gate_result["is_qa_step"]):
    _pause_reason = "header_pause"
else:
    _pause_reason = "auto_close_disabled"
```

**Worktree teardown failures override to `gate_failure`:**
- Line 516: mid-plan teardown failure
- Line 604: final-step teardown failure

**Worktree creation failure** (line 439–440): hardcoded `pause_reason="gate_failure"`.

### (c) Where `rule_22_check_failed` would be assigned

Per the roadmap's routing design: "If a Rule 22 mechanical check fails AND a separate gate also fails (gate_failure), both rows show FAIL in the table. The Pause Reason Code prioritizes gate_failure."

This means:
- If `_gate_rule_22_verification` fails AND other gates also fail → `gate_failure` (existing code path, no change needed)
- If `_gate_rule_22_verification` fails AND it is the ONLY failure → `rule_22_check_failed`

**Implementation:** The check goes AFTER the `gate_failure` branch in both pause blocks. Since `_gate_rule_22_verification` appends to `failures` like any gate, `gate_result["passed"]` will be False when it fails. The distinction requires inspecting WHETHER all failures are rule_22-only:

```python
if not gate_result["passed"]:
    # Check if ALL failures are rule_22 — if so, use dedicated code
    if all(f["gate"] == "rule_22_verification" for f in gate_result["failures"]):
        _pause_reason = "rule_22_check_failed"
    else:
        _pause_reason = "gate_failure"
elif ...
```

This pattern applies at **both** pause blocks (lines 504 and 590). Estimated: ~6 LOC total (3 per block).

### (d) Modules consuming Pause Reason Code

| Module | Location | Consumption | Needs update for new code? |
|---|---|---|---|
| `verdict.py` | `_pause_reason_labels` dict (line 104) | Maps code → human label for verdict file header | **Yes** — add `"rule_22_check_failed": "Rule 22 mechanical check failed"` |
| `verdict.py` | `post_verdict_request` line 116 | Selects `## Gate Failures` section when `pause_reason == "gate_failure"` | **Needs review** — should `rule_22_check_failed` also trigger the Gate Failures section? Probably yes, since the failures list contains the evidence. |
| `verdict.py` | `log_to_ledger` (line 222) | Pass-through to ledger JSONL — no enum validation | No — accepts any string |
| `bellows.py` | `_consume_verdicts` (line 1162) | Reads `pause_reason_code_from_request` from pending file, passes to `log_to_ledger` | No — pass-through, no routing on specific codes |
| `notifier.py` | `notify_verdict_request` | Receives `failures` list, NOT pause_reason_code | No |
| `PLANNER_TEMPLATE.md` | Rule 25 routing table | Routes codes to Planner actions (stop-and-report-CEO, auto-proceed, etc.) | **Yes** — separate governance edit per roadmap |

### Authoring guidance confirmation (path-form)

The `_normalize_deposit_path` function (gates.py:216–236), shipped in commit `eeaedcb`, normalizes paths to a **project-relative** form for internal comparison:
- Absolute `/Users/.../bellows/knowledge/foo.md` → `knowledge/foo.md`
- Project-prefixed `bellows/knowledge/foo.md` → `knowledge/foo.md`
- Already relative `knowledge/foo.md` → unchanged

**Confirmed: project-prefixed relative paths (`bellows/gates.py`) remain canonical for plan authoring.** The normalization function operates on the INTERNAL comparison within `_gate_deposit_exists`. It does not change which form the Planner should use in `**Deposits:**` blocks. The recommendation from the prior diagnostic (Q6 of deposit-exists-path-form-normalization-2026-05-27.md) still holds: plans MUST use project-prefixed relative paths so that:
1. Raw string comparison with agent-declared paths succeeds (before normalization as a belt)
2. Normalization as a suspenders reduces both forms to the same canonical internal representation

The new `_gate_rule_22_verification` gate will also perform path comparison work (checking plan-declared deposits against the QA verification table). Using normalized forms for these comparisons means the fix plan can safely use project-prefixed relative paths in its `**Deposits:**` block.

---

## Implementation Surface Summary

### Files requiring modification

| File | Changes | Estimated LOC |
|---|---|---|
| `gates.py` | New `_gate_rule_22_verification` function; integration into `check()` | ~53 |
| `verdict.py` | Build Verification Results table from gate_result; Planner-Only Checks Remaining fixed section; update `_pause_reason_labels`; update Gate Failures section condition | ~50 |
| `bellows.py` | Modify both pause-reason assignment blocks to distinguish `rule_22_check_failed` from `gate_failure` | ~6 |
| `tests/test_gates.py` | Tests for `_gate_rule_22_verification` | ~60 |
| `tests/test_verdict.py` | Tests for Verification Results table rendering, PASS row composition | ~60 |
| **Total** | | **~229** |

### Data flow: no call-signature change needed

The existing `post_verdict_request` signature already receives `gate_result` (containing `failures`, `is_qa_step`, `files_changed`, `plan_header`) and `intermediate_decisions`. The Verification Results table can be built from these inputs plus a known-gates registry inside verdict.py. The `parsed` dict is NOT passed, but the one field it contributes to PASS detail (`receipt_status`) can be threaded through `gate_result` by having `check()` add it — or the PASS detail for receipt_status can use a generic "Status: Complete" (since receipt_status != Complete is already a failure).

---

## Output Receipt

**Agent:** Bellows Systems Analyst
**Step:** 1 (diagnostic, single-step)
**Status:** Complete

### What Was Done
Investigated the six-question surface required to ship the verdict-enrichment roadmap. Mapped `post_verdict_request`'s current shape (Q1), its four call sites in bellows.py (Q2), the intermediate decisions data flow (Q3), per-gate return shapes with approach recommendation (Q4: post-hoc inference), QA-report parse reuse feasibility (Q5: independent open), and Pause Reason Code routing surface (Q6: two pause blocks, three modules need updates). Confirmed project-prefixed relative paths remain canonical for plan authoring post-normalization fix.

### Files Deposited
- `bellows/knowledge/research/verdict-enrichment-surface-2026-05-27.md` — this diagnostic findings file
- `bellows/knowledge/research/agent-prompt-feedback.md` — appended dated entry per standard protocol

### Files Created or Modified (Code)
- None (read-only diagnostic)

### Decisions Made
- Approach (ii) post-hoc inference recommended for PASS row composition: zero gate refactoring, ~30 LOC in verdict.py
- Independent QA-report open recommended for `_gate_rule_22_verification`: ~5 LOC extra, preserves gate independence
- `rule_22_check_failed` routing: all-rule-22-only failures get dedicated code, mixed failures get `gate_failure`

### Flags for CEO
- None

### Flags for Next Step
- The executable plan must use project-prefixed relative paths in its `**Deposits:**` block per Q6 confirmation
- `verdict.py` line 116 condition (`pause_reason == "gate_failure"`) needs review: should `rule_22_check_failed` also trigger the Gate Failures section?
- The `parsed["receipt_status"]` value is not currently in `gate_result` — the PASS detail for receipt_status either needs this threaded through or uses a generic string
