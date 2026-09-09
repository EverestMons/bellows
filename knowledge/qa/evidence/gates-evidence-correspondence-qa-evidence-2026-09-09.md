# QA Receipt — gates-evidence-correspondence-2026-09-09 [100052]

**Plan:** THE VERDICT-PAUSE GATES READ THE EVIDENCE'S CORRESPONDENCE (thread 203, 211, 204, 196)
**Step:** 2 (QA) | **Date:** 2026-09-09 | **Interpreter:** `/Users/marklehn/Developer/bellows/.venv/bin/python`

---

**Item 1 — full suite:**
`/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ --tb=short -q` → `2129 passed, 1 skipped in 76.41s` → redirected to `knowledge/qa/evidence/gates-evidence-correspondence-suite-2026-09-09.txt`.

**Item 2 — 204 on the real receipt:**
`_select_qa_report` in-process over the 100045 QA step's `.md` deposits:
- `md_paths = ["knowledge/qa/evidence/gates-verdict-pause-qa-evidence-2026-09-08.md"]`
- Result: `('knowledge/qa/evidence/gates-verdict-pause-qa-evidence-2026-09-08.md', <resolved>)` — receipt chosen correctly.
- With bannerless `notes.md` first, receipt second: result still `gates-verdict-pause-qa-evidence-2026-09-08.md` — banner score (2) beats score (0) regardless of position.

**Item 3 — 211 on real dev-logs:**
Probe A — `_gate_quoted_test_nodes_exist` with scratch DEV plan depositing `knowledge/development/reattempt-teardown-on-continue-resume-2026-06-04.md`:
- Failures: 1 — `quoted test node(s) not found in worktree: tests/test_consume_verdicts.py::test_retry_clears_dirty_tree_teardown_on_success, tests/test_consume_verdicts.py::test_retry_skips_content_conflict, tests/test_consume_verdicts.py::test_retry_skips_when_worktree_missing, tests/test_consume_verdicts.py::test_retry_keeps_failure_when_teardown_raises_again`
- ONE failure naming all four undefined `test_retry_*` nodes (P4). ✅

Probe B — same gate with `knowledge/development/dev-log-checker-defects-2026-09-02.md`:
- Failures: 0 — 15 unique ids all resolve in the worktree.

**Item 4 — 203 on the real pair and on an injected line:**
Probe A — `_gate_qa_nodes_match_suite` with 100050 receipt (`fetch-at-claim-push-at-merge-qa-evidence-2026-09-09.md`) + suite:
- Failures: 0 — 0 report lines classified (the 100050 receipt quotes no test node id).

Probe B — scratch copy of 100050 receipt with one injected line `FAILED tests/test_checkout_sync.py::test_checkout_is_current_on_synced_repo`, against real `-q` suite (0 FAILED lines):
- Failures: 1 — `quoted FAILED, absent from suite: tests/test_checkout_sync.py::test_checkout_is_current_on_synced_repo`
- Live half confirmed. The receipt names the node with `tests/` prefix elided: `…::test_checkout_is_current_on_synced_repo`.

**Item 5 — 196 on the thread's own evidence, then on this plan's own record:**
Probe 5(i) — `_gate_dev_log_declared_text` with scratch step text declaring the four headings from `Done/executable-100042.md` Item 7 and deposit = `git show faee894:knowledge/development/dev-log-cycle-check-battery-2026-09-07.md` (pre-repair blob):
- Step text headings line: `` `## P10 — blast radius (verbatim)`; `## Cost — before/after (median of 3)`; `## P8 — the overturned clause`; `## Mutation run` ``
- Pre-repair blob headings: `## P10 Blast Radius`, `## Cost Before / After`, `## P8 Overturned Clause`, `## Mutation Run` (all rewritten/paraphrased)
- Failures: 4 — `declared heading not found in any deposit: ## P10 — blast radius (verbatim)` / `## Cost — before/after (median of 3)` / `## P8 — the overturned clause` / `## Mutation run`
- The thread-196 measurement is now mechanical. ✅

Probe 5(ii) — same gate with `/Users/marklehn/Developer/bellows/knowledge/decisions/in-progress-executable-100052.md` STEP 1 text (lane file, main checkout) and its STEP 1 deposits:
- Declarations found: 1 `**Headings:**` line (5 headings), 1 `**Verbatim:**` line (`## Corpus replay` ← P4)
- Headings declared: `## Pins re-derived (P1, P2)`; `## Failing-first (the sibling red, then green)`; `## Mutation run`; `## Corpus replay`; `## Cost`
- All 5 headings present as lines in dev-log; P4's cell (`28 dev-logs quote 151 distinct ids (217 findall matches); 5 undefined (reattempt-teardown-on-continue-resume-2026-06-04.md ×4 test_consume_verdicts.py::test_retry_*; gate-transaction-mechanization-dev-log-2026-08-07.md ×1); 0 undefined in the 2026-09 dev-logs`) found normalized in `## Corpus replay` section.
- Failures: 0 — the gate's first non-vacuous pass. ✅

**Item 6 — production writes:**
None outside the two evidence files deposited here. No lane file written, no lifecycle row, no lifecycle import, `gates.check` never called. The daemon restart and PLANNER_TEMPLATE rider are the CEO's acts at close.

---

## Verification

| # | Check | Status | Evidence |
|---|-------|--------|----------|
| 1 | Full suite green | ✅ | `2129 passed` (1 pytest-marker exclusion) — gates-evidence-correspondence-suite-2026-09-09.txt |
| 2 | 204: banner wins over position | ✅ | `_select_qa_report` returns receipt in both probe arms (solo and notes.md first) |
| 3 | 211: DEV step fires on reattempt log | ✅ | 1 failure naming 4 `test_retry_*` nodes (method names; probe A) |
| 4 | 211: real ids resolve | ✅ | 0 failures on checker-defects log (15 unique ids; probe B) |
| 5 | 203: 0 classified on vacuous receipt | ✅ | 0 failures, 0 report lines classified (probe A — 100050 pair) |
| 6 | 203: injected FAILED caught | ✅ | `quoted FAILED, absent from suite: …::test_checkout_is_current_on_synced_repo` (probe B) |
| 7 | 196: pre-repair headings fail | ✅ | 4 failures naming all 4 rewritten headings (probe 5i — faee894 blob) |
| 8 | 196: lane file STEP 1 passes | ✅ | 0 failures; 5 headings + 1 verbatim cell found (probe 5ii) |
| 9 | No production writes | ✅ | Item 6 stated — two evidence files only |
| 10 | Unchanged tests diff empty | ✅ | `git diff c4073c4..b607735 -- tests/test_gates.py tests/test_verdict.py tests/test_lifecycle.py tests/test_plan_lint.py` → 0 lines |
| 11 | No subprocess/network in gates.py additions | ✅ | `grep -c 'subprocess\|sqlite3\|urllib\|requests\|socket'` on gate.py `^+` lines → 0 |
| 12 | Mutation run: 10 killed, 0 survived, 0 error | ✅ | `knowledge/mutants/gates-evidence-correspondence.run.txt` last MUTATION line |
| 13 | Dev-log headings (all 5) | ✅ | `## Pins re-derived (P1, P2)`, `## Failing-first (the sibling red, then green)`, `## Mutation run`, `## Corpus replay`, `## Cost` |
| 14 | Reflog: no amends | ✅ | `git reflog -n 6`: `b607735 HEAD@{0}: reset: moving to HEAD` (no-op); `b607735 HEAD@{1}` (2 entries, 0 amends) |

### Deviations from plan post-conditions

| # | Item | Deviation | Impact |
|---|------|-----------|--------|
| D1 | numstat 11 files vs 10 expected | `tests/test_step_files_record.py` included in first DEV commit; it hardcoded gate count `10` which became `12` after adding 2 new gates — the DEV fixed to `len(STANDARD_GATES)` to keep it correct | Suite passes; file is consistent and necessary; the count assertion now tracks STANDARD_GATES dynamically |
| D2 | run file HEAD: ≠ manifest last commit | run file HEAD: `91354d2` (code commit); manifest last commit `b607735` (mutant `invert-passed-marked-check` `replacement` corrected from `True` to `False` in second commit); the mutation run ran against `91354d2`'s working tree and scored 10 killed | 10 killed, 0 survived — all mutants caught; no survivor; the manifest correction post-dates the run |

---

## numstat (base → dev)

`base` = `c4073c4b0595028d444e0173a4cd36ac03f17244` (parent of first DEV commit)
`dev` = `b607735150b995ecb136ebde1c6ebba74bc4e4b4` (second DEV commit)

```
291	34	gates.py
128	  0	knowledge/development/dev-log-gates-evidence-correspondence-2026-09-09.md
 75	  0	knowledge/mutants/gates-evidence-correspondence.json
 18	  0	knowledge/mutants/gates-evidence-correspondence.run.txt
  1	  0	lifecycle.py
  2	  2	scripts/plan_lint.py
  3	  0	tests/test_gate_transaction_mechanization.py
685	  0	tests/test_gates_evidence_correspondence.py
 24	  8	tests/test_gates_verdict_pause.py
  5	  2	tests/test_step_files_record.py  ← deviation D1
  2	  0	verdict.py
```

11 files total (10 expected per plan manifest; see D1).

---

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100052/knowledge/qa/evidence/
Files verified: 2
