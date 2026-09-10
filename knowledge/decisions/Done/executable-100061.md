# bellows — CLOSE THE CYCLE BY TOOL: `scripts/close_cycle.py` runs the close in its one correct order (closing line → baseline → emit → splice by key → baseline → STORED == LIVE → battery → commit) and `scripts/lens_commit.py` gates and commits one lens with a subject that names the lens — the two 2026-09-09 riders retired as code (thread 260)

**Date:** 2026-09-09 | **Project:** bellows | **Tier:** Small (two scripts, two test siblings, one mutation manifest, one dev-log) | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** full-suite (Rule 21 — the scripts subprocess-run `cycle_check`, `fold_check`, `walk_register_lint`, `lens_order_check`; `pytest tests/ -q`) | **Execution:** Step 1 (DEV) → Step 2 (QA) | **pause_for_verdict:** after_qa_step | **Discharges:** thread 260

**auto_close:** false

**Post-close:** no restart (Planner-side scripts; no daemon path imports them). No doctrine: DRAFTING_CYCLE already states the order these scripts mechanize (P5); a one-line pointer to the scripts in §2.7 is a later CEO rider if wanted.

**Depends on:** the CEO's delegation of 2026-09-09 (session d04ebd33): "draft the close tool" — cycled and deposited tonight; HOLDS on class shop-infra for the morning's release. Clone origin by kind: `Done/executable-100052.md` (scripts work: failing-first sibling, mutation run, two commits); by layout: `Done/executable-100055.md`; sibling in shape: the parked `executable-bellows-dev-side-precheck` (thread 253).

**Tier computed (§1):** **T1** — T-1 fires (two new scripts, two test siblings, a manifest: scripts and tests); T-6 does not (no gate, doctrine or daemon change — the checkers are called, not changed); T-2 does not.

## CEO Context

Three drafting cycles closed tonight and two of the three closes went wrong in the same hand-typed sequence: a splice script met the emitter's `## Cycle Manifest` header line and failed silently, so a close commit went out subject-lined "manifest spliced" with `<declare>` still in the file; then the emitter ran between the closing-line rewrite and the fold-baseline save, recorded `cycle_check=CONTINUE, fold_check=DRIFT` from that instant, and the depositor refused the deposit with `validation_mismatch:cycle_check expected=CONTINUE got=BAR_MET` (P4 — the guard working). Earlier the same evening a per-lens commit loop's subject array shifted by one and the assert that should have caught it read the loop index, not the array; four commits were rebuilt from their trees. Both are recorded as RIDERS on entries written the day before (P1). The corrected sequence was then run by hand three times without error (P2). A sequence that is fixed, mechanical, and wrong twice in one evening by hand is a script.

## What this changes

1. **`scripts/close_cycle.py <draft> --closing-file <text-file> [--register <path>] [--commit] [--dry-run]`** — runs, in this order and no other, printing one `CLOSE: <step> <result>` line per step and stopping at the first failure with exit 1: (1) replace the line beginning `**Closing:**` with the file's text (refuses if the draft has no such line or more than one); (2) `fold_check.py --save-baseline <draft>`; (3) `cycle_check.py --emit-manifest <draft>` captured; (4) splice BY KEY — for each of `yields`, `validation`, `coherence`, the emitter's `^<key>: ` line replaces the draft's `^<key>: ` line whatever its current value (`<declare>` or stale), any other emitter line (the `## Cycle Manifest` header, `tier:`, `walks:`) ignored; refuses if any of the three keys is absent from either side; (5) `fold_check.py --save-baseline <draft>` again; (6) STORED == LIVE — `cycle_check.py --emit-manifest` re-run and its `validation:` line compared byte-for-byte with the draft's; (7) the battery — `cycle_check.py <draft>` must print `BAR_MET`, `plan_lint.py <draft>` 0 FAIL, `lens_order_check.py <draft>` `LENS-ORDER OK`, and when `--register` is given `walk_register_lint.py <register> --plan <draft>` SHAPE-OK and not `COVERAGE: INCOMPLETE`; (8) with `--commit`, `git add` the draft, the register and the baseline file and commit with a subject the tool composes — `draft(<slug>): close — WARM after walk <N> (BAR_MET; T<n>); manifest spliced by key, emitted after the baseline` — never before step 6 passed. `--dry-run` runs 1–7 on a temp copy of the draft and register and touches nothing in the tree. Read-only over every tool it calls; the only files it writes are the draft, the baseline file and (with `--commit`) the git index. Two seams, both module-level and both the tests' only patch points: `run_checker(script, *args) -> (returncode, stdout)` (every checker call goes through it) and `after_step(name)` (a no-op called after each step; tests use it to edit the file between steps). The close subject's `walk <N>` and `T<n>` are read from the manifest's `walks:` and `tier:` lines, never from an argument.
2. **`scripts/lens_commit.py <draft> --register <path> --walk <N> --lens <n> --desc "<descriptor>" [--allow-yield-rising]`** — after the Planner's fold script has applied a lens: `fold_check.py --save-baseline`; `walk_register_lint.py` gate (SHAPE-OK, not INCOMPLETE); `cycle_check.py` gate (`CONTINUE` or `BAR_MET`; `ESCALATE:yield-rising` accepted ONLY with `--allow-yield-rising`, which appends the WARN line the CEO's 2026-09-09 under-seven-walks ruling requires to the register before committing, and refuses when `--walk` ≥ 7); composes the subject `draft(<slug>): walk <N> lens <n> — <LensName>: <descriptor>` from a fixed table `{1: Weak spots, 2: Destruction, 3: Vulnerabilities, 4: Integration-record, 5: ACID}` and ASSERTS the subject contains `lens <n> — <LensName>` before committing the draft, register and baseline; the descriptor is the only free text and it comes from the flag, never from an array.
3. **`tests/test_close_cycle.py`** and **`tests/test_lens_commit.py`** — fixtures under `tmp_path` built from `tests/test_cycle_check.py`'s `_make_plan` shape (P7) inside a `git init` repo; the real checkers are subprocess-run on the fixtures (no mocking of the battery); every arm failing-first (STEP 1 Item 2).
4. **`knowledge/mutants/close-cycle.json`** — at least six mutants (P8's contract).
5. **Not changed:** every checker under `scripts/`, `depositor.py`, `gates.py`, every existing test. The diff is seven new files (`git diff --stat <base>..` shows exactly the seven Scope files, the run file included).

## Why this exists

A self-reading instrument at a close must run after the artifact reaches the state it will deposit (LESSONS 2026-09-08), and its rider (2026-09-09) says the order is fixed and must be checked, not remembered. An observer that reads subjects cannot see a shifted subject; its rider says the assert must read the lens NAME. Both are one-line facts that a hand sequence forgets under fatigue and a script cannot.

## What this does NOT do

- Does not change any checker's verdict, the emitter's output, or the depositor's guard.
- Does not deposit, release or claim anything; does not run the daemon.
- Does not edit DRAFTING_CYCLE (a pointer to the scripts is a CEO rider, later).

## MUST-PRESERVE

- ⛔ **Order is the product.** Steps 1–8 run in that order; a mutant that swaps 2 and 3 or removes 6 must be killed by a test that reads the printed step sequence.
- ⛔ **No verdict re-implemented.** Every check is the checker's own stdout, matched on the checker's own token (`BAR_MET`, `CONTINUE`, `LENS-ORDER OK`, `SHAPE-OK`, `FOLD-CHECK VACUOUS`); the scripts parse tokens, never recompute them.
- ⛔ **Suite green at both commits;** nothing outside the seven files moves.

## Numbers discipline — measured 2026-09-09 by the Planner (bellows `af5ec62`, governance `7da26aaa`)

| # | pin | value | how to re-derive |
|---|---|---|---|
| P1 | ⛔ the two riders | LESSONS.md 2026-09-09: `RIDER on \`AN OBSERVER THAT READS SUBJECTS CANNOT SEE A SHIFTED SUBJECT …\` — RECURRED THE SAME EVENING: THE ASSERT CHECKED THE LENS NUMBER, WHICH THE SHIFT PRESERVES; IT MUST CHECK THE LENS NAME` and `RIDER on \`A SELF-READING INSTRUMENT AT A CLOSE MUST RUN AFTER THE ARTIFACT REACHES THE STATE IT WILL DEPOSIT\` — RECURRED: THE EMITTER RAN BETWEEN THE CLOSING REWRITE AND THE BASELINE SAVE, AND THE SPLICE … FAILED SILENTLY ON THE EMITTER'S OWN HEADER` (entries 485 and 486 of 488) | `grep -n 'RIDER on' LESSONS.md \| tail -2` |
| P2 | ⛔ the corrected sequence, run three times by hand | governance `9e324bc3` (#100057's redeposit: "manifest re-emitted AFTER the baseline save"), `9e35a214` (#100058's close), `7da26aaa` (the 258 draft's close) — each: closing line → `fold_check --save-baseline` → `cycle_check --emit-manifest` → splice by key → `--save-baseline` → `STORED == LIVE` printed → `BAR_MET` → commit; the failed forms: governance `34580567` (emit before the baseline, `validation: cycle_check=CONTINUE … fold_check=DRIFT` committed) and `81526436` ("manifest spliced" with `<declare>` still present) | `git -C <governance> show <sha> --stat`; the session transcript |
| P3 | ⛔ the checker surfaces, verbatim | `scripts/cycle_check.py`: `MANIFEST_VALIDATION_KEYS = frozenset({…})` (`:61`), `def emit_manifest(plan_path)` (`:1021`), argv `--emit-manifest <plan>` (`:1103`), usage `cycle_check.py [--emit-manifest] [--basis] <plan.md>` (`:1111`), verdict tokens `BAR_MET` / `CONTINUE` / `ESCALATE:<reason>` on the last stdout line; `scripts/fold_check.py`: `--save-baseline` (`:163`), `FOLD-CHECK VACUOUS` (`:216`), `FOLD-CHECK DRIFT` (`:234`), `ERROR: no baseline` (`:198`); `scripts/walk_register_lint.py <register> --plan <plan>` first line `<file>\tSHAPE-OK\tCOVERAGE: <COVERED\|INCOMPLETE\|UNDECLARED …>`; `scripts/lens_order_check.py <plan>` last line `LENS-ORDER OK — …` | `grep -n` as cited |
| P4 | ⛔ the depositor's guard the order protects | `depositor.py:777–783`: `val = manifest.get("validation", "")` … `expected = val.split("cycle_check=")[1].split(",")[0].strip()` … `if expected and expected != str(verdict):` → hold `validation_mismatch:cycle_check expected=<x> got=<y>`; measured live at 20:00:42 on #100057's second deposit | `sed -n 777,783p depositor.py`; `hold-…hold.json` of that deposit (withdrawn) |
| P5 | the doctrine the scripts mechanize | DRAFTING_CYCLE.md:44 "**Cadence — the self-driving walk loop (auto-advance between walks).** … After a walk's final per-lens commit, …"; `:54` "**The last event before deposit is either a dry lens pass or a declared judged stop meeting the bar above** … recorded with its reasoning"; `cycle_check.py:430` "Do NOT pass warnings on the --emit-manifest path: that call only fills the …"; the manifest keys rule cited in `cycle_check.py` as "DC:253, P2-P8" | `sed -n 44p;54p DRAFTING_CYCLE.md` |
| P6 | ⛔ the lens-commit shape as run tonight (55 lens commits, three cycles) | `fold_check --save-baseline` → `walk_register_lint` → `cycle_check` → gate `[[ $LINT == *SHAPE-OK* ]] && [[ $LINT != *"COVERAGE: INCOMPLETE"* ]] && [[ $CC == CONTINUE* \|\| $CC == BAR_MET* ]]` → subject `draft(<slug>): walk $W lens $i — ${DESC[$i]}` asserted with `[[ $MSG == *"lens $i — ${NAME[$i]}"* ]]` over `declare -A` tables → `git add <draft> <register> <baseline> && git commit`; the yield-rising case at #100057's walk 4: five commits accepted `ESCALATE:yield-rising` under the CEO's ruling with a WARN line appended to the register first | the session transcript; `git -C <governance> log --oneline -60 \| grep 'lens'` |
| P7 | test conventions | `tests/test_cycle_check.py::_make_plan` (a plan-text builder; 91 cross-file callers in the walk-0 anvil build), `tests/test_fold_check.py`, `tests/test_lens_order_check.py`, `tests/test_walk_register_lint.py` exist and subprocess-run the checkers on `tmp_path` fixtures; `tests/conftest.py` autouse fixtures isolate verdicts, runner logs, the lifecycle DB and the notifier memo | `ls tests`; `grep -n 'def _make_plan' tests/test_cycle_check.py` |
| P8 | the mutation contract; class; in-flight | `tools/mutation_check.py`: manifest-driven, `expect_fail` a pytest node id, KILLED = exit 1 only; run file `knowledge/mutants/<slug>.run.txt` ending `MUTATION: N killed, 0 survived, 0 error`; this plan writes `scripts/` and `tests/` → **shop-infra** (HOLDS; the CEO releases in the morning — not tonight); at drafting #100058 is in flight, the 258 diagnostic waits behind it; this plan deposits after both | `sed -n 1,22p tools/mutation_check.py`; `python3 status.py` |

## Drafting Cycle

**Tier:** **T1** — T-1 fires. **Walk register:** /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-close-cycle-tool-2026-09-09.md
**Walks:** walk 0 pinned (P1–P8 measured on bellows `af5ec62`, governance `7da26aaa`; clone-diff against `Done/executable-100052.md` (kind) and `Done/executable-100055.md` (layout) run: FACTS, ARTEFACTS, STRUCTURE); `fold_check --save-baseline` ARMED on v0 before any fold; re-saved after every intended edit.

**Closing:** WARM close after walk 4 — thread 260's plan, a judged stop. The first close (after walk 2) was reopened on the Planner's read-back (f6, a count contradiction; walk 3's yield-rising escalate continued under the CEO's under-seven-walks ruling, register WARN). Four walks: instruction 4 → 0 → 1 → 0. T1, no panel. Deposit via `ready-` tonight; HOLDS on class shop-infra (writes under `scripts/` and `tests/`); the CEO releases in the morning — the overnight delegation did not include releases. Close acts: none beyond the release; a §2.7 pointer to the scripts is a later CEO rider.
- Weak spots:          w1 3 folded — instruction 3 / record 0
- Destruction:         w1 dry
- Vulnerabilities:     w1 1 folded — instruction 1 / record 0
- Integration-record:  w1 dry
- ACID:                w1 dry
- Weak spots:          w2 dry
- Destruction:         w2 dry
- Vulnerabilities:     w2 dry
- Integration-record:  w2 dry
- ACID:                w2 dry
- Weak spots:          w3 1 folded — instruction 1 / record 0
- Destruction:         w3 dry
- Vulnerabilities:     w3 dry
- Integration-record:  w3 dry
- ACID:                w3 dry
- Weak spots:          w4 dry
- Destruction:         w4 dry
- Vulnerabilities:     w4 dry
- Integration-record:  w4 dry
- ACID:                w4 dry
**Walk 4 — DRY, all five lenses, one commit per lens. Instruction 0 on a full pass: the WARM close meets the bar (§2) — a judged stop (5 findings over three warm walks plus f0; yield 4 → 0 → 1 → 0). T1: no panel owed.**
**Walk 3 — one fold at lens 1 (instruction 1 / record 0), four lenses dry; reopened after the first close. Instruction non-zero: walk 4 owed.**
**Walk 2 — DRY, all five lenses, one commit per lens. Instruction 0 on a full pass: the first WARM close (REOPENED on read-back — f6, walk 3) — a judged stop (4 findings over one warm walk plus f0; yield 4 → 0). T1: no panel owed.**
**Walk 1 — four folds across two lenses (instruction 4 / record 0), three lenses dry; one commit per lens.**

## Cycle Manifest
tier: T1
target: scripts/close_cycle.py
class: shop-infra
reads: scripts/cycle_check.py, scripts/fold_check.py, scripts/walk_register_lint.py, scripts/lens_order_check.py, scripts/plan_lint.py, depositor.py, tests/test_cycle_check.py, tests/test_fold_check.py, tests/conftest.py, tools/mutation_check.py, knowledge/decisions/Done/executable-100052.md, knowledge/decisions/Done/executable-100055.md, DRAFTING_CYCLE.md, LESSONS.md
writes: scripts/close_cycle.py, scripts/lens_commit.py, tests/test_close_cycle.py, tests/test_lens_commit.py, knowledge/mutants/close-cycle.json, knowledge/mutants/close-cycle.run.txt, knowledge/development/dev-log-close-cycle-tool-2026-09-09.md, knowledge/qa/evidence/close-cycle-tool-qa-evidence-2026-09-09.md, knowledge/qa/evidence/close-cycle-tool-suite-2026-09-09.txt
open_forks: 1. a DRAFTING_CYCLE §2.7 pointer to the two scripts (CEO rider); 2. `lens_commit.py` learning the fold script itself (`--fold <script> <args>`) so the fold and its commit are one act; 3. the yield-rising acceptance moved from a flag to the checker when thread 250 ships (then the flag is deleted, not kept)
walks: 4
yields: 4, 0, 1, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=VACUOUS, propagation_check=DIVERGENT:3
coherence: 4/4 body walks named in the register (6 register rows; walk-token match, NOT row coverage)
fold_baseline: governance/knowledge/decisions/drafts/.executable-bellows-close-cycle-tool.md.foldcheck.json

---

## STEP 1 — DEV (two scripts, two siblings, one manifest; the mutation run; two commits)

> ⛔ **Every item starts by re-establishing the root** — `cd "$(git rev-parse --show-toplevel)" && test -f gates.py && echo TREE_OK` — HALT unless TREE_OK. ⛔ **The interpreter is `/Users/marklehn/Developer/bellows/.venv/bin/python`, ABSOLUTE.** ⛔ Never run the daemon, `run_plan`, a claim; never import `lifecycle`; the scripts call the checkers by subprocess with this interpreter and the repo-relative `scripts/<checker>.py`, resolved from the script's own `__file__` (`os.path.dirname(os.path.abspath(__file__))`), never from the cwd.
>
> **Scope:**
> - `scripts/close_cycle.py`
> - `scripts/lens_commit.py`
> - `tests/test_close_cycle.py`
> - `tests/test_lens_commit.py`
> - `knowledge/mutants/close-cycle.json`
> - `knowledge/mutants/close-cycle.run.txt`
> - `knowledge/development/dev-log-close-cycle-tool-2026-09-09.md`
>
> **Item 1 — re-derive P3 and P4 and HALT on a mechanism mismatch** (P1, P2, P5–P8 are records; a line-number drift is not a mismatch, a changed token, argv or key set is). Paste the `MANIFEST_VALIDATION_KEYS` literal, the `--emit-manifest` argv branch, the `FOLD-CHECK VACUOUS`/`DRIFT` print lines and `depositor.py:777–783` under the first declared heading.
> **Item 2 — write the failing tests FIRST.** `tests/test_close_cycle.py`, each test building a minimal T1 draft with `_make_plan`'s shape (a `## Cycle Manifest` with `yields: <declare>` / `validation: <declare>` / `coherence: <declare>` and a `fold_baseline:` line, a `**Closing:** not reached.` line, a five-lens walk-1 dry block) plus a matching register, in a `git init` repo under `tmp_path`, and driving `close_cycle.main(argv)`: (c1) the happy path prints the eight `CLOSE:` lines in order and exits 0 with `STORED == LIVE` and the three keys spliced; (c2) an emitter output carrying the `## Cycle Manifest` header line (the rider's first case — returned by a monkeypatched `run_checker` for the emit step) still splices the three keys and ignores the rest; (c3) the order — with `--dry-run`, the printed step sequence equals the fixed list `closing, baseline, emit, splice, baseline, stored==live, battery, commit(skipped)`; (c4) a draft whose stored `validation:` differs from the live emit after step 5 (an `after_step("baseline")` patched to edit the draft's `validation:` line) exits 1 at `stored==live` and does not commit; (c5) a draft with no `**Closing:**` line exits 1 at step 1, file untouched; (c6) `--commit` produces one commit whose subject starts `draft(<slug>): close —` and whose tree contains the draft, register and baseline. `tests/test_lens_commit.py`: (l1) the subject is `draft(<slug>): walk 1 lens 3 — Vulnerabilities: <desc>` for `--lens 3`, from the table, and the assert passes; (l2) a monkeypatched table entry that returns the wrong name makes the assert refuse before any commit (the rider's case); (l3) `ESCALATE:yield-rising` from the checker refuses without the flag, and with `--allow-yield-rising --walk 4` appends a line beginning `**WARN (walk 4):**` to the register and commits; (l4) `--allow-yield-rising --walk 7` refuses; (l5) a register lint `COVERAGE: INCOMPLETE` refuses. Run: all eleven red for the right reason (`ModuleNotFoundError`), pasted under the second declared heading.
> **Item 3 — the two scripts** as *What this changes* 1–2, then the eleven tests green; the FULL suite green.
> **Item 4 — first commit**, gated in one command on the FULL suite's exit code and path-scoped: `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ -q && git add scripts/close_cycle.py scripts/lens_commit.py tests/test_close_cycle.py tests/test_lens_commit.py && git commit -F <msg-file> -- scripts/close_cycle.py scripts/lens_commit.py tests/test_close_cycle.py tests/test_lens_commit.py` — four files; the message tagged with the plan id and `thread 260`.
> **Item 5 — the mutation run, REDIRECTED into `knowledge/mutants/close-cycle.run.txt` (a Deposit):** the manifest `knowledge/mutants/close-cycle.json` with at least six mutants — steps 2 and 3 swapped (c3), step 6 removed (c4), the splice matching the header line as a key (c2), the closing-line refusal inverted (c5), the lens table's entry 3 renamed (l2), the `--walk` ≥ 7 refusal removed (l4) — each `expect_fail` a node id from the siblings; `/Users/marklehn/Developer/bellows/.venv/bin/python tools/mutation_check.py knowledge/mutants/close-cycle.json > knowledge/mutants/close-cycle.run.txt 2>&1`; the last line must read `MUTATION: <n> killed, 0 survived, 0 error` with n ≥ 6 — a survivor is a test to write, not a mutant to delete.
> **Item 6 — the dev-log** `knowledge/development/dev-log-close-cycle-tool-2026-09-09.md` under the four headings declared below; `## Pins re-derived (P3, P4)` opens with P4's value cell pasted verbatim, whole, to its last character — ⛔ the VALUE cell (the third column) ends with the words `on #100057's second deposit`; paste through those words, then stop — the fourth column (`sed -n 777,783p …`) is not part of it. **Second commit**, gated on the FULL suite AND the run file, path-scoped: `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ -q && grep -Eq 'MUTATION: ([6-9]|[1-9][0-9]+) killed, 0 survived, 0 error' knowledge/mutants/close-cycle.run.txt && git add knowledge/mutants/close-cycle.json knowledge/mutants/close-cycle.run.txt knowledge/development/dev-log-close-cycle-tool-2026-09-09.md && git commit -F <msg-file> -- knowledge/mutants/close-cycle.json knowledge/mutants/close-cycle.run.txt knowledge/development/dev-log-close-cycle-tool-2026-09-09.md`.
> **Headings:** `## Pins re-derived (P3, P4)`; `## Failing-first (eleven red, then green)`; `## The order, printed (c3's sequence)`; `## Mutation run`
> **Verbatim:** `## Pins re-derived (P3, P4)` ← P4
>
> **Deposits:**
> - `scripts/close_cycle.py`
> - `scripts/lens_commit.py`
> - `tests/test_close_cycle.py`
> - `tests/test_lens_commit.py`
> - `knowledge/mutants/close-cycle.json`
> - `knowledge/mutants/close-cycle.run.txt`
> - `knowledge/development/dev-log-close-cycle-tool-2026-09-09.md`
>
> **Post-conditions:** eleven tests across the two siblings, all green; the mutation run file's last line `MUTATION: n killed, 0 survived, 0 error` with n ≥ 6; `git diff --stat main..HEAD` names exactly the seven Scope files; the four declared headings present as full lines with P4's cell whole; no checker, `depositor.py`, `gates.py` or existing test changed.

## STEP 2 — QA (full suite + the close tool replayed on tonight's three real closes)

> ⛔ Root re-established as in STEP 1; interpreter ABSOLUTE; read-only beyond the two evidence files; the governance drafts are read with `git -C /Users/marklehn/Developer/eluvian-governance show <sha>:<path>` into a scratch dir, never from the working tree.
>
> **Item 1 — full suite, REDIRECTED not piped:** `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ --tb=short -q > knowledge/qa/evidence/close-cycle-tool-suite-2026-09-09.txt 2>&1`; the summary line quoted in the receipt.
> **Item 2 — the three corrected closes replayed (P2):** for each of governance `9e324bc3`, `9e35a214`, `7da26aaa`, take the draft and its register at the commit BEFORE the close (`<sha>~1`) into `$T`, extract the closing text from `<sha>`'s draft into a file, run `scripts/close_cycle.py <copy> --closing-file <text> --register <copy-register> --dry-run`; expected: eight `CLOSE:` lines, `STORED == LIVE`, `BAR_MET`, and the spliced `validation:` line equal to the one committed at `<sha>` — paste all three.
> **Item 3 — the two failed closes replayed (P2):** the same on `34580567~1` with the closing text from `34580567` — expected: the tool's own `validation:` line reads `cycle_check=BAR_MET … fold_check=VACUOUS` where the hand close committed `CONTINUE … DRIFT` (the tool orders the baseline before the emit); and on `81526436~1` — expected: the three keys spliced where the hand close left `<declare>`. Paste both diffs.
> **Item 4 — the lens-commit assert on the rider's case:** in a scratch `git init` copy of any tonight's draft at a mid-walk commit, run `scripts/lens_commit.py <draft> --register <r> --walk 1 --lens 2 --desc "Weak spots: …"` (a lens-1 descriptor under `--lens 2`) — expected: the subject the tool composes is `… walk 1 lens 2 — Destruction: Weak spots: …`, which the assert ACCEPTS (the name is the table's); state in the receipt that the descriptor's own words are not checked and why that is the designed boundary (the rider's defect was the NAME, supplied by the array; the tool supplies it from the table).
> **Item 5 — production writes, stated exactly:** none outside the two evidence files; no lane file, no lifecycle row, no lifecycle import; every scratch dir removed (`[ -n "$T" ] && [ -d "$T" ] && rm -rf "$T"`).
> **Item 6 — receipt** `knowledge/qa/evidence/close-cycle-tool-qa-evidence-2026-09-09.md`: `numstat` over the DEV commits (`<base>..<dev>`, seven files); opens with the whole-line banner `Rule 20 — QA Self-Check Results`, carries a `## Verification` table with one row per Item 1–5, each quoting the line it rests on, and closes with the whole line `PASSED — SELF-CHECK PASSED` only when every row passes (a failing row makes the closing line `FAILED — SELF-CHECK FAILED` and the step pauses on it); the quoted node ids limited to the siblings' methods.
> **Item 7 — commit**, path-scoped and gated: `grep -Eq '^[0-9]+ passed' knowledge/qa/evidence/close-cycle-tool-suite-2026-09-09.txt && ! grep -Eq '[0-9]+ (failed|error)' knowledge/qa/evidence/close-cycle-tool-suite-2026-09-09.txt && git add knowledge/qa/evidence/close-cycle-tool-qa-evidence-2026-09-09.md knowledge/qa/evidence/close-cycle-tool-suite-2026-09-09.txt && git commit -F <msg-file> -- knowledge/qa/evidence/close-cycle-tool-qa-evidence-2026-09-09.md knowledge/qa/evidence/close-cycle-tool-suite-2026-09-09.txt`.
>
> **Deposits:**
> - `knowledge/qa/evidence/close-cycle-tool-qa-evidence-2026-09-09.md`
> - `knowledge/qa/evidence/close-cycle-tool-suite-2026-09-09.txt`
>
> **Scope:**
> - `knowledge/qa/evidence/close-cycle-tool-qa-evidence-2026-09-09.md`
> - `knowledge/qa/evidence/close-cycle-tool-suite-2026-09-09.txt`
>
> **Post-conditions:** the suite file's summary line is `N passed` with N ≥ the DEV's count; Items 2–3 reproduce the three good closes and the two failed ones with the tool's lines pasted; the receipt's `## Verification` table has five rows; one QA commit carrying the two evidence files.
