# QA Receipt — lens-commit-accepts-continue — 2026-09-10

Plan: bellows #100065 | Step: 2 (QA) | Thread: 266

## DEV diff numstat (f947741..efd74d6 — two commits, five files)

```
79      0       knowledge/development/dev-log-lens-commit-accepts-continue-2026-09-10.md
26      0       knowledge/mutants/lens-commit-accepts-continue.json
11      0       knowledge/mutants/lens-commit-accepts-continue.run.txt
 7      3       scripts/lens_commit.py
106     3       tests/test_lens_commit.py
```

## Verification

| Item | What was verified | Quote | Status |
|------|-------------------|-------|--------|
| 1 — full suite | `2211 passed` in 95.55s — one skip (test_gate_watcher, live-DB); no `failed` in file | `2211 passed` — last line of `lens-commit-accepts-continue-suite-2026-09-10.txt`; one skip (test_gate_watcher, live-DB) | ✅ |
| 2 — real folding lens (positive) | Governance clone: walk 5 lens 1, plan_lint FAIL (qa_steps removed) downgrades BAR_MET → CONTINUE; tool accepts, commits three files | `LENS-COMMIT: cycle OK — CONTINUE` then `LENS-COMMIT: commit OK — draft(executable-bellows-lens-commit-accepts-continue): walk 5 lens 1 — Weak spots: qa rehearsal`; HEAD listed draft, register, `.foldcheck.json` | ✅ |
| 3 — escalation refused (negative) | Governance clone: bogus Walk register ref (non-existent path) causes ESCALATE:assert-fail:2; gate refuses; no commit added | `LENS-COMMIT: cycle FAIL — expected BAR_MET or CONTINUE, got 'ESCALATE:assert-fail:2'`; `commits added: 0 (expect 0)` | ✅ |

## Item 2 — clone runs (pasted)

### Positive: walk 5 lens 1 — real CONTINUE accepted, three files committed

Setup:
- `git clone -q /Users/marklehn/Developer/eluvian-governance $T/gov`
- Committed: rewrite `**Walk register:**` ref to clone's register path
- Working tree: Walk 5 table section + fold row appended to register; `| **qa_steps:** 2` removed from draft header (triggers plan_lint FAIL → CONTINUE downgrade)

```
LENS-COMMIT: plan_lint WARN — (o2) WARN: Deposits entry `scripts/lens_commit.py` is not project-prefixed or absolute
LENS-COMMIT: plan_lint WARN — (o2) WARN: Deposits entry `tests/test_lens_commit.py` is not project-prefixed or absolute
LENS-COMMIT: plan_lint WARN — (o2) WARN: Deposits entry `knowledge/mutants/lens-commit-accepts-continue.json` is not project-prefixed or absolute
LENS-COMMIT: plan_lint WARN — (o2) WARN: Deposits entry `knowledge/mutants/lens-commit-accepts-continue.run.txt` is not project-prefixed or absolute
LENS-COMMIT: plan_lint WARN — (o2) WARN: Deposits entry `knowledge/development/dev-log-lens-commit-accepts-continue-2026-09-10.md` is not project-prefixed or absolute
LENS-COMMIT: plan_lint WARN — (o2) WARN: Deposits entry `knowledge/qa/evidence/lens-commit-accepts-continue-qa-receipt-2026-09-10.md` is not project-prefixed or absolute
LENS-COMMIT: plan_lint WARN — (o2) WARN: Deposits entry `knowledge/qa/evidence/lens-commit-accepts-continue-suite-2026-09-10.txt` is not project-prefixed or absolute
LENS-COMMIT: plan_lint FAIL — FAIL: (y) undeclared QA step — step 2 is QA-labeled but the plan declares no qa_steps — it will NOT be Rule 20/22 gated at dispatch (declare `qa_steps: 2`, or `none` if it is not a QA step)
LENS-COMMIT: cycle WARN — WARN: BAR_MET downgraded to CONTINUE — battery: plan_lint=1_FAIL — fix the FAIL(s) plan_lint names before the next walk
LENS-COMMIT: cycle OK — CONTINUE
LENS-COMMIT: commit OK — draft(executable-bellows-lens-commit-accepts-continue): walk 5 lens 1 — Weak spots: qa rehearsal
exit rc=0
```

Files in HEAD after commit:
```
governance/knowledge/decisions/drafts/.executable-bellows-lens-commit-accepts-continue.md.foldcheck.json
governance/knowledge/decisions/drafts/executable-bellows-lens-commit-accepts-continue.md
governance/knowledge/research/walk-register-lens-commit-accepts-continue-2026-09-10.md
```

### Negative: walk 5 lens 2 — bogus Walk register ref → ESCALATE:assert-fail:2 refused

Setup (from HEAD after positive commit): Walk register ref changed to `/nonexistent/register-9999.md` (bogus path); walk 5 lens 2 fold row appended to real register.

```
LENS-COMMIT: plan_lint WARN — (o2) WARN: Deposits entry `scripts/lens_commit.py` is not project-prefixed or absolute
...
LENS-COMMIT: plan_lint FAIL — FAIL: (y) undeclared QA step — step 2 is QA-labeled but the plan declares no qa_steps — it will NOT be Rule 20/22 gated at dispatch (declare `qa_steps: 2`, or `none` if it is not a QA step)
LENS-COMMIT: cycle FAIL — expected BAR_MET or CONTINUE, got 'ESCALATE:assert-fail:2'
exit rc=1
commits added: 0 (expect 0)
```

## Item 3 — production writes

None outside the two evidence files. No lane file, no lifecycle row, no lifecycle import. Clone and scratch dirs removed (`rm -rf "$T"`).

## Rule 20 — QA Self-Check Results

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100065/knowledge/qa/evidence/
Files verified: 2
```
