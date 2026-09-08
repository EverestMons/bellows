"""substrate_check — is the drafting-cycle SUBSTRATE present for a plan? (thread 183)

DRAFTING_CYCLE §2, auto-advance clause: "The substrate-presence precondition is HARD
and gates BOTH auto-advance AND auto-close ... a substrate-less BAR_MET is
indistinguishable from a fabricated close (cycle_check treats an N/A assert
identically to PASS), so without the substrate the close is MANUAL and
CEO-confirmed, never auto." Substrate = "a committed `**Walk register:**` reference
line pointing to a walk-register file that walk_register_lint validates, a per-walk
commit per walk, and a fold_check baseline."

⛔ Measured 2026-09-07: NOTHING mechanized this. The daemon's only auto-close input
was the plan header's own auto_close field, so a plan declaring no register reached
BAR_MET on N/A asserts and, with auto_close: true, closed itself on its own say-so.
Blast radius at the edit: of 193 T1/T2 plans in Done/, ZERO carry auto_close: true
— the hole was real and unexercised; this guards the first plan that would.

Lives in its own module because cycle_check cannot import lens_order_check (which
imports cycle_check) without a cycle. ONE resolver: register resolution reuses
cycle_check._resolve_register_ref; the commit record reuses lens_order_check's.

Returns (present, detail):
  None  — N/A: the plan declares no T1/T2 tier, so no substrate is owed (T0, pre-cycle)
  True  — all three legs present
  False — at least one leg absent; detail names which
"""
import subprocess
from pathlib import Path

import cycle_check
import lens_order_check
import walk_register_lint
import fold_check


def _committed_and_clean(path):
    repo = lens_order_check._repo_of(path)
    if not repo:
        return False, "register is not inside a git repo"
    rel = str(Path(path).resolve().relative_to(repo))
    tracked = subprocess.run(["git", "-C", str(repo), "ls-files", "--error-unmatch", rel],
                             capture_output=True, text=True)
    if tracked.returncode != 0:
        return False, "register file is UNTRACKED — doctrine requires a COMMITTED register"
    dirty = subprocess.run(["git", "-C", str(repo), "status", "--porcelain", "--", rel],
                           capture_output=True, text=True).stdout.strip()
    if dirty:
        return False, "register has uncommitted changes"
    return True, ""


def substrate_status(plan_path):
    plan_path = Path(plan_path)
    try:
        text = plan_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return False, f"plan unreadable: {type(e).__name__}"
    tier = (lens_order_check.tier_of(text) or "").upper()
    if tier not in ("T1", "T2"):
        return None, f"N/A — cycle_tier {tier or 'undeclared'} owes no substrate"

    missing = []

    # Leg 1 — a committed register the lint validates
    blocks = cycle_check.extract_dc_blocks(text)
    ref = cycle_check.parse_block(blocks[0]).get("walk_register_ref") if len(blocks) == 1 else None
    reg = cycle_check._resolve_register_ref(ref, plan_path) if ref else None
    if not ref:
        missing.append("register: no `**Walk register:**` line")
    elif not reg:
        missing.append(f"register: `{ref}` does not resolve on this machine")
    else:
        ok, why = _committed_and_clean(reg)
        if not ok:
            missing.append(f"register: {why}")
        else:
            try:
                status = walk_register_lint.validate_file(Path(reg))[0]
            except Exception as e:
                status = f"lint raised {type(e).__name__}"
            if status != "CONFORMANT":
                missing.append(f"register: walk_register_lint says {status}")

    # Leg 2 — a per-walk commit for every declared lens walk (plan repo ∪ register repo)
    walks = {w for w in (lens_order_check.declared_walks(text) or set()) if w != 0}
    if not walks:
        missing.append("per-walk commits: the Cycle Log declares no lens walk")
    else:
        try:
            repo = lens_order_check._repo_of(plan_path)
            rows = lens_order_check.commit_record(plan_path, repo) if repo else []
            reg_rows, _ = lens_order_check.register_commit_record(text, plan_path)
            seen = {r[0] for r in rows} | {r[0] for r in reg_rows}
            unproven = sorted(walks - seen)
            if unproven:
                missing.append(f"per-walk commits: walks {unproven} have no commit naming a lens")
        except Exception as e:
            missing.append(f"per-walk commits: record unreadable ({type(e).__name__})")

    # Leg 3 — a fold_check baseline. The baseline is named after the DRAFT and lives
    # beside it, so a plan deposited into another repo cannot find it by position
    # (thread 185, the same class as 163). DRAFTING_CYCLE v2.28: the Cycle Manifest
    # may carry `fold_baseline:` — the baseline's path, resolved exactly like the
    # register ref through the ONE resolver — and walk 0 records it when it arms the
    # baseline. Beside-the-plan remains the fallback for a same-repo cycle.
    manifest = cycle_check.parse_manifest_stanza(text) or {}
    fb_ref = (manifest.get("fold_baseline") or "").strip()
    if fb_ref and fb_ref != "<declare>":
        fb = cycle_check._resolve_register_ref(fb_ref, plan_path)
        if not fb or not Path(fb).is_file():
            missing.append(f"baseline: manifest fold_baseline `{fb_ref}` does not resolve to a file")
    elif not fold_check.baseline_path(plan_path, None).exists():
        missing.append("baseline: no fold_check baseline beside the plan and no `fold_baseline:` "
                       "in the Cycle Manifest (a cross-repo deposit needs the field — thread 185)")

    if missing:
        return False, "; ".join(missing)
    return True, f"register committed + CONFORMANT, walks {sorted(walks)} proven, baseline present"


if __name__ == "__main__":
    import sys
    present, detail = substrate_status(sys.argv[1])
    print(f"SUBSTRATE {'N/A' if present is None else ('PRESENT' if present else 'ABSENT')}: {detail}")
    sys.exit(0 if present is not False else 1)
