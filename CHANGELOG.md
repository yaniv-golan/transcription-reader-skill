# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2026-03-12

First public release with cross-platform support.

### Added
- **Cross-platform support**: works with Claude Code, Cursor, Codex CLI, Manus, ChatGPT, and other Agent Skills-compatible tools
- **Claude Code**: plugin marketplace installation (`/plugin marketplace add`)
- **Cursor**: plugin installation from repo URL
- **Codex CLI**: skill installer support with `agents/openai.yaml` for UI metadata
- **Manus & ChatGPT**: generic zip upload from GitHub Releases
- **Extraction script** (`extract_transcript.py`): parses STJ, VTT, SRT, ASS, SSA formats
  - `--merge-speakers` to consolidate consecutive same-speaker segments
  - `--time-range` to extract specific time windows
  - `--output-format jsonl` for structured output
  - `--keep-timestamps`, `--min-confidence`, `--speakers-only`, `--language` filters
  - `--list-speakers` and `--stats` for quick overviews
  - Diarization-only STJ file support
- **Centralized version management**: `VERSION` file + `tools/bump-version.sh`
- **Stable download URL** for release zips
- **Cross-platform architecture docs** (`docs/cross-platform.md`)

[0.4.0]: https://github.com/yaniv-golan/transcription-reader-skill/releases/tag/v0.4.0
