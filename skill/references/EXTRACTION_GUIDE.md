# Knowledge Extraction Guide

## Purpose

This guide helps identify meaningful learnings from Claude conversation history. The goal is to surface what the user actually learned, not just what they did.

## What Counts as a Learning

### Include
- **New concepts**: Something the user asked about that they didn't know before
- **Aha moments**: When the user's understanding was corrected or deepened
- **New tools/commands**: Commands, tools, or techniques the user hadn't used before
- **Problem-solving patterns**: How a tricky problem was diagnosed and solved
- **Architecture decisions**: Design choices and their rationale
- **Configuration knowledge**: Setup steps, config options, environment details
- **Best practices**: Coding patterns, security practices, or workflow improvements

### Exclude
- Routine operations (git add, commit, push)
- Simple file reads/writes without learning context
- Tool invocations that are just mechanical steps
- Repeated questions about the same thing (consolidate into one learning)
- Plan mode discussions (unless they contain architectural insights)

## How to Identify User Questions

User messages that indicate learning:
- Questions starting with "how", "why", "what is", "can I", "should I"
- Messages expressing confusion: "I don't understand", "this doesn't work"
- Requests for explanation: "explain", "what does X mean"
- Debugging requests: "why is this failing", "what's wrong with"

## How to Extract Knowledge Points

For each meaningful exchange:

1. **Identify the topic**: What subject area does this cover?
2. **State the learning**: What did the user learn? Write it as a concise bullet point.
3. **Include context**: If a code snippet or command was key, include it.
4. **Note the project**: Which project was this conversation about?

## Grouping Strategy

Group learnings by:
1. **Project** (primary grouping) - Which codebase/project was involved
2. **Topic** (secondary grouping) - Within a project, group related learnings

## Quality Filters

- **Consolidate duplicates**: If the same thing was discussed multiple times, merge into one point
- **Prioritize depth**: A detailed explanation of one concept > five superficial mentions
- **Be specific**: "Learned about git rebase" is bad. "Learned that `git rebase -i` can squash commits to clean up history before PR" is good.
- **Include the 'why'**: Don't just state what was learned, but why it matters when possible

## Output Format

For each learning, produce:

```json
{
  "project": "project-name",
  "topic": "Topic Area",
  "learning": "Concise description of what was learned",
  "type": "concept|command|pattern|debug|config",
  "snippet": "optional code/command snippet"
}
```
