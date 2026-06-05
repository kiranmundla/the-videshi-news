#!/usr/bin/env python3
"""Entertainment writer for The Videshi — 2026-06-05 batch"""

import json, os, sys, time, re, urllib.parse, uuid
from datetime import datetime, timezone

import requests

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())

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

UA = 'TheVideshi/1.0 (thevideshi.com)'


# ── Image sourcing ──────────────────────────────────────────────

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f'https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}',
            headers={'User-Agent': UA}, timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get('originalimage', {}).get('source') or data.get('thumbnail', {}).get('source')
            if img:
                print(f'  ✓ Wikipedia image for "{person_name}": {img[:80]}...')
                return img
    except Exception as e:
        print(f'  ⚠ Wikipedia error for "{person_name}": {e}')
    return None


def fetch_wikimedia_commons(query, limit=5):
    """Search Wikimedia Commons for CC-licensed images."""
    try:
        r = requests.get(
            'https://commons.wikimedia.org/w/api.php',
            params={
                'action': 'query', 'generator': 'search',
                'gsrsearch': query, 'gsrnamespace': '6', 'gsrlimit': str(limit),
                'prop': 'imageinfo', 'iiprop': 'url|size|mime',
                'iiurlwidth': '1200', 'format': 'json'
            },
            headers={'User-Agent': UA}, timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get('query', {}).get('pages', {})
            results = []
            for pid, page in pages.items():
                ii = page.get('imageinfo', [{}])[0]
                url = ii.get('thumburl') or ii.get('url')
                mime = ii.get('mime', '')
                if url and 'image' in mime:
                    results.append({'url': url, 'title': page.get('title', ''), 'width': ii.get('width', 0)})
            if results:
                print(f'  ✓ Commons found {len(results)} images for "{query}"')
            return results
    except Exception as e:
        print(f'  ⚠ Commons error for "{query}": {e}')
    return []


def fetch_pexels(query):
    """Search Pexels for a relevant image."""
    if not PEXELS_KEY:
        return None
    try:
        r = requests.get(
            'https://api.pexels.com/v1/search',
            params={'query': query, 'per_page': 5, 'orientation': 'landscape'},
            headers={'Authorization': PEXELS_KEY},
            timeout=10
        )
        if r.status_code == 200:
            photos = r.json().get('photos', [])
            for p in photos:
                url = p.get('src', {}).get('large2x') or p.get('src', {}).get('original')
                if url:
                    print(f'  ✓ Pexels image: {url[:80]}...')
                    return url
    except Exception as e:
        print(f'  ⚠ Pexels error: {e}')
    return None


def validate_image(url):
    """Validate an image URL returns 200 with image content > 5KB."""
    try:
        r = requests.head(url, headers={'User-Agent': UA}, timeout=10, allow_redirects=True)
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct and cl > 5000:
            return True
        # Try GET if HEAD doesn't give content-length
        if r.status_code == 200 and 'image' in ct and cl == 0:
            r2 = requests.get(url, headers={'User-Agent': UA}, timeout=10, stream=True)
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                return True
    except Exception as e:
        print(f'  ⚠ Image validation failed: {e}')
    return False


def find_best_image(person_name=None, commons_query=None, pexels_query=None):
    """Multi-source image search: Wikipedia → Commons → Pexels."""
    candidates = []

    # Wikipedia person image
    if person_name:
        wp = fetch_wikipedia_person_image(person_name)
        if wp and validate_image(wp):
            candidates.append(('wikipedia', wp))

    # Wikimedia Commons
    if commons_query:
        commons = fetch_wikimedia_commons(commons_query)
        for c in commons[:3]:
            if validate_image(c['url']):
                candidates.append(('commons', c['url']))
                break

    # Pexels fallback
    if pexels_query:
        px = fetch_pexels(pexels_query)
        if px and validate_image(px):
            candidates.append(('pexels', px))

    # Pick best: Wikipedia person > Commons specific > Pexels
    for source, url in candidates:
        attr = 'Wikimedia Commons' if source in ('wikipedia', 'commons') else 'Pexels'
        return url, attr

    return None, None


# ── Article insertion ───────────────────────────────────────────

def insert_article(article):
    """Insert an article into Supabase."""
    r = requests.post(
        f'{SUPABASE_URL}/rest/v1/p2_articles',
        headers=HEADERS,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        aid = data[0]['id'] if isinstance(data, list) and data else 'unknown'
        print(f'  ✅ Published: "{article["headline"]}" (id: {aid})')
        return True
    else:
        print(f'  ❌ Insert failed ({r.status_code}): {r.text[:200]}')
        return False


# ── Articles ────────────────────────────────────────────────────

def article_preity_zinta_jacarti():
    """Preity Zinta launches Jacarti luxury jewellery brand."""
    print('\n📝 Article 1: Preity Zinta — Jacarti Jewellery')

    img_url, img_attr = find_best_image(
        person_name='Preity Zinta',
        commons_query='Preity Zinta',
        pexels_query='luxury Indian polki jewellery'
    )

    if not img_url:
        print('  ⚠ No valid image found, skipping article')
        return False

    headline = "Preity Zinta Just Launched a Luxury Jewellery Brand. It Is Not What You Would Expect from a Bollywood Star."
    subheadline = "Jacarti Jewellery reimagines heritage Polki as modern heirloom pieces, backed by a co-founder from Dubai's Timeless Group and the Arvind Mafatlal family."

    body = """Preity Zinta has spent two decades in Bollywood, owned an IPL franchise, and built a life between Los Angeles and Mumbai. On June 4, she added a new line to that resume: fine jewellery entrepreneur.

Jacarti Jewellery, co-founded by Zinta alongside Samara Punjabi of the Dubai-based Timeless Group and Priyavrata Mafatlal, Vice-Chairman of the Arvind Mafatlal Group, launched with a flagship store in Bandra, Mumbai, and an e-commerce platform at jacarti.com. The brand specialises in Polki jewellery — uncut diamond pieces set in gold — but with a design language that leans contemporary rather than bridal.

## A Brand Built on Three Continents

What makes Jacarti unusual is its founding team. Zinta brings celebrity reach and a dual life between India and the United States. Punjabi brings luxury retail experience from the UAE, where Timeless Group has built a significant presence. Mafatlal brings industrial heritage and capital from one of India's oldest business families. The combination is deliberate: a jewellery brand with roots in Indian craft, Gulf-market luxury sensibility, and global distribution ambitions.

The launch event in Bandra drew a mix of industry friends and business partners. Celina Jaitly, Bobby Deol, and Iulia Vantur were among those present. Jaitly called the collection "absolutely phenomenal" and posted what she described as the "mother of all selfies" from the evening.

## Polki, Reimagined

Jacarti's signature line is called 'Merai,' a collection that reinterprets traditional Polki techniques for a younger, globally mobile buyer. The brand positions its pieces as "contemporary heritage heirlooms" — jewellery meant to be passed across generations but designed for everyday luxury rather than locked in a vault between weddings.

The timing is strategic. India's luxury jewellery market is expanding rapidly, driven by a new generation of buyers who want provenance and craftsmanship but not the aesthetic of their grandmother's wedding set. NRI buyers, particularly in the Gulf, UK, and North America, have become a significant driver of high-end Indian jewellery sales, often purchasing during trips home or through online platforms.

## The Diaspora Connection

For NRIs watching from abroad, the launch taps into a familiar tension. Indian fine jewellery has always carried cultural weight — it is gifted at weddings, passed between mothers and daughters, used to mark milestones. But the designs have often felt locked in time. Jacarti's bet is that there is a market for pieces that carry the emotional resonance of heritage jewellery without the heavy, ornate aesthetic that can feel disconnected from daily life in New York, London, or Dubai.

Zinta herself embodies this audience. She has lived in Los Angeles since marrying American consultant Gene Goodenough in 2016. She co-owns the Punjab Kings IPL franchise. She moves between two worlds, and Jacarti is built to sell to people who do the same.

## What Comes Next

The brand is available online globally through jacarti.com and at its Bandra flagship on Waterfield Road. Whether Jacarti can compete in a market dominated by Tanishq, Sabyasachi's jewellery line, and heritage houses like Birdhichand Ghanshyamdas will depend on whether the design proposition resonates beyond the launch-night headlines.

But the founding team is not treating this as a celebrity vanity project. With Mafatlal's manufacturing depth and Punjabi's Gulf retail network, Jacarti has the infrastructure to scale. The question is whether a Bollywood star can build a brand that is taken seriously for its craft rather than its celebrity. Zinta, characteristically, is betting she can.

*Sources: Bollywood Hungama, Gujarat Watch, India Reporter Live, ANI*"""

    return insert_article({
        'headline': headline,
        'subheadline': subheadline,
        'body': body,
        'slug': 'preity-zinta-jacarti-jewellery-polki-luxury-brand-bandra-mumbai-nri-20260605',
        'category': 'entertainment',
        'vertical': 'entertainment',
        'image_url': img_url,
        'image_caption': 'Preity Zinta at a public event in Mumbai',
        'image_attribution': img_attr,
        'status': 'published',
        'published_at': datetime.now(timezone.utc).isoformat(),
        'is_editorial': False,
        'sources': json.dumps([
            {'name': 'Bollywood Hungama', 'url': 'https://www.bollywoodhungama.com'},
            {'name': 'Gujarat Watch', 'url': 'https://gujaratwatch.co.in'},
            {'name': 'India Reporter Live', 'url': 'https://indiareporterlive.co.in'}
        ])
    })


def article_titan_story():
    """Made In India: A Titan Story on Amazon Prime Video."""
    print('\n📝 Article 2: Made In India: A Titan Story')

    img_url, img_attr = find_best_image(
        person_name='Jim Sarbh',
        commons_query='Jim Sarbh actor',
        pexels_query='vintage Indian watch craftsmanship'
    )

    if not img_url:
        # Try Naseeruddin Shah
        img_url, img_attr = find_best_image(
            person_name='Naseeruddin Shah',
            commons_query='Naseeruddin Shah',
            pexels_query=None
        )
    if not img_url:
        # Try Titan watch as fallback
        img_url, img_attr = find_best_image(
            person_name=None,
            commons_query='Titan watches India',
            pexels_query='luxury Indian watch'
        )

    if not img_url:
        print('  ⚠ No valid image found, skipping article')
        return False

    headline = "Made In India: A Titan Story Is the Series Every NRI Should Be Streaming Right Now"
    subheadline = "Jim Sarbh and Naseeruddin Shah turn the origin story of India's most beloved watch brand into one of 2026's most compelling shows on Amazon Prime Video."

    body = """There is a Titan watch in nearly every Indian household. For the diaspora, it is often the watch your father wore, the one your uncle gifted at a graduation, the brand that meant something before you learned to care about brands. Now, the story of how it came to exist is streaming on Amazon MX Player, and it is significantly better than it has any right to be.

*Made In India: A Titan Story*, a six-episode series directed by Robbie Grewal, adapts journalist Vinay Kamath's book *Titan: Inside India's Most Successful Consumer Brand* into a narrative that feels less like a corporate hagiography and more like a drama about what it took to build something in pre-liberalisation India.

## The Story

Jim Sarbh plays Xerxes Desai, the visionary Tata executive who took on the seemingly impossible task of creating an Indian watch brand that could compete globally. Naseeruddin Shah plays J.R.D. Tata, the patriarch whose faith and resources made the dream viable. The series opens in the late 1970s, when a Swiss watchmaker dismisses India's ability to produce a quality timepiece. Rather than accept the insult, Tata channels it into a mandate.

What follows is a story about bureaucratic obstacles, funding crises, internal disagreements, and the kind of patient, grinding effort that rarely makes for compelling television. Except here, it does. Grewal wisely focuses on the human cost — the marriages strained by obsessive work, the friendships tested by professional disagreements, the quiet moments of doubt that preceded every breakthrough.

## Why the Reviews Are Glowing

Critics have been nearly unanimous. India Forums gave it 4 out of 5 stars, calling it "one of 2026's best shows." The Hollywood Reporter India praised Sarbh and Shah for getting "the timing right." Koimoi awarded 3.5 stars, noting that the series is "obsessed with people, not numbers." Bollywood Shaadis called it a "must-watch" that "manages to make the rise of one of India's most iconic brands into an engaging and surprisingly emotional watch."

The consensus is that the series avoids the trap of corporate worship. It does not pretend that Titan succeeded through pure genius. It shows the mess, the luck, the compromises, and the sheer stubbornness that built a brand.

## The Diaspora Angle

For Indians living abroad, *Made In India* carries a particular weight. Titan is not just a watch company. It is one of a handful of Indian brands that successfully became aspirational in a market where "imported" was synonymous with quality. If you grew up in India in the 1980s or 1990s, or your parents did, the Titan jingle is embedded in your memory. The series gives that nostalgia a narrative context.

It also tells a story that resonates with the immigrant experience more broadly: the conviction that you can build something world-class despite being dismissed, the long struggle for credibility, and the eventual pride of proving the doubters wrong. Xerxes Desai's journey mirrors, in its emotional arc, the journey of every NRI who left India carrying the same stubborn belief.

## The Details

All six episodes are now streaming on Amazon MX Player and Amazon Prime Video, available in Hindi. Each episode runs approximately 55 minutes. The supporting cast includes Vaibhav Tatwawadi, Namita Dubey, Kaveri Seth, and Lakshvir Saran.

If you are looking for a binge that will make you proud, nostalgic, and slightly emotional about a watch company, this is the one.

*Sources: Bollywood Hungama, India Forums, Koimoi, Hollywood Reporter India, Gadgets 360*"""

    return insert_article({
        'headline': headline,
        'subheadline': subheadline,
        'body': body,
        'slug': 'made-in-india-titan-story-jim-sarbh-naseeruddin-shah-amazon-review-nri-20260605',
        'category': 'entertainment',
        'vertical': 'entertainment',
        'image_url': img_url,
        'image_caption': 'Jim Sarbh, who plays Xerxes Desai in Made In India: A Titan Story',
        'image_attribution': img_attr,
        'status': 'published',
        'published_at': datetime.now(timezone.utc).isoformat(),
        'is_editorial': False,
        'sources': json.dumps([
            {'name': 'India Forums', 'url': 'https://www.indiaforums.com'},
            {'name': 'Koimoi', 'url': 'https://www.koimoi.com'},
            {'name': 'Hollywood Reporter India', 'url': 'https://www.hollywoodreporterindia.com'},
            {'name': 'Gadgets 360', 'url': 'https://www.gadgets360.com'}
        ])
    })


def article_gram_chikitsalay():
    """Gram Chikitsalay Season 2 on Prime Video."""
    print('\n📝 Article 3: Gram Chikitsalay Season 2')

    img_url, img_attr = find_best_image(
        person_name='Amol Parashar',
        commons_query='Amol Parashar actor India',
        pexels_query='rural India village healthcare doctor'
    )

    if not img_url:
        img_url, img_attr = find_best_image(
            person_name=None,
            commons_query='rural health centre India village',
            pexels_query='rural Indian village doctor'
        )

    if not img_url:
        print('  ⚠ No valid image found, skipping article')
        return False

    headline = "Gram Chikitsalay Season 2 Drops June 23. TVF's Quiet Hit Is About to Go Global."
    subheadline = "The rural healthcare comedy-drama returns on Prime Video with Amol Parashar, Vinay Pathak, and a new addition that has Bhojpuri fans paying attention."

    body = """If you spent the last year telling friends that *Gram Chikitsalay* is the TVF show they should be watching instead of just rewatching *Panchayat*, your vindication arrives on June 23. Prime Video has confirmed that Season 2 of the rural healthcare comedy-drama will premiere globally, available in Hindi across more than 240 countries and territories.

The show, created by The Viral Fever and directed by Lalitam Tiwari, returns with its full ensemble: Amol Parashar as Dr. Prabhat, alongside Vinay Pathak, Akansha Ranjan Kapoor, Akash Makhija, Anandeshwar Dwivedi, and Garima Vikrant Singh. The notable new addition is Bhojpuri superstar Dinesh Lal Yadav, whose casting signals the show's ambition to broaden its audience beyond the urban-educated TVF core.

## The Premise

Set in the fictional village of Bhathkandi, the series follows Dr. Prabhat, an idealistic young doctor assigned to a crumbling Primary Health Centre. Season 1 established the show's tone — a blend of situational comedy, gentle satire, and genuine empathy for the people navigating India's rural healthcare crisis. It drew comparisons to *Panchayat* for its village setting but distinguished itself by anchoring its comedy in the specific absurdities of a medical system designed to fail.

Season 2 picks up where the first left off. Dr. Prabhat has begun earning the trust of his sceptical patients, but fresh obstacles keep arriving. The show deepens its exploration of the gap between idealism and reality, examining what happens when a well-meaning outsider tries to fix a system that has been broken for decades.

## Why Diaspora Audiences Should Care

TVF has built something remarkable over the past few years: a slate of shows that make Indians abroad feel seen in a way that big-budget Bollywood rarely manages. *Panchayat*, *Kota Factory*, *Aspirants* — these are not just popular shows. They are cultural touchstones for a generation of Indians who grew up in small towns, went through the competitive exam system, and eventually scattered across the world.

*Gram Chikitsalay* fits squarely in that tradition. If your parents are doctors, or if you spent childhood summers visiting relatives in villages where the nearest hospital was an hour away, this show will feel uncomfortably familiar. It captures the texture of rural India without romanticising it or reducing it to poverty porn.

The global Prime Video release means NRIs in the US, UK, Canada, and beyond can watch it on premiere day — a small thing that still matters when you are trying to stay culturally connected from ten time zones away.

## Alia Bhatt's Endorsement

In a notable moment of cross-industry support, Alia Bhatt shared a poster of the show on her Instagram Stories this week, writing "My fav doctor is back!" with a tag to Akansha Ranjan Kapoor, her close friend and the show's co-lead. For a TVF production, that kind of A-list endorsement is unusual and suggests the show has broken through beyond its core audience.

## The Bigger TVF Picture

The Gram Chikitsalay renewal was announced alongside a broader TVF slate on Prime Video, including new seasons of *Aspirants*, *Panchayat*, and *Sapne vs Everyone*, plus new shows *Pyramid* and *Vansh*, and films *Vvan* and *College Fest*. TVF has effectively become the HBO of Indian digital content — a studio whose brand alone signals quality to a specific audience. For NRIs who have watched the Indian OTT space fill with loud, overproduced content, TVF's continued commitment to grounded, character-driven storytelling is a relief.

*Gram Chikitsalay* Season 2 premieres June 23 on Prime Video.

*Sources: Bollywood Hungama, Hollywood Reporter India, Filmfare, Gadgets 360*"""

    return insert_article({
        'headline': headline,
        'subheadline': subheadline,
        'body': body,
        'slug': 'gram-chikitsalay-season-2-tvf-prime-video-june-23-amol-parashar-nri-20260605',
        'category': 'entertainment',
        'vertical': 'entertainment',
        'image_url': img_url,
        'image_caption': 'Amol Parashar, who plays Dr. Prabhat in Gram Chikitsalay',
        'image_attribution': img_attr,
        'status': 'published',
        'published_at': datetime.now(timezone.utc).isoformat(),
        'is_editorial': False,
        'sources': json.dumps([
            {'name': 'Bollywood Hungama', 'url': 'https://www.bollywoodhungama.com'},
            {'name': 'Hollywood Reporter India', 'url': 'https://www.hollywoodreporterindia.com'},
            {'name': 'Filmfare', 'url': 'https://www.filmfare.com'},
            {'name': 'Gadgets 360', 'url': 'https://www.gadgets360.com'}
        ])
    })


# ── Main ────────────────────────────────────────────────────────

if __name__ == '__main__':
    print(f'🎬 Entertainment Writer — {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}')
    print('=' * 60)

    results = []
    results.append(('Preity Zinta / Jacarti', article_preity_zinta_jacarti()))
    results.append(('Titan Story', article_titan_story()))
    results.append(('Gram Chikitsalay S2', article_gram_chikitsalay()))

    print('\n' + '=' * 60)
    print('📊 Summary:')
    for name, ok in results:
        print(f'  {"✅" if ok else "❌"} {name}')
    
    success = sum(1 for _, ok in results if ok)
    print(f'\n  Published: {success}/3')
    
    if success == 0:
        sys.exit(1)
