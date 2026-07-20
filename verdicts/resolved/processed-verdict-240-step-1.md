verdict: continue

**Rule 22(b) verified — and deliberately run with extra adversarial weight: plan 240's draft 6 was deposited off a fold, so no pass ever examined the version that shipped (LESSONS 94, established after this plan dispatched). This verification is the compensating pass. It comes up DRY.**

## Everything verified directly against code, not the receipt

- **All four sites treated exactly as specified.** `:670`/`:812` → basename to `both()`, full path to `local()`. `:672`/`:171` → `_sanitize_exception(e)` to `both()`, full exception to `local()`. The diff touches message emission and nothing else.
- **The helper exists EXACTLY ONCE and is pure** — `_sanitize_exception` at `:38`, five lines, `isinstance(e, OSError) → type/errno/strerror, else type-name-only`, called from both handlers. The D1/V2 collision resolved as the plan required: one implementation of the branch, two call sites, zero control-flow involvement.
- **Control flow untouched, and pinned twice** — the commit contains ZERO diff lines matching `return <code>` or `conn.close`, and the G9 forced-failure test asserts `exit_code == 9`. A backup failure still aborts.
- **The detector matches the folded spec verbatim** — `[A-Za-z]:\\`, `\\Users\\`, `/home/`, `/Users/`, multi-segment `/\w+/\w+`; no bare `/`, so the `cft=78/78` failure line cannot false-positive.
- **Both forced-failure tests have teeth.** G9: `OSError(13, "Permission denied", FAKE_PATH)` with a fabricated `C:\Users\FAKEUSER\...` — absent from `paste_lines`, present in `local_lines`, **type name AND strerror asserted PRESENT** (the anti-over-deletion guard). G1: `sqlite3.OperationalError` with an embedded fabricated path — absent from paste, `OperationalError` present. Both assert on `paste_lines` directly, via a shared `_assert_no_path_leak(paste_lines)`.
- **29/29 tests pass, Planner-run.**

## One near-error of my own, recorded

I nearly reported the strerror presence assertion as missing — my grep searched for the attribute name `strerror`, but the test asserts the RENDERED text (`"Permission denied"`). A conclusion read off grep output is not a conclusion (LESSONS 91); reading the test before asserting the gap is what prevented a false finding. The G9 test's type-name assert is in fact SHARPER than specified: `OSError(13, ...)` maps to `PermissionError` via Python's errno mapping, and the test asserts the mapped name.

## Proceed to Step 2 (QA)

All rows as written. The ones that carry the weight:

- **Row 3** (G1+G9 forced failures) — quote both tests including the presence asserts.
- **Row 6/6b** — abort-path diff and the single-helper greps.
- **Row 8** — the FULL-tree exposure map, per-file counts and filenames ONLY, never the matched text. This row informs the CEO's remediation decision; a handoff-only count would falsify it.
- **Row 1** — compute the baseline from `--collect-only` (2348 as of plan 239 plus this plan's net-new); quote the arithmetic; report ACTUAL.

The three standing prohibitions apply. Keep the streak.
