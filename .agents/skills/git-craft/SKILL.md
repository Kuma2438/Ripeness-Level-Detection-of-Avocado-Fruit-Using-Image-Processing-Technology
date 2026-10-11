---
name: git-craft
description: >-
  Use this skill when reviewing git status, staging files, authoring semantic
  commits, and maintaining CHANGELOG.md. Enforces Conventional Commits, prevents
  accidental secret leaks, ensures atomic changes, and summarizes diffs accurately.
---

# Git Craft: Semantic Commits & Release Hygiene

Guidelines for clean, semantic Git history, atomic commits, and automated changelog tracking.

---

## 1. Pre-Commit Inspection & Secret Screening

Before staging or committing, always inspect working directory state:

1. **Check Status & Diffs:**
   - Run `git status` to identify modified and untracked files.
   - Run `git diff` to review exact changes.
2. **Strict Secret & Noise Prevention:**
   - **Never commit:** `.env`, API keys, private tokens, passwords, database credentials.
   - **Never commit:** Temporary data files, cache folders (`__pycache__`, `.pytest_cache`), large raw binaries, or IDE-specific settings.
   - If sensitive or temporary files are untracked, add them to `.gitignore` first before staging.
3. **Atomic Changes:**
   - Group related edits together. Do not mix unrelated refactoring, feature work, and formatting fixes into a single commit.

---

## 2. Conventional Commits Standard

All commit messages must strictly adhere to the [Conventional Commits](https://www.conventionalcommits.org/) specification:

### Format
```text
<type>(<scope>): <short imperative summary>

[optional body explaining motivation and why the change was made]

[optional footer, e.g. Closes #123]
```

### Commit Types
- **`feat`**: A new feature, script, or capability.
- **`fix`**: A bug fix or error correction.
- **`perf`**: Code change that improves performance or memory usage without altering behavior.
- **`refactor`**: Code restructuring that neither fixes a bug nor adds a feature.
- **`docs`**: Documentation or README changes only.
- **`test`**: Adding, updating, or fixing tests.
- **`chore`**: Build process, package dependencies, gitignore, or configuration updates.

### Subject Line Rules
- Use the imperative present tense: `"add"`, `"fix"`, `"optimize"` (never *"added"*, *"fixes"*, *"optimizing"*).
- Lowercase subject line; do NOT put a trailing period at the end.
- Keep the first line under 72 characters.
- Example: `feat(pipeline): add chunked csv processing for large sales datasets`

---

## 3. CHANGELOG.md Maintenance

When delivering a major feature, fix, or release, update or create `CHANGELOG.md` following [Keep a Changelog](https://keepachangelog.com/):

```markdown
# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Feature description...

### Changed
- Refactored logic...

### Fixed
- Bug fix description...

### Performance
- Memory reduction or speed improvement...
```
