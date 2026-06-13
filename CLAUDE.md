# Bellows
Bellows is the autonomous execution engine for Eluvian. It runs plans deposited by the Planner via claude -p, feeds step output to the Planner API for judgment, and notifies the CEO via Pushover only on escalation or completion.

## Start
python bellows.py

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
