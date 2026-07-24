#!/usr/bin/env python3
"""
Sports Writer — June 18, 2026 (10:30 UTC run)
Article: Major League Cricket 2026 launches tonight in Grand Prairie, Texas.
The fourth MLC season (June 18 – July 18) is the most ambitious yet: six
franchises, three venues, the Oakland Coliseum hosting the final for the first
time, and squads stacked with global stars (Smith, Maxwell, du Plessis, Pooran,
Russell, Narine) alongside a deepening core of American-raised, mostly
Indian-origin domestic players — Monank Patel, Saurabh Netravalkar, Nitish
Kumar, Saiteja Mukkamalla, Rushil Ugarkar.
Diaspora angle: MLC is the diaspora's own league — built by Indian-American
money, played in American suburbs with the largest desi populations, and
increasingly powered by US-raised desi kids. Tonight it begins again.
Distinct from recent sports coverage (cricket ODIs vs Afghanistan, women's
T20 WC, India A tri-series, chess, tennis juniors, golf, hockey, football).
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


def fetch_wikimedia_commons_images(search_query, limit=6):
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
print("ARTICLE: MLC 2026 launches — the diaspora's own league")
print("="*60)

art_slug = "major-league-cricket-2026-season-opens-grand-prairie-diaspora-monank-patel-netravalkar-american-cricket"
art_headline = "America's Cricket League Begins Its Fourth Season Tonight. It Was Built in the Suburbs the Diaspora Calls Home."
art_subheadline = "Major League Cricket returns June 18 with Steve Smith, Glenn Maxwell and Faf du Plessis on the marquee — but the league's real project is the American-raised, largely Indian-origin core now sharing a dressing room with them. From Grand Prairie to a sold-out Oakland Coliseum final, this is the diaspora's home team."

art_body = """GRAND PRAIRIE, Texas \u2014 On Thursday night, under the lights of a 7,200-seat stadium wedged between Dallas and Fort Worth, the Texas Super Kings will face the Seattle Orcas to open the fourth season of Major League Cricket. For most of America, it will pass unnoticed. For the millions of Indians, Pakistanis, Sri Lankans and Bangladeshis who have made the United States home, it is something closer to an annual homecoming \u2014 a month in which the sport of their childhoods is played, at a professional standard, in the very suburbs where they now live.

MLC 2026 runs from June 18 to July 18, a 34-match tournament across three venues, culminating for the first time in a championship final at the Oakland Coliseum, the former home of baseball's Athletics. It is the most ambitious edition yet of a league that did not exist five years ago, and which has quietly become one of the more improbable success stories in American sport.

## A League Built by, and for, the Diaspora

Major League Cricket was not willed into being by a broadcaster or a legacy governing body. It was built by American Cricket Enterprises, a venture backed substantially by Indian-American technology money, and several of its franchises are extensions of Indian Premier League empires. MI New York is the New York arm of the Mumbai Indians; the Los Angeles Knight Riders share their DNA with the Kolkata Knight Riders; the Texas Super Kings are cousins of Chennai. The investor base reads like a who's who of Silicon Valley's South Asian elite.

The geography is no accident either. The league's homes \u2014 the Dallas-Fort Worth metroplex, the San Francisco Bay Area, and now Pomona in greater Los Angeles \u2014 map almost exactly onto the densest concentrations of the Indian diaspora in the country. Season three set records for ticket sales, up 53 percent year-on-year, with a striking 84 percent of buyers attending an MLC game for the first time. This is a sport finding its audience precisely where that audience already lives.

## The Stars, and the Point Behind Them

The marquee names are doing their job. Steve Smith captains the Washington Freedom under coach Ricky Ponting; Glenn Maxwell and Rachin Ravindra are alongside him. Faf du Plessis leads the Texas Super Kings, Nicholas Pooran the defending champion MI New York, with Kieron Pollard, Sunil Narine, Andre Russell and Trent Boult scattered across the rosters. For a league still establishing itself, the quality of imported talent is remarkable.

But the foreign stars, capped at six per team, are the spectacle, not the strategy. The longer game is the development of American domestic players \u2014 and here the story turns unmistakably desi. The United States captain Monank Patel, a Gujarat-born wicketkeeper who once waited tables in New Jersey before cricket became a living, holds the record for the highest individual score by an American in MLC history. Saurabh Netravalkar, the left-arm seamer who balances international cricket with a software engineering career in the Bay Area, is among the league's most recognizable homegrown names. Around them sit a growing cohort \u2014 Nitish Kumar, Saiteja Mukkamalla, Rushil Ugarkar, Saideep Ganesh \u2014 many of them children of immigrants who grew up playing weekend cricket in American parks.

## Cricket as an American Immigrant Story

That last detail is the one that matters most for families watching from Edison or Fremont or Plano. For a generation of diaspora parents, cricket has been an act of cultural preservation \u2014 something taught in backyards and community leagues to children who would otherwise be raised entirely on baseball and football. MLC is the first credible promise that the preservation could become a profession; that a desi kid in Texas might one day be paid to play the game their grandparents loved, in a stadium their neighbors can drive to.

The infrastructure is following the ambition. The new Knight Riders Cricket Field at the Fairplex in Pomona joins purpose-built grounds in Grand Prairie, signaling that the league intends to own its venues rather than rent them. The decision to stage the final at the Oakland Coliseum \u2014 a venue that has hosted World Series baseball \u2014 is a statement of intent dressed as a fixture.

## What to Watch

MI New York begin as defending champions, having edged Washington Freedom by five runs in last year's final, and the rivalry between the two best-funded franchises is likely to define the season again. The Super Kings and Knight Riders, perennial nearly-men, have recruited aggressively. And the subplot worth tracking is whether the domestic players continue their upward curve; Patel argued last season that American talent had grown strong enough to justify cutting the foreign quota \u2014 a sign of a league maturing faster than its skeptics predicted.

For one month, beginning tonight, the diaspora gets to watch its sport played at home, by some of the world's best and by a few of its own. In the suburbs where the desi story in America has largely been written, that is its own kind of arrival."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image...")
img_caption = "Major League Cricket action at Grand Prairie Stadium, Texas, home of the Texas Super Kings"
img_attribution = "Wikimedia Commons"
img_final = None

# Try Wikimedia Commons for MLC / stadium / USA cricket imagery first (this is an event/league story)
commons_queries = [
    "Grand Prairie Stadium cricket",
    "Major League Cricket",
    "Oakland Coliseum cricket",
    "Monank Patel cricket",
    "USA cricket team",
]
for q in commons_queries:
    cands = fetch_wikimedia_commons_images(q)
    for c in cands:
        print(f"   candidate: {c['title']} ({c['w']}x{c['h']})")
        # skip obvious logos / non-photo svgs by title
        low = c["title"].lower()
        if "logo" in low or ".svg" in low or "map" in low:
            continue
        got = upload_to_supabase(c["url"], f"{art_slug}.jpg")
        if got:
            img_final = got
            if "grand prairie" in low or "stadium" in low:
                img_caption = "Grand Prairie Stadium in Texas, a purpose-built home of Major League Cricket"
            elif "oakland" in low:
                img_caption = "The Oakland Coliseum, which will host the MLC 2026 final"
            elif "monank" in low or "usa" in low:
                img_caption = "USA captain Monank Patel, the highest individual scorer by an American in MLC history"
            break
    if img_final:
        break

# Fallback: Wikipedia person photo for Monank Patel (central American figure)
if not img_final:
    for name in ["Monank Patel", "Saurabh Netravalkar", "Steve Smith (cricketer)"]:
        cand = fetch_wikipedia_person_image(name)
        if cand:
            if "Monank" in name:
                img_caption = "USA captain Monank Patel, the highest individual scorer by an American in MLC history"
            elif "Netravalkar" in name:
                img_caption = "Saurabh Netravalkar, the Bay Area software engineer and USA international seamer"
            else:
                img_caption = "Steve Smith, captain of the Washington Freedom in Major League Cricket 2026"
            img_final = upload_to_supabase(cand, f"{art_slug}.jpg")
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
    "vertical": "diaspora-sport",
    "status": "review",
    "is_editorial": False,
    "image_url": img_final or "",
    "image_caption": img_caption,
    "image_attribution": img_attribution,
    "sources": json.dumps([
        {"name": "Wikipedia \u2014 2026 Major League Cricket season", "url": "https://en.wikipedia.org/wiki/2026_Major_League_Cricket_season"},
        {"name": "Wisden \u2014 MLC 2026 Schedule: Full Fixtures List, Match Timings And Venues", "url": "https://www.wisden.com/"},
        {"name": "Athlon Sports \u2014 MLC 2025: Monank Patel Guides MI New York to First Win", "url": "https://athlonsports.com/"},
        {"name": "Cricbuzz \u2014 Monank Patel on MLC domestic players", "url": "https://www.cricbuzz.com/"},
    ]),
    "diaspora_angle": "Major League Cricket is the diaspora's own professional league \u2014 funded largely by Indian-American capital, staged in the U.S. suburbs with the densest South Asian populations, and increasingly powered by American-raised, mostly Indian-origin players like Monank Patel and Saurabh Netravalkar, turning a game of cultural preservation into a credible profession for immigrant kids.",
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
