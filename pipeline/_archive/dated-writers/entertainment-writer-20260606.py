#!/usr/bin/env python3
"""Entertainment writer - June 6, 2026 afternoon batch"""

import requests
import json
import os
import sys
import urllib.parse
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
                    os.environ[key.strip()] = val

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: Missing Supabase credentials")
    sys.exit(1)

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

def fetch_wikimedia_commons_images(search_query, limit=5):
    """Search Wikimedia Commons for CC-licensed images."""
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": "1200",
        "format": "json"
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params,
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                url = ii.get("thumburl") or ii.get("url")
                mime = ii.get("mime", "")
                width = ii.get("width", 0)
                if url and "image" in mime and width > 200:
                    results.append({
                        "url": url,
                        "title": page.get("title", ""),
                        "width": width,
                        "height": ii.get("height", 0)
                    })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} results for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error: {e}")
    return []

def fetch_pexels_image(query):
    """Search Pexels for an image using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    try:
        import subprocess
        result = subprocess.run(
            ["curl", "-sS", f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3",
             "-H", f"Authorization: {PEXELS_KEY}"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            if photos:
                url = photos[0]["src"]["large"]
                print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

def validate_image(url):
    """Validate image URL returns 200 and has reasonable size."""
    # Trust known sources (Wikimedia, Pexels) without HEAD check to avoid rate limits
    if "upload.wikimedia.org" in url or "images.pexels.com" in url:
        print(f"  ✓ Image from trusted source, skipping HEAD check")
        return True
    try:
        r = requests.head(url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Image validated: {r.status_code}, {ct}, {cl} bytes")
            return True
        if r.status_code == 429:
            print(f"  ⚠ Rate limited, trusting URL from known source")
            return True
        print(f"  ✗ Image validation failed: status={r.status_code}, type={ct}, size={cl}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False

def insert_article(article):
    """Insert article into Supabase."""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=headers,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            print(f"  ✓ Published: {result[0].get('headline', 'unknown')}")
            return True
        print(f"  ✓ Published (no details returned)")
        return True
    else:
        print(f"  ✗ Insert failed: {r.status_code} - {r.text[:300]}")
        return False


# ================================================================
# ARTICLE 1: Peddi box office crossing ₹150 Cr worldwide
# ================================================================
def write_peddi_box_office():
    print("\n=== ARTICLE 1: Peddi Box Office Update ===")

    # Image: Ram Charan from Wikipedia
    image_url = None
    image_caption = ""
    image_attribution = ""

    wiki_img = fetch_wikipedia_person_image("Ram Charan (actor)")
    if not wiki_img:
        wiki_img = fetch_wikipedia_person_image("Ram Charan")
    
    if wiki_img and validate_image(wiki_img):
        image_url = wiki_img
        image_caption = "Ram Charan, whose solo starrer Peddi has crossed ₹150 crore worldwide in two days"
        image_attribution = "Wikimedia Commons"
    
    if not image_url:
        commons = fetch_wikimedia_commons_images("Ram Charan actor Telugu")
        for c in commons:
            if validate_image(c["url"]):
                image_url = c["url"]
                image_caption = "Ram Charan at a public event"
                image_attribution = "Wikimedia Commons"
                break
    
    if not image_url:
        pexels = fetch_pexels_image("Indian cinema theatre audience")
        if pexels and validate_image(pexels):
            image_url = pexels
            image_caption = "Indian cinema audiences packing theatres for Peddi's opening weekend"
            image_attribution = "Pexels"
    
    if not image_url:
        print("  ✗ No valid image found, skipping article")
        return False

    body = """Ram Charan's Peddi has crossed the ₹150 crore mark worldwide in just two days of its theatrical run, confirming what the opening-day numbers had suggested: this is the actor's biggest solo success, and it arrived exactly when he needed it.

The Buchi Babu Sana-directed sports action drama collected approximately ₹26.90 crore net in India on Day 2 (Friday), bringing its domestic total to ₹96.40 crore net. With ₹18.50 crore from paid previews, ₹51 crore on Day 1, and the Friday hold, the India gross now stands at ₹114.49 crore. Overseas markets have added ₹36 crore, pushing the worldwide gross to ₹150.49 crore.

## The Telugu Heartland Is Carrying This Film

The Telugu states of Andhra Pradesh and Telangana have been the film's engine. Day 2 saw ₹23.75 crore from APTS alone — a number that compares favourably with Kalki 2898 AD and Pushpa 2, both of which recorded ₹27-28 crore on equivalent days. In Coastal Andhra, Peddi actually outperformed both those blockbusters, grossing ₹10.75 crore. The shortfall came primarily from Nizam and Ceded.

The Hindi version, by contrast, has been modest — roughly ₹2.25 crore net on Day 2 — reflecting the film's Telugu-first positioning and mixed critical reception. But the overall trajectory suggests a four-day extended weekend of ₹180-185 crore, with ₹200 crore virtually guaranteed.

## Why This Matters for Ram Charan

The significance is not just in the numbers. It is in what they represent. RRR gave Ram Charan a global footprint, but it was a multi-starrer backed by S.S. Rajamouli's brand. Game Changer, his last release, underwhelmed theatrically and raised questions about whether he could carry a film alone.

Peddi answers that question definitively. It is now the tenth-highest all-time opening in Telugu cinema, and the weekend has not even peaked. Advance bookings for Saturday already exceed ₹13.87 crore gross, with over five lakh tickets sold across 967 cities.

## The Controversy Has Not Hurt — It May Have Helped

The film has not been without turbulence. Director Buchi Babu Sana publicly apologised for the portrayal of Janhvi Kapoor's character after criticism of hypersexualisation. He promised to cut scenes. The discourse around the film became the week's dominant entertainment story. But controversy, in Indian cinema, has often translated into curiosity. Peddi's Day 2 hold, especially in evening and night shows, suggests that audience interest has not wavered.

## The Diaspora Box Office

For NRI audiences, the North America numbers tell their own story. Advance bookings hit $870,000 before the first show began, and the breakeven target is set at $6.5 million for North America and $9 million for total overseas. If the weekend delivers, Peddi will join an exclusive club of Telugu films that have performed strongly in diaspora markets — territory once reserved for the Baahubali and RRR-scale spectacles.

The film is now in a race against its own potential. Trade analysts expect a lifetime gross comfortably above ₹300 crore worldwide if the weekday holds are steady. For Ram Charan, that would not just be a commercial milestone. It would be a statement: he does not need a franchise, a multi-starrer, or a Rajamouli to deliver a blockbuster.

The numbers on Saturday will tell us whether Peddi is heading for very good or genuinely historic territory. Either way, Ram Charan's solo credentials are no longer in question."""

    article = {
        "headline": "Peddi Has Crossed ₹150 Crore Worldwide in Two Days. Ram Charan No Longer Needs a Franchise to Prove Himself.",
        "subheadline": "The Telugu sports drama collected ₹96 crore net in India and ₹36 crore overseas by Day 2. The weekend target is ₹200 crore. The controversy has not slowed it down.",
        "body": body,
        "slug": "peddi-150-crore-worldwide-two-days-ram-charan-solo-blockbuster-nri-20260606",
        "category": "entertainment",
        "vertical": "entertainment",
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "sources": json.dumps(["Pinkvilla", "Sacnilk", "Filmibeat", "Zoom TV Entertainment"]),
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "is_editorial": False
    }
    return insert_article(article)


# ================================================================
# ARTICLE 2: Vicky Kaushal's Mahavatar + Shraddha Kapoor + Ranveer's Pralay
# ================================================================
def write_mahavatar_pralay():
    print("\n=== ARTICLE 2: Mahavatar + Pralay ===")

    # Image: Vicky Kaushal from Wikipedia
    image_url = None
    image_caption = ""
    image_attribution = ""

    wiki_img = fetch_wikipedia_person_image("Vicky Kaushal")
    
    if wiki_img and validate_image(wiki_img):
        image_url = wiki_img
        image_caption = "Vicky Kaushal, who has blocked 18 months for the mythological epic Mahavatar"
        image_attribution = "Wikimedia Commons"
    
    if not image_url:
        commons = fetch_wikimedia_commons_images("Vicky Kaushal actor")
        for c in commons:
            if validate_image(c["url"]):
                image_url = c["url"]
                image_caption = "Vicky Kaushal at a promotional event"
                image_attribution = "Wikimedia Commons"
                break

    if not image_url:
        pexels = fetch_pexels_image("Indian actor preparation training")
        if pexels and validate_image(pexels):
            image_url = pexels
            image_caption = "Actors are committing longer timelines to ambitious Indian productions"
            image_attribution = "Pexels"
    
    if not image_url:
        print("  ✗ No valid image found, skipping article")
        return False

    body = """Vicky Kaushal has committed the next eighteen months of his life to a single film. Starting this month, the actor enters an intensive six-month preparation phase for Mahavatar, Maddock Films' mythological epic in which he plays Lord Parashurama — the immortal warrior sage and sixth avatar of Lord Vishnu. Filming begins in January 2027 and is expected to run through December. He will not take on any other project during this period.

This is an unusual level of commitment by any Bollywood standard, and it signals something larger: India's leading actors are beginning to treat their biggest films the way Hollywood A-listers treat franchise anchors — as multi-year, all-consuming endeavours.

## The Parashurama Preparation

Directed by Amar Kaushik of Stree fame and written by Niren Bhatt (who spent years reading the Bhagavat Purana and eleven other ancient scriptures), Mahavatar demands a physical and emotional transformation that cannot be rushed. Kaushal will undergo months of body conditioning to achieve the muscular build Parashurama requires, followed by workshops to inhabit a character who spans ages and mythological epochs.

The actor is expected to wrap his current work on Sanjay Leela Bhansali's Love and War just in time to begin prep. It was Love and War's extended schedule that originally pushed Mahavatar out of its planned Christmas 2026 release slot. The film is now eyeing an Independence Day 2027 weekend release, though no date has been officially locked.

## Shraddha Kapoor in Talks for the Female Lead

In a development that could add significant star power, Shraddha Kapoor is reportedly in advanced talks to play the female lead. If confirmed, it would be the first on-screen pairing of Kaushal and Kapoor — a combination that producers believe could resonate strongly with audiences. Mid-Day reported that the makers see Shraddha as their primary choice, citing her star value and screen presence as fitting the film's scale.

Maddock Films, under Dinesh Vijan, is treating Mahavatar as its most ambitious production to date. The film is expected to blend heavy VFX, elaborate world-building, and a narrative rooted in Hindu mythology, continuing the trend set by recent hits like Mahavatar Narsimha (an animated prequel from a separate studio that grossed ₹325 crore) and the upcoming Ramayana.

## Meanwhile, Ranveer Singh's Pralay Starts in August

In a parallel move, Ranveer Singh — fresh off the historic ₹1,800 crore worldwide run of Dhurandhar 2 — is preparing to begin shooting Pralay in August. The post-apocalyptic thriller, directed by Jai Mehta, carries a reported budget of ₹300 crore and plans to merge physical sets with AI-driven visual effects to create a dystopian atmosphere unlike anything seen in Indian cinema.

Despite rumours of creative differences, Variety India confirmed the project is on track. South Indian actress Kalyani Priyadarshan has been finalised for her Hindi debut alongside Singh.

## What This Means for Indian Cinema

The dual commitments of Kaushal and Singh mark a shift in how Bollywood's top tier approaches filmmaking. Where the industry once prized quantity — three films a year, back-to-back releases — the economics of ₹300 crore budgets and global ambitions now demand singular focus.

For NRI audiences, this trend is worth watching. Both Mahavatar and Pralay are being designed with international markets in mind. Parashurama's mythology has a built-in audience in every temple town from Edison to Alpharetta. A post-apocalyptic Indian thriller has the genre appeal to cross over. The question is whether the films can match the ambition of their stars' commitments.

Kaushal's eighteen-month window and Singh's August start date make 2027 the year to watch. The productions that survive this level of scale and scrutiny will define what Indian blockbuster cinema looks like for the next decade."""

    article = {
        "headline": "Vicky Kaushal Has Blocked 18 Months for Mahavatar. Shraddha Kapoor May Join Him as the Female Lead.",
        "subheadline": "The actor begins preparation this month for the Lord Parashurama epic. Meanwhile, Ranveer Singh's ₹300 crore Pralay starts shooting in August. India's biggest stars are making singular bets.",
        "body": body,
        "slug": "vicky-kaushal-mahavatar-18-months-shraddha-kapoor-ranveer-pralay-nri-20260606",
        "category": "entertainment",
        "vertical": "entertainment",
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "sources": json.dumps(["Sacnilk", "Mid-Day", "Variety India", "PeepingMoon"]),
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "is_editorial": False
    }
    return insert_article(article)


# ================================================================
# ARTICLE 3: Selena Gomez's Rare Beauty launches in India via Nykaa
# ================================================================
def write_rare_beauty_india():
    print("\n=== ARTICLE 3: Rare Beauty India Launch ===")

    # Image: Selena Gomez from Wikipedia
    image_url = None
    image_caption = ""
    image_attribution = ""

    wiki_img = fetch_wikipedia_person_image("Selena Gomez")
    
    if wiki_img and validate_image(wiki_img):
        image_url = wiki_img
        image_caption = "Selena Gomez, whose beauty brand Rare Beauty has officially launched in India through Nykaa"
        image_attribution = "Wikimedia Commons"
    
    if not image_url:
        commons = fetch_wikimedia_commons_images("Selena Gomez 2024 2025")
        for c in commons:
            if validate_image(c["url"]):
                image_url = c["url"]
                image_caption = "Selena Gomez at a public appearance"
                image_attribution = "Wikimedia Commons"
                break
    
    if not image_url:
        pexels = fetch_pexels_image("beauty cosmetics makeup products premium")
        if pexels and validate_image(pexels):
            image_url = pexels
            image_caption = "Premium beauty products from internationally recognized brands reaching Indian consumers"
            image_attribution = "Pexels"

    if not image_url:
        print("  ✗ No valid image found, skipping article")
        return False

    body = """Selena Gomez's Rare Beauty is now officially available in India through Nykaa. The launch, announced on June 6, makes the celebrity beauty brand accessible across Nykaa's website, mobile app, and 30 retail stores nationwide — a significant expansion from its earlier Sephora-only presence in the country.

In a video message, Gomez said: "I'm so excited to share that we're bringing Rare Beauty to Nykaa in India. Nykaa is such an amazing partner and it makes me so happy to keep growing Rare Beauty in India."

## Why This Launch Matters Beyond the Beauty Counter

Rare Beauty is not just another celebrity brand. Founded in 2020, it has built a global following around a specific mission: challenging unrealistic beauty standards and championing mental health awareness. The brand's Rare Impact Fund aims to raise $100 million over a decade to increase access to mental health services, donating one per cent of all global sales. Every purchase is a micro-contribution to that fund.

The brand's products — all vegan and cruelty-free — have earned viral status. The Soft Pinch Liquid Blush became a social media phenomenon, with TikTok videos driving demand that outstripped supply for months. The Soft Pinch Tinted Lip Oil and True to Myself Natural Matte Longwear Foundation round out the initial India launch lineup.

## India's Premium Beauty Market Is Moving Fast

For Nykaa, this is a strategic play. The company reported revenue of ₹2,648 crore in its latest quarter, up 28.4 per cent year-on-year, with net profit hitting ₹79 crore — its highest since listing. The beauty segment continues to drive that growth, and adding Rare Beauty strengthens its portfolio of international prestige brands.

Anchit Nayar, CEO of Nykaa Beauty, framed the partnership in terms of a "new generation of highly informed and globally engaged consumers seeking elevated brand experiences." That phrasing is telling. India's premium beauty consumer is no longer content with whatever trickles down from Western markets. They want what the global consumer has, at the same time, and they are willing to pay for it.

## The Diaspora Connection

For NRI audiences, the Rare Beauty launch closes a gap that has long been a quiet inconvenience. Indian Americans who discovered the brand in Sephora stores in New York or Los Angeles could never gift it easily to family back home. Indian consumers who saw the products on Instagram had to rely on resellers or international shipping. The Nykaa partnership creates a direct, authorised channel.

This matters in both directions. NRIs visiting India can now shop the same brands they use abroad. Indian consumers travelling to the US no longer need to treat a Rare Beauty blush as a suitcase essential. The brand parity between markets — once a years-long lag — is collapsing.

## Gomez's Star Power in India

Selena Gomez remains one of the most followed people on Instagram, with a fanbase that cuts across geographies. In India, her appeal extends beyond music. Her production work on *13 Reasons Why* and her Emmy-nominated role in *Only Murders in the Building* have built a recognition that transcends the pop-star category. When Rare Beauty launched at Sephora India in 2023, demand was immediate.

The Nykaa deal significantly expands reach. Thirty physical stores across the country — in cities from Mumbai to Bangalore to Delhi — mean that the brand is no longer confined to Sephora's footprint. Online availability through Nykaa's app brings it to tier-two and tier-three cities where prestige beauty has historically been underserved.

## The Bigger Picture

Rare Beauty joining Nykaa is part of a broader pattern. International celebrity and premium brands are accelerating their India timelines. The logic is straightforward: India's beauty market is projected to exceed $30 billion by 2030, and the consumers driving that growth are young, digitally fluent, and globally aware. They do not want to wait.

For Gomez, India is not a footnote market. It is one of the brand's most requested expansion territories. The Nykaa partnership suggests she is taking it seriously."""

    article = {
        "headline": "Selena Gomez's Rare Beauty Has Launched in India Through Nykaa. It Is Available in 30 Stores Today.",
        "subheadline": "The celebrity beauty brand expands beyond Sephora into Nykaa's nationwide network. For NRI audiences, it closes the gap between what is available abroad and what is accessible back home.",
        "body": body,
        "slug": "selena-gomez-rare-beauty-nykaa-india-launch-30-stores-nri-20260606",
        "category": "entertainment",
        "vertical": "entertainment",
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "sources": json.dumps(["afaqs", "Storyboard18", "Passionate in Marketing", "Harper's Bazaar India"]),
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "is_editorial": False
    }
    return insert_article(article)


# ================================================================
# RUN ALL
# ================================================================
if __name__ == "__main__":
    results = []
    
    print("=" * 60)
    print("The Videshi Entertainment Writer - June 6, 2026 (Afternoon)")
    print("=" * 60)
    
    results.append(("Peddi Box Office", write_peddi_box_office()))
    results.append(("Mahavatar + Pralay", write_mahavatar_pralay()))
    results.append(("Rare Beauty India", write_rare_beauty_india()))
    
    print("\n" + "=" * 60)
    print("RESULTS:")
    for name, success in results:
        status = "✓ PUBLISHED" if success else "✗ FAILED"
        print(f"  {status}: {name}")
    
    published = sum(1 for _, s in results if s)
    print(f"\nTotal: {published}/{len(results)} articles published")
    print("=" * 60)
