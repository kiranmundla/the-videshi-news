#!/usr/bin/env python3
"""
Sports Writer — June 18, 2026 (20:30 UTC run)
Article: Esha Singh — at 21, the Hyderabad shooter broke the senior AND junior
25m pistol world records (43/50) to win gold at the ISSF World Cup in Munich,
beating the reigning Olympic champion and a former world champion on her home
range. India's first individual shooting medal of the 2026 ISSF season.

Distinct from recent dashboard sports coverage (cricket ODIs/WC, women's T20 WC,
India A tri-series, chess, junior tennis, golf, hockey, football, athletics,
WNBA basketball). SHOOTING is an untouched vertical — and this is a definitive,
record-breaking achievement with a strong diaspora-pride angle.

Hero image: Esha Singh has a Wikipedia page — fetch her portrait first; fall
back to Commons shooting-sport imagery only if no person photo exists.
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
print("ARTICLE: Esha Singh — 25m pistol world record, Munich")
print("="*60)

art_slug = "esha-singh-25m-pistol-world-record-munich-issf-world-cup-gold-2026-hyderabad-shooter-nri"
art_headline = "She Is 21, She Is From Hyderabad, and She Just Broke a World Record on the Germans' Home Range"
art_subheadline = "At the ISSF World Cup in Munich, Esha Singh shot 43 out of 50 to win the women's 25m pistol gold \u2014 a score that now stands as both the senior and junior world record. She beat the reigning Olympic champion and a former world champion to do it. India's quiet shooting empire just got a new face."

art_body = """MUNICH \u2014 The Olympic shooting range here is one of the most demanding rooms in the sport. It is where Germany's pistol shooters are raised, where home crowds press in close, and where the margins between a medal and a forgotten fifth place are measured in single shots. On a Wednesday in late May, a 21-year-old from Hyderabad walked onto that range, fired ten series of five shots, and walked off with a world record.

Esha Singh won the women's 25m pistol gold at the International Shooting Sport Federation (ISSF) World Cup in Munich with a final score of 43 out of 50 \u2014 a number that now stands as both the senior and the junior world record in the event. It is the kind of result that does not need context to land, but the context makes it better: she did it in front of a German home crowd, beating their own former world champion, with the reigning Olympic gold medallist also in the field and unable to keep up.

## A Final She Refused to Lose

Singh shot perfect fives in half of the ten series \u2014 the competitive equivalent of running clean through the hardest stretch of a race and never breaking stride. Germany's Doreen Vennekamp, a European champion and a regular on the world's podiums, finished second with 38 hits, a full five shots back. Bulgaria's Miroslava Mincheva took bronze with 31. South Korea's Yang Jiin, the reigning Olympic champion who had actually topped qualification, faded to fifth when the final's elimination format turned ruthless.

"Munich meant a lot to me," Singh said afterward. "Everyone knows the kind of competition that goes on here, especially in pistol. Even getting into the top eight is very tight. I really wanted to win this, as this was my third time here."

She was honest about the nerves. "I wasn't calm at all. At one time, when trying to hear the command, I could almost feel my left hand shaking. I had a lot of nerves, but in our sport you can't escape that. You have to face it and embrace it \u2014 and that is what experience is all about."

## The Long Apprenticeship

Singh is not a sudden arrival. She is, in fact, one of those athletes the Indian shooting system has been building toward for the better part of a decade. As a 13-year-old in 2018, she famously upstaged Manu Bhaker \u2014 then the brightest teenager in Indian shooting \u2014 to win a triple crown at the national championships. Her father sold off parts of the family's resources to fund the ranges, the ammunition, and the travel that the sport quietly demands of those without institutional backing. By her early twenties she was already a three-time world championship medallist, a double Asian Games gold medallist, and an Olympian.

The Munich gold was her fourth individual World Cup medal, and her path to the final was its own grind: a 293 in the precision round on Tuesday, a 294 in rapid fire on Wednesday morning, for a qualifying total of 587 in a 98-strong field. Bhaker, the double Olympic medallist, finished 12th in qualification and missed the final cut. So did former Commonwealth champion Rahi Sarnobat in 14th. On this day, in this event, Esha Singh was simply the best shooter India had \u2014 and then the best in the world.

## India's Quiet Empire

For the Indian diaspora in the United States, Britain, and Canada, shooting rarely makes the highlight reels that cricket and, increasingly, chess and athletics command. But it has quietly become one of India's most reliable medal factories \u2014 a discipline where Indian women, in particular, now routinely beat the established European and East Asian powers on their own ranges. Singh's gold was India's first individual shooting medal of the 2026 ISSF World Cup season across rifle, pistol and shotgun, and it carries a tangible reward beyond the headline: a direct qualification berth for the season-ending ISSF World Cup Final in Rome later this year.

There is a particular kind of pride in watching a young woman from Hyderabad outshoot the Olympic champion in Munich and rewrite the record books while doing it. It is not the loud, stadium-filling pride of an IPL night. It is quieter, more precise \u2014 the pride of a sport built on stillness, breath control, and the refusal to flinch. At 21, with a world record now next to her name, Esha Singh has a long runway ahead. The diaspora would do well to learn it now."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image...")
img_caption = "Indian shooter Esha Singh, who broke the 25m pistol world record to win gold at the ISSF World Cup in Munich"
img_attribution = "Wikimedia Commons"
img_final = None

# 1) Try Esha Singh's own Wikipedia portrait
wiki_img = fetch_wikipedia_person_image("Esha Singh (sport shooter)")
if not wiki_img:
    wiki_img = fetch_wikipedia_person_image("Esha Singh")
if wiki_img:
    got = upload_to_supabase(wiki_img, f"{art_slug}.jpg")
    if got:
        img_final = got
        img_caption = "Indian pistol shooter Esha Singh, who set senior and junior 25m pistol world records (43/50) to win gold at the 2026 ISSF World Cup in Munich"

# 2) Fallback: on-topic Commons shooting-sport imagery
if not img_final:
    commons_queries = [
        "Esha Singh shooter",
        "ISSF World Cup pistol",
        "25m pistol shooting",
        "Olympic shooting pistol India",
    ]
    for q in commons_queries:
        cands = fetch_wikimedia_commons_images(q)
        for c in cands:
            low = c["title"].lower()
            print(f"   candidate: {c['title']} ({c['w']}x{c['h']})")
            if any(bad in low for bad in ["logo", ".svg", ".pdf", "map", "seating",
                                           "letters", "diagram", "chart", "target."]):
                continue
            if not any(g in low for g in ["shoot", "pistol", "singh", "issf", "rifle", "olympic"]):
                continue
            got = upload_to_supabase(c["url"], f"{art_slug}.jpg")
            if got:
                img_final = got
                if "singh" in low:
                    img_caption = "Indian pistol shooter Esha Singh, the new 25m pistol world record holder"
                else:
                    img_caption = "25m pistol shooting at an ISSF competition \u2014 the event in which Esha Singh set a new world record in Munich"
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
    "vertical": "diaspora-sport",
    "status": "review",
    "is_editorial": False,
    "image_url": img_final or "",
    "image_caption": img_caption,
    "image_attribution": img_attribution,
    "sources": json.dumps([
        {"name": "ISSF \u2014 Esha Singh breaks World Records to win 25m Pistol Women gold", "url": "https://www.issf-sports.org/news.ashx"},
        {"name": "The Bridge \u2014 Esha Singh wins Munich World Cup gold with record-breaking performance", "url": "https://thebridge.in/"},
        {"name": "Nagaland Post / IANS \u2014 Esha strikes gold with world record at Munich WC", "url": "https://www.nagalandpost.com/"},
        {"name": "The Indian Express \u2014 At 21, Esha Singh breaks a world record and beats the Olympic champion", "url": "https://indianexpress.com/"},
        {"name": "Wikipedia \u2014 Esha Singh", "url": "https://en.wikipedia.org/wiki/Esha_Singh"},
    ]),
    "diaspora_angle": "Shooting rarely makes the diaspora highlight reels that cricket and chess command, yet it has quietly become one of India's most reliable medal factories \u2014 a discipline where Indian women routinely beat established European and East Asian powers on their home ranges. Esha Singh, 21, from Hyderabad, outshot the reigning Olympic champion and a former world champion in Munich to set senior and junior world records, a quieter, more precise kind of pride for NRIs to follow.",
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
