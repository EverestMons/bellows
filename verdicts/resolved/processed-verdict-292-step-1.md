verdict: continue

Self-issued under delegated verdict authority. Gates clean ("failures": []), read-only held
(git status on bellows.py and tests/ stayed clean throughout, watched live), and the deposit
answers every question with per-block evidence rather than argument.

=== THE CENTRAL RESULT — both mandatory controls PASS ===
Candidate rule: if >=2 non-empty stripped lines match ^(-\s|\d+\.\s), emit one row per
matching line; otherwise fall back to lines[0].

- NEGATIVE CONTROL (plan 62's narration fixture): 0 bullet lines -> falls back to lines[0]
  -> "CANARY item text here". "Now commit" and "All 5 checks" both excluded. THE GUARD
  SURVIVES. This was the question the diagnostic existed to settle, and it settled it by
  execution, not by reasoning about the regex.
- POSITIVE CONTROL (the six-bullet block): 6 bullets -> 6 rows.

=== WHAT IT CORRECTED IN ITS OWN INSTRUCTIONS ===
The diagnostic's brief asserted "plan 288 emitted six items as (a)..(f)". The corpus shows
288 emitted THREE and the six-item block was plan 289's. The Planner introduced that error
by mislabelling a 2026-07-31 Gate 1 QA report; the agent corrected it from the corpus and
filed it as Unresolved #3 rather than silently adopting the wrong premise. Correct behaviour.

=== SCALE IS LARGER THAN THE PLANNER ESTIMATED ===
11 of 19 corpus blocks are multi-item. The single-line reduction has been dropping content
across the whole history, not merely in the four-item backlog that prompted this.

=== HONEST ABOUT WHAT IT DOES NOT FIX ===
Q6 reports a partial-write window: if the process dies after the file write/commit but
before record_ledger_write, a redo re-appends and yields 2N rows. It states plainly this is
the SAME failure class as today's single-row behaviour, scaled by N — not a new defect
introduced by the change, and not one the change closes.

=== THREE UNRESOLVED ITEMS, ALL LEGITIMATE ===
1. Several invoice-pulse plans emitted Forward Register blocks with no matching daemon
   append — a possible second instance of the missing-destination bug plan 291 fixed for
   lessons-forge. Needs its own check; do NOT assume it is the same cause.
2. One plan emitted a pipe-delimited TABLE rather than bullets — a shape the candidate rule
   does not handle.
3. The plan-attribution correction above.

Items 1 and 2 must be folded into the downstream plan's scope rather than discovered
mid-run. Item 2 in particular decides whether the rule needs a third branch or an explicit
declared non-goal.

=== BACKLOG ===
Receipt emitted exactly one item and it landed as bellows/knowledge/FORWARD.md row 25 —
the mechanism used correctly while under investigation. Three backlog items remain.
