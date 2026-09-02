# checker-defects-2026-09-02 — dev log

**Date:** 2026-09-02
**Plan:** executable-100022

## Defects fixed

| ID | Script | Thread | Symptom |
|----|--------|--------|---------|
| C-1 | cycle_check.py | 52 | Vacuous CONTINUE for `- Walk N:` bullet lines with no parseable lens data |
| C-2 | cycle_check.py | 52 | WALK_REGISTER_RE captured whole line; long commentary → OSError ENAMETOOLONG crash |
| C-3 | cycle_check.py | 52 | Repo-relative register refs resolved only under git_root; unresolvable → N/A (accepted) → should escalate |
| F58 | cycle_check.py | 58 | CLOSURE_RE matched `**Closing:**` heading itself; NOT CLOSED plans escaped |
| F63a | cycle_yields.py | 63 | `weak\s*spots:` didn't match hyphenated `Weak-spots:` |
| F63b | plan_lint.py | 63 | Same pattern in lint's `required_lenses` list |
| F77 | plan_lint.py | 77 | `rule_20_self_check` reads FIRST `.md` in QA Deposits; no lint check enforced `qa-receipt.md` first |

## Script changes

### `scripts/cycle_check.py`

**C-1 (walk-signal guard):** Added `has_walk_signal` check in `run_check` using regex
`r"(?im)^\s*-\s*Walk\s+[1-9]\d*\b|\bw[1-9]\d*\s+(?:\d+\s+folded|dry)\b"`.
Walk 0 (context pin) excluded. `**Walk N:**` bold-heading prose (legacy format) also excluded —
those plans return CONTINUE. When a walk signal is present but `walk_data={}` → `ESCALATE:unparseable`.

**C-2 (commentary extraction):** `parse_block` now extracts only the backtick-quoted token or the first
`.md`-ending token from the raw register line, ignoring trailing commentary text. OSError guard
added around `(git_root / ref).exists()` and `(gov_root / ref).exists()` calls.

**C-3 (governance-root fallback):** `check_assert_2` uses three-step resolution:
step 1 = absolute path, step 2 = `git_root / ref`, step 3 = `resolve_governance_root() / ref`.
Unresolved refs produce `"UNRESOLVED"` (not `"N/A"`). The assert gate was widened:
`if a2_reg in ("FAIL", "UNRESOLVED"):` → `ESCALATE:assert-fail:2`.

**F58 (NOT CLOSED):** Replaced `CLOSURE_RE` with `_NEGATION_RE` + `_CLAIM_RE` + `_has_closure_claim()`.
Negation (`NOT CLOSED`, `not met`, `unmet`) is stripped before searching for claim tokens
(`BAR MET`, `met the bar`, `CYCLE COMPLETE`). Bare `**Closing:**` heading is no longer a claim.

### `scripts/cycle_yields.py`

**F63a:** `LENS_PREFIXES` weak-spots pattern changed from `^weak\s*spots\s*:` to
`^weak[\s-]*spots\s*:` to accept the hyphenated spelling `Weak-spots:`.

### `scripts/plan_lint.py`

**F63b:** `required_lenses` tuple pattern for Weak spots changed from `r'weak\s*spots'` to
`r'weak[\s-]*spots'`.

**F77 ((u) check):** New WARN-only check after QA steps cross-check: for each QA step, if the
Deposits list has `.md` entries and the first `.md` basename doesn't contain `receipt`, emit
`(u) WARN: step N Deposits: first .md is '...' — rule_20_self_check reads the first .md as the QA report`.
Also warns if no `.txt` evidence entry is present.

## Fail-before / pass-after node IDs

The following 12 tests FAIL against the pre-edit HEAD scripts and PASS against the edited scripts:

```
FAIL (pre-edit) → PASS (post-edit):
  tests/test_cycle_check.py::test_c1_plain_walk_lines_escalate
  tests/test_cycle_check.py::test_c2_commentary_ref_extracted_cleanly
  tests/test_cycle_check.py::test_c2_long_component_no_traceback
  tests/test_cycle_check.py::test_c3_relative_ref_unresolvable_escalates
  tests/test_cycle_check.py::test_58_not_closed_returns_continue
  tests/test_cycle_check.py::test_58_bare_heading_not_a_claim
  tests/test_cycle_check.py::test_63_hyphenated_weakspots_lens_parsed
  tests/test_cycle_yields.py::test_63_hyphen_weakspots_not_none
  tests/test_cycle_yields.py::test_63_hyphen_weakspots_is_dry
  tests/test_plan_lint.py::test_lint_weak_spots_hyphen_no_warn
  tests/test_plan_lint.py::test_u_report_first_warns
  tests/test_plan_lint.py::test_u_no_txt_warns
```

3 additional tests pass both before and after (negative tests or verdict-level tests
whose verdict is unchanged by the fix):
```
  tests/test_cycle_check.py::test_63_hyphenated_lens_yields_bar_met
  tests/test_cycle_check.py::test_walk_register_governance_root_fallback
  tests/test_plan_lint.py::test_u_receipt_first_no_warn
```

## Corpus canaries (after fix)

All governance Done/ plans with a Drafting Cycle section:
- 36 plans: OK (BAR_MET or CONTINUE) — no regressions vs. pre-edit behavior
- 5 plans: ESCALATE:unparseable — pre-existing (same result before and after edit)
  - `diagnostic-285.md`, `diagnostic-308.md`, `executable-309.md`, `executable-373.md`, `executable-432.md`
- Notable: `executable-451.md` (CEO-directed deposit; `**Walk N:**` prose in DC block, no lens lines)
  returned CONTINUE both before and after edit after narrowing the C-1 signal regex to exclude
  `**Walk N:**` bold-heading prose.

## Fixture canaries (five new fixtures)

| Fixture | Before fix | After fix |
|---------|-----------|-----------|
| `plainonly.md` | CONTINUE | ESCALATE:unparseable |
| `longref2.md` | ESCALATE:assert-fail:2 or OSError crash (depending on path length) | ESCALATE:assert-fail:2 (no traceback) |
| `notclosed.md` | ESCALATE:claimed-close-unmet | CONTINUE |
| `hyphen.md` | `parse_lens_line("- Weak-spots: w1 dry")` → None | returns lens tuple; BAR_MET |
| `relref.md` | BAR_MET (N/A accepted, not escalated) | BAR_MET (PASS via governance-root fallback) |

## plan_lint (u) probes

- `governance/knowledge/decisions/halted-executable-328.md` step 2: fires `(u) WARN` (first .md is
  `seat-brief-codification-qa-2026-08-08.md`, not a receipt) — correct
- `eluvian-governance/...executable-100007.md` step 3: fires `(u) WARN` (first .md is
  `lessons-report-2026-09-01.md`, not a receipt) — correct
- Other drafts (halted-diagnostic-508, halted-executable-420, halted-executable-558): no (u) WARNs — correct

## Module import isolation fix (tests only)

When the full test suite runs, `depositor.py` (imported transitively via `bellows.py`) calls
`resolve_bellows_root()` which returns the MAIN checkout, causing `cycle_check` and `cycle_yields`
to be cached in `sys.modules` from the main checkout's pre-edit `scripts/` directory.

Fix: added module-cache invalidation guards at the top of `test_cycle_check.py` and
`test_cycle_yields.py` — if the cached module came from outside the worktree's `scripts/`, it is
deleted from `sys.modules` before the test file imports it fresh from the right path.

## Mutation manifests

Three manifests written (QA runs `tools/mutation_check.py` after commit — Item 2.5):
- `knowledge/mutants/checker-defects-cycle_check.json` — M1 (C-1 guard), M2 (negation strip), M3 (OSError guard), M4 (UNRESOLVED accept)
- `knowledge/mutants/checker-defects-cycle_yields.json` — M5 (weak-spots prefix)
- `knowledge/mutants/checker-defects-plan_lint.json` — M6 (lint pattern), M7 ((u) first-.md test)

## Suite line

```
1782 passed, 1 skipped in 49.29s
```

Full command: `"$BPY" -m pytest tests -q -p no:cacheprovider`

106 new tests added (1782 − 1676 baseline).
