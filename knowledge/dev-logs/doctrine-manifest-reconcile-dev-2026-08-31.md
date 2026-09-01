# Dev Log — doctrine-manifest-reconcile — 2026-08-31

**Plan:** executable-100006  
**Step:** 1 (DEV)  
**Date dispatched:** 2026-09-01  

---

## A0 — Pre-flight resolved paths

**BELLOWS TREE:** `/Users/marklehn/Developer/bellows/.bellows-worktrees/100006` — BELLOWS_TREE_OK  
**MAIN (via --git-common-dir):** `/Users/marklehn/Developer/bellows` — VENV_OK  
**RESOLVED governance:** `/Users/marklehn/Developer/eluvian-governance`  
**RESOLVED builder:** `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/decisions/drafts/build-doctrine-manifest-reconcile.py`  

Both resolved via PRIMARY candidates. The second root candidate (`$HOME/Developer/GitHub`) was NOT exercised — it does not exist on this machine and remains UNVERIFIED.

---

## A1 — Pin comparisons

**P1 — DRAFTING_CYCLE.md sha (pre-edit):**  
`2dcc041cc88a8975e49a5b9cd71990d843ba7bc06c1ce3a8dc26c25b8fedb9be`  
First 16: `2dcc041cc88a8975` — MATCHES plan pin ✓

**P2 — version line (pre-edit, line 5):**  
`**Version:** 2.16 (2026-08-25). Amended only through the Iteration Protocol (§6).`  
Matches plan pin `2.16 (2026-08-25)` ✓

**Date check:** today is 2026-09-01; builder writes `2.17 (2026-09-01)` — dates match ✓  
NOT-YET-APPLIED: grep for `Version:** 2.17 (2026-09-01)` returned nothing pre-edit ✓

**P6 — builder sha:**  
`c381688fa23366d3056c0168fe8773ac22ddd0be400ae3521bf2f54afc927dff`  
First 16: `c381688fa23366d3` — MATCHES plan pin ✓

---

## P3 — Builder --check (anchor verification)

```
anchor E1-validation-example (DRAFTING_CYCLE.md): count=1
anchor E4-version-bump (DRAFTING_CYCLE.md): count=1
anchor E5-changelog-row (DRAFTING_CYCLE.md): count=1
CHECK OK: all 3 anchors unique; no write performed.
```

3 anchors, each `count=1`, exit 0. No edit id contains `class` or `t0`. ✓

---

## A1.5 — Gate baseline (captured BEFORE A2)

**BASELINE PLAN:** `knowledge/decisions/Done/executable-100005.md`

**plan_lint output (verbatim):**
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
PASS count: 9 / FAIL count: 0

**cycle_check output (verbatim):**
```
BAR_MET
```

---

## A2 — Builder output (full)

```
anchor E1-validation-example (DRAFTING_CYCLE.md): count=1
anchor E4-version-bump (DRAFTING_CYCLE.md): count=1
anchor E5-changelog-row (DRAFTING_CYCLE.md): count=1
WROTE DRAFTING_CYCLE.md
APPLIED: 3/3 edits.
```

Exit 0. ✓

---

## A3 — Verification results

**A3.1 — version line post-edit:**  
`sed -n '5p'` → `**Version:** 2.17 (2026-09-01). Amended only through the Iteration Protocol (§6).`  
Reads `2.17 (2026-09-01)` — matches A1's guard and A3.1's expected value ✓

**A3.2 — `cycle_check=BAR_MET` occurrences:**  
Measured count: **3** lines

- Line 228 (prose): `…validation:` carries `checker=verdict` pairs (e.g. `cycle_check=BAR_MET, plan_lint=0_FAIL`)…
- Line 262 (worked example): `validation: cycle_check=BAR_MET, plan_lint=0_FAIL`
- Line 312 (2.17 changelog row): `…The §3 worked example's \`validation:\` line read \`cycle_check=bar-met, plan_lint=0-fail\` while the prose 34 lines above it read \`cycle_check=BAR_MET, plan_lint=0_FAIL\`…`

Line 228 and line 262 both spell the token `BAR_MET` — **they agree** ✓

**A3.3 — changelog rows 2.16 and 2.17:**  
`grep -c '^- \*\*2\.1[67] ('` → **2**  
Line 312: `- **2.17 (2026-09-01):**` (new row) ✓  
Line 313: `- **2.16 (2026-08-25):**` (surviving row) ✓  
Both present ✓

**A3.4 — narrowing held:**  
`grep -c 'T0-R'` → **0** ✓  
class list from file: `{read-only, governed-tooling, register-writing}` — still three values ✓

**A3.5 — diff line count:**  
`diff /tmp/dc.before "$GOV/DRAFTING_CYCLE.md" | grep '^[<>]' | wc -l` → **5**  
Matches P5 pin ✓

Changes:
- Line 5: version bump 2.16 → 2.17 (1 old + 1 new = 2 diff lines)
- Line 262: `cycle_check=bar-met, plan_lint=0-fail` → `cycle_check=BAR_MET, plan_lint=0_FAIL` (1 old + 1 new = 2 diff lines)
- Line 311a312: new 2.17 changelog row inserted (1 new = 1 diff line)

Total: 5 lines ✓

**A3.6 — builder idempotence:**  
`"$PY" "$BUILDER" --repo "$GOV"` → `ALREADY-APPLIED: all 3 edits present.`  
Idempotence confirmed ✓
