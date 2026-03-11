#!/usr/bin/env python3
"""Extract clean Q&A pairs from Claude Code conversation logs (JSONL).

Scans ~/.claude/projects/ for session logs, filters by date, and prints
structured Q&A text to stdout for summarization.

Usage:
    python3 extract_conversations.py --date 2026-03-10
    python3 extract_conversations.py --date 2026-03-10 --project myproject
    python3 extract_conversations.py --date 2026-03-10 --include-subagents
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


CLAUDE_PROJECTS_DIR = Path.home() / ".claude" / "projects"


def find_session_files(projects_dir: Path, project_filter: str | None = None) -> list[Path]:
    """Find all top-level JSONL session files in the projects directory."""
    if not projects_dir.exists():
        return []

    files = []
    for project_dir in projects_dir.iterdir():
        if not project_dir.is_dir():
            continue
        if project_filter and project_filter not in project_dir.name:
            continue
        for jsonl_file in project_dir.glob("*.jsonl"):
            files.append(jsonl_file)
    return sorted(files)


def find_subagent_files(session_file: Path) -> list[Path]:
    """Find subagent JSONL files associated with a session."""
    session_id = session_file.stem
    subagents_dir = session_file.parent / session_id / "subagents"
    if not subagents_dir.exists():
        return []
    return sorted(subagents_dir.glob("*.jsonl"))


def parse_records(jsonl_path: Path) -> list[dict]:
    """Parse a JSONL file into a list of records."""
    records = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


def filter_by_date(records: list[dict], target_date: str) -> list[dict]:
    """Keep only records whose timestamp matches the target date (YYYY-MM-DD)."""
    filtered = []
    for record in records:
        ts = record.get("timestamp", "")
        if not ts:
            continue
        try:
            record_date = ts[:10]  # "2026-03-10T03:20:16.840Z" -> "2026-03-10"
            if record_date == target_date:
                filtered.append(record)
        except (ValueError, IndexError):
            continue
    return filtered


def extract_qa_pairs(records: list[dict]) -> list[dict]:
    """Extract clean Q&A pairs from parsed records.

    Returns list of dicts: {"role": "user"|"assistant", "text": "..."}
    """
    messages = []
    for record in records:
        rec_type = record.get("type", "")

        # Skip non-message records
        if rec_type == "queue-operation":
            continue
        if rec_type == "progress":
            continue

        msg = record.get("message")
        if not msg:
            continue

        role = msg.get("role", "")
        content = msg.get("content", "")

        if role == "user":
            # Only include real user questions (string content)
            # Skip tool_result arrays (those are tool outputs, not user questions)
            if isinstance(content, str) and content.strip():
                messages.append({"role": "user", "text": content.strip()})

        elif role == "assistant":
            # Extract only text blocks from content array
            if isinstance(content, list):
                texts = []
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        text = block.get("text", "").strip()
                        if text:
                            texts.append(text)
                if texts:
                    messages.append({"role": "assistant", "text": "\n\n".join(texts)})
            elif isinstance(content, str) and content.strip():
                messages.append({"role": "assistant", "text": content.strip()})

    return messages


def get_project_name(session_file: Path) -> str:
    """Derive a readable project name from the project directory name."""
    # Directory name is like "-home-user-myproject" -> "myproject"
    dir_name = session_file.parent.name
    parts = dir_name.strip("-").split("-")
    # Take last meaningful segment(s)
    # Skip common prefixes like "home", "user", "Users", username
    skip = {"home", "users", "user", "root"}
    meaningful = [p for p in parts if p.lower() not in skip]
    return "-".join(meaningful) if meaningful else dir_name


def get_session_timestamp(records: list[dict]) -> str:
    """Get the earliest timestamp from records."""
    for record in records:
        ts = record.get("timestamp", "")
        if ts:
            return ts
    return "unknown"


def format_output(session_file: Path, messages: list[dict], records: list[dict]) -> str:
    """Format extracted messages into readable output."""
    if not messages:
        return ""

    project = get_project_name(session_file)
    session_id = session_file.stem
    timestamp = get_session_timestamp(records)

    lines = []
    lines.append(f"=== Session: {session_id[:8]}... | Project: {project} | {timestamp} ===")
    lines.append("")

    for msg in messages:
        role_tag = "[USER]" if msg["role"] == "user" else "[ASSISTANT]"
        lines.append(f"{role_tag} {msg['text']}")
        lines.append("")

    lines.append("=== End Session ===")
    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Extract Q&A pairs from Claude Code conversation logs"
    )
    parser.add_argument(
        "--date",
        default=datetime.now().strftime("%Y-%m-%d"),
        help="Target date in YYYY-MM-DD format (default: today)",
    )
    parser.add_argument(
        "--project",
        default=None,
        help="Filter by project name (substring match)",
    )
    parser.add_argument(
        "--include-subagents",
        action="store_true",
        help="Include subagent conversations",
    )
    parser.add_argument(
        "--logs-dir",
        default=str(CLAUDE_PROJECTS_DIR),
        help=f"Path to Claude projects directory (default: {CLAUDE_PROJECTS_DIR})",
    )
    args = parser.parse_args()

    projects_dir = Path(args.logs_dir)
    if not projects_dir.exists():
        print(f"Error: Projects directory not found: {projects_dir}", file=sys.stderr)
        sys.exit(1)

    session_files = find_session_files(projects_dir, args.project)
    if not session_files:
        print(f"No session files found in {projects_dir}", file=sys.stderr)
        sys.exit(0)

    total_sessions = 0
    total_messages = 0

    for session_file in session_files:
        # Parse and filter main session
        records = parse_records(session_file)
        day_records = filter_by_date(records, args.date)
        if not day_records:
            continue

        messages = extract_qa_pairs(day_records)
        if messages:
            output = format_output(session_file, messages, day_records)
            print(output)
            total_sessions += 1
            total_messages += len(messages)

        # Optionally include subagent conversations
        if args.include_subagents:
            for sub_file in find_subagent_files(session_file):
                sub_records = parse_records(sub_file)
                sub_day_records = filter_by_date(sub_records, args.date)
                if not sub_day_records:
                    continue
                sub_messages = extract_qa_pairs(sub_day_records)
                if sub_messages:
                    output = format_output(sub_file, sub_messages, sub_day_records)
                    print(output)
                    total_sessions += 1
                    total_messages += len(sub_messages)

    # Print summary to stderr
    print(f"\n--- Extracted {total_messages} messages from {total_sessions} sessions for {args.date} ---", file=sys.stderr)


if __name__ == "__main__":
    main()
