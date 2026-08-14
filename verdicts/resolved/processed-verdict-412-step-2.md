verdict: continue

Planner verdict on executable-412 step 2 (foreground QA) -> continue (TERMINAL — closes 412 to Done). Plan B (the forward needs-activity prompt) ships.

MECHANICAL GATE: all PASS — deposit_exists PASS, rule_20_self_check PASS (byte-exact), scope_check PASS.

SUBSTANCE (Planner-verified from RAW evidence):
- knowledge/qa/evidence/ingest-needs-activity-2026-08-14/full-suite.txt: "2 failed, 2668 passed in 1079.35s".
- The 2 failures are EXACTLY the CLAUDE.md-known pre-existing ones (grep ^FAILED). ZERO regressions. +6 passed vs 409 (2662->2668) = the new needs-activity tests.
- QA ran FOREGROUND (1079s), evidence-first.

RECORD: the ingest prompt direction is FLIPPED. A lazy, user-triggered /ingest/panel/needs-activity card lists myAP roster invoices with a status but NO activity history (source='myap' AND NOT EXISTS(invoice_activities), LIMIT NEEDS_ACTIVITY_PANEL_CAP=50) — 'these roster invoices need activity data'. Never fires on page load (card-dimmed + Load button). Combined with Plan A (409, strip + perf), the ingest reframe is complete. Work-machine T-3: CEO clicks 'Load Needs-Activity' to confirm it lists real invoices. Clean. Close 412.
