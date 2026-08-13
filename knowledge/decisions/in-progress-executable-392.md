# Executable: walk-register schema v0.3 + validator guards — the verbatim-ellipsis annotation, DUP-APPEND/headerless-rows detection, the every-tier coherence line

**Type:** Executable
**Project:** bellows
**Depends on:** `/Users/marklehn/Developer/GitHub/gate1-packet-2026-08-13.md` (the TRUNCATION_RE rider — "routes with the 334 schema work"), plan 386's History-row deferral (the record-coherence every-tier home is "the bellows schema plan's to land"), plans 389+391 registers (the F2-1/F2-2 incident records + this session's recurrences), executable-365 step 1 (committed + Planner-verified — schema 0.1→0.2, the version-bump clone origin; the plan itself HALTED at its QA step and `executable-366` is its Done corrective — scout SC-2's status correction), executable-338 (Done — the schema+validator creating ancestor), the three committed reference artifacts (paths + pins in the Ledger)
**Created:** 2026-08-13
**Author:** Planner
**Slug:** `wrl-guards-2026-08-13`
**dispatch_mode:** bellows
**pause_for_verdict:** always
**Priority:** 5
**cycle_tier:** T1
**qa_steps:** 2
**Test Scope:** targeted in DEV (`tests/test_walk_register_lint.py`; baseline **19 passed / 0 failed**, expected post **27 / 0** — 8 new constructed-failure tests); FULL suite in QA (baseline **1017 passed / 0 failed** in ≈26s, expected post **1025 / 0** — expectations measured at authoring, re-measured by the steps, mismatch HALTS)

⚠️ **ID NOTE:** id read at deposit (a read-only PREDICTION; the freeze reads fresh — never a mint).

---

## Why this exists

Three owed items converge on the walk-register surfaces, every one carrying measured live evidence:

1. **The TRUNCATION_RE rider (gate1 packet 2026-08-13):** `walk_register_lint.py` cannot distinguish a verbatim source ellipsis from an elision. Measured at authoring: `truncated_pre_fold_text` fires on **39 rows across 6 committed registers**; the owned verbatim class is documented in two of them (the s40sweep ingest register's f4/f5 — complete pre-image bytes containing display-prefix `…` — and the gate2-dc register's ownership note). Rewriting those bytes to earn CONFORMANT would violate the schema's own VERBATIM ALWAYS rule. The fix is the **`verbatim-ellipsis` row annotation**: the marker in the row's `finding` or `resolution` cell (never inside `pre_fold_text`) downgrades the WARN to `OK`/`verbatim_ellipsis_annotated`. Unannotated stays WARN; closed registers stay byte-stable (their ownership notes stand — forward-looking mechanism only).
2. **The F2-1/F2-2 guard classes (measured twice in one register at 389, recurring live in this session's 391 cycle):** `duplicate_row` (byte-identical fold rows — the DUP-APPEND channel class; corpus today: 0, the guard is prophylactic with two struck incident records), `headerless_rows` (fold rows detached from any header+separator — **INVISIBLE to v0.2 validation**; measured at authoring: **46 rows across 4 committed registers — 21 contract-entry-readability / 16 gate2-dc / 8 predicted-number-pin-census / 1 dc-coldfront — including 16 panel-seat rows no validator run had ever read**, samples verified true-positive by inspection), and `duplicate_adjacent_line` (the duplicated open-tail line's shape; advisory only; corpus today: 0). The first two are structural (flip UNCONFORMANT); the third is advisory (no status flip).
3. **The record-coherence every-tier home (386's declared deferral):** the schema doc gains the line that the rows↔commits both-directions check runs at the walk-0 battery and every culmination at EVERY tier — T1 included. Git-side, deliberately outside the validator (it stays repo-blind).

**The edit mechanism is fully rehearsed:** the amended validator and test file exist as committed reference implementations, proven at authoring — the 19 existing tests pass unmodified against the reference (0 regressions), the 8 new constructed-failure tests pass (27/27 in a mirrored scratch tree), and the corpus sweep numbers above were measured by RUNNING the reference over `governance/knowledge/research/`. The schema-doc edit is a 3-anchor builder, dry-run proven scratch→scratch (`OK — 3 edits`, numstat **18 added / 2 removed**, 122→138 lines), with live-output + shop-root guards proven firing by execution.

**What this plan deliberately does NOT do:** no gate wiring (the validator remains standalone, warn-only, "not wired into any gate chain" — its docstring's claim, retained); no retro-annotation of closed registers (Rule 96's closed-artifact convention — their ownership notes are the record); no edit to DRAFTING_CYCLE.md or plan_lint (nothing here is gate-read; QA sweeps prove it); no consumer migration (import scan measured: no module imports walk_register_lint except its own test).

**Expected gate advisories, pre-classified for the watcher:** plan_lint (o2) warns on ALL SIX Deposits entries — bellows-project plans carry repo-relative paths (the 365/366 convention; the daemon dispatches in the bellows tree) and (o2) reads them as un-prefixed; correct and accepted, six advisory lines. (q): the five pins below expected `result=ok` at a FAITHFUL mirror (one that carries `scripts/plan_lint.py` — Item 5 references it, and an unfaithful mirror fires a spurious (o1)).

**HALT ROUTING:** Step 1 reads this plan, the three reference artifacts, and the three target files; Step 2 reads Step 1's commit, the live tree, and `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md`. Any missing/unreadable input → HALT the step that needs it and name it.

**Environment facts (verbatim, load-bearing):** `grep` is a ugrep shim — `-F` for every literal; a zero-match `grep -c` prints `0` and EXITS 1 (read the count, not the exit code; never `&&`-chain zero-count probes); `--` before dash-leading literals; shell state does not persist between invocations; `git diff --no-index` EXITS 1 when files differ (read the numbers, never the exit code).

---

## Ledger

- **C1 — reference-copy is the only editor.** The validator and test file land by `cp` from the committed references; the schema doc lands by builder apply-copy. No hand edits of any target. *(observer: QA Item 2's byte-identity proofs)*
- **C2 — five pins gate the run** (per-pin lines; derived at authoring by running the command; the freeze re-derives all five):
  - A1 target schema doc:
    `shasum -a 256 knowledge/architecture/walk-register-schema.md` → `6ac80fd2745b374867a4f701296b3a8c7bb40a3e23413bf186b2164b4a41ebb8`
  - A2 target validator:
    `shasum -a 256 scripts/walk_register_lint.py` → `a3323041029dad3c94b974e9fa1956b9fdfb8fa433bc0c95f628b5b3dea82049`
  - A3 target tests:
    `shasum -a 256 tests/test_walk_register_lint.py` → `749cf12e96cb3a2cbc87454661c329e82493e12a8db07f008ae52987a7b6959e`
  - A4 reference validator:
    `shasum -a 256 /Users/marklehn/Developer/GitHub/governance/knowledge/research/wrl-v03-reference-2026-08-13.py` → `19a41ab0b879925be7a5521d663327de4a5a5ac50cc7e9eac9531e767d33e4a2`
  - A5 reference tests:
    `shasum -a 256 /Users/marklehn/Developer/GitHub/governance/knowledge/research/wrl-v03-tests-reference-2026-08-13.py` → `f5708324488ca1576dddb48f6f1a34cf0b2b4038374a885e951689e142079b8a`
  Any mismatch → HALT: a surface moved under the plan. (The schema builder is pinned by freeze-item-0 currency instead — on-disk == committed blob, non-empty `git log -1 --format=%h` required.) *(observer: A0)*
- **C3 — every post-condition proven from the LIVE tree after apply**, each probe proven earnable at authoring (new tokens 0 pre-edit; test counts 19→26 and 1017→1024 measured pre/post on the reference). *(observer: Task C + QA Item 1)*
- **C4 — commits are cd-first + explicit pathspec + name-only verify + bare `git rev-parse --show-toplevel`**, CAPTURE_COMMIT recorded, numstats spelled and compared; one action per state-changing compound, each close verifying its post-condition (PT v4.88 Rule 85); no `--amend`. *(observer: QA Item 3)*
- **C5 — serialized dispatch stated:** no other bellows-tree-writing plan in flight at dispatch (plan 390, in flight on the parallel terminal, writes invoice-pulse — no shared store); the A-pins are the in-window defense. *(observer: A0)*
- **C6 — the corpus sweep is READ-only evidence:** Step 1's sweep runs the amended validator over `governance/knowledge/research/` and REPORTS; no register file is edited, ever (closed artifacts stay byte-stable). *(observer: QA Item 4's porcelain check over the governance registers)*

---

## How to Run This Plan

**Bootstrap prompt:**
```
Read the plan at knowledge/decisions/in-progress-executable-<id>.md (the daemon renames the deposited placeholder on claim). Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation.
```

---

## Scope

**The authority for the write-set; each step's Deposits block carries only its own subset.**

- `knowledge/architecture/walk-register-schema.md`
- `scripts/walk_register_lint.py`
- `tests/test_walk_register_lint.py`
- `knowledge/development/wrl-guards-dev-2026-08-13.md`
- `knowledge/qa/wrl-guards-2026-08-13/qa-receipt.md`
- `knowledge/qa/wrl-guards-2026-08-13/probes-raw.txt`

---

## STEP 1 — DEV (schema v0.3 + validator + tests, by reference copy and builder)

> **FIRST — post a short visible chat message (1-2 sentences) confirming you are starting this plan.** Do NOT rename this file.
>
> ⚠️⚠️ **EXECUTE STEP 1 ONLY, THEN STOP.**
>
> All tree writes are repo-relative in YOUR working tree (the daemon may run you in a worktree — `git rev-parse --show-toplevel` prints yours); external reads (this plan's references) are ABSOLUTE paths, read-only. `<scratch>` must live OUTSIDE the shop root (`/Users/marklehn/Developer/GitHub`) — the session scratchpad qualifies; an in-repo `scratchpad/` does not (the builder rejects it by realpath).
>
> **Task A0 — branches, catch-all LAST.**
> **(1) PINS (C2):** all five shasums above match (A1–A3 repo-relative in your tree; A4–A5 absolute).
> **(2) CLEANLINESS:** `git status --porcelain -- knowledge/architecture/walk-register-schema.md scripts/walk_register_lint.py tests/test_walk_register_lint.py knowledge/development/wrl-guards-dev-2026-08-13.md` empty.
> **(3) RE-ENTRY key:** `git log --oneline -1 -- scripts/walk_register_lint.py` — subject carries this plan's slug?
> - **FRESH** = (1) all match AND (2) empty AND (3) no → Task B.
> - **RE-ENTRY** = (3) yes AND `git status --porcelain -- scripts/walk_register_lint.py knowledge/architecture/walk-register-schema.md tests/test_walk_register_lint.py` empty (target-scoped — the tail arm below repairs the dev note, so its state must not disqualify the branch) → the edits landed; verify Task C's post-conditions on the committed tree. Do NOT re-apply. **Tail half-state:** if the dev note is missing or uncommitted, re-create or commit exactly it (mark `re-derived on re-entry`). Then report complete.
> - **NONE-MATCH** = anything else (including any pin mismatch) → **HALT quoting every measurement.**
>
> **Task B — apply (one action per compound, each with its own close):**
> - **B1 schema by builder:** `python3 /Users/marklehn/Developer/GitHub/governance/knowledge/research/builder-wrl-guards-2026-08-13.py knowledge/architecture/walk-register-schema.md <scratch>/schema-out.md` — expect stdout BEGINNING `OK — 3 edits` (prefix match) and `git diff --no-index --numstat` target-vs-scratch reading **18 added / 2 removed** (exits 1 by design — read the numbers). Mismatch → HALT with both numbers.
> - **B2 apply schema:** `cp <scratch>/schema-out.md knowledge/architecture/walk-register-schema.md`; close (separate compound): `cmp <scratch>/schema-out.md knowledge/architecture/walk-register-schema.md; echo "cmp_exit=$?"` — expect `cmp_exit=0`; any other value → restore (`git checkout -- knowledge/architecture/walk-register-schema.md`) and HALT quoting the cmp output.
> - **B3 apply validator:** `cp /Users/marklehn/Developer/GitHub/governance/knowledge/research/wrl-v03-reference-2026-08-13.py scripts/walk_register_lint.py`; close: same cmp form, expect `cmp_exit=0`, restore+HALT otherwise.
> - **B4 apply tests:** `cp /Users/marklehn/Developer/GitHub/governance/knowledge/research/wrl-v03-tests-reference-2026-08-13.py tests/test_walk_register_lint.py`; close: same cmp form, expect `cmp_exit=0`, restore+HALT otherwise.
>
> **Task C — post-conditions from the LIVE tree, count read never exit code:**
> - `grep -cF -- "# Walk Register Schema — v0.3" knowledge/architecture/walk-register-schema.md` == 1 and `grep -cF -- "## v0.3 — the verbatim-ellipsis annotation" knowledge/architecture/walk-register-schema.md` == 1
> - `grep -cF -- "# Walk Register Schema — v0.2" knowledge/architecture/walk-register-schema.md` == 0 (retired; ⚠️ zero prints with exit 1 by design)
> - `grep -cF "VERBATIM_ELLIPSIS_MARKER" scripts/walk_register_lint.py` == 2 (definition + use)
> - `grep -cF "_structural_guards" scripts/walk_register_lint.py` == 3 (call in the fold-table path + call in the no-table path + def — the value MEASURED on the pinned reference at authoring; scout SC-1 caught the first form of this probe wrong against its own reference)
> - `grep -cF "def test_headerless_rows_warn_and_flip_status" tests/test_walk_register_lint.py` == 1
> - **Targeted tests:** `python3 -m pytest tests/test_walk_register_lint.py -q` → final line reads **27 passed** (0 failures; the count is measured-at-authoring — a different PASS count with 0 failures is reported loudly, not silently accepted).
> - **Corpus sweep (READ-only, C6):** `python3 scripts/walk_register_lint.py /Users/marklehn/Developer/GitHub/governance/knowledge/research/ > <scratch>/sweep.tsv 2>/dev/null` then count notes: `awk -F'\t' '{print $8}' <scratch>/sweep.tsv | sort | uniq -c` — expect `truncated_pre_fold_text` **39**, `headerless_rows` **46**, `duplicate_row` **0**, `duplicate_adjacent_line` **0** (authoring-time measurements). ⚠️ **The expectations BIND ten named files** — the six truncation files (s2-rewrite 31, cycle-ingest 2, inapp-xml-fetch 2, validate-detail-enrich 2, fix-fetch-test-reload-isolation 1, gate2-dc-s40sweep 1) and the four headerless files (contract-entry-readability 21, gate2-dc-s40sweep 16, predicted-number-pin-census 8, dc-coldfront 1). Rows from ANY OTHER register (registers commit continuously — this cycle's own included) are the expected-drift class: list them per file, any note value including `verbatim_ellipsis_annotated`, and proceed. A delta WITHIN the ten named files → HALT (scout SC-5's mechanical delta rule — no timestamp probe needed).
> - Any probe failing → FRESH branch: restore all three targets (`git checkout -- knowledge/architecture/walk-register-schema.md scripts/walk_register_lint.py tests/test_walk_register_lint.py`) and HALT; RE-ENTRY branch: HALT with no restore.
>
> **Task D — dev note + commit.** Write `knowledge/development/wrl-guards-dev-2026-08-13.md` (what applied, all measured numbers, the sweep tally raw). Commit (ONE compound, cd-first to YOUR tree root, no amend): `cd "$(git rev-parse --show-toplevel)" && git add knowledge/architecture/walk-register-schema.md scripts/walk_register_lint.py tests/test_walk_register_lint.py knowledge/development/wrl-guards-dev-2026-08-13.md && git commit -m "[<id from your plan filename>] wrl-guards(wrl-guards-2026-08-13): schema v0.3 + verbatim-ellipsis annotation + duplicate/headerless guards + 7 tests" -- knowledge/architecture/walk-register-schema.md scripts/walk_register_lint.py tests/test_walk_register_lint.py knowledge/development/wrl-guards-dev-2026-08-13.md && git rev-parse HEAD && git rev-parse --show-toplevel`. The printed hash is **CAPTURE_COMMIT**; in a SEPARATE compound verify `git show <CAPTURE_COMMIT> --numstat --format=` shows the schema row **18/2** plus the validator, tests, and dev-note rows (re-measure, mismatch → report loudly). Then STOP.
>
> **Deposits:**
> - `knowledge/architecture/walk-register-schema.md`
> - `scripts/walk_register_lint.py`
> - `tests/test_walk_register_lint.py`
> - `knowledge/development/wrl-guards-dev-2026-08-13.md`
>
> **Scope:**
> - `knowledge/architecture/walk-register-schema.md`
> - `scripts/walk_register_lint.py`
> - `tests/test_walk_register_lint.py`
> - `knowledge/development/wrl-guards-dev-2026-08-13.md`

---

## STEP 2 — QA

> ⚠️⚠️ **PRECONDITION — Step 1 ran as its own dispatch:** `git log --oneline -1 -- scripts/walk_register_lint.py` names the Step-1 commit, made before this step began and not by this context. Otherwise mark the independence gap plainly. **No Monitor anywhere in this step; every command foreground.**
>
> **(A) Rule 20 self-check block** — the canonical block from `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` (read live). The receipt carries the canonical header `Rule 20 — QA Self-Check Results` and, on full pass, the canonical verdict line `PASSED — SELF-CHECK PASSED`. `required_evidence_files` = the qa-directory subset of `## Scope`.
>
> **(B) Deliverable verification — a FAIL is reported, never repaired:**
> - **Item 1 — Task C's probe battery re-run against the COMMITTED content:** extract each target from `<CAPTURE_COMMIT>` (`git show <CAPTURE_COMMIT>:<path> > <scratch>/<name>; echo "show_exit=$?"` — expect 0 + non-empty per file), run EVERY Task C grep probe against the extractions (the list is the authority); raw output into `probes-raw.txt`.
> - **Item 2 — C1 byte-identity:** `diff <scratch>/committed-validator.py /Users/marklehn/Developer/GitHub/governance/knowledge/research/wrl-v03-reference-2026-08-13.py` byte-identical; same for the tests reference; for the schema, first verify the builder's currency in the ROOT repo (`git -C /Users/marklehn/Developer/GitHub status --porcelain -- governance/knowledge/research/builder-wrl-guards-2026-08-13.py` empty AND `git -C /Users/marklehn/Developer/GitHub log -1 --format=%h -- governance/knowledge/research/builder-wrl-guards-2026-08-13.py` NON-EMPTY — an empty result is a FAIL), then run the on-disk builder on the PRE-edit doc (`git show <CAPTURE_COMMIT>~1:knowledge/architecture/walk-register-schema.md` into scratch, exit/non-empty checks) into scratch and diff vs the committed schema — byte-identical proves reference-copy/builder were the only editors.
> - **Item 3 — C4:** CAPTURE_COMMIT's numstat pasted (schema 18/2 + three more rows); toplevel printed; single non-amend commit (one parent, subject matches the Task-D form).
> - **Item 4 — FULL suite + sweep re-run + register porcelain:** `python3 -m pytest tests/ -q` foreground → expect **1024 passed / 0 failed** (measured baseline 1017 + 7; a different pass count with 0 failures is reported loudly with the collected delta, not silently accepted); re-run the Task-C corpus sweep and diff its tally against Step 1's dev-note tally (delta classification per Task C's rule); `git -C /Users/marklehn/Developer/GitHub status --porcelain -- "governance/knowledge/research/walk-register-*.md"` lists NO file except (possibly) `walk-register-wrl-guards-2026-08-13.md` — this cycle's own register accretes until its wrap commit and is exempt; ANY OTHER register appearing dirty is the C6 FAIL (scout SC-4's false-FAIL channel closed).
> - **Item 5 — gate-neutrality:** `verbatim_ellipsis_annotated`, `headerless_rows`, `duplicate_adjacent_line` each count 0 in `scripts/plan_lint.py` and `gates.py` (positive control: `Drafting Cycle` in scripts/plan_lint.py > 0) — nothing here is gate-read.
> - **Item 6 — raw output throughout.**
>
> Commit the receipt + raw file (cd-first, pathspec exactly them, no amend), then STOP.
>
> **Deposits:**
> - `knowledge/qa/wrl-guards-2026-08-13/qa-receipt.md`
> - `knowledge/qa/wrl-guards-2026-08-13/probes-raw.txt`
>
> **Scope:**
> - `knowledge/qa/wrl-guards-2026-08-13/qa-receipt.md`
> - `knowledge/qa/wrl-guards-2026-08-13/probes-raw.txt`

---

## Drafting Cycle

**Tier:** T1 — **T-1 fires** (three files across two subsystems: knowledge/architecture + scripts/tests). Full five-lens walk; cold scout at the Planner's call (CONVENED — the last two cycles' scouts each caught a HIGH; priced ≈100–160k against that record).

**Walk register:** `governance/knowledge/research/walk-register-wrl-guards-2026-08-13.md` (schema 0.2 form; this plan's own v0.3 additions are not retroactive to its register), committed per phase — the v2.8 record clock binding; **the every-tier record-coherence line this plan ships is honored by this cycle** (rows↔commits both directions at each culmination).

**Walk 0 (context pin, measured):** targets pinned A1–A3 (porcelain clean; last writer 365 `705ea50`, step-1-committed-verified; creating ancestor 338); references pinned A4–A5 + builder freeze-item-0; baselines by execution (19/0 targeted, 1017/0 full ≈26s, import scan 0 consumers); corpus sweep measured (39 truncation / 6 files; reference adds 46 headerless / 4 files, 0 dup, 0 adjacent — headerless samples inspected true-positive); reference proven 27/27 in a mirrored tree; builder dry-run `OK — 3 edits`, 18/2, guards (live-output + shop-root) proven firing. Clone taxonomy: version-bump class = 365 (its docstring-bump convention caught my reference's drift — scout SC-3); creating ancestor 338; plan FORM = 391 (reference-copy + builder + cmp-close lineage, Done 2026-08-13). Prototype guard-noise fix f1 (header rows as dups — 34 false hits, fixed, re-measured 0) caught by running the guard on real registers BEFORE pinning expectations.

**Walks (2 warm; the every-tier record-coherence line this plan ships, honored by its own cycle):**
- Weak spots:          w1 1 folded — instruction 1 / record 0 (the QA builder-currency spelling); w2 dry.
- Destruction:         w1 dry (annotation downgrades only WITH the marker; the status flips are the intended catch — no consumer reads file_status); w2 dry.
- Vulnerabilities:     w1 executed-at-authoring, dry (prototype + corpus + 27/27 + guard asserts); w2 dry.
- Integration-record:  w1 dry (bellows conventions swept); w2 dry (rows↔commits both directions).
- ACID:                w1 dry (half-states land in defined branches); w2 dry.

**Scout (Planner's call on T1; ≈128.8k):** CONVENED — 9 findings (1 HIGH / 3 MED / 5 LOW; 2 DIRECTION, neither forcing), ALL NINE folded pre-walk-1: SC-1 the probe-authored-from-prediction HIGH (would have hard-halted a correct run); SC-2 the 365 Done-status correction; SC-3 the reference docstring clone-drift (A4 re-pinned); SC-4 the QA porcelain false-FAIL channel narrowed; SC-5 the mechanical ten-file delta rule; SC-6 schema wording aligned to mechanism; SC-7 the no-table guard gap closed (+ test 8); SC-8 the marker-collision channel priced; SC-9 the every-culmination synthesis declared. Pin-attack: all clean, every measured number reproduced.

**Conformance (§5):** faithful-mirror plan_lint first run at the close (a stated T1 deviation from shape-stability timing — the plan's shape was the 391 clone from v0 and every culmination re-ran the EXECUTABLE battery instead: tests, corpus sweep, builder dry-runs; the mirror lint's own result is the close run's); close run EXIT 0; the close run's FIRST mirror was unfaithful (missing the Item-5 referenced lint script → one spurious (o1)) and the run also falsified the draft's original "no advisories" pre-classification — both corrected before the close commit (the register records the catch): final expected WARN set = the six (o2) bellows-relative advisories exactly, (q) five pins `result=ok`. Freeze item 1 re-runs it at deposit against the faithful mirror.

**Closing:** walk 2 read dry on the instruction class — **instruction 0 / record 1: this Cycle-Log fill itself, written at close** (0 of 1 fold-introduced — the fill is the close's own act, named per §2's bar); closing-record re-read run against the filled block; fold-and-deposit exactly once.
