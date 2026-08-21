verdict: continue

Planner verification (Rule 22(b)) — plan 497 (wrap-hook layer plan B), Step 2 (QA, TERMINAL). ALL SEVEN recorded gates PASS; no failure to adjudicate. Verified independently of the agent Receipt:

1. FULL SUITE, NO REGRESSION. Plan A's pre-change baseline: `1183 passed`. Now: **`1231 passed`, 1 warning, 0 failed, 0 errors**. The +48 delta is exactly the two new modules (20 from plan A, 28 from plan B) — a regression check, not an equality check, and it passes as one.

2. ALL SIX CANARY ASSERTIONS PASS, REPORTED SEPARATELY AND IN THE CORRECT VEHICLE — the split the cold panel's ACID pass forced, because `wrap_check` inspects the four real git repos and is necessarily FAILING while the QA step holds uncommitted evidence, making the unlink branch unreachable in a live canary:
   - Canary (real hook subprocesses, `wrap_check` genuinely failing): **(i)** per-session sentinel created, no bare file. **(ii)** B BLOCKED under ARM-IF-ANY with A's sentinel PRESERVED — non-removal of a foreign sentinel. **(iii)** B blocked on its own sentinel, message names A's foreign sentinel WITH ITS AGE and instructs waiting.
   - Unit tests (`wrap_check` monkeypatched to pass): **(iv)** B removes ONLY its own on a passing check — the disarm defect. **(v)** A can still clear its own — a lock that arms can still be released. **(vi)** a bare legacy sentinel arms, clears on pass, and is NEVER renamed.
   I re-ran the named tests myself: `TestDisarmDefect` + `TestBareSentinel` → **7 passed**.

3. THE LIVE LOCK IS CORRECT AFTER ALL EDITS ACROSS BOTH PLANS. Driving the wired `wrap_stop_hook.py` with a foreign sentinel present and no marker: `decision: block`, foreign sentinel PRESERVED. Exercised, not read.

4. Rule 20 banner pair present verbatim; no `.wrap-in-progress*` left at the real governance root.

THE ARC IS CLOSED, AND BOTH OF TODAY'S CAPTURES ARE FIXED WITH LIVE EVIDENCE:
- The DAEMON capture (exec-493's worker pushed three repos, then deleted the CEO's sentinel): daemon sessions now take the exempt branch — `hooks.log` shows `daemon-exempt` for daemon workers while interactive sessions still log `unarmed-allow`.
- The INTERACTIVE capture (the Planner session handed another terminal's checklist, held ~5 minutes with no way to distinguish working from abandoned): a session can no longer clear another's sentinel, and the block message now names the foreign wrap, reports its AGE, instructs waiting, and warns against resolving work you did not do.

Residuals, stated rather than buried: P2 (no indefinite wedge) is partial — the staleness reaper runs only on a passing `wrap_check`, whose ordinary state is failing; `session_id` stability across auto-compaction remains unmeasured, correctly neutralised by ARM-IF-ANY failing toward staying armed; and the plan-row/verdict-scanner disagreement seen on 496 is untouched by this work.

Terminal step: close to Done.
