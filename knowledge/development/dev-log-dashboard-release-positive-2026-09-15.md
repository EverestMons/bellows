# Dev-log: dashboard-release-positive — 2026-09-15

## Pins re-derived (P1, P2)

`dashboard.py`: `class_hold_rows` :108–113, sorted by `r["file"]` (:112); the shell's `mode` :417 and `release_target` :418; `_do_release` :526–555, which resets `release_target` and `mode` (:554–555); `_handle_key` :557; the `l` branch :564–568; the `confirm_release` branch :580–590 — `if key in (ord("y"), ord("Y")):` :581, `if stdscr is not None:` :582, the footer row :584, the `Releasing` line :585, `addstr` :586, `refresh` :587, `self._do_release(self.release_target)` :588; `return None` :591

Re-derived from `sed -n '108,113p;526,591p' dashboard.py`:

```
def class_hold_rows(deposit_rows):
    """Return deposit rows whose hold reason starts with 'class:', sorted by file."""
    return sorted(
        [r for r in deposit_rows if r.get("status") == "HOLD" and r.get("reason", "").startswith("class:")],
        key=lambda r: r["file"],
    )
    def _do_release(self, row):
        """Run clear_plan.py --release-class-hold for row; set release_note."""
        cmd = [
            sys.executable,
            str(self.bellows_root / "tools" / "clear_plan.py"),
            os.path.join(row["dir"], row["file"]),
            "--release-class-hold",
        ]
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.bellows_root),
                capture_output=True,
                text=True,
                timeout=120,
            )
        except subprocess.TimeoutExpired:
            self.release_note = "release FAILED (timed out after 120 s)"
            self.release_target = None
            self.mode = "normal"
            return
        if result.returncode == 0:
            first_line = result.stdout.splitlines()[0] if result.stdout.strip() else ""
            self.release_note = first_line
        else:
            lines = [l for l in (result.stderr or result.stdout).splitlines() if l.strip()]
            last = lines[-1] if lines else ""
            self.release_note = f"release FAILED (exit {result.returncode}): {last}"
        self.release_target = None
        self.mode = "normal"

    def _handle_key(self, key, state, stdscr=None):
        """Dispatch a keypress; return 'quit' to signal loop exit, else None."""
        if self.mode == "normal":
            if key in (ord("r"), ord("R")):
                self.mode = "confirm_restart"
            elif key in (ord("q"), ord("Q")):
                self.mode = "confirm_quit"
            elif key in (ord("l"), ord("L")):
                holds = class_hold_rows(state.get("deposit_rows", []))
                if holds:
                    self.release_target = holds[0]
                    self.mode = "confirm_release"
        elif self.mode == "confirm_restart":
            if key in (ord("y"), ord("Y")):
                self._do_restart(stdscr)
            else:
                self.mode = "normal"
        elif self.mode == "confirm_quit":
            if key in (ord("y"), ord("Y")):
                self._do_quit()
                return "quit"
            else:
                self.mode = "normal"
        elif self.mode == "confirm_release":
            if key in (ord("y"), ord("Y")):
                if stdscr is not None:
                    h, w = stdscr.getmaxyx()
                    footer_row = h - 1
                    msg = _fit(f"Releasing {self.release_target['file']} …", w)
                    stdscr.addstr(footer_row, 0, msg, curses.A_REVERSE)
                    stdscr.refresh()
                self._do_release(self.release_target)
            else:
                self.mode = "normal"
        return None
```

P1 line numbers confirmed: `class_hold_rows` :108–113, sorted by `r["file"]` (:112); `_do_release` :526–555, resets `release_target` and `mode` (:554–555); `_handle_key` :557; `l` branch :564–568; `confirm_release` branch :580–590 — `if key in (ord("y"), ord("Y")):` :581, `if stdscr is not None:` :582, footer row :584, `Releasing` line :585, `addstr` :586, `refresh` :587, `self._do_release(self.release_target)` :588; `return None` :591.

P2 (re-derived from `grep -n -E '^(class|    def test_)' tests/test_dashboard.py; wc -l tests/test_dashboard.py`):

863 lines (pre-edit baseline: 863 lines — confirmed by `wc -l`); `TestHandleKey` at :840; t7 (`test_confirm_cancels_and_l_needs_a_class_hold`) at :841–863, file's last line :863. No existing test presses `y` in `confirm_release`. No mechanism mismatch.

## Green on the unedited code

```
tests/test_dashboard.py::TestHandleKey::test_confirm_cancels_and_l_needs_a_class_hold PASSED [ 25%]
tests/test_dashboard.py::TestHandleKey::test_y_in_confirm_release_releases_the_target[y] PASSED [ 50%]
tests/test_dashboard.py::TestHandleKey::test_y_in_confirm_release_releases_the_target[Y] PASSED [ 75%]
tests/test_dashboard.py::TestHandleKey::test_release_draws_its_line_before_it_runs PASSED [100%]

4 passed in 2.39s
```

File check: `tests/test_dashboard.py` — 47 passed in 5.71s

Compile check: `/usr/bin/python3 -m py_compile tests/test_dashboard.py` — exit 0

Full suite: 2467 passed, 2 skipped, 9 warnings in 239.00s

## The confirm observed (d1, d2)

```
tests/test_dashboard.py::TestHandleKey::test_y_in_confirm_release_releases_the_target[y] PASSED [ 33%]
tests/test_dashboard.py::TestHandleKey::test_y_in_confirm_release_releases_the_target[Y] PASSED [ 66%]
tests/test_dashboard.py::TestHandleKey::test_release_draws_its_line_before_it_runs PASSED [100%]

3 passed in 0.14s
```

## Mutation run

MUTATION: 5 killed, 0 survived, 0 error
