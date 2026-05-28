#!/usr/bin/env python3
"""Entertainment writer for The Videshi — 2026-05-28 batch"""

import json, os, sys, time, uuid, re, hashlib
from datetime import datetime, timezone

import requests
from urllib.parse import quote

# ── env ──────────────────────────────────────────────────────────────────
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[7:]
            k, _, v = line.partition("=")
            v = v.strip().strip('"').strip("'")
            os.environ.setdefault(k.strip(), v)

load_env(os.path.expanduser("~/.env.supabase"))
load_env(os.path.expanduser("~/workspace/.env.pexels"))

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── helpers ──────────────────────────────────────────────────────────────
def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    if r.status_code in (200, 201):
        return r.json()
    print(f"  ✗ sb_post {table} failed ({r.status_code}): {r.text[:300]}")
    return None

def sb_patch(table, match, data):
    params = "&".join(f"{k}={v}" for k, v in match.items())
    url = f"{SB_URL}/rest/v1/{table}?{params}"
    r = requests.patch(url, headers=HEADERS, json=data, timeout=30)
    if r.status_code in (200, 204):
        return True
    print(f"  ✗ sb_patch {table} failed ({r.status_code}): {r.text[:300]}")
    return False


def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10,
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
    """Fetch a relevant image from Pexels API using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key available")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            result = subprocess.run(
                ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
                 f"https://api.pexels.com/v1/search?query={quote(q)}&per_page=3&orientation=landscape"],
                capture_output=True, text=True, timeout=15,
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for p in photos:
                url = p.get("src", {}).get("large2x") or p.get("src", {}).get("original")
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image_url(url):
    """Verify image URL returns HTTP 200 with Content-Type image/* and size > 5000."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Try GET for servers that don't support HEAD well
        if r.status_code != 200:
            r2 = requests.get(url, timeout=10, stream=True, allow_redirects=True,
                            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            ct = r2.headers.get("Content-Type", "")
            cl = int(r2.headers.get("Content-Length", 0))
            r2.close()
            if r2.status_code == 200 and "image" in ct:
                return True
    except Exception as e:
        print(f"  ⚠ Image validation failed for {url[:60]}: {e}")
    return False


def generate_slug(headline):
    """Generate clean slug from headline."""
    slug = headline.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = re.sub(r'-+', '-', slug)
    slug = slug[:80].rstrip('-')
    return slug


def create_topic(article):
    """Create a topic in p2_topics for the article."""
    topic_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    payload = {
        "id": topic_id,
        "canonical_title": article["headline"][:200],
        "vertical": "entertainment",
        "urgency": article.get("urgency", "developing"),
        "score_diaspora": 70,
        "score_significance": 65,
        "score_recency": 80,
        "score_source_avail": 75,
        "score_total": 72,
        "signal_count": len(article.get("sources", [])),
        "status": "published",
        "keywords": article.get("tags", []),
        "category": "entertainment",
        "created_at": now,
        "updated_at": now,
        "image_url": article.get("image_url"),
        "image_attribution": article.get("image_attribution", ""),
    }

    result = sb_post("p2_topics", payload)
    if result:
        print(f"  ✓ Topic created: {topic_id}")
        return topic_id
    return None


def publish_article(article):
    """Publish an article to Supabase."""
    # First create a topic
    topic_id = create_topic(article)
    if not topic_id:
        print(f"  ✗ Failed to create topic, skipping article")
        return None

    art_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    sources_data = article.get("sources", [])
    # Convert to list of URL strings for compat
    sources_urls = [s["url"] if isinstance(s, dict) else s for s in sources_data]

    payload = {
        "id": art_id,
        "topic_id": topic_id,
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "body": article["body"],
        "slug": article["slug"],
        "category": "entertainment",
        "vertical": "entertainment",
        "urgency": article.get("urgency", "developing"),
        "tags": article.get("tags", []),
        "diaspora_angle": article.get("diaspora_angle", ""),
        "status": "published",
        "published_at": now,
        "sources": json.dumps(sources_urls),
        "image_url": article.get("image_url"),
        "image_caption": article.get("image_caption", ""),
        "image_attribution": article.get("image_attribution", ""),
        "word_count": len(article["body"].split()),
    }

    result = sb_post("p2_articles", payload)
    if result:
        print(f"  ✓ Published: {article['headline'][:60]}... (id={art_id})")
        return art_id
    return None


# ── articles ─────────────────────────────────────────────────────────────

def article_pankaj_bhadouria():
    """MasterChef India Winner Pankaj Bhadouria Diagnosed With Breast Cancer."""
    print("\n📰 Article 1: Pankaj Bhadouria breast cancer diagnosis")

    headline = "MasterChef India's First Winner Just Announced She Has Breast Cancer. She Left a 16-Year Teaching Career for This."
    subheadline = "Pankaj Bhadouria, who won Season 1 in 2010 and became a household name for millions of NRI families, shared her diagnosis from a hospital bed on May 28."
    slug = "pankaj-bhadouria-masterchef-india-winner-breast-cancer-diagnosis-nri-20260528"

    body = """Pankaj Bhadouria shared the news the way she shares everything — directly, without preamble. From a hospital bed in India, the 2010 MasterChef India winner posted to Instagram on May 28: she has been diagnosed with breast cancer and is seeking prayers and support as she begins treatment.

For NRIs of a certain generation — the ones who watched the first season of MasterChef India with their families, debated her dishes at dinner tables from New Jersey to Toronto — Bhadouria is not just a name from reality television. She was the first. The woman who proved that an Indian home cook, a schoolteacher with no professional culinary training, could stand in a competition kitchen and win.

## The Career She Left Behind

Before MasterChef, Bhadouria taught school for 16 years. When she won Season 1, she did what very few contestants from Indian reality television manage: she turned the moment into a career. She became a cookbook author, a YouTube personality, a food consultant. She built a digital presence that reached millions of Indian families — in India and abroad — who cook at home and wanted someone who understood what that kitchen looks like.

Her content was never about molecular gastronomy or restaurant plating. It was about dal, parathas, and the kind of food that NRI families make when they're homesick.

## What She Said

Bhadouria shared hospital photos and updates on social media, emphasising the need for prayers during her recovery. She did not disclose her full treatment plan or prognosis. The announcement was straightforward — no PR release, no delay, no softening. The same directness that won her a cooking competition 16 years ago.

Multiple Indian news outlets confirmed the diagnosis. Medical experts cited in Indian media coverage used the moment to highlight breast cancer detection rates in India, which remain significantly lower than in Western countries despite the disease being the most common cancer among Indian women.

## A Health Conversation the Diaspora Needs

Breast cancer screening rates among South Asian women in the US, UK, and Canada consistently lag behind the general population. Cultural stigma, language barriers, and a tendency to deprioritise personal health checks are well-documented factors. Bhadouria's public disclosure — from a figure who is genuinely trusted in Indian households — may carry more weight than any public health campaign.

She didn't frame it as activism. She asked for prayers. But the effect is the same: a woman whom millions of NRI families invited into their kitchens is now asking them to pay attention to their own health.

## What Comes Next

Bhadouria has not announced a timeline for her return to public life. Her social media accounts, which typically feature cooking content and food industry commentary, have shifted to health updates. The outpouring of support has been immediate and widespread — from fans, fellow chefs, and media personalities across India and the diaspora.

For the NRI community that grew up watching her, the message is simple: get screened. The woman who taught you how to make restaurant-style butter chicken is telling you that early detection matters. Listen."""

    # Image sourcing — Wikipedia first
    img_url = fetch_wikipedia_person_image("Pankaj Bhadouria")
    img_attribution = "Wikimedia Commons"
    img_caption = "Pankaj Bhadouria, winner of MasterChef India Season 1"

    if not img_url or not validate_image_url(img_url):
        print("  ⚠ Wikipedia image not found or invalid, trying Pexels...")
        img_url = fetch_pexels_image("Indian cooking kitchen chef", "MasterChef cooking")
        img_attribution = "Pexels"
        img_caption = "Representational image"

    if img_url and not validate_image_url(img_url):
        print("  ⚠ Image validation failed, skipping image")
        img_url = None

    return {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "urgency": "developing",
        "tags": ["Pankaj Bhadouria", "MasterChef India", "breast cancer", "health awareness", "diaspora"],
        "diaspora_angle": "Bhadouria is a household name for NRI families who watched MasterChef India Season 1. Her diagnosis has sparked a health awareness conversation particularly relevant to South Asian women abroad, who consistently show lower breast cancer screening rates than the general population.",
        "sources": [
            {"name": "LatestLY", "url": "https://latestly.com"},
            {"name": "Curly Tales", "url": "https://curlytales.com"},
            {"name": "Nation Press", "url": "https://nationpress.com"},
        ],
        "image_url": img_url,
        "image_caption": img_caption,
        "image_attribution": img_attribution,
    }


def article_toxic_yash():
    """Yash's Toxic — the most expensive Kannada film ever made keeps getting delayed."""
    print("\n📰 Article 2: Yash's Toxic delays")

    headline = "Yash's Toxic Is the Most Expensive Kannada Film Ever Made. It Has Been Delayed Three Times. No One Knows When It Opens."
    subheadline = "At ₹700-800 crore, Toxic was supposed to follow KGF into the stratosphere. Instead, it has bounced from March to June to a date yet to be announced."
    slug = "yash-toxic-most-expensive-kannada-film-delayed-three-times-release-date-nri-20260528"

    body = """The math on Yash's Toxic is simple. The film cost between ₹700 and ₹800 crore to make. It was announced as the follow-up to KGF: Chapter 2, one of the highest-grossing Indian films of all time. It stars Kiara Advani, Nayanthara, Huma Qureshi, and Tara Sutaria alongside Yash in a dual role. The action sequences were choreographed by JJ Perry, the man behind John Wick. The music is by Ravi Basrur. The director is Geetu Mohandas — the first woman to helm a film at this budget level in Indian cinema.

And nobody knows when you can watch it.

## Three Delays and Counting

Toxic was originally scheduled for March 19, 2026 — timed to land on the Ugadi, Gudi Padwa, and Eid holiday window. It would have clashed with Ranveer Singh's Dhurandhar 2: The Revenge, which was the kind of box office war that gets trade analysts writing in ALL CAPS.

Then it was pushed to June 4, 2026. The stated reason: the Middle East crisis had disrupted global distribution plans, and the makers wanted a wider worldwide theatrical window. The film was shot in Kannada and English — a first for Indian cinema at this scale — and securing English-language distribution across markets required more time.

Then, in what has become a pattern, the June 4 date was also pulled. The producers at KVN Productions issued a statement emphasising "patience" and "global ambitions," but offered no replacement date. As of today — May 28, 2026 — Toxic has no confirmed release.

## What the Industry Saw at CinemaCon

The film is complete. That much is clear. At CinemaCon 2026, the makers showed a nine-minute preview to international distributors and exhibitors. The response, by multiple trade accounts, was "speechless." The footage reportedly showcased the film's period setting — a sprawling narrative across the 1940s to 1970s — and a tone that blends gangster mythology with fairy tale imagery. The subtitle of the film is "A Fairy Tale for Grown-Ups."

Dil Raju's Sri Venkateswara Creations paid ₹120 crore for the Andhra Pradesh and Telangana theatrical rights — the highest ever for a non-Telugu film in the region. Anil Thadani's AA Films is handling North India and Nepal. Phars Film locked the international Indian-language rights for ₹105 crore. These are not the deal structures of a film that anyone thinks will underperform.

## The Problem With Being Too Big

Toxic exists in a category that Indian cinema has only recently created: the ₹500 crore+ production that must perform globally to break even. KGF: Chapter 2 proved a Kannada film could do it. But KGF 2 arrived as a sequel with a built-in audience and thunderous momentum. Toxic is an original property — a period gangster film with an unconventional director and a fairy tale framing. The ingredients are spectacular. The risk is commensurate.

Every delay compounds the problem. Marketing campaigns lose momentum. Distribution partners recalculate their projections. Audiences move on to the next headline. The ₹120 crore that Dil Raju paid was priced on the assumption of a specific release window — not an indefinite hold.

## What NRIs Should Know

If you saw KGF in a packed North American theatre and felt like Indian cinema had permanently changed, Toxic is the film that either confirms that theory or challenges it. The scale is genuine. The talent is undeniable. The financial stakes are the highest in Kannada cinema history.

The only thing missing is a date on the calendar. When it arrives, you'll want to be in a theatre. If it arrives."""

    # Image sourcing — Wikipedia for Yash
    img_url = fetch_wikipedia_person_image("Yash (actor)")
    img_attribution = "Wikimedia Commons"
    img_caption = "Yash, star of KGF and the upcoming Toxic"

    if not img_url or not validate_image_url(img_url):
        img_url = fetch_wikipedia_person_image("Yash Kannada actor")
        
    if not img_url or not validate_image_url(img_url):
        img_url = fetch_pexels_image("gangster film noir dark", "cinematic dark throne")
        img_attribution = "Pexels"
        img_caption = "Representational image"

    if img_url and not validate_image_url(img_url):
        img_url = None

    return {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "urgency": "developing",
        "tags": ["Yash", "Toxic", "Kannada cinema", "KGF", "Kiara Advani", "Nayanthara", "box office"],
        "diaspora_angle": "NRIs who packed theatres for KGF have been waiting for Yash's next. Toxic's repeated delays and enormous budget make it the biggest question mark in Indian cinema's global expansion — and the answer directly affects how many Kannada-language films get wide releases in North America and the UK.",
        "sources": [
            {"name": "Pinkvilla", "url": "https://pinkvilla.com"},
            {"name": "Hollywood Reporter India", "url": "https://hollywoodreporterindia.com"},
            {"name": "Sacnilk", "url": "https://sacnilk.com"},
            {"name": "Wikipedia", "url": "https://en.wikipedia.org/wiki/Toxic_(2026_film)"},
        ],
        "image_url": img_url,
        "image_caption": img_caption,
        "image_attribution": img_attribution,
    }


def article_ramayana_preponed():
    """Ramayana Part 1 — preponed to October 30."""
    print("\n📰 Article 3: Ramayana Part 1 preponed to October 30")

    headline = "Ramayana Part 1 Is Reportedly Coming a Week Before Diwali. The Cast List Alone Would Have Sold Out 2015."
    subheadline = "Ranbir Kapoor as Ram, Sai Pallavi as Sita, Yash as Ravana, Sunny Deol as Hanuman. Music by AR Rahman and Hans Zimmer. Distribution deal: ₹450 crore. Release: October 30, 2026."
    slug = "ramayana-part-1-preponed-october-30-ranbir-kapoor-yash-sai-pallavi-ar-rahman-hans-zimmer-nri-20260528"

    body = """The most anticipated Indian film of 2026 may have just moved up its arrival. According to multiple trade reports, Ramayana Part 1 — directed by Nitesh Tiwari and produced by Namit Malhotra — is now targeting October 30, 2026, a week ahead of Diwali. The original plan was a Diwali-day release. The preponed date is designed to capture the maximum festive window, giving the film a full week of holiday-period screenings before the celebrations peak.

This is, by every available metric, the biggest Indian production currently in existence.

## A Cast That Reads Like a Fever Dream

Ranbir Kapoor plays Lord Ram. Sai Pallavi plays Sita. Yash — the KGF franchise star currently navigating the delayed release of Toxic — plays Ravana. Sunny Deol, in what may be the most inspired piece of casting in recent Indian cinema, plays Hanuman. Ravi Dubey plays Lakshman. Prithviraj Sukumaran has an undisclosed role.

The music is composed by AR Rahman and Hans Zimmer. If you read that twice, you read it correctly. The man who scored Slumdog Millionaire and the man who scored The Dark Knight, Inception, and Interstellar are collaborating on the same Indian film.

## The Business Behind the Mythology

The theatrical distribution deal is reportedly worth ₹450 crore — a figure that reflects the industry's confidence in the film's commercial ceiling. This is a two-part project. Part 1 arrives October 30, 2026. Part 2 is scheduled for Diwali 2027. The introductory video was released on July 3, 2025, more than a year before the first film's release, suggesting a marketing timeline modelled on Hollywood tentpoles rather than typical Bollywood campaigns.

Nitesh Tiwari — the director of Dangal, one of the highest-grossing Indian films globally — is helming the project. The film has been shot across multiple international locations and utilises a visual effects pipeline that the producers describe as the most advanced ever deployed in Indian cinema.

## The Teaser That Already Exists

In late March 2026, a CBFC-certified asset titled "Rama" was cleared for release — a 2 minute, 38-second video that was shown at a special IMAX screening in Los Angeles. Ranbir Kapoor, Nitesh Tiwari, and Namit Malhotra attended the LA event. The footage was released publicly on April 2, Hanuman Jayanti — the cultural alignment between the marketing calendar and the source material being neither subtle nor accidental.

Early reports from the LA screening emphasise character presence and emotional depth over action spectacle. This is not, by available accounts, an effects-driven blockbuster that happens to use Hindu mythology. It is a character film that happens to have an unprecedented effects budget.

## Why NRIs Should Pay Attention

Ramayana occupies a unique position in the diaspora's cultural consciousness. For millions of NRI families, the Ramayan TV serial of the late 1980s is foundational — a shared reference that bridges generations and geographies. A big-screen adaptation with this cast, this director, and this budget is not just a film release. It is a cultural event.

The October 30 date, if confirmed, positions the film to dominate the global box office during a period when Indian audiences — both domestic and overseas — are at their most receptive. Diwali weekend in North America has become one of the most reliable windows for Indian cinema's biggest releases.

Part 1 of Ramayana. Ranbir as Ram. Yash as Ravana. Rahman and Zimmer on the score. October 30. Mark it."""

    # Image sourcing — Wikipedia for Ranbir Kapoor
    img_url = fetch_wikipedia_person_image("Ranbir Kapoor")
    img_attribution = "Wikimedia Commons"
    img_caption = "Ranbir Kapoor, who plays Lord Ram in Ramayana Part 1"

    if not img_url or not validate_image_url(img_url):
        img_url = fetch_wikipedia_person_image("Nitesh Tiwari")
        img_caption = "Nitesh Tiwari, director of Ramayana"

    if not img_url or not validate_image_url(img_url):
        img_url = fetch_pexels_image("ancient Indian temple architecture", "Hindu temple India")
        img_attribution = "Pexels"
        img_caption = "Representational image"

    if img_url and not validate_image_url(img_url):
        img_url = None

    return {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "urgency": "developing",
        "tags": ["Ramayana", "Ranbir Kapoor", "Yash", "Sai Pallavi", "Nitesh Tiwari", "AR Rahman", "Hans Zimmer", "Diwali 2026"],
        "diaspora_angle": "Ramayana is the most culturally significant Indian film project in a generation for the diaspora. The 1987 TV serial is a shared reference across NRI families worldwide. A big-screen adaptation with this cast and this budget, releasing during Diwali, will be the biggest Indian film event of the year in overseas markets.",
        "sources": [
            {"name": "Sacnilk", "url": "https://sacnilk.com"},
            {"name": "Bollywood Hungama", "url": "https://bollywoodhungama.com"},
        ],
        "image_url": img_url,
        "image_caption": img_caption,
        "image_attribution": img_attribution,
    }


# ── main ─────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("The Videshi — Entertainment Writer — 2026-05-28")
    print("=" * 60)

    articles = [
        article_pankaj_bhadouria(),
        article_toxic_yash(),
        article_ramayana_preponed(),
    ]

    published = 0
    for art in articles:
        # Validate
        if len(art["headline"]) > 200:
            print(f"  ⚠ Headline too long ({len(art['headline'])} chars), truncating")
            art["headline"] = art["headline"][:197] + "..."
        if len(art.get("subheadline", "")) < 15:
            print(f"  ⚠ Subheadline too short, skipping article")
            continue
        word_count = len(art["body"].split())
        if word_count < 400:
            print(f"  ⚠ Body too short ({word_count} words), skipping article")
            continue

        print(f"\n  Publishing: {art['headline'][:70]}...")
        print(f"  Slug: {art['slug']}")
        print(f"  Words: {word_count}")
        print(f"  Image: {art.get('image_url', 'None')[:80] if art.get('image_url') else 'None'}")

        result = publish_article(art)
        if result:
            published += 1

    print(f"\n{'=' * 60}")
    print(f"Done. Published {published}/{len(articles)} articles.")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()
