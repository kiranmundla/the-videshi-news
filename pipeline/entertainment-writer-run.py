#!/usr/bin/env python3
"""Entertainment writer for The Videshi — June 3, 2026 run."""

import json
import os
import re
import subprocess
import sys
import time
import uuid
import requests
import urllib.parse
from datetime import datetime, timezone

# Load Supabase env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    key = key.replace('export ', '').strip()
                    val = val.strip().strip('"').strip("'")
                    os.environ[key] = val

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY')

HEADERS_SB = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

UA = 'TheVideshi/1.0 (thevideshi.com)'

# ── Image sourcing functions ──

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA},
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


def fetch_wikimedia_commons_images(search_query, limit=5):
    """Search Wikimedia Commons for CC-licensed images. Returns list of image URLs."""
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json"
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params,
            headers={"User-Agent": UA},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                for ii in page.get("imageinfo", []):
                    url = ii.get("thumburl") or ii.get("url")
                    mime = ii.get("mime", "")
                    if url and "image" in mime and not url.endswith('.svg'):
                        results.append(url)
            if results:
                print(f"  ✓ Wikimedia Commons found {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error for '{search_query}': {e}")
    return []


def fetch_pexels_image(query):
    """Search Pexels for an image. Uses curl to avoid 403."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    try:
        result = subprocess.run(
            ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
             f'https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3'],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        photos = data.get('photos', [])
        if photos:
            url = photos[0]['src']['large2x']
            print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
            return url
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None


def validate_image(url):
    """Validate that an image URL is accessible and not tiny."""
    try:
        r = requests.head(url, headers={"User-Agent": UA}, timeout=10, allow_redirects=True)
        content_type = r.headers.get('Content-Type', '')
        content_length = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in content_type and content_length > 5000:
            return True
        # Try GET as fallback for servers that don't support HEAD well
        r2 = requests.get(url, headers={"User-Agent": UA}, timeout=10, stream=True)
        ct = r2.headers.get('Content-Type', '')
        cl = int(r2.headers.get('Content-Length', 0))
        if r2.status_code == 200 and 'image' in ct:
            # Read a bit to check size
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                return True
    except:
        pass
    return False


def find_best_image(person_name=None, topic_queries=None, pexels_query=None):
    """Multi-source image search. Returns (url, attribution) or (None, None)."""
    candidates = []

    # Wikipedia person image
    if person_name:
        wp = fetch_wikipedia_person_image(person_name)
        if wp and validate_image(wp):
            candidates.append((wp, "Wikimedia Commons"))

    # Wikimedia Commons search
    if topic_queries:
        for q in topic_queries:
            commons = fetch_wikimedia_commons_images(q, limit=3)
            for url in commons:
                if validate_image(url):
                    candidates.append((url, "Wikimedia Commons"))
                    break  # Take best per query

    # Pexels fallback
    if pexels_query and not candidates:
        px = fetch_pexels_image(pexels_query)
        if px and validate_image(px):
            candidates.append((px, "Pexels"))

    if candidates:
        return candidates[0]
    return None, None


def insert_article(article):
    """Insert article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS_SB,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            print(f"  ✓ Published: {data[0].get('headline', '')[:60]}")
            return True
        print(f"  ✓ Published (no return data)")
        return True
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return False


# ── ARTICLE 1: Peddi — Ram Charan's Biggest Bet ──

def write_peddi_article():
    print("\n📝 Article 1: Ram Charan's Peddi")

    # Image: Ram Charan
    img_url, img_attr = find_best_image(
        person_name="Ram Charan",
        topic_queries=["Ram Charan actor", "Ram Charan Peddi film"],
        pexels_query=None  # No generic stock
    )

    headline = "Ram Charan's Peddi Opens in America Before India. The Advance Numbers Suggest Telugu Cinema's Next Blockbuster Has Already Arrived."
    subheadline = "With ₹40 crore in global pre-sales, 28,000 tickets sold across 533 US locations, and premiere shows starting tonight in North America, Peddi is tracking toward the $1 million premiere club that only a dozen Telugu films have ever entered."

    body = """Ram Charan's new sports-action drama *Peddi* hasn't technically released yet, and it's already breaking records.

As of Tuesday evening, global advance bookings for the film have crossed ₹40 crore. North American premiere pre-sales alone have reached $870,000, with 31,237 tickets sold across hundreds of locations. Trade analysts expect the number to blow past $1 million before the first credit rolls — a milestone that would place Peddi alongside Baahubali 2, RRR, Kalki 2898 AD, and Pushpa 2 in an exclusive club of Telugu films that cracked seven figures in US premiere pre-sales.

The film opens tonight in the United States, hours before Indian audiences get their first look. Premiere shows across North America are scheduled for 9:40 AM EST on June 3, which translates to roughly 7:10 PM IST — giving American Telugu audiences a full night's head start on the verdict. In the Telugu states, first-day-first-show screenings begin at 7 AM on June 4. At one point during the booking window, BookMyShow was selling over 40,000 tickets per hour.

## Three Athletes, One Actor

Directed by Buchi Babu Sana, Peddi casts Ram Charan in three distinct crossover athlete avatars — cricketer, runner, and wrestler — all woven into a story set in rural Andhra Pradesh. The film reportedly draws inspiration from sporting legends including MS Dhoni and Sachin Tendulkar. Ram Charan spent nearly a month filming wrestling sequences with real pehelwans rather than stunt doubles, and reportedly suffered a cartilage tear in the process. The final cut runs a meaty 3 hours and 9 minutes — a bet on audience patience that Telugu cinema's biggest blockbusters have historically rewarded.

The supporting cast is stacked: Janhvi Kapoor plays the female lead opposite Charan, with Kannada icon Shiva Rajkumar in a key role alongside Jagapathi Babu, Divyenndu Sharma, and Boman Irani. A.R. Rahman handles the music — his tracks "Chikiri Chikiri," "Rai Rai Rae Raa," and the newly released "Massa Massa" and "Hellallallo" have already generated significant pre-release buzz.

## The Diaspora Angle

For NRIs, Peddi's release strategy is unusually telling. The film's US premiere precedes India's, a move that underscores just how critical the North American Telugu diaspora has become to a big-budget film's financial calculus. Texas alone has contributed over $164,000 in advance sales, followed by California and Virginia — the three states with the largest Telugu-speaking populations in America.

Cinemark is leading the chain-by-chain breakdown with nearly $300,000 in sales, followed by Regal and AMC. Premium format screenings — IMAX, XD, RPX, and D-Box — account for a disproportionate share of revenue, suggesting audiences are treating this less as a casual weeknight outing and more as an event.

## What's at Stake

Peddi is Ram Charan's first release since Game Changer, and the expectations are immense. The film is produced by Vriddhi Cinemas and IVY Entertainment, presented by Mythri Movie Makers and Sukumar Writings — a production pedigree that signals confidence. Cinematography by Ratnavelu, editing by Navin Nooli, and visual effects by Sanath PC round out a technical team assembled for scale.

For Buchi Babu Sana, this is a career-defining moment. His debut film, *Uppena*, was a modest hit. This is something else entirely — a ₹200+ crore bet on whether a rural sports drama can hold its own in a summer crowded with franchise sequels and OTT drops.

The American audience gets to decide first. By tomorrow morning IST, the world will know whether Peddi delivers on its promise or whether the advance numbers were writing checks the film couldn't cash.

**Sources:** ZoomTV Entertainment, Sacnilk (Venky Box Office tracking), Filmibeat, SpotboyE"""

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": "ram-charan-peddi-advance-booking-usa-premiere-north-america-1-million-nri-20260603",
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "is_editorial": False,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": img_url,
        "image_attribution": img_attr,
        "sources": json.dumps(["ZoomTV Entertainment", "Sacnilk", "Filmibeat", "SpotboyE"]),
    }
    if not img_url:
        print("  ⚠ No valid image found — skipping image_url")
        del article["image_url"]
        del article["image_attribution"]

    return insert_article(article)


# ── ARTICLE 2: Mindy Kaling's Not Suitable for Work ──

def write_mindy_kaling_article():
    print("\n📝 Article 2: Mindy Kaling's Not Suitable for Work")

    img_url, img_attr = find_best_image(
        person_name="Mindy Kaling",
        topic_queries=["Mindy Kaling actress"],
        pexels_query=None
    )

    headline = "Mindy Kaling's New Show Has an Indian-American Lead, a 56% on Rotten Tomatoes, and the Weight of a Generation's Expectations."
    subheadline = "Not Suitable for Work premiered on Hulu this week with Avantika playing Abhinaya 'Abby' Chilukuri — a rare South Asian lead in a mainstream network comedy. Critics are divided. The audience hasn't decided yet."

    body = """Mindy Kaling has made a career out of putting brown faces in rooms where Hollywood traditionally didn't seat them. Her latest attempt is *Not Suitable for Work*, a nine-episode comedy about five 20-somethings navigating careers and love in Manhattan's Murray Hill. It premiered on Hulu on June 2 — and landed with a thud on the review aggregators.

At the time of writing, the show sits at 56% on Rotten Tomatoes. That's a notable step down from Kaling's track record: *Never Have I Ever* earned a 94% across four seasons, *The Sex Lives of College Girls* held at 73%, and *Running Point* opened at 84%. The audience score hasn't fully materialized yet, but early viewer reactions range from enthusiastic ("Mindy has a way of writing characters that feel real but also very funny") to dismissive ("I don't know if this generation is actually this lame and dorky or if it's just this show").

## What It Is

The show follows two sets of roommates living in the same Manhattan apartment building. In one unit: AJ Pascarelli (Ella Hunt), a laser-focused finance newcomer from Boston, and Abhinaya "Abby" Chilukuri (Avantika), an assistant to a demanding celebrity stylist played by Constance Wu. Across the hall: three men including Josh Haywood (Jack Martin), the secretly privileged son of a media CEO, and Davis Cooper (Nicholas Duvernay), a finance professional who immediately falls for AJ.

For the Indian diaspora, the casting is the headline. Avantika — who broke through in *Mean Girls* (2024) — plays a fully written South Asian character whose identity isn't the joke, the obstacle, or the lesson. Abby's Indianness is present without being performed. It's the kind of representation Kaling has been building toward for over a decade, and it's worth noting even if the vehicle isn't perfect.

## What Critics Are Saying

The notices are genuinely split. *The Hollywood Reporter* called it "a nice hang" with "an ensemble that is broadly appealing." *The LA Times* praised it as "an amiable, sweet-tempered romantic ensemble comedy with a heftier than usual emphasis on professional ambition." *The Wrap* described it as "lightweight, frothy" — a compliment and a caveat in the same breath.

The negative reviews are more pointed. *The Guardian* gave it two out of five stars, writing that "Kaling's scripts try hard but rarely shine, let alone dazzle as *Friends*' dialogue almost unfailingly did." *RogerEbert.com* called it "too many clichés to result in anything other than mediocrity." *The A.V. Club* noted it isn't "particularly hilarious" but acknowledged enough "bright spots" to suggest a better show might be hiding inside this one.

*USA Today* identified what might be the core problem: the show's "innocent and sunny version of Gen Z young adulthood is beautiful but unrealistic," in a way that feels "unmistakably phony" against 2026's economic backdrop.

## Why It Matters for the Diaspora

Kaling's work has always functioned as a barometer for South Asian representation in American pop culture. *The Mindy Project* proved a brown woman could headline a network sitcom. *Never Have I Ever* gave a generation of first-gen kids a mirror. *Not Suitable for Work* is trying something subtler — making an Indian-American character part of the ensemble without the show being "about" being Indian-American.

Whether it works is a different question. Kaling created the show and executive produces alongside Charlie Grandy, her longtime collaborator from *The Mindy Project* and *Sex Lives*. New episodes drop in pairs every Tuesday through the season finale on June 23. There's time for the show to find its footing — and time for diaspora audiences to decide whether this particular mirror reflects anything they recognize.

**Sources:** Rotten Tomatoes, The Hollywood Reporter, The Guardian, USA Today, Decider, The A.V. Club, CBR, The Wrap"""

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": "mindy-kaling-not-suitable-for-work-hulu-avantika-indian-american-representation-nri-20260603",
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "is_editorial": False,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": img_url,
        "image_attribution": img_attr,
        "sources": json.dumps(["Rotten Tomatoes", "The Hollywood Reporter", "The Guardian", "USA Today", "Decider", "The A.V. Club"]),
    }
    if not img_url:
        del article["image_url"]
        del article["image_attribution"]

    return insert_article(article)


# ── ARTICLE 3: Governor — Manoj Bajpayee as RBI Governor ──

def write_governor_article():
    print("\n📝 Article 3: Governor — Manoj Bajpayee as RBI Governor")

    img_url, img_attr = find_best_image(
        person_name="Manoj Bajpayee",
        topic_queries=["Manoj Bajpayee actor", "Reserve Bank of India 1991 crisis gold"],
        pexels_query=None
    )

    headline = "Manoj Bajpayee Plays the Man Who Secretly Airlifted India's Gold. Governor Opens June 12."
    subheadline = "The film dramatizes the real story of RBI Governor S. Venkitaramanan, who pledged 60 tons of gold to foreign banks in 1991 to save India from sovereign default — the crisis that opened the door to liberalization and, for millions of NRIs, to the career paths that brought them abroad."

    body = """In 1991, India had roughly two weeks of foreign exchange reserves left. The country was days from defaulting on its international obligations. What happened next — a classified operation to airlift 60 tons of gold from the Reserve Bank of India's vaults and pledge it to the Bank of England and the Union Bank of Switzerland — is one of the most dramatic episodes in modern Indian economic history. It is also, somehow, a story most Indians under 40 have never heard in detail.

*Governor*, starring Manoj Bajpayee, is about to change that. The film opens in theaters on June 12.

## The Real Story

S. Venkitaramanan became RBI Governor in December 1990, walking into what was arguably the worst economic crisis independent India had ever faced. Oil prices had spiked after Iraq's invasion of Kuwait, remittances from the Gulf had collapsed, and India's foreign exchange reserves had fallen below $1 billion — not enough to cover two weeks of imports.

Venkitaramanan's solution was as radical as it was desperate: pledge the nation's gold reserves to international banks to raise approximately $405 million in emergency loans. The operation was carried out in secrecy. Gold was physically transported from RBI vaults to airports and shipped overseas. When word leaked, the political backlash was immediate and brutal — critics called it a national humiliation. But it worked. The emergency liquidity bought time for the broader reforms that Finance Minister Manmohan Singh would announce months later, reforms that opened India's economy to the world.

Venkitaramanan passed away in November 2023 at the age of 92. His obituaries noted the irony: the man who helped save the Indian economy from collapse is far less remembered than the politicians who took credit for the reforms that followed.

## What the Film Does With It

Director Chinmay Mandlekar — best known as an actor in *The Kashmir Files* — has structured *Governor* as a political thriller, not a biopic. Bajpayee plays the RBI Governor as an outsider to the political establishment, a technocrat forced to make decisions that the politicians around him are too afraid or too compromised to make.

Adah Sharma plays a journalist who uncovers the secret gold operation and threatens to blow it open, adding a ticking-clock element to the narrative. The ensemble includes Madhoo and Noushad Mohamed Kunju. Javed Akhtar has written the lyrics, and Amit Trivedi has composed the score — a pairing that hasn't worked together in years and signals creative ambition.

The screenplay is credited to Suvendu Bhattacharyjee, Saurabh Bharat, Ravi Asrani, and producer Vipul Amrutlal Shah. Shah's Sunshine Pictures previously produced *The Kerala Story* franchise, which means *Governor* arrives with both commercial credibility and a certain political charge.

## Why NRIs Should Pay Attention

For the Indian diaspora — particularly the wave of professionals who left India in the 1990s and 2000s — the 1991 crisis isn't ancient history. It's origin story. The liberalization that followed Venkitaramanan's gold gambit is what created the IT boom, the outsourcing industry, the H-1B pipeline, and the economic conditions that made emigration viable for millions of middle-class Indians. The Infosys IPO, the Wipro expansion, the Bangalore tech corridor — none of it happens without the reforms that the gold airlift made possible.

*Governor* releases on June 12, the same day as Imtiaz Ali's *Main Vaapas Aaunga* starring Diljit Dosanjh and Kangana Ranaut's *Bharat Bhhagya Viddhaata*. It's a crowded corridor, but Bajpayee's box office track record with smart mid-budget films — from *12th Fail* to *Sirf Ek Bandaa Kaafi Hai* — suggests there's an audience hungry for stories about real people who made real decisions under impossible pressure.

Whether the film lives up to the source material is for audiences to decide. But the story it's telling — of a country on the brink, a bureaucrat who bet everything, and a secret operation that changed the course of a nation — is one the diaspora should know, whether or not they buy a ticket.

**Sources:** Bollywood Hungama, Filmfare, Cinema Express, IANS"""

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": "governor-manoj-bajpayee-rbi-gold-1991-crisis-venkitaramanan-nri-20260603",
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "is_editorial": False,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": img_url,
        "image_attribution": img_attr,
        "sources": json.dumps(["Bollywood Hungama", "Filmfare", "Cinema Express", "IANS"]),
    }
    if not img_url:
        del article["image_url"]
        del article["image_attribution"]

    return insert_article(article)


# ── Main ──

if __name__ == "__main__":
    print("🎬 The Videshi Entertainment Writer — June 3, 2026")
    print(f"   Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print()

    results = []
    results.append(("Peddi", write_peddi_article()))
    results.append(("Mindy Kaling", write_mindy_kaling_article()))
    results.append(("Governor", write_governor_article()))

    print("\n" + "="*50)
    print("📊 Results:")
    for name, ok in results:
        status = "✓" if ok else "✗"
        print(f"  {status} {name}")

    successes = sum(1 for _, ok in results if ok)
    print(f"\n  {successes}/{len(results)} articles published")

    if successes == 0:
        sys.exit(1)
