# bellows — executable: /eluvian gains pull-latest + the system wiring map; ELUVIAN_PATH L131 re-pointed

**Date:** 2026-08-26 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** none (doc-only; the command file is prose an agent executes — no code path) | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always

**auto_close:** false

**Depends on:** the CEO's directive this session ("we should make sure that /eluvian carries the proper wiring for how these systems work together. It's also worthwhile that this command pulls any new code for any of the systems so that no matter that machine, the most recent version is being used"); plans 542–547 (Done — the central-glossary state the wiring map describes is LIVE); the 542 D-3 finding (ELUVIAN_PATH L131 still states the superseded R-F2 routing — folded HERE because the wiring the command recites must not contradict the doctrine it reads in step 2).

## Why this exists

`/eluvian` is the multi-machine alignment pass, but today it neither refreshes code (a second machine runs stale bellows/doctrine until someone pulls by hand) nor states how the systems interlock. This plan adds a safe pull step (fetch + ff-only inside a strict envelope), a wiring map that is both recited and mechanically asserted, and fixes the one root-doctrine line that still contradicts the central-glossary ruling.

## What this plan does NOT do

- It does not touch the daemon, hooks code, wrap.md, or any `.py` — the command file is prose. It never auto-merges, auto-rebases, or auto-restarts anything; the pull envelope is ff-only-or-report.

## Numbers discipline

⚠️ **Measured 2026-08-26 at authoring; Step 1 re-derives — yours supersede.**

| id | pin | value | anchor |
|---|---|---|---|
| S1 | eluvian.md | 15 lines; sha256 prefix `78ecaa35aaca2c09f032` (pre-write guard for the whole-file replacement) | `hooks/commands/eluvian.md` (repo-relative — worktree law) |
| S2 | L131 anchor | the R-F2 line count-1 (quoted in Task C) | `/Users/marklehn/Developer/GitHub/ELUVIAN_PATH.md` (root, 175 lines) |
| S3 | repo census | 10 direct-child repos with origin remotes + root + memory repo (informational — the command ENUMERATES dynamically, never a hand list) | measured at authoring |

## STEP 1 — DEV (rewrite the command, then the doctrine line)

> **Task A — worktree discipline + state branch.** ⚠️ **Your cwd IS the claimed tree (bellows dispatches into a WORKTREE) — never cd to `/Users/marklehn/Developer/GitHub/bellows`.** Open: `cd "$(git rev-parse --show-toplevel)" && test -f hooks/commands/eluvian.md && echo TREE_OK` — HALT unless TREE_OK. Bellows paths RELATIVE; the ONLY absolute paths are the root doctrine file and root-repo commit in Task C. Probe: (i) `shasum -a 256 hooks/commands/eluvian.md` — prefix `78ecaa35aaca2c09f032` → full run; prefix differs AND `/usr/bin/grep -cF -- "Pull latest code" hooks/commands/eluvian.md; true` == 1 → W1 already landed, resume at Task C; differs otherwise → HALT with the sha.
>
> **Task B — whole-file replacement of `hooks/commands/eluvian.md`** (python, RELATIVE path; pre-write assert: the file's sha256 still matches S1 — SystemExit on mismatch, no write) with EXACTLY:
>
> ````
> ---
> description: Align the session with the Eluvian path — pull latest code, assert environment, recite + assert the system wiring, surface parked arcs
> ---
>
> # Eluvian alignment pass
>
> 1. **Pull latest code (multi-machine law: every machine runs the newest committed state).** Enumerate the repos DYNAMICALLY — never a hand list: the root `/Users/marklehn/Developer/GitHub`, every direct child directory with a `.git` and an `origin` remote, and the memory repo at `/Users/marklehn/.claude/projects/-Users-marklehn-Developer-GitHub/memory`. For each: `GIT_TERMINAL_PROMPT=0 git fetch origin` (a fetch failure is a LOUD warning, not a stop); report ahead/behind vs upstream; if BEHIND and not diverged → `GIT_TERMINAL_PROMPT=0 git pull --ff-only`; if DIVERGED, or the ff-only pull refuses, or the tree blocks it → report loudly and TOUCH NOTHING — never merge, rebase, stash, or reset on the command's behalf. ⚠️ If the bellows repo received new commits, compare the RUNNING daemon's sha (from `python3 bellows/status.py`) to the new HEAD and, when they differ, report **"bellows daemon restart needed — running old code"**: a live daemon keeps executing the code it loaded at start.
>
> 2. **Read the doctrine.** Load `/Users/marklehn/Developer/GitHub/ELUVIAN_PATH.md` in full. This is the governing process document.
>
> 3. **Assert the environment:**
>    - **cwd** is `/Users/marklehn/Developer/GitHub` (the governance root)
>    - **bellows daemon** is RUNNING — verify with `python3 bellows/status.py`
>    - **wrap debt** — run `python3 bellows/hooks/eluvian/wrap_check.py` READ-ONLY (report its output, arm nothing)
>    - **parked arcs** — report every line containing `⏸`, `PARKED`, or `RESUME AT` from the head of `shop_next_session.md`
>
> 4. **Recite AND assert the system wiring** (the map goes in the report so every machine's session starts from the same picture; each assert is a real check, not a recollection):
>    - **Root doctrine:** `ELUVIAN_PATH.md` (governing process), `PLANNER_TEMPLATE.md` (Planner law), `DRAFTING_CYCLE.md` (drafting-cycle law), `GLOSSARY.md` (the ONE central domain glossary — entries tagged `[project: <name>]`, proposals 378 + 389; per-repo glossary files are POINTERS, never scaffold or write them), `LESSONS.md` (the shop lesson corpus — APPEND-ONLY, forge-ingested).
>    - **bellows/** — the autonomous execution engine. Plans deposit as `ready-` files in each project's `knowledge/decisions/`; lifecycle: deposit receipt → clearance → daemon claim (id minted from `lifecycle.db`) → step gates → Planner verdicts via `tools/issue_verdict.py` → Done. The live `/wrap` and `/eluvian` commands are symlinks into `bellows/hooks/commands/`.
>    - **lessons-forge/** — the lesson pipeline: ingests `LESSONS.md` into proposals; Gate 1 routes them (the non-author law, exec-459); Gate 2 codifies accepted rows into doctrine; `lessons-forge.db` is local operational state (untracked by policy).
>    - **governance/** — shop-level plans and knowledge; it has NO own `.git` (its history lives in the root repo) and dispatches in place with absolute operands.
>    - **memory repo** — Planner-personal working patterns; on a path to hardcoding — systems must not RELY on it.
>    - **Projects** (anvil, invoice-pulse, freight-kb, …) — own repos, own `knowledge/decisions/` lanes; their DOMAIN knowledge lives in the central `GLOSSARY.md` under their project tag.
>    Mechanical asserts (report each): `GLOSSARY.md` exists at the root; `bellows/lifecycle.db` exists; `lessons-forge/lessons-forge.db` exists.
>
> 5. **Report alignment or misalignment loudly.** State each check's result. If any check fails, state the failure clearly as a warning. **ADVISORY: never refuse to proceed** — a failed assert (including a failed fetch or a refused pull) reports but does not block (fork 3 ruling). Say so in the report.
> ````
>
> Post-write probes (all repo-relative): `/usr/bin/grep -cF -- "Pull latest code" hooks/commands/eluvian.md` == 1 AND `"ff-only"` count >= 2 AND `"never merge, rebase, stash, or reset"` == 1 AND `"daemon restart needed"` == 1 AND `"Recite AND assert the system wiring"` == 1 AND `"ADVISORY: never refuse to proceed"` == 1. MEASURE and RECORD `wc -l hooks/commands/eluvian.md` in the dev note.
>
> **Task C — the root-doctrine line (in place, absolute, root repo).** FIRST the already-done branch (a death between C and D leaves root committed while bellows re-runs fresh): if the anchor below counts 0 AND `/usr/bin/grep -cF -- "Domain knowledge deposited in the CENTRAL glossary" /Users/marklehn/Developer/GitHub/ELUVIAN_PATH.md` == 1 → the root edit already landed: recover **ROOT_COMMIT** = `git -C /Users/marklehn/Developer/GitHub log -1 --format=%H -- ELUVIAN_PATH.md` and continue to Task D. Otherwise replace in `/Users/marklehn/Developer/GitHub/ELUVIAN_PATH.md` the anchor (count-1 asserted, EXACT bytes):
>
> ```
> - Domain knowledge deposited in project's `knowledge/glossary.md` (R2 glossaries live since E5 — scaffold-on-first-use)
> ```
>
> with:
>
> ```
> - Domain knowledge deposited in the CENTRAL glossary `/Users/marklehn/Developer/GitHub/GLOSSARY.md` under `[project: <name>]` tags (proposals 378 + 389, PT v4.93, plans 542–547; the per-repo glossary files are POINTERS — never scaffold them)
> ```
>
> Then commit in the ROOT repo (cd-absolute, pinned, pathspec-limited): `cd /Users/marklehn/Developer/GitHub && git rev-parse --show-toplevel && git add ELUVIAN_PATH.md && git commit -m "docs: ELUVIAN_PATH wrap-artifacts line re-pointed at the central glossary (542 D-3 discharge)" -- ELUVIAN_PATH.md && git rev-parse HEAD` — the hash is **ROOT_COMMIT**.
>
> **Task D — dev note + bellows commit.** Write `knowledge/dev-logs/eluvian-wiring-pull-dev-2026-08-26.md` (branch taken, post-write probe raw counts, recorded `wc -l`, ROOT_COMMIT). Commit (WORKTREE toplevel): `cd "$(git rev-parse --show-toplevel)" && git add hooks/commands/eluvian.md knowledge/dev-logs/eluvian-wiring-pull-dev-2026-08-26.md && git commit -m "[<id from your plan filename>] eluvian-wiring-pull(eluvian-wiring-pull-2026-08-26): /eluvian gains pull-latest (ff-only envelope) + wiring map (recite+assert)" -- hooks/commands/eluvian.md knowledge/dev-logs/eluvian-wiring-pull-dev-2026-08-26.md && git rev-parse HEAD` — **CAPTURE_COMMIT**; separate: `git show <CAPTURE_COMMIT> --numstat --format=` — exactly the two files.
>
> **Deposits:**
> - `hooks/commands/eluvian.md`
> - `knowledge/dev-logs/eluvian-wiring-pull-dev-2026-08-26.md`
>
> **Scope:**
> - `hooks/commands/eluvian.md`
> - `knowledge/dev-logs/eluvian-wiring-pull-dev-2026-08-26.md`

## STEP 2 — QA (verify against the COMMITTED state, BOTH repos)

> **Item 1 — bellows extraction probes.** `cd "$(git rev-parse --show-toplevel)"`; `git show <CAPTURE_COMMIT>:hooks/commands/eluvian.md` to `/private/tmp/` scratch; the six Task-B probes re-run on the extraction at their stated counts, PLUS `wc -l` EQUALS the dev note's recorded value; `cmp` extraction vs live → 0. Raw → `knowledge/qa/evidence/eluvian-wiring-pull-2026-08-26/probes-raw.txt`.
> **Item 2 — root extraction probes.** `git -C /Users/marklehn/Developer/GitHub show <ROOT_COMMIT>:ELUVIAN_PATH.md` to scratch: `"Domain knowledge deposited in the CENTRAL glossary"` == 1 AND `"scaffold-on-first-use"` == 0 AND `"R2 glossaries live since E5"` == 0; `cmp` vs the live file → 0.
> **Item 3 — safety-envelope negative probes (the command must NEVER instruct an unsafe git verb).** On the eluvian.md extraction: `"git merge"` == 0 AND `"git rebase"` == 0 AND `"git reset"` == 0 AND `"git stash"` == 0 (the prose forbids them by name inside the "never merge, rebase, stash, or reset" sentence — that sentence contains NONE of these two-word git-verb literals, so all four probes expect 0; positive control: `"git pull --ff-only"` >= 1 AND `"git fetch origin"` >= 1).
> **Item 4 — commit hygiene.** Both numstats (bellows: exactly 2 files; root: exactly 1 file); both toplevels; reflog `-n 4` each → 0 amends.
> **Item 5 — receipt** `knowledge/qa/evidence/eluvian-wiring-pull-2026-08-26/qa-receipt.md`: per-item table, then the Rule 20 block.
>
> ⚠️ **Gate note (pre-declared):** probe-battery QA, NO pytest scope. `qa_test_result` will report "no parseable pytest summary" — the known-benign class (12th precedent); the Planner overrides with reference to this clause and the evidence.
>
> **Deposits:**
> - `knowledge/qa/evidence/eluvian-wiring-pull-2026-08-26/probes-raw.txt`
> - `knowledge/qa/evidence/eluvian-wiring-pull-2026-08-26/qa-receipt.md`
>
> **Scope:**
> - `knowledge/qa/evidence/eluvian-wiring-pull-2026-08-26/probes-raw.txt`
> - `knowledge/qa/evidence/eluvian-wiring-pull-2026-08-26/qa-receipt.md`

Rule 20 banner (byte-exact, inside the QA receipt's verification section):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```

## Drafting Cycle

**Tier:** T1 — two doc edits (the live command + one doctrine line); the 543 worktree law and mixed-repo commit discipline carried. Two-walk form; direction-class escalates.

**Walk register:** `bellows/knowledge/research/walk-register-eluvian-wiring-pull-2026-08-26.md`

**Walk 0 (context pin, measured):** eluvian.md 15 lines sha-prefix `78ecaa35aaca2c09f032`; L131 anchor count-1 in the 175-line ELUVIAN_PATH.md; repo census 10 children + root + memory (informational — the command enumerates dynamically, the drift-proof-enumeration doctrine). Design notes (a)–(e): the ff-only-or-report pull envelope; the daemon-staleness warning; wiring = recite + mechanical asserts; sha-guarded whole-file replacement; the worktree law with the single root-side absolute write.

**Walks:**
- Weak spots:          w1 dry — Item 3's four negative probes verified absent from the drafted content (the forbidding sentence contains no two-word git-verb literal) with both positive controls present; the ff-only count-2 measured on the draft; the four-backtick fence wraps content with only inline backticks.
- Destruction:         w1 1 folded — a death between Tasks C and D re-runs from a FRESH worktree (uncommitted bellows work lost — the transient-death law) and reaches Task C with the L131 anchor already consumed: the count-1 assert would HALT a CORRECT state. Task C gains the already-done branch (anchor 0 + the replacement line present → recover ROOT_COMMIT from `git log -1 -- ELUVIAN_PATH.md`, continue).
- Vulnerabilities:     w1 dry — the pull envelope is ff-only-or-report (dirty/diverged/fetch-fail all land on LOUD + touch nothing); the advisory law extended to pulls explicitly; the daemon-staleness warning closes the stale-code hole the CEO's directive targets.
- Integration-record:  w1 dry — the wiring map's every claim traces to live state shipped this session (central glossary 542–547, symlinked commands R-F1, non-author law 459); L131's fix discharges 542 D-3 with the plan saying so.
- ACID:                w1 dry — two commits, two repos, each pathspec-limited and pinned; the sha-guarded whole-file replacement admits no partial state.
- **Walk 1 total: one finding, folded.**
- Weak spots:          w2 dry — the folded branch's probes each earnable; blockquote-fenced replacement follows the 543 precedent the executing agent already handled correctly.
- Destruction:         w2 dry — arms now partition fresh-worktree and same-tree re-entries.
- Vulnerabilities:     w2 dry.
- Integration-record:  w2 dry.
- ACID:                w2 dry.
- **Walk 2 total: 0 findings — all five lenses dry.**

**Closing:** ✅ **BAR MET at walk 2 — dry confirming pass, all five lenses.** T1 two-walk form; no direction-class finding; close is MANUAL (CEO-lane verdicts).

**Fold-and-deposit exactly once.**

## Cycle Manifest
tier: T1
target: bellows/hooks/commands/eluvian.md
class: shop-infra
reads: /Users/marklehn/Developer/GitHub/bellows/hooks/commands/eluvian.md, /Users/marklehn/Developer/GitHub/ELUVIAN_PATH.md
writes: hooks/commands/eluvian.md, knowledge/dev-logs/eluvian-wiring-pull-dev-2026-08-26.md, ELUVIAN_PATH.md (root, absolute, own commit), knowledge/qa/evidence/eluvian-wiring-pull-2026-08-26/probes-raw.txt, knowledge/qa/evidence/eluvian-wiring-pull-2026-08-26/qa-receipt.md
open_forks: the invoice-pulse legacy LESSONS.md bin retirement (declared follow-up, rides the wrap or its own plan); the project-tag-on-lessons ruling (awaiting the CEO); the SIX routed record errors + the 346-residue LESSONS entry (wrap-time)
walks: 2
yields: 1, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=N/A
coherence: N/A
