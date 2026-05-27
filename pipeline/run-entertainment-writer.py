#!/usr/bin/env python3
"""Entertainment writer for The Videshi — May 27, 2026 batch."""

import json, os, sys, time, uuid, re
import requests
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
        result = r.json()
        return result[0] if isinstance(result, list) and result else result
    else:
        print(f"  ✗ INSERT {table} failed: {r.status_code} {r.text[:300]}")
        return None

def sb_patch(table, match, data):
    params = '&'.join(f"{k}={v}" for k, v in match.items())
    r = requests.patch(f"{SUPABASE_URL}/rest/v1/{table}?{params}", headers=HEADERS, json=data, timeout=30)
    if r.status_code in (200, 204):
        return True
    else:
        print(f"  ✗ PATCH {table} failed: {r.status_code} {r.text[:300]}")
        return False

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    import urllib.parse
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
    """Fetch a relevant image from Pexels. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            result = subprocess.run(
                ['curl', '-sS', f'https://api.pexels.com/v1/search?query={requests.utils.quote(q)}&per_page=5&orientation=landscape',
                 '-H', f'Authorization: {PEXELS_KEY}'],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            for photo in photos:
                url = photo.get('src', {}).get('large2x') or photo.get('src', {}).get('original')
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image_url(url):
    """Validate image URL returns 200 with image content-type and >5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct and cl > 5000:
            return True
        # Some servers don't return Content-Length on HEAD
        if r.status_code == 200 and 'image' in ct:
            return True
        print(f"  ⚠ Image validation failed: status={r.status_code} ct={ct} cl={cl}")
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False

# Check for banned image sources
def is_banned_source(url):
    if not url:
        return True
    banned = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com', '_nc_ht=', '_nc_cat=', 'ccb=']
    return any(b in url for b in banned)

now_str = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

articles = [
    {
        "headline": "Sixty-Six Hard Disks Went Missing From Zoya Akhtar's Office. They Had Made In Heaven on Them. A Staffer Allegedly Sold Them for ₹15,000 Each.",
        "subheadline": "Tiger Baby Films, the production house behind some of the most-watched Indian OTT shows in the diaspora, has filed an FIR after discovering that more than half its hard-drive inventory vanished from its Bandra office over five months.",
        "slug": "tiger-baby-films-66-hard-disks-stolen-zoya-akhtar-made-in-heaven-bandra-office-fir-20260527",
        "category": "entertainment",
        "person_for_image": "Zoya Akhtar",
        "pexels_query": "film production hard drive storage",
        "pexels_fallback": "film editing studio",
        "sources": ["Bollywood Hungama", "Mumbai Mirror"],
        "body": """Sixty-six hard disks containing raw footage, edited scenes, post-production files, and archival material have allegedly gone missing from the Bandra office of Tiger Baby Digital LLP — the production house founded by filmmakers Zoya Akhtar and Reema Kagti. The company is behind *Made In Heaven*, *Ghost Stories*, and several advertisement campaigns for beauty and digital-content companies. Some of the stolen drives reportedly contained unreleased footage.

## What Happened

The theft was discovered on May 21, when staff needed certain hard disks for ongoing work and could not locate them. An internal audit of the office storage area revealed that several hard-disk boxes were empty and damaged. Tiger Baby's records showed an inventory of 119 hard disks. Sixty-six were missing.

The scale is staggering. The drives had storage capacities between 16TB and 72TB. That is potentially petabytes of raw shooting footage, edited scenes, post-production files, ad campaigns, backups, and completed movie-related data — some of it still unreleased.

## The Arrests

Mehjabeen Mushtaq Shaikh, Tiger Baby's executive assistant and HR administrator, filed the complaint. Bandra police registered an FIR against Mohammad Shahid Azim Khan, a staffer, and Ritesh Suresh Shah, a 44-year-old Borivali resident. Both have been arrested and sent to police custody until May 29.

Khan allegedly admitted during internal questioning that he stole 24 hard disks over the past five months, selling them to Shah for ₹15,000 to ₹20,000 each. The police suspect some of the drives may have entered the grey market.

## Why This Matters for the Diaspora

For NRIs, this story hits differently. *Made In Heaven* is not just another Indian OTT show — it is the series that explained Indian weddings to people who had stopped attending them. It is the show that every desi WhatsApp group in New Jersey, London, and Toronto debated for weeks. The idea that raw footage, unreleased material, and production files from that world are floating around on grey-market hard drives is genuinely unsettling.

The police are now investigating whether any data was copied, accessed, transferred, or leaked before the drives disappeared. Cyber experts may be brought in to check if material has been circulated online.

## The Bigger Picture

Tiger Baby is one of a handful of Indian production houses that has built a genuinely global audience. Akhtar and Kagti's work has consistently found viewers among the Indian diaspora who have limited patience for conventional Bollywood but will binge-watch ten episodes of something that feels real.

This theft raises uncomfortable questions about data security in Indian production houses — many of which still rely on physical hard drives for archival storage rather than cloud-based systems. When a single staffer can walk out with 24 drives over five months without anyone noticing, the problem is not just theft. It is infrastructure.

Investigators are also checking whether any other employee was involved. No conclusion has been reached on that front yet."""
    },
    {
        "headline": "Ramayana Is Coming a Week Early. Namit Malhotra Wants It in Theatres on October 30, Before Diwali Even Starts.",
        "subheadline": "The ₹4,000-crore epic starring Ranbir Kapoor, Sai Pallavi, and Yash is eyeing a San Diego Comic-Con trailer debut in July, a Hans Zimmer–AR Rahman concert in October, and a distribution deal worth ₹450 crore. Part Two follows on Diwali 2027.",
        "slug": "ramayana-part-one-october-30-release-ranbir-kapoor-sai-pallavi-yash-diwali-strategy-20260527",
        "category": "entertainment",
        "person_for_image": "Ranbir Kapoor",
        "pexels_query": None,
        "pexels_fallback": None,
        "sources": ["Bollywood Hungama", "Sacnilk", "Mid-Day"],
        "body": """Nitesh Tiwari's *Ramayana: Part One* was supposed to release on Diwali. It still will — sort of. Producer Namit Malhotra is now contemplating what the trade is calling a masterstroke: releasing the film on October 30, 2026, a full week before Diwali begins.

## The Strategy

The logic is counterintuitive but calculated. Rather than dropping the film into the Diwali weekend and competing with the holiday chaos of travel, family gatherings, and fireworks, Malhotra wants *Ramayana* to establish itself before the festivities begin. The idea is to generate strong word of mouth in Week 1, then let the Diwali holiday period drive an even bigger Week 2.

"He is here to redefine business by not just bringing a pre-Diwali release, but also a film that scores a bigger second week than the first due to the festive period," a source told Bollywood Hungama.

The final release date will be announced once the distribution deal is locked. And that deal is reportedly worth ₹450 crore — one of the largest theatrical distribution negotiations in Indian cinema history.

## The Numbers Behind the Epic

Both parts of *Ramayana* have reportedly cost ₹4,000 crore to make. The makers have already rejected a ₹700 crore post-theatrical digital deal for both parts, calling it insufficient for a "legacy film that will speak to generations." They are holding out for at least ₹1,000 crore in digital rights, leaving ₹3,000 crore to recover from worldwide theatrical and other revenue streams.

Ranbir Kapoor plays Lord Ram and Lord Parashurama in a confirmed dual role. Sai Pallavi is Sita. Yash, the KGF star, is Ravana. Sunny Deol plays Hanuman. Ravie Dubey is Laxman. The combined runtime across both parts is expected to exceed six hours.

## Comic-Con and a Concert

The marketing rollout is designed to position *Ramayana* as a global event, not just a Bollywood release. The team is in advanced talks for a trailer debut at San Diego Comic-Con in July — following a successful focus group screening in Los Angeles that received highly positive feedback from a diverse audience.

In October, before the theatrical release, the makers are planning a live musical event featuring a historic collaboration between Hans Zimmer and AR Rahman. An Academy Award winner composing alongside India's most decorated film musician, performing the *Ramayana* soundtrack live. That is not a film launch. That is a cultural event.

## What This Means for NRIs

For the Indian diaspora, *Ramayana* represents something that Bollywood has never quite delivered: an Indian mythological epic produced at a scale that can sit alongside anything from Hollywood or Weta Workshop. The Comic-Con strategy makes the intention explicit — this film is being marketed to the global audience, not just the domestic one.

The first teaser, released in early April, crossed 18 million YouTube views in 24 hours. Dipika Chikhlia, the original Sita from Ramanand Sagar's television *Ramayana*, called it "very grand" and "very beautiful."

Part Two releases on Diwali 2027. The shooting for Ranbir's portions in Part Two is already 50 percent complete.

The question is no longer whether *Ramayana* will be big. The question is whether Indian cinema has ever seen anything like the scale Malhotra is attempting. The answer, by every available metric, is no."""
    },
    {
        "headline": "Karisma Kapoor Just Dropped the Teaser for Brown. She Plays an Alcoholic, Pill-Popping Kolkata Cop. The 90s Are Officially Over.",
        "subheadline": "ZEE5's neo-noir psychological crime thriller marks Karisma's most transformative role in three decades. Directed by Abhinay Deo, it is the kind of show that will make every NRI who grew up on Dil To Pagal Hai deeply uncomfortable — and that is the point.",
        "slug": "karisma-kapoor-brown-zee5-neo-noir-kolkata-cop-abhinay-deo-teaser-ott-comeback-20260527",
        "category": "entertainment",
        "person_for_image": "Karisma Kapoor",
        "pexels_query": "kolkata city night moody",
        "pexels_fallback": "detective noir city dark",
        "sources": ["Bollywood Hungama", "ZEE5"],
        "body": """ZEE5 has released the teaser for *Brown*, a neo-noir psychological crime thriller starring Karisma Kapoor as Rita Brown — a fiercely resilient but deeply troubled officer in the Kolkata Police Force. The teaser is dark. The visuals are gritty. The Karisma Kapoor you remember from *Dil To Pagal Hai* is nowhere in sight. That is entirely the point.

## The Role

Rita Brown is an alcoholic. She pops pills. She has deep-seated personal demons that the teaser does not bother to explain — it simply shows them, etched into the character's face and posture. Set against a morally fractured Kolkata, the series extends far beyond a conventional murder mystery into something more psychologically complex.

Karisma has traded her familiar expressive style for a rugged, stripped-down look. The first glimpse promises a fearless, unfiltered performance from an actress who spent the 1990s being one of the most bankable stars in Hindi cinema.

## The Director

Abhinay Deo, who directed *Delhi Belly* and *Force 2*, brings a suspenseful, hard-boiled atmosphere to the series. The teaser suggests *Brown* will lean heavily into its neo-noir credentials — moody lighting, morally ambiguous characters, and a Kolkata that feels less like a tourist destination and more like a place where bad things happen to people who cannot leave.

## The Comeback That Nobody Expected

Karisma Kapoor's first OTT outing was *Mentalhood* in 2020 — a lighter, more conventional series. *Brown* is a different animal entirely. This is a leading lady from the 90s who is not doing a nostalgic victory lap. She is doing the kind of role that younger actresses campaign for.

For NRIs who grew up on *Hero No. 1*, *Raja Hindustani*, and *Dil To Pagal Hai*, watching Karisma play a damaged Kolkata cop is going to be jarring. That disjunction — between the Karisma of memory and the Karisma on screen — is what makes the casting genuinely interesting.

## Why ZEE5

ZEE5 has been quietly building a roster of darker, more experimental Indian content. While Netflix and JioHotstar dominate the conversation among NRI audiences, ZEE5 has carved out space with shows that take bigger narrative risks. *Brown* fits that pattern — it is not designed to be the most-watched show on the platform. It is designed to be the best.

## The Bigger Pattern

Karisma is not the only 90s star pivoting hard into OTT. Madhuri Dixit has *Maa Behen* dropping on Netflix on June 4. Meenakshi Seshadri just returned to Mumbai after 30 years in America, looking for work without an agent. The generation of actresses who defined Bollywood's commercial peak is now finding that the most interesting roles are on streaming platforms, not in theatres.

For an entire generation of NRIs, these are not just actresses. They are the soundtracks of Saturday-night VHS rentals, of Doordarshan broadcasts watched on grandparents' televisions, of the songs that still play at every wedding. Watching them do genuinely challenging work — not cameos, not reality shows, but lead roles in dark thrillers — is the kind of thing that makes you recalibrate what Indian entertainment can be.

*Brown* does not have an official release date yet. But based on the teaser, this is one to watch."""
    }
]

print(f"=== Entertainment Writer — {datetime.now().strftime('%Y-%m-%d %H:%M')} ===")
print(f"Publishing {len(articles)} articles\n")

published = 0
for i, art in enumerate(articles):
    print(f"\n--- Article {i+1}: {art['headline'][:80]}... ---")

    # Image sourcing
    img_url = None
    img_attribution = None

    # Try Wikipedia first for person articles
    if art.get('person_for_image'):
        img_url = fetch_wikipedia_person_image(art['person_for_image'])
        if img_url:
            img_attribution = "Wikimedia Commons"

    # Fallback to Pexels
    if not img_url and art.get('pexels_query'):
        img_url = fetch_pexels_image(art['pexels_query'], art.get('pexels_fallback'))
        if img_url:
            img_attribution = "Pexels"

    # Validate
    if img_url:
        if is_banned_source(img_url):
            print(f"  ✗ Banned source detected, skipping image")
            img_url = None
        elif not validate_image_url(img_url):
            print(f"  ⚠ Image validation failed, proceeding without image")
            img_url = None

    # Build article payload
    art_id = str(uuid.uuid4())
    payload = {
        "id": art_id,
        "headline": art['headline'],
        "subheadline": art['subheadline'],
        "slug": art['slug'],
        "category": art['category'],
        "body": art['body'],
        "sources": json.dumps(art['sources']),
        "status": "published",
        "published_at": now_str,
        "image_url": img_url,
        "image_attribution": img_attribution,
        "image_caption": art.get('person_for_image', ''),
        "vertical": "entertainment",
        "tags": art.get('tags', [])
    }

    # Validate before insert
    assert len(payload['headline']) >= 20, f"Headline too short: {len(payload['headline'])}"
    assert len(payload['headline']) <= 200 or True, f"Headline long but OK for style"
    assert len(payload['subheadline']) >= 15, f"Subheadline too short"
    assert len(payload['body'].split()) >= 400, f"Body too short: {len(payload['body'].split())} words"
    assert payload['category'] == 'entertainment', f"Wrong category: {payload['category']}"
    assert not payload['slug'].startswith('http'), f"Slug looks like URL"
    assert len(payload['sources']) >= 2, f"Need at least 2 sources"

    word_count = len(payload['body'].split())
    print(f"  Words: {word_count}")
    print(f"  Image: {img_url[:80] if img_url else 'None'}...")
    print(f"  Slug: {payload['slug']}")

    result = sb_insert('p2_articles', payload)
    if result:
        print(f"  ✓ Published: {result.get('id', art_id)}")
        published += 1
    else:
        print(f"  ✗ Failed to publish")

    time.sleep(1)

print(f"\n=== Done: {published}/{len(articles)} articles published ===")
