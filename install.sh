#!/bin/bash
# Install the daily-summary skill for Claude Code.
#
# This script:
#   1. Copies the skill definition to ~/.claude/skills/daily-summary/
#   2. Saves the project install path to config
#   3. Syncs Python dependencies via uv
#
# Usage: bash install.sh

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$HOME/.claude/skills/daily-summary"
CONFIG_DIR="$HOME/.config/claude-daily-summary"
CONFIG_FILE="$CONFIG_DIR/config.json"

echo "Installing daily-summary skill..."
echo "  Project directory: $PROJECT_DIR"

# 1. Copy skill files
mkdir -p "$SKILL_DIR/references"
cp "$PROJECT_DIR/skill/SKILL.md" "$SKILL_DIR/SKILL.md"
cp "$PROJECT_DIR/skill/references/EXTRACTION_GUIDE.md" "$SKILL_DIR/references/EXTRACTION_GUIDE.md"
echo "  Skill files copied to $SKILL_DIR"

# 2. Save install path to config
mkdir -p "$CONFIG_DIR"
if [ -f "$CONFIG_FILE" ]; then
    # Update existing config — add or replace install_dir
    if command -v python3 &>/dev/null; then
        python3 -c "
import json, sys
with open('$CONFIG_FILE') as f:
    config = json.load(f)
config['install_dir'] = '$PROJECT_DIR'
with open('$CONFIG_FILE', 'w') as f:
    json.dump(config, f, indent=4)
"
    else
        echo "  Warning: python3 not found, cannot update existing config."
        echo "  Please manually add \"install_dir\": \"$PROJECT_DIR\" to $CONFIG_FILE"
    fi
else
    cat > "$CONFIG_FILE" << EOF
{
    "install_dir": "$PROJECT_DIR",
    "claude_session_key": ""
}
EOF
fi
echo "  Config saved to $CONFIG_FILE"

# 3. Sync Python dependencies
if command -v uv &>/dev/null; then
    echo "  Syncing Python dependencies..."
    (cd "$PROJECT_DIR" && uv sync --quiet)
    echo "  Dependencies synced."
else
    echo "  Warning: uv not found. Install it from https://docs.astral.sh/uv/"
    echo "  Then run: cd $PROJECT_DIR && uv sync"
fi

echo ""
echo "Installation complete!"
echo ""
echo "To include web conversations from claude.ai, add your session key:"
echo "  1. Go to https://claude.ai/chats"
echo "  2. Open DevTools (F12) > Application > Cookies > claude.ai"
echo "  3. Copy the 'sessionKey' value"
echo "  4. Edit $CONFIG_FILE and set claude_session_key"
echo ""
echo "Usage: In any Claude Code session, type /daily-summary"
