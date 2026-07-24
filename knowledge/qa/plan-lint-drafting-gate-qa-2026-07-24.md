# QA Report — plan_lint §4 Drafting-Cycle self-check (warn-first)

**Plan:** 271 | **Step:** 2 (QA) | **Date:** 2026-07-24

## Verification Table

| # | Claim | Result | Evidence |
|---|---|---|---|
| 1 | **Warn-first proven** — plan_lint on a tier-less plan and a T1 plan missing a lens prints the WARN AND exits 0 | **PASS** | Tier-less (265): `WARN: no cycle_tier declared`, exit 0. T1 missing ACID: `WARN: Drafting Cycle block missing lens(es): ACID`, exit 0. See `evidence/plan-lint-drafting-gate-2026-07-24/warn-first-verification.txt` |
| 2 | **Compliant plan is clean** — plan_lint on a compliant T2 block emits NO drafting-cycle WARN | **PASS** | Test fixture COMPLIANT_T2_PLAN (270's real block + Cold panel line) emits zero drafting-cycle WARNs, exit 0. Note: the unmodified 270 emits a cold-panel WARN because it predates the requirement — correct behavior. See `evidence/plan-lint-drafting-gate-2026-07-24/compliant-t2-plan-270.txt` |
| 3 | **Each §4 rule fires** independently | **PASS** | (a) no-cycle_tier → `WARN: no cycle_tier declared`; (b) T1 missing ACID → `WARN: ... missing lens(es): ACID`; (c) T2 missing cold-panel → `WARN: T2 plan missing cold-panel line`; (d) fold-closing → `WARN: Drafting Cycle closing indicates fold as last event, not a dry lens pass`; (e) T0 tier-only → NO block/lens/closing WARN. All exit 0. See `evidence/plan-lint-drafting-gate-2026-07-24/warn-first-verification.txt` |
| 4 | **No crash on degenerate input** — empty/malformed `## Drafting Cycle` block WARNs, does not raise | **PASS** | Empty block (heading present, body empty before next `##`): emits WARNs for all 5 missing lenses + cold-panel + no Closing line. No traceback, exit 0. See `evidence/plan-lint-drafting-gate-2026-07-24/warn-first-verification.txt` |
| 5 | **Existing behaviour intact** — every prior plan_lint test passes; ONLY test edit was assertion updated for new WARN | **PASS** | One edit: `test_lint_single_step_diagnostic_no_e_fail` line 350: `assert "WARN" not in result.stdout` → `assert "consider using uppercase" not in result.stdout`. Intent preserved (no step-heading-case WARN). No other existing tests changed. 21 lint tests pass (15 existing + 6 new). See `evidence/plan-lint-drafting-gate-2026-07-24/targeted-lint-tests.txt` |
| 6 | **Scope** — changes limited to `scripts/plan_lint.py` + the test file | **PASS** | `git diff --stat HEAD~2..HEAD~1` shows 3 files: `scripts/plan_lint.py` (+41), `tests/test_plan_lint.py` (+111 -1), `knowledge/development/plan-lint-drafting-gate-dev-2026-07-24.md` (+129). No other bellows module touched. See `evidence/plan-lint-drafting-gate-2026-07-24/scope-diff-stat.txt` |
| 7 | **Full suite** — all tests pass, no regressions | **PASS** | `python3 -m pytest tests/ --tb=short -q`: 813 passed, 1 warning in 21.02s. No failures. See `evidence/plan-lint-drafting-gate-2026-07-24/full-suite.txt` |

## Raw Evidence

### V1 — Warn-first proven (tier-less plan, exit code)

```
$ python3 scripts/plan_lint.py /Users/marklehn/Developer/GitHub/invoice-pulse/knowledge/decisions/Done/executable-265.md
WARN: no cycle_tier declared (DRAFTING_CYCLE.md §1/§3)
PASS: (a) header — parsed
PASS: (a) dispatch_mode — bellows
PASS: (a) pause_for_verdict — always
PASS: (b) step 1 deposits — 1 path(s)
PASS: (b) step 2 deposits — 1 path(s)
PASS: (c) QA banner pair — both strings present
PASS: (d) step 1 scope — 8 file(s), 0 prefix(es)
PASS: (d) step 2 scope — 1 file(s), 1 prefix(es)
$ echo $?
0
```

### V1 — Warn-first proven (T1 missing ACID, exit code)

```
WARN: Drafting Cycle block missing lens(es): ACID (DRAFTING_CYCLE.md §3)
PASS: (a) header — parsed
PASS: (a) dispatch_mode — bellows
PASS: (a) pause_for_verdict — always
EXIT: 0
```

### V2 — Compliant T2 plan (real 270)

```
$ python3 scripts/plan_lint.py /Users/marklehn/Developer/GitHub/governance/knowledge/decisions/Done/executable-270.md
WARN: T2 plan missing cold-panel line in Drafting Cycle block (DRAFTING_CYCLE.md §3)
PASS: (a) header — parsed
PASS: (a) dispatch_mode — bellows
PASS: (a) pause_for_verdict — always
PASS: (b) step 1 deposits — 1 path(s)
PASS: (b) step 2 deposits — 1 path(s)
PASS: (b) step 3 deposits — 1 path(s)
PASS: (c) QA banner pair — both strings present
$ echo $?
0
```

Plan 270 correctly gets the cold-panel WARN because it predates the Cold panel requirement. The test fixture uses 270's real block with the Cold panel line added; that fixture emits NO drafting-cycle WARN.

### V3 — Each §4 rule fires independently

```
=== no cycle_tier ===
WARN: no cycle_tier declared (DRAFTING_CYCLE.md §1/§3)
EXIT: 0

=== T1 missing ACID ===
WARN: Drafting Cycle block missing lens(es): ACID (DRAFTING_CYCLE.md §3)
EXIT: 0

=== T2 missing cold-panel ===
WARN: T2 plan missing cold-panel line in Drafting Cycle block (DRAFTING_CYCLE.md §3)
EXIT: 0

=== Fold closing ===
WARN: Drafting Cycle closing indicates fold as last event, not a dry lens pass (DRAFTING_CYCLE.md §2)
EXIT: 0

=== T0 tier-only ===
PASS: (a) header — parsed
PASS: (a) dispatch_mode — bellows
PASS: (a) pause_for_verdict — always
EXIT: 0
(No drafting-cycle WARN — only tier declaration checked for T0)
```

### V4 — Degenerate/empty Drafting Cycle block

```
WARN: Drafting Cycle block missing lens(es): Weak spots, Destruction, Vulnerabilities, Integration, ACID (DRAFTING_CYCLE.md §3)
WARN: T2 plan missing cold-panel line in Drafting Cycle block (DRAFTING_CYCLE.md §3)
WARN: Drafting Cycle block has no **Closing:** line (DRAFTING_CYCLE.md §3)
PASS: (a) header — parsed
PASS: (a) dispatch_mode — bellows
PASS: (a) pause_for_verdict — always
EXIT: 0
```

No crash, no traceback. All missing elements degrade to WARNs.

### V5 — Existing test edit

```
$ git --no-pager diff HEAD~2..HEAD~1 -- tests/test_plan_lint.py | head -20
diff --git a/tests/test_plan_lint.py b/tests/test_plan_lint.py
index fc1fec6..acb363c 100644
--- a/tests/test_plan_lint.py
+++ b/tests/test_plan_lint.py
@@ -347,7 +347,7 @@ Some analysis goes here.
     result = _run_lint(plan)
     assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
     assert "(e)" not in result.stdout
-    assert "WARN" not in result.stdout
+    assert "consider using uppercase" not in result.stdout
```

One assertion narrowed from broad `"WARN" not in` to specific `"consider using uppercase" not in`. Original intent preserved (no step-heading-case WARN). Six new tests added (lines 370–477).

### V6 — Scope

```
$ git --no-pager diff --stat HEAD~2..HEAD~1
 .../plan-lint-drafting-gate-dev-2026-07-24.md      | 129 +++++++++++++++++++++
 scripts/plan_lint.py                               |  41 +++++++
 tests/test_plan_lint.py                            | 111 +++++++++++++++++-
 3 files changed, 280 insertions(+), 1 deletion(-)
```

### V7 — Full suite

```
$ python3 -m pytest tests/ --tb=short -q 2>&1 | cat
........................................................................ [  8%]
........................................................................ [ 17%]
........................................................................ [ 26%]
........................................................................ [ 35%]
........................................................................ [ 44%]
........................................................................ [ 53%]
........................................................................ [ 61%]
........................................................................ [ 70%]
........................................................................ [ 79%]
........................................................................ [ 88%]
........................................................................ [ 97%]
.....................                                                    [100%]
=============================== warnings summary ===============================
../../../../../Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35
  /Users/marklehn/Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020
    warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
813 passed, 1 warning in 21.02s
```

---

## Rule 20 — QA Self-Check Results

| Check | Result |
|---|---|
| Verification table present with one row per claim | PASS |
| All 7 claims independently verified with raw evidence | PASS |
| Evidence files deposited under `knowledge/qa/evidence/plan-lint-drafting-gate-2026-07-24/` | PASS |
| No code edits made (QA is verification-only) | PASS |
| RAW command output included (≥ last 200 lines incl. pytest summary) | PASS |

PASSED — SELF-CHECK PASSED

---

### Ledger Updates

#### Project Status

- **DRAFTING_CYCLE.md §4 self-check live in plan_lint, warn-first** — plans are now reminded to declare `cycle_tier` and carry the Cycle Log structure; all checks emit WARNs (non-blocking), never FAILs; blocking deferred to a future one-line WARN→FAIL flip.

#### Prompt Feedback

- Verification item 2 says "plan_lint on Done/executable-270.md emits NO drafting-cycle WARN" — but plan 270 legitimately emits the cold-panel WARN because it predates the Cold panel requirement. The DEV step correctly flagged this. The test fixture (COMPLIANT_T2_PLAN) uses 270's real block with the Cold panel line added, which does pass clean. Consider adjusting the plan's verification wording to reference the test fixture rather than the raw 270 file, since 270 is not fully compliant by current standards.

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Independently verified all 7 claims from the Step 2 verification table. Ran plan_lint against real plans (executable-265.md, executable-270.md) and synthetic plans covering every §4 rule. Confirmed warn-first posture (all exit 0), each rule fires independently, degenerate input degrades to WARNs without crashing, existing behaviour is intact (one narrowed assertion, intent preserved), scope is limited to plan_lint + tests, and the full suite passes (813 passed, 0 failures).

### Files Deposited
- `knowledge/qa/plan-lint-drafting-gate-qa-2026-07-24.md` — this QA report

### Evidence Files
- `knowledge/qa/evidence/plan-lint-drafting-gate-2026-07-24/full-suite.txt`
- `knowledge/qa/evidence/plan-lint-drafting-gate-2026-07-24/targeted-lint-tests.txt`
- `knowledge/qa/evidence/plan-lint-drafting-gate-2026-07-24/warn-first-verification.txt`
- `knowledge/qa/evidence/plan-lint-drafting-gate-2026-07-24/compliant-t2-plan-270.txt`
- `knowledge/qa/evidence/plan-lint-drafting-gate-2026-07-24/scope-diff-stat.txt`

### Decisions Made
- None — QA is verification-only, no code edits.

### Flags for CEO
- None. All checks pass.
