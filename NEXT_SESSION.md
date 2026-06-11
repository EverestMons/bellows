# bellows — Next Session

**As of:** 2026-06-11 (Reporting Phase 1 shipped)

## State

- **Reporting Phase 1 COMPLETE and ACTIVE.** Executable A (monotonic id mint at claim, id-only filenames, substring fixes, [id] commit tagging, startup recovery) and Executable B (full lifecycle DB: 10 tables per blueprint 3.4 DDL, write calls at all 7 transition boundaries, log-and-continue contract) both shipped, QA-verified, daemon restarted on 4667e0b. lifecycle.db live at bellows root (gitignored), upgraded in place at restart; bootstrap rows resolved correctly (plans 1/2 abandoned [pre-B halts], 3 closed).
- **New conventions in force:** Planner deposits use `<type>-draft-<HHMMSS>.md` placeholder naming (no descriptive slug); Bellows mints id at claim and renames to `in-progress-<type>-<id>.md`; verdicts are `verdict-<id>-step-N.md`; Done filing is id-canonical (`Done/executable-3.md` is the first). Legacy slug+date names remain accepted everywhere (dual-format, no migration). Descriptive names live in `# Title` only. Commit tagging `[<id>]` confirmed working in production.
- Design artifacts: `knowledge/architecture/lifecycle-db-id-threading-blueprint-2026-06-11.md` (Sections 1-6 incl. the 27-site filename consumer census), `reporting-phase-0-coverage-map-2026-06-10.md` (governance root).
- Plan ids 1 and 2 were halted reruns of B's DEV step (transient agent stall; instructed-DDL deviation respectively) — see LESSONS 2026-06-11 (two planner-discipline entries) and processed verdicts 1/2/3.

## Next pickup

- **Reporting Phase 2:** read-side reporting over lifecycle.db (generated cycle reports replacing hand-maintained BACKLOG backward-looking content per `roadmap-reporting-vs-backlog-2026-06-09.md`). The DB now accrues full transition data on every plan; let a few plans flow through before designing queries if useful.
- **PLANNER_TEMPLATE update owed:** codify the new deposit-placeholder convention, id-native verdict naming, and "implements diagnostic <id>" citation convention (integer ids only create derivations rows — legacy slugs don't resolve, by design). Also fold the two 2026-06-11 LESSONS into the Plan Authoring Checklist (scope lists include conftest for new module-level state; never paraphrase artifact-authoritative specifics inline).
- Bellows reliability backlog still queued: isinstance asymmetry (bellows.py:505/594 — relocate by symbol, lines stale), config.json gitignore, `Bash(git:*)` breadth.

## BACKLOG adds this session (in knowledge/BACKLOG.md)

- Persist partial agent output stream on inactivity-timeout kill (raw_output empty on kill — plan-1 stall had zero forensics).
- in-progress plan files from pre-id era: none in flight; dual-format tolerance covers historical artifacts indefinitely.
