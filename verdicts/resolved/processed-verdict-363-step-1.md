stop

ABANDON — findings invalid (ran under a full-disk condition), per CEO direction 2026-08-12.

Diagnostic 363 investigated plan-358's "~156 full-suite failures + 33 errors +
summary-generation hang." But 363 ran its entire investigation from ~13:38 to
14:42, DURING which the Data volume was full (125Mi free) — the very condition
that produces those artifacts. So 363's own suite runs (the pre-358 baseline, the
current run, the isolation batches) were themselves corrupted by ENOSPC: it was
running inside the artifact-generating state it was trying to characterize, and
cannot distinguish disk-full noise from real failures.

Root cause is now known WITHOUT this diagnostic: the disk was full. That alone
explains the 358 worktree-recovery orphan, the pytest summary-generation hang,
and the mass test failures (tests can't write their temp SQLite DBs/files). The
disk has since been freed (46Gi available). The only genuine remainder is the
6+ stale `CURRENT_SCHEMA_VERSION == 20` pins, which fail on any disk and need
the trivial -> 21 update.

Do not accept 363's findings doc. Re-run the 358 suite check on the now-healthy
disk to confirm the pins-only hypothesis; a fresh diagnostic is not needed unless
that re-run surprises us.
