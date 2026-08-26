# Bellows
Bellows is the autonomous execution engine for Eluvian. It runs plans deposited by the Planner via claude -p, feeds step output to the Planner API for judgment, and notifies the CEO via Pushover only on escalation or completion.

## Start
python dashboard.py          # primary — full-screen TUI that owns the daemon
python bellows.py             # headless daemon (no TUI)

## Logs
Per-run JSON output lives in logs/. Run history in bellows.db.

## Config
Edit config.json to add watched project paths and Pushover credentials.

## Status
python status.py

## Knowledge Base
Plans for Bellows itself live in knowledge/decisions/.

## Claude Code upgrade cadence (manual)

`DISABLE_AUTOUPDATER=1` is set inside `bellows.py` and `runner.py` via
`os.environ.setdefault` so every `claude -p` subprocess inherits it.
This prevents background upgrades from breaking prompt-cache continuity
mid-plan — a new Claude Code version changes system-prompt or tool
definitions, forcing a full cache rebuild on the next invocation.

To upgrade manually:
1. `claude --version` — check current version.
2. `npm install -g @anthropic-ai/claude-code` — install latest.
3. Restart the Bellows daemon so the new binary is picked up.

Recommended cadence: at session-wrap or weekly.
Rationale: BACKLOG entry "Set DISABLE_AUTOUPDATER=1 in the Bellows daemon environment".

## Multi-machine id ranges (CEO ruling 2026-08-26 — option b)

Every machine mints plan ids from ITS OWN `lifecycle.db` `id_sequence`, and
every post-claim artifact (verdict files, `Done/executable-<id>.md`, step
logs) is keyed by that id in SHARED git namespaces. Two machines minting
from overlapping ranges WILL collide — measured 2026-08-26: the mini's ids
1/2 overwrote the shop's historic `processed-verdict-1/2` files.

**The law:** each machine's `id_sequence` is seeded ONCE into a disjoint
100000-block. Shop machine: 1–99999 (historical, continues in place).
Mac mini: 100000–199999 (seed: `UPDATE id_sequence SET next_id = 100000;`
on ITS database, daemon stopped or between claims). Each next machine takes
the next block; allocation is recorded in the tuyere machine registry once
it ships. NEVER re-seed a machine that has already minted in its block, and
never seed into another machine's block — the seeding is one-time, per
machine, on that machine.

The claim rename and all downstream naming are UNCHANGED by this law —
disjoint ranges make collisions arithmetically impossible without touching
code. Definition: the central `GLOSSARY.md` `id-range partitioning` entry.
