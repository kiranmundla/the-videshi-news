#!/usr/bin/env python3
"""
Sports Writer — June 21, 2026 (19:30 UTC slot)

Article: India will send only 125-130 athletes-and-staff to the scaled-down
Glasgow 2026 Commonwealth Games (July 23 - Aug 2), IOA CEO Raghuram Iyer said.
That's a sharp drop from the 208-strong squad that finished 4th with 61 medals
(22 gold) in Birmingham 2022 — and it's no accident. Glasgow's 10-sport program
(athletics, swimming, track cycling, gymnastics, netball, weightlifting, boxing,
judo, bowls, 3x3 basketball) has axed the very disciplines India mines for
medals: wrestling, badminton, table tennis, squash and hockey are all gone.
India competes in 8 able-bodied + 4 para sports. Full contingent named after
the June 23 deadline. India also hosts CWG 2030 in Ahmedabad and will receive
the Commonwealth Sport flag at Glasgow's closing ceremony.

DEDUP: Checked last 3 days of sports. Today already covered: women's hockey
Nations Cup (final + SF), women's T20 WC v SA, post-Kohli ODIs, MLC, FIFA WC,
Neeraj Doha, Kohli England recall. The CWG-contingent / dropped-sports story is
FRESH and uncovered.

Hero: Wikipedia portrait of a retained-sport India medal star (Mirabai Chanu /
Nikhat Zareen / Lovlina), then Commons CWG/Glasgow imagery as fallback.
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
print("ARTICLE: India's leaner Glasgow CWG squad, medal sports dropped")
print("="*60)

art_slug = "india-125-130-athletes-glasgow-2026-commonwealth-games-wrestling-badminton-hockey-dropped-ioa-raghuram-iyer-ahmedabad-2030-diaspora"
art_headline = "A Smaller India Heads to Glasgow — and the Sports It Wins Most Aren't on the Bill"
art_subheadline = "India will send just 125-130 athletes and staff to a stripped-down Commonwealth Games that has dropped wrestling, badminton, hockey and table tennis — its richest medal seams."

art_body = """India is going to the Commonwealth Games with a fraction of the firepower it usually brings. The Indian Olympic Association will send a contingent of 125 to 130 athletes and support staff to Glasgow 2026, IOA chief executive Raghuram Iyer said on Friday — barely half the 208-strong squad that travelled to Birmingham four years ago. The Games run from July 23 to August 2, and India will compete in eight able-bodied and four para sports.

The shrinkage is not a sign of declining ambition. It is a direct consequence of how radically the host has pared back the event. Glasgow stepped in to rescue the 2026 Games after the Australian state of Victoria pulled out over spiralling costs, and the price of keeping the Commonwealth Games alive was a leaner, cheaper model: a 10-sport programme staged in just four venues, with athletes housed in hotels rather than a purpose-built village.

## The Sports India Wins Most Are Gone

For India, the cuts land in the worst possible places. The Glasgow programme keeps athletics and swimming as compulsory sports, alongside track cycling, gymnastics, netball, weightlifting, boxing, judo, lawn bowls and 3x3 basketball. What is missing is a roll-call of India's most reliable medal factories: wrestling, badminton, table tennis, squash and field hockey have all been dropped, along with rugby sevens, triathlon and diving.

Those absences explain the smaller squad more than any belt-tightening in New Delhi. At Birmingham 2022, India finished fourth on the medal table with 61 medals, including 22 gold — and a huge share of that haul came in exactly the disciplines now cut. Wrestlers alone delivered a dozen medals; badminton, table tennis and the Indian women's and men's hockey teams added more. Strip those events out and India's medal map for Glasgow narrows sharply, leaning heavily on weightlifting, boxing and a clutch of track-and-field hopefuls.

## What India Can Still Target

There is still plenty to chase. Weightlifting has long been a Commonwealth stronghold for India, and boxing offers a deep bench of world-level contenders across the men's and women's divisions. The athletics squad carries genuine medal weight too, and the integrated para events — Glasgow folds para competition into six sports, including athletics, swimming and weightlifting — give India's strong parasport programme a real platform.

The IOA expects to confirm the full contingent after June 23, the deadline for submitting entries to organisers, with national federations handling selection. Iyer was at pains to stress the IOA would not interfere in those calls, comments that come against the backdrop of selection rows elsewhere, including the omission of table tennis star Manika Batra from India's Asian Games squad.

## A Bridge to a Bigger Indian Moment

Glasgow is also a staging post for something far larger on India's horizon. India will host the 2030 Commonwealth Games in Ahmedabad — the centenary edition of the Games — and will receive the Commonwealth Sport flag during the closing ceremony in Glasgow. Iyer said Ahmedabad is preparing a special presentation showcasing India's culture and identity, a first public flourish of a home Games that will dwarf anything India has staged before. The same city is central to India's bid to host the 2036 Olympics, talks the IOA says are continuing with the International Olympic Committee.

There is a near-term marker too: India is simultaneously building toward the Asian Games in Aichi-Nagoya, Japan, where it expects to send a contingent of more than 700 athletes — the scale that reveals just how much the Glasgow format has compressed the Commonwealth event.

## Why the Diaspora Should Care

For Indians settled across Britain, Canada and Australia, the Commonwealth Games have always been the most accessible global stage to see India compete — same language, friendly time zones, and host cities with large desi populations close enough to fill the stands. Glasgow, with its substantial South Asian community, would have been a natural pilgrimage. A smaller squad in fewer sports means fewer of those flag-waving moments, and the conspicuous absence of badminton and wrestling — the events that turned Saina Nehwal, the Phogat sisters and a generation of shuttlers and grapplers into household names abroad — will sting for fans who grew up on them.

But the longer arc points homeward. With Ahmedabad 2030 on the way and an Olympic bid alive, the diaspora's relationship with Indian sport is shifting from watching India travel to the world toward the prospect of the world travelling to India. Glasgow, leaner and stranger than the Games that came before it, is where that next chapter quietly begins."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image...")
img_caption = "An Indian athlete competing at the Commonwealth Games"
img_attribution = "Wikimedia Commons"
img_final = None

# 1) Featured retained-sport India medal stars (Wikipedia portraits)
for name, cap in [
    ("Mirabai Chanu", "Weightlifter Mirabai Chanu, one of India's medal hopes in a Glasgow programme that retains weightlifting"),
    ("Nikhat Zareen", "Boxer Nikhat Zareen, a medal contender in one of the sports India retains at Glasgow 2026"),
    ("Lovlina Borgohain", "Boxer Lovlina Borgohain, among India's medal hopes for the Glasgow Commonwealth Games"),
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
    for q in ["Commonwealth Games India athletes", "Commonwealth Games weightlifting",
              "Glasgow 2014 Commonwealth Games", "India Commonwealth Games team"]:
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
                img_caption = "Indian athletes in action at the Commonwealth Games"
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
    "vertical": "olympic-sports",
    "status": "review",
    "is_editorial": False,
    "image_url": img_final or "",
    "image_caption": img_caption,
    "image_attribution": img_attribution,
    "sources": json.dumps([
        {"name": "Madhyamam \u2014 India to send 125-130 athletes to Glasgow Commonwealth Games, says IOA CEO", "url": "https://madhyamamonline.com/sports/india-to-send-125-130-athletes-to-glasgow-commonwealth-games-says-ioa-ceo-1530078"},
        {"name": "Devdiscourse \u2014 Indian Olympic Association hosts 2nd Athletes' Forum 2026", "url": "https://www.devdiscourse.com/news"},
        {"name": "Sportsnet/AP \u2014 No rugby, field hockey, badminton, triathlon or cricket at leaner 2026 Commonwealth Games", "url": "https://www.sportsnet.ca/"},
    ]),
    "diaspora_angle": "The Commonwealth Games have long been the most accessible stage for Indians in Britain, Canada and Australia to watch their country compete, and Glasgow's stripped-down programme \u2014 minus India's signature sports of badminton, wrestling and hockey \u2014 means fewer of those moments, even as Ahmedabad's 2030 Games promise to bring the event home.",
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
