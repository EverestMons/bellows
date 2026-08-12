verdict: continue

Step 1 (helper + three call sites + tests) — clean gate, all mechanical
checks PASS.

Rule 22(b) verified by the Planner BY EXECUTION, not summary: gates.py
carries qa_mandate_suffix (def count 1); bellows.py carries exactly 3 call
sites with the diagnostic bootstrap clean (0); the suffix returns 578 chars
carrying BOTH banner literals byte-exact for a QA step and empty for a
non-QA step (my own live import + calls); bellows.py parses (ast); the
targeted trio ran 345 passed = 159 + 180 + 6 new, zero failures.

Proceed to Step 2 (QA) — which will be the last QA step ever dispatched
WITHOUT the mandate it ships (the running daemon holds old code; the suffix
goes live at the post-plan restart).
