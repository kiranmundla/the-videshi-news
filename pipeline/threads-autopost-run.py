#!/usr/bin/env python3
import os, json, time, re, requests

HOME = os.path.expanduser("~")

# Load env files
def load_env(path):
    env = {}
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env

threads_env = load_env(os.path.join(HOME, "workspace/.env.threads"))
supa_env = load_env(os.path.join(HOME, "workspace/.env.supabase"))

THREADS_ACCESS_TOKEN = threads_env.get("THREADS_ACCESS_TOKEN")
THREADS_USER_ID = "26854521280856098"
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"
SUPABASE_KEY = supa_env.get("SUPABASE_SERVICE_ROLE_KEY")

if not THREADS_ACCESS_TOKEN or not SUPABASE_KEY:
    print("ERROR: missing credentials")
    raise SystemExit(1)

CAT_EMOJI = {
    "news": "🇮🇳",
    "immigration": "🛂",
    "nri-world": "🌏",
    "travel": "✈️",
    "lifestyle-health": "🧘",
    "markets-finance": "📈",
    "technology": "💻",
    "sports": "🏏",
    "entertainment": "🎬",
    "food": "🍛",
}

# Fetch recent published articles
headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
url = (f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published"
       "&order=published_at.desc&limit=10"
       "&select=id,slug,headline,subheadline,category,image_url,body")
r = requests.get(url, headers=headers, timeout=30)
r.raise_for_status()
articles = r.json()
print(f"Fetched {len(articles)} recent published articles")

# Load tracking log
log_path = os.path.join(HOME, "workspace/the-videshi-news/pipeline/threads-log.json")
threads_log = json.load(open(log_path)) if os.path.exists(log_path) else {}

def clean_text(t):
    if not t:
        return ""
    # strip markdown
    t = re.sub(r'#+\s*', '', t)
    t = re.sub(r'\*\*([^*]+)\*\*', r'\1', t)
    t = re.sub(r'\*([^*]+)\*', r'\1', t)
    t = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', t)
    t = re.sub(r'`([^`]+)`', r'\1', t)
    t = re.sub(r'>\s*', '', t)
    t = re.sub(r'\n+', ' ', t)
    t = re.sub(r'\s+', ' ', t)
    return t.strip()

def first_sentences(body, max_chars):
    body = clean_text(body)
    sentences = re.split(r'(?<=[.!?])\s+', body)
    out = ""
    for s in sentences:
        if len(out) + len(s) + 1 <= max_chars:
            out = (out + " " + s).strip()
        else:
            break
    if not out and sentences:
        out = sentences[0][:max_chars]
    return out.strip()

def compose_post(article):
    cat = article.get("category", "news")
    emoji = CAT_EMOJI.get(cat, "📰")
    cat_label = cat.replace("-", " ").upper()
    slug = article.get("slug", "")
    headline = clean_text(article.get("headline", "")).upper()
    footer = f"📰 thevideshi.com/articles/{slug}"
    sep = "━━━━━━━━━━━━━━━━━━━━"
    header = f"{emoji} {cat_label} | The Videshi"

    # budget for summary
    fixed = f"{header}\n\n{sep}\n\n{headline}\n\n\n\n{footer}"
    remaining = 500 - len(fixed)
    summary = ""
    if remaining > 40:
        summary = first_sentences(article.get("body", ""), remaining - 2)
    post = f"{header}\n\n{sep}\n\n{headline}\n\n{summary}\n\n{footer}"
    # final trim safeguard
    if len(post) > 500:
        over = len(post) - 500
        summary = summary[:max(0, len(summary) - over - 3)].rstrip() + "..."
        post = f"{header}\n\n{sep}\n\n{headline}\n\n{summary}\n\n{footer}"
    return post

# Select up to 3 not yet posted, with image_url
selected = []
for a in articles:
    if str(a["id"]) in threads_log:
        continue
    if not a.get("image_url"):
        continue
    selected.append(a)
    if len(selected) >= 3:
        break

print(f"Selected {len(selected)} articles to post")

posted = 0
errors = []

for i, article in enumerate(selected):
    post_text = compose_post(article)
    print(f"\n--- Article {article['id']} ({article['category']}) len={len(post_text)} ---")
    print(post_text)
    print("---")

    def create_container(with_image):
        data = {"text": post_text, "access_token": THREADS_ACCESS_TOKEN}
        if with_image:
            data["media_type"] = "IMAGE"
            data["image_url"] = article["image_url"]
        else:
            data["media_type"] = "TEXT"
        return requests.post(
            f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads",
            data=data, timeout=60)

    try:
        resp = create_container(True)
        jr = resp.json()
        if "id" not in jr:
            print(f"Image container failed: {jr}. Falling back to TEXT.")
            resp = create_container(False)
            jr = resp.json()
        if "id" not in jr:
            errors.append(f"{article['id']}: container error {jr}")
            print(f"TEXT container also failed: {jr}")
            continue
        container_id = jr["id"]
        time.sleep(10)
        pub = requests.post(
            f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads_publish",
            data={"creation_id": container_id, "access_token": THREADS_ACCESS_TOKEN},
            timeout=60)
        pjr = pub.json()
        if "id" not in pjr:
            errors.append(f"{article['id']}: publish error {pjr}")
            print(f"Publish failed: {pjr}")
            continue
        post_id = pjr["id"]
        from datetime import datetime
        threads_log[str(article["id"])] = {
            "slug": article["slug"],
            "threads_post_id": str(post_id),
            "posted_at": datetime.utcnow().isoformat() + "Z",
        }
        with open(log_path, "w") as f:
            json.dump(threads_log, f, indent=2)
        posted += 1
        print(f"Posted! post_id={post_id}")
    except Exception as e:
        errors.append(f"{article['id']}: exception {e}")
        print(f"Exception: {e}")

    if i < len(selected) - 1:
        time.sleep(10)

print(f"\n=== SUMMARY ===")
print(f"Posted: {posted}")
print(f"Errors: {len(errors)}")
for e in errors:
    print(f"  - {e}")
