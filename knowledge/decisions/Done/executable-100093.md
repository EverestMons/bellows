# bellows — THE DASHBOARD RELEASES A CLASS HOLD: when a lane holds a `class:` deposit, the footer offers `l`, a confirm names the file and its class, and `y` runs the same `tools/clear_plan.py <hold> --release-class-hold` the CEO pastes today, on this machine, showing its result — a refusal or a non-zero exit is shown, never swallowed; non-class holds get no key; the key handling moves into a method the tests call without curses (thread 291)

**Date:** 2026-09-11 | **Project:** bellows | **Tier:** Small (one file: a pure selector, a mode, a footer, a release method, the key dispatch factored out; seven tests; one mutation manifest; one dev-log) | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** full-suite (Rule 21 — `dashboard.py` imports `bellows` and `status`; `pytest tests/ -q`) | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** after_qa_step | **known_failures:** 0 | **Discharges:** thread 291

**auto_close:** false

**Post-close:** no daemon restart — the dashboard is a viewer, and a running one picks up the new code when the CEO next opens it (`.venv/bin/python dashboard.py`). One doctrine sentence, the CEO's act after the merge: MACHINE_SETUP §6's release line gains "or the dashboard's `l` key, which runs the same command after a confirm on this machine". Then `tuyere.threads done 291` (a work thread). The dashboard's first live release is the CEO's next class hold.

**Depends on:** thread 291 (CEO direction 2026-09-11, session d04ebd33: "a built in button in bellows dashboard" for releasing a plan; filed as the first proof of a release performed by a program on the CEO's behalf, before the hub of thread 292) and bellows #100087 (Done tonight: the dashboard kickstarts only its own root's agent — the same file, landed first). Clone origin by kind and layout: `Done/executable-100087.md` (the same file and test file, `patch.object` seams so no test reaches a real tool, the two-commit DEV, the full-suite QA) and `Done/executable-100079.md` (the confirm-then-act restart key this plan's key copies).

**Tier computed (§1):** **T1** — T-1 fires (the dashboard gains a path that runs a write-bearing tool); T-6 does not (the doctrine sentence is the CEO's act after, not this plan's edit); T-2 does not (no live write — every test patches the subprocess, and the QA never runs a real release).

## CEO Context

Tonight you released five class holds by pasting a command I handed you. The dashboard already lists every lane's `ready-` and `hold-` files with each hold's reason, and it already has one confirm-then-act key, `r` for restart. This plan adds the second: when a lane holds a deposit whose reason is `class:<name>`, the footer offers `l`; pressing it shows `Release <file> (<class>)? (y/n)`; `y` runs exactly the release command you run today — `tools/clear_plan.py <hold> --release-class-hold`, on this machine, with its checks intact (it refuses a non-class hold, re-runs the cycle check and the lint, writes the clearance `cleared_by=clear_tool`, renames the file for the daemon to claim) — and shows the tool's first line on success or its error on failure. Any other key cancels. A hold for any other reason, such as a stale checkout, gets no key: those recover differently. The act stays yours, at the keyboard of the machine that holds the deposit; the hub (thread 292) later moves the same act behind a button.

## What this changes

1. **`dashboard.py`** — (a) a pure function `class_hold_rows(deposit_rows) -> list` beside `assemble_state` (:108): the rows with `status == "HOLD"` and `reason` starting with `class:`, sorted by `file`, so the target is deterministic whatever order `os.listdir` returns; (b) `render_screen` (:217) accepts a fourth mode, `confirm_release`, whose footer is `Release <file> (<reason>)? (y/n)` for `state["release_target"]`, and in `normal` mode appends `  l release <file>` to the keybar when `class_hold_rows(state["deposit_rows"])` is non-empty (`<file>` the first row), and shows `state["release_note"]`, when present, on the row directly above the footer; (c) `CursesShell` (:392) gains `release_target = None` and `release_note = None`, and `_do_release(self, row)` runs `subprocess.run([sys.executable, str(self.bellows_root / "tools" / "clear_plan.py"), os.path.join(row["dir"], row["file"]), "--release-class-hold"], cwd=str(self.bellows_root), capture_output=True, text=True, timeout=120)` and sets `release_note` to the first line of stdout when the exit is 0, else to `release FAILED (exit <rc>): <the last non-empty line of stderr, else of stdout>`; a `subprocess.TimeoutExpired` sets `release FAILED (timed out after 120 s)`; it then returns to `normal` mode and clears `release_target`; (d) the key dispatch of `_main_loop` (:559–575) moves into `_handle_key(self, key, state, stdscr=None) -> str | None` (`stdscr` passed through to `_do_restart(stdscr)`, which takes it today; the tests call it without one) — `r`, `q` and their `y` confirmations exactly as today (it returns `"quit"` where the loop returned), plus `l`/`L` in `normal` (only when `class_hold_rows(state["deposit_rows"])` is non-empty: `release_target` becomes its first row and the mode `confirm_release`), and in `confirm_release` `y`/`Y` first writes `Releasing <file> …` on the footer row and refreshes when `stdscr` is given — the release blocks the loop while the tool re-runs the cycle check and the lint, typically tens of seconds — then calls `_do_release(self.release_target)`, while any other key returns to `normal`; `_main_loop` passes `release_target` and `release_note` into the state it renders and calls `_handle_key`.
2. **`tests/test_dashboard.py`** — seven tests in the file's own shape (`_make_state`, `_texts`, `render_screen(state, 50, 120, mode=…)`; `CursesShell(bellows_root=tmp_path)` with `(tmp_path / "config.json").write_text("{}")`; `patch.object` on `dashboard.subprocess.run` — no test runs the real tool): (t1) `TestClassHoldRows::test_only_class_holds_sorted` — a `READY` row, a `HOLD` row with `stale-checkout`, and two `HOLD` rows with `class:shop-infra` named `hold-b.md` and `hold-a.md` → exactly the two class rows, `hold-a.md` first; (t2) `TestReleaseFooter::test_offers_release_for_a_class_hold` — the normal footer contains `l release hold-a.md`; (t3) `TestReleaseFooter::test_no_release_key_without_a_class_hold` — with only the `stale-checkout` hold the footer has no `l release`; (t4) `TestReleaseFooter::test_confirm_release_footer` — `mode="confirm_release"` with `release_target` set → the footer reads `Release hold-a.md (class:shop-infra)? (y/n)`; (t5) `TestDoRelease::test_runs_the_same_command_with_the_target_path` — the patched run returns `returncode=0`, stdout `Released class hold: a.md\n…`; after `_do_release(row)` the one call's argv is exactly `[sys.executable, str(tmp_path / "tools" / "clear_plan.py"), os.path.join(row["dir"], row["file"]), "--release-class-hold"]` with `cwd=str(tmp_path)`, and `release_note == "Released class hold: a.md"`; (t6) `TestDoRelease::test_nonzero_exit_is_shown` — `returncode=1`, stderr `ERROR: cycle_check gate: CONTINUE (BAR_MET required) — file left held` → `release_note` starts with `release FAILED (exit 1):` and ends with that line, and `render_screen` with that note shows it above the footer; (t7) `TestHandleKey::test_confirm_cancels_and_l_needs_a_class_hold` — in `confirm_release`, `_handle_key(ord("n"), state)` returns to `normal` and the patched `_do_release` is not called; in `normal`, `_handle_key(ord("l"), <state with no class hold>)` leaves the mode `normal`, and with a class hold sets `confirm_release` and the target.
3. **`knowledge/mutants/dashboard-release-key.json`** — `target` `dashboard.py`, four mutants, each `expect_fail` a class-qualified node id: (m1) the `class:` filter dropped from `class_hold_rows` → t1; (m2) `"--release-class-hold"` dropped from the argv (the bare `clear_plan.py <hold>` is re-entry, which loops — MACHINE_SETUP §6) → t5; (m3) the non-zero branch reported as success → t6; (m4) the `y` test removed in `confirm_release`, so any key releases → t7.
4. **Not changed:** the `r` and `q` keys and their texts; `_spawn_child` and #100087's own-root rule; `tools/clear_plan.py` — the dashboard runs the same tool, and no new release path exists; the depositor; the PTY smoke test and its guard.

## Why this exists

A release is a deterministic act the CEO performs by pasting a command (the action census, thread 293: the release is a keyboard act a program can perform). Putting it behind a key that names what it releases is the smallest proof that a program can perform the CEO's act on the CEO's word — the proof the hub needs before any button moves it off the keyboard.

## What this does NOT do

- Release anything that is not a `class:` hold, or bypass any check `release_class_hold` makes.
- Run a real release in the QA — a real release writes the live lifecycle DB's clearance table; the first live use is the CEO's next class hold.
- Add a cursor or row selection: the target is the first class hold by name, and the confirm names it.
- Reach another machine: the dashboard releases only what its own machine's lanes hold.

## MUST-PRESERVE

- ⛔ **Nothing is released without `y` on a footer that names the file and its class** (t4, t7).
- ⛔ **The dashboard runs the same command the CEO runs,** with exactly those arguments (t5) — every refusal of the tool stands.
- ⛔ **A failure is shown, never swallowed** (t6).
- ⛔ **`r` and `q` behave exactly as before** — the factored `_handle_key` returns `"quit"` where the loop returned, and the PTY smoke test still presses `q` then `y`.
- ⛔ **No test runs the real tool or touches a real lane** — `dashboard.subprocess.run` is patched in t5 and t6, and every state is built with `_make_state` or under `tmp_path`.
- ⛔ **Every `expect_fail` is a class-qualified node id**, and the mutation run is redirected into its deposit, never piped.
- ⛔ **The thread-262 stop:** a QA step that must change production code STOPS and requests a verdict rather than committing.

## Numbers discipline — measured 2026-09-11 by the Planner (bellows `031e2a3`, governance `76f757f4`, daemon pid 3106 under the agent)

| # | pin | value | how to re-derive |
|---|---|---|---|
| P1 | ⛔ the dashboard, by line | `dashboard.py`: `assemble_state(bellows_root, child_proc=None)` :108 builds `deposit_rows` (:164–191) from each `watched_projects` lane — a `READY` row per `ready-*.md` and a `HOLD` row per `hold-*.md` with `reason` read from the `.hold.json` sidecar's `hold_reason` (`(unreadable)` on a read error), each row `{"file", "status", "reason", "dir"}`; `render_screen(state, height, width, mode="normal", has_colors=False)` :217 — modes `normal`, `confirm_restart`, `confirm_quit` (:224), the footer :357–367 (`Restart daemon? (y/n)`, `Quit dashboard and stop daemon? (y/n)`, else `r restart  q quit` or `r relaunch  q quit`); `CursesShell.__init__(self, bellows_root=None)` :392 with `self.mode = "normal"` :395; `_main_loop` :502 renders `assemble_state` every refresh and dispatches keys at :559–575 (`r`→`confirm_restart`, `q`→`confirm_quit`, `y` confirms, any other key returns to `normal`) | `grep -nE 'def \|self\.mode\|ord\(' dashboard.py`; `sed -n 164,191p;357,367p;559,575p dashboard.py` |
| P2 | ⛔ the release tool | `tools/clear_plan.py` `release_class_hold(hold_path)` :79 — allows `hold_reason` starting `class:` (and `held_pending_ceo_release` whose original reason is absent or `class:`), otherwise fails "release_class_hold is for class holds only"; re-runs `cycle_check.run_check` (BAR_MET required) and `plan_lint` (a non-benign FAIL refuses); refuses without a Cycle Manifest `class:` line; writes `lifecycle.write_clearance(<name>, <hash>, <class>, "clear_tool")` to the LIVE DB; renames the hold to the bare name and removes the sidecar; prints `Released class hold: <name>` first and `Daemon will claim within 30 seconds.` last; the entry exits 0 on success and 1 on failure (:305–330) | `sed -n 79,155p;305,330p tools/clear_plan.py` |
| P3 | ⛔ the tests to clone | `tests/test_dashboard.py` (37 tests): `_texts(rows)` :17, `_make_state(**overrides)` :26 with `deposit_rows: []`, `TestRenderConfirmRestart::test_confirm_restart_replaces_footer` :163 (render in a mode, read `lines[-1]`), `TestPTYSmoke::test_pty_launch_refresh_quit` :380 (presses `q` then `y`; its subprocess patches `bellows._agent_loaded`, hotfix `d3456b9`); `tests/test_daemon_agent.py` t5 (`CursesShell(bellows_root=tmp_path)` after `config.json` is written, `patch.object` seams) | the two files at those lines |
| P4 | ⛔ the mutation tool and the manifest form | `tools/mutation_check.py <manifest> [--repo-root] [--keep-sandbox] [--python] [--timeout]`; the manifest form `{"target", "mutants": [{"name", "why", "anchor", "replacement", "expect_fail"}]}` (`knowledge/mutants/dashboard-agent-root.json`, #100087); a clean run's last line `MUTATION: <n> killed, 0 survived, 0 error` | the file; `--help` |
| P5 | the measured need | 2026-09-11: the CEO released five class holds (#100083's redeposit, #100084, #100086, #100087, #100088) by pasting `tools/clear_plan.py <hold> --release-class-hold` from a message; the action census (#100085, thread 293) classes the release as a deterministic CEO-keyboard act | the day's baton block; `governance/knowledge/research/action-census-2026-09-11.tsv` |
| P6 | in-flight; class; interpreter | the plans for threads 299, 298, 296 and 304 closed and queued ahead of this one; writes: `dashboard.py`, `tests/test_dashboard.py`, the manifest, the run file, the dev-log, two QA evidence files → **shop-infra** (`_assign_class`, walk 0) — HOLDS at admission, the CEO releases; the bellows venv, Python 3.12.14 | `.venv/bin/python status.py`; `_assign_class` |

## Drafting Cycle

**Tier:** **T1** — T-1 fires. **Walk register:** /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-dashboard-release-key-2026-09-11.md
**Walks:** walk 0 pinned (P1–P6 measured on bellows `031e2a3`; clone-diff against `Done/executable-100087.md` and `Done/executable-100079.md` run: FACTS, ARTEFACTS, STRUCTURE); `fold_check --save-baseline` ARMED on v0 before any fold; re-saved after every intended edit; every lens commit through `scripts/lens_commit.py`; the tool run bare, its exit read; no lens or walk number in any `--desc`; `lens_order_check` after every walk.

- Weak spots:          w1 2 folded — instruction 2 / record 0; w2 1 folded — instruction 0 / record 1
- Destruction:          w1 dry; w2 dry
- Vulnerabilities:      w1 dry; w2 dry
- Integration-record:   w1 dry; w2 dry
- ACID:                 w1 dry; w2 dry
**Closing:** WARM close after walk 2 — BAR MET (T1), thread 291's key. Two walks: 2 → 0 (walk 1 gave the factored key handler the screen the restart key needs and made the footer say the release is running while the tool blocks; walk 2 removed a drafting placeholder from the record and was dry on every lens). Every lens commit through `lens_commit.py`, the tool run bare, its exit read; the close through `close_cycle.py`. Deposit via `ready-` after the plans for threads 299, 298, 296 and 304 close (P6); HOLDS on class shop-infra, the CEO releases; after the merge: the CEO's MACHINE_SETUP §6 sentence, `threads done 291`.

## Cycle Manifest
tier: T1
target: dashboard.py
class: shop-infra
reads: dashboard.py, status.py, tools/clear_plan.py, depositor.py, tests/test_dashboard.py, tests/test_daemon_agent.py, tools/mutation_check.py, tools/check_deposit.py, knowledge/decisions/Done/executable-100087.md, knowledge/decisions/Done/executable-100079.md, knowledge/mutants/dashboard-agent-root.json
writes: dashboard.py, tests/test_dashboard.py, knowledge/mutants/dashboard-release-key.json, knowledge/mutants/dashboard-release-key.run.txt, knowledge/development/dev-log-dashboard-release-key-2026-09-11.md, knowledge/qa/evidence/dashboard-release-key-qa-receipt-2026-09-11.md, knowledge/qa/evidence/dashboard-release-key-suite-2026-09-11.txt
mutants: knowledge/mutants/dashboard-release-key.json
open_forks: 1. a cursor over the deposit rows, when a lane holds more than one class hold at once; 2. the same act behind a hub button (thread 292), after this proves the act; 3. MACHINE_SETUP §6's release line (the CEO's act, Post-close)
walks: 2
yields: 2, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=VACUOUS, propagation_check=DIVERGENT:13
coherence: 2/2 body walks named in the register (3 register rows; walk-token match, NOT row coverage)
fold_baseline: governance/knowledge/decisions/drafts/.executable-bellows-dashboard-release-key.md.foldcheck.json

---

## STEP 1 — DEV (a selector, a mode, a release method, the key dispatch factored; seven tests; the mutation run; two commits)

> ⛔ **Every item starts by re-establishing the root** — `cd "$(git rev-parse --show-toplevel)" && test -f gates.py && echo TREE_OK` — HALT unless TREE_OK. ⛔ **The interpreter is `/Users/marklehn/Developer/bellows/.venv/bin/python`, ABSOLUTE.** ⛔ Never run the daemon, `run_plan`, a claim, the dashboard itself, or `tools/clear_plan.py` in any mode — the release is observed only through t5 and t6 with `subprocess.run` patched; the live `lifecycle.db` is never opened by this step; `T=$(mktemp -d /tmp/release-key.XXXXXX)` for scratch, removed at the end.
>
> **Scope:**
> - `dashboard.py`
> - `tests/test_dashboard.py`
> - `knowledge/mutants/dashboard-release-key.json`
> - `knowledge/mutants/dashboard-release-key.run.txt`
> - `knowledge/development/dev-log-dashboard-release-key-2026-09-11.md`
>
> **Item 1 — re-derive P1, P2 and P3 and HALT on a mechanism mismatch** (a line-number drift is not a mismatch; a release key or a `confirm_release` mode already in the dashboard, deposit rows without `dir`, or a `release_class_hold` that no longer refuses a non-class hold, IS one). Paste each pin's re-derived line beside it.
> **Item 2 — write the failing tests FIRST:** t1–t7 as *What this changes* 2 (red: `AttributeError` on `class_hold_rows`, `_do_release`, `_handle_key`; the footer tests on the missing text). Run the file; paste the red summary line with each test's reason.
> **Item 3 — the edits** as *What this changes* 1; then the file green (every test, t1–t7 among them, the PTY smoke test still green), then the FULL suite green (`N passed, 2 skipped` — `test_gate_watcher`'s live-DB skip and `test_fallback_live_wal_window`'s version gate).
> **Item 4 — first commit**, gated on the FULL suite AND the pre-check with the stage flag (#100067), path-scoped: `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ -q && /Users/marklehn/Developer/bellows/.venv/bin/python tools/check_deposit.py /Users/marklehn/Developer/bellows/knowledge/decisions/in-progress-executable-<id>.md 1 --wt "$(git rev-parse --show-toplevel)" --expect-missing knowledge/development/dev-log-dashboard-release-key-2026-09-11.md knowledge/mutants/dashboard-release-key.run.txt && git add dashboard.py tests/test_dashboard.py knowledge/mutants/dashboard-release-key.json && git commit -F <msg-file> -- dashboard.py tests/test_dashboard.py knowledge/mutants/dashboard-release-key.json` — three files (the manifest rides this commit so the mutation run's `HEAD:` archive contains it); the message tagged with the plan id and `thread 291`.
> **Item 5 — the mutation run, REDIRECTED into `knowledge/mutants/dashboard-release-key.run.txt` (a Deposit):** `/Users/marklehn/Developer/bellows/.venv/bin/python tools/mutation_check.py knowledge/mutants/dashboard-release-key.json > knowledge/mutants/dashboard-release-key.run.txt 2>&1`; the last line must read `MUTATION: 4 killed, 0 survived, 0 error` — a survivor is a test to write, not a mutant to delete.
> **Item 6 — the dev-log** `knowledge/development/dev-log-dashboard-release-key-2026-09-11.md` under the four headings declared below; `## Pins re-derived (P1, P2, P3)` opens with P2's value cell pasted verbatim, whole, to its last character — ⛔ the cell ends with the words `1 on failure (:305–330)`; paste through those words, then stop. Under `## Failing-first (red, then green)` the red line with each reason and the green line; under `## The command and the refusal (t5, t6)` the two tests' assertions quoted with their outcomes; under `## Mutation run` the run file's last line. **Second commit**, gated on the FULL suite and the pre-check bare (`… tools/check_deposit.py … 1 --wt "$(git rev-parse --show-toplevel)"`, no stage flag — the run file and dev-log now exist), path-scoped to the run file and the dev-log. Last act: `[ -n "$T" ] && [ -d "$T" ] && rm -rf "$T"`.
> **Headings:** `## Pins re-derived (P1, P2, P3)`; `## Failing-first (red, then green)`; `## The command and the refusal (t5, t6)`; `## Mutation run`
> **Verbatim:** `## Pins re-derived (P1, P2, P3)` ← P2
>
> **Deposits:**
> - `knowledge/mutants/dashboard-release-key.json`
> - `knowledge/mutants/dashboard-release-key.run.txt`
> - `knowledge/development/dev-log-dashboard-release-key-2026-09-11.md`
>
> **Post-conditions:** every test in the file green, t1–t7 among them and the PTY smoke test; the full suite `N passed, 2 skipped` with no `failed`; the mutation run's last line `MUTATION: 4 killed, 0 survived, 0 error`; two DEV commits — the first carrying the three files, the second the run file and the dev-log; the dev-log's four headings present as full lines with P2's cell whole; `git status --porcelain` empty after the second commit; `tools/clear_plan.py` unchanged.

## STEP 2 — QA (full suite; the seven tests by name; the receipt)

> ⛔ **Every item starts by re-establishing the root** — `cd "$(git rev-parse --show-toplevel)" && test -f gates.py && echo TREE_OK` — HALT unless TREE_OK. Interpreter ABSOLUTE; read-only beyond the two evidence files; `T=$(mktemp -d /tmp/release-key-qa.XXXXXX)`; `tools/clear_plan.py` is not run, and the dashboard is not started.
>
> **Item 1 — the full suite REDIRECTED not piped:** `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ --tb=short -q > knowledge/qa/evidence/dashboard-release-key-suite-2026-09-11.txt 2>&1`; the summary line quoted in the receipt as `N passed` with the skips named as `two skips (test_gate_watcher live-DB; test_fallback_live_wal_window version gate)` — never the word the Rule 20 block scans for.
> **Item 2 — the seven tests by name:** `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/test_dashboard.py -v -k "ClassHold or ReleaseFooter or DoRelease or HandleKey or PTYSmoke" -p no:cacheprovider > "$T/named.txt" 2>&1`; paste its eight node lines (the seven and the PTY smoke test) into the receipt, each `PASSED`.
> **Item 3 — production writes, stated exactly:** none outside the two evidence files; `$T` removed; no lane file, no live lifecycle row, no daemon act, no release.
> **Item 4 — receipt** `knowledge/qa/evidence/dashboard-release-key-qa-receipt-2026-09-11.md`: `numstat` over the DEV commits (`<base>..<dev>`, five files); a `## Verification` table with one row per Item 1–3, each quoting the line it rests on — ⛔ the status cell holds exactly one token (`✅`) and no positive row's text carries a hedging keyword; then RUN the canonical Rule 20 block (`$ELUVIAN_WRAP_ROOT/RULE_20_SELF_CHECK_BLOCK.md`) with `plan_slug: dashboard-release-key-2026-09-11`, `qa_report_path` and `evidence_dir` absolute under `$(git rev-parse --show-toplevel)/knowledge/qa/evidence/`, `required_evidence_files: ["dashboard-release-key-suite-2026-09-11.txt"]`, and APPEND its stdout — the banner `Rule 20 — QA Self-Check Results` and the closing `PASSED — SELF-CHECK PASSED` line are the block's output, never hand-authored; a `FAILED` stdout goes into the receipt and the step STOPS (thread 262).
> **Item 5 — commit**, path-scoped and gated: `grep -Eq '^[0-9]+ passed' knowledge/qa/evidence/dashboard-release-key-suite-2026-09-11.txt && ! grep -Eq '[0-9]+ (failed|error)' knowledge/qa/evidence/dashboard-release-key-suite-2026-09-11.txt && /Users/marklehn/Developer/bellows/.venv/bin/python tools/check_deposit.py /Users/marklehn/Developer/bellows/knowledge/decisions/in-progress-executable-<id>.md 2 --wt "$(git rev-parse --show-toplevel)" && git add knowledge/qa/evidence/dashboard-release-key-qa-receipt-2026-09-11.md knowledge/qa/evidence/dashboard-release-key-suite-2026-09-11.txt && git commit -F <msg-file> -- knowledge/qa/evidence/dashboard-release-key-qa-receipt-2026-09-11.md knowledge/qa/evidence/dashboard-release-key-suite-2026-09-11.txt`. ⛔ A QA step that must change production code STOPS and requests a verdict (thread 262).
>
> **Deposits:**
> - `knowledge/qa/evidence/dashboard-release-key-qa-receipt-2026-09-11.md`
> - `knowledge/qa/evidence/dashboard-release-key-suite-2026-09-11.txt`
>
> **Scope:**
> - `knowledge/qa/evidence/dashboard-release-key-qa-receipt-2026-09-11.md`
> - `knowledge/qa/evidence/dashboard-release-key-suite-2026-09-11.txt`
>
> **Post-conditions:** the suite file's summary line is `N passed, 2 skipped` with N ≥ the DEV's count and no `failed`; Item 2's eight node lines pasted, each `PASSED`; the receipt's `## Verification` table has three rows and closes with the block's own PASSED line; one QA commit carrying the two evidence files.
