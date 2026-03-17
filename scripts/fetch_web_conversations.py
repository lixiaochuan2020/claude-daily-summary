#!/usr/bin/env python3
"""
Fetch today's conversations from claude.ai using the internal API.

Requires a session cookie stored in ~/.config/claude-daily-summary/config.json:
{
    "claude_session_key": "sk-ant-sid01-..."
}

Output: /tmp/daily-summary-web-conversations.json

Uses `requests` via uv-managed environment.
"""

import json
import sys
from datetime import datetime, date
from pathlib import Path

import requests

CONFIG_PATH = Path.home() / ".config" / "claude-daily-summary" / "config.json"
OUTPUT_PATH = "/tmp/daily-summary-web-conversations.json"
BASE_URL = "https://claude.ai"


def load_config() -> dict:
    """Load configuration with session key."""
    if not CONFIG_PATH.exists():
        print(f"Config not found at {CONFIG_PATH}", file=sys.stderr)
        print("Create it with:", file=sys.stderr)
        print(f"  mkdir -p {CONFIG_PATH.parent}", file=sys.stderr)
        print(f'  echo \'{{"claude_session_key": "YOUR_KEY_HERE"}}\' > {CONFIG_PATH}', file=sys.stderr)
        print("", file=sys.stderr)
        print("To get your session key:", file=sys.stderr)
        print("  1. Go to https://claude.ai/chats", file=sys.stderr)
        print("  2. Open DevTools (F12) > Application > Cookies > claude.ai", file=sys.stderr)
        print("  3. Copy the 'sessionKey' value", file=sys.stderr)
        sys.exit(1)

    with open(CONFIG_PATH) as f:
        config = json.load(f)

    if not config.get("claude_session_key") or config["claude_session_key"] == "YOUR_KEY_HERE":
        print("Error: Please set a valid claude_session_key in config.json", file=sys.stderr)
        sys.exit(1)

    return config


def make_session(session_key: str) -> requests.Session:
    """Create a requests session with auth headers."""
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Referer": f"{BASE_URL}/chats",
        "Cookie": f"sessionKey={session_key}",
    })
    return s


def api_get(session: requests.Session, path: str, timeout: int = 30) -> dict:
    """Make a GET request to the claude.ai API."""
    resp = session.get(f"{BASE_URL}{path}", timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def filter_today_conversations(conversations: list[dict], target_date: date) -> list[dict]:
    """Filter conversations that were active today."""
    today_convs = []
    for conv in conversations:
        updated = conv.get("updated_at", "")
        if not updated:
            continue
        try:
            conv_date = datetime.fromisoformat(
                updated.replace("Z", "+00:00")
            ).date()
        except (ValueError, TypeError):
            continue
        if conv_date == target_date:
            today_convs.append(conv)
    return today_convs


def extract_messages(conv_data: dict, target_date: date) -> list[dict]:
    """Extract user and assistant messages from a conversation."""
    messages = []
    for msg in conv_data.get("chat_messages", []):
        sender = msg.get("sender", "")
        if sender not in ("human", "assistant"):
            continue

        text = msg.get("text", "")
        if not text or not text.strip():
            continue

        # Filter by message date
        created = msg.get("created_at", "")
        if created:
            try:
                msg_date = datetime.fromisoformat(
                    created.replace("Z", "+00:00")
                ).date()
                if msg_date != target_date:
                    continue
            except (ValueError, TypeError):
                pass

        role = "user" if sender == "human" else "assistant"
        messages.append({
            "role": role,
            "content": text[:5000],  # Truncate very long messages
            "timestamp": created,
            "session_id": conv_data.get("uuid", ""),
        })
    return messages


def main():
    target_date = date.today()
    if len(sys.argv) > 1:
        target_date = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()

    config = load_config()
    session = make_session(config["claude_session_key"])

    print(f"Fetching conversations from claude.ai for {target_date}...")

    try:
        orgs = api_get(session, "/api/organizations", timeout=15)
    except requests.HTTPError as e:
        if e.response.status_code in (401, 403):
            print("Error: Session key is invalid or expired. Please update config.json", file=sys.stderr)
            print("See instructions: open DevTools > Application > Cookies on claude.ai", file=sys.stderr)
        else:
            print(f"Error fetching organizations: HTTP {e.response.status_code}", file=sys.stderr)
        sys.exit(1)
    except requests.ConnectionError as e:
        print(f"Error connecting to claude.ai: {e}", file=sys.stderr)
        sys.exit(1)

    if not orgs:
        print("Error: No organizations found", file=sys.stderr)
        sys.exit(1)

    org_id = orgs[0]["uuid"]

    conversations = api_get(session, f"/api/organizations/{org_id}/chat_conversations")
    today_convs = filter_today_conversations(conversations, target_date)

    if not today_convs:
        print(f"No web conversations found for {target_date}")
        output = {
            "date": str(target_date),
            "source": "claude.ai",
            "total_messages": 0,
            "total_conversations": 0,
            "conversations": [],
        }
        with open(OUTPUT_PATH, "w") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print(f"Output written to {OUTPUT_PATH}")
        return

    print(f"Found {len(today_convs)} conversations updated today. Fetching details...")

    all_conversations = []
    total_messages = 0

    for conv in today_convs:
        conv_id = conv["uuid"]
        conv_name = conv.get("name", "Untitled")

        try:
            full_conv = api_get(
                session,
                f"/api/organizations/{org_id}/chat_conversations/{conv_id}",
            )
        except (requests.HTTPError, requests.ConnectionError) as e:
            print(f"  Warning: Could not fetch '{conv_name}': {e}", file=sys.stderr)
            continue

        messages = extract_messages(full_conv, target_date)
        if not messages:
            continue

        all_conversations.append({
            "name": conv_name,
            "uuid": conv_id,
            "message_count": len(messages),
            "messages": messages,
        })
        total_messages += len(messages)
        print(f"  '{conv_name}': {len(messages)} messages")

    output = {
        "date": str(target_date),
        "source": "claude.ai",
        "total_messages": total_messages,
        "total_conversations": len(all_conversations),
        "conversations": all_conversations,
    }

    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Fetched {total_messages} messages from {len(all_conversations)} web conversations")
    print(f"Output written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
