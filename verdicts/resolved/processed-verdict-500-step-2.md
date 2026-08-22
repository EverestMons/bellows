verdict: continue

Planner verification (Rule 22(b)) — plan 500 (CORRECTIVE to halted-499), Step 2 (QA, TERMINAL). ALL SEVEN gates PASS; no failure to adjudicate. Verified independently of the Receipt:

1. FULL SUITE GREEN: `63 passed in 0.10s`, 0 failed. ⚠️ I checked that this IS the full suite rather than accepting the headline: `src/test_lessons_forge.py` is the ONLY test file in the repo, and 63 collected exceeds its 58 `def test_` lines through parametrization. The count also reflects this plan's 8 new tests.

2. ALL FIVE CANARY ASSERTIONS PASS, each reported separately as mandated, and the A/B structure was honoured rather than collapsed into a single run:
   - **(i)** `arm_A.inserted = 11`, `arm_B.inserted = 11` — annotation adds nothing.
   - **(ii)** COMPUTED at run time (not the hard-coded constant walk 1 removed) and equal to the measured control. Under halted-499 this arm gave **51**; the 40-row double-space regression is closed.
   - **(iii)** `stale_proposals_marked = 0` in both arms — the 250 implemented proposals untouched.
   - **(iv)** annotated entries resolve to their ORIGINAL row ids.
   - **(v)** identity property **381/381**.

3. ⚠️ THE 381 IS CORRECT AND I CHECKED IT RATHER THAN ASSUMING: it is 370 stored + the 11 ARM-A legitimately inserted into the throwaway copy before the identity check ran. That the 11 NEW rows also satisfy identity is a stronger result than 370/370 would have been — it proves the INSERT path stores the canonical form, which is the half of the fix a lookup-only test cannot reach.

4. THE LIVE CORPUS WAS NEVER TOUCHED. QA reports SHA256 before and after as identical; I re-ran `shasum -a 256` against the live DB myself and it still matches that value, and `lesson_entries` is still 370. Every exercise ran against `cp` copies in tmp.

The regression that was live in `main` is closed. LESSONS.md annotation is now safe: adding `[status: ...]` / `[target: ...]` to a heading resolves to the same corpus row, inserts nothing, and stales no proposal.

Terminal step: close to Done.
