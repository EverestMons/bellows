# bellows — THE LESSONS GUARD PARKS A CLASS-HELD DEPOSIT: `tools/lessons_guard.py` reads a `hold-` file's sidecar and treats `hold_reason: class:<name>` as PARKED (the CEO's release is owed, not a run), while a `hold-` with no sidecar or any other reason keeps freezing; the pin's line counts the parked holds; the wrap skill's guard sentence names the case (thread 278, CEO ruling 2026-09-11)

**Date:** 2026-09-11 | **Project:** bellows | **Tier:** Small (one predicate change in one tool, one test file extended, one sentence in the wrap skill, one mutation manifest, one dev-log) | **Dispatch Mode:** bellows | **Test Scope:** full-suite (Rule 21 — the guard is imported by the wrap hooks' tests; `pytest tests/ -q`) | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** after_qa_step | **known_failures:** 0 | **Discharges:** thread 278 | **cycle_tier:** T1

**auto_close:** false

**Post-close:** no restart (the guard is a tool the Planner runs, not daemon-loaded); the doctrine half is the CEO's — STANDING_CONSTRAINTS v1.1's rider on line 9, applied as a one-command act beside this plan (the ruling is made; the rider is the record). The LESSONS 2026-09-09 entry gains its RIDER at the next wrap's sweep.

**Depends on:** the CEO's ruling of 2026-09-11 on thread 278: a class-held deposit made under a stated CEO delegation does NOT freeze the lessons guard — measured the night before, when 261's `hold-` file (class shop-infra, releases withheld until morning) froze the guard at the wrap and STANDING_CONSTRAINTS line 9 withdrew the deposit for one extra morning act. Clone origin by kind and layout: `Done/executable-100073.md` (a tool and its tests, two-commit DEV, the mutation run redirected, the QA that runs the tool on a copy).

**Tier computed (§1):** **T1** — T-1 fires (the guard every wrap runs); T-6 does not (the rider is the CEO's separate act); T-2 does not (no data, no schema).

## CEO Context

The guard's freeze predicate is a name test: `_FREEZING_RE` (P1) matches `hold-`, `ready-`, `in-progress-` and `verdict-pending-` cycle plans, and `_PARKED_PREFIXES` exempts `halted-`, `parked-` and `obsolete-` by name. A class hold is not a name the predicate can read — it is the sidecar's `hold_reason` (P2), written by the depositor beside the `hold-` file — so a plan you have already agreed to release freezes the corpus exactly as an un-run cycle would. Your ruling draws the line at the reason: `class:<name>` is a plan awaiting your act, parked; every other hold (`stale-checkout`, `empty_writes`, a collision, `held_pending_ceo_release`) stays a freeze, because those are plans whose next act is not a release. The change is one branch in `freezing_plans`, a count on the pin's line so the operator sees what was parked, and one sentence in the wrap skill that lists the parked prefixes today.

## What this changes

1. **`tools/lessons_guard.py`** — `freezing_plans(root)` gains, for a file whose name starts with `hold-` (after the optional `parallel-N-`), a sidecar read: `<same path with .md → .hold.json>` (the depositor's rule, P2); if the sidecar exists, parses as JSON, and its `hold_reason` is a string starting with `class:`, the file is PARKED. The walk lives once, in a private `_scan(root) -> tuple[list[Path], list[Path]]` (freezing, parked-by-class); `freezing_plans(root) -> list[Path]` keeps its signature and returns the first, a new `parked_class_holds(root) -> list[Path]` returns the second — no module-level state, no caller changes; a missing sidecar, unreadable JSON, or any other reason leaves the file FREEZING as today. `pin` and `verify` print `class-held: N` on their `lanes:` line (`lanes: 12  frozen: no  class-held: 1`), and `_report_frozen`'s list still names only the freezing files. Nothing else in the tool moves.
2. **`tests/test_lessons_guard.py`** — the parametrized table (`:56–75`, sixteen rows) becomes a table with sidecars: the `_shop` helper accepts `sidecars={name: dict}` and writes each as `<name minus .md>.hold.json`; new rows: (t-a) `hold-executable-100031.md` with sidecar `{"hold_reason": "class:shop-infra", "held_at": …, "class_assigned": "shop-infra"}` → does NOT freeze; (t-b) the same with `hold_reason: "stale-checkout"` → freezes; (t-c) with `hold_reason: "held_pending_ceo_release"` → freezes; (t-d) no sidecar → freezes (the row that exists today, kept); (t-e) a sidecar that is not JSON → freezes; (t-f) `parallel-2-hold-executable-x.md` with a class sidecar → does not freeze; plus (t-g) `parked_class_holds` returns exactly the class-held paths; (t-h) `pin` on a shop with one class hold prints `class-held: 1` and exits 0; (t-i) `pin` on a shop with one class hold AND one `stale-checkout` hold refuses (exit 2) and its FROZEN list names only the stale one.
3. **`hooks/commands/wrap.md`** — the guard paragraph's sentence "it treats `halted-`/`parked-` as PARKED (they do not freeze) while `in-progress-` and `verdict-pending-` DO" gains: "and, since bellows #<this plan> (thread 278), a `hold-` deposit whose sidecar says `hold_reason: class:…` — a plan awaiting the CEO's release".
4. **`knowledge/mutants/guard-class-hold-parked.json`** — three mutants: (m1) the `startswith("class:")` test removed (every sidecar-bearing hold parked) → t-b; (m2) the sidecar read removed (a class hold freezes as today) → t-a; (m3) a missing sidecar treated as parked → t-d.
5. **Not changed:** the depositor, the sidecar's shape, `clear_plan.py`, the freeze rule for every other prefix, the forge's ingest.

## Why this exists

The guard is the only mechanical check on the lessons corpus's write window, and it must keep refusing on an un-run cycle. A class hold is not an un-run cycle in the sense the window protects against: nothing about it can move the lessons; only your release can move it. Reading the reason lets the guard keep its refusal for everything else.

## What this does NOT do

- Change what the guard freezes on for `ready-`, `in-progress-`, `verdict-pending-`, or any `hold-` whose reason is not a class.
- Edit STANDING_CONSTRAINTS (the CEO's act) or LESSONS (the wrap's sweep).
- Touch the depositor or the sidecar's fields.

## MUST-PRESERVE

- ⛔ **Fail-closed on the sidecar:** no file, no JSON, no `hold_reason`, a `hold_reason` that is not a string, or a reason that is not `class:…` → the hold FREEZES, as today (t-b, t-c, t-d, t-e; the test is `isinstance(reason, str) and reason.startswith("class:")`).
- ⛔ **Every existing table row keeps its verdict** — the sixteen rows at `:56–75` run unchanged beside the new ones.
- ⛔ **The wrap skill's sentence is one clause**, not a rewrite; the file's other paragraphs are untouched (`git diff --numstat` shows one line changed).
- ⛔ **Every `expect_fail` is a class-qualified node id where the test is a method**; the mutation run is redirected into its deposit, never piped.
- ⛔ **The thread-262 stop** (PT v4.108 §8).

## Numbers discipline — measured 2026-09-11 by the Planner (bellows `2e3d600`, governance `d64d315d`)

| # | pin | value | how to re-derive |
|---|---|---|---|
| P1 | ⛔ the guard's predicate | `tools/lessons_guard.py` (165 lines): `_KIND` `:44`; `_FREEZING_RE` `:53–55` `^(?:parallel-\d+-)?(?:hold-\|ready-\|in-progress-\|verdict-pending-)?(?:executable\|diagnostic\|qa)-.*\.md$`; `_PARKED_PREFIXES = ("halted-", "parked-", "obsolete-")` `:59`; `freezing_plans(root)` `:84–98` (a `startswith(_PARKED_PREFIXES)` skip, then the regex); `_report_frozen` `:114–123`; `pin` prints `lanes: N  frozen: no` (`:148`) and `verify` `lanes: N  frozen: no  sha: unchanged — safe to write NOW` (`:160`); `shop_root()` `:62` and `decision_lanes()` `:73` — 12 lanes on the mini (`pin` output) | `sed -n 40,100p tools/lessons_guard.py` |
| P2 | ⛔ the sidecar | the depositor names it `"hold-" + claimable_name.replace(".md", ".hold.json")` (`depositor.py:847`) — the `.md` replaced, same directory; its fields `hold_reason`, `held_at`, `class_assigned` (this morning's `hold-executable-bellows-scope-step-warn.hold.json`: `{"hold_reason": "class:shop-infra", "held_at": "2026-09-11T…", "class_assigned": "shop-infra"}`); the reasons the depositor writes: `class:<name>`, `empty_writes` (`:232`), a collision's reason (`:243`), `held_pending_ceo_release` (`:245`), and the claim's `stale-checkout` (bellows plan 100050); `tools/clear_plan.py:55` reads it as `os.path.splitext(hold_path)[0] + ".hold.json"` | `grep -n 'hold.json\|hold_reason' depositor.py tools/clear_plan.py` |
| P3 | ⛔ the tests | `tests/test_lessons_guard.py` (146 lines, 7 tests): `_shop(tmp_path, lane_files=[…])` builds a shop with one lane; the parametrized table `:56–75` (sixteen rows: `hold-executable-100031.md` → True today); `test_pin_refuses_when_frozen` `:101`, `test_verify_*` `:109–140` | the file |
| P4 | ⛔ the measured instance | 2026-09-11 00:5x: `hold-executable-bellows-step-status-transition.md` (class shop-infra, the overnight delegation withheld releases) → `pin` FROZEN → withdrawn under STANDING_CONSTRAINTS line 9 → redeposited by the CEO at 08:00 → released → #100073 Done; one extra CEO act for nothing the guard protects | the 28th and 29th baton blocks; thread 278's body |
| P5 | ⛔ the wrap skill's sentence | `hooks/commands/wrap.md:76` "…names, and it treats `halted-`/`parked-` as PARKED (they do not freeze) while `in-progress-` and `verdict-pending-` DO." | `sed -n 76p hooks/commands/wrap.md` |
| P6 | in-flight; class; interpreter | queue empty at drafting (daemon pid 95212, four lanes); writes: `tools/lessons_guard.py`, `tests/test_lessons_guard.py`, `hooks/commands/wrap.md`, the manifest, run file, dev-log, two QA evidence files → **shop-infra** (`_assign_class`, walk 0) — HOLDS at admission, the CEO releases (the guard then reads its own case at the next wrap); Python 3.9.6, the bellows venv | `python3 status.py`; `_assign_class` |

## Drafting Cycle

**Tier:** **T1** — T-1 fires. **Walk register:** /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-guard-class-hold-parked-2026-09-11.md
**Walks:** walk 0 pinned (P1–P6 measured on bellows `2e3d600`; clone-diff against `Done/executable-100073.md` run: FACTS, ARTEFACTS, STRUCTURE); `fold_check --save-baseline` ARMED on v0 before any fold; re-saved after every intended edit; every lens commit through `scripts/lens_commit.py`; the tool run bare, its exit read; no lens or walk number in any `--desc`; `lens_order_check` after every walk.

- Weak spots:          w1 2 folded — instruction 2 / record 0; w2 dry
- Destruction:         w1 dry; w2 dry
- Vulnerabilities:     w1 1 folded — instruction 1 / record 0; w2 dry
- Integration-record:  w1 dry; w2 dry
- ACID:                w1 dry; w2 dry
**Closing:** WARM close after walk 2 — BAR MET (T1), thread 278's tool half after the CEO's ruling. Two walks: 3 → 0 (walk 1 gave the scan one shape with two readers, narrowed the QA's lane copy to the hold files, and made a non-string reason fail closed; walk 2 dry on every lens). Every lens commit through `lens_commit.py`, the tool run bare, its exit read; the close through `close_cycle.py`; the first pass of walk 1 reset and replayed before any push (the register's record note). Deposit via `ready-`; HOLDS on class shop-infra, the CEO releases — and the guard then reads this plan's own hold as its first live case; STANDING_CONSTRAINTS v1.1's rider is the CEO's parallel act.

## Cycle Manifest
tier: T1
target: tools/lessons_guard.py
class: shop-infra
reads: tools/lessons_guard.py, tests/test_lessons_guard.py, depositor.py, tools/clear_plan.py, hooks/commands/wrap.md, knowledge/decisions/Done/executable-100073.md
writes: tools/lessons_guard.py, tests/test_lessons_guard.py, hooks/commands/wrap.md, knowledge/mutants/guard-class-hold-parked.json, knowledge/mutants/guard-class-hold-parked.run.txt, knowledge/development/dev-log-guard-class-hold-parked-2026-09-11.md, knowledge/qa/evidence/guard-class-hold-parked-qa-receipt-2026-09-11.md, knowledge/qa/evidence/guard-class-hold-parked-suite-2026-09-11.txt
mutants: knowledge/mutants/guard-class-hold-parked.json
target_class: detector
state_space: hold_reason as the depositor WRITES it — `class:<name>` (depositor.py:194), `empty_writes` (:232), a collision's reason (:243), `held_pending_ceo_release` (:245), and the claim's `stale-checkout` (bellows.py:1027) — × sidecar state {present and JSON / absent / present but not JSON} × name form {`hold-…`, `parallel-N-hold-…`}; the cells the tests occupy: t-a, t-f (class, present), t-b (stale), t-c (pending release), t-d (absent), t-e (not JSON); the two reasons without a row (`empty_writes`, a collision) fall to the same `else` as t-b and are named, not tested
open_forks: 1. the guard reading the DELEGATION itself (a tuyere record of "releases withheld until <time>") rather than the class alone — if a class hold outside a delegation should still freeze; 2. `wrap_check.py`'s receipts arm counting a class-held deposit's live receipt (the second obstacle the 2026-09-09 entry names)
walks: 2
yields: 3, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=VACUOUS, propagation_check=DIVERGENT:6
coherence: 2/2 body walks named in the register (7 register rows; walk-token match, NOT row coverage)
fold_baseline: governance/knowledge/decisions/drafts/.executable-bellows-guard-class-hold-parked.md.foldcheck.json

---

## STEP 1 — DEV (one predicate branch, nine tests, one sentence; the mutation run; two commits)

> ⛔ **Every item starts by re-establishing the root** — `cd "$(git rev-parse --show-toplevel)" && test -f gates.py && echo TREE_OK` — HALT unless TREE_OK. ⛔ **The interpreter is `/Users/marklehn/Developer/bellows/.venv/bin/python`, ABSOLUTE.** ⛔ Never run the daemon, `run_plan`, a claim; the guard is run only against a `tmp_path` shop in tests (`ELUVIAN_SHOP_ROOT` monkeypatched as the existing tests do) — never against the live shop from this step; `T=$(mktemp -d /tmp/guard-hold.XXXXXX)` for scratch, removed at the end.
>
> **Scope:**
> - `tools/lessons_guard.py`
> - `tests/test_lessons_guard.py`
> - `hooks/commands/wrap.md`
> - `knowledge/mutants/guard-class-hold-parked.json`
> - `knowledge/mutants/guard-class-hold-parked.run.txt`
> - `knowledge/development/dev-log-guard-class-hold-parked-2026-09-11.md`
>
> **Item 1 — re-derive P1, P2, P3 and P5 and HALT on a mechanism mismatch** (a line-number drift is not a mismatch; a sidecar read already inside `freezing_plans`, or a sidecar name rule in the depositor other than `.md → .hold.json`, IS one). Paste each pin's re-derived line beside it.
> **Item 2 — write the failing tests FIRST:** *What this changes* 2 — the `_shop` helper's `sidecars=` parameter, rows t-a … t-f in the table, t-g, t-h, t-i (red: t-a and t-f fail on `hold-executable-100031.md` still freezing; t-g `AttributeError: parked_class_holds`; t-h's `class-held:` absent from the pin line). Run the file; paste the red summary line.
> **Item 3 — the edits** as *What this changes* 1 and 3; then the file green (sixteen old rows plus the new tests), then the FULL suite green (`N passed, 1 skipped` — `test_gate_watcher`'s live-DB skip is the one).
> **Item 4 — first commit**, gated on the FULL suite AND the pre-check with the stage flag (#100067), path-scoped: `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ -q && /Users/marklehn/Developer/bellows/.venv/bin/python tools/check_deposit.py /Users/marklehn/Developer/bellows/knowledge/decisions/in-progress-executable-<id>.md 1 --wt "$(git rev-parse --show-toplevel)" --expect-missing knowledge/development/dev-log-guard-class-hold-parked-2026-09-11.md knowledge/mutants/guard-class-hold-parked.run.txt && git add tools/lessons_guard.py tests/test_lessons_guard.py hooks/commands/wrap.md knowledge/mutants/guard-class-hold-parked.json && git commit -F <msg-file> -- tools/lessons_guard.py tests/test_lessons_guard.py hooks/commands/wrap.md knowledge/mutants/guard-class-hold-parked.json` — four files (the manifest rides this commit so the mutation run's `HEAD:` archive contains it); the message tagged with the plan id and `thread 278`.
> **Item 5 — the mutation run, REDIRECTED into `knowledge/mutants/guard-class-hold-parked.run.txt` (a Deposit):** `/Users/marklehn/Developer/bellows/.venv/bin/python tools/mutation_check.py knowledge/mutants/guard-class-hold-parked.json > knowledge/mutants/guard-class-hold-parked.run.txt 2>&1`; the last line must read `MUTATION: 3 killed, 0 survived, 0 error` — a survivor is a test to write, not a mutant to delete.
> **Item 6 — the dev-log** `knowledge/development/dev-log-guard-class-hold-parked-2026-09-11.md` under the four headings declared below; `## Pins re-derived (P1, P2, P3, P5)` opens with P4's value cell pasted verbatim, whole, to its last character — ⛔ the cell ends with the words `for nothing the guard protects`; paste through those words, then stop. Under `## Failing-first (red, then green)` the red line and the green line; under `## The guard observed (t-a, t-b, t-h)` the three verdicts and the pin line pasted from the tests' output; under `## Mutation run` the run file's last line. **Second commit**, gated on the FULL suite and the pre-check bare (`… tools/check_deposit.py … 1 --wt "$(git rev-parse --show-toplevel)"`, no stage flag), path-scoped to the run file and the dev-log. Last act: `[ -n "$T" ] && [ -d "$T" ] && rm -rf "$T"`.
> **Headings:** `## Pins re-derived (P1, P2, P3, P5)`; `## Failing-first (red, then green)`; `## The guard observed (t-a, t-b, t-h)`; `## Mutation run`
> **Verbatim:** `## Pins re-derived (P1, P2, P3, P5)` ← P4
>
> **Deposits:**
> - `knowledge/mutants/guard-class-hold-parked.json`
> - `knowledge/mutants/guard-class-hold-parked.run.txt`
> - `knowledge/development/dev-log-guard-class-hold-parked-2026-09-11.md`
>
> **Post-conditions:** the sixteen old rows and the nine new tests green; the full suite `N passed, 1 skipped` with no `failed`; the mutation run's last line `MUTATION: 3 killed, 0 survived, 0 error`; two DEV commits — the first carrying the four files, the second the run file and the dev-log; `hooks/commands/wrap.md` changed on one line (`git diff --numstat <base>..<dev> -- hooks/commands/wrap.md` reads `1 1`); the dev-log's four headings present as full lines with P4's cell whole; `git status --porcelain` empty after the second commit; the live shop never read by the guard from this step (every guard call in the tests runs under a monkeypatched `ELUVIAN_SHOP_ROOT`).

## STEP 2 — QA (full suite; the guard run on a COPY of the live lane state; the receipt)

> ⛔ **Every item starts by re-establishing the root** — `cd "$(git rev-parse --show-toplevel)" && test -f gates.py && echo TREE_OK` — HALT unless TREE_OK. Interpreter ABSOLUTE; read-only beyond the two evidence files; `T=$(mktemp -d /tmp/guard-hold-qa.XXXXXX)`.
>
> **Item 1 — the full suite REDIRECTED not piped:** `/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest tests/ --tb=short -q > knowledge/qa/evidence/guard-class-hold-parked-suite-2026-09-11.txt 2>&1`; the summary line quoted in the receipt as `N passed` with the skip named as `one skip (test_gate_watcher, live-DB)` — never the word the Rule 20 block scans for.
> **Item 2 — the guard on a copy of the live lanes, never the live shop:** build `$T/shop/` with one lane `$T/shop/bellows/knowledge/decisions/` holding COPIES of the live bellows lane's `hold-*.md` files and their `.hold.json` sidecars ONLY (`cp /Users/marklehn/Developer/bellows/knowledge/decisions/hold-* "$T/shop/bellows/knowledge/decisions/" 2>/dev/null`) — never the lane's other files: this plan's own `in-progress-executable-<id>.md` sits in that lane while the QA runs and would freeze the copy for a reason the item is not measuring; the `Done/` subtree is not copied and a `LESSONS.md` copy at `$T/shop/eluvian-governance/LESSONS.md`; then `ELUVIAN_SHOP_ROOT="$T/shop" ELUVIAN_WRAP_ROOT="$T/shop/eluvian-governance" /Users/marklehn/Developer/bellows/.venv/bin/python tools/lessons_guard.py pin` (the worktree's guard — the DEV's) and paste its first line: this plan's own `hold-` file, if its release has not yet happened when the QA runs, appears as `class-held: 1` with `frozen: no`; otherwise `class-held: 0`. Then add to the copy a synthetic `hold-executable-qa-probe.md` with a sidecar `{"hold_reason": "stale-checkout"}` and run `pin` again → FROZEN, the probe named, exit 2; paste both. Nothing under the live lane is read by the guard in this item — the environment variables point every read at `$T`.
> **Item 3 — production writes, stated exactly:** none outside the two evidence files; `$T` removed; no lane file, no lifecycle row, no daemon.
> **Item 4 — receipt** `knowledge/qa/evidence/guard-class-hold-parked-qa-receipt-2026-09-11.md`: `numstat` over the DEV commits (`<base>..<dev>`, six files); a `## Verification` table with one row per Item 1–3, each quoting the line it rests on — ⛔ the status cell holds exactly one token (`✅`) and no positive row's text carries a hedging keyword; then RUN the canonical Rule 20 block (`$ELUVIAN_WRAP_ROOT/RULE_20_SELF_CHECK_BLOCK.md`) with `plan_slug: guard-class-hold-parked-2026-09-11`, `qa_report_path` and `evidence_dir` absolute under `$(git rev-parse --show-toplevel)/knowledge/qa/evidence/`, `required_evidence_files: ["guard-class-hold-parked-suite-2026-09-11.txt"]`, and APPEND its stdout — the banner `Rule 20 — QA Self-Check Results` and the closing `PASSED — SELF-CHECK PASSED` line are the block's output, never hand-authored; a `FAILED` stdout goes into the receipt and the step STOPS (PT v4.108 §8).
> **Item 5 — commit**, path-scoped and gated: `grep -Eq '^[0-9]+ passed' knowledge/qa/evidence/guard-class-hold-parked-suite-2026-09-11.txt && ! grep -Eq '[0-9]+ (failed|error)' knowledge/qa/evidence/guard-class-hold-parked-suite-2026-09-11.txt && /Users/marklehn/Developer/bellows/.venv/bin/python tools/check_deposit.py /Users/marklehn/Developer/bellows/knowledge/decisions/in-progress-executable-<id>.md 2 --wt "$(git rev-parse --show-toplevel)" && git add knowledge/qa/evidence/guard-class-hold-parked-qa-receipt-2026-09-11.md knowledge/qa/evidence/guard-class-hold-parked-suite-2026-09-11.txt && git commit -F <msg-file> -- knowledge/qa/evidence/guard-class-hold-parked-qa-receipt-2026-09-11.md knowledge/qa/evidence/guard-class-hold-parked-suite-2026-09-11.txt`. ⛔ A QA step that must change production code STOPS and pauses for a verdict (PT v4.108 §8).
>
> **Deposits:**
> - `knowledge/qa/evidence/guard-class-hold-parked-qa-receipt-2026-09-11.md`
> - `knowledge/qa/evidence/guard-class-hold-parked-suite-2026-09-11.txt`
>
> **Scope:**
> - `knowledge/qa/evidence/guard-class-hold-parked-qa-receipt-2026-09-11.md`
> - `knowledge/qa/evidence/guard-class-hold-parked-suite-2026-09-11.txt`
>
> **Post-conditions:** the suite file's summary line is `N passed, 1 skipped` with N ≥ the DEV's count and no `failed`; Item 2's two pin lines pasted (a class-held count with `frozen: no`; then FROZEN on the synthetic stale hold, exit 2); the receipt's `## Verification` table has three rows and closes with the block's own PASSED line; one QA commit carrying the two evidence files.
