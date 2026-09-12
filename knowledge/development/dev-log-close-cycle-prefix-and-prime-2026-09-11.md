# Dev Log — close_cycle prefix-and-prime — 2026-09-11

## Pins re-derived (P2, P3)

**P2 (re-derived):** `scripts/close_cycle.py` (401 lines): `_replace_closing_line(text, closing_text)` :46 finds the lines starting `**Closing:**` (none → "no **Closing:** line found", more than one → "<n> **Closing:** lines found") and replaces the one with `closing_text` verbatim; `_splice_keys` :67 over `_SPLICE_KEYS` (walks, yields, validation, coherence); `_run_close` :177 — step 1 :178–186, step 2 baseline :188–194, step 3 `emit_out = cycle_check --emit-manifest` :196–202, step 4 splice :204–212, step 5 baseline :214–220, step 6 :222–270 (token compare; one re-splice when only `propagation_check` moved; any other difference → FAIL), step 7 battery; the commit subject and the register seal both read `emit_out`, the output of step 3

No mechanism mismatch: no label check already in `_replace_closing_line`, no prime step already in `_run_close`, fixture manifest has `walks: <declare>` / `yields: <declare>` / `validation: <declare>` / `coherence: <declare>`.

**P3 (re-derived):** `tests/test_close_cycle.py` (469 lines): `_MANIFEST_BLOCK` carries `walks: <declare>`, `yields: <declare>`, `validation: <declare>`, `coherence: <declare>`; `_closing_file(tmp_path, text="**Closing:** WARM close after walk 1 — BAR MET (T1).")`; tests c1–c11 (c1 happy path, c2 emit header ignored, c3 dry-run order, c4 stored/live mismatch — its tamper at the SECOND `after_step("baseline")`, c5 no Closing line, c6 commit, c7 plan_lint echo, c8 battery refuses, c9 walks spliced, c10 propagation fixed point, c10b second comparison fails, c11 cycle_check drift fails); c10, c10b, c11 count `--emit-manifest` calls in a `run_checker` fake (first call versus later); the seam points are `run_checker` and `after_step`

## Failing-first (red, then green)

Tests written first (c12, c13, c13b) and three re-counted fakes (c10, c10b, c11), then `close_cycle.py` edited.

**Red (5 failed, 10 passed) before the edit:**

- `test_c10_propagation_check_fixed_point` — `assert "stored==live NOTE — propagation_check moved" in out` fails: with the re-counted fake (`<= 2`), both emit calls (step 3 and step 6) return DIVERGENT:10 so there is no drift and no NOTE; the prime is not yet present to add call 2
- `test_c10b_fixed_point_second_comparison_fails` — `assert rc == 1` fails (rc=0): with the re-counted fake (`<= 2`/`== 3`), both calls return DIVERGENT:10 so stored==live OK and the test never reaches the second comparison
- `test_c11_cycle_check_drift_fails` — `assert rc == 1` fails (rc=0): with the re-counted fake (`<= 2`), both calls return BAR_MET + DIVERGENT:10 so stored==live OK
- `test_c12_closing_file_without_label_refused` — `assert steps == ["closing"]` fails: label-less closing file accepted, close ran past step 1 producing a full 8-step sequence
- `test_c13_placeholder_manifest_primes_and_closes` — `assert rc == 0` fails (rc=1): STORED==LIVE FAIL without the prime; fake's call 1 splices ESCALATE:claimed-close-unmet, step 6 re-emits BAR_MET — stored≠live

c13b: **GREEN before the edit** — pins today's refusal of a drift on a filled manifest (no prime fires; the fake's ESCALATE→BAR_MET change is a genuine cycle_check drift that fails stored==live, as today).

**Green after the edit:** `15 passed in 17.21s`

**Note on fold_check and the prime's silent baseline:** the prime must refresh the fold baseline before its emit. Without this, the splice removes the `(f) WARN: Cycle Manifest stanza contains <declare> placeholder(s)` signal from plan_lint, causing fold_check=DRIFT during the prime's emit; fold_check=DRIFT also downgrades BAR_MET to CONTINUE via `_apply_battery`. After step 5 saves the baseline, step 6 sees VACUOUS+BAR_MET, while stored has DRIFT+CONTINUE — stored≠live fails. The prime runs `fold_check --save-baseline` silently (no `after_step("baseline")` call) before its emit, making fold_check=VACUOUS and leaving c4's second-baseline tamper boundary at step 5 unchanged.

## The first close on the first run (c13, c13b)

**c13** (placeholder manifest, fake: call 1 → ESCALATE:claimed-close-unmet, calls 2+ → BAR_MET):
```
steps: ['closing', 'baseline', 'emit', 'splice', 'prime', 'baseline', 'stored==live', 'battery', 'commit(skipped)']
rc: 0
```
The prime fires (placeholders in manifest), re-emits, splices BAR_MET, and the close completes on the first run.

**c13b** (filled manifest, same fake — prime condition is `had_placeholder=False`):
```
steps: ['closing', 'baseline', 'emit', 'splice', 'baseline', 'stored==live']
rc: 1
```
No `prime` step. STORED==LIVE FAIL because the fake's ESCALATE→BAR_MET drift on a filled manifest is not primed away.

## Mutation run

`MUTATION: 4 killed, 0 survived, 0 error`
