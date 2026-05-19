#!/usr/bin/env python3
"""Score decay for older articles."""
import os, json, requests, datetime
from pathlib import Path

for line in (Path.home() / ".env.supabase").read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ[k.strip()] = v.strip()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

now = datetime.datetime.now(datetime.timezone.utc)

# Get published articles
r = requests.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&select=id,published_at,score_total",
    headers=HEADERS
)
articles = r.json()
print(f"Found {len(articles)} published articles")

decay_count = 0
for a in articles:
    if not a.get("published_at") or not a.get("score_total"):
        continue
    
    pub = datetime.datetime.fromisoformat(a["published_at"].replace("Z", "+00:00"))
    age_hours = (now - pub).total_seconds() / 3600
    
    # Decay: lose 1 point per 6 hours after first 12 hours, min score 30
    if age_hours > 12:
        decay = int((age_hours - 12) / 6)
        new_score = max(30, a["score_total"] - decay)
        if new_score < a["score_total"]:
            requests.patch(
                f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{a['id']}",
                headers=HEADERS,
                json={"score_total": new_score}
            )
            decay_count += 1

print(f"Decayed {decay_count} article scores")
