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
            # Steps 2-4 live in _resolve_register_ref — ONE resolver, because two
            # copies diverged the moment the shop-root step was added to only one.
            candidate = _resolve_register_ref(ref, plan_path)
            if candidate is not None:
                resolved = True
                resolved_path = candidate
                register_result = "PASS"
            if not resolved:
                register_result = "UNRESOLVED"

        # Validate the resolved register; surface non-conformant status as a WARN.
        # Import happens at function scope to match the existing fold_check pattern (thread 29).
        if resolved_path is not None:
            try:
                reg_status, reg_rows, _ = _validate_register(resolved_path)
                if reg_status not in _REGISTER_SILENT_STATUSES:
                    register_warn = (
                        f"WARN: walk register {resolved_path.name!r}"
                        f" — {reg_status} (non-conformant register; does not block verdict)"
                    )
                # Thread 141: the register carries findings rows while the Cycle Log's
                # Walks block declares none. The body is the ONLY place this tool reads,
                # so in that state every verdict is computed from an EMPTY record.
                # Measured on the Planner's own artifact 2026-09-05: two walks, 17
                # findings and a direction verdict lived in the register while the body
                # said nothing. ⛔ The CONJUNCTION is the discriminator, not the empty
                # body alone — an empty Walks block is CORRECT at walk 0. Over 152 plans:
                # empty-body alone matches 18 (8 declaring no register, 7 unresolvable);
                # the conjunction matches 2.
                if reg_rows and not parsed.get("walk_data"):
                    conj = (
                        f"WARN: walk register {resolved_path.name!r} carries "
                        f"{len(reg_rows)} findings row(s) but the Cycle Log's Walks block "
                        f"declares NO walks — the verdict below is computed from an empty "
                        f"record. Write the per-lens lines into the plan BODY (thread 141)."
                    )
                    register_warn = f"{register_warn}\n{conj}" if register_warn else conj
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
        # Thread 141: this early return fired BEFORE check_assert_2 was ever called, so
        # the register was never resolved and a plan whose findings live only in its
        # register got a silent CONTINUE. Consult the register first; the verdict is
        # unchanged (advisory), and the conjunction warn is the only new output.
        # ⚠️ check_assert_2's git/uncommitted work is itself guarded by `if walk_data:`,
        # so on this path it does register resolution and validation only.
        empty_reg_status = None
        if warnings is not None:
            try:
                empty_reg_status, _, _, empty_warn = check_assert_2(parsed, plan_path)
                if empty_warn is not None:
                    warnings.append(empty_warn)
                # Thread 151: BOTH warns are built inside `if resolved_path is not
                # None`, so a ref resolving to NOTHING left register_warn as None and
                # this path emitted nothing at all — while the SAME ref is a blocking
                # ESCALATE:assert-fail:2 the moment the body has walks (:488, which
                # this early return precedes). Total silence in exactly the state where
                # the register is the only place the record could be.
                # ⚠️ A WARN and not an escalation, measured: all 6 plans in this window
                # are legitimately PRE-WALK — they declare a register they have not
                # created yet, and none claims closure. Escalating would block every
                # one. ⚠️ And a warn only when UNRESOLVED, not on every empty body:
                # the BASIS note below states why a checker that speaks on every run
                # trains the reader to skim it (thread 117).
                if empty_reg_status == "UNRESOLVED":
                    warnings.append(
                        "WARN: walk register declared but UNRESOLVABLE — the body has "
                        "no walks, so this register is the only place the record could "
                        "be, and it is absent (the same ref ESCALATEs once walks exist)"
                    )
            except Exception:
                pass  # never let an advisory path change the verdict

        # ⛔ THREAD 151's SECOND ASYMMETRY IS DELIBERATELY LEFT OPEN. A plan CLAIMING
        # CLOSURE with an empty body is told CONTINUE, bypassing the closure check at
        # :553 which blocks on every other path. That looks like the same defect —
        # but it is RATIFIED: the Tier-2 state-space table (tests/test_cycle_check.py,
        # _WALK_DIM "no walk lines -> CONTINUE regardless") force-classifies rule 2 as
        # "none walk -> CONTINUE, no walk data DOMINATES close/reg", and 8 cells assert
        # it. Closing it flipped all 8. Changing a ratified precedence is a design
        # decision for the CEO, not a bug fix; recorded rather than taken.
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


def _resolve_register_ref(ref, plan_path):
    """The ONE register-ref resolver. Returns a Path that exists, or None.

    ⛔ There were TWO. check_assert_2 walked absolute -> git_root -> gov_root, and
    _compute_coherence walked git_root only. Adding the shop-root step to the first
    left the second still reporting "does not resolve" for the same file — the
    ship-one-copy class (LESSONS 2026-08-08: a value that lives in every tool that
    reads it fails its own tooling when only one copy moves). Both now call this.

    Step 4 is the shop root, and it exists because the two machine layouts put bellows
    on opposite sides of the governance root (bellows_root.resolve_governance_root):
        shop : <root>/{COMPANY.md, bellows/, ...}          — bellows UNDER the root
        mini : ~/Developer/{eluvian-governance/, bellows/} — bellows BESIDE it
    `bellows/knowledge/research/<file>` is exactly right under the shop shape, where
    step 3 resolves it; on the mini the same ref needs the root's PARENT. Measured
    2026-09-06 (thread 153): 22 plans carry that form — 18 Done/, 4 halted — all
    failing here while the file sits on disk. The RECORDS ARE NOT DEFECTIVE; they were
    written correctly for the machine that wrote them, which is why this is a resolver
    step and not an edit to 22 shipped plans.
    """
    def _ok(c):
        try:
            return c.exists()
        except OSError:  # C-2: oversized path component (thread 52)
            return False

    cand = Path(ref)
    if cand.is_absolute():
        return cand if _ok(cand) else None

    git_root = _find_git_root(plan_path)
    if git_root and _ok(git_root / ref):
        return git_root / ref

    try:
        from bellows_root import resolve_governance_root
        gov_root = resolve_governance_root()
    except Exception:
        gov_root = None
    if gov_root:
        if _ok(gov_root / ref):
            return gov_root / ref
        if _ok(gov_root.parent / ref):          # step 4 — the shop root
            return gov_root.parent / ref
    return None


def _compute_coherence(parsed, plan_path):
    """Compute the coherence field — the ONLY body-vs-register reconciliation there is.

    ⛔ EVERY NON-ANSWER NAMES ITSELF, and the empty-body case is no longer one of them.
    Measured 2026-09-06 over the plan corpus: this function returned N/A on 118 plans
    and scored 51, of which 51 were perfect and ZERO disagreed. A measure that has
    never once disagreed is reporting on its own construction (thread 152; the
    `vacuous verdict` class in GLOSSARY).

    The worst arm was `total_walks == 0 -> "N/A"`: a body declaring no walks beside a
    register full of rows is EXACTLY the drift coherence exists to detect, and it was
    the one state guaranteed to say nothing. It is now SUSPECT, which is a finding.

    ⚠️ Two different N/A paths converge on the empty-body population and only one of
    them is this thread's: 14 plans have an empty body and a declared register ref, but
    only 3 of those refs RESOLVE on this machine — the other 11 are thread 153's
    shop-layout refs, and they exit at the unresolvable arm above, not here. Each arm
    now says which it was, so the two are separable in the record.

    ⚠️ SCOPE: the walk-token matcher is UNCHANGED. Thread 152 reports it false-matching
    Gate-2 week tokens (`w28`, `w29`); measured, it cannot — the loop is bounded by
    `total_walks` (17 at corpus maximum) and `\bw2\b` does not match `w28`, because the
    trailing `\b` fails against `8`. Simulated across all 173 registers: ZERO matches on
    a w>=20 token. That contamination is real in the BACKWARD comparison run as analysis
    (scanning a register for every wN token), not in this function. Left alone on
    purpose: changing a matcher that was measured correct would be a fix on a false
    premise.

    ⚠️ What this value is NOT: a coverage measure. It counts body walks whose NUMBER is
    mentioned somewhere in the register text; it says nothing about whether those walks'
    findings have rows. `walk_register_lint` owns row shape and states its own basis.
    """
    ref = parsed.get("walk_register_ref")
    if not ref:
        return "N/A (no register declared)"
    reg_path = _resolve_register_ref(ref, plan_path)
    if reg_path is None:
        return "N/A (register ref does not resolve on this machine)"
    walk_data = parsed.get("walk_data", {})
    total_walks = max(walk_data.keys()) if walk_data else 0
    try:
        reg_text = reg_path.read_text(encoding="utf-8")
        try:
            _, reg_rows, _ = _validate_register(reg_path)
            n_rows = len(reg_rows)
        except Exception:
            n_rows = -1
        rows_note = f"{n_rows} register rows" if n_rows >= 0 else "register rows uncounted"

        if total_walks == 0:
            if n_rows > 0:
                return (f"SUSPECT: body declares NO walks while the register carries "
                        f"{n_rows} rows")
            return f"N/A (body declares no walks; {rows_note})"

        walks_with_rows = 0
        for wn in range(1, total_walks + 1):
            if re.search(rf"\b[Ww]alk\s+{wn}\b|\bw{wn}\b", reg_text):
                walks_with_rows += 1
        return (f"{walks_with_rows}/{total_walks} body walks named in the register "
                f"({rows_note}; walk-token match, NOT row coverage)")
    except Exception as e:
        return f"N/A (register unreadable: {type(e).__name__})"


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
