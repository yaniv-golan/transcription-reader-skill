# Transcription Reader

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Release](https://img.shields.io/github/v/release/yaniv-golan/transcription-reader-skill)](https://github.com/yaniv-golan/transcription-reader-skill/releases)

An AI agent skill for reading, parsing, and analyzing transcription and subtitle files. Strips timing metadata to produce compact, analysis-ready text — saving 40-90% of tokens depending on format.

Uses the open [Agent Skills](https://agentskills.io) standard. Works with Claude, ChatGPT, Codex CLI, Cursor, Windsurf, Manus, and any other compatible tool.

## Supported Formats

| Extension | Format | Key Features |
|-----------|--------|-------------|
| `.stj`, `.stjson`, `.stj.json` | STJ (Standard Transcription JSON) | Speaker names, language per segment, confidence scores, word-level timing |
| `.vtt` | WebVTT | Voice tags and inline speaker labels (Zoom compatible) |
| `.srt` | SubRip | Simple numbered blocks, optional inline speakers |
| `.ass`, `.ssa` | Advanced SubStation Alpha | Named dialogue events, style stripping |

## Installation

### Claude Desktop

1. Click **Customize** in the sidebar
2. Click **Browse Plugins**
3. Go to the **Personal** tab and click **+**
4. Add: `yaniv-golan/transcription-reader-skill`

### Claude Code (CLI)

```bash
/plugin marketplace add yaniv-golan/transcription-reader-skill
```

### ChatGPT

1. Download `transcription-reader-v*.zip` (the generic version) from the [Releases](https://github.com/yaniv-golan/transcription-reader-skill/releases) page
2. Go to [chatgpt.com/skills](https://chatgpt.com/skills)
3. Click **New skill** → **Upload from computer**
4. Upload the zip — the skill auto-activates when relevant

### Other Tools (Codex CLI, Cursor, Windsurf, Manus, etc.)

Download `transcription-reader-v*.zip` from [Releases](https://github.com/yaniv-golan/transcription-reader-skill/releases) and copy the `transcription-reader/` folder to:

- **Project-level**: `.agents/skills/` in your project root
- **User-level**: `~/.agents/skills/`

## How It Works

The skill teaches your AI agent to:

1. **Identify the format** from the file extension
2. **Decide whether to extract** — small files can be read directly, large files benefit from the bundled extraction script (saves thousands of tokens)
3. **Run the extraction script** to produce clean, speaker-labeled text
4. **Analyze** based on your request — summarize, search, extract action items, identify speakers, etc.

## Extraction Script

The bundled `extract_transcript.py` supports:

```
Usage: extract_transcript.py INPUT_FILE [options]

Options:
  --format FORMAT        Force format (auto-detected from extension if omitted)
  --output FILE          Write to file instead of stdout
  --keep-timestamps      Include timestamps in output
  --min-confidence N     Skip low-confidence segments (STJ only)
  --speakers-only NAME   Filter to a specific speaker
  --language LANG        Filter by language (STJ only)
  --list-speakers        List speakers found in the file
  --stats                Show transcript statistics
```

### Dependencies

The script requires Python 3 and format-specific packages (install only what you need):

```bash
pip install stjlib       # STJ format
pip install webvtt-py    # WebVTT format
pip install pysubs2      # SRT, ASS, SSA formats
```

Missing packages are detected gracefully — the script tells you what to install.

## License

MIT
