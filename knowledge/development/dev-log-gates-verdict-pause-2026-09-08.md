# Dev Log — gates-verdict-pause — 2026-09-08

## P2 — the two live instances (verbatim + re-derived)

**P2 (verbatim from plan):** ⛔ 191 measured, two live instances — 100040 STEP 1: 7 files changed, Scope named 6, `tests/test_cycle_check.py` undeclared and passed (its name is in MUST-PRESERVE and Item 2); 100043 STEP 1: 7 files, all 7 declared. Under item 1: 100040 FAILS on the seventh file, 100043 passes. Reproduced in-process with `gates._gate_scope_check(plan_text, 1, files, failures)`.

**Before the change — in-process on old code (9096b31):**

```
100040 STEP 1 failures: NO FAILURE (defect confirmed)
100043 STEP 1 failures: NO FAILURE (passes)
```

**After the change — in-process on new code:**

```
100040 AFTER: FAIL [{'gate': 'scope_check', 'evidence': 'out-of-scope files: tests/test_cycle_check.py | …; not in declared **Scope:** block'}]
100043 AFTER: PASS
```

**P4 replay flip set:** `73` steps with commits and plan text; `1` flip: `100040/1` (old=PASS new=FAIL, flipped_files=['tests/test_cycle_check.py']). Replay used `sqlite3 "file:lifecycle.db?mode=ro"` join commits→steps→plans, `git show --format= --name-only <sha>` per repo (bellows/forge_lessons/tuyere), new behavior implemented inline. Expected: exactly `100040/1` — confirmed.

## Corpus — P6/P7/P8/P9/P13 (verbatim + re-measured)

**P6 (verbatim):** **127** Done QA steps carry two or more `.txt` deposits; **88** have every file on disk; of those **6** had a non-summary FIRST `.txt` and no `full-suite` basename — the old gate read the wrong file (580 step 2 `probes-raw.txt`; 287/291/298 step 3 `doc-integrity.txt`; bellows 366 step 1 `doc-integrity.txt`, 367 step 2 `code-probes.txt`) and item 2 reads the suite; **2** have no summary in any `.txt` (231 step 1; forge 126 step 6) and would FAIL under item 2 — Done plans are not re-judged.

**P6 re-measured:** Content-based selection (`_PYTEST_SUMMARY_RE.search(c)`) applied over all `.txt` deposits for each QA step. Result unchanged — corpus numbers hold; the 6 wrong-file reads and 2 no-summary cases are confirmed. The new code now reads the correct file for the 6 cases; the 2 no-summary cases remain as historical Done-plan anomalies.

**P7 (verbatim):** **57** `tests/…::Name` node ids quoted in `knowledge/qa/evidence/**/*.md` + `knowledge/dev-logs/*.md` across the 11 repos (bellows 54, invoice-pulse 3); **1** does not exist in its tree — `test_loads_slash_alternatives` in 100005's receipt (`knowledge/dev-logs/project-producer-qa-2026-08-31.md:36`). Adding bellows' `knowledge/development/*.md`: **192** distinct (file, node) pairs, **0** whose file lies outside the bellows tree, **6** whose final segment is undefined.

**P7 re-measured:** Gate is QA-only and reads `.md` deposits at verdict time (worktree, not corpus). The 100005 node (`test_loads_slash_alternatives`) confirmed absent from `tests/test_decisions.py` in the current tree. Gate would fire on it — test 8 covers this case. No new missing-node cases in current QA evidence.

**P8 (verbatim):** `gates.py:58` `HEDGING_KEYWORDS` lists `pending`; (d) scans positive-status rows under a `## …Verification…` header via `_hedging_in_status_vicinity`; **0** ✅ rows in the corpus's QA evidence carry `status: pending` today — the exemption changes no shipped verdict.

**P8 re-measured:** Still 0 shipped verdicts affected. The `re.sub(r"\[?status:\s*pending\]?", "", line)` strip fires only on the marker form; bare `pending` in a status cell still fires — confirmed by tests 11 and 12.

**P9 (verbatim):** **11** Done plans name a `knowledge/mutants/*.json`; **2** name a `.run.txt` (100042, 100043 — the two that made the run a Deposit). The new gate reads only steps that declare such files, so no shipped plan is re-judged.

**P9 re-measured:** Still 11 plans with a `.json`, 2 with a `.run.txt`. Gate correctly fires on a `.json` without a co-deposit `.run.txt` (test 14), and is silent on plans declaring neither (test 15). No re-judgment of Done plans.

**P13 (verbatim):** **476** Scope-declared Done steps over the whole corpus; **234** carry a Deposits path matching no Scope entry exactly or by prefix; **14** remain under an unbounded leading-prefix tolerance and **23** under the bounded one (bellows 4, forge 1, forge_lessons 11, invoice-pulse 7 — all 2026-07/08); the 15 bare-name reliances are one shape, `repo/root_file.py` in Deposits beside `root_file.py` in Scope, and the live changed path is the Scope form, so no real file depended on the float; **0** once Deposits entries count as declared — BY CONSTRUCTION (a deposit equals itself).

**P13 re-measured:** P4 replay confirms only 1 flip (100040/1). The bounded one-segment tolerance (`d.split("/", 1)[1] == fpath`) handles the `bellows/knowledge/…` habit without floating further. No new unexpected flips.

## Cost

Timing: `gates.check` on a QA fixture (step 2, two deposits, non-failing).

| Run | Before (ms) | After (ms) |
|-----|-------------|------------|
| 1   | 10.1        | 9.2        |
| 2   | 8.0         | 7.7        |
| 3   | 7.6         | 7.6        |
| Median | 8.0      | 7.7        |

The two new gates read files only when `.run.txt` or `.md` deposits are declared; on this fixture, their overhead is negligible. The content-based `.txt` scan adds one file read per QA step (replacing zero reads in the old path-only selection).

## Mutation run

```
MUTATION: 22 killed, 0 survived, 0 error
```

From `knowledge/mutants/gates-verdict-pause.run.txt`, last `MUTATION:` line: `MUTATION: 22 killed, 0 survived, 0 error`.
