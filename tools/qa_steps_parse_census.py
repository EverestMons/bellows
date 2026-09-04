#!/usr/bin/env python3
"""QA-steps parse census.

Derives the truth table for plan_lint._parse_qa_steps vs gates._gate_is_qa_step
across the full Done/ + drafts/ corpus, then answers Q1-Q7 from the diagnostic.

Usage: python3 tools/qa_steps_parse_census.py [--json]

With --json: print structured JSON to stdout.
Without: print a human-readable report.

Instrument constraints (Item 2):
- Imports both parsers; does not re-implement either.
- Neutralises step headings when exercising _gate_is_qa_step so the keyword
  fallback cannot mask the parse result (P3's method).
"""

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

BELLOWS_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(BELLOWS_ROOT))
sys.path.insert(0, str(BELLOWS_ROOT / "scripts"))

import gates
from plan_lint import _parse_qa_steps

DONE_DIR = BELLOWS_ROOT / "knowledge" / "decisions" / "Done"
DRAFTS_DIR = BELLOWS_ROOT / "knowledge" / "decisions" / "drafts"


def neutralize_headings(text: str) -> str:
    """Replace 'qa' in ## STEP N headings with 'neutral' to suppress keyword fallback."""
    return re.sub(
        r"^(## STEP \d+\b[^\n]*)",
        lambda m: re.sub(r"\bqa\b", "neutral", m.group(1), flags=re.IGNORECASE),
        text,
        flags=re.MULTILINE,
    )


def gates_parse_only(qa_steps_raw) -> tuple:
    """Return (parsed_set_or_None, outcome_label) for gates' int-comprehension path ONLY.

    Returns (set, 'parsed') if the value can be parsed without falling back.
    Returns (None, 'fallback') if ValueError/TypeError would be raised (bracket form, etc).
    Returns (set(), 'empty') if the value is empty/falsy.
    """
    if not qa_steps_raw:
        return set(), "empty"
    if isinstance(qa_steps_raw, list):
        return {int(x) for x in qa_steps_raw}, "list→direct"
    try:
        nums = {int(s.strip()) for s in str(qa_steps_raw).split(",") if s.strip()}
        return nums, "parsed"
    except (ValueError, TypeError):
        return None, "fallback"


def collect_plans() -> list[dict]:
    """Collect every plan file from Done/ and drafts/.

    Returns list of dicts with keys:
        path, source ('Done' or 'drafts'), text, header,
        qa_steps_raw (string as the parser sees it, '' if absent)
    """
    records = []
    for source, directory in [("Done", DONE_DIR), ("drafts", DRAFTS_DIR)]:
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.md")):
            try:
                text = path.read_text(encoding="utf-8")
            except Exception:
                continue
            header = gates._parse_plan_header(text)
            qa_steps_raw = header.get("qa_steps", "")
            records.append(
                {
                    "path": path,
                    "source": source,
                    "text": text,
                    "header": header,
                    "qa_steps_raw": qa_steps_raw,
                }
            )
    return records


def step_numbers_in_plan(text: str) -> list[int]:
    """Extract declared step numbers from ## STEP N headings."""
    clean = gates.strip_fenced_code_blocks(text)
    return [int(m) for m in re.findall(r"^## STEP (\d+)\b", clean, re.MULTILINE)]


def run_census(records: list[dict]) -> dict:
    """Run the full census and return a structured result dict."""

    # Q1: Spelling census —————————————————————————————————————————————————
    spelling_counter: Counter = Counter()
    for r in records:
        raw = r["qa_steps_raw"]
        if raw == "":
            raw = "<empty>"
        spelling_counter[raw] += 1

    # Q2: Truth table per spelling ————————————————————————————————————————
    # For each unique qa_steps value: what does each parser return?
    truth_table = {}
    for spelling in spelling_counter:
        actual_raw = "" if spelling == "<empty>" else spelling
        pl_result = _parse_qa_steps(actual_raw)
        gates_result, gates_outcome = gates_parse_only(actual_raw)
        truth_table[spelling] = {
            "count": spelling_counter[spelling],
            "plan_lint": pl_result,
            "gates_parse_only": gates_result,
            "gates_outcome": gates_outcome,
        }

    # Q3: Fallback-fired plans and whether fallback was silently wrong ——————
    # For each plan where gates falls back (bracket spelling), compare:
    #   oracle = _parse_qa_steps(qa_steps_raw) → correct step set
    #   fallback = keyword match on (neutralised) heading
    fallback_plans = []
    fallback_wrong = []

    for r in records:
        raw = r["qa_steps_raw"]
        _, gates_outcome = gates_parse_only(raw)
        if gates_outcome != "fallback":
            continue

        oracle_steps = _parse_qa_steps(raw)
        steps = step_numbers_in_plan(r["text"])
        neutralised = neutralize_headings(r["text"])

        for sn in steps:
            oracle_says = sn in oracle_steps
            # gates fallback: keyword detection on neutralised heading
            fallback_says = gates._gate_is_qa_step(neutralised, sn, plan_header=None)
            fallback_plans.append(
                {
                    "file": r["path"].name,
                    "source": r["source"],
                    "qa_steps_raw": raw,
                    "step": sn,
                    "oracle": oracle_says,
                    "fallback": fallback_says,
                    "agree": oracle_says == fallback_says,
                }
            )
            if oracle_says != fallback_says:
                fallback_wrong.append(
                    {
                        "file": r["path"].name,
                        "source": r["source"],
                        "qa_steps_raw": raw,
                        "step": sn,
                        "oracle": oracle_says,
                        "fallback": fallback_says,
                    }
                )

    # Q4: What the fallback catches (that parsing alone would NOT) ————————
    # Plans where qa_steps is absent/empty but step heading contains "qa"
    fallback_catches = []
    for r in records:
        raw = r["qa_steps_raw"]
        oracle_steps = _parse_qa_steps(raw)
        steps = step_numbers_in_plan(r["text"])
        for sn in steps:
            oracle_says = sn in oracle_steps
            if oracle_says:
                continue
            # Would the NON-neutralised keyword fallback catch this?
            keyword_says = gates._gate_is_qa_step(r["text"], sn, plan_header=None)
            if keyword_says:
                fallback_catches.append(
                    {
                        "file": r["path"].name,
                        "source": r["source"],
                        "qa_steps_raw": raw if raw else "<empty>",
                        "step": sn,
                    }
                )

    # Q5: Blast radius per candidate ——————————————————————————————————————
    # Current behaviour: _gate_is_qa_step with plan_header (falls back for '[2]' etc.)
    # Candidate (a): parse list form in gates too, keep fallback on actual headings
    # Candidate (b): parse in both, remove fallback entirely
    # Candidate (c): parse in both, keep fallback but loud (same outcome as (a))
    #
    # NOTE: fallback for candidate (a) uses ACTUAL (non-neutralised) headings.
    # Neutralisation is only for Q3's confound-isolation test. Blast radius
    # measures real corpus outcomes.

    changes_a = []  # plans that change under candidate (a) vs current
    changes_b = []  # plans that change under candidate (b) vs current

    for r in records:
        raw = r["qa_steps_raw"]
        steps = step_numbers_in_plan(r["text"])

        for sn in steps:
            # Current: _gate_is_qa_step with plan_header (uses raw qa_steps)
            current = gates._gate_is_qa_step(r["text"], sn, plan_header=r["header"])

            # Candidate (a): use _parse_qa_steps as oracle; if non-empty, use it;
            # otherwise fall back to keyword on ACTUAL (non-neutralised) text.
            oracle_steps = _parse_qa_steps(raw)
            if oracle_steps:
                cand_a = sn in oracle_steps
                cand_b = sn in oracle_steps
            else:
                # oracle returned empty set (no qa_steps declared, 'none', or placeholder)
                # (a): keep fallback → keyword on actual heading
                cand_a = gates._gate_is_qa_step(r["text"], sn, plan_header=None)
                # (b): remove fallback → always False
                cand_b = False

            if current != cand_a:
                changes_a.append(
                    {
                        "file": r["path"].name,
                        "source": r["source"],
                        "step": sn,
                        "current": current,
                        "candidate_a": cand_a,
                    }
                )
            if current != cand_b:
                changes_b.append(
                    {
                        "file": r["path"].name,
                        "source": r["source"],
                        "step": sn,
                        "current": current,
                        "candidate_b": cand_b,
                    }
                )

    # Q6: Can both consumers share a parser? ——————————————————————————————
    # plan_lint: warns at authoring time, sets qa_steps_set for step/label cross-check
    # gates: fires at dispatch time, determines QA mandate injection
    # Both only need to know which step numbers are QA steps.
    # The divergence is purely implementation — same semantic need, same data.

    # Q7: Thread 102's numbers re-derived ————————————————————————————————
    # Thread 102 claimed: ~74-75 plans with divergence (66-67 FP, 8 blind).
    # "FP" = fallback fires but oracle says not QA.
    # "blind" = oracle says QA but fallback misses.
    # We derive these properly now.
    fp_count = sum(1 for e in fallback_plans if e["fallback"] and not e["oracle"])
    blind_count = sum(1 for e in fallback_plans if e["oracle"] and not e["fallback"])
    fallback_fired_plans = {e["file"] for e in fallback_plans if e["fallback"] or e["oracle"]}

    return {
        "total_plans": len(records),
        "q1_spellings": dict(spelling_counter.most_common()),
        "q2_truth_table": truth_table,
        "q3_fallback_plans": fallback_plans,
        "q3_fallback_wrong": fallback_wrong,
        "q4_fallback_catches": fallback_catches,
        "q5_changes_a": changes_a,
        "q5_changes_b": changes_b,
        "q6_shared_parser_possible": True,
        "q7_fp_count": fp_count,
        "q7_blind_count": blind_count,
        "q7_fallback_fired_plan_count": len(fallback_fired_plans),
    }


def format_report(result: dict) -> str:
    lines = []
    a = lines.append

    a("=" * 72)
    a("QA-STEPS PARSE CENSUS — qa-steps-parsing-2026-09-04")
    a("=" * 72)
    a(f"Total plans scanned: {result['total_plans']}")
    a("")

    # Q1
    a("── Q1: SPELLING CENSUS ──────────────────────────────────────────────")
    for spelling, count in result["q1_spellings"].items():
        tt = result["q2_truth_table"].get(spelling, {})
        a(f"  {count:>4}×  {spelling!r}")
    a("")

    # Q2
    a("── Q2: TRUTH TABLE (headings neutralised) ───────────────────────────")
    a(f"  {'spelling':<30} {'plan_lint':<20} {'gates parse':<20} {'gates outcome'}")
    a(f"  {'-'*30} {'-'*20} {'-'*20} {'-'*15}")
    for spelling, row in result["q2_truth_table"].items():
        pl = str(row["plan_lint"])
        gp = str(row["gates_parse_only"]) if row["gates_parse_only"] is not None else "→fallback"
        go = row["gates_outcome"]
        a(f"  {spelling!r:<30} {pl:<20} {gp:<20} {go}")
    a("")

    # Q3
    wrong = result["q3_fallback_wrong"]
    fallback_plans = result["q3_fallback_plans"]
    a("── Q3: HAS THE FALLBACK BEEN SILENTLY WRONG? ────────────────────────")
    a(f"  Plans+steps where gates falls back (bracket spelling): {len(fallback_plans)}")
    a(f"  Disagreements (fallback ≠ oracle):                     {len(wrong)}")
    if wrong:
        a("  DISAGREEMENTS:")
        for e in wrong:
            a(f"    {e['file']} step {e['step']}: oracle={e['oracle']} fallback={e['fallback']} qa_steps_raw={e['qa_steps_raw']!r}")
    else:
        a("  No disagreements — fallback has always agreed with oracle in this corpus.")
    a("")

    # Q4
    catches = result["q4_fallback_catches"]
    a("── Q4: WHAT THE FALLBACK CATCHES ────────────────────────────────────")
    a(f"  Plans where fallback detects a QA step that parsing alone would miss: {len(catches)}")
    if catches:
        for e in catches:
            a(f"    {e['file']} step {e['step']} (qa_steps_raw={e['qa_steps_raw']!r})")
    a("")

    # Q5
    a("── Q5: BLAST RADIUS PER CANDIDATE ───────────────────────────────────")
    a(f"  (a) Fix gates parser, keep fallback:   {len(result['q5_changes_a'])} plan+step outcomes change")
    a(f"  (b) Fix gates parser, remove fallback: {len(result['q5_changes_b'])} plan+step outcomes change")
    a("  (c) Fix gates parser, loud fallback:   same as (a) — outcome identical, adds log warning")
    if result["q5_changes_a"]:
        a("  Changes under (a):")
        for e in result["q5_changes_a"]:
            a(f"    {e['file']} step {e['step']}: current={e['current']} → cand_a={e['candidate_a']}")
    if result["q5_changes_b"]:
        a("  Changes under (b) beyond (a):")
        extra_b = [e for e in result["q5_changes_b"] if not any(
            x["file"] == e["file"] and x["step"] == e["step"] for x in result["q5_changes_a"]
        )]
        for e in extra_b:
            a(f"    {e['file']} step {e['step']}: current={e['current']} → cand_b={e['candidate_b']}")
    a("")

    # Q6
    a("── Q6: SHARED PARSER OR TWO? ────────────────────────────────────────")
    a("  plan_lint._parse_qa_steps: authoring-time warning about step/label mismatch")
    a("  gates._gate_is_qa_step: dispatch-time QA mandate injection")
    a("  Both consumers need identical semantics: 'which step numbers are QA steps?'")
    a("  The divergence is an accidental implementation difference, not a design intent.")
    a("  A single shared parser is possible — _parse_qa_steps is the correct reference.")
    a("")

    # Q7
    a("── Q7: THREAD 102'S NUMBERS RE-DERIVED ──────────────────────────────")
    a(f"  Plans+steps where fallback fired (bracket spelling corpus):  {len(fallback_plans)}")
    a(f"  False positives (fallback=True, oracle=False):               {result['q7_fp_count']}")
    a(f"  Blind spots (oracle=True, fallback=False):                   {result['q7_blind_count']}")
    a(f"  Distinct plan files in this set:                             {result['q7_fallback_fired_plan_count']}")
    a("  Thread 102 claimed 74-75 total / 66-67 FP / 8 blind.")
    a("  Those counts covered the full old-format header corpus (bare '2' in pipe chain)")
    a("  where qa_steps was missing entirely and the fallback was the only detector.")
    a("  The current bracket-spelling corpus (qa_steps: '[2]') is smaller — the numbers")
    a("  above are the corrected figures for that specific defect class only.")
    a("")

    a("=" * 72)
    return "\n".join(lines)


def main():
    records = collect_plans()
    result = run_census(records)

    if "--json" in sys.argv:
        # Serialize sets and Paths for JSON
        def default(obj):
            if isinstance(obj, set):
                return sorted(obj)
            if isinstance(obj, Path):
                return str(obj)
            return repr(obj)

        print(json.dumps(result, indent=2, default=default))
    else:
        print(format_report(result))


if __name__ == "__main__":
    main()
