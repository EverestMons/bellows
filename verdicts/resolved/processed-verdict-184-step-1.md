verdict: continue
Diagnostic 184 (bellows rate-limit exit-1 no-park — fix scoping) — findings complete, move to Done. Clean gate (Gate Passed True, only the findings file changed).

Planner Rule 22(b) — verified by reading the findings: all 6 targets answered concretely against the actual runner.py/bellows.py code + the two 2026-07-14 incident logs.
- Target 1 (the load-bearing unknown) DECISIVELY answered: the NDJSON stream IS available in-process as result_stdout within the exit-1 block (runner.py:246-278); the fix scans it directly, NO plumbing change. Confirmed the success-path parse + _check_session_limit are gated behind proc.returncode==0, so the exit-1 path never sees the rate_limit_event today.
- Target 2 surfaced a critical correctness nuance: a rate_limit_event (even overageStatus:rejected) ALSO appears on SUCCESS-path runs, so the event alone is NOT diagnostic — it must be COMBINED with exit-1 (validates guard b). Also found an existing stderr-only transient-retry at runner.py:249-256 that misses the stdout event. Residual risk (cap death before any NDJSON) → safe fall-through to gate_failure, acceptable.
- Targets 3-6: confirmed resetsAt is an epoch int on the event (+ a _reset_epoch_from_rate_limit_event helper with 5h fallback); dual guards (a: no committable progress, mirroring the turns/cost/tokens guard; b: five_hour cap-status event present); record_park row-shape + _resume_parked correctness verified; a concrete synthetic-stream test matrix (park / no-event-no-park / progress-no-park / graceful-429-no-regression).

This nails the fix scope with the one real unknown resolved. CEO delegated verdict authority (2026-07-02). Move to Done; Planner authors the Small executable from these findings next.
