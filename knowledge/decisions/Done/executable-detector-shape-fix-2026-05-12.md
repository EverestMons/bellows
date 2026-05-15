---
type: executable
project: bellows
created: 2026-05-12
auto_close: false
pause_for_verdict: after_step_1
---

# Executable — Detector NDJSON Shape Fix + Fixture Rewrite + Observability Addition

**Execution Map:** Step 1 (BELLOWS_DEVELOPER) → Step 2 (BELLOWS_QA)

**Context:** The 2026-05-12 canary diagnostic (`Done/diagnostic-canary-detector-validation-2026-05-12.md`) found that `bellows/decisions.py::extract_decision_blocks` reads `event.get("content", [])` from NDJSON assistant events, but the real Claude CLI stream uses `event.get("message", {}).get("content", [])`. The detector returns zero matches on every real plan because the iteration never finds any text blocks. The Step 1 unit tests passed because their synthetic fixtures used the flat shape, not the wrapped shape that production emits. This plan ships three changes: (a) fix the NDJSON parse path, (b) rewrite affected test fixtures to use the real wrapped shape, (c) add `decisions.py` to `_module_fingerprints()` for observability (BACKLOG note from the 2026-05-12 Step 1 verdict). Out of scope: retry canary (separate plan, requires re-engineered task design); subprocess-based integration tests (larger scope, not necessary for this fix). Step 2 QA includes a real-data behavioral test pointing the fixed detector at a production step.json with known phrase-matched narration.

---

## STEP 1 — BELLOWS_DEVELOPER

Read your specialist file first. **Part A — NDJSON shape fix.** Open `bellows/decisions.py`. Find the assistant-event iteration inside `extract_decision_blocks()` — currently reads `content = event.get("content", [])`. Change to `content = event.get("message", {}).get("content", [])` to match the real Claude CLI NDJSON shape. Do NOT add backward-compatibility for the flat shape — the flat shape was never produced by Claude CLI and supporting it preserves the bug-friendly surface. After the fix, verify by inspecting one assistant event in `bellows/logs/20260512-184339-step.json` (the canary's step.json): the event has top-level keys `["type", "message", "parent_tool_use_id", "session_id", "uuid"]` with content nested under `message.content`. **Part B — fixture rewrite.** Open `bellows/tests/test_decisions.py`. Find every synthetic NDJSON event constructed in tests — specifically the 6-S-block ground-truth test (`test_s_class_blocks_from_ground_truth` per the QA report at line 66) and any other tests passing event dicts to `extract_decision_blocks`. Rewrite every assistant-event fixture to use the real wrapped shape: `{"type": "assistant", "message": {"content": [{"type": "text", "text": "<text>"}]}}` instead of `{"type": "assistant", "content": [{"type": "text", "text": "<text>"}]}`. The 6-S-block test should still pass after the rewrite. If any test fails after the fixture rewrite, do NOT adjust the test assertions to make them pass — investigate why. The point of the rewrite is to validate that the detector works against the real shape, not to preserve passing-test-count. **Part C — `_module_fingerprints()` addition.** Open `bellows/bellows.py`. Find `_module_fingerprints()` — it currently tracks 5 modules (`bellows.py`, `gates.py`, `verdict.py`, `parser.py`, `runner.py`). Add `decisions.py` as the 6th module so the new detector module appears in startup banner and heartbeat fingerprints. If the function uses a literal list or constant, update it; if it iterates a directory, no change may be needed (verify). Update the existing test for `_module_fingerprints()` (find it via grep) to expect 6 modules instead of 5. **Run the full test suite.** Report total pass/fail counts; the pre-existing `test_run_step_timeout` failure should remain (unchanged from this plan's scope). **Commit message:** `fix(bellows): detector NDJSON shape + module fingerprint observability`. Deposit a dev log at `bellows/knowledge/development/detector-shape-fix-dev-log-2026-05-12.md` covering: exact line(s) changed in `decisions.py`, count of fixtures rewritten in `test_decisions.py`, change made in `_module_fingerprints()`, test count delta, any decisions made on initiative.

**Deposits:**
- `bellows/decisions.py`
- `bellows/tests/test_decisions.py`
- `bellows/bellows.py`
- `bellows/tests/test_bellows.py`
- `bellows/knowledge/development/detector-shape-fix-dev-log-2026-05-12.md`

---

## STEP 2 — BELLOWS_QA

Read your specialist file and the Rule 20 self-check canonical block at `/Users/marklehn/Desktop/GitHub/RULE_20_SELF_CHECK_BLOCK.md` first. **FIRST — Deliverable Verification.** Read Step 1's Output Receipt. For each modified file: confirm it exists, contains the described change (grep for key content), and the change matches the dev log description. Produce a verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |`. Specific anchors: (1) `decisions.py` reads `event.get("message", {}).get("content", [])` — grep for the literal string; (2) `test_decisions.py` fixtures use `"message": {"content"` wrapping — grep for the literal pattern and report the count of occurrences (should match the count of assistant-event fixtures); (3) `bellows.py::_module_fingerprints()` includes `decisions.py` — grep for `decisions` in the function; (4) `test_bellows.py` expects 6 modules from the fingerprint function — grep for the assertion. If ANY item is ❌, attempt to fix; if unfixable, stop and report. **Behavioral Verification — Real-Data Detection Test.** Point the fixed detector at a real production step.json file with known phrase-matched narration. Pick `bellows/logs/20260512-103456-step.json` (a step from earlier today's intermediate-decision-detector executable Step 1 — multi-file DEV work likely to contain narration phrases). Load the JSON, extract `raw_output`, parse it as NDJSON, call `decisions.extract_decision_blocks(raw_output, decisions.load_phrases())`. Assert the result is a non-empty list. If empty, run the same call against `bellows/logs/20260512-184339-step.json` (the canary's step.json — known to have 3 assistant text blocks but 0 phrase matches per the canary diagnostic, so this should return empty as a control). Document both results in the QA report. The point of this test is end-to-end validation: real production data → working detector → non-empty matches when narration contains phrases. The canary's step.json serves as a negative control (empty result expected). **Run the full test suite.** Report pass/fail counts. **Rule 20 self-check** per the canonical block. Evidence files at `bellows/knowledge/qa/evidence/detector-shape-fix-qa-2026-05-12/`: deliverable-verification grep outputs, real-data detection test output (both files' detector results), test suite output. **Final:** Update `bellows/PROJECT_STATUS.md` — add a milestone entry summarizing the detector shape fix, fixture rewrite, and module fingerprint observability addition. Append to `bellows/feedback.log`: `2026-05-12 — detector NDJSON shape fix shipped — wrapped event.message.content path + fixtures rewritten + decisions.py added to module fingerprints, test count <pre>→<post>`. Final commit message: `docs: PROJECT_STATUS + feedback for detector shape fix`. **STOP.** Do NOT move this plan to Done/. Per the disable-auto-close model, the Planner performs the terminal move after Rule 22 verification passes.

**Deposits:**
- `bellows/knowledge/qa/detector-shape-fix-qa-2026-05-12.md`
- `bellows/knowledge/qa/evidence/detector-shape-fix-qa-2026-05-12/`
- `bellows/PROJECT_STATUS.md`
- `bellows/feedback.log`
