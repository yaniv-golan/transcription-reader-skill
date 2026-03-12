import sys
from pathlib import Path

import pytest

# Add the script directory to sys.path so we can import extract_transcript
SCRIPT_DIR = Path(__file__).parent.parent / "skills" / "transcription-reader" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def vtt_file():
    return str(FIXTURES_DIR / "sample.vtt")


@pytest.fixture
def srt_file():
    return str(FIXTURES_DIR / "sample.srt")


@pytest.fixture
def ass_file():
    return str(FIXTURES_DIR / "sample.ass")


@pytest.fixture
def stj_file():
    return str(FIXTURES_DIR / "sample.stj.json")
