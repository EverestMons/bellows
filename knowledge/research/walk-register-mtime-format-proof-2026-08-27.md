# Walk register — `mtime-format-proof-2026-08-27` (bellows)

**schema_version:** `0.3`

**Plan:** `bellows/knowledge/decisions/drafts/executable-mutation-self-application.md` (stable slug; corrected re-deposit after the exec-578 halt)
**Tier:** T1 (Small — a two-line invalidation fix plus a measurement-driven manifest edit; class shop-infra). **Panel: none.**
**Opened:** 2026-08-27

---

## Walk 0 — context pin (REAL, measured 2026-08-27)

1. **exec-578 halted CORRECTLY and the halt was my plan's fault.** Task B's stop arm said: if the flakiness does not reproduce, STOP. It did not reproduce for the agent (nobump KILLED 5/5, against my 4-SURVIVED/1-KILLED), so the agent stopped and reported. Nothing about its work was wrong.
2. **The agent's explanation was WRONG but CHECKABLE, which is the useful kind of wrong.** It attributed its result to APFS nanosecond-precision mtimes making the mutant write self-invalidating.
3. **⚠️ THE PREMISE IS PROVEN FROM THE FILE FORMAT, which retires the argument entirely.** A `.pyc` header stores the source mtime as a **32-bit SECONDS** field. Measured: `st_mtime_ns=1787850082018594620`, header `1787850082`, `header == int(st_mtime)` True. CPython DISCARDS sub-second resolution for cache validation, so a same-second, same-byte-length rewrite is invisible on ANY filesystem. Nanosecond mtimes do not help.
4. **Both measurements are therefore correct and the disagreement dissolves:** whether a given run crosses a second boundary decides the outcome. The agent's environment put more process startup between the baseline and mutation writes; mine did not. That is exactly the timing dependence the fix removes.
5. **What changes in this re-deposit:** the premise's GROUNDING (from trial counts to the format), and Task B's stop arm (non-reproduction is now RECORDED and the work PROCEEDS; the halt moves to the BUMP condition, which is the one that would mean nothing is worth shipping). The fix itself, the manifest logic, the two-path requirement and every other stop arm are UNCHANGED.
6. **Baselines re-verified live across both halts:** suite 1632 collected; manifest holds 3 mutants; `os.utime` absent from the runner.

⚠️ Walk 0 carries no fold rows. Walks 1+ appended AFTER the draft exists, from real passes. The exec-578 cycle's own three walks live in `walk-register-mutation-mtime-determinism-2026-08-27.md` and are not re-counted here.

---

## Walk 1 — five-lens sequential walk (post-draft, real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| w1-1 | 1 | Weak spots | can the new G1 probe actually run? | fold-introduced (the new format-proof pin) | the probe I wrote to PROVE the premise assumed `m.py` already existed — it compiles and stats that file without creating it. **Verified by running it: `FileNotFoundError: [Errno 2] No such file or directory: 'm.py'`.** A pin whose own probe cannot execute is worse than no pin: the agent would report a tooling failure on the one command that settles the plan's central claim | `python3 -c "import py_compile,os,struct; py_compile.compile('m.py','m.pyc',doraise=True); print(struct.unpack('<4sIII', open('m.pyc','rb').read(16))[2], os.stat('m.py').st_mtime_ns)"` | folded: made SELF-CONTAINED — `mktemp -d`, `printf 'X = 1\\n' > m.py`, then compile/stat/compare, printing header, ns and the equality. Re-run after the fold: `header 1787851050 ns 1787851050326399998 equal True` |
| — | 1 | Destruction | — | — | DRY — the fix is unchanged from exec-578's draft; only prose, one pin and one stop arm moved | — | no fold |
| — | 1 | Vulnerabilities | — | — | DRY — every other stop arm survives intact (the BUMP condition, Task D's manifest-follows-measurement, QA's second-path disagreement), and MUST-PRESERVE gained an explicit clause that non-reproduction is not a refutation | — | no fold |
| — | 1 | Integration-record | — | — | DRY — the register pointer was repointed to this file; deposits and scope unchanged | — | no fold |
| — | 1 | ACID | — | — | DRY | — | no fold |

**Walk 1 total: 1 finding (instruction 1 / record 0), folded. Direction verdict: PROCEED.**

---

## Walk 2 — five-lens sequential walk (real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| — | 2 | Weak spots | — | — | DRY — Task B now names BOTH nobump outcomes as expected and tells the agent which one implies what, so neither result leaves it guessing whether to proceed | — | no fold |
| — | 2 | Destruction | — | — | DRY | — | no fold |
| — | 2 | Vulnerabilities | — | — | DRY — the halt was MOVED rather than removed: it now sits on the bump condition, which is the outcome that would mean the fix does not work and nothing should ship | — | no fold |
| — | 2 | Integration-record | — | — | DRY — the historical references to exec-577 remain accurate (577 is where the mutant flaked); 578 is named as the halt this re-deposit answers | — | no fold |
| — | 2 | ACID | — | — | DRY | — | no fold |

**Walk 2 total: 0 findings — DRY.**

---

## Walk 3 — five-lens sequential walk (confirming pass, real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| — | 3 | Weak spots | — | — | DRY — the dev-log task now requires the G1 probe output AND a sentence on which nobump outcome occurred, so the record captures the disagreement's resolution rather than just a verdict | — | no fold |
| — | 3 | Destruction | — | — | DRY | — | no fold |
| — | 3 | Vulnerabilities | — | — | DRY | — | no fold |
| — | 3 | Integration-record | do the pins still hold after two halts? | — | DRY, re-verified LIVE rather than carried forward: suite 1632 collected, manifest holds 3 mutants, `os.utime` absent from the runner. Neither halt changed the tree, which is consistent with both halting before Task C | — | no fold |
| — | 3 | ACID | — | — | DRY | — | no fold |

**Walk 3 total: 0 findings — DRY. Two consecutive dry walks — BAR MET.**

---

## Conformance (§5) — recorded at the freeze from ACTUAL runs

- **The format proof (the plan's central claim), measured:** `header 1787851050 ns 1787851050326399998 equal True` — the `.pyc` header's seconds field equals `int(st_mtime)` while the filesystem carries nanoseconds, so sub-second changes are invisible to validation.
- **The probe's own failure and repair:** the first form raised `FileNotFoundError`; the self-contained form runs and prints the three values above.
- **Baselines re-verified live:** suite 1632; manifest 3 mutants; `os.utime` absent.
- **Fold verification (`/usr/bin/grep -cF` on the draft):** w1-1 landed ×1 (`SELF-CONTAINED`); the exec-578 stop-arm text verified GONE ×0 (`STOP and report rather than proceeding on my measurement`); the new Task-B wording present ×1 (`BOTH outcomes are expected and NEITHER is a halt`).
- **Structure:** `grep -cE '^## STEP '` → 2.
- **run_check at the freeze (2026-08-27, all branched-on; lint at the DEPOSIT path via a `lintmirror-` copy):** `lint` -> `VERDICT=PASS — exit 0`; exec-576's `(s)`/`(t)` BOTH SILENT; `cycle` -> `VERDICT=PASS — BAR_MET`; `register` -> `VERDICT=PASS — 1 CONFORMANT, 0 UNCONFORMANT` **on the first run** — the ellipsis and escaped-pipe traps both pre-empted at authoring, after four prior encounters this session.
- **fold_check (EARNED, not authored):** v0 reconstructed by restoring the broken probe form (anchor asserted x1), baselined, then the frozen draft diffed against it -> `FOLD-CHECK CLEAN: machine-readable state unchanged (7 signals held)`.

## Closing

**Walks 1-3, yields 1 → 0 → 0. BAR MET on walk 3. Cold panel not convened (T1, a two-line invalidation fix). Close is MANUAL (CEO-lane verdicts; auto_close false). The lesson this re-deposit encodes is about what a STOP ARM should key on. exec-578's arm keyed on whether a TRIAL reproduced, and a trial is a sample — so a correct agent in a slightly different environment halted a correct fix. The arm now keys on whether the FIX works (the bump condition), while the premise rests on a file-format fact that no sampling can refute. A stop arm should guard the claim that would make the work worthless, not the observation that happened to motivate it. The agent's contribution was essential: it disagreed precisely enough to be checked, which is what turned an unresolved measurement conflict into a settled structural fact.**
