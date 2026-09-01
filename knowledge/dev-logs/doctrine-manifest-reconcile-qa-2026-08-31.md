# QA Receipt — doctrine-manifest-reconcile — 2026-08-31

**Plan:** executable-100006
**Step:** 2 (QA)
**Date dispatched:** 2026-09-01

---

## Q0 — Pre-flight resolved paths

**RESOLVED interpreter:** `/Users/marklehn/Developer/bellows/.venv/bin/python` — VENV_OK
**RESOLVED governance:** `/Users/marklehn/Developer/eluvian-governance`

Both resolved via primary candidates. The second root candidate (`$HOME/Developer/GitHub`) was NOT exercised — it does not exist on this machine and remains UNVERIFIED.

---

## Item 1 — Re-verify the reconciliation at the seam

Quoted from the file with `grep -n 'cycle_check=BAR_MET'`:

**Line 228 (prose):**
```
**The `## Cycle Manifest` stanza:...`validation:` carries `checker=verdict` pairs (e.g. `cycle_check=BAR_MET, plan_lint=0_FAIL`) that the depositor RE-RUNS...
```

**Line 262 (worked example):**
```
validation: cycle_check=BAR_MET, plan_lint=0_FAIL
```

Both lines spell the token `BAR_MET` (upper-snake). The prose at `:228` and the worked example at `:262` **now agree**. ✓

---

## Item 2 — Corpus still agrees

Re-ran `cycle_check.parse_manifest_stanza` over both `Done/` directories:

- `/Users/marklehn/Developer/bellows/knowledge/decisions/Done`: 324 files, **31 with stanzas**
- `/Users/marklehn/Developer/tuyere/knowledge/decisions/Done`: 5 files, **5 with stanzas**

**Total stanzas measured: 36**
- `cycle_check` distribution: `{'BAR_MET': 36}` — **36/36 declare upper-snake `BAR_MET`**
- `plan_lint` distribution: `{'0_FAIL': 36}` — **36/36 declare bare upper-snake `0_FAIL`**

The corpus agrees: every stanza uses `BAR_MET`, zero use the old doctrine spelling `bar-met`. ✓

Note: The plan's P4 measurement (2026-08-31) reported 48 stanzas. Today's re-measurement (2026-09-01) yields 36. Numbers are reported from the command output, not restated from the plan's pins. The corpus still unanimously agrees.

---

## Item 3 — The narrowing held

**`T0-R` occurrences** (via `grep -c 'T0-R' "$GOV/DRAFTING_CYCLE.md"`): **0**

**`class:` list from line 228 of the file (verbatim):**
```
{read-only, governed-tooling, register-writing}
```

T0-R count is 0 and the `class:` list is still the three-value form. The narrowing held — neither the T0-R tier floor (thread 68) nor the class-list defect (thread 67) was introduced. ✓

---

## Item 4 — No gate behaviour changed

**Baseline plan (as recorded in dev log A1.5):** `knowledge/decisions/Done/executable-100005.md`

**Dev log recorded values (verbatim from A1.5):**
- `plan_lint`: PASS count 9 / FAIL count 0
- `cycle_check`: `BAR_MET`

**QA re-run values (verbatim output):**

`plan_lint` output:
```
(o1) INFO: candidates=6 excluded=3 fired=2
(o1) WARN: missing path `/Users/marklehn/Developer/GitHub/tuyere`
(o1) WARN: missing path `governance/knowledge/research/walk-register-project-producer-2026-08-31.md`
PIN-CHECK: kind=prefix line=52 token=08f82e409ce4… result=ambiguous
PIN-CHECK: kind=prefix line=52 token=f9855c305c82… result=ambiguous
PIN-CHECK: kind=prefix line=52 token=6e1101438c28… result=ambiguous
PIN-CHECK: kind=prefix line=99 token=08f82e409ce4… result=ambiguous
PASS: (a) header — parsed
PASS: (a) dispatch_mode — bellows
PASS: (a) pause_for_verdict — always
PASS: (a) known_failures — 0
PASS: (b) step 1 deposits — 4 path(s)
PASS: (b) step 2 deposits — 2 path(s)
PASS: (c) QA banner pair — both strings present
PASS: (d) step 1 scope — 4 file(s), 0 prefix(es)
PASS: (d) step 2 scope — 2 file(s), 0 prefix(es)
```
PASS count: **9** / FAIL count: **0**

`cycle_check` output:
```
BAR_MET
```

**Comparison:** QA re-run matches the dev log baseline exactly. PASS count 9, FAIL count 0, verdict `BAR_MET` — identical. A content change to `DRAFTING_CYCLE.md` moved no gate. ✓

---

## Item 5 — The two commits are clean

**Governance commit:**
SHA: `4633603830c140d214b065d6ad60daa8b0f2e7c7`

```
commit 4633603830c140d214b065d6ad60daa8b0f2e7c7
Author: Mark Lehn
Date:   Tue Sep 1 09:36:33 2026 -0500

    [100006] docs(drafting-cycle): reconcile the manifest worked example — DC v2.17

 DRAFTING_CYCLE.md | 5 +++--
 1 file changed, 3 insertions(+), 2 deletions(-)
```

Contains exactly **1 file** (DRAFTING_CYCLE.md). No bellows files present. ✓

**Bellows dev-log commit:**
SHA: `3ca53361f677dc0b5fb31f0604b1d24c0225e9ae`

```
commit 3ca53361f677dc0b5fb31f0604b1d24c0225e9ae
Author: Mark Lehn
Date:   Tue Sep 1 09:36:39 2026 -0500

    [100006] docs(dev-log): doctrine-manifest-reconcile DEV log — DC v2.17

 knowledge/dev-logs/doctrine-manifest-reconcile-dev-2026-08-31.md | 136 +++++++++++++++++++++
 1 file changed, 136 insertions(+)
```

Contains exactly **1 file** (the dev log). No governance files present. ✓

Neither commit contains the other repository's files. The two commits are pathspec-scoped and clean. ✓

---

## Verification

| Item | Check | Status |
|------|-------|--------|
| Q0 | Interpreter resolved: `/Users/marklehn/Developer/bellows/.venv/bin/python` | ✅ |
| Q0 | Governance root resolved: `/Users/marklehn/Developer/eluvian-governance` | ✅ |
| Item 1 | Prose `:228` and worked example `:262` both read `BAR_MET` — agree | ✅ |
| Item 2 | Corpus re-measured: 36 stanzas, 36/36 `BAR_MET`, 36/36 `0_FAIL` | ✅ |
| Item 3 | `T0-R` count=0; `class:` list three-value `{read-only, governed-tooling, register-writing}` | ✅ |
| Item 4 | `plan_lint` PASS=9/FAIL=0, `cycle_check`=`BAR_MET` — matches baseline verbatim | ✅ |
| Item 5 | Gov commit 1 file; bellows commit 1 file; neither cross-contaminates | ✅ |

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100006/knowledge/dev-logs/
Files verified: 1
```
