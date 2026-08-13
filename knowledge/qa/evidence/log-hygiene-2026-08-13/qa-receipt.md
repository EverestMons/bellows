# QA Receipt — log-hygiene-2026-08-13

**Plan:** executable-379 (log-hygiene-2026-08-13)
**Step:** 2 — QA
**Date:** 2026-08-13
**Step 1 commit:** `05b3fc8 [379] log-hygiene-2026-08-13: log retention pruner + disk preflight guard + tests`

---

## Precondition

Step 1 commit `05b3fc8` pre-dates this QA step. Confirmed via `git log --oneline -1 -- bellows.py`.

---

## Deliverable Verification

| Item | Check | Status |
|------|-------|--------|
| 1 | Full suite: 1017 passed (baseline 1006, delta +11 = 11 new tests in `test_log_hygiene.py`) | ✅ |
| 2 | Wiring: `_disk_preflight(config)` at line 647, immediately before claim move; skip path returns without `shutil.move`, rename, or halt — C3 visible | ✅ |
| 3 | C5 restart boundary stated verbatim below | ✅ |
| 4 | Live prune rehearsal: old .json pruned, fresh .json + non-json + terminal/ survived | ✅ |
| 5 | Raw output included throughout and in evidence file | ✅ |

---

## Item 1 — Full Suite

```
$ python3 -m pytest tests/ -q
1017 passed, 1 warning in 25.01s
```

Baseline (C4): 1006 passed (post-376). Delta: +11. The new `tests/test_log_hygiene.py` adds exactly 11 tests: `test_prune_deletes_old_json_only`, `test_prune_uses_config_retention_days`, `test_prune_exception_does_not_crash`, `test_prune_no_logs_dir`, `test_preflight_passes_above_threshold`, `test_preflight_fails_below_threshold`, `test_preflight_onset_flag_dedupes_notifier`, `test_preflight_onset_flag_resets_on_recovery`, `test_preflight_statvfs_failure_degrades_to_allow`, `test_config_defaults_log_retention_days`, `test_config_defaults_disk_min_free_gb`. 1006 + 11 = 1017. Delta fully explained.

Raw output: `pytest-full-raw.txt`.

---

## Item 2 — Wiring From the Diff

**Preflight guard** (`bellows.py` diff hunk at line 647):

```python
            if not _disk_preflight(config):
                if bellows is not None:
                    bellows._seen.discard(verdict.slug_from_path(plan_path))
                return
            # Single rename: deposit placeholder → in-progress-<type>-<id>.md
            id_canonical = f"{plan_type}-{plan_id}.md"
            inprogress_path = os.path.join(plan_dir, f"in-progress-{id_canonical}")
```

The preflight call sits immediately BEFORE the claim move (`shutil.move` to `inprogress_path`). The skip path (`return`) contains no `shutil.move`, no rename, no halt. The deposit stays untouched in `decisions/`. C3 confirmed.

**Prune wiring** (`bellows.py` diff at line 2390):

```python
        _prune_old_logs(self.config)
```

Called once after the session-restart banner is logged. `grep -cF "_prune_old_logs" bellows.py` = 2 (def + call). `grep -cF "_disk_preflight" bellows.py` = 2 (def + call).

---

## Item 3 — C5: Restart Boundary

The restart boundary, stated verbatim from the plan:

> **THE RESTART BOUNDARY:** the running daemon (pid at dispatch time) holds old code; both guards go live at the next restart — the Planner's ops action at the wrap's idle window, never the agent's.

Both `_prune_old_logs` (startup-only) and `_disk_preflight` (pre-claim) are wired in the daemon code that is only loaded at process start. The running daemon at dispatch time holds the old code; the guards become active only after the daemon is restarted.

---

## Item 4 — Live Prune Rehearsal (Scratch-Only)

Built a `tmp` logs dir with old + fresh + terminal/, ran `_prune_old_logs` with `BELLOWS_ROOT` patched to the scratch dir.

```
=== BEFORE ===
  daemon-nohup.log
  step-fresh-003.json
  step-old-001.json
  step-old-002.json
  terminal/session.log

11:04:53 [INFO] pruned old log: step-old-002.json
11:04:53 [INFO] pruned old log: step-old-001.json
11:04:53 [INFO] log retention: 2 file(s) pruned (threshold: 30 days)

=== AFTER ===
  daemon-nohup.log
  step-fresh-003.json
  terminal/session.log
```

Old `.json` files pruned. Fresh `.json`, non-json (`daemon-nohup.log`), and `terminal/` subdir all survived. C2 confirmed.

---

## Item 5 — Raw Output

All raw output included inline above and in `pytest-full-raw.txt`.

---

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/379/knowledge/qa/evidence/log-hygiene-2026-08-13/
Files verified: 2
```

