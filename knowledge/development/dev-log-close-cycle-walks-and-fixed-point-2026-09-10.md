# Dev Log — close-cycle-walks-and-fixed-point — 2026-09-10

Plan 100069 | bellows `b2864cc` (first commit)

## Pins re-derived (P2, P3, P4)

**P2 — the tool as it stood:**

`scripts/close_cycle.py` (sha `054ac75a583e`, last writer `9447208` #100064): `_SPLICE_KEYS = ("yields", "validation", "coherence")` `:30`; `_splice_keys(draft_text, emit_stdout)` `:59–96` (collects `key: ` lines from the emit, replaces the draft's lines by key, errors on a key missing from either side); `_compose_subject` `:113–125` reads `walks:` and `tier:` from the emit output; step 3 `:188–194` emit (captured as `emit_out`); step 4 `:196–204` splice; step 5 `:206–212` baseline; step 6 `:214–230` re-emit and whole-line comparison of `validation:`; step 7 `:232–242` battery; step 8 `:244–` the register seal from `emit_out`'s `walks:` and the commit

Confirmed: `_SPLICE_KEYS` held three keys, not four. `_compose_subject` already read `walks:` from emit output but the splice never wrote it into the draft. Step 6 compared the full `validation:` line as a byte string; no token analysis.

**P3 — the tests as they stood:**

`tests/test_close_cycle.py`: 8 tests — c1 happy path (asserts the eight-step sequence and the three `<declare>` keys gone), c2 emitter header ignored, c3 dry-run order, c4 `stored != live → exit 1` (monkeypatched `after_step` — tampers cycle_check=BAR_MET→CONTINUE, not only propagation_check), c5 no closing line, c6 commit, c7 `plan_lint` WARN echo, c8 `plan_lint` FAIL refuses; `_make_fixture(tmp_path)` `:80` (a git repo with `plan.md` = `_INITIAL_PLAN` whose manifest has `walks: <declare>`, `register.md`, five lens commits), `_closing_file` `:106`.

Verified no test guarded `walks: <declare>`. c4's tamper changes `cycle_check=CONTINUE` and `propagation_check=N/A` — both tokens, not only propagation_check. c4 does not need re-pointing; docstring updated to name which token it moves.

**P4 — the emitter:**

`scripts/cycle_check.py:1089`: `print(f"walks: {walk_count}")`. Confirmed: emitter prints `walks: N` as a standalone line in `--emit-manifest` output. For the test fixture (all five lenses in walk 1), `walk_count = 1`. For the test fixture `propagation_check` returns `NOT_RUN` (no register ref resolves), so step 6's stored and live values match on the first pass without triggering the fixed-point path for the happy-path tests.

## Failing-first (three red, one pinned, then green)

New tests written before the edit; run against the unmodified `scripts/close_cycle.py`:

```
tests/test_close_cycle.py F.......FFF.
4 failed, 8 passed in 14.73s
```

- **c1** RED — new assert `"walks: <declare>" not in plan_text` fails: `walks: <declare>` survives the close (walks not in `_SPLICE_KEYS`).
- **c9** RED — `"walks: <declare>" not in plan_text` fails (same root cause).
- **c10** RED — test expects `rc == 0` after a propagation_check-only drift, but the shipped whole-line comparison returns `rc=1` (`stored==live FAIL`).
- **c10b** RED — test expects `"stored==live NOTE"` in stdout, but no NOTE is printed by the shipped code; just FAIL.
- **c11** GREEN — pins that a `cycle_check=` drift still fails; the shipped whole-line comparison already rejects it. Pinned before the edit so the fix cannot accidentally allow real drifts.
- **c2–c8** GREEN — unaffected.

After the edit (walks added to `_SPLICE_KEYS`; step 6 made a fixed point):

```
tests/test_close_cycle.py ............
12 passed in 12.35s
```

Full suite: `2228 passed, 1 skipped in 104.50s` — `test_gate_watcher` skips in worktree.

## The first-pass failure reproduced (Item 1)

c10's captured output before the edit (the c10b output block carries the FAIL line verbatim):

```
CLOSE: stored==live FAIL — stored 'validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=VACUOUS, propagation_check=DIVERGENT:10' != live 'validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=VACUOUS, propagation_check=DIVERGENT:14'
```

This is exactly P1's second defect: the spliced `validation:` line in the draft carries `DIVERGENT:10` from step 3's emit; the step 6 re-emit produces `DIVERGENT:14` (the splice itself changed the token count); the whole-line comparison fails; a second run passes. After the fix the same sequence prints:

```
CLOSE: stored==live NOTE — propagation_check moved DIVERGENT:10→DIVERGENT:14 (the spliced lines are counted); re-splicing once
CLOSE: stored==live OK
```

## Mutation run

```
MUTANT M1-walks-dropped-from-splice-keys: KILLED — suite caught the defect
MUTANT M2-re-splice-skipped: KILLED — suite caught the defect
MUTANT M3-token-comparison-widened-to-always-re-splice: KILLED — suite caught the defect
MUTANT M4-second-comparison-removed: KILLED — suite caught the defect

LIVE-TREE UNCHANGED: scripts/close_cycle.py sha256=c367bb3f16da

MUTATION: 4 killed, 0 survived, 0 error
```
