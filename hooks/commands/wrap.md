---
description: Arm the wrap-completion lock and perform the Eluvian 4-repo session wrap
---

# Session wrap (locked)

Perform the Eluvian session-wrap ritual. A hard-block lock is engaged for the
duration — you will not be able to end a turn until `wrap_check.py` verifies every
step. Do NOT hand-edit or delete `.wrap-in-progress` to escape; complete the work.

## Scope: THIS MACHINE ONLY

/wrap wraps the sessions that ran on the machine it is invoked from. Fetch every
repo FIRST — to judge debt against fresh state and to land local commits cleanly —
but never sweep, narrate, or complete another machine's sessions: their arcs,
verdicts, and `Lessons-swept:` lines are theirs. If fetch reveals the reported
debt was satisfied elsewhere, say so and stop rather than re-wrapping it.
(Earlier terminals on THIS machine are in scope; other machines are not.)

Machine layouts differ; the governance root is `$ELUVIAN_WRAP_ROOT` (shop
machine: `~/Developer/GitHub`; Mac mini: `~/Developer/eluvian-governance`) and
the memory repo is `$ELUVIAN_WRAP_MEMORY` — both set in `~/.claude/settings.json`
per machine, same names the hooks read.

## Step 0 — QUEUE CHECK, then ARM THE LOCK, then FETCH

**The wrap's FIRST action is a queue check, not the sentinel touch** (SESSION 59's
measured lesson; mid-flight collisions measured again 2026-08-24): run
`python3 <bellows>/status.py` and read IN-FLIGHT / AWAITING VERDICT. If any plan
is mid-flight or verdict-pending on THIS machine, do not append to any artifact
that plan is editing (baton, LESSONS.md, its project's files) — drive the plan
to its pause or close first, or coordinate, and only then arm. A quiet queue →
arm immediately:

```bash
touch "${ELUVIAN_WRAP_ROOT:?ELUVIAN_WRAP_ROOT is unset — the harness sets it; see MACHINE_SETUP.md §1}/.wrap-in-progress"
```

Then `git fetch` in the governance root and every project repo touched this
session, BEFORE judging or editing anything — the debt hook and `wrap_check`
read the LOCAL tree, so stale-tree debt is indistinguishable from
done-on-another-machine-and-not-pulled (measured 2026-08-24).

## Then perform the ritual (reference: eluvian-session-wrap-ritual memory)

1. **Project repos** — in each project touched this session, commit completed plan
   files sitting untracked in `knowledge/decisions/Done/`. Leave unrelated
   pre-existing untracked files alone. Then push each touched project repo —
   the push-each law covers ALL FOUR repo classes, not just bellows/root/memory.
2. **bellows submodule** — commit this session's consumed
   `verdicts/resolved/processed-verdict-<id>-step-N.md` files
   (`chore(bellows): session wrap <date> …`), then push.
3b. **Lessons sweep — DO THIS AS ITS OWN DELIBERATE ACT (most-skipped step).**
   Ask: "what did this session teach that a future session on ANY project would
   want?" This is DISTINCT from the arc/baton narrative — recording the project arc
   is NOT a lessons sweep. Transferable shop-level lessons → `LESSONS.md`
   (house format; verify the prior last entry intact after append;
   classes-not-narratives — record the transferable CLASS, never the session's
   story; never duplicate an already-recorded class).

   ⛔ **Guard (a) is MECHANICAL, and it is RE-TAKEN immediately before the write.**
   Taken once at the top of the sweep, its window is unbounded wall-clock — and for
   a plan paused at a verdict it spans the whole pause. Measured 2026-09-04: two
   writers landed in that window on one day (this machine appended entries 419-423;
   another machine then appended 424-425 and pushed, rejecting this machine's
   commits). Both rebased cleanly, which is ordering luck, not a guarantee.

       python3 bellows/tools/lessons_guard.py pin              # refuses if FROZEN; emits the sha
       # ...compose the entry, then, as the LAST act before writing:
       python3 bellows/tools/lessons_guard.py verify --sha <sha>

   `verify` refuses (exit 2) if the corpus FROZE or if `LESSONS.md` moved since the
   pin — another session here, or another machine's push. ⛔ **Exit 2 means do not
   write**: re-read the file and re-take the pin. The tool scans all TWELVE
   `decisions/` lanes from the shop root, not the single lane the doctrine text
   names, and it treats `halted-`/`parked-` as PARKED (they do not freeze) while
   `in-progress-` and `verdict-pending-` DO. **Marker on a new entry: `[status: pending]` — and
   ONLY that.** Since 2026-09-01 the `[status:]` marker is a projection of the
   forge DB's `lesson_proposals.status` (implemented / proposed / accepted /
   reference / rejected / superseded); `pending` is the one file-side value and
   means "no DB row yet — not ingested". Never write `learned`/`codified`, and
   never set a DB value by hand: after the next forge ingest, run
   `python3 lessons-forge/scripts/project_status_markers.py --db <live db>
   --lessons LESSONS.md --apply` (on the machine that holds the live DB; use
   `--snapshot <dump.sql>` elsewhere) and let it stamp the DB's status. Planner
   working-pattern lessons → the memory repo. **Then add a line to `shop_next_session.md`:**
   `Lessons-swept: <today's date> [sid: <first-8-of-session-id>] — <one-line delta, or 'none'>`
   (the stop-hook lock verifies the NEWEST such line carries THIS session's id;
   the debt hook checks for today's date. Your session prefix is the first 8
   characters of the session UUID — visible in `hooks.log` or receipt filenames).
   **Law:** never start a baton line with a bare `Lessons-swept:` except the
   affirmation itself — format examples in prose must be backticked.
3d. **Domain-knowledge sweep.** Ask: "what domain knowledge did this session
   surface that belongs in the glossary?" For each project touched this
   session, review the session's work and deposit any DEFINITIONS (not
   runbooks, not traps — per the glossary discriminator) into the CENTRAL
   glossary at `$ELUVIAN_WRAP_ROOT/GLOSSARY.md`, each entry as
   `## <term> [project: <name>]` (comma-separate multiple project tags; the
   file already exists — APPEND-ONLY, non-destructive-append and
   class-not-narrative guards apply). ⚠️ NEVER write to — and never scaffold —
   a per-repo `knowledge/glossary.md`: the per-repo files are RETIRED to
   pointers (proposals 378 + 389, PT v4.93, plan 542, 2026-08-26).
   If nothing qualifies, move on — the step is complete when the question has
   been asked, not when an entry has been written.
3. **Governance root** (`$ELUVIAN_WRAP_ROOT`) — refresh the baton
   (`shop_next_session.md`: preserve carried threads, add this arc's ships, demote
   prior ones — append your OWN session block only; never rewrite another
   machine's blocks), `git add bellows` to bump the submodule gitlink, commit
3c. **Carried items → tuyere threads** (GOVERNANCE §5b in the tuyere repo) —
   enter this session's carried/deferred items as threads so the mutable
   to-do state lives in the database, not the baton:
   `python3 -m tuyere.threads add "<imperative title>" --project <p> --body "<standalone context>" --origin '{"kind":"wrap","date":"<date>"}'`
   (run from a tuyere checkout with DB access; close finished ones with
   `threads done <id>`). The baton block stays the NARRATIVE record — write
   carried items there as prose too, but the thread row is the tracked copy.
   No tuyere checkout on this machine → record in the baton alone, as before.
   (`docs: session wrap <date> — … refresh baton, bump bellows`), then push.
   On the mini the submodule dirs are uninitialized — bump the gitlink with
   `git update-index --cacheinfo 160000,<bellows-HEAD-sha>,bellows` instead.
4. **Memory repo** (`$ELUVIAN_WRAP_MEMORY`) — if any memories changed, commit
   them + `MEMORY.md` and push. Skip if untouched. On the mini this points at
   the auto-memory dir, which is not a git repo — write memories there but the
   commit/push half is N/A.
5. **Record the wrap (R2)** — from a tuyere checkout with DB access:
   `.venv/bin/python -m tuyere.wraps record <full-session-uuid>` (the machine
   defaults to this host). No tuyere checkout or unreachable DB → SKIP and say
   so (fail-open ritual; the registry is information, never a gate). ⚠️ This
   step is UNVERIFIED by the lock (deliberate — the stop path stays
   subprocess-free), so the most-skipped-step class applies; a registry row
   attests that THIS STEP RAN, never that the wrap verified complete.

Use the current model's `Co-Authored-By:` trailer. Leave the Bellows daemon running.

## Finish

When done, end your turn normally. The Stop hook runs `wrap_check.py`: if all
steps verify it removes the sentinel and the turn ends; if not, it hands you the
exact remaining checklist and blocks until you finish.
