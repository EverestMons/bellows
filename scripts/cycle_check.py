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

from cycle_yields import (
    extract_dc_blocks,
    parse_lens_line,
    PASS_FOLDED_RE,
    PASS_DRY_RE,
)

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
CLOSURE_RE = re.compile(
    r"\*\*Closing:\*\*|\bCLOSED\b|\bCYCLE\s+COMPLETE\b"
    r"|\bbar\s+met\b|§2\s+bar\s+met",
    re.IGNORECASE,
)


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
    claims_closure = bool(CLOSURE_RE.search(block_text))
    walk_register_ref = None
    current_walk_section = None

    for raw_line in block_text.splitlines():
        m = WALK_REGISTER_RE.search(raw_line)
        if m and walk_register_ref is None:
            ref = m.group(1).strip().rstrip(".")
            walk_register_ref = ref.strip("`") if ref else None

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
            if RESTRUCTURING_RE.search(raw_line):
                restructuring_walks.add(wn)
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
        if ws["instruction"] != wd["instruction"] or ws["record"] != wd["record"]:
            return "FAIL"
    return "PASS"


def check_assert_2(parsed, plan_path):
    """Evidence exists. Returns (register_result, uncommitted, git_has_context)."""
    register_result = "N/A"
    uncommitted = False
    git_has_context = False

    ref = parsed["walk_register_ref"]
    if ref:
        git_root = _find_git_root(plan_path)
        if git_root:
            first_comp = ref.split("/")[0]
            sub_path = git_root / first_comp
            if sub_path.is_dir():
                sub_root = _find_git_root(sub_path)
                if sub_root and sub_root.resolve() != git_root.resolve():
                    register_result = "N/A"
                else:
                    register_result = "PASS" if (git_root / ref).exists() else "FAIL"
            else:
                register_result = "N/A"

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

    return register_result, uncommitted, git_has_context


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


def run_check(plan_path):
    """Main entry. Returns (verdict, exit_code)."""
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

    if not walk_data:
        return "CONTINUE", 0

    current_walk = max(walk_data.keys())
    if current_walk == 0:
        return "CONTINUE", 0

    a1 = check_assert_1(parsed)
    a2_reg, a2_uncom, a2_git = check_assert_2(parsed, plan_path)
    a3 = check_assert_3(parsed, plan_path, a2_git)

    if a1 == "FAIL":
        return "ESCALATE:assert-fail:1", 1
    if a2_reg == "FAIL":
        return "ESCALATE:assert-fail:2", 1
    if a3 == "FAIL":
        return "ESCALATE:assert-fail:3", 1
    if a2_uncom:
        return "ESCALATE:uncommitted-walk", 1

    instruction_counts = get_instruction_counts(parsed)

    if current_walk in parsed["restructuring_walks"]:
        return "ESCALATE:restructuring-fold", 1

    cur_instr = instruction_counts.get(current_walk)
    prior_instr = instruction_counts.get(current_walk - 1)
    if cur_instr is not None and prior_instr is not None:
        if cur_instr > prior_instr:
            return "ESCALATE:yield-rising", 1

    plateau = check_plateau(walk_data, current_walk, instruction_counts)
    if plateau:
        return "ESCALATE:plateau", 1

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

    if parsed["claims_closure"] and verdict == "CONTINUE" and not parsed["has_unparseable"]:
        return "ESCALATE:claimed-close-unmet", 1

    return verdict, 0


def main():
    if len(sys.argv) != 2:
        print("Usage: cycle_check.py <plan.md>", file=sys.stderr)
        sys.exit(2)
    plan_path = Path(sys.argv[1])
    if not plan_path.exists():
        print(f"ERROR: {plan_path} not found", file=sys.stderr)
        sys.exit(2)
    verdict, code = run_check(plan_path)
    if verdict is None:
        sys.exit(2)
    print(verdict)
    sys.exit(code)


if __name__ == "__main__":
    main()
