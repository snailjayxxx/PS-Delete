#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SOURCE="$SCRIPT_DIR/joss-ai-cleanup-core"
INSTALL_DIR="$HOME/Library/Application Support/Joss AI Cleanup"
TARGET="$INSTALL_DIR/joss-ai-cleanup-core"
PLIST="$HOME/Library/LaunchAgents/com.snailjoss.joss-ai-cleanup.plist"

if [[ ! -f "$SOURCE" ]]; then
  echo "未找到 $SOURCE"
  exit 1
fi

mkdir -p "$INSTALL_DIR" "$HOME/Library/LaunchAgents"
cp "$SOURCE" "$TARGET"
chmod 755 "$TARGET"

cat > "$PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.snailjoss.joss-ai-cleanup</string>
  <key>ProgramArguments</key>
  <array>
    <string>$TARGET</string>
    <string>serve</string>
    <string>--host</string><string>127.0.0.1</string>
    <string>--port</string><string>18780</string>
  </array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>$INSTALL_DIR/core.log</string>
  <key>StandardErrorPath</key><string>$INSTALL_DIR/core-error.log</string>
</dict>
</plist>
PLIST

launchctl bootout "gui/$(id -u)" "$PLIST" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
launchctl kickstart -k "gui/$(id -u)/com.snailjoss.joss-ai-cleanup"

echo "安装完成。核心地址：http://127.0.0.1:18780"
echo "如 macOS 阻止运行，请在 系统设置 → 隐私与安全性 中允许。"
