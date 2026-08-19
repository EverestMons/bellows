# Reserved canonical-id-form claim guard — stop phantom-id mints — Executable

**Type:** Executable
**Project:** bellows
**Depends on:** in-session diagnosis of the diagnostic-444 → phantom-445 placeholder collision (bellows-2026-08-18.log 18:43:50; orphan 445 cleared to `abandoned`).
**Created:** 2026-08-18
**Author:** Planner
**dispatch_mode:** bellows
**pause_for_verdict:** on_failure
**qa_steps:** 2
**known_failures:** 0
**Priority:** 10
**cycle_tier:** T1 — one pure predicate + one call-site guard in the claim path; fully test-backed. Expected minted id 448 (NOT baked into the filename — doing so is the very bug this plan closes).
**Deposit target:** `knowledge/decisions/executable-reserved-id-form-claim-guard-2026-08-18.md`

---

## Purpose
Close **RC-2** of the placeholder collision: the claim path mints a fresh id for ANY non-lifecycle-prefixed `.md` in a watched `decisions/` dir, including a bare canonical id-form name like `diagnostic-444.md`. When plan 444 ran, a leaked `diagnostic-444.md` landed in `decisions/` (worktree teardown-merge of an out-of-scope agent write; `scope_check` failed, files_changed=3); the watcher minted **445** for it, the file then vanished, and 445 was stranded in `claimed` forever. The dedup guard `active_plan_for_placeholder()` keys on `deposit_placeholder_name` (the descriptive slug), which can never equal `diagnostic-444.md`, so it is structurally blind to this class.

**Fix:** the daemon OWNS the canonical `<type>-<N>.md` namespace. Any *fresh deposit* using that form is never legitimate — quarantine it to `halted-` and skip the mint. This is a robust backstop: it stops the phantom mint regardless of how the id-form file leaked in (worktree merge, manual copy, agent self-naming).

## STEP 1 — DEV: add the reserved-form predicate + wire the claim guard

**`validators.py`** — add a pure, unit-testable predicate (module already imports `re`):

```python
def is_reserved_canonical_form(base_filename: str) -> bool:
    """True if base_filename is the daemon-owned canonical id-form <type>-<N>.md.
    The daemon mints these names itself at claim (in-progress-<type>-<id>.md,
    Done/<type>-<id>.md). A FRESH deposit using this form is never legitimate —
    it is a leaked in-progress/Done file (e.g. a worktree teardown-merge
    re-materializing decisions/<type>-<id>.md). Minting for it orphans a row
    (see the diagnostic-444 -> phantom-445 collision, 2026-08-18)."""
    return bool(re.fullmatch(r"(?:diagnostic|executable|qa)-\d+\.md", base_filename))
```

**`bellows.py`** — at the START of the FIRST `if not plan_filename.startswith("in-progress-"):` block (currently ~line 781), IMMEDIATELY BEFORE the `validation_result = validators.validate_at_claim(` line, insert the guard (all referenced names — `plan_dir`, `base_filename`, `shutil`, `bellows`, `verdict`, `_log`, `slug_for`, `plan_name` — are already in scope here, matching the existing Rule 35 reject block just below):

```python
            # Reserved-namespace guard (RC-2): the daemon owns the canonical
            # id-form <type>-<N>.md. A fresh deposit using that form is a leaked
            # in-progress/Done file, never a real plan — minting orphans a row.
            if validators.is_reserved_canonical_form(base_filename):
                _log("WARN", f"reserved canonical-id-form deposit '{base_filename}' — daemon owns this namespace; quarantining without minting", slug=slug_for(plan_name))
                halted_path = os.path.join(plan_dir, f"halted-{base_filename}")
                shutil.move(plan_path, halted_path)
                if bellows is not None:
                    bellows._seen.discard(verdict.slug_from_path(plan_path))
                return
```

Placing it before `validate_at_claim` makes quarantine deterministic (independent of whether the leaked file happens to parse a valid header).

Targeted sanity (must stay green): `python3 -m pytest tests/test_validators.py -q 2>&1 | cat`

**Deposits:**
- `validators.py` (new `is_reserved_canonical_form` predicate)
- `bellows.py` (claim-path guard call, before `validate_at_claim`)
- dev note: `knowledge/development/reserved-id-form-guard-dev-2026-08-18.md`

## STEP 2 — QA: regression tests + full suite

Add to **`tests/test_validators.py`** two regression tests for the predicate:
- `test_reserved_canonical_form_matches` — `diagnostic-444.md`, `executable-1.md`, `qa-99.md` → all `True`.
- `test_reserved_form_allows_legit_deposits` — each of these → `False`: a descriptive slug (`diagnostic-base-rate-class-break-alignment-2026-08-18.md`), lifecycle-prefixed forms (`in-progress-diagnostic-444.md`, `halted-diagnostic-444.md`), a non-numeric stem (`diagnostic-foo.md`), an empty number (`executable-.md`), and a non-md extension (`diagnostic-444.txt`).

Run the full suite: `python3 -m pytest tests/ -q 2>&1 | cat`. Deposit RAW stdout. Expect all pass (`known_failures: 0`).

**MANDATORY — Rule 20 self-check banner** (`## Rule 20 — QA Self-Check Results` + `**PASSED — SELF-CHECK PASSED**` verbatim, canonical block from `RULE_20_SELF_CHECK_BLOCK.md`). Values: `plan_slug`: `reserved-id-form-claim-guard-2026-08-18`; `qa_report_path`: `<abs>/knowledge/qa/reserved-id-form-guard-qa-2026-08-18.md`; `evidence_dir`: `<abs>/knowledge/qa/evidence/reserved-id-form-guard-2026-08-18/`; `required_evidence_files`: `[full-suite.txt]`. FAILED → halt.

**Deposits:**
- `tests/test_validators.py` (2 new regression tests)
- `knowledge/qa/reserved-id-form-guard-qa-2026-08-18.md` — QA report
- `knowledge/qa/evidence/reserved-id-form-guard-2026-08-18/full-suite.txt` — raw full-suite stdout

---

## Scope / non-goals
Adds one predicate + one guarded call in the claim path; no existing claim behavior changes for legitimately-named deposits (descriptive slugs and all lifecycle-prefixed names return `False`). Does NOT address RC-1 (worktree teardown-merge leaking out-of-scope agent writes into `decisions/`) — that is a deferred fork; this guard is the backstop that neutralizes RC-1's effect regardless.
