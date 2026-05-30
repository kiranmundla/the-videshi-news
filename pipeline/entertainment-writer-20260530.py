#!/usr/bin/env python3
"""Entertainment writer for The Videshi — 2026-05-30 batch"""

import json, os, re, sys, time, uuid, urllib.parse
import requests

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

SB_URL = os.environ['SUPABASE_URL']
SB_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    'apikey': SB_KEY,
    'Authorization': f'Bearer {SB_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

def sb_insert(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    if r.status_code in (200, 201):
        result = r.json()
        return result[0] if isinstance(result, list) else result
    print(f"  ✗ Insert failed ({r.status_code}): {r.text[:800]}")
    return None

def sb_patch(table, match, data):
    params = '&'.join(f"{k}={v}" for k, v in match.items())
    r = requests.patch(f"{SB_URL}/rest/v1/{table}?{params}", headers=HEADERS, json=data, timeout=30)
    if r.status_code in (200, 204):
        return True
    print(f"  ✗ Patch failed ({r.status_code}): {r.text[:300]}")
    return False

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
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
    """Fetch an image from Pexels using curl (urllib gets 403)."""
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
                 f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5'],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            for photo in photos:
                url = photo.get('src', {}).get('large2x') or photo.get('src', {}).get('large')
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image(url):
    """Check image URL returns valid image with sufficient size."""
    if not url:
        return False
    # Block banned sources
    banned = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com', '_nc_ht=', '_nc_cat=', 'ccb=']
    for b in banned:
        if b in url:
            print(f"  ✗ Banned image source: {b}")
            return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct and cl > 5000:
            return True
        # Try GET for servers that don't support HEAD well
        if r.status_code != 200:
            r2 = requests.get(url, timeout=10, stream=True,
                              headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            ct = r2.headers.get('Content-Type', '')
            cl = int(r2.headers.get('Content-Length', 0))
            if r2.status_code == 200 and 'image' in ct:
                return True
        print(f"  ✗ Image validation failed: status={r.status_code}, type={ct}, size={cl}")
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False

def make_slug(text, date_suffix="20260530"):
    """Create a URL-friendly slug."""
    slug = re.sub(r'[^a-z0-9\s-]', '', text.lower())
    slug = re.sub(r'[\s]+', '-', slug).strip('-')
    slug = re.sub(r'-+', '-', slug)
    return f"{slug[:80]}-nri-{date_suffix}"

# ─────────────────────────────────────────────────────────
# ARTICLES
# ─────────────────────────────────────────────────────────

articles = []

# ──────────────────────────────
# Article 1: Vashu Bhagnani ₹400 Crore Lawsuit
# ──────────────────────────────

articles.append({
    "headline": "Vashu Bhagnani Just Filed a ₹400 Crore Lawsuit to Block Varun Dhawan's Next Film. The Songs in Question Are From 1999.",
    "subheadline": "The producer behind Biwi No 1 says Tips Industries and David Dhawan used 'Chunari Chunari' and 'Ishq Sona Hai' without permission. The film is five days from release.",
    "slug": "vashu-bhagnani-400-crore-lawsuit-tips-david-dhawan-hai-jawani-biwi-no-1-songs-nri-20260530",
    "category": "entertainment",
    "body": """Bollywood's biggest copyright fight in years just got filed in the Bombay High Court, and it could derail a major June release.

Producer Vashu Bhagnani's Puja Entertainment has slapped a ₹400 crore lawsuit against Tips Industries, Ramesh Taurani, Kumar S Taurani, and director David Dhawan over two songs from the 1999 hit *Biwi No 1* — 'Chunari Chunari' and 'Ishq Sona Hai.' The allegation: the defendants used the iconic tracks in the upcoming Varun Dhawan-starrer *Hai Jawani Toh Ishq Hona Hai* without valid rights.

## The Core Dispute

The lawsuit, filed through advocates V K Dubey Associates, seeks an immediate injunction to halt the release, distribution, streaming, and commercial exploitation of the film and any promotional material featuring the two disputed songs. The film is currently scheduled to hit theatres worldwide on June 5.

According to Bhagnani's legal team, the original agreements between Puja Entertainment and Tips Industries covered only audio rights. In 2018, Tips reportedly emailed Bhagnani requesting visual rights — but the negotiations never reached a conclusion. Puja Entertainment subsequently sent a notice cancelling even the previously granted audio rights, which, their lawyers argue, means Tips cannot legally license the songs for use in a new film.

"If they are the lawful owners of the music rights, they must show their documents," advocate Dubey told news agency ANI. "Justice will prevail, and the truth will come out."

## Why This Matters Beyond Bollywood

The lawsuit touches a nerve that runs deep in Indian cinema's commercial infrastructure. For decades, music rights agreements in Bollywood operated on handshake deals and loosely worded contracts. The distinction between audio rights, visual rights, and synchronization rights — standard categories in Western music licensing — was often blurred or ignored entirely.

The *Biwi No 1* songs are not obscure catalogue tracks. 'Chunari Chunari' remains one of the most recognizable Bollywood dance numbers of the 1990s, a staple at every Indian wedding DJ's playlist from New Jersey to London to Sydney. For the diaspora, these aren't just songs — they're cultural bookmarks of a specific era of growing up Indian abroad.

## The Bigger Picture

The timing is brutal. *Hai Jawani Toh Ishq Hona Hai* has been through a carousel of release date changes — originally June 5, then June 12, then May 22, and back to June 5 after Yash's *Toxic* vacated the slot. The film was already surrounded by noise: Mouni Roy playing mother to 39-year-old Varun Dhawan drew social media criticism, and influencer-review controversies added more turbulence.

David Dhawan has positioned this as his final film. Vashu Bhagnani was the producer behind the original *Biwi No 1*, the very film whose songs are now at the centre of this dispute. There's an irony in the fact that a filmmaker's swan song could be derailed by the music from his own earlier success.

Puja Entertainment is also seeking an additional ₹100 crore in damages if the defendants fail to comply. The court has permitted the filing and will hear the matter soon. Whether it results in a stay order before June 5 remains the ₹400-crore question.

## What the Diaspora Should Know

For NRIs who grew up with Govinda-Karisma dance numbers and David Dhawan comedies, this lawsuit is a reminder that the songs you carry in your head are also assets on somebody's balance sheet. As Bollywood's remake and remix culture accelerates, the legal scaffolding underneath it is finally being stress-tested in court.

*Sources: Bollywood Hungama, ANI, Zoom TV Entertainment*""",
    "sources": ["Bollywood Hungama", "ANI", "Zoom TV Entertainment"],
    "person": "Vashu Bhagnani"
})

# ──────────────────────────────
# Article 2: Alpha Preponed to July 3
# ──────────────────────────────

articles.append({
    "headline": "Alpha Just Got Preponed to July 3. Alia Bhatt's Spy Thriller Will Now Have Two Weeks of Open Road.",
    "subheadline": "With Dhamaal 4 and Christopher Nolan's The Odyssey both landing on July 17, Aditya Chopra moved the YRF Spy Universe's first female-led film up by a week.",
    "slug": "alpha-preponed-july-3-alia-bhatt-sharvari-yrf-spy-universe-nri-20260530",
    "category": "entertainment",
    "body": """The Bollywood release calendar just shifted again, and this time it's in a film's favour.

Yash Raj Films has reportedly preponed the release of *Alpha* — the YRF Spy Universe's first female-led instalment — from July 10 to July 3, 2026. The move comes after Ajay Devgn's *Dhamaal 4* vacated the July 3 slot, pushing to July 17 instead. That same week also brings Christopher Nolan's *The Odyssey*, creating a potential traffic jam that *Alpha* now sidesteps entirely.

## The Calendar Chess

The logic is straightforward: with no major Bollywood release planned for July 3, producer Aditya Chopra saw a window and took it. By opening a week earlier, *Alpha* gets a clear two-week theatrical run before the July 17 double punch of *Dhamaal 4* and Nolan's latest.

A trade source told Bollywood Hungama: "July 3 has emerged as an apt date to bring Alpha to cinemas since Dhamaal 4, which was scheduled to release on the same day, has now been pushed to July 17. With no major release planned for July 3, producer Aditya Chopra felt it was the right date to bring Alpha to theatres."

This is not the first date change for *Alpha*. The film was initially planned for Christmas 2025, then shifted to April 2026, then July 10. The latest move, however, is a prepone — a rarity in an industry where delays are the norm.

## What Makes Alpha Different

Directed by Shiv Rawail, who helmed the critically acclaimed series *The Railway Men*, *Alpha* puts Alia Bhatt and Sharvari at the centre of a globe-trotting espionage narrative. Unlike the stylised action of *Pathaan* or *War 2*, the film is described as raw and grounded — closer to field intelligence than franchise spectacle.

Bobby Deol plays the primary antagonist, teased through a post-credits appearance in *War 2*. Anil Kapoor returns as Vikrant Kaul, a senior intelligence official. And Hrithik Roshan is expected to make a special appearance reprising Major Kabir Dhaliwal, tying the film into the broader Spy Universe timeline.

For Alia Bhatt, this is her first theatrical release since *Jigra* in 2024. For Sharvari, who has been steadily building momentum through OTT projects and *Munjya*, it's a chance to cement her position in mainstream cinema.

## The Diaspora Angle

The YRF Spy Universe has always performed well internationally, with *Pathaan* crossing ₹300 crore overseas. Indian audiences in North America, the UK, and the Middle East have driven significant opening-weekend numbers for the franchise. An earlier release means advance booking windows in international markets open sooner — and for a franchise with built-in awareness, that matters.

Sharvari is also currently promoting *Main Vaapas Aaunga*, keeping her visibility high across platforms where diaspora audiences are already engaged. The one-two punch of marketing momentum plus a cleaner release window makes July 3 a calculated bet.

## What's at Stake

The YRF Spy Universe is Bollywood's most ambitious franchise experiment. After the commercial disappointment of *War 2* and *Tiger 3*, the franchise needs a course correction. *Alpha* — with its female leads, its grounded tone, and its leaner storytelling promise — could be exactly that. Or it could confirm that the franchise fatigue is real.

Either way, July 3 is now circled on the calendar.

*Sources: Bollywood Hungama, Filmfare, Sacnilk*""",
    "sources": ["Bollywood Hungama", "Filmfare", "Sacnilk"],
    "person": "Alia Bhatt"
})

# ──────────────────────────────
# Article 3: Divyanka Tripathi & Vivek Dahiya Twins
# ──────────────────────────────

articles.append({
    "headline": "Divyanka Tripathi and Vivek Dahiya Brought Their Twin Boys Home From Hospital. 'Mere Karan Arjun Aa Gaye,' He Said.",
    "subheadline": "After 10 years of marriage, Indian television's most-loved couple stepped out as a family of four — with one request for the paparazzi.",
    "slug": "divyanka-tripathi-vivek-dahiya-twin-boys-karan-arjun-hospital-nri-20260530",
    "category": "entertainment",
    "body": """There are celebrity baby announcements, and then there is Vivek Dahiya quoting *Karan Arjun* while bringing his twin sons home from the hospital.

Television actors Divyanka Tripathi and Vivek Dahiya made their first public appearance with their newborn twin boys on Friday, leaving a Mumbai hospital with their babies in their arms and their extended family in tow. A black car decorated with blue and white balloons pulled up outside the hospital, and Vivek — grinning — introduced himself and Divyanka to the waiting media: "Presenting the new mother and father in town."

## The Announcement

The couple had announced the birth on May 26 through an Instagram post featuring an animated image of two baby boys on clouds. The caption read: "We asked for happiness... God said, 'Take double.' Blessed with twin baby boys."

Vivek's follow-up was pure Bollywood: "The wait is finally over... 'The Boys' are here and life already feels more beautiful than we ever imagined. Mere Karan Arjun aa gaye!" — a reference to the iconic 1995 Salman Khan-Shah Rukh Khan film that every Indian household, across continents, can quote from memory.

## A Decade Together

Divyanka and Vivek met on the sets of *Yeh Hai Mohabbatein* and married in 2016. Over the past decade, they have remained one of Indian television's most recognisable couples — their journey documented across reality shows like *Nach Baliye 8* and *Khatron Ke Khiladi 11*.

Divyanka rose to national fame with *Banoo Main Teri Dulhann* and later became a household name through *Yeh Hai Mohabbatein*, one of the longest-running Indian television serials. Vivek, who started as an outsider in the industry, carved his own space through consistent television work and the couple's joint public presence.

The arrival of their twins after 10 years of marriage drew particularly emotional responses from fans. "Who can refuse such a sweet smiling request from Divyanka," wrote one user. "She is always so polite and courteous. No attitude, always kind."

## One Rule for the Cameras

In the video that went viral across social media, Divyanka thanked the photographers for their well-wishes — and then made one clear request: please don't show the babies' faces. The paparazzi agreed. After a brief introduction of the newborns, the family posed together, distributed sweets, and headed home.

It was a small moment, but fans noticed. Several comments praised the couple for handling the public moment with warmth while drawing a firm line around their children's privacy — a balance that feels increasingly rare in Indian celebrity culture.

## Why the Diaspora Cares

Divyanka Tripathi's fanbase extends well beyond India. Indian television serials, particularly Star Plus and Zee shows, have massive viewership across the US, UK, Canada, and the Middle East through OTT platforms and satellite channels. *Yeh Hai Mohabbatein* ran for six years and built a loyal global following.

For diaspora audiences who grew up watching these serials with their families, the couple's milestone feels personal. The *Karan Arjun* reference is the cherry on top — a line that transcends generations and geographies, instantly recognisable whether you're in Mumbai or Michigan.

A traditional aarti was performed by Divyanka's mother-in-law as the family arrived home, marking the beginning of a new chapter that their fans have waited a decade to celebrate.

*Sources: ANI, LatestLY, Zoom TV Entertainment, India Forums*""",
    "sources": ["ANI", "LatestLY", "Zoom TV Entertainment", "India Forums"],
    "person": "Divyanka Tripathi"
})

# ──────────────────────────────
# Article 4: Anupam Kher's Shri Ram Bhoomi — 552nd Film
# ──────────────────────────────

articles.append({
    "headline": "Anupam Kher Just Started His 552nd Film. It's Called Shri Ram Bhoomi and It's About Ayodhya.",
    "subheadline": "Zee Studios brings in The Kerala Story 2 director Kamakhya Narayan Singh for a drama rooted in faith, sacrifice, and 'one of the most consequential chapters in modern Indian history.'",
    "slug": "anupam-kher-shri-ram-bhoomi-552nd-film-zee-studios-ayodhya-nri-20260530",
    "category": "entertainment",
    "body": """At 71, Anupam Kher is not slowing down. He is, in fact, accelerating.

The veteran actor has commenced shooting for *Shri Ram Bhoomi*, a new drama from Zee Studios that marks his 552nd film — a number that defies easy comprehension in any film industry, anywhere in the world. Directed by National Award-winning filmmaker Kamakhya Narayan Singh, who last helmed *The Kerala Story 2*, the film is positioned as an emotionally charged narrative centred on Ayodhya and the cultural history of Lord Ram's birthplace.

## What We Know

Zee Studios launched the project with a mahurat ceremony and an official announcement across social media: "A title that echoes emotion. A story shrouded in intrigue. The journey of Shri Ram Bhoomi officially begins."

The cast brings together a cross-generational lineup. Kher leads alongside Ritwik Bhowmik — a rising star best known for his OTT work in shows like *Bandish Bandits* — and Amruta Khanvilkar, the versatile actress who has built a reputation across Marathi and Hindi cinema. The production is a collaboration between Zee Studios, Dancing Shiva Films, and Cinekorn Entertainment.

Plot details remain tightly guarded, but the film is described as a story rooted in faith, sacrifice, truth, and homecoming. Given the title and the director's previous work on culturally charged material, the Ayodhya connection is unmistakable.

## The 552-Film Man

Anupam Kher's filmography is its own kind of monument. From *Saaransh* in 1984 — where a 28-year-old Kher played a retired man mourning his son — to Hollywood roles in *Silver Linings Playbook* and *The Big Sick*, his career spans four decades, multiple languages, and virtually every genre Indian cinema has attempted.

His upcoming slate alone reads like a small studio's annual output: *Khosla Ka Ghosla 2* with Dibakar Banerjee (reuniting the original cast including Boman Irani, Parvin Dabas, and Ranvir Shorey), an untitled project with Sooraj Barjatya, and now *Shri Ram Bhoomi*. The man does not have an off switch.

## The Director's Track Record

Kamakhya Narayan Singh's involvement signals the kind of film Zee Studios is aiming for. *The Kerala Story* was one of the most commercially successful — and politically polarising — Indian films in recent years, crossing ₹300 crore worldwide. The sequel continued the franchise's formula of cultural confrontation wrapped in mainstream thriller packaging.

With *Shri Ram Bhoomi*, Singh shifts from religious conversion narratives to the cultural and spiritual history of Ayodhya itself. The timing is not accidental. The ₹4,000-crore *Ramayana* adaptation starring Ranbir Kapoor and Sai Pallavi has dominated industry conversation for months, and Ayodhya-centric stories have become prime real estate for major studios.

## The Diaspora Connection

For NRIs, the Ayodhya Ram Mandir has been a landmark moment of cultural identity — the consecration ceremony in January 2024 was watched by millions of Indians abroad. A cinematic exploration of Ayodhya's significance, led by an actor who has become a fixture of diaspora cultural life (Kher's one-man shows regularly sell out in the US and UK), carries a built-in audience.

Ritwik Bhowmik's presence also signals a generational bridge. His OTT following skews younger and more globally distributed — the kind of audience that discovers Indian content through Netflix and Prime rather than theatrical releases.

Whether *Shri Ram Bhoomi* will aim for theatrical spectacle or a more intimate dramatic register remains to be seen. But with Anupam Kher at 552 and counting, the film already has something most productions lack: the gravitational pull of a performer who has never stopped working.

*Sources: IANS, Bollywood Hungama, Sacnilk, CineTalkers*""",
    "sources": ["IANS", "Bollywood Hungama", "Sacnilk", "CineTalkers"],
    "person": "Anupam Kher"
})

# ─────────────────────────────────────────────────────────
# PUBLISH
# ─────────────────────────────────────────────────────────

published = 0
failed = 0

for i, art in enumerate(articles):
    print(f"\n{'='*60}")
    print(f"Article {i+1}: {art['headline'][:70]}...")
    
    # Validate article
    if len(art['headline']) < 20 or len(art['headline']) > 200:
        print(f"  ✗ Headline length issue: {len(art['headline'])} chars")
    if len(art['subheadline']) < 15:
        print(f"  ✗ Subheadline too short: {len(art['subheadline'])} chars")
    
    word_count = len(art['body'].split())
    if word_count < 400:
        print(f"  ✗ Body too short: {word_count} words (minimum 400)")
        failed += 1
        continue
    print(f"  ✓ Word count: {word_count}")
    
    # Image sourcing — Wikipedia first for person articles
    img_url = None
    person = art.get('person')
    if person:
        img_url = fetch_wikipedia_person_image(person)
        if not img_url and person == "Divyanka Tripathi":
            img_url = fetch_wikipedia_person_image("Divyanka Tripathi Dahiya")
        if not img_url and person == "Vashu Bhagnani":
            img_url = fetch_wikipedia_person_image("Vashu Bhagnani (producer)")
    
    if not img_url:
        # Specific Pexels fallback
        pexels_queries = {
            "Vashu Bhagnani": ("Bombay High Court building", "Indian courthouse"),
            "Alia Bhatt": ("Bollywood spy movie action", "Indian cinema action"),
            "Divyanka Tripathi": ("Indian couple newborn baby celebration", "Indian family celebration"),
            "Anupam Kher": ("Ayodhya temple", "Indian cinema veteran actor")
        }
        if person and person in pexels_queries:
            q1, q2 = pexels_queries[person]
            img_url = fetch_pexels_image(q1, q2)
    
    img_attribution = "Wikimedia Commons"
    if img_url and 'pexels.com' in img_url:
        img_attribution = "The Videshi"
    
    if img_url and validate_image(img_url):
        print(f"  ✓ Image validated")
    elif img_url:
        print(f"  ⚠ Image validation failed, proceeding without image")
        img_url = None
    else:
        print(f"  ⚠ No image found")

    # Insert article
    article_data = {
        "headline": art['headline'],
        "subheadline": art['subheadline'],
        "slug": art['slug'],
        "category": art['category'],
        "body": art['body'],
        "vertical": art['category'],
        "status": "published",
        "published_at": f"2026-05-30T15:32:{30+i:02d}+00:00",
        "sources": ", ".join(art['sources']),
    }
    
    if img_url:
        article_data['image_url'] = img_url
        article_data['image_attribution'] = img_attribution

    result = sb_insert('p2_articles', article_data)
    if result:
        art_id = result.get('id')
        print(f"  ✓ Published: {art['slug']} (id: {art_id})")
        published += 1
    else:
        print(f"  ✗ Failed to publish: {art['slug']}")
        failed += 1

print(f"\n{'='*60}")
print(f"DONE: {published} published, {failed} failed")
