"""In-bellows depositor — stages and clears ready-prefixed plans.

Safety invariant: the depositor never mints, never dispatches.
It stages (ready- to hold-) and clears (ready- to claimable) via atomic
os.rename; the daemon claims via its existing lifecycle path.
"""

import hashlib
import json
import logging
import os
import re
import sqlite3
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

from bellows_root import resolve_bellows_root

_SCRIPTS_DIR = str(resolve_bellows_root() / "scripts")
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

import cycle_check  # noqa: E402 — scripts/ must be on path first
import gates  # noqa: E402
import lifecycle  # noqa: E402
import status  # noqa: E402

log = logging.getLogger("bellows.depositor")

_READ_ONLY_PREFIXES = ("knowledge/research/", "scratch/")

_REGISTER_PATTERNS = (
    re.compile(r"knowledge/decisions/register-"),
    re.compile(r"(?:^|/)DRAFTING_CYCLE\.md$"),
)

_SHOP_INFRA_CODE_DIRS = ("bellows/", "forge/", "lessons-forge/", "anvil/")
_SHOP_INFRA_KNOWLEDGE_EXEMPTIONS = tuple(
    d + "knowledge/" for d in _SHOP_INFRA_CODE_DIRS
)

_BENIGN_LINT_CHECK_LETTERS = {"c", "d"}

_DEDUP_WINDOW = 5.0


class Depositor:
    """Evaluates ready-prefixed plans for auto-deposit or HOLD.

    Injected dependencies (W5 — no ``import bellows``):
        disk_preflight_fn:   callable(config) -> bool
        shutting_down_check: callable() -> bool
        config:              daemon config dict (watched_projects, …)
        lifecycle_db_path:   str path to lifecycle.db
    """

    def __init__(self, *, disk_preflight_fn, shutting_down_check, config,
                 lifecycle_db_path):
        self._disk_preflight = disk_preflight_fn
        self._shutting_down_check = shutting_down_check
        self.config = config
        self._db_path = lifecycle_db_path
        self._lock = threading.Lock()
        self._recent_evals: dict[str, float] = {}
        self._bellows_root = resolve_bellows_root()

    def _watched_dirs(self):
        return self.config.get("watched_projects", [])

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def evaluate(self, path):
        with self._lock:
            self._evaluate_locked(path)

    def reevaluate_on_startup(self):
        for d in self._watched_dirs():
            if not os.path.isdir(d):
                continue
            for fname in os.listdir(d):
                full = os.path.join(d, fname)
                if fname.startswith("ready-") and fname.endswith(".md"):
                    self.evaluate(full)
                elif fname.startswith("hold-") and fname.endswith(".md"):
                    self._reevaluate_hold(full)

    # ------------------------------------------------------------------
    # Locked evaluate
    # ------------------------------------------------------------------

    def _evaluate_locked(self, path):
        if self._shutting_down_check():
            return
        if not os.path.isfile(path):
            return
        filename = os.path.basename(path)
        if not filename.startswith("ready-") or not filename.endswith(".md"):
            return

        now = time.time()
        self._recent_evals = {
            p: t for p, t in self._recent_evals.items()
            if now - t < _DEDUP_WINDOW
        }
        if path in self._recent_evals:
            return
        self._recent_evals[path] = now

        try:
            plan_text = Path(path).read_text(encoding="utf-8")
        except Exception:
            self._hold(path, "unparseable", {"detail": "cannot read plan file"})
            return

        plan_dir = os.path.dirname(path)
        project_root = str(Path(plan_dir).parent.parent)

        try:
            self._do_evaluate(path, plan_text, plan_dir, project_root)
        except Exception as e:
            self._hold(path, f"exception:{type(e).__name__}", {"detail": str(e)})

    def _do_evaluate(self, path, plan_text, plan_dir, project_root):
        writes, reads, declared_class = self._parse_plan(plan_text)

        if not writes:
            self._hold(path, "empty_writes", {
                "detail": "undeclared intent — empty/undeterminable writes set",
            })
            return

        sibling_writes = self._scan_sibling_writes(path)
        if sibling_writes is None:
            self._hold(path, "unparseable_sibling", {
                "detail": "a sibling ready- file has unparseable writes",
            })
            return

        in_flight_writes = self._resolve_in_flight_writes()
        if in_flight_writes is None:
            self._hold(path, "unresolvable_in_flight", {
                "detail": "an in-flight plan file could not be resolved",
            })
            return

        all_other_writes = sibling_writes + in_flight_writes
        collision = self._check_collisions(writes, reads, all_other_writes,
                                           project_root)
        if collision:
            self._hold(path, collision["reason"], collision)
            return

        rerun = self._rerun_validation(path, plan_text)
        if rerun["hold"]:
            self._hold(path, rerun["reason"], rerun)
            return

        if not self._check_receipt(path):
            self._hold(path, "no_receipt", {})
            return

        assigned_class = self._assign_class(writes, project_root)
        if assigned_class is None:
            self._hold(path, "unassignable_class", {})
            return

        if declared_class and declared_class != assigned_class:
            self._hold(path, "class_mismatch", {
                "class_assigned": assigned_class,
                "class_declared": declared_class,
            })
            return

        if not self._disk_preflight(self.config):
            self._hold(path, "disk_low", {})
            return

        if assigned_class == "shop-infra":
            self._hold(path, f"class:{assigned_class}", {
                "class_assigned": assigned_class,
            })
        else:
            in_flight_2 = self._resolve_in_flight_writes()
            sibling_2 = self._scan_sibling_writes(path)
            if in_flight_2 is None or sibling_2 is None:
                self._hold(path, "pre_clear_recheck_failed", {})
                return
            collision_2 = self._check_collisions(
                writes, reads, sibling_2 + in_flight_2, project_root)
            if collision_2:
                self._hold(path, collision_2["reason"], collision_2)
                return
            self._clear(path, assigned_class)

    # ------------------------------------------------------------------
    # Hold re-evaluation (startup only — never auto-clears, A2)
    # ------------------------------------------------------------------

    def _reevaluate_hold(self, path):
        try:
            plan_text = Path(path).read_text(encoding="utf-8")
        except Exception:
            return

        plan_dir = os.path.dirname(path)
        project_root = str(Path(plan_dir).parent.parent)

        writes, reads, _ = self._parse_plan(plan_text)
        if not writes:
            self._update_hold_json(path, "empty_writes", {})
            return

        sibling_writes = self._scan_sibling_writes(path, include_hold=False)
        in_flight_writes = self._resolve_in_flight_writes()
        if sibling_writes is None or in_flight_writes is None:
            return

        collision = self._check_collisions(
            writes, reads, sibling_writes + in_flight_writes, project_root)
        if collision:
            self._update_hold_json(path, collision["reason"], collision)
        else:
            self._update_hold_json(path, "held_pending_ceo_release", {
                "detail": "collision cleared — awaiting CEO rename to ready-",
            })

    # ------------------------------------------------------------------
    # Plan parsing (Path A: manifest stanza; Path B: legacy Deposits/Scope)
    # ------------------------------------------------------------------

    def _parse_plan(self, plan_text):
        manifest = cycle_check.parse_manifest_stanza(plan_text)
        declared_class = None
        writes = []
        reads = []

        if manifest:
            raw_w = manifest.get("writes", "")
            if raw_w:
                writes = [w.strip() for w in raw_w.split(",") if w.strip()]
            raw_r = manifest.get("reads", "")
            if raw_r:
                reads = [r.strip() for r in raw_r.split(",") if r.strip()]
            c = manifest.get("class", "").strip()
            if c and c != "<declare>":
                declared_class = c

        if not writes:
            writes = gates._extract_plan_required_deposits(plan_text)
        if not reads:
            scope_files, scope_prefixes = gates._extract_plan_scope(plan_text)
            reads = scope_files + scope_prefixes

        return writes, reads, declared_class

    # ------------------------------------------------------------------
    # Class assignment
    # ------------------------------------------------------------------

    def _assign_class(self, writes, project_root=""):
        if not writes:
            return None

        project_name = os.path.basename(project_root.rstrip(os.sep))
        project_is_infra = (project_name + "/") in _SHOP_INFRA_CODE_DIRS

        all_read_only = True
        all_out_of_tree = True
        has_register = False
        has_shop_infra = False

        for p in writes:
            normalized = p.lstrip("/")

            if not normalized.startswith("~/") and not normalized.startswith("../"):
                all_out_of_tree = False

            if not any(normalized.startswith(pfx) or f"/{pfx}" in f"/{normalized}"
                       for pfx in _READ_ONLY_PREFIXES):
                if not any(seg + "/" in normalized or normalized.endswith(seg)
                           for seg in ("knowledge/research", "scratch")):
                    all_read_only = False

            for pat in _REGISTER_PATTERNS:
                if pat.search(normalized):
                    has_register = True

            for code_dir in _SHOP_INFRA_CODE_DIRS:
                if normalized.startswith(code_dir):
                    if not any(normalized.startswith(ex)
                              for ex in _SHOP_INFRA_KNOWLEDGE_EXEMPTIONS):
                        has_shop_infra = True

            if "/" not in normalized and not normalized.startswith("knowledge/"):
                has_shop_infra = True

            if project_is_infra and not normalized.startswith("knowledge/"):
                has_shop_infra = True

        if all_read_only:
            return "read-only"
        if has_shop_infra:
            return "shop-infra"
        if all_out_of_tree:
            return None
        if has_register:
            return "register-writing"
        return "app-feature"

    # ------------------------------------------------------------------
    # Collision detection
    # ------------------------------------------------------------------

    def _normalize_path(self, p, project_root):
        if os.path.isabs(p):
            return os.path.normpath(p)
        return os.path.normpath(os.path.join(project_root, p))

    def _paths_collide(self, a, b, root_a, root_b=None):
        if root_b is None:
            root_b = root_a
        na = self._normalize_path(a, root_a)
        nb = self._normalize_path(b, root_b)
        if na == nb:
            return True
        a_pfx = a.endswith("/")
        b_pfx = b.endswith("/")
        if a_pfx and not b_pfx:
            return nb.startswith(na + "/") or nb == na
        if b_pfx and not a_pfx:
            return na.startswith(nb + "/") or na == nb
        if a_pfx and b_pfx:
            return na.startswith(nb) or nb.startswith(na)
        return False

    def _check_collisions(self, writes, reads, other_write_sets, project_root):
        for other in other_write_sets:
            ow = other.get("writes", [])
            oroot = other.get("project_root", project_root)
            label = other.get("label", "unknown")

            for w in writes:
                for o in ow:
                    if self._paths_collide(w, o, project_root, oroot):
                        return {
                            "reason": f"collision:writes∩writes with {label}",
                            "collision_type": "writes∩writes",
                            "collision_path": w,
                            "collision_with": label,
                        }
            for r in reads:
                for o in ow:
                    if self._paths_collide(r, o, project_root, oroot):
                        return {
                            "reason": f"collision:reads∩writes with {label}",
                            "collision_type": "reads∩writes",
                            "collision_path": r,
                            "collision_with": label,
                        }
        return None

    # ------------------------------------------------------------------
    # Sibling scan — all watched dirs (A4)
    # ------------------------------------------------------------------

    def _scan_sibling_writes(self, current_path, include_hold=False):
        siblings = []
        for d in self._watched_dirs():
            if not os.path.isdir(d):
                continue
            project_root = str(Path(d).parent.parent)
            for fname in os.listdir(d):
                fpath = os.path.join(d, fname)
                if fpath == current_path:
                    continue
                if fname.startswith("ready-") and fname.endswith(".md"):
                    pass
                elif include_hold and fname.startswith("hold-") and fname.endswith(".md"):
                    pass
                else:
                    continue
                try:
                    text = Path(fpath).read_text(encoding="utf-8")
                except Exception:
                    return None
                w, _, _ = self._parse_plan(text)
                if w is None:
                    return None
                siblings.append({
                    "writes": w,
                    "project_root": project_root,
                    "label": f"sibling:{fname}",
                })
        return siblings

    # ------------------------------------------------------------------
    # In-flight writes resolution (DISC-1)
    # ------------------------------------------------------------------

    def _resolve_in_flight_writes(self):
        try:
            conn = sqlite3.connect(f"file:{self._db_path}?mode=ro", uri=True)
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT id, type, target_project, deposit_placeholder_name, plan_doc_ref "
                "FROM plans WHERE lifecycle_state IN ('in_progress', 'claimed', 'awaiting_verdict')"
            ).fetchall()
            conn.close()
        except Exception:
            return None

        results = []
        for row in rows:
            plan_id = row["id"]
            plan_type = row["type"]
            target_project = row["target_project"] or ""
            placeholder = row["deposit_placeholder_name"]
            doc_ref = row["plan_doc_ref"]

            in_progress_name = f"in-progress-{plan_type}-{plan_id}.md"
            plan_file = None
            for d in self._watched_dirs():
                candidate = os.path.join(d, in_progress_name)
                if os.path.isfile(candidate):
                    plan_file = candidate
                    break
            if not plan_file and placeholder:
                for d in self._watched_dirs():
                    candidate = os.path.join(d, placeholder)
                    if os.path.isfile(candidate):
                        plan_file = candidate
                        break
            if not plan_file and doc_ref and target_project:
                candidate = os.path.join(target_project, doc_ref)
                if os.path.isfile(candidate):
                    plan_file = candidate

            if not plan_file:
                return None

            try:
                text = Path(plan_file).read_text(encoding="utf-8")
            except Exception:
                return None

            w, _, _ = self._parse_plan(text)
            if not w:
                return None

            proj = target_project
            if not os.path.isabs(proj):
                proj = str(Path(os.path.dirname(plan_file)).parent.parent)

            results.append({
                "writes": w,
                "project_root": proj,
                "label": f"in-flight:#{plan_id}",
            })
        return results

    # ------------------------------------------------------------------
    # Validation re-run
    # ------------------------------------------------------------------

    def _rerun_validation(self, path, plan_text):
        result = {"hold": False, "reason": "",
                  "cycle_check": None, "plan_lint": None}

        try:
            verdict, _ = cycle_check.run_check(Path(path))
            result["cycle_check"] = verdict
            if verdict != "BAR_MET":
                result["hold"] = True
                result["reason"] = f"cycle_check:{verdict}"
                return result
        except Exception as e:
            result["hold"] = True
            result["reason"] = f"cycle_check:exception:{e}"
            return result

        lint_script = str(self._bellows_root / "scripts" / "plan_lint.py")
        try:
            lr = subprocess.run(
                [sys.executable, lint_script, str(path)],
                capture_output=True, text=True, timeout=60,
            )
            result["plan_lint"] = f"exit_{lr.returncode}"
            if lr.returncode != 0:
                fail_lines = [
                    ln for ln in lr.stdout.splitlines() if ln.startswith("FAIL:")
                ]
                non_benign = []
                for fl in fail_lines:
                    m = re.search(r"\(([a-z])\)", fl)
                    if m and m.group(1) in _BENIGN_LINT_CHECK_LETTERS:
                        continue
                    non_benign.append(fl)
                if non_benign:
                    result["hold"] = True
                    result["reason"] = f"plan_lint:{len(non_benign)}_real_FAIL"
                    return result
        except Exception as e:
            result["hold"] = True
            result["reason"] = f"plan_lint:exception:{e}"
            return result

        manifest = cycle_check.parse_manifest_stanza(plan_text)
        if manifest:
            val = manifest.get("validation", "")
            if "cycle_check=" in val:
                expected = val.split("cycle_check=")[1].split(",")[0].strip()
                if expected and expected != str(verdict):
                    result["hold"] = True
                    result["reason"] = (
                        f"validation_mismatch:cycle_check "
                        f"expected={expected} got={verdict}"
                    )
                    return result

        return result

    # ------------------------------------------------------------------
    # CLEAR and HOLD actions
    # ------------------------------------------------------------------

    def _check_receipt(self, path):
        """Fail-closed receipt check: True only if a matching active receipt exists."""
        filename = os.path.basename(path)
        slug = filename
        if slug.startswith("ready-"):
            slug = slug[len("ready-"):]
        if slug.endswith(".md"):
            slug = slug[:-len(".md")]

        plan_bytes = Path(path).read_bytes()
        content_hash = hashlib.sha256(plan_bytes).hexdigest()

        receipts_dir = self._bellows_root / "receipts"
        try:
            entries = os.listdir(receipts_dir)
        except OSError:
            # Fail-closed: unreadable/missing receipts directory → no match
            return False

        for entry in entries:
            if not entry.endswith(".json"):
                continue
            entry_path = os.path.join(str(receipts_dir), entry)
            if os.path.isdir(entry_path):
                continue
            try:
                with open(entry_path) as f:
                    data = json.load(f)
            except (json.JSONDecodeError, OSError):
                continue
            if data.get("slug") == slug and data.get("content_hash") == content_hash:
                return True

        return False

    def _clear(self, path, assigned_class):
        directory = os.path.dirname(path)
        filename = os.path.basename(path)
        claimable_name = filename[len("ready-"):]
        claimable_path = os.path.join(directory, claimable_name)

        if not os.path.isfile(path):
            return

        plan_bytes = Path(path).read_bytes()
        content_hash = hashlib.sha256(plan_bytes).hexdigest()
        lifecycle.write_clearance(
            claimable_name, content_hash, assigned_class, "depositor",
            self._db_path,
        )

        os.rename(path, claimable_path)

        hold_json_name = "hold-" + claimable_name.replace(".md", ".hold.json")
        hold_json_path = os.path.join(directory, hold_json_name)
        if os.path.isfile(hold_json_path):
            try:
                os.remove(hold_json_path)
            except OSError:
                pass

    def _hold(self, path, reason, details=None):
        if not os.path.isfile(path):
            return

        directory = os.path.dirname(path)
        filename = os.path.basename(path)

        if filename.startswith("ready-"):
            hold_name = "hold-" + filename[len("ready-"):]
            hold_path = os.path.join(directory, hold_name)
            os.rename(path, hold_path)
        elif filename.startswith("hold-"):
            hold_path = path
        else:
            return

        hold_json_path = hold_path.replace(".md", ".hold.json")
        try:
            data = {"hold_reason": reason, "held_at": datetime.now().isoformat()}
            if details:
                data.update({k: v for k, v in details.items() if k != "reason"})
            with open(hold_json_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def _update_hold_json(self, path, reason, details=None):
        hold_json_path = path.replace(".md", ".hold.json")
        try:
            existing = {}
            try:
                with open(hold_json_path) as f:
                    existing = json.load(f)
            except (OSError, json.JSONDecodeError, ValueError):
                pass

            data = {"hold_reason": reason, "held_at": datetime.now().isoformat()}
            if details:
                data.update({k: v for k, v in details.items()
                             if k not in ("reason", "original_reason")})

            if existing:
                if "original_reason" in existing:
                    data["original_reason"] = existing["original_reason"]
                elif existing.get("hold_reason") != reason:
                    data["original_reason"] = existing["hold_reason"]

            with open(hold_json_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass
