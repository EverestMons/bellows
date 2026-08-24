verdict: continue

All eleven gates PASS. DEV-B substance spot-verified by the Planner in the
merged commit (936ef5e, 4 files / 427 insertions):

  - is_claimable: whole-body fail-toward-False, raw read_bytes hashing (6/19).
  - Claim-time re-check in run_plan: one read_bytes → hash → decode, with a
    _seen.discard on the refusal path so the arm can hold the drifted file —
    a correct touch the plan implied but did not spell (10/26).
  - consumed_at stamped inside mint_and_claim's own transaction (24) — this
    required a 9-line lifecycle.py delta; lifecycle.py sat in DEV-A's scope
    list, but consume-in-mint LIVES where mint lives, and the boundary was
    the split's imperfection, not the agent's. Recorded, not faulted.
  - The arm: sidecar-before-rename with hold_reason no_clearance, checks
    _seen and never adds (28/29/15); collect_group gated on full_path.
  - tools/clear_plan.py: 47 lines, preconditions + rename-to-ready re-entry.
  - 321 new test lines including the replay pair and mixed-group rows.

Step 3 (QA) is the full-suite + behavioral verification pass; proceeding.
