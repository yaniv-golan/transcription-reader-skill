from extract_transcript import parse_speaker_from_text


class TestParseSpeakerFromText:
    """Test the shared speaker label parser against real-world patterns."""

    def test_capitalized_name(self):
        speaker, text = parse_speaker_from_text("Alice: Hello everyone")
        assert speaker == "Alice"
        assert text == "Hello everyone"

    def test_all_caps_name(self):
        speaker, text = parse_speaker_from_text("ALICE: Hello everyone")
        assert speaker == "ALICE"
        assert text == "Hello everyone"

    def test_short_abbreviation(self):
        speaker, text = parse_speaker_from_text("YG: Let me check")
        assert speaker == "YG"
        assert text == "Let me check"

    def test_name_with_digits(self):
        speaker, text = parse_speaker_from_text("Speaker 1: Hello")
        assert speaker == "Speaker 1"
        assert text == "Hello"

    def test_hyphenated_name(self):
        speaker, text = parse_speaker_from_text("Jean-Luc: Make it so")
        assert speaker == "Jean-Luc"
        assert text == "Make it so"

    def test_apostrophe_name(self):
        speaker, text = parse_speaker_from_text("O'Brien: Aye captain")
        assert speaker == "O'Brien"
        assert text == "Aye captain"

    def test_name_with_parenthetical(self):
        speaker, text = parse_speaker_from_text("Alice (Guest): Hi there")
        assert speaker == "Alice (Guest)"
        assert text == "Hi there"

    def test_lowercase_name(self):
        speaker, text = parse_speaker_from_text("yaniv: sounds good")
        assert speaker == "yaniv"
        assert text == "sounds good"

    def test_double_angle_prefix(self):
        speaker, text = parse_speaker_from_text(">> Alice: Let me share")
        assert speaker == "Alice"
        assert text == "Let me share"

    def test_bracketed_label(self):
        speaker, text = parse_speaker_from_text("[ALICE] Hello everyone")
        assert speaker == "ALICE"
        assert text == "Hello everyone"

    def test_bracketed_with_space(self):
        speaker, text = parse_speaker_from_text("[Speaker 1] Testing")
        assert speaker == "Speaker 1"
        assert text == "Testing"

    def test_plain_text_no_speaker(self):
        speaker, text = parse_speaker_from_text("Hello everyone")
        assert speaker is None
        assert text == "Hello everyone"

    def test_colon_in_sentence_not_speaker(self):
        speaker, text = parse_speaker_from_text(
            "The quick brown fox jumped over the lazy dog: and then rested"
        )
        assert speaker is None
        assert "quick brown fox" in text

    def test_url_not_speaker(self):
        speaker, text = parse_speaker_from_text("Check https://example.com for details")
        assert speaker is None
        assert text == "Check https://example.com for details"

    def test_time_not_speaker(self):
        speaker, text = parse_speaker_from_text("10:30 is when we start")
        assert speaker is None
        assert text == "10:30 is when we start"

    def test_single_char_not_speaker(self):
        speaker, text = parse_speaker_from_text("I: don't think so")
        assert speaker is None
