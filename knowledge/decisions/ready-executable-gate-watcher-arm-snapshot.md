# bellows — executable: gate_watcher staleness by RESOLVED-VERDICT existence (deletes the arm-time snapshot) + a state-space test built without the author's model — corrected re-deposit after the 572 halt

**Date:** 2026-08-27 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** targeted (the state-space suite) + full suite at QA | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always

**auto_close:** false

**Depends on:** the exec-572 HALT (`knowledge/decisions/halted-executable-572.md`, stopped at step 1 on a Planner design defect — this is its corrected re-deposit under the stable slug, per the no-redo verdict grammar); tuyere thread 20; LESSONS.md 2026-08-26 "a live canary must be fired in the STATE the tool exists to discriminate"; LESSONS.md 2026-08-16 "A decision table's correctness is a property of its STATE SPACE — enumerate it in code, because reading cannot" **[status: pending — this plan is its first shipped instance]**.

## Why this exists

Exec-572 shipped a guard on a FALSE PREMISE: it treated any verdict-request present when the watcher armed as "already resolved and awaiting daemon cleanup." That was never checked. A watcher arming after a step completes but BEFORE the Planner issues a verdict sees a genuine pause and silently swallows it — a MISSED PAUSE, strictly worse than the spurious log line it set out to fix.

**Measured live on 572 itself:** its step-1 request appeared at 08:39:03 with no verdict issued; the watcher recorded it as its snapshot, logged `arm-time pending ignored`, and next spoke only at `terminal=halted`. The real pause was never reported. **All 8 of that plan's tests passed** — they encoded the same wrong premise, so a green QA would have certified the defect.

**The correction is a DELETION.** Staleness is not a property of when the watcher armed; it is a property of the request, and it is knowable from disk: a pending `verdict-request-<id>-step-<N>.md` is stale **iff** a verdict for that plan+step has already been issued. That check removes the snapshot mechanism entirely — no `judge_watch_line`, no `arm_pending`, no `armed` flag, no threading — and it makes `--status` MORE correct as a side effect.

## What this plan does NOT do

- **No new CLI surface, no change to the exit contract** (terminal → 0, timeout → 3, usage → 2).
- **No daemon/depositor/receipt changes.**
- **No memory writes** (sandbox-denied to agents; the Planner closes thread 20, corrects its scope text, and records the testing lesson at close).

## Numbers discipline

⚠️ **Measured 2026-08-27 by the Planner; RE-DERIVE each pre-flight — yours supersede and you say so; mismatch on a load-bearing pin → HALT.**

| id | pin | value | anchor/probe |
|---|---|---|---|
| B1 | the resolved-verdict naming, BOTH forms | `verdicts/resolved/verdict-<id>-step-<N>.md` (issued, pre-consumption — `issue_verdict.py` prints this path) and `processed-verdict-<id>-step-<N>.md` (post-consumption). Both measured live: `processed-verdict-570-step-1.md`, `-570-step-2.md`, `-571-step-1.md`, `-571-step-2.md` | `ls verdicts/resolved/ \| /usr/bin/grep -E "^(processed-)?verdict-57[01]-step-"` |
| B2 | the pending writer | `verdict.py:180-188` `post_verdict_request` → `verdicts/pending/verdict-request-{slug}-step-{N}.md`; post-claim the slug IS the plan id (`slug_from_path` strips `executable-`/`diagnostic-` etc. from the id-renamed file) | read `verdict.py:85-95`, `:180-188` |
| B3 | reachable plan states | `SELECT DISTINCT lifecycle_state FROM plans` → `abandoned, closed, halted, in_progress`; `awaiting_verdict` ABSENT (phantom arm — it is written to `steps.status` only, and only on gate failure) | sqlite3 mode=ro on the live DB |
| B4 | code to DELETE | `judge_watch_line` at `tools/gate_watcher.py:113-134`; in `main`, the `arm_pending`/`armed` seeding and threading added by 572 | read the file |
| B5 | baselines | `tests/test_gate_watcher.py` collects **24** (16 + 572's 8, which are DELETED by this plan → net 16 before the new suite); full suite **1582** at exec-570, plus 572's 8 currently in tree | `pytest … --collect-only` |

## MUST-PRESERVE

- ⚠️ **`/usr/bin/grep` for ALL probes (`-F` unless a regex is stated); zero-match exits 1 — never `&&`-chain a probe.**
- ⚠️ **THE SPLIT-PATH LAW:** `lifecycle.db`, `verdicts/`, `logs/` are untracked; resolved at RUNTIME from the tool's own location; tests inject every path explicitly.
- ⚠️ **A pause with NO issued verdict must ALWAYS be reported — at the first poll as readily as at the hundredth.** This is the invariant 572 violated. It is asserted as a PROPERTY over the whole state space, not as one example.
- ⚠️ **The 16 pre-572 tests stay green UNMODIFIED.** 572's 8 `TestArmTimeSnapshot` tests are DELETED with the mechanism they tested — do not adapt them; they encode the falsified premise.
- ⚠️ **Worktree dispatch; every claim cites file:line; absence claims carry positive controls; EVERY DATE IS A FIXED LITERAL.**

## STEP 1 — DEV (delete the snapshot, add the resolved check, build the state-space suite)

> **Task A — worktree discipline.** `cd "$(git rev-parse --show-toplevel)" && test -f tools/gate_watcher.py && echo TREE_OK` — HALT unless TREE_OK. Resume probe: `/usr/bin/grep -cF "_verdict_issued" tools/gate_watcher.py; true` → 0 = full run; ≥1 = resume at Task D.
>
> **Task B — DELETE 572's mechanism** (revert, do not adapt): remove `judge_watch_line` (`:113-134`) whole; in `main`, remove the `armed` flag, the `arm_pending` seeding, and the threading, restoring the loop's line computation to `judge_transition(None if prev == "UNSET" else prev, cur)`. Delete the `TestArmTimeSnapshot` class from `tests/test_gate_watcher.py` entire. Verify: `/usr/bin/grep -cF "arm_pending" tools/gate_watcher.py; true` → 0; `/usr/bin/grep -cF "TestArmTimeSnapshot" tests/test_gate_watcher.py; true` → 0; `python3 -m pytest tests/test_gate_watcher.py -q` → 16 passed (the pre-572 baseline restored; re-derive).
>
> **Task C — add the staleness check to `read_state`:**
> 1. Helper above `read_state`:
>    ```python
>    def _verdict_issued(resolved_dir, plan_id, step):
>        """True iff a verdict for this plan+step already exists on disk.
>
>        BOTH forms count: verdict-<id>-step-<N>.md is written by issue_verdict
>        at the moment the Planner rules; the daemon later renames it to
>        processed-verdict-<id>-step-<N>.md. A pending request with either form
>        present is awaiting DAEMON CLEANUP, not awaiting a verdict.
>        """
>    ```
>    Implement with two `os.path.exists` checks. **Staleness is read from disk — never inferred from when this process started.**
> 2. In `read_state`, resolve `resolved_dir` beside the pending dir: `os.path.join(os.path.dirname(os.path.abspath(pend)), "resolved")` — i.e. `<…>/verdicts/resolved`. Add an optional `resolved_dir=None` kwarg that overrides it (tests inject).
> 3. Partition the glob hits by step number, parsed from the filename with `re.match(r"^verdict-request-\d+-step-(\d+)\.md$", name)`; a name that does not parse is treated as LIVE (fail toward reporting — never silently drop a request the watcher cannot classify). `live = [h for h in hits if not _verdict_issued(resolved_dir, plan_id, step_of(h))]`.
> 4. The pause branch fires only when `live` is non-empty: `phase="awaiting-verdict"`, `pending=live`. When hits exist but `live` is empty, return the `base` dict UNCHANGED (the plan is running / awaiting cleanup, not awaiting a verdict).
>
> **Task D — the STATE-SPACE test suite** (`class TestPauseStateSpace`), replacing example-led tests with forced classification:
> 1. Declare the dimensions as literal tuples AT THE TOP of the class, each with a comment naming the SYSTEM source it was read from (not the author's intuition):
>    - `PENDING = ("absent", "present")` — the daemon's writer, `verdict.py:187`
>    - `VERDICT = ("none", "issued", "processed")` — the two real filename forms (B1) plus absence
>    - `STATE = ("in_progress", "closed", "halted", "abandoned")` — **B3's `SELECT DISTINCT`, the REACHABLE set, deliberately NOT the schema CHECK list** (which contains the phantom `awaiting_verdict` arm)
>
>    ⚠️ **Arming POSITION is deliberately NOT a dimension of this product, and the reason is the point of the whole plan.** After Task B's deletion, `read_state` has no notion of when the watcher started — position CANNOT affect its answer. Parametrizing `read_state` over position would therefore pass trivially: a vacuous check that proves nothing (the a-check-that-cannot-fail class). Position is instead pinned two ways at the layers where it could still exist: the structural probe in item 6 and the loop-layer invariant in item 7.
> 2. Build `CLASSIFICATION`: an explicit dict mapping EVERY cell of the 2×3×4 product to `"REPORT_PAUSE"` or `"NO_PAUSE"`, written out cell by cell. Rules to apply while filling it: pending absent → `NO_PAUSE`; any TERMINAL state → `NO_PAUSE` (terminal wins over pending — the stray-file law); pending present + verdict `none` + non-terminal → **`REPORT_PAUSE`** (the cell 572 got wrong); pending present + verdict `issued`/`processed` + non-terminal → `NO_PAUSE`.
> 3. `test_state_space_is_completely_classified` — assert `len(CLASSIFICATION) == 2*3*4` and that its key set EQUALS `set(itertools.product(PENDING, VERDICT, STATE))`. **This is the test that makes an unclassified cell impossible to leave silently — the property 572 lacked.** A new reachable `lifecycle_state` appearing in the DB makes this FAIL as uncovered rather than pass in silence.
> 4. `test_every_cell_behaves_as_classified` — `@pytest.mark.parametrize` over `CLASSIFICATION.items()`; for each cell CONSTRUCT the world (tmp DB row at that `lifecycle_state`; pending dir with/without the request; resolved dir with the matching verdict form) and assert `read_state(...)["phase"] == "awaiting-verdict"` iff the cell says `REPORT_PAUSE`.
> 5. `test_reachable_states_match_the_classification_dimension` — the drift guard: read the DB named by the `GATE_WATCHER_LIVE_DB` env var (falling back to the tool's default path), `SELECT DISTINCT lifecycle_state`, assert every observed value is in `STATE`. ⚠️ **It must SKIP when no DB is reachable — and a test that only ever skips is a check that cannot fail.** DEV and QA both run in worktrees, which carry no `lifecycle.db`, so this test would skip in BOTH and prove nothing. QA Item 2.6 therefore runs it explicitly with `GATE_WATCHER_LIVE_DB` pointed at the live checkout's DB, and the receipt must show it RAN rather than skipped (`-rs` output pasted). Ties the dimension to the SYSTEM rather than to this author's list.
> 6. `test_no_arming_position_state_survives` — the structural deletion probe as a TEST, not a one-off shell check: read `tools/gate_watcher.py` source and assert `arm_pending`, `armed`, and `judge_watch_line` are all ABSENT. If the snapshot mechanism ever returns, this fails.
> 7. `test_position_cannot_change_the_phase` — the invariant at the only layer where position exists: for one unresolved-pause `cur`, `judge_transition(None, cur)` and `judge_transition(<different prev>, cur)` may differ in whether a LINE is emitted, but both must carry the same `cur["phase"]`; assert the phase is `awaiting-verdict` in both. **A guard that special-cases arming cannot pass this.**
> 8. `test_unparseable_request_name_is_reported_live` — a pending file whose name does not match the pattern still yields `awaiting-verdict` (fail toward reporting).
> 9. `test_mixed_steps_report_only_the_unresolved_one` — steps 1 and 2 both pending, step 1 resolved → `pending == ["verdict-request-<id>-step-2.md"]`.
> **Targeted run:** `python3 -m pytest tests/test_gate_watcher.py -q` → 16 baseline + 6 named tests + 24 parametrized cells; record the exact collected count you observe and state it (do NOT assume — run `--collect-only` first and report the real number; the parametrize expansion is the part most likely to differ from a prediction).
>
> **Task E — dev log** `knowledge/dev-logs/gate-watcher-staleness-dev-2026-08-27.md`: the diff summary, each pin re-derivation (B1-B5, yours vs the table, say "supersedes" where they differ), the `--collect-only` count, the targeted-test tail pasted raw, and the deletion probes' output.
>
> **Task F — commit** (worktree; message `[<id>] gate-watcher-staleness: resolved-verdict check replaces the arm-time snapshot; state-space suite`): `cd "$(git rev-parse --show-toplevel)" && git add tools/gate_watcher.py tests/test_gate_watcher.py knowledge/dev-logs/gate-watcher-staleness-dev-2026-08-27.md && git commit`. Verify `git show --stat HEAD | cat` lists exactly those 3 files.
>
> **Deposits:**
> - `tools/gate_watcher.py` (572's mechanism deleted; `_verdict_issued` + partition added)
> - `tests/test_gate_watcher.py` (`TestArmTimeSnapshot` deleted; `TestPauseStateSpace` added)
> - `knowledge/dev-logs/gate-watcher-staleness-dev-2026-08-27.md`
>
> **Scope:**
> - `tools/gate_watcher.py`
> - `tests/test_gate_watcher.py`
> - `knowledge/dev-logs/gate-watcher-staleness-dev-2026-08-27.md`

## STEP 2 — QA (FULL suite + the 572 regression reproduced live)

> **Item 1 — full suite.** `cd "$(git rev-parse --show-toplevel)"`; `python3 -m pytest tests/ --tb=short -q 2>&1 | cat | tee knowledge/qa/evidence/gate-watcher-staleness-2026-08-27/pytest_full.txt` — 0 failed; record the count and its derivation from the 1582 B5 baseline (572's 8 removed, this plan's suite added).
> **Item 2 — THE 572 REGRESSION, reproduced against the live tool** (full tails to `probes-raw.txt`). `SCRATCH=$(mktemp -d)`; `mkdir -p "$SCRATCH/verdicts/pending" "$SCRATCH/verdicts/resolved"`; resolve this plan's id: `sqlite3 "file:/Users/marklehn/Developer/GitHub/bellows/lifecycle.db?mode=ro" "SELECT id FROM plans WHERE deposit_placeholder_name='executable-gate-watcher-arm-snapshot.md' ORDER BY id DESC LIMIT 1;"` → `$PID`.
> 1. **Baseline, NOT a discriminating probe — say so in the receipt:** `touch "$SCRATCH/verdicts/pending/verdict-request-$PID-step-1.md"` (resolved dir EMPTY); `python3 tools/gate_watcher.py --status executable-gate-watcher-arm-snapshot.md --db-path /Users/marklehn/Developer/GitHub/bellows/lifecycle.db --pending-dir "$SCRATCH/verdicts/pending" --resolved-dir "$SCRATCH/verdicts/resolved"` → `WATCH: awaiting-verdict id=$PID pending=verdict-request-$PID-step-1.md`, exit 0. ⚠️ **This output is the SAME before and after this plan** — 572's guard lived in the poll loop (`judge_watch_line`), never in `read_state`, so `--status` was never affected by it. Recording this as "the 572 regression killed" would be a false claim; it is a control showing the unresolved-pause path still works. The discriminating probes are 1b, 2 and 3.
> **1b. THE ACTUAL 572 REGRESSION — the LOOP, at arm time, over an UNRESOLVED pause:** with the same scratch world (pending present, resolved dir EMPTY), delete any prior log, then run the loop for one minute: `LOG=logs/watch/executable-gate-watcher-arm-snapshot.md.log; rm -f "$LOG"; python3 tools/gate_watcher.py executable-gate-watcher-arm-snapshot.md --db-path /Users/marklehn/Developer/GitHub/bellows/lifecycle.db --pending-dir "$SCRATCH/verdicts/pending" --resolved-dir "$SCRATCH/verdicts/resolved" --timeout-min 1 --interval-sec 5` (exit 3 on timeout, expected). Paste the log whole and assert: `/usr/bin/grep -cF "pending=verdict-request-$PID-step-1.md" "$LOG"` → **≥1** and `/usr/bin/grep -cF "armed over pre-existing" "$LOG"` → **0**. ⚠️ **Under 572's shipped loop this world produced `armed over pre-existing …` and then silence — a missed pause. That is the regression this plan kills. If the first count reads 0, HALT.**
> 2. **Stale, `verdict-` form:** `touch "$SCRATCH/verdicts/resolved/verdict-$PID-step-1.md"`; same command → the plan's live lifecycle phase (NOT `awaiting-verdict`), exit 0.
> 3. **Stale, `processed-verdict-` form:** `rm "$SCRATCH/verdicts/resolved/verdict-$PID-step-1.md" && touch "$SCRATCH/verdicts/resolved/processed-verdict-$PID-step-1.md"`; same command → NOT `awaiting-verdict`. (Both forms must count — B1.)
> 4. **Mixed:** with step-1 still resolved, `touch "$SCRATCH/verdicts/pending/verdict-request-$PID-step-2.md"` → `awaiting-verdict` naming **only** step-2.
> 5. Cleanup: `rm -rf "$SCRATCH"`.
> 6. **Force the drift guard to actually RUN** (it skips in a worktree, and a permanently-skipping test is not a check): `GATE_WATCHER_LIVE_DB=/Users/marklehn/Developer/GitHub/bellows/lifecycle.db python3 -m pytest tests/test_gate_watcher.py -q -rs -k reachable_states 2>&1 | cat` → **1 passed, 0 skipped**. Paste the tail. If it reports `skipped`, the guard is inert: say so plainly in the receipt rather than recording a pass.
> **Item 3 — hygiene + receipt** `knowledge/qa/evidence/gate-watcher-staleness-2026-08-27/qa-receipt.md`: numstat vs the DEV commit (3 files); toplevel; reflog `-n 4` → 0 amends; per-item table; the state-space completeness test named explicitly with its cell count; then the Rule 20 block INSIDE a "Verification"-headed section (the 556 placement law).
> **Item 4 — commit the evidence** (message `[<id>] gate-watcher-staleness: QA — full suite + 572 regression probes`): `git add knowledge/qa/evidence/gate-watcher-staleness-2026-08-27/ && git commit`; verify exactly 3 files.
>
> ⚠️ **Gate note:** pytest summary named above — the gate parses; no benign override pre-declared.
> ⚠️ **`--resolved-dir` is a NEW CLI arg** required by Item 2; add it in Task C alongside `--pending-dir` and thread it to both `read_state` call sites.
>
> **Deposits:**
> - `knowledge/qa/evidence/gate-watcher-staleness-2026-08-27/pytest_full.txt`
> - `knowledge/qa/evidence/gate-watcher-staleness-2026-08-27/probes-raw.txt`
> - `knowledge/qa/evidence/gate-watcher-staleness-2026-08-27/qa-receipt.md`
>
> **Scope:**
> - `knowledge/qa/evidence/gate-watcher-staleness-2026-08-27/pytest_full.txt`
> - `knowledge/qa/evidence/gate-watcher-staleness-2026-08-27/probes-raw.txt`
> - `knowledge/qa/evidence/gate-watcher-staleness-2026-08-27/qa-receipt.md`

Rule 20 banner (byte-exact, inside the QA receipt's VERIFICATION section):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```

## Drafting Cycle

**Tier:** T1 — a deletion plus one disk-read predicate, and a test suite whose oracle is the enumerated state space rather than the author's examples.

**Walk register:** `bellows/knowledge/research/walk-register-gate-watcher-staleness-2026-08-27.md`

**Walks:** walk 0 pinned; **walks 1-4 complete**, genuine sequential five-lens passes — see the register.
**Cold panel: NOT convened, decided with reasoning** — T1, read-only reporter, net-negative code; the 563/569/571 precedent. ⚠️ Noted against that decision: 572 was ALSO a T1 no-panel plan and shipped a false premise past five walks — the mitigation applied here is the state-space suite (an oracle outside the author's model), not a panel.
**Direction verdict (after walk 1): PROCEED** — the delete-and-check shape held.
- Weak spots:          w1 dry; w2 1 folded (the drift guard would skip in BOTH worktree steps — a permanently-skipping test); w3 dry; w4 dry
- Destruction:         w1 dry; w2 dry; w3 dry; w4 dry
- Vulnerabilities:     w1 1 folded (POSITION is not a dimension of read_state — parametrizing it would be vacuous); w2 dry; w3 1 folded (⚠️ QA 2.1 claimed to reproduce the 572 regression via --status, but 572's guard was LOOP-only, so that probe passes identically before and after); w4 dry
- Integration-record:  w1 dry; w2 dry; w3 dry; w4 dry
- ACID:                w1 dry; w2 dry; w3 dry; w4 dry
**Conformance (§5):** recorded at the freeze from actual runs — see the register's conformance block.
**Closing:** **walk 4 confirmed walk 3's folds clear — all five lenses dry; BAR MET.** Instruction series **2 → 1 → 1 → 0**. Close is MANUAL (CEO-lane verdicts; auto_close false).

## Cycle Manifest
tier: T1
target: bellows/tools/gate_watcher.py
class: shop-infra
reads: /Users/marklehn/Developer/GitHub/bellows/tools/gate_watcher.py, /Users/marklehn/Developer/GitHub/bellows/verdict.py, /Users/marklehn/Developer/GitHub/bellows/tests/test_gate_watcher.py, /Users/marklehn/Developer/GitHub/bellows/knowledge/decisions/halted-executable-572.md
writes: tools/gate_watcher.py, tests/test_gate_watcher.py, knowledge/dev-logs/gate-watcher-staleness-dev-2026-08-27.md, knowledge/qa/evidence/gate-watcher-staleness-2026-08-27/pytest_full.txt, knowledge/qa/evidence/gate-watcher-staleness-2026-08-27/probes-raw.txt, knowledge/qa/evidence/gate-watcher-staleness-2026-08-27/qa-receipt.md
open_forks: the general objective-test-suite arc (CEO-raised 2026-08-27; this plan is one instance, the tuyere thread carries the design); whether the daemon should clean consumed requests promptly enough that staleness never appears (would make the check inert, not wrong)
walks: 4
yields: 2, 1, 1, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=CLEAN_x1
coherence: N/A
