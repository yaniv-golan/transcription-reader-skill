# Cross-Platform Architecture

This skill ships from a single source of truth and works across multiple AI platforms. This document explains how.

## Source of Truth

```
skills/transcription-reader/
├── SKILL.md              ← canonical skill definition
├── scripts/
│   └── extract_transcript.py
├── references/
│   └── stj-format.md
└── agents/
    └── openai.yaml       ← Codex CLI UI metadata
```

`SKILL.md` uses `${CLAUDE_SKILL_DIR}` for script paths. This variable is expanded by Claude Code before the LLM sees the content. Platforms that don't support this variable receive a processed copy (see Release Workflow below).

## How Each Platform Consumes the Skill

### Claude Code — direct from repo

- Installs from the plugin marketplace: `/plugin marketplace add yaniv-golan/transcription-reader-skill`
- Manifest: `.claude-plugin/plugin.json` with `"skills": "./skills"`
- Claude Code discovers `skills/transcription-reader/SKILL.md` automatically
- `${CLAUDE_SKILL_DIR}` is expanded to the actual path at runtime

### Cursor — direct from repo

- Installs as a plugin: Settings → paste repo URL into "Search or Paste Link"
- Manifest: `.cursor-plugin/plugin.json` (no `skills` field needed — auto-discovers from `skills/`)
- Same `SKILL.md` as Claude Code

### Manus — upload zip from GitHub Releases

- Download `transcription-reader.zip` from the [latest release](https://github.com/yaniv-golan/transcription-reader-skill/releases/latest/download/transcription-reader.zip)
- Upload at Settings → Skills → + Add → Upload
- The zip contains a flat `transcription-reader/` folder with `${CLAUDE_SKILL_DIR}/` stripped from paths (so `scripts/extract_transcript.py` becomes a relative path)
- Manus has no auto-update mechanism, so zip upload is the intended workflow

### ChatGPT — same zip as Manus

- Download same `transcription-reader.zip` from GitHub Releases
- Upload at Settings → Skills → New Skill → Upload from your Computer

### Codex CLI — install from repo or zip

**From repo (preferred):** Use the built-in skill installer, which copies the skill directory from GitHub:

```
$skill-installer https://github.com/yaniv-golan/transcription-reader-skill
```

The installer detects `skills/transcription-reader/SKILL.md` and installs to `~/.codex/skills/transcription-reader/`.

**From zip (manual):** Download `transcription-reader.zip` from GitHub Releases and extract to `~/.codex/skills/`.

Key details:
- The installer is a one-time copy — no auto-update. To update, remove the local skill directory and reinstall.
- Codex scans for skills in `.agents/skills/` (cwd and parents), `$REPO_ROOT/.agents/skills/`, `~/.codex/skills/`, and `/etc/codex/skills/`
- Supports progressive disclosure: only metadata is loaded initially; full SKILL.md loads on activation
- Includes `agents/openai.yaml` for UI customization (display name, brand color)
- Invoke explicitly with `/skills` or `$transcription-reader`, or implicitly when task matches the skill description

### Others (Windsurf, etc.) — same zip

- Download and extract to `~/.agents/skills/` or `.agents/skills/` in the project root

## Release Workflow

CI (`.github/workflows/release.yml`) runs on version tags (`v*`) and produces the generic zip:

```bash
cp -r skills/transcription-reader transcription-reader
sed -i 's|\${CLAUDE_SKILL_DIR}/||g' transcription-reader/SKILL.md
zip -r "transcription-reader.zip" transcription-reader/
```

The zip filename is fixed (`transcription-reader.zip`, not versioned) so the README can link to a stable URL:
```
https://github.com/yaniv-golan/transcription-reader-skill/releases/latest/download/transcription-reader.zip
```

## Version Management

The canonical version lives in `VERSION` at the repo root. Run `./tools/bump-version.sh` to propagate it to all four locations:

1. `.claude-plugin/plugin.json`
2. `.cursor-plugin/plugin.json`
3. `pyproject.toml`
4. `skills/transcription-reader/SKILL.md` (under `metadata.version`)

See [VERSIONING.md](../VERSIONING.md) for the full release process.

## Known Platform Quirks

### Manus YAML Parser

Manus uses a strict YAML parser for `SKILL.md` frontmatter:

- **No block scalars** — `>-` and `|` are not supported. Use quoted single-line strings.
- **Unquoted colons break parsing** — values containing `:` must be double-quoted.
- **Limited top-level fields** — only `name`, `description`, `license`, `metadata`, and `allowed-tools` are recognized. Custom fields (like `compatibility`) must go under `metadata`.

### Claude Code Plugin Validation

- The `skills` field in `plugin.json` must be a path to a parent directory (e.g., `"./skills"`), not an array or a direct skill path.
- Skills must be in `<skills-dir>/<skill-name>/SKILL.md` structure.

### Cursor Plugin

- Does not require a `skills` field — auto-discovers from `skills/` directory.
- Supports a `displayName` field for human-friendly naming.

### Codex CLI

- The skill installer copies a specific directory path from a GitHub repo — it does not install the whole repo. It needs a path containing `SKILL.md`.
- Installs are one-time copies to `~/.codex/skills/`. No auto-update. To update: remove the directory and reinstall.
- The installer refuses to overwrite an existing destination.
- Scans multiple directories for skills (cwd, parents, repo root, `~/.codex/skills/`, `/etc/codex/skills/`). Duplicate `name` values across locations are not merged — both appear.
- `agents/openai.yaml` provides UI metadata (display name, brand color, icon, default prompt, MCP tool dependencies).

## Architecture Decision: Why Not Root-Level SKILL.md?

Manus expects `SKILL.md` at the root (or in subfolders for multi-skill repos). Claude Code and Cursor expect it under `skills/<name>/`. We considered flattening to root but:

1. Claude Code's `skills` field requires a parent directory containing skill subdirectories — a root-level skill breaks validation.
2. Manus has no auto-update from repos anyway, so there's no advantage to making the repo directly importable by Manus.

The solution: the repo structure serves Claude Code and Cursor natively, and CI produces a processed zip for everything else.
