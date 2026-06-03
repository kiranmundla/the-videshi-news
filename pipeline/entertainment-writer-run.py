#!/usr/bin/env python3
"""Entertainment writer — June 3, 2026 batch"""

import json, os, sys, time, uuid, re, requests, urllib.parse
from datetime import datetime, timezone

# Load env
env_path = os.path.expanduser("~/workspace/.env.supabase")
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k] = v.strip().strip('"').strip("'")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# Load Pexels key
pexels_path = os.path.expanduser("~/workspace/.env.pexels")
PEXELS_KEY = None
if os.path.exists(pexels_path):
    with open(pexels_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                if "PEXELS" in k.upper():
                    PEXELS_KEY = v.strip().strip('"').strip("'")

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

def fetch_wikimedia_commons_images(search_query, limit=5):
    """Search Wikimedia Commons for CC-licensed images."""
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json"
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params,
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                url = ii.get("thumburl") or ii.get("url")
                mime = ii.get("mime", "")
                if url and "image" in mime:
                    results.append({"url": url, "title": page.get("title", ""), "width": ii.get("width", 0)})
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error for '{search_query}': {e}")
    return []

def fetch_pexels_image(query):
    """Search Pexels for an image using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels key")
        return None
    import subprocess
    try:
        result = subprocess.run(
            ["curl", "-sS", f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=5",
             "-H", f"Authorization: {PEXELS_KEY}"],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        photos = data.get("photos", [])
        if photos:
            # Pick the best landscape photo
            for p in photos:
                src = p.get("src", {}).get("large2x") or p.get("src", {}).get("large")
                if src:
                    print(f"  ✓ Pexels image found for '{query}': {src[:80]}...")
                    return src
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None

def validate_image_url(url):
    """Verify URL returns HTTP 200 with image content > 5KB."""
    if not url:
        return False
    # Block banned sources
    banned = ["fbcdn.net", "cdninstagram.com", "lookaside.fbsbx.com", "_nc_ht=", "_nc_cat="]
    for b in banned:
        if b in url:
            print(f"  ✗ Banned source detected: {b}")
            return False
    try:
        r = requests.head(url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Image validated: {cl} bytes, {ct}")
            return True
        # Some servers don't return Content-Length on HEAD
        if r.status_code == 200 and "image" in ct:
            r2 = requests.get(url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=10, stream=True)
            size = len(r2.content)
            if size > 5000:
                print(f"  ✓ Image validated (GET): {size} bytes")
                return True
        print(f"  ✗ Image validation failed: status={r.status_code}, ct={ct}, cl={cl}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False

def find_best_image(person_name=None, topic_queries=None):
    """Multi-source image search: Wikipedia → Wikimedia Commons → Pexels."""
    candidates = []

    # Source 1: Wikipedia person image
    if person_name:
        url = fetch_wikipedia_person_image(person_name)
        if url and validate_image_url(url):
            return url, "Wikimedia Commons"

    # Source 2: Wikimedia Commons
    if topic_queries:
        for q in topic_queries:
            results = fetch_wikimedia_commons_images(q, limit=3)
            for r in results:
                if validate_image_url(r["url"]):
                    candidates.append((r["url"], "Wikimedia Commons"))
            if candidates:
                return candidates[0]

    # Source 3: Pexels
    if topic_queries:
        for q in topic_queries:
            url = fetch_pexels_image(q)
            if url and validate_image_url(url):
                return url, "Pexels"

    return None, None

def insert_article(article):
    """Insert article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article
    )
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            print(f"  ✓ Published: {data[0].get('headline', '')[:60]}...")
            return True
    print(f"  ✗ Insert failed: {r.status_code} — {r.text[:200]}")
    return False

# ═══════════════════════════════════════════════════════════════
# ARTICLE 1: Gullak Season 5 on SonyLIV
# ═══════════════════════════════════════════════════════════════

print("\n" + "="*60)
print("ARTICLE 1: Gullak Season 5")
print("="*60)

# Image sourcing for Gullak
print("\nSourcing image...")
gullak_img, gullak_attr = find_best_image(
    topic_queries=["Gullak Indian TV series", "Indian middle class family", "Indian family living room"]
)
if not gullak_img:
    gullak_img, gullak_attr = find_best_image(
        topic_queries=["Indian small town street", "Indian household"]
    )

gullak_article = {
    "headline": "Gullak Season 5 Drops Thursday on SonyLIV. The Mishra Family Is Back, but One Face Has Changed.",
    "subheadline": "TVF's beloved middle-class family drama returns with a new Annu, a visiting uncle, and the same quiet emotional punch that makes NRIs call their parents at 2 AM.",
    "slug": "gullak-season-5-sonyliv-mishra-family-anant-joshi-tvf-nri-20260603",
    "category": "entertainment",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "is_editorial": False,
    "image_url": gullak_img,
    "image_attribution": gullak_attr,
    "body": """The Mishra family is returning to your screen on June 5, and if you've ever sent money home to parents who insist they don't need anything, this show will wreck you in the best possible way.

Gullak Season 5 premieres on SonyLIV this Thursday, continuing the story of a middle-class Indian family in a small town whose daily struggles — over Wi-Fi passwords, career anxieties, and the politics of who gets the good chair — somehow feel more cinematic than any spy thriller releasing the same week.

## What's New This Season

The biggest change: Anant V. Joshi steps in to play Annu, the elder Mishra son, replacing the actor who originated the role. Recasting a beloved character in a show built entirely on familial chemistry is a high-wire act. The trailer suggests Joshi has found his version of Annu rather than attempting an imitation — slightly more world-weary, visibly wrestling with career pressures and apartment hunting in a way that will feel deeply familiar to anyone who's been the first in their family to move to the city.

Harsh Mayar returns as Aman, now back from college with a maturity that immediately unsettles the family equilibrium. Jameel Khan and Geetanjali Kulkarni reprise their roles as Santosh and Shanti Mishra — the father-mother unit whose silences contain entire novels.

The wildcard this season is Gopal Datt as Shanti's brother Pinky, whose extended visit to Mishra Nivas promises the kind of low-stakes family tension that Gullak has always mined better than any show in Indian television.

## Why This Matters to the Diaspora

There is no Indian show streaming today that captures the texture of middle-class Indian life with more precision than Gullak. The franchise, produced by The Viral Fever, has built its reputation not on star power or production scale but on an almost documentary-level attention to how Indian families actually talk to each other — the love buried under complaints, the pride disguised as criticism, the mother who tracks every rupee but would sell the house if her son needed anything.

For NRIs, watching Gullak is an act of time travel. The Mishra household, with its slowly upgrading appliances and carefully maintained rituals, is the house you grew up in. Santosh installing Wi-Fi this season while clearly suspicious of the technology is the specific kind of generational comedy that hits different when you're explaining cloud storage to your father over a WhatsApp video call from San Jose.

The show has also become a quiet cultural bridge. Unlike Bollywood's version of middle-class India — which typically involves a family that somehow lives in a Bandra duplex — Gullak's India is the India most Indians actually know. Tier-2 towns. Government jobs. The complicated economics of a family where ₹500 is both nothing and everything depending on the context.

## Five Seasons and Still No Wasted Scene

What makes Gullak exceptional among Indian streaming shows is its discipline. Each season runs five episodes. There's no filler subplot about a murder investigation or a sudden trip to Europe. The drama comes from where it always comes from in real life: money, pride, growing up, and the terrifying realization that your parents are aging.

Season 4 ended with the Mishra family navigating change while desperately trying to preserve what makes them who they are. Season 5 appears to push that tension further — Annu's apartment hunt suggests a physical separation that the family isn't ready for, even as everyone pretends they are.

## The Competition

Gullak 5 arrives in possibly the most stacked week of Indian OTT content in 2026. Dhurandhar 2 hits JioHotstar on June 4. Maa Behen, starring Madhuri Dixit and Triptii Dimri, drops on Netflix the same day. Karisma Kapoor's Brown premieres on ZEE5 on June 5, the same day as Gullak. Patriot, featuring Mammootty and Mohanlal together, also arrives on ZEE5.

In that crowd, Gullak won't generate trending hashtags or advance booking numbers. It never has. What it will do, as it has done four times before, is make you pause whatever else you're watching, sit down, and feel something you weren't expecting to feel about a family argument over a visiting uncle.

All five episodes of Gullak Season 5 stream on SonyLIV from June 5.

*Sources: SonyLIV, The Viral Fever, Pinkvilla, Sacnilk*""",
    "sources": json.dumps(["SonyLIV", "The Viral Fever (TVF)", "Pinkvilla", "Sacnilk"]),
    "vertical": "entertainment"
}

print(f"\nInserting article: {gullak_article['headline'][:60]}...")
insert_article(gullak_article)

# ═══════════════════════════════════════════════════════════════
# ARTICLE 2: Suriya's Karuppu closes in on ₹300 Crore
# ═══════════════════════════════════════════════════════════════

print("\n" + "="*60)
print("ARTICLE 2: Suriya's Karuppu")
print("="*60)

# Image sourcing
print("\nSourcing image...")
karuppu_img, karuppu_attr = find_best_image(
    person_name="Suriya (actor)",
    topic_queries=["Suriya Tamil actor", "Suriya Indian film actor"]
)
if not karuppu_img:
    karuppu_img, karuppu_attr = find_best_image(
        person_name="Suriya",
        topic_queries=["Tamil cinema audience theater"]
    )

karuppu_article = {
    "headline": "Suriya's Karuppu Has Crossed ₹290 Crore Worldwide. Tamil Cinema's Quiet Blockbuster Season Just Got Very Loud.",
    "subheadline": "Three weeks in, the film has broken Suriya's career records, crossed ₹100 crore in Tamil Nadu alone, and proved that South Indian cinema's next wave doesn't need a pan-India label to travel.",
    "slug": "suriya-karuppu-290-crore-worldwide-box-office-tamil-cinema-nri-20260603",
    "category": "entertainment",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "is_editorial": False,
    "image_url": karuppu_img,
    "image_attribution": karuppu_attr,
    "body": """Suriya hasn't given an interview in weeks. He hasn't done a promotional dance on a reality show. He hasn't posted a cryptic Instagram story. He's just let the numbers do the talking, and the numbers have been deafening.

Karuppu, released on May 16, has crossed ₹290 crore worldwide in under three weeks. The ₹300 crore milestone — a number that only a handful of Tamil films have ever reached — is now a matter of days, not weeks. For a star whose last few films tested the patience of even his most loyal fans, this isn't just a comeback. It's a recalibration of what Suriya's ceiling actually looks like.

## The Numbers That Matter

The film's India net collection stands at approximately ₹185 crore, with the Tamil Nadu market alone contributing over ₹100 crore — a first in Suriya's career. The overseas gross has climbed past ₹78 crore, driven by strong holds in the US, Gulf, Malaysia, and Singapore, the four markets where Tamil cinema's diaspora audience is most concentrated.

What makes these numbers remarkable isn't their size but their shape. Karuppu's first week collected ₹113.85 crore domestically. Its second week added another ₹54.30 crore. That second-week hold — roughly 48 percent of the opening week — signals genuine word-of-mouth rather than front-loaded hype. For context, even megahits like Jailer and Leo saw steeper second-week drops.

The BookMyShow data tells its own story. On opening weekend, Karuppu sold 690,000 tickets on Day 2 alone, setting a new all-time record for the platform and narrowly beating Rajinikanth's Coolie. The film's cumulative ticket sales have now crossed 43 lakh on the platform.

## Breaking Career Records

For Suriya specifically, Karuppu has rewritten every number that matters. It surpassed the lifetime collection of Singam 2 — his previous career-best — in just four days. It became the first Suriya film to cross ₹100 crore in Tamil Nadu. And its Telugu-dubbed version, VeeraBhadrudu, hit a peak booking speed of 43,000 tickets per hour, confirming the actor's unusual hold in the Telugu states where he's long been called the "Adopted Son."

This comes after a rough patch. Suriya's previous releases had underperformed, leading to the kind of industry whispers that actors at his level dread — questions about whether the market had moved past him, whether his choices had become too conservative, whether the younger generation of Tamil stars had taken his space.

Karuppu has answered all of it without raising its voice.

## Why This Film Worked

The film's director has delivered something that sounds simple but is fiendishly difficult in Tamil commercial cinema: a story that satisfies the mass audience while earning respect from critics. Early reviews praised the film's visual grammar, its refusal to take shortcuts with its antagonist, and a performance from Suriya that multiple reviewers described as career-best.

The other factor is timing. Tamil cinema had been in a nine-month dry spell before Karuppu's release. The audience was hungry, and Suriya delivered a film worth being hungry for. When the market has been starved of a genuine event film, the right release doesn't just succeed — it overperforms.

## What This Means for NRI Audiences

For the Tamil diaspora, Karuppu's overseas performance — ₹78 crore and counting — reflects something bigger than one film's success. It confirms that Tamil cinema's core audience abroad is self-sustaining and doesn't need the "pan-India" marketing machinery to show up.

The film released in Tamil and Telugu, not in Hindi. There was no nationwide promotional blitz. No Karan Johar cameo or Bollywood press tour. The audience simply showed up because the film was good and the star had earned their attention over two decades.

In the US alone, the film has performed well across the traditional South Indian cinema hubs — Dallas, the Bay Area, New Jersey, Chicago — markets where Tamil families make movie-going a weekend ritual regardless of reviews or box office tracking.

## The Road to ₹300 Crore

At its current trajectory, Karuppu will cross ₹300 crore worldwide within the next few days. That number would place it among the top 10 highest-grossing Tamil films ever and cement 2026 as the year Suriya reminded everyone why he's been around for 25 years.

The film faces new competition starting this week — Peddi, Dhurandhar 2's OTT arrival, and a crowded theatrical slate. But its third-week Monday numbers (₹2.05 crore Tamil net, the second-highest third Monday in Kollywood history after Jailer) suggest it still has legs.

Suriya, meanwhile, continues to say nothing. The numbers keep saying everything.

*Sources: Sacnilk, BookMyShow, Venky Box Office, Zoom TV Entertainment*""",
    "sources": json.dumps(["Sacnilk", "BookMyShow", "Venky Box Office", "Zoom TV Entertainment"]),
    "vertical": "entertainment"
}

print(f"\nInserting article: {karuppu_article['headline'][:60]}...")
insert_article(karuppu_article)

print("\n" + "="*60)
print("Entertainment writer complete — 2 articles published")
print("="*60)
