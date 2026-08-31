# project-producer dev log — 2026-08-31

Plan: executable-100005 — THE PROJECT PRODUCER (part A, tolerant by construction)

## A0 — Pre-flight

```
RESOLVED interpreter: /Users/marklehn/Developer/bellows/.venv/bin/python
VENV_OK
```

## P1–P3 (yours vs table)

| id  | pin                          | table value                                    | measured value                                 | note        |
|-----|------------------------------|------------------------------------------------|------------------------------------------------|-------------|
| P1  | claim-test baseline pre-build | 44 passed, 0 failed                           | 44 passed, 0 failed                            | matches     |
| P2  | sha plan_claim.py             | 08f82e409ce427b0                               | 08f82e409ce427b0                               | matches     |
| P2  | sha bellows.py                | f9855c305c8293f2                               | f9855c305c8293f2                               | matches     |
| P2  | sha tests/test_plan_claim.py  | 6e1101438c28b275                               | 6e1101438c28b275                               | matches     |
| P3  | --project occurrences         | 0 in plan_claim.py, 0 in bellows.py            | 0 in plan_claim.py, 0 in bellows.py            | matches     |

All pins match the table; no supersede required.

## A1 — Full-suite baseline (before build)

```
10
FAILED tests/test_decisions.py::TestExtractDecisionBlocks::test_s_class_blocks_from_ground_truth
FAILED tests/test_decisions.py::TestLoadPhrases::test_includes_known_phrases
FAILED tests/test_decisions.py::TestLoadPhrases::test_loads_phrases_from_file
FAILED tests/test_decisions.py::TestLoadPhrases::test_splits_slash_alternatives
FAILED tests/test_notifier_server.py::test_server_respond
FAILED tests/test_phase4_planner_retry.py::test_planner_falls_back_to_continue_on_persistent_failure
FAILED tests/test_phase4_planner_retry.py::test_planner_retries_on_auth_failure
FAILED tests/test_planner.py::test_build_consult_file
FAILED tests/test_planner.py::test_consult_bad_json
FAILED tests/test_planner.py::test_consult_timeout
```

10 pre-existing failures in this worktree. Saved to /tmp/before.txt.

## A2 — Builder output

```
RESOLVED builder: /Users/marklehn/Developer/eluvian-governance/governance/knowledge/decisions/drafts/build-project-producer.py
anchor E1-claim-for-deposit-sig (plan_claim.py): count=1
anchor E2-project-flag (plan_claim.py): count=1
anchor E3-claim-gate-sig (plan_claim.py): count=1
anchor E4-thread-through (plan_claim.py): count=1
anchor E5-docstring-exit4 (plan_claim.py): count=1
anchor E6-self-strand-cause (plan_claim.py): count=1
anchor E7-supply-project (bellows.py): count=1
anchor E8-tests (tests/test_plan_claim.py): count=1
WROTE plan_claim.py
WROTE bellows.py
WROTE tests/test_plan_claim.py
APPLIED: 8/8 edits.
```

## A3 — Verification

### A3.1 — py_compile

```
py_compile exit=0
```

### A3.2 — Claim tests post-build

```
.................................................                        [100%]
49 passed in 0.36s
```

49 passed, 0 failed (44 + 5 new). The HALT condition (non-zero failure count) does not fire.

### A3.3 — Full-suite control comparison

After run: 10 failed, 1626 passed, 1 skipped in 61.83s

```
=== NEW failures (must be EMPTY) ===

=== newly-passing (informational) ===

```

Both comm outputs are empty. NEW-failure set is EMPTY — no regression introduced.

### A3.4 — Earnability

Saved built file to /tmp/pc.built. Restored pre-plan content from git.

SHA guard:
```
sha first 16: 08f82e409ce427b0
SHA GUARD PASSED
```

Claim tests on pre-plan code:
```
FAILED tests/test_plan_claim.py::TestProjectProducer::test_project_appended_to_cmd_when_supplied
FAILED tests/test_plan_claim.py::TestProjectProducer::test_claim_gate_threads_project_through
FAILED tests/test_plan_claim.py::TestProjectProducer::test_self_strand_hint_suppressed_on_a_PROJECT_decline
3 failed, 46 passed in 1.11s
```

Exactly 3 failed as measured (not the predicted 5 — consistent with the plan's note that the prediction was wrong and the measured value is 3).

Restored from /tmp/pc.built. Re-verified:
```
49 passed in 0.28s
```

### A3.5 — Discrimination (mutants)

**M1** — drop `and "held: project " not in detail` from the hint condition:
```
FAILED tests/test_plan_claim.py::TestProjectProducer::test_self_strand_hint_suppressed_on_a_PROJECT_decline
1 failed, 48 passed in 0.94s
```
Exactly 1 failed. Positive twin test_self_strand_hint_still_fires_on_a_SLUG_decline stayed GREEN (in 48 passed). M1 KILLED.

**M2** — replace `if project:` + append with unconditional `cmd += ["--project", str(project)]`:
```
FAILED tests/test_plan_claim.py::TestProjectProducer::test_absent_project_omits_the_flag
1 failed, 48 passed in 0.33s
```
Exactly 1 failed. M2 KILLED.

**M3** — drop `project` from `claim_for_deposit(...)` call inside `claim_gate`:
```
FAILED tests/test_plan_claim.py::TestProjectProducer::test_claim_gate_threads_project_through
1 failed, 48 passed in 0.36s
```
Exactly 1 failed. M3 KILLED.

No mutant survived.

### A3.6 — git diff --stat

```
bellows.py               |  3 +-
plan_claim.py            | 23 ++++++++++---
tests/test_plan_claim.py | 87 ++++++++++++++++++++++++++++++++++++++++++++++++
3 files changed, 107 insertions(+), 6 deletions(-)
```

Exactly 3 files. ✓
