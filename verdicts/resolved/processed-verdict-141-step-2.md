verdict: continue

Step 2 (claim-dedup guard) verified per Rule 22(b) — all 3 fixes present, wired through a shared lifecycle.active_plan_for_placeholder helper:
- Fix 1: CREATE UNIQUE INDEX IF NOT EXISTS idx_plans_active_placeholder (lifecycle.py:165), idempotent, WHERE matches the active-state set; mint_and_claim now raises IntegrityError on duplicate.
- Fix 2: run_plan pre-mint guard (bellows.py:443-450) — on active-placeholder hit, WARN + shutil.move to halted-{base} + _seen.discard + return (no mint, no worktree). Confirmed by direct read.
- Fix 3: _invalidate_seen_on_redeposit (bellows.py:1655) — checks active_plan_for_placeholder before discarding; active → log "re-deposit ignored" and return without discard; else discard as before.
Full suite 767 passed (+12 new tests). Commit 2485539. Proceed to Step 3 (QA).
