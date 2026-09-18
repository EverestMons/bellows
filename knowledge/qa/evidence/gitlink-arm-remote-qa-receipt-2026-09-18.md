# QA Receipt — [3/root] gitlink arm remote check (plan 100128, 2026-09-18)

**Plan:** bellows plan 100128 — `[3/root]` gitlink arm reads published tips  
**Step:** 2 (QA)  
**Date:** 2026-09-18  
**A0 baseline (plan P11, #100126):** 2527 passed, 2 skipped  

## Verification Table

| # | check | result |
|---|---|---|
| 1 | full suite, delta is the ten new tests only | ✅ |
| 2 | ten nodes by name | ✅ |
| 3 | unreadable passes with advisory, stale fails | ✅ |
| 4 | reads bounded, transport non-interactive | ✅ |
| 5 | checker green under `/usr/bin/python3`, five outcomes driven | ✅ |
| 6 | live read flagged the planted stale pointer against the real remote; no advisory | ✅ |
| 7 | arm writes nothing | ✅ |
| 8 | ritual text bumps every gitlink to the published tip; no bellows-only or HEAD-sha instruction remains | ✅ |
| 9 | `_resolve_bellows` tests still pass | ✅ |
| 10 | every mutant killed, live tree unchanged | ✅ |
| 11 | receipt and raw outputs written | ✅ |

## Evidence

### 1. Full suite — `pytest tests/ -q`

A0 baseline: 2527 passed, 2 skipped (plan P11, #100126).  
New total: **2537 passed, 2 skipped** (+10 = the ten new gitlink arm tests, 0 failures).  
Full output: `knowledge/qa/evidence/gitlink-arm-remote-suite-2026-09-18.txt`

### 2. Ten nodes by name

Each `pytest tests/test_wrap_gitlink_arm.py::<name> -v` run individually, all 10 PASSED.  
Full output: `knowledge/qa/evidence/gitlink-arm-remote-nodes-2026-09-18.txt`

### 3. Unreadable tip passes with advisory, stale one fails — node 3

```
tests/test_wrap_gitlink_arm.py::test_unreadable_remote_passes_with_advisory PASSED [100%]
1 passed in 0.49s
```

(Node 3's fixture has a nonexistent local path as the URL — rc 128 in ~14 ms — beside a genuinely stale submodule. Zero `[3/root]` fails for the unreadable one; the advisory line printed; one fail for the stale one.)

### 4. Bounded and non-interactive — node 9

```
tests/test_wrap_gitlink_arm.py::test_remote_reads_are_bounded_and_batch PASSED [100%]
1 passed in 1.14s
```

Wall time 1.14s (three 0.5s sleep-stub reads, concurrent → finished in ~1s, not 1.5s sequential).  
`_GIT_SSH` constant contains `BatchMode=yes` and `ConnectTimeout=` — asserted by the test.

### 5. Checker under `/usr/bin/python3`, five outcomes driven

```
env ELUVIAN_WRAP_ROOT="$SCRATCH/root" ELUVIAN_WRAP_MEMORY="$SCRATCH/memory" \
  /usr/bin/python3 hooks/eluvian/wrap_check.py "" debt
```

Output (five outcomes present):
```
[3/root] WARN (advisory): unreadable_sub — published tip unreadable; gitlink not judged.
[2r/receipts] SKIPPED — receipts directory absent.
[R2/registry] wrap(s) recorded today per the shared registry:
  [76] Marks-Mac-mini.local — 9c02aa5f-c776-4902-9250-e357f1d8220c wrapped at 2026-09-18 10:47:41
— if this machine's tree is stale, fetch first: the debt reported BELOW may be another machine's already-satisfied state (scope law). Genuine local debt still stands.
SESSION WRAP INCOMPLETE — the following steps are not verifiably done:

  ✗ [3/root] bumped_sub has an uncommitted bump — commit or revert it before wrapping.
  ✗ [3/root] no_modules_sub has no .gitmodules entry — add one before wrapping.
  ✗ [3/root] stale_sub gitlink is stale — 06c0ff52 recorded, ff53cb302f1f4ca1180e7420ddf76a2072ddd50e published; bump it to that sha and commit.

Complete these, then this lock clears automatically.
Exit: 1
```

Five outcomes driven:
1. FAIL — uncommitted bump: `bumped_sub has an uncommitted bump`
2. FAIL — missing .gitmodules entry: `no_modules_sub has no .gitmodules entry`
3. PASS advisory: `unreadable_sub — published tip unreadable; gitlink not judged.`
4. PASS current: `current_sub` silent (equal tip)
5. FAIL stale: `stale_sub gitlink is stale — 06c0ff52 recorded, ff53cb302f...`

Porcelain before and after identical (arm writes nothing):
```
=== before === M  bumped_sub  ?? bellows/
=== after  === M  bumped_sub  ?? bellows/
```

### 6. Live read — non-vacuity proof (Observer K)

```
TIP=cfd6fd923ce3f269509433baccc40a2d584cff6f
env -i HOME="$HOME" PATH=/usr/bin:/bin ELUVIAN_WRAP_ROOT="$SCRATCH/gov" \
  /usr/bin/python3 hooks/eluvian/wrap_check.py "" debt
```

Output:
```
[2r/receipts] SKIPPED — receipts directory absent.
[R2/registry] wrap(s) recorded today per the shared registry:
  [76] Marks-Mac-mini.local — 9c02aa5f-c776-4902-9250-e357f1d8220c wrapped at 2026-09-18 10:47:41
— if this machine's tree is stale, fetch first: the debt reported BELOW may be another machine's already-satisfied state (scope law). Genuine local debt still stands.
SESSION WRAP INCOMPLETE — the following steps are not verifiably done:

  ✗ [1/project] governance: 1 commit(s) not pushed — push governance.
  ✗ [2/bellows] 1 commit(s) not pushed — push bellows.
  ✗ [3/root] anvil gitlink is stale — 11111111 recorded, cfd6fd923ce3f269509433baccc40a2d584cff6f published; bump it to that sha and commit.
  ✗ [3/root] 1 commit(s) not pushed — push governance root.

Complete these, then this lock clears automatically.
Exit: 1
```

Assertions:
- ONE `[3/root]` stale line, naming `anvil` ✓
- Published sha `cfd6fd923ce3f269509433baccc40a2d584cff6f` equals `$TIP` ✓
- NO stale line for `bellows` or `lessons-forge` ✓
- NO `published tip unreadable` advisory ✓

Full output: `knowledge/qa/evidence/gitlink-arm-remote-live-read-2026-09-18.txt`

### 7. Arm writes nothing — node 7

```
tests/test_wrap_gitlink_arm.py::test_arm_writes_nothing PASSED [100%]
1 passed in 0.34s
```

Fixture root's `git status --porcelain` before and after `check()` — identical (empty for the test's clean root).

### 8. Ritual text check

```
sed -n '115,130p' hooks/commands/wrap.md
```

Output:
```
(`shop_next_session.md`: preserve carried threads, add this arc's ships, demote
   prior ones — append your OWN session block only; never rewrite another
   machine's blocks), for each stale tracked gitlink the `[3/root]` arm named run
   `git update-index --cacheinfo 160000,<published sha>,<path>` to bump it to its
   published tip (works on either layout — initialized or uninitialized), commit
3c. **Carried items → tuyere threads** ...
   ...
   On both layouts use `git update-index --cacheinfo 160000,<published sha>,<path>`
   with the sha the arm names — never a local HEAD, which can be unpushed.
```

```
/usr/bin/grep -c 'HEAD-sha' hooks/commands/wrap.md   → 0
/usr/bin/grep -c 'published' hooks/commands/wrap.md  → 3
```

No bellows-only instruction remains; bump target is the published tip the arm names, not a local head. ✓

### 9. `_resolve_bellows` untouched

```
pytest tests/test_hook_default_root.py tests/test_gates_cross_machine_paths.py -q
13 passed in 0.17s
```

### 10. Mutation run

```
knowledge/mutants/gitlink-arm-remote.run.txt (re-run with fixed test file at HEAD)
```

Output:
```
MUTATION: 10 killed, 0 survived, 0 error
LIVE-TREE UNCHANGED: hooks/eluvian/wrap_check.py sha256=d3c536b83bc9
```

All 10 mutants killed. (Note: re-run after committing the wc_env fixture fix, so mutations are killed for the correct reason — the fixed tests detect the defect, not an ambient AttributeError.)

### 11. Receipt and raw outputs written

- `knowledge/qa/evidence/gitlink-arm-remote-qa-receipt-2026-09-18.md` ← this file
- `knowledge/qa/evidence/gitlink-arm-remote-suite-2026-09-18.txt` ✓
- `knowledge/qa/evidence/gitlink-arm-remote-nodes-2026-09-18.txt` ✓
- `knowledge/qa/evidence/gitlink-arm-remote-live-read-2026-09-18.txt` ✓

---

## Rule 20 — QA Self-Check Results

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100128/knowledge/qa/evidence/
Files verified: 4
```

