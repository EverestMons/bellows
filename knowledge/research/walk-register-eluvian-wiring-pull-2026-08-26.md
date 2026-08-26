# Walk register — `eluvian-wiring-pull-2026-08-26` (bellows)

**schema_version:** `0.3`

**Plan:** `bellows/knowledge/decisions/drafts/executable-eluvian-wiring-pull.md`
**Tier:** T1 (Small — two doc edits: the live `/eluvian` command + one root-doctrine line; class shop-infra). **Panel: none** (T1 two-walk; direction-class escalates).
**Opened:** 2026-08-26

---

## Walk 0 — context pin (REAL, measured 2026-08-26)

1. **CEO directive (this session, verbatim intent):** `/eluvian` should "carry the proper wiring for how these systems work together" AND "pull any new code for any of the systems so that no matter the machine, the most recent version is being used."
2. **Target pins:** `hooks/commands/eluvian.md` 15 lines, sha-prefix `78ecaa35aaca2c09f032`; `ELUVIAN_PATH.md` 175 lines, the L131 R-F2 line anchor count-1 (the 542 D-3 owed fix — folded into this plan because the wiring the command recites must not contradict the doctrine it reads); bellows porcelain carries only lifecycle files (verdicts/receipts — wrap-time, disjoint).
3. **Repo enumeration measured:** 10 direct-child repos with origin remotes + the root + the memory repo — the pull step ENUMERATES dynamically (drift-proof-enumeration doctrine), never a hand list.
4. **Design notes (v0 facts):**
   - **(a) Pull safety envelope:** fetch always (`GIT_TERMINAL_PROMPT=0`); ff-only pulls ONLY when behind and not diverged; diverged / dirty-refused / fetch-failed → LOUD report, touch nothing; never merge/rebase automatically. The advisory law (fork 3) extends: a failed pull reports, never blocks.
   - **(b) Daemon-staleness warning:** if bellows pulled new commits, compare the RUNNING daemon's sha (status.py) to the new HEAD — differing shas report "daemon restart needed"; a running daemon executes the OLD code until restarted.
   - **(c) Wiring = recite + assert:** the wiring map is recited in the report AND asserted mechanically where cheap (GLOSSARY.md exists at root; lifecycle.db present; lessons-forge.db present) — verify-not-recall.
   - **(d) Command rewrite is a guarded whole-file replacement** (15-line file, sha-pinned pre-write) — not an anchored edit; the L131 edit IS anchored count-1.
   - **(e) Worktree law (543):** bellows files cwd-relative under `git rev-parse --show-toplevel`; the ONE root write (`ELUVIAN_PATH.md`) is absolute and committed in the ROOT repo in place.
5. **id prediction:** id_sequence read 548.

⚠️ Walk 0 carries no fold rows. Walks 1–2 appended AFTER the draft exists, from real passes.

---

## Walk 1 — five-lens sequential walk (post-draft, real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| E1 | 1 | 2 Destruction | 2.2 | — | A death between Tasks C and D re-runs from a FRESH worktree (transient deaths lose uncommitted work) and reaches Task C with the L131 anchor already consumed — the count-1 assert HALTs a correct state. | `Replace in ELUVIAN_PATH.md the anchor (count-1 asserted…)` with no prior-state branch | Folded: Task C opens with the already-done branch (anchor 0 + replacement present → ROOT_COMMIT recovered via `git log -1 -- ELUVIAN_PATH.md`, continue to D). |

**Walk 1 total: one finding, folded.** (Weak spots / Vulnerabilities / Integration-record / ACID dry — Item-3 negatives verified on the drafted content with positive controls; ff-only envelope; wiring claims trace to 542–547 live state; two pinned pathspec-limited commits.)

---

## Walk 2 — five-lens sequential walk (confirming pass, real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| W2-1 | 2 | 1 Weak spots | 1.2 | — | DRY — the folded branch's probes earnable; blockquote-fenced replacement per the 543 precedent. | — | No fold. |
| W2-2 | 2 | 2 Destruction | 2.2 | — | DRY — arms partition fresh-worktree and same-tree re-entries. | — | No fold. |
| W2-3 | 2 | 3 Vulnerabilities | 3.3 | — | DRY. | — | No fold. |
| W2-4 | 2 | 4 Integration-record | 4.1 | — | DRY. | — | No fold. |
| W2-5 | 2 | 5 ACID | 5.2 | — | DRY. | — | No fold. |

**Walk 2 total: 0 findings — all five lenses dry. BAR MET; T1, no panel escalation.**
