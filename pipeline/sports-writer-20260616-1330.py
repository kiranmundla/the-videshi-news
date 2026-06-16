#!/usr/bin/env python3
"""
Sports Writer — June 16, 2026 (13:30 UTC run)
Article: Nishesh Basavareddy, the 21-year-old Indian-American who upset
then-world-No.9 Taylor Fritz at the 2026 French Open, has been seeded No. 26
in the 2026 Wimbledon men's singles qualifying draw (Roehampton, June 22-25).
The diaspora angle: a Telugu-heritage kid from Carmel, Indiana, whose parents
emigrated from Nellore, now faces the one surface he has barely touched as a
pro — grass — with a Grand Slam main-draw spot on the line. Tennis is a clear
gap in the section's last 72 hours of cricket/football coverage.
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
            img = data.get("thumbnail", {}).get("source")
            if img:
                print(f"  \u2713 Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  \u26a0 Wikipedia error for '{person_name}': {e}")
    return None


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
            data=compressed,
            timeout=30,
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
print("ARTICLE: Nishesh Basavareddy — Wimbledon qualifying, grass test")
print("="*60)

art_slug = "nishesh-basavareddy-wimbledon-2026-qualifying-seed-26-indian-american-telugu-nellore-grass-fritz-nri"
art_headline = "He Beat the World No. 9 on Clay in Paris. Now the Indian-American Faces the One Surface He Has Never Played as a Pro."
art_subheadline = "Nishesh Basavareddy, the 21-year-old from Carmel, Indiana, whose parents emigrated from Nellore, has been seeded No. 26 for Wimbledon qualifying starting June 22. His career grass-court record on tour: zero matches."

art_body = """When the seedings for the 2026 Wimbledon men's singles qualifying draw were published on Monday, name number 26 belonged to an American with a Telugu surname: Nishesh Basavareddy. The qualifying competition runs from June 22 to 25 at the Bank of England Sports Ground in Roehampton, the unglamorous proving ground a few miles from the All England Club where 128 players fight for just sixteen places in the Wimbledon main draw. For a particular slice of the Indian diaspora, Basavareddy is the name to watch.

He is, on paper, exactly the kind of player who should sail through. Just three weeks ago, at the French Open, the 21-year-old produced the result of his young career: a four-set first-round upset of Taylor Fritz, then the world number nine, 7-6(5), 7-6(5), 6-7(9-11), 6-1. It was his first win over a top-ten opponent, and it came on clay, a surface he had once struggled on. He followed it into the second round before falling to fellow American Alex Michelsen. The performance reminded the tour of what it had seen in 2025, when Basavareddy climbed to a career-high ranking of world number 99 within six months of leaving college.

## The One Surface He Has Not Conquered

There is, however, a catch that makes Wimbledon a genuine question rather than a formality. Grass is the surface Basavareddy has barely touched as a professional. His career tour-level record on lawns is, remarkably, blank — zero wins, zero losses heading into this grass swing. He grew up on the hard courts of Irvine, California, and Carmel, Indiana; he found his footing on the clay of the European challenger circuit this spring, winning the Savannah Challenger title. But grass, with its low bounce, quick skid and premium on a heavy serve, is the part of the calendar he has had the least time to learn. His flat, early-struck backhand could suit the surface. His serve, by his own coaches' assessment, still lacks the firepower to win cheap points on fast lawns.

That is the drama of Roehampton for him: a player good enough to beat a top-ten name in Paris, walking into the one arena where his game is least tested, three wins away from a Wimbledon main-draw debut.

## From Nellore to Newport Beach

The diaspora resonance runs deeper than the surname. Basavareddy was born in Newport Beach, California, in May 2005, the son of Muralikrishna and Sai Prasanna Basavareddy, who emigrated from Nellore, in Andhra Pradesh, to the United States in 1999. His father worked at Toyota; the family lived in Irvine for eight years before moving to Carmel, Indiana, when Nishesh was eight. He and his older brother Nishanth, also a tennis player, grew up first-generation American but steeped in Telugu values their parents carried from home.

"My brother and I are first-generation kids, and we go by the values they have over there — humble, respectful, and hard-working," Basavareddy told the International Tennis Federation. "Both of my parents are really hardworking, and that has been instilled in me." He has spoken of returning to India as a child to visit grandparents in Hyderabad, Nellore and Puttaparthi, the family making the trip once every few years.

His path is the now-familiar diaspora story rendered on a tennis court. He attended Stanford, studied data science, was named Pac-12 Singles Player of the Year, won All-America honours, recovered from knee surgery, and turned professional in December 2024 after qualifying for the Next Gen ATP Finals. At the 2025 Australian Open, as a wildcard, he took a set off his idol Novak Djokovic in the first round — a moment that announced him to subcontinental fans who had watched, year after year, for an Indian-origin player to make a dent at the very top of the men's game.

## Why It Matters Beyond Roehampton

India has long agonised over its inability to produce a singles Grand Slam contender despite a population of 1.4 billion. Its tennis glory has come in doubles — Leander Paes, Mahesh Bhupathi, Sania Mirza, Rohan Bopanna. Basavareddy is not Indian; he is American, developed by the United States Tennis Association, coached on American courts. But for the diaspora that fills the outer courts of Flushing Meadows and Melbourne Park in saffron, white and green, an Indian-origin singles player ranked inside the top 150, beating top-ten names and chasing a Wimbledon berth, is the closest thing to a homegrown dream realised abroad.

If he comes through three rounds at Roehampton, Basavareddy will walk onto the grass of the All England Club for the first time as a main-draw player when Wimbledon begins on June 29. For families from Nellore to New Jersey, that walk would be worth staying up for."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image...")
img_caption = "Nishesh Basavareddy, the Indian-American seeded No. 26 in Wimbledon qualifying, in action in 2024"
img_attribution = "Wikimedia Commons"
img_final = None

cand = fetch_wikipedia_person_image("Nishesh Basavareddy")
if cand:
    img_final = upload_to_supabase(cand, f"{art_slug}.jpg")

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
        {"name": "Wikipedia \u2014 2026 Wimbledon Championships, Men's singles qualifying", "url": "https://en.wikipedia.org/wiki/2026_Wimbledon_Championships_%E2%80%93_Men%27s_singles_qualifying"},
        {"name": "Sporting News \u2014 Who is Nishesh Basavareddy? Meet the tennis star who upset Taylor Fritz at the French Open", "url": "https://www.sportingnews.com"},
        {"name": "Sportskeeda \u2014 Nishesh Basavareddy Deep Dive: parents, college career and current ranking", "url": "https://www.sportskeeda.com"},
        {"name": "ITF \u2014 Nishesh Basavareddy player profile", "url": "https://www.itftennis.com"},
        {"name": "ATP Tour \u2014 2026 grass-court season calendar", "url": "https://www.atptour.com"},
    ]),
    "diaspora_angle": "Basavareddy is a Telugu-heritage, Nellore-rooted Indian-American chasing a Wimbledon main-draw debut \u2014 the closest the subcontinent's diaspora has to a homegrown singles contender at a Grand Slam, even as the talent was developed entirely in the United States.",
    "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}

art_id = insert_article(art_data)

print("\n" + "="*60)
print("DONE")
print("="*60)
mark = "\u2713" if art_id else "\u2717"
print(f"Article: {mark} {art_slug}")
print(f"Word count: ~{len(art_body.split())} words")
print("Set to status='review'")
