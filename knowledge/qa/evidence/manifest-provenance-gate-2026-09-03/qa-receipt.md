# QA Receipt — manifest-provenance-gate-2026-09-03

**Plan:** `executable-100033.md` | **Step:** 2 (QA) | **Date:** 2026-09-04 | **Agent:** Claude Sonnet 4.6

**Plan slug:** `manifest-provenance-gate-2026-09-03`

---

## Summary

Step 2 QA for the manifest validation key-completeness gate shipped in Step 1 (`a40283a`).
The gate checks whether a plan's `## Cycle Manifest` `validation:` line carries every key that `MANIFEST_VALIDATION_KEYS` declares before allowing `BAR_MET`. The QA step verifies the full test suite, the discriminating control set, the drift false-positive scan, the mutation kill map, and self-application.

---

## Verification

| Item | Check | Status |
|------|-------|--------|
| 1 | Full suite: 1859 passed, 0 failed (1 test excluded by marker) | ✅ |
| 2A | POST-CHANGE control set: `diagnostic-100032` → ESCALATE:claimed-close-unmet (gate fires, not BAR_MET); `100028` and `100030` → BAR_MET | ✅ |
| 2B | PRE-CHANGE control set: all three (`100032`, `100028`, `100030`) → BAR_MET (gate absent) | ✅ |
| 3 | Drift false-positive scan: 5 Done/ plans with full-key stanza, all BAR_MET — zero false fires | ✅ |
| 4a | No-regression: 9 manifest-provenance tests pass; existing cycle_check suite unchanged | ✅ |
| 4b | Byte-identical emit: old and new `--emit-manifest` output on `executable-100028.md` — BYTE-IDENTICAL | ✅ |
| 5 | Mutation kill map: M1 KILLED, M2 KILLED, M3 KILLED, M4 KILLED — 0 survived, 0 error | ✅ |
| 6 | Self-application: `cycle_check` on `executable-100033.md.pristine` → BAR_MET | ✅ |
| 7 | Hygiene: numstat 4 files (scope matches), reflog shows 0 amends | ✅ |

---

## Item 1 — Full Suite

Run from dispatch worktree `/Users/marklehn/Developer/bellows/.bellows-worktrees/100033`.

```
1859 passed, 1 excluded-by-marker in 55.84s
```

Evidence: `pytest_full.txt`

---

## Item 2 — Gate Discriminates (Control Set P9)

**Pre-change** (`a40283a~1` — before the gate was added): all three plans reach `BAR_MET`.

**Post-change** (current HEAD `64486f2`):

| Plan | Post-Change Verdict | Explanation |
|------|---------------------|-------------|
| `diagnostic-100032` | `ESCALATE:claimed-close-unmet` | Gate fires (3 keys stored; `propagation_check` missing); verdict downgraded from BAR_MET to CONTINUE; plan claims closure → ESCALATE |
| `executable-100028` | `BAR_MET` | 4 keys stored, all present — gate does not fire |
| `executable-100030` | `BAR_MET` | 4 keys stored, all present — gate does not fire |

`diagnostic-100032` stored `validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=PASS` (3 keys — missing `propagation_check`). Gate fires, verdict demoted to CONTINUE. Plan's `**Closing:**` line triggers `ESCALATE:claimed-close-unmet` — gate did its job.

Evidence: `probes-raw.txt` Items 2A and 2B.

---

## Item 3 — Drift False-Positive Scan

Plans in `Done/` carrying the full 4-key validation stanza (those closed after `c39927c`, 2026-09-02):

| Plan | Verdict |
|------|---------|
| `executable-100025.md` | BAR_MET |
| `executable-100026.md` | BAR_MET |
| `executable-100027.md` | BAR_MET |
| `executable-100028.md` | BAR_MET |
| `executable-100030.md` | BAR_MET |

Zero drift false-positives. Stored values in these plans differ from a freshly-emitted run (P7 drift), but the gate compares keys not values — confirmed no false fires.

---

## Item 4 — No Regression

**Tests:** 9 new tests in `tests/test_cycle_check_manifest_provenance.py` — all pass. Pre-existing `tests/test_cycle_check.py` suite (135 tests) — all pass.

**Byte-identical emit:** Running `--emit-manifest` on `executable-100028.md` with both old (`a40283a~1`) and new (`a40283a`) versions of `cycle_check.py` — output is BYTE-IDENTICAL. (Both scripts run from `scripts/` directory so `Path(__file__).resolve().parent` resolves correctly.)

---

## Item 5 — Mutation Kill Map

```
MUTATION: 4 killed, 0 survived, 0 error
```

| Mutant | Result |
|--------|--------|
| M1-drop-missing-key-arm | KILLED |
| M2-drop-no-stanza-guard | KILLED |
| M3-compare-values-not-keys | KILLED |
| M4-hardcode-key-list | KILLED |

---

## Item 6 — Self-Application

```
$ python scripts/cycle_check.py /Users/marklehn/Developer/bellows/.bellows-cache/executable-100033.md.pristine
BAR_MET
```

This plan's own stanza carries all four emitter keys (`cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=PASS, propagation_check=DIVERGENT:17`). Gate does not fire; BAR_MET reached.

---

## Item 7 — Hygiene

**DEV commit numstat** (`a40283a`) — exactly 4 files (matches scope):

```
89	0	knowledge/development/dev-log-manifest-provenance-gate-2026-09-03.md
34	0	knowledge/mutants/manifest-provenance-gate.json
34	0	scripts/cycle_check.py
191	0	tests/test_cycle_check_manifest_provenance.py
```

**Reflog:** 0 amends — no `HEAD@{n}: commit (amend)` entries.

---

## Rule 20 Self-Check Results

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100033/knowledge/qa/evidence/manifest-provenance-gate-2026-09-03
Files verified: 2
```
