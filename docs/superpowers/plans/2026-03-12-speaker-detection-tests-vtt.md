# Speaker Detection + Tests + VTT Robustness Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix brittle speaker label detection across VTT/SRT, add comprehensive tests, improve VTT voice tag handling, and add requirements.txt.

**Architecture:** Extract a shared `parse_speaker_from_text()` function that replaces three copy-pasted regexes. Add edge-case fixtures and tests for all extraction functions. Harden VTT voice tag parsing.

**Tech Stack:** Python 3, pytest, webvtt-py, pysubs2, stjlib

---

## Chunk 1: Shared Speaker Parser

### Task 1: Create shared `parse_speaker_from_text()` with tests

**Files:**
- Modify: `skills/transcription-reader/scripts/extract_transcript.py:293-306,364-384`
- Create: `tests/test_speaker_parsing.py`

- [ ] **Step 1: Write failing tests for the new shared parser**

Create `tests/test_speaker_parsing.py`:

```python
from extract_transcript import parse_speaker_from_text


class TestParseSpeakerFromText:
    """Test the shared speaker label parser against real-world patterns."""

    # --- Colon-delimited patterns ---

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

    # --- Prefixed patterns (Zoom/Teams) ---

    def test_double_angle_prefix(self):
        speaker, text = parse_speaker_from_text(">> Alice: Let me share")
        assert speaker == "Alice"
        assert text == "Let me share"

    # --- Bracketed patterns ---

    def test_bracketed_label(self):
        speaker, text = parse_speaker_from_text("[ALICE] Hello everyone")
        assert speaker == "ALICE"
        assert text == "Hello everyone"

    def test_bracketed_with_space(self):
        speaker, text = parse_speaker_from_text("[Speaker 1] Testing")
        assert speaker == "Speaker 1"
        assert text == "Testing"

    # --- Non-speaker text (should return None) ---

    def test_plain_text_no_speaker(self):
        speaker, text = parse_speaker_from_text("Hello everyone")
        assert speaker is None
        assert text == "Hello everyone"

    def test_colon_in_sentence_not_speaker(self):
        """A long prefix before colon is likely a sentence, not a speaker."""
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
        """Timestamps with colons should not be parsed as speakers."""
        speaker, text = parse_speaker_from_text("10:30 is when we start")
        assert speaker is None
        assert text == "10:30 is when we start"

    def test_single_char_not_speaker(self):
        """Single character before colon is too short to be a speaker label."""
        speaker, text = parse_speaker_from_text("I: don't think so")
        assert speaker is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/yaniv/Documents/code/transcription-reader-skill && python -m pytest tests/test_speaker_parsing.py -v`
Expected: FAIL — `parse_speaker_from_text` does not exist yet

- [ ] **Step 3: Implement `parse_speaker_from_text()` in extract_transcript.py**

Add this function after the `Segment` dataclass (around line 32), before `parse_time_range`:

```python
def parse_speaker_from_text(text: str) -> tuple:
    """Extract speaker label from text using common transcription patterns.

    Tries patterns in order of specificity:
    1. >> Name: text  (Zoom/Teams prefix)
    2. [NAME] text    (bracketed label)
    3. Name: text     (inline colon — permissive: allows digits, hyphens, apostrophes, parens)

    Returns (speaker, remaining_text) or (None, original_text).
    """
    # Pattern 1: >> Speaker: text (Zoom/Teams style)
    m = re.match(r'^>>\s*([A-Za-z0-9][A-Za-z0-9\s.\-\'()]{0,30}):\s+(.+)$', text, re.DOTALL)
    if m:
        return m.group(1).strip(), m.group(2).strip()

    # Pattern 2: [SPEAKER] text (bracketed label)
    m = re.match(r'^\[([A-Za-z0-9][A-Za-z0-9\s.\-\']{0,30})\]\s+(.+)$', text, re.DOTALL)
    if m:
        return m.group(1).strip(), m.group(2).strip()

    # Pattern 3: Speaker: text (inline colon, 2+ char label)
    m = re.match(r'^([A-Za-z0-9][A-Za-z0-9\s.\-\'()]{0,30}):\s+(.+)$', text, re.DOTALL)
    if m:
        label = m.group(1).strip()
        # Reject if label is a single character (likely not a speaker)
        if len(label) >= 2:
            return label, m.group(2).strip()

    return None, text
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/yaniv/Documents/code/transcription-reader-skill && python -m pytest tests/test_speaker_parsing.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_speaker_parsing.py skills/transcription-reader/scripts/extract_transcript.py
git commit -m "feat: add shared parse_speaker_from_text() with comprehensive tests"
```

### Task 2: Wire shared parser into VTT extractor

**Files:**
- Modify: `skills/transcription-reader/scripts/extract_transcript.py:293-306`
- Create: `tests/test_extract_vtt.py`

- [ ] **Step 1: Write failing tests for VTT extraction with varied speaker patterns**

Create `tests/test_extract_vtt.py`:

```python
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
        """The existing sample.vtt uses 'Alice: text' format."""
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
```

- [ ] **Step 2: Run tests to verify failures**

Run: `cd /Users/yaniv/Documents/code/transcription-reader-skill && python -m pytest tests/test_extract_vtt.py -v`
Expected: Several tests FAIL (short abbreviations, bracketed, angle prefix patterns)

- [ ] **Step 3: Update VTT `parse_speaker()` to use shared parser**

In `extract_vtt`, replace the inner `parse_speaker` function (lines ~293-306) with:

```python
    def parse_speaker(caption):
        """Extract speaker from VTT voice tags or inline text patterns."""
        # webvtt-py provides caption.voice for <v Speaker>text</v> tags
        if hasattr(caption, 'voice') and caption.voice:
            return caption.voice, caption.text
        # Fall back to raw lines check for older webvtt-py versions
        raw = '\n'.join(caption.lines) if hasattr(caption, 'lines') else caption.text
        m = re.match(r'<v\s+([^>]+)>(.*?)(?:</v>)?$', raw, re.DOTALL)
        if m:
            clean_text = re.sub(r'<[^>]+>', '', m.group(2)).strip()
            return m.group(1).strip(), clean_text
        # Fall back to shared speaker parser for inline labels
        return parse_speaker_from_text(caption.text)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/yaniv/Documents/code/transcription-reader-skill && python -m pytest tests/test_extract_vtt.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_extract_vtt.py skills/transcription-reader/scripts/extract_transcript.py
git commit -m "feat: wire shared speaker parser into VTT extractor"
```

### Task 3: Wire shared parser into SRT/pysubs2 extractor

**Files:**
- Modify: `skills/transcription-reader/scripts/extract_transcript.py:364-384`
- Create: `tests/test_extract_srt.py`

- [ ] **Step 1: Write failing tests for SRT extraction with varied speaker patterns**

Create `tests/test_extract_srt.py`:

```python
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
        """The existing sample.srt uses 'ALICE: text' format."""
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
```

- [ ] **Step 2: Run tests to verify failures**

Run: `cd /Users/yaniv/Documents/code/transcription-reader-skill && python -m pytest tests/test_extract_srt.py -v`
Expected: Several tests FAIL (short abbreviation, bracketed patterns)

- [ ] **Step 3: Update pysubs2 `get_speaker()` and `get_text()` to use shared parser**

Replace `get_speaker` and `get_text` in `extract_pysubs2` (lines ~364-384) with:

```python
    def get_speaker(event):
        """Extract speaker from ASS Name field or inline text patterns."""
        # ASS/SSA uses the Name field
        if event.name and event.name.strip():
            return event.name.strip()
        # SRT sometimes has inline labels — use shared parser
        speaker, _ = parse_speaker_from_text(event.text)
        return speaker

    def get_text(event):
        """Get clean text, stripping inline speaker label if present."""
        if not event.name or not event.name.strip():
            _, text = parse_speaker_from_text(event.text)
        else:
            text = event.text
        # Clean ASS override tags like {\an8}
        text = re.sub(r'\{\\[^}]+\}', '', text)
        # Replace \N with space
        text = text.replace('\\N', ' ').replace('\\n', ' ')
        return text.strip()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/yaniv/Documents/code/transcription-reader-skill && python -m pytest tests/test_extract_srt.py -v`
Expected: All PASS

- [ ] **Step 5: Run all tests to verify no regressions**

Run: `cd /Users/yaniv/Documents/code/transcription-reader-skill && python -m pytest tests/ -v`
Expected: All PASS

- [ ] **Step 6: Commit**

```bash
git add tests/test_extract_srt.py skills/transcription-reader/scripts/extract_transcript.py
git commit -m "feat: wire shared speaker parser into SRT/pysubs2 extractor"
```

## Chunk 2: STJ Tests, VTT Robustness, Requirements

### Task 4: Add STJ extraction tests

**Files:**
- Create: `tests/test_extract_stj.py`

- [ ] **Step 1: Write tests for STJ extraction**

Create `tests/test_extract_stj.py`:

```python
from extract_transcript import extract_stj


class TestExtractStj:
    """Test STJ extraction against sample fixture."""

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
```

- [ ] **Step 2: Run tests to verify they pass**

Run: `cd /Users/yaniv/Documents/code/transcription-reader-skill && python -m pytest tests/test_extract_stj.py -v`
Expected: All PASS (these test existing working behavior)

- [ ] **Step 3: Commit**

```bash
git add tests/test_extract_stj.py
git commit -m "test: add STJ extraction tests"
```

### Task 5: Add VTT voice tag edge case fixture and improve robustness

**Files:**
- Create: `tests/fixtures/voice_tags.vtt`
- Modify: `skills/transcription-reader/scripts/extract_transcript.py:293-300`
- Create: `tests/test_vtt_voice_tags.py`

- [ ] **Step 1: Create edge-case VTT fixture with voice tags**

Create `tests/fixtures/voice_tags.vtt`:

```
WEBVTT

00:00:01.000 --> 00:00:04.000
<v Alice>Welcome to the meeting</v>

00:00:05.000 --> 00:00:08.000
<v Bob>Thanks Alice</v>

00:00:09.000 --> 00:00:13.000
<v Alice>Let's discuss
the quarterly results</v>
```

- [ ] **Step 2: Write tests for voice tag handling**

Create `tests/test_vtt_voice_tags.py`:

```python
import os
from pathlib import Path

from extract_transcript import extract_vtt

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestVttVoiceTags:
    """Test VTT voice tag (<v Speaker>text</v>) handling."""

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
        # Third cue spans two lines
        assert segments[2].speaker == "Alice"
        assert "quarterly results" in segments[2].text
```

- [ ] **Step 3: Run tests — some may fail depending on webvtt-py behavior**

Run: `cd /Users/yaniv/Documents/code/transcription-reader-skill && python -m pytest tests/test_vtt_voice_tags.py -v`

- [ ] **Step 4: If voice tag tests fail, check the webvtt-py version**

The implementation in Task 2 already uses `caption.voice` (available in webvtt-py >= 0.5.0) with a raw-lines fallback. If tests fail, verify:

```bash
python3 -c "import webvtt; c = webvtt.structures.Caption; print(hasattr(c, 'voice'))"
```

If `caption.voice` is not available, the raw-lines regex fallback in the Task 2 implementation handles it. No additional code changes needed — just verify the tests pass.

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd /Users/yaniv/Documents/code/transcription-reader-skill && python -m pytest tests/test_vtt_voice_tags.py -v`
Expected: All PASS

- [ ] **Step 6: Commit**

```bash
git add tests/fixtures/voice_tags.vtt tests/test_vtt_voice_tags.py skills/transcription-reader/scripts/extract_transcript.py
git commit -m "feat: improve VTT voice tag robustness with edge case tests"
```

### Task 6: Add requirements.txt

**Files:**
- Create: `requirements.txt`

- [ ] **Step 1: Create requirements.txt**

```
# Core dependencies for extract_transcript.py
# Install only what you need for your format:
#   STJ:     pip install stjlib
#   VTT:     pip install webvtt-py
#   SRT/ASS: pip install pysubs2
#
# Or install all:
#   pip install -r requirements.txt

stjlib>=0.4.0
webvtt-py>=0.5.0
pysubs2>=1.6.0

# Test dependencies
pytest>=7.0.0
```

- [ ] **Step 2: Verify packages are already installed**

Run: `cd /Users/yaniv/Documents/code/transcription-reader-skill && python3 -c "import stjlib, webvtt, pysubs2; print('All dependencies available')"`
Expected: `All dependencies available`

- [ ] **Step 3: Run full test suite to verify everything works**

Run: `cd /Users/yaniv/Documents/code/transcription-reader-skill && python -m pytest tests/ -v`
Expected: All PASS

- [ ] **Step 4: Commit**

```bash
git add requirements.txt
git commit -m "chore: add requirements.txt with all optional dependencies"
```

### Task 7: Add merge/time-range post-processing tests

**Files:**
- Create: `tests/test_post_processing.py`

- [ ] **Step 1: Write tests for merge and time-range features**

Create `tests/test_post_processing.py`:

```python
from extract_transcript import (
    Segment, merge_speaker_runs, filter_by_time_range,
    segments_to_text, segments_to_jsonl,
)


class TestMergeSpeakerRuns:
    def test_merges_consecutive_same_speaker(self):
        segments = [
            Segment(speaker="Alice", text="Hello", start=0.0, end=1.0),
            Segment(speaker="Alice", text="How are you?", start=1.5, end=3.0),
            Segment(speaker="Bob", text="Good", start=4.0, end=5.0),
        ]
        merged = merge_speaker_runs(segments)
        assert len(merged) == 2
        assert merged[0].text == "Hello How are you?"
        assert merged[0].start == 0.0
        assert merged[0].end == 3.0

    def test_no_merge_different_speakers(self):
        segments = [
            Segment(speaker="Alice", text="Hi", start=0.0, end=1.0),
            Segment(speaker="Bob", text="Hey", start=1.0, end=2.0),
        ]
        merged = merge_speaker_runs(segments)
        assert len(merged) == 2

    def test_empty_input(self):
        assert merge_speaker_runs([]) == []

    def test_none_speaker_not_merged(self):
        segments = [
            Segment(speaker=None, text="Line 1", start=0.0, end=1.0),
            Segment(speaker=None, text="Line 2", start=1.0, end=2.0),
        ]
        merged = merge_speaker_runs(segments)
        assert len(merged) == 2


class TestFilterByTimeRange:
    def test_filters_to_range(self):
        segments = [
            Segment(speaker="A", text="Before", start=0.0, end=5.0),
            Segment(speaker="A", text="Inside", start=10.0, end=15.0),
            Segment(speaker="A", text="After", start=25.0, end=30.0),
        ]
        filtered = filter_by_time_range(segments, "0:08-0:20")
        assert len(filtered) == 1
        assert filtered[0].text == "Inside"

    def test_overlapping_segments_included(self):
        segments = [
            Segment(speaker="A", text="Overlap start", start=5.0, end=12.0),
            Segment(speaker="A", text="Fully inside", start=12.0, end=18.0),
            Segment(speaker="A", text="Overlap end", start=18.0, end=25.0),
        ]
        filtered = filter_by_time_range(segments, "0:10-0:20")
        assert len(filtered) == 3


class TestSegmentsToText:
    def test_speaker_labels_shown_on_change(self):
        segments = [
            Segment(speaker="Alice", text="Hello", start=0.0, end=1.0),
            Segment(speaker="Alice", text="More", start=1.0, end=2.0),
            Segment(speaker="Bob", text="Hi", start=2.0, end=3.0),
        ]
        text = segments_to_text(segments, keep_timestamps=False)
        lines = text.split('\n')
        assert lines[0] == "Alice: Hello"
        assert lines[1] == "More"  # same speaker, no label
        assert lines[2] == "Bob: Hi"

    def test_with_timestamps(self):
        segments = [Segment(speaker="A", text="Hi", start=65.0, end=70.0)]
        text = segments_to_text(segments, keep_timestamps=True)
        assert text == "[01:05] A: Hi"
```

- [ ] **Step 2: Run tests**

Run: `cd /Users/yaniv/Documents/code/transcription-reader-skill && python -m pytest tests/test_post_processing.py -v`
Expected: All PASS (these test existing working behavior)

- [ ] **Step 3: Commit**

```bash
git add tests/test_post_processing.py
git commit -m "test: add post-processing tests for merge, filter, and output"
```

### Task 8: Final full test run and cleanup

- [ ] **Step 1: Run complete test suite**

Run: `cd /Users/yaniv/Documents/code/transcription-reader-skill && python -m pytest tests/ -v --tb=short`
Expected: All PASS

- [ ] **Step 2: Verify old regex patterns are fully removed**

Search for the old pattern to make sure no copy remains:

Run: `cd /Users/yaniv/Documents/code/transcription-reader-skill && grep -n "A-Z\]\[A-Za-z" skills/transcription-reader/scripts/extract_transcript.py`
Expected: No matches (old `[A-Z][A-Za-z\s.]+` patterns should be gone)

- [ ] **Step 3: Final commit if any cleanup needed**
