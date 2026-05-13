#!/usr/bin/env bash
# videshi-pipeline.sh — Hatch-native news pipeline for The Videshi
# Replaces: p2-ingest, p2-rank, p2-synthesize, p2-images edge functions
# Run by Hatch cron every 30 minutes
#
# This script handles Stage 1 (INGEST) fully autonomously.
# Stages 2-4 (RANK, SYNTHESIZE, IMAGES) output structured data
# for the Hatch AI cron agent to process with its native reasoning.

set -euo pipefail

# ── Config ────────────────────────────────────────────────
SB_URL="${SUPABASE_URL:-$(grep SUPABASE_URL ~/.env.supabase 2>/dev/null | cut -d= -f2)}"
SB_KEY="${SUPABASE_SERVICE_ROLE_KEY:-$(grep SUPABASE_SERVICE_ROLE_KEY ~/.env.supabase 2>/dev/null | cut -d= -f2)}"
REST="$SB_URL/rest/v1"
AUTH_HEADERS=(-H "apikey: $SB_KEY" -H "Authorization: Bearer $SB_KEY" -H "Content-Type: application/json")
AGENT="hatch-pipeline"
CUTOFF_48H=$(date -u -d '48 hours ago' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -v-48H +%Y-%m-%dT%H:%M:%SZ)
CUTOFF_96H=$(date -u -d '96 hours ago' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -v-96H +%Y-%m-%dT%H:%M:%SZ)

log() { echo "[$(date -u +%H:%M:%S)] $*"; }

# Helper: POST to Supabase REST
sb_insert() {
  local table="$1"
  local data="$2"
  curl -s -X POST "$REST/$table" "${AUTH_HEADERS[@]}" \
    -H "Prefer: return=representation" \
    -d "$data"
}

sb_upsert() {
  local table="$1"
  local data="$2"
  local conflict="$3"
  curl -s -X POST "$REST/$table" "${AUTH_HEADERS[@]}" \
    -H "Prefer: resolution=ignore-duplicates,return=representation" \
    -H "On-Conflict: $conflict" \
    -d "$data"
}

sb_patch() {
  local table="$1"
  local filter="$2"
  local data="$3"
  curl -s -X PATCH "$REST/${table}?${filter}" "${AUTH_HEADERS[@]}" \
    -H "Prefer: return=minimal" \
    -d "$data"
}

sb_get() {
  local table="$1"
  local params="$2"
  curl -s "$REST/${table}?${params}" "${AUTH_HEADERS[@]}"
}

alert() {
  local severity="$1"
  local msg="$2"
  sb_insert "pipeline_alerts" "{\"agent\":\"$AGENT\",\"severity\":\"$severity\",\"message\":$(echo "$msg" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))')}" >/dev/null 2>&1 || true
}

# ══════════════════════════════════════════════════════════
# STAGE 1: INGEST — Fetch RSS feeds, deduplicate, store signals
# ══════════════════════════════════════════════════════════

log "═══ STAGE 1: INGEST ═══"

# Fetch active sources
SOURCES=$(sb_get "videshi_sources" "select=id,name,slug,source_type,pipeline_stage,endpoint_url,is_active,priority,fetch_interval_min,max_items,consecutive_errors,total_fetches,total_items,avg_items_per_day&is_active=eq.true&pipeline_stage=in.(discovery,primary)&limit=100")

SOURCE_COUNT=$(echo "$SOURCES" | python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d))" 2>/dev/null || echo "0")
log "Found $SOURCE_COUNT active sources"

if [ "$SOURCE_COUNT" -eq 0 ]; then
  log "No active sources found, skipping ingest"
  alert "warning" "No active sources found"
else

TOTAL_FETCHED=0
TOTAL_INSERTED=0
ERRORS=0

# Process each source
echo "$SOURCES" | python3 -c "
import json, sys
sources = json.load(sys.stdin)
for s in sources:
    # Output tab-separated: id, name, url, pipeline_stage, max_items, priority, consecutive_errors, total_fetches, total_items, avg_items_per_day
    url = s.get('endpoint_url', '')
    print(f\"{s['id']}\t{s['name']}\t{url}\t{s.get('pipeline_stage','discovery')}\t{s.get('max_items',20)}\t{s.get('priority',50)}\t{s.get('consecutive_errors',0)}\t{s.get('total_fetches',0)}\t{s.get('total_items',0)}\t{s.get('avg_items_per_day',0)}\")
" | while IFS=$'\t' read -r SRC_ID SRC_NAME SRC_URL SRC_STAGE SRC_MAX SRC_PRIORITY SRC_ERRORS SRC_FETCHES SRC_ITEMS SRC_AVG; do
  
  # Skip sources with no URL
  if [ -z "$SRC_URL" ]; then
    continue
  fi
  
  # Unwrap rss2json proxy URLs
  FETCH_URL="$SRC_URL"
  if echo "$FETCH_URL" | grep -q "rss2json.com"; then
    INNER=$(echo "$FETCH_URL" | python3 -c "from urllib.parse import urlparse, parse_qs; import sys; u=sys.stdin.read().strip(); qs=parse_qs(urlparse(u).query); print(qs.get('rss_url',[''])[0])" 2>/dev/null || echo "")
    if [ -n "$INNER" ]; then
      FETCH_URL="$INNER"
    fi
  fi

  # Fetch the feed
  FEED_XML=$(curl -s -L --max-time 20 \
    -H "User-Agent: Mozilla/5.0 (compatible; Videshi/1.0; +https://thevideshi.com)" \
    -H "Accept: application/rss+xml, application/xml, text/xml, */*" \
    "$FETCH_URL" 2>/dev/null || echo "FETCH_ERROR")
  
  if [ "$FEED_XML" = "FETCH_ERROR" ] || [ -z "$FEED_XML" ]; then
    log "  ✗ $SRC_NAME — fetch failed"
    ERRORS=$((ERRORS + 1))
    NEW_ERRORS=$((SRC_ERRORS + 1))
    sb_patch "videshi_sources" "id=eq.$SRC_ID" "{\"consecutive_errors\":$NEW_ERRORS,\"last_error\":\"fetch failed\",\"last_error_at\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" >/dev/null 2>&1
    sb_insert "videshi_source_logs" "{\"source_id\":\"$SRC_ID\",\"agent\":\"$AGENT\",\"status\":\"error\",\"error_message\":\"fetch failed\"}" >/dev/null 2>&1
    continue
  fi
  
  # Parse RSS/Atom XML into JSON signals using Python
  SIGNALS_JSON=$(echo "$FEED_XML" | python3 -c "
import sys, re, json, hashlib
from datetime import datetime, timezone, timedelta

xml = sys.stdin.read()
cutoff = datetime.now(timezone.utc) - timedelta(hours=48)

items = []

# Try RSS <item> first, then Atom <entry>
blocks = re.findall(r'<item[\s>][\s\S]*?</item>', xml) or re.findall(r'<entry[\s>][\s\S]*?</entry>', xml)

for block in blocks:
    # Title
    m = re.search(r'<title[^>]*><!\[CDATA\[([\s\S]*?)\]\]></title>', block) or \
        re.search(r'<title[^>]*>([\s\S]*?)</title>', block)
    title = (m.group(1).strip() if m else '').replace('\"', \"'\")
    
    # Link
    m = re.search(r'<link[^>]*>([^<]+)</link>', block) or \
        re.search(r'<link[^>]*href=\"([^\"]+)\"', block) or \
        re.search(r'<guid[^>]*>([\s\S]*?)</guid>', block)
    url = m.group(1).strip() if m else ''
    
    # Published date
    m = re.search(r'<pubDate>([\s\S]*?)</pubDate>', block) or \
        re.search(r'<published>([\s\S]*?)</published>', block) or \
        re.search(r'<dc:date>([\s\S]*?)</dc:date>', block)
    pub_str = m.group(1).strip() if m else None
    
    # Content
    m = re.search(r'<content:encoded><!\[CDATA\[([\s\S]*?)\]\]></content:encoded>', block) or \
        re.search(r'<description><!\[CDATA\[([\s\S]*?)\]\]></description>', block) or \
        re.search(r'<description>([\s\S]*?)</description>', block)
    content = (m.group(1).strip()[:10000] if m else None)
    
    if not title or not url:
        continue
    
    # Parse date and filter
    pub_iso = None
    if pub_str:
        for fmt in ['%a, %d %b %Y %H:%M:%S %z', '%a, %d %b %Y %H:%M:%S %Z',
                     '%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%dT%H:%M:%SZ']:
            try:
                dt = datetime.strptime(pub_str.strip(), fmt)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                pub_iso = dt.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
                if dt < cutoff:
                    pub_iso = 'OLD'
                break
            except:
                continue
        if pub_iso == 'OLD':
            continue
    
    url_hash = hashlib.sha256(url.lower().strip().encode()).hexdigest()[:32]
    items.append({
        'title': title[:500],
        'original_url': url[:1000],
        'url_hash': url_hash,
        'published_at': pub_iso,
        'content': content,
    })

print(json.dumps(items[:50]))
" 2>/dev/null || echo "[]")

  ITEM_COUNT=$(echo "$SIGNALS_JSON" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
  
  if [ "$ITEM_COUNT" -eq 0 ]; then
    log "  ○ $SRC_NAME — 0 items"
    sb_insert "videshi_source_logs" "{\"source_id\":\"$SRC_ID\",\"agent\":\"$AGENT\",\"status\":\"empty\",\"items_fetched\":0,\"items_new\":0}" >/dev/null 2>&1
    continue
  fi
  
  # Build signal rows for upsert
  SIGNAL_ROWS=$(echo "$SIGNALS_JSON" | python3 -c "
import json, sys
items = json.load(sys.stdin)
src_id = '$SRC_ID'
rows = []
for item in items:
    row = {
        'feed_source_id': src_id,
        'title': item['title'],
        'original_url': item['original_url'],
        'url_hash': item['url_hash'],
    }
    if item.get('published_at'):
        row['published_at'] = item['published_at']
    rows.append(row)
print(json.dumps(rows))
")
  
  # Upsert signals (dedup on url_hash)
  INSERTED=$(sb_upsert "p2_signals" "$SIGNAL_ROWS" "url_hash")
  INSERT_COUNT=$(echo "$INSERTED" | python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d) if isinstance(d,list) else 0)" 2>/dev/null || echo "0")
  
  # Primary sources also seed p2_source_hunts
  if [ "$SRC_STAGE" = "primary" ]; then
    HUNT_ROWS=$(echo "$SIGNALS_JSON" | python3 -c "
import json, sys
items = json.load(sys.stdin)
src_id = '$SRC_ID'
rows = []
for item in items[:30]:
    if item.get('content') and len(item['content']) > 100:
        row = {
            'feed_source_id': src_id,
            'url': item['original_url'][:1000],
            'title': item['title'][:500],
            'content': item['content'][:10000],
            'is_used': False,
        }
        if item.get('published_at'):
            row['published_at'] = item['published_at']
        rows.append(row)
if rows:
    print(json.dumps(rows))
else:
    print('[]')
")
    if [ "$HUNT_ROWS" != "[]" ]; then
      sb_upsert "p2_source_hunts" "$HUNT_ROWS" "url" >/dev/null 2>&1 || true
    fi
  fi
  
  # Update source metadata
  NEW_AVG=$(python3 -c "avg=$SRC_AVG; items=$ITEM_COUNT; print(round((avg*6 + items*48)/7))" 2>/dev/null || echo "$ITEM_COUNT")
  NEW_FETCHES=$((SRC_FETCHES + 1))
  NEW_ITEMS=$((SRC_ITEMS + ITEM_COUNT))
  sb_patch "videshi_sources" "id=eq.$SRC_ID" "{\"last_fetched_at\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"avg_items_per_day\":$NEW_AVG,\"consecutive_errors\":0,\"total_fetches\":$NEW_FETCHES,\"total_items\":$NEW_ITEMS}" >/dev/null 2>&1
  
  # Log
  sb_insert "videshi_source_logs" "{\"source_id\":\"$SRC_ID\",\"agent\":\"$AGENT\",\"status\":\"ok\",\"items_fetched\":$ITEM_COUNT,\"items_new\":$INSERT_COUNT,\"items_accepted\":$INSERT_COUNT}" >/dev/null 2>&1
  
  TOTAL_FETCHED=$((TOTAL_FETCHED + ITEM_COUNT))
  TOTAL_INSERTED=$((TOTAL_INSERTED + INSERT_COUNT))
  
  if [ "$INSERT_COUNT" -gt 0 ]; then
    log "  ✓ $SRC_NAME — $ITEM_COUNT items, $INSERT_COUNT new"
  fi
  
done

log "Ingest complete: $TOTAL_FETCHED fetched, $TOTAL_INSERTED new signals"
alert "info" "Ingest: $TOTAL_FETCHED fetched, $TOTAL_INSERTED new signals from $SOURCE_COUNT feeds"

fi

# ══════════════════════════════════════════════════════════
# STAGE 2: RANK — Output unprocessed signals for Hatch AI to cluster
# ══════════════════════════════════════════════════════════

log "═══ STAGE 2: RANK (data collection) ═══"

# Fetch unprocessed signals from last 48h
UNPROCESSED=$(sb_get "p2_signals" "select=id,title,feed_source_id,published_at&is_processed=eq.false&published_at=gte.$CUTOFF_48H&order=published_at.desc&limit=80")
UNPROC_COUNT=$(echo "$UNPROCESSED" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")

log "Found $UNPROC_COUNT unprocessed signals"

# Fetch source metadata for enrichment
if [ "$UNPROC_COUNT" -gt 0 ]; then
  SOURCE_IDS=$(echo "$UNPROCESSED" | python3 -c "
import json, sys
sigs = json.load(sys.stdin)
ids = list(set(s.get('feed_source_id','') for s in sigs if s.get('feed_source_id')))
# Output comma-separated for IN filter
print(','.join(ids))
")
  SOURCE_META=$(sb_get "videshi_sources" "select=id,name,slug,categories,priority&id=in.($SOURCE_IDS)")
fi

# Fetch recently published articles (for dedup context)
RECENT_ARTICLES=$(sb_get "p2_articles" "select=id,headline,category,score_total,published_at&status=eq.published&published_at=gte.$CUTOFF_96H&order=published_at.desc&limit=40")

# Fetch recent topics (for dedup context)  
RECENT_TOPICS=$(sb_get "p2_topics" "select=id,canonical_title,keywords&created_at=gte.$CUTOFF_48H&limit=100")

# Output structured data for the Hatch AI cron agent
echo ""
echo "══════════════════════════════════════════"
echo "PIPELINE_DATA_START"
echo "══════════════════════════════════════════"

echo "SECTION:UNPROCESSED_SIGNALS"
echo "$UNPROCESSED" | python3 -c "
import json, sys
from datetime import datetime, timezone

sigs = json.load(sys.stdin)
for i, s in enumerate(sigs):
    hours_ago = '?'
    if s.get('published_at'):
        try:
            dt = datetime.fromisoformat(s['published_at'].replace('Z','+00:00'))
            hours_ago = round((datetime.now(timezone.utc) - dt).total_seconds() / 3600)
        except:
            pass
    print(f'[{i}] {s[\"id\"]} | \"{s[\"title\"]}\" | {hours_ago}h ago | src:{s.get(\"feed_source_id\",\"?\")[:8]}')
" 2>/dev/null

echo ""
echo "SECTION:SOURCE_METADATA"
if [ "$UNPROC_COUNT" -gt 0 ]; then
  echo "$SOURCE_META" | python3 -c "
import json, sys
sources = json.load(sys.stdin)
for s in sources:
    cats = ','.join(s.get('categories',[]) or [])
    print(f'{s[\"id\"]} | {s[\"name\"]} | priority:{s.get(\"priority\",50)} | cats:{cats}')
" 2>/dev/null
fi

echo ""
echo "SECTION:RECENT_ARTICLES"
echo "$RECENT_ARTICLES" | python3 -c "
import json, sys
from datetime import datetime, timezone
articles = json.load(sys.stdin)
for a in articles:
    hours_ago = '?'
    if a.get('published_at'):
        try:
            dt = datetime.fromisoformat(a['published_at'].replace('Z','+00:00'))
            hours_ago = round((datetime.now(timezone.utc) - dt).total_seconds() / 3600)
        except:
            pass
    print(f'{a[\"id\"]} | \"{a[\"headline\"]}\" | {a.get(\"category\",\"?\")} | score:{a.get(\"score_total\",\"?\")} | {hours_ago}h ago')
" 2>/dev/null

echo ""
echo "SECTION:RECENT_TOPICS"
echo "$RECENT_TOPICS" | python3 -c "
import json, sys
topics = json.load(sys.stdin)
for t in topics:
    kw = ','.join(t.get('keywords',[]) or [])
    print(f'{t[\"id\"]} | \"{t[\"canonical_title\"]}\" | keywords:{kw}')
" 2>/dev/null

echo ""
echo "PIPELINE_DATA_END"
echo "══════════════════════════════════════════"
echo ""
log "Pipeline data collection complete. Hatch AI will process stages 2-4."
