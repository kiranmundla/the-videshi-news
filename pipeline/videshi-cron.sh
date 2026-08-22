#!/bin/bash
# Videshi mechanical cron runner
# Runs pipeline scripts that need zero AI judgment
# Logs output to ~/workspace/cron-logs/
# Errors are picked up by the Hatch health cron

# Load proxy/egress env so cron jobs can reach external hosts
if [ -f /etc/profile.d/hatch-egress.sh ]; then
  source /etc/profile.d/hatch-egress.sh
fi

LOGDIR="$HOME/workspace/cron-logs"
mkdir -p "$LOGDIR"

REPO="$HOME/workspace/the-videshi-news"
ENV="$HOME/workspace"

run_job() {
  local job_id="$1"
  shift
  local logfile="$LOGDIR/${job_id}.log"
  local ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  
  echo "[$ts] START $job_id" >> "$logfile"
  
  # Run the command, capture exit code
  eval "$@" >> "$logfile" 2>&1
  local rc=$?
  
  ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  if [ $rc -eq 0 ]; then
    echo "[$ts] OK $job_id (exit $rc)" >> "$logfile"
  else
    echo "[$ts] FAIL $job_id (exit $rc)" >> "$logfile"
    # Write to error log for health cron to pick up
    echo "[$ts] $job_id exit=$rc" >> "$LOGDIR/_errors.log"
  fi
  
  # Keep last 500 lines per job
  tail -500 "$logfile" > "$logfile.tmp" && mv "$logfile.tmp" "$logfile"
}

case "$1" in

  ## === HOURLY (was 1h Hatch crons) ===

  live)
    run_job "live" "cd $REPO/pipeline && \
      set -a; source $ENV/.env.supabase; set +a; \
      python3 -u videshi-pib-photos.py ingest 2>&1 | tail -3; \
      python3 -u videshi-markets.py 2>&1 | tail -3; \
      python3 -u videshi-market-charts.py 2>&1 | tail -3; \
      python3 -u videshi-ipl.py 2>&1 | tail -3; \
      python3 -u videshi-snapshots.py 2>&1 | tail -3"
    ;;

  v2-ingest)
    run_job "v2-ingest" "cd $REPO/pipeline && \
      set -a; source $ENV/.env.supabase; source $ENV/.env.openai; set +a; \
      timeout 1200 python3 -u v3-ingest.py"
    ;;

  visa-alerts)
    run_job "visa-alerts" "cd $REPO && \
      set -a; source $ENV/.env.supabase; source $ENV/.env.resend; set +a; \
      python3 pipeline/visa-alert-sender.py"
    ;;

  ## === EVERY 6H ===

  dedupe-body-images)
    run_job "dedupe-body-images" "cd $HOME/workspace/videshi-tools && \
      set -a; source $ENV/.env.supabase; set +a; \
      python3 -u dedupe-body-images.py --apply --days 1 2>&1 | tail -30"
    ;;

  ping-google)
    run_job "ping-google" "cd $REPO && \
      set -a; source $ENV/.env.supabase; set +a; \
      python3 pipeline/ping-google.py --recent 4"
    ;;

  gmail-scanner)
    run_job "gmail-scanner" "cd $REPO && \
      set -a; source $ENV/.env.supabase; set +a; \
      python3 pipeline/gmail-scanner.py && \
      python3 pipeline/email-signal-ingest.py"
    ;;

  ## === EVERY 12H ===

  celebrity-buzz)
    run_job "celebrity-buzz" "cd $REPO/pipeline && \
      set -a; source $ENV/.env.supabase; set +a; \
      python3 celeb-buzz-refresh.py && \
      cd $REPO && git add -A public/data/celebrity-buzz.json && \
      git diff --cached --quiet || git commit -m 'data: celeb buzz refresh' && git push origin main"
    ;;

  ## === EVERY 16H ===

  article-cards)
    run_job "article-cards" "cd $REPO && \
      set -a; source $ENV/.env.supabase; set +a; \
      python3 pipeline/article-cards.py --limit 21 && \
      git add -A public/data/article-cards* && \
      git diff --cached --quiet || git commit -m 'data: article cards refresh' && git push origin main"
    ;;

  ## === DAILY ===


  topic-cleanup)
    run_job "topic-cleanup" "set -a; source $ENV/.env.supabase; set +a; \
      CUTOFF=\$(date -u -d '3 days ago' '+%Y-%m-%dT%H:%M:%SZ'); \
      curl -sS -X PATCH \"https://\${SUPABASE_URL#https://}/rest/v1/p2_topics?status=eq.pending&created_at=lt.\${CUTOFF}\" \
        -H \"apikey: \$SUPABASE_SERVICE_ROLE_KEY\" \
        -H \"Authorization: Bearer \$SUPABASE_SERVICE_ROLE_KEY\" \
        -H 'Content-Type: application/json' \
        -H 'Prefer: count=exact' \
        -d '{\"status\":\"rejected\",\"evaluated_at\":\"'\"\$(date -u '+%Y-%m-%dT%H:%M:%SZ')\"'\"}' \
        -w '\\nHTTP %{http_code}' -D /dev/stderr 2>&1 | tail -3"
    ;;
  events-cleanup)
    run_job "events-cleanup" "set -a; source $ENV/.env.supabase; set +a; \
      curl -sS -X POST 'https://api.supabase.com/v1/projects/lboecaekpynbpyijrbfz/database/query' \
        -H \"Authorization: Bearer \$SUPABASE_ACCESS_TOKEN\" \
        -H 'Content-Type: application/json' \
        -d '{\"query\": \"DELETE FROM events WHERE date < CURRENT_DATE;\"}' && \
      cd $REPO/pipeline && python3 -u event_dedup.py clean"
    ;;

  directory-enrich)
    run_job "directory-enrich" "cd $REPO && \
      set -a; source $ENV/.env.supabase; source $ENV/.env.openai; set +a; \
      python3 -u pipeline/enrich-directory.py --limit 1000"
    ;;

  credential-check)
    run_job "credential-check" "cd $REPO/pipeline && \
      set -a; source $ENV/.env.supabase; source $ENV/.env.twitter; source $ENV/.env.youtube; \
      source $ENV/.env.openai; set +a; \
      timeout 180 python3 -u morning-credential-check.py"
    ;;

  scrape-sulekha)
    run_job "scrape-sulekha" "cd $REPO && \
      set -a; source $ENV/.env.supabase; set +a; \
      DAY=\$(python3 -c 'from datetime import datetime; print(datetime.now().weekday())'); \
      python3 -u pipeline/scrape-sulekha.py --day \"\$DAY\""
    ;;

  scrape-eventbrite)
    run_job "scrape-eventbrite" "cd $REPO && \
      set -a; source $ENV/.env.supabase; set +a; \
      python3 pipeline/scrape-eventbrite.py"
    ;;

  scrape-meetup)
    run_job "scrape-meetup" "cd $REPO && \
      set -a; source $ENV/.env.supabase; set +a; \
      python3 pipeline/scrape-meetup.py"
    ;;

  scrape-allevents)
    run_job "scrape-allevents" "cd $REPO/pipeline && \
      set -a; source $ENV/.env.supabase; set +a; \
      DAY=\$(( \$(date +%u) - 1 )); \
      python3 -u scrape-allevents.py --day \$DAY"
    ;;

  scrape-eknazar)
    run_job "scrape-eknazar" "cd $REPO && \
      set -a; source $ENV/.env.supabase; set +a; \
      python3 -u pipeline/scrape-eknazar.py"
    ;;

  media-library)
    run_job "media-library" "cd $REPO/pipeline && \
      set -a; source $ENV/.env.supabase; set +a; \
      python3 -u media-library-source.py"
    ;;

  detect-storylines)
    run_job "detect-storylines" "cd $REPO/pipeline && \
      set -a; source $ENV/.env.supabase; source $ENV/.env.openai; set +a; \
      python3 -u detect-storylines.py && \
      python3 -u update-medal-tally.py"
    ;;

  ## === WEEKLY ===

  snapshots-refresh)
    run_job "snapshots-refresh" "cd $REPO/pipeline && \
      set -a; source $ENV/.env.supabase; source $ENV/.env.pexels; set +a; \
      python3 -u videshi-snapshots.py --refresh && \
      cd $REPO && git add -A public/data/snapshots-pool.json && \
      git diff --cached --quiet || git commit -m 'data: snapshots refresh' && git push origin main"
    ;;

  ai-rankings)
    run_job "ai-rankings" "cd $REPO && \
      set -a; source $ENV/.env.supabase; set +a; \
      python3 -u pipeline/scrape-ai-rankings.py --top 10 && \
      git add -A public/data/ai-rankings.json && \
      git diff --cached --quiet || git commit -m 'data: AI rankings refresh' && git push origin main"
    ;;

  scrape-temples)
    run_job "scrape-temples" "cd $REPO/pipeline && \
      set -a; source $ENV/.env.supabase; set +a; \
      python3 -u scrape-temples.py"
    ;;

  ## === STATUS ===


  pulse-refresh)
    run_job "pulse-refresh" "cd $REPO/pipeline && \
      set -a; source $ENV/.env.supabase; source $ENV/.env.twitterapi-io; set +a; \
      python3 -u refresh-pulse-xapi.py && \
      cd $REPO && git add -A public/data/tech-buzz.json && \
      git diff --cached --quiet || git commit -m 'data: pulse refresh' && git push origin main"
    ;;

  check-dead-images)
    run_job "check-dead-images" "cd $REPO/pipeline && \
      set -a; source $ENV/.env.supabase; set +a; \
      timeout 3600 python3 -u check-dead-images.py"
    ;;

  status)
    echo "=== Recent errors ==="
    tail -20 "$LOGDIR/_errors.log" 2>/dev/null || echo "No errors"
    echo ""
    echo "=== Last run times ==="
    for f in "$LOGDIR"/*.log; do
      [ -f "$f" ] || continue
      name=$(basename "$f" .log)
      [ "$name" = "_errors" ] && continue
      last=$(grep -E "^\[.*\] (OK|FAIL)" "$f" | tail -1)
      echo "  $name: $last"
    done
    ;;

  catchup)
    # Run on boot (@reboot) — check every job and run if overdue
    LOG="$LOGDIR/catchup.log"
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Boot catchup starting" >> "$LOG"

    is_stale() {
      # Usage: is_stale <job_name> <max_age_hours>
      local job="$1" max_hours="$2"
      local logfile="$LOGDIR/${job}.log"
      [ ! -f "$logfile" ] && return 0
      local last_ok=$(grep -E "^\[.*\] (OK|START)" "$logfile" | tail -1 | grep -oP '\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}')
      [ -z "$last_ok" ] && return 0
      local last_epoch=$(date -d "$last_ok" +%s 2>/dev/null)
      [ -z "$last_epoch" ] && return 0
      local now_epoch=$(date +%s)
      local age_hours=$(( (now_epoch - last_epoch) / 3600 ))
      [ "$age_hours" -ge "$max_hours" ] && return 0
      return 1
    }

    # Hourly jobs
    is_stale live 2 && {
      echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Catching up: live" >> "$LOG"
      "/home/hatch/workspace/the-videshi-news/pipeline/videshi-cron.sh" live
    }
    is_stale v2-ingest 2 && {
      echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Catching up: v2-ingest" >> "$LOG"
      "/home/hatch/workspace/the-videshi-news/pipeline/videshi-cron.sh" v2-ingest
    }
    is_stale visa-alerts 2 && {
      echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Catching up: visa-alerts" >> "$LOG"
      "/home/hatch/workspace/the-videshi-news/pipeline/videshi-cron.sh" visa-alerts
    }

    # Every 6h jobs
    is_stale dedupe-body-images 8 && {
      echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Catching up: dedupe-body-images" >> "$LOG"
      "/home/hatch/workspace/the-videshi-news/pipeline/videshi-cron.sh" dedupe-body-images
    }
    is_stale ping-google 8 && {
      echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Catching up: ping-google" >> "$LOG"
      "/home/hatch/workspace/the-videshi-news/pipeline/videshi-cron.sh" ping-google
    }
    is_stale gmail-scanner 8 && {
      echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Catching up: gmail-scanner" >> "$LOG"
      "/home/hatch/workspace/the-videshi-news/pipeline/videshi-cron.sh" gmail-scanner
    }

    # Every 12h jobs
    is_stale celebrity-buzz 14 && {
      echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Catching up: celebrity-buzz" >> "$LOG"
      "/home/hatch/workspace/the-videshi-news/pipeline/videshi-cron.sh" celebrity-buzz
    }
    is_stale pulse-refresh 14 && {
      echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Catching up: pulse-refresh" >> "$LOG"
      "/home/hatch/workspace/the-videshi-news/pipeline/videshi-cron.sh" pulse-refresh
    }

    # Daily jobs — run if >26h stale
    for job in events-cleanup topic-cleanup directory-enrich credential-check \
               scrape-meetup scrape-allevents scrape-sulekha scrape-eventbrite \
               media-library detect-storylines article-cards check-dead-images; do
      is_stale "$job" 26 && {
        echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Catching up: $job" >> "$LOG"
        "/home/hatch/workspace/the-videshi-news/pipeline/videshi-cron.sh" "$job"
      }
    done

    # Weekly jobs — run if >9d stale
    is_stale scrape-temples 216 && {
      echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Catching up: scrape-temples" >> "$LOG"
      "/home/hatch/workspace/the-videshi-news/pipeline/videshi-cron.sh" scrape-temples
    }

    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Boot catchup done" >> "$LOG"
    ;;

  *)
    echo "Usage: $0 {live|v2-ingest|visa-alerts|dedupe-body-images|ping-google|gmail-scanner|celebrity-buzz|article-cards|detect-storylines|events-cleanup|directory-enrich|credential-check|scrape-sulekha|scrape-eventbrite|scrape-meetup|scrape-allevents|scrape-temples|media-library|snapshots-refresh|ai-rankings|pulse-refresh|check-dead-images|catchup|status}"
    exit 1
    ;;
esac
