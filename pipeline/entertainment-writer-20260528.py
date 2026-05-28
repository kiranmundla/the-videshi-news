#!/usr/bin/env python3
"""Entertainment writer for The Videshi — 2026-05-28 batch"""

import json, os, sys, time, uuid, re
from datetime import datetime, timezone
import requests
import subprocess

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ[k] = v

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
    encoded = person_name.replace(' ', '_')
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
    """Fetch image from Pexels using curl (urllib gets 403)."""
    import urllib.parse as _up
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            encoded_q = _up.quote(q)
            result = subprocess.run(
                ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
                 f'https://api.pexels.com/v1/search?query={encoded_q}&per_page=3&orientation=landscape'],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            if photos:
                img_url = photos[0]['src']['large2x']
                print(f"  ✓ Pexels image found for '{q}': {img_url[:80]}...")
                return img_url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image(url):
    """Validate image URL returns 200 with image content type and >5KB."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        content_type = r.headers.get('Content-Type', '')
        content_length = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in content_type and content_length > 5000:
            print(f"  ✓ Image validated: {content_length} bytes, {content_type}")
            return True
        # Try GET if HEAD fails
        r = requests.get(url, timeout=10, stream=True, allow_redirects=True,
                        headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        content_type = r.headers.get('Content-Type', '')
        content_length = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in content_type:
            # Read enough to check size
            data = b''
            for chunk in r.iter_content(chunk_size=8192):
                data += chunk
                if len(data) > 5000:
                    print(f"  ✓ Image validated via GET: >{len(data)} bytes")
                    return True
            r.close()
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False

def create_topic(title, category='entertainment'):
    """Create a topic stub in p2_topics and return its ID."""
    topic_id = str(uuid.uuid4())
    payload = {
        'id': topic_id,
        'canonical_title': title[:200],
        'category': category,
        'status': 'published',
        'urgency': 'normal',
        'score_total': 5,
    }
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_topics",
        headers=HEADERS,
        json=payload,
        timeout=15
    )
    if r.status_code in (200, 201):
        print(f"  ✓ Topic created: {topic_id}")
        return topic_id
    else:
        print(f"  ⚠ Topic creation error: {r.status_code} — {r.text[:200]}")
        return topic_id  # might still work

def publish_article(article):
    """Insert article into Supabase."""
    body_text = article['body']
    word_count = len(body_text.split())
    payload = {
        'id': str(uuid.uuid4()),
        'headline': article['headline'],
        'subheadline': article['subheadline'],
        'body': body_text,
        'slug': article['slug'],
        'category': 'entertainment',
        'status': 'published',
        'published_at': datetime.now(timezone.utc).isoformat(),
        'image_url': article.get('image_url'),
        'image_caption': article.get('image_caption', ''),
        'image_attribution': article.get('image_attribution', ''),
        'word_count': word_count,
        'sources': json.dumps(article.get('sources_list', [])),
    }
    
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=payload,
        timeout=15
    )
    if r.status_code in (200, 201):
        result = r.json()
        art_id = result[0]['id'] if isinstance(result, list) else result.get('id', payload['id'])
        print(f"  ✓ Published: {article['headline'][:60]}... (id: {art_id})")
        return art_id
    else:
        print(f"  ✗ FAILED to publish: {r.status_code} — {r.text[:200]}")
        return None

# ============================================================
# ARTICLE 1: NTR 103rd Birth Anniversary
# ============================================================
print("\n=== ARTICLE 1: NTR 103rd Birth Anniversary ===")

ntr_image = fetch_wikipedia_person_image("N. T. Rama Rao")
if not ntr_image:
    ntr_image = fetch_wikipedia_person_image("N. T. Rama Rao (actor)")

if ntr_image and not validate_image(ntr_image):
    ntr_image = None

article1 = {
    'headline': "N.T. Rama Rao Was Born 103 Years Ago Today. PM Modi, Chiranjeevi, and Jr NTR All Stopped to Say So.",
    'subheadline': "The Telugu icon who became a Chief Minister, founded a political dynasty, and played Lord Krishna 17 times was honoured across India on May 28.",
    'slug': 'ntr-103rd-birth-anniversary-modi-chiranjeevi-jr-ntr-tribute-telugu-cinema-20260528',
    'image_url': ntr_image,
    'image_caption': 'N.T. Rama Rao, the Telugu cinema legend and former Andhra Pradesh Chief Minister',
    'image_attribution': 'Wikimedia Commons',
    'body': """N.T. Rama Rao was born on May 28, 1923, in Nimmakuru, a village in what is now Andhra Pradesh. He died in 1996. In between, he made over 300 films, played Hindu deities so convincingly that villagers reportedly prayed to his posters, served as Chief Minister three times, and founded the Telugu Desam Party — the political machine that still shapes Andhra politics today.

On Wednesday, exactly 103 years after his birth, India's political and cinematic establishment lined up to remember him.

## Modi, Chiranjeevi, and the Family

Prime Minister Narendra Modi posted a tribute calling NTR's contributions to cinema and governance "unparalleled." He specifically noted that NTR's welfare schemes — particularly subsidised rice at ₹2 per kilo, launched in the 1980s — established a model that subsequent governments across India would replicate.

Megastar Chiranjeevi, NTR's greatest rival in the Telugu film industry and now a political ally, shared a vintage photograph and wrote that NTR's "influence will never fade from history." The tribute was notable for its warmth — Chiranjeevi and NTR competed fiercely for Telugu audiences through the 1980s, and their political trajectories diverged sharply. For Chiranjeevi to publicly honour NTR's legacy signals how thoroughly the elder actor's reputation has transcended faction.

Jr NTR — NTR's grandson, now one of Indian cinema's biggest global stars after RRR — visited NTR Ghat in Hyderabad with family members. His social media post was brief and emotional, avoiding the political framing that surrounded other tributes.

## The Legacy in Numbers

NTR won three National Film Awards and a Rashtrapati Award. He played Lord Krishna in 17 films and Lord Rama in multiple others, earning the title *Nataratna* (Jewel of Acting). His 1957 film *Mayabazar* is still regularly cited as one of the greatest Indian films ever made.

But his political legacy may be larger. The Telugu Desam Party, which he founded in 1982 to challenge the Congress monopoly in Andhra Pradesh, won its first election within nine months — one of the fastest party-to-power transitions in Indian democratic history. The TDP remains a major force in Andhra Pradesh under his grandson-in-law, Chief Minister N. Chandrababu Naidu.

## Why This Matters to the Diaspora

For Telugu NRIs, NTR is not a historical figure in the way other mid-century Indian actors are. He is a living cultural reference. Telugu associations in the US, UK, and the Gulf regularly screen his mythological films during festivals. The NTR National Award, established in his honour, has been given to Chiranjeevi, Kamal Haasan, and other figures who bridge cinema and public life.

Jr NTR's global stardom — RRR played in over 1,000 screens in North America alone — has introduced a new generation of international audiences to the family name. But for older diaspora audiences, the grandson is simply carrying forward something that started in a village in coastal Andhra a century ago.

## What's Next

The demand for NTR to receive the Bharat Ratna, India's highest civilian honour, has intensified in recent years. Chiranjeevi has publicly backed the campaign. With the BJP-TDP alliance currently governing Andhra Pradesh, the political alignment for such an honour has arguably never been stronger.

Whether or not the award comes, the annual ritual of May 28 tributes shows no sign of fading. In Hyderabad, at NTR Ghat, the flowers were fresh again this morning.

*Sources: PM Modi's official tribute, Chiranjeevi's social media post, IndiaPost, BizzBuzz News, The Popular Story*"""
}

art1_id = publish_article(article1)

# ============================================================
# ARTICLE 2: Dhinchak Pooja Gets Married
# ============================================================
print("\n=== ARTICLE 2: Dhinchak Pooja Wedding ===")

pooja_image = fetch_wikipedia_person_image("Dhinchak Pooja")
if not pooja_image or not validate_image(pooja_image):
    # She's an internet personality, try Pexels for Indian wedding
    pooja_image = fetch_pexels_image("Indian wedding bride ceremony", "Indian bridal mehendi celebration")
    if pooja_image and not validate_image(pooja_image):
        pooja_image = None

article2 = {
    'headline': "The Internet's Most Trolled Singer Just Got Married. She Hid the Groom's Face. Fans Want a Wedding Song.",
    'subheadline': "Dhinchak Pooja — whose 'Selfie Maine Leli Aaj' defined a generation of cringe-pop — shared bridal photos on Instagram. The internet responded exactly how you'd expect.",
    'slug': 'dhinchak-pooja-married-wedding-selfie-maine-leli-aaj-singer-groom-hidden-viral-20260528',
    'image_url': pooja_image,
    'image_caption': 'Dhinchak Pooja shared wedding photos on Instagram, keeping her husband\'s identity hidden',
    'image_attribution': 'Pexels' if pooja_image and 'pexels' in (pooja_image or '') else 'Wikimedia Commons',
    'body': """Dhinchak Pooja got married. The internet's most polarising singer — the woman who uploaded "Selfie Maine Leli Aaj" in 2017 and accidentally invented an entire genre of cringe-pop — shared her wedding photos and clips on Instagram on Wednesday, and the reaction has been exactly what you'd expect: chaotic, affectionate, and deeply meme-driven.

## What We Know

Pooja, whose real name is Pooja Jain, posted images from what appear to be her sangeet, mehendi, haldi, and wedding ceremonies. She wore a pink bridal look. She did not reveal the groom's name. She did not show his face. The clips are edited in her signature style — slightly off-beat, oddly sincere, and impossible to look away from.

Her 788,000 Instagram followers immediately began doing what Dhinchak Pooja fans have always done: oscillating between genuine congratulations and requests for content.

"Where is the wedding song?" was the most common comment. "Selfie Maine Leli Aaj — shaadi edition" trended within hours.

## The Unlikely Cultural Legacy

It is easy to dismiss Dhinchak Pooja. Millions of people have, loudly and repeatedly, since she first appeared on YouTube nearly a decade ago. Her songs — "Selfie Maine Leli Aaj," "Dilon Ka Shooter," "Baapu Dede Thoda Cash" — violated every conventional standard of pitch, production, and musical competence. They were also unstoppable. "Selfie Maine Leli Aaj" crossed 40 million views before YouTube took it down for spam reports. It was re-uploaded. It kept spreading.

What Pooja understood, perhaps before the Indian internet fully grasped it, was that virality does not require quality. It requires memorability. Her songs burrowed into the national consciousness not despite their flaws but because of them. She appeared on Bigg Boss 11. She became a meme template. She outlasted dozens of "real" artists who debuted in the same era.

For the Indian diaspora, Dhinchak Pooja occupies a specific cultural niche: she is the reference that every NRI cousin understands. At desi parties from Edison to Fremont, someone has played "Dilon Ka Shooter" ironically. That ironic play has outlasted most of the year's Bollywood soundtrack.

## The Groom Mystery

The deliberate decision to hide the groom's face is either savvy content strategy or genuine privacy — and with Dhinchak Pooja, the line between the two has always been blurry. Several fan accounts and news outlets are now speculating about the identity, comparing hand jewellery and clothing in different photos. This is precisely the kind of internet detective work that Pooja's career has always generated.

MensXP and several other outlets raised the question of whether the entire thing might be a music video rather than a real wedding, citing Pooja's history of blurring the line between personal content and performance. As of Wednesday evening, she has not clarified.

## What's Next

If history is any guide, a Dhinchak Pooja wedding song is coming. The demand is already there. The audience is already primed. And if there is one thing Pooja Jain has proven over the past nine years, it is that she will always give the internet exactly what it asks for — just not in the way anyone expects.

The comments section under her post is, as always, a masterpiece of contradictions: "Queen 👑," "Please no wedding song 🙏," "Where is the song??? 😭," and "This woman is more consistent than half of Bollywood."

She is. And now she's married.

*Sources: LiveMint, MensXP, Inshorts, SaptashwaTV, News Jobaaj*"""
}

art2_id = publish_article(article2)

# ============================================================
# ARTICLE 3: Raja Shivaji Breaks Sairat's Record
# ============================================================
print("\n=== ARTICLE 3: Raja Shivaji ===")

riteish_image = fetch_wikipedia_person_image("Riteish Deshmukh")
if not riteish_image or not validate_image(riteish_image):
    riteish_image = fetch_pexels_image("Shivaji Maharaj statue monument", "Marathi cinema historical")
    if riteish_image and not validate_image(riteish_image):
        riteish_image = None

article3 = {
    'headline': "A Marathi Film Just Broke a Record That Stood for Ten Years. Riteish Deshmukh Directed It.",
    'subheadline': "Raja Shivaji crossed ₹114 crore worldwide in 26 days, surpassing Sairat's ₹110 crore lifetime. While Bollywood's May flopped, Marathi cinema made history.",
    'slug': 'raja-shivaji-highest-grossing-marathi-film-sairat-record-riteish-deshmukh-114-crore-20260528',
    'image_url': riteish_image,
    'image_caption': 'Riteish Deshmukh, who directed and starred in Raja Shivaji',
    'image_attribution': 'Wikimedia Commons',
    'body': """For ten years, Sairat held the record. Nagraj Manjule's 2016 love story about caste and consequence earned ₹110 crore worldwide and became the film that proved Marathi cinema could play in the big leagues. No Marathi film had come close since.

Raja Shivaji just passed it. In 26 days.

Riteish Deshmukh's directorial debut — a historical epic about Chhatrapati Shivaji Maharaj's rise to power — has crossed ₹114 crore worldwide as of May 27, with ₹109.8 crore in India alone across 87,098 shows. It is now the highest-grossing Marathi film of all time.

## The Numbers Tell a Story

The breakdown is revealing. The Marathi version — the film's primary audience — contributed ₹67.4 crore net from 38,130 shows, maintaining an average occupancy of 33.8%. The Hindi version added ₹24.65 crore from a much wider spread of 47,296 shows, at 13.4% occupancy.

What this means: Marathi audiences showed up in force and kept showing up. The Hindi crossover extended the film's reach but wasn't the primary driver. This is a Marathi film that won on Marathi terms, in Marathi theatres, with Marathi-speaking audiences — and then happened to find Hindi audiences too.

On its opening day, Raja Shivaji earned ₹13.5 crore. By day three, it had hit ₹14.3 crore in a single day. It crossed ₹50 crore in five days. It hit ₹100 crore on day 17. The holds were remarkable — a 53% drop from week two to week three is strong for any Indian film, exceptional for a Marathi one.

## Why Riteish Deshmukh Matters

Riteish Deshmukh is best known to Bollywood audiences as a comic actor — the guy from Housefull, the charmer from Grand Masti, the sidekick in a dozen ensemble comedies. But he is also Vilasrao Deshmukh's son — the late Chief Minister of Maharashtra — and his Marathi identity has always run deeper than his Bollywood filmography suggests.

His decision to direct a film about Shivaji Maharaj, the foundational figure of Marathi identity and pride, was not casual. It was a statement about where his creative ambitions actually live. That the film also features Abhishek Bachchan — for whom Raja Shivaji has become his sixth highest-grossing film — speaks to the scale Deshmukh was aiming for. But the heart of the film is Marathi.

## Bollywood's Worst May vs. Marathi's Best

The timing makes this story sharper. May 2026 has been brutal for Bollywood. Pati Patni Aur Woh Do managed ₹53.85 crore worldwide — underwhelming for a sequel with name recognition. Chand Mera Dil, Karan Johar's romantic drama, scraped ₹21 crore in five days. The two biggest Hindi releases of the month collectively earned less than one Marathi film about a 17th-century warrior king.

Meanwhile, Marathi cinema produced not one but two hits. Deool Band 2, a devotional comedy-drama directed by Pravin Tarde, opened to ₹2.45 crore, grew through word of mouth, and hit ₹26.5 crore in six days. With a budget estimated at ₹8-10 crore, it's marching toward blockbuster status. It became the second-highest Marathi opener of 2026, behind only Raja Shivaji.

## The Diaspora Connection

For Maharashtrian NRIs, Shivaji Maharaj is not a historical figure — he is a living cultural reference, invoked at every Marathi community gathering from New Jersey to the Bay Area. The film's overseas collection of ₹4.18 crore is modest compared to Telugu or Tamil blockbusters, but for a Marathi film, it represents unprecedented international interest.

Sairat's record-breaking run in 2016 coincided with a surge in Marathi cultural pride among diaspora communities. Raja Shivaji's success may accelerate that trend. When a Marathi film about the community's most revered historical figure becomes the industry's biggest hit ever, it sends a signal: there is a global Marathi audience willing to show up in theatres.

## What Comes Next

The trade is now watching whether Raja Shivaji can sustain its run long enough to push past ₹120-130 crore before its digital premiere. More importantly, it is watching whether this success — combined with Deool Band 2's strong performance — signals a structural shift in Marathi cinema's commercial ceiling.

For a decade, Sairat's ₹110 crore stood as both a record and a ceiling. Raja Shivaji has broken through it. The question now is whether other Marathi filmmakers will follow Riteish Deshmukh through the door he just opened.

*Sources: Sacnilk box office data, Pinkvilla, Koimoi, ZoomTV Entertainment*"""
}

art3_id = publish_article(article3)

# Summary
print("\n=== BATCH COMPLETE ===")
print(f"Published: {sum(1 for x in [art1_id, art2_id, art3_id] if x)}/3 articles")
for label, aid in [("NTR Anniversary", art1_id), ("Dhinchak Pooja", art2_id), ("Raja Shivaji", art3_id)]:
    print(f"  {'✓' if aid else '✗'} {label}: {aid or 'FAILED'}")
