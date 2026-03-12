"""Test --output-format jsonl functionality."""
import json

from extract_transcript import segments_to_jsonl, segments_to_text, Segment


def test_jsonl_basic():
    segments = [
        Segment(speaker="Alice", text="Hello.", start=1.0, end=3.0),
        Segment(speaker="Bob", text="Hi there.", start=4.0, end=6.0),
    ]
    output = segments_to_jsonl(segments)
    lines = output.strip().split('\n')
    assert len(lines) == 2

    obj1 = json.loads(lines[0])
    assert obj1["speaker"] == "Alice"
    assert obj1["text"] == "Hello."
    assert obj1["start"] == 1.0
    assert obj1["end"] == 3.0

    obj2 = json.loads(lines[1])
    assert obj2["speaker"] == "Bob"


def test_jsonl_no_speaker():
    segments = [
        Segment(speaker=None, text="Unknown speaker.", start=0.0, end=1.0),
    ]
    output = segments_to_jsonl(segments)
    obj = json.loads(output.strip())
    assert "speaker" not in obj
    assert obj["text"] == "Unknown speaker."


def test_jsonl_no_timestamps():
    segments = [
        Segment(speaker="Alice", text="No timing.", start=None, end=None),
    ]
    output = segments_to_jsonl(segments)
    obj = json.loads(output.strip())
    assert "start" not in obj
    assert "end" not in obj


def test_jsonl_rounds_timestamps():
    segments = [
        Segment(speaker="Alice", text="Hi.", start=1.123456, end=3.789012),
    ]
    output = segments_to_jsonl(segments)
    obj = json.loads(output.strip())
    assert obj["start"] == 1.123
    assert obj["end"] == 3.789


def test_text_output_basic():
    segments = [
        Segment(speaker="Alice", text="Hello.", start=1.0, end=3.0),
        Segment(speaker="Alice", text="More.", start=3.5, end=5.0),
        Segment(speaker="Bob", text="Hi.", start=6.0, end=8.0),
    ]
    output = segments_to_text(segments, keep_timestamps=False)
    lines = output.split('\n')
    assert lines[0] == "Alice: Hello."
    assert lines[1] == "More."  # Same speaker, no label repeated
    assert lines[2] == "Bob: Hi."


def test_text_output_with_timestamps():
    segments = [
        Segment(speaker="Alice", text="Hello.", start=65.0, end=68.0),
    ]
    output = segments_to_text(segments, keep_timestamps=True)
    assert output == "[01:05] Alice: Hello."


def test_jsonl_with_real_vtt(vtt_file):
    from extract_transcript import extract_vtt
    segments = extract_vtt(vtt_file)
    output = segments_to_jsonl(segments)
    lines = output.strip().split('\n')
    assert len(lines) == 8
    for line in lines:
        obj = json.loads(line)
        assert "text" in obj
        assert "start" in obj
        assert "end" in obj
