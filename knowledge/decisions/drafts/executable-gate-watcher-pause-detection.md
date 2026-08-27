# bellows — executable: gate_watcher pause detection — key the poll on the verdict-request file, not `plans.lifecycle_state` (the corrective owed by exec-569; closes tuyere thread 12)

**Date:** 2026-08-26 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** targeted (the extended watcher tests) + full suite at QA | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always

**auto_close:** false

**Depends on:** tuyere thread 12 (opened 2026-08-26, this corrective priced first per the batch-4 wrap); the exec-569 verdict's Planner NOTE (the defect record); LESSONS.md 2026-08-26 "a live canary must be fired in the STATE the tool exists to discriminate"; `bellows-watcher-per-deposited-plan` condition 1 (the correct surface, named there since 2026-08-12).

## Why this exists

`tools/gate_watcher.py` (shipped exec-569) polls `plans.lifecycle_state` for a pause. That column has NEVER held `awaiting_verdict` — the daemon writes that value to `steps.status` only, and only when gates FAIL (P2). A cleanly paused plan therefore reads `in_progress`, indistinguishable from a running one, and the watcher cannot report the one transition its consumer most needs (measured twice on 2026-08-26: the 568 session watcher timed out over a paused plan; the 569 one never fired). The real pause signal is the file the daemon writes at pause: `verdicts/pending/verdict-request-<slug>-step-<N>.md` (P3). This plan re-keys pause detection onto that file, keeps the DB read for everything it is actually authoritative for (identity, terminal states, gate failures), and proves the fix with tests and live probes that CONSTRUCT the paused state.

## What this plan does NOT do

- **No daemon/depositor/gates/receipt changes.** The write set is one tool edit + one test-file extension + logs. `tools/deposit_receipt.py` is untouched: the spawned watcher resolves the pending dir from its own root by the same split-path law it already uses for the DB.
- **No semantic change to any existing output line.** Every currently-earnable `WATCH:` line stays byte-identical for the states it correctly reports; the fix ADDS the `awaiting-verdict` phase that was unreachable.
- **No memory writes** (sandbox-denied to agents; the Planner closes thread 12 and updates the watcher memory's anti-pattern note at close).

## Numbers discipline

⚠️ **Measured 2026-08-26 by the Planner; RE-DERIVE each pre-flight — yours supersede and you say so; mismatch on a load-bearing pin → HALT.**

| id | pin | value | anchor/probe |
|---|---|---|---|
| P1 | reachable plan states | `SELECT DISTINCT lifecycle_state FROM plans` → `abandoned, closed, halted` (+`in_progress` while any plan runs — 3 rows at authoring because none was in-flight); `awaiting_verdict` ABSENT in live data | sqlite3 mode=ro on the LIVE db |
| P2 | who writes `awaiting_verdict` | `bellows.py:1097` and `:1230` — `record_step_end(status=…)` into **steps.status**, and only on `gate_result["passed"] == False`; NO writer targets `plans.lifecycle_state` with it (the schema CHECK arm at `lifecycle.py:46` is phantom for plan rows) | `/usr/bin/grep -rnF "awaiting_verdict" bellows.py lifecycle.py` |
| P3 | pause-file writer + name form | `verdict.py:180-188` `post_verdict_request` writes `verdicts/pending/verdict-request-{slug}-step-{N}.md` where `slug = slug_from_path(plan_path)` (`verdict.py:85-95` strips `in-progress-`/`verdict-pending-`/`executable-`/`diagnostic-` + `.md`); the claim rename makes the plan file id-named, so post-claim slug == str(plan_id) — measured artifacts `processed-verdict-568-step-1.md`, `-569-step-1/2.md` | read both functions; `ls verdicts/resolved/` |
| P4 | the seam | `tools/gate_watcher.py` `read_state()` `:35-65` — already derives `plan_id`; `TERMINAL` set at `:32`; `judge_transition` `:68-81` formats any phase generically (no change needed there) | read the file |
| P5 | test baseline | `tests/test_gate_watcher.py` collects **9 tests**; full suite baseline **1531 passed** (exec-569 QA) | `pytest tests/test_gate_watcher.py -q --collect-only` |

## MUST-PRESERVE

- ⚠️ **`/usr/bin/grep` for ALL probes (`-F` unless a regex is stated); zero-match exits 1 — never `&&`-chain a probe.**
- ⚠️ **THE SPLIT-PATH LAW:** `lifecycle.db`, `verdicts/`, and `logs/` are untracked — the tool resolves them relative to its own installed location at RUNTIME; tests and probes inject `db_path`/`pending_dir` explicitly. When `--db-path` is passed and `--pending-dir` is not, the pending dir derives from the db-path's parent (`<db-dir>/verdicts/pending`) so a worktree-run probe against the live DB reads the live pending dir.
- ⚠️ **The watcher stays a REPORTER** — read-only DB URI, no writes outside its own log; the pending-dir read is `glob` only.
- ⚠️ **Plan-scoped isolation** (`bellows-watcher-per-deposited-plan` condition 4): the pending glob is keyed to THIS plan's id — a foreign plan's verdict-request must not change this watcher's output (tested).
- ⚠️ **A stray pending file must not mask a terminal state:** the pending check runs only when the DB state is non-terminal.
- ⚠️ **All 9 existing watcher tests stay green unmodified** — the change is additive at the call shape (`read_state` gains an optional `pending_dir` kwarg).
- ⚠️ **Worktree dispatch; every claim cites file:line; absence claims carry positive controls; EVERY DATE IS A FIXED LITERAL.**

## STEP 1 — DEV (the fix + constructed-state tests)

> **Task A — worktree discipline.** `cd "$(git rev-parse --show-toplevel)" && test -f tools/gate_watcher.py && echo TREE_OK` — HALT unless TREE_OK. Resume probe: `/usr/bin/grep -cF "awaiting-verdict" tools/gate_watcher.py; true` → 0 = full run; ≥1 = resume at Task C.
>
> **Task B — edit `tools/gate_watcher.py`** (Edit-style anchored changes, NOT a rewrite; each anchor must match exactly once):
>
> 1. **Docstring**, after the "stable state query" paragraph, add:
>    ```
>    Pause detection reads verdicts/pending/, not the DB: plans.lifecycle_state
>    never takes 'awaiting_verdict' (the daemon writes that to steps.status only,
>    and only on gate failure — measured 2026-08-26), so the verdict-request file
>    IS the pause signal. The DB stays authoritative for identity, terminal
>    states, and gate failures.
>    ```
> 2. **Imports**: add `import glob` (stdlib group, alphabetical). NO new module constant — the pending dir derives from the resolved db path in one place (next item), which collapses the live-default and `--db-path` cases into the same expression (`os.path.dirname(os.path.abspath(_DB))` IS `_ROOT`).
> 3. **`read_state` signature** → `def read_state(name, db_path=None, pending_dir=None):`, and inside, after `path = db_path or _DB` (unchanged): `pend = pending_dir or os.path.join(os.path.dirname(os.path.abspath(path)), "verdicts", "pending")`.
> 4. **The pause branch**, inserted after the `fails` query, replacing the current bare return: when `state not in TERMINAL`, `hits = sorted(os.path.basename(p) for p in glob.glob(os.path.join(pend, f"verdict-request-{plan_id}-step-*.md")))`; if `hits`, return phase `"awaiting-verdict"` with `plan_id`, `gate_failures` as before, plus `"pending": hits`; otherwise return exactly the current dict. Terminal states return the current dict UNCONDITIONALLY (no glob — the stray-file law).
> 5. **`judge_transition`**: after the `tail`/`pid_part` lines, add `pend_part = " pending=" + ",".join(cur["pending"]) if cur.get("pending") else ""` and append it to the returned f-string. Every existing phase renders byte-identically (`pending` absent → empty string).
> 6. **`main`**: add `ap.add_argument("--pending-dir", default=None, help="verdicts/pending dir (default: derived from --db-path's parent, else this tool's bellows root)")`; thread `pending_dir=args.pending_dir` through BOTH `read_state` call sites.
>
> **Task C — extend `tests/test_gate_watcher.py`** with a `TestPauseDetection` class (temp-dir fixtures; each test CONSTRUCTS its state — the discriminating-state law):
> 1. `test_paused_plan_reports_awaiting_verdict` — temp DB row `in_progress` id N + temp pending dir containing `verdict-request-N-step-2.md` → `phase == "awaiting-verdict"`, `pending == ["verdict-request-N-step-2.md"]`.
> 2. `test_foreign_plan_request_is_invisible` — pending dir contains ONLY `verdict-request-<N+1>-step-1.md` → `phase == "in_progress"`, no `pending` key.
> 3. `test_terminal_state_ignores_stray_request` — DB row `closed` + a stray MATCHING request file in the pending dir → `phase == "closed"` and no `pending` key. The stray file is the proof: if the terminal path consulted the glob and honored hits, this assertion breaks. (A nonexistent-dir variant proves nothing — `glob` returns `[]` there without raising.)
> 4. `test_empty_pending_dir_reports_in_progress` — the negative control for test 1: same DB, empty dir → `in_progress`.
> 5. `test_pending_dir_derived_from_db_path` — db at `<tmp>/x/lifecycle.db`, request file at `<tmp>/x/verdicts/pending/`, call with `db_path=…` and NO `pending_dir` → `awaiting-verdict`.
> 6. `test_transition_line_carries_pending_names` — `judge_transition(None, {paused-state})` → line contains `awaiting-verdict` and `pending=verdict-request-N-step-2.md`.
> 7. `test_resume_transition_logged` — prev paused, cur `in_progress` without `pending` → non-None line (the resume edge is a reportable transition).
> **Targeted run:** `python3 -m pytest tests/test_gate_watcher.py -q` → 16 passed (9 baseline P5 + 7 new; re-derive if your baseline differs), 0 failed. DEV runs NO full suite.
>
> **Task D — dev log** `knowledge/dev-logs/gate-watcher-pause-dev-2026-08-26.md`: the diff summary, each pin re-derivation (P1-P5, yours vs the table, say "supersedes" where they differ), the targeted-test tail pasted raw.
>
> **Task E — commit** (worktree; message `[<id>] gate-watcher-pause: pause detection keyed on verdict-request file; 7 constructed-state tests`): `cd "$(git rev-parse --show-toplevel)" && git add tools/gate_watcher.py tests/test_gate_watcher.py knowledge/dev-logs/gate-watcher-pause-dev-2026-08-26.md && git commit`. Verify: `git show --stat HEAD | cat` lists exactly those 3 files.
>
> **Deposits:**
> - `tools/gate_watcher.py` (modified — the pause branch, `--pending-dir`, docstring)
> - `tests/test_gate_watcher.py` (extended — `TestPauseDetection`, 7 tests)
> - `knowledge/dev-logs/gate-watcher-pause-dev-2026-08-26.md`
>
> **Scope:**
> - `tools/gate_watcher.py`
> - `tests/test_gate_watcher.py`
> - `knowledge/dev-logs/gate-watcher-pause-dev-2026-08-26.md`

## STEP 2 — QA (FULL suite + live probes in BOTH states)

> **Item 1 — full suite.** `cd "$(git rev-parse --show-toplevel)"`; `python3 -m pytest tests/ --tb=short -q 2>&1 | cat | tee knowledge/qa/evidence/gate-watcher-pause-2026-08-26/pytest_full.txt` — 0 failed (record the count; derivation vs the 1531 P5 baseline).
> **Item 2 — live probes, full tails pasted to `probes-raw.txt`.** Resolve this plan's own minted id first: `sqlite3 "file:/Users/marklehn/Developer/GitHub/bellows/lifecycle.db?mode=ro" "SELECT id FROM plans WHERE deposit_placeholder_name='executable-gate-watcher-pause-detection.md' ORDER BY id DESC LIMIT 1;"` → `$PID`. Scratch dir: `SCRATCH=$(mktemp -d)`.
> 1. **Ordinary state (negative control):** `python3 tools/gate_watcher.py --status executable-gate-watcher-pause-detection.md --db-path /Users/marklehn/Developer/GitHub/bellows/lifecycle.db --pending-dir "$SCRATCH"` → `WATCH: in_progress id=$PID` (this plan IS in_progress during its own QA), exit 0.
> 2. **DISCRIMINATING state:** `touch "$SCRATCH/verdict-request-$PID-step-1.md"`; same command → `WATCH: awaiting-verdict id=$PID pending=verdict-request-$PID-step-1.md`, exit 0. **This output is unreachable on the pre-fix tool** — the probe is earnable only if the pause branch works against the LIVE db.
> 3. **Isolation:** `rm "$SCRATCH/verdict-request-$PID-step-1.md" && touch "$SCRATCH/verdict-request-999999-step-1.md"`; same command → `WATCH: in_progress id=$PID` (foreign id invisible), exit 0.
> 4. Cleanup: `rm -rf "$SCRATCH"`.
> **Item 3 — hygiene + receipt** `knowledge/qa/evidence/gate-watcher-pause-2026-08-26/qa-receipt.md`: numstat vs the DEV commit (3 files); toplevel asserted; reflog `-n 4` → 0 amends; per-item table; then the Rule 20 block INSIDE a "Verification"-headed section (the 556 placement law).
> **Item 4 — commit the evidence** (worktree; message `[<id>] gate-watcher-pause: QA — full suite + constructed-state live probes`): `cd "$(git rev-parse --show-toplevel)" && git add knowledge/qa/evidence/gate-watcher-pause-2026-08-26/ && git commit`. Verify: `git show --stat HEAD | cat` lists exactly the 3 evidence files.
>
> ⚠️ **Gate note:** pytest summary named above — the gate parses; no benign override pre-declared.
>
> **Deposits:**
> - `knowledge/qa/evidence/gate-watcher-pause-2026-08-26/pytest_full.txt`
> - `knowledge/qa/evidence/gate-watcher-pause-2026-08-26/probes-raw.txt`
> - `knowledge/qa/evidence/gate-watcher-pause-2026-08-26/qa-receipt.md`
>
> **Scope:**
> - `knowledge/qa/evidence/gate-watcher-pause-2026-08-26/pytest_full.txt`
> - `knowledge/qa/evidence/gate-watcher-pause-2026-08-26/probes-raw.txt`
> - `knowledge/qa/evidence/gate-watcher-pause-2026-08-26/qa-receipt.md`

Rule 20 banner (byte-exact, inside the QA receipt's VERIFICATION section):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```

## Drafting Cycle

**Tier:** T1 — one anchored tool edit + additive tests; the defect and its fix surface are both pinned from measurements already on record.

**Walk register:** `bellows/knowledge/research/walk-register-gate-watcher-pause-2026-08-26.md`

**Walks:** walk 0 pinned; **walks 1–3 complete**, genuine sequential five-lens passes — see the register.
**Direction verdict (after walk 1): PROCEED** — the single-seam fix shape held; no direction-class finding.
- Weak spots:          w1 1 folded (instruction 1 / record 0) — the pending-dir double-source collapsed to one expression; w2 dry; w3 dry
- Destruction:         w1 dry; w2 dry; w3 dry
- Vulnerabilities:     w1 1 folded (instruction 1 / record 0) — test 3's non-proof parenthetical replaced with the stray-file proof; w2 dry; w3 dry
- Integration-record:  w1 dry; w2 dry; w3 dry
- ACID:                w1 1 folded (instruction 1 / record 0) — the missing QA evidence commit (Item 4) added; w2 dry; w3 dry
**Cold panel: NOT convened, decided with reasoning** — T1 additive corrective to a read-only reporter; no money path, no destructive step; the 563/569 precedent.
**Conformance (§5):** recorded at the freeze from actual runs — see the register's conformance block (fold grep-verifications, structure count, run_check cycle/lint/register all branched-on).
**Closing:** **walk 3 confirmed walk 2's dry — all five lenses dry twice consecutively, BAR MET.** Instruction series **3 → 0 → 0**. Close is MANUAL (CEO-lane verdicts; auto_close false).

## Cycle Manifest
tier: T1
target: bellows/tools/gate_watcher.py
class: shop-infra
reads: /Users/marklehn/Developer/GitHub/bellows/tools/gate_watcher.py, /Users/marklehn/Developer/GitHub/bellows/verdict.py, /Users/marklehn/Developer/GitHub/bellows/bellows.py, /Users/marklehn/Developer/GitHub/bellows/lifecycle.py, /Users/marklehn/Developer/GitHub/bellows/tests/test_gate_watcher.py
writes: tools/gate_watcher.py, tests/test_gate_watcher.py, knowledge/dev-logs/gate-watcher-pause-dev-2026-08-26.md, knowledge/qa/evidence/gate-watcher-pause-2026-08-26/pytest_full.txt, knowledge/qa/evidence/gate-watcher-pause-2026-08-26/probes-raw.txt, knowledge/qa/evidence/gate-watcher-pause-2026-08-26/qa-receipt.md
open_forks: whether deposit_receipt should ALSO pass --pending-dir explicitly (decided NO here — split-path default suffices; revisit only if a worktree-spawned watcher ever appears); the phantom-enum-arm checker (thread 14) mechanizes the class this bug instantiated
walks: 3
yields: 3, 0, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=CLEAN_x1
coherence: N/A
