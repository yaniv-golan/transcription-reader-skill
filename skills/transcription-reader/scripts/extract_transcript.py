#!/usr/bin/env python3
"""
Extract plain-text transcripts from various transcription/subtitle formats.
Strips timing metadata to produce compact, analysis-ready text.

Supported formats: STJ (.stj, .stjson, .stj.json), WebVTT (.vtt),
                   SRT (.srt), ASS/SSA (.ass, .ssa)

Required packages (install only what you need):
  - STJ:     pip install stjlib
  - VTT:     pip install webvtt-py
  - SRT/ASS: pip install pysubs2
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


def detect_format(filepath: str) -> str:
    """Auto-detect transcription format from file extension and content."""
    p = filepath.lower()
    if p.endswith('.stj.json') or p.endswith('.stjson') or p.endswith('.stj'):
        return 'stj'
    if p.endswith('.vtt'):
        return 'vtt'
    if p.endswith('.srt'):
        return 'srt'
    if p.endswith('.ass'):
        return 'ass'
    if p.endswith('.ssa'):
        return 'ssa'
    # Try JSON content detection for .json files
    if p.endswith('.json'):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if 'stj' in data:
                return 'stj'
        except (json.JSONDecodeError, IOError):
            pass
    return None


def format_time(seconds: float) -> str:
    """Format seconds as HH:MM:SS."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def ms_to_seconds(ms: int) -> float:
    """Convert milliseconds to seconds."""
    return ms / 1000.0


def timestamp_str_to_seconds(ts: str) -> float:
    """Convert HH:MM:SS.mmm or MM:SS.mmm to seconds."""
    parts = ts.strip().split(':')
    if len(parts) == 3:
        h, m, rest = parts
        s = float(rest)
        return int(h) * 3600 + int(m) * 60 + s
    elif len(parts) == 2:
        m, rest = parts
        s = float(rest)
        return int(m) * 60 + s
    return 0.0


# ── STJ ──────────────────────────────────────────────────────────────────────

def extract_stj(filepath, keep_timestamps=False, min_confidence=0.0,
                speakers_only=None, language=None, list_speakers=False, stats=False):
    try:
        import stjlib
    except ImportError:
        print("Error: stjlib not installed. Run: pip install stjlib", file=sys.stderr)
        sys.exit(1)

    stj = stjlib.StandardTranscriptionJSON.from_file(filepath)
    transcript = stj.transcript

    # Build speaker name map
    speaker_map = {}
    if transcript.speakers:
        for sp in transcript.speakers:
            speaker_map[sp.id] = sp.name or sp.id

    if list_speakers:
        if not speaker_map:
            print("No speakers defined in this STJ file.")
        else:
            for sid, name in speaker_map.items():
                segs = stj.get_segments_by_speaker(sid)
                print(f"  {name} ({sid}): {len(segs)} segments")
        return

    segments = transcript.segments

    # Detect diarization-only files (speaker timing without transcribed text)
    has_text = any(s.text.strip() for s in segments if s.text)
    if not has_text and not list_speakers and not stats:
        # Check metadata for diarization-only mode
        is_diarization = False
        try:
            meta = stj.metadata
            if meta and meta.extensions:
                for ext_val in meta.extensions.values():
                    if isinstance(ext_val, dict) and ext_val.get('mode') == 'diarization_only':
                        is_diarization = True
        except (AttributeError, TypeError):
            pass

        print("Warning: This STJ file contains no transcribed text.", file=sys.stderr)
        if is_diarization:
            print("  This is a diarization-only file (speaker timing without transcription).", file=sys.stderr)
            print("  It contains speaker segments showing who spoke when, but no words.", file=sys.stderr)
        print("  Use --stats or --list-speakers to see speaker timing information.", file=sys.stderr)

        # Still output speaker timeline as a useful fallback
        lines = []
        for seg in segments:
            speaker_name = speaker_map.get(seg.speaker_id, seg.speaker_id) if seg.speaker_id else "Unknown"
            lines.append(f"[{format_time(seg.start)} - {format_time(seg.end)}] {speaker_name}")
        return '\n'.join(lines)

    # Apply filters
    if min_confidence > 0:
        segments = [s for s in segments if (s.confidence or 1.0) >= min_confidence]
    if speakers_only:
        # Match by name or ID
        target_ids = set()
        for sid, name in speaker_map.items():
            if speakers_only.lower() in name.lower() or speakers_only.lower() == sid.lower():
                target_ids.add(sid)
        if not target_ids:
            print(f"Warning: No speaker matching '{speakers_only}' found.", file=sys.stderr)
        segments = [s for s in segments if s.speaker_id in target_ids]
    if language:
        segments = [s for s in segments if (s.language or '').lower() == language.lower()]

    if stats:
        return _print_stats_stj(stj, segments, speaker_map)

    # Output
    lines = []
    last_speaker = None
    for seg in segments:
        speaker_name = speaker_map.get(seg.speaker_id, seg.speaker_id) if seg.speaker_id else None
        prefix = ""
        if keep_timestamps:
            prefix = f"[{format_time(seg.start)}] "
        if speaker_name and speaker_name != last_speaker:
            lines.append(f"{prefix}{speaker_name}: {seg.text}")
            last_speaker = speaker_name
        elif speaker_name:
            lines.append(f"{prefix}{seg.text}")
        else:
            lines.append(f"{prefix}{seg.text}")
            last_speaker = None

    return '\n'.join(lines)


def _print_stats_stj(stj, segments, speaker_map):
    meta = stj.metadata
    lines = ["=== Transcript Statistics ==="]
    if meta and meta.source and meta.source.duration:
        lines.append(f"Duration: {format_time(meta.source.duration)}")
    if meta and meta.languages:
        lines.append(f"Languages: {', '.join(meta.languages)}")
    lines.append(f"Total segments: {len(segments)}")
    total_words = sum(len(s.text.split()) for s in segments)
    lines.append(f"Total words: {total_words}")

    # Per-speaker stats
    if speaker_map:
        lines.append("\nPer speaker:")
        for sid, name in speaker_map.items():
            sp_segs = [s for s in segments if s.speaker_id == sid]
            sp_words = sum(len(s.text.split()) for s in sp_segs)
            sp_time = sum(s.end - s.start for s in sp_segs)
            lines.append(f"  {name}: {len(sp_segs)} segments, {sp_words} words, ~{format_time(sp_time)} speaking time")

    return '\n'.join(lines)


# ── WebVTT ───────────────────────────────────────────────────────────────────

def extract_vtt(filepath, keep_timestamps=False, speakers_only=None, list_speakers=False, stats=False, **kwargs):
    try:
        import webvtt
    except ImportError:
        print("Error: webvtt-py not installed. Run: pip install webvtt-py", file=sys.stderr)
        sys.exit(1)

    captions = webvtt.read(filepath)

    # Try to extract speaker labels from VTT voice tags or text patterns
    def parse_speaker(caption):
        """Extract speaker from VTT voice tags (in raw lines) or inline text patterns."""
        # Check raw lines for <v Speaker>text</v> tags (text property strips these)
        raw = '\n'.join(caption.lines) if hasattr(caption, 'lines') else caption.text
        m = re.match(r'<v\s+([^>]+)>(.*?)(?:</v>)?$', raw, re.DOTALL)
        if m:
            clean_text = re.sub(r'<[^>]+>', '', m.group(2)).strip()
            return m.group(1).strip(), clean_text
        # SPEAKER NAME: text (from the clean text)
        text = caption.text
        m = re.match(r'^([A-Z][A-Za-z\s.]+):\s*(.+)$', text, re.DOTALL)
        if m:
            return m.group(1).strip(), m.group(2).strip()
        return None, text

    if list_speakers:
        speakers = set()
        for cap in captions:
            sp, _ = parse_speaker(cap)
            if sp:
                speakers.add(sp)
        if speakers:
            for sp in sorted(speakers):
                print(f"  {sp}")
        else:
            print("No speaker labels detected in this VTT file.")
        return

    if stats:
        total_words = sum(len(cap.text.split()) for cap in captions)
        lines = ["=== Transcript Statistics ==="]
        if captions:
            last = captions[-1]
            dur = timestamp_str_to_seconds(last.end)
            lines.append(f"Duration: ~{format_time(dur)}")
        lines.append(f"Total captions: {len(captions)}")
        lines.append(f"Total words: {total_words}")
        return '\n'.join(lines)

    # Build list of (speaker, text, caption) tuples with speaker filtering
    parsed = []
    for cap in captions:
        speaker, text = parse_speaker(cap)
        text = re.sub(r'<[^>]+>', '', text).strip()
        if not text:
            continue
        if speakers_only:
            if not speaker or speakers_only.lower() not in speaker.lower():
                continue
        parsed.append((speaker, text, cap))

    lines = []
    last_speaker = None
    for speaker, text, cap in parsed:
        prefix = ""
        if keep_timestamps:
            start_sec = timestamp_str_to_seconds(cap.start)
            prefix = f"[{format_time(start_sec)}] "

        if speaker and speaker != last_speaker:
            lines.append(f"{prefix}{speaker}: {text}")
            last_speaker = speaker
        elif speaker:
            lines.append(f"{prefix}{text}")
        else:
            lines.append(f"{prefix}{text}")
            last_speaker = None

    return '\n'.join(lines)


# ── SRT / ASS / SSA ─────────────────────────────────────────────────────────

def extract_pysubs2(filepath, fmt, keep_timestamps=False, speakers_only=None,
                    list_speakers=False, stats=False, **kwargs):
    try:
        import pysubs2
    except ImportError:
        print("Error: pysubs2 not installed. Run: pip install pysubs2", file=sys.stderr)
        sys.exit(1)

    subs = pysubs2.load(filepath)

    def get_speaker(event):
        """Extract speaker from ASS Name field or inline text patterns."""
        # ASS/SSA uses the Name field
        if event.name and event.name.strip():
            return event.name.strip()
        # SRT sometimes has inline labels
        m = re.match(r'^([A-Z][A-Za-z\s.]+):\s*(.+)$', event.text, re.DOTALL)
        if m:
            return m.group(1).strip()
        return None

    def get_text(event):
        """Get clean text, stripping inline speaker label if present."""
        m = re.match(r'^([A-Z][A-Za-z\s.]+):\s*(.+)$', event.text, re.DOTALL)
        if m and not event.name:
            return m.group(2).strip()
        # Clean ASS override tags like {\an8}
        text = re.sub(r'\{\\[^}]+\}', '', event.text)
        # Replace \N with space
        text = text.replace('\\N', ' ').replace('\\n', ' ')
        return text.strip()

    # Only process dialogue events
    events = [e for e in subs if e.type == 'Dialogue' or not hasattr(e, 'type')]

    if list_speakers:
        speakers = set()
        for e in events:
            sp = get_speaker(e)
            if sp:
                speakers.add(sp)
        if speakers:
            for sp in sorted(speakers):
                count = sum(1 for e in events if get_speaker(e) == sp)
                print(f"  {sp}: {count} segments")
        else:
            print("No speaker labels detected in this file.")
        return

    if speakers_only:
        events = [e for e in events if get_speaker(e) and
                  speakers_only.lower() in get_speaker(e).lower()]

    if stats:
        total_words = sum(len(get_text(e).split()) for e in events)
        lines = ["=== Transcript Statistics ==="]
        if events:
            dur_ms = max(e.end for e in events)
            lines.append(f"Duration: ~{format_time(ms_to_seconds(dur_ms))}")
        lines.append(f"Total events: {len(events)}")
        lines.append(f"Total words: {total_words}")
        speakers = set(get_speaker(e) for e in events if get_speaker(e))
        if speakers:
            lines.append(f"Speakers: {', '.join(sorted(speakers))}")
        return '\n'.join(lines)

    lines = []
    last_speaker = None
    for e in events:
        speaker = get_speaker(e)
        text = get_text(e)
        if not text:
            continue

        prefix = ""
        if keep_timestamps:
            prefix = f"[{format_time(ms_to_seconds(e.start))}] "

        if speaker and speaker != last_speaker:
            lines.append(f"{prefix}{speaker}: {text}")
            last_speaker = speaker
        elif speaker:
            lines.append(f"{prefix}{text}")
        else:
            lines.append(f"{prefix}{text}")
            last_speaker = None

    return '\n'.join(lines)


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Extract plain-text transcripts from transcription/subtitle files.",
        epilog="Supported formats: STJ, WebVTT, SRT, ASS, SSA"
    )
    parser.add_argument('input', help='Input transcription file')
    parser.add_argument('--format', '-f', choices=['stj', 'vtt', 'srt', 'ass', 'ssa'],
                        help='Force format (auto-detected from extension if omitted)')
    parser.add_argument('--output', '-o', help='Output file (default: stdout)')
    parser.add_argument('--keep-timestamps', '-t', action='store_true',
                        help='Include timestamps in output')
    parser.add_argument('--min-confidence', type=float, default=0.0,
                        help='Skip segments below this confidence (STJ only)')
    parser.add_argument('--speakers-only', '-s',
                        help='Filter to a specific speaker (by name or ID)')
    parser.add_argument('--language', '-l',
                        help='Filter to a specific language (STJ only)')
    parser.add_argument('--list-speakers', action='store_true',
                        help='List speakers found in the file')
    parser.add_argument('--stats', action='store_true',
                        help='Show transcript statistics')

    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    fmt = args.format or detect_format(args.input)
    if not fmt:
        print(f"Error: Cannot detect format for '{args.input}'. Use --format to specify.",
              file=sys.stderr)
        sys.exit(1)

    kwargs = dict(
        keep_timestamps=args.keep_timestamps,
        min_confidence=args.min_confidence,
        speakers_only=args.speakers_only,
        language=args.language,
        list_speakers=args.list_speakers,
        stats=args.stats,
    )

    if fmt == 'stj':
        result = extract_stj(args.input, **kwargs)
    elif fmt == 'vtt':
        result = extract_vtt(args.input, **kwargs)
    elif fmt in ('srt', 'ass', 'ssa'):
        result = extract_pysubs2(args.input, fmt, **kwargs)
    else:
        print(f"Error: Unsupported format: {fmt}", file=sys.stderr)
        sys.exit(1)

    if result is not None:
        if args.output:
            Path(args.output).write_text(result, encoding='utf-8')
            print(f"Written to {args.output}", file=sys.stderr)
        else:
            print(result)


if __name__ == '__main__':
    main()