verdict: continue
Rule 22(b) PASS on Planner review of the DEV diff (not agent prose). Mechanical gate clean (all rows PASS; the 2 INFORMATIONAL intermediate-decisions are benign "let me also check/verify" narration). I read fetch_xml.py + config.py at HEAD and confirmed the walk-hardened cruxes, INCLUDING the specific bugs the walks caught:
- A (window-hide): `if os.name=="nt": CREATE_NO_WINDOW = 0x08000000` on the per-invoice curl subprocess.run ONLY (fetch_xml.py:98-101) — a LITERAL, not subprocess.CREATE_NO_WINDOW (w1-5), and the parent _spawn_fetch_subprocess is UNTOUCHED (still DETACHED_PROCESS only, app.py:579-581) so no CreateProcess mutual-exclusivity breakage (w1-1).
- C (bounded batch): candidate_limit = batch_limit*4 → get_pending_fetch_ids(limit=candidate_limit) → work_ids=[... if not in existing][:batch_limit] (fetch_xml.py:214-217) — the filter-then-take, not a raw SQL LIMIT (w1-3). config.FETCH_BATCH_LIMIT default 500.
- D (progress): fetch_progress.json atomic (temp+os.replace), heartbeat time-based (>=30s refresh, :286), NO pid (w2-1/w2-2).
- B (stop): stop-sentinel cleared at start (:206), checked each loop (:279), removed after (:320).
27 tests pass (22 existing + 5 new safety). Proceeding to Step 2 (UI routes + template).
