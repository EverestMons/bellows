# bellows — `close_cycle.py` SPLICES `walks:` WITH THE OTHER EMITTED KEYS AND REACHES STORED == LIVE AS A FIXED POINT: when the re-emit differs only in `propagation_check` (the spliced lines are what it counts), the tool re-splices once and re-checks, so the first close of a draft commits — the two closes that failed their first pass today and the `walks: 0` a record shipped with (threads 269, 272)

**Date:** 2026-09-10 | **Project:** bellows | **Tier:** Small (one script: one key added to a tuple, one step made a fixed point; one test file gains three tests; one mutation manifest; one dev-log) | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** full-suite (Rule 21 — the tool subprocess-runs four checkers and every close uses it; `pytest tests/ -q`) | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** after_qa_step | **known_failures:** 0 | **Discharges:** thread 269, thread 272

**auto_close:** false

**Post-close:** no restart (`close_cycle.py` is Planner-side, run per invocation). One doctrine clause for the CEO's word at close: DRAFTING_CYCLE:221's close sequence (`closing line → baseline → emit → splice by key → baseline → STORED == LIVE → battery → commit`, v2.34) gains "(four keys — `walks` too; STORED == LIVE reached as a fixed point when only the propagation count moved)" as v2.36 — the v2.35 pattern. §3's manifest contract is unchanged: `walks:` was always an emitted key; the tool simply never wrote it.

**Depends on:** bellows #100061 (Done 2026-09-10, thread 260 — the tool; its item 2 named "the three keys", the origin of thread 269) and #100064 (Done 2026-09-10 — the tool's last writer: the `plan_lint` echo in step 7); the four closes of 2026-09-10 that measured both defects (P1); the CEO's "Let's continue" (2026-09-10 evening) after the four tooling T1s. Clone origin by kind: `Done/executable-100061.md` (the same tool and test file); by layout: the closed 271 draft. In flight: none; the 271 draft (`scripts/lens_commit.py`, `tests/test_lens_commit.py`) shares no file with this one.

**Tier computed (§1):** **T1** — T-1 fires (one script, one test file); T-6 does NOT fire — Planner-side tool, no daemon gate changes (100061's reasoning); T-2 does not.

## CEO Context

Two defects in the close tool, both measured twice on 2026-09-10. Thread 269: `cycle_check --emit-manifest` prints four values the manifest owns — `walks:`, `yields:`, `validation:`, `coherence:` — and `close_cycle.py` splices three (`_SPLICE_KEYS`, P2), so a draft whose author forgot to set `walks:` by hand shipped `walks: 0` in its Done record (#100064's first close) and every close since has needed a `sed` before the tool. Thread 272: the tool emits at step 3, splices at step 4, and at step 6 re-emits to prove STORED == LIVE — but the spliced lines are tokens `propagation_check` counts, so the re-emit's `validation:` line differs in that one number (`DIVERGENT:61` vs `:65`, `:45` vs `:46`), the step fails, and the first run leaves the draft EDITED and UNCOMMITTED; a second run passes because the emitter now reads the spliced text. Twice today a deposit was made in that window on bytes no commit held and had to be withdrawn. Both halves are one plan because they touch the same two steps: splice the fourth key, and make the STORED == LIVE step converge instead of failing on its own side effect — one re-splice when ONLY `propagation_check` moved, a real failure for anything else (the 201 lesson the step exists for: a stale emit).

## What this changes

1. **`scripts/close_cycle.py`** — (a) `_SPLICE_KEYS = ("walks", "yields", "validation", "coherence")` (`:30`; `_splice_keys` `:59–96` then requires `walks:` from the emitter and in the draft, as it does the other three — the emitter prints `walks: N` at `cycle_check.py:1089`; `_compose_subject` `:113–125` and the register seal `:249–255` already read `walks:` from the emit output, unchanged). The docstring's step-4 line becomes `4. splice — walks/yields/validation/coherence by key`. (b) **Step 6 as a fixed point** (`:214–230`): after the re-emit, the stored and live `validation:` lines are compared TOKEN by token (`cycle_check=`, `plan_lint=`, `fold_check=`, `propagation_check=`, split on `, `); if they differ in `propagation_check` ONLY, the tool prints `CLOSE: stored==live NOTE — propagation_check moved <a>→<b> (the spliced lines are counted); re-splicing once`, splices the live emit output (the same `_splice_keys`), re-saves the baseline (`fold_check --save-baseline`), re-emits and compares again — this second comparison must be byte-equal or the step FAILS with today's message; if the first difference is in any other token, or the two lines' KEY SETS differ (an older manifest with fewer pairs), the step FAILS as today — the comparison stays on the `validation:` line alone, as shipped; `walks:`/`yields:`/`coherence:` are not compared (they read the lens lines and the register, which the splice does not touch — widening the check was considered at walk 1 and refused as a new gate) (`CLOSE: stored==live FAIL — stored … != live …`). `CLOSE: stored==live OK` prints on equality at either pass. The docstring's step-6 line becomes `6. stored==live — re-emit and compare; one re-splice when only propagation_check moved`.
2. **`tests/test_close_cycle.py`** — three tests, failing-first, on `_make_fixture` / `_closing_file` (8 tests today, P3; this plan's are c9–c11): **c9** (thread 269): after `main([...])` on the fixture, `plan.md` carries `walks: 1` (the emitter's count for the fixture's one lens walk) and no `walks: <declare>`; c1's assert list gains the same line. **c10** (thread 272, the fixed point): monkeypatch `close_cycle.run_checker` for `cycle_check.py --emit-manifest` only (the c2/c4 pattern) with a fake whose `propagation_check` count is `DIVERGENT:10` on its first call and `DIVERGENT:14` on every later call (the other tokens fixed; the fake answers only the `--emit-manifest` calls and delegates the battery's plain `cycle_check.py` call and every other checker to the real function, the c2/c4 pattern) → rc 0, stdout carries `stored==live NOTE — propagation_check moved 10→14` then `stored==live OK`, and `plan.md`'s `validation:` line carries `DIVERGENT:14`. **c11** (a real drift still fails): the same fake but `cycle_check=BAR_MET` on the first call and `cycle_check=CONTINUE` on the second → rc 1, `stored==live FAIL`, no `NOTE`. c4 (`stored != live → exit 1`, P3) is read at Item 1: if its fake differs only in the propagation count it is re-pointed to a `cycle_check=` difference (its docstring says "stored != live", not which token — the DEV says which it was).
3. **`knowledge/mutants/close-cycle-walks-and-fixed-point.json`** — at least four mutants (`target: scripts/close_cycle.py`; every `expect_fail` a plain `tests/test_close_cycle.py::<test>` node id): `walks` dropped from the tuple (c9); the re-splice removed (c10 — the first pass then fails); the token comparison widened to ignore every token (c11 — the drift passes); the second comparison after the re-splice removed (c10's fake made to keep moving on a third call — the DEV adds that variant to c10 or as c10b, so the mutant is killable).
4. **Not changed:** `cycle_check.py` (its emitter and count are read, not changed), steps 1–5, 7 and 8, `_compose_subject`, the register seal, every other test. The diff touches two files plus the manifest, the run file and the dev-log.

## Why this exists

A close tool that fails on the side effect of its own splice is a tool every author learns to run twice, and the window between the runs is where today's two un-held deposits came from. `walks:` is the one emitted key the tool left to memory, and memory shipped a zero. The STORED == LIVE step keeps its purpose — a stale emit fails — and stops failing on itself.

## What this does NOT do

- Does not change what the emitter prints or counts; does not make `propagation_check` a gate (DC v2.29: DIVERGENT is informational).
- Does not retry more than once: a count that keeps moving after one re-splice is a real instability and fails.
- Does not touch `lens_commit.py` (the 271 draft's file).

## MUST-PRESERVE

- ⛔ **A stale emit still fails.** Only a `propagation_check`-only difference earns the one re-splice; c11 pins it.
- ⛔ **One re-splice, then byte equality.** The second comparison is exact.
- ⛔ **Suite green at both commits;** nothing outside the two files moves.

## Numbers discipline — measured 2026-09-10 by the Planner (bellows `ba74706`, governance `88f42fa6`)

| # | pin | value | how to re-derive |
|---|---|---|---|
| P1 | ⛔ the two defects, measured | thread 269: #100064's first close (governance `f08f3b9c`'s predecessor) shipped `walks: 0` until a `sed` set it; every close since ran `sed -i '' 's/^walks: 0$/walks: N/'` first. Thread 272: the 270 close — `CLOSE: stored==live FAIL — stored '… propagation_check=DIVERGENT:61' != live '… DIVERGENT:65'`, the second run `commit OK`; the 266 close — `DIVERGENT:45` vs `:46`, the second run `commit OK`; the first 270 deposit carried the pre-close bytes and was withdrawn (`withdrawn/270-1st/`) | the closes' transcripts in the session's registers (`walk-register-lens-record-visibility-2026-09-10.md`, `walk-register-lens-commit-accepts-continue-2026-09-10.md`) |
| P2 | ⛔ the tool as it stands | `scripts/close_cycle.py` (sha `054ac75a583e`, last writer `9447208` #100064): `_SPLICE_KEYS = ("yields", "validation", "coherence")` `:30`; `_splice_keys(draft_text, emit_stdout)` `:59–96` (collects `key: ` lines from the emit, replaces the draft's lines by key, errors on a key missing from either side); `_compose_subject` `:113–125` reads `walks:` and `tier:` from the emit output; step 3 `:188–194` emit (captured as `emit_out`); step 4 `:196–204` splice; step 5 `:206–212` baseline; step 6 `:214–230` re-emit and whole-line comparison of `validation:`; step 7 `:232–242` battery; step 8 `:244–` the register seal from `emit_out`'s `walks:` and the commit | `sed -n '30p;59,96p;113,125p;188,230p' scripts/close_cycle.py` |
| P3 | ⛔ the tests as they stand | `tests/test_close_cycle.py`: 8 tests — c1 happy path (asserts the eight-step sequence and the three `<declare>` keys gone), c2 emitter header ignored, c3 dry-run order, c4 `stored != live → exit 1` (monkeypatched `run_checker`), c5 no closing line, c6 commit, c7 `plan_lint` WARN echo, c8 `plan_lint` FAIL refuses; `_make_fixture(tmp_path)` `:80` (a git repo with `plan.md` = `_INITIAL_PLAN` whose manifest has `walks: <declare>`, `register.md`, five lens commits), `_closing_file` `:106` | `grep -n 'def test_\|def _' tests/test_close_cycle.py` |
| P4 | the emitter | `scripts/cycle_check.py:1021` `emit_manifest(plan_path)`: prints `tier:`, `target:`, …, `walks: {walk_count}` `:1089`, `yields:`, `validation:` (the battery's four tokens joined by `, `), `coherence:`; `propagation_check`'s count is a token count over the plan text, so the spliced lines change it (v2.29: DIVERGENT is informational, never a downgrade) | `sed -n 1021,1100p scripts/cycle_check.py` |
| P5 | the mutation contract; class; in-flight | `tools/mutation_check.py`: manifest-driven, KILLED = exit 1 only, sandbox = `git archive HEAD`; run file `knowledge/mutants/<slug>.run.txt` ending `MUTATION: N killed, 0 survived, 0 error`; this plan writes `scripts/` and `tests/` → **shop-infra** (HOLDS, the CEO releases); in flight: none (daemon pid 70398, HEAD `ba74706`); the 271 draft shares no file | `python3 status.py` |

## Drafting Cycle

**Tier:** **T1** — T-1 fires. **Walk register:** /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-close-cycle-walks-and-fixed-point-2026-09-10.md
**Walks:** walk 0 pinned (P1–P5 measured on bellows `ba74706`; clone-diff against `Done/executable-100061.md` (kind) and the closed 271 draft (layout) run: FACTS, ARTEFACTS, STRUCTURE); `fold_check --save-baseline` ARMED on v0 before any fold; re-saved after every intended edit; every lens commit through `scripts/lens_commit.py`; the tool run bare, its exit read; no lens or walk number in any `--desc`.

- Weak spots:          w1 2 folded — instruction 1 / record 1 (QA Item 2 reads the clone's draft, not a dry-run's temp copy; the register's Draft: line); w2 dry

- Destruction:         w1 1 folded — instruction 1 / record 0 (the comparison stays on validation: alone; a differing key set fails); w2 dry

- Vulnerabilities:     w1 1 folded — record 1 (c10's fake delegates the battery's plain cycle_check call); w2 dry

- Integration-record:    w1 dry; w2 dry

- ACID:                  w1 dry; w2 dry

**Closing:** WARM close after walk 2 — BAR MET (T1), threads 269 and 272's plan. Two walks: the walk-1 folds → 0 (walk 2 fully dry). Every lens commit through `lens_commit.py` (folding lenses under the CONTINUE it now accepts — #100065; dry lenses under `--dry`), the tool run bare, its exit read, the observer after each walk; no lens or walk number in any `--desc`. `walks:` set by hand for the last time (thread 269 is this pair). Deposit via `ready-`; HOLDS on class shop-infra, released on the CEO's behalf under the 2026-09-10 delegation.

## Cycle Manifest
tier: T1
target: scripts/close_cycle.py
class: shop-infra
reads: scripts/close_cycle.py, scripts/cycle_check.py, tests/test_close_cycle.py, tools/mutation_check.py, knowledge/decisions/Done/executable-100061.md, DRAFTING_CYCLE.md
writes: scripts/close_cycle.py, tests/test_close_cycle.py, knowledge/mutants/close-cycle-walks-and-fixed-point.json, knowledge/mutants/close-cycle-walks-and-fixed-point.run.txt, knowledge/development/dev-log-close-cycle-walks-and-fixed-point-2026-09-10.md, knowledge/qa/evidence/close-cycle-walks-and-fixed-point-qa-receipt-2026-09-10.md, knowledge/qa/evidence/close-cycle-walks-and-fixed-point-suite-2026-09-10.txt
mutants: knowledge/mutants/close-cycle-walks-and-fixed-point.json
open_forks: 1. the emitter excluding the manifest's own lines from `propagation_check`'s count (a `cycle_check` change — then the fixed point is reached on the first pass by construction; its own plan); 2. `close_cycle.py` refusing when `walks:` in the draft disagrees with the emitter's count before the splice (a hand-set value overwritten silently — after one measured instance)
walks: 2
yields: 2, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=VACUOUS, propagation_check=DIVERGENT:11
coherence: 2/2 body walks named in the register (4 register rows; walk-token match, NOT row coverage)
fold_baseline: governance/knowledge/decisions/drafts/.executable-bellows-close-cycle-walks-and-fixed-point.md.foldcheck.json

---

## STEP 1 — DEV (one key, one fixed point, three tests; the mutation run; two commits)

> ⛔ **Every item starts by re-establishing the root** — `cd "$(git rev-parse --show-toplevel)" && test -f gates.py && echo TREE_OK` — HALT unless TREE_OK. ⛔ **The interpreter is `/Users/marklehn/Developer/bellows/.venv/bin/python`, ABSOLUTE.** ⛔ Never run the daemon, `run_plan`, a claim; never import `lifecycle`. ⛔ Every deposit is written in THIS worktree (`"$(git rev-parse --show-toplevel)"`), never in the canonical checkout; the plan's own lane file lives in the canonical checkout at `/Users/marklehn/Developer/bellows/knowledge/decisions/in-progress-executable-<id>.md` (`<id>` from the prompt).
>
> **Scope:**
> - `scripts/close_cycle.py`
> - `tests/test_close_cycle.py`
> - `knowledge/mutants/close-cycle-walks-and-fixed-point.json`
> - `knowledge/mutants/close-cycle-walks-and-fixed-point.run.txt`
> - `knowledge/development/dev-log-close-cycle-walks-and-fixed-point-2026-09-10.md`
>
> **Item 1 — re-derive P2, P3 and P4 and HALT on a mechanism mismatch** (P1 and P5 are records; a line-number drift is not a mismatch, a `_SPLICE_KEYS` already holding `walks`, a step 6 already token-wise, or an emitter not printing `walks:` is). Paste `_SPLICE_KEYS`, step 6, the emitter's `walks:` line, the eight test names and c4's fake (which token it moves) under the first declared heading. Then reproduce P1's second defect on the fixture: run the shipped tool with a fake emitter (c10's shape) → `stored==live FAIL` on the first pass; paste the line.
> **Item 2 — write the failing tests FIRST:** *What this changes* 2 — c9, c10, c11, and c1's added assert. Run the file: c9 red (`walks: <declare>` survives the close), c10 red (`stored==live FAIL` where OK was expected), c11 GREEN before the edit (it pins today's refusal of a real drift — say so), c1 red on its new assert; c2–c8 green. Paste under the second declared heading.
> **Item 3 — the edit** as *What this changes* 1; then the file green (11 tests), then the FULL suite green (`N passed, 1 skipped` — `test_gate_watcher` skips in a worktree; a skip is not a failure).
> **Item 4 — first commit**, gated on the FULL suite AND the pre-check with the stage flag (#100067), path-scoped: `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ -q && /Users/marklehn/Developer/bellows/.venv/bin/python tools/check_deposit.py /Users/marklehn/Developer/bellows/knowledge/decisions/in-progress-executable-<id>.md 1 --wt "$(git rev-parse --show-toplevel)" --expect-missing knowledge/development/dev-log-close-cycle-walks-and-fixed-point-2026-09-10.md knowledge/mutants/close-cycle-walks-and-fixed-point.run.txt && git add scripts/close_cycle.py tests/test_close_cycle.py knowledge/mutants/close-cycle-walks-and-fixed-point.json && git commit -F <msg-file> -- scripts/close_cycle.py tests/test_close_cycle.py knowledge/mutants/close-cycle-walks-and-fixed-point.json` — three files (the manifest rides this commit so the mutation run's `HEAD:` archive contains it); the message tagged with the plan id and `threads 269, 272`; the paste MUST contain `PRECHECK: 0 failure(s) — … (expecting 2 missing)`.
> **Item 5 — the mutation run, REDIRECTED into `knowledge/mutants/close-cycle-walks-and-fixed-point.run.txt` (a Deposit):** `/Users/marklehn/Developer/bellows/.venv/bin/python tools/mutation_check.py knowledge/mutants/close-cycle-walks-and-fixed-point.json > knowledge/mutants/close-cycle-walks-and-fixed-point.run.txt 2>&1`; the last line must read `MUTATION: <n> killed, 0 survived, 0 error` with n ≥ 4 — a survivor is a test to write, not a mutant to delete.
> **Item 6 — the dev-log** `knowledge/development/dev-log-close-cycle-walks-and-fixed-point-2026-09-10.md` under the four headings declared below; `## Pins re-derived (P2, P3, P4)` opens with P2's value cell pasted verbatim, whole, to its last character — ⛔ the VALUE cell (third column) ends with the words `` `walks:` and the commit ``; paste through those words, then stop. **Second commit**, gated on the FULL suite AND the run file AND the pre-check run BARE, path-scoped: `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ -q && grep -Eq 'MUTATION: ([4-9]|[1-9][0-9]+) killed, 0 survived, 0 error' knowledge/mutants/close-cycle-walks-and-fixed-point.run.txt && /Users/marklehn/Developer/bellows/.venv/bin/python tools/check_deposit.py /Users/marklehn/Developer/bellows/knowledge/decisions/in-progress-executable-<id>.md 1 --wt "$(git rev-parse --show-toplevel)" && git add knowledge/mutants/close-cycle-walks-and-fixed-point.run.txt knowledge/development/dev-log-close-cycle-walks-and-fixed-point-2026-09-10.md && git commit -F <msg-file> -- knowledge/mutants/close-cycle-walks-and-fixed-point.run.txt knowledge/development/dev-log-close-cycle-walks-and-fixed-point-2026-09-10.md` — two files.
> **Headings:** `## Pins re-derived (P2, P3, P4)`; `## Failing-first (three red, one pinned, then green)`; `## The first-pass failure reproduced (Item 1)`; `## Mutation run`
> **Verbatim:** `## Pins re-derived (P2, P3, P4)` ← P2
>
> **Deposits:**
> - `scripts/close_cycle.py`
> - `tests/test_close_cycle.py`
> - `knowledge/mutants/close-cycle-walks-and-fixed-point.json`
> - `knowledge/mutants/close-cycle-walks-and-fixed-point.run.txt`
> - `knowledge/development/dev-log-close-cycle-walks-and-fixed-point-2026-09-10.md`
>
> **Post-conditions:** three new tests green and the eight prior green (c1 with its added assert; c4 re-pointed if it moved only the propagation count); the fixture closes on the FIRST pass with `walks: 1` spliced; a propagation-only drift re-splices once and passes; a `cycle_check=` drift fails; the mutation run's last line `n ≥ 4 killed, 0 survived, 0 error`; `git diff --stat main...HEAD` (three-dot) names exactly the five Scope files; the four declared headings present with P2's cell whole; `cycle_check.py` unchanged.

## STEP 2 — QA (full suite + the real first-pass failure replayed on a clone of today's closed draft)

> ⛔ **Every item starts by re-establishing the root** — `cd "$(git rev-parse --show-toplevel)" && test -f gates.py && echo TREE_OK` — HALT unless TREE_OK. Interpreter ABSOLUTE; read-only beyond the two evidence files. ⛔ No plan-shaped file under any real `knowledge/decisions/`; scratch under `$T` only.
>
> **Item 1 — full suite, REDIRECTED not piped:** `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ --tb=short -q > knowledge/qa/evidence/close-cycle-walks-and-fixed-point-suite-2026-09-10.txt 2>&1`; the summary line quoted in the receipt as `N passed` with the skip named as `one skip (test_gate_watcher, live-DB)` — never the word the Rule 20 block scans for.
> **Item 2 — the real first pass:** `T=$(mktemp -d)`; `git clone -q /Users/marklehn/Developer/eluvian-governance $T/gov`; in the clone, take the 270 draft (`governance/knowledge/decisions/drafts/executable-bellows-lens-record-visibility.md`) and its register, rewrite the draft's absolute `**Walk register:**` ref to the clone's register path (so every checker reads the clone), `git -C $T/gov commit -qam "qa: ref to clone"`, set its `walks:` line to `walks: 0` and its `validation:` line to a stale value (e.g. `propagation_check=DIVERGENT:1`) and commit that too; then `scripts/close_cycle.py <clone draft> --closing-file <its Closing line, saved to a file> --register <clone register>` WITHOUT `--dry-run` and without `--commit` (steps 1–7 edit the CLONE's draft in place and nothing is committed — the dry-run works on temp copies the QA cannot read) → expected: `CLOSE: stored==live NOTE — propagation_check moved …` then `CLOSE: stored==live OK`, `CLOSE: battery OK`, `CLOSE: commit(skipped)`, and `grep '^walks:' <clone draft>` → `walks: 6` (the emitter's count for that draft) — the first pass that today failed. Paste the step lines.
> **Item 3 — production writes, stated exactly:** none outside the two evidence files; the clone and `$T` removed; no lane file, no lifecycle row, no lifecycle import.
> **Item 4 — receipt** `knowledge/qa/evidence/close-cycle-walks-and-fixed-point-qa-receipt-2026-09-10.md`: `numstat` over the DEV commits (`<base>..<dev>`, five files); a `## Verification` table with one row per Item 1–3, each quoting the line it rests on — ⛔ the status cell holds exactly one token (`✅`) and no positive row's text carries a hedging keyword; then RUN the canonical Rule 20 block (`$ELUVIAN_WRAP_ROOT/RULE_20_SELF_CHECK_BLOCK.md`) with `plan_slug: close-cycle-walks-and-fixed-point-2026-09-10`, `qa_report_path` and `evidence_dir` absolute under `$(git rev-parse --show-toplevel)/knowledge/qa/evidence/`, `required_evidence_files: ["close-cycle-walks-and-fixed-point-suite-2026-09-10.txt"]`, and APPEND its stdout — the banner `Rule 20 — QA Self-Check Results` and the closing `PASSED — SELF-CHECK PASSED` line are the block's output, never hand-authored; a `FAILED` stdout goes into the receipt and the step STOPS (thread 262).
> **Item 5 — commit**, path-scoped and gated: `grep -Eq '^[0-9]+ passed' knowledge/qa/evidence/close-cycle-walks-and-fixed-point-suite-2026-09-10.txt && ! grep -Eq '[0-9]+ (failed|error)' knowledge/qa/evidence/close-cycle-walks-and-fixed-point-suite-2026-09-10.txt && /Users/marklehn/Developer/bellows/.venv/bin/python tools/check_deposit.py /Users/marklehn/Developer/bellows/knowledge/decisions/in-progress-executable-<id>.md 2 --wt "$(git rev-parse --show-toplevel)" && git add knowledge/qa/evidence/close-cycle-walks-and-fixed-point-qa-receipt-2026-09-10.md knowledge/qa/evidence/close-cycle-walks-and-fixed-point-suite-2026-09-10.txt && git commit -F <msg-file> -- knowledge/qa/evidence/close-cycle-walks-and-fixed-point-qa-receipt-2026-09-10.md knowledge/qa/evidence/close-cycle-walks-and-fixed-point-suite-2026-09-10.txt`. ⛔ A QA step that finds it must change production code STOPS and requests a verdict (thread 262) rather than committing the change.
>
> **Deposits:**
> - `knowledge/qa/evidence/close-cycle-walks-and-fixed-point-qa-receipt-2026-09-10.md`
> - `knowledge/qa/evidence/close-cycle-walks-and-fixed-point-suite-2026-09-10.txt`
>
> **Scope:**
> - `knowledge/qa/evidence/close-cycle-walks-and-fixed-point-qa-receipt-2026-09-10.md`
> - `knowledge/qa/evidence/close-cycle-walks-and-fixed-point-suite-2026-09-10.txt`
>
> **Post-conditions:** the suite file's summary line is `N passed, 1 skipped` with N ≥ the DEV's count and no `failed`; Item 2's run pasted with the NOTE, the OK and `walks: 6`; the receipt's `## Verification` table has three rows and closes with the block's own PASSED line; one QA commit carrying the two evidence files.
