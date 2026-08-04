verdict: continue

Step 2 (QA) clean — Gate 1 closes for proposals 207-222. All eleven daemon gates PASS, including
the two that only go live on a QA step: rule_20_self_check (banner byte-exact, PASSED line present)
and rule_22_verification (deposits present, table clean, no hedging). Nine files: the QA report,
seven evidence files, and fwcheck.py.

=== VERIFIED FROM THE ARTIFACTS, NOT THE REPORT'S SUMMARY ===
Verification table: 11 ✅ and ZERO failing rows — both ❌ in the file are the column headers
`Status (✅/❌)` at the main table and the Rule 17 deliverable sub-table, located and confirmed.

Corpus final state re-read live: all sixteen 207-222 route='codify', status='proposed', audit
columns NULL; same-instant identity 92|76 so 92 == 76 + 16; outside-range image 76 rows; the seven
foreign non-codify rows unchanged (backlog 161,169 / reference 140,141,146,164,183); distribution
byte-identical, stale 3.

Evidence verified BY MARKER, not by presence — the Rule 20 block only tests non-empty and a
one-byte file satisfies it: `2d5cf9ab` x3 in doctrine_pins.txt (the pin plus BOTH triples, so
row 7's comparison had two real operands rather than citing itself), 161 lines in
outside_range_image.txt (both 76-row images), `SRCLOG-EXIT=` in src_untouched.txt, 16 `codify`
rows in route_readback.txt, `55 passed` in pytest_targeted.txt. Suite matches the authoring
baseline; zero regressions.

=== THE FORWARD REGISTER CHANNEL, SIXTH ATTEMPT ===
fwcheck.py reports FOUR items recovered, WRAP-CHECK=PASS, all four intact and untruncated, with
`FILE=` naming the artifact it read. BOTH runs are present in forward_register_check.txt and are
identical — so the post-final-edit re-run confirms the SHIPPED file, which is the CL7 decay guard
working rather than being asserted.

⚠️ NOT YET OBSERVABLE, and deliberately so: the FORWARD.md row count after the append.
_append_forward_row runs at teardown, after this step's process exits, so the plan asserts
items-in == items-out in-step and defers the row reconciliation to the session wrap. FORWARD.md
stood at 2 data rows (row 2 being the junk stub); four rows are owed. THAT RECONCILIATION IS
OWED AT WRAP and is the real test of the channel.

A0-dep took the fresh-write branch at k=0; the $BK single-source resume rule remains unexercised
in production.

Close the plan.
