# project-producer QA receipt — 2026-08-31

Plan: executable-100005 — THE PROJECT PRODUCER (part A, tolerant by construction)

## Pre-flight

```
RESOLVED interpreter: /Users/marklehn/Developer/bellows/.venv/bin/python
VENV_OK
```

## Item 1 — Claim tests (redirected)

```
exit=0
```

Suite output file: `knowledge/dev-logs/project-producer-suite-2026-08-31.txt`

Contents:
```
.................................................                        [100%]
49 passed in 0.40s
```

49 passed, 0 failed. Unpiped redirect confirmed (not `| tee`).

## Item 2 — Full-suite control comparison

Baseline re-captured in this QA tree:

```
10 pre-existing failures:
FAILED tests/test_decisions.py::TestExtractDecisionBlocks::test_s_class_blocks_from_ground_truth
FAILED tests/test_decisions.py::TestLoadPhrases::test_includes_known_phrases
FAILED tests/test_decisions.py::TestLoadPhrases::test_loads_slash_alternatives
FAILED tests/test_decisions.py::TestLoadPhrases::test_splits_slash_alternatives
FAILED tests/test_notifier_server.py::test_server_respond
FAILED tests/test_phase4_planner_retry.py::test_planner_falls_back_to_continue_on_persistent_failure
FAILED tests/test_phase4_planner_retry.py::test_planner_retries_on_auth_failure
FAILED tests/test_planner.py::test_build_consult_file
FAILED tests/test_planner.py::test_consult_bad_json
FAILED tests/test_planner.py::test_consult_timeout
```

After-build totals: 10 failed, 1626 passed, 1 skipped in 61.60s

```
=== NEW failures (comm -13 qa-before qa-after) ===
(empty)

=== newly-passing (comm -23 qa-before qa-after) ===
(empty)
```

NEW-failure set is EMPTY. No regression introduced.

## Item 3 — Producer proven at the seam

`claim_for_deposit` called twice via monkeypatched `subprocess.run` (no live claim made):

**WITH project='bellows':**
```
cmd: ['/fake/tuyere/.venv/bin/python', '-m', 'tuyere.claims', 'claim', 'executable-100005',
      '--plan-class', 'shop-infra', '--project', 'bellows']
--project present: True
--project value: 'bellows'
outcome: ('proceed', 'claimed')
```

**WITHOUT project (default None):**
```
cmd: ['/fake/tuyere/.venv/bin/python', '-m', 'tuyere.claims', 'claim', 'executable-100005',
      '--plan-class', 'shop-infra']
--project absent: True
outcome: ('proceed', 'claimed')
```

`--project <value>` appears in the first call and no `--project` token appears in the second. No live claim was made — `subprocess.run` was monkeypatched and returned a mock.

## Item 3b — Resolver candidates

Quoting verbatim from the Step-1 dev log:

```
RESOLVED interpreter: /Users/marklehn/Developer/bellows/.venv/bin/python
RESOLVED builder: /Users/marklehn/Developer/eluvian-governance/governance/knowledge/decisions/drafts/build-project-producer.py
```

Interpreter: first candidate `$MAIN/.venv/bin/python` where `MAIN` = `git rev-parse --git-common-dir/..` (the main checkout, not the worktree). Builder: first fallback to `~/Developer/eluvian-governance` (not `$ELUVIAN_WRAP_ROOT`, which is absent from the daemon's environment). No silent fallthrough — both resolvers picked their expected candidate.

## Item 4 — Arm inert end-to-end

- `plan_claim_lock` in `bellows/config.json`: **advisory** (set by fork-1 work prior to this plan; unchanged by this plan)
- `project_lock` in `bellows/config.json`: **(absent)** — not set
- `project_lock` in `tuyere/config.json`: **(absent)** — not set

Neither value was changed by this plan. This plan makes the `--project` datum flow through the claim seam; it does not activate per-project enforcement. `project_lock` remains absent on both sides — tuyere records the project column but does not enforce exclusivity. Arm is INERT end-to-end.

## DEV commit receipt

Identified by tag (not HEAD-relative): `git log --oneline --grep "\[100005\]" -1`

```
b209c48 [100005] project producer: thread the project through the claim seam (part A, tolerant)
```

numstat for commit `b209c488ae599a8fc943f94cbaa711ec9ff59ab7`:

```
2   1   bellows.py
149 0   knowledge/dev-logs/project-producer-dev-2026-08-31.md
18  5   plan_claim.py
87  0   tests/test_plan_claim.py
```

Four files, matching the plan's deposit list.

Toplevel: `/Users/marklehn/Developer/bellows/.bellows-worktrees/100005`

```
git reflog -n 4:
b209c48 HEAD@{0}: reset: moving to HEAD
b209c48 HEAD@{1}: (prior entry)
```

0 amends confirmed (no `amend` in reflog entries).

---

## Verification

| Item | Description | Status |
|------|-------------|--------|
| 1 | Claim tests: 49 passed, 0 failed, exit=0, unpiped redirect | ✅ |
| 2 | Full-suite NEW-failure set empty vs QA-tree baseline | ✅ |
| 3 | `--project` present-when-supplied, absent-when-not at seam; no live claim made | ✅ |
| 3b | Both resolver candidates stated; no silent fallthrough | ✅ |
| 4 | `plan_claim_lock=advisory`, `project_lock=absent` on both sides; neither changed; arm INERT | ✅ |
| suite file | `project-producer-suite-2026-08-31.txt` written, non-empty | ✅ |
| qa file | `project-producer-qa-2026-08-31.md` written, non-empty | ✅ |

---

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100005/knowledge/dev-logs/
Files verified: 2
