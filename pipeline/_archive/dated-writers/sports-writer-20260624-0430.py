#!/usr/bin/env python3
"""
Sports Writer — June 24, 2026 (04:30 UTC slot / videshi-writer-sports)

Article: England name a 17-man T20I squad (June 22) for the five-match home
series against India (July 1-11), their first T20I assignment since losing
the 2026 T20 World Cup semifinal to India. Revenge-series framing, key
ins/outs, strong UK-diaspora hook (Old Trafford, Trent Bridge crowds).

Distinct from recent feed:
- Recent sports feed = India's OWN selection churn (Suryakumar sacked, Shreyas
  Iyer captain), Nitish Reddy ruled out, ODI squad, Headingley Test, MLC,
  women's T20 WC, hockey, Wimbledon doubles, para-badminton, Asian Relays.
- NONE cover ENGLAND's T20I squad announcement or the revenge-series framing.
  This is the counterpart story from the England side — genuinely fresh and
  uncovered. Confirmed zero hits for "England squad"/"Harry Brook"/"Chester-
  le-Street" in the recent sports table.

Key facts (Sportskeeda, Reuters, Wikipedia "Indian cricket team in England in
2026", South Asian Herald — June 22-24 2026):
- England named a 17-member squad on Monday, June 22 for a five-match home T20I
  series vs India. Harry Brook continues as captain.
- This is England's first T20I assignment since the 2026 T20 World Cup, where
  they were knocked out in the semifinal by India.
- Sussex all-rounder James Coles received a maiden call-up.
- Out-of-form veteran keeper-bat Jos Buttler retained despite a dismal WC.
- Jordan Cox, Sonny Baker and Saqib Mahmood return after missing the WC.
- Pace-bowling all-rounders Jamie Overton (quad) and Brydon Carse (hand) miss
  out injured. Opener Ben Duckett, who didn't feature at the WC, also misses.
- Squad: Harry Brook (c), Rehan Ahmed, Jofra Archer, Sonny Baker, Tom Banton,
  Jacob Bethell, Jos Buttler (wk), James Coles, Jordan Cox, Sam Curran, Liam
  Dawson, Will Jacks, Saqib Mahmood, Adil Rashid, Phil Salt, Josh Tongue,
  Luke Wood.
- Schedule (all 5 T20Is): 1 Jul Chester-le-Street (Riverside), 4 Jul Old
  Trafford Manchester, 7 Jul Trent Bridge Nottingham, 9 Jul Bristol (County
  Ground), 11 Jul Southampton (Rose Bowl). ODIs follow Jul 14/16/19.
- On India's side: Shreyas Iyer leads a refreshed T20I squad after Suryakumar
  Yadav was dropped; Nitish Kumar Reddy ruled out injured, replaced by
  Suryansh Shedge. India play two T20Is in Belfast vs Ireland (Jun 26, 28)
  before the England leg.

DIASPORA ANGLE: This is the marquee white-ball summer for British-Indian fans —
five T20Is at grounds with some of the largest desi crowds in world cricket
(Old Trafford, Trent Bridge), and the first India-England meeting since India
ended England's home World Cup in the semis. For NRIs across the UK it is a
ticketed, in-person revenge narrative on their doorstep.

Hero: Wikipedia REST API photo of Harry Brook (England captain, the headline
figure). Fallbacks: Jos Buttler, then Commons "England cricket team".
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
print("ARTICLE: England name T20I squad vs India, WC revenge series")
print("="*60)

art_slug = "england-t20i-squad-india-2026-harry-brook-captain-jos-buttler-james-coles-jofra-archer-five-match-series-world-cup-semifinal-rematch-diaspora-nri"
art_headline = "England Name Their Squad for India \u2014 and a World Cup Score to Settle at Home"
art_subheadline = "Beaten by India in the T20 World Cup semifinal, England have picked a 17-man squad for a five-match home series starting July 1, keeping faith with Jos Buttler and handing Sussex's James Coles a maiden call-up \u2014 the start of a white-ball summer that will fill Old Trafford and Trent Bridge with the diaspora."

art_body = """The last time England and India met in a Twenty20 international, it was a World Cup semifinal on home soil, and it ended with India walking off and England walking out of their own tournament. On Monday, England named the squad that will get the first chance at a reply. Harry Brook will captain a 17-man group for a five-match home T20I series against India that begins on July 1 \u2014 the team's first assignment in the format since that semifinal exit, and the opening act of a white-ball summer loaded with subplots.

The headline selection call was an act of faith. Jos Buttler, whose World Cup campaign was bleak by his own towering standards, was retained as the squad's wicketkeeper-batter, a vote of confidence in a senior figure England are not ready to move past. Around him, the selectors leaned on continuity at the top while reaching for one fresh face: Sussex all-rounder James Coles earned a maiden international call-up, the kind of pick that signals England are still hunting for the next generation even in a revenge series.

## Who's In, Who's Out

There were welcome returns. Jordan Cox, Sonny Baker and Saqib Mahmood are all back in the fold after missing the 2026 World Cup, adding pace and depth to a squad that will need it across five matches in eleven days. The bowling group is anchored by the familiar names \u2014 Jofra Archer, Adil Rashid, Sam Curran and Liam Dawson \u2014 with Josh Tongue and Luke Wood adding seam options.

The absentees told their own story. Pace-bowling all-rounders Jamie Overton and Brydon Carse, two of England's more dynamic options, both miss out injured \u2014 Overton with a quad problem, Carse with a hand injury. Opener Ben Duckett, who did not feature in a single game at the World Cup, was also left out, a reminder that England's T20 top order remains a crowded, contested space.

The full squad: Harry Brook (captain), Rehan Ahmed, Jofra Archer, Sonny Baker, Tom Banton, Jacob Bethell, Jos Buttler (wk), James Coles, Jordan Cox, Sam Curran, Liam Dawson, Will Jacks, Saqib Mahmood, Adil Rashid, Phil Salt, Josh Tongue and Luke Wood.

## A Different India to the One They Remember

India arrive in a state of deliberate reinvention. The team that beat England in the semifinal has been reshaped: Suryakumar Yadav, the man who lifted the World Cup, has been dropped, with Shreyas Iyer installed as the new T20I captain. The visitors have also been hit by an injury of their own \u2014 all-rounder Nitish Kumar Reddy has been ruled out and replaced by uncapped batting all-rounder Suryansh Shedge, who earned the nod after a productive India A tri-series in Sri Lanka.

India will be match-hardened by the time they reach English soil. Iyer's side play two T20Is against Ireland in Belfast on June 26 and 28 before crossing to England, where the schedule then unfolds at pace: Chester-le-Street on July 1, Old Trafford on July 4, Trent Bridge on July 7, Bristol on July 9 and Southampton's Rose Bowl on July 11, with a three-match ODI series to follow at Edgbaston, Cardiff and Lord's.

## Why the Diaspora Should Be Watching

For British-Indian fans, this is the summer's centrepiece. The T20Is land at grounds that, whenever India visit, turn into something close to home fixtures \u2014 Old Trafford and Trent Bridge routinely host some of the loudest desi crowds in world cricket, and Edgbaston's ODI will be no different. A five-match series spread across the country means the contest is within a train ride of almost every major diaspora community in England, from the North West to the Midlands to the South Coast.

The narrative sharpens it further. This is the first India-England meeting since India ended England's World Cup, and it pits a settled, confident Indian white-ball unit against a host side carrying both a grudge and a point to prove. For the millions of Indians in Britain who have spent a decade buying tickets to watch their team in someone else's stadium, July offers five chances to do it again \u2014 with a freshly named England squad lining up on the other side, and a score from the semifinal still hanging in the air."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image (Wikipedia/Commons \u2014 England cricket)...")
img_caption = "England's T20I squad will face India in a five-match home series starting July 1, 2026 (representative image of England cricket)."
img_attribution = "Wikimedia Commons"
img_final = None

# Person-led source rule: try the headline figure (captain) first.
person_caps = {
    "Harry Brook": "Harry Brook, who will captain England in the five-match home T20I series against India starting July 1, 2026.",
    "Jos Buttler": "Jos Buttler, retained in England's T20I squad for the 2026 home series against India.",
    "Jofra Archer": "Jofra Archer, named in England's T20I squad for the 2026 home series against India.",
}
for cand, cap in person_caps.items():
    wiki_url = fetch_wikipedia_person_image(cand)
    if wiki_url:
        print(f"  Wikipedia image ({cand}): {wiki_url}")
        img_final = upload_to_supabase(wiki_url, f"{art_slug}.jpg")
        if img_final:
            img_caption = cap
            break

if not img_final:
    commons_url = fetch_commons_image("England cricket team T20")
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
    "vertical": "cricket",
    "status": "review",
    "is_editorial": False,
    "image_url": img_final or "",
    "image_caption": img_caption,
    "image_attribution": img_attribution,
    "sources": json.dumps([
        {"name": "Sportskeeda \u2014 England announce squad for ENG vs IND 2026 T20Is", "url": "https://www.sportskeeda.com/cricket"},
        {"name": "Reuters \u2014 Injured Reddy to miss India's T20I series against England, Ireland", "url": "https://www.reuters.com/sports/cricket/"},
        {"name": "Wikipedia \u2014 Indian cricket team in England in 2026", "url": "https://en.wikipedia.org/wiki/Indian_cricket_team_in_England_in_2026"},
        {"name": "South Asian Herald \u2014 India Announces Squad for Ireland and England T20I Series", "url": "https://southasianherald.com/"},
    ]),
    "diaspora_angle": "The five-match T20I series lands at grounds with some of the largest British-Indian crowds in world cricket \u2014 Old Trafford, Trent Bridge, Edgbaston \u2014 and is the first India-England meeting since India ended England's home T20 World Cup in the semifinal, putting a ticketed revenge narrative on the diaspora's doorstep across England this July.",
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
