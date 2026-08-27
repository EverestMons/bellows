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

## Cross-machine claim lock (fork 1)

The `plan_claim_lock` key in `config.json` controls the global claim shim.
Values: `off` (default), `advisory`, `required`. An absent or `off` key
produces BYTE-IDENTICAL claim-path behavior — no subprocess, partition
safety governs. An unrecognized value is treated as `required` with a
warning (fail toward safety).

| mode | claim seam | error handling | decline handling |
|------|-----------|----------------|------------------|
| `off` | no subprocess | n/a | n/a |
| `advisory` | subprocess runs | proceed with loud ADVISORY-ERROR | AUTHORITATIVE — stop, never proceed |
| `required` | subprocess runs | blocked — stop | AUTHORITATIVE — stop, never proceed |

**Activation runbook (order is load-bearing):**
1. Populate `eligible_classes` in the machine's tuyere `config.json` from the
   class universe `{read-only, shop-infra, register-writing, app-feature}`.
   An omitted class means that machine declines every plan of that class.
2. ONLY THEN set `plan_claim_lock` to `advisory` (stages 1-2) or `required`
   (stage 3+) in this machine's bellows `config.json`.
   Misorder symptom: mode-before-classes makes every deposit on that machine
   decline exit 4 and nothing dispatches.

**Seam path resolution** (named twin of `wrap_check._tuyere_checkout`):
resolution order is `$ELUVIAN_WRAP_TUYERE`, `~/Developer/tuyere`,
`ROOT/tuyere` where ROOT = `$ELUVIAN_WRAP_ROOT` else the literal
`/Users/marklehn/Developer/GitHub`. First candidate whose
`.venv/bin/python` exists wins.

**R4a claim lifecycle:** claim (in the claim block, after clearance re-check,
before mint) -> run -> completion-release (at every terminal transition).
Down-sweep and manual release are failure lanes. Park keeps the claim (it
auto-resumes). The outer `except` in `run_plan` deliberately holds — an
exception is not a clean disposition and the claim stays for manual
recovery.

**Self-strand recovery:** a claim stranded on an UP machine (crash inside the
claim-mint-rename window, seam timeout after the CLI committed, or
`run_plan`'s outer exception which holds by design) declines as held on
retry. Recovery: `tuyere.claims release <slug> --reason self-strand`.
Every exit-3 decline log carries this hint. Auto-self-heal is deliberately
deferred. R4a's down-only narrowing supersedes the census's stale-release
assumption for this window.

**Stage-3 widen gate:** before ANY `watched_projects` widening, EVERY machine
watching the shared directory must be `required`. The unsafe matrix cells
are all mixed-topology — an off- or advisory-errored machine beside a
shared directory is the double-dispatch channel.

Rulings: `tuyere/knowledge/research/fork1-claim-lock-rulings-2026-08-26.md`.
