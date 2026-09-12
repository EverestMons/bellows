# Dev-log: dashboard-release-key-2026-09-11

## Pins re-derived (P1, P2, P3)

`tools/clear_plan.py` `release_class_hold(hold_path)` :79 — allows `hold_reason` starting `class:` (and `held_pending_ceo_release` whose original reason is absent or `class:`), otherwise fails "release_class_hold is for class holds only"; re-runs `cycle_check.run_check` (BAR_MET required) and `plan_lint` (a non-benign FAIL refuses); refuses without a Cycle Manifest `class:` line; writes `lifecycle.write_clearance(<name>, <hash>, <class>, "clear_tool")` to the LIVE DB; renames the hold to the bare name and removes the sidecar; prints `Released class hold: <name>` first and `Daemon will claim within 30 seconds.` last; the entry exits 0 on success and 1 on failure (:305–330)

P1 re-derived: `assemble_state` :108 confirmed; deposit rows built at :164–191 each with `{"file", "status", "reason", "dir"}`; `render_screen` :217 confirmed three existing modes (`normal`, `confirm_restart`, `confirm_quit`) with footer at :357–367; `CursesShell.__init__` :392 with `self.mode = "normal"` :395; `_main_loop` key dispatch at :559–575 — no `confirm_release` mode, no `class_hold_rows`, no `_do_release`, no `_handle_key` in the pre-edit tree. No mechanism mismatch.

P3 re-derived: `_texts` :17, `_make_state` :26, `TestRenderConfirmRestart` :163, `TestPTYSmoke` at line 380+; `test_daemon_agent.py` `CursesShell(bellows_root=tmp_path)` after `config.json` written, `patch.object` seams.

## Failing-first (red, then green)

Red (6 of 7 new tests failed; t3 passes correctly as it tests absence of `l release` which is absent before the edit):

- `TestClassHoldRows::test_only_class_holds_sorted` — `AttributeError: module 'dashboard' has no attribute 'class_hold_rows'`
- `TestReleaseFooter::test_offers_release_for_a_class_hold` — `AssertionError`: `l release hold-a.md` absent from footer
- `TestReleaseFooter::test_confirm_release_footer` — `AssertionError`: footer not `Release hold-a.md (class:shop-infra)? (y/n)`
- `TestDoRelease::test_runs_the_same_command_with_the_target_path` — `AttributeError: 'CursesShell' object has no attribute '_do_release'`
- `TestDoRelease::test_nonzero_exit_is_shown` — `AttributeError: 'CursesShell' object has no attribute '_do_release'`
- `TestHandleKey::test_confirm_cancels_and_l_needs_a_class_hold` — `AttributeError: 'CursesShell' object has no attribute '_do_release'`

Green after edits: `44 passed in 5.53s` (all 7 new tests green, PTY smoke test green).

Full suite: `2313 passed, 2 skipped` — `test_gate_watcher` live-DB skip and `test_fallback_live_wal_window` version gate.

Note: one render fix was required — `feed_available` originally reserved only 1 row for the footer; with `release_note` a second row must be reserved (`_footer_rows = 2 if state.get("release_note") else 1`) so the release_note sits at `lines[-2]` and the footer at `lines[-1]`.

## The command and the refusal (t5, t6)

t5 (`test_runs_the_same_command_with_the_target_path`): after `_do_release(row)` with subprocess patched to return `returncode=0, stdout="Released class hold: a.md\n..."`:
- assertion `call[0][0] == [sys.executable, str(tmp_path / "tools" / "clear_plan.py"), os.path.join(str(tmp_path), "hold-a.md"), "--release-class-hold"]` — PASSED
- assertion `call[1]["cwd"] == str(tmp_path)` — PASSED
- assertion `shell.release_note == "Released class hold: a.md"` — PASSED

t6 (`test_nonzero_exit_is_shown`): after `_do_release(row)` with `returncode=1, stderr="ERROR: cycle_check gate: CONTINUE (BAR_MET required) — file left held\n"`:
- assertion `shell.release_note.startswith("release FAILED (exit 1):")` — PASSED
- assertion `shell.release_note.endswith("ERROR: cycle_check gate: CONTINUE (BAR_MET required) — file left held")` — PASSED
- assertion `any(err_line in l or "FAILED" in l for l in lines[-3:-1])` — PASSED (release_note at `lines[-2]`)

## Mutation run

MUTATION: 4 killed, 0 survived, 0 error
