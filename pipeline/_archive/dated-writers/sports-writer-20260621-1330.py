#!/usr/bin/env python3
"""
Sports Writer — June 21, 2026 (13:30 UTC slot)
Article: India's women's hockey team beat hosts New Zealand 2-0 in the final of
the FIH Hockey Women's Nations Cup 2025-26 at North Harbour Hockey Stadium,
Auckland, on Sunday June 21. The win is India's SECOND Nations Cup title (after
the inaugural 2022 edition) and — crucially — earns PROMOTION to the 2026-27
FIH Women's Pro League, the sport's elite tier, from which India were relegated
after winning only 2 of 16 matches last season.

Goals: Navneet Kaur 4' (penalty corner), Sunelita Toppo 15' (deflecting
Deepika's effort). India went unbeaten all tournament: USA 3-2, Japan 2-1,
Uruguay 3-2, Chile 6-0 (SF). Deepika joint-top scorer (6 goals, with USA's
Ashley Sessa). Lalremsiami player of the match in the final. GK Savita made a
big save off a NZ penalty corner in Q4. Hockey India awarded Rs 3 lakh/player,
Rs 1.5 lakh/support staff.

ANGLE: Dedup-checked vs last 3 days. The SEMIFINAL (6-0 v Chile, "to the brink
of the Pro League") is already covered (2026-06-20 07:45). This is the FINAL —
the title clinched and promotion sealed — which is FRESH and uncovered. Diaspora
angle: a redemption story for NRI hockey fans after last year's relegation, and
a women's team finally back among the world's best, just as the Auckland-based
NZ diaspora hosted the showpiece.

Hero: Wikipedia portrait of a featured player (Navneet Kaur / Salima Tete /
Deepika), then Commons hockey imagery as fallback.
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
print("ARTICLE: India women win FIH Nations Cup, earn Pro League promotion")
print("="*60)

art_slug = "india-women-hockey-beat-new-zealand-2-0-fih-nations-cup-final-2026-auckland-pro-league-promotion-navneet-kaur-sunelita-toppo-deepika-savita-nri"
art_headline = "India's Women Won in Auckland, and With It a Ticket Back to the Top Table of World Hockey"
art_subheadline = "India beat hosts New Zealand 2-0 to lift the FIH Women's Nations Cup and seal promotion to the Pro League, a year after being relegated from the same elite tier."

art_body = """India's women's hockey team is going back to the big league. On Sunday in Auckland, the Women in Blue beat hosts New Zealand 2-0 in the final of the FIH Hockey Women's Nations Cup, capping an unbeaten tournament with the trophy and, more importantly, a place in next season's FIH Pro League. For a side that was bundled out of that same elite competition only a year ago, it was a night of redemption as much as celebration.

The goals came early and from the team's familiar weapon — the penalty corner. Navneet Kaur opened the scoring in the fourth minute with a powerful drag-flick, and Sunelita Toppo doubled the lead in the 15th, deflecting home an effort from Deepika, the tournament's joint-highest scorer. From there India did what they had done all week: defended with a compact, disciplined structure and refused the hosts a way back, even as New Zealand enjoyed long spells of possession in front of their own crowd at the North Harbour Hockey Stadium.

## A Clean Sweep Through the Tournament

This was the second time India have won the Nations Cup, after lifting the inaugural edition in 2022, and they did it without dropping a single match. The campaign opened with a comeback 3-2 win over the United States, followed by a 2-1 win over Japan and another fightback to beat Uruguay 3-2, which topped Pool A. Then came the semi-final, a thumping 6-0 dismantling of Chile that signalled India had shifted into a higher gear at exactly the right time.

Deepika finished as the tournament's joint-top scorer with six goals, level with the USA's Ashley Sessa, who was named player of the tournament. In the final itself, the experienced forward Lalremsiami was adjudged player of the match for a tireless performance. And when New Zealand finally manufactured a clear opening in the fourth quarter — a penalty corner with the game still alive at 2-0 — it was the veteran goalkeeper Savita who stood tall, producing the save that effectively ended the contest.

## Why This Win Matters

The result is bigger than a single trophy. The FIH Pro League is world hockey's premier annual competition, a home-and-away league featuring the strongest nations, and it is the surest route to regular high-quality matches between major tournaments. India were relegated from it last season after a brutal run in which they won just two of sixteen games and finished bottom of the nine-team table. Promotion back means India's women will once again test themselves week in, week out against the likes of the Netherlands, Argentina, Australia and Belgium — exposure that is hard to replicate any other way and that the team's leadership has long argued is essential to closing the gap at the top.

There is a neat symmetry to how it was won, too. New Zealand had actually qualified for the Pro League last season but declined the spot, choosing instead to play in this Nations Cup — and it was India, beating them on their own turf, who claimed the prize on offer. Hockey India moved quickly to mark the achievement, announcing a cash reward of Rs 3 lakh for each player and Rs 1.5 lakh for every member of the support staff.

## What the Diaspora Will Take From It

For Indians abroad who follow the national teams, this is the kind of comeback that lands harder than a routine win. Twelve months ago the women's program looked adrift, relegated and searching for answers. To respond with an unbeaten run and a final won in hostile conditions is the sort of arc that travels well in living rooms from London to Toronto to the Bay Area, where parents who grew up on stories of India's hockey golden age are now raising children who play the game on artificial turf in Surrey and Surrey-by-the-sea alike.

It also lands in a country — New Zealand — with its own substantial Indian community, many of them in Auckland, where the final was staged. For those families, watching India lift a trophy in their adopted city, against their adopted home, is the particular double-belonging that defines so much of diaspora sport.

The bigger picture is encouraging. A women's team that had slipped off the elite circuit has earned its way back, with a clutch of young scorers in Sunelita Toppo and Deepika, the steadying experience of Navneet Kaur, Lalremsiami and captain Salima Tete, and a goalkeeper in Savita who still rises to the biggest moments. Promotion guarantees them a season among the world's best. On the evidence of Auckland, they intend to make it count."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image...")
img_caption = "India's women's hockey team celebrates a goal"
img_attribution = "Wikimedia Commons"
img_final = None

# 1) Featured player Wikipedia portraits (the story's protagonists)
for name, cap in [
    ("Navneet Kaur (field hockey)", "Navneet Kaur, who scored India's opening goal in the FIH Women's Nations Cup final"),
    ("Salima Tete", "Salima Tete, who captained India to the FIH Women's Nations Cup title in Auckland"),
    ("Savita Punia", "Goalkeeper Savita, whose late save helped India seal the FIH Women's Nations Cup final"),
    ("Deepika (field hockey)", "Deepika, India's joint-highest scorer at the FIH Women's Nations Cup 2025-26"),
    ("Lalremsiami", "Lalremsiami, named player of the match in India's FIH Women's Nations Cup final win"),
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
    for q in ["India women's field hockey team", "India national field hockey team women",
              "field hockey India", "women field hockey match"]:
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
                img_caption = "India's women's field hockey team in action"
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
    "vertical": "hockey",
    "status": "review",
    "is_editorial": False,
    "image_url": img_final or "",
    "image_caption": img_caption,
    "image_attribution": img_attribution,
    "sources": json.dumps([
        {"name": "Saartaj \u2014 India beat New Zealand 2-0 to clinch second FIH Women's Nations Cup, earn Pro League promotion", "url": "https://saartaj.com/"},
        {"name": "Khel Now \u2014 India vs New Zealand final, FIH Hockey Women's Nations Cup 2025-26", "url": "https://khelnow.com/hockey/india-vs-new-zealand-live-womens-nations-cup-202606"},
        {"name": "Wikipedia \u2014 2025\u201326 Women's FIH Hockey Nations Cup", "url": "https://en.wikipedia.org/wiki/2025%E2%80%9326_Women%27s_FIH_Hockey_Nations_Cup"},
    ]),
    "diaspora_angle": "A year after India's women were relegated from world hockey's elite Pro League, an unbeaten Nations Cup run and a final won on New Zealand soil sends them back to the top tier \u2014 a redemption arc that resonates with NRI families from London to Toronto to Auckland, where the final was staged in front of a large local Indian community.",
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
