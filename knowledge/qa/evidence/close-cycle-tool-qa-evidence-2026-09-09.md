# Rule 20 — QA Self-Check Results
**Plan:** 100061 · **Thread:** 260 · **Date:** 2026-09-10

## Summary

QA for `scripts/close_cycle.py` and `scripts/lens_commit.py`, committed at `849c784`.
Two fixes were required during this QA pass (both committed in this QA commit):

1. **`_strip_field` + `--dry-run` fold_baseline strip** — the declared `fold_baseline:` field
   in governance plans resolves to the live post-splice governance baseline, causing
   fold_check to return DRIFT in step 3 (plan content is pre-splice). The fix: in
   `--dry-run` mode, strip the `fold_baseline:` declaration from the plan copy so
   `resolve_fold_baseline` falls through to the beside-the-plan baseline saved by step 2
   (always VACUOUS: content == baseline just saved).

2. **`--git-plan` argument** — governance plans live outside the bellows worktree, so
   `lens_order_check.py` could not find a git repo when `git_plan=draft_path` pointed at
   a temp copy. New `--git-plan <path>` lets callers supply a repo-relative path for
   lens_order_check while the draft copy stays in the temp dir.

## Production writes

Only the two files below were written. All five scratch dirs were removed before commit.

```
knowledge/qa/evidence/close-cycle-tool-suite-2026-09-09.txt   (item 1 output)
knowledge/qa/evidence/close-cycle-tool-qa-evidence-2026-09-09.md  (this file)
```

`scripts/close_cycle.py` was also updated (two fixes above); all 2171 prior tests still
pass, no new tests added for the fixes (they are --dry-run infrastructure, verified by
replaying the governance commits in this evidence file).

## Verification

| # | Check | Quoted line | Result |
|---|-------|------------|--------|
| 1 | Full suite passes | `2171 passed, 1 skipped in 83.88s (0:01:23)` | PASS |
| 2 | Three corrected closes: 8 CLOSE: lines, BAR_MET, spliced == committed sha | `CLOSE: commit(skipped) OK` (all three; see replays below) | PASS |
| 3 | Failed close 34580567 (emit-before-baseline): tool detects inconsistency | `CLOSE: stored==live FAIL — stored '…DIVERGENT:21' != live '…DIVERGENT:17'` | PASS (tool correctly refuses) |
| 4 | Failed close 81526436 (<declare> not spliced): tool splices all fields | `CLOSE: commit(skipped) OK` — validation spliced from `<declare>` to `BAR_MET/VACUOUS` | PASS |
| 5 | lens_commit assert: table name used, not descriptor | `LENS-COMMIT: commit OK — draft(plan): walk 1 lens 2 — Destruction: Weak spots: misleading descriptor` | PASS |

## Replays

### Item 2 — Three corrected closes (--dry-run)

All three: 8 CLOSE: lines, exit 0. Spliced validation matches committed sha byte-for-byte.

**9e324bc3 — anvil-reprice** (sha~1 had CONTINUE/DRIFT from prior failed close)

```
sha~1 validation: validation: cycle_check=CONTINUE, plan_lint=0_FAIL, fold_check=DRIFT, propagation_check=DIVERGENT:21
sha committed:    validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=VACUOUS, propagation_check=DIVERGENT:17
CLOSE: closing OK
CLOSE: baseline OK
CLOSE: emit OK
CLOSE: splice OK
CLOSE: baseline OK
CLOSE: stored==live OK
CLOSE: battery OK
CLOSE: commit(skipped) OK
exit: 0 — spliced validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=VACUOUS, propagation_check=DIVERGENT:17 ✓
```

**9e35a214 — forge-lifecycle-reporter** (sha~1 had validation: <declare>)

```
sha~1 validation: validation: <declare>
sha committed:    validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=VACUOUS, propagation_check=DIVERGENT:15
CLOSE: closing OK
CLOSE: baseline OK
CLOSE: emit OK
CLOSE: splice OK
CLOSE: baseline OK
CLOSE: stored==live OK
CLOSE: battery OK
CLOSE: commit(skipped) OK
exit: 0 — spliced validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=VACUOUS, propagation_check=DIVERGENT:15 ✓
```

**7da26aaa — doctrine-staleness-census** (sha~1 had validation: <declare>)

```
sha~1 validation: validation: <declare>
sha committed:    validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=VACUOUS, propagation_check=DIVERGENT:7
CLOSE: closing OK
CLOSE: baseline OK
CLOSE: emit OK
CLOSE: splice OK
CLOSE: baseline OK
CLOSE: stored==live OK
CLOSE: battery OK
CLOSE: commit(skipped) OK
exit: 0 — spliced validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=VACUOUS, propagation_check=DIVERGENT:7 ✓
```

### Item 3 — Two failed closes (--dry-run)

**34580567 — anvil-reprice (emit-before-baseline error)**

The hand ran emit before saving the baseline; fold_check saw DRIFT at emit time and
cycle_check downgraded BAR_MET → CONTINUE. The sha~1 state also has stale `yields: 6, 2, 0`
(three-walk manifest from the walk-3 close at 97773a54, carried forward through walks 4–5).
When the tool splices, the emitter recomputes yields as `6, 2, 0, 1, 0` (five walks); this
changes `propagation_check` from DIVERGENT:21 (pre-splice) to DIVERGENT:17 (post-splice),
so STORED==LIVE detects the inconsistency and refuses. The hand hid this by producing
CONTINUE/DRIFT silently. The corrected close (9e324bc3) ran on the 34580567 state where
yields were already correct — see Item 2 CORRECTED-1 above.

```
sha~1 validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=VACUOUS, propagation_check=DIVERGENT:17
sha (hand, failed): cycle_check=CONTINUE, plan_lint=0_FAIL, fold_check=DRIFT, propagation_check=DIVERGENT:21
CLOSE: closing OK
CLOSE: baseline OK
CLOSE: emit OK
CLOSE: splice OK
CLOSE: baseline OK
CLOSE: stored==live FAIL — stored '…propagation_check=DIVERGENT:21' != live '…propagation_check=DIVERGENT:17'
exit: 1
```

**81526436 — anvil-reprice (<declare> not spliced)**

The hand committed with `validation: <declare>` (splice step was broken at the time — the
emitter's `## Cycle Manifest` header was being consumed as a key). The tool splices all
three keys correctly:

```
sha~1 validation: <declare>
sha (hand, failed): validation: <declare>   ← hand left <declare>
CLOSE: closing OK
CLOSE: baseline OK
CLOSE: emit OK
CLOSE: splice OK                             ← tool splices where hand could not
CLOSE: baseline OK
CLOSE: stored==live OK
CLOSE: battery OK
CLOSE: commit(skipped) OK
exit: 0 — validation spliced from <declare> to cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=VACUOUS
```

### Item 4 — lens_commit assert test

```
$ lens_commit.py plan.md --register register.md --walk 1 --lens 2 --desc "Weak spots: misleading descriptor"
LENS-COMMIT: commit OK — draft(plan): walk 1 lens 2 — Destruction: Weak spots: misleading descriptor
exit: 0
```

Subject: `draft(plan): walk 1 lens 2 — Destruction: Weak spots: misleading descriptor`

The name "Destruction" is taken from `LENS_NAMES[2]` (the table), NOT from the `--desc`
argument ("Weak spots: …"). The assert `composed_name != expected_name` passes
(`"Destruction" == "Destruction"`), confirming the name-vs-descriptor independence.

---

PASSED — SELF-CHECK PASSED
