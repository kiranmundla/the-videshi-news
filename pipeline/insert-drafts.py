#!/usr/bin/env python3
"""Bulk-insert writer draft articles into p2_articles, then mark topics published.
Reads ~/workspace/the-videshi-news/pipeline/.state/writer-drafts/*.json
Usage: python3 -u insert-drafts.py [--dry-run] [--only slug]
Requires: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY (set -a; source .env.supabase)
"""
import json, os, sys, glob, subprocess, datetime, re

DRAFT_DIR = os.path.expanduser("~/workspace/the-videshi-news/pipeline/.state/writer-drafts")
SB = os.environ["SUPABASE_URL"].rstrip("/")
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = ["-H", f"apikey: {KEY}", "-H", f"Authorization: Bearer {KEY}",
           "-H", "Content-Type: application/json", "-H", "Prefer: return=representation"]

def curl_json(url, method="GET", data=None):
    cmd = ["curl", "-sS", "--max-time", "60", "-X", method] + HEADERS + [url]
    if data is not None:
        cmd += ["-d", json.dumps(data)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(r.stdout) if r.stdout.strip() else None
    except Exception:
        print("CURL RAW:", r.stdout[:400], r.stderr[:200]); return None

def main():
    dry = "--dry-run" in sys.argv
    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1]
    files = sorted(glob.glob(os.path.join(DRAFT_DIR, "*.json")))
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    done, failed = [], []
    for f in files:
        d = json.load(open(f))
        if only and d.get("slug") != only:
            continue
        payload = dict(d)
        payload["published_at"] = now
        # check existing slug
        ex = curl_json(f"{SB}/rest/v1/p2_articles?select=id&slug=eq.{payload['slug']}&limit=1")
        if ex:
            print(f"SKIP (exists): {payload['slug']}")
            done.append((payload["slug"], ex[0]["id"], d.get("topic_id")))
            continue
        if dry:
            print(f"DRY: would insert {payload['slug']}"); continue
        res = curl_json(f"{SB}/rest/v1/p2_articles", method="POST", data=payload)
        aid = None
        if isinstance(res, list) and res:
            aid = res[0].get("id")
        elif isinstance(res, dict):
            aid = res.get("id")
        if aid:
            print(f"OK inserted: {payload['slug']} -> {aid}")
            done.append((payload["slug"], aid, d.get("topic_id")))
        else:
            print(f"FAIL insert: {payload['slug']}"); failed.append(payload["slug"])
    # mark topics published
    for slug, aid, tid in done:
        if not tid:
            continue
        r = curl_json(f"{SB}/rest/v1/p2_topics?id=eq.{tid}", method="PATCH",
                      data={"status": "published", "last_article_id": aid})
        print(f"  topic {tid[:8]} -> published (article {aid[:8]})")
    print(f"\nINSERTED: {len(done)}  FAILED: {len(failed)} {failed}")
    json.dump({"inserted": [{"slug": s, "id": i, "topic": t} for s, i, t in done],
               "failed": failed},
              open(os.path.join(DRAFT_DIR, "insert-results.json"), "w"), indent=1)

if __name__ == "__main__":
    main()
