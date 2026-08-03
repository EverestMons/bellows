verdict: continue

Gates clean ("failures": []), QA 25 ✅ / 0 ❌, and every substantive claim re-verified by the
Planner from raw state rather than from the QA report's account.

=== THE ARTIFACT ===
- governance/knowledge/FORWARD.md exists, committed, working tree clean.
- ZERO data rows — nothing hand-authored.
- Header and separator byte-identical to BOTH proven registers (compared as lines).
- Preamble numbering-safe: zero matches for the daemon's row pattern.
- Rule 20 full canonical block ran: banner and PASSED line byte-exact; the one required
  evidence file (append-simulation.txt, 2194 bytes) is real and non-empty.
- The four other registers are unchanged: bellows 25, invoice-pulse 33, anvil 8,
  lessons-forge 1. Row 6b's HARD condition (no register LOST rows) holds.

=== ⚠️ A DEFECT IN THIS PLAN, FOUND BY THE AGENT AT RUN TIME — recorded, not hidden ===
QA row 7 mandates `grep -Fc -- '#### Forward Register'` across both step deposits return 0.
**That is UNSATISFIABLE on a correct run.** The deposits necessarily quote the FORWARD.md
preamble as evidence (Task C's full content, Task D's simulation output), and the preamble
CONTAINS that string because it describes how rows arrive. Measured: the count is 2 in each
deposit, all four matches being quoted preamble.

The QA agent did the right thing — ran the check, got 2, investigated the matches, and
explained why they are not a violation, rather than failing a correct run or passing silently.

**The row's INTENT is satisfied and was verified independently:** the QA report's
`### Ledger Updates` contains only `#### Project Status` and `#### Prompt Feedback` — no
Forward Register block — so the daemon will append nothing post-merge, which is this plan's
design (the file is in Step 1's files_changed, so an emitted block would be skipped anyway
and would falsely appear to have worked).

**The correct form, for any plan that clones this row:** scope the grep to the
`### Ledger Updates` section, or assert on the absence of the `#### ` HEADING within that
section — never a whole-file count of a string the artifact legitimately contains. This is
the same weak-marker class that recurred repeatedly across this session's cycles; it reached
a deposited plan here and was caught at run time rather than by the drafting cycle. Owed as
a LESSONS entry.

=== WHAT THIS CLOSES ===
Rule 46 routings from governance are no longer silently discarded. The register is LIVE
IMMEDIATELY — the daemon existence-tests the path at call time, not at startup, so no restart
is required. The next governance-dispatched plan's routings will land as row 1.
