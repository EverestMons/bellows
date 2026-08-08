# Executable: the diag-322 sub-check trio — non-`-F` grep lint (n), path-existence lint (o), C-ledger-without-check lint (p)

**Type:** Executable
**Project:** bellows
**Depends on:** **diagnostic-322** (Done, bellows — the lens-mechanization census; CEO decision 2026-08-08: ship its recommendation-4 trio). Its deposit `knowledge/research/lens-mechanization-census-2026-08-08.md` carries the measured false-positive loads this plan's QA re-verifies. ⚠️ **Census figures cited below are AUTHORING-TIME hypotheses with a verify clause — re-measure at QA, never inherit** (4/4 predicted numbers wrong in one recorded session).
**Created:** 2026-08-08
**Author:** Planner
**dispatch_mode:** bellows
**pause_for_verdict:** always
**qa_steps:** [2]
**Priority:** 10
**cycle_tier:** T2

⚠️ **ID NOTE — the deposit filename is decided AT DEPOSIT.** Bellows mints the id from `id_sequence` at claim and does not parse the filename. **Re-read `id_sequence` at deposit** (drift fired live twice this week: 310→311, and 321 consumed in-window by a parallel terminal on 2026-08-08).

⚠️ **pause_for_verdict is `always`, DELIBERATELY** — this plan edits `plan_lint`, a gate surface; the 317-measured `files_changed=[]` blind spot argues for a human read at the DEV gate on this plan class (same judgment as the held sibling).

---

## Why this exists — the only build diag-322's numbers support

The census classified 174 findings from three preserved T2 cycles and fired prototypes at their real pre-fold states. Its central negative result: the big buckets are classification taxa, not check specifications — no broad "lens harness" is licensed. **What IS licensed: three narrow sub-checks whose prototypes showed usable precision, ~120 LOC combined, each catching a measured recurring class:**

| check | class | census evidence (hypotheses to re-verify at QA) |
|---|---|---|
| **(n)** non-`-F` grep lint | M3 sub-type | positive control fired; **0 FP on 3 final plans and 6 Done/ plans — measured on the prototype's NARROWER no-dot form; this plan's dot-widening has an UNMEASURED load until QA item 3 produces it**; 1 documented FP class (retraction text narrating a defective grep verbatim) |
| **(o)** path-existence lint | M1 sub-type | naive form was FP-dominated (matched `python3`, `tokens,`); **the genuine fires were 3+2 across two 320 pre-fold states, 0 FP at those sites** (relative deposit paths) — shippable ONLY with the filtering this plan specifies |
| **(p)** C-ledger-entry-without-executable-check lint | M4 sub-type | 1 FP on finals (311's persistent constraints); seeds the §2.8 "mechanize the constraint" convention warn-first |

**Letter allocation, stated to prevent a 304/317-class collision:** shipped checks end at (l); **the letter (m) is RESERVED by the held rows-25/27/28 batch (expected-lint declaration)** — this plan takes **(n), (o), (p)**. If the held batch has landed by the time this runs, nothing changes; if it lands after, its (m) is unclaimed and waiting.

⚠️ **Coordination with the held sibling, stated:** both plans edit `scripts/plan_lint.py` + `tests/test_plan_lint.py`. They MUST run sequentially, and whichever runs second re-derives every anchor at DEV time (Task A0's verbatim-anchor verification covers this — a moved anchor is a HALT-and-report, not a guess).

---

## How to Run This Plan

**Bootstrap prompt:**
```
Read the plan at knowledge/decisions/in-progress-executable-<id>.md (the daemon renames the deposited placeholder on claim). Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation.
```

⚠️ **Machinery cloned from `executable-303` (the shipped 3-WARN-checks-plus-corpus-sweep class origin), diffed at authoring against `executable-306` (newest same-class: column-0 fixtures, evidence-file producers, PYTHONPATH import notes) and the census's own prototype findings (which ARE the spec's empirical base).**

---
---

## STEP 1 — DEV

> **FIRST — post a short visible chat message (1–2 sentences) confirming you are starting this plan and your immediate next action.** Do NOT rename this plan file. Read your Bellows Developer specialist file, then `scripts/plan_lint.py` in full, then the census deposit `knowledge/research/lens-mechanization-census-2026-08-08.md` §Q3 and §Q6-recommendation-4 (the empirical spec base). **All commands run from `/Users/marklehn/Developer/GitHub/bellows`.**
>
> **Mechanical-only invariant (140/303/306).** All three checks are **WARN-only advisory**: bare `print(...)` lines that must NEVER append to `results`, set `all_passed`, change the return code, or raise. **A malformed or absent block skips with no exception.**
>
> **Task A0 — pre-edit cleanliness + warn-first precondition (303 form).** `git -C /Users/marklehn/Developer/GitHub/bellows status --porcelain -- scripts/plan_lint.py tests/test_plan_lint.py` must be empty. If DIRTY — resume disambiguation (Rule 56): grep for THIS plan's own edits (the `(n)`/`(o)`/`(p)` check comments, the new test names); all attributable → `git restore` both and reapply from scratch; any unattributable hunk → **HALT.**
> ⚠️⚠️ **Confirm warn-first AT HEAD:** every §4-family check (f)–(l) is a bare print never touching `results`/`all_passed`; return is `0 if all_passed else 1`. **If any has flipped to blocking, HALT — the back-compat reasoning changes.** ⚠️ **Verify the letter set at HEAD, with the two cases SPLIT:** a check labeled **(n), (o), or (p)** already existing → **HALT and report** (a genuine collision — the allocation needs re-basing, not improvisation). A check labeled **(m)** existing alone → **the held sibling landed as planned; note it in the dev log and PROCEED** — (m) was reserved for it and the trio's letters remain free (an undifferentiated halt here would be spurious).
>
> **Insertion anchor (Rule 22(a) — quoted, not described).** All three checks insert as a block immediately BEFORE this verbatim line (the results-printing loop):
>
> ```python
>     for status, check, detail in results:
> ```
>
> **Verify the anchor exists verbatim BEFORE editing; grep-confirm after that no duplicate check label was introduced.**

**Check (n) — non-`-F` grep on a literal pattern (M3 sub-type, the census prototype's measured shape, ONE deliberate widening).** Operate on the fence-stripped text (`clean_text` already exists — reuse it, do not re-strip). Scan inline backtick spans whose content begins with `grep ` or contains `| grep `: if the span carries a quoted pattern (single or double quotes, both stated in the code) containing no regex metacharacters **other than `.`** (none of `[](){}|^$*+?\\`; ⚠️ **a pattern whose only metacharacter is `.` — `plan_lint.py`, `foo.md` — is a LITERAL-intent search and stays a candidate: filename dots are the dominant literal class, and exempting `.` would exempt most real hazards, a plausible contributor to the census prototype's 0/43**) and no `-F`/`--fixed-strings` flag and no `-E`/`-P`/`-G` flag, WARN naming the span and the ugrep-shim hazard. ⚠️ **Two documented misses, both stated in the code comment: fenced blocks are deliberately excluded (the measured 0-FP load came from the inline-span form), and UNQUOTED patterns (`grep -c foo file`) are not candidates — the quoted form is the census prototype's measured shape and the unquoted class stays a stated miss, not a silent one.** The retraction-text FP class (a narrated defective grep) is accepted and documented — per-file it reads as a true positive on the file carrying the narration.

**Check (o) — path-existence for input paths (M1 sub-type, shippable only WITH the filters).** Operate on inline backtick spans in `clean_text`. A span is a PATH CANDIDATE only if ALL hold: contains `/`; matches `^[A-Za-z0-9_./-]+$` (no spaces, commas, or the placeholder characters `<>{}$*…`); has ≥2 segments; and either starts with `/Users/` (absolute) or its first segment is one of the repo-conventional roots (`knowledge`, `scripts`, `tests`, `src`, `web`, `engines`, `agents`, `verdicts`, `logs`, `governance`). ⚠️⚠️ **EXCLUDE every path that appears in any `**Deposits:**` or `**Scope:**` block anywhere in the plan (reuse `gates._extract_plan_required_deposits`/`_extract_plan_scope` over the whole text and each step) — deposits do not exist at lint time BY DESIGN, and flagging them would make the check fire on every well-formed plan.** Resolve relative candidates against the PROJECT root derived from the plan file's own path: **split at `/knowledge/` — every deposited plan lives under `<project>/knowledge/decisions/`, and this is what makes governance plans resolve against `<root>/governance/`, not the shop root** (a `.git` walk-up alone would mis-root every governance plan in the corpus sweep — governance has no `.git`); fall back to the `.git` walk-up (file or directory — worktrees have a `.git` file) when the path carries no `/knowledge/`; if neither yields a root, skip silently with a comment. **Resolution is DUAL-ROOT: check the derived project root first, then the fixed shop root `/Users/marklehn/Developer/GitHub` — WARN only when missing at BOTH.** A bellows plan citing `governance/knowledge/…` relatively is real corpus behaviour, and for a WARN-only check the deliberate error direction is under-fire, stated in the code comment. Absolute candidates are checked directly. Candidates with an empty segment (`a//b`) are rejected; fired paths are DEDUPED before reporting. WARN per missing path, capped at 10 per plan with a `(+K more)` tail — an unbounded list on a degenerate plan is noise.

**Check (p) — C-ledger entry without an executable check (M4 sub-type, beside (g)).** Inside `dc_block` only (reuse the (f)-built extraction — do not re-extract): for each `**C<n>** —` entry the (g) regex already finds, WARN if the entry's scanned span — **from the match start to the end of that line, stated so multi-line entries are a known partial scan, not an accident** — carries no backtick-quoted command and no `check:` token — the §2.8 record-without-prevent asymmetry, measured 3× in one cycle, argues constraints should carry their re-run. **Zero entries skip silently ((g) precedent). This seeds a convention that does not exist yet — expect it to fire on most existing ledgers; that is warn-first break-in, not noise, and the QA step measures it. ⚠️ FORWARD-LOOKING ONLY: the corpus fire count is BASELINE DATA — it is not a retrofit work queue, and no plan is licensed to sweep historical `Done/` ledgers into the new convention on this check's authority.**

> **Task D — PROTECT THE EXISTING TESTS (303 form).** Run the existing lint tests before and after; a fixture edit preserves the test's INTENT and is reported explicitly. **Do NOT weaken a check to avoid a test edit.**
>
> **Task E — new observe-the-effect tests, one positive and one negative control per check, each also asserting exit 0.** ⚠️ **Fixtures as string literals at COLUMN 0 (306's self-fire lesson); NO cross-tree plan reads (277's V1).**
> - **(n):** inline ``grep "plain literal" file`` → WARN; ``grep "foo.py" file`` → **WARN (the dot-only literal class — the deliberate widening's own fixture)**; ``grep -F "plain literal" file`` → no WARN; ``grep -E "a|b" file`` → no WARN (regex intent); the same defective grep inside a fenced block → no WARN (documented miss, asserted); pattern with non-dot metacharacters → no WARN.
> - **(o):** ⚠️⚠️ **FIXTURE PLACEMENT IS THE TEST'S FOUNDATION: (o) fixtures live under a SYNTHETIC project tree — `<tmpdir>/proj/knowledge/decisions/fixture.md` with candidate paths rooted in `<tmpdir>/proj/` — because a bare-tmp fixture has no `/knowledge/` and no `.git`, root-derivation SKIPS, and every (o) assertion would pass vacuously while testing NOTHING.** Then: an inline missing path under the synthetic root → WARN; the same path listed in a Deposits block → NO WARN (the exclusion is the test's point); `python3` and `a/b<placeholder>` spans → no WARN (filter); an existing path → no WARN; a bare-tmp fixture → NO (o) output at all (the skip path, asserted as its own test); >10 missing paths → capped `(+K more)` output asserted; duplicate missing path → reported once.
> - **(p):** a dc_block C-entry with no backtick command → WARN; with an inline backtick command → no WARN; zero C-entries → silent.
> - **Degenerate:** empty plan, plan with no dc_block, unparseable header → no crash, no false WARN, exit 0.
>
> **Run targeted tests only:** `python3 -m pytest tests/ -k "plan_lint or lint" --tb=short -q 2>&1 | cat`. ⚠️ **Do NOT run the full suite — that is Step 2's job.** Then run `plan_lint` live against one real compliant plan and one deliberately-tripping fixture — **the fixture must trip ALL THREE checks in one run, and the pasted RAW output must show each of the (n)/(o)/(p) WARN lines plus `echo $?` = 0.**
>
> **Scope:**
> - `scripts/plan_lint.py`
> - `tests/test_plan_lint.py`
> - `knowledge/development/lint-subcheck-trio-dev-log-2026-08-08.md`
>
> **Deposit the dev log** with before/after per check, the warn-first confirmation, every fixture edit, and the RAW targeted-test + live-run output. **Canonical Python/MCP file-write — NO heredoc. Commit all (NO push).** `#### Prompt Feedback` in `### Ledger Updates`.
>
> **STOP. Do NOT proceed to Step 2. Wait for CEO verdict.**

**Deposits:**
- `bellows/scripts/plan_lint.py`
- `bellows/tests/test_plan_lint.py`
- `bellows/knowledge/development/lint-subcheck-trio-dev-log-2026-08-08.md`

---
---

## STEP 2 — QA

⚠️⚠️ **THE FALSE-POSITIVE MEASUREMENT IS THE POINT.** The census's loads (0 FP for (n); FP-dominated-unless-filtered for (o); ~1 FP for (p)'s class) are hypotheses; this step produces the real numbers, and **(o)'s number decides whether its filters worked. The HALT trigger is MECHANICAL, not narrative: if any (o)-fired path string ALSO appears in a `**Deposits:**` or `**Scope:**` block of the same plan, the exclusion failed its design goal → HALT and report. The one-line TP/FP classification is context for the CEO, never a substitute for this test — a fire cannot be narrated out of the HALT.**

> **Task Q0 — RE-PIN (303 C4).** (1) `git -C /Users/marklehn/Developer/GitHub/bellows log -1 --oneline -- scripts/plan_lint.py tests/test_plan_lint.py` — the newest commit touching either must be Step 1's; a foreign commit → **HALT.** (2) `git -C <root> rev-parse HEAD` for each of the five corpus roots, recorded verbatim beside every count.

1. **Full bellows suite** → `knowledge/qa/full-suite.txt` (RAW, ≥ last 200 lines incl. the summary line — never a summary).
2. **Targeted lint tests re-run** → `knowledge/qa/targeted-tests.txt` (RAW; this command is this file's producer).
3. **Corpus sweep:** run `plan_lint` against every plan in all five `Done/` trees, addressed ABSOLUTELY — `/Users/marklehn/Developer/GitHub/{anvil,bellows,governance,invoice-pulse,lessons-forge}/knowledge/decisions/Done/` → `knowledge/qa/corpus-sweep.txt`. **BOOKEND the sweep: re-run all five `rev-parse HEAD` pins immediately after it and report both sets — a delta is concurrent activity (a parallel terminal is live this week), named in the report and never reconciled by force.** Report **per check (n)/(o)/(p), per root, including zeros**, each beside its pin: fire count + plan ids. **Measured numbers with the producing command — this plan predicts no figure.** For (o) additionally: every fire classified true/false positive by a one-line reason — **the FP RATE is the deliverable, not the count.**
4. **WARN-only by MECHANISM:** grep the three new checks — none appends to `results`, none assigns `all_passed`; then `echo $?` = 0 on a fixture tripping all three. **Both, not just the second.**
5. **QA Receipt with the canonical Rule 20 self-check block**, one verification row per item above.
   - `required_evidence_files`: `[targeted-tests.txt, full-suite.txt, corpus-sweep.txt]`
   - ⚠️ Deposit all three BEFORE running the block — it `sys.exit(1)`s if any is missing or empty.
   - ⚠️⚠️ **Include the block's literal stdout. The banner `Rule 20 — QA Self-Check Results` and the `PASSED — SELF-CHECK PASSED` line must appear BYTE-EXACT (em-dash U+2014). If it prints FAILED, HALT.**

> **Scope:**
> - `knowledge/qa/lint-subcheck-trio-qa-report-2026-08-08.md`
> - `knowledge/qa/targeted-tests.txt`
> - `knowledge/qa/full-suite.txt`
> - `knowledge/qa/corpus-sweep.txt`

**Deposits:**
- `bellows/knowledge/qa/lint-subcheck-trio-qa-report-2026-08-08.md`
- `bellows/knowledge/qa/targeted-tests.txt`
- `bellows/knowledge/qa/full-suite.txt`
- `bellows/knowledge/qa/corpus-sweep.txt`

### Output Receipt (Step 2, terminal)

Close with `### Status` (**Complete**), `### Deposits`, `### Ledger Updates` with **`#### Forward Register`: the word NONE** (the census's close-count/reconciliation candidates stay unqueued pending CEO — do not emit them from here) and **`#### Prompt Feedback`**.

**STOP. Terminal step. Wait for CEO verdict.**

---

## Method + boundaries

- ⚠️ **`plan_lint` is a GATE. Purely additive: no existing check — (a)–(l), the unnumbered WARNs — changes behaviour, wording, or status. If a new check cannot land without touching one, HALT and report.**
- **No-output-consumer premise re-verified at authoring (2026-08-08, with a positive control):** no daemon module (`gates.py`, `runner.py`, `validators.py`, `bellows.py`) references `plan_lint`; the only out-of-tree mentions are fixture strings in `tests/test_gates.py`. New WARN lines therefore cannot break a consumer — re-verify at DEV if the claim is load-bearing to any decision there.
- ⚠️⚠️ **HALF-COMPLETE STATE, STATED:** Step 1 without Step 2 leaves three unmeasured WARN-only checks live in the gate — acceptable solely because they cannot block a deposit or change an exit code; if any is ever made blocking, the measurement precedes the flip.
- **Doc-sync deferral, stated:** (p) seeds a §2.8 convention and (n)/(o) mechanize §2.7 sub-rules none of which DRAFTING_CYCLE.md yet names as gate-backed — the governance edit rides the corpus path (198→v1.2 precedent), NOT this plan.
- **Absolute paths:** `/Users/marklehn/Developer/GitHub/bellows/scripts/plan_lint.py`, `/Users/marklehn/Developer/GitHub/bellows/tests/test_plan_lint.py`.
- ⚠️ **`grep -F` mandatory for literals** (ugrep shim — the very hazard check (n) mechanizes).
- ⚠️ **Agents run `git add` and `git commit` only. No push.**
- Where a step cannot be completed as written, **HALT and report** — never substitute a narrower change.

---

## Drafting Cycle

**This section is a RECORD, not instructions.** Gate-matching strings are described here, never quoted.

**Tier:** T2 — computed: **T-6 fires** (`plan_lint` IS a gate; editing it is a governance-surface edit by §1's definition, the 303/306 precedent) and **T-1 fires** (source plus tests). **T-7 consumed:** authored from diagnostic-322, whose findings carry re-verification clauses here rather than inheritance. Clone framing: structure-for-structure from `executable-303`; newest same-class shipped `executable-306`; **clone framing is not licence to down-tier (§2.6) — the cold panel obligation stands.**

**Expected lint:** NOT FINAL — set at the §5 conformance pass; the closing-fold WARN is expected to be EARNED only if the panel ends judged-stop rather than dry.

**Walks:** 1 (four lenses complete + a1 apart), each phase its own turn under CEO direction, per-phase committed; cold panel (T2) owed after a dry walk or judged stop. ⚠️ This header lagged the lenses once (still read "no lens has run" at a1's record read) — the same record-decay class measured 3× in the census cycle; caught here by the pass that exists to catch it.

- Weak spots:          w1 4 folded (1.1 the `.`-exemption defect in (n) — dot-only patterns are the dominant literal class, now candidates with their own fixture; 1.1 (o) project-root by /knowledge/-split primary — the .git walk-up alone mis-roots every governance plan; 1.3 (p) scanned span defined to end-of-line, partial scan stated; census (o)-row figure precision 3+2-across-two-states).
- Destruction:         w1 4 folded (2.2/watering: (o)'s QA HALT made MECHANICAL — fired-path ∈ same plan's Deposits/Scope strings, un-narratable; (n)'s unquoted-pattern miss stated not silent; (p) marked forward-looking — corpus fires are baseline, not a retrofit queue; 2.1 no-output-consumer premise re-verified at HEAD w/ positive control, recorded in Method).
- Vulnerabilities:     w1 4 folded (3.3 the vacuous-(o)-test trap — fixtures require a synthetic `<tmpdir>/proj/knowledge/` tree, bare-tmp asserts the skip path as its own test; 3.1 dual-root resolution — project root then shop root, WARN only when missing at both, under-fire as the stated error direction; live tripping fixture must show all three WARN classes in one pasted run; 3.4 precision trio — both quote styles in (n), empty-segment rejection + dedupe-before-cap in (o)).
- Integration-record:  w1 3 folded, all confirmed by EXECUTING the lint on this draft (4.1 MATERIAL: the Rule 20 banner pair was described-not-quoted in STEP 2 — check (c) FAILed live; the 317-v0 precedent exactly, and a self-clone-drift datum since the held sibling carries the pair; 4.1 the Closing's stale "no lens has read" caught by SHIPPED check (h) — a live true positive from 303's mechanization; panel line moved to canonical `Cold panel` form after the line-anchored check WARNed on the `Panel status:` label — the row-27 class in this plan's own draft).
- ACID:                a1 4 folded, apart (5.3 LOADED for the two-step schedule: corpus sweep gains a post-sweep re-pin bookend — the parallel terminal is live this week; 5.2 the (n) Why-row overstated the census 0-FP as covering the dot-widened form — annotated UNMEASURED-until-QA; 5.2 the A0 letter check over-triggered — (m)-exists now proceeds with a note, only (n)/(o)/(p)-exists HALTs; record read caught the Walks-header lag, the recurring class).

**Cold panel (T2):** not convened — owed after a dry walk or judged stop; the line sits in canonical form so the line-anchored check reads it (this draft's own v0 used a non-canonical `Panel status:` label and the shipped check caught it — the row-27 class, live in the plan shipping that row's siblings).

**Conflicts:** none yet. Constraints append at the END as earned, never inserted above an existing entry.

**Closing:** NOT REACHED — walk 1 complete (four lenses + a1 apart), 19 folds landed. a1 folded, so a confirming pass is owed; the cycle closes only when a confirming pass returns dry with the last event a lens pass, and the cold panel is owed either way (T2).
