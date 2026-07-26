#!/bin/bash
# Pipeline watchdog — runs from system crontab every 2 hours
# Checks two things:
#   1. Is the cron daemon alive? If not, restart it.
#   2. Has it been too long since the last article? If so, log a warning.
# Logs to ~/workspace/cron-logs/watchdog.log

LOGFILE="$HOME/workspace/cron-logs/watchdog.log"
mkdir -p "$(dirname "$LOGFILE")"
TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# --- 1. Cron daemon health ---
if ! pgrep -x cron > /dev/null 2>&1; then
  echo "[$TS] ALERT: cron daemon was dead — restarting" >> "$LOGFILE"
  sudo service cron start >> "$LOGFILE" 2>&1 || cron >> "$LOGFILE" 2>&1
  sleep 2
  if pgrep -x cron > /dev/null 2>&1; then
    echo "[$TS] OK: cron daemon restarted successfully" >> "$LOGFILE"
  else
    echo "[$TS] FAIL: could not restart cron daemon" >> "$LOGFILE"
  fi
else
  echo "[$TS] OK: cron daemon running" >> "$LOGFILE"
fi

# --- 2. Article freshness ---
set -a; source "$HOME/workspace/.env.supabase"; set +a
SUPABASE_HOST="${SUPABASE_URL#https://}"

LATEST=$(curl -sf "https://${SUPABASE_HOST}/rest/v1/p2_articles?select=created_at&status=eq.published&order=created_at.desc&limit=1" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" 2>/dev/null \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print(d[0]['created_at'] if d else '')" 2>/dev/null)

if [ -z "$LATEST" ]; then
  echo "[$TS] WARN: could not fetch latest article timestamp" >> "$LOGFILE"
  exit 0
fi

# Calculate hours since last article
HOURS_AGO=$(python3 -c "
from datetime import datetime, timezone
latest = datetime.fromisoformat('$LATEST'.replace('+00:00','+00:00'))
if latest.tzinfo is None:
    from datetime import timezone as tz
    latest = latest.replace(tzinfo=tz.utc)
diff = datetime.now(timezone.utc) - latest
print(f'{diff.total_seconds()/3600:.1f}')
" 2>/dev/null)

if [ -z "$HOURS_AGO" ]; then
  echo "[$TS] WARN: could not calculate article age" >> "$LOGFILE"
  exit 0
fi

THRESHOLD=8
STALE=$(python3 -c "print('yes' if float('$HOURS_AGO') > $THRESHOLD else 'no')")

if [ "$STALE" = "yes" ]; then
  echo "[$TS] ALERT: no new articles in ${HOURS_AGO}h (threshold: ${THRESHOLD}h) — last: $LATEST" >> "$LOGFILE"
else
  echo "[$TS] OK: last article ${HOURS_AGO}h ago" >> "$LOGFILE"
fi

# Keep log trimmed (last 200 lines)
tail -200 "$LOGFILE" > "$LOGFILE.tmp" && mv "$LOGFILE.tmp" "$LOGFILE"
