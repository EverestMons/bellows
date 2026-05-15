# Bellows — Scaffold
**Date:** 2026-04-13 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA)
**Priority:** 1

## How to Run This Plan

```
Read the plan at bellows/knowledge/decisions/executable-scaffold-2026-04-13.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation before proceeding to Step 2.
```

---
---

## STEP 1 — DEV

---

> **FIRST — claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-scaffold-2026-04-13.md", "bellows/knowledge/decisions/in-progress-executable-scaffold-2026-04-13.md")`. Skip specialist file and glossary reads — this is a pure scaffolding task. Working directory is `/Users/marklehn/Desktop/GitHub/bellows/`. **Git init:** `git init && git --no-pager branch -m main`. **Create knowledge folder structure** via Python: `os.makedirs` for `knowledge/decisions/Done`, `knowledge/architecture`, `knowledge/development`, `knowledge/qa`, `knowledge/research`. **Create `requirements.txt`** with contents: `anthropic`, `watchdog`, `flask`, `requests`. **Create stub Python files** — each file gets a module docstring and a `# TODO` placeholder, nothing else: `bellows.py` ("Entry point. Initializes watcher and starts the orchestration loop."), `runner.py` ("Executes plan steps via claude -p. Manages session IDs."), `parser.py` ("Parses claude -p JSON output. Extracts Output Receipt status and escalation signals."), `planner.py` ("Calls Planner API with context envelope. Returns continue/rewrite/escalate decision."), `notifier.py` ("Pushover push and Flask callback server for CEO escalation responses."). **Create `config.json`** with structure: `{"watched_projects": [], "default_model": "claude-sonnet-4-6", "planner_model": "claude-haiku-4-5-20251001", "pushover": {"app_key": "", "user_key": ""}, "callback_port": 5000}`. **Create `bellows.db`** via Python sqlite3: single table `runs` with columns `id INTEGER PRIMARY KEY`, `plan_path TEXT`, `project TEXT`, `session_id TEXT`, `step INTEGER`, `status TEXT`, `cost_usd REAL`, `started_at TEXT`, `completed_at TEXT`. **Create `CLAUDE.md`** with contents: `# Bellows\nBellows is the autonomous execution engine for Eluvian. It runs plans deposited by the Planner via claude -p, feeds step output to the Planner API for judgment, and notifies the CEO via Pushover only on escalation or completion.\n\n## Start\npython bellows.py\n\n## Logs\nPer-run JSON output lives in logs/. Run history in bellows.db.\n\n## Config\nEdit config.json to add watched project paths and Pushover credentials.\n\n## Knowledge Base\nPlans for Bellows itself live in knowledge/decisions/.`. **Create `PROJECT_STATUS.md`** with contents: `# Bellows — Project Status\n**Last Updated:** 2026-04-13\n\n## Status: Scaffolding\n\n## Completed\n- 2026-04-13: Repo scaffolded. Stub files created. Knowledge structure initialized.\n\n## In Progress\n- Phase 1 build: orchestrator, runner, parser, planner, notifier\n\n## Blocked\n- None`. **Create `.gitignore`** with: `bellows.db\n*.db-shm\n*.db-wal\nlogs/\n.DS_Store\n__pycache__/\n*.pyc\n.venv/`. **Git add and commit:** `git add . && git commit -m "chore: scaffold bellows repo"`. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — QA

---

> Before starting, verify Step 1 committed via `git --no-pager log --oneline -3`. Skip specialist file and glossary reads — mechanical verification only. Verify every item in this table exists on disk: `| Item | Path | Status (✅/❌) |` — `bellows.py`, `runner.py`, `parser.py`, `planner.py`, `notifier.py`, `config.json`, `requirements.txt`, `CLAUDE.md`, `PROJECT_STATUS.md`, `.gitignore`, `knowledge/decisions/Done/` (directory), `knowledge/architecture/` (directory), `knowledge/development/` (directory), `knowledge/qa/` (directory), `knowledge/research/` (directory). Also verify `config.json` is valid JSON (`python3 -c "import json; json.load(open('config.json'))"`) and `bellows.db` has the `runs` table (`python3 -c "import sqlite3; c=sqlite3.connect('bellows.db'); print(c.execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall())"`). Write verification output to `bellows/knowledge/qa/evidence/scaffold/verify.txt` via Python file I/O. Deposit QA report to `bellows/knowledge/qa/scaffold-qa-2026-04-13.md`. **Final:** Update `bellows/PROJECT_STATUS.md` — add entry: "2026-04-13: Scaffold QA passed." Move plan to Done: `import shutil; shutil.move("bellows/knowledge/decisions/in-progress-executable-scaffold-2026-04-13.md", "bellows/knowledge/decisions/Done/executable-scaffold-2026-04-13.md")`. Commit: `chore: QA report — scaffold`. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
