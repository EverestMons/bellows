# bellows — executable: /wrap 3d → the CENTRAL glossary + `knowledge/glossary.md` retired to a pointer

**Date:** 2026-08-26 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** none (doc-only; no code path touched — the 542 DISCOVERY sweep proved no tool parses these files) | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always

**auto_close:** false

**Depends on:** plan 542 (Done 2026-08-26 — PT v4.93 + `/Users/marklehn/Developer/GitHub/GLOSSARY.md` live, byte-identical to the committed seed; the CEO's one-central-glossary ruling, proposals 378 + 389); the 542 DISCOVERY seat's mechanical-consumer sweep (bellows/hooks + tools + scripts + gates.py + forge: the ONLY "glossary" hit is `hooks/commands/wrap.md` L60–69 — the diagnostic ground for this plan); the CEO's direct go-ahead this session ("yes go ahead with the bellows follow-up plan").

## Why this exists

PT v4.93's Session Wrap doctrine routes wrap-time domain facts to the central `GLOSSARY.md` — but the `/wrap` command file itself (live via the R-F1 symlinks) still routes 3d to `<project>/knowledge/glossary.md` AND carries a create-if-missing scaffold clause that would re-create the per-repo files being retired. 542's SC-5 ordering law: re-point 3d FIRST, then pointer-ize. This plan does both, in that order, in one step.

## What this plan does NOT do

- It does not touch `lessons-forge/knowledge/glossary.md` (that repo's own follow-up plan, still owed) nor the three grandfathered legacy glossaries (their own migration plans).
- It does not write to root `GLOSSARY.md` or any root-repo file — root is READ-ONLY here (the completeness guard reads it).

## Numbers discipline

⚠️ **Measured 2026-08-26 at authoring; Step 1 re-derives — yours supersede.**

| id | pin | value | anchor |
|---|---|---|---|
| S1 | wrap.md size | `wc -c` 5852 | `/Users/marklehn/Developer/GitHub/bellows/hooks/commands/wrap.md` |
| S2 | 3d block | the ONLY "glossary" mention in wrap.md (L60–69); anchor count-1 | the 10-line block quoted in Step 1 |
| S3 | old glossary | 34 lines, exactly 10 `## ` entries | `/Users/marklehn/Developer/GitHub/bellows/knowledge/glossary.md` |
| S4 | central census | `[project: bellows]` == 10 | `/Users/marklehn/Developer/GitHub/GLOSSARY.md` (root, read-only) |

Post-edit `"glossary"` counts on wrap.md are NOT predicted here — Step 1 measures and records them in the dev note; QA compares against the RECORDED values (design note (b) in the walk register).

## STEP 1 — DEV (re-point 3d, then retire the per-repo glossary — ORDER LOAD-BEARING)

> **Task A — worktree discipline + state branch (re-entry safe, design notes (c)/(e)).** ⚠️ **Your cwd IS the claimed tree (bellows dispatches into a WORKTREE) — never cd to `/Users/marklehn/Developer/GitHub/bellows`; an absolute cd would edit the LIVE tree and defeat isolation.** Open with: `cd "$(git rev-parse --show-toplevel)" && test -f hooks/commands/wrap.md && test -f knowledge/glossary.md && echo TREE_OK` — HALT unless `TREE_OK`. ALL in-repo paths below are RELATIVE to this toplevel; the ONLY absolute path in this plan is the read-only root `GLOSSARY.md`. Then probe: (i) `/usr/bin/grep -cF -- "surface that belongs in the project's glossary?" hooks/commands/wrap.md; true`, (ii) `/usr/bin/grep -c "^## " knowledge/glossary.md; true` (⚠️ REGEX form deliberately — under `-F` the caret is a LITERAL and the count silently reads 0), (iii) `/usr/bin/grep -cF -- "RETIRED" knowledge/glossary.md; true`, (iv) `/usr/bin/grep -cF -- "Do not add entries here" knowledge/glossary.md; true`.
> - (i)=1 AND (iii)=0 → FULL RUN (Task B then C).
> - (i)=0 AND (ii)=10 AND (iii)=0 → W1 already landed, resume at Task C.
> - (i)=0 AND (iii)=1 AND (ii)=0 AND (iv)=1 → both edits landed INTACT; skip to Task D (commit-check only).
> - Any other combination (incl. a torn pointer: (iii)>=1 with (ii)>0 or (iv)=0) → HALT and report all four values.
>
> **Task B — W1: re-point 3d (python heredoc, count-1 asserted, write-after-assert).** Replace in `hooks/commands/wrap.md` (RELATIVE — the worktree copy, per Task A) the anchor block (verbatim, 10 lines):
>
> ```
> 3d. **Domain-knowledge sweep.** Ask: "what domain knowledge did this session
>    surface that belongs in the project's glossary?" For each project touched
>    this session, review the session's work and deposit any DEFINITIONS (not
>    runbooks, not traps — per the glossary discriminator) into
>    `<project>/knowledge/glossary.md`. If the file does not exist, create it
>    with the scaffold: a `# Glossary — <project-name>` header, the discriminator
>    note (DEFINITION goes here; RUNBOOK goes in CLAUDE.md; TRAP goes into CODE),
>    and a `<!-- Entries below. Format: ## Term \n definition \n -->` comment.
>    If nothing qualifies, move on — the step is complete when the question has
>    been asked, not when an entry has been written.
> ```
>
> with:
>
> ```
> 3d. **Domain-knowledge sweep.** Ask: "what domain knowledge did this session
>    surface that belongs in the glossary?" For each project touched this
>    session, review the session's work and deposit any DEFINITIONS (not
>    runbooks, not traps — per the glossary discriminator) into the CENTRAL
>    glossary at `/Users/marklehn/Developer/GitHub/GLOSSARY.md`, each entry as
>    `## <term> [project: <name>]` (comma-separate multiple project tags; the
>    file already exists — APPEND-ONLY, non-destructive-append and
>    class-not-narrative guards apply). ⚠️ NEVER write to — and never scaffold —
>    a per-repo `knowledge/glossary.md`: the per-repo files are RETIRED to
>    pointers (proposals 378 + 389, PT v4.93, plan 542, 2026-08-26).
>    If nothing qualifies, move on — the step is complete when the question has
>    been asked, not when an entry has been written.
> ```
>
> The heredoc runs from the Task-A toplevel and opens `hooks/commands/wrap.md` RELATIVE; it asserts anchor count == 1 pre-write (SystemExit on mismatch, no write). Post-write: `/usr/bin/grep -cF -- "NEVER write to" hooks/commands/wrap.md` == 1 AND `/usr/bin/grep -cF -- "If the file does not exist, create it" hooks/commands/wrap.md; true` == 0 (the scaffold clause is GONE — this is the ordering law's teeth). MEASURE and RECORD in the dev note: `/usr/bin/grep -icF -- "glossary" hooks/commands/wrap.md` and `wc -c hooks/commands/wrap.md`.
>
> **Task C — W2: completeness-guard then pointer-ize (python heredoc, guard IN the control flow).** ONE script, run from the Task-A toplevel, that (1) parses `knowledge/glossary.md` (RELATIVE — the worktree copy) into its `## <term>` sections — asserts exactly 10 (design note (d)); (2) parses `/Users/marklehn/Developer/GitHub/GLOSSARY.md` (READ-ONLY) sections `## <term> [project: bellows]`; (3) for each of the 10 old terms: the central body must equal the old body after per-line trailing-whitespace strip and outer blank-line strip — ANY mismatch or missing term → SystemExit naming every offending term, NO write; (4) only then overwrites `knowledge/glossary.md` with the pointer:
>
> ```
> # Glossary — bellows (RETIRED → pointer)
>
> **This file is retired.** All 10 entries migrated VERBATIM to the central
> glossary at `/Users/marklehn/Developer/GitHub/GLOSSARY.md` under
> `[project: bellows]` tags (proposals 378 + 389 — the CEO's one-central-glossary
> ruling; Gate 2 route-57 consolidation, plan 542, PT v4.93, 2026-08-26).
> Do not add entries here: new bellows domain definitions go to the central
> file, tagged `[project: bellows]`. The migration-completeness proof (all 10
> bodies matched at retirement) is in this plan's dev note.
> ```
>
> Post-write: `/usr/bin/grep -cF -- "RETIRED" knowledge/glossary.md` == 1 AND `/usr/bin/grep -c "^## " knowledge/glossary.md; true` == 0 (regex form — see Task A's caret warning) AND the script's per-term `MATCH <term>` lines (10 of them) pasted into the dev note.
>
> **Task D — dev note + commit.** Write `knowledge/dev-logs/wrap-3d-central-glossary-dev-2026-08-26.md`: the state branch taken, W1 post-probes, the RECORDED post-edit counts, the 10 `MATCH` lines, `wc -c` values. Commit (ONE compound, cd-first, no amend — the WORKTREE toplevel, never the live tree): `cd "$(git rev-parse --show-toplevel)" && git add hooks/commands/wrap.md knowledge/glossary.md knowledge/dev-logs/wrap-3d-central-glossary-dev-2026-08-26.md && git commit -m "[<id from your plan filename>] wrap-3d-central-glossary(wrap-3d-central-glossary-2026-08-26): 3d -> central GLOSSARY.md; knowledge/glossary.md retired to pointer (completeness-proven)" -- hooks/commands/wrap.md knowledge/glossary.md knowledge/dev-logs/wrap-3d-central-glossary-dev-2026-08-26.md && git rev-parse HEAD`. The hash is **CAPTURE_COMMIT**; separate compound: `git show <CAPTURE_COMMIT> --numstat --format=` — expect exactly the three files (mismatch → report loudly).

> **Deposits:**
> - `hooks/commands/wrap.md`
> - `knowledge/glossary.md`
> - `knowledge/dev-logs/wrap-3d-central-glossary-dev-2026-08-26.md`
>
> **Scope:**
> - `hooks/commands/wrap.md`
> - `knowledge/glossary.md`
> - `knowledge/dev-logs/wrap-3d-central-glossary-dev-2026-08-26.md`

## STEP 2 — QA (verify against the COMMITTED state)

> **Item 1 — committed extractions.** `cd "$(git rev-parse --show-toplevel)"` (your cwd is the claimed tree — Task A's worktree law applies to QA too); extract both files via `git show <CAPTURE_COMMIT>:hooks/commands/wrap.md` and `git show <CAPTURE_COMMIT>:knowledge/glossary.md` to `/private/tmp/` scratch paths; run ALL probes below against the EXTRACTIONS (raw outputs → `knowledge/qa/evidence/wrap-3d-central-glossary-2026-08-26/probes-raw.txt`):
> - wrap.md extraction: `"NEVER write to"` == 1; `"If the file does not exist, create it"` == 0; `"surface that belongs in the project's glossary?"` == 0; `"/Users/marklehn/Developer/GitHub/GLOSSARY.md"` == 1; `"3d."` == 1; the total case-insensitive `"glossary"` count EQUALS the dev note's recorded value (read the dev note; compare — never a plan-predicted number).
> - glossary.md extraction: `"RETIRED"` == 1; `^## ` count == 0 (regex form, never `-F`); `"[project: bellows]"` >= 2 (the pointer names the tag).
> - live-vs-committed: `cmp` each extraction against the live file (exit 0 — no drift since commit).
> **Item 2 — completeness proof re-run.** Re-run Task C's parse-and-compare in CHECK-ONLY mode against the CENTRAL file and the PRE-RETIREMENT glossary extracted via `git show <CAPTURE_COMMIT>^:knowledge/glossary.md` — all 10 `MATCH` lines again, from the parent commit's bytes (proves the guard ran against what was actually retired).
> **Item 3 — commit hygiene.** `git show <CAPTURE_COMMIT> --numstat --format=` pasted (exactly 3 files); `git rev-parse --show-toplevel` = the bellows root; reflog window `-n 4` → 0 amends.
> **Item 4 — write the receipt** `knowledge/qa/evidence/wrap-3d-central-glossary-2026-08-26/qa-receipt.md`: per-item table with expected/measured/✅, then the Rule 20 block.
>
> ⚠️ **Gate note (pre-declared):** this QA is a probe battery — there is NO pytest scope (Test Scope: none). The `qa_test_result` gate will report "no parseable pytest summary": the known-benign class; the Planner overrides with reference to this clause and the evidence files (7th precedent).

> **Deposits:**
> - `knowledge/qa/evidence/wrap-3d-central-glossary-2026-08-26/probes-raw.txt`
> - `knowledge/qa/evidence/wrap-3d-central-glossary-2026-08-26/qa-receipt.md`
>
> **Scope:**
> - `knowledge/qa/evidence/wrap-3d-central-glossary-2026-08-26/probes-raw.txt`
> - `knowledge/qa/evidence/wrap-3d-central-glossary-2026-08-26/qa-receipt.md`

Rule 20 banner (byte-exact, inside the QA receipt's verification section):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```

## Drafting Cycle

**Tier:** T1 — two doc edits, no code path (the 542 DISCOVERY sweep is the diagnostic ground). Two-walk form, no panel; a direction-class finding escalates to Fork C.

**Walk register:** `bellows/knowledge/research/walk-register-wrap-3d-central-glossary-2026-08-26.md`

**Walk 0 (context pin, measured):** wrap.md 5852 bytes, the 3d block the sole glossary surface (L60–69, anchor count-1); old glossary 34 lines / 10 entries; central `[project: bellows]` == 10; id prediction 543. Design notes (a)–(d): the completeness guard IN the control flow; no plan-predicted post-counts (Step 1 records, QA compares); three re-entry branches partitioning the death states; the 10-entry pre-write assert. **(e), folded at walk 1:** the worktree law — cwd-relative paths only, never the live-tree absolute.

**Walks:**
- Weak spots:          w1 1 folded — Task A's entry-count probe was written `-cF "^## "` (a LITERAL caret under -F: silent 0); rewritten as the regex form with the warning inline at both sites.
- Destruction:         w1 2 folded — (F2) the plan cd'd ABSOLUTE into the live bellows tree, defeating worktree isolation and the teardown merge: every in-repo path made cwd-relative under `git rev-parse --show-toplevel`, Deposits made repo-relative, design note (e) recorded; (F3) re-entry branch 3 keyed on `RETIRED>=1` alone would commit a TORN pointer: strengthened to (iii)=1 ∧ (ii)=0 ∧ (iv)=1 with the torn case named in the HALT arm.
- Vulnerabilities:     w1 dry — completeness guard fail-closed on missing/mismatched terms; root repo read-only; dirty-tree intersection at teardown does not include this plan's four paths.
- Integration-record:  w1 dry — supersession chain named in the pointer text; the lessons-forge sibling + grandfathers stay in open_forks; the 7th-precedent override pre-declared.
- ACID:                w1 dry — one commit, three files, atomic in-repo; sentinels 5852/34/10/10 consistent.
- **Walk 1 total: three findings, all folded (1+2 per the lens lines).**
- Weak spots:          w2 dry — probes re-read post-fold; `"If the file does not exist, create it"` verified count-1 in live wrap.md (the ==0 post-probe is earnable and unambiguous); the case-insensitive glossary count measured 4 pre-edit (recorded for the dev-note comparison discipline, not as a plan prediction).
- Destruction:         w2 dry — the four branch predicates partition all death states incl. the torn-pointer arm; parent-commit extraction (`^`) correct inside the worktree.
- Vulnerabilities:     w2 dry — non-bellows-tagged central entries are skipped by the term filter; a multi-tag bellows entry would fail-closed (missing term → HALT), never fail-open.
- Integration-record:  w2 dry — register referenced on its own single line; design note (e) recorded at walk 0's notes and in the plan.
- ACID:                w2 dry.
- **Walk 2 total: 0 findings — all five lenses dry.**

**Closing:** ✅ **BAR MET at walk 2 — dry confirming pass, all five lenses.** T1 two-walk form; no direction-class finding arose (F2 is execution-form, folded in place), so no panel escalation. Close is MANUAL (CEO-lane verdicts).

**Fold-and-deposit exactly once.**

## Cycle Manifest
tier: T1
target: bellows/hooks/commands/wrap.md
class: shop-infra
reads: /Users/marklehn/Developer/GitHub/bellows/hooks/commands/wrap.md, /Users/marklehn/Developer/GitHub/bellows/knowledge/glossary.md, /Users/marklehn/Developer/GitHub/GLOSSARY.md
writes: hooks/commands/wrap.md, knowledge/glossary.md, knowledge/dev-logs/wrap-3d-central-glossary-dev-2026-08-26.md, knowledge/qa/evidence/wrap-3d-central-glossary-2026-08-26/probes-raw.txt, knowledge/qa/evidence/wrap-3d-central-glossary-2026-08-26/qa-receipt.md
open_forks: lessons-forge/knowledge/glossary.md pointer (that repo's own plan, still owed); the three grandfathered migrations + their CLAUDE.md re-points; ELUVIAN_PATH.md L131 (rides the wrap); the CEO's project-tag-on-lessons question (under consideration, not decided here)
walks: 2
yields: 3, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=N/A
coherence: N/A
