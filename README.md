# claude-daily-summary

A Claude Code skill that reads your daily conversations and summarizes the knowledge you've learned into a structured review report — so you never forget what Claude taught you.

## How It Works

1. **Extract**: A Python script parses your Claude Code conversation logs (`~/.claude/projects/`) and extracts clean Q&A pairs
2. **Summarize**: Claude analyzes the extracted conversations and identifies key knowledge, concepts, and insights
3. **Report**: Generates a Markdown report with topic summaries, flashcard-style review questions, and key takeaways

## Setup

1. Clone this repo and `cd` into it:
   ```bash
   git clone https://github.com/lixiaochuan2020/claude-daily-summary.git
   cd claude-daily-summary
   ```

2. That's it — no dependencies to install. The extraction script uses Python stdlib only, and Claude does the summarization directly.

## Usage

### As a Claude Code Skill

From within this project directory in Claude Code, run:

```
/daily-summary
```

Or with a specific date:

```
/daily-summary 2026-03-10
```

Or filter to a specific project:

```
/daily-summary 2026-03-10 myproject
```

### Standalone Extraction Script

You can also run the extraction script directly to see your raw Q&A pairs:

```bash
# Today's conversations
python3 scripts/extract_conversations.py

# Specific date
python3 scripts/extract_conversations.py --date 2026-03-10

# Filter by project
python3 scripts/extract_conversations.py --date 2026-03-10 --project myproject

# Include subagent conversations
python3 scripts/extract_conversations.py --date 2026-03-10 --include-subagents
```

## Output

Reports are saved to `reports/YYYY-MM-DD-summary.md` and include:

- **Topic summaries** with key concepts and practical details
- **Flashcard-style Q&A** for spaced repetition review
- **Key takeaways** highlighting the most important insights
- **Raw Q&A log** (collapsible) for reference

## Project Structure

```
claude-daily-summary/
├── .claude/skills/daily-summary/
│   └── SKILL.md                       # Claude Code skill definition
├── scripts/
│   └── extract_conversations.py       # JSONL log parser
├── reports/                           # Generated reports (gitignored)
├── .gitignore
└── README.md
```

## Optional: Daily Cron Job

To auto-generate a report every evening:

```bash
# Edit crontab
crontab -e

# Add this line (runs at 11 PM daily)
0 23 * * * cd /path/to/claude-daily-summary && python3 scripts/extract_conversations.py > /tmp/daily_qa.txt 2>/dev/null
```

Note: The cron job only runs the extraction. For the full AI-summarized report, use the `/daily-summary` skill interactively.
