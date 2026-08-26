---
description: Align the session with the Eluvian path — pull latest code, assert environment, recite + assert the system wiring, surface parked arcs
---

# Eluvian alignment pass

1. **Pull latest code (multi-machine law: every machine runs the newest committed state).** Enumerate the repos DYNAMICALLY — never a hand list: the root `/Users/marklehn/Developer/GitHub`, every direct child directory with a `.git` and an `origin` remote, and the memory repo at `/Users/marklehn/.claude/projects/-Users-marklehn-Developer-GitHub/memory`. For each: `GIT_TERMINAL_PROMPT=0 git fetch origin` (a fetch failure is a LOUD warning, not a stop); report ahead/behind vs upstream; if BEHIND and not diverged → `GIT_TERMINAL_PROMPT=0 git pull --ff-only`; if DIVERGED, or the ff-only pull refuses, or the tree blocks it → report loudly and TOUCH NOTHING — never merge, rebase, stash, or reset on the command's behalf. ⚠️ If the bellows repo received new commits, compare the RUNNING daemon's sha (from `python3 bellows/status.py`) to the new HEAD and, when they differ, report **"bellows daemon restart needed — running old code"**: a live daemon keeps executing the code it loaded at start.

2. **Read the doctrine.** Load `/Users/marklehn/Developer/GitHub/ELUVIAN_PATH.md` in full. This is the governing process document.

3. **Assert the environment:**
   - **cwd** is `/Users/marklehn/Developer/GitHub` (the governance root)
   - **bellows daemon** is RUNNING — verify with `python3 bellows/status.py`
   - **wrap debt** — run `python3 bellows/hooks/eluvian/wrap_check.py` READ-ONLY (report its output, arm nothing)
   - **parked arcs** — report every line containing `⏸`, `PARKED`, or `RESUME AT` from the head of `shop_next_session.md`

4. **Recite AND assert the system wiring** (the map goes in the report so every machine's session starts from the same picture; each assert is a real check, not a recollection):
   - **Root doctrine:** `ELUVIAN_PATH.md` (governing process), `PLANNER_TEMPLATE.md` (Planner law), `DRAFTING_CYCLE.md` (drafting-cycle law), `GLOSSARY.md` (the ONE central domain glossary — entries tagged `[project: <name>]`, proposals 378 + 389; per-repo glossary files are POINTERS, never scaffold or write them), `LESSONS.md` (the shop lesson corpus — APPEND-ONLY, forge-ingested).
   - **bellows/** — the autonomous execution engine. Plans deposit as `ready-` files in each project's `knowledge/decisions/`; lifecycle: deposit receipt → clearance → daemon claim (id minted from `lifecycle.db`) → step gates → Planner verdicts via `tools/issue_verdict.py` → Done. The live `/wrap` and `/eluvian` commands are symlinks into `bellows/hooks/commands/`.
   - **lessons-forge/** — the lesson pipeline: ingests `LESSONS.md` into proposals; Gate 1 routes them (the non-author law, exec-459); Gate 2 codifies accepted rows into doctrine; `lessons-forge.db` is local operational state (untracked by policy).
   - **governance/** — shop-level plans and knowledge; it has NO own `.git` (its history lives in the root repo) and dispatches in place with absolute operands.
   - **memory repo** — Planner-personal working patterns; on a path to hardcoding — systems must not RELY on it.
   - **Projects** (anvil, invoice-pulse, freight-kb, …) — own repos, own `knowledge/decisions/` lanes; their DOMAIN knowledge lives in the central `GLOSSARY.md` under their project tag.
   Mechanical asserts (report each): `GLOSSARY.md` exists at the root; `bellows/lifecycle.db` exists; `lessons-forge/lessons-forge.db` exists.

5. **Report alignment or misalignment loudly.** State each check's result. If any check fails, state the failure clearly as a warning. **ADVISORY: never refuse to proceed** — a failed assert (including a failed fetch or a refused pull) reports but does not block (fork 3 ruling). Say so in the report.
