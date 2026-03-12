"""End-to-end CLI tests via subprocess."""
import json
import subprocess
import sys
from pathlib import Path

SCRIPT = str(Path(__file__).parent.parent / "skills" / "transcription-reader" / "scripts" / "extract_transcript.py")
FIXTURES = Path(__file__).parent / "fixtures"


def run_script(*args):
    """Run extract_transcript.py and return (stdout, stderr, returncode)."""
    result = subprocess.run(
        [sys.executable, SCRIPT, *args],
        capture_output=True, text=True, timeout=30,
    )
    return result.stdout, result.stderr, result.returncode


def test_cli_vtt_basic():
    stdout, stderr, rc = run_script(str(FIXTURES / "sample.vtt"))
    assert rc == 0
    assert "Welcome everyone" in stdout
    assert "Alice:" in stdout


def test_cli_srt_basic():
    stdout, stderr, rc = run_script(str(FIXTURES / "sample.srt"))
    assert rc == 0
    assert "Welcome everyone" in stdout


def test_cli_ass_basic():
    stdout, stderr, rc = run_script(str(FIXTURES / "sample.ass"))
    assert rc == 0
    assert "Welcome everyone" in stdout
    assert "Alice:" in stdout


def test_cli_stj_basic():
    stdout, stderr, rc = run_script(str(FIXTURES / "sample.stj.json"))
    assert rc == 0
    assert "Welcome everyone" in stdout
    assert "Alice:" in stdout


def test_cli_keep_timestamps():
    stdout, stderr, rc = run_script(str(FIXTURES / "sample.vtt"), "--keep-timestamps")
    assert rc == 0
    assert "[00:01]" in stdout or "[0:01]" in stdout


def test_cli_speakers_only():
    stdout, stderr, rc = run_script(str(FIXTURES / "sample.vtt"), "--speakers-only", "Bob")
    assert rc == 0
    assert "Bob" in stdout or "budget" in stdout
    assert "Charlie" not in stdout


def test_cli_merge_speakers():
    stdout, stderr, rc = run_script(str(FIXTURES / "sample.vtt"), "--merge-speakers")
    assert rc == 0
    lines = [l for l in stdout.strip().split('\n') if l.strip()]
    # Merged: Alice(2) + Bob(2) + Alice(1) + Charlie(2) + Alice(1) = 5 blocks
    assert len(lines) == 5


def test_cli_time_range():
    stdout, stderr, rc = run_script(str(FIXTURES / "sample.vtt"), "--time-range", "00:10-00:25")
    assert rc == 0
    assert "budget" in stdout
    assert "Welcome" not in stdout  # Before the range


def test_cli_jsonl():
    stdout, stderr, rc = run_script(str(FIXTURES / "sample.vtt"), "--output-format", "jsonl")
    assert rc == 0
    lines = stdout.strip().split('\n')
    assert len(lines) == 8
    obj = json.loads(lines[0])
    assert "text" in obj
    assert "speaker" in obj


def test_cli_merge_and_jsonl():
    stdout, stderr, rc = run_script(
        str(FIXTURES / "sample.vtt"), "--merge-speakers", "--output-format", "jsonl"
    )
    assert rc == 0
    lines = stdout.strip().split('\n')
    assert len(lines) == 5
    obj = json.loads(lines[0])
    assert obj["speaker"] == "Alice"
    assert "Welcome" in obj["text"]
    assert "agenda" in obj["text"]


def test_cli_time_range_and_merge():
    stdout, stderr, rc = run_script(
        str(FIXTURES / "sample.vtt"), "--time-range", "00:10-00:25", "--merge-speakers"
    )
    assert rc == 0
    # Should have filtered then merged


def test_cli_file_not_found():
    stdout, stderr, rc = run_script("nonexistent.vtt")
    assert rc == 1
    assert "not found" in stderr.lower() or "Error" in stderr


def test_cli_unknown_format():
    stdout, stderr, rc = run_script(str(FIXTURES / "sample.vtt"), "--format", "stj")
    # This will try to parse VTT as STJ — should error
    assert rc != 0 or "Error" in stderr


def test_cli_list_speakers():
    stdout, stderr, rc = run_script(str(FIXTURES / "sample.vtt"), "--list-speakers")
    assert rc == 0
    assert "Alice" in stdout
    assert "Bob" in stdout
    assert "Charlie" in stdout


def test_cli_stats():
    stdout, stderr, rc = run_script(str(FIXTURES / "sample.vtt"), "--stats")
    assert rc == 0
    assert "Statistics" in stdout
