#!/usr/bin/env python3
"""
Sports Writer — June 17, 2026 (07:30 UTC run)
Article: India men's hockey is enduring its worst-ever FIH Pro League campaign —
zero wins in nine matches, dead last among the non-relegated sides (8th of 9, 4
points, GD -17), with the World Cup and Asian Games months away. Analytical
big-picture piece, distinct from the June 15 match report on the Netherlands loss.
Diaspora angle: hockey is India's national sport; NRIs follow the Pro League on
Star Sports / JioHotstar, and the slump lands just as the team should be peaking
for the two tournaments that define the cycle.
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
print("ARTICLE: India hockey — worst-ever Pro League campaign")
print("="*60)

art_slug = "india-men-hockey-worst-fih-pro-league-campaign-2025-26-zero-wins-eighth-place-fulton-harmanpreet-world-cup-asian-games-nri"
art_headline = "Nine Games, Zero Wins: India's Hockey Team Is Having Its Worst Pro League Ever \u2014 at the Worst Possible Time"
art_subheadline = "India sit eighth of nine in the FIH Pro League with four points and a minus-17 goal difference, having not won a single match in regulation. With the World Cup and Asian Games months away, Craig Fulton's side faces Germany in Rotterdam needing to prove the slump is a blip, not a warning."

art_body = """For a country that has won eight Olympic gold medals in field hockey \u2014 more than any other nation \u2014 the numbers coming out of the 2025\u201326 FIH Pro League make for uncomfortable reading. After nine matches, India have not won once. Not in regulation, not against anyone. Four points, all of them scraped from shoot-outs. A goal difference of minus-17. Eighth place in a nine-team table, ahead of only a Pakistan side that has lost all ten of its games and already been relegated.

This is, by any reasonable measure, India's worst Pro League campaign since they joined the competition in 2020\u201321. And it is arriving at precisely the moment the team can least afford it, with the Men's FIH Hockey World Cup and the Asian Games both looming later this year \u2014 the latter carrying a direct ticket to the 2028 Los Angeles Olympics for whoever wins it.

## How Bad Has It Been

The bare standings tell the story. Belgium, the world champions, sit top with nine wins from ten and have already booked their place at LA 2028. Australia, England, the Netherlands and Argentina are bunched in the chasing pack. Even a transitional German side has eleven points. India have four, and their only points have come via the bonus system: one shoot-out win and two shoot-out losses, with six defeats in regulation time.

The campaign began at home in Rourkela against Belgium and Argentina, moved to Hobart for matches against Australia and Spain, and has now reached the European leg in Rotterdam. Along the way, India have conceded 28 goals and scored just 11. The most recent loss, a 2\u20133 defeat to the Netherlands on June 14 in which Manpreet Singh equalled a 412-cap milestone, followed the now-familiar pattern: competitive for long stretches, undone by a late goal and a thin cushion of their own.

## A Selection Experiment That Hasn't Paid Off

Some of this was, to be fair, by design. Head coach Craig Fulton was candid from the outset that he viewed the Pro League as a laboratory rather than a trophy hunt. "Now's the time to rest some of the more senior guys. Play some of the younger guys in Rourkela," he said before the home leg, framing the season as a selection exercise ahead of the World Cup and Asian Games. Workloads were managed, debutants were capped, and rotation was prioritised over results.

But there is a difference between rotating a squad and losing your identity, and India have at times looked like the latter. The drag-flick battery built around captain Harmanpreet Singh \u2014 still one of the most lethal penalty-corner specialists in the world \u2014 has misfired. The defence that carried India to back-to-back Olympic bronze medals in Tokyo and Paris has leaked goals at a rate the team has not seen in years. "After a disappointing four matches in Rourkela \u2014 where the results didn't go our way \u2014 we've learned some good lessons," Fulton said after the home leg. The lessons have not yet shown up on the scoreboard.

## Why It Matters to the Diaspora

Hockey occupies a particular place in the Indian imagination. It is, by long tradition if not by current viewership, the national sport \u2014 the game of Dhyan Chand and the Helsinki and Melbourne golds, the sport whose decline and partial revival has been treated as a barometer of Indian sporting self-respect. For the diaspora, that emotional weight travels. NRIs across the United States, Britain, Canada and Australia follow the Pro League on Star Sports and JioHotstar, often watching at unfriendly hours, precisely because hockey carries a heritage that cricket, for all its dominance, does not displace.

That is why a winless run stings beyond the table. India's resurgence over the last Olympic cycle \u2014 two Olympic medals, a generation of fans who grew up watching the team lose now watching it win \u2014 had restored a sense that the old powerhouse was back. A nine-match drought, however it is contextualised, chips at that confidence just as the team should be peaking.

## The Road Ahead

There is still time, and the calendar is unforgiving in a useful way. India face Germany in Rotterdam, then the Netherlands again, before a London leg featuring Pakistan and England. Fulton has insisted the World Cup and Asian Games squads will be built around "a solid core," and the players who have absorbed these defeats in Europe are, by his own account, the ones most likely to feature when the medals are on the line.

The optimistic reading is that a hard, humbling Pro League is exactly the kind of preparation a team needs before a major tournament \u2014 better to find the flaws now than in a quarter-final. The pessimistic reading is that form is form, and that a side which cannot win a single match across nine attempts against the world's best has problems no amount of context can explain away. Against Germany, India will get another chance to tell the diaspora which reading is correct."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image...")
img_caption = "India captain Harmanpreet Singh, whose side is enduring a winless 2025\u201326 FIH Pro League campaign"
img_attribution = "Wikimedia Commons"
img_final = None

cand = fetch_wikipedia_person_image("Harmanpreet Singh (field hockey)")
if not cand:
    cand = fetch_wikipedia_person_image("Harmanpreet Singh")
if not cand:
    cand = fetch_wikipedia_person_image("India men's national field hockey team")
    img_caption = "The India men's national field hockey team, eighth in the 2025\u201326 FIH Pro League"

if cand:
    img_final = upload_to_supabase(cand, f"{art_slug}.jpg")

if not img_final:
    print("  \u26a0 No image uploaded \u2014 inserting without image")

art_data = {
    "headline": art_headline,
    "subheadline": art_subheadline,
    "body": art_body,
    "slug": art_slug,
    "category": "sports",
    "vertical": "hockey",
    "status": "review",
    "is_editorial": False,
    "image_url": img_final or "",
    "image_caption": img_caption,
    "image_attribution": img_attribution,
    "sources": json.dumps([
        {"name": "2025\u201326 Men's FIH Pro League \u2014 standings", "url": "https://en.wikipedia.org/wiki/2025%E2%80%9326_Men%27s_FIH_Pro_League"},
        {"name": "International Hockey Federation \u2014 official Pro League site", "url": "https://www.fih.hockey/events/fih-pro-league"},
        {"name": "Sporting News \u2014 India schedule at FIH Pro League: fixtures, live stream, TV channel", "url": "https://www.sportingnews.com/in/hockey/news/india-schedule-fih-pro-league-fixtures-live-stream-tv-channel/"},
        {"name": "FIH \u2014 Fulton and Harmanpreet look ahead to demanding FIH Hockey Pro League season", "url": "https://www.fih.hockey/news"},
    ]),
    "diaspora_angle": "Hockey is India's national sport by heritage, and NRIs across the US, UK, Canada and Australia follow the Pro League on Star Sports and JioHotstar. A winless campaign just as India should be peaking for the World Cup and Asian Games lands hard with a diaspora that treats the team's revival as a point of pride.",
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
