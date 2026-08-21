# ⚠️ v0 DRAFT — lessons-forge — diagnostic: reconcile LESSONS.md against the forge and design the `learned_lessons` log
**Date:** 2026-08-21 | **Tier:** Medium | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** none (read-only diagnostic) | **Execution:** Step 1 (READ-ONLY DIAGNOSTIC) | **Priority:** 1

**auto_close:** false
**pause_for_verdict:** after_step_1

> ⚠️ **v0 DRAFT — NOT cycled, NOT deposit-ready.** Supersedes `v0-diagnostic-lessons-corpus-routing-2026-08-21.md`, whose premise (build a classification from scratch) was FALSE: the forge already carries one.

## The objective (CEO, 2026-08-21) — QUERYABILITY, not size

> *"I want to be able to query LESSONS.md and know exactly what needs implementation. I don't care about the number of entries."*
> *"Lessons/procedures stored in memory should be added into LESSONS.md as an item to build — the goal being to not rely on memory for proper system execution."*

⚠️ **This supersedes an earlier framing that optimized for SHRINKAGE.** Size was a proxy; the real requirement is that a grep answers *what still needs building*. That changes the design in three ways, all favourable:
- **Annotate, do not delete.** Marking an entry `implemented` is additive and reversible; a wrong mark costs a re-check, whereas a wrong DELETE destroys the record. Retirement to a `learned_lessons` log becomes OPTIONAL housekeeping rather than the point.
- **The detector's precision bar drops accordingly** (see Q2) — it now gates a label, not a deletion.
- **`LESSONS.md` becomes the SINGLE build queue**, absorbing memory's un-built items so that no operational knowledge lives in recall.

### The unified queue (Planner-computed 2026-08-21 — RE-VERIFY)

| source | count | disposition |
|---|---:|---|
| `LESSONS.md` pending | **63** | stays, marked `pending` |
| `LESSONS.md` never ingested | **7** | triage, then marked |
| migrated from memory (CODE 48 + DOCTRINE 39 + per-repo 16) | **103** | added as build items |
| **= TOTAL NEEDING BUILD** | **173** | the answer a query must return |
| `LESSONS.md` already implemented | 250 | marked `learned` |
| memory history | 15 | dropped |
| memory project status | 14 | to the baton |

**Operational content remaining in memory afterwards: 0.**

## Context — the finding that reframes the whole effort

**CEO principle:** a lesson is finished when the system enforces it and the note becomes redundant. `LESSONS.md` is a staging QUEUE, not a log; its size is a debt metric.

**Measured 2026-08-21 — the pipeline exists and half-works.** `lessons-forge/lessons-forge.db` already carries `lesson_entries` (370, all sourced from `LESSONS.md`, 2026-04-14 → 2026-08-19) and `lesson_proposals` (378) with `target_layer`, `target_artifact`, `route`, `status`, `duplicate_of`. **Routing was mechanized. The SHRINK step never was.**

| measure | value |
|---|---|
| entries currently in `LESSONS.md` | **320** |
| matched to the forge by normalized heading | **313 (98%)** |
| **in-file AND already `implemented`** | **250** |
| in-file, proposals but none implemented (the REAL queue) | **63** |
| in-file, never ingested | **7** |
| entries in the DB but no longer in the file | ~50 (removal HAS precedent) |

**⇒ `LESSONS.md` should be ~70 entries. A 78% shrink, available now, on work already done.**

**The second finding — the pipeline routes to DOCS, not to the system.** `target_artifact`: `PLANNER_TEMPLATE.md` 204, `DRAFTING_CYCLE.md` 101, and **7 total to code** (`bellows.py` 3, `walk_register_lint.py` 2, `plan_lint.py` 1, `runner.py` 1). `target_layer` is 334 `governance` / 20 `structure` — **there is no CODE, glossary, CLAUDE.md or DELETE rung in the taxonomy.** That is why `PLANNER_TEMPLATE.md` is 420 KB and `DRAFTING_CYCLE.md` 129 KB: lessons have been faithfully converted into more prose. Shrinking `LESSONS.md` without fixing this just moves the bytes.

## The `learned_lessons` design question (CEO-directed artifact)

The log is to record what was implemented, so the queue can shed it. ⚠️ **`lesson_entries.raw_content` ALREADY stores the full text of all 370 entries** — so removing an entry from `LESSONS.md` loses nothing today. The log is therefore mostly a VIEW over data already held.

**Planner recommendation (argue it, do not assume it):** make `learned_lessons` a TABLE/VIEW in the forge DB — `entry_id`, `heading`, `entry_date`, `target_artifact`, `implemented_at`, `proposal_id`, `verification_evidence` — plus an on-demand report generator. ⚠️ **Do NOT create a `LEARNED_LESSONS.md` holding all 250 entries**: at ~480 KB that recreates the exact problem in a new file. If a browsable artifact is wanted, generate it on request rather than maintaining it.

## MUST-PRESERVE

- **READ-ONLY.** This plan proposes and measures. It does not delete a single line of `LESSONS.md`, does not write to the forge DB, and does not create `learned_lessons`. Those are a later, reviewable executable.
- ⚠️⚠️ **`status='implemented'` IS A MARKER, AND THIS SESSION PROVED MARKERS UNRELIABLE.** The memory audit found `SHIPPED`/`FIXED`/`COMPLETE` to be exactly the class that lies. **No entry may be marked `learned` on the strength of its status alone** — the label requires evidence that the target artifact actually contains the rule, cited `file:line`. Anything undecidable is marked `unknown`. And since the objective is queryability rather than size, **prefer marking over deleting in every case**: a deletion that turns out wrong cannot be queried back.
- Do not append to `LESSONS.md` while a lessons-forge cycle plan is un-run (checked 2026-08-21: only `halted-executable-425`, so clear — RE-VERIFY).
- DB reads only via `file:<abs>?mode=ro`.

## STEP 1 — READ-ONLY DIAGNOSTIC

**Role:** DEV (read-only audit). Contract: `/Users/marklehn/Developer/GitHub/READONLY_AUDIT_CONTRACT.md`.

**Q1 — Reproduce the reconciliation.** Independently re-derive the 320 / 313 / 250 / 63 / 7 figures above. Report your own numbers; if they differ, yours supersede. State the matching method and its failure modes (the Planner used normalized-heading matching after tag-stripping; `content_hash` may be stronger — evaluate it).

**Q2 — BUILD AND MEASURE THE RETIREMENT DETECTOR. This is the load-bearing question.** For an entry marked `implemented`, decide whether the target artifact REALLY contains the rule. Propose the check, run it over all 250, and report how many PASS, FAIL, and are UNDECIDABLE. Then hand-verify a random sample of 30 by reading both the lesson and the target, and report the detector's PRECISION against that sample. ⚠️ Because the detector now sets a LABEL rather than authorizing a deletion, a moderate precision is workable — but it must still be MEASURED and stated, and entries it cannot decide must be marked `unknown`, never silently `learned`. A query that returns a confidently wrong build list is worse than one that admits uncertainty.

**Q3 — What happened to the ~50 already-removed entries?** They were ingested but are no longer in the file. Determine whether removal was deliberate (precedent to follow) or accidental (a data-loss event to understand). Cite git history.

**Q3b — DESIGN THE QUERYABLE ENTRY SCHEMA. This is now the primary deliverable.** Propose the machine-readable fields every `LESSONS.md` entry carries so a grep answers "what needs implementation" exactly — at minimum a state (`pending` / `learned` / `unknown`) and a target (the artifact that would enforce it). Entries today carry `[tag: ...]`; propose whether to extend that convention or add a distinct line, and show the EXACT query for each of: what needs building, what needs building in `plan_lint.py`, what was learned and where it landed. ⚠️ Verify the format survives the forge's ingest parser — a schema that breaks ingestion trades one problem for another. Show the parser path you checked.

**Q3c — Plan the memory migration (103 items).** The memory index carries 103 un-built operational items (CODE 48, DOCTRINE 39, per-repo 16) that must become `LESSONS.md` build entries so nothing operational depends on recall. Propose the transform: how a memory file becomes an entry, what date it carries (observed vs migrated), how its existing `[[wiki-links]]` are preserved or rewritten, and how to avoid double-entry where a memory and a lesson already describe the same rule — ⚠️ measure that overlap rather than assuming it is zero. Routing per item is in `governance/knowledge/research/memory-to-system-audit-2026-08-21.md`; treat it as a STARTING POINT to verify, not as truth.

**Q4 — Design `learned_lessons` (now OPTIONAL — argue whether it is needed at all).** Propose the schema, its population query, and the retirement protocol: what must be true before an entry moves. Argue the table-vs-file question above rather than inheriting the recommendation. State how a reader answers "why is this lesson gone?" a year from now.

**Q5 — Characterize the 63 that remain.** These are the genuine queue. Group them by what would enforce them, using the extended ladder (CODE / glossary / CLAUDE.md / DOCTRINE / BACKLOG / DELETE). This is the input to the batch plans.

**Q6 — Fix the taxonomy.** `target_layer` has no CODE, glossary, CLAUDE.md or DELETE rung. Propose the extension and the migration for the 378 existing proposals. ⚠️ Of the 305 routed to `PLANNER_TEMPLATE.md`/`DRAFTING_CYCLE.md`, estimate how many should have been CODE — that number is the ongoing leak, and it matters more than the one-time shrink.

**Q7 — The 7 un-ingested entries.** Why did ingestion miss them? Is the ingest path lossy, and does that undermine the corpus as a system of record?

**Q8 — Sequence it.** Propose the executables that follow, in order, with what each retires.

**Findings document:** Q1–Q8 with command output or `file:line` per answer. Close with `## What could not be measured` (empty is legitimate, MISSING is not), `## Open forks`, and `## Recommended executables`.

**Scope:**
- `/Users/marklehn/Developer/GitHub/lessons-forge/knowledge/research/lessons-reconcile-learned-2026-08-21.md`

**Deposits:**
- `/Users/marklehn/Developer/GitHub/lessons-forge/knowledge/research/lessons-reconcile-learned-2026-08-21.md`

**Commit:** `git -C /Users/marklehn/Developer/GitHub/lessons-forge add <abs> && git -C ... commit -m "..."`. Edit and commit INSIDE your worktree. Your final operation is the commit.

## v0 authoring notes (delete before deposit)
- Not done: walk 0, any lens walk, `plan_lint`, `cycle_check`, tier computed against §1.
- ⚠️ Verify `lessons-forge/knowledge/research/` exists, and the forge worktree contract (`FORGE_GITHUB_ROOT` + absolute DB path) before deposit.
- Q2 is the direction question: if the detector cannot be made precise, the 78% shrink is NOT authorized and this becomes a staged manual retirement. Treat that as a possible §2.0 RE-DRAFT trigger, not a fold.
- Consider whether Q6 should split into its own plan — the taxonomy leak is arguably more valuable than the shrink, and bundling may trip `ESCALATE:yield-rising` as the paired wrap-hook plan did.
