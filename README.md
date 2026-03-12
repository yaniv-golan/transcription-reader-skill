# Transcription Reader

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Release](https://img.shields.io/github/v/release/yaniv-golan/transcription-reader-skill)](https://github.com/yaniv-golan/transcription-reader-skill/releases)
[![Tests](https://img.shields.io/github/actions/workflow/status/yaniv-golan/transcription-reader-skill/tests.yml?label=tests)](https://github.com/yaniv-golan/transcription-reader-skill/actions/workflows/tests.yml)
[![Agent Skills Compatible](https://img.shields.io/badge/Agent_Skills-compatible-4A90D9)](https://agentskills.io)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org)
[![Claude Code Plugin](https://img.shields.io/badge/Claude_Code-plugin-F97316)](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/plugins)
[![Cursor Plugin](https://img.shields.io/badge/Cursor-plugin-00D886)](https://cursor.com/docs/plugins)

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

### Cursor

1. Open **Cursor Settings**
2. Paste `https://github.com/yaniv-golan/transcription-reader-skill` into the **Search or Paste Link** box

### Manus

1. Download [`transcription-reader.zip`](https://github.com/yaniv-golan/transcription-reader-skill/releases/latest/download/transcription-reader.zip)
2. Go to **Settings** → **Skills**
3. Click **+ Add** → **Upload**
4. Upload the zip

### ChatGPT

1. Download [`transcription-reader.zip`](https://github.com/yaniv-golan/transcription-reader-skill/releases/latest/download/transcription-reader.zip)
2. Go to **Settings** → **Skills** → **New Skill** → **Upload from your Computer**
3. Upload the zip

### Other Tools (Codex CLI, Windsurf, etc.)

Download [`transcription-reader.zip`](https://github.com/yaniv-golan/transcription-reader-skill/releases/latest/download/transcription-reader.zip) and extract the `transcription-reader/` folder to:

- **Project-level**: `.agents/skills/` in your project root
- **User-level**: `~/.agents/skills/`

## Usage

The skill auto-activates when you attach or reference a transcription file. You can also invoke it manually with `/transcription-reader`:

```
/transcription-reader summarize the first 20 minutes of the attached conversation
```

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
  --output-format FMT    Output as 'text' (default) or 'jsonl' (one JSON object per line)
  --keep-timestamps      Include timestamps in output
  --merge-speakers       Merge consecutive segments from the same speaker
  --time-range RANGE     Extract only a time range (e.g., 10:00-20:00)
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
