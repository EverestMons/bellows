# Walk register — `gate-watcher-staleness-2026-08-27` (bellows)

**schema_version:** `0.3`

**Plan:** `bellows/knowledge/decisions/drafts/executable-gate-watcher-arm-snapshot.md` (stable slug; corrected re-deposit after the exec-572 halt)
**Tier:** T1 (Small — a deletion plus one disk-read predicate, and a state-space test suite; class shop-infra). **Panel: none.**
**Opened:** 2026-08-27

---

## Walk 0 — context pin (REAL, measured 2026-08-27)

1. **The falsified premise.** Exec-572's `judge_watch_line` docstring asserts a pending request at arm time is "PRE-EXISTING — already resolved and awaiting daemon cleanup." Never checked. A watcher arming after a step completes but before the verdict issues swallows a GENUINE pause.
2. **Measured on 572 itself:** step-1 request written 08:39:03, no verdict issued, watcher logged `arm-time pending ignored: verdict-request-572-step-1.md` and next spoke only at `terminal=halted`. A missed pause, strictly worse than the spurious log line 572 set out to fix.
3. **The tests could not have caught it.** All 8 of 572's tests passed while encoding the same wrong premise. The one test that would have caught it — arm over an UNRESOLVED request and assert a normal pause — was unthinkable inside the author's model. This is why the corrective replaces example-led tests with a STATE SPACE enumerated from the system.
4. **The correction is a DELETION.** Staleness is a property of the request, readable from disk: stale iff `verdicts/resolved/` holds `verdict-<id>-step-<N>.md` or `processed-verdict-<id>-step-<N>.md` (both forms measured live on 570/571). The snapshot mechanism, the arm flag and the threading all go.
5. **The defective guard is CURRENTLY IN MAIN** — the halt stopped the plan, it did not revert the commit (`b092071`). Verified at authoring: `judge_watch_line` present ×2, `TestArmTimeSnapshot` present, 24 tests collected. Live blast radius is hand-runs only: the receipt's deposit-time spawn arms when nothing is pending, so `arm_pending` is None and the guard is inert there.
6. **Baselines:** `tests/test_gate_watcher.py` collects 24; full suite 1582 at exec-570 plus 572's 8 in tree.

⚠️ Walk 0 carries no fold rows. Walks 1+ appended AFTER the draft exists, from real passes.

---

## Walk 1 — five-lens sequential walk (post-draft, real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| — | 1 | Weak spots | — | — | DRY — B1-B5 each carry a live probe; the deletion targets are pinned by line; the stable-slug re-deposit matches the halted plan's placeholder name so QA's id lookup resolves | — | no fold |
| — | 1 | Destruction | — | — | DRY — the deletion is a revert to a known-green 16-test baseline, asserted by its own probe before new work lands; 572's tests are removed WITH their mechanism rather than adapted (adapting would preserve the falsified premise) | — | no fold |
| w1-1 | 1 | Vulnerabilities | is arming POSITION a real dimension of the thing under test? | pre-existing | the draft's product was `PENDING x VERDICT x POSITION x STATE` (48 cells) parametrized over `read_state` — but after the deletion `read_state` has NO notion of arming position, so every POSITION pair is identical BY CONSTRUCTION. The parametrization would pass trivially: a check that cannot fail, dressed as thoroughness | `POSITION = ("first_poll", "later_poll")` as a product dimension, with `len(CLASSIFICATION) == 2*3*2*4` and `REPORT_PAUSE at EVERY position, first_poll included` | folded: POSITION removed from the product (24 cells over `PENDING x VERDICT x STATE`), with an explicit note on WHY, and position pinned at the two layers where it can still exist — a structural test asserting `arm_pending`/`armed`/`judge_watch_line` are absent from the source, and a `judge_transition`-layer test that prev cannot change the phase |
| — | 1 | Integration-record | — | — | DRY — manifest reads include the halted plan; deposits/scope agree on six files; thread-20 closure and its scope correction declared as Planner close acts | — | no fold |
| — | 1 | ACID | — | — | DRY — two pathspec-limited commits, toplevel-first, each with a 3-file assert | — | no fold |

**Walk 1 total: 1 finding (instruction 1 / record 0), folded. Direction verdict: PROCEED — the delete-and-check shape held.**

---

## Walk 2 — five-lens sequential walk (real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| w2-1 | 2 | Weak spots | can the drift guard ever actually run? | fold-introduced (w1's new test 5) | the reachable-states test opens the live DB and skips when absent — but DEV and QA BOTH run in worktrees, which carry no `lifecycle.db`, so it would skip in both and prove nothing. A permanently-skipping test is the vacuous-check class wearing a coverage badge | `open the LIVE DB read-only if present, SELECT DISTINCT lifecycle_state, and assert every value observed is in STATE; skip cleanly when no live DB is reachable (worktree)` | folded: the test reads a `GATE_WATCHER_LIVE_DB` env var, the skip is called out as the failure mode in the instruction itself, and QA gained Item 2.6 which runs it with that var pointed at the live checkout and requires `1 passed, 0 skipped` with `-rs` output pasted |
| — | 2 | Destruction | — | — | DRY — probes write only to `mktemp -d` and an untracked log; the real `verdicts/` is never touched (both `--pending-dir` and `--resolved-dir` are injected) | — | no fold |
| — | 2 | Vulnerabilities | — | — | DRY — unparseable request names fail TOWARD reporting; terminal beats pending (stray-file law) is an explicit classification rule, not an implicit branch | — | no fold |
| — | 2 | Integration-record | — | — | DRY | — | no fold |
| — | 2 | ACID | — | — | DRY | — | no fold |

**Walk 2 total: 1 finding (instruction 1 / record 0), folded. Bar NOT met.**

---

## Walk 3 — five-lens sequential walk (real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| — | 3 | Weak spots | — | — | DRY — `--resolved-dir` is declared as a new CLI arg in the gate note and threaded at both `read_state` call sites; the derivation `dirname(abspath(pend)) + "/resolved"` was traced against the QA scratch layout and against the live layout | — | no fold |
| — | 3 | Destruction | — | — | DRY | — | no fold |
| w3-1 | 3 | Vulnerabilities | does QA Item 2.1 actually reproduce the 572 regression? | pre-existing | ⚠️ **NO — and the claim would have been false in the record.** 572's guard lived in the POLL LOOP (`judge_watch_line`); `read_state` was never touched by it, so a `--status` call in that world returns `awaiting-verdict` BEFORE and AFTER this plan. The probe is non-discriminating and was labelled as the regression kill | `⚠️ **Under 572's shipped code this same world produced an armed-over/no-pause result — that is the regression this plan exists to kill. If this reads anything but awaiting-verdict, HALT.**` | folded: Item 2.1 relabelled a CONTROL with its non-discriminating nature stated for the receipt, and a new Item 1b added that runs the LOOP over an unresolved pause and asserts `pending=…` appears ≥1 while `armed over pre-existing` appears 0 — the layer where the regression actually lives |
| — | 3 | Integration-record | — | — | DRY | — | no fold |
| — | 3 | ACID | — | — | DRY | — | no fold |

**Walk 3 total: 1 finding (instruction 1 / record 0), folded. Bar NOT met.**

---

## Walk 4 — five-lens sequential walk (confirming pass, real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| — | 4 | Weak spots | — | — | DRY — test numbering reconciled 1-9 after the renumber; the targeted-count line refuses to predict the parametrize expansion and orders `--collect-only` first | — | no fold |
| — | 4 | Destruction | — | — | DRY | — | no fold |
| — | 4 | Vulnerabilities | — | — | DRY — every discriminating probe now carries its control (2.1 controls 1b; the classification's NO_PAUSE cells control its REPORT_PAUSE cells); no absence claim without a positive control | — | no fold |
| — | 4 | Integration-record | — | — | DRY — manifest finalization declared as the close act; open_forks records the CEO-raised objective-test-suite arc and the daemon-cleanup fork | — | no fold |
| — | 4 | ACID | — | — | DRY | — | no fold |

**Walk 4 total: 0 findings — DRY. BAR MET.**

---

## Conformance (§5) — recorded at the freeze from ACTUAL runs

- **Fold verification (2026-08-27, `/usr/bin/grep -cF` on the draft):** w1-1 landed ×1 (`Arming POSITION is deliberately NOT a dimension`); w2-1 landed ×2 (`a test that only ever skips is a check that cannot fail`, `Force the drift guard to actually RUN`); w3-1 landed ×2 (`THE ACTUAL 572 REGRESSION`, `NOT a discriminating probe`). Superseded text verified ×0: `2*3*2*4`, `test_first_poll_and_later_poll_agree`, `Under 572's shipped code this same world produced an armed-over`.
- **Structure:** `grep -cE '^## STEP '` → 2.
- **run_check runs at the freeze (2026-08-27, all branched-on; lint at the DEPOSIT path via a `lintmirror-` copy in the real `decisions/`):** `lint` → `VERDICT=PASS — exit 0`; `cycle` → `VERDICT=PASS — BAR_MET`; `register` → `VERDICT=PASS — 1 CONFORMANT, 0 UNCONFORMANT` **on the first run** (the ellipsis-in-`pre_fold_text` trap that failed the 571 and 572 registers was avoided at authoring — third encounter, first time pre-empted).
- **fold_check (EARNED, not authored):** v0 reconstructed by reversing the w3-1 relabel (anchor asserted ×1), baselined, then the frozen draft diffed against it → `FOLD-CHECK CLEAN: machine-readable state unchanged (7 signals held)`. A post-fold baseline would have been a tautology.

## Closing

**Walks 1-4, yields 2 → 1 → 1 → 0. BAR MET on walk 4's dry confirming pass. Cold panel NOT convened — but noted honestly against that decision: exec-572 was also a T1 no-panel plan and shipped a false premise past FIVE dry-trending walks. The mitigation adopted here is not more walking; it is an oracle outside the author's model (the enumerated state space, the structural deletion probe, and the live drift guard forced to run). Walking finds what the author can imagine; the state space finds what the author did not classify. Close is MANUAL (CEO-lane verdicts; auto_close false).**
