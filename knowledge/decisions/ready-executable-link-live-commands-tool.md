# bellows — executable: `tools/link_live_commands.py` — the R-F1 symlink act mechanized for any machine (the mini runs one command)

**Date:** 2026-08-25 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** bellows suite | **Execution:** Step 1 (DEV) → Step 2 (QA) | **Priority:** 2

**auto_close:** false
**pause_for_verdict:** always
**qa_steps:** 2

**Depends on:** ruling R-F1 (`governance/knowledge/research/eluvian-follow-up-rulings-2026-08-25.md`) — executed by hand on the shop machine 2026-08-25; the mini still owes the act, and a prose instruction in a baton is exactly the class this shop retires into tools (the 524 precedent verbatim: when an act's correctness lives in operator memory, mechanize the act). **The mini cannot be reached from this machine (measured: no mini session in the agent roster); the tool travels via the repo the mini already pulls.**

## Why this exists

The R-F1 act on a second machine is five memory-reliant decisions (which files, which vendored targets, backup naming, link direction, verification) performed on a machine whose layout differs from the one the instruction was written on. The tool derives everything from its own location, is idempotent, refuses ambiguity, and self-verifies — the mini's next session (or any future machine) runs `python3 tools/link_live_commands.py` and reads the result.

## What this plan does NOT do

- **It does not touch this machine's `~/.claude`** — the shop's links exist and the tool's idempotent arm will simply report OK when someone runs it here; the DISPATCHED AGENT NEVER RUNS THE TOOL AGAINST THE REAL HOME (the sandbox denies `~/.claude` anyway, measured on 520) — tests use the override flags exclusively.
- **Only `tools/link_live_commands.py` + `tests/test_link_live_commands.py` are written.**

## Numbers discipline

⚠️ **Measured 2026-08-25; re-derive — yours supersede.**

| id | pin | value | probe |
|---|---|---|---|
| L1 | the vendored files | `hooks/commands/wrap.md` (5597 B) and `hooks/commands/eluvian.md` (978 B), both tracked | ls in your worktree; the tool resolves them relative to ITSELF, never a hardcoded root |
| L2 | the shop's live state (the idempotent arm's real case) | both `~/.claude/commands/{wrap.md,eluvian.md}` are symlinks to the shop checkout's vendored files, backups `.pre-symlink` beside them | context only — the agent does NOT probe `~/.claude` |
| L3 | the sandbox law | daemon-dispatched agents CANNOT read or write `~/.claude` (measured, plan 520) | every test uses `--commands-dir` pointing at a tmp dir |
| L4 | suite floor | **1445 collected** | `--collect-only -q`; re-derive |
| L5 | the house tool grammar | stdlib-only, argparse, refusals exit 1, self-verify prints the consumer-checkable result (the issue_verdict.py precedent) | read tools/issue_verdict.py for the shape |

## MUST-PRESERVE

- ⚠️ **THE GREP SHIM IS BROKEN: `/usr/bin/grep` for probes; zero-match exits 1, never &&-chain.**
- ⚠️ **STDLIB ONLY in the tool** (argparse, os, sys, pathlib, filecmp/shutil). No daemon-module imports.
- ⚠️ **The tool NEVER deletes content:** a plain file is BACKED UP before linking (`<name>.pre-symlink`; if that backup already exists, a timestamped variant — never overwrite a backup); a symlink pointing anywhere OTHER than the vendored target is a REFUSAL (report both paths, exit 1, touch nothing).
- ⚠️ **Fence:** `git diff HEAD~1 --stat` at QA == exactly the two new files.
- ⚠️ **Worktree dispatch; deposit paths project-relative.**

## STEP 1 — DEV: the tool and its tests

**Role:** DEV.

**T1 — `tools/link_live_commands.py`:**
- Derives the vendored dir as `Path(__file__).resolve().parent.parent / "hooks" / "commands"` — machine-independent by construction.
- Default targets: the two names `wrap.md`, `eluvian.md`; default commands dir `Path.home() / ".claude" / "commands"`; `--commands-dir DIR` override (tests; also lets a future layout differ); `--vendored-dir DIR` override (tests ONLY — the default derivation from the tool's own location is the production law; the override exists so test 6 can present a checkout missing a vendored file without module-copy gymnastics); `--dry-run` prints the per-file plan without acting.
- Per file, exactly four arms: **(a)** target is a symlink resolving to the vendored file → `OK (already linked)`; **(b)** target is a symlink resolving ELSEWHERE → refuse, print both resolutions, exit 1, act on nothing further; **(c)** target is a plain file → back up (the MUST-PRESERVE naming), then symlink to the vendored file; **(d)** target absent → symlink. Missing commands DIR → create it (`parents=True`) — a fresh machine's first run.
- Self-verify: after acting, every target must be a symlink whose resolved path equals the vendored file AND whose bytes equal the vendored bytes (read through the link); print one line per file (`LINKED`/`OK`/`REFUSED` + paths); exit 0 only when all targets verify.
- The vendored file MISSING (a stale checkout) → refuse before any action, naming the missing path and the fix (`git pull`).

**T2 — `tests/test_link_live_commands.py`** (all via `--commands-dir` on tmp dirs; import the tool as a module and drive its main/helpers):
1. fresh dir (absent targets) → both linked, exit 0, byte-equality holds
2. idempotent second run → both `OK`, exit 0, no new backups
3. plain files present → backed up as `.pre-symlink`, linked, originals' bytes preserved in the backups
4. backup-collision → timestamped variant created, prior backup untouched
5. foreign symlink → refusal exit 1, nothing modified (assert the link still points at the foreign target)
6. missing vendored file (via `--vendored-dir` pointing at a tmp dir lacking one) → refusal before action
7. dry-run → prints the plan, filesystem untouched
8. missing commands dir → created, linked

Targeted DEV run: the new test file only.

**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/tools/link_live_commands.py`
- `/Users/marklehn/Developer/GitHub/bellows/tests/test_link_live_commands.py`

**Scope:**
- `/Users/marklehn/Developer/GitHub/bellows/tools/link_live_commands.py`
- `/Users/marklehn/Developer/GitHub/bellows/tests/test_link_live_commands.py`

**Commit:** `git add tools/link_live_commands.py tests/test_link_live_commands.py && git commit -m "[<id>] tools: link_live_commands — the R-F1 symlink act mechanized (idempotent, backup-first, self-verifying)"` in YOUR worktree cwd.

## STEP 2 — QA: full suite + a tmp-dir end-to-end rehearsal

**Role:** QA.

**Q1 — full suite.** `python3 -m pytest tests/ -q` from the repo root; RAW output to `knowledge/qa/evidence/link-live-commands/pytest_full.txt`; accounting vs L4; zero failures.
**Q2 — end-to-end rehearsal (tmp only).** In a tmp commands dir seeded with PLAIN copies of both vendored files (the mini's exact current state): run the real CLI once (arms c) → verify links + backups; run twice (arm a) → OK idempotent; then the foreign-symlink refusal. Raw transcript in the report. ⚠️ NEVER against the real `~/.claude`.
**Q3 — fence + report.** Diff-stat == the two files; `knowledge/qa/evidence/link-live-commands/qa-report.md` with Q1-Q2 and the per-arm coverage row — **write any ❌ or failure-marker mention in backticks per the 532 report discipline.**

> **QA SELF-CHECK — Rule 20.** Post the block from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` verbatim, under the banner **`Rule 20 — QA Self-Check Results`**, and close with **`PASSED — SELF-CHECK PASSED`** only if every check genuinely passed. ⚠️ Both literals are matched by `plan_lint` check (c) and neither may be paraphrased. Rule 20 block + Q results in the `.md`; raw suite output in `pytest_full.txt` — the two QA gates scan DIFFERENT extensions.

**Deposits:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/link-live-commands/pytest_full.txt`
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/link-live-commands/qa-report.md`

**Scope:**
- `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/link-live-commands/`

**Commit:** `git add knowledge/qa/evidence/link-live-commands/ && git commit -m "[<id>] qa: link_live_commands — full suite + tmp rehearsal"` in YOUR worktree cwd.

## Drafting Cycle
**Tier:** T1 computed — a new standalone stdlib tool, zero daemon-code edits; panel not convened with reasoning (the tool touches nothing live from the lane; its only risky arm — clobbering a live file — is structurally forbidden by the backup-first law and tested in both directions).
**Walk register:** `governance/knowledge/research/walk-register-executable-link-commands.md`
**Walks:** walk 0 pinned; **walks 1–2 complete** — five lenses each; walk 1 folded 1 (the unwritable test 6 → the --vendored-dir test-only override), walk 2 dry across all five lenses.
**Direction verdict (after walk 1): PROCEED.** Tested, not judged.
- Weak spots:          w1 dry; w2 dry
- Destruction:         w1 dry; w2 dry
- Vulnerabilities:     w1 1 folded — instruction 1 / record 0; w2 dry
- Integration-record:  w1 dry; w2 dry — close obligations discharged at this freeze
- ACID:                w1 dry; w2 dry
**Conformance (§5):** recorded at the freeze from actual runs: walk_register_lint CONFORMANT (verdict channel, branched-on); cycle_check BAR_MET post-finalization (verdict channel, branched-on); plan_lint 0 FAIL at the scratch-mirror path.
**Closing:** **walk 2 met the bar — all five lenses dry.** Instruction series **1 → 0**. Receipt BEFORE staging (structural) → shop-infra hold → release under the CEO's directive → claim.

## Cycle Manifest
tier: T1
target: tools/link_live_commands.py
class: shop-infra
reads: /Users/marklehn/Developer/GitHub/bellows/hooks/commands/wrap.md, /Users/marklehn/Developer/GitHub/bellows/hooks/commands/eluvian.md, /Users/marklehn/Developer/GitHub/bellows/tools/issue_verdict.py, /Users/marklehn/Developer/GitHub/governance/knowledge/research/eluvian-follow-up-rulings-2026-08-25.md
writes: tools/link_live_commands.py, tests/test_link_live_commands.py, knowledge/qa/evidence/link-live-commands/pytest_full.txt, knowledge/qa/evidence/link-live-commands/qa-report.md
open_forks: none — R-F1 is ruled; this mechanizes its second-machine half
walks: 2
yields: 1, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=N/A
coherence: N/A

## Rule 20 — QA Self-Check Block

Step 2 is the QA step; the block is posted there per its mandate. Step 1 is DEV-only.
