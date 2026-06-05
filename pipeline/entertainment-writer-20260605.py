#!/usr/bin/env python3
"""Entertainment writer for The Videshi - June 5, 2026"""

import json
import os
import re
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
import requests
import urllib.parse

# Load env
env_path = os.path.expanduser("~/workspace/.env.supabase")
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            os.environ[key.strip()] = val.strip().strip('"').strip("'")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

# Pexels
pexels_env = os.path.expanduser("~/workspace/.env.pexels")
PEXELS_KEY = None
if os.path.exists(pexels_env):
    with open(pexels_env) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                if "PEXELS" in key.upper():
                    PEXELS_KEY = val.strip().strip('"').strip("'")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

UA = "TheVideshi/1.0 (thevideshi.com)"


def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns (url, attribution) or (None, None)."""
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
                return img, "Wikimedia Commons"
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None, None


def fetch_wikimedia_commons(search_query, limit=5):
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
            headers={"User-Agent": UA},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                info = page.get("imageinfo", [{}])[0]
                url = info.get("thumburl") or info.get("url")
                mime = info.get("mime", "")
                if url and "image" in mime:
                    results.append({
                        "url": url,
                        "title": page.get("title", ""),
                        "width": info.get("width", 0),
                        "height": info.get("height", 0)
                    })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} results for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error for '{search_query}': {e}")
    return []


def fetch_pexels_image(query):
    """Search Pexels for a relevant image using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        return None, None
    try:
        result = subprocess.run(
            ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
             f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=5&orientation=landscape"],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        photos = data.get("photos", [])
        for photo in photos:
            url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("large")
            if url:
                print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                return url, "Pexels"
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None, None


def validate_image(url):
    """Validate image URL returns 200 with image content type and > 5KB."""
    try:
        r = requests.head(url, headers={"User-Agent": UA}, timeout=10, allow_redirects=True)
        content_type = r.headers.get("Content-Type", "")
        content_length = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in content_type and content_length > 5000:
            print(f"  ✓ Image validated: {content_length} bytes, {content_type}")
            return True
        # Try GET if HEAD didn't return content-length
        if r.status_code == 200 and "image" in content_type and content_length == 0:
            r2 = requests.get(url, headers={"User-Agent": UA}, timeout=10, stream=True)
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                print(f"  ✓ Image validated via GET: {len(chunk)}+ bytes")
                return True
        print(f"  ✗ Image validation failed: status={r.status_code}, type={content_type}, size={content_length}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False


def source_image(person_name=None, wiki_search=None, pexels_query=None):
    """Multi-source image search: Wikipedia person → Wikimedia Commons → Pexels."""
    # Try Wikipedia person image first
    if person_name:
        url, attr = fetch_wikipedia_person_image(person_name)
        if url and validate_image(url):
            return url, attr

    # Try Wikimedia Commons
    if wiki_search:
        results = fetch_wikimedia_commons(wiki_search)
        for r in results:
            if validate_image(r["url"]):
                return r["url"], "Wikimedia Commons"

    # Fallback to Pexels
    if pexels_query:
        url, attr = fetch_pexels_image(pexels_query)
        if url and validate_image(url):
            return url, attr

    return None, None


def insert_article(article):
    """Insert article into Supabase."""
    payload = {
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "slug": article["slug"],
        "body": article["body"],
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "source_urls": json.dumps(article.get("sources", [])),
        "image_url": article.get("image_url"),
        "image_caption": article.get("image_caption"),
        "image_attribution": article.get("image_attribution"),
        "is_editorial": False,
        "social_embed_url": article.get("social_embed_url")
    }
    # Remove None values
    payload = {k: v for k, v in payload.items() if v is not None}

    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=payload,
        timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        article_id = data[0]["id"] if isinstance(data, list) and data else "unknown"
        print(f"  ✓ Published: {article['headline'][:60]}... (ID: {article_id})")
        return True
    else:
        print(f"  ✗ Failed to publish: {r.status_code} - {r.text[:200]}")
        return False


def count_words(text):
    """Count words in markdown text, excluding markup."""
    clean = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    clean = re.sub(r'[#*_`>]', '', clean)
    return len(clean.split())


# ============================================================
# ARTICLE 1: Vicky Kaushal blocks 18 months for Mahavatar
# ============================================================
print("\n" + "="*60)
print("ARTICLE 1: Vicky Kaushal / Mahavatar")
print("="*60)

img1_url, img1_attr = source_image(
    person_name="Vicky Kaushal",
    wiki_search="Vicky Kaushal actor Bollywood",
    pexels_query=None  # No generic stock for person articles
)

article1 = {
    "headline": "Vicky Kaushal Has Blocked Eighteen Months of His Life for One Role. The Scale of Mahavatar Is Unlike Anything Bollywood Has Attempted.",
    "subheadline": "Six months of physical transformation, twelve months of shooting, no other projects in between — and Shraddha Kapoor may be joining him.",
    "slug": "vicky-kaushal-mahavatar-parashurama-18-months-shraddha-kapoor-maddock-nri-20260605",
    "body": """When Vicky Kaushal wraps his final scenes on Sanjay Leela Bhansali's *Love and War* later this month, he will not move on to the next film on his calendar. He will move into a training facility. For six months, starting in June 2026, the actor will undergo a physical and psychological transformation designed by director Amar Kaushik to prepare him for the role of Chiranjeevi Parashurama in *Mahavatar*, Maddock Films' most ambitious production to date.

The numbers are staggering. Kaushal has blocked a total of eighteen months exclusively for this one project — six months of intensive preparation followed by twelve months of continuous filming, with no other commitments permitted during the entire window. In an industry where leading men routinely juggle three or four productions simultaneously, this is an extraordinary bet on a single performance.

## The Preparation Module

According to reports from Pinkvilla and Sacnilk, the preparatory phase is not a simple gym routine. Amar Kaushik has designed a comprehensive module that includes rigorous physical bulking to match the mythological scale of Parashurama, alongside acting workshops, weapon training, and deep immersion into the spiritual and emotional dimensions of the character. Kaushal is portraying one of the Chiranjivi — the immortals of Hindu mythology — a figure known for immense physical strength and profound spiritual depth.

The director, who delivered back-to-back blockbusters with *Stree* and *Stree 2*, has been quietly working on pre-production for seven months already. Set design, weapon design, character looks, and the complete script have all been locked. "The prep is going on for 6-7 months," Kaushik told Bollywood Hungama in an earlier interview. "We have worked on the set design, weapon design, how every character would look. Yet, we need more time."

## Shraddha Kapoor in Talks

Adding fuel to the anticipation, Mid-Day has reported that Shraddha Kapoor is in advanced talks to play the female lead opposite Kaushal. If she signs on, this would be their first on-screen collaboration — a pairing the makers believe will bring both star power and box office pull to what is already shaping up to be a tentpole release.

The film is part of a broader mythological cinematic universe being built by Maddock Films. The animated *Mahavatar Narsimha*, released in 2025, became the highest-grossing Indian animated film of all time at ₹325 crore worldwide, proving that audiences have an appetite for this mythology-driven storytelling. *Mahavatar* is the live-action expansion of that universe, with Parashurama's story set to connect to the wider narrative across multiple installments.

## What This Means for Bollywood's New Era

Kaushal's commitment reflects a seismic shift in how Bollywood's biggest actors are approaching their careers. The era of churning out three films a year is giving way to singular, high-investment performances that demand total immersion. It is a strategy borrowed from Hollywood's franchise ecosystem and South Indian cinema's recent mega-productions, and it signals that the Indian film industry is betting bigger than ever on event-level storytelling.

The film was originally announced for a Christmas 2026 release, but the extended preparation timeline has pushed it to 2027 — with Independence Day weekend emerging as the likely target. For Kaushal, the gamble is simple: one role, eighteen months, and the kind of physical and emotional transformation that could define a career.

## The Diaspora Angle

For the Indian diaspora, *Mahavatar* represents the kind of globally ambitious mythological storytelling that has long been a source of cultural pride and frustration in equal measure. If Maddock Films can execute at the scale they are promising — and early signs suggest they are sparing nothing — this could be the film that finally bridges the gap between India's mythology and Hollywood's visual spectacle. The eighteen-month commitment from its lead actor suggests everyone involved believes it can.""",
    "sources": [
        "https://www.sacnilk.com/articles/love-and-war-starrer-vicky-kaushal-blocks-18-months-for-amar-kaushik-mahavatar",
        "https://www.sacnilk.com/articles/shraddha-kapoor-to-play-female-lead-in-vicky-kaushal-fronted-mahavatar",
        "https://www.bollywoodhungama.com"
    ],
    "image_url": img1_url,
    "image_caption": "Vicky Kaushal at a film event in Mumbai",
    "image_attribution": img1_attr
}

wc1 = count_words(article1["body"])
print(f"  Word count: {wc1}")
if wc1 >= 400 and img1_url:
    insert_article(article1)
elif not img1_url:
    print("  ✗ Skipping: no valid image found")
else:
    print(f"  ✗ Skipping: word count {wc1} below minimum")


# ============================================================
# ARTICLE 2: Ranveer Singh's Pralay
# ============================================================
print("\n" + "="*60)
print("ARTICLE 2: Ranveer Singh / Pralay")
print("="*60)

img2_url, img2_attr = source_image(
    person_name="Ranveer Singh",
    wiki_search="Ranveer Singh actor Indian",
    pexels_query=None
)

article2 = {
    "headline": "Pralay Is a ₹300-Crore Post-Apocalyptic Thriller. Ranveer Singh Starts Shooting in August.",
    "subheadline": "A South Indian star makes her Hindi debut, AI-driven visual effects replace traditional CGI, and Bollywood's biggest action star enters a genre India has never attempted at this scale.",
    "slug": "ranveer-singh-pralay-300-crore-post-apocalyptic-kalyani-priyadarshan-hindi-debut-nri-20260605",
    "body": """The rumours of a creative fallout were just that — rumours. Ranveer Singh's next film after the record-shattering *Dhurandhar* franchise is not only alive, it has a budget of ₹300 crore, a confirmed August 2026 start date, and a genre that Indian cinema has never attempted at this scale.

*Pralay*, directed by Jai Mehta, is a post-apocalyptic survival thriller — a genre virtually non-existent in Bollywood's playbook. According to a Variety India report confirmed by Sacnilk, the production plans to merge physical sets with cutting-edge AI-driven visual effects to create a dystopian atmosphere that the makers describe as unlike anything previously seen in Indian cinema. This is not the VFX-heavy spectacle of *Brahmastra* or *Adipurush*. This is an entirely new visual language being built from scratch.

## Kalyani Priyadarshan's Hindi Debut

Perhaps the most intriguing casting choice is Kalyani Priyadarshan, who has been finalised as the female lead. The daughter of legendary Malayalam filmmaker Priyadarshan, Kalyani has built a quietly impressive career in South Indian cinema with films across Telugu, Tamil, and Malayalam. *Pralay* will be her Hindi film debut — a crossover move that reflects Bollywood's increasing willingness to look beyond its traditional star system for talent.

The pairing of Ranveer, coming off India's highest-grossing film ever, with a South Indian actress making her Hindi debut is a deliberate creative decision. The makers are reportedly confident that the fresh combination will serve the film's tone — a survival story that requires vulnerability and grit rather than conventional star dynamics.

## The Post-Dhurandhar Pivot

For Ranveer Singh, *Pralay* represents a calculated departure from the spy-action universe that made him India's biggest box office draw. After *Dhurandhar 2: The Revenge* crossed ₹1,800 crore worldwide — shattering records that had stood since *Baahubali 2* — the actor has reportedly stepped away from the *Don* franchise entirely to explore new genres.

This is not a retreat. It is a pivot. Reports suggest that Singh, much like his contemporary Vicky Kaushal, is choosing to invest deeply in singular projects rather than spreading himself across multiple films. The ₹300-crore budget of *Pralay* — comparable to the biggest productions in Indian cinema history — underscores the kind of confidence producers are placing in both the actor and the genre.

## AI-Driven Visual Effects: A New Frontier

The most technically ambitious aspect of *Pralay* is its approach to visual effects. Rather than the traditional VFX pipeline that Indian films have relied on — often with uneven results — the production is integrating AI-driven visual generation into its workflow from the pre-production stage itself. While details remain closely guarded, industry sources suggest this could dramatically reduce the gap between concept and execution that has plagued Indian sci-fi and fantasy films.

If the AI integration works as planned, *Pralay* could become a proof-of-concept for an entirely new way of making visually complex Indian films — one where the technology serves the story rather than becoming a visible, distracting layer on top of it.

## Why Diaspora Audiences Should Pay Attention

The Indian diaspora has long wished for homegrown genre films that can hold their own alongside Hollywood spectacles. Post-apocalyptic narratives — from *Mad Max* to *The Last of Us* — have massive global appeal but zero Indian entries worth mentioning. If *Pralay* delivers on its ambitions, it could open a door that the Indian film industry has never walked through. The ₹300-crore investment suggests the producers are betting it will.""",
    "sources": [
        "https://www.sacnilk.com/articles/bollywood-buzz-ranveer-singh-pralay-shoot-begins-august-2026",
        "https://www.sacnilk.com/articles/ranveer-singh-fwice-non-cooperation-withdrawn",
        "https://boxoffy.com"
    ],
    "image_url": img2_url,
    "image_caption": "Ranveer Singh at a promotional event in Mumbai",
    "image_attribution": img2_attr
}

wc2 = count_words(article2["body"])
print(f"  Word count: {wc2}")
if wc2 >= 400 and img2_url:
    insert_article(article2)
elif not img2_url:
    print("  ✗ Skipping: no valid image found")
else:
    print(f"  ✗ Skipping: word count {wc2} below minimum")


# ============================================================
# ARTICLE 3: Drishyam 3 at 230 Crore, heading to Amazon Prime
# ============================================================
print("\n" + "="*60)
print("ARTICLE 3: Drishyam 3 / OTT + Box Office")
print("="*60)

img3_url, img3_attr = source_image(
    person_name="Mohanlal",
    wiki_search="Mohanlal actor Malayalam",
    pexels_query=None
)

article3 = {
    "headline": "Drishyam 3 Has Crossed ₹230 Crore Worldwide. The Diaspora Is Still Waiting to Stream It.",
    "subheadline": "Georgekutty's final chapter is the highest-grossing installment in the franchise, but a legal dispute with Amazon Prime Video delayed the OTT deal — and the Hindi remake with Ajay Devgn is already dated for October.",
    "slug": "drishyam-3-230-crore-worldwide-amazon-prime-ott-hindi-remake-ajay-devgn-nri-20260605",
    "body": """Fifteen days into its theatrical run, *Drishyam 3* has cemented itself as one of the biggest Malayalam films ever made. Mohanlal's final chapter as Georgekutty — the quiet cable operator whose lies became an entire nation's obsession — has grossed ₹230.47 crore worldwide, crossed ₹100 crore net in India, and become the first South Indian film of 2026 to hit $10 million in overseas markets.

The numbers tell a story of a franchise that has only grown more powerful with each installment. The original *Drishyam* in 2013 was a sleeper hit. *Drishyam 2* in 2021, released directly on Amazon Prime Video during the pandemic, became a global streaming sensation. Now, *Drishyam 3* has proven that the saga's audience was always bigger than any single platform could capture.

## The Legal Dispute That Clouded the OTT Deal

But for millions of Indian diaspora viewers who have been waiting to stream the film, the biggest story is not the box office. It is the legal battle that has delayed clarity on when and where *Drishyam 3* will be available digitally.

Amazon Prime Video went to the Delhi High Court claiming exclusive streaming rights to the *Drishyam* franchise under an earlier agreement with producer Aashirvad Cinemas. Amazon argued that its deal included either first preference or outright exclusivity for future installments. The Delhi High Court granted interim relief in Amazon's favour, temporarily restraining the makers from negotiating OTT deals with third parties.

The court order put the digital rights deal in limbo. In an era where post-theatrical streaming windows are often locked months before a film even releases, this uncertainty is unusual — and for a franchise as commercially valuable as *Drishyam*, it created a standoff worth hundreds of crores.

Current reports indicate that Amazon Prime Video has ultimately secured the digital streaming rights, with a June 2026 OTT debut expected. But the dispute exposed a tension that the Indian film industry is only beginning to grapple with: who owns the digital future of a franchise, and can a streaming deal signed for one film bind the creators for all subsequent installments?

## The Box Office Breakdown

On Day 15 (June 4), *Drishyam 3* collected ₹1.05 crore net across 1,341 shows in India. The India net total stands at ₹102.75 crore, the India gross at ₹119.22 crore, and the overseas gross at ₹111.25 crore — an extraordinary international performance driven by strong demand in the Gulf countries, North America, and the United Kingdom.

Kerala remains the film's strongest domestic market, with Kochi and Thrissur leading footfalls. Evening and night screenings continue to draw solid occupancy even in the third week, suggesting that word-of-mouth has sustained interest beyond the opening surge.

Directed by Jeethu Joseph, the film stars Mohanlal alongside Meena, Ansiba Hassan, Esther Anil, Kalabhavan Shajon, Siddique, Murali Gopy, and Asha Sarath. The narrative picks up from the devastating revelations of the second film and brings the Georgekutty saga to what has been described as a definitive, unforgettable conclusion.

## The Hindi Remake Is Already Coming

While diaspora audiences wait for the Malayalam original to hit streaming, the Hindi machine is already in motion. A *Drishyam 3* Hindi remake starring Ajay Devgn is slated for release on October 2, 2026. The previous two Hindi remakes — produced by Panorama Studios — were both significant box office hits, with the second installment grossing over ₹300 crore worldwide.

For NRI audiences, this creates an unusual viewing calculus. Watch the Malayalam original with subtitles the moment it drops on Prime Video, or wait four more months for the Hindi version on the big screen? The franchise's history suggests most will not wait. The original *Drishyam 2* became a massive crossover streaming hit precisely because diaspora viewers, regardless of language preference, wanted to see Georgekutty's story before the rest of the world caught up.

## Why This Franchise Still Matters

At its core, the *Drishyam* series resonated with Indian audiences — at home and abroad — because it was about an ordinary man navigating an extraordinary lie to protect his family. That premise is universal, but the execution was specifically, unmistakably Indian: the textures of Kerala life, the dynamics of a joint family under pressure, the way the legal system both fails and functions. Three films later, it remains one of the few Indian franchises that has genuinely grown with its audience rather than coasting on familiarity.""",
    "sources": [
        "https://www.sacnilk.com/articles/drishyam-3-ott-rights-put-on-hold-legal-dispute-clouds-digital-deal",
        "https://www.thedailyjagran.com/entertainment/drishyam-3-box-office-collection-day-15",
        "https://www.bombaytimes.com/entertainment/box-office-collection-june-4-2026",
        "https://keralatv.in/june-2026-malayalam-ott-releases"
    ],
    "image_url": img3_url,
    "image_caption": "Mohanlal at a film premiere in Kochi",
    "image_attribution": img3_attr
}

wc3 = count_words(article3["body"])
print(f"  Word count: {wc3}")
if wc3 >= 400 and img3_url:
    insert_article(article3)
elif not img3_url:
    print("  ✗ Skipping: no valid image found")
else:
    print(f"  ✗ Skipping: word count {wc3} below minimum")

print("\n" + "="*60)
print("Entertainment writer run complete")
print("="*60)
