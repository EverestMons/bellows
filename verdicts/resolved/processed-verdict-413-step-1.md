verdict: continue
Clean gate -- plan 413 Step 1 (DEV, remove auto-validation-on-view) auto-continued under delegated verdict authority.

Grounds:
- Mechanical gate: Gate Result Passed=True, failures=[]; 4 files in scope (app.py + dev log + tests/test_invoice_detail_caching.py + tests/test_validation_results.py). Real run (160s).
- Planner-confirmed via git (HEAD): commit 0bc60bc4 [413] merged. The auto-validation block is REMOVED (_needs_validation = 0 hits in app.py). New tests/test_invoice_detail_caching.py patches validate_batch.run_batch and asserts assert_not_called() on GET for FRESH (stale=0), STALE (stale=1), AND UNVALIDATED invoices, plus test_validate_button_does_call_run_batch asserting POST /validate/<id> DOES call run_batch -- exactly the w2-1 mock-based lock, covering all three view cases robustly.
- Tests (step-transcript raw pytest summary): targeted run 103 passed, 0 failed.
- (b): implements Step 1 as specified -- validation runs ONLY via the button now; no hidden validating consumer (Walk-1 w1-3: AJAX cards don't call run_batch); is_stale independent (orange cue survives); no money path.

Proceeding to Step 2 (full-suite QA + Rule 20; terminal). Run the suite FOREGROUND, no Monitor -- expect only the 2 CLAUDE.md-known pre-existing failures.
