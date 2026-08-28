# Diagnostic: Cycle Manifest stanza — mandated by DC v2.12, optional at the gate

**Date:** 2026-08-27 | **Plan:** diagnostic-582

---

## Q-1 — Is the skip real?

### Re-derived pins

**P1 — `(f-stanza)` is presence-optional:**
`scripts/plan_lint.py:508` comment reads `(f-stanza) Cycle Manifest stanza shape check (WARN-only, presence-optional)`. Line `:509` builds the regex: `manifest_m = re.search(r'^## Cycle Manifest\s*$', plan_text, re.MULTILINE)`. Line `:510` the entire check body sits behind `if manifest_m:`. A plan omitting the heading bypasses every field check unconditionally.

**P2 — the silent skip, exercised with a positive control:**

Three arms, all against a COPY of `knowledge/decisions/Done/executable-579.md` in `/tmp`:

| arm | mutation | `(f)` WARNs | exit code |
|-----|----------|-------------|-----------|
| 1 — unmodified | none | 0 | 0 |
| 2 — delete `coherence:` line | `sed -i '' '/^coherence:/d'` | **1** (`(f) WARN: Cycle Manifest stanza missing or empty field: coherence`) | 0 |
| 3 — rename heading to `## Cycle Manifest RENAMED` | `sed -i '' 's/^## Cycle Manifest$/## Cycle Manifest RENAMED/'` | 0 | 0 |

Raw output:

**Arm 1** (unmodified):
```
(o1) INFO: candidates=7 excluded=5 fired=0
[... (o2) WARNs about relative deposit paths ...]
PASS: (a) header — parsed
PASS: (a) dispatch_mode — bellows
PASS: (a) pause_for_verdict — always
PASS: (b) step 1 deposits — 3 path(s)
PASS: (b) step 2 deposits — 3 path(s)
PASS: (c) QA banner pair — both strings present
PASS: (d) step 1 scope — 3 file(s), 0 prefix(es)
PASS: (d) step 2 scope — 3 file(s), 0 prefix(es)
EXIT=0
```

**Arm 2** (positive control — `coherence:` line deleted):
```
(f) WARN: Cycle Manifest stanza missing or empty field: coherence
[... same (o1)/(o2) output, same PASS lines ...]
EXIT=0
```

**Arm 3** (heading renamed — check silenced):
```
[... same (o1)/(o2) output, same PASS lines, NO (f) output ...]
EXIT=0
```

The positive control fires (arm 2 produces exactly 1 `(f)` WARN naming the deleted field). Arm 3 — the heading rename — silences the check entirely.

Additionally, `tests/test_plan_lint.py:3247-3251` explicitly encodes this behavior:
```python
def test_lint_stanza_absent_no_warn():
    """Plan without Cycle Manifest stanza produces NO stanza-related WARN."""
    result = _run_lint(GOOD_PLAN)
    assert result.returncode == 0
    assert "Cycle Manifest" not in result.stdout
```

**Verdict:** Yes. Omitting the `## Cycle Manifest` heading silences the `(f-stanza)` check entirely. The behavior is by design (the comment says "presence-optional" and a test asserts it), but it contradicts the DC v2.12 mandate, which requires the stanza.

---

## Q-2 — How wide is the gap?

### Method

Plan set derived from `**Date:**` headers inside Done/*.md files across six project directories (bellows, invoice-pulse, governance, lessons-forge, anvil, forge). No database used. Each file scanned for `**Date:**` regex, `## Cycle Manifest` heading, and `## Drafting Cycle` heading.

### P4 census (all plans on/after 2026-08-07)

| metric | count |
|--------|-------|
| Plans with parseable `**Date:**` header | 159 |
| Plans carrying `## Cycle Manifest` | 67 |
| Plans without `## Cycle Manifest` | 92 |
| Plans carrying `## Drafting Cycle` | 152 |
| Files without parseable Date header (excluded) | 251 |

**My denominator (159) differs from the Planner's (246).** The Planner used `lifecycle.db` `created_at` joined to Done paths and had 30 of 276 plans fail to resolve. I derived from `**Date:**` headers only, which is a different key — plans whose Date header is missing, malformed, or not in the first 500 bytes are excluded. My 251 unresolved files (no Date header) is large because many older Done files predate the standardized header format.

### P5 census (post-v2.12 mandate, on/after 2026-08-19)

| metric | count |
|--------|-------|
| Total plans | 111 |
| With `## Drafting Cycle` | 107 |
| With DC + `## Cycle Manifest` | 67 |
| **With DC, missing `## Cycle Manifest`** | **40 (37%)** |
| Without `## Drafting Cycle` | 4 |

**Set difference check (P4 vs P5):** The 67 stanza-carrying plans in P4 are EXACTLY the same 67 plans in P5 — zero plans carry a stanza outside the post-mandate window. This confirms the diagnostic's prediction: the stanza did not exist before v2.12.

### Missing plans enumerated (40 total)

**bellows (21):**
diagnostic-455, diagnostic-460, diagnostic-472, diagnostic-478, diagnostic-482, diagnostic-489, diagnostic-491, diagnostic-495, executable-457, executable-461, executable-464, executable-473, executable-474, executable-476, executable-481, executable-483, executable-487, executable-488, executable-492, executable-496, executable-497

**invoice-pulse (14):**
diagnostic-465, diagnostic-486, executable-452, executable-453, executable-454, executable-469, executable-470, executable-471, executable-475, executable-477, executable-479, executable-480, executable-484, executable-494

**governance (1):**
executable-502

**lessons-forge (4):**
diagnostic-498, executable-456, executable-459, executable-500

---

## Q-3 — Are those 40 plans actually non-compliant?

### Method

For each of the 40 plans Q-2 enumerated, I read the Drafting Cycle block, Walks line, Walk STATUS lines, Closing line, and any `cycle_check` dogfood output to determine whether the cycle reached BAR_MET. Evidence tokens: `BAR_MET` in Closing, `bar MET` or `bar met` in Walks line, `BAR_MET` in cycle_check dogfood reference, `CONVERGED` in Closing (pre-cycle_check vocabulary), `CEO-DIRECTED DEPOSIT`, and closing-absent/pending status.

### Classification

#### DRIFT — cycle completed, stanza not pasted (32 of 40)

| plan | evidence |
|------|----------|
| bellows/diagnostic-455 | "bar MET" in Walks line |
| bellows/diagnostic-460 | "bar MET" in Walks line |
| bellows/diagnostic-472 | "BAR_MET" in Closing |
| bellows/diagnostic-478 | "BAR_MET" in Closing |
| bellows/diagnostic-482 | "bar met w5" in Closing |
| bellows/diagnostic-489 | "bar met walk 2" in Closing, "BAR_MET" in cycle_check dogfood |
| bellows/diagnostic-491 | "bar met walk 2" in Closing, "BAR_MET" in cycle_check dogfood |
| bellows/diagnostic-495 | "BAR_MET" in cycle_check reference |
| bellows/executable-457 | "BAR_MET" in Closing |
| bellows/executable-461 | "bar MET" in Walks line |
| bellows/executable-464 | "bar MET" in Walks line |
| bellows/executable-473 | "BAR_MET" in Closing |
| bellows/executable-474 | "bar MET" in Walks line, "BAR_MET" in cycle_check dogfood |
| bellows/executable-476 | "BAR_MET" in Closing |
| bellows/executable-481 | "BAR_MET" in Closing |
| bellows/executable-483 | "bar met w5" in Closing |
| bellows/executable-487 | "bar met walk 3" in Closing, "BAR_MET" in cycle_check dogfood |
| bellows/executable-488 | "BAR_MET" in Closing |
| bellows/executable-492 | "bar met walk 2" in Closing |
| bellows/executable-496 | "BAR_MET" in Closing |
| bellows/executable-497 | "BAR_MET" in cycle_check reference |
| invoice-pulse/diagnostic-465 | "bar MET" in Walks line |
| invoice-pulse/diagnostic-486 | "bar MET" in Walks line |
| invoice-pulse/executable-452 | "bar MET" in Walks line |
| invoice-pulse/executable-469 | "bar MET" in Walk 5 STATUS |
| invoice-pulse/executable-471 | "BAR_MET" in Closing |
| invoice-pulse/executable-475 | "CONVERGED" in Closing |
| invoice-pulse/executable-477 | "CONVERGED" in Closing |
| invoice-pulse/executable-480 | "CONVERGED" in Closing |
| invoice-pulse/executable-484 | "CONVERGED" in Closing |
| lessons-forge/diagnostic-498 | "BAR_MET" in Closing |
| lessons-forge/executable-500 | "BAR_MET" in Closing |

#### LEGITIMATE — never closed at BAR_MET (8 of 40)

| plan | evidence |
|------|----------|
| governance/executable-502 | No BAR_MET anywhere in DC block or Walks; closing discusses panel re-opening |
| invoice-pulse/executable-453 | Closing: "pending — deposit after CEO go" |
| invoice-pulse/executable-454 | Closing: "pending — deposit after CEO go + exec-453 in Done/" |
| invoice-pulse/executable-470 | Walks: "3 run — cycle CLOSED at walk 3 (judged stop on a confirming pass)" — judged stop, not BAR_MET |
| invoice-pulse/executable-479 | STATUS: "CLOSED (2026-08-20)" with yields 1→1→1, no BAR_MET — manual close, pre-cycle_check vocabulary |
| invoice-pulse/executable-494 | No Closing text; no BAR_MET indicator |
| lessons-forge/executable-456 | "CEO-DIRECTED DEPOSIT — §2's bar is NOT met" |
| lessons-forge/executable-459 | "CEO-DIRECTED DEPOSIT — §2's bar is NOT met" |

#### Summary

| bucket | count | percentage of 40 |
|--------|-------|-------------------|
| DRIFT | 32 | 80% |
| LEGITIMATE | 8 | 20% |
| UNCLEAR | 0 | 0% |

**Verdict:** 32 of the 40 missing-stanza plans completed their cycle (BAR_MET or CONVERGED) and should have had the stanza pasted. 8 legitimately lack a stanza because their cycle never reached BAR_MET. The gap is real: **32 plans, or 30% of the 107 post-mandate cycle-running plans, drifted without any warning.**

---

## Q-4 — Where does the stanza come from?

### Method

Copied `knowledge/decisions/Done/executable-579.md` to `/tmp/test-emit-579.md`, ran `python3 scripts/cycle_check.py --emit-manifest /tmp/test-emit-579.md`, captured stdout, checked exit code, and diffed the file before/after.

### Results

**stdout** (the emitted stanza):
```
## Cycle Manifest
tier: T1
target: bellows/tools/mutation_check.py
class: shop-infra
reads: /Users/marklehn/Developer/GitHub/bellows/tools/mutation_check.py, [...]
writes: tools/mutation_check.py, [...]
open_forks: the `expect: survived` CONTROL-mutant feature [...]
walks: 3
yields: N/A
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=N/A
coherence: N/A
```

**Exit code:** 0

**File hash before:** `50d8090ad93509a8f601cecc1ee57299`
**File hash after:** `50d8090ad93509a8f601cecc1ee57299`
**diff:** identical (exit 0)

**Automated callers:** `/usr/bin/grep -rn --exclude-dir=.git -F "emit-manifest" .` finds no automated caller — only the CLI entry point at `scripts/cycle_check.py:584`, test coverage in `tests/test_cycle_check.py`, and a Planner verdict reference.

### Verdict

`emit_manifest` PRINTS the stanza to stdout and DOES NOT write into the plan file. The file is byte-unchanged after the run. The `emit_manifest` docstring at `scripts/cycle_check.py:488-489` says it explicitly: "Strictly read-only — writes nothing, modifies no file."

**The stanza's path into a plan is MANUAL TRANSCRIPTION.** The Planner (or the executing agent) must copy `--emit-manifest` output and paste it into the plan. This — not authorial laziness — is the drift surface a presence check would be policing. The 32 DRIFT plans did not fail to write the stanza; they failed to paste it.

---

## Q-5 — Presence predicate: exercised and measured

### Predicate

The candidate: **warn when a plan contains `## Drafting Cycle` but no `## Cycle Manifest` stanza.**

Implemented as a throwaway script in `/tmp/stanza_presence_predicate.py` and run over the full post-2026-08-19 corpus across all six projects (bellows, invoice-pulse, governance, lessons-forge, anvil, forge).

### Results

| metric | count |
|--------|-------|
| Post-2026-08-19 plans scanned | 111 |
| Plans flagged | **40** |
| Q-3 DRIFT bucket | 32 |
| Q-3 LEGITIMATE bucket | 8 |
| **False positives** (flagged but LEGITIMATE) | **8 (20% of flags)** |

The flag set CONTAINS the entire DRIFT bucket (32 plans) plus 8 false positives. The false positives are plans that legitimately lack a stanza because their cycle never reached BAR_MET:

| false positive | reason |
|----------------|--------|
| governance/executable-502 | Panel re-opened walk, no BAR_MET |
| invoice-pulse/executable-453 | Closing pending |
| invoice-pulse/executable-454 | Closing pending |
| invoice-pulse/executable-470 | Judged stop, not BAR_MET |
| invoice-pulse/executable-479 | Manual close, yields never reached 0 |
| invoice-pulse/executable-494 | No closing text |
| lessons-forge/executable-456 | CEO-directed deposit, bar NOT met |
| lessons-forge/executable-459 | CEO-directed deposit, bar NOT met |

### Is this the right predicate?

The predicate's flag set (40) is close to but not equal to the DRIFT bucket (32). The 8 false positives are plans that have a `## Drafting Cycle` block but legitimately lack a stanza because their cycle did not complete at BAR_MET. A **tighter predicate** would also require evidence of BAR_MET or CONVERGED in the DC block — but that makes it a post-hoc classifier, not a pre-deposit gate.

For a **pre-deposit lint** (which is what `plan_lint` is), the predicate as stated is correct: at deposit time, a plan with a `## Drafting Cycle` block SHOULD have gone through the cycle, and if it lacks a `## Cycle Manifest` stanza, that is worth warning about. The 8 false positives are plans deposited before their cycle completed (CEO-directed, pending close, judged stop) — a WARN on those is informative, not wrong, because it surfaces the absence for the depositor to confirm is intentional.

### Future warn rate

`plan_lint` is a PRE-DEPOSIT lint. Done plans are never re-linted. The 40 historical flags would NOT produce a retro-warning flood — they exist only as a census of what the predicate WOULD HAVE caught if it had existed from v2.12 onward. The future rate on NEW plans depends on:
1. Whether new plans omit the stanza after completing their cycle (the drift surface is the manual paste step — Q-4 confirms it).
2. Whether the warn is implemented as WARN (informative, exit 0) or FAIL (blocking).

The historical drift rate was 32/107 (30%) of post-mandate cycle-running plans. If the presence check had existed, the drift rate on new plans would drop sharply because the warning would catch the omission at deposit time.

---

## Q-6 — What else reads the stanza?

### Search method

1. `/usr/bin/grep -rn --exclude-dir=.git --exclude-dir=knowledge -F "Cycle Manifest" .` — heading-level grep
2. `/usr/bin/grep -rn --exclude-dir=.git -F "parse_manifest_stanza" .` — function-call grep
3. `/usr/bin/grep -rn --exclude-dir=.git --exclude-dir=knowledge --exclude-dir=tests -E 'manifest.*get.*"(class|reads|writes|validation|target)"'` — field-level grep to catch consumers that read stanza fields without naming the heading

**Limitation:** the field-level grep catches `manifest.get("class")` patterns but cannot detect a consumer that reads stanza fields via a different variable name or indirection. No such consumer was found, but the search is inherently incomplete for that class.

### Confirmed consumers

#### Consumer 1: `depositor.py:237-260` — `_parse_plan` (Path A → Path B fallback)

**Reads:** `writes`, `reads`, `class` from `parse_manifest_stanza()` (Path A). When the stanza is absent, `parse_manifest_stanza()` returns `{}`, so `manifest` is falsy. Path B fires: `writes` from `gates._extract_plan_required_deposits(plan_text)`, `reads` from `gates._extract_plan_scope(plan_text)`, `declared_class` stays `None`.

**Impact of absence:** the fallback is SILENT. No log, no warning. The depositor proceeds with Path B data. This is not itself a bug — Path B produces correct results for legacy-format plans. But it means a stanza-less plan's writes/reads come from a different parser, and **any divergence between Path A and Path B data is invisible.**

#### Consumer 2: `depositor.py:173` — class_mismatch guard

```python
if declared_class and declared_class != assigned_class:
    self._hold(path, "class_mismatch", {...})
```

**Impact of absence:** with no stanza, `declared_class` is `None` (from `_parse_plan`). The `if declared_class and ...` guard short-circuits. A stanza-less plan CANNOT be caught declaring the wrong class. The guard is bypassed, not triggered with a default — it ceases to exist.

**Confirmed by code reading.** This consumer is not independently runnable (it's called inside the depositor's intake flow, which requires a running daemon and a ready-file), but the code path is unambiguous: `_parse_plan` returns `declared_class=None`, and `if None and ...` is always `False`.

#### Consumer 3: `depositor.py:513-524` — validation_mismatch check

```python
manifest = cycle_check.parse_manifest_stanza(plan_text)
if manifest:
    val = manifest.get("validation", "")
    if "cycle_check=" in val:
        expected = val.split("cycle_check=")[1].split(",")[0].strip()
        if expected and expected != str(verdict):
            self._hold(path, "validation_mismatch:cycle_check ...")
```

**Impact of absence:** with no stanza, `manifest` is `{}` (falsy). The entire validation cross-check is skipped. A stanza-less plan cannot be caught with a mismatched `cycle_check` expected-vs-actual verdict.

#### Consumer 4: `tools/clear_plan.py:135-138` — class extraction for clear_tool

```python
m = re.search(r"^class:\s*(\S+)\s*$", plan_bytes.decode(...), re.MULTILINE)
if not m:
    return _fail("no Cycle Manifest `class:` line — refuse, never guess")
```

**Impact of absence:** `clear_plan.py` reads the `class:` field DIRECTLY by regex on the raw plan bytes, NOT via `parse_manifest_stanza`. A plan without a `class:` line anywhere in the file causes `_fail` — the tool REFUSES. This is the opposite behavior from the depositor: `clear_plan` fails closed, the depositor fails open.

**Note:** the regex `^class:\s*(\S+)\s*$` is NOT scoped to the `## Cycle Manifest` stanza — it matches any line starting with `class:` anywhere in the file. In practice, the stanza is the only place this pattern appears, but the regex could false-match a `class:` line in a different context (e.g., a code snippet or a different heading's fields).

#### Consumer 5: `scripts/plan_lint.py:508-618` — `(f-stanza)` shape check

**Reads:** all ten required fields plus optional `target_class`, `state_space`, `mutants`. All checks are WARN-only (exit 0 regardless). Presence-optional — this is the gap being measured.

#### Consumer 6: `scripts/cycle_check.py:419-446,487-580` — `parse_manifest_stanza` + `emit_manifest`

`parse_manifest_stanza` is the shared parser. `emit_manifest` reads an existing stanza (if present) to preserve authored fields (`tier`, `target`, `class`, `reads`, `writes`, `open_forks`) and computes `walks`, `yields`, `validation`, `coherence`. It is the PRODUCER, not a consumer in the gate-check sense.

### Consumer behavior summary

| consumer | location | on absence | behavior |
|----------|----------|------------|----------|
| `_parse_plan` | depositor.py:237 | silent fallback to Path B | fails OPEN |
| class_mismatch guard | depositor.py:173 | guard short-circuits | fails OPEN |
| validation_mismatch | depositor.py:513 | check skipped | fails OPEN |
| clear_tool | clear_plan.py:135 | `_fail("refuse, never guess")` | fails CLOSED |
| plan_lint (f-stanza) | plan_lint.py:508 | entire block skipped | fails OPEN |
| emit_manifest | cycle_check.py:487 | uses `<declare>` defaults | N/A (producer) |

**Two consumers, opposite behavior:** the depositor silently proceeds (three separate fail-open paths), while `clear_plan` refuses outright. A presence-required flip in `plan_lint` would surface the absence at deposit time, before either consumer sees it.

---

## Recommendation table

| dimension | current state | proposed state | risk |
|-----------|--------------|----------------|------|
| `plan_lint` (f-stanza) presence | optional | **required** (WARN when DC present, stanza absent) | 8 false positives on LEGITIMATE plans (20% of flags); all informative, none blocking |
| `plan_lint` exit code on new WARN | 0 (WARN-only) | 0 (keep WARN-only) | a FAIL would block plans that legitimately lack a stanza (CEO-directed, pending close) |
| `emit_manifest` write mode | print to stdout | **no change proposed** — a write mode is a separate decision (fork: authored-vs-hybrid population) |
| `depositor.py` Path A/B fallback | silent | **log when falling back to Path B** — the silent skip is the same shape as the (l) silent skip diagnosed in diagnostic-568 |
| `clear_plan.py` regex scope | unscoped `^class:` match | **no change proposed** — the false match risk is theoretical; no Done plan carries a non-stanza `class:` line |
