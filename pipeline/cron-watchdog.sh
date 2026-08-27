#!/bin/bash
# Lightweight watchdog: checks if system cron is alive and cron schedule is present.
# Runs as a separate systemd timer, independent of cron itself.
# Zero LLM usage — pure bash.

LOG="/home/hatch/workspace/cron-logs/watchdog.log"
CRON_FILE="/etc/cron.d/videshi-pipeline"
RESTORE_SCRIPT="/home/hatch/workspace/the-videshi-news/pipeline/restore-cron.sh"

# Check if cron daemon is alive AND cron file is present + non-empty
NEED_RESTORE=false

if ! systemctl is-active --quiet cron.service 2>/dev/null; then
    NEED_RESTORE=true
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] ALERT: cron daemon was dead" >> "$LOG"
fi

if [ ! -s "$CRON_FILE" ]; then
    NEED_RESTORE=true
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] ALERT: cron file missing or empty" >> "$LOG"
fi

if [ "$NEED_RESTORE" = true ]; then
    if [ -x "$RESTORE_SCRIPT" ]; then
        bash "$RESTORE_SCRIPT" >> "$LOG" 2>&1
    else
        echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] CRITICAL: restore-cron.sh not found/executable" >> "$LOG"
        # Fallback: try to start cron at least
        sudo systemctl start cron.service 2>/dev/null
        sleep 2
        if systemctl is-active --quiet cron.service 2>/dev/null; then
            echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] OK: cron daemon restarted (no schedule file)" >> "$LOG"
        else
            echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] CRITICAL: cron restart FAILED" >> "$LOG"
        fi
    fi
fi
