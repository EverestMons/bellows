# Daemon Robustness Batch — Step 2: Claim-Dedup Guard
**Date:** 2026-07-07 | **Plan:** 141

## Active-State Rationale

The non-terminal lifecycle states are `('claimed', 'in_progress', 'awaiting_verdict')` — per the CHECK constraint at `lifecycle.py:46`. A plan in any of these states is "active" and owns its deposit placeholder exclusively. Terminal states (`closed`, `halted`, `abandoned`) release the placeholder for re-use.

## Fix 1 — DB Partial Unique Index (lifecycle.py)

```diff
+    # --- Claim-dedup guard: partial unique index on active placeholders ---
+    conn.execute("""
+        CREATE UNIQUE INDEX IF NOT EXISTS idx_plans_active_placeholder
+        ON plans (deposit_placeholder_name)
+        WHERE lifecycle_state IN ('claimed','in_progress','awaiting_verdict')
+    """)
```

Added in `init_lifecycle_db()` after the `ledger_writes` table, before `conn.commit()`. Uses `CREATE UNIQUE INDEX IF NOT EXISTS` for idempotency — safe to run on pre-existing DBs. The WHERE clause matches the active-state set exactly. Defense-in-depth: `mint_and_claim` raises `sqlite3.IntegrityError` on a duplicate active placeholder.

## Fix 2 — Application Check in `run_plan` (bellows.py ~line 441)

```diff
+            # Claim-dedup guard: refuse if an active plan already owns this placeholder
+            existing_id = lifecycle.active_plan_for_placeholder(base_filename)
+            if existing_id is not None:
+                _log("WARN", f"duplicate deposit — active plan {existing_id} already claimed from same placeholder; refusing second claim", slug=slug_for(plan_name))
+                halted_path = os.path.join(plan_dir, f"halted-{base_filename}")
+                shutil.move(plan_path, halted_path)
+                if bellows is not None:
+                    bellows._seen.discard(verdict.slug_from_path(plan_path))
+                return
```

New helper `active_plan_for_placeholder(placeholder_name, db_path=None)` in `lifecycle.py` queries for an active plan row matching the deposit placeholder name. Returns the plan id if found, else None.

The guard fires before `mint_and_claim`, so no id is minted and no worktree is created. The duplicate deposit is moved to `halted-<name>` and the slug is discarded from `_seen` (so the daemon doesn't re-attempt it on the next scan).

## Fix 3 — Guard `_invalidate_seen_on_redeposit` (bellows.py ~line 1655)

```diff
         slug = verdict.slug_from_path(path)
         if slug in self.orchestrator._seen:
+            existing_id = lifecycle.active_plan_for_placeholder(filename)
+            if existing_id is not None:
+                _log("INFO", f"re-deposit ignored — active plan {existing_id} in progress for slug {slug}", slug=slug_for(filename))
+                return
             self.orchestrator._seen.discard(slug)
```

Before clearing `_seen`, the guard queries for an active plan with the same filename. If one exists, the `_seen` invalidation is blocked — the slug stays in `_seen`, preventing the re-deposited file from being dispatched as a second plan. The existing behavior (clearing `_seen` for genuinely new deposits after a plan is terminal) is preserved.

## Existing Test Fix

`test_lifecycle_meta_and_derivations_at_claim` (test_bellows.py:4346) minted 40 filler plans with the same placeholder name `"f.md"` to burn IDs. Changed to `f"f{i}.md"` to give each a unique placeholder, satisfying the new partial unique index.

## New Tests

| Test | Rationale |
|---|---|
| `TestPartialUniqueIndex::test_second_active_claim_raises_integrity_error` | (a) Verifies the DB index blocks a duplicate active claim |
| `TestPartialUniqueIndex::test_new_claim_allowed_after_terminal_state` | (a) Verifies closed plans release the placeholder |
| `TestPartialUniqueIndex::test_halted_does_not_block_new_claim` | (a) Verifies halted plans release the placeholder |
| `TestActivePlanForPlaceholder::test_returns_id_for_active_plan` | (b) Returns id for claimed plan |
| `TestActivePlanForPlaceholder::test_returns_none_for_closed_plan` | (b) Returns None after close |
| `TestActivePlanForPlaceholder::test_returns_none_for_halted_plan` | (b) Returns None after halt |
| `TestActivePlanForPlaceholder::test_returns_none_for_absent_placeholder` | (b) Returns None for nonexistent |
| `TestActivePlanForPlaceholder::test_returns_id_for_in_progress` | (b) Returns id for in_progress |
| `TestActivePlanForPlaceholder::test_returns_id_for_awaiting_verdict` | (b) Returns id for awaiting_verdict |
| `TestRunPlanDedupGuard::test_duplicate_deposit_routed_to_halted` | (c) run_plan guard refuses dup, moves to halted, no second id |
| `TestInvalidateSeenDedupGuard::test_does_not_discard_seen_when_active` | (d) _seen preserved when active plan exists |
| `TestInvalidateSeenDedupGuard::test_discards_seen_when_no_active_plan` | (d) _seen cleared when no active plan |

## Full Test Suite

```
======================= 767 passed, 1 warning in 29.48s ========================
```

767 tests pass (755 original + 12 new). No failures.

## Commit

```
2485539 feat(bellows): claim-dedup guard — refuse duplicate active-placeholder claims (diagnostic 139) [141]
```

### Ledger Updates

#### Prompt Feedback

The research document (`plan-double-claim-137-138-2026-07-07.md`) §3 fix list was precise and implementation-ready — each fix had the exact function name, line number, and change shape. The active-state set was explicitly stated with the CHECK constraint reference, eliminating ambiguity. One minor gap: the fix list didn't mention the existing test (`test_lifecycle_meta_and_derivations_at_claim`) that would break due to its use of a shared placeholder name for ID-burning — this was discovered during the test run and trivially fixed.

---
## Output Receipt
**Agent:** Bellows Developer
**Step:** 2
**Status:** Complete

### What Was Done
Implemented the 3-fix claim-dedup guard from diagnostic 139's fix list: (1) partial unique index on active placeholders in lifecycle.db, (2) application-level dedup check in run_plan before mint_and_claim, (3) guard on _invalidate_seen_on_redeposit to prevent _seen clearance while an active plan exists. Added 12 new tests covering all fix surfaces. Fixed one existing test that conflicted with the new index.

### Files Deposited
- `knowledge/development/daemon-robustness-batch-step2-2026-07-07.md` — this dev log

### Files Created or Modified (Code)
- `lifecycle.py` — partial unique index in init_lifecycle_db, new active_plan_for_placeholder helper
- `bellows.py` — dedup guard in run_plan (~line 441), guard in _invalidate_seen_on_redeposit (~line 1655)
- `tests/test_lifecycle.py` — 12 new tests (4 classes)
- `tests/test_bellows.py` — fix filler plan placeholder names for index compatibility

### Decisions Made
- Used `shutil.move` to `halted-` prefix (matching the existing rejection pattern from dispatch-mode validator) rather than deleting the duplicate deposit — preserves evidence for forensics
- Added `active_plan_for_placeholder` as a standalone helper in lifecycle.py rather than inlining the query — reusable by both Fix 2 and Fix 3

### Flags for CEO
- None

### Flags for Next Step
- Step 1 worktree-health finding was `benign` — no follow-up plan needed
