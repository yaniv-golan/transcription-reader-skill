from extract_transcript import extract_stj


class TestExtractStj:
    def test_segment_count(self, stj_file):
        segments = extract_stj(stj_file)
        assert len(segments) == 8

    def test_speaker_names_resolved(self, stj_file):
        segments = extract_stj(stj_file)
        assert segments[0].speaker == "Alice"
        assert segments[2].speaker == "Bob"
        assert segments[5].speaker == "Charlie"

    def test_text_content(self, stj_file):
        segments = extract_stj(stj_file)
        assert segments[0].text == "Welcome everyone to the meeting."

    def test_timestamps(self, stj_file):
        segments = extract_stj(stj_file)
        assert segments[0].start == 1.0
        assert segments[0].end == 4.5

    def test_speakers_only_filter(self, stj_file):
        segments = extract_stj(stj_file, speakers_only="Bob")
        assert all(s.speaker == "Bob" for s in segments)
        assert len(segments) == 2

    def test_stats_output(self, stj_file):
        result = extract_stj(stj_file, stats=True)
        assert isinstance(result, str)
        assert "Total segments: 8" in result
        assert "Duration:" in result
