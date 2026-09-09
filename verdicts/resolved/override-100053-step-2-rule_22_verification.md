# Override — plan 100053 STEP 2 — rule_22_verification (two rows, one cause)

**Date:** 2026-09-09 | **Ruled by:** CEO (verdict question answered in session d04ebd33) | **Gate:** rule_22_verification (c) | **Failures:** row 12 `Numstat 16 files ❌ 17 files — test_substrate_check.py (11 lines, worktree isolation) outside declared writes`; row for `git diff … tests/test_substrate_check.py → EMPTY ❌` (non-empty: the 11-line import shim).

**What happened.** The QA receipt reported, honestly and with the cause named, the two post-conditions the STEP 1 shim breaks — the plan lists that test file as UNCHANGED and QA Item 6 asserts its diff EMPTY. Rule 22 (c) fails on every ❌ row; two rows, one cause, the cause already overridden at STEP 1 (`override-100053-step-1-scope_check.md`).

**Why the override is granted.** The receipt did what the gate exists to make it do: it did not hide the deviation behind a ✅. Every other post-condition holds (suite 2145 passed; three run files at their manifests' commits; every real-artifact probe obtained).

**What is recorded against it, not excused.** The same worktree sys.path hazard (thread 243) — a plan cannot honestly promise an untouched test file whose import binds to another checkout; until 243 lands, a plan's "unchanged" list is a promise about the daemon's environment as much as the DEV's discipline.

**Files changed in the step:** the two evidence files, both declared.
