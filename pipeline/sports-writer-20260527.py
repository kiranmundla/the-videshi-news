#!/usr/bin/env python3
"""
Sports writer for The Videshi — 2026-05-27 morning run
Articles:
1. French Open landscape: Medvedev stunned, Kouame makes history, Basavareddy R2 today
2. Divya Deshmukh beats Humpy in all-Indian Norway Chess clash
"""

import json, os, re, sys, time, uuid, urllib.parse
import requests
from datetime import datetime, timezone

# ── ENV ──────────────────────────────────────────────────────────────────
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY   = os.environ.get('PEXELS_API_KEY', '')

HEADERS_SB = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation',
}

# ── WIKIPEDIA IMAGE ──────────────────────────────────────────────────────
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

# ── PEXELS IMAGE ─────────────────────────────────────────────────────────
def fetch_pexels_image(query, fallback_query=None):
    """Fetch from Pexels using curl (requests gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            result = subprocess.run(
                ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
                 f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=3&orientation=landscape'],
                capture_output=True, text=True, timeout=15,
            )
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            for photo in photos:
                url = photo.get('src', {}).get('large2x') or photo.get('src', {}).get('original')
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

# ── SUPABASE IMAGE UPLOAD ────────────────────────────────────────────────
def upload_image_to_supabase(img_url, filename):
    """Download an image and upload to Supabase storage. Return public URL."""
    try:
        r = requests.get(img_url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=15)
        if r.status_code != 200:
            print(f"  ⚠ Image download failed: HTTP {r.status_code}")
            # Wikipedia/Pexels URLs are permanent — use them directly
            if 'upload.wikimedia.org' in img_url or 'images.pexels.com' in img_url:
                print(f"  → Using permanent source URL directly")
                return img_url
            return None
        content_type = r.headers.get('Content-Type', 'image/jpeg')
        if not content_type.startswith('image/'):
            print(f"  ⚠ Not an image: {content_type}")
            return img_url
        if len(r.content) < 5000:
            print(f"  ⚠ Image too small: {len(r.content)} bytes")
            return img_url

        # Upload to Supabase storage
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        up = requests.post(
            upload_url,
            headers={
                'apikey': SUPABASE_KEY,
                'Authorization': f'Bearer {SUPABASE_KEY}',
                'Content-Type': content_type,
                'x-upsert': 'true',
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
            # If the source is a permanent URL (wikimedia, pexels), return it directly
            if 'upload.wikimedia.org' in img_url or 'images.pexels.com' in img_url:
                return img_url
            return None
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        if 'upload.wikimedia.org' in img_url or 'images.pexels.com' in img_url:
            return img_url
        return None

# ── VALIDATE IMAGE ───────────────────────────────────────────────────────
def validate_image_url(url):
    """Check that a URL returns a real image > 5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=10, allow_redirects=True)
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if 'image' in ct and cl > 5000:
            return True
        # Some servers don't return Content-Length on HEAD; try GET
        if 'image' in ct and cl == 0:
            r2 = requests.get(url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=10, stream=True)
            chunk = r2.raw.read(6000)
            r2.close()
            return len(chunk) > 5000
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False

# ── SUPABASE HELPERS ─────────────────────────────────────────────────────
def sb_insert(table, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    r = requests.post(url, headers=HEADERS_SB, json=data, timeout=30)
    if r.status_code in (200, 201):
        result = r.json()
        return result[0] if isinstance(result, list) and result else result
    else:
        print(f"  ✗ Insert into {table} failed: {r.status_code} {r.text[:300]}")
        return None

def sb_patch(table, match, data):
    params = '&'.join(f'{k}={v}' for k, v in match.items())
    url = f"{SUPABASE_URL}/rest/v1/{table}?{params}"
    r = requests.patch(url, headers=HEADERS_SB, json=data, timeout=30)
    if r.status_code in (200, 204):
        return True
    else:
        print(f"  ✗ Patch {table} failed: {r.status_code} {r.text[:300]}")
        return False


# ══════════════════════════════════════════════════════════════════════════
#  ARTICLE 1: French Open landscape — Basavareddy R2
# ══════════════════════════════════════════════════════════════════════════

article1 = {
    "headline": "Medvedev Is Gone. A Seventeen-Year-Old Frenchman Just Made History. And the Kid From Andhra Pradesh Plays Round Two Today.",
    "subheadline": "The French Open draw is blowing apart. Nishesh Basavareddy, ranked 148th, has a path he could not have imagined four days ago.",
    "slug": "french-open-2026-day-4-medvedev-out-kouame-basavareddy-round-2-michelsen-20260527",
    "category": "sports",
    "body": """The 2026 French Open is four days old and already unrecognisable from the draw that was published on the weekend.

## The Sixth Seed Fell First

Daniil Medvedev, the sixth seed and former world number one, lost to Adam Walton in the first round on Tuesday. Walton is ranked 97th in the world. He is a 27-year-old Australian wildcard. The scoreline tells the story of a man who could never settle: 6-2, 1-6, 6-1, 1-6, 6-4.

It was Medvedev's sixth first-round exit in nine appearances at Roland Garros. No other Grand Slam has treated him so brutally. The Parisian clay has always been hostile territory for the Russian, whose flat groundstrokes and serve-dependent game were built for hard courts and indoor arenas. He came to Paris having pushed Jannik Sinner to tiebreaks at Indian Wells and taken a set off him in Rome. None of that mattered on Tuesday.

For every Indian-American watching from a living room in New Jersey or a sports bar in Fremont, the Medvedev exit means one very specific thing: the bottom half of the draw just got lighter. Nishesh Basavareddy is in that half.

## A Seventeen-Year-Old Makes History

On the same afternoon that Medvedev was imploding, a teenager on an outside court was writing his own story. Moise Kouame, a seventeen-year-old Frenchman, beat Marin Cilic — a former US Open champion — 7-6(4), 6-2, 6-1. With that result, Kouame became the youngest man to win a main-draw match at a Grand Slam in seventeen years.

Kouame is not yet ranked inside the top 500. He does not have a full-time coach or a sponsor. What he has is a forehand that travels at 140 kilometres per hour and the nerve to use it against a player who has been competing on tour since before Kouame was born. He will play Adolfo Daniel Vallejo in the second round.

## Sinner Is a Machine

At the top of the draw, the man everyone expects to lift the trophy on June 7 is playing like he has already decided the outcome. Jannik Sinner beat Clement Tabur 6-1, 6-3, 6-4 in the first round, extending his winning streak to thirty consecutive matches. He has won all five ATP Masters 1000 titles this season. No player in the Open Era has done that.

Carlos Alcaraz, the defending champion and the only man considered a genuine threat to Sinner's dominance, withdrew before the tournament with an injury. The betting markets now give Sinner a 75 per cent chance of winning the title. The next closest — Alexander Zverev — is at eight per cent.

## Basavareddy's Moment

And then there is Nishesh Basavareddy. On Saturday, the 21-year-old from Indiana — whose parents left Andhra Pradesh before he was born — beat Taylor Fritz, the seventh seed, in four sets: 7-6, 7-6, 6-7, 6-1. It was only his second Grand Slam main-draw victory. It was Fritz's worst loss at a major since 2022.

Today, Basavareddy faces Alex Michelsen, the world number 42. Their head-to-head record stands at 2-2. Michelsen has more clay experience and more firepower from the baseline. But Basavareddy has something rarer: the knowledge that he has already beaten a player thirty places higher in the rankings on this same surface four days ago.

The match is scheduled for the morning session, 8:50 AM Eastern Time. For the Indian diaspora — which has spent decades producing cricketers, chess grandmasters, and Spelling Bee champions but almost never a male Grand Slam contender — this is unfamiliar and intoxicating territory.

Basavareddy's parents are from Nellore, a coastal city in southern Andhra Pradesh. He grew up in Fishers, Indiana, playing on public courts and training at a local academy. India has 1.4 billion people and could not produce a man ranked inside the world's top 100 in tennis. The United States, using the same Indian DNA, produced one who is now in the second round of the French Open with a draw that is falling apart around him.

## What Comes Next

If Basavareddy wins today, he faces the winner of Rafael Jodar and James Duckworth in the third round. If the upsets keep coming — and this tournament has shown that they will — the path to the second week is more plausible than it has ever been for a player of Indian origin at Roland Garros.

The French Open is live on TNT and the Tennis Channel in the United States. Streaming is available on DIRECTV and Max.

*Sources: Reuters, Tennis Up to Date, Sporting News, Indian Tennis Daily*""",
    "sources_json": [
        {"url": "https://www.reuters.com/sports/tennis/medvedev-stunned-by-wildcard-walton-french-open-first-round-2026-05-26/", "name": "Reuters"},
        {"url": "https://www.tennisuptodate.com/french-open-roland-garros-atp-2026", "name": "Tennis Up to Date"},
        {"url": "https://www.sportingnews.com/", "name": "Sporting News"},
        {"url": "https://indiantennisdaily.com/", "name": "Indian Tennis Daily"}
    ],
    "tags": ["French Open", "Roland Garros", "Nishesh Basavareddy", "Medvedev", "Sinner", "tennis"],
    "image_person": "Nishesh Basavareddy",
    "image_fallback_query": "Roland Garros French Open tennis court clay",
    "image_attribution": "Wikimedia Commons",
}


# ══════════════════════════════════════════════════════════════════════════
#  ARTICLE 2: Divya Deshmukh beats Humpy — Norway Chess
# ══════════════════════════════════════════════════════════════════════════

article2 = {
    "headline": "Divya Deshmukh Is Nineteen. She Just Beat India's Number One. She Has Won Every Match at Norway Chess.",
    "subheadline": "The girl from Nagpur defeated Koneru Humpy in an all-Indian Armageddon clash on Day Two. She leads the women's event with a perfect record.",
    "slug": "divya-deshmukh-beats-koneru-humpy-norway-chess-2026-round-2-all-indian-armageddon-20260527",
    "category": "sports",
    "body": """On Day One in Oslo, Divya Deshmukh beat the women's world champion. On Day Two, she beat her own country's number one. She is nineteen years old and she has not dropped a point.

## The All-Indian Clash

Round Two of Norway Chess 2026 produced a match that Indian chess had been anticipating for years. Divya Deshmukh, the prodigy from Nagpur who earned her Grandmaster title at fifteen, faced Koneru Humpy, the woman who has carried Indian chess on her shoulders for two decades.

The classical game was drawn. Both players were careful, probing, unwilling to concede the decisive mistake. Humpy, who turned 38 this year, played the kind of positional chess that has kept her in the world's top five for most of her career. Deshmukh matched her move for move.

Then came the Armageddon.

In Armageddon, White gets five minutes and must win. Black gets four minutes and only needs a draw. It is the most psychologically brutal format in chess — a tiebreaker designed to force a result, where one wrong calculation under time pressure ends everything.

Deshmukh won. For the second consecutive day, she won in Armageddon. On Day One, it was Ju Wenjun, the reigning women's world champion. On Day Two, it was Humpy. The two most decorated women in the current chess landscape, beaten back-to-back by a teenager from Maharashtra.

## Who Is Divya Deshmukh?

For the Indian diaspora, Deshmukh is part of a generation of chess players who have transformed the sport. She grew up in Nagpur, training under local coaches before her talent became impossible to ignore. She became the youngest Indian woman to earn the Grandmaster title. She won the World Rapid Chess Championship. She represented India at the Chess Olympiad, where the Indian women's team won gold.

But Norway Chess is different from anything she has done before. This is a super-tournament — an invitation-only event featuring the strongest players in the world. The women's field includes the world champion, a former world champion, and some of the highest-rated players alive. Deshmukh is the youngest competitor in either section.

And she is leading.

## The Standings After Two Rounds

Deshmukh sits at the top of the women's standings with a perfect score. Behind her, the field is bunched. Bibisara Assaubayeva of Kazakhstan won a classical game against Humpy on Day One — one of only two classical victories in the women's event so far. Ju Wenjun and Anna Muzychuk have split their Armageddon matches.

Humpy, meanwhile, has lost two consecutive tiebreakers. It has been a difficult start for India's most experienced player, who arrived in Oslo as the second seed. But Humpy has been here before. She has the temperament and the record to recover. The double round-robin format means she will face every opponent again in the second half.

## Meanwhile, in the Men's Section

The men's event belongs to Alireza Firouzja. The 23-year-old Franco-Iranian has won every point available — a perfect six out of six — including classical victories over Magnus Carlsen and R. Praggnanandhaa. He leads by three and a half points.

India's two representatives, world champion D. Gukesh and Praggnanandhaa, are struggling. Gukesh has 2.5 points from a possible six after losing to Wesley So in Armageddon. Praggnanandhaa has just 1.5 points, the lowest in the field, after being demolished by Firouzja in their classical game.

On Wednesday, Firouzja faces Gukesh. It is the most anticipated match of the round — the player who has been perfect against the reigning world champion. For Gukesh, it is a chance to prove that the crown he won at eighteen was not a fluke. For Firouzja, it is a chance to beat every elite player in the world in the span of five days.

## The Larger Picture

Norway Chess runs until June 5. There are eight more rounds. But the story of the first two days is clear: Indian chess is in a generational transition. Humpy and Gukesh are the established stars. Deshmukh and Praggnanandhaa represent what comes next. In Oslo, the future is winning.

For NRIs following from the United States, Norway Chess streams live on Chess.com and ChessBase India's YouTube channel. Round Three begins today.

*Sources: ChessBase India, ChessBase, LatestLY, News Web India 123*""",
    "sources_json": [
        {"url": "https://chessbase.in/news/Norway-Chess-2026-R2", "name": "ChessBase India"},
        {"url": "https://en.chessbase.com/post/norway-chess-2026-r2", "name": "ChessBase"},
        {"url": "https://www.latestly.com/sports/norway-chess-2026/", "name": "LatestLY"},
        {"url": "https://news.webindia123.com/", "name": "News Web India 123"}
    ],
    "tags": ["Norway Chess", "Divya Deshmukh", "Koneru Humpy", "chess", "Indian chess", "women chess"],
    "image_person": "Divya Deshmukh",
    "image_person_disambig": "Divya Deshmukh (chess player)",
    "image_fallback_query": "chess tournament grandmaster woman",
    "image_attribution": "Wikimedia Commons",
}

# ══════════════════════════════════════════════════════════════════════════
#  PUBLISH
# ══════════════════════════════════════════════════════════════════════════

def publish_article(art):
    print(f"\n{'='*60}")
    print(f"Publishing: {art['headline'][:80]}...")
    print(f"{'='*60}")

    # 1. Image sourcing — Wikipedia first
    img_url = None
    person = art.get('image_person')
    if person:
        img_url = fetch_wikipedia_person_image(person)
        if not img_url and art.get('image_person_disambig'):
            img_url = fetch_wikipedia_person_image(art['image_person_disambig'])
    
    if not img_url:
        img_url = fetch_pexels_image(art.get('image_fallback_query', ''), art.get('image_fallback_query2'))

    # 2. Upload to Supabase storage
    final_img_url = None
    attribution = art.get('image_attribution', 'The Videshi')
    if img_url:
        art_id = str(uuid.uuid4())
        filename = f"{art_id}.jpg"
        final_img_url = upload_image_to_supabase(img_url, filename)
        if final_img_url and not validate_image_url(final_img_url):
            print(f"  ⚠ Uploaded image failed validation, trying original URL")
            if 'upload.wikimedia.org' in img_url or 'images.pexels.com' in img_url:
                final_img_url = img_url
            else:
                final_img_url = None
    else:
        art_id = str(uuid.uuid4())
        print("  ⚠ No image found — publishing without image")

    # 3. Build record
    word_count = len(art['body'].split())
    print(f"  Word count: {word_count}")
    if word_count < 400:
        print(f"  ✗ REJECTED — under 400 words ({word_count})")
        return None

    record = {
        'id': art_id,
        'headline': art['headline'],
        'subheadline': art['subheadline'],
        'slug': art['slug'],
        'body': art['body'],
        'category': art['category'],
        'status': 'published',
        'published_at': datetime.now(timezone.utc).isoformat(),
        'sources': art.get('sources_json', []),
        'tags': art.get('tags', []),
        'word_count': word_count,
        'vertical': 'sports',
    }
    if final_img_url:
        record['image_url'] = final_img_url
        record['image_attribution'] = attribution

    # 4. Insert into Supabase
    result = sb_insert('p2_articles', record)
    if result:
        rid = result.get('id', art_id)
        print(f"  ✓ Published: {art['slug']}")
        print(f"    ID: {rid}")
        print(f"    Image: {final_img_url or 'none'}")
        return rid
    else:
        print(f"  ✗ Failed to publish: {art['slug']}")
        return None


# ── MAIN ─────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    articles = [article1, article2]
    results = []
    for art in articles:
        rid = publish_article(art)
        results.append({'slug': art['slug'], 'id': rid, 'ok': rid is not None})
        time.sleep(1)

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for r in results:
        status = '✓' if r['ok'] else '✗'
        print(f"  {status} {r['slug']}")
    
    failed = [r for r in results if not r['ok']]
    if failed:
        print(f"\n  {len(failed)} article(s) failed")
        sys.exit(1)
    else:
        print(f"\n  All {len(results)} articles published successfully")
