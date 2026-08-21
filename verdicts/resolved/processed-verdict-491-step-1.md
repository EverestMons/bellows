verdict: continue

diag-491 (plan_lint check-(f) reads last-lens not final-walk class split — a re-verification of the check-(f) design) — read-only diagnostic, single step, paused on `header_pause` (clean). Continue closes the plan to Done (Total Steps: 1).

⚠️ CLOSE-WITH-CORRECTION (Planner-verified). This diagnostic is a near-DUPLICATE of the already-closed diag-489 (same Finding-6 characterization, same census, same parse spec), and its committed design-doc addition (`418d2af`, "post-executable re-verification confirms all findings") is STALE and MUST NOT be read as the authoritative outcome:
- Its "all findings confirmed" re-verification MISSED a real regression. The check-(f) parser it re-verified false-WARNs on 2 shipped plans — `diagnostic-429` and `executable-430` — whose FINAL dry walk is a `wN`-less line under a `**Walk N**` header (max-walk misread as an earlier walk).
- That regression was caught NOT by 491's re-verification but by the corpus-regression scan on exec-490 (133 unit tests passed; the corpus scan caught it), and FIXED in exec-492 (max-walk now reads `**Walk N**` headers + a `**Walk N STATUS:** instruction K` aggregate).
- Planner-verified at live HEAD: `plan_lint.py` on `diagnostic-429` and `executable-430` is now SILENT (exec-492's fix holds); full suite 134 green; whole-corpus scan clean.

Gate ALL-PASS on 491's own step (Gate Result Passed: True; failures: []; the single deposit `knowledge/research/plan-lint-check-f-class-split-design-2026-08-21.md` present; receipt/errors/permissions all PASS) — so `continue` is mechanically warranted; the correction above is the substantive record that 491's "confirms all findings" is superseded by the exec-490→492 arc, so a later reader of the design doc does not trust the stale confirmation. The authoritative check-(f) design + outcome is diag-489 + exec-492, not this plan.
