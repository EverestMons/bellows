# Dev-log: depositor class assigner — repo-aware (plan 100043, 2026-09-08)

## P2/P3 — the thirteen cases (verbatim)

**P2 verbatim (BEFORE):** `["app.py"]` from invoice-pulse → **shop-infra** (42) · `["GOVERNANCE.md"]` from tuyere → **shop-infra** (26) · abs `…/eluvian-governance/DRAFTING_CYCLE.md` from tuyere → **register-writing** (66) · bare `DRAFTING_CYCLE.md` from tuyere → shop-infra · abs `…/LESSONS.md` from tuyere → **app-feature** (66) · abs `…/DRAFTING_CYCLE.md` from bellows → shop-infra · `["scripts/x.py"]` from `forge_lessons` → **app-feature**, from `lessons-forge` → shop-infra (99) · `["DRAFTING_CYCLE.md"]` with root `""` → shop-infra (the existing test at `tests/test_depositor.py:164`)

**P3 verbatim (prototype AFTER):** 42 → **app-feature**; 26 `GOVERNANCE.md` from tuyere → **shop-infra** (the name floor); 26b `config.example.json` from tuyere → **app-feature**; `docs/GOVERNANCE.md` from tuyere → app-feature (not root); 66 abs DC from tuyere → **shop-infra**; bare DC from tuyere → **shop-infra** (governance-existence redirect); abs LESSONS from tuyere → **shop-infra**; abs DC from bellows → shop-infra; 99 forge_lessons → **shop-infra**; root `""` → shop-infra (unknown repo, fail-shut); `["bellows/depositor.py"]` root `""` → shop-infra; a NEW bare file in tuyere (`brand_new.md`) → app-feature; `knowledge/development/x.md` from bellows → app-feature (exempt)

**Shipped code results (test_1_thirteen_cases, all 13 asserted green):**

| # | writes | root | BEFORE | AFTER | note |
|---|--------|------|--------|-------|------|
| 42 | `["app.py"]` | invoice-pulse | shop-infra | **app-feature** | bare-arm defect fixed |
| 26 | `["GOVERNANCE.md"]` | tuyere | shop-infra | **shop-infra** | name floor |
| 26b | `["config.example.json"]` | tuyere | shop-infra | **app-feature** | tuyere not infra |
| 26c | `["docs/GOVERNANCE.md"]` | tuyere | shop-infra | **app-feature** | not root-level |
| 66a | abs G/DRAFTING_CYCLE.md | tuyere | register-writing | **shop-infra** | outside G/P → UNKNOWN → fail-shut |
| 66b | `["DRAFTING_CYCLE.md"]` | tuyere | shop-infra | **shop-infra** | governance-existence redirect (E5) |
| 66c | abs P/LESSONS.md | tuyere | app-feature | **shop-infra** | LESSONS.md under P → resolver → infra |
| 66d | abs P/bellows/DRAFTING_CYCLE.md | bellows | shop-infra | **shop-infra** | bellows infra |
| 99 | `["scripts/x.py"]` | forge_lessons | app-feature | **shop-infra** | forge_lessons in floor |
| f1 | `["DRAFTING_CYCLE.md"]` | `""` | shop-infra | **shop-infra** | UNKNOWN → fail-shut |
| C4 | `["bellows/depositor.py"]` | `""` | shop-infra | **shop-infra** | leading-seg → bellows in floor |
| new | `["brand_new.md"]` | tuyere | n/a | **app-feature** | no redirect, tuyere not infra |
| exempt | `["knowledge/development/x.md"]` | bellows | app-feature | **app-feature** | knowledge/ exempt |

## P4 — corpus flips (verbatim + re-derived)

**P4 verbatim:** **113 Done plans carry a manifest `writes:`** (bellows 66, eluvian-governance 17, forge_lessons 18, invoice-pulse 4, tuyere 8 — five repos; anvil and forge none); with the name floor the prototype flips **6**, every one an intended fix: bellows 100018 shop-infra→app-feature (its only non-knowledge write is `…/eluvian-governance/governance/knowledge/architecture/…`, an exempt path the old `project_is_infra` arm could not see); forge_lessons `diagnostic-501`, 549 app-feature→shop-infra (99); invoice-pulse 580, 581 shop-infra→app-feature (42); tuyere 100003 shop-infra→app-feature (a bare `config.example.json`, 26b). tuyere 100001, 100002 and 3 STAY shop-infra — each writes `GOVERNANCE.md`, which the name floor holds (f7). BEFORE 82 shop-infra / 11 app-feature / 20 read-only → AFTER 80 / 13 / 20

**Re-derived with shipped code (Done/ glob, bellows+governance+forge_lessons+invoice-pulse+tuyere):**

6 flips — set matches prototype exactly:

| plan | BEFORE | AFTER |
|------|--------|-------|
| bellows/executable-100018.md | shop-infra | app-feature |
| forge_lessons/diagnostic-501.md | app-feature | shop-infra |
| forge_lessons/executable-549.md | app-feature | shop-infra |
| invoice-pulse/executable-580.md | shop-infra | app-feature |
| invoice-pulse/executable-581.md | shop-infra | app-feature |
| tuyere/executable-100003.md | shop-infra | app-feature |

Distribution: BEFORE 82/11/20 → AFTER 80/13/20 (shop-infra / app-feature / read-only). Matches P4.

## Cost

`_assign_class` timed over 113-plan corpus, three runs each.

**BEFORE (80a2ce2, old `project_is_infra` arm, no filesystem calls):**

| run | total | per-plan |
|-----|-------|---------|
| 1 | 1.2 ms | 10 µs |
| 2 | 1.2 ms | 10 µs |
| 3 | 1.2 ms | 10 µs |
| **median** | **1.2 ms** | **10 µs** |

**AFTER (2b9f0cb, `_resolve_write` with `Path.exists()` calls):**

| run | total | per-plan |
|-----|-------|---------|
| 1 | 92.5 ms | 818 µs |
| 2 | 83.7 ms | 740 µs |
| 3 | 83.1 ms | 735 µs |
| **median** | **83.7 ms** | **740 µs** |

The resolver adds `Path.exists()` calls (one per relative write to check governance-existence redirect E5 and leading-segment redirect). Overhead is ~70× per call. Acceptable: class assignment runs once per deposit, not in any hot path.

## Mutation run

```
MUTATION: 12 killed, 0 survived, 0 error
```

(Full output in `knowledge/mutants/depositor-class-assigner.run.txt`, HEAD 2b9f0cb.)

**Deviation from plan:** Plan specified 2 DEV commits and 7 files in numstat. Actual: 3 commits — a mutation fix commit (2b9f0cb) was required after the first code commit because 3 mutants survived (governance-existence-redirect anchor was the comment line not the code line; test_9 assertions used root `""` masking config/floor distinctions). `git diff --numstat 80a2ce2..HEAD` still shows 7 unique files (the fix commit edited already-tracked files, not new ones): depositor.py, test_depositor.py, test_depositor_lens_order_gate.py, test_depositor_class_assigner.py, depositor-class-assigner.json, depositor-class-assigner.run.txt, dev-log (this file). `git reflog -n 6` → 0 amends, 0 resets.
