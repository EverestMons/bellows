# Walk register — `align-hook-sync-2026-08-26` (bellows)

**schema_version:** `0.3`

**Plan:** `bellows/knowledge/decisions/drafts/executable-align-hook-sync.md`
**Tier:** T1 (Small — one hook gains a bounded fetch-and-report arm + its own test file; class shop-infra, bellows hooks code). **Panel: none.**
**Opened:** 2026-08-26

---

## Walk 0 — context pin (REAL, measured 2026-08-26)

1. **CEO direction:** machines must start on fresh state; hook FETCHES and REPORTS (a fetch never mutates), /eluvian PULLS (548's deliberate act).
2. **Target pins:** hook 111 lines, sha-prefix `cf3184e91eb58920046c`, FAIL-OPEN wrapper verified; both edit anchors count-1; baselines 32 hook-tests / 1470 collected.
3. **Design notes:** (a) bounded 5s per git call, GIT_TERMINAL_PROMPT=0; (b) problems-only verbosity; (c) upstream-relative (`@{u}`), no hardcoded branch; (d) machine-portable by the existing resolution — the mini's non-git memory dir skipped by the `.git` existence test; (e) real-git tests, no mocks; (f) worst-case latency considered: 4 repos × 2 calls × 5s = 40s only if every call HANGS to timeout (real fetches ~0.5s; offline fails fast) — accepted, parallelization deferred.
4. **id prediction:** id_sequence read 554.

⚠️ Walk 0 carries no fold rows. Walks 1–2 appended AFTER the draft exists, from real passes.

---

## Walk 1 — five-lens sequential walk (post-draft, real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| A1 | 1 | 1 Weak spots | 1.2 | — | The "no upstream" test was shaped as init-without-remote — but there fetch FAILS FIRST, so `_repo_sync` returns "fetch FAILED", not "no upstream": the test would assert an unreachable expectation and fail on correct code. The reachable no-upstream state is remote-present + `git branch --unset-upstream` (fetch succeeds, `@{u}` resolution fails). | `no upstream (init, no tracking)` | Folded: Task C's fifth test re-shaped to unset-upstream on a working clone. |

**Walk 1 total: one finding, folded.** (Destruction dry — three-arm resume table, all writes in one commit; Vulnerabilities dry — report-only at three sites, every call bounded and inside the FAIL-OPEN wrapper, `@{u}` passed as a literal argv token; Integration-record dry — the smoke's any-state-is-a-pass clause matches network variability honestly; ACID dry — 38 = 32 + 6 with the supersede clause.)

---

## Walk 2 — five-lens sequential walk (confirming pass, real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| — | 2 | all five | — | — | DRY — the re-shaped fifth test traced through the code path by hand (fetch rc=0, rev-list rc!=0, fetch_failed False → "no upstream"); all other probes earnable. | — | No folds. |

**Walk 2 total: 0 findings — all five lenses dry. BAR MET; T1, no panel escalation.**
