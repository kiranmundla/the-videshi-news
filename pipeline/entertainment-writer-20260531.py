#!/usr/bin/env python3
"""Entertainment writer for The Videshi - 2026-05-31 batch"""

import os, json, sys, time, re, uuid, requests, urllib.parse
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, _, val = line.partition('=')
                    val = val.strip().strip('"').strip("'")
                    os.environ.setdefault(key.strip(), val)

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

# --- Wikipedia Image Sourcing ---
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
    """Fetch image from Pexels as fallback."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key available")
        return None
    
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            result = subprocess.run(
                ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
                 f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=3'],
                capture_output=True, text=True, timeout=15
            )
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

def validate_image_url(url):
    """Check image URL is valid and returns proper image content."""
    if not url:
        return False
    # Block banned sources
    banned = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com']
    if any(b in url for b in banned):
        print(f"  ✗ Banned source: {url[:60]}")
        return False
    if any(p in url for p in ['_nc_ht=', '_nc_cat=', 'ccb=']):
        print(f"  ✗ Signed Meta URL: {url[:60]}")
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct and cl > 5000:
            return True
        # Try GET if HEAD doesn't give content-length
        if r.status_code == 200 and 'image' in ct:
            r2 = requests.get(url, timeout=10, stream=True,
                            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                return True
        print(f"  ✗ Image validation failed: status={r.status_code}, ct={ct}, cl={cl}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False

def sb_insert(table, data):
    """Insert into Supabase table."""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    r = requests.post(url, headers=HEADERS, json=data, timeout=30)
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            return result[0]
        return result
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None

def sb_patch(table, filters, data):
    """Update Supabase row."""
    params = '&'.join(f'{k}={v}' for k,v in filters.items())
    url = f"{SUPABASE_URL}/rest/v1/{table}?{params}"
    r = requests.patch(url, headers=HEADERS, json=data, timeout=30)
    if r.status_code in (200, 204):
        return True
    print(f"  ✗ Patch failed ({r.status_code}): {r.text[:300]}")
    return False

# ============================================================================
# ARTICLES
# ============================================================================

articles = []

# --- ARTICLE 1: Maa Behen on Netflix June 4 ---
articles.append({
    "headline": "Madhuri Dixit Returns to Netflix With a Dead Body, a Dysfunctional Family, and Zero Apologies. Maa Behen Drops June 4.",
    "subheadline": "The dark comedy pairs Madhuri with Triptii Dimri and newcomer Dharna Durga as three women trying to hide a corpse while their world falls apart. It includes a 'Dhak Dhak Reloaded' track.",
    "slug": "madhuri-dixit-maa-behen-netflix-dark-comedy-triptii-dimri-june-4-nri-20260531",
    "category": "entertainment",
    "body": """Madhuri Dixit is about to remind streaming audiences why she's been Bollywood's most watchable actress for three decades — and she's doing it with a body bag.

*Maa Behen*, Netflix's new Hindi-language dark comedy, premieres globally on **June 4, 2026**. Directed by Suresh Triveni (*Tumhari Sulu*, *Jalsa*) and written by Pooja Tolani, the film casts Madhuri as Rekha, the matriarch of a spectacularly dysfunctional family living in Gurugram's fictional Adarsh Colony. Triptii Dimri plays her daughter Jaya, and newcomer Dharna Durga rounds out the trio as Sushma — three women who discover a dead body in their home and must figure out what to do before everything unravels.

## A Crime-Comedy With Teeth

The trailer makes the film's DNA unmistakable: this isn't a clean family comedy. It's a chaotic spiral of panic, cover-ups, emotional breakdowns, and hilariously bad decisions. Ravi Kishan plays Gupta Ji, adding mass-market comic timing to what is already an unhinged setup. Geetanjali Kulkarni, Arunoday Singh, Shardul Bhardwaj, and Jatin Sarna (as Rekha's husband) fill out a cast that reads like a who's who of India's best character actors.

Produced by Vikram Malhotra's Abundantia Entertainment — the same banner behind *Breathe*, *Sherni*, and *Jalsa* — in association with Triveni's Opening Image Films, *Maa Behen* is the kind of mid-budget, star-powered OTT project that Netflix India has been betting on with increasing confidence.

## The Diaspora Appeal

For NRI audiences, *Maa Behen* checks every box. It's a **day-and-date global release** on Netflix, meaning viewers in the US, UK, and Canada get it at the same time as India. It features Madhuri Dixit, arguably the most universally beloved actress among the Indian diaspora — a generation of NRIs grew up with her, and she's been smart about reinventing herself for the streaming era (from *The Fame Game* to *Bhool Bhulaiyaa 3*).

The soundtrack includes *Dhak Dhak Reloaded*, a reimagining of the iconic track from *Beta* (1992) that first cemented Madhuri's status as Bollywood's dancing queen. Original composers Anand-Milind's work has been rearranged by Akshay Raheja and Abhishek Singh. Other tracks — *Kaari Kaari*, *Yeh Kaisi Raat*, and *Khol Pinjara* — are composed by Akashdeep Sengupta, with T-Series handling the music label.

## Why This Film Matters

Triveni has built a reputation for making films about women who refuse to be victims — from Vidya Balan in *Tumhari Sulu* to the moral grey zones of *Jalsa*. *Maa Behen* appears to continue that thread: three women navigating a crisis with dark humour and messy solidarity rather than waiting for a man to fix things.

For Triptii Dimri, who broke through with *Animal* and has become one of the most in-demand young actresses in Bollywood, this is a chance to play against type alongside a legend. And for Dharna Durga, it's an introduction to a global audience of millions.

Whether *Maa Behen* becomes Netflix India's next breakout hit or a niche cult favourite, one thing is certain: Madhuri Dixit selling chaos in a Gurugram colony is exactly the kind of content that NRI audiences will queue up for on a Wednesday night.

*Maa Behen premieres on Netflix on June 4, 2026.*

**Sources:** Netflix India, Bollywood Life, Wikipedia, Latestly""",
    "sources": ["Netflix India", "Bollywood Life", "Wikipedia", "Latestly"],
    "person_for_image": "Madhuri Dixit",
    "pexels_query": None,
    "pexels_fallback": None,
    "image_attribution": "Wikimedia Commons"
})

# --- ARTICLE 2: Dhurandhar 2 OTT Premiere ---
articles.append({
    "headline": "Dhurandhar 2 Hits JioHotstar on June 4 With a Raw & Undekha Cut. Here's What NRI Audiences Need to Know.",
    "subheadline": "Ranveer Singh's ₹1,800 crore blockbuster finally lands on streaming — with extended scenes, longer action sequences, and a 30-minute pre-show premiere event.",
    "slug": "dhurandhar-2-the-revenge-jiohotstar-ott-release-june-4-raw-undekha-nri-20260531",
    "category": "entertainment",
    "body": """The wait is over. India's second-biggest film of all time is finally coming to your living room — and it's bringing extra footage.

**Dhurandhar 2: The Revenge** — Aditya Dhar's spy action blockbuster starring Ranveer Singh — premieres on **JioHotstar on June 4, 2026 at 7 PM IST** as the *Raw & Undekha* extended cut. A subsequent Netflix India release follows on June 19.

## What's in the Extended Cut?

The Raw & Undekha version promises additional scenes, longer action sequences, and previously unseen footage that was trimmed from the theatrical release. This follows the precedent set by the first *Dhurandhar*, which also received an extended OTT cut that became a sensation on both Netflix and JioHotstar in May.

The premiere isn't just a standard streaming drop. JioHotstar is hosting an exclusive **30-minute pre-show event** at 7 PM featuring candid cast conversations, behind-the-scenes stories, and production insights — before the film becomes available for general streaming from June 5 onwards.

## The Numbers Behind the Phenomenon

*Dhurandhar 2: The Revenge* has grossed approximately **₹1,800 crore worldwide**, making it the second-highest-grossing Indian film in history. The film opened on March 19, 2026, and was still earning over ₹30 lakh daily in its ninth week — the kind of theatrical endurance that's almost unheard of in contemporary Bollywood.

The sequel picks up the story of Hamza Ali Mazari in the volatile world of Lyari, expanding the power struggles, ambition, and survival that defined the first film. Alongside Ranveer Singh, the cast includes **R. Madhavan, Sanjay Dutt, Arjun Rampal, Sara Arjun, Rakesh Bedi, and Danish Pandor**.

## The Dual-Platform Strategy

The staggered release — JioHotstar first, Netflix two weeks later — is a calculated business move. JioHotstar secured the primary Indian streaming rights in a premium deal, while Netflix retains global distribution and a delayed Indian window. This allows both platforms to maximise subscriber engagement without cannibalising each other's numbers.

## The NRI Angle

For diaspora audiences, the timing is strategic. The OTT premiere lands right after the **IPL 2026 final** — when cricket viewership traditionally transitions back to entertainment content. With cricket season wrapping up and summer blockbusters dominating streaming, *Dhurandhar 2* is positioned to capture undivided attention.

For NRIs who missed the theatrical run, or who want to see the uncut version with the extended sequences that social media has been buzzing about, June 4 is the date to mark. The film is already streaming globally on Netflix in several international markets, but the Raw & Undekha version with the premiere event is exclusive to the JioHotstar launch.

Whether you watched it in IMAX on opening weekend or have been waiting for the couch viewing, the extended cut of India's biggest action spectacle of 2026 is worth the wait.

*Dhurandhar 2: The Revenge (Raw & Undekha) premieres on JioHotstar on June 4 at 7 PM IST. Regular streaming begins June 5. Netflix India release: June 19.*

**Sources:** Sacnilk, Livemint, JioHotstar, Bollywood Hungama""",
    "sources": ["Sacnilk", "Livemint", "JioHotstar", "Bollywood Hungama"],
    "person_for_image": "Ranveer Singh",
    "pexels_query": None,
    "pexels_fallback": None,
    "image_attribution": "Wikimedia Commons"
})

# --- ARTICLE 3: Welcome to the Jungle ---
articles.append({
    "headline": "Welcome to the Jungle Arrives June 26 With 30+ Stars and the Biggest Comedy Cast Bollywood Has Ever Assembled.",
    "subheadline": "Akshay Kumar, Suniel Shetty, Paresh Rawal, Sanjay Dutt, Raveena Tandon, and a parade of Bollywood's finest reunite for the third chapter of the franchise that defined desi comedy.",
    "slug": "welcome-to-the-jungle-june-26-akshay-kumar-massive-cast-comedy-franchise-nri-20260531",
    "category": "entertainment",
    "body": """If you grew up watching Nana Patekar bark "Aap ka Ghoda, Aap ka Gadha" or Anil Kapoor yell his way through *Welcome* (2007), this one's for you. The franchise is back — and it's brought everyone.

**Welcome to the Jungle**, the third instalment of Bollywood's most chaotic comedy franchise, releases theatrically on **June 26, 2026**. Directed by Ahmed Khan and produced by Firoz Nadiadwala, the film features what might be the largest ensemble cast ever assembled for a Hindi comedy: **over 30 actors**, led by Akshay Kumar in his return to the franchise after nearly two decades.

## The Cast Is Absurd (In the Best Way)

The lineup reads like a Bollywood hall of fame reunion: **Akshay Kumar, Suniel Shetty, Paresh Rawal, Sanjay Dutt, Arshad Warsi, Raveena Tandon, Lara Dutta, Disha Patani, Jacqueline Fernandez, Urvashi Rautela, Rajpal Yadav, Johnny Lever, Tusshar Kapoor, Shreyas Talpade, Aftab Shivdasani, Krushna Abhishek, Kiku Sharda, Vindu Dara Singh, Mukesh Tiwari, Yashpal Sharma, Nawab Shah, Kiran Kumar, Puneet Issar, Sudesh Berry, Hemant Pandey, Zakir Hussain, and Sayaji Shinde**. Singer Daler Mehndi appears in a special role.

The film also features the **late Pankaj Dheer** in his final on-screen appearance, making it a poignant watch alongside the comedy.

## The Franchise's Diaspora DNA

The original *Welcome* wasn't just a hit — it became a cultural language for the Indian diaspora. Dialogues from the 2007 film are still quoted at gatherings, WhatsApp groups reference Majnu Bhai's art, and "Uday bhai" remains shorthand for a certain type of chaos. *Welcome Back* (2015) extended that vocabulary, and the franchise's recall value among NRIs is arguably unmatched in the comedy genre.

Ahmed Khan takes over directorial duties from Anees Bazmee, bringing a fresh creative direction while retaining the trademark slapstick chaos. The behind-the-scenes footage that dropped this week went viral across social media, showing the scale of the production — massive sets, high-energy sequences, and the sheer logistical challenge of coordinating 30+ actors in comedy scenes.

## The Business Side

JioStar has acquired the domestic theatrical rights along with satellite and OTT rights, giving the company complete control over the film's Indian lifecycle. The film will eventually stream on JioHotstar after its theatrical window. Pen Marudhar is reportedly finalising overseas rights, with strong interest from diaspora-heavy markets including the **UK, US, Middle East, and North America**.

Akshay Kumar, riding high on the success of *Bhooth Bangla* (which has earned over ₹260 crore domestically and counting), posted a jungle-themed image of himself in a dark suit on a red carpet laid through a forest — the kind of larger-than-life visual that signals the film's ambitions.

## The June Comedy War

*Welcome to the Jungle* isn't arriving in a vacuum. **Dhamaal 4** (Ajay Devgn, Riteish Deshmukh, Arshad Warsi) releases just one week later on July 3, setting up a direct comedy clash at the box office. Before that, **Hai Jawani Toh Ishq Hona Hai** (Varun Dhawan, David Dhawan) and the Imtiaz Ali drama **Main Vaapas Aaunga** (Diljit Dosanjh, Naseeruddin Shah) hit theatres on June 12. It's the most competitive Hindi cinema summer in years.

For NRI audiences, the real question is whether *Welcome to the Jungle* will get a wide international release on opening weekend. Given the franchise's track record and Pen Marudhar's involvement, multiplex screenings in major diaspora cities are likely. But the film's true test will be whether Ahmed Khan can capture the anarchic magic that made the original a classic — not just assemble the cast, but give them something genuinely funny to do.

June 26. Mark it. The jungle is calling.

**Sources:** Sacnilk, Filmibeat, Zoom TV, Bollywood Hungama""",
    "sources": ["Sacnilk", "Filmibeat", "Zoom TV", "Bollywood Hungama"],
    "person_for_image": "Akshay Kumar",
    "pexels_query": None,
    "pexels_fallback": None,
    "image_attribution": "Wikimedia Commons"
})

# --- ARTICLE 4: Spider-Noir hits #1 ---
articles.append({
    "headline": "Nicolas Cage's Spider-Noir Is the Most Popular Show on Prime Video. It's Also the Best Superhero TV in Years.",
    "subheadline": "Set in a noir-styled 1930s New York with a 92% Rotten Tomatoes score and an authentic black-and-white viewing option, the show has dethroned every other Prime original in its first week.",
    "slug": "spider-noir-nicolas-cage-prime-video-number-one-streaming-superhero-best-nri-20260531",
    "category": "entertainment",
    "body": """If you've been burned by too many mediocre superhero shows, *Spider-Noir* is the palate cleanser you didn't know you needed.

Nicolas Cage's new **Prime Video** series launched on **May 27, 2026** and has already become the platform's most popular show, dethroning every other original series in its first week. With a **92% critics score and 93% audience score on Rotten Tomatoes** and an IMDb rating of 8.3, it's not just a hit — it's a genuine phenomenon.

## What Makes It Different

*Spider-Noir* isn't your standard Marvel fare. The eight-episode series is set in a stylized **1930s New York City**, where Cage plays Ben Reilly — a veteran superhero who has hung up his suit to work as a private investigator. The tone is pure pulp detective fiction: shadowy alleyways, moral ambiguity, crackling dialogue, and a mystery that deepens with every episode.

The show offers two viewing modes: **Authentic Black & White** and **True-Hue Full Color**. In black and white, the immersion is remarkable — it feels like a genuine noir film from the era, not a modern show with a filter. The production team, led by showrunners Oren Uziel and Steve Lightfoot with producers Phil Lord, Christopher Miller, and Amy Pascal, clearly understands that atmosphere matters more than spectacle.

## Cage at His Most Restrained (and Most Unhinged)

Critics have praised Cage's performance as one of his best in years. Ruben Peralta Rigaud noted that Cage "delivers a surprisingly restrained and human performance in a series that understands that shadows can be just as interesting as superpowers." The show lets him channel Humphrey Bogart — Cage has said his Ben Reilly is "70 percent Bogart" — while still leaving room for his signature unpredictability.

The supporting cast is equally strong: **Lamorne Morris** as Joe "Robbie" Robertson, **Li Jun Li** as Felicia "Cat" Hardy, **Brendan Gleeson** as Silvermane, **Jack Huston** as Sandman, and **Abraham Popoola** as Tombstone.

## Why It Matters for Streaming Audiences Everywhere

For Indian diaspora audiences who subscribe to Prime Video — and there are millions, given the platform's strong Indian content library — *Spider-Noir* represents exactly the kind of premium English-language content that justifies a subscription. It's binge-worthy (all eight episodes dropped at once), visually distinctive, and doesn't require any prior Spider-Man knowledge.

The show has ranked **#1 on Prime Video's overall chart** according to FlixPatrol data, pushing aside heavyweights like *The Boys*, *Citadel*, *Invincible*, and *Fallout*. Empire Magazine's Alex Godfrey called it a series that "just gets better and better, with a rug-pulling season finale that delivers on every level."

A second season hasn't been confirmed yet, but showrunner Uziel has teased that a potential continuation would go in a more "chaotic" direction. With numbers like these and a Tom Holland *Spider-Man: Brand New Day* theatrical release coming July 31, the Spider-Man universe is having a very good 2026.

*Spider-Noir Season 1 is streaming now on Prime Video worldwide.*

**Sources:** ComicBook.com, ScreenRant, FandomWire, SuperHeroHype, FlixPatrol""",
    "sources": ["ComicBook.com", "ScreenRant", "FandomWire", "SuperHeroHype"],
    "person_for_image": "Nicolas Cage",
    "pexels_query": "noir detective dark city",
    "pexels_fallback": "film noir 1930s",
    "image_attribution": "Wikimedia Commons"
})


# ============================================================================
# PUBLISH
# ============================================================================

published = 0
for i, article in enumerate(articles):
    print(f"\n{'='*60}")
    print(f"Article {i+1}/{len(articles)}: {article['headline'][:70]}...")
    
    # Validate article quality
    body_words = len(article['body'].split())
    if body_words < 400:
        print(f"  ✗ REJECTED: body too short ({body_words} words)")
        continue
    if len(article['headline']) > 200:
        print(f"  ✗ REJECTED: headline too long ({len(article['headline'])} chars)")
        continue
    if len(article['subheadline']) < 15:
        print(f"  ✗ REJECTED: subheadline too short")
        continue
    
    # Image sourcing - Wikipedia first for person articles
    img_url = None
    if article.get('person_for_image'):
        img_url = fetch_wikipedia_person_image(article['person_for_image'])
        if img_url and not validate_image_url(img_url):
            print(f"  ⚠ Wikipedia image failed validation, trying without originalimage...")
            # Try just the thumbnail
            encoded = urllib.parse.quote(article['person_for_image'].replace(' ', '_'))
            try:
                r = requests.get(
                    f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
                    headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
                    timeout=10
                )
                if r.status_code == 200:
                    data = r.json()
                    thumb = data.get("thumbnail", {}).get("source")
                    if thumb and validate_image_url(thumb):
                        img_url = thumb
                        print(f"  ✓ Using thumbnail instead: {thumb[:80]}...")
                    else:
                        img_url = None
            except:
                img_url = None
    
    if not img_url and article.get('pexels_query'):
        img_url = fetch_pexels_image(article['pexels_query'], article.get('pexels_fallback'))
        if img_url:
            article['image_attribution'] = "The Videshi"
            if not validate_image_url(img_url):
                img_url = None
    
    if img_url:
        print(f"  ✓ Final image: {img_url[:80]}...")
    else:
        print(f"  ⚠ No valid image found - publishing without image")
    
    # Build article record
    now_iso = datetime.now(timezone.utc).isoformat()
    record = {
        "headline": article['headline'],
        "subheadline": article['subheadline'],
        "slug": article['slug'],
        "category": article['category'],
        "vertical": article['category'],
        "body": article['body'],
        "status": "published",
        "published_at": now_iso,
        "sources": article['sources'],
        "image_url": img_url,
        "image_attribution": article.get('image_attribution', 'Wikimedia Commons') if img_url else None
    }
    
    result = sb_insert("p2_articles", record)
    if result:
        art_id = result.get('id', 'unknown')
        print(f"  ✓ Published: {article['slug']} (id: {art_id})")
        published += 1
    else:
        print(f"  ✗ Failed to publish: {article['slug']}")
    
    time.sleep(1)  # Rate limit

print(f"\n{'='*60}")
print(f"Done. Published {published}/{len(articles)} articles.")
