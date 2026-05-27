#!/usr/bin/env python3
"""Instagram autopost for The Videshi — posts 1 Reel + 1 Story per run."""

import os, sys, time, json, subprocess, re
from datetime import datetime, timezone

import requests

# ── Load credentials ──
def load_env_file(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            v = v.strip().strip('"').strip("'")
            env[k] = v
    return env

ig_env = load_env_file('~/workspace/.env.instagram')
sb_env = load_env_file('~/workspace/.env.supabase')
vite_env = load_env_file('~/workspace/the-videshi-news/.env')

IG_USER_ID = ig_env['INSTAGRAM_USER_ID']
TOKEN = ig_env['INSTAGRAM_ACCESS_TOKEN']
IG_APP_SECRET = ig_env['INSTAGRAM_APP_SECRET']

SB_URL = "https://lboecaekpynbpyijrbfz.supabase.co"
SB_SERVICE_KEY = sb_env['SUPABASE_SERVICE_ROLE_KEY']
SB_ANON_KEY = vite_env['VITE_SUPABASE_PUBLISHABLE_KEY']

new_token = None

# ── Step 1: Refresh token ──
print("=== Refreshing Instagram token ===")
try:
    r = requests.get("https://graph.instagram.com/refresh_access_token", params={
        "grant_type": "ig_refresh_token",
        "access_token": TOKEN
    }, timeout=15)
    rj = r.json()
    print(f"Token refresh response: {r.status_code} — expires_in={rj.get('expires_in','?')}")
    if 'access_token' in rj:
        new_token = rj['access_token']
        TOKEN = new_token
        print("Token refreshed successfully")
    else:
        print(f"Token refresh warning: {rj}")
except Exception as e:
    print(f"Token refresh error (non-fatal): {e}")

# ── Step 2: Fetch unposted articles ──
print("\n=== Fetching unposted articles ===")
headers = {
    "apikey": SB_SERVICE_KEY,
    "Authorization": f"Bearer {SB_SERVICE_KEY}",
}
r = requests.get(
    f"{SB_URL}/rest/v1/p2_articles",
    params={
        "status": "eq.published",
        "instagrammed_at": "is.null",
        "image_url": "not.is.null",
        "order": "published_at.desc",
        "limit": "20",
        "select": "id,slug,headline,subheadline,category,image_url"
    },
    headers=headers,
    timeout=15
)
articles = r.json()
if not isinstance(articles, list):
    print(f"Error fetching articles: {articles}")
    sys.exit(1)

# Filter out articles with empty image_url
articles = [a for a in articles if a.get('image_url')]
print(f"Found {len(articles)} unposted articles with images")

if not articles:
    print("No articles to post. Done.")
    sys.exit(0)

# Pick up to 2
batch = articles[:2]
for i, a in enumerate(batch):
    print(f"  [{i+1}] {a['category']}: {a['headline'][:80]}...")

# ── Hashtag mapping ──
HASHTAGS = {
    'news': '#India #NRI #IndiaNews #IndianDiaspora',
    'immigration': '#Immigration #H1B #NRI #GreenCard #IndianAmerican',
    'nri-world': '#NRI #IndianDiaspora #NRILife #Desi',
    'travel': '#Travel #India #IndiaTravel #IncredibleIndia',
    'lifestyle': '#Lifestyle #Desi #NRILife #IndianAmerican',
    'lifestyle-health': '#Lifestyle #Desi #NRILife #IndianAmerican',
    'markets': '#Markets #India #NRI #Nifty #Sensex',
    'markets-finance': '#Markets #India #NRI #Nifty #Sensex',
    'technology': '#Tech #India #IndianTech #Startup',
    'sports': '#Cricket #India #IPL #IndianCricket',
    'entertainment': '#Bollywood #Entertainment #IndianCinema #Desi',
    'food': '#IndianFood #Desi #IndianCuisine #NRIFood',
}

def make_caption(article):
    cat = article.get('category', 'news')
    tags = HASHTAGS.get(cat, '#India #NRI #IndianDiaspora')
    slug = article['slug']
    headline = article['headline']
    caption = f"{headline}\n\n📰 Read more: https://thevideshi.com/articles/{slug}\n\n{tags}\n\n#TheVideshi"
    return caption

def mark_posted(article_id):
    now = datetime.now(timezone.utc).isoformat()
    r = requests.patch(
        f"{SB_URL}/rest/v1/p2_articles?id=eq.{article_id}",
        headers={
            "apikey": SB_SERVICE_KEY,
            "Authorization": f"Bearer {SB_SERVICE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        },
        json={"instagrammed_at": now},
        timeout=15
    )
    print(f"  Marked instagrammed_at: {r.status_code}")

# ── Step 3: Post REEL for first article ──
reel_article = batch[0]
reel_ok = False
story_ok = False

print(f"\n=== Generating Reel for: {reel_article['headline'][:60]} ===")
try:
    result = subprocess.run(
        ["python3", "generate-reel.py", "--slug", reel_article['slug'], "--upload"],
        cwd=os.path.expanduser("~/workspace/the-videshi-news/pipeline"),
        capture_output=True, text=True, timeout=180
    )
    print(f"Reel gen exit code: {result.returncode}")
    if result.stdout:
        # Print last 20 lines to avoid flooding
        lines = result.stdout.strip().split('\n')
        for l in lines[-20:]:
            print(f"  > {l}")
    if result.stderr:
        err_lines = result.stderr.strip().split('\n')
        for l in err_lines[-10:]:
            print(f"  ERR> {l}")

    # Find the Supabase URL in output
    reel_url = None
    for line in result.stdout.split('\n'):
        if 'supabase.co/storage' in line and 'http' in line:
            match = re.search(r'(https://[^\s"\']+supabase\.co/storage/[^\s"\']+)', line)
            if match:
                reel_url = match.group(1)
                break

    if not reel_url:
        print("ERROR: Could not find reel URL in output")
        # Try to find the file manually
        slug_short = reel_article['slug'][:80]
        expected_path = os.path.expanduser(f"~/workspace/the-videshi-news/pipeline/reels/reel-{slug_short}.mp4")
        if os.path.exists(expected_path):
            print(f"  Found local file: {expected_path}, uploading manually...")
            fname = f"reels/{slug_short}.mp4"
            with open(expected_path, 'rb') as vf:
                ur = requests.post(
                    f"{SB_URL}/storage/v1/object/article-images/{fname}",
                    headers={
                        "apikey": SB_SERVICE_KEY,
                        "Authorization": f"Bearer {SB_SERVICE_KEY}",
                        "Content-Type": "video/mp4",
                        "x-upsert": "true"
                    },
                    data=vf.read(),
                    timeout=60
                )
            print(f"  Upload response: {ur.status_code}")
            if ur.status_code in (200, 201):
                reel_url = f"{SB_URL}/storage/v1/object/public/article-images/{fname}"
        if not reel_url:
            raise Exception("No reel URL found")

    print(f"Reel URL: {reel_url}")

    # Upload cover image
    cover_local = os.path.expanduser(f"~/workspace/the-videshi-news/pipeline/reels/reel-{reel_article['slug'][:80]}-cover.jpg")
    cover_public_url = None
    if os.path.exists(cover_local):
        cover_filename = f"reels/{reel_article['slug'][:80]}-cover.jpg"
        with open(cover_local, 'rb') as cf:
            cr = requests.post(
                f"{SB_URL}/storage/v1/object/article-images/{cover_filename}",
                headers={
                    "apikey": SB_SERVICE_KEY,
                    "Authorization": f"Bearer {SB_SERVICE_KEY}",
                    "Content-Type": "image/jpeg",
                    "x-upsert": "true"
                },
                data=cf.read(),
                timeout=30
            )
        print(f"  Cover upload: {cr.status_code}")
        if cr.status_code in (200, 201):
            cover_public_url = f"{SB_URL}/storage/v1/object/public/article-images/{cover_filename}"
    else:
        print(f"  No cover image found at {cover_local}")

    # Create Reel container
    print("Creating Reel container...")
    caption = make_caption(reel_article)
    container_data = {
        "video_url": reel_url,
        "media_type": "REELS",
        "caption": caption,
        "access_token": TOKEN
    }
    if cover_public_url:
        container_data["cover_url"] = cover_public_url

    cr = requests.post(f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media", data=container_data, timeout=30)
    crj = cr.json()
    print(f"  Container response: {crj}")
    if 'id' not in crj:
        raise Exception(f"Container creation failed: {crj}")
    container_id = crj['id']

    # Poll for FINISHED
    print("Waiting for video processing...")
    finished = False
    for i in range(18):
        time.sleep(5)
        rs = requests.get(
            f"https://graph.instagram.com/v25.0/{container_id}",
            params={"fields": "status_code", "access_token": TOKEN},
            timeout=15
        )
        status = rs.json().get('status_code', 'UNKNOWN')
        print(f"  Poll {i+1}/18: {status}")
        if status == 'FINISHED':
            finished = True
            break
        elif status == 'ERROR':
            raise Exception(f"Video processing error: {rs.json()}")

    if not finished:
        raise Exception("Video processing timed out (90s)")

    # Publish Reel
    print("Publishing Reel...")
    pr = requests.post(f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media_publish", data={
        "creation_id": container_id,
        "access_token": TOKEN
    }, timeout=30)
    prj = pr.json()
    print(f"  Publish response: {prj}")
    if 'id' in prj:
        reel_ok = True
        print(f"✅ Reel published! Media ID: {prj['id']}")
        mark_posted(reel_article['id'])
    else:
        raise Exception(f"Reel publish failed: {prj}")

except Exception as e:
    print(f"❌ Reel posting failed: {e}")

# ── Wait between posts ──
if reel_ok:
    print("\nWaiting 30 seconds before Story...")
    time.sleep(30)

# ── Step 4: Post Story for second article (or first if only one) ──
story_article = batch[1] if len(batch) > 1 else batch[0]
# Don't re-story the same article if reel failed and only one article
if len(batch) == 1 and not reel_ok:
    print("Only one article and reel failed — skipping story too.")
else:
    print(f"\n=== Posting Story for: {story_article['headline'][:60]} ===")
    try:
        sr = requests.post(f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media", data={
            "image_url": story_article['image_url'],
            "media_type": "STORIES",
            "access_token": TOKEN
        }, timeout=30)
        srj = sr.json()
        print(f"  Story container response: {srj}")
        if 'id' not in srj:
            raise Exception(f"Story container failed: {srj}")
        story_container_id = srj['id']

        print("  Waiting 8 seconds for processing...")
        time.sleep(8)

        sp = requests.post(f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media_publish", data={
            "creation_id": story_container_id,
            "access_token": TOKEN
        }, timeout=30)
        spj = sp.json()
        print(f"  Story publish response: {spj}")
        if 'id' in spj:
            story_ok = True
            print(f"✅ Story published! Media ID: {spj['id']}")
            # Mark story article as posted too (if different from reel article)
            if story_article['id'] != reel_article['id']:
                mark_posted(story_article['id'])
        else:
            raise Exception(f"Story publish failed: {spj}")
    except Exception as e:
        print(f"⚠️ Story posting failed (non-fatal): {e}")

# ── Step 5: Save refreshed token ──
if new_token:
    print("\n=== Saving refreshed token ===")
    env_path = os.path.expanduser('~/workspace/.env.instagram')
    with open(env_path) as f:
        content = f.read()
    # Replace the token line
    new_content = re.sub(
        r'INSTAGRAM_ACCESS_TOKEN=.*',
        f'INSTAGRAM_ACCESS_TOKEN={new_token}',
        content
    )
    with open(env_path, 'w') as f:
        f.write(new_content)
    print("Token saved.")

# ── Summary ──
print(f"\n{'='*50}")
print(f"SUMMARY")
print(f"  Reel posted:  {'✅ YES' if reel_ok else '❌ NO'}")
print(f"  Story posted: {'✅ YES' if story_ok else '❌ NO'}")
print(f"  Articles remaining: {len(articles) - (1 if reel_ok else 0) - (1 if story_ok and len(batch)>1 else 0)}")
print(f"{'='*50}")
