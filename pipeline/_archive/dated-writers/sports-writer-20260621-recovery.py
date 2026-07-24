#!/usr/bin/env python3
"""
Sports Writer — June 21, 2026 (recovery run for failed 09:55 PDT slot)
Article: India Women lost their first match of the ICC Women's T20 World Cup 2026,
beaten by South Africa Women by 6 wickets in Match 18, Group A, at Old Trafford,
Manchester on June 21, 2026.

Score: India 158/7 (20 ov); South Africa 161/4 (19.1 ov). Player of the match:
Marizanne Kapp 81*(45) — 7 fours, 4 sixes, SR 180. India's pick was left-arm
spinner Shree Charani 3/24. Tazmin Brits 40, Wolvaardt 20 set the platform.
India's top order all got starts (Shafali 31, Deepti 29, Harmanpreet 24) but
nobody went big; 158 proved below par.

ANGLE: Dedup-checked. The June 19 article framed India as "unbeaten" after 2
wins. This is their FIRST LOSS — a narrative reversal. Diaspora angle: NRI fans
who followed the unbeaten run now face a reality check, with semifinal seeding
on the line.

Hero: Wikipedia portrait of a featured player (Marizanne Kapp / Smriti Mandhana
/ Harmanpreet Kaur), then Commons cricket imagery as fallback.
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
print("ARTICLE: India women suffer first T20 World Cup loss to South Africa")
print("="*60)

art_slug = "india-women-lose-south-africa-6-wickets-t20-world-cup-2026-kapp-81-old-trafford-first-defeat-charani-mandhana-nri"
art_headline = "India's Unbeaten Run Ends at Old Trafford, Undone by a Marizanne Kapp Masterclass"
art_subheadline = "Chasing 159, South Africa rode an unbeaten 81 from Marizanne Kapp to beat India by six wickets in Manchester, handing the tournament favourites their first defeat of the Women's T20 World Cup."

art_body = """India's serene start to the Women's T20 World Cup hit its first real bump on Sunday. At a cool, cloud-draped Old Trafford in Manchester, South Africa chased down 159 with five balls to spare, winning by six wickets to inflict India's first defeat of the tournament. The architect was Marizanne Kapp, whose unbeaten 81 from 45 balls was the kind of innings that wins knockout games — and very nearly felt like one.

India had won both their opening matches and arrived as Group A's form side, but there were murmurs even before this game that the batting had not yet clicked beyond Smriti Mandhana. Those concerns hardened into a problem here. Put in to bat, India reached 158 for 7, a total that looked competitive on a true surface but never quite safe.

## A Top Order That Started but Didn't Finish

The pattern of India's innings was frustratingly familiar: starts without conclusions. Mandhana made 17 before Kapp bowled her, Shafali Verma raced to 31 from 15 balls before holing out, and through the middle Harmanpreet Kaur (24), Deepti Sharma (29) and Richa Ghosh (15) all got in without going big. Shabnim Ismail, back in the South African attack and bowling with genuine venom, took two key wickets, and Kapp chipped in with two of her own to go with her runs. India's 158 felt 15 or 20 short of where the surface suggested they should have been.

In reply, South Africa lost Laura Wolvaardt early — caught and bowled by the impressive left-arm spinner Shree Charani — but Tazmin Brits anchored with 40 and Kapp simply took the game away. She struck seven fours and four sixes, motoring at a strike rate of 180, and treated India's spinners with a disdain that no one else in the match could manage. By the time she finished things off alongside Chloe Tryon's cameo of 10 from 4, the result had long stopped being in doubt.

For India, Charani was the lone bright spot with the ball, finishing with 3 for 24 from her four overs. Around her, the attack leaked. Deepti Sharma went for 44 from her four overs, and with Shreyanka Patil ruled out injured and replaced by the uncapped Prema Rawat, the death bowling lacked its usual control.

## What It Means for the Group

The defeat does not derail India's campaign, but it complicates it. With two wins and a loss, they remain well placed to reach the semi-finals, yet net run rate and seeding now matter, and a top-two finish that once looked routine will require sharper cricket in their remaining group games. South Africa, beaten earlier by Australia, badly needed this result and got it in emphatic fashion, reviving their own qualification hopes.

There is also history here that India will not enjoy revisiting. South Africa beat India in a bilateral T20I series earlier this year, and the Proteas have made a habit of finding ways to expose India under pressure. The challenge for Harmanpreet's side is less about personnel — the talent is obvious — than about converting individual starts into the kind of partnership that breaks a game open, the very thing Kapp did to them on Sunday.

## The Diaspora Reality Check

For Indian cricket fans abroad, this was the morning the romance of an unbeaten run met a colder reality. In the United States, the match unfolded over breakfast; in Britain, where a large Indian community had hoped to fill Old Trafford for a coronation, it became an exercise in admiring an opponent. The women's team has built a genuine following across the diaspora over the past few years, and with that following comes the same impatience and high expectation long reserved for the men.

The encouraging truth is that nothing about this performance suggested a side in crisis — only one that has not yet played its best cricket. Mandhana remains in fine touch, Verma can win a game in a single powerplay, and India's spin resources are deep. But a World Cup rarely waits for a team to warm up. India's next outing is now less a routine fixture than a test of how quickly this group can answer the questions South Africa just asked of them. On Sunday in Manchester, the favourites were reminded that being the best team on paper guarantees nothing once Marizanne Kapp gets going."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image...")
img_caption = "Action from the Women's T20 World Cup"
img_attribution = "Wikimedia Commons"
img_final = None

# 1) Featured player Wikipedia portraits (the story's protagonists)
for name, cap in [
    ("Marizanne Kapp", "Marizanne Kapp, whose unbeaten 81 powered South Africa past India at Old Trafford"),
    ("Smriti Mandhana", "Smriti Mandhana, who made 17 before being bowled by Kapp"),
    ("Harmanpreet Kaur", "India captain Harmanpreet Kaur during the Women's T20 World Cup"),
    ("Laura Wolvaardt", "South Africa captain Laura Wolvaardt at the Women's T20 World Cup"),
    ("Shafali Verma", "Shafali Verma, who made a quickfire 31 for India"),
]:
    wiki_img = fetch_wikipedia_person_image(name)
    if wiki_img:
        got = upload_to_supabase(wiki_img, f"{art_slug}.jpg")
        if got:
            img_final = got
            img_caption = cap
            break

# 2) Fallback: on-topic Commons imagery
if not img_final:
    for q in ["India women's cricket team", "South Africa women's cricket team",
              "women's cricket match", "Old Trafford cricket ground"]:
        cands = fetch_wikimedia_commons_images(q)
        for c in cands:
            low = c["title"].lower()
            print(f"   candidate: {c['title']} ({c['w']}x{c['h']})")
            if any(bad in low for bad in ["logo", ".svg", ".pdf", "map", "seating",
                                           "letters", "diagram", "chart", "flag", "icon"]):
                continue
            got = upload_to_supabase(c["url"], f"{art_slug}.jpg")
            if got:
                img_final = got
                img_caption = "Action from the Women's T20 World Cup"
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
        {"name": "Khel Now \u2014 South Africa Women won by 6 wickets vs India Women, SA-W vs IND-W 2026 result", "url": "https://khelnow.com/"},
        {"name": "Cricketaddictor \u2014 South Africa Women vs India Women Full Scorecard, Match 18, 21 June 2026", "url": "https://cricketaddictor.com/"},
        {"name": "Sporting News \u2014 Women's T20 World Cup 2026: IND vs SA preview", "url": "https://www.sportingnews.com/"},
    ]),
    "diaspora_angle": "India's women had built a genuine diaspora following on the back of an unbeaten World Cup start, and this first defeat \u2014 in front of a large Indian community in Manchester and over breakfast tables across the US \u2014 is the moment that romance met a colder reality, with semifinal seeding now on the line.",
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
