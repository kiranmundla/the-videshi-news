#!/usr/bin/env python3
"""
Sports Writer — June 24, 2026 (01:30 UTC slot / videshi-writer-sports)

Article: India's women win the 4x100m relay gold at the 2026 Asian Relays
Championships in Shangyu, China (June 21), beating host China, with a mixed
4x400m silver and mixed 4x100m bronze rounding out a three-medal haul.

Distinct from the recent feed:
- Recent sports feed = IPL Pant-Kuldeep trade, Headingley Test, MLC, white-ball
  squad churn, women's T20 WC, hockey, Wimbledon doubles, para-badminton, FIFA
  WC recaps, Neeraj Chopra Doha DL. NONE cover the Asian Relays Championships
  or Indian women's sprinting. Confirmed zero hits for relay/4x100/shangyu/
  srabani in the article table. Fresh (Sun June 21), uncovered, distinct from
  the throws-heavy Chopra/Sachin Yadav athletics coverage.

Key facts (GKToday, The Bridge, Daily Jagran, The Indian Eye — June 21-22 2026):
- 2nd edition of the Asian Relays Championships, held in Shangyu, China.
- WOMEN'S 4x100m GOLD: Srabani Nanda, SS Sneha, Sudeshna Shivankar, Tamanna —
  43.85s, a season best, beating hosts China (silver, 44.09s) and Thailand
  (bronze, 44.11s). India ran a near-perfect race to stun China at home.
- MIXED 4x400m SILVER: MR Poovamma, Neeru Pathak, Theerthesh P Shetty, Barath
  Sridhar — 3:17.06s, behind Kazakhstan (3:16.75s). India's second straight
  4x400m relay medal at these championships (won gold in the inaugural edition).
- MIXED 4x100m BRONZE: Pranav Gurav, Tamanna, Animesh Kujur, SS Sneha — 41.47s,
  just 0.12s short of the national record set at the World Relays earlier in
  2026 (Thailand gold 41.14s, China silver 41.29s).
- Tamanna and SS Sneha each won two medals across the championship.
- India finished with one gold, one silver and one bronze.
- Off-podium: women's 4x400m fourth (3:47.22s SB), men's 4x400m fifth (3:05.33s).
- India will host the 3rd edition in Chandigarh in 2027.

DIASPORA ANGLE: For a country whose track-and-field pride has rested almost
entirely on Neeraj Chopra's javelin, a women's sprint relay gold won by beating
the host nation is a different kind of statement — proof the talent base is
broadening beyond the throws. With the Glasgow Commonwealth Games weeks away and
India hosting the next Asian Relays in Chandigarh, NRIs invested in India's
Olympic ambitions have a new set of names to follow.

Hero: Wikipedia REST API photo of Srabani Nanda (the most established name in
the gold-winning quartet, person-led source rule). Fallbacks handled in code.
"""

import os, sys, json, io
from datetime import datetime, timezone

import requests
from PIL import Image

# -- ENV --
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


def compress_image(img_bytes, max_width=1200, quality=82):
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()


def fetch_wikipedia_person_image(name):
    """Wikipedia REST summary -> originalimage/thumbnail source URL."""
    import urllib.parse
    enc = urllib.parse.quote(name.replace(" ", "_"))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{enc}",
            headers={"User-Agent": UA}, timeout=20,
        )
        if r.status_code == 200:
            d = r.json()
            orig = d.get("originalimage", {}).get("source")
            thumb = d.get("thumbnail", {}).get("source")
            return orig or thumb
    except Exception as e:
        print(f"  wiki fetch error: {e}")
    return None


def fetch_commons_image(query):
    """Wikimedia Commons search -> first usable image file URL."""
    import urllib.parse
    try:
        api = "https://commons.wikimedia.org/w/api.php"
        params = {
            "action": "query", "format": "json", "generator": "search",
            "gsrsearch": f"{query} filetype:bitmap", "gsrlimit": "8",
            "gsrnamespace": "6", "prop": "imageinfo",
            "iiprop": "url|size", "iiurlwidth": "1200",
        }
        r = requests.get(api, params=params, headers={"User-Agent": UA}, timeout=25)
        if r.status_code != 200:
            return None
        pages = r.json().get("query", {}).get("pages", {})
        best = None
        for _, p in pages.items():
            ii = (p.get("imageinfo") or [{}])[0]
            w = ii.get("width", 0)
            url = ii.get("thumburl") or ii.get("url")
            if url and w >= 600:
                if best is None or w > best[0]:
                    best = (w, url)
        return best[1] if best else None
    except Exception as e:
        print(f"  commons fetch error: {e}")
    return None


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
print("ARTICLE: India women 4x100m relay gold, Asian Relays 2026")
print("="*60)

art_slug = "india-women-4x100m-relay-gold-asian-relays-championships-2026-shangyu-china-srabani-nanda-tamanna-beat-china-sprint-diaspora-nri"
art_headline = "India's Women Sprinters Beat China for Relay Gold \u2014 a Statement Beyond the Javelin"
art_subheadline = "At the Asian Relays Championships in Shangyu, India's women's 4x100m quartet ran down the host nation for gold, and a mixed-relay silver and bronze signalled that the country's track ambitions are spreading well past Neeraj Chopra."

art_body = """For years, India's claim to global track-and-field relevance has been carried, almost single-handedly, on the point of Neeraj Chopra's javelin. On a Sunday in Shangyu, four women sprinters offered a different kind of evidence. India's quartet of Srabani Nanda, SS Sneha, Sudeshna Shivankar and Tamanna clocked a season-best 43.85 seconds to win the women's 4x100 metres relay at the 2026 Asian Relays Championships \u2014 and they did it by beating the host nation, China, into silver on its own track.

It was a near-perfect race. China, roared on at home, were expected to control the event, but the Indian baton moved cleanly through every exchange zone and the lead held to the line. China took silver in 44.09 seconds and Thailand bronze in 44.11. For a discipline in which India has rarely troubled the continent's best, beating the host for gold is the sort of result that tends to mark a turning point rather than a one-off.

## Three Medals, Two Double-Winners

The relay gold headlined a three-medal haul at the championship's second edition. India added a silver in the mixed 4x400 metres relay, where MR Poovamma, Neeru Pathak, Theerthesh P Shetty and Barath Sridhar combined for 3:17.06 to finish behind Kazakhstan (3:16.75) \u2014 the country's second straight medal in that event, having won gold at the inaugural edition two years ago. A bronze followed in the mixed 4x100 metres relay, where Pranav Gurav, Tamanna, Animesh Kujur and SS Sneha ran 41.47 seconds, finishing just 0.12 of a second outside the national record set at the World Relays earlier this year.

Two names appeared on the podium twice. Tamanna and SS Sneha each won a pair of medals across the weekend, anchoring both a mixed relay and the women's 4x100m gold \u2014 the kind of workload that hints at genuine depth rather than a single star carrying a team.

## The Gaps That Remain

The championship was not a clean sweep, and the results were honest about where India still falls short. The women's 4x400 metres relay team finished fourth in a season-best 3:47.22, and the men's 4x400m quartet came home fifth in 3:05.33 \u2014 a reminder that the longer relays, where stamina and strength in depth matter most, remain a work in progress. But a gold, a silver and a bronze, with the marquee result coming against the host, is a meaningful return from a young and rotating squad.

The mixed events in particular point to a system that is now built to produce relay specialists rather than assembling teams from whoever is available. The mixed 4x100m bronze, run within a tenth of a second of a national record set only months earlier, suggests the standard is rising fast enough that records are being chased rather than admired.

## Why the Diaspora Should Be Watching

For Indians abroad, athletics has long been an all-or-nothing affair: Chopra's gold in Tokyo and silver in Paris, and not much else to gather around. A women's sprint relay title, won by running down China, broadens that story. It puts new names \u2014 Srabani Nanda, SS Sneha, Sudeshna Shivankar, Tamanna \u2014 into the conversation, and it does so in the sprints, the events that anchor any serious track nation.

The timing sharpens the point. The Glasgow Commonwealth Games are only weeks away, and the relay squads will arrive there with proof they can beat continental heavyweights. India is also set to host the third edition of the Asian Relays in Chandigarh in 2027, turning a quietly growing program into a home event with a home crowd. For a diaspora that has learned to celebrate Indian athletics one javelin throw at a time, Shangyu offered something to cheer that runs in fours \u2014 and runs fast."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image (Wikipedia/Commons \u2014 Indian sprinting)...")
img_caption = "India's women's 4x100m relay team won gold at the 2026 Asian Relays Championships in Shangyu, China, beating the host nation (representative image of Indian athletics)."
img_attribution = "Wikimedia Commons"
img_final = None

# Person-led source rule: try the most established name in the quartet first.
for cand in ["Srabani Nanda", "Dutee Chand"]:
    wiki_url = fetch_wikipedia_person_image(cand)
    if wiki_url:
        print(f"  Wikipedia image ({cand}): {wiki_url}")
        img_final = upload_to_supabase(wiki_url, f"{art_slug}.jpg")
        if img_final:
            if cand == "Srabani Nanda":
                img_caption = "Srabani Nanda, part of India's gold-winning women's 4x100m relay quartet at the 2026 Asian Relays Championships in Shangyu, China."
            else:
                img_caption = "India's women's 4x100m relay team won gold at the 2026 Asian Relays Championships in Shangyu, China, beating host nation China (representative image of Indian sprinting)."
            break

if not img_final:
    commons_url = fetch_commons_image("India athletics relay sprint women")
    if commons_url:
        print(f"  Commons image: {commons_url}")
        img_final = upload_to_supabase(commons_url, f"{art_slug}.jpg")

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
        {"name": "The Bridge \u2014 Asian Relays 2026: India beat China to win women's 4x100m gold", "url": "https://thebridge.in/"},
        {"name": "The Daily Jagran \u2014 Asian Relays Championships 2026: India Win Women's 4x100m Gold, Add Silver And Bronze On Final Day", "url": "https://www.thedailyjagran.com/"},
        {"name": "GKToday \u2014 India Wins Women's 4x100m Relay Gold", "url": "https://www.gktoday.in/"},
    ]),
    "diaspora_angle": "Indian athletics has rested almost entirely on Neeraj Chopra's javelin; a women's sprint relay gold won by beating host China broadens that story with new names, just weeks before the Glasgow Commonwealth Games and with India set to host the next Asian Relays in Chandigarh in 2027 \u2014 a fresh rallying point for NRIs invested in India's Olympic ambitions.",
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
