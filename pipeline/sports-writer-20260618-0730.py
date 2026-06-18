#!/usr/bin/env python3
"""
Sports Writer — June 18, 2026 (07:30 UTC run)
Article: India's chess golden generation — anchored on R Praggnanandhaa's
Norway Chess 2026 title (beating Magnus Carlsen twice and world champion
Gukesh Dommaraju), plus the deep Indian presence at the Freestyle Chess
Grand Slam in Las Vegas. The story is an analysis/explainer of how India
suddenly produced a cluster of 2700+ super-GMs in their teens and twenties,
and what it means for the diaspora.
Distinct from recent sports articles (cricket ODIs, women's T20 WC, India A,
hockey, golf, tennis juniors, football) — chess has NOT been covered recently.
Diaspora angle: the global chess boom runs through Indian-origin families,
and India is now exporting the world's most exciting young talent.
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


def fetch_wikimedia_commons_images(search_query, limit=6):
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
print("ARTICLE: India's chess golden generation (Pragg, Gukesh, Arjun)")
print("="*60)

art_slug = "india-chess-golden-generation-praggnanandhaa-norway-chess-2026-gukesh-arjun-erigaisi-carlsen-diaspora-nri"
art_headline = "He Beat Carlsen Twice and the World Champion Once. In Oslo, a 20-Year-Old From Chennai Showed Why India Now Runs Chess."
art_subheadline = "R Praggnanandhaa's Norway Chess title is the latest sign of a generational shift: a country that had one world champion in 2013 now has the reigning world champion, the tournament's winner, and a clutch of 2700-rated players barely out of their teens. For a global game increasingly played in Indian living rooms, the future has an accent."

art_body = """OSLO \u2014 For five days in early June, the strongest closed tournament in chess was decided by a 20-year-old from a modest Chennai household who learned the game because his parents wanted to pull him away from the television. By the end of Norway Chess 2026, R Praggnanandhaa had finished first in a six-player field that included world number one Magnus Carlsen and the reigning world champion, his compatriot Gukesh Dommaraju. Along the way he beat Carlsen twice and defeated Gukesh \u2014 a sweep of the two highest-profile names in the sport, in their own marquee event.

It was, on its own, a remarkable result. Set against the last eighteen months, it looked like something larger: confirmation that the center of gravity in elite chess has moved, and that it now sits squarely in India.

## A Generation, Not a Prodigy

For decades, Indian chess meant one name. Viswanathan Anand became the country's first grandmaster in 1988 and held a version of the world title for much of the 2000s, an almost solitary giant. When he faded, the worry was that India had produced a genius rather than a system.

That worry has been emphatically answered. India now boasts the reigning world champion in Gukesh, who became the youngest undisputed world champion in history in late 2024 at age 18. It has Praggnanandhaa, a Candidates contender and now a super-tournament winner. It has Arjun Erigaisi, who has flirted with the 2800 rating barrier that only a handful of humans have ever crossed. Behind them are Nihal Sarin, Vidit Gujrathi, and a deep bench of teenagers already rated higher than most national champions elsewhere.

What makes the cohort extraordinary is not any single result but its density. At the Norway Chess final standings, Praggnanandhaa topped the table with 18 points; Gukesh, having an off event, finished last with 8. The point is that both were there at all \u2014 two Indians among the six best players invited to one of the calendar's most exclusive tournaments.

## The Las Vegas Strip, the Sicilian Defence

If Oslo showed India's peak, Las Vegas showed its breadth. At the Freestyle Chess Grand Slam, the variant event co-founded by Carlsen that randomizes the starting position to neutralize memorized opening theory, Arjun Erigaisi and Praggnanandhaa both reached the final stages, finishing sixth and seventh in a field stacked with the world's elite. Praggnanandhaa closed his campaign by beating Wesley So in the final round. The American grandmaster Levon Aronian took the title and its $200,000 first prize, but the story for Indian fans was the simple, unremarkable presence of two of their own in the money rounds of a tournament on the Strip.

That normalization \u2014 Indian names no longer as upset-makers but as expected contenders \u2014 is the real shift.

## Why It Happened

The boom has roots that are part infrastructure, part timing. Anand's success seeded a generation of coaches and academies. The pandemic, which moved chess online and onto streaming platforms, arrived precisely as a wave of Indian juniors hit their teens, giving them unlimited access to elite competition and engine-driven preparation from their bedrooms. Online platforms made a 13-year-old in Chennai or Pune a few clicks away from a grandmaster in Oslo.

And chess, unlike cricket, asks for almost nothing in the way of facilities. A board, an internet connection, and a willing parent will do. In a country where academic discipline is prized and a mentally demanding pursuit carries real social prestige, the game found extraordinarily fertile ground.

## The Diaspora Connection

For the Indian diaspora, this ascendancy lands close to home \u2014 often literally at the kitchen table. Chess participation has surged among Indian-American and Indian-British families, where the game's blend of intellectual rigor and low cost fits neatly into immigrant aspirations. Scholastic chess clubs across American suburbs are increasingly populated by children of Indian origin; weekend tournaments in New Jersey, the Bay Area, and the London commuter belt read, on the entry lists, a little like a Chennai phone book.

When Gukesh won the world title, and again when Praggnanandhaa stood atop the field in Oslo, the celebrations were not confined to India. They rippled through diaspora WhatsApp groups and community halls from Edison to Houston, because these players are not distant national heroes so much as proof of concept for a particular kind of parental bet \u2014 that a child raised between two cultures could reach the very top of a global, cerebral pursuit.

The pipeline shows no sign of slowing. With Gukesh holding the crown, Praggnanandhaa and Arjun pushing toward the top of the live ratings, and a generation of juniors behind them, India is no longer producing champions by accident. It is producing them by design \u2014 and the rest of the chess world is still adjusting to the new map."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image...")
img_caption = "R Praggnanandhaa, who won Norway Chess 2026 ahead of Magnus Carlsen and world champion Gukesh Dommaraju"
img_attribution = "Wikimedia Commons"
img_final = None

# Person article: try Wikipedia first for Praggnanandhaa
for name in ["Praggnanandhaa Rameshbabu", "R Praggnanandhaa", "Praggnanandhaa"]:
    cand = fetch_wikipedia_person_image(name)
    if cand:
        img_final = upload_to_supabase(cand, f"{art_slug}.jpg")
        if img_final:
            break

# Fallback: Gukesh (world champion, central to story)
if not img_final:
    cand2 = fetch_wikipedia_person_image("Gukesh Dommaraju")
    if cand2:
        img_caption = "Gukesh Dommaraju, the reigning world chess champion and part of India's golden generation"
        img_final = upload_to_supabase(cand2, f"{art_slug}.jpg")

# Fallback: Wikimedia Commons chess imagery of the players
if not img_final:
    for q in ["Praggnanandhaa chess", "Gukesh Dommaraju chess", "Norway Chess 2026"]:
        cands = fetch_wikimedia_commons_images(q)
        for c in cands:
            print(f"   candidate: {c['title']} ({c['w']}x{c['h']})")
            got = upload_to_supabase(c["url"], f"{art_slug}.jpg")
            if got:
                img_final = got
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
    "vertical": "chess",
    "status": "review",
    "is_editorial": False,
    "image_url": img_final or "",
    "image_caption": img_caption,
    "image_attribution": img_attribution,
    "sources": json.dumps([
        {"name": "Wikipedia \u2014 Norway Chess 2026 (final standings)", "url": "https://en.wikipedia.org/wiki/Norway_Chess_2026"},
        {"name": "The Indian Eye \u2014 D Gukesh upsets Magnus Carlsen in Norway Chess Tournament", "url": "https://theindianeye.com/"},
        {"name": "The Indian Eye \u2014 Indian Grandmasters finish 6th and 7th in Freestyle Chess Grand Slam (Las Vegas)", "url": "https://theindianeye.com/2025/07/21/indian-grandmasters-finish-6th-and-7th-in-freestyle-chess-grand-slam/"},
        {"name": "CNHI News \u2014 Chess Corner: A class act (Praggnanandhaa wins Norway Chess 2026)", "url": "https://www.cnhinews.com/"},
    ]),
    "diaspora_angle": "India's chess surge runs straight through diaspora living rooms \u2014 the same low-cost, high-prestige game that Indian-American and Indian-British families have embraced en masse is now producing the world's most exciting young grandmasters, making players like Praggnanandhaa and Gukesh proof of concept for a particular immigrant bet.",
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
