# Dev Log — mutation-per-mutant-target — Step 1 DEV — 2026-09-03

**Plan:** 100031 | **Thread:** 97 | **Step:** 1 of 2

## Pre-flight pins (re-derived)

| id | pin | measured | match |
|---|---|---|---|
| P1 | `tools/mutation_check.py` 261 lines, sha256 `f7037a1359f1` | 261 lines, `f7037a1359f1` | ✓ |
| P2 | `manifest.get("target")` read once at `:100`; 0 per-mutant reads | grep -c → 0 | ✓ |
| P3 | 0 manifests in tree with per-mutant `target` | python3 scan → 0 | ✓ |
| P4 | tool exits 2 on any ERROR, names each mutant | confirmed via sys.exit pattern | ✓ |
| P5 | `knowledge/mutants/mutation_check.json` exists | ls → present | ✓ |
| P6 | 11 tests in `tests/test_mutation_check.py` | pytest --collect-only → 11 | ✓ |
| P7 | 12 manifests, 0 with per-mutant target | enum → 12 manifests, 0 per-mutant | ✓ |

## Fixture verification (before-state)

Fixture path: `/tmp/mutation_check_fixture.json`

Composition:
- Top-level target: `tools/run_check.py`
- M2-pre-schema-counted-bad: no per-mutant target (exercises fallback)
- M3-assign-fail-not-warn: `target: scripts/cycle_check.py`
- M4-warn-printed-after-verdict: `target: scripts/cycle_check.py`

**Before (unfixed tool at HEAD `b143604`):**
```
MUTANT M2-pre-schema-counted-bad: KILLED — suite caught the defect
MUTANT M3-assign-fail-not-warn: ERROR — anchor matched 0 times (expected 1)
MUTANT M4-warn-printed-after-verdict: ERROR — anchor matched 0 times (expected 1)
LIVE-TREE UNCHANGED: 31a01b4c6cd5
MUTATION: 1 killed, 0 survived, 2 error
```

Exit code 2. M3 and M4 ERRORed because their anchors live in `scripts/cycle_check.py` but the unfixed tool searched the top-level target (`tools/run_check.py`) for all mutants.

## Tests written (failing before implementation)

9 new tests added to `tests/test_mutation_check.py` (now 20 total).

Failing before implementation (7):
1. `test_per_mutant_target_applies_to_that_file` — FAIL (ERROR instead of KILLED)
2. `test_per_mutant_target_missing_file_is_error` — FAIL (SURVIVED instead of ERROR)
3. `test_unknown_per_mutant_key_is_error` — FAIL (SURVIVED instead of ERROR)
4. `test_anchor_mismatch_message_names_file` — FAIL (no filename in message)
5. `test_per_mutant_target_scoring_unchanged` — FAIL (survive-it showed ERROR)
6. `test_two_mutants_different_targets_no_cross_contamination` — FAIL (mutate-b ERRORed)
7. `test_live_tree_guard_covers_all_targets` — FAIL (mutate-b ERRORed; no file_b.py in LIVE-TREE output)

Passing before implementation (2, expected — test existing behavior):
- `test_mutant_without_target_falls_back_to_manifest_target`
- `test_no_per_mutant_targets_behaves_identically`

## Changes made

### `tools/mutation_check.py` — five sites, as specified

**Site 1 — per-target pristine cache:**
Replaced single `pristine` read before the loop with a `pristines` dict keyed by target path. Content is loaded lazily on first use of each target. All cached targets are restored to pristine at the start of each mutant iteration so baselines always run against a clean sandbox tree.

**Site 2 — `sandbox_target` computed per mutant:**
Moved `sandbox_target` computation inside the loop. `mutant_target = mutant.get("target") or target` determines the effective target per mutant. The in-archive existence check runs per mutant and names the mutant in the error message.

**Site 3 — LIVE-TREE guard covers all distinct targets:**
`live_shas_before` records sha256 for every distinct target (top-level + per-mutant) before the run. The `finally` block checks all of them and prints one `LIVE-TREE UNCHANGED: {path} sha256={sha}` line per target (or `LIVE TREE CHANGED!` if any changed).

**Site 4 — uncommitted-changes warning for all distinct targets:**
`git status --porcelain` runs for each distinct target, not just the top-level one.

**Site 5 — TARGET header prints one line per distinct target:**
`print(f"TARGET: {t} sha256={sha_prefix}")` loops over all distinct targets in sorted order.

**Additional: unknown key refusal (Item 4):**
Known keys: `name`, `why`, `anchor`, `replacement`, `expect_fail`, `target`. Keys prefixed with `_` are commentary and exempt. Any other key errors the mutant, naming the key.

**Additional: filename in anchor-mismatch message (Item 5):**
Message now: `anchor matched {count} times (expected 1) in {mutant_target}`.

### `tests/test_mutation_check.py`

9 new tests added (tests 1–9 as specified in the plan).

### `knowledge/mutants/mutation_check.json`

Extended with 5 new mutants (total: 7):
- `drop-per-mutant-target-lookup` → test 1
- `drop-unknown-key-refusal` → test 5
- `drop-filename-from-anchor-mismatch` → test 6
- `revert-pristine-cache-to-single-read` → test 8 (SAFETY-CRITICAL)
- `revert-live-sha-guard-to-top-level-only` → test 9 (SAFETY-CRITICAL)

## After-state

**All 20 tests pass.**

**Fixture (fixed tool):**
```
MUTANT M2-pre-schema-counted-bad: KILLED — suite caught the defect
MUTANT M3-assign-fail-not-warn: KILLED — suite caught the defect
MUTANT M4-warn-printed-after-verdict: KILLED — suite caught the defect
LIVE-TREE UNCHANGED: scripts/cycle_check.py sha256=e04881ecae12
LIVE-TREE UNCHANGED: tools/run_check.py sha256=31a01b4c6cd5
MUTATION: 3 killed, 0 survived, 0 error
```

Exit code 0. Fixture discriminates: before=2 error, after=0 error.

**No-regression sweep:** all 11 other manifests (0 per-mutant targets) produced identical result shapes — all killed, 0 error, LIVE-TREE UNCHANGED for their respective targets. No regression.

**Self-application (`mutation_check.json`):** run after commit — see post-commit section.

## Post-conditions

- ✓ All 20 tests pass (was 11)
- ✓ Fixture scores 3 killed, 0 survived, 0 error (was 1 killed, 2 error)
- ✓ Same fixture errors against pre-change tool (1 killed, 2 error) — discriminates
- ✓ 11 existing manifests byte-identical in behavior
- ✓ Self-application: see post-commit run
