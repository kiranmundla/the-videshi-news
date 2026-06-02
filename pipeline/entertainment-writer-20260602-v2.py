#!/usr/bin/env python3
"""Entertainment writer - June 2, 2026 batch (v2 - fixed vertical + image handling)"""

import json, os, sys, time, subprocess
import requests
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    import urllib.parse
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            # Use thumbnail (330px) to avoid Wikimedia 429/400 on large originals
            img = data.get("thumbnail", {}).get("source") or data.get("originalimage", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

def fetch_pexels_image(query, fallback_query=None):
    """Fetch image from Pexels API using curl."""
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
                 f'https://api.pexels.com/v1/search?query={requests.utils.quote(q)}&per_page=3&orientation=landscape'],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            if photos:
                url = photos[0]['src']['large2x']
                print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def upload_image_to_supabase(img_url, filename):
    """Download image and upload to Supabase storage bucket."""
    try:
        # Use curl for download to avoid Python request issues
        result = subprocess.run(
            ['curl', '-sS', '-L', '-o', f'/tmp/{filename}',
             '-H', 'User-Agent: TheVideshi/1.0 (thevideshi.com)',
             '-w', '%{http_code}|%{size_download}|%{content_type}',
             img_url],
            capture_output=True, text=True, timeout=30
        )
        parts = result.stdout.strip().split('|')
        http_code = parts[0] if parts else '0'
        file_size = int(parts[1]) if len(parts) > 1 else 0
        content_type = parts[2] if len(parts) > 2 else 'image/jpeg'

        if http_code not in ['200', '301', '302'] or file_size < 5000:
            print(f"  ⚠ Download issue: HTTP {http_code}, size {file_size}")
            # For Wikimedia/Pexels URLs, use directly (they're permanent)
            if 'upload.wikimedia.org' in img_url or 'images.pexels.com' in img_url:
                return img_url
            return None

        if 'image' not in content_type:
            content_type = 'image/jpeg'

        # Upload to Supabase
        with open(f'/tmp/{filename}', 'rb') as f:
            img_data = f.read()

        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        upload_headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': content_type,
            'x-upsert': 'true'
        }
        up = requests.post(upload_url, headers=upload_headers, data=img_data, timeout=20)
        if up.status_code in [200, 201]:
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {filename}")
            return public_url
        else:
            print(f"  ⚠ Upload failed: {up.status_code}")
            if 'upload.wikimedia.org' in img_url or 'images.pexels.com' in img_url:
                return img_url
            return None
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        if 'upload.wikimedia.org' in img_url or 'images.pexels.com' in img_url:
            return img_url
        return None

def insert_article(article):
    """Insert article into Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    r = requests.post(url, headers=HEADERS, json=article, timeout=30)
    if r.status_code in [200, 201]:
        data = r.json()
        art_id = data[0]['id'] if isinstance(data, list) and data else data.get('id')
        print(f"  ✓ Published: {article['headline'][:60]}... (id: {art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed: {r.status_code} {r.text[:500]}")
        return None

def count_words(text):
    return len(text.split())

# ============================================================
# ARTICLE 1: Zee FIFA World Cup Deal
# ============================================================
print("\n=== ARTICLE 1: Zee FIFA World Cup 2026 ===")

art1_slug = "zee-entertainment-fifa-world-cup-2026-india-broadcast-unite8-sports-nri-20260602"
art1_headline = "Zee Just Grabbed the FIFA World Cup. Ten Days Before Kickoff, India Finally Has a Broadcaster."
art1_subheadline = "After months of failed negotiations with JioStar and Sony, Zee Entertainment locked 39 FIFA events through 2034 — including the World Cup happening in your NRI backyard."

art1_body = """The biggest football tournament in history is coming to the United States, Canada, and Mexico. And until Monday, nobody in India could watch it.

Zee Entertainment ended a months-long standoff by securing the broadcast rights to the 2026 FIFA World Cup and 38 other FIFA events through 2034. The deal, confirmed just 10 days before the June 11 kickoff, resolves what had become an embarrassing stalemate — India was one of the last major markets on earth without a confirmed World Cup broadcaster.

## How the Deal Almost Didn't Happen

FIFA originally wanted $100 million for the India package covering the 2026 and 2030 World Cups. When that didn't fly, they slashed the ask to $60 million. JioStar — the Reliance-Disney joint venture that aired the 2022 World Cup through Viacom18 — offered roughly $20 million. FIFA rejected it. Sony, which broadcast the 2014 and 2018 tournaments, held discussions but never placed a bid.

The result was a standoff that lasted well into 2026, with a billion cricket-loving people seemingly indifferent to the fact that the world's most-watched sporting event had no Indian home. Zee stepped in and closed somewhere between $25 million and $80 million — far below FIFA's opening ask, but enough to break the logjam.

## What Zee Gets

This isn't a one-tournament deal. Zee locked in an eight-year package covering 39 FIFA events:

The 2026 and 2030 FIFA World Cups. The 2027 FIFA Women's World Cup. Every U-17 and U-20 World Cup through 2034. Futsal World Cups, the Intercontinental Cup, and FIFA docu-series content.

To deliver all of this, Zee is launching four new channels under the Unite8 Sports brand — Unite8 Sports 1 and 2 in Hindi and English, plus HD variants. The matches will also stream on ZEE5.

Zee's stock surged approximately 7% on the news.

## Why NRIs Should Care More Than Anyone

Here's the detail that makes this story distinctly diaspora: the 2026 World Cup is being played in 16 cities across the United States, Canada, and Mexico. MetLife Stadium in New Jersey. AT&T Stadium in Dallas. SoFi in Los Angeles. BMO Field in Toronto. Estadio Azteca in Mexico City.

For millions of Indian Americans and Canadians, this is the first World Cup in their time zone, in their cities, at venues they can actually drive to. India didn't qualify for the tournament, but the cultural moment is unavoidable — every desi WhatsApp group will be buzzing with watch party plans by June 11.

The broadcast deal means family back home can watch simultaneously. That's the real connector.

## The Bigger Picture for Indian Sports Broadcasting

JioStar currently dominates Indian sports media. It holds the IPL, English Premier League, and a massive portfolio of cricket rights. Zee's FIFA acquisition is a direct play at the one global sport where JioStar's grip is weakest.

Football fandom in India has been growing steadily — the ISL expanded, European league viewership rose, and the 2022 Qatar World Cup drew record Indian audiences. Zee is betting that 2026, played at NRI-friendly hours across North American time zones, will be the inflection point.

Whether this deal makes financial sense for Zee depends entirely on advertising revenue and ZEE5 subscriptions during the tournament window. But strategically, it positions the company as India's football home — and with 39 events over eight years, that's a long runway.

The first match kicks off June 11. For the first time, the diaspora won't need a VPN to share the moment with home."""

# Image
img1_url = fetch_pexels_image("FIFA World Cup football stadium crowd", "football soccer stadium fans")
img1_attribution = "The Videshi"
img1_final = None
if img1_url:
    img1_final = upload_image_to_supabase(img1_url, f"{art1_slug}.jpg")

art1 = {
    "headline": art1_headline,
    "subheadline": art1_subheadline,
    "body": art1_body,
    "slug": art1_slug,
    "category": "entertainment",
    "vertical": "entertainment",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": img1_final,
    "image_attribution": img1_attribution if img1_final else None,
    "is_editorial": False,
    "word_count": count_words(art1_body),
    "sources": [
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "BestMediaInfo", "url": "https://www.bestmediainfo.com"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com"},
        {"name": "LiveMint", "url": "https://www.livemint.com"}
    ]
}

id1 = insert_article(art1)

# ============================================================
# ARTICLE 2: Patriot on ZEE5
# ============================================================
print("\n=== ARTICLE 2: Patriot on ZEE5 ===")
time.sleep(2)  # Rate limit spacing for Wikipedia

art2_slug = "patriot-mammootty-mohanlal-fahadh-faasil-zee5-june-5-spy-thriller-nri-20260602"
art2_headline = "Mammootty and Mohanlal Share a Screen for the First Time in Years. Patriot Hits ZEE5 Thursday."
art2_subheadline = "The three-hour Malayalam spy thriller — with Fahadh Faasil and Nayanthara in tow — was a theatrical blockbuster. Now it's coming to your living room."

img2_url = fetch_wikipedia_person_image("Mammootty")
img2_attribution = "Wikimedia Commons"
if not img2_url:
    time.sleep(1)
    img2_url = fetch_wikipedia_person_image("Mohanlal")
if not img2_url:
    img2_url = fetch_pexels_image("Indian cinema spy thriller dark")
    img2_attribution = "The Videshi"

img2_final = None
if img2_url:
    img2_final = upload_image_to_supabase(img2_url, f"{art2_slug}.jpg")

art2_body = """There are film events, and then there are events that redefine what a film industry can achieve. Patriot — the spy thriller that put Mammootty and Mohanlal in the same frame for the first time in over a decade — starts streaming on ZEE5 this Thursday, June 5. And if you missed the theatrical run, you missed something historic.

## The Cast That Shouldn't Exist on One Poster

Mammootty. Mohanlal. Fahadh Faasil. Nayanthara. Kunchacko Boban. Directed by Mahesh Narayanan, who earned his reputation with C U Soon and Malik.

In any other film industry, assembling even two of these names would be a headline. Getting all five — with Mammootty and Mohanlal together, something Malayalam cinema has barely seen in recent memory — required the kind of gravitational pull that only a script of genuine ambition could generate.

Mammootty plays Dr. Daniel James, an intelligence operative who stumbles onto a surveillance project threatening civil liberties at a national scale. The premise sounds familiar until you realize that Mahesh Narayanan's version of a spy thriller is less about car chases and more about the machinery of the state turning on its own citizens.

## What Happened at the Box Office

Patriot didn't just open well — it opened like a cultural event. Advance bookings in Kerala sold 85,000 tickets within hours of going live on April 28, worth over 1.5 crore rupees. Overseas pre-sales crossed $200,000 before the first domestic show even ran.

The final theatrical verdict was clear: certified blockbuster. The film ran for three hours and audiences stayed. Internationally, it performed particularly well in GCC markets, the UK, and North America — the exact corridors where the Malayalam diaspora concentrates.

The film carries an IMDB rating of 6.6, which for a three-hour Malayalam spy drama that grapples with surveillance ethics suggests it's the kind of film that divides casual viewers but deeply rewards those willing to engage.

## Why the Diaspora Angle Matters

Malayalam cinema has been quietly outperforming its weight class on OTT platforms for years. From Drishyam to Minnal Murali, from Malik to 2018, the industry's best work travels globally because it consistently chooses substance over spectacle.

Patriot continues that tradition. But it also represents something the diaspora specifically responds to: a film about the tension between national security and individual rights, set in a world where the watchers are being watched. For NRIs navigating visa bureaucracies, surveillance debates, and the complex relationship between Indian institutions and their citizens abroad, the thematic resonance runs deeper than entertainment.

## The ZEE5 Factor

The OTT release will be available in Malayalam, Telugu, Hindi, Tamil, and Kannada — five languages that cover essentially every Indian diaspora pocket globally. ZEE5 has been aggressively acquiring South Indian blockbusters, and Patriot is the crown jewel of their June lineup.

Also hitting ZEE5 on the same day: Brown, starring Karisma Kapoor as a disgraced Kolkata cop hunting a serial killer, and KD The Devil, a Kannada period crime thriller with Dhruva Sarja and Sanjay Dutt. It's a stacked Thursday.

But Patriot is the one you watch first. When Mammootty and Mohanlal decide to work together, you show up."""

art2 = {
    "headline": art2_headline,
    "subheadline": art2_subheadline,
    "body": art2_body,
    "slug": art2_slug,
    "category": "entertainment",
    "vertical": "entertainment",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": img2_final,
    "image_attribution": img2_attribution if img2_final else None,
    "is_editorial": False,
    "word_count": count_words(art2_body),
    "sources": [
        {"name": "Sacnilk", "url": "https://www.sacnilk.com"},
        {"name": "Zoom TV Entertainment", "url": "https://www.zoomtventertainment.com"},
        {"name": "FilmiBeat", "url": "https://www.filmibeat.com"}
    ]
}

id2 = insert_article(art2)

# ============================================================
# ARTICLE 3: Rajamouli's Varanasi
# ============================================================
print("\n=== ARTICLE 3: Rajamouli's Varanasi ===")
time.sleep(2)

art3_slug = "rajamouli-varanasi-mahesh-babu-priyanka-chopra-time-travel-epic-march-2027-nri-20260602"
art3_headline = "Rajamouli Is Spending ₹1,300 Crore on a Time-Travel Epic. Priyanka Chopra Holds a Gun in a Saree. This Is Varanasi."
art3_subheadline = "The RRR director, Mahesh Babu, and a global cast are shooting across Africa and Antarctica for a March 2027 release that aims to outscale everything Indian cinema has ever attempted."

img3_url = fetch_wikipedia_person_image("S. S. Rajamouli")
img3_attribution = "Wikimedia Commons"
if not img3_url:
    time.sleep(1)
    img3_url = fetch_wikipedia_person_image("Mahesh Babu")
if not img3_url:
    img3_url = fetch_pexels_image("ancient Varanasi India temple sunrise", "Indian temple spiritual dawn")
    img3_attribution = "The Videshi"

img3_final = None
if img3_url:
    img3_final = upload_image_to_supabase(img3_url, f"{art3_slug}.jpg")

art3_body = """Every few years, Indian cinema produces a project so absurdly ambitious that the industry collectively holds its breath. Baahubali was one. RRR was another. Now comes Varanasi — S.S. Rajamouli's time-travel action epic starring Mahesh Babu, Priyanka Chopra Jonas, and Prithviraj Sukumaran — and the scale has escalated beyond anything previously attempted. The budget stands at a reported ₹1,300 crore.

## What We Know About the Plot

In a recent global interview with DiscussingFilm, the lead cast revealed details that place Varanasi firmly in uncharted territory for Indian filmmaking.

Mahesh Babu plays Rudhra, a fervent devotee of Lord Shiva who is sent on a perilous mission through time to secure an ancient cosmic artifact. The narrative blends ancient Indian mythology with futuristic science fiction — think less superhero movie, more Christopher Nolan by way of the Mahabharata.

Priyanka Chopra plays Mandakini. Her first-look poster — saree, gun, fierce expression — has already become one of the most discussed images in Indian cinema this year. This marks her return to Indian cinema after 2019's The Sky Is Pink, and the role appears designed to be anything but ornamental.

Prithviraj Sukumaran plays Kumbha, the antagonist — described as a brilliant but evil mastermind intent on using the cosmic artifact for global domination.

The screenplay comes from Rajamouli and his father V. Vijayendra Prasad, the same partnership that built the Baahubali universe and crafted RRR's unlikely Oscar-winning trajectory.

## The Production Is Genuinely Global

This isn't a film that shoots in Mumbai and adds international locations for songs. The production has already filmed in Odisha, using the hills and plateaus of Koraput as a backdrop. The team has shot extensively across East Africa — Kenya's forests and the savanna providing the setting for intense action sequences in wild and dense terrain. Rajamouli personally scouted locations across the continent.

But the real headline came from a social media exchange in March where Priyanka Chopra responded to Mahesh Babu with the words: "See you soon in Antarctica." Antarctica. For an Indian film.

The production plans to shoot throughout 2026 across multiple international locations. Originally rumored to be a two-part saga in the Baahubali mold, reports now indicate Rajamouli has opted for a single film with an extended runtime. Given that RRR ran three hours and nobody complained, this feels right.

## A 15-Year Collaboration in the Making

Mahesh Babu revealed in the DiscussingFilm interview that he first met Rajamouli long before the Baahubali franchise existed. The collaboration was discussed, delayed, discussed again, delayed by the pandemic, delayed by RRR's production and global promotion tour. When Mahesh finally heard the full narration after RRR's release, he described feeling nervousness at the sheer scale of the vision.

The title itself — Varanasi, after India's most ancient and sacred city — was officially unveiled at the GlobeTrotter event in Hyderabad in November 2025. The first glimpse showed Mahesh Babu riding a massive white Nandi bull, kicking up clouds of sand in a dramatic, temple-filled backdrop. The imagery immediately confirmed that Varanasi draws deeply from Hindu mythology while pushing into science fiction territory.

## Why the Diaspora Is Already Invested

For NRIs who grew up watching Mahesh Babu mature from the prince of Telugu cinema into a genuine superstar, Varanasi represents the role they've been waiting to see him play on the world stage. For those who followed Priyanka Chopra's Hollywood journey and wondered when she'd return to Indian cinema with something worthy, this appears to be the answer.

The March 2027 release window puts Varanasi in direct proximity to major Hollywood releases, which is itself a statement of intent. Rajamouli doesn't dodge competition — after RRR's global run, which included an Oscar, a Golden Globe nomination, and a Japanese box office surprise, he actively seeks it.

Multiple languages confirmed. Global theatrical release. And a filmmaker who has never once under-delivered on his ambitions.

Mark the date: March 25, 2027. The countdown to Indian cinema's next global event has begun."""

art3 = {
    "headline": art3_headline,
    "subheadline": art3_subheadline,
    "body": art3_body,
    "slug": art3_slug,
    "category": "entertainment",
    "vertical": "entertainment",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": img3_final,
    "image_attribution": img3_attribution if img3_final else None,
    "is_editorial": False,
    "word_count": count_words(art3_body),
    "sources": [
        {"name": "Sacnilk", "url": "https://www.sacnilk.com"},
        {"name": "Pinkvilla", "url": "https://www.pinkvilla.com"},
        {"name": "DiscussingFilm (via Sacnilk)", "url": "https://www.sacnilk.com"},
        {"name": "Filmfare", "url": "https://www.filmfare.com"}
    ]
}

id3 = insert_article(art3)

# ============================================================
# Summary
# ============================================================
print("\n=== SUMMARY ===")
results = [(art1_headline, id1), (art2_headline, id2), (art3_headline, id3)]
for headline, aid in results:
    status = "✓" if aid else "✗"
    print(f"  {status} {headline[:70]}...")
print(f"\nTotal published: {sum(1 for _, a in results if a)}/{len(results)}")

successful = sum(1 for _, a in results if a)
if successful < len(results):
    sys.exit(1)
