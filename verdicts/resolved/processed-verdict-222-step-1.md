verdict: continue

**Rule 22(b) verified independently by the Planner — tests run, code read, the clean-status proof reproduced.**

## The fix is correct and the proof holds under the Planner's own run

- **Lazy resolution:** both emitters `import config`, define `_telemetry_path()`, and `record_*` uses `dest = path if path is not None else _telemetry_path()` — resolved at WRITE time, so the autouse `_isolate_knowledge_writes` fixture takes effect. No module constant is read.
- **Zero production change:** `_telemetry_path()` returns the byte-identical repo-root path the old `__file__` constant did — Planner-executed both, they match `<repo>/knowledge/telemetry/<file>.jsonl`.
- **The anti-regression test is genuinely adversarial:** `test_incidental_caller_writes_to_tmp_not_production` computes the REAL production path from `config.py`'s true location (defeating the monkeypatch), snapshots its size, calls the emitter with NO `path=` (an incidental caller), and asserts production is untouched. Exists for BOTH emitters. This is the test that would have caught the original pollution.
- **The proof, Planner-reproduced:** ran the 3 telemetry test files (49 passed), then `git status --short knowledge/telemetry/` → **CLEAN**. An emitter-exercising run no longer dirties the production corpus.

All 11 gates PASS; 6 scoped files; no schema change.

## Proceed to Step 2 (QA)

Row 1 is the whole point and must be run at FULL-SUITE scale (not just the telemetry files): `git status knowledge/telemetry/` clean → full suite foreground → `git status knowledge/telemetry/` STILL clean, both outputs raw. That is the direct proof the ~2200-test suite no longer pollutes. Row 6 baseline is **2227 passed, 2 failed** ± this plan's net test delta — verify and report ACTUAL, never force. The Step-2 prompt carries the three standing QA prohibitions (no Monitor, no fixing failing tests, no direct PROJECT_STATUS write) — whether they hold is itself worth noting in feedback.
