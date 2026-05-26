# Verdict Ledger Gate-Result Preservation — Fix Shape Audit

**Date:** 2026-05-26 | **Agent:** Bellows Systems Analyst
**Plan:** diagnostic-verdict-ledger-gate-result-preservation-2026-05-26
**Step:** 1 (SA)

---

## Q1 — Current Ledger Write Flow Trace

### (a) Where does `gate_result` originate?

`gate_result` is constructed with real data by `gates.check()` at `gates.py:156-206`. The function runs all 8 gates (6 blocking, 2 informational) and returns:

```python
# gates.py:199-206
return {
    "passed": len(failures) == 0,
    "failures": failures,
    "is_qa_step": is_qa_step,
    "files_changed": files_changed,
    "plan_header": header,
    "verdict_requested": {"requested": requested, "body": request_body},
}
```

Exception: worktree creation failures construct a synthetic `gate_result` at `bellows.py:437`:
```python
gate_result = {"failures": [{"gate": "worktree_creation", "evidence": str(e)}], "files_changed": [], "passed": False, "is_qa_step": False}
```

### (b) How does `gate_result` reach `post_verdict_request`?

The real `gate_result` is passed to `verdict.post_verdict_request()` at four call sites:

| Call site | Context |
|---|---|
| `bellows.py:529` | Mid-plan pause (gate failure, QA checkpoint, header pause, agent verdict request) |
| `bellows.py:621` | Final-step pause (same reasons) |
| `bellows.py:444` | Worktree creation failure |
| `bellows.py:652` | Auto-close worktree teardown failure |

Inside `post_verdict_request` (`verdict.py:178`), the real `gate_result` is rendered into markdown:
- Lines 200-204: `## Gate Failures` section (only for `gate_failure` / `rule_22_check_failed` pause reasons with actual failures)
- Lines 239-242: `## Files Changed` section (always rendered)
- Line 234: `**Gate Result Passed:** {gate_result.get('passed', False)}` metadata field

### (c) How does control flow reach `_consume_verdicts` and the empty-gate_result construction?

`_consume_verdicts` is called by `_rescan()` in the main daemon thread. At `bellows.py:1186-1205`, it loads the pending verdict request file and parses metadata fields (`Plan`, `Total Steps`, `Pause Reason Code`, `Precondition Failure`). Then at line 1226, a **fresh empty** `gate_result` is constructed:

```python
# bellows.py:1226
gate_result = {"failures": [], "files_changed": []}
```

This overwrites the real gate data that was captured at gate-evaluation time and rendered into the pending file's markdown sections.

### (d) Where is `log_to_ledger` called from `_consume_verdicts`?

Three call sites, all receiving the empty `gate_result`:

| Line | Context | Verdict |
|---|---|---|
| `bellows.py:1246` | Continue verdict on final step → move to Done | `"continue-to-done"` |
| `bellows.py:1260` | Continue verdict on non-final step → resume next step | `v` (from CEO verdict) |
| `bellows.py:1275` | Stop verdict → halt plan | `v` (from CEO verdict) |

One additional call site at `bellows.py:656` passes the **REAL** `gate_result` — this is the auto-close path where gates just ran in the same process, so no serialization round-trip is needed. This is the only path where the ledger receives accurate gate data.

---

## Q2 — Ledger Schema and Consumers

### (a) Ledger entry schema

From `verdict.py:319-328`:

```python
entry = {
    "timestamp": datetime.now().isoformat(),   # ISO string
    "plan_path": plan_path,                     # string
    "step": step_number,                        # int
    "gate_failures": gate_result.get("failures", []),    # array of {"gate": str, "evidence": str}
    "files_changed": gate_result.get("files_changed", []), # array of strings
    "verdict": verdict,                         # string ("continue", "stop", "continue-to-done", "auto-close")
    "reason": reason,                           # string
    "pause_reason_code": pause_reason_code,     # string | null
}
```

No ledger file exists in this worktree (gitignored, runtime data). Schema verified from `verdict.py:314-331` and confirmed by `test_verdict.py:286-360` (4 test functions that assert on the schema).

### (b) Read-side consumers

Exhaustive grep of `ledger.jsonl`, `log_to_ledger`, and `ledger_path` across all `.py` files:

| Consumer | Type | Location |
|---|---|---|
| `verdict.log_to_ledger()` | Write-only | `verdict.py:314-331` |
| `test_log_to_ledger_appends_json` | Test (write + read-verify) | `tests/test_verdict.py:286` |
| `test_log_to_ledger_without_pause_reason_code` | Test (write + read-verify) | `tests/test_verdict.py:308` |
| `test_log_to_ledger_with_pause_reason_code_qa_checkpoint` | Test (write + read-verify) | `tests/test_verdict.py:323` |
| `test_log_to_ledger_all_pause_reason_codes` | Test (write + read-verify) | `tests/test_verdict.py:338` |
| QA smoke script | Test (write + read-verify) | `knowledge/qa/evidence/parallel-1-executable-ledger-pause-reason-code-2026-04-30/smoke.py:15-24` |
| `bellows.py:_consume_verdicts` + `run_plan` | Write-only (call sites) | `bellows.py:656,1246,1260,1275` |
| `tests/test_consume_verdicts.py` | Mock (patches `log_to_ledger`) | 8 test functions, all mock rather than assert on output |
| `tests/test_bellows.py` | Mock (patches `log_to_ledger`) | ~30 test functions, all mock rather than assert on output |
| CEO/SA manual forensics | Read (ad-hoc) | Referenced in `knowledge/architecture/bellows-self-exposure-disposition-2026-05-12.md` |

**No production code reads the ledger.** All production uses are append-only writes. All test reads are in isolated temp directories asserting on the write format. There is no Forge ingestion pipeline yet.

### (c) Backward compatibility

No consumer relies on `gate_failures` and `files_changed` being empty arrays. The test functions in `test_verdict.py` pass gate_results with actual data (`{"failures": [], "files_changed": ["test.py"]}` at line 291) and verify the serialized output. The `test_consume_verdicts.py` and `test_bellows.py` tests mock `log_to_ledger` entirely — they don't inspect what data goes in.

**Populating these arrays with real data is fully backward-compatible.**

---

## Q3 — Three-Shape Evaluation Matrix (+ E.4)

| Criterion | E.1 — Markdown parser | E.2 — Structured sidecar | E.3 — Write at post-time | E.4 — JSON metadata line |
|---|---|---|---|---|
| **LOC estimate** | ~20 lines: 15-line parser function in bellows.py + 5-line call-site change | ~15 lines: 3 in verdict.py (write sidecar), 5 in bellows.py (read sidecar), 3 in bellows.py (cleanup), 4 error handling | ~15 lines: 3 in bellows.py (post-time call), 10+ for dedup/schema migration | **~7 lines**: 1 in verdict.py (add JSON field), 2 in bellows.py (init + parse), 1 in bellows.py (replace empty dict), 3 for try/except |
| **New artifacts** | None | `.gate_result.json` per verdict request | None (but dual ledger entries or schema migration) | None |
| **Reversibility** | Remove parser function + revert 1 line | Remove sidecar writer, reader, and cleanup code | Requires ledger entry deduplication or migration | Remove 1 metadata line + 1 parse block |
| **Forge-readiness** | Good — ledger entries contain real data | Good — ledger entries contain real data | Complex — dual entries or missing verdict in post-time entry | Good — ledger entries contain real data |
| **Coupling created** | **High** — regex must match markdown format at verdict.py:200-204. If format changes (e.g., nested evidence, multi-line), parser breaks silently | **Medium** — sidecar filename must match request filename; both must be cleaned up atomically | **High** — temporal coupling: post-time entry lacks verdict, consume-time entry must correlate or deduplicate | **None** — JSON is self-describing; `json.dumps`/`json.loads` round-trips perfectly |
| **Failure modes** | Regex mismatch → silent data loss (empty arrays in ledger, same as today) | Missing sidecar (deleted independently) → KeyError or silent data loss; orphan sidecars if request deleted without sidecar | Duplicate ledger entries confuse consumers; if post-time-only, verdict field is missing | Malformed JSON → caught by try/except, falls back to empty dict (same as today) |

---

## Q4 — Unenumerated Alternatives

### Evaluated

**(i) Pass `gate_result` through call arguments end-to-end.** Not feasible. There is a temporal gap between `post_verdict_request` (gate time) and `_consume_verdicts` (CEO verdict time). The daemon may restart between these events. In-memory state does not survive restarts.

**(ii) Separate gate-time ledger logger.** Equivalent to E.3. The ledger is append-only JSONL with no upsert mechanism. Writing at gate-time produces an entry without the verdict (continue/stop) and reason. Writing again at consume-time creates duplicates. Either the ledger schema must change to support upsert, or consumers must handle dual entries.

**(iii) Preserve the verdict request file.** Currently deleted at `bellows.py:1292-1293`. If retained, the markdown is available indefinitely. But: (a) files accumulate without cleanup, (b) the ledger entry would contain a path reference rather than the data, meaning consumers must chase the file, (c) if the file is later deleted as part of cleanup, the reference becomes dangling.

### Identified: E.4 — JSON Metadata Line

**Description:** Embed a `**Gate Result JSON:**` metadata line in the verdict request file's header (alongside existing `**Total Steps:**`, `**Pause Reason Code:**`, `**Precondition Failure:**`). At consume-time, parse it in the same `for req_line in pending_req_file_text.splitlines()` loop that already parses those fields.

**Writer side** (`verdict.py:234`, inside the content string):
```python
f"**Gate Result JSON:** {json.dumps({'failures': gate_result.get('failures', []), 'files_changed': gate_result.get('files_changed', [])})}\n"
```

**Reader side** (`bellows.py:1185`, initialization):
```python
gate_result_from_request = None
```

**Reader side** (`bellows.py:1205`, after Precondition Failure parse):
```python
if req_line.startswith("**Gate Result JSON:**"):
    try:
        gate_result_from_request = json.loads(req_line.split(":**", 1)[1].strip())
    except (json.JSONDecodeError, IndexError):
        pass
```

**Consumer side** (`bellows.py:1226`, replace empty dict):
```python
gate_result = gate_result_from_request or {"failures": [], "files_changed": []}
```

**Advantages over E.1-E.3:**
- No markdown parsing (JSON round-trips perfectly via `json.dumps`/`json.loads`)
- No new artifact files
- No temporal split or duplicate entries
- Uses the exact metadata-parsing pattern already established at lines 1188-1205
- Backward compatible: pre-existing pending files without the JSON line produce `gate_result_from_request = None`, falling through to the existing empty dict

---

## Q5 — Recommendation

**E.4 (JSON metadata line).**

The failure being fixed is evidence destruction: the original `gate_result` is in memory at gate-evaluation time but lost by consumption time because `_consume_verdicts` constructs a fresh empty dict. E.4 solves this by embedding a JSON-serialized subset of `gate_result` (`failures` + `files_changed`) in the verdict request file's metadata header — the same header that already carries `Total Steps`, `Pause Reason Code`, and `Precondition Failure`. At consume-time, the JSON line is parsed alongside these existing fields in the same `for req_line` loop (3-4 new lines). The ledger then receives the real gate data, making all future gate-failure forensics conclusive. This shape has the best LOC-to-robustness ratio (~7 lines for full evidence preservation), introduces zero new artifacts or dependencies, creates no writer/reader coupling (JSON is self-describing, unlike the markdown regex coupling E.1 would require), and produces clean structured data for future Forge ingestion. Backward compatibility is automatic: pending files created before the fix lack the `**Gate Result JSON:**` line, so `gate_result_from_request` stays `None` and falls through to the existing empty-dict default — identical to today's behavior.

---

## Q6 — Implementation Hand-Off Detail

### Change 1: verdict.py — Add JSON metadata line to verdict request content

**Location:** `verdict.py:234` — after the `**Gate Result Passed:**` line in the content string.

**Change:** Insert one line into the f-string:
```
f"**Gate Result JSON:** {json.dumps({'failures': gate_result.get('failures', []), 'files_changed': gate_result.get('files_changed', [])})}\n"
```

**Note:** `json` is already imported at `verdict.py:3`.

### Change 2: bellows.py — Initialize `gate_result_from_request`

**Location:** `bellows.py:1185` — after `precondition_failure_from_request = False`.

**Change:** Add one line:
```python
gate_result_from_request = None
```

### Change 3: bellows.py — Parse JSON metadata field from pending request file

**Location:** `bellows.py:1205` — after the `Precondition Failure` parse block (inside the `for req_line in pending_req_file_text.splitlines()` loop).

**Change:** Add 4 lines:
```python
if req_line.startswith("**Gate Result JSON:**"):
    try:
        gate_result_from_request = json.loads(req_line.split(":**", 1)[1].strip())
    except (json.JSONDecodeError, IndexError):
        pass
```

**Note:** `json` is already imported in `bellows.py`.

### Change 4: bellows.py — Replace empty gate_result with parsed data

**Location:** `bellows.py:1226` — replace the line:
```python
gate_result = {"failures": [], "files_changed": []}
```

**With:**
```python
gate_result = gate_result_from_request or {"failures": [], "files_changed": []}
```

### Fix Shape F (complementary) — Terminal log expansion

**Location:** `bellows.py:495` — the line:
```python
_log("EVENT", f"gates step {current_step}: passed={gate_result['passed']}, failures={len(gate_result['failures'])}", slug=slug_for(plan_name))
```

**Change:** Expand to include failure gate names and files_changed count:
```python
failure_gates = ", ".join(f["gate"] for f in gate_result["failures"]) if gate_result["failures"] else "none"
_log("EVENT", f"gates step {current_step}: passed={gate_result['passed']}, failures={len(gate_result['failures'])} ({failure_gates}), files_changed={len(gate_result.get('files_changed', []))}", slug=slug_for(plan_name))
```

**Note:** There is a second identical log line at `bellows.py:586` that should receive the same expansion.

### Summary

| File | Lines changed | Description |
|---|---|---|
| `verdict.py` | +1 | Add `**Gate Result JSON:**` metadata line |
| `bellows.py` | +1 (init) +4 (parse) +1 (replace) = +6 | Parse JSON field, use for ledger writes |
| `bellows.py` | +2 (two log sites) | Fix F: expand terminal log with failure details |
| **Total** | **+9** | |

---

## Q7 — Verification Block (Rule 39)

### Load-bearing claim: call-flow trace anchors

Re-verified each `gate_result` reference by re-reading the cited lines:

| Anchor | Cited line | Actual content | Match? |
|---|---|---|---|
| Empty dict construction | `bellows.py:1226` | `gate_result = {"failures": [], "files_changed": []}` | **Yes** |
| Ledger call (continue-to-done) | `bellows.py:1246` | `verdict.log_to_ledger(full_plan_path, step_number, gate_result,` | **Yes** |
| Ledger call (continue-resume) | `bellows.py:1260` | `verdict.log_to_ledger(full_plan_path, step_number, gate_result, v, reason,` | **Yes** |
| Ledger call (stop/halt) | `bellows.py:1275` | `verdict.log_to_ledger(full_plan_path, step_number, gate_result, v, reason,` | **Yes** |
| Auto-close ledger call (REAL data) | `bellows.py:656` | `verdict.log_to_ledger(plan_path, current_step, gate_result, "auto-close",` | **Yes** |
| Gate Failures markdown writer | `verdict.py:200-204` | `if pause_reason in ("gate_failure", "rule_22_check_failed") and gate_result.get("failures"):` ... `pause_section = f"## Gate Failures\n\n{failures_text}"` | **Yes** |
| Files Changed markdown writer | `verdict.py:239-242` | `f"## Files Changed\n\n"` ... `for fc in gate_result.get("files_changed", []):` | **Yes** |
| `log_to_ledger` definition | `verdict.py:314-331` | `def log_to_ledger(plan_path, step_number, gate_result, verdict, reason, pause_reason_code: Optional[str] = None):` | **Yes** |
| Ledger entry fields | `verdict.py:323-324` | `"gate_failures": gate_result.get("failures", []),` / `"files_changed": gate_result.get("files_changed", []),` | **Yes** |
| Pending file read | `bellows.py:1187` | `pending_req_file_text = pending_req_file.read_text()` | **Yes** |
| Metadata parse loop | `bellows.py:1188` | `for req_line in pending_req_file_text.splitlines():` | **Yes** |
| Metadata field init block | `bellows.py:1183-1185` | `total_steps_from_request = None` / `pause_reason_code_from_request = None` / `precondition_failure_from_request = False` | **Yes** |
| Gate Result Passed metadata | `verdict.py:234` | `f"**Gate Result Passed:** {gate_result.get('passed', False)}\n"` | **Yes** |
| Pending file deletion | `bellows.py:1292-1293` | `if pending_file.exists():` / `pending_file.unlink()` | **Yes** |
| Terminal log (first site) | `bellows.py:495` | `_log("EVENT", f"gates step {current_step}: passed={gate_result['passed']}, failures={len(gate_result['failures'])}", slug=slug_for(plan_name))` | **Yes** |
| Terminal log (second site) | `bellows.py:586` | Confirmed identical pattern at this line | **Yes** |

All 16 anchors verified. No line-number drift detected.

---

## Decisions Made

1. **Recommended E.4 (JSON metadata line) over E.1 (markdown parser), E.2 (structured sidecar), and E.3 (write-at-post-time).** E.4 has the lowest LOC (~7 lines), zero new artifacts, zero coupling, and automatic backward compatibility. It uses the exact metadata-parsing pattern already established in `_consume_verdicts`.

2. **Identified E.4 as an unenumerated alternative.** The CEO Context listed three shapes (E.1-E.3). E.4 is superior to all three on every evaluation criterion.

3. **Confirmed no read-side consumers of the ledger exist in production code.** Populating `gate_failures` and `files_changed` with real data is fully backward-compatible.

4. **Confirmed auto-close path already writes real data.** `bellows.py:656` is the only ledger call site that passes the real `gate_result`. The three `_consume_verdicts` sites (1246, 1260, 1275) all pass the empty dict — this is the bug.

---

## Flags for CEO

1. **Architecture recommendation: E.4 (JSON metadata line).** ~7 lines total across `verdict.py` (1 line) and `bellows.py` (6 lines). No new artifacts, no schema migration, no coupling. Falls back gracefully for pre-fix verdict request files.

2. **Implementation hand-off ready.** Q6 contains exact file locations, line numbers, and code snippets for all 4 changes (E.4) plus 2 changes (Fix F). A DEV plan can be authored directly from Q6 without re-investigation.

3. **Fix F (terminal log expansion) confirmed as complementary.** Two log sites at `bellows.py:495` and `:586` currently log only failure count. Expanding to include gate names and files_changed count provides real-time triage evidence. ~2 additional lines per site.

4. **No contingency needed.** Unlike the CEO Context's note about E.2-vs-E.1 contingency, E.4 is unconditionally superior. No CEO call required on shape selection — E.4 dominates on all evaluation criteria.

5. **Next action: Planner authors DEV plan** for Fix E.4 + Fix F, using Q6 as the implementation specification.

---

## Output Receipt

**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done

Full architectural evaluation of four candidate shapes for preserving `gate_result` in the verdict ledger. Traced the complete call flow from gate evaluation through verdict request posting to verdict consumption and ledger write. Identified an unenumerated alternative (E.4 — JSON metadata line) that dominates all three CEO-enumerated shapes on every evaluation criterion. Provided exact implementation hand-off detail with line numbers and code snippets.

### Files Deposited

- `knowledge/research/verdict-ledger-gate-result-preservation-2026-05-26.md` — Q1-Q7 findings, evaluation matrix, recommendation, and implementation hand-off

### Files Created or Modified (Code)

- None (read-only investigation)

### Decisions Made

- Recommended E.4 (JSON metadata line) as the fix shape
- Confirmed no read-side ledger consumers exist — change is backward-compatible
- Confirmed auto-close path (bellows.py:656) already writes real data — only _consume_verdicts sites need fixing

### Flags for CEO

- E.4 recommended — ~7 LOC, zero artifacts, zero coupling, automatic backward compatibility
- Implementation hand-off in Q6 — DEV plan can be authored directly
- Fix F (terminal log expansion) complementary — ~4 additional LOC at two sites
- No contingency or CEO shape-selection call needed — E.4 dominates unconditionally

### Flags for Next Step

- None (single-step diagnostic)
