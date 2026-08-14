# Executable: Gate-2 codification — proposal 348, the `fold_check` tool (bellows scripts + tests)

**Type:** Executable
**Project:** bellows
**Depends on:** plan 416 (Done — the Gate-1 routing write; 348 `accepted|codify`), `/Users/marklehn/Developer/GitHub/gate1-packet-folddamage-2026-08-14.md` (the DECIDED block + the tool-before-doctrine sequencing), the two committed reference artifacts (A3/A4-pinned below), plan 392 (Done — the `walk_register_lint` + tests shape this plan clones)
**Created:** 2026-08-14
**Author:** Planner
**Slug:** `gate2-348-2026-08-14`
**dispatch_mode:** bellows
**pause_for_verdict:** always
**Priority:** 5
**cycle_tier:** T1
**qa_steps:** 2
**Test Scope:** targeted in DEV (`tests/test_fold_check.py`; expected **15 passed / 0 failed** — a NEW file, so there is no prior baseline); FULL suite in QA (baseline **1025 passed / 0 failed** in ≈26s, expected post **1040 / 0** — measured at authoring, re-measured by the steps, mismatch HALTS)

⚠️ **ID NOTE:** id read at deposit (a read-only PREDICTION, never a mint).

⚠️ **Derived by READING 392 SECTION BY SECTION, not token-swapping it** — proposal 350, routed by plan 416 today, mandates exactly that.

---

## Why this exists

Gate 1 routed proposal **348** `accepted|codify` — **decision venue and date: the planner-terminal session of 2026-08-14, CEO directives "agree with codify" then "proceed with the 7" on `gate1-packet-folddamage-2026-08-14.md`; the substance was approved earlier the same session ("proceed as recommended, we will learn along the way"); this sentence is the citable record.** This plan ships the TOOL only.

**What the routed text asks for, verbatim in substance:** *"After ANY fold to a machine-read artifact, re-run every reader (plan_lint, gates.py, probe battery) and diff the result set against the pre-fold baseline — a fold must not change the machine-readable state except in the direction it intends."*

**Two DECLARED adaptations of the routed text, stated not silent:**
1. **`gates.py` is NOT run as a reader.** It is a library the daemon imports, not a CLI — it has no standalone invocation and no artifact-level output to diff (verified by read at authoring). The runnable readers are `plan_lint.py` and `walk_register_lint.py`, and the tool runs whichever applies to the artifact. Naming `gates.py` in the routed text describes the *class* of reader, and the class is honored.
2. **The "probe battery" is NOT auto-run.** A plan's probes are prose instructions with no machine-readable declaration, so there is nothing to execute deterministically. The tool's reader set is extensible (one function, `readers_for`), and wiring probes in is future work — **recorded as owed, not dropped** (Step 2's receipt carries it in `#### Forward Register`).

**⚠️ Sequencing — the tool ships BEFORE the doctrine bullet.** Proposal 347's §2.7 bullet mandates running `fold_check` BY NAME; a doctrine rule pointing at a script that does not exist is a dangling mandate. 347 is the NEXT plan, not this one.

**The tool, proven at authoring by execution:** `fold_check.py` runs the artifact's readers as subprocesses, reduces their output to normalized **signals** (WARN / ERROR / PIN-CHECK / FAIL lines with line numbers and volatile counts stripped, hex identity preserved), and diffs that set against a stored JSON baseline. `--save-baseline` before folding; a bare run after. **Exit 0 = unchanged · 1 = drift (reported line by line) · 2 = the check could not run.**

⚠️ **The tool refuses to read a crashed reader as clean** (`ReaderCrashed` → exit 2): a traceback, or no output at all, HALTs the check. This guard exists because the test suite caught the tool's own first form reporting `FOLD-CHECK CLEAN: 0 signals` when `plan_lint` had crashed on a missing import — a silent reader is otherwise indistinguishable from a clean artifact, which is the exact failure the tool exists to prevent.

**Live proof (executed at authoring, not argued):** baselined the SHIPPED plan `executable-416.md`, applied this session's real X-2 fold (rewriting the literal `newest same-class`), and the tool reported `FOLD-CHECK DRIFT — APPEARED: plan_lint: (k) WARN: clone-framed plan does not name its newest same-class comparison`, exit 1. That is today's actual regression, caught mechanically.

**Test posture:** 15 tests, each a constructed failure; the two integration cases replay MEASURED instances (the deleted `(k)` literal; the bare `test` token tripping the test-scope check), plus a line-shift case that must stay SILENT and two crashed-reader cases. ⚠️ **The `(k)` fixture required a clone-framed `**Tier:**` line to make the check reachable at all — an earlier fixture form left the check unreachable and the test failed as a false negative; the fixture is the positive control and was earned, not assumed.**

**Expected gate advisories — MEASURED at the mirror, not predicted** (DC v2.11's rule: a pre-classification is a prediction the closing run must earn): **exactly FIVE `(o2)` lines**, one per Deposits entry, because bellows plans carry repo-relative paths (the 392 precedent) and (o2) reads them as un-prefixed. Both `(q)` pins `result=ok`. ⚠️ The pre-close run also carries one `Drafting Cycle block missing lens(es)` WARN — the PLACEHOLDER advisory, which clears the moment the Cycle Log's Walks block names its five lenses; **a lens WARN surviving at the freeze means the Cycle Log was never filled** (the 405 X-4 diagnostic, carried).

**Numbers discipline:** reference suite **15 passed** in a mirrored tree; full bellows suite baseline **1025 passed / 0 failed** measured at authoring; expected post **1040**. The steps RE-RUN and compare; any mismatch HALTS.

**HALT ROUTING:** Step 1 reads this plan and the two reference artifacts; Step 2 reads Step 1's commit, the live tree, and `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md`. Any missing/unreadable input → HALT the step that needs it and name it.

**Environment facts (verbatim, load-bearing):** `grep` is a ugrep shim — `-F` for every literal; a zero-match `grep -c` prints `0` and EXITS 1 (read the count, never the exit code); `--` before dash-leading literals; shell state does not persist between invocations.

---

## Ledger

- **C1 — reference-copy is the only editor.** Both files land by `cp` from the committed references; no hand-authoring in the bellows tree. *(observer: QA Item 2's byte-identity proof)*
- **C2 — four pins gate the run** (per-pin lines with interleaved descriptors — ⚠️ **the interleaving is LOAD-BEARING: the (q) resolver takes the FIRST path in a token's context window, and three consecutive `shasum` lines make each digest resolve against the preceding pin's path; measured as two false MISMATCHes earlier today**):
  - the reference implementation, derived at authoring by running the command:
    `shasum -a 256 /Users/marklehn/Developer/GitHub/governance/knowledge/research/fold-check-reference-2026-08-14.py` → `b6eb6dda5465d2c574a37c4ec573d8a070fbe3485c3bf9b4b4afe8b790388b0c`
  - the reference tests, same derivation:
    `shasum -a 256 /Users/marklehn/Developer/GitHub/governance/knowledge/research/fold-check-tests-reference-2026-08-14.py` → `f7e77b9425c01069689f7b9f17d9d45137654ca8bef490d4d3bc1e490e6b63d9`
  - **A3/A4 — the two TARGETS must be ABSENT** (`scripts/fold_check.py`, `tests/test_fold_check.py`): both verified non-existent at authoring; a present file means a foreign writer → HALT.
- **C3 — post-conditions proven from the LIVE tree after apply**, not from the reference. *(observer: Task C + QA Item 1)*
- **C4 — commits are cd-first + explicit pathspec + name-only verify + bare `git rev-parse --show-toplevel`**, CAPTURE_COMMIT recorded; one action per state-changing compound, each with its own post-condition close; no `--amend`. *(observer: QA Item 3)*
- **C5 — the tool is NOT wired into any gate chain by this plan.** `fold_check.py` ships standalone and warn-only, exactly as `walk_register_lint` did (plan 338's deliberate posture). Wiring is a separate decision. *(observer: QA Item 4's grep proving `fold_check` counts 0 in `gates.py` and `bellows.py`)*
- **C6 — serialized dispatch stated:** no other bellows-tree-writing plan in flight at dispatch; the A3/A4 absence check is the in-window detector. *(observer: A0)*

---

## How to Run This Plan

**Bootstrap prompt:**
```
Read the plan at knowledge/decisions/in-progress-executable-<id>.md (the daemon renames the deposited placeholder on claim). Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation.
```

---

## Scope

- `scripts/fold_check.py`
- `tests/test_fold_check.py`
- `knowledge/development/fold-check-dev-2026-08-14.md`
- `knowledge/qa/fold-check-2026-08-14/qa-receipt.md`
- `knowledge/qa/fold-check-2026-08-14/probes-raw.txt`

---

## STEP 1 — DEV (land the tool and its tests by reference copy)

> **FIRST — post a short visible chat message (1-2 sentences) confirming you are starting this plan.** Do NOT rename this file.
>
> ⚠️⚠️ **EXECUTE STEP 1 ONLY, THEN STOP.**
>
> All tree writes are repo-relative in YOUR working tree (the daemon may run you in a worktree — `git rev-parse --show-toplevel` prints yours); the two reference reads are ABSOLUTE, read-only.
>
> **Task A0 — branches, catch-all LAST.**
> **(1) PINS (C2):** both reference shasums match.
> **(2) TARGETS ABSENT (C2's A3/A4):** `ls scripts/fold_check.py tests/test_fold_check.py` → BOTH not-found. ⚠️ **Read the message, not the exit code** — `ls` on two missing files exits non-zero, which is the EXPECTED state here.
> **(3) CLEANLINESS:** `git status --porcelain -- scripts/ tests/ knowledge/development/fold-check-dev-2026-08-14.md` empty.
> **(4) RE-ENTRY key:** `git log --oneline -1 -- scripts/fold_check.py` — subject carries this plan's slug?
> - **FRESH** = (1) match AND (2) both absent AND (3) empty AND (4) no → Task B.
> - **RE-ENTRY** = (4) yes AND `git status --porcelain -- scripts/fold_check.py tests/test_fold_check.py` empty → the copies landed; verify Task C on the committed tree. Do NOT re-copy. **Tail half-state:** if the dev note is missing or uncommitted, create or commit exactly it (mark `re-derived on re-entry`). Then report complete.
> - **NONE-MATCH** = anything else (including either target PRESENT) → **HALT quoting every measurement.**
>
> **Task B — apply, one action per compound, each with its own close:**
> - **B1:** `cp /Users/marklehn/Developer/GitHub/governance/knowledge/research/fold-check-reference-2026-08-14.py scripts/fold_check.py`; close SEPARATELY: `cmp /Users/marklehn/Developer/GitHub/governance/knowledge/research/fold-check-reference-2026-08-14.py scripts/fold_check.py; echo "cmp_exit=$?"` → expect `cmp_exit=0`; otherwise `rm -f scripts/fold_check.py` and HALT quoting the output.
> - **B2:** `cp /Users/marklehn/Developer/GitHub/governance/knowledge/research/fold-check-tests-reference-2026-08-14.py tests/test_fold_check.py`; close with the same `cmp` form, same expectation, same failure handling.
>
> **Task C — post-conditions from the LIVE tree, count read never exit code:**
> - `grep -oF "def fold_check" scripts/fold_check.py | wc -l` == 0 **and** `grep -oF "class ReaderCrashed" scripts/fold_check.py | wc -l` == 1 (the crashed-reader guard is present — the tool's own load-bearing safety property)
> - `grep -oF "FOLD-CHECK DRIFT" scripts/fold_check.py | wc -l` == 1 and `grep -oF "FOLD-CHECK CLEAN" scripts/fold_check.py | wc -l` == 1
> - `grep -oF "def test_" tests/test_fold_check.py | wc -l` == **15** (occurrence form, never `-c` — `-c` counts LINES and would miss two definitions sharing one line)
> - **Targeted tests:** `python3 -m pytest tests/test_fold_check.py -q` → final line reads **15 passed** (0 failures). A different PASS count with 0 failures is reported LOUDLY, never silently accepted.
> - **LIVE PROOF, run scratch-only** (the tool's own contract, exercised): copy any committed plan to `<scratch>/probe.md`, run `python3 scripts/fold_check.py --save-baseline <scratch>/probe.md` (expect `BASELINE SAVED`), then edit the SCRATCH copy to remove the literal `newest same-class` if present (else append a line reading `A count-only test is not sufficient.`), re-run `python3 scripts/fold_check.py <scratch>/probe.md` and expect **exit 1** with a `FOLD-CHECK DRIFT` line. ⚠️ **Scratch only — never baseline or edit a file inside the repo.** If the chosen plan yields no drift, say so and pick another; a silent no-drift is NOT a pass.
> - Any probe failing → FRESH: `rm -f scripts/fold_check.py tests/test_fold_check.py` and HALT; RE-ENTRY: HALT with no removal.
>
> **Task D — dev note + commit.** Write `knowledge/development/fold-check-dev-2026-08-14.md` (what landed, both `cmp` exits, every probe result raw, the targeted-suite tail, the live-proof transcript). Commit (ONE compound, cd-first to YOUR tree root, no amend): `cd "$(git rev-parse --show-toplevel)" && git add scripts/fold_check.py tests/test_fold_check.py knowledge/development/fold-check-dev-2026-08-14.md && git commit -m "[<id from your plan filename>] fold-check(gate2-348-2026-08-14): the fold post-condition tool — diff the machine-readable state against a pre-fold baseline" -- scripts/fold_check.py tests/test_fold_check.py knowledge/development/fold-check-dev-2026-08-14.md && git rev-parse HEAD && git rev-parse --show-toplevel`. The printed hash is **CAPTURE_COMMIT**; in a SEPARATE compound verify `git show <CAPTURE_COMMIT> --numstat --format=` lists exactly the three paths. Then STOP.
>
> **Deposits:**
> - `scripts/fold_check.py`
> - `tests/test_fold_check.py`
> - `knowledge/development/fold-check-dev-2026-08-14.md`
>
> **Scope:**
> - `scripts/fold_check.py`
> - `tests/test_fold_check.py`
> - `knowledge/development/fold-check-dev-2026-08-14.md`

---

## STEP 2 — QA

> ⚠️⚠️ **PRECONDITION — Step 1 ran as its own dispatch:** `git log --oneline -1 -- scripts/fold_check.py` names the Step-1 commit, made before this step began and not by this context. Otherwise mark the independence gap plainly. **No Monitor anywhere in this step; every command foreground.**
>
> **(A) Rule 20 self-check block** — the canonical block from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` (read live). Canonical header `Rule 20 — QA Self-Check Results`; on full pass the canonical line `PASSED — SELF-CHECK PASSED`. `required_evidence_files` = the qa-directory subset of `## Scope`.
>
> **(B) Deliverable verification — a FAIL is reported, never repaired:**
> - **Item 1 — Task C's probe battery re-run against the COMMITTED content:** extract each target from `<CAPTURE_COMMIT>` (`git show <CAPTURE_COMMIT>:<path> > <scratch>/<name>; echo "show_exit=$?"` — expect 0 + non-empty per file), re-run every Task-C grep probe against the extractions (the list is the authority); raw into `probes-raw.txt`.
> - **Item 2 — C1 byte-identity:** `diff` the committed `scripts/fold_check.py` against `/Users/marklehn/Developer/GitHub/governance/knowledge/research/fold-check-reference-2026-08-14.py`, and the committed tests against their reference — byte-identical proves reference-copy was the only editor. ⚠️ First verify the references are themselves committed and clean in the ROOT repo (`git -C /Users/marklehn/Developer/GitHub status --porcelain -- <both paths>` empty AND `git -C … log -1 --format=%h -- <path>` NON-EMPTY per file; an empty hash is a FAIL).
> - **Item 3 — C4:** CAPTURE_COMMIT's numstat pasted; toplevel printed; single non-amend commit (one parent, subject matches the Task-D form).
> - **Item 4 — C5, the tool is NOT gate-wired:** `fold_check` counts **0** in `gates.py` and in `bellows.py` (positive control per file, measured: `Deposits` in `gates.py` > 0; `plan` in `bellows.py` > 0). A non-zero count means something wired it — report, do not repair.
> - **Item 5 — FULL suite:** `python3 -m pytest tests/ -q` foreground → expect **1040 passed / 0 failed** (measured baseline 1025 + 15). A different pass count with 0 failures is reported loudly with the collected delta, never silently accepted.
> - **Item 6 — the live proof, INDEPENDENTLY re-run scratch-only:** repeat Step 1's baseline→fold→detect sequence on a fresh scratch copy of a DIFFERENT committed plan than Step 1 used; expect `BASELINE SAVED` then exit 1 with `FOLD-CHECK DRIFT`. ⚠️ **Never baseline, fold, or write any file inside the repo.**
> - **Item 7 — raw output throughout.**
>
> Commit the receipt + raw file (cd-first, pathspec exactly them, no amend), then STOP.
>
> **Deposits:**
> - `knowledge/qa/fold-check-2026-08-14/qa-receipt.md`
> - `knowledge/qa/fold-check-2026-08-14/probes-raw.txt`
>
> **Scope:**
> - `knowledge/qa/fold-check-2026-08-14/qa-receipt.md`
> - `knowledge/qa/fold-check-2026-08-14/probes-raw.txt`

---

## Drafting Cycle

**Tier:** T1 — new tooling in a single subsystem, additive, no existing behaviour touched and nothing gate-wired (C5); structure-clone of shipped 392 (`walk_register_lint` + tests), so T-8 is silent. Clone origin AND **newest same-class = 392** (Done 2026-08-14, the only prior bellows script+tests plan), measured against `Done/` by ship date.

**Walk register:** `governance/knowledge/research/walk-register-gate2-348-2026-08-14.md` (schema 0.3), committed per phase.

**Walk 0 (context pin, measured 2026-08-14):** both targets ABSENT (`scripts/fold_check.py`, `tests/test_fold_check.py`); bellows `scripts/`+`tests/` porcelain clean; full-suite baseline **1025 passed / 0 failed** ≈26s; reference implementation and tests committed at `f9ac2c1` and pinned; reference suite **15 passed** in a mirrored tree; `fold_check` counts 0 in `gates.py` and `bellows.py` (nothing pre-wired). **Executed proofs at authoring:** the crashed-reader guard was ADDED after the suite caught the tool reporting `CLEAN: 0 signals` on a crashed `plan_lint`; the `(k)` fixture was corrected after the check proved UNREACHABLE without a clone-framed Tier line (a false-negative test); and the tool was run against the SHIPPED `executable-416.md`, reproducing today's real X-2 regression as `FOLD-CHECK DRIFT`, exit 1.

**Walks (2 warm):**
- Weak spots:          w1 dry (A0's four arms incl. the ABSENT-target class, both `cmp` closes, every probe re-read against the reference bytes); w2 dry.
- Destruction:         w1 dry (both targets are NEW files, so nothing existing can be harmed; C5 keeps the tool out of every gate chain, and QA Item 4 proves it by grep — a wiring change would be a separate decision); w2 dry.
- Vulnerabilities:     w1 EXECUTED — the suite in a mirrored tree (15 passed), the crashed-reader guard proven by construction, the `(k)` fixture proven reachable, and the tool run end-to-end against a SHIPPED plan reproducing today's real regression; w2 dry.
- Integration-record:  w1 dry (bellows conventions: repo-relative Scope with project-prefixed Deposits, the `scripts/`+`tests/` pairing from 392, Test Scope header; stray-token sweep clean); w2 dry.
- ACID:                w1 dry (two steps, one gate window; a half-applied copy lands in NONE-MATCH via the target-absence and porcelain arms; the tool writes only to scratch).

**Splits: w1 instruction 0 / record 0 — DRY (the four findings landed at walk 0, all from executing the tool) · w2 dry.**

**Conformance (§5):** faithful-mirror `plan_lint` at the deposit-shaped scratchpad mirror — NEVER the real `decisions/`. Close run measured **EXIT 0** with the five `(o2)` advisories above plus the placeholder-lens WARN this fill clears; both pins `result=ok`. Freeze item 3 binds to the five-line set.

**Closing:** walk 2 read dry on every lens — **instruction 0 / record 1: this Cycle-Log fill itself, written at close with measured content** (0 of 1 fold-introduced). This cycle's yield came entirely from RUNNING the tool at walk 0 rather than reading it: two of the four findings were defects in the tool's own safety properties, and one was a test that could not have failed. Fold-and-deposit exactly once.
