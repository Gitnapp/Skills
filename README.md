# Skills

A collection of reusable skills for AI assistants.

## Available Skills

### xcode-github-release

Step-by-step process for bumping a version in Xcode and publishing a GitHub Release manually in a typical macOS workspace environment.

**Use when:** Creating a new release of a macOS Xcode application, including bumping version codes, building the binary, and publishing via GitHub CLI.

## Structure

```
Skills/
├── <skill-name>/
│   └── SKILL.md    # Skill definition and instructions
```

## Usage

Each skill is self-contained in its own directory with a `SKILL.md` file that includes:
- YAML frontmatter with `name` and `description`
- Detailed instructions and steps
- Prerequisites and potential pitfalls

## Contributing

Feel free to add new skills by creating a new directory with a `SKILL.md` file following the existing structure.
