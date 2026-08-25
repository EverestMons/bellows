# E5 Design: Session-ID-Keyed Wrap Affirmations + Per-Project Glossary

**Date:** 2026-08-25 | **Diagnostic:** 519 | **Depends on:** `eluvian-path-audit-2026-08-24.md` §E5 + bypass (e), `eluvian-path-rulings-2026-08-24.md` (R2 per-project glossary), both T-7.

**The measured defect this closes:** the 3b gate keys on `date.today()` and was discharged by ANOTHER session's same-day line — measured live in SESSION 61 and inherited by every same-day wrap since (at least seven same-day sweep lines rode the hole on 2026-08-24 alone).

---

## Re-derived Pins

All values re-derived 2026-08-25 against bellows main post-518 + the activation restart. These supersede the plan's pins and I say so.

| id | pin | plan value | re-derived value | supersedes? | probe |
|---|---|---|---|---|---|
| G1 | the 3b check today | `wrap_check.py:142` | `wrap_check.py:141-142`: `line.strip().lower().startswith("lessons-swept:") and today in line` over the WHOLE baton via `any()` — ANY line, ANY session, same date discharges it; `today = datetime.date.today().isoformat()` (`:93`) | no | direct read |
| G2 | the E3 interface E5 consumes | `wrap_check.py:90` | `def check(session_id: str | None = None)` — stop hook passes at `wrap_stop_hook.py:207-208` (`session_id or ""`), debt hook at `wrap_debt_hook.py:83-88` (`check_sid`) | no | direct read |
| G3 | glossaries today | **0** | **0** — `ls */knowledge/glossary.md` → `no matches found`; positive control: `ls */knowledge/decisions` matches ai-career-digest, anvil, bellows + others | no | shell |
| G4 | historical Lessons-swept: lines | **22** | **21 actual sweep lines** — the 22nd grep match (baton line 165) is a prose description of the format, not a sweep line; 1 of the 21 (SESSION 63, baton line 71) has a blockquote `>` prefix the current predicate misses (masked by same-day multi-session coverage) | **YES** | `grep -c "Lessons-swept:" shop_next_session.md` = 22; subtract 1 prose; `>` prefix verified by `grep -n` |
| G5 | the ritual doc blob | `3b23291183f4…` | **confirmed** `3b23291183f4e4ed5a25b047fdec11378f0fb201` | no | `git rev-parse HEAD:hooks/commands/wrap.md` |
| G6 | wrap_check blob | `4ac15bfbea14…` | **confirmed** `4ac15bfbea141f2adbfdaa3fb9a9cf85a14efcb2` | no | `git rev-parse HEAD:hooks/eluvian/wrap_check.py` |
| G7 | wrap test surface | test_wrap_hooks 20 + test_wrap_sentinel 28 + E3 receipts tests | test_wrap_hooks **20** + test_wrap_sentinel **28** + test_wrap_receipts **26** + test_deposit_receipt **11** = **85** wrap-related tests | no | `grep -c "def test_"` per file |
| G8 | multi-machine reality | mini wraps against ITS clone; session ids machine-local | confirmed (baton lines 31-53 "MAC MINI SESSION" block; env-override post-`75cc1b4`) | no | baton read |

---

## The Fix-Shape Sentence

From LESSONS.md:4675 (2026-08-24 entry "An affirmation gate keyed on TODAY'S DATE…"):

> *"the newest `Lessons-swept:` line must be one THIS session wrote"*

---

## D-1 — The Keyed 3b Rule

### The current predicate (G1)

`wrap_check.py:141-142`:
```python
swept_ok = any(
    line.strip().lower().startswith("lessons-swept:") and today in line
    for line in baton_text.splitlines()
)
```
where `today = datetime.date.today().isoformat()` at `wrap_check.py:93`.

This scans every line of the baton. Any session that wrote a `Lessons-swept:` line containing today's date discharges the check for all sessions wrapping on the same day.

### Baton structure determines "newest"

The baton is **prepended** (newest session block at the top, oldest at the bottom). Measured: SESSION 64 header at baton line 3, SESSION 60 header at line 175, SESSION 53 at line 457. `Lessons-swept:` lines sit at the end of each session's block. Therefore **the FIRST `Lessons-swept:` line encountered reading top-to-bottom is the NEWEST.**

Complication: 1 of the 21 historical sweep lines (SESSION 63, baton line 71) has a markdown blockquote `>` prefix: `> Lessons-swept: 2026-08-24 (SESSION 63)`. The current predicate's `line.strip().lower().startswith("lessons-swept:")` misses it because after strip+lower, the line starts with `> lessons-swept:`. The new predicate must strip the `>` prefix before matching. This is a latent bugfix in the date-fallback path as well.

### The replacement predicate

Find the NEWEST `Lessons-swept:` line (first match, top-to-bottom, stripping `>` blockquote prefix). Extract its session-id token (D-2 format). Compare against the check's `session_id` argument.

### Arms

**Arm 1 — session id present + newest line carries THIS session's id → PASS.** The current session wrote the newest sweep. The step is enforced.

**Arm 2 — session id present + newest line carries a DIFFERENT session's id → FAIL** with the message:
```
[3b/lessons] The newest Lessons-swept: line belongs to session <foreign-prefix>,
not this session (<this-prefix>). Do the 3b transferable-lessons sweep AS ITS OWN
ACT (distinct from the arc note), then add a Lessons-swept: line carrying this
session's id to shop_next_session.md and commit.
```

**Arm 3 — session id present + newest line has NO session-id token (historical format) → FAIL** with the same action message. A historical line cannot prove the current session swept. The 21 existing lines are all historical-format; the first keyed wrap creates the first id-carrying line and the check transitions.

**Arm 4 — no session id (manual `python wrap_check.py` run) → DATE FALLBACK.** The degrade arm preserves the old `today in line` predicate. Rationale: without a session id, there is nothing to key on. The alternative — hard-fail with "session id required" — blocks manual verification of wrap state, which is a legitimate debugging action. The date-keyed hole is tolerable in manual runs because they are human-witnessed (the human is looking at the output). It is NOT tolerable in hooked runs, where the human is not watching — and hooked runs always carry a session id (G2). The degrade-arm choice does NOT change enforcement posture for hooked wraps (D-7 item 2 tracks the alternative).

**Arm 5 — the debt hook's polarity is opposite the stop hook's.** At SessionStart, the newest `Lessons-swept:` line legitimately belongs to the PRIOR session — the current session has just started and cannot have swept yet. A current-sid-keyed check would fail 3b at EVERY fresh session start. The debt hook's 3b asks "did the PRIOR session sweep?", which a session-id keyed check cannot answer — it can only confirm that SOME session swept (date form) or that a SPECIFIC session swept (id form).

**The debt hook's arm: DATE FALLBACK**, same as arm 4. The resulting asymmetry is the intended law:
- **Stop hook (caller='stop'):** keyed — session-id when available, date when not. The stop hook fires at wrap-end; at that point the current session SHOULD have swept.
- **Debt hook (caller='debt'):** date-only — today's date present in any sweep line. The debt hook fires at session-start; it asks "was there a wrap recently?" not "did this specific session wrap?"

Chosen date-fallback over skip for the debt hook because a missing `Lessons-swept:` line at session start IS actionable debt worth surfacing — the prior session may have closed without wrapping at all.

**Arm 6 — G8's cross-machine case.** The mini wraps against its LOCAL baton clone. After `git fetch + pull`, the baton carries sweep lines from both machines. If the mini is wrapping and its session id is not in the newest line, the check CORRECTLY fails: the mini session needs to do its own sweep and write its own line. After the mini sweeps and writes its line (prepended at the top), THAT becomes the newest line, carrying the mini's session id, and the check passes. The cross-machine case requires no special handling — the prepend ordering naturally makes each new sweep the newest.

**Tie-breaking (MUST-PRESERVE §3):** Two sessions wrapping simultaneously on two machines. Both write their sweep lines. After push/pull, both lines exist, one on top of the other. The check on each machine passes because THAT machine's session wrote a line that was newest at the time. After synchronization, one line is top-most. If the other machine's wrap_check runs again at session start (debt hook), it sees a foreign newest line — but the debt hook uses date-fallback (arm 5), so this is benign. **The keyed check does not create a new trap class** because the check only fires with teeth in the stop hook, and the stop hook runs while the wrap is in progress on THIS machine — its session's line is always freshly written at the top.

### Interface change

`wrap_check.py:90` gains a `caller` parameter:

```python
def check(session_id: str | None = None, caller: str = "stop") -> list[str]:
```

CLI (`wrap_check.py:325-326`):
```python
def main() -> int:
    session_id = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else None
    caller = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] else "stop"
```

Stop hook call (`wrap_stop_hook.py:207-208`):
```python
[sys.executable, str(CHECK), session_id or "", "stop"]
```

Debt hook call (`wrap_debt_hook.py:87-88`):
```python
[sys.executable, str(CHECK), check_sid, "debt"]
```

Default `"stop"` preserves backward compatibility for manual invocations and any call site that doesn't pass the second argument.

### Predicate pseudocode

```python
def _find_newest_sweep_line(baton_text):
    """Return the first (newest) Lessons-swept: line, stripped of > prefix."""
    for line in baton_text.splitlines():
        stripped = line.strip().lstrip(">").strip()
        if stripped.lower().startswith("lessons-swept:"):
            return stripped
    return None

def _extract_sid(sweep_line):
    """Extract session-id prefix from [sid: <value>] token. None if absent."""
    # match [sid: <value>] anywhere in the line
    m = re.search(r'\[sid:\s*([A-Za-z0-9-]+)\]', sweep_line)
    return m.group(1) if m else None

# Inside check():
newest = _find_newest_sweep_line(baton_text)
if newest is None:
    fails.append("[3b/lessons] No Lessons-swept: line found in the baton.")
elif caller == "debt" or not session_id:
    # Date fallback
    if today not in newest:
        fails.append(f"[3b/lessons] No recent Lessons-swept: line (today={today}).")
else:
    # Keyed check (stop hook with session_id)
    sid_in_line = _extract_sid(newest)
    if sid_in_line and session_id.startswith(sid_in_line):
        pass  # arm 1: PASS
    elif sid_in_line:
        fails.append(f"[3b/lessons] The newest Lessons-swept: line belongs to "
                      f"session {sid_in_line}, not this session "
                      f"({session_id[:8]}). ...")  # arm 2
    else:
        fails.append(f"[3b/lessons] The newest Lessons-swept: line is date-keyed "
                      f"only (no session id). ...")  # arm 3
```

The `lstrip(">").strip()` handles the blockquote prefix observed in 1 of the 21 historical lines (SESSION 63, baton line 71).

---

## D-2 — The Line Format

### Session-id token design

The line format adds a trailing `[sid: <prefix>]` token after the date:

```
Lessons-swept: 2026-08-25 [sid: a1b2c3d4] — <delta, or 'none'>
```

**Full UUID vs prefix:** Session UUIDs are 36 characters (e.g., `a1b2c3d4-e5f6-7890-abcd-ef1234567890`). The receipts precedent uses the FULL id in filenames (`receipt-<slug>-<session_id>-<hash12>.json` — `tools/deposit_receipt.py`). The baton line is human-read, and a 36-character UUID in every line degrades readability. An 8-character prefix provides collision safety within the baton's corpus: 21 lines spanning 6 days, 8 hex chars = ~4 billion distinct values, collision probability effectively zero. **Chosen: 8-character prefix** (`session_id[:8]`).

**Parse:** `_extract_sid` matches `[sid: <value>]` via regex `\[sid:\s*([A-Za-z0-9-]+)\]`. The keyed comparison is: `session_id.startswith(sid_in_line)` — a prefix match, so the 8-char line token matches the full 36-char session id.

**`-F`-greppable:** `grep -F "[sid: " shop_next_session.md` matches the token. No collision with historical content: the 21 existing sweep lines contain `[[memory-name]]` double-bracket references and dates, but none contain the single-bracket `[sid: ` prefix. Verified: `grep -F "[sid:" shop_next_session.md` returns 0 matches on the current baton.

**Collision safety against historical lines:** The `_extract_sid` regex requires `[sid:` followed by whitespace and `]` — no historical sweep-line content matches this pattern. The 21 existing lines contain dates (`2026-08-24`), session labels (`(SESSION 64)`), memory links (`[[name]]`), and prose, none of which include `[sid: ...]`.

### wrap.md 3b instruction update

Current instruction at `hooks/commands/wrap.md:50-51`:
```
`Lessons-swept: <today's date> — <one-line delta, or 'none'>`
```

Updated to:
```
`Lessons-swept: <today's date> [sid: <session-id-prefix-8>] — <one-line delta, or 'none'>`
```

Where `<session-id-prefix-8>` is the first 8 characters of the Claude Code session UUID (visible in hooks.log or extractable from the session context).

### ELUVIAN_PATH.md Stage 5 satisfaction

`ELUVIAN_PATH.md:130` reads: `` `Lessons-swept:` line in baton (with session-id key after E5) `` — satisfied by the `[sid: ...]` token in the new format.

`ELUVIAN_PATH.md:120` reads: `3b lessons-swept with session-id key (E5 target — currently calendar-date keyed)` — satisfied by the keyed predicate in D-1.

---

## D-3 — The Glossary Bootstrap (R2)

### The ruling

`eluvian-path-rulings-2026-08-24.md`: **R2** — per-project `knowledge/glossary.md`.

The CEO decision (SESSION 58b, baton line 296): **`glossary.md` is the per-repo home for DOMAIN KNOWLEDGE**; `CLAUDE.md` stays operating protocol. Discriminator: DEFINITION → glossary, RUNBOOK → CLAUDE.md, **TRAP → CODE** (a doc you don't know to read cannot save you).

### Which projects have their own `.git`

Measured 2026-08-25:
```
OWN-GIT: ai-career-digest, anvil, bellows, BrewBuddy, forge,
         freight-kb, invoice-pulse, lessons-forge, SimpleScreen, study
NO-GIT:  Done, governance, knowledge, nonexistent, scratchpad
```

**10 repos** with their own `.git`. G3 confirms: **0** have a `knowledge/glossary.md` today. Positive control: `ls */knowledge/decisions` matches multiple repos — the `knowledge/` directory structure exists; the glossary does not.

### All 10 vs active-only

This is a CEO decision (D-7 item 1). The cost of scaffolding all 10 is trivial (one file each), but some projects are inactive (BrewBuddy, freight-kb, SimpleScreen) and an empty glossary in an untouched repo is noise. **Recommendation: active projects only** — those actively worked on in recent sessions. But "active" needs a ruling because the boundary may shift.

### The scaffold template

```markdown
# Glossary — <project-name>

Domain knowledge for this project. Discriminator: DEFINITION goes here;
RUNBOOK goes in CLAUDE.md; TRAP goes into CODE.

<!-- Entries below. Format: ## Term \n definition \n -->
```

Carrying the DEFINITION / RUNBOOK / TRAP discriminator per the SESSION 58b decision (baton line 296).

### Bootstrap mechanics: scaffold-on-first-use, not a bootstrap executable

A bellows-worktree dispatch operates within ONE repo. The 10 projects with glossaries are independent repos, each with its own `.git`. A bellows plan writing `knowledge/glossary.md` into these repos CANNOT commit into sibling repos from a bellows worktree.

**Options considered:**

| option | mechanics | cost |
|---|---|---|
| (1) Single bellows plan using `git -C` | Crosses repo boundaries from one dispatch. Requires commit rights in repos the plan doesn't own. | Complex, brittle — building a multi-repo commit mechanism that doesn't exist today, for 10 scaffold files. |
| (2) 10 separate per-repo dispatches | Correct isolation, one plan per repo. | 10 plans through the depositor pipeline (cycle_check, plan_lint, clearance, dispatch). Even auto-cleared as read-only, it's 10 cycles of the full lane. |
| (3) Scaffold-on-first-use rule in wrap.md | No bootstrap executable. The first domain-sweep (D-4) in each project creates the file. The wrap ritual doc mandates the template and location. | Zero dispatch complexity, zero cross-repo commit mechanics. The glossary appears incrementally as projects are actually swept. |

**Chosen: option 3 — scaffold-on-first-use.** The glossary file is created at wrap time when the domain sweep produces its first entry for that project, following the template in wrap.md. No executable needed.

---

## D-4 — The Domain-Sweep Ritual Step

### The wrap.md addition

A new step **3d** after 3b, before step 3:

```
3d. **Domain-knowledge sweep.** Ask: "what domain knowledge did this session
    surface that belongs in the project's glossary?" For each project touched
    this session, review the session's work and deposit any DEFINITIONS (not
    runbooks, not traps — per the glossary discriminator) into
    `<project>/knowledge/glossary.md`. If the file does not exist, create it
    with the scaffold template (## Glossary header, discriminator comment, entry
    format). If nothing qualifies, move on — the step is complete when the
    question has been asked, not when an entry has been written.
```

### Enforcement boundary — the honest design

`wrap_check` CAN verify:
- A `glossary.md` file **exists** for a touched project (`Path.exists()`).
- A `glossary.md` was **modified** this session (porcelain probe or mtime comparison).

`wrap_check` CANNOT verify:
- That the domain sweep was **thought about**.
- That the entries deposited are genuine **definitions** vs decoration to pass the gate.

**A touched-file gate would incentivize decoration** — the earn-the-gate lesson (LESSONS.md, "earn the clean gate, don't author it"). A gate that fires on "glossary not touched" incentivizes adding a trivial entry to pass it, which is worse than no gate: it pollutes the glossary with noise AND gives the false signal that a sweep happened.

**Chosen: ritual-only with visibility, no mechanical gate.** The domain sweep is a step in wrap.md. It is NOT checked by `wrap_check`. The sweep's completion is visible in the `Lessons-swept:` line's delta text (the `— <delta>` portion already describes what was done). A future escalation to a gate is possible if the ritual proves insufficient, but the gate would need to verify CONTENT quality, which is beyond what a file-existence or file-touch probe can do.

**Why this is the right call:** The 3b lessons-swept gate works because it verifies a RITUAL ACT (writing a line) that is isomorphic to the actual work (doing the sweep and recording what you found). A domain-knowledge gate would verify a SIDE EFFECT (file touched) that is not isomorphic to the work (thinking about what domain knowledge was surfaced). The gap between the probe and the intent is too wide for a mechanical gate.

---

## D-5 — Coordination

### wrap_check.py as shared substrate

`wrap_check.py` (blob `4ac15bfbea14…`) now carries three layers:
- The E3 `[2r/receipts]` group (`_check_receipts`, lines 170-322)
- The portability env-overrides (`ELUVIAN_WRAP_ROOT`, `ELUVIAN_WRAP_MEMORY`, lines 42-49)
- The 3b check (lines 136-151) — **E5's edit site**

The 3b edit is ADDITIVE (new predicate logic replaces lines 141-151 within the existing `# 3b:` block). It does not move, rename, or restructure the E3 or portability code. The `check()` function gains one parameter (`caller`) with a default.

**X-pin HALT discipline (G6):** The executable must not introduce regressions in the E3 or portability code. The 85-test regression floor (G7) is the guard.

### The mini machine's wrap flows (G8)

The mini wraps against its LOCAL baton clone. After `git fetch`, the baton carries sweep lines from both machines.

- **Stale-clone behavior:** If the mini hasn't fetched, the newest sweep line is from the mini's last wrap. If the mini is currently wrapping, it just wrote a new line → passes. If it hasn't, the newest is stale → fails correctly (the mini needs to sweep).

- **Post-fetch behavior:** After fetch, the shop's newer lines appear at the top. If the mini is wrapping and hasn't written its line yet, the newest line is the shop's → fails correctly. The mini sweeps, writes its line (prepended at top) → passes.

The measured lesson (baton line 50, Mac mini wrap): *"On a multi-machine shop, a wrap verdict is only as fresh as the last fetch."* The E5 keyed check does NOT change this property — it still judges the local baton. The wrap.md step 0 already mandates `git fetch` before the wrap.

### Root-repo writes

E5's scope touches lines in `ELUVIAN_PATH.md`:
1. **Line 120:** `3b lessons-swept with session-id key (E5 target — currently calendar-date keyed)` — update parenthetical to shipped state.
2. **Line 130:** `Lessons-swept: line in baton (with session-id key after E5)` — update parenthetical to shipped state.
3. **Line 131:** `Domain knowledge deposited in project's knowledge/glossary.md (after E5 builds R2)` — no change needed (the scaffold-on-first-use rule satisfies R2; the parenthetical can be updated to reflect "E5 shipped").

These are root-repo writes, `shop-infra` class.

**Routing:** There is an existing carried item in the baton (SESSION 64, line 18): *"Follow-up doc plan (small): ELUVIAN_PATH.md Stage 5 receipt-check line + portability-census RECEIPTS row (gap rows 10/12, routed out of 516 deliberately; root-repo writes → shop-infra class → the release arm now exists for it)."*

**Chosen: fold the E5 ELUVIAN_PATH.md edits INTO the existing follow-up doc plan** rather than carrying them separately. Rationale: the follow-up plan already collects ELUVIAN_PATH.md edits from the E-family; adding E5's three-line update avoids creating a separate plan for a trivial edit. The follow-up plan's scope grows by three lines; its class remains `shop-infra` (HELD for human review, released via the gated clear tool).

---

## D-6 — Test Plan

### Keyed-check arms (wrap_check.py)

| # | test | input | expected |
|---|---|---|---|
| 1 | newest-mine pass | baton with newest `[sid: <prefix>]` matching `session_id[:8]`, caller='stop' | PASS (no `[3b/lessons]` failure) |
| 2 | newest-foreign fail | baton with newest `[sid: <foreign>]`, caller='stop' | FAIL with message naming both sids |
| 3 | no-sid-in-line fail (stop) | baton with sweep line, no `[sid: ...]`, `session_id` present, caller='stop' | FAIL (historical format insufficient for keyed check) |
| 4 | no-session-id degrade | baton with sweep line + today's date, `session_id=None`, caller='stop' | DATE FALLBACK → PASS |
| 5 | no-session-id degrade miss | same but date does not match today | DATE FALLBACK → FAIL |
| 6 | debt-hook date-fallback pass | baton with any sweep line containing today, caller='debt' | PASS (date-only check) |
| 7 | debt-hook date-fallback fail | baton with no today-dated sweep line, caller='debt' | FAIL |
| 8 | historical-lines inert | baton with 21 historical lines + one new keyed line at top | only the keyed line (newest) is judged; historical lines not inspected |
| 9 | cross-machine newest | baton where newest line is from another machine's session, caller='stop' | FAIL (correct: this session hasn't swept) |
| 10 | cross-machine debt | same, caller='debt', today's date present | PASS (date-fallback) |
| 11 | blockquote-prefix | baton where newest sweep line has `> ` prefix | correctly parsed (`>` stripped before matching) |
| 12 | empty baton | no sweep lines | FAIL |
| 13 | prefix-match | `session_id` = full UUID, line has `[sid: <first-8-chars>]` | PASS (prefix match) |

### wrap.md

Doc changes only (steps 3b format update, new step 3d, glossary scaffold template). No mechanical tests — the ritual doc is not tested.

### Glossary scaffolds

No executable code → no tests. The scaffold is created by the wrapping session at ritual time, not by bellows-dispatched code. If the CEO decides a bootstrap executable instead (D-7 item 1), add existence tests for each scaffolded file.

### Regression floor (G7)

The 85-test floor (20 + 28 + 26 + 11) is **unchanged**. E5 ADDS tests (the 13-row table above); it does not modify existing tests. New tests belong in a new `test_wrap_3b_keyed.py` or as additions to `test_wrap_hooks.py`.

### 3b failure message consumer sweep

The `[3b/lessons]` message text changes (from the date-keyed message to the new sid-keyed messages). Any test fixture matching on the OLD message text would break. **Verified:** `grep -F "3b" tests/test_wrap_hooks.py tests/test_wrap_sentinel.py tests/test_wrap_receipts.py` — zero matches. No existing test asserts on the `[3b/lessons]` message text. The consumer-sweep lesson (LESSONS.md 2026-08-24, "a contract change's blast radius is its CONSUMERS") is satisfied: the contract's consumers are enumerated and none break.

---

## D-7 — Open Questions

**1. Glossary breadth (D-3).** All 10 own-git projects vs active-only? Recommendation: active-only (those actively worked on in recent sessions). The scaffold-on-first-use design (D-3) makes this a wrap.md instruction question ("which projects to sweep") rather than a bootstrap question. A ruling defines the scope.

**2. The degrade-arm choice (D-1 arm 4).** Date-fallback for no-session-id manual runs preserves the existing hole in manual invocations. If the CEO prefers hard-fail ("session id required"), manual `python wrap_check.py` runs without a session-id argument would always fail 3b. The enforcement posture changes from "manual runs degrade gracefully" to "manual runs require a session-id argument." Low impact (manual runs are rare and human-witnessed). This does NOT need a ruling if the design's recommendation (date-fallback) is accepted — it only needs a ruling if the CEO wants the stricter posture.

---

## Rule 27 Gap Table — Every Change Site the Executable Touches

| # | file | lines | change | class | decision |
|---|---|---|---|---|---|
| 1 | `hooks/eluvian/wrap_check.py` | 136-151 | Replace 3b predicate: whole-baton `any()` date-keyed → newest-line session-id-keyed with date-fallback arms. Add `_find_newest_sweep_line()` and `_extract_sid()` helpers. | bellows code | D-1 |
| 2 | `hooks/eluvian/wrap_check.py` | 90 | `check()` signature: add `caller: str = "stop"` parameter | bellows code | D-1 arm 5 |
| 3 | `hooks/eluvian/wrap_check.py` | 325-326 | `main()`: parse `sys.argv[2]` as `caller`, default `"stop"` | bellows code | D-1 |
| 4 | `hooks/eluvian/wrap_stop_hook.py` | ~207 | Subprocess call: append `"stop"` as argv[2] | bellows code | D-1 arm 5 |
| 5 | `hooks/eluvian/wrap_debt_hook.py` | ~87 | Subprocess call: append `"debt"` as argv[2] | bellows code | D-1 arm 5 |
| 6 | `hooks/commands/wrap.md` | 50-51 | Update 3b line format to include `[sid: <prefix>]` | bellows doc | D-2 |
| 7 | `hooks/commands/wrap.md` | after 51 | Add step 3d domain-knowledge sweep instruction + glossary scaffold template reference | bellows doc | D-4, D-3 |
| 8 | `tests/test_wrap_3b_keyed.py` | new file | Tests for all 13 keyed-check arms | bellows test | D-6 |
| 9 | `ELUVIAN_PATH.md` | 120, 130-131 | Update E5 parentheticals from target → shipped | **root-repo doc — routed to existing follow-up doc plan** | D-5 |

**Out of this executable's scope (by design):**
- Glossary files themselves — scaffold-on-first-use at wrap time, not a bootstrap (D-3).
- Historical `Lessons-swept:` lines — data, not violations; 21 lines stay untouched (MUST-PRESERVE §4).
- ELUVIAN_PATH.md edits — routed to the follow-up doc plan (D-5).
- The 85-test regression floor — unchanged; E5 only adds tests (D-6).
