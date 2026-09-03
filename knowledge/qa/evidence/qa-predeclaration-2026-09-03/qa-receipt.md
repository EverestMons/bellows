# QA Receipt — plan_lint check (v) — qa-predeclaration-plan_lint-2026-09-03

**Plan:** 100028 — plan_lint (v): a no-pytest QA step must pre-declare qa_test_result override (thread 70)
**Step:** 2 (QA)
**Date:** 2026-09-03
**Executed from:** /Users/marklehn/Developer/bellows/.bellows-worktrees/100028 (worktree — no repo-root config)

---

## Hygiene

**DEV commit numstat** (`778a0a2` → `675f43a`):

```
105  0   knowledge/dev-logs/qa-predeclaration-dev-2026-09-03.md
 61  0   knowledge/mutants/qa-predeclaration-plan_lint.json
 28  1   scripts/plan_lint.py
206  0   tests/test_plan_lint_qa_predeclaration.py
```

4 files exactly (plan specifies 4 — matched).

**Recent commits (toplevel):**

```
675f43a feat(plan-lint): check (v) — no-pytest QA step must pre-declare qa_test_result override [100028]
778a0a2 draft(qa-predeclaration): Cycle Manifest emitted + the three detector fields authored — ready to deposit
75fbf92 draft(qa-predeclaration): FROZEN at walk 9 — cold scout's HIGH folded; the check was specified in the wrong scope
1b6cd90 draft(qa-predeclaration): walks 3-4 folded — the interpreter path was dead from the worktree; the exit-code invariant gains its discriminating mutant
c93d80e draft(qa-predeclaration): v0 → walk 2 — plan_lint (v), a no-pytest QA step must pre-declare its qa_test_result override (thread 70)
```

**Reflog -n 4:** `675f43a HEAD@{0}: reset: moving to HEAD` / `675f43a HEAD@{1}` — 0 amends.

---

## Item Results

### Item 1 — Full suite (worktree, no repo-root config)

- Working directory: `/Users/marklehn/Developer/bellows/.bellows-worktrees/100028`
- No repo-root config file present (confirmed with `ls repo-root-config` → no such file)
- Interpreter: `/Users/marklehn/Developer/bellows/.venv/bin/python` (absolute bind)
- Command: `"$BPY" -m pytest tests/ --tb=short -q`
- P9 baseline: 1814 passed, 1 skipped (1815 collected) — from worktree, 2026-09-02
- This cycle added **9 new tests** in `tests/test_plan_lint_qa_predeclaration.py`
- Arithmetic: 1814 + 9 = **1823 expected**
- Result: **1823 passed, 1 skipped** in 51.83s — exit 0
- Evidence: `knowledge/qa/evidence/qa-predeclaration-2026-09-03/pytest_full.txt`

### Item 2 — Check against real plans

#### 2.1 — Fires on known post-gate true positive (100013)

- Plan: `knowledge/decisions/Done/executable-100013.md`
- Result: **(v) WARN fires** — "step 1 is a QA step whose test_scope starts 'none', but its text carries no pre-declaration clause."
- Resolved verdict `verdicts/resolved/processed-verdict-100013-step-1.md` confirms gate override — confirmed true positive.

#### 2.2 — Silent on all four clause-carrying plans

| Plan | QA step confirmed | (v) WARN count |
|---|---|---|
| executable-100027.md | step 2 (QA by gate) | 0 |
| executable-543.md | step 2 (QA by gate) | 0 |
| executable-548.md | step 2 (QA by gate) | 0 |
| executable-555.md | step 2 (QA by gate) | 0 |

All four are QA-bearing (confirmed via `gates._gate_is_qa_step`). All four suppressed by (v). Zero false positives.

#### 2.3 — Corpus census

Measured with OR logic matching actual implementation: any of `pre-declar` | `gate note` | `qa_test_result` suppresses.

| metric | value |
|---|---|
| Done plans | 543 |
| (v) fires | 9 |
| Delta vs authoring-time | 0 (543 plans, 9 fires) |
| Class change | none |

Fires list: executable-100013.md (step 1), executable-backlog-hygiene-cause-5-and-daemon-logging-2026-05-11.md (step 2), executable-planner-template-bellows-execution-model-section-2026-04-30.md (step 2), executable-planner-template-lessons-step-numbering-2026-04-23.md (step 2), executable-priority-3-audit-closeout-2026-05-21.md (step 2), executable-qa-steps-governance-2026-05-25.md (step 2), executable-rule-26-evidence-path-fix-2026-05-11.md (step 2), executable-settings-local-bash-fallback-doc-2026-05-22.md (step 2), executable-verdict-only-resume-docs-2026-04-28.md (step 2).

100013 is the single post-gate fire (confirmed true positive). The remaining 8 predate the gate (2026-08-18) — retrospective, expected, harmless. Supersede rule: 543 plans matches authoring-time; class unchanged — no halt condition.

#### 2.4 — Exit code unaffected

- DEV commit (tagged [100028]): `675f43a`
- Preceding commit: `778a0a2`
- Plan linted: `knowledge/decisions/Done/executable-100013.md` (trips (v), no FAILs)
- Before (`778a0a2`): exit=0
- After (`675f43a`): exit=0
- (v) WARN does not alter exit code — invariant confirmed.

#### 2.5 — Predicate holds on this plan (100028)

- Plan file resolved: `knowledge/decisions/in-progress-executable-100028.md`
- (u) WARNs fire on step 1 (both arms — the P11 pre-declared instances from MUST-PRESERVE)
- (v) does NOT fire on step 1 (test_scope = "targeted", not "none") — correct
- (v) does NOT fire on step 2 (has real test scope) — correct
- Exit: 0

### Item 3 — Mutation check

```
MUTANT v-drop-scope-gate:            KILLED — suite caught the defect
MUTANT v-invert-suppression:         KILLED — suite caught the defect
MUTANT v-narrow-to-gate-name-token:  KILLED — suite caught the defect
MUTANT v-widen-suppression-to-whole-plan: KILLED — suite caught the defect
MUTANT v-drop-header-guard:          KILLED — suite caught the defect
MUTANT v-swap-gate-predicate:        KILLED — suite caught the defect
MUTANT v-only-last-step:             KILLED — suite caught the defect
MUTANT v-append-as-fail:             KILLED — suite caught the defect

MUTATION: 8 killed, 0 survived, 0 error
```

---

## Re-measured Funnel

Measured 2026-09-03 against 543 `Done/*.md`, using `gates._gate_is_qa_step` (the gate's own predicate):

| population | count |
|---|---|
| Done plans | 543 |
| QA steps by the gate's predicate | 306 (unchanged) |
| …whose test_scope starts with 'none' | 13 (unchanged) |
| …carrying a pre-declaration clause | 4 (100027, 543, 548, 555) |
| …carrying none → (v) fires | **9** |
| …of those 9, authored before the gate (2026-08-18) | 8 — retrospective, expected |
| …authored after | 1 — executable-100013, 2026-09-01 |

Delta vs authoring-time: 0. Class unchanged. Supersede rule applied.

---

## Verification

| Item | Result |
|---|---|
| Suite: 1823 passed (1824 collected), exit 0 | ✅ |
| (v) fires on 100013 (true positive) | ✅ |
| (v) silent on 100027, 543, 548, 555 | ✅ |
| Corpus census: 9 fires, 543 plans, class unchanged | ✅ |
| Exit code: before=0, after=0 (no change) | ✅ |
| Predicate holds: (v) silent on step 1 (targeted scope) | ✅ |
| Mutation check: 8 killed, 0 survived | ✅ |
| Funnel: 9 fires, delta=0, class unchanged | ✅ |


============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100028/knowledge/qa/evidence/qa-predeclaration-2026-09-03/
Files verified: 3
