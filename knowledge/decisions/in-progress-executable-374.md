# Executable: archive the three parked halted plans — bellows

**Type:** Executable
**Project:** bellows
**Depends on:** the three parked files (all audits complete — 336's successor 337 Done; 365's corrective 366 Done; 369's corrective 370 Done), the halted-archival arc's validated move form (plans 252–256, 24/24 archived), `knowledge/decisions/archived-halted-plans/` (the destination, exists)
**Created:** 2026-08-13
**Author:** Planner
**Slug:** `archive-halted-bellows-2026-08-13`
**dispatch_mode:** bellows
**pause_for_verdict:** always
**Priority:** 5
**cycle_tier:** T0

⚠️ **ID NOTE — the deposit filename is decided AT DEPOSIT.** `id_sequence` read at deposit, never at authoring.

---

## Why this exists

Three bellows halted files are parked with their audits complete and dispositions decided (archive): `halted-diagnostic-336.md` (its recall successor 337 shipped), `halted-executable-365.md` (its corrective 366 shipped), `halted-diagnostic-369.md` (its corrective 370 shipped — the teardown-halt predecessor). The halted-archival arc validated exactly this move form. **`scope_check` cannot verify rename destinations per-file — THE MANIFEST BELOW IS THE MOVE GUARD**, asserted before and after.

**The manifest (measured at authoring — the A0 gate; any mismatch → HALT, the file moved under the plan):**

| file | sha256 |
|---|---|
| `knowledge/decisions/halted-diagnostic-336.md` | `8b45bb9ea0d843ded2420026c5137472b90be99285d51b3aad64d895d1f28a57` |
| `knowledge/decisions/halted-executable-365.md` | `3cd60e9cf0c8de5ae57dbe68f8c9700bc7e4f22da8ccc91aa91549569e067c99` |
| `knowledge/decisions/halted-diagnostic-369.md` | `8d1c262b4f5a6a4b2f4a328347a146d2e79e1717578cf74d209875f4fae142d2` |

---

## Scope

- `bellows/knowledge/decisions/archived-halted-plans/halted-diagnostic-336.md`
- `bellows/knowledge/decisions/archived-halted-plans/halted-executable-365.md`
- `bellows/knowledge/decisions/archived-halted-plans/halted-diagnostic-369.md`
- `bellows/knowledge/qa/evidence/archive-halted-bellows-2026-08-13/manifest.txt`

---

## How to Run This Plan

**Bootstrap prompt:**
```
Read the plan at knowledge/decisions/in-progress-executable-<id>.md (the daemon renames the deposited placeholder on claim). Execute Step 1 (the only step). After completing it, STOP.
```

---

## STEP 1 — DEV (the move, manifest-guarded)

> **FIRST — post a short visible chat message (1-2 sentences) confirming you are starting.** Do NOT rename this file. ⚠️ **THE WORKTREE RULE:** every git command runs from your cwd; never `-C` into another checkout for a WRITE.
>
> **Task A0 — branches, catch-all LAST.** (0) tree shape: `git rev-parse --show-toplevel` prints a tree containing `knowledge/decisions`. (1) **manifest gate:** `shasum -a 256` of each of the three SOURCE paths matches the manifest exactly. (2) destinations absent.
> - **FRESH** = (0)+(1)+(2) hold → proceed. **RE-ENTRY** = sources absent AND all three destinations present with matching shas → the move landed; write the manifest receipt if absent and report complete. **NONE-MATCH** = anything else → HALT quoting every measurement.
>
> **The move:** capture the pre-move `shasum` outputs, then `git mv` each file into `knowledge/decisions/archived-halted-plans/`, then **prove the post-condition** (each source ABSENT, each destination present with its manifest sha — after != before, never just the command's exit). Write `knowledge/qa/evidence/archive-halted-bellows-2026-08-13/manifest.txt` carrying the pre- and post-move `shasum` raw outputs. Commit everything from cwd with a pathspec naming the three destinations + the manifest file, subject `[<id from your plan filename>] archive-halted-bellows-2026-08-13: three audited halted plans archived (manifest-guarded)`. Then STOP.
>
> **Deposits:**
> - `bellows/knowledge/decisions/archived-halted-plans/halted-diagnostic-336.md`
> - `bellows/knowledge/decisions/archived-halted-plans/halted-executable-365.md`
> - `bellows/knowledge/decisions/archived-halted-plans/halted-diagnostic-369.md`
> - `bellows/knowledge/qa/evidence/archive-halted-bellows-2026-08-13/manifest.txt`
>
> **Scope:**
> - `bellows/knowledge/decisions/archived-halted-plans/halted-diagnostic-336.md`
> - `bellows/knowledge/decisions/archived-halted-plans/halted-executable-365.md`
> - `bellows/knowledge/decisions/archived-halted-plans/halted-diagnostic-369.md`
> - `bellows/knowledge/qa/evidence/archive-halted-bellows-2026-08-13/manifest.txt`

---

## Drafting Cycle

**Tier:** T0 — move-only, no tier trigger fires (no data mutation, no doctrine, no gate, single subsystem). **Floor pass (lens 4) run at authoring:** the halted-archival arc is the direct precedent (24/24 by this form); the scope-check-illusory lesson is carried as the manifest guard; the worktree rule applied. `plan_lint` mechanical preverify in lieu of a walk cycle (the CEO-sanctioned T0 path); result recorded in the deposit commit.
