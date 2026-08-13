# Pin-Hook Lint — Dev Note (Step 1)

**Plan:** 371 | **Slug:** `pin-hook-lint-2026-08-13`
**Date:** 2026-08-13

## What shipped

Check (q) in `scripts/plan_lint.py` — a deposit-time pin verification check
that is WARN-only (never changes exit code). Phase 1 of Fork 3 from the
CEO's pin-hook scoping packet.

### Implemented

- `_extract_hex_tokens(text)` — maximal hex run tokenizer. 64-char → sha256,
  40-char → git, ≥12 other → prefix, <12 ignored.
- `_extract_pin_path(context_lines)` — backtick-quoted and bare-absolute
  path extraction from shasum/sha256 invocation context.
- `_check_pins(plan_text, project_repo, root_repo)` — M2 (sha256 file pins)
  and M1 (git-object pins) matchers with explicit repo path parameters
  (testability seam).
- Defensive wrapper in `lint()` — no-crash contract; catches all exceptions
  and emits `(q) WARN: check errored (...)`.
- PIN-CHECK telemetry — one line per token with kind/line/token/result.
- Location-independent repo resolution from `BELLOWS_ROOT.parent`.

### Tests added (12)

| Test | Covers |
|------|--------|
| `test_q_extract_hex_tokens` | Token classification: 64/40/prefix/<12; no double-counting |
| `test_q_m2_sha256_match` | M2 ok path |
| `test_q_m2_sha256_mismatch_warns` | M2 MISMATCH → WARN |
| `test_q_m2_missing_file_warns` | M2 missing-file → WARN |
| `test_q_m2_no_sha_context_ambiguous` | M2 no shasum context → ambiguous, no WARN |
| `test_q_m2_backtick_path` | Backtick-quoted path extraction |
| `test_q_m1_resolve_project` | M1 resolve in tmp_path git repo → ok |
| `test_q_m1_unresolved_warns` | M1 unresolved → WARN |
| `test_q_m1_cross_repo` | M1 cross-repo (root but not project) |
| `test_q_fenced_block_pin_seen` | C3: raw-text scan sees fenced-block pins |
| `test_q_warn_first_exit_zero` | C1: failing pins + exit 0 |
| `test_q_no_crash_pathological` | No-crash contract: directory as pinned path |

## Measured counts

- **Before:** 110 passed
- **After:**  122 passed (110 + 12 new)

## Targeted run RAW tail

```
............                                                             [100%]
12 passed, 110 deselected, 1 warning in 0.35s
```
