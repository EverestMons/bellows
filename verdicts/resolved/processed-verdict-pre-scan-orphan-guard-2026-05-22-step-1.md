verdict: stop

Stopping the step-counter loop. The plan's real work was already shipped and verified by QA Step 2 earlier today (08:48 + 09:13). DEV Step 1 commit landed at bellows.py:33 (module-level dedup set) and bellows.py:1135-1162 (orphan-check guard). QA Step 2 added 4 regression tests, ran Rule 20 PASSED, updated PROJECT_STATUS and BACKLOG. All deliverables verified directly.

Root cause of this re-dispatch: Planner-side error — Planner manually renamed in-progress-* to verdict-pending-* to unstick the original Step 2 verdict response that hadn't been consumed (root cause of that: Step 2 gate_failure path didn't rename plan to verdict-pending- as expected). The rename fired the watcher's on_moved handler which re-dispatched the plan, hitting a stale worktree from the earlier QA run, producing this step-counter loop (BACKLOG: step-counter loop after precondition-failure verdict).

Recovery actions to be performed manually by Planner/CEO after this stop verdict:
- CEO: rm -rf /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/pre-scan-orphan-guard-2026-05-22
- CEO: cd /Users/marklehn/Developer/GitHub/bellows && git worktree prune
- Planner: move plan from halted-* to Done/
- Planner: clean stranded verdict-request files (step-1 from re-dispatch loop)
- Planner: clean stranded verdict response files in resolved/ from earlier session

This is not a real "stop the plan" — the plan completed correctly. This is "stop the daemon from re-running already-shipped work."
