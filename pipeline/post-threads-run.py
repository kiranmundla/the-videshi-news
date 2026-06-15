#!/usr/bin/env python3
import os, json, time, re, requests
from datetime import datetime

def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env

threads_env = load_env("~/workspace/.env.threads")
supa_env = load_env("~/workspace/.env.supabase")

THREADS_ACCESS_TOKEN = threads_env["THREADS_ACCESS_TOKEN"]
THREADS_USER_ID = "26854521280856098"
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"
SERVICE_KEY = supa_env["SUPABASE_SERVICE_ROLE_KEY"]
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/threads-log.json")

EMOJI = {
    "news": "🇮🇳", "immigration": "🛂", "nri-world": "🌏", "travel": "✈️",
    "lifestyle-health": "🧘", "markets-finance": "📈", "technology": "💻",
    "sports": "🏏", "entertainment": "🎬", "food": "🍛",
}

url = (f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published"
       "&order=published_at.desc&limit=10"
       "&select=id,slug,headline,subheadline,category,image_url,body")
r = requests.get(url, headers={"apikey": SERVICE_KEY,
                               "Authorization": f"Bearer {SERVICE_KEY}"})
r.raise_for_status()
articles = r.json()
print(f"Fetched {len(articles)} recent published articles")

threads_log = json.load(open(LOG_PATH)) if os.path.exists(LOG_PATH) else {}

candidates = []
for a in articles:
    if str(a["id"]) in threads_log:
        continue
    if not a.get("image_url"):
        print(f"SKIP (no image): {a['headline'][:60]}")
        continue
    candidates.append(a)
    if len(candidates) == 3:
        break

print(f"Selected {len(candidates)} articles to post")

def first_sentences(body, n=2, maxlen=240):
    text = re.sub(r"#+\s*", "", body or "")
    text = re.sub(r"\*\*?", "", text)
    text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    parts = re.split(r"(?<=[.!?])\s+", text)
    out = ""
    count = 0
    for p in parts:
        if len(out) + len(p) + 1 > maxlen:
            break
        out = (out + " " + p).strip()
        count += 1
        if count >= n:
            break
    return out

def compose(a):
    cat = a.get("category", "news")
    emoji = EMOJI.get(cat, "🇮🇳")
    catlabel = cat.replace("-", " ").upper()
    headline = a["headline"].upper()
    summary = first_sentences(a.get("body", ""), n=2, maxlen=240)
    slug = a["slug"]
    sep = "━━━━━━━━━━━━━━━━━━━━"
    footer = f"📰 thevideshi.com/articles/{slug}"

    def build(summ):
        return f"{emoji} {catlabel} | The Videshi\n\n{sep}\n\n{headline}\n\n{summ}\n\n{footer}"

    text = build(summary)
    while len(text) > 500 and summary:
        if "." in summary[:-1]:
            idx = summary.rstrip(".").rfind(".")
            if idx > 0:
                summary = summary[:idx+1]
            else:
                summary = " ".join(summary.split()[:-1])
        else:
            summary = " ".join(summary.split()[:-1])
        text = build(summary)
    if len(text) > 500:
        text = f"{emoji} {catlabel} | The Videshi\n\n{headline}\n\n{summary}\n\n{footer}"[:500]
    return text

posted = 0
errors = []
for i, a in enumerate(candidates):
    post_text = compose(a)
    print("\n" + "="*60)
    print(f"Article {a['id']} | {a['category']} | {len(post_text)} chars")
    print(post_text)
    print("="*60)

    used_image = True
    container_data = {
        "media_type": "IMAGE",
        "image_url": a["image_url"],
        "text": post_text,
        "access_token": THREADS_ACCESS_TOKEN,
    }
    cresp = requests.post(f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads",
                          data=container_data)
    cj = cresp.json()
    if "id" not in cj:
        print(f"  Image container failed: {cj}. Falling back to TEXT.")
        used_image = False
        container_data = {
            "media_type": "TEXT",
            "text": post_text,
            "access_token": THREADS_ACCESS_TOKEN,
        }
        cresp = requests.post(f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads",
                              data=container_data)
        cj = cresp.json()
        if "id" not in cj:
            print(f"  TEXT container ALSO failed: {cj}")
            errors.append(f"{a['id']}: container failed {cj}")
            continue
    container_id = cj["id"]
    time.sleep(10 if used_image else 5)

    presp = requests.post(f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads_publish",
                          data={"creation_id": container_id, "access_token": THREADS_ACCESS_TOKEN})
    pj = presp.json()
    if "id" not in pj:
        print(f"  Publish failed: {pj}")
        errors.append(f"{a['id']}: publish failed {pj}")
        continue
    post_id = pj["id"]
    print(f"  POSTED post_id={post_id} (image={used_image})")
    posted += 1

    threads_log[str(a["id"])] = {
        "slug": a["slug"],
        "threads_post_id": str(post_id),
        "posted_at": datetime.utcnow().isoformat() + "Z",
        "image": used_image,
    }
    with open(LOG_PATH, "w") as f:
        json.dump(threads_log, f, indent=2)

    if i < len(candidates) - 1:
        time.sleep(10)

print("\n" + "#"*60)
print(f"SUMMARY: posted={posted}, errors={len(errors)}")
for e in errors:
    print("  ERR:", e)
