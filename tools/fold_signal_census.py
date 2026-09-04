#!/usr/bin/env python3
"""tools/fold_signal_census.py — instrument for diagnostic-in-cycle-battery-2026-09-04.

Answers Q1–Q7 from the diagnostic by running the battery over the committed
plan-file corpus and measuring signal coverage, count-delta rates, timing, and
output volume across all consecutive commit pairs (fold boundaries).

Populations:
  A — commit-level: every consecutive commit pair (SHA_before, SHA_after) that
      modifies a plan file under knowledge/decisions/drafts/.  Answers Q2,Q4,Q5,Q6,Q7.
  B — walk-linked: plan files with >=5 commits.  Used for Q3 walk attribution.

Extraction choice (stated — it changes the numbers):
  Historical revisions are written to a tempdir at the SAME relative path
  (<tmpdir>/knowledge/decisions/drafts/<name>.md) so plan_lint can locate the
  file, but ABSOLUTE paths referenced inside plan text may not resolve.  (o1)
  signals are EXCLUDED from all comparisons: check (o1) tests file existence on
  disk; historical revisions reference paths that may not exist in the current
  worktree, so (o1) WARNs are artifacts of extraction, not fold-induced changes.
  This exclusion is applied to BOTH sides of every fold pair, so the comparison
  is still controlled.

Count vocabulary (derived from actual tool output — per tool, NOT shared):
  plan_lint:          candidates=\\d+  excluded=\\d+  fired=\\d+  (in INFO lines)
  propagation_check:  DIVERGENCES:\\s+\\d+  (summary line)
  cycle_check:        none — emits only verdicts (CONTINUE/BAR_MET/ESCALATE:*)

Positions excluded from count vocabulary (shift whenever a fold adds a paragraph):
  plan_lint:          line[= ]\\d+  (in WARN messages — is_signal line)
  propagation_check:  L\\d+:  (line references in finding bodies — not signals)

ReaderCrashed revisions are tallied per tool per direction (before/after),
never swallowed.

Usage:
    python tools/fold_signal_census.py [--json] [--max-pairs N]

Options:
    --json          Emit full JSON result; default emits human-readable report
    --max-pairs N   Limit to first N fold pairs (for fast iteration; default: all)
"""

import argparse
import json
import re
import subprocess
import sys
import tempfile
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
GOVERNANCE = Path("/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research")

sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(ROOT))

import fold_check as fc
from fold_check import LINE_NO_RE, COUNTS_RE, DIGIT_RUN_RE, normalize, is_signal, ReaderCrashed

PYTHON = sys.executable

BATTERY_TOOLS_CANONICAL = [
    "plan_lint", "cycle_check", "fold_check",
    "propagation_check", "walk_register_lint", "mutation_check",
]

# Tools run in this census over plan files.  walk_register_lint applies only to
# registers; mutation_check excluded per diagnostic (3589ms/run, only 7 plans
# declare mutants); fold_check is the subject, not a census runner.
PLAN_TOOLS = {
    "plan_lint":          SCRIPTS / "plan_lint.py",
    "propagation_check":  SCRIPTS / "propagation_check.py",
    "cycle_check":        SCRIPTS / "cycle_check.py",
}

# Count field patterns per tool (NOT positions).
_COUNT_PATTERNS = {
    "plan_lint": re.compile(r"(candidates|excluded|fired)=(\d+)"),
    "propagation_check": re.compile(r"DIVERGENCES:\s+(\d+)"),
    "cycle_check": None,
}
# Position patterns per tool (excluded from count vocabulary; stated so a reader
# knows the exclusion is deliberate).
_POSITION_PATTERNS = {
    "plan_lint": re.compile(r"\bline[= ]\d+\b", re.IGNORECASE),
    "propagation_check": re.compile(r"\bL\d+:"),
    "cycle_check": None,
}

FOLD_INTRODUCED_RE = re.compile(r"fold.introduced", re.IGNORECASE)


# ── population derivation ─────────────────────────────────────────────────────

def build_populations(min_commits_b: int = 5):
    """Derive Population A and B from git history.

    Returns:
        pop_a: list of (plan_file_relative, [sha_oldest, ..., sha_newest]) — >=2 commits
        pop_b: subset of pop_a with >=min_commits_b commits
    """
    result = subprocess.run(
        ["git", "log", "--format=%H", "--name-only", "--",
         "knowledge/decisions/drafts/*.md"],
        capture_output=True, text=True, cwd=ROOT,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git log failed: {result.stderr}")

    file_commits: dict[str, list[str]] = defaultdict(list)
    lines = [l.rstrip() for l in result.stdout.splitlines()]
    i = 0
    while i < len(lines):
        line = lines[i]
        if len(line) == 40 and all(c in "0123456789abcdef" for c in line):
            sha = line
            i += 1
            if i < len(lines) and lines[i] == "":
                i += 1
            while i < len(lines) and not (
                len(lines[i]) == 40 and all(c in "0123456789abcdef" for c in lines[i])
            ):
                f = lines[i]
                if f and f.endswith(".md"):
                    file_commits[f].append(sha)
                i += 1
        else:
            i += 1

    pop_a = sorted(
        [(f, shas) for f, shas in file_commits.items() if len(shas) >= 2],
        key=lambda x: x[0],
    )
    pop_b = [(f, shas) for f, shas in pop_a if len(shas) >= min_commits_b]
    return pop_a, pop_b


# ── revision extraction ───────────────────────────────────────────────────────

def extract_revision(sha: str, rel_path: str, tmpdir: Path) -> Path | None:
    """Write the content of rel_path at sha into tmpdir/rel_path.  Returns target path."""
    result = subprocess.run(
        ["git", "show", f"{sha}:{rel_path}"],
        capture_output=True, cwd=ROOT,
    )
    if result.returncode != 0:
        return None
    target = tmpdir / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(result.stdout)
    return target


# ── signal computation ────────────────────────────────────────────────────────

def _filter_signals(lines, skip_o1=True):
    """Apply is_signal and optionally exclude (o1) lines."""
    return [
        l for l in lines
        if is_signal(l) and (not skip_o1 or not l.strip().startswith("(o1)"))
    ]


def _normalize_without(text, skip_re):
    """Apply normalize() but skip one of the three normalizing regexes."""
    s = text.strip()
    if skip_re is not LINE_NO_RE:
        s = LINE_NO_RE.sub("line=N", s)
    if skip_re is not COUNTS_RE:
        s = COUNTS_RE.sub(lambda m: f"{m.group(1)}=N", s)
    if skip_re is not DIGIT_RUN_RE:
        s = DIGIT_RUN_RE.sub(
            lambda m: m.group(0) if re.fullmatch(r"[0-9a-f]{6,}", m.group(0)) else "N", s
        )
    return s


def signal_set(output_lines, skip_o1=True):
    """Signal set as fold_check computes it: is_signal + normalize, (o1) excluded."""
    return frozenset(
        normalize(l) for l in output_lines
        if is_signal(l) and (not skip_o1 or not l.strip().startswith("(o1)"))
    )


def signal_set_without(output_lines, skip_re, skip_o1=True):
    """Signal set without one normalizing regex applied."""
    return frozenset(
        _normalize_without(l, skip_re) for l in output_lines
        if is_signal(l) and (not skip_o1 or not l.strip().startswith("(o1)"))
    )


# ── count extraction ──────────────────────────────────────────────────────────

def extract_count_fingerprint(tool_name: str, full_output: str) -> dict:
    """Extract count-field values from full tool output (not positions).

    Returns a dict of {field_name: value} for fields defined in _COUNT_PATTERNS.
    An empty dict means no count fields found or tool has no count vocabulary.
    """
    pat = _COUNT_PATTERNS.get(tool_name)
    if pat is None:
        return {}
    counts = {}
    for m in pat.finditer(full_output):
        groups = m.groups()
        if len(groups) == 2:  # plan_lint: (field, value)
            counts[groups[0]] = int(groups[1])
        elif len(groups) == 1:  # propagation_check: (value,)
            counts["DIVERGENCES"] = int(groups[0])
    return counts


# ── per-tool runner ───────────────────────────────────────────────────────────

def run_tool(tool_name: str, artifact_path: Path) -> dict:
    """Run one battery tool on an artifact.

    Returns:
        {
            "exit": int,
            "full_output": str,
            "signals": frozenset,          # normalized, (o1) excluded
            "signals_no_linere": frozenset,
            "signals_no_countsre": frozenset,
            "signals_no_digitre": frozenset,
            "count_fp": dict,              # count fingerprint per tool
            "raw_signal_lines": list,      # pre-normalize, (o1) excluded
            "output_lines": int,           # total non-empty output lines
            "wall_ms": float,
            "crashed": bool,
            "crash_reason": str,
        }
    """
    tool_path = PLAN_TOOLS[tool_name]
    t0 = time.perf_counter()
    try:
        p = subprocess.run(
            [PYTHON, str(tool_path), str(artifact_path)],
            capture_output=True, text=True, timeout=120,
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000
        out = (p.stdout or "") + "\n" + (p.stderr or "")
        if "Traceback (most recent call last)" in out:
            tail = [l for l in out.splitlines() if l.strip()][-1:] or ["<no detail>"]
            return {
                "crashed": True,
                "crash_reason": f"traceback: {tail[0].strip()}",
                "wall_ms": elapsed_ms,
                "output_lines": 0,
            }
        if not any(l.strip() for l in out.splitlines()):
            return {
                "crashed": True,
                "crash_reason": "no output",
                "wall_ms": elapsed_ms,
                "output_lines": 0,
            }
        lines = out.splitlines()
        raw_sig = _filter_signals(lines)
        return {
            "exit": p.returncode,
            "full_output": out,
            "signals": signal_set(lines),
            "signals_no_linere": signal_set_without(lines, LINE_NO_RE),
            "signals_no_countsre": signal_set_without(lines, COUNTS_RE),
            "signals_no_digitre": signal_set_without(lines, DIGIT_RUN_RE),
            "count_fp": extract_count_fingerprint(tool_name, out),
            "raw_signal_lines": raw_sig,
            "output_lines": sum(1 for l in lines if l.strip()),
            "wall_ms": elapsed_ms,
            "crashed": False,
            "crash_reason": "",
        }
    except (OSError, subprocess.SubprocessError) as e:
        elapsed_ms = (time.perf_counter() - t0) * 1000
        return {
            "crashed": True,
            "crash_reason": f"could not run: {e}",
            "wall_ms": elapsed_ms,
            "output_lines": 0,
        }


# ── fold pair analysis ────────────────────────────────────────────────────────

def analyze_fold_pair(sha_before: str, sha_after: str, rel_path: str, tmpdir: Path) -> dict:
    """Run all census tools on both revisions of a fold pair.

    Returns per-tool result dicts for before and after, plus crash tallies.
    """
    before_path = extract_revision(sha_before, rel_path, tmpdir / "before")
    after_path  = extract_revision(sha_after,  rel_path, tmpdir / "after")

    results = {}
    for tool_name in PLAN_TOOLS:
        before_r = run_tool(tool_name, before_path) if before_path else {
            "crashed": True, "crash_reason": "git show failed", "wall_ms": 0.0, "output_lines": 0}
        after_r  = run_tool(tool_name, after_path)  if after_path  else {
            "crashed": True, "crash_reason": "git show failed", "wall_ms": 0.0, "output_lines": 0}

        if before_r["crashed"] or after_r["crashed"]:
            results[tool_name] = {
                "crashed_before": before_r["crashed"],
                "crashed_after":  after_r["crashed"],
                "crash_reason_before": before_r.get("crash_reason", ""),
                "crash_reason_after":  after_r.get("crash_reason", ""),
                "wall_ms_before": before_r["wall_ms"],
                "wall_ms_after":  after_r["wall_ms"],
                "output_lines_before": 0,
                "output_lines_after":  0,
                "usable": False,
            }
            continue

        sig_b = before_r["signals"]
        sig_a = after_r["signals"]
        signal_changed = sig_b != sig_a

        count_changed = before_r["count_fp"] != after_r["count_fp"]

        # Normalization impact: did removing one regex reveal a change not shown normalized?
        # A "count-normalized suppression" occurs when the signal sets are EQUAL when fully
        # normalized but DIFFERENT when DIGIT_RUN_RE is skipped (the regex that collapses counts).
        # Likewise for the other two regexes.
        suppressed_by_linere   = (sig_b == sig_a) and (before_r["signals_no_linere"]   != after_r["signals_no_linere"])
        suppressed_by_countsre = (sig_b == sig_a) and (before_r["signals_no_countsre"] != after_r["signals_no_countsre"])
        suppressed_by_digitre  = (sig_b == sig_a) and (before_r["signals_no_digitre"]  != after_r["signals_no_digitre"])

        results[tool_name] = {
            "crashed_before": False,
            "crashed_after":  False,
            "crash_reason_before": "",
            "crash_reason_after":  "",
            "usable": True,
            "signal_changed": signal_changed,
            "count_changed":  count_changed,
            "suppressed_by_linere":   suppressed_by_linere,
            "suppressed_by_countsre": suppressed_by_countsre,
            "suppressed_by_digitre":  suppressed_by_digitre,
            "count_fp_before": before_r["count_fp"],
            "count_fp_after":  after_r["count_fp"],
            "signals_appeared": sorted(sig_a - sig_b),
            "signals_vanished": sorted(sig_b - sig_a),
            "wall_ms_before": before_r["wall_ms"],
            "wall_ms_after":  after_r["wall_ms"],
            "output_lines_before": before_r["output_lines"],
            "output_lines_after":  after_r["output_lines"],
        }
    return results


# ── Population B: fold-introduced findings lookup ─────────────────────────────

def plan_slug_from_path(rel_path: str) -> str:
    """Extract the plan slug from drafts/<plan>.md."""
    name = Path(rel_path).stem
    # Remove executable-/diagnostic- prefix for slug matching
    for pfx in ("executable-", "diagnostic-"):
        if name.startswith(pfx):
            return name[len(pfx):]
    return name


def load_fold_introduced_from_registers(pop_b: list) -> dict:
    """For each Population B plan, find fold-introduced findings in its walk register.

    Returns: {rel_path: {"register": path, "fold_introduced_count": int,
                          "total_findings": int}}
    """
    if not GOVERNANCE.exists():
        return {}

    result = {}
    for rel_path, shas in pop_b:
        slug = plan_slug_from_path(rel_path)
        # Find matching register
        candidates = list(GOVERNANCE.glob(f"walk-register-{slug}*.md"))
        if not candidates:
            # Also try full stem name without prefix
            name_stem = Path(rel_path).stem
            candidates = list(GOVERNANCE.glob(f"walk-register-*{name_stem}*.md"))
        if not candidates:
            result[rel_path] = {
                "register": None, "fold_introduced_count": 0, "total_findings": 0}
            continue

        reg_path = candidates[0]
        text = reg_path.read_text(encoding="utf-8")

        # Count fold-introduced findings
        fold_count = len(FOLD_INTRODUCED_RE.findall(text))
        # Count total finding rows (approximate: pipe-delimited lines with content)
        table_rows = [l for l in text.splitlines()
                      if l.startswith("|") and not re.match(r"^\|[-: |]+\|$", l.strip())]
        # Subtract header rows (one per table)
        header_count = sum(1 for l in text.splitlines()
                           if l.startswith("|") and re.search(r"\|\s*id\s*\|", l, re.IGNORECASE))
        finding_rows = max(0, len(table_rows) - header_count)

        result[rel_path] = {
            "register": str(reg_path),
            "fold_introduced_count": fold_count,
            "total_findings": finding_rows,
        }
    return result


# ── Q1 derivation ─────────────────────────────────────────────────────────────

def derive_q1() -> dict:
    """Enumerate fold_check's reader set mechanically vs the six battery tools."""
    # Mechanically: grep for readers.append in fold_check.py
    fc_path = SCRIPTS / "fold_check.py"
    fc_text = fc_path.read_text(encoding="utf-8")
    reader_appends = re.findall(r'readers\.append\(\("([^"]+)"', fc_text)

    # What readers_for() returns for a plan file (non walk-register)
    # (we derive mechanically from source, not by calling readers_for with a file
    # that must exist on disk)
    all_tools = BATTERY_TOOLS_CANONICAL[:]
    tools_in_fold_check = reader_appends  # exact set from source
    tools_for_plan_file = [t for t in reader_appends
                           if "walk_register" not in t]  # branch taken for plan files

    # Delta: tools in battery but NOT in fold_check's plan-file reader set
    delta = [t for t in all_tools if t not in tools_for_plan_file]
    return {
        "reader_appends_all": reader_appends,
        "tools_for_plan_file": tools_for_plan_file,
        "battery_tools": all_tools,
        "delta_not_in_fold_check": delta,
    }


# ── fold_check's count vocabulary ─────────────────────────────────────────────

def derive_fold_check_count_form() -> dict:
    """Derive fold_check's own count output form from its source (not inherited prose)."""
    fc_path = SCRIPTS / "fold_check.py"
    fc_text = fc_path.read_text(encoding="utf-8")
    # Find print statements in main() that contain numeric fields
    prints = re.findall(r'print\(f"([^"]*\{[^}]*\}[^"]*)"\)', fc_text)
    count_prints = [p for p in prints if re.search(r"\{[^}]*len|signals|readers", p)]
    return {"count_form_patterns": count_prints}


# ── timing sample ─────────────────────────────────────────────────────────────

def measure_timing_sample(pop_a: list, tmpdir: Path, n_sample: int = 20) -> dict:
    """Measure wall-time for C0, C1, C2 over a sample of fold pairs.

    C0 = plan_lint only (as fold_check does today)
    C1 = plan_lint + propagation_check + cycle_check
    C2 = C1 + count-field extraction (negligible overhead — pure Python regex)
    """
    sample = pop_a[:n_sample]
    c0_ms, c1_ms, c2_ms = [], [], []

    for rel_path, shas in sample:
        if len(shas) < 2:
            continue
        sha_b, sha_a = shas[1], shas[0]  # oldest first (shas[0] = most recent)
        bp = extract_revision(sha_b, rel_path, tmpdir / "timing_before")
        ap = extract_revision(sha_a, rel_path, tmpdir / "timing_after")
        if bp is None or ap is None:
            continue

        # C0: plan_lint only
        t0 = time.perf_counter()
        run_tool("plan_lint", bp)
        run_tool("plan_lint", ap)
        c0_ms.append((time.perf_counter() - t0) * 1000)

        # C1: all three tools
        t1 = time.perf_counter()
        for tn in PLAN_TOOLS:
            run_tool(tn, bp)
            run_tool(tn, ap)
        c1_ms.append((time.perf_counter() - t1) * 1000)

        # C2 adds only Python-level count extraction — measure overhead
        t2 = time.perf_counter()
        for tn in PLAN_TOOLS:
            r = run_tool(tn, bp)
            if not r["crashed"]:
                extract_count_fingerprint(tn, r.get("full_output", ""))
            r = run_tool(tn, ap)
            if not r["crashed"]:
                extract_count_fingerprint(tn, r.get("full_output", ""))
        c2_ms.append((time.perf_counter() - t2) * 1000)

    def _stats(vals):
        if not vals:
            return {"n": 0, "mean_ms": None, "min_ms": None, "max_ms": None}
        return {"n": len(vals), "mean_ms": round(sum(vals)/len(vals), 1),
                "min_ms": round(min(vals), 1), "max_ms": round(max(vals), 1)}

    return {"C0": _stats(c0_ms), "C1": _stats(c1_ms), "C2": _stats(c2_ms)}


# ── main census ───────────────────────────────────────────────────────────────

def run_census(pop_a: list, pop_b: list, tmpdir: Path, max_pairs: int | None = None) -> dict:
    """Run the full census over Population A."""
    fold_pairs = []
    for rel_path, shas in pop_a:
        # shas[0] is most recent, shas[-1] is oldest
        # Fold pairs: (shas[i+1], shas[i]) = (older, newer)
        for i in range(len(shas) - 1):
            fold_pairs.append((shas[i + 1], shas[i], rel_path))

    if max_pairs is not None:
        fold_pairs = fold_pairs[:max_pairs]

    total_pairs = len(fold_pairs)
    results = []

    print(f"Running census: {total_pairs} fold pairs × {len(PLAN_TOOLS)} tools",
          file=sys.stderr)

    for idx, (sha_b, sha_a, rel_path) in enumerate(fold_pairs):
        if idx % 50 == 0 and idx > 0:
            print(f"  {idx}/{total_pairs}...", file=sys.stderr)
        try:
            pair_results = analyze_fold_pair(sha_b, sha_a, rel_path, tmpdir)
        except Exception as e:
            pair_results = {t: {"usable": False, "crashed_before": True,
                                "crash_reason_before": str(e)} for t in PLAN_TOOLS}
        results.append({
            "sha_before": sha_b,
            "sha_after": sha_a,
            "rel_path": rel_path,
            "tools": pair_results,
        })

    return {"fold_pairs": results, "total_pairs": total_pairs}


# ── aggregate statistics ──────────────────────────────────────────────────────

def aggregate(census: dict, pop_a: list, pop_b: list,
              fold_introduced: dict, q1: dict, timing: dict) -> dict:
    """Compute Q1–Q7 from the raw census results."""
    pairs = census["fold_pairs"]
    total = census["total_pairs"]
    pop_a_size = len(pop_a)
    pop_b_size = len(pop_b)
    total_fold_pairs_a = sum(len(shas) - 1 for _, shas in pop_a)

    # ── per-tool aggregates ──
    tool_stats = {}
    for tool_name in PLAN_TOOLS:
        usable = [p for p in pairs if p["tools"].get(tool_name, {}).get("usable")]
        crashed_b = sum(1 for p in pairs if p["tools"].get(tool_name, {}).get("crashed_before"))
        crashed_a = sum(1 for p in pairs if p["tools"].get(tool_name, {}).get("crashed_after"))

        n_usable = len(usable)
        signal_changed    = sum(1 for p in usable if p["tools"][tool_name]["signal_changed"])
        count_changed     = sum(1 for p in usable if p["tools"][tool_name]["count_changed"])
        suppressed_linere   = sum(1 for p in usable if p["tools"][tool_name]["suppressed_by_linere"])
        suppressed_countsre = sum(1 for p in usable if p["tools"][tool_name]["suppressed_by_countsre"])
        suppressed_digitre  = sum(1 for p in usable if p["tools"][tool_name]["suppressed_by_digitre"])

        wall_all = ([p["tools"][tool_name]["wall_ms_before"] for p in usable] +
                    [p["tools"][tool_name]["wall_ms_after"]  for p in usable])
        out_all  = ([p["tools"][tool_name]["output_lines_before"] for p in usable] +
                    [p["tools"][tool_name]["output_lines_after"]  for p in usable])

        tool_stats[tool_name] = {
            "usable_pairs": n_usable,
            "crashed_before": crashed_b,
            "crashed_after": crashed_a,
            "signal_changed": signal_changed,
            "signal_changed_rate": round(signal_changed / n_usable, 4) if n_usable else None,
            "count_changed": count_changed,
            "count_changed_rate": round(count_changed / n_usable, 4) if n_usable else None,
            "suppressed_by_linere": suppressed_linere,
            "suppressed_by_countsre": suppressed_countsre,
            "suppressed_by_digitre": suppressed_digitre,
            "wall_ms_mean": round(sum(wall_all) / len(wall_all), 1) if wall_all else None,
            "output_lines_mean": round(sum(out_all) / len(out_all), 1) if out_all else None,
        }

    # ── combined (any-tool) aggregates ──
    usable_any = [p for p in pairs
                  if any(p["tools"].get(t, {}).get("usable") for t in PLAN_TOOLS)]
    n_any = len(usable_any)

    # Q2: folds with signal change vs count-only change (any tool)
    any_signal_changed = sum(1 for p in usable_any
        if any(p["tools"].get(t, {}).get("signal_changed") for t in PLAN_TOOLS))
    any_count_changed  = sum(1 for p in usable_any
        if any(p["tools"].get(t, {}).get("count_changed") for t in PLAN_TOOLS))
    count_only = sum(1 for p in usable_any
        if (any(p["tools"].get(t, {}).get("count_changed") for t in PLAN_TOOLS)
            and not any(p["tools"].get(t, {}).get("signal_changed") for t in PLAN_TOOLS)))
    neither = sum(1 for p in usable_any
        if (not any(p["tools"].get(t, {}).get("signal_changed") for t in PLAN_TOOLS)
            and not any(p["tools"].get(t, {}).get("count_changed") for t in PLAN_TOOLS)))

    # Q7: output volume per design under C0/C1/C2
    # C0 = plan_lint only
    c0_lines = [p["tools"]["plan_lint"]["output_lines_before"] for p in usable_any
                if p["tools"].get("plan_lint", {}).get("usable")]
    c0_lines += [p["tools"]["plan_lint"]["output_lines_after"] for p in usable_any
                 if p["tools"].get("plan_lint", {}).get("usable")]
    # C1 = all three tools
    c1_lines = [
        sum(p["tools"].get(t, {}).get("output_lines_before", 0) for t in PLAN_TOOLS)
        for p in usable_any
    ] + [
        sum(p["tools"].get(t, {}).get("output_lines_after", 0) for t in PLAN_TOOLS)
        for p in usable_any
    ]
    # C2 adds only Python-level overhead (no extra output lines)
    c2_lines = c1_lines  # same output volume as C1

    def _safe_mean(lst):
        return round(sum(lst) / len(lst), 1) if lst else None

    # Population B fold-introduced summary
    pop_b_summary = {}
    for rel_path, shas in pop_b:
        fi = fold_introduced.get(rel_path, {})
        pop_b_summary[Path(rel_path).name] = {
            "commits": len(shas),
            "fold_pairs": len(shas) - 1,
            "register_found": fi.get("register") is not None,
            "fold_introduced_count": fi.get("fold_introduced_count", 0),
            "total_findings": fi.get("total_findings", 0),
        }

    return {
        "populations": {
            "A": {"plan_files": pop_a_size, "fold_pairs": total_fold_pairs_a,
                  "pairs_run": total},
            "B": {"plan_files": pop_b_size,
                  "min_commits_threshold": 5,
                  "summary": pop_b_summary},
        },
        "q1_reader_delta": q1,
        "q2_normalization": {
            "total_usable_pairs": n_any,
            "signal_changed": any_signal_changed,
            "count_changed_in_full_output": any_count_changed,
            "count_only_not_in_signals": count_only,
            "neither_changed": neither,
            "rates": {
                "signal_change_rate": round(any_signal_changed / n_any, 4) if n_any else None,
                "count_change_rate":  round(any_count_changed / n_any, 4) if n_any else None,
                "count_only_rate":    round(count_only / n_any, 4) if n_any else None,
            },
        },
        "q5_per_tool": tool_stats,
        "q6_timing": timing,
        "q7_output_volume": {
            "C0_plan_lint_only_lines_mean": _safe_mean(c0_lines),
            "C1_all_tools_lines_mean": _safe_mean(c1_lines),
            "C2_with_count_delta_lines_mean": _safe_mean(c2_lines),
            "note": "C2 adds no output lines; count delta is an internal flag, not additional output",
        },
        "fold_check_count_form": derive_fold_check_count_form(),
        "extraction_choice": (
            "Historical revisions extracted to tmpdir at same relative path. "
            "(o1) signals excluded from both sides of every fold pair: "
            "check (o1) tests file existence on disk, so historical revisions "
            "referencing not-yet-created files produce WARNs that are extraction "
            "artifacts, not fold-induced changes."
        ),
        "mutation_check_status": (
            "Excluded from census: 3589ms/run (P5), applicable only to plans declaring "
            "mutants. Diagnostic constraint: report for completeness, not in any candidate design."
        ),
    }


# ── entry point ───────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="fold_signal_census — Q1–Q7 measurement instrument")
    ap.add_argument("--json", action="store_true", help="Emit full JSON result")
    ap.add_argument("--max-pairs", type=int, default=None,
                    help="Limit fold pairs (for fast iteration)")
    args = ap.parse_args()

    print("=== fold_signal_census: building populations from git history...", file=sys.stderr)
    pop_a, pop_b = build_populations(min_commits_b=5)
    print(f"  Population A: {len(pop_a)} plan files, "
          f"{sum(len(s)-1 for _,s in pop_a)} fold pairs", file=sys.stderr)
    print(f"  Population B: {len(pop_b)} plan files", file=sys.stderr)

    q1 = derive_q1()
    print(f"\n=== Q1: fold_check reader set:", file=sys.stderr)
    print(f"  readers.append calls: {q1['reader_appends_all']}", file=sys.stderr)
    print(f"  for plan files:       {q1['tools_for_plan_file']}", file=sys.stderr)
    print(f"  delta (not in fold_check): {q1['delta_not_in_fold_check']}", file=sys.stderr)

    fold_introduced = load_fold_introduced_from_registers(pop_b)

    with tempfile.TemporaryDirectory(prefix="fold_census_") as tmpdir_str:
        tmpdir = Path(tmpdir_str)

        print("\n=== Measuring timing sample (first 20 fold pairs)...", file=sys.stderr)
        timing = measure_timing_sample(pop_a, tmpdir, n_sample=20)
        print(f"  C0 (plan_lint only): {timing['C0']['mean_ms']}ms/fold-check mean", file=sys.stderr)
        print(f"  C1 (all 3 tools):    {timing['C1']['mean_ms']}ms/fold-check mean", file=sys.stderr)
        print(f"  C2 (C1+count delta): {timing['C2']['mean_ms']}ms/fold-check mean", file=sys.stderr)

        print("\n=== Running full census...", file=sys.stderr)
        census = run_census(pop_a, pop_b, tmpdir, max_pairs=args.max_pairs)

        result = aggregate(census, pop_a, pop_b, fold_introduced, q1, timing)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        _print_report(result, pop_a, pop_b)


def _print_report(result: dict, pop_a: list, pop_b: list):
    """Print a human-readable report answering Q1–Q7."""
    r = result
    pops = r["populations"]
    q2 = r["q2_normalization"]
    q5 = r["q5_per_tool"]
    q6 = r["q6_timing"]
    q7 = r["q7_output_volume"]
    q1 = r["q1_reader_delta"]

    print("=" * 72)
    print("fold_signal_census — Q1–Q7 results")
    print("=" * 72)
    print()

    print("POPULATIONS")
    print(f"  A (commit-level):  {pops['A']['plan_files']} plan files, "
          f"{pops['A']['fold_pairs']} fold pairs (run: {pops['A']['pairs_run']})")
    print(f"  B (walk-linked):   {pops['B']['plan_files']} plan files (>=5 commits)")
    print()

    print("EXTRACTION CHOICE")
    print(f"  {r['extraction_choice']}")
    print()

    print("Q1 — fold_check reader set vs battery")
    print(f"  readers.append occurrences: {q1['reader_appends_all']}")
    print(f"  For plan files:             {q1['tools_for_plan_file']}")
    print(f"  Six battery tools:          {q1['battery_tools']}")
    print(f"  DELTA (not in fold_check):  {q1['delta_not_in_fold_check']}")
    print()

    print("Q2 — normalization impact (over Population A)")
    n = q2["total_usable_pairs"]
    print(f"  Usable fold pairs: {n}")
    print(f"  Signal changed (C0 catches):            {q2['signal_changed']:4d}  ({q2['rates']['signal_change_rate']:.1%})")
    print(f"  Count changed in full output:           {q2['count_changed_in_full_output']:4d}  ({q2['rates']['count_change_rate']:.1%})")
    print(f"  Count-only change (signal UNCHANGED):   {q2['count_only_not_in_signals']:4d}  ({q2['rates']['count_only_rate']:.1%})")
    print(f"  Neither changed:                        {q2['neither_changed']:4d}")
    print()

    print("Q5 — per-tool signal and count-delta rates")
    print(f"  {'Tool':<22} {'Usable':>7} {'SigChg':>7} {'SigRate':>8} {'CntChg':>7} {'CntRate':>8} "
          f"{'CrashB':>7} {'CrashA':>7} {'SuppLinere':>11} {'SuppDigitre':>12}")
    for tn, ts in q5.items():
        n_u = ts["usable_pairs"]
        sr = f"{ts['signal_changed_rate']:.1%}" if ts['signal_changed_rate'] is not None else "n/a"
        cr = f"{ts['count_changed_rate']:.1%}" if ts['count_changed_rate'] is not None else "n/a"
        print(f"  {tn:<22} {n_u:>7} {ts['signal_changed']:>7} {sr:>8} {ts['count_changed']:>7} {cr:>8} "
              f"{ts['crashed_before']:>7} {ts['crashed_after']:>7} "
              f"{ts['suppressed_by_linere']:>11} {ts['suppressed_by_digitre']:>12}")
    print()

    print("Q6 — timing cost (sample of <=20 fold pairs)")
    for design, dts in q6.items():
        if dts["n"] == 0:
            print(f"  {design}: no data")
        else:
            print(f"  {design}: n={dts['n']} mean={dts['mean_ms']}ms  "
                  f"[{dts['min_ms']}–{dts['max_ms']}ms]")
    # Extrapolate to cycle cost
    if q6.get("C0") and q6["C0"]["n"]:
        print()
        print("  Cycle cost extrapolation (walks × lenses = 9 × 5 = 45 invocations):")
        for design, dts in q6.items():
            if dts["n"] > 0:
                cycle_s = dts["mean_ms"] * 45 / 1000
                print(f"    {design}: ~{cycle_s:.0f}s/cycle at mean cost")
    print()

    print("Q7 — output volume (mean non-empty lines per revision)")
    print(f"  C0 (plan_lint only):   {q7['C0_plan_lint_only_lines_mean']} lines/revision")
    print(f"  C1 (all 3 tools):      {q7['C1_all_tools_lines_mean']} lines/revision")
    print(f"  C2 (C1 + count delta): {q7['C2_with_count_delta_lines_mean']} lines/revision")
    print(f"  Note: {q7['note']}")
    print()

    print("Q3 — Population B fold-introduced cross-reference")
    print(f"  (counts-only changes vs real fold defects over Population B)")
    total_fi = sum(v["fold_introduced_count"] for v in r["populations"]["B"]["summary"].values())
    total_fr = sum(v["total_findings"] for v in r["populations"]["B"]["summary"].values())
    registered = sum(1 for v in r["populations"]["B"]["summary"].values() if v["register_found"])
    print(f"  Registers found for {registered}/{pops['B']['plan_files']} Population B plans")
    print(f"  Total findings: {total_fr}  Fold-introduced: {total_fi}")
    print()
    print("  Plan-by-plan (Population B):")
    for name, v in r["populations"]["B"]["summary"].items():
        reg_str = "register found" if v["register_found"] else "NO REGISTER"
        print(f"    {name:<55} commits={v['commits']:3d} "
              f"fi={v['fold_introduced_count']:3d}/{v['total_findings']:3d}  {reg_str}")
    print()

    print("Q4 — false-positive rate (unanswerable note)")
    print("  Q4 requires knowing which fold pairs produced fold-introduced findings.")
    print("  Cross-referencing commit SHAs with walk-register origin fields requires")
    print("  parsing walk numbers from commit messages — an approximation that is not")
    print("  implemented in this census.  See Q3 above for the total fold-introduced")
    print("  count across Population B.  Q4 is partially unanswerable on this corpus:")
    print("  the registers record fold-introduced findings but not the exact commit")
    print("  boundary at which the fold occurred.")
    print()

    print("COUNT VOCABULARY (per tool, from actual output)")
    print("  plan_lint:          candidates=N  excluded=N  fired=N  (INFO lines, not signals)")
    print("                      line=N in WARN messages = POSITION, excluded from count channel")
    print("  propagation_check:  DIVERGENCES: N  (summary line, not a signal per is_signal())")
    print("                      L\\d+: in findings = POSITION (line refs), excluded")
    print("  cycle_check:        no count fields  (emits only CONTINUE/BAR_MET/ESCALATE:*)")
    print()

    print("FOLD_CHECK COUNT FORM (derived from source, not prose)")
    for p in r["fold_check_count_form"]["count_form_patterns"]:
        print(f"  {p}")
    print()

    print("MUTATION_CHECK STATUS")
    print(f"  {r['mutation_check_status']}")
    print()

    print("CONFOUND (applies to Q2–Q5)")
    print("  Instrument runs TODAY's checkers over HISTORICAL plan revisions.")
    print("  plan_lint checks (u),(v) and the 100033 gate post-date most of the corpus.")
    print("  Numbers show what TODAY's battery would have said, not what the author saw.")
    print("  Comparisons remain controlled: the same tool version runs on both sides")
    print("  of every fold, so a delta is attributable to the fold, not to tool drift.")
    print()

    print("=" * 72)


if __name__ == "__main__":
    main()
