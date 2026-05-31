#!/usr/bin/env python3
"""Sports writer for The Videshi — 2026-05-31 batch"""

import json, os, re, time, uuid, subprocess, urllib.parse
import requests

# Load env
env_path = os.path.expanduser("~/.env.supabase")
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            val = val.strip().strip('"').strip("'")
            os.environ[key] = val

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# Load Pexels key
pexels_env = os.path.expanduser("~/workspace/.env.pexels")
PEXELS_KEY = None
if os.path.exists(pexels_env):
    with open(pexels_env) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                val = val.strip().strip('"').strip("'")
                if "PEXELS" in key.upper():
                    PEXELS_KEY = val

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

def fetch_pexels_image(query, fallback_query=None):
    """Fetch image from Pexels using curl (Python urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key found")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ["curl", "-sS", f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5",
                 "-H", f"Authorization: {PEXELS_KEY}"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for photo in photos:
                src = photo.get("src", {})
                url = src.get("large2x") or src.get("large") or src.get("original")
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def upload_image_to_supabase(image_url, filename):
    """Download image and upload to Supabase storage."""
    try:
        r = requests.get(image_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=20)
        if r.status_code != 200:
            print(f"  ⚠ Image download failed: HTTP {r.status_code}")
            # If it's a permanent source (Wikimedia/Pexels), use URL directly
            if "upload.wikimedia.org" in image_url or "images.pexels.com" in image_url:
                print(f"  → Using permanent URL directly")
                return image_url
            return image_url
        content_type = r.headers.get("Content-Type", "image/jpeg")
        if not content_type.startswith("image/"):
            print(f"  ⚠ Not an image: {content_type}")
            return image_url
        if len(r.content) < 5000:
            print(f"  ⚠ Image too small: {len(r.content)} bytes")
            return image_url

        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        upload_headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": content_type,
            "x-upsert": "true",
        }
        ur = requests.post(upload_url, headers=upload_headers, data=r.content, timeout=30)
        if ur.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Supabase upload failed: {ur.status_code} {ur.text[:200]}")
            # If it's a Wikimedia URL, it's permanent and safe to use directly
            if "upload.wikimedia.org" in image_url or "images.pexels.com" in image_url:
                return image_url
            return None
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        if "upload.wikimedia.org" in image_url or "images.pexels.com" in image_url:
            return image_url
        return None

def validate_image_url(url):
    """Validate that an image URL returns a real image."""
    if not url:
        return False
    try:
        r = requests.head(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=10, allow_redirects=True)
        if r.status_code != 200:
            # Try GET for servers that don't support HEAD
            r = requests.get(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=10, stream=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if "image" in ct and cl > 5000:
            return True
        if "image" in ct and cl == 0:
            # Some servers don't return Content-Length with HEAD
            return True
    except:
        pass
    return False

def sb_insert(table, data):
    """Insert a row into Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    r = requests.post(url, headers=HEADERS, json=data, timeout=30)
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            return result[0]
        return result
    else:
        print(f"  ⚠ Insert failed: {r.status_code} {r.text[:300]}")
        return None

def sb_patch(table, filters, data):
    """Patch a row in Supabase."""
    filter_str = "&".join(f"{k}={v}" for k, v in filters.items())
    url = f"{SUPABASE_URL}/rest/v1/{table}?{filter_str}"
    r = requests.patch(url, headers=HEADERS, json=data, timeout=30)
    return r.status_code in (200, 204)


###############################################################################
# ARTICLE 1: Pooja Singh High Jump National Record
###############################################################################

print("\n=== Article 1: Pooja Singh High Jump National Record ===")

art1_slug = "pooja-singh-high-jump-national-record-1-93m-asian-u20-hong-kong-haryana-nri"
art1_headline = "She Practised With Bamboo Poles and Husk Sacks. Now Pooja Singh Is the Highest-Jumping Woman in Indian History."
art1_subheadline = "The nineteen-year-old from a mason's family in rural Haryana cleared 1.93 metres to break a fourteen-year-old national record and win gold at the Asian U20 Championships in Hong Kong."

art1_body = """When Pooja Singh lined up for her second attempt at 1.93 metres at the Asian U20 Athletics Championships in Hong Kong on Friday, the bar had been set at a height no Indian woman had ever cleared in competition. She ran in, planted her foot, arched her back and sailed over it.

Then she broke down in tears on the track.

The nineteen-year-old from Bosti village in Fatehabad, Haryana, had just shattered a national record that had stood for fourteen years. Sahana Kumari's mark of 1.92 metres, set at the 2012 Federation Cup, had survived every Indian high jumper who came after her — until a teenager who first learned to jump over bamboo poles stuck into sacks of husk in a village field decided it was time.

## From Yoga Mat to Landing Pit

Pooja Singh's journey into high jump began, improbably, in a yoga class. Her first coach, Balwan Singh Parta, noticed the extraordinary flexibility in her asanas — particularly her charasana and dhanurasana — and saw the raw material of a high jumper. He recruited her and began training her on whatever equipment they could find.

Her father, Hansraj, is a construction worker. The family had no money for proper facilities. So Pooja improvised: bamboo poles for crossbars, gunny sacks stuffed with husk for landing mats, village fields for training grounds. The gap between where she started and where she has arrived is measured in more than centimetres.

## The Record Sequence

In Hong Kong, Pooja first cleared 1.91 metres to improve her own Under-20 national record. Then she raised the bar to 1.93 metres. Her first attempt clipped the bar. On her second, she cleared it cleanly and the history books were rewritten.

The previous national record of 1.92 metres had been held by Sahana Kumari since 2012 — a mark that had become a kind of ceiling for Indian women's high jump. Kumari herself was in the stands on Friday, now serving as Pooja's current mentor, and was among the first to embrace her after the leap.

Pooja also broke the championship record of 1.90 metres set by Uzbekistan's Svetlana Radzivil in 2006. Emboldened, she took three attempts at 1.96 metres — the Asian junior record — and came agonisingly close but could not clear it.

"Aaj to ho jaata," she had said after narrowly missing 1.92 metres at a meet in Delhi in April. Two months later, she went a centimetre beyond it.

## A Comeback Season

The record was made more remarkable by the fact that Pooja was sidelined for months last year with a Grade 2 ligament tear that threatened her career. When she returned, she joined a new coach — Sergey Biran of Uzbekistan, who had coached his wife Svetlana Radzivil to three Asian Games titles in the same event.

The partnership bore fruit quickly. Pooja won silver at the Asian Indoor Championships in Tianjin in February 2026, then cleared a personal best of 1.90 metres in Delhi in April. Friday's jump of 1.93 metres was thirteen centimetres above her Asian Championships gold-medal height of 1.89 metres from Gumi, South Korea, in 2025 — a staggering improvement in the space of a year.

## What It Means

The 1.93-metre clearance also breaches the Athletics Federation of India's qualification standard of 1.92 metres for the 2026 Commonwealth Games. Whether she will be selected remains to be seen — the Federation Cup in Ranchi was designated as the final qualifying event, and Pooja did not compete there — but a national record holder will be difficult to leave behind.

India's campaign at the Asian U20 Championships has been exceptional. By the end of day three, the team had collected eight gold medals, four silver and three bronze — second only to China on the medal table. Shahnavaz Khan won gold in the men's long jump with a leap of 7.84 metres, Basant cleared 2.20 metres to win the men's high jump, and Nikhil Chandrashekar set a personal best of 9:25.44 to take the 3000-metre steeplechase title.

But the image that will endure from Hong Kong is a teenager from Haryana, crying on the track, with the Indian flag draped over her shoulders and the number 1.93 on the scoreboard above her.

Union Sports Minister Raksha Khadse summed it up: "India is proud of you, Pooja. Your flight will continue to inspire generations to come."

*Sources: PTI, IANS, Athletics Federation of India, RevSportz*"""

# Image: try Wikipedia first
img1_url = fetch_wikipedia_person_image("Pooja Singh (athlete)")
if not img1_url:
    img1_url = fetch_wikipedia_person_image("Pooja Singh high jumper")
if not img1_url:
    print("  Trying Pexels for high jump image...")
    img1_url = fetch_pexels_image("women high jump athletics", "track field high jump competition")

final_img1 = None
if img1_url:
    final_img1 = upload_image_to_supabase(img1_url, f"{art1_slug}.jpg")
    if final_img1 and not validate_image_url(final_img1):
        print(f"  ⚠ Image validation failed for {final_img1[:60]}, trying direct URL...")
        if "upload.wikimedia.org" in img1_url or "images.pexels.com" in img1_url:
            final_img1 = img1_url
        else:
            final_img1 = None

art1_data = {
    "headline": art1_headline,
    "subheadline": art1_subheadline,
    "body": art1_body,
    "slug": art1_slug,
    "category": "sports",
    "vertical": "sports",
    "diaspora_angle": "India's all-time women's high jump record holder is a nineteen-year-old from a mason's family who trained with bamboo poles. Her CWG qualification and national record resonate with NRIs who follow Indian athletics and grassroots sport development stories.",
    "status": "published",
    "published_at": "2026-05-31T06:00:00Z",
    "sources": json.dumps([
        {"name": "PTI", "url": "https://www.ptinews.com/"},
        {"name": "IANS", "url": "https://ianslive.in/"},
        {"name": "Athletics Federation of India", "url": "https://www.indianathletics.in/"},
        {"name": "RevSportz", "url": "https://revsportz.in/"}
    ]),
    "image_url": final_img1,
    "image_attribution": "Wikimedia Commons" if (final_img1 and "wikimedia" in (final_img1 or "").lower()) else "The Videshi",
}

result1 = sb_insert("p2_articles", art1_data)
if result1:
    art1_id = result1.get("id", "unknown")
    print(f"  ✓ Article 1 published: {art1_headline[:60]}... (ID: {art1_id})")
else:
    print(f"  ✗ Article 1 failed to publish")


###############################################################################
# ARTICLE 2: India Women U18 Beat Korea in Hockey Asia Cup
###############################################################################

print("\n=== Article 2: India Women U18 Beat Korea 3-1 ===")

art2_slug = "india-women-u18-hockey-beat-korea-3-1-asia-cup-nousheen-naz-kakamigahara-nri"
art2_headline = "Nousheen Naz Has Now Scored in Every Game. India's U18 Women Beat Korea 3-1 to Top Their Asia Cup Pool."
art2_subheadline = "The fifteen-year-old from Seoni converted a penalty stroke in the fourth minute, Shruti Kumari and Kiran Ekka added field goals, and India sit first in Pool A in Japan."

art2_body = """On the opening day of the U18 Asia Cup in Kakamigahara, a fifteen-year-old from Seoni in Madhya Pradesh scored both goals in a 2-1 win over Malaysia. Two days later, she was at it again.

Nousheen Naz stepped up to take a penalty stroke in the fourth minute on Sunday and calmly beat the Korean goalkeeper to put India ahead. It was her third goal in two matches. She has now scored in every game India have played at this tournament, and the U18 women's team have won both.

India beat Korea 3-1 in their second Pool A match to move to the top of the group with six points from two games. They will face Singapore in their final pool fixture on June 2.

## The Match

India made their intentions clear from the start. The opening quarter saw them dominate possession and create multiple chances. The penalty stroke came in the fourth minute, and Nousheen made no mistake — placing the ball firmly past the Korean keeper to give India a 1-0 lead.

The Indians continued to press in the second quarter. In the twenty-first minute, Shruti Kumari found the back of the net with a clean field goal, doubling the advantage to 2-0 at halftime. India had earned four penalty corners and converted one penalty stroke in the first two quarters, controlling the tempo and keeping Korean counterattacks to a minimum.

Korea attempted to mount a comeback after the break. In the forty-first minute, Gyeongmin Ryu pulled one back to reduce the deficit to 2-1 and give the Koreans a lifeline heading into the final quarter. But India responded swiftly.

Two minutes later, Kiran Ekka, who was later named Player of the Match, converted a penalty corner to restore the two-goal cushion at 3-1. India's defence held firm through the fourth quarter, denying Korea any further opportunities to get back into the contest.

## Nousheen's Rise

The backstory of Nousheen Naz reads like the kind of tale Indian hockey was built on. She comes from Seoni, a small town in central Madhya Pradesh, and picked up a hockey stick in circumstances that would be familiar to anyone who has followed the sport in India's smaller towns — limited facilities, borrowed equipment, a natural ability spotted by a local coach.

At fifteen, she is the youngest player in the Indian squad and already the tournament's most impactful forward. Her three goals in two games have come through a penalty corner against Malaysia, a field goal against Malaysia, and a penalty stroke against Korea — evidence of a player comfortable scoring from any situation.

## The Bigger Picture

India's men's U18 team has been equally dominant in Kakamigahara. They opened with a 13-0 demolition of Kazakhstan on Friday, with captain Ketan Kushwaha scoring a hat-trick and six other players finding the net. The men face hosts Japan on Sunday in what should be a sterner test of their credentials.

Both Indian teams are now in strong positions to top their pools and qualify for the knockout stages. The U18 Asia Cup serves as a key pathway for identifying future senior internationals, and the performances of players like Nousheen Naz, Kushwaha, and Shruti Kumari suggest India's hockey pipeline continues to produce talent at an encouraging rate.

For the NRI community watching from abroad, the tournament is available through Hockey India's streaming channels. India's women play Singapore on June 2, while the men's schedule continues through the group stage this week in Kakamigahara.

The matches are being played in Japan, which means evening kick-offs for viewers in India and early morning starts for those on the US East Coast — a familiar scheduling challenge for diaspora fans who have learned to set alarms for the sports they love.

*Sources: PTI, Hockey India, RevSportz*"""

# Image: try Wikipedia for field hockey or Pexels
img2_url = fetch_pexels_image("women field hockey game", "hockey sport women")

final_img2 = None
if img2_url:
    final_img2 = upload_image_to_supabase(img2_url, f"{art2_slug}.jpg")
    if final_img2 and not validate_image_url(final_img2):
        print(f"  ⚠ Image validation failed, using Pexels direct")
        if "images.pexels.com" in img2_url:
            final_img2 = img2_url
        else:
            final_img2 = None

art2_data = {
    "headline": art2_headline,
    "subheadline": art2_subheadline,
    "body": art2_body,
    "slug": art2_slug,
    "category": "sports",
    "vertical": "sports",
    "diaspora_angle": "India's junior hockey pipeline continues to produce talent at a pace that resonates with NRIs who grew up watching the sport. The U18 Asia Cup in Japan is streamed live, with early-morning starts for US East Coast viewers.",
    "status": "published",
    "published_at": "2026-05-31T06:00:00Z",
    "sources": json.dumps([
        {"name": "PTI", "url": "https://www.ptinews.com/"},
        {"name": "Hockey India", "url": "https://www.hockeyindia.org/"},
        {"name": "RevSportz", "url": "https://revsportz.in/"}
    ]),
    "image_url": final_img2,
    "image_attribution": "The Videshi",
}

result2 = sb_insert("p2_articles", art2_data)
if result2:
    art2_id = result2.get("id", "unknown")
    print(f"  ✓ Article 2 published: {art2_headline[:60]}... (ID: {art2_id})")
else:
    print(f"  ✗ Article 2 failed to publish")

print("\n=== Sports writer batch complete ===")
