#!/usr/bin/env bash
# Usage: ./insert-article.sh article-file.json
# Reads JSON, finds/uploads image, inserts into DB, updates topic
set -euo pipefail

ARTICLE_JSON="$1"
if [ ! -f "$ARTICLE_JSON" ]; then echo "File not found: $ARTICLE_JSON"; exit 1; fi

set -a; source ~/workspace/.env.supabase; set +a
SUPA_HOST="${SUPABASE_URL#https://}"

python3 -u - "$ARTICLE_JSON" << 'PYEOF'
import sys, json, os, subprocess, re, time
from urllib.parse import quote

article_file = sys.argv[1]
with open(article_file) as f:
    article = json.load(f)

SUPA_HOST = os.environ["SUPABASE_URL"].replace("https://", "")
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = ["-H", f"apikey: {KEY}", "-H", f"Authorization: Bearer {KEY}"]

slug = article["slug"]
headline = article["headline"]
body = article["body"]
category = article.get("category", "news")
vertical = article.get("vertical", category)
tags = article.get("tags", [])
sources = article.get("sources", [])
subheadline = article.get("subheadline", "")
word_count = article.get("word_count", 600)
diaspora_angle = article.get("diaspora_angle", "")
topic_id = article.get("topic_id", "")
image_url = article.get("image_url", "")
image_caption = article.get("image_caption", "")
image_attribution = article.get("image_attribution", "")

# Insert article
now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
payload = {
    "headline": headline,
    "subheadline": subheadline,
    "body": body,
    "slug": slug,
    "category": category,
    "vertical": vertical,
    "tags": tags,
    "sources": sources,
    "image_url": image_url,
    "image_caption": image_caption,
    "image_attribution": image_attribution,
    "word_count": word_count,
    "diaspora_angle": diaspora_angle,
    "topic_id": topic_id,
    "status": "published",
    "published_at": now,
    "article_type": "breaking",
    "is_featured": False,
}

result = subprocess.run(
    ["curl", "-sS", "-X", "POST",
     f"https://{SUPA_HOST}/rest/v1/p2_articles",
     *HEADERS,
     "-H", "Content-Type: application/json",
     "-H", "Prefer: return=representation",
     "-d", json.dumps(payload)],
    capture_output=True, text=True, timeout=30,
)

resp = json.loads(result.stdout)
if isinstance(resp, list) and len(resp) > 0:
    article_id = resp[0]["id"]
    print(f"✅ Inserted article: {headline[:60]}")
    print(f"   ID: {article_id}")
    print(f"   Slug: {slug}")
    
    # Update topic status
    if topic_id:
        topic_result = subprocess.run(
            ["curl", "-sS", "-X", "PATCH",
             f"https://{SUPA_HOST}/rest/v1/p2_topics?id=eq.{topic_id}",
             *HEADERS,
             "-H", "Content-Type: application/json",
             "-d", json.dumps({"status": "published", "last_article_id": article_id})],
            capture_output=True, text=True, timeout=15,
        )
        print(f"   Topic updated: {topic_id[:20]}...")
else:
    print(f"❌ Insert failed: {result.stdout[:200]}")
    sys.exit(1)
PYEOF
