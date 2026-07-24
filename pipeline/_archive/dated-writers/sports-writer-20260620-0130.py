#!/usr/bin/env python3
"""
Sports Writer — June 20, 2026 (01:30 UTC slot)
Article: India begin a five-Test tour of England at Headingley on June 20 — the
first match of the new Anderson-Tendulkar Trophy and the dawn of the Shubman
Gill captaincy era, after the Test retirements of Rohit Sharma and Virat Kohli.

ANGLE: This is a PREVIEW of a brand-new chapter for Indian Test cricket. Recent
sports coverage has been women's T20 WC, Neeraj Chopra, MLC, hockey, World Cup
soccer — nothing on the men's Test side's England tour. The series opens
tomorrow (June 20) at Headingley. The story is the generational handover: Gill
(25) named captain, Pant his deputy, Bumrah managing his workload across only
part of the series, and the Pataudi Trophy retired in favour of the
Anderson-Tendulkar Trophy. Huge for the UK diaspora especially.

Hero: Wikipedia portrait of Shubman Gill (upload.wikimedia.org), then Commons.
"""

import os, sys, json, io
from datetime import datetime, timezone

import requests
from PIL import Image

# ── ENV ──
env_supa = os.path.expanduser("~/.env.supabase")
for line in open(env_supa):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ[k] = v.strip().strip('"').strip("'")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
UA = "TheVideshi/1.0 (thevideshi.com)"
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


def fetch_wikipedia_person_image(person_name):
    encoded = person_name.replace(" ", "_")
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  \u2713 Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  \u26a0 Wikipedia error for '{person_name}': {e}")
    return None


def fetch_wikimedia_commons_images(search_query, limit=8):
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json",
    }
    out = []
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params, headers={"User-Agent": UA}, timeout=15,
        )
        if r.status_code == 200:
            pages = r.json().get("query", {}).get("pages", {})
            for p in pages.values():
                ii = (p.get("imageinfo") or [{}])[0]
                url = ii.get("thumburl") or ii.get("url")
                mime = ii.get("mime", "")
                if url and mime.startswith("image/") and ii.get("width", 0) >= 800:
                    out.append({"url": url, "title": p.get("title", ""),
                                "w": ii.get("width"), "h": ii.get("height")})
    except Exception as e:
        print(f"  \u26a0 Commons error for '{search_query}': {e}")
    return out


def compress_image(img_bytes, max_width=1200, quality=80):
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()


def upload_to_supabase(img_url, filename):
    try:
        import subprocess
        tmp = f"/tmp/{filename}"
        subprocess.run(["curl", "-sS", "-A", UA, "-o", tmp, img_url], capture_output=True)
        if not (os.path.exists(tmp) and os.path.getsize(tmp) > 5000):
            print(f"  \u2717 Download failed for {img_url[:80]}")
            return None
        content = open(tmp, "rb").read()
        compressed = compress_image(content)
        print(f"  \U0001f4e6 Compressed to {len(compressed)/1024:.0f} KB")
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        resp = requests.post(
            upload_url,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "image/jpeg",
                "x-upsert": "true",
            },
            data=compressed, timeout=30,
        )
        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  \u2713 Uploaded: {public_url}")
            return public_url
        else:
            print(f"  \u2717 Upload failed ({resp.status_code}): {resp.text[:200]}")
            return None
    except Exception as e:
        print(f"  \u2717 Upload error: {e}")
        return None


def insert_article(article):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS, json=article, timeout=30,
    )
    if r.status_code in (200, 201):
        result = r.json()
        art_id = result[0]["id"] if isinstance(result, list) else result.get("id")
        print(f"  \u2713 Inserted article: {article['slug']} (id={art_id})")
        return art_id
    else:
        print(f"  \u2717 Insert failed ({r.status_code}): {r.text[:300]}")
        return None


print("\n" + "="*60)
print("ARTICLE: India open England tour — new captain, new trophy, new era")
print("="*60)

art_slug = "india-england-first-test-headingley-2026-shubman-gill-captain-anderson-tendulkar-trophy-new-era-rohit-kohli-retired-pant-bumrah-nri"
art_headline = "New Captain, New Trophy, New Era: India Begin in England Without Rohit and Kohli for the First Time in a Generation"
art_subheadline = "When the first ball is bowled at Headingley on Saturday, it will open the Anderson-Tendulkar Trophy, the 2025-27 World Test Championship, and the captaincy of 25-year-old Shubman Gill \u2014 with the two batters who defined Indian cricket for 15 years watching from home."

art_body = """LEEDS \u2014 For the better part of two decades, an India Test team that walked out at an English ground did so with at least one of Rohit Sharma or Virat Kohli in its ranks. On Saturday morning at Headingley, when Shubman Gill leads his side onto the field for the first ball of a five-match series, neither will be there. Both have retired from the format within the past few weeks, and Indian Test cricket has, almost overnight, become a young man's project.

The match that begins the tour is layered with firsts. It is the opening Test of the new World Test Championship cycle, the 2025-27 edition. It is the first to be played for the Anderson-Tendulkar Trophy, the freshly minted prize that replaces the Pataudi Trophy on English soil and the Anthony de Mello Trophy in India, unifying the rivalry under the names of two of its greatest figures. And it is the first Test in charge for Gill, at 25 one of the youngest men India has ever handed the red-ball captaincy.

## The Handover

The generational shift was not gradual. Kohli announced his Test retirement on May 12, signing off with 9,230 runs from 123 matches at an average of 46.85, ending a 14-year career with the line "#269, signing off." Rohit had already stepped away from the format, and with him went the last of the senior leadership group that had carried India to two World Test Championship finals.

That left the selectors searching for a captain who could be relied upon to play every match of a long, demanding overseas series. Jasprit Bumrah, the obvious cricketing choice, was ruled out of contention by his own workload: managing a history of back trouble, he is not expected to feature in all five Tests, and a part-time captain was not what the moment called for. The job went instead to Gill, with Rishabh Pant \u2014 a proven match-winner in Australia, England and South Africa \u2014 named his vice-captain.

"You want to name a captain who can help the team going forward rather than having someone for one or two tours," chief selector Ajit Agarkar said when the appointment was confirmed. "It is going to be as tough as it gets, maybe he will learn on the job, but we have seen what he can do."

## What India Bring

Gill inherits a side caught between eras. Yashasvi Jaiswal and Sai Sudharsan represent the new top order; KL Rahul and the recalled Karun Nair offer experience; Ravindra Jadeja and Washington Sundar provide the all-round balance that English conditions reward. The bowling, as ever on these tours, will lean on Bumrah when he plays, with Mohammed Siraj, Prasidh Krishna and the returning Mohammed Shami sharing the new-ball load and Shardul Thakur and Nitish Kumar Reddy adding seam-bowling depth.

The conditions will test all of it. Headingley has long been a venue where the Dukes ball talks \u2014 late swing, low scores, sudden collapses \u2014 and the forecast for much of the series leans overcast. India may be tempted into an all-seam attack on the first morning, a luxury they rarely enjoy at home but one English summers demand.

## Why It Matters to the Diaspora

Few sporting events mobilise the Indian diaspora in Britain quite like an India tour of England. Headingley, Lord's, Edgbaston and The Oval fill with travelling support; the grounds turn into a home-from-home of flags, drums and three generations in the same row. For families who emigrated decades ago, these five Tests are a fixed point in the calendar \u2014 a chance to take children born in Leeds or London to watch the team their grandparents grew up on.

This summer carries an added weight. The crowds that show up will be watching not just a series but a transition: the first sustained look at what India look like after Rohit and Kohli, under a captain young enough to be the son of the fans who remember Sachin Tendulkar's tours of the same grounds. The trophy now bears Tendulkar's name; the team chasing it belongs to a generation that grew up idolising him.

## What's Next

India have not won a Test series in England since 2007, and the recent record reads as a string of near-misses and drawn series. Gill's brief is not only to compete but to set a tone for a rebuilt side over the next two years of the WTC cycle. The first answers come quickly: win the toss, read the Headingley sky, and survive the first session against a Dukes ball in English hands. For a captain on debut, with a new trophy on the line and two legends absent from the dressing room, there is no gentler way to begin."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image...")
img_caption = "Shubman Gill, named India's new Test captain for the 2026 tour of England"
img_attribution = "Wikimedia Commons"
img_final = None

# 1) Subject athlete (Wikipedia portrait)
for person, cap in [
    ("Shubman Gill", "Shubman Gill, who leads India in his first Test as captain at Headingley"),
]:
    wiki_img = fetch_wikipedia_person_image(person)
    if wiki_img:
        got = upload_to_supabase(wiki_img, f"{art_slug}.jpg")
        if got:
            img_final = got
            img_caption = cap
            break

# 2) Fallback: on-topic Commons imagery
if not img_final:
    for q in ["Shubman Gill", "Shubman Gill cricket", "Headingley cricket ground", "India cricket team Test"]:
        cands = fetch_wikimedia_commons_images(q)
        for c in cands:
            low = c["title"].lower()
            print(f"   candidate: {c['title']} ({c['w']}x{c['h']})")
            if any(bad in low for bad in ["logo", ".svg", ".pdf", "map", "seating",
                                           "letters", "diagram", "chart", "flag", "icon"]):
                continue
            if not any(g in low for g in ["gill", "headingley", "cricket", "india"]):
                continue
            got = upload_to_supabase(c["url"], f"{art_slug}.jpg")
            if got:
                img_final = got
                if "gill" in low:
                    img_caption = "Shubman Gill, India's new Test captain"
                elif "headingley" in low:
                    img_caption = "Headingley Cricket Ground in Leeds, venue for the first Test"
                else:
                    img_caption = "India's Test side ahead of the 2026 England tour"
                break
        if img_final:
            break

if not img_final:
    print("  \u26a0 No image uploaded \u2014 inserting without image")

art_data = {
    "headline": art_headline,
    "subheadline": art_subheadline,
    "body": art_body,
    "slug": art_slug,
    "category": "sports",
    "vertical": "cricket",
    "status": "review",
    "is_editorial": False,
    "image_url": img_final or "",
    "image_caption": img_caption,
    "image_attribution": img_attribution,
    "sources": json.dumps([
        {"name": "CricTracker \u2014 Ajit Agarkar backs Shubman Gill as long-term leadership option", "url": "https://www.crictracker.com/"},
        {"name": "The Indian Eye \u2014 Indian Test cricket awaits a new era: Shubman Gill as Captain, Rishabh Pant as Vice-Captain", "url": "https://theindianeye.com/"},
        {"name": "CricTracker \u2014 England-India Test series set to be renamed as Anderson-Tendulkar Trophy", "url": "https://www.crictracker.com/"},
        {"name": "Cricbuzz \u2014 Virat Kohli bows out of Test cricket", "url": "https://www.cricbuzz.com/"},
        {"name": "Cricbuzz \u2014 Pant, Pujara and Bumrah to represent Leicestershire in warm-up fixture", "url": "https://www.cricbuzz.com/"},
    ]),
    "diaspora_angle": "An India tour of England is a fixed point on the British-Indian calendar, filling Headingley, Lord's and Edgbaston with travelling support \u2014 and this summer the diaspora gets its first sustained look at the post-Rohit, post-Kohli team under a new captain, playing for a trophy now bearing Sachin Tendulkar's name.",
    "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}

art_id = insert_article(art_data)

print("\n" + "="*60)
print("DONE")
print("="*60)
mark = "\u2713" if art_id else "\u2717"
print(f"Article: {mark} {art_slug}")
print(f"Word count: ~{len(art_body.split())} words")
print(f"Image: {img_final or '(none)'}")
print("Set to status='review'")
