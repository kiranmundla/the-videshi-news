#!/bin/bash
# Lightweight watchdog: checks if system cron is alive every 5 minutes.
# Runs as a separate systemd timer, independent of cron itself.
# Zero LLM usage — pure bash.

LOG="/home/hatch/workspace/cron-logs/watchdog.log"

if systemctl is-active --quiet cron.service; then
    exit 0
fi

# Cron is dead — restart it
echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] ALERT: cron daemon was dead — restarting" >> "$LOG"
sudo systemctl start cron.service
sleep 2

if systemctl is-active --quiet cron.service; then
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] OK: cron daemon restarted successfully" >> "$LOG"
else
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] CRITICAL: cron restart FAILED" >> "$LOG"
fi
