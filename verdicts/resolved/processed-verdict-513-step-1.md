verdict: continue

Single gate FAIL: scope_check on tests/test_depositor.py — diagnosed as a
NECESSARY consequence of the plan's own mandate, not scope creep, and the
substance verified by the Planner from the merged commit (4fdf55a):

  - The corrected `_assign_class(writes, project_root)` signature and the
    ruled taxonomy BREAK three existing depositor tests by design. The 12-line
    delta is exactly that fallout: test_governed_tooling_class renamed and
    re-expected to shop-infra (the ruled name), DRAFTING_CYCLE.md re-expected
    shop-infra (root doctrine per the rule), and a mock wrapper widened to
    *args for the new arity. Nothing else in the file moved. The plan's own
    hot-path-guard warning predicted this class; the scope list simply never
    named the file — an authoring gap the panel's step-split did not close.
  - Substrate spot-verified in the diff: clearances DDL with consumed_at and
    the PARTIAL unique index (content_hash, plan_path) WHERE consumed_at IS
    NULL (correction 23); INSERT OR IGNORE; has_clearance requiring
    unconsumed (14); clearance write from raw read_bytes (19) storing the
    claimable path pre-rename (25/4); _assign_class taking project_root with
    a None/unassignable route (1/12); plan_lint class set + gates allowlist
    one-liners (8/17); 393-line test_admission_flip.py.
  - Receipt reports targeted tests green; py_compile four files.

DISPOSITION: tests/test_depositor.py JOINS the change set retroactively — the
Step-3 QA treats it as in-baseline, and its 12 lines are covered by Q2's
change-set review. Recorded for the wrap sweep: a signature change's test
fallout belongs in Scope at authoring time; the panel reviewed the plan's
files, not the change's blast radius.

Also on the record: the merge window carried a concurrent session's bellows
wrap commit (e6f87f1, consuming ITS plan-512 verdict) — shared-repo reality,
no interference with this step's diff. Proceeding to Step 2 (DEV-B).
