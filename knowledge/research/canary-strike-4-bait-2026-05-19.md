# Canary — Strike 4 Bait

This is Plan B Step 1's deliverable. The Deposits block below intentionally
mentions a `_staging_*` filename to verify that the deposit_exists gate
filters it out post-fix.

Pre-fix, the gate would extract `_staging_canary-strike-4-bait-2026-05-19.md`
from the plan text and report it missing. Post-fix, the gate filters
`_staging_*` basenames before checking on disk, so only the real
deliverable (this file) is validated.

If this plan reaches verdict-pending with Gate Result Passed: True, the
strike-4 fix is loaded.
