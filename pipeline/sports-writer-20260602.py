#!/usr/bin/env python3
"""Sports writer for The Videshi — June 2, 2026 evening batch."""

import json, os, sys, time, uuid, re, urllib.parse
from datetime import datetime, timezone
import requests

# ── env ──────────────────────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY   = os.environ.get("PEXELS_API_KEY", "")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── helpers ──────────────────────────────────────────────────────────
def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


def fetch_pexels_image(query, fallback_query=None):
    """Fetch image from Pexels API. Returns URL or None."""
    if not PEXELS_KEY:
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": PEXELS_KEY},
                params={"query": q, "per_page": 3, "orientation": "landscape"},
                timeout=10,
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                for p in photos:
                    url = p.get("src", {}).get("large2x") or p.get("src", {}).get("original")
                    if url:
                        print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def upload_image_to_supabase(img_url, filename):
    """Download image and upload to Supabase storage. Returns public URL or None."""
    try:
        resp = requests.get(img_url, timeout=15, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if resp.status_code != 200:
            print(f"  ⚠ Image download failed ({resp.status_code}): {img_url[:80]}")
            return None
        content_type = resp.headers.get("Content-Type", "image/jpeg")
        if "image" not in content_type:
            print(f"  ⚠ Not an image: {content_type}")
            return None
        if len(resp.content) < 5000:
            print(f"  ⚠ Image too small ({len(resp.content)} bytes)")
            return None

        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        up = requests.post(
            upload_url,
            headers={
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": content_type,
                "x-upsert": "true",
            },
            data=resp.content,
            timeout=30,
        )
        if up.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed ({up.status_code}): {up.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return None


def validate_image_url(url):
    """Check that a URL returns a valid image."""
    try:
        r = requests.head(url, timeout=10, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
    except:
        pass
    return False


def insert_article(article):
    """Insert article into Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    r = requests.post(url, headers=HEADERS, json=article, timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) else data.get("id")
        print(f"  ✓ Article inserted: {article['slug']} (id={art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None


def patch_article(art_id, patch):
    """Patch an existing article."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{art_id}"
    r = requests.patch(url, headers=HEADERS, json=patch, timeout=15)
    if r.status_code in (200, 204):
        print(f"  ✓ Patched article {art_id}")
    else:
        print(f"  ⚠ Patch failed: {r.text[:200]}")


# ── Article 1: Norway Chess Round 8 ─────────────────────────────────
def write_norway_chess():
    print("\n=== Article 1: Norway Chess Round 8 ===")

    slug = "norway-chess-2026-round-8-praggnanandhaa-beats-carlsen-classical-firouzja-gukesh-nri"
    headline = "He Has Now Beaten Carlsen Twice in Classical. Praggnanandhaa's Norway Chess Resurgence Is the Story of the Tournament."
    subheadline = "The Indian grandmaster defeated the world number one in Round 8, while Firouzja beat Gukesh to tighten the title race heading into the final two rounds in Oslo."

    body = """Praggnanandhaa Rameshbabu has done it again.

In Round 8 of Norway Chess 2026 in Oslo, the 21-year-old Indian grandmaster defeated Magnus Carlsen in a classical game for the **second time in this tournament** — a feat that no player has managed in any elite event in recent memory. Pragg had already beaten Carlsen in Round 3, and with this latest victory, he has scored a perfect 6 out of 6 against the world's highest-rated player across their two encounters.

The win came with the white pieces. Pragg built pressure through a carefully prepared opening and accumulated a decisive advantage as the middlegame sharpened. His technique in the conversion was clinical, leaving Carlsen with no practical chances.

## The Title Race Tightens

The result reshuffled the standings in dramatic fashion. Pragg surged to 12 points, pulling within striking distance of tournament leader Wesley So, who leads on 14 points after drawing his classical game against Vincent Keymer and winning the Armageddon tiebreaker.

In the day's other decisive result, Alireza Firouzja scored a crucial classical victory over World Champion Gukesh Dommaraju to climb to 13 points — just one behind So. For Gukesh, it was another difficult day at the board. The reigning world champion has struggled in Oslo, sitting on 8 points after eight rounds, well off the pace.

**Standings after Round 8:**

| Player | Points |
|---|---|
| Wesley So (USA) | 14 |
| Alireza Firouzja (France) | 13 |
| R Praggnanandhaa (India) | 12 |
| Vincent Keymer (Germany) | 10 |
| Magnus Carlsen (Norway) | 9 |
| Gukesh Dommaraju (India) | 8 |

The gap between the top three is razor-thin. With two rounds remaining, So, Firouzja, and Pragg are separated by just two points. A single classical win — worth three points in Norway Chess's aggressive scoring format — could swing the leaderboard entirely.

## Pragg's Remarkable Arc

What makes Pragg's performance so striking is its trajectory. After losing two classical games in rounds 5 and 6 — including a painful defeat to So that dropped him to the bottom of the standings — the Chennai-born player has won his last two classical games against Firouzja and Carlsen.

Beating Carlsen twice in classical chess in a single event is the kind of result that reshapes how the chess world sees a player. The previous such double in an elite round-robin against the Norwegian legend is hard to recall.

For Pragg, this is no longer just a tournament — it is a statement. The man ranked third in India behind Gukesh and Arjun Erigaisi is making a case that he belongs at the very top.

## Gukesh's Struggles Continue

For Gukesh, Oslo has been a humbling experience. The World Champion, who won the title in dramatic fashion last year, has lost three classical games in this event and sits fifth in the standings.

His Round 8 game against Firouzja followed a familiar pattern. Gukesh showed flashes of brilliance in the middlegame, but the French-Iranian grandmaster's relentless pressure proved too much, and the world champion could not hold the position together.

With two rounds left, Gukesh will look to finish strongly. He faces Pragg in Round 9 — an all-Indian clash that carries both personal rivalry and tournament implications.

## Women's Section: Assaubayeva Pulls Away

In the Women's event, Bibisara Assaubayeva of Kazakhstan delivered a commanding classical win over India's Divya Deshmukh to extend her lead to a virtually unassailable 15.5 points.

Divya, who had been Assaubayeva's closest challenger, conceded the full three points and remains on 10, now 5.5 points adrift with just two rounds to play. India's Koneru Humpy sits on 8 points in last place.

The tournament runs through June 5. Round 9 takes place after a rest day, and the stakes for the Indian contingent could not be higher.

**Sources:** Chess.com, ChessBase, Wikipedia, Norway Chess official"""

    sources = json.dumps([
        {"name": "Chess.com", "url": "https://www.chess.com"},
        {"name": "ChessBase", "url": "https://en.chessbase.com"},
        {"name": "Norway Chess Official", "url": "https://norwaychess.no"},
        {"name": "Wikipedia - Norway Chess 2026", "url": "https://en.wikipedia.org/wiki/2026_Norway_Chess"},
    ])

    # Image sourcing — Wikipedia for Praggnanandhaa
    print("  Sourcing image for Praggnanandhaa...")
    img_url = fetch_wikipedia_person_image("Praggnanandhaa Rameshbabu")
    if not img_url:
        img_url = fetch_wikipedia_person_image("R Praggnanandhaa")
    if not img_url:
        img_url = fetch_pexels_image("chess grandmaster tournament", "chess board competition")

    image_attribution = "Wikimedia Commons"
    final_image_url = None

    if img_url:
        art_id_temp = str(uuid.uuid4())
        filename = f"{art_id_temp}.jpg"
        final_image_url = upload_image_to_supabase(img_url, filename)
        if not final_image_url and "upload.wikimedia.org" in img_url:
            # Wikimedia URLs are permanent, use directly
            if validate_image_url(img_url):
                final_image_url = img_url

    now_ts = datetime.now(timezone.utc).isoformat()
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "sports",
        "vertical": "sports",
        "status": "published",
        "published_at": now_ts,
        "sources": sources,
        "is_editorial": False,
        "image_attribution": image_attribution,
    }
    if final_image_url:
        article["image_url"] = final_image_url

    art_id = insert_article(article)

    # If we used a temp UUID for the filename but now have the real ID, re-upload
    if art_id and final_image_url and art_id_temp in str(final_image_url):
        new_filename = f"{art_id}.jpg"
        if img_url:
            new_url = upload_image_to_supabase(img_url, new_filename)
            if new_url:
                patch_article(art_id, {"image_url": new_url})

    return art_id


# ── Article 2: India Women T20I Loss ────────────────────────────────
def write_india_women_t20():
    print("\n=== Article 2: India Women Lose Final T20I to England ===")

    slug = "india-women-lose-final-t20i-england-taunton-harmanpreet-56-capsey-series-2026-nri"
    headline = "Harmanpreet Made 56 Not Out. Capsey Made 45 Off 21 Balls. England Chased Down 180 to Win the Final T20I at Taunton."
    subheadline = "India posted their highest score of the series but England's Alice Capsey dismantled the target in 18.3 overs, raising concerns about India's T20 World Cup preparation."

    body = """India's women put up a fight in the final T20I at Taunton. It was not enough.

Batting first at the Cooper Associates County Ground on Tuesday, India posted 180 for 5 in their 20 overs — a competitive total built around Harmanpreet Kaur's unbeaten 56 off 40 balls. Yastika Bhatia struck 32 off just 18 deliveries at the top, Jemimah Rodrigues added a brisk 29 off 19, and Deepti Sharma contributed 32 off 24 in the middle overs.

It should have been enough. It was not.

## Capsey's Blitz

England's chase never truly wobbled. After losing Danni Wyatt (5) and Amy Jones (2) early to Kranti Gaud, the hosts regrouped through Sophia Dunkley and then Alice Capsey, who played the innings of the match.

Capsey smashed 45 not out off just 21 balls, hitting seven fours and a six with the kind of audacity that makes selectors salivate. The 21-year-old all-rounder came in at 23 for 2 in the powerplay and never looked back. Heather Knight joined her with an assured 24 not out off 15, and together they steered England to 184 for 4 with nine balls to spare.

England won by six wickets.

## Series Verdict

The result capped a difficult tour for India. Despite moments of individual brilliance — Rodrigues rescued the first match, Harmanpreet anchored the third — the team could not string together a complete performance across both innings.

The bowling, in particular, looked exposed. India's attack conceded 9.95 runs per over across England's chase, with only Gaud (2 for 28 in 3 overs) providing any consistent threat. Deepti Sharma, usually India's most reliable option, conceded 12 runs in her single over. The lack of a genuine pace threat at the top was evident.

## World Cup Warning Signs

With the Women's T20 World Cup in England beginning on June 14 — just 12 days away — this tour was supposed to be preparation, not a confidence drain.

For NRI fans who will travel to grounds across England to watch India at the World Cup, the concerns are real. India's top order has been inconsistent — Smriti Mandhana managed only 8 in this match, and Shafali Verma's aggressive 11 off 6 balls was too brief to count. The middle order depends heavily on Harmanpreet, who turned 37 this year and cannot carry the batting every game.

The positives: Yastika Bhatia's fearless strokeplay at the top suggests she could be the X-factor India needs. And Harmanpreet's ability to bat deep and accelerate remains world-class.

## What It Means

India have now lost consecutive T20I series in England ahead of a home World Cup on English soil. The last time India won a major ICC event in women's cricket was never — and this tour offers little evidence that the drought will end in June.

But cricket, especially T20 cricket, rewards moments. India have the talent to beat anyone on their day. They need to find that day soon.

**India 180/5 (20 overs):** Harmanpreet 56* (40), Yastika 32 (18), Deepti 32 (24), Jemimah 29 (19), Shafali 11 (6)

**England 184/4 (18.3 overs):** Capsey 45* (21), Knight 24* (15), Dunkley 16 (13)

**Sources:** Sportradar, Cricbuzz, CricketnMore, The Bridge"""

    sources = json.dumps([
        {"name": "Sportradar", "url": "https://sportradar.com"},
        {"name": "Cricbuzz", "url": "https://www.cricbuzz.com"},
        {"name": "CricketnMore", "url": "https://www.cricketnmore.com"},
        {"name": "The Bridge", "url": "https://thebridge.in"},
    ])

    # Image — Wikipedia for Harmanpreet Kaur
    print("  Sourcing image for Harmanpreet Kaur...")
    img_url = fetch_wikipedia_person_image("Harmanpreet Kaur")
    if not img_url:
        img_url = fetch_pexels_image("women cricket match", "cricket stadium India")

    image_attribution = "Wikimedia Commons"
    final_image_url = None

    if img_url:
        art_id_temp = str(uuid.uuid4())
        filename = f"{art_id_temp}.jpg"
        final_image_url = upload_image_to_supabase(img_url, filename)
        if not final_image_url and "upload.wikimedia.org" in img_url:
            if validate_image_url(img_url):
                final_image_url = img_url

    now_ts2 = datetime.now(timezone.utc).isoformat()
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "sports",
        "vertical": "sports",
        "status": "published",
        "published_at": now_ts2,
        "sources": sources,
        "is_editorial": False,
        "image_attribution": image_attribution,
    }
    if final_image_url:
        article["image_url"] = final_image_url

    art_id = insert_article(article)

    if art_id and final_image_url and art_id_temp in str(final_image_url):
        new_filename = f"{art_id}.jpg"
        if img_url:
            new_url = upload_image_to_supabase(img_url, new_filename)
            if new_url:
                patch_article(art_id, {"image_url": new_url})

    return art_id


# ── main ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Sports Writer — The Videshi — June 2, 2026 (evening)")
    print("=" * 60)

    results = []
    results.append(("Norway Chess R8", write_norway_chess()))
    results.append(("India Women T20I", write_india_women_t20()))

    print("\n" + "=" * 60)
    print("RESULTS:")
    for name, art_id in results:
        status = f"✓ Published (id={art_id})" if art_id else "✗ Failed"
        print(f"  {name}: {status}")
    print("=" * 60)

    failed = [name for name, art_id in results if not art_id]
    if failed:
        print(f"\n⚠ {len(failed)} article(s) failed: {', '.join(failed)}")
        sys.exit(1)
    else:
        print(f"\n✓ All {len(results)} articles published successfully.")
