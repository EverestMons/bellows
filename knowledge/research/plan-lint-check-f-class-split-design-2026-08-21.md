# plan_lint check-(f) class-split design — 2026-08-21

Diagnostic for honing Finding 6 (unit c): characterize the false-clean bug
in `plan_lint.py` check-(f), design the fix, and specify the test matrix
for the downstream executable.

---

## 1. Confirmed Census

Corpus: `knowledge/decisions/Done/*.md`.

**Command:**
```
grep -l "## Drafting Cycle" *.md | wc -l
→ 50

# Class-split (instruction N / record N on a lens line):
grep -lE '^\s*-\s*(cold[\s-]*)?(Weak|Destruction|Vulnerabilit|Integration|ACID).*instruction\s+[0-9]' *.md
→ 16

# Legacy arrow (→ vN on a lens line):
# Only executable-277.md has the arrow on lens lines (w1 → v1: 1 folded …);
# 4 others (diagnostic-292, diagnostic-295, executable-294, executable-286)
# have → vN only in **Walks:** prose headers, not per-lens lines.
→ 1

# Neither: 50 − 16 − 1 = 33
# Overlap (both class-split AND legacy-arrow): 0
```

| Class          | Count | Examples                                          |
|----------------|------:|---------------------------------------------------|
| Class-split    |    16 | diagnostic-478, executable-464, executable-488    |
| Legacy-arrow   |     1 | executable-277                                    |
| Neither        |    33 | executable-271, executable-302, executable-335    |
| **Total**      | **50**|                                                   |

**Planner estimate (50 / 16 / 1 / ~33): CONFIRMED — exact match.**

Of the 16 class-split plans, **≥7** use the **intra-line multi-walk** format
where a single lens line carries all walks:
diagnostic-478, executable-392, executable-464, executable-476,
executable-481, executable-483, diagnostic-482 (+ diagnostic-472,
diagnostic-460, executable-474 also carry multi-instruction lines).
These are the plans a per-LINE instruction-sum would false-WARN on.

The **collapsed multi-lens line** form appears in executable-488:
`- Weak spots / Destruction / Vulnerabilities / ACID: w2 dry.`
— one status shared by 4 lenses. Currently benign (only used when dry);
must be named in the spec.

---

## 2. Constructed Failing Case — Empirical Proof

### 2a. False-clean (the bug)

**Scenario:** Final walk (w2) has an instruction fold on Weak spots, but
ACID (the last lens line) went dry at w2. The current check reads ONLY the
last lens line.

**Input (`/tmp/false-clean-test.md`):**
```markdown
## Drafting Cycle
**Tier:** T1 — triggers fired: T-8 (novel).
**Walks:** 2.
- Weak spots:         w1 1 folded — instruction 1 / record 0; w2 1 folded — instruction 1 / record 0.
- Destruction:        w1 dry; w2 dry.
- Vulnerabilities:    w1 dry; w2 dry.
- Integration-record: w1 dry; w2 dry.
- ACID:               w1 1 folded — instruction 1 / record 0; w2 dry.
**Closing:** walk 2; deposited once.
```

**Command and output:**
```
$ python3 scripts/plan_lint.py /tmp/false-clean-test.md
PASS: (a) header — parsed
PASS: (a) dispatch_mode — bellows
PASS: (a) pause_for_verdict — always
```

**Result: NO "fold as last event" WARN.** The plan has instruction folds on
its final walk (Weak spots w2: instruction 1) but the check sees only the
ACID line, which contains both `fold` (from w1) and `dry` (from w2) →
`has_fold and not has_dry` = `True and not True` = `False` → no WARN.

**The false-clean is real, not asserted.** §2's bar requires zero
instruction-class findings on the final walk; this plan has one and the
gate does not catch it.

### 2b. Judged-stop counter-case (must stay silent under the fix)

**Scenario:** Final walk has folds but all are record-class (instruction 0).
This is a legitimate judged stop per §2.

**Input (`/tmp/judged-stop-test.md`):**
```markdown
## Drafting Cycle
**Tier:** T1 — triggers fired: T-8 (novel).
**Walks:** 2.
- Weak spots:         w1 1 folded — instruction 1 / record 0; w2 1 folded — instruction 0 / record 1.
- Destruction:        w1 dry; w2 dry.
- Vulnerabilities:    w1 dry; w2 dry.
- Integration-record: w1 dry; w2 1 folded — instruction 0 / record 1.
- ACID:               w1 1 folded — instruction 1 / record 0; w2 1 folded — instruction 0 / record 1.
**Closing:** walk 2; instruction 0 / record 3; deposited once.
```

**Under the current check:** the ACID line has `fold` and no `dry` → WARN
fires (over-warns on a legitimate close).

**Under the fixed check:** final walk (w2) instruction sum across all lenses
= 0 + 0 + 0 + 0 + 0 = 0 → no WARN. The judged stop is correctly silent.

---

## 3. Parse Spec for the Fix

The fix replaces the single-last-lens-line heuristic with a class-split-aware
final-walk instruction sum. **REUSE** `cycle_check.py`'s `CLASS_SPLIT_RE`
(line 24: `instruction\s+(\d+)\s*/\s*record\s+(\d+)`) and the per-pass
segmentation logic from `extract_per_pass_metadata` (lines 60–88), rather
than re-deriving.

### (a) Strip parenthetical annotations

Before any parsing, strip `(…)` from each lens line:
```python
clean = re.sub(r'\([^)]*\)', '', line)
```
This prevents annotation tokens like `(W1 = …)` from being mis-read as
walk markers, and prevents stray `instruction N` inside parentheticals
from contributing to the count.

### (b) Segment each lens line into per-walk pieces

Split the cleaned line into per-walk segments at clause boundaries. A
segment starts at a `wN` token appearing at:
- line start (after the lens name + colon)
- after `;` (semicolon)
- after `. ` (period-space) before a lowercase `w` followed by a digit

Walk markers are anchored to **lowercase `w`** at segment boundaries to
avoid confusion with annotation uppercase `W` tokens inside parentheticals
(which are stripped in step (a) anyway — defense-in-depth).

Each segment binds a walk number (`wN`) to its `instruction N / record N`
split (or `dry` if no class split is present).

**Prior art:** `cycle_check.py:extract_per_pass_metadata` (lines 60–88)
already solves per-pass segmentation. It uses `_FOLD_RE` and `_DRY_RE` to
find per-pass windows and searches each window for `CLASS_SPLIT_RE`. The
fix should import or mirror this logic — specifically the rule that "the
class split binds to the immediately-preceding `N folded` pass" and
"current walk = highest-numbered w" (`cycle_check.py:28`,
`WALK_NUM_RE = re.compile(r"^w(\d+)$", re.IGNORECASE)`).

**Segment delimiter:** `;` OR `. ` (period-space before a `wN`), not just
`;`. Executable-464 uses period-space (`w2 dry. w3 dry. w4 dry.`); others
use semicolons. Both must be handled.

### (c) Final walk = max wN across ALL lens lines

Determine the final walk number as the maximum `wN` across ALL lens lines
in the DC block (not per-line). For each lens line, select ONLY its
segment at that max walk number. A lens with no segment at the final walk
contributes nothing (e.g., a lens that went dry earlier).

### (d) Sum instruction-class folds across final-walk segments only

For each lens's final-walk segment, extract the `instruction N` value
(from `CLASS_SPLIT_RE`). If the segment is `dry`, it contributes 0. If the
segment has a fold but no class split, treat it as instruction 1 (legacy
fall-through — the fold has unknown class, so warn conservatively).

**WARN condition:** the sum of instruction counts across all lenses'
final-walk segments > 0.

**Why per-LINE sums are wrong (the forcing gap):** A per-line instruction
sum (ignoring segmentation) would add w1+w2+w3's instruction folds together,
and false-WARN on the 7+ single-line-multi-walk plans whose earlier walks
folded but whose final walk converged to dry or instruction 0. The
segmentation in (b)/(c) prevents this — it isolates the final walk's
contribution from earlier walks' history.

### (e) Collapsed multi-lens line

Lines like `- Weak spots / Destruction / Vulnerabilities / ACID: w2 dry.`
carry one shared status for multiple lenses. Treat the status as applying
to each named lens. When the shared status is dry, each lens contributes 0
to the final-walk instruction sum (benign). If a collapsed line carried a
fold with a class split, the instruction count would apply to each named
lens — but this form currently appears only in the dry case
(executable-488). Name the handling explicitly; do not ignore the form.

### (f) Fallback (backward-compat)

When NO lens line in the DC block carries an `instruction N` token, the
plan is in legacy-arrow / dry-only / compact / T0 format. In this case,
**keep the CURRENT last-lens heuristic UNCHANGED**: find the last lens line
before `**Closing:**`, check for `fold` and `dry` on the whole line.

The class-split path is PREFERRED when present. The fallback applies only
when no class split is detected anywhere in the block. This ensures:
- The 33 "neither" plans and the 1 legacy-arrow plan continue to get the
  same (lenient) treatment they get today.
- The 16 class-split plans get the new, correct per-final-walk check.
- The existing test suite stays green without modification (the tests use
  mostly non-class-split fixtures for the fold/dry checks).

### (g) Posture: WARN-first (no FAIL upgrade)

The check stays at WARN severity, not FAIL. Rationale from §4 design:
- A judged stop is a NORMAL close (§2) — the Closing line may legitimately
  carry folds with instruction 0. A FAIL would block legitimate closes.
- §4 is warn-first by design; the check is a reminder, not a gate.
- The existing `print("WARN: ...")` mechanism and exit-0 behavior are
  preserved.

### WARN message

Retain the existing message string:
`"WARN: Drafting Cycle closing indicates fold as last event, not a dry lens pass (DRAFTING_CYCLE.md §2)"`

The existing test assertions match on substrings `"fold"` and
`"dry lens pass"` — changing the message would break them.

---

## 4. Rule-27 Gap Table

| File                          | Lines     | Role                                       |
|-------------------------------|-----------|---------------------------------------------|
| `scripts/plan_lint.py`        | 365–388   | The check-(f) implementation (edit target)  |
| `tests/test_plan_lint.py`     | 373–1322  | Existing test suite + new test cases        |
| `scripts/cycle_check.py`      | 24, 60–88 | `CLASS_SPLIT_RE` + `extract_per_pass_metadata` (REUSE source) |
| `scripts/cycle_yields.py`     | (imports) | Shared parsing primitives (`parse_lens_line`, etc.) |

**Other consumers:** `grep -rn 'fold as last event\|dry lens pass' scripts/ --include='*.py'`
returned **no hits outside `plan_lint.py`**. No other script or module
reads or acts on check-(f)'s output string. The change is self-contained.

---

## 5. Test Matrix for the Executable

Each row specifies an input shape, the expected check output under the
fixed check, and how it differs from the current behavior (if at all).

| Row | Label | Input shape | Expected output | Current behavior | Purpose |
|-----|-------|-------------|-----------------|------------------|---------|
| **(i)** | **False-clean** | Final walk has instruction fold in a non-ACID lens (Weak spots w2: instruction 1 / record 0) + dry ACID last line (ACID w2: dry) | **Now WARNs** (instruction sum on final walk = 1 > 0) | Silent (false-clean) | Proves the fix catches the bug |
| **(ii)** | **Judged-stop** | Final walk `instruction 0 / record 1` on multiple lenses; all folds are record-class | **SILENT** (instruction sum on final walk = 0) | WARNs (ACID has fold + no dry) | Proves legitimate judged stops are not blocked |
| **(iii)** | **Legacy-arrow** | Arrow format `w1 → v1: 2 folded (…)` with no class split anywhere in block; dry close | **SILENT** (fallback to current last-lens heuristic; dry present → no WARN) | Silent | Proves backward-compat for legacy form |
| **(iv)** | **Dry-only / compact / T0** | All lens lines carry only `w1 dry` or no walk status; no `instruction N` anywhere | **SILENT** (fallback; no fold detected) | Silent | Proves backward-compat for simple forms |
| **(v)** | **Multi-segment REGRESSION** | Single-line-multi-walk with earlier-walk instruction folds but final-walk `dry` or `instruction 0`. E.g.: `Weak spots: w1 2 folded — instruction 2 / record 0; w2 2 folded — instruction 2 / record 0; w5 dry.` | **SILENT** (final-walk segment w5 = dry, instruction sum = 0) | Silent (but would FALSE-WARN under a naive per-line-sum fix) | Proves the fix does NOT regress correctly-converged plans (the 7+ real plans: diagnostic-478, executable-392/464/476/481/483, diagnostic-482). This is the row the segmentation gap makes essential. |
| **(vi)** | **Full existing suite** | All 22 `test_lint_cycle_*` tests: 13 `"fold as last event"` must-stay-silent assertions + the positive-control WARN assertions (tests f-e, f-k, f-l, f-t, f-u, f-v, f-m3a–e) | **All stay green** | All green (baseline 22 passed, confirmed 2026-08-21) | Proves no regression in the existing surface |

### Test-matrix notes

- Row (v) is the **inverse** of row (i): row (i) proves a false-clean
  now fires; row (v) proves a correctly-converged plan does NOT false-fire.
  Together they bracket the fix.
- Row (vi) requires running the FULL `test_lint_cycle_*` suite, not
  cherry-picking named tests. The assertion count (from live `grep`):
  13 `"fold as last event" not in` lines + 10 `"dry lens pass" in` lines
  + 5 `"dry lens pass" not in` lines = 28 fold/dry-related assertions
  across 22 test functions.
- The collapsed multi-lens line (executable-488's format) is covered by
  §3(e). A dry collapsed line contributes 0 to the instruction sum; no
  separate test row is needed unless a folded collapsed line is constructed
  (currently none exist in the corpus).
- The judged-stop row (ii) tests the POSITIVE path of §2's bar: a cycle
  whose final walk carries only record-class findings closes legitimately.
  The current check over-warns on this; the fix corrects it.

---

## Summary

The false-clean is empirically proven (§2): a plan with an instruction fold
on its final walk passes check-(f) undetected when ACID's line happens to
contain `dry`. The root cause is that check-(f) reads ONE line (the last
lens line) instead of the class split across ALL lenses on the final walk.

The fix (§3) adds a class-split-aware path that segments intra-line
multi-walk lens lines, identifies the final walk as max wN across all
lenses, and sums instruction counts on that walk only. It falls back to
the current heuristic for the 34 non-class-split plans. It reuses
`cycle_check.py`'s `CLASS_SPLIT_RE` and per-pass segmentation rather than
re-deriving. It stays warn-first.

The test matrix (§5) brackets the fix with a false-clean-now-fires row,
a judged-stop-stays-silent row, a multi-segment-regression row, and a
full-existing-suite-stays-green row.

No code is edited by this diagnostic. The downstream executable builds
from this spec.
