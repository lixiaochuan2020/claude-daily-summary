---
name: daily-summary
description: >
  Generate a PDF summarizing today's learning from Claude conversations.
  Use when user says "daily summary", "daily-summary", "summarize my day",
  "what did I learn today", or "今日总结". Scans all Claude conversation
  history from today, extracts key learnings, and produces a PDF report
  with inline diagrams using Typst.
metadata:
  author: community
  version: "2.1.0"
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Task
---

# Daily Summary Generator

Generate a beautifully typeset PDF summarizing today's learning from Claude Code conversations, using Typst with inline fletcher diagrams.

## Overview

This skill scans all Claude conversation history from today, extracts knowledge and learnings, generates a Typst document with diagrams, and compiles it to PDF.

## Workflow

### Step 0: Locate Project Directory

Read the config file to find the installation directory:

```bash
cat ~/.config/claude-daily-summary/config.json
```

Extract the `install_dir` value — this is `$PROJECT_DIR` for all subsequent steps.

If the config file doesn't exist or `install_dir` is missing, look for the project in common locations:
```bash
# Check common locations
for dir in "$HOME/Code/claude-daily-summary" "$HOME/code/claude-daily-summary" "$HOME/projects/claude-daily-summary" "$HOME/.local/share/claude-daily-summary"; do
  [ -d "$dir" ] && echo "$dir" && break
done
```

If the project directory cannot be found, inform the user to run the install script first.

### Step 1: Parse Today's Conversations

Run both parsers to extract today's messages from local and web sources:

```bash
cd $PROJECT_DIR && uv run scripts/parse_conversations.py
cd $PROJECT_DIR && uv run scripts/fetch_web_conversations.py
```

- **Local**: Outputs `/tmp/daily-summary-conversations.json` (Claude Code sessions grouped by project)
- **Web**: Outputs `/tmp/daily-summary-web-conversations.json` (claude.ai conversations)

The web fetcher requires a session key in `~/.config/claude-daily-summary/config.json`. If not configured or if the key is expired, it will print an error — proceed with local conversations only and inform the user.

If no conversations are found from either source, inform the user and stop.

### Step 2: Read Parsed Data

Read both output files:
- `/tmp/daily-summary-conversations.json` (local Claude Code conversations)
- `/tmp/daily-summary-web-conversations.json` (claude.ai web conversations)

### Step 3: Read the Template

Read the Typst template to understand available styling functions:
- Template: `$PROJECT_DIR/templates/daily-summary.typ`

The template provides these utilities:
- `daily-summary()` — main document setup (pass date, sessions, projects, web-conversations)
- `#tag("label", color: accent)` — colored tag chips for categorizing topics (e.g., "Web", "Research", "Local")
- `#concept-card("Title")[Description]` — highlighted card for new concepts
- `#problem-solved("Problem", "Solution")` — formatted problem→solution block
- `#snippet-box(lang: "bash")[code]` — optional styled code box (raw code blocks are also styled automatically)

### Step 4: Extract Knowledge & Generate Typst

Read and follow the extraction guidelines in `references/EXTRACTION_GUIDE.md`.

Analyze the parsed conversations and produce a Typst file at `/tmp/daily-summary-YYYY-MM-DD.typ`.

**Document structure:**

```typst
#import "$PROJECT_DIR/templates/daily-summary.typ": *
#import "@preview/fletcher:0.5.8" as fletcher: diagram, node, edge

#show: daily-summary.with(
  date: "YYYY-MM-DD",
  sessions: N,
  projects: ("project1", "project2"),
  web-conversations: M,
)

= Key Learnings

== Topic Name #tag("Web") #tag("Research", color: warning)

=== Subtopic
- Learning point with *bold key terms*
- Another learning point

// Add a fletcher diagram when a concept benefits from visual explanation
#figure(
  diagram(
    node-stroke: 1pt,
    node((0,0), [*Step A*], fill: accent-light, corner-radius: 3pt),
    edge("-|>"),
    node((1,0), [*Step B*], fill: accent-light, corner-radius: 3pt),
  ),
  caption: [Description of what the diagram shows],
)

= New Concepts

#concept-card("Concept Name")[
  Brief explanation of what was learned and why it matters.
]

= Commands & Code Snippets

=== Description of the command
\`\`\`bash
command here
\`\`\`

= Problems Solved

#problem-solved("Problem description", "How it was solved")
```

**IMPORTANT:** In the generated `.typ` file, replace `$PROJECT_DIR` with the actual absolute path from Step 0. The `#import` must use an absolute path since Typst is compiled with `--root /`.

**Diagram guidelines:**
- Use `fletcher` diagrams for architecture flows, pipelines, decision trees, and process diagrams
- Only add diagrams where they genuinely aid comprehension (not every topic needs one)
- Use the template's color variables: `accent-light`, `accent`, `success`, `warning` for consistent styling
- Keep diagrams compact — typically 3-6 nodes max
- Available fletcher arrow marks: `"-|>"` (filled), `"-->"` (dashed), `"..|>"` (dotted), `"hook-->"` (hook)
- Available node options: `fill`, `stroke`, `corner-radius`, `width`, `shape: diamond`

**Tag colors for topic categories:**
- `#tag("Web")` — blue (default) for web conversations
- `#tag("Local")` — blue for local Claude Code sessions
- `#tag("Research", color: warning)` — amber for research topics
- `#tag("Paper", color: success)` — green for paper readings
- `#tag("Debug", color: rgb("#dc2626"))` — red for debugging topics

### Step 5: Compile to PDF

```bash
bash $PROJECT_DIR/scripts/generate_pdf.sh /tmp/daily-summary-YYYY-MM-DD.typ
```

This compiles the Typst file and generates the PDF at `~/Documents/daily-summaries/YYYY-MM-DD.pdf`.

Report the output path to the user and open it:
```bash
open ~/Documents/daily-summaries/YYYY-MM-DD.pdf  # macOS
# or: xdg-open ~/Documents/daily-summaries/YYYY-MM-DD.pdf  # Linux
```

## Error Handling

### No Conversations Found
- Check if the date filter is correct
- Inform the user that no conversations were found for today

### Project Directory Not Found
- Tell the user to run: `bash /path/to/claude-daily-summary/install.sh`

### Typst Not Installed
- macOS: `brew install typst`
- Linux: `cargo install typst-cli` or download from https://github.com/typst/typst/releases
- Then retry PDF compilation

### Typst Compilation Error
- Check the error message — most common issues:
  - Missing `#import` statements
  - Incorrect fletcher version (use `0.5.8`)
  - Unescaped special characters in content (escape `#`, `$`, `@` with `\`)
- Fix the .typ file and recompile

### No Meaningful Learnings
- If conversations are trivial, produce a minimal summary noting "Light conversation day - no significant new learnings"

## Notes

- The skill processes ALL projects under `~/.claude/projects/`
- Messages are filtered by timestamp, not just file modification time
- The summary should be concise but comprehensive
- Focus on what the USER learned, not routine operations
- Code snippets should only include genuinely useful/novel ones
- Add inline diagrams ONLY for topics that genuinely benefit from visual explanation
- Use Typst math mode for formulas: `$F approx 6 N D$`
- The template handles CJK text natively — no special configuration needed
