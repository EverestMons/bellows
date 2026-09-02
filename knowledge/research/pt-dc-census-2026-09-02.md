# PT/DC enforcement census — 2026-09-02

**Date:** 2026-09-02 | **Plan:** 100024 | **Template version:** PT v4.97 | **DC version:** v2.23
**Instrument:** `census.py` sha `9c52011935a17137` | **Population:** 228 units | **Code files scanned:** 56

---

## Q-0 — Does the instrument fire?

**P1 re-derived:** `shasum -a 256 census.py | cut -c1-16` → `9c52011935a17137` ✓ matches pin.

**Document shas:**
- PT: `f1701a37441868699b552a521dc2fda25d3cf713eb11c92df4fe0287ba40f1d3` — **Version: 4.97** (v4.97 expected; v4.96 pin `c471d3afee3f9094` belonged to the pre-gate2-pt-w28-a version)
- DC: `3a84137ed3669de1d690c4b22b57b158c3387792` — matches P3 pin

**Zero-population control:** `: > /tmp/ptdc-empty.md; census.py /tmp/ptdc-empty.md DC LESSONS scripts --out /tmp/ptdc-empty-out` → `ERROR: a population parsed to zero units: {'trigger': 8, 'lens-subquestion': 21, '2.7-bullet': 52} — EXIT 2, not a result` (exit 2) ✓

**Live run:** exit 0; writes `units.csv` (228 rows) and `summary.txt` ✓

**P5 controls verified in `units.csv`:**
| id | enforcers | n_enforcers | corpus_cites | expected |
|---|---|---|---|---|
| rule-20 | `gates.py;scripts/plan_lint.py` | 2 | 47 | positive ✓ |
| rule-26 | `gates.py;verdict.py` | 2 | 6 | positive ✓ |
| rule-63 | (none) | 0 | 0 | negative ✓ |
| wrap-7 | (none) | 0 | 0 | negative ✓ |

All P5 controls hold. Citation floor is credible.

---

## Q-1 — The population, dated

**Template version:** PT v4.97 (gate2-pt-w28-a landed before this plan was released, per plan design).

**228 units by kind** (measured 2026-09-02 at PT v4.97; P2 re-derived from `summary.txt`):

| kind | count |
|---|---|
| rule | 106 |
| checklist | 33 |
| wrap-step | 8 |
| trigger | 8 |
| lens-subquestion | 21 |
| 2.7-bullet | 52 |
| **TOTAL** | **228** |

**Delta from v4.96 pin (224 units → 228):** +4 rules (103–106). The Planner's v4.96 pin stated 102 rules; v4.97 adds exactly four detector-tier rules from `gate2-pt-w28-a`:

| id | title |
|---|---|
| rule-103 | Move the test ORACLE outside the author's model — every detector gets a tier-2 state-space suite |
| rule-104 | A detector's fire count is a RATIO — report fired/evaluated/skipped; never retire on unmeasured |
| rule-105 | An env var is a property of a PROCESS TREE — test the dispatch environment, never the machine |
| rule-106 | Earnability is not discrimination — enumerate the plausible WRONG fixes, construct each, report the kill map |

All four rules (103–106): no enforcer by citation or callee reading; corpus 0; Q-3 class MECHANIZABLE (subjects covered by plan_lint (s)/(t) partial extension or existing mutation_check.py).

---

## Q-2 — The enforcement map, callee side

**Caller list: 64 checks enumerated across 13 surfaces (see `enforcers.csv` for full rows).**

### plan_lint.py — 18 lettered check ids

| check_id | what_it_tests | units_enforced | units_named | agreement |
|---|---|---|---|---|
| lint(a)-dispatch_mode | header dispatch_mode is a recognized value | rule-35 | rule-35 | named=enforced |
| lint(a)-pause_for_verdict | header pause_for_verdict is a recognized token | — | — | neither |
| lint(a)-known_failures | header known_failures is an integer | — | — | neither |
| lint(b) | steps mentioning deposits have parseable Deposits block | rule-26 | — | enforces-more |
| lint(c) | QA plans contain Rule 20 banner pair | rule-20 | rule-20 | named=enforced |
| lint(d) | Scope block parses to at least one path | — | — | neither |
| lint(e) | step headings use uppercase `## STEP N` when qa_steps declared | — | — | neither |
| lint(f)-dc-block | T1+ plan has DC block with all 5 lenses and Closing line | — | — | neither |
| lint(f)-manifest | Cycle Manifest stanza has required fields, valid class, coherent validation | — | — | neither |
| lint(g) | DC ledger C-entries are strictly ascending | — | — | neither |
| lint(h) | DC Closing does not claim no-lens when lens results are recorded | — | — | neither |
| lint(i) | qa_and_terminal mode requires parseable qa_steps | — | — | neither |
| lint(j) | flags `[INHERITED FROM N — NOT RE-EXECUTED]` markers outside fenced code | — | — | neither |
| lint(k) | clone-framed plan names its newest same-class comparison | — | — | neither |
| lint(l) | clone-framed plan firing T-2 declared below T2 | dc-T-2 | dc-T-2 | named=enforced |
| lint(n) | inline backtick grep on literal pattern uses -F flag | — | — | neither |
| lint(o1) | backtick path candidates exist on disk | — | — | neither |
| lint(o2) | Deposits entries are project-prefixed or absolute | rule-26 | — | enforces-more |
| lint(p) | DC ledger C-entries carry backtick command or check: token | — | — | neither |
| lint(q) | sha256 and git pins verify against actual files/repos | — | — | neither |
| lint(r) | probe constants in step blocks have supersede-class clause | — | — | neither |
| lint(s) | target_class=detector plans declare state_space and mutants | — | — | neither |
| lint(t) | advisory: detector-named targets declare target_class | — | — | neither |
| lint(u) | QA step Deposits: first .md is QA report; .txt evidence present | rule-20 | — | enforces-more |

### gates.py — 11 _gate_ functions

| check_id | what_it_tests | units_enforced | units_named | agreement |
|---|---|---|---|---|
| gate-receipt_status | Output Receipt status is Complete | — | — | neither |
| gate-ceo_flags | no CEO-flagged blockers in receipt | — | — | neither |
| gate-no_errors | agent run produced no error | — | — | neither |
| gate-no_permission_denials | no blocking denials (read-class and git-lock exempt) | — | — | neither |
| gate-deposit_exists | agent-declared AND plan-required deposits exist; uncommitted flagged | rule-22; rule-26 | rule-26 | enforces-more |
| gate-rule_20_self_check | QA report has Rule 20 banner and PASSED line | rule-20 | rule-20 | named=enforced |
| gate-rule_22_verification | verification table: no ❌, positive-status rows; no hedging (d) | rule-22; rule-19 | rule-22 | enforces-more |
| gate-qa_test_result | QA .txt evidence has parseable pytest summary; failures ≤ known_failures | rule-21 | — | enforces-more |
| gate-scope_check | files changed are within step's declared Scope block | — | — | neither |

### wrap_check.py — 7 arms

| check_id | what_it_tests | units_enforced | units_named | agreement |
|---|---|---|---|---|
| wrap[0/resolve] | ELUVIAN_WRAP_BELLOWS override points to real bellows checkout | — | — | neither |
| wrap[1/project] | project Done/ committed; project repo pushed | — | **wrap-1** | names-more |
| wrap[2/bellows] | verdicts/resolved and receipts/ committed; bellows pushed | — | **wrap-2** | names-more |
| wrap[3/root] | baton committed; gitlink committed; root pushed | wrap-8 | **wrap-3** | names-more |
| wrap[3b/lessons] | today's `Lessons-swept:` line with session-id in baton | **wrap-7** | — | enforces-more |
| wrap[4/memory] | memory entries have class: frontmatter; memory committed and pushed | — | **wrap-4** | names-more |
| wrap[2r/receipts] | own-session receipts match clearances or hold sidecars | — | — | neither |

**Critical citation mismatch (wrap-1 through wrap-4):** The instrument's citation predicate for wrap-steps searches for `[N/` patterns in code. The wrap_check.py arms are labeled `[1/project]`, `[2/bellows]`, `[3/root]`, `[4/memory]` — these are the wrap_check's own sequential arm labels, NOT references to PT wrap steps 1–4. The check for arm `[1/project]` verifies that project Done/ files are committed and the repo is pushed; it does NOT verify that PROJECT_STATUS.md was updated (PT wrap step 1's specific act). All four citations are in the **names-more** direction: the code contains text matching the citation predicate but enforces a different act than the PT step describes.

**Wrap-7 and wrap-8 (enforces-more):** The citation predicate finds no `[7/` or `[8/` in code, so the instrument returns zero enforcers. The callee reading finds: `[3b/lessons]` enforces wrap-7 ("Lessons sweep") by verifying a `Lessons-swept:` line with today's date and session-id appears in the baton; `[3/root]` partially enforces wrap-8 ("Session-handoff baton maintenance") by verifying the baton is committed. Both are confirmed by the stop and debt hooks invoking `wrap_check.check()`.

### depositor.py — 5 hold paths

| check_id | what_it_tests | units_enforced |
|---|---|---|
| depositor-empty_writes | plan has non-empty writes set | rule-26 (Deposits block required) |
| depositor-class_mismatch | declared manifest class matches assigned class | — |
| depositor-validation_mismatch | manifest `validation` cycle_check= matches actual verdict | — |
| depositor-receipt_check | matching active receipt exists (slug + content_hash) | — |
| depositor-cycle_check_rerun | plan has BAR_MET at deposit time | — |
| depositor-plan_lint_rerun | plan has no non-benign plan_lint FAIL at deposit time | — |

### cycle_check.py, fold_check.py, propagation_check.py

| check_id | units_enforced | agreement |
|---|---|---|
| cycle_check-assert1 | — (DC internal arithmetic) | neither |
| cycle_check-assert2 | — (register file exists) | neither |
| cycle_check-assert3 | dc-2.7-b1 (fold baseline must exist when folds occurred) | enforces-more |
| cycle_check-BAR_MET | — (bar determination) | neither |
| fold_check | dc-2.7-b1 (fold must not change machine-readable state) | enforces-more |
| propagation_check-restated | dc-2.7-b6; dc-2.7-b8 (declared values not restated unqualified) | enforces-more |
| propagation_check-ordering | dc-2.7-b9 (task sequences consistent) | enforces-more |
| propagation_check-arithmetic | — | neither |

### Other surfaces

| check_id | file | agreement |
|---|---|---|
| walk_register_lint | scripts/walk_register_lint.py | neither (validates register schema, no unit citations) |
| hook-wrap_stop | hooks/eluvian/wrap_stop_hook.py | enforces-more (wrap-7, wrap-8 via wrap_check.check()) |
| hook-wrap_debt | hooks/eluvian/wrap_debt_hook.py | enforces-more (wrap-7, wrap-8) |
| mutation_check | tools/mutation_check.py | neither |
| check_backlog_freshness | scripts/check_backlog_freshness.py | names-more (cites its own Rule 1-4 and Rule 22) |
| verdict-gate_display | verdict.py | named=enforced for rule-22 and rule-26 |
| RULE_20_SELF_CHECK_BLOCK | governance root | named=enforced (rule-20) |

### Per-kind enforcement summary by callee reading

| kind | total | enforced (callee) | cited-only (no enforcement) | neither |
|---|---|---|---|---|
| rule | 106 | 6 (rule-19,20,21,22,26,35) | 4 names-more (rule-1,2,3,4) | 96 |
| checklist | 33 | 0 | 0 | 33 |
| wrap-step | 8 | 2 (wrap-7,8) | 4 names-more (wrap-1,2,3,4) | 2 |
| trigger | 8 | 1 (dc-T-2) | 0 | 7 |
| lens-subquestion | 21 | 0 | 0 | 21 |
| 2.7-bullet | 52 | 4 (b1,b6,b8,b9) | 0 | 48 |
| **TOTAL** | **228** | **13** | **8 disagreements** | **207** |

**Disagreement count (citation vs reading):**
- names-more direction (cited but not enforced): 9 unit citations in 5 checks (rule-1,2,3,4 in backlog freshness; wrap-1,2,3,4 in wrap_check; rule-22 partial in backlog freshness)
- enforces-more direction (enforced but not in citation floor): 8 units (rule-19,21; wrap-7,8; dc-2.7-b1,b6,b8,b9)

---

## Q-3 — The unenforced set, classified

228 total − 13 enforced = 215 unenforced. Classified by the callee reading.

### Counts by class per kind

| kind | MECHANIZABLE | CONVERSATIONAL | UNRESOLVED |
|---|---|---|---|
| rule | 31 | 68 | 1 |
| checklist | 10 | 23 | 0 |
| wrap-step | 1 | 5 | 0 |
| trigger | 5 | 2 | 0 |
| lens-subquestion | 0 | 21 | 0 |
| 2.7-bullet | 10 | 38 | 0 |
| **TOTAL** | **57** | **157** | **1** |

### UNRESOLVED (1)

**rule-17 — Post-execution deliverable verification**: the gate-deposit_exists check verifies that declared deposits EXIST on disk; it does not read whether the Planner has manually verified the deposited content meets the deliverable standard. The agent's receipt is consumed but the verification act itself is free-form prose inside the receipt or the plan step. Home: UNRESOLVED.

### MECHANIZABLE (57) — selected key units

The act each rule mandates produces or could produce an artifact that an existing check could consume. Named check extension needed:

| id | artifact produced/consumed | candidate check |
|---|---|---|
| rule-1/2/3/4 | plan header fields (backlog cites own Rule N, false positive) | plan_lint (a) extension |
| rule-15 | plan text: each step N≥2 has Output Receipt reference | plan_lint new check |
| rule-23 | plan text: end-of-plan step uses anchored-edit patterns | plan_lint new check |
| rule-27 | plan text: diagnostic steps cite artifact ids | plan_lint new check |
| rule-36 | plan text: dormancy steps lack negative-grep patterns | plan_lint new check |
| rule-37 | plan Deposits block: paths are resolvable (not theory) | plan_lint (o1) extension |
| rule-93 | plan text: mandates name inline QA observer | plan_lint new check |
| rule-103..106 | Cycle Manifest detector fields: state_space, mutants, kill map | lint(s) extension |
| checklist-1 | plan Deposits block: canonical multi-line bullet form | plan_lint (b) extension |
| checklist-3 | plan text + dispatch_mode=bellows: no STOP-prose | plan_lint new check |
| checklist-23 | plan step text: Scope block declared | plan_lint (d) upgrade from WARN to check |
| dc-T-1 | write set size from manifest: blast-radius classification | depositor class extension |
| dc-T-5 | write set: destructive-named operations flagged | depositor/plan_lint new check |
| dc-T-6 | manifest writes touching governance/ paths: T-6 in tier line | depositor or plan_lint new check |
| dc-T-7 | plan references a diagnostic id: T-7 should appear in tier | plan_lint (k) extension |
| dc-2.7-b19 | executable check output against real data | propagation_check extension |
| dc-2.7-b21 | plan text: pipes to commands whose exit code matters | plan_lint (n) extension |
| dc-2.7-b24 | plan text grep patterns: line-anchored, fenced blocks stripped | plan_lint (n) extension |
| dc-2.7-b28 | plan text grep: variable patterns via -e flag | plan_lint (n) extension |
| dc-2.7-b44 | plan text: multi-step constraints declared with site names | plan_lint new check |
| dc-2.7-b49 | plan edit anchors: asserted as THE occurrence before rewrite | plan_lint extension |

### CONVERSATIONAL (157) — the legitimate scope of Planner memory (thread 91)

The act produces no artifact and none can be made without changing what the rule is for.

**Largest conversational populations:**
- All 21 lens-subquestions (dc-q1.1 through dc-q5.5): the five-lens walk is the Planner's reading protocol. The subquestions guide what to look for; the answer lives in the Planner's reading, not in a parseable artifact.
- 38 of 52 §2.7 bullets: fold discipline (re-read fold SET, re-run finding lens, treat decision fold as round, etc.) describes acts within the Planner's session. The outcome is prose in the DC block, not a machine-readable artifact distinct from the plan.
- 68 of 106 rules: rules expressing authoring quality standards ("Dense prompts, no narrative"; "Phrase uncertain fixes as verify-first"; "Resume machinery is justified only when the interrupted work is not re-executable") require reading the plan's CONTENT, not its FORM.
- 23 of 33 checklist items: about authoring decisions (front-end field names, session memory exclusions, cross-repo audit contracts) that require contextual judgment.
- 5 wrap steps: wrap-1 ("Update PROJECT_STATUS.md"), wrap-2 ("Update KNOWLEDGE_INDEX.md"), wrap-3 ("Batched glossary update"), wrap-4 ("Synthesize prompt feedback patterns"), wrap-6 ("Surface pending items") — the CONTENT of these acts is verified by the Planner's reading, not by a pattern in the file.
- 2 triggers: dc-T-4 (Money-affecting path) requires recognizing business impact; dc-T-8 (Novel pattern) requires recognizing novelty — both are judgment calls with no artifact that uniquely encodes the firing decision.

**High-corpus CONVERSATIONAL units (mechanization backlog caveat — most-cited and unenforced):**
- rule-25 (corpus 8): Planner polling of Bellows verdict requests — about the Planner's session behavior, produces no plan artifact
- checklist-3 (corpus 5): No reliance on STOP-prose — could be MECHANIZABLE (grep for STOP patterns in bellows-dispatched plans); classified CONVERSATIONAL because the prohibition is on the intent, not the word
- rule-56 (corpus 4): Resume machinery justified only when interrupted work not re-executable — requires reading the plan's context to judge whether interruption is real and re-execution impossible
- dc-q2.2 (corpus 3): Does any step relax an existing guard? — requires reading the step's effect on a gate it calls

---

## Q-4 — The corpus weight

P4 re-derived from `units.csv` (corpus_cites column; predicate: `Rule N` for rules, `(L.n)` for subquestions, etc. in LESSONS.md).

**Total corpus entries citing any unit:** rules 22 units cited (of 106); checklist 9 (of 33); wrap-step 3 (of 8); trigger 1 (of 8); subquestion 4 (of 21); 2.7-bullet 0 (of 52).

**IN-POPULATION CAVEAT:** A rule cited in the corpus is one whose violation was RECORDED. High corpus weight measures the Planner's recording discipline as much as the violation rate. The caveat applies to every count below.

### Top 20 units by corpus weight

| rank | id | corpus | enforced (callee) | Q-3 class | Q-5 home | title (truncated to 55 chars) |
|---|---|---|---|---|---|---|
| 1 | rule-20 | 47 | YES | ENFORCED | STANDARD | Mandatory QA self-check Python block |
| 2 | rule-22 | 20 | YES | ENFORCED | STANDARD | Planner verification of deposited files |
| 3 | wrap-1 | 12 | NO | CONVERSATIONAL | EXEC-MODEL | Update PROJECT_STATUS.md |
| 4 | wrap-2 | 11 | NO | CONVERSATIONAL | EXEC-MODEL | Update KNOWLEDGE_INDEX.md |
| 5 | rule-35 | 10 | YES | ENFORCED | STANDARD | Distinguish manual-bootstrap vs Bellows-dispatch |
| 6 | rule-25 | 8 | NO | CONVERSATIONAL | ROLE | Planner polling of Bellows verdict requests |
| 7 | wrap-3 | 8 | NO | CONVERSATIONAL | EXEC-MODEL | Batched glossary update |
| 8 | rule-21 | 6 | YES | ENFORCED | STANDARD | Test scope must be declared in the plan header |
| 9 | rule-26 | 6 | YES | ENFORCED | STANDARD | Deposits field convention |
| 10 | checklist-3 | 5 | NO | CONVERSATIONAL | ROLE | No reliance on STOP-prose |
| 11 | rule-19 | 4 | YES | ENFORCED | STANDARD | Hedging keywords auto-invalidate |
| 12 | rule-56 | 4 | NO | CONVERSATIONAL | ROLE | Resume machinery is justified only when… |
| 13 | dc-T-6 | 3 | NO | MECHANIZABLE | STANDARD | Governance surface |
| 14 | dc-q2.2 | 3 | NO | CONVERSATIONAL | ROLE | Does any step relax an existing guard? |
| 15 | rule-23 | 3 | NO | MECHANIZABLE | STANDARD | End-of-plan housekeeping anchored edits |
| 16 | rule-36 | 2 | NO | MECHANIZABLE | STANDARD | Negative grep during dormancy is not architectural evidence |
| 17 | rule-39 | 2 | NO | CONVERSATIONAL | ROLE | Pre-edit verification of SA-derived claims |
| 18 | rule-85 | 2 | NO | CONVERSATIONAL | ROLE | Repo-touching compounds — commits AND state-changing ops |
| 19 | dc-q2.1 | 2 | NO | CONVERSATIONAL | ROLE | What breaks if this ships? |
| 20 | rule-15 | 1 | NO | MECHANIZABLE | STANDARD | Every step after Step 1 verifies prior step's Receipt |

**Natural mechanization order** (corpus-cited, unenforced, most-cited first — the backlog): dc-T-6 (3), rule-23 (3), rule-36 (2), rule-15 (1), rule-23 (3), rule-27 (1), rule-37 (1), rule-93 (1). Note: wrap-1, wrap-2, wrap-3 are corpus-cited and unenforced by content but classified CONVERSATIONAL (the content act, not the commitment, is unverifiable), so they sit outside the mechanization backlog.

---

## Q-5 — The home map

**By-enforcer split rule (applied mechanically):**
- **STANDARD**: any check enforces it (Q-2 callee reading) OR any check could (Q-3 MECHANIZABLE)
- **ROLE**: CONVERSATIONAL (the act produces no artifact and none can be made without changing the rule's purpose)
- **EXECUTION-MODEL**: the unit lives in the Template's Bellows or Manual execution sections, regardless of enforcement
- **UNRESOLVED**: genuinely arguable

**PT Bellows / Manual execution section line ranges** (from PT v4.97):
- Session Wrap section (wrap steps 1–8): wrap-step units
- Rule-35 (dispatch mode declaration) and rule-8 (final step moves plan to Done in Bellows dispatch): execution-model rules
- Line ranges to be re-derived from the current PT as the reorganization plan's author reads the Template.

### Counts by home and source document

| home | PLANNER_TEMPLATE | DRAFTING_CYCLE | TOTAL |
|---|---|---|---|
| STANDARD | 48 | 20 | 68 |
| ROLE | 91 | 61 | 152 |
| EXECUTION-MODEL | 7 | 0 | 7 |
| UNRESOLVED | 1 | 0 | 1 |
| **TOTAL** | **147** | **81** | **228** |

### Units that would MOVE in a by-enforcer reorganization

**Template rules → STANDARD (beside DC):** rule-20, rule-21, rule-22, rule-26 — these are enforced by bellows checks and live in the Template section; their enforcement home is the bellows code, aligning them with the STANDARD document.

**Template rules → ROLE (Planner memory):** 68 PT rules classified CONVERSATIONAL. These rules express authoring standards that cannot be mechanized; they belong in a Planner-facing role document.

**DC §2.7 bullets → STANDARD:** dc-2.7-b1, dc-2.7-b6, dc-2.7-b8, dc-2.7-b9 — enforced by fold_check and propagation_check. These bullets live in the DC's cross-cutting rules section but their enforcer is bellows code, pulling them toward the STANDARD document.

### §2.7 bullet pairs with Template rules (same subject — the pairs a merge would fold)

The DC §2.7 section and the PT rules share several subjects. Pairs identified by reading both documents for the same claim stated in two voices:

| DC bullet | PT rule | shared subject | DC sentence (first clause) | PT sentence (first clause) |
|---|---|---|---|---|
| dc-2.7-b1 | (PT fold post-condition rules) | fold post-condition | "THE FOLD IS THE UNIT THAT CARRIES THE POST-CONDITION" | not yet a named PT rule — pair is DC-to-instrument (fold_check) |
| dc-2.7-b49 | (PT edit anchor rules) | edit anchor is not a probe | "An EDIT ANCHOR is not a probe — assert it is THE occurrence you mean before rewriting anything" | PT has no numbered rule with this exact form at v4.97; pair is within DC |
| dc-2.7-b24 | (PT probe integrity) | line-anchored search with fenced blocks stripped | "Anchor every structural search line-anchored, and strip fenced blocks" | plan_lint enforces the fenced-block stripping mechanically |
| dc-2.7-b8 | (PT numbers discipline) | counts in prose go stale without assertion | "A COUNT IN PROSE THAT NO ASSERTION READS WILL GO STALE. Declare a set ONCE" | PT Numbers discipline section covers pin/declare practice |

**Note:** at v4.97 the Template does not have numbered rules whose sentences duplicate §2.7 bullets word-for-word. The §2.7 bullets are operational (walk-time) while PT rules are authoring-time; the overlap is THEMATIC rather than textual. The pairs above are the closest thematic overlaps. The reorganization plan's author should diff the regions directly to settle which pairs merge.

---

## Q-6 — What the three open DC threads cover

### Thread 67 — DRAFTING_CYCLE.md:228 four doc-vs-code defects (manifest-stanza prose cluster)

**Units named:** dc-2.7-b? (not by id); the thread focuses on the DRAFTING_CYCLE.md prose at line 228 describing the Cycle Manifest stanza. The defects are doc-vs-code mismatches:
- S1: "ten ordered fields" stale — plan_lint reads 13 fields (three detector fields added in executable-576)
- S2: "read-only auto-deposits; the other two hold for the CEO" false — depositor._assign_class auto-deposits governed-tooling, register-writing, and app-feature
- S3: "governed-tooling" dead enum arm — _assign_class returns four values, never governed-tooling
- D2: class list names three values; plan_lint:536 accepts five

**Enforcement relationship:** These defects are in the DC's normative description of the manifest stanza (not enumerated units in the census). plan_lint enforces the stanza at the code level; the doc has drifted. A by-enforcer reorganization would put the AUTHORITATIVE stanza description in the STANDARD document beside the code, not in the Planner's role document — so thread 67's fix belongs in the STANDARD layer.

**Superseded or folded by reorganization?** The reorganization would move the stanza documentation to the STANDARD document; thread 67's fix (correcting the existing DC text) becomes an INPUT to that move — it should land BEFORE the reorganization cuts from the DC, so the content moved is correct.

### Thread 72 — Re-draft the gates rule on what gates.check actually reads

**Units named:** the gates rule at DC v2.18 (withdrawn at v2.20). Thread 72 records that the v2.18 bullet claiming gates.check is decidable from plan text alone was false — gates.check takes `parsed` (the Output Receipt) which exists only after a step runs. The SALVAGEABLE RESIDUE identified: `_gate_qa_test_result` reads `_extract_plan_required_deposits(step_text)` before falling back to the receipt, making "does this QA step declare a raw-evidence deposit" answerable at authoring. That is a plan_lint WARN.

**Enforcement relationship:** The withdrawn bullet was in the DC's STANDARD-adjacent zone (it described what bellows checks). Thread 72's salvageable residue would become a new lint(u) extension or a new plan_lint check in the STANDARD document. The by-enforcer reorganization would move this to STANDARD once the correct form is authored.

**Superseded or folded by reorganization?** Not superseded — the reorganization is a structural move; thread 72 supplies the CONTENT of one check that should live in STANDARD. Thread 72 should resolve first (author the new lint check), then the reorganization moves it to the right home.

### Thread 74 — Tier 2 of the §2.7 refactor (merge self-declared pairs)

**Units named:** specific §2.7 bullet pairs at line numbers L147+L191, L161+L168, L162+L167, L155+L159. Tier 1 (grouping into 7 subheads) shipped at cf18eb0/v2.21. Tier 2 merges bullets the file itself declares as "one rule in two parts."

**Enforcement relationship:** None of the named bullets are currently enforced by callee reading (they're all CONVERSATIONAL by Q-3). Thread 74's merges would reduce the §2.7-bullet unit count (228 → fewer) without changing the enforcement map.

**BLOCKER noted in thread 74:** SE-9 — `section-2.7:N` line-number citations in live design docs, two Done/ plan records, and a plan_lint test fixture had drifted non-monotonically after Tier 1. Tier 2 moves bullets again. The blocker must be resolved before Tier 2 lands.

**Superseded or folded by reorganization?** Thread 74 is an INPUT to the reorganization. The reorganization's ROLE document takes the §2.7 conversational bullets as its primary content; Tier 2's merges should land BEFORE the reorganization splits the file, so the content moved is already the merged, correct form.

### Gate-2-accepted proposals (thread 76's remaining eight) vs moved units

The eight accepted proposals (IDs 415, 417, 421, 422, 425, 431, 435, 437 from `lesson_proposals`) all target `PLANNER_TEMPLATE.md`:

| proposal_id | suggested_action (truncated) | target unit (by census) | would land in moved unit? |
|---|---|---|---|
| 415 | Add rule: cross-machine deposit paths must be repo-relative | new rule (not yet in PT v4.97) | STANDARD home (mechanizable via o2 extension) |
| 417 | Add rule: re-pin in-flight plans when pinned dependency is amended | new rule | STANDARD (mechanizable via lint(q) extension) |
| 421 | Add rule: before wiring a gate to an existing field, audit all consumers | new rule | ROLE (judgment-based authoring guidance) |
| 422 | Add rule: STOP ARM must be keyed on a provable premise | new rule | ROLE (authoring judgment) |
| 425 | Add rule: before proposing lifecycle-mode change, measure the mode on the actual machine | new rule | ROLE (authoring judgment) |
| 431 | Add rule: when declaring a field optional, enumerate every consumer | new rule | STANDARD (mechanizable — lint could check optional-field declarations) |
| 435 | Add rule: before adding to watched_projects, inventory existing contents | new rule | ROLE (process judgment) |
| 437 | Add rule: normative worked examples that feed machine comparators must be verified against shipped corpus | new rule | STANDARD (verifiable via corpus counts — lint(q) extension) |

**None of the eight proposals land in a CURRENTLY EXISTING unit that would move.** All eight would become new PT rules. Their home under the by-enforcer split: proposals 415, 417, 431, 437 → STANDARD (mechanizable subjects); proposals 421, 422, 425, 435 → ROLE (authoring judgment). The reorganization plan should account for these new rules arriving in the correct layer.

---

## Appendix — Methodology notes and limitations

**Citation is the floor, not the finding.** The instrument enumerates units that a check NAMES. The callee reading (Q-2) settles which citations correspond to actual enforcement. Disagreements (names-more, enforces-more) are the primary finding: 9 named-but-not-enforced citations and 8 enforced-but-unnamed units.

**The §2.7 bullet population carries zero corpus cites** by the instrument's predicate (bullets have no id a checker names; the section-cited count of 52 reflects files containing `§2.7` as a whole-section reference). This is not a finding about §2.7's importance — it reflects a gap in the citation-predicate coverage for bullets, not their enforcement status.

**CONVERSATIONAL classification is a judgment.** The 157 CONVERSATIONAL units represent this agent's reading of whether the act could produce a machine-readable artifact. The 1 UNRESOLVED (rule-17) is where the reading is genuinely uncertain. The reorganization plan's Planner and the CEO decide — this census does not recommend.

**The by-enforcer split decides nothing.** The home column in Q-5 is one mechanical rule applied to the census data. Whether the EXECUTION-MODEL home becomes a third document or a section within STANDARD or ROLE is a design decision for the T2 reorganization plan.

---

*Instrument: `knowledge/qa/evidence/pt-dc-census-2026-09-02/census.py` sha `9c52011935a17137`*
*Evidence: `knowledge/qa/evidence/pt-dc-census-2026-09-02/` (units.csv, enforcers.csv, summary.txt)*
*Walk register: `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-pt-dc-census-2026-09-02.md`*
