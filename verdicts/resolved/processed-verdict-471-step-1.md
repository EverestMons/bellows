verdict: stop

Halting exec-471 per CEO direction to reconcile the two parallel full-suite temp-leak threads (470 templeak-qa-cert vs 471 raw-redirect fix).

State (Planner-verified):
- 471 Step 1 (DEV) completed and MERGED to main before the halt could land — commit a2ddd69a `test-infra: session TMPDIR redirect in conftest [471]` adds the `_redirect_raw_tmpdir` session-autouse fixture (the cycled Option-c design: `tempfile.tempdir` set directly, `mktemp("raw_tmp")`, restore + rmtree). 471 is paused at `header_pause` awaiting Step-2 (QA) verdict.
- Plan 470 (CEO's `templeak-qa-cert`) is still running its full-suite QA, now against the COMBINED HEAD (partial `_reclaim_test_tmp` + 471's redirect).

Stopping 471 so its Step-2 full-suite QA does NOT run concurrently with 470's — two simultaneous full-suite runs would duplicate work and compound disk pressure. 470 certifies the full suite. 471's redirect commit (a2ddd69a) REMAINS on main pending the CEO's keep-vs-revert decision (the redirect is empirically validated and complements `_reclaim_test_tmp`; reverting is only needed if 470's partial-fix isolation experiment must be re-run cleanly). Per Rule "no redo": stop; any re-dispatch is a fresh corrected deposit.
