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
