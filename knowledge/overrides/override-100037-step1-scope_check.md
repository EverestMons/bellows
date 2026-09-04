CEO-directed override, 2026-09-04, session 42ce7e32.

GATE: scope_check, step 1 of plan 100037. Out-of-scope file: tests/test_cycle_check.py.

WHY THE GATE WAS RIGHT: that file is not in the plan's declared Scope block. The refusal is correct and the omission is the Planner's.

WHY THE CHANGE IS NECESSARY, not a defect: closing FO-1 makes an emitted Cycle Manifest a precondition for BAR_MET. The shared _make_plan fixture helper in tests/test_cycle_check.py builds plans with no manifest, so after the change every existing test constructing one would receive CONTINUE instead of BAR_MET. The agent added a _MANIFEST_STANZA to the helper with include_manifest=True default and an opt-out. That is a fixture update required BY the change, which the Planner's Scope failed to anticipate.

VERIFIED BEFORE OVERRIDING, not read off the receipt:
  - assertion lines changed in that file: ZERO (git show, filtered to +/- lines containing 'assert')
  - test count in that file: 56 before, 56 after — none removed, none added
  - tests/test_cycle_check.py: 135 passed
  - the two new sibling suites: 20 passed
  - FO-1 demonstration: _manifest_validation_keys(halted-executable-100031) was None, now frozenset() — it REFUSES where it passed
  - FO-3 demonstration: _parse_qa_steps('none') -> set() — 'none' no longer demands a banner

MUST-PRESERVE CORRECTION: the plan's MUST-PRESERVE said "every existing cycle_check test unchanged". That was wrong as written — the FIXTURE had to change. The invariant that actually matters, and that holds, is "no assertion weakened, no test removed". The wording is corrected in the record rather than reinterpreted after the fact.

SCOPE OF THIS OVERRIDE: step 1's scope_check only. Step 2's QA re-runs the full suite from a worktree and re-verifies both demonstrations; nothing here pre-approves that.
