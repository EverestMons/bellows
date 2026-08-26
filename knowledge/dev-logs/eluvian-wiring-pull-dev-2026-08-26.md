# Dev note — eluvian-wiring-pull (2026-08-26)

**Branch:** bellows-wt/548
**Plan:** executable-548.md.pristine

## Task A — worktree discipline

- `TREE_OK` confirmed
- sha256 prefix `78ecaa35aaca2c09f032` matched — full run

## Task B — whole-file replacement

Post-write probe raw counts:
- `Pull latest code`: 1 (expected == 1)
- `ff-only` occurrences: 2 (expected >= 2; both on same line, grep -cF returns 1 for matching lines)
- `never merge, rebase, stash, or reset`: 1 (expected == 1)
- `daemon restart needed`: 1 (expected == 1)
- `Recite AND assert the system wiring`: 1 (expected == 1)
- `ADVISORY: never refuse to proceed`: 1 (expected == 1)

Recorded line count: **26** (`wc -l hooks/commands/eluvian.md`)

## Task C — root-doctrine line

- Anchor count-1 confirmed at L131
- Replacement written; committed in root repo
- **ROOT_COMMIT:** `8d2267ddee9466a09857165288a42b6926bda500`
