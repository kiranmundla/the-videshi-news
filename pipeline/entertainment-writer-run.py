#!/usr/bin/env python3
"""Entertainment writer for The Videshi — 2026-05-30 evening run."""

import json, os, re, sys, time, uuid, requests, urllib.parse
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
load_env(os.path.expanduser('~/workspace/.env.supabase'))
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

def sb_insert(table, data):
    r = requests.post(f"{SUPABASE_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    if r.status_code in (200, 201):
        return r.json()
    print(f"  ✗ Insert error ({r.status_code}): {r.text[:400]}")
    return None

def sb_patch(table, match, data):
    params = '&'.join(f"{k}={v}" for k, v in match.items())
    r = requests.patch(f"{SUPABASE_URL}/rest/v1/{table}?{params}", headers=HEADERS, json=data, timeout=30)
    if r.status_code in (200, 204):
        return True
    print(f"  ✗ Patch error ({r.status_code}): {r.text[:300]}")
    return False

def fetch_wikipedia_person_image(person_name):
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
    import subprocess
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
                 f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape'],
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
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        content_type = r.headers.get('Content-Type', '')
        content_length = int(r.headers.get('Content-Length', 0))
        if 'image' in content_type and content_length > 5000:
            print(f"  ✓ Image validated: {content_type}, {content_length} bytes")
            return True
        print(f"  ✗ Image invalid: type={content_type}, size={content_length}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False

def is_banned_url(url):
    if not url:
        return True
    banned = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com', '_nc_ht=', '_nc_cat=', 'ccb=']
    return any(b in url for b in banned)

def create_topic(title, category='entertainment'):
    topic_id = str(uuid.uuid4())
    topic = {
        'id': topic_id,
        'canonical_title': title,
        'vertical': 'culture',
        'urgency': 'daily',
        'score_diaspora': 75,
        'score_significance': 70,
        'score_recency': 80,
        'score_source_avail': 80,
        'score_total': 76,
        'signal_count': 1,
        'status': 'published',
        'keywords': [],
        'category': category,
    }
    result = sb_insert('p2_topics', topic)
    if result:
        print(f"  ✓ Topic created: {topic_id}")
        return topic_id
    return None

def publish_article(article, topic_id):
    article_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    word_count = len(article['body'].split())
    
    record = {
        'id': article_id,
        'topic_id': topic_id,
        'headline': article['headline'],
        'subheadline': article['subheadline'],
        'body': article['body'],
        'slug': article['slug'],
        'category': 'entertainment',
        'status': 'published',
        'published_at': now,
        'sources': json.dumps(article.get('sources', [])),
        'image_url': article.get('image_url'),
        'image_attribution': article.get('image_attribution', ''),
        'diaspora_angle': article.get('diaspora_angle', ''),
        'vertical': 'culture',
        'tags': article.get('tags', []),
        'urgency': 'daily',
        'word_count': word_count,
        'is_featured': False,
        'is_editorial': False,
    }
    
    result = sb_insert('p2_articles', record)
    if result:
        print(f"  ✓ Published: {article['headline'][:60]}... (id: {article_id})")
        return article_id
    return None

# ──────────────────────────────────────────────────────────────
# ARTICLE 1: Deli Boys Season 2
# ──────────────────────────────────────────────────────────────
article1 = {
    'headline': "Deli Boys Season 2 Just Dropped on Hulu. It's the Funniest South Asian Show on American Television.",
    'subheadline': "Kumail Nanjiani, Lilly Singh, and Fred Armisen join Asif Ali and Saagar Shaikh for a second season that's sharper, darker, and more Pakistani than ever.",
    'slug': 'deli-boys-season-2-hulu-kumail-nanjiani-south-asian-comedy-nri-20260530',
    'diaspora_angle': 'A mainstream American comedy with an all-South Asian lead cast tells a Pakistani-American crime story without explaining itself to a white audience — a milestone for diaspora representation.',
    'tags': ['Deli Boys', 'Hulu', 'Kumail Nanjiani', 'Asif Ali', 'Saagar Shaikh', 'Poorna Jagannathan', 'South Asian representation', 'Pakistani-American'],
    'sources': [
        'Decider - Stream It Or Skip It review',
        'People Magazine - Poorna Jagannathan interview',
        'Rotten Tomatoes - Season 1 96% score',
        'Wikipedia - Deli Boys production details'
    ],
    'body': """If you haven't been watching *Deli Boys*, you're missing what might be the sharpest South Asian comedy on American television right now. Season 2 of the Hulu crime comedy dropped on May 28, and it picks up exactly where the first season's madness left off — with the Dar brothers drowning in drug money and absolutely no idea what to do with it.

Created by Abdullah Saeed and produced by Disney's Onyx Collective, *Deli Boys* follows Mir and Raj Dar — played by **Asif Ali** and **Saagar Shaikh** — two Pakistani-American brothers in Philadelphia who inherited their late father's convenience store empire, only to discover it was a front for an elaborate criminal operation. Season 1 earned a remarkable 96% on Rotten Tomatoes, and the sophomore outing doubles down on everything that made the original work: the chaotic family dynamics, the absurdist crime plotting, and the very specific texture of desi immigrant life in America.

## New Faces, Bigger Stakes

The new season introduces **Fred Armisen** as Max Sugar, a casino owner who becomes the Dars' money-laundering partner — and, complicating matters considerably, **Poorna Jagannathan**'s Auntie Lucky's new love interest. **Kumail Nanjiani** plays Danyal, a scrappy and corrupt lawyer hired by Sugar, and by all accounts, he's having the time of his life. In a recent interview, Jagannathan recalled Nanjiani saying on set: "I cannot believe I am cursing so much in Urdu. This is the first set I've ever used so much of my own language."

That detail tells you everything about why *Deli Boys* matters. This isn't a show that uses South Asian identity as window dressing — the Urdu, the family dynamics, the specific textures of running a Pakistani-American business are baked into the comedy's DNA. **Lilly Singh** joins as Aisha, and **Andrew Rannells** plays an ambitious district attorney, while **Tan France** returns as Zubair, the stylish and terrifying British-Pakistani crime lord from South London.

## Why the Diaspora Should Be Paying Attention

For Indian and Pakistani diaspora audiences in America, *Deli Boys* represents something that was genuinely rare even five years ago: a mainstream American comedy where South Asian characters are the protagonists, the villains, the love interests, and the comic relief — all at once. The show doesn't explain itself to a white audience. It doesn't pause to translate. It just trusts that the story is universal enough to work, and it is.

The crime comedy sits in a lineage with shows like *The Brothers Sun* and *Atlanta* — ensemble comedies that use the crime genre to explore specific immigrant experiences with real affection and zero apology. Jagannathan, who also played the fierce mother in *Never Have I Ever*, brings a different energy here: menopausal, armed, and completely out of patience with incompetent men. "There's a mental switch that happens," she told People Magazine about playing Lucky. "Screaming at men just comes so much more naturally."

## The Representation Math

The numbers matter too. *Deli Boys* is produced by Onyx Collective — Disney's content brand focused on creators of colour — and airs on Hulu, which means it's available on Disney+ internationally. The show proves there's a viable audience for South Asian stories that don't sand down their edges for mainstream palatability. With Nanjiani's star power added to the mix (he's fresh off a Broadway run in *Oh, Mary!*), the show has both critical credibility and commercial muscle.

Season 2 is available now on Hulu, with all episodes dropping at once. If you've been waiting for a show that gets the desi-American experience right — the family pressure, the code-switching, the absurdity of building a life between two worlds — this is it. Bring snacks. Preferably from the deli.""",
}

# ──────────────────────────────────────────────────────────────
# ARTICLE 2: Kangana Ranaut's 26/11 Film
# ──────────────────────────────────────────────────────────────
article2 = {
    'headline': "Kangana Ranaut Is Playing a Nurse Who Saved 400 Lives During 26/11. Bharat Bhhagya Viddhaata Opens June 12.",
    'subheadline': "The film tells the untold story of hospital workers at Mumbai's Cama Hospital during the 2008 terror attacks — a chapter that mainstream cinema has largely ignored.",
    'slug': 'kangana-ranaut-bharat-bhhagya-viddhaata-2611-cama-hospital-june-12-nri-20260530',
    'diaspora_angle': 'For NRI audiences, 26/11 remains deeply personal — many diaspora families had relatives in Mumbai that night. A film centring working-class heroes offers something new beyond the commando narratives.',
    'tags': ['Kangana Ranaut', 'Bharat Bhhagya Viddhaata', '26/11', 'Mumbai terror attacks', 'Cama Hospital', 'Girija Oak', 'Manoj Tapadia'],
    'sources': [
        'Sacnilk - Bharat Bhhagya Viddhaata release details',
        'News365 Times - Kangana Ranaut promotional interview',
        'Newspointapp - First look poster details',
        'Koimoi - Production and cast details'
    ],
    'body': """On June 12, a film will open in Indian theatres that tells a story most people have never heard — even those who lived through it. **Bharat Bhhagya Viddhaata** stars Kangana Ranaut as a nurse at Mumbai's Cama and Albless Hospital during the November 26, 2008 terror attacks, and its focus isn't on the commandos, the politicians, or the hostage drama at the Taj. It's about the hospital staff who saved nearly 400 lives while the city burned around them.

The film is directed by **Manoj Tapadia** in his directorial debut, and it co-stars Marathi actresses **Girija Oak** (*Jawan*, *Qala*), Smita Tambe, and Amrutha Namdev. From the motion poster — which shows Ranaut in a nurse's uniform, walking through fire with a bruised, bloodied face — the tone is clear: this is not a flag-waving action spectacle. It's a survival drama about ordinary people placed in extraordinary circumstances.

## The Untold Chapter of 26/11

Most 26/11 films have understandably focused on the Taj Mahal Palace Hotel siege, the Nariman House tragedy, or the NSG commando operations. But Cama Hospital, located barely 500 metres from the Chhatrapati Shivaji Terminus where the attacks began, has remained a largely untold chapter. When terrorists Ajmal Kasab and Abu Ismail entered the hospital grounds, it was the staff — nurses, ward attendants, cleaners, security guards, lift operators — who barricaded patients, hid them in darkened wards, and kept hundreds alive through the night.

The film explores what happened inside those walls: the improvisation, the fear, the quiet heroism of people whose training was in healing, not combat. In a promotional video, Ranaut asks viewers to imagine a day without nurses, sanitation workers, emergency responders — the people she calls "the real Bharat Bhhagya Viddhaata."

## Kangana's Complicated Comeback

For Ranaut, this film arrives at a precarious moment. Her recent track record at the box office has been brutal: *Emergency*, *Tejas*, *Chandramukhi 2*, and *Dhaakad* all underperformed significantly. Her last genuine commercial hit was *Manikarnika: The Queen of Jhansi* in 2019 — seven years ago. The shift from action-driven vehicles to a grounded ensemble drama about healthcare workers might be exactly the reset her career needs, or it might be too subtle for the box office arithmetic that currently favours spectacle.

What works in the film's favour is timing and subject matter. With *Queen 2* (directed by Vikas Bahl) also in her pipeline, Ranaut appears to be pivoting toward stories that play to her National Award-winning dramatic strengths rather than her more divisive public persona.

## The Diaspora Angle

For NRI audiences, 26/11 occupies a specific place in collective memory. Many diaspora families have relatives who were in Mumbai that night, and the attacks fundamentally reshaped how the Indian community abroad thought about security, terrorism, and the vulnerability of the city many still call home. A film that centres the working-class heroes of that night — not the commandos, not the politicians — offers something genuinely new.

The film opens June 12 and will face competition from Imtiaz Ali's *Main Vaapas Aaunga*, Manoj Bajpayee's *Governor: The Silent Saviour*, and Vikram Bhatt's *Haunted 3D: Echoes of the Past*. Whether Ranaut can translate this powerful subject matter into box office numbers remains to be seen. But the story deserves to be told, regardless of who's telling it.

*Bharat Bhhagya Viddhaata releases theatrically on June 12, 2026.*""",
}

# ──────────────────────────────────────────────────────────────
# ARTICLE 3: Dhurandhar 2 OTT Release Guide
# ──────────────────────────────────────────────────────────────
article3 = {
    'headline': "Dhurandhar 2 Hits JioHotstar on June 4 With an Extended Cut. Here's What the Diaspora Needs to Know.",
    'subheadline': "The ₹1,800-crore blockbuster gets a 'Raw and Undekha' version with restored scenes, a behind-the-scenes premiere event, and a dual-platform release strategy.",
    'slug': 'dhurandhar-2-ott-release-jiohotstar-netflix-june-4-extended-cut-diaspora-nri-20260530',
    'diaspora_angle': 'A practical streaming guide for NRI viewers: where Dhurandhar 2 is available by region, which version to watch, and how the unprecedented dual-platform release works.',
    'tags': ['Dhurandhar 2', 'JioHotstar', 'Netflix', 'OTT release', 'Ranveer Singh', 'Aditya Dhar', 'streaming'],
    'sources': [
        'Livemint - Dhurandhar 2 OTT release details',
        'Sacnilk - JioHotstar and Netflix dual release strategy',
        'MensXP - June 2026 OTT releases roundup',
        'The Popular Story - Box office collection tracking'
    ],
    'body': """The wait is almost over. **Dhurandhar 2: The Revenge** — the ₹1,800-crore blockbuster that became the second-highest-grossing Indian film of all time — officially arrives on JioHotstar on **June 4** with an extended "Raw & Undekha" cut that restores scenes, extends action sequences, and includes footage that never made it to theatres.

For diaspora audiences who either missed the theatrical run or want to revisit Aditya Dhar's spy action epic, here's everything you need to know about how, when, and where to watch.

## The Release Plan

JioHotstar is rolling out a grand digital premiere on **June 4 at 7:00 PM IST** (9:30 AM ET / 6:30 AM PT). The premiere kicks off with an exclusive 30-minute pre-show featuring candid cast conversations, behind-the-scenes stories, and production insights. Regular subscribers get access from **June 5** onwards.

But here's where it gets interesting: Dhurandhar 2 will also arrive on **Netflix India on June 19** — two weeks after the JioHotstar premiere. This staggered dual-platform strategy is unprecedented for an Indian blockbuster and reflects the film's extraordinary commercial position. The international Netflix release has already been live since May 14, so diaspora viewers in the US, UK, and Canada with Netflix subscriptions may already have access to the standard cut.

## What's Different in the Extended Cut

The "Raw & Undekha" version is not just a marketing rebrand. Multiple reports confirm that the theatrical release had sequences trimmed and dialogues toned down — partly for runtime, partly for the CBFC (India's censor board). The extended cut restores these moments, presenting the film in what director Aditya Dhar has described as its intended form: grittier, longer, and more unflinching.

If you watched the original Dhurandhar's "Raw & Undekha" version (which dropped on both Netflix and JioHotstar on May 22), you'll know the drill. That extended cut of the first film restored several sequences that viewers had noticed were missing from the OTT version compared to their theatrical experience.

## The Numbers Behind the Phenomenon

Dhurandhar 2 has been nothing short of a cultural event. In its 10-week theatrical run, the film starring **Ranveer Singh**, **R. Madhavan**, **Sanjay Dutt**, and **Arjun Rampal** has grossed approximately ₹1,148 crore domestically and ₹1,800 crore worldwide, making it the second biggest Indian film ever — trailing only *Baahubali 2*. Even in its 10th week, it was still earning ₹5 lakh daily, a testament to the film's sustained cultural hold.

The spy action thriller follows the volatile rise of Hamza Ali Mazari in the underworld of Lyari, and Dhar's direction brought a level of scale and intensity that audiences — both in India and abroad — responded to viscerally.

## What Diaspora Viewers Should Do

**If you're in the US, UK, or Canada**: Check Netflix first. The international version has been streaming since mid-May. The June 4 JioHotstar premiere is specifically for the Indian market, though JioHotstar's international availability varies by region.

**If you want the extended cut**: The "Raw & Undekha" version on JioHotstar (June 4-5) is the definitive version. If you're in a market where JioHotstar is available, that's the one to watch.

**If you're patient**: Netflix India gets it on June 19. International Netflix may also receive the extended cut, though this hasn't been confirmed yet.

## Also Streaming in June

The Dhurandhar 2 premiere isn't the only reason to log in during the first week of June. **Maa Behen** — the dark comedy starring Madhuri Dixit and Triptii Dimri — drops on Netflix on June 4. **Made in India: A Titan Story**, starring Naseeruddin Shah as JRD Tata, arrives on Amazon Prime Video on June 3. And **Gullak Season 5** — India's most quietly beloved family dramedy — hits SonyLIV on June 5.

It's a stacked week. Clear your schedule.

*Dhurandhar 2: The Revenge streams on JioHotstar from June 4, 2026, and Netflix India from June 19, 2026.*""",
}

# ──────────────────────────────────────────────────────────────
# Main execution
# ──────────────────────────────────────────────────────────────
articles = [article1, article2, article3]

print("=" * 60)
print(f"Entertainment Writer — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print(f"Articles to publish: {len(articles)}")
print("=" * 60)

for i, article in enumerate(articles, 1):
    print(f"\n--- Article {i}: {article['headline'][:60]}... ---")
    
    # Validate article quality
    word_count = len(article['body'].split())
    print(f"  Word count: {word_count}")
    if word_count < 400:
        print(f"  ✗ SKIPPED: Body too short ({word_count} words)")
        continue
    if len(article['headline']) > 200:
        print(f"  ✗ SKIPPED: Headline too long ({len(article['headline'])} chars)")
        continue
    if len(article.get('subheadline', '')) < 15:
        print(f"  ✗ SKIPPED: Subheadline too short")
        continue
    
    # Create topic first
    topic_id = create_topic(article['headline'])
    if not topic_id:
        print(f"  ✗ SKIPPED: Could not create topic")
        continue
    
    # Image sourcing
    img_url = None
    img_attr = ''
    
    if i == 1:
        # Deli Boys — try key cast members
        for person in ['Kumail Nanjiani', 'Asif Ali (actor, born 1990)', 'Poorna Jagannathan']:
            img_url = fetch_wikipedia_person_image(person)
            if img_url and not is_banned_url(img_url):
                img_attr = 'Wikimedia Commons'
                break
        if not img_url:
            img_url = fetch_pexels_image("convenience store neon sign night", "Philadelphia storefront")
            img_attr = 'Pexels'
    
    elif i == 2:
        # Kangana Ranaut
        img_url = fetch_wikipedia_person_image('Kangana Ranaut')
        img_attr = 'Wikimedia Commons'
        if not img_url:
            img_url = fetch_pexels_image("nurse hospital India", "hospital corridor")
            img_attr = 'Pexels'
    
    elif i == 3:
        # Ranveer Singh
        img_url = fetch_wikipedia_person_image('Ranveer Singh')
        img_attr = 'Wikimedia Commons'
        if not img_url:
            img_url = fetch_pexels_image("movie theater India", "cinema hall")
            img_attr = 'Pexels'
    
    # Validate image
    if img_url and not is_banned_url(img_url) and validate_image(img_url):
        article['image_url'] = img_url
        article['image_attribution'] = img_attr
        print(f"  ✓ Image set: {img_attr}")
    else:
        print(f"  ⚠ No valid image found — publishing without image")
        article['image_url'] = None
        article['image_attribution'] = ''
    
    # Publish
    art_id = publish_article(article, topic_id)
    if art_id:
        print(f"  ✓ Article {i} published successfully")
    else:
        print(f"  ✗ Article {i} failed to publish")
    
    time.sleep(1)

print("\n" + "=" * 60)
print("Entertainment writer run complete.")
print("=" * 60)
