"""Test --time-range functionality."""
from extract_transcript import filter_by_time_range, parse_time_range, Segment


def test_parse_time_range_mm_ss():
    start, end = parse_time_range("10:00-20:00")
    assert start == 600.0
    assert end == 1200.0


def test_parse_time_range_hh_mm_ss():
    start, end = parse_time_range("1:05:00-1:30:00")
    assert start == 3900.0
    assert end == 5400.0


def test_filter_segments_in_range():
    segments = [
        Segment(speaker="A", text="Before.", start=0.0, end=5.0),
        Segment(speaker="A", text="In range.", start=10.0, end=15.0),
        Segment(speaker="A", text="Also in range.", start=18.0, end=22.0),
        Segment(speaker="A", text="After.", start=30.0, end=35.0),
    ]
    filtered = filter_by_time_range(segments, "00:08-00:25")
    assert len(filtered) == 2
    assert filtered[0].text == "In range."
    assert filtered[1].text == "Also in range."


def test_filter_excludes_non_overlapping():
    segments = [
        Segment(speaker="A", text="Before.", start=0.0, end=5.0),
        Segment(speaker="A", text="After.", start=30.0, end=35.0),
    ]
    filtered = filter_by_time_range(segments, "00:10-00:20")
    assert len(filtered) == 0


def test_filter_includes_partial_overlap():
    segments = [
        Segment(speaker="A", text="Overlaps start.", start=8.0, end=12.0),
        Segment(speaker="A", text="Overlaps end.", start=18.0, end=25.0),
    ]
    filtered = filter_by_time_range(segments, "00:10-00:20")
    assert len(filtered) == 2  # Both overlap the range


def test_filter_with_real_vtt(vtt_file):
    from extract_transcript import extract_vtt
    segments = extract_vtt(vtt_file)
    # Get segments between 10s and 25s
    filtered = filter_by_time_range(segments, "00:10-00:25")
    # Segments: Bob 9-13 (overlaps), Bob 14-18.5, Alice 19-23, Charlie 24-28 (overlaps)
    assert len(filtered) == 4
