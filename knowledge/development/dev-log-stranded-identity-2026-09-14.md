# Stranded-Identity Dev Log — 2026-09-14

## Pins re-derived (P1, P2, P4, P8)

P2 (verbatim from the plan's value cell):

`_create_worktree` :2266 — the in-place return for a project with no `.git` of its own :2276–2279; `if os.path.exists(wt_path):` :2286 — `exists` follows a symlink, so a dangling one reads as absent — and the call `_preserve_and_remove_stranded_worktree(project_path, wt_path, slug, strict=False)` :2287, its return discarded, no `try` around it; the fail-fast on an existing `bellows-wt/<slug>` :2291–2300 (`WorktreeCreationError`, "sequential invariant violated"); `git worktree add <wt> -b <branch> HEAD` :2303 with one retry :2306–2311; `run_plan`'s `except WorktreeCreationError` :1763–1783, around the call at :1762, which runs on every dispatch before `current_step` is read at :1788 — the lane renamed `verdict-pending-`, a verdict request with `gate_failure` and `precondition_failure=True` posted and recorded at step 1 whatever step was dispatched (:1773, :1776), the plan `awaiting_verdict`, "worktree creation failed, awaiting CEO verdict"; the startup close's identity guard :1315–1347 — a symlink refused :1315–1320, `git -C <wt> rev-parse --show-toplevel` against the path's realpath, a string comparison, :1334–1347 — and its strict call

Re-derived lines (worktree `100115`, base `e9e435f3`):

- **P1** — `def _preserve_and_remove_stranded_worktree` at :1114 (plan :1108, drift +6). No mechanism mismatch.
- **P2** — `_create_worktree` at :2275 (plan :2266, drift +9); `if os.path.exists(wt_path):` at :2295 (plan :2286, drift +9); `_preserve_and_remove_stranded_worktree(…)` call at :2296 (plan :2287); `except WorktreeCreationError` at :1770 (plan :1763, drift +7); `post_verdict_request` at :1780 (plan :1773, drift +7); `record_verdict_request` at :1783 (plan :1776, drift +7); `current_step` at :1795 (plan :1788, drift +7). Entry test still `os.path.exists`, step hardcoded to 1, no `samefile`, no foreign-repo check. No mechanism mismatch.
- **P4** — `tests/test_worktree.py`: 26 tests, 1074 lines — matches plan. `tests/test_abandoned_runner_close.py`: 26 tests (plan said 25; `test_refusal_page_pages_when_attended` added by [100112] commit `4de7835b`, thread 321, after the Planner's measurements — count drift, not a mechanism mismatch). No mechanism mismatch.
- **P8** — `_consume_verdicts` at :3824 (plan :3763, drift +61); final-step branch `if step_number >= total_steps_c:` at :3988 (plan :3927, drift +61); post-loop unlink at :4059 (plan :3996, drift +63). Final-step branch still unconditional, retry arm still unlinks after dispatch. No mechanism mismatch.

## Failing-first (red, then green)

Red (base, unedited): `35 failed, 28 passed in 12.25s`

Green (worktree `100115`, all items): `2520 passed, 2 skipped in 248.26s`

Green (test_worktree.py only, item 2 scope): `63 passed in <subset>`

Green (test_abandoned_runner_close.py, item 2 scope): included in the 2520 total above

Green (worktree `100117`, patch applied — test_worktree.py): `63 passed in 14.51s`
Green (worktree `100117`, patch applied — four neighbour files): `323 passed in 115.75s`
Green (worktree `100117`, patch applied — full suite): `2520 passed, 2 skipped in 266.27s`

## Shadow cache (before, after)

Listing taken before Item 2's first run (`ls -la /Users/marklehn/Developer/bellows/.bellows-cache`):

```
total 336
drwxr-xr-x@  8 marklehn  staff    256 Sep 15 20:20 .
drwxr-xr-x@ 52 marklehn  staff   1664 Sep 15 20:20 ..
-rw-r--r--@  1 marklehn  staff     20 Sep 11 16:31 executable-1.md.pristine
-rw-r--r--@  1 marklehn  staff     65 Sep  8 16:13 executable-100044.md.pristine
-rw-r--r--   1 marklehn  staff  25555 Sep 11 15:07 executable-100081.md.pristine
-rw-r--r--   1 marklehn  staff  25555 Sep 11 16:01 executable-100082.md.pristine
-rw-r--r--   1 marklehn  staff  98508 Sep 15 20:20 executable-100115.md.pristine
-rw-r--r--@  1 marklehn  staff     45 Sep 11 16:30 executable-regression-slug-collision-2026-05-01.md.pristine
```

SHA-256 digests (before):

```
983fb5930b8062efc9b1a436c1937018677dffcaa34359a8c5fd60fb71af3364  /Users/marklehn/Developer/bellows/.bellows-cache/executable-1.md.pristine
773dfd7150577991eb2ab5952debf64cbf03eff38504966ca5b16e5a30f85855  /Users/marklehn/Developer/bellows/.bellows-cache/executable-100044.md.pristine
b5f11219d824c6d0eb8ff22001ce786b26b77bc36cc30ebce697280ff624932f  /Users/marklehn/Developer/bellows/.bellows-cache/executable-100081.md.pristine
b5f11219d824c6d0eb8ff22001ce786b26b77bc36cc30ebce697280ff624932f  /Users/marklehn/Developer/bellows/.bellows-cache/executable-100082.md.pristine
bcb472c18a09be064c3a930150fb7cf1dc7c4d32d50aa3a1eed44a92013314f9  /Users/marklehn/Developer/bellows/.bellows-cache/executable-100115.md.pristine
79dab0b0bfeab45cf16755b3f60152d54a0c9dfa8593fa9791a92d9fc1f8f2cd  /Users/marklehn/Developer/bellows/.bellows-cache/executable-regression-slug-collision-2026-05-01.md.pristine
```

Listing taken after Item 5's run (`ls -la /Users/marklehn/Developer/bellows/.bellows-cache`):

```
total 344
drwxr-xr-x@  8 marklehn  staff     256 Sep 16 09:42 .
drwxr-xr-x@ 52 marklehn  staff    1664 Sep 16 09:42 ..
-rw-r--r--@  1 marklehn  staff      20 Sep 11 16:31 executable-1.md.pristine
-rw-r--r--@  1 marklehn  staff      65 Sep  8 16:13 executable-100044.md.pristine
-rw-r--r--   1 marklehn  staff   25555 Sep 11 15:07 executable-100081.md.pristine
-rw-r--r--   1 marklehn  staff   25555 Sep 11 16:01 executable-100082.md.pristine
-rw-r--r--   1 marklehn  staff  103322 Sep 16 09:42 executable-100118.md.pristine
-rw-r--r--@  1 marklehn  staff      45 Sep 11 16:30 executable-regression-slug-collision-2026-05-01.md.pristine
```

SHA-256 digests (after):

```
983fb5930b8062efc9b1a436c1937018677dffcaa34359a8c5fd60fb71af3364  /Users/marklehn/Developer/bellows/.bellows-cache/executable-1.md.pristine
773dfd7150577991eb2ab5952debf64cbf03eff38504966ca5b16e5a30f85855  /Users/marklehn/Developer/bellows/.bellows-cache/executable-100044.md.pristine
b5f11219d824c6d0eb8ff22001ce786b26b77bc36cc30ebce697280ff624932f  /Users/marklehn/Developer/bellows/.bellows-cache/executable-100081.md.pristine
b5f11219d824c6d0eb8ff22001ce786b26b77bc36cc30ebce697280ff624932f  /Users/marklehn/Developer/bellows/.bellows-cache/executable-100082.md.pristine
7b85d6c9af2e80233de1a563be97a8f12322b28f9c849024d4f62a9a27c6a43a  /Users/marklehn/Developer/bellows/.bellows-cache/executable-100118.md.pristine
79dab0b0bfeab45cf16755b3f60152d54a0c9dfa8593fa9791a92d9fc1f8f2cd  /Users/marklehn/Developer/bellows/.bellows-cache/executable-regression-slug-collision-2026-05-01.md.pristine
```

## Recovered work verified

Patch sha256 prefix: `8d049be6e8e60a91` (714 lines, 35,571 bytes). Applied clean on `b8c1d694`. `git diff --numstat` → `339	78	bellows.py` and `54	23	tests/test_worktree.py` exactly. All test_worktree.py hunks at or after old line 1809, none at or above 1074. `git diff -- verdict.py` empty. `git status --porcelain -- knowledge/mutants/` empty.

**MUST-PRESERVE verification (bellows.py lines after patch):**

- ⛔ Strict mode unchanged — `if strict:` branches in helper at :1292–1306 (HEAD read directly), :1359–1360, :1367–1369 (HEAD branch raises PreserveFailed), :1408–1410, :1413–1416 (tip check raises PreserveFailed); removal block at :1419 guards with `if not is_symlink_path:` regardless of mode; strict caller guard at :1561 unchanged; test_abandoned_runner_close.py untouched (`git diff -- tests/test_abandoned_runner_close.py` empty).
- ⛔ No HEAD read through a path not proven its own — identity proof at :1248–1268 (`os.path.samefile(toplevel, wt_path)` by inode, any `OSError` or non-zero reads as not own); `elif is_own:` gate at :1307 means HEAD only read through `git -C wt_path` when proven own; not-own non-symlink reads registered HEAD from project (`_registered_detached_head_for`) at :1322–1327; symlink leaves `wt_head=None` (:1328).
- ⛔ Repository of its own stops before any read — `_foreign_dot_git` at :1115–1158 checks `.git` is-symlink (:1125–1126), is-dir (:1127–1128), or is-file whose gitdir is not this project's (:1130–1158); called at :1229–1244 before identity proof, HEAD read, tip check, and removal; raises `WorktreeCreationError` immediately; symlink path skipped (foreign check runs only `if not is_symlink_path:` (:1229)).
- ⛔ Failed save removes nothing, raises from inside helper — `_save_stop` at :1278–1290 raises `WorktreeCreationError`; removal block at :1419 only reached when no `_save_stop` raised; re-raise guards at :1362–1363 and :1411–1412 keep a WorktreeCreationError raised inside a try from being caught and re-wrapped; `_create_worktree`'s entry-test call at :2541–2542 has no `try` around it, so the raise exits before `worktree add`.
- ⛔ Symlink never handed to `git worktree remove` — removal block guarded by `if not is_symlink_path:` (:1419); symlink takes the removal-stop path if `os.path.lexists(wt_path)` (:1447–1477) with symlink reason and `unlink` act; `_create_worktree` entry test is `os.path.lexists` (:2541) so dangling symlinks reach the helper.
- ⛔ Path not cleared stops after commits kept — removal stop at :1447–1477: commits kept in `kept_branches` before removal; `os.path.lexists(wt_path)` checked after removal; raises `WorktreeCreationError` with the kept branches named.
- ⛔ Stop pauses at step dispatched, continue retries it — `_wce_step = resume_step if resume_step is not None else 1` at :2025; `post_verdict_request(..., _wce_step, ...)` at :2026; `record_verdict_request(plan_id, _wce_step, ...)` at :2029; final-step branch `if step_number >= total_steps_c and not precondition_failure_from_request:` at :4249; consumer early unlink at :4294–4296 before `handle_new_plan` at :4297; post-loop unlink dropped.
- ⛔ Tip kept whenever off main and differs from HEAD kept, in both modes — tip block at :1371–1416 not gated on `strict`; checks `wt_head is None or tip_sha != wt_head` (:1382) and `not tip_already_landed` (:1392).
- ⛔ Every existing test passes unedited — `63 passed` in test_worktree.py (all hunks below :1809); `323 passed` four neighbour files; `2520 passed, 2 skipped` full suite.
- ⛔ Test code under pytest inside tests/ — no test helper called from python -c or scratch script.
- ⛔ Every daemon-entry-point test on its own root — x18, x22, x23, x24: `monkeypatch.setattr(bellows, "BELLOWS_ROOT", bellows_root)` and `monkeypatch.setattr(bellows, "SHADOW_CACHE_DIR", shadow_cache)` with `shadow_cache = bellows_root / ".bellows-cache"` under `tmp_path`.

**Seven test fixes:**

- x15: fixture now patches `shutil.rmtree` via `_block_rmtree` (blocks rmtree on wt_path) and `subprocess.run` blocks `git worktree remove --force` on wt_path — spec: *a directory the removal could only partly clear (a read-only subdirectory)*
- x18: branch assertion changed to `bellows-wt/<slug>` still present after failed save (spec: *a failed save removes nothing*); request glob uses `verdict-request-{plan_id}-step-2.md` (spec: *verdict-request-<id>-step-2.md*, the plan's own name)
- x20: `bellows-wt/<slug>` created in a separate worktree `other_wt` so `wt_path` is free for symlink placement — spec: *a symlink to a worktree elsewhere that has `bellows-wt/<slug>` checked out*
- x22: request glob uses `f"verdict-request-{plan_id}-step-{resume_step}.md"` (without "executable-" prefix) — spec: *verdict-request-<id>-step-N.md*
- x23: request glob uses `f"verdict-request-{plan_id}-step-1.md"` (without "executable-" prefix) — spec: *verdict-request-<id>-step-N.md*
- x24: `_counted_run_plan` kwarg is `bellows=None` matching `run_plan`'s signature; `threading.Event` `plan_ran` awaited after `_consume_verdicts` so re-dispatch completes before assertion — spec: *the consumer unlinks before it dispatches*; request glob uses `f"verdict-request-{plan_id}-step-2.md"`
- x26: `tempfile.mktemp(suffix="-ext-gitdir")` returns a non-existent path (as `git clone --separate-git-dir` requires) — spec: *a `git clone --separate-git-dir` of the project at the path (its `.git` a FILE pointing outside…)*

## The cleanup observed (x1, x7, x13, x16, x18, x22, x24, x25)

Nine PASSED lines from `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest -v` over the node ids (x22 has two cases):

```
tests/test_worktree.py::test_stranded_plain_directory_preserves_branch_tip PASSED [ 11%]
tests/test_worktree.py::test_stranded_plain_directory_registered_detached_head_preserved PASSED [ 22%]
tests/test_worktree.py::test_stranded_failed_save_raises_before_worktree_add PASSED [ 33%]
tests/test_worktree.py::test_stranded_symlink_to_live_worktree_leaves_the_target_intact PASSED [ 44%]
tests/test_worktree.py::test_stranded_stop_on_resumed_dispatch_pauses_at_the_dispatched_step PASSED [ 55%]
tests/test_worktree.py::test_stranded_stop_at_final_step_continue_retries_the_step[two-step-final] PASSED [ 66%]
tests/test_worktree.py::test_stranded_stop_at_final_step_continue_retries_the_step[one-step] PASSED [ 77%]
tests/test_worktree.py::test_stranded_stop_retry_reposts_the_request_the_consumer_keeps PASSED [ 88%]
tests/test_worktree.py::test_stranded_clone_of_the_project_left_intact PASSED [100%]
============================== 9 passed in 2.20s ===============================
```

## Mutation run

`MUTATION: 49 killed, 0 survived, 0 error`

## Recovered manifest verified

**(a) Manifest — 49 entries, target `bellows.py`:**
Each `anchor` matches committed `bellows.py` exactly once — loop over all 49 anchors with `grep -c -F` prints `1` for every entry. Distinct `expect_fail` node ids: 33. All `expect_fail` values are node ids of this plan's tests (`tests/test_worktree.py`) or `tests/test_abandoned_runner_close.py::test_tip_branch_creation_fails_refused` (c-t25).

**(b) Test changes:**

Two new test functions added by the recovery (not in the base `d1ac5cdb`):
- `test_stranded_symlink_save_fail_names_the_symlink` — kills m39 (the failed-save stop's symlink act dropped). Added between x14 and x15.
- `test_stranded_dot_git_file_no_gitdir_line_is_foreign` — kills m48 (any `.git` file accepted, the gitdir check removed). Added between x26 and x27.

Strengthened test (newly kills a mutant):
- x24 (`test_stranded_stop_retry_reposts_the_request_the_consumer_keeps`) — verdict fixture renamed from `verdict-executable-{id}-step-2.md` (legacy) to `verdict-{id}-step-2.md` (id-native), killing m45 (request unlinked after dispatch). Under the legacy name the consumer regex `^verdict-(.+)-step-(\d+)\.md$` gave `plan_slug = "executable-24"` and the pre-dispatch unlink targeted non-existent `verdict-request-executable-24-step-2.md`, making the second stop's request invisible to the unlink; m45 survived. With the renamed fixture, `plan_slug = "24"` and the unlink targets `verdict-request-24-step-2.md` — the actual pending request — so the second stop's request survives the consumer's pass and the second `continue` is taken.

**x24's verdict fixture:**
- Fixture value: `verdict-{plan_id}-step-2.md` (the name `tools/issue_verdict.py:104` writes: `f"verdict-{matched_slug}-step-{step}.md"`; on this checkout: `verdicts/resolved/processed-verdict-100117-step-2.md`).
- Consumer regex `^verdict-(.+)-step-(\d+)\.md$` on `verdict-24-step-2.md` → `plan_slug = "24"`.
- Pre-dispatch unlink targets `verdict-request-24-step-2.md` = the pending request file — the second stop's request survives.
- Under legacy form `verdict-executable-24-step-2.md`: `plan_slug = "executable-24"`, unlink targets non-existent `verdict-request-executable-24-step-2.md` — unlink is a no-op, second stop overwrites the request, second `continue` is refused. m45 survived this way.

**(c) Production files:** `git diff -- bellows.py verdict.py` empty — no production file changes in this step.
