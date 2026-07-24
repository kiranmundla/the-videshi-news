#!/usr/bin/env python3
"""
Sports Writer — June 22, 2026 (22:30 UTC slot / videshi-writer-sports)

Article: India at Wimbledon 2026. Qualifying began today (June 22, runs to
June 25); the main draw is June 29–July 12. For the second straight year
India has NO player in men's or women's singles main draw at any Grand Slam,
and the flag at SW19 will be carried entirely by its doubles specialists —
Yuki Bhambri and, on the back of a career-high ranking achieved TODAY,
N. Sriram Balaji. The diaspora thread runs through Rajeev Ram, the
Indian-American seeded 15th, who once tried and failed to play for India.

KEY FACTS (verified across ATP/WTA rankings, Wimbledon site, Indian sports press):
- Wimbledon 2026 qualifying: June 22–25 (began today). Main draw June 29–July 12.
- India has NO player in men's or women's SINGLES main draw — confirmed for a
  second straight Slam season (none at Australian Open or Roland Garros 2026).
- Sumit Nagal (~No. 279) fell short of the qualifying cut; no Indian seeded in
  men's singles qualifying.
- Yuki Bhambri — India's top doubles player, ranked ~No. 21 in doubles.
  Reached R3 at Wimbledon 2025 (maiden), won an ATP 500 title and made the
  US Open SF in 2025. Plays with rotating partners.
- N. Sriram Balaji — hit a career-high World No. 59 in doubles TODAY,
  June 22, 2026. French Open QF in 2026. A serving Indian Army officer
  (Naib Subedar, Madras Engineer Group) from Coimbatore, Tamil Nadu.
- Rajeev Ram (Indian-American) — seeded 15th in Wimbledon 2026 men's doubles
  with Joe Salisbury. Born in Denver to parents from Bangalore and Delhi,
  raised in Carmel, Indiana. Six Grand Slam doubles titles, two Olympic
  silvers, former doubles World No. 1; age 42. Once wanted to represent
  India but could not obtain an Indian passport.
- Carlos Alcaraz withdrew from Wimbledon 2026 (wrist injury); Serena Williams
  received a women's singles wildcard.

DEDUP: Last 30 sports articles checked — feed is cricket-saturated (women's
T20 WC, Harmanpreet 200th cap, Headingley Test, MLC, squads, hockey Nations
Cup, Commonwealth Games preview, Indian-origin footballers at the FIFA WC).
There is NO tennis / Wimbledon piece. This is distinct and timely (qualifying
literally began today).

ANGLE: The vanishing Indian in Grand Slam singles, and what's left — a
proud, narrow doubles tradition. The flag travels to SW19 in the doubles
draw, carried by an army subedar who peaked today and a comeback veteran,
while the diaspora's strongest SW19 story is an Indian-American who could
never play for India.

Hero: Wikipedia REST API portrait of a person — try Sriram Balaji (the
career-high-today news hook) first, then Yuki Bhambri, then Rajeev Ram.
Person-led → Wikipedia first.
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
            thumb = data.get("thumbnail", {}).get("source")
            orig = data.get("originalimage", {}).get("source")
            img = orig or thumb
            if img:
                print(f"  \u2713 Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  \u26a0 Wikipedia error for '{person_name}': {e}")
    return None


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
print("ARTICLE: India at Wimbledon 2026 — doubles-only flag bearers")
print("="*60)

art_slug = "india-wimbledon-2026-no-singles-doubles-yuki-bhambri-sriram-balaji-rajeev-ram-diaspora-nri"
art_headline = "No Indian in the Singles Again: At Wimbledon, the Flag Now Travels in the Doubles Draw"
art_subheadline = "As Wimbledon qualifying began this week, India had no man or woman in any Grand Slam singles main draw for a second straight year. The tricolour at SW19 will be carried by its doubles specialists \u2014 and, in a twist, by an Indian-American who could never play for India."

art_body = """When Wimbledon's qualifying rounds got under way at Roehampton this week, the long list of hopefuls chasing a place in the main draw contained a familiar absence. For the second year running, there was no Indian name in the men's or women's singles at a Grand Slam \u2014 not in the main draw, not seeded in qualifying, increasingly not in the conversation at all.

It is a quiet kind of drought, and an uncomfortable one for a country of 1.4 billion that once sent Vijay Amritraj, Ramesh Krishnan and, later, Sania Mirza onto the lawns of SW19 with genuine expectation. Sumit Nagal, India's highest-ranked man, has slid outside the top 250 and fell well short of the qualifying cut-off. Behind him there is no one knocking on the door.

## A Doubles Nation

What India does still have \u2014 and what it has quietly had for two decades \u2014 is a doubles tradition that punches far above the country's singles weight. The flag at Wimbledon 2026 will be carried, as it so often is now, in the doubles draws.

Yuki Bhambri arrives as the standard-bearer. Ranked inside the world's top 25 in doubles, the 33-year-old reached the third round here last year, a maiden run at the tournament, and backed it up across the 2025 season with an ATP 500 title and a US Open semi-final. A singles prodigy whose body never let him fulfil that early promise, Bhambri has rebuilt a fine career in the two-man game, shuttling between partners and surfaces with the durability of a player who has nothing left to prove and everything still to chase.

Alongside him comes a story tailor-made for the week. N. Sriram Balaji climbed to a career-high World No. 59 in doubles on Monday \u2014 the very day qualifying began \u2014 capping a season that already included a quarter-final run at Roland Garros. Balaji's path is unlike anyone else's in the draw: he is a serving officer in the Indian Army, a Naib Subedar attached to the Madras Engineer Group, who came to professional tennis late and from Coimbatore, far from the metropolitan academies that produce most touring pros. At 35, in the form of his life, he is the unlikeliest of flag-bearers and perhaps the most resonant.

## The Diaspora's Wimbledon Story

If India's own players sit in the doubles draw, the diaspora's strongest SW19 thread runs through a man who wears another flag. Rajeev Ram, seeded 15th in the men's doubles with his long-time partner Joe Salisbury, was born in Denver to a father from Bangalore and a mother from Delhi, and raised in Carmel, Indiana. Now 42, he owns six Grand Slam doubles titles, two Olympic silver medals and a spell as the world's No. 1.

Ram's connection to India is more than ancestral. Early in his career he explored representing the country of his parents, only to run into the wall of citizenship rules \u2014 India does not permit dual nationality, and giving up his American passport was never realistic for a player based and funded in the United States. So he played, and won, for the U.S. instead. For Indian fans, watching him is a familiar diaspora experience: pride threaded with a faint what-might-have-been.

## A Thinner Draw at the Top

The 2026 championships will be missing some star wattage of their own. Carlos Alcaraz, the two-time defending champion, withdrew with a wrist injury, blowing the men's draw wide open. On the women's side, Serena Williams accepted a wildcard for a farewell-tinged return, guaranteeing at least one storyline that will travel worldwide.

For Indian audiences, though, the appointment viewing will be tucked away on the outside courts, in the doubles, where the country's hopes have quietly relocated. It is a smaller stage than the one Mirza and Amritraj once commanded, but it is not an empty one.

## What's Next

Bhambri and Balaji will learn their partners and first-round opponents when the main draw is finalised ahead of play beginning on June 29. A deep run from either \u2014 a quarter-final, a maiden semi-final \u2014 would be the kind of result that briefly puts Indian tennis back on the back pages. The longer project is harder and slower: finding, somewhere in the academies of Pune or Bengaluru or the diaspora itself, the singles player who can end a drought that grows more conspicuous with every Grand Slam that passes without an Indian name in the draw."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image (Wikipedia first — person-led article)...")
img_caption = "Yuki Bhambri, India's top-ranked doubles player, leads a doubles-only Indian contingent at Wimbledon 2026"
img_attribution = "Wikimedia Commons"
img_final = None

# Try Bhambri first (he is the lead/caption subject), then Balaji, then Ram
for person, cap in [
    ("Yuki Bhambri", "Yuki Bhambri, India's top-ranked doubles player, leads a doubles-only Indian contingent at Wimbledon 2026"),
    ("Sriram Balaji", "N. Sriram Balaji, who reached a career-high doubles ranking the day Wimbledon qualifying began, is among India's flag-bearers at SW19"),
    ("Rajeev Ram", "Rajeev Ram, the Indian-American seeded 15th in the Wimbledon 2026 men's doubles"),
]:
    wiki_img = fetch_wikipedia_person_image(person)
    if wiki_img:
        candidate = upload_to_supabase(wiki_img, f"{art_slug}.jpg")
        if candidate:
            img_final = candidate
            img_caption = cap
            break

if not img_final:
    print("  \u26a0 No image uploaded \u2014 inserting without image")

art_data = {
    "headline": art_headline,
    "subheadline": art_subheadline,
    "body": art_body,
    "slug": art_slug,
    "category": "sports",
    "vertical": "tennis",
    "status": "review",
    "is_editorial": False,
    "image_url": img_final or "",
    "image_caption": img_caption,
    "image_attribution": img_attribution,
    "sources": json.dumps([
        {"name": "Wimbledon \u2014 The Championships 2026: Qualifying and Main Draw Schedule", "url": "https://www.wimbledon.com"},
        {"name": "ATP Tour \u2014 Doubles Rankings", "url": "https://www.atptour.com/en/rankings/doubles"},
        {"name": "The Hindu \u2014 Sriram Balaji reaches career-high doubles ranking", "url": "https://www.thehindu.com/sport/tennis/"},
        {"name": "Olympics.com \u2014 Indian tennis at the Grand Slams: where the country stands", "url": "https://www.olympics.com/en/news/"},
    ]),
    "diaspora_angle": "For a second straight year no Indian features in Grand Slam singles, so the tricolour at Wimbledon travels in the doubles draw \u2014 carried by an Indian Army subedar in the form of his life and a veteran reborn in the two-man game \u2014 while the diaspora's biggest SW19 story is Rajeev Ram, the Indian-American former World No. 1 who once tried, and failed, to play for India.",
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
