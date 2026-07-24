#!/usr/bin/env python3
"""
Sports Writer — June 24, 2026 (07:30 UTC slot / videshi-writer-sports)

Article: A 7'4" teenager from Hoshiarpur, Punjab — Jagmeet Singh — has gone
viral after dominating the Courtside June Camp (June 20-21), with NBA fans and
Spurs supporters dubbing him the "Indian Wemby" (after Victor Wembanyama, also
7'4"). Class of 2027 big man, has played the India U16 pipeline (FIBA U16 Asia),
linked to Chicago-area development. NBA Draft Room projects him a possible
second-round pick in 2028/2029. Diaspora angle: India has never sent a player
to the NBA via the traditional HS-to-draft pipeline; this is a window into the
country's slowly maturing basketball ecosystem (NBA Academy India, Princepal
Singh's G League Ignite path), and the buzz is concentrated in North American
gyms where the desi diaspora is largest.

Distinct from recent feed:
- Recent sports feed = ALL cricket (England/India T20I & ODI squads, Headingley
  Test, women's T20 World Cup, MLC, Pant trade, Wimbledon doubles) plus a few
  athletics/hockey/para-badminton pieces. ZERO basketball, ZERO NBA, ZERO
  India-to-NBA-pipeline coverage. This is a genuinely fresh vertical for the
  feed and a non-cricket diaspora story.

Key facts (Heavy, Fadeaway World, HITC, The Ringer/Wikipedia for context —
June 21-23 2026):
- Jagmeet Singh, 18, born in Hoshiarpur, Punjab; listed 7'4"; Class of 2027.
- Went viral after Courtside Films posted clips from the Courtside June Camp
  (camp held ~June 20-21, post dated June 21, 2026); clips show him finishing
  at the rim, protecting the paint, handling in transition, flashing perimeter
  touch — rare mobility/skill for his height.
- Fans/Spurs supporters dubbed him "Indian Wemby" (Victor Wembanyama is also
  7'4", 22, reigning Defensive Player of the Year, just played 2026 NBA Finals).
- Singh has represented India at youth level incl. FIBA U16 Asia (Qatar) and
  has been linked to grassroots development in the Chicago area; previously
  associated with Don Bosco Institute.
- NBA Draft Room projects him a possible 2nd-round pick in the 2028 or 2029 NBA
  Draft — i.e. years away; no major college commitment / recruiting ranking yet.
- Context: India has never produced an NBA player via the traditional
  high-school-to-draft pipeline. Closest pipeline successes: Satnam Singh
  (first India-born NBA draftee, 2015, Dallas), Princepal Singh (NBA Academy
  India grad, NBA G League Ignite 2021, 2021 Summer League title with the Kings).
  NBA Academy India (Delhi NCR) and NBA-led grassroots have been building the
  base for a decade.

DIASPORA ANGLE: For the millions of Indians in the US and Canada — where
basketball, not cricket, is the playground sport their kids grow up on — a
7'4" Punjabi teenager being talked about in the same breath as Wembanyama is
a rare moment of representation in a North American sport. The buzz is loudest
in the very gyms, camps and AAU circuits where diaspora families already live.

Hero: Wikimedia Commons photo from NBA Academy/Basketball School India
(representative of India's NBA pipeline — no real photo of this brand-new
prospect exists yet). Pexels NOT used (allowed images only; person-named
subject has no Wikipedia page).
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
print("ARTICLE: 7'4\" Punjab teen 'Indian Wemby' goes viral")
print("="*60)

art_slug = "jagmeet-singh-74-punjab-india-basketball-prospect-viral-indian-wemby-victor-wembanyama-courtside-camp-nba-pipeline-diaspora"
art_headline = "A 7-Foot-4 Teenager From Punjab Has the NBA Internet Calling India Its Next 'Wemby'"
art_subheadline = "Jagmeet Singh, an 18-year-old big man from Hoshiarpur, went viral after a prospect camp in the United States \u2014 and for a country that has never produced an NBA draftee through the traditional pipeline, the hype is its own kind of milestone."

art_body = """A clip is all it took. Over the weekend, a video from the Courtside June Camp in the United States began ricocheting across basketball social media: a 7-foot-4 teenager catching lobs, swatting shots, pushing the ball in transition and \u2014 most improbably for someone his size \u2014 stepping out to shoot. The player was Jagmeet Singh, an 18-year-old from Hoshiarpur, Punjab, and within hours the internet had handed him a nickname it could not resist: the "Indian Wemby."

The comparison is to Victor Wembanyama, the San Antonio Spurs phenomenon who is also listed at 7-foot-4, who leads the NBA in blocks and who was just named Defensive Player of the Year. Wembanyama is 22 and already called generational. Singh is four years younger and still in high school, in the Class of 2027. By any sober measure the comparison is premature. But sober measure is not what the internet does, and the clips of a Punjabi teenager moving with that kind of fluidity were enough to make scouts and fans alike stop scrolling.

## Why The Hype, And Why The Caution

Height you cannot teach, and at 7-foot-4 with an enormous standing reach, Singh already owns a physical profile that fewer than a handful of people on earth share. The harder part for players that tall is usually mobility \u2014 the coordination to run, handle and finish without looking like they are wading through water. That is precisely the part of Singh's game that went viral. The footage showed him finishing cleanly around the basket, protecting the rim, and flashing the kind of perimeter touch that modern basketball prizes above almost everything else.

It is worth being clear-eyed about where he actually is. Singh has represented India at youth level, including a FIBA Under-16 Asia campaign in Qatar, and has been linked to grassroots development in the Chicago area, with earlier ties to the Don Bosco Institute. He has no major college commitment yet and no settled ranking from the big recruiting services. NBA Draft Room projects him, speculatively, as a possible second-round pick in the 2028 or 2029 NBA Draft \u2014 which is to say, years away, with a great deal of basketball still to be played. The "Indian Wemby" label will follow him whether it is fair or not, carrying both pressure and a visibility most international teenagers never get this early.

## A Country Still Waiting For Its First Pipeline Star

What makes the moment resonate beyond the highlight reel is context. India has produced cricket icons, badminton champions and chess grandmasters, but it has never sent a player to the NBA through the conventional high-school-to-draft route. The closest the country has come are landmark one-offs: Satnam Singh, the first India-born player drafted into the NBA, taken by Dallas in 2015, and Princepal Singh, an NBA Academy India graduate who signed with the NBA G League Ignite in 2021 and won a Summer League title with the Sacramento Kings.

Those names matter because they were not accidents. For roughly a decade, the NBA Academy India in the Delhi region and a widening web of camps and showcases have been quietly building a base, identifying tall, raw athletes and teaching them the game. Singh is, in that sense, a product of a system that is finally maturing \u2014 a system designed to turn precisely his kind of size and athleticism into something the rest of the world notices.

## Why The Diaspora Is Watching

For the Indian diaspora in North America, the story lands differently than it does back home. In the United States and Canada, basketball \u2014 not cricket \u2014 is the sport many diaspora kids grow up playing in driveways, school gyms and AAU circuits. A 7-foot-4 Punjabi teenager being discussed in the same sentence as Wembanyama is a rare flash of representation in a game that is woven into daily American life, and the buzz is loudest in exactly the spaces where diaspora families already are.

None of it guarantees anything. Viral camp clips have launched plenty of teenagers who never reached the league. But for a community that has spent years cheering Indian success in other sports while waiting for a homegrown NBA breakthrough, a few seconds of footage from a camp gym have offered something to dream on \u2014 and a name, Jagmeet Singh, worth remembering."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image (Wikimedia Commons \u2014 India NBA pipeline)...")
img_caption = "A young player trains at the NBA Basketball School in New Delhi; India's NBA development pipeline has been building for a decade (representative image)."
img_attribution = "Wikimedia Commons"
img_final = None

# No Wikipedia page exists for this brand-new prospect; use a representative
# Commons photo of India's NBA development pipeline.
commons_candidates = [
    ("https://upload.wikimedia.org/wikipedia/commons/e/ef/Govinda_sharma_in_nba_academy.jpg",
     "A young Indian player trains at the NBA Basketball School in New Delhi; India's NBA development pipeline has been building for a decade (representative image)."),
]
for url, cap in commons_candidates:
    print(f"  Commons image: {url}")
    img_final = upload_to_supabase(url, f"{art_slug}.jpg")
    if img_final:
        img_caption = cap
        break

if not img_final:
    commons_url = fetch_commons_image("basketball India players")
    if commons_url:
        print(f"  Commons fallback image: {commons_url}")
        img_final = upload_to_supabase(commons_url, f"{art_slug}.jpg")
        if img_final:
            img_caption = "Basketball in India: the country's grassroots and academy system is producing a new generation of prospects (representative image)."

if not img_final:
    print("  \u26a0 No image uploaded \u2014 inserting without image")

art_data = {
    "headline": art_headline,
    "subheadline": art_subheadline,
    "body": art_body,
    "slug": art_slug,
    "category": "sports",
    "vertical": "basketball",
    "status": "review",
    "is_editorial": False,
    "image_url": img_final or "",
    "image_caption": img_caption,
    "image_attribution": img_attribution,
    "sources": json.dumps([
        {"name": "Heavy \u2014 Spurs Fans Are Eyeing Viral 7'4\" Prospect From India as Wemby's Future Rival", "url": "https://heavy.com/sports/nba/san-antonio-spurs/spurs-viral-74-india-wembys-future-rival/"},
        {"name": "Fadeaway World \u2014 7-Foot-4 Indian Prospect Jagmeet Singh Dominates At Courtside Camp", "url": "https://fadeawayworld.net/"},
        {"name": "HITC \u2014 7'4 'Indian Wemby' goes viral thanks to astonishing prospect camp video", "url": "https://www.hitc.com/"},
        {"name": "Wikipedia \u2014 Princepal Singh (India's NBA G League pipeline)", "url": "https://en.wikipedia.org/wiki/Princepal_Singh"},
    ]),
    "diaspora_angle": "For the Indian diaspora in the US and Canada \u2014 where basketball, not cricket, is the sport their kids grow up playing \u2014 a 7-foot-4 Punjabi teenager being compared to Victor Wembanyama is a rare moment of representation in a North American game, and the buzz is loudest in the very camps and AAU circuits where diaspora families already live.",
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
