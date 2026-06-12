verdict: continue
Rule 22 substance check (b) PASS. The deposit answers the gating question completely: both defects root-caused at file:line with the WARN hypothesis eliminated by evidence, and a per-column Phase 2 trust verdict delivered.

Verification:
- Missing step-2 rows CONFIRMED as resume-path write gap: run_plan re-entered via _consume_verdicts (bellows.py:1607) with an in-progress-* filename skips the mint block (bellows.py:412 condition false), plan_id stays None (bellows.py:411), and every guarded lifecycle write silently no-ops. Cross-confirmed by plan 6's own live rows proving the initial-dispatch path works.
- turns NULL CONFIRMED as a two-part omission: parser.py never extracts num_turns (present in raw result events — num_turns: 100 verified) and both record_step_end callsites (bellows.py:557-558, 667-668) omit the turns kwarg.
- Silent-WARN candidate ELIMINATED: zero lifecycle WARNs in the 2026-06-11 daemon log — writes never attempted, not attempted-and-failed.
- Step-JSON reconciliation independent of the DB: 2 JSONs per plan vs 1 DB row per plan. Cost math cross-checked: plan 4 actual $5.94 vs rolled-up $3.62; plan 5 actual $2.45 vs $1.05 — canonical query 4 confirmed understating.
- G4 bonus finding accepted: _id_tag_instruction (bellows.py:472) is also empty on resume, so step-2 commits for plans 4 and 5 carry no [id] tag — same root cause, fixed by G1.

One deposit overstatement noted for the executable, not a blocker: Section 6 marks plans.lifecycle_state reliable as-is, but plan 6 reads 'claimed' while its file is verdict-pending — intermediate states (in_progress, awaiting_verdict) are never written; only close/halt/abandon update it. Canonical query 3 keys on closed_at so routing is unaffected, but the fix executable should either write intermediate states or document the column as coarse.

Phase 2 disposition: plans-level query design may proceed now; all steps-level query shapes remain blocked until the G1-G3 fix ships and a multi-step plan verifies two rows with turns populated.

Fix executable will follow as a separate deposit citing implements diagnostic 6.
