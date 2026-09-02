# bellows — executable: A PAUSE IS A STATE — write `awaiting_verdict` to the plan row at every verdict pause and restore `in_progress` on resume; widen the four in-flight predicates that would otherwise stop seeing a paused plan; the gate_watcher PUSHES the pause it already detects

**Date:** 2026-09-01 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** targeted (`tests/test_gate_watcher.py`, `tests/test_status.py`, `tests/test_depositor.py`, `tests/test_reconcile_plan.py`, `tests/test_lifecycle.py` + a NEW `tests/test_verdict_signal.py`) + a full-suite CONTROL COMPARISON against the named 10-failure baseline | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always | **known_failures:** 10 | **Priority:** 1

**auto_close:** false

**Slug:** `verdict-signal-2026-09-01`

**Depends on:** the CEO's "Let's do this work now as it affects automaticity of plan queuing" (2026-09-01, session `1663ee38`, after the diagnosis of plan 100008's two unpaged pauses — **the citable authorization for this plan and, once the cycle closes clean and the depositor's gates pass, for the release of its shop-infra hold**); `knowledge/decisions/Done/executable-100005.md` (clone origin BY KIND — the mini's newest bellows code plan, Done 2026-08-31: interpreter resolver, pins re-derived by DEV, targeted tests + full-suite control comparison, mutants as STOPs); `LESSONS.md` 2026-08-18 (*a watcher must key on the signal the system actually emits*, `[status: rejected]` — rejected as already-covered; its mechanism half is this plan) and 2026-08-24 (*a schema enum value is a FEATURE CLAIM — if no code writes it, the feature does not exist*, with the 2026-08-26 RECURRED rider naming exactly this arm). Walk register: `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-verdict-signal-2026-09-01.md`.

**Tier computed, not judged (§1):** **T-1 fires** — six files in one subsystem (`bellows.py`, `depositor.py`, `status.py`, `tools/gate_watcher.py`, `tools/reconcile_plan.py`, tests). **T-2 fires** — the daemon will write a NEW value into production `lifecycle.db` plan rows. **T-8 fires** — not a structure-for-structure clone (100005 is the clone origin BY KIND, not by shape). T-3 does not fire (authored and dispatched on the mini; the shop pulls the same code and restarts on its own schedule — stated in the Restart Discipline paragraph below). T-5 no (every edit is additive; the schema is unchanged — `awaiting_verdict` is ALREADY in the CHECK list, `lifecycle.py:46`). T-6 no (`gates.py` untouched; no doctrine). Highest demand → **T1: full five-lens walk, no panel required; the scout is at the Planner's call and was NOT convened (a T1 code plan whose every claim is measured below).**

## Why this exists — measured on plan 100008, 2026-09-01

Plan 100008 paused twice for a verdict (19:24:25 and 19:50:10 local) and nobody was told. Three layers, each measured:

1. **Detection worked; delivery did not.** The gate_watcher spawned by the receipt tool logged `awaiting-verdict id=100008 pending=verdict-request-100008-step-1.md` eight seconds after the first pause and the second with its gate failure named — into `logs/watch/executable-gate2-dc-w28.md.log`, which nothing reads. Its docstring says it: *a REPORTER, never an actor.*
2. **The daemon's push is configured but cannot fire here.** `bellows.py:1214` and `:1345` call `notifier.notify_verdict_request(...)`; the mini's `config.json` had `notifications.enabled: false` (flipped to `true` 2026-09-01 by the CEO's go) and carries the example's EMPTY Pushover keys — `push()` returns HTTP 400 *application token must be supplied* (measured). The keys are the CEO's to add; this plan does not touch config.
3. **The plan row never says it is paused.** `plans.lifecycle_state` stays `in_progress` across every pause; the daemon writes `awaiting_verdict` only to `steps.status`, and only on a gate FAILURE (`bellows.py:1165`, `:1299`) — a header pause with gates passed leaves the step row `complete`, indistinguishable from a step that finished and moved on (100008 step 1: `complete`; step 2: `awaiting_verdict` only because rule_22 failed). Every DB-keyed watcher is blind to the common case. This is the 2026-08-24 lesson's exact arm — *an enum value with no writer* — recorded, RECURRED 2026-08-26, and recurring here a third time.

**A latent consequence of (3), measured at `lifecycle.py:395–430`:** `recover_half_claimed` (run at every daemon start, `bellows.py:3338`) marks every `in_progress` plan older than the age guard whose worktree is absent as `abandoned`. A plan paused for a verdict has NO worktree (torn down before every pause) and reads `in_progress` — so a paused plan that outlives the age guard across a daemon restart is ABANDONED by the recovery scan. Writing `awaiting_verdict` at the pause takes paused plans out of that scan by construction. ⚠️ Stated as a consequence, not a claim of a past incident: no abandoned row was measured; the code path is read, not run.

## What this plan does

| edit | file | what |
|---|---|---|
| B1–B4 | `bellows.py` | after each of the FOUR pause-site `record_verdict_request(...)` calls (worktree-create failure `:1091`; the two step-end pauses `:1213` and `:1344` — ONE anchor string, count TWO, both sites; teardown failure `:1380`), write `lifecycle.mark_plan_state(plan_id, "awaiting_verdict")` inside the G4 try/except form (`:1023`'s pattern — a lifecycle write never kills the daemon). |
| B5 | `bellows.py` | after the recheck-refusal re-pend `lifecycle.record_verdict_request(_lc_plan_id, step_number)` (`:2725`), the same write with `_lc_plan_id`. |
| B6 | `bellows.py` | on a `continue` that RESUMES (non-final step, `:3031`), `lifecycle.mark_plan_state(_lc_plan_id, "in_progress")` immediately BEFORE `self.handle_new_plan(inprogress_path, resume_step=next_step)`. The final-step continue already marks `closed` (`:3049`); stop already marks `halted` (`:3080`). `plan_doc_ref` is left alone — the file returns to the same `in-progress-<name>` the claim recorded. |
| D1 | `depositor.py` | `_resolve_in_flight_writes` (`:412`): `IN ('in_progress', 'claimed')` → `IN ('in_progress', 'claimed', 'awaiting_verdict')` — a PAUSED plan's writes must still collide (without this, B1–B5 would silently REMOVE paused plans from collision detection: the reason D1 rides in the same plan). |
| S1 | `status.py` | `query_in_flight` (`:220`): the same widening — a paused plan stays IN-FLIGHT; the AWAITING VERDICT section (keyed on `verdicts.outcome IS NULL`) is unchanged. |
| R1 | `tools/reconcile_plan.py` | the `--killed-verified` refusal (`:89`) fires on `awaiting_verdict` as well as `in_progress`. |
| W1 | `tools/gate_watcher.py` | the DELIVERY ARM: when `judge_transition` reports a transition INTO phase `awaiting-verdict`, load `config.json` beside the DB, `notifier.init_notifications(cfg)`, call `notifier.notify_verdict_request(app_key, user_key, <name>, <step>, [{"gate": g} for g in gate_failures])`, and log `WATCH: push sent` / `WATCH: push skipped (<reason>)` — never raise (a failed push must not kill the watcher; the log line is the record either way). The `--status` one-shot never pushes. Repeat polls in the same phase never push (the transition, not the state, is the trigger). |
| W2 | `tools/gate_watcher.py` | the docstring's *plans.lifecycle_state never takes 'awaiting_verdict'* sentence becomes a dated history note; pending-file detection stays PRIMARY (it also sees pauses written by an older daemon), the DB read gains `awaiting_verdict` as a corroborating phase source. |
| L1 | `lifecycle.py` | **NO edit — stated:** `recover_half_claimed`'s stranded scan stays on `in_progress` ONLY. Widening it would abandon every paused plan (no worktree); leaving it is what makes B1–B5 fix the latent consequence above. `find_in_flight`-style readers at `:167`/`:195` already include `awaiting_verdict`. |
| T1–T5 | tests | `tests/test_verdict_signal.py` (NEW): a source-text test that `bellows.py` carries exactly FIVE `mark_plan_state(<id>, "awaiting_verdict")` writes and that the resume write precedes `handle_new_plan(... resume_step=` in text order; `test_status.py`: an `awaiting_verdict` plan renders in IN-FLIGHT; `test_depositor.py`: `_resolve_in_flight_writes` returns an `awaiting_verdict` row; `test_reconcile_plan.py`: `awaiting_verdict` refused without `--killed-verified`, proceeds with it; `test_gate_watcher.py`: the push hook fires ONCE on the transition into awaiting-verdict, not on the next poll in the same phase, not on `--status`, and a raising/disabled notifier is logged as `push skipped` without killing the loop. |

⚠️ **The daemon's OWN pause during this plan will still read `in_progress`** — Restart Discipline: the running daemon executes pre-fix code through this plan's whole lifecycle. The fix is proven by the tests and by the NEXT plan's pause after the CEO restarts the daemon (dashboard `r`); QA Item 6 states this and does not pretend otherwise. The shop's daemon inherits the change on its next pull + restart; until then its plan rows keep the old shape (T-3 does not fire, but the cross-machine consequence is named).

## What this plan does NOT do
- Does not add Pushover keys or touch `config.json` (the CEO's act; done separately for `enabled`).
- Does not route a pause into tuyere (thread 80's shape: a needs-review item at close; the verdict-needed twin rides that thread).
- Does not change `steps.status` semantics, `gates.py`, the schema, or the depositor's class logic.
- Does not restart the daemon (the dashboard's `r`, the owner's act).

## MUST-PRESERVE — clauses whose only carrier is prose
- ⚠️⚠️ **Every new `mark_plan_state` call is wrapped in `try/except Exception` with a `logging.getLogger("bellows").warning`** — the G4 form at `bellows.py:1023`, with the module-level logger because `logger` there is a local of `run_plan` and two of the six sites are outside it. A lifecycle write must never turn a pause into a crash, and the handler must not raise either.
- ⚠️⚠️ **D1 rides with B1–B5 or neither ships.** A daemon that writes `awaiting_verdict` while the depositor still filters on `('in_progress','claimed')` has REMOVED paused plans from collision detection. DEV verifies D1 landed before committing B-edits (the source-text test asserts both).
- ⚠️ **L1 stays untouched** (`lifecycle.py` sha unchanged at QA). Widening the stranded scan abandons paused plans.
- ⚠️ **The push fires on the TRANSITION, never on the state.** A watcher that pushes every 15 s while a plan waits is worse than one that never pushes.
- ⚠️ **The watcher never raises out of the push.** Missing config, empty keys, `notifications.enabled: false`, network failure — each is a logged `push skipped (<reason>)`, and the poll loop continues.
- ⚠️ **`known_failures: 10` is a NAMED set, not a count.** The full-suite comparison passes only if the failing set EQUALS the baseline set by test id (P4); a different 10 is a regression.
- ⚠️ **Do not adjust a test to obtain a desired result.**

## Numbers discipline — the pins DEV re-derives (measured 2026-09-01 by the Planner at bellows `bdcb5d6`; re-derive, yours supersede and you say so)

| id | pin | value | probe |
|---|---|---|---|
| P1 | target shas, pre-edit (first 16) | `bellows.py` `cc0ddb0500200f69` · `depositor.py` `09b2b93b7aad11c7` · `status.py` `a3e3354012d653bb` · `tools/gate_watcher.py` `e8a8e0b628dc13ef` · `tools/reconcile_plan.py` `965df839d6e95c64` · `lifecycle.py` `412abd155d5099aa` (must be UNCHANGED at QA) | `shasum -a 256` |
| P2 | anchor counts, pre-edit | B1 1 · B2/B3 **2** (one string, two sites — both get the write) · B4 1 · B5 1 · B6 1 · D1 1 · S1 1 · R1 1 · W1 1 | `/usr/bin/grep -cF -- "<anchor>"` (anchors quoted in Step 1) |
| P3 | **`MPS_CALLS_POST`** — `mark_plan_state(` calls in `bellows.py`, pre → post | 6 → **12** (four pause sites + the re-pend + the resume; measured pre, asserted post) | `/usr/bin/grep -cF -- "lifecycle.mark_plan_state(" bellows.py` |
| P4 | **`SUITE_PASSED_BASELINE`** — full-suite baseline **by NAME** (the mini, bellows venv, measured 2026-09-01) | 10 failed, **1629** passed — the ten: `test_decisions.py::TestLoadPhrases::{test_loads_phrases_from_file, test_includes_known_phrases, test_splits_slash_alternatives}`, `test_decisions.py::TestExtractDecisionBlocks::test_s_class_blocks_from_ground_truth`, `test_gates_cross_machine_paths.py::TestCrossMachineReRoot::test_relative_path_unchanged`, `test_phase4_planner_retry.py::{test_planner_retries_on_auth_failure, test_planner_falls_back_to_continue_on_persistent_failure}`, `test_planner.py::{test_build_consult_file, test_consult_bad_json, test_consult_timeout}` (thread 56 — shop-layout paths; pre-existing) | `"$PY" -m pytest tests -q -p no:cacheprovider` |
| P5 | targeted suites, pre-edit | `test_gate_watcher.py` **23** · `test_status.py`, `test_depositor.py` (24), `test_reconcile_plan.py`, `test_lifecycle.py` (95) — DEV records each file's pass count pre and post; post ≥ pre, plus the new tests | `"$PY" -m pytest <file> -q` |
| P6 | `awaiting_verdict` writers to `plans`, pre-edit | **0** in `bellows.py` (the CHECK arm has no writer) | `/usr/bin/grep -cF -- "\"awaiting_verdict\")" bellows.py` reads 0 |

## STEP 1 — DEV

> **FIRST — post a short visible chat message (1–2 sentences).** Do NOT rename this file. You are the Bellows Developer.
>
> ⛔ **A0 — pre-flight. RESOLVE THE INTERPRETER FIRST — a worktree has no `.venv`.**
> ```
> cd "$(git rev-parse --show-toplevel)" && [ -f bellows.py ] && [ -d tools ] && echo TREE_OK   # HALT unless TREE_OK
> MAIN=$(cd "$(git rev-parse --git-common-dir)/.." && pwd); PY="$MAIN/.venv/bin/python"; [ -x "$PY" ] && echo VENV_OK || echo NO_VENV   # HALT unless VENV_OK
> ```
> ⚠️ Shell state does not persist between compounds: re-derive `PY` in every compound that uses it (`PY="$(cd "$(git rev-parse --git-common-dir)/.." && pwd)/.venv/bin/python"`). `python3` on this machine has no pytest.
>
> ⛔ **A1 — re-derive the pins (P1, P2, P3, P6) in your tree; state each measured value; a mismatch is a HALT quoting both values** (the tree may have moved since authoring — do not proceed on a moved anchor). Then P5: run each targeted file and record its pass count.
>
> **A2 — the edits, anchored, in this order. Every anchor is a literal; assert its count with `/usr/bin/grep -cF --` BEFORE editing; edit with a script or a careful editor, never a blind global replace.**
>
> **D1 (`depositor.py`)** — anchor (count 1): `"FROM plans WHERE lifecycle_state IN ('in_progress', 'claimed')"` → `"FROM plans WHERE lifecycle_state IN ('in_progress', 'claimed', 'awaiting_verdict')"`.
> **S1 (`status.py`)** — anchor (count 1): `WHERE p.lifecycle_state IN ('in_progress', 'claimed')` → `WHERE p.lifecycle_state IN ('in_progress', 'claimed', 'awaiting_verdict')`.
> **R1 (`tools/reconcile_plan.py`)** — anchor (count 1): `if plan_row["lifecycle_state"] == "in_progress" and not args.killed_verified:` → `if plan_row["lifecycle_state"] in ("in_progress", "awaiting_verdict") and not args.killed_verified:`; and in the message two lines below, `lifecycle_state is 'in_progress'` → `lifecycle_state is 'in_progress' or 'awaiting_verdict'`.
> **B1 (`bellows.py`)** — anchor (count 1): `lifecycle.record_verdict_request(plan_id, 1, pause_reason_code="gate_failure", verdict_file_ref=_vr_path)` — INSERT immediately after it, same indentation:
> ```
> try:
>     lifecycle.mark_plan_state(plan_id, "awaiting_verdict")
> except Exception:
>     logging.getLogger("bellows").warning(f"lifecycle: failed to write awaiting_verdict for plan {plan_id}")
> ```
> ⚠️ `logging.getLogger("bellows")`, NOT the bare `logger`: `logger` is a LOCAL of `run_plan` (`bellows.py:311`), in scope at B1–B4 but NOT at B5 (a staticmethod) or B6 (the consumer) — a bare `logger` there raises `NameError` inside the `except`, turning a swallowed lifecycle failure into a crash (walk 1 w1-1). `import logging` is module-level in `bellows.py`.
> **B2/B3 (`bellows.py`)** — anchor (count **2**): `lifecycle.record_verdict_request(plan_id, current_step, pause_reason_code=_pause_reason, verdict_file_ref=_vr_path)` — INSERT the same four lines after BOTH occurrences, each at its own indentation (they differ: the first sits one level deeper). Post-condition: the anchor still counts 2 and `mark_plan_state(plan_id, "awaiting_verdict")` counts 4 after B4.
> **B4 (`bellows.py`)** — anchor (count 1): `lifecycle.record_verdict_request(plan_id, current_step, pause_reason_code="gate_failure", verdict_file_ref=_vr_path)` — the same four lines after it.
> **B5 (`bellows.py`)** — anchor (count 1): `lifecycle.record_verdict_request(_lc_plan_id, step_number)` — after it: the same four lines with `_lc_plan_id` in place of `plan_id` (this is inside `_recheck_refuse`, a staticmethod — the `logging.getLogger("bellows")` form is why it works here).
> **B6 (`bellows.py`)** — anchor (count 1): `self.handle_new_plan(inprogress_path, resume_step=next_step)` — INSERT immediately BEFORE it, same indentation:
> ```
> try:
>     lifecycle.mark_plan_state(_lc_plan_id, "in_progress")
> except Exception:
>     logging.getLogger("bellows").warning(f"lifecycle: failed to restore in_progress for plan {_lc_plan_id}")
> ```
> **W1 (`tools/gate_watcher.py`)** — anchor (count 1, two lines): `        if line:\n            _log_line(log_path, line)` — REPLACE with a block that logs the line, then, if `cur is not None and cur.get("phase") == "awaiting-verdict" and (prev == "UNSET" or prev is None or prev.get("phase") != "awaiting-verdict")`, calls a new module function `_push_pause(args.name, cur, db_path=args.db_path)` and logs its returned line. Define `_push_pause(name, cur, db_path=None) -> str` at module level: locate `config.json` beside the resolved DB (`os.path.dirname(<db path>)/config.json`); on any failure to read it → return `"WATCH: push skipped (no config.json beside the DB)"`; `sys.path.insert(0, _ROOT)` (the module-level bellows root the script already resolves for `_WATCH_DIR`; the script imports NO bellows module today — it reads the DB with raw sqlite — so this insert is new and lives INSIDE `_push_pause`) then `import notifier` inside the same `try`; `notifier.init_notifications(cfg)`; if `not cfg.get("notifications", {}).get("enabled", True)` → `"WATCH: push skipped (notifications disabled)"`; if either key empty → `"WATCH: push skipped (pushover keys empty)"`; else `ok = notifier.notify_verdict_request(app_key, user_key, name, <the lowest pending step number from cur["pending"] names, or 0>, [{"gate": g} for g in (cur.get("gate_failures") or [])])` inside `try/except Exception as e` → `"WATCH: push skipped (" + type(e).__name__ + ")"`; return `"WATCH: push sent"` if `ok` else `"WATCH: push skipped (pushover returned false)"`. The `--status` path never calls it.
> **W2 (`tools/gate_watcher.py`)** — anchor (count 1): the docstring sentence beginning `Pause detection reads verdicts/pending/, not the DB: plans.lifecycle_state` through `IS the pause signal.` — REPLACE with: `Pause detection reads verdicts/pending/ FIRST (the request file is the pause signal every daemon build emits) and, since verdict-signal-2026-09-01, corroborates it with plans.lifecycle_state == 'awaiting_verdict' (written at every pause by daemons at or after that change; older daemons leave the row in_progress, which is why the file stays primary). Before that change plans.lifecycle_state never took 'awaiting_verdict' (measured 2026-08-26 and again on plan 100008, 2026-09-01).` Then, in `read_state`, treat a plan row whose `lifecycle_state == 'awaiting_verdict'` as phase `awaiting-verdict` even when no pending file is found (a corroborating source, additive — the file path wins when present).
>
> **A3 — tests (T1–T5), then run them.** Add `tests/test_verdict_signal.py` (source-text: `open('bellows.py').read().count('mark_plan_state(plan_id, "awaiting_verdict")') == 4`, `count('mark_plan_state(_lc_plan_id, "awaiting_verdict")') == 1`, the resume write's index < the `handle_new_plan(inprogress_path, resume_step=next_step)` index, and `depositor.py` carries `'awaiting_verdict'` inside `_resolve_in_flight_writes`'s SQL — the D1-rides-with-B guard). Extend `test_status.py` (an `awaiting_verdict` plan appears in `query_in_flight`), `test_depositor.py` (an `awaiting_verdict` row is returned by `_resolve_in_flight_writes`), `test_reconcile_plan.py` (refused without `--killed-verified` on `awaiting_verdict`; proceeds with it), `test_gate_watcher.py` (with `_push_pause` monkeypatched to record calls: ONE call on the transition into awaiting-verdict, ZERO on a repeated poll in the same phase, ZERO for `--status`; and a `_push_pause` that raises is caught and logged as `push skipped`). Run the targeted files: every pre-existing test still passes (P5 post ≥ pre) and every new test passes; a failure is a STOP, not a thing to adjust.
>
> **A4 — post-conditions (counts read, never exit codes):** P3 `mark_plan_state(` == 12 (P3, measured pre 6, asserted post); `"awaiting_verdict")` in `bellows.py` == 5; D1/S1/R1 tokens each == 1 post; `lifecycle.py` sha == P1's (untouched); `git diff --stat` names exactly the six source files + the test files, nothing else.
>
> **A5 — dev log + commit.** `knowledge/development/dev-log-verdict-signal-2026-09-01.md`: the resolved interpreter, A1's measured pins (yours), the anchor counts before and after, the targeted test counts pre/post, A4's raws. Commit by explicit pathspec (`git add` each file by name; `-- <paths>`; no `-A`, no amend): `[<id from your plan filename>] verdict-signal: awaiting_verdict written at every pause, restored on resume; in-flight predicates widened; gate_watcher pushes the transition; tests`. STOP.
>
> **Deposits:**
> - `knowledge/development/dev-log-verdict-signal-2026-09-01.md`
>
> **Scope:**
> - `bellows.py`
> - `depositor.py`
> - `status.py`
> - `tools/gate_watcher.py`
> - `tools/reconcile_plan.py`
> - `tests/test_verdict_signal.py`
> - `tests/test_gate_watcher.py`
> - `tests/test_status.py`
> - `tests/test_depositor.py`
> - `tests/test_reconcile_plan.py`
> - `knowledge/development/dev-log-verdict-signal-2026-09-01.md`

---

## STEP 2 — QA

> **Step 1's Receipt status must be `Status: Complete`.** Anything else → HALT. **FIRST — post a short visible chat message.** You are the Bellows QA agent. `cd "$(git rev-parse --show-toplevel)"`; re-derive `PY` as in A0.
>
> **(A) Rule 20 self-check** — the canonical block from `/Users/marklehn/Developer/eluvian-governance/RULE_20_SELF_CHECK_BLOCK.md` (⚠️ this machine's path; the daemon prompt may name the shop's), run with:
> - `plan_slug`: `verdict-signal-2026-09-01`
> - `qa_report_path`: `knowledge/qa/evidence/verdict-signal-2026-09-01/qa-receipt.md`
> - `evidence_dir`: `"$(pwd)/knowledge/qa/evidence/verdict-signal-2026-09-01"` (your OWN worktree)
> - `required_evidence_files`: `["probes-raw.txt", "full-suite-verdict-signal.txt"]`
>
> **(B) Items — FAIL reported, never repaired:**
> - **Item 1 — the edits landed (source probes, raw → `probes-raw.txt`):** P3 == 12 (measured); `"awaiting_verdict")` in `bellows.py` == 5; D1, S1, R1 post-tokens == 1 each; `_push_pause` defined once and called once in `tools/gate_watcher.py`; `lifecycle.py` sha == P1's; `git show <DEV commit> --numstat --format=` lists exactly the Scope files.
> - **Item 2 — targeted suites:** each of the six test files green under `"$PY"`, counts ≥ P5 pre-counts, the new tests present by name (`-q --co` listing pasted).
> - **Item 3 — the full suite with the CONTROL COMPARISON (P4):** `"$PY" -m pytest tests -q -p no:cacheprovider > knowledge/qa/evidence/verdict-signal-2026-09-01/full-suite-verdict-signal.txt 2>&1; echo "exit=$?" >> <that file>`; then extract the `FAILED` test ids and compare AS A SET to P4's ten names: equal set → PASS; any addition → Critical (a regression), any removal → note it (a fix you did not make — state it). The summary line must read `10 failed, N passed` with N ≥ 1629 + the new tests.
> - **Item 4 — the watcher's arm, executed:** from your worktree, `"$PY" tools/gate_watcher.py --status executable-verdict-signal.md` prints a state line and NO push line (the one-shot never pushes); run the new transition test alone and paste its output.
> - **Item 5 — the reconcile refusal, executed** against a scratch `lifecycle.db` (`cp` of an `init_lifecycle_db` fresh file, in `/tmp`): a row with `awaiting_verdict` → the tool exits 3 without `--killed-verified` (raw).
> - **Item 6 — the Restart Discipline statement:** record that THIS plan's own pause rows read `in_progress` (query the live `lifecycle.db` read-only: `sqlite3 -readonly /Users/marklehn/Developer/bellows/lifecycle.db "SELECT lifecycle_state FROM plans WHERE id=<your id>"`) because the running daemon predates the change; the proof of the daemon half is the NEXT plan's pause after the CEO's dashboard restart — name that as the canary, not as done.
> - **Item 7 — the receipt** at `knowledge/qa/evidence/verdict-signal-2026-09-01/qa-receipt.md` with a `## Verification Table` (`| Deliverable | Expected | Status | Evidence |`; status cells carry the glyph ONLY; no hedge word in any cell of a positive row — the Rule 20 block scans the whole row; ⚠️ write the failure glyph in a description cell only inside backticks, never bare — the rule_22 gate read a bare one as a failing row on plan 100008), then the Rule 20 block's stdout verbatim.
>
> Commit the evidence dir by explicit pathspec, then STOP.
>
> **Deposits:**
> - `knowledge/qa/evidence/verdict-signal-2026-09-01/qa-receipt.md`
> - `knowledge/qa/evidence/verdict-signal-2026-09-01/probes-raw.txt`
> - `knowledge/qa/evidence/verdict-signal-2026-09-01/full-suite-verdict-signal.txt`
>
> **Scope:**
> - `knowledge/qa/evidence/verdict-signal-2026-09-01/qa-receipt.md`
> - `knowledge/qa/evidence/verdict-signal-2026-09-01/probes-raw.txt`
> - `knowledge/qa/evidence/verdict-signal-2026-09-01/full-suite-verdict-signal.txt`

Rule 20 banner (byte-exact, produced by RUNNING the canonical block — never hand-authored):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```

---

## Drafting Cycle

**Tier:** T1 — T-1, T-2 and T-8 fire; none demands T2. Scout not convened (Planner's call; every claim in this plan is a measured line).

**Walk register:** /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-verdict-signal-2026-09-01.md
(Schema 0.3, committed per phase — the note on its own line for `cycle_check`'s register-line regex.)

**Walk 0 (context pin, measured):** target shas P1 at bellows `bdcb5d6`; every anchor counted (P2 — one pair deliberately count 2, stated); the six `mark_plan_state` call sites and the six pause/resume sites read at source, each named by line; the recovery scan's abandon path read and left untouched (L1); the full-suite baseline measured as a NAMED set (P4); blame — the four pause sites written by one commit (`4667e0b3`, the lifecycle-boundaries plan), the re-pend by `[518]`, the resume by the initial import; no target line owned by a halted or in-flight plan. Clone-diff vs `100005` (three passes): FACTS — its interpreter resolver, pin table, targeted-plus-control test form and "mutant is a STOP" rule re-derived for this plan; ARTEFACTS — the `--git-common-dir` venv resolver, `TREE_OK`, pins re-derived by DEV, explicit-pathspec commits, the full-suite control comparison, the Rule 20 four values, worktree-relative deposits: each counted 1 here; STRUCTURE — DEV → QA unchanged; the `known_failures` set is NAMED here where 100005 refused to pin a number (P4 of 100005) — a declared strengthening, because the ten are stable and thread 56 names their cause. Consumer dry-run (DC §2.0, v2.23): `plan_lint` at a faithful mirror, `cycle_check`, the class assigner (`shop-infra` — a bellows code write), the deposit extractor (step 1 one `.md`; step 2 receipt first + a `full-suite` `.txt`) — results on the register's walk-0 line.

**Direction verdict (after walk 1): PROCEED.** Tested: nothing invalidates the clone origin (100005), the mechanism (anchored additive edits + the widened predicates, each anchor counted), or a scope premise (the seven-consumer enumeration is complete by grep; L1's non-edit is reasoned at source).

**Walks:**
- Weak spots:          w1 2 folded — instruction 2 / record 0 (`logger` is a local of `run_plan` — the B5/B6 handlers would have raised NameError inside `except`; the watcher imports no bellows module, so "mirror that import" pointed at nothing — `_ROOT` insert + lazy import)
- Destruction:         w1 dry — a death mid-DEV leaves one uncommitted worktree (A5 is the single commit; teardown lands nothing partial); the daemon runs old code throughout, so no half-written state reaches production during this plan
- Vulnerabilities:     w1 dry — the count-2 anchor is guarded by the source-text test (4 + 1 writes); every HALT names its measurement; the push fires on the transition only and never raises (MUST-PRESERVE, tested)
- Integration-record:  w1 2 folded — instruction 0 / record 2 (a doctrine-plan phrase "History-facing note" with no referent here; the two restated `12`s gained their measured qualifier — `propagation_check` 2 → 0)
- ACID:                w1 dry — the requirement set as a system: D1 ⇔ B1–B5 (paired, asserted by one test), L1 ⇔ B1–B5 (paused plans exit the stranded scan only if the scan is NOT widened), the daemon's own pause reading the old shape ⇔ the canary being the NEXT plan — no pair conflicts
- **Walk 1 total: 4 findings, 4 folded — instruction 2 / record 2; 0 of 4 fold-introduced.**

**Conformance (§5):** *(recorded at the freeze from the last run)*

**Cold panel:** not required at T1; none convened.

## Cycle Manifest
tier: T1
target: bellows.py
class: shop-infra
reads: /Users/marklehn/Developer/bellows/bellows.py, /Users/marklehn/Developer/bellows/depositor.py, /Users/marklehn/Developer/bellows/status.py, /Users/marklehn/Developer/bellows/lifecycle.py, /Users/marklehn/Developer/bellows/tools/gate_watcher.py, /Users/marklehn/Developer/bellows/tools/reconcile_plan.py, /Users/marklehn/Developer/bellows/notifier.py, /Users/marklehn/Developer/bellows/knowledge/decisions/Done/executable-100005.md, /Users/marklehn/Developer/eluvian-governance/RULE_20_SELF_CHECK_BLOCK.md
writes: bellows.py, depositor.py, status.py, tools/gate_watcher.py, tools/reconcile_plan.py, tests/test_verdict_signal.py, tests/test_gate_watcher.py, tests/test_status.py, tests/test_depositor.py, tests/test_reconcile_plan.py, knowledge/development/dev-log-verdict-signal-2026-09-01.md, knowledge/qa/evidence/verdict-signal-2026-09-01/qa-receipt.md, knowledge/qa/evidence/verdict-signal-2026-09-01/probes-raw.txt, knowledge/qa/evidence/verdict-signal-2026-09-01/full-suite-verdict-signal.txt
open_forks: none — the tuyere needs-review twin of this signal rides thread 80; the Pushover keys are the CEO's config act
walks: 1
yields: 4
validation: <declare>
coherence: N/A
