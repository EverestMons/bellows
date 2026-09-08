# QA Evidence — depositor class assigner repo-aware (plan 100043, step 2)

**Date:** 2026-09-08 | **Plan:** 100043 | **Step:** 2 — QA | **Suite:** 2062 passed, 1 skipped

---

## Item 1 — Full suite (redirected)

Command: `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ --tb=short -q > knowledge/qa/evidence/depositor-class-assigner-suite-2026-09-08.txt 2>&1`

Exit: **0**. Evidence file: `depositor-class-assigner-suite-2026-09-08.txt`.

Summary line (tail of evidence file):

```
2062 passed, 1 skipped in 72.57s (0:01:12)
```

HALT condition (non-zero FAILURE count): **not triggered**.

---

## Item 2 — Thirteen P3 cases on shipped code, no mocks

Depositor built with dummies. Real shop roots: P = `/Users/marklehn/Developer`, G = `/Users/marklehn/Developer/eluvian-governance` (mini-shaped: G ≠ P). No monkeypatching — `bellows_root.resolve_projects_parent()` and `bellows_root.resolve_governance_root()` called through the module.

Prerequisite confirmed: `/Users/marklehn/Developer/eluvian-governance/DRAFTING_CYCLE.md` exists (E5 redirect fires for 66b). `/Users/marklehn/Developer/tuyere/brand_new.md` absent (no redirect for `new` case).

| # | writes | root | expected (P3) | got | status |
|---|--------|------|---------------|-----|--------|
| 42 | `["app.py"]` | invoice-pulse | app-feature | app-feature | ✅ |
| 26 | `["GOVERNANCE.md"]` | tuyere | shop-infra | shop-infra | ✅ |
| 26b | `["config.example.json"]` | tuyere | app-feature | app-feature | ✅ |
| 26c | `["docs/GOVERNANCE.md"]` | tuyere | app-feature | app-feature | ✅ |
| 66a | `[G/DRAFTING_CYCLE.md]` (abs) | tuyere | shop-infra | shop-infra | ✅ |
| 66b | `["DRAFTING_CYCLE.md"]` | tuyere | shop-infra | shop-infra | ✅ |
| 66c | `[P/LESSONS.md]` (abs, single-seg) | tuyere | shop-infra | shop-infra | ✅ |
| 66d | `[P/bellows/DRAFTING_CYCLE.md]` (abs) | bellows | shop-infra | shop-infra | ✅ |
| 99 | `["scripts/x.py"]` | forge_lessons | shop-infra | shop-infra | ✅ |
| f1 | `["DRAFTING_CYCLE.md"]` | `""` | shop-infra | shop-infra | ✅ |
| C4 | `["bellows/depositor.py"]` | `""` | shop-infra | shop-infra | ✅ |
| new | `["brand_new.md"]` | tuyere | app-feature | app-feature | ✅ |
| exempt | `["knowledge/development/x.md"]` | bellows | app-feature | app-feature | ✅ |

All 13 values equal P3. **No deviations.**

---

## Item 3 — Corpus re-derived

Scanned all five repos' `Done/` directories (correct paths: governance at `eluvian-governance/governance/knowledge/decisions/Done/`; bellows at `bellows/knowledge/decisions/Done/`; others at `repo/knowledge/decisions/Done/`). Each plan's git toplevel used as `project_root` (C8e). BEFORE from git archive of `80a2ce2`; AFTER from shipped code.

**Per-repo plan counts:** bellows=66, eluvian-governance=17, forge_lessons=18, invoice-pulse=4, tuyere=8. **Total: 113** (matches P4).

**6 flips — set matches P4 exactly:**

| plan | BEFORE | AFTER |
|------|--------|-------|
| bellows/executable-100018.md | shop-infra | app-feature |
| forge_lessons/diagnostic-501.md | app-feature | shop-infra |
| forge_lessons/executable-549.md | app-feature | shop-infra |
| invoice-pulse/executable-580.md | shop-infra | app-feature |
| invoice-pulse/executable-581.md | shop-infra | app-feature |
| tuyere/executable-100003.md | shop-infra | app-feature |

No flip outside P4's list. HALT condition: **not triggered**.

AFTER distribution: shop-infra=80 / app-feature=13 / read-only=20 (matches P4's "AFTER 80 / 13 / 20").

---

## Item 4 — Thread 199 on real tools

Scratch copy: `knowledge/qa/evidence/executable-100037.md` (copied from `Done/executable-100037.md`). Fold baseline saved beside it: `.executable-100037.md.foldcheck.json`. `coherence:` set to `<declare>` (moves a plan_lint signal; triggers fold drift vs. baseline). `_rerun_validation` called via a dummies Depositor with `_bellows_root` pointing to the worktree root.

Result dict:

```json
{
  "hold": true,
  "reason": "cycle_check:CONTINUE",
  "cycle_check": "CONTINUE",
  "plan_lint": null,
  "lens_order": null,
  "warnings": [
    "BATTERY: plan_lint=0_FAIL fold_check=DRIFT propagation_check=DIVERGENT:1",
    "WARN: BAR_MET downgraded to CONTINUE — battery: fold_check=DRIFT — if the change is INTENDED, re-save the baseline and say so in the fold's record"
  ]
}
```

`hold == True` ✅ | `reason == "cycle_check:CONTINUE"` ✅ | `warnings` carries DRIFT WARN with remedy ✅

---

## Item 5 — Production writes

Production writes in this QA step: **exactly two evidence files**:
- `knowledge/qa/evidence/depositor-class-assigner-suite-2026-09-08.txt`
- `knowledge/qa/evidence/depositor-class-assigner-qa-evidence-2026-09-08.md`

No lane file written. No sidecar written. No clearance row written.

The scratch copy (`knowledge/qa/evidence/executable-100037.md`) and its `.foldcheck.json` are worktree-only; discarded at teardown (`git worktree remove --force`, `bellows.py:2216`). Not production writes.

**⚠️ RESTART OWED:** `bellows.py` imports `depositor` in-process; the running daemon classifies with the old rule until restarted. This is the CEO's act at close (Post-close note, plan header).

---

## Item 6 — Receipt

**DEV step commits (three — deviation from plan's two documented in dev-log):**

```
83ff59e [100043] dev-log + mutation run: depositor-class-assigner
2b9f0cb [100043] fix(mutants): tighten test_9 non-root assertions + governance-existence anchor
23cdaac [100043] feat(depositor): repo-aware class assigner — _resolve_write, name floor, 199 warnings
```

**numstat over `80a2ce2..HEAD` — 7 files:**

```
145	17	depositor.py
78	 0	knowledge/development/dev-log-depositor-class-assigner-2026-09-08.md
89	 0	knowledge/mutants/depositor-class-assigner.json
20	 0	knowledge/mutants/depositor-class-assigner.run.txt
 7	 6	tests/test_depositor.py
548	 0	tests/test_depositor_class_assigner.py
  2	 2	tests/test_depositor_lens_order_gate.py
```

7 unique files ✅. (Fix commit `2b9f0cb` edited already-tracked files; no new files added.)

**Run file `HEAD:` line vs. manifest file sha:**

- Run file: `HEAD: 2b9f0cb6b61069e96b74b0a31a94985652b009b9`
- `git log -1 --format=%h -- knowledge/mutants/depositor-class-assigner.json`: `2b9f0cb`

Match ✅ (C3).

**`git diff 80a2ce2..83ff59e -- tests/test_depositor.py`:** ONE hunk (`@@ -184,15 +184,16 @@`), inside lines 187–196 (function rename + docstring + one assertion value). The seven `("…", "")` assertions at lines 157–169 are unchanged (byte-identical — hunk touches only lines ≥184). No other hunk ✅ (C7).

**`git diff 80a2ce2..83ff59e -- tests/test_depositor_lens_order_gate.py`:** TWO hunks:
- `@@ -41,7 +41,7 @@` — one-line change at line 43 (lambda kwarg `warnings=None`)
- `@@ -112,7 +112,7 @@` — one-line change at line 114 (lambda kwarg `warnings=None`)

No other hunk ✅ (C7, E2).

**`git reflog -n 6`:**
```
83ff59e HEAD@{0}: reset: moving to HEAD
83ff59e HEAD@{1}: ...
```
One `reset: moving to HEAD` entry — a no-op reset (HEAD unchanged). 0 amends, 0 destructive resets ✅ (C3).

**Dev-log four headings (grep):**

- `## P2/P3 — the thirteen cases (verbatim)` → line 3 ✅
- `## P4 — corpus flips (verbatim + re-derived)` → line 27 ✅
- `## Cost` → line 46 ✅
- `## Mutation run` → line 70 ✅

**Item-by-item gate summary (each on its own line):**

- Item 1: suite exit=0, 2062 passed, 1 skipped ✅
- Item 2: all 13 P3 values matched on real shop roots ✅
- Item 3: 6 corpus flips, set equals P4's six, AFTER distribution 80/13/20 ✅
- Item 4: hold=True, reason=cycle_check:CONTINUE, warnings carry DRIFT WARN ✅
- Item 5: two evidence files, no lane/sidecar/clearance, restart owed ✅

---

## Verification

| Item | Check | Status |
|------|-------|--------|
| 1 | Full suite exit=0, 2062 passed | ✅ |
| 2 | 13 P3 cases on real roots: all match | ✅ |
| 3 | Corpus: 6 flips = P4's six exactly | ✅ |
| 4 | 199: hold=True, reason=cycle_check:CONTINUE, DRIFT WARN present | ✅ |
| 5 | Production writes: two evidence files only | ✅ |
| 6a | numstat: 7 files | ✅ |
| 6b | Run file HEAD matches manifest sha (2b9f0cb) | ✅ |
| 6c | test_depositor.py: one hunk, lines 157-169 byte-identical | ✅ |
| 6d | test_depositor_lens_order_gate.py: two one-line hunks | ✅ |
| 6e | reflog: 0 amends, 0 destructive resets | ✅ |
| 6f | Dev-log: four required headings present | ✅ |

### Rule 20 Self-Check Block Output

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100043/knowledge/qa/evidence/
Files verified: 2
