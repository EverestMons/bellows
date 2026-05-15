# QA Report — Verdict Schema Plan B (Deposit Field Parser)
**Date:** 2026-04-18 | **Plan:** executable-bellows-verdict-schema-plan-b-2026-04-18

## Deliverable Verification (Rule 17)

| # | Deliverable | Expected | Status | Evidence |
|---|-------------|----------|--------|----------|
| 1 | Regex constants in verdict.py | STRICT_DEPOSIT_RE, BOLD_NOUN_DEPOSIT_RE, INLINE_DEPOSIT_RE, FEEDBACK_EXCLUSION_RE — 4 module-level assignments | ✅ | `knowledge/qa/evidence/executable-bellows-verdict-schema-plan-b-2026-04-18/grep_regex_constants.txt` |
| 2 | BOLD_NOUN_DEPOSIT_RE includes re.IGNORECASE | Load-bearing for ALL-CAPS variant | ✅ | `knowledge/qa/evidence/executable-bellows-verdict-schema-plan-b-2026-04-18/grep_ignorecase_flag.txt` |
| 3 | extract_primary_deposit function | def extract_primary_deposit(step_text: str) -> Optional[str] in verdict.py | ✅ | `knowledge/qa/evidence/executable-bellows-verdict-schema-plan-b-2026-04-18/grep_extract_function.txt` |
| 4 | Deposit field in content template | **Deposit:** line in post_verdict_request f-string, exactly once | ✅ | `knowledge/qa/evidence/executable-bellows-verdict-schema-plan-b-2026-04-18/grep_deposit_field.txt` |
| 5 | Extractor source — single location | Local def in verdict.py (not imported from bellows, avoids circular import) | ✅ | `knowledge/qa/evidence/executable-bellows-verdict-schema-plan-b-2026-04-18/grep_extractor_source.txt` |
| 6 | Call site updates in bellows.py | Both post_verdict_request calls pass step_text=plan_text (lines 274, 333) | ✅ | `knowledge/qa/evidence/executable-bellows-verdict-schema-plan-b-2026-04-18/grep_call_sites.txt` |

## Targeted Test Run

- **Result:** 93 passed, 11 failed
- **Exit code:** 1 (due to pre-existing runner failures)
- **Pre-existing failures (11):** All in test_runner.py (10) and test_runner_parser.py (1) — unchanged from Plan A baseline
- **Verdict + bellows tests:** 93/93 passing — no regressions
- **Evidence:** `knowledge/qa/evidence/executable-bellows-verdict-schema-plan-b-2026-04-18/pytest_targeted.txt`

## QA Fix — INLINE_DEPOSIT_RE regex gap

During parser coverage testing, case (g) "deposit as `path`" (cluster G — zero-noun-phrase before preposition) failed. Root cause: original regex `[\w\s]+?` required at least 1 character between verb and preposition. Fix applied: changed to `(?:[\w]+\s+)*` which allows zero or more word+space groups before the preposition. Fix verified: all 10 parser cases pass, all 93 non-runner tests pass, no regressions.

**Changed:** `verdict.py:15` — `INLINE_DEPOSIT_RE` pattern updated.

## Parser Coverage Smoke Test (10 cases)

| # | Cluster | Input (truncated) | Expected | Status |
|---|---------|-------------------|----------|--------|
| 1 | A | `**Deposit:** \`freight-kb/knowledge/design/foo.md\`` | freight-kb/knowledge/design/foo.md | ✅ |
| 2 | A+text | `**Deposit:** Write the full schema blueprint to \`ai-career-...` | ai-career-digest/knowledge/architecture/bar.md | ✅ |
| 3 | B | `**Deposit dev log** to \`bellows/knowledge/development/baz.md\`` | bellows/knowledge/development/baz.md | ✅ |
| 4 | B-CAPS | `**WRITE THE QA REPORT** to \`bellows/knowledge/qa/caps.md\`` | bellows/knowledge/qa/caps.md | ✅ |
| 5 | B-Write | `**Write QA report** to \`BrewBuddy/knowledge/qa/bb.md\`` | BrewBuddy/knowledge/qa/bb.md | ✅ |
| 6 | C | `Deposit QA report to \`anvil/knowledge/qa/anv.md\`` | anvil/knowledge/qa/anv.md | ✅ |
| 7 | G | `deposit as \`forge/knowledge/research/forge.md\`` | forge/knowledge/research/forge.md | ✅ |
| 8 | H | `**Deposit:** QA report to \`/Users/marklehn/Desktop/GitHub/...` | forge/knowledge/qa/abs.md | ✅ |
| 9 | Excl | `Standard prompt feedback protocol → \`bellows/...` | None | ✅ |
| 10 | None | `This step has no primary deposit.` | None | ✅ |

**Overall:** PASS (10/10)
**Evidence:** `knowledge/qa/evidence/executable-bellows-verdict-schema-plan-b-2026-04-18/e2e_parser_coverage.txt`

## E2E Verdict Write — Deposit Field Populated

- **Input:** step_text containing `**Deposit findings** to \`bellows/knowledge/research/smoke-test.md\``
- **Assert:** `**Deposit:** bellows/knowledge/research/smoke-test.md` in output, `**Deposit:** none` absent
- **Result:** PASS
- **Evidence:** `knowledge/qa/evidence/executable-bellows-verdict-schema-plan-b-2026-04-18/e2e_verdict_deposit_field.txt`

## E2E Verdict Write — None Path

- **Input:** step_text = "This step has no deposits. Just commits code."
- **Assert:** `**Deposit:** none` appears exactly once
- **Result:** PASS
- **Evidence:** `knowledge/qa/evidence/executable-bellows-verdict-schema-plan-b-2026-04-18/e2e_verdict_none_path.txt`

## Overall Status

**PASS** — All deliverables verified, all tests pass (ignoring 11 pre-existing runner failures), parser covers all format clusters including QA-discovered edge case fix, e2e integration confirmed.

## Rule 20 — QA Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: knowledge/qa/evidence/executable-bellows-verdict-schema-plan-b-2026-04-18/
Files verified: 13
```
