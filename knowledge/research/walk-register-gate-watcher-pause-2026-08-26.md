# Walk register — `gate-watcher-pause-2026-08-26` (bellows)

**schema_version:** `0.3`

**Plan:** `bellows/knowledge/decisions/drafts/executable-gate-watcher-pause-detection.md`
**Tier:** T1 (Small — one anchored tool edit + additive tests; class shop-infra). **Panel: none.**
**Opened:** 2026-08-26

---

## Walk 0 — context pin (REAL, measured 2026-08-26)

1. **The defect, measured live twice before authoring:** `plans.lifecycle_state` never takes `awaiting_verdict` — `SELECT DISTINCT` on the live DB returns `abandoned, closed, halted` (+`in_progress` while anything runs); the only writers of that value are `bellows.py:1097`/`:1230` into **steps.status**, and only on gate FAILURE. Two session watchers keyed on the phantom arm spun past their paused targets (568, 569 — CEO-caught both times). Third instance of the [[schema-shape-is-not-write-behavior]] enum-arm class.
2. **The correct surface, already doctrine:** `bellows-watcher-per-deposited-plan` condition 1 names `verdicts/pending/verdict-request-<id>-step-N.md`. Writer: `verdict.py:180-188` (`post_verdict_request`), name form `verdict-request-{slug_from_path(plan_path)}-step-{N}.md`; the claim rename makes the plan file id-named so post-claim slug == str(plan_id) (measured artifacts: `processed-verdict-568-step-1.md`, `-569-step-1/2.md`).
3. **Design:** the fix lives entirely in `read_state` (the seam that already derives `plan_id`) + a `--pending-dir` CLI arg; pending dir defaults from the resolved db path's parent (split-path law, collapses live-default and `--db-path` cases); pause branch only on non-terminal states (stray-file law); glob id-scoped (plan-isolation law, condition 4). `judge_transition` renders the new phase generically — every existing line stays byte-identical.
4. **Evidence law applied (LESSONS 2026-08-26, minted on this very tool's failure):** every test and the QA discriminating probe CONSTRUCT the paused state; the probe output is unreachable on the pre-fix tool.
5. **Baselines:** `tests/test_gate_watcher.py` collects 9; full suite 1531 (exec-569 QA). id prediction: none recorded (deposit-time read).

⚠️ Walk 0 carries no fold rows. Walks 1+ appended AFTER the draft exists, from real passes.

---

## Walk 1 — five-lens sequential walk (post-draft, real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| w1-1 | 1 | Weak spots | is the pending-dir default derivation minimal and single-sourced? | pre-existing | the draft added a `_PENDING` module constant AND a three-way conditional (`pending_dir or (derive-from-db_path if db_path else _PENDING)`) — two sources for one value; `os.path.dirname(os.path.abspath(_DB))` IS `_ROOT`, so the constant and the conditional are dead complexity | `add _PENDING = os.path.join(_ROOT, "verdicts", "pending")` and `pend = pending_dir or (os.path.join(os.path.dirname(os.path.abspath(path)), "verdicts", "pending") if db_path else _PENDING)` | folded: single expression `pend = pending_dir or os.path.join(os.path.dirname(os.path.abspath(path)), "verdicts", "pending")`; the `_PENDING` constant removed from the instruction — complete pre-image bytes quoted, no ellipsis |
| — | 1 | Destruction | — | — | DRY — additive kwarg, both CLI call sites threaded; `pending` key absent → `pend_part` empty → every existing `WATCH:` line byte-identical; poll-loop dict equality keeps paused-state polls quiet (sorted list, deterministic) | — | no fold |
| w1-2 | 1 | Vulnerabilities | does test 3 PROVE the terminal path skips the glob? | pre-existing | the draft's parenthetical claimed a nonexistent-`pending_dir` variant proves the glob is not consulted — it proves nothing (`glob` on a missing dir returns `[]` without raising); the earnable proof is the stray MATCHING file: if the terminal path honored hits, `phase == "closed"` breaks | `(and the glob is provably not consulted: point pending_dir at a nonexistent path — no exception)` | folded: test 3 re-specified around the stray matching file as the proof, with the nonexistent-dir non-proof named as such |
| — | 1 | Integration-record | — | — | DRY — Deposits blocks name every file incl. the QA `.txt` (`pytest_full.txt`) for the qa_test_result gate; thread-12 closure and the memory-note update declared as Planner close acts (sandbox split) | — | no fold |
| w1-3 | 1 | ACID | is the QA evidence ever committed? | pre-existing | STEP 2 wrote three evidence files but had NO commit task — `deposit_exists` would pass in the worktree yet the merge would carry nothing; 569's QA committed its evidence (commit `5d64784`) | STEP 2 ended at Item 3 (receipt) with no commit instruction | folded: Item 4 added — pathspec-limited evidence commit with a `git show --stat` 3-file assert |

**Walk 1 total: 3 findings (instruction 3 / record 0), all folded; each fold grep-verified landed ×1 with superseded text ×0 (run recorded in the conformance block). Direction verdict: PROCEED — no direction-class finding.**

---

## Walk 2 — five-lens sequential walk (real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| — | 2 | Weak spots | — | — | DRY — relative `--db-path` handled by `abspath`; QA probe 1's expected `in_progress` is this plan's own live state during its QA step (the 569 precedent); expected-line literals match `judge_transition`'s field order (phase, id, gate-tail, pending-tail) | — | no fold |
| — | 2 | Destruction | — | — | DRY — a plan with several pending step files renders a sorted deterministic list; `claimed`-state glob is harmless (no request can exist pre-step); pre-claim (`row is None`) returns before the pause branch | — | no fold |
| — | 2 | Vulnerabilities | — | — | DRY — `plan_id` is a DB int (no glob metacharacters); foreign-id invisibility tested (test 2) AND live-probed (QA 2.3); terminal-skip tested (test 3); the discriminating probe carries its negative control (QA 2.1 vs 2.2) | — | no fold |
| — | 2 | Integration-record | — | — | DRY — manifest reads/writes complete vs the plan's actual file set; open_forks records the deposit_receipt no-change decision and the thread-14 mechanization | — | no fold |
| — | 2 | ACID | — | — | DRY — DEV commit 3-file assert; QA commit 3-file assert; both pathspec-limited, toplevel-first | — | no fold |

**Walk 2 total: 0 findings (instruction 0 / record 0) — DRY. Bar NOT met — a further confirming walk required.**

---

## Walk 3 — five-lens sequential walk (confirming pass, real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| — | 3 | Weak spots | — | — | DRY — Task B anchors each unique in the current tool (`_DB = ` ×1, `def read_state` ×1, the return dict ×1, `pid_part` line ×1); Task A resume probe keys on the hyphenated phase string, present only post-edit | — | no fold |
| — | 3 | Destruction | — | — | DRY | — | no fold |
| — | 3 | Vulnerabilities | — | — | DRY — no absence claim without a positive control (P1's absence pin carries P2's writer enumeration as its control) | — | no fold |
| — | 3 | Integration-record | — | — | DRY — manifest finalization declared as the close act; the register's fold list ×3 consistent with the plan's diff | — | no fold |
| — | 3 | ACID | — | — | DRY | — | no fold |

**Walk 3 total: 0 findings — DRY. Two consecutive fully-dry walks — BAR candidate met.**

---

## Conformance (§5) — recorded at the freeze from ACTUAL runs

- **Fold verification (walk 1, run 2026-08-26):** fold w1-1 landed ×1 (`collapses the live-default and`), superseded ×0 (`_PENDING = os.path.join`); fold w1-2 landed ×1 (`The stray file is the proof`), superseded ×0 (`provably not consulted`); fold w1-3 landed ×1 (`Item 4 — commit the evidence`). All via `/usr/bin/grep -cF` on the draft.
- **Structure:** `grep -cE '^## STEP '` → 2 (DEV+QA H2 headers present).
- **run_check runs at the freeze (2026-08-26, all branched-on, at the deposit path via the lintmirror copy):** `run_check.py lint` → `VERDICT=PASS — exit 0` (8 PASS rows; 6 advisory (o2) relative-path WARNs, the house Deposits form); `run_check.py cycle` → `VERDICT=PASS — BAR_MET`; `run_check.py register <this file>` → first run `VERDICT=FAIL` (row w1-1 `truncated_pre_fold_text` — ellipsis read as truncated pre-image bytes; complete bytes substituted), re-run `VERDICT=PASS — 1 file(s) CONFORMANT, 0 UNCONFORMANT`.
- **fold_check (earned, not authored):** v0 reconstructed by reversing the three folds (each reversal anchor asserted ×1), baselined, then the frozen draft diffed against it → `FOLD-CHECK CLEAN: machine-readable state unchanged (6 signals held)`. A baseline taken post-fold would have been a tautology; the reconstruction makes the CLEAN earnable.

## Closing

**Walks 1-3, yields 3 → 0 → 0 (instruction/record split: 3/0, 0/0, 0/0). Walk 3 confirmed walk 2's dry — BAR MET. Cold panel not convened (T1 additive corrective to a read-only reporter; 563/569 precedent). Close is MANUAL (CEO-lane verdicts; auto_close false). Manifest finalized at close: walks 3, yields 3,0,0, validation filled from the run_check verdicts recorded at the freeze.**
