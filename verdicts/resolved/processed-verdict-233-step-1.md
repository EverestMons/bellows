verdict: continue

**Rule 22(b) verified. 11/11 tests pass Planner-run, all 13 guards present including the folded G6b invariant, and the probe lookup correctly carries `ORDER BY price_floor DESC`. TWO defects to fix in Step 2, both numbered below. Neither is a correctness bug in what gets migrated.**

## Verified

- **The engine is called, not replaced** — `from fuel_conflict_detection import recompute_fuel_ceilings` with 8 call sites. The migration decision is entirely the engine's.
- **G6b landed** — the direction and continuation invariants I folded in at the drafting cycle are implemented as their own guard. Guards present: G1, G2, G3, G4, G5, G6, G6b, G7, G8, G9, G10, G11, G12.
- **The probe lookup mirrors production.** `_gate8_lookup` carries `ORDER BY price_floor DESC` with a comment naming why. This was the subtlety most likely to be silently dropped, and it was not.
- **11/11 tests pass**, Planner-run.

## Fix 1 (REQUIRED, Step 2) — G5 reimplements the threshold the plan forbade duplicating

`migrate_fuel_ceilings_floor_only_20260719.py:399-401`:

```python
derived = next_floor - 0.001
delta_mills = round(abs(ceiling - derived) * 1000)
if delta_mills > 10:
```

This is a second copy of the load-bearing classification, in exactly the form the plan banned. **Mitigating: it is used ONLY for reporting** — G5 names which rows are preserved gaps so the CEO can eyeball them. It does not decide what gets migrated. So this is not a live correctness bug.

**But it is a divergence hazard in a guard whose entire purpose is CEO verification.** If the engine's `<= 10` is ever changed, this copy silently disagrees and G5 names the wrong rows to a human checking a money-path migration. That is the precise failure mode the prohibition exists to prevent.

**Fix, in preference order:**
1. **Derive the gap rows by DIFFING the scratch copy against the original** — a row is a preserved genuine gap iff it is interior AND its ceiling is unchanged AND its ceiling differs from `next_floor - 0.001`. This uses the engine's actual behaviour as ground truth and needs no threshold at all.
2. If the formula must remain, at minimum `from fuel_conflict_detection import PRECISION_THRESHOLD_MILLS` and use it — one shared constant, no second literal.

**Note: QA row 2 will FAIL as currently written** — it greps for `next_floor - 0.001`, `delta_mills`, and threshold literals, and all three are present. That is the system working exactly as designed: the numbered row catches what emphatic prose did not. Do not weaken row 2 to accommodate the code; fix the code.

## Fix 2 (REQUIRED, Step 2) — remove the stream-of-consciousness comment block

`:262-272` ships reasoning that contradicts itself:

```
# For configs with last_bracket_rule="continuation", any change IS the last bracket.
# Wait, no — recompute_fuel_ceilings changes interior brackets AND potentially
# the last bracket.
```

The first line is **false** and sits there as an apparent assertion; the correction follows it. The code that results is right (a second scratch run tracking the last row), but a future reader cannot tell which statement is operative.

**On the most safety-critical script in the project, a comment that states a falsehood and then retracts it is worse than no comment.** Replace the whole block with a single sentence stating what the code does and why the second scratch run is necessary.

## Proceed to Step 2

The runbook, plus the two fixes above. Both are **numbered items, not prose asides** — per LESSONS entry 90, an instruction that is not a numbered row is an instruction that evaporates, and this arc has already lost three that way. Report both in the Step-2 dev log with what changed.

The runbook itself must cover the abort paths in plain language (G4 footprint mismatch, G6b invariant violation, G11 parity rollback all leave the database completely unchanged) — a CEO mid-migration needs to know instantly that nothing changed, or an abort that merely *looks* like a failure invites a retry with the guard removed.
