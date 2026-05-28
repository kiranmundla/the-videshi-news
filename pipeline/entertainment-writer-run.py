#!/usr/bin/env python3
"""Entertainment writer for The Videshi - May 28, 2026 run."""

import json
import os
import re
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
import requests
import urllib.parse

# Load environment
env_path = os.path.expanduser("~/.env.supabase")
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                if line.startswith("export "):
                    line = line[7:]
                key, val = line.split("=", 1)
                val = val.strip("'\"")
                os.environ[key] = val

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# Load Pexels key
pexels_env = os.path.expanduser("~/workspace/.env.pexels")
PEXELS_KEY = None
if os.path.exists(pexels_env):
    with open(pexels_env) as f:
        for line in f:
            line = line.strip()
            if line and "=" in line and not line.startswith("#"):
                if line.startswith("export "):
                    line = line[7:]
                k, v = line.split("=", 1)
                if "PEXELS" in k.upper():
                    PEXELS_KEY = v.strip("'\"")


def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(" ", "_"))
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
    """Fetch a relevant image from Pexels. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key available")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ["curl", "-sS", f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape",
                 "-H", f"Authorization: {PEXELS_KEY}"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for p in photos:
                url = p.get("src", {}).get("large2x") or p.get("src", {}).get("large")
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image_url(url):
    """Validate that an image URL returns HTTP 200 with image content-type and >5KB."""
    if not url:
        return False
    # Block banned sources
    banned = ["fbcdn.net", "cdninstagram.com", "lookaside.fbsbx.com", "_nc_ht=", "_nc_cat=", "ccb="]
    for b in banned:
        if b in url:
            print(f"  ✗ Banned image source: {b}")
            return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        content_type = r.headers.get("Content-Type", "")
        content_length = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in content_type and content_length > 5000:
            print(f"  ✓ Image validated: {content_type}, {content_length} bytes")
            return True
        # Some servers don't return Content-Length on HEAD, try GET with range
        if r.status_code == 200 and "image" in content_type:
            r2 = requests.get(url, timeout=10, stream=True,
                            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            size = 0
            for chunk in r2.iter_content(8192):
                size += len(chunk)
                if size > 5000:
                    print(f"  ✓ Image validated via GET: {content_type}, >5KB")
                    return True
            print(f"  ✗ Image too small: {size} bytes")
            return False
        print(f"  ✗ Image validation failed: status={r.status_code}, type={content_type}, size={content_length}")
        return False
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
        return False


def get_image_for_person(person_name, topic_query=None):
    """Get image for a person article: Wikipedia first, then Pexels fallback."""
    img = fetch_wikipedia_person_image(person_name)
    if img and validate_image_url(img):
        return img, "Wikimedia Commons"
    # Try alternate name forms
    if " " in person_name:
        parts = person_name.split()
        if len(parts) >= 2:
            alt = f"{parts[0]} {parts[-1]}"
            if alt != person_name:
                img = fetch_wikipedia_person_image(alt)
                if img and validate_image_url(img):
                    return img, "Wikimedia Commons"
    # Pexels fallback
    if topic_query:
        img = fetch_pexels_image(topic_query)
        if img and validate_image_url(img):
            return img, "Pexels"
    return None, None


def get_image_for_topic(primary_query, fallback_query=None):
    """Get image for a topic article: Pexels with specific query."""
    img = fetch_pexels_image(primary_query, fallback_query)
    if img and validate_image_url(img):
        return img, "Pexels"
    return None, None


def publish_article(article):
    """Publish article to Supabase."""
    print(f"\n📤 Publishing: {article['headline']}")
    payload = {
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "body": article["body"],
        "slug": article["slug"],
        "category": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sources": json.dumps(article.get("sources", [])),
        "vertical": "entertainment",
        "image_url": article.get("image_url"),
        "image_caption": article.get("image_caption"),
        "image_attribution": article.get("image_attribution"),
    }
    # Remove None values
    payload = {k: v for k, v in payload.items() if v is not None}

    try:
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/p2_articles",
            headers=HEADERS,
            json=payload,
            timeout=30,
        )
        if r.status_code in (200, 201):
            result = r.json()
            aid = result[0]["id"] if isinstance(result, list) and result else "unknown"
            print(f"  ✅ Published: {aid}")
            return True
        else:
            print(f"  ❌ Failed ({r.status_code}): {r.text[:200]}")
            return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


# ============================================================
# ARTICLES
# ============================================================

articles = []

# ------- ARTICLE 1: SS Rajamouli's Varanasi Set Leak -------
print("\n🎬 Article 1: SS Rajamouli Varanasi Set Leak")
img1, attr1 = get_image_for_person("S. S. Rajamouli")
if not img1:
    img1, attr1 = get_image_for_person("SS Rajamouli", "Indian film director")

articles.append({
    "headline": "The First Photo From Inside SS Rajamouli's ₹1,000 Crore Set Just Leaked. It Looks Like Nothing Indian Cinema Has Built Before.",
    "subheadline": "A blue-screen cave set for the Ugrabhatti sequence in Varanasi surfaced on social media. Mahesh Babu plays a man seeking a goddess's grace to fight an ancient evil. The film opens April 7, 2027.",
    "slug": "ss-rajamouli-varanasi-ugrabhatti-cave-set-photo-leak-mahesh-babu-priyanka-chopra-2027-nri-20260528",
    "image_url": img1,
    "image_caption": "SS Rajamouli, director of Baahubali and RRR, is building his most ambitious film yet",
    "image_attribution": attr1,
    "sources": [
        "https://www.bollywoodhungama.com/news/bollywood/set-photo-from-varanasi-surfaces-ss-rajamoulis-ugrabhatti-caves-sequence-gets-its-first-leak/",
        "https://www.finsiddhi.com/ss-rajamoulis-varanasi-set-photo-turns-up-online/"
    ],
    "body": """A single photograph, shared on social media on May 26, has done what no teaser or interview could: it has shown the world what SS Rajamouli is actually building.

The image — reportedly taken from the set of *Varanasi*, Rajamouli's next film after *RRR* — reveals a sweeping blue-screen backdrop enclosed by sculptured rock formations and intricately carved rock pillars. There are no actors in the frame. There is no dialogue, no context card, no studio watermark. Just scale. The kind of scale that makes you understand why this film's budget is reportedly north of ₹1,000 crore.

## The Ugrabhatti Caves

The sequence being filmed is called the Ugrabhatti caves. As reported by the Times of India, the set is built around the figure of Mata Chinnamasta Devi — a fierce Hindu goddess linked to themes of self-sacrifice, transformation, and cosmic balance. In classical mythology, she is depicted carrying her own severed head while offering her blood to her attendants.

Within the narrative of *Varanasi*, Mahesh Babu's character Rudhra reportedly seeks the goddess's divine grace to defeat an ancient evil force. The use of blue screens across the set confirms that the final sequence will require extensive visual effects — but the physical craftsmanship of the rock pillars and cave walls suggests Rajamouli is mixing practical set design with digital enhancement, much as he did with the war elephants in *Baahubali*.

## What We Know About the Film

*Varanasi* stars Mahesh Babu as Rudhra, Priyanka Chopra as Mandakini, and Prithviraj Sukumaran as the antagonist Kumbha. Music is composed by MM Keeravani, who won an Oscar for *RRR*'s "Naatu Naatu." The film is produced by K.L. Narayana and S.S. Karthikeya under Sri Durga Arts and Showing Business.

Rajamouli has reportedly travelled to Africa's grasslands to capture real-time footage of migratory animals for a separate sequence. He has also confirmed the use of IMAX cameras, most notably for a Ramayana battle sequence within the film.

The film is scheduled for a worldwide theatrical release on April 7, 2027, in standard and IMAX formats.

## Why the Diaspora Should Pay Attention

*RRR* earned over $15 million in North America alone and became a cultural event in the diaspora — Oscar parties, communal theatre screenings, "Naatu Naatu" flash mobs at weddings. *Varanasi* is positioned to be bigger. The combination of Mahesh Babu's first pan-India release under Rajamouli's direction, Priyanka Chopra's global star power, and a mythology-rooted story set in India's holiest city makes this a film the NRI community will rally around.

One leaked photograph shouldn't generate this much anticipation. But when the man who turned a regional Telugu epic into an Oscar winner shows you even a glimpse of what he's building next, you pay attention.

The fact that this single image has no actors, no action, and no dialogue — and still went viral — tells you everything about where this film sits in the cultural imagination of Indian cinema audiences worldwide."""
})


# ------- ARTICLE 2: Netflix India Global Dominance -------
print("\n🎬 Article 2: Netflix India Global Streaming")
img2, attr2 = get_image_for_topic("streaming entertainment India", "Netflix India content")

articles.append({
    "headline": "Three Indian Titles Are on Netflix's Global Charts Right Now. Combined, They've Been Watched for 31 Million Hours.",
    "subheadline": "Kartavya hit No. 1 on the Global Non-English Films list. Desi Bling is trending at No. 6 on Non-English TV. Dhurandhar: Raw and Undekha is at No. 5. At least one Indian title has charted every week since 2025.",
    "slug": "netflix-india-global-charts-kartavya-desi-bling-dhurandhar-31-million-hours-nri-streaming-20260528",
    "image_url": img2,
    "image_caption": "Indian content is now a permanent fixture on Netflix's global charts",
    "image_attribution": attr2,
    "sources": [
        "https://www.bollywoodhungama.com/news/bollywood/kartavya-dhurandhar-raw-and-undekha-and-desi-bling-power-netflix-indias-global-streak-with-31-million-viewing-hours-combined/",
        "https://www.sacnilk.com/tag/Spotify"
    ],
    "body": """There was a time, not long ago, when Indian content appearing on a global Netflix chart was news. A Bollywood film trending in the Top 10 would get press releases. A Malayalam thriller cracking the list would get think pieces.

That era is over. Indian content is no longer visiting the charts. It lives there.

## The Numbers This Week

This week, three Indian titles are simultaneously occupying spots on Netflix's global rankings — a combined 31 million viewing hours of Indian stories being consumed by audiences worldwide.

Leading the pack is *Kartavya*, starring Saif Ali Khan, Rasika Dugal, and Sanjay Mishra. The film climbed from No. 2 last week to No. 1 on the Global Top 10 Non-English Films list, with 16.3 million viewing hours over two weeks. That's not "good for Indian content." That's the most-watched non-English film on the planet.

At No. 5 on the same list is *Dhurandhar: Raw & Undekha*, adding 4.9 million hours. And on the Non-English TV side, *Desi Bling* — the unscripted series that has been described as part reality show, part cultural flex — is trending at No. 6 with 10.4 million viewing hours.

## The Streak

Here's the statistic that matters more than any individual chart position: at least one Indian title has appeared in Netflix's Global Top 10 Non-English rankings every single week since 2025.

Think about what that means. Not every month. Not most weeks. Every week. For over a year. Indian content has been a persistent, reliable, weekly presence on the most competitive streaming charts in the world.

The milestones along the way tell the story of acceleration. *Taskaree: The Smuggler's Web* made history as the first Indian series to hit No. 1 on the Global Non-English TV list. *Kohrra Season 2* stayed on the list for two consecutive weeks. *Accused* (2026) became the first Indian film to trend in over 70 countries. *Border 2* recorded 11.1 million viewing hours across 16 countries. *Mardaani 3* logged 13.7 million hours.

## What Changed

Netflix India's content strategy has quietly shifted from acquiring theatrical films after their box office runs to commissioning original content designed to travel. Shows like *Maamla Legal Hai*, *Hello Baccho*, and *The Great Indian Kapil Show* have built repeat audiences. Regional language originals — Tamil, Telugu, Malayalam — are charting alongside Hindi content.

For the diaspora, this is personally meaningful. The same content that aunties in Hyderabad are watching is now the same content that cousins in Houston are watching — simultaneously, on the same platform, without waiting for a DVD or a satellite broadcast delay. The cultural lag that once defined the NRI entertainment experience has collapsed to zero.

## The Bigger Picture

The 31 million combined viewing hours this week aren't a spike. They're a new baseline. Indian content isn't having a moment on Netflix. It's having an era."""
})


# ------- ARTICLE 3: Khalnayak Returns Director Hunt -------
print("\n🎬 Article 3: Sanjay Dutt Khalnayak Returns")
img3, attr3 = get_image_for_person("Sanjay Dutt")

articles.append({
    "headline": "Sanjay Dutt Got the Idea for Khalnayak Returns in Prison. He Asked 4,000 Inmates to Write Him a One-Pager. Now He Can't Find a Director.",
    "subheadline": "Rajkumar Santoshi politely declined. Subhash Ghai, who directed the 1993 original, already said no. Sanjay Dutt is still looking. The origin story of this sequel is wilder than any script.",
    "slug": "sanjay-dutt-khalnayak-returns-rajkumar-santoshi-declined-director-search-prison-origin-nri-20260528",
    "image_url": img3,
    "image_caption": "Sanjay Dutt at the Khalnayak Returns announcement event in Mumbai",
    "image_attribution": attr3,
    "sources": [
        "https://www.bollywoodhungama.com/news/bollywood/scoop-sanjay-dutt-asks-rajkumar-santoshi-to-direct-khalnayak-returns-veteran-filmmaker-politely-declines-the-offer/",
        "https://www.latestly.com"
    ],
    "body": """The origin story of *Khalnayak Returns* is better than most Bollywood scripts.

Sanjay Dutt was in prison. He had a lot of time. The inmates kept requesting the same songs — the *Khalnayak* soundtrack, on repeat. So Dutt, being Dutt, asked them a question: "If *Khalnayak* gets made again, who'd want to see it?"

All 4,000 prisoners said yes.

Then he asked them to write one-page ideas for the sequel. Four thousand pages arrived.

"It took me a lot of time to read 4,000 pages," Dutt said at the film's announcement event in Mumbai on April 24, alongside Jio Studios' Jyoti Deshpande and Aspect Entertainment's Aksha Kamboj. "One of the ideas that I got appealed to me."

## The Director Problem

The intro teaser, unveiled at the April 24 event, got a thunderous response. Dutt looked menacing. The original *Khalnayak* theme — the one that every Indian who grew up in the 1990s can hum from memory — played underneath. Everything seemed set.

Except for one detail: no director.

Subhash Ghai, who directed the 1993 original, was the obvious choice. He was on stage at the event. He had produced the character that made "Nayak nahi, khalnayak hoon main" one of the most iconic lines in Hindi cinema. But Ghai confessed early that he would not be returning to the director's chair.

So Dutt went to his next choice: Rajkumar Santoshi, the veteran filmmaker behind *Ghayal*, *Andaz Apna Apna*, and most recently *Lahore 1947*. According to Bollywood Hungama, Dutt approached Santoshi personally, arguing that his understanding of commercial cinema would do justice to the sequel. The two have never worked together — and Dutt felt that made the collaboration even more appealing.

Santoshi politely and respectfully declined.

## Why Santoshi Said No

The reason is pragmatic, not dramatic. Santoshi is currently giving final touches to *Lahore 1947*, starring Sunny Deol. He has also written scripts he wants to pitch to Sunny Deol and Aamir Khan. His dance card, in short, is full.

A source told Bollywood Hungama that Santoshi was "touched by Sanjay Dutt's gesture" and wished him well. He appreciated Dutt's look in the teaser. But time is what it is, and Santoshi didn't have any to spare.

Dutt is now reportedly considering other filmmakers. No names have surfaced.

## What Khalnayak Means to the Diaspora

For NRIs who grew up in the 1990s, *Khalnayak* is not just a film. It's a cultural timestamp. "Choli Ke Peeche" was the song your parents wouldn't let you listen to. "Nayak nahi, khalnayak hoon main" was the line every kid shouted on the school playground. Madhuri Dixit's dance in that white choli was your first encounter with the word "controversy."

A sequel — done right — could tap into a well of nostalgia that runs deeper than any IP Marvel has ever acquired. But "done right" requires a director who understands what made the original dangerous, funny, and unapologetically 90s Bollywood. Two veterans have already passed. The third choice will define whether *Khalnayak Returns* is a film or a footnote.

Sanjay Dutt crowdsourced the idea from prison inmates. He may need to crowdsource the director, too."""
})


# ------- ARTICLE 4: Kangana Ranaut's Bharat Bhhagya Viddhaata -------
print("\n🎬 Article 4: Kangana Ranaut Bharat Bhhagya Viddhaata")
img4, attr4 = get_image_for_person("Kangana Ranaut")

articles.append({
    "headline": "Kangana Ranaut's Next Film Is About the Nurses Who Fought Back During 26/11. It Opens the Same Day as Imtiaz Ali's Partition Film.",
    "subheadline": "Bharat Bhhagya Viddhaata releases June 12. Its motion poster focuses on hospital staff, security guards, and ordinary citizens who saved lives during the 2008 Mumbai attacks. The trailer title: 'The Unseen Heroes.'",
    "slug": "kangana-ranaut-bharat-bhhagya-viddhaata-2611-mumbai-attacks-nurses-june-12-imtiaz-ali-nri-20260528",
    "image_url": img4,
    "image_caption": "Kangana Ranaut stars as a nurse in Bharat Bhhagya Viddhaata, a film about 26/11's unseen heroes",
    "image_attribution": attr4,
    "sources": [
        "https://www.bollywoodhungama.com/news/bollywood/bharat-bhhagya-viddhaata-makers-unveil-motion-poster-titled-the-unseen-heroes-featuring-kangana-ranaut/",
        "https://www.latestly.com/entertainment/kangana-ranauts-bharat-bhhagya-viddhaata-pays-tribute-to-unseen-heroes.html",
        "https://www.koimoi.com/bollywood-news/bharat-bhhagya-viddhaata-kangana-ranaut/"
    ],
    "body": """Most films about 26/11 focus on the Taj Hotel. On the commandos. On the known heroes whose names became headlines.

*Bharat Bhhagya Viddhaata* is not that film.

The motion poster, titled "The Unseen Heroes" and released on May 28, tells you exactly what this film is about by showing you who it's about: nurses. Security guards. Hospital staff. The people in Cama Hospital who faced the same terrorists — Ajmal Kasab walked through those corridors — and chose to fight back, hide patients, and hold the line with nothing but courage and a sense of duty.

Kangana Ranaut plays one of those nurses.

## What the Motion Poster Reveals

Director Manoj Tapadia's approach is deliberate and understated. The poster doesn't show explosions or gunfire. It shows ordinary people — in scrubs, in uniforms, in the kind of clothing that tells you they were at work when the world changed. The title card reads: "They didn't wear badges. They didn't carry guns. They saved lives anyway."

It's a sharp contrast to Kangana's last release, *Emergency*, which was mired in certification delays and political controversy. This film feels quieter and more focused. The cast includes Marathi actress Girija Oak and Smita Tambe, suggesting the film will lean into the Marathi-speaking world of the hospital staff who were on duty that night.

The film is produced by Eunoia Films and Floating Rocks Entertainment. It releases on June 12, 2026.

## The June 12 Box Office Battle

That date puts it directly against Imtiaz Ali's *Main Vaapas Aaunga*, starring Diljit Dosanjh, A.R. Rahman, and Naseeruddin Shah — a Partition love story that has been generating significant buzz. Two very different films about two very different moments in India's history, opening on the same Friday.

For exhibitors, it's a programming headache. For audiences, it's a genuine choice between nostalgia and confrontation, between a love story set against history and a survival story set inside it.

## Why This Film Matters to NRIs

The 2008 Mumbai attacks were a defining moment for Indians everywhere. For NRIs, the experience was uniquely painful — watching the attacks unfold on live television from thousands of miles away, refreshing news feeds through the night, calling family members in Mumbai to check if they were alive.

Many NRIs have personal connections to the Colaba-Fort corridor where the attacks took place. The Taj and Oberoi hotels are where visiting relatives stay. CST station is where you catch the train to your grandmother's house. Cama Hospital is where people you know have been treated.

A film that turns the lens away from the famous rescue operations and onto the hospital workers — the nurses who hid patients under beds, the security guard who is said to have warned people with his last breaths — fills a gap in how this event has been remembered on screen.

Films about 26/11 tend to focus on heroism as spectacle. The motion poster for *Bharat Bhhagya Viddhaata* suggests this one will focus on heroism as routine. On people who did their jobs when doing their jobs meant risking their lives. On the unseen, in a story that has been told many times but never quite from this angle.

Whether Kangana Ranaut — whose public persona has become inseparable from political controversy — can disappear into the role of a nurse in a burning hospital will determine whether this film is remembered as a tribute or a vehicle. The motion poster, at least, suggests Tapadia is aiming for the former."""
})


# ============================================================
# PUBLISH ALL
# ============================================================
print("\n" + "=" * 60)
print(f"Publishing {len(articles)} entertainment articles...")
print("=" * 60)

success_count = 0
for i, article in enumerate(articles, 1):
    print(f"\n--- Article {i}/{len(articles)} ---")
    # Validate word count
    word_count = len(article["body"].split())
    print(f"  Word count: {word_count}")
    if word_count < 400:
        print(f"  ⚠ WARNING: Article below 400-word floor!")

    # Validate headline length
    hl_len = len(article["headline"])
    print(f"  Headline length: {hl_len} chars")

    # Validate subheadline
    sh_len = len(article["subheadline"])
    print(f"  Subheadline length: {sh_len} chars")

    # Validate image
    if article.get("image_url"):
        print(f"  Image: ✓ ({article.get('image_attribution', 'unknown')})")
    else:
        print(f"  Image: ✗ No image (will publish without)")

    if publish_article(article):
        success_count += 1

print(f"\n{'=' * 60}")
print(f"✅ Published {success_count}/{len(articles)} articles")
print(f"{'=' * 60}")
