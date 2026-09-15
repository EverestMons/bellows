# QA Receipt — cycle-check-baseline-368 — 2026-09-15

Plan id: 100108 | Thread: 368 | Step: 2 (QA)

---

## DEV diff summary

`git diff --numstat 08f93a8f..468ff281`:

```
34	0	knowledge/development/dev-log-cycle-check-baseline-2026-09-15.md
26	0	knowledge/mutants/cycle-check-baseline-368.json
11	0	knowledge/mutants/cycle-check-baseline-368.run.txt
 8	5	scripts/cycle_check.py
91	0	tests/test_cycle_check.py
```

Five files, as declared in the manifest.

---

## scripts/cycle_check.py — two sites

`git diff 08f93a8f..468ff281 -- scripts/cycle_check.py`:

```diff
diff --git a/scripts/cycle_check.py b/scripts/cycle_check.py
index 752f0749..542bd9a0 100644
--- a/scripts/cycle_check.py
+++ b/scripts/cycle_check.py
@@ -353,7 +353,7 @@ def check_assert_2(parsed, plan_path):
                 )
                 if r.returncode == 0 and r.stdout.strip():
                     commits = r.stdout.strip().splitlines()
-                    pat = re.compile(r"drafting\(|\[draft\]|deposit\(")
+                    pat = re.compile(r"drafting\(|\[draft\]")  # a deposit( commit is not a walk (thread 368)
                     walk_commits = [c for c in commits if pat.search(c)]
                     if walk_commits:
                         git_has_context = True
@@ -367,14 +367,17 @@ def check_assert_2(parsed, plan_path):
 
 
 def check_assert_3(parsed, plan_path, git_has_context):
-    """Fold happened — baseline exists. Degrades with assert #2.
-    PASS | FAIL | N/A."""
+    """Fold happened — baseline exists, where the manifest declares it (thread 368).
+    Degrades with assert #2. PASS | FAIL | N/A."""
     walk_data = parsed["walk_data"]
     any_folds = any(wd["total_folds"] > 0 for wd in walk_data.values())
     if not any_folds:
         return "N/A"
-    baseline = plan_path.parent / f".{plan_path.name}.foldcheck.json"
-    if not baseline.exists():
+    # thread 368: read the baseline through the ONE resolver — manifest's fold_baseline:
+    # line first, beside the plan only when undeclared; a declared baseline that does
+    # not resolve is None, never a silent fallback to beside-the-plan.
+    baseline_path, _declared = resolve_fold_baseline(plan_path)
+    if baseline_path is None:
         return "FAIL" if git_has_context else "N/A"
     return "PASS"
```

Two sites only: the pattern token removal and the `check_assert_3` baseline lookup. No other production-code lines changed.

---

## tests/test_cycle_check.py — hunk check

`git diff -U0 08f93a8f..468ff281 -- tests/test_cycle_check.py | grep -F '@@'`:

```
@@ -1264,0 +1265,91 @@
```

`git show "08f93a8f:tests/test_cycle_check.py" | wc -l` → `1264`

One hunk, adding 91 lines after line 1264 (the base file's last line), removing none. No hunk touches existing tests. MUST-PRESERVE satisfied.

---

## Item 2 — gate tests (six PASSED lines)

```
tests/test_cycle_check.py::test_t368_assert_3_reads_the_declared_baseline PASSED [ 16%]
tests/test_cycle_check.py::test_t368_a_deposit_commit_is_not_walk_history PASSED [ 33%]
tests/test_cycle_check.py::test_t368_a_declared_baseline_that_does_not_resolve_never_falls_back PASSED [ 50%]
tests/test_cycle_check.py::test_assert_fail_3 PASSED                     [ 66%]
tests/test_cycle_check.py::test_uncommitted_walk PASSED                  [ 83%]
tests/test_cycle_check.py::test_assert_3_baseline_exists PASSED          [100%]
```

`test_assert_fail_3` and `test_assert_3_baseline_exists` are unedited and green: the two MUST-PRESERVE tests from P4. `deposit(` still triggers `test_assert_fail_3`'s mock log without being a walk commit (that log line also has `[draft]`); `test_assert_3_baseline_exists` exercises the undeclared-sibling path, unaffected by the fix.

---

## Item 3 — held plan reads BAR_MET through the fixed gate

`grep -n '^fold_baseline:' knowledge/decisions/hold-executable-gate2-pt-w30-a.md`:

```
87:fold_baseline: governance/knowledge/decisions/drafts/.executable-gate2-pt-w30-a.md.foldcheck.json
```

`/Users/marklehn/Developer/bellows/.venv/bin/python scripts/cycle_check.py knowledge/decisions/hold-executable-gate2-pt-w30-a.md` (last line):

```
BAR_MET
```

The file's git log carries one `deposit(gate2-pt-w30-a):` commit; after the fix that commit no longer makes `git_has_context` True, so assertion 3 is N/A for it — the same result the draft in governance gave. The declared baseline resolves through `resolve_fold_baseline`.

`/Users/marklehn/Developer/bellows/.venv/bin/python scripts/cycle_check.py knowledge/decisions/Done/executable-100104.md` (last line):

```
BAR_MET
```

Plans that read `BAR_MET` before still read `BAR_MET`.

---

## Item 4 — production writes

None. No lane file renamed or released, no lifecycle row written, no daemon act, no `tools/clear_plan.py` call. Only the two evidence files were written in this step.

---

## Verification

| Item | Evidence | Status |
|------|----------|--------|
| 1 — full suite | 2445 passed, two skips (test_gate_watcher live-DB; test_fallback_live_wal_window version gate) | ✅ |
| 2 — gate tests | six PASSED lines above | ✅ |
| 3 — held plan BAR_MET | `BAR_MET` on last line for both hold-executable-gate2-pt-w30-a.md and Done/executable-100104.md | ✅ |
| 4 — production writes | none outside the two evidence files | ✅ |

---

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100108/knowledge/qa/evidence/
Files verified: 1
```

