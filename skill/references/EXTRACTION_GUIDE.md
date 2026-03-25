# Knowledge Extraction Guide

## Purpose

Extract **transferable knowledge** from Claude conversations — things you could teach someone else or apply in a different context. This is NOT an activity log. Never describe what was built or debugged; describe what was **learned** in the process.

## The Core Question

For every conversation, ask: **"If I had this same type of problem again in 6 months, what would I wish I remembered?"**

If the answer is nothing — skip it entirely.

## What Counts as Knowledge

### Include — Transferable Insights
- **Concepts**: A mental model, principle, or idea you didn't know before (e.g., "Typst compiles with `--root /` to allow absolute path imports")
- **Aha moments**: When your understanding was corrected or deepened (e.g., "uv is cross-platform — the platform-dependent part is actually typst installation, not uv")
- **Techniques**: A reusable approach, pattern, or command you hadn't used before
- **Design rationale**: *Why* a certain approach is better than alternatives (not *that* you chose it)
- **Gotchas**: Surprising behavior, common pitfalls, or non-obvious constraints

### Exclude — Activity and Process
- What was built, fixed, or implemented (that's a changelog, not learning)
- Step-by-step development process ("first I created X, then modified Y")
- Bug descriptions and their fixes (unless the root cause reveals a transferable insight)
- File-by-file change descriptions
- Git operations, deployment steps, routine commands
- Plan mode discussions, code review iterations
- Project management decisions (branch naming, PR creation, etc.)

## Examples

### BAD (activity log)
- "Created a Notion integration script that fetches vocabulary words"
- "Fixed a bug where the date filter wasn't working in the query"
- "Updated install.sh to include Notion config fields"
- "Added a vocab-card component to the Typst template"

### GOOD (transferable knowledge)
- "Notion API requires `Notion-Version` header — without it, requests silently return empty results"
- "Notion block children API paginates at 100 blocks — must loop with `start_cursor` to get all content"
- "`uv` is cross-platform (macOS/Linux/Windows), but `typst` installation is platform-dependent (`brew` on macOS, `cargo` or binary download on Linux)"
- "For a project with only one dependency (`requests`), `uv` adds overhead — could use stdlib `urllib.request` instead for zero tooling"

## Brevity Rules

- **One bullet point per insight**, not per conversation
- Each bullet should be 1-2 sentences max
- If you can't state the learning in 2 sentences, you're describing process, not knowledge
- Aim for **5-15 total learnings** for a full day, not 30+
- A day with 3 deep insights is better than 20 shallow ones

## Grouping Strategy

Group by **knowledge domain** (not by project or conversation):
- e.g., "Typst & PDF Generation", "Notion API", "Git Workflows", "Python Packaging"
- Only create a group if it has 2+ learnings; otherwise fold into a general section

## Quality Filters

- **The "so what?" test**: After writing a learning, ask "so what?" If you can't answer why it matters, cut it.
- **The "would I Google this?" test**: If you'd search for this info again later, it's worth including.
- **Consolidate**: If 5 conversations touched the same topic, produce 1-2 bullet points, not 5.
- **Be specific**: "Learned about Notion API" is useless. "Notion API date filters use ISO 8601 format in the `equals` field" is useful.
