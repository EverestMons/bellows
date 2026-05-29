verdict: continue
Rule 22 (b) substance — PASS. Blueprint is implementation-ready.

Walked all 8 sections. Each is actionable without further design decisions:
- Section 1: verbatim function implementation + edge case table + dispatch dict additions by file:line
- Section 2: verbatim replacement strings for all 4 prompts, consolidated 4-row edit summary table
- Section 3: verbatim insertion code matching neighboring GateResult shape, explicit prior_monday weekday math
- Section 4: verbatim HTML with Jinja selected-state logic and legacy-value mapping
- Section 5: clean string-sentinel-vs-NULL tradeoff with picked recommendation (sentinel)
- Section 6: 27 named tests across 3 files (10 prompt + 12 parser + 5 validator), 1973 predicted total
- Section 7: full gap table mapping G1/G2/G3/G5/G6/G7/G8/G10/G11/G12 with dispatch order
- Section 8: explicit out-of-scope with reasoning

Test baseline (1946) reconciles with 2026-05-28 LESSONS entry (1944 passed + 2 pre-existing = 1946 total).

One CEO-flagged decision in §3e: legacy stored prior_monday values left untouched, now correctly routed through the new prior_monday EIA logic. SA framed as "pure improvement." Honest assessment: if a hallucinated prior_monday value originated from LLM guessing where contract actually said something else, the validator now applies the wrong EIA price silently instead of failing loudly. The trade is acceptable because (a) the alternative requires production data access (out of scope §8d) and (b) the production backfill is already correctly identified as a separate executable. Carrying forward: when the backfill executable is authored, it must include a sweep that flags any contract with stored prior_monday for human re-verification, since these are the highest-hallucination-risk values.

Decisions noted within specialist authority (no migration, dropdown grep-verify rather than template tests, dead D1 route deferred to hygiene executable): all reasonable. No re-litigation needed.

Proceed to Step 2 (DEV implementation in the specified dispatch order: Prompts → Write-path → Validator → Dropdown).
