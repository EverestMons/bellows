continue

Step 1 (DEV) of #100099 verified against the plan (the governance draft closed at 4ecb35a2), from the step's transcript (logs/20260914-164909-step.json), tuyere main (a2a8523, da689d1) and the two deposits.

- Item 1: P1-P3 re-derived with no mechanism mismatch (no holder check, no --foreign and no exit 6 before the edit; bellows' claim and release pass no --machine); 115 collected at the base.
- Item 2: r1-r5 appended at the file's end; red `4 failed, 1 passed, 115 deselected` (r1, r2, r4 and r5 red; r3 green), as predicted.
- Item 3: `_cmd_release` reads `active["machine"]` after the exit 3 and before any write; without the flag a foreign release rolls back, prints the specified stderr line word for word and exits 6; `--foreign` (store_true, read through getattr) records `foreign: true` and `holder` only on another machine's claim and adds ` (foreign: held by <holder>)` to the printed line; on an own claim it prints `--foreign not needed: ...` and records nothing extra. The usage line gains `[--foreign]`, the flag's help names the keyboard backstop and GOVERNANCE §4 item 20, and a comment names thread 328; the docstring's exit-code list also gains 6 (not asked, consistent). py_compile OK; `5 passed, 115 deselected`; the full suite `120 passed` (115 + 5).
- r1-r5 assert what What this changes 4 names: r1 exit 6, `held by air`, rows `["claimed"]`; r2 rows `["claimed", "released"]`, machine `mini`, claim_seq 0, detail exactly the five keys; r3 detail exactly the three keys; r4 the no-op line and no `foreign` key; r5 through a subprocess with `cwd=REPO_ROOT`, the test file's own repository: exit 0, then 6 with `held by r5-air`, then 0 with holder `r5-air`.
- MUST-PRESERVE: `tests/test_tuyere.py` carries one hunk, at its end (`@@ -2077,3 +2077,93 @@`), with 0 deletions; exits 3 and 5 unchanged; nothing touched the live claims store (no `tuyere.claims` from a shell, no config read).
- Item 4: the first commit a2a8523 carries the three files, path-scoped, the message naming [100099] and thread 328.
- Item 5: seven mutants, each on the node the plan names; `MUTATION: 7 killed, 0 survived, 0 error` over `HEAD: a2a8523...`, the live tree unchanged.
- Item 6: the dev-log's four headings as full lines, P2's cell whole through `run on the holder`, the red and the two green lines, the three PASSED lines and the run's last line; the last commit da689d1, path-scoped to the run file and the dev-log; `$T` removed; `git status --porcelain` empty.
- Gates: every row PASS, scope_step, rule_22_verification, mutation_result and dev_log_declared_text among them.

Two deviations, recorded; neither changes what landed:
1. Each commit's chain was split across two commands: the suite and the pre-check in one ([38]: `120 passed`, then `PRECHECK: 0 failure(s) ... (expecting 2 missing)`; [44]: `120 passed`, then `PRECHECK: 0 failure(s)`, bare), and `git add` with `git commit` in the next ([39], [45]). They ran in order, with no edit between a check and its commit. Both chains also piped the suite through `| tail -3`, so the suite's exit status did not gate the pre-check; the printed summary line shows it green. The plan asked for ONE command. This is thread 333's class (#100098's pattern); that plan binds only the pre-check link.
2. The Post-conditions' "no PEP 604 union in any signature of tuyere/claims.py" is false to the letter on two pre-existing annotations, `_load_cfg(path: str | None)` :46 and `_active_claim(...) -> dict | None` :79, both #100001's (f5dbde57). The module's `from __future__ import annotations` (:28) keeps them from being evaluated at def time. The DEV added no signature, compiled the module and ran the suite under the 3.9.6 venv. The plan's wording is at fault, not the step's work.

Continue to Step 2 (QA).
