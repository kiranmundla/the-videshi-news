#!/usr/bin/env python3
"""
Sports Writer — June 22, 2026 — India women's hockey win FIH Nations Cup 2025-26

Article: India's women beat hosts New Zealand 2-0 in the Auckland final (Jun 21)
to win the FIH Hockey Women's Nations Cup 2025-26, their second title (after the
inaugural 2022 edition). Navneet Kaur (4') and Sunelita Toppo (15') scored in the
first quarter; India then produced a defensive masterclass (Savita in goal) to
hold the lead. India went unbeaten: beat USA 3-2, Japan 2-1, Uruguay 3-2 in
Pool A, thrashed Chile 6-0 in the semifinal. Lalremsiami was Player of the Match
in the final; Deepika was joint top scorer of the tournament (6 goals, tied with
USA's Ashley Sessa). The win earns promotion to the top-tier FIH Pro League
2026-27. Hockey India announced Rs 3 lakh per player, Rs 1.5 lakh per support
staff.

DEDUP: We covered India REACHING the final (semifinal 6-0 v Chile, Jun 20). The
TITLE WIN + Pro League promotion is FRESH and uncovered. Other recent sports:
Batra Asian Games, ETPL, Glasgow CWG, women's T20 WC, post-Kohli ODIs, MLC,
FIFA WC recaps, Sarpreet Singh, US Open tennis.

ANGLE: A clean, celebratory diaspora story — India's women win silverware and a
promotion abroad, in a non-cricket Olympic sport the diaspora increasingly
follows. Pro League promotion means regular high-level fixtures NRIs can watch.

Hero: Wikipedia REST API portrait of Navneet Kaur (scored the opening goal).
Person/team article -> Wikipedia first.
"""

import os, sys, json, io
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


def fetch_wikipedia_person_image(person_name):
    encoded = person_name.replace(" ", "_")
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            thumb = data.get("thumbnail", {}).get("source")
            orig = data.get("originalimage", {}).get("source")
            img = thumb or orig
            if img:
                print(f"  \u2713 Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  \u26a0 Wikipedia error for '{person_name}': {e}")
    return None


def compress_image(img_bytes, max_width=1200, quality=82):
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
print("ARTICLE: India women win FIH Nations Cup + Pro League promotion")
print("="*60)

art_slug = "india-women-hockey-win-fih-nations-cup-2026-beat-new-zealand-final-auckland-pro-league-promotion-navneet-kaur-toppo-diaspora"
art_headline = "India's Women Won in Auckland — and Won Their Way Back to Hockey's Top Table"
art_subheadline = "Two first-quarter goals and a wall of defence beat hosts New Zealand 2-0 in the Nations Cup final. The bigger prize: promotion to the FIH Pro League, where the diaspora can finally watch them play the world's best, regularly."

art_body = """India's women's hockey team flew home from Auckland on Sunday with two pieces of silverware that matter in very different ways. The first is the trophy itself: the FIH Hockey Women's Nations Cup 2025-26, won with a controlled 2-0 victory over hosts New Zealand in the final. The second is less photogenic but arguably more valuable — promotion to the FIH Pro League, the sport's top annual competition, for the 2026-27 season. One is a medal. The other is a seat at the table.

The final, played in front of a partisan Auckland crowd, was effectively decided inside the opening quarter. Navneet Kaur opened the scoring in the fourth minute, thumping home a penalty corner with the kind of strike that settles nerves early. Eleven minutes later Sunelita Toppo doubled the lead, deflecting a sharp Deepika effort past the New Zealand goalkeeper for India's fifth penalty corner of a frantic first fifteen minutes. After that, the match became an exercise in game management — and India passed it.

## A Defensive Masterclass

New Zealand, ranked tenth in the world and roared on by their home support, dominated possession for long stretches. It did not matter. India's defence, marshalled by the veteran goalkeeper Savita, produced exactly the kind of disciplined, unflashy performance that wins finals. The hosts won penalty corners; Savita and her back line snuffed them out. They built pressure; India absorbed it and broke at speed. Lalremsiami, busy and tireless across the pitch, was named Player of the Match.

It capped a tournament in which India never lost. They came through a tricky Pool A with wins over the United States (3-2), Japan (2-1) and Uruguay (3-2), then dismantled Chile 6-0 in the semifinal before the clean, professional job in the final. Deepika finished as the tournament's joint-top scorer with six goals, sharing the honour with the USA's Ashley Sessa. This is India's second Nations Cup crown, after they won the inaugural edition in 2022.

## Why Promotion Is the Real Prize

The Nations Cup is, by design, a second-tier event — and a ladder. Winning it earns the champion promotion to the FIH Pro League, the elite home-and-away competition contested by the likes of the Netherlands, Argentina, Australia, Germany and England. For an Indian side rebuilding after a bruising couple of years, that promotion is the headline. The Pro League guarantees a regular diet of matches against the world's best, the only environment in which a team genuinely improves, and the kind of exposure that funding, sponsorship and selection depth tend to follow.

It also closes a loop. India had dropped out of the top tier, and the only route back was to go and win the division below it. They did exactly that, unbeaten, away from home. There is no asterisk on this promotion.

Hockey India moved quickly to mark the win, announcing a cash award of three lakh rupees for every player and 1.5 lakh for each member of the support staff — a "fitting reward," the federation said on X, "for a team that made the nation proud."

## What It Means for the Diaspora

For Indians abroad, this is the kind of result that travels quietly but lands deeply. Hockey is the sport of India's Olympic golden age, the game that filled the country's trophy cabinet before cricket swallowed the national imagination whole. Among the diaspora — particularly across Punjab-rooted communities in Canada, the UK and Australia, where field hockey remains a living, played sport rather than a nostalgic one — the women's team carries real emotional weight.

The Pro League promotion matters here in a concrete way too. It means fixtures against European and Australian sides, often played in time zones and cities more accessible to NRI audiences than a domestic Indian tournament, and frequently streamed to a global audience. A diaspora that has long had to seek out women's hockey will, next season, simply be able to watch India take on the best in the world as a matter of routine. For a team that has spent two years fighting to get back into that company, being watched is part of the reward.

## What's Next

The immediate focus shifts to the FIH Pro League 2026-27 calendar and the squad-building that comes with it: India will need depth to survive a long, demanding home-and-away season against opponents who do this every year. But that is a problem for a team on the way up. For now, India's women have a trophy, a promotion, and a result earned without losing a single match — the cleanest kind of verdict there is."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image (Wikipedia first — person article)...")
img_caption = "Navneet Kaur, who scored India's opening goal in the Nations Cup final"
img_attribution = "Wikimedia Commons"
img_final = None

wiki_img = fetch_wikipedia_person_image("Navneet Kaur (field hockey)")
if wiki_img:
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
        {"name": "Khel Now \u2014 Women's Nations Cup 2025-26: India beat New Zealand to clinch title; finish tournament unbeaten", "url": "https://www.khelnow.com/hockey"},
        {"name": "RevSportz \u2014 India Win FIH Hockey Women's Nations Cup Title, Beating Hosts New Zealand 2-0 in the Final", "url": "https://revsportz.in"},
        {"name": "The Bridge \u2014 FIH Nations Cup: Indian women crowned champions; earn promotion to Pro League", "url": "https://thebridge.in"},
        {"name": "Madhyamam \u2014 India beat New Zealand 2-0 to lift FIH Hockey Women's Nations Cup title", "url": "https://www.madhyamamonline.com"},
    ]),
    "diaspora_angle": "Field hockey carries deep emotional weight for the Indian diaspora, especially in Punjab-rooted communities in Canada, the UK and Australia where it remains a played sport. India's title and promotion to the FIH Pro League means regular, globally streamed fixtures against the world's best that NRI audiences can finally watch as a matter of routine.",
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
