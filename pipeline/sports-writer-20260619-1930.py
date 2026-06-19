#!/usr/bin/env python3
"""
Sports Writer — June 19, 2026 (re-run of missed 19:30 UTC slot)
Article: Shreyanka Patil ruled out of the Women's T20 World Cup with an ankle
injury; uncapped 24-year-old legspinner Prema Rawat (Uttarakhand / RCB / India A)
named as her replacement and handed a dream maiden India call-up.

ANGLE: Recent sports articles covered India Women's unbeaten run and the
Netherlands rout. None covered the Patil injury or Rawat's call-up. This is a
fresh, human story: one player's World Cup ends in the Powerplay, another's
begins from an India A tour bus in England. Diaspora hook: India's women's
cricket is the most-followed unifying story for NRIs after the 2025 50-over
title, and Rawat is the kind of unheralded-talent-makes-good arc the diaspora
rallies behind.

Hero: try Wikipedia for Shreyanka Patil and Prema Rawat, then Commons for
India women's cricket imagery, then skip.
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
print("ARTICLE: Shreyanka Patil out, Prema Rawat's dream call-up")
print("="*60)

art_slug = "shreyanka-patil-ankle-injury-ruled-out-womens-t20-world-cup-2026-prema-rawat-uncapped-legspinner-replacement-uttarakhand-rcb-india-nri"
art_headline = "An Ankle Twisted in the Powerplay Ended One World Cup. It Began Another for an Uncapped Spinner Who Was Already in England."
art_subheadline = "Shreyanka Patil is out of the Women's T20 World Cup after injuring her ankle against the Netherlands. Her replacement, 24-year-old legspinner Prema Rawat, has never played for India \u2014 and got the call while on an India A tour bus in England."

art_body = """LEEDS \u2014 It happened in the most ordinary moment of a one-sided match. With the last over of the Powerplay winding down at Headingley on June 17, India offspinner Shreyanka Patil bent to field a ball, twisted her right ankle, and was helped off the field. India went on to crush the Netherlands by 95 runs and stay unbeaten at the top of Group A. But for the 23-year-old from Bengaluru, the tournament was already over. Two days later, the BCCI confirmed what the limp had foretold: Patil has been ruled out of the 2026 Women's T20 World Cup.

In her place, the selectors have reached for a name almost no cricket follower outside the domestic circuit would recognise \u2014 and in doing so handed one of the great underdog stories of this World Cup to a 24-year-old legspinner named Prema Rawat.

## The Player India Loses

Patil's exit is no small thing. The off-spinning all-rounder had only recently fought her way back from a previous injury, and this was meant to be her stage. In the Women's Premier League she had been one of India's most reliable attacking options against left-handers \u2014 11 wickets at an average of 14 with a dot-ball percentage above 40 \u2014 and her electric fielding in the ring had become a signature. She had played a tidy three-over spell against Pakistan in India's opener, finishing with 0 for 17, before the ankle gave way against the Dutch. For a side built on spin, losing a death-overs specialist who troubles left-handers leaves a genuine gap.

## The Player India Gains

Prema Rawat was not even on the same continent's radar. The leg-break bowler from Uttarakhand was in England with the India A squad when the call came from the national selectors \u2014 a phone ringing on a tour she had expected to be the summit of her year, not the start of something far bigger.

Her case had been building quietly. Rawat was part of the Royal Challengers Bengaluru side that lifted the WPL 2026 title, and she has been a fixture of the India A pipeline. At the Women's Asia Cup Rising Stars earlier this year she took eight wickets in five matches at an average under ten as India A won the tournament; on India A's tour of Australia last year she was the joint-leading wicket-taker with seven wickets in three T20s. The Event Technical Committee of the World Cup approved her as Patil's replacement, and the Women's Selection Committee named her in the squad for the rest of the campaign. If she takes the field, she will earn her maiden international cap on the biggest stage the women's game has.

> "Following Prema's inclusion in the squad, Niki Prasad has been added to the India A T20 squad and Minnu Mani has been added to the India A One-Day squad." \u2014 BCCI Women

## A Reshuffle Down the Chain

The promotion set off a small chain reaction. With Rawat moving up, the selectors added Niki Prasad to the India A T20 squad and Minnu Mani to the India A one-day squad for the upcoming series against England A \u2014 a reminder of how deep the Indian women's bench has grown since the side's 50-over World Cup triumph in 2025. India's updated World Cup squad now reads: Harmanpreet Kaur (c), Smriti Mandhana (vc), Shafali Verma, Jemimah Rodrigues, Bharti Fulmali, Deepti Sharma, Richa Ghosh (wk), Sree Charani, Yastika Bhatia (wk), Nandni Sharma, Arundhati Reddy, Renuka Thakur, Kranti Gaud, Radha Yadav and Prema Rawat.

## What's Next

India sit two-from-two at the top of Group A, having dispatched Pakistan and the Netherlands, and face their toughest test yet against South Africa at Old Trafford on June 21. Whether the team risks blooding an uncapped spinner mid-tournament or holds Rawat in reserve, her story is already written into this World Cup. One Indian cricketer's tournament ended on the Headingley turf in the seventh over; another's began with a phone call she will remember for the rest of her life.

For the diaspora that turned the 2025 title into a watershed for the women's game \u2014 packing pubs in London, gurdwara halls in Surrey, and living rooms across New Jersey \u2014 the churn at the bottom of the squad is its own kind of proof. India's women no longer depend on a single name. When one falls, another is already in the country, boots packed, waiting for the call."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image...")
img_caption = "India's women's cricket team, unbeaten at the 2026 T20 World Cup"
img_attribution = "Wikimedia Commons"
img_final = None

# 1) Subject athletes (Wikipedia portraits) — try Patil then Rawat
for person, cap in [
    ("Shreyanka Patil", "India offspinner Shreyanka Patil, ruled out of the 2026 Women's T20 World Cup with an ankle injury"),
    ("Prema Rawat (cricketer)", "Uncapped legspinner Prema Rawat, named as Shreyanka Patil's replacement in India's World Cup squad"),
    ("Prema Rawat", "Uncapped legspinner Prema Rawat, named as Shreyanka Patil's replacement in India's World Cup squad"),
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
    for q in ["Shreyanka Patil", "India women cricket team 2025",
              "India women national cricket team", "Harmanpreet Kaur"]:
        cands = fetch_wikimedia_commons_images(q)
        for c in cands:
            low = c["title"].lower()
            print(f"   candidate: {c['title']} ({c['w']}x{c['h']})")
            if any(bad in low for bad in ["logo", ".svg", ".pdf", "map", "seating",
                                           "letters", "diagram", "chart", "flag", "icon"]):
                continue
            if not any(g in low for g in ["patil", "harmanpreet", "mandhana",
                                          "india", "cricket"]):
                continue
            got = upload_to_supabase(c["url"], f"{art_slug}.jpg")
            if got:
                img_final = got
                if "patil" in low:
                    img_caption = "India offspinner Shreyanka Patil, ruled out of the 2026 Women's T20 World Cup"
                else:
                    img_caption = "India's women's cricket team, unbeaten at the 2026 T20 World Cup"
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
        {"name": "Cricbuzz \u2014 Shreyanka Patil ruled out of Women's T20 World Cup with ankle injury, Prema Rawat named replacement", "url": "https://www.cricbuzz.com/"},
        {"name": "ICC \u2014 India name replacement as spinner ruled out of T20WC 2026", "url": "https://www.icc-cricket.com/"},
        {"name": "Devdiscourse \u2014 ICC Women's T20 World Cup: Prema Rawat to replace injured Shreyanka Patil", "url": "https://www.devdiscourse.com/"},
        {"name": "Cricket Addictor \u2014 Shreyanka Patil ruled out of Women's T20 World Cup 2026 as BCCI names replacement", "url": "https://cricketaddictor.com/"},
        {"name": "BCCI Women (@BCCIWomen) \u2014 official announcement, June 19, 2026", "url": "https://twitter.com/BCCIWomen"},
    ]),
    "diaspora_angle": "India's women's cricket team became a unifying obsession for NRIs after the 2025 50-over World Cup title, and the squad's depth \u2014 an uncapped spinner stepping in for an injured star without missing a beat \u2014 is exactly the kind of story the diaspora rallies behind as the team chases its first T20 World Cup.",
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
