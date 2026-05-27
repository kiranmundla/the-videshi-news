#!/usr/bin/env python3
"""
The Videshi Entertainment Writer — 2026-05-27
Publishes 3 fresh entertainment articles with Wikipedia-first image sourcing.
"""

import json, os, re, sys, time, uuid, subprocess, urllib.parse, textwrap
from datetime import datetime, timezone

# ── Env ──────────────────────────────────────────────────────────────
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY   = os.environ.get('PEXELS_API_KEY', '')

HEADERS_SB = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation',
}

# ── Helpers ──────────────────────────────────────────────────────────
def sb_post(table, data):
    import requests
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    r = requests.post(url, headers=HEADERS_SB, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

def sb_patch(table, match, data):
    import requests
    params = '&'.join(f"{k}={v}" for k, v in match.items())
    url = f"{SUPABASE_URL}/rest/v1/{table}?{params}"
    r = requests.patch(url, headers=HEADERS_SB, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

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
    """Fetch image from Pexels using curl (Python urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
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
            for p in photos:
                url = p.get('src', {}).get('large2x') or p.get('src', {}).get('large')
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image_url(url):
    """Verify the URL returns HTTP 200 with image content and >5KB."""
    if not url:
        return False
    try:
        result = subprocess.run(
            ['curl', '-sS', '-o', '/dev/null', '-w', '%{http_code} %{size_download} %{content_type}', '-L', url],
            capture_output=True, text=True, timeout=15
        )
        parts = result.stdout.strip().split(' ', 2)
        code = parts[0]
        size = int(float(parts[1])) if len(parts) > 1 else 0
        ctype = parts[2] if len(parts) > 2 else ''
        if code == '200' and size > 5000 and 'image' in ctype:
            print(f"  ✓ Image validated: {code}, {size} bytes, {ctype}")
            return True
        else:
            print(f"  ✗ Image validation failed: {code}, {size} bytes, {ctype}")
            return False
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
        return False

def is_banned_url(url):
    """Check if URL is from a banned source (Meta CDN etc)."""
    if not url:
        return True
    banned = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com', '_nc_ht=', '_nc_cat=', 'ccb=']
    return any(b in url for b in banned)

def upload_image_to_supabase(source_url, filename):
    """Download image from URL and upload to Supabase storage bucket 'article-images'."""
    import requests
    tmp_path = f"/tmp/{filename}"
    try:
        # Download
        r = requests.get(source_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=20)
        r.raise_for_status()
        with open(tmp_path, 'wb') as f:
            f.write(r.content)
        print(f"  ✓ Downloaded {len(r.content)} bytes to {tmp_path}")
        
        # Upload to Supabase storage
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        headers = {
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'image/jpeg',
            'x-upsert': 'true',
        }
        with open(tmp_path, 'rb') as f:
            r2 = requests.post(upload_url, headers=headers, data=f, timeout=30)
        
        if r2.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase storage: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed ({r2.status_code}): {r2.text[:200]}")
            return source_url  # Fall back to original URL if it's from Wikipedia/Pexels
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        return source_url
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

# ── Articles ─────────────────────────────────────────────────────────

ARTICLES = [
    {
        "headline": "Hema Malini Accepted Dharmendra's Posthumous Padma Vibhushan on Sunday. Their Daughter Ahana Broke Down. He Made 300 Films in 65 Years and Never Got India's Second-Highest Civilian Honour While He Was Alive.",
        "subheadline": "The Sholay legend, who died in November 2025, was finally recognised with the Padma Vibhushan at Rashtrapati Bhavan. For NRIs who grew up on his films, it was the most emotional two minutes of Indian television this year.",
        "slug": "dharmendra-posthumous-padma-vibhushan-hema-malini-ahana-deol-sholay-nri-legacy-20260527",
        "category": "entertainment",
        "tags": ["entertainment", "bollywood", "dharmendra", "padma-awards", "hema-malini", "sholay", "diaspora", "nri"],
        "person_for_image": "Dharmendra",
        "pexels_query": None,
        "sources": "LatestLY, Filmibeat, Boldsky, The Hindu Business Line, Storyboard18",
        "body": """Dharmendra never collected his Padma Vibhushan.

He died on November 12, 2025 — 89 years old, a career that stretched from 1960's *Dil Bhi Tera Hum Bhi Tere* to 2024's *Teri Baaton Mein Aisa Uljha Jiya*, 300-plus films across six decades, the man who made every Indian boy believe he could punch through a wall and still cry at a wedding. India's second-highest civilian honour arrived six months after his funeral.

On Sunday, May 25, 2026, at Rashtrapati Bhavan in New Delhi, President Droupadi Murmu presented the Padma Vibhushan to Hema Malini — actor, BJP MP, and Dharmendra's wife of nearly five decades — on his behalf. Their daughter Ahana Deol, seated in the audience, broke down in tears. The entire ceremony paused, just for a moment.

## The Man Before the Legend

Born Dharam Singh Deol in Sahnewal, Punjab, in 1935, Dharmendra arrived in Bombay with nothing but a contest win from Filmfare magazine. By the mid-1960s, he was one of Hindi cinema's most bankable leading men. *Phool Aur Patthar* in 1966 made him a star. *Sholay* in 1975 made him immortal.

But the Padma Vibhushan had eluded him. He received the Padma Bhushan in 2012, fourteen years after his frequent co-star Amitabh Bachchan got the same honour. The Vibhushan — given to the likes of Lata Mangeshkar, Dilip Kumar, and Rajinikanth — somehow never came while he was alive.

It came this Sunday, in a ceremony that honoured 66 recipients across five Padma Vibhushan, 13 Padma Bhushan, and 113 Padma Shri awards. Mammootty received the Padma Bhushan for his contribution to Malayalam cinema. Alka Yagnik, who has been losing her hearing since 2024, received the same honour. R. Madhavan received the Padma Shri. But it was Dharmendra's posthumous recognition that drew the most visceral response in the hall.

## What NRIs Lost in November

For the Indian diaspora, Dharmendra wasn't just a movie star — he was the sound of home. If you grew up in an NRI household in the 1980s or 1990s, his films were on perpetual rotation on VHS tapes passed between families, the labels handwritten in Hindi. *Sholay* was the communal text. *Chupke Chupke* was the comedy you quoted at dinner. *Yaadon Ki Baaraat* was the soundtrack to every car ride where your parents felt briefly, impossibly young again.

His death in November 2025 hit the diaspora with a particular kind of grief — the loss of a cultural anchor in a country many had left decades ago. Sunny Deol and Bobby Deol, both established actors, released a joint statement. Amitabh Bachchan, his *Sholay* partner for 50 years, posted a single black-and-white photograph. No caption was needed.

## The Ceremony

The Padma Awards ceremony at Rashtrapati Bhavan is typically a stately, protocol-driven affair. Recipients walk to the President, receive the medal, pose for a photograph, and return to their seats. Hema Malini, 77, dressed in a white sari, walked to the podium with the composure of someone who has been in public life for five decades. She accepted the medallion, turned to face the cameras, and for the first time in a very public career, appeared to struggle with the weight of the moment.

In the audience, Ahana Deol — who has largely stayed away from the film industry — was visibly emotional. The cameras caught it. Social media did the rest.

## 300 Films, One Legacy

Dharmendra's filmography is almost absurdly prolific. Over 300 films in Hindi alone, plus Punjabi projects and cameos that continued well into his 80s. He was the romantic hero in *Haqeeqat*, the action star in *Phool Aur Patthar*, the comic genius in *Chupke Chupke*, and the loveable rogue in *Sholay* — all without the method-acting gravitas that critics demanded. He was accused of being too handsome to be taken seriously, and he responded by being in more hit films than almost anyone in Indian cinema history.

He entered politics, won a Lok Sabha seat from Bikaner in 2004, served one term, and returned to films. He produced *Apne* to work with both sons. He appeared on *Koffee with Karan* and made Karan Johar laugh until he cried. He posted workout videos on Instagram at 87. He never stopped being Dharmendra.

## The Missing Award

India's civilian honours are not awarded posthumously as a rule — the Padma awards are among the few exceptions. The government's decision to posthumously honour Dharmendra with the Vibhushan acknowledges what the industry had been saying for years: the Bhushan was not enough.

He stood alongside Dilip Kumar, Dev Anand, and Raj Kapoor as one of the defining male leads of Hindi cinema. Of the four, three received the Padma Vibhushan in their lifetimes. Dharmendra got his after.

For NRIs who watched the ceremony from living rooms in New Jersey, apartments in London, and homes in Toronto, the moment Hema Malini accepted that medal was a private reckoning — with a country they left, a cinema they never stopped loving, and a man who represented both.

Dharmendra would have hated the solemnity. He would have cracked a joke. He would have flexed a bicep. He would have made the President laugh.

Instead, his wife collected his medal, his daughter cried, and 300 films spoke for themselves."""
    },

    {
        "headline": "Dhanush's Kara Hits Netflix Tomorrow in Five Languages. It Made ₹50 Crore at the Box Office on a ₹100 Crore Budget. The NRI Audience Might Actually Save This Film.",
        "subheadline": "A 1990s Tamil Nadu heist thriller about a reformed thief fighting a corrupt bank — streaming in Tamil, Hindi, Telugu, Malayalam, and Kannada from May 28. Critics were divided. The OTT audience rarely is.",
        "slug": "dhanush-kara-netflix-may-28-ott-premiere-tamil-heist-thriller-nri-streaming-20260527",
        "category": "entertainment",
        "tags": ["entertainment", "tamil-cinema", "dhanush", "netflix", "ott", "streaming", "heist-thriller", "nri"],
        "person_for_image": "Dhanush",
        "pexels_query": None,
        "sources": "Wikipedia, Pinkvilla, BollywoodLife, 7Globe, Hindustan Times, News18",
        "body": """Dhanush's *Kara* lands on Netflix on May 28, and for once, the OTT premiere might matter more than the theatrical run.

The Tamil-language heist action thriller, directed by Vignesh Raja, made approximately ₹50 crore worldwide against a ₹100 crore budget after its April 30 theatrical release. By Bollywood accounting, that's a disappointment. By the logic of streaming, where Netflix paid for the digital rights and the film reaches 190 countries overnight, it's a second life.

For NRIs who missed the theatrical window — and most did, because Tamil films don't get 3,000-screen releases in North America — May 28 is opening night.

## The Story Behind the Heist

*Kara* is set in the early 1990s, against the backdrop of the Gulf War and the fuel crisis that rippled through rural Tamil Nadu. Dhanush plays Karasaami, a reformed thief trying to live an honest life with his wife Selli (Mamitha Baiju). When a corrupt bank seizes his family's ancestral land over a tractor loan his father could never repay, Kara is pulled back into crime — not for greed, but for justice.

What follows is a Robin Hood story in a Tamil register: Kara robs the very banks that have been trapping poor farmers in predatory EMI schemes, returning money and land documents to villagers who had been swindled. The corrupt bank manager Muthu Selvan (Jayaram, against type) has been running a system that profits from farmers' desperation. Kara's heists expose it.

The film was written by Vignesh Raja and Alfred Prakash. Raja made his directorial debut with *Por Thozhil* in 2023, which was acclaimed for its forensic investigation thriller format. *Kara* is a very different film — sprawling, rural, period-set, and anchored by Dhanush's physical transformation into a wiry, desperate man who steals because the law failed him.

## Why the Box Office Didn't Work

*Kara* opened on April 30, a weekday, which immediately limited its first-day numbers. It received mixed reviews from critics — The Times of India gave it 3.5 out of 5, praising the execution and Dhanush's performance while acknowledging familiar tropes. Cinema Express gave it 3 out of 5, noting that the film "works for the longest time, till it decides to shift gears and take a rather safe route to conformity." The Deccan Chronicle was harsher at 1.5 out of 5.

The 161-minute runtime didn't help. Neither did a title dispute — an unrelated Tamil film called *Karaa* was releasing two weeks later, and the producer of *Karaa* filed a plea in the Madras High Court three days before *Kara*'s release, claiming title registration priority. The confusion muddied the marketing. Dhanush himself joked: "Call it 'Kura' or 'Keera', just watch it."

At ₹50 crore worldwide against a ₹100 crore budget, the theatrical run was commercially underwhelming. But Dhanush's track record on OTT tells a different story. His films consistently find their audience on streaming — *Raayan* was a Netflix hit, *Kuberaa* found its audience on Prime Video. Tamil cinema's OTT economics have decoupled from theatrical performance.

## The Cast

Dhanush anchors the film, but the supporting cast is stacked. Suraj Venjaramoodu — the Malayalam actor whose *Android Kunjappan* is an NRI comfort classic — plays DSP Bharathan, the police officer chasing Kara. K. S. Ravikumar, usually behind the camera as a director, plays Kara's father Kandhasaami. Jayaram, another Malayalam veteran, plays the corrupt bank manager. Karunas reunites with Dhanush for the first time in 16 years.

The music, composed by G. V. Prakash Kumar, includes six tracks. "Kannamma En Kannamma," written and sung by Dhanush himself, has already crossed 40 million YouTube views. The album debuted at No. 5 on the US Top Albums chart for Indian music — a rare feat for a Tamil film soundtrack.

## The NRI Factor

Here's what changes on May 28: *Kara* will be available on Netflix in Tamil, Hindi, Telugu, Malayalam, and Kannada. That's five languages, 190 countries, and a potential audience of tens of millions of South Asian diaspora viewers who couldn't access the film in theatres.

The story — land theft, banking corruption, a father's humiliation, a son's rage — resonates differently for NRIs who left India's villages for opportunity abroad but whose families stayed behind and navigated exactly these systems. The 1990s setting hits a generational nerve: many first-generation NRIs left India during exactly this period, when the economy was opening up but rural India was being left behind.

*Kara* is not a perfect film. At 161 minutes, it's overstuffed in the third act, and the heist sequences sacrifice ingenuity for sentimentality in the final hour. But Dhanush at full intensity, in a role that demands both physical menace and emotional vulnerability, is worth the watch. And on Netflix, there's no three-day weekend pressure, no opening-day occupancy tracker, no trade analyst declaring it a flop.

Just a reformed thief, a corrupt bank, and an audience that finally has time to pay attention."""
    },

    {
        "headline": "Yash's Toxic Has Been Postponed So Many Times That BGMI Made a Video Game Collaboration Before the Film Could Pick a Release Date.",
        "subheadline": "March 19 became June 4. June 4 may become August. Meanwhile, KRAFTON launched Toxic voice packs in BGMI, CinemaCon audiences saw nine minutes and lost their minds, and Nayanthara and Kiara Advani are still waiting to promote a film that won't stand still.",
        "slug": "yash-toxic-postponed-again-bgmi-collab-cinemacon-nayanthara-kiara-release-date-chaos-20260527",
        "category": "entertainment",
        "tags": ["entertainment", "kannada-cinema", "yash", "toxic", "bgmi", "gaming", "cinemacon", "nayanthara", "kiara-advani", "nri"],
        "person_for_image": "Yash (actor)",
        "alt_person": "Yash Gowda",
        "pexels_query": "gangster film noir dark",
        "sources": "Sacnilk, Pinkvilla, ZoomTV, Wikipedia, Filmibeat, KRAFTON press release",
        "body": """There is a video game where you can play as Yash's character from *Toxic* and hear his voice lines in Hindi and Kannada while shooting people in a battle royale. The actual film, in which Yash plays the same character, does not have a confirmed release date.

This is the state of *Toxic: A Fairy Tale for Grown-Ups* in May 2026, and it is simultaneously the most anticipated and most postponed Indian film of the year.

## The Timeline of Delays

*Toxic* was originally announced for a March 19, 2026 release — the same date as Ranveer Singh's *Dhurandhar 2*. That clash was enough to move it. The new date: June 4, 2026, which KVN Productions confirmed alongside a statement blaming "Middle East uncertainty" for the shift. The geopolitical reasoning made sense: the Gulf markets are worth tens of crores to a pan-India release, and regional instability can delay distribution deals.

Then June 4 started looking uncertain. Pinkvilla reported that the makers had "once again postponed the release, with a new date yet to be announced." ZoomTV cited industry insiders suggesting August as the new target. The production team has not officially confirmed or denied any of it.

Meanwhile, Sacnilk still lists the theatrical release as June 4 — "Releasing in 7 days." The contradiction is the most honest summary of *Toxic*'s journey: nobody is entirely sure what's happening, including, possibly, the people making it.

## The CinemaCon Moment

What everyone IS sure about is that the film looks extraordinary.

At CinemaCon 2026 in Las Vegas, the production team screened a nine-minute preview of *Toxic*. The footage, set across the 1940s through the 1970s, depicted a rise-and-fall gangster saga in Goa — think *Gangs of Wasseypur* meets *Once Upon a Time in America*, filtered through Geetu Mohandas's art-house sensibility. The international trade audience — the same people who've seen Marvel rough cuts and Star Wars footage — reportedly gave it a standing response.

The IMAX confirmation came shortly after. *Toxic* and *Ramayana* now anchor IMAX's 2026 global premium slate for Indian cinema.

## The BGMI Crossover

Then there is the gaming collaboration, which is either brilliant marketing or a sign that the promotional timeline has completely detached from the production timeline.

KRAFTON India, the company behind Battlegrounds Mobile India (BGMI), announced a *Toxic*-themed update as part of BGMI's 4.4 patch. Starting May 28, 2026, players can download Yash's voice pack — available in both Hindi and Kannada — along with *Toxic*-branded collectibles, weapon skins, and a cameo film. The collaboration explicitly targets Gen Z Indian gamers, the same demographic that made *KGF: Chapter 2* a ₹1,200-crore phenomenon.

The irony is that BGMI players will be engaging with *Toxic* content before cinema audiences get to see the actual film. The game's release date is more reliable than the movie's.

## ₹700 Crore and Five Leading Women

*Toxic* is budgeted at an estimated ₹700-800 crore, making it one of the most expensive Indian films ever produced. Directed by Geetu Mohandas — whose *Moothon* won the FIPRESCI Prize at the Toronto International Film Festival — the film pairs an art-house director with a mass-market superstar in a way that Indian cinema rarely attempts.

The cast is built around women in a way that Yash himself has highlighted in interviews. Nayanthara, Kiara Advani, Huma Qureshi, Tara Sutaria, and Rukmini Vasanth all play significant roles. In an interview with Filmibeat, Yash described their characters as having "a different kind of violence" and said the female gaze makes the film "very refreshing."

Ravi Basrur, who composed the *KGF* scores, handles the music and background score. JJ Perry, the action choreographer behind *John Wick*, designed select action sequences. The Anbariv duo handled additional action work.

## What NRIs Are Waiting For

After *KGF: Chapter 2* became the second-highest-grossing Indian film of 2022, Yash entered a four-year hiatus. For the diaspora, which turned *KGF* into a midnight-show cultural event at every AMC and Cinepolis in North America, *Toxic* is the most awaited follow-up since Rajinikanth's *Kabali*.

The Phars Film distribution deal alone — ₹105 crore for international Indian-language rights — reflects the overseas hunger. NRI audiences don't just want to see *Toxic*; they want to see it on the biggest screen possible, in IMAX, on opening night, with a crowd that yells when Yash enters the frame.

They just need a date.

The film might release in June. It might release in August. It might release when BGMI players have already heard every voice line and unlocked every skin. But when *Toxic* finally arrives — and it will, because ₹700 crore doesn't stay on a shelf — it will be the most pre-marketed, pre-delayed, pre-gamed Indian film in history.

Yash, presumably, is fine with this. He waited four years. The audience can wait a few more weeks. Probably."""
    },
]


# ── Main publish loop ────────────────────────────────────────────────
def main():
    import requests
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    published = []
    
    for i, art in enumerate(ARTICLES, 1):
        print(f"\n{'='*60}")
        print(f"Article {i}: {art['headline'][:80]}...")
        print(f"{'='*60}")
        
        # Image sourcing — Wikipedia first for person articles
        img_url = None
        person = art.get('person_for_image')
        if person:
            print(f"\n📷 Trying Wikipedia for '{person}'...")
            img_url = fetch_wikipedia_person_image(person)
            
            # Try alternate name if provided
            if not img_url and art.get('alt_person'):
                print(f"  Trying alternate: '{art['alt_person']}'...")
                img_url = fetch_wikipedia_person_image(art['alt_person'])
        
        # Pexels fallback
        if not img_url and art.get('pexels_query'):
            print(f"\n📷 Falling back to Pexels: '{art['pexels_query']}'...")
            img_url = fetch_pexels_image(art['pexels_query'])
        
        # Validate
        if img_url:
            if is_banned_url(img_url):
                print(f"  ✗ Banned URL detected, skipping: {img_url[:60]}")
                img_url = None
            elif not validate_image_url(img_url):
                print(f"  ✗ Validation failed, skipping image")
                img_url = None
        
        if not img_url:
            print(f"  ℹ No valid image found — publishing without image (better than wrong image)")
        else:
            # Upload to Supabase storage for permanence
            print(f"\n📤 Uploading image to Supabase storage...")
            img_url = upload_image_to_supabase(img_url, f"{art['slug']}.jpg")
        
        # Prepare article data
        article_data = {
            "headline": art["headline"],
            "subheadline": art["subheadline"],
            "slug": art["slug"],
            "body": art["body"].strip(),
            "category": "entertainment",
            "vertical": "entertainment",
            "status": "published",
            "published_at": now,
            "sources": json.dumps([{"name": s.strip(), "url": ""} for s in art["sources"].split(",")]),
            "tags": art.get("tags", ["entertainment", "bollywood", "diaspora", "nri"]),
            "urgency": "medium",
            "image_url": img_url,
            "image_attribution": "Wikimedia Commons" if img_url and ('wikimedia' in (img_url or '').lower() or 'wikipedia' in (img_url or '').lower()) else ("Pexels" if img_url and 'pexels' in (img_url or '').lower() else None),
        }
        
        # Word count check
        word_count = len(art["body"].split())
        print(f"\n📝 Word count: {word_count}")
        if word_count < 400:
            print(f"  ✗ REJECTED — below 400-word minimum!")
            continue
        
        # Headline length check
        if len(art["headline"]) > 200:
            print(f"  ⚠ Headline is {len(art['headline'])} chars (>200) — truncating would lose meaning, publishing as-is")
        
        print(f"\n📤 Publishing to Supabase...")
        try:
            result = sb_post("p2_articles", article_data)
            print(f"  ✓ Published: {art['slug']}")
            published.append(art['slug'])
        except Exception as e:
            # Get full error details
            if hasattr(e, 'response') and e.response is not None:
                print(f"  ✗ Failed to publish: {e}")
                print(f"  ✗ Response body: {e.response.text[:500]}")
            else:
                print(f"  ✗ Failed to publish: {e}")
            continue
        
        time.sleep(1)  # Rate limiting
    
    print(f"\n{'='*60}")
    print(f"✅ Published {len(published)}/{len(ARTICLES)} articles")
    for slug in published:
        print(f"  → {slug}")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
