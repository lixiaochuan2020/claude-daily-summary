# claude-daily-summary

A Claude Code skill that reads your daily conversations (local + web) and summarizes your acquired knowledge into a beautifully typeset PDF with inline diagrams.

## Features

- Scans all local Claude Code conversation history from today
- Fetches today's conversations from claude.ai (web, optional)
- Extracts key learnings, new concepts, useful commands, and problems solved
- Generates a Typst document with inline `fletcher` diagrams for complex concepts
- Compiles to a styled PDF at `~/Documents/daily-summaries/YYYY-MM-DD.pdf`

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) — Claude's CLI coding agent
- [uv](https://docs.astral.sh/uv/) — Python package manager
- [typst](https://typst.app/) — Modern typesetting system

**macOS:**
```bash
brew install uv typst
```

**Linux:**
```bash
# uv
curl -LsSf https://astral.sh/uv/install.sh | sh
# typst (via cargo, or download from https://github.com/typst/typst/releases)
cargo install typst-cli
```

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/claude-daily-summary.git
cd claude-daily-summary
bash install.sh
```

The install script will:
1. Copy the skill definition to `~/.claude/skills/daily-summary/`
2. Save the project path to `~/.config/claude-daily-summary/config.json`
3. Sync Python dependencies

### Configure web conversations (optional)

To include conversations from claude.ai (not just local Claude Code sessions), provide your session cookie:

1. Open https://claude.ai/chats in your browser (make sure you're logged in)
2. Open DevTools: `Cmd+Option+I` (Mac) or `F12` (Windows/Linux)
3. Go to **Application** tab > **Cookies** > `https://claude.ai`
4. Find the cookie named `sessionKey` and copy its value (starts with `sk-ant-sid01-...`)
5. Edit `~/.config/claude-daily-summary/config.json` and set `claude_session_key`

> **Important:** Keep this file private. The session key grants full access to your claude.ai account.

## Usage

In any Claude Code session, type:

```
/daily-summary
```

The skill will:
1. Parse today's local conversations from `~/.claude/projects/`
2. Fetch today's web conversations from claude.ai (if configured)
3. Extract and summarize key learnings
4. Generate a Typst document with inline diagrams
5. Compile to PDF at `~/Documents/daily-summaries/YYYY-MM-DD.pdf`

### Run scripts directly

```bash
# Parse local conversations only
uv run scripts/parse_conversations.py

# Parse a specific date
uv run scripts/parse_conversations.py 2026-03-15

# Fetch web conversations
uv run scripts/fetch_web_conversations.py

# Compile Typst to PDF
bash scripts/generate_pdf.sh /tmp/daily-summary-2026-03-16.typ
```

## Important Notes

### Session key expiration

The claude.ai session key **expires periodically** (typically every few weeks). When it expires, the web fetcher will print an error and the skill will proceed with local conversations only. Repeat the session key setup with a fresh key to restore web conversation fetching.

### Privacy

- All data stays local. Nothing is sent to external services.
- The session key config file is stored at `~/.config/claude-daily-summary/config.json` — make sure it's not accidentally committed or shared.
- Conversation data is written to `/tmp/` (auto-cleaned on reboot).

### Typst and diagrams

- PDF generation uses [Typst](https://typst.app/), a modern typesetting system with native Unicode/CJK support
- Inline diagrams use the [fletcher](https://typst.app/universe/package/fletcher/) package (auto-downloaded on first compile)
- Diagrams are only added for topics that genuinely benefit from visual explanation
- The template (`templates/daily-summary.typ`) defines the color scheme, layout, and reusable components

## Project Structure

```
claude-daily-summary/
├── scripts/
│   ├── parse_conversations.py      # Parse local Claude Code JSONL sessions
│   ├── fetch_web_conversations.py  # Fetch conversations from claude.ai API
│   └── generate_pdf.sh             # Typst → PDF compilation (cross-platform)
├── templates/
│   ├── daily-summary.typ           # Typst template (layout, colors, components)
│   └── daily-summary.md            # Legacy Markdown template
├── skill/
│   ├── SKILL.md                    # Skill definition (copied to ~/.claude/skills/ on install)
│   └── references/
│       └── EXTRACTION_GUIDE.md     # Knowledge extraction guidelines
├── install.sh                       # One-command installer
├── pyproject.toml                   # Python project config (uv)
└── README.md
```

**After installation, these are created:**

```
~/.claude/skills/daily-summary/
├── SKILL.md                         # Skill definition (triggers, workflow)
└── references/
    └── EXTRACTION_GUIDE.md          # Knowledge extraction guidelines

~/.config/claude-daily-summary/
└── config.json                      # Install path + session key config

~/Documents/daily-summaries/
└── YYYY-MM-DD.pdf                   # Generated PDF output
```

## Uninstall

```bash
rm -rf ~/.claude/skills/daily-summary
rm -rf ~/.config/claude-daily-summary
```
