#!/usr/bin/env python3
"""One-time backfill: re-tag published news/nri-world articles to the
subject rule (Kiran, 2026-10-16).

THE RULE: "news" (India tab) = India is the subject — the story
happens in India, or India / an Indian government / Indian
institutions are the actor (wherever they act), or India is the
affected party. "nri-world" (World tab) = everything outside India —
diaspora people/communities abroad (Indian-origin people acting in
foreign roles count as World) plus general world news, India
relevance not required.

Why this exists: the split was never defined geographically. "news"
was the classifier's default bucket (pure US/global stories landed
in India) and "nri-world" was a keyword bucket (an Indian state
government's NRI policy landed in World). v3-select.py now carries
the rule for new articles; this script repairs the archive from
2026-09-01 onward and re-stamps linked key_updates rows to match.

Usage:
  python3 backfill-category-subject-rule.py --dry-run [--limit 60]
  python3 backfill-category-subject-rule.py --apply

Every flip is logged to pipeline/.state/category-backfill-log.jsonl.
Blind classification: the model sees headlines only, never the
current category, so it cannot anchor.
"""
import argparse, json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, ".state")
LOG = os.path.join(STATE, "category-backfill-log.jsonl")
SINCE = "2026-09-01"

def load_env(path):
    if not os.path.exists(path):
        return
    for line in open(path):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env(os.path.expanduser("~/workspace/.env.supabase"))
load_env(os.path.expanduser("~/workspace/.env.openai"))
SUPA_URL = os.environ["SUPABASE_URL"]
SUPA_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
OAI_KEY = os.environ["OPENAI_API_KEY"]

def curl(args, data=None):
    cmd = ["curl", "-s"] + args
    if data is not None:
        cmd += ["-d", data]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return out.stdout

def supa_get(path, params):
    q = "&".join(f"{k}={v}" for k, v in params.items())
    body = curl([f"{SUPA_URL}/rest/v1/{path}?{q}",
                 "-H", f"apikey: {SUPA_KEY}",
                 "-H", f"Authorization: Bearer {SUPA_KEY}"])
    return json.loads(body)

def supa_patch_article(article_id, category):
    body = curl(["-X", "PATCH",
                 f"{SUPA_URL}/rest/v1/p2_articles?id=eq.{article_id}",
                 "-H", f"apikey: {SUPA_KEY}",
                 "-H", f"Authorization: Bearer {SUPA_KEY}",
                 "-H", "Content-Type: application/json",
                 "-H", "Prefer: return=minimal"],
                data=json.dumps({"category": category}))
    return body

def supa_patch_key_update(row_id, category):
    body = curl(["-X", "PATCH",
                 f"{SUPA_URL}/rest/v1/key_updates?id=eq.{row_id}",
                 "-H", f"apikey: {SUPA_KEY}",
                 "-H", f"Authorization: Bearer {SUPA_KEY}",
                 "-H", "Content-Type: application/json",
                 "-H", "Prefer: return=minimal"],
                data=json.dumps({"category": category}))
    return body

RULE = """You classify headlines for The Videshi's two news tabs using the SUBJECT RULE:
- "news" (India tab): INDIA IS THE SUBJECT. It happens in India, OR India / the Indian government / an Indian state government / Indian institutions are the actor (wherever they act — the PM at the UN is India), OR India is the DIRECT OBJECT of a foreign action (tariffs imposed ON India, sanctions ON India, a ruling against India). An Indian state government's policy is "news" even if its beneficiaries are NRIs.
- "nri-world" (World tab): EVERYTHING OUTSIDE INDIA. Diaspora people/communities abroad; a person of Indian origin acting in a FOREIGN role (a US congresswoman, a British minister) is "nri-world"; private Indian citizens abroad in personal stories (crime victims, Indians killed in a fire abroad, families awaiting repatriation) are "nri-world"; general foreign news (US politics, wars not involving India, foreign crime/disasters) is "nri-world" whether or not it touches India.
CRITICAL distinctions: India merely having STAKES in a foreign event does NOT make India the subject — "US midterms and India's stakes in them" is nri-world (the subject is the US election). Indian victims/families in a foreign incident do NOT make India the subject — the incident abroad is the subject (nri-world), UNLESS an Indian authority is acting in the story (a minister announcing a rescue of Indian nationals -> news). Ask: who is the subject? An Indian state/institution as actor, or India as the direct object -> news. A foreign actor/event, or a diaspora person/community -> nri-world."""

def classify_batch(headlines):
    lines = "\n".join(f"{i+1}. {h}" for i, h in enumerate(headlines))
    payload = {
        "model": "gpt-4o-mini",
        "temperature": 0,
        "messages": [
            {"role": "system", "content": RULE},
            {"role": "user", "content":
             f"Classify each headline. Respond ONLY as JSON: "
             f"{{\"results\": [{{\"n\": 1, \"tab\": \"news\"}}, ...]}} "
             f"with one entry per headline, in order.\n\n{lines}"},
        ],
    }
    body = curl(["-X", "POST", "https://api.openai.com/v1/chat/completions",
                 "-H", f"Authorization: Bearer {OAI_KEY}",
                 "-H", "Content-Type: application/json"],
                data=json.dumps(payload))
    data = json.loads(body)
    if "choices" not in data:
        raise RuntimeError(f"OpenAI error: {body[:300]}")
    content = data["choices"][0]["message"]["content"].strip()
    if content.startswith("```"):
        content = content.strip("`")
        if content.startswith("json"):
            content = content[4:]
        content = content.strip()
    parsed = json.loads(content)
    return {r["n"]: r["tab"] for r in parsed["results"]}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    if not args.apply and not args.dry_run:
        print("specify --dry-run or --apply")
        sys.exit(1)

    articles = []
    for cat in ("news", "nri-world"):
        rows = supa_get("p2_articles", {
            "select": "id,headline,category,slug,created_at",
            "category": f"eq.{cat}",
            "status": "eq.published",
            "created_at": f"gte.{SINCE}",
            "order": "created_at.desc",
            "limit": "2000",
        })
        articles += rows
    articles.sort(key=lambda r: r["created_at"], reverse=True)
    if args.limit:
        articles = articles[: args.limit]
    print(f"articles to classify: {len(articles)}")

    flips = []
    BATCH = 20
    for i in range(0, len(articles), BATCH):
        batch = articles[i:i + BATCH]
        verdicts = classify_batch([a["headline"] for a in batch])
        for j, a in enumerate(batch):
            tab = verdicts.get(j + 1)
            if tab in ("news", "nri-world") and tab != a["category"]:
                flips.append({**a, "new_category": tab})
        print(f"  batch {i // BATCH + 1}: cumulative flips {len(flips)}")
        time.sleep(0.3)

    print(f"\nflips: {len(flips)} / {len(articles)}")
    for f in flips:
        print(f"  {f['category']} -> {f['new_category']} | {f['headline'][:95]}")

    if args.dry_run:
        print("\n(dry run — nothing written)")
        return

    os.makedirs(STATE, exist_ok=True)
    flipped_slugs = {}
    with open(LOG, "a") as log:
        for f in flips:
            supa_patch_article(f["id"], f["new_category"])
            flipped_slugs[f["slug"]] = f["new_category"]
            log.write(json.dumps({
                "article_id": f["id"], "slug": f["slug"],
                "headline": f["headline"],
                "from": f["category"], "to": f["new_category"],
            }) + "\n")
    print(f"articles patched: {len(flips)}")

    # Re-stamp key_updates rows linked to flipped articles.
    restamped = 0
    for slug, new_cat in flipped_slugs.items():
        rows = supa_get("key_updates", {
            "select": "id,category",
            "article_slug": f"eq.{slug}",
            "limit": "50",
        })
        for r in rows:
            if r["category"] != new_cat:
                supa_patch_key_update(r["id"], new_cat)
                restamped += 1
    print(f"key_updates re-stamped: {restamped}")

if __name__ == "__main__":
    main()
