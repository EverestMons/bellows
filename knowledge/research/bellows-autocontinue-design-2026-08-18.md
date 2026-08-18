# Auto-continue-unless-errors: QA-result gate + `on_failure` pause mode — Design Document

**Type:** Design (scoping diagnostic deposit)
**Plan:** 437
**Created:** 2026-08-18
**Status:** Design resolved — ready for executable implementation

---

## CEO Decisions (settled, fixed constraints)

- **D1 — Bellows-native.** The daemon itself auto-continues; the daemon's existing pause+notify-on-failure IS the "watcher." No external per-plan watcher process.
- **D2 — Default for all plans.** `on_failure` becomes the PLANNER_TEMPLATE default; the Planner opts OUT (e.g. `pause_for_verdict: always`) for high-stakes tranche/money plans.
- **D3 — Clean final QA auto-closes.** A clean final QA auto-closes to Done unattended, but `notify_plan_complete` still fires so the CEO sees the ship.

---

## Verified Findings at HEAD (2026-08-18)

### F1 — The daemon already auto-continues clean non-QA steps
`bellows.py:1032` — "All gates passed and not QA — continue to next step", recording `clean_gate_auto` + `continue` (`decided_by='gate_auto'`) at lines 1034–1036. The auto-continue machinery exists.

### F2 — The pause trigger set (three conditions + header)
`bellows.py:993–996` (non-final while-loop):
```python
if (not gate_result["passed"]
        or gate_result["is_qa_step"]
        or gate_result.get("verdict_requested", {}).get("requested", False)
        or header_says_pause(header, current_step, total_steps, gate_result["is_qa_step"])):
```
Mirrored at `:1117–1121` (final-step) with `or not effective_auto_close` added. **`is_qa_step` is an UNCONDITIONAL pause trigger — independent of pause mode.** No mode auto-continues a clean QA step today.

### F3 — The four pause modes
`header_says_pause` at `bellows.py:627–641`; `RECOGNIZED_PAUSE_TOKENS` at `scripts/plan_lint.py:28`:
- `always` — pause every step
- `after_step_1` — pause only on step 1
- `after_qa_step` — pause on QA steps (redundant with `is_qa_step` unconditional trigger)
- `qa_and_terminal` — pause on QA or final step

**None auto-continue a clean QA/terminal step.**

### F4 — THE SAFETY GAP: QA gates check structure, not test substance
`gates.check()` at `gates.py:210–236` runs: `_gate_receipt_status`, `_gate_no_errors`, `_gate_no_permission_denials`, `_gate_deposit_exists`, `_gate_is_qa_step` (informational), `_gate_rule_20_self_check` (banner + PASSED line presence), `_gate_rule_22_verification`, `_gate_file_change_audit` (informational), `_gate_scope_check`.

**NONE parse the pytest summary line.** A QA step can pass every gate while its evidence file shows "2 failed / 2738 passed" — the regression read is done only by the Planner, manually. Auto-continuing clean QA without a new substantive gate risks auto-shipping a regression.

### F5 — Gate failure always pauses + notifies
On pause the daemon posts a verdict-request AND fires `notifier.notify_verdict_request` (`bellows.py:1024–1026`). This IS the "surface errors to handle" channel — no new notifier needed.

### F6 — Sparse-header default is `after_step_1`
`_apply_defensive_header_defaults` at `bellows.py:644–653` defaults sparse multi-step headers to `after_step_1`. Applied at `:773` (pre-run) and `:988` (mid-run header re-read). `plan_lint` check (a) at `scripts/plan_lint.py:198–203` validates against `RECOGNIZED_PAUSE_TOKENS` (line 28). Both must change under D2.

### F7 — The terminal is governed by a SEPARATE `auto_close` header, and `is_qa_step` guards THREE sites
The three condition sites:
1. **`:993–996`** — non-final while-loop pause check (`or gate_result["is_qa_step"]`)
2. **`:1117–1121`** — final-step pause check (`or gate_result["is_qa_step"]` + `or not effective_auto_close`)
3. **`:1162–1166`** — auto-close exclusion (`and not gate_result["is_qa_step"]`)

`effective_auto_close` computed at `:989`: `str(header.get("auto_close", "false")).lower() == "true"` — independent of `pause_for_verdict`. A final QA step NEVER auto-closes today, even with `auto_close: true`.

Display-only `_pause_reason` branches at `:1003` and `:1128` — no condition change needed.
Worktree-failure default at `:898` (`is_qa_step=False`) — irrelevant.

### F8 — SAFETY INVARIANT (coupling, three-legged)
Dropping `is_qa_step` from the pause sets is safe ONLY because:
1. The new QA-result gate makes a regression fail `gate_result["passed"]` → pause via the always-on first condition
2. The `is_qa_step` drop is mode-guarded (`on_failure` only) — other modes untouched
3. Correct `is_qa_step` DETECTION is lint-enforced as a FAIL — a mis-declared QA step evades the gate

All three legs MUST ship in the same executable.

---

## Resolved Design Questions

### Q1 — QA-result gate: baseline source

**Recommendation (for CEO fork A):** Start with `known_failures: <int>` plan-header field (low-friction interim). The gate parses the pytest summary line from the QA evidence file and fails iff `failures > known_failures` (default 0). A per-project `.bellows-baseline` node-id file is the precise long-term target but adds authoring friction and parser complexity — defer to a follow-up plan.

**Gate parse logic:**
- Locate the last pytest summary line matching: `r'=+\s*(?:(\d+)\s+failed\s*,\s*)?(\d+)\s+passed'`
- Extract `failed` count (default 0 if group absent)
- Compare against `known_failures` from plan header (default 0)
- `failed > known_failures` → gate FAILS, `gate_result["passed"] = False`

**CEO Fork A surfaces:** header-field-only (recommended) vs `.bellows-baseline` node-id file (precise, deferred).

### Q2 — Evidence file path resolution

The QA step already declares deposits via `required_evidence_files` + `evidence_dir` in its Rule 20 context and Deposits block. The QA-result gate reuses `_gate_rule_20_self_check`'s deposit resolution path:
1. Extract deposit paths from plan step's `**Deposits:**` block via `_extract_plan_required_deposits`
2. Resolve via `_resolve_deposit_path(path, project_path, wt_path=wt_path)`
3. Read the resolved file and grep the last `=====` pytest summary line

**Summary-line regex:** `r'=+\s*(?:(\d+)\s+failed\s*,?\s*)?(\d+)\s+passed'`

**No-summary-line behavior:** FAIL CLOSED. A QA step claiming tests but producing no parseable pytest result must PAUSE, never auto-continue. This is the fail-closed invariant of the mode — QA auto-continues ONLY on a proven-clean test result.

### Q3 — The new `on_failure` pause mode (three sites)

Add `on_failure` to:
- `RECOGNIZED_PAUSE_TOKENS` in `scripts/plan_lint.py:28`
- `header_says_pause` in `bellows.py:627`: add branch `if pv == "on_failure": return False` (clean steps never pause from header alone under this mode)

Drop `is_qa_step` unconditional trigger WHEN `mode == on_failure` at all three sites:

**Site 1 — non-final while-loop (`bellows.py:993–996`):**
```python
if (not gate_result["passed"]
        or (gate_result["is_qa_step"] and header.get("pause_for_verdict") != "on_failure")
        or gate_result.get("verdict_requested", {}).get("requested", False)
        or header_says_pause(header, current_step, total_steps, gate_result["is_qa_step"])):
```

**Site 2 — final-step pause (`bellows.py:1117–1121`):**
```python
if (not gate_result["passed"]
        or (gate_result["is_qa_step"] and header.get("pause_for_verdict") != "on_failure")
        or gate_result.get("verdict_requested", {}).get("requested", False)
        or header_says_pause(header, current_step, total_steps, gate_result["is_qa_step"])
        or not effective_auto_close):
```

**Site 3 — auto-close exclusion (`bellows.py:1162–1166`):**
```python
if (gate_result["passed"]
        and (not gate_result["is_qa_step"] or header.get("pause_for_verdict") == "on_failure")
        and not header_says_pause(header, current_step, total_steps, gate_result["is_qa_step"])
        and not gate_result.get("verdict_requested", {}).get("requested", False)
        and effective_auto_close):
```

The `not gate_result["passed"]` condition remains always-on — a QA regression (caught by the new QA-result gate) still pauses regardless of mode.

### Q4 — Terminal auto-close coordination (D3)

`on_failure` IMPLIES `effective_auto_close`. One edit at `bellows.py:989`:

```python
effective_auto_close = (
    str(header.get("auto_close", "false")).lower() == "true"
    or header.get("pause_for_verdict") == "on_failure"
)
```

One header (`pause_for_verdict: on_failure`) controls both behaviors — no pairing footgun.

The clean-final auto-close path fires `notifier.notify_plan_complete(plan_name, total_cost)` at `bellows.py:1206` — confirmed. The ship notification is visible under D3.

### Q5 — The no-test-QA hole

Under `on_failure`, if `is_qa_step` is true and no parseable test result exists in the evidence file, FAIL CLOSED to a pause. The QA-result gate's "no summary line found" case already handles this (Q2).

A QA step that declares NO test evidence (doc/DB plans) hits the same fail-closed path — it has no parseable pytest result, so the gate fails, and the step pauses. This is the safe default.

**CEO Fork B surfaces:** fail-closed for all no-test-result QA (recommended, safe) vs allow-auto-continue for explicitly declared doc/DB QA. Deciding fail-closed means doc-only plans keep a terminal pause unless they opt into a lighter mode (`after_step_1`).

### Q6 — Doctrine changes (D2)

PLANNER_TEMPLATE edits:
1. Default `pause_for_verdict` → `on_failure` (replace current default guidance)
2. Opt-OUT guidance: tranche/money/high-stakes → `always` (cite plan 203's rote-step-1 catch as the precedent for when manual review earns its price)
3. Sparse-header default: `_apply_defensive_header_defaults` at `bellows.py:652` — change from `after_step_1` to `on_failure`
4. `plan_lint` check (a) — add `on_failure` to `RECOGNIZED_PAUSE_TOKENS` at `scripts/plan_lint.py:28`
5. `plan_lint` check 9 (multi-step diagnostic forced to `always`) — relax to DEFAULT `on_failure`, with `always` available as an opt-in for high-stakes diagnostics

### Q7 — Backward compatibility

Existing `always`/`after_step_1`/`after_qa_step`/`qa_and_terminal` plans are **unaffected**:
- The new `on_failure` token is additive — `header_says_pause` returns False for it, no existing branch touched
- The `is_qa_step` unconditional drop is guarded by `header.get("pause_for_verdict") != "on_failure"` — other modes retain the unconditional `is_qa_step` pause
- The `effective_auto_close` implication is `or`-ed — existing `auto_close: true` behavior unchanged; existing `auto_close` absent/false behavior unchanged for non-`on_failure` modes
- The QA-result gate runs inside `_gate_rule_20_self_check` flow (or as a new sibling gate) — it's additive; it only causes failures, never removes them

### Q8 — `is_qa_step` detection is now safety-critical

Under `on_failure`, the QA-result gate only runs where `_gate_is_qa_step` fires. A **mis-declared** QA step (missing from `qa_steps`, no QA heading) auto-continues with NO test check — reopening F4.

`qa_and_terminal` guards this with a WARN at `scripts/plan_lint.py:410–416`. Under `on_failure` the same check must be a **FAIL**:

```python
if header and header.get("pause_for_verdict") == "on_failure":
    qs_raw = header.get("qa_steps", "")
    qs_set = _parse_qa_steps(qs_raw) if qs_raw else set()
    if not qs_set:
        # Under on_failure, mis-declared QA auto-ships unchecked — FAIL, not WARN
        results.append(("FAIL", "(i) on_failure qa_steps", "pause_for_verdict=on_failure requires a parseable qa_steps field"))
        all_passed = False
```

This makes correct QA-step declaration a hard precondition of the mode.

---

## CEO Forks Summary

| Fork | Question | Options | Planner lean |
|------|----------|---------|--------------|
| **A** | QA-result baseline source (Q1) | `known_failures: N` header field (low-friction) vs `.bellows-baseline` node-id file (precise) | Header field now, node-id file later |
| **B** | No-test-QA under `on_failure` (Q5) | Fail-closed to pause (safe) vs allow-auto-continue for declared doc/DB QA | Fail-closed |
| **C** | Rollout (D2) | Flip default immediately vs canary window (run `on_failure` on N low-stakes plans, measure catch rate, then flip) | Canary given F4's blast radius |

---

## Executable Step Plan

The downstream executable implements this design verbatim. Suggested step decomposition:

**Step 1 — QA-result gate implementation**
- Add `_gate_qa_test_result(is_qa_step, plan_text, step_number, project_path, parsed, failures, wt_path, plan_header)` to `gates.py`
- Parse the last pytest summary line from the first `.md` deposit
- Fail if `failed > known_failures` (from header, default 0)
- Fail-closed if no parseable summary line and `is_qa_step`
- Wire into `gates.check()` after `_gate_rule_20_self_check`

**Step 2 — `on_failure` mode + three-site edit**
- Add `on_failure` to `RECOGNIZED_PAUSE_TOKENS` in `scripts/plan_lint.py:28`
- Add `on_failure` branch to `header_says_pause` in `bellows.py:627`
- Guard `is_qa_step` at all three condition sites (`:994`, `:1118`, `:1163`) with `and header.get("pause_for_verdict") != "on_failure"`
- Compute `effective_auto_close` with `or header.get("pause_for_verdict") == "on_failure"` at `:989`
- Add `on_failure` FAIL branch to `plan_lint` check (i) at `:410–416`

**Step 3 — Doctrine + defaults**
- Update PLANNER_TEMPLATE: default `pause_for_verdict` → `on_failure`, opt-out guidance
- Update `_apply_defensive_header_defaults` sparse default from `after_step_1` to `on_failure`
- Relax `plan_lint` check 9 for multi-step diagnostics

**Step 4 — QA (full test suite + canary)**
- Run full test suite with the changes
- Verify backward compatibility: existing plans with `always`/`after_step_1`/`after_qa_step`/`qa_and_terminal` are unaffected
- Verify the QA-result gate correctly parses pytest summary lines
- Verify fail-closed behavior for no-summary-line QA steps
- Verify the three-site `is_qa_step` guard under `on_failure`
- Canary: run `on_failure` on a low-stakes plan and confirm the auto-continue fires

---

## Safety Notes for the Executable's Cold Seat

The cold seat's primary targets:
1. **QA-result gate parse logic** — the regex must match ALL pytest summary formats (including `no tests ran`, `X error`, `X xfailed`, etc.) and FAIL CLOSED on any unrecognized format
2. **The coupling invariant (F8)** — the `is_qa_step` drop and the QA-result gate MUST ship in the same commit; verify both are present in every intermediate state
3. **QA-step detection correctness (Q8)** — the `plan_lint` FAIL branch for `on_failure` without `qa_steps` must block plan claim, not just warn
4. **Three-site completeness** — verify `:994`, `:1118`, `:1163` are ALL guarded; a missed site auto-ships regressions under `on_failure`
