# Bellows — scope_check Monorepo Fix Post-Restart Smoke
**Date:** 2026-04-28 | **Tier:** Small | **Test Scope:** none | **Execution:** Step 1 (Bellows Developer)
**Priority:** 5

## Context

Validates BACKLOG #4 fix is loaded in the running Bellows daemon post-restart. The fix shipped via `executable-scope-check-monorepo-fix-2026-04-28` (commit `8db0adc`) changed `_capture_git_diff` argv to include `--relative -- .`, scoping the diff to the project subtree.

Per BACKLOG #14 ("plan fixing bug X tripped bug X during its own close"), the fix plan's QA step was evaluated by the OLD code (daemon hadn't restarted) and tripped a separate gate. CEO restarted Bellows after that plan closed. This smoke runs in the new daemon generation.

**Test mechanism:** The governance-root working tree currently has uncommitted dirty state in `LESSONS.md` (47-line pending edit) and `anvil` (submodule pointer). With the OLD `_capture_git_diff`, running `git diff --stat` from `cwd=bellows` would report both as out-of-scope files for any plan running here. With the NEW code (`--relative -- .`), those files are scoped out at the git command level and `files_changed` shouldn't contain them.

This smoke deposits a single trivial bellows/-relative file and commits. If `scope_check` evaluates clean (no LESSONS.md or anvil flagged), the fix is confirmed loaded. If `scope_check` trips on LESSONS.md or anvil, the fix is NOT loaded and the BACKLOG item must reopen.

This is a diagnostic, not an executable — the deposit IS the test artifact, not a real product change. Single-step, no QA. Planner performs Rule 22 verification on Bellows's gate evaluation output (the verdict request's `Files Changed` section is the actual signal).

Test Scope: none — no production code touched, no tests run.

## How to Run This Plan

Bellows watcher claims this plan automatically. Agent writes a single timestamped acknowledgment file under `bellows/knowledge/research/`, commits, reports completion. Per disable-auto-close, terminal step produces a verdict request. Planner reads the verdict request body's `Files Changed` field — that's the actual smoke result. Rule 22 verification on the deposit, then Done/ move.

---
---

## STEP 1 — Bellows Developer

---

> **FIRST — claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/diagnostic-scope-check-monorepo-fix-smoke-2026-04-28.md", "bellows/knowledge/decisions/in-progress-diagnostic-scope-check-monorepo-fix-smoke-2026-04-28.md")`. **Skip glossary read AND skip specialist file read — this is a trivial smoke deposit, no domain or architecture content.** All commands run from `/Users/marklehn/Desktop/GitHub/`. **Task:** Use `Filesystem:write_file` to create a single file at `bellows/knowledge/research/scope-check-monorepo-fix-smoke-findings-2026-04-28.md` containing exactly this content (verbatim, including the timestamp placeholder which you fill in with the current ISO time at write time):
>
> ```
> # scope_check Monorepo Fix Post-Restart Smoke — Findings
>
> **Date:** 2026-04-28 | **Smoke plan:** diagnostic-scope-check-monorepo-fix-smoke-2026-04-28 | **Bellows generation:** post-restart with commit 8db0adc loaded
>
> This smoke deposits a single trivial file under bellows/knowledge/research/ and commits it. The test is whether Bellows's gate evaluation reports any out-of-project files in its `Files Changed` section. The governance-root working tree currently has dirty state in LESSONS.md (47-line pending edit) and anvil (submodule). With the new `_capture_git_diff` (`--relative -- .`), those files should be scoped out and not appear in `files_changed`. With the old code, they would appear and scope_check would trip.
>
> Smoke run timestamp: <iso-timestamp-here>
> ```
>
> **Commit:** `cd /Users/marklehn/Desktop/GitHub/bellows && git add knowledge/research/scope-check-monorepo-fix-smoke-findings-2026-04-28.md && git commit -m "test: scope_check monorepo fix post-restart smoke"`. **Note for the agent:** Do NOT touch LESSONS.md, anvil, or any file outside bellows/. The whole point of the smoke is to leave that governance-root drift in place so we can observe whether scope_check ignores it. Your commit should ONLY include the one new findings file. **Standard prompt feedback protocol** → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/research/scope-check-monorepo-fix-smoke-findings-2026-04-28.md`
