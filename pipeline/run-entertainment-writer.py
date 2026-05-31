#!/usr/bin/env python3
"""Entertainment writer for The Videshi - generates and publishes articles."""

import json
import os
import sys
import uuid
import re
from datetime import datetime, timezone
import requests
import urllib.parse

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
    """Fetch an image from Pexels API using curl (Python urllib gets 403)."""
    import subprocess
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
                 f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape'],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            for photo in photos:
                src = photo.get('src', {})
                url = src.get('large2x') or src.get('large') or src.get('original')
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image_url(url):
    """Validate that an image URL returns HTTP 200 with image content > 5KB."""
    if not url:
        return False
    # Trust Wikipedia/Wikimedia URLs without validation (they rate-limit HEAD requests)
    if 'upload.wikimedia.org' in url or 'wikipedia.org' in url:
        return True
    # Trust Pexels URLs
    if 'images.pexels.com' in url:
        return True
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code != 200:
            r = requests.get(url, timeout=10, stream=True, allow_redirects=True,
                           headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        content_type = r.headers.get('Content-Type', '')
        content_length = int(r.headers.get('Content-Length', 0))
        if 'image' in content_type and content_length > 5000:
            return True
        if 'image' in content_type and content_length == 0:
            return True
    except:
        pass
    return False

def sb_insert(table, data):
    """Insert a record into Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    r = requests.post(url, headers=HEADERS, json=data, timeout=30)
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            return result[0]
        return result
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:200]}")
        return None

def sb_patch(table, filters, data):
    """Patch a record in Supabase."""
    params = '&'.join(f"{k}={v}" for k, v in filters.items())
    url = f"{SUPABASE_URL}/rest/v1/{table}?{params}"
    r = requests.patch(url, headers=HEADERS, json=data, timeout=30)
    if r.status_code in (200, 204):
        return True
    else:
        print(f"  ✗ Patch failed ({r.status_code}): {r.text[:200]}")
        return False

# ─── ARTICLES ───────────────────────────────────────────────────────

articles = []

# ─── ARTICLE 1: Made in India: A Titan Story ────────────────────────

articles.append({
    "headline": "Naseeruddin Shah Is JRD Tata in Made in India. It's the Indian Startup Origin Story That Streaming Has Been Missing.",
    "subheadline": "Amazon MX Player's six-part series about how Xerxes Desai and JRD Tata built Titan from a failing Tata Press division premieres June 3 — for free.",
    "slug": "made-in-india-titan-story-naseeruddin-shah-jrd-tata-jim-sarbh-amazon-nri-20260531",
    "category": "entertainment",
    "sources": "Brownstone Worldwide, Bollywood Hungama, MensXP, Amazon MX Player",
    "image_person": "Naseeruddin Shah",
    "image_fallback_query": "Indian watch industry Titan",
    "body": """Long before Shark Tank India made "startup" a dinner-table word in every NRI household, there was Xerxes Desai — a man tasked with saving a dying division of the Tata Group who ended up building one of India's most iconic consumer brands instead.

*Made in India: A Titan Story*, a six-part drama series premiering on Amazon MX Player on June 3, tells that story. And it's free to stream worldwide.

## The Casting That Makes This Work

Naseeruddin Shah plays JRD Tata — the towering patriarch of the Tata empire whose quiet faith in people was as legendary as his business acumen. Jim Sarbh takes on Xerxes Desai, the founding managing director of Titan who transformed a struggling Tata Press into the watch brand that would eventually sit on millions of Indian wrists.

The pairing is inspired. Shah, who has spent five decades inhabiting complex men with moral weight, brings exactly the kind of understated gravitas that JRD Tata demands. Sarbh, who described Desai as "quietly rebellious, someone unafraid to challenge convention and imagine what didn't yet exist," has built a career on playing intelligent men navigating systems that weren't designed for them.

Vaibhav Tatwawadi, Namita Dubey, Lakshvir Saran, and Kaveri Seth round out the ensemble. Karan Vyas wrote the series; Robbie Grewal directed.

## Why This Story Matters for the Diaspora

The series is based on Vinay Kamath's book *Titan — India's Most Successful Consumer Brand*, and is set in pre-liberalisation India — a time when importing a Seiko or a Citizen meant knowing someone who knew someone. HMT was the only game in town, and the idea that an Indian company could build a world-class consumer brand was considered, at best, ambitious.

For NRIs who grew up watching their parents wear Titan watches — or who remember the first time a Sonata showed up in a relative's gift bag — this isn't just a business story. It's a cultural touchstone. Titan didn't just make watches. It made Indians believe they could build brands that didn't need to apologize for being Indian.

The series traces the full arc: the bureaucratic hurdles of licence raj, the market challenges of competing against entrenched government monopolies, the personal sacrifices that came with betting everything on an idea. It culminates in the birth of Sonata and the revolutionary Titan Edge — products that redefined what "Made in India" could mean.

## The Streaming Play

Almighty Motion Pictures and T-Series Films produced the series. Amazon MX Player is streaming it for free — a deliberate play to maximize reach across India and the diaspora. The series will be available on mobile devices, connected TVs, the Amazon shopping app, Prime Video, Fire TV, JioTV, and Airtel Xstream.

Jim Sarbh put it best: "What I love about *Made in India: A Titan Story* is that while it speaks of ambition and scale, at its core, it's deeply human — about persistence, instinct, and believing in an idea long before anyone else does."

For a diaspora that has spent the last decade watching Silicon Valley startup stories on every streaming platform imaginable, here's one that starts in Hosur, Tamil Nadu, in the 1980s. It's about time."""
})

# ─── ARTICLE 2: Maa Behen ──────────────────────────────────────────

articles.append({
    "headline": "Madhuri Dixit, Triptii Dimri, and a Dead Body in the Kitchen. Maa Behen Drops on Netflix June 4.",
    "subheadline": "Suresh Triveni's dark comedy about a mother-daughter trio hiding a corpse from their conservative neighbours is Netflix India's biggest June bet.",
    "slug": "maa-behen-madhuri-dixit-triptii-dimri-netflix-dark-comedy-june-4-nri-20260531",
    "category": "entertainment",
    "sources": "Netflix, Bollywood Life, Hollywood Reporter India, Wikipedia",
    "image_person": "Madhuri Dixit",
    "image_fallback_query": "Bollywood dark comedy",
    "body": """There's a dead body in the kitchen. The neighbours are nosy. And the three women who need to make this problem disappear can barely stand each other.

That's the setup for *Maa Behen*, Netflix India's upcoming dark comedy that drops worldwide on June 4. And with Madhuri Dixit, Triptii Dimri, and newcomer Dharna Durga as the dysfunctional mother-daughter trio at its centre, the film is being positioned as one of the streamer's biggest Indian bets this summer.

## The Premise

Rekha (Madhuri Dixit) and her daughters Jaya (Triptii Dimri) and Sushma (Dharna Durga) are already the subject of gossip in their conservative neighbourhood. When they discover a dead body in their kitchen, the perpetually bickering trio is forced into an unlikely alliance — turning their familial friction into a survival strategy as they attempt to dispose of the evidence while keeping up appearances.

The tone sits somewhere in the neighbourhood of *Darlings* — Netflix India's 2022 hit that proved Indian audiences have an appetite for stories where domestic tension, crime, and dark humour coexist without any of them flinching. Ravi Kishan joins the cast as Gupta Ji, adding a layer of comic menace that the trailer suggests will be one of the film's biggest crowd-pleasers.

## Suresh Triveni's Pivot

The director is Suresh Triveni, best known for *Tumhari Sulu* — the 2017 Vidya Balan-starrer about a housewife who becomes a late-night radio jockey. That film operated in a completely different register, warm and aspirational, but Triveni has always been interested in women who find power in unexpected places. With *Maa Behen*, he's taking that thesis into significantly darker territory.

The screenplay is by Pooja Tolani (who also co-wrote the story with Triveni), and the film is produced by Vikram Malhotra's Abundantia Entertainment — the banner behind *Breathe*, *Sherni*, and *Jalsa* — in association with Triveni's own Opening Image Films.

## Dhak Dhak Reloaded

The soundtrack includes "Dhak Dhak Reloaded" — a reworked version of the legendary *Beta* song that defined Madhuri Dixit's career in the '90s. The original, composed by Anand-Milind with vocals by Anuradha Paudwal and Udit Narayan, was the song that made "Dhak Dhak Girl" a permanent prefix to Madhuri's name. The new version, by Akshay and IP, is being positioned as both a nostalgic callback and a meta-commentary on Madhuri's evolution from the dancing queen of Bollywood's golden age to an actress choosing increasingly complex, contemporary roles.

## The NRI Watch

For diaspora audiences, *Maa Behen* represents exactly the kind of Indian streaming content that works at dinner parties and on long flights — a tight, contained dark comedy with recognisable stars, a premise that translates across cultures, and the kind of chaotic family dynamics that every Indian household recognises (minus, hopefully, the dead body).

The film also marks a reunion of sorts for Madhuri Dixit and Triptii Dimri, who appeared together in *Bhool Bhulaiyaa 3* — though in far more traditional roles. Here, the power dynamic is messier, more interesting, and more fun.

Geetanjali Kulkarni, Arunoday Singh, Javed Khan, Shardul Bhardwaj, and Jatin Sarna (as Rekha's husband) round out the ensemble. The promotional campaign has already gone chaotic — the trio arrived at a Gurugram mall on a decorated rickshaw for a flash mob, challenged fans to a "Roti Challenge," and generally behaved as if they'd just hidden a body and were running on adrenaline.

*Maa Behen* premieres on Netflix on June 4, 2026. Worldwide."""
})

# ─── ARTICLE 3: May 2026 Box Office Report ──────────────────────────

articles.append({
    "headline": "May 2026 Was the Month Regional Cinema Broke Bollywood's Back. Here Are the Numbers.",
    "subheadline": "Suriya's Karuppu crossed ₹270 crore. Raja Shivaji became the highest-grossing Marathi film ever. And Bollywood's two big bets couldn't crack ₹55 crore between them.",
    "slug": "may-2026-box-office-report-regional-cinema-dominates-bollywood-struggles-nri-20260531",
    "category": "entertainment",
    "sources": "Sacnilk, Koimoi, Box Office India",
    "image_person": "Suriya",
    "image_person_alt": "Suriya (actor)",
    "image_fallback_query": "Indian cinema box office audience",
    "body": """May 2026 will be remembered as the month that regional Indian cinema didn't just outperform Bollywood — it embarrassed it.

Three films from three different language industries posted numbers that most Hindi films would consider career-defining. Meanwhile, Bollywood's two biggest May releases limped to collections that wouldn't cover a single film's marketing budget in the South. Here's the full picture.

## The Blockbusters

**Karuppu (Tamil) — ₹270+ Crore Worldwide**

Suriya's action drama, directed by RJ Balaji, didn't just succeed — it rewrote the man's entire career trajectory. Released on May 15, *Karuppu* crossed ₹270 crore worldwide in just 15 days, earning more than double Suriya's previous biggest grosser, *Singam 2*. Tamil Nadu alone contributed ₹130+ crore gross. The overseas numbers — particularly from the Gulf, Malaysia, Singapore, and North America — confirmed what trade analysts have been saying for two years: the Tamil diaspora is now a reliable ₹30-40 crore market for the right film.

**Drishyam 3 (Malayalam) — ₹200+ Crore Worldwide**

Mohanlal and director Jeethu Joseph returned with the third instalment of Indian cinema's most celebrated thriller franchise, and the numbers were historic — ₹200+ crore worldwide in just 8 days. What's remarkable is where the money came from: overseas contributed ₹100+ crore, meaning the international audience (heavily NRI-driven) matched the domestic haul almost crore for crore. For a Malayalam film — traditionally considered a "small" market by Bollywood standards — this is an extraordinary statement about the globalisation of Indian cinema.

**Raja Shivaji (Marathi) — ₹114 Crore Worldwide**

Riteish Deshmukh's historical epic shattered Marathi cinema's all-time record, surpassing *Sairat*'s ₹110 crore that had stood untouched for nearly a decade. Released on May 1, *Raja Shivaji* grossed ₹114 crore worldwide in 26 days. For context, most Marathi films consider ₹10 crore a hit. This is a different league entirely.

**Deool Band 2 (Marathi) — ₹26.5 Crore and Climbing**

The surprise of the month. This devotional drama opened to just ₹2.90 crore but rode extraordinary word-of-mouth to ₹26.5 crore in 6 days, marching toward ₹50 crore — blockbuster territory for its scale. It's the kind of slow-burn success that proves the Marathi audience is sophisticated enough to find and elevate quality on their own, without the promotional machinery that Hindi cinema considers essential.

## Bollywood's Rough Month

**Pati Patni Aur Woh Do — ₹53.85 Crore Worldwide**

A sequel that nobody was particularly demanding, *PPAWD* struggled with underwhelming occupancies from day one. Crossing ₹50 crore worldwide is technically acceptable, but for a film with franchise recognition and urban marketing muscle, the number tells a story of audience apathy.

**Chand Mera Dil — ₹21 Crore in 5 Days**

The romantic drama failed to capitalise on its music-driven promotions and urban appeal. ₹21 crore in 5 days is a poor collection by any standard, and the film showed no signs of the momentum required for a rebound.

## What This Means for the Diaspora

The shift is structural, not cyclical. Regional Indian cinema — Tamil, Malayalam, Marathi, Telugu, Kannada — is now producing films that compete with Bollywood on production value, storytelling ambition, and box office returns. For NRIs who grew up thinking "Indian cinema" meant "Hindi cinema," May 2026 is the clearest evidence yet that the centre of gravity has moved.

The overseas numbers are the real story. When a Malayalam film earns ₹100 crore overseas and a Tamil film crosses ₹270 crore worldwide in two weeks, the diaspora isn't just a bonus market anymore — it's a primary one. Exhibitors in the US, UK, Canada, Australia, and the Gulf are now giving regional Indian films premium screens, prime showtimes, and the kind of marketing support that was once reserved for Bollywood blockbusters.

May 2026 didn't kill Bollywood. But it made very clear that Bollywood is no longer the default."""
})

# ─── ARTICLE 4: Jana Nayagan Saga ──────────────────────────────────

articles.append({
    "headline": "Vijay Is Now Chief Minister of Tamil Nadu. His Last Film Still Can't Get a Censor Certificate.",
    "subheadline": "Jana Nayagan's ₹120 crore OTT deal collapsed to ₹50 crore after a full HD piracy leak. Distributors have withdrawn ₹103 crore in deals. And the CBFC still hasn't signed off.",
    "slug": "vijay-jana-nayagan-censor-piracy-crisis-ott-deal-collapse-chief-minister-nri-20260531",
    "category": "entertainment",
    "sources": "Sacnilk, Cinema Express, Pinkvilla",
    "image_person": "Vijay (actor)",
    "image_person_alt": "Vijay (Tamil actor)",
    "image_fallback_query": "Tamil Nadu cinema politics",
    "body": """Thalapathy Vijay won the Tamil Nadu state election. He is the Chief Minister. He leads one of India's largest states. And his final film — the one he made before entering politics full-time — still doesn't have a censor certificate.

The saga of *Jana Nayagan* is, at this point, one of the most extraordinary stories in Indian cinema history. Not because of what happens on screen, but because of everything that has happened off it.

## The Timeline of Chaos

*Jana Nayagan*, directed by H. Vinoth, was supposed to be Vijay's farewell to cinema — a political action thriller that would serve as a bridge between his screen career and his real-life political ambitions. The film was initially scheduled for a massive January 9 theatrical release.

Then the Central Board of Film Certification stepped in.

The CBFC evaluated the film in December 2025 and initially cleared it with minor modifications. But a formal complaint from a single committee member — citing concerns about religious sentiments and military symbols — prompted the CBFC Chairman to refer the film to a Revising Committee. This decision overrode the initial evaluation and triggered a legal battle in the Madras High Court.

The producers eventually withdrew their court petition to pursue the Revising Committee route, hoping for a quicker resolution. It didn't work. A scheduled screening for the Revising Committee on March 9, 2026, was cancelled hours before it was set to begin — reportedly because a key committee member fell ill.

The certification process has been indefinitely deferred ever since.

## The Piracy Catastrophe

On April 9, the film was leaked online in full HD quality. The entire movie — not a cam print, not fragments, but a complete, high-definition version — surfaced on Telegram and piracy platforms before it had played a single paid show in a single theatre.

The financial devastation was immediate. Amazon Prime Video, which had reportedly acquired the digital rights for ₹120 crore, signalled its intent to withdraw from the deal. The leak had rendered the post-theatrical OTT window — the period when a streamer exclusively capitalises on a film's theatrical buzz — essentially worthless.

Under renegotiated terms, the OTT offer has reportedly dropped to around ₹50 crore — less than half the original price. Whether even that deal is locked remains unclear.

## The Distributor Exodus

Tamil Nadu distributors who had bought the film for ₹103 crore on Minimum Guarantee deals have officially withdrawn. Under the new reality — a leaked film, no censor certificate, and an uncertain release date — distributors are now willing to offer only 50 percent of the previous agreement value, shifting the deal entirely to a distribution basis.

For KVN Productions, the producing entity, this represents a liquidity crisis of historic proportions in Tamil cinema.

## The Political Dimension

Here's where *Jana Nayagan* transcends the usual Bollywood/Kollywood box office story and enters genuinely uncharted territory: Vijay isn't just a movie star waiting for his film to release. He's the Chief Minister of a state with 80 million people.

Tamil Nadu's minister for film technology, Rajmohan, recently addressed the situation publicly: "The film can be released only after obtaining censor certification. We cannot do such things to any film for political reasons or any other reasons."

Speculation suggests the film may target a release around Vijay's birthday on June 22, with the District ticketing app briefly listing a June 19 release date and BookMyShow updating the film's release month to June. But no official confirmation has come from the makers.

## What the Diaspora Should Know

For NRIs who follow Tamil cinema, *Jana Nayagan* isn't just a delayed film — it's a case study in how India's regulatory systems, piracy ecosystem, and political landscape can collide to create a perfect storm. A ₹120 crore OTT deal became ₹50 crore. A ₹103 crore distribution deal became 50 percent of that. And a film that was supposed to be the biggest Tamil release of January still hasn't been seen legally by a single paying audience member in May.

Whether *Jana Nayagan* eventually reaches theatres — and whether audiences show up after having had access to the leaked version for months — will tell us something important about the resilience of theatrical cinema in India. And about the limits of star power, even when that star now controls a state."""
})

# ─── PUBLISH ────────────────────────────────────────────────────────

print(f"\n{'='*60}")
print(f"Entertainment Writer Run — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
print(f"{'='*60}\n")

published = 0
failed = 0

for i, article in enumerate(articles, 1):
    print(f"\n--- Article {i}/{len(articles)}: {article['headline'][:60]}... ---")
    
    # Image sourcing
    img_url = None
    img_attribution = None
    
    # Try Wikipedia first for person articles
    person = article.get('image_person')
    if person:
        img_url = fetch_wikipedia_person_image(person)
        if not img_url and article.get('image_person_alt'):
            img_url = fetch_wikipedia_person_image(article['image_person_alt'])
        if img_url:
            img_attribution = "Wikimedia Commons"
    
    # Fallback to Pexels
    if not img_url and article.get('image_fallback_query'):
        img_url = fetch_pexels_image(article['image_fallback_query'])
        if img_url:
            img_attribution = "The Videshi"
    
    # Validate
    if img_url and not validate_image_url(img_url):
        print(f"  ⚠ Image validation failed, dropping image")
        img_url = None
        img_attribution = None
    
    # Check for banned sources
    if img_url:
        banned = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com', '_nc_ht=', '_nc_cat=', 'ccb=']
        if any(b in img_url for b in banned):
            print(f"  ✗ BANNED image source detected, dropping: {img_url[:60]}")
            img_url = None
            img_attribution = None
    
    # Build article record
    art_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    record = {
        "id": art_id,
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "slug": article["slug"],
        "body": article["body"],
        "category": article["category"],
        "vertical": "entertainment",
        "sources": article["sources"],
        "status": "published",
        "published_at": now,
        "created_at": now,
        "updated_at": now,
    }
    
    if img_url:
        record["image_url"] = img_url
    if img_attribution:
        record["image_attribution"] = img_attribution
    
    # Word count check
    word_count = len(article["body"].split())
    if word_count < 400:
        print(f"  ✗ REJECTED: Only {word_count} words (minimum 400)")
        failed += 1
        continue
    
    # Headline length check
    if len(article["headline"]) > 200:
        print(f"  ⚠ Headline too long ({len(article['headline'])} chars), truncating")
        record["headline"] = article["headline"][:197] + "..."
    
    print(f"  Words: {word_count} | Image: {'✓' if img_url else '✗'}")
    
    # Insert
    result = sb_insert("p2_articles", record)
    if result:
        print(f"  ✓ Published: {article['slug']}")
        published += 1
    else:
        print(f"  ✗ Failed to publish")
        failed += 1

print(f"\n{'='*60}")
print(f"Results: {published} published, {failed} failed")
print(f"{'='*60}")
