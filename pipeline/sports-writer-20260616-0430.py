#!/usr/bin/env python3
"""
Sports Writer — June 16, 2026 (04:30 UTC run)
Article: Team USA at the ICC Men's T20 World Cup 2026 (co-hosted by India and
Sri Lanka) is built almost entirely on Indian-origin cricketers — Monank Patel
(born Anand, Gujarat), Sanjay Krishnamurthi (raised in Bengaluru), Saurabh
Netravalkar (Mumbai), Ali Khan, Milind Kumar, Harmeet Singh, Saiteja Mukkamalla.
A diaspora story: Indians who couldn't break into India's system found a path
to a World Cup wearing the Stars and Stripes — playing on Indian soil.
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
            img = data.get("thumbnail", {}).get("source")
            if img:
                print(f"  \u2713 Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  \u26a0 Wikipedia error for '{person_name}': {e}")
    return None


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
        r = requests.get(img_url, headers={"User-Agent": UA}, timeout=30)
        content = None
        if r.status_code != 200:
            import subprocess
            tmp = f"/tmp/{filename}"
            subprocess.run(["curl", "-sS", "-A", UA, "-o", tmp, img_url], capture_output=True)
            if os.path.exists(tmp) and os.path.getsize(tmp) > 5000:
                content = open(tmp, "rb").read()
            else:
                print(f"  \u2717 Download failed ({r.status_code}) for {img_url[:80]}")
                return None
        else:
            ct = r.headers.get("Content-Type", "")
            if not ct.startswith("image/"):
                print(f"  \u2717 Not an image: {ct}")
                return None
            if len(r.content) < 5000:
                print(f"  \u2717 Image too small: {len(r.content)} bytes")
                return None
            content = r.content

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
            data=compressed,
            timeout=30,
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
print("ARTICLE: Team USA's Indian roots at the T20 World Cup")
print("="*60)

art_slug = "usa-cricket-indian-origin-players-t20-world-cup-2026-monank-patel-sanjay-krishnamurthi-diaspora"
art_headline = "They Couldn't Crack India's System. So They Came to a World Cup on Indian Soil \u2014 Wearing USA's Colours."
art_subheadline = "Monank Patel was born in Anand. Sanjay Krishnamurthi grew up in Bengaluru dreaming of the India cap. At the T20 World Cup co-hosted by India, almost the entire United States side carries Indian blood \u2014 a diaspora team chasing the Super 8s in the country that shaped them."

art_body = """When the United States walked out at the MA Chidambaram Stadium in Chennai to face Namibia, the scorecard read like a roll call from an Indian maidan. Monank Patel. Sanjay Krishnamurthi. Saurabh Netravalkar. Milind Kumar. Harmeet Singh. Saiteja Mukkamalla. Shubham Ranjane. The Stars and Stripes on their chests, the subcontinent in their surnames. They put on 199 for four and beat Namibia by 31 runs \u2014 a second win of the group stage that kept their improbable campaign alive.

It is one of the quiet ironies of this T20 World Cup, co-hosted by India and Sri Lanka, that the team most visibly stocked with Indian-origin talent is not playing for India at all. It is playing for America. And for a sprawling diaspora watching from New Jersey to the Bay Area, that distinction is the whole story.

## The Captain From Anand

Monank Patel, the USA skipper, was born on May 1, 1993 in Anand, Gujarat \u2014 the dairy town better known for Amul than for cricket. He played age-group cricket for his state at the under-16 and under-19 levels, but the Indian pipeline is a brutal funnel, and his career stalled. In 2010 he emigrated, received his green card, and settled in New Jersey, where for years he balanced club cricket with shifts in the restaurant trade. He made his List A debut for the USA in 2018 and, within weeks, became the first American to score a century in the Regional Super50. By 2021 he was captain.

His arc is the diaspora's arc in miniature: a talent that could not find room at home, rerouted through hard work and migration into something improbable \u2014 leading a national team at a World Cup, on the very soil he left behind.

## The Boy Who Dreamed of the India Cap

Sanjay Krishnamurthi's story cuts even closer to the bone. Born in the United States, he moved with his family back to Bengaluru as a child and fell in love with the game watching India's 2011 World Cup triumph alongside his father. Like millions of Indian boys, his ambition was singular: the India jersey. But the competition was ferocious and, as an overseas passport holder, the eligibility maze was unforgiving. "From the moment I started playing cricket in India, the goal was to play for India," he has said. "But I can't bank on anything happening."

So he returned to America, enrolled at San Jose State to study computer science, and channelled his game into the US setup and the San Francisco Unicorns in Major League Cricket. Against Namibia in Chennai he reached a 23-ball fifty and was named Player of the Match \u2014 a 68 that announced him to the wider cricket world on the same Indian grounds where he once dreamed of a different flag.

## A Team Built by Migration

The pattern repeats down the order. Saurabh Netravalkar, the left-arm seamer who became a folk hero when the USA stunned Pakistan in 2024, was raised in Mumbai, played for India at the Under-19 World Cup alongside future stars, then moved to the United States for a software engineering career at Oracle before cricket pulled him back. Ali Khan, born in Pakistan, was American cricket's first genuine T20 franchise star. Milind Kumar piled up runs in Indian domestic cricket before crossing over. Harmeet Singh, once a celebrated India Under-19 spinner, found his second act under the Stars and Stripes.

This is not an accident of selection. It is the demographic reality of American cricket, a sport sustained almost entirely by South Asian immigrants \u2014 the engineers, doctors and entrepreneurs who built weekend leagues in suburban parks from Dallas to Edison, and whose children now fill the academies. Major League Cricket, launched in 2023, gave that community a professional ladder. Team USA is what it produced.

## The Super 8 Maths

On the field, the campaign hangs by a thread. The USA finished their Group A fixtures on four points with a healthy net run rate, courtesy of a dominant 93-run win over the Netherlands and the victory over Namibia. But their route to the Super 8s is narrow and out of their hands: they need one of India \u2014 already through \u2014 or Pakistan to slip up and fall behind them on net run rate. It is the familiar lot of the associate side, brilliant enough to win games, still waiting on the giants to leave a door ajar.

Win or go home, the Americans have already made their point. A team of Indian-origin cricketers, many of whom were told in one way or another that there was no place for them at home, has turned up at a World Cup hosted by that same home and refused to be a pushover.

## Why It Matters to the Diaspora

For NRIs in the United States, this is the rare sporting moment that belongs entirely to them. These are not distant icons; they are the sons of the same migration story \u2014 men who packed up from Gujarat and Karnataka and Maharashtra, chased visas and degrees and second chances, and built a cricket culture in a country that barely knew the game. When Monank Patel lifts his bat in Chennai or Sanjay Krishnamurthi clears the ropes, the Indian-American living room erupts not for India, and not quite for a foreign team either, but for something in between: a reflection of itself. The Super 8s may or may not come. The deeper victory \u2014 seeing your own community's children walk out at a World Cup, on the old soil, under a new flag \u2014 has already been won."""

print("\nSourcing image...")
# Hero: MA Chidambaram Stadium, Chennai — the actual venue where USA beat
# Namibia. Permanent Wikimedia Commons URL, real and relevant.
img_candidate = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/MA_Chidambaram_Stadium_In_the_Night_during_a_CSK_Game.jpg/1280px-MA_Chidambaram_Stadium_In_the_Night_during_a_CSK_Game.jpg"
img_caption = "The MA Chidambaram Stadium in Chennai, where the USA beat Namibia in the T20 World Cup 2026"
img_attribution = "Wikimedia Commons"

img_final = upload_to_supabase(img_candidate, f"{art_slug}.jpg")

if not img_final:
    # Fallback: USA squad photo on Commons
    img_final = upload_to_supabase(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/USA_Squad_Photo_2017.jpg/1280px-USA_Squad_Photo_2017.jpg",
        f"{art_slug}-squad.jpg")
    if img_final:
        img_caption = "The United States national cricket squad"

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
        {"name": "Cricbuzz \u2014 USA beat Namibia, T20 World Cup 2026", "url": "https://www.cricbuzz.com"},
        {"name": "CricTracker \u2014 USA in queue for direct qualification", "url": "https://www.crictracker.com"},
        {"name": "Sporting News \u2014 Who is Monank Patel? Gujarat-born cricketer leading USA", "url": "https://www.sportingnews.com"},
        {"name": "Sports Illustrated \u2014 Sanjay Krishnamurthi: A Rising Star in American Cricket", "url": "https://www.si.com"},
    ]),
    "diaspora_angle": "Almost the entire United States cricket team at the India-hosted T20 World Cup is made up of Indian-origin players who couldn't break into India's system \u2014 a story that belongs squarely to the Indian-American community that built cricket in the US.",
    "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}

art_id = insert_article(art_data)

print("\n" + "="*60)
print("DONE")
print("="*60)
mark = "\u2713" if art_id else "\u2717"
print(f"Article: {mark} {art_slug}")
print(f"Word count: ~{len(art_body.split())} words")
print("Set to status='review'")
