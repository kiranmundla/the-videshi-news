#!/usr/bin/env python3
"""
Sports Writer — June 19, 2026 (10:30 UTC run)
Article: Nishan Velupillay — Melbourne-born forward of Anglo-Indian and Sri
Lankan Tamil heritage — is set to face hosts USA in Seattle on Friday in
Australia's second Group D match at the 2026 World Cup. Australia opened with
a 2-0 win over Turkey (Velupillay came on for goalscorer Nestory Irankunda).

ANGLE: A DISTINCT diaspora-at-the-World-Cup story. The Videshi has already
covered Sarpreet Singh (first Sikh / first Indian-origin starter) and Tahsin
Jamshid (Kerala-origin, Qatar). Velupillay is the third and as-yet-uncovered
strand: Anglo-Indian mother, Sri Lankan Tamil father, born and raised in
Melbourne, now a World Cup forward for the Socceroos — and on Friday he could
take the field against the United States in front of a huge South Asian
diaspora crowd in the Pacific Northwest. Debut goal vs China in 2024, three
goals in seven caps (all in WC qualifiers).

Hero: Nishan Velupillay has a Wikipedia/Commons portrait (training for
Melbourne Victory, 2023). Fall back to on-topic Commons, then skip.
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
print("ARTICLE: Nishan Velupillay — diaspora forward faces USA in Seattle")
print("="*60)

art_slug = "nishan-velupillay-australia-socceroos-world-cup-2026-usa-seattle-anglo-indian-sri-lankan-tamil-melbourne-diaspora-nri"
art_headline = "He Is the Son of an Anglo-Indian Mother and a Tamil Father. On Friday, He Could Play the World Cup Hosts in Seattle."
art_subheadline = "Melbourne-born Nishan Velupillay is the least-talked-about of the World Cup's players of Indian heritage \u2014 a Socceroos forward who came off the bench in Australia's opening win and now waits in the wings against the United States."

art_body = """SEATTLE \u2014 When Australia line up against the host United States at Seattle's stadium on Friday, much of the noise will be about the Socceroos' bid to reach the World Cup's knockout rounds after a confident opening win. Less remarked upon \u2014 but quietly significant for millions of South Asians scattered across America's West Coast \u2014 is the 25-year-old forward who could step off the bench wearing No. 17: Nishan Velupillay, a child of the Indian and Sri Lankan diaspora, born and raised in Melbourne.

Velupillay is the least-celebrated strand of a remarkable World Cup story. This is the first tournament to feature multiple players of Indian heritage at once \u2014 New Zealand's Sarpreet Singh, the first Sikh to play at a World Cup; Qatar's Kerala-born winger Tahsin Jamshid; and Velupillay, whose roots run through two of the subcontinent's great diaspora communities. His father, Sasinath, is of Sri Lankan Tamil descent with Malaysian roots; his mother, Gillian, is Anglo-Indian. For a sport India has never reached on the global stage, this World Cup has become a celebration of the talent its diaspora has produced elsewhere.

## A Melbourne Boy Who Worked His Way Up

There is nothing accidental about Velupillay's path. He grew up in Melbourne, attended Mazenod College in Mulgrave, and began his football journey in the youth ranks at Glen Eira FC before earning a place in the Melbourne Victory academy. He is now a senior fixture in the A-League side, and his rise has been built on the kind of family sacrifice that resonates deeply with immigrant households everywhere.

"A lot of days where they're driving you to training and they come back from long, hard days of work and they're willing to put your dream first \u2014 I'm forever grateful for that," Velupillay said ahead of the tournament. "If I can repay them with a World Cup appearance, I'm sure they'll be happy with that."

That repayment is already underway. Velupillay made his senior international debut against China in October 2024, coming on in the 83rd minute and scoring within seven minutes to seal a 3-1 win. He has since collected seven caps and scored three goals \u2014 every one of them in a World Cup qualifier, the matches that carried the most pressure.

## Into the Tournament

Australia, coached by the former Melbourne Victory boss Tony Popovic, opened their Group D campaign with a 2-0 win over Turkey in Vancouver, goals from Nestory Irankunda and Connor Metcalfe giving the Socceroos a perfect start. Velupillay was introduced in the second half, replacing the goalscorer Irankunda \u2014 a sign of the attacking depth Popovic can call on as the group tightens.

Friday's meeting with the United States in Seattle is the pivotal fixture. A result against the co-hosts would put Australia in a commanding position to advance from a group that also contains Paraguay, whom they face in Santa Clara on June 25. Whether Velupillay starts or waits on the bench, his presence in the squad is itself the achievement \u2014 one of seventeen Socceroos making their World Cup debut this summer.

## Why the Diaspora Is Watching

For Indian and Sri Lankan families across the United States \u2014 and especially in the tech-heavy, cricket-and-football-loving communities of the Pacific Northwest and the Bay Area \u2014 Velupillay is a familiar kind of figure: the second-generation kid whose parents emigrated, worked relentlessly, and watched their child chase a dream that the old country could not have offered him. India has never played at a men's World Cup. But through players like Velupillay, Singh and Jamshid, the diaspora finds itself represented on the biggest stage in sport, wearing other nations' colours while carrying subcontinental names.

It is a bittersweet pride \u2014 a reminder of what Indian football has not yet built at home, and of what its scattered children have managed to achieve abroad. On Friday in Seattle, with a World Cup host nation on the other side, one of those children may get his moment. And somewhere in Melbourne, a family that drove to all those training sessions will be watching, knowing the journey was worth it."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image...")
img_caption = "Nishan Velupillay training for Melbourne Victory; the Anglo-Indian, Sri Lankan-Tamil forward is in Australia's 2026 World Cup squad"
img_attribution = "Wikimedia Commons"
img_final = None

# 1) Nishan Velupillay (subject) then Sarpreet Singh (related diaspora figure)
for person, cap in [
    ("Nishan Velupillay", "Nishan Velupillay training for Melbourne Victory; the Anglo-Indian, Sri Lankan-Tamil forward is in Australia's 2026 World Cup squad"),
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
    for q in ["Nishan Velupillay", "Melbourne Victory footballer", "Socceroos Australia football"]:
        cands = fetch_wikimedia_commons_images(q)
        for c in cands:
            low = c["title"].lower()
            print(f"   candidate: {c['title']} ({c['w']}x{c['h']})")
            if any(bad in low for bad in ["logo", ".svg", ".pdf", "map", "seating",
                                           "letters", "diagram", "chart", "flag", "icon"]):
                continue
            if not any(g in low for g in ["velupillay", "socceroo", "melbourne victory", "australia"]):
                continue
            got = upload_to_supabase(c["url"], f"{art_slug}.jpg")
            if got:
                img_final = got
                img_caption = "Australia's Socceroos at the 2026 World Cup"
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
    "vertical": "football",
    "status": "review",
    "is_editorial": False,
    "image_url": img_final or "",
    "image_caption": img_caption,
    "image_attribution": img_attribution,
    "sources": json.dumps([
        {"name": "Sporting News \u2014 Who is Nishan Velupillay? Indian-origin player named in Australia's FIFA World Cup 2026 squad", "url": "https://www.sportingnews.com/"},
        {"name": "Melbourne Victory \u2014 Velupillay ready to turn dreams into reality at World Cup", "url": "https://www.melbournevictory.com.au/"},
        {"name": "Reuters \u2014 New Zealand's Singh proud to blaze a trail for Sikh community at World Cup", "url": "https://www.reuters.com/"},
        {"name": "USA Today \u2014 Australia starting XI projection: Who will start World Cup game vs. USMNT?", "url": "https://www.usatoday.com/"},
    ]),
    "diaspora_angle": "Velupillay is part of the first World Cup to feature multiple players of Indian heritage at once \u2014 and for the large South Asian communities of America's West Coast, watching a Melbourne-born son of an Anglo-Indian mother and Tamil father potentially face the host USA in Seattle is a bittersweet point of pride in a sport India has never reached.",
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
