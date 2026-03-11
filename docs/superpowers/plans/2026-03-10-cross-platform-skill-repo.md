# Cross-Platform Skill Repo Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the transcription-reader skill into a cross-platform GitHub repo with Claude plugin marketplace, ChatGPT compatibility, and CI/CD release pipeline.

**Architecture:** Repo root is the Claude plugin (`.claude-plugin/` with marketplace.json + plugin.json). Skill lives in `skills/transcription-reader/` following the Agent Skills standard. CI/CD on tag push generates generic zips (with `${CLAUDE_SKILL_DIR}` stripped) for non-Claude platforms.

**Tech Stack:** Git, GitHub Actions, Python 3, sed

**Spec:** `docs/superpowers/specs/2026-03-10-cross-platform-skill-repo-design.md`

---

## Chunk 1: Restructure and Configure

### Task 1: Create directory structure and move files

**Files:**
- Create: `skills/transcription-reader/` directory
- Move: `SKILL.md` → `skills/transcription-reader/SKILL.md`
- Move: `scripts/extract-transcript.py` → `skills/transcription-reader/scripts/extract_transcript.py` (rename to underscore)
- Move: `references/stj-format.md` → `skills/transcription-reader/references/stj-format.md`
- Remove: empty `scripts/` and `references/` dirs at root

- [ ] **Step 1: Create skill directory structure**

```bash
mkdir -p skills/transcription-reader/scripts
mkdir -p skills/transcription-reader/references
```

- [ ] **Step 2: Move files to new locations (with script rename)**

```bash
git mv SKILL.md skills/transcription-reader/SKILL.md
git mv scripts/extract-transcript.py skills/transcription-reader/scripts/extract_transcript.py
git mv references/stj-format.md skills/transcription-reader/references/stj-format.md
```

- [ ] **Step 3: Remove empty root directories**

```bash
rmdir scripts references
```

- [ ] **Step 4: Verify structure**

```bash
find . -not -path './.git/*' -not -path './.git' -not -path './docs/*' -type f | sort
```

Expected:
```
./skills/transcription-reader/SKILL.md
./skills/transcription-reader/references/stj-format.md
./skills/transcription-reader/scripts/extract_transcript.py
```

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "refactor: restructure as Agent Skills standard layout

Move skill into skills/transcription-reader/ directory.
Rename extract-transcript.py to extract_transcript.py (Python convention)."
```

### Task 2: Update SKILL.md frontmatter and paths

**Files:**
- Modify: `skills/transcription-reader/SKILL.md`

- [ ] **Step 1: Add frontmatter fields**

Add after the `description` field in the YAML frontmatter:
```yaml
license: MIT
compatibility: Requires Python 3. Optional packages: stjlib (STJ), webvtt-py (VTT), pysubs2 (SRT/ASS/SSA).
metadata:
  author: Yaniv Golan
  version: "1.0.0"
```

- [ ] **Step 2: Replace all script path references**

Replace all occurrences of `SKILL_DIR/scripts/extract_transcript.py` with `${CLAUDE_SKILL_DIR}/scripts/extract_transcript.py` in the SKILL.md body.

Also replace any remaining references to `extract-transcript.py` (hyphen) with `extract_transcript.py` (underscore).

Specifically, these lines need updating:

```
python3 SKILL_DIR/scripts/extract_transcript.py INPUT_FILE [--format FORMAT] [--output OUTPUT_FILE]
```
→
```
python3 ${CLAUDE_SKILL_DIR}/scripts/extract_transcript.py INPUT_FILE [--format FORMAT] [--output OUTPUT_FILE]
```

```
python3 SKILL_DIR/scripts/extract_transcript.py INPUT_FILE --keep-timestamps
```
→
```
python3 ${CLAUDE_SKILL_DIR}/scripts/extract_transcript.py INPUT_FILE --keep-timestamps
```

And the script reference section header line:
```
The bundled `scripts/extract_transcript.py` supports these options:
```
(This one stays as-is — it's a description, not a command.)

- [ ] **Step 3: Verify no stale references remain**

```bash
grep -n 'SKILL_DIR\|extract-transcript' skills/transcription-reader/SKILL.md
```

Expected: no matches.

- [ ] **Step 4: Commit**

```bash
git add skills/transcription-reader/SKILL.md
git commit -m "feat: update SKILL.md for Agent Skills standard

Add license, compatibility, metadata frontmatter fields.
Update script paths to use \${CLAUDE_SKILL_DIR}."
```

### Task 3: Create Claude plugin configuration

**Files:**
- Create: `.claude-plugin/plugin.json`
- Create: `.claude-plugin/marketplace.json`

- [ ] **Step 1: Create .claude-plugin directory**

```bash
mkdir -p .claude-plugin
```

- [ ] **Step 2: Write plugin.json**

Create `.claude-plugin/plugin.json`:
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

- [ ] **Step 3: Write marketplace.json**

Create `.claude-plugin/marketplace.json`:
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

- [ ] **Step 4: Commit**

```bash
git add .claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "feat: add Claude plugin marketplace configuration"
```

### Task 4: Create repo root files

**Files:**
- Create: `LICENSE`
- Create: `.gitignore`
- Create: `README.md`

- [ ] **Step 1: Write MIT LICENSE**

Standard MIT license, copyright 2026 Yaniv Golan.

- [ ] **Step 2: Write .gitignore**

```
__pycache__/
*.pyc
*.pyo
.DS_Store
*.egg-info/
dist/
build/
.env
```

- [ ] **Step 3: Write README.md**

Sections:
1. Header: `# Transcription Reader` + one-line description + badges (MIT license, GitHub release)
2. What it does: reads STJ/VTT/SRT/ASS/SSA, strips timing metadata, outputs clean text
3. Installation:
   - **Claude Desktop** (primary): Customize → Browse Plugins → Personal → + → `yaniv-golan/transcription-reader-skill`
   - **Claude Code** (CLI): `/plugin marketplace add yaniv-golan/transcription-reader-skill`
   - **ChatGPT**: Download generic zip from [Releases] → upload at chatgpt.com/skills
   - **Other tools** (Codex CLI, Cursor, Windsurf, Manus, etc.): Download generic zip → copy to `~/.agents/skills/`
4. Supported formats table (extension, format name, key features)
5. Script usage (extract_transcript.py options)
6. Dependencies (`pip install stjlib webvtt-py pysubs2`)
7. License: MIT

- [ ] **Step 4: Commit**

```bash
git add LICENSE .gitignore README.md
git commit -m "feat: add README, LICENSE (MIT), and .gitignore"
```

## Chunk 2: CI/CD and Push

### Task 5: Create GitHub Actions release workflow

**Files:**
- Create: `.github/workflows/release.yml`

- [ ] **Step 1: Create workflow directory**

```bash
mkdir -p .github/workflows
```

- [ ] **Step 2: Write release.yml**

Create `.github/workflows/release.yml`:

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

permissions:
  contents: write

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Extract version from tag
        id: version
        run: echo "version=${GITHUB_REF#refs/tags/v}" >> "$GITHUB_OUTPUT"

      - name: Build generic zip (non-Claude platforms)
        run: |
          cp -r skills/transcription-reader transcription-reader
          sed -i 's|\${CLAUDE_SKILL_DIR}/||g' transcription-reader/SKILL.md
          zip -r "transcription-reader-v${{ steps.version.outputs.version }}.zip" transcription-reader/
          rm -rf transcription-reader

      - name: Build Claude zip
        run: |
          cp -r skills/transcription-reader transcription-reader
          zip -r "transcription-reader-claude-v${{ steps.version.outputs.version }}.zip" transcription-reader/
          rm -rf transcription-reader

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          generate_release_notes: true
          files: |
            transcription-reader-v${{ steps.version.outputs.version }}.zip
            transcription-reader-claude-v${{ steps.version.outputs.version }}.zip
```

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/release.yml
git commit -m "ci: add release workflow for cross-platform skill zips"
```

### Task 6: Push to GitHub and create first release

- [ ] **Step 1: Push main branch**

```bash
git push -u origin main
```

- [ ] **Step 2: Tag and push v1.0.0**

```bash
git tag v1.0.0
git push origin v1.0.0
```

- [ ] **Step 3: Verify GitHub Actions created the release**

Check https://github.com/yaniv-golan/transcription-reader-skill/releases for:
- `transcription-reader-v1.0.0.zip` (generic)
- `transcription-reader-claude-v1.0.0.zip` (Claude)
- Auto-generated release notes

- [ ] **Step 4: Verify generic zip contents**

Download `transcription-reader-v1.0.0.zip` and confirm SKILL.md uses relative paths (no `${CLAUDE_SKILL_DIR}`).
