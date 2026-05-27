#!/usr/bin/env python3
"""
The Videshi - Sports Writer (May 27, 2026)
Articles:
1. Unity Cup: Nigeria 2-0 Zimbabwe, India face Jamaica today
2. Norway Chess R3: Firouzja vs Gukesh, Pragg vs Carlsen last-place showdown
"""

import os, json, uuid, requests, urllib.parse, time
from datetime import datetime, timezone

# ── env ──
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")
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
            timeout=10,
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
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            result = subprocess.run(
                ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
                 f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape"],
                capture_output=True, text=True, timeout=15,
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for p in photos:
                url = p.get("src", {}).get("large2x") or p.get("src", {}).get("original")
                if url:
                    print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def upload_image_to_supabase(image_url, filename):
    """Download image and upload to Supabase storage bucket 'article-images'."""
    try:
        r = requests.get(image_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=30)
        if r.status_code != 200:
            print(f"  ⚠ Image download failed: HTTP {r.status_code}")
            return None
        content_type = r.headers.get("Content-Type", "image/jpeg")
        if "image" not in content_type:
            print(f"  ⚠ Not an image: {content_type}")
            return None
        if len(r.content) < 5000:
            print(f"  ⚠ Image too small: {len(r.content)} bytes")
            return None

        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        up = requests.post(
            upload_url,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": content_type,
                "x-upsert": "true",
            },
            data=r.content,
            timeout=30,
        )
        if up.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed: {up.status_code} {up.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return None


def insert_article(article):
    """Insert article into p2_articles."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30,
    )
    if r.status_code in (200, 201):
        result = r.json()
        art_id = result[0]["id"] if isinstance(result, list) else result.get("id")
        print(f"  ✓ Article inserted: {article['slug']} (id: {art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed: {r.status_code} {r.text[:300]}")
        return None


def update_article(art_id, updates):
    """Patch article fields."""
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{art_id}",
        headers=HEADERS,
        json=updates,
        timeout=30,
    )
    if r.status_code in (200, 201, 204):
        print(f"  ✓ Article updated: {art_id}")
    else:
        print(f"  ⚠ Update failed: {r.status_code} {r.text[:200]}")


# ══════════════════════════════════════════════════════════════════════════════
# ARTICLE 1: Unity Cup — Nigeria 2-0 Zimbabwe, India face Jamaica
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("ARTICLE 1: Unity Cup — Nigeria Through, India vs Jamaica Today")
print("=" * 70)

art1_slug = "unity-cup-2026-nigeria-beat-zimbabwe-india-jamaica-semifinal-london-valley-20260527"
art1_headline = "Nigeria Are Already in the Final. India Play Jamaica at the Valley on Wednesday Night. It Is India's First Match in England in Twenty-Four Years."
art1_subheadline = "Femi Azeez scored twice on his senior debut to send Nigeria through 2-0. Now a depleted India squad — missing seven players after Mohun Bagan refused to release them — must beat Jamaica to reach the Unity Cup final."

art1_body = """India's senior men's football team will walk onto the pitch at The Valley in Charlton, southeast London, on Wednesday night for a match that carries more symbolism than any recent friendly. It is the Unity Cup semifinal against Jamaica. It is India's first match on English soil since 2002. And it comes after the other semifinal has already been decided.

## Nigeria Set the Bar

On Tuesday night, Nigeria's Super Eagles dispatched Zimbabwe 2-0 in the first semifinal, booking their place in Friday's final. The goals came from Femi Azeez, the Millwall winger making his senior international debut. He scored inside five minutes with a composed finish, then doubled Nigeria's lead in the 63rd minute. Zimbabwe, ranked 130th, offered little resistance.

Nigeria are the defending Unity Cup champions, having won the tournament in 2002, 2004, and 2025. Head coach Éric Chelle praised the performance of his debutants, and Azeez — fresh off a strong English Championship campaign — is now expected to attract summer transfer window interest.

The result means the winner of India vs Jamaica will face Nigeria in the final on Friday. The loser drops to the third-place match on the same day.

## India's Uphill Battle

India arrive in London undermanned and underranked. Ranked 136th by FIFA, they face a Jamaica side ranked 71st — forty-five places higher in the global pecking order. More critically, India are missing seven players after Mohun Bagan, the country's biggest club, refused to release them for the tournament. The squad was trimmed to just seventeen players before four late additions — including Macarton and Barla — brought the number to a barely functional twenty-one.

Head coach Manolo Márquez has had limited time to prepare. The squad flew to London knowing they would face a Jamaica team that includes players from the English Championship and MLS, with a generation of dual-nationality athletes who have chosen the Reggae Boyz over larger federations.

## Why It Matters for the Diaspora

For NRIs in the United Kingdom, this is a rare opportunity to watch India play football in person. India has never been a footballing destination for diaspora sports fans in the way cricket has. The last time India played a match in England was over two decades ago, and opportunities to see the Blue Tigers live in Europe are virtually nonexistent.

The Valley, home to Charlton Athletic, is a modest ground by Premier League standards but a serious venue by Unity Cup standards. The tournament's four-team format — India, Jamaica, Nigeria, Zimbabwe — creates a compressed, high-stakes bracket that rewards showing up ready.

## The Context: India's Football Trajectory

Indian football has been on a slow upward trajectory under the joint efforts of the AIFF and ISL investment, but the Mohun Bagan player-release dispute exposes the same fault lines that have held the sport back for decades. Club-versus-country conflicts, scheduling overlaps, and the lack of enforceable FIFA windows for friendlies continue to hobble India's ability to field full-strength squads in international tournaments.

The Unity Cup, while not a FIFA-sanctioned competition, represents one of the few invitational windows where India can test themselves against teams from different confederations. Jamaica, Nigeria, and Zimbabwe bring Caribbean, African, and southern African football styles that India's players rarely encounter.

## What to Watch

The match kicks off at The Valley on Wednesday evening London time. For viewers in India, that translates to the early hours of Thursday morning (IST). FanCode has the streaming rights in India.

Key players to watch include Ryan Williams, who has been one of India's more reliable performers in recent windows, and Jamaica's Bailey Cadamarteri, a young forward attracting attention from English clubs. Nigeria's Azeez will be watching from the stands, already knowing his opponent for Friday.

For India, a win would be historic — not just for reaching the Unity Cup final, but for beating a Caribbean nation ranked nearly fifty places above them, in England, with a depleted squad. A loss would be instructive but familiar.

The game matters either way. India are playing football in London. That alone is worth watching.

**Sources:** Trendbrio24, Khel Now, LiveMint, Wikipedia (2026 Unity Cup), IndiaSportsHub, South Asian Herald"""

# Image: Try Wikipedia for India national football team, or Sunil Chhetri, or use Pexels
print("  Sourcing image for Unity Cup article...")
img1_url = fetch_wikipedia_person_image("India national football team")
if not img1_url:
    img1_url = fetch_wikipedia_person_image("Sunil Chhetri")
if not img1_url:
    img1_url = fetch_pexels_image("football match stadium night", "soccer match floodlights")

img1_final = None
if img1_url:
    img1_final = upload_image_to_supabase(img1_url, f"unity-cup-india-jamaica-20260527.jpg")

art1_data = {
    "headline": art1_headline,
    "subheadline": art1_subheadline,
    "body": art1_body,
    "slug": art1_slug,
    "category": "sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps([
        {"name": "Trendbrio24", "url": "https://trendbrio24.com/nigeria-defeat-zimbabwe-2-0-to-reach-2026-unity-cup-final/"},
        {"name": "Khel Now", "url": "https://khelnow.com/"},
        {"name": "LiveMint", "url": "https://www.livemint.com/"},
        {"name": "Wikipedia", "url": "https://en.wikipedia.org/wiki/2026_Unity_Cup"},
    ]),
    "image_url": img1_final,
    "image_attribution": "Wikimedia Commons" if img1_final and ("wikipedia" in (img1_url or "").lower() or "wikimedia" in (img1_url or "").lower()) else "Pexels",
    "urgency": "daily",
    "is_featured": False,
    "score_total": 50,
    "diaspora_angle": "For NRIs in the UK, this is a rare chance to watch India play football live on English soil — the first time in 24 years. The Unity Cup in London features India, Jamaica, Nigeria, and Zimbabwe at The Valley in Charlton. The Mohun Bagan player-release dispute highlights club-vs-country tensions that diaspora fans have long criticized. FanCode streams the match in India.",
}

art1_id = insert_article(art1_data)

# ══════════════════════════════════════════════════════════════════════════════
# ARTICLE 2: Norway Chess R3 — Firouzja vs Gukesh, Pragg vs Carlsen
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("ARTICLE 2: Norway Chess R3 — Firouzja vs Gukesh, Pragg vs Carlsen")
print("=" * 70)

art2_slug = "norway-chess-2026-round-3-firouzja-gukesh-pragg-carlsen-last-place-divya-assaubayeva-20260527"
art2_headline = "Firouzja Has Not Dropped a Single Point. On Wednesday He Plays the World Champion. Praggnanandhaa Faces Carlsen in a Battle Between the Two Players in Last Place."
art2_subheadline = "Norway Chess round three pits the tournament's most dominant player against India's Gukesh Dommaraju. The other board features Pragg and Carlsen — both desperate to stop the bleeding. In the women's event, Divya Deshmukh faces tournament leader Assaubayeva."

art2_body = """After two rounds of Norway Chess 2026 in Oslo, the standings tell a story that almost nobody predicted. Alireza Firouzja has a perfect 6 out of 6 points. He has beaten Magnus Carlsen and Praggnanandhaa Rameshbabu in consecutive classical games. He is playing with an injured ankle. And on Wednesday, he faces the reigning World Chess Champion, Gukesh Dommaraju.

## Firouzja's Extraordinary Run

The 22-year-old French-Iranian grandmaster arrived in Oslo with something to prove after a disappointing performance in Bucharest, where he lost three games. What followed has been a masterclass.

In round one, Firouzja secured his first-ever classical victory over Carlsen — the five-time world champion, the highest-rated player in history, and the man who has been virtually unbeatable in Norway Chess since its inception. In round two, he dismantled Praggnanandhaa with clinical precision, converting a smooth endgame after the Indian prodigy lost his way in the middlegame.

When asked about his preparation, Firouzja was characteristically understated. "Not today, for sure," he said of round two's opening. "It was a decent game, but I don't think the opening was something special." On the ankle injury that has required him to use crutches between games: "I have a lot of pain, but it's something that keeps me focused — it makes me not think about pain."

His 6/6 score gives him a 3.5-point lead over Wesley So and Gukesh, who are tied for second. In the Norway Chess format — where a classical win earns 3 points, an armageddon win 1.5, and an armageddon loss 1 — that gap is enormous. Firouzja is guaranteed to remain the sole leader after round three regardless of results.

## The Main Event: Firouzja vs Gukesh

Gukesh Dommaraju, 20, is the youngest-ever undisputed World Chess Champion. He won the title in December 2024 and has since become one of the most feared competitors in classical chess. But Norway Chess has been a struggle.

In round one, Gukesh survived a 144-move marathon against Vincent Keymer — the longest game of the tournament so far — only to eke out a draw and win in armageddon. In round two, he had Wesley So on the ropes in the classical game, forcing the Filipino-American grandmaster into a queen sacrifice. But Gukesh could not convert, and So struck back to win the armageddon tiebreaker.

The round-three pairing is intriguing for another reason: Firouzja will have the Black pieces. In elite chess, Black traditionally plays for a draw and hopes for more. Firouzja has been anything but traditional. Whether he maintains his aggressive approach or shifts to a more measured strategy against the world champion will define the round.

## The Bottom-of-the-Table Battle: Pragg vs Carlsen

If Firouzja vs Gukesh is the marquee matchup, the other board offers its own drama. Praggnanandhaa Rameshbabu faces Magnus Carlsen, and both players sit at the bottom of the standings.

Carlsen — the tournament's defending champion and the overwhelming pre-tournament favorite — has had an uncharacteristically rocky start. He lost to Firouzja in round one and barely survived a chaotic classical game against Keymer in round two, missing a winning position before salvaging an armageddon victory. His dad joke about the game being "an udder embarrassment" has become the tournament's most quoted line.

Praggnanandhaa, meanwhile, has been on the wrong end of both results — a round-one armageddon win over So followed by a 3-0 classical loss to Firouzja in round two. For the 20-year-old Indian, the Carlsen matchup is both a danger and an opportunity. A classical win over the world's top-rated player would transform his tournament.

For Indian chess fans, the sight of Pragg and Gukesh playing simultaneously on adjacent boards in Norway Chess is becoming a familiar but still thrilling spectacle. Both players are part of India's remarkable chess generation that has produced two world championship challengers in their teens.

## Women's Event: Divya vs Assaubayeva

The women's tournament has its own compelling round-three matchup. Divya Deshmukh, the 19-year-old Indian star who stunned Women's World Champion Ju Wenjun in round one and beat Koneru Humpy in an all-Indian armageddon clash in round two, now faces tournament leader Bibisara Assaubayeva.

The Kazakh grandmaster leads by 1.5 points and will have the White pieces, but Divya has been the most exciting player in the women's field. When asked if she managed to eat the dried mangoes she had been eyeing during round one, she laughed: "I think it's there, but I didn't eat it today. I was pretty busy in the game!"

Anna Muzychuk rounds out the top three after recovering from an armageddon loss with a spirited win over Ju Wenjun that ended in checkmate on the board. "As a spectator, you get a lot of joy, but as a player, it's crazy!" she said.

## Round Three Schedule

Round three begins Wednesday, May 27, at 11:00 AM ET (8:30 PM IST / 5:00 PM CEST). Games can be watched on Chess24's YouTube and Twitch channels.

**Sources:** Chess.com, ChessBase, ChessBase India, Norway Chess official"""

# Image: Wikipedia image for Gukesh (Firouzja may 429), then Firouzja, then Pragg
print("  Sourcing image for Norway Chess article...")
img2_url = fetch_wikipedia_person_image("Gukesh Dommaraju")
if not img2_url:
    time.sleep(2)
    img2_url = fetch_wikipedia_person_image("Alireza Firouzja")
if not img2_url:
    img2_url = fetch_wikipedia_person_image("Praggnanandhaa Rameshbabu")
if not img2_url:
    img2_url = fetch_pexels_image("chess grandmaster tournament", "chess championship board")

img2_final = None
if img2_url:
    img2_final = upload_image_to_supabase(img2_url, f"norway-chess-r3-firouzja-gukesh-20260527.jpg")

art2_data = {
    "headline": art2_headline,
    "subheadline": art2_subheadline,
    "body": art2_body,
    "slug": art2_slug,
    "category": "sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps([
        {"name": "Chess.com", "url": "https://www.chess.com/news/view/2026-norway-chess-round-2"},
        {"name": "ChessBase India", "url": "https://chessbase.in/"},
        {"name": "ChessBase", "url": "https://en.chessbase.com/"},
        {"name": "Norway Chess", "url": "https://norwaychess.no/"},
    ]),
    "image_url": img2_final,
    "image_attribution": "Wikimedia Commons" if img2_final and ("wikipedia" in (img2_url or "").lower() or "wikimedia" in (img2_url or "").lower()) else "Pexels",
    "urgency": "daily",
    "is_featured": False,
    "score_total": 52,
    "diaspora_angle": "Three Indian grandmasters — Gukesh (world champion), Praggnanandhaa, and Divya Deshmukh — are competing in the same elite event in Oslo. Gukesh faces the tournament leader Firouzja with Black on Wednesday. Pragg takes on Carlsen. Divya faces tournament leader Assaubayeva in the women's event. India's chess dominance is the diaspora's proudest sports story right now.",
}

art2_id = insert_article(art2_data)

# ── Summary ──
print("\n" + "=" * 70)
print("SPORTS WRITER COMPLETE")
print("=" * 70)
print(f"Article 1: {'✓' if art1_id else '✗'} Unity Cup ({art1_slug})")
print(f"  Image: {img1_final or 'NONE'}")
print(f"Article 2: {'✓' if art2_id else '✗'} Norway Chess R3 ({art2_slug})")
print(f"  Image: {img2_final or 'NONE'}")
