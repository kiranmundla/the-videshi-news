#!/usr/bin/env python3
"""Entertainment writer for The Videshi - 2026-06-02 run"""

import json, os, re, sys, time, uuid, urllib.parse, subprocess
from datetime import datetime, timezone

# Load env
def load_env(filepath):
    if not os.path.exists(filepath):
        return
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, _, val = line.partition('=')
                key = key.strip().replace('export ', '')
                val = val.strip().strip('"').strip("'")
                os.environ[key] = val

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

import requests

def sb_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

def sb_insert(table, data):
    r = requests.post(f"{SUPABASE_URL}/rest/v1/{table}", json=data, headers=sb_headers(), timeout=30)
    if r.status_code in (200, 201):
        return r.json()
    else:
        print(f"  ✗ Supabase insert error: {r.status_code} - {r.text[:300]}")
        return None

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
    """Fetch an image from Pexels. Use curl because Python urllib gets 403."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
                 f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=3'],
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
    """Download image and upload to Supabase storage bucket 'article-images'."""
    try:
        r = requests.get(img_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=20)
        if r.status_code != 200 or len(r.content) < 5000:
            print(f"  ⚠ Image download failed or too small: {r.status_code}, {len(r.content)} bytes")
            return img_url  # Fall back to direct URL
        
        content_type = r.headers.get('Content-Type', 'image/jpeg')
        if 'image' not in content_type:
            content_type = 'image/jpeg'
        
        upload_headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": content_type,
            "x-upsert": "true"
        }
        up = requests.post(
            f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}",
            data=r.content,
            headers=upload_headers,
            timeout=30
        )
        if up.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Supabase upload error: {up.status_code} - {up.text[:200]}")
            return img_url
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        return img_url

def validate_image_url(url):
    """Check that URL returns a valid image."""
    if not url:
        return False
    try:
        r = requests.head(url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=10, allow_redirects=True)
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct and cl > 5000:
            return True
        # Try GET for servers that don't support HEAD
        r = requests.get(url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=10, stream=True)
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        return r.status_code == 200 and 'image' in ct
    except:
        return False

# ──────────────────────────────────────────
# ARTICLES
# ──────────────────────────────────────────

articles = []

# ─── ARTICLE 1: Peddi — Ram Charan's biggest solo bet arrives Wednesday ───

articles.append({
    "headline": "Ram Charan's Peddi Arrives Wednesday With $700K in US Pre-Sales. The Diaspora Is Treating It Like an Event.",
    "subheadline": "A.R. Rahman's score, IMAX screens, and a ₹450 crore break-even target. Ram Charan's biggest solo release since RRR opens in two days — and NRI audiences are already buying in.",
    "slug": "peddi-ram-charan-700k-us-presales-imax-ar-rahman-diaspora-nri-20260602",
    "category": "entertainment",
    "image_person": "Ram Charan",
    "image_fallback_query": "Telugu cinema Ram Charan",
    "sources": [
        {"name": "Sacnilk", "url": "https://sacnilk.com"},
        {"name": "Filmibeat", "url": "https://filmibeat.com"},
        {"name": "Zoom TV Entertainment", "url": "https://zoomtventertainment.com"},
        {"name": "Filmfare", "url": "https://filmfare.com"}
    ],
    "body": """Ram Charan's sports-action drama *Peddi* opens worldwide on Wednesday, June 4, and the numbers arriving from North America suggest the diaspora has already decided this is the Telugu event of the summer.

## The Advance Booking Story

As of Sunday, US premiere advance sales had crossed $692,000, with overall North American pre-sales approaching $767,000 — roughly ₹7.33 crore before a single reel has spun. The film became the fastest Indian release to cross $100,000 in North American pre-sales, hitting that mark within four hours of bookings opening in mid-May. Hundreds of premiere shows are planned across the US and Canada, and the trajectory suggests Peddi could challenge RRR's premiere benchmarks for a Telugu film in the region.

For the NRI audience that made RRR a cultural moment in American multiplexes, this is the payoff. Ram Charan's post-RRR star power is being tested as a standalone commodity for the first time — without the Rajamouli brand, without the Jr. NTR pairing, without the Hollywood distribution machinery that put RRR on the global map.

## What's at Stake

The production economics are steep. Directed by Buchi Babu Sana (*Uppena*), *Peddi* is co-produced by Vriddhi Cinemas, Mythri Movie Makers, Sukumar Writings, and IVY Entertainment, with Jio Studios handling North India distribution. Trade analysts estimate the film needs approximately ₹450 crore worldwide to break even — a figure that would make it Ram Charan's biggest solo grosser and his second-largest overall after RRR.

The film tells the story of Peddi Raju, a young daily-wage worker at construction sites whose athletic talent becomes his ticket out. Janhvi Kapoor plays the female lead, with Shiva Rajkumar, Jagapathi Babu, and Divyenndu rounding out a cast that spans Telugu, Kannada, and Hindi cinema.

## The A.R. Rahman Factor

The music, composed by A.R. Rahman, has already found traction — the songs have been in rotation across Indian diaspora playlists for weeks, and the background score is being positioned as one of Rahman's most emotionally layered since *Roja*. For NRI audiences who grew up on Rahman soundtracks, this is both nostalgia and novelty. Cinematography by Ratnavelu, editing by Navin Nooli, and visual effects supervised by Sanath PC complete a technical crew that signals blockbuster ambition.

## IMAX and the Premium Play

Peddi has been confirmed for an IMAX release, with Preetham Daniel, IMAX's Vice President for India and surrounding regions, publicly announcing the premium format rollout. This puts the film in direct competition for large-format screens with *Masters of the Universe*, which opens on IMAX just one day later on June 5. For diaspora audiences willing to pay the IMAX premium, Wednesday night becomes a genuine event.

## The Week Ahead

The first weekend of June is unusually crowded. Yash's *Toxic: A Fairy Tale for Grown-ups* opens the same day as Peddi. Bobby Deol's *Bandar* and Varun Dhawan's *Hai Jawani Toh Ishq Hona Hai* follow on June 5. But in North America, where Telugu cinema audiences are fiercely loyal and screen allocation favours whoever books first, Peddi has a clear head start.

The question isn't whether Peddi will open big — the advance numbers have already answered that. The question is whether Ram Charan, without a director whose name alone sells tickets, can sustain the kind of run that turns a ₹450 crore target from daunting into inevitable."""
})


# ─── ARTICLE 2: Bollywood's Missing Middle ───

articles.append({
    "headline": "Bollywood's Middle Ground Is Vanishing. The Box Office Data Proves It.",
    "subheadline": "Dhurandhar 2 earned ₹1,850 crore. Fourteen other films from Q1 2026 earned less than ₹50 crore combined. The Indian film industry's binary reality is no longer a theory — it's the balance sheet.",
    "slug": "bollywood-box-office-2026-missing-middle-dhurandhar-flops-analysis-nri-20260602",
    "category": "entertainment",
    "image_person": None,
    "image_fallback_query": "Bollywood cinema theatre India",
    "sources": [
        {"name": "Sacnilk", "url": "https://sacnilk.com"},
        {"name": "Koimoi", "url": "https://koimoi.com"},
        {"name": "Bollywood Hungama", "url": "https://bollywoodhungama.com"}
    ],
    "body": """The numbers from the first half of 2026 tell a story that Bollywood has been whispering about for two years and can no longer avoid saying out loud. The middle of the market — the ₹50-150 crore zone where decent films used to build decent careers — has effectively disappeared.

## The Data

Consider the top of the chart. Ranveer Singh's *Dhurandhar 2: The Revenge* has earned approximately ₹1,850 crore worldwide, entering the top 10 highest-grossing films globally in 2026 — a feat virtually unheard of for an Indian production. *Border 2* collected ₹485 crore. *Bhooth Bangla*, Akshay Kumar's horror-comedy, crossed ₹289 crore. Together, these three films account for over ₹2,600 crore of Bollywood's total 2026 gross.

Now consider the rest. *O'Romeo* (₹123 crore, verdict: "Losing"). *Mardaani 3* (₹77 crore, "Losing"). *Ikkis* (₹46 crore, "Losing"). Then the cliff: *Chand Mera Dil* (₹34 crore), *Pati Patni Aur Woh Do* (₹65 crore), and a graveyard of titles — *Ek Din*, *Ginny Wedss Sunny 2*, *Do Deewane Seher Mein*, *Tu Yaa Main*, *Rahu Ketu*, *Happy Patel*, *Vadh 2*, *Bhabiji Ghar Par Hain* — each earning between ₹1.5 crore and ₹15 crore. Virtually all carry a "Flop" verdict.

The pattern is binary. You're either above ₹200 crore or below ₹50 crore. The zone between — where mid-budget dramas, rom-coms, and character studies once found a sustainable audience — has been hollowed out.

## What Killed the Middle

Three forces converged simultaneously.

**Franchise dominance.** The success of *Dhurandhar 2* and *Bhooth Bangla* proved that audiences will pay premium prices and make repeat visits for event-scale franchise properties. This pulls discretionary spending away from films that audiences perceive as "can wait for OTT." The theatrical window is now a luxury good, not a democratic marketplace.

**OTT as safety net, then as executioner.** Streaming platforms initially saved mid-budget films by offering digital premieres at guaranteed minimums. But the abundance of streaming content has conditioned audiences to expect mid-tier films at home within weeks. The theatrical window for a ₹30-60 crore film is now functionally two weekends — and if the first weekend underperforms, multiplexes replace it with the franchise tentpole that's still drawing crowds.

**Cost inflation without revenue expansion.** Star fees, VFX budgets, and marketing spends have all escalated. A film that would have cost ₹25 crore in 2019 now costs ₹50 crore. But the mid-range audience hasn't grown proportionally. The economics of a "hit" have moved upward while the audience pool for non-event films has remained flat.

## What This Means for the NRI Audience

For diaspora viewers, the shift is felt at the ticket counter. In major US and UK markets, Indian films compete for limited screens. When a *Dhurandhar 2* or *Peddi* dominates bookings, smaller films get squeezed out entirely — often receiving no North American theatrical release at all. The mid-budget films that once offered nuanced storytelling and fresh faces increasingly bypass theatres and go straight to Netflix, JioHotstar, or Amazon Prime.

This is both a loss and a realignment. The NRI audience that once discovered films like *Vicky Donor*, *Bareilly Ki Barfi*, or *Badhaai Ho* in theatres now discovers their equivalents at home on streaming apps. The theatrical experience has been reserved for spectacle.

## The Road Ahead

June offers a test case. The first week alone features five major releases across languages. *Peddi* and *Toxic* are event-scale bets; *Bandar* and *Hai Jawani Toh Ishq Hona Hai* are mid-budget plays. By month's end, *Welcome to the Jungle* and *Cocktail 2* add to the pile. The box office will reveal whether any of these non-franchise titles can find breathing room — or whether 2026 confirms that Bollywood's middle class, like its audience, has been split into those who can afford the premium and those who stay home."""
})


# ─── ARTICLE 3: Christmas 2026 Box Office Clash ───

articles.append({
    "headline": "Shah Rukh Khan's King Lines Up Against Avengers, Dune 3, and Jumanji for Christmas 2026. It's the Biggest Box Office Clash in History.",
    "subheadline": "A ₹350 crore Bollywood action thriller, Suhana Khan's debut, and three Hollywood tentpoles — all fighting for the same holiday screens. The stakes have never been higher for Indian cinema abroad.",
    "slug": "king-srk-christmas-2026-avengers-dune-3-jumanji-box-office-clash-nri-20260602",
    "category": "entertainment",
    "image_person": "Shah Rukh Khan",
    "image_fallback_query": "Shah Rukh Khan Bollywood",
    "sources": [
        {"name": "Sacnilk", "url": "https://sacnilk.com"},
        {"name": "Bollywood Hungama", "url": "https://bollywoodhungama.com"},
        {"name": "Filmfare", "url": "https://filmfare.com"}
    ],
    "body": """Six months from now, the global box office will witness something unprecedented. Shah Rukh Khan's action thriller *King* has locked December 24, 2026 as its release date — placing it directly in the path of Marvel's *Avengers: Doomsday* (December 18), Denis Villeneuve's *Dune: Part Three* (December 18), and Dwayne Johnson's *Jumanji: Open World* (December 25).

This isn't a clash. It's a four-way collision at the busiest box office corridor of the year, and for the first time in Bollywood history, an Indian film is voluntarily walking into a Hollywood firefight of this magnitude.

## The Film

Directed by Siddharth Anand, who previously helmed the ₹1,000 crore-grossing *Pathaan*, *King* reunites him with Shah Rukh Khan for what's being described as a globetrotting assassin thriller. SRK reportedly plays a deadly contract killer, with Suhana Khan — his daughter — making her theatrical debut as his protégé. Abhishek Bachchan has been cast as the primary antagonist, and reports consistently link Deepika Padukone to a substantial cameo. Arshad Warsi, Jaideep Ahlawat, and Abhay Verma round out the ensemble.

The budget is reported at ₹350 crore, with Anirudh Ravichander composing the soundtrack — his second collaboration with SRK after the blockbuster *Jawan*. Principal photography is nearing completion, with global-scale post-production planned.

## Why It Matters for the Diaspora

For NRI audiences, Christmas is the one window where Indian and Hollywood blockbusters compete head-to-head for the same screens, the same afternoon, and the same family outing. In markets like the US, UK, Canada, Australia, and the Middle East, multiplexes allocate screens based on advance booking velocity. A strong SRK opening can command 600-800 screens across North America; a weak one might get 200.

The 45-day gap between *Ramayana: Part 1* (expected Diwali 2026) and *King* (Christmas) is strategic — it ensures SRK doesn't cannibalise his own audience's theatrical appetite. But the Hollywood titles aren't so considerate. *Avengers: Doomsday* alone could command 4,000+ screens in North America, and *Dune 3* has secured a three-week exclusive IMAX window starting December 18, which means *King* won't get IMAX screens until early January at the earliest.

## The Precedent

SRK has historically owned the Christmas window. *Dilwale* (2015), *Zero* (2018), *Dunki* (2023) — the results have been mixed, but the strategy has been consistent: use the holiday footfall to maximise opening weekends. What's different in 2026 is the scale of Hollywood competition. No previous Christmas has featured three Hollywood tentpoles of this calibre releasing within the same week.

The counterargument: *Pathaan* proved that SRK's current audience is franchise-loyal and will show up regardless of competition. *Jawan* confirmed that his appeal now crosses linguistic boundaries in ways it didn't a decade ago. If *King* delivers the action spectacle its pedigree promises, the Indian diaspora audience — which turned out for *Pathaan* in numbers that shocked US exhibitors — could give it a runway independent of Hollywood's dominance.

## Suhana Khan's Debut

The industry is watching Suhana Khan's theatrical launch as closely as the box office arithmetic. Star-kid debuts have been brutally punished by audiences in recent years — Shanaya Kapoor, Ibrahim Ali Khan, and others have faced scepticism that their predecessors never encountered. Suhana's Netflix film *The Archies* drew mixed reviews. But a Christmas release alongside her father, in an action genre that masks acting limitations with choreography and pace, is the most commercially protected debut imaginable.

## The Stakes

At ₹350 crore, *King* needs approximately ₹700-800 crore worldwide to be considered a clean hit. That's achievable for peak-era SRK — *Pathaan* earned over ₹1,000 crore — but it requires the kind of sustained theatrical run that Hollywood competition could truncate. Screens lost to *Avengers* in week one can't be recovered in week three.

For the NRI audience planning their holiday movie outings, December 2026 presents an embarrassment of riches. The question is whether the Indian film in the lineup can hold its own — or whether King becomes the latest evidence that Bollywood, for all its ambition, still fights for scraps at the global table."""
})

# ──────────────────────────────────────────
# PUBLISH
# ──────────────────────────────────────────

now = datetime.now(timezone.utc).isoformat()

for i, art in enumerate(articles):
    print(f"\n{'='*60}")
    print(f"Article {i+1}: {art['headline'][:60]}...")
    
    # Image sourcing
    img_url = None
    img_attribution = None
    
    if art.get("image_person"):
        img_url = fetch_wikipedia_person_image(art["image_person"])
        if img_url:
            img_attribution = "Wikimedia Commons"
    
    if not img_url and art.get("image_fallback_query"):
        img_url = fetch_pexels_image(art["image_fallback_query"])
        if img_url:
            img_attribution = "The Videshi"
    
    # Upload to Supabase if we have an image
    final_img_url = None
    if img_url:
        filename = f"{art['slug']}.jpg"
        final_img_url = upload_image_to_supabase(img_url, filename)
        if not validate_image_url(final_img_url):
            print(f"  ⚠ Image validation failed, trying direct URL...")
            if validate_image_url(img_url):
                final_img_url = img_url
            else:
                print(f"  ⚠ Direct URL also failed, skipping image")
                final_img_url = None

    art_id = str(uuid.uuid4())
    
    payload = {
        "id": art_id,
        "headline": art["headline"],
        "subheadline": art["subheadline"],
        "slug": art["slug"],
        "body": art["body"],
        "category": art["category"],
        "vertical": art["category"],
        "sources": art["sources"],
        "tags": [],
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "is_featured": False,
        "image_url": final_img_url,
        "image_attribution": img_attribution,
    }
    
    result = sb_insert("p2_articles", payload)
    if result:
        print(f"  ✓ Published: {art['slug']}")
    else:
        print(f"  ✗ Failed to publish: {art['slug']}")
    
    time.sleep(1)

print(f"\n{'='*60}")
print(f"Entertainment writer complete. {len(articles)} articles processed.")
