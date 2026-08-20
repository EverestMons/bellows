verdict: continue

Terminal DIAG step of diagnostic 468 (full-suite temp-leak reclaim gap). Clean gate — self-issued under delegated verdict authority; header_pause, not a failure. All seven gate_events PASS and the declared deposit is present (`knowledge/research/full-suite-temp-leak-reclaim-gap-2026-08-19.md`, ~12 KB, read directly).

Planner (b) substance check — the findings answer Q1–Q5 with concrete, checkable specifics:
- Q1 enumerates 17 raw-TMPDIR sites with file:line, artifact, `delete=` value, and cleanup method, and correctly separates non-leaks (context managers, `__main__`-only blocks, mocked `mkstemp`). It surfaces two non-obvious details a static skim misses: sites 1–10 `os.unlink` the `.db` but NOT the SQLite `-shm`/`-wal` companions (leaked), and `test_pdf_parse_probe.py:321/337` unlink OUTSIDE `finally` (leak on assertion failure).
- Q3 confirms the reclaim gap precisely (the `_reclaim_test_tmp` fixture iterates only `tmp_path`; the 17 sites live in the parent raw TMPDIR).
- Q2 is HONEST about a measurement it could not run (guarded wrapper hardcodes the main repo, not the worktree) and materially REFRAMES the problem: the per-run residual from these sites is small (~330 KB normal / ~1.5 MB killed) — the multi-GB peak is driven by ACCUMULATION across repeated killed runs (finally blocks skipped on kill) plus pytest's 3-session `tmp_path` retention, not a single run leaking 6 GB. This corrects the working premise and matters for the fix.
- Q4 recommends Option (c) — a session-scoped `TMPDIR` redirect in conftest + `rmtree` at session end (one edit; catches present + future sites; makes bare `pytest tests/` self-contained; subsumes the external guarded wrapper). Q5 sets a checkable acceptance target (peak ≤ 50 MB, zero residual, bare full suite completes without ENOSPC).

The Option (c) recommendation is Planner-plausible and will be RE-VERIFIED by the fix executable's own drafting cycle — notably the `tempfile.tempdir` caching caveat (setting `os.environ["TMPDIR"]` after tempfile has resolved its dir is a no-op; the fixture must set it before any tempfile use or set `tempfile.tempdir` directly). Not vouched for here. Continue → move to Done.
