#!/usr/bin/env python3
"""
Sports Writer — June 24, 2026 (13:30 UTC slot / videshi-writer-sports)

Article: India hosts the Asian Senior Fencing Championships for the first time
(June 19-24, 2026, Bharat Mandapam, New Delhi), with Bhavani Devi's black-card
suspension as the news hook. A niche-but-growing Olympic sport gets its biggest
ever Indian moment — and its biggest star a costly disciplinary blot — just as
the event doubles as an Asian Games qualifier and an LA 2028 ranking meet.

DEDUP CHECK (vs recent feed, last ~4 days of sports):
- Sports feed is cricket-heavy (England/India T20I & ODI squads, Headingley
  Test, women's T20 World Cup, Pant trade, MLC, Vaibhav Sooryavanshi), plus
  athletics one-offs (Animesh Kujur sprinter profile Jun 24, women's 4x100m
  relay gold Jun 24), Jagmeet Singh basketball (Jun 24), para-badminton youth
  games (Jun 23), Manika Batra table tennis (Jun 22).
- FENCING and Bhavani Devi appear NOWHERE in the feed. India hosting the Asian
  Senior Fencing Championships for the first time is wholly uncovered.

Key facts (FIE, Fencing Association of India, PTI/Olympics.com, Sportstar,
Hindustan Times — June 2026):
- Asian Senior Fencing Championships 2026: June 19-24, Bharat Mandapam, New
  Delhi. India hosting for the FIRST TIME EVER. ~34 countries.
- Doubles as a 2026 Asian Games qualifier and carries LA 2028 Olympic ranking
  points.
- India's best results: men's sabre team (Karan Singh, Vishal Thapar and
  others) reached the quarter-finals before losing to China; India finished
  around 10th overall in the medal/team standings. Individually, Karan Singh
  made the top-32 before losing 11-15 to Olympic champion Oh Sang-uk (KOR).
- Women's épée: Prachi Lohan 22nd, Taniksha Khatri 29th. Men's foil: Sachin 25th.
- Bhavani Devi controversy: received a BLACK CARD during the women's sabre team
  event (threw her mask aside after disputing a referee's decision); the FIE
  handed her a TWO-MONTH suspension. She apologized formally; the Fencing
  Association of India appealed to the FIE for a reduction/removal ahead of next
  month's World Championships.
- Bhavani Devi background: full name Chadalavada Anandha Sundhararaman Bhavani
  Devi; first Indian fencer to qualify for the Olympics (Tokyo 2020); first
  Indian to win a medal at the Asian Fencing Championships (sabre bronze, 2023
  Wuxi); multiple Commonwealth fencing golds.
- Other event winners: Oh Sang-uk (KOR) men's sabre individual gold; Japan's
  foil strength; Kazakhstan's Bakaldina women's épée.

DIASPORA ANGLE: Fencing is European/East-Asian by tradition; India has one
genuine global star in Bhavani Devi and almost no grassroots base. Hosting the
continental championships in Delhi is a statement of intent for a country trying
to broaden beyond cricket. For diaspora families in the US, UK and Canada —
where fencing is an established school and college sport, an Ivy League
recruiting pathway — an Indian-hosted Asian Championship is a bridge between
the sport they know abroad and the country they came from.

Hero: Wikipedia/Wikimedia Commons photo of Bhavani Devi (real photo of the
named athlete, 1331x2000 original). Pexels/generic stock NOT used (rules forbid
generic stock for a named athlete).
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
print("ARTICLE: India hosts Asian Fencing Championships + Bhavani Devi")
print("="*60)

art_slug = "india-hosts-asian-senior-fencing-championships-first-time-new-delhi-bhavani-devi-black-card-suspension-2026-diaspora"
art_headline = "India Just Hosted Asia's Biggest Fencing Event for the First Time. Its Brightest Star Left With a Suspension."
art_subheadline = "The Asian Senior Fencing Championships came to New Delhi this week \u2014 a milestone for an Olympic sport India is only beginning to build \u2014 but a black card for Bhavani Devi, the country's first Olympic fencer, cast a shadow over the breakthrough."

art_body = """For one week in June, the cavernous halls of Bharat Mandapam in New Delhi echoed with a sound India's sports fans rarely hear: the clash of blades and the electronic buzz of touches landing in a fencing piste. From June 19 to 24, India hosted the Asian Senior Fencing Championships for the first time in its history, drawing fencers from some 34 countries to a continental showpiece that, until now, had always been somebody else's to stage.

It was a quiet milestone with loud ambitions. The championship is no exhibition: it doubles as a qualifying event for the Asian Games and carries world-ranking points on the long road to the Los Angeles 2028 Olympics. Bringing it to Delhi was a statement from the Fencing Association of India that a sport long confined to the margins of the national imagination wants a seat at the table \u2014 and is willing to build the infrastructure to earn one.

## What India Achieved on the Piste

On the strip, India's results were a portrait of a programme still finding its feet against Asia's powerhouses. The men's sabre team \u2014 led by Karan Singh and Vishal Thapar \u2014 produced the host nation's standout run, fighting into the quarter-finals before falling to a formidable China. Individually, Karan Singh reached the top 32 before losing 11-15 to South Korea's Oh Sang-uk, the reigning Olympic champion who went on to claim individual sabre gold.

Elsewhere the gaps were clearer. In the women's épée, Prachi Lohan finished 22nd and Taniksha Khatri 29th; in the men's foil, Sachin placed 25th. India ended the week around tenth in the overall standings, a respectable showing for a host still decades behind the continent's traditional fencing nations of South Korea, China and Japan, but a long way from the podium. For a sport with almost no grassroots base in India, simply being competitive in the team events on home soil counted as progress.

## The Shadow Over the Week

The headlines, though, belonged to the moment everyone wishes had not happened. Bhavani Devi \u2014 the most decorated fencer India has ever produced \u2014 was shown a black card, the most serious sanction in the sport, during the women's sabre team event after she disputed a referee's decision and threw her mask aside. The International Fencing Federation (FIE) responded with a two-month suspension, a punishment that would sideline her through next month's World Championships.

For Bhavani Devi, the timing could hardly be worse, and the stakes could hardly be higher. She is not just another competitor: she is the woman who in 2020 became the first Indian fencer ever to qualify for the Olympic Games, who took India's first-ever medal at the Asian Fencing Championships with a sabre bronze in Wuxi in 2023, and who has carried the sport's hopes almost single-handedly for a decade. She has issued a formal apology, and the Fencing Association of India has appealed to the FIE for the ban to be reduced or lifted before the Worlds.

That a generational athlete's lapse of composure should overshadow her country's biggest fencing moment is its own kind of cruelty. It is also a reminder of how thin India's fencing depth remains \u2014 in a country with a deeper bench, one star's suspension would not feel like a crisis.

## Why It Matters to the Diaspora

Here is where the story travels. In the United States, Britain and Canada, fencing is not exotic. It is a fixture of school gymnasiums and university athletics programmes, an established route into Ivy League recruiting, a sport that diaspora parents enroll their children in precisely because it is competitive, disciplined and college-friendly. Many Indian-American and British-Indian families know fencing far better than relatives back home ever did.

That gap is exactly what makes an India-hosted Asian Championship significant. It is a bridge between the sport the diaspora already lives with abroad and the country it came from \u2014 a signal that the next Bhavani Devi might be coached in Delhi rather than discovered by accident. India has spent a generation proving it can win beyond cricket, in badminton and wrestling and javelin and chess. Fencing is one of the harder frontiers, with no tradition to lean on and a single world-class name to protect.

This week showed both sides of that reality at once: the ambition to host Asia's best, and the fragility of a programme whose brightest light walked away under a cloud. The blades have been packed away in Bharat Mandapam. What India does next \u2014 with its young sabreurs, and with the star it cannot yet afford to lose \u2014 will decide whether this was a beginning or just a moment."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image (Wikipedia \u2014 Bhavani Devi)...")
img_caption = "Bhavani Devi, India's first Olympic fencer, in competition. A black card at the Asian Championships in New Delhi earned her a two-month suspension."
img_attribution = "Wikimedia Commons"
img_final = None

wiki_img = fetch_wikipedia_person_image("Bhavani Devi")
if wiki_img:
    print(f"  Wikipedia image: {wiki_img}")
    img_final = upload_to_supabase(wiki_img, f"{art_slug}.jpg")

if not img_final:
    print("  \u26a0 No image uploaded \u2014 inserting without image")

art_data = {
    "headline": art_headline,
    "subheadline": art_subheadline,
    "body": art_body,
    "slug": art_slug,
    "category": "sports",
    "vertical": "fencing",
    "status": "review",
    "is_editorial": False,
    "image_url": img_final or "",
    "image_caption": img_caption,
    "image_attribution": img_attribution,
    "sources": json.dumps([
        {"name": "Wikipedia \u2014 Bhavani Devi", "url": "https://en.wikipedia.org/wiki/Bhavani_Devi"},
        {"name": "Wikipedia \u2014 Asian Fencing Championships", "url": "https://en.wikipedia.org/wiki/Asian_Fencing_Championships"},
        {"name": "Olympics.com \u2014 Bhavani Devi profile", "url": "https://www.olympics.com/en/athletes/bhavani-devi"},
        {"name": "Fencing Association of India", "url": "https://fencingindia.org.in/"},
    ]),
    "diaspora_angle": "Fencing is a European and East-Asian sport by tradition, but in the US, UK and Canada it is an established school and college sport and an Ivy League recruiting pathway \u2014 something many diaspora families know far better than relatives back home. India hosting the Asian Senior Fencing Championships for the first time, led by its one global star Bhavani Devi, is a bridge between the sport the diaspora lives with abroad and the country it came from.",
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
