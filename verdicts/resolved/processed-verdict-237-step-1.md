verdict: stop

**Stopping on a Planner process failure, caught by a CEO governance check — not by anything the agent did.**

Plan 237 was deposited after a compressed drafting cycle: one weak-spots sweep plus a consistency sweep, not the full four passes. **By my own precedent it should have had the full cycle** — plan 232 was the same shape (a change to the sanitized-telemetry leak surface plus a CEO-run tool) and got four passes. The CEO asked whether this one did, and the honest answer was no.

Running passes 2-4 properly afterwards found five items, two of them material. Step 1 had not committed, so nothing is lost by stopping and re-dispatching with them folded in.

## Material — must be fixed before dispatch

**1. (Destruction) The handoff write can break the migration.** Step 2 adds file-writing to `migrate_fuel_ceilings_floor_only_20260719.py`. If `knowledge/handoff/` does not exist on the work machine — it will not, on first run — or the write fails for any reason, a **money-path CEO-run tool now aborts because a reporting convenience failed.** The plan must require: create the directory if absent, and treat a report-write failure as non-fatal (log it, keep the stdout paste-back, let the migration proceed). A migration must never fail because logging failed.

**2. (Vulnerability) The carrier mapping has no uniqueness guarantee.** The plan requires stability (same carrier → same label) and the tests check it, but nothing prevents two concurrent Sync runs from assigning the same carrier two different labels, or two carriers one label. The mapping table needs a **UNIQUE constraint on `carrier_code`** and an atomic get-or-create, so a race cannot fragment the corpus. Stability tests pass happily while this is broken.

## Minor — fold in

**3. NULL/empty `carrier_code` behaviour is unspecified.** `_LabelAllocator.get_label` returns `None` for a `None` value; with a persisted mapping, a NULL key could create a junk row. Specify what happens and test it.

**4. Report-before-abort.** The handoff report must be written AFTER the run resolves and must state the final outcome including aborts. A report written incrementally could describe an apply that then rolled back.

**5. (Integration-vs-record) The same defect exists in a sibling file.** `import_failure_telemetry.py:123` also instantiates `_LabelAllocator()` per run — so the import-failure telemetry corpus has the identical cross-run label-instability problem this plan fixes for the forge export. **Out of scope here; record it in the Forward Register** rather than expanding the plan.

## Process note

This is the fourth dropped-instruction-class failure in this session and the second where the Planner was the cause. The pattern is consistent: **when I compress a process, the thing I skip is the part that catches what I did not already suspect.** The floor pass found the `data_examples` gap because I was already thinking about leaks; passes 2-4 found the migration-abort risk because they force a different question — *what does this break?* — that a leak-focused sweep never asks.

Re-dispatch as plan 238 with all five folded into the plan file, per LESSONS entry 90's refinement: location, not numbering.
