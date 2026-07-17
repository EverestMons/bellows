verdict: continue

**Final step. Telemetry test-pollution is fixed structurally — a full suite no longer dirties the corpus. Fast-follow (d) complete.**

## Verified — and this QA passed the gate CLEANLY

All 11 gates PASS with **no Monitor denial and no scope_check failure** — the first clean QA gate of the fuel arc. The three standing prohibitions written into the Step-2 prompt (no Monitor; don't fix failing tests; emit status via receipt not a direct PROJECT_STATUS write) ALL held. Naming the prior oversteps in plan text prevented their repeat — evidence the fix can live in the specialist prompt.

All **7 rows PASS**:
- **Row 1 (the proof):** `git status --short knowledge/telemetry/` CLEAN pre-suite AND CLEAN post-suite — the full ~2200-test suite no longer writes to the production corpus. Planner corroborated at targeted scale (49 telemetry tests → clean) before this run; QA confirmed at full-suite scale.
- **Row 6:** `2229 passed, 2 failed` — baseline 2227 + 2 Task-D anti-regression tests (Planner-checked arithmetic), the 2 failures the known CLAUDE.md pair. Zero regressions.
- Production path byte-unchanged; lazy resolution; the adversarial anti-regression test (snapshots the real production file, defeating the monkeypatch) present for both emitters.

## Consequence — retire a ritual

The wrap-time "check `git status knowledge/telemetry/` and revert test pollution" step I added two wraps ago is **no longer needed** — the suite can no longer pollute. The baton should retire that instruction (keep it only as history of why the fix exists).

## What remains (fast-follows, unbuilt)

The unresolved-conflict resolution UI; reject a non-last `99.999` sentinel at import; reject overlapping ranges. And the standing CEO-side threads: the 5 missing-continuation configs + 7/9 window re-check (PDF work), and the Windows git-gc/OneDrive issue.

Move the plan to `Done/`.
