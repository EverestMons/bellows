verdict: continue
Rule 22 (b) substance — PASS. The diagnostic answers all six section questions cleanly and surfaces material findings beyond the original scope.

Sections A–F all hit. Output Receipt complete with comprehensive Files Read list spanning extraction surface, write paths, engine, validator, and prior-art prerequisites.

Material reframing in Section A: IP has no direct LLM integration. The user takes the prompt to an external LLM (ChatGPT/Claude) with their screenshot, then pastes the resulting CSV back into IP. The "screenshot extraction" surface is fully out-of-process from IP. This means "harden bracket extraction" splits into two distinct surfaces — prompt instructions (what the external LLM sees) and write-path/engine/validator robustness (what IP does with whatever the LLM emits). These are independently fixable.

Key findings substantive to the sample→full goal:

G1 (extraction-prompt): zero language about partial/sampled tables. Rule 13 handles output truncation but not input truncation. CERTAIN failure on the CEO's workflow.

G6 (write-path): no is_partial / sample-vs-full marker in contract_fuel or contract_fuel_table. Partial extractions stored as-authoritative.

G8 (engine): non-uniform price increment gate refuses the example table's mixed widths. Even with perfect extraction of all 25 rows, the engine cannot infer a continuation pattern because bracket widths shift from 0.049 → 0.050 → 0.010. The G4 check at fuel_pattern_inference.py:131–155 fires before cycle detection.

G9 (engine): single-cycle-or-nothing. The example's plateau + linear + tail = no single cycle. Engine returns no_pattern or non_uniform_increment.

G10 (engine): preamble skip is more broken than the 05-28 fix appeared to leave it. The skip requires price_floor == 0.0 AND fsc_pct == 0.0. The example's second zero-rate row (1.150–1.199 at 0%) has price_floor=1.150 and would NOT be skipped, despite being structurally part of the preamble. Enters the analysis set with fsc_pct=0.0 and corrupts the delta computation.

G11 (extrapolation): materialization is upward-only from start_price. Sample→full requires extrapolation in both directions (below sample minimum AND above sample maximum) which doesn't exist.

The four-gap blocker chain (G1, G6, G8/G9, G11) is the load-bearing finding. Each is independently fixable; G8/G9 (engine multi-region support) is the largest surface and probably warrants a roadmap rather than a single executable.

One explicit CEO policy decision surfaced in Section F: should the engine attempt extrapolation on tables with detected plateau regions (where rates repeat and slope is irregular), or refuse and require fully-published brackets for those regions. Defer to next planning session.

Plan closes to Done. Follow-on artifact is a roadmap that sequences prompt-side, write-side, engine-side, and validator-side work — not a single executable.
