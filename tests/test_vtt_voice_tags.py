import os
from pathlib import Path

from extract_transcript import extract_vtt

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestVttVoiceTags:
    def test_voice_tag_speaker_extracted(self):
        path = str(FIXTURES_DIR / "voice_tags.vtt")
        segments = extract_vtt(path)
        assert segments[0].speaker == "Alice"
        assert segments[1].speaker == "Bob"

    def test_voice_tag_text_clean(self):
        path = str(FIXTURES_DIR / "voice_tags.vtt")
        segments = extract_vtt(path)
        assert segments[0].text == "Welcome to the meeting"
        assert "<v" not in segments[0].text
        assert "</v>" not in segments[0].text

    def test_multiline_voice_tag(self):
        path = str(FIXTURES_DIR / "voice_tags.vtt")
        segments = extract_vtt(path)
        assert segments[2].speaker == "Alice"
        assert "quarterly results" in segments[2].text
