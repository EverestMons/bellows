# E4 Design: Verdict Conditioning — Re-check Mechanism, Refusal Disposition, Override Arm, Activation

**Date:** 2026-08-24 | **Diagnostic:** 517 | **Implements:** bypass (d) from `eluvian-path-audit-2026-08-24.md` §E4 | **Ruling consumed:** fork 5 from `eluvian-path-rulings-2026-08-24.md`

**Fork 5, verbatim:** "Daemon re-checks at consumption — the daemon re-runs the gate check when consuming a `continue`; verdict files stay plain; the enforcing party is the acting party."

**Structural precedent:** `diagnostic-511`→`executable-513` (E2) and `diagnostic-515`→`executable-516` (E3) — the same two-step shape, third running.

---

## Re-derived Numbers

All measured 2026-08-24 against bellows main (post-E3, `c3da7e7` era). These supersede the plan's pins; each is independently re-derived.

| id | pin | re-derived value | probe |
|---|---|---|---|
| G1 | bypass (d) re-derived | **CONFIRMED** — only `worktree_teardown` conditions a continue | bellows.py:2576-2597: the `v == "continue"` branch's sole gate consultation is `any(f.get("gate") == "worktree_teardown" for f in gate_result.get("failures", []))` at :2581. `record_verdict_outcome` at :2574 fires BEFORE any conditioning. Every other failed-gate + continue → advances unconditionally |
| G2 | the fail-open gate-record fallback | **CONFIRMED** — bellows.py:2570 | `gate_result = gate_result_from_request or {"failures": [], "files_changed": []}`. An absent or unparseable pending-request file reads as NO FAILURES. Deleting `verdicts/pending/verdict-request-<slug>-step-N.md` evades even the teardown guard |
| G3 | the pre-built, unconsumed substrate | **CONFIRMED** — lifecycle.py:470-510; DDL at lifecycle.py:130-138 | `record_gate_events` writes BOTH pass rows and fail rows per step (called at bellows.py:1080, :1210). DDL: `gate_events(step_id, gate_name, result CHECK IN ('pass','fail'), reason_code, overridden INTEGER DEFAULT 0, override_ref)`. **Writers of `overridden`/`override_ref`: NONE.** Measured on live DB: `SELECT COUNT(*), SUM(overridden) FROM gate_events` → `6431, 0`. `grep -rn 'overridden\|override_ref' bellows.py gates.py verdict.py tools/` → only lifecycle.py:486-491 (the INSERT that reads from gate_result dict — no caller ever sets those keys). Positive control: `record_gate_events` found at its 2 call sites (bellows.py:1080, :1210). Nothing at consumption READS gate_events either — same dead-substrate class as `cleared_by='clear_tool'` (lifecycle.py:175 enum arm; the 2026-08-24 lesson) |
| G4 | a full gate re-RUN post-teardown is impossible | **CONFIRMED** — gates.py:186 | `check(parsed, plan_text, step_number, project_path, files_changed=None, wt_path=None)` needs step-time context — the agent's parsed output and the worktree, both destroyed at step end. "Re-runs the gate check" must therefore mean CONSUMING THE RECORDED RESULT |
| G5 | verdict file contract | **CONFIRMED** — verdict.py:282-302 | First line `^(?:verdict:\s*)?(continue|stop)$`, reason = remainder; malformed → skip + notify (bellows.py:2504-2508). Fork 5's "verdict files stay plain" constrains D-3 |
| G6 | the workflow E4 must not break | **CONFIRMED** — precedent | continue-with-reasoning on known-benign gate failures (the exec-493 evidence-path false-positive class). Enforcement without an override arm converts every false-positive gate into a hard block |
| G7 | consumption test surface | **CONFIRMED** — 20 | `grep -cE '^def test\|^    def test' tests/test_consume_verdicts.py` → 20 |
| G8 | live state at authoring | **CONFIRMED** — daemon PID 22189; suite 1325 green; E3's `_retire_receipts` calls at bellows.py:2596/:2630/:2660 as fixed landmarks | `python3 -m pytest --co -q` → 1325 tests collected |

---

## D-1 — The Re-check Mechanism

### What "re-runs the gate check" means under G4

A full gate re-RUN (`gates.check(parsed, ...)`) is impossible post-teardown — the agent's parsed output and the worktree are destroyed at step end (gates.py:186; bellows.py:1110-1112). "Re-runs the gate check" means: **consult the durable record of the step-time gate result when consuming a `continue`, and refuse to advance when unoverridden failures are present.**

### Sources consulted

Two sources carry the gate result at consumption time:

**(a) Request file's `Gate Result JSON`** (bellows.py:2545-2549). Parsed from `verdicts/pending/verdict-request-<slug>-step-N.md`. Present for all plans post-May-2026 (the `_make_verdict_request_content` enrichment). **Weakness:** deletable — the G2 bypass. An absent file reads as `{"failures": [], "files_changed": []}` today.

**(b) `gate_events` rows** (lifecycle.py:470-510). Durable DB rows keyed on `step_id`. Record both pass and fail rows per gate. Survive file deletion. **Weakness:** require a `step_id` which requires a `plan_id` — and slug-only legacy plans have `_lc_plan_id = None` (bellows.py:2572-2573: the `fullmatch` is `r"(?:(?:diagnostic|executable|qa)-)?(\d+)"`, id-native only).

### Decision: dual-source, fail-closed

The consumption check consults **both** sources:

1. **Primary: `gate_events` rows** for the step (when `_lc_plan_id` is not None). Query: `SELECT gate_name, result, overridden FROM gate_events WHERE step_id = (SELECT id FROM steps WHERE plan_id = ? AND step_number = ?) AND result = 'fail' AND overridden = 0`. Any rows returned → unoverridden failures present → the continue is subject to the D-2 disposition.

2. **Fallback: request file's `Gate Result JSON`** (when `_lc_plan_id` is None, or as cross-check). The parsed `gate_result_from_request` at bellows.py:2545-2549. Failures in the list that lack `"overridden": true` → unoverridden failures present.

3. **Fail-closed on absence of both:** If `_lc_plan_id` is None AND the request file is absent or unparseable → the gate record is UNVERIFIABLE, not clean. The continue is REFUSED with disposition `"continue-rejected-unverifiable-gates"`. This flips G2 fail-closed.

### Legacy/edge plan behavior

Plans predating gate recording (pre-May-2026) that genuinely lack both sources: their continue is refused with a named disposition. This is correct — a plan that cannot prove its gates passed should not advance silently. The CEO can issue a stop verdict and re-plan through the modern pipeline, or the override tool (D-3) can mark specific gates overridden before re-issuing the continue.

Parked plans from the pre-id-native era: 44 parked arcs exist. Those with slug-only names (e.g., `foo-bar-2026-05-01`) have `_lc_plan_id = None`. Their resume path falls to the request-file fallback. If the request file is present (the normal case — it persists in `verdicts/pending/` until consumed), the gate re-check works. If someone manually deleted the request file, the plan is unverifiable → refused.

### Re-derivable gates post-teardown

Against the merged tree (post-teardown), a subset of gates are THEORETICALLY re-derivable:

- **`deposit_exists`** (gates.py:405-440): checks file presence. After teardown + merge, the deposit is on main. However: a file legitimately moved or renamed between step-end and consumption reads as a new failure. **Not worth the drift risk.**
- **All other gates** (`receipt_status`, `no_errors`, `no_permission_denials`, `scope_check`, `rule_20_self_check`, `rule_22_verification`, `qa_test_result`): require the agent's parsed output — unavailable post-teardown.

**Decision: consume the RECORDED result only. No re-derivation.** The drift risk outweighs the marginal safety gain. The recorded result was correct at step-execution time; re-derivation against a potentially-mutated tree introduces false positives.

### Insertion point in `_consume_verdicts`

The new check inserts at bellows.py:2576, INSIDE the `if v == "continue":` branch, AFTER `record_verdict_outcome` at :2574 and BEFORE the existing worktree_teardown guard at :2581.

**Order of operations (post-E4):**
1. `:2574` — `record_verdict_outcome(_lc_plan_id, step_number, v, ...)` — records that a verdict was received (unchanged)
2. **NEW** — gate re-check: query gate_events / inspect gate_result. If unoverridden failures found and not a precondition-failure retry (D-4), → D-2 disposition. `record_verdict_outcome` is called AGAIN with outcome `"continue-rejected"` to overwrite the initial `"continue"` row, preserving the audit trail: received → refused.
3. `:2581` — worktree_teardown guard (PRESERVED as a distinct arm). The worktree_teardown check is now redundant with the general check BUT has a distinct halted-routing disposition. **Keep as a distinct arm** — the "commits not landed" operational severity warrants its own routing to halted + R2 recovery, separate from the general "reject and leave pending" disposition.
4. `:2599+` — normal continue advancement (unchanged)

### Interaction with `record_verdict_outcome` at :2574

The initial `record_verdict_outcome` fires BEFORE any conditioning (unchanged — backward compatibility for the audit trail). If the continue is subsequently rejected, a SECOND `record_verdict_outcome` call overwrites the pending row with outcome `"continue-rejected"` and `disposition_summary` naming the refusing gates. The `UPDATE ... WHERE outcome IS NULL` predicate (lifecycle.py:579) is replaced with `UPDATE ... WHERE plan_id = ? AND step_number = ? ORDER BY id DESC LIMIT 1` to allow overwriting the initial recording. Alternatively, the initial recording could be deferred — but that changes the existing behavior for stop verdicts and clean continues. **Decision: keep the initial recording, overwrite on rejection.**

---

## D-2 — The Refusal Disposition

### Decision: reject-and-leave-pending

A `continue` verdict on unoverridden failed gates (other than `worktree_teardown`, which retains its distinct halted-routing disposition) is handled as:

1. **Reject** — the continue does NOT advance the plan.
2. **Leave pending** — the plan stays in `verdict-pending-` state.
3. **Rename verdict file** — the consumed verdict file is renamed from `verdict-{slug}-step-{N}.md` to `rejected-verdict-{slug}-step-{N}.md` in `verdicts/resolved/`. This prevents the scanner from re-processing it on the next poll. The `rejected-` prefix is excluded by the existing `fname.startswith("verdict-")` filter at bellows.py:2499 — wait, that WOULD match `rejected-verdict-`. So: move the rejected file to `verdicts/resolved/processed-{fname}` (the existing processed pattern at bellows.py:2673), which is already excluded from re-scan.
4. **Log to ledger** — `verdict.log_to_ledger(...)` with action `"continue-rejected-gate-failure"` and the failing gates named in the reason.
5. **Record lifecycle** — `record_verdict_outcome` with outcome `"continue-rejected"` and `disposition_summary` listing the unoverridden failing gates.
6. **Notify** — push notification: "Continue rejected on {plan_slug} step {N}: unoverridden gate failures: {gate_names}. Override with clear_plan.py --override-gate, or issue stop."

### Idempotency

The scanner loops (`_consume_verdicts` runs on every poll). The rejection renames the verdict file to `processed-{fname}` on the FIRST pass. Subsequent polls do not see it (already processed). One rejection, one notification, no log storm. The plan stays `verdict-pending-` so the Planner can act.

### Planner's next moves after rejection

1. **Override and re-issue:** Use the override tool (D-3) to mark specific gate failures as overridden, then write a new verdict file. The next poll sees the new verdict, re-checks gates, finds all failures overridden, and advances.
2. **Issue a corrective plan:** Stop the current plan, create a new plan to fix the underlying issue.
3. **Issue a stop verdict:** Write `stop` — never conditioned by E4, routes to halted as always.

### Why not route-to-halted

The worktree_teardown precedent routes to halted because "commits not landed" is operationally irreversible without R2 manual recovery. Other gate failures (scope_check, deposit_exists, etc.) are commonly false positives — the evidence-path class from exec-493. Routing to halted on every false positive would create unnecessary operational overhead. Reject-and-leave-pending gives the Planner a chance to override without manual recovery.

### Costs

- The plan stays in `verdict-pending-` state until the Planner acts. This is visible in the daemon's status output.
- If the Planner never acts, the plan sits indefinitely. This is acceptable — it's the same behavior as a verdict-pending plan where the CEO hasn't written a verdict yet.

---

## D-3 — The Override Arm (Benign-Failure Workflow Under Enforcement)

### Decision: separate gated override tool (option b)

A new subcommand of `tools/clear_plan.py`:

```
python tools/clear_plan.py --override-gate <plan-slug-or-path> \
    --gate <gate_name> --ref "<justification>"
```

This is a deliberate second act — the `--release-class-hold` precedent (clear_plan.py:75-129). The Planner (or CEO) runs it BEFORE writing the continue verdict, or after the first continue is rejected.

### Mechanism

1. **Locate the gate_events row:** query `gate_events` for the step's fail row matching `gate_name`.
2. **Require the row exists:** no phantom overrides — the gate must have actually failed at step-execution time.
3. **Write the override:** `UPDATE gate_events SET overridden = 1, override_ref = ? WHERE id = ?`.
4. **Log:** print confirmation with gate name, plan slug, step, and override_ref.

### Why this satisfies fork 5

Fork 5: "verdict files stay plain." The override tool writes to the DB, not the verdict file. The verdict file remains a plain `continue` or `stop` with optional human-authored reasoning. No embedded exit codes, no structured override declarations. **The boundary is unambiguous: the verdict file is never touched by the override mechanism.**

### Why not option (a) — override line in verdict file

An override line (`override: scope_check — false positive per evidence-path pattern`) would be human-authored judgment, not a checker exit code. Whether this violates "verdict files stay plain" is an interpretive question. Option (b) avoids the question entirely. If a future simplification wants to fold the override into the verdict file, the ruling in D-7 would be needed.

### Why not option (c) — benign-class allowlist in config

A config allowlist (`benign_gate_failures: [scope_check, deposit_exists]`) creates the shop's invisible-when-incomplete problem: gates not on the list are silently blocked; the list's absence is indistinguishable from "all gates are blocking." The drift risk is unacceptable for a safety mechanism.

### G3's dead columns come alive

The override tool is the FIRST WRITER of `gate_events.overridden` and `gate_events.override_ref`. After E4:

- **Writers of `overridden`:** `tools/clear_plan.py --override-gate` (sets to 1) + `lifecycle.record_gate_events` (records initial 0, or echoes 1 if `gate_result` dict carries it — the future path for programmatic overrides).
- **Writers of `override_ref`:** `tools/clear_plan.py --override-gate` (sets to justification string).
- **Readers of `overridden`:** the D-1 consumption check (`WHERE result = 'fail' AND overridden = 0` filters out overridden failures).

The audit trail: `gate_events` records WHO overrode WHAT, with the `override_ref` capturing WHY. Discoverable via `SELECT * FROM gate_events WHERE overridden = 1`.

### The no-lifecycle-identity arm

For slug-only plans (`_lc_plan_id = None`), `gate_events` has no rows (step_id requires plan_id). The override tool cannot write to a row that doesn't exist. **These plans cannot use the DB-backed override mechanism.**

Fallback for slug-only plans: the override is encoded in the request file's `Gate Result JSON` — add `"overridden": true` to the failure dict. This is file mutation, which is fragile but acceptable for the legacy case. Alternatively: slug-only plans cannot override and must use stop + re-plan through the modern pipeline. Given that all new plans are id-native (the id_sequence is at 517), the legacy case is vanishingly rare.

**Decision:** slug-only plans fall back to the request-file override path. The override tool edits the `Gate Result JSON` in the pending request file when no DB identity exists. This keeps both paths working without forcing a re-plan.

---

## D-4 — Interaction with Existing Flows

### gate_auto advancement (bellows.py:1136, :1293)

Already gated on clean gates — `gate_auto` only fires when `gate_result["passed"]` is True (the while-loop and auto-close paths both check `gate_result["passed"]` before entering their respective branches). The E4 check fires ONLY in `_consume_verdicts`, not in `run_plan`. **Unaffected.**

### Precondition-failure retry (bellows.py:2641-2646)

When `precondition_failure_from_request` is True, the Planner's continue means "retry the step" — the step never ran, so the gate results reflect the precondition failure (e.g., `worktree_creation` at bellows.py:995), not the step's output. Retrying the step will produce fresh gate results.

**Decision: the E4 gate re-check is SKIPPED when `precondition_failure_from_request` is True.** The check inserts BEFORE the precondition-failure branch at :2641. The skip is explicit: `if precondition_failure_from_request: # E4 skipped — precondition failure, step will be retried with fresh gates`. This preserves the existing retry workflow.

### Stop verdicts (bellows.py:2648-2662)

Never conditioned by E4. A stop on failed gates is the system working — the Planner saw the failures and chose to halt. The E4 check is inside `if v == "continue":` and does not touch the `else:` (stop) branch. **Unaffected.**

### Auto_close path (bellows.py:1262-1266)

Only fires when `gate_result["passed"]` is True AND `effective_auto_close` is True. No failed gates reach this path. **Unaffected.**

### Orphan-verdict reconciliation (the no-match WARN path)

Fires when no `verdict-pending-` plan matches the verdict's slug (bellows.py post-:2663, the `if not plan_matched:` branch). The E4 check is INSIDE the `plan_matched` block. **Unaffected.**

### E3's retirement calls (bellows.py:2596, :2630, :2660)

Fixed landmarks. The E4 check fires early in the `v == "continue"` branch (at :2576, before :2581). If the continue is rejected (D-2), execution breaks out before reaching any retirement call. If the continue advances (clean gates or all overridden), the retirement calls fire at their existing positions. **Byte-identical — the executable must not edit these three lines.**

### The no-lifecycle-identity arm

`_lc_plan_id` is None for any slug that doesn't match `r"(?:(?:diagnostic|executable|qa)-)?(\d+)"` (bellows.py:2572-2573). This affects:

1. **gate_events query:** no plan_id → no step_id → no gate_events rows. The D-1 primary source is unavailable. Falls to the request-file fallback.
2. **Override tool:** cannot write to gate_events without a row to update. Falls to the request-file override path (D-3).
3. **record_verdict_outcome:** `_lc_plan_id = None` → the call is a no-op (lifecycle.py:572-573). The outcome is recorded only in the ledger (verdict.log_to_ledger), not the lifecycle DB.

**Which plans present this shape today:** any slug-only plan — `foo-bar-2026-05-01` style. All 44 parked arcs predate the id-native era (id_sequence started at 1, is now at 517). A parked arc resumed as `verdict-pending-` would present this shape. The request-file fallback handles it.

**A DB-backed fail-closed check would refuse EVERY legacy plan's continue unconditionally.** This is why the dual-source design (D-1) exists — the request-file fallback preserves the legacy path while the DB path handles the modern case.

---

## D-5 — Activation + Coordination

### Inertness

The change is daemon code. INERT until the daemon process restarts. The pending restart ALSO activates E3's `_retire_receipts` (bellows.py:2596/:2630/:2660) — one deliberate restart, two arcs' activation.

### Shared-file fence

`bellows.py` was modified under E3 this same session day (2026-08-24). The E4 executable X-pins the blob hash:

**bellows.py blob:** `ae26abf741a42827bb956cb4083cc2f12fea9dc9`

The executable HALTs on drift — if `git hash-object bellows.py` at execution time does not match the X-pin, the step fails with a named disposition. This prevents the executable from applying a patch against a file that has moved under it.

### Post-restart canary — E4

**Canary:** a `continue` verdict on a synthetic failed-gate verdict-request → observe the refusal disposition.

**Construction (safe-if-misfired, safe-in-construction):**

A synthetic verdict-pending plan + request + verdict trio placed in a **dedicated scratch watched dir** (not a production watched dir). The scratch dir:

1. Create `<tmp>/canary-e4/knowledge/decisions/` structure.
2. Add the scratch dir to `config.json` `watched_projects` before restart.
3. Place the synthetic trio:
   - `verdict-pending-diagnostic-canary-e4.md` (single-step plan text)
   - `verdicts/pending/verdict-request-canary-e4-step-1.md` with `Gate Result JSON: {"failures": [{"gate": "scope_check", "evidence": "canary synthetic failure"}], "files_changed": []}` and `Pause Reason Code: gate_failure`
   - `verdicts/resolved/verdict-canary-e4-step-1.md` with content `continue\nCanary: testing E4 refusal`
4. Restart daemon.
5. Observe:
   - **Expected (E4 working):** the continue is rejected. The verdict file moves to `processed-`. The plan stays `verdict-pending-`. Notification fires naming `scope_check`.
   - **Misfired (E4 not working):** the continue advances. `handle_new_plan` runs on step 2 of a plan with no step 2 → plan moves to Done. **Safe:** the canary plan is in the scratch dir, no real work is dispatched. The scratch dir is removed from config after the canary window.

**Daemon outcomes enumerated:**
- Advance (clean gates pre-E4): plan moves to in-progress → handle_new_plan → no step 2 → Done. Harmless in scratch dir.
- Halt (worktree_teardown): impossible — the synthetic gate_result has scope_check, not worktree_teardown.
- Reject (E4): the expected outcome. Plan stays verdict-pending. Harmless.
- Retire receipts: fires on plan close (Done or halted). If advance-to-Done occurs (misfired), retirement looks for receipts for the canary plan — none exist. No-op. Harmless.

All outcomes harmless under the scratch dir isolation.

### Post-restart canary — E3

**Canary:** a plan close in any watched dir → observe receipt retirement.

This canary is simpler: it's observable from any plan that closes (moves to Done or halts) after restart. The first real plan close post-restart will exercise `_retire_receipts`. If no plan closes during the canary window, a synthetic plan-close in the scratch dir can be used (a verdict-pending plan with a `continue` on clean gates → Done → retirement fires).

**Safe-if-misfired:** if retirement doesn't work, receipts remain in `receipts/` instead of `receipts/archived/`. No operational impact — receipts are informational.

### Canary sequence

1. Add scratch dir to config.
2. Place E4 canary trio.
3. Restart daemon.
4. Wait for poll cycle (≤30 seconds).
5. Verify E4 canary: check that `verdict-pending-diagnostic-canary-e4.md` still exists AND the verdict file is processed.
6. For E3 canary: observe the next real plan close, or place a clean-gate canary in the scratch dir.
7. Remove scratch dir from config. Clean up scratch dir.

---

## D-6 — Test Plan

### Baseline

`tests/test_consume_verdicts.py`: **20 tests** (G7). Full suite: **1325 tests** (G8).

### New tests (7)

| # | test name | what it verifies |
|---|---|---|
| 1 | `test_continue_rejected_on_unoverridden_gate_failure` | continue + gate_result with `scope_check` failure (not overridden) → plan stays `verdict-pending-`, verdict file processed, ledger action `"continue-rejected-gate-failure"` |
| 2 | `test_continue_allowed_on_overridden_gate_failure` | continue + gate_result with `scope_check` failure marked `"overridden": true` → plan advances normally |
| 3 | `test_absent_request_and_absent_gate_events_fail_closed` | no request file, `_lc_plan_id = None` → continue refused with `"continue-rejected-unverifiable-gates"` |
| 4 | `test_precondition_failure_skips_gate_recheck` | `precondition_failure=True` + gate_result with failures → continue allowed (retry), resume_step = same step |
| 5 | `test_stop_unaffected_by_gate_recheck` | stop verdict + gate_result with failures → routes to halted normally (E4 does not condition stops) |
| 6 | `test_scanner_loop_exception_containment` | a gate re-check that raises an exception → the exception is caught, that plan's verdict is skipped with a WARN, other plans' consumption is not stalled |
| 7 | `test_continue_on_clean_gates_with_gate_recheck` | clean gate_result (no failures) + continue → advances normally (the E4 check does not false-trip on clean gates) |

### Existing tests that change (2)

| test | current behavior | E4 behavior | change |
|---|---|---|---|
| `test_consume_verdicts_parses_gate_result_json_continue_to_done` (line 525) | Passes gate_data with `{"failures": [{"gate": "scope_check", "evidence": "out-of-scope"}]}`, expects continue → Done | Under E4, the unoverridden scope_check failure triggers rejection | Update gate_data to mark the failure as `"overridden": true`, OR change the test expectation to rejection, OR use a clean gate_result. **Recommendation:** split into two tests — one with clean gates (advances), one with unoverridden failure (rejected) |
| `test_consume_verdicts_parses_gate_result_json_continue_resume` (line 583) | Passes gate_data with `{"failures": [{"gate": "deposit_exists", "evidence": "missing deposit"}]}`, expects continue → resume | Same issue as above | Same resolution: split or mark overridden |

### Existing tests that must pass unchanged (18)

All other 18 tests in the file are unaffected:
- Tests with clean gate results → no failures → E4 check passes → behavior unchanged
- Tests with worktree_teardown failures → the teardown guard fires BEFORE the general E4 check → behavior unchanged
- Stop verdict tests → E4 doesn't condition stops → behavior unchanged
- Slug normalization, orphan reconciliation, startup sweep tests → don't touch the continue conditioning path

### Full suite assertion

The 1325-test suite stays green. The 1305 tests outside `test_consume_verdicts.py` do not exercise `_consume_verdicts` directly.

---

## D-7 — Open Questions

**No new CEO ruling is required.** The design chose the separate override tool (D-3, option b) specifically to avoid testing the boundary of "verdict files stay plain." The verdict file is never touched by the override mechanism; fork 5 is unambiguously satisfied.

**If the override arm's shape ever changes** from (b) separate tool to (a) verdict-file override line, a ruling IS needed on whether a human-authored override line (e.g., `override: scope_check — false positive per evidence-path pattern`) violates "verdict files stay plain." The ruling's original target was embedded checker exit codes; a human judgment line is a different beast. **This question is PARKED, not decided — it arises only if the tool-based approach proves operationally untenable.**

---

## Rule 27 Gap Table — Executable Change Sites

Every code-change site the E4 executable will touch, with file:line:

| # | file | line(s) | change | disposition on failure |
|---|---|---|---|---|
| 1 | bellows.py | :2570 | Fail-closed flip: `gate_result = gate_result_from_request or {"failures": [], "files_changed": []}` → when BOTH gate_events AND request file are absent, refuse the continue instead of defaulting to clean | Fails toward not-advancing (refuse). Cannot crash the scanner loop (wrapped in try/except at the same level as existing checks) |
| 2 | bellows.py | :2576 (insert) | New gate re-check block: query gate_events for unoverridden fail rows (primary) or inspect gate_result_from_request failures (fallback). If unoverridden failures found and not precondition_failure → D-2 disposition | Fails toward not-advancing (reject-and-leave-pending). Exception in the check → caught, WARN logged, that plan's verdict skipped, scanner continues to next file |
| 3 | bellows.py | :2574 | Add second `record_verdict_outcome` call with `"continue-rejected"` on the rejection path. Requires changing the UPDATE predicate in lifecycle.py to allow overwriting | Fails toward audit-trail gap (non-fatal — the ledger still records the rejection) |
| 4 | lifecycle.py | :577-581 | Update `record_verdict_outcome` UPDATE predicate to allow overwriting an initial recording with a rejection outcome | Non-fatal if skipped — existing predicate would leave the initial "continue" row, which is misleading but not dangerous |
| 5 | lifecycle.py | NEW function | `get_gate_failures_for_step(plan_id, step_number)` → query gate_events for unoverridden fail rows. Returns list of `{"gate": str, "evidence": str}` or None if no rows exist | Pure read. Non-fatal if it raises — the caller falls back to the request-file source |
| 6 | tools/clear_plan.py | NEW subcommand | `--override-gate` subcommand: locates gate_events row, writes `overridden=1, override_ref`, logs. Falls back to request-file edit for slug-only plans | Non-fatal — the tool is a human-initiated act, errors are visible in the terminal |
| 7 | tests/test_consume_verdicts.py | NEW tests + 2 updates | 7 new tests, 2 existing tests updated (see D-6) | Test-only |

### Lines the executable MUST NOT edit (byte-identical landmarks)

| file | line(s) | reason |
|---|---|---|
| bellows.py | :2596 | `_retire_receipts(_lc_plan_id)` — E3 landmark (worktree_teardown halted path) |
| bellows.py | :2630 | `_retire_receipts(_lc_plan_id)` — E3 landmark (continue-to-done path) |
| bellows.py | :2660 | `_retire_receipts(_lc_plan_id)` — E3 landmark (stop/halted path) |

---

## Summary of Decisions

| decision | chosen | defended against |
|---|---|---|
| D-1 re-check source | Dual: gate_events primary, request-file fallback, fail-closed on both absent | (a) request-file only (deletable, G2), (b) gate_events only (no legacy support), (c) both-must-agree (too strict, breaks when one source is absent) |
| D-1 re-derivation | None — consume recorded result only | Re-deriving deposit_exists against merged tree (drift risk) |
| D-1 insertion point | bellows.py:2576, after record_verdict_outcome, before worktree_teardown guard | After worktree_teardown guard (would skip the re-check for teardown failures) |
| D-1 teardown guard | Kept as distinct arm with halted-routing disposition | Subsumed by general check (loses the R2 recovery routing) |
| D-2 disposition | Reject-and-leave-pending | Route-to-halted (too aggressive for false positives) |
| D-3 override mechanism | Separate gated override tool (clear_plan.py --override-gate) | (a) verdict-file override line (uncertain "plain" boundary), (c) config allowlist (drift risk) |
| D-3 no-identity fallback | Request-file override for slug-only plans | Refuse all slug-only overrides (too restrictive for legacy plans) |
| D-4 precondition_failure | E4 check SKIPPED when precondition_failure=True | Checking precondition-failure gates (would block every retry) |
| D-5 canary | Scratch dir isolation + enumerate all daemon outcomes | Production dir canary (incident-mandate class risk) |
