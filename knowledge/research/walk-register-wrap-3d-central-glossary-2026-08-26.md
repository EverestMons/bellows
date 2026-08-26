# Walk register — `wrap-3d-central-glossary-2026-08-26` (bellows)

**schema_version:** `0.3`

**Plan:** `bellows/knowledge/decisions/drafts/executable-wrap-3d-central-glossary.md`
**Tier:** T1 (Small — two doc edits on bellows-owned files; wrap.md is a live command via the R-F1 symlinks, so class shop-infra). **Panel: none** (T1 two-walk form; escalate to Fork C only on a direction-class finding).
**Opened:** 2026-08-26

---

## Walk 0 — context pin (REAL, measured 2026-08-26)

1. **Diagnostic ground (this session, plan-542 arc):** the 542 DISCOVERY seat's mechanical-consumer sweep — `grep -rinF "glossary"` over bellows/hooks, bellows/tools, bellows/scripts, gates.py, forge — hit ONLY `hooks/commands/wrap.md` L61–65 (the 3d block). No tool or hook parses the per-repo glossary path; the prose block is the whole surface.
2. **Target pins:** wrap.md `wc -c` **5852**; the 3d block (L60–69) is the only "glossary" mention; `knowledge/glossary.md` **34 lines, 10 `## ` entries**; root `GLOSSARY.md` `[project: bellows]` count **10** (plan 542, byte-copied from the committed seed).
3. **Ordering law carried from 542 (SC-5):** the 3d scaffold clause must be gone BEFORE the pointer-ization — else the next wrap re-creates the per-repo file. Satisfied structurally: both edits in ONE step, W1 (wrap.md) sequenced before W2 (glossary.md), and W2 is guarded by a migration-completeness assert.
4. **Design notes (v0 facts, recorded here — NOT walk findings):**
   - **(a) Migration-completeness guard:** W2 does not trust 542's verbatim claim — Step 1 re-proves it: every `## <term>` body in the OLD glossary.md must match the `## <term> [project: bellows]` body in root GLOSSARY.md (trailing-whitespace-normalized) BEFORE the pointer overwrite; any mismatch HALTs with both terms named. The guard is in the control flow, not a printed note.
   - **(b) No plan-predicted post-counts:** the post-edit `"glossary"` occurrence count on wrap.md is MEASURED by Step 1 and recorded in the dev note; QA compares against the recorded value, never a plan-authored prediction (4/4 of authored predictions were wrong in a measured session).
   - **(c) Re-entry branches:** Step 1 opens with a state branch — 3d anchor present → full run; anchor absent AND glossary.md has 10 entries → W2-only resume; anchor absent AND pointer present → edits already landed, commit-check only. Death between W1 and W2 is a SAFE state (old file intact, scaffold clause already gone).
   - **(d) W2 pre-write assert:** the whole-file pointer overwrite (a RETIRING file, not a live draft) additionally asserts the file still has exactly 10 `## ` entries at write time.
5. **id prediction:** id_sequence read 543 (authoring-time prediction; an in-window dispatch consumes it).
6. **Anchor discipline:** W1's anchor is the full 10-line 3d block verbatim, count-1 asserted.

⚠️ Walk 0 carries no fold rows. Walks 1–2 are appended AFTER the draft exists, from real passes.

---

## Walk 1 — five-lens sequential walk (post-draft, real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| W1-F1 | 1 | 1 Weak spots | 1.2 | — | Entry-count probe written `-cF "^## "` — under -F the caret is a literal; the count silently reads 0 (probe-must-match-representation). | `/usr/bin/grep -cF -- "^## " knowledge/glossary.md` | Folded: regex `-c "^## "` at both sites with the warning inline. |
| W1-F2 | 1 | 2 Destruction | 2.2 | — | The plan cd'd ABSOLUTE into the live bellows tree — bellows dispatches into a WORKTREE; an absolute cd edits the live tree, defeats isolation and the teardown merge. | `…` at Tasks A/D and QA Item 1 | Folded: `cd "$(git rev-parse --show-toplevel)"` everywhere; all in-repo paths relative; Deposits repo-relative; the sole absolute path is the read-only root GLOSSARY.md; design note (e). |
| W1-F3 | 1 | 2 Destruction | 2.2 | — | Re-entry branch 3 keyed on `RETIRED>=1` alone — a torn half-written pointer would pass to commit-check and ship. | `(i)=0 AND (iii)>=1 → both edits landed` | Folded: branch 3 requires (iii)=1 ∧ (ii)=0 ∧ (iv)=1; the torn case is a named HALT arm; probe (iv) added. |

**Walk 1 total: 3 findings, 3 folded.**

---

## Walk 2 — five-lens sequential walk (confirming pass, real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| W2-1 | 2 | 1 Weak spots | 1.2 | — | DRY — `"If the file does not exist, create it"` measured count-1 in live wrap.md (the ==0 post-probe is earnable); case-insensitive glossary count measured 4 pre-edit. | — | No fold. |
| W2-2 | 2 | 2 Destruction | 2.2 | — | DRY — four branch predicates partition all death states incl. torn-pointer; `^` parent extraction correct in the worktree. | — | No fold. |
| W2-3 | 2 | 3 Vulnerabilities | 3.3 | — | DRY — term filter skips non-bellows tags; a multi-tag bellows entry fails CLOSED. | — | No fold. |
| W2-4 | 2 | 4 Integration-record | 4.1 | — | DRY — supersession chain in the pointer; open_forks carries the siblings; register single-line ref. | — | No fold. |
| W2-5 | 2 | 5 ACID | 5.2 | — | DRY. | — | No fold. |

**Walk 2 total: 0 findings — all five lenses dry. BAR MET; T1, no panel escalation (no direction-class finding).**
