#!/usr/bin/env python3
"""Entertainment writer for The Videshi – May 29, 2026 run."""

import json, os, subprocess, sys, uuid, re, time
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
                    os.environ[k] = v

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS_SB = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

import requests

def sb_post(table, data):
    """Insert into Supabase table."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=HEADERS_SB,
        json=data,
        timeout=30
    )
    if r.status_code in (200, 201):
        result = r.json()
        return result[0] if isinstance(result, list) and result else result
    else:
        print(f"  ✗ Supabase insert failed ({r.status_code}): {r.text[:300]}")
        return None

def sb_patch(table, match, data):
    """Update a Supabase row."""
    params = '&'.join(f"{k}={v}" for k, v in match.items())
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/{table}?{params}",
        headers=HEADERS_SB,
        json=data,
        timeout=30
    )
    if r.status_code in (200, 204):
        return True
    else:
        print(f"  ✗ Supabase patch failed ({r.status_code}): {r.text[:300]}")
        return False

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
            # Prefer originalimage (higher res), fall back to thumbnail AS-IS
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

def fetch_pexels_image(query, fallback_query=None):
    """Fetch an image from Pexels using curl (urllib gets 403)."""
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
                 f'https://api.pexels.com/v1/search?query={q}&per_page=5&orientation=landscape'],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            for photo in photos:
                url = photo.get('src', {}).get('large2x') or photo.get('src', {}).get('large')
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image_url(url):
    """Verify image URL returns 200 with image content-type and >5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True, 
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct and cl > 5000:
            return True
        # Some servers don't support HEAD well, try GET
        if r.status_code != 200:
            r2 = requests.get(url, timeout=10, stream=True,
                            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            ct2 = r2.headers.get('Content-Type', '')
            cl2 = int(r2.headers.get('Content-Length', 0))
            if r2.status_code == 200 and 'image' in ct2:
                return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False

def is_banned_url(url):
    """Check if URL is from a banned source."""
    if not url:
        return True
    banned_patterns = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com',
                       '_nc_ht=', '_nc_cat=', 'ccb=']
    for p in banned_patterns:
        if p in url:
            return True
    return False

def source_image(person_name=None, topic_query=None, fallback_query=None):
    """Source an image following the hierarchy: Wikipedia → Pexels → None."""
    img_url = None
    attribution = None
    
    # 1. Try Wikipedia for person articles
    if person_name:
        img_url = fetch_wikipedia_person_image(person_name)
        if img_url and not is_banned_url(img_url) and validate_image_url(img_url):
            return img_url, "Wikimedia Commons"
        # Try alternate forms
        if not img_url and ' ' in person_name:
            # Try just last name
            parts = person_name.split()
            for alt in [f"{parts[0]}_{parts[-1]}", person_name]:
                img_url = fetch_wikipedia_person_image(alt)
                if img_url and not is_banned_url(img_url) and validate_image_url(img_url):
                    return img_url, "Wikimedia Commons"
    
    # 2. Try Pexels with specific queries
    if topic_query:
        img_url = fetch_pexels_image(topic_query, fallback_query)
        if img_url and not is_banned_url(img_url) and validate_image_url(img_url):
            return img_url, "Pexels"
    
    return None, None

# ============================================
# ARTICLES
# ============================================

articles = []

# --- ARTICLE 1: Diljit Dosanjh Sardaar Ji 3 ---
articles.append({
    "headline": "Sardaar Ji 3 Is Banned in India. For the Diaspora, It's the Only Way to Watch Diljit's Next Film.",
    "subheadline": "FWICE has called for a complete ban on Diljit Dosanjh's projects over casting Pakistani actress Hania Aamir. The film releases overseas-only on June 27.",
    "slug": "diljit-dosanjh-sardaar-ji-3-banned-india-overseas-only-hania-aamir-fwice-nri-20260529",
    "category": "entertainment",
    "person": "Diljit Dosanjh",
    "topic_query": "Punjabi Bollywood film production",
    "fallback_query": "Indian film cinema",
    "sources": "Bollywood Life, India Today, Hindustan Times, Zoom TV",
    "body": """Diljit Dosanjh's *Sardaar Ji 3* has become the most politically charged Punjabi film of 2026 — and it hasn't even released yet.

The trailer, which dropped this week confirming Pakistani actress **Hania Aamir** in a prominent role, has triggered a full-blown industry crisis. The Federation of Western India Cine Employees (FWICE) has called for a ban not just on the film, but on **all of Diljit Dosanjh's upcoming projects** — films, songs, everything.

## The Ban and the Backlash

FWICE President **BN Tiwari** didn't mince words. In a statement to Hindustan Times, he said Diljit had "hurt Indian sentiments, disrespected the nation, and insulted the sacrifices of our brave soldiers" by casting a Pakistani actor amid ongoing India-Pakistan tensions.

The directive goes beyond Sardaar Ji 3. FWICE has called for a strict ban on all future projects involving Diljit, as well as sanctions against the film's producers — **White Hill Studios** and **Story Time Productions**, led by producer **Gunbir Singh Sidhu**.

Sidhu, for his part, has pushed back. Speaking to India Today, he pointed out that the film was shot *before* the escalation in India-Pakistan tensions. He also confirmed the decision to skip India's theatrical market entirely, citing respect for public sentiment.

## Overseas-Only: What That Means for NRIs

*Sardaar Ji 3* will release globally on **June 27** — but not in India. For the Indian diaspora in North America, the UK, Australia, and the Middle East, this creates an unusual situation: a major Punjabi franchise film available only to audiences abroad.

The horror-comedy, directed by **Amar Hundal**, reunites Diljit with **Neeru Bajwa** and adds **Gulshan Grover** to the cast. It continues the franchise that began with 2015's *Sardaar Ji*, which became a landmark in Punjabi cinema's commercial growth. Behind-the-scenes photos released this week show the film leaning into its signature blend of comedy and supernatural elements.

## The Bigger Picture

This isn't the first time FWICE has taken action against an artist over Pakistani collaborations. The federation previously issued directives against **Mika Singh** for performing in Karachi. But the Diljit situation carries heavier weight — he's one of the biggest crossover stars in Indian entertainment, fresh off his Met Gala appearance, a collaboration with **A.R. Rahman** and **Imtiaz Ali**, and the global success of Border 2.

The irony isn't lost on anyone. Diljit's next Bollywood release is also an **Imtiaz Ali** film — a romantic drama co-starring **Vedang Raina** and **Sharvari**, releasing on **June 12**. That film, produced by Applause Entertainment and Window Seat Films, faces no controversy. The difference: no Pakistani talent involved.

## What the Diaspora Is Saying

On social media, the reaction has been split. Some NRI audiences have rallied behind the ban, echoing FWICE's position. Others have questioned why a film shot before the current tensions should be retroactively punished — especially when the artist has otherwise been a vocal supporter of Indian armed forces (his role in *Border 2* was literally a tribute to the 1971 war).

Diljit himself has stayed silent. No Instagram post, no press statement, no response to FWICE. For an artist who normally controls his narrative with precision, the quiet is conspicuous.

The film will find its audience — the Punjabi diaspora is one of the most commercially active cinema-going communities in the world. Whether *Sardaar Ji 3* becomes a rallying point for artistic freedom or a cautionary tale about geopolitical timing will depend on what happens in the next four weeks.

*Sardaar Ji 3 releases overseas on June 27, 2026. No Indian theatrical release is planned.*"""
})

# --- ARTICLE 2: Cocktail 2 ---
articles.append({
    "headline": "Cocktail 2's Trailer Was Supposed to Drop Today. Then Maddock Films Pulled the Plug at the Last Minute.",
    "subheadline": "Shahid Kapoor, Kriti Sanon, and Rashmika Mandanna's modern love triangle has been pushed to a tighter June launch window. Here's what we know.",
    "slug": "cocktail-2-trailer-postponed-shahid-kapoor-kriti-sanon-rashmika-mandanna-june-2026-nri-20260529",
    "category": "entertainment",
    "person": "Shahid Kapoor",
    "topic_query": "Bollywood romantic film modern love",
    "fallback_query": "Mumbai city nightlife",
    "sources": "Filmibeat, Bollywood Hungama, Sacnilk",
    "body": """The trailer launch event for *Cocktail 2* was set for today — May 29, 2026. Everything was in place: venue booked, press invited, social media countdown running. Then Maddock Films cancelled it at the last moment.

The new date is **June 2**, and the film's theatrical release on **June 19** remains unchanged. But the sudden postponement has become a story in itself, raising questions about marketing strategy, industry jitters, and what this sequel is actually trying to be.

## Not a Sequel. A Spiritual Successor.

Let's get this straight: *Cocktail 2* is not a continuation of Saif Ali Khan, Deepika Padukone, and Diana Penty's 2012 story. Director **Homi Adajania** returns, but the film is being described as a **spiritual successor** — same thematic DNA (friendship, romance, emotional complications in modern urban India), entirely new characters.

The new cast is a deliberate remix. **Shahid Kapoor** and **Kriti Sanon**, who built undeniable chemistry in *Teri Baaton Mein Aisa Uljha Jiya*, reunite here. Adding **Rashmika Mandanna** gives the project pan-India reach — she's been the most bankable face in Telugu and Kannada cinema for years, and her Bollywood presence keeps growing.

## Why the Delay?

Maddock Films hasn't offered a detailed explanation, but the pattern is clear: a **tighter promotional window**. Instead of giving the trailer three weeks before release, the team is compressing the marketing into 17 days — trailer on June 2, release on June 19.

This isn't unusual in 2026's Bollywood landscape. Studios are learning that audiences have shorter attention spans for trailers. A compressed campaign keeps the film in active social media conversation right until opening weekend, rather than peaking early and fading. *Dhurandhar 2* ran a similar compressed campaign and it became the highest-grossing Hindi film of the year.

## The Legacy It's Chasing

The original *Cocktail* was a sleeper hit that became a cultural touchstone. Its music — *Tumhi Ho Bandhu*, *Daaru Desi*, *Tera Naam Doon* — dominated playlists for years. Deepika Padukone's Veronica became one of Bollywood's most referenced characters. The film didn't just tell a love triangle story; it captured a very specific moment in urban Indian relationships, particularly for young Indians navigating Western and Indian identities simultaneously.

That's the bar *Cocktail 2* has to clear — and it's a high one, especially for NRI audiences who saw themselves in the original's London setting and cultural tensions. Whether Shahid, Kriti, and Rashmika can create the same generational resonance remains the biggest question.

## What to Expect

The storyline is under wraps, but the film is expected to explore **modern relationships, heartbreak, friendship, and emotional choices** set against a stylish city backdrop. Given Homi Adajania's track record (*Finding Fanny*, *Angrezi Medium*), expect a film that's emotionally literate, visually polished, and willing to let its characters be messy.

The trailer — now arriving June 2 — will be the real test. Can it make audiences feel the way the original's trailer did fourteen years ago? Or will this be another franchise revival that trades on nostalgia without earning its own identity?

For NRI audiences, the timing is ideal: a potential date-night film arriving in the middle of June, before the summer blockbuster season heats up. If the music lands (no composer has been officially announced yet for this installment), *Cocktail 2* could become one of the most rewatchable Bollywood films of the year.

*Cocktail 2 trailer drops June 2. Theatrical release June 19, 2026.*"""
})

# --- ARTICLE 3: Desi Bling on Netflix ---
articles.append({
    "headline": "Netflix Put Dubai's Richest Indians on Camera. The Internet Can't Decide Whether to Cringe or Binge.",
    "subheadline": "Desi Bling premiered with a viral on-screen engagement, Bollywood cameos, and enough drama to make Dubai Bling look subtle. It's already on Netflix's global charts.",
    "slug": "netflix-desi-bling-dubai-indian-reality-karan-kundrra-tejasswi-prakash-engagement-nri-20260529",
    "category": "entertainment",
    "person": "Tejasswi Prakash",
    "person_alt": "Karan Kundrra",
    "topic_query": "Dubai luxury lifestyle Indian",
    "fallback_query": "Dubai skyline luxury",
    "sources": "Bollywood Hungama, Mint, Koimoi, The Tab, Hollywood Reporter India",
    "body": """Netflix didn't just make a show about wealthy Indians in Dubai. It made a show where a man proposes to his girlfriend on camera, in Punjabi, on one knee, inside what appears to be a private ballroom in the UAE — and 31 million hours of viewership followed.

*Desi Bling* premiered on May 20, and within days it had landed on Netflix's global charts alongside *Kartavya* and *Dhurandhar*. But the numbers tell only half the story. The real conversation — happening across Twitter, Instagram, and WhatsApp groups from New Jersey to Southall to Melbourne — is about what this show says about the Indian diaspora's relationship with wealth, identity, and self-representation.

## The Engagement That Broke the Internet

The moment everyone's talking about: **Karan Kundrra** going down on one knee and proposing to **Tejasswi Prakash** — the television couple known to fans as "TejRan" — during filming in Dubai. He expressed his feelings in Punjabi through heartfelt verses, then asked, "Yes or a yes?"

The clip went instantly viral. Tejasswi was visibly shaking as the ring went on. "You are my everything," she told him through tears. Fans flooded every platform with screenshots, edits, and reaction videos. For the millions who followed their relationship since *Bigg Boss 15*, this was the payoff.

Netflix knew exactly what it was doing. The engagement wasn't an afterthought — it was the emotional anchor of the entire series.

## Guilty Pleasure or Cultural Mirror?

*Desi Bling* follows the ultra-rich Indian social circle in Dubai: entrepreneurs, socialites, beauty queens, and television stars navigating luxury lifestyles, shifting alliances, and personal drama. Think *Dubai Bling* — which it spins off from — but specifically focused on the Indian expat community.

The cast includes **Rizwan Sajan**, **Shilpa Shetty**, and a roster of Dubai-based entrepreneurs like **Satish Sanpal** (founder of ANAX Holding) and **Pamala Serena**, who's become the show's breakout personality. Seven episodes run 40-45 minutes each, shot across beach clubs, wellness sanctuaries, luxury golf spots, and restaurants where cocktails cost more than a weekly grocery bill.

The internet's response has been predictably divided. Mint called it one of the platform's most-discussed "guilty pleasures," with viewers swinging between "whole vibe" and "second-hand embarrassment." Koimoi's review was harsher, critiquing the scripted-feeling fights and noting that Tejasswi says "shut up" approximately 8,000 times per episode.

## What NRIs Are Really Watching

Here's what makes *Desi Bling* more interesting than it might appear: it's the first major global reality show to center the Indian diaspora's wealth and social dynamics in the Gulf.

The Gulf States — UAE, Qatar, Saudi Arabia, Bahrain — are home to an estimated 9 million Indians, many of whom have built extraordinary wealth in real estate, trading, and finance. This community has been invisible in Western media for decades. *Desi Bling* puts them front and center, penthouses and private jets included.

For NRIs in North America and the UK, the show offers a different kind of mirror. The Dubai Indian community operates with its own rules — more openly opulent than the understated-wealth ethos of Silicon Valley desis, more connected to Bollywood and cricket than the academic-professional networks of the East Coast. Watching it is partly entertainment, partly anthropology.

## The Business of Indian Reality

Netflix's bet on Indian reality content has been paying off. *Indian Matchmaking* ran three seasons. *Fabulous Lives of Bollywood Wives* became a franchise. *The Buckingham Murders* documentary cracked global lists. Now *Desi Bling* joins what's becoming a reliable genre: Indian lives, unfiltered (or strategically filtered), for a global audience.

The engagement between Karan and Tejasswi guarantees that Season 2 conversations are already underway. Whether the show can sustain interest beyond the TejRan moment — whether it can become appointment viewing rather than a one-weekend binge — depends on whether Netflix can find stories in Dubai's Indian elite that go deeper than the surface glamour.

For now, 31 million hours suggest the answer is: people will watch, even if they can't decide whether they're watching ironically.

*Desi Bling is streaming on Netflix. Seven episodes available now.*"""
})

# ============================================
# PUBLISH
# ============================================

def publish_article(article):
    """Publish a single article to Supabase."""
    print(f"\n{'='*60}")
    print(f"Publishing: {article['headline'][:70]}...")
    
    # Source image
    print("  Sourcing image...")
    img_url, attribution = source_image(
        person_name=article.get('person'),
        topic_query=article.get('topic_query'),
        fallback_query=article.get('fallback_query')
    )
    
    # If first person didn't work, try alternate
    if not img_url and article.get('person_alt'):
        print(f"  Trying alternate person: {article['person_alt']}")
        img_url, attribution = source_image(person_name=article['person_alt'])
    
    if img_url:
        print(f"  ✓ Image sourced: {img_url[:80]}...")
    else:
        print(f"  ⚠ No image found — publishing without image (no image > wrong image)")
    
    # Build article data
    art_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    data = {
        "id": art_id,
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "slug": article["slug"],
        "body": article["body"],
        "category": "entertainment",
        "vertical": "entertainment",
        "tags": [],
        "status": "published",
        "published_at": now,
        "created_at": now,
        "updated_at": now,
        "sources": article.get("sources", ""),
        "image_url": img_url if img_url else None,
        "image_attribution": attribution if attribution else None,
        "image_caption": article.get("person", None),
    }
    
    result = sb_post("p2_articles", data)
    if result:
        print(f"  ✓ Published: {article['slug']}")
        return True
    else:
        print(f"  ✗ Failed to publish: {article['slug']}")
        return False

# Main execution
print("=" * 60)
print("The Videshi — Entertainment Writer")
print(f"Run time: {datetime.now(timezone.utc).isoformat()}")
print("=" * 60)

published = 0
failed = 0

for article in articles:
    if publish_article(article):
        published += 1
    else:
        failed += 1
    time.sleep(1)  # Small delay between publishes

print(f"\n{'='*60}")
print(f"DONE: {published} published, {failed} failed")
print("=" * 60)
