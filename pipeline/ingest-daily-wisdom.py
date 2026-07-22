#!/usr/bin/env python3
"""
Daily Wisdom Ingestion Pipeline
Fetches spiritual teachings from YouTube channels across traditions,
extracts wisdom quotes via GPT, and stores in the daily_wisdom table.
"""

import json, os, sys, time, hashlib, subprocess, re
from datetime import datetime, timedelta, date
from urllib.parse import quote

# ── Config ──────────────────────────────────────────────────────────────
TEACHERS = [
    # Hindu / Yoga
    {"name": "Sadhguru", "channel_id": "UCtL6NhEiPLTByMGBhOD6a1g", "tradition": "Hindu / Yoga", "search_terms": ["wisdom", "life", "meditation", "consciousness"], "image": "https://yt3.googleusercontent.com/ytc/AIdro_na07UlC-qu3VXOQ6ME3sx8BVrBey0Z8DxNFhvqB8PBSg=s176-c-k-c0x00ffffff-no-rj"},
    {"name": "Sri Sri Ravi Shankar", "channel_id": "UC3VNfbjmaxpseKEis8G0m1g", "tradition": "Hindu / Yoga", "search_terms": ["wisdom", "knowledge", "meditation", "peace"], "image": "https://yt3.googleusercontent.com/ytc/AIdro_kN5hHs1RbFDXeqj8jLi-llhln-F5dSxFOALRlVrNP-gg=s176-c-k-c0x00ffffff-no-rj"},
    {"name": "BK Shivani", "channel_id": "UCsRPErhHNBN5pBJCMdYaN2g", "tradition": "Hindu / Yoga", "search_terms": ["English", "wisdom", "peace", "relationships"], "image": "https://yt3.googleusercontent.com/ytc/AIdro_lDSl6Ry2z7P10OM8ZkCQ_8o3fhHK-X5V0HV6VR0T1GlQ=s176-c-k-c0x00ffffff-no-rj"},
    {"name": "Gaur Gopal Das", "channel_id": "UCFv9KILAifYCmbsNiYI_fhA", "tradition": "Hindu / Yoga", "search_terms": ["life", "happiness", "wisdom", "purpose"], "image": "https://yt3.googleusercontent.com/ytc/AIdro_nFWr4BjDY3hKkJOIK7H8RVz4BY3Tm_A6_NuKQFPbWCUQ=s176-c-k-c0x00ffffff-no-rj"},
    {"name": "Mooji", "channel_id": "UCpw2gh99XM6Mwsbksv0feEg", "tradition": "Hindu / Yoga", "search_terms": ["satsang", "awareness", "self", "truth"], "image": "https://yt3.googleusercontent.com/ytc/AIdro_lh0-dBnN7G0h7bJfWJHZ1l2WMdD_5xtUJfHn0=s176-c-k-c0x00ffffff-no-rj"},
    
    # Buddhist
    {"name": "Dalai Lama", "channel_id": "UCiPJ_g02LuOgOG0ZNk5j1jA", "tradition": "Buddhist", "search_terms": ["compassion", "peace", "wisdom", "teaching"], "image": "https://yt3.googleusercontent.com/ytc/AIdro_nE2PJpOGAP5-KWG0lE9j4KPtUvqNJxQ1F7VxH2=s176-c-k-c0x00ffffff-no-rj"},
    {"name": "Plum Village", "channel_id": "UCcflNOLE_HkuELsBaGiYWYw", "tradition": "Buddhist", "search_terms": ["thich nhat hanh", "mindfulness", "peace", "meditation"], "image": "https://yt3.googleusercontent.com/ytc/AIdro_kd7lMKR_CPbLl9k4mElAqNqyT-97pEq0wHRxXn=s176-c-k-c0x00ffffff-no-rj"},
    
    # Interfaith / Modern
    {"name": "Deepak Chopra", "channel_id": "UCfEwFbc4sB2lyyyP7OFNjYQ", "tradition": "Interfaith / Modern", "search_terms": ["meditation", "consciousness", "wisdom", "healing"], "image": "https://yt3.googleusercontent.com/ytc/AIdro_kCeNHRjOoX7EV5YR0W_WJwPjWfKgIe_dw6NuLl=s176-c-k-c0x00ffffff-no-rj"},
    {"name": "Jay Shetty", "channel_id": "UCbV60AGIHKz3F3O1M-YTrzA", "tradition": "Interfaith / Modern", "search_terms": ["purpose", "mindfulness", "wisdom", "relationships"], "image": "https://yt3.googleusercontent.com/ytc/AIdro_k9IcIXFCdCWBfW9xPfLSCOg-WqXg6-lJcJxKRO=s176-c-k-c0x00ffffff-no-rj"},
    {"name": "Eckhart Tolle", "channel_id": "UCJ9rNTfBMnReELNy94AcJKg", "tradition": "Interfaith / Modern", "search_terms": ["presence", "consciousness", "ego", "awareness"], "image": "https://yt3.googleusercontent.com/ytc/AIdro_kKEAJ_Oy_TLYO1qH2WZGn5GI6lJV31ygMJ_h4C=s176-c-k-c0x00ffffff-no-rj"},
    
    # Sikh
    {"name": "Basics of Sikhi", "channel_id": "UC3vVQJ59Lqrv_uW_fHexk8g", "tradition": "Sikh", "search_terms": ["gurbani", "wisdom", "sikhi", "spiritual"], "image": "https://yt3.googleusercontent.com/ytc/AIdro_kZvZw_DPu_8m7Hg-Tq5YWwcG5hSnO3U=s176-c-k-c0x00ffffff-no-rj"},
    {"name": "Nanak Naam", "channel_id": "UCaxTUBLCIG99yNGcbf0bulg", "tradition": "Sikh", "search_terms": ["meditation", "naam", "consciousness", "peace"], "image": "https://yt3.googleusercontent.com/ytc/AIdro_kH5p-F2m3f5nA0dQ0P1xq6aexJYjN=s176-c-k-c0x00ffffff-no-rj"},
    
    # Islamic
    {"name": "Omar Suleiman", "channel_id": "UCfL6PrCfJP5a3EyiJvgRxXA", "tradition": "Islamic", "search_terms": ["faith", "spirituality", "wisdom", "patience"], "image": "https://yt3.googleusercontent.com/ytc/AIdro_lC0LSTqYy_YK5HEEgQxUh0d-9PpbqZyGzR=s176-c-k-c0x00ffffff-no-rj"},
    
    # Jain
    {"name": "Pujya Gurudevshri Rakeshji", "channel_id": "UCcQIW8E4_4DmyF0ENBICxTQ", "tradition": "Jain", "search_terms": ["atma", "dharma", "meditation", "wisdom"], "image": ""},
]

# YouTube API
def get_youtube_api_key():
    """Get YouTube API key via OAuth refresh token."""
    env = {}
    with open(os.path.expanduser("~/workspace/.env.youtube")) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                k = k.replace("export ", "").strip()
                env[k] = v.strip().strip('"').strip("'")
    
    # Refresh the access token
    r = subprocess.run(
        ["curl", "-s", "-X", "POST", "https://oauth2.googleapis.com/token",
         "-d", f"client_id={env['YOUTUBE_CLIENT_ID']}&client_secret={env['YOUTUBE_CLIENT_SECRET']}&refresh_token={env['YOUTUBE_REFRESH_TOKEN']}&grant_type=refresh_token"],
        capture_output=True, text=True
    )
    data = json.loads(r.stdout)
    return data.get("access_token")


def search_youtube_channel(channel_id, query, access_token, max_results=5):
    """Search a YouTube channel for videos matching a query."""
    url = (
        f"https://www.googleapis.com/youtube/v3/search"
        f"?channelId={channel_id}"
        f"&q={quote(query)}"
        f"&type=video"
        f"&order=date"
        f"&maxResults={max_results}"
        f"&part=snippet"
        f"&videoDuration=short"  # Under 4 min — short wisdom clips
    )
    r = subprocess.run(
        ["curl", "-s", url, "-H", f"Authorization: Bearer {access_token}"],
        capture_output=True, text=True
    )
    try:
        return json.loads(r.stdout)
    except:
        print(f"  ⚠ Failed to parse YouTube response for {channel_id}: {r.stdout[:200]}")
        return {"items": []}


def extract_wisdom_quote(title, description, teacher_name, tradition):
    """Use GPT-4o-mini to extract a clean wisdom quote from a YouTube video's title and description."""
    env = {}
    with open(os.path.expanduser("~/workspace/.env.openai")) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                k = k.replace("export ", "").strip()
                env[k] = v.strip().strip('"').strip("'")
    
    prompt = f"""You are extracting a daily wisdom quote for a spiritual content section on a news website.

Given this YouTube video from {teacher_name} ({tradition} tradition):
Title: {title}
Description (first 500 chars): {description[:500]}

Extract or compose a concise, impactful wisdom teaching (2-4 sentences max) that captures the essence of this video's spiritual message. It should:
1. Be meaningful, contemplative, and universally applicable
2. Sound like a direct teaching from {teacher_name}
3. Not mention YouTube, videos, or links
4. Not be promotional or about events/products
5. Be in English

If the title/description is not actually spiritual content (it's promotional, event logistics, or not in English), return SKIP.

Return ONLY the quote text, nothing else. Or SKIP if not suitable."""

    payload = json.dumps({
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 200
    })
    
    r = subprocess.run(
        ["curl", "-s", "-X", "POST", "https://api.openai.com/v1/chat/completions",
         "-H", f"Authorization: Bearer {env['OPENAI_API_KEY']}",
         "-H", "Content-Type: application/json",
         "-d", payload],
        capture_output=True, text=True
    )
    
    try:
        data = json.loads(r.stdout)
        content = data["choices"][0]["message"]["content"].strip()
        if content == "SKIP" or "SKIP" in content[:10]:
            return None
        return content
    except Exception as e:
        print(f"  ⚠ GPT extraction failed: {e}")
        return None


def upsert_wisdom(entry):
    """Insert a wisdom entry into the daily_wisdom table."""
    env = {}
    with open(os.path.expanduser("~/workspace/.env.supabase")) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                k = k.replace("export ", "").strip()
                env[k] = v.strip().strip('"').strip("'")
    
    url = f"{env['SUPABASE_URL']}/rest/v1/daily_wisdom"
    payload = json.dumps(entry)
    
    r = subprocess.run(
        ["curl", "-s", "-X", "POST", url,
         "-H", f"apikey: {env['SUPABASE_SERVICE_ROLE_KEY']}",
         "-H", f"Authorization: Bearer {env['SUPABASE_SERVICE_ROLE_KEY']}",
         "-H", "Content-Type: application/json",
         "-H", "Prefer: return=representation",
         "-d", payload],
        capture_output=True, text=True
    )
    
    try:
        data = json.loads(r.stdout)
        if isinstance(data, list) and len(data) > 0:
            return data[0].get("id")
        elif isinstance(data, dict) and "message" in data:
            print(f"  ⚠ Upsert failed: {data['message']}")
            return None
    except:
        print(f"  ⚠ Upsert parse failed: {r.stdout[:200]}")
    return None


def assign_featured_dates():
    """Assign featured_date to unfeatured wisdom entries, rotating across traditions."""
    env = {}
    with open(os.path.expanduser("~/workspace/.env.supabase")) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                k = k.replace("export ", "").strip()
                env[k] = v.strip().strip('"').strip("'")
    
    url = f"{env['SUPABASE_URL']}/rest/v1/daily_wisdom"
    
    # Get the latest featured date
    r = subprocess.run(
        ["curl", "-s", f"{url}?select=featured_date&featured_date=not.is.null&order=featured_date.desc&limit=1",
         "-H", f"apikey: {env['SUPABASE_SERVICE_ROLE_KEY']}",
         "-H", f"Authorization: Bearer {env['SUPABASE_SERVICE_ROLE_KEY']}"],
        capture_output=True, text=True
    )
    
    latest_rows = json.loads(r.stdout) if r.stdout.strip() else []
    if latest_rows and latest_rows[0].get("featured_date"):
        next_date = datetime.strptime(latest_rows[0]["featured_date"], "%Y-%m-%d").date() + timedelta(days=1)
    else:
        next_date = date.today()
    
    # Get unfeatured entries
    r = subprocess.run(
        ["curl", "-s", f"{url}?select=id,teacher_name,tradition&featured_date=is.null&is_approved=eq.true&order=created_at.asc",
         "-H", f"apikey: {env['SUPABASE_SERVICE_ROLE_KEY']}",
         "-H", f"Authorization: Bearer {env['SUPABASE_SERVICE_ROLE_KEY']}"],
        capture_output=True, text=True
    )
    
    unfeatured = json.loads(r.stdout) if r.stdout.strip() else []
    if not unfeatured:
        print("No unfeatured entries to schedule.")
        return
    
    # Sort to maximize tradition variety — round-robin across traditions
    traditions = list(set(e["tradition"] for e in unfeatured))
    tradition_queues = {t: [e for e in unfeatured if e["tradition"] == t] for t in traditions}
    
    scheduled = []
    last_teacher = ""
    while any(tradition_queues.values()):
        for t in traditions:
            if tradition_queues[t]:
                entry = tradition_queues[t].pop(0)
                # Skip if same teacher as last
                if entry["teacher_name"] == last_teacher and any(tradition_queues.values()):
                    # Put back and try next tradition
                    tradition_queues[t].append(entry)
                    continue
                scheduled.append(entry)
                last_teacher = entry["teacher_name"]
    
    # Assign dates
    for entry in scheduled:
        d = next_date.isoformat()
        r = subprocess.run(
            ["curl", "-s", "-X", "PATCH",
             f"{url}?id=eq.{entry['id']}",
             "-H", f"apikey: {env['SUPABASE_SERVICE_ROLE_KEY']}",
             "-H", f"Authorization: Bearer {env['SUPABASE_SERVICE_ROLE_KEY']}",
             "-H", "Content-Type: application/json",
             "-d", json.dumps({"featured_date": d})],
            capture_output=True, text=True
        )
        print(f"  📅 {d}: {entry['teacher_name']} ({entry['tradition']})")
        next_date += timedelta(days=1)
    
    print(f"\nScheduled {len(scheduled)} wisdom entries from {date.today()} onwards.")


def main():
    print("=" * 60)
    print(f"Daily Wisdom Ingestion — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    # Get YouTube access token
    print("\n🔑 Getting YouTube access token...")
    access_token = get_youtube_api_key()
    if not access_token:
        print("❌ Failed to get YouTube access token")
        sys.exit(1)
    print("✅ Got access token")
    
    total_added = 0
    
    for teacher in TEACHERS:
        print(f"\n🙏 {teacher['name']} ({teacher['tradition']})")
        
        # Search for recent wisdom videos
        for term in teacher["search_terms"][:2]:  # Limit to 2 search terms per teacher
            results = search_youtube_channel(
                teacher["channel_id"], term, access_token, max_results=3
            )
            
            items = results.get("items", [])
            if not items:
                print(f"  No results for '{term}'")
                continue
            
            for item in items:
                snippet = item.get("snippet", {})
                video_id = item.get("id", {}).get("videoId", "")
                title = snippet.get("title", "")
                description = snippet.get("description", "")
                thumbnail = snippet.get("thumbnails", {}).get("high", {}).get("url", "")
                
                if not title or not video_id:
                    continue
                
                # Skip non-English titles
                if re.search(r'[\u0900-\u097F\u0980-\u09FF\u0A00-\u0A7F]', title):
                    print(f"  ⏭ Skipping non-English: {title[:50]}")
                    continue
                
                print(f"  📹 {title[:60]}...")
                
                # Extract wisdom quote via GPT
                quote_text = extract_wisdom_quote(title, description, teacher["name"], teacher["tradition"])
                if not quote_text:
                    print(f"    ⏭ Skipped (not suitable)")
                    continue
                
                # Build entry
                entry = {
                    "teacher_name": teacher["name"],
                    "tradition": teacher["tradition"],
                    "quote": quote_text,
                    "source_title": title,
                    "source_url": f"https://www.youtube.com/watch?v={video_id}",
                    "source_type": "youtube",
                    "thumbnail_url": thumbnail,
                    "teacher_image_url": teacher.get("image", ""),
                    "video_id": video_id,
                }
                
                result_id = upsert_wisdom(entry)
                if result_id:
                    print(f"    ✅ Added: {quote_text[:60]}...")
                    total_added += 1
                
                time.sleep(0.5)  # Rate limit
            
            time.sleep(1)  # Between search terms
    
    print(f"\n{'=' * 60}")
    print(f"Total new wisdom entries: {total_added}")
    
    # Assign featured dates
    if total_added > 0:
        print("\n📅 Assigning featured dates...")
        assign_featured_dates()
    
    print(f"\n✅ Done!")


if __name__ == "__main__":
    main()
