import os
import tempfile

from extract_transcript import extract_vtt


def _write_vtt(content):
    """Write VTT content to a temp file and return path."""
    f = tempfile.NamedTemporaryFile(mode='w', suffix='.vtt', delete=False, encoding='utf-8')
    f.write(content)
    f.close()
    return f.name


class TestExtractVttSpeakers:
    """Test VTT extraction with various speaker label formats."""

    def test_inline_capitalized_speaker(self, vtt_file):
        segments = extract_vtt(vtt_file)
        assert segments[0].speaker == "Alice"
        assert segments[0].text == "Welcome everyone to the meeting."

    def test_all_caps_speaker(self):
        vtt = "WEBVTT\n\n00:00:01.000 --> 00:00:04.000\nALICE: Hello everyone\n"
        path = _write_vtt(vtt)
        try:
            segments = extract_vtt(path)
            assert segments[0].speaker == "ALICE"
            assert segments[0].text == "Hello everyone"
        finally:
            os.unlink(path)

    def test_short_abbreviation_speaker(self):
        vtt = "WEBVTT\n\n00:00:01.000 --> 00:00:04.000\nYG: Let me check\n"
        path = _write_vtt(vtt)
        try:
            segments = extract_vtt(path)
            assert segments[0].speaker == "YG"
        finally:
            os.unlink(path)

    def test_speaker_with_digits(self):
        vtt = "WEBVTT\n\n00:00:01.000 --> 00:00:04.000\nSpeaker 1: Hello\n"
        path = _write_vtt(vtt)
        try:
            segments = extract_vtt(path)
            assert segments[0].speaker == "Speaker 1"
        finally:
            os.unlink(path)

    def test_bracketed_speaker(self):
        vtt = "WEBVTT\n\n00:00:01.000 --> 00:00:04.000\n[ALICE] Hello everyone\n"
        path = _write_vtt(vtt)
        try:
            segments = extract_vtt(path)
            assert segments[0].speaker == "ALICE"
            assert segments[0].text == "Hello everyone"
        finally:
            os.unlink(path)

    def test_angle_prefix_speaker(self):
        vtt = "WEBVTT\n\n00:00:01.000 --> 00:00:04.000\n>> Alice: Let me share\n"
        path = _write_vtt(vtt)
        try:
            segments = extract_vtt(path)
            assert segments[0].speaker == "Alice"
        finally:
            os.unlink(path)

    def test_no_speaker(self):
        vtt = "WEBVTT\n\n00:00:01.000 --> 00:00:04.000\nJust some caption text\n"
        path = _write_vtt(vtt)
        try:
            segments = extract_vtt(path)
            assert segments[0].speaker is None
            assert segments[0].text == "Just some caption text"
        finally:
            os.unlink(path)

    def test_voice_tag_speaker(self):
        vtt = "WEBVTT\n\n00:00:01.000 --> 00:00:04.000\n<v Alice>Hello everyone</v>\n"
        path = _write_vtt(vtt)
        try:
            segments = extract_vtt(path)
            assert segments[0].speaker == "Alice"
            assert segments[0].text == "Hello everyone"
        finally:
            os.unlink(path)

    def test_timestamps_present(self, vtt_file):
        segments = extract_vtt(vtt_file)
        assert segments[0].start == 1.0
        assert segments[0].end == 4.5

    def test_segment_count(self, vtt_file):
        segments = extract_vtt(vtt_file)
        assert len(segments) == 8
