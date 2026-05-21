# SA Findings — bellows expected-keys warning diagnostic

**Date:** 2026-05-21
**Diagnostic:** `diagnostic-bellows-expected-keys-warning-2026-05-21`
**Scope:** read-only investigation of `bellows.py`, `gates.py`, `validators.py`, `parser.py`, `verdict.py`, and 30 Done plans

---

## 1. Confirm the warning code

The warning lives at `bellows.py:416-419`:

```python
# bellows.py:416-419
expected_keys = {"project", "date", "author", "total_steps", "pause_for_verdict"}
missing_keys = expected_keys - set(header.keys())
if total_steps > 1 and missing_keys:
    _log("WARN", f"⚠️ {total_steps} steps but parsed header is missing: {sorted(missing_keys)}. Parsed keys: {sorted(header.keys())}. If pause_for_verdict was missing, the defensive default has set it to after_step_1.", slug=slug_for(plan_name))
```

**`expected_keys` set membership:** `{"project", "date", "author", "total_steps", "pause_for_verdict"}` — five keys.

**WARN log format string:** Reports step count, sorted list of missing keys, sorted list of parsed keys, and a note about the `pause_for_verdict` defensive default.

**Trigger condition:** `total_steps > 1 and missing_keys` — fires only for multi-step plans and only when at least one of the five expected keys is absent from the parsed header dict.

**Related code — defensive defaults (fires BEFORE the warning):**

```python
# bellows.py:317-326
def _apply_defensive_header_defaults(header: dict, total_steps: int) -> dict:
    if total_steps > 1 and len(header) < 3:
        if not header.get("pause_for_verdict", "").strip():
            header["pause_for_verdict"] = "after_step_1"
    return header
```

Called at `bellows.py:381` before the warning at line 418. This means:
- If `pause_for_verdict` was missing AND the header had < 3 keys, the defensive default fires and inserts `"after_step_1"` into the header dict **before** the missing-keys check runs.
- In that case, `pause_for_verdict` would NOT appear in `missing_keys` despite being absent from the original plan header.
- If the header has ≥ 3 keys but no `pause_for_verdict`, the defensive default does NOT fire, and `pause_for_verdict` DOES appear in the warning — this is the case called out by the BACKLOG entry.

**Related code — downstream consumers of parsed header:**

```python
# bellows.py:384 — model extraction
model = header.get("Model", header.get("model", config["default_model"]))

# bellows.py:495 — auto_close extraction (after gates.check re-parses header)
effective_auto_close = str(header.get("auto_close", "false")).lower() == "true"
```

---

## 2. Per-key runtime audit

### `project` — COSMETIC

**Consumption sites:** None. No `header.get("project")` or `header["project"]` call exists in `bellows.py`, `gates.py`, `validators.py`, `verdict.py`, or `runner.py`.

The project path used at runtime is derived from the filesystem:
```python
# bellows.py:344-345
plan_p = pathlib.Path(plan_path)
project_path = str(plan_p.parents[2])
```

The `project` header field is pure metadata — it is never consumed for routing, validation, or any control flow decision.

### `date` — COSMETIC

**Consumption sites:** None. No `header.get("date")` or `header["date"]` call exists in any runtime module.

The plan date is captured in the filename convention (`*-2026-05-21.md`) and in the `record_run` database via `datetime.now().isoformat()` (bellows.py:294). The header `date` field is metadata only.

### `author` — COSMETIC

**Consumption sites:** None. No `header.get("author")` or `header["author"]` call exists in any runtime module.

Author identity has no runtime role in Bellows. It serves only as plan provenance metadata.

### `total_steps` — COSMETIC (header field value not consumed)

**Consumption sites for the header field:** None. No `header.get("total_steps")` or `header["total_steps"]` call exists in any runtime module.

The actual step count consumed by the orchestration loop is derived from plan body parsing:
```python
# bellows.py:214-220
def extract_total_steps(plan_text: str) -> int:
    plan_text = strip_fenced_code_blocks(plan_text)
    case_insensitive_count = len(re.findall(r"^## STEP\s+\d+", plan_text, re.MULTILINE | re.IGNORECASE))
    ...
    return case_insensitive_count
```

The `total_steps` header field (parsed from `**Total Steps:** N`) is never read. The step count is always derived from counting `## STEP N` headers in the plan body.

**Additional parser mismatch:** Some plans emit `**Steps:** 2` (parsed to key `steps`) or `**steps:** 2` (also parsed to key `steps`), which never matches the expected key `total_steps`. The expected-keys warning fires on these plans even though a step-count field IS present in the header — just under a different key name.

### `pause_for_verdict` — SAFETY-CRITICAL

**Consumption sites:**

1. `header_says_pause()` at `bellows.py:305-314` — **controls pause routing**:
   ```python
   def header_says_pause(header: dict, current_step: int, total_steps: int, is_qa_step: bool) -> bool:
       pv = header.get("pause_for_verdict", "")
       if pv == "always":
           return True
       if pv == "after_step_1":
           return current_step == 1
       if pv == "after_qa_step":
           return is_qa_step
       return False
   ```
   Called at `bellows.py:502` (while-loop) and `bellows.py:590` (final-step). Determines whether Bellows pauses for CEO verdict or auto-advances to the next step.

2. `_apply_defensive_header_defaults()` at `bellows.py:317-326` — **safety net for sparse headers**:
   Sets `pause_for_verdict = "after_step_1"` when header has < 3 keys and `total_steps > 1`.

3. `validators.check_pause_for_verdict_value()` at `validators.py:126-138` — **claim-time enum validation**:
   Warns if value is not in `{"always", "after_step_1", "after_qa_step", "after_each_step", ""}`.

**What "missing" means at runtime if the defensive default fires:** If `pause_for_verdict` is absent from the original plan header AND the header has < 3 keys, `_apply_defensive_header_defaults` inserts `"after_step_1"` before the missing-keys check. The key then appears present in the dict, so the warning does NOT mention it. The plan pauses after step 1 — safe behavior.

If `pause_for_verdict` is absent but the header has ≥ 3 keys (e.g., a pipe-format header with `date`, `tier`, `test_scope`, `execution`), the defensive default does NOT fire. `header_says_pause()` returns `False` for all steps (empty string doesn't match any enum value). **The plan auto-advances without pausing.** The warning fires and mentions `pause_for_verdict` — this is the genuinely dangerous case, and the warning IS informative here.

---

## 3. Dispatch-mode and other keys NOT in expected_keys

### `dispatch_mode` — SAFETY-CRITICAL (not in expected_keys)

**Consumption site:** `validators.validate_at_claim()` → `validators.check_missing_dispatch_mode()` at `validators.py:27-42`:

```python
# validators.py:19-42
def _get_dispatch_mode(header: dict) -> Optional[str]:
    raw = header.get("dispatch_mode") or header.get("Dispatch Mode")
    if raw is None:
        return None
    return str(raw).strip().lower()

def check_missing_dispatch_mode(header: dict) -> Optional[dict]:
    mode = _get_dispatch_mode(header)
    if mode is None:
        return {
            "check": "missing_dispatch_mode",
            "severity": "reject",
            "message": "Plan header missing **Dispatch Mode:** field. Per Rule 35, this field is required. Plan will not be claimed."
        }
    if mode not in ("bellows", "manual_bootstrap"):
        return {
            "check": "missing_dispatch_mode",
            "severity": "reject",
            "message": f"Plan header has invalid dispatch_mode='{mode}'. Must be 'bellows' or 'manual_bootstrap'. Plan will not be claimed."
        }
    return None
```

Called at `bellows.py:388`. **A missing or invalid `dispatch_mode` causes plan rejection** — the plan is moved to `halted-*` and a Pushover notification is sent. This is more safety-critical than any key in `expected_keys` except `pause_for_verdict`.

However, `dispatch_mode` already has its own validator (`check_missing_dispatch_mode`) at claim time, which runs BEFORE the expected-keys warning. The warning at line 419 would be redundant for this key — plans missing `dispatch_mode` are rejected before reaching that code path.

### `auto_close` — SAFETY-CRITICAL (not in expected_keys)

**Consumption site:** `bellows.py:495`:

```python
# bellows.py:495
effective_auto_close = str(header.get("auto_close", "false")).lower() == "true"
```

Controls whether the plan auto-closes (moves to Done/) on clean gates at final step, or pauses for CEO verdict. Used at:
- `bellows.py:591`: `or not effective_auto_close` — final-step pause condition
- `bellows.py:631`: `and effective_auto_close` — auto-close condition

**Default behavior when absent:** `"false"` — plan pauses for verdict. This is the safe default. Missing `auto_close` produces safe behavior (pause), so its absence is not dangerous. The current `expected_keys` omission is acceptable.

### `model` / `Model` — OPERATIONAL (not in expected_keys)

**Consumption site:** `bellows.py:384`:
```python
model = header.get("Model", header.get("model", config["default_model"]))
```

Falls back to `config["default_model"]` when absent. Safe default.

### Other header keys with no runtime consumption

`tier`, `test_scope`, `execution`, `type`, `priority`, `depends_on`, `plan`, `plan_slug`, `last_updated`, `created` — none of these have `header.get()` consumers in any runtime module. All are metadata only.

---

## 4. Planner template audit

**Note:** No single `PLANNER_TEMPLATE.md` file exists in this repository. The Planner template lives in the governance-root repo (referenced as versions v4.35–v4.47 in BACKLOG entries). Template evolution is tracked via `knowledge/development/planner-template-*.md` files.

**Documented header formats observed in Done/ plans:**

**Format A — Old pipe-separated (pre ~2026-05-10):**
`**Date:** 2026-04-16 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA)`

**Format B — Transitional pipe-separated (~2026-05-12):**
`**project:** bellows | **type:** executable | **steps:** 2 | **pause_for_verdict:** after_step_1 | **auto_close:** false`

**Format C — Multi-line bold (~2026-05-10+):**
```
**Project:** bellows
**Date:** 2026-05-10
**Author:** Planner
**Total Steps:** 2
**pause_for_verdict:** after_step_1
```

**Format D — Current pipe-separated (~2026-05-19+):**
`**Date:** 2026-05-21 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** none | **Execution:** Step 1 (SA) | **pause_for_verdict:** after_step_1`

**Format E — Current multi-line bold (~2026-05-19+):**
```
**Project:** bellows
**Dispatch Mode:** bellows
**Plan Type:** executable
**Date:** 2026-05-27
**Total Steps:** 3
```

### Per-key emission rates (30-plan sample, sorted by mtime descending)

| Key | Emission Rate | Notes |
|-----|---------------|-------|
| `project` | 12/30 (40%) | Absent from Format A plans; present in Formats B/C/D/E |
| `date` | 28/30 (93%) | Universally present except Format B which uses different key set |
| `author` | 2/30 (7%) | Only in Format C (e.g., `executable-startup-sweep-extract-2026-05-10`, `executable-bellows-config-split-2026-05-23`) |
| `total_steps` | 3/30 (10%) | Only in Formats C/E as `**Total Steps:**`. Format B uses `**steps:**` which parses to `steps` not `total_steps` |
| `pause_for_verdict` | 15/30 (50%) | Absent from all Format A plans pre-2026-05-08; present in most plans since |

**Plans that emit ALL 5 expected keys:** 2/30 (7%) — only `executable-startup-sweep-extract-2026-05-10` and `executable-bellows-config-split-2026-05-23`.

**Conclusion:** The warning fires on the vast majority of multi-step plans because the template historically never required `author` or `total_steps`, and `project` was only added in later template versions. The warning is effectively always-on for multi-step plans dispatched before ~2026-05-23 format stabilization.

---

## 5. Single-line header impact

The parser lives at `gates.py:79-145`. Strategy 2 (bold-Markdown) uses this extraction regex at `gates.py:141`:

```python
# gates.py:141
for m in re.finditer(r'\*\*([^:*]+):\*\*\s*([^|]*?)(?:\s*\||$)', header_line):
    key = m.group(1).strip().lower().replace(" ", "_")
    value = m.group(2).strip()
    result[key] = value
```

**Key normalization:** `.strip().lower().replace(" ", "_")` — so:
- `**Date:**` → `date` ✓
- `**Project:**` / `**project:**` → `project` ✓
- `**Author:**` → `author` ✓
- `**Total Steps:**` → `total_steps` ✓
- `**Steps:**` / `**steps:**` → `steps` ✗ (does NOT match expected key `total_steps`)
- `**pause_for_verdict:**` → `pause_for_verdict` ✓
- `**Pause for verdict:**` → `pause_for_verdict` ✓
- `**Dispatch Mode:**` → `dispatch_mode` ✓

**Parser-extractable vs. plan-emitted gap:** The parser CAN extract all 5 expected keys if the plan header uses exact key names. The issue is not parser limitation — it is template gap. The parser correctly extracts every key the plan actually emits.

**`steps` vs `total_steps` naming collision:** Plans using `**Steps:** 2` (Format B) produce key `steps` which is NOT in `expected_keys`. The warning reports `total_steps` as missing even though a step-count field exists — just under a different name. This is a key-name normalization issue between template versions, not a parser bug.

**Multi-line collection (gates.py:117-131):** The parser collects consecutive `**bold:**` lines after the title and joins them with ` | ` before applying the pipe-separator regex. This means multi-line bold headers (Formats C/E) are correctly parsed identically to pipe-separated headers.

---

## 6. Recommendation — Gap Assessment

| Gap | Current State | Proposed State | Change Required | Recommended | Rationale |
|-----|--------------|----------------|-----------------|-------------|-----------|
| (a) `project` key | In `expected_keys` — warning fires when absent. Never consumed at runtime. | Remove from `expected_keys`. | Bellows code change (1 LOC) | **Yes** | Cosmetic metadata. No runtime consumer. Warning is noise. |
| (b) `date` key | In `expected_keys` — warning fires when absent. Never consumed at runtime. | Remove from `expected_keys`. | Bellows code change (1 LOC) | **Yes** | Cosmetic metadata. No runtime consumer. Emitted by 93% of plans so low noise, but still meaningless as a warning. |
| (c) `author` key | In `expected_keys` — warning fires when absent. Never consumed at runtime. | Remove from `expected_keys`. | Bellows code change (1 LOC) | **Yes** | Cosmetic metadata. Emitted by 7% of plans — constant noise source. |
| (d) `total_steps` key | In `expected_keys` — warning fires when absent. Never consumed at runtime (step count derived from `## STEP N` headers). | Remove from `expected_keys`. | Bellows code change (1 LOC) | **Yes** | Value in header is never used. The key name also doesn't match Format B plans (`steps` vs `total_steps`). |
| (e) `pause_for_verdict` key | In `expected_keys` — warning fires when absent. **Consumed at runtime** by `header_says_pause()` for pause routing. Defensive default covers sparse headers. | **Keep in `expected_keys`** (as sole remaining member) OR use targeted warning. | Bellows code change (refine warning) | **Yes — keep, but refine** | Only safety-critical key in the set. Warning should fire for this key specifically, not bundled with cosmetic keys. |
| (f) `dispatch_mode` (not in `expected_keys`) | Has its own validator at claim time (`check_missing_dispatch_mode`) that rejects plans with missing/invalid values. | No change needed. | None | **Defer** | Already guarded by a reject-level validator at claim time. Plans missing `dispatch_mode` never reach the expected-keys warning. Adding to `expected_keys` would be redundant. |
| (g) `auto_close` (not in `expected_keys`) | Default when absent is `"false"` — safe behavior (pause for verdict). | No change needed. | None | **Defer** | Safe default. Missing `auto_close` produces the conservative outcome (pause). |

### Overall resolution shape recommendation: **Shape (1) — Narrow the warning**

**Rationale:** Of the 5 keys in `expected_keys`, only `pause_for_verdict` is safety-critical. The other 4 are cosmetic metadata with zero runtime consumption. The warning currently fires on essentially all multi-step plans from before ~2026-05-23, producing persistent noise that dilutes the signal when `pause_for_verdict` is genuinely missing.

**Recommended implementation:**
- Replace `expected_keys = {"project", "date", "author", "total_steps", "pause_for_verdict"}` with a targeted check for `pause_for_verdict` only.
- Anchor line for edit: `bellows.py:416` (the `expected_keys = ...` assignment).
- The warning should fire specifically when `total_steps > 1` and `pause_for_verdict` is absent from the header dict AND the defensive default did NOT inject it (i.e., the header had ≥ 3 keys, so `_apply_defensive_header_defaults` skipped it).
- Shape (2) (fix templates upstream) is NOT recommended as standalone fix because: (a) the template has already evolved to include `pause_for_verdict` in most plans since 2026-05-08, (b) `author` and `total_steps` are structurally unnecessary at runtime, and (c) the warning would still fire on all in-flight and Done/ plans from before the template change, producing persistent noise with no value.

**Not recommending adding `dispatch_mode` or `auto_close` to `expected_keys`:** `dispatch_mode` has its own claim-time validator that rejects on absence (stronger than a warning). `auto_close` defaults to safe behavior (pause).
