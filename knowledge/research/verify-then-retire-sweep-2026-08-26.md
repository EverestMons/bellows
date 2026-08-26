# Verify-then-retire sweep — batch-4 diagnostic (2026-08-26)

Seven enforcement surfaces measured, eight memory retirements licensed or routed.

---

## R-1 — yield-rising (memory `rising-yield-means-split-not-walk`)

### Re-derived pins

| pin | file:line | value |
|---|---|---|
| P1 | `scripts/cycle_check.py:394` | returns `"ESCALATE:yield-rising", 1` |
| P1 test | `tests/test_cycle_check.py:128` | `assert verdict == "ESCALATE:yield-rising"` |

### Instrument runs

**Probe — grep yield-rising:**
```
/usr/bin/grep -nF "yield-rising" scripts/cycle_check.py tests/test_cycle_check.py
scripts/cycle_check.py:394:            return "ESCALATE:yield-rising", 1
tests/test_cycle_check.py:128:    assert verdict == "ESCALATE:yield-rising"
```

**Pytest:**
```
python3 -m pytest tests/test_cycle_check.py -q 2>&1 | tail -3
35 passed, 1 warning in 0.91s
```

**DC §2.8 cut/target triggers — rising yield:**
DC L210: "(i) yield RISING rather than falling across consecutive passes" — named as the first of three measurable cut/target trigger signals. DC L40 (§2 Cadence): "The loop is `cycle_check`-gated for the mechanical signals (plateau, rising yield, assert failures)." The trigger token "rising yield" is present in DC §2.8 L210, though not as `yield-rising` literally — the DC prose says "yield RISING" and cycle_check emits `ESCALATE:yield-rising`.

**Note on DC search:** `/usr/bin/grep -nF "yield-rising" DRAFTING_CYCLE.md` returned exit 1 (no match). The DC does not use the hyphenated token `yield-rising` — it uses the prose form "yield RISING" at L210. The probe `grep -ni "rising"` confirms L40 and L210 carry the signal. This re-derivation supersedes P1's DC anchor.

### Verdict: **COVERED**

The mechanical escalation at `cycle_check.py:394` fires on rising instruction-count between consecutive walks, halting auto-advance with `ESCALATE:yield-rising` (exit 1). The DC §2.8 L210 cut/target trigger clause names rising yield as the first measurable signal prompting a cut or targeted pass. Together they cover the memory's warning (rising yield ⇒ stop walking, consider splitting). The memory's split-on-the-risk-boundary REMEDY is judgment prose — it survives in DC §2.8 L210's trigger clause, which reads: "reaching a trigger is never by itself a mandate to cut — it is the prompt to consider one, and a cut still runs the subtractive-trim discipline." The pointer can cite DC §2.8 L210 for the judgment home.

---

## R-2 — register substrate (memories `fabricated-close-reaches-execution-register-is-the-guard`, `no-fabricated-drafting-cycle`)

### Re-derived pins

| pin | file:line | value |
|---|---|---|
| P2a | `scripts/cycle_check.py:377` | `return "ESCALATE:assert-fail:1", 1` |
| P2b | `scripts/cycle_check.py:379` | `return "ESCALATE:assert-fail:2", 1` |
| P2c | `scripts/cycle_check.py:381` | `return "ESCALATE:assert-fail:3", 1` |
| P2d | `scripts/cycle_check.py:383` | `return "ESCALATE:uncommitted-walk", 1` |
| P2e | `scripts/cycle_check.py:262` | `register_result = "PASS" if (git_root / ref).exists() else "FAIL"` |
| P2f | `scripts/cycle_check.py:478-482` | `walks_with_rows` coverage counter |

### Instrument runs

**Probe — substrate/register tests:**
```
/usr/bin/grep -nE "uncommitted|substrate|register" tests/test_cycle_check.py
  (selected matching test names:)
  test_uncommitted_walk (L223) — asserts ESCALATE:uncommitted-walk
  test_assert_fail_1 (L65) — assert-fail:1
  test_assert_fail_2 (L74) — assert-fail:2
  test_assert_fail_3 (L87) — assert-fail:3
  test_walk_register_cross_repo (L352) — register N/A for cross-repo
  test_emit_manifest_coherence_no_register (L585) — coherence N/A without register
  test_assert_3_baseline_exists (L422) — assert-3 baseline
```

**Pytest (same run as R-1):**
```
35 passed, 1 warning in 0.91s
```

**DC §2 L40 — substrate clause (both halves verified):**
1. Substrate verified DIRECTLY: "Substrate-presence is verified DIRECTLY — a committed `**Walk register:**` reference line (the exact token cycle_check's assert #2 reads) pointing to a `walk-register-<slug>.md` file that `walk_register_lint` validates, a per-walk commit per walk, and a `fold_check` baseline — NOT inferred from the `cycle_check` verdict"
2. Substrate-less close is MANUAL: "a substrate-less `BAR_MET` is indistinguishable from a fabricated close (cycle_check treats an N/A assert identically to PASS), so without the substrate the close is MANUAL and CEO-confirmed, never auto."

Both halves present at DC L40. The substrate-presence precondition gates BOTH auto-advance AND auto-close (stated twice, including the panel-DISC-1 tag).

**DC changelog 2.13 (L315):**
"Paired cross-repo memory rewrite: `drafting-cycle-one-pass-per-turn`, `no-fabricated-drafting-cycle`, `drafting-walk-phases-separated-by-turn` — all three aligned to the auto-advance cadence with the substrate-presence gate on both advance and close (the Planner's act at the same close, CEO-authorized)."

Planner-attested fact (per diagnostic instruction): both memory entries already carry a "MECHANIZED by the DC v2.13 §2 auto-advance cadence" header, and DC changelog 2.13 L315 records the paired rewrite — attested, not self-verified (memory files live outside this agent's sandbox).

### Verdict: **COVERED** (both memories)

**`fabricated-close-reaches-execution-register-is-the-guard`:** A fabricated close is now mechanically distinguishable wherever auto-advance/auto-close would act. The substrate-presence check at DC §2 L40 verifies the register directly (not via cycle_check's verdict), and the substrate-less arm falls back to manual (CEO-confirmed). The six code sites (assert-fail:1/2/3, uncommitted-walk, register PASS/FAIL, walks-with-rows) enforce a present-but-broken substrate mechanically.

**`no-fabricated-drafting-cycle`:** Same enforcement surface. DC §2 L40's cadence clause makes auto-advance depend on committed substrate presence, and DC changelog 2.13 records both memories aligned to this cadence.

---

## R-3 — fold_check (memory `claimed-fold-may-never-have-landed`)

### Re-derived pins

`scripts/fold_check.py` — full contract read:
- **What it compares:** Machine-readable signals (lines starting with WARN, ERROR, PIN-CHECK, FAIL) from a set of readers (plan_lint for plans, walk_register_lint for walk registers), normalized to strip line numbers and volatile counts.
- **When it fails:** When the set of normalized signals DIFFERS between a saved baseline and a post-fold check (exit 1 = drift, exit 2 = could not run, exit 0 = clean).
- **What it does NOT check:** Whether a fold was actually MADE. It checks signal DRIFT, not fold presence/absence.

### Instrument runs

**Pytest:**
```
python3 -m pytest tests/test_fold_check.py -q 2>&1 | tail -3
15 passed, 1 warning in 0.99s
```

**LANDED-NOTHING case (constructed live in /tmp):**
```
cp knowledge/decisions/Done/executable-563.md /tmp/fold_test_568.md

python3 scripts/fold_check.py --save-baseline /tmp/fold_test_568.md --baseline /tmp/fold_baseline_568.json
BASELINE SAVED: /tmp/fold_baseline_568.json
readers=1 signals=6
  plan_lint: exit=0 signals=6

# Changed NOTHING — ran check immediately:
python3 scripts/fold_check.py /tmp/fold_test_568.md --baseline /tmp/fold_baseline_568.json
FOLD-CHECK CLEAN: machine-readable state unchanged (6 signals held)
exit 0
```

A no-op "fold" — save baseline, change nothing, check — passes clean. fold_check detects signal DRIFT (a fold that changed machine-readable state) but does NOT detect a claimed-but-absent fold (a fold was recorded but changed nothing). A fold that was claimed in the Cycle Log but made zero edits passes silently.

### Verdict: **PARTIAL**

fold_check covers half of the memory's warning: it prevents a fold from BREAKING a machine contract (the signal-drift half, proposal 348's three measured instances). It does NOT cover the other half: the record-vs-artifact attestation — a fold can be RECORDED (in the Cycle Log, the walk register) and exist NOWHERE in the artifact. The memory's second trap — "probes must be EARNABLE against the pre-edit file" — is also uncovered, since fold_check only reads signals, not probe content.

**Uncovered case:** A claimed fold that changed nothing. fold_check's baseline-then-check model silently passes a no-op edit, which is indistinguishable from a clean fold that genuinely changed only prose (which is the intended pass case). The distinction requires a fold_check mode that compares the artifact's byte content (or diff) rather than its reader signals — or a plan_lint WARN that flags a walk register entry claiming N folds when the per-fold diffs total zero lines.

**Route:** batch-item-3 plan_lint cluster — a WARN-level check: when a walk's Cycle Log claims folds but the committed diff for that walk is empty (or the fold count exceeds the diff's hunk count), flag the discrepancy. Alternatively a fold_check `--verify-edit` mode that asserts the artifact's content hash changed between baseline and check. The memory retires WITH this cluster, not before, per the Planner's routing.

---

## R-4 — wrap ritual (memory `eluvian-session-wrap-ritual`)

### Re-derived pins

| arm | wrap_check.py line | enforcement |
|---|---|---|
| [1/project] | L160-175 | `porcelain(repo, "knowledge/decisions/Done")` + `unpushed_count(repo)` |
| [2/bellows] | L177-192 | `porcelain(BELLOWS, "verdicts/resolved")` + `porcelain(BELLOWS, "receipts")` + `unpushed_count(BELLOWS)` |
| [3/root] | L194-205 | `porcelain(ROOT, "shop_next_session.md")` + `porcelain(ROOT, "bellows")` + `unpushed_count(ROOT)` |
| [3b/lessons] | L206-252 | `Lessons-swept:` line in baton with today's date + session-id key |
| [4/memory] | L254-311 | `porcelain(MEMORY)` + class-frontmatter gate + `unpushed_count(MEMORY)` |

Five arms, matching the docstring at L23-27 which names the four repos and references the memory.

### Instrument runs

**Pytest (six test files):**
```
python3 -m pytest tests/test_wrap_hooks.py tests/test_wrap_3b_keyed.py \
  tests/test_wrap_memory_class_gate.py tests/test_wrap_sentinel.py \
  tests/test_wrap_receipts.py tests/test_wrap_r2_registry.py -q 2>&1 | tail -3
128 passed, 1 warning in 9.86s
```

### Ritual-step-to-arm mapping

| Ritual step (inlined from memory) | Enforcing arm | Evidence |
|---|---|---|
| (1) project repos — commit Done/ | [1/project] L160-175 | porcelain + unpushed |
| (2) bellows — commit + push verdicts/resolved/ | [2/bellows] L177-192 | porcelain verdicts + receipts + unpushed |
| (3) governance root — baton refreshed + committed, gitlink bumped, push | [3/root] L194-205 | porcelain baton + gitlink + unpushed |
| (3b) lessons sweep — Lessons-swept: baton line | [3b/lessons] L206-252 | baton parse + session-id key |
| (4) memory repo — commit + push if touched | [4/memory] L254-311 | porcelain + class gate + unpushed |
| Push each repo | Each arm's unpushed_count | [1/project] L171, [2/bellows] L190, [3/root] L203, [4/memory] L309 |

No unmapped step. Every ritual step has a blocking enforcement arm.

### Instruction home

The ritual HOW-TO instruction now lives in:
1. The `/wrap` skill (invoked as a Claude Code skill)
2. `hooks/eluvian/wrap_check.py` docstring L1-28 (the four-repo ritual reference with per-step descriptions)

The memory is type: reference (a HOW-TO). Enforcement ≠ instruction, but the instruction has an in-path home at both locations. The pointer can cite the `/wrap` skill + `wrap_check.py` docstring.

### Verdict: **COVERED**

Every ritual step has a blocking arm in wrap_check.py, verified by 128 passing tests across six test files. The instruction now lives in the /wrap skill and wrap_check.py's own docstring. The memory is retirable as a stale pointer aiming at those homes.

---

## R-5 — step headers (memory `bellows-step-headers-h2-required`)

### Re-derived pins

| pin | file:line | value |
|---|---|---|
| P5a | `scripts/plan_lint.py:260-269` | check (e): step heading case guard |
| P5b | `scripts/plan_lint.py:262` | fires when `not step_headers and header.get("qa_steps")` |

### Instrument runs

**Fixture A (with qa_steps, H3 steps):**
```
python3 scripts/plan_lint.py /tmp/fixture_a_568.md
WARN: qa_steps lists step 2 but step 2 is not QA-labeled — it will be gated as QA (plan-133 trap)
WARN: no cycle_tier declared (DRAFTING_CYCLE.md §1/§3)
PASS: (a) header — parsed
FAIL: (e) step heading format — header declares qa_steps but no uppercase '## STEP N' heading found — step checks (b)/(d) were skipped (vacuous pass)
FAIL: (c) QA banner pair — missing: banner, PASSED line
exit 1
```
**Confirmed:** FAIL (e) + FAIL (c), exit 1.

**Fixture B (without qa_steps, H3 steps):**
```
python3 scripts/plan_lint.py /tmp/fixture_b_568.md
WARN: no cycle_tier declared (DRAFTING_CYCLE.md §1/§3)
PASS: (a) header — parsed
exit 0
```
**Confirmed:** exit 0, clean.

Fixture spec as constructed: both fixtures have identical H3 `### Step` headings. A has `**qa_steps:** 2` in the header; B omits that field entirely. Plan_lint (e) fires only when `qa_steps` is declared — without that field, H3 steps pass silently.

**Census — H3 `### Step` in deposited plans:**
```
/usr/bin/grep -rlE '^### Step' knowledge/decisions/
  → 1 file: knowledge/decisions/roadmap-per-plan-step-state-tracker-2026-04-17.md

/usr/bin/grep -rlE '^### Step' /Users/marklehn/Developer/GitHub/{governance,invoice-pulse,lessons-forge}/knowledge/decisions/
  → 22 files in invoice-pulse/knowledge/decisions/Done/ (including executable-434.md — the memory's incident plan)
  → 0 in governance, 0 in lessons-forge
```
Total: 23 plans ever carried H3 steps. 22 are early invoice-pulse plans (pre-dating the H2 convention); 1 is a bellows roadmap file. The H3 pattern is extinct in current authoring.

**PT L1603 confirmation:**
"Single-step doc plans and DEV-only plans are not permitted shapes — **no gate fires on step composition**, so this check must be enforced at plan-authoring time."

### Verdict: **PARTIAL**

Plan_lint (e) catches H3 steps ONLY when `qa_steps` is declared (because the guard's condition is `not step_headers and header.get("qa_steps")`). A plan with H3 steps but no `qa_steps` field — fixture B — passes clean at exit 0. PT L1603 confirms no gate fires on step composition. The qa_steps-less arm is the uncovered half.

**Route:** batch-item-3 plan_lint cluster gains an (e) extension: FAIL any `executable-*` plan parsing zero `^## STEP ` headers regardless of whether `qa_steps` is declared. The current guard protects against vacuous-pass of checks (b)/(d) when qa_steps is present; the extension would catch the shape error independently. The memory retires WITH that cluster, not before.

---

## R-6 — rule-20 (memory `rule-20-form-by-plan-class`)

### Re-derived pins

| pin | file:line | value |
|---|---|---|
| P6a | `gates.py:582` | `_gate_rule_20_self_check` — QA banner + PASSED enforcement |
| P6b | `scripts/plan_lint.py:286-309` | check (c): QA banner pair presence |
| P6c | `tests/test_gates.py` | 21 `rule_20`-keyword tests |
| P6d | `RULE_20_SELF_CHECK_BLOCK.md` | exists at shop root (verified) |
| P6e | `PLANNER_TEMPLATE.md:1139-1147` | Rule 60 — form by plan class |
| P6f | `PLANNER_TEMPLATE.md:1459` | Checklist #4 — cross-references Rule 60 |

### Instrument runs

**Pytest (rule_20 tests):**
```
python3 -m pytest tests/test_gates.py -k "rule_20" -q 2>&1 | tail -3
21 passed, 148 deselected, 1 warning in 0.32s
```

**RULE_20_SELF_CHECK_BLOCK.md existence:**
```
ls /Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md → exists
```

**Rule 60 in PT (L1139-1147):**
```
### 60. Rule 20 self-check form selected by plan class

When authoring a QA step's Rule 20 self-check, select the form by plan class:
- Full canonical block — for plans whose QA produces evidence files.
  The block runs with adapted real evidence files (evidence_dir and
  required_evidence_files both non-empty). Clone-verification clause present.
- Simple banner — for move-only or trivial plans with no evidence artifacts.
  Run the canonical block with an empty required_evidence_files list and a
  real evidence_dir, never hand-author the output.

Both forms pass the gate identically: gates.py requires only the banner + PASSED line.
Source: proposal 192, lesson 2026-07-30
```

**PT changelog row (L2207):**
"v4.81: ... New Rule 60 for Rule 20 form-by-class selection (192)."

Rule 60 carries the class-choice judgment (full block vs simple banner, when to use which, evidence_dir/required_evidence_files criteria). The RULE_20_SELF_CHECK_BLOCK.md at L19 specifies `evidence_dir: <absolute-path-to-evidence-directory>` — the absolute-path convention guards against pwd-relative computation. The unsatisfiable-QA-step concept at PT L1587 is scoped to time-dependent regression gates, not QA steps in general.

### Verdict: **COVERED**

Rule 60's text carries the class-choice judgment. The evidence_dir-from-pwd trap is addressed by the absolute-path placeholder in `RULE_20_SELF_CHECK_BLOCK.md` L19 and by PT L1815's read/write path-discipline rule. The `_gate_rule_20_self_check` at `gates.py:582` enforces banner + PASSED mechanically; plan_lint (c) enforces the pair at lint time. 21 dedicated tests cover the gate. The pointer aims at Rule 60 (PT L1139) + `RULE_20_SELF_CHECK_BLOCK.md`.

---

## R-7 — propagation_check (memory `walking-cannot-close-propagation-defects`)

### Re-derived pins

| pin | file:line | value |
|---|---|---|
| P7a | `scripts/propagation_check.py` | present — three detectors: RESTATED VALUE, ORDERING, ARITHMETIC |
| P7b | DC §2.7 L192 | sweep trigger: "pre-existing-class yield reaches 0 on a walk AND total yield did not fall" |
| P7c | DC §5 L291 | freeze run: "Run `bellows/scripts/propagation_check.py` at this conformance pass, beside `plan_lint`" |
| P7d | `tests/test_propagation*.py` | NO test file exists |

### Instrument runs

**Live run 1 — executable-563.md:**
```
python3 scripts/propagation_check.py knowledge/decisions/Done/executable-563.md
declared symbols: (none found)

ERROR: no symbol declarations parsed — detector (1) cannot run.
  Expected a Numbers-discipline row of the form:  | Dn | **`SYM`** … | … | **VALUE** | …
  This is EXIT 2 (could not run), never a clean result.
exit 2
```
Exit 2 (could not run) — executable-563 has no Numbers-discipline table. The tool correctly refuses to report "clean" over a plan it cannot read (the zero-declaration guard at L206-214).

**Live run 2 — POSITIVE CONTROL (mandatory):**

Fixture constructed by reading `propagation_check.py`'s detector: `detect_restated` at L88-101 searches for `declared_values` matches (parsed from `| **`SYM`** ... | **VALUE** |` rows) appearing as bare numerals in instruction prose without qualifiers. The fixture plants a `**`FLEET`**` = `**42**` declaration and a bare `42` in step prose:

```
python3 scripts/propagation_check.py /tmp/prop_fixture_568.md
declared symbols: {'FLEET': '42'}
instruction region: 12 lines of 15

(1) RESTATED VALUE — a declared value written as a bare numeral in prose
  L11: `FLEET` = 42 restated unqualified
      Deploy the fleet of 42 agents to handle the workload.

(2) ORDERING — distinct task sequences (>1 distinct = a claim stated two ways)
  0 distinct sequence — consistent

(3) ARITHMETIC — same operands, different constants
  none

DIVERGENCES: 1
exit 1
```
**Positive control FIRED.** The instrument found the planted divergence. Absence claims from live run 1 are valid (the instrument is proven).

**DC sweep trigger — §2.7 L192:**
"Trigger (mechanical, both halves measured per walk): **pre-existing-class yield reaches 0 on a walk AND total yield did not fall**" — matches the memory's trigger verbatim.

**DC §5 L291 freeze run:**
"Run `bellows/scripts/propagation_check.py` at this conformance pass, beside `plan_lint`, and record its exit code with the linter's." — mandate confirmed.

**Fence caveat check:**
```
/usr/bin/grep -nF "fence" /Users/marklehn/Developer/GitHub/DRAFTING_CYCLE.md
168: ... excise the WHOLE SPAN of a multi-line construct ...
176: ... strip fenced blocks and blockquotes before matching ...
```
Neither line carries the memory's "never-substitute-a-symbol-inside-a-code-fence" caveat. L168 is about excising constructs when verifying deletion; L176 is about stripping fenced blocks before structural matching. Both are SEARCH discipline, not edit discipline. The memory's caveat — that value substitution (editing) must not touch inside code fences — is **absent from DC**.

**No test file:**
```
ls tests/test_propagation*.py → no matches found
```
Positive control required for any live run — this absence is confirmed (P7d re-derived). No test coverage for propagation_check.

### Verdict: **COVERED** (with residue)

The mechanical enforcement (propagation_check.py) + the DC sweep trigger (§2.7 L192) + the DC freeze mandate (§5 L291) cover the memory's core claim: walking cannot close propagation defects, so a mechanical tool runs at two fixed points (sweep trigger and conformance freeze). The positive control proved the instrument works.

**Residue (pointer text, not a retirement blocker):** The memory's ⚠️ never-substitute-a-symbol-inside-a-code-fence caveat is absent from DC. DC L176 covers stripping fenced blocks before MATCHING (search discipline) but not before EDITING (edit discipline). This single clause should be named in the pointer text so it is not silently lost — it is a narrow authoring-discipline caution, not a mechanical enforcement gap, and does not block retirement.

---

## License table

| Row | Memory entry | Verdict | Licensed act |
|---|---|---|---|
| R-1 | `rising-yield-means-split-not-walk` | COVERED | Retire to `class: stale` pointer → DC §2.8 L210 (cut/target trigger) + `cycle_check.py:394` |
| R-2a | `fabricated-close-reaches-execution-register-is-the-guard` | COVERED | Retire to `class: stale` pointer → DC §2 L40 (substrate-presence gate) + `cycle_check.py:377-383,262,478` |
| R-2b | `no-fabricated-drafting-cycle` | COVERED | Retire to `class: stale` pointer → DC §2 L40 + DC changelog 2.13 L315 (paired rewrite) |
| R-3 | `claimed-fold-may-never-have-landed` | PARTIAL | Route: batch-item-3 plan_lint cluster — WARN on zero-diff fold claim; memory retires WITH that cluster |
| R-4 | `eluvian-session-wrap-ritual` | COVERED | Retire to `class: stale` pointer → `/wrap` skill + `wrap_check.py` docstring L23-27 |
| R-5 | `bellows-step-headers-h2-required` | PARTIAL | Route: batch-item-3 plan_lint cluster — (e) extension FAIL on zero `## STEP` regardless of `qa_steps`; memory retires WITH that cluster |
| R-6 | `rule-20-form-by-plan-class` | COVERED | Retire to `class: stale` pointer → PT Rule 60 (L1139) + `RULE_20_SELF_CHECK_BLOCK.md` |
| R-7 | `walking-cannot-close-propagation-defects` | COVERED | Retire to `class: stale` pointer → `propagation_check.py` + DC §2.7 L192 + DC §5 L291; pointer text carries the fence caveat residue |

**Summary:** 6 of 8 memories fully COVERED and licensed for retirement. 2 PARTIAL (R-3, R-5) routed to the batch-item-3 plan_lint cluster — both retire when that cluster ships.
