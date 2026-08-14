verdict: continue

Planner verdict on executable-404 step 2 (foreground QA) -> continue (TERMINAL — closes 404 to Done). The self-migrate hardening ships.

MECHANICAL GATE: all PASS — deposit_exists PASS, rule_20_self_check PASS (byte-exact), scope_check PASS.

SUBSTANCE (Planner-verified from RAW evidence):
- knowledge/qa/evidence/delete-not-xml-selfmigrate-2026-08-14/full-suite.txt: "2 failed, 2653 passed in 969.89s".
- The 2 failures are EXACTLY the CLAUDE.md-known pre-existing ones (grep ^FAILED confirms). ZERO regressions. +1 vs 403 (2652->2653) = the new self-migrate regression test.
- QA ran FOREGROUND (970s), evidence-first.

RECORD: delete_not_xml.py now calls init_db() at start -> self-migrates -> the live 'no such table: deleted_invoices' failure cannot recur; a regression test locks it. Delete/cascade/tombstone logic unchanged. Clean. Close 404.
