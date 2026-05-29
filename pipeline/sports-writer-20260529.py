#!/usr/bin/env python3
"""Sports writer for The Videshi — 2026-05-29 batch"""

import json, os, re, sys, time, uuid, requests, urllib.parse
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    v = v.strip().strip('"').strip("'")
                    os.environ.setdefault(k, v)

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

def sb_insert(table, data):
    r = requests.post(f"{SUPABASE_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    if r.status_code in (200, 201):
        result = r.json()
        return result[0] if isinstance(result, list) else result
    print(f"  ✗ Insert error ({r.status_code}): {r.text[:300]}")
    return None

def sb_patch(table, filters, data):
    params = '&'.join(f"{k}={v}" for k, v in filters.items())
    url = f"{SUPABASE_URL}/rest/v1/{table}?{params}"
    r = requests.patch(url, headers=HEADERS, json=data, timeout=30)
    if r.status_code in (200, 204):
        return True
    print(f"  ✗ Patch error ({r.status_code}): {r.text[:300]}")
    return False

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
    """Fetch an image from Pexels API. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            result = subprocess.run(
                ['curl', '-sS', f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape',
                 '-H', f'Authorization: {PEXELS_KEY}'],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            for photo in photos:
                url = photo.get('src', {}).get('large2x') or photo.get('src', {}).get('large')
                if url:
                    # Validate
                    hr = requests.head(url, timeout=10)
                    cl = int(hr.headers.get('Content-Length', 0))
                    ct = hr.headers.get('Content-Type', '')
                    if cl > 5000 and 'image' in ct:
                        print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def upload_to_supabase_storage(image_url, filename):
    """Download image and upload to Supabase storage bucket."""
    try:
        r = requests.get(image_url, timeout=30, headers={"User-Agent": "TheVideshi/1.0"})
        if r.status_code != 200:
            print(f"  ⚠ Download failed: {r.status_code}")
            return image_url  # fallback to original
        
        content_type = r.headers.get('Content-Type', 'image/jpeg')
        if 'image' not in content_type:
            content_type = 'image/jpeg'
        
        upload_headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': content_type,
            'x-upsert': 'true'
        }
        
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        ur = requests.post(upload_url, headers=upload_headers, data=r.content, timeout=30)
        
        if ur.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed ({ur.status_code}): {ur.text[:200]}")
            # If it's a Wikimedia/Pexels URL, it's permanent - OK to use directly
            if 'upload.wikimedia.org' in image_url or 'images.pexels.com' in image_url:
                return image_url
            return None
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        if 'upload.wikimedia.org' in image_url or 'images.pexels.com' in image_url:
            return image_url
        return None

def validate_image_url(url):
    """Validate that URL returns a real image."""
    if not url:
        return False
    # Block banned sources
    banned = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com']
    if any(b in url for b in banned):
        return False
    banned_params = ['_nc_ht=', '_nc_cat=', 'ccb=']
    if any(p in url for p in banned_params):
        return False
    try:
        r = requests.head(url, timeout=10, headers={"User-Agent": "TheVideshi/1.0"}, allow_redirects=True)
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if 'image' in ct and cl > 5000:
            return True
        # Some servers don't return Content-Length on HEAD
        if 'image' in ct:
            return True
    except:
        pass
    return False

# ========================================================================
# ARTICLE 1: Wembanyama Forces Game 7 — Spurs Crush Thunder 118-91
# ========================================================================
def write_article_1():
    print("\n=== Article 1: Wembanyama Forces Game 7 ===")
    
    slug = "wembanyama-28-points-spurs-118-91-thunder-game-7-western-conference-finals-nba-20260529"
    headline = "Victor Wembanyama Scored Twenty-Eight Points and Ten Rebounds. The Spurs Won by Twenty-Seven. Game 7 Is Saturday in Oklahoma City."
    subheadline = "San Antonio's third-quarter avalanche buried the Thunder 118-91, tying the Western Conference finals at three games apiece. Shai Gilgeous-Alexander scored a season-low fifteen points. The winner on Saturday faces the New York Knicks for the NBA title."
    
    body = """The San Antonio Spurs were facing elimination on Thursday night. By the third quarter, they were playing like it was the Oklahoma City Thunder's season on the line.

Victor Wembanyama scored twenty-eight points and pulled down ten rebounds as the Spurs demolished the Thunder 118-91 in Game 6 of the Western Conference finals, forcing a decisive Game 7 on Saturday in Oklahoma City. The winner advances to face the New York Knicks in the NBA Finals.

## The Third-Quarter Avalanche

The game was competitive through halftime. San Antonio led 60-53, with Wembanyama already on twenty-two points — but the Thunder had been in bigger holes this series and climbed out. Then the third quarter happened.

The Spurs went on a devastating 20-0 run that broke the game open. Their defence suffocated Oklahoma City's offence, holding the Thunder to just twenty-eight points in the second half. By the time the fourth quarter began, the outcome was beyond doubt.

Dylan Harper added eighteen points and six rebounds. Stephon Castle posted seventeen points with nine assists and five rebounds — flirting with a triple-double in the biggest game of his young career. The Spurs outrebounded the Thunder 52-43 and shot 41 percent from three-point range while holding Oklahoma City to 25 percent.

## SGA's Worst Night

Shai Gilgeous-Alexander, the two-time consecutive MVP, had the worst game of his postseason. He finished with fifteen points on 33 percent shooting — a season low that left the Thunder without their primary engine when they needed him most.

Jalen Williams made a surprise return from injury but managed just one point. Chet Holmgren contributed ten points and eleven rebounds, and Cason Wallace had eleven points and three steals, but the Thunder's supporting cast could not compensate for their superstar's disappearance.

The series has been defined by lopsided margins — the average victory margin across six games is 18.3 points. The home team has won every game. That pattern gives Oklahoma City reason for optimism heading into Game 7 at Paycom Center, but the Spurs have already stolen a game on the road in this series, winning Game 1 in double overtime.

## Wembanyama Makes His Case

At twenty years old, Wembanyama is delivering in the highest-pressure moments the NBA offers. His Game 6 performance — twenty-eight points, ten rebounds, three blocks — was the kind of dominant two-way display that has league observers drawing comparisons to the all-time greats.

Coach Mitch Johnson had publicly said after Game 5 that the Spurs needed more from their franchise player. Wembanyama answered with perhaps his finest playoff performance, controlling the game from the opening minutes and never letting the Thunder establish any rhythm.

## What It Means for NRI Fans

The NBA has invested heavily in the Indian market in recent years. The league staged preseason games in Mumbai, has a growing streaming presence on Indian platforms, and counts millions of fans across the subcontinent. Saturday's Game 7 — Wembanyama versus Gilgeous-Alexander, with a trip to the Finals on the line — is the kind of event that transcends time zones.

For the growing Indian American basketball community, particularly the thousands who play in recreational leagues across the Bay Area, Houston, and the Northeast, the stakes are simple: the next NBA champion will be decided starting Saturday night.

Game 7 tips off Saturday evening at Paycom Center in Oklahoma City. The game will air on NBC and stream on Peacock. The winner faces the New York Knicks, who are already waiting for the Finals to begin.

The series asked one question all along: is Wembanyama ready to be the best player in the world? On Thursday, for forty-eight minutes, the answer was yes. On Saturday, against a hostile crowd and a wounded but desperate Thunder team, he will have to prove it one more time.

*Sources: Reuters, USA Today, NBC Sports, The Score*"""

    # Image sourcing — Wikipedia for Wembanyama
    print("  Sourcing image...")
    img_url = fetch_wikipedia_person_image("Victor Wembanyama")
    img_attribution = "Wikimedia Commons"
    
    if not img_url:
        img_url = fetch_pexels_image("NBA basketball game arena", "basketball court game")
        img_attribution = "The Videshi"
    
    final_img = None
    if img_url:
        art_id = str(uuid.uuid4())
        final_img = upload_to_supabase_storage(img_url, f"{art_id}.jpg")
        if not validate_image_url(final_img):
            final_img = None
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "sports",
        "vertical": "sports",
        "urgency": "medium",
        "tags": [],
        "score_total": 55,
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        
        "image_url": final_img or "",
        "image_caption": "Victor Wembanyama dominated Game 6 with twenty-eight points and ten rebounds as the Spurs forced a decisive Game 7",
        "image_attribution": img_attribution if final_img else "",
        "sources": json.dumps(["Reuters", "USA Today", "NBC Sports", "The Score"])
    }
    
    result = sb_insert("p2_articles", article)
    if result:
        art_id_db = result.get('id', 'unknown')
        print(f"  ✓ Published: {headline[:60]}... (id: {art_id_db})")
        # Upload image with article ID if we used a UUID
        if final_img and art_id_db != 'unknown' and img_url:
            new_img = upload_to_supabase_storage(img_url, f"{art_id_db}.jpg")
            if new_img and validate_image_url(new_img):
                sb_patch("p2_articles", {"id": f"eq.{art_id_db}"}, {"image_url": new_img})
                print(f"  ✓ Updated image with article ID")
    else:
        print(f"  ✗ Failed to publish article 1")
    return result

# ========================================================================
# ARTICLE 2: Indian Open of Surfing — Asian Games Selection Trials
# ========================================================================
def write_article_2():
    print("\n=== Article 2: Indian Open of Surfing ===")
    
    slug = "indian-open-surfing-2026-mangalore-asian-games-selection-trial-80-surfers-six-states-20260529"
    headline = "Eighty Surfers From Six States Are in Mangalore This Week. India's First Asian Games Surfing Squad Will Be Chosen From Among Them."
    subheadline = "The seventh Indian Open of Surfing, which begins Thursday in Mangalore, doubles as the final domestic selection trial before surfing's debut at the Aichi-Nagoya Asian Games. India has never competed in international surfing at the continental level."
    
    body = """The waves off Mangalore's Panambur Beach are not Banzai Pipeline. They are not Teahupo'o. On most days, they are modest, warm, and forgiving — the kind of breaks that taught a generation of Indian surfers how to ride before they ever heard the word "competitive."

But starting Thursday, those waves will carry the weight of history. Over eighty surfers from six Indian states have converged on the Karnataka coast for the seventh Indian Open of Surfing, a three-day event that will serve as the final and most decisive domestic selection trial before surfing's debut at the Aichi-Nagoya Asian Games later this year.

India has never sent a surfing team to the Asian Games. This week, the country will choose who goes first.

## The Selection Stakes

The Indian Open is the second stop on the National Championship Series, and the Surfing Federation of India has positioned it as the single most important event in the selection calendar. Performances here will carry significant weight when the continental squad is finalised.

The field includes Ramesh Budihal, one of India's most experienced competitive surfers, and Kamali P, the young woman from Mahabalipuram whose story — a fisherman's daughter who learned to surf on a borrowed board — has become one of Indian sport's most compelling narratives. Both are expected to contend for Asian Games berths.

The event runs across six categories: Men's Open, Women's Open, Men's Longboard, Women's Longboard, Groms Boys, and Groms Girls. For the senior categories, every heat is essentially an audition for the national team.

## A Sport Growing From the Margins

Indian surfing has no IPL. It has no billion-dollar broadcast deal. Its athletes train on beaches that double as fishing villages, and its competitions draw crowds measured in hundreds, not thousands. But the sport has grown steadily over the past decade, driven by small surf schools along the coasts of Karnataka, Tamil Nadu, Kerala, and Goa.

Mangalore — or Mangaluru, as the city is officially known — sits at the centre of India's west-coast surf culture. The Panambur and Sasihitlu breaks are well-mapped by the domestic surfing community, and the city's surf schools have produced several national-level competitors.

For the NRI community, the Asian Games debut carries particular resonance. Many Indian Americans with roots in coastal Karnataka and Kerala grew up near these waters without ever associating them with competitive sport. The idea that India's beaches could produce athletes who compete against Japan, Australia, and Indonesia — nations with deep surfing traditions — would have seemed far-fetched a decade ago.

## What the Asian Games Mean

Surfing's inclusion in the Asian Games is part of a broader push by international sporting bodies to bring the discipline into the multi-sport fold. The sport debuted at the Olympics in Tokyo 2021 and returned in Paris 2024, where wave quality at Teahupo'o produced some of the most dramatic competition in Olympic history.

At the Asian level, Japan and Indonesia are expected to dominate. Australia competes under Oceania, not Asia, removing one powerhouse from the field. But nations like the Philippines, Sri Lanka, and the Maldives have growing surf scenes, and India's entry adds another emerging nation to the mix.

The realistic expectation for India's first Asian Games surfing team is not a medal. It is presence — the act of showing up, competing, and establishing that Indian surfing exists on the continental stage. What comes after that depends on investment, infrastructure, and whether the next generation of coastal Indian kids sees surfing as a viable path.

## Three Days in Mangalore

The competition runs from May 29 through May 31, with heats scheduled across both morning and afternoon sessions to take advantage of tidal patterns. The Surfing Federation of India will use the results, combined with earlier National Championship Series performances, to finalise its Asian Games recommendations.

For the eighty-plus athletes paddling out this week, Mangalore is more than a surf break. It is the place where Indian surfing stops being a curiosity and starts becoming a competitive reality.

*Sources: LatestLY, Nation Press, IndiaSportsHub, Surfing Federation of India*"""

    # Image sourcing — Pexels for surfing
    print("  Sourcing image...")
    img_url = fetch_pexels_image("competitive surfing ocean wave", "surfer riding wave tropical")
    img_attribution = "The Videshi"
    
    final_img = None
    if img_url:
        art_id = str(uuid.uuid4())
        final_img = upload_to_supabase_storage(img_url, f"{art_id}.jpg")
        if not validate_image_url(final_img):
            final_img = None
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "sports",
        "vertical": "sports",
        "urgency": "medium",
        "tags": [],
        "score_total": 55,
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        
        "image_url": final_img or "",
        "image_caption": "India's best surfers gather in Mangalore for the selection trials that will determine the country's first Asian Games surfing team",
        "image_attribution": img_attribution if final_img else "",
        "sources": json.dumps(["LatestLY", "Nation Press", "IndiaSportsHub", "Surfing Federation of India"])
    }
    
    result = sb_insert("p2_articles", article)
    if result:
        art_id_db = result.get('id', 'unknown')
        print(f"  ✓ Published: {headline[:60]}... (id: {art_id_db})")
        if final_img and art_id_db != 'unknown' and img_url:
            new_img = upload_to_supabase_storage(img_url, f"{art_id_db}.jpg")
            if new_img and validate_image_url(new_img):
                sb_patch("p2_articles", {"id": f"eq.{art_id_db}"}, {"image_url": new_img})
                print(f"  ✓ Updated image with article ID")
    else:
        print(f"  ✗ Failed to publish article 2")
    return result

# ========================================================================
# ARTICLE 3: India U-18 Hockey Teams Begin Asia Cup in Japan
# ========================================================================
def write_article_3():
    print("\n=== Article 3: India U-18 Hockey Asia Cup ===")
    
    slug = "india-u18-hockey-asia-cup-2026-japan-kakamigahara-men-women-campaign-begins-20260529"
    headline = "India's Under-18 Hockey Teams Start Their Asia Cup Campaign in Japan Today. The Senior Pipeline Depends on What Happens Next."
    subheadline = "The men's and women's U-18 squads open their tournament in Kakamigahara against some of Asia's strongest junior programmes. For India's hockey establishment, this is where the next Olympic generation is identified."
    
    body = """When the Indian men's hockey team won bronze at the Tokyo Olympics in 2021, it ended a forty-one-year medal drought and set off a wave of investment in the sport's development pathways. Five years later, the dividends of that investment are about to be tested in Kakamigahara, Japan.

India's under-18 men's and women's hockey teams begin their Asia Cup campaigns on Thursday, facing established Asian powers in a tournament that runs through June 6. For India's hockey establishment — Hockey India, the Sports Authority of India, and the network of state academies that feed the national programme — this is where the next generation proves itself.

## The Men's Challenge

The men's squad, captained by Ketan Kushwaha, has been placed in Pool A alongside Japan, South Korea, Kazakhstan, and Chinese Taipei. The top two teams from each pool advance to the semi-finals on June 5, with the final scheduled for June 6.

Japan and South Korea present the toughest obstacles. Both nations have invested heavily in junior hockey development, and Japan's home advantage adds another layer of difficulty. India's junior programmes have historically performed well at the Asian level — the country has won the Junior Asia Cup multiple times — but consistency against East Asian opponents on their home turf has been a persistent challenge.

The squad was assembled after a national camp at the Sports Authority of India's Bhopal centre, followed by an exposure tour to Australia. That Australian trip was designed to stress-test the squad against physical, fast-paced opposition — a deliberate effort to prepare the players for the tempo they will face against Japan and Korea.

## The Women's Path

The women's team, led by captain Sweety Kujur, competes in Pool B against Malaysia, South Korea, and Singapore. India's women's hockey programme has undergone a transformation since the senior team's fourth-place finish at the Tokyo Olympics, and the under-18 pathway has benefited from that momentum.

Unlike the men's draw, the women's pool does not include a host-nation opponent, which slightly eases the challenge. But South Korea remains formidable at every age level, and Malaysia's women's programme has shown improvement in recent years.

The women's semi-finals and final follow the same June 5-6 schedule as the men's, meaning India could be competing for two continental titles on the same weekend.

## Why It Matters Beyond the Scoreboard

For NRI hockey fans — and there are more than many casual observers realise, particularly in the diaspora communities of the UK, Canada, and the Gulf states — junior tournaments are where names first surface. Several members of India's 2024 Paris Olympics squad were identified through Asia Cup performances at the under-18 and under-21 levels.

Hockey India has made the development pipeline a strategic priority since the Tokyo bronze. The formula is straightforward: identify talent early, expose it to international competition, and integrate the best performers into the senior programme before they are twenty. The Asia Cup is the primary testing ground for that formula.

Beyond the medals, the tournament serves a structural purpose. It reveals which state academies are producing the best players, which coaching methods are working, and where India's junior hockey sits relative to the rest of Asia. Those data points shape funding decisions, coaching appointments, and selection policies for years to come.

## The Week Ahead

India's men open against Kazakhstan — a manageable first assignment — before facing the stiffer tests of Japan and South Korea later in the pool stage. The women begin against Singapore, with Malaysia and South Korea to follow.

For the young athletes who have spent months at the Bhopal camp and survived the Australian tour, this is the beginning of a path that could lead to the Asian Games, the World Cup, and eventually the Olympics. That path starts in a mid-sized Japanese city that most Indian sports fans have never heard of. But the players boarding the plane to Kakamigahara know exactly what is at stake.

*Sources: Hockey India, LatestLY, Nation Press, IndiaSportsHub*"""

    # Image sourcing — Wikipedia for field hockey India or Pexels
    print("  Sourcing image...")
    img_url = fetch_pexels_image("field hockey game players", "hockey players turf stadium")
    img_attribution = "The Videshi"
    
    final_img = None
    if img_url:
        art_id = str(uuid.uuid4())
        final_img = upload_to_supabase_storage(img_url, f"{art_id}.jpg")
        if not validate_image_url(final_img):
            final_img = None
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "sports",
        "vertical": "sports",
        "urgency": "medium",
        "tags": [],
        "score_total": 55,
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        
        "image_url": final_img or "",
        "image_caption": "India's under-18 hockey squads open their Asia Cup campaign in Japan with senior team aspirations at stake",
        "image_attribution": img_attribution if final_img else "",
        "sources": json.dumps(["Hockey India", "LatestLY", "Nation Press", "IndiaSportsHub"])
    }
    
    result = sb_insert("p2_articles", article)
    if result:
        art_id_db = result.get('id', 'unknown')
        print(f"  ✓ Published: {headline[:60]}... (id: {art_id_db})")
        if final_img and art_id_db != 'unknown' and img_url:
            new_img = upload_to_supabase_storage(img_url, f"{art_id_db}.jpg")
            if new_img and validate_image_url(new_img):
                sb_patch("p2_articles", {"id": f"eq.{art_id_db}"}, {"image_url": new_img})
                print(f"  ✓ Updated image with article ID")
    else:
        print(f"  ✗ Failed to publish article 3")
    return result

# ========================================================================
# MAIN
# ========================================================================
if __name__ == '__main__':
    print(f"Sports Writer — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)
    
    results = []
    
    r1 = write_article_1()
    results.append(r1)
    
    r2 = write_article_2()
    results.append(r2)
    
    r3 = write_article_3()
    results.append(r3)
    
    published = sum(1 for r in results if r)
    print(f"\n{'=' * 60}")
    print(f"Done. {published}/{len(results)} articles published.")
