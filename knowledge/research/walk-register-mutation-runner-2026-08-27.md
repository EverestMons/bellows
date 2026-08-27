# Walk register — `mutation-runner-2026-08-27` (bellows)

**schema_version:** `0.3`

**Plan:** `bellows/knowledge/decisions/drafts/executable-mutation-runner.md`
**Tier:** T1 (Small — one new tool that never writes the live tree, a data manifest, and its own tests; class shop-infra). **Panel: none.**
**Opened:** 2026-08-27

---

## Walk 0 — context pin (REAL, measured 2026-08-27)

1. **The CEO directive** (memory `mechanize-to-reserve-reasoning`, 2026-08-27): every check that CAN be arithmetic becomes code, so reasoning is spent only where it is irreducible. Thread 24 is sequenced FIRST of the arc because mutation AUDITS the other mechanisms — a state-space suite that looks principled but whose mutants all survive is decorative, and only mutation says so mechanically.
2. **The motivating defect:** exec-572 shipped a guard whose premise was false, past 7/7 gates, 8 dedicated tests and 5 walks. The question "would these tests have caught it?" was answerable only by reasoning, and the reasoning was the thing that was wrong.
3. **The two design points that decide honesty,** both pinned in the plan: (a) only pytest exit **1** counts as KILLED — exits 5 (no tests collected), 4, 3, 2 are ERROR, because a wrong selector otherwise scores KILLED and the tool manufactures the false confidence it exists to destroy; (b) every mutant gets a **baseline** run on pristine code required to exit 0, the positive control the negative-probe law demands.
4. **Sandbox mechanism measured:** `git archive HEAD | tar -x` reproduces the tracked tree with no `.git` — 4719 files, 30.2 MB. Extract ONCE, mutate per-mutant, restore between, so the cost is one extraction rather than N.
5. **Both mutants are EARNED, not invented** — each reproduces a defect actually shipped this session: M1 the exec-572 suppression mode, M2 the exec-571 phantom-arm detection. Anchors verified at authoring to match **exactly once** against the shipped file.
6. **Baselines:** `tests/test_gate_watcher.py` collects 46; full suite 1611 passed + 1 skipped = 1612.

⚠️ Walk 0 carries no fold rows. Walks 1+ appended AFTER the draft exists, from real passes.

---

## Walk 1 — five-lens sequential walk (post-draft, real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| w1-1 | 1 | Weak spots | which code does the sandbox actually judge? | pre-existing | `git archive HEAD` archives the last COMMIT, so the tool audits committed code and uncommitted edits to the target are INVISIBLE. A clean mutation report about code the author is not looking at is precisely the false confidence this tool exists to remove, and nothing in the draft surfaced the gap | `Flow: read the live target's sha256; git archive HEAD \| tar -x -C <mktemp -d>; keep a pristine copy of the sandbox target in memory; then per mutant:` | folded: a `git status --porcelain -- <target>` check before extraction printing `WARNING: target has uncommitted changes — this run audits HEAD, not your working tree`, the warning carried into the summary line, and the HEAD sha stated in the report so every result names the code it judged |
| w1-2 | 1 | Destruction | what happens to the sandbox on an exception? | pre-existing | the extraction and per-mutant loop had no `try/finally`, so a crash mid-run leaks a 30 MB temp tree | (same flow sentence as w1-1, before the fold) | folded: the whole run wrapped in `try/finally` so the sandbox is removed even on an exception (`--keep-sandbox` still honored) |
| w1-3 | 1 | Vulnerabilities | can the QA step corrupt its own measurement? | pre-existing | ⚠️ the draft barred QA from editing the TARGET and its TESTS, but said nothing about the MANIFEST — which IS in this plan's scope. Retuning an anchor, replacement or selector until the result turns green is the same corruption through an easier door, and it looks like fixing the tool rather than faking the result | `⚠️ **Do NOT edit tests/test_gate_watcher.py or tools/gate_watcher.py in this step under any circumstance** — they are outside this plan's Scope, and "fixing" a survivor here would destroy the measurement. A survivor is reported and routed, never patched.` (no manifest clause) | folded: an explicit second prohibition covering `knowledge/mutants/gate_watcher.json`, stating that the manifest is IN scope so the bar must be written rather than relied on, and routing a bad-anchor ERROR to a follow-up plan instead of an in-measurement correction |
| — | 1 | Integration-record | — | — | DRY — manifest writes list all seven files; the deposits and scope blocks agree; thread-24 promote step and thread-23 pairing recorded in open_forks | — | no fold |
| — | 1 | ACID | — | — | DRY — two pathspec-limited commits (4 files, then 3), toplevel-first, each with a `git show --stat` assert | — | no fold |

**Walk 1 total: 3 findings (instruction 3 / record 0), folded. Direction verdict: PROCEED — the manifest-plus-sandbox shape held.**

---

## Walk 2 — five-lens sequential walk (real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| — | 2 | Weak spots | — | — | DRY — **both mutant anchors verified live at authoring**: M1's three-line anchor and M2's single line each `count() == 1` against the shipped `tools/gate_watcher.py`. A wrong anchor would degrade to ERROR rather than a false KILL (the fail-safe working), but verifying now avoids burning a QA run | — | no fold |
| — | 2 | Destruction | — | — | DRY — the tool writes only inside `mktemp -d`; the live-tree sha256 assertion is a positive control, not a comment | — | no fold |
| — | 2 | Vulnerabilities | — | — | DRY — the empty-selector trap is covered TWICE, synthetically (test 3) and against the real tool (QA Item 3); `expect_fail` names a class node id, and the drift guard's SKIP inside that class does not make pytest exit non-zero, so the required green baseline holds | — | no fold |
| — | 2 | Integration-record | — | — | DRY | — | no fold |
| — | 2 | ACID | — | — | DRY | — | no fold |

**Walk 2 total: 0 findings — DRY.**

---

## Walk 3 — five-lens sequential walk (confirming pass, real)

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| — | 3 | Weak spots | — | — | DRY — Task B verifies the C1 exit-code pin EMPIRICALLY before the runner is built on it, with a STOP arm if pytest's empty-selection code is not 5 on this build | — | no fold |
| — | 3 | Destruction | — | — | DRY | — | no fold |
| — | 3 | Vulnerabilities | — | — | DRY — QA Item 2 explicitly does NOT require the mutants to be killed and names SURVIVED as a valuable finding, so the step cannot be pressured toward a green result | — | no fold |
| — | 3 | Integration-record | — | — | DRY — the self-application fork (a mutant that makes the runner score exit 5 as KILLED, expecting `test_empty_selector_is_error_not_killed` to fail) recorded in open_forks with its regress limit stated | — | no fold |
| — | 3 | ACID | — | — | DRY | — | no fold |

**Walk 3 total: 0 findings — DRY. Two consecutive dry walks — BAR MET.**

---

## Conformance (§5) — recorded at the freeze from ACTUAL runs

- **Anchor verification (2026-08-27, run against the shipped file):** M1 three-line anchor `count == 1`; M2 anchor `count == 1`. Recorded because a mutant manifest whose anchors do not match is a manifest that measures nothing.
- **Fold verification (`/usr/bin/grep -cF` on the draft):** w1-1 landed ×1 (`this run audits HEAD, not your working tree`); w1-2 landed ×1 (`try/finally`); w1-3 landed ×1 (`Nor may you edit`). Superseded text verified ×0 for the pre-fold flow sentence.
- **Structure:** `grep -cE '^## STEP '` → 2.
- **run_check runs at the freeze (2026-08-27, all branched-on; lint at the DEPOSIT path via a `lintmirror-` copy in the real `decisions/`):** `lint` → `VERDICT=PASS — exit 0`; `cycle` → `VERDICT=PASS — BAR_MET`; `register` → `VERDICT=PASS — 1 CONFORMANT, 0 UNCONFORMANT` on the first run (the ellipsis-in-`pre_fold_text` trap pre-empted at authoring for the second consecutive plan).
- **fold_check (EARNED, not authored):** v0 reconstructed by reversing the w1-3 manifest-prohibition fold (anchor asserted ×1), baselined, then the frozen draft diffed against it → `FOLD-CHECK CLEAN: machine-readable state unchanged (8 signals held)`. A post-fold baseline would have been a tautology.

## Closing

**Walks 1-3, yields 3 → 0 → 0. BAR MET on walk 3's dry confirming pass. Cold panel not convened (T1 additive tooling that never writes the live tree; 563/569/571/573 precedent). Close is MANUAL (CEO-lane verdicts; auto_close false). The walk that mattered was w1-3: the plan had carefully barred the QA step from patching the code under measurement while leaving the MANIFEST — the instrument itself — editable. A measurement whose instrument can be retuned until it agrees is not a measurement, and that door was open in a plan whose entire purpose is to remove reasoning from verification.**
