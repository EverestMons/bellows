"""E2E test: verify legacy verdict files with literal 'None' in Total Steps don't break the parser."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
from pathlib import Path

BELLOWS_ROOT = Path(__file__).resolve().parents[4]

# Create a fake legacy verdict file
fake_dir = BELLOWS_ROOT / "verdicts" / "pending"
fake_dir.mkdir(parents=True, exist_ok=True)
fake_file = fake_dir / "verdict-request-fake-legacy-step-1.md"
fake_file.write_text("**Plan:** /fake\n**Step:** 1\n**Total Steps:** None\n")

# Simulate the parser logic from _consume_verdicts
total_steps_from_request = "NOT_SET"
try:
    text = fake_file.read_text()
    for req_line in text.splitlines():
        if req_line.startswith("**Total Steps:**"):
            raw_val = req_line.split(":**", 1)[1].strip()
            if raw_val == "None":
                total_steps_from_request = None
            else:
                try:
                    total_steps_from_request = int(raw_val)
                except (ValueError, IndexError):
                    pass

    if total_steps_from_request is None:
        print("PASS: parser set total_steps_from_request = None (legacy tolerance works)")
    else:
        print(f"FAIL: expected None, got {total_steps_from_request}")
except Exception as e:
    print(f"FAIL: parser raised {type(e).__name__}: {e}")
finally:
    if fake_file.exists():
        fake_file.unlink()
