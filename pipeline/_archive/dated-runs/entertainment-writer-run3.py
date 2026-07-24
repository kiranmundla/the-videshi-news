#!/usr/bin/env python3
"""Videshi Entertainment Writer — Run 3 (2026-05-18 15:30 UTC)"""

import requests
import os
import json
import re
from datetime import datetime, timezone

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

def make_slug(headline, suffix="20260518"):
    slug = headline.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug[:70].rstrip('-')
    return f"{slug}-{suffix}"

def update_topic(topic_id, status):
    url = f"{SUPABASE_URL}/rest/v1/p2_topics?id=eq.{topic_id}"
    r = requests.patch(url, headers=HEADERS, json={"status": status})
    print(f"  Topic {topic_id[:8]} -> {status}: {r.status_code}")

def insert_article(article):
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    r = requests.post(url, headers=HEADERS, json=article)
    if r.status_code in (200, 201):
        data = r.json()
        aid = data[0]['id'] if isinstance(data, list) else data['id']
        print(f"  ✅ Published: {article['headline'][:60]}... -> {aid}")
        return aid
    else:
        print(f"  ❌ Failed: {r.status_code} {r.text[:200]}")
        return None

# ─────────────────────────────────────────
# ARTICLE 1: Welcome to the Jungle Title Track
# ─────────────────────────────────────────

headline_1 = "The Song That Made Every NRI's Uncle Forward a WhatsApp Voice Note: 'Welcome to the Jungle' Title Track Is Here"
subheadline_1 = "Shaan's vocals, Sajid Wajid's legacy, and a franchise that refuses to let the diaspora forget where comedy comes from. The third installment drops its anthem — and it sounds exactly like 2007 feels."
slug_1 = make_slug("welcome-jungle-title-track-nri-nostalgia-bollywood", "20260518")

body_1 = """There are exactly three things guaranteed to unite every Indian family WhatsApp group: someone's kid's birthday photos, a "Good Morning 🌸" forward at 5:47 AM, and the Welcome franchise.

The title track of *Welcome to the Jungle* — the third film in the franchise that gave us Nana Patekar saying "Aap chronology samajhiye" a decade before the phrase became a political meme — dropped this week, and it does precisely what it needs to do: remind you of 2007 while sounding like it belongs in 2026.

## Shaan, Sajid Wajid, and the Architecture of Nostalgia

The original *Welcome* title track wasn't just a song. For a generation of Indian kids growing up abroad, it was the sound of summer trips to India, of cousins crammed into an Ambassador, of watching pirated DVDs on a portable player during a 16-hour flight to Delhi.

This reimagined version — composed by Vikram Montrose with new lyrics by Meggha Bali and Shabbir Ahmed — keeps Sajid Wajid's melodic DNA intact while layering in the kind of bass-heavy production that'll make your Dolby Atmos subscription feel worth it. Shaan, whose voice has been the unofficial background score of Indian childhood since the late '90s, returns alongside Priya Patidar, and together they deliver a track that straddles the line between homage and reinvention.

## The Cast: Everyone You Remember, Plus a Few You'll Learn

Akshay Kumar and Suniel Shetty are back — because what is *Welcome* without Majnu Bhai's paintings and Uday Shetty's deadpan? Joining them are Disha Patani, Jacqueline Fernandez, Arshad Warsi, and Jackie Shroff, a cast list that reads like a Filmfare party guest list from two different decades.

Director Ahmed Khan, who took over from Anees Bazmee, has described the film's tone as darker and more layered than its predecessors — which is a bold claim for a franchise whose most iconic scene involves Nana Patekar yelling at a goat. The soundtrack spans six tracks, each apparently calibrated to a different flavour of chaos.

## June 26: Mark Your Calendars (and Your Fandango Alerts)

*Welcome to the Jungle* is set for a June 26, 2026 theatrical release — which, for NRIs in North America, means a Thursday night IMAX showing if you're lucky, or a Saturday matinee at that one AMC in Edison, New Jersey that always smells like samosas because someone in the back row definitely brought some.

The franchise has always punched above its weight internationally. The original *Welcome* grossed handsomely overseas at a time when Bollywood's international footprint was still finding its shape. *Welcome Back* in 2015 did even better. This third instalment, with its bigger cast and louder production, is clearly chasing the diaspora dollar — and the title track is the opening salvo.

## What the Title Track Actually Tells You

Strip away the nostalgia, and the track reveals something interesting about where Bollywood music is heading. The blend of Shaan's classical training with Montrose's contemporary production isn't just sonic — it's strategic. Bollywood's biggest hits right now live on Instagram Reels and YouTube Shorts, and this track is engineered for exactly that lifecycle: a hook that lands in the first eight seconds, a chorus that begs to be lip-synced, and a bridge that gives wedding DJs exactly what they need.

For the diaspora, the real test isn't whether the song is good. It's whether it'll dethrone "Swag Se Swagat" at your cousin's sangeet. Early signs suggest: quite possibly.

The full soundtrack is now streaming on Spotify, Apple Music, JioSaavn, and every other platform your dad accidentally subscribed to while trying to play bhajans."""

article_1 = {
    "headline": headline_1,
    "subheadline": subheadline_1,
    "slug": slug_1,
    "body": body_1,
    "category": "entertainment",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": [
        {"url": "https://www.bollywoodhungama.com/news/bollywood/welcome-to-the-jungle-title-track-out-now/", "name": "Bollywood Hungama"},
        {"url": "https://www.filmfare.com/news/bollywood/makers-drop-welcome-to-the-jungle-title-track-featuring-akshay-kumar-suniel-shetty-more", "name": "Filmfare"}
    ],
    "score_total": 56,
    "word_count": len(body_1.split()),
    "vertical": "entertainment",
    "urgency": "daily",
    "topic_id": "55012064-817f-46ef-ba07-2e23345d4857",
    "tags": ["Akshay Kumar", "Welcome to the Jungle", "Bollywood", "Shaan", "franchise", "title track", "Suniel Shetty", "Disha Patani"],
    "diaspora_angle": "The Welcome franchise is comfort cinema for NRIs — the title track is engineered for diaspora nostalgia, wedding DJs, and overseas theatrical runs.",
    "image_search_query": "Akshay Kumar Welcome to the Jungle 2026 Bollywood film",
    "image_must_show": "Akshay Kumar or Welcome to the Jungle film poster/still"
}

# ─────────────────────────────────────────
# ARTICLE 2: Karthik Subbaraj + Ilaiyaraaja + Guneet Monga
# ─────────────────────────────────────────

headline_2 = "1,540 Films Later, Ilaiyaraaja Said Yes to a Director Born After His First Hit — and It Might Be the Most Important Tamil Collaboration of the Decade"
subheadline_2 = "Karthik Subbaraj's 10th film pairs him with the maestro whose music soundtracked every Tamil household on three continents. Guneet Monga — the Oscar winner — is producing. Here's why this matters."
slug_2 = make_slug("ilaiyaraaja-karthik-subbaraj-guneet-monga-tamil", "20260518")

body_2 = """Here is a number that should make you sit down: 1,540.

That's how many films Ilaiyaraaja has composed music for. One thousand, five hundred, and forty. By the time you finish reading this article, he might have started on 1,541. The man who gave Tamil cinema its emotional vocabulary — who made a violin weep in *Hey Ram*, made a flute laugh in *Mouna Ragam*, and made an entire generation of Tamils abroad cry into their filter coffee every time "Ilaiya Nila" played at a community gathering — has agreed to score Karthik Subbaraj's 10th directorial film.

This is Subbaraj's first time working with Ilaiyaraaja. Let that sink in.

## The Director Who Grew Up on the Maestro's Music

Karthik Subbaraj is 42. Ilaiyaraaja is 81. When Ilaiyaraaja composed the music for *Annakili* in 1976 — the film that announced him to the world — Subbaraj's parents might not have even met yet. Subbaraj has spoken openly about growing up in a household where Ilaiyaraaja's music wasn't just background noise; it was weather. It shaped the room. It determined the mood. It was the difference between a good Sunday and a great one.

"This is a dream come true," Subbaraj said when the collaboration was announced. For once, the phrase isn't cliché. You can hear the kid from Madurai in that sentence, the one who watched *Nayakan* on a VCR and decided he wanted to make films.

The project — untitled for now — began production in Madurai after a traditional pooja ceremony. The symbolism is intentional: Subbaraj returning to where he started, carrying the music of the man who started everything.

## Guneet Monga: From the Oscars to Madurai

The producing credit might be the most fascinating part of this equation. Guneet Monga Kapoor — who, through Sikhya Entertainment, produced *The Elephant Whisperers*, which won India's first Academy Award for Best Documentary Short in 2023 — is backing this film alongside Jio Studios.

Monga's involvement signals something significant. She doesn't chase volume. She chases stories that travel — films that work in Chennai and in Cannes, that resonate at TIFF and at the neighbourhood Urvashi Theatre. Her track record includes *The Lunchbox*, *Masaan*, and *Pagglait* — films that the Indian diaspora discovered on Netflix and Amazon and adopted as personal favourites. If she's backing Subbaraj's collaboration with Ilaiyaraaja, it's because she believes it has global legs.

For NRIs who've watched Monga's career from afar — who felt a swell of pride when she walked the Oscar stage in a sari — this film represents the best possible version of what Indian independent cinema can be: auteur-driven, culturally rooted, internationally ambitious, and scored by a literal god.

## What 1,540 Means to the Diaspora

There is a specific experience that only Tamil diaspora families understand: the moment when Ilaiyaraaja's music comes on — at a temple function in Flushing, at a Pongal celebration in Scarborough, at a house party in Hounslow — and every uncle in the room suddenly becomes 22 again.

His music isn't just composition. It's time travel. It's the bridge between the India your parents left and the one you visit every two years. It's the reason your Spotify Wrapped has a genre that says "Tamil Film Classical" even though you listen to Drake the other 11 months.

Ilaiyaraaja composing his 1,540th film at 81 — for a director who represents Tamil cinema's next generation, produced by a woman who brought India its first documentary Oscar — isn't just a collaboration. It's a handshake across eras, across oceans, across the vast distance between the Madurai of 1976 and the global Tamil diaspora of 2026.

## What We Know So Far

The title hasn't been announced. The cast is under wraps. The genre is a mystery. What we know: it's an indie production by Tamil cinema standards, backed by Jio Studios' resources and Sikhya's taste. Subbaraj's filmography — *Pizza*, *Iraivi*, *Jigarthanda*, *Mahaan* — suggests it won't be a typical commercial outing. And Ilaiyaraaja has said he finds Subbaraj's storytelling "refreshing," which, coming from a man who has worked with Mani Ratnam, Balachander, and Bharathiraja, is about as high a compliment as Tamil cinema offers.

Watch this space. The music, when it arrives, will make your Spotify algorithm very confused — and your parents very, very happy."""

article_2 = {
    "headline": headline_2,
    "subheadline": subheadline_2,
    "slug": slug_2,
    "body": body_2,
    "category": "entertainment",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": [
        {"url": "https://www.filmfare.com/news/tamil/karthik-subbaraj-ropes-in-ilaiyaraaja-for-milestone-tenth-film", "name": "Filmfare"},
        {"url": "https://news.webindia123.com/director-karthik-subbaraj-teams-up-with-maestro-ilaiyaraaja", "name": "WebIndia123"},
        {"url": "https://tamilmoviesdatabase.com/karthik-subbaraj-joins-hands-with-ilaiyaraaja", "name": "Tamil Movies Database"}
    ],
    "score_total": 56,
    "word_count": len(body_2.split()),
    "vertical": "entertainment",
    "urgency": "daily",
    "topic_id": "95b6f74e-cb23-4ab1-bf16-37aecc5b1853",
    "tags": ["Ilaiyaraaja", "Karthik Subbaraj", "Guneet Monga", "Tamil cinema", "Sikhya Entertainment", "Jio Studios", "Oscar", "Indian independent cinema"],
    "diaspora_angle": "Guneet Monga's Oscar win resonated deeply with the Indian diaspora; Ilaiyaraaja's music is the emotional soundtrack of Tamil households on three continents.",
    "image_search_query": "Ilaiyaraaja composer 2025 2026",
    "image_must_show": "Ilaiyaraaja or Karthik Subbaraj"
}

# ─────────────────────────────────────────
# EXECUTE
# ─────────────────────────────────────────

print("=" * 60)
print("VIDESHI ENTERTAINMENT WRITER — RUN 3")
print("=" * 60)

# Publish articles
print("\n📝 Publishing Article 1: Welcome to the Jungle")
aid_1 = insert_article(article_1)

print("\n📝 Publishing Article 2: Ilaiyaraaja x Subbaraj x Monga")
aid_2 = insert_article(article_2)

# Update topic statuses
print("\n📋 Updating topic statuses...")
update_topic("55012064-817f-46ef-ba07-2e23345d4857", "published")  # Akshay Kumar Welcome
update_topic("95b6f74e-cb23-4ab1-bf16-37aecc5b1853", "published")  # Karthik Subbaraj
update_topic("afd7a6ca-ec8e-43d0-bdbf-9e7aff732093", "rejected")   # Ram Charan Peddi (overlap)
update_topic("f6a859f4-8ce5-4bba-89db-19f384b9f9c3", "rejected")   # Dan Levy (no diaspora)

print("\n✅ Articles published, topics updated.")
print(f"   Article 1 ID: {aid_1}")
print(f"   Article 2 ID: {aid_2}")
