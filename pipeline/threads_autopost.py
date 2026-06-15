#!/usr/bin/env python3
import os, json, time, re, requests
from datetime import datetime

# ---- Load env ----
def load_env(path):
    env = {}
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env

th = load_env(os.path.expanduser("~/workspace/.env.threads"))
sb = load_env(os.path.expanduser("~/workspace/.env.supabase"))

THREADS_ACCESS_TOKEN = th.get("THREADS_ACCESS_TOKEN")
THREADS_USER_ID = "26854521280856098"
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"
SERVICE_KEY = sb.get("SUPABASE_SERVICE_ROLE_KEY")

assert THREADS_ACCESS_TOKEN, "Missing Threads token"
assert SERVICE_KEY, "Missing Supabase key"

EMOJI = {
    "news": "🇮🇳", "immigration": "🛂", "nri-world": "🌏", "travel": "✈️",
    "lifestyle-health": "🧘", "markets-finance": "📈", "technology": "💻",
    "sports": "🏏", "entertainment": "🎬", "food": "🍛",
}

LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/threads-log.json")
threads_log = json.load(open(LOG_PATH)) if os.path.exists(LOG_PATH) else {}

# ---- Fetch recent published articles ----
url = (f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published"
       f"&order=published_at.desc&limit=10"
       f"&select=id,slug,headline,subheadline,category,image_url,body")
r = requests.get(url, headers={
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
})
r.raise_for_status()
articles = r.json()
print(f"Fetched {len(articles)} recent published articles")

# ---- Pick up to 3 not yet posted, with image ----
candidates = []
for a in articles:
    if str(a["id"]) in threads_log:
        continue
    if not a.get("image_url"):
        print(f"  skip (no image): {a.get('slug')}")
        continue
    candidates.append(a)
    if len(candidates) == 3:
        break

print(f"{len(candidates)} candidates to post")

def clean_text(s):
    if not s:
        return ""
    s = re.sub(r'<[^>]+>', '', s)              # html tags
    s = re.sub(r'\*\*|__|[*_#>`]', '', s)       # md emphasis
    s = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', s)  # images
    s = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', s)  # links
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def first_sentences(body, max_chars):
    body = clean_text(body)
    # split into sentences
    parts = re.split(r'(?<=[.!?])\s+', body)
    out = ""
    for p in parts:
        if not p.strip():
            continue
        if len(out) + len(p) + 1 > max_chars:
            break
        out = (out + " " + p).strip()
        if len(out) >= max_chars * 0.6 and len(out.split('. ')) >= 1:
            # enough for 1-2 sentences
            if out.count('.') >= 2:
                break
    if not out:
        out = body[:max_chars].rsplit(' ', 1)[0]
    return out.strip()

def compose(a):
    cat = a.get("category", "news")
    emoji = EMOJI.get(cat, "📰")
    cat_label = cat.replace("-", " ").upper()
    headline = clean_text(a.get("headline", "")).upper()
    slug = a.get("slug")
    footer = f"📰 thevideshi.com/articles/{slug}"
    header = f"{emoji} {cat_label} | The Videshi"
    sep = "━━━━━━━━━━━━━━━━━━━━"

    # budget for summary
    fixed = len(header) + len(sep) + len(headline) + len(footer) + 8  # newlines
    avail = 500 - fixed - 4
    summary = first_sentences(a.get("body", ""), max(60, avail))
    # assemble
    post = f"{header}\n\n{sep}\n\n{headline}\n\n{summary}\n\n{footer}"
    # trim if over
    while len(post) > 500 and summary:
        summary = summary[:summary.rfind(' ')] if ' ' in summary else ""
        post = f"{header}\n\n{sep}\n\n{headline}\n\n{summary}\n\n{footer}"
    return post

def post_thread(a):
    post_text = compose(a)
    print(f"\n--- {a['slug']} ({len(post_text)} chars) ---")
    print(post_text)
    # Step 1: container with image
    container_data = {
        "media_type": "IMAGE",
        "image_url": a["image_url"],
        "text": post_text,
        "access_token": THREADS_ACCESS_TOKEN,
    }
    resp = requests.post(
        f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads",
        data=container_data)
    j = resp.json()
    if "id" not in j:
        print(f"  IMAGE container failed: {j}. Falling back to TEXT.")
        resp = requests.post(
            f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads",
            data={"media_type": "TEXT", "text": post_text,
                  "access_token": THREADS_ACCESS_TOKEN})
        j = resp.json()
        if "id" not in j:
            print(f"  TEXT container also failed: {j}")
            return None
    container_id = j["id"]
    time.sleep(10)
    resp = requests.post(
        f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads_publish",
        data={"creation_id": container_id, "access_token": THREADS_ACCESS_TOKEN})
    j = resp.json()
    if "id" not in j:
        print(f"  publish failed: {j}")
        return None
    return j["id"]

posted = 0
errors = []
for i, a in enumerate(candidates):
    try:
        pid = post_thread(a)
        if pid:
            threads_log[str(a["id"])] = {
                "slug": a["slug"],
                "threads_post_id": str(pid),
                "posted_at": datetime.utcnow().isoformat() + "Z",
            }
            with open(LOG_PATH, 'w') as f:
                json.dump(threads_log, f, indent=2)
            posted += 1
            print(f"  POSTED -> {pid}")
        else:
            errors.append(a["slug"])
    except Exception as e:
        print(f"  ERROR {a['slug']}: {e}")
        errors.append(a["slug"])
    if i < len(candidates) - 1:
        time.sleep(10)

print(f"\n=== SUMMARY: posted {posted}, errors {len(errors)} {errors} ===")
