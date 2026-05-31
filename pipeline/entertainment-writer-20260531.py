#!/usr/bin/env python3
"""Entertainment writer for The Videshi — 2026-05-31 batch"""

import json, os, re, sys, time, uuid, urllib.parse, subprocess
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ[k.strip()] = v.strip().strip('"').strip("'")

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    import requests
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
    """Fetch an image from Pexels API using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
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
                url = photos[0].get('src', {}).get('large2x') or photos[0].get('src', {}).get('large')
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image(url):
    """Validate image URL returns HTTP 200 with image content type and >5KB."""
    if not url:
        return False
    try:
        result = subprocess.run(
            ['curl', '-sS', '-I', '-L', '--max-time', '10', url],
            capture_output=True, text=True, timeout=15
        )
        headers = result.stdout.lower()
        if '200 ok' in headers and 'content-type: image/' in headers:
            # Check content-length
            for line in headers.split('\n'):
                if 'content-length:' in line:
                    size = int(line.split(':')[1].strip())
                    if size > 5000:
                        return True
                    else:
                        print(f"  ⚠ Image too small: {size} bytes")
                        return False
            # If no content-length header, assume it's OK (chunked)
            return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False

def publish_article(article):
    """Publish article to Supabase."""
    import requests
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }
    payload = {
        'headline': article['headline'],
        'subheadline': article['subheadline'],
        'body': article['body'],
        'slug': article['slug'],
        'category': 'entertainment',
        'image_url': article.get('image_url', ''),
        'image_attribution': article.get('image_attribution', ''),
        'sources': json.dumps(article.get('sources', [])),
        'status': 'published',
        'vertical': 'entertainment',
        'published_at': datetime.now(timezone.utc).isoformat(),
    }
    try:
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/p2_articles",
            headers=headers,
            json=payload,
            timeout=15
        )
        if r.status_code in [200, 201]:
            print(f"  ✓ Published: {article['headline'][:60]}...")
            return True
        else:
            print(f"  ✗ Publish failed ({r.status_code}): {r.text[:200]}")
            return False
    except Exception as e:
        print(f"  ✗ Publish error: {e}")
        return False


# ─── ARTICLE 1: Karan Johar Instagram Digital Detox ───────────────────────────

def write_karan_johar_article():
    print("\n📝 Article 1: Karan Johar Instagram Digital Detox")
    
    # Image: try Wikipedia for Karan Johar
    image_url = fetch_wikipedia_person_image("Karan Johar")
    image_attribution = "Wikimedia Commons"
    
    if not validate_image(image_url):
        image_url = fetch_pexels_image("Instagram social media phone", "social media detox")
        image_attribution = "Pexels"
    
    article = {
        'headline': "Karan Johar Unfollowed Shah Rukh Khan, Alia Bhatt, and Nearly Everyone on Instagram. He Only Kept Priyanka Chopra.",
        'subheadline': "The filmmaker called it a 'digital detox,' but the internet noticed he still follows exactly one Bollywood star — and she's the one who left India.",
        'slug': 'karan-johar-unfollows-srk-alia-instagram-digital-detox-priyanka-chopra-nri-20260531',
        'image_url': image_url or '',
        'image_attribution': image_attribution,
        'sources': [
            {"name": "Filmfare", "url": "https://filmfare.com"},
            {"name": "Bollywood Hungama", "url": "https://bollywoodhungama.com"},
            {"name": "Pinkvilla", "url": "https://pinkvilla.com"}
        ],
        'body': """Karan Johar has done a lot of dramatic things in his career. He's made Shah Rukh Khan cry on a train platform. He's turned Kajol into a college legend. He's spent two decades being the loudest, most Instagram-fluent filmmaker in Bollywood. But what he did on Thursday might be the most dramatic thing he's done all year — and he did it with a single tap.

He unfollowed almost everyone on Instagram.

Shah Rukh Khan. Alia Bhatt. Kareena Kapoor Khan. Varun Dhawan. Sidharth Malhotra. Kajol. Malaika Arora. Ananya Panday. Manish Malhotra. Even the entire Khan family — Gauri, Aryan, Suhana. Gone. All of them, wiped from his following list in one sweep.

By Friday morning, Karan Johar — a man with 17.5 million followers — was following exactly 74 accounts. Among Bollywood celebrities, only one name remained: **Priyanka Chopra Jonas**.

## The Internet Lost Its Mind

Reddit noticed first, because Reddit always notices first. Screenshots of Karan's following list began circulating within hours. The theories ranged from industry fallout to secret feuds to elaborate PR stunts. Some fans wondered if this was about the underwhelming box office performance of *Chand Mera Dil*, his latest production starring Ananya Panday and Lakshya. Others speculated about behind-the-scenes tensions with Dharma's talent roster.

The timing was suspicious. Karan had just come off a birthday bash at Manish Malhotra's house — a party attended by the same people he was now unfollowing. What changed between cake and unfollow?

## "This Can't Be National News"

Karan addressed the frenzy through his Instagram Story, and he was characteristically blunt.

"It's a DIGITAL DETOX!!!! Am unfollowing everyone to reduce my time and energy spent on the gram!!! This can't be national news for god's sake... please clickbait something else! This is irrelevant!"

A source close to the filmmaker told media outlets that the mass unfollowing was a "social media strategy" — nothing to do with any particular star, page, or person.

## Why Priyanka Chopra?

But the detail that nobody can stop talking about is the Priyanka Chopra detail. Of all the Bollywood celebrities in Karan Johar's orbit — people he's launched, directed, partied with, cried on camera with — the one person he chose to keep following is the one who left Mumbai for Hollywood.

It's probably a coincidence. Maybe he just didn't get to her name in the unfollowing spree. Maybe it's contractual. But for the NRI audience watching from Los Angeles and London and Toronto, it's hard not to read something into it. Priyanka Chopra is the Bollywood star who chose the diaspora path — who moved to America, married an American, built a career outside the Bollywood ecosystem. And she's the one Karan kept.

## What It Says About Bollywood's Social Media Culture

The real story here isn't about who Karan follows. It's about the fact that an Instagram unfollow by a film producer became the biggest entertainment story in India for 48 hours.

Bollywood's relationship with social media has always been performative. Follows and unfollows are read as political statements. Likes are counted. Comment sections are mined for subtext. The industry has built an entire ecosystem around engagement metrics — and Karan Johar, more than anyone, has been at the center of it.

His "digital detox" — whether genuine or strategic — is an acknowledgment that the machine has become exhausting even for the people who built it.

For the diaspora watching from abroad, it's a reminder that Bollywood's real drama has long since moved from the screen to the feed. And sometimes the most interesting plot twist is someone choosing to log off."""
    }
    
    return publish_article(article)


# ─── ARTICLE 2: Vashu Bhagnani ₹400 Crore Lawsuit ────────────────────────────

def write_vashu_bhagnani_article():
    print("\n📝 Article 2: Vashu Bhagnani ₹400 Crore Lawsuit")
    
    # Image: try Wikipedia for David Dhawan
    image_url = fetch_wikipedia_person_image("David Dhawan")
    image_attribution = "Wikimedia Commons"
    
    if not validate_image(image_url):
        image_url = fetch_wikipedia_person_image("Varun Dhawan")
        image_attribution = "Wikimedia Commons"
    
    if not validate_image(image_url):
        image_url = fetch_pexels_image("Bollywood film courtroom", "legal gavel court")
        image_attribution = "Pexels"
    
    article = {
        'headline': "Vashu Bhagnani Just Filed a ₹400 Crore Lawsuit Over Two Songs From Biwi No. 1. The Film They're In Opens June 5.",
        'subheadline': "The 'Chunari Chunari' and 'Ishq Sona Hai' dispute could block the release of David Dhawan's Hai Jawani Toh Ishq Hona Hai, starring Varun Dhawan.",
        'slug': 'vashu-bhagnani-400-crore-lawsuit-tips-biwi-no-1-chunari-chunari-hai-jawani-nri-20260531',
        'image_url': image_url or '',
        'image_attribution': image_attribution,
        'sources': [
            {"name": "Bollywood Hungama", "url": "https://bollywoodhungama.com"},
            {"name": "Zoom TV Entertainment", "url": "https://zoomtventertainment.com"},
            {"name": "India Forums", "url": "https://indiaforums.com"}
        ],
        'body': """There is a particular kind of chaos that only Bollywood can produce — the kind where a 27-year-old song, a father directing his son, a ₹400 crore lawsuit, and a June 5 release date all collide in the same week. Welcome to the *Hai Jawani Toh Ishq Hona Hai* saga.

Veteran producer Vashu Bhagnani's Puja Entertainment has filed a ₹400 crore suit in the Bombay High Court against Tips Industries Limited, Ramesh Taurani, Kumar S. Taurani, and filmmaker David Dhawan. The allegation: two iconic songs from the 1999 blockbuster *Biwi No. 1* — **'Chunari Chunari'** and **'Ishq Sona Hai'** — were used in the upcoming Varun Dhawan-starrer without proper authorization.

The film releases in six days. The court has reportedly permitted the filing and kept it for hearing soon. This could be one of the most explosive copyright battles in recent Bollywood history.

## What Happened

The dispute goes deeper than a simple remix controversy. According to Puja Entertainment's lawyer, Advocate VK Dubey, the original agreements between Puja Entertainment and Tips only covered audio rights — not video. In 2018, Tips reportedly approached Puja Entertainment asking for visual rights as well, but the request fell through.

What happened next is the core of the lawsuit: Puja Entertainment claims it sent a formal notice cancelling even the audio rights, citing non-compliance with royalty terms.

"After these rights were nullified, they should have gone to some court," Dubey told ANI. "You didn't go and you continued to use the music. Not just audio, but they continued to stream the songs on YouTube, Instagram, and other platforms."

If the allegations hold, Tips not only used songs it no longer had rights to — it incorporated them into an entirely new film.

## The Film in the Crosshairs

*Hai Jawani Toh Ishq Hona Hai* stars Varun Dhawan, Mrunal Thakur, and Pooja Hegde, directed by David Dhawan — Varun's father. The CBFC has already cleared the film with a U/A rating and a 136-minute runtime. It's scheduled for a worldwide release on June 5.

The lawsuit seeks an immediate injunction to halt the release, distribution, exhibition, and streaming of the film and its promotional material featuring the disputed songs. Bhagnani is also seeking an additional ₹100 crore in damages if David Dhawan and Tips refuse to change the film's title — which directly references 'Ishq Sona Hai.'

PVR Inox Pictures has already issued a statement dismissing reports of a parallel legal dispute, calling certain claims "misleading." But the Bombay High Court filing is real, and the clock is ticking.

## Why the Diaspora Should Pay Attention

For NRIs who grew up in the late '90s, 'Chunari Chunari' isn't just a song — it's a generational marker. It played at every wedding, every Diwali party, every school cultural night from Edison to Southall. The idea that the rights to that song are contested — and that the contestation is happening days before a major release — is a reminder of how casually Bollywood has historically treated intellectual property.

The Indian film industry's relationship with music rights has always been murky. Songs were traded, re-licensed, and remixed in handshake deals that worked fine until they didn't. What's different now is that the amounts involved (₹400 crore) and the legal infrastructure (Bombay High Court, formal injunction requests) suggest the industry is finally being forced to professionalize.

If the court grants an injunction, *Hai Jawani Toh Ishq Hona Hai* could be delayed or forced into emergency re-edits days before release — a nightmare scenario for any production.

## What Happens Next

The court hearing is expected soon. The film's release date remains June 5 for now. Varun Dhawan has been actively promoting the film, recently clapping back at an influencer who accused him of faking reviews.

Meanwhile, David Dhawan — who has said this will be his last film — is watching his farewell project become the center of a legal firestorm involving songs he didn't produce, rights he doesn't own, and a lawsuit filed by the man who made the original film that made those songs famous.

Bollywood has always been a family business. This week, it's also a family lawsuit."""
    }
    
    return publish_article(article)


# ─── ARTICLE 3: Ram Charan's Peddi — The ₹350 Crore Diaspora Bet ─────────────

def write_ram_charan_peddi_article():
    print("\n📝 Article 3: Ram Charan's Peddi")
    
    # Image: try Wikipedia for Ram Charan
    image_url = fetch_wikipedia_person_image("Ram Charan")
    image_attribution = "Wikimedia Commons"
    
    if not validate_image(image_url):
        image_url = fetch_wikipedia_person_image("Ram Charan (actor)")
        image_attribution = "Wikimedia Commons"
    
    if not validate_image(image_url):
        image_url = fetch_pexels_image("Indian sports wrestling rural", "Indian village sports")
        image_attribution = "Pexels"
    
    article = {
        'headline': "Ram Charan's ₹350 Crore Peddi Opens June 4. It Already Broke the Fastest Indian Pre-Sale Record in North America.",
        'subheadline': "The Telugu sports-action drama hit $100K in US premiere bookings in just four hours — faster than Pushpa 2, Devara, and every other Indian film before it.",
        'slug': 'ram-charan-peddi-350-crore-north-america-advance-booking-record-june-4-nri-20260531',
        'image_url': image_url or '',
        'image_attribution': image_attribution,
        'sources': [
            {"name": "Sacnilk", "url": "https://sacnilk.com"},
            {"name": "Pinkvilla", "url": "https://pinkvilla.com"},
            {"name": "Bollywood Hungama", "url": "https://bollywoodhungama.com"}
        ],
        'body': """The numbers for Ram Charan's *Peddi* don't look like numbers for an Indian film. They look like numbers for a Marvel premiere.

In North America, the Telugu sports-action drama has already sold 10,000 tickets for its premiere shows — nearly three weeks before release. It crossed $100,000 in US pre-sales in just four hours, making it the fastest Indian film to reach that benchmark. As of mid-May, total North American premiere pre-sales had surpassed $300,000.

For context, here's where *Peddi* stands against recent Telugu premieres in North America:

- **Peddi**: $100K+ in 4 hours
- **OG Movie**: $82K+ in 24 hours
- **Devara Part 1**: $75K+ in 24 hours
- **Pushpa 2**: $52K+ in 24 hours
- **Salaar Part 1**: $40K+ in 24 hours

The film releases worldwide on **June 4, 2026**, with North American premieres on June 3.

## What Is Peddi?

Directed by Buchi Babu Sana, *Peddi* is a sports-action drama about a young man from a village who is regarded as a legend in multiple disciplines — cricket, wrestling, running. As he navigates everyday life, he faces a defining test and tries to make a name for himself using the talent he's honed over years.

It's described as a journey of self-discovery and excellence, with themes of personal rivalry and romance woven through the action. Think *Dangal* meets *Rangasthalam*, with A.R. Rahman composing the soundtrack.

The cast includes **Janhvi Kapoor** as the female lead, alongside **Shiva Rajkumar**, **Jagapathi Babu**, **Divyenndu**, and **Boman Irani**.

## ₹350 Crore and Two Delays

The budget — reportedly around ₹350 crore — makes *Peddi* one of the most expensive Telugu films ever produced. It was originally scheduled for March 27, then pushed to April 30, and finally locked for June 4 after post-production delays. The makers made the shift when Yash's *Toxic* vacated the date.

The delays created anxiety in trade circles, but the advance booking numbers have silenced most doubts. The Nizam theatrical rights alone were reportedly locked at ₹63 crore, one of the biggest regional deals in Telugu cinema history.

Ram Charan recently addressed the importance of box office performance, telling ANI: "Good box office performance is related to the next film. You get the scope to experiment more. So numbers are important, but they are not the only thing."

## Why the NRI Market Matters

The $300K+ North American pre-sale isn't just a nice headline — it's a signal of where Indian cinema's economics are heading. For big-ticket Telugu films, the overseas market is no longer supplementary. It's structural.

Ram Charan's post-*RRR* stardom has made him a genuinely global draw. The Telugu diaspora in the US and Canada has grown into one of the most organized film-going communities in North America, with premiere screenings functioning as community events. IMAX tickets for *Peddi* are priced at $35, with premium formats at $30 and standard at $25 — pricing that would have been unthinkable for an Indian film a decade ago.

For the Indian diaspora watching from Edison, Fremont, Plano, and Mississauga, *Peddi* isn't just a movie. It's a test of whether a rural Telugu sports drama — with no English-language crossover play, no superhero IP, no franchise sequel safety net — can command Hollywood-scale ticket prices in American multiplexes.

The advance booking suggests it can.

## What's at Stake

The Telugu film industry is watching *Peddi* closely because the economics are razor-thin at this budget level. At ₹350 crore, the film needs to gross at least ₹500-600 crore worldwide to be considered a financial success. The Telangana exhibitor dispute — where single-screen owners are demanding a shift from rental to percentage-sharing models — adds an additional layer of risk.

The film's producer made an emotional appeal during a recent chamber meeting: "I spent 350 crores on this film. We have already postponed from March 27 and April 30. My film should not be affected by this percentage model conflict."

Whether *Peddi* delivers or stumbles, it will define the ceiling for Telugu cinema's global ambitions in 2026. The premiere is in five days. The tickets are selling. The diaspora is watching."""
    }
    
    return publish_article(article)


# ─── MAIN ─────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("=" * 60)
    print("The Videshi — Entertainment Writer (2026-05-31)")
    print("=" * 60)
    
    results = []
    results.append(("Karan Johar Digital Detox", write_karan_johar_article()))
    results.append(("Vashu Bhagnani Lawsuit", write_vashu_bhagnani_article()))
    results.append(("Ram Charan Peddi", write_ram_charan_peddi_article()))
    
    print("\n" + "=" * 60)
    print("RESULTS:")
    for name, success in results:
        print(f"  {'✓' if success else '✗'} {name}")
    
    failures = sum(1 for _, s in results if not s)
    if failures:
        print(f"\n⚠ {failures} article(s) failed to publish")
        sys.exit(1)
    else:
        print(f"\n✓ All {len(results)} articles published successfully")
