continue

Step 2 (QA) clean and final. All gates PASS incl. rule_20_self_check (banner byte-exact) and rule_22_verification. Raw evidence: full-suite.txt "874 passed, 1 warning in 22.23s" (873 baseline + 1 net from the invariant-3 flip plus TestAutoCloseProvenance); targeted-tests.txt "38 passed, 148 deselected". decided_by now carries mechanical provenance — gate_auto for auto-close transitions, verdict_file for consumed-file transitions; no leftover "ceo"; no production consumer affected. The 312 gap is closed. Final step — close to Done/.
