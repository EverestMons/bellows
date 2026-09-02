# checker-defects-2026-09-02 — QA Receipt

**Date:** 2026-09-02  
**Plan:** executable-100022  
**Slug:** checker-defects-2026-09-02  
**Step:** 2 (QA)  
**Evidence dir:** `knowledge/qa/evidence/checker-defects-2026-09-02/`

---

## Verification Table

| Item | What was checked | Status |
|------|-----------------|--------|
| Step 1 commit present | HEAD = e088d05; files match Step 1 Deposits | ✅ |
| Pre-edit SHA match (P1) | `cycle_check.py` `2efd4e2de1a3f9ea`, `cycle_yields.py` `439f2a7f9393305b`, `plan_lint.py` `fabbf1ac2d8ad95a` — all match | ✅ |
| Item 1 — fail-before (module-level) | 8 of 12 tests FAIL against pre-edit modules: C-1, C-2 commentary, C-3, 58 NOT-CLOSED, 58 bare-heading, 63 hyphen (cycle_check), 63 hyphen (cycle_yields ×2) | ✅ |
| Item 1 — fail-before (subprocess tests) | 4 subprocess tests verified via direct pre-edit invocation: C-2 long-component crashes with `OSError: [Errno 63]`; lint weak-spots hyphen fires `missing lens(es): Weak spots`; lint (u) tests show no `(u)` in pre-edit output | ✅ |
| Item 1 — pass-after | All 12 tests PASS against post-edit scripts: 12/12 | ✅ |
| Item 2 — corpus canaries (held drafts) | 5 drafts: bellows-bootstrap, shop-server-invariant-sketch, shop-server-invariant-company, gate2-pt-w28-a, forge-cycle-w29 → BAR_MET 5/5 | ✅ |
| Item 2 — corpus canaries (Done plans) | bellows Done: 100005–100021 (10 files); forge_lessons Done: 100007, 100008, 100016, 100020 (4 files) → BAR_MET 14/14 | ✅ |
| Item 2 — fixture plainonly.md | ESCALATE:unparseable | ✅ |
| Item 2 — fixture longref2.md (lintmirror- staged inside) | ESCALATE:assert-fail:2, 0 tracebacks; lintmirror count after delete: 0 | ✅ |
| Item 2 — fixture notclosed.md | CONTINUE | ✅ |
| Item 2 — fixture hyphen.md | BAR_MET; `parse_lens_line("- Weak-spots: w1 dry")` → non-None | ✅ |
| Item 2 — fixture relref.md | BAR_MET (governance-root fallback); nonexistent register variant → ESCALATE:assert-fail:2 | ✅ |
| Item 2.5 — kill map cycle_check | M1 KILLED, M4 KILLED; M2 SURVIVED (Critical), M3 SURVIVED (Critical) | ❌ |
| Item 2.5 — kill map cycle_yields | M5 KILLED, 0 survived | ✅ |
| Item 2.5 — kill map plan_lint | M6 KILLED, M7 KILLED, 0 survived | ✅ |
| Item 3 — (u) five drafts | 0 `(u)` warnings each; 5/5 | ✅ |
| Item 3 — (u) 100007 step 3 | 1 `(u)` WARN naming `lessons-report-2026-09-01.md` | ✅ |
| Item 3 — (u) synthetic no-txt | Both `(u)` WARNs fire: report-first WARN + no-.txt WARN | ✅ |
| Item 3 — plan_lint exit codes | 19 corpus files: exit=0 for all 19 under new plan_lint | ✅ |
| Item 4 — full suite | `full-suite-checker-defects.txt`: 1782 total, exit=0, 0 failed | ✅ |

---

## Critical Findings — Item 2.5

**Critical: M2-drop-negation-stripping SURVIVED.**  
`expect_fail`: `tests/test_cycle_check.py::test_58_not_closed_returns_continue`.  
The test fixture contains `NOT CLOSED` (not `NOT BAR MET`). With negation stripping removed, `_CLAIM_RE` searches for `\bBAR MET\b|met the bar|CYCLE COMPLETE` in the unmodified block; none appear in `NOT CLOSED` text, so the verdict is still CONTINUE and the test still passes. A test with `**Closing:** NOT BAR MET — bar not met.\n` → CONTINUE would discriminate this mutant.

**Critical: M3-drop-oserror-guard SURVIVED.**  
`expect_fail`: `tests/test_cycle_check.py::test_c2_long_component_no_traceback`.  
This test runs cycle_check.py via subprocess. The C-2 extraction fix (part 1 of the fix) strips commentary to the first `.md` token *before* the OSError guard is reached, so the path passed to `.exists()` is always short. With M3 applied (guard changed from `except OSError` to `except ValueError`), no OSError is ever raised and the test assertions still pass. The guard is dead code in the post-extraction code path for this test. A unit-level test calling `(very_long_path).exists()` inside `check_assert_2` would be needed to discriminate.

---

## Follow-ups

1. **Daemon restart** — the modified scripts are committed; the Bellows daemon must be restarted to pick up the updated `scripts/cycle_check.py`, `scripts/cycle_yields.py`, and `scripts/plan_lint.py`.
2. **Threads 52, 58, 63, 77 closure** — these four tuyere threads are closed at the keyboard after QA acceptance.
3. **Next drafting cycle as the canary** — the next plan through the checker will be the live integration test for all five fixes.
4. **M2 kill-gap follow-up** — a follow-up plan should add a `test_58_not_bar_met_stripped` case (`**Closing:** NOT BAR MET — bar not met.` → CONTINUE) to kill the M2 mutant. (The negation stripping is correct code; the test gap is a coverage debt.)
5. **M3 kill-gap note** — M3's guard is now largely dead code after the extraction fix. It remains as defensive depth-of-field. No separate plan required unless the team decides to remove it.

---

<!-- Rule 20 self-check output appended below -->

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100022/knowledge/qa/evidence/checker-defects-2026-09-02/
Files verified: 2
