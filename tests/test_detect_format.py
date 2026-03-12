from extract_transcript import detect_format


def test_detect_vtt():
    assert detect_format("meeting.vtt") == "vtt"


def test_detect_srt():
    assert detect_format("meeting.srt") == "srt"


def test_detect_ass():
    assert detect_format("meeting.ass") == "ass"


def test_detect_ssa():
    assert detect_format("meeting.ssa") == "ssa"


def test_detect_stj():
    assert detect_format("meeting.stj") == "stj"


def test_detect_stjson():
    assert detect_format("meeting.stjson") == "stj"


def test_detect_stj_json():
    assert detect_format("meeting.stj.json") == "stj"


def test_detect_stj_from_json_content(stj_file):
    assert detect_format(stj_file) == "stj"


def test_detect_unknown():
    assert detect_format("meeting.txt") is None
