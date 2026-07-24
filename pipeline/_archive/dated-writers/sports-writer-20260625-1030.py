#!/usr/bin/env python3
"""
Sports Writer — June 25, 2026 (10:30 UTC slot / videshi-writer-sports)

Article: India's women win the FIH Hockey Women's Nations Cup 2025-26 in
Auckland, beating hosts New Zealand 2-0 in the final to clinch the title AND
secure promotion back to the FIH Pro League for 2026-27 — a redemption after
relegation and a heartbreak loss to England at a World Cup qualifier.

DEDUP CHECK (vs recent ~3 days sports feed, category=sports):
- Feed HAS: Edgbaston Test preview; Headingley Test result; India ODI/T20
  squads; Suryakumar sacking; Sooryavanshi; Nitish Reddy injury; Pant-Kuldeep
  IPL trade; women's T20 WC qualification; Wimbledon; Neeraj Chopra Doha;
  Indian Athletics Awards; fencing; Anushka Yadav hammer; Animesh Kujur;
  Jagmeet Singh basketball; women's 4x100m relay; para-badminton; MI New York.
- Feed does NOT have: the WOMEN'S FIELD HOCKEY Nations Cup TITLE win and Pro
  League promotion. Completely distinct sport and story. CLEAR TO WRITE.

Key facts (Hockey India / FIH via LatestLY, IANS, Devdiscourse, Yardbarker;
Wikipedia 2025-26 Women's FIH Hockey Nations Cup):
- Final: India 2-0 New Zealand, North Harbour National Hockey Centre, Auckland,
  Sunday June 21, 2026. Goals: Navneet Kaur 4' (penalty corner), Sunelita
  Toppo 15' (penalty corner) — both in the first quarter.
- India unbeaten all tournament: beat USA, Japan, Uruguay (pool); Chile (SF);
  New Zealand (final). Captain: Salima Tete. Chief Coach: Sjoerd Marijne.
- This is India's SECOND Nations Cup title; it earns DIRECT PROMOTION to the
  2026-27 Women's FIH Pro League — a return after relegation.
- Lalremsiami = Player of the Match in the final. Deepika = joint top scorer of
  the tournament with 6 goals (shared with USA's Ashley Sessa). Final standings:
  1 India, 2 New Zealand, 3 USA, 4 Chile.
- Hockey India cash reward: Rs 3 lakh per player, Rs 1.5 lakh per support staff.
- Marijne: "Of course, we are delighted to win our first tournament and final
  together. It was crucial for us to learn how to win finals, especially after
  our recent heartbreak against England at the World Cup qualifier... We relied
  on a very strong and well-organised defence."
- Salima Tete: clear mindset to bring the trophy home.

Hero: Wikipedia/Commons photo of captain Salima Tete. Permanent Wikimedia URL,
downloaded + re-uploaded to Supabase.
"""

import os, io, json, subprocess
from datetime import datetime, timezone

import requests
from PIL import Image

# -- ENV --
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


def compress_image(img_bytes, max_width=1200, quality=85):
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


print("\n" + "=" * 60)
print("ARTICLE: India women win Hockey Nations Cup, earn Pro League promotion")
print("=" * 60)

art_slug = "india-women-hockey-nations-cup-2026-champions-beat-new-zealand-2-0-auckland-salima-tete-navneet-kaur-toppo-pro-league-promotion-diaspora-nri"
art_headline = "India's Women Won a Trophy and a Promotion in One Night in Auckland"
art_subheadline = "Two first-quarter penalty corners beat hosts New Zealand 2-0 in the FIH Hockey Women's Nations Cup final, handing Salima Tete's unbeaten side the title and a direct return to the elite Pro League barely a year after relegation."

art_body = """For an Indian women's hockey team still carrying the sting of a World Cup qualifier heartbreak and a drop out of the sport's top tier, the night of June 21 in Auckland answered both wounds at once. India beat hosts New Zealand 2-0 in the final of the FIH Hockey Women's Nations Cup 2025-26, lifting the trophy and, with it, earning direct promotion back to the elite FIH Pro League for the 2026-27 season.

The match was effectively decided inside the opening 15 minutes. Navneet Kaur converted a penalty corner in the fourth minute, and Sunelita Toppo struck from another set piece in the 15th. After that, the story was defensive control: India held a two-goal cushion across the final three quarters at the North Harbour National Hockey Centre, smothering a New Zealand side roared on by its home crowd.

## An unbeaten run, start to finish

What makes the title more than a one-off is how India got there. Salima Tete's side did not lose a single match in the tournament. They came through a pool containing the United States, Japan and Uruguay, dispatched Chile in the semi-final, and then closed it out against the hosts. The final standings read India first, New Zealand second, the USA third and Chile fourth — and for India, that top placing carried the prize that mattered most beyond the medal: a place back among the world's best.

"We had a clear mindset to bring the trophy home," captain Tete said after the win — a line that captured a campaign defined less by flair than by composure under pressure.

## A coach's lesson in winning finals

For chief coach Sjoerd Marijne, the value was as much psychological as it was tactical. "Of course, we are delighted to win our first tournament and final together," he said. "It was crucial for us to learn how to win finals, especially after our recent heartbreak against England at the World Cup qualifier. The team improved with every match. We relied on a very strong and well-organised defence."

That emphasis on defence showed in the scoreline. India did not chase an open, end-to-end final; they took their early chances and then protected them, exactly the kind of game-management that had eluded them in tighter matches before.

## The names behind the title

Individual honours were spread across the squad. Striker Lalremsiami was named Player of the Match in the final for a relentless performance up front. Drag-flicker Deepika finished as the tournament's joint top scorer with six goals, sharing that distinction with the USA's Ashley Sessa. Navneet Kaur and Toppo, the two who scored when it counted, gave India the platform their defence then defended.

Hockey India moved quickly to reward the achievement, announcing a cash prize of Rs 3 lakh for each player and Rs 1.5 lakh for every member of the support staff — recognition of a result that resets the team's trajectory.

## Why the promotion is the real headline

The Pro League is where the world's top hockey nations meet home and away across a long season, and the regular, high-quality competition it offers is exactly what a developing side needs. India's relegation had threatened to slow that growth. Winning the Nations Cup reverses it immediately: instead of rebuilding from the second tier, Tete's team will once again test itself against the likes of the Netherlands, Argentina and Germany on a routine basis.

## Why the diaspora should care

For Indian sports fans abroad, women's hockey has quietly become one of the country's most consistent international stories, and this title adds a second Nations Cup to the trophy cabinet. The promotion guarantees that diaspora supporters in Europe and beyond will have far more chances to watch India play live over the coming season, as Pro League fixtures travel to host cities around the world. After a year of setbacks, an unbeaten run in Auckland has put India's women back where they want to be — and back within reach of fans who follow them from afar."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing hero image (Wikipedia/Commons \u2014 Salima Tete)...")
img_caption = "India captain Salima Tete, who led the team to an unbeaten FIH Hockey Women's Nations Cup title in Auckland."
img_attribution = "Wikimedia Commons"

wiki_img = "https://upload.wikimedia.org/wikipedia/commons/8/8b/Women%27s_Hockey5s_Medallist_Ceremony_YOG18_14-10-2018_%28038%29_%28cropped%29.jpg"
img_final = upload_to_supabase(wiki_img, f"{art_slug}.jpg")

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
        {"name": "LatestLY \u2014 India Clinches FIH Nations Cup 2025-26 Title, Returns to Women's Hockey Pro League", "url": "https://www.latestly.com/"},
        {"name": "IANS \u2014 'We had a clear mindset to bring the trophy home,' says captain Salima on India's title win at Nations Cup", "url": "https://www.ianslive.in/"},
        {"name": "Devdiscourse \u2014 Captain Salima Tete on India's title win at FIH Hockey Women's Nations Cup", "url": "https://www.devdiscourse.com/"},
        {"name": "Wikipedia \u2014 2025-26 Women's FIH Hockey Nations Cup", "url": "https://en.wikipedia.org/wiki/2025%E2%80%9326_Women%27s_FIH_Hockey_Nations_Cup"},
    ]),
    "diaspora_angle": "India's women returning to the FIH Pro League means diaspora fans across Europe and beyond will get far more chances to watch the national team play live next season, as Pro League fixtures tour host cities worldwide.",
    "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}

art_id = insert_article(art_data)

print("\n" + "=" * 60)
print("DONE")
print("=" * 60)
mark = "\u2713" if art_id else "\u2717"
print(f"Article: {mark} {art_slug}")
print(f"Word count: ~{len(art_body.split())} words")
print(f"Image: {img_final or '(none)'}")
print("Set to status='review'")
