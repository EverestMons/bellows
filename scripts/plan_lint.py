#!/usr/bin/env python3
"""Pre-deposit plan lint. Validates plan structure before execution.

Usage: python3 scripts/plan_lint.py <plan-path>

Checks:
  (a) Header parses with valid dispatch_mode and pause_for_verdict tokens
  (b) Every step mentioning deposits has a parseable Deposits block
  (c) QA plans contain the Rule 20 banner pair

Exit 0 if all checks pass, exit 1 otherwise.
"""

import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

BELLOWS_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(BELLOWS_ROOT))

import gates
import cycle_check

RECOGNIZED_DISPATCH_MODES = {"bellows", "manual_bootstrap"}
# Mirrored from bellows.py header_says_pause — do not invent
RECOGNIZED_PAUSE_TOKENS = {"always", "after_step_1", "after_qa_step", "qa_and_terminal", "on_failure"}


def _parse_qa_steps(qa_steps_raw):
    """Delegates to `gates.parse_qa_steps` — THE single reader of this field.

    ⛔ This used to be a SECOND parser of the `qa_steps` header, and the two
    disagreed: this one stripped brackets, gates' did not (threads 116/121/122,
    FO-2). Keeping two readers in sync by editing both is what produced the
    divergence; delegating is what makes it unrepresentable.

    Preserves this function's historical contract for its existing callers:
    always a set, with absent/malformed collapsing to set(). Callers that need
    to distinguish "absent" from "declared none" must call gates.parse_qa_steps
    directly, which returns None for absent.
    """
    try:
        parsed = gates.parse_qa_steps(qa_steps_raw)
    except (ValueError, TypeError):
        return set()
    return set() if parsed is None else parsed


_SHA_PAT = r'\bsha(?:sum|256(?:sum)?)\b'


def _extract_hex_tokens(text):
    """Extract maximal hex runs >=12 chars. Returns [(line_num, token, kind)]."""
    hex_re = re.compile(r'[0-9a-fA-F]+')
    results = []
    for line_num, line in enumerate(text.splitlines(), 1):
        for m in hex_re.finditer(line):
            tok = m.group(0)
            n = len(tok)
            if n < 12:
                continue
            if n == 64:
                results.append((line_num, tok, 'sha256'))
            elif n == 40:
                results.append((line_num, tok, 'git'))
            else:
                results.append((line_num, tok, 'prefix'))
    return results


def _extract_pin_path(context_lines):
    """Extract file path from context lines containing a shasum/sha256 invocation."""
    for line in context_lines:
        if not re.search(_SHA_PAT, line, re.IGNORECASE):
            continue
        for m in re.finditer(r'`([^`\n]+)`', line):
            cand = m.group(1).strip()
            cmd_m = re.match(
                r'sha(?:sum|256(?:sum)?)\s+(?:-a\s+\d+\s+)?([^-\s]\S*)',
                cand, re.IGNORECASE,
            )
            if cmd_m:
                return cmd_m.group(1).strip().strip('`')
            if re.match(r'sha', cand, re.IGNORECASE) or cand.startswith('-'):
                continue
            if '/' in cand or re.search(r'\.\w+$', cand):
                return cand
        abs_m = re.search(r'(/[A-Za-z0-9_./-]+)', line)
        if abs_m:
            return abs_m.group(1).rstrip(')')
    return None


def _check_pins(plan_text, project_repo, root_repo):
    """Check pin tokens against file hashes (M2) and git repos (M1).
    Returns (telemetry, warns).
    """
    text_lines = plan_text.splitlines()
    tokens = _extract_hex_tokens(plan_text)
    telemetry = []
    warns = []

    for line_num, token, kind in tokens:
        tp = token[:12]

        if kind == 'sha256':
            # The pin's OWN line first, then its neighbours (thread 129).
            # line_num is 1-based, so text_lines[line_num - 1] IS the pin's line;
            # the old order [prev, own, next] let a NEIGHBOURING pin row's path
            # shadow the pin's own and produced a false MISMATCH naming the wrong
            # file. A row that names its own file must resolve to that file.
            ctx_idx = [i for i in [line_num - 1, line_num - 2, line_num]
                       if 0 <= i < len(text_lines)]
            ctx = [text_lines[i] for i in ctx_idx]
            if not any(re.search(_SHA_PAT, ln, re.IGNORECASE) for ln in ctx):
                telemetry.append(('sha256', line_num, tp, 'ambiguous'))
                continue
            file_path = _extract_pin_path(ctx)
            if not file_path:
                telemetry.append(('sha256', line_num, tp, 'ambiguous'))
                continue
            if os.path.isabs(file_path):
                resolved = file_path
            elif project_repo:
                resolved = os.path.join(str(project_repo), file_path)
            else:
                telemetry.append(('sha256', line_num, tp, 'ambiguous'))
                continue
            if not os.path.isfile(resolved):
                warns.append(
                    f"(q) WARN: line {line_num} sha256 pin {tp}… file missing: {file_path}")
                telemetry.append(('sha256', line_num, tp, 'missing-file'))
                continue
            try:
                actual = hashlib.sha256(Path(resolved).read_bytes()).hexdigest()
                if actual.lower() == token.lower():
                    telemetry.append(('sha256', line_num, tp, 'ok'))
                else:
                    warns.append(
                        f"(q) WARN: line {line_num} sha256 pin {tp}… MISMATCH on {file_path}")
                    telemetry.append(('sha256', line_num, tp, 'mismatch'))
            except Exception:
                warns.append(
                    f"(q) WARN: line {line_num} sha256 pin {tp}… file not readable: {file_path}")
                telemetry.append(('sha256', line_num, tp, 'missing-file'))

        elif kind == 'git':
            repos = []
            if project_repo and os.path.exists(
                    os.path.join(str(project_repo), '.git')):
                repos.append(('project', str(project_repo)))
            if root_repo and os.path.exists(
                    os.path.join(str(root_repo), '.git')):
                repos.append(('root', str(root_repo)))
            line_text = text_lines[line_num - 1] if line_num <= len(text_lines) else ''
            for cm in re.finditer(r'git\s+-C\s+(/\S+)', line_text):
                extra = cm.group(1)
                if os.path.exists(os.path.join(extra, '.git')):
                    repos.append(('named', extra))
            if not repos:
                telemetry.append(('git', line_num, tp, 'repo-unavailable'))
                continue
            resolved_in = None
            for label, repo in repos:
                try:
                    r = subprocess.run(
                        ['git', '-C', repo, 'cat-file', '-e', token],
                        capture_output=True, timeout=5,
                    )
                    if r.returncode == 0:
                        resolved_in = label
                        break
                except Exception:
                    continue
            if resolved_in == 'project':
                telemetry.append(('git', line_num, tp, 'ok'))
            elif resolved_in is not None:
                telemetry.append(('git', line_num, tp, 'cross-repo'))
            else:
                warns.append(
                    f"(q) WARN: line {line_num} git pin {tp}… unresolved")
                telemetry.append(('git', line_num, tp, 'unresolved'))

        else:
            telemetry.append(('prefix', line_num, tp, 'ambiguous'))

    return telemetry, warns


_BARE_CONSTANT_RE = re.compile(r"(==|>=|<=)\s*\*{0,2}\d+\*{0,2}")
_CLAUSE_MARKERS = ("supersede", "re-derive", "rederive", "yours ", "recorded",
                   "record", "measured", "measure and")


_CHANGELOG_SLUG_RE = re.compile(r"slug\s+([a-z0-9][\w-]{6,})")


def _check_discharges(plan_text):
    """(g) — the declared plan->thread link (thread 80).

    `**Discharges:** thread 75[, thread 73]`, presence-OPTIONAL and warn-first,
    on the (f-stanza) precedent. The field declares an INTENT TO DISCHARGE, never
    a closure: at the plan's completion transition bellows enqueues a tuyere
    review intent per id, and the CEO confirms or declines at the keyboard.
    Nothing auto-closes — a plan often discharges only PART of a thread, and a
    mis-declared field must not close the wrong one silently.

    ⛔ Parsing lives in gates.parse_discharges, NOT here. Two copies of a parser
    diverge the moment one moves (measured 2026-09-06: a register resolver gained
    a step in one consumer and the other kept reporting the file unresolvable).
    """
    ids, residue = gates.parse_discharges(plan_text)
    if ids is None:
        return                      # field absent — optional by design
    if residue:
        print(f"(g) WARN: Discharges field has text this parser does not understand: "
              f"{residue[:60]!r} — the form is `thread <id>[, thread <id>]`, integer "
              f"ids only, exact match (a loose match links the WRONG thread)")
    if not ids:
        print("(g) WARN: Discharges field declares no thread id — omit the field "
              "rather than leaving it empty")
        return
    print(f"(g) INFO: declares discharge of thread(s) {', '.join(str(i) for i in ids)} "
          f"— a review intent is enqueued per id at plan close; nothing auto-closes")


def _check_shipped_doctrine_tranche(plan_path):
    """(x) WARN when this plan's OWN slug already names a shipped doctrine changelog row.

    Thread 157: nothing in the admission path asks whether a plan's work has ALREADY
    BEEN DONE. `cycle_check` BAR_MET attests that the plan's own cycle converged; it
    says nothing about the world the plan would act on. Measured 2026-09-06: of 7
    gate-clean drafts, FOUR had shipped — two of them doctrine tranches that would have
    re-applied proposals already codified into PT v4.98 and DC v2.24.

    ⛔ NARROW ON PURPOSE. Thread 157 lists three detection signals; measured against the
    four known-shipped drafts, only this one discriminates:
        (a) all declared deposits exist on disk   21 hits, 4 true, 17 FALSE (81%)
        (b) THIS CHECK                             1 hit,  1 true,  0 false
        (c) a Done/ plan with the same stem        0 hits — its own example pairs
            register-validate-first with Done/executable-100030, same SUBJECT and a
            different name, which no mechanical stem match finds
        (d) (a) AND the slug in a commit subject  20 hits, 4 true, 16 false — degenerate,
            because every walked draft appears in its own `draft(<slug>):` commits
    (a) and (d) must NOT ship as rules at those rates. This catches 1 of the 4, and it
    is the highest-harm one; the general remedy is the retirement ritual (2bb7b20's
    precedent), not a gate.

    ⚠️ Keyed on the FILENAME, never on prose. 27 of 35 drafts MENTION some changelog
    slug — citing a shipped tranche is normal — so a text match is degenerate. An
    earlier cut of this measurement keyed on the first `slug X` in the body and got the
    right answer by luck, because that file's first mention happened to be its own.
    """
    try:
        stem = re.sub(r"^(executable|diagnostic|qa)-", "", Path(plan_path).stem)
        if not stem:
            return
        from bellows_root import resolve_governance_root
        gov = resolve_governance_root()
        text = ""
        for name in ("DRAFTING_CYCLE.md", "PLANNER_TEMPLATE.md"):
            f = gov / name
            if f.is_file():
                text += f.read_text(encoding="utf-8", errors="replace")
        for slug in set(_CHANGELOG_SLUG_RE.findall(text)):
            if slug == stem or slug.startswith(stem + "-20"):
                print(f"(x) WARN: this plan's own slug names a SHIPPED doctrine "
                      f"changelog row (`slug {slug}`) — its subject may already be "
                      f"codified; verify before depositing (thread 157)")
                return
    except Exception:
        return  # advisory only — never let this decide a verdict


def _check_bare_constants(plan_text):
    """(r) WARN-FIRST: a probe constant (== / >= / <= N) inside a STEP block
    with no supersede-class clause on the line or within 2 lines either side.
    The global Numbers-discipline banner deliberately does NOT satisfy this
    check: the gap being closed is the ad-hoc probe line outside the banner's
    reach (the 554 case). Advisory only — never a FAIL; the verdict on
    whether a constant is genuinely load-bearing stays with the reader.
    Fenced code is never scanned — the 563-measured false-positive class
    (structural constants in code blocks)."""
    lines = plan_text.splitlines()
    in_step = False
    in_fence = False
    warns = []
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        while stripped.startswith(">"):
            stripped = stripped[1:].lstrip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if line.startswith("## STEP "):
            in_step = True
        elif line.startswith("## ") and not line.startswith("## STEP "):
            in_step = False
        if not in_step or in_fence or not _BARE_CONSTANT_RE.search(line):
            continue
        window = " ".join(lines[max(0, i - 2):i + 3]).lower()
        if not any(m in window for m in _CLAUSE_MARKERS):
            warns.append(i + 1)
    for n in warns:
        print(f"(r) WARN: line {n} probe constant without a supersede-class "
              f"clause within 2 lines — a wrong authored number here HARD-FAILS "
              f"a correct state (the 554 class); add measure-record-supersede "
              f"language or verify the constant is structural")
    return len(warns)


def lint(plan_path):
    plan_text = Path(plan_path).read_text(encoding="utf-8")
    results = []
    all_passed = True

    # (a) Header parses
    header = gates._parse_plan_header(plan_text)
    if not header:
        results.append(("FAIL", "(a) header", "plan header parse returned empty"))
        all_passed = False
    else:
        results.append(("PASS", "(a) header", "parsed"))

        dm = header.get("dispatch_mode", "")
        if dm and dm not in RECOGNIZED_DISPATCH_MODES:
            results.append(("FAIL", "(a) dispatch_mode", f"unrecognized: {dm!r} (expected: {', '.join(sorted(RECOGNIZED_DISPATCH_MODES))})"))
            all_passed = False
        elif dm:
            results.append(("PASS", "(a) dispatch_mode", dm))

        pv = header.get("pause_for_verdict", "")
        if pv and pv not in RECOGNIZED_PAUSE_TOKENS:
            results.append(("FAIL", "(a) pause_for_verdict", f"unrecognized: {pv!r} (expected: {', '.join(sorted(RECOGNIZED_PAUSE_TOKENS))})"))
            all_passed = False
        elif pv:
            results.append(("PASS", "(a) pause_for_verdict", pv))

        kf_raw = header.get("known_failures")
        if kf_raw is not None:
            try:
                int(kf_raw)
                results.append(("PASS", "(a) known_failures", str(kf_raw)))
            except (ValueError, TypeError):
                results.append(("FAIL", "(a) known_failures", f"non-integer value: {kf_raw!r} — must be an int (daemon fail-closes on malformed values)"))
                all_passed = False

    # Extract step numbers from plan
    clean_text = gates.strip_fenced_code_blocks(plan_text)
    step_headers = re.findall(r'^(## STEP (\d+)\b[^\n]*)', clean_text, re.MULTILINE)

    # (e) Step heading case guard: catch vacuous-pass from title-case headings
    ci_step_headers = re.findall(r'^(##\s+step\s+(\d+)\b[^\n]*)', clean_text, re.IGNORECASE | re.MULTILINE)
    if not step_headers and header.get("qa_steps"):
        msg = "header declares qa_steps but no uppercase '## STEP N' heading found — step checks (b)/(d) were skipped (vacuous pass)"
        if ci_step_headers:
            msg += "; found lowercase '## Step N' headings, use uppercase '## STEP N'"
        results.append(("FAIL", "(e) step heading format", msg))
        all_passed = False
    elif not step_headers and ci_step_headers:
        print("WARN: found '## Step N' headings but no uppercase '## STEP N' — consider using uppercase for lint coverage")

    # (b) Deposits blocks: steps mentioning "deposit" must yield parseable paths
    for header_line, step_num_str in step_headers:
        step_num = int(step_num_str)
        step_text = gates._extract_step_text(plan_text, step_num)
        if not step_text:
            continue
        if "deposit" not in step_text.lower():
            continue
        deposits = gates._extract_plan_required_deposits(step_text)
        if deposits:
            results.append(("PASS", f"(b) step {step_num} deposits", f"{len(deposits)} path(s)"))
        else:
            results.append(("FAIL", f"(b) step {step_num} deposits", "step mentions deposit but **Deposits:** block yields no paths"))
            all_passed = False

    # (c) QA banner pair: QA plans must contain both template strings
    _QA_STEPS_PLACEHOLDER = "[comma-separated step numbers]"
    has_qa = False
    qa_steps_raw = header.get("qa_steps", "")
    if qa_steps_raw:
        if qa_steps_raw.strip() == _QA_STEPS_PLACEHOLDER:
            print("(c) WARN: qa_steps: unfilled template placeholder — update with step numbers")
        elif qa_steps_raw.strip().lower() != "none":
            has_qa = True
    if not has_qa:
        for header_line, _ in step_headers:
            if "qa" in header_line.lower():
                has_qa = True
                break

    # (c) COMPENSATING CONTROL for FO-2's retirement (threads 119/121).
    # gates._gate_is_qa_step no longer guesses from the step TITLE when the
    # header is silent, so an undeclared QA step would otherwise reach dispatch
    # ungated and unwarned — the existing cross-check below sits inside
    # `if qa_steps_raw:` and never runs for this case. Catch it at AUTHORING,
    # where the header is still editable.
    if not str(qa_steps_raw).strip():
        _undeclared_qa = [int(sn) for hl, sn in step_headers if "qa" in hl.lower()]
        for _n in sorted(_undeclared_qa):
            print(f"(c) WARN: step {_n} is QA-labeled but the plan declares no"
                  f" qa_steps — it will NOT be Rule 20/22 gated at dispatch"
                  f" (declare `qa_steps: {_n}`, or `none` if it is not a QA step)")
    elif _parse_qa_steps(qa_steps_raw) == set() and \
            str(qa_steps_raw).strip().lower() != "none" and \
            str(qa_steps_raw).strip() != _QA_STEPS_PLACEHOLDER:
        print(f"(c) WARN: qa_steps={qa_steps_raw!r} is present but unparseable —"
              f" every step will be treated as NOT a QA step at dispatch")

    if has_qa:
        banner = "Rule 20 — QA Self-Check Results"
        passed_line = "PASSED — SELF-CHECK PASSED"
        has_banner = banner in plan_text
        has_passed = passed_line in plan_text
        if has_banner and has_passed:
            results.append(("PASS", "(c) QA banner pair", "both strings present"))
        else:
            missing = []
            if not has_banner:
                missing.append("banner")
            if not has_passed:
                missing.append("PASSED line")
            results.append(("FAIL", "(c) QA banner pair", f"missing: {', '.join(missing)}"))
            all_passed = False

    # (d) Scope block: if present, must parse to at least one file or prefix
    for header_line, step_num_str in step_headers:
        step_num = int(step_num_str)
        step_text = gates._extract_step_text(plan_text, step_num)
        if not step_text:
            continue
        scope_block_present = re.search(r'[> ]*\*\*Scope:\*\*', step_text)
        if not scope_block_present:
            continue
        scope_files, scope_prefixes = gates._extract_plan_scope(step_text)
        if scope_files or scope_prefixes:
            results.append(("PASS", f"(d) step {step_num} scope", f"{len(scope_files)} file(s), {len(scope_prefixes)} prefix(es)"))
        else:
            results.append(("FAIL", f"(d) step {step_num} scope", "**Scope:** block present but parses to zero entries"))
            all_passed = False

    # WARN: step mentions "test" but declares no test scope
    for header_line, step_num_str in step_headers:
        step_num = int(step_num_str)
        step_text = gates._extract_step_text(plan_text, step_num)
        if not step_text:
            continue
        if not re.search(r'\btest\b', step_text, re.IGNORECASE):
            continue
        scope_files, scope_prefixes = gates._extract_plan_scope(step_text)
        has_test_scope = any("test_" in f and f.endswith(".py") for f in scope_files)
        has_test_prefix = any(p.rstrip("/").split("/")[-1] == "tests" or p == "tests/" for p in scope_prefixes)
        has_test_in_text = bool(re.search(r'test_\w+\.py', step_text)) or "tests/" in step_text
        if not has_test_scope and not has_test_prefix and not has_test_in_text:
            print(f"WARN: step {step_num} mentions tests but declares no test scope")

    # WARN: qa_steps ↔ step-label cross-check
    qa_steps_raw = header.get("qa_steps", "") if header else ""
    if qa_steps_raw:
        qa_steps_set = _parse_qa_steps(qa_steps_raw)
        qa_labeled_steps = {int(sn) for hl, sn in step_headers if "qa" in hl.lower()}
        for n in sorted(qa_labeled_steps - qa_steps_set):
            print(f"WARN: step {n} is QA-labeled but absent from qa_steps={qa_steps_raw!r} — it will not be Rule 20/22 gated")
        for n in sorted(qa_steps_set - qa_labeled_steps):
            print(f"WARN: qa_steps lists step {n} but step {n} is not QA-labeled — it will be gated as QA (plan-133 trap)")

    # (u) QA Deposits order (WARN-only, thread 77): rule_20_self_check reads the first .md as the report
    qa_steps_set_u = _parse_qa_steps(qa_steps_raw) if qa_steps_raw else set()
    for hl, sn_str in step_headers:
        sn = int(sn_str)
        step_text_u = gates._extract_step_text(plan_text, sn)
        if not step_text_u:
            continue
        is_qa_step = sn in qa_steps_set_u or "Rule 20" in step_text_u
        if not is_qa_step:
            continue
        deps_u = gates._extract_plan_required_deposits(step_text_u)
        md_entries = [d for d in deps_u if d.rstrip('/').endswith('.md')]
        if md_entries:
            first_basename = Path(md_entries[0]).name
            if 'receipt' not in first_basename:
                print(f"(u) WARN: step {sn} Deposits: first .md is {first_basename!r}"
                      f" — rule_20_self_check reads the first .md as the QA report (thread 77)")
        if not any(d.endswith('.txt') for d in deps_u):
            print(f"(u) WARN: step {sn} Deposits: no .txt evidence entry (thread 77)")

    # (v) No-pytest QA step without pre-declaration clause (WARN-only, advisory, thread 70).
    # Must call gates._gate_is_qa_step — NOT (u)'s local heuristic. This check keys on
    # the author's test_scope declaration; whether a step will produce a pytest summary
    # is not inferrable from plan text alone, so it needs the predicate the DISPATCH
    # gate actually uses.
    #
    # ⚠️ This comment previously justified itself with "P11 measured 74 divergences
    # across 861 steps (66 false positives, 8 blind spots)". Those figures were struck
    # 2026-09-04 (thread 102, closed): the denominator does not reproduce — 102 reports
    # 861 steps in Done/ at 2026-09-03 10:55, and the tree at that moment (df83640)
    # yields 870, which is above every neighbouring measurement, so it is not drift.
    # The divergence between (u) and this gate is REAL but the counts were never
    # re-derived. Do not re-cite them.
    #
    # ⛔ HISTORICAL NOTE, now discharged. Diagnostic 100036 Q6 measured that
    # _parse_qa_steps was the CORRECT reference — it handled every corpus spelling —
    # while gates._gate_is_qa_step failed on the `[2]` form and masked it with keyword
    # detection, so converging (u) onto that gate would have converged it onto the
    # defective side. That divergence is GONE as of 2026-09-06 (FO-2): both now read
    # gates.parse_qa_steps, and the keyword fallback is retired. The two sides can no
    # longer disagree, so the reason not to converge (u) no longer applies — but
    # converging it is still a ruling, not a tidy-up.
    _v_test_scope = header.get("test_scope", "") if header else ""
    if _v_test_scope.strip().lower().startswith("none"):
        for hl, sn_str in step_headers:
            sn = int(sn_str)
            if not gates._gate_is_qa_step(plan_text, sn, plan_header=header):
                continue
            _v_step_text = gates._extract_step_text(plan_text, sn)
            if not _v_step_text:
                continue
            _v_lower = _v_step_text.lower()
            if "pre-declar" in _v_lower or "gate note" in _v_lower or "qa_test_result" in _v_lower:
                continue
            print(
                f"(v) WARN: step {sn} is a QA step whose test_scope starts 'none',"
                f" but its text carries no pre-declaration clause."
                f" A raw-evidence .txt deposit alone does not clear _gate_qa_test_result:"
                f" its second branch requires a parseable pytest summary and will FAIL"
                f" without one. Remedy: add a bolded gate-note in this step's text"
                f" pre-declaring the benign class and that the Planner overrides at"
                f" the verdict. (thread 70)"
            )

    dc_block = None

    # (f) Drafting Cycle self-check (DRAFTING_CYCLE.md §4, warn-first)
    cycle_tier_raw = header.get("cycle_tier", "") if header else ""
    ct_match = re.match(r'^T([012])\b', cycle_tier_raw)
    if not cycle_tier_raw:
        print("WARN: no cycle_tier declared (DRAFTING_CYCLE.md §1/§3)")
    elif not ct_match:
        print(f"WARN: cycle_tier {cycle_tier_raw!r} not recognized (expected T0, T1, or T2)")
    else:
        tier_num = int(ct_match.group(1))
        if tier_num >= 1:
            dc_match = re.search(r'^## Drafting Cycle\s*$', plan_text, re.MULTILINE)
            if not dc_match:
                print(f"WARN: {cycle_tier_raw} plan has no '## Drafting Cycle' block (DRAFTING_CYCLE.md §3)")
            else:
                dc_start = dc_match.end()
                next_h2 = re.search(r'^## ', plan_text[dc_start:], re.MULTILINE)
                dc_block = plan_text[dc_start:dc_start + next_h2.start()] if next_h2 else plan_text[dc_start:]

                required_lenses = [
                    ("Weak spots", r'weak[\s-]*spots'),  # 63: hyphenated spelling
                    ("Destruction", r'destruction'),
                    ("Vulnerabilities", r'vulnerabilit'),
                    ("Integration", r'integration'),
                    ("ACID", r'acid'),
                ]
                missing = [name for name, pat in required_lenses if not re.search(pat, dc_block, re.IGNORECASE)]
                if missing:
                    print(f"WARN: Drafting Cycle block missing lens(es): {', '.join(missing)} (DRAFTING_CYCLE.md §3)")

                if tier_num == 2:
                    cold_bold_re = re.compile(r'^\*\*cold[\s-]+panel', re.IGNORECASE)
                    cold_dash_re = re.compile(r'^-\s*cold[\s-]', re.IGNORECASE)
                    has_cold_content = False
                    for line in dc_block.splitlines():
                        stripped = line.strip()
                        if cold_bold_re.match(stripped):
                            remainder = cold_bold_re.sub('', stripped)
                            remainder = re.sub(r'\([^)]*\)', '', remainder)
                            remainder = remainder.replace(':', '').replace('*', '').strip()
                            if remainder:
                                has_cold_content = True
                                break
                        elif cold_dash_re.match(stripped):
                            remainder = re.sub(r'^-\s*cold[\s-]+\S+', '', stripped, flags=re.IGNORECASE)
                            remainder = re.sub(r'\([^)]*\)', '', remainder)
                            remainder = remainder.replace(':', '').strip()
                            if remainder:
                                has_cold_content = True
                                break
                    if not has_cold_content:
                        print("WARN: T2 plan missing cold-panel line in Drafting Cycle block (DRAFTING_CYCLE.md §3)")

                lens_line_re = re.compile(
                    r'^-\s*(?:cold[\s-]+)?(?:weak[\s-]*spots|destruction|vulnerabilit\w*|integration|acid)\b',
                    re.IGNORECASE,
                )
                closing_pos = re.search(r'^\*\*Closing:\*\*', dc_block, re.MULTILINE)
                search_region = dc_block[:closing_pos.start()] if closing_pos else dc_block
                lens_lines = []
                for line in search_region.splitlines():
                    if lens_line_re.match(line):
                        lens_lines.append(line)

                _class_split_re = re.compile(r'instruction\s+(\d+)\s*/\s*record\s+(\d+)')
                has_class_split = any(_class_split_re.search(l) for l in lens_lines)

                if has_class_split:
                    _walk_token_re = re.compile(r'\bw(\d+)\b')
                    max_walk = 0
                    for l in lens_lines:
                        clean = re.sub(r'\([^)]*\)', '', l)
                        for m in _walk_token_re.finditer(clean):
                            wn = int(m.group(1))
                            if wn > max_walk:
                                max_walk = wn
                    _walk_header_re = re.compile(r'\*\*Walk\s+(\d+)\b')
                    for m in _walk_header_re.finditer(dc_block):
                        wn = int(m.group(1))
                        if wn > max_walk:
                            max_walk = wn

                    instruction_sum = 0
                    if max_walk > 0:
                        _status_re = re.compile(
                            r'\*\*Walk\s+(\d+)\s+STATUS:\*\*.*?instruction\s+(\d+)', re.I)
                        status_hit = None
                        for sm in _status_re.finditer(dc_block):
                            if int(sm.group(1)) == max_walk:
                                status_hit = sm
                                break
                        if status_hit:
                            instruction_sum = int(status_hit.group(2))
                        else:
                            for l in lens_lines:
                                clean = re.sub(r'\([^)]*\)', '', l)
                                segments = re.split(r';\s*', clean)
                                expanded = []
                                for seg in segments:
                                    expanded.extend(re.split(r'\.\s+(?=w\d)', seg))
                                for seg in expanded:
                                    m = _walk_token_re.search(seg)
                                    if m and int(m.group(1)) == max_walk:
                                        cs = _class_split_re.search(seg)
                                        if cs:
                                            instruction_sum += int(cs.group(1))
                                        elif 'fold' in seg.lower():
                                            instruction_sum += 1
                                        break
                    if instruction_sum > 0:
                        print("WARN: Drafting Cycle closing indicates fold as last event, not a dry lens pass (DRAFTING_CYCLE.md §2)")
                elif lens_lines:
                    ll_lower = lens_lines[-1].lower()
                    has_fold = 'fold' in ll_lower
                    cleaned = re.sub(r'\b(?:not|no|never)\s+(?:\w+\s+)?dry\b', '', ll_lower)
                    has_dry = bool(re.search(r'\bdry\b', cleaned))
                    if has_fold and not has_dry:
                        print("WARN: Drafting Cycle closing indicates fold as last event, not a dry lens pass (DRAFTING_CYCLE.md §2)")
                else:
                    closing_match = re.search(r'^\*\*Closing:\*\*\s*(.*)', dc_block, re.MULTILINE)
                    if closing_match:
                        closing_text = closing_match.group(1).lower()
                        if 'fold' in closing_text and 'dry' not in closing_text:
                            print("WARN: Drafting Cycle closing indicates fold as last event, not a dry lens pass (DRAFTING_CYCLE.md §2)")

                if not closing_pos:
                    print("WARN: Drafting Cycle block has no **Closing:** line (DRAFTING_CYCLE.md §3)")

                # (g) Ledger ordering (WARN-only): constraint entries **C<n>** — must be
                # strictly ascending. Zero entries is not a failure; skip silently.
                ledger_entry_re = re.compile(r'\*\*C(\d+)\*\*\s*—')
                c_nums = [int(m.group(1)) for m in ledger_entry_re.finditer(dc_block)]
                if len(c_nums) >= 2:
                    for j in range(1, len(c_nums)):
                        if c_nums[j] <= c_nums[j - 1]:
                            print(f"WARN: Drafting Cycle ledger out of order: C{c_nums[j - 1]} before C{c_nums[j]}")
                            break

                # (h) Stale closing disclaimer (WARN-only): contradiction check — if any
                # lens line records a walk result AND the Closing asserts no lens has read
                # the artifact, that pair is a defect. Neither condition alone fires.
                any_lens_ran = False
                for ln in dc_block.splitlines():
                    if lens_line_re.match(ln) and re.search(r'[wa]\d+', ln):
                        any_lens_ran = True
                        break
                closing_claims_unread = False
                if closing_pos:
                    cl_match = re.search(r'^\*\*Closing:\*\*\s*(.*)', dc_block, re.MULTILINE)
                    if cl_match and 'no lens has read' in cl_match.group(1).lower():
                        closing_claims_unread = True
                if any_lens_ran and closing_claims_unread:
                    print("WARN: Drafting Cycle Closing claims no lens has read the artifact, but lens results are recorded")

    # (f-stanza) Cycle Manifest stanza shape check (WARN-only, presence-optional)
    manifest_m = re.search(r'^## Cycle Manifest\s*$', plan_text, re.MULTILINE)
    if manifest_m:
        stanza_start = manifest_m.end()
        stanza_end_m = re.search(r'^(?:## |---)', plan_text[stanza_start:], re.MULTILINE)
        stanza_text = plan_text[stanza_start:stanza_start + stanza_end_m.start()] if stanza_end_m else plan_text[stanza_start:]

        # (f-stanza) ⛔ UNEMITTED vs INCOMPLETE. A heading whose stanza parses to ZERO
        # fields is not "ten missing fields" — it is a manifest no consumer can read:
        # cycle_check.parse_manifest_stanza returns {} and depositor._parse_plan falls
        # back to gates._extract_plan_required_deposits, narrowing the write set. That
        # is the 2026-09-03 failed-open deposit (LESSONS 413): four writes became two,
        # every one under knowledge/, so the infra rule never fired, the plan classed
        # app-feature and AUTO-CLEARED past the shop-infra human release act — while
        # this check emitted ten WARNs and exit 0.
        #
        # ⚠️ Conditioned on a CLOSURE CLAIM, and that condition is load-bearing: a plan
        # mid-cycle carries `*(emitted at BAR_MET)*` legitimately, and FAILing every walk
        # of every cycle is how a FAIL gets trained into background noise. Measured over
        # 617 plans (2026-09-05): 8 carry a heading that parses to zero fields; exactly
        # ONE claims closure, and it is halted-executable-100031.md — the plan the
        # incident came from. The other 7 keep their WARNs.
        #
        # The closure predicate and the DC block are cycle_check's own, not a local copy:
        # a second implementation of "does this claim closure" is a divergence waiting to
        # happen, and cycle_check is the enforcer that already blocks BAR_MET on this
        # (its _manifest_validation_keys arm B).
        stanza_fields = {}
        s_current_key = None
        s_current_val = None
        for s_line in stanza_text.splitlines():
            s_stripped = s_line.strip()
            if not s_stripped:
                continue
            if s_line.startswith("  ") and s_current_key:
                s_current_val = s_current_val.rstrip(",") + ", " + s_stripped.rstrip(",")
                stanza_fields[s_current_key] = s_current_val
                continue
            s_fm = re.match(r'^(\w[\w_]*):\s*(.*)', s_stripped)
            if s_fm:
                s_current_key = s_fm.group(1)
                s_current_val = s_fm.group(2).strip()
                stanza_fields[s_current_key] = s_current_val

        # (w) DC work declares its mutants (advisory, WARN-only).
        # A plan whose manifest writes: names a shop instrument is DC WORK: its DEV step
        # edits a checker, and its own QA then runs that edited checker to validate it.
        # The bootstrap remedy — revert the tool, confirm the new tests FAIL — is already
        # practised (six instrument fixes, 2026-09-04) but was never declared. Measured
        # 2026-09-05: of 11 Done plans writing a shop instrument, 6 declared `mutants:`
        # and 5 did not, including 100033 and 100037, which changed cycle_check and
        # plan_lint themselves.
        # ⛔ Advisory, NOT required: mutation_check is the least-trusted instrument in
        # the set (5% recording rate per 100032; threads 97/107/112 open against it), so
        # a hard requirement would make it load-bearing for the shop's most sensitive
        # work. Promote only after that debt is settled.
        _DC_INSTRUMENTS = (
            "cycle_check", "plan_lint", "fold_check",
            "propagation_check", "walk_register_lint", "mutation_check",
        )
        _w_writes = stanza_fields.get("writes", "")
        _w_hits = sorted({i for i in _DC_INSTRUMENTS if f"{i}.py" in _w_writes})
        if _w_hits:
            _w_mut = stanza_fields.get("mutants", "").strip()
            if not _w_mut or _w_mut.upper().startswith("NONE"):
                print(
                    f"(w) WARN: writes: names shop instrument(s) {', '.join(_w_hits)}"
                    f" but mutants: is {'absent' if not _w_mut else 'NONE'}"
                    f" — DC work should declare the mutants that prove the OLD tool"
                    f" fails the NEW tests (advisory)"
                )

        if not stanza_fields:
            _claims_closure = False
            try:
                _blocks = cycle_check.extract_dc_blocks(plan_text)
                if len(_blocks) == 1:
                    _claims_closure = cycle_check.parse_block(_blocks[0])["claims_closure"]
            except Exception:
                _claims_closure = False   # never let the probe decide the verdict
            if _claims_closure:
                # ⛔ results.append alone does NOT fail the lint — the exit code is
                # driven by all_passed, a separate flag. A FAIL that leaves it True
                # prints like a failure and exits 0, and depositor.py:508 only reads
                # FAIL: lines when returncode != 0, so it would be invisible there.
                all_passed = False
                results.append((
                    "FAIL", "(f) manifest",
                    "'## Cycle Manifest' heading present but the stanza parses to ZERO "
                    "fields, and the cycle CLAIMS CLOSURE — the manifest is unemitted. "
                    "cycle_check.parse_manifest_stanza returns {} and depositor._parse_plan "
                    "falls back to prose deposits, narrowing the write set and the class",
                ))

        _STANZA_REQUIRED = [
            "tier", "target", "class", "reads", "writes",
            "open_forks", "walks", "yields", "validation", "coherence",
        ]
        _STANZA_VALID_CLASSES = {"read-only", "governed-tooling", "register-writing", "shop-infra", "app-feature"}

        has_declare = False
        for sf in _STANZA_REQUIRED:
            sv = stanza_fields.get(sf, "")
            if not sv:
                print(f"(f) WARN: Cycle Manifest stanza missing or empty field: {sf}")
            elif sv == "<declare>":
                has_declare = True

        if has_declare:
            print("(f) WARN: Cycle Manifest stanza contains <declare> placeholder(s) — incomplete template")

        class_val = stanza_fields.get("class", "")
        if class_val and class_val != "<declare>" and class_val not in _STANZA_VALID_CLASSES:
            print(f"(f) WARN: Cycle Manifest class value {class_val!r} not in {_STANZA_VALID_CLASSES}")

        reads_val = stanza_fields.get("reads", "")
        if not reads_val:
            pass  # already warned above as missing
        elif reads_val == "<declare>":
            pass  # already warned as <declare>

        if class_val and class_val != "read-only" and class_val != "<declare>":
            writes_val = stanza_fields.get("writes", "")
            if not writes_val or writes_val == "<declare>":
                print("(f) WARN: Cycle Manifest non-read-only plan has empty or undeclared writes")

        validation_val = stanza_fields.get("validation", "")
        if validation_val and validation_val != "<declare>":
            if "cycle_check=" not in validation_val:
                print("(f) WARN: Cycle Manifest validation missing cycle_check= entry")
            if "plan_lint=" not in validation_val:
                print("(f) WARN: Cycle Manifest validation missing plan_lint= entry")

        # (s) Detector consequences: target_class=detector mechanizes state_space
        # and mutants as required follow-through. The declaration itself is authored
        # — only its consequences are mechanized.
        tc_val = stanza_fields.get("target_class", "").strip()
        if tc_val == "detector":
            ss_val = stanza_fields.get("state_space", "").strip()
            if not ss_val:
                print("(s) WARN: target_class=detector but no state_space field"
                      " — a detector’s tests must enumerate its state space"
                      " from SYSTEM artifacts (SELECT DISTINCT, real filenames,"
                      " the actual writer), not the author’s model;"
                      " see exec-573 TestPauseStateSpace")
            mut_val = stanza_fields.get("mutants", "").strip()
            if not mut_val:
                print("(s) WARN: target_class=detector but mutants names no"
                      " manifest that exists or is promised in Deposits"
                      " — ‘would the suite catch this?’ has no"
                      " mechanical answer; see tools/mutation_check.py (exec-575)")
            else:
                try:
                    mut_on_disk = Path(mut_val).exists()
                except OSError:
                    mut_on_disk = False
                mut_in_deposits = False
                if not mut_on_disk:
                    for dep_m in re.finditer(r'\*\*Deposits:\*\*', plan_text):
                        dep_start = dep_m.end()
                        dep_block = plan_text[dep_start:dep_start + 500]
                        if mut_val in dep_block:
                            mut_in_deposits = True
                            break
                if not mut_on_disk and not mut_in_deposits:
                    print("(s) WARN: target_class=detector but mutants names no"
                          " manifest that exists or is promised in Deposits"
                          " — ‘would the suite catch this?’ has no"
                          " mechanical answer; see tools/mutation_check.py (exec-575)")

        # (t) Detector name nudge — advisory heuristic.
        # A name heuristic is invisible when incomplete and must NEVER become a
        # FAIL basis — it exists to make the omission visible, not to decide it.
        if not tc_val:
            tgt_val = stanza_fields.get("target", "").strip()
            if tgt_val.endswith(".py"):
                tgt_base = Path(tgt_val).name
                if re.search(r'(check|guard|watch|filter|dedup|stale|detect|valid|lint|verif)', tgt_base, re.IGNORECASE):
                    print("(t) WARN: target basename looks like a detector but"
                          " target_class is not declared — declare"
                          " ‘target_class: detector’ (and then state_space"
                          " + mutants), or leave it undeclared deliberately;"
                          " this heuristic is advisory and cannot decide the question")

    # (i) qa_and_terminal ↔ qa_steps coupling: under this mode a mis-declared QA step
    # advances mechanically — the lint is the authoring-time guard.
    if header and header.get("pause_for_verdict") == "qa_and_terminal":
        qs_raw = header.get("qa_steps", "")
        qs_set = _parse_qa_steps(qs_raw) if qs_raw else set()
        if not qs_set:
            print("WARN: pause_for_verdict=qa_and_terminal but qa_steps is missing or unparseable — QA steps may advance mechanically")

    if header and header.get("pause_for_verdict") == "on_failure":
        qs_raw = header.get("qa_steps", "")
        qs_set = _parse_qa_steps(qs_raw) if qs_raw else set()
        if not qs_set:
            results.append(("FAIL", "(i) on_failure qa_steps", "pause_for_verdict=on_failure requires a parseable qa_steps field"))
            all_passed = False

    # --- Checks (j), (k), (l) — whole-plan-text scope, NOT inside dc_block ---
    # Unlike (g)/(h) which operate inside the Drafting Cycle dc_block scope,
    # these checks read the whole plan text: (j) and (k) key on literals that
    # can appear anywhere, and (l) additionally reads the header's cycle_tier.

    # (j) Inherited-premise marker (WARN-only): flags
    # [INHERITED FROM <numeric-id> — NOT RE-EXECUTED] markers outside fenced
    # code blocks. Numeric id required; inline code spans NOT excluded; fenced
    # blocks excluded via gates.strip_fenced_code_blocks (reuse, not a second
    # parser). Cannot see: whether the re-run was actually priced — the check
    # flags the SITE; the panel judges the quality.
    # Known per-LINE false positive: a retraction narrating a marker verbatim
    # with a real id fires at line level; per FILE the result stays true positive.
    inherited_re = re.compile(r'\[INHERITED FROM (\d+(?:/\d+)*)\s*—\s*NOT RE-EXECUTED\]')
    j_stripped = list(inherited_re.finditer(clean_text))
    if j_stripped:
        orig_lines = plan_text.splitlines()
        all_orig_j = []
        for i, line in enumerate(orig_lines):
            for m in inherited_re.finditer(line):
                all_orig_j.append((i + 1, m.group(1)))
        oi = 0
        for sm in j_stripped:
            sid = sm.group(1)
            for idx in range(oi, len(all_orig_j)):
                if all_orig_j[idx][1] == sid:
                    print(f"(j) WARN: line {all_orig_j[idx][0]} carries an inherited-premise marker from plan {sid}")
                    oi = idx + 1
                    break

    # (k) Clone-claim check (WARN-only): a plan declaring clone framing on its
    # Cycle Log tier line but not naming its newest same-class comparison.
    # Declaration-keyed on the FIRST line-start **Tier:** in stripped text (a
    # fenced tier-line quote must not match). Cannot see: whether the diff was
    # actually performed, nor which plan IS the newest same-class.
    # False-NEGATIVE directions: (1) 'newest same-class' in discussion text
    # suppresses; (2) undeclared clones skip; (3) provenance declared only off
    # the tier line (e.g. a dedicated "Clone lineage" section) is invisible.
    tier_line_m = re.search(r'^\*\*Tier:\*\*.*$', clean_text, re.MULTILINE)
    clone_re = re.compile(r'proven[\s-]+clone|clone\s+of|structure-clone', re.IGNORECASE)
    has_clone_framing = False
    tier_line_text = ""
    if tier_line_m:
        tier_line_text = tier_line_m.group(0)
        if clone_re.search(tier_line_text):
            has_clone_framing = True
            if not re.search(r'newest\s+same-class', clean_text, re.IGNORECASE):
                print("(k) WARN: clone-framed plan does not name its newest same-class comparison (§2.6 :75)")

    # (l) Clone-mutation down-tier warn (WARN-only): a clone-framed plan firing
    # T-2 at a declared tier below T2. Segment-bounded: T-2 counts as firing
    # iff it appears after 'trigger(s) fired:' and before the first '.' or '('.
    # Cannot see: actual mutation behaviour (only the declared trigger); inert
    # on plans that under-declare T-2. Shipped inert — no down-tiered T-2
    # population exists until the §1 executable lands.
    # Under-match floor: a tier line with neither 'trigger fired:' nor 'triggers
    # fired:' skips silently — some diagnostics use parenthetical forms the
    # segment bound cannot parse.
    if has_clone_framing and tier_line_m:
        fired_seg = re.search(r'triggers?\s+fired:\s*', tier_line_text)
        if fired_seg:
            after = tier_line_text[fired_seg.end():]
            seg_end = re.search(r'[.(]', after)
            segment = after[:seg_end.start()] if seg_end else after
            if re.search(r'\bT-2\b', segment):
                if ct_match:
                    declared_tier = int(ct_match.group(1))
                    if declared_tier < 2:
                        print("(l) WARN: clone-framed plan firing T-2 declares tier < T2 — §2.6: clone framing is not licence to down-tier; consider self-escalation to the cold panel")

    # Shared single-line inline backtick span extractor for (n) and (o1)
    backtick_spans = []
    for line in clean_text.splitlines():
        for m in re.finditer(r'`([^`\n]+)`', line):
            backtick_spans.append(m.group(1))

    # (n) Non-F grep lint (WARN-only): flags inline backtick grep commands using
    # literal patterns without -F/--fixed-strings. Fenced blocks excluded via
    # clean_text. Documented misses: unquoted patterns, fenced-block greps.
    for span in backtick_spans:
        if not (span.startswith('grep ') or '| grep ' in span):
            continue
        grep_part = span[span.rindex('| grep ') + 2:] if '| grep ' in span else span
        if re.search(r'(?:^|\s)-\w*F', grep_part) or '--fixed-strings' in grep_part:
            continue
        if re.search(r'(?:^|\s)-\w*[EPG]', grep_part):
            continue
        pattern_match = re.search(r'"([^"]*)"', grep_part)
        if not pattern_match:
            pattern_match = re.search(r"'([^']*)'", grep_part)
        if not pattern_match:
            continue
        pattern_text = pattern_match.group(1)
        if re.search(r'[\[\](){}|^$*+?\\]', pattern_text):
            continue
        print(f"(n) WARN: `{span}` — grep on literal pattern without -F (ugrep-shim hazard)")

    # (o) Path checks — two sub-rules
    REPO_ROOTS = {'knowledge', 'scripts', 'tests', 'src', 'web', 'engines', 'agents', 'verdicts', 'logs', 'governance'}
    KNOWN_PROJECTS = {'anvil', 'bellows', 'governance', 'invoice-pulse', 'lessons-forge', 'forge'}
    try:
        from bellows_root import resolve_governance_root as _resolve_gov
        SHOP_ROOT = str(_resolve_gov())  # the governance root on THIS machine (name kept for the (o1) read below)
    except Exception:
        SHOP_ROOT = str(Path.home() / 'Developer' / 'eluvian-governance')

    plan_path_resolved = str(Path(plan_path).resolve())
    project_root = None
    if '/knowledge/' in plan_path_resolved:
        project_root = plan_path_resolved[:plan_path_resolved.index('/knowledge/')]
    else:
        candidate_dir = Path(plan_path).resolve().parent
        while candidate_dir != candidate_dir.parent:
            if (candidate_dir / '.git').exists():
                project_root = str(candidate_dir)
                break
            candidate_dir = candidate_dir.parent

    exclusion_set = set()
    all_excl_entries = list(gates._extract_plan_required_deposits(plan_text))
    excl_scope_files, _ = gates._extract_plan_scope(plan_text)
    all_excl_entries.extend(excl_scope_files)
    for _, step_num_str in step_headers:
        st = gates._extract_step_text(plan_text, int(step_num_str))
        if st:
            all_excl_entries.extend(gates._extract_plan_required_deposits(st))
            sf, _ = gates._extract_plan_scope(st)
            all_excl_entries.extend(sf)
    for entry in all_excl_entries:
        exclusion_set.add(entry)
        parts = entry.split('/')
        if parts and parts[0] in KNOWN_PROJECTS:
            stripped = '/'.join(parts[1:])
            if stripped:
                exclusion_set.add(stripped)

    # (o1) Input-path existence (WARN-only)
    path_char_re = re.compile(r'^[A-Za-z0-9_./-]+$')
    candidates_o1 = []
    seen_o1 = set()
    for span in backtick_spans:
        if '/' not in span:
            continue
        if not path_char_re.match(span):
            continue
        segments = span.split('/')
        if span.startswith('/') and segments and segments[0] == '':
            segments = segments[1:]
        if len(segments) < 2 or any(s == '' for s in segments):
            continue
        if not span.startswith('/Users/') and segments[0] not in REPO_ROOTS:
            continue
        if span not in seen_o1:
            seen_o1.add(span)
            candidates_o1.append(span)

    excluded_o1 = 0
    fired_o1 = []
    fired_o1_seen = set()
    for cand in candidates_o1:
        if cand in exclusion_set:
            excluded_o1 += 1
            continue
        exists = False
        if cand.startswith('/Users/'):
            exists = os.path.exists(cand)
        elif project_root is not None:
            if os.path.exists(os.path.join(project_root, cand)):
                exists = True
            elif os.path.exists(os.path.join(SHOP_ROOT, cand)):
                exists = True
        if not exists and cand not in fired_o1_seen:
            if cand.startswith('/Users/') or project_root is not None:
                fired_o1.append(cand)
                fired_o1_seen.add(cand)

    if candidates_o1:
        print(f"(o1) INFO: candidates={len(candidates_o1)} excluded={excluded_o1} fired={len(fired_o1)}")

    uncap = os.environ.get('PLAN_LINT_UNCAP') == '1'
    listing_limit = len(fired_o1) if uncap else 10
    for fp in fired_o1[:listing_limit]:
        print(f"(o1) WARN: missing path `{fp}`")
    if not uncap and len(fired_o1) > 10:
        print(f"(o1) WARN: (+{len(fired_o1) - 10} more)")

    # (o2) Deposits-entry form (WARN-only): entries should be project-prefixed
    # or absolute. Scope entries are EXEMPT (C1).
    o2_deposits = list(gates._extract_plan_required_deposits(plan_text))
    for _, step_num_str in step_headers:
        st = gates._extract_step_text(plan_text, int(step_num_str))
        if st:
            o2_deposits.extend(gates._extract_plan_required_deposits(st))
    o2_deposits = list(dict.fromkeys(o2_deposits))
    for dep in o2_deposits:
        if dep.startswith('/Users/'):
            continue
        parts = dep.split('/')
        if parts and parts[0] in KNOWN_PROJECTS:
            continue
        print(f"(o2) WARN: Deposits entry `{dep}` is not project-prefixed or absolute")

    # (p) C-ledger entry without executable check (WARN-only): seeds §2.8
    # convention that constraint entries should carry their runnable re-check.
    if dc_block is not None:
        p_ledger_re = re.compile(r'\*\*C(\d+)\*\*\s*—')
        for m_p in p_ledger_re.finditer(dc_block):
            match_start = m_p.start()
            line_end = dc_block.find('\n', match_start)
            if line_end == -1:
                line_end = len(dc_block)
            scanned = dc_block[match_start:line_end]
            has_backtick = bool(re.search(r'`[^`]+`', scanned))
            has_check = 'check:' in scanned.lower()
            if not has_backtick and not has_check:
                print(f"(p) WARN: C{m_p.group(1)} has no backtick-quoted command or check: token")

    # (q) Pin verification (WARN-only, advisory — scans RAW plan_text, not clean_text)
    # Pins live inside fenced bootstrap blocks; clean_text would blind this check.
    try:
        repo_base = BELLOWS_ROOT.parent
        project_name = header.get("project", "") if header else ""
        p_repo = str(repo_base / project_name) if project_name else None
        r_repo = str(repo_base)
        pin_telemetry, pin_warns = _check_pins(plan_text, p_repo, r_repo)
        for kind, line, prefix, result in pin_telemetry:
            print(f"PIN-CHECK: kind={kind} line={line} token={prefix}… result={result}")
        for w in pin_warns:
            print(w)
    except Exception as e:
        print(f"(q) WARN: check errored ({e})")

    _check_bare_constants(plan_text)
    _check_discharges(plan_text)
    _check_shipped_doctrine_tranche(plan_path)

    for status, check, detail in results:
        print(f"{status}: {check} — {detail}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <plan-path>", file=sys.stderr)
        sys.exit(2)
    sys.exit(lint(sys.argv[1]))
