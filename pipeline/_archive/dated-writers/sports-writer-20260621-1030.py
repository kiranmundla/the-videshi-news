#!/usr/bin/env python3
"""
Sports Writer — June 21, 2026 (10:30 UTC slot)
Article: BCCI recalls Virat Kohli to India's ODI squad for the July tour of
England (3 ODIs: July 14 Edgbaston, July 16 Sophia Gardens/Cardiff, July 19
Lord's), subject to a fitness clearance. Kohli missed the Afghanistan ODIs
after a hamstring injury in the IPL 2026 final (RCB's second straight title,
his 75*). Jaiswal — who replaced him and made 110 in the third ODI — was left
out. Harshit Rana returns after a knee layoff. Gill captains.

ANGLE: Dedup-checked against last 3 days of sports articles. Covered already:
Headingley Day 1, Afghanistan 3-0 sweep (Jaiswal 110), Sooryavanshi T20I call-up,
post-Kohli Test era. This ODI SQUAD recall (Kohli's white-ball return announced
today) is FRESH and uncovered. Diaspora angle: Kohli — the single biggest draw
in world cricket — returns to play at Edgbaston, Cardiff and Lord's in front of
the UK's vast NRI community in the same English summer that India began their
Test era WITHOUT him.

Hero: Wikipedia portrait of Virat Kohli (most reliable photo), then Shubman Gill.
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
print("ARTICLE: Kohli recalled for England ODIs")
print("="*60)

art_slug = "virat-kohli-recalled-india-odi-squad-england-tour-july-2026-edgbaston-lords-fitness-test-jaiswal-dropped-harshit-rana-gill-captain-diaspora-nri"
art_headline = "Kohli Is Coming Back to England — This Time With a White Ball, and the Diaspora Is Counting Down"
art_subheadline = "India recalled Virat Kohli for next month's three ODIs in England, subject to a fitness test. Yashasvi Jaiswal, who replaced him and made a hundred against Afghanistan, was left out."

art_body = """India will take Virat Kohli back to England next month. The Board of Control for Cricket in India named him on Sunday in its squad for the three one-day internationals against England in July, subject to a fitness clearance, and with that single line the most anticipated comeback in world cricket moved a decisive step closer. For the millions of Indians scattered across Britain — and the many more who will fly in or stay up through the night elsewhere — it is the news the summer was waiting for.

Kohli has not played for India since the IPL final on May 31, when he made an unbeaten 75 to drag Royal Challengers Bengaluru to a second successive title against Gujarat Titans. He picked up a hamstring strain in that innings, an injury that ruled him out of this month's home ODI series against Afghanistan. India won that series 3-0 without him, and the man who took his place — Yashasvi Jaiswal — signed off with an unbeaten 110 in the final match in Chennai. It was not enough to keep his seat. Jaiswal was left out of the England squad altogether, a reminder of how unforgiving the queue for India's top order has become.

## The Squad

Shubman Gill, freshly installed as captain across formats, leads a side built around returning seniors. Rohit Sharma and Kohli anchor a batting group that also includes Shreyas Iyer, KL Rahul and Ishan Kishan, while Jasprit Bumrah, Prasidh Krishna, Arshdeep Singh and the uncapped Gurnoor Brar make up a varied seam attack. Axar Patel, Washington Sundar and Kuldeep Yadav provide the spin, with Nitish Kumar Reddy offering a seam-bowling all-rounder's balance.

The other notable name is Harshit Rana, recalled after a long layoff with a knee injury that cost him both the Twenty20 World Cup and the IPL. The selectors, clearly, are using this short white-ball trip to take stock of who is fit and firing with one eye on the 2027 World Cup.

## A Test, Then a Tour

Kohli's inclusion comes with a caveat that every fan will be tracking. He must pass a fitness assessment, expected at the BCCI's Centre of Excellence in Bengaluru in the coming days, before his place is rubber-stamped. Reports from his rehabilitation suggest the hamstring is healing faster than feared, and the timeline lines up neatly: the three ODIs are scheduled for July 14 at Edgbaston in Birmingham, July 16 at Sophia Gardens in Cardiff, and July 19 at Lord's in London.

There is a poignancy to the venues. This is the same English summer in which India began a new era of Test cricket without Kohli and Rohit Sharma, both of whom have stepped away from the red-ball game. At Headingley this week, a young top order has been writing the first chapter of that post-Kohli story. Now, a few weeks later and a few miles down the road, Kohli himself returns in coloured clothing — gone from one format, indispensable in another, all in the space of a single tour.

## Why the Diaspora Should Care

No cricketer on earth moves tickets and travel plans the way Kohli does, and nowhere is that truer than in Britain. England's grounds have long doubled as home fixtures for India, the stands a sea of blue jerseys and tricolours whenever the Men in Blue come to town. A Kohli appearance at Lord's — cricket's most storied address — is the kind of occasion British-Indian families plan their summers around, the sort of day where grandparents who left Punjab or Gujarat decades ago sit beside grandchildren born in Leicester or Southall and watch the same hero.

For the wider diaspora, the symbolism runs deeper still. Kohli is, for a generation of Indians abroad, the embodiment of a confident, unapologetic India on the global stage — the boy from Delhi who became the most famous athlete in the country and carried that aura into every foreign arena. To see him walk out at Edgbaston and Lord's one more time, in what may be among his final seasons of international cricket, is not just a sporting event. It is a homecoming of sorts, staged thousands of miles from home, for a community that has always claimed him as their own.

There is business to be done, too. England will be desperate to test India's white-ball depth ahead of a packed calendar, and the ODIs double as a dress rehearsal for the long road to 2027. But for the families already refreshing ticket pages from London to Birmingham to Cardiff, the calculation is simpler. Kohli is coming back to England. The countdown has begun."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image...")
img_caption = "Virat Kohli, recalled to India's ODI squad for the July tour of England"
img_attribution = "Wikimedia Commons"
img_final = None

# 1) Featured player Wikipedia portraits (the story's protagonists)
for name, cap in [
    ("Virat Kohli", "Virat Kohli, recalled to India's ODI squad for the July tour of England, subject to a fitness test"),
    ("Shubman Gill", "Shubman Gill, who captains India in the three ODIs against England in July"),
    ("Rohit Sharma", "Rohit Sharma, named alongside Virat Kohli in India's ODI squad for England"),
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
    for q in ["Virat Kohli batting", "India cricket team ODI",
              "Lord's Cricket Ground", "Edgbaston cricket"]:
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
                img_caption = "Lord's Cricket Ground in London, host of India's third ODI against England in July"
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
        {"name": "Reuters \u2014 India recall Kohli for England ODI tour, subject to fitness", "url": "https://www.reuters.com/sports/cricket/"},
        {"name": "Khel Now \u2014 Indian squad for England ODIs announcement", "url": "https://www.khelnow.com/"},
        {"name": "Cricbuzz \u2014 News Digest, June 2026", "url": "https://www.cricbuzz.com/"},
    ]),
    "diaspora_angle": "No cricketer moves tickets and travel plans across Britain like Virat Kohli, and his recall means the UK's vast NRI community can watch him at Edgbaston, Cardiff and Lord's in July \u2014 a homecoming of sorts staged thousands of miles from home, in the same English summer India began their Test era without him.",
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
