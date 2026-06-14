#!/usr/bin/env python3
"""
Google Indexing API — backlog submitter.
Submits older articles that haven't been submitted yet.
Tracks progress in a state file to avoid re-submitting.
Runs daily, submitting up to 180 URLs per run (leaving 20 for the regular 3h cron).
"""

import json, os, sys, time
from datetime import datetime, timezone
from google.oauth2 import service_account
import google.auth.transport.requests
import requests

KEY_PATH = os.path.expanduser("~/workspace/.google-indexing-key.json")
STATE_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/.indexing-backlog-state.json")
SCOPES = ["https://www.googleapis.com/auth/indexing"]
INDEXING_API = "https://indexing.googleapis.com/v3/urlNotifications:publish"
SITE_URL = "https://www.thevideshi.com"
BATCH_SIZE = 180  # Leave 20/day for the regular cron

def load_state():
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH) as f:
            return json.load(f)
    return {"submitted_slugs": [], "last_run": None}

def save_state(state):
    state["last_run"] = datetime.now(timezone.utc).isoformat()
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)

def get_supabase_creds():
    env_path = os.path.expanduser("~/workspace/.env.supabase")
    env = {}
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env

def main():
    state = load_state()
    already = set(state["submitted_slugs"])
    
    # Get all published article slugs
    env = get_supabase_creds()
    resp = requests.get(
        f"{env['SUPABASE_URL']}/rest/v1/p2_articles",
        params={
            "select": "slug",
            "status": "eq.published",
            "slug": "not.is.null",
            "order": "published_at.asc",
            "limit": "5000"
        },
        headers={
            "apikey": env["SUPABASE_SERVICE_ROLE_KEY"],
            "Authorization": f"Bearer {env['SUPABASE_SERVICE_ROLE_KEY']}",
        },
        timeout=30,
    )
    
    if resp.status_code != 200:
        print(f"❌ Supabase error: {resp.status_code}")
        return
    
    all_slugs = [a["slug"] for a in resp.json() if a.get("slug")]
    pending = [s for s in all_slugs if s not in already]
    
    if not pending:
        print(f"✅ All {len(all_slugs)} articles already submitted. Backlog complete!")
        return
    
    print(f"Total articles: {len(all_slugs)}")
    print(f"Already submitted: {len(already)}")
    print(f"Pending: {len(pending)}")
    print(f"Will submit: {min(len(pending), BATCH_SIZE)}\n")
    
    # Get token
    credentials = service_account.Credentials.from_service_account_file(KEY_PATH, scopes=SCOPES)
    credentials.refresh(google.auth.transport.requests.Request())
    token = credentials.token
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    
    batch = pending[:BATCH_SIZE]
    ok = 0
    for i, slug in enumerate(batch):
        url = f"{SITE_URL}/articles/{slug}"
        body = {"url": url, "type": "URL_UPDATED"}
        try:
            r = requests.post(INDEXING_API, headers=headers, json=body, timeout=30)
            if r.status_code == 200:
                ok += 1
                state["submitted_slugs"].append(slug)
                if i < 5 or i % 30 == 0:
                    print(f"  ✅ [{i+1}/{len(batch)}] {slug[:60]}")
            else:
                error = r.json().get("error", {})
                code = error.get("code")
                print(f"  ❌ [{i+1}] {code}: {error.get('message', '')[:80]}")
                if code == 429:
                    print("  ⚠️  Quota exceeded — saving progress and stopping")
                    break
        except Exception as e:
            print(f"  ❌ [{i+1}] {e}")
        
        if i > 0 and i % 10 == 0:
            time.sleep(1)
    
    save_state(state)
    remaining = len(pending) - ok
    days_left = (remaining // BATCH_SIZE) + 1 if remaining > 0 else 0
    
    print(f"\n{'='*50}")
    print(f"✅ Submitted: {ok}/{len(batch)}")
    print(f"📊 Total submitted to date: {len(state['submitted_slugs'])}/{len(all_slugs)}")
    print(f"⏳ Remaining: {remaining} (~{days_left} days to complete backlog)")

if __name__ == "__main__":
    main()
