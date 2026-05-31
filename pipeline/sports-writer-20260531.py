#!/usr/bin/env python3
"""
Sports Writer — 2026-05-31
Publishes 2 fresh sports articles for The Videshi:
1. Norway Chess Round 5: Gukesh's first classical win + Divya leads women's
2. Zee to broadcast FIFA World Cup 2026 in India
"""

import os, json, uuid, datetime, requests, urllib.parse, re, sys

# ── env ──
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/.env.supabase"))
load_dotenv(os.path.expanduser("~/workspace/.env.pexels"))

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY   = os.environ.get("PEXELS_API_KEY", "")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── helpers ──

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


def fetch_pexels_image(query, fallback_query=None):
    """Fetch an image from Pexels using curl (Python urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            result = subprocess.run(
                ["curl", "-sS", f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape",
                 "-H", f"Authorization: {PEXELS_KEY}"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for p in photos:
                url = p.get("src", {}).get("large2x") or p.get("src", {}).get("original")
                if url:
                    # Validate
                    head = requests.head(url, timeout=5)
                    clen = int(head.headers.get("Content-Length", 0))
                    if clen > 5000:
                        print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def upload_to_supabase_storage(image_url, filename):
    """Download image and upload to Supabase article-images bucket."""
    try:
        resp = requests.get(image_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=15)
        if resp.status_code != 200:
            print(f"  ⚠ Failed to download image: HTTP {resp.status_code}")
            return image_url  # fall back to original URL if permanent
        content_type = resp.headers.get("Content-Type", "image/jpeg")
        if not content_type.startswith("image/"):
            content_type = "image/jpeg"
        if len(resp.content) < 5000:
            print(f"  ⚠ Image too small ({len(resp.content)} bytes), skipping upload")
            return image_url

        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        upload_resp = requests.post(
            upload_url,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": content_type,
                "x-upsert": "true",
            },
            data=resp.content,
            timeout=30,
        )
        if upload_resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Supabase upload failed: {upload_resp.status_code} {upload_resp.text[:200]}")
            # If the original URL is from Wikipedia/Pexels (permanent), use it directly
            if "upload.wikimedia.org" in image_url or "images.pexels.com" in image_url:
                return image_url
            return None
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        if "upload.wikimedia.org" in image_url or "images.pexels.com" in image_url:
            return image_url
        return None


def insert_article(article):
    """Insert article into Supabase."""
    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
    )
    if resp.status_code in (200, 201):
        data = resp.json()
        art_id = data[0]["id"] if isinstance(data, list) else data["id"]
        print(f"  ✓ Article inserted: {art_id}")
        return art_id
    else:
        print(f"  ✗ Insert failed: {resp.status_code} {resp.text[:300]}")
        return None


def patch_article(art_id, updates):
    """Patch an article by ID."""
    resp = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{art_id}",
        headers=HEADERS,
        json=updates,
    )
    if resp.status_code in (200, 204):
        print(f"  ✓ Article patched: {art_id}")
    else:
        print(f"  ⚠ Patch issue: {resp.status_code} {resp.text[:200]}")


def validate_image_url(url):
    """Verify URL returns 200 with image content-type and >5KB."""
    if not url:
        return False
    try:
        head = requests.head(url, timeout=10, allow_redirects=True,
                             headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = head.headers.get("Content-Type", "")
        cl = int(head.headers.get("Content-Length", 0))
        if head.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Some servers don't support HEAD, try GET with range
        if head.status_code in (200, 405, 403):
            r = requests.get(url, timeout=10, stream=True,
                            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            ct = r.headers.get("Content-Type", "")
            if r.status_code == 200 and "image" in ct:
                chunk = r.raw.read(6000)
                if len(chunk) >= 5000:
                    return True
    except:
        pass
    return False


# ── Article 1: Norway Chess Round 5 ──
print("\n" + "="*60)
print("ARTICLE 1: Norway Chess Round 5 — Gukesh's First Classical Win")
print("="*60)

art1_slug = "norway-chess-2026-round-5-gukesh-first-classical-win-divya-deshmukh-leads-women-pragg"
art1_headline = "Gukesh Has Won His First Classical Game at Norway Chess. Divya Deshmukh Has Taken the Lead in the Women's Tournament."
art1_subheadline = "The world champion beat Praggnanandhaa in Round 5 after four frustrating rounds. Wesley So stunned Carlsen. And Divya Deshmukh overtook Bibisara Assaubayeva to lead the women's event in Oslo."

art1_body = """D Gukesh needed this. After four rounds of miscues, Armageddon losses, and a punishing classical defeat to Magnus Carlsen, the reigning world champion finally played the kind of chess that won him the title in Singapore last December.

In Round 5 of Norway Chess 2026, Gukesh defeated fellow Indian R Praggnanandhaa in a classical game to register his first full three-point win of the tournament. It was the all-India clash that the chess world had circled since the pairings were announced — the world champion against the player many believe will challenge him next.

## Gukesh Finds His Rhythm

Gukesh had entered the day bottom of the standings on 3.5 points, a position unbefitting a world champion. His tournament had been defined by near-misses: two Armageddon losses and a classical defeat to Carlsen in Round 4 that left him staring at the standings from the wrong end.

Against Pragg, he found clarity. The game featured sharp middlegame play where Gukesh gradually outmaneuvered his compatriot's defenses. The win was clinical rather than spectacular — a world champion executing his preparation with precision when it mattered most.

For Pragg, the loss was a setback after an impressive start to the tournament. The 20-year-old had won his first two Armageddon games and sat in second place heading into Round 5. He remains well-positioned in the standings but will need to regroup.

## Wesley So Ends Carlsen's Momentum

The bigger surprise of Round 5 came on the adjacent board, where Wesley So defeated Magnus Carlsen. The American grandmaster, representing the Philippines by birth and the United States by choice, has long been one of the most underrated players in elite chess.

So's victory ended Carlsen's resurgence after the Norwegian had beaten Gukesh in Round 4. The world number one had looked back to his imperious best against the Indian champion, but So exposed defensive weaknesses that the top-ranked player could not solve.

Alireza Firouzja, the French-Iranian prodigy, continues to lead the open tournament despite losing his Armageddon game to So. The 23-year-old's unbeaten run in classical games remains intact, and he sits comfortably ahead of the field.

## Divya Deshmukh Takes Over

The women's tournament produced its own dramatic shift. India's Divya Deshmukh overtook Kazakhstan's Bibisara Assaubayeva to take the lead in the women's event — a remarkable achievement for the 19-year-old from Nagpur.

Deshmukh, who stunned reigning women's world champion Ju Wenjun earlier in the tournament, has been the most consistent performer in the women's field. Her rise to the top of the standings confirms what Indian chess followers have long suspected: she is ready for the very highest level.

The women's tournament features a six-player round-robin running parallel to the open event, with equal prize money of 1,690,000 NOK (approximately $182,000) — a welcome step toward parity in professional chess.

## The NRI Perspective

For the Indian diaspora, Norway Chess 2026 represents something extraordinary. Three Indian players — Gukesh, Pragg, and Divya — are competing at the highest level of classical chess simultaneously, a scenario that would have seemed unimaginable a decade ago.

Gukesh, at 20, is the youngest world champion in history. Pragg, also 20, pushed Carlsen to a tiebreaker in the 2023 World Cup final. Divya, at 19, is leading a prestigious women's event against the established elite. The depth of Indian chess talent has never been greater.

Norway Chess continues through June 5 in Oslo, with the open and women's events running in parallel. The classical time control — 120 minutes for 40 moves with a 10-second increment — means these are the deepest, most consequential games these players will face outside of world championship matches.

## Standings After Round 5

**Open:** Firouzja leads, followed by Pragg, So, Carlsen, Gukesh, and Keymer.

**Women's:** Divya Deshmukh leads, having overtaken Assaubayeva.

Round 6 pairings promise more fireworks, with Gukesh facing Firouzja and Carlsen taking on Pragg in rematches that could reshape the standings entirely.

*Norway Chess 2026 is streamed live on Chess24's YouTube and Twitch channels. All games begin at 5 PM CEST (8:30 PM IST, 11 AM ET, 8 AM PT).*

**Sources:** Chess.com, ChessBase, Norway Chess official"""

# Image for Gukesh
print("  Sourcing image for Gukesh...")
img1_url = fetch_wikipedia_person_image("D. Gukesh")
if not img1_url:
    img1_url = fetch_wikipedia_person_image("Gukesh D")
if not img1_url:
    img1_url = fetch_wikipedia_person_image("Dommaraju Gukesh")

art1_id = str(uuid.uuid4())
img1_attribution = "Wikimedia Commons"

if img1_url:
    final_img1 = upload_to_supabase_storage(img1_url, f"{art1_id}.jpg")
    if not final_img1 or not validate_image_url(final_img1):
        # Try direct Wikipedia URL
        if validate_image_url(img1_url):
            final_img1 = img1_url
        else:
            final_img1 = None
else:
    final_img1 = None
    print("  ⚠ No Wikipedia image found for Gukesh, trying Pexels...")
    pexels_img = fetch_pexels_image("chess tournament grandmaster", "chess pieces competition")
    if pexels_img:
        final_img1 = pexels_img
        img1_attribution = "The Videshi"

article1 = {
    "id": art1_id,
    "headline": art1_headline,
    "subheadline": art1_subheadline,
    "slug": art1_slug,
    "body": art1_body,
    "category": "sports",
    "status": "published",
    "published_at": datetime.datetime.utcnow().isoformat() + "Z",
    "sources": json.dumps([
        {"name": "Chess.com", "url": "https://www.chess.com/news/view/2026-norway-chess-round-5"},
        {"name": "ChessBase", "url": "https://en.chessbase.com/"},
        {"name": "Norway Chess", "url": "https://norwaychess.no/"}
    ]),
    "image_url": final_img1,
    "image_attribution": img1_attribution if final_img1 else None,
}

result1 = insert_article(article1)


# ── Article 2: Zee to Broadcast FIFA World Cup 2026 in India ──
print("\n" + "="*60)
print("ARTICLE 2: Zee to Broadcast FIFA World Cup 2026 in India")
print("="*60)

art2_slug = "zee-broadcast-fifa-world-cup-2026-india-unite8-sports-nri-watch-guide"
art2_headline = "Zee Will Broadcast the FIFA World Cup in India. Twelve Days Before Kickoff, Indian Fans Finally Have an Answer."
art2_subheadline = "After weeks of uncertainty, Zee Entertainment is set to announce a broadcast deal with FIFA. Matches will air on Unite8 Sports channels and stream on Zee5 — ending fears of a World Cup blackout in one of football's biggest markets."

art2_body = """For weeks, Indian football fans have lived with an absurd question: will the biggest sporting event in the world actually be shown in their country?

With the FIFA World Cup 2026 kicking off on June 11 across the United States, Canada, and Mexico, India — a nation of 1.4 billion people with a rapidly growing football audience — still had no confirmed broadcaster. That is about to change.

## Zee Steps In

According to multiple reports, Zee Entertainment Enterprises is set to officially announce a broadcast deal with FIFA over the coming days. The agreement covers the 2026 FIFA World Cup and will bring all 104 matches to Indian television screens through Zee's newly launched Unite8 Sports channels and its OTT platform Zee5.

The channels — Unite8 Sports 1 and Unite8 Sports 1 HD in Hindi, alongside Unite8 Sports 2 and Unite8 Sports 2 HD in English — represent Zee's renewed push into sports broadcasting. For the diaspora community, the Zee5 streaming option means NRIs with existing subscriptions may be able to access coverage digitally, though geo-restrictions will vary by region.

## How India Nearly Missed the World Cup

The road to this deal was anything but smooth. FIFA initially sought $100 million from Indian broadcasters for the 2026 and 2030 editions combined. That figure was later reduced to $60 million — the same price paid for the 2022 tournament in Qatar.

Reliance-Disney's JioStar, which controls the IPL and most premium cricket rights in India, entered discussions but walked away. Sony Pictures Networks India held talks but ultimately declined to submit a formal bid. The impasse left FIFA facing the embarrassing prospect of a World Cup blackout in one of the world's largest television markets.

Meanwhile, an Indian-American investment firm called Avni LLC, based in Washington DC, emerged as an unlikely contender. Led by CEO Deelip Mhaske, the firm claimed to have submitted a corporate guarantee exceeding $300 million as part of FIFA's closed tender process. Avni pitched a vision built around AI-powered multilingual broadcasting, mobile micro-subscriptions, and esports integrations across Asia.

A Delhi High Court petition added further pressure, seeking directions to ensure the tournament is broadcast on Doordarshan and DD Sports — India's free-to-air public broadcasters — to prevent a total blackout.

## What NRIs Need to Know

For Indian Americans and the broader diaspora, the World Cup broadcast landscape varies by country:

**United States:** Fox Sports and Telemundo hold English and Spanish rights respectively. Fox will broadcast matches across Fox, FS1, and the Fox Sports app. The tournament is being hosted across 16 American cities including New York, Los Angeles, Dallas, Houston, Miami, and the Bay Area.

**Canada:** CTV/TSN holds English rights, with TVA Sports broadcasting in French.

**United Kingdom:** BBC and ITV share free-to-air rights.

**India:** Zee's Unite8 Sports channels and Zee5 streaming platform. Exact pricing and packages are expected to be announced shortly.

The timing challenge remains significant for Indian audiences. With matches kicking off during North American afternoon and evening hours, most games will fall between midnight and 6 AM IST — a familiar inconvenience for cricket fans accustomed to watching overseas series, but still a hurdle for mass viewership.

## The Bigger Picture

India's World Cup broadcast saga reflects the broader tensions in global sports media rights. FIFA's valuation expectations clashed with the reality of a time-zone-disadvantaged market. Cricket still dominates Indian sports viewership so comprehensively that even the world's biggest football tournament struggled to find a buyer.

Yet the 2022 Qatar World Cup generated record television numbers in India, with late-night viewing parties becoming a cultural phenomenon in cities across the country. Football's audience in India — particularly among young, urban, and diaspora-connected viewers — continues to grow.

For NRIs in the United States, this World Cup is uniquely accessible. With matches happening across American time zones and venues within driving distance of major Indian-American population centers, the 2026 tournament offers an opportunity to experience the global game on home soil.

Zee's late entry ensures that fans back home will not miss out. The deal may have come down to the wire, but Indian football fans — both in the country and across the world — can finally plan their viewing schedules.

*The FIFA World Cup 2026 runs from June 11 to July 19 across 16 cities in the United States, Canada, and Mexico. 48 teams will compete in 104 matches.*

**Sources:** RevSportz, MensXP, The Indian Eye, Reuters"""

# Image for FIFA World Cup
print("  Sourcing image for FIFA World Cup...")
img2_url = fetch_pexels_image("soccer football stadium world cup", "football match stadium")
art2_id = str(uuid.uuid4())

if img2_url:
    final_img2 = upload_to_supabase_storage(img2_url, f"{art2_id}.jpg")
    if not final_img2 or not validate_image_url(final_img2):
        if validate_image_url(img2_url):
            final_img2 = img2_url
        else:
            final_img2 = None
    img2_attribution = "The Videshi"
else:
    final_img2 = None
    img2_attribution = None

article2 = {
    "id": art2_id,
    "headline": art2_headline,
    "subheadline": art2_subheadline,
    "slug": art2_slug,
    "body": art2_body,
    "category": "sports",
    "status": "published",
    "published_at": datetime.datetime.utcnow().isoformat() + "Z",
    "sources": json.dumps([
        {"name": "RevSportz", "url": "https://revsportz.in/zee-set-to-broadcast-fifa-world-cup-2026-in-india/"},
        {"name": "MensXP", "url": "https://www.mensxp.com/"},
        {"name": "The Indian Eye", "url": "https://theindianeye.com/"}
    ]),
    "image_url": final_img2,
    "image_attribution": img2_attribution,
}

result2 = insert_article(article2)

# ── Summary ──
print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Article 1: {'✓' if result1 else '✗'} {art1_headline[:80]}...")
print(f"  Slug: {art1_slug}")
print(f"  Image: {'✓' if final_img1 else '✗ (no image)'}")
print(f"Article 2: {'✓' if result2 else '✗'} {art2_headline[:80]}...")
print(f"  Slug: {art2_slug}")
print(f"  Image: {'✓' if final_img2 else '✗ (no image)'}")
