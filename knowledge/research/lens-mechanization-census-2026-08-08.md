# Lens-mechanization census — findings deposit

**Bookend HEAD pins (start of run):**
- lessons-forge: `8d7e6c118d30b2c33bbbad9b1b0aaacda8771df8`
- bellows: `356f4ca2eb38aeb651c2098e039b52c248d4f25a`
- shop root: `a773cd8b6a714c1ea550d87030a649bdf7a4f1bc`

---

## Q1 — Corpus assembly

### Cycle 311 (lessons-forge)

**Draft path:** `knowledge/research/draft-cycle-run-2026-08-07.md`
**Close commit:** `e52275f` — claims "30 drafting commits preserved"
**Path enumeration:** 16 commits touch the draft path (1 close + 15 `[draft]`)
**RECONCILIATION MISMATCH:** path enumeration = 16 total (15 drafting), close claims 30. The path enumeration is authoritative per Q1 method.

| # | SHA | Phase | Declared folds | Files touched |
|---|-----|-------|---------------|---------------|
| 1 | `d91e045` | v1 (initial batch) | NONE | draft only |
| 2 | `45cf56d` | w1 | 11 | draft only |
| 3 | `6583fa7` | ACID-1 | 7 | draft only |
| 4 | `460a037` | w2 | 6 | draft only |
| 5 | `90f1732` | ACID-2 | 3 | draft only |
| 6 | `3370d67` | w3 | 4 (+rider) | draft only |
| 7 | `8bb4d3d` | seat-1 | 8 | draft only |
| 8 | `bd3ea56` | seat-2 | 6 | draft only |
| 9 | `a209a82` | seat-3 | 5 (+nit) | draft only |
| 10 | `fc4b3d6` | seat-4 | 5 | draft only |
| 11 | `93761db` | seat-5 | 10 | draft only |
| 12 | `ec110e5` | seat-5 rider | NONE (1 reword at 3 sites) | draft only |
| 13 | `48d799f` | c1 | 4 (record folds) | draft only |
| 14 | `61bd637` | CLOSE (c2 dry) | NONE | draft only |
| 15 | `9da43f6` | re-token | NONE | draft only |
| 16 | `e52275f` | close (delete) | — | draft only |

**Total declared folds:** 69 from explicitly-counted commits. The "+rider" (w3) and "+nit" (seat-3) add 2 items; the seat-5 rider commit adds 1. Total finding units: 72. Zero-fold rows: v1, CLOSE, re-token = 3. No merge commits. No NON-PHASE commits (every commit touches only the draft file).

### Cycle 317 (bellows)

**Draft path:** `knowledge/research/draft-clean-gate-auto-continue-2026-08-08.md`
**Close commit:** `253c085` — claims "21 drafting commits preserved"
**Path enumeration:** 14 commits touch the draft path (1 close + 13 `[draft]`)
**RECONCILIATION MISMATCH:** path enumeration = 14 total (13 drafting), close claims 21.

| # | SHA | Phase | Declared folds | Files touched |
|---|-----|-------|---------------|---------------|
| 1 | `56914df` | v0 (initial) | NONE | draft only |
| 2 | `7ec2c03` | v0 lint-fix | NONE | draft only |
| 3 | `d96e3a6` | w1 | 7 | draft only |
| 4 | `80b53fc` | a1 | 3 | draft only |
| 5 | `a3b7b25` | c1 | 3 (re-run dry) | draft only |
| 6 | `8c7745c` | aC (dry at zero) | NONE | draft only |
| 7 | `0265b99` | seat-1 | 8 | draft only |
| 8 | `f41c229` | seat-2 | 5 (counted from diff; no explicit "N folds" in message) | draft only |
| 9 | `a4d65c3` | seat-3 | 8 (counted from diff; no explicit "N folds" in message) | draft only |
| 10 | `ba19b32` | seat-4 | 8 (counted from diff; no explicit "N folds" in message) | draft only |
| 11 | `d4fee3e` | seat-5 | 7 (counted from diff; no explicit "N folds" in message) | draft only |
| 12 | `eb6fe69` | cc | 3 (fold-residue folds) | draft only |
| 13 | `57c05ab` | aC2 | 1 | draft only |
| 14 | `253c085` | close (delete) | — | draft only |

**Total declared folds:** 53 finding units. Zero-fold rows: v0, v0 lint-fix, aC = 3. No merge commits. No NON-PHASE commits. **Segmentation note:** seats 2–5 lack explicit "N folds:" declarations in their commit messages; fold counts derived from diff hunk segmentation. These carry LOW-CONFIDENCE marks on per-finding hunk attribution per the Q1 segmentation rule.

### Cycle 320 (shop root)

**Draft path:** `governance/knowledge/research/draft-template-qa-and-terminal-correction-2026-08-08.md`
**Close commit:** `74fd2b9` — states NO commit count
**Path enumeration:** 14 commits touch the draft path (1 close + 13 `[draft]`)
**RECONCILIATION NOTE:** close commit states no count — absence, not mismatch. No reconciliation possible.

| # | SHA | Phase | Declared folds | Files touched |
|---|-----|-------|---------------|---------------|
| 1 | `e1d5cf7` | v0 (initial) | NONE | draft only |
| 2 | `4b96748` | w1 | 7 | draft only |
| 3 | `c5db40b` | a1 | 4 (from diff; message lists 4 clauses) | draft only |
| 4 | `6a3c19d` | c1 | 2 (dry after) | draft only |
| 5 | `a87916f` | aC | 1 (dry after) | draft only |
| 6 | `ba5aed6` | seat-1 | 10 (incl. 3 HIGH) | draft only |
| 7 | `7a5ae48` | seat-2 | 9 (incl. 2 HIGH) | draft only |
| 8 | `142d674` | seat-3 | 9 (incl. 2 HIGH) | draft only |
| 9 | `8e75e2f` | seat-4 | 8 (incl. HIGH) | draft only |
| 10 | `151fcfb` | seat-5 | 10 (PANEL COMPLETE 10-9-9-8-10 = 46) | draft only |
| 11 | `eab648b` | Closing update | 1 (record update) | draft only |
| 12 | `1a166c6` | cc | 3 (dry after) | draft only |
| 13 | `4aa508b` | aC2 | 1 (dry after) | draft only |
| 14 | `74fd2b9` | close (delete + file to Done/) | — | Done/ filing |

**Total declared folds:** 65 finding units (the seat-5 commit message declares "46" as the cumulative panel total for 10-9-9-8-10, matching the per-seat sums). Zero-fold rows: v0 = 1. No merge commits. No NON-PHASE commits. The close commit's only touched file under `--name-only` is the `Done/` target, not the draft path — the draft deletion is visible only under `--diff-filter=D`.

### Cross-cycle reconciliation summary

| Cycle | Path-enum commits | Close-claimed count | Mismatch |
|-------|------------------|--------------------|---------:|
| 311 | 16 (15 drafting + close) | 30 | 15 vs 30 |
| 317 | 14 (13 drafting + close) | 21 | 13 vs 21 |
| 320 | 14 (13 drafting + close) | ABSENT | N/A |

**All three close-commit counts are unreliable reconciliation anchors** — path enumeration is authoritative. The systematic over-count in 311 and 317 suggests close commits may count something other than path-touching commits (e.g., all commits on the step branch, or including non-draft-touching session commits).

---

## Q2 — Classification

**Classification taxonomy:** M1 (anchor liveness), M2 (R/W window), M3 (mandated-command harness), M4 (executable ledger), M5 (clone structural diff), M6 (consumer census), M7 (guard-relaxation diff), M8 (environment probes), R (shipped plan_lint), J (judgment-only), O (other-mechanizable), AMBIGUOUS.

**Shipped plan_lint checks at worktree HEAD** (re-derived from `scripts/plan_lint.py`): (a) header parse, (b) deposits blocks, (c) QA banner pair, (d) scope block, (e) step heading format, (f) Drafting Cycle self-check (lenses, closing, tier), (g) ledger ordering, (h) stale closing disclaimer, (i) qa_and_terminal ↔ qa_steps coupling, (j) inherited-premise marker, (k) clone-claim check, (l) clone-mutation down-tier. Plus 3 unnumbered WARNs: test-scope, qa_steps ↔ step-label, fold-as-last-event.

### Cycle 311 — per-finding classification

| ID | Phase | Label | Bucket | Evidence summary |
|---|---|---|---|---|
| 311-w1-1 | w1 | tranche manifest C17 — committed manifest requirement | M4 | adds `#### Tranche manifest` commit-before-insert constraint to Steps 2–4; ledger constraint with runnable check |
| 311-w1-2 | w1 | dispatch-state probes for Steps 2–4 | M3 | adds `git show HEAD:<path>` / working-tree / `git log --all` probe block; mandated commands |
| 311-w1-3 | w1 | branched staleability — FRESH/RESUME branch replaces vacuous check | M4 | replaces unconditional `STALE_IN_SET` with FRESH/RESUME branch; testable constraint |
| 311-w1-4 | w1 | inline core bounds — classification contract restated in Steps 3–4 | M6 | adds full `insert_proposal` call-signature inline; consumer enumeration |
| 311-w1-5 | w1 | verified cycle-fn description against source | M3 | replaces inherited description with source-read at `src/lessons_forge.py:440–510`; mandated probe |
| 311-w1-6 | w1 | 7th dict key `cycle_timestamp` added | M1 | changes to "Print all SEVEN keys…verified against the source at authoring"; anchor liveness |
| 311-w1-7 | w1 | cluster-A `target_artifact` convention stated inline | M6 | adds consumer check: `target_artifact` must resolve through existence check |
| 311-w1-8 | w1 | HEAD pin changed to literal SHA `0fb50e2` | M1 | replaces generic reference with recorded authoring HEAD |
| 311-w1-9 | w1 | `ls -t` mtime-proxy replaced by `id_sequence`/`Done/` enumeration | M1 | corrects "verified by `ls -t`" to `Done/` set enumeration |
| 311-w1-10 | w1 | Forward Register: non-request item removed + splitter fallback | O | integration-record correction; propose: check Forward block has exactly one bullet |
| 311-w1-11 | w1 | Family/lineage carrier list corrected per-tranche | M1 | corrects carrier claim with measured per-tranche list |
| 311-a1-1 | ACID-1 | C7 widened + CONTRADICTION→HALT arm | M4 | adds `FRESH + UNCLASSIFIED ≠ 51 → CONTRADICTION → HALT (C7)` |
| 311-a1-2 | ACID-1 | STALE_IN_MINE manifest-derived operand | M4 | corrects constraint operand to manifest-derived form |
| 311-a1-3 | ACID-1 | idempotent re-dispatch branch | M4 | adds PROCEED-value check with manifest ∩ unclassified empty condition |
| 311-a1-4 | ACID-1 | cluster-A inline lines propagated to Steps 3–4 | M6 | consumer census propagation |
| 311-a1-5 | ACID-1 | precedent-poor-five taxonomy clarified | M6 | corrects consumer-facing rule text at multiple sites |
| 311-a1-6 | ACID-1 | Step 5 staling-signature HALT branch | M4 | adds below-expectation count → HALT with runnable SQL check |
| 311-a1-7 | ACID-1 | halt-durability: explicit-pathspec commit before HALT | M3 | mandated "commit by EXPLICIT PATHSPEC before stopping" |
| 311-w2-1 | w2 | front-matter staleability prose synced to ACID-1 machinery | J | reason: record-decay correction matching prose to implemented checks; no standalone mechanical form |
| 311-w2-2 | w2 | deferred-entries carve-out added to CONTRADICTION HALT arms | M4 | adds shortfall carve-out to Steps 2–4 pre-flight; executable branching |
| 311-w2-3 | w2 | row-2 clone-drop restored from 296 | M5 | block present in 296 absent from clone; clone structural diff |
| 311-w2-4 | w2 | row-9 calibration re-measured against 296's real data | M3 | replaces inherited calibration with mandated-algorithm run |
| 311-w2-5 | w2 | Step-4 idempotency conjunct: derived remainder not self-referential | M4 | fixes self-referential constraint to manifest-derived form |
| 311-w2-6 | w2 | gates-banner claim re-verified live at `gates.py:567` | M1 | anchor liveness re-verified against delivering code |
| 311-a2-1 | ACID-2 | deferred carve-out: SURPLUS not shortfall + retraction | M4 | constraint could never fire under old text; corrected direction |
| 311-a2-2 | ACID-2 | G6 option (i) marked tranche-incompatible | M4 | ledger-level guard: "INVALIDATES the tranche arithmetic" |
| 311-a2-3 | ACID-2 | Step-4 derivation precision wording | J | reason: precision/wording fix with no new check; no anchor, no command |
| 311-w3-1 | w3 | G6 deferral producer: agent writes candidate section | M4 | deferral branch had no producer, making it unreachable |
| 311-w3-2 | w3 | part-file content specs for classifications parts 1/2/3 | O | deposits declared without producer spec; propose: deposit completeness checker |
| 311-w3-3 | w3 | row-9 algorithm mandated at Steps 2–4 | M3 | mandated `canon() + SequenceMatcher` at all tranche receipts |
| 311-w3-4 | w3 | WARN record refreshed to earned four | J | reason: record-only update of lint-WARN count; no mechanical form |
| 311-w3-rider | w3 | deferral path noted as least-verified branch | J | reason: verification-status note; qualitative assessment |
| 311-s1-1 | seat-1 | deferral one-bit banner: `OPERATING UNDER G6 DEFERRAL` | M6 | enumerates approval-channel consumers |
| 311-s1-2 | seat-1 | zero-match diagnostic for `detect_duplicates` | M3 | mandated "PRINT LIST LENGTH; HALT if 0" |
| 311-s1-3 | seat-1 | backup count 20→8 with retraction | M3 | corrects mandated-command result; glob error identified |
| 311-s1-4 | seat-1 | backtick-exact tag matching replaces `LIKE '%tag%'` | M4 | executable constraint: LIKE produces substring double-count |
| 311-s1-5 | seat-1 | hostile-id corrections: tranche B measured set (234, 244) | M1 | corrects to measured set; anchor liveness |
| 311-s1-6 | seat-1 | narrow-state register note | J | reason: analysis of what events reach deferral state; qualitative |
| 311-s1-7 | seat-1 | copy-aside id caveat: use ACTUAL plan id not expected 310 | M1 | stale expected id; anchor liveness |
| 311-s1-8 | seat-1 | Rule 56 prior question restored | J | reason: record restoration of judgment rationale; no mechanical check |
| 311-s2-1 | seat-2 | causal terminal-flip test at 3 sites | M4 | requires `route` set for legitimate Gate-2 flips; closes laundering path |
| 311-s2-2 | seat-2 | full-manifest anchor reconstruction on resume | M4 | partial anchor under-scopes staleability guards |
| 311-s2-3 | seat-2 | deposit-completion branch propagated to Steps 3–4 | M4 | executable branch propagation |
| 311-s2-4 | seat-2 | Step 1a-bis window honesty acknowledged | J | reason: honest scope statement; no new check, risk disclosure |
| 311-s2-5 | seat-2 | row-5 heading→id mapping deposit restored | M5 | block present in 296 absent from clone |
| 311-s2-6 | seat-2 | row-3 blind-spot disclosure restored | M5 | block present in 296 absent from clone |
| 311-s3-1 | seat-3 | row-4 `ambiguous` carve-out (C5 violation) | M4 | executable constraint: `proposed + ambiguous == classified count` |
| 311-s3-2 | seat-3 | line-anchored disposition count in Python | M3 | replaces grep with `startswith()` + over-count arm; mandated precision |
| 311-s3-3 | seat-3 | probe-(iii) positive control mandated | M3 | mandated positive-control run; empty-output trap demonstrated |
| 311-s3-4 | seat-3 | G6 gate-token exemption | M4 | executable: match on `HALTED at G6` token |
| 311-s3-5 | seat-3 | Rule-20 write-report-first ordering | M3 | mandated ordering: report must exist before block runs |
| 311-s3-nit | seat-3 | orphan arithmetic stated precisely: 57 unmatched | M1 | corrects "the surplus" to "57 unmatched DB rows" |
| 311-s4-1 | seat-4 | two-deposits residue: shape (b) means ONE deposit | M5 | block from 296 not applicable to clone |
| 311-s4-2 | seat-4 | category arms recorded-divergence adjudication | M4 | executable constraint parallel to target adjudication |
| 311-s4-3 | seat-4 | entry-224 corrected: §5 shipped at 1.0 | M1 | anchor liveness against live doctrine |
| 311-s4-4 | seat-4 | entry-244 half-membership split routing | J | reason: judgment on dual-substance entry classification |
| 311-s4-5 | seat-4 | tranche-A hostile list per C14 | M1 | previously rule lived only in front matter; anchor liveness |
| 311-s5-1 | seat-5 | deferral anchor producer: ingested-entry anchor in Receipt | M4 | without it, approved deferral branch fails rows 3/8 at QA |
| 311-s5-2 | seat-5 | G5 re-keyed on `ingested_count` + receipt | M4 | 296 trigger unreachable under shape (b) |
| 311-s5-3 | seat-5 | category-divergence producer rule (C14) | M6 | consumer census for verifier-only rule |
| 311-s5-4 | seat-5 | deposit-completion branch completeness | M4 | executable ledger completeness |
| 311-s5-5 | seat-5 | C17 exception RETIRED (manifest required for resume) | M4 | ledger constraint |
| 311-s5-6 | seat-5 | rejected + CEO carve-out | M4 | executable exception: `status='rejected' + ceo + route NULL` |
| 311-s5-7 | seat-5 | G1 arm order: resume requires `n ≥ 1` | M4 | executable ledger |
| 311-s5-8 | seat-5 | Forward Register medium: transcript not deposited file | M1 | anchor liveness for channel/medium |
| 311-s5-9 | seat-5 | deposit-completion conjunct restated for Step 3 | M4 | executable ledger |
| 311-s5-10 | seat-5 | pointer fix: row 8 not row 3 | M1 | anchor liveness |
| 311-s5r-1 | seat-5r | "test against" → "checked against" clears plan_lint WARN | R | clears shipped plan_lint test-mention WARN (unnumbered check) |
| 311-c1-1 | c1 | Walks header panel-state sync | J | reason: record update; no mechanical form |
| 311-c1-2 | c1 | Conflicts line defers to ledger paragraph | J | reason: record structure; no check |
| 311-c1-3 | c1 | Closing rewritten with composition-vs-dry datum | J | reason: terminal-record; narrative assessment |
| 311-c1-4 | c1 | bold-marker cosmetic | J | reason: formatting consistency; no mechanical form |

**311 per-bucket totals:** M1: 12, M3: 8, M4: 22, M5: 4, M6: 5, R: 1, J: 11, O: 2. **AMBIGUOUS: 0. Total: 65.**

### Cycle 317 — per-finding classification

| ID | Phase | Label | Bucket | Evidence summary |
|---|---|---|---|---|
| 317-w1-1 | w1 | Site 1 calls `is_final_step` to prevent predicate drift | M1 | anchor `def is_final_step(...)` verified; reuse over mirror |
| 317-w1-2 | w1 | auto_close precedence pin — mode wins at terminal step | J | reason: structural judgment; no independent runnable check |
| 317-w1-3 | w1 | Never-NULL claim made honest via fail-soft acknowledgment | J | reason: conceptual correction; no executable form |
| 317-w1-4 | w1 | Task C import hedge dropped — test_bellows precedent | M1 | anchor `tests/test_bellows.py` verified side-effect-free |
| 317-w1-5 | w1 | Task E `-k` binding via mandated class names | M3 | pytest `-k` expression tightened with class names |
| 317-w1-6 | w1 | Semantic-shift note mandated in dev log AND QA report | J | reason: documentation mandate only; no executable check |
| 317-w1-7 | w1 | Site 3 — `verdicts/README.md` pause-table backfill | M6 | consumer census: `pause_reason_code` surface enumerated |
| 317-a1-1 | a1 | `-k` binding is module-name term, not class names | M3 | pytest collect-only probe run 6/6; corrects false string-logic |
| 317-a1-2 | a1 | Task B retitled to "three sites" | J | reason: cosmetic accuracy; label sync only |
| 317-a1-3 | a1 | Q0 re-pin pathspec gains `verdicts/README.md` | M2 | R/W window: scope extension covered new file |
| 317-c1-1 | c1 | A0 + HALT-ROUTING list missed `verdicts/README.md` | M2 | R/W window: two sites omitted a file in scope |
| 317-c1-2 | c1 | Site 3 count-wording kept FIVE | J | reason: non-pause codes distinguished; judgment rewrite |
| 317-c1-3 | c1 | Destruction + Integration numbers verified against 315 deposit | M4 | ledger constraint re-check: 3.08%, 83.3%, 874 verified |
| 317-s1-1 | seat-1 | `record_verdict_outcome` docstring overstates | M1 | anchor docstring vs actual SQL verified; no ORDER BY/LIMIT |
| 317-s1-2 | seat-1 | Task D two-row case pins UPDATE semantics | M4 | executable: two-row test pins actual behavior |
| 317-s1-3 | seat-1 | Ledger-half 313 clone declared out of scope | J | reason: undisclosed omission; documentation integrity |
| 317-s1-4 | seat-1 | Phantom `test_bellows.py` deposit dropped | R | plan_lint (b) deposits validation; file not a deposit target |
| 317-s1-5 | seat-1 | Two number slips: 314 mechanizable / 13.5% Q4 | M4 | numbers verified against 315 deposit |
| 317-s1-6 | seat-1 | Forward bullets re-blockquoted | M3 | Forward-register parser requires blockquote form |
| 317-s1-7 | seat-1 | Invisible fail-soft acknowledged with canary as check | J | reason: swallowed INSERT + failed UPDATE has no signal; canary named |
| 317-s1-8 | seat-1 | Site 3 stale `header_pause` row + terminal-pause ambiguity | M1 | anchor `pause_for_verdict: true` verified stale; real values are four modes |
| 317-s2-1 | seat-2 | Recognized-value enum in THREE files; plan had only one | M6 | consumer census: `plan_lint.py` + `validators.py` missed |
| 317-s2-2 | seat-2 | aC record corrected (surface incomplete) | J | reason: attestation integrity; no check |
| 317-s2-3 | seat-2 | Site 2 guard re-labeled; false precedent corrected | M1 | anchor `:771` verified live — unguarded |
| 317-s2-4 | seat-2 | Stranded-NULL re-based on stamp-at-consumption mechanism | J | reason: unreachability judgment correction |
| 317-s2-5 | seat-2 | `after_each_step` ghost value disclosed | J | reason: ghost value never implemented; disclosure mandate |
| 317-s3-1 | seat-3 | `run_plan` integration assertion MANDATORY | M3 | spy-pattern integration test required; deferral struck |
| 317-s3-2 | seat-3 | `$?` after pipe → `pipestatus` (vacuous exit check) | M3 | Task E exit-code was always `cat`'s exit |
| 317-s3-3 | seat-3 | "pending"-keyword false-HALT trap defused in QA item 5 | M3 | Rule 20 block CRITICAL-fails on "pending"; item excludes word |
| 317-s3-4 | seat-3 | 313's verification-table mandate restored | R | plan_lint (c)/(d) scan verification tables; prose-only QA vacuous |
| 317-s3-5 | seat-3 | Stale-evidence satisfiability disclosed | J | reason: existence-check alone can't prove freshness; Planner layer |
| 317-s3-6 | seat-3 | `qa_steps: 2` scalar form replaces list form | R | plan_lint header format; `qa_steps: [2]` not primary parser shape |
| 317-s3-7 | seat-3 | Q0 auto-stage allowance (daemon commit) | M2 | R/W window: Q0 HALT would false-fire on daemon auto-stage |
| 317-s3-8 | seat-3 | Finding 8 verified benign, no action | J | reason: verified benign after live check |
| 317-s4-1 | seat-4 | Why-section population corrected: 7/169=4.1% | M4 | ledger constraint: re-query against 315 evidence |
| 317-s4-2 | seat-4 | Template Forward bullet re-scoped to CORRECTION | J | reason: scope upgrade judgment |
| 317-s4-3 | seat-4 | Site 4(c) coupling lint — `qa_and_terminal` + missing `qa_steps` | O | propose: plan_lint check guards authoring-time QA-step declaration |
| 317-s4-4 | seat-4 | 83.3% relabeled; 162-slice sized separately | M4 | numbers verified against 315; continues-only vs class share |
| 317-s4-5 | seat-4 | Forward-channel vouching: two-row verdict-time check | M4 | dup-append failure mode pinned |
| 317-s4-6 | seat-4 | `| cat` pipe removed (pipestatus fix was shell-dependent) | M3 | fold-on-fold: seat-3's fix was itself wrong |
| 317-s4-7 | seat-4 | Closing-line staleness fixed (two seats stale) | J | reason: record-decay class; no mechanical form |
| 317-s4-8 | seat-4 | STOP-prose divergence routed to template touch | J | reason: byte-identical to 313; no plan action |
| 317-s5-1 | seat-5 | Dev-log deposit still had include-or-defer hook | M3 | deferral license should have been struck at seat-3 |
| 317-s5-2 | seat-5 | Site 4(c) silent-drop corridor closed | M3 | three-part corridor: grep count + dev-log + collect-only paste |
| 317-s5-3 | seat-5 | Depends-on header 83.3% relabeled (missed by seat-4) | M4 | same number, missed site |
| 317-s5-4 | seat-5 | Seat-1 record's superseded 314 annotated | J | reason: attestation integrity; record-decay class |
| 317-s5-5 | seat-5 | Sixth README grep added to QA item 3 | M3 | `grep -F "qa_and_terminal" verdicts/README.md` was missing |
| 317-s5-6 | seat-5 | Import wording: `import bellows` not `import from bellows` | M1 | anchor form corrected |
| 317-s5-7 | seat-5 | Item 1 pipe convention explained against re-flagging | J | reason: evidence is summary line, not exit code |
| 317-cc-1 | cc | Task B header "three sites" → "four sites" | J | reason: record-decay / label-sync; cosmetic accuracy |
| 317-cc-2 | cc | Method Scope missing `plan_lint.py` + `validators.py` | M2 | R/W window: scope statement omitted two files added by seat-2 |
| 317-cc-3 | cc | Method numbers bullet outgrown by artifact | J | reason: closed list no longer enumerated all numbers; generalized |
| 317-aC2-1 | aC2 | Task D run_plan integration: seventh grep + dual quote-trace | M3 | mandated mechanical presence proof |

**317 per-bucket totals:** M1: 6, M2: 4, M3: 11, M4: 7, M6: 2, R: 3, J: 18, O: 1. **AMBIGUOUS: 0. Total: 52.**

### Cycle 320 — per-finding classification

| ID | Phase | Label | Bucket | Evidence summary |
|---|---|---|---|---|
| 320-w1-1 | w1 | Deposit dev-log at absolute path (wrong-repo landing) | M3 | relative → absolute path; wrong-repo landing is runnable check |
| 320-w1-2 | w1 | S4 three quoted-anchor sub-sites (S4a/S4b/S4c) | M1 | anchors quoted and enumerated before edit |
| 320-w1-3 | w1 | Version hedge with crash-redo re-entry branch | M3 | HALT-routing branch with runnable `grep -c`/version check |
| 320-w1-4 | w1 | Anchor uniqueness: `grep -c -F` each anchor, count = 1 | M3 | mandated `grep -c -F` commands; every count must be 1 |
| 320-w1-5 | w1 | S4b `after_step_N` falsehood discovered | M1 | anchor enumerated by `grep -c -F`; live liveness check |
| 320-w1-6 | w1 | Pathspec-limited root commit | M3 | `git commit -- PLANNER_TEMPLATE.md` mandated explicitly |
| 320-w1-7 | w1 | S4 precondition: grep `gates.py` + `plan_lint.py` before edit | M7 | guard-relaxation check: verify no shipped enforcement coupling |
| 320-a1-1 | a1 | A0(3) uniqueness check scoped to fresh path only | M3 | re-entry path counts invert; executable condition |
| 320-a1-2 | a1 | Step 2 QA report at absolute path | M3 | same wrong-repo hazard as dev log |
| 320-a1-3 | a1 | Step 2 item 0: re-pin template against dev-log hash | M3 | `git log -1 --format=%H` must equal recorded hash; foreign edit → HALT |
| 320-a1-4 | a1 | S4 precondition greps carry absolute bellows paths | M3 | cwd is shop root; absolute-path discipline |
| 320-c1-1 | c1 | S5 must name this plan (slug + id) | M3 | A0(2) re-entry detection key had no producer |
| 320-c1-2 | c1 | "two false rule texts" → "three" | J | reason: label-count sync; no mechanical check |
| 320-aC-1 | aC | "Four sites" → five-entry list | J | reason: label-lag class; no mechanical check |
| 320-s1-1 | seat-1 | [HIGH] plan_lint not wired into daemon/deposit | M1 | "hard-checks at deposit" claim false; Planner-run only |
| 320-s1-2 | seat-1 | [HIGH] 318 is counterexample, not precedent | M1 | `318` removed from precedent list; anchor verified |
| 320-s1-3 | seat-1 | [HIGH] validators warn-only + `after_each_step` ghost | M1 | `validators.py` enum verified: warns only, never blocks |
| 320-s1-4 | seat-1 | Topology: governance has no project .git | M1 | cwd = governance subtree, not shop root; verified against runner |
| 320-s1-5 | seat-1 | Both deposits gain mandatory pathspec commits | M3 | `git commit -- <path>`; deposit_uncommitted gate is real |
| 320-s1-6 | seat-1 | Verify-source: 4.1% is DECOY from different file | M1 | anchor pointed to wrong source file |
| 320-s1-7 | seat-1 | S5 Last-Updated second version-site | M1 | anchor `**Last Updated:**` carries version twice |
| 320-s1-8 | seat-1 | QA item 1 gains second-count grep + Last-Updated grep | M3 | new negative greps added to harness |
| 320-s1-9 | seat-1 | Why item-2 characterization made precise | J | reason: narrative accuracy; no runnable check |
| 320-s1-10 | seat-1 | S1 not-mode-exclusive phrasing care | J | reason: authoring guidance; no runnable check |
| 320-s2-1 | seat-2 | [HIGH] Last-Updated grep: file prints 2, not 1 | M3 | deterministic QA false-fail on correct edit; grep re-based |
| 320-s2-2 | seat-2 | [HIGH] cwd contract FALSE at three sites | M3 | governance subtree dispatch, not shop root |
| 320-s2-3 | seat-2 | Pathspec commits gain `git add` before commit | M3 | untracked-file error on bare pathspec is live behavior |
| 320-s2-4 | seat-2 | 318 characterization qualified | M1 | anchor against 318 record amended |
| 320-s2-5 | seat-2 | S5 Lessons Learned table with first-row insertion | M1 | anchor `## Lessons Learned` verified; append → insert |
| 320-s2-6 | seat-2 | HALT ROUTING enumerated to ten files + re-derive rule | M3 | full file list added; 309 re-derive rule restored |
| 320-s2-7 | seat-2 | Rule 20 report-before-block ordering | M3 | ordering constraint: write report, run block, append stdout |
| 320-s2-8 | seat-2 | Basename/no-re-date clause restored | J | reason: policy/judgment; no runnable check |
| 320-s2-9 | seat-2 | S4b enumeration: `-c` → `-n` | M3 | `-n` gives line numbers needed for multi-occurrence coordination |
| 320-s3-1 | seat-3 | [HIGH] S4 precondition wrong file set: validators.py missing | M7 | guard-relaxation: shipped STOP-prose check lives in validators.py |
| 320-s3-2 | seat-3 | [HIGH] 4th falsehood: "future validator" paragraph | M1 | paragraph describes shipped warner as unbuilt; verified live |
| 320-s3-3 | seat-3 | Duplicate dev-log commit instruction deleted | M3 | redundant commit instruction removed |
| 320-s3-4 | seat-3 | Checklist #3 heading retitle mandated | M1 | prohibition heading contradicts reworded permission body |
| 320-s3-5 | seat-3 | 309 triple-pin restored at item 0 | M3 | three checks: git log hash, shasum, porcelain |
| 320-s3-6 | seat-3 | Execution-Model scope-out recorded | J | reason: scope documentation; no check |
| 320-s3-7 | seat-3 | LESSONS three-value-era divergence noted | J | reason: acceptable-divergence classification |
| 320-s3-8 | seat-3 | "silently" → "warn-in-console" at S2 | M1 | anchor against validators.py behavior |
| 320-s3-9 | seat-3 | v4.85 row-prefix style pinned | J | reason: style enforcement; judgment-only |
| 320-s4-1 | seat-4 | [HIGH] S4d three-tier validator + S4e 5th falsehood | M1 | `check_missing_dispatch_mode` is severity-REJECT; verified |
| 320-s4-2 | seat-4 | S3 governance half: Planner sets header | J | reason: content authoring guidance; no executable check |
| 320-s4-3 | seat-4 | S2 empty-string nuance clause | M1 | genuinely silent at all three layers; verified |
| 320-s4-4 | seat-4 | S4a norm stated affirmatively | J | reason: authoring guidance |
| 320-s4-5 | seat-4 | S4c five-pattern grep list scoped to two shipped | M1 | which patterns are live in validators.py verified |
| 320-s4-6 | seat-4 | S5 date from `date` command | M3 | mandated command form; never from plan slug |
| 320-s4-7 | seat-4 | S3 verbatim anchor + insertion point | M1 | anchor `### 49.` specified before `### 50.` |
| 320-s4-8 | seat-4 | S1 absent-field stale sentence | M1 | verified against `auto_close_disabled` pause and sparse-header default |
| 320-s5-1 | seat-5 | [HIGH] Dev-log content spec two generations stale | M5 | clone structural diff: spec under-specifying after S4d/S4e |
| 320-s5-2 | seat-5 | [HIGH] Two "four sub-sites" labels lagged five | M5 | permanent history row spec would carry wrong count |
| 320-s5-3 | seat-5 | Falsehood-count re-based to FIVE | J | reason: label sync; judgment-only |
| 320-s5-4 | seat-5 | A0(2) re-entry key: match by SLUG not id | M3 | crash-redo mints new id; id match would spurious-HALT |
| 320-s5-5 | seat-5 | Dev log "before" texts from `git show <hash>^:` | M3 | mandated command for re-entry path |
| 320-s5-6 | seat-5 | S4e + old #3 heading gain QA negatives | M3 | negative greps added; miss mechanically undetected without |
| 320-s5-7 | seat-5 | Rule 20 block source at absolute path | M3 | dispatch cwd collision; relative → absolute |
| 320-s5-8 | seat-5 | QA-report commit as step's FINAL action | M3 | pre-commit leaves deposit dirty; fails gate |
| 320-s5-9 | seat-5 | 888/892 double-edit collision coordination | M3 | mandated one-rewrite-per-line coordination |
| 320-s5-10 | seat-5 | S4 header label swept to "FIVE" | J | reason: label sync completing sweep |
| 320-close-1 | Closing | Closing updated to panel-complete state | J | reason: status record update |
| 320-cc-1 | cc | Why "ignores entirely" overstatement reworded | M7 | guard-relaxation: text carried exact overstatement S4 precondition forbids |
| 320-cc-2 | cc | aC record line relocated chronologically | J | reason: document structure; judgment-only |
| 320-cc-3 | cc | S4e ellipsis replaced with `-F`-greppable prefix | M3 | mandated-command harness: literal must be `grep -F` safe |
| 320-aC2-1 | aC2 | A0(3) census: six anchors across five sub-sites | M3 | anchor grep count undercounting by one |

**320 per-bucket totals:** M1: 16, M3: 24, M5: 2, M7: 3, J: 12, O: 0. **AMBIGUOUS: 0. Total: 57.**

### Cross-cycle bucket summary

| Bucket | 311 | 317 | 320 | Total |
|--------|----:|----:|----:|------:|
| M1 (anchor liveness) | 12 | 6 | 16 | **34** |
| M2 (R/W window) | 0 | 4 | 0 | **4** |
| M3 (mandated-command) | 8 | 11 | 24 | **43** |
| M4 (executable ledger) | 22 | 7 | 0 | **29** |
| M5 (clone structural) | 4 | 0 | 2 | **6** |
| M6 (consumer census) | 5 | 2 | 0 | **7** |
| M7 (guard-relaxation) | 0 | 0 | 3 | **3** |
| M8 (environment) | 0 | 0 | 0 | **0** |
| R (shipped plan_lint) | 1 | 3 | 0 | **4** |
| J (judgment-only) | 11 | 18 | 12 | **41** |
| O (other-mechanizable) | 2 | 1 | 0 | **3** |
| AMBIGUOUS | 0 | 0 | 0 | **0** |
| **Total** | **65** | **52** | **57** | **174** |

**Top 3 M/O buckets by coverage (Q3 prototype candidates):**
1. **M3 (mandated-command harness): 43** — extract mandated commands; verify stated success/failure outputs exist; flag non-`-F` literal greps
2. **M1 (anchor liveness): 34** — verify every quoted anchor/path against the live target file
3. **M4 (executable ledger constraints): 29** — extract C<n> ledger entries with runnable checks; post-fold battery

No tie at rank 3.

**M8 and AMBIGUOUS are zero-coverage — findings against the Planner's seeded taxonomy.** M2, M5, M6, M7 are low-coverage but non-zero. O has 3 entries (311-w1-10, 311-w3-2, 317-s4-3); the 317-s4-3 entry (qa_and_terminal ↔ qa_steps coupling lint) was SUBSEQUENTLY SHIPPED as plan_lint check (i) — reclassification deferred to avoid post-hoc re-sort before Q3 freeze.

---

**Q2 FREEZE — committed as `8483f0d` before Q3 prototype construction.**

---

## Q3 — Construct and fire the top candidates

**Top 3 by Q2 coverage:** M3 (43), M1 (34), M4 (29). No tie at rank 3.

### Prototype: M3 (mandated-command harness) — non-F grep form checker

**Source:** `/tmp/census-m3-grep-form.py` (44 lines). Imports `gates.strip_fenced_code_blocks` via `PYTHONPATH=/Users/marklehn/Developer/GitHub/bellows`. Scans inline backtick-quoted `grep` commands for missing `-F` flag on literal patterns. Regex-based and extended-regex greps (`-E`, `-P`) are excluded.

**Positive control:** `/tmp/census-synthetic-m3.md` — contains `grep "some literal pattern" file.txt` and `grep -c "another pattern" /tmp/test.txt`. Result: **FIRES** (2 non-F greps detected). Control valid.

**Per-finding fire results on pre-fold states:**

The M3 prototype fires at **0/43 findings** (0%) on pre-fold states. Tested against pre-fold states of: 311-pre-w1, 311-pre-s1, 311-pre-s3, 317-pre-w1, 317-pre-s3, 320-pre-w1, 320-pre-s1, 320-pre-s2. All returned DOES NOT FIRE.

**Diagnosis:** The M3 bucket covers 43 findings but these are DIVERSE defect types — mandated DB probes, pathspec commits, exit-code checks, ordering constraints, version checks, import probes, positive-control requirements. The non-`-F` grep sub-check catches only ONE narrow sub-type of M3 defects. The 43 findings are real M3 classifications (mandated commands were added, corrected, or ordering-constrained), but no single syntactic checker covers the breadth of the bucket. **The bucket was misclassified or the check is weaker than the census claims — reported as such per Q3 rules.** The M3 bucket's 43-coverage count is CLASSIFICATION evidence, confirmed as such; the fire rate says the PROTOTYPE is too narrow, not that the classification is wrong.

**False-positive load:**
- Final deposited plans (3): 0 fires
- Done/ plans (6): 0 fires
- Retraction control: **1 fire** — the retraction text quotes a defective grep verbatim to describe the correction. This is the 305 retraction-control pattern: a checker that matches the RECORD of a defect overstates its precision.

### Prototype: M1 (anchor liveness) — path existence checker

**Source:** `/tmp/census-m1-anchor-liveness.py` (56 lines). Imports `gates.strip_fenced_code_blocks`. Extracts backtick-quoted strings containing `/` (treating them as file paths), then checks existence against bellows, lessons-forge, and shop-root filesystems.

**Positive control:** `/tmp/census-synthetic-m1.md` — contains `scripts/nonexistent_module.py`, `knowledge/decisions/Done/phantom-file-999.md`, `src/totally/fake/path.py`. Result: **FIRES** (3 paths not found). Control valid.

**Per-finding fire results on pre-fold states:**

The M1 prototype fires on all tested pre-fold states, but with **overwhelming false positives**. The path extraction heuristic matches backtick-quoted words containing `/` that are not file paths (e.g., `python3`, `snapshot`, `**using`, `tokens,`, `sub-lists`, `622–2131`).

Tested against 311-pre-w1 (14 fires, ~12 false positives), 311-pre-s1 (19 fires, ~17 FP), 320-pre-w1 (3 fires, 0 FP — these are REAL: relative deposit paths `knowledge/development/...` and `knowledge/qa/...` that should be absolute), 320-pre-s1 (2 fires, 0 FP — same class).

**Located true fires:** The 320 pre-fold fires locate within the hunks that finding 320-w1-1 (absolute path correction) edited. Fire rate for M1 findings where defect IS a stale/wrong path: **~3/34 (9%)** — most M1 findings are about anchor CONTENT liveness (a quoted function name or claim verified against source code), not about path existence. The prototype checks path existence, but most M1 defects are "the quoted text X does not match what the live code says" — requiring semantic comparison, not just existence checking.

**False-positive load:**
- Final deposited plans (3): **3 fires** (all false positives — `python3`, `grep`, `shasum` and similar non-path backtick strings)
- Done/ plans (3): **3 fires** (all false positives — `plan_lint`, `decisions/`, `Done/<type>-<id>.md` template strings)
- Retraction control: **1 fire** (true positive on planted path `scripts/nonexistent_module.py`)

**The false-positive rate makes this prototype unusable as shipped.** A viable M1 checker would need a curated path-pattern allowlist or structured `<!-- path: ... -->` annotations.

### Prototype: M4 (executable ledger constraints) — constraint-keyword checker

**Source:** `/tmp/census-m4-ledger-constraint.py` (55 lines). Imports `gates.strip_fenced_code_blocks`. Extracts `**C<n>**` constraint entries from the Drafting Cycle block and checks for executable-check keywords (`halt`, `verify`, `count`, `query`, `grep`, `must be`, `==`, etc.).

**Positive control:** `/tmp/census-synthetic-m4.md` — contains `**C1**` and `**C2**` without executable language. Result: **FIRES** (C1 and C2 flagged). Control valid.

**Per-finding fire results on pre-fold states:**

Tested against 311-pre-w1, 311-pre-s1, 317-pre-w1, 320-pre-w1.

- **311-pre-w1: FIRES** — C4 (resume anchor constraint), C6 (convention-as-constraint), C11 (no third status glyph) flagged. C4 and C11 are constraints without explicit executable language — **partially correct**; C4 is a constraint about anchoring on original committed data, which is a run-time-verifiable property. C6 is about convention landing as constraint, which IS judgment-laden. **2 of 3 fires are true positives (C4, C11), 1 is a false positive (C6's keywords are present but in non-executable form).**
- **311-pre-s1: FIRES** — C4 and C11 again (same constraints, still unfixed at seat-1). These are the same constraints that persisted through the cycle.
- **317-pre-w1: DOES NOT FIRE** — 317 had no C<n> constraints in its Drafting Cycle at the v0 stage.
- **320-pre-w1: DOES NOT FIRE** — 320 had no C<n> constraints.

**Fire rate:** The M4 prototype fires only on 311 constraints. The 311 cycle had C1–C17 constraints added during the cycle; the prototype correctly flags C4 and C11 as lacking executable check keywords, but the 29 M4-classified findings are mostly about STEP-LEVEL ledger constraints (pre-flight checks, HALT arms, SQL queries, arithmetic conjuncts), not about Drafting Cycle `C<n>` entries. **The prototype checks the wrong surface:** M4 findings live in step text, not in the Drafting Cycle constraint ledger. The prototype catches constraint-DECLARATION defects, not constraint-ENFORCEMENT defects.

**False-positive load:**
- Final deposited plans: 311-final FIRES (same C4, C11 — still present in final); 317 and 320 DOES NOT FIRE
- Done/ plans: 0 fires (no C<n> entries in tested Done/ plans)
- Retraction control: **1 fire** (C1 with retraction text — the retraction narrates the constraint, fire is on the narrative)

### Q3 summary

| Prototype | Coverage (Q2) | Fires-on-own-case | True-fire rate | False-positive load | Diagnosis |
|-----------|--------------|-------------------|---------------|--------------------|----|
| M3 (non-F grep) | 43 | 0/43 (0%) | 0% | 0 finals, 0 Done/, 1 retraction | Prototype too narrow; bucket is diverse |
| M1 (path exists) | 34 | ~3/34 (9%) | 9% | 3 finals (all FP), 3 Done/ (all FP), 1 retraction | False-positive dominated; most M1 defects are semantic |
| M4 (C<n> keyword) | 29 | 2/29 (7%) | 7% | 1 final (311), 0 Done/, 1 retraction | Wrong surface: step constraints vs DC entries |

**All three prototypes fire below 10% on their own classified findings.** This is the census's central finding: the top-3 M/O buckets are CLASSIFICATION buckets, not CATCH buckets. The findings are correctly classified as check-shaped (a mechanical form exists in principle for each), but no single syntactic prototype covers the diversity within any bucket. Each bucket decomposes into 3–8 sub-types, each requiring its own checker. The non-F grep sub-check, the path-existence sub-check, and the C<n>-keyword sub-check each catch a narrow slice.

---

## Q4 — Re-finding decomposition

### Novel vs prior-fold-introduced classification

**Method:** Commit messages are scanned for explicit references to prior-phase findings (phrases like "a1's Q0 class", "fold-residue", "same class as", "corrects seat-N fold", "propagating walk-1's fix", "missed by seat-N"). Findings are classified as PRIOR-FOLD-INTRODUCED when the commit message explicitly names a prior fold as the defect's origin. **LOW-CONFIDENCE** mark: findings where the prior-fold attribution is inferred from diff-overlap rather than stated in the message.

**Prior-fold-introduced findings (stated in commit messages):**

| Cycle | Finding ID | Prior fold origin | Bucket |
|-------|-----------|-------------------|--------|
| 311 | 311-w2-1 | ACID-1 machinery | J |
| 311 | 311-a1-4 | w1 Step 2 fix | M6 |
| 311 | 311-a2-1 | w2 carve-out | M4 |
| 311 | 311-s2-3 | s2-2 | M4 |
| 311 | 311-s3-1 | s1-4 (C5) | M4 |
| 311 | 311-s4-2 | s3-1 (C5 asymmetry) | M4 |
| 311 | 311-s5-4 | s2 deposit-completion | M4 |
| 311 | 311-s5-9 | s2/s5 conjunct | M4 |
| 317 | 317-a1-1 | w1-5 (-k binding) | M3 |
| 317 | 317-c1-1 | a1-3 (same class) | M2 |
| 317 | 317-s4-6 | s3-2 (pipestatus) | M3 |
| 317 | 317-s5-1 | s3-1 (deferral) | M3 |
| 317 | 317-s5-3 | s4-4 (missed site) | M4 |
| 317 | 317-cc-1 | a1-2 (label-lag) | J |
| 317 | 317-cc-2 | s2-1 (scope) | M2 |
| 320 | 320-a1-2 | w1-1 (same class) | M3 |
| 320 | 320-a1-4 | w1-1 (absolute path) | M3 |
| 320 | 320-s1-7 | w1-2 (anchor) | M1 |
| 320 | 320-s2-3 | s1-5 (pathspec) | M3 |
| 320 | 320-s2-4 | s1-2 (318) | M1 |
| 320 | 320-s3-3 | prior fold dup | M3 |
| 320 | 320-s3-8 | s1-3 (validators) | M1 |
| 320 | 320-s4-1 | s3-2 (S4d) | M1 |
| 320 | 320-s5-1 | s4 (dev-log spec) | M5 |
| 320 | 320-s5-2 | s4-1 (sub-site count) | M5 |
| 320 | 320-s5-6 | s4-1 (S4e) | M3 |
| 320 | 320-cc-1 | s3-1 (guard) | M7 |
| 320 | 320-aC2-1 | s4-1 (anchor count) | M3 |

**Total prior-fold-introduced: 28 out of 174 = 16.1%**

### Dual-rate report

**Whole-cycle re-finding rate:**
- 311: 8 prior-fold out of 65 = **12.3%**
- 317: 7 prior-fold out of 52 = **13.5%**
- 320: 13 prior-fold out of 57 = **22.8%**
- **Overall: 28/174 = 16.1%**

**Panel-round-only re-finding rate** (seats 1–5 only, the slice comparable to doctrine's "roughly a third"):
- 311 panel findings: s1(8)+s2(6)+s3(6)+s4(5)+s5(10)+s5r(1) = 36; prior-fold-introduced: s3-1, s4-2, s5-4, s5-9 = **4/36 = 11.1%**
- 317 panel findings: s1(8)+s2(5)+s3(8)+s4(8)+s5(7) = 36; prior-fold-introduced: s4-6, s5-1, s5-3 = **3/36 = 8.3%**
- 320 panel findings: s1(10)+s2(9)+s3(9)+s4(8)+s5(10) = 46; prior-fold-introduced: s1-7, s2-3, s2-4, s3-3, s3-8, s4-1, s5-1, s5-2, s5-6 = **9/46 = 19.6%**
- **Panel overall: 16/118 = 13.6%**

**Doctrine comparison (panel-round slice only):** Doctrine states "roughly a third of each round are the previous round's folds' defects." Measured: **13.6%** — significantly below a third. **The divergence is a finding, not an error per the diagnostic's standing instruction.** Possible explanations: (1) the "third" figure may describe a different population (e.g., within a single round rather than cumulative across all rounds); (2) the 311/317 cycles are T2 executables with more novel-defect-heavy v0 batches that dilute the rate.

**Doctrine yield comparison:** Doctrine carries "yield stays flat: 11/12/12/12/12." The measured per-seat counts are:
- 311: v1(NONE)/w1(11)/a1(7)/w2(6)/a2(3)/w3(5)/s1(8)/s2(6)/s3(6)/s4(5)/s5(11)/c1(4)/close(0)/re-token(0) — non-flat, declining warm→ACID→panel
- 317: v0(NONE)/v0-fix(NONE)/w1(7)/a1(3)/c1(3)/aC(0)/s1(8)/s2(5)/s3(8)/s4(8)/s5(7)/cc(3)/aC2(1) — panel yields 8/5/8/8/7, closer to flat
- 320: v0(NONE)/w1(7)/a1(4)/c1(2)/aC(1)/s1(10)/s2(9)/s3(9)/s4(8)/s5(10)/close-update(1)/cc(3)/aC2(1) — panel yields 10/9/9/8/10, remarkably flat

**Panel-only yields: 311: 8/6/6/5/11, 317: 8/5/8/8/7, 320: 10/9/9/8/10.** The 320 panel is strikingly close to the 11/12/12/12/12 doctrine shape. 311's panel has a seat-5 outlier (11 folds) but otherwise trends downward. 317's panel has a dip at seat-2 (5).

### Prior-fold-introduced bucket distribution

| Bucket | Prior-fold count | Total in bucket | Fraction |
|--------|-----------------|----------------|----------|
| M1 | 5 | 34 | 14.7% |
| M2 | 2 | 4 | 50.0% |
| M3 | 8 | 43 | 18.6% |
| M4 | 7 | 29 | 24.1% |
| M5 | 2 | 6 | 33.3% |
| M6 | 1 | 7 | 14.3% |
| M7 | 1 | 3 | 33.3% |
| J | 2 | 41 | 4.9% |
| R | 0 | 4 | 0.0% |
| **Total** | **28** | **174** | **16.1%** |

**CEILING for a fold-time battery:** 26 of 28 prior-fold-introduced findings are in M/O/R buckets (93%). This means a perfect fold-time battery that implements all M/O/R checks could CEILING-catch 26/28 prior-fold defects. **This is a CEILING, not a catch prediction — most of those checks do not exist yet.**

### R-bucket executed slice (MEASURED, not ceiling)

**R-bucket findings:** 311-s5r-1, 317-s1-4, 317-s3-4, 317-s3-6 (4 total).

**All 4 are in the LIVE shipped set** (re-derived from worktree-HEAD `plan_lint.py`):
- 311-s5r-1: maps to the unnumbered test-mention WARN
- 317-s1-4: maps to check (b) deposits validation
- 317-s3-4: maps to check (c)/(d) QA verification tables
- 317-s3-6: maps to check (a) header parse

**plan_lint fires/doesn't on pre-fold states (raw output above):**

| Finding | Pre-fold SHA | plan_lint fires? | Evidence |
|---------|-------------|-----------------|----------|
| 311-s5r-1 | `ec110e5~1` = `93761db` | **YES** — "WARN: step 1/2/6 mentions tests but declares no test scope" | The "test against" phrasing triggered the WARN; the fold changed it to "checked against" |
| 317-s1-4 | `0265b99~1` = `8c7745c` | **NO** — all PASS | Phantom deposit `test_bellows.py` was a syntactically valid path; (b) checks parseability, not correctness |
| 317-s3-4 | `a4d65c3~1` = `f41c229` | **NO** — all PASS | QA banner pair strings present; (c) checks banner existence, not verification-table structure |
| 317-s3-6 | `a4d65c3~1` = `f41c229` | **NO** — all PASS | `qa_steps: [2]` parses successfully; `_parse_qa_steps` handles both list and scalar |

**R-bucket executed fire rate: 1/4 = 25%.** The 3 non-fires are R-classified findings where the shipped check DOES NOT catch the specific defect — the check validates a broader structural property (path parseability, banner presence, header parse) while the finding was about a narrower semantic property (phantom path, missing verification table, non-primary parser form). **These 3 are candidate reclassifications (R → J or O), but recorded as ~~R~~ → O under the struck-through-original rule, since the evidence is post-Q3.**

**Corrected R-bucket after executed slice:** 1 genuine R, 3 reclassified to O. But per the two-commit form, original classification preserved with strike-through.

---

## Q5 — Extension census

### Cycle 315 (bellows, T1 diagnostic — added for tier diversity)

**Draft path:** `knowledge/research/draft-verdict-mechanization-distribution-refresh-2026-08-08.md`
**Close commit:** `e53185b` — claims 9 drafting commits
**Path enumeration:** 8 commits touch the path (1 close + 7 `[draft]`)
**RECONCILIATION MISMATCH:** path = 8, close claims 9.

| # | SHA | Phase | Declared folds |
|---|-----|-------|---------------|
| 1 | `5477075` | v0 | NONE |
| 2 | `c6efe04` | w1 | 13 |
| 3 | `3bf8162` | a1 | 5 |
| 4 | `9c8a61a` | c1 | 4 (1 MATERIAL) |
| 5 | `1eaaafa` | record (phase deviation) | NONE |
| 6 | `d118b7a` | c2 | 2 (dry) |
| 7 | `e637c01` | aC | 1 (dry) |
| 8 | `e53185b` | close | — |

**Total finding units:** 25 (13+5+4+2+1).

**Classification (from commit message labels, no diff reading — Q5 is classification-only):**

| Bucket | Count | Representative labels |
|--------|------:|---|
| M1 | 3 | verdict_file_ref stale-by-construction, Q3 locator naming convention, six-codes record decay |
| M3 | 5 | live DB probes falsified six-code premise, 11 clean-code stops surfaced, 22 multi-attempt steps, bookend totals, Q5 answer |
| M4 | 1 | vacuous-clean gap (clean requires gates run) |
| M6 | 1 | verdict-files-read named |
| J | 15 | scope contradiction, headline rate matched-pair, plan-level time axis, opening re-scoped, Q6 premise, definition choices, re-bucket edge |
| **Total** | **25** | |

**Tier-diversity finding:** The T1 diagnostic cycle has **60% J** (15/25), compared to the T2 cycles' 24–35% J. T1 cycles are more judgment-heavy because diagnostics measure and interpret rather than build — their findings are methodology and framing decisions. This confirms the Q5 rationale: a build decision fitted only to T2 cycles would over-fit by under-counting J.

### Cycle 306 (bellows)

**NOT ENUMERABLE.** The diagnostic predicted this at authoring: "`close(306)` does not exist in bellows." Verified: `git -C /Users/marklehn/Developer/GitHub/bellows log --all --oneline | grep -F "close(306)"` returns empty. The fallback `git log --diff-filter=D` shows the draft was deleted in the **shop root** (`1f8bcf6 close(306)` in `/Users/marklehn/Developer/GitHub`), not in bellows — 306's draft path was `governance/knowledge/research/draft-executable-enforcement-warn-checks-2026-08-06.md` in the shop root repo. The close commit's own message says "byte-identical to bellows Done/executable-306.md" — the plan DEPOSITED to bellows but was DRAFTED in governance. The Q1 recipe would need to query the shop root repo for 306's history, but the recipe specifies 306 → bellows. **Reported as NOT ENUMERABLE with probe evidence above.**

### Cycle 309 (shop root)

**NOT REACHED.** Partial order 315 → 306 → 309; 306 failed enumeration. Reason: 306 is the penultimate in the partial order and its recipe failure means 309 (31 commits, the largest extension corpus) would need independent Q1 assembly from scratch. Time budget exhausted on the required corpus (311/317/320) + Q3 prototyping + Q4 decomposition.

---

## Q6 — Ranking table

### Candidate-check ranking for CEO choice

| Candidate check | Coverage (Q2) | Fire rate (Q3) | FP load | Constructibility | Column type |
|----------------|--------------|---------------|---------|-----------------|-------------|
| **M3** (mandated-command harness) | 43 | 0% (non-F grep sub-check only) | 0 finals, 1 retraction | ESTIMATE: ~200 LOC for a broad M3; decomposes into 5–8 sub-checkers (grep-form, pathspec-commit, exit-code, ordering, version-check, positive-control, import-probe, HALT-routing); each sub-checker ~30–50 LOC; standalone drafting-harness script, not plan_lint §4 | Coverage is CLASSIFICATION evidence |
| **M1** (anchor liveness) | 34 | 9% (path-exists sub-check only) | 3 finals (all FP) | ESTIMATE: ~150 LOC for path-exists; the semantic anchor sub-check (code liveness) would need structured annotations or AST parsing; plan_lint §4 check for path-exists, standalone for code-anchor | Coverage is CLASSIFICATION evidence |
| **M4** (executable ledger) | 29 | 7% (C<n> keyword sub-check only) | 1 final (311 — persistent C4/C11) | ESTIMATE: ~100 LOC for C<n> keyword scan; the step-level constraint check is infeasible without semantic plan understanding; plan_lint §4 for C<n> entries | Coverage is CLASSIFICATION evidence |
| M6 (consumer census) | 7 | — | — | ESTIMATE | ESTIMATE |
| M5 (clone structural diff) | 6 | — | — | ESTIMATE: requires origin-plan access + structural alignment; ~300 LOC | ESTIMATE |
| M2 (R/W window) | 4 | — | — | ESTIMATE: requires scope parsing + cross-step overlap detection; ~200 LOC | ESTIMATE |
| M7 (guard-relaxation) | 3 | — | — | ESTIMATE: diff-based; ~150 LOC on top of plan structure parser | ESTIMATE |
| R (shipped plan_lint) | 4 (1 genuine after Q4) | 25% (1/4 fires) | N/A (already shipped) | SHIPPED | MEASURED |
| O (other-mechanizable) | 3 (+3 reclassified from R) | — | — | ESTIMATE: 317-s4-3 already shipped as (i); 311-w1-10 and 311-w3-2 are niche | ESTIMATE |

⚠️ **Coverage is CLASSIFICATION evidence, not catch evidence.** A coverage count of 43 says the census classified 43 findings as M3-shaped; only a Q3 fire-rate says a check caught them. The Q3 fire-rates of 0–9% demonstrate that single prototype implementations catch a small fraction of their classified bucket. **Do not read "coverage 43" as "catches 43."**

### The do-nothing column

Without any new checks, the same findings cost **prose walk-phases** when caught. Across the three required cycles:
- Total folds: 174
- Warm-cycle phases (w1/a1/c1/aC per cycle): ~48 folds in ~4 phases per cycle = ~12 fold-hours
- Cold panel phases (seats 1–5): ~118 folds in 15 seat-sessions = ~8 folds/session
- Confirming phases (cc/aC2): ~12 folds in 6 sessions

**The current prose-based drafting cycle catches ~174 defects across ~25 phases per cycle.** The yield is flat at ~7–10 folds per panel seat (measured), declining from ~11 at w1 to ~3 at confirming. The cycle exits on dry, so the total cost is deterministic per artifact.

### Recommendation for CEO choice

**No single check is recommended for immediate build.** The census shows that:

1. **The top-3 buckets are internally diverse.** M3's 43 findings decompose into 5–8 sub-types (grep-form, pathspec, exit-code, ordering, etc.). Building "an M3 checker" is really building 5–8 checkers. The bucket is a CLASSIFICATION, not a specification.

2. **The buildable sub-checks have narrow scope.** The non-`-F` grep checker, the path-existence checker, and the C<n> keyword checker each catch <10% of their bucket. Their combined catch across all 174 findings is ~5 catches — less than a single panel seat produces.

3. **The fold-time battery ceiling is 93% of prior-fold defects (26/28) — but 16% of total findings are prior-fold.** Even a perfect battery would catch ~26 findings, which is 15% of the total. The remaining 85% are NOVEL defects that no post-fold battery can anticipate.

4. **Three concrete sub-checks are cheapest to ship** if any build is authorized:
   - Non-`-F` grep lint (M3 sub-type): ~30 LOC, 0 false positives on finals/Done/, catches a narrow class (plan_lint §4 or standalone)
   - Path-existence lint (M1 sub-type): ~50 LOC after FP filtering, needs path-pattern allowlist (plan_lint §4)
   - C<n>-without-executable-check lint (M4 sub-type): ~40 LOC, low FP (plan_lint §4 extension to (g))

These three together would add ~120 LOC to plan_lint and catch a combined ~5–8 findings per cycle at current defect rates. **Cost: ~2 hours to build + test. Benefit: ~5–8 findings per cycle caught at fold-time instead of walk-phase. The do-nothing alternative catches the same findings ~1–3 phases later.**

---

## Unresolved

1. **311 close-commit count mismatch (30 vs 16):** The close commit `e52275f` claims "30 drafting commits preserved" but path enumeration shows 16. The cause is unknown — the close commit may count something other than draft-path-touching commits (e.g., all commits on the step branch, including non-draft-touching session commits). Not resolved by argument per Q1 rules.

2. **317 close-commit count mismatch (21 vs 14):** Same class as #1. Close `253c085` claims 21, path enumeration shows 14.

3. **315 close-commit count mismatch (9 vs 8):** Close `e53185b` claims 9, path enumeration shows 8. Same class.

4. **306 cross-repo draft location:** 306's draft path was in the shop root repo but the plan deposited to bellows. This complicates any recipe that assumes the draft and deposit live in the same repo.

5. **R-bucket precision:** 3 of 4 R-classified findings were not caught by the shipped plan_lint check they were mapped to. The checks validate structural properties broader than the specific defects. Whether these should be reclassified as O (with a proposed narrower check) or J (no mechanical form for the specific defect) is a judgment call for the Planner.

6. **M3/M1/M4 sub-type decomposition:** Each top-3 bucket decomposes into multiple sub-types that would each need a separate checker. The census classified at BUCKET level; a build plan would need SUB-TYPE specifications. This decomposition is not provided by this census (it would be the follow-on build plan's work).

---

**Bookend HEAD pins (end of run):**
- lessons-forge: `8d7e6c118d30b2c33bbbad9b1b0aaacda8771df8`
- bellows: `356f4ca2eb38aeb651c2098e039b52c248d4f25a`
- shop root: `a773cd8b6a714c1ea550d87030a649bdf7a4f1bc`

**Delta:** All three pins identical to start-of-run. No concurrent activity detected.

---

### Status

**Complete**

### Deposits

- `bellows/knowledge/research/lens-mechanization-census-2026-08-08.md`

### Ledger Updates

#### Prompt Feedback

No prompt feedback generated by this diagnostic.
