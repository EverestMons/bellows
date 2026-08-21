continue

Capstone design diagnostic VERIFIED against the produced findings file (knowledge/research/component4-capstone-design-2026-08-20.md, 29.6KB):
- All Q0–Q7 answered; 7-row Rule 27 gap table (build-ready): §2 auto-advance cadence clause + 3 named memory rewrites (one-pass-per-turn, no-fabricated-drafting-cycle, walk-phases-separated-by-turn) + version 2.12→2.13 + "no re-mandate" on the already-doctrine substrate (§2.7/§3) + "no gate change" (cycle_check already emits the verdicts).
- Safety invariant intact + load-bearing: auto-advance is licensed ONLY when the committed substrate makes cycle_check asserts #1/#2/#3 all PASS (never N/A); an N/A assert = substrate absent → do NOT auto-advance (fall back to manual). The fabrication paths (walk-not-run, fold-not-applied, close-unearned) are each mapped to a cycle_check guard (asserts #1/#2/#3, claimed-close-unmet).
- The loop is Planner-GATED, not cycle_check-blind: manual entry through the §2.0 direction verdict (W5), the Planner's oscillation/runaway backstop (V3), and the MANDATORY closing-record re-read before any close (V4) are preserved. Crash-recovery corollary: the substrate makes the loop resumable.
- Gate clean (receipt Complete, deposit_exists, rule_22 PASS). Read-only class → auto-deposit was correct.
Single-step diagnostic; continue closes it. The §2 capstone amendment (governance in-place, T-6, earns a cold panel) builds from this gap table — the arc's final step.
