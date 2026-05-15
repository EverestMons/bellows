# bellows — Gate 5 Path Resolution Fix (Double Project Name)
**Date:** 2026-04-17 | **Type:** Executable | **Priority:** 1

## How to Run This Plan

**Bootstrap:** `Read the plan at bellows/knowledge/decisions/executable-gate5-path-double-project-2026-04-17.md. Execute it fully. Deposit your development log and report Complete when done.`

## Context

Gate 5 `_gate_deposit_exists` joins deposit paths with `project_path` using `os.path.join(project_path, path)`. But plan deposit instructions use project-prefixed paths like `invoice-pulse/knowledge/development/foo.md`. When joined with `project_path` (`/Users/marklehn/Desktop/GitHub/invoice-pulse`), the result is `/invoice-pulse/invoice-pulse/knowledge/...` — double project name, always returns False. This caused every deposit gate check this session to fail even when files existed on disk. Verified: `os.path.join(project_path, "knowledge/development/foo.md")` resolves correctly; `os.path.join(project_path, "invoice-pulse/knowledge/development/foo.md")` does not.

---

## STEP 1 — DEV

---

> **FIRST — claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-gate5-path-double-project-2026-04-17.md", "bellows/knowledge/decisions/in-progress-executable-gate5-path-double-project-2026-04-17.md")`. Read `bellows/gates.py`, specifically `_gate_deposit_exists`. **Single commit.** Fix the path resolution to try multiple strategies. In `_gate_deposit_exists`, when checking if a deposit file exists, try paths in this order and return True (no failure) on the first hit: (1) `os.path.isfile(path)` — handles absolute paths, (2) `os.path.isfile(os.path.join(project_path, path))` — handles paths relative to project root without project name prefix (e.g. `knowledge/development/foo.md`), (3) `os.path.isfile(os.path.join(os.path.dirname(project_path), path))` — handles paths that include the project directory name (e.g. `invoice-pulse/knowledge/development/foo.md`). Also apply the same multi-strategy resolution to the plan-aware deposit extraction (the regex-matched paths from plan text). These paths come with backtick quoting already stripped but may include the project directory prefix. The fix should be a helper function like `_resolve_deposit_path(path, project_path)` that returns True if the file exists at any of the three resolution strategies, used by both the agent-declared and plan-required deposit checks. Commit: `fix: gate 5 path resolution — handle project-prefixed deposit paths`. **Deposit dev log** to `bellows/knowledge/development/gate5-path-double-project-2026-04-17.md` using canonical Python file write. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed further. Wait for CEO confirmation.**
