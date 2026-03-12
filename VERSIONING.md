# Versioning

This project uses [Semantic Versioning](https://semver.org/) (`MAJOR.MINOR.PATCH`).

## Version Locations

Update the version in **all three** files:

1. `.claude-plugin/plugin.json` → `"version"` field
2. `SKILL.md` → `metadata.version` in YAML frontmatter
3. `pyproject.toml` → `version` field under `[project]`

## Release Process

```bash
# 1. Bump version in both files above
# 2. Commit
git commit -am "chore: bump version to X.Y.Z"
# 3. Tag and push
git tag vX.Y.Z
git push origin main --tags
```

CI automatically creates a GitHub Release with platform-specific zips.
