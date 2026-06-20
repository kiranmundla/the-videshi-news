#!/usr/bin/env python3
"""
Sports Writer — June 20, 2026 (04:30 UTC slot)
Article: India have handed a maiden T20I call-up to 15-year-old Vaibhav
Sooryavanshi for the white-ball leg of the UK tour (two T20Is in Ireland from
June 26, then five against England). Shreyas Iyer named T20I captain, replacing
World Cup-winning skipper Suryakumar Yadav; Tilak Varma his deputy. BCCI is
sending the teenager's parents on tour to ease his transition into a senior
dressing room.

ANGLE: A 15-year-old being picked for India's senior side is a once-in-a-
generation story — the youngest path into international cricket, the IPL record
breaker, and a deliberate, caretaking BCCI. Diaspora angle: British-Indian fans
in Belfast/England get to witness the debut of the most-hyped teenager in world
cricket in person. Recent sports coverage was the men's Test preview (Gill),
women's T20 WC, Neeraj, hockey, MLC — nothing on the white-ball squad/
Sooryavanshi. Fresh.

Hero: Wikipedia portrait of Vaibhav Sooryavanshi (upload.wikimedia.org),
then Commons.
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
print("ARTICLE: Sooryavanshi, 15, handed maiden India T20I call-up")
print("="*60)

art_slug = "vaibhav-sooryavanshi-15-maiden-india-t20i-call-up-ireland-england-tour-2026-shreyas-iyer-captain-suryakumar-dropped-parents-tour-nri"
art_headline = "He Is 15, He Broke the IPL's Records, and Now India Are Sending His Parents With Him to Watch His Debut"
art_subheadline = "Vaibhav Sooryavanshi's maiden call-up for the white-ball tour of Ireland and England makes him one of the youngest cricketers India has ever picked \u2014 and the BCCI is taking the unusual step of flying his parents along to ease a schoolboy into an adult dressing room."

art_body = """When India name a squad, the headline usually belongs to the captain. This time it belongs to a boy young enough to still be in school. Vaibhav Sooryavanshi, 15 years old, has been handed his maiden India T20I call-up for the upcoming white-ball tour of the United Kingdom \u2014 two Twenty20 internationals against Ireland in Belfast from June 26, followed by a five-match series against England.

It is the kind of selection that has no real precedent in the modern game. Sooryavanshi is not a wildcard pick or a developmental gesture. He arrives in the senior squad as the reigning sensation of Indian cricket, and the selectors have made room for him while leaving out one of the format's biggest names.

## From Under-19 Final to the IPL Record Books

The numbers explain the hurry. Sooryavanshi first announced himself with a staggering 175 off 80 balls in the ICC Under-19 World Cup final, a left-hander's assault that suggested the usual age-group caution simply did not apply to him. He carried it into the Indian Premier League, where in 2025 he became the fastest Indian to a century in IPL history while still 14.

His 2026 IPL season removed any lingering doubt. Sooryavanshi piled up 776 runs at an average of 44.69 and a strike rate of 237.30, won the Orange Cap as the tournament's leading run-scorer, and was named its Most Valuable Player. Those are not the figures of a prospect being eased in; they are the best in the competition, produced by a teenager facing the world's most expensive bowling attacks.

"He has done something very special at such a young age," former South Africa captain Graeme Smith said of him recently, calling the left-hander one of the most exciting young T20 talents in the world. He was picked alongside fellow IPL breakout Prince Yadav, who took 16 wickets in his first full season, with both earning maiden T20 call-ups.

## A New Captain, and a Big Name Left Out

The squad marks a changing of the guard at the top, too. Shreyas Iyer has been named India's new T20I captain, replacing Suryakumar Yadav, who led India to the T20 World Cup title earlier this year but misses out on this tour. Tilak Varma, who is also captaining the India A side that reached the Dambulla tri-series final, has been named Iyer's deputy.

Around them sits a blend of the familiar and the rebuilt. T20I regulars Abhishek Sharma, Sanju Samson, Ishan Kishan, Shivam Dube and Arshdeep Singh remain, and Harshit Rana returns from an injury layoff. Prasidh Krishna comes in for Mohammed Siraj as the selectors manage workloads, while Hardik Pandya and Jasprit Bumrah are not part of the white-ball plans for this leg. With the next T20 World Cup in 2028 and cricket's return to the Olympics that same year in Los Angeles, India are openly building a core for the cycle ahead \u2014 and Sooryavanshi is being positioned at the centre of it.

## The Parents on Tour

What sets this call-up apart is not just the age but the care being taken around it. The BCCI has decided to send Sooryavanshi's parents with him on the UK tour, an unusual move for a senior international assignment.

"We are doing this because we believe it will ease a lot of issues as far as Vaibhav is concerned," board secretary Devajit Saikia said, framing the decision around the simple reality that a 15-year-old is being asked to live and travel inside an adult professional environment. Saikia drew a comparison to how a young Sachin Tendulkar leaned on the calming influence of senior players on his 1989 debut tour of Pakistan \u2014 and noted that the board sees Sooryavanshi as a potential asset to Indian cricket for the next two to three decades.

The protective instinct is not abstract. Sooryavanshi drew criticism for an on-field altercation during an India A clash against Sri Lanka A, a flashpoint that underlined how much scrutiny now follows a teenager who has barely begun. Tilak Varma, his India A captain, will be in the senior squad to help guide him through the transition.

## Why the Diaspora Will Be Watching

For British-Indian fans, the timing could hardly be better. The most-hyped teenager in world cricket will make his international bow on their doorstep \u2014 first in Belfast, then across grounds in England where the diaspora turns up in numbers for any India fixture. Parents who grew up on Tendulkar and Kohli now get to take their own children to watch the next name being written, in person rather than on a screen at an awkward hour.

There is a neat symmetry to it. The squad that tours England for the Tests is built around the post-Rohit, post-Kohli generation under Shubman Gill. The white-ball squad reaches even further forward, to a player born well into the smartphone era. India's selectors are not just picking teams for this summer; they are auditioning the faces the diaspora will follow for the next twenty years. The first of them is 15, and his mother and father will be in the stands."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image...")
img_caption = "Vaibhav Sooryavanshi, the 15-year-old handed a maiden India T20I call-up"
img_attribution = "Wikimedia Commons"
img_final = None

# 1) Subject athlete (Wikipedia portrait)
for person, cap in [
    ("Vaibhav Sooryavanshi", "Vaibhav Sooryavanshi, the 15-year-old handed a maiden India T20I call-up"),
    ("Vaibhav Suryavanshi", "Vaibhav Sooryavanshi, the 15-year-old handed a maiden India T20I call-up"),
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
    for q in ["Vaibhav Suryavanshi", "Vaibhav Sooryavanshi cricket", "Rajasthan Royals cricket", "India cricket team T20"]:
        cands = fetch_wikimedia_commons_images(q)
        for c in cands:
            low = c["title"].lower()
            print(f"   candidate: {c['title']} ({c['w']}x{c['h']})")
            if any(bad in low for bad in ["logo", ".svg", ".pdf", "map", "seating",
                                           "letters", "diagram", "chart", "flag", "icon"]):
                continue
            if not any(g in low for g in ["suryavanshi", "sooryavanshi", "royals", "cricket", "india"]):
                continue
            got = upload_to_supabase(c["url"], f"{art_slug}.jpg")
            if got:
                img_final = got
                if "vanshi" in low:
                    img_caption = "Vaibhav Sooryavanshi, India's 15-year-old batting sensation"
                else:
                    img_caption = "India's white-ball squad ahead of the 2026 UK tour"
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
        {"name": "The Indian Eye \u2014 Iyer named India\u2019s T20I captain for England, Ireland tours; BCCI hands maiden call-up to Vaibhav Sooryavanshi", "url": "https://theindianeye.com/"},
        {"name": "KhelNow \u2014 What time will IND vs IRE T20I series start? Squad and schedule", "url": "https://khelnow.com/"},
        {"name": "SportsTak \u2014 BCCI to send Vaibhav Sooryavanshi\u2019s parents on UK tour for T20I debut", "url": "https://www.thesportstak.com/"},
        {"name": "CricketAddictor \u2014 Graeme Smith crowns Vaibhav Sooryavanshi a T20 talent to watch", "url": "https://cricketaddictor.com/"},
    ]),
    "diaspora_angle": "The most-hyped teenager in world cricket will make his India debut on the diaspora's doorstep \u2014 in Belfast and across England \u2014 letting British-Indian families watch the sport's next superstar in person rather than on a screen half a world away.",
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
