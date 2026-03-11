# Cross-Platform Skill Repo Design

**Date**: 2026-03-10
**Status**: Approved

## Goal

Transform the transcription-reader skill into a public GitHub repo that works as:
1. A Claude plugin marketplace (Claude Desktop + Claude Code)
2. A ChatGPT-uploadable skill
3. A portable skill for any Agent Skills standard-compatible tool (Codex CLI, Cursor, Windsurf, Manus, Gemini CLI, etc.)

**Repo**: https://github.com/yaniv-golan/transcription-reader-skill

## Repo Structure

```
transcription-reader-skill/
├── .claude-plugin/
│   ├── plugin.json                  # Claude plugin manifest
│   └── marketplace.json             # Claude marketplace entry (single-plugin)
├── skills/
│   └── transcription-reader/        # Skill dir (name = SKILL.md name field)
│       ├── SKILL.md                 # Source of truth, uses ${CLAUDE_SKILL_DIR}
│       ├── scripts/
│       │   └── extract_transcript.py   # Renamed from extract-transcript.py (Python convention)
│       └── references/
│           └── stj-format.md
├── .github/
│   └── workflows/
│       └── release.yml              # On tag push: build generic + Claude zips
├── .gitignore
├── LICENSE                          # MIT
└── README.md                        # Cross-platform install instructions
```

## Key Design Decisions

### Source of truth: Claude version

The repo's SKILL.md uses `${CLAUDE_SKILL_DIR}` for script paths. This means:
- The repo works directly as a Claude plugin (no build step for primary platform)
- CI/CD generates generic variants by stripping `${CLAUDE_SKILL_DIR}/` → relative paths

### Two release artifacts

CI/CD (GitHub Actions on tag push `v*`) produces:
1. **`transcription-reader-claude-v{VERSION}.zip`** — SKILL.md with `${CLAUDE_SKILL_DIR}`, for Claude users who prefer manual install
2. **`transcription-reader-v{VERSION}.zip`** — SKILL.md with relative paths, for ChatGPT/Manus/Codex/Cursor/all others

The transformation is a single sed: `s|\${CLAUDE_SKILL_DIR}/||g`

### Why this works across platforms

| Platform | Script path resolution | What it needs |
|----------|----------------------|---------------|
| Claude Code/Desktop | `${CLAUDE_SKILL_DIR}` variable | Claude zip / repo directly |
| ChatGPT | Container cwd = skill dir | Generic zip (relative paths) |
| Manus | Model resolves relative paths to absolute using known skill location | Generic zip (relative paths) |
| Codex CLI | Scans `.agents/skills/`, resolves relative paths | Generic zip (relative paths) |
| Cursor/Windsurf/others | Same convention as Codex | Generic zip (relative paths) |

### Plugin configuration

**`.claude-plugin/plugin.json`:**
```json
{
  "name": "transcription-reader",
  "version": "1.0.0",
  "description": "Read, parse, and analyze transcription and subtitle files (STJ, VTT, SRT, ASS, SSA)",
  "author": {
    "name": "Yaniv Golan",
    "email": "yaniv@golan.name"
  },
  "repository": "https://github.com/yaniv-golan/transcription-reader-skill",
  "license": "MIT",
  "keywords": ["transcription", "subtitles", "captions", "vtt", "srt", "stj", "ass", "ssa"]
}
```

**`.claude-plugin/marketplace.json`:**
```json
{
  "name": "transcription-reader-marketplace",
  "owner": {
    "name": "Yaniv Golan",
    "email": "yaniv@golan.name"
  },
  "metadata": {
    "description": "Transcription and subtitle file reader skill"
  },
  "plugins": [
    {
      "name": "transcription-reader",
      "source": "./",
      "description": "Read, parse, and analyze transcription and subtitle files (STJ, VTT, SRT, ASS, SSA)",
      "category": "productivity",
      "tags": ["transcription", "subtitles", "captions", "meeting-notes"]
    }
  ]
}
```

Uses the `"source": "./"` pattern (repo root = plugin root).

### SKILL.md changes

**Frontmatter additions:**
```yaml
license: MIT
compatibility: Requires Python 3. Optional packages: stjlib (STJ), webvtt-py (VTT), pysubs2 (SRT/ASS/SSA).
metadata:
  author: Yaniv Golan
  version: "1.0.0"
```

**Body changes:**
- All `SKILL_DIR/scripts/extract_transcript.py` → `${CLAUDE_SKILL_DIR}/scripts/extract_transcript.py`
- Script filename references: `extract-transcript.py` → `extract_transcript.py`
- No content/instruction changes

### README structure

1. Header + badges (license, release)
2. What it does (one paragraph)
3. Cross-Platform Installation:
   - **Claude Desktop** (primary): Customize → Browse Plugins → Personal → + → `yaniv-golan/transcription-reader-skill`
   - **Claude Code** (CLI): `/plugin marketplace add yaniv-golan/transcription-reader-skill`
   - **ChatGPT**: Download generic zip from Releases → upload at chatgpt.com/skills
   - **Other tools**: Download generic zip → copy to `~/.agents/skills/`
4. Supported formats table
5. Script usage / CLI options
6. Dependencies
7. License

### Script rename

`extract-transcript.py` → `extract_transcript.py` (Python naming convention, matches SKILL.md references).
