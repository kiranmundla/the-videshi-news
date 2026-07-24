#!/usr/bin/env python3
"""
Sports Writer — June 25, 2026 (23:30 PT slot / videshi-writer-sports)

Article: Arvid Lindblad — the 18-year-old Racing Bulls rookie and first F1 driver
of Indian heritage in over a decade — heads into this weekend's Austrian Grand
Prix (June 26-28, Red Bull Ring) carrying the British, Swedish AND Indian flags
on his helmet. Diaspora angle: India has had only two F1 drivers ever (Narain
Karthikeyan, Karun Chandhok); Lindblad, son of a British-Indian mother, is the
closest thing the sport has had to an Indian presence on the grid since 2010,
and he is doing it as a Red Bull junior with 13 points in his rookie half-season.

DEDUP CHECK (vs recent ~3-4 days sports feed, category=sports):
- Feed HAS (last 3 days): MLC Oakland Coliseum debut / SF Unicorns; India Women
  vs Bangladesh T20 WC; India-Ireland T20I preview (Iyer era); Dev Meena pole
  vault; women's hockey Nations Cup; Edgbaston Test preview; Sooryavanshi
  safeguarding/fastest-fifty; Neeraj Chopra Doha; BWF Worlds Delhi; athletics
  awards; fencing; Animesh Kujur sprinter; Jagmeet Singh basketball; England
  T20I squad; women's relay gold; Pant-to-Delhi trade; para-badminton; Reddy
  injury; Headingley Test.
- NO Formula 1 article in the feed. NO Arvid Lindblad article. This is a
  motorsport / F1 diaspora story, an entirely new sport for the feed and a
  fresh named subject. CLEAR TO WRITE.

Key facts (Wikipedia 'Arvid Lindblad'; Sky Sports; ESPN; The Times; Formula1.com;
Sporting News; Sky Sports Austrian GP schedule):
- Arvid Anand Olof Lindblad, born 8 Aug 2007 in Virginia Water, Surrey. Swedish
  father, British-Indian mother. Races under British flag; helmet carries
  British, Swedish AND Indian flags. Visited India to connect with maternal
  roots Jan 2025.
- Red Bull Junior Team member since 2021 (aged 13). Karting from age 5. British
  Cadet Champion 2019. Mentored by Formula E champion Oliver Rowland.
- Junior record: Italian F4 (3rd, 2023, Prema); Macau F4 race winner 2023; FIA
  F3 2024 (youngest F3 race winner); FR Oceania title 2025 (M2); FIA F2 2025
  (Campos) — became youngest race-winner in F2 history; finished 6th/7th in F2.
- F1 2026: Racing Bulls-Red Bull Ford, car #41, alongside Liam Lawson. Debuted
  at 2026 Australian GP aged 18, finished 8th (4 points) on debut — youngest
  British F1 driver ever, third-youngest F1 debutant ever.
- Career so far (per Wikipedia infobox, to Barcelona-Catalunya GP): 7 entries,
  6 starts, 13 career points. Back-to-back recent fantasy scores 18 and 10;
  leads all drivers for total overtakes (10) across the last two race weekends
  (Formula1.com fantasy preview).
- India's F1 history: only TWO Indian drivers ever — Narain Karthikeyan
  (Jordan, 2005) and Karun Chandhok (HRT, 2010). No driver with Indian roots
  on the grid since Chandhok in 2011. (Force India was a team, not a driver.)
- This weekend: Austrian Grand Prix, Red Bull Ring, Spielberg. Practice Fri
  June 26, qualifying Sat June 27, race Sun June 28 (2pm UK / 3pm local). First
  of a double-header with the British GP at Silverstone the following weekend
  (July 3-5) — Lindblad's home race.

Hero: Wikipedia/Wikimedia photo of Arvid Lindblad (Melbourne, 2026). Permanent
Wikimedia URL via Wikipedia REST API, downloaded + re-uploaded to Supabase.
"""

import os, io, json, subprocess
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


def compress_image(img_bytes, max_width=1200, quality=85):
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
    """Return (thumb_or_original_url) from Wikipedia REST summary, or None."""
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{name.replace(' ', '_')}"
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code != 200:
            return None
        d = r.json()
        # Prefer originalimage for full-res; fall back to thumbnail.source AS-IS.
        orig = d.get("originalimage", {}).get("source")
        thumb = d.get("thumbnail", {}).get("source")
        return orig or thumb
    except Exception as e:
        print(f"  wiki image error: {e}")
        return None


def upload_to_supabase(img_url, filename):
    try:
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


print("\n" + "=" * 60)
print("ARTICLE: Arvid Lindblad, F1's Indian-heritage rookie, into Austria")
print("=" * 60)

art_slug = "arvid-lindblad-f1-indian-heritage-racing-bulls-rookie-austrian-grand-prix-2026-red-bull-ring-karthikeyan-chandhok-diaspora-nri"
art_headline = "An 18-Year-Old With an Indian Flag on His Helmet Is the Closest Thing F1 Has Had to India in 15 Years"
art_subheadline = "Racing Bulls rookie Arvid Lindblad — born to a British-Indian mother and a Swedish father — arrives at this weekend's Austrian Grand Prix as the only driver of Indian heritage on the grid since Karun Chandhok in 2011."

art_body = """When the lights go out at the Red Bull Ring on Sunday, the youngest British driver in Formula 1 history will be somewhere in the midfield, hunting points in a car that has surprised people all season. His name is Arvid Lindblad, he is 18, and on the side of his helmet sit three flags: the Union Jack, the blue-and-yellow of Sweden, and the Indian tricolour. For a sport that India has watched from a distance for most of its history, that third flag carries a lot of weight.

Lindblad races under a British licence, but he has never hidden the rest of who he is. Born in Virginia Water, Surrey, to a Swedish father and a British-Indian mother, he has spoken openly about being proud to represent Great Britain, Sweden and India "whenever I race." In January 2025 he travelled to India to connect with his maternal roots. The flags on the helmet are not a marketing flourish; they are a statement about a multicultural upbringing that he wears at 220mph.

## Why this matters to India

The hard truth is that India has barely existed in Formula 1. In more than seven decades of the world championship, exactly two Indian drivers have ever started a grand prix: Narain Karthikeyan, who debuted for Jordan in 2005, and Karun Chandhok, who raced for the cash-strapped HRT team in 2010. After Chandhok's brief run, the grid went silent on India. Force India was an Indian-owned team, but it never fielded an Indian driver. Since 2011, there has been no one on the grid with Indian blood — until now.

That is what makes Lindblad's rise resonate well beyond Surrey. He is not Indian by passport, and he is careful never to overstate it, but for a diaspora that has produced cricketers, chess prodigies and Silicon Valley chief executives, a teenager with Indian heritage competing at the absolute pinnacle of motorsport is a genuinely new kind of story.

## A meteoric climb

Lindblad's ascent has been almost absurdly fast. He first sat in a go-kart at five, became a British Cadet karting champion at 11, and signed to the Red Bull Junior Team in 2021 when he was just 13 — a rare bet on a child by the most ruthless talent pipeline in the sport. He won the Macau Formula 4 race, took podiums in FIA Formula 3 as its youngest-ever race winner, claimed the Formula Regional Oceania title, and then in 2025 became the youngest race winner in Formula 2 history.

Red Bull, never sentimental, fast-tracked him into a 2026 race seat at its junior team, Racing Bulls, alongside Liam Lawson. When he lined up in Melbourne in March he became the youngest British driver ever to start a Formula 1 race, and the third-youngest debutant the sport has seen. He marked it with an eighth-place finish and four points — the kind of unflustered debut that makes paddock veterans take notice.

## Finding his feet

Half a season in, the numbers back up the hype. Lindblad has collected 13 championship points across his opening races, and he has been getting stronger as the year goes on. Heading into this double-header — Austria this weekend, his home British Grand Prix at Silverstone the next — he leads every driver on the grid for total overtakes across the last two rounds, a statistic that speaks to the fearless racecraft that first caught Red Bull's eye. His idol growing up was Lewis Hamilton, another British driver of colour who debuted, fittingly, in 2007, the year Lindblad was born.

## The weekend ahead

The Austrian Grand Prix runs from Friday to Sunday at the Red Bull Ring in Spielberg, with practice on Friday, qualifying on Saturday and the race on Sunday. It is a short, sharp circuit that rewards exactly the decisive, late-braking aggression Lindblad has built his reputation on, and his Racing Bulls car has been quick enough to score points on its day. Then it is straight on to Silverstone, where the British crowd will roar for a hometown teenager — and where, dotted through the grandstands, there will be Indian fans waving for the flag on his helmet. India has waited 15 years for a reason to care about a Formula 1 driver again. It may finally have found one."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing hero image (Wikipedia REST \u2014 Arvid Lindblad)...")
img_caption = "Arvid Lindblad, the 18-year-old Racing Bulls rookie of Indian and Swedish heritage, in Melbourne during the 2026 Formula 1 season."
img_attribution = "Wikimedia Commons"

wiki_img = fetch_wikipedia_person_image("Arvid Lindblad")
img_final = None
if wiki_img:
    print(f"  Wikipedia image: {wiki_img}")
    img_final = upload_to_supabase(wiki_img, f"{art_slug}.jpg")

if not img_final:
    print("  \u26a0 Wikipedia upload failed \u2014 trying thumbnail URL as-is")
    img_final = upload_to_supabase(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Arvid_Lindblad_at_the_Red_Bull_Fan_Zone_%E2%80%93_Crown_Riverwalk%2C_Melbourne_%28028A7869%29_%28cropped%29.jpg/330px-Arvid_Lindblad_at_the_Red_Bull_Fan_Zone_%E2%80%93_Crown_Riverwalk%2C_Melbourne_%28028A7869%29_%28cropped%29.jpg",
        f"{art_slug}.jpg",
    )

art_data = {
    "headline": art_headline,
    "subheadline": art_subheadline,
    "body": art_body,
    "slug": art_slug,
    "category": "sports",
    "vertical": "motorsport",
    "status": "review",
    "is_editorial": False,
    "image_url": img_final or "",
    "image_caption": img_caption,
    "image_attribution": img_attribution,
    "sources": json.dumps([
        {"name": "Wikipedia \u2014 Arvid Lindblad (biography, heritage, junior record, F1 debut, career points)", "url": "https://en.wikipedia.org/wiki/Arvid_Lindblad"},
        {"name": "Sporting News \u2014 Who is Arvid Lindblad? Racing driver with Indian-Swedish heritage set for F1 debut", "url": "https://www.sportingnews.com/"},
        {"name": "Sky Sports \u2014 Austrian GP 2026: schedule, start time and how to watch", "url": "https://www.skysports.com/f1"},
        {"name": "Formula1.com \u2014 F1 Fantasy Strategist Preview, Austrian and British Grands Prix (Lindblad overtakes, form)", "url": "https://www.formula1.com/"},
    ]),
    "diaspora_angle": "Arvid Lindblad, born to a British-Indian mother, is the first driver of Indian heritage on the Formula 1 grid since Karun Chandhok in 2011 \u2014 giving the diaspora a reason to follow the sport again as he races this weekend in Austria.",
    "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}

art_id = insert_article(art_data)
print("\nDONE." if art_id else "\nFAILED to insert.")
