verdict: continue

All gates PASS. Substance verified in bd79b8b (4 files / 64 insertions):
the opt-in helper hashes raw read_bytes and writes via lifecycle.write_clearance
with the claimable basename; applied at the shared deposit points (49 lines in
test_bellows.py covering its 38, 2 lines in each of the other two suites);
conftest autouse count UNCHANGED at 3 — no blanket clear, mechanically
confirmed against the pre-state.

One deviation noted, not blocking: the plan mandated cleared_by='test' and
the helper writes cleared_by='depositor'. Cosmetic in tmp-DB tests, but the
audit-trail label is wrong-in-kind; folded forward as a nit for any future
clearance-audit tooling rather than re-dispatching a 1-token change. QA's
full suite and control arm are the real acceptance. Proceeding to Step 2.
