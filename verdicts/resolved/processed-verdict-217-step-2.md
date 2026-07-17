verdict: continue

**Final step. The sentinel-repair deliverable is complete and verified end-to-end — plan 217 closes the arc plan 216 started.**

## Verified

All mechanical gates PASS. All **17 verification rows PASS** — the 13 original rows from halted-216 executed verbatim plus the 4 correction rows. Planner independently re-verified: the hash pin (`shasum -a 256` first-8 = **`ef5b8fe4`** — recomputed by the Planner, matches QA row 13/17 exactly); suite arithmetic (2141 baseline + 36 new = **2177 passed**, the 2 known CLAUDE.md failures, zero regressions); the one-line script diff; the narrow exclusion helper; and 15 additional Planner-run loops of the test file (15/15) on top of the DEV's 25 and QA's 5 — **45/45 total against the flake**.

Row 12's extra diff files are the established benign class: the daemon-owned `agent-prompt-feedback.md` regeneration plus the two plans' dev-logs. The script's last-touching commit is `853206c`; the pin is computed there and holds unless a later commit touches the script — at which point the stale-pin rule forbids running without a re-pin.

## What closes and what opens

- **Closes:** the 216→217 correction arc. The repair TOOL is shipped, 11-guard, leak-tested on success and abort paths, deterministic, hash-pinned.
- **Opens (CEO, work machine — the 8-step runbook in the plan's CEO Context and the script's `--help`):** pull → `certutil -hashfile repair_fuel_sentinel_20260716.py SHA256` must start **`ef5b8fe4`** → close the app → dry-run → PDF eyeball of the LOCAL section (pct triple; top-of-table) → paste the safe block → **Planner GO** → `--apply` → paste-back. **The data is NOT repaired until that runs.**
- The dry-run may surface the table-top/PDF question (chronic truncation carrier) — if the PDF shows a longer or open-ended table, that becomes its own top-restore follow-up.

Move the plan to `Done/`.
