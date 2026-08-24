# Deposit Watcher Receipts

Slug-keyed receipt files written at deposit time by `tools/deposit_receipt.py`.

## Contract

Each receipt is a JSON file named `receipt-<slug>-<session_id>-<hash12>.json` where:
- `slug` is `plans.deposit_placeholder_name` (stable across all renames)
- `session_id` is the depositing session's id (shape: `[A-Za-z0-9-]+`)
- `hash12` is the first 12 hex characters of the plan file's SHA-256 content hash

## Attestation boundary

This receipt proves the watcher was ARMED at write time. It does NOT prove the
watcher stayed alive. Liveness of a session-local monitor is not externally
verifiable.

## Ordering contract

The receipt is written BEFORE the plan is staged as `ready-<slug>.md`. The ritual:
1. Run `tools/deposit_receipt.py <draft-path> <session-id>` against the draft file
   (same bytes that will be staged — hash equality is the proof)
2. Stage as `ready-<slug>.md`

## Retirement

On plan close (terminal `closed` or `halted` state), the daemon moves matching
receipts to `archived/`. Archived receipts are not checked by the blocking arm
but are still consulted by the warning arm (a retired receipt proves its deposit
was armed).

## Session id

The session id is the UUID that names the session's scratchpad directory — the
same id the wrap hooks receive as `session_id`. A wrong id does not trap: the
blocking arm never sees the receipt and the deposit surfaces in the warning arm
instead.

## Disarm paths

- **Sanctioned deletion:** remove the receipt file to disarm the blocking check
  for that deposit.
- **Field corruption:** a receipt with missing or unparseable fields degrades to
  a WARNING, effectively a second disarm path — equivalent in effect, always
  visible in the wrap-check step output.

## Visibility boundary

On a clean wrap (rc 0), both hook consumers (stop hook, debt hook) discard
stdout. Warnings from the `[2r/receipts]` step surface only in manual
`wrap_check.py` runs and wraps that fail on other grounds.
