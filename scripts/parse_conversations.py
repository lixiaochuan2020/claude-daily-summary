#!/usr/bin/env python3
"""
Parse Claude Code conversation history and extract today's messages.

Scans all JSONL session files under ~/.claude/projects/*/
and extracts user questions and assistant responses from today.

Output: /tmp/daily-summary-conversations.json
"""

import json
import os
import sys
from datetime import datetime, date
from pathlib import Path
from typing import Optional


def get_target_date() -> date:
    """Get the target date from CLI arg or default to today."""
    if len(sys.argv) > 1:
        return datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
    return date.today()


def project_name_from_path(path: str) -> str:
    """Extract a readable project name from the projects directory path.

    Claude Code stores projects with path-encoded directory names, e.g.:
      '-Users-alice-Code-my-project' -> 'my-project'
      '-Users-alice--config-ghostty' -> 'config/ghostty'
      '-Users-alice-Code'            -> '~/Code'
    """
    dirname = os.path.basename(path)
    # The dirname represents a filesystem path with dashes replacing slashes
    # e.g. '-Users-lxc-Code-my-project' represents /Users/lxc/Code/my-project
    # Double dashes represent paths with dots like .config -> --config

    # Reconstruct the original path
    # Replace leading dash, then split on single dashes (not double)
    clean = dirname.lstrip("-")

    # Try to find "Code" segment and take everything after it
    # Handle the path: Users/lxc/Code/project-name
    parts = clean.split("-")

    # Find last occurrence of known directory markers
    for marker in ("Code", "Downloads", "Documents", "Desktop"):
        for i, part in enumerate(parts):
            if part == marker:
                remainder = "-".join(parts[i + 1:]) if i + 1 < len(parts) else ""
                return remainder if remainder else f"~/{marker}"

    # Handle dot-prefixed dirs (double-dash = dot)
    # e.g. Users-lxc--config-ghostty -> .config/ghostty
    if "--" in clean:
        # Everything after username (parts[0]=Users, parts[1]=username)
        after_user = "-".join(parts[2:]) if len(parts) > 2 else clean
        return after_user.replace("--", "/.").lstrip("-")

    # Fallback: last 2 parts
    if len(parts) > 3:
        return "-".join(parts[-2:])
    return clean


def extract_text_content(content) -> str:
    """Extract text from message content (string or list of blocks)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        texts = []
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text":
                    texts.append(block.get("text", ""))
                elif block.get("type") == "tool_result":
                    # Skip tool results for summary purposes
                    pass
        return "\n".join(texts)
    return ""


def parse_jsonl_file(filepath: str, target_date: date) -> list[dict]:
    """Parse a JSONL file and extract messages from the target date."""
    messages = []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                # Only process user and assistant messages
                msg_type = entry.get("type")
                if msg_type not in ("user", "assistant"):
                    continue

                # Check timestamp
                timestamp_str = entry.get("timestamp", "")
                if not timestamp_str:
                    continue

                try:
                    msg_date = datetime.fromisoformat(
                        timestamp_str.replace("Z", "+00:00")
                    ).date()
                except (ValueError, TypeError):
                    continue

                if msg_date != target_date:
                    continue

                # Extract message content
                message = entry.get("message", {})
                role = message.get("role", msg_type)
                content = extract_text_content(message.get("content", ""))

                # Skip empty messages and tool-only messages
                if not content.strip():
                    continue

                # Skip very short assistant messages (likely just tool calls)
                if role == "assistant" and len(content.strip()) < 20:
                    continue

                messages.append({
                    "role": role,
                    "content": content[:5000],  # Truncate very long messages
                    "timestamp": timestamp_str,
                    "session_id": entry.get("sessionId", ""),
                })
    except (OSError, IOError) as e:
        print(f"Warning: Could not read {filepath}: {e}", file=sys.stderr)

    return messages


def main():
    target_date = get_target_date()
    projects_dir = Path.home() / ".claude" / "projects"

    if not projects_dir.exists():
        print(json.dumps({"error": "No projects directory found", "date": str(target_date)}))
        sys.exit(1)

    results = {}
    total_messages = 0

    # Scan all project directories
    for project_dir in sorted(projects_dir.iterdir()):
        if not project_dir.is_dir():
            continue

        project_name = project_name_from_path(str(project_dir))
        project_messages = []

        # Find all JSONL files in this project
        for jsonl_file in project_dir.glob("*.jsonl"):
            messages = parse_jsonl_file(str(jsonl_file), target_date)
            if messages:
                project_messages.extend(messages)

        if project_messages:
            # Sort by timestamp
            project_messages.sort(key=lambda m: m["timestamp"])
            results[project_name] = {
                "project_path": str(project_dir),
                "message_count": len(project_messages),
                "sessions": list(set(m["session_id"] for m in project_messages)),
                "messages": project_messages,
            }
            total_messages += len(project_messages)

    output = {
        "date": str(target_date),
        "total_messages": total_messages,
        "total_projects": len(results),
        "projects": results,
    }

    output_path = "/tmp/daily-summary-conversations.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Parsed {total_messages} messages from {len(results)} projects for {target_date}")
    print(f"Output written to {output_path}")


if __name__ == "__main__":
    main()
