#!/usr/bin/env python3
"""Entertainment writer for The Videshi — 2026-05-28 batch"""

import os, json, requests, urllib.parse, time, uuid, re
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

# ── Wikipedia image fetcher ──
def fetch_wikipedia_person_image(person_name, retries=3):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    for attempt in range(retries):
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
                return None
            elif r.status_code == 429:
                wait = (attempt + 1) * 3
                print(f"  ⚠ Wikipedia rate limit for '{person_name}', retrying in {wait}s...")
                time.sleep(wait)
                continue
            else:
                return None
        except Exception as e:
            print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

# ── Pexels image fetcher ──
def fetch_pexels_image(query, fallback_query=None):
    """Fetch an image from Pexels using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            result = subprocess.run(
                ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
                 f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=3&orientation=landscape'],
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

# ── Image upload to Supabase ──
def upload_image_to_supabase(image_url, filename):
    """Download image and upload to Supabase storage bucket."""
    try:
        r = requests.get(image_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=20)
        if r.status_code != 200:
            print(f"  ⚠ Failed to download image: HTTP {r.status_code}")
            return image_url  # Return original URL as fallback
        
        content_type = r.headers.get('Content-Type', 'image/jpeg')
        if 'image' not in content_type:
            print(f"  ⚠ Not an image: {content_type}")
            return image_url
            
        if len(r.content) < 5000:
            print(f"  ⚠ Image too small: {len(r.content)} bytes")
            return image_url

        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        upload_r = requests.post(
            upload_url,
            headers={
                'apikey': SUPABASE_KEY,
                'Authorization': f'Bearer {SUPABASE_KEY}',
                'Content-Type': content_type,
                'x-upsert': 'true'
            },
            data=r.content,
            timeout=30
        )
        if upload_r.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed: {upload_r.status_code} {upload_r.text[:200]}")
            # If it's a wikimedia URL, it's permanent, so return it directly
            if 'upload.wikimedia.org' in image_url or 'images.pexels.com' in image_url:
                return image_url
            return image_url
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        if 'upload.wikimedia.org' in image_url or 'images.pexels.com' in image_url:
            return image_url
        return image_url

# ── Supabase helpers ──
def sb_insert(table, data):
    """Insert a record into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=HEADERS,
        json=data,
        timeout=30
    )
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and len(result) > 0:
            return result[0]
        return result
    else:
        print(f"  ⚠ Insert error: {r.status_code} {r.text[:300]}")
        return None

def sb_patch(table, filters, data):
    """Update records in Supabase."""
    params = '&'.join(f"{k}={v}" for k, v in filters.items())
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/{table}?{params}",
        headers=HEADERS,
        json=data,
        timeout=30
    )
    if r.status_code in (200, 201):
        return r.json()
    else:
        print(f"  ⚠ Patch error: {r.status_code} {r.text[:300]}")
        return None

# ── Validate image URL ──
def validate_image(url):
    """Check that a URL returns a valid image."""
    if not url:
        return False
    # Block banned sources
    banned = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com', '_nc_ht=', '_nc_cat=', 'ccb=']
    for b in banned:
        if b in url:
            print(f"  ❌ BANNED source detected: {b}")
            return False
    try:
        r = requests.head(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=10, allow_redirects=True)
        if r.status_code == 200:
            ct = r.headers.get('Content-Type', '')
            cl = int(r.headers.get('Content-Length', 0))
            if 'image' in ct and cl > 5000:
                return True
            elif 'image' in ct and cl == 0:
                # Some servers don't return Content-Length on HEAD
                return True
        # Try GET for servers that don't support HEAD well
        r = requests.get(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=10, stream=True)
        ct = r.headers.get('Content-Type', '')
        if r.status_code == 200 and 'image' in ct:
            return True
    except Exception as e:
        print(f"  ⚠ Validation error for {url[:60]}: {e}")
    return False


# ════════════════════════════════════════════
# ARTICLE 1: Agar Tum Saath Ho Spotify milestone
# ════════════════════════════════════════════

article1 = {
    "headline": "A Song From a Film That Flopped in 2015 Just Became the Most-Streamed Indian Track on Spotify. It Has 717 Million Plays.",
    "subheadline": "'Agar Tum Saath Ho' from Tamasha overtakes 'Kesariya' — composed by A.R. Rahman, sung by Arijit Singh and Alka Yagnik, the track is now Indian music's defining digital monument.",
    "slug": "agar-tum-saath-ho-tamasha-most-streamed-indian-song-spotify-717-million-arijit-ar-rahman",
    "category": "entertainment",
    "body": """A song about two people who can't be together just became the most-streamed Indian song on any platform, anywhere in the world.

"Agar Tum Saath Ho," the devastating ballad from Imtiaz Ali's *Tamasha* (2015), has crossed approximately 717 million streams on Spotify — overtaking "Kesariya" from *Brahmastra* to claim the all-time record for an Indian track. A decade after its release, and nearly seven years after streaming became India's primary way of consuming music, the song is still growing.

## The Numbers Don't Make Sense Until They Do

*Tamasha* opened to mixed reviews and earned ₹138 crore worldwide — respectable, not spectacular. It was considered a commercial disappointment by Ranbir Kapoor's standards. The soundtrack, released weeks before the film, was treated as A.R. Rahman's quietest album in years. No club bangers. No remixes for DJ nights. Just four tracks that sounded like private conversations.

"Agar Tum Saath Ho" wasn't the lead single. It wasn't the one that played during the trailer. It was the song that played during the scene where Deepika Padukone tells Ranbir Kapoor she can't keep pretending he's someone he's not. If you've seen the film, you know the exact frame. If you haven't, you've still heard the song — at a wedding reception, in someone's car at 2 AM, through a cousin's Instagram story with no caption except the lyrics.

Rahman composed it in a register he rarely uses: stripped down, conversational, almost like humming to yourself. Arijit Singh sang his parts like he was trying to convince someone to stay. Alka Yagnik — the voice behind three decades of Bollywood's biggest love songs — sang hers like she already knew they wouldn't.

## Why 717 Million Is a Different Kind of Record

The previous record-holder, "Kesariya," is from a ₹431-crore blockbuster. It was pre-released months before the film, went viral on Instagram Reels, and was designed for maximum streaming impact. It's a beautiful song that was also a marketing campaign.

"Agar Tum Saath Ho" had none of that infrastructure. It comes from a film most people discovered years after its theatrical run — often on Netflix, often alone, often at exactly the moment they needed it. Its streaming curve isn't a spike followed by a decline. It's a steady, relentless climb, month after month, year after year. Spotify's data shows the track has never left India's top 200 since the platform launched in the country in 2019.

That's not virality. That's something closer to need.

## The Diaspora Connection

Ask any NRI which Bollywood song makes them homesick and you'll hear one of three answers: "Agar Tum Saath Ho," "Kun Faya Kun," or "Tujhe Dekha Toh." Two of those are Rahman. The third is from a 1995 film that defined an entire generation's idea of romance.

A significant portion of those 717 million streams come from outside India. Spotify's own data has repeatedly named Arijit Singh — who became the platform's most-followed artist globally in 2025, surpassing Taylor Swift — as one of India's most-exported cultural figures. And Alka Yagnik, who received the Padma Bhushan just days ago, has been losing her hearing since 2024. The voice on this track may be one of the last recordings of Yagnik at the peak of her powers.

## What This Means for Indian Music

The record matters because of what it represents. Indian music is no longer a niche category on global streaming platforms — it's a dominant force. In May 2026, Spotify's India charts are led almost entirely by Indian artists. Fewer international hits are breaking through in India than at any point since streaming began. The audience isn't just large; it's loyal in a way that Western pop audiences often aren't.

And at the top of all of it sits a quiet song from a misunderstood film about a man who couldn't figure out who he was supposed to be.

Irfan Siddiqui, who wrote the lyrics, once said he wrote the words in a single sitting. Rahman called it one of his most personal compositions. Imtiaz Ali has said *Tamasha* is the film closest to his heart. Ranbir Kapoor considers it his best performance. None of those claims seemed credible in November 2015, when the film underperformed and everyone moved on.

717 million streams later, everyone came back.

*Sources: Filmibeat, Zoom TV, Spotify India charts, Koimoi*""",
    "sources": ["Filmibeat", "Zoom TV", "Spotify India", "Koimoi"],
    "image_person": "Arijit Singh"
}


# ════════════════════════════════════════════
# ARTICLE 2: Triptii Dimri's meteoric rise
# ════════════════════════════════════════════

article2 = {
    "headline": "Triptii Dimri Was a Background in a Bathtub Two Years Ago. She Now Has Four Films Opposite Prabhas, Madhuri Dixit, and Ranbir Kapoor.",
    "subheadline": "From Animal's breakout moment to a ₹1,000-crore slate spanning Spirit, Maa Behen, Animal Park, and a Parveen Babi biopic — the fastest career acceleration in recent Bollywood history.",
    "slug": "triptii-dimri-rise-spirit-prabhas-maa-behen-animal-park-bollywood-leading-lady-2026",
    "category": "entertainment",
    "body": """Two years ago, Triptii Dimri was best known for being in a bathtub. The scene in Sandeep Reddy Vanga's *Animal* (2023) — where Ranbir Kapoor's character brings his girlfriend to confront his wife — made Dimri the subject of a thousand memes, a million Instagram followers, and an uncomfortable national conversation about what it means to be the "other woman" in a Bollywood blockbuster.

The conversation was reductive. Her career since has not been.

## The Slate That Changed Everything

In the next eighteen months, Dimri will appear in four major films that span the full range of Indian cinema's ambitions:

**Maa Behen** (Netflix, June 4, 2026): A dark comedy directed by Ashwiny Iyer Tiwari, starring Dimri alongside Madhuri Dixit. The premise — Madhuri hides a dead body while Dimri plays her daughter who discovers it — inverts the typical mother-daughter dynamic in Hindi cinema. Dimri gets her first pairing with a legacy star, and the film positions her as the dramatic anchor, not the romantic interest.

**Spirit** (Theatrical, March 5, 2027): Sandeep Reddy Vanga's follow-up to *Animal*, this time with Prabhas in the lead. Dimri plays opposite one of South India's biggest stars in a medical-cop drama about an international crime syndicate. The first-look poster, released on January 1, 2026, showed Prabhas injured and Dimri unadorned — no glamour shots, no dance number tease. The production budget is reportedly north of ₹300 crore. This is a pan-India film in eight languages.

**Animal Park** (Date TBA): The sequel to the film that made her famous. Dimri returns opposite Ranbir Kapoor in what Vanga has described as a "continuation, not a repetition." If *Animal* made her a name, *Animal Park* will determine whether she can carry the weight of a franchise.

**Parveen Babi biopic** (Date TBA): Directed by Shonali Bose (*The Sky Is Pink*), this film about the troubled 1970s-80s icon is Dimri's first solo-lead project with a prestige director. Parveen Babi — who struggled with schizophrenia, made the cover of TIME Magazine, and died alone in her Mumbai apartment in 2005 — is one of Bollywood's most haunting stories. It is also a role that every young actress would want and very few could pull off.

## The Speed of the Ascent

Before *Animal*, Dimri had exactly one film that anyone outside of critics' circles had seen: *Bulbbul* (2020), a Netflix supernatural drama produced by Anushka Sharma. She was excellent in it. Almost nobody watched it. Her next two films — *Qala* and *Bad Newz* — ranged from underseen to underperforming.

What *Animal* did was prove that she could command attention in a scene designed to focus entirely on someone else. The bathtub scene was Ranbir Kapoor's moment of moral collapse. Dimri's job was to be present, vulnerable, and completely real in a way that made the audience unable to look away. She did it so well that the audience remembered her face, not his.

The industry noticed. Within months, she was attached to four films with a combined production budget that likely exceeds ₹1,000 crore. She went from "the girl from *Animal*" to a leading lady with a slate that includes Madhuri Dixit, Prabhas, and a biographical drama that could win awards.

## What the Diaspora Should Watch For

For NRI audiences, Dimri's trajectory matters because she represents a new model for how Bollywood stardom works. She didn't come from a film family. She didn't have a debut opposite a Khan. She wasn't launched by Dharma or YRF. She was a working actress who took the right role at the right time and turned a supporting part into a career.

*Maa Behen* arrives on Netflix on June 4 — the same day Ram Charan's *Peddi* opens in theatres. If the film works, Dimri gets to prove she can hold the screen alongside Madhuri Dixit, not just Ranbir Kapoor. If *Spirit* works, she becomes one of the very few actresses working simultaneously across Bollywood and the South Indian film industry.

She's 31 years old. Two years ago she was in a bathtub. Now she's in four of the most anticipated films on the Indian calendar.

The industry has a word for this kind of acceleration. They call it a moment. Triptii Dimri's moment is looking less like a moment and more like a decade.

*Sources: Bombay Times, Pinkvilla, Zoom TV, Bollywood Hungama*""",
    "sources": ["Bombay Times", "Pinkvilla", "Zoom TV", "Bollywood Hungama"],
    "image_person": "Triptii Dimri"
}


# ════════════════════════════════════════════
# ARTICLE 3: JioHotstar's ₹4,000 crore South India bet
# ════════════════════════════════════════════

article3 = {
    "headline": "JioHotstar Just Put ₹4,000 Crore on South India. After Bollywood's Worst May in Five Years, the Math Makes Sense.",
    "subheadline": "1,500 hours of new Tamil, Telugu, and Malayalam content. Kerala Crime Files returns. Vijay Sethupathi and Nivin Pauly sign on. The biggest bet in Indian OTT history follows the money to where the audiences actually are.",
    "slug": "jiohotstar-4000-crore-south-india-ott-investment-tamil-malayalam-telugu-bollywood-may-2026",
    "category": "entertainment",
    "body": """The numbers from May 2026 tell a story that Bollywood would rather not hear.

The three highest-grossing Indian films this month are a Tamil thriller (*Karuppu*, ₹163 crore), a Marathi period drama (*Raja Shivaji*, ₹93 crore), and a Malayalam sequel (*Drishyam 3*, ₹75 crore). The best Bollywood managed was *Pati Patni Aur Woh Do* at ₹40 crore. Not one Hindi film cracked the top three. Regional cinema didn't just compete with Bollywood in May — it replaced it.

JioHotstar, it seems, read the same report card.

## The Bet

The platform has committed ₹4,000 crore over five years to South Indian content — the single largest investment in regional streaming in Indian OTT history. The details, announced in partnership with the Tamil Nadu government, are staggering:

**1,500 hours** of new original programming across Tamil, Telugu, Malayalam, and Kannada. **25 new titles** in the first slate alone. A letter of intent signed with Deputy Chief Minister Udhayanidhi Stalin's government, which projects the deal will create 1,000 direct jobs and 15,000 indirect ones.

The names attached are not filler. **Kerala Crime Files**, the Malayalam true-crime series that became JioHotstar's most-watched original from the South, returns for a new season. **Vijay Sethupathi**, arguably the most bankable actor in Tamil cinema, is on the slate. So is **Nivin Pauly**, Malayalam cinema's most reliable hitmaker. The titles range from *Kaattaan* (an adventure series) to *Heartbeat Season 3* to *Good Wife Season 2* — a deliberate mix of returning franchises and new IP.

## Why Now

The timing is not coincidence. Three structural shifts have converged:

**The box office has moved south.** In 2026, the highest-grossing Indian film is *Dhurandhar 2: The Revenge* (₹1,850 crore) — a Hindi film, yes, but one starring Ranveer Singh in a franchise modeled on South Indian action cinema. The second-highest is *Border 2* (₹464 crore), which drew heavily from the Telugu war-film playbook. Meanwhile, *Karuppu* became the Tamil industry's biggest May opening ever, and *Drishyam 3* is tracking to become the highest-grossing Malayalam film of all time. The audience hasn't abandoned Hindi cinema — they've expanded their appetite, and South Indian films are feeding it.

**OTT viewership in the South is surging.** JioHotstar reported a 70% increase in South Indian content viewership year-over-year, driven by multilingual releases and improved dubbing. The platform now offers content in 8 languages, and its 100 million subscriber base increasingly skews toward regional content.

**The NRI audience is driving premiums.** For the Indian diaspora, OTT platforms are often the primary — sometimes the only — way to watch regional cinema. Tamil, Malayalam, and Telugu films that might get limited or no theatrical release in North America are available on streaming within weeks. Platforms that invest in this content capture not just eyeballs but high-ARPU subscribers who pay for annual plans and rarely churn.

## What This Means for Diaspora Viewers

If you're an NRI who grew up watching Malayalam or Tamil films at home and has struggled to find them on mainstream streaming platforms, this is the inflection point. ₹4,000 crore doesn't buy a few prestige originals — it buys an ecosystem. It means more shows in your mother tongue, with subtitles, available the day they premiere, on a platform you already pay for.

It also means competition. Netflix India has been investing in South Indian original content (*Paava Kadhaigal*, *Minnal Murali*, *Maharaja*), and Amazon Prime has had early success with Tamil and Telugu films (*Jai Bhim*, *Soorarai Pottru*). JioHotstar's move forces both platforms to either match the spend or cede the territory. For viewers, that means more content, higher production values, and faster release windows.

## The Bigger Picture

JioHotstar's ₹4,000 crore bet is not charity toward regional cinema. It's a business decision that reflects where Indian entertainment is actually headed. Hindi cinema still has the star power and the global brand recognition, but the box office increasingly rewards stories and styles that originate in the South. The streaming platforms are simply following the money.

For the Tamil, Telugu, Malayalam, and Kannada film industries — long accustomed to being described as "regional" in a dismissive tone — this is vindication. For the diaspora audiences who've always known what the rest of India is slowly discovering, it's about time.

*Sources: Exchange4Media, Bollywood Hungama, Filmibeat, Sacnilk, AngelOne*""",
    "sources": ["Exchange4Media", "Bollywood Hungama", "Filmibeat", "Sacnilk"],
    "image_person": None  # No single person — use Pexels
}


# ════════════════════════════════════════════
# PUBLISH
# ════════════════════════════════════════════

articles = [article1, article2, article3]

for i, art in enumerate(articles, 1):
    print(f"\n{'='*60}")
    print(f"ARTICLE {i}: {art['headline'][:80]}...")
    print(f"{'='*60}")
    
    # Image sourcing
    img_url = None
    img_attribution = "The Videshi"
    
    if art.get('image_person'):
        person = art['image_person']
        print(f"\n📸 Sourcing image for: {person}")
        img_url = fetch_wikipedia_person_image(person)
        if img_url:
            img_attribution = "Wikimedia Commons"
        else:
            # Try alternate names
            for alt in [f"{person} (singer)", f"{person} (actress)", f"{person} (actor)"]:
                img_url = fetch_wikipedia_person_image(alt)
                if img_url:
                    img_attribution = "Wikimedia Commons"
                    break
    
    if not img_url:
        # Pexels fallback with specific terms
        if i == 1:
            img_url = fetch_pexels_image("music streaming headphones concert", "Spotify music listening")
        elif i == 2:
            img_url = fetch_pexels_image("Bollywood actress film set", "Indian cinema actress")
        elif i == 3:
            img_url = fetch_pexels_image("South Indian cinema film", "Indian movie theater audience")
    
    # Validate image
    if img_url and not validate_image(img_url):
        print(f"  ⚠ Image validation failed, trying Pexels fallback...")
        if i == 1:
            img_url = fetch_pexels_image("music concert stage lights", "Indian music performance")
        elif i == 2:
            img_url = fetch_pexels_image("movie film camera Bollywood", "Indian cinema production")
        elif i == 3:
            img_url = fetch_pexels_image("streaming television OTT", "Indian entertainment digital")
    
    # Upload to Supabase if we have an image
    final_img_url = None
    if img_url:
        filename = f"{art['slug']}.jpg"
        final_img_url = upload_image_to_supabase(img_url, filename)
    
    # Create article record
    now = datetime.now(timezone.utc).isoformat()
    record = {
        "headline": art["headline"],
        "subheadline": art["subheadline"],
        "slug": art["slug"],
        "category": art["category"],
        "vertical": art["category"],  # vertical matches category
        "body": art["body"],
        "sources": json.dumps(art["sources"]),
        "status": "published",
        "published_at": now,
        "image_url": final_img_url,
        "image_attribution": img_attribution if final_img_url else None,
    }
    
    print(f"\n📝 Publishing: {art['slug']}")
    result = sb_insert("p2_articles", record)
    
    if result:
        art_id = result.get('id', 'unknown')
        print(f"  ✅ Published! ID: {art_id}")
        print(f"  📰 Headline: {art['headline'][:70]}...")
        print(f"  🏷️  Category: {art['category']}")
        print(f"  🔗 Slug: {art['slug']}")
        if final_img_url:
            print(f"  🖼️  Image: {final_img_url[:60]}...")
    else:
        print(f"  ❌ FAILED to publish article {i}")
    
    time.sleep(1)

print(f"\n{'='*60}")
print("✅ Entertainment writer batch complete!")
print(f"{'='*60}")
