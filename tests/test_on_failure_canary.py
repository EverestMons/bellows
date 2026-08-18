"""Regression-guard canary for the on_failure pause mode (plan 441)."""

import inspect
import textwrap

import bellows
from scripts.plan_lint import RECOGNIZED_PAUSE_TOKENS


def test_on_failure_in_recognized_tokens():
    assert "on_failure" in RECOGNIZED_PAUSE_TOKENS


def test_header_says_pause_on_failure_returns_false():
    header = {"pause_for_verdict": "on_failure"}
    assert bellows.header_says_pause(header, 1, 3, False) is False
    assert bellows.header_says_pause(header, 1, 3, True) is False


def test_effective_auto_close_implied_by_on_failure():
    src = inspect.getsource(bellows.run_plan)
    needle = 'header.get("pause_for_verdict") == "on_failure"'
    assert needle in src, (
        "effective_auto_close must include the on_failure disjunct"
    )
