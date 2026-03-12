"""Test --merge-speakers functionality."""
from extract_transcript import merge_speaker_runs, Segment


def test_merge_consecutive_same_speaker():
    segments = [
        Segment(speaker="Alice", text="Hello.", start=0.0, end=2.0),
        Segment(speaker="Alice", text="How are you?", start=2.5, end=4.0),
        Segment(speaker="Bob", text="Good thanks.", start=5.0, end=7.0),
    ]
    merged = merge_speaker_runs(segments)
    assert len(merged) == 2
    assert merged[0].speaker == "Alice"
    assert merged[0].text == "Hello. How are you?"
    assert merged[0].start == 0.0
    assert merged[0].end == 4.0
    assert merged[1].speaker == "Bob"


def test_merge_alternating_speakers():
    segments = [
        Segment(speaker="Alice", text="Hi.", start=0.0, end=1.0),
        Segment(speaker="Bob", text="Hello.", start=1.5, end=2.5),
        Segment(speaker="Alice", text="How are you?", start=3.0, end=4.0),
    ]
    merged = merge_speaker_runs(segments)
    assert len(merged) == 3  # No merging — all different


def test_merge_three_consecutive():
    segments = [
        Segment(speaker="Alice", text="One.", start=0.0, end=1.0),
        Segment(speaker="Alice", text="Two.", start=1.5, end=2.5),
        Segment(speaker="Alice", text="Three.", start=3.0, end=4.0),
    ]
    merged = merge_speaker_runs(segments)
    assert len(merged) == 1
    assert merged[0].text == "One. Two. Three."
    assert merged[0].start == 0.0
    assert merged[0].end == 4.0


def test_merge_empty_list():
    assert merge_speaker_runs([]) == []


def test_merge_single_segment():
    segments = [Segment(speaker="Alice", text="Hello.", start=0.0, end=1.0)]
    merged = merge_speaker_runs(segments)
    assert len(merged) == 1
    assert merged[0].text == "Hello."


def test_merge_none_speaker_not_merged():
    segments = [
        Segment(speaker=None, text="First.", start=0.0, end=1.0),
        Segment(speaker=None, text="Second.", start=1.5, end=2.5),
    ]
    merged = merge_speaker_runs(segments)
    # None speakers should not be merged (they're unknown/different)
    assert len(merged) == 2


def test_merge_with_real_vtt(vtt_file):
    from extract_transcript import extract_vtt
    segments = extract_vtt(vtt_file)
    assert len(segments) == 8
    merged = merge_speaker_runs(segments)
    # Alice(2) + Bob(2) + Alice(1) + Charlie(2) + Alice(1) = 5 blocks
    assert len(merged) == 5
    assert merged[0].speaker == "Alice"
    assert "Welcome" in merged[0].text
    assert "agenda" in merged[0].text
