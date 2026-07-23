verdict: continue
Plan 263 Step 2 (QA) — terminal close authorized by the Planner with CEO approval, OVERRIDING the rule_20_self_check gate failure.

The gate failure is real but a QA-report-hygiene slip, not a substantive failure. The QA report is missing the byte-exact `Rule 20 — QA Self-Check Results` banner (grep count 0). Cause (Events 341/344): the QA agent's own non-ASCII grep used a perl `\x00` pattern that embedded a NUL byte in the report; while rewriting to remove it, the agent dropped the Rule 20 self-check block. No NUL remains; the report is otherwise clean ASCII.

Everything the banner attests to is independently confirmed:
- rule_22_verification PASSED (evidence files present, verification table clean, no hedging keywords) — the substance of the Rule 20 self-check.
- 7/7 QA rows PASS (Event 363): no non-ASCII in the script, `encoding="utf-8"` write, receipt `content.encode("ascii")` succeeds, the regression test asserts ASCII (2/2 pass), isolation (`knowledge/handoff/` clean before/after), README documents the Windows-safe convention.
- Full suite 2361 passed / 2 known pre-existing failures (the CLAUDE.md pair) / 0 regressions (846s).
- Planner-independent: the fix works — the receipt now reads `!= monday` (ASCII), and both non-ASCII chars (`≠` U+2260 + the docstring em-dash U+2014) are gone; `encoding="utf-8"` is on the write.

CEO approved the override (2026-07-23). Record defect noted: the Done/ QA report lacks the Rule 20 banner — a one-off from this NUL-byte rewrite, NOT a general rule_20 waiver.

Terminal step — proceed to close (move plan 263 to Done/, merge the fix to invoice-pulse main).
