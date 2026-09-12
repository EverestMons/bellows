# QA Receipt — what-works-callers — 2026-09-11

## DEV Commits — numstat

```
commit 9de4502  dev(what-works-callers): mutation manifest and run — verified_callers one edge set [100086] [thread 283]
42      0       knowledge/mutants/what-works-callers.json
13      0       knowledge/mutants/what-works-callers.run.txt

commit d206cd0  dev(what-works-callers): dev-log — pins, failing-first, mutation run [100086] [thread 283]
35      0       knowledge/development/dev-log-what-works-callers-2026-09-11.md
```

## Anvil Tree — git diff --numstat

```
4       3       scripts/what_works.py
30      31      src/what_works.py
161     0       tests/test_what_works.py
```

## Item 2 — Generator re-run

**Bellows HEAD**: #100075 receipt = `a7ba78c`; this run = `c690041` (bellows main moved)

**P&R values**:
| metric | #100075 (a7ba78c) | v2 (c690041) |
|--------|-------------------|--------------|
| P@33   | 0.394             | 0.394        |
| R@33   | 0.394             | 0.394        |
| P@20   | 0.450             | 0.450        |
| R@20   | 0.273             | 0.273        |

Numbers unchanged — bellows main moved but the edge count is the same set.

**Four rows named by thread 283** (P7 vs v2):

| def | P7 (#100075) | v2 (this run) |
|-----|-------------|---------------|
| lifecycle.py::init_lifecycle_db | 120 (`bellows.py::bellows.py`, `tests/conftest.py::isolate_lifecycle_db`, `tests/test_admission_flip.py::tmp_db`) | 125 (`bellows.py (module)`, `tests/conftest.py::isolate_lifecycle_db`, `tests/test_admission_flip.py (module)`) |
| verdict.py::slug_from_path | 55 (`bellows.py::bellows.py`, `bellows.py::run_plan`, …) | 55 (`bellows.py (module)`, `bellows.py::run_plan`, `tests/test_admission_flip.py (module)`) |
| depositor.py::_assign_class | 74 () | 74 (`tests/test_admission_flip.py (module)`, `tests/test_depositor.py (module)`, `tests/test_depositor_class_assigner.py (module)`) |
| bellows.py::_apply_ledger_updates | 32 () | 32 (`tests/test_bellows.py (module)`) |

Every caller label is `file::name` or `file (module)` — no `file::file` form survives.
No row shows a count above 0 with an empty list.

**Greps**:
- `grep -c '::[a-zA-Z_./-]*\.py[,)]' v2.md` → `0`
- `grep -cE '\| [1-9][0-9]* \(\)' v2.md` → `0`

## Item 3 — Production writes

`git -C /Users/marklehn/Developer/eluvian-governance status --porcelain -- governance/knowledge/research/` output:
```
?? governance/knowledge/research/action-census-2026-09-11.md
?? governance/knowledge/research/action-census-2026-09-11.tsv
?? governance/knowledge/research/what-works-entries-bellows-2026-09-11-v2.md
?? governance/knowledge/research/what-works-entries-bellows-2026-09-11-v2.tsv
```

Pre-existing untracked (not touched): `action-census-2026-09-11.md`, `action-census-2026-09-11.tsv` (deposited by #100085).
New files written: `what-works-entries-bellows-2026-09-11-v2.md`, `what-works-entries-bellows-2026-09-11-v2.tsv`.

Anvil tree: three declared paths only (`scripts/what_works.py`, `src/what_works.py`, `tests/test_what_works.py`); HEAD `fc32f63` (unchanged).
First entries doc byte-identical: `git diff --quiet` exits 0.
No lane file, no live lifecycle row, no daemon.

## Verification

| Item | Evidence | Status |
|------|----------|--------|
| Item 1 — anvil suite | `278 passed in 1.93s` (what-works-callers-suite-2026-09-11.txt last line) | ✅ |
| Item 2 — generator re-run | `P@33=0.394 R@33=0.394 P@20=0.450 R@20=0.273`; four named rows show module labels; two greps → 0 | ✅ |
| Item 3 — production writes | anvil three paths at fc32f63; first doc byte-identical; two v2 files written; two pre-existing files named | ✅ |

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100086/knowledge/qa/evidence/
Files verified: 1
