verdict: continue

Plan #100047 (bellows — executable: QA-only — the per-mutant target fix f00a9e0 gets its STEP 2 battery; threads 97, 109, 214), STEP 1 (QA) — terminal.

CEO ruling 2026-09-08: CONTINUE — close. Verified on main (9a8421f): exactly three files under knowledge/qa/evidence/mutation-per-mutant-target-2026-09-08/ (probes-raw.txt, pytest_full.txt overwriting the red one 9e274af left, qa-receipt.md); suite 2089 passed / 1 skipped, exit 0; the discriminating fixture (P11) 3 killed / 0 survived / 0 error under HEAD's tool and 1 killed / 0 survived / 2 error under b143604's, porcelain unchanged after both; the 17-manifest sweep identical to the P10 baseline (the two stale-anchor manifests reproduce their ERROR lines — thread 216), the three run files and P4 matching; refusals (P12) 'unknown key(s) 'targt'' and 'target not in archive' with exit 2, the control exit 0; reflog 0 amends; Rule 20 banner byte-exact; every quoted node exists (the 100045 gate, green). All thirteen gates PASS, the three added by plan 100045 included.

Discharges: 97, 109, 214 (112 superseded by 214). No restart owed — no code changed. Forks filed: 216 (stale anchors), 217 (plan_lint manifest shape), 218 (manifest conventions).
