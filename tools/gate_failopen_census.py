#!/usr/bin/env python3
"""gate_failopen_census.py — enumerate every check by its module's identifier convention.

Derives inventory from CODE, not from docstrings (diagnostic contract: all four
known instances are cases where behaviour and description disagreed; a description
is a hypothesis to test, never evidence).

Per-module identifier conventions (DIFFER PER MODULE — not a shared pattern):
  plan_lint         (x) labels in results.append/print calls
  gates.py          _gate_* function names (def _gate_)
  depositor.py      _hold(path, "literal_reason") strings
  cycle_check.py    return "VERDICT" string literals
  wrap_check.py     [n/name] step tags in fails.append lines
  walk_register_lint STATUS_* constant definitions

Usage:
    python tools/gate_failopen_census.py
    python tools/gate_failopen_census.py --verbose
    python tools/gate_failopen_census.py --module gates      # single module
"""

import argparse
import re
import sys
from pathlib import Path

BELLOWS_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = BELLOWS_ROOT / "scripts"
HOOKS_DIR = BELLOWS_ROOT / "hooks" / "eluvian"


# ---------------------------------------------------------------------------
# Per-module extractors
# ---------------------------------------------------------------------------

def extract_plan_lint_checks(src: str) -> list[dict]:
    """Extract (x) check labels from results.append and print calls.

    plan_lint's emission form: results.append(("FAIL"/"PASS", "(x) label", ...))
    and print(f"(x) WARN: ...") / print(f"WARN: ...")
    Identifier convention: the parenthesized letter(s) in the label string.
    """
    checks = {}
    # results.append form: ("FAIL"/"PASS", "(x) ...")
    for m in re.finditer(r'results\.append\(\(["\'](FAIL|PASS)["\'],\s*["\'](\([a-z0-9]+\)[^"\']*)["\']', src):
        status, label = m.group(1), m.group(2)
        key_m = re.match(r'\(([a-z0-9]+)\)', label)
        if key_m:
            key = key_m.group(1)
            entry = checks.setdefault(key, {"key": key, "statuses": set(), "label": label.split("—")[0].strip()})
            entry["statuses"].add(status)
    # print form: "(x) WARN: ..." or "WARN: ..."
    for m in re.finditer(r'print\(f?["\'](\([a-z0-9]+\))\s+(WARN|INFO):', src):
        key_m = re.match(r'\(([a-z0-9]+)\)', m.group(1))
        if key_m:
            key = key_m.group(1)
            entry = checks.setdefault(key, {"key": key, "statuses": set(), "label": f"({key})"})
            entry["statuses"].add(m.group(2))
    # print bare WARN (no letter prefix)
    for m in re.finditer(r'print\(f?["\']WARN:', src):
        checks.setdefault("bare_warn", {"key": "bare_warn", "statuses": {"WARN"}, "label": "bare WARN (no check letter)"})

    result = []
    for key in sorted(checks):
        entry = checks[key]
        result.append({
            "module": "plan_lint",
            "identifier": f"({key})",
            "statuses": sorted(entry["statuses"]),
            "blocking": "FAIL" in entry["statuses"],
            "label": entry["label"],
        })
    return result


def extract_gates_checks(src: str) -> list[dict]:
    """Extract _gate_* function names.

    gates.py convention: def _gate_NAME(... failures) — appends to failures to FAIL.
    Informational gates: _gate_file_change_audit (returns list, never appends),
    _gate_is_qa_step (returns bool, determines if QA-gated checks fire).
    """
    checks = []
    for m in re.finditer(r'^def (_gate_\w+)\(', src, re.MULTILINE):
        name = m.group(1)
        # Classify informational vs blocking
        # Informational: file_change_audit (never appends to failures), is_qa_step (returns bool)
        informational = name in ("_gate_file_change_audit", "_gate_is_qa_step")
        # QA-conditional: fire only when is_qa_step is True
        qa_only = name in ("_gate_rule_20_self_check", "_gate_qa_test_result")
        checks.append({
            "module": "gates",
            "identifier": name,
            "blocking": not informational,
            "qa_only": qa_only,
            "informational": informational,
        })
    return checks


def extract_depositor_holds(src: str) -> list[dict]:
    """Extract _hold(path, "literal_reason") literal strings.

    depositor.py convention: self._hold(path, "reason_string", ...).
    Dynamic reasons (f-strings with variables) are noted separately.
    """
    checks = []
    seen = set()
    # Static string literals
    for m in re.finditer(r'self\._hold\(path,\s*["\']([^"\']+)["\']', src):
        reason = m.group(1)
        if reason not in seen:
            seen.add(reason)
            checks.append({
                "module": "depositor",
                "identifier": f'_hold:"{reason}"',
                "reason": reason,
                "blocking": True,  # all holds are blocking (plan cannot proceed)
                "dynamic": False,
            })
    # Dynamic f-string reasons (collision, cycle_check, plan_lint, class:)
    dynamic_patterns = [
        ("collision:writes∩writes", "collision with sibling/in-flight write"),
        ("collision:reads∩writes", "collision with sibling/in-flight read"),
        ("cycle_check:{verdict}", "cycle_check returned non-BAR_MET"),
        ("cycle_check:exception:{e}", "cycle_check raised exception"),
        ("plan_lint:{n}_real_FAIL", "plan_lint returned non-benign FAIL(s)"),
        ("plan_lint:exception:{e}", "plan_lint subprocess exception"),
        ("validation_mismatch:cycle_check", "manifest validation: cycle_check mismatch"),
        ("class:{assigned_class}", "shop-infra plan held for CEO release"),
    ]
    for reason, desc in dynamic_patterns:
        checks.append({
            "module": "depositor",
            "identifier": f'_hold:"{reason}"',
            "reason": reason,
            "blocking": True,
            "dynamic": True,
            "description": desc,
        })
    return checks


def extract_cycle_check_verdicts(src: str) -> list[dict]:
    """Extract return "VERDICT" string literals.

    cycle_check.py convention: return "ESCALATE:*" (exit 1), "BAR_MET" (exit 0),
    "CONTINUE" (exit 0). Duplicate return sites for same verdict are deduplicated.
    """
    checks = []
    seen = set()
    for m in re.finditer(r'return\s+["\']([A-Z_:a-z0-9-]+)["\'],\s*([01])', src):
        verdict, exit_code = m.group(1), m.group(2)
        if verdict not in seen:
            seen.add(verdict)
            checks.append({
                "module": "cycle_check",
                "identifier": verdict,
                "blocking": exit_code == "1",
                "exit_code": int(exit_code),
            })
    return sorted(checks, key=lambda c: (c["exit_code"], c["identifier"]))


def extract_wrap_check_steps(src: str) -> list[dict]:
    """Extract [n/name] step tags from fails.append lines.

    wrap_check.py convention: fails.append(f"[n/name] ...") — step tag in fails = blocking.
    print(...) with [n/name] = advisory (WARN, never blocking).
    Also: _check_receipts [2r/receipts] tags.
    """
    checks = []
    seen = set()
    # Blocking: fails.append lines
    for m in re.finditer(r'fails\.append\([^\)]*\[(\d+[a-z]?/\w+)\]', src):
        tag = m.group(1)
        if tag not in seen:
            seen.add(tag)
            checks.append({
                "module": "wrap_check",
                "identifier": f"[{tag}]",
                "blocking": True,
            })
    # Advisory: print lines (not fails.append)
    for m in re.finditer(r'print\([^\)]*\[([A-Z0-9]+/\w+)\]', src):
        tag = m.group(1)
        if tag not in seen:
            seen.add(tag)
            checks.append({
                "module": "wrap_check",
                "identifier": f"[{tag}]",
                "blocking": False,
                "advisory": True,
            })
    return sorted(checks, key=lambda c: c["identifier"])


def extract_walk_register_statuses(src: str) -> list[dict]:
    """Extract STATUS_* constant definitions.

    walk_register_lint.py convention: STATUS_NAME = "VALUE" at module scope.
    """
    checks = []
    for m in re.finditer(r'^(STATUS_\w+)\s*=\s*["\']([^"\']+)["\']', src, re.MULTILINE):
        const, value = m.group(1), m.group(2)
        # Blocking for the caller (cycle_check treats non-silent statuses as WARN)
        silent = const in ("STATUS_CONFORMANT", "STATUS_PRE_SCHEMA", "STATUS_LEGACY_SCHEMA")
        checks.append({
            "module": "walk_register_lint",
            "identifier": const,
            "value": value,
            "blocking": not silent,  # non-silent statuses surface as WARN in cycle_check
            "silent": silent,
        })
    return checks


# ---------------------------------------------------------------------------
# Main census runner
# ---------------------------------------------------------------------------

def run_census(verbose: bool = False, module_filter: str | None = None) -> int:
    modules = {
        "plan_lint": (SCRIPTS_DIR / "plan_lint.py", extract_plan_lint_checks),
        "gates": (BELLOWS_ROOT / "gates.py", extract_gates_checks),
        "depositor": (BELLOWS_ROOT / "depositor.py", extract_depositor_holds),
        "cycle_check": (SCRIPTS_DIR / "cycle_check.py", extract_cycle_check_verdicts),
        "wrap_check": (HOOKS_DIR / "wrap_check.py", extract_wrap_check_steps),
        "walk_register_lint": (SCRIPTS_DIR / "walk_register_lint.py", extract_walk_register_statuses),
    }

    if module_filter:
        modules = {k: v for k, v in modules.items() if k == module_filter}
        if not modules:
            print(f"ERROR: unknown module {module_filter!r}", file=sys.stderr)
            return 2

    all_checks = []
    errors = []

    for mod_name, (path, extractor) in modules.items():
        try:
            src = path.read_text(encoding="utf-8")
        except OSError as e:
            errors.append(f"  {mod_name}: {e}")
            continue
        checks = extractor(src)
        all_checks.extend(checks)
        if verbose:
            print(f"\n--- {mod_name} ({path.name}) ---")
            for c in checks:
                blocking = "[BLOCKING]" if c.get("blocking") else "[advisory]"
                print(f"  {blocking} {c['identifier']}")

    if not verbose:
        # Structured summary
        print("# Gate / Check Population Census")
        print(f"# Source: code extraction per module identifier convention")
        print(f"# Extracted: {len(all_checks)} check identifiers across {len(modules)} modules")
        print()

        blocking = [c for c in all_checks if c.get("blocking")]
        advisory = [c for c in all_checks if not c.get("blocking")]
        print(f"Blocking checks: {len(blocking)}")
        print(f"Advisory checks: {len(advisory)}")
        print(f"Total:           {len(all_checks)}")
        print()

        by_module = {}
        for c in all_checks:
            by_module.setdefault(c["module"], []).append(c)

        for mod_name in modules:
            checks = by_module.get(mod_name, [])
            b = sum(1 for c in checks if c.get("blocking"))
            a = len(checks) - b
            print(f"  {mod_name}: {len(checks)} total ({b} blocking, {a} advisory)")
            for c in checks:
                tag = "B" if c.get("blocking") else "a"
                suffix = ""
                if c.get("qa_only"):
                    suffix = " [QA-step only]"
                if c.get("informational"):
                    suffix = " [informational]"
                if c.get("dynamic"):
                    suffix = " [dynamic reason]"
                if c.get("silent"):
                    suffix = " [silent in cycle_check]"
                print(f"    [{tag}] {c['identifier']}{suffix}")

    if errors:
        print("\nERRORS (source files unreadable):")
        for e in errors:
            print(e)
        return 2

    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Enumerate all gate/check identifiers by module convention")
    ap.add_argument("--verbose", action="store_true", help="Show per-module detail")
    ap.add_argument("--module", default=None, help="Restrict to one module")
    args = ap.parse_args()
    return run_census(verbose=args.verbose, module_filter=args.module)


if __name__ == "__main__":
    sys.exit(main())
