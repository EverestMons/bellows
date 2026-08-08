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
| **(n)** non-`-F` grep lint | M3 sub-type | positive control fired; **0 FP on 3 final plans and 6 Done/ plans**; 1 documented FP class (retraction text narrating a defective grep verbatim) |
| **(o)** path-existence lint | M1 sub-type | naive form was FP-dominated (matched `python3`, `tokens,`); **the 4 real fires were genuine** (320's relative deposit paths) — shippable ONLY with the filtering this plan specifies |
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
> ⚠️⚠️ **Confirm warn-first AT HEAD:** every §4-family check (f)–(l) is a bare print never touching `results`/`all_passed`; return is `0 if all_passed else 1`. **If any has flipped to blocking, HALT — the back-compat reasoning changes.** ⚠️ **Verify the letter set at HEAD:** if a check labeled (m), (n), (o), or (p) already exists (the held sibling or another plan landed in-window), HALT and report — the allocation above needs re-basing, not improvisation.
>
> **Insertion anchor (Rule 22(a) — quoted, not described).** All three checks insert as a block immediately BEFORE this verbatim line (the results-printing loop):
>
> ```python
>     for status, check, detail in results:
> ```
>
> **Verify the anchor exists verbatim BEFORE editing; grep-confirm after that no duplicate check label was introduced.**

**Check (n) — non-`-F` grep on a literal pattern (M3 sub-type, the census prototype's measured shape).** Operate on the fence-stripped text (`clean_text` already exists — reuse it, do not re-strip). Scan inline backtick spans whose content begins with `grep ` or contains `| grep `: if the span carries a quoted pattern containing no regex metacharacters (none of `[](){}|^$*+?\\.`) and no `-F`/`--fixed-strings` flag and no `-E`/`-P`/`-G` flag, WARN naming the span and the ugrep-shim hazard. ⚠️ **Fenced blocks are deliberately excluded — the measured 0-FP load came from the inline-span form; commands inside fences are the documented miss, stated in the code comment.** The retraction-text FP class (a narrated defective grep) is accepted and documented — per-file it reads as a true positive on the file carrying the narration.

**Check (o) — path-existence for input paths (M1 sub-type, shippable only WITH the filters).** Operate on inline backtick spans in `clean_text`. A span is a PATH CANDIDATE only if ALL hold: contains `/`; matches `^[A-Za-z0-9_./-]+$` (no spaces, commas, or the placeholder characters `<>{}$*…`); has ≥2 segments; and either starts with `/Users/` (absolute) or its first segment is one of the repo-conventional roots (`knowledge`, `scripts`, `tests`, `src`, `web`, `engines`, `agents`, `verdicts`, `logs`, `governance`). ⚠️⚠️ **EXCLUDE every path that appears in any `**Deposits:**` or `**Scope:**` block anywhere in the plan (reuse `gates._extract_plan_required_deposits`/`_extract_plan_scope` over the whole text and each step) — deposits do not exist at lint time BY DESIGN, and flagging them would make the check fire on every well-formed plan.** Resolve relative candidates against the repo root found by walking up from the plan file's directory to the first entry named `.git` (file or directory — worktrees have a `.git` file); if no root is found, skip silently with a comment. Absolute candidates are checked directly. WARN per missing path, capped at 10 per plan with a `(+K more)` tail — an unbounded list on a degenerate plan is noise.

**Check (p) — C-ledger entry without an executable check (M4 sub-type, beside (g)).** Inside `dc_block` only (reuse the (f)-built extraction — do not re-extract): for each `**C<n>** —` entry the (g) regex already finds, WARN if the entry's line carries no backtick-quoted command and no `check:` token — the §2.8 record-without-prevent asymmetry, measured 3× in one cycle, argues constraints should carry their re-run. **Zero entries skip silently ((g) precedent). This seeds a convention that does not exist yet — expect it to fire on most existing ledgers; that is warn-first break-in, not noise, and the QA step measures it.**

> **Task D — PROTECT THE EXISTING TESTS (303 form).** Run the existing lint tests before and after; a fixture edit preserves the test's INTENT and is reported explicitly. **Do NOT weaken a check to avoid a test edit.**
>
> **Task E — new observe-the-effect tests, one positive and one negative control per check, each also asserting exit 0.** ⚠️ **Fixtures as string literals at COLUMN 0 (306's self-fire lesson); NO cross-tree plan reads (277's V1).**
> - **(n):** inline ``grep "plain literal" file`` → WARN; ``grep -F "plain literal" file`` → no WARN; ``grep -E "a|b" file`` → no WARN (regex intent); the same defective grep inside a fenced block → no WARN (documented miss, asserted); pattern with metacharacters → no WARN.
> - **(o):** an inline `knowledge/research/does-not-exist-999.md` → WARN; the same path listed in a Deposits block → NO WARN (the exclusion is the test's point); `python3` and `a/b<placeholder>` spans → no WARN (filter); an absolute existing path → no WARN; >10 missing paths → capped output asserted.
> - **(p):** a dc_block C-entry with no backtick command → WARN; with an inline backtick command → no WARN; zero C-entries → silent.
> - **Degenerate:** empty plan, plan with no dc_block, unparseable header → no crash, no false WARN, exit 0.
>
> **Run targeted tests only:** `python3 -m pytest tests/ -k "plan_lint or lint" --tb=short -q 2>&1 | cat`. ⚠️ **Do NOT run the full suite — that is Step 2's job.** Then run `plan_lint` live against one real compliant plan and one deliberately-tripping fixture; **paste RAW output and `echo $?` = 0 on each.**
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

⚠️⚠️ **THE FALSE-POSITIVE MEASUREMENT IS THE POINT.** The census's loads (0 FP for (n); FP-dominated-unless-filtered for (o); ~1 FP for (p)'s class) are hypotheses; this step produces the real numbers, and **(o)'s number decides whether its filters worked — if (o) fires on well-formed deposit declarations anywhere, the filter failed its design goal and that is a HALT-and-report, not a shrug.**

> **Task Q0 — RE-PIN (303 C4).** (1) `git -C /Users/marklehn/Developer/GitHub/bellows log -1 --oneline -- scripts/plan_lint.py tests/test_plan_lint.py` — the newest commit touching either must be Step 1's; a foreign commit → **HALT.** (2) `git -C <root> rev-parse HEAD` for each of the five corpus roots, recorded verbatim beside every count.

1. **Full bellows suite** → `knowledge/qa/full-suite.txt` (RAW, ≥ last 200 lines incl. the summary line — never a summary).
2. **Targeted lint tests re-run** → `knowledge/qa/targeted-tests.txt` (RAW; this command is this file's producer).
3. **Corpus sweep:** run `plan_lint` against every plan in all five `Done/` trees, addressed ABSOLUTELY — `/Users/marklehn/Developer/GitHub/{anvil,bellows,governance,invoice-pulse,lessons-forge}/knowledge/decisions/Done/` → `knowledge/qa/corpus-sweep.txt`. Report **per check (n)/(o)/(p), per root, including zeros**, each beside its pin: fire count + plan ids. **Measured numbers with the producing command — this plan predicts no figure.** For (o) additionally: every fire classified true/false positive by a one-line reason — **the FP RATE is the deliverable, not the count.**
4. **WARN-only by MECHANISM:** grep the three new checks — none appends to `results`, none assigns `all_passed`; then `echo $?` = 0 on a fixture tripping all three. **Both, not just the second.**
5. **QA Receipt with the canonical Rule 20 self-check block**, one verification row per item above.
   - `required_evidence_files`: `[targeted-tests.txt, full-suite.txt, corpus-sweep.txt]`
   - ⚠️ Deposit all three BEFORE running the block — it `sys.exit(1)`s if any is missing or empty.
   - ⚠️⚠️ **Literal stdout; banner + PASSED line BYTE-EXACT (em-dash U+2014). FAILED → HALT.**

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

**Walks:** none yet — v0 draft; no lens has run. Phases one per turn under CEO direction; ACID apart; cold panel (T2) after a dry walk or judged stop.

- Weak spots:          not run.
- Destruction:         not run.
- Vulnerabilities:     not run.
- Integration-record:  not run.
- ACID:                not run.

**Panel status:** not convened (v0).

**Conflicts:** none yet. Constraints append at the END as earned, never inserted above an existing entry.

**Closing:** NOT REACHED — v0 draft; no lens has read this artifact.
