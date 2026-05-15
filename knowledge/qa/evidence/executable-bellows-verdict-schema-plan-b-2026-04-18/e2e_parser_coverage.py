"""Comprehensive parser smoke test — tests extract_primary_deposit against every format cluster."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
from verdict import extract_primary_deposit

test_cases = [
    # (a) cluster A — strict deposit
    ("**Deposit:** `freight-kb/knowledge/design/foo.md`",
     "freight-kb/knowledge/design/foo.md"),
    # (b) cluster A with interposed text
    ("**Deposit:** Write the full schema blueprint to `ai-career-digest/knowledge/architecture/bar.md`",
     "ai-career-digest/knowledge/architecture/bar.md"),
    # (c) cluster B bold-noun
    ("**Deposit dev log** to `bellows/knowledge/development/baz.md`",
     "bellows/knowledge/development/baz.md"),
    # (d) cluster B ALL-CAPS variant (re.IGNORECASE test)
    ("**WRITE THE QA REPORT** to `bellows/knowledge/qa/caps.md`",
     "bellows/knowledge/qa/caps.md"),
    # (e) cluster B Write variant
    ("**Write QA report** to `BrewBuddy/knowledge/qa/bb.md`",
     "BrewBuddy/knowledge/qa/bb.md"),
    # (f) cluster C inline prose
    ("Deposit QA report to `anvil/knowledge/qa/anv.md`",
     "anvil/knowledge/qa/anv.md"),
    # (g) cluster G inline prose "as"
    ("deposit as `forge/knowledge/research/forge.md`",
     "forge/knowledge/research/forge.md"),
    # (h) cluster H absolute path normalization
    ("**Deposit:** QA report to `/Users/marklehn/Desktop/GitHub/forge/knowledge/qa/abs.md`",
     "forge/knowledge/qa/abs.md"),
    # (i) feedback-exclusion
    ("Standard prompt feedback protocol \u2192 `bellows/knowledge/research/agent-prompt-feedback.md`",
     None),
    # (j) no-match
    ("This step has no primary deposit.",
     None),
]

passed = 0
failed = 0
for i, (input_text, expected) in enumerate(test_cases, 1):
    result = extract_primary_deposit(input_text)
    ok = result == expected
    status = "PASS" if ok else "FAIL"
    if ok:
        passed += 1
    else:
        failed += 1
    display = input_text[:80]
    print(f"  [{status}] case {i}: {display!r}")
    if not ok:
        print(f"         expected: {expected!r}")
        print(f"         got:      {result!r}")

print()
if failed == 0:
    print(f"OVERALL: PASS ({passed}/{passed + failed})")
else:
    print(f"OVERALL: FAIL ({passed} passed, {failed} failed)")
    sys.exit(1)
