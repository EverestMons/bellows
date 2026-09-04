# Dev Log — manifest-provenance gate (plan 100033, 2026-09-03)

**Target:** `scripts/cycle_check.py`
**Plan:** `executable-100033.md`

---

## What changed

One conditional added to `run_check` at `:515–518`. When the verdict would be
`BAR_MET`, the gate checks whether the stored `validation:` line in the plan's
`## Cycle Manifest` stanza contains every key declared by `MANIFEST_VALIDATION_KEYS`.
If any key is absent, the verdict is downgraded to `CONTINUE`.

One constant added: `MANIFEST_VALIDATION_KEYS = frozenset({"cycle_check", "plan_lint", "fold_check", "propagation_check"})`. Both the gate and any future caller read this single source of truth so the two cannot drift.

One helper added: `_manifest_validation_keys(plan_text)` — returns the frozenset of key names found in the stored `validation:` line, or `None` to signal "skip the gate."

---

## Rejected predicate 1: value comparison (P7)

The gate compares KEY names, not VALUES. Values legitimately drift after freeze
— `executable-100028`'s stored `propagation_check=DIVERGENT:50` vs a freshly
emitted `DIVERGENT:56`; `fold_check=PASS` vs `N/A`. A value comparison
false-positives on every closed plan. Keys do not drift: once emitted, the key
set is stable. Any value-comparison proposal must produce new evidence that
values no longer drift.

---

## Rejected predicate 2: hardcoded "four keys" (P8)

53 plans in `Done/` legitimately carry three-key `validation:` lines — they
closed before `c39927c` (2026-09-02 17:14) added `propagation_check`. A
predicate that hardcodes "must have exactly four" false-positives on all of
them. The predicate must be "the key set the CURRENT emitter writes", which is
what `MANIFEST_VALIDATION_KEYS` encodes.

---

## Recursion hazard — why the gate is NOT in plan_lint (P4/P5)

`emit_manifest` (`:613`) subprocess-runs `plan_lint.py`, `fold_check.py`, and
`propagation_check.py`. Any check that calls `--emit-manifest` from within
`plan_lint` would recurse without termination:
`plan_lint → cycle_check --emit-manifest → plan_lint → …`

The gate at `run_check`'s BAR_MET decision costs no subprocess and cannot
recurse. Note: `plan_lint` (f) already inspects `validation:` keys at `:613`
with no subprocess and no recursion — the hazard is invoking the EMITTER, not
the placement. The gate moved to `cycle_check` on one honest argument: a WARN
is the delivery mechanism the 2026-09-03 diagnostic measured as failing this
author three times in one night. If a future plan proposes adding a `plan_lint`
WARN instead, that plan owes new evidence that WARNs are heeded.

---

## Depositor relationship (P3 of "does not do")

`depositor.py:515-524` re-validates `cycle_check=`'s VALUE at deposit and holds
on `validation_mismatch`. That check is untouched and authoritative: it fires
at deposit, after the author has stopped working. This gate fires at FREEZE,
while the plan is still in hand. Two checks at two moments; if they disagree,
the depositor's is authoritative because it re-runs.

---

## Guards adopted from plan_lint (f)

`_manifest_validation_keys` adopts the falsy and `<declare>` guards from
`plan_lint` (f) at `:612` verbatim:

```python
if not validation_val or validation_val == "<declare>" or validation_val == "N/A":
    return None
```

Two guard expressions written independently diverge — the class this plan exists
for. Adopting them from (f) rather than re-deriving is deliberate.

---

## Byte-identical emitter output

The emitter's f-string at `:658` is unchanged. The refactor adds a constant and
a helper; it does not restructure the output path. Verified by diffing
`--emit-manifest` stdout on `executable-100028.md` before and after: zero bytes
differ.
