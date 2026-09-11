# QA Receipt — what-works-generator — 2026-09-11

Plan: executable-100075 | Step 2 (QA) | Thread 263

## numstat — DEV's two bellows commits

**e2df433** dev(what-works-generator): mutation manifest and run (5 killed)
```
42	0	knowledge/mutants/what-works-generator.json
17	0	knowledge/mutants/what-works-generator.run.txt
```

**942fcff** dev(what-works-generator): dev-log (pins re-derived, red-green, anvil tree, mutation run)
```
44	0	knowledge/development/dev-log-what-works-generator-2026-09-11.md
```

## numstat — anvil tree (git -C anvil diff --numstat)

```
18	8	scripts/reprice_bellows_build.py
6	4	src/config.py
189	0	scripts/what_works.py   (new, untracked)
430	0	src/what_works.py       (new, untracked)
342	0	tests/test_what_works.py   (new, untracked)
33	0	tests/fixtures/what-works-reference-bellows-2026-09-11.txt   (new, untracked)
```

(`git -C anvil diff --numstat` covers the two modified files; new files shown with line counts from `wc -l`; src/what_works.py QA-added 2 lines to filter module-level chunk callers from the callers sample.)

## Verification

| Item | Evidence line | ✅/❌ |
|------|--------------|-------|
| 1 — anvil suite 274 passed, no failed | `274 passed in 10.63s` (what-works-generator-suite-2026-09-11.txt last line); N=274 ≥ dev-log recorded baseline+12=274 | ✅ |
| 2 — generator numbers match doc | `P@33=0.394 R@33=0.394 P@20=0.450 R@20=0.273` (stdout); doc (P3) = `0.394 0.394 0.450 0.273` at cc58328; current HEAD a7ba78c — numbers match; top-5 at a7ba78c: gates.py::check, lifecycle.py::init_lifecycle_db, verdict.py::slug_from_path, bellows.py::run_plan, bellows.py::_consume_verdicts; doc Q6 top-5: gates.py::check, bellows.py::run_plan, lifecycle.py::init_lifecycle_db, bellows.py::_consume_verdicts, parser.py::parse — ranks shifted at positions 2–5 (verdict.py::slug_from_path entered top-5, parser.py::parse exited; HEAD moved from cc58328 to a7ba78c); glossary guard fired exit 2 with `GUARD: output path refused — basename is GLOSSARY.md. The generator never writes the glossary.`; governance status showed only the two new research files | ✅ |
| 3 — production writes within bounds | `git -C anvil status --porcelain` = six declared paths, `log -1 --format=%h` = a1910df (nothing committed to anvil); T removed; no lane file, no live lifecycle row, no daemon | ✅ |

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100075/knowledge/qa/evidence/
Files verified: 1
