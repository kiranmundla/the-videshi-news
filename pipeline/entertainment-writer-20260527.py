#!/usr/bin/env python3
"""Entertainment writer for The Videshi — 2026-05-27 run"""

import json, os, re, sys, time, uuid, traceback
from datetime import datetime, timezone
import requests, urllib.parse

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

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
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
    for attempt in range(3):
        try:
            r = requests.get(
                f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
                headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
                timeout=10
            )
            if r.status_code == 429:
                wait = 2 * (attempt + 1)
                print(f"  ⚠ Wikipedia rate limited, waiting {wait}s...")
                time.sleep(wait)
                continue
            if r.status_code == 200:
                data = r.json()
                img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
                if img:
                    print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                    return img
            break
        except Exception as e:
            print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
            break
    return None

def fetch_pexels_image(query, fallback_query=None):
    """Fetch a relevant image from Pexels as fallback."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    import subprocess
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
                 f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=3&orientation=landscape'],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            if photos:
                url = photos[0]['src']['large2x']
                print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image(url):
    """Validate image URL returns HTTP 200 with image content > 5KB."""
    if not url:
        return False
    for attempt in range(3):
        try:
            r = requests.head(url, timeout=10, allow_redirects=True,
                             headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            if r.status_code == 429:
                wait = 2 * (attempt + 1)
                print(f"  ⚠ Image validation rate limited, waiting {wait}s...")
                time.sleep(wait)
                continue
            content_type = r.headers.get('Content-Type', '')
            content_length = int(r.headers.get('Content-Length', 0))
            if r.status_code == 200 and 'image' in content_type:
                if content_length == 0 or content_length > 5000:
                    print(f"  ✓ Image validated: {r.status_code}, {content_type}, {content_length} bytes")
                    return True
                else:
                    print(f"  ✗ Image too small: {content_length} bytes")
            else:
                print(f"  ✗ Image validation failed: {r.status_code}, {content_type}")
            return False
        except Exception as e:
            print(f"  ✗ Image validation error: {e}")
            return False
    return False

def publish_article(article):
    """Publish article to Supabase."""
    payload = {
        'id': str(uuid.uuid4()),
        'headline': article['headline'],
        'subheadline': article['subheadline'],
        'body': article['body'],
        'slug': article['slug'],
        'category': 'entertainment',
        'vertical': 'entertainment',
        'status': 'published',
        'published_at': datetime.now(timezone.utc).isoformat(),
        'sources': json.dumps(article.get('sources', [])),
        'image_url': article.get('image_url', ''),
        'image_caption': article.get('image_caption', ''),
        'image_attribution': article.get('image_attribution', ''),
        'urgency': 'daily',
        'word_count': len(article['body'].split()),
        'score_total': 80
    }

    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=payload,
        timeout=30
    )
    if r.status_code in (200, 201):
        print(f"  ✓ Published: {article['headline'][:60]}...")
        return True
    else:
        print(f"  ✗ Publish failed ({r.status_code}): {r.text[:200]}")
        return False


# ============================================================
# ARTICLE 1: Suriya's Karuppu — ₹250 Crore Blockbuster
# ============================================================

def write_article_1():
    print("\n📝 Article 1: Suriya's Karuppu ₹250 Crore Blockbuster")

    # Image: Wikipedia for Suriya
    image_url = fetch_wikipedia_person_image("Suriya")
    if not image_url or not validate_image(image_url):
        image_url = fetch_wikipedia_person_image("Suriya (actor)")
        if not image_url or not validate_image(image_url):
            image_url = fetch_pexels_image("Tamil cinema audience celebration")
    image_attr = "Wikimedia Commons" if image_url and "wiki" in image_url else "Pexels"

    body = """Suriya has spent the better part of a decade watching Tamil cinema's commercial centre shift toward younger faces and bigger franchises. Kanguva underwhelmed. Retro grossed respectably but never turned a profit against its budget. The talk, in industry circles and among NRI Tamil audiences who once packed single-screens for Singam, was that the Suriya era had quietly ended.

Karuppu has made that conversation irrelevant.

## The Numbers That Matter

Directed by RJ Balaji, the fantasy-action-courtroom drama crossed ₹250 crore worldwide in just 12 days — making it Suriya's highest-grossing film by a wide margin and the biggest Tamil hit of 2026 so far. In Tamil Nadu alone, it has collected over ₹130 crore, shattering Singam 2's 13-year-old state record and becoming only the second Tamil film ever to cross that mark after Rajinikanth's Enthiran.

The India net stands at approximately ₹155 crore. Overseas, Tamil diaspora audiences have contributed ₹67-68 crore — a staggering number for a Tamil-language film that is not a franchise sequel and has no Hindi dub release.

## What Makes Karuppu Different

The film blends a guardian-deity mythology with a courtroom drama about systemic corruption — not exactly the formula Hollywood studios greenlight in pitch meetings. RJ Balaji, better known as an actor-comedian, directed with a visual ambition and tonal control that surprised even the film's producers at Dream Warrior Pictures.

Trisha Krishnan returns opposite Suriya for the first time in years, and their pairing has been cited by audiences as a key driver for repeat viewings — particularly in B-centres and rural Tamil Nadu, where the film's single-screen numbers are unusually strong.

## The Vijay Connection

In a revelation that added another layer to the film's narrative, RJ Balaji disclosed that Karuppu was originally conceived as Vijay's final film before the actor entered Tamil Nadu politics. When Vijay's political timeline accelerated and his farewell project Jana Nayagan took a different route (which itself remains stalled in CBFC limbo), the script was adapted for Suriya with significant creative reworking.

The fact that Tamil Nadu Chief Minister Vijay personally congratulated the Karuppu team after its release suggests no hard feelings — and adds a fascinating footnote to both careers.

## Why NRIs Should Pay Attention

For the Tamil diaspora, Karuppu represents something increasingly rare: a mass Tamil film that is genuinely good at the box office without relying on franchise recognition or a pan-India dubbed release strategy. Its overseas numbers — nearly $8 million — were driven almost entirely by Tamil-speaking audiences in the US, UK, Canada, and the Gulf.

In an industry where the loudest commercial successes often come from dubbed Hindi releases or sequel IP, Karuppu's purely Tamil-rooted performance is a statement. It says the language-specific audience, at home and abroad, can still carry a film past ₹250 crore without any crossover concessions.

## What Comes Next

The film is expected to comfortably cross ₹300 crore worldwide before its theatrical run ends, which would place it among the top 10 highest-grossing Tamil films of all time. An OTT deal — likely with a premium streamer given the numbers — has not been announced but is expected within the month.

For Suriya, now 50, the message is simpler: the audience was always there. The material just needed to meet them where they live."""

    return {
        'headline': "Suriya's Karuppu Just Crossed ₹250 Crore in 12 Days. It Was Originally Written for Vijay. Tamil Cinema's Biggest Hit of 2026 Was Supposed to Be Someone Else's Farewell.",
        'subheadline': "RJ Balaji's fantasy-courtroom drama has become Suriya's highest-grossing film ever, shattering Singam 2's 13-year Tamil Nadu record and proving the Tamil-language audience — at home and in the diaspora — doesn't need a Hindi dub to deliver blockbuster numbers.",
        'body': body,
        'slug': 'suriya-karuppu-250-crore-vijay-original-script-tamil-cinema-biggest-hit-2026-nri-diaspora',
        'sources': [
            {"name": "Filmibeat", "url": "https://www.filmibeat.com"},
            {"name": "Cinema Express", "url": "https://www.cinemaexpress.com"},
            {"name": "Pinkvilla", "url": "https://www.pinkvilla.com"},
            {"name": "Hollywood Reporter India", "url": "https://www.hollywoodreporterindia.com"}
        ],
        'image_url': image_url or '',
        'image_caption': 'Suriya in a promotional still',
        'image_attribution': image_attr
    }


# ============================================================
# ARTICLE 2: Imtiaz Ali's Main Vaapas Aaunga
# ============================================================

def write_article_2():
    print("\n📝 Article 2: Imtiaz Ali's Main Vaapas Aaunga")

    # Image: Wikipedia for Imtiaz Ali
    image_url = fetch_wikipedia_person_image("Imtiaz Ali (director)")
    if not image_url or not validate_image(image_url):
        image_url = fetch_wikipedia_person_image("Imtiaz Ali")
        if not image_url or not validate_image(image_url):
            image_url = fetch_pexels_image("vintage train India Partition")
    image_attr = "Wikimedia Commons" if image_url and "wiki" in image_url else "Pexels"

    body = """Imtiaz Ali has not made a film since Love Aaj Kal in 2020. That film was a commercial disaster and a creative misfire that seemed to confirm what the industry whispered: the man who made Jab We Met and Rockstar had lost his compass. Six years of silence followed. Now he is back with a Partition love story, an A.R. Rahman score, Diljit Dosanjh in a major role, and two of Bollywood's most promising young actors. The film releases on June 12. It is called Main Vaapas Aaunga.

## The Story

The film spans two timelines. In the present, Naseeruddin Shah plays an elderly Sardar navigating the weight of a love severed by the 1947 Partition. In the past, Vedang Raina and Sharvari play the young lovers whose world is torn apart. Diljit Dosanjh occupies a role that connects both timelines — details of which the team has kept deliberately vague.

In interviews, Ali has said every element of the film is rooted in real accounts collected over years from Partition survivors. "The generation that lived through it is almost gone," he told Anupama Chopra. "If we don't tell their stories now, we lose them forever."

## The Reunion That Matters Most

This is an A.R. Rahman-Irshad Kamil-Imtiaz Ali reunion — the same trio behind Rockstar, Highway, and Tamasha. For a generation of listeners (and an even larger generation of NRIs who grew up on those soundtracks), this combination carries enormous emotional weight. Rahman's involvement was reportedly finalized before the cast, which tells you where Ali's priorities sit.

## The Cast

Vedang Raina (fresh off The Archies and reportedly the lead of YRF's next big franchise play) and Sharvari (Alpha, Munjya) bring a young commercial credibility that Ali's recent films have lacked. Diljit Dosanjh — who just made history as the first South Asian artist to sell out two consecutive nights at Madison Square Garden — brings the star power and the Punjabi cultural authenticity that a Partition story demands.

Naseeruddin Shah, at 76, lends the gravitas of an actor who has spent five decades making Hindi cinema smarter. Ali has called casting a non-Sikh actor as a Sardar "a deliberate creative choice about the universality of loss."

## The Box Office Clash

Main Vaapas Aaunga opens on June 12 against Kangana Ranaut's Bharat Bhhagya Viddhaata, Manoj Bajpayee's Governor: The Silent Saviour, and Vikram Bhatt's Haunted 3D: Echoes of the Past. Ali, characteristically unfazed, has said he announced his date first and sees no reason to move.

The real question is whether Indian audiences — and specifically NRI audiences who keep Ali's films alive on streaming long after their theatrical runs — will show up for a Partition film in summer. The genre has a complicated history at the box office. Gadar 2 worked because it was a sequel to a phenomenon. Original Partition stories, even good ones, have historically struggled commercially.

## Why It Matters for the Diaspora

Partition is not history for much of the Indian diaspora. It is family memory. Grandparents who crossed borders, relatives who stayed behind, stories told at kitchen tables that never quite ended. Ali has built his career on capturing the ache of separation — romantic, geographic, emotional. A film that applies that instinct to the foundational separation of modern South Asian identity could resonate deeply with NRI audiences who carry those stories in ways they rarely articulate.

Or it could be another Love Aaj Kal 2. That is the risk of caring about a filmmaker who has both Rockstar and Love Aaj Kal 2 on his resume. June 12 will tell us which version of Imtiaz Ali showed up."""

    return {
        'headline': "Imtiaz Ali Has Not Made a Film in Six Years. His Comeback Is a Partition Love Story With Diljit, A.R. Rahman, and Naseeruddin Shah. It Opens June 12 Against Kangana.",
        'subheadline': "Main Vaapas Aaunga reunites the Rockstar trio of Ali, Rahman, and Irshad Kamil for a two-timeline story about love severed in 1947 — featuring Vedang Raina, Sharvari, and the biggest Punjabi star on the planet.",
        'body': body,
        'slug': 'imtiaz-ali-main-vaapas-aaunga-partition-diljit-dosanjh-ar-rahman-june-12-nri-diaspora',
        'sources': [
            {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com"},
            {"name": "Hollywood Reporter India", "url": "https://www.hollywoodreporterindia.com"},
            {"name": "Filmfare", "url": "https://www.filmfare.com"},
            {"name": "Zoom TV Entertainment", "url": "https://www.zoomtventertainment.com"}
        ],
        'image_url': image_url or '',
        'image_caption': 'Director Imtiaz Ali',
        'image_attribution': image_attr
    }


# ============================================================
# ARTICLE 3: Diljit Dosanjh — MSG History and Bomb Threats
# ============================================================

def write_article_3():
    print("\n📝 Article 3: Diljit Dosanjh — MSG History to Bomb Threats")

    # Image: Wikipedia for Diljit Dosanjh
    image_url = fetch_wikipedia_person_image("Diljit Dosanjh")
    if not image_url or not validate_image(image_url):
        image_url = fetch_pexels_image("concert arena crowd lights", "Madison Square Garden concert")
    image_attr = "Wikimedia Commons" if image_url and "wiki" in image_url else "Pexels"

    body = """On May 25, Diljit Dosanjh became the first South Asian artist to sell out two consecutive nights at Madison Square Garden. Thousands of fans — many of them first-generation Punjabi Americans and second-generation kids who grew up on their parents' playlists — packed the arena for the AURA tour. Free Kada Prasad was distributed to the crowd. Chef Vikas Khanna called him "India's global ambassador." The moment felt like a cultural arrival that was years in the making.

The same day, a bomb threat was emailed to the Ludhiana Municipal Corporation naming Diljit's family home as a target.

## The Threat

The email, sent on May 25 to municipal officials, claimed affiliation with the "Khalistan National Army" and warned of blasts before June 6 — the anniversary of Operation Blue Star, the 1984 Indian military operation at the Golden Temple in Amritsar. The sender wrote that "whoever helps Diljit will be killed."

Punjab Police and cybercrime units launched an investigation. Diljit's Ludhiana residence was searched; no suspicious materials were found. Authorities have classified the threat as a hoax, but security has been tightened around the singer's properties and the broader Ludhiana area in the lead-up to the sensitive June anniversary period.

This is not an isolated incident. Punjab has seen a surge in institutional bomb threats in 2026, with schools, government offices, and public figures targeted by email campaigns that investigators believe are coordinated from outside India.

## The MSG Milestone

The bomb threat is a grim counterpoint to what should have been an unambiguous moment of celebration. Diljit's MSG concerts were not just sold out — they were cultural events. The stage that has hosted Elton John, Madonna, and Billy Joel now belongs, for two nights, to a Punjabi singer from Dosanjh Kalan, a village in Jalandhar district.

During his recent Vancouver show, Diljit paused to speak about the Komagata Maru incident — the 1914 turning away of a ship carrying Punjabi immigrants from Canada — connecting his global tour to the longer history of South Asian migration, exclusion, and eventual belonging.

## The Tour Continues

The AURA tour has additional dates through June and July, including shows in Toronto and Vancouver — the two cities with the largest Punjabi diaspora populations outside India. Whether the bomb threat will affect security protocols or concert logistics remains unclear, but Diljit's team has not indicated any cancellations.

## Where Diljit Stands Now

At 42, Diljit Dosanjh occupies a position no Indian artist has held before. He is simultaneously the biggest live act in the Punjabi diaspora, a Bollywood leading man (his next film, Imtiaz Ali's Main Vaapas Aaunga, opens June 12), a streaming phenomenon, and — after Sia and David Guetta collaborations — a crossover name in global pop.

He is also, as the bomb threat makes uncomfortably clear, a symbol. For the diaspora, he represents the possibility that Punjabi culture can command the world's most famous stages without dilution. For extremist elements that the threat email represents, he is a target precisely because of that mainstream success — a Sikh artist who chose music over politics, global stages over ideological allegiance.

## For NRIs With Tickets

If you are an NRI with AURA tour tickets — and many of you are, given that Diljit's North American shows sell out within hours — the practical concern is security at upcoming venues. Large-scale concert security in the US and Canada operates at a fundamentally different level than in India, and venue operators typically coordinate with local law enforcement well in advance of any flagged events.

The emotional concern is harder to address. Watching a cultural icon achieve something historic while simultaneously being threatened for existing in public is a dissonance that diaspora communities know intimately. Diljit's response, characteristically, has been to keep performing. The next show is the answer."""

    return {
        'headline': "Diljit Dosanjh Sold Out Two Consecutive Nights at Madison Square Garden. The Same Day, Someone Emailed a Bomb Threat to His Family Home in Ludhiana.",
        'subheadline': "The first South Asian artist to sell out back-to-back MSG shows is now performing under heightened security after a threat linked to the Operation Blue Star anniversary targeted his residence. The AURA tour continues.",
        'body': body,
        'slug': 'diljit-dosanjh-madison-square-garden-bomb-threat-ludhiana-aura-tour-nri-diaspora',
        'sources': [
            {"name": "Cinema Express", "url": "https://www.cinemaexpress.com"},
            {"name": "Bollywood Life", "url": "https://www.bollywoodlife.com"},
            {"name": "Punjab News Line", "url": "https://www.punjabnewsline.com"},
            {"name": "Inshorts", "url": "https://www.inshorts.com"}
        ],
        'image_url': image_url or '',
        'image_caption': 'Diljit Dosanjh',
        'image_attribution': image_attr
    }


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    print("=" * 60)
    print("The Videshi Entertainment Writer — 2026-05-27")
    print("=" * 60)

    articles = []
    for writer_fn in [write_article_1, write_article_2, write_article_3]:
        try:
            article = writer_fn()
            articles.append(article)
        except Exception as e:
            print(f"  ✗ Error writing article: {e}")
            traceback.print_exc()

    print(f"\n📤 Publishing {len(articles)} articles...")
    published = 0
    for article in articles:
        # Final validation
        if len(article['body']) < 400:
            print(f"  ✗ REJECTED (body too short: {len(article['body'])} chars): {article['headline'][:50]}")
            continue
        if len(article['headline']) > 200:
            print(f"  ⚠ Headline over 200 chars ({len(article['headline'])}), truncating")
            article['headline'] = article['headline'][:197] + "..."
        if not article.get('subheadline') or len(article['subheadline']) < 15:
            print(f"  ✗ REJECTED (missing/short subheadline): {article['headline'][:50]}")
            continue

        if publish_article(article):
            published += 1
        time.sleep(1)

    print(f"\n✅ Done: {published}/{len(articles)} articles published")
