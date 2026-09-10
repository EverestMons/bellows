# QA Receipt — lens-record-visibility — 2026-09-10

Plan id: 100063 | Thread 270 | Step: 2 (QA)

## DEV Commits Covered

Commits on branch `bellows-wt/100063` since `main` (`git diff --numstat main...HEAD`):

```
75  0   knowledge/development/dev-log-lens-record-visibility-2026-09-10.md
108 0   knowledge/mutants/lens-record-visibility.json
24  0   knowledge/mutants/lens-record-visibility.run.txt
152 6   scripts/lens_commit.py
63  2   scripts/lens_order_check.py
211 4   tests/test_lens_commit.py
228 0   tests/test_lens_order_check.py
```

Seven files exactly as declared in Step 1 Scope.

## Item 1 — Full Suite

Command: `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ --tb=short -q > knowledge/qa/evidence/lens-record-visibility-suite-2026-09-10.txt 2>&1`

Summary line from evidence file:

```
2203 passed, 1 skipped in 88.52s (0:01:28)
```

2203 passed (≥ DEV count of 2203), one skip (test_gate_watcher, live-DB), no failed, no error.

## Item 2 — Real Record from a Deposit-Shaped Copy

`T=$(mktemp -d)` → `/var/folders/…/tmp.EvtqoKnmpT`

Deposit-shaped copy: `cp governance/decisions/drafts/executable-bellows-lint-warn-to-fail.md $T/proj/knowledge/decisions/…` then `git init -q $T/proj && git commit -q -m "deposit-shaped copy"`.

**Positive run (with fold_baseline:):**

```
BASIS: source=draft+register, one log via fold_baseline (executable-bellows-lint-warn-to-fail.md) tier=T1 declared_walks=[1, 2, 3, 4] lens_commits=20 walks_with_lens_commits=[1, 2, 3, 4]
LENS-ORDER OK — 20 lens commit(s) across walks [1, 2, 3, 4]; each names one lens, ascending, and every closed walk carries its tier's full set
rc:0
```

Matches P9 prototype line verbatim. The 2026-09-10 hold is lifted.

**Negative run (fold_baseline: line deleted):**

```
BASIS: source=plan+register, merged by time (walk-register-lint-warn-to-fail-2026-09-10.md) tier=T1 declared_walks=[1, 2, 3, 4] lens_commits=9 walks_with_lens_commits=[1, 2, 3, 4]
INCOMPLETE: walk 2 — closed walk proves lenses [1, 3]; T1 requires [1, 2, 3, 4, 5] — missing [2, 4, 5]
INCOMPLETE: walk 3 — closed walk proves lenses [1]; T1 requires [1, 2, 3, 4, 5] — missing [2, 3, 4, 5]
rc:1
```

The 2026-09-10 hold reproduced byte-for-byte in its verdict lines (P1). The pointer-absent reading is byte-identical to today (MUST-PRESERVE 3).

## Item 3 — Tool Rehearsed on a Clone

`git clone -q /Users/marklehn/Developer/eluvian-governance $T/gov`

Draft: `$T/gov/governance/knowledge/decisions/drafts/executable-bellows-lint-warn-to-fail.md`  
Register: `$T/gov/governance/knowledge/research/walk-register-lint-warn-to-fail-2026-09-10.md`

Note: the clone's draft carries the LIVE register's absolute `**Walk register:**` ref, so step 3 (`cycle_check`) reads the live register while step 2 lints and step 5 writes the clone's. This is a mixed-repo rehearsal: nothing live is written.

**Case 1 — `--dry` walk 5 lens 1 (cycle-record-only edit: `; w5 dry` appended to last `- Weak spots:` line):**

```
LENS-COMMIT: commit OK — draft(executable-bellows-lint-warn-to-fail): walk 5 lens 1 — Weak spots: qa rehearsal
rc:0
```

`git -C $T/gov show --name-only --format= HEAD`:
```
governance/knowledge/decisions/drafts/.executable-bellows-lint-warn-to-fail.md.foldcheck.json
governance/knowledge/decisions/drafts/executable-bellows-lint-warn-to-fail.md
governance/knowledge/research/walk-register-lint-warn-to-fail-2026-09-10.md
```

Last lines of register after commit:
```
<!-- cycle-close: WARM walk 4 (T1) -->
**Walk 5 lens 1 — Weak spots — DRY, basis:** qa rehearsal
```

All three files committed (draft, register, baseline). DRY line appended.

**Case 2 — fold without a register row (no `--dry`, walk 5 lens 2, one line appended to draft body):**

```
LENS-COMMIT: record FAIL — the register carries no row for walk 5 lens 2; write the fold row (§2.7), or pass --dry for a dry lens
rc:1
```

No commit made.

**Case 3 — `--dry` over the same body change (walk 5 lens 2):**

```
LENS-COMMIT: record FAIL — --dry, but the draft changed beyond its cycle record: extra qa rehearsal body line
rc:1
```

No commit made. The offending line quoted.

## Item 4 — Production Writes

None beyond the two evidence files (`lens-record-visibility-qa-receipt-2026-09-10.md` and `lens-record-visibility-suite-2026-09-10.txt`). No lane file written, no lifecycle row, no lifecycle import, no write to any real `knowledge/decisions/`. The clone and scratch dir were removed (`rm -rf $T`).

## Verification

| Item | Assertion | Status |
|------|-----------|--------|
| 1 — Full suite | 2203 passed, one skip (test_gate_watcher, live-DB), no failed; evidence file `lens-record-visibility-suite-2026-09-10.txt` non-empty | ✅ |
| 2 — Deposit-shaped copy positive | rc 0, `LENS-ORDER OK`, `source=draft+register, one log via fold_baseline`; 20 lens commits across walks [1,2,3,4] | ✅ |
| 2 — Deposit-shaped copy negative | rc 1, `merged by time`, `INCOMPLETE: walk 2`, `INCOMPLETE: walk 3` — hold reproduced | ✅ |
| 3 — Tool rehearsal: dry commit | rc 0, `commit OK`, draft+register+baseline in `git show --name-only`, DRY line in register | ✅ |
| 3 — Tool rehearsal: fold without row | rc 1, `record FAIL — the register carries no row for walk 5 lens 2` | ✅ |
| 3 — Tool rehearsal: dry over body | rc 1, `record FAIL — --dry, but the draft changed beyond its cycle record: extra qa rehearsal body line` | ✅ |
| 4 — Production writes | No writes outside the two evidence files; no lifecycle import; clone removed | ✅ |

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100063/knowledge/qa/evidence/
Files verified: 1
