# bellows — executable: RECONCILE THE MANIFEST WORKED EXAMPLE — the doctrine disagreed with itself, and the depositor sided with the prose

**Date:** 2026-08-31 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T2 | **Test Scope:** none (doc-only — no code path reads this file's CONTENT; see MUST-PRESERVE) | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **known_failures:** 0 | **Priority:** 1

**auto_close:** false
**pause_for_verdict:** always

**Tier computed, not judged (§1):** **T-6 fires** — this edits doctrine. No other trigger fires: no code changes (T-1), no production data (T-2), the plan is authored and dispatched on the SAME machine (T-3). ⚠️ A0's second root candidate is a HALT-safe fallback, **not a portability claim** — it does not resolve on this machine and is therefore UNVERIFIED here; if it ever fires, treat it as untested, nothing irreversible (T-5), and it is a structure-for-structure clone of `548` by kind (T-8). Highest demand → **T2: full five-lens walk PLUS the cold-reader panel (§2.6).** ⚠️ **The panel's Gate-1 non-author read has ALREADY BEEN PERFORMED** and is recorded in the Drafting Cycle block — it returned ROUTE-AMEND and is what narrowed this plan from five edits to three.

**Clone origin BY KIND — measured:** `executable-548` — a **bellows** plan editing a **governance-root doctrine file by absolute path, in its own commit**, doc-only, DEV → QA, `Test Scope: none`. **Divergence:** 548 pulled wiring into `ELUVIAN_PATH.md`; this one reconciles a file to itself.

## Why this exists

⛔ **`DRAFTING_CYCLE.md` contradicts itself 34 lines apart, and the enforcing code sides with the prose.**

- `:228` **prose** states the manifest's `validation:` field carries `checker=verdict` pairs, and gives the pair spellings in **UPPER_SNAKE**.
- `:262` **worked example** — the block a Planner copies — gives the same two pairs in **lower-hyphen**.

`depositor.py:518` compares the declared `cycle_check=` token to `cycle_check`'s actual output with a **case-sensitive exact compare** (`expected != str(verdict)`). The emitter produces the upper-snake token. **So the doc's own worked example is a trap that fires at deposit**, and it fired: `executable-100005` was held on 2026-08-31 with `validation_mismatch`, its manifest having been written by copying `:262` verbatim.

**Measured over one corpus at one instant** (`cycle_check.parse_manifest_stanza` across `bellows/knowledge/decisions/Done/` + `tuyere/knowledge/decisions/Done/`): **48 stanzas — 41 bellows, 7 tuyere. 48/48 declare the upper-snake `cycle_check` token. 45 declare a bare upper-snake `plan_lint` token and all 48 begin with one. ZERO use the doctrine's spelling.**

⛔ **This is not a judgement about the right value.** The document already states it correctly, 34 lines above the wrong one, and 48/48 shipped plans agree with the prose. **No rule changes.**

## What this plan does NOT do — the narrowing, and where each piece went

A **non-author Gate-1 cold read** (CEO-injected, per the v2.14 strengthening) returned **ROUTE-AMEND**. The CEO ruled *narrow and spin*. Removed from this plan:

- **The `class:` list and the rest of the `:228` sentence → thread 67.** That sentence carries **four** doc-vs-code defects, not one. ⚠️ **Fixing the class list ALONE would expand the set to five and leave "the other two hold for the CEO" dangling off it** — turning a false sentence into a false *and* ungrammatical one. It must be fixed as ONE edit, and not here.
- **A tier floor for rule-preserving reconciliations (T0-R) → thread 68.** It is a **rule addition**, not a reconciliation, and it has no business riding in a plan whose premise is that no rule changes. The cold read also refuted the draft clause: `plan_lint`'s tier pattern matches `T0` *inside* `T0-R`, so nothing distinguishes or audits it.
- **The CEO-class-gate hole → thread 66.** The hold keys on path shape, so the same doctrine edit auto-deposits filed from `tuyere` and holds filed from `bellows`.

**Does not touch §1 or §4.** No trigger, tier, or gate behaviour changes — so §6's *coordinate-doctrine-and-gate* obligation is satisfied **trivially, not deferred**.

## MUST-PRESERVE — clauses whose only carrier is prose

- ⚠️⚠️ **THE BUILDER WRITES TO THE LIVE GOVERNANCE ROOT, NOT TO THE WORKTREE.** This plan dispatches in a bellows worktree, but its target is a **different repository** that has no worktree. `--repo` must be given the **absolute governance root**. ⛔ **Worktree isolation does not cover this edit** — a rollback of the bellows worktree does NOT roll back the doctrine file. The builder's own rollback (byte-equality proven, exit 7 if incomplete) covers ONLY a write failure inside the builder — it does NOT fire on a later step's halt, which is why A2 carries an explicit recovery command.
- ⚠️⚠️ **TWO COMMITS, TWO REPOSITORIES.** The doctrine edit commits at the **governance root** (its own commit, per `548`); the dev log and QA receipt commit in **bellows**. Neither commit may contain the other repo's files.
- ⚠️ **No code path reads this file's CONTENT.** `depositor.py:38` matches its **PATH** only — `DRAFTING_CYCLE.md` is a `_REGISTER_PATTERNS` entry used to classify plans that *write* it. A content change therefore cannot alter any gate's behaviour, which is why `Test Scope: none` is legitimate and not laziness.
- ⚠️ **Exactly THREE edits — E1, E4, E5.** If the builder reports any other count, or names an edit id containing `class` or `t0`, the narrowing has been undone: **HALT**.
- ⚠️ **The 2.16 changelog row must survive.** E5 inserts above it; it does not replace it.
- ⚠️ **Do not "improve" the sentence at `:228` while you are in the file.** It is wrong in four ways and belongs to thread 67. Touching it here re-merges what the CEO ruled apart.

## Numbers discipline — the pins DEV re-derives

⚠️ **Measured 2026-08-31 by the Planner on the live checkout. Re-derive; yours supersede and you say so.**

| id | pin | value | probe |
|---|---|---|---|
| P1 | `DRAFTING_CYCLE.md` sha, pre-edit (first 16) | `2dcc041cc88a8975` | `shasum -a 256` |
| P2 | doctrine version, pre-edit | **2.16 (2026-08-25)**, declared at line 5 | `sed -n '5p'` |
| P3 | builder anchors | **3**, each `count=1` | `build-doctrine-manifest-reconcile.py --repo <gov> --check` |
| P4 | corpus, one corpus one instant | **48 stanzas; 48/48 upper-snake `cycle_check`; 45 bare upper-snake `plan_lint`** | `cycle_check.parse_manifest_stanza` over both `Done/` dirs |
| P5 | lines changed by the builder | **5** | `diff` pre/post in a scratch copy |
| P6 | ⚠️ **BUILDER sha** (first 16) — the tool is in the governance repo, NOT dispatched and NOT worktree-isolated | `c381688fa23366d3` | `shasum -a 256 "$BUILDER"` |

⛔ **P6 CREATES A COUPLING THAT MUST BE MAINTAINED IN THE SAME FOLD.** Any later walk that edits the builder invalidates P6, and A1 would then HALT on a legitimate tool — a self-inflicted outage of exactly the kind the `${ELUVIAN_WRAP_ROOT:?}` lesson describes. **If a fold touches the builder, re-measure P6 in that same fold and say so in the walk's register row.** A pin is a promise about a second artifact; it goes stale silently.

## STEP 1 — DEV

> ⛔ **A0 — pre-flight. RESOLVE BOTH ROOTS FIRST — this plan spans two repositories.**
> ```
> cd "$(git rev-parse --show-toplevel)" && [ -f bellows.py ] && echo BELLOWS_TREE_OK   # HALT unless OK
> MAIN=$(cd "$(git rev-parse --git-common-dir)/.." && pwd)
> PY="$MAIN/.venv/bin/python"; [ -x "$PY" ] && echo VENV_OK || echo NO_VENV           # HALT unless VENV_OK
> GOV=""
> for c in "$HOME/Developer/eluvian-governance" "$HOME/Developer/GitHub"; do
>   [ -f "$c/DRAFTING_CYCLE.md" ] && GOV="$c" && break
> done
> [ -n "$GOV" ] && echo "RESOLVED governance: $GOV" || { echo NO_GOV; exit 1; }        # HALT unless resolved
> BUILDER=""
> for c in "$GOV/governance/knowledge/decisions/drafts/build-doctrine-manifest-reconcile.py"; do
>   [ -f "$c" ] && BUILDER="$c" && break
> done
> [ -n "$BUILDER" ] && echo "RESOLVED builder: $BUILDER" || { echo NO_BUILDER; exit 1; }
> ```
> ⚠️ **The second root candidate is UNVERIFIED from the authoring machine** — it does not exist here, so its arm has never been exercised. If A0 resolves via it, say so explicitly in the dev log and treat every downstream path as untested.
> ⚠️ **State both resolved paths on their own lines in the dev log.** The interpreter resolver uses `--git-common-dir` because a worktree has no `.venv`; the governance resolver tries known roots because machine layouts differ and `ELUVIAN_WRAP_ROOT` is absent from the daemon's environment.
>
> ⛔ **A1 — verify the pins BEFORE building.** `shasum -a 256 "$GOV/DRAFTING_CYCLE.md"` (P1) and `sed -n '5p' "$GOV/DRAFTING_CYCLE.md"` (P2). ⚠️ **⛔ **A sha mismatch has TWO causes and they need opposite responses. Distinguish before reporting:**
> ```
> grep -q 'Version:\*\* 2.17 (2026-09-01)' "$GOV/DRAFTING_CYCLE.md" \
>   && echo 'ALREADY-LANDED: this plan has already applied. Stop cleanly; do NOT re-run A2.' \
>   || echo 'FOREIGN CHANGE: the file moved under this plan. HALT and report.'
> ```
> ⚠️ **Measured at walk 8:** after this plan's own edits land, the sha is `f4fc6913d3ff7700` against P1's `2dcc041cc88a8975`, so a RETRY trips this check — and the un-split message blamed an outside actor for the plan's own success. The builder would have said `ALREADY-APPLIED`, but A1 halts before it runs.** ⛔ **Also confirm TODAY'S DATE matches the version line the builder writes** (`2.17 (2026-09-01)`). If they differ, the plan sat between authoring and dispatch: **HALT** — the Planner re-dates the builder, re-measures P6 in that same fold, and re-deposits. A permanent doctrine history row must carry the date it LANDED, not the date it was drafted. ⛔⛔ **THIS PLAN IS DISPATCHABLE FOR ONE DAY ONLY. If it is not dispatched on the date its version line carries, A1 HALTS and a six-site re-date is required before it can run.** That is deliberate — a permanent doctrine history row must carry the date it LANDED — but the COST is real and was unstated until walk 9: **every day this plan sits undispatched costs a full re-date plus a re-pin.** It has already sat one day on an escalation. ⚠️ **Treat dispatch as time-boxed: deposit and release on the same day the Planner dates it, or budget the re-date.**
> ⛔ **A RE-DATE IS A FIVE-SITE EDIT PLUS A RE-PIN — a list that GREW TWICE while being written.** Walk 4 performed three sites and the re-pin; walk 5 found a fourth (A3.1) and wrote the list; walk 6 found a fifth (Step 1's post-conditions) that walk 5's own fold had created. ⚠️ **A site list is itself a site**: adding an assertion anywhere adds a member, so the list must be re-checked whenever the plan grows one. The sites: (1) the builder's `**Version:**` POST string, (2) the builder's changelog-row POST string, (3) **this guard's expected date**, (4) **A3.1's assertion**, (5) **Step 1's post-conditions line** — and then (6) **re-measure P6**, because touching the builder invalidates it. ⚠️ Missing (4) is what walk 5 caught: the plan asserted two different dates for the same version line and would have HALTED on a correct build.
> ⛔ **Then pin the BUILDER ITSELF: `shasum -a 256 "$BUILDER"` must match P6.** The builder lives in a repo this plan does not dispatch into and no worktree isolates — so the tool DEV executes can differ from the tool the cycle reviewed, and nothing else would notice. **A mismatch is a HALT**: report both shas and stop. Then `"$PY" "$BUILDER" --repo "$GOV" --check` — **expect exactly 3 anchors, each `count=1`, exit 0, no write** (P3). ⛔ **If the count is not 3, or any edit id contains `class` or `t0`, HALT** — the narrowing has been undone.
>
> ⛔ **A1.5 — CAPTURE THE GATE BASELINE BEFORE THE EDIT, or Item 4 cannot be performed.** Bind the baseline plan to a VARIABLE so Item 4 can name the identical file:
> ```
> BASE=knowledge/decisions/Done/executable-100005.md
> [ -f "$BASE" ] || BASE=$(ls -t knowledge/decisions/Done/executable-*.md | head -1)   # NEWEST by mtime
> grep -q '^## Cycle Manifest' "$BASE" || { echo "BASELINE PLAN HAS NO MANIFEST: $BASE"; exit 1; }   # HALT
> [ -f "$BASE" ] && echo "BASELINE PLAN: $BASE" || { echo NO_BASELINE_PLAN; exit 1; }   # HALT if none
> ```
> ⚠️ **The fallback sorts by mtime, NOT alphabetically.** Measured at walk 8: `| tail -1` on an alphabetical listing resolved to a plan from 2026-05-27 — deterministic, but on the wrong axis, and an old plan's gate verdicts can differ for reasons unrelated to this edit. The manifest check exists for the same reason: a plan with no stanza yields a verdict that cannot be compared. ⚠️ **State `BASELINE PLAN:` on its own line in the dev log** — Item 4 must run against the SAME file, and "pick one" without recording which is not a baseline. Then record, verbatim, both:
> ```
> "$PY" "$MAIN/scripts/plan_lint.py"  "$BASE"   # record the PASS/FAIL counts
> "$PY" "$MAIN/scripts/cycle_check.py" "$BASE"  # record the verdict token
> ```
> ⚠️ **This must run BEFORE A2.** After the builder writes, the pre-edit state is gone and Item 4 becomes an assertion with nothing behind it — the same unperformable-control defect this shop has recorded twice.
>
> **A2 — run the Planner's builder.** `"$PY" "$BUILDER" --repo "$GOV"`. Expect `APPLIED: 3/3 edits.` ⚠️ **Do not hand-edit `DRAFTING_CYCLE.md`.** Any exit other than 0 is a STOP; the builder rolls back and proves byte-equality itself.
>
> ⛔ **RECOVERY — IF THIS PLAN HALTS ANYWHERE BETWEEN A2 AND A5, THE GOVERNANCE ROOT IS LEFT DIRTY AND NOTHING CLEANS IT.**
> The builder's rollback lives inside its own write `try/except` — it fires ONLY on a write failure *inside the builder*, never on a later step's HALT. And `_teardown_worktree` operates on the **dispatching project only** (`bellows.py:1908`), so the bellows worktree teardown cannot see a modified file in another repository. **A halt at A3 or A4 therefore leaves `DRAFTING_CYCLE.md` modified and uncommitted in the live governance root**, where the next session or `/wrap` finds it as unexplained dirt.
> **Recovery is one command, in the governance root:**
> ```
> git -C "$GOV" checkout -- DRAFTING_CYCLE.md
> git -C "$GOV" status --porcelain DRAFTING_CYCLE.md    # must print NOTHING
> ```
> ⛔⛔ **RUN THIS ONLY FOR A HALT AT A3 OR A4 — NEVER AFTER AN A1 HALT.** An A1 halt means the sha did NOT match, i.e. the file already carried uncommitted changes that are **not this plan's**; `checkout --` would DESTROY that work, and A1 exists precisely to detect that state. ⚠️ **Before running it, confirm A2 reported `APPLIED: 3/3` in this run.** If A2 did not run, there is nothing to recover and the correct action is to report and stop. Within that scope: leaving doctrine dirty for the wrap to find is worse than the halt itself.
>
> **A3 — verify, in the governance root.** ⛔ **EVERY sub-step below names `"$GOV"` explicitly.** A3 runs from a bellows worktree, where no `DRAFTING_CYCLE.md` exists; a bare path checks nothing or checks the wrong file. ⚠️ Walk 5 gave two of the six an explicit root and walk 6 found the other four — **enumerate all six when editing any one.**
> - **A3.1** — `sed -n '5p' "$GOV/DRAFTING_CYCLE.md"` reads **2.17 (2026-09-01)** — the SAME date A1's guard checked. ⚠️ These two must always agree: walk 4 re-dated the builder and this assertion was left behind, which would have failed a CORRECT build.
> - **A3.2** — `grep -n 'cycle_check=BAR_MET' "$GOV/DRAFTING_CYCLE.md"` returns **THREE** lines: the `:228` prose, the `:262` worked example, and the new `2.17` changelog row, which quotes the corrected spelling. **Quote the first two and state they agree.** ⚠️ **Measured, not predicted** — and TWICE corrected: a pattern matching only `validation: cycle_check=` finds the example alone and cannot show agreement at all, while this pattern also catches the changelog row the same plan adds. **An expected COUNT must be measured against a real build, because the plan's own edit changes it.**
> - **A3.3** — `grep -c '^- \*\*2\.1[67] (' "$GOV/DRAFTING_CYCLE.md"` returns **2**: the new `2.17` row AND the surviving `2.16` row. ⛔ Both, or HALT.
> - **A3.4** — ⚠️ **the narrowing held:** `grep -c 'T0-R' "$GOV/DRAFTING_CYCLE.md"` returns **0**, and the `class:` list is still the three-value form. ⛔ Either failing is a STOP.
> - **A3.5** — `git -C "$GOV" show HEAD:DRAFTING_CYCLE.md > /tmp/dc.before && diff /tmp/dc.before "$GOV/DRAFTING_CYCLE.md"` ⚠️ (written WITHOUT process substitution — `<(…)` is a bash/zsh extension and is a syntax error under `sh`) changes **exactly 5 lines** (P5). Report the number you measure. ⛔ **The `-C "$GOV"` is REQUIRED** — this step runs from a bellows worktree, and a bare `git show` would resolve against the WRONG repository and compare the wrong artifact.
> - **A3.6** — re-run the builder **against the same root** — `"$PY" "$BUILDER" --repo "$GOV"` — and it must print `ALREADY-APPLIED`, not re-apply. ⚠️ Omitting `--repo "$GOV"` makes the builder ABORT on a missing target rather than confirm idempotence, which reads as a failure when nothing is wrong.
>
> **A4 — dev log** `knowledge/dev-logs/doctrine-manifest-reconcile-dev-2026-08-31.md`: **both resolved paths on their own stated lines**, the P1/P2/**P6** pin comparisons, **A1.5's gate baseline verbatim (the named plan, its PASS/FAIL counts and verdict token)**, the builder's full output, and each A3 result with the number you measured.
>
> **Deposits:**
> - `/Users/marklehn/Developer/eluvian-governance/DRAFTING_CYCLE.md`
> - `bellows/knowledge/dev-logs/doctrine-manifest-reconcile-dev-2026-08-31.md`
>
> **Scope:**
> - `/Users/marklehn/Developer/eluvian-governance/DRAFTING_CYCLE.md`
> - `bellows/knowledge/dev-logs/doctrine-manifest-reconcile-dev-2026-08-31.md`
>
> **Post-conditions:** ⚠️ **one per HALT-bearing check, A0 through A5 — verified complete at walk 7 by mapping each to its producing step.** A0's governance root AND builder both resolved and stated · P1/P2/P6 all matched, or the step HALTED · today's date matches the version line the builder writes · A1.5's gate baseline captured on a NAMED plan and recorded verbatim BEFORE A2 · builder reported `APPLIED: 3/3` with 3 anchors each `count=1` · version reads **2.17 (2026-09-01)** — version AND date, matching A1's guard and A3.1 exactly — the worked example agrees with the `:228` prose, the 2.17 row exists AND the 2.16 row survives · **both changelog rows present — the new 2.17 AND the surviving 2.16 (A3.3)** · the narrowing held — `class:` list still three values, `T0-R` count 0 · diff exactly 5 lines · re-run reports ALREADY-APPLIED · two pathspec-scoped commits, each containing exactly one file, neither carrying the other repo's.
>
> **A5 — commit, TWO repositories, in this order.** ⚠️ **Governance FIRST** (it is the load-bearing change): `git -C "$GOV" commit --only DRAFTING_CYCLE.md -m "[<plan-id>] docs(drafting-cycle): reconcile the manifest worked example — DC v2.17"`. ⛔ **The `-m` is REQUIRED, not decorative** — a bare `git commit` opens an editor, and this step runs non-interactively under the daemon, where that hangs or dies rather than committing. Then the bellows dev log in its own commit, likewise `--only` and likewise with an explicit `-m`. ⛔ **THE TWO COMMITS ARE NOT ATOMIC ACROSS REPOSITORIES, AND THE A2 RECOVERY DOES NOT APPLY ONCE THE FIRST HAS LANDED.**
> ⚠️ **The two commits do not even land by the same MECHANISM.** The bellows dev-log commit is made inside a **worktree branch** and reaches main only when `_teardown_worktree` merges it back (`bellows.py:1909`), which **raises and leaves the worktree alive on a merge conflict**; the governance commit is **immediate and global** the moment it runs. So they are not merely non-atomic — one is provisional until teardown and the other is not. Governance commits FIRST because it is the load-bearing change: the surviving half-state is then *landed but unlogged*, which is recoverable, rather than *logged but unlanded*, which is a false record. ⚠️ **If the bellows commit fails after governance has committed, DO NOT `checkout --` or revert the governance commit** — the A2 recovery block is for the UNCOMMITTED case only and is actively wrong here. Instead: report the governance sha, state that the dev log is unwritten, and let the next step or session complete the bellows half. A landed doctrine change with a missing log is a bookkeeping gap; a reverted doctrine change with a written log is a corrupted record.
>
> ⛔ **BOTH COMMITS MUST BE PATHSPEC-SCOPED — `--only`, never a bare `git commit`.** A bare commit writes the whole INDEX, so anything staged beforehand in either repo rides along silently; this plan's QA step already scopes its commit, and DEV must too. ⛔ **Verify with `git show --stat` on both: the governance commit must contain EXACTLY ONE file and the bellows commit EXACTLY ONE.** Neither may contain the other repo's files. State both shas and both file counts.

---

## STEP 2 — QA

> ⛔ **Q0 — pre-flight. STEP 2 IS A FRESH AGENT INVOCATION — EVERY VARIABLE STEP 1'S A0 SET IS GONE.** Step 2 needs only `$PY` and `$GOV`; it never invokes the builder, so re-resolve exactly those two and nothing else:
> ```
> MAIN=$(cd "$(git rev-parse --git-common-dir)/.." && pwd)
> PY="$MAIN/.venv/bin/python"; [ -x "$PY" ] && echo VENV_OK || echo NO_VENV        # HALT unless VENV_OK
> GOV=""
> for c in "$HOME/Developer/eluvian-governance" "$HOME/Developer/GitHub"; do
>   [ -f "$c/DRAFTING_CYCLE.md" ] && GOV="$c" && break
> done
> [ -n "$GOV" ] && echo "RESOLVED governance: $GOV" || { echo NO_GOV; exit 1; }
> ```
> ⛔ **Q0 IS A SECOND COPY OF A0's RESOLVER — THE TWO MUST MOVE TOGETHER.** The governance loop and the `--git-common-dir` interpreter derivation each appear TWICE in this plan. **A fold that changes one and not the other silently diverges the two steps**, and the divergence only shows at dispatch, in the step that was not updated. ⚠️ If a walk edits either resolver, it must edit both in the SAME fold and say so in that walk's register row.
> ⚠️ **State both resolved paths in the receipt.** A step that inherits a variable it never set is the defect this shop has now paid for three times — once in the plan lane's A0, once in its own tooling, and once here.
>
> **Item 1 — re-verify the reconciliation at the seam.** In the governance root, print the `:228` prose pair spellings and the worked example's `validation:` line **side by side** and state that they now agree. ⚠️ Quote them from the FILE — `sed -n`/`grep -o` — never restate them.
>
> **Item 2 — the corpus still agrees.** Re-run the P4 measurement over both `Done/` dirs with `cycle_check.parse_manifest_stanza` and state the stanza count and the token tallies you measure. ⛔ **Copy the numbers from your own command output; do not restate the plan's.**
>
> **Item 3 — the narrowing held.** State the `class:` list value verbatim from the file and the `T0-R` occurrence count. Both must show the edit did NOT happen.
>
> **Item 4 — no gate behaviour changed.** Run `plan_lint` and `cycle_check` (under Q0's resolved interpreter) against **the plan A1.5 recorded as `BASELINE PLAN:`**, and compare to the counts and verdict token **A1.5 recorded in the dev log**. ⛔ **Quote both the recorded values and yours** — a comparison against a baseline you did not read is not a comparison. ⚠️ This is the evidence that a content change to this file cannot move a gate.
>
> **Item 5 — the two commits are clean.** `git show --stat` on each; state both shas and confirm neither contains the other repo's files.
>
> **Item 6 — receipt** `knowledge/dev-logs/doctrine-manifest-reconcile-qa-2026-08-31.md`: **Q0's two resolved paths, then Items 1-5, each on its own stated line — SIX lines, not five.** ⚠️ Q0 was added at walk 3 and this enumeration did not absorb it until the same walk swept for it; Items 6 and 7 are the receipt and the commit themselves and are correctly excluded. Then the Rule 20 block inside a "Verification"-headed section.
>
> **Item 7 — commit**, pathspec-scoped: the receipt only, exactly one file.
>
> ⚠️ **Gate note:** nothing executable runs here — the header declares no scope, deliberately. Do not invent one; a doc-only plan that invokes a suite is declaring a scope it does not have.
>
> **Deposits:**
> - `bellows/knowledge/dev-logs/doctrine-manifest-reconcile-qa-2026-08-31.md`
>
> **Scope:**
> - `bellows/knowledge/dev-logs/doctrine-manifest-reconcile-qa-2026-08-31.md`
>
> **Post-conditions:** Q0's interpreter and governance root both resolved and stated · prose and example agree, quoted from the file · corpus re-measured with stated denominators · `class:` list and `T0-R` both prove the narrowing held · a shipped plan's gate verdicts unchanged · two commits, each clean of the other repo.

Rule 20 banner (byte-exact, inside the QA receipt's VERIFICATION section):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```

---

## Drafting Cycle

**Tier:** T2 — triggers fired: T-6. Doctrine surface.

**Walks:** walk 0 pinned (5 measurements + clone-diff by kind). **Cold Gate-1 read performed by a NON-AUTHOR before v0 prose existed** — the §2.6 cold half, injected by the CEO per the v2.14 strengthening.

- **Walk 0 STATUS:** 2 defects pinned, 1 hypothesis refused by measurement, 0 folds (no plan text existed yet)
- **Walk 1 STATUS:** 5 folded — instruction 5 / record 0 (weak spots 1, destruction 1, vulnerabilities 1, integration-record 1, ACID 1); 0 HIGH; **5 of 5 pre-existing-v0, 0 fold-introduced.** ⚠️ Run under the full §2.7 discipline — one commit per LENS and `fold_check` after every fold, all five `FOLD-CHECK CLEAN`
- **Walk 2 STATUS:** 4 folded — instruction 3 / record 1 (weak spots 1, destruction 1, vulnerabilities 1, integration-record 1; ACID dry); **1 HIGH**; **2 of 4 fold-introduced by walk 1's own folds.** First walk to auto-advance on `CONTINUE` without a CEO pause
- **Walk 3 STATUS:** 5 folded — instruction 5 / record 0 (weak spots 1, destruction 1, vulnerabilities 1, integration-record 1, ACID 1); 0 HIGH; **2 of 5 fold-introduced, both caught in the SAME walk that introduced them**
- **Walk 4 STATUS:** 4 folded — instruction 3 / record 1 (weak spots 1, vulnerabilities 1, integration-record 1, ACID 1; destruction dry); 0 HIGH; **2 of 4 fold-introduced by walk 3, both caught here.** Resumed from the CEO escalation
⚠️ **WALK-CLOSE OBLIGATION: the manifest's `walks:` and `yields:` fields are updated in the SAME commit that appends the walk's STATUS bullet.** Stated as a step because the prose promise alone failed three walks running.

- **Walk 5 STATUS:** 5 folded — instruction 5 / record 0 (weak spots 1, destruction 1, vulnerabilities 1, integration-record 1, ACID 1); 0 HIGH; **3 of 5 fold-introduced by walk 4's re-date**
- **Walk 6 STATUS:** 6 folded — instruction 5 / record 1 (weak spots 1, destruction 1, vulnerabilities 2, integration-record 1, ACID 1); 0 HIGH; **5 of 6 fold-introduced, 3 of them within walk 6 itself**
- **Walk 7 STATUS:** 4 folded — instruction 3 / record 1 (weak spots 1, vulnerabilities 1, integration-record 1, ACID 1; destruction DRY by execution); 0 HIGH; **3 of 4 fold-introduced**
- **Walk 8 STATUS:** 5 folded — instruction 4 / record 1 (weak spots 1, destruction 1, vulnerabilities 1, integration-record 1, ACID 1); 0 HIGH; **1 of 5 fold-introduced; 1 CLONE-DRIFT inherited from `executable-548`**
- **Walk 9 STATUS:** 2 folded — instruction 1 / record 1 (weak spots 1, integration-record 1; destruction, vulnerabilities and ACID all DRY **by execution**); 0 HIGH; 0 fold-introduced. ⚠️ Run as an EXECUTION pass — every A-step and every executable QA item run as written against a real build, **zero deviations**
- **Walk 10 STATUS:** 0 folded — instruction 0 / record 0 (weak spots dry, destruction dry, vulnerabilities dry, integration-record dry, ACID dry); 0 HIGH. ⚠️ A second EXECUTION pass, aimed at the FAILURE arms nine walks had left untested — builder exits 2, 3, 5 and 6 all exercised, each writing nothing
- Cold panel — Gate-1 non-author read (walk 0.5): verdict **ROUTE-AMEND**, 7 required amendments, **5 corrections to walk 0's own pins**, 4 missed siblings, 1 live gate hole. ⛔ **It refuted the author on the record**: the corpus figures were wrong and one was RECALLED not measured; the sibling sweep enumerated from one call's spelling in one consumer (4 fields where there are 13); and the safety claim was over-generalised. **Resolution: the CEO ruled narrow-and-spin; this plan went from 5 edits to 3, and threads 66, 67, 68 were opened.**

**Closing:** ✅ **full walk 10 dry; last event = lens pass; bar met — instruction 0 / record 0 across all five lenses.** Instruction-class 0 → 5 → 3 → 5 → 3 → 5 → 5 → 3 → 4 → 1 → **0**. The mandatory closing-record re-read was run and is DRY: 10 STATUS bullets against 10 register rows, every per-walk split agreeing with the manifest sequence, and the Closing's own claims re-checked against source (3 builder commits, 3 edits). ⚠️ **The convergence came from changing HOW the plan was walked, not from walking more.** The eight read-passes yielded 5, 4, 5, 4, 5, 6, 4, 5 — never below 4, and mostly debris from their predecessors' folds. The two EXECUTION passes yielded **2 and 0**. ⛔ **Three false claims were made to the CEO during this cycle and all three were caught by measurement, none by re-reading**: a recalled corpus figure at walk 0 (47 vs the true 48), "the builder has not moved since walk 0" repeated at walks 6-8 (it has three commits), and a mis-designed anchor probe at walk 10 that appeared to show the builder writing over a broken anchor. ✅ **The change itself is unchanged since the Gate-1 narrowing**: three edits, three anchors, five lines, verified by a zero-deviation end-to-end run at walk 9 and by exits 2/3/5/6 all refusing to write at walk 10.

**Walk register:** `governance/knowledge/research/walk-register-doctrine-manifest-reconcile-2026-08-31.md`

---

⛔ **On the `validation:` line below — `<pending>` is a PLACEHOLDER, and `depositor.py:518` has no sentinel exemption for it** (`class` gets `<declare>`; `validation` gets nothing). Depositing with it unreplaced HOLDS the plan with `validation_mismatch` — the defect this plan exists to fix, reproduced in the plan itself. At BAR_MET the stanza is emitted by `cycle_check --emit-manifest` (§3); the four COMPUTED fields are never hand-typed. ⚠️ **This warning lives ABOVE the stanza deliberately**: the parser treats a 2-space-indented line as a CONTINUATION of the preceding field, so a note placed inside the block is swallowed into the value it is warning about — measured at walk 2, where it had grown the `validation` value to 610 characters and changed the extracted token.

⛔ **`writes:` and `reads:` are COMMA-SEPARATED PATH LISTS — no parentheticals, ever.** The first entry is a governance-root path written by absolute reference in its own commit; that fact is stated here, in prose, because putting it inline made `depositor.py` parse **five** writes instead of three — `…DRAFTING_CYCLE.md (root`, `absolute`, `own commit)` — mangling the real path so a `writes∩writes` collision on it could never match, and returning the right class only by accident off the bare token `absolute`. ⚠️ **Measured at walk 8, and inherited from the clone origin `executable-548`, which shipped with the identical defect** (thread filed). Same lesson as w2-1: a note inside the stanza is swallowed by the parser — there, a continuation line; here, a comma.

## Cycle Manifest
tier: T2
target: eluvian-governance/DRAFTING_CYCLE.md
class: shop-infra
reads: /Users/marklehn/Developer/eluvian-governance/DRAFTING_CYCLE.md, /Users/marklehn/Developer/eluvian-governance/governance/knowledge/decisions/drafts/build-doctrine-manifest-reconcile.py, /Users/marklehn/Developer/bellows/depositor.py, /Users/marklehn/Developer/bellows/scripts/plan_lint.py, /Users/marklehn/Developer/bellows/bellows.py, /Users/marklehn/Developer/bellows/gates.py, /Users/marklehn/Developer/bellows/scripts/cycle_check.py
writes: /Users/marklehn/Developer/eluvian-governance/DRAFTING_CYCLE.md, knowledge/dev-logs/doctrine-manifest-reconcile-dev-2026-08-31.md, knowledge/dev-logs/doctrine-manifest-reconcile-qa-2026-08-31.md
open_forks: (0) **thread 64 is this plan's PARENT** — it ships only the `:262` reconciliation; everything else 64 originally carried was spun out below; (0b) **thread 63** gained a FOURTH member during this cycle's own authoring — `plan_lint`'s scope-declaration check matches the POSIX conditional builtin used in every pre-flight guard, and then matches a note that merely QUOTES the header field's name — so the sentence declaring the absence is what makes the check fire. ⚠️ **Described, not quoted, per §3's rule that the Cycle Log must carry no string a gate matches** — a rule whose reason is mechanical: `_extract_step_text` for the LAST step runs to end-of-document, so the Log and this manifest are both INSIDE step 2's text for every step-level check; (1) **thread 67** — the `:228` sentence's four doc-vs-code defects, to be fixed as ONE edit; (2) **thread 68** — T0-R, a reconciliation tier floor, needs a token plan_lint can see, a size bound, and a bar on reconciling doctrine to unratified code; (3) **thread 66** — the CEO class hold keys on path shape, so this same edit would auto-deposit filed from tuyere; this plan's own shop-infra assignment is contingent on being filed from bellows
walks: 10 warm (walk 0 pin + a cold Gate-1 non-author read + walks 1-8 read-passes + walks 9-10 EXECUTION passes); closing-record re-read run at the bar, dry. ⛔ **This field carried the annotation "kept CURRENT per walk" from walk 2 and was then NOT updated at walks 3, 4 or 5** — the promise was written and not kept, which is precisely the failure the annotation was added to prevent. Walk 6 corrected it and the obligation now names the walk-close step that must perform it
yields: 0, 5, 4, 5, 4, 5, 6, 4, 5, 2, 0 | instruction-class: 0, 5, 3, 5, 3, 5, 5, 3, 4, 1, 0 | Gate-1 direction: ROUTE-AMEND → narrowed 5 edits to 3; §2.0 direction verdict after walk 1: PROCEED; ESCALATED yield-rising at walks 3 and 5, CEO-resumed both times
validation: cycle_check=BAR_MET, plan_lint=0_FAIL
coherence: 11/11 walks have register rows (walk 0 + walks 1-10); builder written and verified BEFORE this prose; closing-record re-read run at the bar and dry — STATUS bullets, register rows and the yields sequence all agree
