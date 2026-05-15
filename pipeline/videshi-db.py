#!/usr/bin/env python3
"""
videshi-db.py — Supabase helper for Hatch AI pipeline stages.
Called by the cron agent after AI processing to write results back to Supabase.

Usage:
  python3 videshi-db.py insert-topic <json>
  python3 videshi-db.py mark-signals-processed <id1,id2,...>
  python3 videshi-db.py link-signals <topic_id> <signal_id1,signal_id2,...>
  python3 videshi-db.py insert-article <json>
  python3 videshi-db.py update-topic-status <topic_id> <status>
  python3 videshi-db.py update-article-scores <json>  (re-rank existing articles)
  python3 videshi-db.py decay-scores <json>  (apply time-based decay)
"""

import json
import sys
import os
import hashlib
import requests
from datetime import datetime, timezone

SB_URL = os.environ.get("SUPABASE_URL", "https://lboecaekpynbpyijrbfz.supabase.co")
SB_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
REST = f"{SB_URL}/rest/v1"
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
}

VERTICAL_TO_CATEGORY = {
    "politics": "news",
    "economy": "markets-finance",
    "tech": "technology",
    "immigration": "nri-world",
    "diaspora": "nri-world",
    "science": "technology",
    "culture": "lifestyle-health",
    "sports": "sports",
    "entertainment": "entertainment",
    "education": "news",
}


def clamp(v, lo=0, hi=100):
    try:
        return min(hi, max(lo, round(float(v))))
    except:
        return 50


def slugify(text):
    import re, time
    s = text.lower()
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'\s+', '-', s)
    s = re.sub(r'-+', '-', s).strip('-')
    return s[:80] + '-' + format(int(time.time()), 'x')


def sb_post(table, data, headers_extra=None):
    h = {**HEADERS, "Prefer": "return=representation"}
    if headers_extra:
        h.update(headers_extra)
    r = requests.post(f"{REST}/{table}", headers=h, json=data)
    return r.json() if r.text else None


def sb_patch(table, filters, data):
    h = {**HEADERS, "Prefer": "return=minimal"}
    r = requests.patch(f"{REST}/{table}?{filters}", headers=h, json=data)
    return r.status_code


def sb_upsert(table, data, conflict):
    h = {
        **HEADERS,
        "Prefer": "resolution=ignore-duplicates,return=representation",
        "On-Conflict": conflict,
    }
    r = requests.post(f"{REST}/{table}", headers=h, json=data)
    return r.json() if r.text else None


def cmd_insert_topic(data):
    """Insert a new topic into p2_topics and return its id."""
    topic = json.loads(data) if isinstance(data, str) else data
    vertical = str(topic.get("vertical", "news"))
    category = topic.get("category") or VERTICAL_TO_CATEGORY.get(vertical, "news")

    score_diaspora = clamp(topic.get("score_diaspora", 50))
    score_significance = clamp(topic.get("score_significance", 50))
    score_total = min(100, round(score_diaspora * 0.60 + score_significance * 0.30))

    row = {
        "canonical_title": str(topic["canonical_title"])[:200],
        "vertical": vertical,
        "category": category,
        "urgency": topic.get("urgency", "daily"),
        "score_diaspora": score_diaspora,
        "score_significance": score_significance,
        "score_recency": 50,
        "score_source_avail": clamp(topic.get("score_source_avail", 50)),
        "score_total": score_total,
        "signal_count": topic.get("signal_count", 1),
        "status": "pending",
        "keywords": topic.get("keywords", []),
        "image_url": topic.get("image_url"),
        "image_attribution": topic.get("image_attribution"),
        "image_license": topic.get("image_license"),
        "image_search_query": topic.get("image_search_query"),
    }

    result = sb_post("p2_topics", row)
    if isinstance(result, list) and len(result) > 0:
        print(json.dumps({"ok": True, "id": result[0]["id"], "score_total": score_total}))
    elif isinstance(result, dict) and result.get("id"):
        print(json.dumps({"ok": True, "id": result["id"], "score_total": score_total}))
    else:
        print(json.dumps({"ok": False, "error": str(result)}))


def cmd_mark_signals_processed(signal_ids_str):
    """Mark signals as processed."""
    ids = [s.strip() for s in signal_ids_str.split(",") if s.strip()]
    for sid in ids:
        sb_patch("p2_signals", f"id=eq.{sid}", {"is_processed": True})
    print(json.dumps({"ok": True, "marked": len(ids)}))


def cmd_link_signals(topic_id, signal_ids_str):
    """Link signals to a topic via p2_topic_signals."""
    ids = [s.strip() for s in signal_ids_str.split(",") if s.strip()]
    rows = [{"topic_id": topic_id, "signal_id": sid} for sid in ids]
    if rows:
        sb_upsert("p2_topic_signals", rows, "topic_id,signal_id")
    print(json.dumps({"ok": True, "linked": len(rows)}))


def cmd_insert_article(data):
    """Insert a new article into p2_articles."""
    article = json.loads(data) if isinstance(data, str) else data

    vertical = article.get("vertical", "news")
    category = article.get("category") or VERTICAL_TO_CATEGORY.get(vertical, "news")

    body = str(article.get("body", ""))
    word_count = len(body.split())

    # Auto-publish logic: honor explicit status if passed, otherwise use confidence threshold
    confidence = article.get("confidence", 0)
    score_diaspora = article.get("score_diaspora", 0)
    if "status" in article and article["status"] in ("published", "review", "draft"):
        status = article["status"]
    else:
        auto_publish = confidence >= 65 and score_diaspora >= 60
        status = "published" if auto_publish else "review"
    # Always set published_at for published articles
    published_at = article.get("published_at") or None
    if status == "published" and not published_at:
        published_at = datetime.now(timezone.utc).isoformat()

    score_total = article.get("score_total", 50)

    row = {
        "topic_id": article.get("topic_id"),
        "headline": str(article.get("headline", ""))[:200],
        "subheadline": (str(article["subheadline"])[:300] if article.get("subheadline") else None),
        "body": body,
        "diaspora_angle": (str(article["diaspora_angle"])[:500] if article.get("diaspora_angle") else None),
        "vertical": vertical,
        "category": category,
        "tags": article.get("tags", []),
        "urgency": article.get("urgency", "daily"),
        "sources": article.get("sources", []),
        "image_entities": article.get("image_entities", []),
        "image_must_show": article.get("image_must_show"),
        "image_search_query": article.get("image_search_query"),
        "slug": slugify(str(article.get("headline", "article"))),
        "word_count": word_count,
        "status": status,
        "is_featured": score_total >= 82,
        "score_total": score_total,
        "published_at": published_at,
    }

    result = sb_post("p2_articles", row)
    if isinstance(result, list) and len(result) > 0:
        aid = result[0].get("id", "?")
        print(json.dumps({"ok": True, "id": aid, "status": status, "auto_publish": auto_publish, "headline": row["headline"]}))
    else:
        print(json.dumps({"ok": False, "error": str(result)[:500]}))


def cmd_update_topic_status(topic_id, status):
    """Update a topic's status."""
    sb_patch("p2_topics", f"id=eq.{topic_id}", {"status": status})
    print(json.dumps({"ok": True, "topic_id": topic_id, "status": status}))


def cmd_update_article_scores(data):
    """Re-rank existing articles with new scores."""
    items = json.loads(data) if isinstance(data, str) else data
    if not isinstance(items, list):
        items = [items]
    updated = 0
    for item in items:
        if item.get("id") and item.get("score_total") is not None:
            sb_patch("p2_articles", f"id=eq.{item['id']}", {"score_total": round(item["score_total"])})
            updated += 1
    print(json.dumps({"ok": True, "updated": updated}))


def cmd_decay_scores(data):
    """Apply time-based decay to articles not explicitly re-ranked."""
    articles = json.loads(data) if isinstance(data, str) else data
    if not isinstance(articles, list):
        articles = [articles]
    updated = 0
    for a in articles:
        if not a.get("id") or not a.get("published_at"):
            continue
        try:
            dt = datetime.fromisoformat(a["published_at"].replace("Z", "+00:00"))
            hours = (datetime.now(timezone.utc) - dt).total_seconds() / 3600
        except:
            continue

        if hours <= 6:
            freshness = 1.0
        elif hours <= 12:
            freshness = 0.90
        elif hours <= 24:
            freshness = 0.75
        elif hours <= 48:
            freshness = 0.55
        elif hours <= 72:
            freshness = 0.35
        else:
            freshness = 0.20

        current = a.get("score_total", 50)
        decayed = round(current * freshness)
        if decayed != current:
            sb_patch("p2_articles", f"id=eq.{a['id']}", {"score_total": decayed})
            updated += 1
    print(json.dumps({"ok": True, "decayed": updated}))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: videshi-db.py <command> [args...]")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "insert-topic":
        cmd_insert_topic(sys.argv[2])
    elif cmd == "mark-signals-processed":
        cmd_mark_signals_processed(sys.argv[2])
    elif cmd == "link-signals":
        cmd_link_signals(sys.argv[2], sys.argv[3])
    elif cmd == "insert-article":
        cmd_insert_article(sys.argv[2])
    elif cmd == "update-topic-status":
        cmd_update_topic_status(sys.argv[2], sys.argv[3])
    elif cmd == "update-article-scores":
        cmd_update_article_scores(sys.argv[2])
    elif cmd == "decay-scores":
        cmd_decay_scores(sys.argv[2])
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
