# claude-daily-summary

A Claude Code skill that reads your daily conversations (local + web) and summarizes your acquired knowledge into a beautifully typeset PDF with inline diagrams.

## Features

- Scans all local Claude Code conversation history from today
- Fetches today's conversations from claude.ai (web)
- Extracts key learnings, new concepts, useful commands, and problems solved
- Generates a Typst document with inline `fletcher` diagrams for complex concepts
- Compiles to a styled PDF at `~/Documents/daily-summaries/YYYY-MM-DD.pdf`

## Prerequisites

- [uv](https://docs.astral.sh/uv/) — Python package manager
- [typst](https://typst.app/) — Modern typesetting system (replaces LaTeX/pandoc)

```bash
brew install uv typst
```

## Setup

### 1. Install Python dependencies

```bash
cd ~/Code/claude-daily-summary
uv sync
```

### 2. Configure Claude session key (for web conversations)

To include conversations from claude.ai (not just local Claude Code sessions), you need to provide your session cookie.

**Get your session key:**

1. Open https://claude.ai/chats in your browser (make sure you're logged in)
2. Open DevTools: `Cmd+Option+I` (Mac) or `F12` (Windows/Linux)
3. Go to **Application** tab > **Cookies** > `https://claude.ai`
4. Find the cookie named `sessionKey` and copy its value (starts with `sk-ant-sid01-...`)

**Save it to the config file:**

```bash
mkdir -p ~/.config/claude-daily-summary
cat > ~/.config/claude-daily-summary/config.json << 'EOF'
{
    "claude_session_key": "sk-ant-sid01-PASTE_YOUR_KEY_HERE"
}
EOF
```

> **Important:** Keep this file private. The session key grants full access to your claude.ai account.

### 3. Verify the skill is registered

Open Claude Code and type `/daily-summary`. If it appears in the autocomplete, you're set.

## Usage

In any Claude Code session, run:

```
/daily-summary
```

The skill will:
1. Parse today's local conversations from `~/.claude/projects/`
2. Fetch today's web conversations from claude.ai
3. Extract and summarize key learnings
4. Generate a Typst document with inline diagrams for complex topics
5. Compile to PDF at `~/Documents/daily-summaries/YYYY-MM-DD.pdf`

You can also run the scripts directly:

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

The claude.ai session key **expires periodically** (typically every few weeks). When it expires, the web fetcher will print an error and the skill will proceed with local conversations only. To fix, repeat the session key setup step above with a fresh key.

### Privacy

- All data stays local. Nothing is sent to external services.
- The session key config file is stored at `~/.config/claude-daily-summary/config.json` — make sure it's not accidentally committed or shared.
- Conversation data is written to `/tmp/` (auto-cleaned on reboot).

### Typst and diagrams

- The PDF is generated using [Typst](https://typst.app/), a modern typesetting system with native Unicode/CJK support
- Inline diagrams use the [fletcher](https://typst.app/universe/package/fletcher/) package (auto-downloaded on first compile)
- Diagrams are only added for topics that genuinely benefit from visual explanation
- The template (`templates/daily-summary.typ`) defines the color scheme, layout, and reusable components

## Project Structure

```
claude-daily-summary/
├── scripts/
│   ├── parse_conversations.py      # Parse local Claude Code JSONL sessions
│   ├── fetch_web_conversations.py  # Fetch conversations from claude.ai API
│   └── generate_pdf.sh             # Typst → PDF compilation
├── templates/
│   ├── daily-summary.typ           # Typst template (layout, colors, components)
│   └── daily-summary.md            # Legacy Markdown template
├── pyproject.toml                   # uv project config
└── README.md

~/.claude/skills/daily-summary/
├── SKILL.md                         # Skill definition (triggers, workflow)
└── references/
    └── EXTRACTION_GUIDE.md          # Knowledge extraction guidelines

~/.config/claude-daily-summary/
└── config.json                      # Session key config
```
