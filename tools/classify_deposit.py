"""classify_deposit.py — print the depositor's class assignment for a plan."""
import argparse
import json
import os
import re
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "scripts"))
sys.path.insert(0, _ROOT)


def _find_unparsed_stanza_lines(plan_text):
    """Return stanza lines the manifest parser skips (non-blank, not field, not continuation)."""
    heading_re = re.compile(r"^## Cycle Manifest\s*$", re.MULTILINE)
    m = heading_re.search(plan_text)
    if not m:
        return []
    start = m.end()
    end_m = re.search(r"^(?:## |---)", plan_text[start:], re.MULTILINE)
    stanza = plan_text[start: start + end_m.start()] if end_m else plan_text[start:]

    skipped = []
    current_key = None
    for line in stanza.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if line.startswith("  ") and current_key:
            continue
        if re.match(r"^(\w[\w_]*):\s*(.*)", stripped):
            current_key = stripped.split(":")[0]
            continue
        skipped.append(line)
    return skipped


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="classify_deposit.py",
        description="Print the depositor's class assignment for a plan file.",
    )
    parser.add_argument("plan", help="Path to the plan file.")
    parser.add_argument(
        "--project-root",
        required=True,
        help="Project root passed to _assign_class (required; no default).",
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Path to config.json (default: bellows root config.json, {} if absent).",
    )
    args = parser.parse_args(argv)

    if not os.path.isfile(args.plan):
        parser.error(f"plan is not a file: {args.plan}")

    import bellows_root

    if args.config is None:
        default_cfg = bellows_root.resolve_bellows_root() / "config.json"
        if default_cfg.is_file():
            try:
                with open(default_cfg) as f:
                    config_data = json.load(f)
            except json.JSONDecodeError as exc:
                parser.error(f"default config is not valid JSON: {exc}")
            if not isinstance(config_data, dict):
                parser.error(f"default config is not a JSON object: {default_cfg}")
        else:
            config_data = {}
    else:
        if not os.path.isfile(args.config):
            parser.error(f"--config is not a file: {args.config}")
        try:
            with open(args.config) as f:
                config_data = json.load(f)
        except json.JSONDecodeError as exc:
            parser.error(f"--config is not valid JSON: {exc}")
        if not isinstance(config_data, dict):
            parser.error(f"--config is not a JSON object: {args.config}")

    with open(args.plan) as f:
        plan_text = f.read()

    import cycle_check
    import depositor as dep_mod

    dep = dep_mod.Depositor(
        disk_preflight_fn=lambda: True,
        shutting_down_check=lambda: False,
        config=config_data,
        lifecycle_db_path=os.devnull,
    )

    writes, reads, declared_class = dep._parse_plan(plan_text)

    manifest = cycle_check.parse_manifest_stanza(plan_text)
    manifest_present = bool(manifest)
    writes_from_manifest = manifest_present and bool(manifest.get("writes", "").strip())
    writes_from_fallback = not writes_from_manifest

    unparsed_lines = _find_unparsed_stanza_lines(plan_text)
    assigned_class = dep._assign_class(writes, args.project_root)

    print(f"plan: {args.plan}")
    if manifest_present:
        print(f"manifest: parsed ({len(manifest)} fields)")
    else:
        print("manifest: absent")

    source = "manifest" if writes_from_manifest else "fallback"
    print(f"writes ({len(writes)}) from {source}")
    for i, w in enumerate(writes, 1):
        print(f"  {i}. {w}")

    print(f"unparsed stanza lines ({len(unparsed_lines)})")
    for line in unparsed_lines:
        print(f"  {line}")

    print(f"reads ({len(reads)})")
    for r in reads:
        print(f"  {r}")

    if declared_class:
        print(f"declared class: {declared_class}")
    else:
        print("declared class: none")

    if assigned_class:
        print(f"assigned class: {assigned_class}")
    else:
        print("assigned class: none")

    if writes_from_fallback:
        print("RESULT: FALLBACK")
        return 3
    if unparsed_lines:
        print("RESULT: UNPARSED-STANZA")
        return 3
    if declared_class is None:
        print("RESULT: NO-DECLARED-CLASS")
        return 3
    if declared_class != assigned_class:
        print("RESULT: MISMATCH")
        return 1
    print("RESULT: MATCH")
    return 0


if __name__ == "__main__":
    sys.exit(main())
