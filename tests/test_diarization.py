"""Tests for diarization-only STJ file handling.

Diarization-only files have speaker timing but no transcribed text.
They should return Segment objects so the post-processing pipeline
(--merge-speakers, --time-range, --output-format jsonl) works on them.
"""
import json
import os
import tempfile

from extract_transcript import (
    Segment, extract_stj, merge_speaker_runs, segments_to_text,
    segments_to_jsonl, filter_by_time_range,
)


def _write_diarization_stj():
    """Create a minimal diarization-only STJ file."""
    data = {
        "stj": {
            "version": "0.6.1",
            "metadata": {
                "transcriber": {"name": "test", "version": "1.0"},
                "created_at": "2026-01-01T00:00:00Z",
                "source": {"duration": 30.0},
            },
            "transcript": {
                "speakers": [
                    {"id": "s1", "name": "Alice"},
                    {"id": "s2", "name": "Bob"},
                ],
                "segments": [
                    {"start": 0.0, "end": 5.0, "text": "", "speaker_id": "s1"},
                    {"start": 5.0, "end": 10.0, "text": "", "speaker_id": "s1"},
                    {"start": 10.0, "end": 15.0, "text": "", "speaker_id": "s2"},
                    {"start": 15.0, "end": 20.0, "text": "", "speaker_id": "s2"},
                    {"start": 20.0, "end": 25.0, "text": "", "speaker_id": "s1"},
                    {"start": 25.0, "end": 30.0, "text": "", "speaker_id": "s2"},
                ],
            },
        }
    }
    f = tempfile.NamedTemporaryFile(
        mode='w', suffix='.stj.json', delete=False, encoding='utf-8'
    )
    json.dump(data, f)
    f.close()
    return f.name


class TestDiarizationReturnsSegments:
    """Diarization path should return List[Segment], not str."""

    def test_returns_list_of_segments(self):
        path = _write_diarization_stj()
        try:
            result = extract_stj(path)
            assert isinstance(result, list)
            assert all(isinstance(s, Segment) for s in result)
        finally:
            os.unlink(path)

    def test_segments_have_speaker_names(self):
        path = _write_diarization_stj()
        try:
            result = extract_stj(path)
            assert result[0].speaker == "Alice"
            assert result[2].speaker == "Bob"
        finally:
            os.unlink(path)

    def test_segments_have_timestamps(self):
        path = _write_diarization_stj()
        try:
            result = extract_stj(path)
            assert result[0].start == 0.0
            assert result[0].end == 5.0
        finally:
            os.unlink(path)

    def test_segments_have_empty_text(self):
        path = _write_diarization_stj()
        try:
            result = extract_stj(path)
            assert result[0].text == ""
        finally:
            os.unlink(path)

    def test_segment_count(self):
        path = _write_diarization_stj()
        try:
            result = extract_stj(path)
            assert len(result) == 6
        finally:
            os.unlink(path)


class TestDiarizationWithMerge:
    """--merge-speakers should collapse consecutive same-speaker diarization segments."""

    def test_merge_reduces_count(self):
        path = _write_diarization_stj()
        try:
            segments = extract_stj(path)
            merged = merge_speaker_runs(segments)
            # 6 segments: Alice,Alice,Bob,Bob,Alice,Bob → 4 merged
            assert len(merged) == 4
        finally:
            os.unlink(path)

    def test_merge_preserves_time_range(self):
        path = _write_diarization_stj()
        try:
            segments = extract_stj(path)
            merged = merge_speaker_runs(segments)
            # First merged block: Alice 0-10
            assert merged[0].speaker == "Alice"
            assert merged[0].start == 0.0
            assert merged[0].end == 10.0
        finally:
            os.unlink(path)


class TestDiarizationWithTimeRange:
    """--time-range should filter diarization segments."""

    def test_time_range_filters(self):
        path = _write_diarization_stj()
        try:
            segments = extract_stj(path)
            filtered = filter_by_time_range(segments, "0:08-0:22")
            # Segments overlapping 8-22s: [5-10], [10-15], [15-20], [20-25]
            assert len(filtered) == 4
        finally:
            os.unlink(path)


class TestDiarizationTextOutput:
    """Text output for diarization segments should be clean."""

    def test_text_output_with_timestamps(self):
        path = _write_diarization_stj()
        try:
            segments = extract_stj(path)
            merged = merge_speaker_runs(segments)
            text = segments_to_text(merged, keep_timestamps=True)
            lines = text.strip().split('\n')
            # Should have speaker labels and timestamps, no trailing whitespace
            assert "[00:00]" in lines[0]
            assert "Alice" in lines[0]
            for line in lines:
                assert line == line.rstrip(), f"Trailing whitespace in: {repr(line)}"
        finally:
            os.unlink(path)

    def test_text_output_without_timestamps(self):
        path = _write_diarization_stj()
        try:
            segments = extract_stj(path)
            merged = merge_speaker_runs(segments)
            text = segments_to_text(merged, keep_timestamps=False)
            lines = text.strip().split('\n')
            assert "Alice:" in lines[0]
            for line in lines:
                assert line == line.rstrip(), f"Trailing whitespace in: {repr(line)}"
        finally:
            os.unlink(path)


class TestDiarizationJsonlOutput:
    """JSONL output should work for diarization segments."""

    def test_jsonl_output(self):
        path = _write_diarization_stj()
        try:
            segments = extract_stj(path)
            output = segments_to_jsonl(segments)
            lines = output.strip().split('\n')
            assert len(lines) == 6
            first = json.loads(lines[0])
            assert first["speaker"] == "Alice"
            assert first["start"] == 0.0
            assert first["end"] == 5.0
        finally:
            os.unlink(path)
