#!/usr/bin/env python3
"""Helper to insert a V3 article into Supabase and update topic status."""
import json, os, sys, subprocess, urllib.parse, re
from datetime import datetime, timezone

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

def supabase_req(method, path, data=None, params=None):
    url = f"{SUPABASE_URL}{path}"
    if params:
        url += "?" + "&".join(f"{k}={urllib.parse.quote(str(v), safe='')}" for k, v in params.items())
    cmd = ["curl", "-s", "-X", method, url,
           "-H", f"apikey: {SUPABASE_KEY}",
           "-H", f"Authorization: Bearer {SUPABASE_KEY}",
           "-H", "Content-Type: application/json",
           "-H", "Prefer: return=representation"]
    if data:
        cmd += ["-d", json.dumps(data)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except:
        print(f"Error: {r.stdout[:500]}", file=sys.stderr)
        return None

def upload_image(local_path, slug):
    """Upload image to Supabase storage."""
    storage_path = f"article-images/{slug}.jpg"
    url = f"{SUPABASE_URL}/storage/v1/object/article-images/{slug}.jpg"
    cmd = ["curl", "-s", "-X", "POST", url,
           "-H", f"apikey: {SUPABASE_KEY}",
           "-H", f"Authorization: Bearer {SUPABASE_KEY}",
           "-H", "Content-Type: image/jpeg",
           "--data-binary", f"@{local_path}"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    # If exists, try upsert
    if "Duplicate" in r.stdout or "already exists" in r.stdout:
        cmd[3] = "PUT"  # switch to PUT for update
        r = subprocess.run(cmd, capture_output=True, text=True)
    public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{slug}.jpg"
    return public_url

def insert_article(article_data):
    """Insert article into p2_articles."""
    result = supabase_req("POST", "/rest/v1/p2_articles", article_data)
    if result and isinstance(result, list) and len(result) > 0:
        return result[0]
    return result

def update_topic(topic_id, article_id):
    """Update topic status to published."""
    supabase_req("PATCH", f"/rest/v1/p2_topics", 
                 {"status": "published", "last_article_id": article_id},
                 {"id": f"eq.{topic_id}"})

if __name__ == "__main__":
    article_file = sys.argv[1]
    with open(article_file) as f:
        data = json.load(f)
    
    # Handle image if provided
    if data.get("_image_local_path") and data.get("slug"):
        print(f"Uploading image for {data['slug']}...")
        img_url = upload_image(data["_image_local_path"], data["slug"])
        data["image_url"] = img_url
        del data["_image_local_path"]
    
    topic_id = data.pop("_topic_id", None)
    
    # Insert article
    print(f"Inserting article: {data['headline'][:60]}...")
    result = insert_article(data)
    if result and isinstance(result, dict) and result.get("id"):
        article_id = result["id"]
        print(f"  ✓ Inserted: {article_id}")
        
        # Update topic
        if topic_id:
            update_topic(topic_id, article_id)
            print(f"  ✓ Topic {topic_id[:8]} updated")
    else:
        print(f"  ✗ Insert failed: {result}", file=sys.stderr)
        sys.exit(1)
