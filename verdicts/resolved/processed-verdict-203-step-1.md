verdict: stop

**Step 1 executed correctly and all gates passed — this stop is NOT a fault of the step.** The DEV did exactly what the plan asked: ingested 3 entries, derived the work list via the Rule #47 helper, and recorded the dedup advisory read-only. The stop is because Step 1's output REVEALED a corpus-integrity bug that Step 2 would compound.

## Why stop (CEO decision 2026-07-16)

**Root cause proven.** The 2026-07-07 wrap commit (e57a22b) appended three lessons to LESSONS.md as **33 insertions, 0 deletions**. The appended block opens with a `---` separator, and `parse_lessons_md` assigns those separator lines to the PREVIOUS entry's body. Entry 137's `content_hash` therefore flipped `4ff4c905` -> `b9875afa` over **7 bytes of trailing whitespace**, with zero substantive change (bodies are byte-identical once the trailing separator is stripped — verified by parsing `git show e57a22b^:LESSONS.md` vs current).

**Damage.** That whitespace-only hash flip drove `ingest_lesson_entries`'s update path (`src/lessons_forge.py:143-150`), whose stale-marking is `WHERE entry_id = ? AND status != 'stale'` — it demotes ANY status, including `implemented`. Proposal 145 went **implemented -> stale** at 2026-07-16T13:15:46Z (distribution moved implemented 97->96, stale 3->4). A rule already codified in PLANNER_TEMPLATE silently lost its implemented record and re-entered the work list.

**Systematic, not a one-off.** All 4 `stale` proposals in the corpus are this same artifact — each entry was the LAST entry in LESSONS.md at the time of the prior cycle:

| Entry | Staled proposal | Reclassified as | Outcome |
|---|---|---|---|
| 93  | 98  | 122 | rejected |
| 116 | 121 | 123 | rejected |
| 123 | 130 | 131 | rejected |
| 137 | 145 (today) | pending | would be #4 |

Three of three completed instances ended as a **rejected duplicate proposal** — a 100% waste rate. Step 2 would have made entry 137 the fourth.

**Reframing that matters:** proposal 131 — the motivating case for plan 154's entire dedup-advisory build — is a DOWNSTREAM SYMPTOM of this bug. Plan 154 built machinery to help reviewers catch duplicates that this bug manufactures, rather than stopping their manufacture.

## Disposition

Fix the root cause before any reclassification, per the CEO's standing precedent (2026-06-03 Gate 1: route the underlying bug to a fix rather than codify/accommodate the workaround). A fix plan follows: normalize trailing separator/whitespace before hashing, guard the stale path against demoting terminal statuses, restore proposal 145 to `implemented`, and audit 98/121/130.

**Note for the re-dispatched cycle:** Step 1's ingest already COMMITTED — entries 138-140 exist and proposal 145 is already staled. A re-run will report `ingested_count=0` and a work list of [137,138,139,140] until the fix lands; that is expected, not an ingest failure.

**Plan 154 advisory (CEO: note and defer):** first production run measured 353 DB-wide overlaps; for entry 138 it returned 10 hits all reading `tag overlap: bellows; keyword overlap: bellows` — the heuristic degenerates to tag equality. Its fate is deferred to Gate 1 after the root-cause fix, since its value may largely evaporate once the duplicate generator is gone. No action on plan 154 in the fix plan.
