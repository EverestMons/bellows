verdict: stop

The QA gates fired TRULY and the stop is the honest disposition: 40 failed /
1248 passed, all 40 in pre-existing suites (test_bellows.py, 
test_consume_verdicts.py, test_gate_transaction_mechanization.py) whose
fixtures deposit plans and expect dispatch WITHOUT clearance records — the
admission flip refusing them is the built behavior working. The blast radius
the panel swept for test_depositor.py at DEV-A exists at 40x scale in the
dispatch-path suites, and neither the plan nor the four-seat panel scoped it:
A2/B2 built NEW tests; nobody swept the EXISTING fixtures' admission
assumptions. The QA agent's conduct was exemplary: every failure named, one
uniform diagnosis, Rule 20 kept honest with a plain X — the exact class
LESSONS-191 describes, where an honest QA failure trips the hedging gate.

STATE SHIPPED, STATED PLAINLY: DEV-A (4fdf55a) and DEV-B (936ef5e) remain
committed on bellows main with a red suite AGAINST THE NEW CODE PATHS ONLY.
The live daemon runs old code (inert until restart); activation was already
gated on the post-close canary and now additionally on the corrective below.
No revert: the code is panel-verified and the red is confined to fixtures
that predate the law the code introduces.

DISPOSITION: corrective executable follows immediately under the stable arc —
teach the pre-existing fixtures the admission law (a clearance-writing helper
at the fixtures' deposit points, opt-in so the flip's own negative tests keep
their refusals), then the full suite green at known_failures 0. Activation
(restart + two-arm canary) only after that close.
