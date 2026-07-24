#!/usr/bin/env python3
"""
Sports Writer — June 19, 2026 (01:30 UTC run)
Article: Neeraj Chopra returns at the Doha Diamond League (June 19) after a
nine-month injury layoff — his longest break since the 2021 Olympic gold.
In a candid pre-meet press conference he revealed he hid a lower-back injury
at the 2025 Tokyo Worlds (where he finished 8th, his worst senior result),
and he explained why he split with Czech legend Jan Zelezny in January 2026
to train under Indian coach Jaiveer "Jay" Chaudhary, his longtime mentor.

ANGLE: Not a comeback recap — the meet is hours away as this publishes. This
is the introspective "why I went back to an Indian coach + the injury I
ignored" narrative, plus a forward look to Doha, the Commonwealth Games and
Asian Games. The earlier "Doha comeback" piece was a straight preview; this
is built around his new confessions and the coaching-philosophy shift.

Hero image: Neeraj Chopra has a Wikipedia portrait. Try his page first.
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
print("ARTICLE: Neeraj Chopra returns in Doha \u2014 the injury he hid, the coach he left")
print("="*60)

art_slug = "neeraj-chopra-doha-diamond-league-return-injury-zelezny-split-indian-coach-jay-chaudhary-2026"
art_headline = "The Injury He Hid, the Coach He Left: Neeraj Chopra Returns to the Runway in Doha"
art_subheadline = "After nine months away \u2014 his longest absence since Olympic gold \u2014 India's greatest track-and-field star opens his 2026 season on Friday with a startling admission about Tokyo, and a quiet rebellion against the foreign-expert model: he has gone back to an Indian coach."

art_body = """DOHA \u2014 When Neeraj Chopra walks onto the runway at Khalifa International Stadium on Friday, it will have been exactly nine months and one day since he last competed \u2014 the longest he has been away from a javelin runway since the August evening in 2021 when he became Olympic champion and changed the arithmetic of Indian sport forever. The break was not by choice. And in a press conference on the eve of his return, the 28-year-old from Haryana finally explained why it lasted so long, with a candour that is rare even for him.

The short version: he should never have thrown in Tokyo at all.

## The Confession

At the 2025 World Championships last September, Chopra finished eighth with a best of 84.03 metres \u2014 the worst result of his senior career, and the end of a staggering streak of 26 consecutive top-two finishes and 33 straight podiums. At the time, it looked like a champion having an off day. It was, he now admits, a champion competing on a body that was breaking down.

"I had some injury before the Tokyo World Championships. We worked a lot and still decided to compete there, but I don't think that was a good decision because I already knew I had a problem," Chopra told reporters in Doha. "But it was the last competition of 2025, so I decided to compete."

The problem was his lower back, picked up in a gruelling training session before the championship. Pushing through it set off a familiar and cruel chain reaction. "In an athlete's life, if there is one injury, you try to protect that area and then something else starts hurting," he said. "I had issues with my ankle, then somewhere in my shoulder. So I sat down with my team and physio, and we worked on every aspect." The recovery swallowed the entire early season; the Doha Diamond League, originally scheduled for May 8 and postponed because of the conflict in West Asia, became a fortunate landing spot for his comeback.

## The Coach He Left

The more revealing story, though, is who is \u2014 and isn't \u2014 in his corner.

In January, Chopra parted ways with Jan Zelezny, the Czech world-record holder and the greatest javelin thrower in history, after a single season together. It was a partnership that had produced the defining technical milestone of Chopra's career: under Zelezny, at this very meet last year, he finally breached the 90-metre barrier with a national-record 90.23m. By any conventional logic, you do not walk away from the man who unlocked your ceiling.

Chopra walked anyway \u2014 and his reasoning cuts against the grain of how Indian sport has long thought about expertise. "Zelezny was a great athlete and a really good coach. We worked on a few specific things, and I'm happy that I broke the 90m mark under him," he said. "But I had to stay in one place to continue working with him, and that wasn't possible for me. After the Tokyo World Championships, we felt it was time for me to work with my own ideas and an Indian coach."

He is now training under Jaiveer "Jay" Chaudhary, the mentor who has been in his inner circle since his earliest days in the sport, and the focus, he says, is on returning to his own natural technique. Even his celebrated 90-metre throw, he suggested, was more a triumph of raw arm speed than of method. "Technically, that throw was not that good. It was really fast from the arm, but if I had used my lower body better, it could have gone two or three metres farther," he said.

## A Stacked Return

Chopra has not made it easy on himself. The nine-man field he returns into is one of the deepest in recent memory. The season's world leader is Sri Lanka's Rumesh Tharanga Pathirage, who threw a jaw-dropping 92.62m in Rome on June 4. Also on the start list are reigning world champion Keshorn Walcott of Trinidad and Tobago, two-time world champion Anderson Peters of Grenada, Tokyo Olympic silver medallist Jakub Vadlejch of Czechia, the evergreen Julius Yego of Kenya and World Championships bronze medallist Curtis Thompson of the United States.

A late addition to the field \u2014 his name was absent from the entry list released on June 12 \u2014 Chopra trained for a 47-day block at Switzerland's Olympic Centre in Bienne with his longtime physiotherapist Ishaan Marwaha and coach Chaudhary, building toward a packed calendar that includes the 2026 Commonwealth Games (where the Athletics Federation of India's provisional nod requires a baseline of 82.61m) and the Asian Games.

## Why the Diaspora Is Watching

For the Indian diaspora, Neeraj Chopra is not just an athlete; he is the rarest of things \u2014 an Indian individual-sport icon who conquered the world, in a discipline with no cricketing safety net. Living rooms in New Jersey, Toronto and Wembley emptied onto WhatsApp the night he won gold in 2021. His face sells everything from insurance to instant noodles. When he competes, NRIs who can name the entire Indian javelin order \u2014 and a few who cannot \u2014 tune in at odd hours to watch one of their own stand on a global podium.

His decision to return to an Indian coach carries a resonance the diaspora will feel keenly. The community is intimately familiar with the foreign-expert premium \u2014 the belief that real polish must be imported. Chopra, having imported the best there is and broken his barrier, has chosen to trust his own instincts and a homegrown mentor instead. It is, in its quiet way, a statement.

He may not win on Friday; nine months is a long time to be away, and Pathirage's 92m looms. But the throw itself is almost beside the point. After a year of injury, doubt and reinvention, India's greatest Olympian is simply back on the runway \u2014 doing it his way, with one of his own beside him. For the millions watching from abroad, that is reason enough to set an alarm."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image...")
img_caption = "Neeraj Chopra, India's double Olympic medallist, returns to competition at the Doha Diamond League after a nine-month injury layoff"
img_attribution = "Wikimedia Commons"
img_final = None

# 1) Try Neeraj Chopra's own Wikipedia portrait
wiki_img = fetch_wikipedia_person_image("Neeraj Chopra")
if wiki_img:
    got = upload_to_supabase(wiki_img, f"{art_slug}.jpg")
    if got:
        img_final = got

# 2) Fallback: on-topic Commons imagery
if not img_final:
    commons_queries = [
        "Neeraj Chopra",
        "Neeraj Chopra javelin",
        "javelin throw athlete India",
        "javelin throw Diamond League",
    ]
    for q in commons_queries:
        cands = fetch_wikimedia_commons_images(q)
        for c in cands:
            low = c["title"].lower()
            print(f"   candidate: {c['title']} ({c['w']}x{c['h']})")
            if any(bad in low for bad in ["logo", ".svg", ".pdf", "map", "seating",
                                           "letters", "diagram", "chart", "flag", "icon"]):
                continue
            if not any(g in low for g in ["neeraj", "chopra", "javelin", "athlet"]):
                continue
            got = upload_to_supabase(c["url"], f"{art_slug}.jpg")
            if got:
                img_final = got
                if "neeraj" in low or "chopra" in low:
                    img_caption = "Neeraj Chopra, India's double Olympic medallist, returns to competition at the Doha Diamond League"
                else:
                    img_caption = "Javelin \u2014 the event in which Neeraj Chopra, India's double Olympic medallist, returns to competition at the Doha Diamond League"
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
    "vertical": "athletics",
    "status": "review",
    "is_editorial": False,
    "image_url": img_final or "",
    "image_caption": img_caption,
    "image_attribution": img_attribution,
    "sources": json.dumps([
        {"name": "Dainik Bhaskar English \u2014 Neeraj Chopra: Injury Reveal, Coach Separation; Tokyo WC & Doha Return", "url": "https://www.bhaskarenglish.in/"},
        {"name": "SportsTak \u2014 'Not a good decision to compete in World Championships': Neeraj Chopra's confession before Doha 2026", "url": "https://www.thesportstak.com/"},
        {"name": "ESPN \u2014 Neeraj Chopra parts ways with coach Jan Zelezny", "url": "https://www.espn.com/"},
        {"name": "PTI / Nagaland Post \u2014 Neeraj Chopra to return to action at Doha Diamond League", "url": "https://www.nagalandpost.com/"},
        {"name": "The Indian Eye \u2014 Neeraj Chopra Set for 2026 Season Debut at Doha Diamond League", "url": "https://theindianeye.com/"},
        {"name": "FloTrack \u2014 Doha Diamond League 2026 Schedule and Start Lists", "url": "https://www.flotrack.org/"},
    ]),
    "diaspora_angle": "Neeraj Chopra is the Indian diaspora's rarest icon \u2014 an individual-sport world conqueror with no cricketing safety net \u2014 and NRIs across the US, UK and Canada set alarms to watch him compete. His return at the Doha Diamond League after a nine-month injury layoff carries an extra charge: he has left the legendary Czech coach Jan Zelezny to train under an Indian mentor, Jaiveer 'Jay' Chaudhary, a quiet rejection of the foreign-expert premium the diaspora knows so well, and a bet on his own instincts ahead of the Commonwealth and Asian Games.",
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
