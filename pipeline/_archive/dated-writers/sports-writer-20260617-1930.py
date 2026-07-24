#!/usr/bin/env python3
"""
Sports Writer — June 17, 2026 (19:30 UTC run)
Article: India's WOMEN'S hockey team is unbeaten through two pool games at the FIH
Hockey Women's Nations Cup 2026 in Auckland — beating USA 3-2 (from 2-0 down) and
Japan 2-1 — and has booked a semi-final spot with a game to spare. The tournament
winner earns promotion to the 2026-27 FIH Pro League. Distinct, fresh angle: a
deliberate counterpoint to today's earlier piece on the MEN's worst-ever Pro League
campaign. Diaspora angle: India's women chase a Pro League berth that would put them
on the same elite circuit, and the squad is anchored by tribal-belt athletes
(Salima Tete from Jharkhand, Lalremsiami from Mizoram) whose rise resonates widely.
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
print("ARTICLE: India women's hockey unbeaten, into Nations Cup SF")
print("="*60)

art_slug = "india-women-hockey-fih-nations-cup-2026-auckland-semifinal-pro-league-promotion-salima-tete-deepika-nri"
art_headline = "Same Week the Men Finished Last, India's Women Are Unbeaten in Auckland — and One Step From a Pro League Promotion"
art_subheadline = "India's women's hockey team beat the USA 3-2 from two goals down, then edged Japan 2-1 to reach the FIH Nations Cup semi-finals with a game to spare. Win the tournament in New Zealand and they are promoted to the 2026-27 FIH Pro League \u2014 the elite circuit the men's side just endured a winless season in."

art_body = """AUCKLAND \u2014 In the same fortnight that India's men's hockey team limped to the worst Pro League campaign in its history \u2014 nine games, zero wins, dead last \u2014 the women's side has quietly assembled the kind of run that changes a season. At the North Harbour National Hockey Centre, Salima Tete's team has won both its pool matches at the FIH Hockey Women's Nations Cup 2025-26, booked a semi-final berth with a game still to play, and put itself two victories away from the promotion that would land it on the same elite circuit the men just exited in disgrace.

The prize on offer in New Zealand is concrete. The winner of the Nations Cup earns promotion to the FIH Pro League for the 2026-27 season \u2014 a standing invitation to play the world's best home and away across an entire year, the exposure and ranking points that come with it, and a place at hockey's top table. India's women dropped out of the Pro League and have been fighting to climb back ever since. Auckland is their pathway.

## Two Goals Down, Then a Comeback

The campaign opened on Sunday in the most alarming way possible. The United States raced two goals clear inside seven minutes, Ashley Sessa with a field goal and Madeleine Zimmer from a penalty corner, and India looked rattled. What followed was the kind of response that defines tournament teams. Deepika, back in the side and playing like she had never left, converted penalty corners in the 17th and 24th minutes to level the match, and Navneet Kaur put India ahead for the first time in the 28th. The drag-flicker's brace earned her Player of the Match, and India held firm through a second half in which both sides earned six short corners apiece but neither defence broke. A 3-2 win, salvaged from 2-0 down, set the tone.

## A Captain's Goal Against Japan

Tuesday's meeting with Japan was tighter still, scoreless at the long break and finely poised until the third quarter cracked it open. India struck first in the 33rd minute through a well-drilled penalty corner variation: Navneet Kaur's effort was deflected to the captain by Nikki Pradhan, and Salima Tete slotted home. Japan equalised within two minutes through Hiramitsu Ai's penalty corner, but India found the decisive blow in the 49th, Sushila Chanu Pukhrambam threading a pass from the top of the circle for Lalremsiami to deflect into the net. The 2-1 win took India to the top of Pool A on six points and confirmed a semi-final place with a match to spare. It was a milestone evening for midfielder Jyoti, who marked her 100th senior international cap.

## A Squad Built in the Tribal Belt

What gives this side its texture is who is in it. Salima Tete grew up in a village in Jharkhand's Simdega district, the cradle of Indian women's hockey, and learned the game on uneven ground before captaining her country. Lalremsiami, the match-winner against Japan, is from Mizoram and pushed through personal tragedy \u2014 she famously played on at the 2019 Junior World Cup days after losing her father \u2014 to become one of the team's most reliable forwards. Chief coach Sjoerd Marijne, in his second spell with the side, has leaned on a core that blends that hardscrabble Simdega-and-northeast pipeline with the drag-flicking firepower of Deepika and the experience of Sushila Chanu. India will close the pool stage against Uruguay on Thursday before turning to the knockout rounds over the weekend.

## Why the Diaspora Should Watch

For Indians abroad, hockey occupies a particular emotional register \u2014 the sport of eight Olympic golds, of a heritage older than independence, now carried largely by women from districts most NRIs have never visited. A Pro League promotion would mean India's women appear regularly on broadcast schedules in Europe, Australia and beyond, the same calendars on which diaspora families already follow cricket and football. The men's winless Pro League season was a painful watch for a community that takes the game's history personally. In Auckland, the women are offering the opposite story: a team climbing, not sliding, and two wins away from earning back a seat that the country has been desperate to reclaim. The semi-final, not the disappointment in Europe, may yet be the hockey image India's diaspora carries out of this summer."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image...")
img_caption = "India captain Salima Tete, who scored against Japan as India reached the FIH Women's Nations Cup semi-finals in Auckland"
img_attribution = "Wikimedia Commons"
img_final = None

cand = fetch_wikipedia_person_image("Salima Tete")
if cand:
    img_final = upload_to_supabase(cand, f"{art_slug}.jpg")

if not img_final:
    cand2 = fetch_wikipedia_person_image("Lalremsiami")
    if cand2:
        img_caption = "India forward Lalremsiami, whose 49th-minute deflection sank Japan and sent India top of Pool A in Auckland"
        img_final = upload_to_supabase(cand2, f"{art_slug}.jpg")

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
        {"name": "IANS \u2014 India beat Japan 2-1 to enter FIH Hockey Women's Nations Cup SF", "url": "https://ianslive.in/"},
        {"name": "myKhel \u2014 India Women's Hockey Beat USA 3-2 In Nations Cup Opener", "url": "https://www.mykhel.com/hockey/"},
        {"name": "Khel Now \u2014 India book semi-final berth with victory over Japan in FIH Hockey Women's Nations Cup 2025-26", "url": "https://khelnow.com/"},
        {"name": "FIH \u2014 Hockey Women's Nations Cup New Zealand 2025-26", "url": "https://www.fih.hockey/"},
    ]),
    "diaspora_angle": "Hockey carries deep heritage for Indians abroad, and a Nations Cup win would promote India's women \u2014 led by athletes from Jharkhand's Simdega belt and the northeast \u2014 to the elite FIH Pro League, putting them on the same broadcast calendars the diaspora already follows for cricket and football.",
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
