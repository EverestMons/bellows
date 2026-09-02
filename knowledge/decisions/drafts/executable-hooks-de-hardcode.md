# bellows — executable: THE HOOKS LEARN THE TWO HOMES — four session hooks and the /wrap command text drop the shop literal (marker-verified default, env precedence kept), the wrap twin's third candidate becomes the projects parent; the persona-contract line severed to its own touch

**Date:** 2026-09-02 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** targeted (`tests/test_hook_default_root.py` NEW; `tests/test_wrap_hooks.py`, `tests/test_align_hook_sync.py`, `tests/test_wrap_sentinel.py`, `tests/test_wrap_receipts.py`, `tests/test_wrap_3b_keyed.py`, `tests/test_wrap_memory_class_gate.py`, `tests/test_wrap_r2_registry.py`, `tests/test_plan_claim.py`) + a full-suite CONTROL COMPARISON in the worktree shape (set EMPTY) + the four hooks imported under the HARNESS interpreter `/usr/bin/python3` | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always | **known_failures:** 0 | **Priority:** 2

**auto_close:** false

**Slug:** `hooks-de-hardcode-2026-09-02`

**Depends on:** the CEO's "All three" (2026-09-02 00:0x — the overnight list, this plan second); plan 100011's severance (its does-NOT section named these seven sites as the bound follow-up `hooks-de-hardcode`) and its resolver semantics (`Done/executable-100012.md` + `halted-executable-100011.md`; `bellows_root.resolve_governance_root` / `resolve_projects_parent` on main at `6b892a3`); `hooks/README.md` (the repo is the canonical copy; `~/.claude/eluvian/` is the LIVE location the harness loads — copies, not links, measured); `tests/test_plan_claim.py::TestResolverTwin` (the twin contract between `plan_claim._tuyere_checkout` and `wrap_check._tuyere_checkout`). Clone origin by kind: 100012 (tests-only shape) and 100011 (the resolver's candidate discipline). Walk register: `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-hooks-de-hardcode-2026-09-02.md`.

**Tier computed, not judged (§1):** **T-1 fires** (five files in one subsystem — the four hooks and the command text). **T-3 fires** — the hooks run under the HARNESS's interpreter, `/usr/bin/python3` 3.9.6 (measured), not the bellows venv 3.12: a different execution environment; QA imports every changed hook under it. **T-8 fires** (a clone by kind). **T-6, priced and SEVERED:** `agents/BELLOWS_DEVELOPER.md:66` carries the literal in a sentence about `.claude/settings.local.json` — that file is a SPECIALIST CONTRACT under §1's words, so touching it fires T-6 and a panel; the sentence is documentation of a path, on no code path, and a one-line contract edit does not deserve a five-seat ceremony riding a hooks plan. Split on tier (§1): it stays named here and untouched — the remainder re-computes to **T1: the five-lens walk, no panel.** The hooks themselves are session tooling with a test suite (seven files, 134 tests), not doctrine, template, gates or contracts.

## Why this exists — measured 2026-09-02 on the mini at bellows `3b0c19c`

Four hooks in `hooks/eluvian/` and the `/wrap` command text carry `/Users/marklehn/Developer/GitHub` as the fallback when `$ELUVIAN_WRAP_ROOT` is unset (`wrap_arm_hook.py:36`, `wrap_stop_hook.py:34` as `_DEFAULT_ROOT`; `wrap_check.py:43-44` as `ROOT`; `eluvian_align_hook.py:21-22` as `_GOV_ROOT`; `hooks/commands/wrap.md:36` as a shell default and `:80` as a bare path). The harness sets the variable (one `env` entry in `~/.claude/settings.json`, measured), so the literal is dormant today — and dormant is the class 100011 removed from the daemon: a fallback that names one machine is wrong on every other one the moment the override is absent (a fresh machine before its settings are placed, a hook run by hand, a test that deletes the variable). And `wrap_check._tuyere_checkout`'s third candidate is `ROOT / "tuyere"` — the governance root — while its declared twin `plan_claim._tuyere_checkout` now (100011) uses the PROJECTS PARENT; on the shop the two coincide, on the mini `ROOT/tuyere` is `eluvian-governance/tuyere`, which does not exist. The twins must diverge nowhere.

Two facts shape the fix. (1) The hooks are STANDALONE files: no bellows module on their path, and the harness runs COPIES from `~/.claude/eluvian/` (five files, byte-identical to the repo — `cmp` ×5, measured), so a shared helper module would be a sixth file to install and a new way for the copies to drift. The resolver is therefore duplicated verbatim in the four hooks, with a test asserting the four bodies stay identical. (2) A hook must never crash a session: the default resolves the two known homes by their `COMPANY.md` marker and falls back to the first name if neither holds it — a wrong-but-quiet default, never a traceback in the harness.

## What this plan does

- **E1 `hooks/eluvian/wrap_arm_hook.py`** — anchor `_DEFAULT_ROOT = Path("/Users/marklehn/Developer/GitHub")\n` (count 1) → the helper `_default_root()` (the exact text below) followed by `_DEFAULT_ROOT = _default_root()\n`.
- **E2 `hooks/eluvian/wrap_stop_hook.py`** — the same anchor (count 1), the same replacement.
- **E3 `hooks/eluvian/wrap_check.py`** — anchor the two lines `ROOT = Path(os.environ.get("ELUVIAN_WRAP_ROOT")\n            or "/Users/marklehn/Developer/GitHub")\n` (count 1) → the helper, then `ROOT = Path(os.environ.get("ELUVIAN_WRAP_ROOT") or _default_root())\n`.
- **E4 `hooks/eluvian/eluvian_align_hook.py`** — anchor the two lines `_GOV_ROOT = Path(os.environ.get("ELUVIAN_WRAP_ROOT")\n                 or "/Users/marklehn/Developer/GitHub")\n` (count 1) → the helper, then `_GOV_ROOT = Path(os.environ.get("ELUVIAN_WRAP_ROOT") or _default_root())\n`.
- **E5 `hooks/eluvian/wrap_check.py:150`** — anchor `    candidates.append(ROOT / "tuyere")\n` (count 1) → `    candidates.append(_resolve_bellows(ROOT).parent / "tuyere")  # the PROJECTS PARENT — plan_claim's twin since 100011\n`. `_resolve_bellows` already knows both shapes (`<root>/bellows` on the shop, `<root>/../bellows` on the mini, by the `status.py` marker), so its parent IS the projects parent on both; where neither exists it returns `root / "bellows"`, whose parent is `root` — the old behaviour, unchanged.
- **E6 `hooks/commands/wrap.md:36`** — anchor `touch "${ELUVIAN_WRAP_ROOT:-/Users/marklehn/Developer/GitHub}/.wrap-in-progress"` (count 1) → `touch "${ELUVIAN_WRAP_ROOT:?ELUVIAN_WRAP_ROOT is unset — the harness sets it; see MACHINE_SETUP.md §1}/.wrap-in-progress"` (a loud shell failure beats a silent write into another machine's path).
- **E7 `hooks/commands/wrap.md:80`** — anchor `glossary at `/Users/marklehn/Developer/GitHub/GLOSSARY.md`` (count 1) → `glossary at `$ELUVIAN_WRAP_ROOT/GLOSSARY.md``.
- **E8 NEW `tests/test_hook_default_root.py`** (DEV writes it to this spec): loads each of the four hooks by path with `importlib.util.spec_from_file_location` under a monkeypatched `Path.home` (a `tmp_path` home) and with `ELUVIAN_WRAP_ROOT`, `ELUVIAN_WRAP_BELLOWS`, `ELUVIAN_WRAP_TUYERE` deleted; tests: (a) with `tmp/Developer/eluvian-governance/COMPANY.md` present → each hook's `_default_root()` returns it; (b) with only `tmp/Developer/GitHub/COMPANY.md` → returns that; (c) with neither → returns `tmp/Developer/eluvian-governance` and raises nothing; (d) `inspect.getsource(<hook>._default_root)` is identical across the four (the duplication guard); (e) the wrap twin, shop shape: env root `tmp/root` with `root/bellows/status.py` and `root/tuyere/.venv/bin/python` → `wrap_check._tuyere_checkout()` is `root/tuyere`; (f) the wrap twin, mini shape: env root `tmp/gov` (no `bellows/` inside), `tmp/bellows/status.py`, `tmp/tuyere/.venv/bin/python` → `tmp/tuyere` — the projects parent, not `gov/tuyere`; (g) env precedence: `ELUVIAN_WRAP_ROOT` set to a directory WITHOUT the marker → `wrap_check.ROOT` is that directory (the override is authoritative, as today).

**The helper, byte-identical in all four hooks (E1–E4), placed immediately above the line it replaces:**
```
def _default_root() -> Path:
    """The governance root when $ELUVIAN_WRAP_ROOT is unset: the two known homes,
    admitted only by their COMPANY.md marker; the first if neither holds it — a
    hook must never crash a session. Duplicated verbatim in the four hooks by
    design: they are standalone files copied into ~/.claude/eluvian/, and a
    shared module would be one more file to install (test_hook_default_root
    asserts the four bodies stay identical). Plan hooks-de-hardcode, 2026-09-02."""
    for cand in (Path.home() / "Developer" / "eluvian-governance",
                 Path.home() / "Developer" / "GitHub"):
        if (cand / "COMPANY.md").is_file():
            return cand
    return Path.home() / "Developer" / "eluvian-governance"
```

## What this plan does NOT do

- Does not touch `agents/BELLOWS_DEVELOPER.md:66` (severed above — a specialist contract; named, not done) or `wrap_debt_hook.py` (no root literal — measured).
- **Does not install.** The harness loads `~/.claude/eluvian/*.py`, copies of the repo files (`hooks/README.md`). Copying the four changed hooks there is the operator's per-machine act after this plan closes (the Planner's session on the mini tonight; the shop's on its next wrap) — outside any worktree, like a daemon restart, and named for `MACHINE_SETUP.md`. Until it happens the LIVE hooks keep the literal, dormant behind the env variable. The canary is one command on the installed copy with the variable removed.
- Does not change what happens when the variable IS set (every existing hook test sets it; all 134 must still pass unchanged).

## MUST-PRESERVE

- **A hook never raises on a missing root.** The helper returns a name, marker or not; the loud failure belongs to `/wrap`'s shell line (E6), which runs in a terminal a human reads.
- **Env precedence is unchanged at all four sites** — `$ELUVIAN_WRAP_ROOT` wins whenever set, marker or not (test (g)); the helper is only the fallback.
- **The four helper bodies are identical** (test (d)); a later edit to one of them is a test failure by construction.
- **The twin semantics:** `wrap_check`'s third candidate is the projects parent via `_resolve_bellows(ROOT).parent`, which equals `ROOT` wherever `_resolve_bellows` falls back — so every existing behaviour with a populated `<root>/bellows` or no bellows at all is byte-identical; only the sibling shape changes, to the correct directory.
- **`known_failures: 0`** with the gate's count semantics (100011's MUST-PRESERVE); the worktree set is EMPTY since 100012; the flake protocol applies.

## Numbers discipline — the pins DEV re-derives (measured 2026-09-02 by the Planner at bellows `3b0c19c`)

| pin | what | value | how |
|---|---|---|---|
| P1 | **`TARGET_SHAS`** | `hooks/eluvian/wrap_arm_hook.py` `37c0f8af28df9fa6` · `hooks/eluvian/wrap_stop_hook.py` `571b2552ab347e46` · `hooks/eluvian/wrap_check.py` `c840bbfae2ad8ff9` · `hooks/eluvian/eluvian_align_hook.py` `61e64c61a8f59804` · `hooks/commands/wrap.md` `11a0af73cc11378f` | `shasum -a 256 <f> \| cut -c1-16` |
| P2 | **`ANCHORS`** — E1–E7, each count 1 (E3 and E4 are two-line anchors — count with a script) | **7** anchors, all 1 | `/usr/bin/grep -cF -- '<anchor>' <f>` (single-line), a script for the two-line ones |
| P3 | **`TOKENS`** post-edit | `def _default_root` → 1 in each of the four hooks (4 total); `/Users/marklehn/Developer/GitHub` → 0 in all five files (pre: 1 each in the four hooks, 2 in `wrap.md`); `_resolve_bellows(ROOT).parent / "tuyere"` → 1 in `wrap_check.py`; `ELUVIAN_WRAP_ROOT:?` → 1 in `wrap.md` | same |
| P4 | **`HOOK_SUITE_PRE`** — the seven hook test files | `134 passed` | `"$PY" -m pytest -q -p no:cacheprovider tests/test_wrap_hooks.py tests/test_align_hook_sync.py tests/test_wrap_sentinel.py tests/test_wrap_receipts.py tests/test_wrap_3b_keyed.py tests/test_wrap_memory_class_gate.py tests/test_wrap_r2_registry.py` |
| P5 | **`HARNESS_PY`** | `/usr/bin/python3` is `Python 3.9.6`; each of the four hooks imports under it (`importlib.util.spec_from_file_location`) with the env variable SET — `imports OK` ×4 pre-edit | `/usr/bin/python3 --version`; the import one-liner in QA Item 4 |
| P6 | **`INSTALLED_COPIES`** — repo vs `~/.claude/eluvian/` | `IDENTICAL` ×5 pre-edit (the four hooks + `wrap_debt_hook.py`); NOT touched by this plan | `cmp -s hooks/eluvian/<f>.py ~/.claude/eluvian/<f>.py` |
| P7 | **`SUITE_POST`** — full suite, WORKTREE shape | failing set EMPTY; passed ≥ **1669 + the new tests** (100012's QA measured `1669 passed, 1 skipped` in the worktree; the skip is the live-DB test's location property) | `"$PY" -m pytest tests -q -p no:cacheprovider` |

## STEP 1 — DEV

> **FIRST — post a short visible chat message (1–2 sentences).** Do NOT rename this file. You are the Bellows Developer.
>
> ⛔ **A0 — pre-flight.** `cd "$(git rev-parse --show-toplevel)" && [ -f bellows.py ] && [ -f hooks/eluvian/wrap_check.py ] && echo TREE_OK` — HALT unless TREE_OK. `MAIN=$(cd "$(git rev-parse --git-common-dir)/.." && pwd); PY="$MAIN/.venv/bin/python"; [ -x "$PY" ] && echo VENV_OK || echo NO_VENV` — HALT unless VENV_OK. Re-derive `PY` in every compound; zsh arrays for lists; `/usr/bin/grep -F` with `--` for every literal.
>
> ⛔ **A1 — re-derive P1, P2, P3-pre, P4, P5, P6; state each; a mismatch is a HALT quoting both values.**
>
> **A2 — the seven edits, with a script that asserts each anchor count BEFORE editing** (never a blind global replace). E1–E4 insert the helper text EXACTLY as given (copy it from this plan into a heredoc once, insert it four times — that is how the bodies stay identical) immediately above the replaced line; E5–E7 as stated. Then P3-post; `"$PY" -m py_compile` on the four hooks; and under the harness interpreter: `for f in wrap_arm_hook wrap_stop_hook wrap_check eluvian_align_hook; do env -u ELUVIAN_WRAP_ROOT /usr/bin/python3 -c "import importlib.util; s=importlib.util.spec_from_file_location('$f','hooks/eluvian/$f.py'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print('$f', m._default_root())"; done` → four lines, each ending `/Users/marklehn/Developer/eluvian-governance` (this machine's marker-verified home).
>
> **A3 — write `tests/test_hook_default_root.py` to E8's spec** (seven tests a–g; a module-level helper that loads a hook by path; `monkeypatch.delenv` the three variables and `monkeypatch.setattr(Path, "home", ...)` in every test; for (e)/(f) reload `wrap_check` AFTER setting the env root, since it computes `ROOT` at import). Then: `"$PY" -m pytest -q -p no:cacheprovider tests/test_hook_default_root.py` → `7 passed`; the seven hook files (P4's command) → `134 passed`; `tests/test_plan_claim.py` → `49 passed` (the twin test still holds); the full suite from your worktree (P7) → no `FAILED` line, `N passed` with N ≥ 1676; a flake → re-run that file once, FLAKE-PASSED-ON-RERUN or HALT.
>
> **A4 — dev-log + commit by explicit pathspec.** `knowledge/development/dev-log-hooks-de-hardcode-2026-09-02.md`: A1's pins as measured, the seven anchor counts, P3 post, the four harness-interpreter lines, the A3 summary lines verbatim. `T=(hooks/eluvian/wrap_arm_hook.py hooks/eluvian/wrap_stop_hook.py hooks/eluvian/wrap_check.py hooks/eluvian/eluvian_align_hook.py hooks/commands/wrap.md tests/test_hook_default_root.py knowledge/development/dev-log-hooks-de-hardcode-2026-09-02.md); git add "${T[@]}" && git commit -m "[<id from your plan filename>] hooks learn the two homes: marker-verified default root in four hooks, /wrap text, the wrap twin's third candidate is the projects parent; seven tests" -- "${T[@]}"`. `git status --short` → empty. STOP.
>
> **Deposits:**
> - `knowledge/development/dev-log-hooks-de-hardcode-2026-09-02.md`
> - `hooks/eluvian/wrap_arm_hook.py`
> - `hooks/eluvian/wrap_stop_hook.py`
> - `hooks/eluvian/wrap_check.py`
> - `hooks/eluvian/eluvian_align_hook.py`
> - `hooks/commands/wrap.md`
> - `tests/test_hook_default_root.py`
>
> **Scope:**
> - `knowledge/development/dev-log-hooks-de-hardcode-2026-09-02.md`
> - `hooks/eluvian/wrap_arm_hook.py`
> - `hooks/eluvian/wrap_stop_hook.py`
> - `hooks/eluvian/wrap_check.py`
> - `hooks/eluvian/eluvian_align_hook.py`
> - `hooks/commands/wrap.md`
> - `tests/test_hook_default_root.py`

## STEP 2 — QA

> **Step 1's Receipt status must be `Status: Complete`.** Anything else → HALT. **FIRST — post a short visible chat message.** You are the Bellows QA agent. `cd "$(git rev-parse --show-toplevel)"`; re-derive `PY` as in A0; re-declare the array `T` (A4's) in every compound that uses it.
>
> **(A) Rule 20 self-check** — the canonical block from the path the dispatcher's mandate names (since plan 100011 and the 2026-09-01 restart it is this machine's `RULE_20_SELF_CHECK_BLOCK.md`; quote the path you were handed in the report). Run with:
> - `plan_slug`: `hooks-de-hardcode-2026-09-02`
> - `qa_report_path`: `"$(pwd)/knowledge/qa/evidence/hooks-de-hardcode-2026-09-02/qa-receipt.md"`
> - `evidence_dir`: `"$(pwd)/knowledge/qa/evidence/hooks-de-hardcode-2026-09-02"`
> - `required_evidence_files`: `["probes-raw.txt", "full-suite-hooks-de-hardcode.txt"]`
>
> **(B) Items — raw output appended to `probes-raw.txt` (`mkdir -p` the evidence dir first):**
> - **Item 1 — the edits are what the plan says:** P3-post counts, each as a `/usr/bin/grep -cF` line; `git show --stat HEAD --format=` lists exactly the seven declared paths.
> - **Item 2 — the four bodies are one body:** `for f in wrap_arm_hook wrap_stop_hook wrap_check eluvian_align_hook; do "$PY" -c "import importlib.util,inspect; s=importlib.util.spec_from_file_location('$f','hooks/eluvian/$f.py'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(__import__('hashlib').sha256(inspect.getsource(m._default_root).encode()).hexdigest()[:16])"; done` → four IDENTICAL lines.
> - **Item 3 — the full suite with the CONTROL COMPARISON (P7):** `"$PY" -m pytest tests -q -p no:cacheprovider > knowledge/qa/evidence/hooks-de-hardcode-2026-09-02/full-suite-hooks-de-hardcode.txt 2>&1; echo "exit=$?" >> knowledge/qa/evidence/hooks-de-hardcode-2026-09-02/full-suite-hooks-de-hardcode.txt`; the `FAILED` set must be EMPTY (the CWD survivor cannot appear in a worktree — if it does, HALT); any other id → re-run once, FLAKE-PASSED-ON-RERUN or Critical; state N ≥ 1676 and the skip count.
> - **Item 4 — the harness interpreter (T-3):** A2's `env -u ELUVIAN_WRAP_ROOT /usr/bin/python3 …` loop → four lines ending `/Users/marklehn/Developer/eluvian-governance`; then the same loop WITH `ELUVIAN_WRAP_ROOT=/tmp/no-marker-here` (create the dir, no `COMPANY.md`) reading `m.ROOT` for `wrap_check`, `m._GOV_ROOT` for the align hook, `m._wrap_root()` for arm/stop → all four `/tmp/no-marker-here` (env precedence, marker or not).
> - **Item 5 — the twin on THIS machine, both sides:** `env -u ELUVIAN_WRAP_ROOT -u ELUVIAN_WRAP_TUYERE "$PY" -c "import importlib.util, plan_claim; s=importlib.util.spec_from_file_location('wc','hooks/eluvian/wrap_check.py'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(m._tuyere_checkout()); print(plan_claim._tuyere_checkout())"` → two identical lines, `/Users/marklehn/Developer/tuyere`.
> - **Item 6 — the sweep over the hooks tree and the command text:** `/usr/bin/grep -rlF --exclude-dir=__pycache__ -- '/Users/marklehn/Developer/GitHub' hooks; echo "exit=$?"` → NO files, `exit=1`; liveness pair: `/usr/bin/grep -cF -- '"GitHub"' hooks/eluvian/wrap_check.py` → 1 (the helper's second candidate is built from path COMPONENTS — `Path.home() / "Developer" / "GitHub"` — so the string `Developer/GitHub` does not occur in the post-edit file; the component literal does, once, and that is the hit that proves the grep is alive).
> - **Item 7 — the installed copies are untouched by this plan (P6, and the operator's act is still owed):** `for f in wrap_arm_hook wrap_stop_hook wrap_check eluvian_align_hook; do cmp -s hooks/eluvian/$f.py ~/.claude/eluvian/$f.py && echo "SAME $f" || echo "DIFFERS $f"; done` → four `DIFFERS` (the repo moved, the live copies did not — expected; state it as the Restart-Discipline-shaped fact it is).
>
> **(C) The report** `qa-receipt.md`: the verification table, the install note (the live hooks are copies; the operator copies the four files to `~/.claude/eluvian/` after close and runs Item 4's first loop against the copies as the canary), the Rule 20 stdout APPENDED. Commit: `git add knowledge/qa/evidence/hooks-de-hardcode-2026-09-02/ && git commit -m "[<id>] QA: hooks de-hardcode — four identical bodies, harness interpreter both ways, twin both sides, sweep empty" -- knowledge/qa/evidence/hooks-de-hardcode-2026-09-02/`. STOP.
>
> **Deposits:**
> - `knowledge/qa/evidence/hooks-de-hardcode-2026-09-02/qa-receipt.md`
> - `knowledge/qa/evidence/hooks-de-hardcode-2026-09-02/probes-raw.txt`
> - `knowledge/qa/evidence/hooks-de-hardcode-2026-09-02/full-suite-hooks-de-hardcode.txt`
>
> **Scope:**
> - `knowledge/qa/evidence/hooks-de-hardcode-2026-09-02/qa-receipt.md`
> - `knowledge/qa/evidence/hooks-de-hardcode-2026-09-02/probes-raw.txt`
> - `knowledge/qa/evidence/hooks-de-hardcode-2026-09-02/full-suite-hooks-de-hardcode.txt`

Rule 20 banner (byte-exact, produced by RUNNING the canonical block — never hand-authored):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```

---

## Drafting Cycle

**Tier:** T1 — T-1, T-3, T-8 fire; T-6 severed (the persona-contract line). Five-lens walk, no panel.

**Walk register:** /Users/marklehn/Developer/eluvian-governance/governance/knowledge/research/walk-register-hooks-de-hardcode-2026-09-02.md

**Walk 0 (context pin, measured):** the five target shas; seven anchors counted (1 each, two of them two-line); the installed copies compared (`cmp` ×5 IDENTICAL — copies, not links; the README's "repoint" never landed); the harness interpreter identified (`/usr/bin/python3` 3.9.6) and the four hooks imported under it; the hook suite `134 passed`; `_resolve_bellows` and `_tuyere_checkout` read at source (the twin's fallback equals `root`); the consumer dry-run (§2.0) on the register's walk-0 line.

**Direction verdict (after walk 1): PROCEED.** Tested: the premise (seven sites measured, the live copies measured as copies), the mechanism (seven anchored edits, a helper inserted from one heredoc four times, a test that pins the four bodies together, the twin's parent via `_resolve_bellows`), the scope (the persona-contract line severed by tier, the install step named as the operator's).

**Walks:**
- Weak spots:          w1 1 folded — instruction 1 / record 0 (Item 6's liveness pair grepped for `Developer/GitHub`, a string the post-edit helper never contains — it builds the path from components — so the pair would read 0 and the empty sweep would carry no proof of life; now the component literal `"GitHub"` → 1)
- Destruction:         w1 dry — a hook can only get QUIETER (a marker-verified name or the first name, never a raise); the twin's parent equals `ROOT` wherever `_resolve_bellows` falls back, so every existing behaviour is byte-identical; E6's `:?` moves one failure from silent to loud, in a terminal a human reads; the live copies are untouched by the plan (Item 7 expects them to lag)
- Vulnerabilities:     w1 dry — T-3 proven under the harness interpreter both ways (env unset → the marker home; env set to a markerless dir → the env dir); `wrap_check` reloaded after the env is set in tests (e)/(f) because it computes `ROOT` at import; zsh arrays; `--` before literals; no `-k` selectors
- Integration-record:  w1 2 folded — instruction 0 / record 2 (the manifest's `class: pending` → `shop-infra`, the depositor's measured assignment — a hold, released under the standing sentence; the helper's docstring said "a fifth file" where the Why says "a sixth" — the installed set is five files, so a shared module would be the sixth — reworded to "one more file")
- ACID:                w1 dry — one DEV commit of seven paths by explicit pathspec, one QA commit of the evidence dir; the four helper bodies asserted identical by test (d) so a half-applied E1–E4 fails A3, never lands
- **Walk 1 total: 3 findings, 3 folded — instruction 1 / record 2; 0 of 3 fold-introduced.**
- Weak spots:          w2 dry — instruction 0 / record 0 — E1–E7 re-read as written; the helper text re-read once against its four insertion sites
- Destruction:         w2 dry — instruction 0 / record 0 — unchanged
- Vulnerabilities:     w2 dry — instruction 0 / record 0 — unchanged
- Integration-record:  w2 dry — instruction 0 / record 0 — `propagation_check` clean; the manifest below is the emitter's, spliced at the freeze
- ACID:                w2 dry — instruction 0 / record 0 — unchanged
- **Walk 2 total: 0 findings — instruction 0 / record 0, ALL FIVE LENSES DRY.** Instruction series 1 → 0.

**Conformance (§5):** first run at walk 0 (shape-stability) and re-run after walk 1 and at the freeze: `plan_lint` exit 0 / 0 FAIL at the faithful mirror — expected WARN set (o2)×10 (worktree-relative deposits) and (o1)×1 (the shop literal the Why names, absent here by definition); `cycle_check` BAR_MET; `fold_check` baseline saved; `propagation_check` exit 0.

**Closing:** ✅ **BAR MET — walk 2 dry (all five lenses) after walk 1's three folds; T1, no panel owed, none convened.** Substrate present (the register committed at each phase; `fold_check` baseline). The closing-record re-read (§2.7) ran against this block, the register and the emitted manifest at the freeze.

**Fold-and-deposit exactly once.**

## Cycle Manifest
tier: T1
target: hooks/eluvian/wrap_arm_hook.py, hooks/eluvian/wrap_stop_hook.py, hooks/eluvian/wrap_check.py, hooks/eluvian/eluvian_align_hook.py, hooks/commands/wrap.md, tests/test_hook_default_root.py
class: shop-infra
reads: /Users/marklehn/Developer/bellows/hooks/README.md, /Users/marklehn/Developer/bellows/plan_claim.py, /Users/marklehn/Developer/bellows/bellows_root.py, /Users/marklehn/Developer/bellows/tests/test_plan_claim.py, /Users/marklehn/.claude/settings.json
writes: hooks/eluvian/wrap_arm_hook.py, hooks/eluvian/wrap_stop_hook.py, hooks/eluvian/wrap_check.py, hooks/eluvian/eluvian_align_hook.py, hooks/commands/wrap.md, tests/test_hook_default_root.py, knowledge/development/dev-log-hooks-de-hardcode-2026-09-02.md, knowledge/qa/evidence/hooks-de-hardcode-2026-09-02/qa-receipt.md, knowledge/qa/evidence/hooks-de-hardcode-2026-09-02/probes-raw.txt, knowledge/qa/evidence/hooks-de-hardcode-2026-09-02/full-suite-hooks-de-hardcode.txt
open_forks: none
walks: 0
yields: 0
validation: cycle_check=PENDING, plan_lint=PENDING, fold_check=PENDING
coherence: 0/0 walks have register rows
