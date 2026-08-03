#!/bin/bash
set -euo pipefail
PLIST="$HOME/Library/LaunchAgents/com.snailjoss.joss-ai-cleanup.plist"
launchctl bootout "gui/$(id -u)" "$PLIST" 2>/dev/null || true
rm -f "$PLIST"
rm -rf "$HOME/Library/Application Support/Joss AI Cleanup"
echo "Joss AI Cleanup Core 已卸载。系统凭据库中的 API Key 需按需手动删除。"
