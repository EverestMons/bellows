# Dev Log — mutation-mtime-determinism (exec-579, Step 1)

**Date:** 2026-08-27

## Task B — Trial Results

### G1 probe (structural proof)

```
header 1787851248 ns 1787851248660249036 equal True
```

The `.pyc` header stores the source mtime as a 32-bit SECONDS field. Sub-second resolution is discarded for cache validation, so a same-second same-length rewrite is invisible on any filesystem. This is the structural proof — it does not depend on timing.

### Condition 1: nobump (5 trials)

Path: `$TMPDIR/trial_nobump_{1..5}`

```
SURVIVED
SURVIVED
SURVIVED
SURVIVED
SURVIVED
```

**Nobump result: SURVIVED 5/5.** All writes landed within the same mtime second, so the stale `.pyc` was served consistently. This directly reproduces the flakiness. Either outcome (SURVIVED or KILLED) is expected — SURVIVED means the writes stayed within the same second; KILLED means they straddled a boundary. The mechanism is proven from G1 regardless.

### Condition 2: bump at path A (5 trials)

Path: `/var/folders/vf/8nw0z7hj1m34w6z48l5dp54w0000gn/T/trial_bump_pathA_{1..5}`

```
KILLED
KILLED
KILLED
KILLED
KILLED
```

### Condition 3: bump at path B (5 trials)

Path: `/tmp/trial_bump_pathB_{1..5}`

```
KILLED
KILLED
KILLED
KILLED
KILLED
```

**Bump conditions: KILLED 10/10 across two different absolute paths.** The fix is deterministic and path-independent.

## Anchor counts (Task C)

After inserting the mtime bump:

- `            if exit_code == 1:` → 1
- `            if baseline_exit != 0:` → 1
- `    env["PYTHONDONTWRITEBYTECODE"] = "1"` → 1

All anchors remain unique.

## Task D — Mutant probe results

### Probe 1: drop-mtime-bump

```
MUTANT drop-mtime-bump: SURVIVED — suite does not discriminate this defect
MUTATION: 0 killed, 1 survived, 0 error
```

### Probe 2: drop-bytecode-isolation

```
MUTANT drop-bytecode-isolation: SURVIVED — suite does not discriminate this defect
MUTATION: 0 killed, 1 survived, 0 error
```

**Both probes SURVIVED.** The two invalidation guards (env var + mtime bump) are jointly sufficient and individually redundant. Removing either alone leaves the other covering. Both-at-once is not expressible under the single-anchor-per-mutant schema.

Manifest set to: `score-any-nonzero-as-killed` and `drop-baseline-control` only. `drop-bytecode-isolation` removed; `drop-mtime-bump` not added. `_removed_note` records the reason.

## Task E — Targeted run + final manifest

Tests: 11 collected, 11 passed, 0 failed.

Final manifest: 2 killed, 0 survived, 0 error, exit=0.

## Pin re-derivation (G1–G6)

| id | plan value | my value | status |
|---|---|---|---|
| G1 | header == int(st_mtime) is True; 32-bit seconds field | header 1787851248, ns 1787851248660249036, equal True | **agrees** |
| G1b | Planner 4S/1K nobump; exec-578 5K nobump | 5S nobump (SURVIVED 5/5) | **agrees with mechanism** — my writes consistently landed in same second |
| G2 | KILLED 5/5 at both paths with bump | KILLED 5/5 at path A, KILLED 5/5 at path B | **agrees** |
| G3 | write site at :188-190 | confirmed at :188-190 (pre-edit line numbers) | **agrees** |
| G4 | `import os` count 1 | 1 | **agrees** |
| G5 | 3 mutants in manifest | 3 mutants confirmed pre-edit | **agrees** |
| G6 | 1632 tests collected | 1632 tests collected | **agrees** |
