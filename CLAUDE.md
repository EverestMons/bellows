# Bellows
Bellows is the autonomous execution engine for Eluvian. It runs plans deposited by the Planner via claude -p, feeds step output to the Planner API for judgment, and notifies the CEO via Pushover only on escalation or completion.

## Start
python bellows.py

## Logs
Per-run JSON output lives in logs/. Run history in bellows.db.

## Config
Edit config.json to add watched project paths and Pushover credentials.

## Knowledge Base
Plans for Bellows itself live in knowledge/decisions/.
