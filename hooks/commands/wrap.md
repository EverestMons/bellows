---
description: Arm the wrap-completion lock and perform the Eluvian 4-repo session wrap
---

# Session wrap (locked)

Perform the Eluvian session-wrap ritual. A hard-block lock is engaged for the
duration — you will not be able to end a turn until `wrap_check.py` verifies every
step. Do NOT hand-edit or delete `.wrap-in-progress` to escape; complete the work.

## Step 0 — ARM THE LOCK (do this first, before anything else)

```bash
touch /Users/marklehn/Developer/GitHub/.wrap-in-progress
```

## Then perform the ritual (reference: eluvian-session-wrap-ritual memory)

1. **Project repos** — in each project touched this session, commit completed plan
   files sitting untracked in `knowledge/decisions/Done/`. Leave unrelated
   pre-existing untracked files alone.
2. **bellows submodule** — commit this session's consumed
   `verdicts/resolved/processed-verdict-<id>-step-N.md` files
   (`chore(bellows): session wrap <date> …`), then push.
3b. **Lessons sweep — DO THIS AS ITS OWN DELIBERATE ACT (most-skipped step).**
   Ask: "what did this session teach that a future session on ANY project would
   want?" This is DISTINCT from the arc/baton narrative — recording the project arc
   is NOT a lessons sweep. Transferable shop-level lessons → `LESSONS.md`
   (house format; not while a lessons-forge cycle plan sits un-run; verify the
   prior last entry intact after append). Planner working-pattern lessons → the
   memory repo. **Then add a line to `shop_next_session.md`:**
   `Lessons-swept: <today's date> — <one-line delta, or 'none'>`
   (the lock verifies this line exists with today's date; that is how 3b becomes
   un-skippable).
3. **Governance root** (`/Users/marklehn/Developer/GitHub`) — refresh the baton
   (`shop_next_session.md`: preserve carried threads, add this arc's ships, demote
   prior ones), `git add bellows` to bump the submodule gitlink, commit
   (`docs: session wrap <date> — … refresh baton, bump bellows`), then push.
4. **Memory repo** (`~/.claude/projects/-Users-marklehn-Developer-GitHub/memory/`)
   — if any memories changed, commit them + `MEMORY.md` and push. Skip if untouched.

Use the current model's `Co-Authored-By:` trailer. Leave the Bellows daemon running.

## Finish

When done, end your turn normally. The Stop hook runs `wrap_check.py`: if all
steps verify it removes the sentinel and the turn ends; if not, it hands you the
exact remaining checklist and blocks until you finish.
