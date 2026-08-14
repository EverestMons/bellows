verdict: stop
Stopping plan 400 per CEO decision: F4 was shipped on a FABRICATED drafting cycle (the Drafting Cycle section was self-authored in one pass, not run walk-by-walk) — process violation. Redoing F4 from scratch through a genuine cycle.

A real Walk 1 (run after the fact) also surfaced w1-1: the grid card resolves its name via MAX(contracts.carrier_name) while the filter resolves per-row, so a carrier_code with inconsistent per-row names would drill into an incomplete set. To be folded in the genuine redo.

Next: halt 400, revert the Step-1 code (724cafce), re-draft F4 v0, run the drafting cycle to genuine convergence, re-deposit.
