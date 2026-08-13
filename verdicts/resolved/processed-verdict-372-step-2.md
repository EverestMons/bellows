verdict: continue
Rule 22(b) PASS on Planner review of the Step-2 UI diff (app.py + ingest.html + tests). Mechanical gate clean (the 1 INFORMATIONAL intermediate-decision is the agent correctly updating a validation test after the sanctioned pending-precheck drop). Verified every walk-hardened UI crux at HEAD:
- /ingest/fetch/status REWRITTEN to `_read_fetch_progress()` (reads fetch_progress.json, NO COUNT over invoices) — the count-free perf fix + progress source.
- /ingest/fetch/run: not_configured 400 kept; concurrent-run guard `if progress.running and not progress._stale -> already_running 409` (w1-2 heartbeat-freshness, cross-platform); clears the stop-sentinel; spawns.
- NEW /ingest/fetch/stop writes the sentinel (app.py:608).
- /ingest/validation/status REMOVED (absent) + a `test_get_validation_status_returns_404` observe-the-effect test; the C1 validation/run already_running 409 guard RETAINED (app.py:506) + its 409 test kept.
- _read_fetch_progress applies the staleness rule (heartbeat age -> _stale) so a crashed job never reads as running (w1-4/w2-1); absent file -> {running:false} (w1-6).
- Template: Reset wraps confirm() (w1-3); CSRF meta+X-CSRFToken on all POSTs incl. /fetch/stop, and button-disable-during-POST preserved (MUST-PRESERVE).
Proceeding to Step 3 (QA full suite).
