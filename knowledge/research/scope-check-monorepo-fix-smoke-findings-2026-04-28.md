# scope_check Monorepo Fix Post-Restart Smoke — Findings

**Date:** 2026-04-28 | **Smoke plan:** diagnostic-scope-check-monorepo-fix-smoke-2026-04-28 | **Bellows generation:** post-restart with commit 8db0adc loaded

This smoke deposits a single trivial file under bellows/knowledge/research/ and commits it. The test is whether Bellows's gate evaluation reports any out-of-project files in its `Files Changed` section. The governance-root working tree currently has dirty state in LESSONS.md (47-line pending edit) and anvil (submodule). With the new `_capture_git_diff` (`--relative -- .`), those files should be scoped out and not appear in `files_changed`. With the old code, they would appear and scope_check would trip.

Smoke run timestamp: 2026-04-29T01:34:32Z
