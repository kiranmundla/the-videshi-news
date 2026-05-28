#!/usr/bin/env python3
"""Entertainment writer for The Videshi — 2026-05-28 evening run."""

import json, os, sys, time, uuid, re
import requests
import urllib.parse
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
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com; contact@thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            # Use thumbnail source AS-IS (330px) per rules
            img = data.get("thumbnail", {}).get("source") or data.get("originalimage", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
        elif r.status_code == 429:
            print(f"  ⚠ Wikipedia rate limited for '{person_name}', waiting...")
            time.sleep(3)
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

def fetch_pexels_image(query, fallback_query=None):
    """Fetch a relevant image from Pexels. Use curl approach."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            result = subprocess.run(
                ['curl', '-sS', f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5',
                 '-H', f'Authorization: {PEXELS_KEY}'],
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

def validate_image(url):
    """Validate image URL returns 200 with image content-type and reasonable size."""
    if not url:
        return False
    # Block banned sources
    banned = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com', '_nc_ht=', '_nc_cat=', 'ccb=']
    for b in banned:
        if b in url:
            print(f"  ✗ Banned source detected: {b}")
            return False
    # Trust Wikipedia/Wikimedia URLs
    if 'upload.wikimedia.org' in url:
        print(f"  ✓ Trusted Wikimedia URL")
        return True
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct and cl > 5000:
            print(f"  ✓ Image validated: {cl} bytes, {ct}")
            return True
        if r.status_code == 200 and 'image' in ct:
            print(f"  ✓ Image validated (no Content-Length): {ct}")
            return True
        print(f"  ✗ Image validation failed: status={r.status_code}, ct={ct}, cl={cl}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False

def publish_article(article):
    """Publish article to Supabase."""
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S+00:00')
    payload = {
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "body": article["body"],
        "slug": article["slug"],
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": now,
        "sources": article.get("sources", []),
        "image_url": article.get("image_url", ""),
        "image_caption": article.get("image_caption", ""),
        "image_attribution": article.get("image_attribution", ""),
        "tags": article.get("tags", [])
    }
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=payload,
        timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        aid = data[0].get('id', 'unknown') if isinstance(data, list) and data else 'unknown'
        print(f"  ✓ Published: {article['headline'][:60]}... (id: {aid})")
        return True
    else:
        print(f"  ✗ Publish failed ({r.status_code}): {r.text[:200]}")
        return False


# ─────────────────────────────────────────────
# ARTICLE 1: Ram Charan's Peddi
# ─────────────────────────────────────────────

def write_peddi_article():
    print("\n📝 Article 1: Ram Charan's Peddi")
    
    # Get Wikipedia image
    img = fetch_wikipedia_person_image("Ram Charan")
    img_caption = "Ram Charan"
    img_attr = "Wikimedia Commons"
    
    if not img or not validate_image(img):
        img = fetch_wikipedia_person_image("Ram Charan (actor)")
        if not img or not validate_image(img):
            img = fetch_pexels_image("cricket stadium India", "sports rural India")
            img_attr = "Pexels"
            img_caption = "Peddi blends sports and village life in 1980s Andhra Pradesh"
    
    headline = "Ram Charan's Peddi Opens in Six Days. It Has AR Rahman, a Three-Hour Runtime, and 15,000 Tickets Already Sold in North America."
    subheadline = "The most expensive Telugu film of the year arrives June 4 with Priyanka Chopra's endorsement, Chiranjeevi's intervention in Telangana theaters, and a trailer that hit 175 million views in 48 hours."
    
    body = """The last time Ram Charan stepped into a theater was with *RRR*. That was four years and one Oscar ago. On June 4, he returns with *Peddi* — a three-hour, nine-minute sports drama set in 1980s rural Andhra Pradesh, directed by Buchi Babu Sana, scored by AR Rahman, and carrying enough expectations to make everyone involved nervous.

The trailer, released on May 16 alongside a live AR Rahman concert in Bhopal, crossed 101 million views in its first 24 hours and blew past 175 million within 48. It shows Ram Charan as a village athlete — cricketer, wrestler, runner — who channels sporting ambition into a fight for his community's dignity against a powerful rival. Janhvi Kapoor plays opposite him in what early footage suggests is a grounded rural performance far from her urban Bollywood work. Shiva Rajkumar, Kannada cinema's living legend, plays a role described only as "pivotal." Shruti Haasan appears in a special song, Hellallallo, which the makers released as a promo ahead of the Bhopal concert.

The production is massive. Vriddhi Cinemas and IVY Entertainment are producing, with Mythri Movie Makers and Sukumar Writings involved. Jio Studios, which distributed both *Dhurandhar* films and *Raja Shivaji* in North India, will handle the Hindi-language rollout. The CBFC cleared the film with a U/A 16+ certificate after edits to some dialogue, while action sequences remain intact.

## The NRI Factor

For diaspora audiences, the advance booking numbers tell the story. North America premieres have already crossed 15,000 tickets sold, with the US premiere set for June 3 — a full day before the Indian release. In the UK, bookings opened to similarly strong demand. The Telugu version leads the charge, but dubbed Hindi, Tamil, and Kannada versions will also screen internationally.

Priyanka Chopra — currently filming Rajamouli's *SSMB29* alongside Ram Charan's co-star Mahesh Babu — shared the trailer on X, calling it "fire." Rishab Shetty, fresh off *Kantara 2*, called it "spectacular." When actors from other industries start promoting your film unprompted, the anticipation has moved past marketing into genuine industry curiosity.

## The Telangana Problem (and Chiranjeevi's Fix)

Behind the excitement sits an industry dispute that nearly derailed the film's biggest domestic market. Telangana exhibitors had been locked in a standoff with producers over how ticket revenue gets divided. Unlike the traditional fixed-rental system where theaters pay producers a guaranteed fee upfront, the newer percentage-sharing model splits box office earnings proportionally — a structure already standard in most of India but resisted in Telangana.

Chiranjeevi, Ram Charan's father and arguably the most influential voice in Telugu cinema, personally intervened to broker a resolution. Under the compromise, Telangana theaters have agreed to adopt a revenue-sharing model effective July 3, with *Peddi* among the first major releases to operate under this framework. A June 30 deadline has been set for finalizing terms. The political undercurrents — Chiranjeevi's own political history in Andhra Pradesh, the family's influence across Telugu media — make this more than a business negotiation.

## What to Expect

*Peddi* is not a small film pretending to be big. The budget is massive, the runtime is long enough to require an intermission, and the film sits in a genre — rural sports drama — that carries both enormous potential and specific risks. *Dangal* proved the genre could cross ₹2,000 crore worldwide. *Liger* proved it could also fall flat.

For NRIs who watched Ram Charan dance across the world stage in *RRR* and then waited four years for his return, *Peddi* is the real test: whether the goodwill translates at the box office for a film that is unapologetically Telugu, unapologetically long, and unapologetically rooted in a world that does not look like a Marvel set. AR Rahman's involvement adds another layer — the Oscar-winning composer has been selective with his commitments, and his presence signals genuine artistic ambition beyond star power.

June 4 will answer the question. The tickets are already selling."""
    
    sources = [
        {"name": "Sacnilk", "url": "https://sacnilk.com"},
        {"name": "Bollywood Hungama", "url": "https://bollywoodhungama.com"},
        {"name": "Pinkvilla", "url": "https://pinkvilla.com"},
        {"name": "Tupaki", "url": "https://english.tupaki.com"}
    ]
    
    return {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": "ram-charan-peddi-june-4-ar-rahman-175-million-views-north-america-advance-booking-nri-20260528",
        "sources": sources,
        "image_url": img or "",
        "image_caption": img_caption,
        "image_attribution": img_attr,
        "tags": ["Ram Charan", "Peddi", "AR Rahman", "Telugu cinema", "box office", "Chiranjeevi", "Janhvi Kapoor"]
    }


# ─────────────────────────────────────────────
# ARTICLE 2: South Indian Exhibitors OTT Window
# ─────────────────────────────────────────────

def write_ott_window_article():
    print("\n📝 Article 2: South Indian Exhibitors OTT Window")
    
    # Try for a relevant image
    img = fetch_pexels_image("movie theater India audience", "cinema hall India")
    img_attr = "Pexels"
    img_caption = "South Indian exhibitors have mandated an eight-week gap before films can move to streaming platforms"
    
    if not img or not validate_image(img):
        img = ""
        img_caption = ""
        img_attr = ""
    
    headline = "South Indian Exhibitors Just Mandated an Eight-Week OTT Window. If You Watch Films on Netflix, This Changes Everything."
    subheadline = "The new rule forces all South Indian films to stay off streaming platforms for two full months after theatrical release — a direct challenge to the NRI habit of waiting for OTT."
    
    body = """Here is what used to happen: a Telugu or Tamil film would open in theaters, run for two or three weeks, and then quietly appear on Netflix or JioHotstar for the rest of us to watch at home. The theatrical-to-OTT pipeline was fast, informal, and — for diaspora audiences who could not always get to an Indian film screening — essential.

That pipeline just got a wall built across it.

South Indian exhibitors have formally mandated an eight-week OTT window for all films released across Telugu, Tamil, Malayalam, and Kannada markets. No exceptions. No quiet side deals. Eight full weeks between the day a film opens in theaters and the day it can legally stream on any platform. Alongside this, exhibitors have pushed through a shift from the traditional fixed-rental model to a revenue-sharing arrangement, fundamentally changing how risk and reward are distributed between producers and theater owners.

## Why This Matters for NRIs

The four-week OTT window that informally governed much of South Indian cinema was a lifeline for diaspora audiences. If you live in Houston or London or Toronto and the nearest theater showing a Kannada film is two hours away, the knowledge that it would land on streaming within a month made the wait bearable. That wait just doubled.

This is not new territory — Bollywood multiplexes implemented an eight-week window in 2022, and the Hindi film industry has largely operated under this framework since. But South Indian cinema's adoption is significant because it produces the most internationally consumed Indian content right now. Tamil, Telugu, Malayalam, and Kannada films now regularly outperform Bollywood at global box offices. *Kara*, Dhanush's heist thriller which just landed on Netflix on May 28 after roughly four weeks in theaters, might be among the last South Indian films to arrive on streaming this quickly.

The impact will be felt most sharply by NRI families who subscribe to JioHotstar or Netflix primarily for Indian content. The value proposition of those subscriptions depends on a steady stream of relatively fresh theatrical releases. An eight-week delay does not eliminate the content — it just pushes it into a limbo where films are no longer in theaters and not yet on streaming. For audiences outside India, that limbo can feel permanent.

## The Revenue-Sharing Shift

The OTT window change comes bundled with a structural shift in how theaters pay producers. Under the old fixed-rental model, exhibitors paid a guaranteed fee upfront for the right to screen a film, regardless of how many tickets they sold. This protected producers from box office risk but left exhibitors bearing all the downside when a film flopped.

The new revenue-sharing model distributes the economics more evenly. Both sides benefit when a film does well and both absorb losses when it does not. This model has long been standard in North America, Europe, and the Hindi-speaking belt, and its adoption in South India aligns the world's most prolific film-producing region with global theatrical norms. The transition has not been seamless — in Telangana, Chiranjeevi personally intervened to broker a deal for Ram Charan's *Peddi* ahead of its June 4 release, suggesting the new model is being negotiated film by film rather than blanket-adopted.

## Who Benefits, Who Loses

Theater owners benefit the most. The eight-week window gives films more room to run, boosting second- and third-week footfalls that had been decimated by the rush to OTT. For films with strong word-of-mouth — the kind that South Indian cinema frequently produces — the longer window can translate to significantly higher lifetime collections. *Bhooth Bangla*, Akshay Kumar's horror comedy, is currently in its sixth week and still earning ₹5+ crore net per week. That kind of long-tail performance only happens when OTT is not an option yet.

Producers with big-budget tentpoles benefit too. A film like *Peddi* or *Toxic*, both opening June 4, will have two full months of theatrical exclusivity before any streaming deal kicks in. For films that cost hundreds of crores, that runway can make the difference between a hit and a disaster.

The losers are mid-budget filmmakers who depend on OTT acquisition deals to recoup costs, and diaspora audiences who will now face a longer wait with fewer options for catching up on films that have already left their nearest theater. The compromise is pragmatic but imperfect. The Indian theatrical ecosystem genuinely needs protection from a streaming industry that was cannibalizing its runway. But the diaspora streaming habit — built over a decade of increasingly fast theatrical-to-OTT pipelines — has been acknowledged as collateral damage rather than a constituency worth protecting."""
    
    sources = [
        {"name": "Sacnilk", "url": "https://sacnilk.com/news/South_Indian_Exhibitors_Mandate_8_Week_OTT_Window_and_Shift_to_Revenue_Sharing_Model_for_All_Films"},
        {"name": "Pinkvilla", "url": "https://pinkvilla.com"},
        {"name": "Bollywood Hungama", "url": "https://bollywoodhungama.com"}
    ]
    
    return {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": "south-indian-exhibitors-eight-week-ott-window-revenue-sharing-nri-streaming-impact-20260528",
        "sources": sources,
        "image_url": img or "",
        "image_caption": img_caption,
        "image_attribution": img_attr,
        "tags": ["OTT", "streaming", "Netflix", "JioHotstar", "South Indian cinema", "exhibitors", "NRI"]
    }


# ─────────────────────────────────────────────
# ARTICLE 3: Bollywood's 18-Month Commitment Era
# ─────────────────────────────────────────────

def write_mega_tentpole_article():
    print("\n📝 Article 3: Bollywood's Mega-Tentpole Era")
    
    # Wikipedia images for Vicky Kaushal
    img = fetch_wikipedia_person_image("Vicky Kaushal")
    img_caption = "Vicky Kaushal"
    img_attr = "Wikimedia Commons"
    
    if not img or not validate_image(img):
        img = fetch_wikipedia_person_image("Ranveer Singh")
        img_caption = "Ranveer Singh"
        if not img or not validate_image(img):
            img = ""
            img_caption = ""
            img_attr = ""
    
    headline = "Vicky Kaushal Has Blocked 18 Months of His Life for One Film. Ranveer Singh Is Spending ₹300 Crore on Zombies. This Is Bollywood Now."
    subheadline = "Mahavatar and Pralay signal a new era where India's biggest male stars are betting their entire schedules on single, massive, world-building projects — just like Hollywood's franchise actors."
    
    body = """There was a time when a Bollywood superstar did four films a year. Two big releases, one multi-starrer, and maybe a cameo somewhere. The math was simple: more films meant more chances at a hit.

That math is dead.

Vicky Kaushal has blocked eighteen months — from June 2026 to December 2027 — exclusively for *Mahavatar*, a mythological epic in which he will play the immortal sage-warrior Parashurama. Six of those months are preparation: physical transformation, intensive workshops, and deep character immersion under the guidance of director Amar Kaushik, who previously directed the blockbuster *Stree* franchise. The remaining twelve months are principal photography. During this entire period, Kaushal will not take on any other film. He wraps Sanjay Leela Bhansali's *Love and War* just in time, and then he disappears into one role. Writer Niren Bhatt, who penned the screenplay, has described the preparation as the most intense he has witnessed for any Indian film.

Meanwhile, Ranveer Singh — riding the historic, record-breaking success of the *Dhurandhar* franchise — has locked in *Pralay*, a post-apocalyptic zombie thriller directed by Jai Mehta. The budget: ₹300 crore. The production plan, beginning in August 2026: AI-driven visuals merged with physical sets to create a dystopian India unlike anything the industry has attempted. South Indian actress Kalyani Priyadarshan, daughter of director Priyadarshan (who incidentally just gave Akshay Kumar his biggest hit in years with *Bhooth Bangla*), makes her Hindi debut opposite Singh. Recent rumors about creative differences on the project were shot down by a Variety India report confirming the film is fully on track.

This is not a coincidence. This is a pattern.

## The Tentpole Calendar

Look at the production calendar for India's top male stars and the picture becomes clear. Ranbir Kapoor has been embedded inside *Ramayana* for over a year, a film so large it required AR Rahman and Hans Zimmer to co-compose the score and has its release date preponed to late October — a week before Diwali. Mahesh Babu is locked inside Rajamouli's *SSMB29* for what will likely be a two-year commitment. Aamir Khan just blocked time for an Ashutosh Gowariker cricket biopic about Lala Amarnath starting October 2026, followed by the *3 Idiots* sequel pushed to mid-2027. Yash's *Toxic* alone absorbed over two years of his schedule.

Every major male star in Indian cinema is now operating on the Hollywood tentpole model: one massive project at a time, years of exclusive commitment, budgets that would have funded an entire studio's annual slate a decade ago. The four-films-a-year era produced stars who were constantly visible but rarely transcendent. The new model bets on scarcity and scale.

## What This Means for NRI Audiences

For diaspora viewers, the shift cuts both ways. The upside: the films that do eventually arrive will be genuinely ambitious, globally competitive productions designed to play on IMAX screens in Edison and Brampton, not just in Bandra. The quality ceiling is rising. When Vicky Kaushal emerges from eighteen months of single-minded preparation, the expectation is that what he delivers will justify the wait.

The downside: the pipeline is thinning. With top stars locked into singular mega-projects, the volume of star-driven Hindi films is dropping noticeably. The mid-budget star vehicle — the kind that kept NRI multiplex screens reliably stocked year-round — is becoming genuinely rare. The result is feast-or-famine: months of nothing from your favorite actor, followed by a single massive release that either justifies the wait or makes the gap feel wasted. There is no middle ground anymore.

## The Risk Nobody Talks About

Every one of these bets carries existential risk. *War 2* was supposed to be Hrithik Roshan and Jr NTR's tentpole event. It opened strong and then collapsed, grossing ₹365 crore worldwide against expectations of ₹500+ crore — technically profitable but widely viewed as a disappointment that dented the Spy Universe brand. When your entire multi-year schedule depends on a single film landing, the margin for creative error shrinks to nothing.

Vicky Kaushal's *Mahavatar* is a mythological epic in a market where recent mythological epics — *Adipurush* chief among them — have catastrophically misfired on visual execution. Ranveer Singh's *Pralay* is a zombie film in a country that has never produced a successful zombie franchise. Neither project is a safe bet by any conventional industry calculus.

But safe bets are exactly what these actors are running from. The four-films-a-year model produced forgettable content and exhausted audiences with overexposure. The new model asks a fundamentally different question: what if you gave everything to one film, spent years inside it, and made it impossible to ignore?

We will find out. Just not for another eighteen months."""
    
    sources = [
        {"name": "Sacnilk", "url": "https://sacnilk.com/news/bollywood-buzz-ranveer-singhs-pralay-shoot-begins-in-august-2026-as-vicky-kaushal-blocks-18-months-for-mahavatar"},
        {"name": "Pinkvilla", "url": "https://pinkvilla.com"},
        {"name": "Variety India", "url": "https://variety.com"}
    ]
    
    return {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": "vicky-kaushal-mahavatar-ranveer-singh-pralay-bollywood-mega-tentpole-era-nri-20260528",
        "sources": sources,
        "image_url": img or "",
        "image_caption": img_caption,
        "image_attribution": img_attr,
        "tags": ["Vicky Kaushal", "Ranveer Singh", "Mahavatar", "Pralay", "Bollywood", "tentpole", "Ranbir Kapoor", "Aamir Khan"]
    }


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("🎬 The Videshi Entertainment Writer — 2026-05-28 Evening Run")
    print("=" * 60)
    
    articles = []
    
    # Write all 3 articles
    articles.append(write_peddi_article())
    time.sleep(2)  # Avoid Wikipedia rate limiting
    articles.append(write_ott_window_article())
    time.sleep(2)
    articles.append(write_mega_tentpole_article())
    
    # Validate and publish
    published = 0
    for i, article in enumerate(articles, 1):
        print(f"\n{'='*60}")
        print(f"Publishing article {i}/{len(articles)}: {article['headline'][:60]}...")
        
        # Validate
        h_len = len(article['headline'])
        sh_len = len(article['subheadline'])
        body_words = len(article['body'].split())
        
        print(f"  Headline: {h_len} chars (20-200 required)")
        print(f"  Subheadline: {sh_len} chars (15+ required)")
        print(f"  Body: {body_words} words (600-800+ target, 400 floor)")
        print(f"  Slug: {article['slug']}")
        print(f"  Image: {'Yes' if article['image_url'] else 'No'}")
        
        if h_len < 20 or h_len > 200:
            print(f"  ⚠ Headline length out of range!")
        if sh_len < 15:
            print(f"  ⚠ Subheadline too short!")
        if body_words < 400:
            print(f"  ✗ Body too short! Skipping.")
            continue
        
        if publish_article(article):
            published += 1
        
        time.sleep(1)  # Rate limiting
    
    print(f"\n{'='*60}")
    print(f"✅ Published {published}/{len(articles)} articles")
    print("🎬 Entertainment writer run complete.")
