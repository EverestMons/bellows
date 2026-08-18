continue

Canary 441 step 2 (QA) verdict: CONTINUE-WITH-REASONING over a VERIFIED-BENIGN gate_failure.
- The qa_test_result gate failed with "no parseable pytest summary — cannot certify clean; pausing". This is a FALSE failure: Planner INDEPENDENTLY read the raw evidence knowledge/qa/evidence/on-failure-canary-2026-08-18/full-suite.txt — "1101 passed, 1 warning in 31.08s", 0 failed, 0 errors. The suite is genuinely clean.
- ROOT CAUSE (canary's real finding): _PYTEST_SUMMARY_RE = r'=+\s+.+\s+=+' REQUIRES ===== borders, but piped pytest output (-q | cat) writes a BORDERLESS counts line; the only bordered line is "=== warnings summary ===" (no counts), so the gate matched the wrong line -> no 'passed' -> fail-closed. FAIL-CLOSED WORKED (safe pause, not auto-ship).
- rule_20_self_check PASS, rule_22 PASS. STEP 1 auto-continued correctly (no step-1 verdict — the non-final on_failure auto-continue works).
Continuing to ship the regression-guard test (genuinely clean). A CORRECTIVE plan fixes _PYTEST_SUMMARY_RE to content-based detection; a fresh canary then demonstrates true clean auto-continue.
