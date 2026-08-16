verdict: continue

Planner verdict on executable-419 step 3 (foreground QA) -> continue (TERMINAL — closes 419 to Done). The XML re-fetch idempotency fix + dedup tool ship.

MECHANICAL GATE: all PASS -- deposit_exists PASS, rule_20_self_check PASS (byte-exact), scope_check PASS.

SUBSTANCE (Planner-verified from RAW evidence):
- knowledge/qa/evidence/xml-refetch-idempotency-2026-08-14/full-suite.txt: "2 failed, 2689 passed in 966.79s".
- The 2 failures are EXACTLY the CLAUDE.md-known pre-existing ones (grep ^FAILED). ZERO regressions. +21 vs 412 (2668->2689) = the new idempotency (8) + dedup (8) + other tests.
- QA ran FOREGROUND (967s), evidence-first.

RECORD: apply_xml_to_invoice now delete-firsts inside a SAVEPOINT -> Fetch XML is idempotent (replace, not append) + atomic (rollback keeps prior charges, never zero). dedup_xml_data.py (CEO-run, dry-run default) cleans accumulated dups by re-enrich-only (file-absent skipped, never emptied). Supersession-clear left OUT (CEO chose LEAVE); invoice-versioning idea parked separately. Work-machine T-3: CEO presses Fetch XML twice (no double) + runs dedup_xml_data.py dry-run -> --execute. Clean. Close 419.
