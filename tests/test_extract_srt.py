import os
import tempfile

from extract_transcript import extract_pysubs2


def _write_srt(content):
    f = tempfile.NamedTemporaryFile(mode='w', suffix='.srt', delete=False, encoding='utf-8')
    f.write(content)
    f.close()
    return f.name


class TestExtractSrtSpeakers:
    """Test SRT extraction with various speaker label formats."""

    def test_all_caps_speaker(self, srt_file):
        segments = extract_pysubs2(srt_file, 'srt')
        assert segments[0].speaker == "ALICE"
        assert segments[0].text == "Welcome everyone to the meeting."

    def test_short_abbreviation(self):
        srt = "1\n00:00:01,000 --> 00:00:04,000\nYG: Let me check\n"
        path = _write_srt(srt)
        try:
            segments = extract_pysubs2(path, 'srt')
            assert segments[0].speaker == "YG"
        finally:
            os.unlink(path)

    def test_speaker_with_digits(self):
        srt = "1\n00:00:01,000 --> 00:00:04,000\nSpeaker 1: Hello\n"
        path = _write_srt(srt)
        try:
            segments = extract_pysubs2(path, 'srt')
            assert segments[0].speaker == "Speaker 1"
        finally:
            os.unlink(path)

    def test_bracketed_speaker(self):
        srt = "1\n00:00:01,000 --> 00:00:04,000\n[BOB] Hello there\n"
        path = _write_srt(srt)
        try:
            segments = extract_pysubs2(path, 'srt')
            assert segments[0].speaker == "BOB"
            assert segments[0].text == "Hello there"
        finally:
            os.unlink(path)

    def test_no_speaker(self):
        srt = "1\n00:00:01,000 --> 00:00:04,000\nJust plain text\n"
        path = _write_srt(srt)
        try:
            segments = extract_pysubs2(path, 'srt')
            assert segments[0].speaker is None
            assert segments[0].text == "Just plain text"
        finally:
            os.unlink(path)

    def test_ass_name_field_preserved(self, ass_file):
        """ASS files use the Name field — shared parser should NOT interfere."""
        segments = extract_pysubs2(ass_file, 'ass')
        assert segments[0].speaker == "Alice"
        assert segments[0].text == "Welcome everyone to the meeting."

    def test_segment_count(self, srt_file):
        segments = extract_pysubs2(srt_file, 'srt')
        assert len(segments) == 8

    def test_timestamps_present(self, srt_file):
        segments = extract_pysubs2(srt_file, 'srt')
        assert segments[0].start == 1.0
        assert segments[0].end == 4.5
