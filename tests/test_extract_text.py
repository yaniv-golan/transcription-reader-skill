"""Test core extraction for each format — verifies segments are returned correctly."""
from extract_transcript import extract_vtt, extract_stj, extract_pysubs2, Segment


def test_vtt_returns_segments(vtt_file):
    result = extract_vtt(vtt_file)
    assert isinstance(result, list)
    assert all(isinstance(s, Segment) for s in result)
    assert len(result) == 8


def test_vtt_speaker_detection(vtt_file):
    result = extract_vtt(vtt_file)
    assert result[0].speaker == "Alice"
    assert result[2].speaker == "Bob"
    assert result[5].speaker == "Charlie"


def test_vtt_text_content(vtt_file):
    result = extract_vtt(vtt_file)
    assert result[0].text == "Welcome everyone to the meeting."


def test_vtt_timestamps(vtt_file):
    result = extract_vtt(vtt_file)
    assert result[0].start == 1.0
    assert result[0].end == 4.5


def test_vtt_speakers_only(vtt_file):
    result = extract_vtt(vtt_file, speakers_only="Bob")
    assert len(result) == 2
    assert all(s.speaker == "Bob" for s in result)


def test_srt_returns_segments(srt_file):
    result = extract_pysubs2(srt_file, "srt")
    assert isinstance(result, list)
    assert all(isinstance(s, Segment) for s in result)
    assert len(result) == 8


def test_srt_speaker_detection(srt_file):
    result = extract_pysubs2(srt_file, "srt")
    assert result[0].speaker == "ALICE"
    assert result[2].speaker == "BOB"


def test_srt_timestamps(srt_file):
    result = extract_pysubs2(srt_file, "srt")
    assert result[0].start == 1.0
    assert result[0].end == 4.5


def test_ass_returns_segments(ass_file):
    result = extract_pysubs2(ass_file, "ass")
    assert isinstance(result, list)
    assert all(isinstance(s, Segment) for s in result)
    assert len(result) == 8


def test_ass_speaker_from_name_field(ass_file):
    result = extract_pysubs2(ass_file, "ass")
    assert result[0].speaker == "Alice"
    assert result[2].speaker == "Bob"
    assert result[5].speaker == "Charlie"


def test_stj_returns_segments(stj_file):
    result = extract_stj(stj_file)
    assert isinstance(result, list)
    assert all(isinstance(s, Segment) for s in result)
    assert len(result) == 8


def test_stj_speaker_names_resolved(stj_file):
    result = extract_stj(stj_file)
    # Should resolve speaker IDs to names
    assert result[0].speaker == "Alice"
    assert result[2].speaker == "Bob"
    assert result[5].speaker == "Charlie"


def test_stj_timestamps(stj_file):
    result = extract_stj(stj_file)
    assert result[0].start == 1.0
    assert result[0].end == 4.5


def test_stj_speakers_only(stj_file):
    result = extract_stj(stj_file, speakers_only="Bob")
    assert len(result) == 2
    assert all(s.speaker == "Bob" for s in result)
