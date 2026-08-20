# Component 4 — Capstone: Self-Driving Walk Loop — Design + Rule 27 Gap Assessment

**Date:** 2026-08-20
**Diagnostic:** 482 (read-only design)
**Tier:** T1 — triggers T-7, T-8
**Deposit:** `bellows/knowledge/research/component4-capstone-design-2026-08-20.md`

---

## Q0 — Routed Decisions (restated)

These decisions are RATIFIED — the amendment clones their shape, it does not re-derive them.

1. **Plateau threshold = 3 walks.** `check_plateau` (`scripts/cycle_check.py:326`) fires `ESCALATE:plateau` when 3+ consecutive walks report the same instruction count with no new finding class. The amendment adopts this threshold.
2. **ESCALATE = a resumable PAUSE, not a stop.** An `ESCALATE:*` verdict pauses the loop for the CEO; a single-word resume ("continue" / "go") directs the Planner to run the next walk. The cycle is NOT ended — only RE-DRAFT (§2.0 direction verdict) ends a cycle without a deposit.
3. **No cost/token escalation.** The loop does not introduce new token spend beyond what the Planner already performs per walk. `cycle_check` itself is a Python script (~0 tokens). The one material autonomous spend is the cold panel (Q5).
4. **Cold reads fire automatically** at the codified §2.6 triggers — the lens-4 consecutive-pre-existing signal, the T2 walk-0 scout, and the bar-met panel. `[[autonomous-panel-grant]]` authorizes the form (all seats sequential in one turn, findings author-verified between seats).

---

## Q1 — The Loop Mechanism (driver vs walks)

### The distinction

The capstone mechanizes the **DRIVER**, not the **WALKS**.

- **The WALKS** are Planner cognition: five adversarial lenses (§2.1–§2.5), each requiring a genuine read of the artifact, fold-by-fold sequential application (§2.7 sequential-fold rule), per-lens commits, per-fold `fold_check` re-baseline, class sweeps, record updates. These are NOT scriptable — they require fresh-context judgment against the post-fold artifact. The walks remain exactly as they are today.

- **The DRIVER** is the decision between walks: "did cycle_check say CONTINUE? did the Planner surface a direction-class finding? then run the next walk." Today the CEO makes this decision manually ("continue" / "go"). The capstone replaces the CEO's per-walk directive with a protocol: run `cycle_check.run_check` (`scripts/cycle_check.py:347`) after each walk's final commit → act on the verdict.

### Verdict → action mapping

| cycle_check verdict | Loop action |
|---|---|
| `CONTINUE` (exit 0) | Auto-run walk N+1, PROVIDED the Planner has no direction-class finding (see below) |
| `BAR_MET` (exit 0) | Run the mandatory closing-record re-read (§2.7), THEN close + `cycle_check --emit-manifest` |
| `ESCALATE:*` (exit 1) | PAUSE for the CEO. One-word resume runs walk N+1 |

### The driver needs NO new code

**Recommendation: purely a Planner-cadence protocol, no new code.** Reasoning:

1. `cycle_check` already exists, is live-tested this session (dogfooded every walk), and emits the three verdicts the loop needs.
2. `--emit-manifest` already exists (component 2b, plan 474).
3. The depositor (component 3, plan 481) already consumes the manifest.
4. The Planner already runs the walks — the change is WHEN IT STOPS between walks, not what it does during them.

The amendment is a §2 cadence clause telling the Planner "after the walk's final per-lens commit, run cycle_check; on CONTINUE, proceed to the next walk without awaiting CEO direction." No bellows code, no runner change, no new script.

### Two guards the driver is NOT blind to

**Guard 1 — Planner-side direction findings (W4 fold).** Auto-advance requires BOTH `cycle_check=CONTINUE` AND no Planner-side §2.0 forcing/direction finding. The three forcing findings (§2.0: invalidated clone-origin, invalidated mechanism, invalidated scope premise) PAUSE for the CEO even on a CONTINUE verdict. `cycle_check` cannot detect a forcing finding — it reads arithmetic and structure, not semantics. The Planner retains §2.0 direction-verdict authority. The loop is cycle_check-GATED, not cycle_check-BLIND.

**Guard 2 — Entry gate (W5 fold).** Auto-advance applies from **walk 2 onward**. The loop's ENTRY — walk 0 (context pin, §2.0 measurements), walk 1 (first five-lens pass), and the §2.0 DIRECTION VERDICT — is the Planner's manual gate. `cycle_check` has no walk-0 state and no direction-verdict state. A RE-DRAFT verdict ends the cycle; a CUT-AND-PROCEED restructures before auto-advance begins. Auto-advance is licensed only after a PROCEED verdict at the end of walk 1.

---

## Q2 — The Non-Fabrication Substrate (the load-bearing prerequisite)

### What makes a walk non-fabricable

Verified against live `cycle_check` (`scripts/cycle_check.py`):

**Assert #1 — Arithmetic** (`check_assert_1`, `:224`). Per-lens fold counts sum to the walk STATUS total; class splits (instruction + record) sum to the fold count. PASS when the arithmetic is consistent, FAIL on mismatch, N/A when no class-split data is present. This is always available from the plan text — no external substrate needed.

**Assert #2 — Evidence exists** (`check_assert_2`, `:245`).
- **Register arm (`:246–264`):** Needs a `**Walk register:**` line in the DC block (matched by `WALK_REGISTER_RE`, `:31`). The regex captures the ref path. The code resolves it against the plan's git root. If the first path component is a directory under the git root AND is itself a separate git repo → N/A (cross-repo, unreachable). If it's a same-repo directory → checks if the referenced file exists: PASS if yes, FAIL if no. If no `**Walk register:**` line at all → N/A.
- **Git-commit arm (`:267–288`):** Counts `drafting(`/`[draft]`/`deposit(` commits scoped to the plan path. If fewer walk-commits than the highest walk number → `ESCALATE:uncommitted-walk`. This is the "uncommitted walk" detection.

**Assert #3 — Fold happened, baseline exists** (`check_assert_3`, `:292`).
- Needs fold data in the walk (any `total_folds > 0`). Checks for a `.{planname}.foldcheck.json` baseline file. If baseline exists → PASS. If no baseline but git context exists → FAIL. If no git context → N/A.

### The substrate as a PRACTICE

"A register file exists" is insufficient. The FULL substrate is:

1. **A `walk-register-<slug>.md` file** conforming to the walk register schema (`knowledge/architecture/walk-register-schema.md`), with per-lens/per-walk fold rows carrying the eight required fields (including `pre_fold_text` — the verbatim bytes).
2. **A `**Walk register:**` line** in the DC block pointing to the register path within the plan's own repo (not cross-repo — assert #2's register arm returns N/A for cross-repo refs).
3. **Per-walk COMMITS** of both the register and the draft — assert #2's git-commit arm (`ESCALATE:uncommitted-walk`) verifies this; per-lens commits (§2.7:160) make the sequential-fold discipline provable.
4. **A `fold_check` baseline** (`.{planname}.foldcheck.json`) — assert #3 verifies this exists when folds are present.

### Confirmed gap: scratchpad cycles produced N/A

**Live demonstration** (run against the committed corpus):

```
REGISTER-LESS (bellows/executable-439):
  Walk register ref: None
  Assert #1 (arithmetic): N/A
  Assert #2 (register):   N/A (uncommitted=False, git_ctx=False)
  Assert #3 (fold_check): N/A

REGISTER CROSS-REPO (bellows/executable-418):
  Walk register ref: governance/knowledge/research/walk-register-gate2-348-2026-08-14.md
  Assert #2 (register):   N/A (cross-repo — governance/ is a subdirectory with a separate git root)
```

The bellows plans' registers live cross-repo at `governance/knowledge/research/`, so assert #2's register arm returns N/A even when the register exists and is committed. The scratchpad cycles (this session's drafts) committed nothing per walk → both arms return N/A.

**The gap:** auto-advance over N/A asserts is indistinguishable from fabrication. An N/A assert means the substrate is absent — the machinery that would catch a fabricated walk (register coherence, uncommitted-walk detection, fold_check baseline) is not running. The substrate must be PRESENT and the asserts non-N/A before auto-advance is licensed.

---

## Q3 — The Doctrine Amendment (two surfaces) + Rule 27 Gap Table

### The amendment: what it adds, what it does NOT re-mandate

The amendment ADDS a §2 cadence clause. It does NOT re-mandate the committed substrate — that is already mandated by:
- §2.7:160 — per-phase + per-LENS commits
- §3:210 — walk register committed per phase to `governance/knowledge/research/`
- §2.6:133 — record-coherence: register rows ↔ per-phase commits

The amendment NOTES the substrate as an existing dependency to ADOPT in practice (I1). It mandates only the cadence change and the memory rewrite.

### §2 insertion point

Pin: `DRAFTING_CYCLE.md` v2.12 (2026-08-19), line 38.

The cadence clause inserts as a new paragraph after §2's opening paragraph (`:38`, "Walk the lenses **in order, one pass per lens per walk.**…"), BEFORE the doneness-bar paragraph (`:40`, "**The cycle is DONE when…**"). This is the cadence region of §2 — the clause governs WHEN the Planner advances between walks, which is cadence, not bar.

### The cadence clause (draft text for the amendment to refine)

> **Auto-advance cadence.** After each walk's final per-lens commit, run `cycle_check.run_check` against the plan. On `CONTINUE`, auto-run walk N+1 — provided (a) the committed substrate is present (all three asserts report PASS, never N/A — see below), and (b) the Planner has surfaced no §2.0 direction-class finding. On `BAR_MET`, run the mandatory closing-record re-read (§2.7), then close and emit the manifest (`cycle_check --emit-manifest`). On `ESCALATE:*`, PAUSE for the CEO; a one-word resume runs the next walk. **Auto-advance applies from walk 2 onward** — walk 0 (context pin) + walk 1 + the §2.0 direction verdict remain the Planner's manual entry gate. **The substrate-presence precondition is hard:** when the committed register is absent, the `**Walk register:**` line is missing, or any assert returns N/A, the loop falls back to manual one-pass-per-turn cadence (the Planner awaits CEO direction between walks). This is the exact guard `[[no-fabricated-drafting-cycle]]` encodes, mechanized: N/A asserts mean the machinery that would catch a fabricated walk is not running.

### Memory rewrite (the second surface)

| Memory slug | Current state | Proposed state |
|---|---|---|
| `drafting-cycle-one-pass-per-turn` | "Write draft 1, then STOP and wait for the CEO to direct each analysis pass." SUPERSEDED annotation at bottom re cadence refinement. | Rewrite to: the per-walk CEO directive is replaced by auto-advance on `cycle_check=CONTINUE` + substrate present + no direction finding. The sequential-fold discipline and per-lens commit are UNCHANGED. The per-lens PAUSE is already removed (cadence refinement 2026-08-15). The memory records the history and points at the §2 cadence clause as the canonical source. |
| `no-fabricated-drafting-cycle` | "NEVER write a Drafting Cycle section that claims walks I didn't actually run." | Rewrite to: auto-advance is NOT fabrication WHEN the substrate is present (asserts #1/#2/#3 all PASS). The memory retains the fabrication prohibition and points at the §2 cadence clause's substrate-presence precondition as the mechanized form. Falls back to manual when substrate is absent. |
| `drafting-walk-phases-separated-by-turn` | "The control is the FOLD ORDER, not the turn split." | Rewrite to: the fold-order control is UNCHANGED. The turn boundary that was already superseded (2026-08-10) is now formally replaced by the auto-advance cadence. The sequential-fold rule (§2.7) is the invariant; the cadence clause governs when the Planner advances between walks. |

### Cross-repo atomicity

The §2 clause (in `DRAFTING_CYCLE.md` at `/Users/marklehn/Developer/GitHub/DRAFTING_CYCLE.md`, the governance root) and the memory rewrite (in the Planner memory repo at `/Users/marklehn/.claude/projects/-Users-marklehn-Developer-GitHub/memory/`) are a CROSS-REPO ATOMIC pair. They MUST ship together — a half-applied amendment leaves doctrine saying auto-advance while memory says stop-each-turn, a direct contradiction. The memory rewrite is CEO-authorized (the capstone is CEO-formalized per §11), not a Planner-unilateral change.

### Compaction/subsumption

The §2 clause ADDS the auto-advance cadence. It REMOVES no live §2 rule:
- The doneness bar (`:40`) is unchanged — the bar is what CLOSES the cycle, not what advances between walks.
- The sequential-fold rule (§2.7:155) is unchanged — auto-advance governs BETWEEN walks, sequential folding governs WITHIN a walk.
- Per-lens commits (§2.7:160) are unchanged — the substrate-presence precondition DEPENDS on them.
- The closing-record re-read (§2.7:144) is unchanged — the BAR_MET→close path preserves it.

### Version bump + History row

Version: 2.12 → 2.13. History row pattern follows 2.12 (CEO-authorized direct amendment, declared §6 deviation).

### §6 coordinate-doctrine-and-gate

`cycle_check` already IS the gate — no new gate code, no `plan_lint` change, no `gates.py` change. The amendment is §2 prose only. This is unlike a §1/§4 change which would pair with a `plan_lint` edit.

### Rule 27 Gap Table

| Gap | Current State | Proposed State | Change Required |
|---|---|---|---|
| **§2 auto-advance cadence** | No cadence clause in §2. The Planner awaits CEO direction between walks (memory-encoded, not doctrine-encoded). CEO's cadence refinement (2026-08-15) removed per-lens pause but left per-walk pause. | §2 cadence clause (draft above) at `:38–39` insertion point: auto-advance from walk 2 on `CONTINUE` + substrate present + no direction finding; manual fallback when substrate absent; BAR_MET → re-read → close; ESCALATE → CEO pause. | In-place §2 edit (governance root, like 2a). T-6 governance surface → T2 cycle with cold panel. |
| **Memory: `drafting-cycle-one-pass-per-turn`** | "STOP and wait for CEO to direct each analysis pass." With 2026-08-15 cadence refinement annotation. | Rewritten to point at §2 cadence clause. Per-walk CEO directive replaced by auto-advance. History preserved. | Planner memory rewrite (cross-repo, shipped atomically with §2 clause). CEO-authorized per §11. |
| **Memory: `no-fabricated-drafting-cycle`** | "NEVER write a Drafting Cycle section that claims walks I didn't actually run." | Auto-advance is not fabrication when substrate is present (asserts PASS). Fabrication prohibition retained. Manual fallback when substrate absent. | Planner memory rewrite (cross-repo, shipped atomically). CEO-authorized per §11. |
| **Memory: `drafting-walk-phases-separated-by-turn`** | "The control is the FOLD ORDER, not the turn split." Already superseded the turn-boundary framing. | Rewritten to name auto-advance as the formal replacement. Fold-order control unchanged. | Planner memory rewrite (cross-repo, shipped atomically). CEO-authorized per §11. |
| **§6 gate coordination** | `cycle_check` is the mechanical gate. `plan_lint` checks structure. | No change — `cycle_check` already emits the verdicts the loop uses; no new gate code. | None. Note in the History row. |
| **Version** | 2.12 (2026-08-19) | 2.13 | Version bump + History row. |
| **Substrate adoption** | §2.7/§3 mandate the committed register + per-lens commits. Practice: scratchpad cycles skip them → asserts N/A. | No re-mandate (I1). The cadence clause's substrate-presence precondition makes adoption LOAD-BEARING: without the substrate, auto-advance is unavailable. | Practice change, not doctrine change. Early cycles that don't produce a committed register stay manual. |

---

## Q4 — The ESCALATE/pause Contract

### ESCALATE reasons → CEO pauses

Every `ESCALATE:*` verdict (`scripts/cycle_check.py:357–414`) pauses the loop for the CEO:

| ESCALATE reason | cycle_check line | What triggered it | CEO action |
|---|---|---|---|
| `unparseable` | `:357, :363` | DC block missing or lens lines all unparseable | Fix the record, resume |
| `assert-fail:1` | `:377` | Arithmetic mismatch (instruction + record ≠ fold count) | Fix the count, resume |
| `assert-fail:2` | `:379` | Walk register referenced but not found in repo | Commit the register, resume |
| `assert-fail:3` | `:381` | Fold_check baseline missing with git context | Create/commit the baseline, resume |
| `uncommitted-walk` | `:383` | Fewer walk-commits than walks claimed | Commit the uncommitted walk, resume |
| `restructuring-fold` | `:388` | Current walk contains a restructuring fold | The convergence clock resets (§2); CEO decides next walk |
| `yield-rising` | `:394` | Current walk's instruction count > prior walk's | A rising yield is a non-convergence signal; CEO assesses |
| `plateau` | `:398` | 3+ consecutive walks at flat instruction count, no new lens | A flat plateau with no new class; CEO decides (end/restructure) |
| `claimed-close-unmet` | `:414` | Plan claims closure but cycle_check sees CONTINUE, not BAR_MET | A premature close claim; CEO investigates |

### §2.0 forcing findings that pause WITHOUT a cycle_check flag

Three findings FORCE a pause even on a `CONTINUE` verdict — `cycle_check` cannot detect them because they are semantic, not structural:

1. **Invalidated clone-origin / precedent** — the plan's clone origin or the precedent it inherits from is wrong.
2. **Invalidated mechanism** — the mechanism by which the plan's edits act is wrong.
3. **Invalidated scope premise** — a premise that licenses the plan's scope is wrong.

These are §2.0 DIRECTION findings, not folds. The Planner surfaces them as a pause ("I found a direction-class finding; pausing for CEO direction") even though `cycle_check` returned `CONTINUE`.

### CEO resume

One word ("continue" / "go" / "resume") → the Planner runs the next walk. The resume mechanism is unchanged from today's manual cadence — the CEO already resumes after inspecting an ESCALATE or a direction finding.

### RE-DRAFT reconciliation

RE-DRAFT is a Planner direction verdict (§2.0), NOT a cycle_check state. `cycle_check` has no state for RE-DRAFT — it reads arithmetic and structure, not direction judgments.

The loop surfaces RE-DRAFT as follows: the Planner issues a RE-DRAFT verdict after walk 1 (the direction verdict is part of the entry gate, which is manual). The cycle ENDS here without a deposit. Since auto-advance doesn't begin until after a PROCEED verdict at the end of walk 1, RE-DRAFT is structurally outside the auto-advance region — it can never conflict with the loop.

### The runaway backstop

**The gap:** `check_plateau` (`scripts/cycle_check.py:326–344`) catches FLAT instruction counts — 3+ consecutive walks at the same count with no new finding class. But an OSCILLATING count (e.g. 3, 2, 3, 2, …) never plateaus mechanically: `check_plateau` counts backwards from the current walk and breaks at the first walk with a different instruction count (`if instr != current_instr: break`, `:335`). An oscillating series resets the consecutive counter every other walk → `consecutive` never reaches 3 → `ESCALATE:plateau` never fires.

A pure cycle_check-follower loop could auto-advance indefinitely on `CONTINUE` with an oscillating count. "No cost escalation" means cycle_check won't stop it.

**The backstop:** §2.8's oscillation signal ("If the same region keeps being re-folded across walks, or the per-lens instruction-class count stops trending toward zero, take that as the prompt to step back and joint-resolve or escalate") is a PLANNER judgment, not a cycle_check state. The Planner-side pause (Q1, Guard 1) is the backstop: the Planner recognizes oscillation as a direction-class signal and pauses for the CEO, even on a `CONTINUE` verdict.

The amendment must NAME this: the loop is cycle_check-gated for the mechanical signals (plateau, rising yield, assert failures) and Planner-gated for the semantic signals (direction findings, oscillation). The loop is not a runaway-prone pure-mechanical follower because the Planner retains judgment authority.

---

## Q5 — Cold-Read Automation

### Trigger conditions (from §2.6, `DRAFTING_CYCLE.md:103–137`)

Cold panels fire at three codified triggers:

1. **The lens-4 consecutive-pre-existing signal** (§2.6:104): "do not keep walking while lens 4 still returns pre-existing findings on consecutive walks; that is the signal to spend the panel now." An early-fired panel discharges the panel obligation; the cycle still closes only on a fully dry walk.

2. **The T2 walk-0 scout** (§2.0:62): "On T2, walk 0 also convenes ONE cold scout seat." Runs BEFORE lens 1.

3. **The bar-met panel** (§2.6:103): Once the sequential walk meets §2's bar — dry or judged stop with residue enumerated — the cold panel convenes. "The panel is not waived by a judged stop."

### How the loop auto-convenes them

Today: the CEO says "go"/"proceed" to authorize each panel convene. The capstone makes that automatic at the trigger — when the trigger condition is met, the Planner convenes the panel under the `[[autonomous-panel-grant]]` authorization (all seats sequential in one turn, findings author-verified between seats, one complete report).

The panel's own findings re-open the walk on the same terms as any other lens pass — the Planner folds them, commits per seat, and the loop continues (cycle_check on the post-panel state).

### Autonomous cost profile

**The loop's autonomous token spend must be surfaced.** Auto-convening a cold panel is a MATERIAL spend:
- The standing baseline: 563k tokens / 45 findings (§2.6:133)
- Component 3's full-form panel: ~255k tokens
- The small-form panel (scout + EXECUTION + CAPSTONE): lower but still significant

The `[[autonomous-panel-grant]]` authorizes this spend. "No cost escalation" means cycle_check won't pause on token cost — it has no token-cost state. The amendment must state that the loop spends panel-scale tokens without asking, so the CEO knows the loop's autonomous cost profile. The grant is bounded to the panel; the confirming closes after the panel are outside the grant unless separately authorized.

---

## Q6 — The Fabrication-Safety Analysis (LOAD-BEARING)

### Fabrication paths and their closures

| Fabrication path | How the substrate + cycle_check closes it |
|---|---|
| **A walk recorded but not run** (walks written as prose without genuine lens passes — the [[no-fabricated-drafting-cycle]] breach) | Assert #2's git-commit arm: fewer walk-commits than walks claimed → `ESCALATE:uncommitted-walk` (`:383`). Per-lens commits (§2.7:160) make each lens provable from the commit history. The register carries per-lens/per-walk fold rows with `pre_fold_text` — verbatim bytes the fold replaced, not a paraphrase. |
| **A fold claimed but not applied** (a finding recorded in the register but the draft unchanged) | Assert #3: `fold_check` baseline (`:292–302`). The baseline captures the pre-fold machine-readable state; a post-fold re-run catches a fold that changed nothing. Per-fold `fold_check` (§2.7:142) is the within-walk guard. |
| **Arithmetic inconsistency** (fold counts that don't add up — a fabricated walk is sloppy) | Assert #1: instruction + record ≠ fold count → `ESCALATE:assert-fail:1` (`:377`). |
| **A close claimed but unearned** (plan claims closure but bar not met) | `claimed-close-unmet` (`:413–414`): plan claims closure (`**Closing:**` / `CLOSED` / `CYCLE COMPLETE`) but cycle_check sees CONTINUE, not BAR_MET → `ESCALATE:claimed-close-unmet`. |
| **Sequential folding violated** (batched lenses against one draft) | Per-lens commits (§2.7:160) make sequential execution provable — one commit per lens. The register's per-walk fold rows carry the walk and lens identity. |

### The BAR_MET → close path preserves the closing-record re-read

On `BAR_MET` the loop does NOT auto-close. The sequence is:

1. `cycle_check` returns `BAR_MET` (exit 0)
2. The Planner runs the MANDATORY closing-record re-read (§2.7:144) — re-reads the Closing line, per-lens summary lines, and status header adversarially against the artifact
3. If the re-read finds defects → fold them (record-class by the bar's own condition), re-run cycle_check → the re-read's folds may change the verdict
4. If the re-read is dry → close + `cycle_check --emit-manifest`

This session's closing re-reads caught real defects at EVERY close:
- A w2 yield miscount
- Lagging per-lens tallies
- A self-refuted panel premise

A false-BAR_MET (record decay making the artifact look drier than it is) or record-decay defect must not auto-ship. The closing re-read is a Planner cognitive gate the loop preserves between BAR_MET and close.

### The single invariant

**Auto-advance is licensed ONLY when the substrate is present and asserts #1/#2/#3 are all PASS (never N/A).**

An N/A assert means the substrate is absent → the machinery that would catch a fabricated walk is not running → the loop MUST NOT auto-advance. Fall back to manual one-pass-per-turn cadence.

This is the exact guard `[[no-fabricated-drafting-cycle]]` encodes, mechanized:
- Today: "NEVER write a Drafting Cycle section that claims walks I didn't actually run" — a behavioral prohibition enforced by the CEO's presence.
- Capstone: the committed substrate + non-N/A asserts make each walk's genuineness PROVABLE, and `cycle_check` verifies it mechanically. The CEO's presence is replaced by the substrate's presence.

**Recommendation:** the amendment makes the substrate-presence a HARD precondition of auto-advance. Not advisory, not best-practice — hard. The fallback to manual is explicit and automatic.

### The positive corollary: crash-recovery

The committed substrate doubles as CRASH-RECOVERY. A loop that dies mid-cycle (session termination, process crash, timeout) resumes from the last committed walk: `cycle_check` reads the committed state (the register's walk rows, the per-lens commits, the fold_check baseline), and the Planner picks up from the last completed walk. The substrate is both the non-fabrication guard AND the resumability mechanism.

---

## Q7 — Sequencing + Adoption

### Arc position

The capstone is the arc's LAST component (component 4 of 4, per proposal §11):
1. **Component 1 — cycle_check** (the mechanical gate): shipped, live, dogfooded every walk this session.
2. **Component 2 — cycle manifest** (2a: §2 manifest governance; 2b: `--emit-manifest` + `plan_lint` stanza check): shipped.
3. **Component 3 — depositor** (in-bellows depositor + dashboard DEPOSITS panel): shipped (plan 481, 2026-08-20).
4. **Component 4 — capstone** (self-driving walk loop): this diagnostic's subject.

Ships AFTER component 3 (per §11, now done).

### Adoption

Adoption is a cadence change the Planner practices from the next cycle. Dogfood like cycle_check was: the first cycles under the amendment run the auto-advance cadence with the Planner reporting to the CEO what it would have done (auto-advanced / paused / closed), and the CEO confirming or overriding. Once validated, the CEO stops confirming.

The substrate-presence precondition means adoption is GRADUAL: early cycles that don't yet produce a committed register stay manual until they do. The amendment does not flip every cycle to auto-advance overnight — it gates auto-advance on the substrate being real.

### The loop → depositor handoff

The arc's four components connect end-to-end:

1. **cycle_check** gates each walk (CONTINUE / ESCALATE / BAR_MET)
2. **BAR_MET** → close → `--emit-manifest` produces the manifest-bearing plan
3. **The depositor** (component 3) reads the manifest, stages the plan, runs validation re-checks (`cycle_check=BAR_MET`, `plan_lint=0_FAIL`), and clears/holds based on the `class:` field and collision queries
4. **The self-driving loop** (this capstone) replaces the CEO's per-walk "continue" with auto-advance gated on cycle_check + substrate

The Planner runs the loop; the depositor processes its output. The CEO is notified on ESCALATE (pause) and at deposit (completion) — per the existing Pushover notification pattern.

### Amendment tier

The amendment is a **T-6 §2 governance surface** (edits doctrine, specifically the cadence of the Drafting Cycle's Lens Register). T-6 triggers T2 → the amendment earns a cold-panel cycle.

---

## Appendix: Live cycle_check Assert Demonstration

Run against the committed corpus to show the N/A state that gates the loop:

```
REGISTER-LESS plan (bellows/executable-439):
  Walk register ref: None
  Assert #1 (arithmetic): N/A
  Assert #2 (register):   N/A
  Assert #3 (fold_check): N/A
  → All asserts N/A → substrate absent → auto-advance NOT licensed

REGISTER CROSS-REPO plan (bellows/executable-418):
  Walk register ref: governance/knowledge/research/walk-register-gate2-348-2026-08-14.md
  Assert #2 (register):   N/A (cross-repo ref → unreachable from plan's git root)
  → Substrate effectively absent for the auto-advance gate
```

The N/A→PASS transition requires:
1. A `**Walk register:**` ref pointing to a path WITHIN the plan's own git root
2. The referenced register file existing and committed
3. Per-walk commits of both register and draft (git-commit arm active)
4. A `fold_check` baseline (assert #3)

When all four are present, the asserts report PASS and the substrate is confirmed — auto-advance is licensed. When any is absent, one or more asserts report N/A → manual fallback.
