verdict: continue

Planner verdict on diagnostic-417 step 1 (xml-refetch idempotency) -> continue (single step, closes to Done).

MECHANICAL GATE: all PASS (deposit_exists, scope_check, rule_22). Findings present (20KB).

SUBSTANCE (Planner-verified on disk; NOT vouching for the agent's code-level line claims — the executable re-verifies at its own HEAD):
- Q1: confirmed the append bug + that invoice_charges/locations are EXCLUSIVELY XML-derived (D1 fold -> blanket delete-first is SAFE). Found the choke point has 5 callers (gap_dashboard.py:3899 was uncounted) + a BYPASS path (app.py:710 ingest_xml_paste calls the inserts directly) — the fix covers the 5 via apply_xml_to_invoice; the bypass is a separate follow-up.
- Q2 (load-bearing): implicit-transaction rollback exists but is FRAGILE; fix MUST add SAVEPOINT wrapping inside apply_xml_to_invoice (cloning the validate route app.py:2125-2147). Emulate-existing-pattern.
- Q3: recommends LEAVE superseded XML (audit; superseded invoices excluded from routing) — argues the CEO's "clear existing" is the RE-FETCH case (idempotency fix), not supersession. A CEO policy fork.
- Q4: work-machine dup-count probes incl. the byte-identical Probe 3 (V1 fold); recommends clear-all + re-enrich (pulls current XML) over min-id dedup.
- Q5: confirmed do NOT block re-fetch. Q6: smallest fix = delete-first + SAVEPOINT in apply_xml_to_invoice; bypass-refactor + supersession + existing-dup cleanup sequenced separately.
- MUST-PRESERVE 1-7 carried (incl. the 5th-caller/bypass note).

DIAGNOSTIC-ONLY: decides/changes nothing. CEO decisions (build the fix; the Q3 supersession policy) surfaced separately. Clean; close.
