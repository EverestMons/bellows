"""DEV-side manual parser smoke test for extract_primary_deposit()."""
import sys
sys.path.insert(0, "/Users/marklehn/Desktop/GitHub/bellows")
from verdict import extract_primary_deposit

test_cases = [
    (
        "Cluster A",
        "**Deposit:** `bellows/knowledge/research/foo.md`",
        "bellows/knowledge/research/foo.md",
    ),
    (
        "Cluster B bold-noun",
        "**Deposit dev log** to `bellows/knowledge/development/bar.md`",
        "bellows/knowledge/development/bar.md",
    ),
    (
        "Cluster B ALL-CAPS",
        "**WRITE THE QA REPORT** to `bellows/knowledge/qa/baz.md`",
        "bellows/knowledge/qa/baz.md",
    ),
    (
        "Cluster C inline",
        "Deposit QA report to `bellows/knowledge/qa/qux.md`",
        "bellows/knowledge/qa/qux.md",
    ),
    (
        "Feedback exclusion",
        "Standard prompt feedback protocol \u2192 `bellows/knowledge/research/agent-prompt-feedback.md`",
        None,
    ),
]

all_pass = True
for label, input_text, expected in test_cases:
    result = extract_primary_deposit(input_text)
    status = "PASS" if result == expected else "FAIL"
    if status == "FAIL":
        all_pass = False
    print(f"{status}: {label} | got={result!r} expected={expected!r}")

print()
print("OVERALL:", "PASS" if all_pass else "FAIL")
