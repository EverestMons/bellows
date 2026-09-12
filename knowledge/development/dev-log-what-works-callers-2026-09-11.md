# Dev Log — what-works-callers — 2026-09-11

## Pins re-derived (P1, P2, P3)

P1 confirmed: two separate queries present — `verified_inbound` at :146 and `entry`'s own caller SQL at :321–333 with `src_c.name NOT LIKE '%/%'`. `verified_callers` not present (HALT condition clear).

P2 re-derived: `SELECT sum(name = file_path), count(*) FROM code_chunks WHERE chunk_type = 'module'` → `(5272, 5272)` — every module chunk's name IS its file path (5272 of 5272; P2's 5244 was the count at drafting, the shape is unchanged).

P3 verbatim: same scratch DB: target depositor.py::_assign_class (chunk_type method) — 74 cross-file call edges, ALL from chunks (chunk_type='module', name has '/', name == file_path), e.g. ('tests/test_admission_flip.py', 'tests/test_admission_flip.py', 'module'); verified_inbound → 74 (EDGES — call sites: the first three rows of the 74 came from the same chunk, tests/test_admission_flip.py), entry(...)["verified_callers_sample"] → []; bellows.py::_apply_ledger_updates (function) — 32 edges, all tests/test_bellows.py module chunks; 32 and []; lifecycle.py::init_lifecycle_db — 120 edges: module-root 1 (bellows.py), function 17, module-subdir 86, test_case 16; verified_inbound 120, sample ['bellows.py::bellows.py', 'tests/conftest.py::isolate_lifecycle_db', 'tests/test_admission_flip.py::tmp_db'] — the doc's rows 2, 9 and 10 reproduced

(This run's init_lifecycle_db count: 125 edges — bellows main moved since drafting. The shape is unchanged.)

Baseline interpreter: `3.9.6 2.0.0` (matches P4). Baseline suite: `274 passed in 1.53s` (matches P4).

## Failing-first (red, then green)

Red (t13–t16, before edits): `4 failed, 12 passed in 0.45s` — `ImportError: cannot import name 'verified_callers' from 'src.what_works'`

Green (t13–t16, after edits): `16 passed in 0.62s`

Anvil full suite after all edits: `278 passed in 1.91s` (274 baseline + 4 new; N ≥ 278)

MUST-PRESERVE verified: `grep -c "src_c.file_path || '::'" src/what_works.py` → `0`

## The anvil tree left for the Planner

```
M scripts/what_works.py
 M src/what_works.py
 M tests/test_what_works.py
```

## Mutation run

MUTATION: 5 killed, 0 survived, 0 error
