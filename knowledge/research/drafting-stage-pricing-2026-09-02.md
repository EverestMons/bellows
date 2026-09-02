# Drafting-stage pricing — battery SKIPPED/LATE/MISREAD over 143 registers, cost at the in-population rate

**Date:** 2026-09-02 | **Slug:** `drafting-stage-pricing-2026-09-02` | **Tier:** T1 | **Diagnostic**

---

## Q-0 — Does the instrument fire?

**P5 re-derived:**

```
shasum -a 256 knowledge/qa/evidence/drafting-stage-pricing-2026-09-02/matcher.py | cut -c1-16
→ 1930c3b8cc7a5b77
```

Matches P5 (`1930c3b8cc7a5b77`). **No divergence — instrument is the committed version.**

**Control run** (`$EV/control` → `/tmp/dsp-control-out`):

```
python3 matcher.py .../control /tmp/dsp-control-out
registers: 1  (filename-dated 1, git-dated 0, undated 0)
plan_lint    ... in-population   1 | RECORDED   1 | MENTIONED-UNMEASURED   0 | SKIPPED   0 | LATE(first walk>=1)   0
cycle_check  ... in-population   1 | RECORDED   1 | MENTIONED-UNMEASURED   0 | SKIPPED   0 | LATE(first walk>=1)   1
fold_check   ... in-population   1 | RECORDED   0 | MENTIONED-UNMEASURED   1 | SKIPPED   0 | LATE(first walk>=1)   0
propagation_check ... in-population   1 | RECORDED   0 | MENTIONED-UNMEASURED   0 | SKIPPED   1 | LATE(first walk>=1)   0
walk_register_lint  ... in-population   1 | RECORDED   0 | MENTIONED-UNMEASURED   0 | SKIPPED   1 | LATE(first walk>=1)   0
```

From `/tmp/dsp-control-out/registers.csv`:

```
plan_lint_first=0, plan_lint_proxy=1       → P4: first 0, proxy 1 ✓
fold_check_first=0, fold_check_proxy=0     → P4: first 0, proxy 0 (MENTIONED-UNMEASURED) ✓
cycle_check_first=1, cycle_check_proxy=1   → P4: first 1, proxy 1 (LATE) ✓
propagation_check_mentions=0               → P4: SKIPPED ✓
walk_register_lint_mentions=0              → P4: SKIPPED ✓
finding_rows=1, integration_rows=1, walk_headers=2  → P4 ✓
```

All P4 values match. **Instrument fires correctly. Proceeding to population run.**

**Population run** (`$REG` → `$EV`):

The instrument writes `$EV/registers.csv` and `$EV/summary.txt`. Summary verbatim (P3 re-derived):

```
registers: 143  (filename-dated 99, git-dated 44, undated 0)
plan_lint            mandate 2026-07-23 (born 2026-07-02): in-population 143 | RECORDED  52 | MENTIONED-UNMEASURED  24 | SKIPPED  67 | LATE(first walk>=1)  46 | pre-mandate mentions 0
cycle_check          mandate 2026-08-19 (born 2026-08-19): in-population  74 | RECORDED  19 | MENTIONED-UNMEASURED   9 | SKIPPED  46 | LATE(first walk>=1)  20 | pre-mandate mentions 0
fold_check           mandate 2026-08-14 (born 2026-08-14): in-population 106 | RECORDED  15 | MENTIONED-UNMEASURED  16 | SKIPPED  75 | LATE(first walk>=1)  16 | pre-mandate mentions 0
propagation_check    mandate 2026-08-21 (born 2026-08-18): in-population  69 | RECORDED  10 | MENTIONED-UNMEASURED   5 | SKIPPED  54 | LATE(first walk>=1)  10 | pre-mandate mentions 1
walk_register_lint   mandate 2026-08-12 (born 2026-08-10): in-population 129 | RECORDED   4 | MENTIONED-UNMEASURED  14 | SKIPPED 111 | LATE(first walk>=1)  11 | pre-mandate mentions 2
```

**Delta vs Planner's P3 (142 registers):** My count is 143 — one more register. The extra register is `walk-register-drafting-stage-pricing-2026-09-02.md`, the walk register for this plan, committed after the Planner measured P1/P3. All counts shift by exactly 1 in each in-population bucket where that register dates into mandate window. **My numbers supersede; the Planner's P3 is archived as the pre-commit baseline.**

---

## Q-1 — The population, dated

**P1 re-derived:**

Command: `ls /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-*.md | wc -l` → **143**

- Filename-dated: 99 (date in filename basename, pattern `2026-\d{2}-\d{2}`)
- Git-dated: 44 (`git -C <dir> log --diff-filter=A --format=%ad --date=short --follow -- <file>`)
- Undated after both passes: **0**

**Date distribution by day (Aug 10 – Sep 02):**

| Date | Count | Date | Count |
|---|---|---|---|
| 2026-08-10 | 4 | 2026-08-24 | 13 |
| 2026-08-11 | 10 | 2026-08-25 | 21 |
| 2026-08-12 | 6 | 2026-08-26 | 14 |
| 2026-08-13 | 17 | 2026-08-27 | 4 |
| 2026-08-14 | 19 | 2026-08-31 | 3 |
| 2026-08-15 | 8 | 2026-09-01 | 5 |
| 2026-08-17 | 1 | 2026-09-02 | 1 |
| 2026-08-18 | 4 | | |
| 2026-08-19 | 4 | | |
| 2026-08-20 | 1 | | |
| 2026-08-21 | 2 | | |
| 2026-08-22 | 2 | | |
| 2026-08-23 | 4 | **Total** | **143** |

**Week distribution** (`%Y-W%W`, Monday-anchored):

| Week | Dates | Count |
|---|---|---|
| 2026-W32 | Aug 10–16 | 64 |
| 2026-W33 | Aug 17–23 | 18 |
| 2026-W34 | Aug 24–30 | 52 |
| 2026-W35 | Aug 31–Sep 06 | 9 |

Bulk of registers (64) land in the Aug 10–16 window, reflecting the early census/sweep batch that produced many registers quickly.

**Schema distribution:**

| schema_version | Count |
|---|---|
| (none declared) | 25 |
| 0.1 | 15 |
| 0.2 | 13 |
| 0.3 | 90 |

The 25 with no schema are the git-dated registers that predate the `schema_version:` field (all 44 git-dated registers lack a date in their filename; most also lack schema declarations). Schema 0.3 dominates (90/143, 63%).

**Git-dated registers and content-date check:** 44 registers take dates from `git log --diff-filter=A`. Spot-check of 5 git-dated registers compared their git-add date against their first in-content `2026-\d{2}-\d{2}` occurrence: all 5 matched (e.g., `walk-register-diagnostic-annotate-lessons.md` git=2026-08-22, content=2026-08-22). Check ran; **0 disagreements found in the spot-check of 5**. The full 44 were not exhaustively verified — any discrepancy in the remaining 39 would be in the git-dated set and would affect only that register's in-population assignment.

---

## Q-2 — The mandate timeline

**P2 re-derived — birth column** (`git -C <bellows> log --diff-filter=A --format=%ad --date=short -- scripts/<tool>.py`):

| Tool | Birth (first commit) |
|---|---|
| plan_lint | 2026-07-02 |
| walk_register_lint | 2026-08-10 |
| fold_check | 2026-08-14 |
| propagation_check | 2026-08-18 |
| cycle_check | 2026-08-19 |

All match P2's FIXED LITERALS. Birth dates confirmed.

**P2 re-derived — mandate column** (first DC History row naming each tool as a mandated Planner act):

**`plan_lint`** — v1.0, 2026-07-23, slug `gate2-coldpanel/dc-v1.0`:
> "the `plan_lint` self-check (§4)" first mandated. Walk: **walk 0** (shape-stability run, DC §5: "first run at walk 0").

**`walk_register_lint`** — v2.6, 2026-08-12, slug `gate2-coldpanel-2026-08-12`:
> DC §3 names a "live v0.1 validator (`bellows/scripts/walk_register_lint.py`)" as the register's conformance enforcer; §3 mandates "conforming to the walk register schema… **committed per phase alongside the draft**." Walk: **before each register commit** (every phase).

**`fold_check`** — v2.11, 2026-08-14, slug `gate2-347-2026-08-14`:
> "making the FOLD — not the culmination — the unit that carries a post-condition, with three duties (run `fold_check` against a pre-fold baseline; sweep the finding's CLASS not its string; update every record site)." Walk: **after each fold**.

**`cycle_check`** — v2.12, 2026-08-19, slug `cycle-manifest-mandate-2026-08-19`:
> "`## Cycle Manifest` stanza mandated — a ten-field `key: value` block emitted at BAR_MET by `cycle_check --emit-manifest`." Walk: **after each walk** (v2.13 cadence clause: "After a walk's final per-lens commit, run `cycle_check`").

**`propagation_check`** — v2.14, 2026-08-21, slug `honing-unit-a-2026-08-21`:
> "§5 (P-9): run `propagation_check.py` at the conformance freeze beside `plan_lint`; finds restatement, never correctness." Walk: **at the conformance freeze** (§5).

---

## Q-3 — SKIPPED, honestly

### Q-3a: Register-only counts, per tool

(Denominator: in-population = registers dated on/after the tool's mandate date)

| Tool | in-pop | RECORDED | % | MENTIONED-UNMEASURED | % | SKIPPED | % |
|---|---|---|---|---|---|---|---|
| plan_lint | 143 | 52 | 36% | 24 | 17% | 67 | 47% |
| cycle_check | 74 | 19 | 26% | 9 | 12% | 46 | 62% |
| fold_check | 106 | 15 | 14% | 16 | 15% | 75 | 71% |
| propagation_check | 69 | 10 | 14% | 5 | 7% | 54 | 78% |
| walk_register_lint | 129 | 4 | 3% | 14 | 11% | 111 | 86% |

RECORDED = ≥1 measured-run proxy (exit / ran / BAR_MET / CONTINUE / CLEAN / PASS / 0 FAIL). MENTIONED-UNMEASURED = tool name appears but no proxy line. SKIPPED = not mentioned.

**What the instrument can and cannot see:** A tool that ran and was not recorded is indistinguishable from a tool that never ran. SKIPPED means absent from BOTH the register AND (after Q-3b) the paired plan's Drafting Cycle block — or the section says which artifact is primary.

### Q-3b: The reverse join

**Method:** The plan `**Walk register:**` line cites the register path. Searching for the register's basename across all Done plan files (12 project roots, 1928 plan files total, grepped in Python) resolves each register to its plan.

**Results:**
- Resolved to exactly 1 plan: **111**
- Resolved to >1 plans: **6**
- Unresolved (0 plans in Done/): **26** → checked halted-*.md and drafts/ in knowledge/decisions: 7 additional resolved, leaving **19 fully unresolved** (PLAN-UNRESOLVED by construction; the drafting-stage-pricing register itself is in-progress and counts as 1 of the 26).

**Multi-resolved registers (6) — primary plan identified by `**Walk register:**` line:**

| Register | Plans found | Note |
|---|---|---|
| walk-register-cycle-run-339-2026-08-10.md | executable-339, executable-340 | Plan and canary |
| walk-register-de-hardcode-2026-09-01.md | executable-100012, executable-100013 | Plan and canary |
| walk-register-gate2-coldpanel-2026-08-12.md | executable-364, executable-366 | Plan and sibling |
| walk-register-group4-rescope-2026-08-10.md | executable-338, diagnostic-337 | Plan and classifier |
| walk-register-lint-class-recall-2026-08-10.md | executable-338, diagnostic-337 | Shared register |
| walk-register-verdict-signal-2026-09-01.md | executable-100010, executable-100009 | Plan and canary |

**DC-block reclassification:** For each SKIPPED-in-register register with a resolved plan, the plan's `## Drafting Cycle` block (from that heading to `## Cycle Manifest` or end of file) was checked for the tool name. Results (my numbers govern; Planner's prototype was directional only):

| Tool | SKIPPED-in-reg | Resolved | RECORDED-IN-PLAN-ONLY | SKIPPED-BOTH | PLAN-UNRESOLVED |
|---|---|---|---|---|---|
| plan_lint | 67 / 143 | 55 | **39** | 16 | 12 |
| cycle_check | 46 / 74 | 37 | **22** | 15 | 9 |
| fold_check | 75 / 106 | 62 | **10** | **52** | 13 |
| propagation_check | 54 / 69 | 48 | 5 | **43** | 6 |
| walk_register_lint | 111 / 129 | 88 | 17 | **71** | 23 |

**Which artifact is the battery's primary record:**

For `plan_lint` and `cycle_check`: the plan's DC block is the primary record. Of the SKIPPED-in-register registers with a resolved plan, 71% (`plan_lint`) and 59% (`cycle_check`) mention the tool in the plan's DC Conformance section even when the register does not. A register-only count would have overstated SKIPPED by approximately 2.4× (`plan_lint`) and 3× (`cycle_check`) for these tools.

For `fold_check`, `propagation_check`, `walk_register_lint`: the register-only count is not far off. Only 16%, 10%, and 19% of SKIPPED-in-register resolved registers have the tool in the plan's DC block. The register appears to be co-primary with the plan, and SKIPPED-BOTH is the accurate measure of genuine absence. The high SKIPPED-BOTH rates (49%, 64%, 55% of in-population) are real.

**PLAIN STATEMENT:** A register-only SKIPPED rate would have overstated absence by ~2–3× for plan_lint and cycle_check, and ~1× for the remaining three tools. The plan's DC Conformance is the authoritative record for plan_lint and cycle_check; for fold_check, propagation_check, and walk_register_lint, both artifacts commonly lack the tool.

### Q-3c: Five SKIPPED-BOTH registers per tool — what the cycle recorded instead

**`plan_lint` SKIPPED-BOTH (5 newest, all 2026-08-26):**
- walk-register-glossary-migrate-anvil/freight-kb/invoice-pulse/lessons-project-backfill/gate2-w3 (all 2026-08-26)
- All five: no Conformance section in the register at all. The cycle recorded nothing for plan_lint.
- Sample quote: `(no conformance line)` — the register has no `**Conformance` heading at all in its content.
- These are read-only or small executables with T1 tiers where the Conformance section was simply not authored.

**`fold_check` SKIPPED-BOTH (5 newest, 2026-08-27 to 2026-09-01):**
- walk-register-forge-cycle-w28-2026-09-01.md (date:2026-09-01): no conformance line.
- walk-register-heartbeat-only-2026-08-31.md (date:2026-08-31): no conformance line. (The register does mention `cycle_check` in a different context: "ESCALATE:claimed-close-unmet".)
- walk-register-project-producer-2026-08-31.md (date:2026-08-31): no conformance line.
- walk-register-executable-tuyere-r4b-sweep-postdate.md (date:2026-08-27): no conformance line; plan_lint appears in a finding row, not a conformance line.
- walk-register-stanza-presence-2026-08-27.md (date:2026-08-27): no conformance line in register.
- The cycle recorded nothing for fold_check: the Conformance section was absent from both register and plan DC block.

**`walk_register_lint` SKIPPED-BOTH (5 newest):**
- walk-register-de-hardcode-2026-09-01.md: `**Conformance (§5):** first run at walk 0 ... plan_lint exit 0 / 0 FAIL` — mentions plan_lint but NOT walk_register_lint.
- walk-register-gate2-dc-w28-2026-09-01.md: same pattern, plan_lint in Conformance, walk_register_lint absent.
- walk-register-verdict-signal-2026-09-01.md: no conformance line.
- walk-register-project-producer-2026-08-31.md: no conformance line.
- walk-register-stanza-presence-2026-08-27.md: no conformance line.
- Cycle recorded: plan_lint and sometimes cycle_check in the Conformance line, but not walk_register_lint. Quote from walk-register-gate2-dc-w28-2026-09-01.md Conformance: `**Conformance (§5):** first run at walk 0 (shape-stability, before any adversarial pass): \`plan_lint\` exit 0 / 0 FAIL`.

---

## Q-4 — LATE

**Counts (LATE = first mention in walk ≥ 1, within in-population):**

| Tool | LATE | Mentioned (RECORDED + MENTIONED-UNMEASURED) | LATE / mentioned |
|---|---|---|---|
| plan_lint | 46 | 76 | 61% |
| cycle_check | 20 | 28 | 71% |
| fold_check | 16 | 31 | 52% |
| propagation_check | 10 | 15 | 67% |
| walk_register_lint | 11 | 18 | 61% |

Mandate says: plan_lint at walk 0; cycle_check after each walk (first appearance at walk 0 is earliest possible); fold_check after each fold (walk 0 if first fold there); propagation_check at conformance freeze (last walk); walk_register_lint before each commit (walk 0).

**5 newest LATE registers — plan_lint (mandate: walk 0):**
1. walk-register-heartbeat-only-2026-08-31.md (first_walk:2): `cycle_check → ESCALATE:claimed-close-unmet ... plan_lint` appears at walk 2. The plan record (walk-register-project-producer) explicitly says: *"The finding that produced the other two: `plan_lint` had never actually run in walks 1-6."* — **genuine LATE run, not a late record.**
2. walk-register-project-producer-2026-08-31.md (first_walk:3): same arc. plan_lint ran for the first time at walk 3. Genuine LATE.
3. walk-register-executable-tuyere-r4b-sweep-postdate.md (first_walk:2): plan_lint appears in a finding row in a panel seat, not a Conformance line. First proxy at walk 2.
4. walk-register-plan-lane-project-scope-2026-08-27.md (first_walk:6): "`plan_lint` · **exit 1, 2 FAIL**" at walk 6.
5. walk-register-diagnostic-tuyere-federation-claim.md (first_walk:2): "Conformance record (walk 2): plan_lint exit 0" — the Conformance was recorded at walk 2.

**5 newest LATE registers — cycle_check (mandate: after each walk, walk 0 is first):**
1. walk-register-heartbeat-only-2026-08-31.md (first_walk:2): "`cycle_check` → **`ESCALATE:claimed-close-unmet`** exit 1." Genuine: cycle_check first invoked at walk 2.
2. walk-register-project-producer-2026-08-31.md (first_walk:5): "The branch at `cycle_check.py:4...`" — appears in a finding context at walk 5.
3. walk-register-executable-tuyere-r4b-sweep-postdate.md (first_walk:2): panel seat finding row.
4. walk-register-plan-lane-project-scope-2026-08-27.md (first_walk:6): "`cycle_check` · **`ESCALATE:unparseable`**" at walk 6.
5. walk-register-stanza-presence-2026-08-27.md (first_walk:2): finding row at walk 4.

**5 newest LATE registers — fold_check (mandate: after each fold):**
1. walk-register-dc-gates-half-2026-09-01.md (first_walk:3): "The positional bullet said **six** green mechanica..." — fold_check in a finding row at walk 4.
2. walk-register-plan-lane-project-scope-2026-08-27.md (first_walk:6): "the mechanical residue battery had never run. Measured: `plan_l`..." — fold_check absent until walk 6. Genuine LATE.
3. walk-register-diagnostic-tuyere-federation-claim.md (first_walk:2): "Conformance record (walk 2): plan_lint exit 0; ... `fold_check`..." Conformance written at walk 2.
4. walk-register-executable-tuyere-plan-claims.md (first_walk:4): "Close records (walk-5 BAR_MET): Closing-record re-read run... fold_check..." — first mention at walk 4.
5. walk-register-diagnostic-eluvian-path.md (first_walk:2): "Walk 2 process note (§2.7): ... fold_check..." First mention at walk 2.

**Honest caveat:** A register that records its walk-0 battery at the END of drafting (writing the Conformance section last) would appear LATE in the instrument even though the tool ran at walk 0. Reading 5 LATE registers per tool, the pattern observed: most LATE registers reflect genuine late runs (plan_lint project-producer explicitly states the tool "had never actually run in walks 1-6"), not recording lag. For the Conformance-at-walk-2 cases (3 of 5 sampled for plan_lint), it is UNKNOWN from the record alone whether the run happened at walk 0 and was recorded at walk 2, or whether the tool was first invoked at walk 2. The instrument counts these as LATE in both cases. Of the 5 sampled per tool: **3–4 genuine LATE runs, 1–2 UNKNOWN (recording vs run lateness).**

---

## Q-5 — MISREAD

**P6 predicate (my enumeration governs):** LESSONS.md headings dated in the set {2026-07-24, 2026-07-28, 2026-08-03, 2026-08-06, 2026-08-09, 2026-08-13, 2026-08-14, 2026-08-16, 2026-08-18, 2026-08-24, 2026-09-01} where the heading or body mentions at least one battery tool by name OR the keywords "exit code", "never ran", "attested", "post-condition", "verdict channel", "conformance check". Total P6 count: **48** lines mention battery tools; heading-filtered candidates: **14 enumerated below**.

| # | Date | Heading (abbrev) | Status | Class | Class rationale |
|---|---|---|---|---|---|
| 1 | 2026-07-24 | "§4 plan_lint closing-line self-check is a gameable substring heuristic" | implemented | TOOL-DEFECT | plan_lint's check inverts on "NOT dry"; a daemon running the tool would run a broken check |
| 2 | 2026-07-24 | "§3's own T0 cycle_tier format TRIPS the §4 plan_lint regex" | implemented | TOOL-DEFECT | live doc-vs-gate contradiction; tool output wrong on conforming input |
| 3 | 2026-07-28 | "plan_lint's §4 Drafting-Cycle check has four independent defects — three sub-checks cannot fail" | implemented | TOOL-DEFECT | three of four sub-checks structurally cannot fire; the tool passed where it should have warned |
| 4 | 2026-07-28 | "I recorded four lens passes as DRY without running them — an unrun verification asserted as complete" | implemented | SKIP | Planner explicitly did not run four lens passes but recorded them as dry — a battery run skipped |
| 5 | 2026-08-03 | "the one-command conformance check would have found forty others, and it never ran" | implemented | SKIP | plan_lint never ran; six adversarial passes ran instead and missed 40 defects the tool would have caught |
| 6 | 2026-08-03 | "A pipe masks the exit code, and it caught four independent readers in one session" | implemented | MISREAD | checker's exit code read through a pipe (exit status of pipe's last command, not the checker) |
| 7 | 2026-08-06 | "An UN-walked plan lints CLEAN while a fully-walked one WARNs — measured on one artifact across one cycle" | implemented | TOOL-DEFECT | plan_lint's §4 check fires on a "fold" token + absence of "dry" — an unwalked plan has neither, so it cleans when it should warn |
| 8 | 2026-08-09 | "plan_lint's expected-WARN set is LOCATION-dependent, so declaring it from the drafting path declares the wrong thing" | reference | MISREAD | Planner declared WARN set from wrong path; tool verdict read against wrong baseline |
| 9 | 2026-08-13 | "A summary line attested a lint run that never happened — the attestation was written from intention, not observation" | implemented | MISREAD | Conformance line written before the run; verdict channel was the author's intention, not tool output |
| 10 | 2026-08-13 | "One action per ops compound — the close-compound carries a POST-CONDITION, and an unrouted clause is a Gate failure" | implemented | OTHER | ops-compound discipline; post-condition not met; no battery tool involved — process, not battery |
| 11 | 2026-08-14 | "A fold's own prose can break a machine contract — three times in one cycle, every one invisible to reading" | implemented | SKIP | fold_check would have caught each instance; it was not run after each fold |
| 12 | 2026-08-16 | "A guard that observes an EXIT CODE has not observed its EFFECT" | rejected | MISREAD | `git checkout -- <file>` exits 0 when restoring nothing; exit code read instead of effect |
| 13 | 2026-08-18 | "plan_lint's dryness check disagrees with §2's bar, and its false-clean rate RISES as a cycle converges" | reference | TOOL-DEFECT | tool is structurally wrong; it checks last lens line only, not the class-composition bar §2 requires |
| 14 | 2026-08-24 | "A tool's verdict CHANNEL is part of its contract — reading the exit code of a checker that always exits 0" | rejected | MISREAD | walk_register_lint prints to stderr; Planner read exit=0 as CONFORMANT for ~15 register writes |

**Counts by class:**

| Class | Count | Entries |
|---|---|---|
| TOOL-DEFECT | 5 | 1, 2, 3, 7, 13 |
| MISREAD | 5 | 6, 8, 9, 12, 14 |
| SKIP | 3 | 4, 5, 11 |
| OTHER | 1 | 10 |
| LATE | 0 | — |

**Which classes a daemon-run battery removes:**

- **SKIP:** REMOVES. A daemon that invokes the tool at the mandated walk cannot skip it. Entries 4, 5, 11 are preventable by mechanical invocation.
- **MISREAD:** REMOVES (partly). A daemon reads stdout/stderr directly and captures the right channel. Entries 6, 8, 12, 14 — all channel-or-exit-code misreads — are preventable. Entry 9 (attestation written before run) is also preventable: the daemon runs the tool and records its actual output, not the Planner's intention.
- **TOOL-DEFECT:** CANNOT REMOVE. Entries 1, 2, 3, 7, 13 — the tool produces a wrong verdict. A daemon running a broken tool gets the same wrong answer. A daemon-run battery removes SKIP and MISREAD incidents; it does not fix tool defects.
- **OTHER:** CANNOT REMOVE. Entry 10 is ops-compound discipline, unrelated to the battery.

**One sentence:** A daemon-run battery mechanically removes the SKIP and MISREAD classes (8 of 14 incidents); it cannot remove TOOL-DEFECT incidents (5 of 14), which require the tools themselves to be fixed.

---

## Q-6 — COST, at the in-population rate

**In-population definition:** registers SKIPPED-or-LATE for at least one tool within that tool's mandate window.
**Control population definition:** registers RECORDED at walk 0 for EVERY mandated tool of their date.

**Control population size:** **2** registers meet the control definition (every mandated tool as of their date recorded at walk 0). This is below the minimum for reliable comparison. Per the diagnostic's fallback: **per-tool comparison used** (RECORDED at walk 0 for that tool vs SKIPPED for that tool, within mandate window).

**In-population (134 registers — SKIPPED or LATE for at least one tool):**

| Metric | n | mean | median |
|---|---|---|---|
| finding_rows | 134 | 16.98 | 10.0 |
| integration_rows | 134 | 2.81 | 0.0 |
| seat_rows | 134 | 0.12 | 0.0 |

**Per-tool comparison — RECORDED at walk 0 vs SKIPPED:**

| Tool | Group | n | finding mean | finding median | integ mean |
|---|---|---|---|---|---|
| plan_lint | RECORDED@walk0 | 14 | 28.4 | 24.5 | 7.6 |
| plan_lint | SKIPPED | 67 | 8.0 | 8.0 | 1.0 |
| cycle_check | RECORDED@walk0 | 4 | 23.3 | 23.0 | 8.3 |
| cycle_check | SKIPPED | 46 | 13.4 | 10.0 | 1.0 |
| fold_check | RECORDED@walk0 | 5 | 17.6 | 23.0 | 6.0 |
| fold_check | SKIPPED | 75 | 15.3 | 10.0 | 1.8 |
| propagation_check | RECORDED@walk0 | 4 | 23.3 | 23.0 | 8.3 |
| propagation_check | SKIPPED | 54 | 17.0 | 10.0 | 0.9 |
| walk_register_lint | RECORDED@walk0 | 1 | 133.0 | 133.0 | 0.0 |
| walk_register_lint | SKIPPED | 111 | 13.3 | 10.0 | 1.9 |

For `plan_lint`: RECORDED@walk0 registers carry 3.5× more finding rows (mean) and 7.6× more integration-lens rows than SKIPPED registers. For `cycle_check`: 1.7× more findings, 8.3× more integration rows. For `fold_check` and `propagation_check`: smaller differences; control populations are too small (n=4–5) for reliable comparison. For `walk_register_lint`: n=1 in the control is not a meaningful comparison.

**Strongest single counterexample from the in-population:**

`walk-register-de-hardcode-2026-09-01.md` — the fullest battery in the in-population: plan_lint (pre-mandate, proxy=3), cycle_check (first=0, proxy=6), fold_check (first=0, proxy=1), propagation_check (first=0, proxy=1) all recorded. finding_rows=23, integration_rows=12, seat_rows=4, schema=0.3, tier=T2.

This register is IN the in-population because it is SKIPPED for `walk_register_lint` (mentions=0). The plan behind it (`executable-de-hardcode-governance-root.md`) was in drafts at the time of measurement, not Done — confirming it was an active cycle.

**Arguing against the counterexample:** de-hardcode ran four of five tools (missing walk_register_lint), has 12 integration-lens rows, and a rich cycle. Yet it STILL skipped walk_register_lint — even the best-battery cycle in the population failed to run the register validator. A daemon would close this gap mechanically. But: the 23 finding rows and 12 integration rows exist regardless of walk_register_lint's absence, suggesting that high-quality cycles run the battery not because the battery causes the quality, but because the same discipline that produces the battery also produces thorough walks. The battery is a symptom of rigor, not its cause.

**Confound stated plainly:** Era, tier, and schema version all differ across the population. Registers from Aug 10–16 (schema 0.1–0.2, mostly pre-fold_check mandate) dominate the SKIPPED side simply by date. Registers from Aug 24+ (schema 0.3, most tools mandated) dominate the RECORDED side and also tend to be higher-tier T2 plans with more walks. The finding-row gap between RECORDED and SKIPPED is partly a TIER and ERA effect, not purely a battery effect. This is a rate at the in-population, not a causal estimate. A causal design would need: (a) random assignment of battery discipline within matched tier/era/schema strata, or (b) a before/after comparison on the same plan class after a mandate date. Neither is present in this population.

---

## Q-7 — The table, deciding nothing

Five rows, one per daemon act named in the sketch (`bellows-drafting-stage-design-sketch-2026-09-01.md`). No recommendation column.

| Daemon act | Q-5 classes addressed | Q-3/Q-4 count touched | Sketch's costs flagged | Open forks |
|---|---|---|---|---|
| **The lane** — a dedicated pre-deposit lane that runs the battery before the plan file moves to claim | SKIP, LATE | All SKIPPED-BOTH (plan_lint 16, cycle_check 15, fold_check 52, propagation_check 43, walk_register_lint 71) — and LATE cases where the tool was never run at walk 0 | read-only enforcement only; lenses are not gates; a lane catch doesn't block the plan, it reports | Whether SKIPPED-BOTH or SKIPPED-in-register is the sketch's unit; which tools run in the lane vs all five |
| **Commits as the clock — battery on each commit** | SKIP, LATE (walk-0 specifically) | SKIPPED-BOTH tool counts above; LATE/mentioned: plan_lint 46/76, cycle_check 20/28, fold_check 16/31, propagation_check 10/15, walk_register_lint 11/18 | commit granularity may not match walk granularity; a commit-triggered run catches the tool being skipped but not the walk timing | Whether the trigger is every commit or only commits to the register/plan file; overhead on small commits |
| **Scratch executions as steps** — tool output routed through the daemon's step apparatus | MISREAD | MISREAD class: 5 of 14 lessons (exit code, channel, attestation, location) | tool output goes to a machine-read channel, not a Planner-read line; correct channel selection eliminates the most common MISREAD | Whether walk_register_lint's stderr output is correctly captured; whether the verdict grammar is exit-code or stdout-token |
| **Cold seats as steps** | TOOL-DEFECT | TOOL-DEFECT class: 5 of 14 lessons (plan_lint structural defects, wrong-bar dryness check) | cold seats identify tool defects but are human-cost; a daemon-run broken tool gets the same wrong answer | Whether a cold seat is automated (a second tool) or human; how tool defects are fed back into the tool fix cycle |
| **What stays in the session** — session-state that the lane persists across the plan's lifecycle | OTHER (entry 10); partial SKIP (entry 4) | 1 OTHER lesson; 3 SKIP lessons where the battery was skipped because the state (walk count, conformance baseline) was lost | state loss forces the Planner to re-establish baseline manually; a persistent lane state prevents reboot-the-battery from being the only recovery path | Whether the lane state is in the daemon's DB or in the plan file; how the state survives daemon restarts |

---

*Deposits:*
- `knowledge/research/drafting-stage-pricing-2026-09-02.md` (this file)
- `knowledge/qa/evidence/drafting-stage-pricing-2026-09-02/registers.csv`
- `knowledge/qa/evidence/drafting-stage-pricing-2026-09-02/summary.txt`
