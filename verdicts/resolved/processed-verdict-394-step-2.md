verdict: continue

Planner verdict on executable-394 step 2 (activity_import reroute — the core step) -> continue to step 3.

MECHANICAL GATE: all PASS, zero failures (3 files: activity_import.py, dev log, test_activity_import.py; scope_check PASS).

SUBSTANCE (Planner-verified DIRECTLY in code + by running tests):
- All stub-create machinery REMOVED: grep finds zero _build_stub_tuple / _flush_stubs / stubs_created_this_run / STUB-{ / stub_rows.
- Unmatched activities route to buffer: resolve branch (activity_import.py:432) `if key in pro_load_map: enrich (append to activity_rows) / else: buffer_rows.append(...)`; _flush_buffer (:229) INSERT OR IGNORE INTO pending_activities.
- V1 INVARIANT HELD: buffer stores NORMALIZED (pro,load) — buffer_rows.append uses the pro/load locals from _normalize_id/_normalize_load (:376-377), same as the match key, so Step 3's drain will match representation.
- D2 COLLISION GUARD CORRECT: _preload_invoice_map returns (pro_load_map, ambiguous_keys); on two non-stub invoices colliding post-normalization it adds to ambiguous_keys AND pops the key from pro_load_map (:203-204) + logs a warning, and skips further rows for that key (:191-192). So an ambiguous key is FALSE for `key in pro_load_map` -> falls to the buffer branch, never mis-enriched onto an arbitrary invoice. Stub-preference (:198-201) preserved.
- Log: activity_import_log INSERT keeps stubs_created (writes 0) and adds buffered_activities (:485-499) — matches F2/Step 1 schema.
- TESTS RUN (Planner, foreground): TestNormalization (leading-zero match both directions = Q2), TestCollisionGuard (buffers + logs = D2), TestStubUpgrade (legacy _try_upgrade_stub intact), TestBuffering (unmatched buffers, matched enriches, dedup) => 12 passed. Full targeted -k run => 13 passed.

NON-BLOCKING: 2 intermediate-decision blocks benign (implementation plan narration + test-update note). The CLAUDE.md-known TestFlaskRoute::test_get_activity_import_page pre-existing failure is unrelated.

Clean and correct. Proceed to step 3 (ingest.py _apply_pending_activities drain).
