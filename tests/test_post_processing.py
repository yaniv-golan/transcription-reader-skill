from extract_transcript import (
    Segment, merge_speaker_runs, filter_by_time_range,
    segments_to_text, segments_to_jsonl,
)


class TestMergeSpeakerRuns:
    def test_merges_consecutive_same_speaker(self):
        segments = [
            Segment(speaker="Alice", text="Hello", start=0.0, end=1.0),
            Segment(speaker="Alice", text="How are you?", start=1.5, end=3.0),
            Segment(speaker="Bob", text="Good", start=4.0, end=5.0),
        ]
        merged = merge_speaker_runs(segments)
        assert len(merged) == 2
        assert merged[0].text == "Hello How are you?"
        assert merged[0].start == 0.0
        assert merged[0].end == 3.0

    def test_no_merge_different_speakers(self):
        segments = [
            Segment(speaker="Alice", text="Hi", start=0.0, end=1.0),
            Segment(speaker="Bob", text="Hey", start=1.0, end=2.0),
        ]
        merged = merge_speaker_runs(segments)
        assert len(merged) == 2

    def test_empty_input(self):
        assert merge_speaker_runs([]) == []

    def test_none_speaker_not_merged(self):
        segments = [
            Segment(speaker=None, text="Line 1", start=0.0, end=1.0),
            Segment(speaker=None, text="Line 2", start=1.0, end=2.0),
        ]
        merged = merge_speaker_runs(segments)
        assert len(merged) == 2


class TestFilterByTimeRange:
    def test_filters_to_range(self):
        segments = [
            Segment(speaker="A", text="Before", start=0.0, end=5.0),
            Segment(speaker="A", text="Inside", start=10.0, end=15.0),
            Segment(speaker="A", text="After", start=25.0, end=30.0),
        ]
        filtered = filter_by_time_range(segments, "0:08-0:20")
        assert len(filtered) == 1
        assert filtered[0].text == "Inside"

    def test_overlapping_segments_included(self):
        segments = [
            Segment(speaker="A", text="Overlap start", start=5.0, end=12.0),
            Segment(speaker="A", text="Fully inside", start=12.0, end=18.0),
            Segment(speaker="A", text="Overlap end", start=18.0, end=25.0),
        ]
        filtered = filter_by_time_range(segments, "0:10-0:20")
        assert len(filtered) == 3


class TestSegmentsToText:
    def test_speaker_labels_shown_on_change(self):
        segments = [
            Segment(speaker="Alice", text="Hello", start=0.0, end=1.0),
            Segment(speaker="Alice", text="More", start=1.0, end=2.0),
            Segment(speaker="Bob", text="Hi", start=2.0, end=3.0),
        ]
        text = segments_to_text(segments, keep_timestamps=False)
        lines = text.split('\n')
        assert lines[0] == "Alice: Hello"
        assert lines[1] == "More"
        assert lines[2] == "Bob: Hi"

    def test_with_timestamps(self):
        segments = [Segment(speaker="A", text="Hi", start=65.0, end=70.0)]
        text = segments_to_text(segments, keep_timestamps=True)
        assert text == "[01:05] A: Hi"
