import json
import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import decisions


def _make_assistant_event(text, event_idx=0):
    """Build a minimal assistant NDJSON event with a single text content item."""
    return {"type": "assistant", "message": {"content": [{"type": "text", "text": text}]}}


def _make_ndjson(*events):
    """Build an NDJSON string from a list of event dicts."""
    return "\n".join(json.dumps(e) for e in events)


class TestLoadPhrases:
    def setup_method(self):
        # Reset the module-level cache before each test
        decisions._cached_phrases = None

    def test_loads_phrases_from_file(self):
        phrases = decisions.load_phrases()
        assert len(phrases) > 0
        # All should be lowercased
        for p in phrases:
            assert p == p.lower(), f"Phrase not lowercased: {p}"

    def test_includes_known_phrases(self):
        phrases = decisions.load_phrases()
        assert "had to" in phrases
        assert "decided to" in phrases
        assert "wait," in phrases
        assert "need to fix" in phrases  # split from "let me fix / need to fix"
        assert "let me fix" in phrases

    def test_splits_slash_alternatives(self):
        phrases = decisions.load_phrases()
        # "re-run / rerun" should produce two separate entries
        assert "re-run" in phrases
        assert "rerun" in phrases
        # "doesn't exist / does not exist"
        assert "doesn't exist" in phrases
        assert "does not exist" in phrases

    def test_handles_missing_file(self):
        with patch.object(decisions, "PHRASES_FILE", decisions.Path("/nonexistent/path.md")):
            decisions._cached_phrases = None
            phrases = decisions.load_phrases()
            assert phrases == []

    def test_caches_result(self):
        phrases1 = decisions.load_phrases()
        phrases2 = decisions.load_phrases()
        assert phrases1 is phrases2


class TestExtractDecisionBlocks:
    def setup_method(self):
        decisions._cached_phrases = None

    def test_s_class_blocks_from_ground_truth(self):
        """All 6 S-class blocks from the detection design ground truth must match."""
        labeled_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "knowledge", "qa", "evidence",
            "intermediate-decision-detection-2026-05-12",
            "labeled-blocks.jsonl",
        )
        phrases = decisions.load_phrases()

        s_blocks = []
        with open(labeled_path) as f:
            for line in f:
                entry = json.loads(line)
                if entry["label"] == "S":
                    s_blocks.append(entry)

        assert len(s_blocks) == 6, f"Expected 6 S-class blocks, got {len(s_blocks)}"

        for block in s_blocks:
            event = _make_assistant_event(block["text"])
            ndjson = _make_ndjson(event)
            results = decisions.extract_decision_blocks(ndjson, phrases)
            assert len(results) > 0, (
                f"S-class block not matched: plan={block['plan']}, "
                f"step={block['step']}, block_idx={block['block_idx']}, "
                f"text={block['text'][:80]}"
            )

    def test_empty_input_string(self):
        phrases = decisions.load_phrases()
        assert decisions.extract_decision_blocks("", phrases) == []

    def test_empty_input_list(self):
        phrases = decisions.load_phrases()
        assert decisions.extract_decision_blocks([], phrases) == []

    def test_none_input(self):
        phrases = decisions.load_phrases()
        assert decisions.extract_decision_blocks(None, phrases) == []

    def test_empty_phrases(self):
        event = _make_assistant_event("I decided to change the approach.")
        ndjson = _make_ndjson(event)
        assert decisions.extract_decision_blocks(ndjson, []) == []

    def test_malformed_ndjson(self):
        phrases = decisions.load_phrases()
        malformed = "not valid json\n{broken\n"
        result = decisions.extract_decision_blocks(malformed, phrases)
        assert result == []

    def test_malformed_mixed_with_valid(self):
        phrases = ["decided to"]
        valid_event = json.dumps(_make_assistant_event("I decided to skip that."))
        ndjson = f"not json\n{valid_event}\n{{broken}}\n"
        result = decisions.extract_decision_blocks(ndjson, phrases)
        assert len(result) == 1
        assert "decided to" in result[0]["matched_phrases"]

    def test_multiple_content_items(self):
        """Assistant event with multiple text content items — each should be checked."""
        phrases = ["decided to", "wait,"]
        event = {
            "type": "assistant",
            "message": {"content": [
                {"type": "text", "text": "I decided to change this."},
                {"type": "tool_use", "name": "Read"},
                {"type": "text", "text": "Wait, that's wrong."},
            ]},
        }
        ndjson = _make_ndjson(event)
        results = decisions.extract_decision_blocks(ndjson, phrases)
        assert len(results) == 2
        assert results[0]["matched_phrases"] == ["decided to"]
        assert results[1]["matched_phrases"] == ["wait,"]

    def test_text_truncation(self):
        phrases = ["decided to"]
        long_text = "I decided to " + "x" * 600
        event = _make_assistant_event(long_text)
        ndjson = _make_ndjson(event)
        results = decisions.extract_decision_blocks(ndjson, phrases)
        assert len(results) == 1
        assert len(results[0]["text"]) == 500

    def test_case_insensitive_matching(self):
        phrases = ["decided to"]
        event = _make_assistant_event("I DECIDED TO change things.")
        ndjson = _make_ndjson(event)
        results = decisions.extract_decision_blocks(ndjson, phrases)
        assert len(results) == 1

    def test_non_assistant_events_ignored(self):
        phrases = ["decided to"]
        events = [
            {"type": "system", "content": [{"type": "text", "text": "I decided to do this."}]},
            {"type": "user", "content": [{"type": "text", "text": "I decided to ask."}]},
            {"type": "result", "result": "I decided to finish."},
        ]
        ndjson = _make_ndjson(*events)
        results = decisions.extract_decision_blocks(ndjson, phrases)
        assert results == []

    def test_pre_parsed_event_list(self):
        phrases = ["decided to"]
        events = [_make_assistant_event("I decided to change this.")]
        results = decisions.extract_decision_blocks(events, phrases)
        assert len(results) == 1
        assert results[0]["event_idx"] == 0

    def test_event_idx_tracking(self):
        phrases = ["decided to"]
        events = [
            {"type": "system", "content": []},
            {"type": "assistant", "message": {"content": [{"type": "text", "text": "No match here."}]}},
            {"type": "assistant", "message": {"content": [{"type": "text", "text": "I decided to act."}]}},
        ]
        ndjson = _make_ndjson(*events)
        results = decisions.extract_decision_blocks(ndjson, phrases)
        assert len(results) == 1
        assert results[0]["event_idx"] == 2
