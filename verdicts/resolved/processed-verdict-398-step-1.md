verdict: continue

Planner verdict on diagnostic-398 step 1 (delete-not-xml scoping) -> continue (single step, closes to Done).

MECHANICAL GATE: all PASS (deposit_exists, scope_check, rule_22). Findings present (23KB).

SUBSTANCE (Planner-verified on disk; NOT vouching for the agent's code-level line claims — the downstream executable re-verifies at its own HEAD per MUST-PRESERVE #5):
- Q1 delivered a COMPLETE child map + 12-step FK-safe delete order, AND caught a table the scout MISSED: action_queue_audit (contract_tables.py:878, soft-ref, invoice_id TEXT no FK) — exactly the failure mode MUST-PRESERVE #5 (re-enumerate) exists to prevent. 7 hard-FK + 4 soft-ref confirmed.
- Q2(c) delivered the load-bearing finding: not_xml invoices ARE real myAP invoices (carrier_amt + status/workflow from CSV; XML is a later enrichment layer). Hard delete destroys real invoice + validation data. This is CEO-facing and material.
- Q3 traced the actual transaction idiom (web/contracts.py:1162-1212, child-first single commit) + a standalone-script variant.
- Q4 gave leak-safe COUNT-only probes (count, per-table blast radius, charge-bearing/validated reality check) — deferred (dev empty).
- Q5 recommended a smallest-safe combo (dry-run default + JSON export + count-match confirm + atomic FK-safe txn, CEO-run cp1252-safe script). Q6 named the executable (delete_not_xml.py).
- MUST-PRESERVE 1-6 carried, including the two cycle folds (re-enumerate, materialized preview==delete set).

DIAGNOSTIC-ONLY: decides/deletes nothing. The CEO decision (whether/how to build the destructive executable, informed by Q2c + the Q4 work-machine counts) is surfaced separately. Clean; close.
