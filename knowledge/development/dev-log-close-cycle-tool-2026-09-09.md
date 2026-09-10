# Dev-log: close_cycle + lens_commit tools — 2026-09-09 (plan 100061, thread 260)

## Pins re-derived (P3, P4)

**P4 (the depositor's guard the order protects):** `depositor.py:777–783`: `val = manifest.get("validation", "")` … `expected = val.split("cycle_check=")[1].split(",")[0].strip()` … `if expected and expected != str(verdict):` → hold `validation_mismatch:cycle_check expected=<x> got=<y>`; measured live at 20:00:42 on #100057's second deposit

**P3 re-derived (cycle_check.py):**
- `MANIFEST_VALIDATION_KEYS = frozenset({"cycle_check", "plan_lint", "fold_check", "propagation_check"})` at `:61`
- `def emit_manifest(plan_path)` at `:1021`; argv `--emit-manifest <plan>` at `:1103`; always returns exit 0 and prints `## Cycle Manifest` then all keys
- `BAR_MET` / `CONTINUE` / `ESCALATE:<reason>` on the last stdout line of the non-emit invocation

**P3 re-derived (fold_check.py):**
- `--save-baseline` at `:163`; always exits 0; writes `.{name}.foldcheck.json` beside the artifact
- `FOLD-CHECK VACUOUS` at `:216` (exit 2): baseline sha256 == current sha256 — cannot observe a fold
- `FOLD-CHECK DRIFT` at `:234` (exit 1): machine-readable state changed
- `ERROR: no baseline` at `:198` (exit 2): `--baseline` path not found

**P3 re-derived (walk_register_lint.py):** `walk_register_lint.py <register> --plan <plan>` first output line is `<file>\tSHAPE-OK\tCOVERAGE: <token>…` printed to STDERR (`:584`). `run_checker` must use `stderr=subprocess.STDOUT` to capture it.

## Failing-first (eleven red, then green)

Both test files were written and confirmed failing before any script was written. The expected failure in each file was `ModuleNotFoundError: No module named 'close_cycle'` / `No module named 'lens_commit'` (the import at module level fires immediately). All eleven collected as errors, zero as passed.

After writing `scripts/close_cycle.py` and `scripts/lens_commit.py`, all eleven passed in one run. Three fixes applied during the green pass:

1. **plan_lint battery check**: the battery checked `"0_FAIL" in out` against plan_lint's stdout, but plan_lint never outputs "0_FAIL" — that token appears in cycle_check's `BATTERY:` line. Fixed to check `rc != 0`.

2. **Recursion in l3/l4/l5 fakes**: the test fakes called `lens_commit.run_checker` after `monkeypatch.setattr` had replaced it with the fake itself. Fixed by capturing the real function into a local variable (`_real = lens_commit.run_checker`) before setting the attribute — same pattern used by test_c2 in close_cycle.

3. **Dry-run battery failure (`ESCALATE:assert-fail:2`)**: cycle_check calls `check_assert_2` which resolves the walk register via `_resolve_register_ref`. Without a git root in the temp directory, the register was UNRESOLVED. Fixed by init-ing a minimal git repo in the temp directory and committing the copied plan and register before `_run_close` is called. For `lens_order_check` specifically, the original plan path (inside the real repo, with the five lens commits) is passed as `git_plan`.

Full suite after fix: **2171 passed, 1 skipped**.

## The order, printed (c3's sequence)

`test_c3_dry_run_order` asserts that the eight printed step labels, in order, are:

```
closing, baseline, emit, splice, baseline, stored==live, battery, commit(skipped)
```

Extracted as `[l.split()[1] for l in out.splitlines() if l.startswith("CLOSE:")]`. The step names map directly to the eight printed `CLOSE: <name> OK` lines, so a swap, removal or insertion anywhere in the sequence is observable by the test.

## Mutation run

Seven mutants, all killed. Run against HEAD `849c784b81d4eaa4fd888a11576545122be722be`:

| mutant | target | what it changes | killed by |
|--------|--------|-----------------|-----------|
| M1-drop-coherence-from-splice-keys | close_cycle.py | removes `coherence` from `_SPLICE_KEYS`; splice step fails | test_c1_happy_path |
| M2-no-op-splice-write | close_cycle.py | replaces the spliced value with the original line (no-op); `<declare>` stays; STORED≠LIVE | test_c1_happy_path |
| M3-flip-stored-live-comparison | close_cycle.py | `!=` → `==`; happy path fails at stored==live; tamper case passes | test_c1_happy_path |
| M4-battery-checks-CONTINUE-not-BAR_MET | close_cycle.py | battery checks for `CONTINUE` instead of `BAR_MET`; always fires | test_c1_happy_path |
| M5-lens-assert-self-comparison | lens_commit.py | `composed_name != expected_name` → `composed_name != composed_name` (tautology) | test_l2_assert_checks_name |
| M6-yield-rising-ceiling-inverted | lens_commit.py | `walk_n > ceiling` → `walk_n < ceiling`; walk 7 no longer refused | test_l4_yield_rising_walk7_refused |
| M7-lint-gate-inverted | lens_commit.py | `"SHAPE-OK" not in out` → `"SHAPE-OK" in out`; valid register refused | test_l1_subject_lens_name |

Final line: `MUTATION: 7 killed, 0 survived, 0 error`
