#!/usr/bin/env python3
"""Instagram auto-poster for The Videshi — posts Reels + Stories."""

import os
import re
import sys
import json
import time
import subprocess
from datetime import datetime, timezone

import requests

# ── Load credentials ──────────────────────────────────────────────
def load_env_file(path):
    """Parse KEY=VALUE (with optional quotes) from a file."""
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue
            k, v = line.split('=', 1)
            v = v.strip().strip('"').strip("'")
            env[k] = v
    return env

ig_env = load_env_file("~/workspace/.env.instagram")
sb_env = load_env_file("~/workspace/.env.supabase")
vite_env = load_env_file("~/workspace/the-videshi-news/.env")

IG_USER_ID = ig_env["INSTAGRAM_USER_ID"]
TOKEN = ig_env["INSTAGRAM_ACCESS_TOKEN"]
IG_APP_SECRET = ig_env["INSTAGRAM_APP_SECRET"]
SB_SERVICE_KEY = sb_env["SUPABASE_SERVICE_ROLE_KEY"]
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"

# ── Load AI review keys ───────────────────────────────────────────
ai_env = load_env_file("~/workspace/.env.openai")
gemini_env = load_env_file("~/workspace/.env.google-ai")
OPENAI_KEY = ai_env.get("OPENAI_API_KEY", "")
GEMINI_KEY = gemini_env.get("GOOGLE_AI_API_KEY", "")


def review_reel_quality(article, caption):
    """AI quality gate for reels — checks caption + headline before posting.
    Returns (pass: bool, feedback: str)."""
    prompt = f"""You are a social media editor for The Videshi, an Indian diaspora news platform.
Review this Instagram Reel caption and article headline for quality before posting.

HEADLINE: {article.get('headline', 'N/A')}
CATEGORY: {article.get('category', 'N/A')}

CAPTION:
{caption}

Score 1-10 and check:
1. Caption is factually consistent with headline (no contradictions)
2. No broken hashtags or formatting issues
3. Tone is professional but engaging (not clickbait)
4. Hashtags are relevant to the topic
5. No hallucinated claims not supported by the headline

Respond in JSON: {{"score": N, "pass": true/false, "issues": ["issue1"], "suggestion": "optional fix"}}
Score 7+ = pass. Below 7 = fail with issues."""

    # Try GPT-4o-mini first
    if OPENAI_KEY:
        try:
            r = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"},
                json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}],
                      "temperature": 0.3, "response_format": {"type": "json_object"}},
                timeout=30
            )
            if r.status_code == 200:
                result = json.loads(r.json()["choices"][0]["message"]["content"])
                return result.get("pass", True), f"GPT-4o-mini score {result.get('score','?')}: {result.get('issues', [])}"
        except Exception as e:
            print(f"  ⚠️ OpenAI review failed: {e}")

    # Fallback to Gemini
    if GEMINI_KEY:
        try:
            r = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}",
                headers={"Content-Type": "application/json"},
                json={"contents": [{"parts": [{"text": prompt}]}],
                      "generationConfig": {"responseMimeType": "application/json", "temperature": 0.3}},
                timeout=30
            )
            if r.status_code == 200:
                text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                result = json.loads(text)
                return result.get("pass", True), f"Gemini score {result.get('score','?')}: {result.get('issues', [])}"
        except Exception as e:
            print(f"  ⚠️ Gemini review failed: {e}")

    # If both fail, pass by default (don't block posting on API issues)
    return True, "AI review unavailable — passing by default"

# ── Step 1: Refresh token ─────────────────────────────────────────
print("=== Refreshing Instagram token ===")
try:
    r = requests.get("https://graph.instagram.com/refresh_access_token", params={
        "grant_type": "ig_refresh_token",
        "access_token": TOKEN
    }, timeout=15)
    rj = r.json()
    if 'access_token' in rj:
        new_token = rj['access_token']
        if new_token != TOKEN:
            TOKEN = new_token
            # Rewrite .env.instagram preserving all other values
            ig_env["INSTAGRAM_ACCESS_TOKEN"] = TOKEN
            with open(os.path.expanduser("~/workspace/.env.instagram"), 'w') as f:
                for k, v in ig_env.items():
                    f.write(f"{k}={v}\n")
            print(f"Token refreshed and saved (expires in {rj.get('expires_in', '?')}s)")
        else:
            print(f"Token unchanged (expires in {rj.get('expires_in', '?')}s)")
    else:
        print(f"Token refresh response (no new token): {rj}")
except Exception as e:
    print(f"Token refresh failed (non-fatal): {e}")

# ── Step 2: Fetch unposted articles ──────────────────────────────
print("\n=== Fetching unposted articles ===")
headers = {
    "apikey": SB_SERVICE_KEY,
    "Authorization": f"Bearer {SB_SERVICE_KEY}",
    "Content-Type": "application/json"
}

r = requests.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles",
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

if r.status_code != 200:
    print(f"ERROR: Supabase fetch failed: {r.status_code} {r.text}")
    sys.exit(1)

articles = r.json()
print(f"Found {len(articles)} unposted articles with images")

if not articles:
    print("Nothing to post. Exiting.")
    sys.exit(0)

# Pick up to 2 articles
batch = articles[:2]
for a in batch:
    print(f"  - [{a['category']}] {a['headline'][:80]}...")

# ── Hashtag mapping ──────────────────────────────────────────────
CATEGORY_HASHTAGS = {
    "news": "#India #NRI #IndiaNews #IndianDiaspora #BreakingNews #DesiNews #SouthAsian #IndianAmerican #NRINews",
    "immigration": "#Immigration #H1B #H1BVisa #NRI #GreenCard #IndianAmerican #USImmigration #VisaUpdate #OPT #USCIS #Desi",
    "nri-world": "#NRI #IndianDiaspora #NRILife #Desi #IndianAmerican #SouthAsian #DesiAbroad #IndianImmigrant #NRICommunity",
    "travel": "#Travel #India #IndiaTravel #IncredibleIndia #TravelIndia #DesiTravel #IndianDestinations #TravelDiaries #Wanderlust",
    "lifestyle-health": "#Lifestyle #Desi #NRILife #IndianAmerican #DesiLifestyle #Wellness #Health #SouthAsian #DesiCulture",
    "markets-finance": "#Markets #India #NRI #Nifty #Sensex #BSE #NSE #IndianMarkets #StockMarket #Finance #NRIInvesting",
    "technology": "#Tech #India #IndianTech #Startup #H1B #SiliconValley #AI #TechNews #IndianEngineers #FAANG #IndiansinTech",
    "sports": "#Cricket #India #IPL #IPL2026 #IndianCricket #BCCI #CricketNews #Desi #TeamIndia",
    "entertainment": "#Bollywood #Entertainment #IndianCinema #Desi #BollywoodNews #Tollywood #IndianMovies #DesiEntertainment",
    "food": "#IndianFood #Desi #IndianCuisine #NRIFood #DesiFood #IndianCooking #Foodie #IndianRecipes #DesiChef",
}

def extract_topic_hashtags(headline):
    """Extract person/company/place names from headline as hashtags."""
    tags = []
    # Common patterns — person names, companies, places
    known = {
        "modi": "#NarendraModi #Modi", "trump": "#Trump #DonaldTrump",
        "kohli": "#ViratKohli #Kohli", "rohit": "#RohitSharma",
        "dhoni": "#MSDhoni #Dhoni", "bumrah": "#JaspritBumrah",
        "shah rukh": "#ShahRukhKhan #SRK", "salman khan": "#SalmanKhan",
        "aamir khan": "#AamirKhan", "deepika": "#DeepikaPadukone",
        "priyanka": "#PriyankaChopra", "alia": "#AliaBhatt",
        "infosys": "#Infosys", "tcs": "#TCS", "wipro": "#Wipro",
        "reliance": "#Reliance", "tata": "#Tata", "adani": "#Adani",
        "ambani": "#Ambani", "google": "#Google", "apple": "#Apple",
        "microsoft": "#Microsoft", "meta": "#Meta", "tesla": "#Tesla",
        "h-1b": "#H1BVisa #H1B", "h1b": "#H1BVisa #H1B",
        "green card": "#GreenCard", "ipl": "#IPL #IPL2026",
        "mumbai": "#Mumbai", "delhi": "#Delhi", "bangalore": "#Bangalore",
        "hyderabad": "#Hyderabad", "chennai": "#Chennai",
        "new york": "#NewYork", "silicon valley": "#SiliconValley",
        "jaishankar": "#Jaishankar", "rahul gandhi": "#RahulGandhi",
        "kejriwal": "#Kejriwal", "yogi": "#YogiAdityanath",
        "sundar pichai": "#SundarPichai", "satya nadella": "#SatyaNadella",
        "sam altman": "#SamAltman", "elon musk": "#ElonMusk",
        "bollywood": "#Bollywood", "cricket": "#Cricket",
        "sachin": "#SachinTendulkar", "bcci": "#BCCI",
        "canada": "#Canada", "uk": "#UK", "australia": "#Australia",
        "visa": "#Visa", "uscis": "#USCIS",
        "ai": "#AI #ArtificialIntelligence",
        "startup": "#Startup #IndianStartup",
    }
    hl = headline.lower()
    found = set()
    for pattern, tag_str in known.items():
        if pattern in hl:
            for t in tag_str.split():
                found.add(t)
    return list(found)[:4]

def build_caption(article):
    headline = article['headline']
    slug = article['slug']
    cat = article.get('category', 'news') or 'news'

    cat_tags = CATEGORY_HASHTAGS.get(cat, CATEGORY_HASHTAGS['news'])
    topic_tags = extract_topic_hashtags(headline)
    topic_str = " ".join(topic_tags)

    caption = f"""{headline}

📰 Read more: https://thevideshi.com/articles/{slug}

{cat_tags}
{topic_str}

#TheVideshi #Reels"""

    # Ensure max 20 hashtags
    all_tags = re.findall(r'#\w+', caption)
    if len(all_tags) > 20:
        # Keep first 18 + #TheVideshi + #Reels
        excess = len(all_tags) - 20
        # Remove some category tags from the middle
        cat_tag_list = cat_tags.split()
        trimmed = cat_tag_list[:len(cat_tag_list) - excess]
        cat_tags = " ".join(trimmed)
        caption = f"""{headline}

📰 Read more: https://thevideshi.com/articles/{slug}

{cat_tags}
{topic_str}

#TheVideshi #Reels"""

    return caption.strip()

def mark_instagrammed(article_id):
    now = datetime.now(timezone.utc).isoformat()
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}",
        headers={
            "apikey": SB_SERVICE_KEY,
            "Authorization": f"Bearer {SB_SERVICE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        },
        json={"instagrammed_at": now},
        timeout=15
    )
    if r.status_code in (200, 204):
        print(f"  Marked article {article_id} as instagrammed at {now}")
    else:
        print(f"  WARNING: Failed to mark instagrammed: {r.status_code} {r.text}")

# ── Step 3: Check prebuilt_reels table first ─────────────────────
import glob

prebuilt_reel = None
prebuilt_reel_url = None
prebuilt_caption = None

print("\n=== Checking prebuilt_reels table ===")
try:
    pr_resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/prebuilt_reels",
        params={
            "status": "eq.pending",
            "order": "created_at.asc",
            "limit": "1"
        },
        headers=headers,
        timeout=15
    )
    if pr_resp.status_code == 200 and pr_resp.json():
        prebuilt_reel = pr_resp.json()[0]
        print(f"📦 Found prebuilt reel: {prebuilt_reel['headline']}")
        print(f"   Source: {prebuilt_reel['source']}, Path: {prebuilt_reel['video_path']}")

        # Upload video to Supabase storage if not already uploaded
        if prebuilt_reel.get('video_url'):
            prebuilt_reel_url = prebuilt_reel['video_url']
            print(f"   Already uploaded: {prebuilt_reel_url}")
        else:
            local_path = os.path.expanduser(f"~/workspace/the-videshi-news/{prebuilt_reel['video_path']}")
            if os.path.exists(local_path):
                storage_name = f"reels/prebuilt-{prebuilt_reel['id']}.mp4"
                # Mark uploading
                requests.patch(
                    f"{SUPABASE_URL}/rest/v1/prebuilt_reels?id=eq.{prebuilt_reel['id']}",
                    headers={**headers, "Prefer": "return=minimal"},
                    json={"status": "uploading", "updated_at": "now()"},
                    timeout=15
                )
                with open(local_path, 'rb') as vf:
                    ur = requests.post(
                        f"{SUPABASE_URL}/storage/v1/object/article-images/{storage_name}",
                        headers={
                            "apikey": SB_SERVICE_KEY,
                            "Authorization": f"Bearer {SB_SERVICE_KEY}",
                            "Content-Type": "video/mp4",
                            "x-upsert": "true"
                        },
                        data=vf.read(),
                        timeout=120
                    )
                if ur.status_code in (200, 201):
                    prebuilt_reel_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{storage_name}"
                    # Save URL back to table
                    requests.patch(
                        f"{SUPABASE_URL}/rest/v1/prebuilt_reels?id=eq.{prebuilt_reel['id']}",
                        headers={**headers, "Prefer": "return=minimal"},
                        json={"video_url": prebuilt_reel_url, "updated_at": "now()"},
                        timeout=15
                    )
                    print(f"   ✅ Uploaded: {prebuilt_reel_url}")
                else:
                    print(f"   ⚠️ Upload failed ({ur.status_code}): {ur.text[:200]}")
            else:
                print(f"   ⚠️ Video file not found: {local_path}")
        prebuilt_caption = prebuilt_reel.get('caption')
    else:
        print("No pending prebuilt reels.")
except Exception as e:
    print(f"Prebuilt reels check failed (non-fatal): {e}")

# ── Step 3b: Post Reel — prebuilt or generated ───────────────────
# If we have a prebuilt reel, use its article; otherwise pick from batch
if prebuilt_reel and prebuilt_reel_url:
    # Use the prebuilt reel's linked article
    reel_article_id = prebuilt_reel.get('article_id')
    if reel_article_id:
        ar = requests.get(
            f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{reel_article_id}&select=*&limit=1",
            headers=headers, timeout=15
        )
        if ar.status_code == 200 and ar.json():
            reel_article = ar.json()[0]
        else:
            reel_article = batch[0]
    else:
        reel_article = batch[0]
else:
    reel_article = batch[0]

reel_posted = False
story_posted = False

print(f"\n=== Posting Reel for: {reel_article['headline'][:60]}... ===")

try:
    reel_url = prebuilt_reel_url  # Will be None if no prebuilt

    if not reel_url:
        # No prebuilt reel — generate fresh via generate-reel.py
        result = subprocess.run(
            ["python3", "generate-reel.py", "--slug", reel_article['slug'], "--upload"],
            cwd=os.path.expanduser("~/workspace/the-videshi-news/pipeline"),
            capture_output=True, text=True, timeout=180
        )
        print(f"generate-reel.py exit code: {result.returncode}")
        if result.stdout:
            print(f"STDOUT:\n{result.stdout[-2000:]}")
        if result.stderr:
            print(f"STDERR:\n{result.stderr[-1000:]}")

        # Parse the Supabase URL from output
        for line in result.stdout.split('\n'):
            if 'supabase.co/storage' in line and 'http' in line:
                match = re.search(r'(https://[^\s]+supabase\.co/storage/[^\s]+)', line)
                if match:
                    reel_url = match.group(1)
                    break

    if not reel_url:
        print("ERROR: Could not find reel URL")
        raise Exception("No reel URL found")

    print(f"Reel video URL: {reel_url}")

    # Step A2: Upload cover image to Supabase
    slug_short = reel_article['slug'][:80]
    cover_local = os.path.expanduser(f"~/workspace/the-videshi-news/pipeline/reels/reel-{slug_short}-cover.jpg")
    cover_public_url = None

    if os.path.exists(cover_local):
        cover_filename = f"reels/{slug_short}-cover.jpg"
        with open(cover_local, 'rb') as cf:
            cr = requests.post(
                f"{SUPABASE_URL}/storage/v1/object/article-images/{cover_filename}",
                headers={
                    "apikey": SB_SERVICE_KEY,
                    "Authorization": f"Bearer {SB_SERVICE_KEY}",
                    "Content-Type": "image/jpeg",
                    "x-upsert": "true"
                },
                data=cf.read(),
                timeout=30
            )
        if cr.status_code in (200, 201):
            cover_public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{cover_filename}"
            print(f"Cover uploaded: {cover_public_url}")
        else:
            print(f"Cover upload failed: {cr.status_code} {cr.text}")
    else:
        print(f"No cover image found at {cover_local}")

    # Step B: Quality gate — AI review before posting
    caption = prebuilt_caption if prebuilt_caption else build_caption(reel_article)
    print(f"\nCaption:\n{caption}\n")

    print("🔍 Running AI quality review...")
    reel_pass, reel_feedback = review_reel_quality(reel_article, caption)
    print(f"  Review: {'✅ PASS' if reel_pass else '❌ FAIL'} — {reel_feedback}")

    if not reel_pass:
        print("  ⛔ Reel failed quality review — skipping post")
        if prebuilt_reel:
            requests.patch(
                f"{SUPABASE_URL}/rest/v1/prebuilt_reels?id=eq.{prebuilt_reel['id']}",
                headers={**headers, "Prefer": "return=minimal"},
                json={"status": "failed", "updated_at": "now()"},
                timeout=15
            )
        raise Exception(f"Quality gate rejected: {reel_feedback}")

    # Step B2: Video visual quality gate (GPT-4o + Gemini vision)
    local_reel_path = os.path.expanduser(f"~/workspace/the-videshi-news/pipeline/reels/reel-{reel_article['slug'][:80]}.mp4")
    if os.path.exists(local_reel_path):
        print("  🎥 Running AI video visual review...")
        try:
            _vr = subprocess.run(
                ["python3", os.path.expanduser("~/workspace/the-videshi-news/pipeline/review-reel-video.py"),
                 local_reel_path, "--title", reel_article.get("headline", "")[:100], "--headline", reel_article.get("headline", "")],
                capture_output=True, text=True, timeout=120
            )
            print(_vr.stdout[-500:] if len(_vr.stdout) > 500 else _vr.stdout)
            if _vr.returncode == 1:
                print("  ⛔ Reel failed video visual review — skipping post")
                raise Exception("Video visual quality gate rejected")
            elif _vr.returncode == 2:
                print("  ⚠️ Video review error — proceeding with caution")
        except subprocess.TimeoutExpired:
            print("  ⚠️ Video review timed out — proceeding with caution")
        except Exception as e:
            if "quality gate rejected" in str(e).lower():
                raise
            print(f"  ⚠️ Video review error ({e}) — proceeding with caution")
    else:
        print(f"  ⚠️ Local reel not found for visual review, skipping video check")

    # Step C: Create Reel container

    container_data = {
        "video_url": reel_url,
        "media_type": "REELS",
        "caption": caption,
        "access_token": TOKEN
    }
    if cover_public_url:
        container_data["cover_url"] = cover_public_url

    r = requests.post(
        f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media",
        data=container_data,
        timeout=30
    )
    rj = r.json()
    print(f"Container response: {rj}")

    if 'id' not in rj:
        raise Exception(f"Container creation failed: {rj}")

    container_id = rj['id']

    # Step C: Wait for processing
    print("Waiting for video processing...")
    finished = False
    for i in range(18):
        time.sleep(5)
        r_status = requests.get(
            f"https://graph.instagram.com/v25.0/{container_id}",
            params={"fields": "status_code", "access_token": TOKEN},
            timeout=15
        )
        status = r_status.json().get('status_code', 'UNKNOWN')
        print(f"  Poll {i+1}/18: {status}")
        if status == 'FINISHED':
            finished = True
            break
        elif status == 'ERROR':
            raise Exception(f"Video processing error: {r_status.json()}")

    if not finished:
        print("WARNING: Video processing did not finish in 90s, attempting publish anyway")

    # Step D: Publish Reel
    r2 = requests.post(
        f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media_publish",
        data={"creation_id": container_id, "access_token": TOKEN},
        timeout=30
    )
    r2j = r2.json()
    print(f"Publish response: {r2j}")

    if 'id' in r2j:
        reel_posted = True
        print(f"✅ REEL POSTED — Media ID: {r2j['id']}")
        mark_instagrammed(reel_article['id'])
        # Update prebuilt_reels table if this was a prebuilt reel
        if prebuilt_reel:
            try:
                from datetime import datetime, timezone
                now_ts = datetime.now(timezone.utc).isoformat()
                requests.patch(
                    f"{SUPABASE_URL}/rest/v1/prebuilt_reels?id=eq.{prebuilt_reel['id']}",
                    headers={**headers, "Prefer": "return=minimal"},
                    json={"status": "ig_posted", "ig_media_id": r2j['id'], "ig_posted_at": now_ts, "updated_at": now_ts},
                    timeout=15
                )
                print(f"   📦 Prebuilt reel marked ig_posted")
            except Exception as pe:
                print(f"   ⚠️ Failed to update prebuilt_reels: {pe}")
    else:
        print(f"❌ Reel publish failed: {r2j}")
        if prebuilt_reel:
            try:
                requests.patch(
                    f"{SUPABASE_URL}/rest/v1/prebuilt_reels?id=eq.{prebuilt_reel['id']}",
                    headers={**headers, "Prefer": "return=minimal"},
                    json={"status": "failed", "updated_at": "now()"},
                    timeout=15
                )
            except Exception:
                pass

except Exception as e:
    print(f"❌ Reel posting failed: {e}")
    if prebuilt_reel:
        try:
            requests.patch(
                f"{SUPABASE_URL}/rest/v1/prebuilt_reels?id=eq.{prebuilt_reel['id']}",
                headers={**headers, "Prefer": "return=minimal"},
                json={"status": "failed", "updated_at": "now()"},
                timeout=15
            )
        except Exception:
            pass

# ── Step 4: Post Story for second article (or first if only one) ──
print("\n=== Posting Story ===")
# Use the second article if available, else first
story_article = batch[1] if len(batch) > 1 else batch[0]
# Don't re-story the same article we just reeled unless it's the only one
if len(batch) == 1 and reel_posted:
    print("Only one article available and already posted as Reel. Skipping story.")
else:
    print(f"Story article: {story_article['headline'][:60]}...")

    # Wait between posts
    if reel_posted:
        print("Waiting 30s between posts...")
        time.sleep(30)

    try:
        # Step A: Create story container
        r = requests.post(
            f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media",
            data={
                "image_url": story_article['image_url'],
                "media_type": "STORIES",
                "access_token": TOKEN
            },
            timeout=30
        )
        sj = r.json()
        print(f"Story container response: {sj}")

        if 'id' not in sj:
            raise Exception(f"Story container failed: {sj}")

        story_container_id = sj['id']

        # Step B: Wait for processing
        print("Waiting 8s for story processing...")
        time.sleep(8)

        # Step C: Publish story
        r2 = requests.post(
            f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media_publish",
            data={"creation_id": story_container_id, "access_token": TOKEN},
            timeout=30
        )
        r2j = r2.json()
        print(f"Story publish response: {r2j}")

        if 'id' in r2j:
            story_posted = True
            print(f"✅ STORY POSTED — Media ID: {r2j['id']}")
            # Mark story article as instagrammed too if it's different
            if story_article['id'] != reel_article['id']:
                mark_instagrammed(story_article['id'])
        else:
            print(f"❌ Story publish failed: {r2j}")

    except Exception as e:
        print(f"❌ Story posting failed (non-fatal): {e}")

# ── Summary ──────────────────────────────────────────────────────
print(f"""
========================================
SUMMARY
========================================
Reel posted:  {'✅ YES' if reel_posted else '❌ NO'}
  Article:    {reel_article['headline'][:70]}
Story posted: {'✅ YES' if story_posted else '❌ NO'}
  Article:    {story_article['headline'][:70] if story_article else 'N/A'}
========================================
""")
