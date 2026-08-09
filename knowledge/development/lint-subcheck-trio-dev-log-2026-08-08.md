# Lint Sub-check Trio Dev Log — Plan 324

**PRE_EDIT_HASH:** `47976bfa5f888f63bd552ca3b1849a107e43556c`

## Task A0 — Pre-edit Cleanliness

- `git status --porcelain -- scripts/plan_lint.py tests/test_plan_lint.py gates.py` → empty (clean)
- Warn-first confirmed: all checks (f)–(l) are bare prints, never touching `results`/`all_passed`; return is `0 if all_passed else 1`
- No (n), (o1), (o2), (p) labels exist at HEAD — clean
- No (m) found — held sibling has not landed
- Insertion anchor `    for status, check, detail in results:` exists at line 328
- `dc_block = None` initialized immediately before the (f) branch — `dc_block` was previously assigned only inside (f)'s nested else (T1+ tier AND heading present), so (p) reading it would `NameError` on any no-tier plan. The init changes no existing check's behaviour.

## Check (n) — Before/After

**Before:** No (n) check. Inline non-`-F` grep commands on literal patterns were undetected.

**After:** Added (n) WARN-only check scanning inline backtick spans (single-line, shared extractor with o1) for `grep` commands with quoted literal patterns missing `-F`/`--fixed-strings`. Patterns containing only `.` (no other metacharacters) stay candidates — filename dots are the dominant literal class. Fenced blocks excluded via `clean_text`. Documented misses: unquoted patterns, fenced-block greps.

## Check (o1) — Before/After

**Before:** No path-existence check.

**After:** Added (o1) WARN-only check collecting path candidates from inline backtick spans, resolving via dual-root (project root by `/knowledge/` split, then shop root `/Users/marklehn/Developer/GitHub`), WARN only when missing at both. Exclusion set normalized from Deposits + Scope entries (union of whole-text and per-step extraction, each in verbatim and project-prefix-stripped form). Listing capped at 10 with `(+K more)`, lifted by `PLAN_LINT_UNCAP=1`. INFO accounting line printed when C > 0. Root-derivation failure suppresses relative-candidate resolution only; absolute candidates and accounting still run. Fixed leading-`/` segment handling for absolute paths during implementation (split produces empty first segment).

## Check (o2) — Before/After

**Before:** No deposits-form check.

**After:** Added (o2) WARN-only check on Deposits entries (union of whole-text and per-step, deduped). Flags entries not `/Users/`-absolute and not project-prefixed (first segment not in known projects). Scope entries are EXEMPT (C1). No filesystem access.

## Check (p) — Before/After

**Before:** No constraint-executable check.

**After:** Added (p) WARN-only check inside `dc_block` (when non-None). For each `**C<n>** —` entry found by the same regex as (g), scans from match start to end-of-line for backtick-quoted commands or `check:` tokens. WARN on absence. Zero entries skip silently.

## Task D — Existing Tests

- Before: 73 passed
- After: 73 passed (no regressions, no fixture edits required)

## Task E — New Tests

Added 24 new tests (97 total):

**(n):** literal WARN, dot-only WARN, piped WARN, single-quoted WARN, -F no WARN, -E regex no WARN, fenced no WARN, metachar no WARN, megaspan degenerate pair (stray backtick + paired span).

**(o1):** missing absolute path WARN, excluded-by-deposits no WARN, non-path spans no WARN, existing path no WARN, bare-tmp relative-only INFO, cap/uncap >10, dedup.

**(o2):** unprefixed WARN, project-prefixed no WARN, absolute no WARN, scope exempt no WARN.

**(p):** no-backtick WARN, with-backtick no WARN, zero-entries silent.

**Degenerate:** empty plan + no-dc plan + unparseable header → no crash, no new-check WARN, exit code matches pre-existing check (a) behavior (exit 1 for unparseable).

## Targeted Test Output

```
$ python3 -m pytest tests/ -k "plan_lint or lint" --tb=short -q 2>&1 | cat
........................................................................ [ 74%]
.........................                                                [100%]
97 passed, 818 deselected, 1 warning in 3.82s
```

## Live Run — Tripping Fixture

**Fixture path:** `<tmpdir>/proj/knowledge/decisions/tripping-fixture.md`

**Fixture text:**
```
# Tripping Fixture
**Dispatch Mode:** bellows | **pause_for_verdict:** always | **cycle_tier:** T1

## STEP 1 — DEV

> Run `grep "plan_lint.py" scripts/` to find the lint script.
>
> Check `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/nonexistent-tripping-fixture-xyzzy.txt` for reference.
>
> **Deposits:**
> - `knowledge/development/dev-log.md`

## Drafting Cycle
**Tier:** T1 — triggers fired: T-8 (novel).
- Weak spots:         w1 dry.
- Destruction:        w1 dry.
- Vulnerabilities:    w1 dry.
- Integration-record: w1 dry.
- ACID:               w1 dry.
**Conflicts:** one constraint.
- **C1** — this constraint has no executable form
**Closing:** walk 1 dry; last event = lens pass.
```

**Raw output:**
```
(n) WARN: `grep "plan_lint.py" scripts/` — grep on literal pattern without -F (ugrep-shim hazard)
(o1) INFO: candidates=2 excluded=1 fired=1
(o1) WARN: missing path `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/nonexistent-tripping-fixture-xyzzy.txt`
(o2) WARN: Deposits entry `knowledge/development/dev-log.md` is not project-prefixed or absolute
(p) WARN: C1 has no backtick-quoted command or check: token
PASS: (a) header — parsed
PASS: (a) dispatch_mode — bellows
PASS: (a) pause_for_verdict — always
PASS: (b) step 1 deposits — 1 path(s)
```
```
$ echo $?
0
```

All four labels fire: (n), (o1), (o2), (p). Exit 0.

## Live Run — Compliant Plan

**Plan:** `knowledge/decisions/Done/qa-149.md`

**Raw output:**
```
WARN: no cycle_tier declared (DRAFTING_CYCLE.md §1/§3)
(o1) INFO: candidates=3 excluded=1 fired=0
PASS: (a) header — parsed
PASS: (a) dispatch_mode — bellows
PASS: (a) pause_for_verdict — always
PASS: (b) step 1 deposits — 1 path(s)
PASS: (c) QA banner pair — both strings present
PASS: (d) step 1 scope — 1 file(s), 0 prefix(es)
```
```
$ echo $?
0
```

Exit 0. Expected-baseline WARNs: `cycle_tier` missing (older plan), `(o1) INFO` with zero fires.

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Implemented four WARN-only lint sub-checks (n), (o1), (o2), (p) in `scripts/plan_lint.py` and added 24 new tests in `tests/test_plan_lint.py`. All 97 tests pass; all four labels fire on the tripping fixture with exit 0.

### Files Deposited
- `knowledge/development/lint-subcheck-trio-dev-log-2026-08-08.md` — this dev log

### Files Created or Modified (Code)
- `scripts/plan_lint.py` — added `import os`, `dc_block = None` init, checks (n)/(o1)/(o2)/(p) before results loop
- `tests/test_plan_lint.py` — added `import shutil`, 24 new tests for the four checks + degenerate cases

### Decisions Made
- Initialized `dc_block = None` before (f) branch to prevent `NameError` in (p) on no-tier plans — changes no existing check's behaviour
- Fixed absolute-path segment handling in o1 (leading `/` produces empty first segment on split)

### Flags for CEO
- None

### Flags for Next Step
- PRE_EDIT_HASH: `47976bfa5f888f63bd552ca3b1849a107e43556c`
- Tripping fixture text and placement path recorded above for Step 2's live positive control

#### Prompt Feedback

No prompt feedback.
