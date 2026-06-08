#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# The Daily arXiv — Mac Installer
# Sets up AM and optional PM LaunchAgents to run automatically each day.
# ─────────────────────────────────────────────────────────────────────────────
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/the_daily_arxiv.py"
AM_PLIST_NAME="com.thedailyarxiv.am"
PM_PLIST_NAME="com.thedailyarxiv.pm"
AM_PLIST_PATH="$HOME/Library/LaunchAgents/$AM_PLIST_NAME.plist" ## should we swithc these to LaunchDaemons at some point?
PM_PLIST_PATH="$HOME/Library/LaunchAgents/$PM_PLIST_NAME.plist"

echo ""
echo "    The Daily arXiv — Installer"
echo "   ###################################"
echo ""

# Python
PYTHON=$(which python3 2>/dev/null || "")
if [ -z "$PYTHON" ]; then
  echo " Python 3 not found. Install from https://python.org"
  exit 1
fi
echo "  Python version acceptable. $("$PYTHON" --version 2>&1)"
chmod +x "$PYTHON_SCRIPT"
echo " Script is executable"

# terminal-notifier 
echo ""
if command -v terminal-notifier &>/dev/null; then
  echo " terminal-notifier found — notifications will be clickable"
else
  echo "  ℹ  terminal-notifier not found (notifications will still work but will NOT be clickable)"
  if command -v brew &>/dev/null; then
    read -rp "     Install via Homebrew now? [y/N] " yn
    if [[ "$yn" =~ ^[Yy]$ ]]; then
      brew install terminal-notifier
      echo " terminal-notifier installed"
    fi
  else
    echo "     Run: brew install terminal-notifier"
  fi
fi

# AM schedule (first run)
echo ""
echo "What time would you like to receive the notifications?"
read -rp "  Hour   (Specify a number 0-23, default 8):  " am_hour
read -rp "  Minute (Specify a number 0-59, default 30): " am_min
AM_HOUR=${am_hour:-8}
AM_MINUTE=${am_min:-30}

mkdir -p "$HOME/Library/LaunchAgents"

  cat > "$AM_PLIST_PATH" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>$AM_PLIST_NAME</string>
  <key>ProgramArguments</key>
  <array>
    <string>$PYTHON</string>
    <string>$PYTHON_SCRIPT</string>
    <string>--am</string>
  </array>
  <key>StartCalendarInterval</key>
  <array>
    <dict>
      <key>Weekday</key><integer>1</integer>
      <key>Hour</key><integer>$AM_HOUR</integer>
      <key>Minute</key><integer>$AM_MINUTE</integer>
    </dict>
    <dict>
      <key>Weekday</key><integer>2</integer>
      <key>Hour</key><integer>$AM_HOUR</integer>
      <key>Minute</key><integer>$AM_MINUTE</integer>
    </dict>
    <dict>
      <key>Weekday</key><integer>3</integer>
      <key>Hour</key><integer>$AM_HOUR</integer>
      <key>Minute</key><integer>$AM_MINUTE</integer>
    </dict>
    <dict>
      <key>Weekday</key><integer>4</integer>
      <key>Hour</key><integer>$AM_HOUR</integer>
      <key>Minute</key><integer>$AM_MINUTE</integer>
    </dict>
    <dict>
      <key>Weekday</key><integer>5</integer>
      <key>Hour</key><integer>$AM_HOUR</integer>
      <key>Minute</key><integer>$AM_MINUTE</integer>
    </dict>
  </array>
  <key>StandardErrorPath</key>
  <string>$SCRIPT_DIR/daily_arxiv.log</string>
  <key>StandardOutPath</key>
  <string>$SCRIPT_DIR/daily_arxiv.log</string>
</dict>
</plist>
EOF 

launchctl unload "$AM_PLIST_PATH" 2>/dev/null || true
launchctl load -w "$AM_PLIST_PATH"
echo "  ✓  AM run scheduled at $AM_HOUR:$(printf '%02d' $AM_MINUTE)"

# PM schedule (optional 2nd run)
echo ""
read -rp " Would you like an additional (perhaps PM) run? [y/N] " add_pm
if [[ "$add_pm" =~ ^[Yy]$ ]]; then
  echo ""
  echo "  ── PM Run ──────────────────────────────"
  read -rp "  Hour   (0-23, default 13): " pm_hour
  read -rp "  Minute (0-59, default 0):  " pm_min
  PM_HOUR=${pm_hour:-13}
  PM_MINUTE=${pm_min:-0}

  cat > "$PM_PLIST_PATH" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>$PM_PLIST_NAME</string>
  <key>ProgramArguments</key>
  <array>
    <string>$PYTHON</string>
    <string>$PYTHON_SCRIPT</string>
    <string>--pm</string>
  </array>
  <key>StartCalendarInterval</key>
  <array>
    <dict>
      <key>Weekday</key><integer>1</integer>
      <key>Hour</key><integer>$PM_HOUR</integer>
      <key>Minute</key><integer>$PM_MINUTE</integer>
    </dict>
    <dict>
      <key>Weekday</key><integer>2</integer>
      <key>Hour</key><integer>$PM_HOUR</integer>
      <key>Minute</key><integer>$PM_MINUTE</integer>
    </dict>
    <dict>
      <key>Weekday</key><integer>3</integer>
      <key>Hour</key><integer>$PM_HOUR</integer>
      <key>Minute</key><integer>$PM_MINUTE</integer>
    </dict>
    <dict>
      <key>Weekday</key><integer>4</integer>
      <key>Hour</key><integer>$PM_HOUR</integer>
      <key>Minute</key><integer>$PM_MINUTE</integer>
    </dict>
    <dict>
      <key>Weekday</key><integer>5</integer>
      <key>Hour</key><integer>$PM_HOUR</integer>
      <key>Minute</key><integer>$PM_MINUTE</integer>
    </dict>
  </array>
  <key>StandardErrorPath</key>
  <string>$SCRIPT_DIR/daily_arxiv.log</string>
  <key>StandardOutPath</key>
  <string>$SCRIPT_DIR/daily_arxiv.log</string>
</dict>
</plist>
EOF

  launchctl unload "$PM_PLIST_PATH" 2>/dev/null || true
  launchctl load -w "$PM_PLIST_PATH"
  echo "  ✓  PM run scheduled at $PM_HOUR:$(printf '%02d' $PM_MINUTE)"


# Notification permission reminder
echo ""
echo " You MUST set notifications to Alerts for them to stay on screen:"
echo " To do so, go to System Settings -> Notifications -> Terminal -> Alerts"
echo ""

# Test run 
read -rp "  Test it now? [Y/n] " test_yn
if [[ ! "$test_yn" =~ ^[Nn]$ ]]; then
  echo "  Fetching papers…"
  "$PYTHON" "$PYTHON_SCRIPT" --am
  echo "  ✓  Done! Check your notifications."
fi

echo ""
echo "  ─────────────────────────────────"
echo " the_daily_arxiv has been successfully installed!"
echo ""
echo "  Commands:"
echo "    Edit keywords:   python3 \"$PYTHON_SCRIPT\" --settings"
echo "    Run AM now:      python3 \"$PYTHON_SCRIPT\" --am"
echo "    Run PM now:      python3 \"$PYTHON_SCRIPT\" --pm"
echo "    Open HTML:       python3 \"$PYTHON_SCRIPT\" --html"
echo "    Clear seen log:  python3 \"$PYTHON_SCRIPT\" --clear-seen"
echo "    Check setup:     python3 \"$PYTHON_SCRIPT\" --check"
echo "    Uninstall:       bash \"$SCRIPT_DIR/uninstall.sh\""
echo ""
