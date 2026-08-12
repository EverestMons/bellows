continue

Step 1 (DEV) — clean gate, Rule 22(b) substance verified by the Planner.

Mechanical gates: all PASS (receipt Complete, scope_check within plan, 10 files
changed incl. the new fetch_xml.py, deposits present, rule_22 pass, not a QA step).

Rule 22(b) — the deposited content faithfully implements every drafting-cycle fold:
- fetch_xml.py: curl `--negotiate -u :` SSPI shell-out (F1); the response-is-XML
  guard with a `not_xml` status for HTML auth-redirects (walk-1 ACID 5.2); the full
  marker taxonomy fetched/not_found(404)/auth_fail(401)/not_xml/error; the work-list
  retries ONLY not_found/error and never auth_fail/not_xml (the stop-don't-loop
  fold) and is NULL-safe; ThreadPoolExecutor concurrency cap (C6); ascii_safe cp1252
  output (C5); a per-run failure log (not DEVNULL).
- The ATOMIC write is exactly C7/C9: tempfile.mkstemp(dir=xml_folder) (UNIQUE tmp,
  the concurrent-writer fix) + os.replace (atomic-replace, not os.rename — the
  Windows fold), same-folder (no cross-device edge).
- Schema (C4): CURRENT_SCHEMA_VERSION 20 to 21; fetch_attempted_at/fetch_status added
  via the ALTER TABLE ADD COLUMN helper — NO table-recreation of invoices (FK-safe).
- Spawn (C1): _spawn_fetch_subprocess uses an absolute BASE_DIR path + cwd + a real
  log file, never DEVNULL — the deferred-validation origin's silent-failure bug fixed.
- The atomic-publish invariant has a test (test_successful_write_is_atomic, the f16
  fold); existing schema tests correctly updated to assert == 21 (not weakened) — the
  anticipated schema-bump ripple.

Intermediate decisions (2) are benign — the agent verifying "21 fetch tests pass"
and running the schema migration tests. No scope creep, no guard relaxed.

Continue to Step 2 (QA).
