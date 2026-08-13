# Dev Note: log-hygiene-2026-08-13

**Plan:** executable-379 (log retention + disk preflight)
**Date:** 2026-08-13

## What shipped

Two guards added to `bellows.py`:

1. **`_prune_old_logs(config)`** — called once at daemon startup (after session-restart banner). Deletes `logs/*.json` older than `log_retention_days` (default 30) by mtime. Skips `terminal/`, non-json, and fresh files. Per-file exception handling; outer try/except so a failed prune never kills the daemon.

2. **`_disk_preflight(config)`** — called immediately before the claim move (`shutil.move`). `os.statvfs` on BELLOWS_ROOT; free bytes below `disk_min_free_gb` (default 2 GB) returns False → claim skipped, deposit stays untouched. Onset-dedup flag prevents notification storms; flag resets when disk recovers. `statvfs` failure degrades to allow (never kills daemon).

Both config keys (`log_retention_days`, `disk_min_free_gb`) added to `config.example.json` with their defaults.

## Measured counts

- `grep -cF "_disk_preflight" bellows.py` → 2 (def + call)
- `grep -cF "_prune_old_logs" bellows.py` → 2 (def + call)
- `test_log_hygiene.py` → 11 tests
- `test_bellows.py` → 189 tests (baseline confirmed)
- **Targeted suite: 200 passed**

## Raw tail

```
200 passed, 1 warning in 4.77s
```

## Restart boundary

Both guards go live at the next daemon restart. The running daemon (pid at dispatch time) holds old code.
