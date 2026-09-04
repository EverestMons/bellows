#!/usr/bin/env python3
"""cycle_check — drafting-cycle validator (CONTINUE / BAR_MET / ESCALATE).

Emits exactly one verdict to stdout:
  CONTINUE   (exit 0)
  BAR_MET    (exit 0)
  ESCALATE:* (exit 1)

Exit 2 = internal error (bad args, unreadable file).
Strictly read-only — writes nothing, commits nothing.
"""

import re
import subprocess
import sys
from pathlib import Path

# C-3: bellows root on sys.path so bellows_root is importable from scripts/ (thread 52)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cycle_yields import (
    extract_dc_blocks,
    parse_lens_line,
    PASS_FOLDED_RE,
    PASS_DRY_RE,
)
from walk_register_lint import (
    validate_file as _validate_register,
    STATUS_CONFORMANT as _REG_CONFORMANT,
    STATUS_PRE_SCHEMA as _REG_PRE_SCHEMA,
    STATUS_LEGACY_SCHEMA as _REG_LEGACY_SCHEMA,
)
# Statuses that do not warrant a register WARN: CONFORMANT (valid), PRE-SCHEMA (pre-dates
# schema, not a defect), LEGACY_SCHEMA (honest old-version record, not a defect).
_REGISTER_SILENT_STATUSES = frozenset({_REG_CONFORMANT, _REG_PRE_SCHEMA, _REG_LEGACY_SCHEMA})

CLASS_SPLIT_RE = re.compile(r"instruction\s+(\d+)\s*/\s*record\s+(\d+)")
WALK_STATUS_RE = re.compile(
    r"\*\*Walk\s+(\d+)\s+STATUS:\*\*\s*(\d+)\s+folded"
)
WALK_NUM_RE = re.compile(r"^w(\d+)$", re.IGNORECASE)
WALK_SECTION_RE = re.compile(r"\*\*Walk\s+(\d+)\b")
WALK_REGISTER_RE = re.compile(r"\*\*Walk\s+register:\*\*\s*(.*)")
_FOLD_RE = re.compile(r"(?:(?:^|[;.:)])\s*)(\w+)\s+(?:\([^)]*\)\s+)?(\d+)\s+folded\b")
_DRY_RE = re.compile(r"(?:(?:^|[;.:)])\s*)(\w+)\s+(?:\([^)]*\)\s+)?(?:dry|DRY)\b")
RESTRUCTURING_RE = re.compile(
    r"\b(?:restructuring|restructure|reorder)\b", re.IGNORECASE
)
_NEGATION_RE = re.compile(r"\bNOT\s+(?:CLOSED|MET)\b|\bnot\s+met\b|\bunmet\b", re.IGNORECASE)
_CLAIM_RE = re.compile(r"\bBAR\s+MET\b|\bmet\s+the\s+bar\b|\bCYCLE\s+COMPLETE\b", re.IGNORECASE)

def _has_closure_claim(block_text):
    # 58: bare **Closing:** heading is not a claim; strip negated spans first
    stripped = _NEGATION_RE.sub("", block_text)
    return bool(_CLAIM_RE.search(stripped))
MANIFEST_HEADING_RE = re.compile(r"^## Cycle Manifest\s*$", re.MULTILINE)

# The four keys the emitter writes to validation: (DC:253 — COMPUTED, never hand-typed).
# Both the gate in run_check and any caller that needs the authoritative set read this
# constant so the two cannot drift if a key is added.
MANIFEST_VALIDATION_KEYS = frozenset({
    "cycle_check", "plan_lint", "fold_check", "propagation_check"
})


def walk_number(token):
    m = WALK_NUM_RE.match(token)
    return int(m.group(1)) if m else None


def _find_git_root(path):
    try:
        r = subprocess.run(
            ["git", "-C", str(path.parent if path.is_file() else path),
             "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5,
        )
        return Path(r.stdout.strip()) if r.returncode == 0 else None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


def extract_per_pass_metadata(line):
    """Per-pass class-split and restructuring from a raw lens line.

    The class-split binds to the immediately-preceding N-folded pass.
    Returns {token: {class_split: (instr, rec)|None, restructuring: bool}}.
    """
    clean = re.sub(r"\*\*", "", line)
    result = {}
    folds = list(_FOLD_RE.finditer(clean))
    dry_starts = [m.start() for m in _DRY_RE.finditer(clean)]
    for i, m in enumerate(folds):
        token, end = m.group(1), m.end()
        win_end = len(clean)
        if i + 1 < len(folds):
            win_end = min(win_end, folds[i + 1].start())
        for ds in dry_starts:
            if ds > end:
                win_end = min(win_end, ds)
                break
        sc = clean.find(";", end)
        if 0 <= sc < win_end:
            win_end = sc
        window = clean[end:win_end]
        cs = CLASS_SPLIT_RE.search(window)
        result[token] = {
            "class_split": (int(cs.group(1)), int(cs.group(2))) if cs else None,
            "restructuring": bool(RESTRUCTURING_RE.search(window)),
        }
    return result


def parse_block(block_text):
    """Parse a DC block into structured walk data."""
    walk_data = {}
    walk_status = {}
    assert1_checks = []
    has_lens_lines = False
    has_unparseable = False
    has_any_parsed = False
    has_class_split = False
    restructuring_walks = set()
    claims_closure = _has_closure_claim(block_text)
    walk_register_ref = None
    current_walk_section = None

    for raw_line in block_text.splitlines():
        m = WALK_REGISTER_RE.search(raw_line)
        if m and walk_register_ref is None:
            raw_ref = m.group(1).strip()
            # C-2: take backtick span if present; else first whitespace-delimited .md token (thread 52)
            bt_m = re.search(r'`([^`]+)`', raw_ref)
            if bt_m:
                walk_register_ref = bt_m.group(1).strip()
            else:
                tokens = raw_ref.split()
                md_tok = next((t.rstrip('.') for t in tokens if t.rstrip('.').endswith('.md')), None)
                walk_register_ref = md_tok if md_tok else None

        m = WALK_STATUS_RE.search(raw_line)
        if m:
            wn, total = int(m.group(1)), int(m.group(2))
            cs = CLASS_SPLIT_RE.search(raw_line[m.end():])
            walk_status[wn] = {
                "total": total,
                "instruction": int(cs.group(1)) if cs else None,
                "record": int(cs.group(2)) if cs else None,
            }
            if cs:
                has_class_split = True
            continue

        m_sec = WALK_SECTION_RE.match(raw_line)
        if m_sec and "STATUS:" not in raw_line:
            current_walk_section = int(m_sec.group(1))

        parsed = parse_lens_line(raw_line)
        if parsed is None:
            continue
        has_lens_lines = True

        all_unparseable = all(item[0] == "UNPARSEABLE" for item in parsed)

        if all_unparseable and current_walk_section is not None:
            clean_lower = re.sub(r"\*\*", "", raw_line).lower()
            if re.search(r"\bdry\b", clean_lower) and "folded" not in clean_lower:
                walk_data.setdefault(current_walk_section, {
                    "total_folds": 0, "instruction": None,
                    "record": None, "lenses": set(),
                })
                has_any_parsed = True
                continue

        if all_unparseable:
            has_unparseable = True
            continue

        for item in parsed:
            if item[0] == "UNPARSEABLE":
                has_unparseable = True
                continue
            has_any_parsed = True
            lens_name, pass_token, fold_str = item[0], item[1], item[2]
            fold_count = int(fold_str)
            wn = walk_number(pass_token)
            if wn is None:
                continue
            wd = walk_data.setdefault(wn, {
                "total_folds": 0, "instruction": None,
                "record": None, "lenses": set(),
            })
            wd["total_folds"] += fold_count
            if fold_count > 0:
                wd["lenses"].add(lens_name)

        per_pass = extract_per_pass_metadata(raw_line)
        for token, meta in per_pass.items():
            wn = walk_number(token)
            if wn is None:
                continue
            if meta["restructuring"]:
                restructuring_walks.add(wn)
            cs = meta["class_split"]
            if cs is None:
                continue
            instr, rec = cs
            has_class_split = True
            fold_for_token = None
            for item in parsed:
                if item[0] != "UNPARSEABLE" and item[1] == token:
                    fold_for_token = int(item[2])
                    break
            if fold_for_token is not None:
                lens_name = next(
                    (it[0] for it in parsed if it[0] != "UNPARSEABLE"), "?"
                )
                assert1_checks.append(
                    (lens_name, token, fold_for_token, instr, rec)
                )
            wd = walk_data.setdefault(wn, {
                "total_folds": 0, "instruction": None,
                "record": None, "lenses": set(),
            })
            if wd["instruction"] is None:
                wd["instruction"] = 0
                wd["record"] = 0
            wd["instruction"] += instr
            wd["record"] += rec

    for wn, ws in walk_status.items():
        if wn not in walk_data:
            walk_data[wn] = {
                "total_folds": ws["total"],
                "instruction": ws["instruction"],
                "record": ws["record"],
                "lenses": set(),
            }

    return {
        "walk_data": walk_data,
        "walk_status": walk_status,
        "assert1_checks": assert1_checks,
        "has_lens_lines": has_lens_lines,
        "has_unparseable": has_unparseable,
        "has_any_parsed": has_any_parsed,
        "has_class_split": has_class_split,
        "restructuring_walks": restructuring_walks,
        "claims_closure": claims_closure,
        "walk_register_ref": walk_register_ref,
    }


def check_assert_1(parsed):
    """Internal arithmetic. PASS | FAIL | N/A."""
    checks = parsed["assert1_checks"]
    if not checks:
        return "N/A"
    for _, _, fold_count, instr, rec in checks:
        if instr + rec != fold_count:
            return "FAIL"
    for wn, ws in parsed["walk_status"].items():
        if ws["instruction"] is None:
            continue
        wd = parsed["walk_data"].get(wn)
        if wd is None or wd["instruction"] is None:
            continue
        if wd["total_folds"] != ws["total"]:
            continue
        if ws["instruction"] != wd["instruction"] or ws["record"] != wd["record"]:
            return "FAIL"
    return "PASS"


def check_assert_2(parsed, plan_path):
    """Evidence exists. Returns (register_result, uncommitted, git_has_context, register_warn).

    register_warn is a WARN string when the resolved register fails validation, or None.
    Does NOT assign register_result = "FAIL": the pre-wired arm at run_check():424 is the
    earned promotion path for blocking enforcement; warn-first is deliberate here.
    """
    register_result = "N/A"
    uncommitted = False
    git_has_context = False
    register_warn = None

    ref = parsed["walk_register_ref"]
    if ref:
        # C-3: three-step resolution order (thread 52)
        resolved = False
        resolved_path = None
        # Step 1: absolute path
        if Path(ref).is_absolute():
            candidate = Path(ref)
            try:
                resolved = candidate.exists()
            except OSError:
                resolved = False
            if resolved:
                resolved_path = candidate
            register_result = "PASS" if resolved else "UNRESOLVED"
        else:
            git_root = _find_git_root(plan_path)
            # Step 2: git_root / ref
            if git_root:
                candidate = git_root / ref
                try:
                    resolved = candidate.exists()
                except OSError:  # C-2: oversized path component (thread 52)
                    resolved = False
                if resolved:
                    resolved_path = candidate
                    register_result = "PASS"
            # Step 3: governance root fallback
            if not resolved:
                try:
                    from bellows_root import resolve_governance_root
                    gov_root = resolve_governance_root()
                except ImportError:
                    gov_root = None
                if gov_root:
                    candidate = gov_root / ref
                    try:
                        resolved = candidate.exists()
                    except OSError:
                        resolved = False
                    if resolved:
                        resolved_path = candidate
                        register_result = "PASS"
            if not resolved:
                register_result = "UNRESOLVED"

        # Validate the resolved register; surface non-conformant status as a WARN.
        # Import happens at function scope to match the existing fold_check pattern (thread 29).
        if resolved_path is not None:
            try:
                reg_status, _, _ = _validate_register(resolved_path)
                if reg_status not in _REGISTER_SILENT_STATUSES:
                    register_warn = (
                        f"WARN: walk register {resolved_path.name!r}"
                        f" — {reg_status} (non-conformant register; does not block verdict)"
                    )
            except Exception:
                pass  # validation failure does not affect register_result or verdict

    walk_data = parsed["walk_data"]
    if walk_data:
        git_root = _find_git_root(plan_path)
        if git_root:
            try:
                rel = plan_path.resolve().relative_to(git_root.resolve())
                r = subprocess.run(
                    ["git", "-C", str(git_root), "log", "--oneline",
                     "--", str(rel)],
                    capture_output=True, text=True, timeout=10,
                )
                if r.returncode == 0 and r.stdout.strip():
                    commits = r.stdout.strip().splitlines()
                    pat = re.compile(r"drafting\(|\[draft\]|deposit\(")
                    walk_commits = [c for c in commits if pat.search(c)]
                    if walk_commits:
                        git_has_context = True
                        max_walk = max(walk_data.keys())
                        if len(walk_commits) < max_walk:
                            uncommitted = True
            except (subprocess.TimeoutExpired, ValueError):
                pass

    return register_result, uncommitted, git_has_context, register_warn


def check_assert_3(parsed, plan_path, git_has_context):
    """Fold happened — baseline exists. Degrades with assert #2.
    PASS | FAIL | N/A."""
    walk_data = parsed["walk_data"]
    any_folds = any(wd["total_folds"] > 0 for wd in walk_data.values())
    if not any_folds:
        return "N/A"
    baseline = plan_path.parent / f".{plan_path.name}.foldcheck.json"
    if not baseline.exists():
        return "FAIL" if git_has_context else "N/A"
    return "PASS"


def get_instruction_counts(parsed):
    """Per-walk instruction counts from best available source."""
    walk_data = parsed["walk_data"]
    walk_status = parsed["walk_status"]
    counts = {}
    for wn in sorted(set(walk_data) | set(walk_status)):
        ws = walk_status.get(wn)
        if ws and ws["instruction"] is not None:
            counts[wn] = ws["instruction"]
            continue
        wd = walk_data.get(wn)
        if wd and wd["instruction"] is not None:
            counts[wn] = wd["instruction"]
            continue
        if wd and wd["total_folds"] == 0:
            counts[wn] = 0
            continue
        counts[wn] = None
    return counts


def check_plateau(walk_data, current_walk, instruction_counts):
    """3+ consecutive walks at flat instruction count, no new finding class.
    Returns True, False, or None (N/A)."""
    current_instr = instruction_counts.get(current_walk)
    if current_instr is None:
        return None
    consecutive = 0
    for wn in range(current_walk, 0, -1):
        instr = instruction_counts.get(wn)
        if instr is None or instr != current_instr:
            break
        wn_lenses = walk_data.get(wn, {}).get("lenses", set())
        prior = set()
        for p in range(1, wn):
            prior |= walk_data.get(p, {}).get("lenses", set())
        if wn_lenses - prior:
            break
        consecutive += 1
    return consecutive >= 3


def run_check(plan_path, warnings=None):
    """Main entry. Returns (verdict, exit_code).

    warnings: optional list; register WARN strings are appended when supplied.
    All 43 existing call sites pass no kwarg and remain byte-for-byte unaffected.
    Only main()'s verdict path passes a list so it can print WARNs before the verdict.
    Do NOT pass warnings on the --emit-manifest path (:562): that call only fills the
    manifest validation: field and must not inject advisory text into the artifact.
    """
    try:
        text = plan_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"ERROR: cannot read {plan_path}: {e}", file=sys.stderr)
        return None, 2

    blocks = extract_dc_blocks(text)
    if len(blocks) != 1:
        return "ESCALATE:unparseable", 1

    parsed = parse_block(blocks[0])
    walk_data = parsed["walk_data"]

    if parsed["has_lens_lines"] and not parsed["has_any_parsed"]:
        return "ESCALATE:unparseable", 1

    # C-1: plain walk lines with no parseable lens data → unparseable, not vacuous CONTINUE (thread 52)
    # Walk 0 (context pin) is excluded; it carries no lens data and legitimately returns CONTINUE.
    # **Walk N:** bold-heading prose (legacy format) is NOT a bullet-list signal; those plans return CONTINUE.
    block = blocks[0]
    has_walk_signal = bool(re.search(
        r"(?im)^\s*-\s*Walk\s+[1-9]\d*\b|\bw[1-9]\d*\s+(?:\d+\s+folded|dry)\b", block
    ))
    if has_walk_signal and not walk_data:
        return "ESCALATE:unparseable", 1

    if not walk_data:
        return "CONTINUE", 0

    current_walk = max(walk_data.keys())
    if current_walk == 0:
        return "CONTINUE", 0

    a1 = check_assert_1(parsed)
    a2_reg, a2_uncom, a2_git, a2_warn = check_assert_2(parsed, plan_path)
    a3 = check_assert_3(parsed, plan_path, a2_git)

    if warnings is not None and a2_warn is not None:
        warnings.append(a2_warn)

    if a1 == "FAIL":
        return "ESCALATE:assert-fail:1", 1
    if a2_reg in ("FAIL", "UNRESOLVED"):  # C-3: UNRESOLVED routes same as FAIL (thread 52)
        return "ESCALATE:assert-fail:2", 1
    if a3 == "FAIL":
        return "ESCALATE:assert-fail:3", 1
    if a2_uncom:
        return "ESCALATE:uncommitted-walk", 1

    instruction_counts = get_instruction_counts(parsed)

    # BASIS (thread 133). The ladder below is first-match-wins over several
    # conditions, and a verdict alone does not say which of them had DATA to
    # evaluate. Measured 2026-09-04: a cycle whose restructuring fold was declared
    # in its walk register but not in its body returned ESCALATE:yield-rising, and
    # the CEO resumed past it; the machine-correct ruling was restructuring-fold,
    # which is stronger (no walk containing one can meet the bar). `restructuring_walks`
    # is read ONLY from the body's per-lens lines, so an empty set is indistinguishable
    # from "none declared" unless it is stated. Emitted on ESCALATE only — the
    # CONTINUE/BAR_MET paths stay byte-identical, because a checker that speaks on
    # every run trains the reader to skim it (thread 117's habituation finding).
    def _escalate(tag):
        if warnings is not None:
            restr = parsed["restructuring_walks"]
            warnings.append(
                "BASIS: current_walk=%s instruction_counts=%s restructuring_walks=%s"
                % (
                    current_walk,
                    {k: instruction_counts[k] for k in sorted(instruction_counts)},
                    (sorted(restr) if restr else "EMPTY — none declared in the plan BODY; "
                     "this arm had no data to evaluate"),
                )
            )
        return tag, 1

    if current_walk in parsed["restructuring_walks"]:
        return _escalate("ESCALATE:restructuring-fold")

    cur_instr = instruction_counts.get(current_walk)
    prior_instr = instruction_counts.get(current_walk - 1)
    if cur_instr is not None and prior_instr is not None:
        if cur_instr > prior_instr:
            return _escalate("ESCALATE:yield-rising")

    plateau = check_plateau(walk_data, current_walk, instruction_counts)
    if plateau:
        return _escalate("ESCALATE:plateau")

    cur_wd = walk_data[current_walk]
    if cur_instr is not None:
        current_dry = cur_instr == 0
    else:
        current_dry = cur_wd["total_folds"] == 0

    asserts_ok = all(r in ("PASS", "N/A") for r in [a1, a2_reg, a3])

    if current_dry and asserts_ok:
        verdict = "CONTINUE" if parsed["has_unparseable"] else "BAR_MET"
    else:
        verdict = "CONTINUE"

    # Gate: manifest validation: must carry every key the emitter writes (DC:253, P2-P8).
    # No subprocess; key comparison is against the MANIFEST_VALIDATION_KEYS constant.
    if verdict == "BAR_MET":
        stored = _manifest_validation_keys(text)
        if stored is not None and not MANIFEST_VALIDATION_KEYS.issubset(stored):
            verdict = "CONTINUE"

    if parsed["claims_closure"] and verdict == "CONTINUE" and not parsed["has_unparseable"]:
        return "ESCALATE:claimed-close-unmet", 1

    return verdict, 0


def parse_manifest_stanza(plan_text):
    """Extract fields from an existing ## Cycle Manifest stanza in the plan.
    Returns dict of field_name→value, or empty dict if no stanza found.
    Handles 2-space continuation lines for multi-line values."""
    m = MANIFEST_HEADING_RE.search(plan_text)
    if not m:
        return {}
    start = m.end()
    end_m = re.search(r"^(?:## |---)", plan_text[start:], re.MULTILINE)
    stanza_text = plan_text[start:start + end_m.start()] if end_m else plan_text[start:]

    fields = {}
    current_key = None
    current_val = None
    for line in stanza_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if line.startswith("  ") and current_key:
            current_val = current_val.rstrip(",") + ", " + stripped.rstrip(",")
            fields[current_key] = current_val
            continue
        fm = re.match(r"^(\w[\w_]*):\s*(.*)", stripped)
        if fm:
            current_key = fm.group(1)
            current_val = fm.group(2).strip()
            fields[current_key] = current_val
    return fields


def _manifest_validation_keys(plan_text):
    """Return the frozenset of key names in the stored validation: line, or None to skip.

    Returns frozenset() (blocks BAR_MET) when:
      - no ## Cycle Manifest heading present (arm A — silence is not innocence),
      - heading found but stanza does not parse as key-value pairs (arm B),
      - validation field absent or empty.
    Returns None (skip check) when validation value is <declare> or N/A — those
    are legitimate mid-emission and no-walk-data placeholders, not parse failures.
    Returns frozenset of key names when a proper key=value validation line is present.
    """
    if not MANIFEST_HEADING_RE.search(plan_text):
        return frozenset()  # arm A: no heading — absence is a defect at BAR_MET
    manifest = parse_manifest_stanza(plan_text)
    if not manifest:
        return frozenset()  # arm B: heading exists but stanza did not parse
    validation_val = manifest.get("validation", "")
    if not validation_val:
        return frozenset()  # validation field absent or empty
    if validation_val == "<declare>" or validation_val == "N/A":
        return None  # explicit skip values — not a parse failure
    return frozenset(
        part.split("=")[0].strip()
        for part in validation_val.split(",")
        if "=" in part
    )


def _extract_tier_from_plan(plan_text, dc_block):
    """Extract tier (T0/T1/T2) from DC block Tier line or header cycle_tier."""
    if dc_block:
        m = re.search(r"\*\*Tier:\*\*\s*(T[012])\b", dc_block)
        if m:
            return m.group(1)
    m = re.search(r"\*\*cycle_tier:\*\*\s*(T[012])\b", plan_text)
    if m:
        return m.group(1)
    return None


def _compute_coherence(parsed, plan_path):
    """Compute the coherence field value for --emit-manifest."""
    ref = parsed.get("walk_register_ref")
    if not ref:
        return "N/A (no register declared)"
    git_root = _find_git_root(plan_path)
    if not git_root:
        return "N/A"
    reg_path = git_root / ref
    if not reg_path.exists():
        return "N/A"
    walk_data = parsed.get("walk_data", {})
    total_walks = max(walk_data.keys()) if walk_data else 0
    if total_walks == 0:
        return "N/A"
    try:
        reg_text = reg_path.read_text(encoding="utf-8")
        walks_with_rows = 0
        for wn in range(1, total_walks + 1):
            if re.search(rf"\b[Ww]alk\s+{wn}\b|\bw{wn}\b", reg_text):
                walks_with_rows += 1
        return f"{walks_with_rows}/{total_walks} walks have register rows"
    except Exception:
        return "N/A"


def emit_manifest(plan_path):
    """Emit a complete ## Cycle Manifest stanza to STDOUT. Returns exit code.
    Strictly read-only — writes nothing, modifies no file."""
    try:
        plan_text = plan_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"ERROR: cannot read {plan_path}: {e}", file=sys.stderr)
        return 2

    blocks = extract_dc_blocks(plan_text)
    dc_block = blocks[0] if len(blocks) == 1 else None

    if dc_block:
        parsed = parse_block(dc_block)
        walk_data = parsed["walk_data"]
        walk_count = max(walk_data.keys()) if walk_data else 0

        instruction_counts = get_instruction_counts(parsed)
        yields_parts = []
        yields_ok = walk_count > 0
        for wn in range(1, walk_count + 1):
            ic = instruction_counts.get(wn)
            if ic is None:
                yields_ok = False
                break
            yields_parts.append(str(ic))
        yields_str = ", ".join(yields_parts) if yields_ok else "N/A"

        verdict, _ = run_check(plan_path)
        if verdict is None:
            verdict = "N/A"

        try:
            lint_r = subprocess.run(
                [sys.executable, str(Path(__file__).resolve().parent / "plan_lint.py"),
                 str(plan_path)],
                capture_output=True, text=True, timeout=30,
            )
            fail_count = lint_r.stdout.count("FAIL:")
            lint_val = f"{fail_count}_FAIL"
        except Exception:
            lint_val = "N/A"

        baseline = plan_path.parent / f".{plan_path.name}.foldcheck.json"
        if baseline.exists():
            try:
                fc_r = subprocess.run(
                    [sys.executable,
                     str(Path(__file__).resolve().parent / "fold_check.py"),
                     str(plan_path)],
                    capture_output=True, text=True, timeout=30,
                )
                fold_verdict = "PASS" if fc_r.returncode == 0 else "N/A"
            except Exception:
                fold_verdict = "N/A"
        else:
            fold_verdict = "N/A"

        try:
            pc_r = subprocess.run(
                [sys.executable,
                 str(Path(__file__).resolve().parent / "propagation_check.py"),
                 str(plan_path)],
                capture_output=True, text=True, timeout=30,
            )
            if pc_r.returncode == 0:
                pc_val = "CLEAN"
            elif pc_r.returncode == 1:
                import re as _re
                pm = _re.search(r'DIVERGENCES:\s*(\d+)', pc_r.stdout)
                pc_val = f"DIVERGENT:{pm.group(1)}" if pm else "DIVERGENT:?"
            elif pc_r.returncode == 2:
                pc_val = "NOT_RUN"
            else:
                pc_val = "N/A"
        except Exception:
            pc_val = "N/A"

        validation_str = (
            f"cycle_check={verdict}, plan_lint={lint_val}, "
            f"fold_check={fold_verdict}, propagation_check={pc_val}"
        )
        coherence_str = _compute_coherence(parsed, plan_path)
    else:
        walk_count = "N/A"
        yields_str = "N/A"
        validation_str = "N/A"
        coherence_str = "N/A"

    existing = parse_manifest_stanza(plan_text)

    tier = existing.get("tier")
    if not tier:
        tier = _extract_tier_from_plan(plan_text, dc_block)
    if not tier:
        tier = "<declare>"

    target = existing.get("target", "<declare>")
    plan_class = existing.get("class", "<declare>")
    reads = existing.get("reads", "<declare>")
    writes = existing.get("writes", "<declare>")
    open_forks = existing.get("open_forks", "<declare>")

    print("## Cycle Manifest")
    print(f"tier: {tier}")
    print(f"target: {target}")
    print(f"class: {plan_class}")
    print(f"reads: {reads}")
    print(f"writes: {writes}")
    print(f"open_forks: {open_forks}")
    print(f"walks: {walk_count}")
    print(f"yields: {yields_str}")
    print(f"validation: {validation_str}")
    print(f"coherence: {coherence_str}")
    return 0


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--emit-manifest":
        plan_path = Path(sys.argv[2])
        if not plan_path.exists():
            print(f"ERROR: {plan_path} not found", file=sys.stderr)
            sys.exit(2)
        sys.exit(emit_manifest(plan_path))

    if len(sys.argv) != 2:
        print("Usage: cycle_check.py [--emit-manifest] <plan.md>", file=sys.stderr)
        sys.exit(2)
    plan_path = Path(sys.argv[1])
    if not plan_path.exists():
        print(f"ERROR: {plan_path} not found", file=sys.stderr)
        sys.exit(2)
    verdict_warnings = []
    verdict, code = run_check(plan_path, warnings=verdict_warnings)
    if verdict is None:
        sys.exit(2)
    for w in verdict_warnings:
        print(w)  # before verdict; stdout contract (P8): verdict is always the LAST line
    print(verdict)
    sys.exit(code)


if __name__ == "__main__":
    main()
