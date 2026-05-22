verdict: continue

Rule 22 override on gate_failure verdict request — substance verified, investigation complete.

Bellows-mechanized gate failure: `no_permission_denials` reported 1 blocking denial for `mcp__vexp__get_context_capsule`. The denied tool was a supplementary context-fetch the agent attempted before falling back to direct file reads. The investigation completed in full using the allowed tools.

Planner substance check (Rule 22 (b)) on the deposited findings at `invoice-pulse/knowledge/research/fuel-continuation-inference-findings-2026-05-21.md`:

Q1 (data threshold): ANSWERED. Six gates mapped with file:line, check logic, message, and clear-conditions. 34 rows clears all volume gates (G1=6, G2=4, G5=3, G6 cycle counts all satisfied with 33 deltas). Rejection must be one of: G3 (gap between adjacent bracket rows), G4 (non-uniform price increments), or G6 (no repeating FSC delta pattern). UI misleadingly displays "Insufficient data for 99% confidence" headline for all three refusal types; the actual reason is in the `detail` field as secondary italic text.

Q2 (timing rule extraction): ANSWERED. Timing is a discrete extracted field from copilot prompts (`timing_rule`, `effective_day`) — present in 5 prompt variants in `copilot_prompts.py`. The fuel continuation inference engine does NOT see contract prose at all; it operates purely on bracket row dicts (`price_floor`, `price_ceiling`, `fsc_pct`). The two systems are connected only via `_corroborate_inference` after the fact.

Parallel implementation check: confirmed only one bracket-inference implementation exists. Related but distinct systems (copilot prose extraction, invoice pattern discovery) identified and scoped.

Receipt section present with 12 files read and 1 file deposited. Findings are surgical and actionable.

Closing the plan. Next step is CEO decision on whether to author an executable to either (a) re-run inference and read the `detail` field to identify which of G3/G4/G6 fired, or (b) fix the misleading UI headline first since it obscures the actual rejection reason.
