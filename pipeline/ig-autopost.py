#!/usr/bin/env python3
"""Instagram autopost for The Videshi — posts 1 Reel + 1 Story per run."""

import os, sys, json, time, subprocess, re
from datetime import datetime, timezone

import requests

# ── Credentials ──────────────────────────────────────────────────────────────
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            k, _, v = line.partition('=')
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env

ig_env = load_env("~/workspace/.env.instagram")
sb_env = load_env("~/workspace/.env.supabase")

IG_USER_ID = ig_env["INSTAGRAM_USER_ID"]
TOKEN = ig_env["INSTAGRAM_ACCESS_TOKEN"]
SB_URL = "https://lboecaekpynbpyijrbfz.supabase.co"
SB_KEY = sb_env["SUPABASE_SERVICE_ROLE_KEY"]

# ── 1. Refresh token ────────────────────────────────────────────────────────
print("=== Refreshing Instagram token ===")
try:
    r = requests.get("https://graph.instagram.com/refresh_access_token", params={
        "grant_type": "ig_refresh_token",
        "access_token": TOKEN
    }, timeout=15)
    rj = r.json()
    if "access_token" in rj:
        new_token = rj["access_token"]
        if new_token != TOKEN:
            TOKEN = new_token
            # Rewrite .env.instagram preserving other values
            ig_env["INSTAGRAM_ACCESS_TOKEN"] = TOKEN
            with open(os.path.expanduser("~/workspace/.env.instagram"), "w") as f:
                for k, v in ig_env.items():
                    f.write(f"{k}={v}\n")
            print("Token refreshed and saved.")
        else:
            print("Token unchanged after refresh.")
    else:
        print(f"Token refresh response (no new token): {rj}")
except Exception as e:
    print(f"Token refresh failed (non-fatal): {e}")

# ── 2. Fetch unposted articles ──────────────────────────────────────────────
print("\n=== Fetching unposted articles ===")
headers = {"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"}
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
    headers=headers, timeout=15
)
articles = r.json()
if not isinstance(articles, list):
    print(f"Unexpected response: {articles}")
    sys.exit(1)

# Filter out any with empty/null image_url
articles = [a for a in articles if a.get("image_url")]
print(f"Found {len(articles)} unposted articles with images.")

if not articles:
    print("Nothing to post. Done.")
    sys.exit(0)

# Pick up to 2
batch = articles[:2]

# ── Hashtag map ──────────────────────────────────────────────────────────────
CATEGORY_TAGS = {
    "news": "#India #NRI #IndiaNews #IndianDiaspora",
    "immigration": "#Immigration #H1B #NRI #GreenCard #IndianAmerican",
    "nri-world": "#NRI #IndianDiaspora #NRILife #Desi",
    "travel": "#Travel #India #IndiaTravel #IncredibleIndia",
    "lifestyle": "#Lifestyle #Desi #NRILife #IndianAmerican",
    "markets": "#Markets #India #NRI #Nifty #Sensex",
    "technology": "#Tech #India #IndianTech #Startup",
    "sports": "#Cricket #India #IPL #IndianCricket",
    "entertainment": "#Bollywood #Entertainment #IndianCinema #Desi",
    "food": "#IndianFood #Desi #IndianCuisine #NRIFood",
}

def make_caption(article):
    cat = (article.get("category") or "news").lower().strip()
    tags = CATEGORY_TAGS.get(cat, "#India #NRI #IndianDiaspora")
    headline = article.get("headline", "").strip()
    slug = article.get("slug", "")
    return f"""{headline}

📰 Read more: https://thevideshi.com/articles/{slug}

{tags}

#TheVideshi"""

# ── 3. Post Reel (first article) ────────────────────────────────────────────
reel_article = batch[0]
reel_ok = False
print(f"\n=== Generating Reel for: {reel_article['headline'][:80]} ===")
print(f"    slug: {reel_article['slug']}")

try:
    result = subprocess.run(
        ["python3", "generate-reel.py", "--slug", reel_article["slug"], "--upload"],
        cwd=os.path.expanduser("~/workspace/the-videshi-news/pipeline"),
        capture_output=True, text=True, timeout=180
    )
    print("generate-reel stdout (last 30 lines):")
    for line in result.stdout.strip().split("\n")[-30:]:
        print(f"  {line}")
    if result.stderr.strip():
        print("generate-reel stderr (last 10 lines):")
        for line in result.stderr.strip().split("\n")[-10:]:
            print(f"  {line}")

    # Extract Supabase URL from output
    reel_url = None
    for line in result.stdout.split("\n"):
        if "supabase.co/storage" in line and "http" in line:
            match = re.search(r'(https://[^\s"\']+supabase\.co/storage/[^\s"\']+)', line)
            if match:
                reel_url = match.group(1)
                break

    if not reel_url:
        print("ERROR: Could not find reel URL in generate-reel output")
        raise Exception("No reel URL found")

    print(f"Reel URL: {reel_url}")

    # Upload cover image
    slug_trunc = reel_article["slug"][:80]
    cover_local = os.path.expanduser(f"~/workspace/the-videshi-news/pipeline/reels/reel-{slug_trunc}-cover.jpg")
    cover_public_url = None
    if os.path.exists(cover_local):
        cover_filename = f"reels/{slug_trunc}-cover.jpg"
        with open(cover_local, "rb") as cf:
            cr = requests.post(
                f"{SB_URL}/storage/v1/object/article-images/{cover_filename}",
                headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}",
                         "Content-Type": "image/jpeg", "x-upsert": "true"},
                data=cf.read(), timeout=30
            )
        if cr.status_code < 300:
            cover_public_url = f"{SB_URL}/storage/v1/object/public/article-images/{cover_filename}"
            print(f"Cover uploaded: {cover_public_url}")
        else:
            print(f"Cover upload failed ({cr.status_code}): {cr.text[:200]}")
    else:
        print(f"No cover image at {cover_local}")

    # Create Reel container
    caption = make_caption(reel_article)
    container_data = {
        "video_url": reel_url,
        "media_type": "REELS",
        "caption": caption,
        "access_token": TOKEN,
    }
    if cover_public_url:
        container_data["cover_url"] = cover_public_url

    print("Creating Reel container...")
    rc = requests.post(f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media",
                       data=container_data, timeout=30)
    rcj = rc.json()
    print(f"Container response: {rcj}")
    if "id" not in rcj:
        raise Exception(f"Container creation failed: {rcj}")
    container_id = rcj["id"]

    # Poll for FINISHED
    print("Waiting for video processing...")
    finished = False
    for i in range(18):
        time.sleep(5)
        rs = requests.get(
            f"https://graph.instagram.com/v25.0/{container_id}",
            params={"fields": "status_code", "access_token": TOKEN}, timeout=15
        )
        status = rs.json().get("status_code", "UNKNOWN")
        print(f"  Poll {i+1}/18: {status}")
        if status == "FINISHED":
            finished = True
            break
        elif status == "ERROR":
            print(f"  ERROR details: {rs.json()}")
            raise Exception("Video processing returned ERROR")

    if not finished:
        raise Exception("Video processing timed out after 90s")

    # Publish Reel
    print("Publishing Reel...")
    rp = requests.post(f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media_publish",
                       data={"creation_id": container_id, "access_token": TOKEN}, timeout=30)
    rpj = rp.json()
    print(f"Publish response: {rpj}")
    if "id" in rpj:
        reel_ok = True
        # Mark as instagrammed
        now_utc = datetime.now(timezone.utc).isoformat()
        requests.patch(
            f"{SB_URL}/rest/v1/p2_articles?id=eq.{reel_article['id']}",
            headers={**headers, "Content-Type": "application/json", "Prefer": "return=minimal"},
            json={"instagrammed_at": now_utc}, timeout=15
        )
        print(f"✅ Reel posted and article marked. Media ID: {rpj['id']}")
    else:
        print(f"❌ Reel publish failed: {rpj}")

except Exception as e:
    print(f"❌ Reel generation/posting failed: {e}")

# ── 4. Story (use second article if available, else first) ───────────────────
print("\n=== Posting Story ===")
story_ok = False
story_article = batch[1] if len(batch) > 1 else batch[0]
# Don't story the same article we just reeled unless it's the only one
if len(batch) == 1 and reel_ok:
    print("Only 1 article in batch and already posted as Reel. Skipping story.")
else:
    print(f"Story article: {story_article['headline'][:80]}")
    try:
        time.sleep(30)  # Rate limit pause
        # Create story container
        rs = requests.post(f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media", data={
            "image_url": story_article["image_url"],
            "media_type": "STORIES",
            "access_token": TOKEN,
        }, timeout=30)
        rsj = rs.json()
        print(f"Story container response: {rsj}")
        if "id" not in rsj:
            raise Exception(f"Story container failed: {rsj}")
        story_container_id = rsj["id"]

        # Wait for processing
        time.sleep(8)

        # Publish story
        rsp = requests.post(f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media_publish", data={
            "creation_id": story_container_id,
            "access_token": TOKEN,
        }, timeout=30)
        rspj = rsp.json()
        print(f"Story publish response: {rspj}")
        if "id" in rspj:
            story_ok = True
            # Also mark this article if it's different from the reel article
            if story_article["id"] != reel_article["id"]:
                now_utc = datetime.now(timezone.utc).isoformat()
                requests.patch(
                    f"{SB_URL}/rest/v1/p2_articles?id=eq.{story_article['id']}",
                    headers={**headers, "Content-Type": "application/json", "Prefer": "return=minimal"},
                    json={"instagrammed_at": now_utc}, timeout=15
                )
            print(f"✅ Story posted. Media ID: {rspj['id']}")
        else:
            print(f"❌ Story publish failed: {rspj}")
    except Exception as e:
        print(f"❌ Story failed (non-fatal): {e}")

# ── Summary ──────────────────────────────────────────────────────────────────
print(f"\n{'='*50}")
print(f"SUMMARY")
print(f"  Reel:  {'✅ Posted' if reel_ok else '❌ Failed'} — {reel_article['headline'][:60]}")
if len(batch) > 1 or not reel_ok:
    print(f"  Story: {'✅ Posted' if story_ok else '❌ Failed'} — {story_article['headline'][:60]}")
else:
    print(f"  Story: ⏭️ Skipped (only 1 article)")
print(f"{'='*50}")
