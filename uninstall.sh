#!/bin/bash
AM_PLIST="$HOME/Library/LaunchAgents/com.thedailyarxiv.am.plist"
PM_PLIST="$HOME/Library/LaunchAgents/com.thedailyarxiv.pm.plist"

launchctl unload "$AM_PLIST" 2>/dev/null && echo "✓ AM agent unloaded" || echo "(AM agent not loaded)"
launchctl unload "$PM_PLIST" 2>/dev/null && echo "✓ PM agent unloaded" || echo "(PM agent not loaded)"
rm -f "$AM_PLIST" "$PM_PLIST"
echo "✓ Plist files removed"
echo "Done. Delete this folder to fully remove the_daily_arxiv."
