#!/usr/bin/env python3
"""
Sports Writer — June 19, 2026 (13:30 UTC run)
Article: India's women are 2-0 and top of Group A at the T20 World Cup in
England, having dismantled Pakistan (by 64 runs) and the Netherlands (by 95
runs, a record-laden 209/5). Smriti Mandhana is in imperious form; Shafali
Verma rediscovered hers; Shree Charani is the breakout bowler. Next up: South
Africa at Old Trafford on June 21.

ANGLE: A campaign overview — NOT a single-match report. The Videshi covered the
Netherlands match on its own, but has not framed the WHOLE group-stage surge:
the reigning ODI world champions chasing the one global title that has eluded
them, two from two, NRR-leading, with the diaspora across England and the US
tuning in on JioHotstar. Bittersweet sub-thread: Shreyanka Patil's ankle injury.

Hero: Smriti Mandhana has a Wikipedia/Commons portrait. Fall back to on-topic
Commons cricket imagery, then skip.
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
print("ARTICLE: India women 2-0 at T20 World Cup — campaign overview")
print("="*60)

art_slug = "india-women-t20-world-cup-2026-group-a-unbeaten-mandhana-shafali-charani-south-africa-old-trafford-diaspora-nri"
art_headline = "Two From Two, and the One Trophy They've Never Won Looks Closer Than Ever"
art_subheadline = "India's women, reigning 50-over world champions, have opened the T20 World Cup in England with a 64-run rout of Pakistan and a record-breaking 95-run demolition of the Netherlands \u2014 and a diaspora that has waited a generation for this is watching."

art_body = """MANCHESTER \u2014 For all that India's women have achieved \u2014 a maiden 50-over World Cup on home soil last year, a generation of stars who have made the WPL a global draw \u2014 one prize has always slipped through their fingers. The Twenty20 World Cup has been a tournament of near-misses: five semi-final appearances, one heartbreaking final in 2020, and never the title. Two matches into the 2026 edition in England, the Women in Blue look better placed than they have ever been to change that.

India sit top of Group A, unbeaten, having dispatched their two opening opponents with a ruthlessness that has put the rest of the field on notice. They beat Pakistan by 64 runs at Edgbaston, then produced one of the most emphatic performances in the tournament's history against the Netherlands at Headingley \u2014 a 95-run win built on a record-laden 209 for 5. Only net run rate, and barely that, separates them from Australia at the summit.

## Mandhana's Class, Shafali's Return

The engine of it all has been the opening pair. Smriti Mandhana, the vice-captain, has been imperious, her 74 from 47 balls against the Netherlands earning a second straight player-of-the-match award and confirming her as the batter the tournament's bowlers least want to face. Alongside her, Shafali Verma answered her critics in the most direct way possible. After a quiet start to the year and an early exit against Pakistan, she rediscovered her destructive best with a 38-ball 55, the two openers combining for a 115-run stand that the Dutch attack simply could not contain.

The depth behind them is just as striking. Richa Ghosh's 20 from eight balls and a two-ball cameo from Deepti Sharma carried India past 200, while the captain, Harmanpreet Kaur, has the luxury of a line-up in which contributions arrive from everywhere.

## A Breakout Bowler

If there is a new name the diaspora should learn, it is Shree Charani. The left-arm spinner returned figures of 4 for 19 against the Netherlands, choking the chase from the outset and turning a contest into a procession. Shafali then chipped in with 3 for 20 to underline her all-round value, the Dutch folding for 114. India's bowling, often the question mark hanging over their white-ball sides, has so far looked the most settled part of the team.

The one shadow over an otherwise dominant week was the sight of spinner Shreyanka Patil being stretchered off with an ankle injury mid-match \u2014 a worry for a squad that will want every option available as the tournament sharpens.

## What Comes Next

The road does not get easier. India face South Africa at Old Trafford on Sunday, June 21, before a meeting with Bangladesh on June 25 and a marquee clash with defending-era rivals Australia at Lord's on June 28. The top two from the group advance directly to the semi-finals, so two wins from two has bought India breathing room \u2014 but not complacency. South Africa, beaten finalists not long ago, remain a dangerous side, and the Australia fixture looms as a likely decider for top spot.

## Why the Diaspora Is Tuned In

For Indian families scattered across England's cricket-loving cities \u2014 Birmingham, Leeds, Manchester, London \u2014 this World Cup is a rare gift: a home-soil-adjacent tournament where they can buy a ticket and watch the Women in Blue in the flesh. For the millions more in the United States and Canada, the matches stream on JioHotstar at unsociable hours that few seem to mind. The reigning ODI champions arrived in England carrying the weight of a long wait and the momentum of a breakthrough. Halfway through the group stage, the cricket has matched the expectation.

There is a long way to go \u2014 semi-finals on July 2 and 3, a final at Lord's on July 5 \u2014 and Indian fans know better than most how cruelly this particular trophy has eluded them before. But for now, two from two, top of the table, and playing the most complete cricket of any side in the competition, the Women in Blue have given a global diaspora permission to dream."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image...")
img_caption = "India vice-captain Smriti Mandhana, whose form has anchored India's unbeaten start to the 2026 Women's T20 World Cup"
img_attribution = "Wikimedia Commons"
img_final = None

# 1) Subject athletes (Wikipedia portraits)
for person, cap in [
    ("Smriti Mandhana", "India vice-captain Smriti Mandhana, whose back-to-back player-of-the-match displays have anchored India's unbeaten start to the 2026 Women's T20 World Cup"),
    ("Shafali Verma", "India opener Shafali Verma, who returned to form with a 38-ball 55 against the Netherlands at the 2026 Women's T20 World Cup"),
    ("Harmanpreet Kaur", "India captain Harmanpreet Kaur, leading a side chasing its first T20 World Cup title"),
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
    for q in ["Smriti Mandhana", "India women cricket team", "Women's cricket India"]:
        cands = fetch_wikimedia_commons_images(q)
        for c in cands:
            low = c["title"].lower()
            print(f"   candidate: {c['title']} ({c['w']}x{c['h']})")
            if any(bad in low for bad in ["logo", ".svg", ".pdf", "map", "seating",
                                           "letters", "diagram", "chart", "flag", "icon"]):
                continue
            if not any(g in low for g in ["mandhana", "shafali", "harmanpreet", "india", "cricket"]):
                continue
            got = upload_to_supabase(c["url"], f"{art_slug}.jpg")
            if got:
                img_final = got
                img_caption = "India's women's cricket team at the 2026 T20 World Cup"
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
        {"name": "Sporting News \u2014 India Women's T20 World Cup 2026 schedule and how to watch", "url": "https://www.sportingnews.com/"},
        {"name": "Sporting News \u2014 Women's T20 World Cup 2026 points table: Live standings", "url": "https://www.sportingnews.com/"},
        {"name": "Sportstak \u2014 Mandhana, Shafali, Charani cast spell on Netherlands with 95-run triumph", "url": "https://www.thesportstak.com/"},
        {"name": "MyKhel \u2014 Women's T20 World Cup 2026 Points Table: Updated Standings and Results", "url": "https://www.mykhel.com/"},
    ]),
    "diaspora_angle": "India's women, reigning 50-over world champions, are chasing the one global title that has always eluded them \u2014 and a diaspora across England, the US and Canada is watching, in stadiums in Birmingham, Leeds and Manchester or on JioHotstar streams at all hours. After last year's home-soil ODI breakthrough, an unbeaten T20 World Cup start has given a generation of NRI fans permission to dream of a first T20 crown.",
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
