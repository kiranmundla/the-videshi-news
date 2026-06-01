#!/usr/bin/env python3
"""Entertainment writer for The Videshi — June 1, 2026 batch."""

import json, os, re, sys, time, uuid, urllib.parse
import requests

# Load env
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                if line.startswith('export '):
                    line = line[7:]
                key, val = line.split('=', 1)
                val = val.strip().strip('"').strip("'")
                os.environ[key] = val

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
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            # Prefer thumbnail (330px, always works) over originalimage (may 429 on download)
            img = data.get("thumbnail", {}).get("source") or data.get("originalimage", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
        elif r.status_code == 429:
            print(f"  ⚠ Wikipedia rate limited for '{person_name}', retrying in 3s...")
            time.sleep(3)
            r = requests.get(
                f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
                headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
                timeout=10
            )
            if r.status_code == 200:
                data = r.json()
                img = data.get("thumbnail", {}).get("source") or data.get("originalimage", {}).get("source")
                if img:
                    print(f"  ✓ Wikipedia image found (retry) for '{person_name}': {img[:80]}...")
                    return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

def fetch_pexels_image(query, fallback_query=None):
    """Fetch an image from Pexels using curl (urllib gets 403)."""
    import subprocess
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run([
                'curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
                f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=3&orientation=landscape'
            ], capture_output=True, text=True, timeout=15)
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            if photos:
                url = photos[0].get('src', {}).get('large2x') or photos[0].get('src', {}).get('original')
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def upload_image_to_supabase(image_url, filename):
    """Download image and upload to Supabase storage bucket."""
    try:
        resp = requests.get(image_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=30)
        if resp.status_code == 429:
            print(f"  ⚠ Rate limited downloading image, using direct URL")
            if 'upload.wikimedia.org' in image_url or 'images.pexels.com' in image_url:
                return image_url
            return None
        if resp.status_code != 200:
            print(f"  ⚠ Failed to download image: HTTP {resp.status_code}")
            return image_url  # fallback to original
        
        content_type = resp.headers.get('Content-Type', 'image/jpeg')
        if 'image' not in content_type:
            print(f"  ⚠ Not an image: {content_type}")
            return image_url
        
        if len(resp.content) < 5000:
            print(f"  ⚠ Image too small: {len(resp.content)} bytes")
            return image_url
        
        # Upload to Supabase storage
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        upload_resp = requests.post(
            upload_url,
            headers={
                'apikey': SUPABASE_KEY,
                'Authorization': f'Bearer {SUPABASE_KEY}',
                'Content-Type': content_type,
                'x-upsert': 'true'
            },
            data=resp.content,
            timeout=30
        )
        if upload_resp.status_code in [200, 201]:
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed: {upload_resp.status_code} {upload_resp.text[:200]}")
            # Return original URL only if it's from a permanent source
            if 'upload.wikimedia.org' in image_url or 'images.pexels.com' in image_url:
                return image_url
            return None
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        if 'upload.wikimedia.org' in image_url or 'images.pexels.com' in image_url:
            return image_url
        return None

def validate_image_url(url):
    """Validate an image URL returns HTTP 200 with image content."""
    if not url:
        return False
    try:
        resp = requests.head(url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=10, allow_redirects=True)
        if resp.status_code == 200:
            ct = resp.headers.get('Content-Type', '')
            cl = int(resp.headers.get('Content-Length', '0'))
            if 'image' in ct and cl > 5000:
                return True
            # Some servers don't return Content-Length on HEAD
            if 'image' in ct:
                return True
        # Try GET for servers that don't support HEAD well
        resp = requests.get(url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=10, stream=True)
        ct = resp.headers.get('Content-Type', '')
        cl = int(resp.headers.get('Content-Length', '0'))
        resp.close()
        return 'image' in ct and cl > 5000
    except:
        return False

def insert_article(article):
    """Insert article into Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    resp = requests.post(url, headers=HEADERS, json=article, timeout=30)
    if resp.status_code in [200, 201]:
        data = resp.json()
        art_id = data[0]['id'] if isinstance(data, list) else data.get('id')
        print(f"  ✓ Inserted: {article['headline'][:60]}... (id: {art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed: {resp.status_code} {resp.text[:300]}")
        return None


# ============================================================
# ARTICLE 1: Diljit Dosanjh Wembley Stadium announcement
# ============================================================
def write_article_1():
    print("\n=== Article 1: Diljit Dosanjh Wembley Stadium ===")
    
    slug = "diljit-dosanjh-wembley-stadium-london-first-south-asian-artist-nri-20260601"
    
    headline = "Diljit Dosanjh Just Announced a Wembley Stadium Show. No South Asian Artist Has Ever Headlined There."
    
    subheadline = "The Punjabi superstar broke the news mid-concert in Toronto, adding September 12 to his Aura World Tour. Michael Jackson, Prince, and Queen have played the venue. Now Diljit."
    
    body = """The announcement came where all the best Diljit moments come from — on stage, mid-show, in a stadium full of people losing their minds.

During his sold-out performance at Rogers Centre in Toronto on May 31, the final North American stop of his Aura World Tour, Diljit Dosanjh told the crowd he was adding a show at Wembley Stadium in London on September 12, 2026. And then he let the fact speak for itself: no South Asian artist has ever headlined the venue.

"Michael Jackson performed there. Prince performed there. The Queen's Band performs there," Diljit said from the stage. "Wembley Stadium, for the first time in the history of South Asian artists, especially Punjabis — Wembley Stadium London."

## A Tour That Keeps Getting Bigger

The Wembley addition caps what has already been the most commercially dominant tour by an Indian artist in history. The Aura World Tour, which launched in Vancouver in April, has sold out arenas across 13 North American cities — including two nights at Madison Square Garden, a venue that South Asian acts couldn't reliably fill five years ago.

In Vancouver, he drew over 50,000 fans to BC Place, making it the largest Punjabi concert ever held outside India. The tour still has California dates remaining — Crypto.com Arena in Los Angeles on June 18, and two nights at Chase Center in San Francisco on June 20-21.

Wembley Stadium seats 90,000. The London date, if it sells anywhere near capacity, would be the single largest ticketed event by an Indian artist anywhere in the world.

## What This Means for the Diaspora

For NRI audiences — especially the Punjabi and broader South Asian communities in the UK, where an estimated 1.8 million people of Indian origin live — this isn't just a concert announcement. It's a cultural marker. The UK has the largest Indian diaspora outside of the US, and Wembley has been the symbolic peak of live performance since it was rebuilt in 2007.

Diljit's crossover from Punjabi music star to global touring phenomenon has been building since his Coachella set in 2024, which made him the first Punjabi artist to perform at the festival. The Dil-Luminati Tour that followed set North American records. Now with the Aura tour, he's not just repeating the feat — he's scaling it.

## His Mother Called It

In a moment that resonated with fans who shared the clip thousands of times overnight, Diljit recalled what his mother told him growing up.

"She used to say, whenever you have a problem, something good is going to happen," he said. "I used to say, mom, I am going to a big place. I am going to Wembley Stadium. She doesn't know what Wembley Stadium is."

The quote landed because it captures something the Indian diaspora understands intuitively — the gap between where our parents imagined we could go and where some of us have actually landed.

## What's Next

Diljit's acting schedule is equally packed. His next film, *Main Vaapas Aaunga*, directed by Imtiaz Ali and co-starring Naseeruddin Shah, Sharvari, and Vedang Raina, releases theatrically in June. The film is already the most anticipated Indian title on IMDb for 2026.

Tickets and on-sale details for the Wembley show have not been announced yet, but given the pace at which his recent dates have sold, NRIs in the UK would be wise to set their alarms early.

*Sources: IANS, Ticketmaster, SeatGeek, Diljit Dosanjh's official Instagram*"""

    # Image: Wikipedia for Diljit Dosanjh
    img_url = fetch_wikipedia_person_image("Diljit Dosanjh")
    if not img_url:
        img_url = fetch_pexels_image("Wembley Stadium London concert", "music concert stadium crowd")
    
    final_img = None
    attribution = "Wikimedia Commons"
    if img_url:
        if 'upload.wikimedia.org' in img_url:
            final_img = upload_image_to_supabase(img_url, f"{slug}.jpg")
            attribution = "Wikimedia Commons"
        elif 'images.pexels.com' in img_url:
            final_img = img_url
            attribution = "Pexels"
        else:
            final_img = upload_image_to_supabase(img_url, f"{slug}.jpg")
    
    article = {
        'headline': headline,
        'subheadline': subheadline,
        'body': body,
        'slug': slug,
        'category': 'entertainment',
        'status': 'published',
        'published_at': '2026-06-01T13:00:00Z',
        'sources': json.dumps([{'name': 'IANS'}, {'name': 'Ticketmaster'}, {'name': 'SeatGeek'}, {'name': 'Diljit Dosanjh Instagram'}]),
        'vertical': 'entertainment',
        'image_url': final_img,
        'image_attribution': attribution,
        'is_editorial': False
    }
    
    art_id = insert_article(article)
    return art_id


# ============================================================
# ARTICLE 2: Peddi $700K US advance booking
# ============================================================
def write_article_2():
    print("\n=== Article 2: Peddi USA Advance Booking ===")
    
    slug = "peddi-ram-charan-usa-advance-booking-700k-north-america-nri-20260601"
    
    headline = "Ram Charan's Peddi Is at $700K in US Advance Booking. NRI Audiences Are Driving a Telugu Pre-Sale Record."
    
    subheadline = "With three days left before its June 4 release, Peddi has crossed $767K in North American premiere bookings — the strongest pre-sale for a Telugu film since RRR."
    
    body = """Three days before its theatrical debut, Ram Charan's *Peddi* has quietly become the pre-sale story of the summer for Indian cinema — and the numbers are being written entirely by audiences overseas.

As of Sunday morning, the Telugu sports action drama had crossed $692,000 in US premiere advance sales, with total North American premiere bookings reaching approximately $767,000 (roughly ₹7.33 crore), according to box office tracker Jerin Georgekutty. The film releases worldwide on June 4, with US premiere shows on June 3.

## The Numbers in Context

To understand what $700K in US pre-sales means, consider the recent landscape. *Peddi* crossed $100K in North American advance bookings within four hours of tickets going live in early May — a record for any Indian film. By mid-May, it had sold 10,000 premiere tickets.

The film's advance trajectory puts it in conversation with Ram Charan's own *RRR*, which remains the benchmark for Telugu cinema's overseas performance. If the current pace holds through Tuesday, Peddi could register one of the biggest premiere grossers for any Indian film in North America this year.

## Why NRIs Are Buying Early

The overseas appetite for *Peddi* reflects several converging factors. Ram Charan's post-RRR star power in North America has been well-documented — Telugu audiences in the US, concentrated in metros like Dallas, Chicago, the Bay Area, and the New Jersey corridor, have become the most reliable overseas ticket buyers for any Indian-language cinema.

The film also has A.R. Rahman scoring the music and background, with Buchi Babu Sana (who directed the acclaimed *Uppena*) helming the project. The rural sports drama genre — a combination that worked spectacularly for *Dangal* and *83* — has cross-demographic appeal.

## A Packed Weekend Ahead

*Peddi* releases into a June first week that's already one of the busiest of 2026. Varun Dhawan's *Hai Jawani Toh Ishq Hona Hai* moved to June 12 to avoid the clash. But the Telugu film still faces holdover competition from *Drishyam 3* (which has crossed ₹225 crore worldwide) and the Hollywood slate.

The real question isn't whether *Peddi* will open big — it will. With a reported ₹350 crore budget, the question is whether it can sustain past the premiere rush. To break even, trade analysts estimate the film needs approximately ₹450 crore worldwide.

The cast — which includes Janhvi Kapoor, Shiva Rajkumar, Jagapathi Babu, Divyenndu, and Boman Irani — gives it multi-market appeal. The film releases in standard, IMAX, Dolby Cinema, 4DX, and several premium formats, maximizing per-ticket revenue.

## What Peddi Tells Us About the NRI Box Office

For the diaspora audience, especially Telugu-speaking families in the US, premiere night has evolved from a movie outing into a community event. Theatres in cities like Frisco, Dallas, and Edison now routinely program 4 AM and 7 AM fan shows for Indian tentpoles. *Peddi* is no exception — many of these early shows are already sold out.

It's a dynamic that Indian studios have learned to engineer for, and it's reshaping how films are marketed, released, and monetized in North America.

*Sources: Filmibeat, Sacnilk, ZoomTV Entertainment, Wikipedia*"""

    # Image: Wikipedia for Ram Charan
    img_url = fetch_wikipedia_person_image("Ram Charan")
    if not img_url:
        img_url = fetch_wikipedia_person_image("Ram Charan (actor)")
    if not img_url:
        img_url = fetch_pexels_image("Indian cinema movie premiere", "Telugu cinema audience")
    
    final_img = None
    attribution = "Wikimedia Commons"
    if img_url:
        if 'upload.wikimedia.org' in img_url:
            final_img = upload_image_to_supabase(img_url, f"{slug}.jpg")
            attribution = "Wikimedia Commons"
        elif 'images.pexels.com' in img_url:
            final_img = img_url
            attribution = "Pexels"
        else:
            final_img = upload_image_to_supabase(img_url, f"{slug}.jpg")
    
    article = {
        'headline': headline,
        'subheadline': subheadline,
        'body': body,
        'slug': slug,
        'category': 'entertainment',
        'status': 'published',
        'published_at': '2026-06-01T13:05:00Z',
        'sources': json.dumps([{'name': 'Filmibeat'}, {'name': 'Sacnilk'}, {'name': 'ZoomTV Entertainment'}, {'name': 'Wikipedia'}]),
        'vertical': 'entertainment',
        'image_url': final_img,
        'image_attribution': attribution,
        'is_editorial': False,
        
    }
    
    art_id = insert_article(article)
    return art_id


# ============================================================
# ARTICLE 3: Drishyam 3 overseas vs domestic — NRI angle
# ============================================================
def write_article_3():
    print("\n=== Article 3: Drishyam 3 Box Office NRI angle ===")
    
    slug = "drishyam-3-overseas-beats-domestic-225-crore-worldwide-mohanlal-nri-20260601"
    
    headline = "Drishyam 3's Overseas Collections Have Outpaced India. That's Never Happened for a Malayalam Thriller."
    
    subheadline = "Mohanlal's franchise closer has crossed ₹225 crore worldwide in 11 days. The diaspora — Gulf, US, UK, Australia — has contributed more than Kerala."
    
    body = """Here's a statistic that would have been inconceivable five years ago: *Drishyam 3*, a Malayalam-language crime thriller, has earned more money outside India than inside it.

After 11 days of theatrical release, Jeethu Joseph's franchise closer has grossed approximately ₹228.95 crore worldwide. Of that, overseas markets — led by the Gulf, North America, the UK, and Australia — have contributed roughly ₹114 crore. The India gross stands at about ₹110 crore (₹96.70 crore net). It's the first time a Malayalam thriller has had its overseas total outpace its domestic one.

## The Gulf Connection

The numbers make sense when you map them against the Malayalam-speaking diaspora. The Gulf Cooperation Council countries alone are home to an estimated 2.5 million Malayalis — nurses, engineers, IT workers, and business owners who have been the bedrock of Kerala's remittance economy for decades. For this audience, *Drishyam 3* isn't just a movie. It's a shared cultural text.

The franchise has a unique relationship with overseas audiences. The original *Drishyam* (2013) became one of the most remade Indian films — spawning Hindi, Telugu, Tamil, Kannada, and even Chinese adaptations. Its premise — a working-class father who outsmarts the police to protect his family — resonated universally, but it hit particularly hard in the Gulf, where many viewers saw their own vulnerability and resourcefulness mirrored in Georgekutty.

## A Mixed-Reviews Blockbuster

What makes the commercial performance more remarkable is that *Drishyam 3* has received mixed critical reception. Unlike the universally acclaimed first two installments, reviews for the third chapter have been divided. Yet the audience has shown up regardless — opening day alone saw 587,000 tickets sold on BookMyShow, shattering the previous Day 1 record held by *Thudarum* (430,000).

The film has crossed the 3 million ticket mark on BookMyShow in just 11 days, placing it among the top seven Malayalam films ever on the platform. Only *Lokah Chapter 1* (5.5 million) sits significantly ahead.

## What It Means for Malayalam Cinema's Business Model

The overseas-heavy revenue split signals a structural shift. Malayalam cinema has traditionally been a domestic-first industry, with the Gulf as a reliable but secondary market. But a succession of global hits — *Manjummel Boys*, *Lokah Chapter 1*, *Thudarum*, *Vaazha 2*, and now *Drishyam 3* — has established a new paradigm where overseas revenue can match or exceed India collections.

For NRI audiences, the implication is straightforward: studios are now marketing and releasing with you in mind, not as an afterthought. Simultaneous dubbed releases in Tamil, Telugu, and Kannada — which *Drishyam 3* has for the first time — are designed to capture pan-Indian diaspora audiences who might not speak Malayalam but know the franchise from its remakes.

## The Hindi Remake Is Coming

The financial success of the original virtually guarantees that Ajay Devgn's *Drishyam 3* Hindi remake, which is already in production, will arrive as scheduled on October 2, 2026. The remake franchise has its own massive following — the Hindi *Drishyam 2* earned over ₹240 crore worldwide.

But the Malayalam original has now established that it doesn't need the Hindi version to access a global audience. That's the real story.

## Box Office Breakdown (11 Days)

- **India Net**: ₹96.70 crore
- **India Gross**: ~₹110.75 crore
- **Overseas Gross**: ~₹114.10 crore
- **Worldwide Gross**: ₹228.95 crore (approx.)
- **Budget**: ₹60 crore (reported)
- **ROI**: ~275%

*Sources: Sacnilk, BoxOfficeWala, Hollywood Reporter India, Livemint, Wikipedia*"""

    # Image: Wikipedia for Mohanlal
    img_url = fetch_wikipedia_person_image("Mohanlal")
    if not img_url:
        img_url = fetch_pexels_image("Indian cinema audience theater", "movie theater audience India")
    
    final_img = None
    attribution = "Wikimedia Commons"
    if img_url:
        if 'upload.wikimedia.org' in img_url:
            final_img = upload_image_to_supabase(img_url, f"{slug}.jpg")
            attribution = "Wikimedia Commons"
        elif 'images.pexels.com' in img_url:
            final_img = img_url
            attribution = "Pexels"
        else:
            final_img = upload_image_to_supabase(img_url, f"{slug}.jpg")
    
    article = {
        'headline': headline,
        'subheadline': subheadline,
        'body': body,
        'slug': slug,
        'category': 'entertainment',
        'status': 'published',
        'published_at': '2026-06-01T13:10:00Z',
        'sources': json.dumps([{'name': 'Sacnilk'}, {'name': 'BoxOfficeWala'}, {'name': 'Hollywood Reporter India'}, {'name': 'Livemint'}, {'name': 'Wikipedia'}]),
        'vertical': 'entertainment',
        'image_url': final_img,
        'image_attribution': attribution,
        'is_editorial': False,
        
    }
    
    art_id = insert_article(article)
    return art_id


# ============================================================
# Run all
# ============================================================
if __name__ == '__main__':
    print("=" * 60)
    print("The Videshi Entertainment Writer — June 1, 2026")
    print("=" * 60)
    
    results = []
    
    art1 = write_article_1()
    results.append(('Diljit Wembley', art1))
    
    time.sleep(2)  # Avoid Wikipedia rate limiting
    
    art2 = write_article_2()
    results.append(('Peddi USA Booking', art2))
    
    time.sleep(2)  # Avoid Wikipedia rate limiting
    
    art3 = write_article_3()
    results.append(('Drishyam 3 Overseas', art3))
    
    print("\n" + "=" * 60)
    print("RESULTS:")
    for name, aid in results:
        status = "✓" if aid else "✗"
        print(f"  {status} {name}: {aid}")
    
    successes = sum(1 for _, a in results if a)
    print(f"\n{successes}/{len(results)} articles published successfully.")
    print("=" * 60)
